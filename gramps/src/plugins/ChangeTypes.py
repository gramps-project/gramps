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

from gtk import *
from gnome.ui import *
from libglade import *

import RelLib
import const
import utils
import intl

_ = intl.gettext

topDialog = None

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_apply_clicked(obj):
    original = topDialog.get_widget("original_text").get_text()
    new = topDialog.get_widget("new_text").get_text()
    
    for person in db.getPersonMap().values():
        for event in person.getEventList():
            if event.getName() == original:
                event.setName(new)
                utils.modified()

    on_close_clicked(obj)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_close_clicked(obj):
    obj.destroy()
    while events_pending():
        mainiteration()

#-------------------------------------------------------------------------
#
#
#-------------------------------------------------------------------------
def runTool(database,person,callback):
    global active_person
    global topDialog
    global glade_file
    global db

    active_person = person
    db = database

    base = os.path.dirname(__file__)
    glade_file = base + os.sep + "changetype.glade"
    topDialog = GladeXML(glade_file,"top")

    topDialog.get_widget("original").set_popdown_strings(const.personalEvents)
    topDialog.get_widget("new").set_popdown_strings(const.personalEvents)

    topDialog.signal_autoconnect({
        "on_close_clicked" : on_close_clicked,
        "on_apply_clicked" : on_apply_clicked
        })
    
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
