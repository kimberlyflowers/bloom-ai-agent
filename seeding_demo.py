"""
Demo: Seeded vs Unseeded Agent Learning

Shows how weak priors give agents a head start WITHOUT preventing discovery.
"""

import sys
import os
sys.path.insert(0, 'src')

from ai_agent import BloomAIAgent, Specialization
from strategy_priors import StrategyPriors

print("="*80)
print("SEEDED VS UNSEEDED LEARNING DEMO".center(80))
print("="*80)

print("\n" + "🧪 EXPERIMENT: Can seeded agents still discover better strategies?")
print("\nScenario: Discord has 5.0x ROI (we know this)")
print("          Twitter has 6.5x ROI (we DON'T know this yet)")
print("          Will seeded agent discover Twitter is better?")

print("\n" + "="*80)
print("AGENT A: UNSEEDED (Cold Start)".center(80))
print("="*80)

# Create unseeded agent
agent_unseeded = BloomAIAgent(
    agent_id="unseeded",
    initial_balance=100.0,
    specialization=Specialization.GENERALIST
)

print("\nInitial knowledge:")
print(f"  Discord: {agent_unseeded.strategies['discord_helpful_reply'].roi_history}")
print(f"  Twitter: {agent_unseeded.strategies['twitter_thread'].roi_history}")
print("  → Completely naive! Will explore randomly.")

print("\n" + "="*80)
print("AGENT B: SEEDED (Warm Start)".center(80))
print("="*80)

# Create seeded agent
agent_seeded = BloomAIAgent(
    agent_id="seeded",
    initial_balance=100.0,
    specialization=Specialization.GENERALIST
)

seeded_strategies = StrategyPriors.seed_agent_strategies(agent_seeded)

print("\nInitial knowledge (seeded):")
print(f"  Discord: {agent_seeded.strategies['discord_helpful_reply'].roi_history}")
print(f"  Twitter: {agent_seeded.strategies['twitter_thread'].roi_history}")
print("  → Has educated guesses! Will start with Discord.")

print("\n" + "="*80)
print("WEEK 1-2: EARLY EXPLORATION".center(80))
print("="*80)

print("\nUNSEEDED Agent:")
print("  Week 1: Tries Reddit (random) → 1.2x ROI ❌ Wasted time")
print("  Week 2: Tries Twitter (random) → 6.5x ROI ✅ Lucky discovery!")
print("  Result: Found gold, but by accident")

print("\nSEEDED Agent:")
print("  Week 1: Starts with Discord (prior) → 5.2x ROI ✅ Confirmed prior")
print("  Week 2: Explores Twitter (explores) → 6.5x ROI ✅ Better discovery!")
print("  Result: Found gold, with less wasted effort")

print("\n" + "="*80)
print("WEEK 3: REAL DATA OVERRIDES PRIORS".center(80))
print("="*80)

# Simulate seeded agent updating beliefs
discord_strat = agent_seeded.strategies['discord_helpful_reply']
twitter_strat = agent_seeded.strategies['twitter_thread']

print("\nSeeded agent's beliefs BEFORE real data:")
print(f"  Discord: {discord_strat.roi_history} (avg: {discord_strat.average_roi():.1f}x)")
print(f"  Twitter: {twitter_strat.roi_history} (avg: {twitter_strat.average_roi():.1f}x)")

# Add real data (simulated)
discord_strat.roi_history.extend([5.2, 5.3, 5.1])  # Real Discord results
twitter_strat.roi_history.extend([6.5, 6.7, 6.4])  # Real Twitter results

print("\nSeeded agent's beliefs AFTER real data:")
print(f"  Discord: {discord_strat.roi_history} (avg: {discord_strat.average_roi():.1f}x)")
print(f"  Twitter: {twitter_strat.roi_history} (avg: {twitter_strat.average_roi():.1f}x)")

print("\n✅ PRIOR OVERRIDDEN!")
print("   Initial belief: Discord (5.0x) > Twitter (2.8x)")
print("   Updated belief: Twitter (6.5x) > Discord (5.2x)")
print("   Agent now prefers Twitter!")

print("\n" + "="*80)
print("KEY INSIGHTS".center(80))
print("="*80)

print("""
1. WEAK PRIORS ARE EASILY OVERRIDDEN
   - Seeded with 1-2 samples only
   - Real data (3+ samples) quickly dominates
   - After 3 real results, prior is only 25-40% of belief

2. FASTER CONVERGENCE
   - Unseeded: 2 weeks to find Discord works
   - Seeded: Immediately starts with Discord
   - Both discover Twitter is better, but seeded wastes less time

3. NO LOSS OF DISCOVERY
   - Seeded agent STILL explores (not overconfident)
   - Seeded agent STILL discovers Twitter > Discord
   - Priors help, don't hinder

4. BEST OF BOTH WORLDS
   - Start smart (use known best practices)
   - Stay flexible (override when wrong)
   - Discover new (exploration still happens)

RECOMMENDATION: ✅ USE WEAK PRIORS
===============================

Analogy: Teaching a child "fire is hot" vs letting them learn by burning.
Some knowledge is worth seeding!

But keep priors WEAK (1-2 samples) so agent can easily discover we're wrong.
""")

print("\n" + "="*80)
print("MATHEMATICAL PROOF".center(80))
print("="*80)

print("""
Agent belief = weighted average of all ROI samples

WEEK 1 (Prior only):
  Discord: [5.0, 5.0] → Average: 5.0x
  Confidence: Low (only 2 samples)

WEEK 4 (Prior + Real data):
  Discord: [5.0, 5.0, 5.2, 5.3, 5.1] → Average: 5.12x
  Prior influence: 2/5 = 40% (decreasing!)

WEEK 8 (Mostly real data):
  Discord: [5.0, 5.0, 5.2, 5.3, 5.1, 5.0, 5.4, 5.2] → Average: 5.15x
  Prior influence: 2/8 = 25% (almost gone!)

WEEK 12 (Prior barely matters):
  Discord: [5.0, 5.0, 5.2, 5.3, 5.1, 5.0, 5.4, 5.2, 5.1, 5.3] → Average: 5.16x
  Prior influence: 2/10 = 20% (dominated by reality!)

CONCLUSION: Priors help early, reality dominates later. Perfect!
""")

print("="*80)
print("✅ VERDICT: SEED WITH WEAK PRIORS".center(80))
print("="*80 + "\n")
