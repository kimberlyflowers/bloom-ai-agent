#!/usr/bin/env python3
"""
IP DEFENDER - Game Demo
Shows the transformation from marketing agent to educational game.
"""

import os
import sys
import time
import random

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from game_engine import IPDefender, ThreatType, PlayerTier
from evolution_system import EvolutionManager, EVOLUTION_BENCHMARKS


def print_header(text: str):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def print_player_status(player: IPDefender, title: str = "Player Status"):
    """Print player status"""
    report = player.get_performance_report()

    print(f"\n{'─' * 70}")
    print(f"  {title}: {player.player_id}")
    print(f"{'─' * 70}")
    print(f"  Creative Energy:   {report['creative_energy']} CE")
    print(f"  Total CE Earned:   {report['total_ce_earned']} CE")
    print(f"  Total CE Spent:    {report['total_ce_spent']} CE")
    print(f"  Success Rate:      {report['success_rate']:.1%}")
    print(f"  Player Tier:       {report['player_tier'].upper()}")
    print(f"  Threats Defeated:  {report['threats_defeated']}")
    print(f"  Current Streak:    {report['current_streak']}")
    print(f"  BLOOM Features:    {len(report['bloom_features_discovered'])}")
    print(f"{'─' * 70}\n")


def demo_1_pain_relief():
    """Demo 1: Experience the pain → relief journey"""
    print_header("DEMO 1: The Pain → Relief Journey")

    print("Welcome to IP Defender! You're a digital artist.")
    print("Someone just stole your artwork for AI training...\n")

    player = IPDefender(player_id="artist_1", initial_ce=100)

    time.sleep(1)

    print("\n🎯 CHALLENGE: Protect your artwork!\n")
    print("Available actions:")
    print("  1. Manual DMCA takedown (5 CE, 15 min, 30% success) - Frustration: 😫😫😫")
    print("  2. BLOOM Fingerprint (10 CE, instant, 95% success) - Frustration: 😊")

    time.sleep(2)

    print("\n\n📝 Let's try the MANUAL way first (how most people start)...\n")

    # Manual action - frustrating
    action = player.actions['manual_dmca']
    player.spend_ce(action.ce_cost, 'manual_dmca')

    print(f"⏳ Filing DMCA takedown... (waiting 15 minutes...)")
    print("   [In the game, this would be a real timer showing progress]")
    time.sleep(2)

    # Simulate failure (30% success rate)
    success = random.random() < 0.30
    if not success:
        print("\n❌ DMCA REJECTED: Platform says 'insufficient evidence'")
        print("💔 You LOST your artwork. The thief continues training AI on it.")
        print("🤬 Frustration level: MAX")
        player.earn_ce(0, ThreatType.AI_SCRAPING, 'manual_dmca', False)
    else:
        print("\n✓ DMCA accepted (got lucky!)")
        player.earn_ce(15, ThreatType.AI_SCRAPING, 'manual_dmca', True)

    time.sleep(2)

    print("\n\n🎨 NEW THREAT: Another company scraped your art portfolio!")
    print("\n💡 Hint: Maybe try something different?\n")

    time.sleep(1)

    print("📝 Let's try the BLOOM way...\n")

    # BLOOM action - relief!
    action = player.actions['bloom_fingerprint']
    player.spend_ce(action.ce_cost, 'bloom_fingerprint')

    print(f"⚡ BLOOM Fingerprint activating...")
    time.sleep(0.5)

    print("\n✅ INSTANT SUCCESS!")
    print("🛡️  Artwork fingerprinted and protected")
    print("📊 Monitoring enabled across ALL platforms")
    print("⛓️  Blockchain proof of ownership recorded")
    print("🎉 You earn 50 CE!")
    print("😊 Frustration level: ZERO")

    player.earn_ce(50, ThreatType.AI_SCRAPING, 'bloom_fingerprint', True, 'fingerprint')

    time.sleep(2)

    print_player_status(player, "After Experiencing Both Methods")

    print("\n💭 What did we learn?")
    print("   Manual DMCA: 30% success, 15 minutes, frustrating")
    print("   BLOOM: 95% success, instant, effortless")
    print("\n   Which would YOU use for your real artwork? 🤔")

    # Check conversion trigger
    trigger_msg = player.check_conversion_trigger()
    if trigger_msg:
        print(f"\n\n🎯 CONVERSION TRIGGER: {trigger_msg}")
        print("   [CTA Button: Try BLOOM Free →]")

    input("\nPress Enter to continue to Demo 2...")


def demo_2_learning_system():
    """Demo 2: AI learns player preferences"""
    print_header("DEMO 2: AI Learning System")

    print("The game's AI learns which actions work best for YOU.\n")
    print("Let's simulate 20 protection attempts...\n")

    player = IPDefender(player_id="artist_2", initial_ce=500)

    actions_to_try = [
        ('manual_dmca', ThreatType.DIRECT_COPY),
        ('manual_dmca', ThreatType.AI_SCRAPING),
        ('bloom_fingerprint', ThreatType.AI_SCRAPING),
        ('manual_dmca', ThreatType.MARKETPLACE_THEFT),
        ('bloom_fingerprint', ThreatType.DIRECT_COPY),
        ('bloom_auto_monitor', ThreatType.AI_SCRAPING),
        ('manual_dmca', ThreatType.UNAUTHORIZED_USE),
        ('bloom_fingerprint', ThreatType.MARKETPLACE_THEFT),
        ('bloom_blockchain_proof', ThreatType.DIRECT_COPY),
        ('manual_dmca', ThreatType.AI_SCRAPING),
    ] * 2  # 20 attempts

    for i, (action_name, threat) in enumerate(actions_to_try, 1):
        action = player.actions[action_name]

        if player.spend_ce(action.ce_cost, action_name):
            # Simulate success based on actual rates
            success = random.random() < action.base_success_rate

            ce_earned = action.ce_reward_on_success if success else 0
            player.earn_ce(ce_earned, threat, action_name, success,
                          'bloom_feature' if 'bloom' in action_name else None)

            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"  {i}. {action_name}: {status} "
                  f"(earned {ce_earned} CE, success rate: {action.average_success_rate():.0%})")

        time.sleep(0.1)

    print_player_status(player, "After 20 Attempts")

    print("\n📊 AI Learning Results:\n")
    report = player.get_performance_report()

    for action_data in sorted(report['action_performance'],
                             key=lambda x: x['success_rate'], reverse=True):
        if action_data['attempts'] > 0:
            print(f"  {action_data['name']}:")
            print(f"    Success Rate: {action_data['success_rate']:.0%}")
            print(f"    Net CE: {action_data['net_ce']:+d}")
            print(f"    Type: {action_data['type']}")
            print()

    print("💡 Notice: The AI now knows BLOOM actions are way better!")
    print("   Future actions will prioritize high-success methods.\n")

    # Show what the AI will choose next
    next_choice = player.choose_action()
    if next_choice:
        print(f"🤖 AI's next choice: {next_choice[0]}")
        print(f"   Why? Because it has the highest expected CE return!\n")

    input("\nPress Enter to continue to Demo 3...")


def demo_3_evolution():
    """Demo 3: Player evolution system"""
    print_header("DEMO 3: Player Evolution System")

    print("When you hit milestones, you EVOLVE and unlock new abilities!\n")

    # Create successful player
    player = IPDefender(player_id="pro_artist", initial_ce=250)
    player.total_ce_earned = 600
    player.threats_defeated = 40
    player.threats_failed = 10

    # Add success history
    for action in player.actions.values():
        if action.action_type == 'bloom_powered':
            action.success_history = [True] * 15 + [False] * 2
        else:
            action.success_history = [True] * 5 + [False] * 10

    # Fast-forward creation date
    from datetime import datetime, timedelta
    player.creation_date = datetime.now() - timedelta(days=5)

    print_player_status(player, "Current Status")

    # Create evolution manager
    evolution_mgr = EvolutionManager()
    evolution_mgr.add_player(player)

    print("\n🔍 Checking evolution eligibility...\n")

    benchmark = evolution_mgr.check_evolution_eligibility("pro_artist")

    if benchmark:
        print(f"✨ EVOLUTION AVAILABLE! ✨\n")
        print(f"  Level: {benchmark.level}")
        print(f"  Achievement: {benchmark.achievement_name}")
        print(f"  Unlocks: {benchmark.unlocked_specialization.value}")
        print(f"  Bonus: {benchmark.specialization_bonus}")

        print("\n  Requirements:")
        print(f"    ✅ Total CE: {player.total_ce_earned} ≥ {benchmark.min_total_ce}")
        print(f"    ✅ Balance: {player.creative_energy} ≥ {benchmark.min_ce_balance}")
        print(f"    ✅ Success Rate: {player.threats_defeated/(player.threats_defeated+player.threats_failed):.1%} ≥ {benchmark.min_success_rate:.1%}")
        print(f"    ✅ Days Active: {(datetime.now()-player.creation_date).days} ≥ {benchmark.min_days_active}")

        time.sleep(2)

        print("\n\n✨ EVOLVING...\n")
        time.sleep(1)

        evolution_mgr.evolve_player("pro_artist", benchmark)

        time.sleep(1)

        print(f"\n🎉 EVOLUTION COMPLETE!")
        print(f"   You are now a {benchmark.unlocked_specialization.value}!")

        updated_stats = evolution_mgr.get_player_stats("pro_artist")
        if updated_stats and 'evolution' in updated_stats:
            print(f"\n   Evolution Level: {updated_stats['evolution']['current_level']}")
            print(f"   Achievements: {', '.join(updated_stats['evolution']['achievements'])}")

    else:
        print("Not quite ready for evolution yet. Keep playing!")

    print("\n\n💡 All 6 Evolution Levels:")
    for i, bench in enumerate(EVOLUTION_BENCHMARKS, 1):
        print(f"\n  Level {i}: {bench.achievement_name}")
        print(f"    Unlocks: {bench.unlocked_specialization.value}")
        print(f"    Bonus: {bench.specialization_bonus}")
        print(f"    Requires: {bench.min_total_ce} CE, {bench.min_success_rate:.0%} success")

    input("\nPress Enter to finish...")


def main():
    """Run game demonstration"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║              IP DEFENDER - EDUCATIONAL GAME DEMO                   ║")
    print("║                                                                    ║")
    print("║  From Marketing Agent → Educational Game                           ║")
    print("║  Same AI intelligence, 100% Reddit compliant                       ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")

    print("\n\nThis demo shows the transformation:\n")
    print("  1. Pain → Relief journey (core game mechanic)")
    print("  2. AI learning system (same as agent)")
    print("  3. Player evolution (same as reproduction)")

    input("\nPress Enter to start...")

    try:
        demo_1_pain_relief()
        demo_2_learning_system()
        demo_3_evolution()

        print_header("DEMO COMPLETE")
        print("The IP Defender game demonstrates BLOOM's value through gameplay!")
        print("\n✅ Same AI intelligence as marketing agent")
        print("✅ 100% Reddit TOS compliant")
        print("✅ Potential to earn $167K from Reddit Developer Funds")
        print("✅ Better conversions through education\n")

        print("Next steps:")
        print("  1. Build Devvit integration")
        print("  2. Deploy to r/ArtistLounge")
        print("  3. Iterate based on feedback")
        print("  4. Scale to $167,000! 🚀\n")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
