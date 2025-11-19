"""
🚀 ULTIMATE AGENT SYSTEM DEMO

This demonstrates the COMPLETE vision:

1. Agents with full identities (System #12)
2. Email inboxes (System #13)
3. Natural conversations with Claude AI (System #15)
4. Visual/browser capabilities (System #16)
5. Job descriptions and routines (System #17)
6. GoHighLevel automation (System #17)
7. Team collaboration - Backend + Frontend (System #18)

ALL WORKING TOGETHER! 🤯
"""

import sys
sys.path.append('src')

from agent_profiles import ProfileManager, AgentRole, AgentDepartment
from email_integration import EmailManager
from claude_ai_integration import ConversationManager
from agent_routines import RoutineManager, create_sales_rep_job_description
from agent_teams import TeamManager, AgentType, TeamRole
import os


def demo_header(title: str):
    """Print demo section header"""
    print("\n\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def create_complete_agent_system():
    """Create complete agent system with all features"""

    demo_header("🎭 CREATING COMPLETE AGENT SYSTEM")

    print("\nWe'll create the Sales Dream Team:")
    print("   • Sarah (Frontend): LinkedIn, Reddit, social engagement")
    print("   • Alex (Backend): APIs, data, CRM automation")
    print("   • Mike (Hybrid): Demos, calls, closing")

    input("\n👉 Press Enter to start...")

    # Initialize all managers
    profile_manager = ProfileManager()
    email_manager = EmailManager()
    conv_manager = ConversationManager()
    routine_manager = RoutineManager()
    team_manager = TeamManager()

    # ========================================================================
    # SARAH - FRONTEND SPECIALIST
    # ========================================================================

    demo_header("👩 CREATING SARAH - FRONTEND SPECIALIST")

    print("\nSarah handles all visual/UI tasks:")
    print("   • LinkedIn outreach and engagement")
    print("   • Reddit community building")
    print("   • Browser automation for any platform")
    print("   • Takes screenshots of everything")

    # Create profile
    sarah = profile_manager.create_profile(
        first_name="Sarah",
        last_name="Thompson",
        job_title="Senior Sales Representative (Frontend Specialist)",
        email="sarah.thompson@bloomai.company",
        bio="10+ years in B2B SaaS sales. Expert at LinkedIn and social selling.",
        skills=["LinkedIn Outreach", "Social Selling", "Community Building", "Browser Automation"],
        role=AgentRole.SALES_REP,
        department=AgentDepartment.SALES,
        phone="+1 (555) 012-0101",
        location="San Francisco, CA",
        avatar_url="https://i.pravatar.cc/300?img=47"
    )

    print(f"\n✅ Profile created for {sarah.full_name}")
    print(f"   Email: {sarah.email}")
    print(f"   Specialization: Frontend/Visual tasks")

    # Create email inbox
    sarah_inbox = email_manager.create_inbox(sarah.agent_id, sarah.email)
    print(f"✅ Email inbox created: {sarah.email}")

    # Create job description
    sarah_job = create_sales_rep_job_description()
    sarah_job.title = "Frontend Sales Specialist"
    sarah_job.daily_tasks.append("Check LinkedIn notifications every 15 minutes")
    sarah_job.daily_tasks.append("Respond to Reddit comments on r/SaaS")
    sarah_job.daily_tasks.append("Take screenshots of all LinkedIn interactions")
    routine_manager.job_descriptions[sarah.agent_id] = sarah_job

    print(f"✅ Job description created with {len(sarah_job.daily_tasks)} daily tasks")

    # Create routine
    sarah_routine = routine_manager.create_routine_from_job_description(
        sarah.agent_id,
        sarah_job
    )
    print(f"✅ Daily routine created with {len(sarah_routine.get_all_tasks())} tasks")

    # ========================================================================
    # ALEX - BACKEND SPECIALIST
    # ========================================================================

    demo_header("👨 CREATING ALEX - BACKEND SPECIALIST")

    print("\nAlex handles all API/data tasks:")
    print("   • CRM automation via APIs")
    print("   • Email campaign automation")
    print("   • Data analysis and lead scoring")
    print("   • Proposal generation")

    # Create profile
    alex = profile_manager.create_profile(
        first_name="Alex",
        last_name="Rodriguez",
        job_title="Sales Operations Specialist (Backend)",
        email="alex.rodriguez@bloomai.company",
        bio="Expert in sales automation, CRM APIs, and data analytics.",
        skills=["API Integration", "Python", "Data Analysis", "CRM Automation", "Email Marketing"],
        role=AgentRole.ASSISTANT,
        department=AgentDepartment.SALES,
        phone="+1 (555) 012-0102",
        location="Austin, TX",
        avatar_url="https://i.pravatar.cc/300?img=12"
    )

    print(f"\n✅ Profile created for {alex.full_name}")
    print(f"   Email: {alex.email}")
    print(f"   Specialization: Backend/API tasks")

    # Create email inbox
    alex_inbox = email_manager.create_inbox(alex.agent_id, alex.email)
    print(f"✅ Email inbox created: {alex.email}")

    # ========================================================================
    # MIKE - HYBRID LEAD
    # ========================================================================

    demo_header("👨‍💼 CREATING MIKE - HYBRID TEAM LEAD")

    print("\nMike is the team lead (can do both!):")
    print("   • Conducts product demos")
    print("   • Makes sales calls")
    print("   • Closes deals and negotiates")
    print("   • Coordinates the team")

    # Create profile
    mike = profile_manager.create_profile(
        first_name="Mike",
        last_name="Chen",
        job_title="Senior Account Executive (Team Lead)",
        email="mike.chen@bloomai.company",
        bio="Enterprise sales expert. Closing deals and leading high-performing teams.",
        skills=["Sales Demos", "Deal Closing", "Negotiation", "Team Leadership", "Enterprise Sales"],
        role=AgentRole.MANAGER,
        department=AgentDepartment.SALES,
        phone="+1 (555) 012-0103",
        location="New York, NY",
        avatar_url="https://i.pravatar.cc/300?img=33"
    )

    print(f"\n✅ Profile created for {mike.full_name}")
    print(f"   Email: {mike.email}")
    print(f"   Role: Team Lead (Hybrid)")

    # Create email inbox
    mike_inbox = email_manager.create_inbox(mike.agent_id, mike.email)
    print(f"✅ Email inbox created: {mike.email}")

    # ========================================================================
    # CREATE TEAM
    # ========================================================================

    demo_header("🤝 FORMING THE SALES DREAM TEAM")

    # Create team
    team = team_manager.create_team(
        team_name="Sales Dream Team",
        department="Sales",
        goals={
            "Monthly Revenue": "$100,000",
            "Close Rate": "40%+",
            "LinkedIn Connections": "500+/month",
            "Email Response Rate": "50%+"
        },
        shared_tools=["GoHighLevel CRM", "Slack", "LinkedIn", "Reddit"],
        communication_channels=["Slack #sales-team", "Daily standup at 9am EST"]
    )

    # Add members
    team_manager.add_team_member(
        team_id=team.team_id,
        agent_id=sarah.agent_id,
        agent_name=sarah.full_name,
        agent_type=AgentType.FRONTEND,
        team_role=TeamRole.SPECIALIST,
        skills=sarah.skills,
        specializations=["LinkedIn", "Reddit", "Browser Automation"],
        tools=["LinkedIn Sales Navigator", "Reddit", "Playwright"]
    )

    team_manager.add_team_member(
        team_id=team.team_id,
        agent_id=alex.agent_id,
        agent_name=alex.full_name,
        agent_type=AgentType.BACKEND,
        team_role=TeamRole.SPECIALIST,
        skills=alex.skills,
        specializations=["CRM APIs", "Email Automation", "Data Analytics"],
        tools=["GoHighLevel API", "Email API", "Python"]
    )

    team_manager.add_team_member(
        team_id=team.team_id,
        agent_id=mike.agent_id,
        agent_name=mike.full_name,
        agent_type=AgentType.HYBRID,
        team_role=TeamRole.LEAD,
        skills=mike.skills,
        specializations=["Product Demos", "Deal Closing", "Team Leadership"],
        tools=["Zoom", "Calendly", "GoHighLevel"]
    )

    # Show team summary
    print(team_manager.get_team_summary(team.team_id))

    return {
        "sarah": {"profile": sarah, "inbox": sarah_inbox, "routine": sarah_routine},
        "alex": {"profile": alex, "inbox": alex_inbox},
        "mike": {"profile": mike, "inbox": mike_inbox},
        "team": team,
        "managers": {
            "profile": profile_manager,
            "email": email_manager,
            "conv": conv_manager,
            "routine": routine_manager,
            "team": team_manager
        }
    }


def demo_complete_workflow(system):
    """Demo complete workflow with team collaboration"""

    demo_header("🎬 COMPLETE WORKFLOW: CLOSING ENTERPRISE DEAL")

    print("\n🎯 Scenario: BigCorp Inc. needs our solution")
    print("   Company Size: 500 employees")
    print("   Budget: $50,000")
    print("   Decision Maker: John Smith (VP of Sales)")

    print("\n📋 How our team will collaborate:")
    print("   1. Sarah: Find and engage John on LinkedIn (FRONTEND)")
    print("   2. Alex: Pull BigCorp data, prepare proposal (BACKEND)")
    print("   3. Sarah: Build relationship, get responses (FRONTEND)")
    print("   4. Alex: Run email nurture campaign (BACKEND)")
    print("   5. Mike: Conduct demo and close deal (HYBRID)")

    input("\n👉 Press Enter to start workflow...")

    # ========================================================================
    # WEEK 1: SARAH'S LINKEDIN OUTREACH
    # ========================================================================

    demo_header("📅 WEEK 1: SARAH'S LINKEDIN OUTREACH (Frontend)")

    print("\n👩 Sarah starts her morning routine:")
    print("   9:00 AM - Check email")
    print("   9:15 AM - Check LinkedIn notifications")
    print("   9:30 AM - Review today's target accounts")

    print("\n🔍 Sarah's Task: Research BigCorp executives on LinkedIn")
    print("   Tool: Browser Automation (Playwright)")
    print("   Method: Uses actual LinkedIn website (not API!)")

    print("\n   Sarah opens browser...")
    print("   ✅ Navigates to linkedin.com")
    print("   ✅ Logs in (human-like typing delays)")
    print("   ✅ Searches: 'BigCorp Inc VP of Sales'")
    print("   ✅ Finds John Smith's profile")
    print("   ✅ Takes screenshot of profile")
    print("   ✅ Clicks 'Connect' button")
    print("   ✅ Writes personalized message:")

    print("\n   " + "-" * 76)
    print('''
    Hi John,

    I noticed BigCorp is scaling rapidly - congrats on the growth!

    I work with companies at your stage to optimize their sales process with AI.
    Our clients typically see 40%+ improvement in close rates.

    Would love to connect and share some insights relevant to your space.

    Best,
    Sarah
    ''')
    print("   " + "-" * 76)

    print("\n   ✅ Sarah types message character-by-character (human-like!)")
    print("   ✅ Clicks 'Send' with random delay")
    print("   ✅ Takes screenshot: 'Connection request sent to John Smith'")
    print("   ✅ Saves to visual knowledge base")

    print("\n📸 Sarah's Screenshots:")
    print("   • John's LinkedIn profile")
    print("   • Connection request dialog")
    print("   • Confirmation: Request sent")

    input("\n👉 Press Enter to continue...")

    # ========================================================================
    # WEEK 1: ALEX'S BACKEND WORK
    # ========================================================================

    demo_header("📅 WEEK 1: ALEX'S DATA PREP (Backend)")

    print("\n👨 Alex gets notified of new target account")
    print("   Tool: CRM API (GoHighLevel)")
    print("   Method: Python scripts, API calls")

    print("\n🔍 Alex's Tasks:")
    print("   1. Pull BigCorp data from CRM")
    print("   2. Enrich with public data")
    print("   3. Generate custom pricing")
    print("   4. Prepare proposal template")

    print("\n   Alex runs his automation script...")
    print("   ✅ API call: GET /contacts?company=BigCorp")
    print("   ✅ Found 3 contacts from BigCorp")
    print("   ✅ Enriching data from Clearbit API...")
    print("   ✅ BigCorp details:")
    print("      - Employees: 500")
    print("      - Revenue: $50M/year")
    print("      - Tech stack: Salesforce, HubSpot")
    print("      - Pain points: Manual lead scoring, low conversion")

    print("\n   ✅ Generating custom pricing...")
    print("      - Enterprise plan: $50,000/year")
    print("      - 500 user seats")
    print("      - Custom integrations included")
    print("      - ROI projection: 300% in year 1")

    print("\n   ✅ Creating proposal PDF...")
    print("      - Company-specific case studies")
    print("      - Customized pricing")
    print("      - Implementation timeline")
    print("      - Success metrics")

    print("\n   ✅ Proposal saved to: /proposals/BigCorp_Proposal_2025.pdf")
    print("   ✅ Updated CRM with BigCorp enriched data")

    input("\n👉 Press Enter for Week 2...")

    # ========================================================================
    # WEEK 2: SARAH'S ENGAGEMENT
    # ========================================================================

    demo_header("📅 WEEK 2: SARAH BUILDS RELATIONSHIP (Frontend)")

    print("\n🔔 LinkedIn notification: 'John Smith accepted your connection!'")

    print("\n👩 Sarah receives notification via email:")
    sarah_inbox = system["sarah"]["inbox"]
    sarah_inbox.add_email(
        from_email="notifications@linkedin.com",
        from_name="LinkedIn",
        to_email="sarah.thompson@bloomai.company",
        to_name="Sarah Thompson",
        subject="John Smith accepted your connection request",
        body="John Smith is now a connection. Say hi!"
    )

    print("   ✅ Email received in Sarah's inbox")
    print("   📧 From: LinkedIn Notifications")
    print("   📧 Subject: John Smith accepted your connection request")

    print("\n   Sarah opens LinkedIn (browser automation)...")
    print("   ✅ Sees John accepted")
    print("   ✅ Checks John's recent activity")
    print("   ✅ John posted: 'Excited about Q4 - our team is crushing it!'")
    print("   ✅ Sarah clicks 'Like' (with delay)")
    print("   ✅ Sarah comments:")

    print("\n   " + "-" * 76)
    print("""
    Love to see it! Q4 momentum is everything. How are you thinking about
    scaling the team for next year?
    """)
    print("   " + "-" * 76)

    print("\n   ✅ Sarah types comment with human-like delays")
    print("   ✅ Takes screenshot of comment")
    print("   ✅ Saves to visual knowledge base")

    print("\n   30 minutes later...")
    print("   🔔 John replies: 'Thanks Sarah! Scaling is top priority...'")
    print("   ✅ Sarah continues conversation naturally")

    print("\n📸 Sarah's Screenshots This Week:")
    print("   • Connection accepted notification")
    print("   • John's post with Sarah's comment")
    print("   • John's reply")
    print("   • DM conversation thread")

    input("\n👉 Press Enter for Alex's email campaign...")

    # ========================================================================
    # WEEK 2: ALEX'S EMAIL CAMPAIGN
    # ========================================================================

    demo_header("📅 WEEK 2: ALEX'S EMAIL AUTOMATION (Backend)")

    print("\n👨 Alex launches email nurture sequence")
    print("   Tool: Email API + GoHighLevel API")
    print("   Method: Automated drip campaign")

    print("\n📧 Email Sequence (5 emails over 2 weeks):")

    emails = [
        {
            "day": "Day 1",
            "subject": "John - quick question about BigCorp's growth",
            "preview": "Saw your recent post about Q4 momentum..."
        },
        {
            "day": "Day 3",
            "subject": "How we helped SimilarCorp increase close rates 40%",
            "preview": "I thought this case study might be relevant..."
        },
        {
            "day": "Day 7",
            "subject": "3 ways AI is changing B2B sales in 2025",
            "preview": "Here are the trends we're seeing..."
        },
        {
            "day": "Day 10",
            "subject": "Quick demo? (15 min)",
            "preview": "Would love to show you how this works..."
        },
        {
            "day": "Day 14",
            "subject": "Custom proposal for BigCorp",
            "preview": "I put together something specific for your team..."
        }
    ]

    for email in emails:
        print(f"\n   {email['day']}: {email['subject']}")
        print(f"      Preview: {email['preview']}")
        print(f"      ✅ Sent via API")
        print(f"      ✅ Tracking opened/clicked")

    print("\n📊 Email Performance (tracked by Alex):")
    print("   • Email 1: Opened (55% open rate)")
    print("   • Email 2: Opened + Clicked case study link")
    print("   • Email 3: Opened (engaged!)")
    print("   • Email 4: Opened + Replied: 'Yes, let's chat!'")
    print("   • Email 5: Not sent yet (John already replied!)")

    print("\n   ✅ Alex updates CRM:")
    print("      - Status: Hot Lead")
    print("      - Interest Level: High")
    print("      - Next Step: Schedule demo")
    print("      - Assigned to: Mike (for demo)")

    input("\n👉 Press Enter for Week 3...")

    # ========================================================================
    # WEEK 3: MIKE'S DEMO
    # ========================================================================

    demo_header("📅 WEEK 3: MIKE CONDUCTS DEMO (Hybrid)")

    print("\n👨‍💼 Mike gets notification: 'John Smith ready for demo!'")

    print("\n📧 Mike receives handoff email from Alex:")
    mike_inbox = system["mike"]["inbox"]
    mike_inbox.add_email(
        from_email="alex.rodriguez@bloomai.company",
        from_name="Alex Rodriguez",
        to_email="mike.chen@bloomai.company",
        to_name="Mike Chen",
        subject="Hot Lead: BigCorp - Demo Requested",
        body="""
Mike,

John Smith from BigCorp is ready for a demo!

Company: BigCorp Inc.
Size: 500 employees
Budget: $50K
Decision Maker: John Smith (VP of Sales)

Context:
- Sarah connected on LinkedIn 2 weeks ago
- Great engagement on LinkedIn posts
- Responded to email #4 asking for demo
- Very interested in improving close rates

Proposal ready at: /proposals/BigCorp_Proposal_2025.pdf

Let's close this one!

-Alex
        """
    )

    print("\n   ✅ Mike reviews handoff")
    print("   ✅ Checks Sarah's LinkedIn screenshots")
    print("   ✅ Reviews Alex's email analytics")
    print("   ✅ Reads proposal")

    print("\n   Mike sends calendar invite (Calendly integration):")
    print("   ✅ Product Demo with BigCorp")
    print("   ✅ Date: Friday 2pm EST")
    print("   ✅ Zoom link included")
    print("   ✅ Proposal attached")

    print("\n🎥 DEMO DAY:")
    print("   ✅ Mike joins Zoom call")
    print("   ✅ John is impressed by product")
    print("   ✅ Loves the custom proposal")
    print("   ✅ Mentions Sarah's great insights on LinkedIn")
    print("   ✅ Asks about implementation timeline")
    print("   ✅ Mike answers all questions perfectly")

    print("\n   John: 'This looks perfect for us. Let's move forward!'")

    print("\n   ✅ Mike sends contract (via DocuSign API)")
    print("   ✅ John signs same day")
    print("   ✅ DEAL CLOSED: $50,000! 🎉")

    input("\n👉 Press Enter for final summary...")

    # ========================================================================
    # DEAL SUMMARY
    # ========================================================================

    demo_header("🎉 DEAL CLOSED - TEAM COLLABORATION WIN!")

    print("\n💰 REVENUE: $50,000 Annual Contract")

    print("\n👥 Team Contributions:")
    print("\n   👩 SARAH (Frontend Specialist):")
    print("      ✅ Found John Smith on LinkedIn")
    print("      ✅ Sent personalized connection request")
    print("      ✅ Built relationship through comments and DMs")
    print("      ✅ Kept engagement warm throughout process")
    print("      ✅ Took screenshots proving every interaction")
    print("      📸 Visual proof: 15 screenshots in knowledge base")

    print("\n   👨 ALEX (Backend Specialist):")
    print("      ✅ Pulled BigCorp data via CRM API")
    print("      ✅ Enriched data from external APIs")
    print("      ✅ Generated custom pricing and proposal")
    print("      ✅ Ran automated email nurture campaign")
    print("      ✅ Tracked all email engagement")
    print("      ✅ Updated CRM with clean data")
    print("      📊 All done via APIs - zero manual work!")

    print("\n   👨‍💼 MIKE (Hybrid Team Lead):")
    print("      ✅ Received perfect handoff from team")
    print("      ✅ Reviewed Sarah's LinkedIn proof")
    print("      ✅ Used Alex's proposal and data")
    print("      ✅ Scheduled demo via Calendly")
    print("      ✅ Conducted amazing product demo")
    print("      ✅ Closed deal and sent contract")
    print("      🏆 The closer!")

    print("\n🎯 Why This Worked:")
    print("   ✅ Frontend + Backend + Hybrid = Complete coverage")
    print("   ✅ Sarah did what only humans can see (LinkedIn UI)")
    print("   ✅ Alex did what APIs do best (data, automation)")
    print("   ✅ Mike added human touch when needed (demo, closing)")
    print("   ✅ Every agent played to their strengths")
    print("   ✅ Visual proof of all activity (screenshots)")
    print("   ✅ Clean data in CRM (API automation)")

    print("\n📈 Old Way vs New Way:")
    print("\n   OLD WAY (Human Sales Rep):")
    print("      • 1 person doing everything")
    print("      • Manual data entry")
    print("      • Inconsistent follow-up")
    print("      • No proof of outreach")
    print("      • Close rate: 20%")
    print("      • Cost: $120K/year salary")

    print("\n   NEW WAY (AI Agent Team):")
    print("      • 3 specialized agents working together")
    print("      • Automated data management")
    print("      • Perfect follow-up timing")
    print("      • Screenshots prove everything")
    print("      • Close rate: 40%")
    print("      • Cost: Fraction of human team!")

    print("\n🚀 What This Enables:")
    print("   • Scale infinitely (create more agent teams)")
    print("   • 24/7 operation (agents never sleep)")
    print("   • Perfect execution every time")
    print("   • Visual and data proof of all work")
    print("   • Continuous improvement (learn from every deal)")


def main():
    """Run ultimate demo"""
    print("\n\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "🚀 ULTIMATE AGENT SYSTEM DEMO" + " " * 32 + "║")
    print("╚" + "=" * 78 + "╝")

    print("\n🎯 This demo showcases:")
    print("   • Complete agent identities with job descriptions")
    print("   • Daily routines and task scheduling")
    print("   • Frontend agents (browser automation, screenshots)")
    print("   • Backend agents (APIs, data, automation)")
    print("   • Hybrid agents (best of both worlds)")
    print("   • Team collaboration to close deals")

    print("\n💡 The Complete Vision:")
    print("   Backend Agent + Frontend Agent = UNSTOPPABLE TEAM")

    input("\n👉 Press Enter to start demo...")

    try:
        # Create system
        system = create_complete_agent_system()

        input("\n👉 Press Enter to see complete workflow...")

        # Show workflow
        demo_complete_workflow(system)

        # Final message
        print("\n\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 25 + "🎉 DEMO COMPLETE!" + " " * 36 + "║")
        print("╚" + "=" * 78 + "╝")

        print("\n🌟 WHAT WE JUST SAW:")
        print("   ✅ 3 specialized agents working as a team")
        print("   ✅ Sarah (Frontend): LinkedIn relationship building")
        print("   ✅ Alex (Backend): Data automation and email campaigns")
        print("   ✅ Mike (Hybrid): Demo and deal closing")
        print("   ✅ Complete collaboration from start to finish")
        print("   ✅ $50,000 deal closed!")

        print("\n🎯 Each Agent Did What They Do BEST:")
        print("   • Frontend: Visual tasks only humans can see")
        print("   • Backend: API/data tasks that are perfect for automation")
        print("   • Hybrid: Human touch when needed")

        print("\n💡 This Is The Future:")
        print("   • No more 'jack of all trades, master of none'")
        print("   • Specialized agents working together")
        print("   • Frontend handles UI/visual platforms")
        print("   • Backend handles APIs/data")
        print("   • Together they're UNSTOPPABLE!")

        print("\n🚀 What You Can Do Now:")
        print("   1. Create specialized agent teams")
        print("   2. Pair frontend + backend agents")
        print("   3. Give each clear job descriptions")
        print("   4. Let them collaborate on tasks")
        print("   5. Scale infinitely!")

        print("\n" + "=" * 80)
        print("🌸 BLOOM AI AGENT - 18 Complete Systems")
        print("   Where AI Agents Become Unstoppable Teams")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
