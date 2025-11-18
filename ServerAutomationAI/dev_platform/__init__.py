"""
AI Multi-Agent Development Platform
Replit-like AI system for automatic application development
"""

__version__ = "2.0.0-dev"
__author__ = "Agent #7 - Planner Agent"

from dev_platform.cli_interface import run_cli, run_simple_cli, DeveloperCLI

__all__ = [
    "run_cli",
    "run_simple_cli", 
    "DeveloperCLI"
]
