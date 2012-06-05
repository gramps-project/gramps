#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010        Nick Hall
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
"""
Tag editing module for Gramps. 
"""
#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gen.ggettext import sgettext as _
from gui.managedwindow import ManagedWindow
import const
import GrampsDisplay
from ListModel import ListModel, TOGGLE

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = '%s_-_Entering_and_Editing_Data:_Detailed_-_part_3' % \
                                                        const.URL_MANUAL_PAGE
WIKI_HELP_SEC = _('manual|Tags')

#-------------------------------------------------------------------------
#
# TagEditor
#
#-------------------------------------------------------------------------
class TagEditor(ManagedWindow):
    """
    Dialog to allow the user to edit a list of tags.
    """

    def __init__(self, tag_list, full_list, uistate, track):
        """
        Initiate and display the dialog.
        """
        ManagedWindow.__init__(self, uistate, track, self)

        self.namemodel = None
        top = self._create_dialog()
        self.set_window(top, None, _('Tag selection'))            

        for tag in full_list:
            self.namemodel.add([tag[0], tag in tag_list, tag[1]])
        self.namemodel.connect_model()

        # The dialog is modal.  We don't want to have several open dialogs of
        # this type, since then the user will loose track of which is which.
        self.return_list = None
        self.show()

        while True:
            response = self.window.run()
            if response == gtk.RESPONSE_HELP:
                GrampsDisplay.help(webpage=WIKI_HELP_PAGE,
                                   section=WIKI_HELP_SEC)
            elif response == gtk.RESPONSE_DELETE_EVENT:
                break
            else:
                if response == gtk.RESPONSE_OK:
                    self.return_list = [(row[0], row[2])
                                        for row in self.namemodel.model
                                        if row[1]]
                self.close()
                break

    def _create_dialog(self):
        """
        Create a dialog box to select tags.
        """
        # pylint: disable-msg=E1101
        title = _("%(title)s - Gramps") % {'title': _("Edit Tags")}
        top = gtk.Dialog(title)
        top.set_default_size(360, 400)
        top.set_modal(True)
        top.set_has_separator(False)
        top.vbox.set_spacing(5)

        columns = [('', -1, 300),
                   (' ', -1, 25, TOGGLE, True, None),
                   (_('Tag'), -1, 300)]
        view = gtk.TreeView()
        self.namemodel = ListModel(view, columns)

        slist = gtk.ScrolledWindow()
        slist.add_with_viewport(view)
        slist.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        top.vbox.pack_start(slist, 1, 1, 5)
        
        top.add_button(gtk.STOCK_HELP, gtk.RESPONSE_HELP)
        top.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        top.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        top.show_all()
        return top

    def build_menu_names(self, obj):
        """
        Define the menu entry for the ManagedWindows.
        """
        return (_("Tag selection"), None)
