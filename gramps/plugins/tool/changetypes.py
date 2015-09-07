#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
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

"""Database Processing/Rename Event Types"""

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
ngettext = glocale.translation.ngettext # else "nearby" comments are ignored
from gramps.gui.utils import ProgressMeter
from gramps.gui.managedwindow import ManagedWindow
from gramps.gui.autocomp import fill_combo
from gramps.gen.lib import EventType
from gramps.gen.db import DbTxn
from gramps.gui.plug import tool
from gramps.gui.glade import Glade

#-------------------------------------------------------------------------
#
# ChangeTypes class
#
#-------------------------------------------------------------------------
class ChangeTypes(tool.BatchTool, ManagedWindow):

    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate
        self.user = user

        tool.BatchTool.__init__(self, dbstate, user, options_class, name)
        if self.fail:
            return

        if uistate:
            self.title = _('Change Event Types')
            ManagedWindow.__init__(self,uistate,[],
                                                 self.__class__)
            self.init_gui()
        else:
            self.run_tool()

    def init_gui(self):
        # Draw dialog and make it handle everything

        self.glade = Glade()

        self.auto1 = self.glade.get_object("original")
        self.auto2 = self.glade.get_object("new")

        # Need to display localized event names
        etype = EventType()
        event_names = sorted(etype.get_standard_names(), key=glocale.sort_key)

        fill_combo(self.auto1,event_names)
        fill_combo(self.auto2,event_names)

        etype.set_from_xml_str(self.options.handler.options_dict['fromtype'])
        self.auto1.get_child().set_text(str(etype))

        etype.set_from_xml_str(self.options.handler.options_dict['totype'])
        self.auto2.get_child().set_text(str(etype))

        window = self.glade.toplevel
        self.set_window(window,self.glade.get_object('title'),self.title)

        self.glade.connect_signals({
            "on_close_clicked"  : self.close,
            "on_apply_clicked"  : self.on_apply_clicked,
            "on_delete_event"   : self.close,
            })

        self.show()

    def build_menu_names(self, obj):
        return (self.title,None)

    def run_tool(self, parent_window = None):
        # Run tool and return results
        # These are English names, no conversion needed
        fromtype = self.options.handler.options_dict['fromtype']
        totype = self.options.handler.options_dict['totype']

        modified = 0

        with DbTxn(_('Change types'), self.db, batch=True) as self.trans:
            self.db.disable_signals()
            with self.user.progress(
                    _('Analyzing Events'), '',
                    self.db.get_number_of_events()) as step:
                for event_handle in self.db.get_event_handles():
                    event = self.db.get_event_from_handle(event_handle)
                    if event.get_type().xml_str() == fromtype:
                        event.type.set_from_xml_str(totype)
                        modified += 1
                        self.db.commit_event(event,self.trans)
                        step()
        self.db.enable_signals()
        self.db.request_rebuild()

        if modified == 0:
            msg = _("No event record was modified.")
        else:
            # translators: leave all/any {...} untranslated
            msg = ngettext("{number_of} event record was modified.",
                           "{number_of} event records were modified.", modified
                          ).format(number_of=modified)

        self.user.info(_('Change types'), msg, parent_window)
        return (bool(modified),msg)

    def on_apply_clicked(self, obj):
        # Need to store English names for later comparison
        the_type = EventType()

        the_type.set(self.auto1.get_child().get_text())
        self.options.handler.options_dict['fromtype'] = the_type.xml_str()

        the_type.set(self.auto2.get_child().get_text())
        self.options.handler.options_dict['totype'] = the_type.xml_str()

        self.run_tool(self.window)

        # Save options
        self.options.handler.save_options()

        self.close()

#------------------------------------------------------------------------
#
#
#
#------------------------------------------------------------------------
class ChangeTypesOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name,person_id=None):
        tool.ToolOptions.__init__(self, name,person_id)

        # Options specific for this report
        self.options_dict = {
            'fromtype'   : '',
            'totype'     : '',
        }
        self.options_help = {
            'fromtype'   : ("=str","Type of events to replace",
                            "Event type string"),
            'totype'     : ("=str","New type replacing the old one",
                            "Event type string"),
        }
