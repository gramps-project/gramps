#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Utils
import AutoComp
import const
import RelLib
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# QuickAdd
#
#-------------------------------------------------------------------------
class QuickAdd:
    def __init__(self,db,sex,callback,default_name = ""):
        self.db = db
        self.callback = callback
        
        self.xml = gtk.glade.XML(const.gladeFile,"addperson","gramps")
        self.xml.get_widget(sex).set_active(1)
        self.xml.signal_autoconnect({
            "on_addfather_close": self.close,
            "destroy_passed_object" : Utils.destroy_passed_object
            })

        self.window = self.xml.get_widget("addperson")
        title = self.xml.get_widget('title')
        combo = self.xml.get_widget("surnameCombo")
        self.surname = self.xml.get_widget("surname")
        self.given = self.xml.get_widget("given")
        
        Utils.set_titles(self.window,title, _('Add Person'))
        
        self.c = AutoComp.AutoCombo(combo,self.db.getSurnames())
        if default_name:
            self.surname.set_text(default_name)
            
    def close(self,obj):
        surname = self.surname.get_text()
        given = self.given.get_text()
        person = RelLib.Person()
        name = person.getPrimaryName()
        name.setSurname(surname)
        name.setFirstName(given)
        
        if self.xml.get_widget("male").get_active():
            person.setGender(RelLib.Person.male)
        else:
            person.setGender(RelLib.Person.female)
        self.db.addPerson(person)
        Utils.modified()
        Utils.destroy_passed_object(self.window)
        self.callback(person)
