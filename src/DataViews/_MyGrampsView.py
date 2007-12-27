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
import gobject
import traceback
import time
import pango
import os

import Errors
import const
import PageView
import ManagedWindow
import ConfigParser
import Utils

AVAILABLE_GADGETS = {}
GADGET_FILENAME = os.path.join(const.HOME_DIR,"gadgets.ini")
NL = "\n" 

debug = False

def register_gadget(data_dict):
    global AVAILABLE_GADGETS
    base_opts = {"name":"Unnamed Gadget",
                 "state":"maximized",
                 "column": -1, "row": -1,
                 "data": []}
    base_opts.update(data_dict)
    AVAILABLE_GADGETS[base_opts["name"]] = base_opts

def register(**data):
    if "type" in data:
        if data["type"].lower() == "gadget":
            register_gadget(data)
        else:
            print ("Unknown plugin type: '%s'" % data["type"])
    else:
        print ("Plugin did not define type.")

def get_gadget_opts(name, opts):
    if name in AVAILABLE_GADGETS:
        data = AVAILABLE_GADGETS[name]
        my_data = data.copy()
        my_data.update(opts)
        return my_data
    else:
        print ("Unknown gadget name: '%s'" % name)
        return {}

def get_gadget_options_by_name(name):
    if debug: print "name:", name
    if name in AVAILABLE_GADGETS:
        return AVAILABLE_GADGETS[name].copy()
    else:
        print ("Unknown gadget name: '%s'" % name)
        return None

def make_requested_gadget(viewpage, name, opts, dbstate, uistate):
    if name in AVAILABLE_GADGETS:
        gui = GuiGadget(viewpage, dbstate, uistate, **opts)
        if opts.get("content", None):
            opts["content"](gui)
        # now that we have user code, set the tooltips
        msg = None
        if gui.pui:
            msg = gui.pui.tooltip
        if msg == None:
            msg = _("Drag Properties Button to move and click it for setup")
        if msg:
            gui.tooltips = gtk.Tooltips()
            gui.tooltips.set_tip(gui.textview, msg)
        return gui
    return None

class LinkTag(gtk.TextTag):
    lid = 0
    def __init__(self, buffer):
        LinkTag.lid += 1
        gtk.TextTag.__init__(self, str(LinkTag.lid))
        tag_table = buffer.get_tag_table()
        self.set_property('foreground', "#0000ff")
        self.set_property('underline', pango.UNDERLINE_SINGLE)
        tag_table.add(self)

class GadgetWindow(ManagedWindow.ManagedWindow):
    def __init__(self, gadget):
        self.title = gadget.title + " Gadget"
        self.gadget = gadget
        ManagedWindow.ManagedWindow.__init__(self, gadget.uistate, [], gadget)
        self.set_window(gtk.Dialog("",gadget.uistate.window,
                                   gtk.DIALOG_DESTROY_WITH_PARENT,
                                   (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)),
                        None, self.title)
        self.window.set_size_request(400,300)
        self.window.connect('response', self.close)
        self.gadget.mainframe.reparent(self.window.vbox)
        self.window.show()
        
    def build_menu_names(self, obj):
        return (self.title, 'Gadget')

    def get_title(self):
        return self.title

    def close(self, *args):
        """
        Closes the detached GadgetWindow.
        """
        self.gadget.gvclose.show()
        self.gadget.gvstate.show()
        self.gadget.gvproperties.show()
        self.gadget.viewpage.detached_frames.remove(self.gadget)
        self.gadget.state = "maximized"
        self.gadget.mainframe.reparent(self.gadget.parent)
        # FIXME: need to pack as it was, not just stick it in
        ManagedWindow.ManagedWindow.close(self, *args)

#------------------------------------------------------------------------

class Gadget(object):
    def __init__(self, gui):
        self._idle_id = 0
        self._generator = None
        self._need_to_update = False
        self._tags = []
        self.tooltip = None
        self.link_cursor = gtk.gdk.Cursor(gtk.gdk.LEFT_PTR)
        self.standard_cursor = gtk.gdk.Cursor(gtk.gdk.XTERM)
        # links to each other:
        self.gui = gui   # plugin gadget has link to gui
        gui.pui = self   # gui has link to plugin ui
        self.dbstate = gui.dbstate
        self.init()
        self.on_load()
        self.dbstate.connect('database-changed', self._db_changed)
        self.dbstate.connect('active-changed', self.active_changed)
        self.gui.textview.connect('button-press-event', 
                                  self.on_button_press) 
        self.gui.textview.connect('motion-notify-event', 
                                  self.on_motion)

    def init(self): # once, constructor
        pass

    def main(self): # once per db open
        pass 

    def background(self): # return false finishes
        """
        Generator which will be run in the background.
        """
        if debug: print "%s dummy" % self.gui.title
        yield False

    def on_load(self):
        """
        Gadgets should override this to take care of loading previously
        their special data.
        """
        pass

    def on_save(self):
        """
        Gadgets should override this to take care of saving their
        special data.
        """
        if debug: print ("on_save: '%s'" % self.gui.title)
        return

    def active_changed(self, handle):
        pass

    def db_changed(self):
        if debug: print "%s is connecting" % self.gui.title
        pass

    def link(self, text, data):
        buffer = self.gui.buffer
        iter = buffer.get_end_iter()
        offset = buffer.get_char_count()
        self.append_text(text)
        start = buffer.get_iter_at_offset(offset)
        end = buffer.get_end_iter()
        self._tags.append((LinkTag(buffer),data))
        buffer.apply_tag(self._tags[-1][0], start, end)

    def get_text(self):
        start = self.gui.buffer.get_start_iter()
        end = self.gui.buffer.get_end_iter()
        return self.gui.buffer.get_text(start, end)
        
    def insert_text(self, text):
        self.gui.buffer.insert_at_cursor(text)

    def clear_text(self):
        self.gui.buffer.set_text('')
        
    def set_text(self, text, scroll_to='start'):
        self.gui.buffer.set_text('')
        self.append_text(text, scroll_to)

    def append_text(self, text, scroll_to="end"):
        enditer = self.gui.buffer.get_end_iter()
        start = self.gui.buffer.create_mark(None, enditer, True)
        self.gui.buffer.insert(enditer, text)
        if scroll_to == "end":
            enditer = self.gui.buffer.get_end_iter()
            end = self.gui.buffer.create_mark(None, enditer, True)
            self.gui.textview.scroll_to_mark(end, 0.0, True, 0, 0)
        else:
            self.gui.textview.scroll_to_mark(start, 0.0, True, 0, 0)

    def load_data_to_text(self, pos=0):
        if len(self.gui.data) >= pos + 1:
            text = self.gui.data[pos]
            text = text.replace("\\n", chr(10))
            self.set_text(text, 'end')

    def save_text_to_data(self):
        text = self.get_text()
        text = text.replace(chr(10), "\\n")
        self.gui.data.append(text)

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

    def interrupt(self):
        """
        Force the generator to stop running.
        """
        if self._idle_id == 0:
            if debug: print "%s removing from gobject" % self.gui.title
            gobject.source_remove(self._idle_id)
            self._idle_id = 0

    def _db_changed(self, db):
        if debug: print "%s is _connecting" % self.gui.title
        self.dbstate.db = db
        self.gui.dbstate.db = db
        self.db_changed()
        self.update()

    def _updater(self):
        """
        Runs the generator.
        """
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

    def on_motion(self, view, event):
        buffer_location = view.window_to_buffer_coords(gtk.TEXT_WINDOW_TEXT, 
                                                       int(event.x), 
                                                       int(event.y))
        iter = view.get_iter_at_location(*buffer_location)
        for (tag, person_handle) in self._tags:
            if iter.has_tag(tag):
                view.get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(self.link_cursor)
                return False # handle event further, if necessary
        view.get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(self.standard_cursor)
        return False # handle event further, if necessary

    def on_button_press(self, view, event):
        from Editors import EditPerson
        buffer_location = view.window_to_buffer_coords(gtk.TEXT_WINDOW_TEXT, 
                                                       int(event.x), 
                                                       int(event.y))
        iter = view.get_iter_at_location(*buffer_location)
        for (tag, person_handle) in self._tags:
            if iter.has_tag(tag):
                person = self.dbstate.db.get_person_from_handle(person_handle)
                if event.button == 1:
                    if event.type == gtk.gdk._2BUTTON_PRESS:
                        try:
                            EditPerson(self.gui.dbstate, self.gui.uistate, [], person)
                        except Errors.WindowActiveError:
                            pass
                    else:
                        # Create filters on the fly:
                        #f = GenericFilterFactory('Person')()
                        #r = Rules.Person.HasNameOf
                        #rule = r([person.get_primary_name.get_surname()])
                        #f.add_rule(rule)
                        #filter_info = (False, f)
                        #model = self.make_model(self.dbstate.db, 0, 
                        #                        search=filter_info)
                        #self.list.set_model(self.model)
                        #self.dirty = False
                        #self.uistate.show_filter_results(self.dbstate, 
                        #                                 self.model.displayed, 
                        #                                 self.model.total)
                        self.gui.dbstate.change_active_person(person)
                    return True # handled event
        return False # did not handle event

        
def logical_true(value):
    return value in ["True", True, 1, "1"]

class GuiGadget:
    """
    Class that handles the plugin interfaces for the MyGrampsView.
    """
    TARGET_TYPE_FRAME = 80
    LOCAL_DRAG_TYPE   = 'GADGET'
    LOCAL_DRAG_TARGET = (LOCAL_DRAG_TYPE, 0, TARGET_TYPE_FRAME)
    def __init__(self, viewpage, dbstate, uistate, title, **kwargs):
        self.viewpage = viewpage
        self.dbstate = dbstate
        self.uistate = uistate
        self.title = title
        ########## Set defaults
        self.name = kwargs.get("name", "Unnamed Gadget")
        self.expand = logical_true(kwargs.get("expand", False))
        self.height = int(kwargs.get("height", 200))
        self.column = int(kwargs.get("column", -1))
        self.row = int(kwargs.get("row", -1))
        self.state = kwargs.get("state", "maximized")
        self.data = kwargs.get("data", [])
        ##########
        self.pui = None # user code
        self.xml = gtk.glade.XML(const.GLADE_FILE, 'gvgadget', "gramps")
        self.mainframe = self.xml.get_widget('gvgadget')
        self.textview = self.xml.get_widget('gvtextview')
        self.buffer = self.textview.get_buffer()
        self.scrolledwindow = self.xml.get_widget('gvscrolledwindow')
        self.titlelabel = self.xml.get_widget('gvtitle')
        self.titlelabel.set_text("<b><i>%s</i></b>" % self.title)
        self.titlelabel.set_use_markup(True)
        self.gvclose = self.xml.get_widget('gvclose')
        self.gvclose.connect('clicked', self.close)
        self.gvstate = self.xml.get_widget('gvstate')
        self.gvstate.connect('clicked', self.change_state)
        self.gvproperties = self.xml.get_widget('gvproperties')
        self.gvproperties.connect('clicked', self.set_properties)
        self.xml.get_widget('gvcloseimage').set_from_stock(gtk.STOCK_CLOSE,
                                                           gtk.ICON_SIZE_MENU)
        self.xml.get_widget('gvstateimage').set_from_stock(gtk.STOCK_REMOVE,
                                                           gtk.ICON_SIZE_MENU)
        self.xml.get_widget('gvpropertiesimage').set_from_stock(gtk.STOCK_PROPERTIES,
                                                                gtk.ICON_SIZE_MENU)

        # source:
        drag = self.gvproperties
        drag.drag_source_set(gtk.gdk.BUTTON1_MASK,
                             [GuiGadget.LOCAL_DRAG_TARGET],
                             gtk.gdk.ACTION_COPY)

    def close(self, obj):
        if self.state == "windowed":
            return
        del self.viewpage.gadget_map[self.title]
        del self.viewpage.frame_map[str(self.mainframe)]
        self.mainframe.destroy()

    def detach(self):
        # hide buttons:
        self.set_state("maximized")
        self.gvclose.hide()
        self.gvstate.hide()
        self.gvproperties.hide()
        # keep a pointer to old parent frame:
        self.parent = self.mainframe.get_parent()
        self.viewpage.detached_frames.append(self)
        # make a window, and attach it there
        self.detached_window = GadgetWindow(self)
        self.state = "windowed"

    def set_state(self, state):
        self.state = state
        if state == "minimized":
            self.scrolledwindow.hide()
            self.xml.get_widget('gvstateimage').set_from_stock(gtk.STOCK_ADD,
                                                               gtk.ICON_SIZE_MENU)
            column = self.mainframe.get_parent() # column
            expand,fill,padding,pack =  column.query_child_packing(self.mainframe)
            column.set_child_packing(self.mainframe,False,fill,padding,pack)

        else:
            self.scrolledwindow.show()
            self.xml.get_widget('gvstateimage').set_from_stock(gtk.STOCK_REMOVE,
                                                               gtk.ICON_SIZE_MENU)
            column = self.mainframe.get_parent() # column
            expand,fill,padding,pack =  column.query_child_packing(self.mainframe)
            column.set_child_packing(self.mainframe,self.expand,fill,padding,pack)

    def change_state(self, obj):
        if self.state == "windowed":
            pass # don't change if windowed
        else:
            if self.state == "maximized":
                self.set_state("minimized")
            else:
                self.set_state("maximized")
                
    def set_properties(self, obj):
        if self.state == "windowed":
            pass
        else:
            self.detach()
        return
        # FIXME: add control for expand AND detach
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
        
    def get_source_widget(self):
        """
        Hack to allow us to send this object to the drop_widget
        method as a context.
        """
        return self.gvproperties

class MyScrolledWindow(gtk.ScrolledWindow):
    def show_all(self):
        # first show them all:
        gtk.ScrolledWindow.show_all(self)
        # Hack to get around show_all that shows hidden items
        # do once, the first time showing
        if self.viewpage:
            gadgets = [g for g in self.viewpage.gadget_map.values()]
            self.viewpage = None
            for gadget in gadgets:
                if gadget.state == "minimized":
                    gadget.set_state("minimized")

class MyGrampsView(PageView.PageView):
    """
    MyGrampsView interface
    """

    def __init__(self, dbstate, uistate):
        """
        Creates a MyGrampsView, with the current dbstate and uistate
        """
        PageView.PageView.__init__(self, _('My Gramps'), dbstate, uistate)
        self._popup_xy = None

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
        # load the user's gadgets and set columns, etc
        user_gadgets = self.load_gadgets()
        # build the GUI:
        frame = MyScrolledWindow()
        msg = _("Right click to add gadgets")
        self.tooltips = gtk.Tooltips()
        self.tooltips.set_tip(frame, msg)
        frame.viewpage = self
        frame.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.hbox = gtk.HBox(homogeneous=True)
        # FIXME: issue when window is scrolled down; drops in wrong place
        # Set up drag and drop
        frame.drag_dest_set(gtk.DEST_DEFAULT_MOTION |
                            gtk.DEST_DEFAULT_HIGHLIGHT |
                            gtk.DEST_DEFAULT_DROP,
                            [('GADGET', 0, 80)],
                            gtk.gdk.ACTION_COPY)
        frame.connect('drag_drop', self.drop_widget)
        frame.connect('button-press-event', self._button_press)

        frame.add_with_viewport(self.hbox)
        # Create the columns:
        self.columns = []
        for i in range(self.column_count):
            self.columns.append(gtk.VBox())
            self.hbox.pack_start(self.columns[-1],expand=True)
        # Load the gadgets
        self.gadget_map = {} # title->gadget
        self.frame_map = {} # frame->gadget
        self.detached_frames = [] # list of detached mainframes
        # get the user's gadgets from ~/.gramps/gadgets.ini
        # Load the user's gadgets:
        for (name, opts) in user_gadgets:
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
                g = make_requested_gadget(self, name, all_opts, 
                                          self.dbstate, self.uistate)
                if g:
                    self.gadget_map[all_opts["title"]] = g
                    self.frame_map[str(g.mainframe)] = g
                else:
                    print "Can't make gadget of type '%s'." % name
            else:
                print "Ignoring duplicate named gadget '%s'." % all_opts["title"]
        self.place_gadgets()
        return frame

    def clear_gadgets(self):
        """
        Detach all of the mainframe gadgets from the columns.
        """
        gadgets = [g for g in self.gadget_map.values()]
        for gadget in gadgets:
            column = gadget.mainframe.get_parent()
            column.remove(gadget.mainframe)

    def place_gadgets(self):
        """
        Place the gadget mainframes in the columns.
        """
        gadgets = [g for g in self.gadget_map.values()]
        # put the gadgets where they go:
        # sort by row
        gadgets.sort(lambda a, b: cmp(a.row, b.row))
        cnt = 0
        for gadget in gadgets:
            # see if the user wants this in a particular location:
            # and if there are that many columns
            if gadget.column >= 0 and gadget.column < self.column_count:
                pos = gadget.column
            else:
                # else, spread them out:
                pos = cnt % self.column_count
            self.columns[pos].pack_start(gadget.mainframe, expand=gadget.expand)
            gadget.column = pos
            # set height on gadget.scrolledwindow here:
            gadget.scrolledwindow.set_size_request(-1, gadget.height)
            # Can't minimize here, because GRAMPS calls show_all later:
            #if gadget.state == "minimized": # starts max, change to min it
            #    gadget.set_state("minimized") # minimize it
            if gadget.state == "windowed":
                gadget.detach() 
            cnt += 1

    def load_gadgets(self):
        self.column_count = 2 # default for new user
        retval = []
        filename = GADGET_FILENAME
        if filename and os.path.exists(filename):
            cp = ConfigParser.ConfigParser()
            cp.read(filename)
            for sec in cp.sections():
                if sec == "My Gramps View Options":
                    if "column_count" in cp.options(sec):
                        self.column_count = int(cp.get(sec, "column_count"))
                else:
                    data = {}
                    for opt in cp.options(sec):
                        if opt.startswith("data["):
                            temp = data.get("data", [])
                            temp.append(cp.get(sec, opt).strip())
                            data["data"] = temp
                        else:
                            data[opt] = cp.get(sec, opt).strip()
                    if "name" not in data:
                        data["name"] = "Unnamed Gadget"
                    retval.append((data["name"], data)) # name, opts
        else:
            # give defaults as currently known
            for name in ["Top Surnames Gadget", "Welcome Gadget"]:
                if name in AVAILABLE_GADGETS:
                    retval.append((name, AVAILABLE_GADGETS[name]))
        return retval

    def save(self, *args):
        if debug: print "saving"
        filename = GADGET_FILENAME
        try:
            fp = open(filename, "w")
        except:
            print "Failed writing '%s'; gadgets not saved" % filename
            return
        fp.write(";; Gramps gadgets file" + NL)
        fp.write((";; Automatically created at %s" % time.strftime("%Y/%m/%d %H:%M:%S")) + NL + NL)
        fp.write("[My Gramps View Options]" + NL)
        fp.write(("column_count=%d" + NL + NL) % self.column_count)
        for col in range(self.column_count):
            row = 0
            for gframe in self.columns[col]:
                gadget = self.frame_map[str(gframe)]
                opts = get_gadget_options_by_name(gadget.name)
                if opts != None:
                    base_opts = opts.copy()
                    for key in base_opts:
                        if key in gadget.__dict__:
                            base_opts[key] = gadget.__dict__[key]
                    fp.write(("[%s]" + NL) % gadget.title)
                    for key in base_opts:
                        if key == "content": continue
                        if key == "title": continue
                        if key == "column": continue
                        if key == "row": continue
                        if key == "data":
                            cnt = 0
                            for item in base_opts["data"]:
                                fp.write(("data[%d]=%s" + NL) % (cnt, item))
                                cnt += 1
                        else:
                            fp.write(("%s=%s" + NL)% (key, base_opts[key]))
                    fp.write(("column=%d" + NL) % col)
                    fp.write(("row=%d" + NL) % row)
                    fp.write(NL)
                row += 1
        for gadget in self.detached_frames:
            opts = get_gadget_options_by_name(gadget.name)
            if opts != None:
                base_opts = opts.copy()
                for key in base_opts:
                    if key in gadget.__dict__:
                        base_opts[key] = gadget.__dict__[key]
                fp.write(("[%s]" + NL) % gadget.title)
                for key in base_opts:
                    if key == "content": continue
                    if key == "title": continue
                    fp.write(("%s=%s" + NL)% (key, base_opts[key]))
                fp.write(NL)
        fp.close()

    def drop_widget(self, source, context, x, y, timedata):
        """
        This is the destination method for handling drag and drop
        of a gadget onto the main scrolled window.
        """
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
        maingadget.column = col
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
        self.action = gtk.ActionGroup(self.title + "/Gadgets")
        self.action.add_actions([('AddGadget',gtk.STOCK_ADD,_("_Add a gadget")),
                                 ('Columns1',None,_("Set columns to 1"),
                                  None,None,
                                  lambda obj:self.set_columns(1)),
                                 ('Columns2',None,_("Set columns to 2"),
                                  None,None,
                                  lambda obj:self.set_columns(2)),
                                 ('Columns3',None,_("Set columns to 3"),
                                  None,None,
                                  lambda obj:self.set_columns(3)),
                                 ])
        self._add_action_group(self.action)

    def set_columns(self, num):
        # clear the gadgets:
        self.clear_gadgets()
        # clear the columns:
        for column in self.columns:
            frame = column.get_parent()
            frame.remove(column)
            del column
        # create the new ones:
        self.column_count = num
        self.columns = []
        for i in range(self.column_count):
            self.columns.append(gtk.VBox())
            self.columns[-1].show()
            self.hbox.pack_start(self.columns[-1],expand=True)
        # place the gadgets back in the new columns
        self.place_gadgets()
        self.widget.show()

    def add_gadget(self, obj):
        name = obj.get_child().get_label()
        all_opts = get_gadget_options_by_name(name)
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
            g = make_requested_gadget(self, name, all_opts, 
                                      self.dbstate, self.uistate)
            if g:
                self.gadget_map[all_opts["title"]] = g
                self.frame_map[str(g.mainframe)] = g
            else:
                print "Can't make gadget of type '%s'." % name
        else:
            print "Ignoring duplicate named gadget '%s'." % all_opts["title"]

        if g:
            gadget = g
            if gadget.column >= 0 and gadget.column < len(self.columns):
                pos = gadget.column
            else:
                pos = 0
            self.columns[pos].pack_start(gadget.mainframe, expand=gadget.expand)
            # set height on gadget.scrolledwindow here:
            gadget.scrolledwindow.set_size_request(-1, gadget.height)
        ## now drop it in right place
        if self._popup_xy != None:
            self.drop_widget(self.widget, gadget, 
                             self._popup_xy[0], self._popup_xy[1], 0)

    def get_stock(self):
        """
        Returns image associated with the view, which is used for the 
        icon for the button.
        """
        return 'gtk-home'
    
    def build_tree(self):
        return 

    def ui_definition(self):
        return """
        <ui>
          <menubar name="MenuBar">
            <menu action="ViewMenu">
              <menuitem action="AddGadget"/>
              <separator/>
              <menuitem action="Columns1"/>
              <menuitem action="Columns2"/>
              <menuitem action="Columns3"/>
            </menu>
          </menubar>
          <popup name="Popup">
            <menuitem action="AddGadget"/>
            <separator/>
            <menuitem action="Columns1"/>
            <menuitem action="Columns2"/>
            <menuitem action="Columns3"/>
          </popup>
        </ui>
        """
        
    def _button_press(self, obj, event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            self._popup_xy = None
            menu = self.uistate.uimanager.get_widget('/ViewMenu')
            ag_menu = self.uistate.uimanager.get_widget('/ViewMenu/AddGadget')
            if ag_menu:
                qr_menu = ag_menu.get_submenu()
                if qr_menu == None:
                    qr_menu = gtk.Menu()
                    names = AVAILABLE_GADGETS.keys()
                    names.sort()
                    for name in names:
                        Utils.add_menuitem(qr_menu, name, 
                                           None, self.add_gadget)
                    self.uistate.uimanager.get_widget('/ViewMenu/AddGadget').set_submenu(qr_menu)
            #if menu:
            #    menu.popup(None, None, None, event.button, event.time)
                return True
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self._popup_xy = (event.x, event.y)
            menu = self.uistate.uimanager.get_widget('/Popup')
            ag_menu = self.uistate.uimanager.get_widget('/Popup/AddGadget')
            if ag_menu:
                qr_menu = ag_menu.get_submenu()
                if qr_menu == None:
                    qr_menu = gtk.Menu()
                    names = AVAILABLE_GADGETS.keys()
                    names.sort()
                    for name in names:
                        Utils.add_menuitem(qr_menu, name, 
                                           None, self.add_gadget)
                    self.uistate.uimanager.get_widget('/Popup/AddGadget').set_submenu(qr_menu)
            if menu:
                menu.popup(None, None, None, event.button, event.time)
                return True
        return False

    def on_delete(self):
        gadgets = [g for g in self.gadget_map.values()]
        for gadget in gadgets:
            # this is the only place where the gui runs user code directly
            if gadget.pui:
                gadget.pui.on_save()
        self.save()
