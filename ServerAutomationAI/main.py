#!/usr/bin/env python3

import sys
import time
import signal
from agent_manager import AgentManager
from agents.ai_manager import AIManager
from agents.performance_monitor import PerformanceMonitor
from agents.log_analyzer import LogAnalyzer
from agents.security_monitor import SecurityMonitor
from agents.database_manager import DatabaseManager
from agents.backup_recovery import BackupRecoveryAgent
from tools.logger import get_logger


class AIMultiAgentSystem:
    def __init__(self):
        self.logger = get_logger('main')
        self.agent_manager = AgentManager()
        self.running = False
        
        self.logger.info("AI Multi-Agent Server Automation System starting...")
        
        self._register_agents()
        self._setup_signal_handlers()
    
    def _register_agents(self):
        self.logger.info("Registering agents...")
        
        try:
            ai_manager = AIManager()
            self.agent_manager.register_agent('ai_manager', ai_manager)
        except Exception as e:
            self.logger.error(f"Failed to register AI Manager: {e}")
        
        try:
            perf_monitor = PerformanceMonitor()
            self.agent_manager.register_agent('performance_monitor', perf_monitor)
        except Exception as e:
            self.logger.error(f"Failed to register Performance Monitor: {e}")
        
        try:
            log_analyzer = LogAnalyzer()
            self.agent_manager.register_agent('log_analyzer', log_analyzer)
        except Exception as e:
            self.logger.error(f"Failed to register Log Analyzer: {e}")
        
        try:
            security_monitor = SecurityMonitor()
            self.agent_manager.register_agent('security_monitor', security_monitor)
        except Exception as e:
            self.logger.error(f"Failed to register Security Monitor: {e}")
        
        try:
            db_manager = DatabaseManager()
            self.agent_manager.register_agent('database_manager', db_manager)
        except Exception as e:
            self.logger.error(f"Failed to register Database Manager: {e}")
        
        try:
            backup_agent = BackupRecoveryAgent()
            self.agent_manager.register_agent('backup_recovery', backup_agent)
        except Exception as e:
            self.logger.error(f"Failed to register Backup & Recovery Agent: {e}")
        
        self.logger.info("All agents registered successfully")
    
    def _setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
    
    def _handle_shutdown(self, signum, frame):
        self.logger.info("Shutdown signal received")
        self.stop()
    
    def start(self):
        self.running = True
        self.logger.info("=" * 60)
        self.logger.info("AI Multi-Agent Server Automation System")
        self.logger.info("=" * 60)
        
        started = self.agent_manager.start_all_agents()
        
        self.logger.info(f"System started with {started} active agents")
        self.logger.info("System is now running. Press Ctrl+C to stop.")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
            self.stop()
    
    def stop(self):
        if not self.running:
            return
        
        self.running = False
        self.logger.info("Stopping AI Multi-Agent System...")
        
        self.agent_manager.stop_all_agents()
        
        self.logger.info("System stopped successfully")
    
    def status(self):
        print("\n" + "=" * 60)
        print("AI Multi-Agent System Status")
        print("=" * 60)
        
        status = self.agent_manager.get_all_status()
        
        for agent_name, agent_status in status.items():
            status_str = "✓ RUNNING" if agent_status['status'] == 'running' else "✗ STOPPED"
            print(f"{agent_name:25} {status_str}")
        
        print("=" * 60 + "\n")


def print_banner():
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║       AI Multi-Agent Server Automation System           ║
    ║                     Version 1.0.0                        ║
    ║                                                          ║
    ║  Intelligent server management with autonomous agents   ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_usage():
    usage = """
Usage: python main.py [command] [options]

Commands:
  start     - Start the AI Multi-Agent System (Infrastructure Agents)
  status    - Display status of all infrastructure agents
  dev       - Launch Developer Platform CLI/TUI (Phase 2A)
  dev-simple- Launch simple CLI overview (non-interactive)
  help      - Show this help message

Examples:
  python main.py                    # Start infrastructure agents
  python main.py start              # Same as above
  python main.py status             # Show agent status
  python main.py dev                # Launch Developer Platform (interactive)
  python main.py dev-simple         # Quick developer overview
    """
    print(usage)


def main():
    print_banner()
    
    command = sys.argv[1] if len(sys.argv) > 1 else 'start'
    
    if command == 'dev':
        from dev_platform import run_cli
        print("\n🚀 Launching Developer Platform CLI/TUI...\n")
        print("Phase 2A: Developer UX Interface")
        print("Press 'q' to quit, use number keys to select workflows\n")
        run_cli()
        return
    
    elif command == 'dev-simple':
        from dev_platform import run_simple_cli
        print("\n📊 Developer Platform Overview\n")
        run_simple_cli()
        return
    
    system = AIMultiAgentSystem()
    
    if command == 'start':
        system.start()
    elif command == 'status':
        system.status()
    elif command == 'help':
        print_usage()
    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
