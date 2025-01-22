from volatility3 import framework
from volatility3.framework import interfaces
from volatility3.framework.symbols.linux import extensions, LinuxUtilities
from typing import Iterable, Optional


class Modules(interfaces.configuration.VersionableInterface):
    """Kernel modules related utilities."""

    _version = (1, 0, 0)
    _required_framework_version = (2, 0, 0)

    framework.require_interface_version(*_required_framework_version)

    @staticmethod
    def module_lookup_by_address(
        context: interfaces.context.ContextInterface,
        layer_name: str,
        modules: Iterable[extensions.module],
        target_address: int,
    ) -> Optional[extensions.module]:
        """
        Determine if a target address lies in a module memory space.
        Returns the module where the provided address lies.

        Args:
            context: The context on which to operate
            layer_name: The name of the layer on which to operate
            modules: An iterable containing the modules to match the address against
            target_address: The address to check for a match
        """

        for module in modules:
            _, start, end = LinuxUtilities.mask_mods_list(
                context, layer_name, [module]
            )[0]
            if start <= target_address <= end:
                return module

        return None
