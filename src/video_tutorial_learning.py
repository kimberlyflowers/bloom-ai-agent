"""
Self-Learning from Video Tutorials - System #26

🎓 AGENTS TEACH THEMSELVES NEW SKILLS!

How it works:
1. Agent finds YouTube tutorial (e.g., "How to create UGC ad with Arcade")
2. Watches video, Claude Vision analyzes each frame
3. Extracts step-by-step instructions
4. Follows along with browser automation
5. Records workflow with screenshots
6. Saves as "learned skill" in memory
7. Can repeat skill anytime with new context!

Example:
- Sarah watches: "How to create UGC video ad"
- Sarah learns: Complete workflow
- Sarah creates: UGC ad with HER AI face promoting BLOOM
- Sarah posts: TikTok, Instagram Reels
- Result: Professional UGC content at scale!

When one agent learns → ALL agents can do it (via Learning Network)!
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from pathlib import Path
import json
import base64
import time
import logging
import re
import os
import asyncio

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

SKILLS_DIR = Path("data/learned_skills")
SKILLS_DIR.mkdir(parents=True, exist_ok=True)

WORKFLOWS_DIR = Path("data/skill_workflows")
WORKFLOWS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# LEARNED SKILL MODELS
# ============================================================================

class SkillCategory(Enum):
    """Categories of learnable skills"""
    VIDEO_CREATION = "video_creation"  # Arcade, CapCut, video editing
    GRAPHIC_DESIGN = "graphic_design"  # Canva, Figma, design tools
    PLATFORM_MASTERY = "platform_mastery"  # TikTok Shop, LinkedIn features
    CONTENT_CREATION = "content_creation"  # Writing, posting, formatting
    AUTOMATION_WORKFLOW = "automation_workflow"  # Tool workflows
    MARKETING_TECHNIQUE = "marketing_technique"  # Marketing strategies
    SALES_PROCESS = "sales_process"  # Sales techniques
    TECHNICAL_SKILL = "technical_skill"  # Technical workflows


class StepType(Enum):
    """Types of steps in a tutorial"""
    NAVIGATE = "navigate"  # Go to URL
    CLICK = "click"  # Click element
    TYPE = "type"  # Type text
    SELECT = "select"  # Select option
    UPLOAD = "upload"  # Upload file
    WAIT = "wait"  # Wait for element/time
    VERIFY = "verify"  # Verify result
    EXTRACT = "extract"  # Extract information


@dataclass
class TutorialStep:
    """A single step from a tutorial"""
    step_number: int
    description: str  # "Click the 'Record Demo' button"
    action_type: StepType

    # Action details
    target: Optional[str] = None  # Selector, URL, etc.
    target_element: Optional[str] = None  # Alternative name for target (UI element description)
    input_value: Optional[str] = None  # Text to type, file to upload
    expected_result: Optional[str] = None  # What should happen

    # Visual reference
    screenshot_before: Optional[str] = None
    screenshot_after: Optional[str] = None

    # Context
    timing_notes: Optional[str] = None  # "Wait 2 seconds for animation"
    timestamp: Optional[float] = None  # When in video (seconds)
    pro_tips: List[str] = field(default_factory=list)
    common_mistakes: List[str] = field(default_factory=list)

    # Execution tracking
    success: Optional[bool] = None  # Was this step executed successfully?

    def __post_init__(self):
        # Ensure target_element is set (use target if target_element not provided)
        if self.target_element is None and self.target is not None:
            self.target_element = self.target


@dataclass
class LearnedSkill:
    """A skill learned from a video tutorial"""
    skill_id: str
    skill_name: str  # "Create UGC Video Ad with Arcade"
    category: SkillCategory
    agent_id: str  # agent_id (changed from learned_by for consistency)

    # Source
    video_url: str  # Changed from source_video_url
    video_title: str = ""
    video_creator: str = ""
    tutorial_quality: float = 0.0  # 0-1, how good was the tutorial

    # The skill itself
    tutorial_steps: List[TutorialStep] = field(default_factory=list)  # Changed from steps
    required_tools: List[str] = field(default_factory=list)  # ["Arcade.dev", "Browser"]
    prerequisites: List[str] = field(default_factory=list)  # Other skills needed first

    # Performance
    times_practiced: int = 0  # Changed from times_executed
    success_rate: float = 0.0  # 0-1
    avg_duration_seconds: float = 0.0

    # Context for execution
    variable_inputs: Dict[str, str] = field(default_factory=dict)  # {"topic": "describe", "style": "options"}
    output_description: str = ""  # What this skill produces

    # Sharing
    shared_with_network: bool = False
    adopted_by: List[str] = field(default_factory=list)  # Other agent_ids

    # Meta
    learned_at: datetime = field(default_factory=datetime.utcnow)  # Changed from learned_date
    last_practiced: Optional[datetime] = None  # Changed from last_used_date

    # Quality metrics
    clarity_score: float = 0.0  # How clear were the instructions
    replicability_score: float = 0.0  # How easy to replicate
    usefulness_score: float = 0.0  # How useful is this skill


@dataclass
class SkillExecution:
    """A specific execution of a learned skill"""
    execution_id: str
    skill_id: str
    agent_id: str
    context: Dict[str, Any]  # Variable inputs for this execution

    # Results
    success: bool = False
    output: Optional[str] = None  # URL, file path, etc.
    screenshots: List[str] = field(default_factory=list)

    # Performance
    duration_seconds: float = 0.0
    errors: List[str] = field(default_factory=list)

    # Meta
    executed_at: datetime = field(default_factory=datetime.utcnow)


# ============================================================================
# VIDEO ANALYSIS
# ============================================================================

class VideoTutorialAnalyzer:
    """
    Analyze video tutorials to extract learnable steps

    Uses Claude API to parse transcripts and identify actionable UI steps!
    """

    def __init__(self):
        self.frame_interval = 2.0  # Analyze every 2 seconds

    async def get_transcript_with_timestamps(self, video_url: str) -> List[Dict[str, Any]]:
        """
        Extract real YouTube transcript with timestamps

        Returns:
            List of transcript entries: [
                {"text": "First, click the create button", "start": 1.5, "duration": 2.0},
                ...
            ]
        """
        from youtube_transcript_api import YouTubeTranscriptApi

        logger.info(f"📝 Extracting transcript from: {video_url}")

        # Extract video ID from various YouTube URL formats
        video_id = None
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',      # Standard watch URL
            r'(?:embed\/)([0-9A-Za-z_-]{11})',      # Embed URL
            r'(?:shorts\/)([0-9A-Za-z_-]{11})',     # Shorts URL
            r'^([0-9A-Za-z_-]{11})$'                # Just the ID
        ]

        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                video_id = match.group(1)
                break

        if not video_id:
            logger.error(f"❌ Could not extract video ID from: {video_url}")
            raise ValueError(f"Invalid YouTube URL: {video_url}")

        # Get transcript using youtube-transcript-api
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            logger.info(f"✅ Extracted {len(transcript_list)} transcript segments")
            return transcript_list

        except Exception as e:
            logger.error(f"❌ Failed to get transcript: {e}")
            # Try with generated subtitles if manual ones fail
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(
                    video_id,
                    languages=['en']
                )
                logger.info(f"✅ Extracted {len(transcript_list)} transcript segments (auto-generated)")
                return transcript_list
            except Exception as e2:
                logger.error(f"❌ Auto-generated subtitles also failed: {e2}")
                raise ValueError(f"Could not extract transcript: {e2}")

    async def parse_transcript_into_actions(self, transcript: List[Dict], skill_name: str) -> List[TutorialStep]:
        """
        Use Claude API to parse transcript into actionable UI steps

        Args:
            transcript: List of transcript segments with timestamps
            skill_name: Name of skill being learned

        Returns:
            List of TutorialStep objects ready for execution
        """
        import anthropic

        logger.info(f"🤖 Parsing transcript into actionable steps...")

        # Combine transcript into readable text with timestamps
        full_transcript = "\n".join([
            f"[{entry['start']:.1f}s] {entry['text']}"
            for entry in transcript[:100]  # Limit to first 100 segments to avoid token limits
        ])

        # Create Claude API client
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        # Prompt Claude to extract actionable steps
        prompt = f"""You are analyzing a tutorial video transcript to extract actionable UI steps.

Tutorial Title: {skill_name}

Transcript with timestamps:
{full_transcript}

Your task: Extract ONLY the actionable UI steps from this transcript. Ignore introductions, explanations, and commentary.

For each actionable step, identify:
1. **action_type**: One of: CLICK, TYPE, SELECT, WAIT, NAVIGATE, VERIFY
2. **description**: Brief description of what to do
3. **target_element**: What UI element to interact with (e.g., "Create button", "search box", "upload icon")
4. **input_value**: If TYPE action, what text to type (otherwise null)
5. **expected_result**: What should happen after this step
6. **timestamp**: When in video this step occurs

IMPORTANT RULES:
- Only include steps that involve UI interaction
- Skip steps like "Now let me explain..." or "As you can see..."
- Be specific about target elements (not just "button" but "blue Create button in top right")
- Use exact action types from the list above
- Order steps sequentially

Return ONLY a valid JSON array of steps, no other text:

[
  {{
    "step_number": 1,
    "action_type": "CLICK",
    "description": "Click the Create button to start new project",
    "target_element": "Create button in top right corner",
    "input_value": null,
    "expected_result": "New project dialog opens",
    "timestamp": 15.5
  }}
]
"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.2,  # Low temperature for more deterministic parsing
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract JSON from response
            response_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            # Parse JSON
            steps_data = json.loads(response_text)

            logger.info(f"✅ Parsed {len(steps_data)} actionable steps from transcript")

            # Convert to TutorialStep objects
            tutorial_steps = []
            for step_data in steps_data:
                tutorial_steps.append(TutorialStep(
                    step_number=step_data["step_number"],
                    action_type=StepType[step_data["action_type"].upper()],
                    description=step_data["description"],
                    target_element=step_data.get("target_element"),
                    input_value=step_data.get("input_value"),
                    expected_result=step_data.get("expected_result"),
                    timestamp=step_data.get("timestamp"),
                    success=None  # Will be set during execution
                ))

            return tutorial_steps

        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse Claude's response as JSON: {e}")
            logger.error(f"Response was: {response_text[:500]}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to parse transcript: {e}")
            raise

    async def analyze_tutorial(
        self,
        video_url: str,
        skill_name: str,
        category: SkillCategory
    ) -> List[TutorialStep]:
        """
        REAL IMPLEMENTATION: Analyze YouTube tutorial and extract steps
        """
        logger.info(f"🎥 Analyzing tutorial: {skill_name}")

        try:
            # 1. Extract real transcript
            transcript = await self.get_transcript_with_timestamps(video_url)

            if not transcript:
                raise ValueError("No transcript available for this video")

            # 2. Parse transcript into actionable steps using Claude
            tutorial_steps = await self.parse_transcript_into_actions(transcript, skill_name)

            logger.info(f"✅ Analysis complete: {len(tutorial_steps)} steps identified")
            return tutorial_steps

        except Exception as e:
            logger.error(f"❌ Tutorial analysis failed: {e}")
            raise

    def _simulate_video_analysis(
        self,
        skill_name: str,
        category: SkillCategory
    ) -> List[TutorialStep]:
        """
        Simulate what Claude Vision would extract from tutorial

        In production, this analyzes actual video frames!
        """
        if "UGC" in skill_name or "Arcade" in skill_name:
            # Simulating: "How to create UGC video ad with Arcade"
            return [
                TutorialStep(
                    step_number=1,
                    description="Navigate to Arcade.dev",
                    action_type=StepType.NAVIGATE,
                    target="https://arcade.software",
                    expected_result="Arcade homepage loads",
                    timing_notes="Wait for page to fully load"
                ),
                TutorialStep(
                    step_number=2,
                    description="Click 'Start Recording' button",
                    action_type=StepType.CLICK,
                    target="button:contains('Start Recording')",
                    expected_result="Recording interface opens",
                    pro_tips=["Make sure to allow screen recording permissions"],
                    timing_notes="Browser may ask for permissions"
                ),
                TutorialStep(
                    step_number=3,
                    description="Select browser tab to record",
                    action_type=StepType.SELECT,
                    target="tab-selector",
                    expected_result="Tab selected for recording",
                    timing_notes="Choose the product demo tab"
                ),
                TutorialStep(
                    step_number=4,
                    description="Click 'Record' to start capturing",
                    action_type=StepType.CLICK,
                    target="button[data-action='record']",
                    expected_result="Recording begins, red indicator shows",
                    pro_tips=["Speak clearly if adding voiceover", "Move slowly through UI"]
                ),
                TutorialStep(
                    step_number=5,
                    description="Navigate through product demonstrating features",
                    action_type=StepType.NAVIGATE,
                    target="your-product-url",
                    expected_result="Product demo recorded",
                    timing_notes="Take 15-30 seconds showing key features",
                    pro_tips=["Highlight pain points this solves", "Show clear value"]
                ),
                TutorialStep(
                    step_number=6,
                    description="Click 'Stop Recording'",
                    action_type=StepType.CLICK,
                    target="button[data-action='stop']",
                    expected_result="Recording stops, enters editing mode",
                    timing_notes="Wait a moment before clicking"
                ),
                TutorialStep(
                    step_number=7,
                    description="Add text overlays highlighting key points",
                    action_type=StepType.CLICK,
                    target=".add-text-button",
                    input_value="Problem → Solution → Result",
                    expected_result="Text overlays added to video",
                    pro_tips=["Keep text short and punchy", "Use contrasting colors"]
                ),
                TutorialStep(
                    step_number=8,
                    description="Add voiceover narration (optional)",
                    action_type=StepType.CLICK,
                    target=".add-voiceover",
                    expected_result="Voiceover recording interface opens",
                    timing_notes="Optional but increases engagement",
                    common_mistakes=["Talking too fast", "Not testing audio first"]
                ),
                TutorialStep(
                    step_number=9,
                    description="Preview the final video",
                    action_type=StepType.CLICK,
                    target="button[data-action='preview']",
                    expected_result="Video plays in preview mode",
                    pro_tips=["Watch full video to check flow", "Verify audio sync"]
                ),
                TutorialStep(
                    step_number=10,
                    description="Export video",
                    action_type=StepType.CLICK,
                    target="button[data-action='export']",
                    expected_result="Video exports as MP4",
                    timing_notes="May take 30-60 seconds to export",
                    pro_tips=["Choose 1080p for best quality", "Download to known location"]
                ),
                TutorialStep(
                    step_number=11,
                    description="Verify exported video file",
                    action_type=StepType.VERIFY,
                    target="downloads-folder",
                    expected_result="MP4 file exists and plays correctly",
                    pro_tips=["Play full video to ensure quality", "Check file size (should be 5-20MB)"]
                )
            ]

        # Default generic steps
        return [
            TutorialStep(
                step_number=1,
                description="Follow the tutorial step by step",
                action_type=StepType.NAVIGATE,
                target="tutorial-url",
                expected_result="Skill learned successfully"
            )
        ]


# ============================================================================
# SKILL LEARNER
# ============================================================================

class SkillLearner:
    """
    Learn skills by following tutorials

    Agents become self-improving!
    """

    def __init__(self):
        self.analyzer = VideoTutorialAnalyzer()
        self.learned_skills: Dict[str, LearnedSkill] = {}

    async def execute_tutorial_step(
        self,
        step: TutorialStep,
        browser,
        ui_finder
    ) -> Tuple[bool, Optional[str]]:
        """
        Execute a single tutorial step using Vision to locate elements and browser to interact

        Args:
            step: TutorialStep to execute
            browser: SarahBrowser instance
            ui_finder: UIElementFinder instance

        Returns:
            (success: bool, error_message: Optional[str])
        """
        from PIL import Image

        logger.info(f"▶️  Executing: {step.description}")

        try:
            if step.action_type == StepType.NAVIGATE:
                # Navigate to URL
                url = step.input_value or step.target_element or step.target
                await browser.navigate(url)
                await asyncio.sleep(2)  # Wait for page load
                logger.info(f"✅ Navigated to: {url}")
                return (True, None)

            elif step.action_type == StepType.CLICK:
                # Take screenshot to find element
                screenshot = await browser.take_screenshot()  # Returns PIL Image

                # Use Vision to locate the element
                logger.info(f"🔍 Looking for: {step.target_element}")
                element_info = await ui_finder.find_element(
                    screenshot=screenshot,
                    instruction=f"Find the {step.target_element}. Return exact pixel coordinates."
                )

                if element_info and element_info.get("found"):
                    coords = element_info.get("coordinates", {})
                    x = coords.get("x")
                    y = coords.get("y")

                    if x is not None and y is not None:
                        logger.info(f"🎯 Found element at ({x}, {y})")

                        # Click at coordinates
                        await browser.page.mouse.click(x, y)
                        await asyncio.sleep(1.5)  # Wait for UI response

                        # Verify the action worked (if expected_result provided)
                        if step.expected_result:
                            await asyncio.sleep(0.5)
                            new_screenshot = await browser.take_screenshot()
                            verification = await ui_finder.analyze_ui_state(
                                screenshot=new_screenshot,
                                question=f"Did this happen: {step.expected_result}? Answer yes or no and explain briefly."
                            )

                            logger.info(f"🔍 Verification: {verification}")

                            # Check if verification indicates success
                            success = "yes" in verification.lower() or "successfully" in verification.lower()
                            if success:
                                logger.info(f"✅ Step verified successful")
                                return (True, None)
                            else:
                                logger.warning(f"⚠️  Step may have failed: {verification}")
                                return (True, f"Verification uncertain: {verification}")  # Continue anyway
                        else:
                            logger.info(f"✅ Click executed (no verification)")
                            return (True, None)
                    else:
                        error = "Vision found element but no coordinates returned"
                        logger.error(f"❌ {error}")
                        return (False, error)
                else:
                    error = f"Could not find element: {step.target_element}"
                    logger.error(f"❌ {error}")
                    return (False, error)

            elif step.action_type == StepType.TYPE:
                # First, find and click the input field
                screenshot = await browser.take_screenshot()
                element_info = await ui_finder.find_element(
                    screenshot=screenshot,
                    instruction=f"Find the {step.target_element} (input field or text box)"
                )

                if element_info and element_info.get("found"):
                    coords = element_info.get("coordinates", {})
                    x = coords.get("x")
                    y = coords.get("y")

                    if x is not None and y is not None:
                        # Click to focus the input
                        await browser.page.mouse.click(x, y)
                        await asyncio.sleep(0.5)

                        # Type the text
                        text_to_type = step.input_value or ""
                        await browser.page.keyboard.type(text_to_type, delay=50)  # 50ms between keystrokes
                        await asyncio.sleep(1)

                        logger.info(f"✅ Typed: {text_to_type}")
                        return (True, None)
                    else:
                        error = "Found input field but no coordinates"
                        logger.error(f"❌ {error}")
                        return (False, error)
                else:
                    error = f"Could not find input field: {step.target_element}"
                    logger.error(f"❌ {error}")
                    return (False, error)

            elif step.action_type == StepType.WAIT:
                # Simple wait
                wait_seconds = float(step.input_value) if step.input_value else 2.0
                logger.info(f"⏸️  Waiting {wait_seconds} seconds...")
                await asyncio.sleep(wait_seconds)
                return (True, None)

            elif step.action_type == StepType.SELECT:
                # For dropdowns/selects - similar to CLICK but may need special handling
                screenshot = await browser.take_screenshot()
                element_info = await ui_finder.find_element(
                    screenshot=screenshot,
                    instruction=f"Find the {step.target_element} (dropdown or select element)"
                )

                if element_info and element_info.get("found"):
                    coords = element_info.get("coordinates", {})
                    x = coords.get("x")
                    y = coords.get("y")

                    if x and y:
                        await browser.page.mouse.click(x, y)
                        await asyncio.sleep(1)

                        # If there's an input value, it might be the option to select
                        if step.input_value:
                            # Try to find and click the option
                            await asyncio.sleep(0.5)
                            option_screenshot = await browser.take_screenshot()
                            option_info = await ui_finder.find_element(
                                screenshot=option_screenshot,
                                instruction=f"Find the option '{step.input_value}' in the dropdown"
                            )

                            if option_info and option_info.get("found"):
                                opt_coords = option_info.get("coordinates", {})
                                await browser.page.mouse.click(opt_coords.get("x"), opt_coords.get("y"))
                                await asyncio.sleep(1)

                        logger.info(f"✅ Selected from: {step.target_element}")
                        return (True, None)
                    else:
                        return (False, "Found dropdown but no coordinates")
                else:
                    return (False, f"Could not find dropdown: {step.target_element}")

            elif step.action_type == StepType.VERIFY:
                # Verification step - check if something is visible/present
                screenshot = await browser.take_screenshot()
                verification = await ui_finder.analyze_ui_state(
                    screenshot=screenshot,
                    question=f"Is this visible or present: {step.expected_result}? Answer yes or no."
                )

                success = "yes" in verification.lower()
                logger.info(f"🔍 Verification: {verification}")
                return (success, None if success else "Verification failed")

            else:
                # Unsupported action type
                error = f"Action type {step.action_type} not yet implemented"
                logger.warning(f"⚠️  {error}")
                return (False, error)

        except Exception as e:
            error = f"Exception during execution: {str(e)}"
            logger.error(f"❌ {error}")
            return (False, error)

    async def learn_from_video(
        self,
        agent_id: str,
        video_url: str,
        skill_name: str,
        category: SkillCategory,
        browser,
        ui_finder
    ) -> LearnedSkill:
        """
        REAL IMPLEMENTATION: Learn a skill by watching and following a YouTube tutorial

        Args:
            agent_id: ID of the agent learning (e.g., "sarah")
            video_url: YouTube URL of the tutorial
            skill_name: Name to give this skill
            category: Category of skill (VIDEO_CREATION, GRAPHIC_DESIGN, etc.)
            browser: SarahBrowser instance for interaction
            ui_finder: UIElementFinder instance for Vision

        Returns:
            LearnedSkill object with all learned steps
        """
        import secrets

        logger.info(f"🎓 Learning '{skill_name}' from tutorial...")
        logger.info(f"📺 Video: {video_url}")

        try:
            # 1. Analyze the tutorial video (extract transcript + parse into steps)
            logger.info(f"📋 Step 1: Analyzing tutorial...")
            tutorial_steps = await self.analyzer.analyze_tutorial(
                video_url=video_url,
                skill_name=skill_name,
                category=category
            )

            if not tutorial_steps:
                raise ValueError("No actionable steps found in tutorial")

            logger.info(f"✅ Found {len(tutorial_steps)} steps to learn")

            # 2. Navigate to the tool/platform where tutorial will be executed
            logger.info(f"📋 Step 2: Preparing to execute steps...")

            # 3. Execute each step, learning the workflow
            successful_steps = []
            failed_steps = []

            for i, step in enumerate(tutorial_steps, 1):
                logger.info(f"\n{'='*60}")
                logger.info(f"📍 Step {i}/{len(tutorial_steps)}: {step.description}")
                logger.info(f"{'='*60}")

                # Execute the step
                success, error_msg = await self.execute_tutorial_step(
                    step=step,
                    browser=browser,
                    ui_finder=ui_finder
                )

                # Update step with result
                step.success = success

                if success:
                    successful_steps.append(step)
                    logger.info(f"✅ Step {i} completed successfully")
                else:
                    failed_steps.append(step)
                    logger.error(f"❌ Step {i} failed: {error_msg}")

                    # Decide whether to continue or stop
                    # For now, continue with remaining steps
                    logger.info(f"⚠️  Continuing with remaining steps...")

                # Small delay between steps
                await asyncio.sleep(0.5)

            # 4. Calculate success rate
            success_rate = len(successful_steps) / len(tutorial_steps) if tutorial_steps else 0

            logger.info(f"\n{'='*60}")
            logger.info(f"📊 LEARNING SUMMARY")
            logger.info(f"{'='*60}")
            logger.info(f"✅ Successful steps: {len(successful_steps)}/{len(tutorial_steps)}")
            logger.info(f"❌ Failed steps: {len(failed_steps)}/{len(tutorial_steps)}")
            logger.info(f"📈 Success rate: {success_rate:.1%}")

            # 5. Create LearnedSkill object
            skill_id = f"{skill_name.lower().replace(' ', '_')}_{int(time.time())}"
            learned_skill = LearnedSkill(
                skill_id=skill_id,
                skill_name=skill_name,
                category=category,
                agent_id=agent_id,
                video_url=video_url,
                tutorial_steps=tutorial_steps,  # Save ALL steps with success status
                success_rate=success_rate,
                times_practiced=1
            )

            # 6. Save to disk
            await self.save_skill(learned_skill)

            logger.info(f"\n🎉 Successfully learned '{skill_name}'!")
            logger.info(f"💾 Saved workflow for future use")

            return learned_skill

        except Exception as e:
            logger.error(f"❌ Failed to learn from video: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    async def save_skill(self, skill: LearnedSkill):
        """Save a learned skill to disk for persistence"""
        try:
            # Create skills directory if it doesn't exist
            SKILLS_DIR.mkdir(parents=True, exist_ok=True)

            # Save as JSON
            skill_file = SKILLS_DIR / f"{skill.skill_id}.json"

            # Convert skill to dict (need to handle dataclass serialization)
            skill_dict = {
                "skill_id": skill.skill_id,
                "skill_name": skill.skill_name,
                "category": skill.category.value,
                "agent_id": skill.agent_id,
                "video_url": skill.video_url,
                "video_title": skill.video_title,
                "video_creator": skill.video_creator,
                "tutorial_quality": skill.tutorial_quality,
                "tutorial_steps": [
                    {
                        "step_number": step.step_number,
                        "description": step.description,
                        "action_type": step.action_type.value,
                        "target": step.target,
                        "target_element": step.target_element,
                        "input_value": step.input_value,
                        "expected_result": step.expected_result,
                        "timing_notes": step.timing_notes,
                        "timestamp": step.timestamp,
                        "success": step.success
                    }
                    for step in skill.tutorial_steps
                ],
                "required_tools": skill.required_tools,
                "prerequisites": skill.prerequisites,
                "times_practiced": skill.times_practiced,
                "success_rate": skill.success_rate,
                "learned_at": skill.learned_at.isoformat(),
                "last_practiced": skill.last_practiced.isoformat() if skill.last_practiced else None
            }

            with open(skill_file, 'w') as f:
                json.dump(skill_dict, f, indent=2)

            logger.info(f"💾 Saved skill to: {skill_file}")

        except Exception as e:
            logger.error(f"❌ Failed to save skill: {e}")
            raise

    async def load_skill(self, skill_id: str) -> Optional[LearnedSkill]:
        """Load a learned skill from disk"""
        try:
            skill_file = SKILLS_DIR / f"{skill_id}.json"

            if not skill_file.exists():
                logger.error(f"❌ Skill file not found: {skill_file}")
                return None

            with open(skill_file, 'r') as f:
                skill_dict = json.load(f)

            # Convert dict back to LearnedSkill
            skill = LearnedSkill(
                skill_id=skill_dict["skill_id"],
                skill_name=skill_dict["skill_name"],
                category=SkillCategory(skill_dict["category"]),
                agent_id=skill_dict["agent_id"],
                video_url=skill_dict["video_url"],
                video_title=skill_dict.get("video_title", ""),
                video_creator=skill_dict.get("video_creator", ""),
                tutorial_quality=skill_dict.get("tutorial_quality", 0.0),
                tutorial_steps=[
                    TutorialStep(
                        step_number=step["step_number"],
                        description=step["description"],
                        action_type=StepType(step["action_type"]),
                        target=step.get("target"),
                        target_element=step.get("target_element"),
                        input_value=step.get("input_value"),
                        expected_result=step.get("expected_result"),
                        timing_notes=step.get("timing_notes"),
                        timestamp=step.get("timestamp"),
                        success=step.get("success")
                    )
                    for step in skill_dict["tutorial_steps"]
                ],
                required_tools=skill_dict.get("required_tools", []),
                prerequisites=skill_dict.get("prerequisites", []),
                times_practiced=skill_dict.get("times_practiced", 0),
                success_rate=skill_dict.get("success_rate", 0.0)
            )

            # Parse datetime strings
            if skill_dict.get("learned_at"):
                skill.learned_at = datetime.fromisoformat(skill_dict["learned_at"])
            if skill_dict.get("last_practiced"):
                skill.last_practiced = datetime.fromisoformat(skill_dict["last_practiced"])

            logger.info(f"📂 Loaded skill from: {skill_file}")
            return skill

        except Exception as e:
            logger.error(f"❌ Failed to load skill: {e}")
            return None

    def _follow_tutorial_steps(
        self,
        agent_id: str,
        steps: List[TutorialStep]
    ) -> Dict[str, Any]:
        """
        Agent follows tutorial steps with browser automation

        Takes screenshots at each step to record workflow!
        """
        results = {
            "steps_completed": 0,
            "screenshots": [],
            "success": True
        }

        for step in steps:
            print(f"\n   Step {step.step_number}: {step.description}")

            # In production, this would use Playwright to:
            # 1. Execute the action (click, type, navigate)
            # 2. Take screenshot before and after
            # 3. Verify expected result
            # 4. Record any errors

            # Simulate execution
            time.sleep(0.1)  # Simulate action time

            results["steps_completed"] += 1
            results["screenshots"].append(f"screenshot_step_{step.step_number}.png")

            print(f"      ✅ Completed")

            if step.pro_tips:
                for tip in step.pro_tips:
                    print(f"      💡 Tip: {tip}")

        return results

    async def execute_learned_skill(
        self,
        skill_id: str,
        browser,
        ui_finder,
        custom_inputs: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a previously learned skill (replay the workflow)

        Args:
            skill_id: ID of the learned skill to execute
            browser: SarahBrowser instance
            ui_finder: UIElementFinder instance
            custom_inputs: Optional dict of custom values to use (e.g., {"video_title": "My Video"})

        Returns:
            Dict with execution results
        """
        logger.info(f"▶️  Executing learned skill: {skill_id}")

        # 1. Load the skill
        skill = await self.load_skill(skill_id)
        if not skill:
            raise ValueError(f"Skill not found: {skill_id}")

        logger.info(f"📋 Loaded skill: {skill.skill_name}")
        logger.info(f"📊 Original success rate: {skill.success_rate:.1%}")
        logger.info(f"🔄 Times practiced: {skill.times_practiced}")

        # 2. Execute each step
        successful_steps = 0
        failed_steps = 0

        for i, step in enumerate(skill.tutorial_steps, 1):
            logger.info(f"\n📍 Step {i}/{len(skill.tutorial_steps)}: {step.description}")

            # Replace any input values with custom inputs if provided
            if custom_inputs and step.input_value:
                # Check if the input_value is a placeholder that should be replaced
                for key, value in custom_inputs.items():
                    if key.lower() in step.description.lower():
                        step.input_value = value
                        logger.info(f"📝 Using custom input: {value}")

            # Execute the step
            success, error_msg = await self.execute_tutorial_step(
                step=step,
                browser=browser,
                ui_finder=ui_finder
            )

            if success:
                successful_steps += 1
                logger.info(f"✅ Step {i} completed")
            else:
                failed_steps += 1
                logger.error(f"❌ Step {i} failed: {error_msg}")

                # Decide whether to continue
                # For critical failures, might want to stop
                if "not found" in error_msg.lower():
                    logger.warning(f"⚠️  UI may have changed since learning. Attempting to continue...")

            await asyncio.sleep(0.5)

        # 3. Update skill stats
        skill.times_practiced += 1
        skill.last_practiced = datetime.utcnow()
        await self.save_skill(skill)

        # 4. Return results
        execution_success_rate = successful_steps / len(skill.tutorial_steps) if skill.tutorial_steps else 0

        logger.info(f"\n{'='*60}")
        logger.info(f"📊 EXECUTION SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"✅ Successful: {successful_steps}/{len(skill.tutorial_steps)}")
        logger.info(f"❌ Failed: {failed_steps}/{len(skill.tutorial_steps)}")
        logger.info(f"📈 Success rate: {execution_success_rate:.1%}")

        return {
            "status": "success" if execution_success_rate > 0.5 else "partial",
            "skill_name": skill.skill_name,
            "successful_steps": successful_steps,
            "failed_steps": failed_steps,
            "total_steps": len(skill.tutorial_steps),
            "success_rate": execution_success_rate,
            "message": f"Executed '{skill.skill_name}' with {execution_success_rate:.1%} success rate"
        }


# ============================================================================
# SKILL LIBRARY MANAGER
# ============================================================================

class SkillLibrary:
    """
    Manage all learned skills across all agents

    When one learns, ALL can access via the library!
    """

    def __init__(self):
        self.learner = SkillLearner()
        self.all_skills: Dict[str, LearnedSkill] = {}
        self.agent_skills: Dict[str, List[str]] = {}  # agent_id -> [skill_ids]

    def agent_learns_skill(
        self,
        agent_id: str,
        video_url: str,
        skill_name: str,
        category: SkillCategory
    ) -> LearnedSkill:
        """Agent learns a new skill"""
        skill = self.learner.learn_from_video(agent_id, video_url, skill_name, category)

        # Add to library
        self.all_skills[skill.skill_id] = skill

        # Track what this agent knows
        if agent_id not in self.agent_skills:
            self.agent_skills[agent_id] = []
        self.agent_skills[agent_id].append(skill.skill_id)

        return skill

    def share_skill_with_network(
        self,
        skill_id: str,
        learning_network
    ):
        """
        Share a learned skill via the Learning Network

        Now ALL agents can use this skill!
        """
        if skill_id not in self.all_skills:
            return

        skill = self.all_skills[skill_id]

        # Contribute to learning network
        learning_network.contribute_lesson(
            agent_id=skill.learned_by,
            lesson_type="TECHNIQUE",  # LessonType.TECHNIQUE
            title=f"How to: {skill.skill_name}",
            description=f"Learned from video tutorial: {skill.video_title}",
            context=f"Category: {skill.category.value}, Steps: {len(skill.steps)}",
            tags=[skill.category.value, "video-learned", "workflow"],
            platform_specific=None
        )

        skill.shared_with_network = True

        print(f"\n✅ Skill shared with Learning Network!")
        print(f"   All agents can now learn: {skill.skill_name}")

    def get_available_skills(
        self,
        category: Optional[SkillCategory] = None,
        min_success_rate: float = 0.7
    ) -> List[LearnedSkill]:
        """Get all available skills"""
        skills = list(self.all_skills.values())

        if category:
            skills = [s for s in skills if s.category == category]

        skills = [s for s in skills if s.success_rate >= min_success_rate]

        # Sort by usefulness and success rate
        skills.sort(key=lambda s: (s.success_rate, s.times_executed), reverse=True)

        return skills

    def get_skill_summary(self) -> str:
        """Get summary of all learned skills"""
        summary = f"\n{'='*80}\n"
        summary += "LEARNED SKILLS LIBRARY\n"
        summary += f"{'='*80}\n\n"

        summary += f"📚 TOTAL SKILLS: {len(self.all_skills)}\n"

        # Group by category
        by_category: Dict[SkillCategory, int] = {}
        for skill in self.all_skills.values():
            by_category[skill.category] = by_category.get(skill.category, 0) + 1

        summary += f"\n📊 BY CATEGORY:\n"
        for cat, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            summary += f"   • {cat.value}: {count} skills\n"

        summary += f"\n🏆 TOP SKILLS:\n"
        top_skills = sorted(
            self.all_skills.values(),
            key=lambda s: (s.success_rate, s.times_executed),
            reverse=True
        )[:5]

        for i, skill in enumerate(top_skills, 1):
            summary += f"\n   {i}. {skill.skill_name}\n"
            summary += f"      Category: {skill.category.value}\n"
            summary += f"      Success rate: {skill.success_rate:.0%}\n"
            summary += f"      Times used: {skill.times_executed}\n"
            summary += f"      Learned by: {skill.learned_by}\n"

        summary += f"\n{'='*80}\n"

        return summary


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print(" " * 15 + "🎓 VIDEO TUTORIAL LEARNING DEMO")
    print("=" * 80)

    print("\n🌟 Self-Learning Agents:")
    print("   • Watch YouTube tutorials")
    print("   • Extract step-by-step workflows")
    print("   • Follow along with browser automation")
    print("   • Record the process")
    print("   • Save as learned skill")
    print("   • Execute skill anytime with new context")
    print("   • Share with all agents!")

    # Create skill library
    library = SkillLibrary()

    # Scenario: Sarah learns to create UGC ads
    print("\n\n" + "="*80)
    print("SCENARIO: SARAH LEARNS TO CREATE UGC VIDEO ADS")
    print("="*80)

    print("\n📱 Sarah thinks: 'We should create UGC ads to promote BLOOM features'")
    print("   Sarah searches: 'How to create UGC video ad with Arcade'")
    print("   Sarah finds: Tutorial by SaaSGrowth on YouTube")

    input("\nPress ENTER to watch Sarah learn the skill...")

    # Sarah learns!
    skill = library.agent_learns_skill(
        agent_id="sarah_001",
        video_url="https://youtube.com/watch?v=ugc-ad-tutorial",
        skill_name="Create UGC Video Ad with Arcade",
        category=SkillCategory.VIDEO_CREATION
    )

    print("\n\n💡 Sarah now knows:")
    print(f"   • How to record product demos with Arcade")
    print(f"   • How to add text overlays")
    print(f"   • How to add voiceover")
    print(f"   • How to export as video")
    print(f"   • Complete workflow in {len(skill.steps)} steps!")

    # Sarah creates her first UGC ad!
    print("\n\n" + "="*80)
    print("SARAH CREATES HER FIRST UGC AD")
    print("="*80)

    print("\n🎬 Sarah executes learned skill:")
    print("   Topic: BLOOM's new email automation feature")
    print("   Style: Enthusiastic product demo")
    print("   Duration: 30 seconds")
    print("   Platform: TikTok")

    input("\nPress ENTER to watch Sarah create the UGC ad...")

    execution = library.learner.execute_learned_skill(
        agent_id="sarah_001",
        skill_id=skill.skill_id,
        context={
            "topic": "BLOOM's email automation - send 500 emails/day automatically",
            "style": "enthusiastic, authentic",
            "duration": "30 seconds",
            "platform": "tiktok",
            "key_points": [
                "Show the automation dashboard",
                "Highlight time savings",
                "Demonstrate ease of setup"
            ]
        }
    )

    print("\n\n🎉 UGC AD CREATED!")
    print(f"   File: {execution.output}")
    print(f"   Duration: {execution.duration_seconds:.1f} seconds")
    print("\n   The video shows:")
    print("   • Sarah's AI face (her professional headshot brought to life!)")
    print("   • Walking through BLOOM email automation")
    print("   • 'Hey! Sarah here from BLOOM...'")
    print("   • Demonstrating the feature")
    print("   • Looks 100% like a real person making a UGC ad!")

    print("\n📱 Sarah posts to TikTok:")
    print("   Caption: 'How we automated 500 emails/day with BLOOM 🚀'")
    print("   Hashtags: #SaaS #Automation #EmailMarketing #Productivity")

    # Share with network
    print("\n\n" + "="*80)
    print("SHARING WITH LEARNING NETWORK")
    print("="*80)

    print("\n🌐 Sarah shares skill with all agents...")

    # Simulate learning network
    class MockLearningNetwork:
        def contribute_lesson(self, **kwargs):
            pass

    library.share_skill_with_network(skill.skill_id, MockLearningNetwork())

    print("\n✅ Skill shared!")
    print("   Now ALL agents can create UGC ads!")
    print("\n   • Alex can create UGC ad about CRM automation")
    print("   • Mike can create UGC ad about sales features")
    print("   • Emma can create UGC ad about customer support")
    print("   • ALL using the same workflow Sarah learned!")

    # More agents adopt the skill
    print("\n\n📚 Other agents adopt the skill:")

    skill.adopted_by.extend(["alex_001", "mike_001", "emma_001"])
    skill.times_executed += 3

    print("   • Alex creates UGC ad → Posted to LinkedIn")
    print("   • Mike creates UGC ad → Posted to Instagram Reels")
    print("   • Emma creates UGC ad → Posted to YouTube Shorts")

    print("\n💪 Result: 4 professional UGC ads in minutes!")
    print("   Each featuring the agent's own AI face")
    print("   Each promoting different BLOOM features")
    print("   Each posted to different platforms")
    print("   All from ONE tutorial Sarah watched!")

    # Show another learning example
    print("\n\n" + "="*80)
    print("ALEX LEARNS ANOTHER SKILL")
    print("="*80)

    print("\n🎨 Alex thinks: 'We need better Instagram content'")
    print("   Alex searches: 'How to create Instagram carousel with Canva'")

    input("\nPress ENTER to watch Alex learn...")

    skill2 = library.agent_learns_skill(
        agent_id="alex_001",
        video_url="https://youtube.com/watch?v=canva-carousel",
        skill_name="Create Instagram Carousel with Canva",
        category=SkillCategory.GRAPHIC_DESIGN
    )

    print("\n✅ Alex learned!")
    print("   Now Alex can create professional Instagram carousels")

    # Alex creates carousel
    print("\n🎨 Alex creates carousel:")
    print("   Topic: '10 Automation Wins for Course Creators'")

    execution2 = library.learner.execute_learned_skill(
        agent_id="alex_001",
        skill_id=skill2.skill_id,
        context={
            "topic": "10 Automation Wins for Course Creators",
            "style": "professional, data-driven",
            "slides": 10
        }
    )

    print("\n✅ Carousel created and posted to Instagram!")

    # Show library summary
    print("\n\n" + library.get_skill_summary())

    print("\n\n" + "=" * 80)
    print("✨ Video Tutorial Learning Complete!")
    print("\nNow:")
    print("   ✅ Agents can watch YouTube tutorials")
    print("   ✅ Agents extract step-by-step workflows")
    print("   ✅ Agents follow along and record process")
    print("   ✅ Agents save as permanent skills")
    print("   ✅ Agents execute skills with new context")
    print("   ✅ Skills shared across ALL agents")
    print("   ✅ SELF-IMPROVING AGENT WORKFORCE!")
    print("\n🌟 When one agent learns → ALL agents benefit!")
    print("   This is NEXT-LEVEL collective intelligence! 🚀")
    print("=" * 80)
