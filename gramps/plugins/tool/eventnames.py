#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

"""Tools/Database Processing/Extract Event Descriptions from Event Data"""

# -------------------------------------------------------------------------
#
# python modules
#
# -------------------------------------------------------------------------


# -------------------------------------------------------------------------
#
# gnome/gtk
#
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
ngettext = glocale.translation.ngettext  # else "nearby" comments are ignored
from gramps.gen.lib import EventRoleType
from gramps.gen.db import DbTxn
from gramps.gen.utils.db import family_name

from gramps.gui.plug import tool
from gramps.gen.display.name import displayer as name_displayer


# -------------------------------------------------------------------------
#
# EventNames
#
# -------------------------------------------------------------------------
class EventNames(tool.BatchTool):
    """
    Look for events that do not have a description, and build the description
    from the item that contains it.

    Looks for a PRIMARY role type for events attached to a persons, and a
    FAMILY role for an event that is attached to a family.

    """

    def __init__(self, dbstate, user, options_class, name, callback=None):
        self.user = user
        tool.BatchTool.__init__(self, dbstate, user, options_class, name)

        if not self.fail:
            self.run()

    def run(self):
        """
        Perform the actual extraction of information.
        """
        with DbTxn(_("Event name changes"), self.db, batch=True) as trans:
            self.db.disable_signals()
            self.change = False
            counter = 0

            with self.user.progress(_("Extract Event Description"), "", 2) as step:
                for person in self.db.iter_people():
                    for event_ref in person.get_event_ref_list():
                        if event_ref.get_role() == EventRoleType.PRIMARY:
                            event_handle = event_ref.ref
                            event = self.db.get_event_from_handle(event_handle)
                            if event.get_description() == "":
                                person_event_name(event, person)
                                self.db.commit_event(event, trans)
                                self.change = True
                                counter += 1
                step()

                for family in self.db.iter_families():
                    for event_ref in family.get_event_ref_list():
                        if event_ref.get_role() == EventRoleType.FAMILY:
                            event_handle = event_ref.ref
                            event = self.db.get_event_from_handle(event_handle)
                            if event.get_description() == "":
                                family_event_name(event, family, self.db)
                                self.db.commit_event(event, trans)
                                self.change = True
                                counter += 1
                step()

        self.db.enable_signals()
        self.db.request_rebuild()

        if hasattr(self.user.uistate, "window"):
            parent_window = self.user.uistate.window
        else:
            parent_window = None
        if self.change == True:
            # Translators: leave all/any {...} untranslated
            message = ngettext(
                "{quantity} event description has been added",
                "{quantity} event descriptions have been added",
                counter,
            ).format(quantity=counter)
            self.user.info(_("Modifications made"), message, parent=parent_window)
        else:
            self.user.info(
                _("No modifications made"),
                _("No event description has been added."),
                parent=parent_window,
            )


# -------------------------------------------------------------------------
#
# Support functions
#
# -------------------------------------------------------------------------

# feature requests 2356, 1658: avoid genitive form
EVENT_FAMILY_STR = _("%(event_name)s of %(family)s")
# feature requests 2356, 1658: avoid genitive form
EVENT_PERSON_STR = _("%(event_name)s of %(person)s")


def person_event_name(event, person):
    """
    Build a name for an event based on the primary person's information.
    """
    if not event.get_description():
        text = EVENT_PERSON_STR % {
            "event_name": str(event.get_type()),
            "person": name_displayer.display(person),
        }
        event.set_description(text)


def family_event_name(event, family, dbase):
    """
    Build a name for an event based on the family's information.
    """
    if not event.get_description():
        text = EVENT_FAMILY_STR % {
            "event_name": str(event.get_type()),
            "family": family_name(family, dbase),
        }
        event.set_description(text)


# ------------------------------------------------------------------------
#
#
#
# ------------------------------------------------------------------------
class EventNamesOptions(tool.ToolOptions):
    """
    Define options and provides handling interface.
    """

    def __init__(self, name, person_id=None):
        tool.ToolOptions.__init__(self, name, person_id)
