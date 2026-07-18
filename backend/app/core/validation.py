from abc import ABC, abstractmethod
from typing import Any, Dict, List
from app.exceptions.service import ValidationException

class ValidationError:
    """Represents a single validation error."""
    def __init__(self, field: str, message: str, code: str):
        self.field = field
        self.message = message
        self.code = code

    def dict(self) -> Dict[str, str]:
        return {"field": self.field, "message": self.message, "code": self.code}

class Validator(ABC):
    """Abstract base class for all validators."""
    @abstractmethod
    async def validate(self, context: Any) -> List[ValidationError]:
        """
        Validates the given context.
        Returns a list of ValidationErrors if validation fails, or an empty list if successful.
        """
        pass

class ValidationPipeline:
    """
    Executes a series of validators against a given context.
    Collects all errors before throwing, allowing users to see multiple issues at once.
    """
    def __init__(self, validators: List[Validator]):
        self.validators = validators

    async def execute(self, context: Any) -> None:
        """
        Executes all validators.
        Raises ValidationException if any errors are found.
        """
        errors: List[ValidationError] = []
        for validator in self.validators:
            result = await validator.validate(context)
            if result:
                errors.extend(result)

        if errors:
            raise ValidationException(
                message="Validation failed",
                details={"errors": [e.dict() for e in errors]}
            )
