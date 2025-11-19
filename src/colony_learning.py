"""
BLOOM AI Agent - Collaborative Learning System

Agents learn from the BEST performer while protecting promising experiments.

Key Innovation:
- Agents share knowledge collaboratively (no "loser bots")
- Promising experiments are PROTECTED even if ROI is currently low
- Balances short-term optimization with long-term discovery
- Prevents "local maximum trap" where colony misses better strategies
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class LearningRole(Enum):
    """Roles agents can play in colony learning"""
    OPTIMIZER = "Optimizer"        # 60% - Copy proven winners
    EXPERIMENTER = "Experimenter"  # 30% - Test promising strategies
    INNOVATOR = "Innovator"        # 10% - Explore wild new ideas


@dataclass
class StrategyInsight:
    """Insight about what's working in the colony"""
    strategy_name: str
    platform: str
    avg_roi: float
    trend: str  # 'improving', 'declining', 'flat'
    sample_size: int
    best_agent_id: str

    def __str__(self):
        return (f"{self.strategy_name} on {self.platform}: "
                f"{self.avg_roi:.2f}x ROI ({self.trend}, "
                f"{self.sample_size} samples, "
                f"best: {self.best_agent_id})")


@dataclass
class ExperimentStatus:
    """Track an agent's experiment to see if it's promising"""
    agent_id: str
    strategy_name: str
    platform: str
    start_date: datetime
    roi_history: List[float] = field(default_factory=list)

    def days_running(self) -> int:
        """How long has this experiment been running?"""
        return (datetime.now() - self.start_date).days

    def is_improving(self, min_trend: float = 0.1) -> bool:
        """Is ROI trending upward?"""
        if len(self.roi_history) < 3:
            return True  # Too early to tell, give it a chance

        # Linear regression to find trend
        # Simple version: compare first half to second half
        mid = len(self.roi_history) // 2
        first_half_avg = sum(self.roi_history[:mid]) / mid
        second_half_avg = sum(self.roi_history[mid:]) / (len(self.roi_history) - mid)

        improvement = second_half_avg - first_half_avg
        return improvement >= min_trend

    def current_roi(self) -> float:
        """Current ROI (latest measurement)"""
        return self.roi_history[-1] if self.roi_history else 0.0

    def should_protect(self, min_roi: float = 1.5, max_age_days: int = 28) -> bool:
        """
        Should we protect this experiment from being abandoned?

        Protect if:
        - It's improving over time
        - ROI is above minimum viable (1.5x)
        - It's been running < 4 weeks (give it time!)
        """
        if self.days_running() > max_age_days:
            return False  # Had enough time, not working

        if self.current_roi() < min_roi:
            return False  # Too low to justify continuing

        if self.is_improving():
            return True  # Trending up! Keep going!

        return False


class ColonyLearning:
    """
    Collaborative learning system for agent colony.

    Agents learn from the best while protecting promising experiments.
    Prevents "local maximum trap" where colony misses better long-term strategies.
    """

    def __init__(self, colony_id: str = "main"):
        self.colony_id = colony_id

        # Track experiments
        self.active_experiments: Dict[str, ExperimentStatus] = {}

        # Learning history
        self.learning_sessions: List[dict] = []

        # Role distribution (can be tuned)
        self.role_distribution = {
            LearningRole.OPTIMIZER: 0.60,     # 60% copy winners
            LearningRole.EXPERIMENTER: 0.30,  # 30% protected experiments
            LearningRole.INNOVATOR: 0.10      # 10% wild innovation
        }

        logger.info(f"Colony learning system initialized for {colony_id}")

    def analyze_colony_performance(self, colony) -> Dict[str, any]:
        """
        Analyze what's working across the colony.

        Returns insights about:
        - Best performing strategies
        - Best performing platforms
        - Trending strategies (improving over time)
        - Top performer agent
        """
        if not colony.agents:
            return {}

        # Find best overall performer
        best_agent_id = None
        best_roi = 0.0

        for agent_id, agent in colony.agents.items():
            overall_roi = agent.total_earned / agent.total_spent if agent.total_spent > 0 else 0
            if overall_roi > best_roi:
                best_roi = overall_roi
                best_agent_id = agent_id

        if not best_agent_id:
            return {}

        best_agent = colony.agents[best_agent_id]

        # Analyze best agent's strategies
        winning_strategies = []

        for strategy_name, strategy in best_agent.strategies.items():
            if not strategy.enabled:
                continue

            avg_roi = strategy.average_roi()
            if avg_roi > 2.0:  # Only consider strategies with good ROI
                # Determine platform from strategy name
                platform = 'unknown'
                if 'discord' in strategy_name.lower():
                    platform = 'discord'
                elif 'telegram' in strategy_name.lower():
                    platform = 'telegram'
                elif 'slack' in strategy_name.lower():
                    platform = 'slack'
                elif 'reddit' in strategy_name.lower():
                    platform = 'reddit'
                elif 'twitter' in strategy_name.lower():
                    platform = 'twitter'

                # Determine trend
                trend = 'flat'
                if len(strategy.roi_history) >= 5:
                    recent = strategy.roi_history[-3:]
                    older = strategy.roi_history[-6:-3] if len(strategy.roi_history) >= 6 else strategy.roi_history[:-3]
                    recent_avg = sum(recent) / len(recent)
                    older_avg = sum(older) / len(older) if older else recent_avg

                    if recent_avg > older_avg + 0.2:
                        trend = 'improving'
                    elif recent_avg < older_avg - 0.2:
                        trend = 'declining'

                insight = StrategyInsight(
                    strategy_name=strategy_name,
                    platform=platform,
                    avg_roi=avg_roi,
                    trend=trend,
                    sample_size=len(strategy.roi_history),
                    best_agent_id=best_agent_id
                )
                winning_strategies.append(insight)

        # Sort by ROI
        winning_strategies.sort(key=lambda x: x.avg_roi, reverse=True)

        return {
            'best_agent_id': best_agent_id,
            'best_agent_roi': best_roi,
            'winning_strategies': winning_strategies[:5],  # Top 5
            'analysis_timestamp': datetime.now().isoformat()
        }

    def register_experiment(self, agent_id: str, strategy_name: str,
                           platform: str, current_roi: float):
        """
        Register an agent's experiment to track its progress.

        This protects promising experiments from being abandoned too early.
        """
        key = f"{agent_id}_{strategy_name}"

        if key not in self.active_experiments:
            self.active_experiments[key] = ExperimentStatus(
                agent_id=agent_id,
                strategy_name=strategy_name,
                platform=platform,
                start_date=datetime.now()
            )

        # Add current ROI to history
        self.active_experiments[key].roi_history.append(current_roi)

        logger.debug(f"Registered experiment: {agent_id} testing {strategy_name} "
                    f"(ROI: {current_roi:.2f}x, day {self.active_experiments[key].days_running()})")

    def assign_learning_roles(self, colony) -> Dict[str, LearningRole]:
        """
        Assign each agent a learning role based on their current status.

        Roles:
        - OPTIMIZER: Copy proven winners (for struggling agents)
        - EXPERIMENTER: Protect promising experiments (for improving agents)
        - INNOVATOR: Try new things (for successful agents)
        """
        if not colony.agents:
            return {}

        roles = {}

        # Calculate colony average ROI
        total_roi = 0.0
        count = 0
        for agent in colony.agents.values():
            roi = agent.total_earned / agent.total_spent if agent.total_spent > 0 else 0
            total_roi += roi
            count += 1

        avg_colony_roi = total_roi / count if count > 0 else 2.0

        for agent_id, agent in colony.agents.items():
            agent_roi = agent.total_earned / agent.total_spent if agent.total_spent > 0 else 0

            # Check if this agent has a protected experiment
            has_protected_experiment = False
            for key, exp in self.active_experiments.items():
                if exp.agent_id == agent_id and exp.should_protect():
                    has_protected_experiment = True
                    break

            # Assign role based on performance and experiments
            if has_protected_experiment:
                # Protect this agent's experiment
                roles[agent_id] = LearningRole.EXPERIMENTER

            elif agent_roi < avg_colony_roi * 0.7:
                # Struggling (< 70% of average)
                roles[agent_id] = LearningRole.OPTIMIZER

            elif agent_roi > avg_colony_roi * 1.3:
                # Successful (> 130% of average)
                roles[agent_id] = LearningRole.INNOVATOR

            else:
                # Middle of the pack - could experiment or optimize
                # Use role distribution to decide
                import random
                if random.random() < 0.5:
                    roles[agent_id] = LearningRole.EXPERIMENTER
                else:
                    roles[agent_id] = LearningRole.OPTIMIZER

        return roles

    def run_learning_session(self, colony) -> dict:
        """
        Run a collaborative learning session.

        Steps:
        1. Analyze what's working (find best strategies/platforms)
        2. Assign learning roles to each agent
        3. Share insights:
           - Optimizers: Copy the winner
           - Experimenters: Keep your experiment (it's showing promise!)
           - Innovators: Try variations on what works
        4. Record session for history
        """
        logger.info("🧠 Running colony learning session...")

        # 1. Analyze performance
        insights = self.analyze_colony_performance(colony)

        if not insights:
            logger.info("Not enough data for learning session yet")
            return {}

        best_agent_id = insights['best_agent_id']
        winning_strategies = insights['winning_strategies']

        logger.info(f"📊 Best performer: {best_agent_id} ({insights['best_agent_roi']:.2f}x ROI)")
        logger.info(f"🏆 Top strategies:")
        for i, strategy in enumerate(winning_strategies, 1):
            logger.info(f"  {i}. {strategy}")

        # 2. Assign roles
        roles = self.assign_learning_roles(colony)

        # Count roles
        role_counts = {role: 0 for role in LearningRole}
        for role in roles.values():
            role_counts[role] += 1

        logger.info(f"\n📋 Learning roles assigned:")
        for role, count in role_counts.items():
            logger.info(f"  {role.value}: {count} agents")

        # 3. Apply learning
        learning_actions = []

        for agent_id, role in roles.items():
            agent = colony.agents[agent_id]
            agent_roi = agent.total_earned / agent.total_spent if agent.total_spent > 0 else 0

            if role == LearningRole.OPTIMIZER:
                # Copy the winner
                action = self._apply_optimizer_learning(agent, colony.agents[best_agent_id], winning_strategies)
                learning_actions.append({
                    'agent_id': agent_id,
                    'role': 'Optimizer',
                    'action': action,
                    'current_roi': agent_roi
                })

            elif role == LearningRole.EXPERIMENTER:
                # Protect experiment
                action = f"Continue experiment (showing promise!)"
                learning_actions.append({
                    'agent_id': agent_id,
                    'role': 'Experimenter',
                    'action': action,
                    'current_roi': agent_roi
                })

            elif role == LearningRole.INNOVATOR:
                # Try new variations
                action = f"Innovate on winning strategies"
                learning_actions.append({
                    'agent_id': agent_id,
                    'role': 'Innovator',
                    'action': action,
                    'current_roi': agent_roi
                })

        # 4. Record session
        session = {
            'timestamp': datetime.now().isoformat(),
            'best_agent': best_agent_id,
            'best_roi': insights['best_agent_roi'],
            'winning_strategies': [str(s) for s in winning_strategies],
            'role_distribution': {role.value: count for role, count in role_counts.items()},
            'actions': learning_actions
        }

        self.learning_sessions.append(session)

        logger.info(f"\n✅ Learning session complete! {len(learning_actions)} agents learned.")

        return session

    def _apply_optimizer_learning(self, agent, best_agent, winning_strategies) -> str:
        """
        Apply learning from best agent to optimizer agent.

        Increases weight of winning strategies in agent's selection.
        """
        if not winning_strategies:
            return "No winning strategies to learn from"

        # Get top winning strategy
        top_strategy = winning_strategies[0]

        # If agent has this strategy, boost its preference
        if top_strategy.strategy_name in agent.strategies:
            strategy = agent.strategies[top_strategy.strategy_name]

            # Copy ROI history from best agent (knowledge transfer!)
            if top_strategy.strategy_name in best_agent.strategies:
                best_strategy = best_agent.strategies[top_strategy.strategy_name]
                # Blend ROI histories (50% from best agent, 50% keep own)
                if best_strategy.roi_history:
                    strategy.roi_history = (
                        strategy.roi_history[-3:] +  # Keep recent 3
                        best_strategy.roi_history[-3:]  # Add best's recent 3
                    )

            return f"Learned {top_strategy.strategy_name} from {top_strategy.best_agent_id} ({top_strategy.avg_roi:.2f}x ROI)"

        return f"Adopted focus on {top_strategy.platform} platform"

    def get_learning_history(self, limit: int = 5) -> List[dict]:
        """Get recent learning sessions"""
        return self.learning_sessions[-limit:]

    def get_experiment_status(self, agent_id: str) -> Optional[ExperimentStatus]:
        """Get current experiment status for an agent"""
        for exp in self.active_experiments.values():
            if exp.agent_id == agent_id and exp.should_protect():
                return exp
        return None


def print_learning_report(session: dict):
    """Pretty print learning session report"""
    print("\n" + "="*80)
    print("🧠 COLONY LEARNING SESSION REPORT".center(80))
    print("="*80)

    print(f"\n🏆 Best Performer: {session['best_agent']}")
    print(f"   ROI: {session['best_roi']:.2f}x")

    print(f"\n📊 Winning Strategies:")
    for i, strategy in enumerate(session['winning_strategies'], 1):
        print(f"   {i}. {strategy}")

    print(f"\n📋 Role Distribution:")
    for role, count in session['role_distribution'].items():
        print(f"   {role}: {count} agents")

    print(f"\n💡 Learning Actions:")
    for action in session['actions'][:10]:  # Show top 10
        print(f"   {action['agent_id']} ({action['role']}): {action['action']}")
        print(f"      Current ROI: {action['current_roi']:.2f}x")

    print("\n" + "="*80 + "\n")
