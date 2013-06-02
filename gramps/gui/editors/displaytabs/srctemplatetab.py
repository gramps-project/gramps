#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013       Benny Malengier
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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps libraries
#
#-------------------------------------------------------------------------
from gramps.gen.lib.srcattrtype import (SrcAttributeType, REF_TYPE_F, 
                                REF_TYPE_S, REF_TYPE_L)
from gramps.gen.lib.srcattribute import SrcAttribute
from ...autocomp import StandardCustomSelector
from ...widgets.srctemplatetreeview import SrcTemplateTreeView
from ...widgets import UndoableEntry, MonitoredEntry
from .grampstab import GrampsTab

#-------------------------------------------------------------------------
#
# Classes
#
#-------------------------------------------------------------------------
class SrcTemplateTab(GrampsTab):
    """
    This class provides the tabpage for template generation of attributes.
    """
    def __init__(self, dbstate, uistate, track, src, glade,
                 callback_src_changed):
        """
        @param dbstate: The database state. Contains a reference to
        the database, along with other state information. The GrampsTab
        uses this to access the database and to pass to and created
        child windows (such as edit dialogs).
        @type dbstate: DbState
        @param uistate: The UI state. Used primarily to pass to any created
        subwindows.
        @type uistate: DisplayState
        @param track: The window tracking mechanism used to manage windows.
        This is only used to pass to generted child windows.
        @type track: list
        @param src: source which we manage in this tab
        @type src: gen.lib.Source
        @param glade: glade objects with the needed widgets
        """
        self.src = src
        self.glade = glade
        self.callback_src_changed = callback_src_changed
        self.readonly = dbstate.db.readonly
        
        GrampsTab.__init__(self, dbstate, uistate, track, _("Source Template"))
        eventbox = Gtk.EventBox()
        widget = self.glade.get_object('gridtemplate')
        eventbox.add(widget)
        self.pack_start(eventbox, True, True, 0)
        self._set_label(show_image=False)
        widget.connect('key_press_event', self.key_pressed)
        
        self.lbls = []
        self.inpts = []
        self.gridfields = self.glade.get_object('gridfields')
        #self.vbox_fields_label = self.glade.get_object('fields_01')
        #self.vbox_fields_input = self.glade.get_object('fields_02')
        self.setup_interface(self.glade.get_object('scrolledtemplates'))
        self.show_all()

    def is_empty(self):
        """
        Override base class
        """
        return False

    def setup_interface(self, scrolled):
        """
        Set all information on the widgets
        * template selection
        * setting attribute fields
        
        :param scrolled: GtkScrolledWindow to which to add treeview with templates
        """
        srcattr = SrcAttributeType()
        templ = self.src.get_source_template()
        self.temp_tv = SrcTemplateTreeView(templ[2],
                                sel_callback=self.on_template_selected)
        scrolled.add(self.temp_tv)

    def on_template_selected(self, index, key):
        """
        Selected template changed, we save this and update interface
        """
        self.src.set_source_template(index, key)
        self.callback_src_changed()
        
        srcattr = SrcAttributeType()
        if index in srcattr.EVIDENCETEMPLATES:
            #a predefined template, 
            self.reset_template_fields(srcattr.EVIDENCETEMPLATES[index])

    def reset_template_fields(self, template):
        # first remove old fields
        for lbl in self.lbls:
            self.gridfields.remove(lbl)
        for inpt in self.inpts:
            self.gridfields.remove(inpt)
        self.lbls = []
        self.inpts = []
        row = 1
        # now add new fields
        for fielddef in template[REF_TYPE_F]:
            self.gridfields.insert_row(row)
            row += 1
            field = fielddef[1]
            #setup label
            srcattr = SrcAttributeType(field)
            lbl = Gtk.Label(_("%s:") %str(srcattr))
            lbl.set_halign(Gtk.Align.START)
            self.gridfields.attach(lbl, 0, row-1, 1, 1)
            self.lbls.append(lbl)
            #setup entry
            inpt = UndoableEntry()
            inpt.set_halign(Gtk.Align.FILL)
            inpt.set_hexpand(True)
            self.gridfields.attach(inpt, 1, row-1, 1, 1)
            self.inpts.append(inpt)
            MonitoredEntry(inpt, self.set_field, self.get_field, 
                           read_only=self.dbstate.db.readonly, 
                           parameter=field)
        
        self.show_all()

    def get_field(self, srcattrtype):
        """
        Obtain srcattribute with type srcattrtype, where srcattrtype is an
        integer key!
        """
        src = self.src
        val = ''
        for attr in src.attribute_list:
            if int(attr.get_type()) == srcattrtype:
                val = attr.get_value()
                break
        return val

    def set_field(self, value, srcattrtype):
        """
        Set attribute of source of type srcattrtype (which is integer!) to 
        value. If not present, create attribute. If value == '', remove
        """
        src = self.src
        value = value.strip()
        foundattr = None
        for attr in src.attribute_list:
            if int(attr.get_type()) == srcattrtype:
                attr.set_value(value)
                foundattr = attr
                break
        if foundattr and value == '':
            src.remove_attribute(foundattr)
        if foundattr is None and value != '':
            foundattr = SrcAttribute()
            foundattr.set_type(srcattrtype)
            foundattr.set_value(value)
            src.add_attribute(foundattr)
        #indicate source object changed
        self.callback_src_changed()
        

##    def setup_autocomp_combobox(self):
##        """
##        Experimental code to set up a combobox with all templates.
##        This is too slow, we use treeview in second attempt
##        """
##        self.srctempcmb = Gtk.ComboBox(has_entry=True)
##        ignore_values = []
##        custom_values = []
##        srcattr = SrcAttributeType()
##        default = srcattr.get_templatevalue_default()
##        maptempval = srcattr.get_templatevalue_map().copy()
##        if ignore_values :
##            for key in list(maptempval.keys()):
##                if key in ignore_values and key not in (None, default):
##                    del map[key]
##
##        self.sel = StandardCustomSelector(
##            maptempval, 
##            self.srctempcmb, 
##            srcattr.get_custom(), 
##            default, 
##            additional=custom_values)
##
##        templ = self.src.get_source_template()
##        self.sel.set_values((templ[0], templ[1]))
##        self.srctempcmb.set_sensitive(not self.readonly)
##        self.srctempcmb.connect('changed', self.on_change_template)
##        srctemphbox.pack_start(self.srctempcmb, False, True, 0)
##        
##        return topvbox

##    def fix_value(self, value):
##        if value[0] == SrcAttributeType.CUSTOM:
##            return value
##        else:
##            return (value[0], '')
##
##    def on_change_template(self, obj):
##        #value = self.fix_value(self.srctempcmb.get_values())
##        value = self.sel.get_values()
##        self.src.set_source_template(value[0], value[1])
