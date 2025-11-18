"""
Workflow Tools
Run and manage workflows
"""

import time
from typing import Dict, Optional
import logging
from .code_executor import execute_bash

logger = logging.getLogger(__name__)


class WorkflowTools:
    """
    Workflow management toolkit
    
    Tools:
    - run_workflow: Execute predefined workflows
    """
    
    def __init__(self):
        # Predefined workflows
        self.workflows = {
            "test": {
                "description": "Run all tests",
                "commands": [
                    "pytest tests/ -v"
                ]
            },
            "lint": {
                "description": "Run code linting",
                "commands": [
                    "find . -name '*.py' -not -path './venv/*' | xargs pylint || true",
                    "flake8 . --exclude=venv,__pycache__ || true"
                ]
            },
            "deploy": {
                "description": "Deploy to production",
                "commands": [
                    "git status",
                    "python3 bridge_tool/cli.py push"
                ]
            },
            "backup": {
                "description": "Create backup",
                "commands": [
                    "python3 src/setup/backup_database.py"
                ]
            },
            "install": {
                "description": "Install dependencies",
                "commands": [
                    "pip install -r requirements.txt"
                ]
            }
        }
    
    def run_workflow(
        self,
        name: str,
        custom_command: Optional[str] = None,
        timeout: int = 300
    ) -> Dict:
        """
        Run a predefined workflow or custom command
        
        Args:
            name: Workflow name (test, lint, deploy, backup, install, custom)
            custom_command: Custom command to run (if name='custom')
            timeout: Timeout in seconds (default: 300)
        
        Returns:
            Dict with 'success', 'results', and optional 'error'
        """
        try:
            # Handle custom workflow
            if name == "custom":
                if not custom_command:
                    return {
                        "success": False,
                        "error": "custom_command is required for custom workflows"
                    }
                
                logger.info(f"Running custom workflow: {custom_command[:50]}...")
                result = execute_bash(custom_command, timeout=timeout)
                
                return {
                    "success": result["success"],
                    "workflow": "custom",
                    "command": custom_command,
                    "result": result
                }
            
            # Check if workflow exists
            if name not in self.workflows:
                return {
                    "success": False,
                    "error": f"Workflow not found: {name}",
                    "available_workflows": list(self.workflows.keys())
                }
            
            workflow = self.workflows[name]
            logger.info(f"Running workflow: {name} - {workflow['description']}")
            
            results = []
            all_success = True
            
            start_time = time.time()
            
            # Execute each command in the workflow
            for i, command in enumerate(workflow["commands"], 1):
                logger.info(f"[{i}/{len(workflow['commands'])}] Executing: {command}")
                
                result = execute_bash(command, timeout=timeout)
                results.append({
                    "step": i,
                    "command": command,
                    "success": result["success"],
                    "stdout": result.get("stdout", ""),
                    "stderr": result.get("stderr", ""),
                    "returncode": result.get("returncode")
                })
                
                if not result["success"]:
                    all_success = False
                    logger.error(f"Step {i} failed: {command}")
                    # Continue to next step (don't break)
            
            elapsed = time.time() - start_time
            
            return {
                "success": all_success,
                "workflow": name,
                "description": workflow["description"],
                "total_steps": len(workflow["commands"]),
                "successful_steps": sum(1 for r in results if r["success"]),
                "failed_steps": sum(1 for r in results if not r["success"]),
                "results": results,
                "elapsed_time": round(elapsed, 2)
            }
        
        except Exception as e:
            logger.error(f"Error running workflow {name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "workflow": name
            }
    
    def list_workflows(self) -> Dict:
        """
        List all available workflows
        
        Returns:
            Dict with 'success' and 'workflows'
        """
        workflows_info = []
        
        for name, info in self.workflows.items():
            workflows_info.append({
                "name": name,
                "description": info["description"],
                "steps": len(info["commands"])
            })
        
        return {
            "success": True,
            "workflows": workflows_info,
            "total": len(self.workflows)
        }


# Convenience functions
_workflow_tools = WorkflowTools()

def run_workflow(
    name: str,
    custom_command: Optional[str] = None,
    timeout: int = 300
) -> Dict:
    """Run a workflow"""
    return _workflow_tools.run_workflow(name, custom_command, timeout)

def list_workflows() -> Dict:
    """List available workflows"""
    return _workflow_tools.list_workflows()
