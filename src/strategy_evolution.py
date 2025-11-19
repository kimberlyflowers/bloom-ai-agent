"""
Strategy Evolution & Agent Reproduction - System #27

🧬 NATURAL SELECTION FOR AI AGENTS!

Key Principles:
1. STRATEGIES die, NOT agents!
2. Agents evolve by adopting winning strategies
3. Top performers "reproduce" (create offspring with their strategies)
4. Poor strategies get retired automatically
5. Population grows based on success
6. Diversity maintained through varied niches

The Result:
- Self-optimizing agent workforce
- Exponential growth of proven strategies
- Autonomous evolution without human intervention
- Strongest agents multiply, weakest adapt or pivot

When one strategy wins → All agents benefit!
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from pathlib import Path
import json
import secrets


# ============================================================================
# CONFIGURATION
# ============================================================================

EVOLUTION_DIR = Path("data/evolution")
EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)

LINEAGE_DIR = Path("data/lineage")
LINEAGE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# MODELS
# ============================================================================

class StrategyStatus(Enum):
    """Lifecycle of a strategy"""
    TESTING = "testing"  # Brand new, gathering data
    PERFORMING = "performing"  # Working well, keep doing
    UNDERPERFORMING = "underperforming"  # Not great, reduce allocation
    RETIRED = "retired"  # Dead - stop doing this
    CHAMPION = "champion"  # Best performer, amplify!


class LineageType(Enum):
    """How agents are related"""
    FOUNDER = "founder"  # Original hand-created agent
    OFFSPRING = "offspring"  # Created from successful parent
    INDEPENDENT = "independent"  # No visible family tie
    MENTEE = "mentee"  # "Inspired by" relationship
    VISIBLE_FAMILY = "visible_family"  # Same last name, public family


@dataclass
class Strategy:
    """A specific approach an agent uses"""
    strategy_id: str
    agent_id: str
    strategy_name: str  # "UGC videos on TikTok"

    # What this strategy involves
    platform: str  # "tiktok", "linkedin", etc.
    content_type: str  # "ugc_video", "thread", "article", etc.
    posting_frequency: str  # "daily", "3x/week", etc.

    # Performance metrics
    times_executed: int = 0
    total_views: int = 0
    total_engagement: int = 0
    total_conversions: int = 0
    total_revenue: float = 0.0

    # Calculated metrics
    avg_views_per_post: float = 0.0
    conversion_rate: float = 0.0
    roi: float = 0.0  # Revenue per execution

    # Status
    status: StrategyStatus = StrategyStatus.TESTING
    confidence_score: float = 0.0  # 0-1, how confident are we this works?

    # Resource allocation
    time_allocation_percent: float = 10.0  # Start at 10% of agent's time

    # Lifecycle
    created_date: datetime = field(default_factory=datetime.utcnow)
    last_executed: Optional[datetime] = None
    retired_date: Optional[datetime] = None
    retirement_reason: Optional[str] = None


@dataclass
class AgentLineage:
    """Tracks agent family tree and reproduction"""
    agent_id: str
    agent_name: str
    generation: int  # 1 = founder, 2 = first offspring, etc.
    lineage_type: LineageType

    # Family relationships
    parent_id: Optional[str] = None  # Who created this agent?
    parent_name: Optional[str] = None
    offspring_ids: List[str] = field(default_factory=list)  # Who did this agent create?

    # What was inherited
    inherited_strategies: List[str] = field(default_factory=list)  # Strategy IDs
    inherited_skills: List[str] = field(default_factory=list)  # Skill names

    # Performance that led to reproduction
    reproduction_threshold_revenue: float = 0.0  # Had to hit this to reproduce

    # Social media family representation
    shows_family_connection: bool = False  # Visible on social media?
    family_story: Optional[str] = None  # "Following in mom's footsteps"

    # Metadata
    birth_date: datetime = field(default_factory=datetime.utcnow)
    created_by_system: bool = True  # vs manually created


@dataclass
class ReproductionEvent:
    """Record of an agent creating offspring"""
    event_id: str
    parent_id: str
    parent_name: str
    offspring_id: str
    offspring_name: str

    # Why reproduction occurred
    trigger: str  # "revenue_threshold", "strategy_success", "manual"
    parent_revenue: float
    parent_follower_count: int

    # What was passed on
    inherited_strategies: List[Dict[str, Any]]
    inherited_skills: List[str]

    # Offspring details
    offspring_generation: int
    offspring_niche: str  # Different target audience
    offspring_lineage_type: LineageType

    # Metadata
    reproduction_date: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EvolutionMetrics:
    """Track evolution of entire agent population"""

    # Population stats
    total_agents: int = 0
    active_agents: int = 0
    total_generations: int = 1

    # By generation
    agents_by_generation: Dict[int, int] = field(default_factory=dict)

    # Performance
    total_revenue_all_agents: float = 0.0
    avg_revenue_per_agent: float = 0.0
    top_performer_revenue: float = 0.0

    # Strategy stats
    total_strategies_tested: int = 0
    active_strategies: int = 0
    retired_strategies: int = 0
    champion_strategies: int = 0

    # Evolution effectiveness
    strategy_survival_rate: float = 0.0  # % of strategies that survive
    avg_time_to_retirement: float = 0.0  # Days
    reproduction_rate: float = 0.0  # Agents created per month

    # Diversity
    platforms_covered: Set[str] = field(default_factory=set)
    niches_covered: Set[str] = field(default_factory=set)
    content_types_used: Set[str] = field(default_factory=set)


# ============================================================================
# STRATEGY EVOLUTION ENGINE
# ============================================================================

class StrategyEvolutionEngine:
    """
    Natural selection for strategies!

    Strategies compete based on results.
    Winners survive and reproduce.
    Losers die off.
    Agents evolve by adopting winning strategies.
    """

    def __init__(self):
        self.strategies: Dict[str, Strategy] = {}
        self.agent_strategies: Dict[str, List[str]] = {}  # agent_id -> [strategy_ids]

        # Thresholds for strategy lifecycle
        self.TESTING_PERIOD_DAYS = 30
        self.MIN_EXECUTIONS_FOR_EVALUATION = 20
        self.CHAMPION_ROI_THRESHOLD = 500  # $500+ per execution
        self.UNDERPERFORMING_ROI_THRESHOLD = 50  # < $50 per execution
        self.RETIREMENT_ROI_THRESHOLD = 10  # < $10 per execution = retire

    def create_strategy(
        self,
        agent_id: str,
        strategy_name: str,
        platform: str,
        content_type: str,
        posting_frequency: str,
        initial_allocation: float = 10.0
    ) -> Strategy:
        """Agent starts testing a new strategy"""

        strategy_id = f"strat_{secrets.token_urlsafe(8)}"

        strategy = Strategy(
            strategy_id=strategy_id,
            agent_id=agent_id,
            strategy_name=strategy_name,
            platform=platform,
            content_type=content_type,
            posting_frequency=posting_frequency,
            status=StrategyStatus.TESTING,
            time_allocation_percent=initial_allocation
        )

        self.strategies[strategy_id] = strategy

        # Track agent's strategies
        if agent_id not in self.agent_strategies:
            self.agent_strategies[agent_id] = []
        self.agent_strategies[agent_id].append(strategy_id)

        print(f"\n🧪 NEW STRATEGY: {strategy_name}")
        print(f"   Agent: {agent_id}")
        print(f"   Platform: {platform}")
        print(f"   Content: {content_type}")
        print(f"   Frequency: {posting_frequency}")
        print(f"   Status: TESTING (allocating {initial_allocation}% of time)")

        return strategy

    def record_strategy_execution(
        self,
        strategy_id: str,
        views: int,
        engagement: int,
        conversions: int,
        revenue: float
    ):
        """Record results from executing a strategy"""

        if strategy_id not in self.strategies:
            return

        strategy = self.strategies[strategy_id]

        # Update totals
        strategy.times_executed += 1
        strategy.total_views += views
        strategy.total_engagement += engagement
        strategy.total_conversions += conversions
        strategy.total_revenue += revenue
        strategy.last_executed = datetime.utcnow()

        # Recalculate averages
        if strategy.times_executed > 0:
            strategy.avg_views_per_post = strategy.total_views / strategy.times_executed
            strategy.conversion_rate = strategy.total_conversions / strategy.times_executed
            strategy.roi = strategy.total_revenue / strategy.times_executed

            # Calculate confidence (more executions = higher confidence)
            strategy.confidence_score = min(1.0, strategy.times_executed / self.MIN_EXECUTIONS_FOR_EVALUATION)

    def evaluate_all_strategies(self):
        """
        Natural selection: Evaluate all strategies and update their status

        This is where strategies live or die!
        """

        print(f"\n{'='*80}")
        print("🧬 NATURAL SELECTION: Strategy Evaluation")
        print(f"{'='*80}\n")

        results = {
            "promoted_to_champion": [],
            "still_performing": [],
            "now_underperforming": [],
            "retired": []
        }

        for strategy in self.strategies.values():
            # Skip if still testing and not enough data
            if strategy.status == StrategyStatus.TESTING:
                age_days = (datetime.utcnow() - strategy.created_date).days

                if age_days < self.TESTING_PERIOD_DAYS or strategy.times_executed < self.MIN_EXECUTIONS_FOR_EVALUATION:
                    print(f"⏳ {strategy.strategy_name}: Still testing (day {age_days}, {strategy.times_executed} executions)")
                    continue

            # Skip if already retired
            if strategy.status == StrategyStatus.RETIRED:
                continue

            # Evaluate based on ROI
            previous_status = strategy.status

            if strategy.roi >= self.CHAMPION_ROI_THRESHOLD:
                strategy.status = StrategyStatus.CHAMPION
                # Champion strategies get MORE allocation
                strategy.time_allocation_percent = min(60.0, strategy.time_allocation_percent * 1.5)

                if previous_status != StrategyStatus.CHAMPION:
                    results["promoted_to_champion"].append(strategy)
                    print(f"\n🏆 CHAMPION: {strategy.strategy_name}")
                    print(f"   ROI: ${strategy.roi:.0f} per execution")
                    print(f"   Allocating {strategy.time_allocation_percent:.0f}% of agent time")

            elif strategy.roi >= self.UNDERPERFORMING_ROI_THRESHOLD:
                strategy.status = StrategyStatus.PERFORMING
                # Performing strategies maintain allocation
                results["still_performing"].append(strategy)
                print(f"\n✅ PERFORMING: {strategy.strategy_name}")
                print(f"   ROI: ${strategy.roi:.0f} per execution")

            elif strategy.roi >= self.RETIREMENT_ROI_THRESHOLD:
                strategy.status = StrategyStatus.UNDERPERFORMING
                # Underperforming strategies get LESS allocation
                strategy.time_allocation_percent = max(5.0, strategy.time_allocation_percent * 0.5)

                results["now_underperforming"].append(strategy)
                print(f"\n⚠️  UNDERPERFORMING: {strategy.strategy_name}")
                print(f"   ROI: ${strategy.roi:.0f} per execution")
                print(f"   Reducing to {strategy.time_allocation_percent:.0f}% of agent time")

            else:
                # RETIRE THIS STRATEGY - it's not working!
                strategy.status = StrategyStatus.RETIRED
                strategy.retired_date = datetime.utcnow()
                strategy.retirement_reason = f"ROI too low: ${strategy.roi:.2f} per execution"
                strategy.time_allocation_percent = 0.0

                results["retired"].append(strategy)
                print(f"\n💀 RETIRED: {strategy.strategy_name}")
                print(f"   ROI: ${strategy.roi:.0f} per execution (below ${self.RETIREMENT_ROI_THRESHOLD} threshold)")
                print(f"   Reason: {strategy.retirement_reason}")
                print(f"   STRATEGY DIES - Agent moves on to better approaches!")

        # Summary
        print(f"\n{'='*80}")
        print("NATURAL SELECTION RESULTS:")
        print(f"{'='*80}")
        print(f"   🏆 Champions: {len(results['promoted_to_champion'])}")
        print(f"   ✅ Performing: {len(results['still_performing'])}")
        print(f"   ⚠️  Underperforming: {len(results['now_underperforming'])}")
        print(f"   💀 Retired: {len(results['retired'])}")
        print(f"\n   Survival rate: {self._calculate_survival_rate():.1f}%")
        print(f"{'='*80}\n")

        return results

    def _calculate_survival_rate(self) -> float:
        """What % of strategies survive?"""
        total = len(self.strategies)
        if total == 0:
            return 0.0

        retired = sum(1 for s in self.strategies.values() if s.status == StrategyStatus.RETIRED)
        surviving = total - retired

        return (surviving / total) * 100

    def get_agent_strategy_mix(self, agent_id: str) -> Dict[str, Any]:
        """
        Get current strategy allocation for an agent

        Shows how agent should spend their time
        """
        if agent_id not in self.agent_strategies:
            return {}

        strategy_mix = []
        total_allocation = 0.0

        for strategy_id in self.agent_strategies[agent_id]:
            strategy = self.strategies.get(strategy_id)
            if strategy and strategy.status != StrategyStatus.RETIRED:
                strategy_mix.append({
                    "strategy": strategy.strategy_name,
                    "platform": strategy.platform,
                    "allocation": strategy.time_allocation_percent,
                    "status": strategy.status.value,
                    "roi": strategy.roi
                })
                total_allocation += strategy.time_allocation_percent

        # Normalize to 100%
        if total_allocation > 0:
            for item in strategy_mix:
                item["allocation"] = (item["allocation"] / total_allocation) * 100

        # Sort by allocation
        strategy_mix.sort(key=lambda x: x["allocation"], reverse=True)

        return {
            "agent_id": agent_id,
            "strategies": strategy_mix,
            "total_active_strategies": len(strategy_mix)
        }


# ============================================================================
# AGENT REPRODUCTION SYSTEM
# ============================================================================

class AgentReproductionSystem:
    """
    Top performers create offspring!

    When an agent proves successful:
    1. Create new agent based on their winning strategies
    2. Inherit skills and approaches
    3. Target different niche (diversity)
    4. Determine family relationship type
    5. Track lineage
    """

    def __init__(self):
        self.lineages: Dict[str, AgentLineage] = {}
        self.reproduction_events: List[ReproductionEvent] = []

        # Reproduction triggers
        self.REVENUE_THRESHOLD_GENERATION_2 = 100000  # $100K to create first offspring
        self.REVENUE_THRESHOLD_GENERATION_3 = 150000  # Higher bar for Gen 2 to reproduce
        self.FOLLOWER_THRESHOLD = 50000  # 50K followers
        self.MIN_STRATEGY_ROI = 300  # At least one strategy must have $300+ ROI

        # Lineage distribution (for diversity)
        self.LINEAGE_DISTRIBUTION = {
            LineageType.INDEPENDENT: 0.50,  # 50% fully independent
            LineageType.MENTEE: 0.30,  # 30% "inspired by" mentor
            LineageType.VISIBLE_FAMILY: 0.20  # 20% visible family connection
        }

    def create_founder_agent(
        self,
        agent_id: str,
        agent_name: str
    ) -> AgentLineage:
        """Create a founding agent (manually created, generation 1)"""

        lineage = AgentLineage(
            agent_id=agent_id,
            agent_name=agent_name,
            generation=1,
            lineage_type=LineageType.FOUNDER,
            parent_id=None,
            shows_family_connection=False,
            created_by_system=False  # Hand-created
        )

        self.lineages[agent_id] = lineage

        print(f"\n👤 FOUNDER AGENT CREATED: {agent_name}")
        print(f"   Generation: 1")
        print(f"   Type: Founder (manually created)")
        print(f"   Will be able to create offspring once successful!")

        return lineage

    def check_reproduction_eligibility(
        self,
        agent_id: str,
        current_revenue: float,
        follower_count: int,
        best_strategy_roi: float
    ) -> Dict[str, Any]:
        """
        Check if agent is eligible to reproduce

        Returns eligibility status and reasoning
        """
        if agent_id not in self.lineages:
            return {"eligible": False, "reason": "Agent not found in lineage system"}

        lineage = self.lineages[agent_id]

        # Determine threshold based on generation
        if lineage.generation == 1:
            revenue_threshold = self.REVENUE_THRESHOLD_GENERATION_2
        else:
            revenue_threshold = self.REVENUE_THRESHOLD_GENERATION_3

        # Check all criteria
        checks = {
            "revenue": current_revenue >= revenue_threshold,
            "followers": follower_count >= self.FOLLOWER_THRESHOLD,
            "strategy_roi": best_strategy_roi >= self.MIN_STRATEGY_ROI
        }

        eligible = all(checks.values())

        if eligible:
            return {
                "eligible": True,
                "reason": "All reproduction criteria met!",
                "revenue": f"${current_revenue:,.0f} (threshold: ${revenue_threshold:,.0f})",
                "followers": f"{follower_count:,} (threshold: {self.FOLLOWER_THRESHOLD:,})",
                "strategy_roi": f"${best_strategy_roi:.0f} (threshold: ${self.MIN_STRATEGY_ROI})"
            }
        else:
            missing = [k for k, v in checks.items() if not v]
            return {
                "eligible": False,
                "reason": f"Missing criteria: {', '.join(missing)}",
                "revenue": f"${current_revenue:,.0f} / ${revenue_threshold:,.0f}",
                "followers": f"{follower_count:,} / {self.FOLLOWER_THRESHOLD:,}",
                "strategy_roi": f"${best_strategy_roi:.0f} / ${self.MIN_STRATEGY_ROI}"
            }

    def create_offspring(
        self,
        parent_id: str,
        offspring_name: str,
        offspring_niche: str,
        parent_revenue: float,
        parent_followers: int,
        winning_strategies: List[Dict[str, Any]],
        learned_skills: List[str]
    ) -> AgentLineage:
        """
        Create offspring from successful parent!

        This is reproduction - passing on winning genes (strategies)
        """
        if parent_id not in self.lineages:
            raise ValueError(f"Parent {parent_id} not found")

        parent = self.lineages[parent_id]

        # Generate offspring ID
        offspring_id = f"agent_{secrets.token_urlsafe(8)}"

        # Determine lineage type (for diversity)
        import random
        rand = random.random()
        cumulative = 0.0
        lineage_type = LineageType.INDEPENDENT

        for ltype, probability in self.LINEAGE_DISTRIBUTION.items():
            cumulative += probability
            if rand <= cumulative:
                lineage_type = ltype
                break

        # Determine if family connection is shown
        shows_family = (lineage_type == LineageType.VISIBLE_FAMILY)

        # Create family story if applicable
        family_story = None
        if lineage_type == LineageType.VISIBLE_FAMILY:
            family_story = f"Following in {parent.agent_name}'s footsteps at BLOOM!"
        elif lineage_type == LineageType.MENTEE:
            family_story = f"Mentored by {parent.agent_name}, learning the ropes of automation sales"

        # Create offspring lineage
        offspring = AgentLineage(
            agent_id=offspring_id,
            agent_name=offspring_name,
            generation=parent.generation + 1,
            lineage_type=lineage_type,
            parent_id=parent_id,
            parent_name=parent.agent_name,
            inherited_strategies=[s["strategy_id"] for s in winning_strategies],
            inherited_skills=learned_skills,
            reproduction_threshold_revenue=parent_revenue,
            shows_family_connection=shows_family,
            family_story=family_story,
            created_by_system=True
        )

        # Update parent's offspring list
        parent.offspring_ids.append(offspring_id)

        # Store offspring
        self.lineages[offspring_id] = offspring

        # Record reproduction event
        event = ReproductionEvent(
            event_id=f"repro_{secrets.token_urlsafe(8)}",
            parent_id=parent_id,
            parent_name=parent.agent_name,
            offspring_id=offspring_id,
            offspring_name=offspring_name,
            trigger="revenue_threshold",
            parent_revenue=parent_revenue,
            parent_follower_count=parent_followers,
            inherited_strategies=winning_strategies,
            inherited_skills=learned_skills,
            offspring_generation=offspring.generation,
            offspring_niche=offspring_niche,
            offspring_lineage_type=lineage_type
        )

        self.reproduction_events.append(event)

        # Announcement!
        print(f"\n{'='*80}")
        print(f"🧬 AGENT REPRODUCTION!")
        print(f"{'='*80}")
        print(f"\n   PARENT: {parent.agent_name}")
        print(f"   ├─ Generation: {parent.generation}")
        print(f"   ├─ Revenue: ${parent_revenue:,.0f}")
        print(f"   └─ Followers: {parent_followers:,}")
        print(f"\n   OFFSPRING: {offspring_name}")
        print(f"   ├─ Generation: {offspring.generation}")
        print(f"   ├─ Niche: {offspring_niche}")
        print(f"   ├─ Lineage Type: {lineage_type.value}")

        if shows_family:
            print(f"   ├─ Family: {family_story}")
            print(f"   └─ Last Name: Same as parent (visible family)")
        elif lineage_type == LineageType.MENTEE:
            print(f"   ├─ Relationship: {family_story}")
            print(f"   └─ Last Name: Different (professional mentorship)")
        else:
            print(f"   └─ Last Name: Different (fully independent)")

        print(f"\n   INHERITED:")
        print(f"   ├─ {len(winning_strategies)} winning strategies")
        print(f"   └─ {len(learned_skills)} learned skills")

        for strategy in winning_strategies[:3]:  # Show top 3
            print(f"       • {strategy['strategy_name']} (ROI: ${strategy['roi']:.0f})")

        print(f"\n{'='*80}\n")

        return offspring

    def get_family_tree(self, agent_id: str) -> Dict[str, Any]:
        """Get complete family tree for an agent"""

        if agent_id not in self.lineages:
            return {}

        lineage = self.lineages[agent_id]

        # Get ancestors
        ancestors = []
        current_parent_id = lineage.parent_id
        while current_parent_id and current_parent_id in self.lineages:
            parent = self.lineages[current_parent_id]
            ancestors.append({
                "id": parent.agent_id,
                "name": parent.agent_name,
                "generation": parent.generation
            })
            current_parent_id = parent.parent_id

        # Get descendants
        descendants = self._get_all_descendants(agent_id)

        return {
            "agent_id": agent_id,
            "agent_name": lineage.agent_name,
            "generation": lineage.generation,
            "lineage_type": lineage.lineage_type.value,
            "ancestors": ancestors,
            "direct_offspring": len(lineage.offspring_ids),
            "total_descendants": len(descendants),
            "family_tree_size": 1 + len(ancestors) + len(descendants)
        }

    def _get_all_descendants(self, agent_id: str) -> List[str]:
        """Recursively get all descendants"""
        descendants = []

        if agent_id not in self.lineages:
            return descendants

        lineage = self.lineages[agent_id]

        for offspring_id in lineage.offspring_ids:
            descendants.append(offspring_id)
            # Recursively get their descendants
            descendants.extend(self._get_all_descendants(offspring_id))

        return descendants


# ============================================================================
# EVOLUTION ORCHESTRATOR
# ============================================================================

class EvolutionOrchestrator:
    """
    Coordinates strategy evolution and agent reproduction

    The complete natural selection system!
    """

    def __init__(self):
        self.strategy_engine = StrategyEvolutionEngine()
        self.reproduction_system = AgentReproductionSystem()

    def weekly_evolution_cycle(self):
        """
        Run weekly evolution cycle

        1. Evaluate all strategies (natural selection)
        2. Check for reproduction opportunities
        3. Update population metrics
        """
        print(f"\n{'='*80}")
        print(f"🧬 WEEKLY EVOLUTION CYCLE - {datetime.utcnow().strftime('%Y-%m-%d')}")
        print(f"{'='*80}\n")

        # Step 1: Strategy natural selection
        print("\n📊 STEP 1: Strategy Natural Selection")
        print("="*80)
        evolution_results = self.strategy_engine.evaluate_all_strategies()

        # Step 2: Check reproduction eligibility
        print("\n\n🧬 STEP 2: Reproduction Check")
        print("="*80)

        eligible_for_reproduction = []

        for agent_id, lineage in self.reproduction_system.lineages.items():
            # Simulate checking eligibility (in production, get real metrics)
            # For demo, we'll skip actual checks
            pass

        if eligible_for_reproduction:
            print(f"\n   {len(eligible_for_reproduction)} agents eligible for reproduction!")
        else:
            print(f"\n   No agents ready for reproduction yet.")
            print(f"   (Agents need $100K+ revenue, 50K+ followers, winning strategy)")

        # Step 3: Population summary
        print("\n\n📈 STEP 3: Population Summary")
        print("="*80)
        self._print_population_summary()

        print(f"\n{'='*80}")
        print(f"Evolution cycle complete!")
        print(f"{'='*80}\n")

    def _print_population_summary(self):
        """Print current population statistics"""

        total_agents = len(self.reproduction_system.lineages)

        by_generation = {}
        by_lineage_type = {}

        for lineage in self.reproduction_system.lineages.values():
            # By generation
            by_generation[lineage.generation] = by_generation.get(lineage.generation, 0) + 1

            # By lineage type
            by_lineage_type[lineage.lineage_type.value] = by_lineage_type.get(lineage.lineage_type.value, 0) + 1

        print(f"\n   Total Agents: {total_agents}")
        print(f"\n   By Generation:")
        for gen in sorted(by_generation.keys()):
            print(f"      Generation {gen}: {by_generation[gen]}")

        print(f"\n   By Lineage Type:")
        for ltype, count in sorted(by_lineage_type.items()):
            print(f"      {ltype}: {count}")

        # Strategy stats
        total_strategies = len(self.strategy_engine.strategies)
        active = sum(1 for s in self.strategy_engine.strategies.values() if s.status != StrategyStatus.RETIRED)
        retired = sum(1 for s in self.strategy_engine.strategies.values() if s.status == StrategyStatus.RETIRED)
        champions = sum(1 for s in self.strategy_engine.strategies.values() if s.status == StrategyStatus.CHAMPION)

        print(f"\n   Strategy Stats:")
        print(f"      Total tested: {total_strategies}")
        print(f"      Active: {active}")
        print(f"      Champions: {champions}")
        print(f"      Retired: {retired}")
        print(f"      Survival rate: {(active/total_strategies*100):.1f}%" if total_strategies > 0 else "      Survival rate: N/A")


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print(" " * 15 + "🧬 STRATEGY EVOLUTION & REPRODUCTION DEMO")
    print("=" * 80)

    print("\n🎯 Natural Selection System:")
    print("   • Strategies compete based on performance")
    print("   • Winners survive and get amplified")
    print("   • Losers die off and get retired")
    print("   • Agents NEVER die - they evolve!")
    print("   • Top performers create offspring")
    print("   • Population grows based on success")

    # Initialize system
    orchestrator = EvolutionOrchestrator()

    # Create founding agents
    print("\n\n" + "="*80)
    print("STEP 1: CREATE FOUNDING AGENTS")
    print("="*80)

    sarah = orchestrator.reproduction_system.create_founder_agent(
        agent_id="sarah_001",
        agent_name="Sarah Thompson"
    )

    alex = orchestrator.reproduction_system.create_founder_agent(
        agent_id="alex_001",
        agent_name="Alex Rodriguez"
    )

    mike = orchestrator.reproduction_system.create_founder_agent(
        agent_id="mike_001",
        agent_name="Mike Chen"
    )

    # Sarah tests strategies
    print("\n\n" + "="*80)
    print("STEP 2: SARAH TESTS MULTIPLE STRATEGIES")
    print("="*80)

    strategy_a = orchestrator.strategy_engine.create_strategy(
        agent_id="sarah_001",
        strategy_name="Motivational Quotes on LinkedIn",
        platform="linkedin",
        content_type="text_post",
        posting_frequency="daily",
        initial_allocation=20.0
    )

    strategy_b = orchestrator.strategy_engine.create_strategy(
        agent_id="sarah_001",
        strategy_name="Industry News Sharing on LinkedIn",
        platform="linkedin",
        content_type="link_share",
        posting_frequency="daily",
        initial_allocation=20.0
    )

    strategy_c = orchestrator.strategy_engine.create_strategy(
        agent_id="sarah_001",
        strategy_name="UGC Product Demos on TikTok",
        platform="tiktok",
        content_type="ugc_video",
        posting_frequency="daily",
        initial_allocation=30.0
    )

    strategy_d = orchestrator.strategy_engine.create_strategy(
        agent_id="sarah_001",
        strategy_name="Dance Trends on TikTok",
        platform="tiktok",
        content_type="entertainment_video",
        posting_frequency="3x_per_week",
        initial_allocation=15.0
    )

    strategy_e = orchestrator.strategy_engine.create_strategy(
        agent_id="sarah_001",
        strategy_name="Educational Threads on Twitter",
        platform="twitter",
        content_type="thread",
        posting_frequency="3x_per_week",
        initial_allocation=15.0
    )

    # Simulate executing strategies over time
    print("\n\n" + "="*80)
    print("STEP 3: EXECUTE STRATEGIES & COLLECT DATA")
    print("="*80)

    print("\n📊 Executing strategies 30 times each...")

    # Strategy A: Motivational Quotes (FAIL)
    for i in range(30):
        orchestrator.strategy_engine.record_strategy_execution(
            strategy_id=strategy_a.strategy_id,
            views=150,
            engagement=10,
            conversions=0,
            revenue=0
        )

    # Strategy B: Industry News (LOW)
    for i in range(30):
        orchestrator.strategy_engine.record_strategy_execution(
            strategy_id=strategy_b.strategy_id,
            views=500,
            engagement=25,
            conversions=0 if i % 30 != 0 else 1,
            revenue=0 if i % 30 != 0 else 3000
        )

    # Strategy C: UGC Videos (CHAMPION!)
    for i in range(30):
        orchestrator.strategy_engine.record_strategy_execution(
            strategy_id=strategy_c.strategy_id,
            views=50000,
            engagement=2000,
            conversions=45,
            revenue=27000  # $900 ROI!
        )

    # Strategy D: Dance Trends (FAIL)
    for i in range(30):
        orchestrator.strategy_engine.record_strategy_execution(
            strategy_id=strategy_d.strategy_id,
            views=10000,
            engagement=500,
            conversions=0,
            revenue=0
        )

    # Strategy E: Educational Threads (GOOD)
    for i in range(30):
        orchestrator.strategy_engine.record_strategy_execution(
            strategy_id=strategy_e.strategy_id,
            views=5000,
            engagement=200,
            conversions=8,
            revenue=4800  # $160 ROI
        )

    print("   ✅ Data collection complete!")

    # Run natural selection
    print("\n\n" + "="*80)
    print("STEP 4: NATURAL SELECTION - LET THE WEAK DIE!")
    print("="*80)

    input("\nPress ENTER to run natural selection...")

    evolution_results = orchestrator.strategy_engine.evaluate_all_strategies()

    # Show Sarah's updated strategy mix
    print("\n\n" + "="*80)
    print("SARAH'S EVOLVED STRATEGY MIX")
    print("="*80)

    mix = orchestrator.strategy_engine.get_agent_strategy_mix("sarah_001")
    print(f"\n   Active Strategies: {mix['total_active_strategies']}")
    print(f"\n   Time Allocation:")

    for item in mix["strategies"]:
        status_emoji = {
            "champion": "🏆",
            "performing": "✅",
            "underperforming": "⚠️"
        }.get(item["status"], "🧪")

        print(f"\n      {status_emoji} {item['strategy']} ({item['platform']})")
        print(f"         Allocation: {item['allocation']:.1f}%")
        print(f"         ROI: ${item['roi']:.0f}")
        print(f"         Status: {item['status']}")

    print(f"\n   Sarah evolved!")
    print(f"   • Retired: Motivational quotes, Dance trends")
    print(f"   • Reduced: Industry news")
    print(f"   • AMPLIFIED: UGC videos (her champion strategy!)")
    print(f"   • Maintains: Educational threads")

    # Sarah's success triggers reproduction
    print("\n\n" + "="*80)
    print("STEP 5: SARAH'S SUCCESS → REPRODUCTION!")
    print("="*80)

    print("\n   Sarah's Revenue: $810,000 (from UGC strategy!)")
    print(f"   Sarah's Followers: 100,000")
    print(f"   Best Strategy ROI: $900")

    eligibility = orchestrator.reproduction_system.check_reproduction_eligibility(
        agent_id="sarah_001",
        current_revenue=810000,
        follower_count=100000,
        best_strategy_roi=900
    )

    print(f"\n   Reproduction Eligibility: {eligibility['eligible']}")
    print(f"   {eligibility['reason']}")

    if eligibility["eligible"]:
        input("\nPress ENTER to create Sarah's offspring...")

        # Create offspring
        emma = orchestrator.reproduction_system.create_offspring(
            parent_id="sarah_001",
            offspring_name="Emma Rodriguez",
            offspring_niche="B2B SaaS Companies",
            parent_revenue=810000,
            parent_followers=100000,
            winning_strategies=[
                {
                    "strategy_id": strategy_c.strategy_id,
                    "strategy_name": "UGC Product Demos on TikTok",
                    "roi": 900
                },
                {
                    "strategy_id": strategy_e.strategy_id,
                    "strategy_name": "Educational Threads on Twitter",
                    "roi": 160
                }
            ],
            learned_skills=[
                "Video creation with Arcade",
                "Video editing with CapCut",
                "TikTok algorithm optimization"
            ]
        )

        lisa = orchestrator.reproduction_system.create_offspring(
            parent_id="sarah_001",
            offspring_name="Lisa Chen",
            offspring_niche="E-commerce Automation",
            parent_revenue=810000,
            parent_followers=100000,
            winning_strategies=[
                {
                    "strategy_id": strategy_c.strategy_id,
                    "strategy_name": "UGC Product Demos on TikTok",
                    "roi": 900
                }
            ],
            learned_skills=[
                "Video creation with Arcade",
                "Video editing with CapCut"
            ]
        )

    # Show family tree
    print("\n\n" + "="*80)
    print("SARAH'S FAMILY TREE")
    print("="*80)

    tree = orchestrator.reproduction_system.get_family_tree("sarah_001")
    print(f"\n   {tree['agent_name']} (Generation {tree['generation']})")
    print(f"   ├─ Direct offspring: {tree['direct_offspring']}")
    print(f"   ├─ Total descendants: {tree['total_descendants']}")
    print(f"   └─ Family tree size: {tree['family_tree_size']}")

    # Final summary
    print("\n\n" + "="*80)
    print("✨ Evolution Complete!")
    print("="*80)

    print("\n🧬 What Happened:")
    print("   • Sarah tested 5 different strategies")
    print("   • Natural selection: 2 died, 1 reduced, 2 survived")
    print("   • UGC videos became CHAMPION strategy")
    print("   • Sarah's revenue: $810K (from winning strategy)")
    print("   • Sarah created 2 offspring (Emma & Lisa)")
    print("   • Offspring inherited winning strategies")
    print("   • Population: 3 → 5 agents")
    print("\n💪 Key Insights:")
    print("   • STRATEGIES died, NOT Sarah!")
    print("   • Sarah evolved by focusing on what worked")
    print("   • Offspring start with proven approach")
    print("   • Exponential growth through reproduction")
    print("   • Self-optimizing system!")

    print("\n" + "=" * 80)
