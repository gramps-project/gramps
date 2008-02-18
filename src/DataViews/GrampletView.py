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

"""
GrampletView interface.
"""

#-------------------------------------------------------------------------
#
# gtk modules
#
#-------------------------------------------------------------------------
import gtk
from gtk import glade
import gobject
import pango

import traceback
import time
import types
import os
from gettext import gettext as _

import Errors
import const
import PageView
import ManagedWindow
import ConfigParser
import Utils
from QuickReports import run_quick_report_by_name

AVAILABLE_GRAMPLETS = {}
GRAMPLET_FILENAME = os.path.join(const.HOME_DIR,"gramplets.ini")
NL = "\n" 

debug = False

def register_gramplet(data_dict):
    global AVAILABLE_GRAMPLETS
    base_opts = {"name":"Unnamed Gramplet",
                 "tname": _("Unnamed Gramplet"),
                 "state":"maximized",
                 "column": -1, "row": -1,
                 "data": []}
    base_opts.update(data_dict)
    AVAILABLE_GRAMPLETS[base_opts["name"]] = base_opts

def register(**data):
    if "type" in data:
        if data["type"].lower() == "gramplet":
            register_gramplet(data)
        else:
            print ("Unknown plugin type: '%s'" % data["type"])
    else:
        print ("Plugin did not define type.")

def get_gramplet_opts(name, opts):
    if name in AVAILABLE_GRAMPLETS:
        data = AVAILABLE_GRAMPLETS[name]
        my_data = data.copy()
        my_data.update(opts)
        return my_data
    else:
        print ("Unknown gramplet name: '%s'" % name)
        return {}

def get_gramplet_options_by_name(name):
    if debug: print "name:", name
    if name in AVAILABLE_GRAMPLETS:
        return AVAILABLE_GRAMPLETS[name].copy()
    else:
        print ("Unknown gramplet name: '%s'" % name)
        return None

def get_gramplet_options_by_tname(name):
    if debug: print "name:", name
    for key in AVAILABLE_GRAMPLETS:
        if AVAILABLE_GRAMPLETS[key]["tname"] == name:
            return AVAILABLE_GRAMPLETS[key].copy()
    print ("Unknown gramplet name: '%s'" % name)
    return None

def make_requested_gramplet(viewpage, name, opts, dbstate, uistate):
    if name in AVAILABLE_GRAMPLETS:
        gui = GuiGramplet(viewpage, dbstate, uistate, **opts)
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
            gui.tooltips.set_tip(gui.scrolledwindow, msg)
            gui.tooltips_text = msg
        return gui
    return None

class LinkTag(gtk.TextTag):
    lid = 0
    def __init__(self, buffer):
        LinkTag.lid += 1
        gtk.TextTag.__init__(self, str(LinkTag.lid))
        tag_table = buffer.get_tag_table()
        self.set_property('foreground', "#0000ff")
        #self.set_property('underline', pango.UNDERLINE_SINGLE)
        tag_table.add(self)

class GrampletWindow(ManagedWindow.ManagedWindow):
    def __init__(self, gramplet):
        self.title = gramplet.title + " Gramplet"
        self.gramplet = gramplet
        ManagedWindow.ManagedWindow.__init__(self, gramplet.uistate, [], gramplet)
        self.set_window(gtk.Dialog("",gramplet.uistate.window,
                                   gtk.DIALOG_DESTROY_WITH_PARENT,
                                   (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)),
                        None, self.title)
        self.window.set_size_request(gramplet.detached_width,
                                     gramplet.detached_height)
        self.window.connect('response', self.close)
        self.gramplet.mainframe.reparent(self.window.vbox)
        self.window.show()
        
    def build_menu_names(self, obj):
        return (self.title, 'Gramplet')

    def get_title(self):
        return self.title

    def close(self, *args):
        """
        Closes the detached GrampletWindow.
        """
        self.gramplet.gvclose.show()
        self.gramplet.gvstate.show()
        self.gramplet.gvproperties.show()
        self.gramplet.viewpage.detached_gramplets.remove(self.gramplet)
        self.gramplet.state = "maximized"
        self.gramplet.mainframe.reparent(self.gramplet.parent)
        expand,fill,padding,pack =  self.gramplet.parent.query_child_packing(self.gramplet.mainframe)
        self.gramplet.parent.set_child_packing(self.gramplet.mainframe,self.gramplet.expand,fill,padding,pack)
        ManagedWindow.ManagedWindow.close(self, *args)

#------------------------------------------------------------------------

class Gramplet(object):
    def __init__(self, gui):
        self._idle_id = 0
        self._generator = None
        self._need_to_update = False
        self._tags = []
        self.tooltip = None
        self.link_cursor = gtk.gdk.Cursor(gtk.gdk.LEFT_PTR)
        self.standard_cursor = gtk.gdk.Cursor(gtk.gdk.XTERM)
        # links to each other:
        self.gui = gui   # plugin gramplet has link to gui
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
        if self.dbstate.active: # already changed
            self._db_changed(self.dbstate.db)
            self.active_changed(self.dbstate.active.handle)

    def init(self): # once, constructor
        pass

    def main(self): # return false finishes
        """
        Generator which will be run in the background.
        """
        if debug: print "%s dummy" % self.gui.title
        yield False

    def on_load(self):
        """
        Gramplets should override this to take care of loading previously
        their special data.
        """
        pass

    def on_save(self):
        """
        Gramplets should override this to take care of saving their
        special data.
        """
        if debug: print ("on_save: '%s'" % self.gui.title)
        return

    def active_changed(self, handle):
        pass

    def db_changed(self):
        if debug: print "%s is connecting" % self.gui.title
        pass

    def link(self, text, link_type, data, size=None, tooltip=None):
        buffer = self.gui.buffer
        iter = buffer.get_end_iter()
        offset = buffer.get_char_count()
        self.append_text(text)
        start = buffer.get_iter_at_offset(offset)
        end = buffer.get_end_iter()
        link_data = (LinkTag(buffer), link_type, data, tooltip)
        if size:
            link_data[0].set_property("size-points", size)
        self._tags.append(link_data)
        buffer.apply_tag(link_data[0], start, end)

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
        elif scroll_to == "start": # beginning of this append
            self.gui.textview.scroll_to_mark(start, 0.0, True, 0, 0)
        elif scroll_to == "begin": # beginning of this append
            begin_iter = self.gui.buffer.get_start_iter()
            begin = self.gui.buffer.create_mark(None, begin_iter, True)
            self.gui.textview.scroll_to_mark(begin, 0.0, True, 0, 0)
        else:
            raise AttributeError, ("no such cursor position: '%s'" % scroll_to)

    def load_data_to_text(self, pos=0):
        if len(self.gui.data) >= pos + 1:
            text = self.gui.data[pos]
            text = text.replace("\\n", chr(10))
            self.set_text(text, 'end')

    def save_text_to_data(self):
        text = self.get_text()
        text = text.replace(chr(10), "\\n")
        self.gui.data.append(text)

    def update(self, *args):
        if self._idle_id != 0:
            if debug: print "%s interrupt!" % self.gui.title
            self.interrupt()
        if debug: print "%s creating generator" % self.gui.title
        self._generator = self.main()
        if debug: print "%s adding to gobject" % self.gui.title
        self._idle_id = gobject.idle_add(self._updater, 
                                         priority=gobject.PRIORITY_LOW - 10)

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
        if type(self._generator) != types.GeneratorType:
            self._idle_id = 0
            return False
        try:
            retval = self._generator.next()
            if not retval:
                self._idle_id = 0
            return retval
        except StopIteration:
            self._idle_id = 0
            return False
        except Exception, e:
            print "Gramplet gave an error"
            traceback.print_exc()
            print "Continuing after gramplet error..."
            self._idle_id = 0
            return False

    def on_motion(self, view, event):
        buffer_location = view.window_to_buffer_coords(gtk.TEXT_WINDOW_TEXT, 
                                                       int(event.x), 
                                                       int(event.y))
        iter = view.get_iter_at_location(*buffer_location)
        cursor = self.standard_cursor
        ttip = None
        for (tag, link_type, handle, tooltip) in self._tags:
            if iter.has_tag(tag):
                tag.set_property('underline', pango.UNDERLINE_SINGLE)
                cursor = self.link_cursor
                ttip = tooltip
            else:
                tag.set_property('underline', pango.UNDERLINE_NONE)
        view.get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(cursor)
        if self.gui.tooltips:
            if ttip:
                self.gui.tooltips.set_tip(self.gui.scrolledwindow, 
                                          ttip)
            else:
                self.gui.tooltips.set_tip(self.gui.scrolledwindow, 
                                          self.gui.tooltips_text)
        return False # handle event further, if necessary

    def on_button_press(self, view, event):
        buffer_location = view.window_to_buffer_coords(gtk.TEXT_WINDOW_TEXT, 
                                                       int(event.x), 
                                                       int(event.y))
        iter = view.get_iter_at_location(*buffer_location)
        for (tag, link_type, handle, tooltip) in self._tags:
            if iter.has_tag(tag):
                if link_type == 'Person':
                    person = self.dbstate.db.get_person_from_handle(handle)
                    if person != None:
                        if event.button == 1: # left mouse
                            if event.type == gtk.gdk._2BUTTON_PRESS: # double
                                try:
                                    from Editors import EditPerson
                                    EditPerson(self.gui.dbstate, 
                                               self.gui.uistate, 
                                               [], person)
                                    return True # handled event
                                except Errors.WindowActiveError:
                                    pass
                            elif event.type == gtk.gdk.BUTTON_PRESS: # single click
                                self.gui.dbstate.change_active_person(person)
                                return True # handled event
                        elif event.button == 3: # right mouse
                            #FIXME: add a popup menu with options
                            try:
                                from Editors import EditPerson
                                EditPerson(self.gui.dbstate, 
                                           self.gui.uistate, 
                                           [], person)
                                return True # handled event
                            except Errors.WindowActiveError:
                                pass
                elif link_type == 'Surname':
                    if event.button == 1: # left mouse
                        if event.type == gtk.gdk._2BUTTON_PRESS: # double
                            run_quick_report_by_name(self.gui.dbstate, 
                                                     self.gui.uistate, 
                                                     'samesurnames', 
                                                     handle)
                    return True
        return False # did not handle event
        
def logical_true(value):
    return value in ["True", True, 1, "1"]

class GuiGramplet:
    """
    Class that handles the plugin interfaces for the GrampletView.
    """
    TARGET_TYPE_FRAME = 80
    LOCAL_DRAG_TYPE   = 'GRAMPLET'
    LOCAL_DRAG_TARGET = (LOCAL_DRAG_TYPE, 0, TARGET_TYPE_FRAME)
    def __init__(self, viewpage, dbstate, uistate, title, **kwargs):
        self.viewpage = viewpage
        self.dbstate = dbstate
        self.uistate = uistate
        self.title = title
        ########## Set defaults
        self.name = kwargs.get("name", "Unnamed Gramplet")
        self.expand = logical_true(kwargs.get("expand", False))
        self.height = int(kwargs.get("height", 200))
        self.column = int(kwargs.get("column", -1))
        self.detached_height = int(kwargs.get("detached_height", 300))
        self.detached_width = int(kwargs.get("detached_width", 400))
        self.row = int(kwargs.get("row", -1))
        self.state = kwargs.get("state", "maximized")
        self.data = kwargs.get("data", [])
        ##########
        self.pui = None # user code
        self.tooltips = None
        self.tooltips_text = None
        self.xml = glade.XML(const.GLADE_FILE, 'gvgramplet', "gramps")
        self.mainframe = self.xml.get_widget('gvgramplet')
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
                             [GuiGramplet.LOCAL_DRAG_TARGET],
                             gtk.gdk.ACTION_COPY)

    def close(self, *obj):
        if self.state == "windowed":
            return
        self.state = "closed"
        self.viewpage.closed_gramplets.append(self)
        self.mainframe.get_parent().remove(self.mainframe)

    def detach(self):
        # hide buttons:
        self.set_state("maximized")
        self.gvclose.hide()
        self.gvstate.hide()
        self.gvproperties.hide()
        # keep a pointer to old parent frame:
        self.parent = self.mainframe.get_parent()
        self.viewpage.detached_gramplets.append(self)
        # make a window, and attach it there
        self.detached_window = GrampletWindow(self)
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
            gramplets = [g for g in self.viewpage.gramplet_map.values() if g != None]
            self.viewpage = None
            for gramplet in gramplets:
                if gramplet.state == "minimized":
                    gramplet.set_state("minimized")

class GrampletView(PageView.PageView):
    """
    GrampletView interface
    """

    def __init__(self, dbstate, uistate):
        """
        Creates a GrampletView, with the current dbstate and uistate
        """
        PageView.PageView.__init__(self, _('Gramplets'), dbstate, uistate)
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
        # load the user's gramplets and set columns, etc
        user_gramplets = self.load_gramplets()
        # build the GUI:
        frame = MyScrolledWindow()
        msg = _("Right click to add gramplets")
        self.tooltips = gtk.Tooltips()
        self.tooltips.set_tip(frame, msg)
        frame.viewpage = self
        frame.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.hbox = gtk.HBox(homogeneous=True)
        # Set up drag and drop
        frame.drag_dest_set(gtk.DEST_DEFAULT_MOTION |
                            gtk.DEST_DEFAULT_HIGHLIGHT |
                            gtk.DEST_DEFAULT_DROP,
                            [('GRAMPLET', 0, 80)],
                            gtk.gdk.ACTION_COPY)
        frame.connect('drag_drop', self.drop_widget)
        frame.connect('button-press-event', self._button_press)

        frame.add_with_viewport(self.hbox)
        # Create the columns:
        self.columns = []
        for i in range(self.column_count):
            self.columns.append(gtk.VBox())
            self.hbox.pack_start(self.columns[-1],expand=True)
        # Load the gramplets
        self.gramplet_map = {} # title->gramplet
        self.frame_map = {} # frame->gramplet
        self.detached_gramplets = [] # list of detached gramplets
        self.closed_gramplets = []   # list of closed gramplets
        self.closed_opts = []      # list of closed options from ini file
        # get the user's gramplets from ~/.gramps/gramplets.ini
        # Load the user's gramplets:
        for (name, opts) in user_gramplets:
            all_opts = get_gramplet_opts(name, opts)
            if "title" not in all_opts:
                all_opts["title"] = "Untitled Gramplet"
            if "state" not in all_opts:
                all_opts["state"] = "maximized"
            # uniqify titles:
            unique = all_opts["title"]
            cnt = 1
            while unique in self.gramplet_map:
                unique = all_opts["title"] + ("-%d" % cnt)
                cnt += 1
            all_opts["title"] = unique
            if all_opts["state"] == "closed":
                self.gramplet_map[all_opts["title"]] = None # save closed name
                self.closed_opts.append(all_opts)
                continue
            g = make_requested_gramplet(self, name, all_opts, 
                                      self.dbstate, self.uistate)
            if g:
                self.gramplet_map[all_opts["title"]] = g
                self.frame_map[str(g.mainframe)] = g
            else:
                print "Can't make gramplet of type '%s'." % name
        self.place_gramplets()
        return frame

    def clear_gramplets(self):
        """
        Detach all of the mainframe gramplets from the columns.
        """
        gramplets = [g for g in self.gramplet_map.values() if g != None]
        for gramplet in gramplets:
            column = gramplet.mainframe.get_parent()
            if column:
                column.remove(gramplet.mainframe)

    def place_gramplets(self):
        """
        Place the gramplet mainframes in the columns.
        """
        gramplets = [g for g in self.gramplet_map.values() if g != None]
        # put the gramplets where they go:
        # sort by row
        gramplets.sort(lambda a, b: cmp(a.row, b.row))
        cnt = 0
        for gramplet in gramplets:
            # see if the user wants this in a particular location:
            # and if there are that many columns
            if gramplet.column >= 0 and gramplet.column < self.column_count:
                pos = gramplet.column
            else:
                # else, spread them out:
                pos = cnt % self.column_count
            self.columns[pos].pack_start(gramplet.mainframe, expand=gramplet.expand)
            gramplet.column = pos
            # set height on gramplet.scrolledwindow here:
            gramplet.scrolledwindow.set_size_request(-1, gramplet.height)
            # Can't minimize here, because GRAMPS calls show_all later:
            #if gramplet.state == "minimized": # starts max, change to min it
            #    gramplet.set_state("minimized") # minimize it
            # set minimized is called in page subclass hack (above)
            if gramplet.state == "windowed":
                gramplet.detach() 
            elif gramplet.state == "closed":
                gramplet.close() 
            cnt += 1

    def load_gramplets(self):
        self.column_count = 2 # default for new user
        retval = []
        filename = GRAMPLET_FILENAME
        if filename and os.path.exists(filename):
            cp = ConfigParser.ConfigParser()
            cp.read(filename)
            for sec in cp.sections():
                if sec == "Gramplet View Options":
                    if "column_count" in cp.options(sec):
                        self.column_count = int(cp.get(sec, "column_count"))
                else:
                    data = {"title": sec}
                    for opt in cp.options(sec):
                        if opt.startswith("data["):
                            temp = data.get("data", [])
                            temp.append(cp.get(sec, opt).strip())
                            data["data"] = temp
                        else:
                            data[opt] = cp.get(sec, opt).strip()
                    if "name" not in data:
                        data["name"] = "Unnamed Gramplet"
                        data["tname"]= _("Unnamed Gramplet")
                    retval.append((data["name"], data)) # name, opts
        else:
            # give defaults as currently known
            for name in ["Top Surnames Gramplet", "Welcome Gramplet"]:
                if name in AVAILABLE_GRAMPLETS:
                    retval.append((name, AVAILABLE_GRAMPLETS[name]))
        return retval

    def save(self, *args):
        if debug: print "saving"
        if len(self.frame_map.keys() + 
               self.detached_gramplets + 
               self.closed_gramplets) == 0:
            return # something is the matter
        filename = GRAMPLET_FILENAME
        try:
            fp = open(filename, "w")
        except:
            print "Failed writing '%s'; gramplets not saved" % filename
            return
        fp.write(";; Gramps gramplets file" + NL)
        fp.write((";; Automatically created at %s" % time.strftime("%Y/%m/%d %H:%M:%S")) + NL + NL)
        fp.write("[Gramplet View Options]" + NL)
        fp.write(("column_count=%d" + NL + NL) % self.column_count)
        # showing gramplets:
        for col in range(self.column_count):
            row = 0
            for gframe in self.columns[col]:
                gramplet = self.frame_map[str(gframe)]
                opts = get_gramplet_options_by_name(gramplet.name)
                if opts != None:
                    base_opts = opts.copy()
                    for key in base_opts:
                        if key in gramplet.__dict__:
                            base_opts[key] = gramplet.__dict__[key]
                    fp.write(("[%s]" + NL) % gramplet.title)
                    for key in base_opts:
                        if key == "content": continue
                        elif key == "title": continue
                        elif key == "column": continue
                        elif key == "row": continue
                        elif key == "data":
                            if type(base_opts["data"]) not in [list, tuple]:
                                fp.write(("data[0]=%s" + NL) % base_opts["data"])
                            else:
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
        for gramplet in self.detached_gramplets + self.closed_gramplets:
            opts = get_gramplet_options_by_name(gramplet.name)
            if opts != None:
                base_opts = opts.copy()
                for key in base_opts:
                    if key in gramplet.__dict__:
                        base_opts[key] = gramplet.__dict__[key]
                fp.write(("[%s]" + NL) % gramplet.title)
                for key in base_opts:
                    if key == "content": continue
                    elif key == "title": continue
                    elif key == "data":
                        if type(base_opts["data"]) not in [list, tuple]:
                            fp.write(("data[0]=%s" + NL) % base_opts["data"])
                        else:
                            cnt = 0
                            for item in base_opts["data"]:
                                fp.write(("data[%d]=%s" + NL) % (cnt, item))
                                cnt += 1
                    else:
                        fp.write(("%s=%s" + NL)% (key, base_opts[key]))
                fp.write(NL)
        for opts in self.closed_opts:
            fp.write(("[%s]" + NL) % opts["title"])
            for key in opts:
                if key == "content": continue
                elif key == "title": continue
                elif key == "data":
                    if type(opts["data"]) not in [list, tuple]:
                        fp.write(("data[0]=%s" + NL) % opts["data"])
                    else:
                        cnt = 0
                        for item in opts["data"]:
                            fp.write(("data[%d]=%s" + NL) % (cnt, item))
                            cnt += 1
                else:
                    fp.write(("%s=%s" + NL)% (key, opts[key]))
            fp.write(NL)
        fp.close()

    def drop_widget(self, source, context, x, y, timedata):
        """
        This is the destination method for handling drag and drop
        of a gramplet onto the main scrolled window.
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
        if fromcol:
            fromcol.remove(mainframe)
        # now find where to insert in column:
        stack = []
        for gframe in self.columns[col]:
            rect = gframe.get_allocation()
            if y < (rect.y + 15): # starts at 0, this allows insert before
                self.columns[col].remove(gframe)
                stack.append(gframe)
        maingramplet = self.frame_map.get(str(mainframe), None)
        maingramplet.column = col
        if maingramplet.state == "maximized":
            expand = maingramplet.expand
        else:
            expand = False
        self.columns[col].pack_start(mainframe, expand=expand)
        for gframe in stack:
            gramplet = self.frame_map[str(gframe)]
            if gramplet.state == "maximized":
                expand = gramplet.expand
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
        self.action = gtk.ActionGroup(self.title + "/Gramplets")
        self.action.add_actions([('AddGramplet',gtk.STOCK_ADD,_("_Add a gramplet")),
                                 ('RestoreGramplet',None,_("_Restore a gramplet")),
                                 ('DeleteGramplet',None,_("_Delete a gramplet")),
                                 ('Columns1',None,_("Set Columns to _1"),
                                  None,None,
                                  lambda obj:self.set_columns(1)),
                                 ('Columns2',None,_("Set Columns to _2"),
                                  None,None,
                                  lambda obj:self.set_columns(2)),
                                 ('Columns3',None,_("Set Columns to _3"),
                                  None,None,
                                  lambda obj:self.set_columns(3)),
                                 ])
        self._add_action_group(self.action)

    def set_columns(self, num):
        # clear the gramplets:
        self.clear_gramplets()
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
        # place the gramplets back in the new columns
        self.place_gramplets()
        self.widget.show()

    def delete_gramplet(self, obj):
        name = obj.get_child().get_label()
        ############### First kind: from current session
        for gramplet in self.closed_gramplets:
            if gramplet.title == name:
                self.closed_gramplets.remove(gramplet)
                self.gramplet_map[gramplet.title]
                self.frame_map[str(gramplet.mainframe)]
                del gramplet
                return
        ################ Second kind: from options
        for opts in self.closed_opts:
            if opts["title"] == name:
                self.closed_opts.remove(opts)
                return

    def restore_gramplet(self, obj):
        name = obj.get_child().get_label()
        ############### First kind: from current session
        for gramplet in self.closed_gramplets:
            if gramplet.title == name:
                gramplet.state = "maximized"
                self.closed_gramplets.remove(gramplet)
                if self._popup_xy != None:
                    self.drop_widget(self.widget, gramplet, 
                                     self._popup_xy[0], self._popup_xy[1], 0)
                else:
                    self.drop_widget(self.widget, gramplet, 0, 0, 0)
                return
        ################ Second kind: from options
        for opts in self.closed_opts:
            if opts["title"] == name:
                self.closed_opts.remove(opts)
                g = make_requested_gramplet(self, opts["name"], opts, 
                                          self.dbstate, self.uistate)
                if g:
                    self.gramplet_map[opts["title"]] = g
                    self.frame_map[str(g.mainframe)] = g
                else:
                    print "Can't make gramplet of type '%s'." % name
        if g:
            gramplet = g
            gramplet.state = "maximized"
            if gramplet.column >= 0 and gramplet.column < len(self.columns):
                pos = gramplet.column
            else:
                pos = 0
            self.columns[pos].pack_start(gramplet.mainframe, expand=gramplet.expand)
            # set height on gramplet.scrolledwindow here:
            gramplet.scrolledwindow.set_size_request(-1, gramplet.height)
            ## now drop it in right place
            if self._popup_xy != None:
                self.drop_widget(self.widget, gramplet, 
                                 self._popup_xy[0], self._popup_xy[1], 0)
            else:
                self.drop_widget(self.widget, gramplet, 0, 0, 0)

    def add_gramplet(self, obj):
        tname = obj.get_child().get_label()
        all_opts = get_gramplet_options_by_tname(tname)
        name = all_opts["name"]
        if all_opts == None:
            print "Unknown gramplet type: '%s'; bad gramplets.ini file?" % name
            return
        if "title" not in all_opts:
            all_opts["title"] = "Untitled Gramplet"
        # uniqify titles:
        unique = all_opts["title"]
        cnt = 1
        while unique in self.gramplet_map:
            unique = all_opts["title"] + ("-%d" % cnt)
            cnt += 1
        all_opts["title"] = unique
        if all_opts["title"] not in self.gramplet_map:
            g = make_requested_gramplet(self, name, all_opts, 
                                      self.dbstate, self.uistate)
        if g:
            self.gramplet_map[all_opts["title"]] = g
            self.frame_map[str(g.mainframe)] = g
            gramplet = g
            if gramplet.column >= 0 and gramplet.column < len(self.columns):
                pos = gramplet.column
            else:
                pos = 0
            self.columns[pos].pack_start(gramplet.mainframe, expand=gramplet.expand)
            # set height on gramplet.scrolledwindow here:
            gramplet.scrolledwindow.set_size_request(-1, gramplet.height)
            ## now drop it in right place
            if self._popup_xy != None:
                self.drop_widget(self.widget, gramplet, 
                                 self._popup_xy[0], self._popup_xy[1], 0)
            else:
                self.drop_widget(self.widget, gramplet, 0, 0, 0)
        else:
            print "Can't make gramplet of type '%s'." % name

    def get_stock(self):
        """
        Returns image associated with the view, which is used for the 
        icon for the button.
        """
        return 'gramps-gramplet'
    
    def build_tree(self):
        return 

    def ui_definition(self):
        return """
        <ui>
          <menubar name="MenuBar">
            <menu action="ViewMenu">
              <menuitem action="Columns1"/>
              <menuitem action="Columns2"/>
              <menuitem action="Columns3"/>
            </menu>
          </menubar>
          <popup name="Popup">
            <menuitem action="AddGramplet"/>
            <menuitem action="RestoreGramplet"/>
            <menuitem action="DeleteGramplet"/>
            <separator/>
            <menuitem action="Columns1"/>
            <menuitem action="Columns2"/>
            <menuitem action="Columns3"/>
          </popup>
        </ui>
        """
        
    def _button_press(self, obj, event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self._popup_xy = (event.x, event.y)
            menu = self.uistate.uimanager.get_widget('/Popup')
            ag_menu = self.uistate.uimanager.get_widget('/Popup/AddGramplet')
            if ag_menu:
                qr_menu = ag_menu.get_submenu()
                if qr_menu == None:
                    qr_menu = gtk.Menu()
                    names = [AVAILABLE_GRAMPLETS[key]["tname"] for key 
                             in AVAILABLE_GRAMPLETS.keys()]
                    names.sort()
                    for name in names:
                        Utils.add_menuitem(qr_menu, name, 
                                           None, self.add_gramplet)
                    self.uistate.uimanager.get_widget('/Popup/AddGramplet').set_submenu(qr_menu)
            rg_menu = self.uistate.uimanager.get_widget('/Popup/RestoreGramplet')
            dg_menu = self.uistate.uimanager.get_widget('/Popup/DeleteGramplet')
            if rg_menu:
                qr_menu = rg_menu.get_submenu()
                if qr_menu != None:
                    rg_menu.remove_submenu()
                qr2_menu = dg_menu.get_submenu()
                if qr2_menu != None:
                    dg_menu.remove_submenu()
                names = []
                for gramplet in self.closed_gramplets:
                    names.append(gramplet.title)
                for opts in self.closed_opts:
                    names.append(opts["title"])
                names.sort()
                if len(names) > 0:
                    qr_menu = gtk.Menu()
                    qr2_menu = gtk.Menu()
                    for name in names:
                        Utils.add_menuitem(qr_menu, name, 
                                           None, self.restore_gramplet)
                        Utils.add_menuitem(qr2_menu, name, 
                                           None, self.delete_gramplet)
                    self.uistate.uimanager.get_widget('/Popup/RestoreGramplet').set_submenu(qr_menu)
                    self.uistate.uimanager.get_widget('/Popup/DeleteGramplet').set_submenu(qr2_menu)
            if menu:
                menu.popup(None, None, None, event.button, event.time)
                return True
        return False

    def on_delete(self):
        gramplets = [g for g in self.gramplet_map.values() if g != None]
        for gramplet in gramplets:
            # this is the only place where the gui runs user code directly
            if gramplet.pui:
                gramplet.pui.on_save()
        self.save()
