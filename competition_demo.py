"""
BLOOM AI Agent - Competition System Demo

Demonstrates how agents compete for higher commission rates based on performance.
"""

import logging
import random
from datetime import datetime
from src.colony_orchestrator import ColonyOrchestrator
from src.ai_agent import Specialization
from src.agent_competition import print_leaderboard

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def simulate_agent_performance(orchestrator: ColonyOrchestrator, cycles: int = 50):
    """
    Simulate multiple action cycles to build up performance data.

    This simulates:
    - Agents taking marketing actions (spending money)
    - Some conversions happening (earning commissions)
    - Performance varying between agents
    """

    print("\n" + "="*80)
    print("🔬 SIMULATING AGENT PERFORMANCE".center(80))
    print("="*80)
    print(f"Running {cycles} action cycles...")
    print()

    conversion_probability = 0.15  # 15% chance of conversion per action

    for cycle in range(cycles):
        # Each agent takes an action
        for agent_id in list(orchestrator.colony.agents.keys()):
            orchestrator.execute_agent_action(agent_id)

            # Randomly simulate conversions (15% chance)
            if random.random() < conversion_probability:
                plan_types = ['pro_monthly', 'agency_monthly', 'enterprise_annual']
                plan_type = random.choice(plan_types)

                orchestrator.simulate_conversion(
                    agent_id=agent_id,
                    plan_type=plan_type,
                    source_strategy='simulated',
                    source_platform='demo'
                )

        # Check for reproductions every 10 cycles
        if cycle % 10 == 0 and cycle > 0:
            orchestrator.check_reproductions()

        # Show progress
        if (cycle + 1) % 10 == 0:
            stats = orchestrator.colony.get_colony_stats()
            print(f"Cycle {cycle + 1}/{cycles}: "
                  f"{stats['colony_size']} agents, "
                  f"${stats['total_earned']:.2f} earned, "
                  f"{stats['overall_roi']:.2f}x ROI")

    print("\n✅ Simulation complete!\n")


def demo_competition_system():
    """Main demo of competition system"""

    print("\n" + "="*80)
    print("🎮 BLOOM AI AGENT - COMPETITION SYSTEM DEMO".center(80))
    print("="*80)
    print()
    print("This demo shows how agents compete for higher commission rates!")
    print()
    print("Performance Tiers:")
    print("  🏆 Elite (90-100 score):     15% commission (1.5x multiplier)")
    print("  🥇 Champion (75-89 score):   12% commission (1.2x multiplier)")
    print("  🥈 Competitor (50-74 score): 10% commission (1.0x - default)")
    print("  🥉 Learner (0-49 score):      8% commission (0.8x multiplier)")
    print()
    print("="*80)

    # Create colony with founding agent
    print("\n📍 Step 1: Creating colony with founding agent 'Adam'...")
    orchestrator = ColonyOrchestrator(
        initial_agent_id="adam",
        initial_balance=100.0
    )

    # Add a few more agents manually for demo purposes
    print("📍 Step 2: Adding more agents to the colony...")

    # Create diverse agents
    from src.ai_agent import BloomAIAgent

    agents_to_add = [
        ("beta", 80.0, Specialization.REDDIT_SPECIALIST),
        ("gamma", 60.0, Specialization.TWITTER_SPECIALIST),
        ("delta", 70.0, Specialization.CONTENT_CREATOR),
    ]

    for agent_id, balance, spec in agents_to_add:
        agent = BloomAIAgent(
            agent_id=agent_id,
            initial_balance=balance,
            specialization=spec
        )
        orchestrator.colony.add_agent(
            agent=agent,
            agent_id=agent_id,
            parent_id="adam",  # All children of Adam for demo
            specialization=spec
        )

    print(f"✅ Colony now has {len(orchestrator.colony.agents)} agents\n")

    # Simulate performance
    print("📍 Step 3: Simulating agent performance...")
    simulate_agent_performance(orchestrator, cycles=50)

    # Show current leaderboard
    print("📍 Step 4: Current Performance Leaderboard")
    print_leaderboard(orchestrator.colony.competition, title="CURRENT COMPETITION STANDINGS")

    # Show detailed stats for each agent
    print("\n📍 Step 5: Detailed Agent Statistics")
    print("="*80)

    for agent_id in orchestrator.colony.agents.keys():
        stats = orchestrator.colony.competition.get_agent_stats(agent_id)

        if stats:
            print(f"\n🤖 Agent: {agent_id}")
            print(f"   Performance Score: {stats['performance_score']:.2f}/100")
            print(f"   Tier: {stats['tier']}")
            print(f"   Commission Rate: {stats['commission_rate']} (multiplier: {stats['commission_multiplier']}x)")
            print(f"   Metrics:")
            print(f"     - ROI: {stats['metrics']['roi']}")
            print(f"     - Conversion Rate: {stats['metrics']['conversion_rate']}")
            print(f"     - Revenue per Action: {stats['metrics']['revenue_per_action']}")
            print(f"     - Total Revenue: {stats['metrics']['total_revenue']}")
            print(f"     - Total Actions: {stats['metrics']['total_actions']}")
            print(f"     - Total Conversions: {stats['metrics']['total_conversions']}")
            print(f"   Eligible for Competition: {'Yes ✅' if stats['eligible_for_competition'] else 'No ❌'}")

    print("\n" + "="*80)

    # Run weekly competition
    print("\n📍 Step 6: Running Weekly Competition")
    print("="*80)
    orchestrator.run_weekly_competition()

    # Show how commission rates vary
    print("\n📍 Step 7: Commission Rate Comparison")
    print("="*80)
    print("\nExample: If all agents converted a $50/month Pro plan user:\n")

    base_commission = 5.0  # $50 * 10% base rate

    for agent_id in orchestrator.colony.agents.keys():
        multiplier = orchestrator.colony.competition.get_commission_multiplier(agent_id)
        actual_commission = base_commission * multiplier
        tier = orchestrator.colony.competition.get_agent_tier(agent_id)

        print(f"  {agent_id:20} ({tier.display_name:12}): "
              f"${actual_commission:.2f} "
              f"(base ${base_commission:.2f} × {multiplier:.1f}x)")

    print("\n💡 Notice: Elite performers earn 1.5x more commission than Learner tier!")
    print("   This extra commission lets them take more actions → more conversions → more growth!")

    # Show natural selection impact
    print("\n📍 Step 8: Natural Selection Impact")
    print("="*80)
    print("""
    🧬 How Natural Selection Works:

    1. Elite Agent (1.5x commission):
       - Earns $7.50 per conversion (vs $5.00 base)
       - Can take 50% more actions with same conversions
       - Finds more customers → earns even more → scales faster
       - Reaches reproduction benchmarks faster
       - Creates more specialized children

    2. Learner Agent (0.8x commission):
       - Earns $4.00 per conversion (vs $5.00 base)
       - Can take 20% fewer actions
       - Struggles to find customers
       - May never reach reproduction benchmarks
       - Naturally phases out of the colony

    3. Result: Best strategies dominate!
       - High-ROI strategies spread through reproduction
       - Low-ROI strategies fade away
       - Colony naturally optimizes itself
       - No manual tuning required!
    """)

    # Final summary
    print("\n" + "="*80)
    print("✅ DEMO COMPLETE!".center(80))
    print("="*80)
    print("""
    🎯 Key Takeaways:

    1. Performance-Based Rewards
       - Agents compete based on ROI, conversion rate, and revenue
       - Top performers earn higher commission rates (up to 1.5x)

    2. Automatic Optimization
       - No manual configuration needed
       - Best agents naturally dominate through higher earnings
       - Poor performers fade out due to limited resources

    3. Evolutionary Pressure
       - Elite agents reproduce faster (more commission → more budget)
       - Their successful strategies spread to children
       - Colony naturally evolves toward optimal performance

    4. Fair Competition
       - All agents start equal (10% commission)
       - Performance is measured objectively
       - Weekly/monthly competitions keep it fresh
       - Tiers update dynamically based on current performance

    This creates a self-improving system that gets better over time! 🚀
    """)
    print("="*80 + "\n")


if __name__ == "__main__":
    demo_competition_system()
