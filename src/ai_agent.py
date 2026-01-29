"""
BLOOM AI Agent - Core Agent Class
Verified for Railway Stability.
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

# CRASH FIX: Create directories before logging initializes
# This prevents FileNotFoundError on Railway's strict file system
os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Configure logging to be Railway-friendly
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# SILENCE NOISY LIBRARIES to prevent 500 logs/sec rate limit crashes
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
        # Self-healing loader handles missing keys in old save files
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

    def __init__(self, agent_id: str = "sarah_001", initial_balance: float = 50.0):
        self.agent_id = agent_id
        self.commission_balance = initial_balance
        self.total_earned = 0.0
        self.total_spent = 0.0
        self.commission_history: List[CommissionEvent] = []
        self.today_spent = 0.0
        self.last_reset_date = datetime.now().date()
        self.creation_date = datetime.now()
        self.strategies: Dict[str, Strategy] = self._initialize_strategies()
        
        # LAZY IMPORT: Prevents circular dependency crashes
        self.command_center = None
        try:
            from src.orchestration_dashboard import OrchestrationDashboard
            self.command_center = OrchestrationDashboard()
        except:
            pass

        api_key = os.getenv('ANTHROPIC_API_KEY')
        self.anthropic_client = Anthropic(api_key=api_key) if api_key else None
        
        logger.info(f"INIT: {agent_id} | Balance: ${initial_balance:.2f}")

    def _initialize_strategies(self) -> Dict[str, Strategy]:
        return {
            'reddit_comment': Strategy('reddit_comment', Platform.REDDIT, 0.10),
            'twitter_reply': Strategy('twitter_reply', Platform.TWITTER, 0.10),
            'canva_gen': Strategy('canva_gen', Platform.CANVA, 0.50)
        }

    def record_action_result(self, strategy_name: str, success: bool, reward: float = 0.0):
        """Sarah's Feedback Loop. Stops phantom reporting."""
        if strategy_name not in self.strategies: return
        strat = self.strategies[strategy_name]
        
        if success:
            strat.success_count += 1
            strat.total_earned += reward
            logger.info(f"SUCCESS: {strategy_name}")
            if self.command_center:
                self.command_center.update_trust_metrics(self.agent_id, trust_score=1)
        else:
            strat.failure_count += 1
            logger.error(f"FAILURE: {strategy_name}")
            if self.command_center:
                self.command_center.log_product_intelligence(self.agent_id, "technical_fail", strategy_name)

    def save_state(self, filepath: str):
        state = {
            'agent_id': self.agent_id,
            'balance': self.commission_balance,
            'total_earned': self.total_earned,
            'total_spent': self.total_spent,
            'strategies': {n: s.to_dict() for n, s in self.strategies.items()}
        }
        with open(filepath, 'w') as f:
            # Minified JSON saves logging bandwidth
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
