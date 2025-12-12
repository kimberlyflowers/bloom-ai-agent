"""
Orchestration & Command Center - System #22

Central command for managing hundreds of AI agents with:
- Trust-based metrics (not just revenue!)
- Product feedback loops (agents → product intelligence)
- Agent performance tracking
- Community health monitoring
- Feature request intelligence
- Friend Test failure analysis
- Real-time dashboard
- Resource management

Manage 100+ agents efficiently while maintaining quality and trust!
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from pathlib import Path
import json


# ============================================================================
# CONFIGURATION
# ============================================================================

ORCHESTRATION_DIR = Path("data/orchestration")
ORCHESTRATION_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# METRICS & TRACKING
# ============================================================================

class MetricType(Enum):
    """Types of metrics we track"""
    # Trust-based metrics (NEW!)
    TRUST_SCORE = "trust_score"
    COMMUNITY_REPUTATION = "community_reputation"
    FRIEND_TEST_PASS_RATE = "friend_test_pass_rate"
    VALUE_PROVIDED = "value_provided"
    UPVOTE_RATIO = "upvote_ratio"
    ENGAGEMENT_QUALITY = "engagement_quality"

    # Traditional metrics
    REVENUE = "revenue"
    CONVERSIONS = "conversions"
    INTERACTIONS = "interactions"

    # Product feedback metrics
    FEATURE_REQUESTS = "feature_requests"
    FRIEND_TEST_FAILURES = "friend_test_failures"
    COMPETITOR_MENTIONS = "competitor_mentions"
    PRODUCT_GAPS = "product_gaps"


@dataclass
class AgentMetrics:
    """Complete metrics for an agent"""
    agent_id: str
    agent_name: str

    # Trust-Based Metrics (PRIMARY!)
    trust_score: float = 50.0  # 0-100
    community_reputation: Dict[str, int] = field(default_factory=dict)  # {"reddit": 850, "linkedin": 1200}
    friend_test_pass_rate: float = 0.0  # % of times agent could recommend BLOOM
    value_provided_count: int = 0  # Helpful interactions
    upvote_ratio: float = 0.0  # On platforms that have voting
    engagement_quality: float = 50.0  # 0-100, how meaningful are responses

    # Traditional Metrics (SECONDARY!)
    revenue_generated: float = 0.0
    conversions: int = 0
    total_interactions: int = 0

    # Product Intelligence
    feature_requests_logged: int = 0
    friend_test_failures: int = 0
    competitor_intel_reports: int = 0

    # Health Indicators
    reputation_trend: str = "stable"  # "growing", "stable", "declining"
    community_health: str = "healthy"  # "healthy", "warning", "critical"
    burnout_risk: str = "low"  # "low", "medium", "high"

    # Time-based
    last_active: Optional[datetime] = None
    active_days: int = 0


@dataclass
class ProductIntelligence:
    """Intelligence gathered from agent conversations"""
    intelligence_id: str
    type: str  # "feature_request", "friend_test_failure", "competitor_mention", "product_gap"

    # Details
    description: str
    agent_id: str
    prospect_context: str
    date_reported: datetime = field(default_factory=datetime.utcnow)

    # Business impact
    deals_affected: int = 0
    revenue_at_risk: float = 0.0

    # Urgency
    priority: str = "medium"  # "low", "medium", "high", "critical"
    frequency: int = 1  # How many times reported

    # Resolution
    status: str = "new"  # "new", "acknowledged", "in_progress", "shipped", "wont_fix"
    product_team_notes: str = ""


@dataclass
class FeatureRequest:
    """Specific feature request from agents"""
    feature_id: str
    feature_name: str
    description: str

    # Demand
    requested_by: List[str] = field(default_factory=list)  # agent_ids
    request_count: int = 0
    prospect_count: int = 0  # How many prospects asked

    # Impact
    deals_blocked: int = 0  # Lost deals due to missing feature
    revenue_blocked: float = 0.0
    friend_test_failures: int = 0  # Times agents couldn't recommend due to this

    # Competitive
    competitors_have_it: List[str] = field(default_factory=list)

    # Status
    priority: str = "medium"
    status: str = "new"
    estimated_value: float = 0.0  # Revenue unlock if built


# ============================================================================
# ORCHESTRATION DASHBOARD
# ============================================================================

class OrchestrationDashboard:
    """
    Central command center for all agents

    Manage hundreds of agents efficiently!
    """

    def __init__(self):
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.product_intelligence: Dict[str, ProductIntelligence] = {}
        self.feature_requests: Dict[str, FeatureRequest] = {}

        # Real-time tracking
        self.active_agents: List[str] = []
        self.agents_needing_attention: List[str] = []
        self.critical_alerts: List[Dict] = []

        # Content approval system (NEW for command center!)
        self.pending_approvals: Dict[str, Dict] = {}  # content_id -> content data
        self.approved_content: Dict[str, Dict] = {}   # content_id -> content data
        self.rejected_content: Dict[str, Dict] = {}   # content_id -> content data

    def register_agent(self, agent_id: str, agent_name: str) -> AgentMetrics:
        """Register new agent for tracking"""
        metrics = AgentMetrics(
            agent_id=agent_id,
            agent_name=agent_name
        )

        self.agent_metrics[agent_id] = metrics
        print(f"✅ Registered agent for orchestration: {agent_name}")

        return metrics

    # ========================================================================
    # CONTENT APPROVAL SYSTEM (NEW for command center!)
    # ========================================================================

    def submit_content_for_approval(self, content: Dict) -> str:
        """
        Submit content for approval (called by agents)

        Args:
            content: Dict with:
                - agent_id: Agent who created it
                - content_type: "video", "image", "post", etc.
                - title: Content title
                - video_path: Path to video file (if video)
                - thumbnail_path: Path to thumbnail (if video)
                - script: Script text (if video)
                - caption: Caption text
                - platform: Target platform
                - ... other metadata

        Returns:
            content_id: Unique ID for this submission
        """
        import secrets
        content_id = f"content_{secrets.token_urlsafe(8)}"

        # Add metadata
        content["content_id"] = content_id
        content["status"] = "pending"
        content["submitted_at"] = datetime.utcnow().isoformat()

        # Add to pending approvals
        self.pending_approvals[content_id] = content

        print(f"📥 Content submitted for approval: {content.get('title', 'untitled')} (ID: {content_id})")

        return content_id

    def get_pending_approvals(self) -> List[Dict]:
        """Get all pending approvals"""
        return list(self.pending_approvals.values())

    def get_all_agents_data(self) -> Dict[str, Dict]:
        """Get all agent data for dashboard"""
        agents_data = {}

        for agent_id, metrics in self.agent_metrics.items():
            # Get current task (if any)
            current_task = "Idle"
            if agent_id in self.active_agents:
                current_task = "Working"

            # Count pending approvals for this agent
            pending_count = len([
                c for c in self.pending_approvals.values()
                if c.get("agent_id") == agent_id
            ])

            agents_data[agent_id] = {
                "agent_id": agent_id,
                "name": metrics.agent_name,
                "status": "active" if agent_id in self.active_agents else "idle",
                "trust_score": metrics.trust_score,
                "current_task": current_task,
                "pending_approvals": pending_count,
                "total_interactions": metrics.total_interactions,
                "revenue_generated": metrics.revenue_generated,
                "friend_test_pass_rate": metrics.friend_test_pass_rate
            }

        return agents_data

    async def approve_content(self, content_id: str, feedback: str = "") -> bool:
        """
        Approve content

        Args:
            content_id: Content ID
            feedback: Optional feedback/notes

        Returns:
            True if approved, False if not found
        """
        if content_id not in self.pending_approvals:
            print(f"⚠️ Content not found: {content_id}")
            return False

        # Move from pending to approved
        content = self.pending_approvals.pop(content_id)
        content["status"] = "approved"
        content["approved_at"] = datetime.utcnow().isoformat()
        content["feedback"] = feedback

        self.approved_content[content_id] = content

        print(f"✅ Content approved: {content.get('title', 'untitled')}")

        return True

    async def reject_content(self, content_id: str, feedback: str = "Please make changes") -> bool:
        """
        Reject content with feedback

        Args:
            content_id: Content ID
            feedback: Feedback for agent

        Returns:
            True if rejected, False if not found
        """
        if content_id not in self.pending_approvals:
            print(f"⚠️ Content not found: {content_id}")
            return False

        # Move from pending to rejected
        content = self.pending_approvals.pop(content_id)
        content["status"] = "rejected"
        content["rejected_at"] = datetime.utcnow().isoformat()
        content["feedback"] = feedback

        self.rejected_content[content_id] = content

        print(f"❌ Content rejected: {content.get('title', 'untitled')}")
        print(f"   Feedback: {feedback}")

        return True

    # ========================================================================
    # END CONTENT APPROVAL SYSTEM
    # ========================================================================

    def update_trust_metrics(
        self,
        agent_id: str,
        trust_score: Optional[float] = None,
        community_reputation: Optional[Dict[str, int]] = None,
        friend_test_result: Optional[bool] = None,
        value_provided: bool = False,
        upvote_ratio: Optional[float] = None
    ):
        """Update trust-based metrics for agent"""
        if agent_id not in self.agent_metrics:
            return

        metrics = self.agent_metrics[agent_id]

        if trust_score is not None:
            metrics.trust_score = trust_score

        if community_reputation:
            metrics.community_reputation.update(community_reputation)

        if friend_test_result is not None:
            # Calculate pass rate
            total_tests = metrics.friend_test_failures + (metrics.conversions * 2)  # Rough estimate
            if friend_test_result:
                metrics.friend_test_pass_rate = ((total_tests - metrics.friend_test_failures) / max(total_tests, 1)) * 100
            else:
                metrics.friend_test_failures += 1
                metrics.friend_test_pass_rate = ((total_tests - metrics.friend_test_failures) / max(total_tests + 1, 1)) * 100

        if value_provided:
            metrics.value_provided_count += 1

        if upvote_ratio is not None:
            metrics.upvote_ratio = upvote_ratio

    def log_product_intelligence(
        self,
        agent_id: str,
        type: str,
        description: str,
        prospect_context: str,
        deals_affected: int = 0,
        revenue_at_risk: float = 0.0,
        priority: str = "medium"
    ) -> ProductIntelligence:
        """Log intelligence gathered from conversations"""
        import secrets

        intel_id = f"intel_{secrets.token_urlsafe(8)}"

        intel = ProductIntelligence(
            intelligence_id=intel_id,
            type=type,
            description=description,
            agent_id=agent_id,
            prospect_context=prospect_context,
            deals_affected=deals_affected,
            revenue_at_risk=revenue_at_risk,
            priority=priority
        )

        self.product_intelligence[intel_id] = intel

        # Update agent metrics
        if agent_id in self.agent_metrics:
            if type == "feature_request":
                self.agent_metrics[agent_id].feature_requests_logged += 1
            elif type == "friend_test_failure":
                self.agent_metrics[agent_id].friend_test_failures += 1
            elif type == "competitor_mention":
                self.agent_metrics[agent_id].competitor_intel_reports += 1

        print(f"📊 Intelligence logged: {type} from {agent_id}")

        return intel

    def request_feature(
        self,
        agent_id: str,
        feature_name: str,
        description: str,
        prospect_asked: bool = True,
        deal_blocked: bool = False,
        revenue_blocked: float = 0.0
    ) -> FeatureRequest:
        """Agent requests a feature based on prospect conversations"""

        # Find existing request or create new
        feature_id = None
        for fid, freq in self.feature_requests.items():
            if freq.feature_name.lower() == feature_name.lower():
                feature_id = fid
                break

        if feature_id:
            # Update existing request
            freq = self.feature_requests[feature_id]
            if agent_id not in freq.requested_by:
                freq.requested_by.append(agent_id)
            freq.request_count += 1
            if prospect_asked:
                freq.prospect_count += 1
            if deal_blocked:
                freq.deals_blocked += 1
                freq.revenue_blocked += revenue_blocked
                freq.friend_test_failures += 1

            print(f"📈 Feature request updated: {feature_name} (now {freq.request_count} requests)")
        else:
            # Create new request
            import secrets
            feature_id = f"feature_{secrets.token_urlsafe(8)}"

            freq = FeatureRequest(
                feature_id=feature_id,
                feature_name=feature_name,
                description=description,
                requested_by=[agent_id],
                request_count=1,
                prospect_count=1 if prospect_asked else 0,
                deals_blocked=1 if deal_blocked else 0,
                revenue_blocked=revenue_blocked if deal_blocked else 0.0,
                friend_test_failures=1 if deal_blocked else 0
            )

            self.feature_requests[feature_id] = freq
            print(f"🆕 New feature request: {feature_name}")

        # Log intelligence
        self.log_product_intelligence(
            agent_id=agent_id,
            type="feature_request",
            description=f"Feature requested: {feature_name}. {description}",
            prospect_context=f"Prospect asked: {prospect_asked}, Deal blocked: {deal_blocked}",
            deals_affected=1 if deal_blocked else 0,
            revenue_at_risk=revenue_blocked,
            priority="high" if deal_blocked else "medium"
        )

        return self.feature_requests[feature_id]

    def get_top_feature_requests(self, limit: int = 10) -> List[FeatureRequest]:
        """Get top feature requests by impact"""
        all_requests = list(self.feature_requests.values())

        # Sort by revenue blocked, then request count
        all_requests.sort(
            key=lambda f: (f.revenue_blocked, f.request_count, f.prospect_count),
            reverse=True
        )

        return all_requests[:limit]

    def get_agent_leaderboard(self, metric: str = "trust_score", limit: int = 10) -> List[AgentMetrics]:
        """Get top performing agents"""
        all_metrics = list(self.agent_metrics.values())

        if metric == "trust_score":
            all_metrics.sort(key=lambda m: m.trust_score, reverse=True)
        elif metric == "revenue":
            all_metrics.sort(key=lambda m: m.revenue_generated, reverse=True)
        elif metric == "friend_test_pass_rate":
            all_metrics.sort(key=lambda m: m.friend_test_pass_rate, reverse=True)
        elif metric == "value_provided":
            all_metrics.sort(key=lambda m: m.value_provided_count, reverse=True)

        return all_metrics[:limit]

    def get_agents_needing_attention(self) -> List[Dict]:
        """Get agents that need intervention"""
        needs_attention = []

        for agent_id, metrics in self.agent_metrics.items():
            issues = []
            severity = "info"

            # Check trust score
            if metrics.trust_score < 40:
                issues.append("Low trust score")
                severity = "critical"

            # Check community health
            if metrics.community_health == "critical":
                issues.append("Community health critical")
                severity = "critical"
            elif metrics.community_health == "warning":
                issues.append("Community health warning")
                if severity != "critical":
                    severity = "warning"

            # Check Friend Test pass rate
            if metrics.friend_test_pass_rate < 50 and metrics.total_interactions > 10:
                issues.append(f"Low Friend Test pass rate ({metrics.friend_test_pass_rate:.0f}%)")
                if severity == "info":
                    severity = "warning"

            # Check burnout
            if metrics.burnout_risk == "high":
                issues.append("High burnout risk")
                if severity == "info":
                    severity = "warning"

            # Check reputation trend
            if metrics.reputation_trend == "declining":
                issues.append("Reputation declining")
                if severity == "info":
                    severity = "warning"

            if issues:
                needs_attention.append({
                    "agent_id": agent_id,
                    "agent_name": metrics.agent_name,
                    "issues": issues,
                    "severity": severity,
                    "metrics": metrics
                })

        # Sort by severity
        severity_order = {"critical": 0, "warning": 1, "info": 2}
        needs_attention.sort(key=lambda a: severity_order.get(a["severity"], 3))

        return needs_attention

    def get_dashboard_summary(self) -> str:
        """Get human-readable dashboard summary"""
        summary = f"\n{'='*80}\n"
        summary += "ORCHESTRATION COMMAND CENTER\n"
        summary += f"{'='*80}\n\n"

        # Overview
        total_agents = len(self.agent_metrics)
        active_agents = len([m for m in self.agent_metrics.values() if m.last_active and (datetime.utcnow() - m.last_active).days < 1])

        summary += f"📊 OVERVIEW:\n"
        summary += f"   Total Agents: {total_agents}\n"
        summary += f"   Active (24h): {active_agents}\n"
        summary += f"   Feature Requests: {len(self.feature_requests)}\n"
        summary += f"   Intelligence Reports: {len(self.product_intelligence)}\n"

        # Trust Metrics (PRIMARY!)
        avg_trust = sum(m.trust_score for m in self.agent_metrics.values()) / max(len(self.agent_metrics), 1)
        avg_friend_test = sum(m.friend_test_pass_rate for m in self.agent_metrics.values()) / max(len(self.agent_metrics), 1)
        total_value = sum(m.value_provided_count for m in self.agent_metrics.values())

        summary += f"\n✨ TRUST METRICS (PRIMARY):\n"
        summary += f"   Average Trust Score: {avg_trust:.1f}/100\n"
        summary += f"   Average Friend Test Pass Rate: {avg_friend_test:.1f}%\n"
        summary += f"   Total Value Provided: {total_value:,} helpful interactions\n"

        # Traditional Metrics (SECONDARY!)
        total_revenue = sum(m.revenue_generated for m in self.agent_metrics.values())
        total_conversions = sum(m.conversions for m in self.agent_metrics.values())

        summary += f"\n💰 BUSINESS METRICS (SECONDARY):\n"
        summary += f"   Total Revenue: ${total_revenue:,.2f}\n"
        summary += f"   Total Conversions: {total_conversions}\n"

        # Top Performers
        summary += f"\n🏆 TOP PERFORMERS (by Trust Score):\n"
        top_agents = self.get_agent_leaderboard("trust_score", limit=5)
        for i, metrics in enumerate(top_agents, 1):
            summary += f"   {i}. {metrics.agent_name}\n"
            summary += f"      Trust: {metrics.trust_score:.0f}/100 | Friend Test: {metrics.friend_test_pass_rate:.0f}% | Revenue: ${metrics.revenue_generated:,.0f}\n"

        # Top Feature Requests
        summary += f"\n🔥 TOP FEATURE REQUESTS:\n"
        top_features = self.get_top_feature_requests(limit=5)
        for i, freq in enumerate(top_features, 1):
            summary += f"   {i}. {freq.feature_name}\n"
            summary += f"      Requests: {freq.request_count} | Prospects: {freq.prospect_count} | Revenue Blocked: ${freq.revenue_blocked:,.0f}\n"

        # Agents Needing Attention
        needs_attention = self.get_agents_needing_attention()
        if needs_attention:
            summary += f"\n⚠️  AGENTS NEEDING ATTENTION ({len(needs_attention)}):\n"
            for agent_alert in needs_attention[:3]:
                summary += f"   • {agent_alert['agent_name']} [{agent_alert['severity'].upper()}]\n"
                for issue in agent_alert['issues']:
                    summary += f"     - {issue}\n"

        summary += f"\n{'='*80}\n"

        return summary

    def generate_product_intelligence_report(self) -> str:
        """Generate report for product team"""
        report = f"\n{'='*80}\n"
        report += "PRODUCT INTELLIGENCE REPORT\n"
        report += f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
        report += f"{'='*80}\n\n"

        # Feature Requests by Priority
        report += "🔥 TOP FEATURE REQUESTS:\n"
        report += f"{'='*80}\n\n"

        top_features = self.get_top_feature_requests(limit=10)
        for i, freq in enumerate(top_features, 1):
            report += f"{i}. {freq.feature_name}\n"
            report += f"   Description: {freq.description}\n"
            report += f"   Requested by: {len(freq.requested_by)} agents\n"
            report += f"   Total requests: {freq.request_count}\n"
            report += f"   Prospects asking: {freq.prospect_count}\n"
            report += f"   Deals blocked: {freq.deals_blocked}\n"
            report += f"   Revenue at risk: ${freq.revenue_blocked:,.2f}\n"
            report += f"   Friend Test failures: {freq.friend_test_failures}\n"
            if freq.competitors_have_it:
                report += f"   Competitors have it: {', '.join(freq.competitors_have_it)}\n"
            report += f"   Priority: {freq.priority.upper()}\n"
            report += f"   Status: {freq.status}\n\n"

        # Friend Test Failure Analysis
        total_failures = sum(m.friend_test_failures for m in self.agent_metrics.values())
        report += f"\n📉 FRIEND TEST FAILURES:\n"
        report += f"{'='*80}\n\n"
        report += f"Total failures: {total_failures}\n"
        report += f"Primary reasons:\n"

        # Top reasons from intelligence
        failure_intel = [i for i in self.product_intelligence.values() if i.type == "friend_test_failure"]
        report += f"   - {len(failure_intel)} detailed failure reports\n"
        report += f"   - Review individual reports for specific context\n\n"

        # Competitive Intelligence
        competitor_intel = [i for i in self.product_intelligence.values() if i.type == "competitor_mention"]
        report += f"\n🎯 COMPETITIVE INTELLIGENCE:\n"
        report += f"{'='*80}\n\n"
        report += f"Competitor mentions: {len(competitor_intel)}\n"
        report += f"Review these reports to understand why prospects choose competitors\n\n"

        # Revenue Impact Summary
        total_revenue_at_risk = sum(freq.revenue_blocked for freq in self.feature_requests.values())
        report += f"\n💰 REVENUE IMPACT:\n"
        report += f"{'='*80}\n\n"
        report += f"Total revenue blocked by missing features: ${total_revenue_at_risk:,.2f}\n"
        report += f"Estimated value of top 5 features: ${sum(f.revenue_blocked for f in top_features[:5]):,.2f}\n\n"

        report += f"{'='*80}\n"
        report += "END OF REPORT\n"
        report += f"{'='*80}\n"

        return report


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print(" " * 10 + "🎛️  ORCHESTRATION COMMAND CENTER DEMO")
    print("=" * 80)

    print("\n🎯 What This System Does:")
    print("   • Manage 100+ agents from one place")
    print("   • Track TRUST metrics (not just revenue!)")
    print("   • Gather product intelligence from conversations")
    print("   • Identify feature requests with revenue impact")
    print("   • Monitor agent health and reputation")
    print("   • Provide actionable insights for product team")

    # Create dashboard
    dashboard = OrchestrationDashboard()

    # Register agents
    print("\n\n📋 Registering Agents...")
    dashboard.register_agent("sarah_001", "Sarah Thompson")
    dashboard.register_agent("mike_001", "Mike Chen")
    dashboard.register_agent("alex_001", "Alex Rodriguez")

    # Update trust metrics
    print("\n📊 Updating Trust Metrics...")
    dashboard.update_trust_metrics(
        "sarah_001",
        trust_score=94,
        community_reputation={"reddit": 850, "linkedin": 1200},
        friend_test_result=True,
        value_provided=True,
        upvote_ratio=0.85
    )

    dashboard.agent_metrics["sarah_001"].revenue_generated = 125000
    dashboard.agent_metrics["sarah_001"].conversions = 5
    dashboard.agent_metrics["sarah_001"].total_interactions = 250
    dashboard.agent_metrics["sarah_001"].friend_test_pass_rate = 87

    dashboard.update_trust_metrics(
        "mike_001",
        trust_score=89,
        community_reputation={"linkedin": 980},
        friend_test_result=True,
        value_provided=True
    )

    dashboard.agent_metrics["mike_001"].revenue_generated = 98000
    dashboard.agent_metrics["mike_001"].conversions = 4
    dashboard.agent_metrics["mike_001"].friend_test_pass_rate = 78

    # Log feature requests
    print("\n🔥 Logging Feature Requests...")

    dashboard.request_feature(
        agent_id="sarah_001",
        feature_name="Slack Integration",
        description="Prospects keep asking if BLOOM integrates with Slack for notifications",
        prospect_asked=True,
        deal_blocked=True,
        revenue_blocked=50000
    )

    dashboard.request_feature(
        agent_id="mike_001",
        feature_name="Slack Integration",
        description="Lost deal to competitor because they have Slack integration",
        prospect_asked=True,
        deal_blocked=True,
        revenue_blocked=75000
    )

    dashboard.request_feature(
        agent_id="alex_001",
        feature_name="Multi-language Support",
        description="EU prospects need German and French language support",
        prospect_asked=True,
        deal_blocked=True,
        revenue_blocked=120000
    )

    dashboard.request_feature(
        agent_id="sarah_001",
        feature_name="Mobile App",
        description="Several prospects asked for mobile app for on-the-go access",
        prospect_asked=True,
        deal_blocked=False
    )

    # Show dashboard
    print(dashboard.get_dashboard_summary())

    # Show product intelligence report
    print("\n\n📊 PRODUCT INTELLIGENCE REPORT:")
    print(dashboard.generate_product_intelligence_report())

    print("\n" + "=" * 80)
    print("✨ Orchestration System Complete!")
    print("\nYou can now:")
    print("   ✅ Manage 100+ agents from one dashboard")
    print("   ✅ Track trust metrics (primary!)")
    print("   ✅ Gather product intelligence")
    print("   ✅ See feature requests with revenue impact")
    print("   ✅ Monitor agent health")
    print("   ✅ Get actionable insights for product team")
    print("=" * 80)
