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

# FIX: Standardized Relative Imports for Railway src/ folder
try:
    from .ai_agent import BloomAIAgent, Specialization
    from .agent_reproduction import AgentColony
    from .colony_learning import ColonyLearning
    from .reddit_integration import RedditMonitor
    from .twitter_integration import TwitterMonitor
    from .orchestration_dashboard import OrchestrationDashboard
except (ImportError, ValueError):
    # Fallback for different execution environments
    from ai_agent import BloomAIAgent, Specialization
    from agent_reproduction import AgentColony
    from colony_learning import ColonyLearning
    from reddit_integration import RedditMonitor
    from twitter_integration import TwitterMonitor
    from orchestration_dashboard import OrchestrationDashboard

logger = logging.getLogger(__name__)

class ColonyOrchestrator:
    """
    Orchestrates a colony of AI agents with reproduction capability.
    """

    def __init__(self, initial_agent_id: str = "sarah_001", initial_balance: float = 50.0):
        """Initialize colony with founding agent"""
        
        # Create directories for Railway persistence
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)

        self.colony = AgentColony()
        self.dashboard = OrchestrationDashboard()

        # Founding agent
        founding_agent = BloomAIAgent(
            agent_id=initial_agent_id,
            initial_balance=initial_balance,
            specialization=Specialization.GENERALIST
        )

        self.colony.add_agent(
            agent=founding_agent,
            agent_id=initial_agent_id,
            parent_id=None,
            specialization=Specialization.GENERALIST
        )

        self.reddit_monitor = RedditMonitor()
        self.twitter_monitor = TwitterMonitor()
        self.learning = ColonyLearning(colony_id="main")

        self._setup_schedule()
        logger.info(f"Colony initialized with agent '{initial_agent_id}'")

    def _setup_schedule(self):
        """Setup colony-wide schedule"""
        schedule.every().day.at("09:00").do(self.morning_routine)
        schedule.every().hour.do(self.run_colony_cycle)
        schedule.every().day.at("21:00").do(self.evening_routine)
        schedule.every(6).hours.do(self.check_reproductions)
        schedule.every().hour.do(self.save_all_states)

    def morning_routine(self):
        """Morning routine: Find opportunities and ping dashboard"""
        logger.info("🌅 Running colony morning routine...")
        self.reddit_monitor.find_opportunities(limit=50)
        self.twitter_monitor.find_opportunities(max_results=50)
        
        # Update Dashboard for the founding agent
        self.dashboard.update_trust_metrics("sarah_001", value_provided=True)

    def evening_routine(self):
        """Evening routine - save and report"""
        logger.info("🌙 Running colony evening routine...")
        self.save_all_states()

    def execute_agent_action(self, agent_id: str):
        """Execute action and report to dashboard"""
        if agent_id not in self.colony.agents:
            return

        agent = self.colony.agents[agent_id]
        choice = agent.choose_next_strategy()

        if not choice:
            return

        strategy_name, strategy = choice
        if not agent.spend(strategy.cost_per_action, strategy_name):
            return

        # Sarah performs action and updates her trust score
        success = True # Placeholder for actual action result logic
        agent.record_action_result(strategy_name, success, reward=0.0)
        
        # Report to global colony stats
        self.colony.record_agent_action(agent_id, 0.0, strategy.cost_per_action, 1 if success else 0, 1)
        
        # Update your Vercel/Dashboard Trust Score
        self.dashboard.update_trust_metrics(agent_id, value_provided=success)

    def run_colony_cycle(self):
        """Run one action cycle for all agents"""
        for agent_id in list(self.colony.agents.keys()):
            self.execute_agent_action(agent_id)
        self.check_reproductions()

    def check_reproductions(self):
        """Check all agents for reproduction eligibility"""
        reproductions = self.colony.run_reproduction_cycle()
        if reproductions > 0:
            logger.info(f"🎉 {reproductions} new agent(s) born!")

    def save_all_states(self):
        """Save state to the Railway Volume"""
        self.colony.save_colony_state('data')

    @staticmethod
    def load_colony(directory: str = 'data') -> 'ColonyOrchestrator':
        """Safely reloads the colony after a Railway restart"""
        try:
            orchestrator = ColonyOrchestrator.__new__(ColonyOrchestrator)
            orchestrator.colony = AgentColony.load_colony_state(directory)
            orchestrator.dashboard = OrchestrationDashboard()
            orchestrator.reddit_monitor = RedditMonitor()
            orchestrator.twitter_monitor = TwitterMonitor()
            orchestrator._setup_schedule()
            return orchestrator
        except Exception as e:
            logger.error(f"Failed to load colony: {e}. Starting fresh.")
            return ColonyOrchestrator()

def main():
    # Railway Entry Point
    initial_balance = float(os.getenv('INITIAL_BALANCE', '50.0'))
    
    if os.path.exists('data/genealogy.json'):
        logger.info("Found existing colony data. Loading...")
        orchestrator = ColonyOrchestrator.load_colony('data')
    else:
        logger.info("No existing data. Creating founding agent...")
        orchestrator = ColonyOrchestrator(initial_agent_id="sarah_001", initial_balance=initial_balance)
    
    # Keep the process alive for Railway
    while True:
        schedule.run_pending()
        orchestrator.run_colony_cycle()
        time.sleep(60)

if __name__ == "__main__":
    main()
