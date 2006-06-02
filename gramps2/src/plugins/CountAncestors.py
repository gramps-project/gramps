#
# count_anc.py - Ancestor counting plugin for gramps
#
# Copyright (C) 2001  Jesper Zedlitz
# Copyright (C) 2004-2006  Donald Allingham
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

"View/Number of ancestors"

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import os
from gettext import gettext as _
from math import pow
try:
    set()
except NameError:
    from sets import Set as set

#------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#------------------------------------------------------------------------
import gtk.glade

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from PluginUtils import register_report
from ReportBase import CATEGORY_VIEW, MODE_GUI
import ManagedWindow

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class CountAncestors(ManagedWindow.ManagedWindow):
    
    def __init__(self,dbstate,uistate,person):
        self.title = _('Ancestors of "%s"') \
                     % person.get_primary_name().get_name()

        ManagedWindow.ManagedWindow.__init__(self,uistate,[],self.__class__)

        database = dbstate.db        
        text = ""
        glade_file = "%s/summary.glade" % os.path.dirname(__file__)
        topDialog = gtk.glade.XML(glade_file,"summary","gramps")
        topDialog.signal_autoconnect({
            "destroy_passed_object" : self.close,
            })
        thisgen = set()
        all = set()
        allgen = 0
        total_theoretical = 0
        thisgen.add(person.get_handle())
        

        window = topDialog.get_widget("summary")
        title = topDialog.get_widget("title")
        self.set_window(window,title,self.title)

        thisgensize = 1
        gen = 0
        while thisgensize > 0:
            thisgensize = 0
            if thisgen:
                thisgensize = len( thisgen )
                gen += 1
                theoretical = pow(2, ( gen - 1 ) )
                total_theoretical += theoretical
                percent = ( thisgensize / theoretical ) * 100
                if thisgensize == 1 :
                    text += _("Generation %d has 1 individual. (%3.2f%%)\n") \
                            % (gen,percent)
                else:
                    text += _("Generation %d has %d individuals. (%3.2f%%)\n")\
                            % (gen,thisgensize,percent)
            temp = thisgen
            thisgen = set()
            for person_handle in temp:
                person = database.get_person_from_handle(person_handle)
                family_handle = person.get_main_parents_family_handle()
                if family_handle:
                    family = database.get_family_from_handle(family_handle)
                    father_handle = family.get_father_handle()
                    mother_handle = family.get_mother_handle()
                    if father_handle and father_handle not in all:
                        thisgen.add(father_handle)
                        all.add(father_handle)
                    if mother_handle and mother_handle not in all:
                        thisgen.add(mother_handle)
                        all.add(mother_handle)
            allgen += len(thisgen)

        if( total_theoretical != 1 ):
            percent = ( (allgen) / (total_theoretical-1) ) * 100
        else:
            percent = 0

        text += _("Total ancestors in generations 2 to %d is %d. (%3.2f%%)\n")\
                % (gen,allgen,percent)

        textwindow = topDialog.get_widget("textwindow")
        textwindow.get_buffer().set_text(text)
        self.show()

    def build_menu_names(self,obj):
        return (self.title,None)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
register_report(
    name = 'count_ancestors',
    category = CATEGORY_VIEW,
    report_class = CountAncestors,
    options_class = None,
    modes = MODE_GUI,
    translated_name = _("Number of ancestors"),
    status = _("Stable"),
    description= _("Counts number of ancestors of selected person")
    )
