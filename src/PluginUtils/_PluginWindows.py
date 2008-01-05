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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import traceback
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
import gtk
import pango

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import ManagedWindow
import Errors
import _PluginMgr as PluginMgr
import _Tool as Tool
from BasicUtils import name_displayer

#-------------------------------------------------------------------------
#
# PluginStatus: overview of all plugins
#
#-------------------------------------------------------------------------
class PluginStatus(ManagedWindow.ManagedWindow):
    """Displays a dialog showing the status of loaded plugins"""
    
    def __init__(self, state, uistate, track=[]):

        self.title = _("Plugin Status")
        ManagedWindow.ManagedWindow.__init__(self,uistate,track,self.__class__)

        self.set_window(gtk.Dialog("",uistate.window,
                                   gtk.DIALOG_DESTROY_WITH_PARENT,
                                   (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)),
                        None, self.title)
        self.window.set_size_request(600,400)
        self.window.connect('response', self.close)
        
        scrolled_window = gtk.ScrolledWindow()
        self.list = gtk.TreeView()
        self.model = gtk.ListStore(str, str, str, object)
        self.selection = self.list.get_selection()
        
        self.list.set_model(self.model)
        self.list.set_rules_hint(True)
        self.list.connect('button-press-event', self.button_press)
        self.list.append_column(
            gtk.TreeViewColumn(_('Status'), gtk.CellRendererText(),
                               markup=0))
        self.list.append_column(
            gtk.TreeViewColumn(_('File'), gtk.CellRendererText(),
                               text=1))
        self.list.append_column(
            gtk.TreeViewColumn(_('Message'), gtk.CellRendererText(),
                               text=2))

        scrolled_window.add(self.list)
        self.window.vbox.add(scrolled_window)
        self.window.show_all()

        for i in PluginMgr.failmsg_list:
            err = i[1][0]
            
            if err == Errors.UnavailableError:
                self.model.append(row=[
                    '<span color="blue">%s</span>' % _('Unavailable'),
                    i[0], str(i[1][1]), None])
            else:
                self.model.append(row=[
                    '<span weight="bold" color="red">%s</span>' % _('Fail'),
                    i[0], str(i[1][1]), i[1]])

        for i in PluginMgr.success_list:
            modname = i[1].__name__
            descr = PluginMgr.mod2text.get(modname,'')
            self.model.append(row=[
                '<span weight="bold" color="#267726">%s</span>' % _("OK"),
                i[0], descr, None])

    def button_press(self, obj, event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            model, node = self.selection.get_selected()
            data = model.get_value(node, 3)
            name = model.get_value(node, 1)
            if data:
                PluginTrace(self.uistate, self.track, data, name)
                
    def build_menu_names(self,obj):
        return ( _('Summary'),self.title)

#-------------------------------------------------------------------------
#
# Details for an individual plugin that failed
#
#-------------------------------------------------------------------------
class PluginTrace(ManagedWindow.ManagedWindow):
    """Displays a dialog showing the status of loaded plugins"""
    
    def __init__(self, uistate, track, data, name):
        self.name = name
        title = "%s: %s" % (_("Plugin Status"),name)
        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)

        self.set_window(gtk.Dialog("",uistate.window,
                                   gtk.DIALOG_DESTROY_WITH_PARENT,
                                   (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)),
                        None, title)
        self.window.set_size_request(600,400)
        self.window.connect('response', self.close)
        
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.text = gtk.TextView()
        scrolled_window.add(self.text)
        self.text.get_buffer().set_text(
            "".join(traceback.format_exception(data[0],data[1],data[2])))

        self.window.vbox.add(scrolled_window)
        self.window.show_all()

    def build_menu_names(self,obj):
        return (self.name, None)


#-------------------------------------------------------------------------
#
# Classes for tools
#
#-------------------------------------------------------------------------
class LinkTag(gtk.TextTag):
    def __init__(self, link, buffer):
        gtk.TextTag.__init__(self, link)
        tag_table = buffer.get_tag_table()
        self.set_property('foreground', "#0000ff")
        self.set_property('underline', pango.UNDERLINE_SINGLE)
        try:
            tag_table.add(self)
        except ValueError:
            pass # already in table

class ToolManagedWindowBase(ManagedWindow.ManagedWindow):
    """
    Copied from src/ReportBase/_BareReportDialog.py BareReportDialog
    """
    frame_pad = 5
    border_pad = 6
    HELP_TOPIC = None
    def __init__(self, dbstate, uistate, option_class, name, callback=None):
        self.name = name
        ManagedWindow.ManagedWindow.__init__(self, uistate, [], self)

        self.extra_menu = None
        self.widgets = []
        self.frame_names = []
        self.frames = {}
        self.format_menu = None
        self.style_button = None

        window = gtk.Dialog('Tool')
        self.set_window(window,None,self.get_title())
        #self.window.set_has_separator(False)

        #self.window.connect('response', self.close)
        self.cancel = self.window.add_button(gtk.STOCK_CLOSE,
                                             gtk.RESPONSE_CANCEL)
        self.cancel.connect('clicked',self.close)

        self.ok = self.window.add_button(gtk.STOCK_APPLY, gtk.RESPONSE_OK)
        self.ok.connect('clicked',self.on_ok_clicked)

        self.window.set_default_size(600,-1)

        # Set up and run the dialog.  These calls are not in top down
        # order when looking at the dialog box as there is some
        # interaction between the various frames.

        self.setup_title()
        self.setup_header()
        self.tbl = gtk.Table(4,4,False)
        self.tbl.set_col_spacings(12)
        self.tbl.set_row_spacings(6)
        self.tbl.set_border_width(6)
        self.col = 0
        self.window.vbox.add(self.tbl)

        # Build the list of widgets that are used to extend the Options
        # frame and to create other frames
        self.add_user_options()
        
        self.notebook = gtk.Notebook()
        self.notebook.set_border_width(6)
        self.window.vbox.add(self.notebook)

        self.results_text = gtk.TextView() 
        self.results_text.connect('button-press-event', 
                                  self.on_button_press) 
        self.results_text.connect('motion-notify-event', 
                                  self.on_motion)
        self.tags = []
        self.link_cursor = gtk.gdk.Cursor(gtk.gdk.LEFT_PTR)
        self.standard_cursor = gtk.gdk.Cursor(gtk.gdk.XTERM)

        self.setup_other_frames()
        self.set_current_frame(self.initial_frame())
        self.show()

    #------------------------------------------------------------------------
    #
    # Callback functions from the dialog
    #
    #------------------------------------------------------------------------
    def on_cancel(self,*obj):
        pass # cancel just closes

    def on_ok_clicked(self, obj):
        """
        The user is satisfied with the dialog choices. Parse all options
        and run the tool.
        """
        # Save options
        self.options.parse_user_options(self)
        self.options.handler.save_options()
        self.pre_run()
        self.run() # activate results tab
        self.post_run()

    def initial_frame(self):
        return None

    def on_motion(self, view, event):
        buffer_location = view.window_to_buffer_coords(gtk.TEXT_WINDOW_TEXT, 
                                                       int(event.x), 
                                                       int(event.y))
        iter = view.get_iter_at_location(*buffer_location)
        for (tag, person_handle) in self.tags:
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
        for (tag, person_handle) in self.tags:
            if iter.has_tag(tag):
                person = self.db.get_person_from_handle(person_handle)
                if event.button == 1:
                    if event.type == gtk.gdk._2BUTTON_PRESS:
                        try:
                            EditPerson(self.dbstate, self.uistate, [], person)
                        except Errors.WindowActiveError:
                            pass
                    else:
                        self.dbstate.change_active_person(person)
                    return True # handled event
        return False # did not handle event

    def results_write_link(self, text, person, person_handle):
        self.results_write("   ")
        buffer = self.results_text.get_buffer()
        iter = buffer.get_end_iter()
        offset = buffer.get_char_count()
        self.results_write(text)
        start = buffer.get_iter_at_offset(offset)
        end = buffer.get_end_iter()
        self.tags.append((LinkTag(person_handle, buffer),person_handle))
        buffer.apply_tag(self.tags[-1][0], start, end)
        
    def results_write(self, text):
        buffer = self.results_text.get_buffer()
        mark = buffer.create_mark("end", buffer.get_end_iter())
        self.results_text.scroll_to_mark(mark, 0)
        buffer.insert_at_cursor(text)
        buffer.delete_mark_by_name("end")        

    def results_clear(self):
        # Remove all tags and clear text
        buffer = self.results_text.get_buffer()
        tag_table = buffer.get_tag_table()
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        for (tag, handle) in self.tags:
            buffer.remove_tag(tag, start, end)
            tag_table.remove(tag)
        self.tags = []
        buffer.set_text("")
        
    def pre_run(self):
        from Utils import ProgressMeter
        self.progress = ProgressMeter(self.get_title())
        
    def run(self):
        raise NotImplementedError, "tool needs to define a run() method"

    def post_run(self):
        self.progress.close()

    #------------------------------------------------------------------------
    #
    # Functions related to setting up the dialog window.
    #
    #------------------------------------------------------------------------
    def get_title(self):
        """The window title for this dialog"""
        return "Tool" # self.title

    def get_header(self, name):
        """The header line to put at the top of the contents of the
        dialog box.  By default this will just be the name of the
        selected person.  Most subclasses will customize this to give
        some indication of what the report will be, i.e. 'Descendant
        Report for %s'."""
        return self.get_title()
        
    def setup_title(self):
        """Set up the title bar of the dialog.  This function relies
        on the get_title() customization function for what the title
        should be."""
        self.window.set_title(self.get_title())

    def setup_header(self):
        """Set up the header line bar of the dialog.  This function
        relies on the get_header() customization function for what the
        header line should read.  If no customization function is
        supplied by the subclass, the default is to use the full name
        of the currently selected person."""

        title = self.get_header(self.get_title())
        label = gtk.Label('<span size="larger" weight="bold">%s</span>' % title)
        label.set_use_markup(True)
        self.window.vbox.pack_start(label, True, True, self.border_pad)

    def add_frame_option(self,frame_name,label_text,widget,tooltip=None):
        """Similar to add_option this method takes a frame_name, a
        text string and a Gtk Widget. When the interface is built,
        all widgets with the same frame_name are grouped into a
        GtkFrame. This allows the subclass to create its own sections,
        filling them with its own widgets. The subclass is reponsible for
        all managing of the widgets, including extracting the final value
        before the report executes. This task should only be called in
        the add_user_options task."""
        
        if self.frames.has_key(frame_name):
            self.frames[frame_name].append((label_text,widget))
        else:
            self.frames[frame_name] = [(label_text,widget)]
            self.frame_names.append(frame_name)
        if tooltip:
            self.add_tooltip(widget,tooltip)

    def set_current_frame(self, name):
        if name == None:
            self.notebook.set_current_page(0)
        else:
            for frame_name in self.frame_names:
                if name == frame_name:
                    if len(self.frames[frame_name]) > 0:
                        fname, child = self.frames[frame_name][0]
                        page = self.notebook.page_num(child)
                        self.notebook.set_current_page(page)
                    return

    def add_results_frame(self,frame_name="Results"):
        if frame_name not in self.frames:
            window = gtk.ScrolledWindow()
            window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            window.add(self.results_text)
            window.set_shadow_type(gtk.SHADOW_IN)
            self.frames[frame_name] = [[frame_name, window]] 
            self.frame_names.append(frame_name)
            l = gtk.Label("<b>%s</b>" % _(frame_name))
            l.set_use_markup(True)
            self.notebook.append_page(window, l)
            self.notebook.show_all()
        else:
            self.results_clear()
        self.set_current_frame(frame_name)

    def setup_other_frames(self):
        """Similar to add_option this method takes a frame_name, a
        text string and a Gtk Widget. When the interface is built,
        all widgets with the same frame_name are grouped into a
        GtkFrame. This allows the subclass to create its own sections,
        filling them with its own widgets. The subclass is reponsible for
        all managing of the widgets, including extracting the final value
        before the report executes. This task should only be called in
        the add_user_options task."""
        for key in self.frame_names:
            flist = self.frames[key]
            table = gtk.Table(3,len(flist))
            table.set_col_spacings(12)
            table.set_row_spacings(6)
            table.set_border_width(6)
            l = gtk.Label("<b>%s</b>" % key)
            l.set_use_markup(True)
            self.notebook.append_page(table,l)
            row = 0
            for (text,widget) in flist:
                if text:
                    text_widget = gtk.Label('%s:' % text)
                    text_widget.set_alignment(0.0,0.5)
                    table.attach(text_widget, 1, 2, row, row+1,
                                 gtk.SHRINK|gtk.FILL, gtk.SHRINK)
                    table.attach(widget, 2, 3, row, row+1,
                                 yoptions=gtk.SHRINK)
                else:
                    table.attach(widget, 2, 3, row, row+1,
                                 yoptions=gtk.SHRINK)
                row = row + 1
        self.notebook.show_all()

    #------------------------------------------------------------------------
    #
    # Functions related to extending the options
    #
    #------------------------------------------------------------------------
    def add_user_options(self):
        """Called to allow subclasses add widgets to the dialog form.
        It is called immediately before the window is displayed. All
        calls to add_option or add_frame_option should be called in
        this task."""
        self.options.add_user_options(self)

    def build_menu_names(self, obj):
        return (_('Main window'), self.get_title())



class ToolManagedWindowBatch(Tool.BatchTool, ToolManagedWindowBase):
    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        # This constructor will ask a question, set self.fail:
        self.dbstate = dbstate
        self.uistate = uistate
        Tool.BatchTool.__init__(self,dbstate,options_class,name)
        if not self.fail:
            ToolManagedWindowBase.__init__(self, dbstate, uistate, 
                                           options_class, name, callback)

class ToolManagedWindow(Tool.Tool, ToolManagedWindowBase):
    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        self.dbstate = dbstate
        self.uistate = uistate
        Tool.Tool.__init__(self,dbstate,options_class,name)
        ToolManagedWindowBase.__init__(self, dbstate, uistate, options_class, 
                                       name, callback)
