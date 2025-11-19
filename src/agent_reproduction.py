"""
BLOOM AI Agent - Cellular Reproduction System
Manages agent reproduction and colony genealogy.
"""

import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from ai_agent import BloomAIAgent, Specialization
from agent_competition import AgentCompetition

logger = logging.getLogger(__name__)


@dataclass
class ReproductionBenchmark:
    """Criteria for agent reproduction"""
    level: int
    min_total_earned: float
    min_balance: float
    min_roi: float
    min_days_active: int
    child_specialization: Specialization
    child_starting_balance: float

    def is_met(self, agent: BloomAIAgent, days_active: int) -> bool:
        """Check if agent meets all benchmark criteria"""
        if agent.total_earned < self.min_total_earned:
            return False
        if agent.commission_balance < self.min_balance:
            return False
        if days_active < self.min_days_active:
            return False

        # Calculate overall ROI
        overall_roi = agent.total_earned / agent.total_spent if agent.total_spent > 0 else 0
        if overall_roi < self.min_roi:
            return False

        return True


# Define all 6 reproduction benchmarks
REPRODUCTION_BENCHMARKS = [
    ReproductionBenchmark(
        level=1,
        min_total_earned=500.0,
        min_balance=200.0,
        min_roi=2.5,
        min_days_active=14,
        child_specialization=Specialization.REDDIT_SPECIALIST,
        child_starting_balance=100.0
    ),
    ReproductionBenchmark(
        level=2,
        min_total_earned=1200.0,
        min_balance=400.0,
        min_roi=3.0,
        min_days_active=30,
        child_specialization=Specialization.TWITTER_SPECIALIST,
        child_starting_balance=150.0
    ),
    ReproductionBenchmark(
        level=3,
        min_total_earned=2500.0,
        min_balance=800.0,
        min_roi=3.5,
        min_days_active=45,
        child_specialization=Specialization.CONTENT_CREATOR,
        child_starting_balance=200.0
    ),
    ReproductionBenchmark(
        level=4,
        min_total_earned=5000.0,
        min_balance=1500.0,
        min_roi=4.0,
        min_days_active=60,
        child_specialization=Specialization.COMMUNITY_ENGAGER,
        child_starting_balance=300.0
    ),
    ReproductionBenchmark(
        level=5,
        min_total_earned=10000.0,
        min_balance=3000.0,
        min_roi=4.5,
        min_days_active=90,
        child_specialization=Specialization.PAID_ADVERTISER,
        child_starting_balance=500.0
    ),
    ReproductionBenchmark(
        level=6,
        min_total_earned=20000.0,
        min_balance=5000.0,
        min_roi=5.0,
        min_days_active=120,
        child_specialization=Specialization.ENTERPRISE_HUNTER,
        child_starting_balance=1000.0
    )
]


@dataclass
class AgentGenealogy:
    """Tracks agent family tree and reproduction history"""
    agent_id: str
    parent_id: Optional[str]
    generation: int
    specialization: Specialization
    birth_date: datetime
    birth_balance: float
    children: List[str]  # List of child agent IDs

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'agent_id': self.agent_id,
            'parent_id': self.parent_id,
            'generation': self.generation,
            'specialization': self.specialization.value,
            'birth_date': self.birth_date.isoformat(),
            'birth_balance': self.birth_balance,
            'children': self.children
        }

    @staticmethod
    def from_dict(data: dict) -> 'AgentGenealogy':
        """Create from dictionary"""
        return AgentGenealogy(
            agent_id=data['agent_id'],
            parent_id=data['parent_id'],
            generation=data['generation'],
            specialization=Specialization(data['specialization']),
            birth_date=datetime.fromisoformat(data['birth_date']),
            birth_balance=data['birth_balance'],
            children=data['children']
        )


class AgentColony:
    """
    Manages a colony of AI agents with reproduction capability.
    Now includes competition system for performance-based rewards!
    """

    def __init__(self, colony_id: str = "main"):
        """Initialize empty colony"""
        self.colony_id = colony_id
        self.agents: Dict[str, BloomAIAgent] = {}
        self.genealogy: Dict[str, AgentGenealogy] = {}
        self.reproduction_history: List[dict] = []

        # Competition system for performance-based rewards
        self.competition = AgentCompetition(colony_id=colony_id)

        logger.info(f"Agent colony '{colony_id}' initialized with competition system")

    def add_agent(self, agent: BloomAIAgent, agent_id: str,
                  parent_id: Optional[str] = None,
                  specialization: Specialization = Specialization.GENERALIST):
        """Add an agent to the colony"""

        # Determine generation
        generation = 0
        if parent_id and parent_id in self.genealogy:
            generation = self.genealogy[parent_id].generation + 1

        # Create genealogy record
        genealogy = AgentGenealogy(
            agent_id=agent_id,
            parent_id=parent_id,
            generation=generation,
            specialization=specialization,
            birth_date=agent.creation_date,
            birth_balance=agent.commission_balance,
            children=[]
        )

        # Update parent's children list
        if parent_id and parent_id in self.genealogy:
            self.genealogy[parent_id].children.append(agent_id)

        self.agents[agent_id] = agent
        self.genealogy[agent_id] = genealogy

        logger.info(f"Agent '{agent_id}' added to colony - "
                   f"Generation: {generation}, "
                   f"Specialization: {specialization.value}, "
                   f"Balance: ${agent.commission_balance:.2f}")

    def check_reproduction_eligibility(self, agent_id: str) -> Optional[ReproductionBenchmark]:
        """
        Check if an agent is eligible for reproduction.
        Returns the highest benchmark met, or None if none met.
        """
        if agent_id not in self.agents:
            return None

        agent = self.agents[agent_id]
        genealogy = self.genealogy[agent_id]

        # Calculate days active
        days_active = (datetime.now() - agent.creation_date).days

        # Check which benchmarks are met
        # Start from highest level and work down to find the first unmet level
        highest_met = None

        for benchmark in REPRODUCTION_BENCHMARKS:
            # Check if this level has already been reproduced
            child_count_at_level = sum(
                1 for child_id in genealogy.children
                if self.genealogy[child_id].specialization == benchmark.child_specialization
            )

            # Only allow one reproduction per benchmark level
            if child_count_at_level > 0:
                continue

            # Check if benchmark is met
            if benchmark.is_met(agent, days_active):
                if highest_met is None or benchmark.level > highest_met.level:
                    highest_met = benchmark

        return highest_met

    def reproduce_agent(self, parent_id: str, benchmark: ReproductionBenchmark) -> Optional[str]:
        """
        Create a child agent through reproduction.
        Returns child agent ID if successful.
        """
        if parent_id not in self.agents:
            logger.error(f"Parent agent '{parent_id}' not found")
            return None

        parent = self.agents[parent_id]

        # Check if parent has enough balance
        if parent.commission_balance < benchmark.child_starting_balance:
            logger.warning(f"Parent '{parent_id}' lacks funds for reproduction: "
                         f"${parent.commission_balance:.2f} < ${benchmark.child_starting_balance:.2f}")
            return None

        # Generate child ID
        child_id = f"{parent_id}_child_{len(self.genealogy[parent_id].children) + 1}"

        # Transfer funds from parent to child
        parent.commission_balance -= benchmark.child_starting_balance

        # Create child agent
        child = BloomAIAgent(
            agent_id=child_id,
            initial_balance=benchmark.child_starting_balance,
            specialization=benchmark.child_specialization
        )

        # Apply specialization (inherit parent's ROI knowledge for relevant strategies)
        self._apply_specialization(child, benchmark.child_specialization, parent)

        # Add child to colony
        self.add_agent(
            agent=child,
            agent_id=child_id,
            parent_id=parent_id,
            specialization=benchmark.child_specialization
        )

        # Record reproduction event
        reproduction_event = {
            'timestamp': datetime.now().isoformat(),
            'parent_id': parent_id,
            'child_id': child_id,
            'benchmark_level': benchmark.level,
            'specialization': benchmark.child_specialization.value,
            'starting_balance': benchmark.child_starting_balance,
            'parent_balance_after': parent.commission_balance
        }
        self.reproduction_history.append(reproduction_event)

        logger.info(f"🧬 REPRODUCTION EVENT 🧬")
        logger.info(f"Parent: {parent_id}")
        logger.info(f"Child: {child_id}")
        logger.info(f"Level: {benchmark.level}")
        logger.info(f"Specialization: {benchmark.child_specialization.value}")
        logger.info(f"Child Balance: ${benchmark.child_starting_balance:.2f}")
        logger.info(f"Parent Balance After: ${parent.commission_balance:.2f}")

        return child_id

    def _apply_specialization(self, agent: BloomAIAgent, specialization: Specialization,
                             parent: BloomAIAgent):
        """
        Apply specialization to child agent.
        Inherits parent's ROI knowledge for relevant strategies and disables irrelevant ones.
        """

        if specialization == Specialization.REDDIT_SPECIALIST:
            # Only enable Reddit strategies
            for name, strategy in agent.strategies.items():
                if 'twitter' in name:
                    strategy.enabled = False
                elif name in parent.strategies:
                    # Inherit parent's ROI history for Reddit strategies
                    parent_strat = parent.strategies[name]
                    strategy.roi_history = parent_strat.roi_history.copy()

        elif specialization == Specialization.TWITTER_SPECIALIST:
            # Only enable Twitter strategies
            for name, strategy in agent.strategies.items():
                if 'reddit' in name:
                    strategy.enabled = False
                elif name in parent.strategies:
                    # Inherit parent's ROI history for Twitter strategies
                    parent_strat = parent.strategies[name]
                    strategy.roi_history = parent_strat.roi_history.copy()

        elif specialization == Specialization.CONTENT_CREATOR:
            # Only enable post/thread creation strategies (no comments/replies)
            for name, strategy in agent.strategies.items():
                if 'comment' in name or 'reply' in name:
                    strategy.enabled = False
                elif name in parent.strategies:
                    parent_strat = parent.strategies[name]
                    strategy.roi_history = parent_strat.roi_history.copy()

        elif specialization == Specialization.COMMUNITY_ENGAGER:
            # Only enable comment/reply strategies (no posts/threads)
            for name, strategy in agent.strategies.items():
                if 'post' in name or 'thread' in name or 'boost' in name or 'promoted' in name:
                    strategy.enabled = False
                elif name in parent.strategies:
                    parent_strat = parent.strategies[name]
                    strategy.roi_history = parent_strat.roi_history.copy()

        elif specialization == Specialization.PAID_ADVERTISER:
            # Only enable paid promotion strategies with 10x spending limit
            for name, strategy in agent.strategies.items():
                if 'boost' not in name and 'promoted' not in name:
                    strategy.enabled = False
                else:
                    # 10x spending limits for paid advertiser
                    strategy.cost_per_action *= 10
                    if name in parent.strategies:
                        parent_strat = parent.strategies[name]
                        strategy.roi_history = parent_strat.roi_history.copy()

        elif specialization == Specialization.ENTERPRISE_HUNTER:
            # Enable all strategies, inherit all knowledge
            # 20% commission rate (2x) for enterprise clients
            for name, strategy in agent.strategies.items():
                if name in parent.strategies:
                    parent_strat = parent.strategies[name]
                    strategy.roi_history = parent_strat.roi_history.copy()

            # Note: The 2x commission is handled in the webhook when recording commissions

        # GENERALIST inherits everything as-is (default behavior)

        logger.info(f"Specialization applied: {specialization.value}")
        enabled_count = sum(1 for s in agent.strategies.values() if s.enabled)
        logger.info(f"Enabled strategies: {enabled_count}/{len(agent.strategies)}")

    def run_reproduction_cycle(self):
        """
        Check all agents for reproduction eligibility and reproduce if possible.
        """
        reproductions = 0

        for agent_id in list(self.agents.keys()):  # Use list() to avoid modification during iteration
            benchmark = self.check_reproduction_eligibility(agent_id)

            if benchmark:
                child_id = self.reproduce_agent(agent_id, benchmark)
                if child_id:
                    reproductions += 1
                    logger.info(f"✨ Agent '{agent_id}' successfully reproduced → '{child_id}'")

        if reproductions > 0:
            logger.info(f"🎉 {reproductions} reproduction(s) in this cycle!")
        else:
            logger.debug("No reproductions this cycle")

        return reproductions

    def get_colony_stats(self) -> dict:
        """Get comprehensive colony statistics"""
        if not self.agents:
            return {'colony_size': 0}

        # Calculate totals
        total_balance = sum(agent.commission_balance for agent in self.agents.values())
        total_earned = sum(agent.total_earned for agent in self.agents.values())
        total_spent = sum(agent.total_spent for agent in self.agents.values())
        total_conversions = sum(len(agent.commission_history) for agent in self.agents.values())

        # Calculate overall ROI
        overall_roi = total_earned / total_spent if total_spent > 0 else 0

        # Generation stats
        generations = {}
        for genealogy in self.genealogy.values():
            gen = genealogy.generation
            if gen not in generations:
                generations[gen] = 0
            generations[gen] += 1

        # Specialization stats
        specializations = {}
        for genealogy in self.genealogy.values():
            spec = genealogy.specialization.value
            if spec not in specializations:
                specializations[spec] = 0
            specializations[spec] += 1

        return {
            'colony_size': len(self.agents),
            'total_balance': total_balance,
            'total_earned': total_earned,
            'total_spent': total_spent,
            'overall_roi': overall_roi,
            'total_conversions': total_conversions,
            'total_reproductions': len(self.reproduction_history),
            'generations': generations,
            'specializations': specializations,
            'agents': [
                {
                    'agent_id': agent_id,
                    'balance': agent.commission_balance,
                    'total_earned': agent.total_earned,
                    'roi': agent.total_earned / agent.total_spent if agent.total_spent > 0 else 0,
                    'specialization': self.genealogy[agent_id].specialization.value,
                    'generation': self.genealogy[agent_id].generation,
                    'children_count': len(self.genealogy[agent_id].children)
                }
                for agent_id, agent in self.agents.items()
            ]
        }

    def get_family_tree(self) -> dict:
        """Get the full family tree structure"""
        tree = {}

        for agent_id, genealogy in self.genealogy.items():
            tree[agent_id] = {
                'parent_id': genealogy.parent_id,
                'generation': genealogy.generation,
                'specialization': genealogy.specialization.value,
                'birth_date': genealogy.birth_date.isoformat(),
                'children': genealogy.children,
                'balance': self.agents[agent_id].commission_balance,
                'total_earned': self.agents[agent_id].total_earned
            }

        return tree

    def record_agent_action(self, agent_id: str, revenue: float = 0.0,
                           spent: float = 0.0, conversions: int = 0, actions: int = 1):
        """
        Record agent activity for competition tracking.
        Call this whenever an agent takes an action.

        Args:
            agent_id: Agent ID
            revenue: Commission earned from this action
            spent: Cost of this action
            conversions: Number of conversions (usually 0 or 1)
            actions: Number of actions taken (default 1)
        """
        if agent_id not in self.agents:
            logger.warning(f"Cannot record action for unknown agent '{agent_id}'")
            return

        # Record in competition system
        self.competition.record_agent_activity(
            agent_id=agent_id,
            revenue=revenue,
            spent=spent,
            conversions=conversions,
            actions=actions
        )

        logger.debug(f"Recorded action for {agent_id}: ${revenue:.2f} revenue, ${spent:.2f} spent")

    def get_agent_commission_rate(self, agent_id: str, base_rate: float = 0.10) -> float:
        """
        Get commission rate for agent including performance multiplier.

        Returns:
            float: Commission rate (e.g., 0.15 for Elite tier, 0.08 for Learner)
        """
        return self.competition.get_commission_rate(agent_id, base_rate)

    def run_weekly_competition(self):
        """Run weekly competition and return results"""
        result = self.competition.run_weekly_competition()
        logger.info(f"Weekly competition complete! Winner: {result.winner_id}")
        return result

    def run_monthly_competition(self):
        """Run monthly competition and return results"""
        result = self.competition.run_monthly_competition()
        logger.info(f"Monthly competition complete! Winner: {result.winner_id}")
        return result

    def get_leaderboard(self, limit: int = 10):
        """Get current competition leaderboard"""
        return self.competition.get_leaderboard(limit=limit)

    def save_colony_state(self, directory: str = 'data'):
        """Save all colony data to files"""
        os.makedirs(directory, exist_ok=True)

        # Save each agent's state
        for agent_id, agent in self.agents.items():
            filepath = f"{directory}/{agent_id}_state.json"
            agent.save_state(filepath)

        # Save genealogy
        genealogy_data = {
            agent_id: gen.to_dict()
            for agent_id, gen in self.genealogy.items()
        }

        with open(f"{directory}/genealogy.json", 'w') as f:
            json.dump(genealogy_data, f, indent=2)

        # Save reproduction history
        with open(f"{directory}/reproduction_history.json", 'w') as f:
            json.dump(self.reproduction_history, f, indent=2)

        # Save competition state
        self.competition.save_state(f"{directory}/competition_state.json")

        logger.info(f"Colony state saved to {directory}/")

    @staticmethod
    def load_colony_state(directory: str = 'data', colony_id: str = "main") -> 'AgentColony':
        """Load colony from saved files"""
        colony = AgentColony(colony_id=colony_id)

        # Load genealogy first
        with open(f"{directory}/genealogy.json", 'r') as f:
            genealogy_data = json.load(f)

        colony.genealogy = {
            agent_id: AgentGenealogy.from_dict(data)
            for agent_id, data in genealogy_data.items()
        }

        # Load each agent
        for agent_id in colony.genealogy.keys():
            filepath = f"{directory}/{agent_id}_state.json"
            if os.path.exists(filepath):
                agent = BloomAIAgent.load_state(filepath)
                colony.agents[agent_id] = agent

        # Load reproduction history
        history_path = f"{directory}/reproduction_history.json"
        if os.path.exists(history_path):
            with open(history_path, 'r') as f:
                colony.reproduction_history = json.load(f)

        # Load competition state
        competition_path = f"{directory}/competition_state.json"
        if os.path.exists(competition_path):
            colony.competition = AgentCompetition.load_state(competition_path)
            logger.info("Competition state loaded")

        logger.info(f"Colony loaded from {directory}/ - {len(colony.agents)} agents")

        return colony
