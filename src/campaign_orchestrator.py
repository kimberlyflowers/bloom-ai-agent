"""
Multi-Agent Campaign Orchestrator - Complex coordinated campaigns

Enables teams of specialized agents to execute sophisticated multi-platform
marketing campaigns with dependencies, sequencing, and real-time adaptation.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class CampaignPhase(Enum):
    """Phases of a marketing campaign"""
    AWARENESS = "awareness"  # Make people aware (reach, impressions)
    EDUCATION = "education"  # Educate them (value, use cases)
    CONSIDERATION = "consideration"  # Get them considering (comparisons, demos)
    CONVERSION = "conversion"  # Convert them (trials, purchases)
    RETENTION = "retention"  # Keep them engaged (support, updates)


class AgentRole(Enum):
    """Roles agents can play in campaigns"""
    CONTENT_CREATOR = "content_creator"  # Creates content
    DISTRIBUTOR = "distributor"  # Distributes content
    ENGAGER = "engager"  # Engages with audience
    CONVERTER = "converter"  # Drives conversions
    SUPPORTER = "supporter"  # Provides support


@dataclass
class CampaignTask:
    """Single task within campaign"""
    task_id: str
    phase: CampaignPhase
    role: AgentRole
    platform: str
    description: str
    assigned_agent: Optional[str] = None

    # Timing
    start_after: Optional[str] = None  # task_id to wait for
    duration_hours: int = 24

    # Resources
    budget: float = 0.0
    target_actions: int = 0

    # Status
    status: str = "pending"  # pending, in_progress, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Results
    actual_actions: int = 0
    conversions: int = 0
    roi: float = 0.0


@dataclass
class CampaignStrategy:
    """Complete multi-phase campaign strategy"""
    campaign_id: str
    goal: str
    total_budget: float
    start_date: datetime
    duration_days: int

    # Tasks by phase
    tasks: List[CampaignTask] = field(default_factory=list)

    # Team assignment
    agent_assignments: Dict[str, List[str]] = field(default_factory=dict)  # agent_id -> [task_ids]

    # Performance tracking
    phase_performance: Dict[CampaignPhase, dict] = field(default_factory=dict)
    overall_roi: float = 0.0


class CampaignOrchestrator:
    """Orchestrates complex multi-agent campaigns"""

    def __init__(self):
        self.active_campaigns: Dict[str, CampaignStrategy] = {}
        self.task_dependencies: Dict[str, List[str]] = {}  # task_id -> [dependent_task_ids]

    def create_product_launch_campaign(
        self,
        campaign_id: str,
        product_name: str,
        budget: float,
        colony
    ) -> CampaignStrategy:
        """
        Create a pre-built product launch campaign.

        Phases:
        1. Awareness (Days 1-3): Announce product, create buzz
        2. Education (Days 4-7): Explain features, benefits
        3. Consideration (Days 8-12): Share comparisons, case studies
        4. Conversion (Days 13-21): Drive signups/purchases
        5. Retention (Days 22-30): Onboard, support, engage
        """
        campaign = CampaignStrategy(
            campaign_id=campaign_id,
            goal=f"Launch {product_name}",
            total_budget=budget,
            start_date=datetime.now(),
            duration_days=30
        )

        # Phase 1: Awareness (Days 1-3)
        awareness_tasks = [
            CampaignTask(
                task_id=f"{campaign_id}_awareness_twitter",
                phase=CampaignPhase.AWARENESS,
                role=AgentRole.CONTENT_CREATOR,
                platform="twitter",
                description=f"Create announcement thread for {product_name}",
                budget=budget * 0.05,
                target_actions=10,
                duration_hours=72
            ),
            CampaignTask(
                task_id=f"{campaign_id}_awareness_discord",
                phase=CampaignPhase.AWARENESS,
                role=AgentRole.DISTRIBUTOR,
                platform="discord",
                description=f"Share {product_name} launch in relevant communities",
                budget=budget * 0.05,
                target_actions=20,
                duration_hours=72
            )
        ]

        # Phase 2: Education (Days 4-7)
        education_tasks = [
            CampaignTask(
                task_id=f"{campaign_id}_education_content",
                phase=CampaignPhase.EDUCATION,
                role=AgentRole.CONTENT_CREATOR,
                platform="blog",
                description=f"Create educational guide for {product_name}",
                start_after=f"{campaign_id}_awareness_twitter",  # Wait for awareness
                budget=budget * 0.10,
                target_actions=5,
                duration_hours=96
            ),
            CampaignTask(
                task_id=f"{campaign_id}_education_distribution",
                phase=CampaignPhase.EDUCATION,
                role=AgentRole.DISTRIBUTOR,
                platform="reddit",
                description=f"Share educational content about {product_name}",
                start_after=f"{campaign_id}_education_content",
                budget=budget * 0.10,
                target_actions=15,
                duration_hours=96
            )
        ]

        # Phase 3: Consideration (Days 8-12)
        consideration_tasks = [
            CampaignTask(
                task_id=f"{campaign_id}_consideration_comparison",
                phase=CampaignPhase.CONSIDERATION,
                role=AgentRole.CONTENT_CREATOR,
                platform="blog",
                description=f"Create comparison guide: {product_name} vs alternatives",
                start_after=f"{campaign_id}_education_distribution",
                budget=budget * 0.10,
                target_actions=3,
                duration_hours=120
            ),
            CampaignTask(
                task_id=f"{campaign_id}_consideration_engagement",
                phase=CampaignPhase.CONSIDERATION,
                role=AgentRole.ENGAGER,
                platform="discord",
                description=f"Engage with interested users about {product_name}",
                start_after=f"{campaign_id}_consideration_comparison",
                budget=budget * 0.15,
                target_actions=50,
                duration_hours=120
            )
        ]

        # Phase 4: Conversion (Days 13-21)
        conversion_tasks = [
            CampaignTask(
                task_id=f"{campaign_id}_conversion_outreach",
                phase=CampaignPhase.CONVERSION,
                role=AgentRole.CONVERTER,
                platform="email",
                description=f"Targeted outreach to interested users",
                start_after=f"{campaign_id}_consideration_engagement",
                budget=budget * 0.30,
                target_actions=100,
                duration_hours=216
            ),
            CampaignTask(
                task_id=f"{campaign_id}_conversion_support",
                phase=CampaignPhase.CONVERSION,
                role=AgentRole.SUPPORTER,
                platform="discord",
                description=f"Answer questions, help with trials",
                start_after=f"{campaign_id}_conversion_outreach",
                budget=budget * 0.10,
                target_actions=50,
                duration_hours=216
            )
        ]

        # Phase 5: Retention (Days 22-30)
        retention_tasks = [
            CampaignTask(
                task_id=f"{campaign_id}_retention_onboarding",
                phase=CampaignPhase.RETENTION,
                role=AgentRole.SUPPORTER,
                platform="email",
                description=f"Onboard new {product_name} users",
                start_after=f"{campaign_id}_conversion_support",
                budget=budget * 0.05,
                target_actions=30,
                duration_hours=216
            )
        ]

        # Add all tasks
        campaign.tasks.extend(awareness_tasks)
        campaign.tasks.extend(education_tasks)
        campaign.tasks.extend(consideration_tasks)
        campaign.tasks.extend(conversion_tasks)
        campaign.tasks.extend(retention_tasks)

        # Build dependency graph
        for task in campaign.tasks:
            if task.start_after:
                if task.start_after not in self.task_dependencies:
                    self.task_dependencies[task.start_after] = []
                self.task_dependencies[task.start_after].append(task.task_id)

        # Assign agents based on specialization
        self._assign_agents_to_tasks(campaign, colony)

        # Store campaign
        self.active_campaigns[campaign_id] = campaign

        logger.info(f"Created product launch campaign: {campaign_id} with {len(campaign.tasks)} tasks")
        return campaign

    def _assign_agents_to_tasks(self, campaign: CampaignStrategy, colony):
        """Assign best agents to tasks based on specialization and role"""
        for task in campaign.tasks:
            # Find best agent for this task
            best_agent = None
            best_score = 0.0

            for agent_id, agent in colony.agents.items():
                # Score based on specialization match
                score = 0.0

                # Platform match
                specialization_str = str(agent.specialization).lower()
                if task.platform in specialization_str:
                    score += 10.0

                # Role match (content creation = generalist or specialist)
                if task.role == AgentRole.CONTENT_CREATOR:
                    score += 5.0
                elif task.role == AgentRole.CONVERTER:
                    # Prefer agents with high conversion rates
                    if hasattr(agent, 'total_conversions') and agent.total_conversions > 10:
                        score += 8.0

                # Performance history
                if hasattr(agent, 'total_revenue') and agent.total_revenue > 50:
                    score += 3.0

                if score > best_score:
                    best_score = score
                    best_agent = agent_id

            if best_agent:
                task.assigned_agent = best_agent
                if best_agent not in campaign.agent_assignments:
                    campaign.agent_assignments[best_agent] = []
                campaign.agent_assignments[best_agent].append(task.task_id)

        logger.info(f"Assigned {len(campaign.agent_assignments)} agents to {len(campaign.tasks)} tasks")

    def get_ready_tasks(self, campaign_id: str) -> List[CampaignTask]:
        """Get tasks that are ready to start (dependencies met)"""
        campaign = self.active_campaigns[campaign_id]
        ready_tasks = []

        for task in campaign.tasks:
            # Skip if already started
            if task.status != "pending":
                continue

            # Check if dependency met
            if task.start_after:
                # Find dependency task
                dep_task = next((t for t in campaign.tasks if t.task_id == task.start_after), None)
                if not dep_task or dep_task.status != "completed":
                    continue  # Dependency not met

            ready_tasks.append(task)

        return ready_tasks

    def start_task(self, campaign_id: str, task_id: str):
        """Start a task"""
        campaign = self.active_campaigns[campaign_id]
        task = next((t for t in campaign.tasks if t.task_id == task_id), None)

        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = "in_progress"
        task.started_at = datetime.now()

        logger.info(f"Started task {task_id}: {task.description}")

    def complete_task(self, campaign_id: str, task_id: str,
                     actions: int, conversions: int, cost: float):
        """Complete a task with results"""
        campaign = self.active_campaigns[campaign_id]
        task = next((t for t in campaign.tasks if t.task_id == task_id), None)

        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = "completed"
        task.completed_at = datetime.now()
        task.actual_actions = actions
        task.conversions = conversions
        task.roi = (conversions * 50.0) / cost if cost > 0 else 0.0  # Assume $50 LTV

        # Update phase performance
        if task.phase not in campaign.phase_performance:
            campaign.phase_performance[task.phase] = {
                'total_actions': 0,
                'total_conversions': 0,
                'total_cost': 0.0,
                'roi': 0.0
            }

        phase_perf = campaign.phase_performance[task.phase]
        phase_perf['total_actions'] += actions
        phase_perf['total_conversions'] += conversions
        phase_perf['total_cost'] += cost
        revenue = conversions * 50.0
        phase_perf['roi'] = revenue / phase_perf['total_cost'] if phase_perf['total_cost'] > 0 else 0.0

        logger.info(f"Completed task {task_id}: {actions} actions, {conversions} conversions, {task.roi:.2f}x ROI")

        # Trigger dependent tasks
        if task_id in self.task_dependencies:
            for dependent_task_id in self.task_dependencies[task_id]:
                logger.info(f"Task {dependent_task_id} is now ready (dependency {task_id} completed)")

    def get_campaign_status(self, campaign_id: str) -> Dict:
        """Get current campaign status"""
        campaign = self.active_campaigns[campaign_id]

        total_tasks = len(campaign.tasks)
        completed_tasks = len([t for t in campaign.tasks if t.status == "completed"])
        in_progress_tasks = len([t for t in campaign.tasks if t.status == "in_progress"])

        total_conversions = sum(t.conversions for t in campaign.tasks if t.status == "completed")
        total_cost = sum(t.budget for t in campaign.tasks if t.status == "completed")

        return {
            'campaign_id': campaign_id,
            'goal': campaign.goal,
            'progress': f"{completed_tasks}/{total_tasks} tasks completed",
            'in_progress': in_progress_tasks,
            'total_conversions': total_conversions,
            'total_cost': total_cost,
            'current_roi': (total_conversions * 50.0) / total_cost if total_cost > 0 else 0.0,
            'phase_performance': campaign.phase_performance,
            'next_tasks': [t.description for t in self.get_ready_tasks(campaign_id)[:3]]
        }


if __name__ == "__main__":
    # Demo
    print("=" * 80)
    print("MULTI-AGENT CAMPAIGN ORCHESTRATOR - DEMO".center(80))
    print("=" * 80)

    from src.agent_reproduction import AgentColony
    from src.ai_agent import BloomAIAgent, Specialization

    # Create colony
    colony = AgentColony()
    colony.agents['discord_expert'] = BloomAIAgent('discord_expert', 100.0, Specialization.COMMUNITY_ENGAGER)
    colony.agents['twitter_expert'] = BloomAIAgent('twitter_expert', 100.0, Specialization.TWITTER_SPECIALIST)
    colony.agents['generalist'] = BloomAIAgent('generalist', 100.0, Specialization.GENERALIST)

    # Create campaign
    orchestrator = CampaignOrchestrator()
    campaign = orchestrator.create_product_launch_campaign(
        'bloom_v2_launch',
        'BLOOM v2.0',
        1000.0,
        colony
    )

    print(f"\n1. CAMPAIGN CREATED: {campaign.goal}")
    print("-" * 80)
    print(f"Total Budget: ${campaign.total_budget}")
    print(f"Duration: {campaign.duration_days} days")
    print(f"Total Tasks: {len(campaign.tasks)}")
    print(f"Agents Assigned: {len(campaign.agent_assignments)}")

    # Show tasks by phase
    print("\n2. CAMPAIGN PHASES & TASKS")
    print("-" * 80)

    for phase in CampaignPhase:
        phase_tasks = [t for t in campaign.tasks if t.phase == phase]
        if not phase_tasks:
            continue

        print(f"\n{phase.value.upper()} ({len(phase_tasks)} tasks):")
        for task in phase_tasks:
            print(f"  • {task.description}")
            print(f"    Platform: {task.platform}, Budget: ${task.budget:.0f}")
            print(f"    Assigned: {task.assigned_agent}")
            if task.start_after:
                print(f"    Waits for: {task.start_after}")

    # Simulate execution
    print("\n3. CAMPAIGN EXECUTION SIMULATION")
    print("-" * 80)

    import time

    for i in range(5):  # Simulate first 5 tasks
        ready_tasks = orchestrator.get_ready_tasks('bloom_v2_launch')

        if not ready_tasks:
            break

        task = ready_tasks[0]
        print(f"\nStarting: {task.description}")
        orchestrator.start_task('bloom_v2_launch', task.task_id)

        # Simulate work
        import random
        actions = random.randint(task.target_actions - 5, task.target_actions + 10)
        conversions = int(actions * random.uniform(0.05, 0.15))
        cost = task.budget * random.uniform(0.8, 1.0)

        orchestrator.complete_task('bloom_v2_launch', task.task_id, actions, conversions, cost)
        print(f"Completed: {actions} actions, {conversions} conversions, ROI: {task.roi:.2f}x")

    # Show status
    print("\n4. CAMPAIGN STATUS")
    print("-" * 80)

    status = orchestrator.get_campaign_status('bloom_v2_launch')
    print(f"\nGoal: {status['goal']}")
    print(f"Progress: {status['progress']}")
    print(f"In Progress: {status['in_progress']} tasks")
    print(f"Total Conversions: {status['total_conversions']}")
    print(f"Total Spent: ${status['total_cost']:.2f}")
    print(f"Current ROI: {status['current_roi']:.2f}x")

    print(f"\nPhase Performance:")
    for phase, perf in status['phase_performance'].items():
        print(f"  {phase.value.upper()}:")
        print(f"    Actions: {perf['total_actions']}")
        print(f"    Conversions: {perf['total_conversions']}")
        print(f"    ROI: {perf['roi']:.2f}x")

    print(f"\nNext Tasks:")
    for task_desc in status['next_tasks']:
        print(f"  • {task_desc}")

    print("\n" + "=" * 80)
    print("🎯 MULTI-PHASE CAMPAIGNS READY!".center(80))
    print("=" * 80)
