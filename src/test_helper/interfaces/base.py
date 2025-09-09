"""Base interface class for all interfaces (test_helper)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from test_helper.base import BaseComponent


class BaseInterface(ABC, BaseComponent):
    """Abstract base class for all interfaces."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the interface.

        Returns:
            str: The interface name

        """

    @abstractmethod
    def run(self) -> None:
        """Run the interface.

        This method should contain the main logic for starting
        and running the interface.
        """

    @abstractmethod
    def create_project(self, name: str, url: str, **kwargs: Any) -> dict[str, Any]:
        """Create a new test project.

        Args:
            name: Project name
            url: Target application URL
            **kwargs: Additional configuration

        Returns:
            Project data

        """

    @abstractmethod
    def list_projects(self, **kwargs: Any) -> list[dict[str, Any]]:
        """List test projects.

        Args:
            **kwargs: Filter and pagination options

        Returns:
            List of projects

        """

    @abstractmethod
    def get_project(self, project_id: str) -> dict[str, Any] | None:
        """Get project details.

        Args:
            project_id: Project ID

        Returns:
            Project data or None if not found

        """

    @abstractmethod
    def update_project(self, project_id: str, **kwargs: Any) -> dict[str, Any]:
        """Update a project.

        Args:
            project_id: Project ID
            **kwargs: Fields to update

        Returns:
            Updated project data

        """

    @abstractmethod
    def delete_project(self, project_id: str) -> bool:
        """Delete a project.

        Args:
            project_id: Project ID

        Returns:
            Success status

        """
