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
import utils

topDialog = None

#-------------------------------------------------------------------------
#
#
#-------------------------------------------------------------------------
def on_apply_clicked(obj):
    
    text = obj.get_text()
    value = topDialog.get_widget("value").set_text(soundex.soundex(text))
    
#-------------------------------------------------------------------------
#
#
#-------------------------------------------------------------------------
def runTool(database,active_person,callback):
    global topDialog
    
    base = os.path.dirname(__file__)
    glade_file = base + os.sep + "soundex.glade"

    topDialog = GladeXML(glade_file,"soundEx")
    topDialog.signal_autoconnect({
        "destroy_passed_object" : utils.destroy_passed_object,
        "on_apply_clicked" : on_apply_clicked
        })

    names = []
    for person in database.getPersonMap().values():
        lastname = person.getPrimaryName().getSurname()
        if lastname not in names:
            names.append(lastname)

    names.sort()
    topDialog.get_widget("nameList").set_popdown_strings(names)
    topDialog.get_widget("name").set_text("")
    topDialog.get_widget("soundEx").show()    

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_description():
    return _("Generates SoundEx codes for names")
