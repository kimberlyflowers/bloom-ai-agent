"""
BLOOM AI Agent - Core Agent Class
Verified for Railway Stability & Rate-Limited Logging.
"""

import json
import logging
import os
import random
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Tuple
from anthropic import Anthropic

# CRASH FIX: Ensure directory exists BEFORE logging starts
os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Configure logging to be less "chatty" for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s', # Stripped down format to save log bandwidth
    handlers=[
        logging.FileHandler('logs/agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# SILENCE NOISY LIBRARIES (Prevents the 500 logs/sec crash)
logging.getLogger("anthropic").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

class Platform(Enum):
    REDDIT = "reddit"
    TWITTER = "twitter"
    CANVA = "canva"

class OperatingMode(Enum):
    SURVIVAL = "survival"
    GROWTH = "growth"
    SCALE = "scale"

class Specialization(Enum):
    GENERALIST = "generalist"
    REDDIT_SPECIALIST = "reddit_specialist"
    TWITTER_SPECIALIST = "twitter_specialist"
    CONTENT_CREATOR = "content_creator"
    COMMUNITY_ENGAGER = "community_engager"
    PAID_ADVERTISER = "paid_advertiser"
    ENTERPRISE_HUNTER = "enterprise_hunter"

@dataclass
class CommissionEvent:
    timestamp: str
    amount: float
    user_id: str
    plan_type: str
    source_strategy: str
    source_platform: str
    conversion_path: str

@dataclass
class Strategy:
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
        return Strategy(
            name=data.get('name', 'unknown'),
            platform=Platform(data.get('platform', 'reddit')),
            cost_per_action=data.get('cost_per_action', 0.10),
            roi_history=data.get('roi_history', []),
            total_spent=data.get('total_spent', 0.0),
            total_earned=data.get('total_earned', 0.0),
            success_count=data.get('success_count', 0),
            failure_count=data.get('failure_count', 0),
            enabled=data.get('enabled', True)
        )

class BloomAIAgent:
    """AI Agent for BLOOM growth marketing with integrated orchestration."""

    DAILY_SPENDING_LIMITS = {
        OperatingMode.SURVIVAL: 10.0,
        OperatingMode.GROWTH: 50.0,
        OperatingMode.SCALE: 200.0
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
        
        # Dashboard Bridge - Dynamic Import to prevent circular crashes
        try:
            from src.orchestration_dashboard import OrchestrationDashboard
            self.command_center = OrchestrationDashboard()
        except:
            self.command_center = None

        api_key = os.getenv('ANTHROPIC_API_KEY')
        self.anthropic_client = Anthropic(api_key=api_key) if api_key else None
        
        logger.info(f"Agent {agent_id} Ready. Mode: {self.get_operating_mode().value}")

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
        """Sarah's Learning Engine. Updates local stats and global dashboard."""
        if strategy_name not in self.strategies: return
        strat = self.strategies[strategy_name]
        
        if success:
            strat.success_count += 1
            strat.total_earned += reward
            logger.info(f"SUCCESS: {strategy_name} | Balance: ${self.commission_balance:.2f}")
            if self.command_center:
                self.command_center.update_trust_metrics(self.agent_id, trust_score=1)
        else:
            strat.failure_count += 1
            logger.error(f"FAILURE: {strategy_name} | Logged to Intel dashboard")
            if self.command_center:
                self.command_center.log_product_intelligence(self.agent_id, "technical_blocked", f"Failed: {strategy_name}")

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
        with open(filepath, 'w') as f:
            json.dump(state, f) # Removed indent=2 to save log rate limits

    @staticmethod
    def load_state(filepath: str) -> 'BloomAIAgent':
        if not os.path.exists(filepath): return BloomAIAgent()
        with open(filepath, 'r') as f:
            s = json.load(f)
        
        agent = BloomAIAgent(s.get('agent_id', 'sarah_001'), s.get('commission_balance', 50.0))
        agent.total_earned = s.get('total_earned', 0.0)
        agent.total_spent = s.get('total_spent', 0.0)
        history = s.get('commission_history', [])
        agent.commission_history = [CommissionEvent(**e) for e in history]
        return agent
