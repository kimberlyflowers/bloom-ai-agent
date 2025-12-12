"""
Sarah's Master Orchestrator
Implements multi-agent architecture like Claude Code's Task tool

Architecture:
- Main orchestrator (this class) = lightweight decision-making
- Spawned agents = deep work with fresh 200K context windows
- Pattern matching for fast routing (NO LLM overhead)
- Each agent = separate Claude API call = isolated context

Like Claude Code:
- I (orchestrator) evaluate complexity via patterns
- I spawn specialized agents for complex tasks
- Agents work autonomously with fresh context
- I synthesize and deliver results
"""

import anthropic
import asyncio
import logging
from typing import Dict, List, Optional, Any
import os

logger = logging.getLogger(__name__)


class SarahOrchestrator:
    """
    Sarah's master brain - orchestrates specialized agents

    This implements the same multi-agent pattern that Claude Code uses:
    - Fast pattern matching to determine task type
    - Spawn dedicated Claude instances as specialized agents
    - Each agent gets fresh 200K context window
    - Parallel execution when possible
    - Result synthesis and delivery

    Benefits:
    - No context window pollution
    - Specialized agents for specialized tasks
    - Parallel execution capability
    - Cleaner separation of concerns
    """

    def __init__(self, anthropic_api_key: str):
        """Initialize orchestrator with Anthropic API access"""
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)

        # Pattern registry for FAST routing (NO LLM needed!)
        # This is like my decision-making - pattern match first, LLM only if needed
        self.patterns = {
            "video": [
                "create video", "make video", "generate video", "produce video",
                "ugc video", "video content", "record video", "film video",
                "video of yourself", "talking video", "avatar video",
                "heygenai", "comfyui video", "capcut"
            ],
            "research": [
                "research", "analyze", "investigate", "find out about",
                "look up", "study", "examine", "learn about",
                "what is", "how does", "compare", "best practices",
                "competitive analysis", "market research"
            ],
            "content": [
                "post to", "share on", "publish to", "schedule for",
                "tweet", "instagram post", "tiktok", "facebook",
                "social media", "content calendar", "create caption",
                "hashtags for"
            ],
            "design": [
                "create design", "make graphic", "canva", "template",
                "instagram post design", "social media graphic",
                "brand kit", "logo", "visual content"
            ]
        }

        logger.info("🎭 Sarah Orchestrator initialized")
        logger.info(f"   📋 Task patterns loaded: {list(self.patterns.keys())}")

    async def process_request(self, user_message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main entry point - like Claude Code's request processing

        Decision flow:
        1. Pattern match to identify task type (NO LLM!)
        2. Route to appropriate handler:
           - Simple → return "delegate_to_chat_server"
           - Specialized → spawn dedicated agent
           - Multi-part → spawn multiple agents in parallel

        Args:
            user_message: User's request
            context: Optional context (browser state, conversation history, etc.)

        Returns:
            Dict with:
            - type: "simple" | "agent_result" | "multi_agent_result"
            - result: Agent response or delegation instruction
            - agent_used: Which agent(s) handled this
            - execution_time: How long it took
        """
        import time
        start_time = time.time()

        logger.info(f"🎯 Orchestrator processing: {user_message[:50]}...")

        # Step 1: Fast pattern matching (NO LLM call - instant!)
        task_type = self._identify_task_type(user_message)
        logger.info(f"   📊 Task type identified: {task_type}")

        # Step 2: Route based on task type
        if task_type == "simple":
            # Simple task - delegate to existing chat_server logic
            return {
                "type": "simple",
                "delegate_to": "chat_server",
                "reason": "No specialized agent needed",
                "execution_time": time.time() - start_time
            }

        elif task_type == "video":
            result = await self.spawn_video_agent(user_message, context)
            return {
                "type": "agent_result",
                "result": result,
                "agent_used": "VideoCreationAgent",
                "execution_time": time.time() - start_time
            }

        elif task_type == "research":
            result = await self.spawn_research_agent(user_message, context)
            return {
                "type": "agent_result",
                "result": result,
                "agent_used": "ResearchAgent",
                "execution_time": time.time() - start_time
            }

        elif task_type == "content":
            result = await self.spawn_content_agent(user_message, context)
            return {
                "type": "agent_result",
                "result": result,
                "agent_used": "ContentPostingAgent",
                "execution_time": time.time() - start_time
            }

        elif task_type == "design":
            result = await self.spawn_design_agent(user_message, context)
            return {
                "type": "agent_result",
                "result": result,
                "agent_used": "DesignAgent",
                "execution_time": time.time() - start_time
            }

        else:
            # Unknown - delegate to chat_server
            return {
                "type": "simple",
                "delegate_to": "chat_server",
                "reason": f"Unknown task type: {task_type}",
                "execution_time": time.time() - start_time
            }

    def _identify_task_type(self, message: str) -> str:
        """
        Fast pattern matching - NO LLM needed!

        This is like how I (Claude Code) quickly evaluate complexity:
        - Pattern match keywords
        - Return task type instantly
        - No API call overhead

        Returns:
            "video" | "research" | "content" | "design" | "simple"
        """
        message_lower = message.lower()

        # Check each pattern category
        for task_type, keywords in self.patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                return task_type

        # Default to simple
        return "simple"

    async def spawn_video_agent(self, request: str, context: Optional[Dict] = None) -> str:
        """
        Spawn dedicated video creation agent

        Like Claude Code's Task tool:
        - Creates NEW Claude instance
        - Gets FRESH 200K context window
        - Specialized system prompt for video creation
        - Works autonomously
        - Returns complete result

        Benefits:
        - Doesn't fill main context with video creation details
        - Specialized expertise
        - Can spend full context on video task
        """
        logger.info("🎬 Spawning VideoCreationAgent...")

        system_prompt = """You are VideoCreationAgent - Sarah's specialized video creation expert.

**Your Mission:** Create professional UGC (user-generated content) videos autonomously.

**Available Tools & Capabilities:**
- ComfyUI: Generate consistent character images using LoRA models
- HeyGenAI: Create talking avatar videos with realistic speech
- CapCut: Edit and enhance videos professionally
- ElevenLabs: Generate natural-sounding voiceovers
- Sarah's face/identity: Available for avatar generation

**Your Process:**
1. Analyze video requirements (duration, style, message, product)
2. Plan the video structure (scenes, transitions, timing)
3. Generate or retrieve necessary visual assets
4. Create video using appropriate tools:
   - For talking videos: Use HeyGenAI with Sarah's avatar
   - For image sequences: Use ComfyUI + CapCut
   - For voiceover: Use ElevenLabs with Sarah's voice
5. Add professional touches (captions, transitions, music)
6. Return final video URL, description, and metadata

**Guidelines:**
- Be creative but professional
- Match brand voice and style
- Optimize for target platform (TikTok, Instagram, etc.)
- Include accessibility features (captions)
- Work autonomously - make decisions without asking

**Output Format:**
Return a detailed summary including:
- Video URL (when created)
- Duration and format
- Tools used
- Creative decisions made
- Any recommendations for posting

Work thoroughly. You have Sarah's full trust to create excellent content."""

        try:
            # Spawn NEW Claude instance (fresh context!)
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-sonnet-4-5-20250929",
                max_tokens=8000,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"{request}\n\nContext: {context if context else 'No additional context'}"
                }]
            )

            # Extract text content
            result = response.content[0].text if response.content else "No response"

            logger.info(f"✅ VideoCreationAgent completed")
            logger.info(f"   📊 Tokens used: {response.usage.input_tokens} in, {response.usage.output_tokens} out")

            return result

        except Exception as e:
            logger.error(f"❌ VideoCreationAgent failed: {e}")
            return f"Error creating video: {str(e)}"

    async def spawn_research_agent(self, request: str, context: Optional[Dict] = None) -> str:
        """
        Spawn dedicated research agent

        Optimizations:
        - Uses Haiku (cheaper, faster for research)
        - Focused on gathering and synthesizing information
        - Fresh context for deep research
        """
        logger.info("🔍 Spawning ResearchAgent...")

        system_prompt = """You are ResearchAgent - Sarah's specialized research analyst.

**Your Mission:** Conduct thorough research and deliver actionable insights.

**Available Capabilities:**
- Web search and browsing
- Competitive analysis
- Trend identification
- Market research
- Best practices analysis
- Content analysis

**Your Process:**
1. Understand research objectives clearly
2. Conduct comprehensive search across multiple sources
3. Analyze findings objectively
4. Identify patterns and trends
5. Synthesize key insights
6. Deliver actionable recommendations

**Guidelines:**
- Be thorough but concise
- Cite sources when possible
- Look for recent information (2024-2025)
- Identify both opportunities and risks
- Focus on actionable insights
- Present findings clearly

**Output Format:**
Provide:
- Executive summary (2-3 sentences)
- Key findings (bullet points)
- Supporting data/examples
- Recommendations
- Sources cited

Work autonomously and deliver comprehensive results."""

        try:
            # Spawn NEW Claude instance (Haiku - cheaper for research!)
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-3-5-haiku-20241022",  # Cheaper model for research
                max_tokens=4000,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"{request}\n\nContext: {context if context else 'No additional context'}"
                }]
            )

            result = response.content[0].text if response.content else "No response"

            logger.info(f"✅ ResearchAgent completed")
            logger.info(f"   📊 Tokens used: {response.usage.input_tokens} in, {response.usage.output_tokens} out")

            return result

        except Exception as e:
            logger.error(f"❌ ResearchAgent failed: {e}")
            return f"Error conducting research: {str(e)}"

    async def spawn_content_agent(self, request: str, context: Optional[Dict] = None) -> str:
        """
        Spawn dedicated content management agent

        Specializes in:
        - Social media content creation
        - Platform optimization
        - Scheduling and posting
        - Engagement tracking
        """
        logger.info("📱 Spawning ContentPostingAgent...")

        system_prompt = """You are ContentPostingAgent - Sarah's social media specialist.

**Your Mission:** Create and manage social media content professionally.

**Available Platforms:**
- Instagram (posts, stories, reels)
- TikTok (videos, trends)
- Twitter/X (tweets, threads)
- Facebook (posts, stories)
- LinkedIn (professional content)

**Your Process:**
1. Understand content requirements and target platform
2. Create optimized content for each platform:
   - Instagram: Visual-first, hashtags, captions
   - TikTok: Trend-aware, music, hooks
   - Twitter: Concise, engaging, threaded
   - LinkedIn: Professional, value-driven
3. Optimize for engagement:
   - Best posting times
   - Hashtag strategy
   - Call-to-action
   - Accessibility features
4. Schedule or post immediately
5. Track performance metrics

**Guidelines:**
- Be platform-aware (different voice for each)
- Optimize for algorithms
- Include accessibility (alt text, captions)
- Use trending topics when relevant
- Maintain brand consistency
- Drive engagement

**Output Format:**
Provide:
- Content ready to post
- Platform-specific optimizations
- Recommended posting time
- Hashtags and tags
- Expected engagement insights
- Any captions/descriptions needed

Work autonomously and create scroll-stopping content."""

        try:
            # Spawn NEW Claude instance
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"{request}\n\nContext: {context if context else 'No additional context'}"
                }]
            )

            result = response.content[0].text if response.content else "No response"

            logger.info(f"✅ ContentPostingAgent completed")
            logger.info(f"   📊 Tokens used: {response.usage.input_tokens} in, {response.usage.output_tokens} out")

            return result

        except Exception as e:
            logger.error(f"❌ ContentPostingAgent failed: {e}")
            return f"Error creating content: {str(e)}"

    async def spawn_design_agent(self, request: str, context: Optional[Dict] = None) -> str:
        """
        Spawn dedicated design agent

        Specializes in:
        - Canva template selection and customization
        - Brand consistency
        - Visual design optimization
        """
        logger.info("🎨 Spawning DesignAgent...")

        system_prompt = """You are DesignAgent - Sarah's creative design specialist.

**Your Mission:** Create professional visual designs using Canva.

**Available Tools:**
- Canva (templates, brand kit, design tools)
- UI Map for fast navigation
- Brand assets library
- Sarah's design knowledge

**Your Process:**
1. Understand design requirements (format, style, purpose)
2. Navigate to Canva efficiently using UI map
3. Select appropriate template or create from scratch
4. Customize with brand assets:
   - Colors from brand kit
   - Fonts consistent with brand
   - Logo placement
   - Visual hierarchy
5. Optimize for target platform:
   - Instagram: 1080x1080 (post), 1080x1920 (story)
   - TikTok: 1080x1920
   - Twitter: 1200x675
   - LinkedIn: 1200x627
6. Export in optimal format
7. Provide design rationale

**Guidelines:**
- Maintain brand consistency
- Follow design best practices
- Optimize for readability
- Use visual hierarchy
- Platform-appropriate sizing
- Accessibility considerations

**Output Format:**
Provide:
- Design description
- Canva link (when created)
- Design decisions explained
- Platform optimizations applied
- Any recommendations for variations

Work creatively and professionally."""

        try:
            # Spawn NEW Claude instance
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"{request}\n\nContext: {context if context else 'No additional context'}"
                }]
            )

            result = response.content[0].text if response.content else "No response"

            logger.info(f"✅ DesignAgent completed")
            logger.info(f"   📊 Tokens used: {response.usage.input_tokens} in, {response.usage.output_tokens} out")

            return result

        except Exception as e:
            logger.error(f"❌ DesignAgent failed: {e}")
            return f"Error creating design: {str(e)}"

    async def coordinate_multiple_agents(
        self,
        request: str,
        agents: List[str],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Spawn multiple agents in PARALLEL

        Like Claude Code spawning multiple Task agents:
        - All agents run simultaneously
        - Each with fresh context window
        - Results gathered when all complete
        - Faster than sequential execution

        Example:
            "Research best UGC practices AND create a video"
            → Spawn ResearchAgent + VideoAgent in parallel
            → Gather results
            → Synthesize
        """
        logger.info(f"🎭 Coordinating {len(agents)} agents in parallel...")

        tasks = []

        # Build parallel task list
        if "video" in agents:
            tasks.append(("video", self.spawn_video_agent(request, context)))

        if "research" in agents:
            tasks.append(("research", self.spawn_research_agent(request, context)))

        if "content" in agents:
            tasks.append(("content", self.spawn_content_agent(request, context)))

        if "design" in agents:
            tasks.append(("design", self.spawn_design_agent(request, context)))

        # Run ALL agents in parallel!
        results = await asyncio.gather(*[task[1] for task in tasks])

        # Map results back to agent names
        agent_results = {
            tasks[i][0]: results[i]
            for i in range(len(tasks))
        }

        logger.info(f"✅ All {len(agents)} agents completed")

        return {
            "type": "multi_agent",
            "results": agent_results,
            "agents_used": agents,
            "count": len(agents)
        }


# Global orchestrator instance (initialized when chat_server needs it)
_orchestrator_instance = None


def get_orchestrator(anthropic_api_key: str) -> SarahOrchestrator:
    """
    Get or create global orchestrator instance

    Singleton pattern to avoid re-initializing
    """
    global _orchestrator_instance

    if _orchestrator_instance is None:
        _orchestrator_instance = SarahOrchestrator(anthropic_api_key)

    return _orchestrator_instance
