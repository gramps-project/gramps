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
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

#------------------------------------------------------------------------
#
# RelativesGramplet class
#
#------------------------------------------------------------------------
class RelativesGramplet(Gramplet):
    """
    This gramplet gives a list of clickable relatives of the active person.
    Clicking them, changes the active person.
    """
    def init(self):
        self.set_text(_("No Family Tree loaded."))
        self.set_tooltip(_("Click name to make person active\n") +
                         _("Right-click name to edit person"))

    def db_changed(self):
        """
        If person or family changes, the relatives of active person might have
        changed
        """
        self.connect(self.dbstate.db, 'person-add', self.update)
        self.connect(self.dbstate.db, 'person-delete', self.update)
        self.connect(self.dbstate.db, 'family-add', self.update)
        self.connect(self.dbstate.db, 'family-delete', self.update)
        self.connect(self.dbstate.db, 'person-rebuild', self.update)
        self.connect(self.dbstate.db, 'family-rebuild', self.update)

    def active_changed(self, handle):
        self.update()

    def main(self): # return false finishes
        """
        Generator which will be run in the background.
        """
        self.set_text("")
        database = self.dbstate.db
        active_handle = self.get_active('Person')
        if not active_handle:
            return
        active_person = self.dbstate.db.get_person_from_handle(active_handle)
        if not active_person:
            return
        name = name_displayer.display(active_person)
        self.append_text(_("Active person: %s") % name)
        self.append_text("\n\n")
        #obtain families
        famc = 0
        for family_handle in active_person.get_family_handle_list():
            famc += 1
            family = database.get_family_from_handle(family_handle)
            if not family: continue
            if active_person.handle == family.get_father_handle():
                spouse_handle = family.get_mother_handle()
            else:
                spouse_handle = family.get_father_handle()
            if spouse_handle:
                spouse = database.get_person_from_handle(spouse_handle)
                spousename = name_displayer.display(spouse)
                text = "%s" %  spousename
                self.append_text(_("%(count)d. %(relation)s: ") %
                                   {"count": famc,
                                    "relation": family.get_relationship()})
                self.link(text, 'Person', spouse_handle)
                self.append_text("\n")
            else:
                self.append_text(_("%d. Partner: Not known") % (famc))
                self.append_text("\n")
            #obtain children
            childc = 0
            for child_ref in family.get_child_ref_list():
                childc += 1
                child = database.get_person_from_handle(child_ref.ref)
                childname = name_displayer.display(child)
                text = "%s" %  childname
                self.append_text("   %d.%-3d: " % (famc, childc))
                self.link(text, 'Person', child_ref.ref)
                self.append_text("\n")
            yield True
        #obtain parent families
        self.append_text("\n")
        self.append_text(_("Parents:"))
        self.append_text("\n")
        famc = 0
        for family_handle in active_person.get_parent_family_handle_list():
            famc += 1
            family = database.get_family_from_handle(family_handle)
            mother_handle = family.get_mother_handle()
            father_handle = family.get_father_handle()
            if mother_handle:
                mother = database.get_person_from_handle(mother_handle)
                mothername = name_displayer.display(mother)
                text = "%s" %  mothername
                self.append_text(_("   %d.a Mother: ") % (famc))
                self.link(text, 'Person', mother_handle)
                self.append_text("\n")
            else:
                self.append_text(_("   %d.a Mother: ") % (famc))
                self.append_text(_("Unknown"))
                self.append_text("\n")
            if father_handle:
                father = database.get_person_from_handle(father_handle)
                fathername = name_displayer.display(father)
                text = "%s" %  fathername
                self.append_text(_("   %d.b Father: ") % (famc))
                self.link(text, 'Person', father_handle)
                self.append_text("\n")
            else:
                self.append_text(_("   %d.b Father: ") % (famc))
                self.append_text(_("Unknown"))
                self.append_text("\n")
