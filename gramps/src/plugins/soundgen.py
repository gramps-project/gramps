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

"Utilities/Generate SoundEx codes"

import os

from gtk import *
from gnome.ui import *
from libglade import *

import RelLib
import soundex
import Utils
import intl

_ = intl.gettext

#-------------------------------------------------------------------------
#
#
#-------------------------------------------------------------------------
def runTool(database,active_person,callback):
    SoundGen(database,active_person)


class SoundGen:
    def __init__(self,database,active_person):
        self.db = database
        
        base = os.path.dirname(__file__)
        glade_file = base + os.sep + "soundex.glade"

        self.glade = GladeXML(glade_file,"soundEx")
        self.glade.signal_autoconnect({
            "destroy_passed_object" : Utils.destroy_passed_object,
            "on_combo_insert_text"  : Utils.combo_insert_text,
            "on_apply_clicked"      : self.on_apply_clicked,
        })

        self.value = self.glade.get_widget("value")
        self.name = self.glade.get_widget("name")
        names = []
        for person in self.db.getPersonMap().values():
            lastname = person.getPrimaryName().getSurname()
            if lastname not in names:
                names.append(lastname)

        names.sort()
        self.glade.get_widget("nameList").set_popdown_strings(names)

        if active_person:
            n = active_person.getPrimaryName().getSurname()
            self.name.set_text(n)
            self.value.set_text(soundex.soundex(n))
        else:
            self.name.set_text("")
            
        self.glade.get_widget("soundEx").show()    

    def on_apply_clicked(self,obj):
        self.value.set_text(soundex.soundex(obj.get_text()))

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from Plugins import register_tool

register_tool(
    runTool,
    _("Generate SoundEx codes"),
    category=_("Utilities"),
    description=_("Generates SoundEx codes for names")
    )


