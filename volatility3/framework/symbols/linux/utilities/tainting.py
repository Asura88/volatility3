from volatility3 import framework
from volatility3.framework import interfaces
from volatility3.framework.symbols.linux.utilities import LinuxUtilityInterface
from volatility3.framework.constants import linux as linux_constants
from typing import List, Optional


class Tainting(LinuxUtilityInterface):
    """Tainted kernel and modules parsing capabilities.

    Relevant Linux kernel functions:
        - modules: module_flags_taint
        - kernel: print_tainted
    """

    _version = (1, 0, 0)
    _required_framework_version = (2, 16, 0)

    framework.require_interface_version(*_required_framework_version)

    def __init__(
        self,
        context: interfaces.context.ContextInterface,
        kernel_module_name: str,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._kernel = context.modules[kernel_module_name]

    @property
    def _kernel_taint_flags_list(
        self,
    ) -> Optional[List[interfaces.objects.ObjectInterface]]:
        if self._kernel.has_symbol("taint_flags"):
            return list(self._kernel.object_from_symbol("taint_flags"))
        return None

    def _module_flags_taint_pre_4_10_rc1(
        self, taints: int, is_module: bool = False
    ) -> str:
        """Convert the module's taints value to a 1-1 character mapping.
        Relies on statically defined taints mappings in the framework.

        Args:
            taints: The taints value, represented by an integer
            is_module: Indicates if the taints value is associated with a built-in/LKM module

        Returns:
            The raw taints string.
        """
        taints_string = ""
        for char, taint_flag in linux_constants.TAINT_FLAGS.items():
            if is_module and not taint_flag.module:
                continue

            if taints & taint_flag.shift:
                taints_string += char

        return taints_string

    def _module_flags_taint_post_4_10_rc1(
        self, taints: int, is_module: bool = False
    ) -> str:
        """Convert the module's taints value to a 1-1 character mapping.
        Relies on kernel symbol embedded taints definitions.

            struct taint_flag {
                char c_true;		/* character printed when tainted */
                char c_false;		/* character printed when not tainted */
                bool module;		/* also show as a per-module taint flag */
            };

        Args:
            taints: The taints value, represented by an integer
            is_module: Indicates if the taints value is associated with a built-in/LKM module

        Returns:
            The raw taints string.
        """
        taints_string = ""
        for taint_bit, taint_flag in enumerate(self._kernel_taint_flags_list):
            if is_module and not taint_flag.module:
                continue
            c_true = chr(taint_flag.c_true)
            c_false = chr(taint_flag.c_false)
            if taints & (1 << taint_bit):
                taints_string += c_true
            elif c_false != " ":
                taints_string += c_false

        return taints_string

    def get_taints_as_plain_string(self, taints: int, is_module: bool = False) -> str:
        """Convert the taints value to a 1-1 character mapping.

        Args:
            taints: The taints value, represented by an integer
            is_module: Indicates if the taints value is associated with a built-in/LKM module
        Returns:
            The raw taints string.

        Documentation:
            - module_flags_taint kernel function
        """

        if self._kernel_taint_flags_list:
            return self._module_flags_taint_post_4_10_rc1(taints, is_module)
        return self._module_flags_taint_pre_4_10_rc1(taints, is_module)

    def get_taints_parsed(self, taints: int, is_module: bool = False) -> List[str]:
        """Convert the taints string to a 1-1 descriptor mapping.

        Args:
            taints: The taints value, represented by an integer
            is_module: Indicates if the taints value is associated with a built-in/LKM module

        Returns:
            A comprehensive (user-friendly) taint descriptor list.

        Documentation:
            - module_flags_taint kernel function
        """
        comprehensive_taints = []
        for character in self.get_taints_as_plain_string(taints, is_module):
            taint_flag = linux_constants.TAINT_FLAGS.get(character)
            if not taint_flag:
                comprehensive_taints.append(f"<UNKNOWN_TAINT_CHAR_{character}>")
            elif taint_flag.when_present:
                comprehensive_taints.append(taint_flag.desc)

        return comprehensive_taints
