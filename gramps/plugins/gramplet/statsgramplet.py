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

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
import posixpath

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gen.utils.file import media_path_full
from gramps.gen.datehandler import get_date
from gramps.gen.lib import Person
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------

_YIELD_INTERVAL = 200

#------------------------------------------------------------------------
#
# StatsGramplet class
#
#------------------------------------------------------------------------
class StatsGramplet(Gramplet):
    def init(self):
        self.set_text(_("No Family Tree loaded."))
        self.set_tooltip(_("Double-click item to see matches"))

    def active_changed(self, handle):
        self.update()

    def db_changed(self):
        self.dbstate.db.connect('person-add', self.update)
        self.dbstate.db.connect('person-edit', self.update)
        self.dbstate.db.connect('person-delete', self.update)
        self.dbstate.db.connect('family-add', self.update)
        self.dbstate.db.connect('family-delete', self.update)
        self.dbstate.db.connect('person-rebuild', self.update)
        self.dbstate.db.connect('family-rebuild', self.update)

    def main(self):
        self.set_text(_("Processing..."))
        database = self.dbstate.db

        total_media = 0
        males = 0
        females = 0
        unknowns = 0
        bytes = 0
        notfound = []

        mobjects = database.get_number_of_media()
        mbytes = "0"
        for media in database.iter_media():
            fullname = media_path_full(database, media.get_path())
            try:
                bytes += posixpath.getsize(fullname)
                length = len(str(bytes))
                if bytes <= 999999:
                    mbytes = _("less than 1")
                else:
                    mbytes = str(bytes)[:(length-6)]
            except OSError:
                notfound.append(media.get_path())

        if hasattr(database, 'genderStats'):
            males = sum([v[0] for v in database.genderStats.stats.values()])
            females = sum([v[1] for v in database.genderStats.stats.values()])
            unknowns = sum([v[2] for v in database.genderStats.stats.values()])

        self.clear_text()
        self.append_text(_("Individuals") + "\n")
        self.append_text("----------------------------\n")
        self.link(_("Number of individuals") + ":",
                  'Filter', 'all people')
        self.append_text(" %s" % database.get_number_of_people())
        self.append_text("\n")
        self.link(_("%s:") % _("Males"), 'Filter', 'males')
        self.append_text(" %s" % males)
        self.append_text("\n")
        self.link(_("%s:") % _("Females"), 'Filter', 'females')
        self.append_text(" %s" % females)
        self.append_text("\n")
        self.link(_("%s:") % _("Individuals with unknown gender"),
                  'Filter', 'people with unknown gender')
        self.append_text(" %s" % unknowns)
        self.append_text("\n")
        self.append_text("\n%s\n" % _("Family Information"))
        self.append_text("----------------------------\n")
        self.link(_("%s:") % _("Number of families"),
                  'Filter', 'all families')
        self.append_text(" %s" % database.get_number_of_families())
        self.append_text("\n")
        if hasattr(database, 'surname_list'):
            self.link(_("%s:") % _("Unique surnames"),
                      'Filter', 'unique surnames')
            self.append_text(" %s" % len(set(database.surname_list)))
            self.append_text("\n")
        self.append_text("\n%s\n" % _("Media Objects"))
        self.append_text("----------------------------\n")
        self.link(_("%s:") % _("Total number of media object references"),
                  'Filter', 'media references')
        self.append_text(" %s" % total_media)
        self.append_text("\n")
        self.link(_("%s:") % _("Number of unique media objects"),
                  'Filter', 'unique media')
        self.append_text(" %s" % mobjects)
        self.append_text("\n")

        self.link(_("%s:") % _("Total size of media objects"),
                  'Filter', 'media by size')
        self.append_text(" %s %s" % (mbytes, _("Megabyte|MB")))
        self.append_text("\n")
        self.link(_("%s:") % _("Missing Media Objects"),
                  'Filter', 'missing media')
        self.append_text(" %s\n" % len(notfound))
        self.append_text("", scroll_to="begin")
