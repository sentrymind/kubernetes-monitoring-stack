"""
FastAPI main application
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from pathlib import Path
import time
from typing import List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared import (
    SearchRequest, SearchResponse, Paper, Source,
    PubMedClient, ArxivClient, SemanticSearchEngine,
    ResearchAnalytics, ResearchVisualizer,
    setup_logging, create_directories
)

# Initialize
logger = setup_logging(__name__)
create_directories()

# Create FastAPI app
app = FastAPI(
    title="Research Agent API",
    description="AI-powered research paper search and analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

# Initialize clients
pubmed_email = os.getenv("PUBMED_EMAIL", "research-agent@example.com")
pubmed_client = PubMedClient(email=pubmed_email)
arxiv_client = ArxivClient()
semantic_engine = None  # Lazy loading


def get_semantic_engine():
    """Lazy load semantic search engine"""
    global semantic_engine
    if semantic_engine is None:
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        semantic_engine = SemanticSearchEngine(model_name=model_name)
    return semantic_engine


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve frontend"""
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>Research Agent API</h1><p>Use /docs for API documentation</p>")


@app.post("/api/search", response_model=SearchResponse)
async def search_papers(request: SearchRequest):
    """
    Search for research papers

    Args:
        request: Search request with query and parameters

    Returns:
        SearchResponse with papers and metadata
    """
    start_time = time.time()
    logger.info(f"Search request: {request.query}")

    all_papers = []

    # Search PubMed
    if Source.PUBMED in request.sources or Source.ALL in request.sources:
        try:
            pubmed_papers = pubmed_client.search(
                query=request.query,
                max_results=request.max_results,
                start_year=request.start_year,
                end_year=request.end_year
            )
            all_papers.extend(pubmed_papers)
            logger.info(f"Found {len(pubmed_papers)} PubMed papers")
        except Exception as e:
            logger.error(f"PubMed search failed: {e}")

    # Search arXiv
    if Source.ARXIV in request.sources or Source.ALL in request.sources:
        try:
            arxiv_papers = arxiv_client.search(
                query=request.query,
                max_results=request.max_results,
                start_year=request.start_year,
                end_year=request.end_year
            )
            all_papers.extend(arxiv_papers)
            logger.info(f"Found {len(arxiv_papers)} arXiv papers")
        except Exception as e:
            logger.error(f"arXiv search failed: {e}")

    # Apply semantic ranking if requested
    if request.semantic_search and all_papers:
        try:
            engine = get_semantic_engine()
            ranked_papers = engine.rank_papers(
                query=request.query,
                papers=all_papers,
                top_k=request.max_results
            )
            all_papers = [paper for paper, score in ranked_papers]
            logger.info("Applied semantic ranking")
        except Exception as e:
            logger.error(f"Semantic ranking failed: {e}")

    # Limit results
    all_papers = all_papers[:request.max_results]

    search_time = time.time() - start_time

    return SearchResponse(
        query=request.query,
        total_results=len(all_papers),
        papers=all_papers,
        search_time=search_time
    )


@app.post("/api/visualize/timeline")
async def create_timeline_viz(papers: List[Paper]):
    """
    Create publication timeline visualization

    Args:
        papers: List of papers

    Returns:
        Path to visualization file
    """
    try:
        visualizer = ResearchVisualizer()
        filepath = visualizer.plot_timeline(papers)

        if filepath:
            return {"success": True, "file": filepath}
        else:
            raise HTTPException(status_code=400, detail="Failed to create visualization")
    except Exception as e:
        logger.error(f"Timeline visualization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/visualize/wordcloud")
async def create_wordcloud_viz(papers: List[Paper]):
    """
    Create word cloud visualization

    Args:
        papers: List of papers

    Returns:
        Path to visualization file
    """
    try:
        visualizer = ResearchVisualizer()
        filepath = visualizer.plot_wordcloud(papers)

        if filepath:
            return {"success": True, "file": filepath}
        else:
            raise HTTPException(status_code=400, detail="Failed to create visualization")
    except Exception as e:
        logger.error(f"Word cloud visualization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/visualize/coauthors")
async def create_coauthor_viz(papers: List[Paper]):
    """
    Create co-author network visualization

    Args:
        papers: List of papers

    Returns:
        Path to visualization file
    """
    try:
        visualizer = ResearchVisualizer()
        filepath = visualizer.plot_coauthor_network(papers)

        if filepath:
            return {"success": True, "file": filepath}
        else:
            raise HTTPException(status_code=400, detail="Failed to create visualization")
    except Exception as e:
        logger.error(f"Co-author network visualization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/visualize/trends")
async def create_trends_viz(papers: List[Paper], keywords: List[str] = None):
    """
    Create keyword trends visualization

    Args:
        papers: List of papers
        keywords: Optional list of keywords to track

    Returns:
        Path to visualization file
    """
    try:
        visualizer = ResearchVisualizer()
        filepath = visualizer.plot_keyword_trends(papers, keywords=keywords)

        if filepath:
            return {"success": True, "file": filepath}
        else:
            raise HTTPException(status_code=400, detail="Failed to create visualization")
    except Exception as e:
        logger.error(f"Trends visualization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def analyze_papers(papers: List[Paper]):
    """
    Analyze papers and return statistics

    Args:
        papers: List of papers

    Returns:
        Analysis results
    """
    try:
        analytics = ResearchAnalytics(papers)

        return {
            "summary": analytics.get_summary_statistics(),
            "timeline": analytics.get_publication_timeline(),
            "top_keywords": analytics.extract_trending_keywords(top_n=20),
            "top_authors": analytics.get_top_authors(top_n=10),
            "top_journals": analytics.get_top_journals(top_n=10),
            "source_distribution": analytics.get_source_distribution()
        }
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "pubmed": "available",
            "arxiv": "available",
            "semantic_search": "available" if semantic_engine else "not loaded"
        }
    }


@app.get("/visualizations/{filename}")
async def get_visualization(filename: str):
    """
    Get visualization file

    Args:
        filename: Name of the visualization file

    Returns:
        File response
    """
    filepath = Path("visualizations") / filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Visualization not found")

    return FileResponse(filepath)


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))

    logger.info(f"Starting Research Agent API on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
