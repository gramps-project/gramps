#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

# $Id: EventNames.py 8023 2007-02-01 17:26:51Z rshura $

"Database Processing/Fix capitalization of family names"

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# gnome/gtk
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import ManagedWindow
import RelLib
import Utils

from PluginUtils import Tool, register_tool
from BasicUtils import name_displayer

#-------------------------------------------------------------------------
#
# EventNames
#
#-------------------------------------------------------------------------
class EventNames(Tool.BatchTool, ManagedWindow.ManagedWindow):
    """
    Looks for events that do not have a description, and builds the 
    description from the item that contains it. Looks for a PRIMARY role
    type for events attached to a persons, and a FAMILY role for an event
    that is attached to a family.
    """

    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        self.label = _('Capitalization changes')
        
        Tool.BatchTool.__init__(self, dbstate, options_class, name)

        if not self.fail:
            uistate.set_busy_cursor(True)
            self.run()
            uistate.set_busy_cursor(False)

    def run(self):
        """
        Performs the actual extraction of information
        """
        trans = self.db.transaction_begin("", batch=True)
        self.db.disable_signals()
        
        for handle in self.db.get_person_handles():
            person = self.db.get_person_from_handle(handle)
            for event_ref in person.get_event_ref_list():
                if event_ref.get_role() == RelLib.EventRoleType.PRIMARY:
                    event_handle = event_ref.ref
                    event = self.db.get_event_from_handle(event_handle)
                    if event.get_description() == "":
                        person_event_name(event, person)
                        self.db.commit_event(event, trans)
                        self.change = True

        for handle in self.db.get_family_handles():
            family = self.db.get_family_from_handle(handle)
            for event_ref in family.get_event_ref_list():
                if event_ref.get_role() == RelLib.EventRoleType.FAMILY:
                    event_handle = event_ref.ref
                    event = self.db.get_event_from_handle(event_handle)
                    if event.get_description() == "":
                        family_event_name(event, family, self.db)
                        self.db.commit_event(event, trans)

        self.db.transaction_commit(trans, _("Event name changes"))
        self.db.enable_signals()
        self.db.request_rebuild()

#-------------------------------------------------------------------------
#
# Support functions
#
#-------------------------------------------------------------------------

EVENT_FAMILY_STR = _("%(event_name)s of %(family)s")
EVENT_PERSON_STR = _("%(event_name)s of %(person)s")

def person_event_name(event, person):
    """
    Builds a name for an event based on the primary person's information
    """
    if not event.get_description():
        text = EVENT_PERSON_STR % {
            'event_name' : str(event.get_type()), 
            'person' : name_displayer.display(person), 
            }
        event.set_description(text)

def family_event_name(event, family, dbase):
    """
    Builds a name for an event based on the family's information
    """
    if not event.get_description():
        text = EVENT_FAMILY_STR % {
            'event_name' : str(event.get_type()), 
            'family' : Utils.family_name(family, dbase), 
            }
        event.set_description(text)
            
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class EventNamesOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, person_id=None):
        Tool.ToolOptions.__init__(self, name, person_id)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_tool(
    name = 'evname', 
    category = Tool.TOOL_DBPROC, 
    tool_class = EventNames, 
    options_class = EventNamesOptions, 
    modes = Tool.MODE_GUI, 
    translated_name = _("Extract event descriptions from event data"), 
    status = _("Stable"), 
    author_name = "Donald N. Allingham", 
    author_email = "don@gramps-project.org", 
    description = _("Extracts event descriptions from the event data")
    )
