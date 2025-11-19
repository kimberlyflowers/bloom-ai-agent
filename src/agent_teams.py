"""
Agent Team Collaboration - System #18

Pair backend agents with frontend agents to work as teams!

Backend Agent:
- API calls
- Data processing
- Database operations
- Business logic

Frontend Agent:
- Browser automation
- Visual tasks
- Platform UIs
- Screenshots/proofs

Together: UNSTOPPABLE! 🚀
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json
from pathlib import Path


# ============================================================================
# CONFIGURATION
# ============================================================================

TEAMS_DIR = Path("data/agent_teams")
TEAMS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# AGENT ROLES
# ============================================================================

class AgentType(Enum):
    """Type of agent"""
    BACKEND = "backend"  # API calls, data processing
    FRONTEND = "frontend"  # Browser automation, visual tasks
    HYBRID = "hybrid"  # Can do both!


class TeamRole(Enum):
    """Role in team"""
    LEAD = "lead"  # Coordinates team
    SPECIALIST = "specialist"  # Focused on specific tasks
    SUPPORT = "support"  # Assists other agents


# ============================================================================
# TEAM MEMBER
# ============================================================================

@dataclass
class TeamMember:
    """An agent on a team"""
    agent_id: str
    agent_name: str
    agent_type: AgentType
    team_role: TeamRole

    # Skills
    skills: List[str] = field(default_factory=list)
    specializations: List[str] = field(default_factory=list)

    # Tools access
    tools: List[str] = field(default_factory=list)

    # Performance
    tasks_completed: int = 0
    tasks_assigned: int = 0
    success_rate: float = 100.0

    active: bool = True


# ============================================================================
# AGENT TEAM
# ============================================================================

@dataclass
class AgentTeam:
    """
    Team of agents working together

    Example: Sales Team
    - Sarah (Frontend): LinkedIn outreach, social engagement
    - Alex (Backend): CRM updates, data analysis, email automation
    - Mike (Hybrid): Demos, calls, deal closing

    They collaborate on shared goals!
    """
    team_id: str
    team_name: str
    department: str

    # Team members
    members: List[TeamMember] = field(default_factory=list)

    # Team goals
    goals: Dict[str, str] = field(default_factory=dict)
    success_metrics: Dict[str, Any] = field(default_factory=dict)

    # Collaboration
    shared_tools: List[str] = field(default_factory=list)
    communication_channels: List[str] = field(default_factory=list)

    # Performance
    created_at: datetime = field(default_factory=datetime.utcnow)
    total_tasks_completed: int = 0
    total_revenue_generated: float = 0.0

    active: bool = True

    def get_backend_agents(self) -> List[TeamMember]:
        """Get all backend agents"""
        return [m for m in self.members if m.agent_type == AgentType.BACKEND]

    def get_frontend_agents(self) -> List[TeamMember]:
        """Get all frontend agents"""
        return [m for m in self.members if m.agent_type == AgentType.FRONTEND]

    def get_team_lead(self) -> Optional[TeamMember]:
        """Get team lead"""
        leads = [m for m in self.members if m.team_role == TeamRole.LEAD]
        return leads[0] if leads else None


# ============================================================================
# TEAM TASK
# ============================================================================

@dataclass
class TeamTask:
    """
    Task that requires collaboration between agents

    Example: "Close enterprise deal with BigCorp"
    - Sarah (Frontend): LinkedIn engagement, builds relationship
    - Alex (Backend): Prepares proposal, CRM data, pricing
    - Mike (Hybrid): Conducts demo, negotiates, closes

    Each agent does their part!
    """
    task_id: str
    task_name: str
    description: str
    team_id: str

    # Task breakdown
    subtasks: List[Dict[str, Any]] = field(default_factory=list)
    # [{"subtask_id": "...", "assigned_to": "agent_id", "type": "backend/frontend", ...}]

    # Status
    status: str = "pending"  # pending, in_progress, completed, failed
    priority: int = 5  # 1-10

    # Timing
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Results
    outcome: Optional[str] = None
    revenue_generated: float = 0.0


# ============================================================================
# TEAM MANAGER
# ============================================================================

class TeamManager:
    """
    Manages agent teams and collaboration

    Coordinates backend + frontend agents working together!
    """

    def __init__(self):
        self.teams: Dict[str, AgentTeam] = {}
        self.tasks: Dict[str, TeamTask] = {}

    def create_team(
        self,
        team_name: str,
        department: str,
        goals: Dict[str, str],
        **kwargs
    ) -> AgentTeam:
        """Create new agent team"""
        import secrets

        team_id = f"team_{secrets.token_urlsafe(8)}"

        team = AgentTeam(
            team_id=team_id,
            team_name=team_name,
            department=department,
            goals=goals,
            **kwargs
        )

        self.teams[team_id] = team

        print(f"✅ Team created: {team_name}")
        print(f"   Team ID: {team_id}")
        print(f"   Department: {department}")

        return team

    def add_team_member(
        self,
        team_id: str,
        agent_id: str,
        agent_name: str,
        agent_type: AgentType,
        team_role: TeamRole,
        **kwargs
    ) -> bool:
        """Add agent to team"""
        if team_id not in self.teams:
            print(f"❌ Team not found: {team_id}")
            return False

        team = self.teams[team_id]

        member = TeamMember(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_type=agent_type,
            team_role=team_role,
            **kwargs
        )

        team.members.append(member)

        print(f"✅ Added {agent_name} to {team.team_name}")
        print(f"   Type: {agent_type.value}")
        print(f"   Role: {team_role.value}")

        return True

    def create_team_task(
        self,
        team_id: str,
        task_name: str,
        description: str,
        subtasks: List[Dict[str, Any]],
        **kwargs
    ) -> TeamTask:
        """
        Create task that requires team collaboration

        Example subtasks:
        [
            {
                "subtask_id": "linkedin_outreach",
                "name": "Engage with prospect on LinkedIn",
                "assigned_to": "sarah_001",  # Frontend agent
                "type": "frontend",
                "tools": ["LinkedIn", "Browser"],
                "deliverable": "Built relationship, got response"
            },
            {
                "subtask_id": "prepare_proposal",
                "name": "Prepare custom proposal with pricing",
                "assigned_to": "alex_001",  # Backend agent
                "type": "backend",
                "tools": ["CRM API", "Pricing Engine"],
                "deliverable": "Proposal PDF ready"
            },
            {
                "subtask_id": "conduct_demo",
                "name": "Conduct product demo",
                "assigned_to": "mike_001",  # Hybrid agent
                "type": "hybrid",
                "tools": ["Zoom", "Demo Environment"],
                "deliverable": "Demo completed, next steps agreed"
            }
        ]
        """
        import secrets

        task_id = f"task_{secrets.token_urlsafe(8)}"

        task = TeamTask(
            task_id=task_id,
            task_name=task_name,
            description=description,
            team_id=team_id,
            subtasks=subtasks,
            **kwargs
        )

        self.tasks[task_id] = task

        print(f"\n✅ Team task created: {task_name}")
        print(f"   Task ID: {task_id}")
        print(f"   Subtasks: {len(subtasks)}")

        for subtask in subtasks:
            print(f"\n   • {subtask['name']}")
            print(f"     Assigned to: {subtask['assigned_to']}")
            print(f"     Type: {subtask['type']}")

        return task

    def assign_subtask_automatically(
        self,
        team_id: str,
        subtask_type: str,  # "frontend", "backend", "hybrid"
        task_description: str
    ) -> Optional[str]:
        """
        Automatically assign subtask to best agent

        Finds available agent with matching type and skills!
        """
        if team_id not in self.teams:
            return None

        team = self.teams[team_id]

        # Find agents matching type
        candidates = []
        for member in team.members:
            if member.agent_type.value == subtask_type and member.active:
                candidates.append(member)

        if not candidates:
            # Try hybrid agents
            candidates = [m for m in team.members if m.agent_type == AgentType.HYBRID and m.active]

        if not candidates:
            print(f"⚠️  No available agents for {subtask_type} task")
            return None

        # Pick agent with best success rate
        best_agent = max(candidates, key=lambda m: m.success_rate)

        print(f"✅ Auto-assigned to {best_agent.agent_name} ({best_agent.agent_type.value})")
        return best_agent.agent_id

    def get_team_status(self, team_id: str) -> Dict:
        """Get team status and performance"""
        if team_id not in self.teams:
            return {}

        team = self.teams[team_id]

        # Count tasks
        team_tasks = [t for t in self.tasks.values() if t.team_id == team_id]
        completed_tasks = [t for t in team_tasks if t.status == "completed"]
        in_progress_tasks = [t for t in team_tasks if t.status == "in_progress"]

        # Calculate total revenue
        total_revenue = sum(t.revenue_generated for t in completed_tasks)

        status = {
            "team_name": team.team_name,
            "team_id": team_id,
            "department": team.department,
            "member_count": len(team.members),
            "backend_agents": len(team.get_backend_agents()),
            "frontend_agents": len(team.get_frontend_agents()),
            "total_tasks": len(team_tasks),
            "completed_tasks": len(completed_tasks),
            "in_progress_tasks": len(in_progress_tasks),
            "total_revenue": total_revenue,
            "active": team.active
        }

        return status

    def get_team_summary(self, team_id: str) -> str:
        """Get human-readable team summary"""
        if team_id not in self.teams:
            return "Team not found"

        team = self.teams[team_id]
        status = self.get_team_status(team_id)

        summary = f"\n{'='*80}\n"
        summary += f"TEAM: {team.team_name}\n"
        summary += f"{'='*80}\n\n"

        summary += f"📊 TEAM OVERVIEW:\n"
        summary += f"   Department: {team.department}\n"
        summary += f"   Members: {status['member_count']}\n"
        summary += f"   • Backend Agents: {status['backend_agents']}\n"
        summary += f"   • Frontend Agents: {status['frontend_agents']}\n"

        summary += f"\n👥 TEAM MEMBERS:\n"
        for member in team.members:
            summary += f"   • {member.agent_name} ({member.agent_type.value})\n"
            summary += f"     Role: {member.team_role.value}\n"
            summary += f"     Success Rate: {member.success_rate:.1f}%\n"
            if member.specializations:
                summary += f"     Specializations: {', '.join(member.specializations)}\n"

        summary += f"\n🎯 TEAM GOALS:\n"
        for goal, target in team.goals.items():
            summary += f"   • {goal}: {target}\n"

        summary += f"\n📈 PERFORMANCE:\n"
        summary += f"   Total Tasks: {status['total_tasks']}\n"
        summary += f"   Completed: {status['completed_tasks']}\n"
        summary += f"   In Progress: {status['in_progress_tasks']}\n"
        summary += f"   Revenue Generated: ${status['total_revenue']:,.2f}\n"

        summary += f"\n{'='*80}\n"

        return summary


# ============================================================================
# PRE-BUILT TEAMS
# ============================================================================

def create_sales_dream_team(manager: TeamManager) -> AgentTeam:
    """
    Create the ultimate sales team

    Sarah (Frontend):
    - LinkedIn outreach and engagement
    - Reddit community building
    - Social media presence
    - Visual relationship building

    Alex (Backend):
    - CRM automation (API)
    - Email campaigns
    - Data analysis
    - Lead scoring
    - Proposal generation

    Mike (Hybrid):
    - Product demos
    - Sales calls
    - Deal closing
    - Contract negotiation
    """

    # Create team
    team = manager.create_team(
        team_name="Sales Dream Team",
        department="Sales",
        goals={
            "Monthly Revenue": "$100,000",
            "Close Rate": "40%+",
            "LinkedIn Engagement": "500+ connections/month",
            "Email Response Rate": "50%+"
        },
        success_metrics={
            "deals_closed": 0,
            "revenue_generated": 0.0,
            "linkedin_connections": 0,
            "emails_sent": 0
        },
        shared_tools=["GoHighLevel CRM", "Slack", "Google Workspace"],
        communication_channels=["Slack #sales-team", "Daily standup at 9am"]
    )

    # Add Sarah (Frontend Specialist)
    manager.add_team_member(
        team_id=team.team_id,
        agent_id="sarah_001",
        agent_name="Sarah Thompson",
        agent_type=AgentType.FRONTEND,
        team_role=TeamRole.SPECIALIST,
        skills=["LinkedIn Outreach", "Social Selling", "Relationship Building"],
        specializations=["LinkedIn", "Reddit", "Community Engagement"],
        tools=["LinkedIn Sales Navigator", "Reddit", "Browser Automation", "Screenshot Tools"]
    )

    # Add Alex (Backend Specialist)
    manager.add_team_member(
        team_id=team.team_id,
        agent_id="alex_001",
        agent_name="Alex Rodriguez",
        agent_type=AgentType.BACKEND,
        team_role=TeamRole.SPECIALIST,
        skills=["API Integration", "Data Analysis", "Email Automation"],
        specializations=["CRM APIs", "Lead Scoring", "Proposal Generation"],
        tools=["GoHighLevel API", "Email API", "Data Analytics", "Python"]
    )

    # Add Mike (Hybrid Lead)
    manager.add_team_member(
        team_id=team.team_id,
        agent_id="mike_001",
        agent_name="Mike Chen",
        agent_type=AgentType.HYBRID,
        team_role=TeamRole.LEAD,
        skills=["Sales Demos", "Deal Closing", "Negotiation", "Leadership"],
        specializations=["Product Knowledge", "Enterprise Sales", "Team Coordination"],
        tools=["Zoom", "GoHighLevel", "Calendly", "Contract Management"]
    )

    return team


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print(" " * 15 + "🤝 AGENT TEAM COLLABORATION DEMO")
    print("=" * 80)

    print("\n🎯 The Power of Team Collaboration:")
    print("   • Frontend agents handle visual/UI tasks")
    print("   • Backend agents handle APIs/data")
    print("   • Together they're UNSTOPPABLE!")

    # Create manager
    manager = TeamManager()

    # Create sales dream team
    print("\n\n📋 Creating Sales Dream Team...")
    team = create_sales_dream_team(manager)

    # Show team summary
    print(manager.get_team_summary(team.team_id))

    # Create collaborative task
    print("\n\n🎯 Example: Close Enterprise Deal")
    print("-" * 80)

    task = manager.create_team_task(
        team_id=team.team_id,
        task_name="Close $50K Enterprise Deal with BigCorp",
        description="Land BigCorp as enterprise customer",
        priority=10,
        subtasks=[
            {
                "subtask_id": "linkedin_research",
                "name": "Research BigCorp executives on LinkedIn",
                "assigned_to": "sarah_001",  # Frontend
                "type": "frontend",
                "tools": ["LinkedIn", "Browser"],
                "deliverable": "List of 5 decision makers with insights",
                "estimated_time": "2 hours"
            },
            {
                "subtask_id": "linkedin_outreach",
                "name": "Connect and engage with executives",
                "assigned_to": "sarah_001",  # Frontend
                "type": "frontend",
                "tools": ["LinkedIn", "Browser"],
                "deliverable": "3+ connections accepted, ongoing engagement",
                "estimated_time": "1 week"
            },
            {
                "subtask_id": "prepare_proposal",
                "name": "Generate custom proposal with pricing",
                "assigned_to": "alex_001",  # Backend
                "type": "backend",
                "tools": ["CRM API", "Pricing Engine", "Proposal Generator"],
                "deliverable": "Professional proposal PDF",
                "estimated_time": "3 hours"
            },
            {
                "subtask_id": "email_nurture",
                "name": "Run automated email nurture sequence",
                "assigned_to": "alex_001",  # Backend
                "type": "backend",
                "tools": ["Email API", "CRM"],
                "deliverable": "5-email sequence sent, engagement tracked",
                "estimated_time": "2 weeks"
            },
            {
                "subtask_id": "schedule_demo",
                "name": "Schedule and conduct product demo",
                "assigned_to": "mike_001",  # Hybrid
                "type": "hybrid",
                "tools": ["Calendly", "Zoom", "Demo Environment"],
                "deliverable": "Demo completed, next steps agreed",
                "estimated_time": "1 hour + prep"
            },
            {
                "subtask_id": "negotiate_close",
                "name": "Negotiate terms and close deal",
                "assigned_to": "mike_001",  # Hybrid
                "type": "hybrid",
                "tools": ["CRM", "Contract System"],
                "deliverable": "Contract signed, $50K revenue!",
                "estimated_time": "1 week"
            }
        ]
    )

    print("\n\n🔄 How The Team Collaborates:")
    print("-" * 80)
    print("""
Week 1:
  - Sarah: Researches BigCorp on LinkedIn (FRONTEND - uses browser)
  - Sarah: Connects with 5 executives (FRONTEND - clicks, types, screenshots)
  - Alex: Pulls BigCorp data from CRM (BACKEND - API call)
  - Alex: Generates custom pricing (BACKEND - Python script)

Week 2:
  - Sarah: Engages with LinkedIn connections (FRONTEND - comments, DMs)
  - Sarah: Screenshots all interactions for proof
  - Alex: Starts email nurture sequence (BACKEND - Email API)
  - Alex: Tracks email engagement (BACKEND - database)

Week 3:
  - Sarah: One executive responds interested!
  - Sarah: Hands off to Mike (TEAM LEAD)
  - Mike: Schedules demo via Calendly (HYBRID - uses UI + API)
  - Alex: Sends proposal before demo (BACKEND - automated)

Week 4:
  - Mike: Conducts amazing demo (HYBRID - Zoom + screen share)
  - Sarah: Executive engages on LinkedIn post during demo!
  - Alex: Updates CRM with demo notes (BACKEND - API)
  - Mike: Negotiates and closes deal! 🎉

Result:
  ✅ $50,000 deal closed
  ✅ Each agent did what they do best
  ✅ Frontend + Backend + Hybrid = UNSTOPPABLE
  ✅ Visual proof of every step (Sarah's screenshots)
  ✅ Clean data in CRM (Alex's automation)
  ✅ Human touch when needed (Mike's demo)
    """)

    print("\n" + "=" * 80)
    print("🌸 AGENT TEAMS: The Future of AI Work!")
    print("=" * 80)
