import threading
import time
from typing import Dict, List
import yaml
from pathlib import Path
from tools.logger import get_logger


class AgentManager:
    def __init__(self):
        self.logger = get_logger('agent_manager')
        self.config = self._load_config()
        self.agents = {}
        self.agent_threads = {}
        self.running = False
        
        self.logger.info("Agent Manager initialized")
    
    def _load_config(self):
        config_path = Path(__file__).parent / 'configs' / 'config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def register_agent(self, name: str, agent_instance):
        self.agents[name] = agent_instance
        self.logger.info(f"Agent registered: {name}")
    
    def start_agent(self, name: str):
        if name not in self.agents:
            self.logger.error(f"Agent not found: {name}")
            return False
        
        if name in self.agent_threads and self.agent_threads[name].is_alive():
            self.logger.warning(f"Agent already running: {name}")
            return False
        
        agent = self.agents[name]
        thread = threading.Thread(target=agent.start, name=name, daemon=True)
        thread.start()
        
        self.agent_threads[name] = thread
        self.logger.info(f"Agent started: {name}")
        return True
    
    def stop_agent(self, name: str):
        if name not in self.agents:
            self.logger.error(f"Agent not found: {name}")
            return False
        
        agent = self.agents[name]
        agent.stop()
        
        if name in self.agent_threads:
            self.agent_threads[name].join(timeout=5)
        
        self.logger.info(f"Agent stopped: {name}")
        return True
    
    def start_all_agents(self):
        self.logger.info("Starting all enabled agents...")
        
        agents_config = self.config.get('agents', {})
        started_count = 0
        
        for agent_name, agent_config in agents_config.items():
            if agent_config.get('enabled', False) and agent_name in self.agents:
                if self.start_agent(agent_name):
                    started_count += 1
                time.sleep(0.5)
        
        self.logger.info(f"Started {started_count} agents")
        return started_count
    
    def stop_all_agents(self):
        self.logger.info("Stopping all agents...")
        
        for agent_name in list(self.agents.keys()):
            self.stop_agent(agent_name)
        
        self.logger.info("All agents stopped")
    
    def get_agent_status(self, name: str) -> Dict:
        if name not in self.agents:
            return {'status': 'not_found'}
        
        is_running = name in self.agent_threads and self.agent_threads[name].is_alive()
        
        return {
            'status': 'running' if is_running else 'stopped',
            'name': name,
            'thread_alive': is_running
        }
    
    def get_all_status(self) -> Dict:
        status = {}
        for agent_name in self.agents.keys():
            status[agent_name] = self.get_agent_status(agent_name)
        return status


if __name__ == "__main__":
    manager = AgentManager()
    print("✓ Agent Manager initialized")
