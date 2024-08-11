# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
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

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
import time

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------

from gramps.gen.lib import Person, Family
from gramps.gen.db import PERSON_KEY, FAMILY_KEY, TXNDEL
from gramps.gen.plug import Gramplet
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.utils.db import family_name
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# LogGramplet class
#
# ------------------------------------------------------------------------
class LogGramplet(Gramplet):
    def init(self):
        self.set_tooltip(_("Click name to change active\nDouble-click name to edit"))
        self.set_text(_("Log for this Session") + "\n")
        self.gui.force_update = True  # will always update, even if minimized
        self.last_log = None

    def timestamp(self):
        self.append_text(time.strftime("%Y-%m-%d %H:%M:%S "))

    def db_changed(self):
        self.timestamp()
        self.append_text(_("Opened data base -----------\n"))
        # List of translated strings used here (translated in self.log ).
        _("Added"), _("Deleted"), _("Edited"), _("Selected")  # Dead code for l10n
        self.connect(
            self.dbstate.db,
            "person-add",
            lambda handles: self.log("Person", "Added", handles),
        )
        self.connect(
            self.dbstate.db,
            "person-delete",
            lambda handles: self.log("Person", "Deleted", handles),
        )
        self.connect(
            self.dbstate.db,
            "person-update",
            lambda handles: self.log("Person", "Edited", handles),
        )
        self.connect(
            self.dbstate.db,
            "family-add",
            lambda handles: self.log("Family", "Added", handles),
        )
        self.connect(
            self.dbstate.db,
            "family-delete",
            lambda handles: self.log("Family", "Deleted", handles),
        )
        self.connect(
            self.dbstate.db,
            "family-update",
            lambda handles: self.log("Family", "Edited", handles),
        )
        self.connect_signal("Person", self.active_changed)
        self.connect_signal("Family", self.active_changed_family)

    def active_changed(self, handle):
        if handle:
            self.log("Person", "Selected", [handle])

    def active_changed_family(self, handle):
        if handle:
            self.log("Family", "Selected", [handle])

    def log(self, ltype, action, handles):
        for handle in set(handles):
            if self.last_log == (ltype, action, handle):
                continue
            self.last_log = (ltype, action, handle)
            self.timestamp()
            # Translators: needed for French, ignore otherwise
            self.append_text(_("%s: ") % _(action))
            if action == "Deleted":
                transaction = self.dbstate.db.transaction
                if ltype == "Person":
                    name = "a person"
                    if transaction is not None:
                        for i in transaction.get_recnos(reverse=True):
                            (
                                obj_type,
                                trans_type,
                                hndl,
                                old_data,
                                dummy,
                            ) = transaction.get_record(i)
                            if isinstance(hndl, bytes):
                                hndl = str(hndl, "utf-8")
                            if (
                                obj_type == PERSON_KEY
                                and trans_type == TXNDEL
                                and hndl == handle
                            ):
                                person = Person()
                                person.unserialize(old_data)
                                name = name_displayer.display(person)
                                break
                elif ltype == "Family":
                    name = "a family"
                    if transaction is not None:
                        for i in transaction.get_recnos(reverse=True):
                            (
                                obj_type,
                                trans_type,
                                hndl,
                                old_data,
                                dummy,
                            ) = transaction.get_record(i)
                            if isinstance(hndl, bytes):
                                hndl = str(hndl, "utf-8")
                            if (
                                obj_type == FAMILY_KEY
                                and trans_type == TXNDEL
                                and hndl == handle
                            ):
                                family = Family()
                                family.unserialize(old_data)
                                name = family_name(family, self.dbstate.db, name)
                                break
                self.append_text(name)
            else:
                if ltype == "Person":
                    person = self.dbstate.db.get_person_from_handle(handle)
                    name = name_displayer.display(person)
                elif ltype == "Family":
                    family = self.dbstate.db.get_family_from_handle(handle)
                    name = family_name(family, self.dbstate.db, "a family")
                self.link(name, ltype, handle)
            self.append_text("\n")
