#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025  The Gramps Project
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

"""
Prompt new users to import the bundled Example Family Tree on first startup.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import logging
import os
import shutil

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.cli.clidbman import CLIDbManager
from gramps.gen.config import config
from gramps.gen.const import DATA_DIR, DOC_DIR, USER_CACHE, GRAMPS_LOCALE as glocale
from gramps.gen.db.utils import make_database
from gramps.gen.plug import BasePluginManager

_ = glocale.translation.gettext

LOG = logging.getLogger(__name__)

_EXAMPLE_TREE_NAME = "Example Family Tree"
_EXAMPLE_DATA = os.path.join(DOC_DIR, "example", "gramps", "data.gramps")
_BUNDLED_TILES_DIR = os.path.join(DATA_DIR, "maps", "openstreetmap")


# -------------------------------------------------------------------------
#
# ExampleImportDialog
#
# -------------------------------------------------------------------------
class ExampleImportDialog(Gtk.Dialog):
    """
    One-time dialog offering to import the bundled Example Family Tree.
    """

    def __init__(self, parent_window: Gtk.Window | None) -> None:
        """
        Build the welcome/import prompt dialog.
        """
        super().__init__(
            title=_("Welcome to Gramps"),
            transient_for=parent_window,
            modal=True,
        )
        self.set_default_size(480, -1)
        self.set_border_width(12)

        content = self.get_content_area()
        content.set_spacing(12)

        label = Gtk.Label()
        label.set_markup(
            _(
                "Would you like to import the <b>Example Family Tree</b>?\n\n"
                "This sample data lets you explore Gramps features — people, "
                "events, places, media, and maps — before entering your own "
                "family information."
            )
        )
        label.set_line_wrap(True)
        label.set_xalign(0.0)
        content.pack_start(label, True, True, 0)

        self.dont_ask = Gtk.CheckButton.new_with_mnemonic(_("_Don't ask again"))
        content.pack_start(self.dont_ask, False, False, 0)

        self.add_button(_("_Skip"), Gtk.ResponseType.REJECT)
        btn = self.add_button(_("_Import Example Tree"), Gtk.ResponseType.ACCEPT)
        btn.get_style_context().add_class("suggested-action")
        self.set_default_response(Gtk.ResponseType.ACCEPT)

        content.show_all()


# -------------------------------------------------------------------------
#
# Public entry point
#
# -------------------------------------------------------------------------
def maybe_prompt_example_import(vm: object) -> None:
    """
    Show the example-import prompt if conditions are met.

    Conditions that suppress the prompt:
    - ``behavior.show-example-prompt`` config key is False.
    - A tree named "Example Family Tree" already exists.
    - The bundled ``data.gramps`` file cannot be found on disk.
    """
    if not config.get("behavior.show-example-prompt"):
        return

    if not os.path.isfile(_EXAMPLE_DATA):
        return

    dbman = CLIDbManager(vm.dbstate)
    if dbman.get_family_tree_path(_EXAMPLE_TREE_NAME) is not None:
        return

    parent = getattr(getattr(vm, "uistate", None), "window", None)
    dialog = ExampleImportDialog(parent)
    response = dialog.run()
    dont_ask = dialog.dont_ask.get_active()
    dialog.destroy()

    if dont_ask or response != Gtk.ResponseType.ACCEPT:
        # Only suppress future prompts when the user explicitly opts out.
        # Importing leaves the config key True; the tree-name check handles
        # suppression, so renaming the tree correctly re-triggers the prompt.
        config.set("behavior.show-example-prompt", False)
        return

    _do_import(vm, _EXAMPLE_DATA)


# -------------------------------------------------------------------------
#
# Private helpers
#
# -------------------------------------------------------------------------
def _do_import(vm: object, data_gramps_path: str) -> None:
    """
    Create "Example Family Tree", import data.gramps into it, seed map
    tiles, then open the new tree in the main window.
    """
    dbid = config.get("database.backend")
    dbman = CLIDbManager(vm.dbstate)

    try:
        new_path, _title = dbman.create_new_db_cli(_EXAMPLE_TREE_NAME, dbid=dbid)
    except Exception:
        LOG.exception("Failed to create Example Family Tree database directory.")
        return

    try:
        dbase = make_database(dbid)
        dbase.load(new_path)

        pmgr = BasePluginManager.get_instance()
        importer = None
        for plugin in pmgr.get_import_plugins():
            if plugin.get_extension() == "gramps":
                importer = plugin.get_import_function()
                break

        if importer is None:
            LOG.error("No .gramps XML importer found; cannot import example tree.")
            dbase.close()
            return

        from gramps.gui.user import User

        user = User(uistate=vm.uistate, dbstate=vm.dbstate)
        importer(dbase, data_gramps_path, user)
    except Exception:
        LOG.exception("Error while importing example data.")
        try:
            dbase.close()
        except Exception:
            pass
        return

    dbase.close()

    _seed_map_tiles()

    # Open the newly created tree in the main window.
    if vm.dbstate.is_open():
        vm.dbstate.db.close(user=vm.user)
    vm.db_loader.read_file(new_path)
    vm._post_load_newdb(new_path, "x-directory/normal", _EXAMPLE_TREE_NAME)


def _seed_map_tiles() -> None:
    """
    Copy the bundled zoom-0/1/2 OSM tiles into the user's tile cache.

    Only tiles that do not already exist are copied, so any previously
    cached (fresher) tile is left untouched.
    """
    if not os.path.isdir(_BUNDLED_TILES_DIR):
        return

    geography_path = config.get("geography.path")
    if not geography_path:
        geography_path = os.path.join(USER_CACHE, "maps")

    dest_dir = os.path.join(geography_path, "openstreetmap")

    for zoom in os.listdir(_BUNDLED_TILES_DIR):
        zoom_src = os.path.join(_BUNDLED_TILES_DIR, zoom)
        if not os.path.isdir(zoom_src):
            continue
        for x_col in os.listdir(zoom_src):
            col_src = os.path.join(zoom_src, x_col)
            if not os.path.isdir(col_src):
                continue
            col_dst = os.path.join(dest_dir, zoom, x_col)
            os.makedirs(col_dst, exist_ok=True)
            for tile_file in os.listdir(col_src):
                src_tile = os.path.join(col_src, tile_file)
                dst_tile = os.path.join(col_dst, tile_file)
                if not os.path.exists(dst_tile):
                    try:
                        shutil.copy2(src_tile, dst_tile)
                    except OSError:
                        LOG.warning("Could not copy tile %s to %s", src_tile, dst_tile)
