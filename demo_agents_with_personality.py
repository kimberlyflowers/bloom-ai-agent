"""
🌸 BLOOM AI Agent - Agents with Personality Demo

This demo shows how BLOOM agents now have:
- Real names and job titles
- Professional email addresses
- Their own email inboxes
- Performance tracking
- Team assignments

Every agent is now a "digital employee" with their own identity!
"""

import sys
sys.path.insert(0, 'src')

from agent_profiles import (
    ProfileManager, AgentRole, AgentDepartment, AgentStatus,
    generate_agent_email
)
from email_integration import EmailManager, EmailPriority, EmailCategory
from datetime import datetime


def main():
    print("=" * 80)
    print(" " * 20 + "🌸 BLOOM AI AGENT - AGENT PERSONALITY DEMO")
    print("=" * 80)

    # Initialize systems
    profile_manager = ProfileManager()
    email_manager = EmailManager()

    print("\n\n📋 STEP 1: Creating Your AI Team")
    print("-" * 80)
    print("Let's create a team of 5 AI agents, each with their own personality...\n")

    # Create Sarah - Sales Rep
    sarah = profile_manager.create_profile(
        first_name="Sarah",
        last_name="Thompson",
        job_title="Senior Sales Representative",
        email=generate_agent_email("Sarah", "Thompson", "yourcompany.ai"),
        bio="10+ years in B2B SaaS sales. Specializes in enterprise accounts and consultative selling.",
        skills=["Enterprise Sales", "Lead Qualification", "Negotiation", "CRM", "Cold Outreach"],
        role=AgentRole.SALES_REP,
        department=AgentDepartment.SALES,
        location="San Francisco, CA",
        phone="+1 (555) 0101"
    )

    # Create inbox for Sarah
    sarah_inbox = email_manager.create_inbox(sarah.agent_id, sarah.email)

    print(f"✅ {sarah.display_name}")
    print(f"   📧 Email: {sarah.email}")
    print(f"   📞 Phone: {sarah.phone}")
    print(f"   💼 {', '.join(sarah.skills[:3])}")
    print(f"   ℹ️  {sarah.bio[:60]}...")
    print()

    # Create Mike - Support Specialist
    mike = profile_manager.create_profile(
        first_name="Mike",
        last_name="Rodriguez",
        job_title="Customer Support Specialist",
        email=generate_agent_email("Mike", "Rodriguez", "yourcompany.ai"),
        bio="Passionate about customer success. Expert at solving technical issues quickly.",
        skills=["Customer Support", "Technical Troubleshooting", "Communication", "Empathy"],
        role=AgentRole.CUSTOMER_SUPPORT,
        department=AgentDepartment.SUPPORT,
        location="Austin, TX",
        phone="+1 (555) 0102"
    )

    mike_inbox = email_manager.create_inbox(mike.agent_id, mike.email)

    print(f"✅ {mike.display_name}")
    print(f"   📧 Email: {mike.email}")
    print(f"   💼 {', '.join(mike.skills[:3])}")
    print()

    # Create Emma - Marketing Specialist
    emma = profile_manager.create_profile(
        first_name="Emma",
        last_name="Chen",
        job_title="Marketing Automation Specialist",
        email=generate_agent_email("Emma", "Chen", "yourcompany.ai"),
        bio="Data-driven marketer focused on growth hacking and conversion optimization.",
        skills=["Email Marketing", "SEO", "Analytics", "A/B Testing", "Content Strategy"],
        role=AgentRole.MARKETING_SPECIALIST,
        department=AgentDepartment.MARKETING,
        location="New York, NY",
        phone="+1 (555) 0103"
    )

    emma_inbox = email_manager.create_inbox(emma.agent_id, emma.email)

    print(f"✅ {emma.display_name}")
    print(f"   📧 Email: {emma.email}")
    print(f"   💼 {', '.join(emma.skills[:3])}")
    print()

    # Create Alex - Lead Qualifier
    alex = profile_manager.create_profile(
        first_name="Alex",
        last_name="Johnson",
        job_title="Lead Qualification Specialist",
        email=generate_agent_email("Alex", "Johnson", "yourcompany.ai"),
        bio="Expert at identifying high-quality leads and routing them to sales.",
        skills=["Lead Qualification", "Research", "Communication", "Data Analysis"],
        role=AgentRole.LEAD_QUALIFIER,
        department=AgentDepartment.SALES,
        location="Boston, MA",
        phone="+1 (555) 0104"
    )

    alex_inbox = email_manager.create_inbox(alex.agent_id, alex.email)

    print(f"✅ {alex.display_name}")
    print(f"   📧 Email: {alex.email}")
    print(f"   💼 {', '.join(alex.skills[:3])}")
    print()

    # Create Jordan - Account Manager
    jordan = profile_manager.create_profile(
        first_name="Jordan",
        last_name="Williams",
        job_title="Account Manager",
        email=generate_agent_email("Jordan", "Williams", "yourcompany.ai"),
        bio="Builds long-term relationships with customers. Focuses on retention and upsells.",
        skills=["Account Management", "Relationship Building", "Upselling", "Strategy"],
        role=AgentRole.ACCOUNT_MANAGER,
        department=AgentDepartment.SALES,
        location="Chicago, IL",
        phone="+1 (555) 0105"
    )

    jordan_inbox = email_manager.create_inbox(jordan.agent_id, jordan.email)

    print(f"✅ {jordan.display_name}")
    print(f"   📧 Email: {jordan.email}")
    print(f"   💼 {', '.join(jordan.skills[:3])}")

    # Summary
    stats = profile_manager.get_stats()
    print(f"\n📊 Team Created: {stats['total_agents']} agents across {len(set(p.department for p in profile_manager.profiles.values()))} departments")

    # ========================================================================
    # STEP 2: Simulate Real Work Day
    # ========================================================================

    print("\n\n" + "=" * 80)
    print("📨 STEP 2: Simulating a Real Work Day")
    print("-" * 80)
    print("Let's see how these agents handle incoming emails...\n")

    # Sarah receives a hot lead
    print("🔔 Sarah receives an urgent email from a potential customer...")
    email1 = email_manager.receive_email(
        to_email=sarah.email,
        from_email="ceo@bigtechcorp.com",
        from_name="Jennifer Martinez - CEO",
        subject="URGENT: Need pricing for 500 seats ASAP",
        body="""Hi Sarah,

We're looking to purchase your solution for our entire company (500 employees).
We need pricing and a demo THIS WEEK as we're making our final decision.

This is a high priority project for us. Can you help?

Best,
Jennifer Martinez
CEO, BigTech Corp
"""
    )

    print(f"✅ Email received!")
    print(f"   From: {email1.from_address}")
    print(f"   Subject: {email1.subject}")
    print(f"   Priority: {email1.priority.value.upper()} ⚠️")
    print(f"   Category: {email1.category.value}")
    print(f"   Auto-detected as: {'NEEDS URGENT RESPONSE' if email1.needs_urgent_response else 'Normal'}")

    # Sarah updates her status and responds
    print(f"\n💼 Sarah sees the urgent email and takes action...")
    sarah.update_status(AgentStatus.BUSY, "Responding to enterprise lead")
    email1.mark_read()

    reply1 = email_manager.send_email(
        from_agent_id=sarah.agent_id,
        to_email="ceo@bigtechcorp.com",
        to_name="Jennifer Martinez",
        subject="Re: URGENT: Need pricing for 500 seats ASAP",
        body="""Hi Jennifer,

Thank you for reaching out! I'm excited to help with your evaluation.

For 500 seats, I can offer you:
- Enterprise Plan: $15/user/month = $7,500/month ($90K/year)
- Includes: Priority support, custom integrations, dedicated success manager
- Special offer: 20% discount if signed this week = $72K/year

I have availability for a demo tomorrow at 10am or 2pm PST. Which works better for your team?

Looking forward to working with you!

Best regards,
Sarah Thompson
Senior Sales Representative
Phone: +1 (555) 0101
Email: sarah.thompson@yourcompany.ai
""",
        in_reply_to=email1.email_id
    )

    sarah.update_performance(action_success=True, revenue=90000, cost=50)
    print(f"✅ Sarah responded within seconds!")
    print(f"   Status: {email1.status.value} ✓")
    print(f"   Potential deal value: $90,000/year")

    # Mike receives support request
    print(f"\n\n🔔 Mike receives a support request...")
    email2 = email_manager.receive_email(
        to_email=mike.email,
        from_email="frustrated.user@customer.com",
        from_name="Tom Johnson",
        subject="Product broken - can't login!",
        body="""Hey Mike,

I can't login to the platform. Keep getting error 500. This is really frustrating
as I have a deadline today. Please help ASAP!

Tom
"""
    )

    print(f"✅ Email received!")
    print(f"   From: {email2.from_address}")
    print(f"   Category: {email2.category.value}")
    print(f"   Sentiment: {email2.sentiment.value}")

    # Mike responds quickly
    print(f"\n💼 Mike jumps on the issue immediately...")
    mike.update_status(AgentStatus.BUSY, "Helping customer with login issue")
    email2.mark_read()

    reply2 = email_manager.send_email(
        from_agent_id=mike.agent_id,
        to_email="frustrated.user@customer.com",
        to_name="Tom Johnson",
        subject="Re: Product broken - can't login!",
        body="""Hi Tom,

I'm sorry to hear you're having trouble logging in. Let me help you right away!

I just checked our systems and found the issue - there was a temporary server issue
that's now resolved. Please try logging in again now.

If you still have any problems, reply to this email or call me directly at
+1 (555) 0102 and I'll get you sorted immediately.

Thanks for your patience!

Best,
Mike Rodriguez
Customer Support Specialist
""",
        in_reply_to=email2.email_id
    )

    mike.update_performance(action_success=True, cost=10)
    print(f"✅ Mike resolved the issue!")
    print(f"   Response time: < 5 minutes")

    # Emma receives marketing inquiry
    print(f"\n\n🔔 Emma receives a partnership inquiry...")
    email3 = email_manager.receive_email(
        to_email=emma.email,
        from_email="marketing@partner.com",
        from_name="Lisa Chang",
        subject="Interested in co-marketing partnership",
        body="""Hi Emma,

We love what you're doing at BLOOM AI! We'd like to explore a co-marketing
partnership. Our audiences seem very aligned.

Would you be open to a quick call next week?

Best,
Lisa Chang
Head of Marketing
Partner Corp
"""
    )

    print(f"✅ Email received!")
    print(f"   From: {email3.from_address}")
    print(f"   Category: {email3.category.value}")

    emma.update_performance(action_success=True, revenue=5000, cost=20)
    emma.update_status(AgentStatus.ACTIVE, "Evaluating partnership opportunity")

    # ========================================================================
    # STEP 3: Show Team Performance
    # ========================================================================

    print("\n\n" + "=" * 80)
    print("📊 STEP 3: Team Performance Dashboard")
    print("-" * 80)
    print()

    # Show each agent's status
    print("👥 AGENT STATUS:\n")
    for profile in profile_manager.profiles.values():
        status_emoji = {
            AgentStatus.ACTIVE: "🟢",
            AgentStatus.BUSY: "🔵",
            AgentStatus.IDLE: "⚪",
            AgentStatus.OFFLINE: "⚫"
        }.get(profile.status, "⚪")

        print(f"{status_emoji} {profile.full_name} ({profile.job_title})")
        print(f"   Status: {profile.status.value} - {profile.status_message}")
        if profile.total_actions > 0:
            print(f"   Actions: {profile.total_actions} | Success Rate: {profile.success_rate:.1f}%")
            if profile.total_revenue_generated > 0:
                print(f"   Revenue: ${profile.total_revenue_generated:,.0f} | ROI: {profile.current_roi:.1f}x")
        print()

    # Show email statistics
    print("\n📧 EMAIL STATISTICS:\n")
    email_stats = email_manager.get_stats()
    print(f"Total Inboxes: {email_stats['total_inboxes']}")
    print(f"Total Emails: {email_stats['total_emails']}")
    print(f"Unread: {email_stats['total_unread']}")
    print(f"Urgent: {email_stats['total_urgent']}")

    # Show top performers
    print("\n\n🏆 TOP PERFORMERS:\n")
    top_performers = profile_manager.get_top_performers(limit=3, metric="revenue")
    for i, profile in enumerate(top_performers, 1):
        if profile.total_revenue_generated > 0:
            print(f"{i}. {profile.full_name}")
            print(f"   Revenue Generated: ${profile.total_revenue_generated:,.0f}")
            print(f"   ROI: {profile.current_roi:.1f}x")
            print(f"   Success Rate: {profile.success_rate:.1f}%")
            print()

    # Show team statistics
    print("\n📈 OVERALL TEAM STATS:\n")
    team_stats = profile_manager.get_stats()
    print(f"Total Agents: {team_stats['total_agents']}")
    print(f"Active Agents: {team_stats['active_agents']}")
    print(f"Total Revenue Generated: ${team_stats['total_revenue']:,.0f}")
    print(f"Total Cost: ${team_stats['total_cost']:,.0f}")
    print(f"Team Average ROI: {team_stats['average_roi']:.2f}x")

    # Show department breakdown
    print(f"\n📊 AGENTS BY DEPARTMENT:\n")
    for dept, count in team_stats['departments'].items():
        if count > 0:
            print(f"   {dept.title()}: {count}")

    print("\n\n" + "=" * 80)
    print("✨ YOUR AI AGENTS NOW HAVE REAL PERSONALITIES!")
    print("=" * 80)
    print("\n🎉 Key Features:")
    print("   ✅ Each agent has a name, job title, and email address")
    print("   ✅ Agents can send and receive emails in real-time")
    print("   ✅ Emails are automatically categorized and prioritized")
    print("   ✅ Agents track their own performance (ROI, success rate)")
    print("   ✅ Full team management and statistics")
    print("   ✅ Professional profiles with skills and bios")
    print("\n💡 This makes AI agents feel like real digital employees!")
    print("=" * 80)


if __name__ == "__main__":
    main()
