import os
import asyncio
import logging
import subprocess
from datetime import datetime

# Import Sarah's core systems
from src.identity_persistence import IdentityManager, Backstory, PersonalityTraits, WritingStyle
from src.relationship_management import RelationshipManager
from src.ethical_framework import EthicalFramework
from src.chat_server import SarahChatServer
from src.sarah_browser import SarahBrowser
from src.unified_websocket_server import UnifiedWebSocketServer

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

        self.identity = IdentityManager()
        self.relationships = RelationshipManager()
        self.ethics = EthicalFramework()

        # Get port configuration (Railway provides PORT env var)
        railway_port = os.getenv("PORT")
        websocket_port = int(railway_port) if railway_port else 8080

        logger.info(f"📡 WebSocket server will run on port: {websocket_port}")
        logger.info(f"   💬 Chat route: /chat")
        logger.info(f"   🎥 Screen route: /screen")

        # Initialize browser (headless mode for Railway)
        self.browser = SarahBrowser(headless=True, stream_port=websocket_port)
        logger.info("✅ Browser initialized")

        # Initialize chat server with browser
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_api_key:
            self.chat_server = SarahChatServer(
                anthropic_api_key=anthropic_api_key,
                port=websocket_port,
                identity_manager=self.identity,
                browser=self.browser
            )
            logger.info("✅ Chat server initialized")
        else:
            logger.warning("⚠️ No ANTHROPIC_API_KEY - chat will not be available")
            self.chat_server = None

        # Initialize unified WebSocket server
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
        if self.agent_id in self.identity.identities:
            logger.info("Sarah's identity already exists")
            return

        logger.info("Creating Sarah's identity...")

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
            openness=0.85,
            conscientiousness=0.75,
            extraversion=0.70,
            agreeableness=0.80,
            neuroticism=0.30
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

    async def check_email(self):
        """Check email and respond (placeholder)"""
        logger.info("📧 Checking email...")
        return []

    async def daily_routine(self):
        """Sarah's daily routine"""
        logger.info("🌅 Starting daily routine...")
        await self.check_email()
        total_relationships = len(self.relationships.relationships)
        logger.info(f"💝 Managing {total_relationships} relationships")
        logger.info("✅ Daily routine complete!")

    async def run(self):
        """Main loop - Sarah's 'life'"""
        logger.info("🌸 Sarah Rodriguez is online!")

        # 1. Ensure Identity
        self.create_identity()

        # 2. RUNTIME BROWSER CHECK (Persistent Volume Fix)
        # This checks if the browser binaries are in the /data volume
        browser_path = os.getenv('PLAYWRIGHT_BROWSERS_PATH', '/data/playwright-browsers')
        chromium_path = os.path.join(browser_path, 'chromium-1200')
        
        if not os.path.exists(chromium_path):
            logger.info("📦 First run or browsers missing in /data. Installing to persistent storage...")
            try:
                os.makedirs(browser_path, exist_ok=True)
                os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browser_path
                
                # Install browsers directly to the mounted volume
                process = await asyncio.create_subprocess_exec(
                    'playwright', 'install', '--with-deps', 'chromium',
                    env=os.environ
                )
                await process.wait()
                logger.info("✅ Playwright browsers successfully installed to /data!")
            except Exception as e:
                logger.error(f"❌ Runtime browser installation failed: {e}")
        else:
            logger.info(f"✅ Persistent browsers found at: {browser_path}")

        # 3. Start browser (Now it will find the files in /data)
        logger.info("🌐 Starting browser...")
        browser_started = await self.browser.start()

        if not browser_started:
            logger.error("❌ Failed to start browser - screen streaming won't work")
        else:
            logger.info("✅ Browser ready!")

        # 4. Start WebSocket Server & Streaming
        if self.unified_server:
            asyncio.create_task(self.unified_server.start())
            logger.info("🚀 Unified WebSocket server started!")
            asyncio.create_task(self.browser.streamer.stream_browser())
            logger.info("📺 Screen streaming loop started!")

        # 5. Continuous Loop
        while True:
            try:
                await self.daily_routine()
                logger.info("😴 Sleeping for 1 hour...")
                await asyncio.sleep(3600)
            except Exception as e:
                logger.error(f"❌ Error in daily routine: {e}")
                await asyncio.sleep(300)

async def main():
    """Entry point"""
    logger.info("=" * 60)
    logger.info("🚀 BLOOM AI AGENT - STARTING UP")
    logger.info("=" * 60)
    sarah = Sarah()
    await sarah.run()

if __name__ == "__main__":
    asyncio.run(main())
