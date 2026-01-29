"""
BLOOM AI Agent - Colony Orchestrator
Coordinates multiple agents with Command Center integration.
Verified for branch: claude/fix-railway-serving-Ohk5u
"""

import logging
import os
import sys
import random
import time
import json
import schedule
from datetime import datetime

# ABSOLUTE PATH PROTECTION: Re-verify pathing within the module
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# UNIVERSAL IMPORT SHIELD: Resolves the "No module named 'ai_agent'" loop
try:
    from src.ai_agent import BloomAIAgent, Specialization
    from src.agent_reproduction import AgentColony
    from src.orchestration_dashboard import OrchestrationDashboard
    from src.reddit_integration import RedditMonitor
    from src.twitter_integration import TwitterMonitor
    from src.colony_learning import ColonyLearning
except ImportError:
    # Package-level fallback for Railway local execution
    from ai_agent import BloomAIAgent, Specialization
    from agent_reproduction import AgentColony
    from orchestration_dashboard import OrchestrationDashboard
    from reddit_integration import RedditMonitor
    from twitter_integration import TwitterMonitor
    from colony_learning import ColonyLearning

logger = logging.getLogger(__name__)

class ColonyOrchestrator:
    def __init__(self, initial_agent_id: str = "sarah_001", initial_balance: float = 50.0):
        # Create directories for Railway persistence
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)

        self.colony = AgentColony()
        self.dashboard = OrchestrationDashboard()

        # Initialize Founding Agent (Sarah Rodriguez)
        founding_agent = BloomAIAgent(
            agent_id=initial_agent_id,
            initial_balance=initial_balance
        )

        self.colony.add_agent(
            agent=founding_agent,
            agent_id=initial_agent_id,
            specialization=Specialization.GENERALIST
        )

        self.reddit_monitor = RedditMonitor()
        self.twitter_monitor = TwitterMonitor()
        self.learning = ColonyLearning(colony_id="main")

        self._setup_schedule()
        logger.info(f"CORE: Colony initialized on branch fix-railway-serving. Founding Agent: {initial_agent_id}")

    def _setup_schedule(self):
        """Standardized heartbeat for Railway persistence."""
        schedule.every().hour.do(self.run_colony_cycle)
        schedule.every(6).hours.do(self.check_reproductions)
        schedule.every().hour.do(self.save_all_states)

    def execute_agent_action(self, agent_id: str):
        if agent_id not in self.colony.agents: return
        agent = self.colony.agents[agent_id]
        choice = agent.choose_next_strategy()
        if not choice: return

        strategy_name, strategy = choice
        if agent.spend(strategy.cost_per_action, strategy_name):
            # Report success and update Trust Score
            agent.record_action_result(strategy_name, True)
            self.dashboard.update_trust_metrics(agent_id, value_provided=True)

    def run_colony_cycle(self):
        logger.info(f"CYCLE: Processing actions for {len(self.colony.agents)} agents.")
        for agent_id in list(self.colony.agents.keys()):
            self.execute_agent_action(agent_id)
        self.check_reproductions()

    def check_reproductions(self):
        reproductions = self.colony.run_reproduction_cycle()
        if reproductions > 0:
            logger.info(f"EVOLUTION: {reproductions} new agents spawned.")

    def save_all_states(self):
        """Direct sync to Railway persistent volume."""
        try:
            self.colony.save_colony_state('data')
            logger.info("STORAGE: Colony state synced successfully.")
        except Exception as e:
            logger.error(f"STORAGE_ERROR: {e}")

    @staticmethod
    def load_colony(directory: str = 'data') -> 'ColonyOrchestrator':
        try:
            orchestrator = ColonyOrchestrator.__new__(ColonyOrchestrator)
            orchestrator.colony = AgentColony.load_colony_state(directory)
            orchestrator.dashboard = OrchestrationDashboard()
            orchestrator.reddit_monitor = RedditMonitor()
            orchestrator.twitter_monitor = TwitterMonitor()
            orchestrator._setup_schedule()
            return orchestrator
        except Exception as e:
            logger.warning(f"LOAD_FAILED: {e}. Starting fresh.")
            return ColonyOrchestrator()

def main():
    # Railway initialization sequence
    initial_balance = float(os.getenv('INITIAL_BALANCE', '50.0'))
    
    if os.path.exists('data/genealogy.json') and os.path.getsize('data/genealogy.json') > 0:
        logger.info("RESUME: Data found. Re-establishing colony...")
        orchestrator = ColonyOrchestrator.load_colony('data')
    else:
        logger.info("START: No data found. Initializing founding sequence...")
        orchestrator = ColonyOrchestrator(initial_agent_id="sarah_001", initial_balance=initial_balance)
    
    # Keep-Alive loop required for Railway service stability
    while True:
        schedule.run_pending()
        orchestrator.run_colony_cycle()
        time.sleep(3600) # Process cycle every hour

if __name__ == "__main__":
    main()
