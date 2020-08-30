# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2017       Alois Poettker
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

"""
Provide the event view.
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".plugins.eventview")

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

from gramps.gui.dialog import ErrorDialog, MultiSelectDialog, QuestionDialog
from gramps.gen.db import DbTxn
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Event
from gramps.gen.utils.string import data_recover_msg

from gramps.gui.ddtargets import DdTargets
from gramps.gui.editors import EditEvent, DeleteEventQuery
from gramps.gui.filters.sidebar import EventSidebarFilter
from gramps.gui.merge import MergeEvent
from gramps.gen.plug import CATEGORY_QR_EVENT
from gramps.gui.views.bookmarks import EventBookmarks
from gramps.gui.views.listview import ListView, TEXT, MARKUP, ICON
from gramps.gui.views.treemodels import EventModel

#-------------------------------------------------------------------------
#
# EventView
#
#-------------------------------------------------------------------------
class EventView(ListView):
    """
    EventView class, derived from the ListView
    """
    # columns in the model used in view
    COL_DESCR = 0
    COL_ID = 1
    COL_TYPE = 2
    COL_DATE = 3
    COL_PLACE = 4
    COL_PRIV = 5
    COL_TAGS = 6
    COL_CHAN = 7
    COL_PARTIC = 8
    # column definitions
    COLUMNS = [
        (_('Description'), TEXT, None),
        (_('ID'), TEXT, None),
        (_('Type'), TEXT, None),
        (_('Date'), MARKUP, None),
        (_('Place'), TEXT, None),
        (_('Private'), ICON, 'gramps-lock'),
        (_('Tags'), TEXT, None),
        (_('Last Changed'), TEXT, None),
        (_('Main Participants'), TEXT, None),
        ]
    # default setting with visible columns, order of the col, and their size
    CONFIGSETTINGS = (
        ('columns.visible', [COL_TYPE, COL_PARTIC, COL_DATE, COL_PLACE,
                             COL_DESCR, COL_ID]),
        ('columns.rank', [COL_TYPE, COL_PARTIC, COL_DATE, COL_PLACE, COL_DESCR,
                          COL_ID, COL_PRIV, COL_TAGS, COL_CHAN]),
        ('columns.size', [100, 230, 150, 200, 100, 75, 40, 100, 100])
        )
    ADD_MSG = _("Add a new event")
    EDIT_MSG = _("Edit the selected event")
    DEL_MSG = _("Delete the selected event")
    MERGE_MSG = _("Merge the selected events")
    FILTER_TYPE = "Event"
    QR_CATEGORY = CATEGORY_QR_EVENT

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        """
        Create the Event View
        """
        signal_map = {
            'event-add'     : self.row_add,
            'event-update'  : self.row_update,
            'event-delete'  : self.row_delete,
            'event-rebuild' : self.object_build,
            'person-update' : self.person_update,
            'person-add'    : self.person_update,
            'person-delete' : self.object_build,  # TODO slow way to do this
            'family-update' : self.family_update,
            'family-add'    : self.family_update,
            'family-delete' : self.object_build,  # TODO slow way to do this
            'place-update'  : self.related_update,
            }

        ListView.__init__(
            self, _('Events'), pdata, dbstate, uistate,
            EventModel,
            signal_map,
            EventBookmarks, nav_group,
            multiple=True,
            filter_class=EventSidebarFilter)

        uistate.connect('nameformat-changed', self.build_tree)
        uistate.connect('placeformat-changed', self.build_tree)

        self.additional_uis.append(self.additional_ui)

    def person_update(self, hndl_list):
        """ Deal with person updates thay may effect the Main Participants
        column.  These cannot use the more generic mechanism because Person
        objects use EventRef to point to events, rather than Events pointing
        to persons. Example: A person's name change or add event to person"""
        update_list = []
        for hndl in hndl_list:
            person = self.dbstate.db.get_person_from_handle(hndl)
            for eventref in person.get_event_ref_list():
                update_list.append(eventref.ref)
        self.row_update(update_list)

    def family_update(self, hndl_list):
        """ Deal with family updates thay may effect the Main Participants
        column.  These cannot use the more generic mechanism because Family
        objects use EventRef to point to events, rather than Events pointing
        to Families. Example: Change/add/removal of parent, or add family to
        event"""
        update_list = []
        for hndl in hndl_list:
            family = self.dbstate.db.get_family_from_handle(hndl)
            for eventref in family.get_event_ref_list():
                update_list.append(eventref.ref)
        self.row_update(update_list)

    def navigation_type(self):
        return 'Event'

    def drag_info(self):
        """
        Indicate that the drag type is an EVENT
        """
        return DdTargets.EVENT

    def get_stock(self):
        """
        Use the gramps-event stock icon
        """
        return 'gramps-event'

    additional_ui = [  # Defines the UI string for UIManager
        '''
      <placeholder id="LocalExport">
        <item>
          <attribute name="action">win.ExportTab</attribute>
          <attribute name="label" translatable="yes">Export View...</attribute>
        </item>
      </placeholder>
''',
        '''
      <section id="AddEditBook">
        <item>
          <attribute name="action">win.AddBook</attribute>
          <attribute name="label" translatable="yes">_Add Bookmark</attribute>
        </item>
        <item>
          <attribute name="action">win.EditBook</attribute>
          <attribute name="label" translatable="no">%s...</attribute>
        </item>
      </section>
''' % _('Organize Bookmarks'),
        '''
      <placeholder id="CommonGo">
      <section>
        <item>
          <attribute name="action">win.Back</attribute>
          <attribute name="label" translatable="yes">_Back</attribute>
        </item>
        <item>
          <attribute name="action">win.Forward</attribute>
          <attribute name="label" translatable="yes">_Forward</attribute>
        </item>
      </section>
      </placeholder>
''',
        '''
      <section id='CommonEdit' groups='RW'>
        <item>
          <attribute name="action">win.Add</attribute>
          <attribute name="label" translatable="yes">_Add...</attribute>
        </item>
        <item>
          <attribute name="action">win.Edit</attribute>
          <attribute name="label">%s</attribute>
        </item>
        <item>
          <attribute name="action">win.Remove</attribute>
          <attribute name="label" translatable="yes">_Delete</attribute>
        </item>
        <item>
          <attribute name="action">win.Merge</attribute>
          <attribute name="label" translatable="yes">_Merge...</attribute>
        </item>
      </section>
''' % _("_Edit...", "action"),  # to use sgettext()
        '''
        <placeholder id='otheredit'>
        <item>
          <attribute name="action">win.FilterEdit</attribute>
          <attribute name="label" translatable="yes">'''
        '''Event Filter Editor</attribute>
        </item>
        </placeholder>
''',  # Following are the Toolbar items
        '''
    <placeholder id='CommonNavigation'>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-previous</property>
        <property name="action-name">win.Back</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Go to the previous object in the history</property>
        <property name="label" translatable="yes">_Back</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-next</property>
        <property name="action-name">win.Forward</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Go to the next object in the history</property>
        <property name="label" translatable="yes">_Forward</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
''',
        '''
    <placeholder id='BarCommonEdit'>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">list-add</property>
        <property name="action-name">win.Add</property>
        <property name="tooltip_text">%s</property>
        <property name="label" translatable="yes">_Add...</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">gtk-edit</property>
        <property name="action-name">win.Edit</property>
        <property name="tooltip_text">%s</property>
        <property name="label" translatable="yes">Edit...</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">list-remove</property>
        <property name="action-name">win.Remove</property>
        <property name="tooltip_text">%s</property>
        <property name="label" translatable="yes">_Delete</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-merge</property>
        <property name="action-name">win.Merge</property>
        <property name="tooltip_text">%s</property>
        <property name="label" translatable="yes">_Merge...</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
   </placeholder>
''' % (ADD_MSG, EDIT_MSG, DEL_MSG, MERGE_MSG),
        '''
    <menu id="Popup">
      <section>
        <item>
          <attribute name="action">win.Back</attribute>
          <attribute name="label" translatable="yes">_Back</attribute>
        </item>
        <item>
          <attribute name="action">win.Forward</attribute>
          <attribute name="label" translatable="yes">Forward</attribute>
        </item>
      </section>
      <section id="PopUpTree">
      </section>
      <section>
        <item>
          <attribute name="action">win.Add</attribute>
          <attribute name="label" translatable="yes">_Add...</attribute>
        </item>
        <item>
          <attribute name="action">win.Edit</attribute>
          <attribute name="label">%s</attribute>
        </item>
        <item>
          <attribute name="action">win.Remove</attribute>
          <attribute name="label" translatable="yes">_Delete</attribute>
        </item>
        <item>
          <attribute name="action">win.Merge</attribute>
          <attribute name="label" translatable="yes">_Merge...</attribute>
        </item>
      </section>
      <section>
        <placeholder id='QuickReport'>
        </placeholder>
      </section>
    </menu>
''' % _('_Edit...', 'action')  # to use sgettext()
    ]

    def get_handle_from_gramps_id(self, gid):
        obj = self.dbstate.db.get_event_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        else:
            return None

    def add(self, *obj):
        try:
            EditEvent(self.dbstate, self.uistate, [], Event())
        except WindowActiveError:
            pass

    def remove(self, *obj):
        """
        Method called when deleting event(s) from the event view.
        """
        handles = self.selected_handles()
        if len(handles) == 1:
            event = self.dbstate.db.get_event_from_handle(handles[0])
            msg1 = self._message1_format(event)
            msg2 = self._message2_format(event)
            msg2 = "%s %s" % (msg2, data_recover_msg)
            QuestionDialog(msg1,
                           msg2,
                           _('_Delete Event'),
                           lambda: self.delete_event_response(event),
                           parent=self.uistate.window)
        else:
            MultiSelectDialog(self._message1_format,
                              self._message2_format,
                              handles,
                              self.dbstate.db.get_event_from_handle,
                              yes_func=self.delete_event_response,
                              multi_yes_func=self.delete_multi_event_response,
                              parent=self.uistate.window)

    def _message1_format(self, event):
        """
        Header format for remove dialogs.
        """
        return _('Delete {type} [{gid}]?').format(type=str(event.type),
                                                  gid=event.gramps_id)

    def _message2_format(self, event):
        """
        Detailed message format for the remove dialogs.
        """
        return _('Deleting item will remove it from the database.')

    def delete_event_response(self, event):
        """
        Delete the event from the database.
        """
        person_list = [item[1] for item in
            self.dbstate.db.find_backlink_handles(event.handle, ['Person'])]
        family_list = [item[1] for item in
            self.dbstate.db.find_backlink_handles(event.handle, ['Family'])]

        query = DeleteEventQuery(self.dbstate, self.uistate, event,
                                 person_list, family_list)
        query.query_response()

    def delete_multi_event_response(self, handles=None):
        """
        Deletes multiple events from the database.
        """
        # set the busy cursor, so the user knows that we are working
        self.uistate.set_busy_cursor(True)
        self.uistate.progress.show()
        self.uistate.push_message(self.dbstate, _("Processing..."))
        hndl_cnt = len(handles) / 100
        _db = self.dbstate.db
        _db.disable_signals()

        # create the transaction
        with DbTxn('', _db) as trans:
            for (indx, handle) in enumerate(handles):
                ev_handle_list = [handle]

                person_list = [
                    item[1] for item in
                    _db.find_backlink_handles(handle, ['Person'])]
                for hndl in person_list:
                    person = _db.get_person_from_handle(hndl)
                    person.remove_handle_references('Event', ev_handle_list)
                    _db.commit_person(person, trans)

                family_list = [
                    item[1] for item in
                    _db.find_backlink_handles(handle, ['Family'])]
                for hndl in family_list:
                    family = _db.get_family_from_handle(hndl)
                    family.remove_handle_references('Event', ev_handle_list)
                    _db.commit_family(family, trans)

                _db.remove_event(handle, trans)
                self.uistate.pulse_progressbar(indx / hndl_cnt)
            trans.set_description(_("Multiple Selection Delete"))

        _db.enable_signals()
        _db.request_rebuild()
        self.uistate.progress.hide()
        self.uistate.set_busy_cursor(False)

    def remove_object_from_handle(self, handle):
        """
        The remove_selected_objects method is not called in this view.
        """
        pass

    def edit(self, *obj):
        for handle in self.selected_handles():
            event = self.dbstate.db.get_event_from_handle(handle)
            try:
                EditEvent(self.dbstate, self.uistate, [], event)
            except WindowActiveError:
                pass

    def merge(self, *obj):
        """
        Merge the selected events.
        """
        mlist = self.selected_handles()

        if len(mlist) != 2:
            msg = _("Cannot merge event objects.")
            msg2 = _("Exactly two events must be selected to perform a merge. "
                     "A second object can be selected by holding down the "
                     "control key while clicking on the desired event.")
            ErrorDialog(msg, msg2, parent=self.uistate.window)
        else:
            MergeEvent(self.dbstate, self.uistate, [], mlist[0], mlist[1])

    def tag_updated(self, handle_list):
        """
        Update tagged rows when a tag color changes.
        """
        all_links = set([])
        for tag_handle in handle_list:
            links = set([link[1] for link in
                         self.dbstate.db.find_backlink_handles(tag_handle,
                                                    include_classes='Event')])
            all_links = all_links.union(links)
        self.row_update(list(all_links))

    def add_tag(self, transaction, event_handle, tag_handle):
        """
        Add the given tag to the given event.
        """
        event = self.dbstate.db.get_event_from_handle(event_handle)
        event.add_tag(tag_handle)
        self.dbstate.db.commit_event(event, transaction)

    def remove_tag(self, transaction, event_handle, tag_handle):
        """
        Remove the given tag from the given event.
        """
        event = self.dbstate.db.get_event_from_handle(event_handle)
        event.remove_tag(tag_handle)
        self.dbstate.db.commit_event(event, transaction)

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return (("Event Filter",),
                ("Event Gallery",
                 "Event Citations",
                 "Event Notes",
                 "Event Attributes",
                 "Event Backlinks"))
