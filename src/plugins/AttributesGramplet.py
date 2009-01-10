# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Douglas S. Blank
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

from DataViews import Gramplet, register
from BasicUtils import name_displayer

class AttributesGramplet(Gramplet):
    """
    Displays attributes of a person.
    """
    def init(self):
        self.set_text(_("No Family Tree loaded."))
        self.set_use_markup(True)
        self.no_wrap()

    def db_changed(self):
        self.dbstate.db.connect('person-edit', self.update)
        self.update()

    def active_changed(self, handle):
        self.update()

    def main(self): # return false finishes
        self.set_text("")
        active_person = self.dbstate.get_active_person()
        if not active_person:
            return
        name = name_displayer.display(active_person)
        self.render_text(_("Active person: <b>%s</b>") % name)
        self.append_text("\n\n")
        for attr in active_person.attribute_list:
            # # text, type, data
            self.link(str(attr.type), 'Attribute', str(attr.type)) 
            self.append_text(": %s\n" % attr.get_value())
        self.append_text("\n", scroll_to="begin")
        
register(type="gramplet", 
         name="Attributes Gramplet", 
         tname=_("Attributes Gramplet"), 
         height=150,
         expand=True,
         content = AttributesGramplet,
         title=_("Attributes"),
         detached_width = 325,
         detached_height = 250,
         )

