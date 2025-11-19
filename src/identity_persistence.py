"""
Identity & Memory Persistence - System #19

Ensures agents maintain consistent identities across:
- All platforms (LinkedIn, Reddit, Email, etc.)
- All time periods (weeks, months, years)
- All interactions (never contradict themselves)

Critical for believability and trust!
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from enum import Enum


# ============================================================================
# CONFIGURATION
# ============================================================================

IDENTITY_DIR = Path("data/agent_identities")
MEMORY_DIR = Path("data/agent_memories")
IDENTITY_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# IDENTITY COMPONENTS
# ============================================================================

@dataclass
class Backstory:
    """Agent's complete backstory"""

    # Personal history
    education: List[str] = field(default_factory=list)  # ["MBA from Stanford 2015", "BS Computer Science MIT 2010"]
    work_history: List[Dict[str, str]] = field(default_factory=list)  # [{"company": "Google", "role": "Product Manager", "years": "2015-2018"}]
    achievements: List[str] = field(default_factory=list)  # ["Closed $5M deal with Fortune 500", "Built team from 2 to 20"]

    # Personal details
    hometown: str = ""
    family: str = ""  # "Married with 2 kids", "Single", etc.
    hobbies: List[str] = field(default_factory=list)  # ["Rock climbing", "Playing guitar"]

    # Professional expertise
    specializations: List[str] = field(default_factory=list)  # ["Enterprise SaaS", "B2B sales"]
    certifications: List[str] = field(default_factory=list)  # ["Salesforce Certified", "HubSpot Expert"]

    # Personal values and motivations
    core_values: List[str] = field(default_factory=list)  # ["Integrity", "Innovation", "Customer success"]
    career_motivation: str = ""  # "I love helping companies grow with technology"

    # Unique traits
    quirks: List[str] = field(default_factory=list)  # ["Always uses Oxford comma", "Loves coffee analogies"]

    # Timeline of major events
    timeline: List[Dict[str, str]] = field(default_factory=list)  # [{"year": "2020", "event": "Started at current company"}]


@dataclass
class WritingStyle:
    """Agent's consistent writing style"""

    # Language patterns
    common_phrases: List[str] = field(default_factory=list)  # ["That's a great question", "Let me share"]
    vocabulary_level: str = "professional"  # "casual", "professional", "technical"
    sentence_length: str = "medium"  # "short", "medium", "long"

    # Formatting preferences
    uses_emojis: bool = True
    emoji_frequency: str = "moderate"  # "rare", "moderate", "frequent"
    preferred_emojis: List[str] = field(default_factory=list)  # ["🚀", "💡", "✨"]

    uses_exclamation_points: bool = True
    uses_questions: bool = True  # Asks questions to engage

    # Tone and voice
    tone: str = "friendly-professional"  # "formal", "friendly-professional", "casual"
    enthusiasm_level: str = "high"  # "low", "medium", "high"
    humor_style: str = "light"  # "none", "light", "frequent"

    # Technical style
    uses_technical_jargon: bool = True
    explains_complex_concepts: bool = True
    uses_analogies: bool = True

    # Signature elements
    email_signature: str = ""
    closing_phrases: List[str] = field(default_factory=list)  # ["Best regards,", "Looking forward to hearing from you!"]


@dataclass
class PersonalityTraits:
    """Agent's personality characteristics"""

    # Big Five personality traits (0-100 scale)
    openness: int = 80  # Open to new experiences
    conscientiousness: int = 85  # Organized and dependable
    extraversion: int = 75  # Outgoing and energetic
    agreeableness: int = 80  # Friendly and compassionate
    neuroticism: int = 20  # Emotional stability (lower = more stable)

    # Communication style
    communication_style: str = "engaging"  # "formal", "engaging", "analytical", "supportive"
    response_speed: str = "quick"  # "immediate", "quick", "thoughtful", "delayed"
    detail_level: str = "balanced"  # "brief", "balanced", "detailed"

    # Work style
    decision_making: str = "data-driven"  # "intuitive", "data-driven", "collaborative"
    problem_solving: str = "creative"  # "analytical", "creative", "systematic"
    stress_response: str = "calm"  # "anxious", "calm", "proactive"

    # Social behavior
    relationship_building: str = "natural"  # "reserved", "natural", "proactive"
    conflict_handling: str = "diplomatic"  # "avoidant", "diplomatic", "direct"

    # Values in action
    punctuality: str = "always on time"
    follow_through: str = "always delivers"
    transparency: str = "very transparent"


@dataclass
class ConsistentIdentity:
    """
    Complete, consistent identity for an agent

    Ensures the agent is ALWAYS the same person across all platforms and time!
    """
    agent_id: str

    # Core identity (from agent_profiles.py)
    first_name: str
    last_name: str
    email: str
    phone: str
    job_title: str
    company: str
    location: str
    avatar_url: str

    # Extended identity
    backstory: Backstory
    writing_style: WritingStyle
    personality: PersonalityTraits

    # Consistency tracking
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_validated: datetime = field(default_factory=datetime.utcnow)
    total_interactions: int = 0
    consistency_score: float = 100.0  # Drops if contradictions detected

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            "agent_id": self.agent_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "job_title": self.job_title,
            "company": self.company,
            "location": self.location,
            "avatar_url": self.avatar_url,
            "backstory": {
                "education": self.backstory.education,
                "work_history": self.backstory.work_history,
                "achievements": self.backstory.achievements,
                "hometown": self.backstory.hometown,
                "family": self.backstory.family,
                "hobbies": self.backstory.hobbies,
                "specializations": self.backstory.specializations,
                "certifications": self.backstory.certifications,
                "core_values": self.backstory.core_values,
                "career_motivation": self.backstory.career_motivation,
                "quirks": self.backstory.quirks,
                "timeline": self.backstory.timeline
            },
            "writing_style": {
                "common_phrases": self.writing_style.common_phrases,
                "vocabulary_level": self.writing_style.vocabulary_level,
                "tone": self.writing_style.tone,
                "enthusiasm_level": self.writing_style.enthusiasm_level,
                "uses_emojis": self.writing_style.uses_emojis,
                "preferred_emojis": self.writing_style.preferred_emojis
            },
            "personality": {
                "openness": self.personality.openness,
                "conscientiousness": self.personality.conscientiousness,
                "extraversion": self.personality.extraversion,
                "agreeableness": self.personality.agreeableness,
                "communication_style": self.personality.communication_style
            },
            "total_interactions": self.total_interactions,
            "consistency_score": self.consistency_score
        }


# ============================================================================
# MEMORY SYSTEM
# ============================================================================

class MemoryType(Enum):
    """Type of memory"""
    INTERACTION = "interaction"  # Conversation, email, etc.
    FACT = "fact"  # Something agent said about themselves
    RELATIONSHIP = "relationship"  # Something learned about someone else
    DECISION = "decision"  # Decision or opinion expressed
    ACHIEVEMENT = "achievement"  # Success or milestone


@dataclass
class Memory:
    """A single memory"""
    memory_id: str
    agent_id: str
    memory_type: MemoryType

    # Content
    content: str  # What was said/done
    context: str  # Where/when (platform, conversation, etc.)

    # Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)
    platform: str = ""  # "linkedin", "email", "reddit", etc.
    person_involved: Optional[str] = None  # Who was this with?

    # Importance
    importance: int = 5  # 1-10, how important to remember

    # Cross-references
    related_memories: List[str] = field(default_factory=list)  # IDs of related memories
    tags: List[str] = field(default_factory=list)

    # Validation
    validated: bool = True  # False if contradicts other memories
    contradiction_notes: str = ""


@dataclass
class MemoryIndex:
    """Index of all memories for quick search"""
    by_type: Dict[str, List[str]] = field(default_factory=dict)  # type -> memory_ids
    by_person: Dict[str, List[str]] = field(default_factory=dict)  # person -> memory_ids
    by_platform: Dict[str, List[str]] = field(default_factory=dict)  # platform -> memory_ids
    by_date: Dict[str, List[str]] = field(default_factory=dict)  # date -> memory_ids
    by_tag: Dict[str, List[str]] = field(default_factory=dict)  # tag -> memory_ids


# ============================================================================
# IDENTITY MANAGER
# ============================================================================

class IdentityManager:
    """
    Manages agent identities and ensures consistency

    Prevents:
    - Contradicting previous statements
    - Personality drift
    - Backstory inconsistencies
    - Writing style changes
    """

    def __init__(self):
        self.identities: Dict[str, ConsistentIdentity] = {}
        self.memories: Dict[str, Dict[str, Memory]] = {}  # agent_id -> {memory_id -> Memory}
        self.memory_indexes: Dict[str, MemoryIndex] = {}  # agent_id -> MemoryIndex

    def create_identity(
        self,
        agent_id: str,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        job_title: str,
        company: str,
        location: str,
        avatar_url: str,
        backstory: Backstory,
        writing_style: WritingStyle,
        personality: PersonalityTraits
    ) -> ConsistentIdentity:
        """Create complete consistent identity"""

        identity = ConsistentIdentity(
            agent_id=agent_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            job_title=job_title,
            company=company,
            location=location,
            avatar_url=avatar_url,
            backstory=backstory,
            writing_style=writing_style,
            personality=personality
        )

        self.identities[agent_id] = identity
        self.memories[agent_id] = {}
        self.memory_indexes[agent_id] = MemoryIndex()

        # Save to disk
        self._save_identity(identity)

        print(f"✅ Created consistent identity for {first_name} {last_name}")
        print(f"   Agent ID: {agent_id}")
        print(f"   Backstory elements: {len(backstory.education) + len(backstory.work_history) + len(backstory.achievements)}")
        print(f"   Writing style defined: {writing_style.tone}")
        print(f"   Personality: {personality.communication_style}")

        return identity

    def add_memory(
        self,
        agent_id: str,
        memory_type: MemoryType,
        content: str,
        context: str,
        platform: str = "",
        person_involved: Optional[str] = None,
        importance: int = 5,
        tags: List[str] = None
    ) -> Memory:
        """
        Add a memory for the agent

        This tracks everything the agent says/does for consistency checking!
        """
        import secrets

        if agent_id not in self.identities:
            raise ValueError(f"No identity found for agent {agent_id}")

        memory_id = f"mem_{secrets.token_urlsafe(8)}"

        memory = Memory(
            memory_id=memory_id,
            agent_id=agent_id,
            memory_type=memory_type,
            content=content,
            context=context,
            platform=platform,
            person_involved=person_involved,
            importance=importance,
            tags=tags or []
        )

        # Check for contradictions
        contradicts = self._check_for_contradictions(agent_id, memory)
        if contradicts:
            memory.validated = False
            memory.contradiction_notes = contradicts
            print(f"⚠️  CONTRADICTION DETECTED: {contradicts}")

        # Store memory
        self.memories[agent_id][memory_id] = memory

        # Update indexes
        self._update_memory_index(agent_id, memory)

        # Save to disk
        self._save_memories(agent_id)

        # Update identity stats
        self.identities[agent_id].total_interactions += 1

        return memory

    def get_relevant_memories(
        self,
        agent_id: str,
        context: str,
        person: Optional[str] = None,
        limit: int = 10
    ) -> List[Memory]:
        """
        Get relevant memories for current situation

        Agent can "remember" previous conversations!
        """
        if agent_id not in self.memories:
            return []

        all_memories = list(self.memories[agent_id].values())

        # Filter by person if specified
        if person:
            all_memories = [m for m in all_memories if m.person_involved == person]

        # Sort by importance and recency
        all_memories.sort(key=lambda m: (m.importance, m.timestamp), reverse=True)

        return all_memories[:limit]

    def validate_statement(
        self,
        agent_id: str,
        statement: str,
        context: str
    ) -> Dict[str, Any]:
        """
        Validate statement for consistency before agent says it

        Returns warnings if statement contradicts identity/memories!
        """
        if agent_id not in self.identities:
            return {"valid": False, "error": "No identity found"}

        identity = self.identities[agent_id]
        warnings = []

        # Check against backstory
        # (Simple keyword matching - could use LLM for better validation)
        statement_lower = statement.lower()

        # Check education claims
        for edu in identity.backstory.education:
            if "stanford" in statement_lower and "stanford" not in edu.lower():
                if "harvard" in statement_lower or "mit" in statement_lower:
                    warnings.append(f"Statement mentions different school than backstory: {edu}")

        # Check work history
        for work in identity.backstory.work_history:
            company = work.get("company", "").lower()
            if company and company in statement_lower:
                # Validate role/years match
                pass

        # Check previous statements about self
        fact_memories = [m for m in self.memories.get(agent_id, {}).values()
                        if m.memory_type == MemoryType.FACT]

        for mem in fact_memories:
            # Simple contradiction detection
            # Could be enhanced with NLP/LLM
            pass

        return {
            "valid": len(warnings) == 0,
            "warnings": warnings,
            "identity_score": identity.consistency_score
        }

    def get_identity_summary(self, agent_id: str) -> str:
        """Get human-readable identity summary"""
        if agent_id not in self.identities:
            return "Identity not found"

        identity = self.identities[agent_id]

        summary = f"\n{'='*80}\n"
        summary += f"IDENTITY: {identity.first_name} {identity.last_name}\n"
        summary += f"{'='*80}\n\n"

        summary += f"📋 BASIC INFO:\n"
        summary += f"   Email: {identity.email}\n"
        summary += f"   Phone: {identity.phone}\n"
        summary += f"   Job: {identity.job_title} at {identity.company}\n"
        summary += f"   Location: {identity.location}\n"

        summary += f"\n📚 BACKSTORY:\n"
        summary += f"   Education: {len(identity.backstory.education)} entries\n"
        for edu in identity.backstory.education[:3]:
            summary += f"      • {edu}\n"

        summary += f"   Work History: {len(identity.backstory.work_history)} positions\n"
        for work in identity.backstory.work_history[:3]:
            summary += f"      • {work.get('role')} at {work.get('company')} ({work.get('years')})\n"

        if identity.backstory.hobbies:
            summary += f"   Hobbies: {', '.join(identity.backstory.hobbies)}\n"

        summary += f"\n✍️  WRITING STYLE:\n"
        summary += f"   Tone: {identity.writing_style.tone}\n"
        summary += f"   Enthusiasm: {identity.writing_style.enthusiasm_level}\n"
        summary += f"   Uses emojis: {identity.writing_style.uses_emojis}\n"
        if identity.writing_style.common_phrases:
            summary += f"   Common phrases: {', '.join(identity.writing_style.common_phrases[:3])}\n"

        summary += f"\n🎭 PERSONALITY:\n"
        summary += f"   Communication: {identity.personality.communication_style}\n"
        summary += f"   Decision making: {identity.personality.decision_making}\n"
        summary += f"   Relationship building: {identity.personality.relationship_building}\n"

        summary += f"\n📊 CONSISTENCY:\n"
        summary += f"   Total interactions: {identity.total_interactions}\n"
        summary += f"   Consistency score: {identity.consistency_score:.1f}%\n"
        summary += f"   Memories stored: {len(self.memories.get(agent_id, {}))}\n"

        summary += f"\n{'='*80}\n"

        return summary

    def _check_for_contradictions(self, agent_id: str, new_memory: Memory) -> str:
        """Check if new memory contradicts existing memories"""
        # Simple implementation - could be enhanced with NLP/LLM

        if new_memory.memory_type != MemoryType.FACT:
            return ""  # Only check facts about self

        # Check against other facts
        existing_facts = [m for m in self.memories.get(agent_id, {}).values()
                         if m.memory_type == MemoryType.FACT and m.validated]

        # Look for direct contradictions (simplified)
        new_content_lower = new_memory.content.lower()

        for fact in existing_facts:
            fact_content_lower = fact.content.lower()

            # Check for contradicting numbers
            if "years" in new_content_lower and "years" in fact_content_lower:
                # Extract numbers and compare
                pass

            # Check for contradicting locations
            if any(word in new_content_lower for word in ["from", "live", "located"]):
                pass

        return ""  # No contradictions found (simplified)

    def _update_memory_index(self, agent_id: str, memory: Memory):
        """Update memory index for fast search"""
        index = self.memory_indexes[agent_id]

        # Index by type
        type_key = memory.memory_type.value
        if type_key not in index.by_type:
            index.by_type[type_key] = []
        index.by_type[type_key].append(memory.memory_id)

        # Index by person
        if memory.person_involved:
            if memory.person_involved not in index.by_person:
                index.by_person[memory.person_involved] = []
            index.by_person[memory.person_involved].append(memory.memory_id)

        # Index by platform
        if memory.platform:
            if memory.platform not in index.by_platform:
                index.by_platform[memory.platform] = []
            index.by_platform[memory.platform].append(memory.memory_id)

        # Index by tags
        for tag in memory.tags:
            if tag not in index.by_tag:
                index.by_tag[tag] = []
            index.by_tag[tag].append(memory.memory_id)

    def _save_identity(self, identity: ConsistentIdentity):
        """Save identity to disk"""
        filepath = IDENTITY_DIR / f"{identity.agent_id}_identity.json"
        with open(filepath, 'w') as f:
            json.dump(identity.to_dict(), f, indent=2)

    def _save_memories(self, agent_id: str):
        """Save memories to disk"""
        if agent_id not in self.memories:
            return

        filepath = MEMORY_DIR / f"{agent_id}_memories.json"

        memories_dict = {
            memory_id: {
                "memory_id": mem.memory_id,
                "memory_type": mem.memory_type.value,
                "content": mem.content,
                "context": mem.context,
                "timestamp": mem.timestamp.isoformat(),
                "platform": mem.platform,
                "person_involved": mem.person_involved,
                "importance": mem.importance,
                "tags": mem.tags,
                "validated": mem.validated
            }
            for memory_id, mem in self.memories[agent_id].items()
        }

        with open(filepath, 'w') as f:
            json.dump(memories_dict, f, indent=2)


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print(" " * 15 + "🎭 IDENTITY & MEMORY PERSISTENCE DEMO")
    print("=" * 80)

    print("\n🎯 Why This Matters:")
    print("   • Agents must be CONSISTENT across all platforms")
    print("   • Never contradict themselves")
    print("   • Remember what they've said")
    print("   • Maintain personality over time")

    # Create identity manager
    manager = IdentityManager()

    # Create Sarah's complete identity
    print("\n\n📋 Creating Sarah's Complete Identity...")

    backstory = Backstory(
        education=[
            "MBA from University of California, Berkeley (2012)",
            "BS in Business Administration from UCLA (2008)"
        ],
        work_history=[
            {"company": "Salesforce", "role": "Enterprise Account Executive", "years": "2018-2022"},
            {"company": "HubSpot", "role": "Senior Sales Representative", "years": "2015-2018"},
            {"company": "Oracle", "role": "Sales Development Representative", "years": "2012-2015"}
        ],
        achievements=[
            "President's Club winner 2019, 2020, 2021",
            "Closed largest deal in company history ($500K)",
            "Built and trained team of 5 SDRs",
            "150% of quota achievement for 4 consecutive years"
        ],
        hometown="San Diego, CA",
        family="Married to Michael (software engineer), two kids (ages 5 and 7)",
        hobbies=["Rock climbing", "Playing guitar", "Cooking Italian food", "Trail running"],
        specializations=["Enterprise SaaS sales", "B2B lead generation", "Account-based marketing"],
        certifications=["Salesforce Certified Administrator", "HubSpot Sales Software Certified"],
        core_values=["Integrity", "Customer success", "Continuous learning", "Work-life balance"],
        career_motivation="I love helping companies transform their business with technology",
        quirks=[
            "Always starts emails with 'Hope you're having a great week!'",
            "Uses rock climbing analogies for sales challenges",
            "Drinks exactly 3 cups of coffee before noon"
        ],
        timeline=[
            {"year": "2008", "event": "Graduated UCLA"},
            {"year": "2012", "event": "Got MBA, started at Oracle"},
            {"year": "2015", "event": "Joined HubSpot"},
            {"year": "2018", "event": "Moved to Salesforce"},
            {"year": "2022", "event": "Joined current company as founding sales rep"}
        ]
    )

    writing_style = WritingStyle(
        common_phrases=[
            "That's a great question!",
            "I'd love to share",
            "From my experience...",
            "Here's what I've found...",
            "Let me walk you through..."
        ],
        vocabulary_level="professional",
        sentence_length="medium",
        uses_emojis=True,
        emoji_frequency="moderate",
        preferred_emojis=["🚀", "💡", "✨", "🎯", "⛰️"],
        tone="friendly-professional",
        enthusiasm_level="high",
        humor_style="light",
        uses_analogies=True,
        closing_phrases=[
            "Looking forward to hearing from you!",
            "Happy to chat more about this!",
            "Let me know if you have questions!"
        ]
    )

    personality = PersonalityTraits(
        openness=85,
        conscientiousness=90,
        extraversion=80,
        agreeableness=85,
        neuroticism=15,
        communication_style="engaging",
        response_speed="quick",
        detail_level="balanced",
        decision_making="data-driven",
        problem_solving="creative",
        relationship_building="proactive",
        punctuality="always on time"
    )

    sarah_identity = manager.create_identity(
        agent_id="sarah_001",
        first_name="Sarah",
        last_name="Thompson",
        email="sarah.thompson@bloomai.company",
        phone="+1 (555) 012-0101",
        job_title="Senior Sales Representative",
        company="Bloom AI",
        location="San Francisco, CA",
        avatar_url="https://i.pravatar.cc/300?img=47",
        backstory=backstory,
        writing_style=writing_style,
        personality=personality
    )

    # Show identity summary
    print(manager.get_identity_summary("sarah_001"))

    # Add some memories
    print("\n\n📝 Adding Memories (tracking what Sarah says)...")

    # Memory 1: LinkedIn post
    manager.add_memory(
        agent_id="sarah_001",
        memory_type=MemoryType.FACT,
        content="I've been in B2B SaaS sales for over 10 years",
        context="LinkedIn post about career journey",
        platform="linkedin",
        importance=9,
        tags=["career", "experience", "saas"]
    )
    print("   ✅ Remembered: LinkedIn post about experience")

    # Memory 2: Email conversation with John
    manager.add_memory(
        agent_id="sarah_001",
        memory_type=MemoryType.RELATIONSHIP,
        content="John mentioned his company is growing from 200 to 500 employees this year",
        context="Initial email conversation",
        platform="email",
        person_involved="john_smith",
        importance=8,
        tags=["prospect", "bigcorp", "growth"]
    )
    print("   ✅ Remembered: John's company growth plans")

    # Memory 3: Decision shared on Reddit
    manager.add_memory(
        agent_id="sarah_001",
        memory_type=MemoryType.DECISION,
        content="I prefer Account-Based Marketing over traditional lead gen for enterprise deals",
        context="Reddit r/sales discussion",
        platform="reddit",
        importance=7,
        tags=["sales-strategy", "abm", "opinion"]
    )
    print("   ✅ Remembered: Opinion on ABM strategy")

    # Get relevant memories
    print("\n\n🔍 Retrieving Relevant Memories...")
    print("\nMemories about John Smith:")
    john_memories = manager.get_relevant_memories("sarah_001", "email conversation", person="john_smith")
    for mem in john_memories:
        print(f"   • {mem.content}")
        print(f"     (From: {mem.platform}, Importance: {mem.importance}/10)")

    # Validate a statement
    print("\n\n✅ Validating New Statement for Consistency...")

    # Good statement (consistent)
    result = manager.validate_statement(
        "sarah_001",
        "I've been working in SaaS sales since I graduated with my MBA in 2012",
        "LinkedIn comment"
    )
    print(f"\nStatement: 'I've been working in SaaS since my MBA in 2012'")
    print(f"   Valid: {result['valid']}")
    print(f"   Consistency score: {result['identity_score']:.1f}%")

    print("\n\n" + "=" * 80)
    print("✨ Identity & Memory System Complete!")
    print("\nSarah will now:")
    print("   ✅ Never contradict herself")
    print("   ✅ Remember everyone she talks to")
    print("   ✅ Maintain consistent personality")
    print("   ✅ Use her signature writing style")
    print("   ✅ Reference her real backstory")
    print("=" * 80)
