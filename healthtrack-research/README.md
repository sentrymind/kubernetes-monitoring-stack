# 💊 HealthTrack Research

**Evidence-based supplement tracking with PubMed integration**

Comprehensive platform that combines supplement tracking with automatic research analysis from PubMed. Get evidence-based dosage recommendations, track interactions, and generate personalized reports.

## 🌟 Features

### Core Functionality
- ✅ **Supplement Management**: Track multiple supplements with dosages and schedules
- ✅ **Daily Intake Logging**: Record intake with wellbeing metrics (energy, sleep, mood)
- ✅ **Automatic Research Search**: Auto-search PubMed when adding supplements
- ✅ **Evidence Caching**: Smart caching of research articles (no API spam)
- ✅ **Dosage Analysis**: Compare your dosage against RCT/systematic review recommendations
- ✅ **Interaction Checking**: Detect potential supplement-supplement interactions
- ✅ **Evidence Summaries**: Visual breakdowns of study quality and timeline

### Research Integration
- **PubMed Auto-Search**: Automatically finds RCTs, systematic reviews, and meta-analyses
- **Evidence Levels**: Categorizes studies by quality (high/medium/low)
- **Dosage Extraction**: Parses abstracts for recommended dosages
- **Key Findings**: Extracts conclusions from research papers
- **Smart Filtering**: 2015-2025, humans, adults only

### Analytics & Visualization
- **Timeline Charts**: Publication trends over years
- **Evidence Quality Pie Charts**: Distribution of study types
- **Dosage Comparison**: Visual comparison of your dosage vs recommendations
- **Compliance Tracking**: Monitor adherence over time

## 🏗️ Architecture

```
healthtrack-research/
├── backend/                  # FastAPI backend
│   ├── main.py              # REST API endpoints
│   ├── database.py          # SQLAlchemy models
│   ├── pubmed_service.py    # PubMed integration
│   └── analyzer.py          # Dosage & interaction analysis
├── frontend/                 # Streamlit frontend
│   └── app.py               # Web interface
├── data/                     # SQLite database
├── tests/                    # Unit tests
├── docker-compose.yml        # Docker orchestration
└── requirements.txt          # Python dependencies
```

## 🚀 Quick Start

### Method 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd healthtrack-research
```

2. Create `.env` file:
```bash
cp .env.example .env
# Edit .env and set PUBMED_EMAIL
```

3. Start with Docker Compose:
```bash
docker-compose up -d
```

4. Access the applications:
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

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
```

5. Initialize database:
```bash
python -c "from backend.database import init_db; init_db()"
```

6. Start backend:
```bash
cd backend
python main.py
```

7. Start frontend (in another terminal):
```bash
streamlit run frontend/app.py
```

## 📖 Usage Guide

### Adding Your First Supplement

1. Go to **"Add Supplement"** page
2. Enter supplement details:
   - Name: "Vitamin D3"
   - Dosage: 5000
   - Unit: IU
   - Frequency: Daily
3. Check **"Auto-search research"** (enabled by default)
4. Click **"Add Supplement"**

The system will automatically:
- Search PubMed for high-quality research
- Cache 15-20 relevant studies
- Extract dosage recommendations
- Categorize evidence quality

### Tracking Daily Intake

1. Go to **"Track Intake"** page
2. Select date (defaults to today)
3. For each supplement:
   - Check "Taken" if you took it
   - Rate energy level (1-10)
   - Rate sleep quality (1-10)
   - Add optional notes
4. Click **"Save Log"**

### Analyzing Dosages

1. Go to **"Analysis"** page
2. Select a supplement
3. View:
   - **Status**: Optimal / Above / Below recommended range
   - **Recommended Range**: Based on research
   - **Visual Comparison**: Your dosage vs. recommendations
   - **Top Sources**: PMIDs with evidence levels

Example output:
```
Status: ABOVE
Your dosage: 5000 IU
Recommended: 2000-4000 IU (based on 12 RCTs)
Top Sources:
- 4000 IU - PMID: 12345678 (2023) - Evidence: high
- 3000 IU - PMID: 87654321 (2022) - Evidence: high
```

### Viewing Research

1. Go to **"Research"** page
2. Select supplement
3. Browse articles sorted by:
   - Evidence quality (high → low)
   - Publication year (newest first)
4. For each article, view:
   - Title, authors, journal
   - Publication type (RCT, SR, etc.)
   - Evidence level
   - Key findings
   - Recommended dosage
   - Link to PubMed

### Checking Interactions

*Coming soon in v1.1*

## 🔧 API Documentation

Full interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

#### Supplements
```bash
# Create supplement with auto-search
POST /api/supplements
{
  "name": "Omega-3",
  "dosage": 1000,
  "dosage_unit": "mg",
  "frequency": "daily",
  "auto_search": true
}

# Get all supplements
GET /api/supplements

# Update supplement
PUT /api/supplements/{id}

# Delete supplement
DELETE /api/supplements/{id}
```

#### Intake Logging
```bash
# Log intake
POST /api/intake
{
  "supplement_id": 1,
  "date": "2024-11-05",
  "taken": true,
  "energy_level": 8,
  "sleep_quality": 7
}

# Get intake logs
GET /api/intake/{supplement_id}?start_date=2024-11-01&end_date=2024-11-30
```

#### Research
```bash
# Get cached research
GET /api/research/{supplement_id}

# Refresh research from PubMed
POST /api/research/refresh/{supplement_id}
```

#### Analysis
```bash
# Analyze dosage
GET /api/analyze/dosage/{supplement_id}

# Get evidence summary
GET /api/analyze/evidence/{supplement_id}

# Check interactions
POST /api/analyze/interactions
["1", "2", "3"]  # supplement IDs
```

## 📊 Database Schema

### Tables

**supplements**
- id, name, dosage, dosage_unit, frequency
- user_notes, created_at, updated_at

**intake_log**
- id, supplement_id, date, taken
- energy_level, sleep_quality, mood_level
- notes, time_taken

**research_cache**
- id, supplement_id, pmid
- title, abstract, year, publication_type
- evidence_level, recommended_dosage
- key_findings, authors, journal, doi

**interactions**
- id, supplement_a_id, supplement_b_id
- interaction_type, severity
- description, source_pmid

## 🧪 Testing

Run tests:
```bash
pytest tests/ -v
```

With coverage:
```bash
pytest tests/ --cov=backend --cov-report=html
```

## 🐳 Docker

Build images:
```bash
docker-compose build
```

Start services:
```bash
docker-compose up -d
```

View logs:
```bash
docker-compose logs -f
```

Stop services:
```bash
docker-compose down
```

## 🔒 Environment Variables

Create `.env` file:

```bash
# Required
PUBMED_EMAIL=your.email@example.com

# Optional
DATABASE_URL=sqlite:///data/healthtrack.db
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

## 📈 Roadmap

### v1.1 (Next Release)
- [ ] PDF report generation
- [ ] Interaction detection with PubMed
- [ ] Adherence statistics
- [ ] Email reminders

### v2.0 (Future)
- [ ] Multi-user support
- [ ] Mobile app
- [ ] Lab results integration
- [ ] ML-based recommendations
- [ ] Symptom tracking
- [ ] Cost tracking

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **NCBI/PubMed**: https://www.ncbi.nlm.nih.gov/
- **Biopython**: https://biopython.org/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Streamlit**: https://streamlit.io/

## 📧 Support

For issues, questions, or contributions:
- GitHub Issues: <repository-url>/issues
- Documentation: <repository-url>/wiki

---

**Version**: 1.0.0
**Last Updated**: 2024
**Created with**: Claude Code

## 💡 Tips & Best Practices

### PubMed Search Tips
- Use specific supplement names (e.g., "Vitamin D3" not "Vitamin D")
- System focuses on RCTs and systematic reviews for best evidence
- Research is cached for 90 days to avoid re-querying
- Click "Refresh Research" to update with latest studies

### Dosage Tracking
- Always use the same units for consistency
- Log at the same time each day
- Include wellbeing metrics for correlation analysis
- Add notes about changes (diet, exercise, etc.)

### Evidence Interpretation
- **High Evidence**: Meta-analyses, systematic reviews
- **Medium Evidence**: Randomized controlled trials
- **Low Evidence**: Observational studies, case reports

### Safety Notes
⚠️ **Important Disclaimers**:
- This tool is for informational purposes only
- Always consult healthcare professionals before starting supplements
- Do not exceed recommended dosages without medical supervision
- Report adverse effects to your doctor immediately
- This is not medical advice

---

Made with ❤️ for evidence-based health tracking
