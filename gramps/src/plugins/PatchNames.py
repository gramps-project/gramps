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
_ = intl.gettext

from gnome.ui import *

import RelLib
import utils

#-------------------------------------------------------------------------
#
# Search each name in the database, and compare the firstname against the
# form of "Name (Nickname)".  If it matches, change the first name entry
# to "Name" and add "Nickname" into the nickname field.
#
#-------------------------------------------------------------------------
def runTool(database,active_person,callback):

    title_re = re.compile(r"^([A-Za-z][A-Za-z]+\.)\s+(.*)$")
    nick_re = re.compile(r"(.+)[(\"](.*)[)\"]")
    title_count = 0
    nick_count = 0
    
    personMap = database.getPersonMap()
    for key in personMap.keys():
        
        person = personMap[key] 
        name = person.getPrimaryName()
        first = name.getFirstName()
        match = title_re.match(first)
        if match:
            groups = match.groups()
            name.setFirstName(groups[1])
            name.setTitle(groups[0])
            title_count = title_count + 1
        match = nick_re.match(first)
        if match:
            groups = match.groups()
            name.setFirstName(groups[0])
            person.setNickName(groups[1])
            nick_count = nick_count + 1

    if nick_count == 1:
        msg = _("1 nickname was extracted")
    else:
        msg = _("%d nicknames were extracted\n") % nick_count

    if title_count == 1:
        msg = msg + "\n" + _("1 title was extracted")
    else:
        msg = msg + "\n" + _("%d titles were extracted") % title_count

    if nick_count > 0 or title_count > 0:
        utils.modified()
        
    box = GnomeOkDialog(msg)
    box.show()
    callback(1)
        
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def get_description():
    return _("Searches the entire database and attempts to extract titles and nicknames that may be embedded in a person's given name field.")

def get_name():
    return _("Database Processing/Extract information from names")






