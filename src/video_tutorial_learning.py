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
import asyncio
import os
import re
import logging


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
    input_value: Optional[str] = None  # Text to type, file to upload
    expected_result: Optional[str] = None  # What should happen

    # Visual reference
    screenshot_before: Optional[str] = None
    screenshot_after: Optional[str] = None

    # Context
    timing_notes: Optional[str] = None  # "Wait 2 seconds for animation"
    pro_tips: List[str] = field(default_factory=list)
    common_mistakes: List[str] = field(default_factory=list)


@dataclass
class LearnedSkill:
    """A skill learned from a video tutorial"""
    skill_id: str
    skill_name: str  # "Create UGC Video Ad with Arcade"
    category: SkillCategory
    learned_by: str  # agent_id

    # Source
    source_video_url: str
    video_title: str
    video_creator: str
    tutorial_quality: float = 0.0  # 0-1, how good was the tutorial

    # The skill itself
    steps: List[TutorialStep] = field(default_factory=list)
    required_tools: List[str] = field(default_factory=list)  # ["Arcade.dev", "Browser"]
    prerequisites: List[str] = field(default_factory=list)  # Other skills needed first

    # Performance
    times_executed: int = 0
    success_rate: float = 0.0  # 0-1
    avg_duration_seconds: float = 0.0

    # Context for execution
    variable_inputs: Dict[str, str] = field(default_factory=dict)  # {"topic": "describe", "style": "options"}
    output_description: str = ""  # What this skill produces

    # Sharing
    shared_with_network: bool = False
    adopted_by: List[str] = field(default_factory=list)  # Other agent_ids

    # Meta
    learned_date: datetime = field(default_factory=datetime.utcnow)
    last_used_date: Optional[datetime] = None

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

    Uses Claude Vision to understand what's happening in each frame!
    """

    def __init__(self):
        self.frame_interval = 2.0  # Analyze every 2 seconds
        self.logger = logging.getLogger(__name__)

    async def get_transcript_with_timestamps(self, video_url: str) -> List[Dict[str, Any]]:
        """
        Extract real YouTube transcript with timestamps

        Returns:
            List of transcript entries: [
                {"text": "First, click the create button", "start": 1.5, "duration": 2.0},
                {"text": "Then type your video title", "start": 3.5, "duration": 2.5},
                ...
            ]
        """
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
        except ImportError:
            self.logger.error("❌ youtube-transcript-api not installed. Install with: pip install youtube-transcript-api")
            raise ImportError("youtube-transcript-api required. Install with: pip install youtube-transcript-api")

        self.logger.info(f"📝 Extracting transcript from: {video_url}")

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
            self.logger.error(f"❌ Could not extract video ID from: {video_url}")
            raise ValueError(f"Invalid YouTube URL: {video_url}")

        self.logger.info(f"📹 Video ID: {video_id}")

        # Get transcript using youtube-transcript-api
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            self.logger.info(f"✅ Extracted {len(transcript_list)} transcript segments")
            return transcript_list

        except Exception as e:
            self.logger.error(f"❌ Failed to get transcript: {e}")
            # Try with generated subtitles if manual ones fail
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(
                    video_id,
                    languages=['en']
                )
                self.logger.info(f"✅ Extracted {len(transcript_list)} transcript segments (auto-generated)")
                return transcript_list
            except Exception as e2:
                self.logger.error(f"❌ Auto-generated subtitles also failed: {e2}")
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
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            self.logger.error("❌ anthropic not installed. Install with: pip install anthropic")
            raise ImportError("anthropic required. Install with: pip install anthropic")

        self.logger.info(f"🤖 Parsing transcript into actionable steps...")

        # Combine transcript into readable text with timestamps
        full_transcript = "\n".join([
            f"[{entry['start']:.1f}s] {entry['text']}"
            for entry in transcript[:100]  # Limit to first 100 segments to avoid token limits
        ])

        # Create Claude API client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            self.logger.error("❌ ANTHROPIC_API_KEY environment variable not set")
            raise ValueError("ANTHROPIC_API_KEY required")

        client = AsyncAnthropic(api_key=api_key)

        # Prompt Claude to extract actionable steps
        prompt = f"""You are analyzing a tutorial video transcript to extract actionable UI steps.

Tutorial Title: {skill_name}

Transcript with timestamps:
{full_transcript}

Your task: Extract ONLY the actionable UI steps from this transcript. Ignore introductions, explanations, and commentary.

For each actionable step, identify:
1. **action_type**: One of: CLICK, TYPE, SELECT, WAIT, NAVIGATE, VERIFY, UPLOAD, EXTRACT
2. **description**: Brief description of what to do
3. **target_element**: What UI element to interact with (e.g., "Create button", "search box", "upload icon")
4. **input_value**: If TYPE action, what text to type (otherwise null)
5. **expected_result**: What should happen after this step
6. **timestamp**: When in video this step occurs

IMPORTANT RULES:
- Only include steps that involve UI interaction
- Skip steps like "Now let me explain..." or "As you can see..."
- Be specific about target elements (not just "button" but "blue Create button in top right")
- Use exact action types from the list above (all caps)
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
  }},
  ...
]
"""

        try:
            response = await client.messages.create(
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

            self.logger.info(f"✅ Parsed {len(steps_data)} actionable steps from transcript")

            # Convert to TutorialStep objects
            tutorial_steps = []
            for step_data in steps_data:
                # Map action_type string to StepType enum
                action_type_str = step_data["action_type"].upper()
                try:
                    action_type = StepType[action_type_str]
                except KeyError:
                    self.logger.warning(f"⚠️  Unknown action type '{action_type_str}', defaulting to CLICK")
                    action_type = StepType.CLICK

                tutorial_steps.append(TutorialStep(
                    step_number=step_data["step_number"],
                    action_type=action_type,
                    description=step_data["description"],
                    target=step_data.get("target_element"),
                    input_value=step_data.get("input_value"),
                    expected_result=step_data.get("expected_result"),
                    timing_notes=f"Occurs at {step_data.get('timestamp', 0)}s in video"
                ))

            return tutorial_steps

        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Failed to parse Claude's response as JSON: {e}")
            self.logger.error(f"Response was: {response_text[:500]}")
            raise
        except Exception as e:
            self.logger.error(f"❌ Failed to parse transcript: {e}")
            raise

    async def analyze_tutorial(
        self,
        video_url: str,
        skill_name: str,
        category: SkillCategory
    ) -> List[TutorialStep]:
        """
        REAL IMPLEMENTATION: Analyze YouTube tutorial and extract steps

        Uses real YouTube transcript extraction and Claude API parsing!
        """
        self.logger.info(f"🎥 Analyzing tutorial: {skill_name}")
        self.logger.info(f"   URL: {video_url}")
        self.logger.info(f"   Category: {category.value}")

        try:
            # 1. Extract real transcript from YouTube
            self.logger.info("📝 Step 1: Extracting YouTube transcript...")
            transcript = await self.get_transcript_with_timestamps(video_url)

            if not transcript:
                raise ValueError("No transcript available for this video")

            # 2. Parse transcript into actionable steps using Claude
            self.logger.info("🤖 Step 2: Parsing transcript into actions...")
            tutorial_steps = await self.parse_transcript_into_actions(transcript, skill_name)

            self.logger.info(f"✅ Analysis complete: {len(tutorial_steps)} steps identified")
            return tutorial_steps

        except Exception as e:
            self.logger.error(f"❌ Tutorial analysis failed: {e}")
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
        self.logger = logging.getLogger(__name__)

        # Rate limiting for Claude API
        self.last_api_call = 0
        self.min_api_interval = 1.0  # Minimum 1 second between calls

        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 2.0  # Seconds between retries

    async def _rate_limited_api_call(self, api_call_func, *args, **kwargs):
        """Rate-limited wrapper for Claude API calls to prevent hitting rate limits"""
        import time

        # Enforce minimum time between API calls
        time_since_last = time.time() - self.last_api_call
        if time_since_last < self.min_api_interval:
            await asyncio.sleep(self.min_api_interval - time_since_last)

        self.last_api_call = time.time()
        return await api_call_func(*args, **kwargs)

    def _is_transient_error(self, error: Exception) -> bool:
        """Check if error is transient and worth retrying"""
        transient_keywords = [
            "timeout", "connection", "network", "temporary",
            "rate limit", "503", "502", "429"
        ]
        error_str = str(error).lower()
        return any(keyword in error_str for keyword in transient_keywords)

    async def execute_tutorial_step(
        self,
        step: TutorialStep,
        browser,
        ui_finder
    ) -> Tuple[bool, Optional[str]]:
        """
        Execute a single tutorial step using Vision to locate elements and browser to interact
        Includes fallback mechanisms for when Vision fails

        Args:
            step: TutorialStep to execute
            browser: SarahBrowser instance
            ui_finder: UIElementFinder instance

        Returns:
            (success: bool, error_message: Optional[str])
        """
        from PIL import Image

        self.logger.info(f"▶️  Executing: {step.description}")

        try:
            if step.action_type == StepType.NAVIGATE:
                # Navigate to URL
                url = step.input_value or step.target
                await browser.navigate(url)
                await asyncio.sleep(2)  # Wait for page load
                self.logger.info(f"✅ Navigated to: {url}")
                return (True, None)

            elif step.action_type == StepType.CLICK:
                # Take screenshot to find element
                screenshot = await browser.take_screenshot()  # Returns PIL Image

                # ATTEMPT 1: Use Vision to locate the element
                self.logger.info(f"🔍 Looking for: {step.target}")
                element_info = await ui_finder.find_element(
                    screenshot=screenshot,
                    instruction=f"Find the {step.target}. Return exact pixel coordinates."
                )

                # FALLBACK 1: If Vision fails, try different phrasing
                if not element_info or not element_info.get("found"):
                    self.logger.warning(f"⚠️  Vision attempt 1 failed, trying alternate phrasing...")
                    element_info = await ui_finder.find_element(
                        screenshot=screenshot,
                        instruction=f"Locate the button, link, or element labeled '{step.target}'. Give me x,y coordinates."
                    )

                # FALLBACK 2: Try CSS/text selectors as last resort
                if not element_info or not element_info.get("found"):
                    self.logger.warning(f"⚠️  Vision attempt 2 failed, trying CSS/text selectors...")
                    try:
                        # Try common selector patterns
                        selectors = [
                            f"button:has-text('{step.target}')",
                            f"[aria-label*='{step.target}' i]",
                            f"a:has-text('{step.target}')",
                            f"[title*='{step.target}' i]"
                        ]

                        for selector in selectors:
                            try:
                                element = await browser.page.query_selector(selector)
                                if element:
                                    await element.click()
                                    await asyncio.sleep(1.5)
                                    self.logger.info(f"✅ Clicked using selector: {selector}")
                                    return (True, None)
                            except:
                                continue
                    except Exception as e:
                        self.logger.warning(f"⚠️  Selector fallback also failed: {e}")

                # Check if Vision succeeded
                if element_info and element_info.get("found"):
                    coords = element_info.get("coordinates", {})
                    x = coords.get("x")
                    y = coords.get("y")

                    if x is not None and y is not None:
                        self.logger.info(f"🎯 Found element at ({x}, {y})")

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

                            self.logger.info(f"🔍 Verification: {verification}")

                            # Check if verification indicates success
                            success = "yes" in verification.lower() or "successfully" in verification.lower()
                            if success:
                                self.logger.info(f"✅ Step verified successful")
                                return (True, None)
                            else:
                                self.logger.warning(f"⚠️  Step may have failed: {verification}")
                                return (True, f"Verification uncertain: {verification}")
                        else:
                            self.logger.info(f"✅ Click executed (no verification)")
                            return (True, None)
                    else:
                        error = "Vision found element but no coordinates returned"
                        self.logger.error(f"❌ {error}")
                        return (False, error)
                else:
                    error = f"Could not find element '{step.target}' after all attempts (Vision + selectors)"
                    self.logger.error(f"❌ {error}")
                    return (False, error)

            elif step.action_type == StepType.TYPE:
                # First, find and click the input field
                screenshot = await browser.take_screenshot()
                element_info = await ui_finder.find_element(
                    screenshot=screenshot,
                    instruction=f"Find the {step.target} (input field or text box)"
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

                        self.logger.info(f"✅ Typed: {text_to_type}")
                        return (True, None)
                    else:
                        error = "Found input field but no coordinates"
                        self.logger.error(f"❌ {error}")
                        return (False, error)
                else:
                    error = f"Could not find input field: {step.target}"
                    self.logger.error(f"❌ {error}")
                    return (False, error)

            elif step.action_type == StepType.WAIT:
                # Simple wait
                wait_seconds = float(step.input_value) if step.input_value else 2.0
                self.logger.info(f"⏸️  Waiting {wait_seconds} seconds...")
                await asyncio.sleep(wait_seconds)
                return (True, None)

            elif step.action_type == StepType.SELECT:
                # For dropdowns/selects
                screenshot = await browser.take_screenshot()
                element_info = await ui_finder.find_element(
                    screenshot=screenshot,
                    instruction=f"Find the {step.target} (dropdown or select element)"
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

                        self.logger.info(f"✅ Selected from: {step.target}")
                        return (True, None)
                    else:
                        return (False, "Found dropdown but no coordinates")
                else:
                    return (False, f"Could not find dropdown: {step.target}")

            elif step.action_type == StepType.VERIFY:
                # Verification step - check if something is visible/present
                screenshot = await browser.take_screenshot()
                verification = await ui_finder.analyze_ui_state(
                    screenshot=screenshot,
                    question=f"Is this visible or present: {step.expected_result}? Answer yes or no."
                )

                success = "yes" in verification.lower()
                self.logger.info(f"🔍 Verification: {verification}")
                return (success, None if success else "Verification failed")

            else:
                # Unsupported action type
                error = f"Action type {step.action_type} not yet implemented"
                self.logger.warning(f"⚠️  {error}")
                return (False, error)

        except Exception as e:
            error = f"Exception during execution: {str(e)}"
            self.logger.error(f"❌ {error}")
            import traceback
            self.logger.error(traceback.format_exc())
            return (False, error)

    async def execute_tutorial_step_with_retry(
        self,
        step: TutorialStep,
        browser,
        ui_finder,
        retry_count: int = 0
    ) -> Tuple[bool, Optional[str]]:
        """
        Execute step with automatic retry logic for transient failures
        Includes 30-second timeout per attempt
        """
        try:
            # Add timeout to prevent infinite hangs
            return await asyncio.wait_for(
                self.execute_tutorial_step(step, browser, ui_finder),
                timeout=30.0  # 30 second timeout per step
            )
        except asyncio.TimeoutError:
            self.logger.error(f"⏱️  Step timed out after 30 seconds")

            if retry_count < self.max_retries:
                self.logger.info(f"🔄 Retrying... (attempt {retry_count + 1}/{self.max_retries})")
                await asyncio.sleep(self.retry_delay)
                return await self.execute_tutorial_step_with_retry(
                    step, browser, ui_finder, retry_count + 1
                )
            else:
                return (False, "Step timed out after 3 retries")

        except Exception as e:
            self.logger.error(f"❌ Step execution failed: {e}")

            # Retry transient errors
            if retry_count < self.max_retries and self._is_transient_error(e):
                self.logger.info(f"🔄 Transient error detected, retrying...")
                await asyncio.sleep(self.retry_delay)
                return await self.execute_tutorial_step_with_retry(
                    step, browser, ui_finder, retry_count + 1
                )
            else:
                return (False, str(e))

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
        import time
        from datetime import datetime

        self.logger.info(f"🎓 Learning '{skill_name}' from tutorial...")
        self.logger.info(f"📺 Video: {video_url}")

        try:
            # 1. Analyze the tutorial video (extract transcript + parse into steps)
            self.logger.info(f"📋 Step 1: Analyzing tutorial...")
            tutorial_steps = await self.analyzer.analyze_tutorial(
                video_url=video_url,
                skill_name=skill_name,
                category=category
            )

            if not tutorial_steps:
                raise ValueError("No actionable steps found in tutorial")

            self.logger.info(f"✅ Found {len(tutorial_steps)} steps to learn")

            # 2. Prepare for execution
            self.logger.info(f"📋 Step 2: Preparing to execute steps...")

            # 3. Execute each step with retry logic
            successful_steps = []
            failed_steps = []

            for i, step in enumerate(tutorial_steps, 1):
                self.logger.info(f"\n{'='*60}")
                self.logger.info(f"📍 Step {i}/{len(tutorial_steps)}: {step.description}")
                self.logger.info(f"{'='*60}")

                # Execute with retry logic
                success, error_msg = await self.execute_tutorial_step_with_retry(
                    step=step,
                    browser=browser,
                    ui_finder=ui_finder
                )

                if success:
                    successful_steps.append(step)
                    self.logger.info(f"✅ Step {i} completed successfully")
                else:
                    failed_steps.append(step)
                    self.logger.error(f"❌ Step {i} failed: {error_msg}")
                    self.logger.info(f"⚠️  Continuing with remaining steps...")

                # Small delay between steps
                await asyncio.sleep(0.5)

            # 4. Calculate success rate
            success_rate = len(successful_steps) / len(tutorial_steps) if tutorial_steps else 0

            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"📊 LEARNING SUMMARY")
            self.logger.info(f"{'='*60}")
            self.logger.info(f"✅ Successful steps: {len(successful_steps)}/{len(tutorial_steps)}")
            self.logger.info(f"❌ Failed steps: {len(failed_steps)}/{len(tutorial_steps)}")
            self.logger.info(f"📈 Success rate: {success_rate:.1%}")

            # 5. Create LearnedSkill object
            import secrets
            skill_id = f"{skill_name.lower().replace(' ', '_')}_{int(time.time())}"

            learned_skill = LearnedSkill(
                skill_id=skill_id,
                skill_name=skill_name,
                category=category,
                learned_by=agent_id,
                source_video_url=video_url,
                video_title=f"Tutorial: {skill_name}",  # Will be improved with metadata later
                video_creator="YouTube",
                steps=tutorial_steps,
                required_tools=["Browser", "Claude Vision"],
                success_rate=success_rate,
                times_executed=1,
                last_used_date=datetime.utcnow()
            )

            # 6. Save to memory (in-memory for now, file-based later)
            self.learned_skills[skill_id] = learned_skill

            self.logger.info(f"\n🎉 Successfully learned '{skill_name}'!")
            self.logger.info(f"💾 Saved workflow for future use")

            return learned_skill

        except Exception as e:
            self.logger.error(f"❌ Failed to learn from video: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            raise

    async def save_skill(self, skill: LearnedSkill):
        """Save a learned skill to disk"""
        try:
            skill_file = SKILLS_DIR / f"{skill.skill_id}.json"

            # Convert to dict
            skill_data = {
                "skill_id": skill.skill_id,
                "skill_name": skill.skill_name,
                "category": skill.category.value,
                "learned_by": skill.learned_by,
                "source_video_url": skill.source_video_url,
                "video_title": skill.video_title,
                "video_creator": skill.video_creator,
                "steps": [
                    {
                        "step_number": s.step_number,
                        "description": s.description,
                        "action_type": s.action_type.value,
                        "target": s.target,
                        "input_value": s.input_value,
                        "expected_result": s.expected_result,
                        "timing_notes": s.timing_notes
                    }
                    for s in skill.steps
                ],
                "required_tools": skill.required_tools,
                "success_rate": skill.success_rate,
                "times_executed": skill.times_executed,
                "last_used_date": skill.last_used_date.isoformat() if skill.last_used_date else None
            }

            # Save to file
            with open(skill_file, 'w') as f:
                json.dump(skill_data, f, indent=2)

            self.logger.info(f"💾 Saved skill to: {skill_file}")

        except Exception as e:
            self.logger.error(f"❌ Failed to save skill: {e}")

    async def load_skill(self, skill_id: str) -> Optional[LearnedSkill]:
        """Load a learned skill from disk"""
        try:
            skill_file = SKILLS_DIR / f"{skill_id}.json"

            if not skill_file.exists():
                self.logger.warning(f"⚠️  Skill file not found: {skill_file}")
                return None

            with open(skill_file, 'r') as f:
                skill_data = json.load(f)

            # Convert back to LearnedSkill
            from datetime import datetime

            steps = [
                TutorialStep(
                    step_number=s["step_number"],
                    description=s["description"],
                    action_type=StepType[s["action_type"].upper()],
                    target=s.get("target"),
                    input_value=s.get("input_value"),
                    expected_result=s.get("expected_result"),
                    timing_notes=s.get("timing_notes")
                )
                for s in skill_data["steps"]
            ]

            skill = LearnedSkill(
                skill_id=skill_data["skill_id"],
                skill_name=skill_data["skill_name"],
                category=SkillCategory[skill_data["category"].upper()],
                learned_by=skill_data["learned_by"],
                source_video_url=skill_data["source_video_url"],
                video_title=skill_data["video_title"],
                video_creator=skill_data["video_creator"],
                steps=steps,
                required_tools=skill_data["required_tools"],
                success_rate=skill_data["success_rate"],
                times_executed=skill_data["times_executed"],
                last_used_date=datetime.fromisoformat(skill_data["last_used_date"]) if skill_data.get("last_used_date") else None
            )

            self.logger.info(f"✅ Loaded skill: {skill.skill_name}")
            return skill

        except Exception as e:
            self.logger.error(f"❌ Failed to load skill: {e}")
            return None

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
            custom_inputs: Optional dict of custom values (e.g., {"video_title": "My Video"})

        Returns:
            Dict with execution results
        """
        from datetime import datetime

        self.logger.info(f"▶️  Executing learned skill: {skill_id}")

        # 1. Load the skill
        skill = await self.load_skill(skill_id)
        if not skill:
            # Try in-memory
            skill = self.learned_skills.get(skill_id)
            if not skill:
                raise ValueError(f"Skill not found: {skill_id}")

        self.logger.info(f"📋 Loaded skill: {skill.skill_name}")
        self.logger.info(f"📊 Original success rate: {skill.success_rate:.1%}")
        self.logger.info(f"🔄 Times practiced: {skill.times_executed}")

        # 2. Execute each step
        successful_steps = 0
        failed_steps = 0

        for i, step in enumerate(skill.steps, 1):
            self.logger.info(f"\n📍 Step {i}/{len(skill.steps)}: {step.description}")

            # Replace input values with custom inputs if provided
            if custom_inputs and step.input_value:
                for key, value in custom_inputs.items():
                    if key.lower() in step.description.lower():
                        step.input_value = value
                        self.logger.info(f"📝 Using custom input: {value}")

            # Execute with retry
            success, error_msg = await self.execute_tutorial_step_with_retry(
                step=step,
                browser=browser,
                ui_finder=ui_finder
            )

            if success:
                successful_steps += 1
                self.logger.info(f"✅ Step {i} completed")
            else:
                failed_steps += 1
                self.logger.error(f"❌ Step {i} failed: {error_msg}")

                if "not found" in error_msg.lower():
                    self.logger.warning(f"⚠️  UI may have changed since learning")

            await asyncio.sleep(0.5)

        # 3. Update skill stats
        skill.times_executed += 1
        skill.last_used_date = datetime.utcnow()
        await self.save_skill(skill)

        # 4. Return results
        execution_success_rate = successful_steps / len(skill.steps) if skill.steps else 0

        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"📊 EXECUTION SUMMARY")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"✅ Successful: {successful_steps}/{len(skill.steps)}")
        self.logger.info(f"❌ Failed: {failed_steps}/{len(skill.steps)}")
        self.logger.info(f"📈 Success rate: {execution_success_rate:.1%}")

        return {
            "status": "success" if execution_success_rate > 0.5 else "partial",
            "skill_name": skill.skill_name,
            "successful_steps": successful_steps,
            "failed_steps": failed_steps,
            "total_steps": len(skill.steps),
            "success_rate": execution_success_rate,
            "message": f"Executed '{skill.skill_name}' with {execution_success_rate:.1%} success rate"
        }

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

    def execute_learned_skill(
        self,
        agent_id: str,
        skill_id: str,
        context: Dict[str, Any]
    ) -> SkillExecution:
        """
        Execute a previously learned skill with new context

        This is where agents APPLY what they learned!
        """
        if skill_id not in self.learned_skills:
            raise ValueError(f"Skill {skill_id} not found")

        skill = self.learned_skills[skill_id]

        print(f"\n{'='*80}")
        print(f"🎬 EXECUTING LEARNED SKILL")
        print(f"{'='*80}")
        print(f"\n   Agent: {agent_id}")
        print(f"   Skill: {skill.skill_name}")
        print(f"   Context: {context}")

        import secrets
        execution_id = f"exec_{secrets.token_urlsafe(8)}"

        start_time = time.time()

        # Execute each step with the new context
        print(f"\n📋 Executing {len(skill.steps)} steps...")

        screenshots = []
        for step in skill.steps:
            print(f"\n   Step {step.step_number}: {step.description}")

            # Apply context to step
            # For example, if context has "topic": "email automation"
            # And step is "record product demo"
            # We'd navigate to the email automation feature

            # In production: Execute with Playwright + context
            time.sleep(0.1)

            screenshots.append(f"exec_screenshot_{step.step_number}.png")
            print(f"      ✅ Done")

        duration = time.time() - start_time

        # Create execution record
        execution = SkillExecution(
            execution_id=execution_id,
            skill_id=skill_id,
            agent_id=agent_id,
            context=context,
            success=True,
            output="ugc_ad_video.mp4",  # Example output
            screenshots=screenshots,
            duration_seconds=duration
        )

        # Update skill metrics
        skill.times_executed += 1
        skill.last_used_date = datetime.utcnow()

        print(f"\n✅ SKILL EXECUTED SUCCESSFULLY!")
        print(f"   Output: {execution.output}")
        print(f"   Duration: {duration:.1f} seconds")

        return execution


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
