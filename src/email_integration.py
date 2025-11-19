"""
Email Integration System - Agents Can Send & Receive Emails

This system provides:
- Email inbox monitoring for each agent
- Email sending with templates
- Email parsing and classification
- Priority/importance detection
- Auto-response capabilities
- Email metrics tracking
- Thread management

Every BLOOM agent has their own email inbox they can check!
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import secrets
import re


# ============================================================================
# ENUMS
# ============================================================================

class EmailPriority(Enum):
    """Email priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class EmailStatus(Enum):
    """Email status"""
    UNREAD = "unread"
    READ = "read"
    REPLIED = "replied"
    ARCHIVED = "archived"
    DELETED = "deleted"
    FLAGGED = "flagged"


class EmailCategory(Enum):
    """Email categories"""
    LEAD = "lead"
    CUSTOMER_INQUIRY = "customer_inquiry"
    SUPPORT_REQUEST = "support_request"
    SALES_OPPORTUNITY = "sales_opportunity"
    MEETING_REQUEST = "meeting_request"
    FOLLOW_UP = "follow_up"
    NEWSLETTER = "newsletter"
    SPAM = "spam"
    INTERNAL = "internal"
    OTHER = "other"


class EmailSentiment(Enum):
    """Email sentiment"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    URGENT = "urgent"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class EmailAddress:
    """Email address with name"""
    email: str
    name: Optional[str] = None

    def __str__(self) -> str:
        if self.name:
            return f"{self.name} <{self.email}>"
        return self.email


@dataclass
class Email:
    """
    Email message

    Example:
        email = Email(
            email_id="msg_123",
            from_address=EmailAddress("customer@example.com", "John Smith"),
            to_addresses=[EmailAddress("sarah.thompson@bloomai.agent", "Sarah Thompson")],
            subject="Interested in your product",
            body="Hi Sarah, I'd like to learn more about...",
            priority=EmailPriority.HIGH,
            category=EmailCategory.LEAD
        )
    """
    email_id: str
    from_address: EmailAddress
    to_addresses: List[EmailAddress]
    subject: str
    body: str

    # Optional fields
    cc_addresses: List[EmailAddress] = field(default_factory=list)
    bcc_addresses: List[EmailAddress] = field(default_factory=list)
    reply_to: Optional[EmailAddress] = None

    # Metadata
    priority: EmailPriority = EmailPriority.NORMAL
    status: EmailStatus = EmailStatus.UNREAD
    category: EmailCategory = EmailCategory.OTHER
    sentiment: EmailSentiment = EmailSentiment.NEUTRAL

    # Threading
    thread_id: Optional[str] = None
    in_reply_to: Optional[str] = None
    references: List[str] = field(default_factory=list)

    # Attachments
    attachments: List[Dict] = field(default_factory=list)

    # Flags
    is_flagged: bool = False
    is_important: bool = False

    # Timestamps
    received_at: datetime = field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None

    # Analysis
    keywords: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def mark_read(self):
        """Mark email as read"""
        if self.status == EmailStatus.UNREAD:
            self.status = EmailStatus.READ
            self.read_at = datetime.utcnow()

    def mark_replied(self):
        """Mark email as replied"""
        self.status = EmailStatus.REPLIED
        self.replied_at = datetime.utcnow()

    def flag(self):
        """Flag email"""
        self.is_flagged = True

    def unflag(self):
        """Unflag email"""
        self.is_flagged = False

    def archive(self):
        """Archive email"""
        self.status = EmailStatus.ARCHIVED

    @property
    def is_unread(self) -> bool:
        return self.status == EmailStatus.UNREAD

    @property
    def age_minutes(self) -> float:
        """Get email age in minutes"""
        return (datetime.utcnow() - self.received_at).total_seconds() / 60

    @property
    def needs_urgent_response(self) -> bool:
        """Check if email needs urgent response"""
        return (
            self.priority == EmailPriority.URGENT or
            self.sentiment == EmailSentiment.URGENT or
            (self.is_important and self.age_minutes > 60)
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "email_id": self.email_id,
            "from": str(self.from_address),
            "to": [str(addr) for addr in self.to_addresses],
            "subject": self.subject,
            "body_preview": self.body[:200] + "..." if len(self.body) > 200 else self.body,
            "priority": self.priority.value,
            "status": self.status.value,
            "category": self.category.value,
            "sentiment": self.sentiment.value,
            "is_unread": self.is_unread,
            "is_flagged": self.is_flagged,
            "is_important": self.is_important,
            "needs_urgent_response": self.needs_urgent_response,
            "received_at": self.received_at.isoformat(),
            "age_minutes": self.age_minutes,
            "tags": self.tags
        }


@dataclass
class EmailTemplate:
    """Email template for sending"""
    template_id: str
    name: str
    subject: str
    body_template: str
    category: EmailCategory
    variables: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def render(self, variables: Dict[str, str]) -> tuple[str, str]:
        """Render template with variables"""
        subject = self.subject
        body = self.body_template

        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            subject = subject.replace(placeholder, value)
            body = body.replace(placeholder, value)

        return subject, body


# ============================================================================
# EMAIL INBOX
# ============================================================================

class EmailInbox:
    """
    Email inbox for an agent

    Features:
    - Store and organize emails
    - Filter and search
    - Priority inbox
    - Unread count
    - Thread management
    """

    def __init__(self, agent_id: str, agent_email: str):
        self.agent_id = agent_id
        self.agent_email = agent_email
        self.emails: Dict[str, Email] = {}
        self.threads: Dict[str, List[str]] = {}  # thread_id -> [email_ids]

    def add_email(self, email: Email):
        """Add email to inbox"""
        self.emails[email.email_id] = email

        # Update thread
        if email.thread_id:
            if email.thread_id not in self.threads:
                self.threads[email.thread_id] = []
            self.threads[email.thread_id].append(email.email_id)

    def get_email(self, email_id: str) -> Optional[Email]:
        """Get email by ID"""
        return self.emails.get(email_id)

    def get_unread_emails(self) -> List[Email]:
        """Get all unread emails"""
        return [email for email in self.emails.values() if email.is_unread]

    def get_urgent_emails(self) -> List[Email]:
        """Get emails needing urgent response"""
        return [email for email in self.emails.values() if email.needs_urgent_response]

    def get_emails_by_category(self, category: EmailCategory) -> List[Email]:
        """Get emails by category"""
        return [email for email in self.emails.values() if email.category == category]

    def get_emails_by_sender(self, sender_email: str) -> List[Email]:
        """Get all emails from a sender"""
        return [
            email for email in self.emails.values()
            if email.from_address.email.lower() == sender_email.lower()
        ]

    def get_thread(self, thread_id: str) -> List[Email]:
        """Get all emails in a thread"""
        email_ids = self.threads.get(thread_id, [])
        emails = [self.emails[eid] for eid in email_ids if eid in self.emails]
        return sorted(emails, key=lambda e: e.received_at)

    def search_emails(self, query: str) -> List[Email]:
        """Search emails by text"""
        query_lower = query.lower()
        results = []

        for email in self.emails.values():
            if (
                query_lower in email.subject.lower() or
                query_lower in email.body.lower() or
                query_lower in email.from_address.email.lower()
            ):
                results.append(email)

        return results

    def get_stats(self) -> Dict:
        """Get inbox statistics"""
        emails = list(self.emails.values())
        unread = [e for e in emails if e.is_unread]
        urgent = [e for e in emails if e.needs_urgent_response]

        return {
            "total_emails": len(emails),
            "unread_count": len(unread),
            "urgent_count": len(urgent),
            "flagged_count": len([e for e in emails if e.is_flagged]),
            "categories": {
                cat.value: len([e for e in emails if e.category == cat])
                for cat in EmailCategory
            }
        }


# ============================================================================
# EMAIL ANALYZER
# ============================================================================

class EmailAnalyzer:
    """
    Analyzes emails to extract insights

    Features:
    - Priority detection
    - Category classification
    - Sentiment analysis
    - Keyword extraction
    - Intent detection
    """

    # Keywords for priority detection
    URGENT_KEYWORDS = [
        "urgent", "asap", "immediately", "emergency", "critical",
        "important", "priority", "deadline", "now", "quick"
    ]

    # Keywords for sentiment
    POSITIVE_KEYWORDS = ["thanks", "appreciate", "great", "excellent", "love", "perfect"]
    NEGATIVE_KEYWORDS = ["problem", "issue", "broken", "frustrated", "angry", "disappointed"]

    # Category patterns
    CATEGORY_PATTERNS = {
        EmailCategory.LEAD: ["interested in", "want to know", "looking for", "demo", "trial"],
        EmailCategory.SUPPORT_REQUEST: ["help", "issue", "problem", "not working", "error"],
        EmailCategory.SALES_OPPORTUNITY: ["purchase", "buy", "quote", "pricing", "proposal"],
        EmailCategory.MEETING_REQUEST: ["meeting", "call", "schedule", "available", "calendar"],
    }

    @staticmethod
    def analyze_email(email: Email) -> Email:
        """Analyze email and update metadata"""
        text = f"{email.subject} {email.body}".lower()

        # Detect priority
        email.priority = EmailAnalyzer._detect_priority(text)

        # Detect category
        email.category = EmailAnalyzer._detect_category(text)

        # Detect sentiment
        email.sentiment = EmailAnalyzer._detect_sentiment(text)

        # Mark as important if needed
        email.is_important = email.priority in [EmailPriority.HIGH, EmailPriority.URGENT]

        # Extract keywords
        email.keywords = EmailAnalyzer._extract_keywords(text)

        return email

    @staticmethod
    def _detect_priority(text: str) -> EmailPriority:
        """Detect email priority"""
        urgent_count = sum(1 for keyword in EmailAnalyzer.URGENT_KEYWORDS if keyword in text)

        if urgent_count >= 2:
            return EmailPriority.URGENT
        elif urgent_count >= 1:
            return EmailPriority.HIGH
        else:
            return EmailPriority.NORMAL

    @staticmethod
    def _detect_category(text: str) -> EmailCategory:
        """Detect email category"""
        for category, keywords in EmailAnalyzer.CATEGORY_PATTERNS.items():
            if any(keyword in text for keyword in keywords):
                return category

        return EmailCategory.OTHER

    @staticmethod
    def _detect_sentiment(text: str) -> EmailSentiment:
        """Detect email sentiment"""
        positive_count = sum(1 for kw in EmailAnalyzer.POSITIVE_KEYWORDS if kw in text)
        negative_count = sum(1 for kw in EmailAnalyzer.NEGATIVE_KEYWORDS if kw in text)
        urgent_count = sum(1 for kw in EmailAnalyzer.URGENT_KEYWORDS if kw in text)

        if urgent_count >= 2:
            return EmailSentiment.URGENT
        elif negative_count > positive_count:
            return EmailSentiment.NEGATIVE
        elif positive_count > negative_count:
            return EmailSentiment.POSITIVE
        else:
            return EmailSentiment.NEUTRAL

    @staticmethod
    def _extract_keywords(text: str) -> List[str]:
        """Extract important keywords"""
        # Simple keyword extraction (in production, use NLP)
        words = re.findall(r'\b[a-z]{4,}\b', text)
        # Get unique words
        return list(set(words))[:10]


# ============================================================================
# EMAIL MANAGER
# ============================================================================

class EmailManager:
    """
    Central email management system

    Features:
    - Manage inboxes for all agents
    - Send emails
    - Templates
    - Auto-responses
    - Email routing
    """

    def __init__(self):
        self.inboxes: Dict[str, EmailInbox] = {}  # agent_id -> inbox
        self.templates: Dict[str, EmailTemplate] = {}
        self.auto_responders: Dict[EmailCategory, Callable] = {}

    def create_inbox(self, agent_id: str, agent_email: str) -> EmailInbox:
        """Create inbox for an agent"""
        inbox = EmailInbox(agent_id, agent_email)
        self.inboxes[agent_id] = inbox
        return inbox

    def get_inbox(self, agent_id: str) -> Optional[EmailInbox]:
        """Get agent's inbox"""
        return self.inboxes.get(agent_id)

    def receive_email(
        self,
        to_email: str,
        from_email: str,
        from_name: Optional[str],
        subject: str,
        body: str,
        **kwargs
    ) -> Optional[Email]:
        """
        Receive an email (simulates incoming email)

        Example:
            email = manager.receive_email(
                to_email="sarah.thompson@bloomai.agent",
                from_email="customer@example.com",
                from_name="John Smith",
                subject="Interested in your product",
                body="Hi Sarah, I'd love to learn more..."
            )
        """
        # Find which agent's inbox this email goes to
        inbox = None
        agent_id = None

        for aid, ib in self.inboxes.items():
            if ib.agent_email.lower() == to_email.lower():
                inbox = ib
                agent_id = aid
                break

        if not inbox:
            return None

        # Create email
        email = Email(
            email_id=f"email_{secrets.token_urlsafe(16)}",
            from_address=EmailAddress(from_email, from_name),
            to_addresses=[EmailAddress(to_email)],
            subject=subject,
            body=body,
            **kwargs
        )

        # Analyze email
        email = EmailAnalyzer.analyze_email(email)

        # Add to inbox
        inbox.add_email(email)

        # Check for auto-responder
        if email.category in self.auto_responders:
            auto_responder = self.auto_responders[email.category]
            auto_responder(email, agent_id)

        return email

    def send_email(
        self,
        from_agent_id: str,
        to_email: str,
        to_name: Optional[str],
        subject: str,
        body: str,
        in_reply_to: Optional[str] = None
    ) -> Email:
        """
        Send an email from an agent

        Example:
            email = manager.send_email(
                from_agent_id="agent_001",
                to_email="customer@example.com",
                to_name="John Smith",
                subject="Re: Product Inquiry",
                body="Hi John, Thanks for your interest..."
            )
        """
        inbox = self.inboxes.get(from_agent_id)
        if not inbox:
            raise ValueError(f"No inbox found for agent {from_agent_id}")

        # Create email
        email = Email(
            email_id=f"email_{secrets.token_urlsafe(16)}",
            from_address=EmailAddress(inbox.agent_email),
            to_addresses=[EmailAddress(to_email, to_name)],
            subject=subject,
            body=body,
            status=EmailStatus.READ,
            in_reply_to=in_reply_to
        )

        # Mark original email as replied if this is a reply
        if in_reply_to:
            original = inbox.get_email(in_reply_to)
            if original:
                original.mark_replied()

        return email

    def send_from_template(
        self,
        from_agent_id: str,
        to_email: str,
        to_name: Optional[str],
        template_id: str,
        variables: Dict[str, str]
    ) -> Email:
        """Send email using a template"""
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        subject, body = template.render(variables)

        return self.send_email(
            from_agent_id=from_agent_id,
            to_email=to_email,
            to_name=to_name,
            subject=subject,
            body=body
        )

    def register_template(self, template: EmailTemplate):
        """Register an email template"""
        self.templates[template.template_id] = template

    def register_auto_responder(self, category: EmailCategory, responder: Callable):
        """Register auto-responder for a category"""
        self.auto_responders[category] = responder

    def get_all_unread_count(self) -> int:
        """Get total unread count across all inboxes"""
        return sum(
            len(inbox.get_unread_emails())
            for inbox in self.inboxes.values()
        )

    def get_stats(self) -> Dict:
        """Get overall email statistics"""
        total_emails = sum(len(inbox.emails) for inbox in self.inboxes.values())
        total_unread = self.get_all_unread_count()
        total_urgent = sum(
            len(inbox.get_urgent_emails())
            for inbox in self.inboxes.values()
        )

        return {
            "total_inboxes": len(self.inboxes),
            "total_emails": total_emails,
            "total_unread": total_unread,
            "total_urgent": total_urgent
        }


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("📧 Email Integration System Demo")
    print("=" * 70)

    # Create email manager
    manager = EmailManager()

    # Create inboxes for agents
    print("\n📥 Creating Agent Inboxes...")
    sarah_inbox = manager.create_inbox("agent_001", "sarah.thompson@bloomai.agent")
    mike_inbox = manager.create_inbox("agent_002", "mike.rodriguez@bloomai.agent")

    print(f"✅ Created inbox for sarah.thompson@bloomai.agent")
    print(f"✅ Created inbox for mike.rodriguez@bloomai.agent")

    # Receive some emails
    print("\n\n📨 Receiving Emails...")

    email1 = manager.receive_email(
        to_email="sarah.thompson@bloomai.agent",
        from_email="john.smith@acmecorp.com",
        from_name="John Smith",
        subject="URGENT: Need demo ASAP",
        body="Hi Sarah, We're very interested in your product and need to see a demo as soon as possible. Our team is evaluating solutions this week. Can we schedule something for tomorrow?"
    )

    email2 = manager.receive_email(
        to_email="sarah.thompson@bloomai.agent",
        from_email="jane.doe@example.com",
        from_name="Jane Doe",
        subject="Thanks for the great service!",
        body="Hi Sarah, I wanted to thank you for the excellent support. Everything is working perfectly now. Really appreciate your help!"
    )

    email3 = manager.receive_email(
        to_email="mike.rodriguez@bloomai.agent",
        from_email="customer@problem.com",
        from_name="Frustrated Customer",
        subject="Product not working - Need help immediately",
        body="Hi Mike, I'm having a critical issue with your product. It's completely broken and affecting my business. Please help urgently!"
    )

    print(f"✅ Received {manager.get_stats()['total_emails']} emails")

    # Show Sarah's inbox
    print("\n\n📬 Sarah's Inbox:")
    print("-" * 70)
    stats = sarah_inbox.get_stats()
    print(f"Total: {stats['total_emails']} | Unread: {stats['unread_count']} | Urgent: {stats['urgent_count']}")
    print()

    for email in sarah_inbox.emails.values():
        print(f"{'🔴 ' if email.is_unread else '✅ '}From: {email.from_address}")
        print(f"   Subject: {email.subject}")
        print(f"   Priority: {email.priority.value.upper()} | Category: {email.category.value}")
        print(f"   Sentiment: {email.sentiment.value} | Age: {email.age_minutes:.1f} min")
        if email.needs_urgent_response:
            print(f"   ⚠️  NEEDS URGENT RESPONSE!")
        print()

    # Show Mike's inbox
    print("\n📬 Mike's Inbox:")
    print("-" * 70)
    stats = mike_inbox.get_stats()
    print(f"Total: {stats['total_emails']} | Unread: {stats['unread_count']} | Urgent: {stats['urgent_count']}")
    print()

    for email in mike_inbox.emails.values():
        print(f"{'🔴 ' if email.is_unread else '✅ '}From: {email.from_address}")
        print(f"   Subject: {email.subject}")
        print(f"   Priority: {email.priority.value.upper()} | Category: {email.category.value}")
        if email.needs_urgent_response:
            print(f"   ⚠️  NEEDS URGENT RESPONSE!")
        print()

    # Sarah reads and replies to urgent email
    print("\n\n💬 Sarah Responding to Urgent Email...")
    if email1:
        email1.mark_read()
        reply = manager.send_email(
            from_agent_id="agent_001",
            to_email="john.smith@acmecorp.com",
            to_name="John Smith",
            subject="Re: URGENT: Need demo ASAP",
            body="Hi John,\n\nThank you for your interest! I'd be happy to schedule a demo for tomorrow. I have availability at 10am or 2pm EST. Which works better for your team?\n\nLooking forward to showing you what we can do!\n\nBest,\nSarah Thompson\nSenior Sales Representative",
            in_reply_to=email1.email_id
        )
        print(f"✅ Sarah replied to: {email1.subject}")
        print(f"   Email marked as: {email1.status.value}")

    # Register email template
    print("\n\n📝 Registering Email Templates...")
    template = EmailTemplate(
        template_id="welcome_email",
        name="Welcome New Customer",
        subject="Welcome to BLOOM AI!",
        body_template="""Hi {customer_name},

Welcome to BLOOM AI! We're excited to have you on board.

Your account is now active and ready to use. If you have any questions, feel free to reach out!

Best regards,
{agent_name}
{agent_title}""",
        category=EmailCategory.INTERNAL,
        variables=["customer_name", "agent_name", "agent_title"]
    )
    manager.register_template(template)
    print(f"✅ Registered template: {template.name}")

    # Send using template
    print("\n\n📤 Sending Email from Template...")
    welcome_email = manager.send_from_template(
        from_agent_id="agent_001",
        to_email="newcustomer@example.com",
        to_name="New Customer",
        template_id="welcome_email",
        variables={
            "customer_name": "Alex",
            "agent_name": "Sarah Thompson",
            "agent_title": "Senior Sales Representative"
        }
    )
    print(f"✅ Sent: {welcome_email.subject}")
    print(f"   To: {welcome_email.to_addresses[0]}")

    # Overall statistics
    print("\n\n📊 Overall Email Statistics:")
    print("-" * 70)
    overall_stats = manager.get_stats()
    print(f"Total Inboxes: {overall_stats['total_inboxes']}")
    print(f"Total Emails: {overall_stats['total_emails']}")
    print(f"Unread: {overall_stats['total_unread']}")
    print(f"Urgent: {overall_stats['total_urgent']}")

    print("\n" + "=" * 70)
    print("✨ Agents can now send and receive emails!")
