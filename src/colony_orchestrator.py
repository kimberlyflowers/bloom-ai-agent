"""
BLOOM AI Agent - Colony Orchestrator
Coordinates multiple agents with reproduction capability and Command Center integration.
"""

import logging
import os
import random
import time
import json
from datetime import datetime
import schedule

# ELEVATED VIEW FIX: Use a robust universal import pattern to solve ModuleNotFoundError
try:
    # First, try relative imports (Standard for src/ package)
    from .ai_agent import BloomAIAgent, Specialization
    from .agent_reproduction import AgentColony
    from .colony_learning import ColonyLearning
    from .reddit_integration import RedditMonitor
    from .twitter_integration import TwitterMonitor
    from .orchestration_dashboard import OrchestrationDashboard
except (ImportError, ValueError):
    # Fallback: Try direct imports (Standard for root execution)
    try:
        from ai_agent import BloomAIAgent, Specialization
        from agent_reproduction import AgentColony
        from colony_learning import ColonyLearning
        from reddit_integration import RedditMonitor
        from twitter_integration import TwitterMonitor
        from orchestration_dashboard import OrchestrationDashboard
    except ImportError:
        # Last Resort: Forced absolute pathing
        from src.ai_agent import BloomAIAgent, Specialization
        from src.agent_reproduction import AgentColony
        from src.colony_learning import ColonyLearning
        from src.reddit_integration import RedditMonitor
        from src.twitter_integration import TwitterMonitor
        from src.orchestration_dashboard import OrchestrationDashboard

logger = logging.getLogger(__name__)

class ColonyOrchestrator:
    """
    Orchestrates a colony of AI agents with reproduction capability.
    """

    def __init__(self, initial_agent_id: str = "sarah_001", initial_balance: float = 50.0):
        # Create directories for Railway persistence immediately
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)

        self.colony = AgentColony()
        self.dashboard = OrchestrationDashboard()

        # Initialize Founding Agent
        founding_agent = BloomAIAgent(
            agent_id=initial_agent_id,
            initial_balance=initial_balance
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
        logger.info(f"CORE: Colony initialized with founding agent '{initial_agent_id}'")

    def _setup_schedule(self):
        schedule.every().hour.do(self.run_colony_cycle)
        schedule.every(6).hours.do(self.check_reproductions)
        schedule.every().hour.do(self.save_all_states)

    def execute_agent_action(self, agent_id: str):
        if agent_id not in self.colony.agents:
            return

        agent = self.colony.agents[agent_id]
        choice = agent.choose_next_strategy()

        if not choice:
            return

        strategy_name, strategy = choice
        if not agent.spend(strategy.cost_per_action, strategy_name):
            return

        # Execute and report
        success = True 
        agent.record_action_result(strategy_name, success)
        
        # Sync with global colony stats
        self.colony.record_agent_action(agent_id, 0.0, strategy.cost_per_action, 1 if success else 0, 1)
        
        # Push to Trust Dashboard
        self.dashboard.update_trust_metrics(agent_id, value_provided=success)

    def run_colony_cycle(self):
        logger.info(f"CYCLE: Running actions for {len(self.colony.agents)} agents...")
        for agent_id in list(self.colony.agents.keys()):
            self.execute_agent_action(agent_id)
        self.check_reproductions()

    def check_reproductions(self):
        reproductions = self.colony.run_reproduction_cycle()
        if reproductions > 0:
            logger.info(f"EVOLUTION: {reproductions} new agent(s) spawned.")

    def save_all_states(self):
        try:
            self.colony.save_colony_state('data')
            logger.info("STORAGE: All states synced to Railway volume.")
        except Exception as e:
            logger.error(f"STORAGE_ERROR: {e}")

    @staticmethod
    def load_colony(directory: str = 'data') -> 'ColonyOrchestrator':
        """Self-healing loader prevents startup crashes from missing files."""
        try:
            orchestrator = ColonyOrchestrator.__new__(ColonyOrchestrator)
            orchestrator.colony = AgentColony.load_colony_state(directory)
            orchestrator.dashboard = OrchestrationDashboard()
            orchestrator.reddit_monitor = RedditMonitor()
            orchestrator.twitter_monitor = TwitterMonitor()
            orchestrator._setup_schedule()
            return orchestrator
        except Exception as e:
            logger.warning(f"LOAD_FAILED: {e}. Orchestrating fresh start.")
            return ColonyOrchestrator()

def main():
    initial_balance = float(os.getenv('INITIAL_BALANCE', '50.0'))
    
    # Check if we have valid data to resume from
    if os.path.exists('data/genealogy.json') and os.path.getsize('data/genealogy.json') > 0:
        logger.info("RESUME: Existing genealogy found. Re-establishing colony...")
        orchestrator = ColonyOrchestrator.load_colony('data')
    else:
        logger.info("START: No valid data found. Initializing founding sequence...")
        orchestrator = ColonyOrchestrator(initial_agent_id="sarah_001", initial_balance=initial_balance)
    
    # Keep-Alive loop to prevent Railway from timing out the process
    while True:
        schedule.run_pending()
        orchestrator.run_colony_cycle()
        time.sleep(3600) 

if __name__ == "__main__":
    main()
