"""
IP DEFENDER - Game Engine
Transforms ai_agent.py commission system into Creative Energy (CE) game economy.
Maintains all AI learning intelligence for game optimization.
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
        logging.FileHandler('logs/game.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ThreatType(Enum):
    """Types of IP theft scenarios"""
    AI_SCRAPING = "ai_scraping"          # AI training data theft
    DIRECT_COPY = "direct_copy"          # Someone copied your work
    MARKETPLACE_THEFT = "marketplace"    # Selling your work
    UNAUTHORIZED_USE = "unauthorized"    # Using without permission


class PlayerTier(Enum):
    """Player progression tiers (replaces OperatingMode)"""
    NOVICE = "novice"          # 0-500 CE: Learning the ropes
    DEFENDER = "defender"      # 500-2500 CE: Active protection
    GUARDIAN = "guardian"      # 2500+ CE: Master protector


class Specialization(Enum):
    """Player specializations (replaces agent specializations)"""
    GENERALIST = "generalist"           # Balanced gameplay
    DMCA_EXPERT = "dmca_expert"         # Manual protection specialist
    AUTO_DEFENDER = "auto_defender"      # Automation specialist
    BLOCKCHAIN_GUARDIAN = "blockchain"   # Proof specialist
    COMMUNITY_PROTECTOR = "community"    # Multi-player specialist
    LEGAL_WARRIOR = "legal_warrior"      # Complex cases specialist
    ENTERPRISE_SHIELD = "enterprise"     # High-value protection


@dataclass
class CEEvent:
    """Creative Energy earning event (replaces CommissionEvent)"""
    timestamp: str
    ce_amount: int
    threat_type: str
    action_taken: str
    success: bool
    bloom_feature_used: Optional[str] = None


@dataclass
class GameAction:
    """
    Game action representing IP protection methods.
    Replaces Strategy from ai_agent.py
    """
    name: str
    action_type: str                 # "manual", "automated", "bloom_powered"
    ce_cost: int                     # Creative Energy cost
    time_seconds: int                # Real-world time this would take
    base_success_rate: float         # 0.0-1.0 probability of success
    ce_reward_on_success: int        # CE earned if successful

    # Learning tracking (same as Strategy)
    success_history: List[bool]
    total_ce_spent: int
    total_ce_earned: int
    enabled: bool

    # Pain point demonstration
    frustration_level: int           # 0-10, shows manual pain
    educational_value: str           # What this teaches player

    def average_success_rate(self) -> float:
        """Calculate actual success rate from history"""
        if not self.success_history:
            return self.base_success_rate
        return sum(self.success_history) / len(self.success_history)

    def recent_success_rate(self, n: int = 10) -> float:
        """Recent success rate for learning"""
        if not self.success_history:
            return self.base_success_rate
        recent = self.success_history[-n:]
        return sum(recent) / len(recent)

    def expected_ce_return(self) -> float:
        """Expected CE return on investment"""
        success_rate = self.recent_success_rate(10)
        return (self.ce_reward_on_success * success_rate) - self.ce_cost

    def net_ce(self) -> int:
        """Total CE profit/loss"""
        return self.total_ce_earned - self.total_ce_spent

    def to_dict(self) -> dict:
        """Serialize for saving"""
        return {
            'name': self.name,
            'action_type': self.action_type,
            'ce_cost': self.ce_cost,
            'time_seconds': self.time_seconds,
            'base_success_rate': self.base_success_rate,
            'ce_reward_on_success': self.ce_reward_on_success,
            'success_history': self.success_history,
            'total_ce_spent': self.total_ce_spent,
            'total_ce_earned': self.total_ce_earned,
            'enabled': self.enabled,
            'frustration_level': self.frustration_level,
            'educational_value': self.educational_value
        }

    @staticmethod
    def from_dict(data: dict) -> 'GameAction':
        """Deserialize from save file"""
        return GameAction(
            name=data['name'],
            action_type=data['action_type'],
            ce_cost=data['ce_cost'],
            time_seconds=data['time_seconds'],
            base_success_rate=data['base_success_rate'],
            ce_reward_on_success=data['ce_reward_on_success'],
            success_history=data['success_history'],
            total_ce_spent=data['total_ce_spent'],
            total_ce_earned=data['total_ce_earned'],
            enabled=data['enabled'],
            frustration_level=data['frustration_level'],
            educational_value=data['educational_value']
        )


class IPDefender:
    """
    Main game player class.
    Replaces BloomAIAgent with game-focused mechanics.
    """

    # CE costs for daily actions (replaces DAILY_SPENDING_LIMITS)
    DAILY_CE_LIMITS = {
        PlayerTier.NOVICE: 50,      # Limited actions per day
        PlayerTier.DEFENDER: 200,   # More active
        PlayerTier.GUARDIAN: 500    # Unlimited-ish
    }

    def __init__(self, player_id: str = "player1", initial_ce: int = 100,
                 specialization: Specialization = Specialization.GENERALIST):
        """Initialize player"""
        self.player_id = player_id
        self.specialization = specialization
        self.creative_energy = initial_ce
        self.total_ce_earned = 0
        self.total_ce_spent = 0
        self.ce_history: List[CEEvent] = []
        self.today_ce_spent = 0
        self.last_reset_date = datetime.now().date()
        self.creation_date = datetime.now()

        # Game-specific stats
        self.threats_defeated = 0
        self.threats_failed = 0
        self.bloom_features_discovered: List[str] = []
        self.current_streak = 0

        self.actions: Dict[str, GameAction] = self._initialize_game_actions()

        # Initialize Claude for scenario generation
        api_key = os.getenv('ANTHROPIC_API_KEY')
        self.anthropic_client = Anthropic(api_key=api_key) if api_key else None

        logger.info(f"Player '{player_id}' initialized with {initial_ce} CE, "
                   f"specialization: {specialization.value}")

    def _initialize_game_actions(self) -> Dict[str, GameAction]:
        """
        Initialize game actions that demonstrate IP protection methods.
        These replace marketing strategies with educational scenarios.
        """
        actions = {
            # MANUAL PROTECTION (High frustration, teaches pain points)
            'manual_dmca': GameAction(
                name='manual_dmca',
                action_type='manual',
                ce_cost=5,
                time_seconds=900,  # 15 minutes
                base_success_rate=0.30,  # Often fails
                ce_reward_on_success=15,
                success_history=[],
                total_ce_spent=0,
                total_ce_earned=0,
                enabled=True,
                frustration_level=8,
                educational_value="DMCA takedowns are slow and often fail"
            ),

            'copyright_registration': GameAction(
                name='copyright_registration',
                action_type='manual',
                ce_cost=50,
                time_seconds=15552000,  # 6 months!
                base_success_rate=0.50,
                ce_reward_on_success=150,
                success_history=[],
                total_ce_spent=0,
                total_ce_earned=0,
                enabled=True,
                frustration_level=9,
                educational_value="Traditional copyright is EXTREMELY slow"
            ),

            'reverse_image_search': GameAction(
                name='reverse_image_search',
                action_type='manual',
                ce_cost=10,
                time_seconds=1800,  # 30 minutes
                base_success_rate=0.40,
                ce_reward_on_success=25,
                success_history=[],
                total_ce_spent=0,
                total_ce_earned=0,
                enabled=True,
                frustration_level=7,
                educational_value="Manual searches miss 60% of theft"
            ),

            # BLOOM-POWERED ACTIONS (Low frustration, high success)
            'bloom_fingerprint': GameAction(
                name='bloom_fingerprint',
                action_type='bloom_powered',
                ce_cost=10,
                time_seconds=1,  # Instant!
                base_success_rate=0.95,
                ce_reward_on_success=50,
                success_history=[],
                total_ce_spent=0,
                total_ce_earned=0,
                enabled=True,
                frustration_level=1,
                educational_value="BLOOM's fingerprinting is instant and reliable"
            ),

            'bloom_auto_monitor': GameAction(
                name='bloom_auto_monitor',
                action_type='bloom_powered',
                ce_cost=20,
                time_seconds=0,  # Passive!
                base_success_rate=0.90,
                ce_reward_on_success=100,
                success_history=[],
                total_ce_spent=0,
                total_ce_earned=0,
                enabled=True,
                frustration_level=0,
                educational_value="Automated monitoring works while you create"
            ),

            'bloom_blockchain_proof': GameAction(
                name='bloom_blockchain_proof',
                action_type='bloom_powered',
                ce_cost=15,
                time_seconds=5,  # Nearly instant
                base_success_rate=0.99,
                ce_reward_on_success=75,
                success_history=[],
                total_ce_spent=0,
                total_ce_earned=0,
                enabled=True,
                frustration_level=0,
                educational_value="Blockchain proof is irrefutable and fast"
            ),

            # AUTOMATED (Middle ground)
            'automated_watermark': GameAction(
                name='automated_watermark',
                action_type='automated',
                ce_cost=15,
                time_seconds=60,
                base_success_rate=0.60,
                ce_reward_on_success=40,
                success_history=[],
                total_ce_spent=0,
                total_ce_earned=0,
                enabled=True,
                frustration_level=4,
                educational_value="Watermarks help but can be removed"
            ),
        }

        return actions

    def get_player_tier(self) -> PlayerTier:
        """Determine player tier based on CE balance"""
        if self.creative_energy < 500:
            return PlayerTier.NOVICE
        elif self.creative_energy < 2500:
            return PlayerTier.DEFENDER
        else:
            return PlayerTier.GUARDIAN

    def _reset_daily_ce_if_needed(self):
        """Reset daily CE spending counter"""
        today = datetime.now().date()
        if today != self.last_reset_date:
            self.today_ce_spent = 0
            self.last_reset_date = today
            logger.info(f"Daily CE reset for {self.player_id}")

    def earn_ce(self, amount: int, threat_type: ThreatType, action_name: str,
                success: bool, bloom_feature: Optional[str] = None):
        """
        Earn Creative Energy (replaces record_commission).
        This is the core reward mechanism.
        """
        event = CEEvent(
            timestamp=datetime.now().isoformat(),
            ce_amount=amount,
            threat_type=threat_type.value,
            action_taken=action_name,
            success=success,
            bloom_feature_used=bloom_feature
        )

        if success:
            self.creative_energy += amount
            self.total_ce_earned += amount
            self.threats_defeated += 1
            self.current_streak += 1

            # Track BLOOM feature discovery
            if bloom_feature and bloom_feature not in self.bloom_features_discovered:
                self.bloom_features_discovered.append(bloom_feature)
                logger.info(f"🎉 Player discovered BLOOM feature: {bloom_feature}")
        else:
            self.threats_failed += 1
            self.current_streak = 0

        self.ce_history.append(event)

        # Update action learning
        if action_name in self.actions:
            action = self.actions[action_name]
            action.success_history.append(success)
            if success:
                action.total_ce_earned += amount

        logger.info(f"{'💰 SUCCESS' if success else '❌ FAILED'}: {action_name} "
                   f"{'earned' if success else 'missed'} {amount} CE | "
                   f"Balance: {self.creative_energy} CE | Streak: {self.current_streak}")

        return event

    def _score_action(self, action: GameAction) -> float:
        """
        Score action for AI selection (same algorithm as agent).
        Higher score = more likely to be chosen.
        """
        tier = self.get_player_tier()

        # Base score from expected CE return
        expected = action.expected_ce_return()

        # Tier-specific multipliers (same pattern as operating modes)
        if tier == PlayerTier.NOVICE:
            # Novices should learn with manual actions first (see the pain)
            if len(action.success_history) < 3:
                return expected * 0.5
            if action.average_success_rate() < 0.5:
                return 0.0
            return expected * 1.0

        elif tier == PlayerTier.DEFENDER:
            # Defenders balance manual and BLOOM
            if len(action.success_history) < 3:
                return expected * 0.7
            if action.action_type == 'bloom_powered':
                return expected * 1.5  # Encourage BLOOM discovery
            return expected * 1.0

        else:  # GUARDIAN
            # Guardians maximize BLOOM features
            if action.action_type == 'bloom_powered' and action.recent_success_rate(10) > 0.85:
                return expected * 2.0
            if len(action.success_history) < 5:
                return expected * 0.8
            return expected * 1.0

    def choose_action(self) -> Optional[Tuple[str, GameAction]]:
        """
        AI chooses best action (same as choose_next_strategy).
        This is where the learning happens!
        """
        self._reset_daily_ce_if_needed()
        tier = self.get_player_tier()
        daily_limit = self.DAILY_CE_LIMITS[tier]

        # Filter to enabled and affordable actions
        affordable = {
            name: action for name, action in self.actions.items()
            if action.enabled
            and action.ce_cost <= self.creative_energy
            and (self.today_ce_spent + action.ce_cost) <= daily_limit
        }

        if not affordable:
            logger.warning(f"No affordable actions. CE: {self.creative_energy}, "
                         f"Daily spent: {self.today_ce_spent}/{daily_limit}")
            return None

        # Score all affordable actions
        scores = {name: self._score_action(action)
                 for name, action in affordable.items()}

        # Choose highest scoring action
        best_action = max(scores.items(), key=lambda x: x[1])
        action_name = best_action[0]

        logger.info(f"Selected action: {action_name} (score: {best_action[1]:.2f}) "
                   f"in {tier.value} tier")

        return action_name, self.actions[action_name]

    def spend_ce(self, amount: int, action_name: str) -> bool:
        """Spend CE on an action"""
        if amount > self.creative_energy:
            logger.warning(f"Insufficient CE for {action_name}: "
                         f"{amount} needed, {self.creative_energy} available")
            return False

        self.creative_energy -= amount
        self.total_ce_spent += amount
        self.today_ce_spent += amount

        if action_name in self.actions:
            self.actions[action_name].total_ce_spent += amount

        logger.info(f"💸 Spent {amount} CE on {action_name} | "
                   f"Remaining: {self.creative_energy} CE")

        return True

    def generate_scenario(self, threat_type: ThreatType, context: dict) -> str:
        """
        Generate IP threat scenario using Claude AI.
        This replaces generate_content from ai_agent.py
        """
        if not self.anthropic_client:
            return self._fallback_scenario(threat_type, context)

        tier = self.get_player_tier()

        prompt = f"""
        You are generating an IP protection game scenario for IP Defender.

        Context:
        - Threat Type: {threat_type.value}
        - Player Tier: {tier.value}
        - Player Specialization: {self.specialization.value}
        - Scenario: {context.get('scenario', 'general IP theft')}

        Create a short (2-3 sentences) educational scenario that:
        1. Describes a specific IP theft situation
        2. Makes the threat feel real and urgent
        3. Naturally demonstrates why automated protection is better

        The scenario should educate about IP protection while being engaging gameplay.
        """

        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}]
            )

            scenario = message.content[0].text
            logger.info(f"Generated scenario for {threat_type.value}")
            return scenario

        except Exception as e:
            logger.error(f"Error generating scenario: {e}")
            return self._fallback_scenario(threat_type, context)

    def _fallback_scenario(self, threat_type: ThreatType, context: dict) -> str:
        """Fallback scenarios when Claude unavailable"""
        scenarios = {
            ThreatType.AI_SCRAPING: "Your artwork was found in an AI training dataset without consent. It's being used to generate competing art styles.",
            ThreatType.DIRECT_COPY: "Someone directly copied your design and is selling it on Etsy. They've already made 50 sales.",
            ThreatType.MARKETPLACE_THEFT: "Your music track appeared on a stock music site without permission. It's priced at $49.",
            ThreatType.UNAUTHORIZED_USE: "A company used your illustration in their ad campaign. The campaign reached 2M people."
        }
        return scenarios.get(threat_type, "Your IP is being used without permission.")

    def get_performance_report(self) -> dict:
        """Generate player performance report"""
        tier = self.get_player_tier()

        # Calculate success rate
        total_attempts = self.threats_defeated + self.threats_failed
        success_rate = self.threats_defeated / total_attempts if total_attempts > 0 else 0

        # Action performance
        action_stats = []
        for name, action in self.actions.items():
            if action.total_ce_spent > 0 or action.total_ce_earned > 0:
                action_stats.append({
                    'name': name,
                    'type': action.action_type,
                    'ce_spent': action.total_ce_spent,
                    'ce_earned': action.total_ce_earned,
                    'net_ce': action.net_ce(),
                    'success_rate': action.average_success_rate(),
                    'frustration': action.frustration_level,
                    'attempts': len(action.success_history)
                })

        # Sort by net CE
        action_stats.sort(key=lambda x: x['net_ce'], reverse=True)

        return {
            'player_id': self.player_id,
            'specialization': self.specialization.value,
            'timestamp': datetime.now().isoformat(),
            'creative_energy': self.creative_energy,
            'total_ce_earned': self.total_ce_earned,
            'total_ce_spent': self.total_ce_spent,
            'net_ce': self.creative_energy,
            'player_tier': tier.value,
            'days_active': (datetime.now() - self.creation_date).days,
            'threats_defeated': self.threats_defeated,
            'threats_failed': self.threats_failed,
            'success_rate': success_rate,
            'current_streak': self.current_streak,
            'bloom_features_discovered': self.bloom_features_discovered,
            'action_performance': action_stats,
            'today_ce_spent': self.today_ce_spent,
            'daily_limit': self.DAILY_CE_LIMITS[tier]
        }

    def check_conversion_trigger(self) -> Optional[str]:
        """
        Check if player should see BLOOM conversion offer.
        This is the key conversion funnel logic!
        """
        # Trigger conditions (player has experienced the pain)
        if len(self.ce_history) < 10:
            return None  # Too early

        # Calculate frustration from manual actions
        manual_attempts = sum(
            len(a.success_history) for a in self.actions.values()
            if a.action_type == 'manual'
        )

        if manual_attempts < 5:
            return None  # Haven't felt manual pain yet

        # Check if they've discovered BLOOM superiority
        bloom_attempts = sum(
            len(a.success_history) for a in self.actions.values()
            if a.action_type == 'bloom_powered'
        )

        if bloom_attempts < 3:
            return "Try BLOOM's automated protection - it's much easier!"

        # Compare success rates
        manual_success = sum(
            a.average_success_rate() * len(a.success_history)
            for a in self.actions.values() if a.action_type == 'manual'
        ) / max(manual_attempts, 1)

        bloom_success = sum(
            a.average_success_rate() * len(a.success_history)
            for a in self.actions.values() if a.action_type == 'bloom_powered'
        ) / max(bloom_attempts, 1)

        # If BLOOM is clearly better, trigger conversion
        if bloom_success > manual_success + 0.3:
            return f"BLOOM's success rate ({bloom_success:.0%}) is {(bloom_success - manual_success):.0%} higher! Get the full version."

        return None

    def save_state(self, filepath: str):
        """Save player state"""
        state = {
            'player_id': self.player_id,
            'specialization': self.specialization.value,
            'creative_energy': self.creative_energy,
            'total_ce_earned': self.total_ce_earned,
            'total_ce_spent': self.total_ce_spent,
            'today_ce_spent': self.today_ce_spent,
            'last_reset_date': self.last_reset_date.isoformat(),
            'creation_date': self.creation_date.isoformat(),
            'threats_defeated': self.threats_defeated,
            'threats_failed': self.threats_failed,
            'current_streak': self.current_streak,
            'bloom_features_discovered': self.bloom_features_discovered,
            'ce_history': [asdict(event) for event in self.ce_history],
            'actions': {name: action.to_dict() for name, action in self.actions.items()}
        }

        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)

        logger.info(f"Player state saved to {filepath}")

    @staticmethod
    def load_state(filepath: str) -> 'IPDefender':
        """Load player state"""
        with open(filepath, 'r') as f:
            state = json.load(f)

        player = IPDefender(
            player_id=state['player_id'],
            initial_ce=state['creative_energy'],
            specialization=Specialization(state['specialization'])
        )

        player.total_ce_earned = state['total_ce_earned']
        player.total_ce_spent = state['total_ce_spent']
        player.today_ce_spent = state['today_ce_spent']
        player.last_reset_date = datetime.fromisoformat(state['last_reset_date']).date()
        player.creation_date = datetime.fromisoformat(state['creation_date'])
        player.threats_defeated = state['threats_defeated']
        player.threats_failed = state['threats_failed']
        player.current_streak = state['current_streak']
        player.bloom_features_discovered = state['bloom_features_discovered']

        # Load CE history
        player.ce_history = [
            CEEvent(**event) for event in state['ce_history']
        ]

        # Load actions
        player.actions = {
            name: GameAction.from_dict(action_data)
            for name, action_data in state['actions'].items()
        }

        logger.info(f"Player state loaded from {filepath}")
        return player
