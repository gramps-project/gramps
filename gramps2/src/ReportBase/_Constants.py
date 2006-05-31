#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"Report Generation Framework"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

# Modes for generating reports
MODE_GUI = 1    # Standalone report using GUI
MODE_BKI = 2    # Book Item interface using GUI
MODE_CLI = 4    # Command line interface (CLI)

# Report categories
CATEGORY_TEXT = 0
CATEGORY_DRAW = 1
CATEGORY_CODE = 2
CATEGORY_WEB  = 3
CATEGORY_VIEW = 4
CATEGORY_BOOK = 5

standalone_categories = {
    CATEGORY_TEXT : _("Text Reports"),
    CATEGORY_DRAW : _("Graphical Reports"),
    CATEGORY_CODE : _("Code Generators"),
    CATEGORY_WEB  : _("Web Page"),
    CATEGORY_VIEW : _("View"),
    CATEGORY_BOOK : _("Books"),
}

book_categories = {
    CATEGORY_TEXT : _("Text"),
    CATEGORY_DRAW : _("Graphics"),
}
