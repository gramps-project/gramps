#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006 Donald N. Allingham
# Copyright (C)      2010 Rob G. Healey <robhealey1@gmail.com>
# Copyright (C)      2010 Jakim Friant
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

"Report Generation Framework"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
from ...const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
import os

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

# Report categories
from .. import (CATEGORY_TEXT, CATEGORY_DRAW, CATEGORY_CODE, CATEGORY_WEB,
                CATEGORY_BOOK, CATEGORY_GRAPHVIZ, CATEGORY_TREE)

standalone_categories = {
    CATEGORY_TEXT     : ("RepText", _("Text Reports")),
    CATEGORY_DRAW     : ("RepGraph", _("Graphical Reports")),
    CATEGORY_CODE     : ("RepCode", _("Code Generators")),
    CATEGORY_WEB      : ("RepWeb", _("Web Pages")),
    CATEGORY_BOOK     : ("RepBook", _("Books")),
    CATEGORY_GRAPHVIZ : ("Graphs", _("Graphs")),
    CATEGORY_TREE    : ("Trees", _("Trees")),
}
book_categories = {
    CATEGORY_TEXT : _("Text"),
    CATEGORY_DRAW : _("Graphics"),
}
