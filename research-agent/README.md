# 🔬 Research Agent

AI-powered scientific research paper search and analysis platform with semantic search, trend analysis, and advanced visualizations.

## Features

### 🔍 Multi-Source Search
- **PubMed Integration**: Access to millions of biomedical papers via NCBI Entrez API
- **arXiv Integration**: Full-text preprints from physics, mathematics, CS, and more
- **Semantic Search**: Vector-based similarity ranking using sentence transformers
- **Advanced Filters**: Filter by year range, source, and relevance

### 📊 Analytics & Visualizations
- **Publication Timeline**: Track research trends over time
- **Keyword Trends**: Analyze keyword frequency by year
- **Word Clouds**: Visual representation of trending topics
- **Co-Author Networks**: Interactive collaboration network graphs
- **Statistical Analysis**: Comprehensive metrics on papers, authors, and journals

### 🚀 Technology Stack
- **Backend**: FastAPI (Python)
- **Search**: Biopython (PubMed), arxiv-py (arXiv)
- **NLP**: Sentence-Transformers, scikit-learn
- **Visualization**: Plotly, Matplotlib, WordCloud, NetworkX
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Infrastructure**: Docker, Redis (optional)

## Architecture

```
research-agent/
├── api/                    # FastAPI backend
│   └── main.py            # API endpoints
├── shared/                # Shared modules
│   ├── models.py         # Data models
│   ├── pubmed_client.py  # PubMed integration
│   ├── arxiv_client.py   # arXiv integration
│   ├── semantic_search.py # Semantic search engine
│   ├── analytics.py      # Trend analysis
│   └── visualizations.py # Visualization generators
├── frontend/              # Web interface
│   ├── index.html
│   ├── style.css
│   └── app.js
├── data/                  # Data storage
├── visualizations/        # Generated visualizations
└── docker-compose.yml    # Docker configuration
```

## Installation

### Method 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd research-agent
```

2. Create `.env` file:
```bash
cp .env.example .env
# Edit .env and set PUBMED_EMAIL to your email
```

3. Build and run:
```bash
docker-compose up -d
```

4. Access the application:
- Web Interface: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Method 2: Local Installation

1. Install Python 3.11+

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
export PUBMED_EMAIL="your.email@example.com"
export API_HOST="0.0.0.0"
export API_PORT="8000"
```

5. Run the application:
```bash
python api/main.py
```

6. Access: http://localhost:8000

## Usage

### Web Interface

1. Open http://localhost:8000 in your browser
2. Enter your search query (e.g., "machine learning in healthcare")
3. Select data sources (PubMed, arXiv, or both)
4. Configure filters (year range, max results, semantic search)
5. Click "Search" to retrieve papers
6. Explore visualizations and analysis

### API Endpoints

#### Search Papers
```bash
POST /api/search
Content-Type: application/json

{
  "query": "deep learning",
  "sources": ["pubmed", "arxiv"],
  "max_results": 50,
  "start_year": 2020,
  "end_year": 2024,
  "semantic_search": true
}
```

#### Analyze Papers
```bash
POST /api/analyze
Content-Type: application/json

[
  {
    "id": "paper_1",
    "title": "...",
    "authors": [...],
    "abstract": "...",
    ...
  }
]
```

#### Create Visualizations
```bash
POST /api/visualize/timeline
POST /api/visualize/wordcloud
POST /api/visualize/coauthors
POST /api/visualize/trends
```

### Python SDK

```python
from shared import PubMedClient, ArxivClient, SemanticSearchEngine

# Initialize clients
pubmed = PubMedClient(email="your.email@example.com")
arxiv = ArxivClient()

# Search PubMed
pubmed_papers = pubmed.search(
    query="machine learning",
    max_results=50,
    start_year=2020
)

# Search arXiv
arxiv_papers = arxiv.search(
    query="deep learning",
    max_results=50
)

# Semantic ranking
semantic_engine = SemanticSearchEngine()
ranked_papers = semantic_engine.rank_papers(
    query="neural networks",
    papers=pubmed_papers + arxiv_papers,
    top_k=20
)

# Analyze and visualize
from shared import ResearchAnalytics, ResearchVisualizer

analytics = ResearchAnalytics(ranked_papers)
stats = analytics.get_summary_statistics()
keywords = analytics.extract_trending_keywords(top_n=20)

visualizer = ResearchVisualizer()
visualizer.plot_timeline(ranked_papers)
visualizer.plot_wordcloud(ranked_papers)
visualizer.plot_coauthor_network(ranked_papers)
```

## API Documentation

Full interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Features in Detail

### Semantic Search
Uses Sentence-BERT (all-MiniLM-L6-v2) to:
- Encode paper abstracts and titles into 384-dimensional vectors
- Calculate cosine similarity between query and papers
- Rank results by semantic relevance, not just keyword matching
- Find similar papers based on content

### Trend Analysis
- Extract keywords from titles and abstracts
- Track keyword frequency over time
- Identify emerging research topics
- Analyze author collaboration patterns
- Determine top journals and venues

### Visualizations
1. **Publication Timeline**: Line chart showing papers per year
2. **Word Cloud**: Visual frequency map of keywords
3. **Co-Author Network**: Graph showing author collaborations
4. **Keyword Trends**: Multi-line chart tracking keywords over time
5. **Source Distribution**: Pie chart of paper sources

## Configuration

### Environment Variables
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# PubMed (required by NCBI)
PUBMED_EMAIL=your.email@example.com

# Semantic Search Model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Embedding Models
You can use different sentence-transformer models:
- `all-MiniLM-L6-v2` (default, fast, 384 dims)
- `all-mpnet-base-v2` (better quality, 768 dims)
- `multi-qa-MiniLM-L6-cos-v1` (optimized for questions)

## Performance

- **PubMed**: ~2-5 seconds for 50 papers
- **arXiv**: ~1-3 seconds for 50 papers
- **Semantic Encoding**: ~1 second per 50 abstracts
- **Visualizations**: ~1-3 seconds each

## Limitations

- **PubMed**: Rate limited to 3 requests/second by NCBI
- **arXiv**: Limited to 100 results per query
- **Semantic Search**: Requires ~500MB RAM for model
- **Long Abstracts**: Truncated to 512 tokens for embedding

## Troubleshooting

### Import Errors
```bash
# Ensure you're in the project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Model Download Issues
```bash
# Pre-download the embedding model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### PubMed Errors
- Set `PUBMED_EMAIL` to a valid email address
- Check NCBI API status: https://www.ncbi.nlm.nih.gov/

### Memory Issues
- Use a smaller embedding model
- Reduce `max_results` in searches
- Increase Docker memory limit

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Code Style
```bash
black api/ shared/
flake8 api/ shared/
```

### Adding New Sources
1. Create client in `shared/<source>_client.py`
2. Implement `search()` method returning `List[Paper]`
3. Add source to `Source` enum in `shared/models.py`
4. Update API endpoints in `api/main.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- **NCBI/PubMed**: https://www.ncbi.nlm.nih.gov/
- **arXiv**: https://arxiv.org/
- **Sentence-Transformers**: https://www.sbert.net/
- **FastAPI**: https://fastapi.tiangolo.com/

## Support

For issues, questions, or contributions:
- GitHub Issues: <repository-url>/issues
- Documentation: <repository-url>/wiki

---

**Version**: 1.0.0
**Last Updated**: 2024
**Created with**: Claude Code
