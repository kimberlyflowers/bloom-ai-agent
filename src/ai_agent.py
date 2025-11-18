"""
BLOOM AI Agent - Core Agent Class
Manages commission tracking, learning system, and strategy selection.
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Tuple
import os
from anthropic import Anthropic


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
    roi_history: List[float]
    total_spent: float
    total_earned: float
    success_count: int
    failure_count: int
    enabled: bool

    def average_roi(self) -> float:
        """Calculate average ROI across all history"""
        if not self.roi_history:
            return 0.0
        return sum(self.roi_history) / len(self.roi_history)

    def recent_roi(self, n: int = 10) -> float:
        """Calculate average ROI for last N actions"""
        if not self.roi_history:
            return 0.0
        recent = self.roi_history[-n:]
        return sum(recent) / len(recent)

    def expected_return(self) -> float:
        """Expected return on investment for next action"""
        if not self.roi_history:
            return 0.0
        # Use recent ROI for better adaptation
        recent = self.recent_roi(10)
        return self.cost_per_action * recent

    def is_profitable(self) -> bool:
        """Check if strategy is profitable overall"""
        return self.total_earned > self.total_spent

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
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
        """Create Strategy from dictionary"""
        return Strategy(
            name=data['name'],
            platform=Platform(data['platform']),
            cost_per_action=data['cost_per_action'],
            roi_history=data['roi_history'],
            total_spent=data['total_spent'],
            total_earned=data['total_earned'],
            success_count=data['success_count'],
            failure_count=data['failure_count'],
            enabled=data['enabled']
        )


class BloomAIAgent:
    """
    AI Agent for BLOOM growth marketing with commission-based learning.
    """

    # Daily spending limits by operating mode
    DAILY_SPENDING_LIMITS = {
        OperatingMode.SURVIVAL: 10.0,
        OperatingMode.GROWTH: 50.0,
        OperatingMode.SCALE: 200.0
    }

    # Commission rates by plan type
    COMMISSION_RATES = {
        'free': 0.50,
        'verify': 1.90,
        'creator': 4.90,
        'studio': 9.90,
        'agency': 99.90
    }

    def __init__(self, agent_id: str = "adam", initial_balance: float = 50.0,
                 specialization: Specialization = Specialization.GENERALIST):
        """Initialize the AI agent"""
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

        # Initialize Anthropic client
        api_key = os.getenv('ANTHROPIC_API_KEY')
        self.anthropic_client = Anthropic(api_key=api_key) if api_key else None

        logger.info(f"Agent '{agent_id}' initialized with ${initial_balance:.2f} balance, "
                   f"specialization: {specialization.value}")

    def _initialize_strategies(self) -> Dict[str, Strategy]:
        """Initialize default marketing strategies"""
        strategies = {
            'reddit_value_comment': Strategy(
                name='reddit_value_comment',
                platform=Platform.REDDIT,
                cost_per_action=0.10,
                roi_history=[],
                total_spent=0.0,
                total_earned=0.0,
                success_count=0,
                failure_count=0,
                enabled=True
            ),
            'reddit_educational_post': Strategy(
                name='reddit_educational_post',
                platform=Platform.REDDIT,
                cost_per_action=0.50,
                roi_history=[],
                total_spent=0.0,
                total_earned=0.0,
                success_count=0,
                failure_count=0,
                enabled=True
            ),
            'twitter_thread': Strategy(
                name='twitter_thread',
                platform=Platform.TWITTER,
                cost_per_action=0.30,
                roi_history=[],
                total_spent=0.0,
                total_earned=0.0,
                success_count=0,
                failure_count=0,
                enabled=True
            ),
            'twitter_reply': Strategy(
                name='twitter_reply',
                platform=Platform.TWITTER,
                cost_per_action=0.10,
                roi_history=[],
                total_spent=0.0,
                total_earned=0.0,
                success_count=0,
                failure_count=0,
                enabled=True
            ),
            'reddit_boost': Strategy(
                name='reddit_boost',
                platform=Platform.REDDIT,
                cost_per_action=15.00,
                roi_history=[],
                total_spent=0.0,
                total_earned=0.0,
                success_count=0,
                failure_count=0,
                enabled=True
            ),
            'twitter_promoted': Strategy(
                name='twitter_promoted',
                platform=Platform.TWITTER,
                cost_per_action=25.00,
                roi_history=[],
                total_spent=0.0,
                total_earned=0.0,
                success_count=0,
                failure_count=0,
                enabled=True
            )
        }
        return strategies

    def get_operating_mode(self) -> OperatingMode:
        """Determine operating mode based on current balance"""
        if self.commission_balance < 50:
            return OperatingMode.SURVIVAL
        elif self.commission_balance < 500:
            return OperatingMode.GROWTH
        else:
            return OperatingMode.SCALE

    def _reset_daily_spending_if_needed(self):
        """Reset daily spending counter if new day"""
        today = datetime.now().date()
        if today != self.last_reset_date:
            self.today_spent = 0.0
            self.last_reset_date = today
            logger.info(f"Daily spending reset for {self.agent_id}")

    def record_commission(self, amount: float, user_id: str, plan_type: str,
                         source_strategy: str, source_platform: str,
                         conversion_path: str):
        """Record a commission earned from conversion"""
        event = CommissionEvent(
            timestamp=datetime.now().isoformat(),
            amount=amount,
            user_id=user_id,
            plan_type=plan_type,
            source_strategy=source_strategy,
            source_platform=source_platform,
            conversion_path=conversion_path
        )

        self.commission_balance += amount
        self.total_earned += amount
        self.commission_history.append(event)

        # Update strategy ROI
        if source_strategy in self.strategies:
            strategy = self.strategies[source_strategy]
            strategy.total_earned += amount
            strategy.success_count += 1

            # Calculate ROI for this action
            if strategy.total_spent > 0:
                roi = strategy.total_earned / strategy.total_spent
                strategy.roi_history.append(roi)

        logger.info(f"💰 Commission recorded: ${amount:.2f} from {plan_type} "
                   f"via {source_strategy} | New balance: ${self.commission_balance:.2f}")

        return event

    def _score_strategy(self, strategy: Strategy) -> float:
        """
        Calculate score for strategy selection.
        Higher score = more likely to be chosen.
        """
        mode = self.get_operating_mode()

        # Base score from expected return
        expected = strategy.expected_return()

        # Mode-specific multipliers
        if mode == OperatingMode.SURVIVAL:
            # In survival, heavily penalize unproven strategies
            if len(strategy.roi_history) < 3:
                return expected * 0.1
            # Only use strategies with positive ROI
            if strategy.average_roi() < 1.5:
                return 0.0
            return expected * 1.0

        elif mode == OperatingMode.GROWTH:
            # Balance proven and experimental
            if len(strategy.roi_history) < 3:
                # Give new strategies a chance
                return expected * 0.5
            # Boost profitable strategies
            if strategy.is_profitable():
                return expected * 1.5
            return expected * 1.0

        else:  # SCALE mode
            # Aggressively pursue winners
            if strategy.recent_roi(10) > 3.0:
                return expected * 2.0
            if len(strategy.roi_history) < 5:
                # Still test new strategies
                return expected * 0.7
            return expected * 1.0

    def choose_next_strategy(self) -> Optional[Tuple[str, Strategy]]:
        """
        Choose the next strategy to execute based on ROI and mode.
        Returns (strategy_name, strategy) or None if no affordable strategy.
        """
        self._reset_daily_spending_if_needed()
        mode = self.get_operating_mode()
        daily_limit = self.DAILY_SPENDING_LIMITS[mode]

        # Filter to enabled and affordable strategies
        affordable = {
            name: strat for name, strat in self.strategies.items()
            if strat.enabled
            and strat.cost_per_action <= self.commission_balance
            and (self.today_spent + strat.cost_per_action) <= daily_limit
        }

        if not affordable:
            logger.warning(f"No affordable strategies available. "
                         f"Balance: ${self.commission_balance:.2f}, "
                         f"Daily spent: ${self.today_spent:.2f}/{daily_limit:.2f}")
            return None

        # Score all affordable strategies
        scores = {name: self._score_strategy(strat)
                 for name, strat in affordable.items()}

        # Choose strategy with highest score
        best_strategy = max(scores.items(), key=lambda x: x[1])
        strategy_name = best_strategy[0]

        logger.info(f"Selected strategy: {strategy_name} (score: {best_strategy[1]:.2f}) "
                   f"in {mode.value} mode")

        return strategy_name, self.strategies[strategy_name]

    def spend(self, amount: float, strategy_name: str) -> bool:
        """
        Spend money on a strategy if affordable.
        Returns True if successful, False if insufficient funds.
        """
        if amount > self.commission_balance:
            logger.warning(f"Insufficient balance for {strategy_name}: "
                         f"${amount:.2f} needed, ${self.commission_balance:.2f} available")
            return False

        self.commission_balance -= amount
        self.total_spent += amount
        self.today_spent += amount

        if strategy_name in self.strategies:
            self.strategies[strategy_name].total_spent += amount

        logger.info(f"💸 Spent ${amount:.2f} on {strategy_name} | "
                   f"Remaining: ${self.commission_balance:.2f}")

        return True

    def generate_content(self, strategy_name: str, context: dict) -> str:
        """
        Generate content using Claude API based on strategy and context.
        """
        if not self.anthropic_client:
            logger.warning("Anthropic client not initialized, using fallback content")
            return self._fallback_content(strategy_name, context)

        mode = self.get_operating_mode()

        # Build prompt based on strategy
        prompt = self._build_content_prompt(strategy_name, context, mode)

        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = message.content[0].text
            logger.info(f"Generated content for {strategy_name} using Claude API")
            return content

        except Exception as e:
            logger.error(f"Error generating content with Claude: {e}")
            return self._fallback_content(strategy_name, context)

    def _build_content_prompt(self, strategy_name: str, context: dict,
                             mode: OperatingMode) -> str:
        """Build prompt for Claude content generation"""

        base_context = """
        You are a marketing AI for BLOOM, a platform that helps creators protect their
        digital content from unauthorized AI training and theft. BLOOM provides:

        - Content fingerprinting and tracking
        - Automated DMCA takedown assistance
        - Proof of ownership via blockchain
        - AI training opt-out enforcement

        Plans: Free, VERIFY ($19), Creator ($49/mo), Studio ($99/mo), Agency ($999/mo)
        """

        if 'reddit' in strategy_name:
            if 'comment' in strategy_name:
                return f"""{base_context}

                Create a helpful, value-adding Reddit comment for this post:

                Subreddit: {context.get('subreddit', 'unknown')}
                Post Title: {context.get('post_title', 'unknown')}
                Post Content: {context.get('post_content', 'unknown')}

                Guidelines:
                - Be genuinely helpful, not salesy
                - Address the user's specific concern
                - Mention BLOOM naturally only if highly relevant
                - Keep it conversational and authentic
                - Operating mode: {mode.value} (adjust tone accordingly)
                """
            else:  # educational post
                return f"""{base_context}

                Create an educational Reddit post for r/{context.get('subreddit', 'ArtistLounge')}
                Topic: {context.get('topic', 'protecting digital content')}

                Guidelines:
                - Provide real value and education
                - Share actionable tips
                - Mention BLOOM as one solution among others
                - Include discussion questions
                - Operating mode: {mode.value}
                """

        elif 'twitter' in strategy_name:
            if 'reply' in strategy_name:
                return f"""{base_context}

                Create a helpful Twitter reply to this tweet:

                Tweet: {context.get('tweet_text', 'unknown')}

                Guidelines:
                - Be empathetic and helpful
                - Keep under 280 characters
                - Mention BLOOM if relevant
                - Operating mode: {mode.value}
                """
            else:  # thread
                return f"""{base_context}

                Create an educational Twitter thread (3-5 tweets) about:
                {context.get('topic', 'protecting your creative work from AI scraping')}

                Guidelines:
                - Start with a hook
                - Provide valuable information
                - Include actionable tips
                - Mention BLOOM in final tweet
                - Operating mode: {mode.value}
                """

        return "Create helpful marketing content for BLOOM."

    def _fallback_content(self, strategy_name: str, context: dict) -> str:
        """Fallback content when Claude API is unavailable"""
        fallbacks = {
            'reddit_value_comment': "Have you looked into content fingerprinting? It can help track unauthorized use of your work.",
            'reddit_educational_post': "Tips for protecting your digital content...",
            'twitter_reply': "Sorry to hear about that. Content protection tools can help prevent this.",
            'twitter_thread': "🧵 Thread: How to protect your creative work online..."
        }
        return fallbacks.get(strategy_name, "Check out BLOOM for content protection.")

    def record_action_result(self, strategy_name: str, cost: float,
                           conversions: int = 0, revenue: float = 0.0):
        """
        Record the result of a marketing action.
        Updates strategy ROI and learning.
        """
        if strategy_name not in self.strategies:
            logger.warning(f"Unknown strategy: {strategy_name}")
            return

        strategy = self.strategies[strategy_name]

        if conversions == 0:
            strategy.failure_count += 1
            # Record 0 ROI for failed actions
            if strategy.total_spent > 0:
                roi = strategy.total_earned / strategy.total_spent
                strategy.roi_history.append(roi)

        logger.info(f"Action result for {strategy_name}: "
                   f"{conversions} conversions, ${revenue:.2f} revenue")

    def get_performance_report(self) -> dict:
        """Generate comprehensive performance report"""
        mode = self.get_operating_mode()

        # Calculate metrics
        overall_roi = self.total_earned / self.total_spent if self.total_spent > 0 else 0

        # Strategy performance
        strategy_stats = []
        for name, strat in self.strategies.items():
            if strat.total_spent > 0 or strat.total_earned > 0:
                strategy_stats.append({
                    'name': name,
                    'total_spent': strat.total_spent,
                    'total_earned': strat.total_earned,
                    'roi': strat.average_roi(),
                    'recent_roi': strat.recent_roi(5),
                    'success_count': strat.success_count,
                    'failure_count': strat.failure_count,
                    'enabled': strat.enabled
                })

        # Sort by ROI
        strategy_stats.sort(key=lambda x: x['roi'], reverse=True)

        return {
            'agent_id': self.agent_id,
            'specialization': self.specialization.value,
            'timestamp': datetime.now().isoformat(),
            'balance': self.commission_balance,
            'total_earned': self.total_earned,
            'total_spent': self.total_spent,
            'overall_roi': overall_roi,
            'operating_mode': mode.value,
            'days_active': (datetime.now() - self.creation_date).days,
            'total_conversions': len(self.commission_history),
            'strategy_performance': strategy_stats,
            'today_spent': self.today_spent,
            'daily_limit': self.DAILY_SPENDING_LIMITS[mode]
        }

    def save_state(self, filepath: str):
        """Save agent state to JSON file"""
        state = {
            'agent_id': self.agent_id,
            'specialization': self.specialization.value,
            'commission_balance': self.commission_balance,
            'total_earned': self.total_earned,
            'total_spent': self.total_spent,
            'today_spent': self.today_spent,
            'last_reset_date': self.last_reset_date.isoformat(),
            'creation_date': self.creation_date.isoformat(),
            'commission_history': [asdict(event) for event in self.commission_history],
            'strategies': {name: strat.to_dict() for name, strat in self.strategies.items()}
        }

        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)

        logger.info(f"Agent state saved to {filepath}")

    @staticmethod
    def load_state(filepath: str) -> 'BloomAIAgent':
        """Load agent state from JSON file"""
        with open(filepath, 'r') as f:
            state = json.load(f)

        agent = BloomAIAgent(
            agent_id=state['agent_id'],
            initial_balance=state['commission_balance'],
            specialization=Specialization(state['specialization'])
        )

        agent.total_earned = state['total_earned']
        agent.total_spent = state['total_spent']
        agent.today_spent = state['today_spent']
        agent.last_reset_date = datetime.fromisoformat(state['last_reset_date']).date()
        agent.creation_date = datetime.fromisoformat(state['creation_date'])

        # Load commission history
        agent.commission_history = [
            CommissionEvent(**event) for event in state['commission_history']
        ]

        # Load strategies
        agent.strategies = {
            name: Strategy.from_dict(strat_data)
            for name, strat_data in state['strategies'].items()
        }

        logger.info(f"Agent state loaded from {filepath}")
        return agent
