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

"Database Processing/Rename personal event types"

import os

import gnome.ui
import libglade

import const
import Utils
import intl

_ = intl.gettext

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def runTool(database,person,callback):
    try:
        ChangeTypes(database,person)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

class ChangeTypes:
    def __init__(self,db,person):
        self.person = person
        self.db = db

        base = os.path.dirname(__file__)
        glade_file = "%s/%s" % (base,"changetype.glade")
        self.glade = libglade.GladeXML(glade_file,"top")

        self.glade.get_widget("original").set_popdown_strings(const.personalEvents)
        self.glade.get_widget("new").set_popdown_strings(const.personalEvents)

        self.glade.signal_autoconnect({
            "on_close_clicked"     : Utils.destroy_passed_object,
            "on_combo_insert_text" : Utils.combo_insert_text,
            "on_apply_clicked"     : self.on_apply_clicked
            })
    
    def on_apply_clicked(self,obj):
        modified = 0
        original = self.glade.get_widget("original_text").get_text()
        new = self.glade.get_widget("new_text").get_text()

        for person in self.db.getPersonMap().values():
            for event in person.getEventList():
                if event.getName() == original:
                    event.setName(new)
                    modified = modified + 1
                    Utils.modified()

        if modified == 1:
            msg = _("1 event record was modified")
        else:
            msg = _("%d event records were modified") % modified
            
        gnome.ui.GnomeOkDialog(msg)
        Utils.destroy_passed_object(obj)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_tool

register_tool(
    runTool,
    _("Rename personal event types"),
    category=_("Database Processing"),
    description=_("Allows all the events of a certain name to be renamed to a new name")
    )
