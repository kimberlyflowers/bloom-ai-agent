"""
BLOOM AI Agent - Competition & Performance Rewards System

Gamification layer where reproduced agents compete for higher commission rates!

Performance-based commission multipliers:
- Elite Tier (90-100 score): 15% commission (1.5x)
- Champion Tier (75-89): 12% commission (1.2x)
- Competitor Tier (50-74): 10% commission (1.0x - default)
- Learner Tier (0-49): 8% commission (0.8x)
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum
import json

logger = logging.getLogger(__name__)


class PerformanceTier(Enum):
    """Performance tiers with commission multipliers"""
    ELITE = ("Elite", 90, 100, 1.5)        # 15% commission
    CHAMPION = ("Champion", 75, 89, 1.2)   # 12% commission
    COMPETITOR = ("Competitor", 50, 74, 1.0)  # 10% commission (default)
    LEARNER = ("Learner", 0, 49, 0.8)      # 8% commission

    def __init__(self, display_name: str, min_score: int, max_score: int, multiplier: float):
        self.display_name = display_name
        self.min_score = min_score
        self.max_score = max_score
        self.multiplier = multiplier

    @classmethod
    def from_score(cls, score: float) -> 'PerformanceTier':
        """Get tier from performance score"""
        for tier in cls:
            if tier.min_score <= score <= tier.max_score:
                return tier
        return cls.LEARNER


@dataclass
class PerformanceMetrics:
    """Agent performance metrics used for scoring"""
    agent_id: str

    # Core metrics
    total_revenue: float = 0.0
    total_spent: float = 0.0
    total_actions: int = 0
    total_conversions: int = 0

    # Time window
    window_start: datetime = field(default_factory=datetime.now)
    window_end: datetime = field(default_factory=datetime.now)

    # Derived metrics (calculated)
    roi: float = 0.0
    conversion_rate: float = 0.0
    revenue_per_action: float = 0.0

    def calculate_derived_metrics(self):
        """Calculate ROI, conversion rate, etc."""
        # ROI
        if self.total_spent > 0:
            self.roi = self.total_revenue / self.total_spent
        else:
            self.roi = 0.0

        # Conversion rate
        if self.total_actions > 0:
            self.conversion_rate = (self.total_conversions / self.total_actions) * 100
        else:
            self.conversion_rate = 0.0

        # Revenue per action
        if self.total_actions > 0:
            self.revenue_per_action = self.total_revenue / self.total_actions
        else:
            self.revenue_per_action = 0.0

    def calculate_performance_score(self) -> float:
        """
        Calculate overall performance score (0-100).

        Weights:
        - ROI: 40%
        - Conversion Rate: 30%
        - Revenue per Action: 20%
        - Total Revenue: 10%
        """
        self.calculate_derived_metrics()

        # ROI score (capped at 5x for scoring purposes)
        roi_score = min(self.roi / 5.0, 1.0) * 100 * 0.40

        # Conversion rate score (capped at 10% for scoring)
        conversion_score = min(self.conversion_rate / 10.0, 1.0) * 100 * 0.30

        # Revenue per action score (capped at $50 for scoring)
        rpa_score = min(self.revenue_per_action / 50.0, 1.0) * 100 * 0.20

        # Total revenue score (capped at $1000 for scoring)
        revenue_score = min(self.total_revenue / 1000.0, 1.0) * 100 * 0.10

        total_score = roi_score + conversion_score + rpa_score + revenue_score

        return round(total_score, 2)


@dataclass
class CompetitionResult:
    """Result of a competition period"""
    competition_id: str
    period_type: str  # 'weekly', 'monthly', 'all_time'
    start_date: datetime
    end_date: datetime

    # Rankings
    rankings: List[Tuple[str, float, PerformanceTier]] = field(default_factory=list)
    # [(agent_id, score, tier), ...]

    # Winners
    winner_id: Optional[str] = None
    winner_score: Optional[float] = None
    winner_tier: Optional[PerformanceTier] = None

    def to_dict(self) -> dict:
        """Serialize to dict"""
        return {
            'competition_id': self.competition_id,
            'period_type': self.period_type,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'rankings': [
                {
                    'agent_id': agent_id,
                    'score': score,
                    'tier': tier.display_name,
                    'commission_rate': f"{tier.multiplier * 10}%"
                }
                for agent_id, score, tier in self.rankings
            ],
            'winner': {
                'agent_id': self.winner_id,
                'score': self.winner_score,
                'tier': self.winner_tier.display_name if self.winner_tier else None,
                'commission_rate': f"{self.winner_tier.multiplier * 10}%" if self.winner_tier else None
            } if self.winner_id else None
        }


class AgentCompetition:
    """
    Manages agent competitions and performance-based rewards.

    Features:
    - Weekly and monthly tournaments
    - Performance scoring (0-100)
    - Tier-based commission multipliers
    - Leaderboards and rankings
    """

    def __init__(self, colony_id: str = "main"):
        self.colony_id = colony_id

        # Track agent performance
        self.agent_metrics: Dict[str, PerformanceMetrics] = {}

        # Competition history
        self.competitions: List[CompetitionResult] = []

        # Current competition period
        self.current_week_start = self._get_week_start()
        self.current_month_start = self._get_month_start()

        logger.info(f"Competition system initialized for colony {colony_id}")

    def _get_week_start(self) -> datetime:
        """Get start of current week (Monday)"""
        now = datetime.now()
        return now - timedelta(days=now.weekday())

    def _get_month_start(self) -> datetime:
        """Get start of current month"""
        now = datetime.now()
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    def record_agent_activity(self, agent_id: str, revenue: float,
                             spent: float, conversions: int, actions: int):
        """
        Record agent activity for competition scoring.

        Call this whenever an agent completes actions.
        """
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = PerformanceMetrics(
                agent_id=agent_id,
                window_start=datetime.now()
            )

        metrics = self.agent_metrics[agent_id]
        metrics.total_revenue += revenue
        metrics.total_spent += spent
        metrics.total_actions += actions
        metrics.total_conversions += conversions
        metrics.window_end = datetime.now()

        logger.debug(f"Recorded activity for {agent_id}: +${revenue:.2f} revenue, {conversions} conversions")

    def get_agent_performance_score(self, agent_id: str) -> float:
        """Get current performance score for agent"""
        if agent_id not in self.agent_metrics:
            return 0.0

        return self.agent_metrics[agent_id].calculate_performance_score()

    def get_agent_tier(self, agent_id: str) -> PerformanceTier:
        """Get current performance tier for agent"""
        score = self.get_agent_performance_score(agent_id)
        return PerformanceTier.from_score(score)

    def get_commission_multiplier(self, agent_id: str) -> float:
        """
        Get commission multiplier for agent based on performance.

        Returns:
            float: Multiplier (0.8 to 1.5)
        """
        tier = self.get_agent_tier(agent_id)
        return tier.multiplier

    def get_commission_rate(self, agent_id: str, base_rate: float = 0.10) -> float:
        """
        Get actual commission rate including performance multiplier.

        Args:
            agent_id: Agent ID
            base_rate: Base commission rate (default 10%)

        Returns:
            float: Actual commission rate (e.g., 0.15 for Elite tier)
        """
        multiplier = self.get_commission_multiplier(agent_id)
        return base_rate * multiplier

    def is_eligible_for_competition(self, agent_id: str,
                                   min_actions: int = 10,
                                   min_age_days: int = 7) -> bool:
        """
        Check if agent is eligible to compete.

        Requirements:
        - At least min_actions taken
        - At least min_age_days old
        """
        if agent_id not in self.agent_metrics:
            return False

        metrics = self.agent_metrics[agent_id]

        # Check action count
        if metrics.total_actions < min_actions:
            return False

        # Check age
        age = datetime.now() - metrics.window_start
        if age.days < min_age_days:
            return False

        return True

    def run_weekly_competition(self) -> CompetitionResult:
        """
        Run weekly competition and determine rankings.

        Returns:
            CompetitionResult with rankings and winner
        """
        # Check if week is over
        now = datetime.now()
        week_start = self._get_week_start()

        competition_id = f"weekly_{week_start.strftime('%Y%m%d')}"

        # Get eligible agents
        eligible = [
            agent_id for agent_id in self.agent_metrics.keys()
            if self.is_eligible_for_competition(agent_id)
        ]

        if not eligible:
            logger.info("No eligible agents for weekly competition")
            return CompetitionResult(
                competition_id=competition_id,
                period_type='weekly',
                start_date=week_start,
                end_date=now
            )

        # Calculate scores and rankings
        rankings = []
        for agent_id in eligible:
            score = self.get_agent_performance_score(agent_id)
            tier = PerformanceTier.from_score(score)
            rankings.append((agent_id, score, tier))

        # Sort by score (descending)
        rankings.sort(key=lambda x: x[1], reverse=True)

        # Create result
        result = CompetitionResult(
            competition_id=competition_id,
            period_type='weekly',
            start_date=week_start,
            end_date=now,
            rankings=rankings,
            winner_id=rankings[0][0] if rankings else None,
            winner_score=rankings[0][1] if rankings else None,
            winner_tier=rankings[0][2] if rankings else None
        )

        self.competitions.append(result)

        logger.info(f"Weekly competition complete! Winner: {result.winner_id} (score: {result.winner_score})")

        return result

    def run_monthly_competition(self) -> CompetitionResult:
        """Run monthly competition (similar to weekly)"""
        now = datetime.now()
        month_start = self._get_month_start()

        competition_id = f"monthly_{month_start.strftime('%Y%m')}"

        eligible = [
            agent_id for agent_id in self.agent_metrics.keys()
            if self.is_eligible_for_competition(agent_id, min_actions=50, min_age_days=14)
        ]

        if not eligible:
            logger.info("No eligible agents for monthly competition")
            return CompetitionResult(
                competition_id=competition_id,
                period_type='monthly',
                start_date=month_start,
                end_date=now
            )

        rankings = []
        for agent_id in eligible:
            score = self.get_agent_performance_score(agent_id)
            tier = PerformanceTier.from_score(score)
            rankings.append((agent_id, score, tier))

        rankings.sort(key=lambda x: x[1], reverse=True)

        result = CompetitionResult(
            competition_id=competition_id,
            period_type='monthly',
            start_date=month_start,
            end_date=now,
            rankings=rankings,
            winner_id=rankings[0][0] if rankings else None,
            winner_score=rankings[0][1] if rankings else None,
            winner_tier=rankings[0][2] if rankings else None
        )

        self.competitions.append(result)

        logger.info(f"Monthly competition complete! Winner: {result.winner_id} (score: {result.winner_score})")

        return result

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """
        Get current leaderboard (all-time).

        Returns:
            List of agent rankings with scores and tiers
        """
        rankings = []
        for agent_id in self.agent_metrics.keys():
            if not self.is_eligible_for_competition(agent_id):
                continue

            score = self.get_agent_performance_score(agent_id)
            tier = PerformanceTier.from_score(score)
            metrics = self.agent_metrics[agent_id]

            rankings.append({
                'rank': 0,  # Will be set below
                'agent_id': agent_id,
                'score': score,
                'tier': tier.display_name,
                'commission_rate': f"{tier.multiplier * 10}%",
                'multiplier': tier.multiplier,
                'roi': metrics.roi,
                'conversion_rate': f"{metrics.conversion_rate:.2f}%",
                'total_revenue': f"${metrics.total_revenue:.2f}",
                'total_conversions': metrics.total_conversions
            })

        # Sort by score
        rankings.sort(key=lambda x: x['score'], reverse=True)

        # Add ranks
        for i, entry in enumerate(rankings[:limit], 1):
            entry['rank'] = i

        return rankings[:limit]

    def get_competition_history(self, limit: int = 5) -> List[Dict]:
        """Get recent competition results"""
        return [comp.to_dict() for comp in self.competitions[-limit:]]

    def get_agent_stats(self, agent_id: str) -> Optional[Dict]:
        """Get detailed stats for an agent"""
        if agent_id not in self.agent_metrics:
            return None

        metrics = self.agent_metrics[agent_id]
        metrics.calculate_derived_metrics()

        score = metrics.calculate_performance_score()
        tier = PerformanceTier.from_score(score)

        return {
            'agent_id': agent_id,
            'performance_score': score,
            'tier': tier.display_name,
            'commission_multiplier': tier.multiplier,
            'commission_rate': f"{tier.multiplier * 10}%",
            'metrics': {
                'roi': f"{metrics.roi:.2f}x",
                'conversion_rate': f"{metrics.conversion_rate:.2f}%",
                'revenue_per_action': f"${metrics.revenue_per_action:.2f}",
                'total_revenue': f"${metrics.total_revenue:.2f}",
                'total_spent': f"${metrics.total_spent:.2f}",
                'total_actions': metrics.total_actions,
                'total_conversions': metrics.total_conversions
            },
            'eligible_for_competition': self.is_eligible_for_competition(agent_id),
            'window_start': metrics.window_start.isoformat(),
            'window_end': metrics.window_end.isoformat()
        }

    def save_state(self, filepath: str):
        """Save competition state to file"""
        state = {
            'colony_id': self.colony_id,
            'agent_metrics': {
                agent_id: {
                    'agent_id': m.agent_id,
                    'total_revenue': m.total_revenue,
                    'total_spent': m.total_spent,
                    'total_actions': m.total_actions,
                    'total_conversions': m.total_conversions,
                    'window_start': m.window_start.isoformat(),
                    'window_end': m.window_end.isoformat()
                }
                for agent_id, m in self.agent_metrics.items()
            },
            'competitions': [comp.to_dict() for comp in self.competitions],
            'current_week_start': self.current_week_start.isoformat(),
            'current_month_start': self.current_month_start.isoformat()
        }

        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)

        logger.info(f"Competition state saved to {filepath}")

    @classmethod
    def load_state(cls, filepath: str) -> 'AgentCompetition':
        """Load competition state from file"""
        with open(filepath, 'r') as f:
            state = json.load(f)

        competition = cls(colony_id=state['colony_id'])

        # Load agent metrics
        for agent_id, m_data in state['agent_metrics'].items():
            metrics = PerformanceMetrics(
                agent_id=m_data['agent_id'],
                total_revenue=m_data['total_revenue'],
                total_spent=m_data['total_spent'],
                total_actions=m_data['total_actions'],
                total_conversions=m_data['total_conversions'],
                window_start=datetime.fromisoformat(m_data['window_start']),
                window_end=datetime.fromisoformat(m_data['window_end'])
            )
            competition.agent_metrics[agent_id] = metrics

        # Load competition history
        for comp_data in state['competitions']:
            # Reconstruct CompetitionResult
            # (simplified - full reconstruction would be more complex)
            pass

        competition.current_week_start = datetime.fromisoformat(state['current_week_start'])
        competition.current_month_start = datetime.fromisoformat(state['current_month_start'])

        logger.info(f"Competition state loaded from {filepath}")

        return competition


def print_leaderboard(competition: AgentCompetition, title: str = "AGENT LEADERBOARD"):
    """Pretty print leaderboard"""
    print("\n" + "="*80)
    print(f"🏆 {title} 🏆".center(80))
    print("="*80)

    leaderboard = competition.get_leaderboard(limit=10)

    if not leaderboard:
        print("No agents eligible for competition yet.".center(80))
        print("="*80)
        return

    # Header
    print(f"{'Rank':<6} {'Agent ID':<20} {'Score':<8} {'Tier':<12} {'Commission':<12} {'ROI':<8} {'Conv%':<8}")
    print("-"*80)

    # Entries
    for entry in leaderboard:
        print(
            f"{entry['rank']:<6} "
            f"{entry['agent_id']:<20} "
            f"{entry['score']:<8.2f} "
            f"{entry['tier']:<12} "
            f"{entry['commission_rate']:<12} "
            f"{entry['roi']:<8.2f}x "
            f"{entry['conversion_rate']:<8}"
        )

    print("="*80)
    print(f"💰 Top performers earn up to 1.5x commission (15% vs 10% base)!")
    print("="*80 + "\n")
