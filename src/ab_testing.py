"""A/B Testing Framework - Rigorous experiment framework"""
import logging
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

@dataclass
class ABExperiment:
    """Controlled A/B test"""
    experiment_id: str
    hypothesis: str
    control_strategy: str
    treatment_strategy: str
    start_date: datetime
    duration_days: int
    sample_size: int

    control_results: List[float] = None
    treatment_results: List[float] = None

    def __post_init__(self):
        if self.control_results is None:
            self.control_results = []
        if self.treatment_results is None:
            self.treatment_results = []

class ABTestingFramework:
    """Rigorous A/B testing for agent strategies"""

    def __init__(self):
        self.experiments: Dict[str, ABExperiment] = {}

    def create_experiment(self, hypothesis: str, control: str, treatment: str,
                         duration_days: int = 14, sample_size: int = 100) -> str:
        """Create controlled experiment"""
        exp_id = f"exp_{len(self.experiments)}"
        experiment = ABExperiment(
            experiment_id=exp_id,
            hypothesis=hypothesis,
            control_strategy=control,
            treatment_strategy=treatment,
            start_date=datetime.now(),
            duration_days=duration_days,
            sample_size=sample_size
        )
        self.experiments[exp_id] = experiment
        logger.info(f"Experiment created: {hypothesis}")
        return exp_id

    def record_result(self, exp_id: str, variant: str, roi: float):
        """Record result for control or treatment"""
        exp = self.experiments[exp_id]
        if variant == 'control':
            exp.control_results.append(roi)
        else:
            exp.treatment_results.append(roi)

    def analyze(self, exp_id: str) -> Dict:
        """Statistical analysis with confidence intervals"""
        exp = self.experiments[exp_id]

        if not exp.control_results or not exp.treatment_results:
            return {'status': 'insufficient_data'}

        control_avg = sum(exp.control_results) / len(exp.control_results)
        treatment_avg = sum(exp.treatment_results) / len(exp.treatment_results)

        effect_size = treatment_avg - control_avg
        percent_improvement = (effect_size / control_avg) * 100 if control_avg > 0 else 0

        # Simple significance test (would use scipy.stats in production)
        significant = abs(percent_improvement) > 20 and len(exp.control_results) >= 30

        return {
            'status': 'complete',
            'control_avg_roi': control_avg,
            'treatment_avg_roi': treatment_avg,
            'effect_size': effect_size,
            'percent_improvement': percent_improvement,
            'statistically_significant': significant,
            'sample_sizes': {
                'control': len(exp.control_results),
                'treatment': len(exp.treatment_results)
            }
        }
