#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

"Database Processing/Extract information from names"

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import os
import re
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# gnome/gtk
#
#-------------------------------------------------------------------------
import gobject
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Utils
from PluginUtils import Tool, register_tool
from QuestionDialog import OkDialog
import ManagedWindow
import GrampsDisplay
import RelLib

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


_title_re = re.compile(r"^([A-Za-z][A-Za-z]+\.)\s+(.*)$")
_nick_re = re.compile(r"(.+)\s*[(\"](.*)[)\"]")
_fn_prefix_re = re.compile("(.*)\s+(%s)\s*$" % '|'.join(prefix_list),
                           re.IGNORECASE)
_sn_prefix_re = re.compile("^\s*(%s)\s+(.*)" % '|'.join(prefix_list),
                           re.IGNORECASE)
                
#-------------------------------------------------------------------------
#
# Search each name in the database, and compare the firstname against the
# form of "Name (Nickname)".  If it matches, change the first name entry
# to "Name" and add "Nickname" into the nickname field.
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# PatchNames
#
#-------------------------------------------------------------------------
class PatchNames(Tool.BatchTool, ManagedWindow.ManagedWindow):
    
    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        self.label = _('Name and title extraction tool')
        ManagedWindow.ManagedWindow.__init__(self,uistate,[],self.__class__)
        self.set_window(gtk.Window(),gtk.Label(),'')
       
        Tool.BatchTool.__init__(self, dbstate, options_class, name)
        if self.fail:
            return

        self.cb = callback
        self.title_list = []
        self.nick_list = []
        self.prefix1_list = []
        self.prefix2_list = []

        self.progress = Utils.ProgressMeter(
            _('Extracting information from names'),'')
        self.progress.set_pass(_('Analyzing names'),
                               self.db.get_number_of_people())

        for key in self.db.get_person_handles(sort_handles=False):
        
            person = self.db.get_person_from_handle(key)
            name = person.get_primary_name()
            first = name.get_first_name()
            sname = name.get_surname()

            if name.get_title():
                old_title = [name.get_title()]
            else:
                old_title = []
            new_title = []

            match = _title_re.match(first)
            while match:
                groups = match.groups()
                first = groups[1]
                new_title.append(groups[0])
                match = _title_re.match(first)

            if new_title:
                self.title_list.append((key," ".join(old_title+new_title),
                                        first))
                continue
            
            match = _nick_re.match(first)
            if match:
                groups = match.groups()
                self.nick_list.append((key,groups[0],groups[1]))
                continue

            old_prefix = name.get_surname_prefix()

            match = _fn_prefix_re.match(first)
            if match:
                groups = match.groups()
                self.prefix1_list.append((key,groups[0],
                                          " ".join([groups[1],old_prefix]))
                                         )
                continue
            
            match = _sn_prefix_re.match(sname)
            if match:
                groups = match.groups()
                self.prefix2_list.append((key,groups[1],
                                          " ".join([old_prefix,groups[0]]))
                                         )

            self.progress.step()

        if self.nick_list or self.title_list or self.prefix1_list or self.prefix2_list:
            self.display()
        else:
            self.progress.close()
            self.close()
            OkDialog(_('No modifications made'),
                     _("No titles or nicknames were found"))

    def build_menu_names(self,obj):
        return (self.label,None)

    def toggled(self,cell,path_string):
        path = tuple([int (i) for i in path_string.split(':')])
        row = self.model[path]
        row[0] = not row[0]
        self.model.row_changed(path,row.iter)

    def display(self):

        base = os.path.dirname(__file__)
        glade_file = base + os.sep + "patchnames.glade"
        
        self.top = gtk.glade.XML(glade_file,"top","gramps")
        window = self.top.get_widget('top')
        self.top.signal_autoconnect({
            "destroy_passed_object" : self.close,
            "on_ok_clicked" : self.on_ok_clicked,
            "on_help_clicked"       : self.on_help_clicked,
            })
        self.list = self.top.get_widget("list")
        self.set_window(window,self.top.get_widget('title'),self.label)

        self.model = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING, gobject.TYPE_STRING,
                                   gobject.TYPE_STRING)

        r = gtk.CellRendererToggle()
        r.connect('toggled',self.toggled)
        c = gtk.TreeViewColumn(_('Select'),r,active=0)
        self.list.append_column(c)

        c = gtk.TreeViewColumn(_('ID'),gtk.CellRendererText(),text=1)
        self.list.append_column(c)

        c = gtk.TreeViewColumn(_('Type'),gtk.CellRendererText(),text=2)
        self.list.append_column(c)

        c = gtk.TreeViewColumn(_('Value'),gtk.CellRendererText(),text=3)
        self.list.append_column(c)

        c = gtk.TreeViewColumn(_('Name'),gtk.CellRendererText(),text=4)
        self.list.append_column(c)

        self.list.set_model(self.model)

        self.nick_hash = {}
        self.title_hash = {}
        self.prefix1_hash = {}
        self.prefix2_hash = {}

        self.progress.set_pass(_('Bulding display'),
                               len(self.nick_list)+len(self.title_list)
                               +len(self.prefix1_list)+len(self.prefix2_list))

        for (id,name,nick) in self.nick_list:
            p = self.db.get_person_from_handle(id)
            gid = p.get_gramps_id()
            handle = self.model.append()
            self.model.set_value(handle,0,1)
            self.model.set_value(handle,1,gid)
            self.model.set_value(handle,2,_('Nickname'))
            self.model.set_value(handle,3,nick)
            self.model.set_value(handle,4,p.get_primary_name().get_name())
            self.nick_hash[id] = handle
            self.progress.step()
            
        for (id,title,name) in self.title_list:
            p = self.db.get_person_from_handle(id)
            gid = p.get_gramps_id()
            handle = self.model.append()
            self.model.set_value(handle,0,1)
            self.model.set_value(handle,1,gid)
            self.model.set_value(handle,2,_('Title'))
            self.model.set_value(handle,3,title)
            self.model.set_value(handle,4,p.get_primary_name().get_name())
            self.title_hash[id] = handle
            self.progress.step()

        for (id,fname,prefix) in self.prefix1_list:
            p = self.db.get_person_from_handle(id)
            gid = p.get_gramps_id()
            handle = self.model.append()
            self.model.set_value(handle,0,1)
            self.model.set_value(handle,1,gid)
            self.model.set_value(handle,2,_('Prefix'))
            self.model.set_value(handle,3,prefix)
            self.model.set_value(handle,4,p.get_primary_name().get_name())
            self.prefix1_hash[id] = handle
            self.progress.step()

        for (id,sname,prefix) in self.prefix2_list:
            p = self.db.get_person_from_handle(id)
            gid = p.get_gramps_id()
            handle = self.model.append()
            self.model.set_value(handle,0,1)
            self.model.set_value(handle,1,gid)
            self.model.set_value(handle,2,_('Prefix'))
            self.model.set_value(handle,3,prefix)
            self.model.set_value(handle,4,p.get_primary_name().get_name())
            self.prefix2_hash[id] = handle
            self.progress.step()

        self.progress.close()
        self.show()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('tools-db')

    def on_ok_clicked(self,obj):
        self.trans = self.db.transaction_begin("",batch=True)
        self.db.disable_signals()
        for grp in self.nick_list:
            handle = self.nick_hash[grp[0]]
            val = self.model.get_value(handle,0)
            if val:
                p = self.db.get_person_from_handle(grp[0])
                name = p.get_primary_name()
                name.set_first_name(grp[1].strip())
                nick_name = grp[2].strip()
                attr = RelLib.Attribute()
                attr.set_type(RelLib.AttributeType.NICKNAME)
                attr.set_value(nick_name)
                p.add_attribute(attr)
                self.db.commit_person(p,self.trans)

        for grp in self.title_list:
            handle = self.title_hash[grp[0]]
            val = self.model.get_value(handle,0)
            if val:
                p = self.db.get_person_from_handle(grp[0])
                name = p.get_primary_name()
                name.set_first_name(grp[2].strip())
                name.set_title(grp[1].strip())
                self.db.commit_person(p,self.trans)

        for grp in self.prefix1_list:
            handle = self.prefix1_hash[grp[0]]
            val = self.model.get_value(handle,0)
            if val:
                p = self.db.get_person_from_handle(grp[0])
                name = p.get_primary_name()
                name.set_first_name(grp[1].strip())
                name.set_surname_prefix(grp[2].strip())
                self.db.commit_person(p,self.trans)

        for grp in self.prefix2_list:
            handle = self.prefix2_hash[grp[0]]
            val = self.model.get_value(handle,0)
            if val:
                p = self.db.get_person_from_handle(grp[0])
                name = p.get_primary_name()
                name.set_surname(grp[1].strip())
                name.set_surname_prefix(grp[2].strip())
                self.db.commit_person(p,self.trans)

        self.db.transaction_commit(self.trans,
                                   _("Extract information from names"))
        self.db.enable_signals()
        self.db.request_rebuild()
        self.close()
        self.cb()
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class PatchNamesOptions(Tool.ToolOptions):
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
register_tool(
    name = 'patchnames',
    category = Tool.TOOL_DBPROC,
    tool_class = PatchNames,
    options_class = PatchNamesOptions,
    modes = Tool.MODE_GUI,
    translated_name = _("Extract information from names"),
    status=(_("Stable")),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description=_("Searches the entire database and attempts to "
                  "extract titles, nicknames and surname prefixes "
                  "that may be embedded in a person's given name field.")
    )
