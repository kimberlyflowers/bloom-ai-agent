"""Swarm Coordination - Multi-agent campaign coordination"""
import logging
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class SwarmCampaign:
    """Coordinated multi-agent campaign"""
    campaign_id: str
    goal: str
    total_budget: float
    start_date: datetime
    agent_assignments: Dict[str, dict]
    performance: Dict = None

class SwarmCoordinator:
    """Coordinate swarms of agents for complex campaigns"""

    def __init__(self):
        self.active_campaigns: Dict[str, SwarmCampaign] = {}
        self.lead_registry: set = set()  # Avoid duplicate outreach

    def create_campaign(self, campaign_id: str, goal: str, budget: float,
                       colony) -> SwarmCampaign:
        """Create coordinated campaign"""
        # Assign agents based on specialization
        assignments = {}
        budget_per_agent = budget / len(colony.agents)

        for agent_id, agent in colony.agents.items():
            spec = str(agent.specialization)
            assignments[agent_id] = {
                'role': spec,
                'budget': budget_per_agent,
                'status': 'assigned'
            }

        campaign = SwarmCampaign(
            campaign_id=campaign_id,
            goal=goal,
            total_budget=budget,
            start_date=datetime.now(),
            agent_assignments=assignments
        )

        self.active_campaigns[campaign_id] = campaign
        logger.info(f"Campaign '{goal}' created with {len(assignments)} agents")
        return campaign

    def claim_lead(self, lead_id: str, agent_id: str) -> bool:
        """Claim a lead to avoid duplicate outreach"""
        if lead_id in self.lead_registry:
            logger.warning(f"Lead {lead_id} already claimed")
            return False
        self.lead_registry.add(lead_id)
        logger.info(f"Lead {lead_id} claimed by {agent_id}")
        return True

    def reallocate_budget(self, campaign_id: str, performance_data: Dict):
        """Dynamically reallocate budget based on performance"""
        campaign = self.active_campaigns[campaign_id]

        # Find best performing agents
        sorted_agents = sorted(
            performance_data.items(),
            key=lambda x: x[1]['roi'],
            reverse=True
        )

        # Shift 30% of budget to top performers
        reallocation = campaign.total_budget * 0.3
        top_agents = sorted_agents[:len(sorted_agents)//3]

        for agent_id, _ in top_agents:
            campaign.agent_assignments[agent_id]['budget'] += reallocation / len(top_agents)

        logger.info(f"Reallocated ${reallocation} to {len(top_agents)} top performers")
