#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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

import pickle
import os
from xml.sax.saxutils import escape

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.gdk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------

import const
import Utils
import ListModel
import TreeTips

from gettext import gettext as _

from gtk.gdk import ACTION_COPY, BUTTON1_MASK

#-------------------------------------------------------------------------
#
# Globals
#
#-------------------------------------------------------------------------

text_targets =  ['text/plain',
                 'TEXT',
                 'STRING',
                 'COMPOUND_TEXT',
                 'UTF8_STRING']

text_tgts = [('text/plain',0,0),
             ('TEXT', 0, 1),
             ('STRING', 0, 2),
             ('COMPOUND_TEXT', 0, 3),
             ('UTF8_STRING', 0, 4)]

gramps_targets = ['url',
                  'pevent',
                  'pattr',
                  'paddr',
                  'srcref']

pycode_tgts = [('url', 0, 0),
               ('pevent', 0, 1),
               ('pattr', 0, 2),
               ('paddr', 0, 3),
               ('srcref', 0, 4)] + text_tgts
               

TEXT_TARGET = 'TEXT'

target_map = {'url':[('url', 0, 0)],
              'pevent': [('pevent', 0, 1)],
              'pattr': [('pattr', 0, 2)],
              'paddr': [('paddr', 0, 3)],
              'srcref': [('srcref', 0, 4)],
              TEXT_TARGET: text_tgts}



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
    
    def __init__(self,database,parent):
        """Initializes the ScratchPad class, and displays the window"""

        self.db = database
        self.parent = parent
        self.win_key = self

        self.olist = []
        self.otitles = [(_('Type'),-1,150),
                        (_('Title'),-1,150),
                        (_('Value'),-1,150),
                        ('',-1,0)] # To hold the tooltip text

        base = os.path.dirname(__file__)
        self.glade_file = "%s/%s" % (base,"scratchpad.glade")

        self.top = gtk.glade.XML(self.glade_file,"scratchPad","gramps")
        self.window = self.top.get_widget("scratchPad")
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
            "on_objectlist_delete_event": self.on_delete_event,
            "on_scratchPad_delete_event": self.on_delete_event
            })

        self.object_list.drag_dest_set(gtk.DEST_DEFAULT_ALL, pycode_tgts,
                                           ACTION_COPY)

        self.object_list.connect('drag_data_get', self.object_drag_data_get)
        self.object_list.connect('drag_begin', self.object_drag_begin)
        self.object_list.connect('drag_data_received',
                                 self.object_drag_data_received)

        self.add_itself_to_menu()
        self.window.show()


    def on_delete_event(self,obj,b):
        self.remove_itself_from_menu()
        
    def add_itself_to_menu(self):
        """Add the ScratchPad window to the list of windows in the
        main GRAMPS interface. If this is the first instance to be
        created a submenu is created, if it is not the first instance
        then an entry is created in the existing sub menu."""
        
        sub_menu_label = _("Scratch Pad Tool")
        instance_number_key = "scratch_pad_instance_number"
        
        self.parent.child_windows[self.win_key] = self

        # First check to see if the Scratch Pad sub menu already exists.
        # The MenuItems contain a list of child widgets, the first one
        # should be the AccelLabel so we can check the label text on
        # that one.        
        sub_menu_list  = [ menu for menu in self.parent.winsmenu.get_children() if \
                           menu.get_children()[0].get_label() == sub_menu_label ]

        if len(sub_menu_list) > 0:
            # This list should always be of length 0 or 1 but in the unlikely
            # situation that it is greater than 1 it will still be safe to use
            # the first.
            self.parent_menu_item = sub_menu_list[0]
        else:
            # There is no existing instances so we must create the submenu. 
            self.parent_menu_item = gtk.MenuItem(sub_menu_label)            
            self.parent_menu_item.set_submenu(gtk.Menu())
            self.parent_menu_item.show()
            self.parent.winsmenu.append(self.parent_menu_item)

        # Get a handle to the submenu and remember it so that
        # remove_itself_from_menu can delete it later.
        self.winsmenu = self.parent_menu_item.get_submenu()

        # Get the first available instance number. The instance number
        # is stored in the data item store of the menu item so we can
        # read it with get_data.
        num = 1
        existing_instances = [ menu_item.get_data(instance_number_key) \
                               for menu_item in self.winsmenu.get_children() ]
        
        if len(existing_instances) > 0:
            # Calculate the first available instance number. 
            existing_instances.sort()
            for instance_num in existing_instances:
                if instance_num != num:
                    break
                else:
                    num += 1

        # Create the instance menuitem with the instance number in the
        # label.
        instance_title = _('Scratch Pad - %d') % (num,)
        self.menu_item = gtk.MenuItem(instance_title)
        self.menu_item.set_data(instance_number_key,num)
        self.menu_item.connect("activate",self.present)
        self.menu_item.show()

        # Set the window title to the same as the menu label.
        self.window.set_title(instance_title)

        # Add the item to the submenu.
        self.winsmenu.append(self.menu_item)

    def remove_itself_from_menu(self):
        """Remove the instance of the pad from the Window menu in the
        main GRAMPS window. If this is the last pad then remove the
        ScratchPad sub menu as well."""
        
        del self.parent.child_windows[self.win_key]
        self.menu_item.destroy()
        if len(self.winsmenu.get_children()) == 0:            
            self.winsmenu.destroy()
            self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()


    def on_close_scratchpad(self,obj):
        self.remove_itself_from_menu()
        self.window.destroy()

    def on_clear_clicked(self,obj):
        """Deletes the selected object from the object list"""
        store,node = self.otree.get_selected()
        if node:
            self.olist.remove(self.otree.get_object(node))
            self.redraw_object_list()

    def on_clear_all_clicked(self,obj):
        self.olist = []
        self.redraw_object_list()

    def on_object_select_row(self,obj):
        global target_map
        global TEXT_TARGET
        
        o = self.otree.get_selected_objects()
        
        if len(o):
            bits_per = 8; # we're going to pass a string

            obj_targets = o[0]['targets']

            # union with gramps_types
            if len([target for target \
                    in obj_targets if target in gramps_targets]) > 0:

                exec 'data = %s' % o[0]['data']
                exec 'mytype = "%s"' % data[0]
                target = target_map[mytype]
            
            # Union with text targets
            elif len([target for target \
                      in obj_targets if target in text_targets]) > 0:
                target = target_map[TEXT_TARGET]

            self.object_list.drag_source_unset()
            self.object_list.drag_source_set(BUTTON1_MASK, target, ACTION_COPY)

        
    def on_update_object_clicked(self, obj):
        pass

    def object_drag_begin(self, context, a):
        return

    def object_drag_data_get(self,widget, context, sel_data, info, time):

        global gramps_targets
        global text_targets
        
        o = self.otree.get_selected_objects()
        
        if len(o):
            bits_per = 8; # we're going to pass a string

            obj_targets = o[0]['targets']

            # union with gramps_types
            if len([target for target \
                    in obj_targets if target in gramps_targets]) > 0:

                exec 'data = %s' % o[0]['data']
                exec 'mytype = "%s"' % data[0]
                exec 'person = "%s"' % data[1]

                pickled = data[2]
                send_data = str((mytype,person,pickled));
            
            # Union with text targets
            elif len([target for target \
                      in obj_targets if target in text_targets]) > 0:
                send_data = str(o[0]['data'])

            sel_data.set(sel_data.target, bits_per, send_data)


    def object_drag_data_received(self,widget,context,x,y,sel_data,info,time):
        row = self.otree.get_row_at(x,y)
            
        if sel_data and sel_data.data:
            self.olist.insert(row,{'targets':context.targets,
                                   'data':sel_data.data})
            self.redraw_object_list()
            

    def redraw_object_list(self):
        """Redraws the address list"""

        global gramps_targets
        global text_targets

        self.otree.clear()
        
        for obj in self.olist:
            obj_targets = obj['targets']

            # union with gramps_types
            if len([target for target \
                    in obj_targets if target in gramps_targets]) > 0:
                
                exec 'unpack_data = %s' % obj['data']
                exec 'mytype = "%s"' % unpack_data[0]
                data = pickle.loads(unpack_data[2]);

                node = None

                if mytype == 'paddr':                
                    location = "%s %s %s %s" % (data.get_street(),data.get_city(),
                                                data.get_state(),data.get_country())
                    node = self.otree.add([_("Address"),
                                           data.get_date(),
                                           location,
                                           self.generate_addr_tooltip(data)],obj)

                elif mytype == 'pevent':
                    node = self.otree.add([_("Event"),
                                           const.display_pevent(data.get_name()),
                                           data.get_description(),
                                           self.generate_event_tooltip(data)],obj)

                elif mytype == 'url':
                    node = self.otree.add([_("Url"),
                                           data.get_path(),
                                           data.get_description(),
                                           self.generate_url_tooltip(data)],obj)
                elif mytype == 'pattr':
                    node = self.otree.add([_("Attribute"),
                                           const.display_pattr(data.get_type()),
                                           data.get_value(),
                                           self.generate_pattr_tooltip(data)],obj)
                elif mytype == 'srcref':
                    base = self.db.get_source_from_handle(data.get_base_handle())
                    node = self.otree.add([_("SourceRef"),
                                           base.get_title(),
                                           data.get_text(),
                                           self.generate_srcref_tooltip(data)],obj)

            # Union with text targets
            elif len([target for target \
                      in obj_targets if target in text_targets]) > 0:
                node = self.otree.add([_("Text"),
                                       "",
                                       obj['data'],
                                       self.generate_text_tooltip(obj['data'])],obj)
                

                

                
        if self.olist:
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


