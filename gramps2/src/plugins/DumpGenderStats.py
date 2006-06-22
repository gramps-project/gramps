#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Martin Hawlisch, Donald N. Allingham
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

"Dump gender stats"

import gtk
import ListModel
import ManagedWindow

from PluginUtils import Tool, register_tool
_GENDER = [ _(u'female'), _(u'male'), _(u'unknown') ]

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class DumpGenderStats(Tool.Tool, ManagedWindow.ManagedWindow):
    
    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        self.label = _("Gender Statistics tool")
        Tool.Tool.__init__(self, dbstate, options_class, name)
        ManagedWindow.ManagedWindow.__init__(self,uistate,[],self.__class__)

        stats_list = []

        for name in dbstate.db.genderStats.stats.keys():
            stats_list.append(
                (name,)
                + dbstate.db.genderStats.stats[name]
                + (_GENDER[dbstate.db.genderStats.guess_gender(name)],)
                )

        if uistate:
            titles = [
                (_('Name'),0,100),
                (_('Male'),1,70,ListModel.INTEGER),
                (_('Female'),2,70,ListModel.INTEGER),
                (_('Unknown'),3,70,ListModel.INTEGER),
                (_('Guess'),4,70)
                ]
        
            treeview = gtk.TreeView()
            model = ListModel.ListModel(treeview,titles)
            for entry in stats_list:
                model.add(entry,entry[0])
                
            window = gtk.Window()
            window.set_default_size(400,300)
            s = gtk.ScrolledWindow()
            s.add(treeview)
            window.add(s)
            window.show_all()
            self.set_window(window,None,self.label)
            self.show()
            
        else:
            print "\t%s\t%s\t%s\t%s\t%s\n" % (
                'Name','Male','Female','Unknown','Guess')
            for entry in stats_list:
                print "\t%s\t%s\t%s\t%s\t%s" % entry

    def build_menu_names(self,obj):
        return (self.label,None)
            
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class DumpGenderStatsOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        Tool.ToolOptions.__init__(self,name,person_id)

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------

if __debug__:
    
    register_tool(
        name = 'dgenstats',
        category = Tool.TOOL_DEBUG,
        tool_class = DumpGenderStats,
        options_class = DumpGenderStatsOptions,
        modes = Tool.MODE_GUI | Tool.MODE_CLI,
        translated_name = _("Dumps gender statistics"),
        description = _("Will dump the statistics for the gender guessing "
                        "from the first name.")
        )
