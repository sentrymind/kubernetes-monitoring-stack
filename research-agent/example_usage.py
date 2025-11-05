"""
Example usage of Research Agent Python SDK
"""
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from shared import (
    PubMedClient, ArxivClient, SemanticSearchEngine,
    ResearchAnalytics, ResearchVisualizer
)


def main():
    print("🔬 Research Agent - Python SDK Example")
    print("=" * 50)

    # Initialize clients
    print("\n1. Initializing clients...")
    pubmed = PubMedClient(email="research-agent@example.com")
    arxiv = ArxivClient()

    # Search query
    query = "machine learning in healthcare"
    print(f"\n2. Searching for: '{query}'")

    # Search PubMed
    print("\n   Searching PubMed...")
    pubmed_papers = pubmed.search(
        query=query,
        max_results=20,
        start_year=2022
    )
    print(f"   Found {len(pubmed_papers)} PubMed papers")

    # Search arXiv
    print("\n   Searching arXiv...")
    arxiv_papers = arxiv.search(
        query=query,
        max_results=20,
        start_year=2022
    )
    print(f"   Found {len(arxiv_papers)} arXiv papers")

    # Combine results
    all_papers = pubmed_papers + arxiv_papers
    print(f"\n   Total papers: {len(all_papers)}")

    # Semantic ranking
    print("\n3. Applying semantic search...")
    semantic_engine = SemanticSearchEngine()

    ranked_papers = semantic_engine.rank_papers(
        query=query,
        papers=all_papers,
        top_k=20
    )

    print(f"   Ranked {len(ranked_papers)} papers by relevance")

    # Show top 5
    print("\n   Top 5 papers:")
    for i, (paper, score) in enumerate(ranked_papers[:5], 1):
        print(f"   {i}. [{score:.3f}] {paper.title[:80]}...")

    # Analytics
    print("\n4. Running analytics...")
    papers = [p for p, s in ranked_papers]
    analytics = ResearchAnalytics(papers)

    stats = analytics.get_summary_statistics()
    print(f"\n   Summary:")
    print(f"   - Total papers: {stats['total_papers']}")
    print(f"   - Total authors: {stats['total_authors']}")
    print(f"   - Date range: {stats['date_range']['start']} - {stats['date_range']['end']}")

    keywords = analytics.extract_trending_keywords(top_n=10)
    print(f"\n   Top keywords:")
    for i, (kw, count) in enumerate(list(keywords.items())[:5], 1):
        print(f"   {i}. {kw}: {count}")

    # Visualizations
    print("\n5. Creating visualizations...")
    visualizer = ResearchVisualizer()

    timeline_path = visualizer.plot_timeline(papers)
    print(f"   Timeline: {timeline_path}")

    wordcloud_path = visualizer.plot_wordcloud(papers)
    print(f"   Word cloud: {wordcloud_path}")

    network_path = visualizer.plot_coauthor_network(papers, min_collaborations=1)
    if network_path:
        print(f"   Co-author network: {network_path}")

    trends_path = visualizer.plot_keyword_trends(papers, top_n=3)
    if trends_path:
        print(f"   Keyword trends: {trends_path}")

    print("\n✅ Done! Check the visualizations/ directory")


if __name__ == "__main__":
    main()
