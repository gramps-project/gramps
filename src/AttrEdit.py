#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

"""
The AttrEdit module provides the AddressEditor class. This provides a
mechanism for the user to edit address information.
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk.glade
import gnome

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import Sources
import AutoComp
import RelLib
from QuestionDialog import WarningDialog

from gettext import gettext as _

#-------------------------------------------------------------------------
#
# AttributeEditor class
#
#-------------------------------------------------------------------------
class AttributeEditor:
    """
    Displays a dialog that allows the user to edit an attribute.
    """
    def __init__(self,parent,attrib,title,list,callback,parent_window=None):
        """
        Displays the dialog box.

        parent - The class that called the Address editor.
        attrib - The attribute that is to be edited
        title - The title of the dialog box
        list - list of options for the pop down menu
        """

        self.parent = parent
        self.db = self.parent.db
        self.attrib = attrib
        self.top = gtk.glade.XML(const.dialogFile, "attr_edit","gramps")
        self.type_field  = self.top.get_widget("attr_type")
        self.slist  = self.top.get_widget("slist")
        self.value_field = self.top.get_widget("attr_value")
        self.note_field = self.top.get_widget("attr_note")
        self.attrib_menu = self.top.get_widget("attr_menu")
        self.source_field = self.top.get_widget("attr_source")
        self.priv = self.top.get_widget("priv")
        self.sources_label = self.top.get_widget("sourcesAttr")
        self.notes_label = self.top.get_widget("noteAttr")
        self.flowed = self.top.get_widget("attr_flowed")
        self.preform = self.top.get_widget("attr_preform")
        self.callback = callback
        self.alist = list

        self.window = self.top.get_widget("attr_edit")
        
        if attrib:
            self.srcreflist = self.attrib.get_source_references()
        else:
            self.srcreflist = []

        self.sourcetab = Sources.SourceTab(self.srcreflist,self,self.top,
                                           self.window, self.slist,
                                           self.top.get_widget('add_src'),
                                           self.top.get_widget('edit_src'),
                                           self.top.get_widget('del_src'))

        if title == ", ":
            title = _("Attribute Editor")
        else:
            title = _("Attribute Editor for %s") % title
        l = self.top.get_widget("title")
        Utils.set_titles(self.window,l,title,_('Attribute Editor'))

        AutoComp.AutoCombo(self.attrib_menu,list)

        if attrib != None:
            self.type_field.set_text(attrib.get_type())
            self.value_field.set_text(attrib.get_value())
            self.priv.set_active(attrib.get_privacy())

            if attrib.get_note():
                self.note_field.get_buffer().set_text(attrib.get_note())
                Utils.bold_label(self.notes_label)
            	if attrib.get_note_format() == 1:
                    self.preform.set_active(1)
            	else:
                    self.flowed.set_active(1)

        self.top.signal_autoconnect({
            "on_add_src_clicked" : self.add_source,
            "on_del_src_clicked" : self.del_source,
            "on_help_attr_clicked" : self.on_help_clicked,
            "on_switch_page" : self.on_switch_page
            })

        if parent_window:
            self.window.set_transient_for(parent_window)
        self.val = self.window.run()
        if self.val == gtk.RESPONSE_OK:
            self.on_ok_clicked()
        self.window.destroy()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-complete')
        self.val = self.window.run()

    def add_source(self,obj):
        pass

    def del_source(self,obj):
        pass

    def on_ok_clicked(self):
        """
        Called when the OK button is pressed. Gets data from the
        form and updates the Attribute data structure.
        """
        type = unicode(self.type_field.get_text())
        value = unicode(self.value_field.get_text())

        buf = self.note_field.get_buffer()
        note = unicode(buf.get_text(buf.get_start_iter(),buf.get_end_iter(),gtk.FALSE))
        format = self.preform.get_active()
        priv = self.priv.get_active()

        if not type in self.alist:
            WarningDialog(_('New attribute type created'),
                          _('The "%s" attribute type has been added to this database.\n'
                            'It will now appear in the attribute menus for this database') % type)
            self.alist.append(type)
            self.alist.sort()

        if self.attrib == None:
            self.attrib = RelLib.Attribute()
            self.parent.alist.append(self.attrib)

        self.attrib.set_source_reference_list(self.srcreflist)
        self.update(type,value,note,format,priv)
        self.callback(self.attrib)

    def check(self,get,set,data):
        """Compares a data item, updates if necessary, and sets the
        parents lists_changed flag"""
        if get() != data:
            set(data)
            self.parent.lists_changed = 1
            
    def update(self,type,value,note,format,priv):
        """Compares the data items, and updates if necessary"""
        ntype = const.save_pattr(type)
        self.check(self.attrib.get_type,self.attrib.set_type,ntype)
        self.check(self.attrib.get_value,self.attrib.set_value,value)
        self.check(self.attrib.get_note,self.attrib.set_note,note)
        self.check(self.attrib.get_note_format,self.attrib.set_note_format,format)
        self.check(self.attrib.get_privacy,self.attrib.set_privacy,priv)

    def on_switch_page(self,obj,a,page):
        buf = self.note_field.get_buffer()
        text = unicode(buf.get_text(buf.get_start_iter(),buf.get_end_iter(),gtk.FALSE))
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)
