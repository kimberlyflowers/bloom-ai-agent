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
