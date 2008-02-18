#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

"""Tools/Database Processing/Fix Capitalization of Family Names..."""

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import os
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# gnome/gtk
#
#-------------------------------------------------------------------------
import gobject
import gtk
from gtk import glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Utils
import GrampsDisplay
import ManagedWindow

from QuestionDialog import OkDialog
from PluginUtils import Tool, register_tool

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------

prefix_list = [
    "de", "van", "von", "di", "le", "du", "dela", "della",
    "des", "vande", "ten", "da", "af", "den", "das", "dello",
    "del", "en", "ein", "el" "et", "les", "lo", "los", "un",
    "um", "una", "uno",
    ]



#-------------------------------------------------------------------------
#
# ChangeNames
#
#-------------------------------------------------------------------------
class ChangeNames(Tool.BatchTool, ManagedWindow.ManagedWindow):

    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        self.label = _('Capitalization changes')
        self.cb = callback
        
        ManagedWindow.ManagedWindow.__init__(self,uistate,[],self.__class__)
        self.set_window(gtk.Window(),gtk.Label(),'')

        Tool.BatchTool.__init__(self, dbstate, options_class, name)
        if self.fail:
            return

        self.progress = Utils.ProgressMeter(_('Checking Family Names'),'')
        self.progress.set_pass(_('Searching family names'),
                               len(self.db.get_surname_list()))
        self.name_list = []
        
        for name in self.db.get_surname_list():
            name.strip()            
            namesplitSP= name.split()
            lSP = len(namesplitSP)
            namesplitHY= name.split('-')
            lHY = len(namesplitHY)
            if lSP == 1 and lHY == 1:
                if name != name.capitalize():
                    # Single surname without hyphen(s)
                    self.name_list.append(name)
            #if lSP == 1 and lHY > 1:
                #print "LSP==1",name,name.capitalize()
                #if name != name.capitalize():
                    # Single surname with hyphen(s)
                    #self.name_list.append(name)
            if lSP>1 and lHY == 1:
                # more than one string in surname but no hyphen
                # check if first string is in prefix_list, if so test for cap in rest
                s1 = 0
                if namesplitSP[0].lower() in prefix_list:
                    s1 = 1
                for x in range(len(namesplitSP)-s1):
                    # check if any subsurname is not cap
                    notcap = False
                    if namesplitSP[s1+x] != namesplitSP[s1+x].capitalize():
                        notcap = True
                        break
                if notcap:
                    # Multiple surnames possibly after prefix
                    self.name_list.append(name)
            if lHY > 1:
                # more than one string in surname but hyphen(s) exists
                # check if first string is in prefix_list, if so test for cap
                if namesplitSP[0].lower() in prefix_list:
                    namesplitHY[0] = namesplitHY[0].replace(namesplitSP[0],'').strip()
                for x in range(len(namesplitHY)):
                    # check if any subsurname is not cap
                    notcap = False
                    if namesplitHY[x] != namesplitHY[x].capitalize():
                        notcap = True
                        break
                if notcap:
                    # Multiple surnames possibly after frefix
                    self.name_list.append(name)
                    
            if uistate:
                self.progress.step()
        
        if self.name_list:
            self.display()
        else:
            self.progress.close()
            self.close()
            OkDialog(_('No modifications made'),
                     _("No capitalization changes were detected."))

    def name_cap(self,name):
        name.strip()            
        namesplitSP = name.split()
        lSP = len(namesplitSP)
        lHY = len(name.split('-'))
        namesep = ' '
        if lHY > 1:
            namesep = '-'
            namesplitSP = name.replace(namesep,' ').split()
            lSP= len(namesplitSP)
        if lSP == 1 and lHY == 1:
            #if name != name.capitalize():
            # Single surname without space(s) or hyphen(s), normal case
            return name.capitalize()
        else: 
            # more than one string in surname but no hyphen
            # check if first string is in prefix_list, if so CAP the rest
            # Names like (von) Kohl(-)Brandt 
            result = ""
            s1 = 0
            if namesplitSP[0].lower() in prefix_list:
                s1 = 1
                result = namesplitSP[0].lower()+ ' '
            for x in range(lSP-s1):
                # CAP all subsurnames
                result = result + namesplitSP[s1+x].capitalize() + namesep
            return result[:-1]

    def display(self):

        base = os.path.dirname(__file__)
        glade_file = os.path.join(base,"changenames.glade")
        
        self.top = glade.XML(glade_file,"top","gramps")
        window = self.top.get_widget('top')
        self.top.signal_autoconnect({
            "destroy_passed_object" : self.close,
            "on_ok_clicked" : self.on_ok_clicked,
            "on_help_clicked" : self.on_help_clicked,
            })
        
        self.list = self.top.get_widget("list")
        self.set_window(window,self.top.get_widget('title'),self.label)

        self.model = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING, 
                                   gobject.TYPE_STRING)

        r = gtk.CellRendererToggle()
        r.connect('toggled',self.toggled)
        c = gtk.TreeViewColumn(_('Select'),r,active=0)
        self.list.append_column(c)

        c = gtk.TreeViewColumn(_('Original Name'),
                               gtk.CellRendererText(),text=1)
        self.list.append_column(c)

        c = gtk.TreeViewColumn(_('Capitalization Change'),
                               gtk.CellRendererText(),text=2)
        self.list.append_column(c)

        self.list.set_model(self.model)

        self.iter_list = []
        self.progress.set_pass(_('Building display'),len(self.name_list))
        for name in self.name_list:
            handle = self.model.append()
            self.model.set_value(handle,0,True)
            self.model.set_value(handle,1,name)
            namecap = self.name_cap(name)
            self.model.set_value(handle,2,namecap)
            self.iter_list.append(handle)
            self.progress.step()
        self.progress.close()
            
        self.show()

    def toggled(self,cell,path_string):
        path = tuple([int (i) for i in path_string.split(':')])
        row = self.model[path]
        row[0] = not row[0]

    def build_menu_names(self,obj):
        return (self.label,None)

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('tools-db')

    def on_ok_clicked(self,obj):
        self.trans = self.db.transaction_begin("",batch=True)
        self.db.disable_signals()
        changelist = [self.model.get_value(node,1)
                      for node in self.iter_list
                      if self.model.get_value(node,0)]

        for handle in self.db.get_person_handles():
            change = False
            person = self.db.get_person_from_handle(handle)
            for name in [person.get_primary_name()] + person.get_alternate_names():
                sname = name.get_surname()
                if sname in changelist:
                    change = True
                    sname = self.name_cap(sname)
                    name.set_surname(sname)
            if change:
                self.db.commit_person(person,self.trans)

        self.db.transaction_commit(self.trans,_("Capitalization changes"))
        self.db.enable_signals()
        self.db.request_rebuild()
        # FIXME: this probably needs to be removed, and bookmarks
        # should always be rebuilt on a commit_person via signals
        # self.parent.bookmarks.redraw()
        self.close()
        self.cb()
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class ChangeNamesOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        Tool.ToolOptions.__init__(self,name,person_id)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_tool(
    name = 'chname',
    category = Tool.TOOL_DBPROC,
    tool_class = ChangeNames,
    options_class = ChangeNamesOptions,
    modes = Tool.MODE_GUI,
    translated_name = _("Fix Capitalization of Family Names..."),
    status = _("Stable"),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description = _("Searches the entire database and attempts to "
                    "fix capitalization of the names.")
    )
