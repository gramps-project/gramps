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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

# $Id$

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
import posixpath

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from DataViews import register, Gramplet
from TransUtils import sgettext as _
from Utils import media_path_full
import DateHandler
import gen

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------

_YIELD_INTERVAL = 200

#------------------------------------------------------------------------
#
# Gramplet class
#
#------------------------------------------------------------------------
class StatsGramplet(Gramplet):
    def init(self):
        self.set_text(_("No Family Tree loaded."))
        self.set_tooltip(_("Double-click item to see matches"))

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
        personList = database.iter_people()

        with_photos = 0
        total_photos = 0
        incomp_names = 0
        disconnected = 0
        missing_bday = 0
        males = 0
        females = 0
        unknowns = 0
        bytes = 0
        namelist = []
        notfound = []

        pobjects = database.get_number_of_media_objects()
        for photo_id in database.get_media_object_handles():
            photo = database.get_object_from_handle(photo_id)
            fullname = media_path_full(database, photo.get_path())
            try:
                bytes += posixpath.getsize(fullname)
            except:
                notfound.append(photo.get_path())

        for cnt, person in enumerate(personList):
            length = len(person.get_media_list())
            if length > 0:
                with_photos += 1
                total_photos += length

            names = [person.get_primary_name()] + person.get_alternate_names()
            for name in names:
                if name.get_first_name() == "" or name.get_group_name() == "":
                    incomp_names += 1
                if name.get_group_name() not in namelist:
                    namelist.append(name.get_group_name())
                    
            if (not person.get_main_parents_family_handle() and 
                not len(person.get_family_handle_list())):
                disconnected += 1
                
            birth_ref = person.get_birth_ref()
            if birth_ref:
                birth = database.get_event_from_handle(birth_ref.ref)
                if not DateHandler.get_date(birth):
                    missing_bday += 1
            else:
                missing_bday += 1
                
            if person.get_gender() == gen.lib.Person.FEMALE:
                females += 1
            elif person.get_gender() == gen.lib.Person.MALE:
                males += 1
            else:
                unknowns += 1
            if not cnt % _YIELD_INTERVAL:
                yield True

        self.clear_text()
        self.append_text(_("Individuals") + "\n")
        self.append_text("----------------------------\n")
        self.link(_("Number of individuals") + ":",
                  'Filter', 'all people')
        self.append_text(" %s" % database.get_number_of_people())
        self.append_text("\n")
        self.link("%s:" % _("Males"), 'Filter', 'males')
        self.append_text(" %s" % males)
        self.append_text("\n")
        self.link("%s:" % _("Females"), 'Filter', 'females')
        self.append_text(" %s" % females)
        self.append_text("\n")
        self.link("%s:" % _("Individuals with unknown gender"),
                  'Filter', 'people with unknown gender')
        self.append_text(" %s" % unknowns)
        self.append_text("\n")
        self.link("%s:" % _("Individuals with incomplete names"),
                  'Filter', 'people with incomplete names')
        self.append_text(" %s" % incomp_names)
        self.append_text("\n")
        self.link("%s:" % _("Individuals missing birth dates"),
                  'Filter', 'people with missing birth dates')
        self.append_text(" %s" % missing_bday)
        self.append_text("\n")
        self.link("%s:" % _("Disconnected individuals"),
                  'Filter', 'disconnected people')
        self.append_text(" %s" % disconnected)
        self.append_text("\n")
        self.append_text("\n%s\n" % _("Family Information"))
        self.append_text("----------------------------\n")
        self.link("%s:" % _("Number of families"),
                  'Filter', 'all families')
        self.append_text(" %s" % database.get_number_of_families())
        self.append_text("\n")
        self.link("%s:" % _("Unique surnames"), 
                  'Filter', 'unique surnames')
        self.append_text(" %s" % len(namelist))
        self.append_text("\n")
        self.append_text("\n%s\n" % _("Media Objects"))
        self.append_text("----------------------------\n")
        self.link("%s:" % _("Individuals with media objects"),
                  'Filter', 'people with media')
        self.append_text(" %s" % with_photos)
        self.append_text("\n")
        self.link("%s:" % _("Total number of media object references"),
                  'Filter', 'media references')
        self.append_text(" %s" % total_photos)
        self.append_text("\n")
        self.link("%s:" % _("Number of unique media objects"),
                  'Filter', 'unique media')
        self.append_text(" %s" % pobjects)
        self.append_text("\n")

        self.link("%s:" % _("Total size of media objects"),
                  'Filter', 'media by size')
        self.append_text(" %d %s" % (bytes, _("bytes")))
        self.append_text("\n")
        self.link("%s:" % _("Missing Media Objects"),
                  'Filter', 'missing media')
        self.append_text(" %s\n" % len(notfound))
        self.append_text("", scroll_to="begin")

#------------------------------------------------------------------------
#
# Register Gramplet
#
#------------------------------------------------------------------------
register(type="gramplet", 
         name="Statistics Gramplet", 
         tname=_("Statistics Gramplet"), 
         height=230,
         expand=True,
         content = StatsGramplet,
         title=_("Statistics"),
         )

