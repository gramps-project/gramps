#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

import TextDoc
import gtk
import GrampsCfg

from intl import gettext
_ = gettext

paper_sizes = [
    TextDoc.PaperStyle("Letter",27.94,21.59),
    TextDoc.PaperStyle("Legal",35.56,21.59),
    TextDoc.PaperStyle("A3",42.0,29.7),
    TextDoc.PaperStyle("A4",29.7,21.0),
    TextDoc.PaperStyle("A5",21.0,14.8),
    TextDoc.PaperStyle("B4",35.3,25.0),
    TextDoc.PaperStyle("B6",17.6,12.5),
    TextDoc.PaperStyle("C4",32.4,22.9),
    TextDoc.PaperStyle("C5",22.9,16.2),
    TextDoc.PaperStyle("C6",16.2,11.4)
    ]

def make_paper_menu(main_menu):

    index = 0
    myMenu = gtk.GtkMenu()
    for paper in paper_sizes:
        name = paper.get_name()
        menuitem = gtk.GtkMenuItem(name)
        menuitem.set_data("i",paper)
        menuitem.show()
        myMenu.append(menuitem)
        if name == GrampsCfg.paper_preference:
            myMenu.set_active(index)
        index = index + 1
    main_menu.set_menu(myMenu)

def make_orientation_menu(main_menu):

    myMenu = gtk.GtkMenu()
    menuitem = gtk.GtkMenuItem(_("Portrait"))
    menuitem.set_data("i",TextDoc.PAPER_PORTRAIT)
    menuitem.show()
    myMenu.append(menuitem)

    menuitem = gtk.GtkMenuItem(_("Landscape"))
    menuitem.set_data("i",TextDoc.PAPER_LANDSCAPE)
    menuitem.show()
    myMenu.append(menuitem)

    main_menu.set_menu(myMenu)

