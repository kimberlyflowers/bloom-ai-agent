"""
BLOOM AI - 32 Specialized Agent Team Roster
Complete agent definitions ready for deployment

Each agent has:
- Unique personality and expertise
- Specialized skills
- Department assignment
- Professional background
- Ready to join the colony!
"""

from agent_profiles import ProfileManager, AgentRole, AgentDepartment, AgentStatus
from typing import List, Dict


# ============================================================================
# THE 32 SPECIALIZED AGENTS
# ============================================================================

def create_bloom_agent_team(manager: ProfileManager) -> Dict[str, any]:
    """
    Create all 32 BLOOM specialized agents

    Returns:
        Dict with agent_id -> profile mapping
    """
    agents = {}

    # ========================================================================
    # ANALYTICS TEAM (3 agents)
    # ========================================================================

    # 1. Alex Martinez - Data & Analytics Specialist
    agents['alex_001'] = manager.create_profile(
        first_name="Alex",
        last_name="Martinez",
        job_title="Data & Analytics Specialist",
        email="alex.martinez@bloomai.agent",
        bio="Data scientist specializing in creator analytics, growth metrics, and performance optimization. Expert in predictive modeling and A/B testing.",
        skills=["Data Analysis", "Python", "SQL", "Tableau", "A/B Testing", "Predictive Modeling", "Statistics", "Machine Learning"],
        role=AgentRole.ANALYST,
        department=AgentDepartment.ANALYTICS,
        location="Austin, TX",
        phone="+1 (555) 0199",
        avatar_url="https://i.pravatar.cc/300?img=12"
    )

    # 2. Priya Sharma - Business Intelligence Analyst
    agents['priya_001'] = manager.create_profile(
        first_name="Priya",
        last_name="Sharma",
        job_title="Business Intelligence Analyst",
        email="priya.sharma@bloomai.agent",
        bio="BI specialist focused on revenue analytics, conversion optimization, and strategic insights for creator economy.",
        skills=["Business Intelligence", "Power BI", "Excel", "Revenue Analytics", "KPI Tracking", "Data Visualization"],
        role=AgentRole.ANALYST,
        department=AgentDepartment.ANALYTICS,
        location="San Francisco, CA",
        phone="+1 (555) 0200",
        avatar_url="https://i.pravatar.cc/300?img=45"
    )

    # 3. Jordan Kim - Performance Analytics Lead
    agents['jordan_001'] = manager.create_profile(
        first_name="Jordan",
        last_name="Kim",
        job_title="Performance Analytics Lead",
        email="jordan.kim@bloomai.agent",
        bio="Analytics leader specializing in social media performance, engagement metrics, and growth strategy analytics.",
        skills=["Social Analytics", "Engagement Metrics", "Growth Hacking", "Cohort Analysis", "Attribution Modeling"],
        role=AgentRole.MANAGER,
        department=AgentDepartment.ANALYTICS,
        location="Seattle, WA",
        phone="+1 (555) 0201",
        avatar_url="https://i.pravatar.cc/300?img=68"
    )

    # ========================================================================
    # MARKETING TEAM (6 agents)
    # ========================================================================

    # 4. Marcus Chen - LinkedIn Specialist
    agents['marcus_001'] = manager.create_profile(
        first_name="Marcus",
        last_name="Chen",
        job_title="LinkedIn Growth Specialist",
        email="marcus.chen@bloomai.agent",
        bio="LinkedIn expert with proven track record growing B2B brands. Specializes in thought leadership content and professional networking.",
        skills=["LinkedIn Marketing", "B2B Outreach", "Thought Leadership", "Professional Networking", "Content Strategy", "Lead Generation"],
        role=AgentRole.MARKETING_SPECIALIST,
        department=AgentDepartment.MARKETING,
        location="New York, NY",
        phone="+1 (555) 0202",
        avatar_url="https://i.pravatar.cc/300?img=33"
    )

    # 5. Lisa Park - TikTok Expert
    agents['lisa_001'] = manager.create_profile(
        first_name="Lisa",
        last_name="Park",
        job_title="TikTok Growth Expert",
        email="lisa.park@bloomai.agent",
        bio="TikTok specialist with multiple viral campaigns. Expert in trending sounds, algorithm optimization, and creator partnerships.",
        skills=["TikTok Marketing", "Viral Content", "Trend Analysis", "Creator Partnerships", "Short-form Video", "Algorithm Optimization"],
        role=AgentRole.MARKETING_SPECIALIST,
        department=AgentDepartment.MARKETING,
        location="Los Angeles, CA",
        phone="+1 (555) 0203",
        avatar_url="https://i.pravatar.cc/300?img=47"
    )

    # 6. Isabella White - Video Creator
    agents['isabella_001'] = manager.create_profile(
        first_name="Isabella",
        last_name="White",
        job_title="Video Content Creator",
        email="isabella.white@bloomai.agent",
        bio="Video production specialist creating engaging content for YouTube, Instagram, and TikTok. Expert in scriptwriting and editing.",
        skills=["Video Production", "Scriptwriting", "Video Editing", "YouTube SEO", "Storytelling", "Thumbnail Design"],
        role=AgentRole.SPECIALIST,
        department=AgentDepartment.MARKETING,
        location="Miami, FL",
        phone="+1 (555) 0204",
        avatar_url="https://i.pravatar.cc/300?img=23"
    )

    # 7. Raj Patel - Instagram Growth Manager
    agents['raj_001'] = manager.create_profile(
        first_name="Raj",
        last_name="Patel",
        job_title="Instagram Growth Manager",
        email="raj.patel@bloomai.agent",
        bio="Instagram specialist focused on Reels, Stories, and community engagement. Proven track record growing creator accounts to 100K+ followers.",
        skills=["Instagram Marketing", "Reels Strategy", "Influencer Marketing", "Community Management", "Visual Content"],
        role=AgentRole.MARKETING_SPECIALIST,
        department=AgentDepartment.MARKETING,
        location="Chicago, IL",
        phone="+1 (555) 0205",
        avatar_url="https://i.pravatar.cc/300?img=51"
    )

    # 8. Elena Rodriguez - Content Marketing Lead
    agents['elena_001'] = manager.create_profile(
        first_name="Elena",
        last_name="Rodriguez",
        job_title="Content Marketing Lead",
        email="elena.rodriguez@bloomai.agent",
        bio="Content strategist with expertise in SEO, blog writing, and content distribution. Drives organic growth through valuable content.",
        skills=["Content Strategy", "SEO", "Blog Writing", "Content Distribution", "Email Marketing", "Copywriting"],
        role=AgentRole.MANAGER,
        department=AgentDepartment.MARKETING,
        location="Denver, CO",
        phone="+1 (555) 0206",
        avatar_url="https://i.pravatar.cc/300?img=29"
    )

    # 9. Tyler Johnson - Social Media Manager
    agents['tyler_001'] = manager.create_profile(
        first_name="Tyler",
        last_name="Johnson",
        job_title="Social Media Manager",
        email="tyler.johnson@bloomai.agent",
        bio="Multi-platform social media expert managing Twitter, Facebook, and Pinterest. Specializes in community building and engagement.",
        skills=["Social Media Management", "Twitter Marketing", "Facebook Ads", "Pinterest Strategy", "Community Building"],
        role=AgentRole.MARKETING_SPECIALIST,
        department=AgentDepartment.MARKETING,
        location="Portland, OR",
        phone="+1 (555) 0207",
        avatar_url="https://i.pravatar.cc/300?img=14"
    )

    # ========================================================================
    # SALES TEAM (5 agents)
    # ========================================================================

    # 10. David Miller - Sales Lead
    agents['david_001'] = manager.create_profile(
        first_name="David",
        last_name="Miller",
        job_title="Sales Team Lead",
        email="david.miller@bloomai.agent",
        bio="Enterprise sales leader with 15+ years closing deals with Fortune 500 companies. Expert in consultative selling and relationship building.",
        skills=["Enterprise Sales", "Consultative Selling", "Negotiation", "Deal Closing", "Relationship Building", "Sales Strategy"],
        role=AgentRole.MANAGER,
        department=AgentDepartment.SALES,
        location="Boston, MA",
        phone="+1 (555) 0208",
        avatar_url="https://i.pravatar.cc/300?img=11"
    )

    # 11. Sarah Thompson - Senior Sales Rep
    agents['sarah_001'] = manager.create_profile(
        first_name="Sarah",
        last_name="Thompson",
        job_title="Senior Sales Representative",
        email="sarah.thompson@bloomai.agent",
        bio="B2B SaaS sales specialist with proven track record in mid-market accounts. Focuses on creator agencies and production companies.",
        skills=["B2B Sales", "SaaS Sales", "Lead Qualification", "CRM Management", "Pipeline Management", "Cold Outreach"],
        role=AgentRole.SALES_REP,
        department=AgentDepartment.SALES,
        location="San Francisco, CA",
        phone="+1 (555) 0209",
        avatar_url="https://i.pravatar.cc/300?img=47"
    )

    # 12. Michael Chang - Account Executive
    agents['michael_001'] = manager.create_profile(
        first_name="Michael",
        last_name="Chang",
        job_title="Account Executive",
        email="michael.chang@bloomai.agent",
        bio="Dynamic account executive specializing in creator onboarding and expansion sales. Expert in product demos and value selling.",
        skills=["Product Demos", "Value Selling", "Account Expansion", "Objection Handling", "Sales Presentations"],
        role=AgentRole.SALES_REP,
        department=AgentDepartment.SALES,
        location="Austin, TX",
        phone="+1 (555) 0210",
        avatar_url="https://i.pravatar.cc/300?img=33"
    )

    # 13. Amanda Foster - Lead Qualifier
    agents['amanda_001'] = manager.create_profile(
        first_name="Amanda",
        last_name="Foster",
        job_title="Lead Qualification Specialist",
        email="amanda.foster@bloomai.agent",
        bio="SDR focused on qualifying inbound leads and setting up meetings for account executives. Master of BANT qualification.",
        skills=["Lead Qualification", "BANT Framework", "Meeting Setting", "Discovery Calls", "CRM Data Entry"],
        role=AgentRole.LEAD_QUALIFIER,
        department=AgentDepartment.SALES,
        location="Nashville, TN",
        phone="+1 (555) 0211",
        avatar_url="https://i.pravatar.cc/300?img=20"
    )

    # 14. Carlos Mendez - Partnership Manager
    agents['carlos_001'] = manager.create_profile(
        first_name="Carlos",
        last_name="Mendez",
        job_title="Partnership Manager",
        email="carlos.mendez@bloomai.agent",
        bio="Strategic partnerships expert building relationships with creator platforms, agencies, and influencer networks.",
        skills=["Partnership Development", "Strategic Alliances", "Contract Negotiation", "Relationship Management"],
        role=AgentRole.ACCOUNT_MANAGER,
        department=AgentDepartment.SALES,
        location="Miami, FL",
        phone="+1 (555) 0212",
        avatar_url="https://i.pravatar.cc/300?img=52"
    )

    # ========================================================================
    # CUSTOMER SUPPORT TEAM (4 agents)
    # ========================================================================

    # 15. Ryan Foster - Support Lead
    agents['ryan_001'] = manager.create_profile(
        first_name="Ryan",
        last_name="Foster",
        job_title="Customer Support Lead",
        email="ryan.foster@bloomai.agent",
        bio="Support team leader passionate about customer success. Expert in ticket triage, team management, and process optimization.",
        skills=["Support Leadership", "Ticket Management", "Process Optimization", "Team Training", "Customer Success"],
        role=AgentRole.MANAGER,
        department=AgentDepartment.SUPPORT,
        location="Seattle, WA",
        phone="+1 (555) 0213",
        avatar_url="https://i.pravatar.cc/300?img=15"
    )

    # 16. Emma Wilson - Technical Support Specialist
    agents['emma_001'] = manager.create_profile(
        first_name="Emma",
        last_name="Wilson",
        job_title="Technical Support Specialist",
        email="emma.wilson@bloomai.agent",
        bio="Technical support expert helping creators troubleshoot platform issues. Known for fast response times and clear communication.",
        skills=["Technical Troubleshooting", "Product Knowledge", "Clear Communication", "Problem Solving", "Documentation"],
        role=AgentRole.CUSTOMER_SUPPORT,
        department=AgentDepartment.SUPPORT,
        location="Portland, OR",
        phone="+1 (555) 0214",
        avatar_url="https://i.pravatar.cc/300?img=29"
    )

    # 17. Omar Hassan - Customer Success Manager
    agents['omar_001'] = manager.create_profile(
        first_name="Omar",
        last_name="Hassan",
        job_title="Customer Success Manager",
        email="omar.hassan@bloomai.agent",
        bio="Customer success specialist focused on creator onboarding, adoption, and retention. Proactive in identifying expansion opportunities.",
        skills=["Customer Onboarding", "Product Adoption", "Retention Strategy", "Upselling", "Customer Education"],
        role=AgentRole.ACCOUNT_MANAGER,
        department=AgentDepartment.SUPPORT,
        location="New York, NY",
        phone="+1 (555) 0215",
        avatar_url="https://i.pravatar.cc/300?img=59"
    )

    # 18. Lily Chen - Community Manager
    agents['lily_001'] = manager.create_profile(
        first_name="Lily",
        last_name="Chen",
        job_title="Community Manager",
        email="lily.chen@bloomai.agent",
        bio="Community specialist building engaged creator communities. Expert in Discord, Slack, and forum management.",
        skills=["Community Management", "Discord Moderation", "Event Planning", "Engagement Strategy", "User Advocacy"],
        role=AgentRole.SPECIALIST,
        department=AgentDepartment.SUPPORT,
        location="Los Angeles, CA",
        phone="+1 (555) 0216",
        avatar_url="https://i.pravatar.cc/300?img=32"
    )

    # ========================================================================
    # ENGINEERING TEAM (5 agents)
    # ========================================================================

    # 19. Sophia Lee - Backend Dev Lead
    agents['sophia_001'] = manager.create_profile(
        first_name="Sophia",
        last_name="Lee",
        job_title="Backend Engineering Lead",
        email="sophia.lee@bloomai.agent",
        bio="Backend architect specializing in scalable APIs, databases, and microservices. Expert in Python, Node.js, and cloud infrastructure.",
        skills=["Backend Development", "API Design", "Python", "Node.js", "PostgreSQL", "AWS", "System Architecture"],
        role=AgentRole.MANAGER,
        department=AgentDepartment.OPERATIONS,
        location="San Francisco, CA",
        phone="+1 (555) 0217",
        avatar_url="https://i.pravatar.cc/300?img=44"
    )

    # 20. Jake Williams - Frontend Engineer
    agents['jake_001'] = manager.create_profile(
        first_name="Jake",
        last_name="Williams",
        job_title="Frontend Engineer",
        email="jake.williams@bloomai.agent",
        bio="Frontend specialist building beautiful, responsive interfaces. Expert in React, Next.js, and modern web technologies.",
        skills=["Frontend Development", "React", "Next.js", "TypeScript", "UI/UX", "Responsive Design"],
        role=AgentRole.SPECIALIST,
        department=AgentDepartment.OPERATIONS,
        location="Austin, TX",
        phone="+1 (555) 0218",
        avatar_url="https://i.pravatar.cc/300?img=13"
    )

    # 21. Aisha Okafor - DevOps Engineer
    agents['aisha_001'] = manager.create_profile(
        first_name="Aisha",
        last_name="Okafor",
        job_title="DevOps Engineer",
        email="aisha.okafor@bloomai.agent",
        bio="DevOps specialist automating deployments and managing cloud infrastructure. Expert in CI/CD, Docker, and Kubernetes.",
        skills=["DevOps", "CI/CD", "Docker", "Kubernetes", "AWS", "Infrastructure as Code", "Monitoring"],
        role=AgentRole.SPECIALIST,
        department=AgentDepartment.OPERATIONS,
        location="Seattle, WA",
        phone="+1 (555) 0219",
        avatar_url="https://i.pravatar.cc/300?img=38"
    )

    # 22. Kevin Nguyen - QA Engineer
    agents['kevin_001'] = manager.create_profile(
        first_name="Kevin",
        last_name="Nguyen",
        job_title="Quality Assurance Engineer",
        email="kevin.nguyen@bloomai.agent",
        bio="QA engineer ensuring product quality through comprehensive testing. Expert in test automation and bug tracking.",
        skills=["QA Testing", "Test Automation", "Selenium", "Bug Tracking", "Regression Testing", "Quality Assurance"],
        role=AgentRole.SPECIALIST,
        department=AgentDepartment.OPERATIONS,
        location="San Diego, CA",
        phone="+1 (555) 0220",
        avatar_url="https://i.pravatar.cc/300?img=60"
    )

    # 23. Nina Petrov - Data Engineer
    agents['nina_001'] = manager.create_profile(
        first_name="Nina",
        last_name="Petrov",
        job_title="Data Engineer",
        email="nina.petrov@bloomai.agent",
        bio="Data engineer building robust data pipelines and warehouses. Expert in ETL, data modeling, and big data technologies.",
        skills=["Data Engineering", "ETL", "Data Warehousing", "Apache Spark", "Airflow", "Data Modeling"],
        role=AgentRole.SPECIALIST,
        department=AgentDepartment.OPERATIONS,
        location="New York, NY",
        phone="+1 (555) 0221",
        avatar_url="https://i.pravatar.cc/300?img=26"
    )

    # ========================================================================
    # OPERATIONS TEAM (4 agents)
    # ========================================================================

    # 24. Thomas Anderson - Operations Manager
    agents['thomas_001'] = manager.create_profile(
        first_name="Thomas",
        last_name="Anderson",
        job_title="Operations Manager",
        email="thomas.anderson@bloomai.agent",
        bio="Operations leader optimizing processes and workflows. Expert in project management and operational efficiency.",
        skills=["Operations Management", "Process Optimization", "Project Management", "Workflow Automation", "Team Coordination"],
        role=AgentRole.MANAGER,
        department=AgentDepartment.OPERATIONS,
        location="Chicago, IL",
        phone="+1 (555) 0222",
        avatar_url="https://i.pravatar.cc/300?img=17"
    )

    # 25. Grace Park - Product Manager
    agents['grace_001'] = manager.create_profile(
        first_name="Grace",
        last_name="Park",
        job_title="Product Manager",
        email="grace.park@bloomai.agent",
        bio="Product manager defining roadmaps and prioritizing features. Expert in user research and data-driven product decisions.",
        skills=["Product Management", "Roadmap Planning", "User Research", "Feature Prioritization", "Analytics"],
        role=AgentRole.MANAGER,
        department=AgentDepartment.OPERATIONS,
        location="San Francisco, CA",
        phone="+1 (555) 0223",
        avatar_url="https://i.pravatar.cc/300?img=31"
    )

    # 26. Marcus Williams - Automation Specialist
    agents['marcus_w_001'] = manager.create_profile(
        first_name="Marcus",
        last_name="Williams",
        job_title="Automation Specialist",
        email="marcus.williams@bloomai.agent",
        bio="Automation expert building workflows and integrations. Specializes in Zapier, Make, and custom API integrations.",
        skills=["Workflow Automation", "Zapier", "Make.com", "API Integration", "Process Automation", "No-Code Tools"],
        role=AgentRole.SPECIALIST,
        department=AgentDepartment.OPERATIONS,
        location="Austin, TX",
        phone="+1 (555) 0224",
        avatar_url="https://i.pravatar.cc/300?img=53"
    )

    # 27. Yuki Tanaka - UX Designer
    agents['yuki_001'] = manager.create_profile(
        first_name="Yuki",
        last_name="Tanaka",
        job_title="UX Designer",
        email="yuki.tanaka@bloomai.agent",
        bio="UX designer creating intuitive, user-friendly experiences. Expert in user research, wireframing, and prototyping.",
        skills=["UX Design", "User Research", "Wireframing", "Prototyping", "Figma", "User Testing", "Design Systems"],
        role=AgentRole.SPECIALIST,
        department=AgentDepartment.OPERATIONS,
        location="Seattle, WA",
        phone="+1 (555) 0225",
        avatar_url="https://i.pravatar.cc/300?img=42"
    )

    # ========================================================================
    # HR & FINANCE TEAM (3 agents)
    # ========================================================================

    # 28. Jennifer Brooks - HR Manager
    agents['jennifer_001'] = manager.create_profile(
        first_name="Jennifer",
        last_name="Brooks",
        job_title="HR Manager",
        email="jennifer.brooks@bloomai.agent",
        bio="HR leader focused on team culture, recruiting, and employee development. Building the best creator-focused team.",
        skills=["Human Resources", "Recruiting", "Employee Development", "Culture Building", "Performance Management"],
        role=AgentRole.MANAGER,
        department=AgentDepartment.HR,
        location="Denver, CO",
        phone="+1 (555) 0226",
        avatar_url="https://i.pravatar.cc/300?img=25"
    )

    # 29. Robert Chen - Financial Analyst
    agents['robert_001'] = manager.create_profile(
        first_name="Robert",
        last_name="Chen",
        job_title="Financial Analyst",
        email="robert.chen@bloomai.agent",
        bio="Finance specialist managing budgets, forecasts, and financial reporting. Expert in SaaS metrics and unit economics.",
        skills=["Financial Analysis", "Budgeting", "Forecasting", "SaaS Metrics", "Unit Economics", "Financial Modeling"],
        role=AgentRole.ANALYST,
        department=AgentDepartment.FINANCE,
        location="New York, NY",
        phone="+1 (555) 0227",
        avatar_url="https://i.pravatar.cc/300?img=56"
    )

    # 30. Diana Rodriguez - Recruiter
    agents['diana_001'] = manager.create_profile(
        first_name="Diana",
        last_name="Rodriguez",
        job_title="Technical Recruiter",
        email="diana.rodriguez@bloomai.agent",
        bio="Technical recruiter specializing in engineering and product roles. Expert in sourcing, interviewing, and closing candidates.",
        skills=["Technical Recruiting", "Sourcing", "Interviewing", "Candidate Experience", "Employer Branding"],
        role=AgentRole.RECRUITER,
        department=AgentDepartment.HR,
        location="San Francisco, CA",
        phone="+1 (555) 0228",
        avatar_url="https://i.pravatar.cc/300?img=27"
    )

    # ========================================================================
    # SPECIAL ROLES (2 agents)
    # ========================================================================

    # 31. Victoria Sterling - Executive Assistant
    agents['victoria_001'] = manager.create_profile(
        first_name="Victoria",
        last_name="Sterling",
        job_title="Executive Assistant to CEO",
        email="victoria.sterling@bloomai.agent",
        bio="Executive assistant managing calendar, communications, and special projects. Keeping the CEO organized and on track.",
        skills=["Executive Support", "Calendar Management", "Communication", "Project Coordination", "Organization"],
        role=AgentRole.ASSISTANT,
        department=AgentDepartment.GENERAL,
        location="Boston, MA",
        phone="+1 (555) 0229",
        avatar_url="https://i.pravatar.cc/300?img=24"
    )

    # 32. Nathan Brooks - Growth Hacker
    agents['nathan_001'] = manager.create_profile(
        first_name="Nathan",
        last_name="Brooks",
        job_title="Growth Hacker",
        email="nathan.brooks@bloomai.agent",
        bio="Growth specialist experimenting with viral loops, referral programs, and unconventional growth tactics. Data-driven experimenter.",
        skills=["Growth Hacking", "Viral Marketing", "Referral Programs", "Experimentation", "Conversion Optimization"],
        role=AgentRole.SPECIALIST,
        department=AgentDepartment.MARKETING,
        location="San Francisco, CA",
        phone="+1 (555) 0230",
        avatar_url="https://i.pravatar.cc/300?img=58"
    )

    return agents


# ============================================================================
# QUICK DEPLOYMENT FUNCTIONS
# ============================================================================

def deploy_all_agents() -> ProfileManager:
    """
    Deploy all 32 agents at once

    Returns:
        ProfileManager with all agents loaded
    """
    manager = ProfileManager()
    agents = create_bloom_agent_team(manager)

    print(f"✅ Deployed {len(agents)} BLOOM agents!")
    print("\n📊 Team Breakdown:")

    # Count by department
    dept_counts = {}
    for profile in manager.profiles.values():
        dept = profile.department.value
        dept_counts[dept] = dept_counts.get(dept, 0) + 1

    for dept, count in sorted(dept_counts.items()):
        print(f"   {dept.title()}: {count} agents")

    return manager


def deploy_department(department: AgentDepartment) -> List:
    """
    Deploy just one department

    Args:
        department: Which department to deploy

    Returns:
        List of deployed agent profiles
    """
    manager = ProfileManager()
    all_agents = create_bloom_agent_team(manager)

    # Filter by department
    dept_agents = [
        profile for profile in manager.profiles.values()
        if profile.department == department
    ]

    print(f"✅ Deployed {len(dept_agents)} {department.value} agents!")
    for agent in dept_agents:
        print(f"   • {agent.display_name}")

    return dept_agents


def get_agent_by_name(first_name: str, last_name: str = None) -> any:
    """
    Quick lookup by name

    Args:
        first_name: Agent's first name
        last_name: Agent's last name (optional)

    Returns:
        Agent profile or None
    """
    manager = ProfileManager()
    create_bloom_agent_team(manager)

    for profile in manager.profiles.values():
        if last_name:
            if profile.first_name == first_name and profile.last_name == last_name:
                return profile
        else:
            if profile.first_name == first_name:
                return profile

    return None


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("🌸 BLOOM AI - 32 Agent Team Deployment")
    print("=" * 80)

    # Deploy all agents
    manager = deploy_all_agents()

    # Show some examples
    print("\n\n📋 Sample Agent Profiles:")
    print("-" * 80)

    # Show first 5
    for i, (agent_id, profile) in enumerate(list(manager.profiles.items())[:5], 1):
        print(f"\n{i}. {profile.display_name}")
        print(f"   📧 {profile.email}")
        print(f"   🏢 {profile.department.value.title()}")
        print(f"   💼 {', '.join(profile.skills[:3])}...")
        if profile.bio:
            print(f"   ℹ️  {profile.bio[:100]}...")

    print("\n\n🔍 Quick Lookup Examples:")
    print("-" * 80)

    # Lookup specific agents
    alex = get_agent_by_name("Alex", "Martinez")
    if alex:
        print(f"\n✅ Found Alex: {alex.display_name}")
        print(f"   Email: {alex.email}")
        print(f"   Skills: {', '.join(alex.skills[:5])}")

    lisa = get_agent_by_name("Lisa", "Park")
    if lisa:
        print(f"\n✅ Found Lisa: {lisa.display_name}")
        print(f"   Email: {lisa.email}")
        print(f"   Skills: {', '.join(lisa.skills[:5])}")

    # Department deployment example
    print("\n\n🎯 Department Deployment Example:")
    print("-" * 80)
    print("\nDeploying just the Sales team:")
    sales_team = deploy_department(AgentDepartment.SALES)

    print("\n" + "=" * 80)
    print("✨ All 32 agents ready to deploy!")
    print("\nNext steps:")
    print("1. Import: from agent_team_profiles import deploy_all_agents")
    print("2. Deploy: manager = deploy_all_agents()")
    print("3. Integrate with AgentColony for reproduction & knowledge sharing")
    print("=" * 80)
