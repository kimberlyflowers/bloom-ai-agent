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

# Import tool registry for agent capabilities
from src.capabilities.registry import (
    get_video_creation_tools,
    get_research_agent_tools,
    get_content_agent_tools,
    execute_tool
)

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
                "heygenai", "comfyui video", "capcut",
                # IMAGE GENERATION (uses same video agent tools)
                "generate image", "create image", "make image", "generate picture",
                "create picture", "ai image", "generate character", "create character",
                "photo of", "picture of", "image of", "ai art", "generate art"
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
        1. Detect if task is complex (needs decomposition)
        2. If complex: Decompose into sub-tasks → coordinate multiple agents
        3. If simple specialized: Route to single agent
        4. If trivial: Delegate to chat_server

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

        # Step 1: Check if task is complex (needs multiple agents or decomposition)
        is_complex = await self._detect_complex_task(user_message)

        if is_complex:
            # COMPLEX TASK - Decompose and coordinate multiple agents
            logger.info("🔀 Complex task detected - decomposing...")

            result = await self._handle_complex_task(user_message, context)

            return {
                "type": "multi_agent_result",
                "result": result,
                "agent_type": "ComplexWorkflow",
                "execution_time": time.time() - start_time
            }

        # Step 2: Fast pattern matching for simple specialized tasks
        task_type = self._identify_task_type(user_message)
        logger.info(f"   📊 Task type identified: {task_type}")

        # Step 3: Route based on task type
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
                "agent_type": "VideoCreationAgent",
                "execution_time": time.time() - start_time
            }

        elif task_type == "research":
            result = await self.spawn_research_agent(user_message, context)
            return {
                "type": "agent_result",
                "result": result,
                "agent_type": "ResearchAgent",
                "execution_time": time.time() - start_time
            }

        elif task_type == "content":
            result = await self.spawn_content_agent(user_message, context)
            return {
                "type": "agent_result",
                "result": result,
                "agent_type": "ContentPostingAgent",
                "execution_time": time.time() - start_time
            }

        elif task_type == "design":
            result = await self.spawn_design_agent(user_message, context)
            return {
                "type": "agent_result",
                "result": result,
                "agent_type": "DesignAgent",
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

    async def _detect_complex_task(self, message: str) -> bool:
        """
        Detect if task requires decomposition and multiple agents

        Complex task indicators:
        - Multiple action types (AND/THEN/ALSO)
        - Quantities > 1 ("create 10 videos", "post to 5 platforms")
        - Multi-step workflows ("research then create then post")
        - Coordination words ("coordinate", "manage", "orchestrate")

        Uses fast heuristics + LLM confirmation for edge cases
        """
        message_lower = message.lower()

        # FAST HEURISTICS (no LLM needed)

        # Check for explicit quantities > 1
        import re
        quantity_patterns = [
            r'(\d+)\s+(videos?|posts?|designs?|articles?|campaigns?)',
            r'(ten|twenty|thirty|forty|fifty|\d+)\s+(videos?|posts?)',
            r'multiple\s+(videos?|posts?|designs?)',
            r'several\s+(videos?|posts?|designs?)',
            r'a bunch of\s+(videos?|posts?)'
        ]

        for pattern in quantity_patterns:
            match = re.search(pattern, message_lower)
            if match:
                logger.info(f"🔢 Complex task: Quantity detected ({match.group(0)})")
                return True

        # Check for multi-step indicators
        multi_step_words = [
            ' and then ', ' then ', ' after that', ' next ',
            ' and also ', ' also ', ' as well as ',
            ' followed by ', ' and finally '
        ]

        if any(word in message_lower for word in multi_step_words):
            logger.info(f"🔀 Complex task: Multi-step workflow detected")
            return True

        # Check for multiple different task types mentioned
        task_types_mentioned = []
        for task_type in self.patterns.keys():
            if self._identify_task_type(message) == task_type:
                task_types_mentioned.append(task_type)

        # Check if message contains keywords from MULTIPLE task types
        types_found = set()
        for task_type, keywords in self.patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                types_found.add(task_type)

        if len(types_found) > 1:
            logger.info(f"🎭 Complex task: Multiple task types ({types_found})")
            return True

        # Check for coordination/workflow words
        workflow_words = [
            'coordinate', 'manage', 'organize', 'schedule',
            'campaign', 'workflow', 'process', 'pipeline',
            'end to end', 'full cycle', 'complete process'
        ]

        if any(word in message_lower for word in workflow_words):
            logger.info(f"📋 Complex task: Workflow coordination detected")
            return True

        # Not complex
        return False

    async def _handle_complex_task(self, message: str, context: Optional[Dict] = None) -> str:
        """
        Handle complex tasks requiring decomposition and coordination

        Process:
        1. Use LLM to decompose task into sub-tasks
        2. Identify which agents needed for each sub-task
        3. Determine execution order (sequential vs parallel)
        4. Spawn agents dynamically
        5. Coordinate execution
        6. Synthesize results

        This is the CORE of multi-agent orchestration
        """
        logger.info("🧠 Decomposing complex task using LLM...")

        # Step 1: Decompose task into structured plan
        plan = await self._decompose_task(message, context)

        if not plan or not plan.get('sub_tasks'):
            logger.warning("⚠️ Task decomposition failed - falling back to single agent")
            # Fallback to simple routing
            task_type = self._identify_task_type(message)
            if task_type == "video":
                return await self.spawn_video_agent(message, context)
            elif task_type == "research":
                return await self.spawn_research_agent(message, context)
            elif task_type == "content":
                return await self.spawn_content_agent(message, context)
            elif task_type == "design":
                return await self.spawn_design_agent(message, context)
            else:
                return "I'll work on that for you!"

        logger.info(f"📋 Task decomposed into {len(plan['sub_tasks'])} sub-tasks")

        # Step 2: Execute sub-tasks (respecting dependencies)
        results = await self._execute_task_plan(plan, context)

        # Step 3: Synthesize results into coherent response
        final_result = await self._synthesize_results(message, plan, results)

        return final_result

    async def _decompose_task(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Use LLM to decompose complex task into structured plan

        Returns plan with:
        - sub_tasks: List of sub-tasks to execute
        - dependencies: Which tasks depend on others
        - parallel_groups: Which tasks can run in parallel
        - agent_types: Which agent type for each sub-task
        """
        decomposition_prompt = f"""Decompose this complex task into a structured execution plan.

Task: "{message}"

Available agent types:
- video: Create UGC videos (ComfyUI, HeyGen, CapCut, ElevenLabs)
- research: Conduct research and analysis
- content: Social media content creation and posting
- design: Visual design using Canva

Return JSON only:
{{
  "sub_tasks": [
    {{
      "id": "task_1",
      "description": "What to do",
      "agent_type": "video|research|content|design",
      "dependencies": ["task_id that must complete first"],
      "parallel_group": 1
    }}
  ],
  "execution_strategy": "sequential|parallel|mixed",
  "reasoning": "Why this decomposition"
}}

Rules:
- If task says "create 10 videos", create 10 separate video sub-tasks
- If task has "research then create", research must complete before create
- Tasks with no dependencies can run in same parallel_group
- Be specific about what each sub-task should accomplish

Return ONLY valid JSON, no explanation."""

        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-3-5-haiku-20241022",  # Fast model for planning
                max_tokens=2000,
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": decomposition_prompt
                }]
            )

            # Parse JSON response
            import json
            plan_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if plan_text.startswith('```'):
                plan_text = plan_text.split('```')[1]
                if plan_text.startswith('json'):
                    plan_text = plan_text[4:]
                plan_text = plan_text.strip()

            plan = json.loads(plan_text)

            logger.info(f"✅ Task decomposed: {plan.get('reasoning', 'No reasoning')}")
            logger.info(f"   📊 Sub-tasks: {len(plan.get('sub_tasks', []))}")
            logger.info(f"   🔀 Strategy: {plan.get('execution_strategy', 'unknown')}")

            return plan

        except Exception as e:
            logger.error(f"❌ Task decomposition failed: {e}")
            return None

    async def _execute_task_plan(self, plan: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute task plan respecting dependencies and parallelization

        Process:
        1. Group tasks by parallel_group
        2. Execute each group (all tasks in group run in parallel)
        3. Wait for group completion before next group
        4. Pass results between dependent tasks
        """
        sub_tasks = plan.get('sub_tasks', [])
        results = {}

        # Group tasks by parallel_group
        from collections import defaultdict
        groups = defaultdict(list)

        for task in sub_tasks:
            group_id = task.get('parallel_group', 0)
            groups[group_id].append(task)

        logger.info(f"🎯 Executing {len(sub_tasks)} sub-tasks across {len(groups)} parallel groups")

        # Execute groups in order
        for group_id in sorted(groups.keys()):
            group_tasks = groups[group_id]
            logger.info(f"🔄 Executing parallel group {group_id} ({len(group_tasks)} tasks)...")

            # Build coroutines for this group
            coroutines = []
            task_ids = []

            for task in group_tasks:
                task_id = task['id']
                description = task['description']
                agent_type = task['agent_type']

                # Build context including dependency results
                task_context = dict(context) if context else {}
                dependencies = task.get('dependencies', [])

                if dependencies:
                    task_context['dependency_results'] = {
                        dep_id: results.get(dep_id, 'N/A')
                        for dep_id in dependencies
                    }

                # Spawn appropriate agent
                if agent_type == "video":
                    coroutines.append(self.spawn_video_agent(description, task_context))
                elif agent_type == "research":
                    coroutines.append(self.spawn_research_agent(description, task_context))
                elif agent_type == "content":
                    coroutines.append(self.spawn_content_agent(description, task_context))
                elif agent_type == "design":
                    coroutines.append(self.spawn_design_agent(description, task_context))
                else:
                    logger.warning(f"⚠️ Unknown agent type: {agent_type}")
                    coroutines.append(self._dummy_agent(description))

                task_ids.append(task_id)

            # Execute all tasks in this group IN PARALLEL
            group_results = await asyncio.gather(*coroutines, return_exceptions=True)

            # Store results
            for i, task_id in enumerate(task_ids):
                result = group_results[i]
                if isinstance(result, Exception):
                    logger.error(f"❌ Task {task_id} failed: {result}")
                    results[task_id] = f"Error: {str(result)}"
                else:
                    results[task_id] = result
                    logger.info(f"✅ Task {task_id} completed")

        logger.info(f"🎉 All {len(sub_tasks)} sub-tasks completed!")

        return results

    async def _synthesize_results(
        self,
        original_request: str,
        plan: Dict[str, Any],
        results: Dict[str, Any]
    ) -> str:
        """
        Synthesize multiple agent results into coherent final response

        Uses LLM to:
        - Combine all sub-task results
        - Create cohesive narrative
        - Highlight key accomplishments
        - Present actionable next steps
        """
        logger.info("🔮 Synthesizing results from all agents...")

        # Build results summary
        results_summary = []
        for task in plan.get('sub_tasks', []):
            task_id = task['id']
            task_desc = task['description']
            task_result = results.get(task_id, 'No result')

            results_summary.append(f"**{task_desc}**\n{task_result}\n")

        synthesis_prompt = f"""Synthesize these multi-agent results into a cohesive response.

Original request: "{original_request}"

Sub-task results:
{chr(10).join(results_summary)}

Create a professional, cohesive summary that:
1. Confirms all tasks completed
2. Highlights key accomplishments
3. Presents results in logical order
4. Includes actionable next steps if relevant
5. Maintains Sarah's friendly, enthusiastic tone

Be concise but complete. Use emojis naturally: ✨ 🎯 💡 🚀"""

        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-3-5-haiku-20241022",  # Fast model for synthesis
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": synthesis_prompt
                }]
            )

            synthesis = response.content[0].text if response.content else "Tasks completed!"

            logger.info("✅ Results synthesized")

            return synthesis

        except Exception as e:
            logger.error(f"❌ Result synthesis failed: {e}")
            # Fallback to simple concatenation
            return "\n\n".join(results_summary)

    async def _dummy_agent(self, request: str) -> str:
        """Fallback dummy agent for unknown types"""
        return f"Task noted: {request}"

    async def _execute_agent_with_tools(
        self,
        model: str,
        system_prompt: str,
        initial_message: str,
        tools: List[Dict[str, Any]],
        max_tokens: int = 8000,
        agent_name: str = "Agent"
    ) -> str:
        """
        Execute agent conversation with tool use support

        Handles the full tool use loop:
        1. Send message to agent
        2. If agent uses tools, execute them
        3. Send tool results back to agent
        4. Repeat until agent returns final text response

        Args:
            model: Claude model to use
            system_prompt: System prompt for the agent
            initial_message: Initial user message
            tools: List of tool definitions
            max_tokens: Max tokens for responses
            agent_name: Agent name for logging

        Returns:
            Final text response from agent
        """
        try:
            messages = [{
                "role": "user",
                "content": initial_message
            }]

            # Tool use loop - keep going until agent stops using tools
            iteration = 0
            max_iterations = 20  # Prevent infinite loops

            while iteration < max_iterations:
                iteration += 1

                # Call Claude API
                response = await asyncio.to_thread(
                    self.client.messages.create,
                    model=model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    tools=tools,
                    messages=messages
                )

                logger.info(f"   🔄 {agent_name} iteration {iteration} - {response.usage.input_tokens} in, {response.usage.output_tokens} out")

                # Check stop reason
                if response.stop_reason == "end_turn":
                    # Agent finished - extract final text
                    final_text = ""
                    for block in response.content:
                        if block.type == "text":
                            final_text += block.text

                    logger.info(f"✅ {agent_name} completed after {iteration} iterations")
                    return final_text if final_text else "Task completed successfully"

                elif response.stop_reason == "tool_use":
                    # Agent wants to use tools - execute them
                    logger.info(f"   🔧 {agent_name} using tools...")

                    # Add assistant message to conversation
                    messages.append({
                        "role": "assistant",
                        "content": response.content
                    })

                    # Execute each tool call
                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            tool_name = block.name
                            tool_input = block.input
                            tool_use_id = block.id

                            logger.info(f"      🛠️  Executing: {tool_name}")

                            # Execute tool
                            try:
                                result = await execute_tool(tool_name, tool_input)
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": tool_use_id,
                                    "content": str(result)
                                })
                                logger.info(f"      ✅ {tool_name} succeeded")
                            except Exception as e:
                                logger.error(f"      ❌ {tool_name} failed: {e}")
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": tool_use_id,
                                    "content": f"Error: {str(e)}",
                                    "is_error": True
                                })

                    # Add tool results to conversation
                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })

                    # Continue loop to get agent's next response

                else:
                    # Unexpected stop reason
                    logger.warning(f"⚠️ Unexpected stop reason: {response.stop_reason}")
                    return f"Agent stopped unexpectedly: {response.stop_reason}"

            # Max iterations reached
            logger.warning(f"⚠️ {agent_name} reached max iterations ({max_iterations})")
            return f"Task incomplete - reached maximum iterations"

        except Exception as e:
            logger.error(f"❌ {agent_name} execution failed: {e}")
            return f"Error: {str(e)}"

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

**Your Capabilities:**
You have access to powerful tools for complete video production:

PERSONA TOOLS:
- persona_database_query: Get persona data, reference images, voice ID
- load_persona_assets: Load all persona assets at once

SCRIPTWRITING TOOLS:
- write_video_script: Generate complete UGC-style scripts
- create_hook: Create attention-grabbing hooks (first 3 seconds)

AVATAR GENERATION TOOLS:
- nanobanna_generate_character_image: Generate photo-realistic character images
- nanobanna_batch_generate_poses: Generate 3 poses for 45-second videos
- elevenlabs_generate_voice: Text-to-speech with natural voices
- seaweed_image_to_video: Convert image + audio to talking head video

VIDEO EDITING TOOLS:
- moviepy_composite_video: Combine clips into complete video
- whisper_generate_captions: Auto-generate captions from audio
- moviepy_add_hardcoded_captions: Burn captions into video
- ffmpeg_optimize_for_tiktok: Optimize for TikTok (1080x1920)
- ffmpeg_add_background_music: Add background music

PUBLISHING TOOLS:
- tiktok_api_upload_video: Upload to TikTok
- tiktok_generate_ugc_caption: Generate TikTok captions with hashtags
- update_persona_content_library: Track created videos

**Your Process:**
1. Load persona assets (reference images, voice ID)
2. Write engaging UGC script
3. Generate voice audio from script
4. Generate character image(s) using persona reference images
5. Create talking video from image + audio
6. Add captions and optimize for platform
7. Upload to platform
8. Update content library

**Guidelines:**
- Work autonomously - use tools to actually create content
- Be creative but stay on-brand
- Optimize for target platform
- Include captions for accessibility
- Track all created content

**Output Format:**
Return a summary with:
- Video URL/path
- Duration and platform
- Tools used
- Performance predictions
- Posting recommendations

Use tools proactively. You have full authority to create content."""

        # Get video creation tools
        tools = get_video_creation_tools()

        # Execute agent with tools
        message = f"{request}\n\nContext: {context if context else 'No additional context'}"

        result = await self._execute_agent_with_tools(
            model="claude-sonnet-4-5-20250929",
            system_prompt=system_prompt,
            initial_message=message,
            tools=tools,
            max_tokens=8000,
            agent_name="VideoCreationAgent"
        )

        return result

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

**Your Capabilities:**
You have access to powerful research tools:

RESEARCH TOOLS:
- trending_topics_research: Research trending topics in any niche
  * Analyzes what's gaining traction on TikTok/YouTube/Instagram
  * Returns trend scores, volume estimates, content angles
  * Identifies emerging opportunities

- competitor_analysis: Analyze top-performing competitor content
  * Studies content themes, posting frequency, formats
  * Identifies engagement patterns and winning strategies
  * Finds content gaps and opportunities

- generate_video_ideas: Generate 10+ viral video ideas
  * Creates ideas based on trends and topics
  * Includes hooks, hashtags, performance estimates
  * Tailored for specific platforms

**Your Process:**
1. Use research tools to gather data
2. Analyze findings objectively
3. Identify patterns and opportunities
4. Synthesize actionable insights
5. Generate specific recommendations

**Guidelines:**
- Use tools to conduct actual research
- Focus on recent trends (2024-2025)
- Provide data-driven insights
- Identify both opportunities and risks
- Generate actionable recommendations

**Output Format:**
Provide:
- Executive summary (2-3 sentences)
- Key findings from research tools
- Data and examples
- Specific recommendations
- Generated video ideas (when relevant)

Work autonomously using tools."""

        # Get research tools
        tools = get_research_agent_tools()

        # Execute agent with tools
        message = f"{request}\n\nContext: {context if context else 'No additional context'}"

        result = await self._execute_agent_with_tools(
            model="claude-3-5-haiku-20241022",  # Cheaper model for research
            system_prompt=system_prompt,
            initial_message=message,
            tools=tools,
            max_tokens=4000,
            agent_name="ResearchAgent"
        )

        return result

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

        system_prompt = """You are ContentPostingAgent - Sarah's social media publishing specialist.

**Your Mission:** Publish and manage content across social platforms.

**Your Capabilities:**
You have access to powerful publishing tools:

PUBLISHING TOOLS:
- tiktok_api_upload_video: Upload videos to TikTok
  * Handles video file upload
  * Accepts caption and privacy settings
  * Returns video URL and post ID

- instagram_api_upload_reel: Upload Reels to Instagram
  * Publishes vertical videos
  * Adds captions and hashtags
  * Returns post URL and media ID

**Your Process:**
1. Understand what needs to be published
2. Use appropriate publishing tool for platform
3. Include optimized captions with hashtags
4. Verify successful upload
5. Return post URLs and metadata

**Guidelines:**
- Use tools to actually publish content
- Ensure videos meet platform requirements
- Optimize captions for each platform
- Include relevant hashtags
- Track all published content

**Output Format:**
Provide:
- Published video URLs
- Platform and post IDs
- Caption used
- Engagement predictions
- Next steps

Work autonomously using tools to publish content."""

        # Get content agent tools
        tools = get_content_agent_tools()

        # Execute agent with tools
        message = f"{request}\n\nContext: {context if context else 'No additional context'}"

        result = await self._execute_agent_with_tools(
            model="claude-sonnet-4-5-20250929",
            system_prompt=system_prompt,
            initial_message=message,
            tools=tools,
            max_tokens=4000,
            agent_name="ContentPostingAgent"
        )

        return result

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
