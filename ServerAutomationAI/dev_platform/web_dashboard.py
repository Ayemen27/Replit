#!/usr/bin/env python3
"""
Web Dashboard Entry Point

Starts the FastAPI web server for monitoring the AI Multi-Agent Platform.
Usage:
    python dev_platform/web_dashboard.py [--host HOST] [--port PORT]
"""
import argparse
import asyncio
import logging
import sys

from dev_platform.web.api_server import start_server
from dev_platform.agents import get_ops_coordinator_agent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def initialize_coordinator():
    """Initialize OpsCoordinator async components"""
    try:
        coordinator = get_ops_coordinator_agent()
        await coordinator.initialize_async()
        logger.info("OpsCoordinator initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize OpsCoordinator: {e}")
        raise


def main():
    """Main entry point for web dashboard"""
    parser = argparse.ArgumentParser(
        description="AI Multi-Agent Platform Web Dashboard"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind server (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to bind server (default: 5000)"
    )
    
    args = parser.parse_args()
    
    try:
        logger.info("=" * 60)
        logger.info("AI Multi-Agent Platform - Web Dashboard")
        logger.info("=" * 60)
        logger.info(f"Starting web server on http://{args.host}:{args.port}")
        logger.info("Press Ctrl+C to stop")
        
        asyncio.run(initialize_coordinator())
        
        start_server(host=args.host, port=args.port)
    
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
