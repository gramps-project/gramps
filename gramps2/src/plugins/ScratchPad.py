#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
#
# This program is free software; you can redistribute it and/or modiy
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

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import pickle
import os
from xml.sax.saxutils import escape
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
from gtk.gdk import ACTION_COPY, BUTTON1_MASK
from gnome import help_display

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import ListModel
import TreeTips

from DdTargets import DdTargets


#-------------------------------------------------------------------------
#
# ScatchPadWindow class
#
#-------------------------------------------------------------------------
class ScratchPadWindow:
    """
        The ScratchPad provides a temporary area to hold objects that can
        be reused accross multiple Person records. The pad provides a window
        onto which objects can be dropped and then dragged into new Person
        dialogs. The objects are stored as the pickles that are built by the
        origininating widget. The objects are only unpickled in order to
        provide the text in the display.

        No attempt is made to ensure that any references contained within
        the pickles are valid. Because the pad extends the life time of drag
        and drop objects, it is possible that references that were valid
        when an object is copied to the pad are invalid by the time they
        are dragged to a new Person. For this reason, using the pad places
        a responsibility on all '_drag_data_received' methods to check the
        references of objects before attempting to use them.
        """
    
    # Class attribute used to hold the content of the
    # ScratchPad. A class attribute is used so that the content
    # it preserved even when the ScratchPad window is closed.
    # As there is only ever one ScratchPad we do not need to
    # maintain a list of these.
    olist = [] 
    
    def __init__(self,database,parent):
        """Initializes the ScratchPad class, and displays the window"""

        self.db = database
        self.parent = parent
        if self.parent.child_windows.has_key(self.__class__):
            self.parent.child_windows[self.__class__].present(None)
            return
        self.win_key = self.__class__

        self.otitles = [(_('Type'),-1,150),
                        (_('Title'),-1,150),
                        (_('Value'),-1,150),
                        ('',-1,0)] # To hold the tooltip text

        base = os.path.dirname(__file__)
        self.glade_file = "%s/%s" % (base,"scratchpad.glade")

        self.top = gtk.glade.XML(self.glade_file,"scratch_pad","gramps")
        self.window = self.top.get_widget("scratch_pad")
        self.window.set_icon(self.parent.topWindow.get_icon())
        
        self.object_list = self.top.get_widget('objectlist')

        self.otree = ListModel.ListModel(self.object_list,self.otitles,
                                         self.on_object_select_row,
                                         self.on_update_object_clicked)

        self.treetips = TreeTips.TreeTips(self.object_list,3,True)

        self.top.signal_autoconnect({
            "on_close_scratchpad" : self.on_close_scratchpad,
            "on_clear_clicked": self.on_clear_clicked,
            "on_clear_all_clicked": self.on_clear_all_clicked,
            "on_help_clicked": self.on_help_clicked,
            "on_objectlist_delete_event": self.on_delete_event,
            "on_scratchPad_delete_event": self.on_delete_event
            })

        self.object_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,
                                       DdTargets.all_targets(),
                                       ACTION_COPY)

        self.object_list.connect('drag_data_get', self.object_drag_data_get)
        self.object_list.connect('drag_begin', self.object_drag_begin)
        self.object_list.connect('drag_data_received',
                                 self.object_drag_data_received)

        self.add_itself_to_menu()
        self.window.show()

        self.redraw_object_list()

    def on_delete_event(self,obj,b):
        self.remove_itself_from_menu()
        
    def add_itself_to_menu(self):
        """Add the ScratchPad window to the list of windows in the
        main GRAMPS interface. If this is the first instance to be
        created a submenu is created, if it is not the first instance
        then an entry is created in the existing sub menu."""
        self.parent.child_windows[self.win_key] = self
        self.parent_menu_item = gtk.MenuItem(_('Scratch Pad'))
        self.parent_menu_item.connect("activate",self.present)
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)

    def remove_itself_from_menu(self):
        """Remove the instance of the pad from the Window menu in the
        main GRAMPS window. If this is the last pad then remove the
        ScratchPad sub menu as well."""
        
        del self.parent.child_windows[self.win_key]
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        help_display('gramps-manual','tools-util')

    def on_close_scratchpad(self,obj):
        self.remove_itself_from_menu()
        self.window.destroy()

    def on_clear_clicked(self,obj):
        """Deletes the selected object from the object list"""
        store,node = self.otree.get_selected()
        if node:
            ScratchPadWindow.olist.remove(self.otree.get_object(node))
            self.redraw_object_list()

    def on_clear_all_clicked(self,obj):
        ScratchPadWindow.olist = []
        self.redraw_object_list()

    def on_object_select_row(self,obj):
        
        o = self.otree.get_selected_objects()
        
        if len(o):
            bits_per = 8; # we're going to pass a string

            obj_targets = o[0]['targets']

            # union with gramps_types
            if len([target for target \
                    in obj_targets if DdTargets.is_gramps_type(target)]) > 0:

                exec 'data = %s' % o[0]['data']
                exec 'mytype = "%s"' % data[0]
                target = DdTargets.get_dd_type_from_type_name(mytype).target()
            
            # Union with text targets
            elif len([target for target \
                      in obj_targets if DdTargets.is_text_type(target)]) > 0:
                target = DdTargets.TEXT.target()

            self.object_list.drag_source_unset()
            self.object_list.drag_source_set(BUTTON1_MASK, [target], ACTION_COPY)

        
    def on_update_object_clicked(self, obj):
        pass

    def object_drag_begin(self, context, a):
        return

    def object_drag_data_get(self,widget, context, sel_data, info, time):
        
        o = self.otree.get_selected_objects()
        
        if len(o):
            bits_per = 8; # we're going to pass a string

            obj_targets = o[0]['targets']

            # union with gramps_types
            if len([target for target \
                    in obj_targets if DdTargets.is_gramps_type(target)]) > 0:

                exec 'data = %s' % o[0]['data']
                exec 'mytype = "%s"' % data[0]
                exec 'person = "%s"' % data[1]

                pickled = data[2]
                send_data = str((mytype,person,pickled));
            
            # Union with text targets
            elif len([target for target \
                      in obj_targets if DdTargets.is_text_type(target)]) > 0:
                send_data = str(o[0]['data'])

            sel_data.set(sel_data.target, bits_per, send_data)


    def object_drag_data_received(self,widget,context,x,y,sel_data,info,time):
        row = self.otree.get_row_at(x,y)
            
        if sel_data and sel_data.data:
            ScratchPadWindow.olist.insert(row,{'targets':context.targets,
                                               'data':sel_data.data})
            self.redraw_object_list()
            

    def redraw_object_list(self):
        """Redraws the address list"""

        self.otree.clear()
        
        for obj in ScratchPadWindow.olist:
            obj_targets = obj['targets']

            # union with gramps_types
            if len([target for target \
                    in obj_targets if DdTargets.is_gramps_type(target)]) > 0:
                
                exec 'unpack_data = %s' % obj['data']
                exec 'mytype = "%s"' % unpack_data[0]
                data = pickle.loads(unpack_data[2]);

                node = None

                if mytype == DdTargets.ADDRESS.drag_type:                
                    location = "%s %s %s %s" % (data.get_street(),data.get_city(),
                                                data.get_state(),data.get_country())
                    node = self.otree.add([_("Address"),
                                           data.get_date(),
                                           location,
                                           self.generate_addr_tooltip(data)],obj)

                elif mytype == DdTargets.EVENT.drag_type:
                    node = self.otree.add([_("Event"),
                                           const.display_pevent(data.get_name()),
                                           data.get_description(),
                                           self.generate_event_tooltip(data)],obj)

                elif mytype == DdTargets.URL.drag_type:
                    node = self.otree.add([_("Url"),
                                           data.get_path(),
                                           data.get_description(),
                                           self.generate_url_tooltip(data)],obj)
                elif mytype == DdTargets.ATTRIBUTE.drag_type:
                    node = self.otree.add([_("Attribute"),
                                           const.display_pattr(data.get_type()),
                                           data.get_value(),
                                           self.generate_pattr_tooltip(data)],obj)
                elif mytype == DdTargets.SOURCEREF.drag_type:
                    base = self.db.get_source_from_handle(data.get_base_handle())
                    node = self.otree.add([_("SourceRef"),
                                           base.get_title(),
                                           data.get_text(),
                                           self.generate_srcref_tooltip(data)],obj)

            # Union with text targets
            elif len([target for target \
                      in obj_targets if DdTargets.is_text_type(target)]) > 0:
                node = self.otree.add([_("Text"),
                                       "",
                                       obj['data'],
                                       self.generate_text_tooltip(obj['data'])],obj)
                

                

                
        if ScratchPadWindow.olist:
            self.otree.select_row(0)
            


    def generate_event_tooltip(self,event):
        global escape
        
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n" % (
            _("Event"),
            _("Type"),escape(const.display_pevent(event.get_name())),
            _("Date"),escape(event.get_date()),
            _("Place"),escape(place_title(self.db,event)),
            _("Cause"),escape(event.get_cause()),
            _("Description"), escape(event.get_description()))

        if len(event.get_source_references()) > 0:
            psrc_ref = event.get_source_references()[0]
            psrc_id = psrc_ref.get_base_handle()
            psrc = self.db.get_source_from_handle(psrc_id)

            s += "\n<big><b>%s</b></big>\n\n"\
                 "\t<b>%s:</b>\t%s\n" % (
                _("Primary source"),
                _("Name"),
                escape(short(psrc.get_title())))

        return s

    def generate_addr_tooltip(self,addr):
        global escape
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\n"\
            "\t\t%s\n"\
            "\t\t%s\n"\
            "\t\t%s\n"\
            "\t\t%s\n"\
            "\t\t%s\n"\
            "\t<b>%s:</b>\t%s\n" % (
            _("Address"),
            _("Date"), escape(addr.get_date()),
            _("Location"),
            escape(addr.get_street()),
            escape(addr.get_city()),
            escape(addr.get_state()),
            escape(addr.get_country()),
            escape(addr.get_postal_code()),
            _("Telephone"), escape(addr.get_phone()))
    
        if len(addr.get_source_references()) > 0:
            psrc_ref = addr.get_source_references()[0]
            psrc_id = psrc_ref.get_base_handle()
            psrc = self.db.get_source_from_handle(psrc_id)
            s += "\n<big><b>%s</b></big>\n\n"\
                 "\t<b>%s:</b>\t%s\n" % (
                _("Sources"),
                _("Name"),escape(short(psrc.get_title())))
            
        return s

    
    def generate_url_tooltip(self,url):
        global escape
        return "<big><b>%s</b></big>\n\n"\
               "\t<b>%s:</b>\t%s\n"\
               "\t<b>%s:</b>\t%s" % (_("Url"),
                                     _("Path"),
                                     escape(url.get_path()),
                                     _("Description"),
                                     escape(url.get_description()))

    def generate_pattr_tooltip(self,attr):
        global escape
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s" % (_("Attribute"),
                                  _("Type"),
                                  escape(const.display_pattr(attr.get_type())),
                                  _("Value"),
                                  escape(attr.get_value()))
        
        if len(attr.get_source_references()) > 0:
            psrc_ref = attr.get_source_references()[0]
            psrc_id = psrc_ref.get_base_handle()
            psrc = self.db.get_source_from_handle(psrc_id)
            s += "\n<big><b>%s</b></big>\n\n"\
                 "\t<b>%s:</b>\t%s\n" % (
                _("Sources"),
                _("Name"),escape(short(psrc.get_title())))

        return s

        
    def generate_srcref_tooltip(self,srcref):
        global escape
        base = self.db.get_source_from_handle(srcref.get_base_handle())
        s = "<big><b>%s</b></big>\n\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s\n"\
            "\t<b>%s:</b>\t%s" % (
            _("SourceRef"),
            _("Title"),escape(base.get_title()),
            _("Page"), escape(srcref.get_page()),
            _("Text"), escape(srcref.get_text()),
            _("Comment"), escape(srcref.get_comments()))

        return s

    def generate_text_tooltip(self,text):
        global escape
        return "<big><b>%s</b></big>\n"\
               "%s" % (_("Text"),
                       escape(text))

def short(val,size=60):
    if len(val) > size:
        return "%s..." % val[0:size]
    else:
        return val

def place_title(db,event):
    pid = event.get_place_handle()
    if pid:
        return db.get_place_from_handle(pid).get_title()
    else:
        return u''

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def ScratchPad(database,person,callback,parent=None):
    ScratchPadWindow(database,parent)
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
from PluginMgr import register_tool


register_tool(
    ScratchPad,
    _("Scratch Pad"),
    category=_("Utilities"),
    description=_("The Scratch Pad provides a tempory note pad to store "
                  "objects for easy reuse.")
    )


