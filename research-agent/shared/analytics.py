"""
Analytics module for trend analysis
"""
from typing import List, Dict, Any, Tuple
from collections import Counter
import pandas as pd
from .models import Paper
from .utils import extract_keywords, setup_logging

logger = setup_logging(__name__)


class ResearchAnalytics:
    """Analytics for research papers"""

    def __init__(self, papers: List[Paper]):
        """
        Initialize analytics

        Args:
            papers: List of papers to analyze
        """
        self.papers = papers
        self.df = self._papers_to_dataframe()

    def _papers_to_dataframe(self) -> pd.DataFrame:
        """Convert papers to pandas DataFrame"""
        data = []
        for paper in self.papers:
            data.append({
                'id': paper.id,
                'title': paper.title,
                'authors': paper.authors,
                'year': paper.year,
                'source': paper.source.value,
                'abstract': paper.abstract,
                'keywords': paper.keywords,
                'journal': paper.journal
            })
        return pd.DataFrame(data)

    def get_publication_timeline(self) -> Dict[int, int]:
        """
        Get publication counts by year

        Returns:
            Dictionary of {year: count}
        """
        if self.df.empty or 'year' not in self.df.columns:
            return {}

        # Filter out None years
        df_with_years = self.df[self.df['year'].notna()]

        timeline = df_with_years['year'].value_counts().to_dict()
        # Convert to int keys and sort
        timeline = {int(k): int(v) for k, v in timeline.items()}
        return dict(sorted(timeline.items()))

    def extract_trending_keywords(
        self,
        top_n: int = 20,
        min_frequency: int = 2
    ) -> Dict[str, int]:
        """
        Extract trending keywords from papers

        Args:
            top_n: Number of top keywords to return
            min_frequency: Minimum keyword frequency

        Returns:
            Dictionary of {keyword: frequency}
        """
        all_keywords = []

        # Collect keywords from metadata
        for keywords in self.df['keywords']:
            if isinstance(keywords, list):
                all_keywords.extend([k.lower() for k in keywords])

        # Also extract from titles and abstracts
        for _, row in self.df.iterrows():
            text = f"{row['title']} {row['abstract']}"
            extracted = extract_keywords(text, top_n=10)
            all_keywords.extend(extracted)

        # Count frequencies
        keyword_counts = Counter(all_keywords)

        # Filter by minimum frequency
        filtered = {
            k: v for k, v in keyword_counts.items()
            if v >= min_frequency
        }

        # Get top N
        top_keywords = dict(
            sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:top_n]
        )

        return top_keywords

    def get_keyword_trends_by_year(
        self,
        keywords: List[str] = None,
        top_n: int = 10
    ) -> Dict[str, Dict[int, int]]:
        """
        Track keyword frequency over years

        Args:
            keywords: Specific keywords to track (None = auto-detect top)
            top_n: Number of top keywords if auto-detecting

        Returns:
            Dictionary of {keyword: {year: count}}
        """
        if keywords is None:
            # Auto-detect top keywords
            all_keywords = self.extract_trending_keywords(top_n=top_n)
            keywords = list(all_keywords.keys())

        keyword_trends = {kw: {} for kw in keywords}

        for _, row in self.df.iterrows():
            year = row['year']
            if pd.isna(year):
                continue

            year = int(year)

            # Check title and abstract for keywords
            text = f"{row['title']} {row['abstract']}".lower()

            for keyword in keywords:
                if keyword.lower() in text:
                    if year not in keyword_trends[keyword]:
                        keyword_trends[keyword][year] = 0
                    keyword_trends[keyword][year] += 1

        # Sort years for each keyword
        for keyword in keyword_trends:
            keyword_trends[keyword] = dict(sorted(keyword_trends[keyword].items()))

        return keyword_trends

    def get_top_authors(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Get most prolific authors

        Args:
            top_n: Number of top authors

        Returns:
            List of {author, count, papers}
        """
        author_counts = Counter()
        author_papers = {}

        for _, row in self.df.iterrows():
            if isinstance(row['authors'], list):
                for author in row['authors']:
                    author_counts[author] += 1
                    if author not in author_papers:
                        author_papers[author] = []
                    author_papers[author].append(row['title'])

        top_authors = []
        for author, count in author_counts.most_common(top_n):
            top_authors.append({
                'author': author,
                'paper_count': count,
                'papers': author_papers[author][:5]  # Sample of papers
            })

        return top_authors

    def get_top_journals(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Get top journals by publication count

        Args:
            top_n: Number of top journals

        Returns:
            List of {journal, count}
        """
        df_with_journal = self.df[self.df['journal'].notna()]

        if df_with_journal.empty:
            return []

        journal_counts = df_with_journal['journal'].value_counts()

        top_journals = []
        for journal, count in journal_counts.head(top_n).items():
            top_journals.append({
                'journal': journal,
                'paper_count': int(count)
            })

        return top_journals

    def get_coauthor_network(self) -> List[Tuple[str, str, int]]:
        """
        Build co-author network

        Returns:
            List of (author1, author2, collaboration_count) edges
        """
        edges = Counter()

        for _, row in self.df.iterrows():
            if isinstance(row['authors'], list) and len(row['authors']) > 1:
                authors = sorted(row['authors'])
                # Create edges between all pairs
                for i in range(len(authors)):
                    for j in range(i + 1, len(authors)):
                        edge = (authors[i], authors[j])
                        edges[edge] += 1

        # Convert to list
        network = [(a1, a2, count) for (a1, a2), count in edges.items()]
        network.sort(key=lambda x: x[2], reverse=True)

        return network

    def get_source_distribution(self) -> Dict[str, int]:
        """
        Get distribution of papers by source

        Returns:
            Dictionary of {source: count}
        """
        return dict(self.df['source'].value_counts())

    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics

        Returns:
            Dictionary with various statistics
        """
        stats = {
            'total_papers': len(self.papers),
            'total_authors': len(set([
                author for authors in self.df['authors']
                for author in (authors if isinstance(authors, list) else [])
            ])),
            'date_range': {
                'start': int(self.df['year'].min()) if not self.df['year'].isna().all() else None,
                'end': int(self.df['year'].max()) if not self.df['year'].isna().all() else None
            },
            'sources': self.get_source_distribution(),
            'avg_authors_per_paper': self.df['authors'].apply(
                lambda x: len(x) if isinstance(x, list) else 0
            ).mean()
        }

        return stats
