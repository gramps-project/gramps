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

# $Id: _MyGrampsView.py $

"""
MyGrampsView interface
"""

__author__ = "Doug Blank"
__revision__ = "$Revision: $"

import gtk
import PageView
import const
import gobject
import traceback
import time

AVAILABLE_GADGETS = []

debug = False

def register_gadget(data_dict):
    global AVAILABLE_GADGETS
    AVAILABLE_GADGETS.append(data_dict)

def register(**data):
    if "type" in data:
        if data["type"].lower() == "gadget":
            register_gadget(data)

def get_gadget_opts(name, opts):
    for data in AVAILABLE_GADGETS:
        if data.get("name", None) == name:
            my_data = data.copy()
            my_data.update(opts)
            return my_data
    return {}

def make_requested_gadget(viewpage, name, opts, dbstate):
    for data in AVAILABLE_GADGETS:
        if data.get("name", None) == name:
            gui = GuiGadget(viewpage, dbstate, **opts)
            if opts.get("content", None):
                opts["content"](gui)
            return gui
    return None

class Gadget(object):
    def __init__(self, gui):
        self._idle_id = 0
        self._generator = None
        self._need_to_update = False
        self.gui = gui
        self.dbstate = gui.dbstate
        self.init()
        self.dbstate.connect('database-changed', self._db_changed)
        self.dbstate.connect('active-changed', self.active_changed)

    def active_changed(self, handle):
        pass

    def _db_changed(self, dbstate):
        if debug: print "%s is _connecting" % self.gui.title
        self.dbstate = dbstate
        self.gui.dbstate = dbstate
        self.db_changed()
        self.update()

    def db_changed(self):
        if debug: print "%s is connecting" % self.gui.title
        pass

    def init(self): # once, constructor
        pass

    def main(self): # once per db open
        pass 

    def update(self, *handles):
        self.main()
        if self._idle_id != 0:
            if debug: print "%s interrupt!" % self.gui.title
            self.interrupt()
        if debug: print "%s creating generator" % self.gui.title
        self._generator = self.background()
        if debug: print "%s adding to gobject" % self.gui.title
        self._idle_id = gobject.idle_add(self._updater, 
                                         priority=gobject.PRIORITY_LOW)

    def background(self): # return false finishes
        if debug: print "%s dummy" % self.gui.title
        yield False

    def interrupt(self):
        """
        Force the generator to stop running.
        """
        if self._idle_id == 0:
            if debug: print "%s removing from gobject" % self.gui.title
            gobject.source_remove(self._idle_id)
            self._idle_id = 0

    def _updater(self):
        if debug: print "%s _updater" % self.gui.title
        try:
            retval = self._generator.next()
            if retval == False:
                self._idle_id = 0
            return retval
        except StopIteration:
            self._idle_id = 0
            return False
        except Exception, e:
            #self._error = e
            traceback.print_exc()
            self._idle_id = 0
            return False
        except:
            self._idle_id = 0
            return False

    def append_text(self, text):
        end = self.gui.buffer.get_end_iter()
        mark = self.gui.buffer.create_mark(None, end, True)
        self.gui.buffer.insert(end, text)
        self.gui.textview.scroll_to_mark(mark, 0.0, True, 0, 0)

    def insert_text(self, text):
        self.gui.buffer.insert_at_cursor(text)

    def clear_text(self):
        self.gui.buffer.set_text('')
        
    def set_text(self, text):
        self.gui.buffer.set_text(text)
        

class GuiGadget:
    """
    Class that handles the plugin interfaces for the MyGrampsView.
    """
    TARGET_TYPE_FRAME = 80
    LOCAL_DRAG_TYPE   = 'GADGET'
    LOCAL_DRAG_TARGET = (LOCAL_DRAG_TYPE, 0, TARGET_TYPE_FRAME)
    def __init__(self, viewpage, dbstate, title, **kwargs):
        self.viewpage = viewpage
        self.dbstate = dbstate
        self.title = title
        ########## Set defaults
        self.expand = kwargs.get("expand", False)
        self.height = kwargs.get("height", 200)
        self.column = kwargs.get("column", -1)
        self.row = kwargs.get("row", -1)
        self.state = kwargs.get("state", "maximized")
        ##########
        self.xml = gtk.glade.XML(const.GLADE_FILE, 'gvgadget', "gramps")
        self.mainframe = self.xml.get_widget('gvgadget')
        self.textview = self.xml.get_widget('gvtextview')
        self.buffer = self.textview.get_buffer()
        self.scrolledwindow = self.xml.get_widget('gvscrolledwindow')
        self.titlelabel = self.xml.get_widget('gvtitle')
        self.titlelabel.set_text("<b><i>%s</i></b>" % self.title)
        self.titlelabel.set_use_markup(True)
        self.xml.get_widget('gvclose').connect('clicked', self.close)
        self.xml.get_widget('gvstate').connect('clicked', self.change_state)
        self.xml.get_widget('gvproperties').connect('clicked', 
                                                    self.set_properties)
        self.xml.get_widget('gvcloseimage').set_from_stock(gtk.STOCK_CLOSE,
                                                           gtk.ICON_SIZE_MENU)
        self.xml.get_widget('gvstateimage').set_from_stock(gtk.STOCK_REMOVE,
                                                           gtk.ICON_SIZE_MENU)
        self.xml.get_widget('gvpropertiesimage').set_from_stock(gtk.STOCK_PROPERTIES,
                                                                gtk.ICON_SIZE_MENU)

        # source:
        drag = self.xml.get_widget('gvproperties')
        drag.drag_source_set(gtk.gdk.BUTTON1_MASK,
                             [GuiGadget.LOCAL_DRAG_TARGET],
                             gtk.gdk.ACTION_COPY)

    def close(self, obj):
        del self.viewpage.gadget_map[self.title]
        del self.viewpage.frame_map[str(self.mainframe)]
        self.mainframe.destroy()

    def change_state(self, obj):
        if self.state == "maximized":
            self.scrolledwindow.hide()
            self.xml.get_widget('gvstateimage').set_from_stock(gtk.STOCK_ADD,
                                                               gtk.ICON_SIZE_MENU)
            self.state = "minimized"
        else:
            self.scrolledwindow.show()
            self.xml.get_widget('gvstateimage').set_from_stock(gtk.STOCK_REMOVE,
                                                               gtk.ICON_SIZE_MENU)
            self.state = "maximized"
        if self.expand:
            column = self.mainframe.get_parent() # column
            expand,fill,padding,pack =  column.query_child_packing(self.mainframe)
            column.set_child_packing(self.mainframe,(not expand),fill,padding,pack)

    def set_properties(self, obj):
        self.expand = not self.expand
        if self.state == "maximized":
            column = self.mainframe.get_parent() # column
            expand,fill,padding,pack =  column.query_child_packing(self.mainframe)
            column.set_child_packing(self.mainframe,self.expand,fill,padding,pack)

    def append_text(self, text):
        self.buffer.insert_at_cursor(text)

    def clear_text(self):
        self.buffer.set_text('')
        
    def set_text(self, text):
        self.buffer.set_text(text)
        


class MyGrampsView(PageView.PageView):
    """
    MyGrampsView interface
    """

    def __init__(self, dbstate, uistate):
        """
        Creates a MyGrampsView, with the current dbstate and uistate
        """
        PageView.PageView.__init__(self, _('My Gramps'), dbstate, uistate)
        self.column_count = 3

    def change_db(self, event):
        """
        """
        # FIXME: remove/add widgets from new db ini file
        pass

    def build_widget(self):
        """
        Builds the container widget for the interface. Must be overridden by the
        the base class. Returns a gtk container widget.
        """
        frame = gtk.ScrolledWindow()
        frame.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hbox = gtk.HBox(homogeneous=True)
        # Set up drag and drop
        frame.drag_dest_set(gtk.DEST_DEFAULT_MOTION |
                            gtk.DEST_DEFAULT_HIGHLIGHT |
                            gtk.DEST_DEFAULT_DROP,
                            [('GADGET', 0, 80)],
                            gtk.gdk.ACTION_COPY)
        frame.connect('drag_drop', self.drop_widget)

        frame.add_with_viewport(hbox)
        # Create the columns:
        self.columns = []
        for i in range(self.column_count):
            self.columns.append(gtk.VBox())
            hbox.pack_start(self.columns[-1],expand=True)
        # Load the gadgets
        self.gadget_map = {} # title->gadget
        self.frame_map = {} # frame->gadget
        # FIXME
        # get the user's gadgets from .gramps
        # and/or from open database
        # Load the user's gadgets:
        for (name, opts) in [('Stats Gadget', {}),
                             ('Top Surnames Gadget', {}),
                             #('Families Gadget', {}),
                             #('Families Gadget', {"title": "My Peeps"}),
                             ('Hello World Gadget', {}),
                             ('Log Gadget', {}),
                             ('Shell Gadget', {}),
                             ('Python Gadget', {}),
                             #('Events Gadget', {}),
                             ]:
            all_opts = get_gadget_opts(name, opts)
            if "title" not in all_opts:
                all_opts["title"] = "Untitled Gadget"
            # uniqify titles:
            unique = all_opts["title"]
            cnt = 1
            while unique in self.gadget_map:
                unique = all_opts["title"] + ("-%d" % cnt)
                cnt += 1
            all_opts["title"] = unique
            if all_opts["title"] not in self.gadget_map:
                g = make_requested_gadget(self, name, all_opts, self.dbstate)
                if g:
                    self.gadget_map[all_opts["title"]] = g
                    self.frame_map[str(g.mainframe)] = g
                else:
                    print "Can't make gadget of type '%s'." % name
            else:
                print "Ignoring duplicate named gadget '%s'." % all_opts["title"]

        # put the gadgets where they go:
        cnt = 0
        for gadget in self.gadget_map.values():
            # see if the user wants this in a particular location:
            # and if there are that many columns
            if gadget.column >= 0 and gadget.column < len(self.columns):
                pos = gadget.column
            else:
                # else, spread them out:
                pos = cnt % len(self.columns)
            if gadget.state == "minimized": # starts max, change to min it
                gadget.state = "maximized"
                gadget.change_state(gadget) # minimize it
            # to make as big as possible, set to True:
            self.columns[pos].pack_start(gadget.mainframe, expand=gadget.expand)
            # set height on gadget.scrolledwindow here:
            gadget.scrolledwindow.set_size_request(-1, gadget.height)
            cnt += 1
        return frame

    def drop_widget(self, source, context, x, y, timedata):
        button = context.get_source_widget()
        hbox = button.get_parent()
        mainframe = hbox.get_parent()
        rect = source.get_allocation()
        sx, sy = rect.width, rect.height
        # first, find column:
        col = 0
        for i in range(len(self.columns)):
            if x < (sx/len(self.columns) * (i + 1)): 
                col = i
                break
        fromcol = mainframe.get_parent()
        fromcol.remove(mainframe)
        # now find where to insert in column:
        stack = []
        for gframe in self.columns[col]:
            rect = gframe.get_allocation()
            if y < (rect.y + 15): # starts at 0, this allows insert before
                self.columns[col].remove(gframe)
                stack.append(gframe)
        maingadget = self.frame_map[str(mainframe)]
        if maingadget.state == "maximized":
            expand = maingadget.expand
        else:
            expand = False
        self.columns[col].pack_start(mainframe, expand=expand)
        for gframe in stack:
            gadget = self.frame_map[str(gframe)]
            if gadget.state == "maximized":
                expand = gadget.expand
            else:
                expand = False
            self.columns[col].pack_start(gframe, expand=expand)
        return True

    def define_actions(self):
        """
        Defines the UIManager actions. Called by the ViewManager to set up the
        View. The user typically defines self.action_list and 
        self.action_toggle_list in this function. 
        """
        return ''

    def get_stock(self):
        """
        Returns image associated with the view, which is used for the 
        icon for the button.
        """
        return 'gtk-home'
    
    def build_tree(self):
        return 

