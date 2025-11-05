"""
Data models for research agent
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class Source(str, Enum):
    """Available paper sources"""
    PUBMED = "pubmed"
    ARXIV = "arxiv"
    ALL = "all"


class Paper(BaseModel):
    """Paper data model"""
    id: str
    title: str
    authors: List[str]
    abstract: str
    publication_date: Optional[datetime] = None
    year: Optional[int] = None
    source: Source
    doi: Optional[str] = None
    url: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    citations: Optional[int] = None
    journal: Optional[str] = None

    # Computed fields
    embedding: Optional[List[float]] = None
    similarity_score: Optional[float] = None


class SearchRequest(BaseModel):
    """Search request model"""
    query: str = Field(..., min_length=3, max_length=500)
    sources: List[Source] = Field(default=[Source.ALL])
    max_results: int = Field(default=50, ge=1, le=500)
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    semantic_search: bool = Field(default=True)


class SearchResponse(BaseModel):
    """Search response model"""
    query: str
    total_results: int
    papers: List[Paper]
    search_time: float
    task_id: Optional[str] = None


class TrendAnalysis(BaseModel):
    """Trend analysis results"""
    keywords: Dict[str, int]
    timeline: Dict[int, int]
    top_authors: List[Dict[str, Any]]
    top_journals: List[Dict[str, Any]]


class VisualizationRequest(BaseModel):
    """Visualization request"""
    papers: List[Paper]
    viz_type: str = Field(..., regex="^(timeline|coauthors|wordcloud|trends)$")
    params: Dict[str, Any] = Field(default_factory=dict)


class VisualizationResponse(BaseModel):
    """Visualization response"""
    viz_type: str
    image_path: str
    data: Optional[Dict[str, Any]] = None
