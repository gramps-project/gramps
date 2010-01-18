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
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

# Report categories
from gen.plug import CATEGORY_TEXT, CATEGORY_DRAW, CATEGORY_CODE, CATEGORY_WEB,\
                     CATEGORY_BOOK, CATEGORY_GRAPHVIZ

standalone_categories = {
    CATEGORY_TEXT     : _("Text Reports"),
    CATEGORY_DRAW     : _("Graphical Reports"),
    CATEGORY_CODE     : _("Code Generators"),
    CATEGORY_WEB      : _("Web Pages"),
    CATEGORY_BOOK     : _("Books"),
    CATEGORY_GRAPHVIZ : _("Graphs"),
}

book_categories = {
    CATEGORY_TEXT : _("Text"),
    CATEGORY_DRAW : _("Graphics"),
}

#Common data for html reports
## TODO: move to a system where css files are registered
# This information defines the list of styles in the Web reports
# options dialog as well as the location of the corresponding
# stylesheets in src/data.

CSS_FILES = [
    # First is used as default selection.
    [_("Basic-Ash"),            'Web_Basic-Ash.css'],
    [_("Basic-Cypress"),        'Web_Basic-Cypress.css'],
    [_("Basic-Lilac"),          'Web_Basic-Lilac.css'],
    [_("Basic-Peach"),          'Web_Basic-Peach.css'],
    [_("Basic-Spruce"),         'Web_Basic-Spruce.css'],
    [_("Mainz"),                'Web_Mainz.css'],
    [_("Nebraska"),             'Web_Nebraska.css'],
    [_("Visually Impaired"),    'Web_Visually.css'],
    [_("No style sheet"),       ''],
    ]
