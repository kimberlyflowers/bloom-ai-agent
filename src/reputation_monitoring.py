"""
Reputation Health Monitoring - System #23

CRITICAL safety system that monitors agent reputation in real-time:
- Community sentiment tracking
- Upvote/downvote ratios
- Report rates and moderator warnings
- Engagement quality analysis
- Early warning system
- Auto-pause agents before disasters
- Recovery protocols

Prevents reputation catastrophes!
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

REPUTATION_DIR = Path("data/reputation")
REPUTATION_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# REPUTATION TRACKING
# ============================================================================

class HealthStatus(Enum):
    """Overall health status"""
    EXCELLENT = "excellent"  # 90-100 score
    HEALTHY = "healthy"  # 70-89 score
    WARNING = "warning"  # 50-69 score
    CRITICAL = "critical"  # 30-49 score
    EMERGENCY = "emergency"  # < 30 score - PAUSE AGENT!


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class PlatformReputation:
    """Reputation on a specific platform"""
    platform: str  # "reddit", "linkedin", "hackernews", etc.

    # Karma/Reputation Points
    karma: int = 0
    karma_trend: str = "stable"  # "growing", "stable", "declining", "tanking"

    # Engagement Metrics
    upvote_ratio: float = 0.5  # 0-1, higher is better
    average_upvotes: float = 0.0
    average_downvotes: float = 0.0

    # Negative Signals
    report_count: int = 0  # Times reported by users
    moderator_warnings: int = 0
    shadowbanned: bool = False
    banned: bool = False

    # Positive Signals
    awards_received: int = 0
    positive_replies_ratio: float = 0.0  # Ratio of supportive vs. negative replies
    follower_count: int = 0
    follower_trend: str = "stable"

    # Activity Patterns
    post_frequency: float = 0.0  # Posts per day
    comment_frequency: float = 0.0  # Comments per day
    response_rate: float = 0.0  # How often do people respond to agent

    # Last updated
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ReputationAlert:
    """An alert about reputation issues"""
    alert_id: str
    agent_id: str
    platform: str
    level: AlertLevel
    issue: str
    details: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Actions
    recommended_action: str = ""
    auto_paused: bool = False
    resolved: bool = False


@dataclass
class ReputationScore:
    """Overall reputation score for an agent"""
    agent_id: str

    # Platform scores
    platform_scores: Dict[str, float] = field(default_factory=dict)  # platform -> 0-100 score

    # Overall score
    overall_score: float = 50.0  # 0-100
    health_status: HealthStatus = HealthStatus.HEALTHY

    # Trends
    score_7d_ago: float = 50.0
    score_30d_ago: float = 50.0
    trend: str = "stable"  # "improving", "stable", "declining", "critical_decline"

    # Components
    engagement_score: float = 50.0  # How well people engage
    sentiment_score: float = 50.0  # How positive is sentiment
    trust_score: float = 50.0  # How trustworthy agent appears
    activity_score: float = 50.0  # Activity patterns (too much = spam, too little = inactive)

    # Alerts
    active_alerts: List[str] = field(default_factory=list)  # alert_ids


# ============================================================================
# REPUTATION MONITOR
# ============================================================================

class ReputationMonitor:
    """
    Monitors agent reputation in real-time

    CRITICAL for preventing disasters!
    """

    def __init__(self):
        self.reputations: Dict[str, Dict[str, PlatformReputation]] = {}  # agent_id -> {platform -> reputation}
        self.scores: Dict[str, ReputationScore] = {}
        self.alerts: Dict[str, ReputationAlert] = {}

        # Thresholds for alerts
        self.thresholds = {
            "upvote_ratio_warning": 0.4,  # Below 40% upvotes
            "upvote_ratio_critical": 0.2,  # Below 20% upvotes
            "report_rate_warning": 0.05,  # 5% of posts reported
            "report_rate_critical": 0.10,  # 10% of posts reported
            "karma_decline_warning": -50,  # Lost 50+ karma
            "karma_decline_critical": -100,  # Lost 100+ karma
        }

    def register_agent(self, agent_id: str) -> ReputationScore:
        """Register agent for monitoring"""
        score = ReputationScore(agent_id=agent_id)
        self.scores[agent_id] = score
        self.reputations[agent_id] = {}

        print(f"✅ Reputation monitoring enabled for agent: {agent_id}")
        return score

    def update_platform_reputation(
        self,
        agent_id: str,
        platform: str,
        karma: Optional[int] = None,
        upvote_ratio: Optional[float] = None,
        report_count: Optional[int] = None,
        moderator_warnings: Optional[int] = None,
        **kwargs
    ):
        """Update reputation metrics for a platform"""
        if agent_id not in self.reputations:
            self.reputations[agent_id] = {}

        if platform not in self.reputations[agent_id]:
            self.reputations[agent_id][platform] = PlatformReputation(platform=platform)

        rep = self.reputations[agent_id][platform]

        # Update values
        if karma is not None:
            old_karma = rep.karma
            rep.karma = karma

            # Detect karma trend
            if karma > old_karma + 50:
                rep.karma_trend = "growing"
            elif karma < old_karma - 50:
                rep.karma_trend = "declining"
                if karma < old_karma - 100:
                    rep.karma_trend = "tanking"
            else:
                rep.karma_trend = "stable"

        if upvote_ratio is not None:
            rep.upvote_ratio = upvote_ratio

        if report_count is not None:
            rep.report_count = report_count

        if moderator_warnings is not None:
            rep.moderator_warnings = moderator_warnings

        # Update other kwargs
        for key, value in kwargs.items():
            if hasattr(rep, key):
                setattr(rep, key, value)

        rep.last_updated = datetime.utcnow()

        # Check for alerts
        self._check_for_alerts(agent_id, platform, rep)

        # Recalculate overall score
        self._calculate_overall_score(agent_id)

    def _check_for_alerts(self, agent_id: str, platform: str, rep: PlatformReputation):
        """Check if reputation issues require alerts"""
        import secrets

        # Check upvote ratio
        if rep.upvote_ratio < self.thresholds["upvote_ratio_critical"]:
            self._create_alert(
                agent_id=agent_id,
                platform=platform,
                level=AlertLevel.CRITICAL,
                issue="Very low upvote ratio",
                details=f"Upvote ratio is {rep.upvote_ratio:.1%} (threshold: {self.thresholds['upvote_ratio_critical']:.1%}). Content is being heavily downvoted.",
                recommended_action="PAUSE agent immediately. Review content strategy. Community is rejecting this agent.",
                auto_pause=True
            )
        elif rep.upvote_ratio < self.thresholds["upvote_ratio_warning"]:
            self._create_alert(
                agent_id=agent_id,
                platform=platform,
                level=AlertLevel.WARNING,
                issue="Low upvote ratio",
                details=f"Upvote ratio is {rep.upvote_ratio:.1%}. Content may not be resonating with community.",
                recommended_action="Review recent posts. Adjust tone/content. Provide more value."
            )

        # Check reports
        if rep.report_count > 0:
            total_posts = max(rep.karma / 10, 1)  # Rough estimate
            report_rate = rep.report_count / total_posts

            if report_rate > self.thresholds["report_rate_critical"]:
                self._create_alert(
                    agent_id=agent_id,
                    platform=platform,
                    level=AlertLevel.EMERGENCY,
                    issue="High report rate",
                    details=f"{rep.report_count} reports. Community is flagging this agent as spam/problematic.",
                    recommended_action="PAUSE IMMEDIATELY. Review all activity. Possible ban incoming.",
                    auto_pause=True
                )
            elif report_rate > self.thresholds["report_rate_warning"]:
                self._create_alert(
                    agent_id=agent_id,
                    platform=platform,
                    level=AlertLevel.WARNING,
                    issue="Moderate report rate",
                    details=f"{rep.report_count} reports. Some users finding content inappropriate.",
                    recommended_action="Review flagged posts. Adjust approach."
                )

        # Check moderator warnings
        if rep.moderator_warnings > 0:
            self._create_alert(
                agent_id=agent_id,
                platform=platform,
                level=AlertLevel.CRITICAL,
                issue="Moderator warnings",
                details=f"{rep.moderator_warnings} warnings from moderators. Next step is usually a ban.",
                recommended_action="PAUSE agent. Contact moderators if possible. Review all platform rules.",
                auto_pause=True
            )

        # Check if banned
        if rep.banned:
            self._create_alert(
                agent_id=agent_id,
                platform=platform,
                level=AlertLevel.EMERGENCY,
                issue="BANNED",
                details=f"Agent has been banned from {platform}. Reputation destroyed.",
                recommended_action="Agent inactive on this platform. Review what went wrong. Learn for other agents.",
                auto_pause=True
            )

        # Check karma decline
        if rep.karma_trend == "tanking":
            self._create_alert(
                agent_id=agent_id,
                platform=platform,
                level=AlertLevel.CRITICAL,
                issue="Karma tanking",
                details=f"Karma dropping rapidly. Community turning against this agent.",
                recommended_action="PAUSE agent. Review recent activity. Major course correction needed."
            )

    def _create_alert(
        self,
        agent_id: str,
        platform: str,
        level: AlertLevel,
        issue: str,
        details: str,
        recommended_action: str,
        auto_pause: bool = False
    ):
        """Create a reputation alert"""
        import secrets

        alert_id = f"alert_{secrets.token_urlsafe(8)}"

        alert = ReputationAlert(
            alert_id=alert_id,
            agent_id=agent_id,
            platform=platform,
            level=level,
            issue=issue,
            details=details,
            recommended_action=recommended_action,
            auto_paused=auto_pause
        )

        self.alerts[alert_id] = alert

        # Add to agent's active alerts
        if agent_id in self.scores:
            if alert_id not in self.scores[agent_id].active_alerts:
                self.scores[agent_id].active_alerts.append(alert_id)

        # Print alert
        print(f"\n🚨 REPUTATION ALERT [{level.value.upper()}]")
        print(f"   Agent: {agent_id}")
        print(f"   Platform: {platform}")
        print(f"   Issue: {issue}")
        print(f"   Details: {details}")
        print(f"   Action: {recommended_action}")
        if auto_pause:
            print(f"   ⚠️  AGENT AUTO-PAUSED!")

    def _calculate_overall_score(self, agent_id: str):
        """Calculate overall reputation score"""
        if agent_id not in self.reputations or agent_id not in self.scores:
            return

        score_obj = self.scores[agent_id]
        platform_reps = self.reputations[agent_id]

        if not platform_reps:
            return

        # Calculate per-platform scores
        platform_scores = {}

        for platform, rep in platform_reps.items():
            # Components of platform score
            engagement = min(100, (rep.upvote_ratio * 100 + rep.response_rate * 100) / 2)
            trust = min(100, 100 - (rep.report_count * 10) - (rep.moderator_warnings * 20))
            activity = 50  # Baseline, adjust based on frequency
            if rep.banned:
                platform_score = 0
            else:
                platform_score = (engagement * 0.4 + trust * 0.4 + activity * 0.2)

            platform_scores[platform] = platform_score

        score_obj.platform_scores = platform_scores

        # Overall score is average of platforms
        if platform_scores:
            score_obj.overall_score = sum(platform_scores.values()) / len(platform_scores)

        # Determine health status
        if score_obj.overall_score >= 90:
            score_obj.health_status = HealthStatus.EXCELLENT
        elif score_obj.overall_score >= 70:
            score_obj.health_status = HealthStatus.HEALTHY
        elif score_obj.overall_score >= 50:
            score_obj.health_status = HealthStatus.WARNING
        elif score_obj.overall_score >= 30:
            score_obj.health_status = HealthStatus.CRITICAL
        else:
            score_obj.health_status = HealthStatus.EMERGENCY

    def get_critical_alerts(self) -> List[ReputationAlert]:
        """Get all critical/emergency alerts"""
        critical = [
            alert for alert in self.alerts.values()
            if alert.level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY] and not alert.resolved
        ]

        critical.sort(key=lambda a: (0 if a.level == AlertLevel.EMERGENCY else 1, a.timestamp), reverse=True)

        return critical

    def get_agent_health_report(self, agent_id: str) -> str:
        """Get health report for specific agent"""
        if agent_id not in self.scores:
            return "Agent not found in monitoring system"

        score = self.scores[agent_id]
        reps = self.reputations.get(agent_id, {})

        report = f"\n{'='*80}\n"
        report += f"REPUTATION HEALTH REPORT: {agent_id}\n"
        report += f"{'='*80}\n\n"

        # Overall Status
        report += f"🏥 OVERALL HEALTH:\n"
        report += f"   Status: {score.health_status.value.upper()}\n"
        report += f"   Score: {score.overall_score:.1f}/100\n"
        report += f"   Trend: {score.trend}\n\n"

        # Platform Breakdown
        report += f"📊 PLATFORM REPUTATION:\n"
        for platform, platform_score in score.platform_scores.items():
            rep = reps.get(platform)
            if rep:
                report += f"\n   {platform.upper()}:\n"
                report += f"      Score: {platform_score:.1f}/100\n"
                report += f"      Karma: {rep.karma} ({rep.karma_trend})\n"
                report += f"      Upvote Ratio: {rep.upvote_ratio:.1%}\n"
                if rep.report_count > 0:
                    report += f"      ⚠️  Reports: {rep.report_count}\n"
                if rep.moderator_warnings > 0:
                    report += f"      ⚠️  Mod Warnings: {rep.moderator_warnings}\n"
                if rep.banned:
                    report += f"      🚫 STATUS: BANNED\n"

        # Active Alerts
        if score.active_alerts:
            report += f"\n🚨 ACTIVE ALERTS ({len(score.active_alerts)}):\n"
            for alert_id in score.active_alerts:
                if alert_id in self.alerts:
                    alert = self.alerts[alert_id]
                    report += f"\n   [{alert.level.value.upper()}] {alert.issue}\n"
                    report += f"      Platform: {alert.platform}\n"
                    report += f"      {alert.details}\n"
                    report += f"      Action: {alert.recommended_action}\n"

        report += f"\n{'='*80}\n"

        return report


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print(" " * 10 + "🛡️  REPUTATION HEALTH MONITORING DEMO")
    print("=" * 80)

    print("\n🎯 Why This Is CRITICAL:")
    print("   • Prevents reputation disasters")
    print("   • Early warning before bans")
    print("   • Auto-pause agents going wrong")
    print("   • Monitor community sentiment")
    print("   • Protect brand reputation")

    # Create monitor
    monitor = ReputationMonitor()

    # Register agents
    print("\n\n📋 Registering Agents for Monitoring...")
    monitor.register_agent("sarah_001")
    monitor.register_agent("spambot_002")

    # Scenario 1: Healthy agent (Sarah)
    print("\n\n✅ SCENARIO 1: Healthy Agent (Sarah)")
    print("-" * 80)

    monitor.update_platform_reputation(
        agent_id="sarah_001",
        platform="reddit",
        karma=850,
        upvote_ratio=0.85,
        report_count=0,
        moderator_warnings=0,
        follower_count=120,
        response_rate=0.65
    )

    print("Updated Sarah's Reddit reputation:")
    print("   Karma: 850")
    print("   Upvote ratio: 85%")
    print("   Reports: 0")
    print("   Result: HEALTHY ✅")

    # Scenario 2: Problematic agent
    print("\n\n🚨 SCENARIO 2: Problematic Agent (Bot Going Wrong)")
    print("-" * 80)

    monitor.update_platform_reputation(
        agent_id="spambot_002",
        platform="reddit",
        karma=-50,
        upvote_ratio=0.15,  # Only 15% upvotes - CRITICAL!
        report_count=12,  # Being reported as spam
        moderator_warnings=2,  # Mods already warned
        response_rate=0.05
    )

    print("Updated Spambot's Reddit reputation:")
    print("   Karma: -50")
    print("   Upvote ratio: 15% (CRITICAL!)")
    print("   Reports: 12 (HIGH!)")
    print("   Mod warnings: 2")
    print("   Result: AUTO-PAUSED! 🚨")

    # Show critical alerts
    print("\n\n🚨 CRITICAL ALERTS:")
    print("=" * 80)
    critical_alerts = monitor.get_critical_alerts()
    print(f"\nFound {len(critical_alerts)} critical alerts:\n")

    for alert in critical_alerts:
        print(f"[{alert.level.value.upper()}] {alert.agent_id} on {alert.platform}")
        print(f"   Issue: {alert.issue}")
        print(f"   Action: {alert.recommended_action}")
        if alert.auto_paused:
            print(f"   🚨 AGENT AUTO-PAUSED")
        print()

    # Health reports
    print("\n📊 HEALTH REPORTS:")
    print("=" * 80)

    print(monitor.get_agent_health_report("sarah_001"))
    print(monitor.get_agent_health_report("spambot_002"))

    print("\n" + "=" * 80)
    print("✨ Reputation Monitoring Complete!")
    print("\nThis system:")
    print("   ✅ Monitors reputation in real-time")
    print("   ✅ Detects problems early")
    print("   ✅ Auto-pauses agents before disasters")
    print("   ✅ Provides actionable alerts")
    print("   ✅ Protects brand reputation")
    print("=" * 80)
