"""
PubMed API client using Biopython
"""
from Bio import Entrez
from typing import List, Optional, Dict, Any
from datetime import datetime
import time
from .models import Paper, Source
from .utils import setup_logging

logger = setup_logging(__name__)


class PubMedClient:
    """Client for PubMed/NCBI Entrez API"""

    def __init__(self, email: str, tool: str = "research-agent"):
        """
        Initialize PubMed client

        Args:
            email: Email for NCBI (required)
            tool: Tool name for NCBI
        """
        Entrez.email = email
        Entrez.tool = tool
        self.max_retries = 3
        self.retry_delay = 2

    def search(
        self,
        query: str,
        max_results: int = 50,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> List[Paper]:
        """
        Search PubMed for papers

        Args:
            query: Search query
            max_results: Maximum number of results
            start_year: Filter by start year
            end_year: Filter by end year

        Returns:
            List of Paper objects
        """
        # Build search term with date filters
        search_term = query

        if start_year and end_year:
            search_term += f" AND {start_year}:{end_year}[pdat]"
        elif start_year:
            search_term += f" AND {start_year}:3000[pdat]"
        elif end_year:
            search_term += f" AND 1900:{end_year}[pdat]"

        logger.info(f"Searching PubMed: {search_term}")

        try:
            # Search for PMIDs
            handle = Entrez.esearch(
                db="pubmed",
                term=search_term,
                retmax=max_results,
                sort="relevance"
            )
            record = Entrez.read(handle)
            handle.close()

            pmids = record["IdList"]
            logger.info(f"Found {len(pmids)} PubMed IDs")

            if not pmids:
                return []

            # Fetch details for each PMID
            papers = []
            batch_size = 20

            for i in range(0, len(pmids), batch_size):
                batch_pmids = pmids[i:i + batch_size]
                batch_papers = self._fetch_details(batch_pmids)
                papers.extend(batch_papers)
                time.sleep(0.5)  # Rate limiting

            return papers

        except Exception as e:
            logger.error(f"PubMed search error: {e}")
            return []

    def _fetch_details(self, pmids: List[str]) -> List[Paper]:
        """
        Fetch paper details for given PMIDs

        Args:
            pmids: List of PubMed IDs

        Returns:
            List of Paper objects
        """
        papers = []

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
                    paper = self._parse_record(record)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    logger.warning(f"Error parsing record: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error fetching details: {e}")

        return papers

    def _parse_record(self, record: Dict[str, Any]) -> Optional[Paper]:
        """
        Parse PubMed record to Paper object

        Args:
            record: PubMed XML record

        Returns:
            Paper object or None
        """
        try:
            article = record['MedlineCitation']['Article']
            pmid = str(record['MedlineCitation']['PMID'])

            # Title
            title = article.get('ArticleTitle', '')

            # Authors
            authors = []
            if 'AuthorList' in article:
                for author in article['AuthorList']:
                    if 'LastName' in author and 'ForeName' in author:
                        name = f"{author['ForeName']} {author['LastName']}"
                        authors.append(name)

            # Abstract
            abstract = ""
            if 'Abstract' in article and 'AbstractText' in article['Abstract']:
                abstract_parts = article['Abstract']['AbstractText']
                if isinstance(abstract_parts, list):
                    abstract = " ".join(str(part) for part in abstract_parts)
                else:
                    abstract = str(abstract_parts)

            # Publication date
            pub_date = None
            year = None

            if 'Journal' in article and 'JournalIssue' in article['Journal']:
                issue = article['Journal']['JournalIssue']
                if 'PubDate' in issue:
                    date_info = issue['PubDate']
                    year = int(date_info.get('Year', 0))
                    if year:
                        try:
                            month = date_info.get('Month', '01')
                            if isinstance(month, str) and not month.isdigit():
                                month = self._month_to_number(month)
                            day = date_info.get('Day', '01')
                            pub_date = datetime(year, int(month), int(day))
                        except:
                            pub_date = datetime(year, 1, 1)

            # Journal
            journal = ""
            if 'Journal' in article and 'Title' in article['Journal']:
                journal = article['Journal']['Title']

            # DOI
            doi = None
            if 'ELocationID' in article:
                for eid in article['ELocationID']:
                    if eid.attributes.get('EIdType') == 'doi':
                        doi = str(eid)

            # Keywords
            keywords = []
            if 'MeshHeadingList' in record['MedlineCitation']:
                for mesh in record['MedlineCitation']['MeshHeadingList']:
                    if 'DescriptorName' in mesh:
                        keywords.append(str(mesh['DescriptorName']))

            # URL
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

            return Paper(
                id=f"pubmed_{pmid}",
                title=title,
                authors=authors,
                abstract=abstract,
                publication_date=pub_date,
                year=year,
                source=Source.PUBMED,
                doi=doi,
                url=url,
                keywords=keywords,
                journal=journal
            )

        except Exception as e:
            logger.error(f"Error parsing record: {e}")
            return None

    @staticmethod
    def _month_to_number(month: str) -> int:
        """Convert month name to number"""
        months = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
            'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        return months.get(month[:3].lower(), 1)
