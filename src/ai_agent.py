"""
BLOOM AI Agent - Core Agent Class
Manages commission tracking, learning system, and strategy selection.
"""

import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Tuple
from anthropic import Anthropic

# FIX: Automatically create logs directory to prevent FileNotFoundError crash
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Platform(Enum):
    """Social media platforms"""
    REDDIT = "reddit"
    TWITTER = "twitter"
    CANVA = "canva"


class OperatingMode(Enum):
    """Agent operating modes based on balance"""
    SURVIVAL = "survival"  # $0-$50: Conservative, proven tactics only
    GROWTH = "growth"      # $50-$500: Balanced, test new + proven
    SCALE = "scale"        # $500+: Aggressive, maximize winners


class Specialization(Enum):
    """Agent specializations for reproduction"""
    GENERALIST = "generalist"
    REDDIT_SPECIALIST = "reddit_specialist"
    TWITTER_SPECIALIST = "twitter_specialist"
    CONTENT_CREATOR = "content_creator"
    COMMUNITY_ENGAGER = "community_engager"
    PAID_ADVERTISER = "paid_advertiser"
    ENTERPRISE_HUNTER = "enterprise_hunter"


@dataclass
class CommissionEvent:
    """Record of a commission earned"""
    timestamp: str
    amount: float
    user_id: str
    plan_type: str
    source_strategy: str
    source_platform: str
    conversion_path: str


@dataclass
class Strategy:
    """Marketing strategy with ROI tracking"""
    name: str
    platform: Platform
    cost_per_action: float
    roi_history: List[float] = field(default_factory=list)
    total_spent: float = 0.0
    total_earned: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    enabled: bool = True

    def average_roi(self) -> float:
        if not self.roi_history: return 0.0
        return sum(self.roi_history) / len(self.roi_history)

    def recent_roi(self, n: int = 10) -> float:
        if not self.roi_history: return 0.0
        recent = self.roi_history[-n:]
        return sum(recent) / len(recent)

    def expected_return(self) -> float:
        if not self.roi_history: return 0.0
        return self.cost_per_action * self.recent_roi(10)

    def is_profitable(self) -> bool:
        return self.total_earned > self.total_spent

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'platform': self.platform.value,
            'cost_per_action': self.cost_per_action,
            'roi_history': self.roi_history,
            'total_spent': self.total_spent,
            'total_earned': self.total_earned,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'enabled': self.enabled
        }

    @staticmethod
    def from_dict(data: dict) -> 'Strategy':
        data['platform'] = Platform(data['platform'])
        return Strategy(**data)


class BloomAIAgent:
    """AI Agent for BLOOM growth marketing with integrated orchestration."""

    DAILY_SPENDING_LIMITS = {
        OperatingMode.SURVIVAL: 10.0,
        OperatingMode.GROWTH: 50.0,
        OperatingMode.SCALE: 200.0
    }

    COMMISSION_RATES = {
        'free': 0.50,
        'verify': 1.90,
        'creator': 4.90,
        'studio': 9.90,
        'agency': 99.90
    }

    def __init__(self, agent_id: str = "sarah_001", initial_balance: float = 50.0,
                 specialization: Specialization = Specialization.GENERALIST):
        self.agent_id = agent_id
        self.specialization = specialization
        self.commission_balance = initial_balance
        self.total_earned = 0.0
        self.total_spent = 0.0
        self.commission_history: List[CommissionEvent] = []
        self.today_spent = 0.0
        self.last_reset_date = datetime.now().date()
        self.creation_date = datetime.now()
        self.strategies: Dict[str, Strategy] = self._initialize_strategies()
        
        # Dashboard Bridge
        from src.orchestration_dashboard import OrchestrationDashboard
        self.command_center = OrchestrationDashboard()

        api_key = os.getenv('ANTHROPIC_API_KEY')
        self.anthropic_client = Anthropic(api_key=api_key) if api_key else None

    def _initialize_strategies(self) -> Dict[str, Strategy]:
        return {
            'reddit_value_comment': Strategy('reddit_value_comment', Platform.REDDIT, 0.10),
            'twitter_reply': Strategy('twitter_reply', Platform.TWITTER, 0.10),
            'canva_ugc_gen': Strategy('canva_ugc_gen', Platform.CANVA, 0.50)
        }

    def get_operating_mode(self) -> OperatingMode:
        if self.commission_balance < 50: return OperatingMode.SURVIVAL
        elif self.commission_balance < 500: return OperatingMode.GROWTH
        else: return OperatingMode.SCALE

    def spend(self, amount: float, strategy_name: str) -> bool:
        if amount > self.commission_balance: return False
        self.commission_balance -= amount
        self.total_spent += amount
        self.today_spent += amount
        if strategy_name in self.strategies:
            self.strategies[strategy_name].total_spent += amount
        return True

    def record_action_result(self, strategy_name: str, success: bool, reward: float = 0.0):
        """Sarah learns from her Canva and Social actions here."""
        if strategy_name not in self.strategies: return
        strat = self.strategies[strategy_name]
        if success:
            strat.success_count += 1
            strat.total_earned += reward
            # Update Trust Score in Command Center
            self.command_center.update_trust_metrics(self.agent_id, trust_score=min(100, self.command_center.agent_metrics[self.agent_id].trust_score + 1))
        else:
            strat.failure_count += 1
            # Log product intelligence if it was a technical failure (like Canva gate)
            self.command_center.log_product_intelligence(self.agent_id, "technical_blocked", f"Strategy {strategy_name} failed")

    def save_state(self, filepath: str):
        state = {
            'agent_id': self.agent_id,
            'specialization': self.specialization.value,
            'commission_balance': self.commission_balance,
            'total_earned': self.total_earned,
            'total_spent': self.total_spent,
            'today_spent': self.today_spent,
            'last_reset_date': self.last_reset_date.isoformat(),
            'creation_date': self.creation_date.isoformat(),
            'commission_history': [asdict(e) for e in self.commission_history],
            'strategies': {n: s.to_dict() for n, s in self.strategies.items()}
        }
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)

    @staticmethod
    def load_state(filepath: str) -> 'BloomAIAgent':
        if not os.path.exists(filepath): return BloomAIAgent()
        with open(filepath, 'r') as f:
            s = json.load(f)
        agent = BloomAIAgent(s['agent_id'], s['commission_balance'], Specialization(s['specialization']))
        agent.total_earned = s['total_earned']
        agent.total_spent = s['total_spent']
        agent.today_spent = s['today_spent']
        agent.commission_history = [CommissionEvent(**e) for e in s['commission_history']]
        return agent
