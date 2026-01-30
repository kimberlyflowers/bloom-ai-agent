"""
BLOOM AI Agent - Colony Orchestrator
Coordinates multiple agents with reproduction capability.
"""

import logging
import os
import random
import time
from datetime import datetime
import schedule
from src.ai_agent import BloomAIAgent, Specialization
from src.agent_reproduction import AgentColony
from src.colony_learning import ColonyLearning, print_learning_report
from src.reddit_integration import RedditMonitor, RedditStrategy
from src.twitter_integration import TwitterMonitor, TwitterStrategy

logger = logging.getLogger(__name__)


class ColonyOrchestrator:
    """
    Orchestrates a colony of AI agents with reproduction capability.
    """

    def __init__(self, initial_agent_id: str = "adam", initial_balance: float = 50.0):
        """Initialize colony with founding agent"""

        # Create colony
        self.colony = AgentColony()

        # Create founding agent
        founding_agent = BloomAIAgent(
            agent_id=initial_agent_id,
            initial_balance=initial_balance,
            specialization=Specialization.GENERALIST
        )

        # Add to colony
        self.colony.add_agent(
            agent=founding_agent,
            agent_id=initial_agent_id,
            parent_id=None,
            specialization=Specialization.GENERALIST
        )

        # Initialize platform monitors (shared across all agents)
        self.reddit_monitor = RedditMonitor()
        self.twitter_monitor = TwitterMonitor()

        # Initialize collaborative learning system
        self.learning = ColonyLearning(colony_id="main")

        # Setup schedule
        self._setup_schedule()

        logger.info(f"Colony orchestrator initialized with founding agent '{initial_agent_id}' and collaborative learning")

    def _setup_schedule(self):
        """Setup colony-wide schedule"""
        # Morning routine - colony-wide
        schedule.every().day.at("09:00").do(self.morning_routine)

        # Execute actions throughout the day
        schedule.every().hour.do(self.run_colony_cycle)

        # Evening routine
        schedule.every().day.at("21:00").do(self.evening_routine)

        # Check for reproductions every 6 hours
        schedule.every(6).hours.do(self.check_reproductions)

        # Collaborative learning sessions
        schedule.every().sunday.at("18:00").do(self.run_learning_session)  # Weekly on Sunday evening

        # Competition runs (keep for performance tracking)
        schedule.every().monday.at("00:00").do(self.run_weekly_competition)  # Weekly on Monday
        schedule.every().month.at("00:00").do(self.run_monthly_competition)  # Monthly on 1st

        # Save state every hour
        schedule.every().hour.do(self.save_all_states)

        logger.info("Colony schedule configured with collaborative learning and competition system")

    def morning_routine(self):
        """Morning routine for entire colony"""
        logger.info("🌅 Running colony morning routine...")

        # Scan platforms
        reddit_opps = self.reddit_monitor.find_opportunities(limit=100)
        twitter_opps = self.twitter_monitor.find_opportunities(max_results=100)

        logger.info(f"Found {len(reddit_opps)} Reddit opportunities")
        logger.info(f"Found {len(twitter_opps)} Twitter opportunities")

        # Get colony stats
        stats = self.colony.get_colony_stats()
        logger.info(f"Colony Status: {stats['colony_size']} agents, "
                   f"${stats['total_balance']:.2f} total balance, "
                   f"ROI: {stats['overall_roi']:.2f}x")

    def evening_routine(self):
        """Evening routine - comprehensive colony report"""
        logger.info("🌙 Running colony evening routine...")

        stats = self.colony.get_colony_stats()

        logger.info(f"""
        Colony Performance Report:
        =========================
        Colony Size: {stats['colony_size']} agents
        Total Balance: ${stats['total_balance']:.2f}
        Total Earned: ${stats['total_earned']:.2f}
        Total Spent: ${stats['total_spent']:.2f}
        Overall ROI: {stats['overall_roi']:.2f}x
        Total Conversions: {stats['total_conversions']}
        Total Reproductions: {stats['total_reproductions']}

        Generations:
        """)

        for gen, count in sorted(stats['generations'].items()):
            logger.info(f"  Generation {gen}: {count} agents")

        logger.info("\n        Specializations:")
        for spec, count in stats['specializations'].items():
            logger.info(f"  {spec}: {count} agents")

        logger.info("\n        Top Performing Agents:")
        # Sort agents by ROI
        top_agents = sorted(stats['agents'], key=lambda x: x['roi'], reverse=True)[:5]
        for agent_info in top_agents:
            logger.info(f"  {agent_info['agent_id']}: "
                       f"${agent_info['balance']:.2f} balance, "
                       f"{agent_info['roi']:.2f}x ROI, "
                       f"{agent_info['children_count']} children")

        # Show competition leaderboard
        logger.info("\n        🏆 Competition Leaderboard:")
        leaderboard = self.colony.get_leaderboard(limit=5)
        if leaderboard:
            for entry in leaderboard:
                logger.info(f"  #{entry['rank']} {entry['agent_id']}: "
                           f"Score {entry['score']:.1f}, "
                           f"{entry['tier']} tier, "
                           f"{entry['commission_rate']} commission, "
                           f"{entry['roi']:.2f}x ROI")
        else:
            logger.info("  (No agents eligible for competition yet)")

        # Save state
        self.save_all_states()

    def execute_agent_action(self, agent_id: str):
        """Execute one marketing action for a specific agent"""
        if agent_id not in self.colony.agents:
            logger.warning(f"Agent '{agent_id}' not found")
            return

        agent = self.colony.agents[agent_id]
        genealogy = self.colony.genealogy[agent_id]

        # Choose strategy
        choice = agent.choose_next_strategy()

        if not choice:
            logger.debug(f"Agent '{agent_id}' has no affordable strategy")
            return

        strategy_name, strategy = choice

        # Spend money
        if not agent.spend(strategy.cost_per_action, strategy_name):
            logger.warning(f"Agent '{agent_id}' failed to spend on {strategy_name}")
            return

        # Execute the strategy based on specialization
        success = False

        try:
            # Create strategy executors
            reddit_strategy = RedditStrategy(self.reddit_monitor, agent)
            twitter_strategy = TwitterStrategy(self.twitter_monitor, agent)

            if strategy_name == 'reddit_value_comment':
                success = reddit_strategy.execute_value_comment_strategy()

            elif strategy_name == 'reddit_educational_post':
                success = reddit_strategy.execute_educational_post_strategy()

            elif strategy_name == 'twitter_reply':
                success = twitter_strategy.execute_reply_strategy()

            elif strategy_name == 'twitter_thread':
                success = twitter_strategy.execute_thread_strategy()

            elif strategy_name == 'reddit_boost':
                logger.info(f"Agent '{agent_id}' - Reddit boost strategy")
                success = True  # Simulated

            elif strategy_name == 'twitter_promoted':
                logger.info(f"Agent '{agent_id}' - Twitter promoted strategy")
                success = True  # Simulated

            else:
                logger.warning(f"Unknown strategy: {strategy_name}")

        except Exception as e:
            logger.error(f"Error executing {strategy_name} for agent '{agent_id}': {e}")
            success = False

        # Record result in agent's history
        agent.record_action_result(
            strategy_name=strategy_name,
            cost=strategy.cost_per_action,
            conversions=0,
            revenue=0.0
        )

        # Record action in competition system (for performance tracking)
        self.colony.record_agent_action(
            agent_id=agent_id,
            revenue=0.0,  # No revenue yet (comes from conversions via webhook)
            spent=strategy.cost_per_action,
            conversions=0,
            actions=1
        )

        if success:
            logger.info(f"✅ Agent '{agent_id}' executed {strategy_name}")
        else:
            logger.warning(f"❌ Agent '{agent_id}' failed {strategy_name}")

    def run_colony_cycle(self):
        """Run one action cycle for all agents"""
        logger.info(f"🔄 Running colony cycle with {len(self.colony.agents)} agents...")

        # Each agent executes one action
        for agent_id in list(self.colony.agents.keys()):
            self.execute_agent_action(agent_id)

        # Check for reproductions
        self.check_reproductions()

    def check_reproductions(self):
        """Check all agents for reproduction eligibility"""
        reproductions = self.colony.run_reproduction_cycle()

        if reproductions > 0:
            logger.info(f"🎉 {reproductions} new agent(s) born!")
            # Update schedule if needed (more agents = more activity)

    def simulate_conversion(self, agent_id: str, plan_type: str,
                          source_strategy: str, source_platform: str,
                          conversion_path: str = "simulated"):
        """
        Simulate a conversion for testing.
        In production, this comes via webhook.
        """
        if agent_id not in self.colony.agents:
            logger.warning(f"Agent '{agent_id}' not found for conversion")
            return

        agent = self.colony.agents[agent_id]

        # Calculate base commission
        base_commission = agent.COMMISSION_RATES.get(plan_type, 0.50)

        # Apply specialization multiplier
        genealogy = self.colony.genealogy[agent_id]
        if genealogy.specialization == Specialization.ENTERPRISE_HUNTER:
            base_commission *= 2.0  # 2x commission for enterprise hunter

        # Apply performance multiplier from competition system
        performance_multiplier = self.colony.competition.get_commission_multiplier(agent_id)
        commission_amount = base_commission * performance_multiplier

        # Record commission in agent
        agent.record_commission(
            amount=commission_amount,
            user_id=f"user_{random.randint(1000, 9999)}",
            plan_type=plan_type,
            source_strategy=source_strategy,
            source_platform=source_platform,
            conversion_path=conversion_path
        )

        # Record revenue in competition system
        self.colony.record_agent_action(
            agent_id=agent_id,
            revenue=commission_amount,
            spent=0.0,
            conversions=1,
            actions=0
        )

        tier = self.colony.competition.get_agent_tier(agent_id)
        logger.info(f"🎉 Conversion recorded for agent '{agent_id}': "
                   f"{plan_type} → ${commission_amount:.2f} commission "
                   f"(base ${base_commission:.2f} × {performance_multiplier}x {tier.display_name} tier)")

    def run_weekly_competition(self):
        """Run weekly competition and announce results"""
        logger.info("🏆 Running weekly competition...")

        result = self.colony.run_weekly_competition()

        if result.winner_id:
            logger.info(f"""
            🎊 WEEKLY COMPETITION RESULTS 🎊
            ================================
            Winner: {result.winner_id}
            Score: {result.winner_score:.2f}/100
            Tier: {result.winner_tier.display_name}
            Commission Rate: {result.winner_tier.multiplier * 10}%

            Top 5 Rankings:
            """)

            for i, (agent_id, score, tier) in enumerate(result.rankings[:5], 1):
                logger.info(f"  {i}. {agent_id}: {score:.2f} points ({tier.display_name} tier)")

            logger.info(f"\nTotal participants: {len(result.rankings)}")
        else:
            logger.info("No eligible agents for this week's competition")

    def run_monthly_competition(self):
        """Run monthly competition and announce results"""
        logger.info("🏆🏆 Running MONTHLY competition...")

        result = self.colony.run_monthly_competition()

        if result.winner_id:
            logger.info(f"""
            🎊🎊 MONTHLY COMPETITION RESULTS 🎊🎊
            ====================================
            Winner: {result.winner_id}
            Score: {result.winner_score:.2f}/100
            Tier: {result.winner_tier.display_name}
            Commission Rate: {result.winner_tier.multiplier * 10}%

            Top 10 Rankings:
            """)

            for i, (agent_id, score, tier) in enumerate(result.rankings[:10], 1):
                logger.info(f"  {i}. {agent_id}: {score:.2f} points ({tier.display_name} tier)")

            logger.info(f"\nTotal participants: {len(result.rankings)}")
        else:
            logger.info("No eligible agents for this month's competition")

    def run_learning_session(self):
        """
        Run collaborative learning session.

        Agents learn from the best while protecting promising experiments.
        This prevents the "local maximum trap" where everyone chases quick wins
        and misses better long-term strategies.
        """
        logger.info("🧠 Running weekly learning session...")

        session = self.learning.run_learning_session(self.colony)

        if session:
            # Print detailed report
            print_learning_report(session)

            # Log key insights
            logger.info(f"\n💡 Learning Insights:")
            logger.info(f"  Best performer: {session['best_agent']} ({session['best_roi']:.2f}x ROI)")
            logger.info(f"  Agents improved: {len(session['actions'])}")

            # Show protected experiments
            protected_count = sum(1 for action in session['actions']
                                 if action['role'] == 'Experimenter')
            if protected_count > 0:
                logger.info(f"  🛡️ Protected experiments: {protected_count}")
                logger.info(f"     (These are showing promise even if ROI is currently lower)")

        else:
            logger.info("Not enough data for learning session yet")

    def get_colony_report(self) -> dict:
        """Get comprehensive colony report"""
        stats = self.colony.get_colony_stats()
        tree = self.colony.get_family_tree()
        leaderboard = self.colony.get_leaderboard(limit=10)

        return {
            'timestamp': datetime.now().isoformat(),
            'stats': stats,
            'family_tree': tree,
            'reproduction_history': self.colony.reproduction_history,
            'competition_leaderboard': leaderboard
        }

    def run_continuously(self):
        """Run colony continuously with schedule"""
        logger.info("🚀 Starting continuous colony operation...")

        # Run morning routine immediately
        self.morning_routine()

        # Run scheduled tasks
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def save_all_states(self):
        """Save all colony state"""
        self.colony.save_colony_state('data')
        logger.info("All colony states saved")

    @staticmethod
    def load_colony(directory: str = 'data') -> 'ColonyOrchestrator':
        """Load colony from saved state"""
        orchestrator = ColonyOrchestrator.__new__(ColonyOrchestrator)

        # Load colony
        orchestrator.colony = AgentColony.load_colony_state(directory)

        # Initialize platform monitors
        orchestrator.reddit_monitor = RedditMonitor()
        orchestrator.twitter_monitor = TwitterMonitor()

        # Setup schedule
        orchestrator._setup_schedule()

        logger.info(f"Colony loaded from {directory}/ - {len(orchestrator.colony.agents)} agents")

        return orchestrator


def main():
    """Main entry point for colony"""
    # Load configuration
    from dotenv import load_dotenv
    load_dotenv()

    # Get configuration
    initial_balance = float(os.getenv('INITIAL_BALANCE', '50.0'))
    run_mode = os.getenv('RUN_MODE', 'once')

    # Try to load existing colony, or create new one
    if os.path.exists('data/genealogy.json'):
        logger.info("Loading existing colony...")
        orchestrator = ColonyOrchestrator.load_colony('data')
    else:
        logger.info("Creating new colony...")
        orchestrator = ColonyOrchestrator(
            initial_agent_id="adam",
            initial_balance=initial_balance
        )

    # Run based on mode
    if run_mode == 'continuous':
        orchestrator.run_continuously()
    else:
        # Run a single cycle
        orchestrator.morning_routine()
        orchestrator.run_colony_cycle()
        orchestrator.evening_routine()


if __name__ == "__main__":
    main()
