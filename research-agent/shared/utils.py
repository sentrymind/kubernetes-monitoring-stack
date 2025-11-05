"""
Utility functions
"""
import os
import logging
from typing import List, Dict, Any
from datetime import datetime
import hashlib
import json


def setup_logging(name: str, level: str = "INFO") -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Console handler
    handler = logging.StreamHandler()
    handler.setLevel(getattr(logging, level.upper()))

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


def create_directories():
    """Create necessary directories"""
    dirs = ['data', 'visualizations', 'logs']
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def generate_task_id(query: str) -> str:
    """Generate unique task ID from query"""
    timestamp = datetime.now().isoformat()
    combined = f"{query}_{timestamp}"
    return hashlib.md5(combined.encode()).hexdigest()


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """Extract keywords from text (simple implementation)"""
    # Remove common words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'should', 'could', 'may', 'might', 'can', 'this', 'that', 'these',
        'those', 'it', 'its', 'they', 'their', 'them', 'we', 'our', 'you',
        'your', 'he', 'she', 'him', 'her'
    }

    # Tokenize and filter
    words = text.lower().split()
    words = [w.strip('.,!?;:()[]{}') for w in words]
    words = [w for w in words if w and w not in stop_words and len(w) > 3]

    # Count frequency
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1

    # Get top N
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:top_n]]


def save_json(data: Any, filepath: str):
    """Save data to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def load_json(filepath: str) -> Any:
    """Load data from JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def format_authors(authors: List[str], max_authors: int = 3) -> str:
    """Format author list for display"""
    if not authors:
        return "Unknown"

    if len(authors) <= max_authors:
        return ", ".join(authors)

    return f"{', '.join(authors[:max_authors])} et al."


def extract_year(date: datetime) -> int:
    """Extract year from datetime"""
    if isinstance(date, datetime):
        return date.year
    return None
