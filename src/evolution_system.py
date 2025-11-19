"""
IP DEFENDER - Evolution System
Transforms agent_reproduction.py into player progression and unlocks.
Maintains evolutionary intelligence for game balancing.
"""

import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional
from game_engine import IPDefender, Specialization, PlayerTier

logger = logging.getLogger(__name__)


@dataclass
class EvolutionBenchmark:
    """
    Player evolution criteria (replaces ReproductionBenchmark).
    Instead of creating child agents, players unlock new abilities.
    """
    level: int
    min_total_ce: int              # Minimum total CE earned
    min_ce_balance: int            # Minimum current balance
    min_success_rate: float        # Minimum win rate
    min_days_active: int           # Minimum play days
    unlocked_specialization: Specialization
    specialization_bonus: str      # What this specialization unlocks
    achievement_name: str          # Achievement title

    def is_met(self, player: IPDefender, days_active: int) -> bool:
        """Check if player meets evolution criteria"""
        if player.total_ce_earned < self.min_total_ce:
            return False
        if player.creative_energy < self.min_ce_balance:
            return False
        if days_active < self.min_days_active:
            return False

        # Calculate success rate
        total_attempts = player.threats_defeated + player.threats_failed
        if total_attempts == 0:
            return False

        success_rate = player.threats_defeated / total_attempts
        if success_rate < self.min_success_rate:
            return False

        return True


# Define 6 evolution levels (mirrors reproduction benchmarks)
EVOLUTION_BENCHMARKS = [
    EvolutionBenchmark(
        level=1,
        min_total_ce=500,
        min_ce_balance=200,
        min_success_rate=0.60,
        min_days_active=3,
        unlocked_specialization=Specialization.DMCA_EXPERT,
        specialization_bonus="Unlock advanced DMCA strategies with 2x success rate",
        achievement_name="📜 DMCA Warrior"
    ),
    EvolutionBenchmark(
        level=2,
        min_total_ce=1200,
        min_ce_balance=400,
        min_success_rate=0.65,
        min_days_active=7,
        unlocked_specialization=Specialization.AUTO_DEFENDER,
        specialization_bonus="Unlock passive CE generation (earn while offline!)",
        achievement_name="🤖 Automation Master"
    ),
    EvolutionBenchmark(
        level=3,
        min_total_ce=2500,
        min_ce_balance=800,
        min_success_rate=0.70,
        min_days_active=14,
        unlocked_specialization=Specialization.BLOCKCHAIN_GUARDIAN,
        specialization_bonus="Unlock blockchain proof (99% success rate!)",
        achievement_name="⛓️ Blockchain Guardian"
    ),
    EvolutionBenchmark(
        level=4,
        min_total_ce=5000,
        min_ce_balance=1500,
        min_success_rate=0.75,
        min_days_active=21,
        unlocked_specialization=Specialization.COMMUNITY_PROTECTOR,
        specialization_bonus="Unlock squad system (team up with other players)",
        achievement_name="👥 Community Champion"
    ),
    EvolutionBenchmark(
        level=5,
        min_total_ce=10000,
        min_ce_balance=3000,
        min_success_rate=0.80,
        min_days_active=30,
        unlocked_specialization=Specialization.LEGAL_WARRIOR,
        specialization_bonus="Unlock enterprise-grade protection tools",
        achievement_name="⚖️ Legal Legend"
    ),
    EvolutionBenchmark(
        level=6,
        min_total_ce=20000,
        min_ce_balance=5000,
        min_success_rate=0.85,
        min_days_active=45,
        unlocked_specialization=Specialization.ENTERPRISE_SHIELD,
        specialization_bonus="Unlock ultimate protection (full BLOOM platform access)",
        achievement_name="🛡️ Ultimate Guardian"
    )
]


@dataclass
class PlayerProgress:
    """
    Tracks player's evolution journey.
    Replaces AgentGenealogy but for individual progression.
    """
    player_id: str
    current_specialization: Specialization
    unlocked_specializations: List[str]
    evolution_level: int
    achievements_earned: List[str]
    evolution_date: datetime
    total_evolutions: int

    def to_dict(self) -> dict:
        return {
            'player_id': self.player_id,
            'current_specialization': self.current_specialization.value,
            'unlocked_specializations': self.unlocked_specializations,
            'evolution_level': self.evolution_level,
            'achievements_earned': self.achievements_earned,
            'evolution_date': self.evolution_date.isoformat(),
            'total_evolutions': self.total_evolutions
        }

    @staticmethod
    def from_dict(data: dict) -> 'PlayerProgress':
        return PlayerProgress(
            player_id=data['player_id'],
            current_specialization=Specialization(data['current_specialization']),
            unlocked_specializations=data['unlocked_specializations'],
            evolution_level=data['evolution_level'],
            achievements_earned=data['achievements_earned'],
            evolution_date=datetime.fromisoformat(data['evolution_date']),
            total_evolutions=data['total_evolutions']
        )


class EvolutionManager:
    """
    Manages player evolution and progression.
    Replaces AgentColony but for single-player progression.
    """

    def __init__(self):
        self.players: Dict[str, IPDefender] = {}
        self.progress: Dict[str, PlayerProgress] = {}
        self.evolution_history: List[dict] = []

        logger.info("Evolution manager initialized")

    def add_player(self, player: IPDefender):
        """Add a player to tracking"""
        progress = PlayerProgress(
            player_id=player.player_id,
            current_specialization=player.specialization,
            unlocked_specializations=[player.specialization.value],
            evolution_level=0,
            achievements_earned=[],
            evolution_date=player.creation_date,
            total_evolutions=0
        )

        self.players[player.player_id] = player
        self.progress[player.player_id] = progress

        logger.info(f"Player '{player.player_id}' added to evolution tracking")

    def check_evolution_eligibility(self, player_id: str) -> Optional[EvolutionBenchmark]:
        """
        Check if player is eligible for evolution.
        Returns highest benchmark met, or None.
        """
        if player_id not in self.players:
            return None

        player = self.players[player_id]
        progress = self.progress[player_id]

        # Calculate days active
        days_active = (datetime.now() - player.creation_date).days

        # Check which benchmarks are met
        highest_met = None

        for benchmark in EVOLUTION_BENCHMARKS:
            # Skip if already unlocked
            if benchmark.unlocked_specialization.value in progress.unlocked_specializations:
                continue

            # Check if benchmark is met
            if benchmark.is_met(player, days_active):
                if highest_met is None or benchmark.level > highest_met.level:
                    highest_met = benchmark

        return highest_met

    def evolve_player(self, player_id: str, benchmark: EvolutionBenchmark) -> bool:
        """
        Evolve player by unlocking new specialization.
        Returns True if successful.
        """
        if player_id not in self.players:
            logger.error(f"Player '{player_id}' not found")
            return False

        player = self.players[player_id]
        progress = self.progress[player_id]

        # Unlock the specialization
        progress.unlocked_specializations.append(benchmark.unlocked_specialization.value)
        progress.evolution_level = benchmark.level
        progress.achievements_earned.append(benchmark.achievement_name)
        progress.total_evolutions += 1
        progress.evolution_date = datetime.now()

        # Apply specialization bonuses to player
        self._apply_specialization_bonus(player, benchmark.unlocked_specialization)

        # Record evolution event
        evolution_event = {
            'timestamp': datetime.now().isoformat(),
            'player_id': player_id,
            'evolution_level': benchmark.level,
            'specialization': benchmark.unlocked_specialization.value,
            'achievement': benchmark.achievement_name,
            'bonus': benchmark.specialization_bonus
        }
        self.evolution_history.append(evolution_event)

        logger.info(f"✨ EVOLUTION EVENT ✨")
        logger.info(f"Player: {player_id}")
        logger.info(f"Level: {benchmark.level}")
        logger.info(f"Specialization: {benchmark.unlocked_specialization.value}")
        logger.info(f"Achievement: {benchmark.achievement_name}")
        logger.info(f"Bonus: {benchmark.specialization_bonus}")

        return True

    def _apply_specialization_bonus(self, player: IPDefender,
                                   specialization: Specialization):
        """
        Apply specialization bonuses to player's abilities.
        This is where gameplay gets enhanced!
        """

        if specialization == Specialization.DMCA_EXPERT:
            # Improve manual DMCA success rate
            if 'manual_dmca' in player.actions:
                action = player.actions['manual_dmca']
                action.base_success_rate *= 2.0  # 2x success rate
                action.ce_reward_on_success = int(action.ce_reward_on_success * 1.5)
                logger.info("DMCA actions now 2x more successful!")

        elif specialization == Specialization.AUTO_DEFENDER:
            # Enable passive CE generation
            if 'bloom_auto_monitor' in player.actions:
                action = player.actions['bloom_auto_monitor']
                action.ce_cost = 0  # Free to use!
                action.ce_reward_on_success = int(action.ce_reward_on_success * 1.5)
                logger.info("Automated monitoring is now FREE and earns 50% more CE!")

        elif specialization == Specialization.BLOCKCHAIN_GUARDIAN:
            # Maximize blockchain proof
            if 'bloom_blockchain_proof' in player.actions:
                action = player.actions['bloom_blockchain_proof']
                action.base_success_rate = 0.99  # Nearly perfect
                action.ce_reward_on_success = int(action.ce_reward_on_success * 2.0)
                logger.info("Blockchain proof now 99% successful and 2x CE rewards!")

        elif specialization == Specialization.COMMUNITY_PROTECTOR:
            # Unlock squad/team mechanics (future feature)
            logger.info("Squad mechanics unlocked! (coming soon)")

        elif specialization == Specialization.LEGAL_WARRIOR:
            # Boost all actions
            for action in player.actions.values():
                action.base_success_rate = min(action.base_success_rate * 1.2, 0.99)
                action.ce_reward_on_success = int(action.ce_reward_on_success * 1.3)
            logger.info("All actions boosted! +20% success, +30% CE rewards")

        elif specialization == Specialization.ENTERPRISE_SHIELD:
            # Ultimate power: all BLOOM features at maximum
            for action in player.actions.values():
                if action.action_type == 'bloom_powered':
                    action.base_success_rate = 0.99
                    action.ce_cost = max(action.ce_cost // 2, 1)  # Half cost
                    action.ce_reward_on_success = int(action.ce_reward_on_success * 2.0)
            logger.info("ULTIMATE POWER: All BLOOM features maximized!")

    def run_evolution_check(self):
        """
        Check all players for evolution eligibility.
        This runs periodically in the game loop.
        """
        evolutions = 0

        for player_id in list(self.players.keys()):
            benchmark = self.check_evolution_eligibility(player_id)

            if benchmark:
                if self.evolve_player(player_id, benchmark):
                    evolutions += 1
                    logger.info(f"✨ Player '{player_id}' evolved to level {benchmark.level}")

        if evolutions > 0:
            logger.info(f"🎉 {evolutions} evolution(s) this cycle!")

        return evolutions

    def get_player_stats(self, player_id: str) -> Optional[dict]:
        """Get comprehensive player stats"""
        if player_id not in self.players:
            return None

        player = self.players[player_id]
        progress = self.progress[player_id]

        # Get player report
        report = player.get_performance_report()

        # Add evolution data
        report['evolution'] = {
            'current_level': progress.evolution_level,
            'total_evolutions': progress.total_evolutions,
            'unlocked_specializations': progress.unlocked_specializations,
            'achievements': progress.achievements_earned,
            'next_evolution': None
        }

        # Check next evolution
        next_benchmark = self.check_evolution_eligibility(player_id)
        if next_benchmark:
            days_active = (datetime.now() - player.creation_date).days
            total_attempts = player.threats_defeated + player.threats_failed
            current_success = player.threats_defeated / max(total_attempts, 1)

            report['evolution']['next_evolution'] = {
                'level': next_benchmark.level,
                'specialization': next_benchmark.unlocked_specialization.value,
                'achievement': next_benchmark.achievement_name,
                'bonus': next_benchmark.specialization_bonus,
                'progress': {
                    'ce_earned': f"{player.total_ce_earned}/{next_benchmark.min_total_ce}",
                    'ce_balance': f"{player.creative_energy}/{next_benchmark.min_ce_balance}",
                    'success_rate': f"{current_success:.1%}/{next_benchmark.min_success_rate:.1%}",
                    'days_active': f"{days_active}/{next_benchmark.min_days_active}",
                }
            }

        return report

    def get_leaderboard(self, metric: str = 'ce_earned', limit: int = 10) -> List[dict]:
        """
        Get player leaderboard.
        This encourages competition and engagement!
        """
        leaderboard = []

        for player_id, player in self.players.items():
            progress = self.progress[player_id]

            entry = {
                'player_id': player_id,
                'ce_earned': player.total_ce_earned,
                'threats_defeated': player.threats_defeated,
                'current_streak': player.current_streak,
                'evolution_level': progress.evolution_level,
                'achievements': len(progress.achievements_earned),
                'specializations': len(progress.unlocked_specializations)
            }

            leaderboard.append(entry)

        # Sort by metric
        leaderboard.sort(key=lambda x: x.get(metric, 0), reverse=True)

        return leaderboard[:limit]

    def save_evolution_state(self, directory: str = 'data'):
        """Save all evolution data"""
        os.makedirs(directory, exist_ok=True)

        # Save each player
        for player_id, player in self.players.items():
            filepath = f"{directory}/{player_id}_state.json"
            player.save_state(filepath)

        # Save progress data
        progress_data = {
            player_id: prog.to_dict()
            for player_id, prog in self.progress.items()
        }

        with open(f"{directory}/evolution_progress.json", 'w') as f:
            json.dump(progress_data, f, indent=2)

        # Save evolution history
        with open(f"{directory}/evolution_history.json", 'w') as f:
            json.dump(self.evolution_history, f, indent=2)

        logger.info(f"Evolution state saved to {directory}/")

    @staticmethod
    def load_evolution_state(directory: str = 'data') -> 'EvolutionManager':
        """Load evolution state from files"""
        manager = EvolutionManager()

        # Load progress data
        with open(f"{directory}/evolution_progress.json", 'r') as f:
            progress_data = json.load(f)

        for player_id, data in progress_data.items():
            progress = PlayerProgress.from_dict(data)
            manager.progress[player_id] = progress

        # Load each player
        for player_id in progress_data.keys():
            filepath = f"{directory}/{player_id}_state.json"
            if os.path.exists(filepath):
                player = IPDefender.load_state(filepath)
                manager.players[player_id] = player

        # Load evolution history
        history_path = f"{directory}/evolution_history.json"
        if os.path.exists(history_path):
            with open(history_path, 'r') as f:
                manager.evolution_history = json.load(f)

        logger.info(f"Evolution state loaded - {len(manager.players)} players")

        return manager
