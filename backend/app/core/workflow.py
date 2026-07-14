from abc import ABC, abstractmethod
from typing import Any, Dict, List
from app.exceptions.service import WorkflowException
import logging

logger = logging.getLogger(__name__)

class WorkflowContext:
    """Shared state passed between steps in a workflow."""
    def __init__(self, **kwargs):
        self.state: Dict[str, Any] = {}
        for key, value in kwargs.items():
            self.set(key, value)

    def set(self, key: str, value: Any):
        self.state[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)

class WorkflowStep(ABC):
    """Abstract base class for a step in a workflow."""
    
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    async def execute(self, context: WorkflowContext) -> None:
        """Executes the step."""
        pass

    @abstractmethod
    async def compensate(self, context: WorkflowContext) -> None:
        """
        Rolls back the step if a subsequent step fails. 
        Implement this for distributed transactions or side-effects outside the DB.
        """
        pass

class WorkflowOrchestrator:
    """
    Coordinates execution of multiple workflow steps.
    If a step fails, it executes compensate() on all previously succeeded steps
    in reverse order (Saga pattern).
    """
    def __init__(self, name: str):
        self.name = name
        self.steps: List[WorkflowStep] = []

    def add_step(self, step: WorkflowStep) -> 'WorkflowOrchestrator':
        self.steps.append(step)
        return self

    async def execute(self, context: WorkflowContext) -> None:
        """Executes the workflow. Rolls back on failure."""
        executed_steps: List[WorkflowStep] = []

        logger.info(f"Starting workflow: {self.name}")
        
        for step in self.steps:
            logger.info(f"Workflow {self.name}: Executing step {step.get_name()}")
            try:
                await step.execute(context)
                executed_steps.append(step)
            except Exception as e:
                logger.error(f"Workflow {self.name}: Step {step.get_name()} failed. Error: {str(e)}")
                await self._compensate(executed_steps, context)
                raise WorkflowException(
                    f"Workflow '{self.name}' failed at step '{step.get_name()}': {str(e)}",
                    details={"failed_step": step.get_name()}
                ) from e
                
        logger.info(f"Workflow {self.name} completed successfully.")

    async def _compensate(self, executed_steps: List[WorkflowStep], context: WorkflowContext) -> None:
        """Runs compensation on executed steps in reverse order."""
        logger.info(f"Workflow {self.name}: Starting compensation...")
        for step in reversed(executed_steps):
            logger.info(f"Workflow {self.name}: Compensating step {step.get_name()}")
            try:
                await step.compensate(context)
            except Exception as e:
                # Log but do not swallow completely if it's critical, 
                # but typically compensation failures are logged for manual intervention.
                logger.error(f"Workflow {self.name}: Compensation failed for step {step.get_name()}: {str(e)}", exc_info=True)
