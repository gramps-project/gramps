#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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

"Utilities/Generate SoundEx codes"

import os

import gtk
import gtk.glade

import soundex
import Utils
import AutoComp

from gettext import gettext as _

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

        self.glade = gtk.glade.XML(glade_file,"soundEx","gramps")
        self.glade.signal_autoconnect({
            "destroy_passed_object" : Utils.destroy_passed_object,
        })

        Utils.set_titles(self.glade.get_widget('soundEx'),
                         self.glade.get_widget('title'),
                         _('SoundEx code generator'))

        self.value = self.glade.get_widget("value")
        self.name = self.glade.get_widget("name")

        self.name.connect('changed',self.on_apply_clicked)

        names = []
        for person in self.db.get_person_id_map().values():
            lastname = person.get_primary_name().get_surname()
            if lastname not in names:
                names.append(lastname)

        names.sort()
        self.autocomp = AutoComp.AutoCombo(self.glade.get_widget("nameList"),
                                           names)

        if active_person:
            n = active_person.get_primary_name().get_surname()
            self.name.set_text(n)
            try:
                se_text = soundex.soundex(n)
            except UnicodeEncodeError:
                se_text = soundex.soundex('')
            self.value.set_text(se_text)
        else:
            self.name.set_text("")
            
        self.glade.get_widget("soundEx").show()    

    def on_apply_clicked(self,obj):
        try:
            se_text = soundex.soundex(unicode(obj.get_text()))
        except UnicodeEncodeError:
            se_text = soundex.soundex('')
        self.value.set_text(se_text)

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
