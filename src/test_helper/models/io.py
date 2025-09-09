"""Input/Output models for interfaces (test_helper)."""

from pydantic import BaseModel, Field


class WelcomeMessage(BaseModel):
    """Welcome message model for CLI interface."""

    message: str = Field(
        default="Welcome to Test Helper!",
        description="The welcome message to display",
    )
    hint: str = Field(
        default="Type --help for more information",
        description="Hint message for users",
    )
