"""
BLOOM AI Agent - Webhook Handler
Receives conversion notifications from BLOOM backend.
"""

import logging
import os
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn
from colony_orchestrator import ColonyOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Create FastAPI app
app = FastAPI(title="BLOOM AI Agent Webhook Handler")

# Global colony orchestrator
colony_orchestrator: Optional[ColonyOrchestrator] = None


class ConversionNotification(BaseModel):
    """Conversion notification from BLOOM backend"""
    agent_id: str
    plan_type: str
    source_strategy: str
    source_platform: str
    conversion_path: str
    user_id: Optional[str] = None
    timestamp: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize colony on startup"""
    global colony_orchestrator

    logger.info("Starting webhook handler...")

    # Load or create colony
    if os.path.exists('data/genealogy.json'):
        logger.info("Loading existing colony...")
        colony_orchestrator = ColonyOrchestrator.load_colony('data')
    else:
        logger.info("Creating new colony...")
        initial_balance = float(os.getenv('INITIAL_BALANCE', '50.0'))
        colony_orchestrator = ColonyOrchestrator(
            initial_agent_id="adam",
            initial_balance=initial_balance
        )

    logger.info("Webhook handler ready!")


@app.post("/conversion")
async def receive_conversion(notification: ConversionNotification):
    """
    Receive conversion notification from BLOOM backend.

    Expected payload:
    {
        "agent_id": "adam",
        "plan_type": "creator",
        "source_strategy": "reddit_value_comment",
        "source_platform": "reddit",
        "conversion_path": "https://bloom.com?utm_source=reddit&utm_medium=ai_agent..."
    }
    """
    global colony_orchestrator

    if not colony_orchestrator:
        logger.error("Colony orchestrator not initialized")
        raise HTTPException(status_code=503, detail="Service not ready")

    logger.info(f"📥 Conversion received: {notification.agent_id} - {notification.plan_type}")

    # Validate agent exists
    if notification.agent_id not in colony_orchestrator.colony.agents:
        logger.warning(f"Unknown agent ID: {notification.agent_id}")
        raise HTTPException(status_code=404, detail=f"Agent '{notification.agent_id}' not found")

    # Get agent
    agent = colony_orchestrator.colony.agents[notification.agent_id]
    genealogy = colony_orchestrator.colony.genealogy[notification.agent_id]

    # Calculate commission
    commission_amount = agent.COMMISSION_RATES.get(notification.plan_type, 0.50)

    # Apply 2x commission for enterprise hunters
    from ai_agent import Specialization
    if genealogy.specialization == Specialization.ENTERPRISE_HUNTER:
        commission_amount *= 2.0
        logger.info(f"Enterprise hunter bonus: 2x commission = ${commission_amount:.2f}")

    # Record commission
    agent.record_commission(
        amount=commission_amount,
        user_id=notification.user_id or f"user_{datetime.now().timestamp()}",
        plan_type=notification.plan_type,
        source_strategy=notification.source_strategy,
        source_platform=notification.source_platform,
        conversion_path=notification.conversion_path
    )

    # Save state immediately
    colony_orchestrator.save_all_states()

    # Check if agent is now eligible for reproduction
    benchmark = colony_orchestrator.colony.check_reproduction_eligibility(notification.agent_id)
    reproduction_info = None

    if benchmark:
        logger.info(f"🧬 Agent '{notification.agent_id}' is eligible for reproduction at level {benchmark.level}!")
        child_id = colony_orchestrator.colony.reproduce_agent(notification.agent_id, benchmark)

        if child_id:
            reproduction_info = {
                'reproduced': True,
                'child_id': child_id,
                'benchmark_level': benchmark.level,
                'child_specialization': benchmark.child_specialization.value
            }
            # Save state after reproduction
            colony_orchestrator.save_all_states()

    # Return response
    return {
        'status': 'success',
        'agent_id': notification.agent_id,
        'commission_recorded': commission_amount,
        'new_balance': agent.commission_balance,
        'total_earned': agent.total_earned,
        'reproduction': reproduction_info,
        'timestamp': datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }


@app.get("/status")
async def get_status():
    """Get colony status"""
    global colony_orchestrator

    if not colony_orchestrator:
        raise HTTPException(status_code=503, detail="Service not ready")

    stats = colony_orchestrator.colony.get_colony_stats()

    return {
        'status': 'operational',
        'colony_stats': stats,
        'timestamp': datetime.now().isoformat()
    }


@app.get("/agents/{agent_id}")
async def get_agent_info(agent_id: str):
    """Get detailed info about a specific agent"""
    global colony_orchestrator

    if not colony_orchestrator:
        raise HTTPException(status_code=503, detail="Service not ready")

    if agent_id not in colony_orchestrator.colony.agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    agent = colony_orchestrator.colony.agents[agent_id]
    genealogy = colony_orchestrator.colony.genealogy[agent_id]

    # Get performance report
    report = agent.get_performance_report()

    # Add genealogy info
    report['genealogy'] = {
        'parent_id': genealogy.parent_id,
        'generation': genealogy.generation,
        'children': genealogy.children,
        'birth_date': genealogy.birth_date.isoformat()
    }

    return report


@app.get("/family-tree")
async def get_family_tree():
    """Get the full family tree"""
    global colony_orchestrator

    if not colony_orchestrator:
        raise HTTPException(status_code=503, detail="Service not ready")

    tree = colony_orchestrator.colony.get_family_tree()

    return {
        'family_tree': tree,
        'reproduction_history': colony_orchestrator.colony.reproduction_history,
        'timestamp': datetime.now().isoformat()
    }


def run_webhook_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the webhook server"""
    logger.info(f"Starting webhook server on {host}:{port}...")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()

    # Create logs directory
    os.makedirs('logs', exist_ok=True)

    # Run server
    run_webhook_server()
