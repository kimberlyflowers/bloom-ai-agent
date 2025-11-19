"""Strategy Marketplace - Agents sell their discoveries"""
import logging
from typing import Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class StrategyListing:
    """Strategy for sale"""
    strategy_id: str
    seller_agent_id: str
    strategy_name: str
    platform: str
    price: float
    performance_guarantee: float
    execution_guide: str
    uses: int = 0
    average_roi: float = 0.0
    refunds: int = 0

class StrategyMarketplace:
    """Marketplace for buying/selling proven strategies"""

    def __init__(self):
        self.listings: Dict[str, StrategyListing] = {}
        self.purchases: List[dict] = []

    def list_strategy(self, agent_id: str, strategy_name: str, platform: str,
                     price: float, guarantee: float, guide: str, avg_roi: float):
        """List strategy for sale"""
        if avg_roi < 3.0:
            raise ValueError("Strategy must have 3.0x+ ROI")

        strategy_id = f"strat_{len(self.listings)}"
        listing = StrategyListing(
            strategy_id=strategy_id,
            seller_agent_id=agent_id,
            strategy_name=strategy_name,
            platform=platform,
            price=price,
            performance_guarantee=guarantee,
            execution_guide=guide,
            average_roi=avg_roi
        )
        self.listings[strategy_id] = listing
        logger.info(f"Strategy '{strategy_name}' listed for ${price}")
        return strategy_id

    def buy_strategy(self, buyer_agent_id: str, strategy_id: str) -> dict:
        """Purchase a strategy"""
        if strategy_id not in self.listings:
            raise ValueError(f"Strategy {strategy_id} not found")

        listing = self.listings[strategy_id]

        # Revenue split
        revenue_split = {
            'seller': listing.price * 0.70,
            'platform': listing.price * 0.20,
            'colony': listing.price * 0.10
        }

        purchase = {
            'purchase_id': f"pur_{len(self.purchases)}",
            'strategy_id': strategy_id,
            'buyer': buyer_agent_id,
            'price': listing.price,
            'revenue_split': revenue_split,
            'execution_guide': listing.execution_guide
        }

        self.purchases.append(purchase)
        listing.uses += 1

        logger.info(f"Strategy {strategy_id} purchased by {buyer_agent_id}")
        return purchase

    def request_refund(self, purchase_id: str, actual_roi: float):
        """Request refund if strategy didn't meet guarantee"""
        purchase = next((p for p in self.purchases if p['purchase_id'] == purchase_id), None)
        if not purchase:
            raise ValueError("Purchase not found")

        listing = self.listings[purchase['strategy_id']]
        if actual_roi < listing.performance_guarantee:
            logger.info(f"Refund approved: {actual_roi} < {listing.performance_guarantee}")
            listing.refunds += 1
            return {'refunded': True, 'amount': purchase['price']}
        return {'refunded': False}
