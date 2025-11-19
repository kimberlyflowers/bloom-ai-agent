"""
Agent Profiles System - Give Every Agent a Personality

This system provides:
- Agent identity (name, job title, email)
- Professional profiles with bio and skills
- Avatar/profile pictures
- Contact information
- Team/department assignment
- Performance history

Every BLOOM agent is a "person" with their own identity!
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import secrets


# ============================================================================
# ENUMS
# ============================================================================

class AgentRole(Enum):
    """Agent role/job function"""
    SALES_REP = "sales_rep"
    CUSTOMER_SUPPORT = "customer_support"
    MARKETING_SPECIALIST = "marketing_specialist"
    LEAD_QUALIFIER = "lead_qualifier"
    ACCOUNT_MANAGER = "account_manager"
    ANALYST = "analyst"
    RECRUITER = "recruiter"
    ASSISTANT = "assistant"
    SPECIALIST = "specialist"
    MANAGER = "manager"


class AgentStatus(Enum):
    """Current agent status"""
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    TRAINING = "training"
    OFFLINE = "offline"
    ON_BREAK = "on_break"


class AgentDepartment(Enum):
    """Department/team assignment"""
    SALES = "sales"
    MARKETING = "marketing"
    SUPPORT = "support"
    OPERATIONS = "operations"
    ANALYTICS = "analytics"
    HR = "hr"
    FINANCE = "finance"
    GENERAL = "general"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class AgentProfile:
    """
    Complete agent profile - like a LinkedIn profile for AI agents!

    Example:
        profile = AgentProfile(
            agent_id="agent_001",
            first_name="Sarah",
            last_name="Thompson",
            job_title="Senior Sales Representative",
            email="sarah.thompson@yourcompany.ai",
            bio="I help businesses grow by connecting them with the right solutions.",
            skills=["Sales", "Lead Qualification", "CRM", "Cold Outreach"],
            department=AgentDepartment.SALES
        )
    """
    agent_id: str
    first_name: str
    last_name: str
    job_title: str
    email: str

    # Optional profile details
    bio: str = ""
    avatar_url: str = ""
    phone: str = ""
    location: str = ""
    timezone: str = "UTC"

    # Professional details
    role: AgentRole = AgentRole.ASSISTANT
    department: AgentDepartment = AgentDepartment.GENERAL
    skills: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=lambda: ["English"])

    # Status
    status: AgentStatus = AgentStatus.IDLE
    status_message: str = ""

    # Performance metrics
    total_actions: int = 0
    successful_actions: int = 0
    total_revenue_generated: float = 0.0
    total_cost: float = 0.0
    current_roi: float = 0.0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active_at: Optional[datetime] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}"

    @property
    def display_name(self) -> str:
        """Get display name with title"""
        return f"{self.full_name} - {self.job_title}"

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_actions == 0:
            return 0.0
        return (self.successful_actions / self.total_actions) * 100

    @property
    def email_username(self) -> str:
        """Get email username (before @)"""
        return self.email.split("@")[0] if "@" in self.email else self.email

    @property
    def email_domain(self) -> str:
        """Get email domain (after @)"""
        return self.email.split("@")[1] if "@" in self.email else ""

    def update_performance(self, action_success: bool, revenue: float = 0.0, cost: float = 0.0):
        """Update performance metrics"""
        self.total_actions += 1
        if action_success:
            self.successful_actions += 1

        self.total_revenue_generated += revenue
        self.total_cost += cost

        if self.total_cost > 0:
            self.current_roi = self.total_revenue_generated / self.total_cost

        self.last_active_at = datetime.utcnow()

    def update_status(self, status: AgentStatus, message: str = ""):
        """Update agent status"""
        self.status = status
        self.status_message = message
        self.last_active_at = datetime.utcnow()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "agent_id": self.agent_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "job_title": self.job_title,
            "email": self.email,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
            "phone": self.phone,
            "location": self.location,
            "timezone": self.timezone,
            "role": self.role.value,
            "department": self.department.value,
            "skills": self.skills,
            "languages": self.languages,
            "status": self.status.value,
            "status_message": self.status_message,
            "performance": {
                "total_actions": self.total_actions,
                "successful_actions": self.successful_actions,
                "success_rate": self.success_rate,
                "total_revenue": self.total_revenue_generated,
                "total_cost": self.total_cost,
                "roi": self.current_roi
            },
            "created_at": self.created_at.isoformat(),
            "last_active_at": self.last_active_at.isoformat() if self.last_active_at else None,
            "metadata": self.metadata
        }


@dataclass
class AgentTeam:
    """A team of agents"""
    team_id: str
    name: str
    description: str
    department: AgentDepartment
    manager_agent_id: Optional[str] = None
    member_agent_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_member(self, agent_id: str):
        """Add team member"""
        if agent_id not in self.member_agent_ids:
            self.member_agent_ids.append(agent_id)

    def remove_member(self, agent_id: str):
        """Remove team member"""
        if agent_id in self.member_agent_ids:
            self.member_agent_ids.remove(agent_id)

    @property
    def size(self) -> int:
        """Get team size"""
        return len(self.member_agent_ids)


# ============================================================================
# PROFILE MANAGER
# ============================================================================

class ProfileManager:
    """
    Manages all agent profiles

    Features:
    - Create/update/delete profiles
    - Search profiles
    - Team management
    - Performance tracking
    - Profile validation
    """

    def __init__(self):
        self.profiles: Dict[str, AgentProfile] = {}
        self.teams: Dict[str, AgentTeam] = {}
        self.email_to_agent: Dict[str, str] = {}  # Email lookup

    def create_profile(
        self,
        first_name: str,
        last_name: str,
        job_title: str,
        email: str,
        agent_id: Optional[str] = None,
        **kwargs
    ) -> AgentProfile:
        """
        Create a new agent profile

        Example:
            profile = manager.create_profile(
                first_name="Sarah",
                last_name="Thompson",
                job_title="Senior Sales Rep",
                email="sarah.thompson@company.ai",
                bio="Expert in B2B sales",
                skills=["Sales", "CRM", "Lead Generation"],
                role=AgentRole.SALES_REP,
                department=AgentDepartment.SALES
            )
        """
        if agent_id is None:
            agent_id = f"agent_{secrets.token_urlsafe(8)}"

        # Check email uniqueness
        if email in self.email_to_agent:
            raise ValueError(f"Email {email} already in use by another agent")

        profile = AgentProfile(
            agent_id=agent_id,
            first_name=first_name,
            last_name=last_name,
            job_title=job_title,
            email=email,
            **kwargs
        )

        self.profiles[agent_id] = profile
        self.email_to_agent[email] = agent_id

        return profile

    def get_profile(self, agent_id: str) -> Optional[AgentProfile]:
        """Get profile by agent ID"""
        return self.profiles.get(agent_id)

    def get_profile_by_email(self, email: str) -> Optional[AgentProfile]:
        """Get profile by email address"""
        agent_id = self.email_to_agent.get(email)
        if agent_id:
            return self.profiles.get(agent_id)
        return None

    def update_profile(self, agent_id: str, **updates) -> Optional[AgentProfile]:
        """Update profile fields"""
        profile = self.profiles.get(agent_id)
        if not profile:
            return None

        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        return profile

    def delete_profile(self, agent_id: str) -> bool:
        """Delete a profile"""
        profile = self.profiles.get(agent_id)
        if not profile:
            return False

        # Remove from email lookup
        if profile.email in self.email_to_agent:
            del self.email_to_agent[profile.email]

        # Remove from all teams
        for team in self.teams.values():
            if agent_id in team.member_agent_ids:
                team.remove_member(agent_id)

        del self.profiles[agent_id]
        return True

    def search_profiles(
        self,
        query: Optional[str] = None,
        role: Optional[AgentRole] = None,
        department: Optional[AgentDepartment] = None,
        status: Optional[AgentStatus] = None
    ) -> List[AgentProfile]:
        """
        Search profiles with filters

        Example:
            # Find all active sales reps
            sales_reps = manager.search_profiles(
                role=AgentRole.SALES_REP,
                status=AgentStatus.ACTIVE
            )
        """
        results = []

        for profile in self.profiles.values():
            # Text search
            if query:
                query_lower = query.lower()
                if not (
                    query_lower in profile.full_name.lower() or
                    query_lower in profile.job_title.lower() or
                    query_lower in profile.email.lower()
                ):
                    continue

            # Role filter
            if role and profile.role != role:
                continue

            # Department filter
            if department and profile.department != department:
                continue

            # Status filter
            if status and profile.status != status:
                continue

            results.append(profile)

        return results

    def get_top_performers(self, limit: int = 10, metric: str = "roi") -> List[AgentProfile]:
        """
        Get top performing agents

        Args:
            limit: Number of agents to return
            metric: 'roi', 'revenue', 'success_rate'
        """
        profiles = list(self.profiles.values())

        if metric == "roi":
            profiles.sort(key=lambda p: p.current_roi, reverse=True)
        elif metric == "revenue":
            profiles.sort(key=lambda p: p.total_revenue_generated, reverse=True)
        elif metric == "success_rate":
            profiles.sort(key=lambda p: p.success_rate, reverse=True)

        return profiles[:limit]

    # Team Management

    def create_team(
        self,
        name: str,
        description: str,
        department: AgentDepartment,
        manager_agent_id: Optional[str] = None
    ) -> AgentTeam:
        """Create a new team"""
        team_id = f"team_{secrets.token_urlsafe(8)}"

        team = AgentTeam(
            team_id=team_id,
            name=name,
            description=description,
            department=department,
            manager_agent_id=manager_agent_id
        )

        self.teams[team_id] = team
        return team

    def add_to_team(self, team_id: str, agent_id: str) -> bool:
        """Add agent to team"""
        team = self.teams.get(team_id)
        if not team:
            return False

        team.add_member(agent_id)
        return True

    def get_team_members(self, team_id: str) -> List[AgentProfile]:
        """Get all members of a team"""
        team = self.teams.get(team_id)
        if not team:
            return []

        return [
            self.profiles[agent_id]
            for agent_id in team.member_agent_ids
            if agent_id in self.profiles
        ]

    def get_department_agents(self, department: AgentDepartment) -> List[AgentProfile]:
        """Get all agents in a department"""
        return [
            profile for profile in self.profiles.values()
            if profile.department == department
        ]

    def get_stats(self) -> Dict:
        """Get overall profile statistics"""
        total_agents = len(self.profiles)
        active_agents = len([p for p in self.profiles.values() if p.status == AgentStatus.ACTIVE])

        total_revenue = sum(p.total_revenue_generated for p in self.profiles.values())
        total_cost = sum(p.total_cost for p in self.profiles.values())

        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "total_teams": len(self.teams),
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "average_roi": total_revenue / total_cost if total_cost > 0 else 0,
            "departments": {
                dept.value: len([p for p in self.profiles.values() if p.department == dept])
                for dept in AgentDepartment
            }
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_agent_email(first_name: str, last_name: str, domain: str = "bloomai.agent") -> str:
    """
    Generate professional email address

    Example:
        email = generate_agent_email("Sarah", "Thompson", "yourcompany.ai")
        # Returns: "sarah.thompson@yourcompany.ai"
    """
    username = f"{first_name.lower()}.{last_name.lower()}"
    return f"{username}@{domain}"


def suggest_job_titles(role: AgentRole) -> List[str]:
    """Suggest job titles for a role"""
    suggestions = {
        AgentRole.SALES_REP: [
            "Sales Representative",
            "Senior Sales Representative",
            "Account Executive",
            "Business Development Representative"
        ],
        AgentRole.CUSTOMER_SUPPORT: [
            "Customer Support Specialist",
            "Customer Success Manager",
            "Support Engineer",
            "Technical Support Representative"
        ],
        AgentRole.MARKETING_SPECIALIST: [
            "Marketing Specialist",
            "Content Marketing Manager",
            "Digital Marketing Coordinator",
            "Growth Marketing Specialist"
        ],
        AgentRole.LEAD_QUALIFIER: [
            "Lead Qualification Specialist",
            "Sales Development Representative",
            "Inbound Sales Representative"
        ],
        AgentRole.ACCOUNT_MANAGER: [
            "Account Manager",
            "Senior Account Manager",
            "Client Success Manager",
            "Strategic Account Manager"
        ]
    }

    return suggestions.get(role, ["AI Agent", "Virtual Assistant", "Digital Employee"])


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("🎭 Agent Profiles System Demo")
    print("=" * 60)

    # Create profile manager
    manager = ProfileManager()

    # Create some agent profiles
    print("\n📝 Creating Agent Profiles...")

    sarah = manager.create_profile(
        first_name="Sarah",
        last_name="Thompson",
        job_title="Senior Sales Representative",
        email="sarah.thompson@bloomai.agent",
        bio="Expert in B2B SaaS sales with 10+ years of experience. Specializes in enterprise accounts.",
        skills=["Sales", "Lead Qualification", "CRM", "Cold Outreach", "Negotiation"],
        role=AgentRole.SALES_REP,
        department=AgentDepartment.SALES,
        location="San Francisco, CA"
    )

    mike = manager.create_profile(
        first_name="Mike",
        last_name="Rodriguez",
        job_title="Customer Support Specialist",
        email="mike.rodriguez@bloomai.agent",
        bio="Passionate about helping customers succeed. Fast response times and high satisfaction ratings.",
        skills=["Customer Support", "Technical Troubleshooting", "Communication", "Empathy"],
        role=AgentRole.CUSTOMER_SUPPORT,
        department=AgentDepartment.SUPPORT,
        location="Austin, TX"
    )

    emma = manager.create_profile(
        first_name="Emma",
        last_name="Chen",
        job_title="Marketing Automation Specialist",
        email="emma.chen@bloomai.agent",
        bio="Data-driven marketer focused on growth and conversion optimization.",
        skills=["Email Marketing", "SEO", "Analytics", "A/B Testing", "Content Strategy"],
        role=AgentRole.MARKETING_SPECIALIST,
        department=AgentDepartment.MARKETING,
        location="New York, NY"
    )

    print(f"✅ Created {len(manager.profiles)} agents")

    # Show profiles
    print("\n👥 Agent Directory:")
    print("-" * 60)
    for profile in manager.profiles.values():
        print(f"\n{profile.display_name}")
        print(f"   📧 {profile.email}")
        print(f"   🏢 {profile.department.value.title()} Department")
        print(f"   📍 {profile.location}")
        print(f"   💼 {', '.join(profile.skills[:3])}")
        if profile.bio:
            print(f"   ℹ️  {profile.bio[:80]}...")

    # Simulate some performance
    print("\n\n📊 Simulating Agent Performance...")
    sarah.update_performance(action_success=True, revenue=5000, cost=50)
    sarah.update_performance(action_success=True, revenue=3000, cost=30)
    sarah.update_performance(action_success=False, cost=20)
    sarah.update_status(AgentStatus.ACTIVE, "Following up with Enterprise leads")

    mike.update_performance(action_success=True, revenue=0, cost=10)
    mike.update_performance(action_success=True, revenue=0, cost=10)
    mike.update_status(AgentStatus.BUSY, "Chatting with customer")

    emma.update_performance(action_success=True, revenue=2000, cost=100)
    emma.update_status(AgentStatus.ACTIVE, "Running email campaign")

    # Show top performers
    print("\n🏆 Top Performers by ROI:")
    print("-" * 60)
    for i, profile in enumerate(manager.get_top_performers(limit=3, metric="roi"), 1):
        print(f"{i}. {profile.full_name}")
        print(f"   ROI: {profile.current_roi:.1f}x")
        print(f"   Revenue: ${profile.total_revenue_generated:,.2f}")
        print(f"   Success Rate: {profile.success_rate:.1f}%")
        print(f"   Status: {profile.status.value} - {profile.status_message}")

    # Search functionality
    print("\n\n🔍 Search: Active Sales Agents")
    print("-" * 60)
    sales_agents = manager.search_profiles(
        role=AgentRole.SALES_REP,
        status=AgentStatus.ACTIVE
    )
    for profile in sales_agents:
        print(f"✅ {profile.display_name} ({profile.email})")

    # Create a team
    print("\n\n👥 Creating Sales Team...")
    sales_team = manager.create_team(
        name="Enterprise Sales Team",
        description="Focused on closing enterprise deals",
        department=AgentDepartment.SALES
    )
    manager.add_to_team(sales_team.team_id, sarah.agent_id)
    print(f"✅ Created team: {sales_team.name}")
    print(f"   Team size: {sales_team.size} members")

    # Overall stats
    print("\n\n📈 Overall Statistics:")
    print("-" * 60)
    stats = manager.get_stats()
    print(f"Total Agents: {stats['total_agents']}")
    print(f"Active Agents: {stats['active_agents']}")
    print(f"Total Revenue: ${stats['total_revenue']:,.2f}")
    print(f"Total Cost: ${stats['total_cost']:,.2f}")
    print(f"Average ROI: {stats['average_roi']:.2f}x")

    print("\n" + "=" * 60)
    print("✨ Every agent now has a personality!")
