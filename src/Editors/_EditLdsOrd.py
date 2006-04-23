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

# $Id: _EditAttribute.py 6248 2006-03-31 23:46:34Z dallingham $ 

"""
The EditLdsOrd module provides the EditLdsOrd class. This provides a
mechanism for the user to edit personal LDS information.
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision: 6248 $"

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import RelLib
import GrampsDisplay
import NameDisplay
import lds

from _EditSecondary import EditSecondary

from DisplayTabs import *
from GrampsWidgets import *

#-------------------------------------------------------------------------
#
# EditLdsOrd class
#
#-------------------------------------------------------------------------
class EditLdsOrd(EditSecondary):
    """
    Displays a dialog that allows the user to edit an attribute.
    """

    _data_map = {
        RelLib.LdsOrd.BAPTISM : [
            (_("<No Status>"), RelLib.LdsOrd.STATUS_NONE),
            (_("Child"), RelLib.LdsOrd.STATUS_CHILD),
            (_("Cleared"), RelLib.LdsOrd.STATUS_CLEARED),
            (_("Completed"), RelLib.LdsOrd.STATUS_COMPLETED),
            (_("Infant"), RelLib.LdsOrd.STATUS_INFANT),
            (_("Pre-1970"), RelLib.LdsOrd.STATUS_PRE_1970),
            (_("Qualified"), RelLib.LdsOrd.STATUS_QUALIFIED),
            (_("Stillborn"), RelLib.LdsOrd.STATUS_STILLBORN),
            (_("Submitted"), RelLib.LdsOrd.STATUS_SUBMITTED),
            (_("Uncleared"), RelLib.LdsOrd.STATUS_UNCLEARED),
            ],
        RelLib.LdsOrd.ENDOWMENT: [
            (_("<No Status>"), RelLib.LdsOrd.STATUS_NONE),
            (_("Child"), RelLib.LdsOrd.STATUS_CHILD),
            (_("Cleared"), RelLib.LdsOrd.STATUS_CLEARED),
            (_("Completed"), RelLib.LdsOrd.STATUS_COMPLETED),
            (_("Infant"), RelLib.LdsOrd.STATUS_INFANT),
            (_("Pre-1970"), RelLib.LdsOrd.STATUS_PRE_1970),
            (_("Qualified"), RelLib.LdsOrd.STATUS_QUALIFIED),
            (_("Stillborn"), RelLib.LdsOrd.STATUS_STILLBORN),
            (_("Submitted"), RelLib.LdsOrd.STATUS_SUBMITTED),
            (_("Uncleared"), RelLib.LdsOrd.STATUS_UNCLEARED),
            ],
        RelLib.LdsOrd.SEAL_TO_PARENTS:[
            (_("<No Status>"), RelLib.LdsOrd.STATUS_NONE),
            (_("BIC"), RelLib.LdsOrd.STATUS_BIC),
            (_("Cleared"), RelLib.LdsOrd.STATUS_CLEARED),
            (_("Completed"), RelLib.LdsOrd.STATUS_COMPLETED),
            (_("DNS"), RelLib.LdsOrd.STATUS_DNS),
            (_("Pre-1970"), RelLib.LdsOrd.STATUS_PRE_1970),
            (_("Qualified"), RelLib.LdsOrd.STATUS_QUALIFIED),
            (_("Stillborn"), RelLib.LdsOrd.STATUS_STILLBORN),
            (_("Submitted"), RelLib.LdsOrd.STATUS_SUBMITTED),
            (_("Uncleared"), RelLib.LdsOrd.STATUS_UNCLEARED),
            ],
        }

    def __init__(self, state, uistate, track, attrib, callback):
        """
        Displays the dialog box.

        parent - The class that called the Address editor.
        attrib - The attribute that is to be edited
        title - The title of the dialog box
        list - list of options for the pop down menu
        """
        EditSecondary.__init__(self, state, uistate, track, attrib, callback)

    def _local_init(self):
        self.top = gtk.glade.XML(const.gladeFile, "lds_person_edit","gramps")
        self.set_window(self.top.get_widget("lds_person_edit"),
                        self.top.get_widget('title'),
                        _('LDS Ordinance Editor'))

    def _connect_signals(self):
        self.parents_select.connect('clicked',self.select_parents_clicked)
        self.define_cancel_button(self.top.get_widget('cancel'))
        self.define_help_button(self.top.get_widget('help'),'adv-at')
        self.define_ok_button(self.top.get_widget('ok'),self.save)

    def _setup_fields(self):

        self.parents_label = self.top.get_widget('parents_label')
        self.parents = self.top.get_widget('parents')
        self.parents_select = self.top.get_widget('parents_select')

        self.priv = PrivacyButton(
            self.top.get_widget("private"),
            self.obj)

        self.date_field = MonitoredDate(
            self.top.get_widget("date"),
            self.top.get_widget("date_stat"),
            self.obj.get_date_object(),
            self.window, self.db.readonly)

        self.place_field = PlaceEntry(
            self.top.get_widget("place"),
            self.obj.get_place_handle(),
            self.dbstate.get_place_completion(),
            self.db.readonly)

        self.type_menu = MonitoredMenu(
            self.top.get_widget('type'),
            self.obj.set_type,
            self.obj.get_type,
            [(_('Baptism'),RelLib.LdsOrd.BAPTISM),
             (_('Endowment'),RelLib.LdsOrd.ENDOWMENT),
             (_('Sealed to Parents'),RelLib.LdsOrd.SEAL_TO_PARENTS)],
            self.db.readonly,
            changed=self.ord_type_changed)

        temple_list = []
        for val in lds.temples:
            temple_list.append((val[1],val[0]))

        self.temple_menu = MonitoredStrMenu(
            self.top.get_widget('temple'),
            self.obj.set_temple,
            self.obj.get_temple,
            temple_list,
            self.db.readonly)

        self.status_menu = MonitoredMenu(
            self.top.get_widget('status'),
            self.obj.set_status,
            self.obj.get_status,
            self._data_map[self.obj.get_type()],
            self.db.readonly)

        self.ord_type_changed()
        self.update_parent_label()

    def ord_type_changed(self):
        if self.obj.get_type() == RelLib.LdsOrd.BAPTISM:
            self.parents.hide()
            self.parents_label.hide()
            self.parents_select.hide()
        elif self.obj.get_type() == RelLib.LdsOrd.ENDOWMENT:
            self.parents.hide()
            self.parents_label.hide()
            self.parents_select.hide()
        elif self.obj.get_type() == RelLib.LdsOrd.SEAL_TO_PARENTS:
            self.parents.show()
            self.parents_label.show()
            self.parents_select.show()
        self.status_menu.change_menu(self._data_map[self.obj.get_type()])

    def _create_tabbed_pages(self):
        notebook = gtk.Notebook()
        self.srcref_list = self._add_tab(
            notebook,
            SourceEmbedList(self.dbstate,self.uistate, self.track,
                            self.obj.source_list))
        
        self.note_tab = self._add_tab(
            notebook,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.obj.get_note_object()))
        
        notebook.show_all()
        self.top.get_widget('vbox').pack_start(notebook,True)

    def select_parents_clicked(self, obj):
        from SelectFamily import SelectFamily

        dialog = SelectFamily(self.dbstate.db, _('Select Family'))
        family = dialog.run()
        if family:
            self.obj.set_family_handle(family.handle)
        self.update_parent_label()

    def update_parent_label(self):
        handle = self.obj.get_family_handle()
        if handle:
            family = self.dbstate.db.get_family_from_handle(handle)
            f = self.dbstate.db.get_person_from_handle(family.get_father_handle())
            m = self.dbstate.db.get_person_from_handle(family.get_mother_handle())
            if f and m:
                label = _("%(father)s and %(mother)s [%(gramps_id)s]") % {
                    'father' : NameDisplay.displayer.display(f),
                    'mother' : NameDisplay.displayer.display(m),
                    'gramps_id' : family.gramps_id,
                    }
            elif f:
                label = _("%(father)s [%(gramps_id)s]") % {
                    'father' : NameDisplay.displayer.display(f),
                    'gramps_id' : family.gramps_id,
                    }
            elif m:
                label = _("%(mother)s [%(gramps_id)s]") % {
                    'mother' : NameDisplay.displayer.display(m),
                    'gramps_id' : family.gramps_id,
                    }
            else:
                label = _("[%(gramps_id)s]") % {
                    'gramps_id' : family.gramps_id,
                    }
        else:
            label = ""

        self.parents.set_text(label)

    def build_menu_names(self, attrib):
        label = _("LDS Ordinance")
        return (label, _('LDS Ordinance Editor'))

    def save(self,*obj):
        """
        Called when the OK button is pressed. Gets data from the
        form and updates the LdsOrd data structure.
        """

        (need_new, handle) = self.place_field.get_place_info()
        if need_new:
            place_obj = RelLib.Place()
            place_obj.set_title(handle)
            trans = self.db.transaction_begin()
            self.db.add_place(place_obj,trans)
            self.db.transaction_commit(trans,_("Add Place"))
            self.obj.set_place_handle(place_obj.get_handle())
        else:
            self.obj.set_place_handle(handle)

        if self.callback:
            self.callback(self.obj)
        self.close_window(obj)

#-------------------------------------------------------------------------
#
# EditFamilyLdsOrd
#
#-------------------------------------------------------------------------
class EditFamilyLdsOrd(EditSecondary):
    """
    Displays a dialog that allows the user to edit an attribute.
    """

    def __init__(self, state, uistate, track, attrib, callback):
        """
        Displays the dialog box.

        parent - The class that called the Address editor.
        attrib - The attribute that is to be edited
        title - The title of the dialog box
        list - list of options for the pop down menu
        """
        EditSecondary.__init__(self, state, uistate, track, attrib, callback)

    def _local_init(self):
        self.top = gtk.glade.XML(const.gladeFile, "lds_person_edit","gramps")
        self.set_window(self.top.get_widget("lds_person_edit"),
                        self.top.get_widget('title'),
                        _('LDS Ordinance Editor'))

    def _connect_signals(self):
        self.define_cancel_button(self.top.get_widget('cancel'))
        self.define_help_button(self.top.get_widget('help'),'adv-at')
        self.define_ok_button(self.top.get_widget('ok'),self.save)

    def _setup_fields(self):

        self.parents_label = self.top.get_widget('parents_label')
        self.parents = self.top.get_widget('parents')
        self.parents_select = self.top.get_widget('parents_select')

        self.priv = PrivacyButton(
            self.top.get_widget("private"),
            self.obj)

        self.date_field = MonitoredDate(
            self.top.get_widget("date"),
            self.top.get_widget("date_stat"),
            self.obj.get_date_object(),
            self.window, self.db.readonly)

        self.place_field = PlaceEntry(
            self.top.get_widget("place"),
            self.obj.get_place_handle(),
            self.dbstate.get_place_completion(),
            self.db.readonly)

        self.type_menu = MonitoredMenu(
            self.top.get_widget('type'),
            self.obj.set_type,
            self.obj.get_type,
            [(_('Sealed to Spouse'),RelLib.LdsOrd.SEAL_TO_SPOUSE)],
            self.db.readonly)

        temple_list = []
        for val in lds.temples:
            temple_list.append((val[1],val[0]))

        self.temple_menu = MonitoredStrMenu(
            self.top.get_widget('temple'),
            self.obj.set_temple,
            self.obj.get_temple,
            temple_list,
            self.db.readonly)

        self.status_menu = MonitoredMenu(
            self.top.get_widget('status'),
            self.obj.set_status,
            self.obj.get_status,
            [(_('<No Status>'), RelLib.LdsOrd.STATUS_NONE),
             (_('Canceled'), RelLib.LdsOrd.STATUS_CANCELED),
             (_("Cleared"), RelLib.LdsOrd.STATUS_CLEARED),
             (_("Completed"), RelLib.LdsOrd.STATUS_COMPLETED),
             (_("DNS"), RelLib.LdsOrd.STATUS_DNS),
             (_("Pre-1970"), RelLib.LdsOrd.STATUS_PRE_1970),
             (_("Qualified"), RelLib.LdsOrd.STATUS_QUALIFIED),
             (_("DNS/CAN"), RelLib.LdsOrd.STATUS_DNS_CAN),
             (_("Submitted"), RelLib.LdsOrd.STATUS_SUBMITTED),
             (_("Uncleared"), RelLib.LdsOrd.STATUS_UNCLEARED),],
            self.db.readonly)

    def _create_tabbed_pages(self):
        notebook = gtk.Notebook()
        self.srcref_list = self._add_tab(
            notebook,
            SourceEmbedList(self.dbstate,self.uistate, self.track,
                            self.obj.source_list))
        
        self.note_tab = self._add_tab(
            notebook,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.obj.get_note_object()))
        
        notebook.show_all()
        self.top.get_widget('vbox').pack_start(notebook,True)

    def build_menu_names(self, attrib):
        label = _("LDS Ordinance")
        return (label, _('LDS Ordinance Editor'))

    def save(self,*obj):
        """
        Called when the OK button is pressed. Gets data from the
        form and updates the LdsOrd data structure.
        """

        (need_new, handle) = self.place_field.get_place_info()
        if need_new:
            place_obj = RelLib.Place()
            place_obj.set_title(handle)
            trans = self.db.transaction_begin()
            self.db.add_place(place_obj,trans)
            self.db.transaction_commit(trans,_("Add Place"))
            self.obj.set_place_handle(place_obj.get_handle())
        else:
            self.obj.set_place_handle(handle)

        if self.callback:
            self.callback(self.obj)
        self.close_window(obj)
