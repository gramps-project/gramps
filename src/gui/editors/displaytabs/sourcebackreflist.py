#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2-11       Tim G L Lyons
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
# GRAMPS classes
#
#-------------------------------------------------------------------------
from backrefmodel import BackRefModel
from backreflist import BackRefList
from gui.widgets import SimpleButton

class SourceBackRefList(BackRefList):

    def __init__(self, dbstate, uistate, track, obj, callback=None):
        BackRefList.__init__(self, dbstate, uistate, track, obj, 
                             BackRefModel, callback=callback)

    def _create_buttons(self, share=False, move=False, jump=False, top_label=None):
        """
        SourceBackrefList inherits from BackrefList inherits from EmbeddedList
        inherits from ButtonTab
        _create_buttons is defined in ButtonTab, and overridden in BackRefList.
        But needs to be overriden here so that there is no edit button for
        References to Source, because they will all be citations,
        and the Citations will be displayed in the top part of the
        editcitation dialogue.

        Create a button box consisting of one button: Edit.
        This has to be created here because backreflist.py sets it sensitive 
        This button box is then not appended hbox (self).
        Method has signature of, and overrides create_buttons from _ButtonTab.py
        """
        self.edit_btn = SimpleButton(gtk.STOCK_EDIT, self.edit_button_clicked)
        self.edit_btn.set_tooltip_text(_('Edit reference'))

        hbox = gtk.HBox()
        hbox.set_spacing(6)
#        hbox.pack_start(self.edit_btn, False)
        hbox.show_all()
        self.pack_start(hbox, False)
        
        self.add_btn = None
        self.del_btn = None

        self.track_ref_for_deletion("edit_btn")
        self.track_ref_for_deletion("add_btn")
        self.track_ref_for_deletion("del_btn")

    def get_icon_name(self):
        return 'gramps-source'
