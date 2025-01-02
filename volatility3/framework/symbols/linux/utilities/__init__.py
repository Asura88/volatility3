from volatility3 import framework
from volatility3.framework import interfaces


class LinuxUtilityInterface(interfaces.configuration.VersionableInterface):
    """Class with multiple useful Linux functions surrounding a specific piece of functionality."""

    _version = (2, 1, 1)
    _required_framework_version = (2, 0, 0)

    framework.require_interface_version(*_required_framework_version)
