#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Brian Caudill
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

"""Shared launcher for the Grizard Data Merge flow."""

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
# GTK modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
LOG = logging.getLogger(__name__)


# ------------------------------------------------------------
#
# Grizard launcher helpers
#
# ------------------------------------------------------------
def _case_insensitive_pattern(extension: str) -> str:
    """
    Build a case-insensitive glob pattern for a file extension.
    """
    body = "".join(
        "[%s%s]" % (char.lower(), char.upper()) if char.isalpha() else char
        for char in extension
    )
    return "*.%s" % body


def build_source_file_filters() -> list[Gtk.FileFilter]:
    """
    Build file filters covering every registered Gramps importer.
    """
    filters: list[Gtk.FileFilter] = []
    try:
        from gramps.gui.pluginmanager import GuiPluginManager

        plugins = GuiPluginManager.get_instance().get_import_plugins()
    except Exception:  # pylint: disable=broad-except
        plugins = []
    supported = Gtk.FileFilter()
    supported.set_name(_("All supported files"))
    seen: set[str] = set()
    for plugin in plugins:
        extension = str(getattr(plugin, "extension", "") or "").lower()
        if not extension or extension in seen:
            continue
        seen.add(extension)
        pattern = _case_insensitive_pattern(extension)
        supported.add_pattern(pattern)
        single = Gtk.FileFilter()
        single.set_name("%s (.%s)" % (plugin.name, extension))
        single.add_pattern(pattern)
        filters.append(single)
    if seen:
        filters.insert(0, supported)
    else:
        fallback = Gtk.FileFilter()
        fallback.set_name(_("Genealogy files"))
        for pattern in ("*.ged", "*.gramps", "*.xml", "*.gpkg", "*.csv"):
            fallback.add_pattern(pattern)
        filters.append(fallback)
    any_filter = Gtk.FileFilter()
    any_filter.set_name(_("All files"))
    any_filter.add_pattern("*")
    filters.append(any_filter)
    return filters


def ask_source_file(parent: Any, title: str | None = None) -> str | None:
    """
    Ask the user for a source genealogy file.
    """
    dialog = Gtk.FileChooserDialog(
        title=title or str(_("Select File to Compare")),
        transient_for=parent,
        action=Gtk.FileChooserAction.OPEN,
    )
    dialog.add_buttons(
        _("_Cancel"),
        Gtk.ResponseType.CANCEL,
        _("_OK"),
        Gtk.ResponseType.OK,
    )
    for file_filter in build_source_file_filters():
        dialog.add_filter(file_filter)
    response = dialog.run()
    path = dialog.get_filename()
    dialog.destroy()
    if response != Gtk.ResponseType.OK or not path:
        return None
    return str(path)


def load_source_grizard(db: Any, path: str) -> Any:
    """
    Connect and load a source file into a Grizard session.
    """
    import os

    from gramps.gen.grizard.gedcom import GedGrizard

    if not path or not os.path.isfile(path):
        raise ValueError(str(_("The selected file is missing.")))
    grizard = GedGrizard(db)
    if not grizard.run_step("connect", gedcom_path=path):
        raise ValueError(str(_("Could not read the selected file.")))
    try:
        grizard.run_step("load")
    except Exception as error:
        LOG.error("Failed to load source file for comparison: %s", error)
        raise RuntimeError(str(error)) from error
    return grizard


def open_compare_window(
    uistate: Any, dbstate: Any, grizard: Any, parent: Any = None
) -> Any:
    """
    Open the side-by-side comparison window for a loaded session.
    """
    from gramps.gui.grizard.grizardcompare import GrizardCompareWindow

    window = GrizardCompareWindow(uistate, dbstate, grizard, parent=parent)
    window.show()
    return window


def run_grizard_merge_flow(uistate: Any, dbstate: Any, parent: Any = None) -> bool:
    """
    Run the full flow: ask for a file, load it, open compare.

    Shared by the Family Trees menu entry and the Tools plugin.
    """
    from gramps.gui.dialog import ErrorDialog
    from gramps.gui.utils import ProgressMeter

    if parent is None:
        try:
            parent = uistate.window
        except Exception:  # pylint: disable=broad-except
            parent = None
    path = ask_source_file(parent)
    if not path:
        return False
    meter = ProgressMeter(
        str(_("Loading Data Merge")),
        str(_("Reading the selected file...")),
        parent=parent,
    )
    meter.set_pass(
        str(_("Reading the selected file...")),
        mode=ProgressMeter.MODE_ACTIVITY,
    )
    meter.step()
    try:
        grizard = load_source_grizard(dbstate.db, path)
    except (ValueError, RuntimeError) as error:
        meter.close()
        ErrorDialog(_("Load Failed"), str(error), parent=parent)
        return False
    meter.set_header(str(_("Building the comparison window...")))
    meter.step()
    try:
        open_compare_window(uistate, dbstate, grizard, parent=parent)
    finally:
        meter.close()
    return True
