"""
BLOOM AI Agent - Core Agent Class
Verified for Railway Stability and Feedback Loops.
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

# Ensure directory exists BEFORE logging starts to prevent FileNotFoundError
os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Configure logging to be minimal for Railway's rate limits
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Silent third-party noise to prevent log overflow
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
    def __init__(self, agent_id: str = "sarah_001", initial_balance: float = 50.0):
        self.agent_id = agent_id
        self.commission_balance = initial_balance
        self.total_earned = 0.0
        self.total_spent = 0.0
        self.commission_history = []
        self.strategies = self._initialize_strategies()
        self.command_center = None
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        self.anthropic_client = Anthropic(api_key=api_key) if api_key else None
        
        logger.info(f"INIT: {agent_id} initialized.")

    def _initialize_strategies(self) -> Dict[str, Strategy]:
        return {
            'reddit_comment': Strategy('reddit_comment', Platform.REDDIT, 0.10),
            'twitter_reply': Strategy('twitter_reply', Platform.TWITTER, 0.10),
            'canva_gen': Strategy('canva_gen', Platform.CANVA, 0.50)
        }

    def choose_next_strategy(self):
        # High-level strategy selection logic
        available = [s for s in self.strategies.keys() if self.strategies[s].enabled]
        if not available: return None
        name = random.choice(available)
        return name, self.strategies[name]

    def record_action_result(self, strategy_name: str, success: bool, reward: float = 0.0):
        # Lazy import handles circular dependencies at the package level
        if self.command_center is None:
            try:
                from .orchestration_dashboard import OrchestrationDashboard
                self.command_center = OrchestrationDashboard()
            except:
                pass

        if strategy_name in self.strategies:
            strat = self.strategies[strategy_name]
            if success:
                strat.success_count += 1
                strat.total_earned += reward
                if self.command_center: self.command_center.update_trust_metrics(self.agent_id, 1)
            else:
                strat.failure_count += 1
                if self.command_center: self.command_center.log_product_intelligence(self.agent_id, "tech_fail", strategy_name)

    def spend(self, amount: float, strategy_name: str) -> bool:
        if amount > self.commission_balance: return False
        self.commission_balance -= amount
        self.total_spent += amount
        return True

    def save_state(self, filepath: str):
        state = {
            'agent_id': self.agent_id,
            'balance': self.commission_balance,
            'total_earned': self.total_earned,
            'total_spent': self.total_spent,
            'strategies': {n: s.to_dict() for n, s in self.strategies.items()}
        }
        with open(filepath, 'w') as f:
            json.dump(state, f)

    @staticmethod
    def load_state(filepath: str) -> 'BloomAIAgent':
        if not os.path.exists(filepath): return BloomAIAgent()
        with open(filepath, 'r') as f:
            s = json.load(f)
        agent = BloomAIAgent(s.get('agent_id', 'sarah_001'), s.get('balance', 50.0))
        agent.total_earned = s.get('total_earned', 0.0)
        agent.total_spent = s.get('total_spent', 0.0)
        return agent
