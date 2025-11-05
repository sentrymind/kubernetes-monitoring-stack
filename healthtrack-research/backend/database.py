"""
Database models and session management
"""
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean,
    Date, DateTime, Text, ForeignKey, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/healthtrack.db")

# Create engine
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()


class Supplement(Base):
    """Supplement information"""
    __tablename__ = "supplements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    dosage = Column(Float, nullable=False)
    dosage_unit = Column(String(20), nullable=False)  # mg, IU, mcg, etc.
    frequency = Column(String(50), nullable=False)  # daily, twice daily, etc.
    user_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    intake_logs = relationship("IntakeLog", back_populates="supplement", cascade="all, delete-orphan")
    research_cache = relationship("ResearchCache", back_populates="supplement", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Supplement(name='{self.name}', dosage={self.dosage}{self.dosage_unit})>"


class IntakeLog(Base):
    """Daily intake tracking"""
    __tablename__ = "intake_log"

    id = Column(Integer, primary_key=True, index=True)
    supplement_id = Column(Integer, ForeignKey("supplements.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    taken = Column(Boolean, default=False, nullable=False)
    actual_dosage = Column(Float, nullable=True)  # If different from standard
    time_taken = Column(DateTime, nullable=True)
    energy_level = Column(Integer, nullable=True)  # 1-10
    sleep_quality = Column(Integer, nullable=True)  # 1-10
    mood_level = Column(Integer, nullable=True)  # 1-10
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    supplement = relationship("Supplement", back_populates="intake_logs")

    def __repr__(self):
        return f"<IntakeLog(supplement_id={self.supplement_id}, date={self.date}, taken={self.taken})>"


class ResearchCache(Base):
    """Cached PubMed research results"""
    __tablename__ = "research_cache"

    id = Column(Integer, primary_key=True, index=True)
    supplement_id = Column(Integer, ForeignKey("supplements.id"), nullable=False)
    pmid = Column(String(20), nullable=False, unique=True, index=True)
    title = Column(Text, nullable=False)
    abstract = Column(Text, nullable=True)
    year = Column(Integer, nullable=True, index=True)
    publication_type = Column(String(100), nullable=True)  # RCT, SR, Meta-analysis, etc.
    evidence_level = Column(String(20), nullable=True)  # high, medium, low
    authors = Column(Text, nullable=True)
    journal = Column(String(200), nullable=True)
    doi = Column(String(100), nullable=True)
    url = Column(String(500), nullable=True)

    # Extracted information
    recommended_dosage = Column(Float, nullable=True)
    dosage_unit = Column(String(20), nullable=True)
    key_findings = Column(Text, nullable=True)

    # Metadata
    cached_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    supplement = relationship("Supplement", back_populates="research_cache")

    def __repr__(self):
        return f"<ResearchCache(pmid='{self.pmid}', title='{self.title[:50]}...')>"


class Interaction(Base):
    """Supplement-supplement interactions"""
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    supplement_a_id = Column(Integer, ForeignKey("supplements.id"), nullable=False)
    supplement_b_id = Column(Integer, ForeignKey("supplements.id"), nullable=False)
    interaction_type = Column(String(100), nullable=False)  # synergistic, antagonistic, etc.
    severity = Column(String(20), nullable=False)  # low, moderate, high
    description = Column(Text, nullable=True)
    source_pmid = Column(String(20), nullable=True)
    source_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    supplement_a = relationship("Supplement", foreign_keys=[supplement_a_id])
    supplement_b = relationship("Supplement", foreign_keys=[supplement_b_id])

    def __repr__(self):
        return f"<Interaction(a={self.supplement_a_id}, b={self.supplement_b_id}, severity='{self.severity}')>"


# Database initialization
def init_db():
    """Initialize database tables"""
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
