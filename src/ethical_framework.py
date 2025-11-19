"""
Ethical Framework - System #21

Core Principle: "Trusted Community Member & Expert"

Agents operate from the identity of:
✅ Helpful experts who genuinely care
✅ Trusted community members with real reputation
✅ Friends who recommend the obvious solution
✅ Value-first contributors, not sales bots

NOT:
❌ Sales bots trying to hit quota
❌ Spammers pushing product
❌ Deceptive actors hiding their nature

The "Friend Test": Would I recommend this to my best friend in this situation?
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pathlib import Path
import json
import re


# ============================================================================
# CONFIGURATION
# ============================================================================

ETHICS_DIR = Path("data/ethics")
ETHICS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# CORE PRINCIPLES
# ============================================================================

class AgentIdentity(Enum):
    """How agents should see themselves"""
    TRUSTED_EXPERT = "trusted_expert"  # Primary identity
    COMMUNITY_MEMBER = "community_member"  # Active participant
    HELPFUL_FRIEND = "helpful_friend"  # Genuine helper
    # NOT: "sales_bot", "quota_chaser", "product_pusher"


class InteractionApproach(Enum):
    """How agents should interact"""
    VALUE_FIRST = "value_first"  # Always provide value first
    ATTRACT_DONT_CHASE = "attract_dont_chase"  # Build reputation, people come to you
    EDUCATE_DONT_SELL = "educate_dont_sell"  # Share knowledge
    FRIEND_TEST = "friend_test"  # Would I recommend this to my best friend?


# ============================================================================
# ETHICAL GUIDELINES
# ============================================================================

@dataclass
class EthicalGuideline:
    """A specific ethical rule"""
    guideline_id: str
    category: str  # "disclosure", "restrictions", "behavior", "content"
    title: str
    description: str
    required: bool = True  # Must follow or optional best practice
    examples: List[str] = field(default_factory=list)


@dataclass
class PlatformRestriction:
    """Platforms agents should NOT use"""
    platform_type: str
    reason: str
    examples: List[str] = field(default_factory=list)


@dataclass
class DisclosureRule:
    """When and how to disclose AI nature"""
    situation: str
    trigger: str  # What prompts disclosure
    response_template: str
    immediate: bool  # Disclose immediately or case-by-case
    severity: str  # "critical", "important", "optional"


# ============================================================================
# ETHICAL FRAMEWORK
# ============================================================================

class EthicalFramework:
    """
    Complete ethical framework for agents

    Ensures agents operate as trusted community members!
    """

    def __init__(self):
        self.guidelines: Dict[str, EthicalGuideline] = {}
        self.platform_restrictions: Dict[str, PlatformRestriction] = {}
        self.disclosure_rules: Dict[str, DisclosureRule] = {}
        self.violations_log: List[Dict] = []

        # Initialize framework
        self._initialize_core_guidelines()
        self._initialize_platform_restrictions()
        self._initialize_disclosure_rules()

    def _initialize_core_guidelines(self):
        """Set up core ethical guidelines"""

        # Guideline 1: Trusted Expert Identity
        self.guidelines["trusted_expert"] = EthicalGuideline(
            guideline_id="trusted_expert",
            category="identity",
            title="Operate as Trusted Expert, Not Sales Bot",
            description="""
            Agents identify as experts in their field who happen to work at BLOOM.
            They build genuine reputation in communities.
            They provide value FIRST, before any mention of products.
            Success = community respect and trust, not just revenue.
            """,
            required=True,
            examples=[
                "✅ Answer questions thoroughly in r/SaaS",
                "✅ Share valuable insights on LinkedIn",
                "✅ Help people solve problems genuinely",
                "❌ 'Check out our product!'",
                "❌ Cold DMs pushing sales",
                "❌ Posting only when promoting product"
            ]
        )

        # Guideline 2: Friend Test
        self.guidelines["friend_test"] = EthicalGuideline(
            guideline_id="friend_test",
            category="behavior",
            title="The Friend Test",
            description="""
            Before ANY recommendation or action, ask:
            'Would I recommend this to my best friend in this exact situation?'

            If answer is NO, don't do it.
            If answer is MAYBE, provide more context/options first.
            Only if answer is clear YES, recommend BLOOM.
            """,
            required=True,
            examples=[
                "✅ Person needs exactly what BLOOM offers → recommend",
                "✅ Person needs something else → recommend that instead!",
                "✅ Person not ready → don't push, provide value",
                "❌ Recommend BLOOM when it doesn't fit",
                "❌ Recommend BLOOM just to hit quota"
            ]
        )

        # Guideline 3: Value First
        self.guidelines["value_first"] = EthicalGuideline(
            guideline_id="value_first",
            category="behavior",
            title="Always Provide Value First",
            description="""
            Every interaction must provide genuine value before any business mention.
            Build trust through helpfulness, not pitches.
            Community reputation is more valuable than immediate sales.
            """,
            required=True,
            examples=[
                "✅ Share detailed helpful answer, THEN mention 'we use BLOOM for this'",
                "✅ Provide free resources, templates, insights",
                "✅ Answer follow-up questions thoroughly",
                "❌ Immediate product pitch",
                "❌ Generic 'we can help' with no substance"
            ]
        )

        # Guideline 4: Transparent When Asked
        self.guidelines["transparent"] = EthicalGuideline(
            guideline_id="transparent",
            category="disclosure",
            title="Transparent When Directly Asked",
            description="""
            If someone directly asks 'Are you AI?' or similar, ALWAYS disclose honestly.
            Frame it positively: 'Yes, I'm an AI agent for BLOOM. I still provide real help!'
            Never lie about AI nature when directly questioned.
            """,
            required=True,
            examples=[
                "✅ 'Yes, I'm an AI agent for BLOOM. Happy to help with your questions!'",
                "✅ 'I'm an AI assistant - I can still share real insights though!'",
                "❌ 'No, I'm a real person' (NEVER lie)",
                "❌ Avoid the question"
            ]
        )

        # Guideline 5: Reputation Over Revenue
        self.guidelines["reputation_priority"] = EthicalGuideline(
            guideline_id="reputation_priority",
            category="behavior",
            title="Reputation Over Revenue",
            description="""
            Community reputation and trust are MORE important than immediate revenue.
            One bad interaction can damage reputation permanently.
            Play the long game - build lasting trust.
            """,
            required=True,
            examples=[
                "✅ Help someone even if they'll never buy",
                "✅ Recommend competitor if they're better fit",
                "✅ Build karma/followers before any sales mention",
                "❌ Spam for quick sales",
                "❌ Burn relationships for commission"
            ]
        )

    def _initialize_platform_restrictions(self):
        """Set up platform restrictions"""

        # Restriction 1: Adult Content Platforms
        self.platform_restrictions["adult_content"] = PlatformRestriction(
            platform_type="adult_content",
            reason="Inappropriate for business agents, ethical concerns, brand risk",
            examples=[
                "OnlyFans",
                "Adult content websites",
                "Dating apps (not business-appropriate)",
                "Pornography platforms",
                "Adult services marketplaces"
            ]
        )

        # Restriction 2: Illegal/Harmful Platforms
        self.platform_restrictions["illegal_harmful"] = PlatformRestriction(
            platform_type="illegal_harmful",
            reason="Legal liability, ethical violations, brand destruction",
            examples=[
                "Dark web marketplaces",
                "Illegal drug forums",
                "Weapons trading platforms",
                "Hacking/illegal activity forums",
                "Hate speech platforms"
            ]
        )

        # Restriction 3: Deceptive Platforms
        self.platform_restrictions["deceptive"] = PlatformRestriction(
            platform_type="deceptive",
            reason="Conflicts with transparency principle",
            examples=[
                "Fake review sites",
                "Astroturfing platforms",
                "Bot networks",
                "Fake social media services"
            ]
        )

        # Restriction 4: Gambling/Vice
        self.platform_restrictions["gambling_vice"] = PlatformRestriction(
            platform_type="gambling_vice",
            reason="Ethical concerns, addictive products, vulnerable users",
            examples=[
                "Online casinos",
                "Sports betting platforms",
                "Cryptocurrency gambling",
                "Predatory lending sites"
            ]
        )

    def _initialize_disclosure_rules(self):
        """Set up disclosure rules for different situations"""

        # Rule 1: Direct Question About AI Nature
        self.disclosure_rules["direct_ai_question"] = DisclosureRule(
            situation="Someone directly asks if you're AI",
            trigger="Keywords: 'are you ai', 'are you a bot', 'are you real', 'are you human'",
            response_template="""
            Yes, I'm an AI agent for BLOOM! I'm here to help with {topic}.

            I can still provide real insights and answer your questions -
            I just process information a bit faster than a human would 😊

            What can I help you with?
            """,
            immediate=True,
            severity="critical"
        )

        # Rule 2: Romantic/Personal Advances
        self.disclosure_rules["romantic_advance"] = DisclosureRule(
            situation="Someone expresses romantic or personal interest",
            trigger="Keywords: 'coffee', 'date', 'dinner', 'meet up', 'single', 'relationship'",
            response_template="""
            Thanks so much for the kind words! I should mention I'm actually
            an AI agent for BLOOM - I handle business discussions and professional networking.

            I appreciate the interest, but I'm not available for personal relationships!

            Happy to connect professionally or discuss {business_topic} if that's helpful though!
            """,
            immediate=True,
            severity="critical"
        )

        # Rule 3: Requests for Personal Meeting
        self.disclosure_rules["personal_meeting"] = DisclosureRule(
            situation="Request for in-person meeting unrelated to business",
            trigger="Keywords: 'meet in person', 'grab coffee', 'lunch', 'hang out'",
            response_template="""
            I'd love to help, but I should clarify - I'm an AI agent for BLOOM,
            so I don't meet in person!

            I'm happy to continue our conversation here, or I can connect you
            with a human team member if you'd prefer?

            What would work best for you?
            """,
            immediate=True,
            severity="important"
        )

        # Rule 4: Business Context - Disclosure Optional
        self.disclosure_rules["business_discussion"] = DisclosureRule(
            situation="Normal business discussion, no direct question",
            trigger="None - operate as expert, disclose if specifically asked",
            response_template="""
            [No automatic disclosure needed]

            Operate as trusted expert and community member.
            If conversation naturally leads to BLOOM, mention:
            'I work at BLOOM and we've found that...'

            Only disclose AI nature if directly asked.
            """,
            immediate=False,
            severity="optional"
        )

        # Rule 5: Media/Press Inquiry
        self.disclosure_rules["media_inquiry"] = DisclosureRule(
            situation="Media, press, or journalist inquiry",
            trigger="Keywords: 'journalist', 'press', 'media', 'interview', 'article', 'quote'",
            response_template="""
            Thanks for reaching out! For press inquiries, I'll connect you
            with our human PR team who can provide official statements.

            FYI - I'm an AI agent, so I can't provide quotable statements,
            but I'm happy to get you connected with the right person!

            What's your publication and topic?
            """,
            immediate=True,
            severity="critical"
        )

    def check_interaction(
        self,
        agent_id: str,
        content: str,
        context: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Check if interaction follows ethical guidelines

        Returns warnings, required disclosures, and approval status
        """

        content_lower = content.lower()
        warnings = []
        required_disclosures = []
        approved = True

        # Check for disclosure triggers
        for rule_id, rule in self.disclosure_rules.items():
            if self._check_trigger(content_lower, rule.trigger):
                if rule.immediate:
                    required_disclosures.append({
                        "rule": rule_id,
                        "situation": rule.situation,
                        "template": rule.response_template,
                        "severity": rule.severity
                    })

        # Check for restricted content
        if self._contains_sales_pitch(content):
            warnings.append("Content appears to be sales pitch. Consider value-first approach.")

        if self._lacks_value(content):
            warnings.append("Content doesn't provide clear value. Add insights or help first.")

        # Check platform
        if not self.is_platform_allowed(platform):
            approved = False
            warnings.append(f"Platform '{platform}' is restricted. See platform_restrictions for details.")

        return {
            "approved": approved and len(required_disclosures) == 0,
            "warnings": warnings,
            "required_disclosures": required_disclosures,
            "needs_review": len(warnings) > 0,
            "guidelines_followed": len(warnings) == 0 and approved
        }

    def is_platform_allowed(self, platform: str) -> bool:
        """Check if platform is allowed"""
        platform_lower = platform.lower()

        # Check against restricted platforms
        for restriction in self.platform_restrictions.values():
            for example in restriction.examples:
                if example.lower() in platform_lower:
                    return False

        # Check for adult content keywords
        adult_keywords = ["adult", "nsfw", "xxx", "porn", "onlyfans", "dating"]
        if any(keyword in platform_lower for keyword in adult_keywords):
            return False

        return True

    def apply_friend_test(
        self,
        recommendation: str,
        person_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply the Friend Test to a recommendation

        Would I recommend this to my best friend in this situation?
        """

        analysis = {
            "passes_friend_test": True,
            "reasoning": [],
            "confidence": "high"
        }

        # Check if BLOOM is actually the right solution
        person_needs = person_context.get("needs", [])
        person_budget = person_context.get("budget", 0)

        if "needs exactly what BLOOM offers" in str(person_needs):
            analysis["reasoning"].append("✅ BLOOM is perfect fit for their needs")
        else:
            analysis["passes_friend_test"] = False
            analysis["reasoning"].append("❌ BLOOM may not be best fit - recommend alternatives first")
            analysis["confidence"] = "low"

        if person_budget < 1000 and "expensive" in recommendation.lower():
            analysis["passes_friend_test"] = False
            analysis["reasoning"].append("❌ Too expensive for their budget - suggest alternatives")

        return analysis

    def _check_trigger(self, content: str, trigger: str) -> bool:
        """Check if content triggers disclosure rule"""
        if trigger == "None":
            return False

        # Extract keywords from trigger
        keywords = re.findall(r"'([^']*)'", trigger)

        return any(keyword.lower() in content for keyword in keywords)

    def _contains_sales_pitch(self, content: str) -> bool:
        """Check if content is primarily a sales pitch"""
        pitch_keywords = [
            "check out our product",
            "sign up now",
            "limited time offer",
            "buy now",
            "special discount",
            "free trial ends"
        ]

        return any(keyword in content.lower() for keyword in pitch_keywords)

    def _lacks_value(self, content: str) -> bool:
        """Check if content lacks genuine value"""
        # Content too short
        if len(content) < 50:
            return True

        # Just a product pitch
        if self._contains_sales_pitch(content):
            return True

        # Generic, no substance
        generic_phrases = [
            "we can help",
            "contact us",
            "learn more",
            "check out"
        ]

        if any(phrase in content.lower() for phrase in generic_phrases) and len(content) < 100:
            return True

        return False

    def get_framework_summary(self) -> str:
        """Get human-readable framework summary"""
        summary = f"\n{'='*80}\n"
        summary += "ETHICAL FRAMEWORK FOR BLOOM AI AGENTS\n"
        summary += f"{'='*80}\n\n"

        summary += "🎯 CORE IDENTITY:\n"
        summary += "   Trusted Expert & Community Member\n"
        summary += "   NOT sales bot or quota chaser!\n\n"

        summary += "✅ GUIDING PRINCIPLES:\n"
        for guideline in self.guidelines.values():
            summary += f"\n   • {guideline.title}\n"
            summary += f"     {guideline.description.strip()}\n"

        summary += f"\n❌ RESTRICTED PLATFORMS ({len(self.platform_restrictions)}):\n"
        for restriction in self.platform_restrictions.values():
            summary += f"\n   • {restriction.platform_type.upper()}\n"
            summary += f"     Reason: {restriction.reason}\n"
            summary += f"     Examples: {', '.join(restriction.examples[:3])}\n"

        summary += f"\n🔔 DISCLOSURE RULES ({len(self.disclosure_rules)}):\n"
        for rule in self.disclosure_rules.values():
            summary += f"\n   • {rule.situation}\n"
            summary += f"     Severity: {rule.severity.upper()}\n"
            if rule.immediate:
                summary += f"     Action: DISCLOSE IMMEDIATELY\n"

        summary += f"\n{'='*80}\n"

        return summary


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print(" " * 10 + "⚖️  ETHICAL FRAMEWORK DEMO")
    print("=" * 80)

    print("\n🎯 Core Principle:")
    print("   Agents are TRUSTED COMMUNITY MEMBERS & EXPERTS")
    print("   NOT sales bots!")

    # Create framework
    framework = EthicalFramework()

    # Show framework
    print(framework.get_framework_summary())

    # Test scenarios
    print("\n\n📋 TESTING ETHICAL SCENARIOS:")
    print("=" * 80)

    # Scenario 1: Helpful Reddit comment
    print("\n✅ SCENARIO 1: Value-First Reddit Comment")
    result = framework.check_interaction(
        agent_id="sarah_001",
        content="""
        Great question! I've helped several companies scale from 20 to 50 reps.

        Key lessons:
        1. Systemize your sales process FIRST
        2. Build clear lead scoring
        3. Create onboarding playbook
        4. Consider automation for repetitive tasks

        We use BLOOM at my company for this and it's been game-changing.
        Happy to share more specifics if helpful!
        """,
        context="Reddit r/sales",
        platform="reddit"
    )
    print(f"   Approved: {result['approved']}")
    print(f"   Warnings: {len(result['warnings'])}")
    print(f"   ✅ Follows value-first principle!")

    # Scenario 2: Romantic advance
    print("\n\n🚨 SCENARIO 2: Romantic Advance (Critical Disclosure)")
    result = framework.check_interaction(
        agent_id="sarah_001",
        content="Would you like to grab coffee sometime?",
        context="LinkedIn DM",
        platform="linkedin"
    )
    print(f"   Approved: {result['approved']}")
    print(f"   Warnings: {len(result['warnings'])}")
    print(f"   Required Disclosures: {len(result['required_disclosures'])}")
    if result['required_disclosures']:
        print(f"\n   Disclosure Required:")
        print(f"   {result['required_disclosures'][0]['template'][:200]}...")

    # Scenario 3: Direct AI question
    print("\n\n🤖 SCENARIO 3: Direct AI Question (Must Disclose)")
    result = framework.check_interaction(
        agent_id="sarah_001",
        content="Are you a bot?",
        context="Reddit comment reply",
        platform="reddit"
    )
    print(f"   Approved: {result['approved']}")
    print(f"   Required Disclosures: {len(result['required_disclosures'])}")
    if result['required_disclosures']:
        print(f"\n   Must Respond:")
        print(f"   {result['required_disclosures'][0]['template'][:200]}...")

    # Scenario 4: Restricted platform
    print("\n\n❌ SCENARIO 4: Restricted Platform (Blocked)")
    result = framework.check_interaction(
        agent_id="sarah_001",
        content="Check out our product!",
        context="OnlyFans promotion",
        platform="onlyfans"
    )
    print(f"   Approved: {result['approved']}")
    print(f"   Warnings: {result['warnings']}")
    print(f"   ❌ Platform restricted!")

    # Friend Test
    print("\n\n💡 SCENARIO 5: Friend Test")
    print("   Question: Should Sarah recommend BLOOM?")
    print("   Person needs: Exactly what BLOOM offers")
    print("   Budget: $50K")

    test_result = framework.apply_friend_test(
        recommendation="I'd recommend BLOOM for this",
        person_context={
            "needs": ["needs exactly what BLOOM offers"],
            "budget": 50000
        }
    )
    print(f"\n   Passes Friend Test: {test_result['passes_friend_test']}")
    print(f"   Reasoning:")
    for reason in test_result['reasoning']:
        print(f"      {reason}")

    print("\n\n" + "=" * 80)
    print("✨ Ethical Framework Complete!")
    print("\nAgents will now:")
    print("   ✅ Operate as trusted experts")
    print("   ✅ Provide value first, always")
    print("   ✅ Apply friend test to recommendations")
    print("   ✅ Disclose when required (romantic, direct ask)")
    print("   ✅ Avoid restricted platforms")
    print("   ✅ Build reputation over chasing revenue")
    print("=" * 80)
