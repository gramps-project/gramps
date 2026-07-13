#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Doug Blank
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
Regenerate gramps/gui/keybinding_themes/Default.jsonl from a live Gramps
session.

The bundled "Default" theme file needs a real, running Gramps session to
regenerate accurately: most shortcuts are known statically at startup (see
ViewManager.__register_static_shortcuts), but each view's own ordinary
menu/toolbar actions (e.g. "win.NewTag", "win.SourceAdd") are only known
once that view has actually been built, which requires a real display for
GTK to construct real widgets and menu XML against. There is currently no
lighter-weight way to capture those labels.

This script boots the real UIManager/ViewManager stack (not the full
GrampsApplication -- that would auto-open the Family Tree manager dialog,
which we don't want here), visits every registered view once so all of
their actions register, then calls save_accels(only_changed=False) and
copies the result over the bundled Default.jsonl.

It runs against a throwaway, isolated GRAMPSHOME so it never reads or
writes a developer's real Gramps settings, and never loads any existing
accel/theme file, so the output reflects Gramps' true hard-coded defaults
rather than whatever the previous Default.jsonl happened to contain.

Requires a real X display, since GTK cannot resolve virtual modifiers
like <Primary> or build real widgets/menus without one:

    xvfb-run -a python3 scripts/regenerate_default_theme.py

Re-run this after adding, renaming, or removing a keyboard shortcut
anywhere in Gramps, then review the diff to gramps/gui/keybinding_themes/
Default.jsonl before committing.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import argparse
import os
import shutil
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUTPUT = os.path.join(
    REPO_ROOT, "gramps", "gui", "keybinding_themes", "Default.jsonl"
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help="file to overwrite with the regenerated theme (default: %(default)s)",
    )
    args = parser.parse_args()

    if not os.environ.get("DISPLAY"):
        sys.exit(
            "No DISPLAY set. This needs a real X display to build real "
            "widgets/menus and resolve modifiers like <Primary> correctly "
            "-- run it under Xvfb, e.g.:\n\n"
            "    xvfb-run -a python3 scripts/regenerate_default_theme.py"
        )

    os.environ.pop("GDK_BACKEND", None)
    os.environ.setdefault("GRAMPS_RESOURCES", os.path.join(REPO_ROOT, "build", "share"))

    # An isolated, throwaway profile: this must never read or write a
    # developer's real Gramps settings, and must never load an existing
    # accel/theme file, so the output reflects Gramps' true hard-coded
    # defaults rather than whatever a previous Default.jsonl contained.
    with tempfile.TemporaryDirectory(prefix="gramps-regen-home-") as gramps_home:
        os.environ["GRAMPSHOME"] = gramps_home
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            _generate(tmp_path)
            shutil.copyfile(tmp_path, args.output)
        finally:
            os.remove(tmp_path)

    print(f"Wrote {args.output}")


def _generate(output_path):
    """Build a live UIManager/ViewManager, visit every view once, and
    save every known shortcut (with label/category) to output_path."""
    sys.path.insert(0, REPO_ROOT)

    import gi

    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    from gramps.gen.config import config
    from gramps.gen.dbstate import DbState
    from gramps.gui.grampsgui import UIDEFAULT
    from gramps.gui.uimanager import UIManager
    from gramps.gui.viewmanager import ViewManager

    app = Gtk.Application(application_id="org.gramps_project.RegenerateDefaultTheme")
    app.register()

    app.uimanager = UIManager(app, UIDEFAULT)
    app.uimanager.update_menu(init=True)
    # Deliberately skip loading any existing gramps.jsonl/theme file here --
    # this run must only ever see Gramps' own hard-coded defaults.

    dbstate = DbState()
    view_manager = ViewManager(app, dbstate, config.get("interface.view-categories"))
    view_manager.init_interface()

    for cat_num, cat_views in enumerate(view_manager.views):
        for view_num in range(len(cat_views)):
            view_manager.goto_page(cat_num, view_num)

    view_manager.uimanager.save_accels(output_path, only_changed=False)


if __name__ == "__main__":
    main()
