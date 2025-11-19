"""
Comprehensive Test Suite for All Opportunity Systems

Tests:
1. Human Feedback System
2. Cross-Colony Learning Network
3. Agent Marketplace
4. Strategy Marketplace
5. Agent DNA Genetic Algorithm
6. Swarm Coordination
7. A/B Testing Framework
8. Performance Analytics SaaS
"""

import sys
import os
sys.path.insert(0, 'src')

print("=" * 80)
print("OPPORTUNITY SYSTEMS - COMPREHENSIVE TEST SUITE".center(80))
print("=" * 80)

errors = []
passes = []

# Test 1: Human Feedback System
print("\n1. TESTING HUMAN FEEDBACK SYSTEM")
print("-" * 80)

try:
    from human_feedback import HumanFeedbackLoop, HumanFeedback, ActionForReview

    feedback_loop = HumanFeedbackLoop(sample_rate=0.1)

    # Test action review request
    action = {
        'action_id': 'test_001',
        'agent_id': 'test_agent',
        'platform': 'discord',
        'strategy_name': 'helpful_reply',
        'content_preview': 'Test content',
        'context': 'Test context',
        'estimated_cost': 10.0,
        'expected_roi': 5.0,
        'is_new_strategy': True
    }

    review = feedback_loop.request_review(action)
    assert review.action_id == 'test_001'
    assert review.priority_score() > 0

    # Test feedback submission
    feedback = feedback_loop.submit_feedback(
        'test_001',
        {
            'helpfulness': 5,
            'brand_alignment': 4,
            'ethical_safety': 5,
            'long_term_reputation': 4,
            'creativity': 3
        }
    )

    assert feedback.overall_score() > 0
    assert feedback.is_approved()

    print("✅ Human Feedback: Action review works")
    print("✅ Human Feedback: Feedback submission works")
    print("✅ Human Feedback: Scoring calculation works")
    passes.append("Human Feedback System")

except Exception as e:
    print(f"❌ Human Feedback: {e}")
    errors.append(f"Human Feedback: {e}")

# Test 2: Cross-Colony Learning Network
print("\n2. TESTING CROSS-COLONY LEARNING NETWORK")
print("-" * 80)

try:
    from cross_colony_network import CrossColonyNetwork, AnonymizedLearning

    network = CrossColonyNetwork()

    # Test contribution
    learnings = [
        {
            'platform': 'discord',
            'strategy_type': 'helpful_reply',
            'roi': 5.2,
            'industry': 'creative_tools'
        }
    ]

    network.contribute('colony_1', learnings)
    assert len(network.global_learnings) == 1

    # Test insights
    insights = network.get_insights(platform='discord', industry='creative_tools')
    assert insights['sample_size'] == 1
    assert insights['average_roi'] == 5.2

    print("✅ Cross-Colony: Data contribution works")
    print("✅ Cross-Colony: Insights retrieval works")
    passes.append("Cross-Colony Learning Network")

except Exception as e:
    print(f"❌ Cross-Colony: {e}")
    errors.append(f"Cross-Colony: {e}")

# Test 3: Agent Marketplace
print("\n3. TESTING AGENT MARKETPLACE")
print("-" * 80)

try:
    from agent_marketplace import AgentMarketplace, AgentListing
    from ai_agent import BloomAIAgent, Specialization

    marketplace = AgentMarketplace()

    # Create mock agent
    agent = BloomAIAgent('test_agent', 100.0, Specialization.GENERALIST)
    agent.total_revenue = 150.0  # Meets requirements
    agent.days_active = 35  # Meets requirements
    agent.total_conversions = 50

    # Test listing
    marketplace.list_agent('test_agent', agent, 'user_1', 50.0)
    assert 'test_agent' in marketplace.listings

    # Test rental
    rental = marketplace.rent_agent('user_2', 'test_agent', 7)
    assert rental['total_cost'] == 350.0  # 50 * 7
    assert rental['revenue_split']['owner'] == 210.0  # 60%

    print("✅ Marketplace: Agent listing works")
    print("✅ Marketplace: Agent rental works")
    print("✅ Marketplace: Revenue split correct")
    passes.append("Agent Marketplace")

except Exception as e:
    print(f"❌ Marketplace: {e}")
    errors.append(f"Agent Marketplace: {e}")

# Test 4: Strategy Marketplace
print("\n4. TESTING STRATEGY MARKETPLACE")
print("-" * 80)

try:
    from strategy_marketplace import StrategyMarketplace, StrategyListing

    marketplace = StrategyMarketplace()

    # Test listing
    strategy_id = marketplace.list_strategy(
        'agent_1',
        'discord_helpful_reply',
        'discord',
        10.0,
        3.0,
        'Execution guide here...',
        5.2
    )

    assert strategy_id in marketplace.listings

    # Test purchase
    purchase = marketplace.buy_strategy('agent_2', strategy_id)
    assert purchase['price'] == 10.0
    assert purchase['revenue_split']['seller'] == 7.0  # 70%

    print("✅ Strategy Marketplace: Listing works")
    print("✅ Strategy Marketplace: Purchase works")
    print("✅ Strategy Marketplace: Revenue split correct")
    passes.append("Strategy Marketplace")

except Exception as e:
    print(f"❌ Strategy Marketplace: {e}")
    errors.append(f"Strategy Marketplace: {e}")

# Test 5: Agent DNA Genetic Algorithm
print("\n5. TESTING AGENT DNA GENETIC ALGORITHM")
print("-" * 80)

try:
    from agent_dna import AgentDNA, GeneticEvolution

    # Test DNA creation
    dna_a = AgentDNA()
    dna_b = AgentDNA()

    assert len(dna_a.genes) == 8
    assert all(0 <= v <= 1 for v in dna_a.genes.values())

    # Test crossover
    child_dna = dna_a.crossover(dna_b, mutation_rate=0.2)
    assert len(child_dna.genes) == 8

    # Test trait expression
    traits = child_dna.express_traits()
    assert 'max_actions_per_day' in traits
    assert 'exploration_rate' in traits

    # Test genetic evolution
    evolution = GeneticEvolution()
    evolution.register_agent('agent_a', dna_a)
    child_dna = evolution.reproduce('agent_a')

    assert evolution.generation == 1

    print("✅ Agent DNA: Creation works")
    print("✅ Agent DNA: Crossover works")
    print("✅ Agent DNA: Trait expression works")
    print("✅ Agent DNA: Evolution works")
    passes.append("Agent DNA Genetic Algorithm")

except Exception as e:
    print(f"❌ Agent DNA: {e}")
    errors.append(f"Agent DNA: {e}")

# Test 6: Swarm Coordination
print("\n6. TESTING SWARM COORDINATION")
print("-" * 80)

try:
    from swarm_coordinator import SwarmCoordinator, SwarmCampaign
    from agent_reproduction import AgentColony

    swarm = SwarmCoordinator()
    colony = AgentColony()

    # Add test agents
    from ai_agent import BloomAIAgent, Specialization
    colony.agents['agent_1'] = BloomAIAgent('agent_1', 100.0, Specialization.DISCORD_EXPERT)
    colony.agents['agent_2'] = BloomAIAgent('agent_2', 100.0, Specialization.TWITTER_EXPERT)

    # Test campaign creation
    campaign = swarm.create_campaign('test_campaign', 'Test goal', 1000.0, colony)
    assert campaign.total_budget == 1000.0
    assert len(campaign.agent_assignments) == 2

    # Test lead claiming
    claimed = swarm.claim_lead('lead_123', 'agent_1')
    assert claimed == True

    reclaimed = swarm.claim_lead('lead_123', 'agent_2')
    assert reclaimed == False  # Already claimed

    print("✅ Swarm: Campaign creation works")
    print("✅ Swarm: Lead deduplication works")
    passes.append("Swarm Coordination")

except Exception as e:
    print(f"❌ Swarm: {e}")
    errors.append(f"Swarm Coordination: {e}")

# Test 7: A/B Testing Framework
print("\n7. TESTING A/B TESTING FRAMEWORK")
print("-" * 80)

try:
    from ab_testing import ABTestingFramework, ABExperiment

    framework = ABTestingFramework()

    # Test experiment creation
    exp_id = framework.create_experiment(
        'Educational vs Promotional',
        'promotional_tweet',
        'educational_thread',
        duration_days=14,
        sample_size=100
    )

    assert exp_id in framework.experiments

    # Test result recording
    for i in range(30):
        framework.record_result(exp_id, 'control', 2.3)
        framework.record_result(exp_id, 'treatment', 4.1)

    # Test analysis
    analysis = framework.analyze(exp_id)
    assert analysis['status'] == 'complete'
    assert analysis['treatment_avg_roi'] > analysis['control_avg_roi']

    print("✅ A/B Testing: Experiment creation works")
    print("✅ A/B Testing: Result recording works")
    print("✅ A/B Testing: Analysis works")
    passes.append("A/B Testing Framework")

except Exception as e:
    print(f"❌ A/B Testing: {e}")
    errors.append(f"A/B Testing: {e}")

# Test 8: Performance Analytics SaaS
print("\n8. TESTING PERFORMANCE ANALYTICS SaaS")
print("-" * 80)

try:
    from performance_analytics import PerformanceAnalytics, SubscriptionTier, PerformanceDataPoint
    from datetime import datetime

    analytics = PerformanceAnalytics()

    # Test data ingestion
    from ai_agent import BloomAIAgent, Specialization
    agent = BloomAIAgent('test_agent', 100.0, Specialization.DISCORD_EXPERT)

    analytics.ingest_data(agent, 'colony_1', 'user_1', 'creative_tools')
    assert len(analytics.data_points) > 0

    # Add more data for benchmarking
    for i in range(100):
        data_point = PerformanceDataPoint(
            timestamp=datetime.now(),
            agent_id=f'agent_{i}',
            colony_id='colony_1',
            user_id='user_1',
            platform='discord',
            strategy_type='helpful_reply',
            industry='creative_tools',
            roi=5.0,
            conversion_rate=5.0,
            revenue=100.0,
            cost=20.0,
            actions=10,
            conversions=5,
            agent_age_days=30,
            agent_specialization='discord'
        )
        analytics.data_points.append(data_point)

    # Test benchmark calculation
    analytics.calculate_benchmarks()
    assert len(analytics.benchmarks) > 0

    # Test subscription access control
    analytics.set_subscription('user_1', SubscriptionTier.FREE)
    benchmark = analytics.get_benchmark('platform', 'discord', 'user_1')
    assert benchmark is None  # Free tier blocked

    analytics.set_subscription('user_1', SubscriptionTier.BASIC)
    benchmark = analytics.get_benchmark('platform', 'discord', 'user_1')
    assert benchmark is not None  # Basic tier has access

    # Test Pro features
    analytics.set_subscription('user_1', SubscriptionTier.PRO)
    insights = analytics.generate_insights_report('user_1')
    assert 'key_findings' in insights

    api_token = analytics.get_api_access_token('user_1')
    assert api_token is not None

    print("✅ Analytics: Data ingestion works")
    print("✅ Analytics: Benchmark calculation works")
    print("✅ Analytics: Access control works")
    print("✅ Analytics: Insights generation works")
    print("✅ Analytics: API token generation works")
    passes.append("Performance Analytics SaaS")

except Exception as e:
    print(f"❌ Analytics: {e}")
    errors.append(f"Performance Analytics: {e}")

# Final Report
print("\n" + "=" * 80)
print("TEST RESULTS".center(80))
print("=" * 80)

print(f"\n✅ PASSES: {len(passes)}/{len(passes) + len(errors)}")
for p in passes:
    print(f"   • {p}")

if errors:
    print(f"\n❌ ERRORS: {len(errors)}")
    for e in errors:
        print(f"   • {e}")
else:
    print(f"\n🎉 ALL TESTS PASSED!")

print("\n" + "=" * 80)

if len(errors) == 0:
    print("✅ ALL OPPORTUNITY SYSTEMS WORKING CORRECTLY".center(80))
    print("=" * 80)
    exit(0)
else:
    print("❌ SOME SYSTEMS HAVE ERRORS".center(80))
    print("=" * 80)
    exit(1)
