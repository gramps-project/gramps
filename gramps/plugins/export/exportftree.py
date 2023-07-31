#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006, 2008  Donald N. Allingham
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

"Export to Web Family Tree"

# -------------------------------------------------------------------------
#
# standard python modules
#
# -------------------------------------------------------------------------

# ------------------------------------------------------------------------
#
# Set up logging
#
# ------------------------------------------------------------------------
import logging
from collections import abc

log = logging.getLogger(".WriteFtree")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
# keep the following line even though not obviously used (works on import)
from gramps.gui.plug.export import WriterOptionBox
from gramps.gui.dialog import ErrorDialog
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# writeData
#
# -------------------------------------------------------------------------
def writeData(database, filename, user, option_box=None):
    """function to export Web Family Tree file"""
    writer = FtreeWriter(database, filename, user, option_box)
    return writer.export_data()


# -------------------------------------------------------------------------
#
# FtreeWriter
#
# -------------------------------------------------------------------------
class FtreeWriter:
    """Export a Web Family Tree format file"""

    def __init__(self, database, filename, user, option_box=None):
        self.db = database
        self.filename = filename
        self.user = user
        self.option_box = option_box
        # is callback is really callable?
        if isinstance(self.user.callback, abc.Callable):
            self.update = self.update_real
        else:
            self.update = self.update_empty

        if option_box:
            self.option_box.parse_options()
            self.db = option_box.get_filtered_database(self.db)

        self.plist = self.db.get_person_handles()
        self.plist.sort()
        # the following are used to update the progress meter
        self.total = 2 * len(self.plist)
        self.count = 0
        self.oldval = 0  # we only update when percentage changes

    def update_empty(self):
        """used when no callback is present"""
        pass

    def update_real(self):
        """Progress update"""
        self.count += 1
        newval = int(100 * self.count / self.total)
        if newval != self.oldval:
            self.user.callback(newval)
            self.oldval = newval

    def export_data(self):
        """main export processing"""
        name_map = {}
        id_map = {}
        id_name = {}

        for key in self.plist:
            self.update()
            pnam = self.db.get_person_from_handle(key).get_primary_name()
            snam = pnam.get_surname()
            items = pnam.get_first_name().split()
            nam = ("%s %s" % (items[0], snam)) if items else snam

            count = -1
            if nam in name_map:
                count = 0
                while 1:
                    nam_num = "%s%d" % (nam, count)
                    if nam_num not in name_map:
                        break
                    count += 1
                name_map[nam_num] = key
                id_map[key] = nam_num
            else:
                name_map[nam] = key
                id_map[key] = nam
            id_name[key] = get_name(pnam, snam, count)

        try:
            with open(self.filename, "w", encoding="utf_8") as file:
                return self._export_data(file, id_name, id_map)
        except IOError as msg:
            msg2 = _("Could not create %s") % self.filename
            ErrorDialog(msg2, str(msg), parent=self.option_box.window)
            return False

    def _export_data(self, file, id_name, id_map):
        """file export processing"""
        for key in self.plist:
            self.update()
            pers = self.db.get_person_from_handle(key)
            name = id_name[key]
            father = mother = email = web = ""

            family_handle = pers.get_main_parents_family_handle()
            if family_handle:
                family = self.db.get_family_from_handle(family_handle)
                if family.get_father_handle() and family.get_father_handle() in id_map:
                    father = id_map[family.get_father_handle()]
                if family.get_mother_handle() and family.get_mother_handle() in id_map:
                    mother = id_map[family.get_mother_handle()]

            #
            # Calculate Date
            #
            birth_ref = pers.get_birth_ref()
            death_ref = pers.get_death_ref()
            if birth_ref:
                birth_event = self.db.get_event_from_handle(birth_ref.ref)
                birth = birth_event.get_date_object()
            else:
                birth = None
            if death_ref:
                death_event = self.db.get_event_from_handle(death_ref.ref)
                death = death_event.get_date_object()
            else:
                death = None

            # if self.restrict:
            #    alive = probably_alive(pers, self.db)
            # else:
            #    alive = 0

            if birth:
                if death:
                    dates = "%s-%s" % (fdate(birth), fdate(death))
                else:
                    dates = fdate(birth)
            else:
                if death:
                    dates = fdate(death)
                else:
                    dates = ""

            file.write(
                "%s;%s;%s;%s;%s;%s\n" % (name, father, mother, email, web, dates)
            )

        return True


def fdate(val):
    """return properly formatted date"""
    if val.get_year_valid():
        if val.get_month_valid():
            if val.get_day_valid():
                return "%d/%d/%d" % (val.get_day(), val.get_month(), val.get_year())
            return "%d/%d" % (val.get_month(), val.get_year())
        return "%d" % val.get_year()
    return ""


def get_name(name, surname, count):
    """returns a name string built from the components of the Name
    instance, in the form of Firstname Surname"""

    return (
        name.first_name
        + " "
        + surname
        + (str(count) if count != -1 else "")
        + (", " + name.suffix if name.suffix else "")
    )
