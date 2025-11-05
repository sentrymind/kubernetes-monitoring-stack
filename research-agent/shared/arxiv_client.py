"""
arXiv API client
"""
import arxiv
from typing import List, Optional
from datetime import datetime
from .models import Paper, Source
from .utils import setup_logging

logger = setup_logging(__name__)


class ArxivClient:
    """Client for arXiv API"""

    def __init__(self):
        """Initialize arXiv client"""
        self.client = arxiv.Client()

    def search(
        self,
        query: str,
        max_results: int = 50,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> List[Paper]:
        """
        Search arXiv for papers

        Args:
            query: Search query
            max_results: Maximum number of results
            start_year: Filter by start year
            end_year: Filter by end year

        Returns:
            List of Paper objects
        """
        logger.info(f"Searching arXiv: {query}")

        try:
            # Create search
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )

            papers = []

            # Fetch results
            for result in self.client.results(search):
                paper = self._parse_result(result)

                # Apply year filters
                if start_year and paper.year and paper.year < start_year:
                    continue
                if end_year and paper.year and paper.year > end_year:
                    continue

                papers.append(paper)

            logger.info(f"Found {len(papers)} arXiv papers")
            return papers

        except Exception as e:
            logger.error(f"arXiv search error: {e}")
            return []

    def _parse_result(self, result: arxiv.Result) -> Paper:
        """
        Parse arXiv result to Paper object

        Args:
            result: arXiv search result

        Returns:
            Paper object
        """
        # Extract arXiv ID
        arxiv_id = result.entry_id.split('/abs/')[-1]

        # Authors
        authors = [str(author) for author in result.authors]

        # Publication date
        pub_date = result.published
        year = pub_date.year if pub_date else None

        # Categories as keywords
        keywords = result.categories

        # DOI
        doi = result.doi

        # URL
        url = result.entry_id

        return Paper(
            id=f"arxiv_{arxiv_id}",
            title=result.title,
            authors=authors,
            abstract=result.summary,
            publication_date=pub_date,
            year=year,
            source=Source.ARXIV,
            doi=doi,
            url=url,
            keywords=keywords,
            journal=result.journal_ref
        )
