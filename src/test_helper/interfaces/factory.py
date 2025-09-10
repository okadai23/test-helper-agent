"""Factory pattern implementation for creating interfaces (test_helper)."""

from test_helper.types import InterfaceType
from test_helper.utils.settings import get_interface_settings

from .base import BaseInterface
from .cli import CLIInterface


class InterfaceFactory:
    """Factory for creating interface instances."""

    def create(self, interface_type: InterfaceType) -> BaseInterface:
        """Create an interface instance based on the type.

        Args:
            interface_type: The type of interface to create

        Returns:
            BaseInterface: The created interface instance

        Raises:
            ValueError: If the interface type is unknown

        """
        if interface_type == InterfaceType.CLI:
            return CLIInterface()
        if interface_type == InterfaceType.RESTAPI:
            # RestAPI interface will be implemented later
            msg = "RestAPI interface is not yet implemented"
            raise NotImplementedError(msg)

        msg = f"Unknown interface type: {interface_type}"
        raise ValueError(msg)

    def create_from_settings(self) -> BaseInterface:
        """Create an interface instance from settings.

        Returns:
            BaseInterface: The created interface instance

        """
        settings = get_interface_settings()
        interface_type = InterfaceType(settings.interface_type)
        return self.create(interface_type)
