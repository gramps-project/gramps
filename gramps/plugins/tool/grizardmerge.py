#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Kevin White
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""Tools/Family Tree Processing/Grizard Data Merge."""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations
import logging
from typing import Any

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gui.plug import tool

_ = glocale.translation.sgettext
LOG = logging.getLogger(__name__)


# ------------------------------------------------------------
#
# GrizardMergeToolOptions
#
# ------------------------------------------------------------
class GrizardMergeToolOptions(tool.ToolOptions):
    """Defines options and provides handling interface."""

    def __init__(self, name: str, person_id: str | None = None) -> None:
        """Initialize the options."""
        tool.ToolOptions.__init__(self, name, person_id)
        self.options_dict = {}
        self.options_help = {}


# ------------------------------------------------------------
#
# GrizardMergeTool
#
# ------------------------------------------------------------
class GrizardMergeTool(tool.Tool):
    """
    Launch the Grizard Data Merge flow.

    Thin wrapper around the shared launcher: ask for a source file,
    load it, and open the side-by-side compare window. Identical to
    the Family Trees menu entry.
    """

    def __init__(
        self,
        dbstate: Any,
        user: Any,
        options_class: Any,
        name: str,
        callback: Any = None,
    ) -> None:
        """Initialize the tool and run the shared merge flow."""
        uistate = user.uistate
        tool.Tool.__init__(self, dbstate, options_class, name)
        # When installed as a standalone addon, sibling modules live in the
        # addon directory, which Gramps removes from sys.path after import.
        # Re-add it so "from grizardlauncher import ..." keeps working here
        # and inside the sibling modules themselves.
        import os as _os
        import sys as _sys

        _addon_dir = _os.path.dirname(_os.path.abspath(__file__))
        if _addon_dir not in _sys.path:
            _sys.path.insert(0, _addon_dir)
        try:
            from grizardlauncher import run_grizard_merge_flow
        except ImportError:
            # Running from the source tree: fall back to the core location.
            from gramps.gui.grizard.grizardlauncher import (
                run_grizard_merge_flow,
            )

        run_grizard_merge_flow(uistate, dbstate, parent=uistate.window)
