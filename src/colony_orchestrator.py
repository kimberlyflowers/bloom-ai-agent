"""
BLOOM AI Agent - Colony Orchestrator
Coordinates multiple agents with reproduction capability and Command Center integration.
"""

import logging
import os
import random
import time
from datetime import datetime
import schedule

# Standardized Imports for Railway Pathing
try:
    from .ai_agent import BloomAIAgent, Specialization
except (ImportError, ValueError):
    try:
        from ai_agent import BloomAIAgent, Specialization
    except ImportError:
        from src.ai_agent import BloomAIAgent, Specialization

from .agent_reproduction import AgentColony
from .colony_learning import ColonyLearning, print_learning_report
from .reddit_integration import RedditMonitor, RedditStrategy
from .twitter_integration import TwitterMonitor, TwitterStrategy

# NEW: Import Dashboard for Trust tracking
from .orchestration_dashboard import OrchestrationDashboard

logger = logging.getLogger(__name__)


class ColonyOrchestrator:
    """
    Orchestrates a colony of AI agents with reproduction capability.
    """

    def __init__(self, initial_agent_id: str = "adam", initial_balance: float = 50.0):
        """Initialize colony with founding agent"""

        # Create colony
        self.colony = AgentColony()
        
        # Initialize Command Center link
        self.dashboard = OrchestrationDashboard()

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

        logger.info(f"Colony orchestrator initialized with founding agent '{initial_agent_id}'")

    def _setup_schedule(self):
        """Setup colony-wide schedule"""
        schedule.every().day.at("09:00").do(self.morning_routine)
        schedule.every().hour.do(self.run_colony_cycle)
        schedule.every().day.at("21:00").do(self.evening_routine)
        schedule.every(6).hours.do(self.check_reproductions)
        schedule.every().sunday.at("18:00").do(self.run_learning_session)
        schedule.every().hour.do(self.save_all_states)

    def morning_routine(self):
        """Morning routine for entire colony"""
        logger.info("🌅 Running colony morning routine...")
        reddit_opps = self.reddit_monitor.find_opportunities(limit=100)
        twitter_opps = self.twitter_monitor.find_opportunities(max_results=100)
        
        stats = self.colony.get_colony_stats()
        
        # Update Dashboard Trust Metrics
        self.dashboard.update_trust_metrics(
            "sarah_001", # Link to Sarah's specific ID
            value_provided=True
        )
        
        logger.info(f"Colony Status: {stats['colony_size']} agents, ROI: {stats['overall_roi']:.2f}x")

    def evening_routine(self):
        """Evening routine - comprehensive colony report"""
        logger.info("🌙 Running colony evening routine...")
        stats = self.colony.get_colony_stats()
        self.save_all_states()

    def execute_agent_action(self, agent_id: str):
        """Execute action for a specific agent and report to dashboard"""
        if agent_id not in self.colony.agents:
            return

        agent = self.colony.agents[agent_id]
        choice = agent.choose_next_strategy()

        if not choice:
            return

        strategy_name, strategy = choice
        if not agent.spend(strategy.cost_per_action, strategy_name):
            return

        # Update ROI and Dashboard Metrics
        agent.record_action_result(strategy_name, strategy.cost_per_action)
        self.colony.record_agent_action(agent_id, 0.0, strategy.cost_per_action, 0, 1)
        
        # Increment Value Provided on your Vercel Dashboard
        self.dashboard.update_trust_metrics(agent_id, value_provided=True)

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

    def save_all_states(self):
        """Save state to the /data Railway Volume"""
        self.colony.save_colony_state('data')
        logger.info("All colony states saved to persistent volume")

    @staticmethod
    def load_colony(directory: str = 'data') -> 'ColonyOrchestrator':
        orchestrator = ColonyOrchestrator.__new__(ColonyOrchestrator)
        orchestrator.colony = AgentColony.load_colony_state(directory)
        orchestrator.dashboard = OrchestrationDashboard()
        orchestrator.reddit_monitor = RedditMonitor()
        orchestrator.twitter_monitor = TwitterMonitor()
        orchestrator._setup_schedule()
        return orchestrator

def main():
    from dotenv import load_dotenv
    load_dotenv()
    initial_balance = float(os.getenv('INITIAL_BALANCE', '50.0'))
    
    # Try to load existing colony from /data volume
    if os.path.exists('data/genealogy.json'):
        orchestrator = ColonyOrchestrator.load_colony('data')
    else:
        orchestrator = ColonyOrchestrator(initial_agent_id="adam", initial_balance=initial_balance)
    
    orchestrator.run_colony_cycle()

if __name__ == "__main__":
    main()
