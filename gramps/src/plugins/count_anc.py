#
# count_anc.py - Ancestor counting plugin for gramps
#
# Copyright (C) 2001  Jesper Zedlitz
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

"View/Number of ancestors"

from RelLib import *
import os
import Utils
import intl
_ = intl.gettext

from gtk import *
from gnome.ui import *
from libglade import *

def report(database,person):
    try:
        CountAncestors(database,person)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

class CountAncestors:
    
    def __init__(self,database,person):
        
        text = ""
        base = os.path.dirname(__file__)
        glade_file = base + os.sep + "summary.glade"
        topDialog = GladeXML(glade_file,"summary")
        topDialog.signal_autoconnect({
            "destroy_passed_object" : Utils.destroy_passed_object,
            })
        thisgen = []
        allgen = []
        thisgen.append(person)
        title = _("Number of ancestors of \"%s\" by generation") % person.getPrimaryName().getName()
        text = text + title + ':\n'
        thisgensize=1
        gen=1
        while thisgensize>0:
            thisgensize=0
            if len(thisgen) >0:
                thisgensize=len(thisgen)
                gen= gen-1
                if thisgensize == 1 :
                    text = text + _("Generation %d has 1 individual.\n") % (gen)
                else:
                    text = text + _("Generation %d has %d individuals.\n") % (gen, thisgensize)
            temp = thisgen
            thisgen = []
            for person in temp:
                family = person.getMainParents()
                if family != None:
                    father = family.getFather()
                    mother = family.getMother()
                    if father != None:
                        thisgen.append(father)
                    if mother != None:
                        thisgen.append(mother)
            allgen = allgen + thisgen
	  
        text = text + _("Total ancestors in generations %d to -1 is %d .\n") % (gen, len(allgen))

        top = topDialog.get_widget("summary")
        textwindow = topDialog.get_widget("textwindow")
        topDialog.get_widget("summaryTitle").set_text(title)
        textwindow.show_string(text)
        top.show()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from Plugins import register_report

register_report(
    report,
    _("Number of ancestors"),
    category=_("View"),
    description=_("Counts number of ancestors of selected person")
    )

