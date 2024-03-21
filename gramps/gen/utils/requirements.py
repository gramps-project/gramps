#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2023       Nick Hall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
from importlib.util import find_spec

# -------------------------------------------------------------------------
#
# GTK modules
#
# -------------------------------------------------------------------------
import gi

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .file import search_for
from ..config import config
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# Requirements
#
# -------------------------------------------------------------------------
class Requirements:
    def __init__(self):
        self.mod_list = []
        self.gi_list = []
        self.exe_list = []

    def check_mod(self, module):
        """
        Check to see if a given module is available.
        """
        if module in self.mod_list:
            return True
        if find_spec(module) is not None:
            self.mod_list.append(module)
            return True
        else:
            return False

    def check_gi(self, module_spec):
        """
        Check to see if a GObject introspection module is available.
        """
        if module_spec in self.gi_list:
            return True

        if "," in module_spec[1]:
            for version in module_spec[1].split(","):
                if self._test_gi(module_spec[0], version.strip()):
                    self.gi_list.append(module_spec)
                    return True
        else:
            if self._test_gi(*module_spec):
                self.gi_list.append(module_spec)
                return True
        return False

    def _test_gi(self, module, version):
        """
        Test to see if a particular version of a module is available.
        """
        try:
            gi.require_version(module, version)
            return True
        except ValueError:
            return False

    def check_exe(self, executable):
        """
        Check to see if a given executable is available.
        """
        if executable in self.exe_list:
            return True
        if search_for(executable) or search_for(executable + ".exe"):
            self.exe_list.append(executable)
            return True
        else:
            return False

    def check(self, gi_list, exe_list, mod_list, install=False):
        """
        Check lists of requirements.
        """
        for module_spec in gi_list:
            if not self.check_gi(module_spec):
                return False
        for executable in exe_list:
            if not self.check_exe(executable):
                return False
        if install and config.get("behavior.addons-allow-install"):
            return True
        for module in mod_list:
            if not self.check_mod(module):
                return False
        return True

    def check_addon(self, addon, install=False):
        """
        Check the requirements of a given addon.
        """
        return self.check(
            addon.get("rg", []), addon.get("re", []), addon.get("rm", []), install
        )

    def check_plugin(self, plugin):
        """
        Check the requirements of a given plugin.
        """
        return self.check(plugin.requires_gi, plugin.requires_exe, plugin.requires_mod)

    def install(self, addon):
        """
        Return a list of modules required to be installed.
        """
        install_list = []
        if "rm" in addon:
            for module in addon.get("rm"):
                if not self.check_mod(module):
                    install_list.append(module)
        return install_list

    def info(self, addon):
        """
        Provide the requirements status of a given addon.
        """
        info = []
        if "rm" in addon:
            info.append(_("Python modules"))
            table = []
            for module in addon.get("rm"):
                result = self.check_mod(module)
                table.append([module, tick_cross(result)])
            info.append(table)
        if "rg" in addon:
            info.append(_("GObject introspection modules"))
            table = []
            for module_spec in addon.get("rg"):
                result = self.check_gi(module_spec)
                table.append([" ".join(module_spec), tick_cross(result)])
            info.append(table)
        if "re" in addon:
            info.append(_("Executables"))
            table = []
            for executable in addon.get("re"):
                result = self.check_exe(executable)
                table.append([executable, tick_cross(result)])
            info.append(table)
        return info


def tick_cross(value):
    """
    Return a tick for True or a cross for False
    """
    return "\N{CHECK MARK}" if value else "\N{CROSS MARK}"
