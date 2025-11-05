"""
FastAPI backend for HealthTrack Research
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
import logging

from .database import (
    get_db, init_db, Supplement, IntakeLog,
    ResearchCache, Interaction
)
from .pubmed_service import PubMedService
from .analyzer import DosageAnalyzer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="HealthTrack Research API",
    description="Evidence-based supplement tracking with PubMed integration",
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

# Pydantic models
class SupplementCreate(BaseModel):
    name: str
    dosage: float
    dosage_unit: str
    frequency: str
    user_notes: Optional[str] = None
    auto_search: bool = True

class SupplementUpdate(BaseModel):
    name: Optional[str] = None
    dosage: Optional[float] = None
    dosage_unit: Optional[str] = None
    frequency: Optional[str] = None
    user_notes: Optional[str] = None

class IntakeLogCreate(BaseModel):
    supplement_id: int
    date: date
    taken: bool
    actual_dosage: Optional[float] = None
    energy_level: Optional[int] = None
    sleep_quality: Optional[int] = None
    mood_level: Optional[int] = None
    notes: Optional[str] = None

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    logger.info("Database initialized")

# Health check
@app.get("/api/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": ["database", "pubmed", "analyzer"]
    }

# Supplement endpoints
@app.post("/api/supplements", status_code=201)
async def create_supplement(
    supplement: SupplementCreate,
    db: Session = Depends(get_db)
):
    """Create a new supplement and auto-search research"""
    # Check if supplement already exists
    existing = db.query(Supplement).filter(Supplement.name == supplement.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Supplement already exists")

    # Create supplement
    db_supplement = Supplement(
        name=supplement.name,
        dosage=supplement.dosage,
        dosage_unit=supplement.dosage_unit,
        frequency=supplement.frequency,
        user_notes=supplement.user_notes
    )
    db.add(db_supplement)
    db.commit()
    db.refresh(db_supplement)

    # Auto-search research if requested
    if supplement.auto_search:
        try:
            pubmed_service = PubMedService(db)
            articles = pubmed_service.auto_search_for_supplement(supplement.name)
            cached_count = pubmed_service.cache_research(db_supplement.id, articles)

            logger.info(f"Auto-search completed: {cached_count} articles cached")

            return {
                "id": db_supplement.id,
                "name": db_supplement.name,
                "dosage": db_supplement.dosage,
                "dosage_unit": db_supplement.dosage_unit,
                "research_found": len(articles),
                "research_cached": cached_count
            }
        except Exception as e:
            logger.error(f"Auto-search failed: {e}")
            # Still return supplement even if search fails
            return {
                "id": db_supplement.id,
                "name": db_supplement.name,
                "dosage": db_supplement.dosage,
                "dosage_unit": db_supplement.dosage_unit,
                "research_found": 0,
                "research_cached": 0,
                "warning": "Auto-search failed"
            }

    return {
        "id": db_supplement.id,
        "name": db_supplement.name,
        "dosage": db_supplement.dosage,
        "dosage_unit": db_supplement.dosage_unit
    }

@app.get("/api/supplements")
async def get_supplements(db: Session = Depends(get_db)):
    """Get all supplements"""
    supplements = db.query(Supplement).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "dosage": s.dosage,
            "dosage_unit": s.dosage_unit,
            "frequency": s.frequency,
            "user_notes": s.user_notes,
            "created_at": s.created_at,
            "research_count": len(s.research_cache)
        }
        for s in supplements
    ]

@app.get("/api/supplements/{supplement_id}")
async def get_supplement(supplement_id: int, db: Session = Depends(get_db)):
    """Get specific supplement"""
    supplement = db.query(Supplement).filter(Supplement.id == supplement_id).first()
    if not supplement:
        raise HTTPException(status_code=404, detail="Supplement not found")

    return {
        "id": supplement.id,
        "name": supplement.name,
        "dosage": supplement.dosage,
        "dosage_unit": supplement.dosage_unit,
        "frequency": supplement.frequency,
        "user_notes": supplement.user_notes,
        "created_at": supplement.created_at,
        "research_count": len(supplement.research_cache)
    }

@app.put("/api/supplements/{supplement_id}")
async def update_supplement(
    supplement_id: int,
    supplement: SupplementUpdate,
    db: Session = Depends(get_db)
):
    """Update supplement"""
    db_supplement = db.query(Supplement).filter(Supplement.id == supplement_id).first()
    if not db_supplement:
        raise HTTPException(status_code=404, detail="Supplement not found")

    if supplement.name:
        db_supplement.name = supplement.name
    if supplement.dosage:
        db_supplement.dosage = supplement.dosage
    if supplement.dosage_unit:
        db_supplement.dosage_unit = supplement.dosage_unit
    if supplement.frequency:
        db_supplement.frequency = supplement.frequency
    if supplement.user_notes is not None:
        db_supplement.user_notes = supplement.user_notes

    db_supplement.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Supplement updated successfully"}

@app.delete("/api/supplements/{supplement_id}")
async def delete_supplement(supplement_id: int, db: Session = Depends(get_db)):
    """Delete supplement"""
    db_supplement = db.query(Supplement).filter(Supplement.id == supplement_id).first()
    if not db_supplement:
        raise HTTPException(status_code=404, detail="Supplement not found")

    db.delete(db_supplement)
    db.commit()

    return {"message": "Supplement deleted successfully"}

# Intake log endpoints
@app.post("/api/intake", status_code=201)
async def log_intake(intake: IntakeLogCreate, db: Session = Depends(get_db)):
    """Log daily supplement intake"""
    # Check if supplement exists
    supplement = db.query(Supplement).filter(Supplement.id == intake.supplement_id).first()
    if not supplement:
        raise HTTPException(status_code=404, detail="Supplement not found")

    # Check if log already exists for this date
    existing = db.query(IntakeLog).filter(
        IntakeLog.supplement_id == intake.supplement_id,
        IntakeLog.date == intake.date
    ).first()

    if existing:
        # Update existing log
        existing.taken = intake.taken
        existing.actual_dosage = intake.actual_dosage
        existing.energy_level = intake.energy_level
        existing.sleep_quality = intake.sleep_quality
        existing.mood_level = intake.mood_level
        existing.notes = intake.notes
        existing.time_taken = datetime.utcnow()
    else:
        # Create new log
        db_intake = IntakeLog(
            supplement_id=intake.supplement_id,
            date=intake.date,
            taken=intake.taken,
            actual_dosage=intake.actual_dosage,
            time_taken=datetime.utcnow() if intake.taken else None,
            energy_level=intake.energy_level,
            sleep_quality=intake.sleep_quality,
            mood_level=intake.mood_level,
            notes=intake.notes
        )
        db.add(db_intake)

    db.commit()

    return {"message": "Intake logged successfully"}

@app.get("/api/intake/{supplement_id}")
async def get_intake_logs(
    supplement_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get intake logs for a supplement"""
    query = db.query(IntakeLog).filter(IntakeLog.supplement_id == supplement_id)

    if start_date:
        query = query.filter(IntakeLog.date >= start_date)
    if end_date:
        query = query.filter(IntakeLog.date <= end_date)

    logs = query.order_by(IntakeLog.date.desc()).all()

    return [
        {
            "id": log.id,
            "date": log.date,
            "taken": log.taken,
            "actual_dosage": log.actual_dosage,
            "energy_level": log.energy_level,
            "sleep_quality": log.sleep_quality,
            "mood_level": log.mood_level,
            "notes": log.notes
        }
        for log in logs
    ]

# Research endpoints
@app.get("/api/research/{supplement_id}")
async def get_research(supplement_id: int, db: Session = Depends(get_db)):
    """Get cached research for a supplement"""
    research = db.query(ResearchCache).filter(
        ResearchCache.supplement_id == supplement_id
    ).order_by(
        ResearchCache.evidence_level.desc(),
        ResearchCache.year.desc()
    ).all()

    return [
        {
            "pmid": r.pmid,
            "title": r.title,
            "abstract": r.abstract,
            "year": r.year,
            "publication_type": r.publication_type,
            "evidence_level": r.evidence_level,
            "authors": r.authors,
            "journal": r.journal,
            "doi": r.doi,
            "url": r.url,
            "recommended_dosage": r.recommended_dosage,
            "dosage_unit": r.dosage_unit,
            "key_findings": r.key_findings
        }
        for r in research
    ]

@app.post("/api/research/refresh/{supplement_id}")
async def refresh_research(supplement_id: int, db: Session = Depends(get_db)):
    """Refresh research for a supplement"""
    supplement = db.query(Supplement).filter(Supplement.id == supplement_id).first()
    if not supplement:
        raise HTTPException(status_code=404, detail="Supplement not found")

    try:
        pubmed_service = PubMedService(db)
        articles = pubmed_service.auto_search_for_supplement(supplement.name)
        cached_count = pubmed_service.cache_research(supplement_id, articles)

        return {
            "message": "Research refreshed",
            "articles_found": len(articles),
            "articles_cached": cached_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research refresh failed: {str(e)}")

# Analysis endpoints
@app.get("/api/analyze/dosage/{supplement_id}")
async def analyze_dosage(supplement_id: int, db: Session = Depends(get_db)):
    """Analyze supplement dosage against research"""
    analyzer = DosageAnalyzer(db)
    analysis = analyzer.analyze_supplement_dosage(supplement_id)

    if "error" in analysis:
        raise HTTPException(status_code=404, detail=analysis["error"])

    return analysis

@app.get("/api/analyze/evidence/{supplement_id}")
async def get_evidence_summary(supplement_id: int, db: Session = Depends(get_db)):
    """Get evidence summary for a supplement"""
    analyzer = DosageAnalyzer(db)
    summary = analyzer.get_evidence_summary(supplement_id)

    if "error" in summary:
        raise HTTPException(status_code=404, detail=summary["error"])

    return summary

@app.post("/api/analyze/interactions")
async def check_interactions(supplement_ids: List[int], db: Session = Depends(get_db)):
    """Check for interactions between supplements"""
    analyzer = DosageAnalyzer(db)
    interactions = analyzer.check_interactions(supplement_ids)

    return {
        "supplements_checked": len(supplement_ids),
        "interactions_found": len(interactions),
        "interactions": interactions
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
