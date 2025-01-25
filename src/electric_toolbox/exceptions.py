"""Custom exceptions for the parsing module."""

from typing import Any, Dict


class ParsingError(Exception):
    """Custom exception for the parsing module."""

    def __init__(
        self,
        message: str,
        cause: Exception,
        context: Dict[str, Any] = {},
    ):
        """Custom exception for the parsing module.

        Args:
            message (str): Message describing the error.
            cause (Exception): The exception that caused the error.
            context (Dict[str, Any], optional): Additional Context. Defaults to {}.
        """
        self.message = message
        self.cause = cause
        self.context = context or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        """Returns a string representation of the exception."""
        details = f'ParsingError: {self.message}'
        if self.cause:
            details += f' -- Caused by: {type(self.cause).__name__}: {self.cause}'
        if self.context:
            details += ' -- Context:'
            for key, value in self.context.items():
                details += f' <|> {key}: {value}'
        return details
