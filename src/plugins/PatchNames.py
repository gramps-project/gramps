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

"Database Processing/Extract information from names"

import os
import re
import intl
import utils

_ = intl.gettext

from gnome.ui import *

import libglade
import RelLib
import utils

title_list = []
nick_list = []
cb = None

#-------------------------------------------------------------------------
#
# Search each name in the database, and compare the firstname against the
# form of "Name (Nickname)".  If it matches, change the first name entry
# to "Name" and add "Nickname" into the nickname field.
#
#-------------------------------------------------------------------------
def runTool(database,active_person,callback):

    global cb

    cb = callback
    title_re = re.compile(r"^([A-Za-z][A-Za-z]+\.)\s+(.*)$")
    nick_re = re.compile(r"(.+)[(\"](.*)[)\"]")
    
    personMap = database.getPersonMap()
    for key in personMap.keys():
        
        person = personMap[key]
        first = person.getPrimaryName().getFirstName()
        match = title_re.match(first)
        if match:
            groups = match.groups()
            title_list.append((person,groups[0],groups[1]))

        match = nick_re.match(first)
        if match:
            groups = match.groups()
            nick_list.append((person,groups[0],groups[1]))

    msg = ""
    if len(nick_list) > 0 or len(title_list) > 0:
        if len(nick_list) > 0:
            for name in nick_list:
                msg = msg + _("%s will be extracted as a nickname from %s\n") % \
                      (name[2],name[0].getPrimaryName().getName())

        if len(title_list) > 0:
            for name in title_list:
                msg = msg + _("%s will be extracted as a title from %s\n") % \
                      (name[0].getPrimaryName().getName(),name[1])

        base = os.path.dirname(__file__)
        glade_file = base + os.sep + "patchnames.glade"

        top = libglade.GladeXML(glade_file,"summary")
        top.signal_autoconnect({
            "destroy_passed_object" : utils.destroy_passed_object,
            "on_ok_clicked" : on_ok_clicked
            })
        top.get_widget("textwindow").show_string(msg)
    else:
        GnomeOkDialog(_("No titles or nicknames were found"))
        callback(0)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def on_ok_clicked(obj):
    for grp in nick_list:
        name = grp[0].getPrimaryName()
        name.setFirstName(grp[1])
        grp[0].setNickName(grp[2])
        utils.modified()

    for grp in title_list:
        name = grp[0].getPrimaryName()
        name.setFirstName(grp[2])
        name.setTitle(grp[1])
        utils.modified()

    utils.destroy_passed_object(obj)
    cb(1)
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_tool

register_tool(
    runTool,
    _("Extract information from names"),
    category=_("Database Processing"),
    description=_("Searches the entire database and attempts to extract titles and nicknames that may be embedded in a person's given name field.")
    )



