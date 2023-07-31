#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010 Nick Hall
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
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

MODULE_VERSION = "5.2"

# ------------------------------------------------------------------------
#
# Register default sidebars
#
# ------------------------------------------------------------------------

register(
    SIDEBAR,
    id="categorysidebar",
    name=_("Category Sidebar"),
    description=_("A sidebar to allow the selection of view categories"),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="categorysidebar.py",
    authors=["Nick Hall"],
    authors_email=["nick__hall@hotmail.com"],
    sidebarclass="CategorySidebar",
    menu_label=_("Category"),
    order=START,
)

register(
    SIDEBAR,
    id="dropdownsidebar",
    name=_("Drop-down Sidebar"),
    description=_("Selection of categories and views from drop-down lists"),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="dropdownsidebar.py",
    authors=["Nick Hall"],
    authors_email=["nick__hall@hotmail.com"],
    sidebarclass="DropdownSidebar",
    menu_label=_("Drop-Down"),
    order=END,
)

register(
    SIDEBAR,
    id="expandersidebar",
    name=_("Expander Sidebar"),
    description=_("Selection of views from lists with expanders"),
    version="1.0",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="expandersidebar.py",
    authors=["Nick Hall"],
    authors_email=["nick__hall@hotmail.com"],
    sidebarclass="ExpanderSidebar",
    menu_label=_("Expander"),
    order=END,
)
