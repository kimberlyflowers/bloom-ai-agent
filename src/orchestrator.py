"""
BLOOM AI Agent - Single Agent Orchestrator
Coordinates a single agent's activities with scheduling.
"""

import logging
import os
import random
import time
from datetime import datetime
import schedule
from src.ai_agent import BloomAIAgent, Specialization
from src.reddit_integration import RedditMonitor, RedditStrategy
from src.twitter_integration import TwitterMonitor, TwitterStrategy

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates a single AI agent's daily activities.
    """

    def __init__(self, agent_id: str = "adam", initial_balance: float = 50.0,
                 specialization: Specialization = Specialization.GENERALIST):
        """Initialize orchestrator with agent and platform integrations"""

        # Create agent
        self.agent = BloomAIAgent(
            agent_id=agent_id,
            initial_balance=initial_balance,
            specialization=specialization
        )

        # Initialize platform monitors
        self.reddit_monitor = RedditMonitor()
        self.twitter_monitor = TwitterMonitor()

        # Initialize strategies
        self.reddit_strategy = RedditStrategy(self.reddit_monitor, self.agent)
        self.twitter_strategy = TwitterStrategy(self.twitter_monitor, self.agent)

        # Setup schedule
        self._setup_schedule()

        logger.info(f"Orchestrator initialized for agent '{agent_id}'")

    def _setup_schedule(self):
        """Setup daily schedule"""
        # Morning routine - scan opportunities
        schedule.every().day.at("09:00").do(self.morning_routine)

        # Execute strategies throughout the day
        schedule.every().day.at("12:00").do(self.execute_best_strategy)
        schedule.every().day.at("15:00").do(self.execute_best_strategy)
        schedule.every().day.at("18:00").do(self.execute_best_strategy)

        # Evening routine - review performance
        schedule.every().day.at("21:00").do(self.evening_routine)

        # Save state every hour
        schedule.every().hour.do(self.save_state)

        logger.info("Schedule configured")

    def morning_routine(self):
        """Morning routine - scan for opportunities"""
        logger.info("🌅 Running morning routine...")

        # Scan Reddit
        reddit_opps = self.reddit_monitor.find_opportunities(limit=50)
        logger.info(f"Found {len(reddit_opps)} Reddit opportunities")

        # Scan Twitter
        twitter_opps = self.twitter_monitor.find_opportunities(max_results=50)
        logger.info(f"Found {len(twitter_opps)} Twitter opportunities")

        # Log agent status
        report = self.agent.get_performance_report()
        logger.info(f"Agent Status: Balance ${report['balance']:.2f}, "
                   f"Mode: {report['operating_mode']}, "
                   f"ROI: {report['overall_roi']:.2f}x")

    def evening_routine(self):
        """Evening routine - review performance"""
        logger.info("🌙 Running evening routine...")

        # Generate performance report
        report = self.agent.get_performance_report()

        logger.info(f"""
        Daily Performance Report:
        ========================
        Balance: ${report['balance']:.2f}
        Total Earned: ${report['total_earned']:.2f}
        Total Spent: ${report['total_spent']:.2f}
        Overall ROI: {report['overall_roi']:.2f}x
        Operating Mode: {report['operating_mode']}
        Days Active: {report['days_active']}
        Total Conversions: {report['total_conversions']}
        Today Spent: ${report['today_spent']:.2f} / ${report['daily_limit']:.2f}

        Top Strategies:
        """)

        for strat in report['strategy_performance'][:3]:
            logger.info(f"  - {strat['name']}: ROI {strat['roi']:.2f}x "
                       f"(${strat['total_earned']:.2f} earned)")

        # Save state
        self.save_state()

    def execute_best_strategy(self):
        """Choose and execute the best strategy based on ROI"""
        logger.info("🎯 Executing best strategy...")

        # Choose strategy
        choice = self.agent.choose_next_strategy()

        if not choice:
            logger.warning("No affordable strategy available")
            return

        strategy_name, strategy = choice

        # Spend money
        if not self.agent.spend(strategy.cost_per_action, strategy_name):
            logger.error(f"Failed to spend on {strategy_name}")
            return

        # Execute the strategy
        success = False

        try:
            if strategy_name == 'reddit_value_comment':
                success = self.reddit_strategy.execute_value_comment_strategy()

            elif strategy_name == 'reddit_educational_post':
                success = self.reddit_strategy.execute_educational_post_strategy()

            elif strategy_name == 'twitter_reply':
                success = self.twitter_strategy.execute_reply_strategy()

            elif strategy_name == 'twitter_thread':
                success = self.twitter_strategy.execute_thread_strategy()

            elif strategy_name == 'reddit_boost':
                logger.info("Reddit boost strategy - would promote best post")
                success = True  # Simulated

            elif strategy_name == 'twitter_promoted':
                logger.info("Twitter promoted strategy - would promote best tweet")
                success = True  # Simulated

            else:
                logger.warning(f"Unknown strategy: {strategy_name}")

        except Exception as e:
            logger.error(f"Error executing {strategy_name}: {e}")
            success = False

        # Record result (no conversion yet, will come via webhook)
        self.agent.record_action_result(
            strategy_name=strategy_name,
            cost=strategy.cost_per_action,
            conversions=0,
            revenue=0.0
        )

        if success:
            logger.info(f"✅ Successfully executed {strategy_name}")
        else:
            logger.warning(f"❌ Failed to execute {strategy_name}")

    def simulate_conversion(self, plan_type: str, source_strategy: str,
                          source_platform: str, conversion_path: str = "simulated"):
        """
        Simulate a conversion (for testing/demo).
        In production, conversions come via webhook.
        """
        commission_amount = self.agent.COMMISSION_RATES.get(plan_type, 0.50)

        self.agent.record_commission(
            amount=commission_amount,
            user_id=f"user_{random.randint(1000, 9999)}",
            plan_type=plan_type,
            source_strategy=source_strategy,
            source_platform=source_platform,
            conversion_path=conversion_path
        )

        logger.info(f"🎉 Conversion simulated: {plan_type} → ${commission_amount:.2f} commission")

    def run_daily_cycle(self):
        """Run a full daily cycle (for testing)"""
        logger.info("🔄 Running daily cycle...")

        self.morning_routine()

        # Execute a few strategies
        for i in range(3):
            self.execute_best_strategy()
            time.sleep(1)  # Small delay

        self.evening_routine()

    def run_continuously(self):
        """Run agent continuously with schedule"""
        logger.info("🚀 Starting continuous agent operation...")

        # Run morning routine immediately
        self.morning_routine()

        # Run scheduled tasks
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def save_state(self):
        """Save agent state"""
        os.makedirs('data', exist_ok=True)
        filepath = f"data/{self.agent.agent_id}_state.json"
        self.agent.save_state(filepath)
        logger.info(f"State saved to {filepath}")

    @staticmethod
    def load_agent(agent_id: str) -> 'AgentOrchestrator':
        """Load agent from saved state"""
        filepath = f"data/{agent_id}_state.json"

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"No saved state found for agent '{agent_id}'")

        # Load agent
        agent = BloomAIAgent.load_state(filepath)

        # Create orchestrator
        orchestrator = AgentOrchestrator.__new__(AgentOrchestrator)
        orchestrator.agent = agent
        orchestrator.reddit_monitor = RedditMonitor()
        orchestrator.twitter_monitor = TwitterMonitor()
        orchestrator.reddit_strategy = RedditStrategy(orchestrator.reddit_monitor, agent)
        orchestrator.twitter_strategy = TwitterStrategy(orchestrator.twitter_monitor, agent)
        orchestrator._setup_schedule()

        logger.info(f"Agent '{agent_id}' loaded from {filepath}")

        return orchestrator


def main():
    """Main entry point for single agent"""
    # Load configuration
    from dotenv import load_dotenv
    load_dotenv()

    # Get initial balance from env
    initial_balance = float(os.getenv('INITIAL_BALANCE', '50.0'))
    run_mode = os.getenv('RUN_MODE', 'once')

    # Create orchestrator
    orchestrator = AgentOrchestrator(
        agent_id="adam",
        initial_balance=initial_balance
    )

    # Run based on mode
    if run_mode == 'continuous':
        orchestrator.run_continuously()
    else:
        orchestrator.run_daily_cycle()


if __name__ == "__main__":
    main()
