#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# Classes
#
#-------------------------------------------------------------------------
class GrampsTab(gtk.HBox):
    """
    This class provides the base level class for 'tabs', which are used to
    fill in notebook tabs for GRAMPS edit dialogs. Each tab returns a
    gtk container widget which can be inserted into a gtk.Notebook by the
    instantiating object.

    All tab classes should inherit from GrampsTab
    """

    def __init__(self, dbstate, uistate, track, name):
        """
        @param dbstate: The database state. Contains a reference to
        the database, along with other state information. The GrampsTab
        uses this to access the database and to pass to and created
        child windows (such as edit dialogs).
        @type dbstate: DbState
        @param uistate: The UI state. Used primarily to pass to any created
        subwindows.
        @type uistate: DisplayState
        @param track: The window tracking mechanism used to manage windows.
        This is only used to pass to generted child windows.
        @type track: list
        @param name: Notebook label name
        @type name: str/unicode
        """
        gtk.HBox.__init__(self)

        # store information to pass to child windows
        self.dbstate = dbstate
        self.uistate = uistate
        self.track = track
        self.changed = False
        
        # save name used for notebook label, and build the widget used
        # for the label
        
        self.tab_name = name
        self.label_container = self.build_label_widget()

        # build the interface
        self.share_btn = None
        self.build_interface()

    def get_selected(self):
        return None

    def is_empty(self):
        """
        Indicates if the tab contains any data. This is used to determine
        how the label should be displayed.
        """
        return True

    def build_label_widget(self):
        """
        Standard routine to build a widget. Does not need to be overridden
        by the derrived class. Creates an container that has the label and
        the icon in it.
        @returns: widget to be used for the notebook label.
        @rtype: gtk.HBox
        """
        hbox = gtk.HBox()
        icon = self.get_icon_name()

        if type(icon) == tuple:
            if icon[0] == 0:
                func = gtk.image_new_from_icon_name
            else:
                func = gtk.image_new_from_stock
            name = icon[1]
        else:
            func = gtk.image_new_from_stock
            name = icon
        
        self.tab_image = func(name, gtk.ICON_SIZE_MENU)
        self.label = gtk.Label(self.tab_name)
        hbox.pack_start(self.tab_image)
        hbox.set_spacing(6)
        hbox.add(self.label)
        hbox.show_all()
        return hbox

    def get_icon_name(self):
        """
        Provides the name of the registered stock icon to be used as the
        icon in the label. This is typically overridden by the derrived
        class to provide the new name.
        @returns: stock icon name
        @rtype: str
        """
        return gtk.STOCK_NEW

    def get_tab_widget(self):
        """
        Provides the widget to be used for the notebook tab label. A
        container class is provided, and the object may manipulate the
        child widgets contained in the container.
        @returns: gtk widget
        @rtype: gtk.HBox
        """
        return self.label_container

    def _set_label(self):
        """
        Updates the label based of if the tab contains information. Tabs
        without information will not have an icon, and the text will not
        be bold. Tabs that contain data will have their icon displayed and
        the label text will be in bold face.
        """
        if not self.is_empty():
            self.tab_image.show()
            self.label.set_text("<b>%s</b>" % self.tab_name)
            self.label.set_use_markup(True)
        else:
            self.tab_image.hide()
            self.label.set_text(self.tab_name)

    def build_interface(self):
        """
        Builds the interface for the derived class. This function should be
        overridden in the derived class. Since the classes are derrived from
        gtk.HBox, the self.pack_start, self.pack_end, and self.add functions
        can be used to add widgets to the interface.
        """
        pass
