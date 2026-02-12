"""
Workflow System Base
Defines base classes and registry for workflows
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseWorkflow(ABC):
    """Base class for workflows"""
    
    name: str = "base_workflow"
    description: str = "Base workflow"
    agents_involved: List[str] = []
    
    @abstractmethod
    async def execute(self, dispatcher, params: Dict[str, Any]):
        """Execute the workflow"""
        pass


# Workflow registry
_workflows: Dict[str, BaseWorkflow] = {}


def register_workflow(workflow: BaseWorkflow):
    """Register a workflow"""
    _workflows[workflow.name] = workflow
    logger.info(f"[Workflows] Registered: {workflow.name}")


def get_workflow(name: str) -> Optional[BaseWorkflow]:
    """Get a workflow by name"""
    return _workflows.get(name)


def list_workflows() -> List[str]:
    """List all registered workflows"""
    return list(_workflows.keys())
