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

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import os
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
import collections
log = logging.getLogger(".WriteFtree")

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.utils.alive import probably_alive
from gramps.gui.plug.export import WriterOptionBox
from gramps.gui.glade import Glade

#-------------------------------------------------------------------------
#
# writeData
#
#-------------------------------------------------------------------------
def writeData(database, filename, user, option_box=None):
    writer = FtreeWriter(database, filename, user, option_box)
    return writer.export_data()

#-------------------------------------------------------------------------
#
# FtreeWriter
#
#-------------------------------------------------------------------------
class FtreeWriter:

    def __init__(self, database, filename, user, option_box=None):
        self.db = database
        self.filename = filename
        self.user = user
        self.option_box = option_box
        if isinstance(self.user.callback, collections.Callable): # callback is really callable
            self.update = self.update_real
        else:
            self.update = self.update_empty

        if option_box:
            self.option_box.parse_options()
            self.db = option_box.get_filtered_database(self.db)

        self.plist = [x for x in self.db.iter_person_handles()]

    def update_empty(self):
        pass

    def update_real(self):
        self.count += 1
        newval = int(100*self.count/self.total)
        if newval != self.oldval:
            self.user.callback(newval)
            self.oldval = newval

    def export_data(self):
        name_map = {}
        id_map = {}
        id_name = {}
        self.count = 0
        self.oldval = 0
        self.total = 2*len(self.plist)

        for key in self.plist:
            self.update()
            pn = self.db.get_person_from_handle(key).get_primary_name()
            sn = pn.get_surname()
            items = pn.get_first_name().split()
            n = ("%s %s" % (items[0], sn)) if items else sn

            count = -1
            if n in name_map:
                count = 0
                while 1:
                    nn = "%s%d" % (n, count)
                    if nn not in name_map:
                        break;
                    count += 1
                name_map[nn] = key
                id_map[key] = nn
            else:
                name_map[n] = key
                id_map[key] = n
            id_name[key] = get_name(pn, sn, count)

        with open(self.filename,"w") as f:

            for key in self.plist:
                self.update()
                p = self.db.get_person_from_handle(key)
                name = id_name[key]
                father = mother = email = web = ""

                family_handle = p.get_main_parents_family_handle()
                if family_handle:
                    family = self.db.get_family_from_handle(family_handle)
                    if family.get_father_handle() and \
                      family.get_father_handle() in id_map:
                        father = id_map[family.get_father_handle()]
                    if family.get_mother_handle() and \
                      family.get_mother_handle() in id_map:
                        mother = id_map[family.get_mother_handle()]

                #
                # Calculate Date
                #
                birth_ref = p.get_birth_ref()
                death_ref = p.get_death_ref()
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

                #if self.restrict:
                #    alive = probably_alive(p, self.db)
                #else:
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

                f.write('%s;%s;%s;%s;%s;%s\n' % (name, father, mother, email, web,
                                                 dates))

            return True

def fdate(val):
    if val.get_year_valid():
        if val.get_month_valid():
            if val.get_day_valid():
                return "%d/%d/%d" % (val.get_day(), val.get_month(),
                                     val.get_year())
            else:
                return "%d/%d" % (val.get_month(), val.get_year())
        else:
            return "%d" % val.get_year()
    else:
        return ""

def get_name(name, surname, count):
    """returns a name string built from the components of the Name
    instance, in the form of Firstname Surname"""

    return (name.first_name + ' ' +
           surname +
           (str(count) if count != -1 else '') +
           (', ' +name.suffix if name.suffix else '')
           )
