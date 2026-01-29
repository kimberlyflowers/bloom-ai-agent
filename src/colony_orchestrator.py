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

# FIX: Use relative imports to find ai_agent in the same src/ directory
try:
    from .ai_agent import BloomAIAgent, Specialization
except (ImportError, ValueError):
    from ai_agent import BloomAIAgent, Specialization

from .agent_reproduction import AgentColony
from .colony_learning import ColonyLearning, print_learning_report
from .reddit_integration import RedditMonitor, RedditStrategy
from .twitter_integration import TwitterMonitor, TwitterStrategy

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
                success = True
            elif strategy_name == 'twitter_promoted':
                logger.info(f"Agent '{agent_id}' - Twitter promoted strategy")
                success = True
            else:
                logger.warning(f"Unknown strategy: {strategy_name}")

        except Exception as e:
            logger.error(f"Error executing {strategy_name} for agent '{agent_id}': {e}")
            success = False

        # Record results
        agent.record_action_result(
            strategy_name=strategy_name,
            cost=strategy.cost_per_action,
            conversions=0,
            revenue=0.0
        )

        self.colony.record_agent_action(
            agent_id=agent_id,
            revenue=0.0,
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
        for agent_id in list(self.colony.agents.keys()):
            self.execute_agent_action(agent_id)
        self.check_reproductions()

    def check_reproductions(self):
        """Check all agents for reproduction eligibility"""
        reproductions = self.colony.run_reproduction_cycle()
        if reproductions > 0:
            logger.info(f"🎉 {reproductions} new agent(s) born!")

    def simulate_conversion(self, agent_id: str, plan_type: str,
                           source_strategy: str, source_platform: str,
                           conversion_path: str = "simulated"):
        if agent_id not in self.colony.agents:
            logger.warning(f"Agent '{agent_id}' not found for conversion")
            return

        agent = self.colony.agents[agent_id]
        base_commission = agent.COMMISSION_RATES.get(plan_type, 0.50)
        genealogy = self.colony.genealogy[agent_id]
        if genealogy.specialization == Specialization.ENTERPRISE_HUNTER:
            base_commission *= 2.0

        performance_multiplier = self.colony.competition.get_commission_multiplier(agent_id)
        commission_amount = base_commission * performance_multiplier

        agent.record_commission(
            amount=commission_amount,
            user_id=f"user_{random.randint(1000, 9999)}",
            plan_type=plan_type,
            source_strategy=source_strategy,
            source_platform=source_platform,
            conversion_path=conversion_path
        )

        self.colony.record_agent_action(
            agent_id=agent_id,
            revenue=commission_amount,
            spent=0.0,
            conversions=1,
            actions=0
        )

    def run_weekly_competition(self):
        logger.info("🏆 Running weekly competition...")
        result = self.colony.run_weekly_competition()
        if result.winner_id:
            logger.info(f"🎊 Winner: {result.winner_id} with Score {result.winner_score:.2f}")

    def run_monthly_competition(self):
        logger.info("🏆🏆 Running MONTHLY competition...")
        result = self.colony.run_monthly_competition()
        if result.winner_id:
            logger.info(f"🎊🎊 Winner: {result.winner_id} with Score {result.winner_score:.2f}")

    def run_learning_session(self):
        logger.info("🧠 Running weekly learning session...")
        session = self.learning.run_learning_session(self.colony)
        if session:
            print_learning_report(session)
        else:
            logger.info("Not enough data for learning session yet")

    def get_colony_report(self) -> dict:
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
        logger.info("🚀 Starting continuous colony operation...")
        self.morning_routine()
        while True:
            schedule.run_pending()
            time.sleep(60)

    def save_all_states(self):
        self.colony.save_colony_state('data')
        logger.info("All colony states saved")

    @staticmethod
    def load_colony(directory: str = 'data') -> 'ColonyOrchestrator':
        orchestrator = ColonyOrchestrator.__new__(ColonyOrchestrator)
        orchestrator.colony = AgentColony.load_colony_state(directory)
        orchestrator.reddit_monitor = RedditMonitor()
        orchestrator.twitter_monitor = TwitterMonitor()
        orchestrator._setup_schedule()
        logger.info(f"Colony loaded from {directory}/ - {len(orchestrator.colony.agents)} agents")
        return orchestrator


def main():
    from dotenv import load_dotenv
    load_dotenv()
    initial_balance = float(os.getenv('INITIAL_BALANCE', '50.0'))
    run_mode = os.getenv('RUN_MODE', 'once')

    if os.path.exists('data/genealogy.json'):
        logger.info("Loading existing colony...")
        orchestrator = ColonyOrchestrator.load_colony('data')
    else:
        logger.info("Creating new colony...")
        orchestrator = ColonyOrchestrator(
            initial_agent_id="adam",
            initial_balance=initial_balance
        )

    if run_mode == 'continuous':
        orchestrator.run_continuously()
    else:
        orchestrator.morning_routine()
        orchestrator.run_colony_cycle()
        orchestrator.evening_routine()


if __name__ == "__main__":
    main()
