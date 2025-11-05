"""
Analyzer for dosage recommendations and interactions
"""
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from .database import Supplement, ResearchCache, Interaction
import logging

logger = logging.getLogger(__name__)


class DosageAnalyzer:
    """Analyzer for supplement dosages and recommendations"""

    def __init__(self, db: Session):
        self.db = db

    def analyze_supplement_dosage(self, supplement_id: int) -> Dict[str, Any]:
        """
        Analyze supplement dosage against research recommendations

        Returns:
            Analysis with recommendations and warnings
        """
        supplement = self.db.query(Supplement).filter(Supplement.id == supplement_id).first()
        if not supplement:
            return {"error": "Supplement not found"}

        # Get cached research
        research = self.db.query(ResearchCache).filter(
            ResearchCache.supplement_id == supplement_id,
            ResearchCache.recommended_dosage.isnot(None)
        ).order_by(ResearchCache.evidence_level.desc(), ResearchCache.year.desc()).all()

        if not research:
            return {
                "supplement": supplement.name,
                "current_dosage": supplement.dosage,
                "current_unit": supplement.dosage_unit,
                "status": "no_data",
                "message": "No dosage recommendations found in research"
            }

        # Analyze dosages from research
        dosages = []
        for r in research:
            if r.recommended_dosage and r.dosage_unit:
                # Normalize to same unit if possible
                normalized_dosage = self._normalize_dosage(
                    r.recommended_dosage,
                    r.dosage_unit,
                    supplement.dosage_unit
                )
                if normalized_dosage:
                    dosages.append({
                        'value': normalized_dosage,
                        'unit': supplement.dosage_unit,
                        'pmid': r.pmid,
                        'year': r.year,
                        'evidence_level': r.evidence_level
                    })

        if not dosages:
            return {
                "supplement": supplement.name,
                "current_dosage": supplement.dosage,
                "current_unit": supplement.dosage_unit,
                "status": "unit_mismatch",
                "message": "Research dosages use different units"
            }

        # Calculate statistics
        dosage_values = [d['value'] for d in dosages]
        min_recommended = min(dosage_values)
        max_recommended = max(dosage_values)
        avg_recommended = sum(dosage_values) / len(dosage_values)

        # Determine status
        current = supplement.dosage
        status = "optimal"
        message = f"Your dosage is within recommended range"

        if current < min_recommended:
            status = "below"
            message = f"Your dosage ({current} {supplement.dosage_unit}) is below the recommended range"
        elif current > max_recommended:
            status = "above"
            message = f"Your dosage ({current} {supplement.dosage_unit}) exceeds the recommended range"

        return {
            "supplement": supplement.name,
            "current_dosage": current,
            "current_unit": supplement.dosage_unit,
            "recommended_range": {
                "min": min_recommended,
                "max": max_recommended,
                "avg": round(avg_recommended, 2),
                "unit": supplement.dosage_unit
            },
            "status": status,
            "message": message,
            "research_count": len(dosages),
            "top_sources": [
                {
                    "pmid": d['pmid'],
                    "dosage": d['value'],
                    "year": d['year'],
                    "evidence_level": d['evidence_level']
                }
                for d in sorted(dosages, key=lambda x: (
                    {'high': 0, 'medium': 1, 'low': 2}.get(x['evidence_level'], 3),
                    -x['year']
                ))[:3]
            ]
        }

    def _normalize_dosage(
        self,
        value: float,
        from_unit: str,
        to_unit: str
    ) -> Optional[float]:
        """
        Normalize dosage between units

        Returns:
            Normalized value or None if conversion not possible
        """
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()

        if from_unit == to_unit:
            return value

        # Conversion factors
        conversions = {
            ('mcg', 'mg'): 0.001,
            ('mg', 'mcg'): 1000,
            ('g', 'mg'): 1000,
            ('mg', 'g'): 0.001,
            ('g', 'mcg'): 1000000,
            ('mcg', 'g'): 0.000001,
        }

        key = (from_unit, to_unit)
        if key in conversions:
            return value * conversions[key]

        return None

    def check_interactions(self, supplement_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Check for interactions between supplements

        Args:
            supplement_ids: List of supplement IDs to check

        Returns:
            List of potential interactions
        """
        interactions = []

        # Query existing interactions in database
        for i in range(len(supplement_ids)):
            for j in range(i + 1, len(supplement_ids)):
                id_a, id_b = supplement_ids[i], supplement_ids[j]

                # Check both directions
                interaction = self.db.query(Interaction).filter(
                    ((Interaction.supplement_a_id == id_a) & (Interaction.supplement_b_id == id_b)) |
                    ((Interaction.supplement_a_id == id_b) & (Interaction.supplement_b_id == id_a))
                ).first()

                if interaction:
                    supp_a = self.db.query(Supplement).filter(Supplement.id == interaction.supplement_a_id).first()
                    supp_b = self.db.query(Supplement).filter(Supplement.id == interaction.supplement_b_id).first()

                    interactions.append({
                        "supplement_a": supp_a.name,
                        "supplement_b": supp_b.name,
                        "interaction_type": interaction.interaction_type,
                        "severity": interaction.severity,
                        "description": interaction.description,
                        "source_pmid": interaction.source_pmid,
                        "source_url": interaction.source_url
                    })

        return interactions

    def get_evidence_summary(self, supplement_id: int) -> Dict[str, Any]:
        """
        Get summary of evidence for a supplement

        Returns:
            Evidence summary with statistics
        """
        supplement = self.db.query(Supplement).filter(Supplement.id == supplement_id).first()
        if not supplement:
            return {"error": "Supplement not found"}

        research = self.db.query(ResearchCache).filter(
            ResearchCache.supplement_id == supplement_id
        ).all()

        if not research:
            return {
                "supplement": supplement.name,
                "total_studies": 0,
                "evidence_levels": {},
                "year_distribution": {},
                "message": "No research data available"
            }

        # Calculate statistics
        total_studies = len(research)

        # Evidence levels
        evidence_counts = {}
        for r in research:
            level = r.evidence_level or 'unknown'
            evidence_counts[level] = evidence_counts.get(level, 0) + 1

        # Year distribution
        year_counts = {}
        for r in research:
            if r.year:
                year_counts[r.year] = year_counts.get(r.year, 0) + 1

        # Publication types
        pub_types = {}
        for r in research:
            if r.publication_type:
                for pt in r.publication_type.split(','):
                    pt = pt.strip()
                    pub_types[pt] = pub_types.get(pt, 0) + 1

        # Get key findings from top studies
        top_studies = sorted(
            research,
            key=lambda x: (
                {'high': 0, 'medium': 1, 'low': 2}.get(x.evidence_level, 3),
                -(x.year or 0)
            )
        )[:5]

        key_findings = []
        for study in top_studies:
            if study.key_findings:
                key_findings.append({
                    "pmid": study.pmid,
                    "year": study.year,
                    "evidence_level": study.evidence_level,
                    "finding": study.key_findings
                })

        return {
            "supplement": supplement.name,
            "total_studies": total_studies,
            "evidence_levels": evidence_counts,
            "year_distribution": dict(sorted(year_counts.items(), reverse=True)),
            "publication_types": pub_types,
            "key_findings": key_findings
        }
