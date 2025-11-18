#!/usr/bin/env python3
"""
BLOOM AI Agent - Interactive Demo
Demonstrates the AI agent system with commission tracking, learning, and reproduction.
"""

import os
import sys
import time
import random
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai_agent import BloomAIAgent, Specialization, OperatingMode
from agent_reproduction import AgentColony, REPRODUCTION_BENCHMARKS
from colony_orchestrator import ColonyOrchestrator


def print_header(text: str):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_agent_status(agent: BloomAIAgent, title: str = "Agent Status"):
    """Print agent status"""
    report = agent.get_performance_report()

    print(f"\n{'─' * 70}")
    print(f"  {title}: {agent.agent_id}")
    print(f"{'─' * 70}")
    print(f"  Balance:        ${report['balance']:.2f}")
    print(f"  Total Earned:   ${report['total_earned']:.2f}")
    print(f"  Total Spent:    ${report['total_spent']:.2f}")
    print(f"  ROI:            {report['overall_roi']:.2f}x")
    print(f"  Operating Mode: {report['operating_mode'].upper()}")
    print(f"  Conversions:    {report['total_conversions']}")
    print(f"{'─' * 70}\n")


def demo_1_basic_agent():
    """Demo 1: Basic agent with commission tracking"""
    print_header("DEMO 1: Basic Agent Operation")

    print("Creating agent 'Adam' with $50 starting balance...\n")
    agent = BloomAIAgent(agent_id="adam", initial_balance=50.0)

    print_agent_status(agent, "Initial State")

    print("Agent is in SURVIVAL mode (balance < $50)")
    print("In SURVIVAL mode, agent uses conservative, proven strategies.\n")

    time.sleep(1)

    print("\n📊 Agent's available strategies:")
    for name, strat in agent.strategies.items():
        print(f"  • {name}: ${strat.cost_per_action:.2f} per action")

    time.sleep(1)

    print("\n\n🎯 Choosing best strategy...")
    choice = agent.choose_next_strategy()

    if choice:
        strategy_name, strategy = choice
        print(f"✓ Selected: {strategy_name} (cost: ${strategy.cost_per_action:.2f})")

        print(f"\n💸 Spending ${strategy.cost_per_action:.2f} on {strategy_name}...")
        agent.spend(strategy.cost_per_action, strategy_name)

        print_agent_status(agent, "After Spending")

    time.sleep(1)

    print("\n\n🎉 Simulating a conversion...")
    print("A user found via reddit_value_comment signs up for Creator plan ($49/mo)")

    agent.record_commission(
        amount=4.90,
        user_id="user_001",
        plan_type="creator",
        source_strategy="reddit_value_comment",
        source_platform="reddit",
        conversion_path="https://bloom.com?utm_source=reddit"
    )

    print_agent_status(agent, "After Conversion")

    print("💡 Notice how the agent's balance increased and it's still in SURVIVAL mode.")

    input("\nPress Enter to continue to Demo 2...")


def demo_2_learning_system():
    """Demo 2: Learning and strategy optimization"""
    print_header("DEMO 2: Learning System")

    print("Creating agent and simulating multiple actions with varying ROI...\n")

    agent = BloomAIAgent(agent_id="beta", initial_balance=100.0)

    # Simulate different strategies with different success rates
    strategies_to_test = [
        ("reddit_value_comment", 0.10, 0.7),  # name, cost, success_rate
        ("twitter_reply", 0.10, 0.5),
        ("reddit_educational_post", 0.50, 0.8),
        ("twitter_thread", 0.30, 0.6)
    ]

    print("Executing 20 actions with varying success rates...\n")

    for i in range(20):
        strategy_name, cost, success_rate = random.choice(strategies_to_test)

        # Spend
        if agent.spend(cost, strategy_name):
            print(f"  Action {i+1}: {strategy_name} (${cost:.2f})", end="")

            # Random success
            if random.random() < success_rate:
                # Success! Record commission
                commission = random.choice([0.50, 1.90, 4.90])
                agent.record_commission(
                    amount=commission,
                    user_id=f"user_{i}",
                    plan_type="creator",
                    source_strategy=strategy_name,
                    source_platform="reddit" if "reddit" in strategy_name else "twitter",
                    conversion_path=f"conversion_{i}"
                )
                print(f" → ✓ Conversion! +${commission:.2f}")
            else:
                # No conversion
                agent.record_action_result(strategy_name, cost, 0, 0)
                print(" → ✗ No conversion")

        time.sleep(0.1)

    print_agent_status(agent, "After Learning Period")

    print("\n📈 Strategy Performance:")
    report = agent.get_performance_report()

    for strat in sorted(report['strategy_performance'], key=lambda x: x['roi'], reverse=True):
        if strat['total_spent'] > 0:
            print(f"\n  {strat['name']}:")
            print(f"    ROI: {strat['roi']:.2f}x")
            print(f"    Spent: ${strat['total_spent']:.2f}")
            print(f"    Earned: ${strat['total_earned']:.2f}")
            print(f"    Success Rate: {strat['success_count']}/{strat['success_count'] + strat['failure_count']}")

    print("\n\n💡 The agent now knows which strategies work best!")
    print("   It will favor high-ROI strategies in future decisions.")

    input("\nPress Enter to continue to Demo 3...")


def demo_3_operating_modes():
    """Demo 3: Operating modes (SURVIVAL → GROWTH → SCALE)"""
    print_header("DEMO 3: Operating Modes")

    print("Demonstrating how agent behavior changes across operating modes...\n")

    # Start in SURVIVAL
    agent = BloomAIAgent(agent_id="gamma", initial_balance=25.0)
    print_agent_status(agent, "SURVIVAL Mode (< $50)")

    print("In SURVIVAL mode:")
    print("  • Conservative strategy selection")
    print("  • Daily spending limit: $10")
    print("  • Heavily penalizes unproven strategies\n")

    time.sleep(1)

    # Upgrade to GROWTH
    print("\n💰 Adding funds to reach GROWTH mode...")
    agent.commission_balance = 150.0
    agent.total_earned = 150.0

    print_agent_status(agent, "GROWTH Mode ($50 - $500)")

    print("In GROWTH mode:")
    print("  • Balanced approach")
    print("  • Daily spending limit: $50")
    print("  • Tests new strategies while using proven ones\n")

    time.sleep(1)

    # Upgrade to SCALE
    print("\n💰💰 Adding more funds to reach SCALE mode...")
    agent.commission_balance = 750.0
    agent.total_earned = 750.0

    print_agent_status(agent, "SCALE Mode ($500+)")

    print("In SCALE mode:")
    print("  • Aggressive growth")
    print("  • Daily spending limit: $200")
    print("  • 2x boost for strategies with ROI > 3.0x")
    print("  • Maximizes high-performing strategies\n")

    input("\nPress Enter to continue to Demo 4...")


def demo_4_reproduction():
    """Demo 4: Cellular reproduction"""
    print_header("DEMO 4: Cellular Reproduction")

    print("Demonstrating agent reproduction when benchmarks are met...\n")

    # Create colony with successful agent
    colony = AgentColony()

    print("Creating founding agent 'Adam'...")
    adam = BloomAIAgent(agent_id="adam", initial_balance=250.0)

    # Simulate success to meet benchmark 1
    adam.total_earned = 600.0
    adam.total_spent = 200.0
    adam.commission_balance = 300.0

    # Add some ROI history
    for _ in range(15):
        for strat in adam.strategies.values():
            strat.roi_history.append(random.uniform(2.0, 4.0))

    # Backdate creation to meet days requirement
    adam.creation_date = datetime.now() - timedelta(days=20)

    colony.add_agent(adam, "adam", None, Specialization.GENERALIST)

    print_agent_status(adam, "Founding Agent 'Adam'")

    print("\n📋 Checking reproduction benchmarks...\n")

    benchmark = colony.check_reproduction_eligibility("adam")

    if benchmark:
        print(f"✓ Agent meets Reproduction Benchmark Level {benchmark.level}!")
        print(f"\n  Requirements:")
        print(f"    • Total Earned: ${benchmark.min_total_earned:.2f} ✓")
        print(f"    • Balance: ${benchmark.min_balance:.2f} ✓")
        print(f"    • ROI: {benchmark.min_roi:.1f}x ✓")
        print(f"    • Days Active: {benchmark.min_days_active} ✓")
        print(f"\n  Child Agent:")
        print(f"    • Specialization: {benchmark.child_specialization.value}")
        print(f"    • Starting Balance: ${benchmark.child_starting_balance:.2f}")

        time.sleep(1)

        print("\n\n🧬 INITIATING REPRODUCTION...\n")
        time.sleep(0.5)

        child_id = colony.reproduce_agent("adam", benchmark)

        if child_id:
            print(f"🎉 SUCCESS! New agent born: '{child_id}'")

            child = colony.agents[child_id]
            print_agent_status(child, f"Child Agent '{child_id}'")

            print(f"Parent 'Adam' balance after reproduction: ${adam.commission_balance:.2f}")

            print("\n🔍 Child's specialized strategies:")
            for name, strat in child.strategies.items():
                status = "✓ ENABLED" if strat.enabled else "✗ DISABLED"
                print(f"  {name}: {status}")
                if strat.enabled and len(strat.roi_history) > 0:
                    print(f"    (Inherited ROI knowledge from parent)")

    print("\n\n💡 The child agent inherits parent's knowledge but specializes!")
    print("   This allows the colony to grow and optimize over time.")

    input("\nPress Enter to continue to Demo 5...")


def demo_5_full_colony():
    """Demo 5: Full colony simulation"""
    print_header("DEMO 5: Full Colony Simulation")

    print("Creating and evolving a multi-agent colony...\n")

    # Create colony orchestrator
    print("Initializing colony with founding agent...")
    colony_orch = ColonyOrchestrator(initial_agent_id="adam", initial_balance=100.0)

    time.sleep(1)

    print("\n📅 Simulating 3 months of activity...\n")

    # Simulate conversions over time
    for month in range(1, 4):
        print(f"\n{'─' * 70}")
        print(f"  MONTH {month}")
        print(f"{'─' * 70}\n")

        # Random conversions for agents
        conversions_this_month = random.randint(10, 25)

        for i in range(conversions_this_month):
            # Pick random agent
            agent_ids = list(colony_orch.colony.agents.keys())
            agent_id = random.choice(agent_ids)

            # Random plan type
            plan_types = ['free', 'verify', 'creator', 'studio']
            weights = [0.4, 0.3, 0.2, 0.1]
            plan_type = random.choices(plan_types, weights=weights)[0]

            # Record conversion
            colony_orch.simulate_conversion(
                agent_id=agent_id,
                plan_type=plan_type,
                source_strategy="reddit_value_comment",
                source_platform="reddit"
            )

            # Small chance to execute an action
            if random.random() < 0.3:
                colony_orch.execute_agent_action(agent_id)

        # Check for reproductions
        reproductions = colony_orch.colony.run_reproduction_cycle()

        if reproductions > 0:
            print(f"\n  🧬 {reproductions} new agent(s) reproduced this month!")

        # Show stats
        stats = colony_orch.colony.get_colony_stats()
        print(f"\n  Colony Stats:")
        print(f"    • Total Agents: {stats['colony_size']}")
        print(f"    • Total Balance: ${stats['total_balance']:.2f}")
        print(f"    • Total Earned: ${stats['total_earned']:.2f}")
        print(f"    • Overall ROI: {stats['overall_roi']:.2f}x")
        print(f"    • Total Conversions: {stats['total_conversions']}")

        time.sleep(1)

    # Final report
    print_header("FINAL COLONY REPORT")

    stats = colony_orch.colony.get_colony_stats()

    print(f"Colony Size: {stats['colony_size']} agents")
    print(f"Total Balance: ${stats['total_balance']:.2f}")
    print(f"Total Earned: ${stats['total_earned']:.2f}")
    print(f"Overall ROI: {stats['overall_roi']:.2f}x")
    print(f"Total Reproductions: {stats['total_reproductions']}")

    print(f"\n📊 Generations:")
    for gen, count in sorted(stats['generations'].items()):
        print(f"  Generation {gen}: {count} agent(s)")

    print(f"\n🎯 Specializations:")
    for spec, count in stats['specializations'].items():
        print(f"  {spec}: {count} agent(s)")

    print(f"\n🏆 Top Performing Agents:")
    top_agents = sorted(stats['agents'], key=lambda x: x['total_earned'], reverse=True)[:5]
    for i, agent_info in enumerate(top_agents, 1):
        print(f"\n  {i}. {agent_info['agent_id']}")
        print(f"     Balance: ${agent_info['balance']:.2f}")
        print(f"     Earned: ${agent_info['total_earned']:.2f}")
        print(f"     ROI: {agent_info['roi']:.2f}x")
        print(f"     Children: {agent_info['children_count']}")

    print("\n\n🎉 Demo complete! The colony has evolved and grown autonomously.")


def main():
    """Run interactive demo"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║           BLOOM AI AGENT - CELLULAR REPRODUCTION DEMO              ║")
    print("║                                                                    ║")
    print("║  This demo showcases the AI agent system with:                    ║")
    print("║  • Commission-based learning                                      ║")
    print("║  • Adaptive strategy selection                                    ║")
    print("║  • Operating modes (SURVIVAL/GROWTH/SCALE)                        ║")
    print("║  • Cellular reproduction with specialization                      ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")

    print("\n\nThis demo runs 5 demonstrations:\n")
    print("  1. Basic agent operation")
    print("  2. Learning system")
    print("  3. Operating modes")
    print("  4. Cellular reproduction")
    print("  5. Full colony simulation")

    input("\nPress Enter to start...")

    try:
        demo_1_basic_agent()
        demo_2_learning_system()
        demo_3_operating_modes()
        demo_4_reproduction()
        demo_5_full_colony()

        print_header("ALL DEMOS COMPLETE")
        print("Thank you for exploring the BLOOM AI Agent system!\n")
        print("To run the actual system, use:")
        print("  • python src/orchestrator.py (single agent)")
        print("  • python src/colony_orchestrator.py (colony)")
        print("  • python src/webhook_handler.py (webhook server)\n")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
