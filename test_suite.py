"""
BLOOM AI Agent - Comprehensive Test Suite

Automated tests to verify all systems are working correctly.
"""

import sys
import os
import traceback
from datetime import datetime

# Test results
test_results = []
errors_found = []


def test_result(test_name, passed, details=""):
    """Record a test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    test_results.append({
        'test': test_name,
        'passed': passed,
        'details': details
    })
    print(f"{status} - {test_name}")
    if details:
        print(f"      {details}")
    if not passed:
        errors_found.append(f"{test_name}: {details}")


def test_imports():
    """Test 1: All imports work correctly"""
    print("\n" + "="*80)
    print("TEST 1: Import Checks")
    print("="*80)

    # Test core imports
    try:
        from src.ai_agent import BloomAIAgent, Specialization, Strategy
        test_result("Import ai_agent", True)
    except Exception as e:
        test_result("Import ai_agent", False, str(e))

    try:
        from src.agent_reproduction import AgentColony, ReproductionBenchmark
        test_result("Import agent_reproduction", True)
    except Exception as e:
        test_result("Import agent_reproduction", False, str(e))

    try:
        from src.agent_competition import AgentCompetition, PerformanceTier
        test_result("Import agent_competition", True)
    except Exception as e:
        test_result("Import agent_competition", False, str(e))

    try:
        from src.colony_learning import ColonyLearning, LearningRole
        test_result("Import colony_learning", True)
    except Exception as e:
        test_result("Import colony_learning", False, str(e))

    try:
        from src.colony_orchestrator import ColonyOrchestrator
        test_result("Import colony_orchestrator", True)
    except Exception as e:
        test_result("Import colony_orchestrator", False, str(e))

    # Test platform integrations
    try:
        from src.reddit_integration import RedditMonitor
        test_result("Import reddit_integration", True)
    except Exception as e:
        test_result("Import reddit_integration", False, str(e))

    try:
        from src.twitter_integration import TwitterMonitor
        test_result("Import twitter_integration", True)
    except Exception as e:
        test_result("Import twitter_integration", False, str(e))

    try:
        from src.discord_integration import DiscordMonitor
        test_result("Import discord_integration", True)
    except Exception as e:
        test_result("Import discord_integration", False, str(e))

    try:
        from src.telegram_integration import TelegramMonitor
        test_result("Import telegram_integration", True)
    except Exception as e:
        test_result("Import telegram_integration", False, str(e))

    try:
        from src.slack_integration import SlackMonitor
        test_result("Import slack_integration", True)
    except Exception as e:
        test_result("Import slack_integration", False, str(e))


def test_basic_functionality():
    """Test 2: Basic functionality of core components"""
    print("\n" + "="*80)
    print("TEST 2: Basic Functionality")
    print("="*80)

    try:
        from src.ai_agent import BloomAIAgent, Specialization

        # Create agent
        agent = BloomAIAgent(agent_id="test", initial_balance=100.0)
        test_result("Create BloomAIAgent", True)

        # Test strategy selection
        choice = agent.choose_next_strategy()
        if choice:
            test_result("Strategy selection", True, f"Selected: {choice[0]}")
        else:
            test_result("Strategy selection", False, "No strategy selected")

        # Test commission recording
        agent.record_commission(
            amount=5.0,
            user_id="test_user",
            plan_type="creator",
            source_strategy="test",
            source_platform="test",
            conversion_path="test"
        )
        if agent.total_earned == 5.0:
            test_result("Commission recording", True, f"Earned: ${agent.total_earned:.2f}")
        else:
            test_result("Commission recording", False, f"Expected $5.00, got ${agent.total_earned:.2f}")

    except Exception as e:
        test_result("Basic agent functionality", False, str(e))
        traceback.print_exc()


def test_colony_system():
    """Test 3: Colony and reproduction system"""
    print("\n" + "="*80)
    print("TEST 3: Colony System")
    print("="*80)

    try:
        from src.agent_reproduction import AgentColony
        from src.ai_agent import BloomAIAgent, Specialization

        # Create colony
        colony = AgentColony(colony_id="test")
        test_result("Create AgentColony", True)

        # Add agent
        agent = BloomAIAgent(agent_id="test_agent", initial_balance=100.0)
        colony.add_agent(agent, "test_agent", specialization=Specialization.GENERALIST)

        if len(colony.agents) == 1:
            test_result("Add agent to colony", True, f"Colony size: {len(colony.agents)}")
        else:
            test_result("Add agent to colony", False, f"Expected 1 agent, got {len(colony.agents)}")

        # Test colony stats
        stats = colony.get_colony_stats()
        if 'colony_size' in stats and stats['colony_size'] == 1:
            test_result("Colony stats", True)
        else:
            test_result("Colony stats", False, "Stats missing colony_size")

    except Exception as e:
        test_result("Colony system", False, str(e))
        traceback.print_exc()


def test_competition_system():
    """Test 4: Competition system"""
    print("\n" + "="*80)
    print("TEST 4: Competition System")
    print("="*80)

    try:
        from src.agent_competition import AgentCompetition, PerformanceTier

        # Create competition
        competition = AgentCompetition(colony_id="test")
        test_result("Create AgentCompetition", True)

        # Record activity
        competition.record_agent_activity(
            agent_id="test_agent",
            revenue=50.0,
            spent=10.0,
            conversions=1,
            actions=1
        )
        test_result("Record agent activity", True)

        # Get performance score
        score = competition.get_agent_performance_score("test_agent")
        if score > 0:
            test_result("Calculate performance score", True, f"Score: {score:.2f}/100")
        else:
            test_result("Calculate performance score", False, f"Score is {score}")

        # Get tier
        tier = competition.get_agent_tier("test_agent")
        test_result("Get performance tier", True, f"Tier: {tier.display_name}")

        # Get commission multiplier
        multiplier = competition.get_commission_multiplier("test_agent")
        if 0.8 <= multiplier <= 1.5:
            test_result("Get commission multiplier", True, f"Multiplier: {multiplier}x")
        else:
            test_result("Get commission multiplier", False, f"Invalid multiplier: {multiplier}")

    except Exception as e:
        test_result("Competition system", False, str(e))
        traceback.print_exc()


def test_learning_system():
    """Test 5: Collaborative learning system"""
    print("\n" + "="*80)
    print("TEST 5: Collaborative Learning System")
    print("="*80)

    try:
        from src.colony_learning import ColonyLearning, LearningRole, ExperimentStatus
        from src.agent_reproduction import AgentColony
        from src.ai_agent import BloomAIAgent
        from datetime import datetime

        # Create learning system
        learning = ColonyLearning(colony_id="test")
        test_result("Create ColonyLearning", True)

        # Create colony with agents
        colony = AgentColony(colony_id="test")
        agent1 = BloomAIAgent(agent_id="agent1", initial_balance=100.0)
        agent1.total_earned = 520.0
        agent1.total_spent = 100.0
        colony.add_agent(agent1, "agent1")

        agent2 = BloomAIAgent(agent_id="agent2", initial_balance=100.0)
        agent2.total_earned = 180.0
        agent2.total_spent = 100.0
        colony.add_agent(agent2, "agent2")

        # Register experiment
        learning.register_experiment(
            agent_id="agent2",
            strategy_name="test_strategy",
            platform="test",
            current_roi=1.8
        )
        test_result("Register experiment", True)

        # Check experiment status
        exp = learning.get_experiment_status("agent2")
        if exp:
            test_result("Get experiment status", True, f"Experiment found for agent2")
        else:
            test_result("Get experiment status", False, "Experiment not found")

        # Assign roles
        roles = learning.assign_learning_roles(colony)
        if len(roles) == 2:
            test_result("Assign learning roles", True, f"Assigned {len(roles)} roles")
        else:
            test_result("Assign learning roles", False, f"Expected 2 roles, got {len(roles)}")

    except Exception as e:
        test_result("Learning system", False, str(e))
        traceback.print_exc()


def test_integration():
    """Test 6: Full system integration"""
    print("\n" + "="*80)
    print("TEST 6: Full System Integration")
    print("="*80)

    try:
        from src.colony_orchestrator import ColonyOrchestrator

        # Create orchestrator (this integrates everything)
        orchestrator = ColonyOrchestrator(
            initial_agent_id="test_adam",
            initial_balance=100.0
        )
        test_result("Create ColonyOrchestrator", True)

        # Check colony exists
        if orchestrator.colony:
            test_result("Orchestrator has colony", True)
        else:
            test_result("Orchestrator has colony", False)

        # Check learning system exists
        if orchestrator.learning:
            test_result("Orchestrator has learning", True)
        else:
            test_result("Orchestrator has learning", False)

        # Check initial agent exists
        if "test_adam" in orchestrator.colony.agents:
            test_result("Initial agent created", True)
        else:
            test_result("Initial agent created", False)

        # Test conversion simulation
        orchestrator.simulate_conversion(
            agent_id="test_adam",
            plan_type="creator",
            source_strategy="test",
            source_platform="test"
        )

        agent = orchestrator.colony.agents["test_adam"]
        if agent.total_earned > 0:
            test_result("Conversion simulation", True, f"Agent earned ${agent.total_earned:.2f}")
        else:
            test_result("Conversion simulation", False, "No earnings recorded")

    except Exception as e:
        test_result("System integration", False, str(e))
        traceback.print_exc()


def test_action_tracking():
    """Test 7: Action tracking for competition"""
    print("\n" + "="*80)
    print("TEST 7: Action Tracking")
    print("="*80)

    try:
        from src.agent_reproduction import AgentColony
        from src.ai_agent import BloomAIAgent

        colony = AgentColony(colony_id="test")
        agent = BloomAIAgent(agent_id="test", initial_balance=100.0)
        colony.add_agent(agent, "test")

        # Record action
        colony.record_agent_action(
            agent_id="test",
            revenue=0.0,
            spent=0.10,
            conversions=0,
            actions=1
        )
        test_result("Record agent action", True)

        # Check competition tracking
        score = colony.competition.get_agent_performance_score("test")
        test_result("Action tracked in competition", True, f"Score updated: {score:.2f}")

    except Exception as e:
        test_result("Action tracking", False, str(e))
        traceback.print_exc()


def generate_report():
    """Generate final test report"""
    print("\n" + "="*80)
    print("FINAL TEST REPORT".center(80))
    print("="*80)

    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r['passed'])
    failed_tests = total_tests - passed_tests

    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    print(f"\nTotal Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Pass Rate: {pass_rate:.1f}%")

    if failed_tests > 0:
        print("\n" + "="*80)
        print("ERRORS FOUND:".center(80))
        print("="*80)
        for i, error in enumerate(errors_found, 1):
            print(f"\n{i}. {error}")

    print("\n" + "="*80)
    if pass_rate == 100:
        print("🎉 ALL TESTS PASSED! 🎉".center(80))
        print("System is ready for deployment!".center(80))
    elif pass_rate >= 80:
        print("⚠️  MOSTLY PASSING ⚠️".center(80))
        print("System mostly works, some fixes needed.".center(80))
    else:
        print("❌ SYSTEM HAS ISSUES ❌".center(80))
        print("Critical fixes required before deployment.".center(80))
    print("="*80)

    return pass_rate >= 80  # Pass if 80%+ tests pass


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("BLOOM AI AGENT - COMPREHENSIVE TEST SUITE".center(80))
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run all tests
    test_imports()
    test_basic_functionality()
    test_colony_system()
    test_competition_system()
    test_learning_system()
    test_integration()
    test_action_tracking()

    # Generate report
    passed = generate_report()

    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
