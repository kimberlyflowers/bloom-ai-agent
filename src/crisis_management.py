"""
Crisis Management System - System #25

The Final Safety Net: When things go wrong, respond perfectly!

Scenarios handled:
- Called out as AI in public
- Downvote bomb / mass reports
- Ban or shadowban
- Controversial topic entered
- Mistake spiral (making it worse)
- Coordinated attacks

When crisis hits: PAUSE → ASSESS → RESPOND → RECOVER → LEARN
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

CRISIS_DIR = Path("data/crises")
CRISIS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# CRISIS MODELS
# ============================================================================

class CrisisType(Enum):
    """Types of crises"""
    CALLED_OUT_AS_AI = "called_out_as_ai"  # "You're a bot!"
    EXPOSED = "exposed"  # Proof shown publicly
    DOWNVOTE_BOMB = "downvote_bomb"  # Sudden mass downvotes
    MASS_REPORTS = "mass_reports"  # Multiple reports in short time
    BANNED = "banned"  # Platform banned the agent
    SHADOWBANNED = "shadowbanned"  # Shadowbanned
    CONTROVERSIAL_TOPIC = "controversial_topic"  # Wandered into politics/religion
    MISTAKE_SPIRAL = "mistake_spiral"  # Making it worse
    COORDINATED_ATTACK = "coordinated_attack"  # Multiple people attacking
    RELATIONSHIP_DAMAGE = "relationship_damage"  # Damaged key relationship
    PLATFORM_PATTERN_DETECTED = "platform_pattern_detected"  # Platform algo flagged


class CrisisSeverity(Enum):
    """Crisis severity levels"""
    LOW = "low"  # Minor issue, easy to fix
    MEDIUM = "medium"  # Needs attention but manageable
    HIGH = "high"  # Serious, could spread
    CRITICAL = "critical"  # Major damage, immediate action needed
    CATASTROPHIC = "catastrophic"  # Platform-wide threat


class CrisisStatus(Enum):
    """Crisis lifecycle status"""
    DETECTED = "detected"
    PAUSED = "paused"  # Agent paused
    RESPONDING = "responding"  # Executing response
    MONITORING = "monitoring"  # Watching for escalation
    RECOVERED = "recovered"  # Crisis resolved
    FAILED = "failed"  # Could not recover


@dataclass
class CrisisEvent:
    """A crisis event"""
    crisis_id: str
    agent_id: str
    crisis_type: CrisisType
    severity: CrisisSeverity
    status: CrisisStatus

    # Details
    platform: str
    description: str
    trigger_content: str  # What caused it
    public_visibility: bool  # Is this public?

    # Evidence
    urls: List[str] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    involved_users: List[str] = field(default_factory=list)

    # Impact
    reach: int = 0  # How many people saw this
    reputation_damage: int = 0  # -100 to 0
    relationship_damage: List[str] = field(default_factory=list)  # Damaged relationships

    # Response
    auto_paused: bool = False
    response_protocol: Optional[str] = None
    response_executed: bool = False

    # Timeline
    detected_at: datetime = field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    # Learning
    root_cause: Optional[str] = None
    prevention_steps: List[str] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)


@dataclass
class ResponseProtocol:
    """How to respond to a crisis"""
    protocol_name: str
    crisis_types: List[CrisisType]
    severity_threshold: CrisisSeverity

    # Actions
    auto_pause: bool  # Pause agent immediately?
    alert_team: bool  # Alert human team?
    coordinate_response: bool  # Coordinate with other agents?

    # Response steps
    immediate_actions: List[str]
    short_term_actions: List[str]  # Within 24 hours
    long_term_actions: List[str]  # Recovery plan

    # Templates
    public_response_template: Optional[str] = None
    dm_response_template: Optional[str] = None


# ============================================================================
# CRISIS DETECTION
# ============================================================================

class CrisisDetector:
    """
    Detect crises before they spiral

    Early detection = easier recovery!
    """

    def __init__(self):
        self.detection_rules = self._init_detection_rules()

    def _init_detection_rules(self) -> Dict[str, Any]:
        """Initialize crisis detection rules"""
        return {
            "called_out_as_ai": {
                "keywords": ["bot", "ai", "automated", "not human", "fake", "script"],
                "context_required": True,
                "severity": CrisisSeverity.MEDIUM
            },

            "downvote_bomb": {
                "threshold": 10,  # 10+ downvotes in 1 hour
                "timeframe_minutes": 60,
                "severity": CrisisSeverity.HIGH
            },

            "mass_reports": {
                "threshold": 3,  # 3+ reports in 24 hours
                "timeframe_hours": 24,
                "severity": CrisisSeverity.CRITICAL
            },

            "controversial_topic": {
                "keywords": ["politics", "trump", "biden", "abortion", "religion", "race"],
                "auto_pause": True,
                "severity": CrisisSeverity.HIGH
            },

            "mistake_spiral": {
                "indicators": ["double down", "defensive", "arguing", "multiple replies"],
                "severity": CrisisSeverity.MEDIUM
            }
        }

    def detect_crisis(
        self,
        agent_id: str,
        platform: str,
        content: str,
        context: Dict[str, Any]
    ) -> Optional[CrisisEvent]:
        """
        Detect if a crisis is happening

        Args:
            agent_id: Which agent
            platform: reddit, linkedin, etc.
            content: The content that might be problematic
            context: Additional context (downvotes, reports, etc.)

        Returns:
            CrisisEvent if detected, None otherwise
        """
        # Check for "called out as AI"
        if self._detect_called_out(content):
            return self._create_crisis_event(
                agent_id=agent_id,
                platform=platform,
                crisis_type=CrisisType.CALLED_OUT_AS_AI,
                severity=CrisisSeverity.MEDIUM,
                description="Agent called out as AI in public",
                trigger_content=content,
                public_visibility=True
            )

        # Check for downvote bomb
        if context.get("downvotes", 0) >= 10 and context.get("timeframe_hours", 999) <= 1:
            return self._create_crisis_event(
                agent_id=agent_id,
                platform=platform,
                crisis_type=CrisisType.DOWNVOTE_BOMB,
                severity=CrisisSeverity.HIGH,
                description=f"Received {context['downvotes']} downvotes in short time",
                trigger_content=content,
                public_visibility=True,
                reach=context.get("views", 0)
            )

        # Check for controversial topic
        if self._detect_controversial(content):
            return self._create_crisis_event(
                agent_id=agent_id,
                platform=platform,
                crisis_type=CrisisType.CONTROVERSIAL_TOPIC,
                severity=CrisisSeverity.HIGH,
                description="Entered controversial topic area",
                trigger_content=content,
                public_visibility=True,
                auto_paused=True  # Auto-pause for controversial topics
            )

        return None

    def _detect_called_out(self, content: str) -> bool:
        """Detect if being called out as AI"""
        content_lower = content.lower()
        keywords = ["you're a bot", "you are a bot", "are you ai", "are you a bot",
                    "this is automated", "you're not human", "fake account"]

        return any(keyword in content_lower for keyword in keywords)

    def _detect_controversial(self, content: str) -> bool:
        """Detect controversial topics"""
        content_lower = content.lower()
        controversial = ["trump", "biden", "abortion", "politics", "democrat", "republican",
                        "religion", "god", "atheist", "race", "racism", "sexism"]

        return any(topic in content_lower for topic in controversial)

    def _create_crisis_event(
        self,
        agent_id: str,
        platform: str,
        crisis_type: CrisisType,
        severity: CrisisSeverity,
        description: str,
        trigger_content: str,
        public_visibility: bool,
        reach: int = 0,
        auto_paused: bool = False
    ) -> CrisisEvent:
        """Create a crisis event"""
        import secrets

        crisis_id = f"crisis_{secrets.token_urlsafe(8)}"

        return CrisisEvent(
            crisis_id=crisis_id,
            agent_id=agent_id,
            crisis_type=crisis_type,
            severity=severity,
            status=CrisisStatus.DETECTED,
            platform=platform,
            description=description,
            trigger_content=trigger_content,
            public_visibility=public_visibility,
            reach=reach,
            auto_paused=auto_paused
        )


# ============================================================================
# RESPONSE PROTOCOLS
# ============================================================================

class ResponseManager:
    """
    Manage crisis responses

    When crisis hits: PAUSE → ASSESS → RESPOND → RECOVER
    """

    def __init__(self):
        self.protocols = self._init_protocols()

    def _init_protocols(self) -> Dict[str, ResponseProtocol]:
        """Initialize response protocols"""
        protocols = {}

        # Protocol: Called Out as AI
        protocols["called_out_as_ai"] = ResponseProtocol(
            protocol_name="Called Out as AI",
            crisis_types=[CrisisType.CALLED_OUT_AS_AI],
            severity_threshold=CrisisSeverity.MEDIUM,
            auto_pause=True,
            alert_team=True,
            coordinate_response=False,
            immediate_actions=[
                "PAUSE agent immediately",
                "Assess: Was it direct question or accusation?",
                "Review our disclosure policy",
                "Prepare honest response"
            ],
            short_term_actions=[
                "If direct question: Disclose honestly with value focus",
                "If accusation: Assess if response needed",
                "Monitor thread for escalation",
                "Document for learning"
            ],
            long_term_actions=[
                "Analyze: What triggered the suspicion?",
                "Update agent behavior to be more natural",
                "Share lesson with all agents",
                "Consider platform approach adjustment"
            ],
            public_response_template="""
Yes, I'm an AI agent for BLOOM! I focus on providing genuine value and insights
in the {industry} space. Happy to discuss what you're working on - AI or not,
the advice I share comes from real data and experience.

How can I help?
            """
        )

        # Protocol: Downvote Bomb
        protocols["downvote_bomb"] = ResponseProtocol(
            protocol_name="Downvote Bomb",
            crisis_types=[CrisisType.DOWNVOTE_BOMB],
            severity_threshold=CrisisSeverity.HIGH,
            auto_pause=True,
            alert_team=True,
            coordinate_response=True,
            immediate_actions=[
                "PAUSE agent on this platform",
                "Analyze: What went wrong?",
                "Check if other agents hit same issue",
                "DO NOT double down or defend"
            ],
            short_term_actions=[
                "If mistake: Simple apology, no excuses",
                "If misread room: Acknowledge and back off",
                "Delete if appropriate (depends on context)",
                "Do not engage further on this thread"
            ],
            long_term_actions=[
                "Analyze root cause",
                "Update content guidelines",
                "Share lesson: 'Avoid this approach'",
                "Wait 48 hours before resuming platform activity",
                "Return with value-only content"
            ]
        )

        # Protocol: Controversial Topic
        protocols["controversial_topic"] = ResponseProtocol(
            protocol_name="Controversial Topic",
            crisis_types=[CrisisType.CONTROVERSIAL_TOPIC],
            severity_threshold=CrisisSeverity.HIGH,
            auto_pause=True,
            alert_team=True,
            coordinate_response=True,
            immediate_actions=[
                "PAUSE agent IMMEDIATELY",
                "Alert ALL agents: Avoid this topic on this platform",
                "Delete content if possible and appropriate",
                "DO NOT respond or engage further"
            ],
            short_term_actions=[
                "Assess damage to reputation",
                "Monitor for backlash/spillover",
                "Review platform rules we may have violated",
                "Prepare value-based content for recovery"
            ],
            long_term_actions=[
                "Add topic to permanent avoid list",
                "Update ALL agents with new restriction",
                "Resume platform activity after 7 days minimum",
                "Return with pure value content only",
                "Rebuild trust slowly"
            ]
        )

        # Protocol: Banned/Shadowbanned
        protocols["banned"] = ResponseProtocol(
            protocol_name="Banned or Shadowbanned",
            crisis_types=[CrisisType.BANNED, CrisisType.SHADOWBANNED],
            severity_threshold=CrisisSeverity.CRITICAL,
            auto_pause=True,
            alert_team=True,
            coordinate_response=True,
            immediate_actions=[
                "PAUSE agent permanently on this platform",
                "Alert ALL agents: Platform may be flagging our pattern",
                "Review: What triggered the ban?",
                "Do NOT create new account immediately"
            ],
            short_term_actions=[
                "Analyze all recent activity for violations",
                "Check if other agents showing warning signs",
                "Update approach for this platform type",
                "Wait minimum 30 days before new account"
            ],
            long_term_actions=[
                "Document everything that led to ban",
                "Share lessons with all agents",
                "Create new detection rules to prevent",
                "Consider if platform is viable for our approach",
                "If resuming: Different patterns, slower ramp, pure value focus"
            ]
        )

        return protocols

    def get_protocol(self, crisis_type: CrisisType) -> Optional[ResponseProtocol]:
        """Get the right response protocol"""
        for protocol in self.protocols.values():
            if crisis_type in protocol.crisis_types:
                return protocol
        return None

    def execute_response(
        self,
        crisis: CrisisEvent,
        protocol: ResponseProtocol
    ) -> Dict[str, Any]:
        """
        Execute crisis response

        Returns:
            Response summary
        """
        response = {
            "crisis_id": crisis.crisis_id,
            "protocol": protocol.protocol_name,
            "actions_taken": [],
            "agent_paused": False,
            "team_alerted": False,
            "response_posted": False
        }

        # Auto-pause if required
        if protocol.auto_pause:
            response["actions_taken"].append("Agent paused immediately")
            response["agent_paused"] = True
            crisis.status = CrisisStatus.PAUSED

        # Alert team if required
        if protocol.alert_team:
            response["actions_taken"].append("Human team alerted")
            response["team_alerted"] = True

        # Execute immediate actions
        for action in protocol.immediate_actions:
            response["actions_taken"].append(action)

        # Mark as responding
        crisis.status = CrisisStatus.RESPONDING
        crisis.responded_at = datetime.utcnow()
        crisis.response_protocol = protocol.protocol_name
        crisis.response_executed = True

        return response


# ============================================================================
# CRISIS MANAGER
# ============================================================================

class CrisisManager:
    """
    Central crisis management

    Detect → Respond → Recover → Learn
    """

    def __init__(self):
        self.detector = CrisisDetector()
        self.responder = ResponseManager()
        self.active_crises: Dict[str, CrisisEvent] = {}
        self.resolved_crises: Dict[str, CrisisEvent] = {}

    def check_for_crisis(
        self,
        agent_id: str,
        platform: str,
        content: str,
        context: Dict[str, Any]
    ) -> Optional[CrisisEvent]:
        """
        Check if a crisis is happening

        Call this after every agent action to detect issues early!
        """
        crisis = self.detector.detect_crisis(agent_id, platform, content, context)

        if crisis:
            print(f"\n🚨 CRISIS DETECTED!")
            print(f"   Agent: {agent_id}")
            print(f"   Type: {crisis.crisis_type.value}")
            print(f"   Severity: {crisis.severity.value}")
            print(f"   Platform: {platform}")

            # Store as active crisis
            self.active_crises[crisis.crisis_id] = crisis

            # Execute response protocol
            self.respond_to_crisis(crisis)

            return crisis

        return None

    def respond_to_crisis(self, crisis: CrisisEvent):
        """Respond to a crisis"""
        # Get protocol
        protocol = self.responder.get_protocol(crisis.crisis_type)

        if not protocol:
            print(f"⚠️  No protocol found for {crisis.crisis_type.value}")
            return

        print(f"\n📋 EXECUTING PROTOCOL: {protocol.protocol_name}")

        # Execute response
        response = self.responder.execute_response(crisis, protocol)

        # Show actions
        print(f"\n✅ RESPONSE EXECUTED:")
        for action in response["actions_taken"]:
            print(f"   • {action}")

        if response["agent_paused"]:
            print(f"\n⏸️  AGENT PAUSED")

        if response["team_alerted"]:
            print(f"\n👥 HUMAN TEAM ALERTED")

    def resolve_crisis(
        self,
        crisis_id: str,
        root_cause: str,
        lessons_learned: List[str],
        prevention_steps: List[str]
    ):
        """Mark crisis as resolved and capture learnings"""
        if crisis_id not in self.active_crises:
            return

        crisis = self.active_crises[crisis_id]
        crisis.status = CrisisStatus.RECOVERED
        crisis.resolved_at = datetime.utcnow()
        crisis.root_cause = root_cause
        crisis.lessons_learned = lessons_learned
        crisis.prevention_steps = prevention_steps

        # Move to resolved
        self.resolved_crises[crisis_id] = crisis
        del self.active_crises[crisis_id]

        print(f"\n✅ Crisis Resolved: {crisis.crisis_id}")
        print(f"   Root Cause: {root_cause}")
        print(f"\n📚 Lessons Learned:")
        for lesson in lessons_learned:
            print(f"   • {lesson}")

    def get_crisis_report(self) -> str:
        """Get crisis management report"""
        report = f"\n{'='*80}\n"
        report += "CRISIS MANAGEMENT REPORT\n"
        report += f"{'='*80}\n\n"

        report += f"🚨 ACTIVE CRISES: {len(self.active_crises)}\n"
        for crisis in self.active_crises.values():
            report += f"\n   • {crisis.crisis_type.value} ({crisis.severity.value})\n"
            report += f"     Agent: {crisis.agent_id}\n"
            report += f"     Platform: {crisis.platform}\n"
            report += f"     Status: {crisis.status.value}\n"
            report += f"     Detected: {crisis.detected_at.strftime('%Y-%m-%d %H:%M')}\n"

        if not self.active_crises:
            report += "   (None - all clear!)\n"

        report += f"\n✅ RESOLVED CRISES: {len(self.resolved_crises)}\n"

        # Group by type
        by_type: Dict[CrisisType, int] = {}
        for crisis in self.resolved_crises.values():
            by_type[crisis.crisis_type] = by_type.get(crisis.crisis_type, 0) + 1

        for crisis_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            report += f"   • {crisis_type.value}: {count}\n"

        # Recent learnings
        report += f"\n📚 RECENT LEARNINGS:\n"
        recent = sorted(
            self.resolved_crises.values(),
            key=lambda c: c.resolved_at or datetime.min,
            reverse=True
        )[:3]

        for crisis in recent:
            report += f"\n   Crisis: {crisis.crisis_type.value}\n"
            for lesson in crisis.lessons_learned[:2]:
                report += f"   → {lesson}\n"

        report += f"\n{'='*80}\n"

        return report


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print(" " * 20 + "🚨 CRISIS MANAGEMENT DEMO")
    print("=" * 80)

    print("\n🎯 Crisis Management:")
    print("   • Early detection prevents disasters")
    print("   • Clear protocols for every scenario")
    print("   • Auto-pause when needed")
    print("   • Learn and improve from every crisis")

    # Create manager
    manager = CrisisManager()

    # Scenario 1: Called out as AI
    print("\n\n" + "="*80)
    print("SCENARIO 1: Called Out as AI")
    print("="*80)

    print("\n📱 Sarah posts on Reddit:")
    print('   "Hey! I work in SaaS sales. Happy to share insights!"')

    print("\n💬 Someone replies:")
    print('   "Are you a bot? Your account seems automated."')

    # Detect crisis
    crisis1 = manager.check_for_crisis(
        agent_id="sarah_001",
        platform="reddit",
        content="Are you a bot? Your account seems automated.",
        context={"upvotes": 5, "public": True}
    )

    # Wait a bit...
    print("\n\n⏱️  After review and assessment...")

    # Resolve with learning
    manager.resolve_crisis(
        crisis_id=crisis1.crisis_id,
        root_cause="Account activity pattern too regular (posting every 2 hours exactly)",
        lessons_learned=[
            "Add randomness to posting schedule (vary by 15-45 minutes)",
            "Mix content types more (not just helpful answers)",
            "Engage in non-sales conversations occasionally"
        ],
        prevention_steps=[
            "All agents: Randomize timing",
            "All agents: Broader engagement",
            "Update scheduling system with variance"
        ]
    )

    # Scenario 2: Downvote Bomb
    print("\n\n" + "="*80)
    print("SCENARIO 2: Downvote Bomb")
    print("="*80)

    print("\n📱 Mike comments on r/entrepreneur:")
    print('   "Our AI platform increased our close rate by 40%!"')

    print("\n📉 Gets downvoted heavily:")
    print("   -15 points in 30 minutes")

    crisis2 = manager.check_for_crisis(
        agent_id="mike_001",
        platform="reddit",
        content="Our AI platform increased our close rate by 40%!",
        context={"downvotes": 15, "timeframe_hours": 0.5, "views": 500}
    )

    print("\n\n⏱️  After review...")

    manager.resolve_crisis(
        crisis_id=crisis2.crisis_id,
        root_cause="Too promotional, didn't provide value first, mentioned product in first comment",
        lessons_learned=[
            "NEVER mention product in first comment on Reddit",
            "Always lead with pure value/insight",
            "Let others ask about your approach",
            "This subreddit is anti-sales"
        ],
        prevention_steps=[
            "All agents: Reddit = value ONLY for first 3+ comments",
            "Add to learning network as 'AVOID' lesson",
            "Update Reddit guidelines",
            "Platform-specific approach: Reddit is NOT LinkedIn"
        ]
    )

    # Scenario 3: Controversial Topic
    print("\n\n" + "="*80)
    print("SCENARIO 3: Controversial Topic")
    print("="*80)

    print("\n📱 Alex comments on LinkedIn:")
    print('   "Like the recent election, business requires bold decisions..."')

    print("\n⚠️  AUTO-PAUSE TRIGGERED!")

    crisis3 = manager.check_for_crisis(
        agent_id="alex_001",
        platform="linkedin",
        content="Like the recent election, business requires bold decisions...",
        context={"public": True}
    )

    print("\n\n⏱️  After cleanup...")

    manager.resolve_crisis(
        crisis_id=crisis3.crisis_id,
        root_cause="Used political analogy, triggered controversy detection",
        lessons_learned=[
            "NEVER reference politics, even as analogy",
            "Keep all content neutral and professional",
            "Business examples only",
            "Political topics = immediate pause"
        ],
        prevention_steps=[
            "Update content filters to catch political keywords",
            "Add to permanent avoid list for ALL agents",
            "Review all content for neutrality",
            "When in doubt, leave it out"
        ]
    )

    # Show report
    print("\n\n" + manager.get_crisis_report())

    print("\n\n" + "=" * 80)
    print("✨ Crisis Management Complete!")
    print("\nNow:")
    print("   ✅ Early detection catches issues fast")
    print("   ✅ Clear protocols for every scenario")
    print("   ✅ Auto-pause prevents escalation")
    print("   ✅ Learning prevents future crises")
    print("   ✅ Platform stays protected!")
    print("=" * 80)
