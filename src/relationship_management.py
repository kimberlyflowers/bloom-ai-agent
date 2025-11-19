"""
Relationship Management CRM - System #20

Track and nurture deep, lasting relationships:
- Relationship stages (Cold → Warm → Hot → Customer → Advocate)
- Personal details ("John's daughter plays soccer")
- Relationship milestones (first meeting, first win, etc.)
- Smart follow-up timing (not too pushy, not too distant)
- Celebrate their wins

Build REAL relationships, not just transactional contacts!
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

RELATIONSHIPS_DIR = Path("data/relationships")
RELATIONSHIPS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# RELATIONSHIP STAGES
# ============================================================================

class RelationshipStage(Enum):
    """Relationship progression stages"""
    COLD = "cold"  # Never interacted
    AWARE = "aware"  # They know about you/your company
    INTERESTED = "interested"  # Showed some interest
    ENGAGED = "engaged"  # Active conversation
    WARM = "warm"  # Regular communication, trust building
    HOT = "hot"  # Ready to buy/partner
    CUSTOMER = "customer"  # Active customer
    CHAMPION = "champion"  # Refers others, advocates for you
    INACTIVE = "inactive"  # Was active, now dormant
    LOST = "lost"  # Deal lost or relationship ended


class InteractionType(Enum):
    """Types of interactions"""
    LINKEDIN_CONNECTION = "linkedin_connection"
    LINKEDIN_MESSAGE = "linkedin_message"
    LINKEDIN_COMMENT = "linkedin_comment"
    EMAIL = "email"
    PHONE_CALL = "phone_call"
    MEETING = "meeting"
    DEMO = "demo"
    PROPOSAL_SENT = "proposal_sent"
    CONTRACT_SIGNED = "contract_signed"
    SOCIAL_MEDIA = "social_media"
    REFERRAL = "referral"


# ============================================================================
# PERSONAL DETAILS
# ============================================================================

@dataclass
class PersonalDetail:
    """Personal information about someone"""
    category: str  # "family", "hobbies", "career", "challenges", "goals"
    detail: str  # The actual information
    source: str  # Where we learned this
    date_learned: datetime = field(default_factory=datetime.utcnow)
    importance: int = 5  # 1-10
    verified: bool = False  # Have we confirmed this?


@dataclass
class PersonProfile:
    """Complete profile of a person"""
    person_id: str
    full_name: str
    company: str
    job_title: str
    email: str
    phone: str = ""
    linkedin_url: str = ""

    # Personal details
    personal_details: List[PersonalDetail] = field(default_factory=list)

    # Communication preferences
    preferred_contact_method: str = "email"  # "email", "linkedin", "phone"
    best_time_to_contact: str = "morning"  # "morning", "afternoon", "evening"
    response_pattern: str = "quick"  # "immediate", "quick", "slow", "inconsistent"

    # Demographics
    location: str = ""
    timezone: str = ""

    # Interests and pain points
    interests: List[str] = field(default_factory=list)
    pain_points: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)


# ============================================================================
# RELATIONSHIP TRACKING
# ============================================================================

@dataclass
class Interaction:
    """A single interaction with someone"""
    interaction_id: str
    person_id: str
    agent_id: str

    # Interaction details
    interaction_type: InteractionType
    date: datetime
    platform: str  # "linkedin", "email", "zoom", etc.

    # Content
    subject: str = ""  # Email subject, meeting topic, etc.
    summary: str = ""  # Brief summary of interaction
    sentiment: str = "neutral"  # "positive", "neutral", "negative"

    # Outcomes
    next_steps: List[str] = field(default_factory=list)
    outcome: str = ""  # "demo scheduled", "interested in pricing", etc.

    # Value
    moved_stage_forward: bool = False
    added_value: bool = True  # Did we provide value?


@dataclass
class Milestone:
    """Important milestone in relationship"""
    milestone_id: str
    person_id: str
    milestone_type: str  # "first_connection", "first_meeting", "first_win", etc.
    date: datetime
    description: str
    significance: int = 5  # 1-10, how important


@dataclass
class Relationship:
    """
    Complete relationship with a person

    Tracks everything needed to build deep, lasting connection!
    """
    relationship_id: str
    agent_id: str  # Which agent owns this relationship
    person: PersonProfile

    # Relationship status
    stage: RelationshipStage = RelationshipStage.COLD
    health_score: int = 50  # 0-100, how healthy is this relationship

    # Timing
    first_contact: Optional[datetime] = None
    last_contact: Optional[datetime] = None
    next_follow_up: Optional[datetime] = None

    # History
    interactions: List[Interaction] = field(default_factory=list)
    milestones: List[Milestone] = field(default_factory=list)

    # Metrics
    total_touchpoints: int = 0
    average_response_time: float = 0.0  # Hours
    engagement_score: int = 50  # 0-100

    # Business context
    deal_value: float = 0.0
    deal_stage: str = ""  # "prospecting", "qualifying", "proposal", "negotiation", "closed"
    probability: int = 0  # 0-100% chance of closing

    # Notes and tags
    notes: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    # Relationship characteristics
    relationship_type: str = "professional"  # "professional", "partner", "customer", "mentor"
    influence_level: str = "decision_maker"  # "influencer", "decision_maker", "champion", "user"

    def add_interaction(self, interaction: Interaction):
        """Add interaction and update metrics"""
        self.interactions.append(interaction)
        self.total_touchpoints += 1
        self.last_contact = interaction.date

        # Update health score based on interaction
        if interaction.sentiment == "positive":
            self.health_score = min(100, self.health_score + 5)
        elif interaction.sentiment == "negative":
            self.health_score = max(0, self.health_score - 10)

        # Update engagement score
        if interaction.added_value:
            self.engagement_score = min(100, self.engagement_score + 3)

    def add_milestone(self, milestone: Milestone):
        """Add milestone"""
        self.milestones.append(milestone)

        # Milestones boost health score
        self.health_score = min(100, self.health_score + (milestone.significance * 2))

    def days_since_last_contact(self) -> int:
        """Calculate days since last contact"""
        if not self.last_contact:
            return 9999
        return (datetime.utcnow() - self.last_contact).days

    def should_follow_up(self) -> bool:
        """Determine if it's time to follow up"""
        if not self.next_follow_up:
            return self.days_since_last_contact() > 7  # Default: 7 days

        return datetime.utcnow() >= self.next_follow_up


# ============================================================================
# RELATIONSHIP MANAGER
# ============================================================================

class RelationshipManager:
    """
    Manages all relationships for agents

    Ensures deep, lasting connections!
    """

    def __init__(self):
        self.relationships: Dict[str, Relationship] = {}  # relationship_id -> Relationship
        self.by_person: Dict[str, str] = {}  # person_id -> relationship_id
        self.by_agent: Dict[str, List[str]] = {}  # agent_id -> [relationship_ids]

    def create_relationship(
        self,
        agent_id: str,
        person_name: str,
        person_email: str,
        company: str = "",
        job_title: str = "",
        **kwargs
    ) -> Relationship:
        """Create new relationship"""
        import secrets

        relationship_id = f"rel_{secrets.token_urlsafe(8)}"
        person_id = f"person_{secrets.token_urlsafe(8)}"

        person = PersonProfile(
            person_id=person_id,
            full_name=person_name,
            company=company,
            job_title=job_title,
            email=person_email,
            **kwargs
        )

        relationship = Relationship(
            relationship_id=relationship_id,
            agent_id=agent_id,
            person=person,
            first_contact=datetime.utcnow()
        )

        # Store
        self.relationships[relationship_id] = relationship
        self.by_person[person_id] = relationship_id

        if agent_id not in self.by_agent:
            self.by_agent[agent_id] = []
        self.by_agent[agent_id].append(relationship_id)

        print(f"✅ Created relationship: {agent_id} → {person_name}")

        return relationship

    def add_interaction(
        self,
        relationship_id: str,
        agent_id: str,
        interaction_type: InteractionType,
        platform: str,
        subject: str = "",
        summary: str = "",
        sentiment: str = "neutral",
        outcome: str = "",
        next_steps: List[str] = None
    ) -> Interaction:
        """Log an interaction"""
        import secrets

        if relationship_id not in self.relationships:
            raise ValueError(f"Relationship not found: {relationship_id}")

        relationship = self.relationships[relationship_id]

        interaction_id = f"int_{secrets.token_urlsafe(8)}"

        interaction = Interaction(
            interaction_id=interaction_id,
            person_id=relationship.person.person_id,
            agent_id=agent_id,
            interaction_type=interaction_type,
            date=datetime.utcnow(),
            platform=platform,
            subject=subject,
            summary=summary,
            sentiment=sentiment,
            outcome=outcome,
            next_steps=next_steps or []
        )

        relationship.add_interaction(interaction)

        # Calculate next follow-up based on stage
        relationship.next_follow_up = self._calculate_next_followup(relationship)

        self._save_relationship(relationship)

        return interaction

    def add_personal_detail(
        self,
        relationship_id: str,
        category: str,
        detail: str,
        source: str,
        importance: int = 5
    ):
        """Add personal detail about the person"""
        if relationship_id not in self.relationships:
            return

        relationship = self.relationships[relationship_id]

        personal_detail = PersonalDetail(
            category=category,
            detail=detail,
            source=source,
            importance=importance
        )

        relationship.person.personal_details.append(personal_detail)

        print(f"✅ Remembered: {detail}")
        print(f"   (About: {relationship.person.full_name})")

        self._save_relationship(relationship)

    def progress_stage(
        self,
        relationship_id: str,
        new_stage: RelationshipStage,
        reason: str = ""
    ):
        """Move relationship to new stage"""
        if relationship_id not in self.relationships:
            return

        relationship = self.relationships[relationship_id]
        old_stage = relationship.stage

        relationship.stage = new_stage

        # Add milestone
        import secrets
        milestone = Milestone(
            milestone_id=f"mile_{secrets.token_urlsafe(8)}",
            person_id=relationship.person.person_id,
            milestone_type=f"progressed_to_{new_stage.value}",
            date=datetime.utcnow(),
            description=f"Moved from {old_stage.value} to {new_stage.value}. {reason}",
            significance=7
        )

        relationship.add_milestone(milestone)

        print(f"✅ Relationship progressed: {old_stage.value} → {new_stage.value}")

        self._save_relationship(relationship)

    def get_follow_ups_due(self, agent_id: str) -> List[Relationship]:
        """Get relationships that need follow-up"""
        agent_relationships = [
            self.relationships[rel_id]
            for rel_id in self.by_agent.get(agent_id, [])
        ]

        due = [rel for rel in agent_relationships if rel.should_follow_up()]

        # Sort by priority (hot leads first, then by days since contact)
        stage_priority = {
            RelationshipStage.HOT: 1,
            RelationshipStage.WARM: 2,
            RelationshipStage.ENGAGED: 3,
            RelationshipStage.INTERESTED: 4,
            RelationshipStage.AWARE: 5,
            RelationshipStage.COLD: 6
        }

        due.sort(key=lambda r: (stage_priority.get(r.stage, 10), -r.days_since_last_contact()))

        return due

    def get_relationship_summary(self, relationship_id: str) -> str:
        """Get human-readable relationship summary"""
        if relationship_id not in self.relationships:
            return "Relationship not found"

        rel = self.relationships[relationship_id]
        person = rel.person

        summary = f"\n{'='*80}\n"
        summary += f"RELATIONSHIP: {person.full_name}\n"
        summary += f"{'='*80}\n\n"

        summary += f"👤 PERSON INFO:\n"
        summary += f"   Name: {person.full_name}\n"
        summary += f"   Company: {person.company}\n"
        summary += f"   Title: {person.job_title}\n"
        summary += f"   Email: {person.email}\n"
        if person.phone:
            summary += f"   Phone: {person.phone}\n"
        if person.linkedin_url:
            summary += f"   LinkedIn: {person.linkedin_url}\n"

        summary += f"\n📊 RELATIONSHIP STATUS:\n"
        summary += f"   Stage: {rel.stage.value.upper()}\n"
        summary += f"   Health Score: {rel.health_score}/100\n"
        summary += f"   Engagement Score: {rel.engagement_score}/100\n"
        summary += f"   Days Since Last Contact: {rel.days_since_last_contact()}\n"

        if rel.next_follow_up:
            summary += f"   Next Follow-up: {rel.next_follow_up.strftime('%Y-%m-%d')}\n"

        summary += f"\n💝 PERSONAL DETAILS ({len(person.personal_details)}):\n"
        for detail in person.personal_details[:5]:
            summary += f"   • [{detail.category}] {detail.detail}\n"
            summary += f"     (Learned: {detail.source})\n"

        if len(person.personal_details) > 5:
            summary += f"   ... and {len(person.personal_details) - 5} more\n"

        summary += f"\n📅 RECENT INTERACTIONS ({len(rel.interactions)}):\n"
        for interaction in rel.interactions[-5:]:
            summary += f"   • {interaction.date.strftime('%Y-%m-%d')}: {interaction.interaction_type.value}\n"
            if interaction.summary:
                summary += f"     {interaction.summary}\n"
            summary += f"     Sentiment: {interaction.sentiment}\n"

        if rel.milestones:
            summary += f"\n🎯 MILESTONES ({len(rel.milestones)}):\n"
            for milestone in rel.milestones[-5:]:
                summary += f"   • {milestone.date.strftime('%Y-%m-%d')}: {milestone.milestone_type}\n"
                summary += f"     {milestone.description}\n"

        if rel.deal_value > 0:
            summary += f"\n💰 DEAL INFO:\n"
            summary += f"   Value: ${rel.deal_value:,.2f}\n"
            summary += f"   Stage: {rel.deal_stage}\n"
            summary += f"   Probability: {rel.probability}%\n"

        summary += f"\n{'='*80}\n"

        return summary

    def _calculate_next_followup(self, relationship: Relationship) -> datetime:
        """Calculate smart follow-up timing based on stage"""

        # Follow-up frequency by stage
        followup_days = {
            RelationshipStage.HOT: 2,  # Every 2 days
            RelationshipStage.WARM: 5,  # Every 5 days
            RelationshipStage.ENGAGED: 7,  # Weekly
            RelationshipStage.INTERESTED: 10,  # Every 10 days
            RelationshipStage.AWARE: 14,  # Every 2 weeks
            RelationshipStage.COLD: 30,  # Monthly
            RelationshipStage.CUSTOMER: 7,  # Weekly check-ins
            RelationshipStage.CHAMPION: 14,  # Bi-weekly
            RelationshipStage.INACTIVE: 30,  # Monthly re-engagement
        }

        days = followup_days.get(relationship.stage, 7)

        return datetime.utcnow() + timedelta(days=days)

    def _save_relationship(self, relationship: Relationship):
        """Save relationship to disk"""
        filepath = RELATIONSHIPS_DIR / f"{relationship.relationship_id}.json"

        data = {
            "relationship_id": relationship.relationship_id,
            "agent_id": relationship.agent_id,
            "person": {
                "person_id": relationship.person.person_id,
                "full_name": relationship.person.full_name,
                "company": relationship.person.company,
                "job_title": relationship.person.job_title,
                "email": relationship.person.email,
                "phone": relationship.person.phone,
                "personal_details": [
                    {
                        "category": d.category,
                        "detail": d.detail,
                        "source": d.source,
                        "date_learned": d.date_learned.isoformat(),
                        "importance": d.importance
                    }
                    for d in relationship.person.personal_details
                ]
            },
            "stage": relationship.stage.value,
            "health_score": relationship.health_score,
            "engagement_score": relationship.engagement_score,
            "first_contact": relationship.first_contact.isoformat() if relationship.first_contact else None,
            "last_contact": relationship.last_contact.isoformat() if relationship.last_contact else None,
            "next_follow_up": relationship.next_follow_up.isoformat() if relationship.next_follow_up else None,
            "total_touchpoints": relationship.total_touchpoints,
            "deal_value": relationship.deal_value,
            "deal_stage": relationship.deal_stage
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print(" " * 10 + "💝 RELATIONSHIP MANAGEMENT CRM DEMO")
    print("=" * 80)

    print("\n🎯 Why This Matters:")
    print("   • Build DEEP, lasting relationships")
    print("   • Remember personal details")
    print("   • Smart follow-up timing")
    print("   • Track relationship health")
    print("   • Celebrate their wins!")

    # Create manager
    manager = RelationshipManager()

    # Create relationship with John
    print("\n\n📋 Creating Relationship with John Smith...")

    relationship = manager.create_relationship(
        agent_id="sarah_001",
        person_name="John Smith",
        person_email="john.smith@bigcorp.com",
        company="BigCorp Inc.",
        job_title="VP of Sales",
        phone="+1 (555) 987-6543",
        linkedin_url="https://linkedin.com/in/johnsmith"
    )

    # Add first interaction (LinkedIn connection)
    print("\n📱 Week 1: LinkedIn Connection Request...")
    manager.add_interaction(
        relationship_id=relationship.relationship_id,
        agent_id="sarah_001",
        interaction_type=InteractionType.LINKEDIN_CONNECTION,
        platform="linkedin",
        subject="Connection request",
        summary="Sent personalized connection request highlighting shared interest in enterprise SaaS",
        sentiment="positive",
        outcome="Connection accepted within 2 hours!"
    )

    # Progress stage
    manager.progress_stage(
        relationship.relationship_id,
        RelationshipStage.AWARE,
        "Accepted LinkedIn connection"
    )

    # Add personal detail
    print("\n💝 Learned Personal Detail...")
    manager.add_personal_detail(
        relationship.relationship_id,
        category="family",
        detail="Has a daughter who plays competitive soccer",
        source="LinkedIn comment on his post",
        importance=7
    )

    manager.add_personal_detail(
        relationship.relationship_id,
        category="goals",
        detail="Wants to scale sales team from 20 to 50 reps this year",
        source="LinkedIn post about hiring",
        importance=9
    )

    # Week 2: Comment interaction
    print("\n📱 Week 2: LinkedIn Engagement...")
    manager.add_interaction(
        relationship_id=relationship.relationship_id,
        agent_id="sarah_001",
        interaction_type=InteractionType.LINKEDIN_COMMENT,
        platform="linkedin",
        subject="Comment on his post about Q4 goals",
        summary="Commented with genuine interest and value-add insight about scaling sales teams",
        sentiment="positive",
        outcome="John replied and started conversation"
    )

    manager.progress_stage(
        relationship.relationship_id,
        RelationshipStage.INTERESTED,
        "Active two-way engagement"
    )

    # Week 3: Email conversation
    print("\n📧 Week 3: Email Conversation...")
    manager.add_interaction(
        relationship_id=relationship.relationship_id,
        agent_id="sarah_001",
        interaction_type=InteractionType.EMAIL,
        platform="email",
        subject="Re: Scaling sales teams",
        summary="Shared case study of similar company that scaled from 20 to 50 reps. John very interested!",
        sentiment="positive",
        outcome="John asked for demo",
        next_steps=["Schedule demo", "Send calendar invite", "Prepare custom deck"]
    )

    manager.progress_stage(
        relationship.relationship_id,
        RelationshipStage.WARM,
        "Requested demo - strong buying signal"
    )

    # Update deal info
    relationship.deal_value = 50000
    relationship.deal_stage = "demo scheduled"
    relationship.probability = 40

    # Week 4: Demo
    print("\n🎥 Week 4: Product Demo...")
    manager.add_interaction(
        relationship_id=relationship.relationship_id,
        agent_id="sarah_001",
        interaction_type=InteractionType.DEMO,
        platform="zoom",
        subject="BigCorp - Product Demo",
        summary="Great demo! John loved the sales team scaling features. Asked detailed questions about onboarding.",
        sentiment="positive",
        outcome="Requesting proposal and pricing",
        next_steps=["Send proposal", "Schedule follow-up", "Introduce to CSM"]
    )

    manager.progress_stage(
        relationship.relationship_id,
        RelationshipStage.HOT,
        "Requested proposal after successful demo"
    )

    relationship.probability = 70

    # Show relationship summary
    print(manager.get_relationship_summary(relationship.relationship_id))

    # Check follow-ups due
    print("\n📅 Checking Follow-ups Due...")
    due = manager.get_follow_ups_due("sarah_001")
    print(f"\nRelationships needing follow-up: {len(due)}")
    for rel in due:
        print(f"   • {rel.person.full_name} ({rel.stage.value})")
        print(f"     Last contact: {rel.days_since_last_contact()} days ago")
        print(f"     Health: {rel.health_score}/100")

    print("\n\n" + "=" * 80)
    print("✨ Relationship Management Complete!")
    print("\nSarah now:")
    print("   ✅ Tracks every interaction with John")
    print("   ✅ Remembers his daughter plays soccer")
    print("   ✅ Knows his goal to scale to 50 reps")
    print("   ✅ Has smart follow-up timing")
    print("   ✅ Monitors relationship health")
    print("   ✅ Can celebrate his wins!")
    print("=" * 80)
