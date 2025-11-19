"""
Agent Learning Network - System #24

Collective Intelligence: Agents share knowledge and learn from each other!

When Sarah discovers something that works, ALL agents benefit.
When Mike makes a mistake, ALL agents learn to avoid it.

100 agents = 100x the learning speed!
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pathlib import Path
import json


# ============================================================================
# CONFIGURATION
# ============================================================================

LEARNING_DIR = Path("data/agent_learning")
LEARNING_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# LEARNING MODELS
# ============================================================================

class LessonType(Enum):
    """Types of lessons"""
    BEST_PRACTICE = "best_practice"  # Something that works well
    AVOID = "avoid"  # Something that backfired
    INSIGHT = "insight"  # Useful knowledge
    TECHNIQUE = "technique"  # Specific method/approach
    PATTERN = "pattern"  # Recurring successful pattern


@dataclass
class Lesson:
    """A lesson learned by an agent"""
    lesson_id: str
    discovered_by: str  # agent_id
    lesson_type: LessonType

    # Content
    title: str
    description: str
    context: str  # When/where this applies

    # Evidence
    success_count: int = 0  # How many times this worked
    failure_count: int = 0  # How many times this failed
    confidence: float = 0.5  # 0-1, how confident are we

    # Impact
    avg_improvement: float = 0.0  # % improvement when applied
    revenue_impact: float = 0.0  # Revenue attributed to this lesson

    # Validation
    validated_by: List[str] = field(default_factory=list)  # Other agent_ids who confirm
    adopted_by: List[str] = field(default_factory=list)  # Agents using this

    # Meta
    discovered_date: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    platform_specific: Optional[str] = None  # "reddit", "linkedin", etc.


@dataclass
class AgentContribution:
    """Track what each agent contributes to collective knowledge"""
    agent_id: str
    lessons_contributed: int = 0
    lessons_validated: int = 0
    lessons_adopted: int = 0
    impact_score: float = 0.0  # How much have their lessons helped others


# ============================================================================
# LEARNING NETWORK
# ============================================================================

class AgentLearningNetwork:
    """
    Collective intelligence for all agents

    When one learns, all benefit!
    """

    def __init__(self):
        self.lessons: Dict[str, Lesson] = {}
        self.contributions: Dict[str, AgentContribution] = {}

    def contribute_lesson(
        self,
        agent_id: str,
        lesson_type: LessonType,
        title: str,
        description: str,
        context: str,
        success_count: int = 1,
        tags: List[str] = None,
        platform_specific: Optional[str] = None
    ) -> Lesson:
        """Agent contributes a lesson to the network"""
        import secrets

        lesson_id = f"lesson_{secrets.token_urlsafe(8)}"

        lesson = Lesson(
            lesson_id=lesson_id,
            discovered_by=agent_id,
            lesson_type=lesson_type,
            title=title,
            description=description,
            context=context,
            success_count=success_count,
            tags=tags or [],
            platform_specific=platform_specific
        )

        self.lessons[lesson_id] = lesson

        # Track contribution
        if agent_id not in self.contributions:
            self.contributions[agent_id] = AgentContribution(agent_id=agent_id)

        self.contributions[agent_id].lessons_contributed += 1

        print(f"✅ Lesson shared: {title}")
        print(f"   By: {agent_id}")
        print(f"   Type: {lesson_type.value}")

        return lesson

    def validate_lesson(self, lesson_id: str, agent_id: str, worked: bool = True):
        """Agent validates a lesson (tried it, did it work?)"""
        if lesson_id not in self.lessons:
            return

        lesson = self.lessons[lesson_id]

        if agent_id not in lesson.validated_by:
            lesson.validated_by.append(agent_id)

            if worked:
                lesson.success_count += 1
            else:
                lesson.failure_count += 1

            # Update confidence
            total = lesson.success_count + lesson.failure_count
            lesson.confidence = lesson.success_count / max(total, 1)

            # Track validation contribution
            if agent_id not in self.contributions:
                self.contributions[agent_id] = AgentContribution(agent_id=agent_id)

            self.contributions[agent_id].lessons_validated += 1

            print(f"✅ Lesson validated by {agent_id}")
            print(f"   Worked: {worked}")
            print(f"   New confidence: {lesson.confidence:.0%}")

    def adopt_lesson(self, lesson_id: str, agent_id: str):
        """Agent adopts a lesson (will use this going forward)"""
        if lesson_id not in self.lessons:
            return

        lesson = self.lessons[lesson_id]

        if agent_id not in lesson.adopted_by:
            lesson.adopted_by.append(agent_id)

            if agent_id not in self.contributions:
                self.contributions[agent_id] = AgentContribution(agent_id=agent_id)

            self.contributions[agent_id].lessons_adopted += 1

            print(f"✅ {agent_id} adopted lesson: {lesson.title}")

    def get_relevant_lessons(
        self,
        context: str = "",
        platform: Optional[str] = None,
        tags: List[str] = None,
        min_confidence: float = 0.6,
        limit: int = 10
    ) -> List[Lesson]:
        """Get lessons relevant to current situation"""
        relevant = []

        for lesson in self.lessons.values():
            # Check confidence threshold
            if lesson.confidence < min_confidence:
                continue

            # Check platform
            if platform and lesson.platform_specific and lesson.platform_specific != platform:
                continue

            # Check tags
            if tags and not any(tag in lesson.tags for tag in tags):
                continue

            relevant.append(lesson)

        # Sort by confidence and success count
        relevant.sort(key=lambda l: (l.confidence, l.success_count), reverse=True)

        return relevant[:limit]

    def get_best_practices(self, platform: Optional[str] = None, limit: int = 10) -> List[Lesson]:
        """Get top best practices"""
        practices = [
            l for l in self.lessons.values()
            if l.lesson_type == LessonType.BEST_PRACTICE and l.confidence >= 0.7
        ]

        if platform:
            practices = [p for p in practices if p.platform_specific == platform or p.platform_specific is None]

        practices.sort(key=lambda p: (p.confidence, p.success_count, len(p.adopted_by)), reverse=True)

        return practices[:limit]

    def get_learning_summary(self) -> str:
        """Get summary of collective learning"""
        summary = f"\n{'='*80}\n"
        summary += "AGENT LEARNING NETWORK\n"
        summary += f"{'='*80}\n\n"

        summary += f"📚 COLLECTIVE KNOWLEDGE:\n"
        summary += f"   Total Lessons: {len(self.lessons)}\n"
        summary += f"   Best Practices: {len([l for l in self.lessons.values() if l.lesson_type == LessonType.BEST_PRACTICE])}\n"
        summary += f"   Techniques: {len([l for l in self.lessons.values() if l.lesson_type == LessonType.TECHNIQUE])}\n"
        summary += f"   Avoid: {len([l for l in self.lessons.values() if l.lesson_type == LessonType.AVOID])}\n"

        summary += f"\n🏆 TOP CONTRIBUTORS:\n"
        top_contributors = sorted(
            self.contributions.values(),
            key=lambda c: c.lessons_contributed,
            reverse=True
        )[:5]

        for contrib in top_contributors:
            summary += f"   • {contrib.agent_id}: {contrib.lessons_contributed} lessons\n"

        summary += f"\n✨ TOP BEST PRACTICES:\n"
        best_practices = self.get_best_practices(limit=5)
        for i, practice in enumerate(best_practices, 1):
            summary += f"\n   {i}. {practice.title}\n"
            summary += f"      Confidence: {practice.confidence:.0%} ({practice.success_count} successes)\n"
            summary += f"      Adopted by: {len(practice.adopted_by)} agents\n"
            summary += f"      {practice.description[:100]}...\n"

        summary += f"\n{'='*80}\n"

        return summary


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print(" " * 10 + "🧠 AGENT LEARNING NETWORK DEMO")
    print("=" * 80)

    print("\n🎯 Collective Intelligence:")
    print("   • When one agent learns, ALL benefit")
    print("   • 100 agents = 100x learning speed")
    print("   • Best practices spread instantly")
    print("   • Mistakes prevent future failures")

    # Create network
    network = AgentLearningNetwork()

    # Sarah discovers something that works
    print("\n\n📚 Sarah Discovers Best Practice...")

    lesson1 = network.contribute_lesson(
        agent_id="sarah_001",
        lesson_type=LessonType.BEST_PRACTICE,
        title="Ask about tech stack before recommending solutions",
        description="""
        When someone mentions 'scaling challenges', asking about their current tech stack
        FIRST builds way more trust than jumping to solutions. People appreciate that you
        want to understand their situation before recommending anything.

        This consistently leads to better conversations and higher close rates.
        """,
        context="LinkedIn and Reddit technical discussions",
        success_count=15,
        tags=["trust-building", "discovery", "technical"],
        platform_specific=None  # Works on all platforms
    )

    # Mike tries it and validates
    print("\n✅ Mike Tries Sarah's Approach...")
    network.validate_lesson(lesson1.lesson_id, "mike_001", worked=True)

    # Alex tries it too
    print("\n✅ Alex Tries It...")
    network.validate_lesson(lesson1.lesson_id, "alex_001", worked=True)

    # Now all agents adopt it
    print("\n📖 Agents Adopt Lesson...")
    network.adopt_lesson(lesson1.lesson_id, "mike_001")
    network.adopt_lesson(lesson1.lesson_id, "alex_001")

    # Mike discovers what NOT to do
    print("\n\n⚠️  Mike Discovers What to Avoid...")

    lesson2 = network.contribute_lesson(
        agent_id="mike_001",
        lesson_type=LessonType.AVOID,
        title="Don't mention pricing in first Reddit comment",
        description="""
        Mentioning pricing in the first Reddit comment comes across as too salesy,
        even if you provide value first. Wait until they ask or until the conversation
        naturally goes there (usually 2-3 comments in).

        Early pricing mentions get downvoted and hurt trust.
        """,
        context="Reddit discussions in technical subreddits",
        success_count=0,
        tags=["reddit", "pricing", "timing"],
        platform_specific="reddit"
    )

    # Sarah validates - yes, she's seen this too
    network.validate_lesson(lesson2.lesson_id, "sarah_001", worked=False)  # Failed for her too

    # Everyone adopts to avoid this mistake
    network.adopt_lesson(lesson2.lesson_id, "sarah_001")
    network.adopt_lesson(lesson2.lesson_id, "alex_001")

    # Show learning summary
    print("\n\n" + network.get_learning_summary())

    # Alex looks for relevant lessons before responding to prospect
    print("\n\n🔍 Alex Looks for Relevant Lessons Before Reddit Comment...")
    relevant = network.get_relevant_lessons(
        platform="reddit",
        tags=["technical"],
        min_confidence=0.6
    )

    print(f"\nFound {len(relevant)} relevant lessons:")
    for lesson in relevant:
        print(f"\n   • {lesson.title}")
        print(f"     Confidence: {lesson.confidence:.0%}")
        print(f"     Use this: {lesson.description[:80]}...")

    print("\n\n" + "=" * 80)
    print("✨ Learning Network Complete!")
    print("\nNow:")
    print("   ✅ Sarah's insights benefit everyone")
    print("   ✅ Mike's mistakes prevent future failures")
    print("   ✅ All agents get smarter together")
    print("   ✅ 100 agents = 100x learning speed!")
    print("=" * 80)
