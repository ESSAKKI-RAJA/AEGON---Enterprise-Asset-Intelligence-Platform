from abc import ABC, abstractmethod
from typing import Any, Dict
from app.exceptions.service import BusinessRuleException

class RuleContext:
    """Provides context (data, services, dependencies) needed by a rule to execute."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class BusinessRule(ABC):
    """Abstract base class for all business rules."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Returns the identifier of the rule."""
        pass
        
    @abstractmethod
    def get_description(self) -> str:
        """Returns a human-readable description of the rule."""
        pass

    @abstractmethod
    async def evaluate(self, context: RuleContext) -> bool:
        """
        Evaluates the rule condition without applying any changes.
        Returns True if the rule conditions are met, False otherwise.
        """
        pass
        
    @abstractmethod
    async def execute(self, context: RuleContext) -> Any:
        """
        Executes the business rule logic, potentially mutating context or returning a value.
        Should raise BusinessRuleException if the rule evaluation fails.
        """
        pass

class BusinessRuleEngine:
    """Executes business rules and enforces enterprise business logic."""
    
    async def run(self, rule: BusinessRule, context: RuleContext) -> Any:
        """
        Runs a business rule against a context.
        First evaluates the condition, then executes the rule logic.
        """
        if not await rule.evaluate(context):
            raise BusinessRuleException(
                f"Business rule '{rule.get_name()}' evaluation failed: {rule.get_description()}",
                details={"rule": rule.get_name()}
            )
            
        return await rule.execute(context)
