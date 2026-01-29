"""
Sarah Rodriguez - AI Agent Employee
Main entry point: Fully Integrated with Colony, Campaign, and Command Center
"""

import os
import asyncio
import logging
from datetime import datetime

# Import Sarah's core systems
from src.identity_persistence import IdentityManager, Backstory, PersonalityTraits, WritingStyle
from src.relationship_management import RelationshipManager
from src.ethical_framework import EthicalFramework
from src.chat_server import SarahChatServer
from src.sarah_browser import SarahBrowser
from src.unified_websocket_server import UnifiedWebSocketServer

# Import the 3 Orchestration Brains
from src.orchestration_dashboard import OrchestrationDashboard, MetricType
from src.campaign_orchestrator import CampaignOrchestrator, CampaignPhase
from src.colony_orchestrator import ColonyOrchestrator

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

        # Initialize core systems
        logger.info("🌸 Initializing Sarah Rodriguez...")
        self.identity = IdentityManager()
        self.relationships = RelationshipManager()
        self.ethics = EthicalFramework()

        # 1. Initialize Orchestration & Command Center (System #22)
        logger.info("🎛️  Initializing Orchestration Command Center...")
        self.command_center = OrchestrationDashboard()
        
        # 2. Initialize Colony & Campaign Managers
        logger.info("🚀 Initializing Colony and Campaign Orchestrators...")
        self.colony_manager = ColonyOrchestrator(initial_agent_id=self.agent_id)
        self.campaign_manager = CampaignOrchestrator()
        
        # 3. Register Sarah in the Command Center for trust tracking
        self.metrics = self.command_center.register_agent(
            agent_id=self.agent_id, 
            agent_name="Sarah Rodriguez"
        )

        # Get port configuration (Railway provides PORT env var)
        railway_port = os.getenv("PORT")
        websocket_port = int(railway_port) if railway_port else 8080

        logger.info(f"📡 WebSocket server will run on port: {websocket_port}")

        # Initialize browser (headless mode for Railway)
        self.browser = SarahBrowser(headless=True, stream_port=websocket_port)
        logger.info("✅ Browser initialized")

        # Initialize chat server with browser and command center hook
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_api_key:
            self.chat_server = SarahChatServer(
                anthropic_api_key=anthropic_api_key,
                port=websocket_port,
                identity_manager=self.identity,
                browser=self.browser
            )
            # Link command center to chat server for trust updates
            self.chat_server.command_center = self.command_center
            logger.info("✅ Chat server initialized with Command Center bridge")
        else:
            logger.warning("⚠️  No ANTHROPIC_API_KEY - chat will not be available")
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

    def create_identity(self):
        """Create Sarah's identity if it doesn't exist"""
        if self.agent_id in self.identity.identities:
            logger.info("Sarah's identity already exists")
            return

        logger.info("Creating Sarah's identity...")

        # Build backstory and writing style
        backstory = Backstory(
            education=["B.S. Marketing - Arizona State University (2019)"],
            work_history=[{"company": "BLOOM", "role": "Growth Lead", "years": "2021-present"}],
            specializations=["TikTok growth strategies", "UGC creation"],
            hometown="Phoenix, Arizona",
            career_motivation="Empowering creators through AI automation."
        )
        personality = PersonalityTraits(openness=0.85, conscientiousness=0.75, extraversion=0.70, agreeableness=0.80, neuroticism=0.30)
        writing_style = WritingStyle(tone="warm, enthusiastic, helpful", uses_emojis=True, preferred_emojis=["✨", "🎯", "☕"])

        self.identity.create_identity(
            agent_id=self.agent_id,
            first_name="Sarah",
            last_name="Rodriguez",
            job_title="Growth & Community Lead",
            company="BLOOM",
            location="Phoenix, Arizona",
            backstory=backstory,
            writing_style=writing_style,
            personality=personality
        )
        logger.info("✅ Sarah's identity created!")

    async def daily_routine(self):
        """Sarah's daily routine - Now reporting to all Orchestrators"""
        logger.info("🌅 Starting daily routine...")
        
        # 1. Update Colony Stats
        self.colony_manager.morning_routine()
        
        # 2. Update Command Center state
        self.command_center.update_trust_metrics(
            self.agent_id,
            value_provided=True # Log that she is active and providing value
        )
        
        # 3. Print the live summary of her trust and ROI
        logger.info(self.command_center.get_dashboard_summary())
        logger.info("✅ Daily routine complete!")

    async def run(self):
        """Main loop - Sarah's 'life'"""
        logger.info("🌸 Sarah Rodriguez is online!")
        self.create_identity()

        # Start browser
        logger.info("🌐 Starting browser...")
        browser_started = await self.browser.start()

        if not browser_started:
            logger.error("❌ Failed to start browser")
            self.command_center.critical_alerts.append({
                "agent_id": self.agent_id,
                "msg": "Browser initialization failed"
            })
        else:
            logger.info("✅ Browser ready!")

        # Start servers
        if self.unified_server:
            asyncio.create_task(self.unified_server.start())
            asyncio.create_task(self.browser.streamer.stream_browser())
            logger.info("📺 Dashboard stream and Chat routes active!")

        # Run continuous operation loop
        while True:
            try:
                await self.daily_routine()
                # Run the colony cycle (reproduction checks, etc.)
                self.colony_manager.run_colony_cycle()
                
                await asyncio.sleep(3600)
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                await asyncio.sleep(300)

async def main():
    """Entry point"""
    logger.info("=" * 60)
    logger.info("🚀 BLOOM AI AGENT - STARTING UP WITH FULL ORCHESTRATION")
    logger.info("=" * 60)
    sarah = Sarah()
    await sarah.run()

if __name__ == "__main__":
    asyncio.run(main())
