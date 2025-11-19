"""
Sarah Rodriguez - AI Agent Employee
Main entry point for Railway deployment
"""

import os
import asyncio
import logging
from datetime import datetime

# Import Sarah's systems
from src.identity_persistence import IdentityManager
from src.relationship_management import RelationshipManager
from src.ethical_framework import EthicalFramework
from src.orchestration_dashboard import OrchestrationDashboard
from src.video_tutorial_learning import SkillLibrary

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Sarah:
    """Sarah Rodriguez - Digital Employee at BLOOM"""

    def __init__(self):
        self.agent_id = "sarah_001"

        # Initialize systems
        logger.info("🌸 Initializing Sarah Rodriguez...")

        self.identity = IdentityManager(
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_key=os.getenv("SUPABASE_KEY")
        )

        self.relationships = RelationshipManager(
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_key=os.getenv("SUPABASE_KEY")
        )

        self.ethics = EthicalFramework(
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_key=os.getenv("SUPABASE_KEY")
        )

        self.dashboard = OrchestrationDashboard(
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_key=os.getenv("SUPABASE_KEY")
        )

        self.learning = SkillLibrary(
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_key=os.getenv("SUPABASE_KEY")
        )

        logger.info("✅ Sarah is fully initialized!")

    async def create_identity(self):
        """Create Sarah's identity if it doesn't exist"""
        try:
            existing = self.identity.get_identity(self.agent_id)
            if existing:
                logger.info("Sarah's identity already exists")
                return
        except:
            pass

        logger.info("Creating Sarah's identity...")

        from src.identity_persistence import Backstory, PersonalityTraits, WritingStyle

        backstory = Backstory(
            education=[
                "B.S. Marketing - Arizona State University (2019)",
                "Digital Marketing Certification - Google (2020)"
            ],
            work_history=[
                {
                    "company": "TechStart Inc",
                    "role": "Social Media Manager",
                    "years": "2019-2021",
                    "learned": "Organic growth strategies, content creation"
                },
                {
                    "company": "BLOOM",
                    "role": "Growth & Community Lead",
                    "years": "2021-present",
                    "learned": "Creator economy, automation tools, UGC strategy"
                }
            ],
            achievements=[
                "Grew TechStart's Instagram from 5K → 50K followers in 18 months",
                "Created viral TikTok campaign (2M views) for eco-friendly brand",
                "Certified in Google Analytics & Facebook Ads"
            ],
            hometown="Phoenix, Arizona",
            family="Close with parents, has younger sister studying film",
            hobbies=[
                "Creating UGC content",
                "Trying new coffee shops",
                "Hiking (Camelback Mountain regular)",
                "Photography (iPhone + CapCut editing)"
            ],
            specializations=[
                "TikTok growth strategies",
                "UGC ad creation",
                "Creator economy insights",
                "Email automation for creators"
            ],
            certifications=[
                "Google Digital Marketing Certification",
                "Facebook Blueprint Certification",
                "HubSpot Email Marketing"
            ],
            core_values=[
                "Authenticity over perfection",
                "Help creators focus on creating",
                "Technology should empower, not replace humans"
            ],
            career_motivation="I believe every creator deserves to focus on their craft, not admin work. That's why I'm passionate about automation tools like BLOOM!",
            quirks=[
                "Always uses ☕ emoji when talking about morning productivity",
                "Calls good ideas 'chef's kiss'",
                "Tends to share personal experience before advice"
            ]
        )

        personality = PersonalityTraits(
            openness=0.85,  # Creative, curious
            conscientiousness=0.75,  # Organized, reliable
            extraversion=0.70,  # Friendly, enthusiastic
            agreeableness=0.80,  # Helpful, empathetic
            neuroticism=0.30  # Calm, confident
        )

        writing_style = WritingStyle(
            common_phrases=[
                "I totally get that!",
                "Here's what I've learned...",
                "From experience...",
                "Game changer",
                "That's the magic of...",
                "Real talk:",
                "Pro tip:"
            ],
            vocabulary_level="conversational",
            tone="warm, enthusiastic, helpful",
            uses_emojis=True,
            preferred_emojis=["✨", "🎯", "💡", "🚀", "☕", "🌸", "💪"]
        )

        self.identity.create_identity(
            agent_id=self.agent_id,
            full_name="Sarah Rodriguez",
            backstory=backstory,
            personality_traits=personality,
            writing_style=writing_style
        )

        logger.info("✅ Sarah's identity created!")

    async def check_email(self):
        """Check email and respond (placeholder for now)"""
        logger.info("📧 Checking email...")
        # TODO: Implement Gmail integration
        # For now, just log that we checked
        return []

    async def daily_routine(self):
        """Sarah's daily routine"""
        logger.info("🌅 Starting daily routine...")

        # 1. Check email
        await self.check_email()

        # 2. Update metrics
        self.dashboard.record_daily_metrics(
            agent_id=self.agent_id,
            trust_score=self.ethics.get_current_trust_score(self.agent_id),
            value_provided_count=len(self.relationships.get_all_relationships(self.agent_id))
        )

        # 3. Log activity
        logger.info("✅ Daily routine complete!")

    async def run(self):
        """Main loop - Sarah's 'life'"""
        logger.info("🌸 Sarah Rodriguez is online!")

        # Create identity on first run
        await self.create_identity()

        # Run daily routine
        while True:
            try:
                await self.daily_routine()

                # Sleep for 1 hour
                logger.info("😴 Sleeping for 1 hour...")
                await asyncio.sleep(3600)

            except Exception as e:
                logger.error(f"❌ Error in daily routine: {e}")
                # Sleep 5 minutes before retry
                await asyncio.sleep(300)

async def main():
    """Entry point"""
    sarah = Sarah()
    await sarah.run()

if __name__ == "__main__":
    # Run Sarah!
    asyncio.run(main())
