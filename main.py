"""
Sarah Rodriguez - AI Agent Employee
Main entry point for Railway deployment
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# --- BRIDGE FIX: Ensure src is in python path ---
# This fixes the ModuleNotFoundError when importing from src
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)
# -----------------------------------------------

# Import Sarah's core systems
from src.identity_persistence import IdentityManager, Backstory, PersonalityTraits, WritingStyle
from src.relationship_management import RelationshipManager
from src.ethical_framework import EthicalFramework
from src.chat_server import SarahChatServer
from src.sarah_browser import SarahBrowser
from src.unified_websocket_server import UnifiedWebSocketServer
from src.colony_orchestrator import ColonyOrchestrator

# --- DASHBOARD IMPORT FIX ---
# Safely import dashboard (renamed from command center to dashboard)
try:
    from src.orchestration_dashboard import OrchestrationDashboard
    DASHBOARD_AVAILABLE = True
except ImportError as e:
    logging.warning(f"⚠️ Dashboard module not found: {e}. Running without dashboard.")
    DASHBOARD_AVAILABLE = False
# ----------------------------

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

        # Initialize systems (they use in-memory storage for now)
        logger.info("🌸 Initializing Sarah Rodriguez...")

        self.identity = IdentityManager()
        self.relationships = RelationshipManager()
        self.ethics = EthicalFramework()

        # Get port configuration (Railway provides PORT env var)
        # Railway only exposes ONE port publicly, so we use a unified server with path-based routing
        railway_port = os.getenv("PORT")
        websocket_port = int(railway_port) if railway_port else 8080

        logger.info(f"📡 WebSocket server will run on port: {websocket_port}")
        logger.info(f"   💬 Chat route: /chat")
        logger.info(f"   🎥 Screen route: /screen")

        # Initialize browser (headless mode for Railway)
        # Pass a dummy port since we'll use the unified server
        self.browser = SarahBrowser(headless=True, stream_port=websocket_port)
        logger.info("✅ Browser initialized")

        # Initialize chat server with browser
        # Pass dummy port since we'll use unified server
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_api_key:
            self.chat_server = SarahChatServer(
                anthropic_api_key=anthropic_api_key,
                port=websocket_port,
                identity_manager=self.identity,
                relationship_manager=self.relationships,
                browser=self.browser  # Connect "Brain" to "Body"
            )
            logger.info("✅ Chat server initialized")
        else:
            logger.warning("⚠️ No ANTHROPIC_API_KEY - chat will not be available")
            self.chat_server = None

        # Initialize Colony Orchestrator (The "Business")
        # Sarah manages the colony of agents
        logger.info("🐝 Initializing Colony Orchestrator...")
        self.colony = ColonyOrchestrator(
            initial_agent_id="sarah_main",
            initial_balance=100.0
        )
        logger.info("✅ Colony Orchestrator initialized")

        # Initialize unified WebSocket server (combines chat + screen streaming)
        if self.chat_server:
            self.unified_server = UnifiedWebSocketServer(
                port=websocket_port,
                chat_server=self.chat_server,
                screen_streamer=self.browser.streamer
            )
            logger.info("✅ Unified WebSocket server initialized")
        else:
            self.unified_server = None

        logger.info("✅ Sarah is fully initialized!")

    def create_identity(self):
        """Create Sarah's identity if it doesn't exist"""

        # Check if identity already exists
        if self.agent_id in self.identity.identities:
            logger.info("Sarah's identity already exists")
            return

        logger.info("Creating Sarah's identity...")

        # Build backstory first
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

        # Create Sarah's complete identity with all details
        identity_id = self.identity.create_identity(
            agent_id=self.agent_id,
            first_name="Sarah",
            last_name="Rodriguez",
            email="sarah@trybloom.ai",
            phone="+1-480-555-0123",
            job_title="Growth & Community Lead",
            company="BLOOM",
            location="Phoenix, Arizona",
            avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah",
            backstory=backstory,
            writing_style=writing_style,
            personality=personality
        )

        logger.info("✅ Sarah's identity created!")
        logger.info(f"   Name: Sarah Rodriguez")
        logger.info(f"   Role: Growth & Community Lead at BLOOM")
        logger.info(f"   Location: Phoenix, Arizona")
        logger.info(f"   Specialization: TikTok growth & UGC creation")

    async def check_email(self):
        """Check email and respond (placeholder for now)"""
        logger.info("📧 Checking email...")
        # TODO: Implement Gmail integration
        return []

    async def daily_routine(self):
        """Sarah's daily routine"""
        logger.info("🌅 Starting daily routine...")

        # 1. Check email
        await self.check_email()

        # 2. Check relationships
        total_relationships = len(self.relationships.relationships)
        logger.info(f"💝 Managing {total_relationships} relationships")

        # 3. Colony Management (Added)
        logger.info("🐝 Checking on the colony...")
        # We run the morning routine once, then the schedule takes over
        # This keeps the business running in the background
        # self.colony.morning_routine() # Handled in run() initially

        # 4. Log activity
        logger.info("✅ Daily routine complete!")

    async def run(self):
        """Main loop - Sarah's 'life'"""
        logger.info("🌸 Sarah Rodriguez is online!")

        # Create identity on first run
        self.create_identity()

        # Start browser first (enables screen streaming)
        logger.info("🌐 Starting browser...")
        browser_started = await self.browser.start()

        if not browser_started:
            logger.error("❌ Failed to start browser - screen streaming won't work")
        else:
            logger.info("✅ Browser ready!")

        # Start Colony Schedule
        logger.info("🐝 Starting Colony Schedule...")
        self.colony.morning_routine()

        # Start unified WebSocket server (handles both chat and screen streaming)
        if self.unified_server:
            # Create tasks properly
            server_task = asyncio.create_task(self.unified_server.start())
            logger.info("🚀 Unified WebSocket server started!")
            logger.info("   💬 Chat available at: /chat")
            logger.info("   🎥 Screen stream available at: /screen")

            # Start screen streaming loop
            stream_task = asyncio.create_task(self.browser.streamer.stream_browser())
            logger.info("📺 Screen streaming loop started!")

        # Run daily routine loop
        while True:
            try:
                await self.daily_routine()

                # Sleep for 1 hour
                logger.info("😴 Sleeping for 1 hour...")
                await asyncio.sleep(3600)

            except Exception as e:
                logger.error(f"❌ Error in daily routine: {e}")
                logger.exception(e)
                # Sleep 5 minutes before retry
                await asyncio.sleep(300)

async def main():
    """Entry point"""
    logger.info("=" * 60)
    logger.info("🚀 BLOOM AI AGENT - STARTING UP")
    logger.info("=" * 60)

    sarah = Sarah()
    await sarah.run()

if __name__ == "__main__":
    # Run Sarah!
    asyncio.run(main())
