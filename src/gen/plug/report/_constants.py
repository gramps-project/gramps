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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id: _Constants.py 15146 2010-04-15 14:37:18Z robhealey1 $

"Report Generation Framework"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _
import os

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
import const

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
    # id, user selectable, translated_name, fullpath, navigation target name, additional files
    # "default" is used as default
    ["Basic-Ash",     1, _("Basic-Ash"),         os.path.join(const.DATA_DIR, 'Web_Basic-Ash.css'),     None, []],
    ["Basic-Blue",    1, _("Basic-Blue"),        os.path.join(const.DATA_DIR, 'Web_Basic-Blue.css'),    "Web_Navigation-Menus.css", []],
    ["Basic-Cypress", 1, _("Basic-Cypress"),     os.path.join(const.DATA_DIR, 'Web_Basic-Cypress.css'), None, []],
    ["Basic-Lilac",   1, _("Basic-Lilac"),       os.path.join(const.DATA_DIR, 'Web_Basic-Lilac.css'),   None, []],
    ["Basic-Peach",   1, _("Basic-Peach"),       os.path.join(const.DATA_DIR, 'Web_Basic-Peach.css'),   None, []],
    ["Basic-Spruce",  1, _("Basic-Spruce"),      os.path.join(const.DATA_DIR, 'Web_Basic-Spruce.css'),  None, []],
    ["Mainz",         1, _("Mainz"),             os.path.join(const.DATA_DIR, 'Web_Mainz.css'),         None, 
     [os.path.join(const.IMAGE_DIR, "Web_Mainz_Bkgd.png"), 
      os.path.join(const.IMAGE_DIR, "Web_Mainz_Header.png"), 
      os.path.join(const.IMAGE_DIR, "Web_Mainz_Mid.png"), 
      os.path.join(const.IMAGE_DIR, "Web_Mainz_MidLight.png")]],
    ["Nebraska",      1, _("Nebraska"),          os.path.join(const.DATA_DIR, 'Web_Nebraska.css'),      None, []],
    ["Visually Impaired", 1, _("Visually Impaired"), os.path.join(const.DATA_DIR, 'Web_Visually.css'),  "Web_Navigation-Menus.css", []],
    ["No style sheet",1, _("No style sheet"),    '',                                                    None, []],
    ["behaviour",     0, "Behaviour",            os.path.join(const.DATA_DIR, 'behaviour.css'),          None, []],
    ["default",       0, _("Basic-Ash"),         os.path.join(const.DATA_DIR, 'Web_Basic-Ash.css'),     None, []],
    ["Print-Default", 0, "Print-Default",        os.path.join(const.DATA_DIR, 'Web_Print-Default.css'), None, []],
    ["Navigation-Vertical", 0, "Navigation-Vertical", os.path.join(const.DATA_DIR, 'Web_Navigation-Vertical.css'), None, []],
    ["Navigation-Horizontal", 0, "Navigation-Horizontal", os.path.join(const.DATA_DIR, 'Web_Navigation-Horizontal.css'), None, []],
    ]
