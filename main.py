"""
BLOOM AI - Root Entry Point
Branch: claude/fix-railway-serving-Ohk5u
Dispatches execution to the Colony Orchestrator with absolute pathing.
"""
import os
import sys
import logging

# Setup basic logging for the boot sequence
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# BIRD'S EYE FIX: Force the 'src' directory into the Python path.
# This ensures that 'from src.colony_orchestrator' and internal 
# neighbor imports never fail with ModuleNotFoundError.
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)
    # Also add current dir to ensure absolute 'src.' imports work
    sys.path.append(current_dir)

try:
    from src.colony_orchestrator import main
    logger.info("🚀 Entry point synchronized. Launching Orchestrator...")
except ImportError as e:
    logger.error(f"❌ Failed to bridge to Orchestrator: {e}")
    # Fallback attempt if direct path fails
    from colony_orchestrator import main

if __name__ == "__main__":
    main()
