"""Cross-Colony Learning Network - Federated learning across all BLOOM users"""
import logging
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class AnonymizedLearning:
    """Privacy-preserving learning data"""
    platform: str
    strategy_type: str
    roi: float
    industry: str
    timestamp: datetime

class CrossColonyNetwork:
    """Network intelligence across all BLOOM colonies"""

    def __init__(self):
        self.global_learnings: List[AnonymizedLearning] = []

    def contribute(self, colony_id: str, learnings: List[dict]):
        """Share anonymized learnings with network"""
        for learning in learnings:
            anon = AnonymizedLearning(
                platform=learning['platform'],
                strategy_type=learning['strategy_type'],
                roi=learning['roi'],
                industry=learning.get('industry', 'general'),
                timestamp=datetime.now()
            )
            self.global_learnings.append(anon)
        logger.info(f"Colony {colony_id} contributed {len(learnings)} learnings")

    def get_insights(self, platform: str = None, industry: str = None) -> Dict:
        """Get aggregated insights from entire network"""
        filtered = self.global_learnings
        if platform:
            filtered = [l for l in filtered if l.platform == platform]
        if industry:
            filtered = [l for l in filtered if l.industry == industry]

        if not filtered:
            return {'average_roi': 0.0, 'sample_size': 0}

        avg_roi = sum(l.roi for l in filtered) / len(filtered)
        return {
            'average_roi': avg_roi,
            'sample_size': len(filtered),
            'best_roi': max(l.roi for l in filtered),
            'platforms': len(set(l.platform for l in filtered))
        }
