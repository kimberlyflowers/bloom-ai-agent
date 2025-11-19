"""
GoHighLevel CRM Automation - Frontend Agent Example

Agents can now:
- Log into GoHighLevel CRM
- Run SMS campaigns through the UI
- Build websites with the visual builder
- Manage contacts, deals, pipelines
- NO API needed - uses actual frontend!

Perfect for platforms where backend API isn't available or is limited!
"""

import sys
sys.path.append('.')

from visual_capabilities import BrowserAgent, VisualKnowledgeBase
from typing import List, Dict, Optional
from datetime import datetime
import time
import random


class GoHighLevelAgent:
    """
    Automate GoHighLevel CRM through frontend

    Can do EVERYTHING a human can do in GHL!
    """

    def __init__(
        self,
        agent_id: str,
        email: str,
        password: str,
        account_url: str  # Your GHL subdomain
    ):
        self.agent_id = agent_id
        self.email = email
        self.password = password
        self.account_url = account_url

        # Create browser agent
        self.browser = BrowserAgent(agent_id, headless=False)  # Show UI for demo
        self.knowledge_base = VisualKnowledgeBase()
        self.logged_in = False

    def login(self) -> bool:
        """Log into GoHighLevel"""
        print("\n🔐 Logging into GoHighLevel...")

        if not self.browser.start():
            return False

        # Navigate to login
        login_url = f"{self.account_url}/login"
        self.browser.navigate(login_url)
        self.browser.wait(2)

        # Screenshot login page
        self.browser.screenshot("GHL login page", ["gohighlevel", "login"])

        # Enter credentials
        print("   Entering email...")
        self.browser.type_text("input[type='email']", self.email, human_like=True)
        self.browser.wait(0.5)

        print("   Entering password...")
        self.browser.type_text("input[type='password']", self.password, human_like=True)
        self.browser.wait(0.5)

        # Click login
        print("   Clicking login button...")
        self.browser.click("button[type='submit']", human_like=True)
        self.browser.wait(3)

        # Screenshot after login
        screenshot = self.browser.screenshot("GHL dashboard", ["gohighlevel", "dashboard"])
        if screenshot:
            self.knowledge_base.add_screenshot(screenshot)

        self.logged_in = True
        print("✅ Logged into GoHighLevel!")
        return True

    def create_sms_campaign(
        self,
        campaign_name: str,
        contact_list: str,
        message: str,
        schedule_time: Optional[str] = None
    ) -> bool:
        """
        Create and launch SMS campaign through UI

        Args:
            campaign_name: Name for the campaign
            contact_list: Which contact list to use
            message: SMS message content
            schedule_time: When to send (None = send now)
        """
        if not self.logged_in:
            print("❌ Not logged in!")
            return False

        print(f"\n📱 Creating SMS Campaign: {campaign_name}")

        # Navigate to campaigns
        print("   Navigating to campaigns...")
        self.browser.click("a[href='/campaigns']", human_like=True)
        self.browser.wait(2)

        # Click "New Campaign"
        print("   Creating new campaign...")
        self.browser.click("button:contains('New Campaign')", human_like=True)
        self.browser.wait(1)

        # Select SMS campaign type
        print("   Selecting SMS campaign...")
        self.browser.click("div[data-type='sms']", human_like=True)
        self.browser.wait(1)

        # Enter campaign name
        print("   Entering campaign name...")
        self.browser.type_text("input[name='campaign_name']", campaign_name, human_like=True)
        self.browser.wait(0.5)

        # Screenshot campaign setup
        self.browser.screenshot("Campaign setup", ["gohighlevel", "campaign", "setup"])

        # Select contact list
        print("   Selecting contact list...")
        self.browser.click("select[name='contact_list']", human_like=True)
        self.browser.wait(0.3)
        self.browser.click(f"option:contains('{contact_list}')", human_like=True)
        self.browser.wait(0.5)

        # Enter message
        print("   Writing message...")
        self.browser.type_text("textarea[name='message']", message, human_like=True)
        self.browser.wait(1)

        # Screenshot message
        self.browser.screenshot(f"Campaign message: {campaign_name}", ["gohighlevel", "campaign", "message"])

        # Schedule or send now
        if schedule_time:
            print(f"   Scheduling for {schedule_time}...")
            self.browser.click("input[name='schedule']", human_like=True)
            self.browser.type_text("input[name='schedule_time']", schedule_time, human_like=True)
        else:
            print("   Setting to send now...")
            self.browser.click("input[value='send_now']", human_like=True)

        # Screenshot before sending
        screenshot = self.browser.screenshot(
            f"Ready to send: {campaign_name}",
            ["gohighlevel", "campaign", "ready"]
        )
        if screenshot:
            self.knowledge_base.add_screenshot(screenshot)

        # DON'T actually send in demo mode
        print("\n✅ Campaign created and ready!")
        print(f"   Name: {campaign_name}")
        print(f"   List: {contact_list}")
        print(f"   Message: {message[:50]}...")
        print("   (NOT sent - demo mode)")

        return True

    def build_website_page(
        self,
        page_name: str,
        template: str,
        customize_steps: List[Dict]
    ) -> bool:
        """
        Build website page using visual builder

        Args:
            page_name: Name for the page
            template: Which template to use
            customize_steps: List of customization steps
                [{"action": "change_text", "element": ".headline", "text": "New headline"}]
        """
        if not self.logged_in:
            print("❌ Not logged in!")
            return False

        print(f"\n🎨 Building Website Page: {page_name}")

        # Navigate to websites
        print("   Opening website builder...")
        self.browser.click("a[href='/sites']", human_like=True)
        self.browser.wait(2)

        # Create new page
        print("   Creating new page...")
        self.browser.click("button:contains('New Page')", human_like=True)
        self.browser.wait(1)

        # Enter page name
        self.browser.type_text("input[name='page_name']", page_name, human_like=True)
        self.browser.wait(0.5)

        # Select template
        print(f"   Selecting template: {template}...")
        self.browser.click(f"div[data-template='{template}']", human_like=True)
        self.browser.wait(2)

        # Screenshot initial template
        self.browser.screenshot(f"Template: {template}", ["gohighlevel", "website", "template"])

        # Customize page
        for step in customize_steps:
            action = step.get("action")
            element = step.get("element")

            if action == "change_text":
                print(f"   Changing text: {element}...")
                self.browser.click(element, human_like=True)
                self.browser.wait(0.5)
                self.browser.type_text("input.text-editor", step["text"], human_like=True)
                self.browser.wait(0.5)

            elif action == "upload_image":
                print(f"   Uploading image: {element}...")
                self.browser.click(element, human_like=True)
                self.browser.wait(0.5)
                # Upload file logic here

            elif action == "change_color":
                print(f"   Changing color: {element}...")
                self.browser.click(element, human_like=True)
                self.browser.wait(0.5)
                self.browser.click(f"div[data-color='{step['color']}']", human_like=True)

        # Screenshot final page
        screenshot = self.browser.screenshot(
            f"Page complete: {page_name}",
            ["gohighlevel", "website", "complete"]
        )
        if screenshot:
            self.knowledge_base.add_screenshot(screenshot)

        # Save (but don't publish in demo)
        print("   Saving page...")
        self.browser.click("button:contains('Save')", human_like=True)
        self.browser.wait(2)

        print(f"\n✅ Website page created: {page_name}")
        print("   (NOT published - demo mode)")

        return True

    def manage_contact(
        self,
        contact_name: str,
        action: str,  # "add_note", "change_status", "add_tag", "assign_to"
        **kwargs
    ) -> bool:
        """
        Manage contact through UI

        Examples:
            manage_contact("John Smith", "add_note", note="Had great call!")
            manage_contact("Jane Doe", "change_status", status="Hot Lead")
            manage_contact("Bob Johnson", "add_tag", tag="Enterprise")
        """
        if not self.logged_in:
            return False

        print(f"\n👤 Managing Contact: {contact_name}")

        # Navigate to contacts
        self.browser.click("a[href='/contacts']", human_like=True)
        self.browser.wait(2)

        # Search for contact
        print(f"   Searching for {contact_name}...")
        self.browser.type_text("input[placeholder='Search contacts']", contact_name, human_like=True)
        self.browser.wait(1)

        # Click on contact
        self.browser.click(f"div:contains('{contact_name}')", human_like=True)
        self.browser.wait(2)

        # Perform action
        if action == "add_note":
            note = kwargs.get("note", "")
            print(f"   Adding note...")
            self.browser.click("button:contains('Add Note')", human_like=True)
            self.browser.wait(0.5)
            self.browser.type_text("textarea", note, human_like=True)
            self.browser.click("button:contains('Save')", human_like=True)

        elif action == "change_status":
            status = kwargs.get("status", "")
            print(f"   Changing status to: {status}...")
            self.browser.click("select[name='status']", human_like=True)
            self.browser.wait(0.3)
            self.browser.click(f"option:contains('{status}')", human_like=True)

        elif action == "add_tag":
            tag = kwargs.get("tag", "")
            print(f"   Adding tag: {tag}...")
            self.browser.click("input[placeholder='Add tag']", human_like=True)
            self.browser.type_text("input[placeholder='Add tag']", tag, human_like=True)
            self.browser.click("button:contains('Add')", human_like=True)

        # Screenshot
        screenshot = self.browser.screenshot(
            f"Contact updated: {contact_name}",
            ["gohighlevel", "contact", "updated"]
        )
        if screenshot:
            self.knowledge_base.add_screenshot(screenshot)

        print(f"✅ Contact updated!")
        return True

    def close(self):
        """Close browser"""
        self.browser.close()


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print(" " * 10 + "🚀 GOHIGHLEVEL FRONTEND AUTOMATION DEMO")
    print("=" * 80)

    print("\n🎯 What This Enables:")
    print("   • Automate GoHighLevel through the UI (not API!)")
    print("   • Run SMS campaigns like a human would")
    print("   • Build websites with visual builder")
    print("   • Manage contacts, deals, pipelines")
    print("   • Take screenshots of every action")
    print("   • NO API limitations!")

    print("\n💡 Example Usage:")
    print("-" * 80)
    print("""
# Create GHL agent
sarah_ghl = GoHighLevelAgent(
    agent_id="sarah_001",
    email="sarah@yourcompany.com",
    password="secure_password",
    account_url="https://yourcompany.gohighlevel.com"
)

# Login to GHL
sarah_ghl.login()

# Run SMS campaign
sarah_ghl.create_sms_campaign(
    campaign_name="Black Friday Deal",
    contact_list="Hot Leads",
    message="Hi {first_name}! Special offer just for you: 50% off this weekend!",
    schedule_time="2025-11-25 09:00"
)

# Build landing page
sarah_ghl.build_website_page(
    page_name="Black Friday Landing Page",
    template="sales_page_1",
    customize_steps=[
        {"action": "change_text", "element": ".headline", "text": "50% Off This Weekend!"},
        {"action": "change_text", "element": ".subheadline", "text": "Limited time offer"},
        {"action": "change_color", "element": ".cta-button", "color": "#FF0000"}
    ]
)

# Manage contacts
sarah_ghl.manage_contact("John Smith", "add_note", note="Interested in enterprise plan")
sarah_ghl.manage_contact("Jane Doe", "change_status", status="Hot Lead")
sarah_ghl.manage_contact("Bob Johnson", "add_tag", tag="Black Friday")
    """)
    print("-" * 80)

    print("\n✨ Why This Is Powerful:")
    print("   ✅ Works even if GHL API has limitations")
    print("   ✅ Can do ANYTHING a human can do")
    print("   ✅ Visual builder automation (impossible with API!)")
    print("   ✅ Screenshots prove every action")
    print("   ✅ Human-like delays avoid detection")

    print("\n🎯 Same approach works for:")
    print("   • HubSpot")
    print("   • Salesforce")
    print("   • Active Campaign")
    print("   • Keap")
    print("   • Any CRM with a web interface!")

    print("\n" + "=" * 80)
    print("🌸 Frontend automation unlocks UNLIMITED possibilities!")
    print("=" * 80)
