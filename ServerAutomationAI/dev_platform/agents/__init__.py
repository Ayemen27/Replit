"""AI Development Agents"""

from .base_agent import BaseAgent
from .planner_agent import PlannerAgent, get_planner_agent
from .code_executor_agent import CodeExecutorAgent
from .qa_test_agent import QATestAgent
from .ops_coordinator_agent import OpsCoordinatorAgent

# Singleton instances
_code_executor_instance = None
_qa_test_instance = None
_ops_coordinator_instance = None


def get_code_executor_agent():
    """Get singleton CodeExecutorAgent instance"""
    global _code_executor_instance
    if _code_executor_instance is None:
        _code_executor_instance = CodeExecutorAgent()
    return _code_executor_instance


def get_qa_test_agent():
    """Get singleton QATestAgent instance"""
    global _qa_test_instance
    if _qa_test_instance is None:
        _qa_test_instance = QATestAgent()
    return _qa_test_instance


def get_ops_coordinator_agent():
    """Get singleton OpsCoordinatorAgent instance"""
    global _ops_coordinator_instance
    if _ops_coordinator_instance is None:
        _ops_coordinator_instance = OpsCoordinatorAgent()
    return _ops_coordinator_instance


__all__ = [
    "BaseAgent",
    "PlannerAgent",
    "get_planner_agent",
    "CodeExecutorAgent",
    "get_code_executor_agent",
    "QATestAgent",
    "get_qa_test_agent",
    "OpsCoordinatorAgent",
    "get_ops_coordinator_agent"
]
