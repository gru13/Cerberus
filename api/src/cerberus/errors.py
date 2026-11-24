"""Intent: Define the base error type that every Cerberus error extends.

Why: One error tree gives stable codes, safe messages, and one HTTP mapping (story 8.1.3).
"""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict

type DetailValue = str | int | float | bool | None


class ErrorPayload(BaseModel):
    """Serializable form of a Cerberus error for API responses and logs."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    message: str
    details: dict[str, DetailValue]


class CerberusError(Exception):
    """Base class for every error that Cerberus code raises.

    Functional: Subclasses name one failure; callers catch by class, clients read `code`.
    Technical: `code`, `message`, and `http_status` are class constants; variable data goes in
        `details` so that messages stay fixed STE100 sentences without user data.
    Invariants: `code` is a dotted name; `message` is one STE100 sentence; details hold no secrets.
    """

    code: ClassVar[str] = "cerberus.error"
    message: ClassVar[str] = "An error occurs in Cerberus."
    http_status: ClassVar[int] = 500

    def __init__(self, *, details: dict[str, DetailValue] | None = None) -> None:
        """Create the error with optional safe details.

        Functional: Stores context values that help a person or client see what failed.
        Technical: Copies `details` so later changes by the caller do not alter the error.
        """
        super().__init__(self.message)
        self.details: dict[str, DetailValue] = dict(details or {})

    def to_payload(self) -> ErrorPayload:
        """Return the error as a Pydantic payload."""
        return ErrorPayload(code=self.code, message=self.message, details=self.details)
