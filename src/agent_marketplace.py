"""Agent-as-a-Service Marketplace - Rent successful agents"""
import logging
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class AgentListing:
    """Agent listed for rent"""
    agent_id: str
    owner_user_id: str
    rental_price_per_day: float
    performance_stats: Dict
    specialization: str
    total_rentals: int = 0
    rating: float = 5.0

class AgentMarketplace:
    """Marketplace for renting successful agents"""

    def __init__(self):
        self.listings: Dict[str, AgentListing] = {}
        self.active_rentals: List[dict] = []

    def list_agent(self, agent_id: str, agent, owner_user_id: str, price: float):
        """List agent for rent (requires proven track record)"""
        # Check qualifications
        if agent.total_revenue < 100:
            raise ValueError("Agent must have $100+ revenue")
        if agent.days_active < 30:
            raise ValueError("Agent must be 30+ days old")

        listing = AgentListing(
            agent_id=agent_id,
            owner_user_id=owner_user_id,
            rental_price_per_day=price,
            performance_stats={
                'total_revenue': agent.total_revenue,
                'average_roi': self._calculate_avg_roi(agent),
                'total_conversions': agent.total_conversions
            },
            specialization=str(agent.specialization)
        )
        self.listings[agent_id] = listing
        logger.info(f"Agent {agent_id} listed at ${price}/day")

    def rent_agent(self, renter_user_id: str, agent_id: str, days: int) -> dict:
        """Rent an agent"""
        if agent_id not in self.listings:
            raise ValueError(f"Agent {agent_id} not available")

        listing = self.listings[agent_id]
        total_cost = listing.rental_price_per_day * days

        # Revenue split
        revenue_split = {
            'owner': total_cost * 0.60,
            'platform': total_cost * 0.30,
            'parent_agent': total_cost * 0.10
        }

        rental = {
            'rental_id': f"rent_{len(self.active_rentals)}",
            'agent_id': agent_id,
            'renter': renter_user_id,
            'start_date': datetime.now(),
            'end_date': datetime.now() + timedelta(days=days),
            'total_cost': total_cost,
            'revenue_split': revenue_split
        }

        self.active_rentals.append(rental)
        listing.total_rentals += 1

        logger.info(f"Agent {agent_id} rented to {renter_user_id} for {days} days")
        return rental

    def _calculate_avg_roi(self, agent) -> float:
        """Calculate agent's average ROI"""
        all_rois = []
        for strategy in agent.strategies.values():
            if strategy.roi_history:
                all_rois.extend(strategy.roi_history)
        return sum(all_rois) / len(all_rois) if all_rois else 0.0
