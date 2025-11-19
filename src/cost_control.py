"""
BLOOM Cost Control System

Prevents runaway costs with:
- Budget caps per agent/user
- Real-time cost tracking
- Automatic pause when exceeded
- Predictive alerts (before overspending)
- Cost optimization recommendations
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class BudgetPeriod(Enum):
    """Budget period types"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    TOTAL = "total"  # Lifetime budget


class CostType(Enum):
    """Types of costs"""
    API_CALL = "api_call"  # Anthropic API
    PLATFORM_FEE = "platform_fee"  # Platform usage fees
    WEBHOOK_DELIVERY = "webhook_delivery"
    DATA_STORAGE = "data_storage"
    BANDWIDTH = "bandwidth"


@dataclass
class Budget:
    """Budget configuration"""
    budget_id: str
    user_id: str
    agent_id: Optional[str] = None  # None = user-level budget

    # Budget limits
    daily_limit: Optional[float] = None
    weekly_limit: Optional[float] = None
    monthly_limit: Optional[float] = None
    total_limit: Optional[float] = None

    # Current spend
    daily_spend: float = 0.0
    weekly_spend: float = 0.0
    monthly_spend: float = 0.0
    total_spend: float = 0.0

    # Reset timestamps
    daily_reset_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=1))
    weekly_reset_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(weeks=1))
    monthly_reset_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=30))

    # Alert configuration
    alert_threshold_percent: int = 80  # Alert at 80% of budget

    # Status
    is_paused: bool = False
    pause_reason: Optional[str] = None
    paused_at: Optional[datetime] = None

    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CostRecord:
    """Record of a cost"""
    cost_id: str
    user_id: str
    agent_id: Optional[str]
    cost_type: CostType
    amount: float
    currency: str = "USD"

    # Context
    description: str = ""
    metadata: Dict = field(default_factory=dict)

    # External reference
    external_transaction_id: Optional[str] = None

    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BudgetAlert:
    """Budget alert"""
    alert_id: str
    user_id: str
    agent_id: Optional[str]
    alert_type: str  # 'threshold_reached', 'budget_exceeded', 'predicted_overspend'
    severity: str  # 'info', 'warning', 'critical'
    message: str

    # Budget context
    current_spend: float
    budget_limit: float
    percent_used: float
    remaining: float

    # Prediction (for predicted_overspend)
    predicted_spend: Optional[float] = None
    predicted_date: Optional[datetime] = None

    # Status
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None

    created_at: datetime = field(default_factory=datetime.now)


class CostTracker:
    """Tracks all costs"""

    def __init__(self):
        self.costs: List[CostRecord] = []

    def record_cost(
        self,
        user_id: str,
        cost_type: CostType,
        amount: float,
        agent_id: Optional[str] = None,
        description: str = "",
        metadata: Optional[Dict] = None
    ) -> CostRecord:
        """Record a cost"""
        import secrets

        cost = CostRecord(
            cost_id=secrets.token_urlsafe(16),
            user_id=user_id,
            agent_id=agent_id,
            cost_type=cost_type,
            amount=amount,
            description=description,
            metadata=metadata or {}
        )

        self.costs.append(cost)

        logger.info(
            f"Recorded cost: ${amount:.2f} ({cost_type.value}) "
            f"for user {user_id}{f'/agent {agent_id}' if agent_id else ''}"
        )

        return cost

    def get_costs(
        self,
        user_id: str,
        agent_id: Optional[str] = None,
        cost_type: Optional[CostType] = None,
        since: Optional[datetime] = None
    ) -> List[CostRecord]:
        """Get filtered costs"""
        costs = [c for c in self.costs if c.user_id == user_id]

        if agent_id:
            costs = [c for c in costs if c.agent_id == agent_id]

        if cost_type:
            costs = [c for c in costs if c.cost_type == cost_type]

        if since:
            costs = [c for c in costs if c.timestamp >= since]

        return costs

    def calculate_total(
        self,
        user_id: str,
        agent_id: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> float:
        """Calculate total cost"""
        costs = self.get_costs(user_id, agent_id, since=since)
        return sum(c.amount for c in costs)


class BudgetManager:
    """Manages budgets and enforces limits"""

    def __init__(self, cost_tracker: CostTracker):
        self.cost_tracker = cost_tracker
        self.budgets: Dict[str, Budget] = {}  # budget_id -> Budget
        self.alerts: List[BudgetAlert] = []

    def create_budget(
        self,
        user_id: str,
        agent_id: Optional[str] = None,
        daily_limit: Optional[float] = None,
        weekly_limit: Optional[float] = None,
        monthly_limit: Optional[float] = None,
        total_limit: Optional[float] = None,
        alert_threshold_percent: int = 80
    ) -> Budget:
        """Create budget"""
        import secrets

        budget = Budget(
            budget_id=secrets.token_urlsafe(16),
            user_id=user_id,
            agent_id=agent_id,
            daily_limit=daily_limit,
            weekly_limit=weekly_limit,
            monthly_limit=monthly_limit,
            total_limit=total_limit,
            alert_threshold_percent=alert_threshold_percent
        )

        self.budgets[budget.budget_id] = budget

        scope = f"agent {agent_id}" if agent_id else "user account"
        logger.info(f"Created budget for {scope}: {budget.budget_id}")

        return budget

    def check_budget(
        self,
        user_id: str,
        agent_id: Optional[str] = None,
        cost_amount: float = 0.0
    ) -> tuple[bool, Optional[str]]:
        """
        Check if cost is within budget.

        Returns:
            (allowed: bool, reason: Optional[str])
        """
        # Find budget
        budget = self._find_budget(user_id, agent_id)

        if not budget:
            return True, None  # No budget = unlimited

        # Check if already paused
        if budget.is_paused:
            return False, f"Budget paused: {budget.pause_reason}"

        # Update current spend
        self._update_budget_spend(budget)

        # Check each period
        if budget.daily_limit:
            if budget.daily_spend + cost_amount > budget.daily_limit:
                self._pause_budget(budget, "Daily budget exceeded")
                return False, f"Daily budget exceeded (${budget.daily_limit:.2f})"

        if budget.weekly_limit:
            if budget.weekly_spend + cost_amount > budget.weekly_limit:
                self._pause_budget(budget, "Weekly budget exceeded")
                return False, f"Weekly budget exceeded (${budget.weekly_limit:.2f})"

        if budget.monthly_limit:
            if budget.monthly_spend + cost_amount > budget.monthly_limit:
                self._pause_budget(budget, "Monthly budget exceeded")
                return False, f"Monthly budget exceeded (${budget.monthly_limit:.2f})"

        if budget.total_limit:
            if budget.total_spend + cost_amount > budget.total_limit:
                self._pause_budget(budget, "Total budget exceeded")
                return False, f"Total budget exceeded (${budget.total_limit:.2f})"

        # Check for threshold alerts
        self._check_threshold_alerts(budget, cost_amount)

        return True, None

    def _find_budget(self, user_id: str, agent_id: Optional[str]) -> Optional[Budget]:
        """Find budget for user/agent"""
        # Try agent-specific budget first
        if agent_id:
            for budget in self.budgets.values():
                if budget.user_id == user_id and budget.agent_id == agent_id:
                    return budget

        # Fall back to user-level budget
        for budget in self.budgets.values():
            if budget.user_id == user_id and budget.agent_id is None:
                return budget

        return None

    def _update_budget_spend(self, budget: Budget):
        """Update budget spend from cost tracker"""
        now = datetime.now()

        # Reset if needed
        if now >= budget.daily_reset_at:
            budget.daily_spend = 0.0
            budget.daily_reset_at = now + timedelta(days=1)

        if now >= budget.weekly_reset_at:
            budget.weekly_spend = 0.0
            budget.weekly_reset_at = now + timedelta(weeks=1)

        if now >= budget.monthly_reset_at:
            budget.monthly_spend = 0.0
            budget.monthly_reset_at = now + timedelta(days=30)

        # Calculate current spend
        daily_start = now - timedelta(days=1)
        weekly_start = now - timedelta(weeks=1)
        monthly_start = now - timedelta(days=30)

        budget.daily_spend = self.cost_tracker.calculate_total(
            budget.user_id, budget.agent_id, since=daily_start
        )

        budget.weekly_spend = self.cost_tracker.calculate_total(
            budget.user_id, budget.agent_id, since=weekly_start
        )

        budget.monthly_spend = self.cost_tracker.calculate_total(
            budget.user_id, budget.agent_id, since=monthly_start
        )

        budget.total_spend = self.cost_tracker.calculate_total(
            budget.user_id, budget.agent_id
        )

    def _pause_budget(self, budget: Budget, reason: str):
        """Pause budget"""
        budget.is_paused = True
        budget.pause_reason = reason
        budget.paused_at = datetime.now()

        # Create critical alert
        self._create_alert(
            budget=budget,
            alert_type="budget_exceeded",
            severity="critical",
            message=f"Budget exceeded: {reason}. Agent automatically paused."
        )

        logger.warning(f"Budget paused: {budget.budget_id} - {reason}")

    def _check_threshold_alerts(self, budget: Budget, upcoming_cost: float):
        """Check if approaching budget limit"""
        checks = [
            ("daily", budget.daily_limit, budget.daily_spend),
            ("weekly", budget.weekly_limit, budget.weekly_spend),
            ("monthly", budget.monthly_limit, budget.monthly_spend),
            ("total", budget.total_limit, budget.total_spend)
        ]

        for period, limit, spend in checks:
            if not limit:
                continue

            projected_spend = spend + upcoming_cost
            percent_used = (projected_spend / limit) * 100

            # Alert at threshold (e.g., 80%)
            if percent_used >= budget.alert_threshold_percent and spend < limit:
                self._create_alert(
                    budget=budget,
                    alert_type="threshold_reached",
                    severity="warning",
                    message=f"{period.capitalize()} budget {percent_used:.0f}% used (${projected_spend:.2f} of ${limit:.2f})"
                )

    def _create_alert(
        self,
        budget: Budget,
        alert_type: str,
        severity: str,
        message: str
    ):
        """Create budget alert"""
        import secrets

        # Find applicable limit for context
        limit = budget.daily_limit or budget.weekly_limit or budget.monthly_limit or budget.total_limit or 0.0
        spend = budget.daily_spend or budget.weekly_spend or budget.monthly_spend or budget.total_spend

        alert = BudgetAlert(
            alert_id=secrets.token_urlsafe(16),
            user_id=budget.user_id,
            agent_id=budget.agent_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            current_spend=spend,
            budget_limit=limit,
            percent_used=(spend / limit * 100) if limit > 0 else 0.0,
            remaining=limit - spend if limit > 0 else 0.0
        )

        self.alerts.append(alert)

        logger.info(f"Budget alert created: {alert_type} - {message}")

    def predict_overspend(self, budget: Budget) -> Optional[BudgetAlert]:
        """
        Predict if budget will be exceeded based on current burn rate.

        Returns alert if overspend predicted.
        """
        # Calculate burn rate (cost per hour)
        recent_costs = self.cost_tracker.get_costs(
            budget.user_id,
            budget.agent_id,
            since=datetime.now() - timedelta(hours=24)
        )

        if not recent_costs:
            return None  # Not enough data

        total_recent = sum(c.amount for c in recent_costs)
        burn_rate_per_hour = total_recent / 24

        # Predict daily spend
        predicted_daily = burn_rate_per_hour * 24

        # Check if predicted spend exceeds limit
        if budget.daily_limit and predicted_daily > budget.daily_limit:
            hours_until_exceeded = (budget.daily_limit - budget.daily_spend) / burn_rate_per_hour

            if hours_until_exceeded < 24:  # Will exceed today
                import secrets

                alert = BudgetAlert(
                    alert_id=secrets.token_urlsafe(16),
                    user_id=budget.user_id,
                    agent_id=budget.agent_id,
                    alert_type="predicted_overspend",
                    severity="warning",
                    message=f"Predicted to exceed daily budget in {hours_until_exceeded:.1f} hours",
                    current_spend=budget.daily_spend,
                    budget_limit=budget.daily_limit,
                    percent_used=(budget.daily_spend / budget.daily_limit * 100),
                    remaining=budget.daily_limit - budget.daily_spend,
                    predicted_spend=predicted_daily,
                    predicted_date=datetime.now() + timedelta(hours=hours_until_exceeded)
                )

                self.alerts.append(alert)

                logger.warning(
                    f"Predicted overspend: {budget.budget_id} will exceed daily budget in {hours_until_exceeded:.1f}h"
                )

                return alert

        return None

    def get_budget_summary(self, user_id: str, agent_id: Optional[str] = None) -> Dict:
        """Get budget summary"""
        budget = self._find_budget(user_id, agent_id)

        if not budget:
            return {'error': 'No budget found'}

        self._update_budget_spend(budget)

        return {
            'budget_id': budget.budget_id,
            'is_paused': budget.is_paused,
            'pause_reason': budget.pause_reason,
            'daily': {
                'limit': budget.daily_limit,
                'spend': budget.daily_spend,
                'remaining': (budget.daily_limit - budget.daily_spend) if budget.daily_limit else None,
                'percent_used': (budget.daily_spend / budget.daily_limit * 100) if budget.daily_limit else 0.0
            },
            'weekly': {
                'limit': budget.weekly_limit,
                'spend': budget.weekly_spend,
                'remaining': (budget.weekly_limit - budget.weekly_spend) if budget.weekly_limit else None,
                'percent_used': (budget.weekly_spend / budget.weekly_limit * 100) if budget.weekly_limit else 0.0
            },
            'monthly': {
                'limit': budget.monthly_limit,
                'spend': budget.monthly_spend,
                'remaining': (budget.monthly_limit - budget.monthly_spend) if budget.monthly_limit else None,
                'percent_used': (budget.monthly_spend / budget.monthly_limit * 100) if budget.monthly_limit else 0.0
            },
            'total': {
                'limit': budget.total_limit,
                'spend': budget.total_spend,
                'remaining': (budget.total_limit - budget.total_spend) if budget.total_limit else None,
                'percent_used': (budget.total_spend / budget.total_limit * 100) if budget.total_limit else 0.0
            }
        }


if __name__ == "__main__":
    print("=" * 80)
    print("BLOOM COST CONTROL SYSTEM - DEMO".center(80))
    print("=" * 80)

    # Create cost tracker and budget manager
    cost_tracker = CostTracker()
    budget_manager = BudgetManager(cost_tracker)

    # Create budget
    print("\n1. CREATE BUDGET")
    print("-" * 80)

    budget = budget_manager.create_budget(
        user_id="user_123",
        agent_id="agent_alpha",
        daily_limit=100.0,
        weekly_limit=500.0,
        monthly_limit=2000.0,
        alert_threshold_percent=80
    )

    print(f"✅ Budget created: {budget.budget_id}")
    print(f"   Daily limit: ${budget.daily_limit}")
    print(f"   Weekly limit: ${budget.weekly_limit}")
    print(f"   Monthly limit: ${budget.monthly_limit}")
    print(f"   Alert threshold: {budget.alert_threshold_percent}%")

    # Simulate costs
    print("\n2. RECORD COSTS")
    print("-" * 80)

    costs = [
        (CostType.API_CALL, 15.50, "Anthropic API - 100K tokens"),
        (CostType.API_CALL, 22.30, "Anthropic API - 150K tokens"),
        (CostType.API_CALL, 18.75, "Anthropic API - 125K tokens"),
        (CostType.PLATFORM_FEE, 5.00, "Platform usage fee"),
    ]

    for cost_type, amount, description in costs:
        cost = cost_tracker.record_cost(
            user_id="user_123",
            agent_id="agent_alpha",
            cost_type=cost_type,
            amount=amount,
            description=description
        )
        print(f"✅ ${amount:.2f} - {description}")

    # Check budget
    print("\n3. CHECK BUDGET")
    print("-" * 80)

    summary = budget_manager.get_budget_summary("user_123", "agent_alpha")

    print(f"Daily budget:")
    print(f"  Spent: ${summary['daily']['spend']:.2f}")
    print(f"  Limit: ${summary['daily']['limit']:.2f}")
    print(f"  Remaining: ${summary['daily']['remaining']:.2f}")
    print(f"  Used: {summary['daily']['percent_used']:.1f}%")

    # Try to spend more
    print("\n4. CHECK IF NEXT COST ALLOWED")
    print("-" * 80)

    next_cost = 45.00
    allowed, reason = budget_manager.check_budget("user_123", "agent_alpha", next_cost)

    if allowed:
        print(f"✅ Cost ${next_cost:.2f} allowed")
    else:
        print(f"❌ Cost ${next_cost:.2f} rejected: {reason}")

    # Simulate exceeding budget
    print("\n5. SIMULATE BUDGET EXCEEDED")
    print("-" * 80)

    # Add cost that exceeds daily limit
    cost_tracker.record_cost(
        user_id="user_123",
        agent_id="agent_alpha",
        cost_type=CostType.API_CALL,
        amount=50.00,
        description="Large API call"
    )

    summary = budget_manager.get_budget_summary("user_123", "agent_alpha")
    print(f"Daily spent: ${summary['daily']['spend']:.2f} / ${summary['daily']['limit']:.2f}")
    print(f"Used: {summary['daily']['percent_used']:.1f}%")

    # Try another cost
    allowed, reason = budget_manager.check_budget("user_123", "agent_alpha", 10.00)

    if not allowed:
        print(f"❌ Budget exceeded! {reason}")
        print(f"   Budget is now paused")

    # Show alerts
    print("\n6. BUDGET ALERTS")
    print("-" * 80)

    recent_alerts = budget_manager.alerts[-3:]  # Last 3 alerts

    for alert in recent_alerts:
        severity_emoji = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'critical': '🚨'
        }

        emoji = severity_emoji.get(alert.severity, '•')
        print(f"\n{emoji} {alert.alert_type.upper()}")
        print(f"   {alert.message}")
        print(f"   Spent: ${alert.current_spend:.2f} / ${alert.budget_limit:.2f}")
        print(f"   Used: {alert.percent_used:.1f}%")

    print("\n" + "=" * 80)
    print("KEY FEATURES".center(80))
    print("=" * 80)
    print("""
    ✅ COST PROTECTION:

    1. BUDGET CAPS
       - Daily, weekly, monthly, total limits
       - Per-agent or per-user budgets
       - Automatic enforcement

    2. REAL-TIME TRACKING
       - Track all costs (API, platform, webhooks, storage)
       - Real-time spend calculations
       - Automatic period resets

    3. AUTOMATIC PAUSE
       - Pauses agent when budget exceeded
       - Prevents overspending
       - Clear pause reasons

    4. PREDICTIVE ALERTS
       - Warns before budget exceeded
       - Calculates burn rate
       - Predicts overspend timing

    5. ALERT THRESHOLDS
       - Configurable (default 80%)
       - Multiple severity levels
       - Actionable messages

    6. COST BREAKDOWN
       - By cost type (API, platform, etc.)
       - By time period
       - By agent

    💰 BUSINESS IMPACT:

    - Prevents $1,000s in unexpected costs
    - Gives users control
    - Builds trust
    - Enables risk-free trials
    - Predictable pricing

    🎯 USE CASES:

    - Set $10/day limit for new users
    - Limit experimental agents to $50
    - Cap total monthly spend at $500
    - Alert when 80% of budget used
    - Auto-pause when exceeded

    📊 RECOMMENDED DEFAULTS:

    - New users: $10/day, $50/week, $200/month
    - Established users: $100/day, $500/week, $2000/month
    - Enterprise: Custom limits
    """)
    print("=" * 80)
