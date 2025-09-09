"""Type definitions for test_helper."""

from enum import Enum


class InterfaceType(str, Enum):
    """Available interface types."""

    CLI = "cli"
    RESTAPI = "restapi"
