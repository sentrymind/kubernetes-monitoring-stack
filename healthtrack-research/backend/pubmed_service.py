"""
PubMed integration service with auto-search and caching
"""
from Bio import Entrez
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import time
import os
import re
from sqlalchemy.orm import Session
from .database import Supplement, ResearchCache

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Entrez
Entrez.email = os.getenv("PUBMED_EMAIL", "healthtrack@example.com")
Entrez.api_key = os.getenv("PUBMED_API_KEY")


class PubMedService:
    """Service for searching and caching PubMed research"""

    def __init__(self, db: Session):
        self.db = db
        self.rate_limit_delay = 0.34  # ~3 requests per second

    def auto_search_for_supplement(
        self,
        supplement_name: str,
        max_results: int = 20,
        start_year: int = 2015,
        end_year: int = 2025
    ) -> List[Dict[str, Any]]:
        """
        Automatically search for research when adding a new supplement

        Args:
            supplement_name: Name of the supplement
            max_results: Maximum number of results to fetch
            start_year: Start year for filtering
            end_year: End year for filtering

        Returns:
            List of research articles
        """
        logger.info(f"Auto-searching PubMed for: {supplement_name}")

        # Build search query focusing on high-quality evidence
        query = f'("{supplement_name}"[Title/Abstract]) AND '
        query += '(("randomized controlled trial"[Publication Type]) OR '
        query += '("systematic review"[Publication Type]) OR '
        query += '("meta-analysis"[Publication Type])) AND '
        query += f'{start_year}:{end_year}[Date - Publication] AND '
        query += '("humans"[MeSH Terms]) AND ("adult"[MeSH Terms])'

        try:
            # Search PubMed
            handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=max_results,
                sort="relevance"
            )
            record = Entrez.read(handle)
            handle.close()

            pmids = record["IdList"]
            logger.info(f"Found {len(pmids)} articles for {supplement_name}")

            if not pmids:
                return []

            # Fetch details
            time.sleep(self.rate_limit_delay)
            articles = self._fetch_article_details(pmids)

            return articles

        except Exception as e:
            logger.error(f"PubMed search error: {e}")
            return []

    def _fetch_article_details(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """Fetch detailed information for PMIDs"""
        articles = []

        try:
            handle = Entrez.efetch(
                db="pubmed",
                id=pmids,
                rettype="xml",
                retmode="xml"
            )
            records = Entrez.read(handle)
            handle.close()

            for record in records['PubmedArticle']:
                try:
                    article = self._parse_article(record)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.warning(f"Error parsing article: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error fetching article details: {e}")

        return articles

    def _parse_article(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse PubMed XML record"""
        try:
            article_data = record['MedlineCitation']['Article']
            pmid = str(record['MedlineCitation']['PMID'])

            # Basic information
            title = article_data.get('ArticleTitle', '')
            abstract = self._extract_abstract(article_data)

            # Authors
            authors = []
            if 'AuthorList' in article_data:
                for author in article_data['AuthorList'][:3]:  # First 3 authors
                    if 'LastName' in author and 'ForeName' in author:
                        authors.append(f"{author['ForeName']} {author['LastName']}")

            # Year
            year = self._extract_year(article_data)

            # Publication type and evidence level
            pub_types = self._extract_publication_types(record)
            evidence_level = self._determine_evidence_level(pub_types)

            # Journal
            journal = article_data.get('Journal', {}).get('Title', '')

            # DOI
            doi = self._extract_doi(article_data)

            # URL
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

            # Extract dosage information from abstract
            recommended_dosage, dosage_unit = self._extract_dosage_from_abstract(abstract)

            # Extract key findings
            key_findings = self._extract_key_findings(abstract)

            return {
                'pmid': pmid,
                'title': title,
                'abstract': abstract,
                'year': year,
                'publication_type': ', '.join(pub_types),
                'evidence_level': evidence_level,
                'authors': ', '.join(authors),
                'journal': journal,
                'doi': doi,
                'url': url,
                'recommended_dosage': recommended_dosage,
                'dosage_unit': dosage_unit,
                'key_findings': key_findings
            }

        except Exception as e:
            logger.error(f"Error parsing article: {e}")
            return None

    def _extract_abstract(self, article_data: Dict[str, Any]) -> str:
        """Extract abstract text"""
        abstract = ""
        if 'Abstract' in article_data and 'AbstractText' in article_data['Abstract']:
            abstract_parts = article_data['Abstract']['AbstractText']
            if isinstance(abstract_parts, list):
                abstract = " ".join(str(part) for part in abstract_parts)
            else:
                abstract = str(abstract_parts)
        return abstract

    def _extract_year(self, article_data: Dict[str, Any]) -> Optional[int]:
        """Extract publication year"""
        try:
            if 'Journal' in article_data and 'JournalIssue' in article_data['Journal']:
                issue = article_data['Journal']['JournalIssue']
                if 'PubDate' in issue and 'Year' in issue['PubDate']:
                    return int(issue['PubDate']['Year'])
        except:
            pass
        return None

    def _extract_publication_types(self, record: Dict[str, Any]) -> List[str]:
        """Extract publication types"""
        pub_types = []
        try:
            if 'PublicationTypeList' in record['MedlineCitation']['Article']:
                pub_types = [str(pt) for pt in record['MedlineCitation']['Article']['PublicationTypeList']]
        except:
            pass
        return pub_types

    def _determine_evidence_level(self, pub_types: List[str]) -> str:
        """Determine evidence level based on publication type"""
        pub_types_lower = [pt.lower() for pt in pub_types]

        if any('meta-analysis' in pt for pt in pub_types_lower):
            return 'high'
        elif any('systematic review' in pt for pt in pub_types_lower):
            return 'high'
        elif any('randomized controlled trial' in pt for pt in pub_types_lower):
            return 'medium'
        else:
            return 'low'

    def _extract_doi(self, article_data: Dict[str, Any]) -> Optional[str]:
        """Extract DOI"""
        try:
            if 'ELocationID' in article_data:
                for eid in article_data['ELocationID']:
                    if eid.attributes.get('EIdType') == 'doi':
                        return str(eid)
        except:
            pass
        return None

    def _extract_dosage_from_abstract(self, abstract: str) -> tuple[Optional[float], Optional[str]]:
        """
        Extract recommended dosage from abstract

        Returns:
            (dosage_value, dosage_unit)
        """
        if not abstract:
            return None, None

        # Patterns for dosage extraction
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(mg|g|mcg|μg|iu|IU)\s*(?:per\s+day|daily|/day)',
            r'(?:dose|dosage|supplementation).*?(\d+(?:\.\d+)?)\s*(mg|g|mcg|μg|iu|IU)',
            r'(\d+(?:\.\d+)?)\s*(mg|g|mcg|μg|iu|IU)\s*(?:of|supplementation)',
        ]

        for pattern in patterns:
            match = re.search(pattern, abstract, re.IGNORECASE)
            if match:
                try:
                    dosage = float(match.group(1))
                    unit = match.group(2).lower()

                    # Normalize units
                    if unit in ['μg', 'mcg']:
                        unit = 'mcg'
                    elif unit in ['iu', 'IU']:
                        unit = 'IU'

                    return dosage, unit
                except:
                    continue

        return None, None

    def _extract_key_findings(self, abstract: str, max_length: int = 300) -> Optional[str]:
        """Extract key findings from abstract"""
        if not abstract:
            return None

        # Look for conclusion section
        conclusion_patterns = [
            r'CONCLUSION[S]?:\s*(.+?)(?:\.|$)',
            r'CONCLUSIONS:\s*(.+?)(?:\.|$)',
            r'RESULTS:\s*(.+?)(?:\.|$)',
        ]

        for pattern in conclusion_patterns:
            match = re.search(pattern, abstract, re.IGNORECASE | re.DOTALL)
            if match:
                finding = match.group(1).strip()
                if len(finding) > max_length:
                    finding = finding[:max_length] + "..."
                return finding

        # If no specific section found, return first part of abstract
        if len(abstract) > max_length:
            return abstract[:max_length] + "..."

        return abstract

    def cache_research(self, supplement_id: int, articles: List[Dict[str, Any]]) -> int:
        """
        Cache research articles in database

        Args:
            supplement_id: ID of the supplement
            articles: List of article data

        Returns:
            Number of articles cached
        """
        cached_count = 0

        for article in articles:
            try:
                # Check if already cached
                existing = self.db.query(ResearchCache).filter(
                    ResearchCache.pmid == article['pmid']
                ).first()

                if existing:
                    # Update last accessed
                    existing.last_accessed = datetime.utcnow()
                    continue

                # Create new cache entry
                cache_entry = ResearchCache(
                    supplement_id=supplement_id,
                    pmid=article['pmid'],
                    title=article['title'],
                    abstract=article['abstract'],
                    year=article['year'],
                    publication_type=article['publication_type'],
                    evidence_level=article['evidence_level'],
                    authors=article['authors'],
                    journal=article['journal'],
                    doi=article['doi'],
                    url=article['url'],
                    recommended_dosage=article['recommended_dosage'],
                    dosage_unit=article['dosage_unit'],
                    key_findings=article['key_findings']
                )

                self.db.add(cache_entry)
                cached_count += 1

            except Exception as e:
                logger.error(f"Error caching article {article['pmid']}: {e}")
                continue

        self.db.commit()
        logger.info(f"Cached {cached_count} new articles for supplement {supplement_id}")

        return cached_count

    def search_interactions(
        self,
        supplement_a: str,
        supplement_b: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for supplement-supplement interactions

        Args:
            supplement_a: Name of first supplement
            supplement_b: Name of second supplement
            max_results: Maximum results

        Returns:
            List of interaction articles
        """
        logger.info(f"Searching interactions: {supplement_a} + {supplement_b}")

        query = f'("{supplement_a}"[Title/Abstract]) AND '
        query += f'("{supplement_b}"[Title/Abstract]) AND '
        query += '("interaction"[Title/Abstract] OR "adverse effect"[Title/Abstract]) AND '
        query += '("humans"[MeSH Terms])'

        try:
            handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=max_results,
                sort="relevance"
            )
            record = Entrez.read(handle)
            handle.close()

            pmids = record["IdList"]

            if not pmids:
                return []

            time.sleep(self.rate_limit_delay)
            articles = self._fetch_article_details(pmids)

            return articles

        except Exception as e:
            logger.error(f"Interaction search error: {e}")
            return []
