"""
Dynamic Agent Spawning System

Sarah spawns specialized agents on-demand based on task complexity.
Each agent gets ONLY the capabilities it needs for its specific task.

Architecture:
- DynamicAgent: A worker that can execute any set of capabilities
- AgentSpawner: Analyzes tasks and spawns the right agents
- TaskAnalyzer: Determines which capabilities are needed for a task

Example:
    User: "Create a TikTok video about skincare"

    Sarah analyzes → needs:
        - Script writing capabilities
        - Character generation capabilities
        - Video editing capabilities
        - Publishing capabilities

    Sarah spawns:
        - Script Agent (write_video_script, create_hook)
        - Avatar Agent (nanobanna, elevenlabs, seaweed)
        - Video Editing Agent (moviepy, ffmpeg)
        - Publishing Agent (tiktok_api_upload)

    Dashboard shows all 4 agents working in real-time!
"""

import uuid
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime

from src.capability_agent_mapping import (
    get_agent_type_for_capability,
    get_capabilities_for_agent_type,
    get_agent_metadata
)

logger = logging.getLogger(__name__)


class DynamicAgent:
    """
    A specialized agent that can execute any set of capabilities.

    Unlike fixed agent types, this agent is created on-demand with exactly
    the capabilities needed for its task.
    """

    def __init__(self, agent_id: str, agent_type: str, capabilities_dict: Dict):
        """
        Initialize dynamic agent

        Args:
            agent_id: Unique ID (e.g., "script_agent_abc123")
            agent_type: Type name (e.g., "script", "video_editing")
            capabilities_dict: Dictionary of capability_name → function
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities_dict

        # Get metadata
        metadata = get_agent_metadata(agent_type)
        self.name = metadata['name']
        self.icon = metadata['icon']
        self.description = metadata['description']

        # Task state
        self.status = "idle"  # idle, working, completed, failed
        self.current_task = None
        self.current_task_description = None
        self.progress = 0
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None

        logger.info(f"🤖 Spawned {self.icon} {self.name} (ID: {self.agent_id})")
        logger.info(f"   Capabilities: {list(self.capabilities.keys())}")

    async def execute_task(self, task_description: str, context: dict = None) -> dict:
        """
        Execute a task using this agent's capabilities

        Args:
            task_description: What to do (e.g., "Write a 30-second TikTok script")
            context: Additional context (product info, platform, etc.)

        Returns:
            Dictionary with results
        """
        self.status = "working"
        self.current_task_description = task_description
        self.started_at = datetime.now()
        self.progress = 0

        logger.info(f"{self.icon} {self.name} starting: {task_description}")

        try:
            # In a real implementation, this would:
            # 1. Call Claude with the task and available capabilities
            # 2. Claude decides which capabilities to use
            # 3. Execute capability functions based on Claude's decisions
            # 4. Return results

            # For now, simulate work
            results = await self._simulate_work(task_description, context)

            self.status = "completed"
            self.progress = 100
            self.completed_at = datetime.now()
            self.result = results

            duration = (self.completed_at - self.started_at).total_seconds()
            logger.info(f"✅ {self.name} completed in {duration:.1f}s")

            return results

        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            self.completed_at = datetime.now()

            logger.error(f"❌ {self.name} failed: {e}")
            raise

    async def _simulate_work(self, task: str, context: dict) -> dict:
        """
        Simulate agent work (replace with real Claude AI execution)

        In production, this would:
        1. Build a system prompt listing available capabilities
        2. Call Claude API with the task
        3. Execute tool calls as Claude requests them
        4. Return final results
        """
        # Simulate progressive work
        steps = 5
        for i in range(steps):
            await asyncio.sleep(0.5)  # Simulate work
            self.progress = int((i + 1) / steps * 100)
            logger.debug(f"{self.name} progress: {self.progress}%")

        return {
            'status': 'success',
            'task': task,
            'agent_type': self.agent_type,
            'capabilities_used': list(self.capabilities.keys()),
            'message': f'{self.name} completed: {task}'
        }

    def to_dict(self) -> dict:
        """
        Serialize agent state for dashboard display

        Returns:
            Dictionary suitable for JSON serialization
        """
        return {
            'id': self.agent_id,
            'agent_name': self.name,
            'agent_type': self.agent_type,
            'icon': self.icon,
            'description': self.current_task_description or self.description,
            'status': self.status,
            'progress': self.progress,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'capabilities': list(self.capabilities.keys())
        }


class TaskAnalyzer:
    """
    Analyzes tasks to determine which capabilities are needed

    In production, this would use an LLM to intelligently analyze tasks.
    For now, it uses keyword matching.
    """

    def __init__(self):
        self.keyword_capability_map = {
            # Video creation keywords
            'video': ['write_video_script', 'nanobanna_generate_character_image',
                     'elevenlabs_generate_voice', 'seaweed_image_to_video',
                     'moviepy_composite_video'],
            'script': ['write_video_script', 'create_hook', 'add_timestamps'],

            # Platform-specific
            'tiktok': ['tiktok_api_upload_video', 'tiktok_generate_ugc_caption',
                      'tiktok_select_trending_hashtags', 'ffmpeg_optimize_for_tiktok'],
            'youtube': ['youtube_api_upload', 'youtube_set_metadata',
                       'ffmpeg_optimize_for_youtube'],
            'instagram': ['instagram_api_upload_reel', 'instagram_set_caption',
                         'ffmpeg_optimize_for_instagram'],

            # Content operations
            'analyze': ['youtube_analytics_fetch', 'tiktok_analytics_fetch',
                       'track_engagement_metrics', 'generate_performance_report'],
            'research': ['trending_topics_research', 'competitor_analysis',
                        'keyword_research', 'generate_video_ideas'],
            'edit': ['moviepy_composite_video', 'ffmpeg_add_transitions',
                    'ffmpeg_add_background_music'],
            'publish': ['youtube_api_upload', 'tiktok_api_upload_video',
                       'instagram_api_upload_reel', 'cross_platform_scheduler'],

            # Character/Avatar
            'character': ['nanobanna_generate_character_image',
                         'nanobanna_batch_generate_poses', 'character_sheet_generation'],
            'voice': ['elevenlabs_clone_voice', 'elevenlabs_generate_voice'],

            # Design
            'thumbnail': ['design_thumbnail', 'generate_ai_image'],
            'design': ['generate_ai_image', 'create_lower_thirds',
                      'create_motion_graphics'],
        }

    def analyze_task(self, task_description: str) -> List[str]:
        """
        Analyze a task and determine which capabilities are needed

        Args:
            task_description: Natural language task description

        Returns:
            List of capability names needed
        """
        task_lower = task_description.lower()
        needed_capabilities = set()

        # Match keywords to capabilities
        for keyword, capabilities in self.keyword_capability_map.items():
            if keyword in task_lower:
                needed_capabilities.update(capabilities)

        # If nothing matched, assume it's a video creation task
        if not needed_capabilities:
            needed_capabilities.update(self.keyword_capability_map['video'])

        logger.info(f"📋 Task analysis: '{task_description}'")
        logger.info(f"   Capabilities needed: {list(needed_capabilities)}")

        return list(needed_capabilities)


class AgentSpawner:
    """
    Spawns specialized agents dynamically based on task needs

    This is Sarah's "hiring manager" - she analyzes what help she needs
    and spawns the right specialists.
    """

    def __init__(self, all_capabilities: Dict = None):
        """
        Initialize agent spawner

        Args:
            all_capabilities: Dictionary of ALL available capabilities
                              {capability_name: function_reference}
                              If None, uses placeholder functions
        """
        self.all_capabilities = all_capabilities or {}
        self.active_agents: Dict[str, DynamicAgent] = {}
        self.task_analyzer = TaskAnalyzer()

        logger.info("🎯 Agent Spawner initialized")
        logger.info(f"   Available capabilities: {len(self.all_capabilities)}")

    def group_capabilities_by_agent_type(self, capability_names: List[str]) -> Dict[str, List[str]]:
        """
        Group capabilities into agent types

        Args:
            capability_names: List of capability names needed

        Returns:
            Dictionary of {agent_type: [capability_names]}
        """
        grouped = {}

        for cap_name in capability_names:
            agent_type = get_agent_type_for_capability(cap_name)

            if agent_type:  # None means Sarah handles it directly
                if agent_type not in grouped:
                    grouped[agent_type] = []
                grouped[agent_type].append(cap_name)

        return grouped

    def spawn_agents_for_task(self, task_description: str) -> List[DynamicAgent]:
        """
        Main method: Spawn all agents needed for a task

        Args:
            task_description: Natural language task description

        Returns:
            List of spawned DynamicAgent objects
        """
        logger.info(f"\n🚀 Spawning agents for task: '{task_description}'")

        # Step 1: Analyze task to determine needed capabilities
        needed_capabilities = self.task_analyzer.analyze_task(task_description)

        # Step 2: Group capabilities by agent type
        grouped = self.group_capabilities_by_agent_type(needed_capabilities)

        logger.info(f"   Will spawn {len(grouped)} agent types")

        # Step 3: Spawn one agent per type
        spawned_agents = []

        for agent_type, cap_names in grouped.items():
            # Build capability dict for this agent
            agent_capabilities = {}
            for cap_name in cap_names:
                if cap_name in self.all_capabilities:
                    agent_capabilities[cap_name] = self.all_capabilities[cap_name]
                else:
                    # Placeholder if capability not implemented
                    agent_capabilities[cap_name] = lambda: None

            # Generate unique ID
            agent_id = f"{agent_type}_{uuid.uuid4().hex[:8]}"

            # Create agent
            agent = DynamicAgent(
                agent_id=agent_id,
                agent_type=agent_type,
                capabilities_dict=agent_capabilities
            )

            # Track active agent
            self.active_agents[agent_id] = agent
            spawned_agents.append(agent)

        logger.info(f"✅ Spawned {len(spawned_agents)} agents")
        return spawned_agents

    def get_active_agents(self) -> List[DynamicAgent]:
        """
        Get all currently active agents

        Returns:
            List of DynamicAgent objects
        """
        return list(self.active_agents.values())

    def get_active_agents_for_dashboard(self) -> List[dict]:
        """
        Get agent data formatted for dashboard display

        Returns:
            List of dictionaries suitable for JSON serialization
        """
        return [agent.to_dict() for agent in self.active_agents.values()]

    def remove_agent(self, agent_id: str):
        """Remove completed/failed agent"""
        if agent_id in self.active_agents:
            agent = self.active_agents[agent_id]
            logger.info(f"🗑️ Removing {agent.name} (status: {agent.status})")
            del self.active_agents[agent_id]

    def cleanup_completed_agents(self):
        """Remove all completed or failed agents"""
        to_remove = [
            agent_id for agent_id, agent in self.active_agents.items()
            if agent.status in ['completed', 'failed']
        ]

        for agent_id in to_remove:
            self.remove_agent(agent_id)

        if to_remove:
            logger.info(f"🧹 Cleaned up {len(to_remove)} completed agents")


# Demo/Test
async def demo():
    """Demonstrate dynamic agent spawning"""
    print("🎬 Dynamic Agent Spawning Demo\n")

    # Initialize spawner
    spawner = AgentSpawner()

    # Test task 1: Create TikTok video
    print("=" * 60)
    task1 = "Create a TikTok video about skincare routine"
    agents1 = spawner.spawn_agents_for_task(task1)

    print(f"\n📊 Spawned {len(agents1)} agents:")
    for agent in agents1:
        print(f"   {agent.icon} {agent.name}")

    # Simulate agents working
    print("\n⚙️ Agents working...")
    tasks = [agent.execute_task(task1) for agent in agents1]
    await asyncio.gather(*tasks)

    print("\n✅ All agents completed!")
    print("\n📋 Dashboard would show:")
    for agent_data in spawner.get_active_agents_for_dashboard():
        print(f"   {agent_data['icon']} {agent_data['agent_name']}: {agent_data['status']} ({agent_data['progress']}%)")

    # Cleanup
    spawner.cleanup_completed_agents()
    print(f"\n🧹 Active agents after cleanup: {len(spawner.get_active_agents())}")


if __name__ == "__main__":
    asyncio.run(demo())
