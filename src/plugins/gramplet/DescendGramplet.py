#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
# Copyright (C) 2008       Douglas S. Blank
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

# $Id$

"""Descendant Gramplet"""

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from DataViews import register, Gramplet
from ReportBase import ReportUtils
from BasicUtils import name_displayer
import DateHandler

class DescendantGramplet(Gramplet):
    def init(self):
        self.set_text(_("No Family Tree loaded."))
        self.set_tooltip(_("Move mouse over links for options"))
        self.set_use_markup(True)
        self.no_wrap()
        self.max_generations = 100

    def db_changed(self):
        self.update()

    def active_changed(self, handle):
        self.update()

    def main(self):
        if self.dbstate.get_active_person() is None:
            self.set_text(_("No Active Person selected."))
            return
        self.set_text("")
        self.center_person =  self.dbstate.get_active_person()
        name = name_displayer.display(self.center_person)
        title = _("Descendants of %s") % name
        self.append_text(title)
        self.append_text("\n\n")
        self.dump(1,self.center_person)
        self.append_text("", scroll_to="begin")

    def dump_dates(self, person):
        birth_date = ""
        birth_ref = person.get_birth_ref()
        if birth_ref:
            birth = self.dbstate.db.get_event_from_handle(birth_ref.ref)
            birth_date = DateHandler.get_date(birth)
        else:
            birth = None

        death_date = ""
        death_ref = person.get_death_ref()
        if death_ref:
            death = self.dbstate.db.get_event_from_handle(death_ref.ref)
            death_date = DateHandler.get_date(death)
        else:
            death = None

        if birth or death:
            self.append_text(' (')

            birth_place = ""
            if birth:
                bplace_handle = birth.get_place_handle()
                if bplace_handle:
                    birth_place = self.dbstate.db.get_place_from_handle(
                        bplace_handle).get_title()

            death_place = ""
            if death:
                dplace_handle = death.get_place_handle()
                if dplace_handle:
                    death_place = self.dbstate.db.get_place_from_handle(
                        dplace_handle).get_title()

            if birth:
                if birth_place:
                    self.append_text(_("b. %(birth_date)s - %(place)s") % {
                        'birth_date' : birth_date,
                        'place' : birth_place,
                        })
                else:
                    self.append_text(_("b. %(birth_date)s") % {
                        'birth_date' : birth_date
                        })

            if death:
                if birth:
                    self.append_text(', ')
                if death_place:
                    self.append_text(_("d. %(death_date)s - %(place)s") % {
                        'death_date' : death_date,
                        'place' : death_place,
                        })
                else:
                    self.append_text(_("d. %(death_date)s") % {
                        'death_date' : death_date
                        })

            self.append_text(')')
        
    def dump(self,level,person):
        self.append_text("    " * (level - 1))
        self.append_text("%s. " % level)
        self.link(name_displayer.display_name(person.get_primary_name()),
                  'Person', person.handle, 
                  tooltip=_("Click to make active\n") + \
                      _("Right-click to edit"))
        self.dump_dates(person)
        self.append_text("\n")

        if level >= self.max_generations:
            return
        
        for family_handle in person.get_family_handle_list():
            family = self.dbstate.db.get_family_from_handle(family_handle)

            spouse_handle = ReportUtils.find_spouse(person,family)
            if spouse_handle:
                spouse = self.dbstate.db.get_person_from_handle(spouse_handle)
                self.append_text("    " * (level - 1))
                self.append_text(_("   sp. ")) 
                self.link(name_displayer.display_name(spouse.get_primary_name()),
                          'Person', spouse.handle, 
                          tooltip=_("Click to make active\n") + \
                              _("Right-click to edit"))
                self.dump_dates(spouse)
                self.append_text("\n")

            childlist = family.get_child_ref_list()[:]
            for child_ref in childlist:
                child = self.dbstate.db.get_person_from_handle(child_ref.ref)
                self.dump(level+1,child)

register(type="gramplet", 
         name = "Descendant Gramplet", 
         tname=_("Descendant Gramplet"), 
         height=100,
         expand=True,
         content = DescendantGramplet,
         title=_("Descendants"),
         detached_width = 500,
         detached_height = 500,
         )
