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

"Utilities/Generate SoundEx codes"

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import os
from TransUtils import sgettext as _

#------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#------------------------------------------------------------------------
import gtk
import gtk.glade
import GrampsDisplay

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import soundex
import Utils
import AutoComp
from PluginUtils import Tool, register_tool

#-------------------------------------------------------------------------
#
#
#-------------------------------------------------------------------------
class SoundGen(Tool.Tool):
    def __init__(self,db,person,options_class,name,callback=None,parent=None):
        Tool.Tool.__init__(self,db,person,options_class,name)

        self.parent = parent
        if self.parent.child_windows.has_key(self.__class__):
            self.parent.child_windows[self.__class__].present(None)
            return
        self.win_key = self.__class__
        
        base = os.path.dirname(__file__)
        glade_file = base + os.sep + "soundex.glade"

        self.glade = gtk.glade.XML(glade_file,"soundEx","gramps")
        self.glade.signal_autoconnect({
            "destroy_passed_object" : self.close,
            "on_help_clicked"       : self.on_help_clicked,
            "on_delete_event"       : self.on_delete_event,
        })

        self.window = self.glade.get_widget("soundEx")
        self.window.set_icon(self.parent.topWindow.get_icon())
        Utils.set_titles(self.window,
                         self.glade.get_widget('title'),
                         _('SoundEx code generator'))

        self.value = self.glade.get_widget("value")
        self.autocomp = self.glade.get_widget("name_list")
        self.name = self.autocomp.child

        self.name.connect('changed',self.on_apply_clicked)

        names = []
        for person_handle in self.db.get_person_handles(sort_handles=False):
            person = self.db.get_person_from_handle(person_handle)
            lastname = person.get_primary_name().get_surname()
            if lastname not in names:
                names.append(lastname)

        names.sort()

        AutoComp.fill_combo(self.autocomp, names)

        if person:
            n = person.get_primary_name().get_surname()
            self.name.set_text(n)
            try:
                se_text = soundex.soundex(n)
            except UnicodeEncodeError:
                se_text = soundex.soundex('')
            self.value.set_text(se_text)
        else:
            self.name.set_text("")
            
        self.add_itself_to_menu()
        self.window.show()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('tools-util-other')

    def on_delete_event(self,obj,b):
        self.remove_itself_from_menu()

    def close(self,obj):
        self.remove_itself_from_menu()
        self.window.destroy()

    def add_itself_to_menu(self):
        self.parent.child_windows[self.win_key] = self
        self.parent_menu_item = gtk.MenuItem(_('SoundEx code generator tool'))
        self.parent_menu_item.connect("activate",self.present)
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self.win_key]
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def on_apply_clicked(self,obj):
        try:
            se_text = soundex.soundex(unicode(obj.get_text()))
        except UnicodeEncodeError:
            se_text = soundex.soundex('')
        self.value.set_text(se_text)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class SoundGenOptions(Tool.ToolOptions):
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
    name = 'soundgen',
    category = Tool.TOOL_UTILS,
    tool_class = SoundGen,
    options_class = SoundGenOptions,
    modes = Tool.MODE_GUI,
    translated_name = _("Generate SoundEx codes"),
    status=(_("Stable")),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description=_("Generates SoundEx codes for names")
    )
