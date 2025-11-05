"""
Semantic search using sentence transformers
"""
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Tuple
import os
from .models import Paper
from .utils import setup_logging

logger = setup_logging(__name__)


class SemanticSearchEngine:
    """Semantic search engine using sentence transformers"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize semantic search engine

        Args:
            model_name: Name of the sentence transformer model
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info("Embedding model loaded successfully")

    def encode_query(self, query: str) -> np.ndarray:
        """
        Encode search query into vector

        Args:
            query: Search query text

        Returns:
            Query embedding vector
        """
        return self.model.encode([query])[0]

    def encode_papers(self, papers: List[Paper]) -> List[np.ndarray]:
        """
        Encode paper abstracts into vectors

        Args:
            papers: List of papers

        Returns:
            List of embedding vectors
        """
        # Combine title and abstract for better embedding
        texts = []
        for paper in papers:
            text = f"{paper.title}. {paper.abstract}"
            texts.append(text)

        logger.info(f"Encoding {len(texts)} papers...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        logger.info("Encoding completed")

        return embeddings

    def rank_papers(
        self,
        query: str,
        papers: List[Paper],
        top_k: int = None
    ) -> List[Tuple[Paper, float]]:
        """
        Rank papers by semantic similarity to query

        Args:
            query: Search query
            papers: List of papers to rank
            top_k: Return top K results (None = all)

        Returns:
            List of (paper, similarity_score) tuples, sorted by score
        """
        if not papers:
            return []

        # Encode query
        query_embedding = self.encode_query(query)

        # Encode papers
        paper_embeddings = self.encode_papers(papers)

        # Calculate similarities
        similarities = cosine_similarity(
            [query_embedding],
            paper_embeddings
        )[0]

        # Combine papers with scores
        paper_scores = list(zip(papers, similarities))

        # Sort by similarity (descending)
        paper_scores.sort(key=lambda x: x[1], reverse=True)

        # Add similarity scores to papers
        for paper, score in paper_scores:
            paper.similarity_score = float(score)

        # Return top K
        if top_k:
            return paper_scores[:top_k]

        return paper_scores

    def find_similar_papers(
        self,
        target_paper: Paper,
        candidate_papers: List[Paper],
        threshold: float = 0.7,
        top_k: int = 10
    ) -> List[Tuple[Paper, float]]:
        """
        Find papers similar to a target paper

        Args:
            target_paper: Target paper
            candidate_papers: List of candidate papers
            threshold: Minimum similarity threshold
            top_k: Maximum number of results

        Returns:
            List of (paper, similarity_score) tuples
        """
        if not candidate_papers:
            return []

        # Encode target paper
        target_text = f"{target_paper.title}. {target_paper.abstract}"
        target_embedding = self.model.encode([target_text])[0]

        # Encode candidate papers
        candidate_embeddings = self.encode_papers(candidate_papers)

        # Calculate similarities
        similarities = cosine_similarity(
            [target_embedding],
            candidate_embeddings
        )[0]

        # Filter by threshold and combine with papers
        results = []
        for paper, score in zip(candidate_papers, similarities):
            if score >= threshold and paper.id != target_paper.id:
                paper.similarity_score = float(score)
                results.append((paper, float(score)))

        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:top_k]

    def cluster_papers(
        self,
        papers: List[Paper],
        n_clusters: int = 5
    ) -> List[List[Paper]]:
        """
        Cluster papers by semantic similarity

        Args:
            papers: List of papers to cluster
            n_clusters: Number of clusters

        Returns:
            List of paper clusters
        """
        from sklearn.cluster import KMeans

        if len(papers) < n_clusters:
            return [papers]

        # Encode papers
        embeddings = self.encode_papers(papers)

        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(embeddings)

        # Group papers by cluster
        clusters = [[] for _ in range(n_clusters)]
        for paper, label in zip(papers, labels):
            clusters[label].append(paper)

        return clusters
