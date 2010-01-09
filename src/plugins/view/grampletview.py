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
# Python modules
#
#-------------------------------------------------------------------------
import gtk
import gobject
import pango

import traceback
import time
import types
import os
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import Errors
import const
from gui.views.pageview import PageView
from gui.editors import EditPerson, EditFamily
import ManagedWindow
import ConfigParser
from gui.utils import add_menuitem
from QuickReports import run_quick_report_by_name
import GrampsDisplay
from glade import Glade
from gui.pluginmanager import GuiPluginManager

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = const.URL_MANUAL_PAGE + '_-_Gramplets'

#-------------------------------------------------------------------------
#
# Globals
#
#-------------------------------------------------------------------------
PLUGMAN = GuiPluginManager.get_instance()

GRAMPLET_FILENAME = os.path.join(const.HOME_DIR,"gramplets.ini")
NL = "\n" 

debug = False

def AVAILABLE_GRAMPLETS():
    return [gplug.id for gplug in PLUGMAN.get_reg_gramplets()]

def GET_AVAILABLE_GRAMPLETS(name):
    for gplug in PLUGMAN.get_reg_gramplets():
        if gplug.id == name:
            return {
                "name":    gplug.id,
                "tname":   gplug.name,
                "version": gplug.version,
                "height":  gplug.height,
                "expand":  gplug.expand, 
                "title":   gplug.gramplet_title,
                "content": gplug.gramplet,
                "detached_width": gplug.detached_width,
                "detached_height": gplug.detached_height,
                "state":   "maximized",
                "gramps":  "0.0.0",
                "column":  -1, 
                "row":     -1,
                "data":    [],
                "help_url": gplug.help_url,
                }
    return None

def parse_tag_attr(text):
    """
    Function used to parse markup.
    """
    text = text.strip()
    parts = text.split(" ", 1)
    attrs = {}
    if len(parts) == 2:
        attr_values = parts[1].split(" ") # "name=value name=value"
        for av in attr_values:
            attribute, value = av.split("=", 1)
            value = value.strip()
            # trim off quotes:
            if value[0] == value[-1] and value[0] in ['"', "'"]:
                value = value[1:-1]
            attrs[attribute.strip().lower()] = value
    return [parts[0].upper(), attrs]

def get_gramplet_opts(name, opts):
    """
    Lookup the options for a given gramplet name and update
    the options with provided dictionary, opts.
    """
    if name in AVAILABLE_GRAMPLETS():
        data = GET_AVAILABLE_GRAMPLETS(name)
        my_data = data.copy()
        my_data.update(opts)
        return my_data
    else:
        print ("Unknown gramplet name: '%s'" % name)
        return {}

def get_gramplet_options_by_name(name):
    """
    Get options by gramplet name.
    """
    if debug: print "name:", name
    if name in AVAILABLE_GRAMPLETS():
        return GET_AVAILABLE_GRAMPLETS(name).copy()
    else:
        print ("Unknown gramplet name: '%s'" % name)
        return None

def get_gramplet_options_by_tname(name):
    """
    get options by translated name.
    """
    if debug: print "name:", name
    for key in AVAILABLE_GRAMPLETS():
        if GET_AVAILABLE_GRAMPLETS(key)["tname"] == name:
            return GET_AVAILABLE_GRAMPLETS(key).copy()
    print ("Unknown gramplet name: '%s'" % name)
    return None

def make_requested_gramplet(viewpage, name, opts, dbstate, uistate):
    """
    Make a GUI gramplet given its name.
    """
    if name in AVAILABLE_GRAMPLETS():
        gui = GuiGramplet(viewpage, dbstate, uistate, **opts)
        if opts.get("content", None):
            pdata = PLUGMAN.get_plugin(opts["name"])
            module = PLUGMAN.load_plugin(pdata)
            if module:
                getattr(module, opts["content"])(gui)
            else:
                print "Error loading gramplet '%s': skipping content" \
                                                                % opts["name"]
        # now that we have user code, set the tooltips
        msg = gui.tooltip
        if msg is None:
            msg = _("Drag Properties Button to move and click it for setup")
        if msg:
            gui.scrolledwindow.set_tooltip_text(msg)
            gui.tooltips_text = msg
        gui.make_gui_options()
        gui.gvoptions.hide()
        return gui
    return None

def logical_true(value):
    """
    Used for converting text file values to booleans.
    """
    return value in ["True", True, 1, "1"]

class LinkTag(gtk.TextTag):
    """
    Class for keeping track of link data.
    """
    lid = 0
    def __init__(self, buffer):
        LinkTag.lid += 1
        gtk.TextTag.__init__(self, str(LinkTag.lid))
        tag_table = buffer.get_tag_table()
        self.set_property('foreground', "blue")
        #self.set_property('underline', pango.UNDERLINE_SINGLE)
        try:
            tag_table.add(self)
        except ValueError: # tag is already in tag table
            pass

class GrampletWindow(ManagedWindow.ManagedWindow):
    """
    Class for showing a detached gramplet.
    """
    def __init__(self, gramplet):
        """
        Constructs the window, and loads the GUI gramplet.
        """
        self.title = gramplet.title + " " + _("Gramplet")
        self.gramplet = gramplet
        # Keep track of what state it was in:
        self.docked_state = gramplet.state
        # Now detach it
        self.gramplet.set_state("detached") 
        ManagedWindow.ManagedWindow.__init__(self, gramplet.uistate, [], self.title)
        self.set_window(gtk.Dialog("",gramplet.uistate.window,
                                   gtk.DIALOG_DESTROY_WITH_PARENT,
                                   (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)),
                        None, self.title)
        self.window.set_size_request(gramplet.detached_width,
                                     gramplet.detached_height)
        self.window.add_button(gtk.STOCK_HELP, gtk.RESPONSE_HELP)
        # add gramplet:
        self.gramplet.mainframe.reparent(self.window.vbox)
        self.window.connect('response', self.handle_response)
        # HACK: must show window to make it work right:
        self.show()
        # But that shows everything, hide them here:
        self.gramplet.gvclose.hide()
        self.gramplet.gvstate.hide()
        self.gramplet.gvproperties.hide()
        if self.gramplet.pui and len(self.gramplet.pui.option_dict) > 0:
            self.gramplet.gvoptions.show()
        else:
            self.gramplet.gvoptions.hide()

    def handle_response(self, object, response):
        """
        Callback for taking care of button clicks.
        """
        if response in [gtk.RESPONSE_CLOSE, gtk.STOCK_CLOSE]:
            self.close()
        elif response == gtk.RESPONSE_HELP:
            # translated name:
            if self.gramplet.help_url:
                if self.gramplet.help_url.startswith("http://"):
                    GrampsDisplay.url(self.gramplet.help_url)
                else:
                    GrampsDisplay.help(self.gramplet.help_url)
            else:
                GrampsDisplay.help(WIKI_HELP_PAGE, 
                                   self.gramplet.tname.replace(" ", "_"))
        
    def build_menu_names(self, obj):
        """
        Part of the GRAMPS window interface.
        """
        return (self.title, 'Gramplet')

    def get_title(self):
        """
        Returns the window title.
        """
        return self.title

    def close(self, *args):
        """
        Dock the detached GrampletWindow back in the column from where it came.
        """
        self.gramplet.gvoptions.hide()
        self.gramplet.viewpage.detached_gramplets.remove(self.gramplet)
        if self.docked_state == "minimized":
            self.gramplet.set_state("minimized")
        else:
            self.gramplet.set_state("maximized")
        viewpage = self.gramplet.viewpage
        col = self.gramplet.column
        stack = []
        for gframe in viewpage.columns[col]:
            gramplet = viewpage.frame_map[str(gframe)]
            if gramplet.row > self.gramplet.row:
                viewpage.columns[col].remove(gframe)
                stack.append(gframe)
        expand = self.gramplet.state == "maximized" and self.gramplet.expand
        column = viewpage.columns[col]
        parent = self.gramplet.viewpage.get_column_frame(self.gramplet.column)
        self.gramplet.mainframe.reparent(parent)
        for gframe in stack:
            gramplet = viewpage.frame_map[str(gframe)]
            expand = gramplet.state == "maximized" and gramplet.expand
            viewpage.columns[col].pack_start(gframe, expand=expand)
        # Now make sure they all have the correct expand:
        for gframe in viewpage.columns[col]:
            gramplet = viewpage.frame_map[str(gframe)]
            expand, fill, padding, pack =  column.query_child_packing(gramplet.mainframe)
            expand = gramplet.state == "maximized" and gramplet.expand
            column.set_child_packing(gramplet.mainframe, expand, fill, padding, pack)
        self.gramplet.gvclose.show()
        self.gramplet.gvstate.show()
        self.gramplet.gvproperties.show()
        ManagedWindow.ManagedWindow.close(self, *args)

#------------------------------------------------------------------------

class GuiGramplet(object):
    """
    Class that handles the plugin interfaces for the GrampletView.
    """
    TARGET_TYPE_FRAME = 80
    LOCAL_DRAG_TYPE   = 'GRAMPLET'
    LOCAL_DRAG_TARGET = (LOCAL_DRAG_TYPE, 0, TARGET_TYPE_FRAME)
    def __init__(self, viewpage, dbstate, uistate, title, **kwargs):
        """
        Internal constructor for GUI portion of a gramplet.
        """
        self.viewpage = viewpage
        self.dbstate = dbstate
        self.uistate = uistate
        self.title = title
        self.force_update = False
        self._tags = []
        self.link_cursor = gtk.gdk.Cursor(gtk.gdk.LEFT_PTR)
        self.standard_cursor = gtk.gdk.Cursor(gtk.gdk.XTERM)
        ########## Set defaults
        self.name = kwargs.get("name", "Unnamed Gramplet")
        self.tname = kwargs.get("tname", "Unnamed Gramplet")
        self.version = kwargs.get("version", "0.0.0")
        self.gramps = kwargs.get("gramps", "0.0.0")
        self.expand = logical_true(kwargs.get("expand", False))
        self.height = int(kwargs.get("height", 200))
        self.column = int(kwargs.get("column", -1))
        self.detached_height = int(kwargs.get("detached_height", 300))
        self.detached_width = int(kwargs.get("detached_width", 400))
        self.row = int(kwargs.get("row", -1))
        self.state = kwargs.get("state", "maximized")
        self.data = kwargs.get("data", [])
        self.help_url = kwargs.get("help_url", None)
        ##########
        self.use_markup = False
        self.pui = None # user code
        self.tooltip = None # text
        self.tooltips = None # gtk tooltip widget
        self.tooltips_text = None
        
        self.xml = Glade()
        self.gvwin = self.xml.toplevel
        self.mainframe = self.xml.get_object('gvgramplet')
        self.gvwin.remove(self.mainframe)

        self.gvoptions = self.xml.get_object('gvoptions')
        self.textview = self.xml.get_object('gvtextview')
        self.buffer = self.textview.get_buffer()
        self.scrolledwindow = self.xml.get_object('gvscrolledwindow')
        self.vboxtop = self.xml.get_object('vboxtop')
        self.titlelabel = self.xml.get_object('gvtitle')
        self.titlelabel.set_text("<b><i>%s</i></b>" % self.title)
        self.titlelabel.set_use_markup(True)
        self.gvclose = self.xml.get_object('gvclose')
        self.gvclose.connect('clicked', self.close)
        self.gvstate = self.xml.get_object('gvstate')
        self.gvstate.connect('clicked', self.change_state)
        self.gvproperties = self.xml.get_object('gvproperties')
        self.gvproperties.connect('clicked', self.set_properties)
        self.xml.get_object('gvcloseimage').set_from_stock(gtk.STOCK_CLOSE,
                                                           gtk.ICON_SIZE_MENU)
        self.xml.get_object('gvstateimage').set_from_stock(gtk.STOCK_REMOVE,
                                                           gtk.ICON_SIZE_MENU)
        self.xml.get_object('gvpropertiesimage').set_from_stock(gtk.STOCK_PROPERTIES,
                                                                gtk.ICON_SIZE_MENU)

        # source:
        drag = self.gvproperties
        drag.drag_source_set(gtk.gdk.BUTTON1_MASK,
                             [GuiGramplet.LOCAL_DRAG_TARGET],
                             gtk.gdk.ACTION_COPY)

    def close(self, *obj):
        """
        Remove (delete) the gramplet from view. 
        """
        if self.state == "detached":
            return
        self.state = "closed"
        self.viewpage.closed_gramplets.append(self)
        self.mainframe.get_parent().remove(self.mainframe)

    def detach(self):
        """
        Detach the gramplet from the GrampletView, and open in own window.
        """
        # hide buttons:
        #self.set_state("detached") 
        self.viewpage.detached_gramplets.append(self)
        # make a window, and attach it there
        self.detached_window = GrampletWindow(self)

    def set_state(self, state):
        """
        Set the state of a gramplet.
        """
        oldstate = self.state
        self.state = state
        if state == "minimized":
            self.scrolledwindow.hide()
            self.xml.get_object('gvstateimage').set_from_stock(gtk.STOCK_ADD,
                                                               gtk.ICON_SIZE_MENU)
            column = self.mainframe.get_parent() # column
            expand,fill,padding,pack =  column.query_child_packing(self.mainframe)
            column.set_child_packing(self.mainframe,False,fill,padding,pack)

        else:
            self.scrolledwindow.show()
            self.xml.get_object('gvstateimage').set_from_stock(gtk.STOCK_REMOVE,
                                                               gtk.ICON_SIZE_MENU)
            column = self.mainframe.get_parent() # column
            expand,fill,padding,pack =  column.query_child_packing(self.mainframe)
            column.set_child_packing(self.mainframe,
                                     self.expand,
                                     fill,
                                     padding,
                                     pack)
            if oldstate is "minimized" and self.pui:
                self.pui.update()

    def change_state(self, obj):
        """
        Change the state of a gramplet.
        """
        if self.state == "detached":
            pass # don't change if detached
        else:
            if self.state == "maximized":
                self.set_state("minimized")
            else:
                self.set_state("maximized")
                
    def set_properties(self, obj):
        """
        Set the properties of a gramplet.
        """
        if self.state == "detached":
            pass
        else:
            self.detach()
        return
        self.expand = not self.expand
        if self.state == "maximized":
            column = self.mainframe.get_parent() # column
            expand,fill,padding,pack =  column.query_child_packing(self.mainframe)
            column.set_child_packing(self.mainframe,self.expand,fill,padding,pack)

    def append_text(self, text, scroll_to="end"):
        enditer = self.buffer.get_end_iter()
        start = self.buffer.create_mark(None, enditer, True)
        self.buffer.insert(enditer, text)
        if scroll_to == "end":
            enditer = self.buffer.get_end_iter()
            end = self.buffer.create_mark(None, enditer, True)
            self.textview.scroll_to_mark(end, 0.0, True, 0, 0)
        elif scroll_to == "start": # beginning of this append
            self.textview.scroll_to_mark(start, 0.0, True, 0, 0)
        elif scroll_to == "begin": # beginning of the buffer
            begin_iter = self.buffer.get_start_iter()
            begin = self.buffer.create_mark(None, begin_iter, True)
            self.textview.scroll_to_mark(begin, 0.0, True, 0, 0)
        else:
            raise AttributeError, ("no such cursor position: '%s'" % scroll_to)

    def clear_text(self):
        self.buffer.set_text('')

    def get_text(self):
        start = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()
        return self.buffer.get_text(start, end)

    def insert_text(self, text):
        self.buffer.insert_at_cursor(text)

    def len_text(self, text):
        i = 0
        r = 0
        while i < len(text):
            if ord(text[i]) > 126:
                t = 0
                while i < len(text) and ord(text[i]) > 126:
                    i += 1
                    t += 1
                r += t/2
            elif text[i] == "\\":
                r += 1
                i += 2
            else:
                r += 1
                i += 1
        return r

    def render_text(self, text):
        markup_pos = {"B": [], "I": [], "U": [], "A": [], "TT": []}
        retval = ""
        i = 0
        r = 0
        tag = ""
        while i < len(text):
            if text[i:i+2] == "</":
                # start of ending tag
                stop = text[i:].find(">")
                if stop < 0:
                    retval += text[i]
                    r += 1
                    i += 1
                else:
                    markup = text[i+2:i+stop].upper() # close tag
                    markup_pos[markup][-1].append(r)
                    i += stop + 1
            elif text[i] == "<":
                # start of start tag
                stop = text[i:].find(">")
                if stop < 0:
                    retval += text[i]
                    r += 1
                    i += 1
                else:
                    markup, attr = parse_tag_attr(text[i+1:i+stop])
                    markup_pos[markup].append([r, attr])
                    i += stop + 1
            elif text[i] == "\\":
                retval += text[i+1]
                r += 1
                i += 2
            elif ord(text[i]) > 126:
                while ord(text[i]) > 126:
                    retval += text[i]
                    i += 1
                r += 1
            else:
                retval += text[i]
                r += 1
                i += 1
        offset = self.len_text(self.get_text())
        self.append_text(retval)
        for items in markup_pos["TT"]:
            if len(items) == 3:
                (a,attributes,b) = items
                start = self.buffer.get_iter_at_offset(a + offset)
                stop = self.buffer.get_iter_at_offset(b + offset)
                self.buffer.apply_tag_by_name("fixed", start, stop)
        for items in markup_pos["B"]:
            if len(items) == 3:
                (a,attributes,b) = items
                start = self.buffer.get_iter_at_offset(a + offset)
                stop = self.buffer.get_iter_at_offset(b + offset)
                self.buffer.apply_tag_by_name("bold", start, stop)
        for items in markup_pos["I"]:
            if len(items) == 3:
                (a,attributes,b) = items
                start = self.buffer.get_iter_at_offset(a + offset)
                stop = self.buffer.get_iter_at_offset(b + offset)
                self.buffer.apply_tag_by_name("italic", start, stop)
        for items in markup_pos["U"]:
            if len(items) == 3:
                (a,attributes,b) = items
                start = self.buffer.get_iter_at_offset(a + offset)
                stop = self.buffer.get_iter_at_offset(b + offset)
                self.buffer.apply_tag_by_name("underline", start, stop)
        for items in markup_pos["A"]:
            if len(items) == 3:
                (a,attributes,b) = items
                start = self.buffer.get_iter_at_offset(a + offset)
                stop = self.buffer.get_iter_at_offset(b + offset)
                if "href" in attributes:
                    url = attributes["href"]
                    self.link_region(start, stop, "URL", url) # tooltip?
                elif "wiki" in attributes:
                    url = attributes["wiki"]
                    self.link_region(start, stop, "WIKI", url) # tooltip?
                else:
                    print "warning: no url on link: '%s'" % text[start, stop]

    def link_region(self, start, stop, link_type, url):
        link_data = (LinkTag(self.buffer), link_type, url, url)
        self._tags.append(link_data)
        self.buffer.apply_tag(link_data[0], start, stop)

    def set_use_markup(self, value):
        if self.use_markup == value: return
        self.use_markup = value
        if value:
            self.buffer.create_tag("bold",weight=pango.WEIGHT_HEAVY)
            self.buffer.create_tag("italic",style=pango.STYLE_ITALIC)
            self.buffer.create_tag("underline",underline=pango.UNDERLINE_SINGLE)
            self.buffer.create_tag("fixed", font="monospace")
        else:
            tag_table = self.buffer.get_tag_table()
            tag_table.foreach(lambda tag, data: tag_table.remove(tag))

    def set_text(self, text, scroll_to='start'):
        self.buffer.set_text('')
        self.append_text(text, scroll_to)

    def get_source_widget(self):
        """
        Hack to allow us to send this object to the drop_widget
        method as a context.
        """
        return self.gvproperties

    def get_container_widget(self):
        return self.scrolledwindow

    def make_gui_options(self):
        if not self.pui: return
        topbox = gtk.VBox()
        hbox = gtk.HBox()
        labels = gtk.VBox()
        options = gtk.VBox()
        hbox.pack_start(labels, False)
        hbox.pack_start(options, True)
        topbox.add(hbox)
        self.gvoptions.add(topbox)
        for item in self.pui.option_order:
            label = gtk.Label(item + ":")
            label.set_alignment(1.0, 0.5)
            labels.add(label)
            options.add(self.pui.option_dict[item][0]) # widget
        save_button = gtk.Button(stock=gtk.STOCK_SAVE)
        topbox.add(save_button)
        topbox.show_all()
        save_button.connect('clicked', self.pui.save_update_options)

    def link(self, text, link_type, data, size=None, tooltip=None):
        buffer = self.buffer
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
        if ttip:
            self.scrolledwindow.set_tooltip_text(ttip)
        elif self.tooltips_text:
            self.scrolledwindow.set_tooltip_text(self.tooltips_text)
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
                    if person is not None:
                        if event.button == 1: # left mouse
                            if event.type == gtk.gdk._2BUTTON_PRESS: # double
                                try:
                                    EditPerson(self.dbstate, 
                                               self.uistate, 
                                               [], person)
                                    return True # handled event
                                except Errors.WindowActiveError:
                                    pass
                            elif event.type == gtk.gdk.BUTTON_PRESS: # single click
                                self.dbstate.change_active_person(person)
                                return True # handled event
                        elif event.button == 3: # right mouse
                            #FIXME: add a popup menu with options
                            try:
                                EditPerson(self.dbstate, 
                                           self.uistate, 
                                           [], person)
                                return True # handled event
                            except Errors.WindowActiveError:
                                pass
                elif link_type == 'Surname':
                    if event.button == 1: # left mouse
                        if event.type == gtk.gdk._2BUTTON_PRESS: # double
                            run_quick_report_by_name(self.dbstate, 
                                                     self.uistate, 
                                                     'samesurnames', 
                                                     handle)
                    return True
                elif link_type == 'Given':
                    if event.button == 1: # left mouse
                        if event.type == gtk.gdk._2BUTTON_PRESS: # double
                            run_quick_report_by_name(self.dbstate, 
                                                     self.uistate, 
                                                     'samegivens_misc', 
                                                     handle)
                    return True
                elif link_type == 'Filter':
                    if event.button == 1: # left mouse
                        if event.type == gtk.gdk._2BUTTON_PRESS: # double
                            run_quick_report_by_name(self.dbstate, 
                                                     self.uistate, 
                                                     'filterbyname', 
                                                     handle)
                    return True
                elif link_type == 'URL':
                    if event.button == 1: # left mouse
                        GrampsDisplay.url(handle)
                    return True
                elif link_type == 'WIKI':
                    if event.button == 1: # left mouse
                        GrampsDisplay.help(handle.replace(" ", "_"))
                    return True
                elif link_type == 'Family':
                    family = self.dbstate.db.get_family_from_handle(handle)
                    if family is not None:
                        if event.button == 1: # left mouse
                            if event.type == gtk.gdk._2BUTTON_PRESS: # double
                                try:
                                    EditFamily(self.dbstate, 
                                               self.uistate, 
                                               [], family)
                                    return True # handled event
                                except Errors.WindowActiveError:
                                    pass
                        elif event.button == 3: # right mouse
                            #FIXME: add a popup menu with options
                            try:
                                EditFamily(self.dbstate, 
                                           self.uistate, 
                                           [], family)
                                return True # handled event
                            except Errors.WindowActiveError:
                                pass
                elif link_type == 'PersonList':
                    if event.button == 1: # left mouse
                        if event.type == gtk.gdk._2BUTTON_PRESS: # double
                            run_quick_report_by_name(self.dbstate, 
                                                     self.uistate, 
                                                     'filterbyname', 
                                                     'list of people',
                                                     handles=handle)
                    return True
                elif link_type == 'Attribute':
                    if event.button == 1: # left mouse
                        if event.type == gtk.gdk._2BUTTON_PRESS: # double
                            run_quick_report_by_name(self.dbstate, 
                                                     self.uistate, 
                                                     'attribute_match', 
                                                     handle)
                    return True
        return False # did not handle event

class MyScrolledWindow(gtk.ScrolledWindow):
    def show_all(self):
        # first show them all:
        gtk.ScrolledWindow.show_all(self)
        # Hack to get around show_all that shows hidden items
        # do once, the first time showing
        if self.viewpage:
            gramplets = (g for g in self.viewpage.gramplet_map.itervalues() 
                            if g is not None)
            self.viewpage = None
            for gramplet in gramplets:
                gramplet.gvoptions.hide()
                if gramplet.state == "minimized":
                    gramplet.set_state("minimized")

class GrampletView(PageView): 
    """
    GrampletView interface
    """

    def __init__(self, dbstate, uistate):
        """
        Create a GrampletView, with the current dbstate and uistate
        """
        PageView.__init__(self, _('Gramplets'), dbstate, uistate)
        self._popup_xy = None

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
        frame.set_tooltip_text(msg)
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

    def get_column_frame(self, column_num):
        if column_num < len(self.columns):
            return self.columns[column_num]
        else:
            return self.columns[-1] # it was too big, so select largest

    def clear_gramplets(self):
        """
        Detach all of the mainframe gramplets from the columns.
        """
        gramplets = (g for g in self.gramplet_map.itervalues() 
                        if g is not None)
        for gramplet in gramplets:
            if (gramplet.state == "detached" or gramplet.state == "closed"):
                continue
            column = gramplet.mainframe.get_parent()
            if column:
                column.remove(gramplet.mainframe)

    def place_gramplets(self, recolumn=False):
        """
        Place the gramplet mainframes in the columns.
        """
        gramplets = [g for g in self.gramplet_map.itervalues() 
                        if g is not None]
        # put the gramplets where they go:
        # sort by row
        gramplets.sort(key=lambda x: x.row)
        rows = [0] * max(self.column_count, 1)
        for cnt, gramplet in enumerate(gramplets):
            # see if the user wants this in a particular location:
            # and if there are that many columns
            if gramplet.column >= 0 and gramplet.column < self.column_count:
                pos = gramplet.column
            else:
                # else, spread them out:
                pos = cnt % self.column_count
            gramplet.column = pos
            gramplet.row = rows[gramplet.column]
            rows[gramplet.column] += 1
            if recolumn and (gramplet.state == "detached" or gramplet.state == "closed"):
                continue
            if gramplet.state == "minimized":
                self.columns[pos].pack_start(gramplet.mainframe, expand=False)
            else:
                self.columns[pos].pack_start(gramplet.mainframe, expand=gramplet.expand)
            # set height on gramplet.scrolledwindow here:
            gramplet.scrolledwindow.set_size_request(-1, gramplet.height)
            # Can't minimize here, because GRAMPS calls show_all later:
            #if gramplet.state == "minimized": # starts max, change to min it
            #    gramplet.set_state("minimized") # minimize it
            # set minimized is called in page subclass hack (above)
            if gramplet.state == "detached":
                gramplet.detach() 
            elif gramplet.state == "closed":
                gramplet.close() 

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
                if name in AVAILABLE_GRAMPLETS():
                    retval.append((name, GET_AVAILABLE_GRAMPLETS(name)))
        return retval

    def save(self, *args):
        if debug: print "saving"
        if len(self.frame_map) + len(self.detached_gramplets) == 0:
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
                if opts is not None:
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
                        elif key == "version": continue # code, don't save
                        elif key == "gramps": continue # code, don't save
                        elif key == "data":
                            if not isinstance(base_opts["data"], (list, tuple)):
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
        for gramplet in self.detached_gramplets:
            opts = get_gramplet_options_by_name(gramplet.name)
            if opts is not None:
                base_opts = opts.copy()
                for key in base_opts:
                    if key in gramplet.__dict__:
                        base_opts[key] = gramplet.__dict__[key]
                fp.write(("[%s]" + NL) % gramplet.title)
                for key in base_opts:
                    if key == "content": continue
                    elif key == "title": continue
                    elif key == "data":
                        if not isinstance(base_opts["data"], (list, tuple)):
                            fp.write(("data[0]=%s" + NL) % base_opts["data"])
                        else:
                            cnt = 0
                            for item in base_opts["data"]:
                                fp.write(("data[%d]=%s" + NL) % (cnt, item))
                                cnt += 1
                    else:
                        fp.write(("%s=%s" + NL)% (key, base_opts[key]))
                fp.write(NL)
        fp.close()

    def drop_widget(self, source, context, x, y, timedata):
        """
        This is the destination method for handling drag and drop
        of a gramplet onto the main scrolled window.
        """
        button = context.get_source_widget()
        hbox = button.get_parent()
        mframe = hbox.get_parent()
        mainframe = mframe.get_parent() # actually a vbox
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
        current_row = 0
        for gframe in self.columns[col]:
            gramplet = self.frame_map[str(gframe)]
            gramplet.row = current_row
            current_row += 1
            rect = gframe.get_allocation()
            if y < (rect.y + 15): # starts at 0, this allows insert before
                self.columns[col].remove(gframe)
                stack.append(gframe)
        maingramplet = self.frame_map.get(str(mainframe), None)
        maingramplet.column = col
        maingramplet.row = current_row
        current_row += 1
        expand = maingramplet.state == "maximized" and maingramplet.expand
        self.columns[col].pack_start(mainframe, expand=expand)
        for gframe in stack:
            gramplet = self.frame_map[str(gframe)]
            gramplet.row = current_row
            current_row += 1
            expand = gramplet.state == "maximized" and gramplet.expand
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
                                 ('RestoreGramplet',None,_("_Undelete gramplet")),
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
        self.place_gramplets(recolumn=True)
        self.widget.show()

    def restore_gramplet(self, obj):
        name = obj.get_child().get_label()
        ############### First kind: from current session
        for gramplet in self.closed_gramplets:
            if gramplet.title == name:
                #gramplet.state = "maximized"
                self.closed_gramplets.remove(gramplet)
                if self._popup_xy is not None:
                    self.drop_widget(self.widget, gramplet, 
                                     self._popup_xy[0], self._popup_xy[1], 0)
                else:
                    self.drop_widget(self.widget, gramplet, 0, 0, 0)
                gramplet.set_state("maximized")
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
            if self._popup_xy is not None:
                self.drop_widget(self.widget, gramplet, 
                                 self._popup_xy[0], self._popup_xy[1], 0)
            else:
                self.drop_widget(self.widget, gramplet, 0, 0, 0)

    def add_gramplet(self, obj):
        tname = obj.get_child().get_label()
        all_opts = get_gramplet_options_by_tname(tname)
        name = all_opts["name"]
        if all_opts is None:
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
            if self._popup_xy is not None:
                self.drop_widget(self.widget, gramplet, 
                                 self._popup_xy[0], self._popup_xy[1], 0)
            else:
                self.drop_widget(self.widget, gramplet, 0, 0, 0)
            #if g.pui:
            #    g.pui.update()
        else:
            print "Can't make gramplet of type '%s'." % name

    def get_stock(self):
        """
        Return image associated with the view, which is used for the 
        icon for the button.
        """
        return 'gramps-gramplet'
    
    def get_viewtype_stock(self):
        """Type of view in category
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
                qr_menu = gtk.Menu()
                names = [GET_AVAILABLE_GRAMPLETS(key)["tname"] for key 
                         in AVAILABLE_GRAMPLETS()]
                names.sort()
                for name in names:
                    add_menuitem(qr_menu, name, 
                                       None, self.add_gramplet)
                self.uistate.uimanager.get_widget('/Popup/AddGramplet').set_submenu(qr_menu)
            rg_menu = self.uistate.uimanager.get_widget('/Popup/RestoreGramplet')
            if rg_menu:
                qr_menu = rg_menu.get_submenu()
                if qr_menu is not None:
                    rg_menu.remove_submenu()
                names = []
                for gramplet in self.closed_gramplets:
                    names.append(gramplet.title)
                for opts in self.closed_opts:
                    names.append(opts["title"])
                names.sort()
                if len(names) > 0:
                    qr_menu = gtk.Menu()
                    for name in names:
                        add_menuitem(qr_menu, name, 
                                           None, self.restore_gramplet)
                    self.uistate.uimanager.get_widget('/Popup/RestoreGramplet').set_submenu(qr_menu)
            if menu:
                menu.popup(None, None, None, event.button, event.time)
                return True
        return False

    def on_delete(self):
        gramplets = (g for g in self.gramplet_map.itervalues() 
                        if g is not None)
        for gramplet in gramplets:
            # this is the only place where the gui runs user code directly
            if gramplet.pui:
                gramplet.pui.on_save()
        self.save()
