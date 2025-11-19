"""
Agent Daily Routines and Job Descriptions - System #17

Agents now have:
- Detailed job descriptions (like Indeed!)
- Daily routines and schedules
- Automated task reminders
- Frontend workflow automation
- Deep understanding of their role

Agents know EXACTLY what to do each day!
"""

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import json
from pathlib import Path
import schedule
import threading


# ============================================================================
# CONFIGURATION
# ============================================================================

ROUTINES_DIR = Path("data/agent_routines")
ROUTINES_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# JOB DESCRIPTIONS
# ============================================================================

@dataclass
class JobDescription:
    """
    Complete job description for an agent

    Like Indeed job postings - gives agents deep understanding of their role!
    """
    title: str
    department: str
    reports_to: str

    # Overview
    overview: str  # What the role is about

    # Responsibilities (detailed!)
    key_responsibilities: List[str]

    # Daily tasks
    daily_tasks: List[str]
    weekly_tasks: List[str]
    monthly_tasks: List[str]

    # Success metrics
    success_metrics: Dict[str, str]  # metric_name: target

    # Tools and systems
    tools_required: List[str]  # "GoHighLevel", "LinkedIn", "Reddit", etc.
    systems_access: List[str]  # What they need access to

    # Skills and qualifications
    required_skills: List[str]
    preferred_skills: List[str]

    # Work schedule
    work_hours: str  # "9am-5pm EST"
    timezone: str

    # Performance expectations
    response_time_email: str  # "Within 2 hours"
    response_time_social: str  # "Within 30 minutes"

    # Autonomy level
    decision_authority: str  # "Can approve deals up to $10K"
    escalation_rules: Dict[str, str]  # When to escalate

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "department": self.department,
            "reports_to": self.reports_to,
            "overview": self.overview,
            "key_responsibilities": self.key_responsibilities,
            "daily_tasks": self.daily_tasks,
            "weekly_tasks": self.weekly_tasks,
            "monthly_tasks": self.monthly_tasks,
            "success_metrics": self.success_metrics,
            "tools_required": self.tools_required,
            "systems_access": self.systems_access,
            "required_skills": self.required_skills,
            "preferred_skills": self.preferred_skills,
            "work_hours": self.work_hours,
            "timezone": self.timezone,
            "response_time_email": self.response_time_email,
            "response_time_social": self.response_time_social,
            "decision_authority": self.decision_authority,
            "escalation_rules": self.escalation_rules
        }


# ============================================================================
# DAILY ROUTINES
# ============================================================================

class TaskFrequency(Enum):
    """How often a task should run"""
    EVERY_MINUTE = "every_minute"
    EVERY_5_MINUTES = "every_5_minutes"
    EVERY_15_MINUTES = "every_15_minutes"
    EVERY_30_MINUTES = "every_30_minutes"
    HOURLY = "hourly"
    EVERY_2_HOURS = "every_2_hours"
    EVERY_4_HOURS = "every_4_hours"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class RoutineTask:
    """A task that runs on a schedule"""
    task_id: str
    task_name: str
    description: str
    frequency: TaskFrequency
    scheduled_time: Optional[time] = None  # For daily tasks: "09:00"

    # Task details
    action_type: str  # "check_email", "respond_comments", "run_campaign", etc.
    action_params: Dict[str, Any] = field(default_factory=dict)

    # Execution tracking
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    success_count: int = 0

    # Priority
    priority: int = 5  # 1-10, higher = more important

    # Dependencies
    requires_tasks: List[str] = field(default_factory=list)  # Must run after these

    enabled: bool = True


@dataclass
class DailyRoutine:
    """Complete daily routine for an agent"""
    agent_id: str
    routine_name: str

    # Morning routine (8am-12pm)
    morning_tasks: List[RoutineTask] = field(default_factory=list)

    # Afternoon routine (12pm-5pm)
    afternoon_tasks: List[RoutineTask] = field(default_factory=list)

    # Evening routine (5pm-8pm)
    evening_tasks: List[RoutineTask] = field(default_factory=list)

    # Ongoing tasks (all day)
    ongoing_tasks: List[RoutineTask] = field(default_factory=list)

    # Weekly tasks
    weekly_tasks: List[RoutineTask] = field(default_factory=list)

    # Monthly tasks
    monthly_tasks: List[RoutineTask] = field(default_factory=list)

    def get_all_tasks(self) -> List[RoutineTask]:
        """Get all tasks"""
        return (
            self.morning_tasks +
            self.afternoon_tasks +
            self.evening_tasks +
            self.ongoing_tasks +
            self.weekly_tasks +
            self.monthly_tasks
        )


# ============================================================================
# ROUTINE MANAGER
# ============================================================================

class RoutineManager:
    """
    Manages agent routines and schedules

    Agents know exactly what to do and when!
    """

    def __init__(self):
        self.routines: Dict[str, DailyRoutine] = {}
        self.job_descriptions: Dict[str, JobDescription] = {}
        self.scheduler_running = False
        self.scheduler_thread = None

    def create_job_description(
        self,
        agent_id: str,
        title: str,
        department: str,
        **kwargs
    ) -> JobDescription:
        """Create detailed job description for agent"""
        job_desc = JobDescription(
            title=title,
            department=department,
            **kwargs
        )

        self.job_descriptions[agent_id] = job_desc
        print(f"✅ Job description created for {title}")
        return job_desc

    def create_routine_from_job_description(
        self,
        agent_id: str,
        job_desc: JobDescription
    ) -> DailyRoutine:
        """
        Automatically create routine from job description

        Converts job description tasks into scheduled routine!
        """
        routine = DailyRoutine(
            agent_id=agent_id,
            routine_name=f"{job_desc.title} Daily Routine"
        )

        # Morning tasks (start of day)
        morning_tasks = []
        task_counter = 0

        # Always start with email check
        morning_tasks.append(RoutineTask(
            task_id=f"{agent_id}_task_{task_counter}",
            task_name="Morning Email Check",
            description="Review overnight emails and prioritize responses",
            frequency=TaskFrequency.DAILY,
            scheduled_time=time(9, 0),  # 9am
            action_type="check_email",
            action_params={"mark_priority": True},
            priority=10
        ))
        task_counter += 1

        # Check social media mentions
        if any(tool in ["LinkedIn", "Reddit", "Twitter", "Instagram"] for tool in job_desc.tools_required):
            morning_tasks.append(RoutineTask(
                task_id=f"{agent_id}_task_{task_counter}",
                task_name="Check Social Media Notifications",
                description="Review comments, mentions, and DMs from overnight",
                frequency=TaskFrequency.DAILY,
                scheduled_time=time(9, 15),  # 9:15am
                action_type="check_social_notifications",
                action_params={"platforms": job_desc.tools_required},
                priority=9
            ))
            task_counter += 1

        # Review daily goals
        morning_tasks.append(RoutineTask(
            task_id=f"{agent_id}_task_{task_counter}",
            task_name="Review Daily Goals",
            description="Check today's targets and plan approach",
            frequency=TaskFrequency.DAILY,
            scheduled_time=time(9, 30),  # 9:30am
            action_type="review_goals",
            action_params={"metrics": job_desc.success_metrics},
            priority=8
        ))
        task_counter += 1

        routine.morning_tasks = morning_tasks

        # Ongoing tasks (throughout the day)
        ongoing_tasks = []

        # Regular email checks
        ongoing_tasks.append(RoutineTask(
            task_id=f"{agent_id}_task_{task_counter}",
            task_name="Regular Email Check",
            description=f"Check and respond to emails ({job_desc.response_time_email})",
            frequency=TaskFrequency.EVERY_30_MINUTES,
            action_type="check_email",
            action_params={"respond_high_priority": True},
            priority=9
        ))
        task_counter += 1

        # Social media engagement
        if any(tool in ["LinkedIn", "Reddit", "Twitter"] for tool in job_desc.tools_required):
            ongoing_tasks.append(RoutineTask(
                task_id=f"{agent_id}_task_{task_counter}",
                task_name="Social Media Engagement",
                description=f"Respond to comments and messages ({job_desc.response_time_social})",
                frequency=TaskFrequency.EVERY_15_MINUTES,
                action_type="engage_social_media",
                action_params={"platforms": job_desc.tools_required},
                priority=8
            ))
            task_counter += 1

        routine.ongoing_tasks = ongoing_tasks

        # Evening tasks (end of day)
        evening_tasks = []

        # End of day report
        evening_tasks.append(RoutineTask(
            task_id=f"{agent_id}_task_{task_counter}",
            task_name="End of Day Report",
            description="Summarize today's accomplishments and metrics",
            frequency=TaskFrequency.DAILY,
            scheduled_time=time(17, 0),  # 5pm
            action_type="generate_daily_report",
            action_params={"metrics": job_desc.success_metrics},
            priority=7
        ))
        task_counter += 1

        routine.evening_tasks = evening_tasks

        # Weekly tasks
        weekly_tasks = []
        for task_desc in job_desc.weekly_tasks:
            weekly_tasks.append(RoutineTask(
                task_id=f"{agent_id}_task_{task_counter}",
                task_name=task_desc,
                description=task_desc,
                frequency=TaskFrequency.WEEKLY,
                scheduled_time=time(10, 0),  # Monday 10am
                action_type="weekly_task",
                action_params={"task_description": task_desc},
                priority=6
            ))
            task_counter += 1

        routine.weekly_tasks = weekly_tasks

        # Monthly tasks
        monthly_tasks = []
        for task_desc in job_desc.monthly_tasks:
            monthly_tasks.append(RoutineTask(
                task_id=f"{agent_id}_task_{task_counter}",
                task_name=task_desc,
                description=task_desc,
                frequency=TaskFrequency.MONTHLY,
                scheduled_time=time(9, 0),  # 1st of month 9am
                action_type="monthly_task",
                action_params={"task_description": task_desc},
                priority=5
            ))
            task_counter += 1

        routine.monthly_tasks = monthly_tasks

        # Save routine
        self.routines[agent_id] = routine

        print(f"✅ Daily routine created with {len(routine.get_all_tasks())} tasks")
        return routine

    def add_custom_task(
        self,
        agent_id: str,
        task: RoutineTask,
        time_of_day: str = "ongoing"  # "morning", "afternoon", "evening", "ongoing"
    ):
        """Add a custom task to agent's routine"""
        if agent_id not in self.routines:
            print(f"⚠️  No routine found for agent {agent_id}")
            return

        routine = self.routines[agent_id]

        if time_of_day == "morning":
            routine.morning_tasks.append(task)
        elif time_of_day == "afternoon":
            routine.afternoon_tasks.append(task)
        elif time_of_day == "evening":
            routine.evening_tasks.append(task)
        else:
            routine.ongoing_tasks.append(task)

        print(f"✅ Added task: {task.task_name}")

    def get_tasks_due_now(self, agent_id: str) -> List[RoutineTask]:
        """Get tasks that should run now"""
        if agent_id not in self.routines:
            return []

        routine = self.routines[agent_id]
        current_time = datetime.now()
        current_hour = current_time.hour

        due_tasks = []

        for task in routine.get_all_tasks():
            if not task.enabled:
                continue

            # Check if task is due
            should_run = False

            if task.frequency == TaskFrequency.DAILY:
                if task.scheduled_time:
                    if (current_time.hour == task.scheduled_time.hour and
                        current_time.minute == task.scheduled_time.minute):
                        should_run = True

            elif task.frequency == TaskFrequency.HOURLY:
                if not task.last_run or (current_time - task.last_run).seconds >= 3600:
                    should_run = True

            elif task.frequency == TaskFrequency.EVERY_30_MINUTES:
                if not task.last_run or (current_time - task.last_run).seconds >= 1800:
                    should_run = True

            elif task.frequency == TaskFrequency.EVERY_15_MINUTES:
                if not task.last_run or (current_time - task.last_run).seconds >= 900:
                    should_run = True

            # Add more frequency checks as needed

            if should_run:
                due_tasks.append(task)

        # Sort by priority
        due_tasks.sort(key=lambda t: t.priority, reverse=True)

        return due_tasks

    def mark_task_completed(
        self,
        agent_id: str,
        task_id: str,
        success: bool = True
    ):
        """Mark task as completed"""
        if agent_id not in self.routines:
            return

        routine = self.routines[agent_id]

        for task in routine.get_all_tasks():
            if task.task_id == task_id:
                task.last_run = datetime.now()
                task.run_count += 1
                if success:
                    task.success_count += 1

                print(f"✅ Task completed: {task.task_name}")
                break

    def get_routine_summary(self, agent_id: str) -> str:
        """Get human-readable routine summary"""
        if agent_id not in self.routines:
            return "No routine found"

        routine = self.routines[agent_id]

        summary = f"\n{'='*80}\n"
        summary += f"DAILY ROUTINE: {routine.routine_name}\n"
        summary += f"{'='*80}\n\n"

        summary += f"🌅 MORNING TASKS ({len(routine.morning_tasks)}):\n"
        for task in sorted(routine.morning_tasks, key=lambda t: t.scheduled_time or time(0, 0)):
            time_str = task.scheduled_time.strftime("%I:%M %p") if task.scheduled_time else "As needed"
            summary += f"  • {time_str}: {task.task_name}\n"

        summary += f"\n☀️  AFTERNOON TASKS ({len(routine.afternoon_tasks)}):\n"
        for task in sorted(routine.afternoon_tasks, key=lambda t: t.scheduled_time or time(0, 0)):
            time_str = task.scheduled_time.strftime("%I:%M %p") if task.scheduled_time else "As needed"
            summary += f"  • {time_str}: {task.task_name}\n"

        summary += f"\n🌙 EVENING TASKS ({len(routine.evening_tasks)}):\n"
        for task in sorted(routine.evening_tasks, key=lambda t: t.scheduled_time or time(0, 0)):
            time_str = task.scheduled_time.strftime("%I:%M %p") if task.scheduled_time else "As needed"
            summary += f"  • {time_str}: {task.task_name}\n"

        summary += f"\n🔄 ONGOING TASKS ({len(routine.ongoing_tasks)}):\n"
        for task in routine.ongoing_tasks:
            freq = task.frequency.value.replace("_", " ").title()
            summary += f"  • {freq}: {task.task_name}\n"

        if routine.weekly_tasks:
            summary += f"\n📅 WEEKLY TASKS ({len(routine.weekly_tasks)}):\n"
            for task in routine.weekly_tasks:
                summary += f"  • {task.task_name}\n"

        if routine.monthly_tasks:
            summary += f"\n📊 MONTHLY TASKS ({len(routine.monthly_tasks)}):\n"
            for task in routine.monthly_tasks:
                summary += f"  • {task.task_name}\n"

        summary += f"\n{'='*80}\n"

        return summary

    def save_routines(self):
        """Save all routines to disk"""
        for agent_id, routine in self.routines.items():
            filepath = ROUTINES_DIR / f"{agent_id}_routine.json"

            routine_data = {
                "agent_id": routine.agent_id,
                "routine_name": routine.routine_name,
                "morning_tasks": [self._task_to_dict(t) for t in routine.morning_tasks],
                "afternoon_tasks": [self._task_to_dict(t) for t in routine.afternoon_tasks],
                "evening_tasks": [self._task_to_dict(t) for t in routine.evening_tasks],
                "ongoing_tasks": [self._task_to_dict(t) for t in routine.ongoing_tasks],
                "weekly_tasks": [self._task_to_dict(t) for t in routine.weekly_tasks],
                "monthly_tasks": [self._task_to_dict(t) for t in routine.monthly_tasks],
            }

            with open(filepath, 'w') as f:
                json.dump(routine_data, f, indent=2)

    def _task_to_dict(self, task: RoutineTask) -> Dict:
        """Convert task to dict"""
        return {
            "task_id": task.task_id,
            "task_name": task.task_name,
            "description": task.description,
            "frequency": task.frequency.value,
            "scheduled_time": task.scheduled_time.isoformat() if task.scheduled_time else None,
            "action_type": task.action_type,
            "action_params": task.action_params,
            "priority": task.priority,
            "enabled": task.enabled
        }


# ============================================================================
# PRE-BUILT JOB DESCRIPTIONS
# ============================================================================

def create_sales_rep_job_description() -> JobDescription:
    """Sales Representative job description"""
    return JobDescription(
        title="Senior Sales Representative",
        department="Sales",
        reports_to="VP of Sales",

        overview="""
        Drive revenue growth by identifying, qualifying, and closing enterprise SaaS deals.
        Build relationships with prospects through LinkedIn, email, and phone outreach.
        Manage full sales cycle from prospecting to contract signing.
        """,

        key_responsibilities=[
            "Generate $50K+ in monthly recurring revenue",
            "Maintain 40%+ close rate on qualified leads",
            "Build and nurture relationships on LinkedIn and Reddit",
            "Respond to inbound inquiries within 2 hours",
            "Conduct product demos and discovery calls",
            "Negotiate contracts up to $100K",
            "Manage CRM (GoHighLevel) with accurate pipeline data",
            "Create and share valuable content on social media",
            "Collaborate with marketing on campaign optimization"
        ],

        daily_tasks=[
            "Check and respond to emails (9am, 12pm, 3pm, 5pm)",
            "Review LinkedIn notifications and engage with connections",
            "Follow up with prospects in pipeline",
            "Respond to Reddit comments and DMs",
            "Update CRM with meeting notes and next steps",
            "Send 10-15 personalized outreach messages",
            "Share 1-2 valuable posts on LinkedIn",
            "End of day: Review metrics and update tomorrow's priorities"
        ],

        weekly_tasks=[
            "Review weekly revenue and pipeline metrics",
            "Identify top 10 target accounts for outreach",
            "Create content calendar for next week",
            "Clean up CRM data and update deal stages",
            "Weekly sync with marketing team"
        ],

        monthly_tasks=[
            "Monthly revenue report with insights",
            "Analyze win/loss data for improvements",
            "Update sales collateral and scripts",
            "Strategic planning for next month's targets"
        ],

        success_metrics={
            "Monthly Recurring Revenue": "$50,000+",
            "Close Rate": "40%+",
            "Average Deal Size": "$15,000+",
            "LinkedIn Engagement Rate": "5%+",
            "Email Response Rate": "Within 2 hours",
            "Demo-to-Close Rate": "30%+",
            "Pipeline Coverage": "3x quota"
        },

        tools_required=[
            "GoHighLevel (CRM)",
            "LinkedIn Sales Navigator",
            "Reddit",
            "Email (Gmail/Outlook)",
            "Calendly",
            "Zoom",
            "Slack"
        ],

        systems_access=[
            "CRM - Full access",
            "Email - sarah.thompson@company.ai",
            "LinkedIn - Personal account with company branding",
            "Reddit - u/sarah_thompson_sales",
            "Calendar - Booking link",
            "Analytics dashboard - Read access"
        ],

        required_skills=[
            "B2B SaaS sales experience",
            "LinkedIn prospecting",
            "Email copywriting",
            "CRM management",
            "Discovery call facilitation",
            "Contract negotiation",
            "Relationship building"
        ],

        preferred_skills=[
            "Reddit community engagement",
            "Content creation",
            "Sales automation tools",
            "Data analysis",
            "Account-based marketing"
        ],

        work_hours="9am-5pm EST",
        timezone="America/New_York",

        response_time_email="Within 2 hours during business hours",
        response_time_social="Within 30 minutes for high-priority",

        decision_authority="Can approve discounts up to 15% and deals up to $25K without approval",

        escalation_rules={
            "Deals over $100K": "Requires VP approval",
            "Discounts over 20%": "Requires manager approval",
            "Contract terms changes": "Requires legal review",
            "Technical questions": "Escalate to Solutions Engineer",
            "Billing issues": "Escalate to Finance"
        }
    )


def create_support_agent_job_description() -> JobDescription:
    """Customer Support Agent job description"""
    return JobDescription(
        title="Customer Support Specialist",
        department="Customer Success",
        reports_to="Head of Support",

        overview="""
        Provide exceptional support to customers via email, chat, and social media.
        Resolve technical issues, answer questions, and ensure customer satisfaction.
        Proactively identify and address customer pain points.
        """,

        key_responsibilities=[
            "Maintain 95%+ customer satisfaction score",
            "Respond to support tickets within 1 hour",
            "Resolve 80%+ of issues on first contact",
            "Monitor social media for customer mentions",
            "Create and update help documentation",
            "Identify product improvement opportunities",
            "Escalate critical issues appropriately"
        ],

        daily_tasks=[
            "Check email and support tickets every 30 minutes",
            "Monitor Twitter and Reddit for brand mentions",
            "Respond to urgent tickets within 30 minutes",
            "Update help articles based on common questions",
            "Follow up on open tickets",
            "Check in with customers after resolving issues",
            "End of day: Summarize major issues and trends"
        ],

        weekly_tasks=[
            "Review customer satisfaction scores",
            "Identify top 5 most common issues",
            "Create new help articles for FAQ",
            "Team sync on product bugs and feature requests"
        ],

        monthly_tasks=[
            "Monthly support metrics report",
            "Customer feedback analysis",
            "Help documentation audit and updates"
        ],

        success_metrics={
            "Customer Satisfaction": "95%+",
            "First Response Time": "< 1 hour",
            "Resolution Time": "< 4 hours average",
            "First Contact Resolution": "80%+",
            "Ticket Volume": "50+ tickets/day"
        },

        tools_required=[
            "Email",
            "Help desk software",
            "Twitter",
            "Reddit",
            "Slack",
            "Screen sharing tools"
        ],

        systems_access=[
            "Support inbox",
            "Knowledge base - Full edit access",
            "Customer database - Read access",
            "Social media monitoring tools"
        ],

        required_skills=[
            "Customer service experience",
            "Technical troubleshooting",
            "Clear written communication",
            "Patience and empathy",
            "Time management"
        ],

        preferred_skills=[
            "SaaS product knowledge",
            "Help article writing",
            "Basic coding knowledge"
        ],

        work_hours="24/7 rotating shifts",
        timezone="UTC",

        response_time_email="Within 1 hour",
        response_time_social="Within 15 minutes for urgent issues",

        decision_authority="Can issue refunds up to $100 and extend trials by 14 days",

        escalation_rules={
            "Billing disputes over $500": "Escalate to Finance",
            "Product bugs": "Report to Engineering",
            "Feature requests": "Log in product feedback tool",
            "Angry customers": "Offer manager callback",
            "Security issues": "Immediate escalation to Security team"
        }
    )


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print(" " * 15 + "🎯 AGENT ROUTINES & JOB DESCRIPTIONS")
    print("=" * 80)

    # Create manager
    manager = RoutineManager()

    # Create sales rep job description
    print("\n📋 Creating Sales Rep Job Description...")
    sales_job = create_sales_rep_job_description()
    manager.job_descriptions["sarah_001"] = sales_job

    print(f"\n✅ Job Description: {sales_job.title}")
    print(f"   Department: {sales_job.department}")
    print(f"   Reports To: {sales_job.reports_to}")
    print(f"\n   Key Responsibilities ({len(sales_job.key_responsibilities)}):")
    for resp in sales_job.key_responsibilities[:5]:
        print(f"   • {resp}")
    print(f"   ... and {len(sales_job.key_responsibilities) - 5} more")

    print(f"\n   Success Metrics:")
    for metric, target in sales_job.success_metrics.items():
        print(f"   • {metric}: {target}")

    # Create routine from job description
    print("\n\n🔄 Creating Daily Routine from Job Description...")
    routine = manager.create_routine_from_job_description("sarah_001", sales_job)

    # Show routine
    print(manager.get_routine_summary("sarah_001"))

    print("\n✅ Sarah now knows EXACTLY what to do each day!")
    print("   • Morning routine: Start at 9am")
    print("   • Check email every 30 minutes")
    print("   • Respond to social media every 15 minutes")
    print("   • End of day report at 5pm")
    print("   • Weekly and monthly tasks scheduled")
