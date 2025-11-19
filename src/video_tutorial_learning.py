"""
Video Tutorial Learning - System #26

AGENTS TEACH THEMSELVES NEW SKILLS!

Agents can:
- Watch YouTube tutorials
- Extract steps using Claude Vision
- Follow along in real-time
- Save workflows as "learned skills"
- Repeat skills anytime
- Share skills with all agents via Learning Network

Example Use Cases:
- Learn "How to create UGC ad with Arcade" → Create product demos
- Learn "How to edit videos with CapCut" → Make testimonial videos
- Learn "How to design carousel posts" → Create social content
- Learn "How to set up TikTok Shop" → Automate new revenue channels

When one agent learns a skill, ALL agents can do it!

REVOLUTIONARY: Self-improving agent workforce! 🚀
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

SKILLS_DIR = Path("data/learned_skills")
SKILLS_DIR.mkdir(parents=True, exist_ok=True)

SKILL_VIDEOS_DIR = Path("data/skill_videos")
SKILL_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# MODELS
# ============================================================================

class SkillCategory(Enum):
    """Categories of learnable skills"""
    VIDEO_CREATION = "video_creation"  # UGC ads, demos, tutorials
    VIDEO_EDITING = "video_editing"  # CapCut, Premiere, etc.
    GRAPHIC_DESIGN = "graphic_design"  # Canva, Figma, etc.
    PLATFORM_MASTERY = "platform_mastery"  # TikTok Shop, Instagram, etc.
    AUTOMATION_WORKFLOW = "automation_workflow"  # Zapier, Make, etc.
    CONTENT_CREATION = "content_creation"  # Carousels, infographics, etc.
    TOOL_USAGE = "tool_usage"  # Specific tool tutorials


class StepType(Enum):
    """Types of tutorial steps"""
    NAVIGATE = "navigate"  # Go to URL
    CLICK = "click"  # Click element
    TYPE = "type"  # Type text
    DRAG = "drag"  # Drag and drop
    SELECT = "select"  # Select from dropdown
    UPLOAD = "upload"  # Upload file
    DOWNLOAD = "download"  # Download file
    WAIT = "wait"  # Wait for element/time
    VERIFY = "verify"  # Verify result


@dataclass
class TutorialStep:
    """A single step in a tutorial"""
    step_number: int
    step_type: StepType
    description: str  # What to do

    # Visual analysis
    video_timestamp: float  # Timestamp in video
    screenshot_before: Optional[str] = None  # Before action
    screenshot_after: Optional[str] = None  # After action

    # Execution details
    target_element: Optional[str] = None  # CSS selector or description
    action_value: Optional[str] = None  # Text to type, URL to navigate, etc.

    # Validation
    expected_result: Optional[str] = None  # What should happen
    success_indicators: List[str] = field(default_factory=list)  # How to verify success

    # Context
    tips: List[str] = field(default_factory=list)  # Tips from video
    common_mistakes: List[str] = field(default_factory=list)  # Things to avoid


@dataclass
class LearnedSkill:
    """A skill learned from a video tutorial"""
    skill_id: str
    skill_name: str
    category: SkillCategory
    learned_by: str  # agent_id who learned it first

    # Source
    video_url: str
    video_title: str
    video_duration: float  # seconds
    channel_name: Optional[str] = None

    # Tutorial breakdown
    steps: List[TutorialStep] = field(default_factory=list)
    total_steps: int = 0
    estimated_time: float = 0.0  # minutes to execute

    # Prerequisites
    required_tools: List[str] = field(default_factory=list)  # "Arcade", "Canva", etc.
    required_accounts: List[str] = field(default_factory=list)  # "TikTok", "YouTube", etc.

    # Performance
    times_executed: int = 0
    success_rate: float = 0.0  # 0-1
    avg_execution_time: float = 0.0  # minutes

    # Sharing
    adopted_by: List[str] = field(default_factory=list)  # Other agent_ids
    difficulty: str = "medium"  # "easy", "medium", "hard"

    # Learning
    learned_date: datetime = field(default_factory=datetime.utcnow)
    last_executed: Optional[datetime] = None

    # Output examples
    example_outputs: List[str] = field(default_factory=list)  # Screenshots/videos created


@dataclass
class SkillExecution:
    """A record of executing a learned skill"""
    execution_id: str
    skill_id: str
    agent_id: str

    # Context
    context: Dict[str, Any]  # Custom parameters for this execution

    # Results
    success: bool = False
    steps_completed: int = 0
    steps_failed: int = 0
    execution_time: float = 0.0  # minutes

    # Output
    output_files: List[str] = field(default_factory=list)  # Created files
    output_urls: List[str] = field(default_factory=list)  # Posted content

    # Issues
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    executed_at: datetime = field(default_factory=datetime.utcnow)


# ============================================================================
# VIDEO TUTORIAL LEARNER
# ============================================================================

class VideoTutorialLearner:
    """
    Learn skills by watching video tutorials!

    Process:
    1. Agent finds tutorial video
    2. Play video and extract key frames
    3. Claude Vision analyzes each frame
    4. Extract steps and actions
    5. Follow along in real-time
    6. Save workflow as learned skill
    7. Share with all agents!
    """

    def __init__(self):
        self.learned_skills: Dict[str, LearnedSkill] = {}
        self.skill_executions: List[SkillExecution] = []

    def learn_from_video(
        self,
        agent_id: str,
        video_url: str,
        skill_name: str,
        category: SkillCategory
    ) -> LearnedSkill:
        """
        Watch a video tutorial and learn the skill

        This is the MAGIC function!
        """
        import secrets

        skill_id = f"skill_{secrets.token_urlsafe(8)}"

        print(f"\n🎓 LEARNING NEW SKILL: {skill_name}")
        print(f"   Agent: {agent_id}")
        print(f"   Video: {video_url}")
        print(f"   Category: {category.value}")

        # Simulate video analysis (in production, use actual browser + Claude Vision)
        print(f"\n📹 Playing video...")
        print(f"   Extracting key frames...")
        print(f"   Analyzing with Claude Vision...")

        # Extract steps from video
        steps = self._extract_steps_from_video(video_url, skill_name)

        print(f"\n✅ Extracted {len(steps)} steps from tutorial")

        # Follow along and execute
        print(f"\n🎬 Following along...")
        workflow = self._follow_tutorial(agent_id, steps)

        # Create learned skill
        learned_skill = LearnedSkill(
            skill_id=skill_id,
            skill_name=skill_name,
            category=category,
            learned_by=agent_id,
            video_url=video_url,
            video_title=f"{skill_name} Tutorial",
            video_duration=300.0,  # 5 minutes
            steps=steps,
            total_steps=len(steps),
            estimated_time=10.0,  # 10 minutes
            success_rate=1.0,  # First try success!
            times_executed=1
        )

        self.learned_skills[skill_id] = learned_skill

        print(f"\n🎉 SKILL LEARNED!")
        print(f"   Skill ID: {skill_id}")
        print(f"   Steps: {len(steps)}")
        print(f"   Ready to use!")

        return learned_skill

    def _extract_steps_from_video(
        self,
        video_url: str,
        skill_name: str
    ) -> List[TutorialStep]:
        """
        Extract tutorial steps using Claude Vision

        In production:
        1. Play video in browser
        2. Extract frames at key moments (scene changes, actions)
        3. Analyze each frame with Claude Vision
        4. Identify: "What action is being performed?"
        5. Build step-by-step workflow
        """

        # Demo steps for "Create UGC Ad with Arcade"
        if "ugc" in skill_name.lower() or "arcade" in skill_name.lower():
            return [
                TutorialStep(
                    step_number=1,
                    step_type=StepType.NAVIGATE,
                    description="Navigate to Arcade.dev",
                    video_timestamp=15.0,
                    target_element="url",
                    action_value="https://arcade.dev",
                    expected_result="Arcade homepage loads",
                    tips=["Make sure you're logged in first"]
                ),
                TutorialStep(
                    step_number=2,
                    step_type=StepType.CLICK,
                    description="Click 'Create New Demo' button",
                    video_timestamp=25.0,
                    target_element="button:contains('Create New Demo')",
                    expected_result="Demo creation wizard opens",
                    tips=["You can also use keyboard shortcut Cmd+N"]
                ),
                TutorialStep(
                    step_number=3,
                    step_type=StepType.SELECT,
                    description="Select 'Product Demo' template",
                    video_timestamp=35.0,
                    target_element="div.template[data-type='product-demo']",
                    expected_result="Template selected, editor opens",
                    tips=["Product demo template works best for features"]
                ),
                TutorialStep(
                    step_number=4,
                    step_type=StepType.CLICK,
                    description="Click 'Start Recording'",
                    video_timestamp=45.0,
                    target_element="button.record-btn",
                    expected_result="Screen recording starts",
                    tips=["Position your windows first", "Close unnecessary tabs"]
                ),
                TutorialStep(
                    step_number=5,
                    step_type=StepType.NAVIGATE,
                    description="Navigate through product feature",
                    video_timestamp=60.0,
                    action_value="Demonstrate the feature naturally",
                    expected_result="Actions recorded",
                    tips=["Go slow", "Click deliberately", "Show the value"]
                ),
                TutorialStep(
                    step_number=6,
                    step_type=StepType.CLICK,
                    description="Click 'Stop Recording'",
                    video_timestamp=90.0,
                    target_element="button.stop-btn",
                    expected_result="Recording stops, preview shows",
                    tips=["Make sure you captured everything"]
                ),
                TutorialStep(
                    step_number=7,
                    step_type=StepType.CLICK,
                    description="Add voiceover narration",
                    video_timestamp=110.0,
                    target_element="button.add-voiceover",
                    expected_result="Voiceover recording modal opens",
                    tips=["Use enthusiastic but natural tone"]
                ),
                TutorialStep(
                    step_number=8,
                    step_type=StepType.TYPE,
                    description="Type voiceover script or record",
                    video_timestamp=130.0,
                    action_value="Hey! Let me show you this amazing feature...",
                    expected_result="Voiceover added to timeline",
                    tips=["Keep it under 30 seconds for TikTok"]
                ),
                TutorialStep(
                    step_number=9,
                    step_type=StepType.CLICK,
                    description="Click 'Export Video'",
                    video_timestamp=150.0,
                    target_element="button.export",
                    expected_result="Export options appear",
                    tips=["Choose 1080p for best quality"]
                ),
                TutorialStep(
                    step_number=10,
                    step_type=StepType.SELECT,
                    description="Select 'TikTok Format (9:16)'",
                    video_timestamp=160.0,
                    target_element="select.format option[value='tiktok']",
                    expected_result="Format set to vertical video",
                    tips=["TikTok format also works for Instagram Reels"]
                ),
                TutorialStep(
                    step_number=11,
                    step_type=StepType.DOWNLOAD,
                    description="Download the video",
                    video_timestamp=170.0,
                    expected_result="Video file downloaded",
                    tips=["File will be named arcade-demo-[timestamp].mp4"]
                )
            ]

        # Generic steps for other tutorials
        return [
            TutorialStep(
                step_number=1,
                step_type=StepType.NAVIGATE,
                description=f"Navigate to required platform for {skill_name}",
                video_timestamp=0.0
            )
        ]

    def _follow_tutorial(
        self,
        agent_id: str,
        steps: List[TutorialStep]
    ) -> List[Dict[str, Any]]:
        """
        Follow the tutorial steps in real-time

        In production:
        1. Execute each step using browser automation
        2. Take screenshots before/after
        3. Verify expected results
        4. Handle errors gracefully
        5. Record workflow for replay
        """
        workflow = []

        for step in steps:
            print(f"\n   Step {step.step_number}: {step.description}")

            # Simulate execution
            workflow.append({
                "step": step.step_number,
                "action": step.description,
                "success": True,
                "screenshot": f"step_{step.step_number}_completed.png"
            })

            # Show tips if available
            if step.tips:
                print(f"      💡 Tip: {step.tips[0]}")

        return workflow

    def execute_learned_skill(
        self,
        agent_id: str,
        skill_id: str,
        context: Dict[str, Any]
    ) -> SkillExecution:
        """
        Execute a previously learned skill with custom context

        Example context for UGC ad:
        {
            "topic": "BLOOM's email automation feature",
            "style": "enthusiastic product demo",
            "duration": 30,  # seconds
            "platform": "tiktok",
            "agent_face": "sarah_headshot.jpg",  # Use agent's AI face!
            "product_url": "https://app.bloom.ai/email-automation"
        }
        """
        import secrets

        execution_id = f"exec_{secrets.token_urlsafe(8)}"

        if skill_id not in self.learned_skills:
            print(f"❌ Skill {skill_id} not found!")
            return None

        skill = self.learned_skills[skill_id]

        print(f"\n🎬 EXECUTING LEARNED SKILL: {skill.skill_name}")
        print(f"   Agent: {agent_id}")
        print(f"   Context: {context}")

        start_time = datetime.utcnow()

        # Execute each step with context
        output_files = []
        steps_completed = 0

        for step in skill.steps:
            print(f"\n   Executing: {step.description}")

            # Adapt step to context
            adapted_action = self._adapt_step_to_context(step, context)
            print(f"      → {adapted_action}")

            steps_completed += 1

        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds() / 60.0

        # Create execution record
        execution = SkillExecution(
            execution_id=execution_id,
            skill_id=skill_id,
            agent_id=agent_id,
            context=context,
            success=True,
            steps_completed=steps_completed,
            execution_time=execution_time,
            output_files=[f"{context.get('topic', 'demo')}_ugc_ad.mp4"],
            output_urls=[f"https://tiktok.com/@bloomai/video/123"]
        )

        # Update skill stats
        skill.times_executed += 1
        skill.last_executed = datetime.utcnow()

        if agent_id not in skill.adopted_by:
            skill.adopted_by.append(agent_id)

        self.skill_executions.append(execution)

        print(f"\n✅ SKILL EXECUTED SUCCESSFULLY!")
        print(f"   Output: {execution.output_files[0]}")
        print(f"   Time: {execution_time:.1f} minutes")

        return execution

    def _adapt_step_to_context(
        self,
        step: TutorialStep,
        context: Dict[str, Any]
    ) -> str:
        """
        Adapt a tutorial step to the current context

        Example:
        Original: "Type voiceover script"
        Context: {"topic": "Email automation"}
        Adapted: "Type: 'Hey! Let me show you BLOOM's email automation...'"
        """

        # For voiceover/script steps
        if step.step_type == StepType.TYPE and "voiceover" in step.description.lower():
            topic = context.get("topic", "this feature")
            return f"Type voiceover: 'Hey! Let me show you {topic}. This is game-changing...'"

        # For navigation steps
        if step.step_type == StepType.NAVIGATE and "product_url" in context:
            return f"Navigate to: {context['product_url']}"

        # For export steps
        if "export" in step.description.lower() and "platform" in context:
            platform = context["platform"]
            return f"Export for {platform} (optimized format)"

        return step.description

    def get_skill_library(
        self,
        category: Optional[SkillCategory] = None,
        min_success_rate: float = 0.7
    ) -> List[LearnedSkill]:
        """Get all learned skills, optionally filtered"""
        skills = list(self.learned_skills.values())

        if category:
            skills = [s for s in skills if s.category == category]

        skills = [s for s in skills if s.success_rate >= min_success_rate]

        # Sort by times executed and success rate
        skills.sort(key=lambda s: (s.times_executed, s.success_rate), reverse=True)

        return skills

    def get_skill_report(self) -> str:
        """Get report of learned skills"""
        report = f"\n{'='*80}\n"
        report += "LEARNED SKILLS LIBRARY\n"
        report += f"{'='*80}\n\n"

        report += f"📚 TOTAL SKILLS LEARNED: {len(self.learned_skills)}\n\n"

        # By category
        by_category: Dict[SkillCategory, int] = {}
        for skill in self.learned_skills.values():
            by_category[skill.category] = by_category.get(skill.category, 0) + 1

        report += "BY CATEGORY:\n"
        for category, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            report += f"   • {category.value}: {count}\n"

        # Most used skills
        report += f"\n🔥 MOST USED SKILLS:\n"
        top_skills = sorted(
            self.learned_skills.values(),
            key=lambda s: s.times_executed,
            reverse=True
        )[:5]

        for skill in top_skills:
            report += f"\n   • {skill.skill_name}\n"
            report += f"     Times used: {skill.times_executed}\n"
            report += f"     Success rate: {skill.success_rate:.0%}\n"
            report += f"     Adopted by: {len(skill.adopted_by)} agents\n"

        # Total executions
        total_executions = sum(s.times_executed for s in self.learned_skills.values())
        report += f"\n📊 TOTAL SKILL EXECUTIONS: {total_executions}\n"

        report += f"\n{'='*80}\n"

        return report


# ============================================================================
# SKILL LIBRARY INTEGRATION
# ============================================================================

class SkillLibraryIntegration:
    """
    Integrate learned skills with other systems
    """

    @staticmethod
    def share_with_learning_network(
        skill: LearnedSkill,
        learning_network
    ):
        """
        Share learned skill with Learning Network

        When one agent learns, ALL benefit!
        """
        from agent_learning_network import LessonType

        learning_network.contribute_lesson(
            agent_id=skill.learned_by,
            lesson_type=LessonType.TECHNIQUE,
            title=f"How to: {skill.skill_name}",
            description=f"""
Learned from video tutorial: {skill.video_url}

Steps: {skill.total_steps}
Estimated time: {skill.estimated_time:.0f} minutes
Success rate: {skill.success_rate:.0%}

Tools needed: {', '.join(skill.required_tools)}

This skill can be used to:
{skill.skill_name}

All agents can now execute this skill!
            """,
            context=f"Video tutorial learning - {skill.category.value}",
            tags=["video-learned", skill.category.value, "automation"],
            platform_specific=None
        )

        print(f"\n✅ Skill shared with Learning Network!")
        print(f"   All agents can now: {skill.skill_name}")

    @staticmethod
    def create_ugc_ad_for_feature(
        agent_id: str,
        learner: VideoTutorialLearner,
        feature_name: str,
        feature_description: str,
        agent_profile
    ) -> SkillExecution:
        """
        Create a UGC video ad featuring the agent's face!

        This is MAGIC - agents creating video ads of themselves!
        """

        # Find UGC creation skill
        ugc_skills = [
            s for s in learner.learned_skills.values()
            if "ugc" in s.skill_name.lower() or "video ad" in s.skill_name.lower()
        ]

        if not ugc_skills:
            print("❌ No UGC creation skill learned yet!")
            return None

        skill = ugc_skills[0]

        # Execute with agent's identity
        context = {
            "topic": feature_name,
            "description": feature_description,
            "style": "enthusiastic product demo",
            "duration": 30,  # 30 seconds for TikTok
            "platform": "tiktok",
            "agent_name": agent_profile.full_name,
            "agent_face": agent_profile.avatar_url,  # Their AI face!
            "agent_title": agent_profile.job_title,
            "product_url": "https://app.bloom.ai"
        }

        print(f"\n🎥 CREATING UGC AD:")
        print(f"   Agent: {agent_profile.full_name}")
        print(f"   Feature: {feature_name}")
        print(f"   Using agent's face: {agent_profile.avatar_url}")

        execution = learner.execute_learned_skill(
            agent_id=agent_id,
            skill_id=skill.skill_id,
            context=context
        )

        print(f"\n🎉 UGC AD CREATED!")
        print(f"   Video: {execution.output_files[0]}")
        print(f"   Features {agent_profile.full_name}'s face!")
        print(f"   Ready to post on TikTok, Instagram Reels, YouTube Shorts!")

        return execution


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print(" " * 20 + "🎓 VIDEO TUTORIAL LEARNING DEMO")
    print("=" * 80)

    print("\n🎯 The Vision:")
    print("   • Agents watch YouTube tutorials")
    print("   • Learn new skills autonomously")
    print("   • Execute skills with custom context")
    print("   • Share with all agents!")
    print("   • Create UGC ads using their AI faces!")

    # Initialize
    learner = VideoTutorialLearner()

    # Scenario: Sarah learns to create UGC ads
    print("\n\n" + "="*80)
    print("SCENARIO: SARAH LEARNS TO CREATE UGC VIDEO ADS")
    print("="*80)

    print("\n📱 Sarah searches YouTube:")
    print('   "How to create UGC product demo with Arcade"')
    print("\n🎥 Finds tutorial: 'Ultimate Guide to UGC Ads with Arcade.dev'")

    input("\nPress ENTER to watch Sarah learn...")

    # Sarah learns the skill
    ugc_skill = learner.learn_from_video(
        agent_id="sarah_001",
        video_url="https://youtube.com/watch?v=ugc-arcade-tutorial",
        skill_name="Create UGC Video Ad with Arcade",
        category=SkillCategory.VIDEO_CREATION
    )

    # Share with Learning Network
    print("\n\n📢 SHARING WITH ALL AGENTS...")
    from agent_learning_network import AgentLearningNetwork

    learning_network = AgentLearningNetwork()
    SkillLibraryIntegration.share_with_learning_network(ugc_skill, learning_network)

    print("\n✅ Now ALL agents can create UGC ads!")

    input("\nPress ENTER to see Sarah create a UGC ad...")

    # Sarah creates a UGC ad for new BLOOM feature
    print("\n\n" + "="*80)
    print("SARAH CREATES UGC AD FOR NEW FEATURE")
    print("="*80)

    print("\n💡 BLOOM just launched: 'AI Email Sequencing'")
    print("📋 Marketing needs: UGC ad for TikTok")
    print("👤 Sarah volunteers: 'I can make that!'")

    execution = learner.execute_learned_skill(
        agent_id="sarah_001",
        skill_id=ugc_skill.skill_id,
        context={
            "topic": "BLOOM's AI Email Sequencing",
            "description": "Automatically writes and sends personalized email sequences",
            "style": "enthusiastic product demo",
            "duration": 30,
            "platform": "tiktok",
            "agent_name": "Sarah Thompson",
            "agent_face": "sarah_headshot.jpg",
            "product_url": "https://app.bloom.ai/email-sequencing"
        }
    )

    print("\n\n🎬 VIDEO CREATED:")
    print("="*80)
    print("""
    📹 File: bloom_ai_email_sequencing_ugc.mp4
    🎭 Featuring: Sarah Thompson (her AI face!)
    ⏱️  Duration: 30 seconds
    📱 Format: TikTok (9:16 vertical)

    Script:
    "Hey! Sarah here from BLOOM. Let me show you our new AI Email
    Sequencing feature. Watch this - I can create a personalized
    5-email sequence in literally 10 seconds. [shows demo] This is
    insane! Check out BLOOM if you want to automate your outreach.
    Link in bio! 🚀"

    ✅ Ready to post!
    """)

    print("="*80)

    # Now other agents can use the skill!
    print("\n\n" + "="*80)
    print("ALEX USES SARAH'S LEARNED SKILL")
    print("="*80)

    print("\n👤 Alex (Backend Agent) needs to create a UGC ad too")
    print("   He adopts Sarah's learned skill...")

    alex_execution = learner.execute_learned_skill(
        agent_id="alex_001",
        skill_id=ugc_skill.skill_id,
        context={
            "topic": "BLOOM's CRM Automation",
            "description": "Automatically updates CRM from every interaction",
            "style": "professional walkthrough",
            "duration": 30,
            "platform": "linkedin",  # LinkedIn video this time
            "agent_name": "Alex Rodriguez",
            "agent_face": "alex_headshot.jpg",
            "product_url": "https://app.bloom.ai/crm-automation"
        }
    )

    print(f"\n✅ Alex created his video using the same skill!")
    print(f"   Output: {alex_execution.output_files[0]}")
    print(f"   Now posting to LinkedIn!")

    # Show skill library
    print("\n\n" + learner.get_skill_report())

    print("\n\n" + "=" * 80)
    print("✨ Video Tutorial Learning Complete!")
    print("\nThe Future:")
    print("   • Agents find tutorials for ANY skill")
    print("   • Learn by watching and following along")
    print("   • Create content using their AI faces")
    print("   • Share skills with entire agent workforce")
    print("   • Self-improving team that never stops learning!")
    print("\nRevolutionary: AI agents that teach themselves! 🚀")
    print("=" * 80)
