#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Paul Franklin
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import traceback
import os


#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import GObject

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ..managedwindow import ManagedWindow
from . import tool
from ._guioptions import add_gui_options
from ..editors import EditPerson
from gramps.gen.errors import WindowActiveError
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
ngettext = glocale.translation.ngettext  # else "nearby" comments are ignored


def display_message(message):
    """
    A default callback for displaying messages.
    """
    print(message)


#-------------------------------------------------------------------------
#
# Classes for tools
#
#-------------------------------------------------------------------------
class LinkTag(Gtk.TextTag):
    def __init__(self, link, buffer):
        Gtk.TextTag.__init__(self, name=link)
        tag_table = buffer.get_tag_table()
        self.set_property('foreground', "#0000ff")
        self.set_property('underline', Pango.Underline.SINGLE)
        try:
            tag_table.add(self)
        except ValueError:
            pass # already in table

class ToolManagedWindowBase(ManagedWindow):
    """
    Copied from src/ReportBase/_BareReportDialog.py BareReportDialog
    """
    border_pad = 6
    HELP_TOPIC = None
    def __init__(self, dbstate, uistate, option_class, name, callback=None):
        self.name = name
        ManagedWindow.__init__(self, uistate, [], self)

        self.extra_menu = None
        self.widgets = []
        self.frame_names = []
        self.frames = {}
        self.format_menu = None
        self.style_button = None

        window = Gtk.Dialog('Tool')
        self.set_window(window, None, self.get_title())

        #self.window.connect('response', self.close)
        self.cancel = self.window.add_button(_('_Close'),
                                             Gtk.ResponseType.CANCEL)
        self.cancel.connect('clicked', self.close)

        self.ok = self.window.add_button(_('_Execute'), Gtk.ResponseType.OK)
        self.ok.connect('clicked', self.on_ok_clicked)

        self.window.set_default_size(600, -1)

        # Set up and run the dialog.  These calls are not in top down
        # order when looking at the dialog box as there is some
        # interaction between the various frames.

        self.setup_title()
        self.setup_header()

        # Build the list of widgets that are used to extend the Options
        # frame and to create other frames
        self.add_user_options()

        self.notebook = Gtk.Notebook()
        self.notebook.set_border_width(6)
        self.window.get_content_area().add(self.notebook)

        self.results_text = Gtk.TextView()
        self.results_text.connect('button-press-event',
                                  self.on_button_press)
        self.results_text.connect('motion-notify-event',
                                  self.on_motion)
        self.tags = []
        self.link_cursor = \
            Gdk.Cursor.new_for_display(Gdk.Display.get_default(),
                                       Gdk.CursorType.LEFT_PTR)
        self.standard_cursor = \
            Gdk.Cursor.new_for_display(Gdk.Display.get_default(),
                                       Gdk.CursorType.XTERM)

        self.setup_other_frames()
        self.set_current_frame(self.initial_frame())
        self.show()

    #------------------------------------------------------------------------
    #
    # Callback functions from the dialog
    #
    #------------------------------------------------------------------------
    def on_cancel(self, *obj):
        pass # cancel just closes

    def on_ok_clicked(self, obj):
        """
        The user is satisfied with the dialog choices. Parse all options
        and run the tool.
        """
        # Save options
        self.options.parse_user_options()
        self.options.handler.save_options()
        self.pre_run()
        self.run() # activate results tab
        self.post_run()

    def initial_frame(self):
        return None

    def on_motion(self, view, event):
        buffer_location = view.window_to_buffer_coords(Gtk.TextWindowType.TEXT,
                                                       int(event.x),
                                                       int(event.y))
        iter = view.get_iter_at_location(*buffer_location)
        for (tag, person_handle) in self.tags:
            if iter.has_tag(tag):
                _window = view.get_window(Gtk.TextWindowType.TEXT)
                _window.set_cursor(self.link_cursor)
                return False # handle event further, if necessary
        view.get_window(Gtk.TextWindowType.TEXT).set_cursor(self.standard_cursor)
        return False # handle event further, if necessary

    def on_button_press(self, view, event):
        buffer_location = view.window_to_buffer_coords(Gtk.TextWindowType.TEXT,
                                                       int(event.x),
                                                       int(event.y))
        iter = view.get_iter_at_location(*buffer_location)
        for (tag, person_handle) in self.tags:
            if iter.has_tag(tag):
                person = self.dbstate.get_person_from_handle(person_handle)
                if event.button == 1:
                    if event.type == Gdk.EventType._2BUTTON_PRESS:
                        try:
                            EditPerson(self.dbstate, self.uistate, [], person)
                        except WindowActiveError:
                            pass
                    else:
                        self.uistate.set_active(person_handle, 'Person')
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
        self.tags.append((LinkTag(person_handle, buffer), person_handle))
        buffer.apply_tag(self.tags[-1][0], start, end)

    def results_write(self, text):
        buffer = self.results_text.get_buffer()
        mark = buffer.create_mark("end", buffer.get_end_iter())
        self.results_text.scroll_to_mark(mark, 0.0, True, 0, 0)
        buffer.insert_at_cursor(text)
        buffer.delete_mark_by_name("end")

    def write_to_page(self, page, text):
        buffer = page.get_buffer()
        mark = buffer.create_mark("end", buffer.get_end_iter())
        page.scroll_to_mark(mark, 0.0, True, 0, 0)
        buffer.insert_at_cursor(text)
        buffer.delete_mark_by_name("end")

    def clear(self, text):
        # Remove all tags and clear text
        buffer = text.get_buffer()
        tag_table = buffer.get_tag_table()
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        for (tag, handle) in self.tags:
            buffer.remove_tag(tag, start, end)
            tag_table.remove(tag)
        self.tags = []
        buffer.set_text("")

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
        from ..utils import ProgressMeter
        self.progress = ProgressMeter(self.get_title(),
                                      parent=self.window)

    def run(self):
        raise NotImplementedError("tool needs to define a run() method")

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
        label = Gtk.Label(label='<span size="larger" weight="bold">%s</span>' % title)
        label.set_use_markup(True)
        self.window.get_content_area().pack_start(label, False, False,
                                                  self.border_pad)

    def add_frame_option(self, frame_name, label_text, widget):
        """Similar to add_option this method takes a frame_name, a
        text string and a Gtk Widget. When the interface is built,
        all widgets with the same frame_name are grouped into a
        GtkFrame. This allows the subclass to create its own sections,
        filling them with its own widgets. The subclass is reponsible for
        all managing of the widgets, including extracting the final value
        before the report executes. This task should only be called in
        the add_user_options task."""

        if frame_name in self.frames:
            self.frames[frame_name].append((label_text, widget))
        else:
            self.frames[frame_name] = [(label_text, widget)]
            self.frame_names.append(frame_name)

    def set_current_frame(self, name):
        if name is None:
            self.notebook.set_current_page(0)
        else:
            for frame_name in self.frame_names:
                if name == frame_name:
                    if len(self.frames[frame_name]) > 0:
                        fname, child = self.frames[frame_name][0]
                        page = self.notebook.page_num(child)
                        self.notebook.set_current_page(page)
                        return

    def add_results_frame(self, frame_name="Results"):
        if frame_name not in self.frames:
            window = Gtk.ScrolledWindow()
            window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            window.add(self.results_text)
            window.set_shadow_type(Gtk.ShadowType.IN)
            self.frames[frame_name] = [[frame_name, window]]
            self.frame_names.append(frame_name)
            l = Gtk.Label(label="<b>%s</b>" % _(frame_name))
            l.set_use_markup(True)
            self.notebook.append_page(window, l)
            self.notebook.show_all()
        else:
            self.results_clear()
        return self.results_text

    def add_page(self, frame_name="Help"):
        if frame_name not in self.frames:
            text = Gtk.TextView()
            text.set_wrap_mode(Gtk.WrapMode.WORD)
            window = Gtk.ScrolledWindow()
            window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            window.add(text)
            window.set_shadow_type(Gtk.ShadowType.IN)
            self.frames[frame_name] = [[frame_name, window]]
            self.frame_names.append(frame_name)
            l = Gtk.Label(label="<b>%s</b>" % _(frame_name))
            l.set_use_markup(True)
            self.notebook.append_page(window, l)
            self.notebook.show_all()
        else:
            # FIXME: get text
            #
            text = self.frames[frame_name][0][1].something
        return text

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
            grid = Gtk.Grid()
            grid.set_column_spacing(12)
            grid.set_row_spacing(6)
            grid.set_border_width(6)
            l = Gtk.Label(label="<b>%s</b>" % key)
            l.set_use_markup(True)
            self.notebook.append_page(grid, l)
            row = 0
            for (text, widget) in flist:
                widget.set_hexpand(True)
                if text:
                    text_widget = Gtk.Label(label='%s:' % text)
                    text_widget.set_halign(Gtk.Align.START)
                    grid.attach(text_widget, 1, row, 1, 1)
                    grid.attach(widget, 2, row, 1, 1)
                else:
                    grid.attach(widget, 2, row, 1, 1)
                row += 1
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
        add_gui_options(self)

    def build_menu_names(self, obj):
        return (_('Main window'), self.get_title())



class ToolManagedWindowBatch(tool.BatchTool, ToolManagedWindowBase):
    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate
        # This constructor will ask a question, set self.fail:
        self.dbstate = dbstate
        self.uistate = uistate
        tool.BatchTool.__init__(self, dbstate, user, options_class, name)
        if not self.fail:
            ToolManagedWindowBase.__init__(self, dbstate, uistate,
                                           options_class, name, callback)

class ToolManagedWindow(tool.Tool, ToolManagedWindowBase):
    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        self.dbstate = dbstate
        self.uistate = uistate
        tool.Tool.__init__(self, dbstate, options_class, name)
        ToolManagedWindowBase.__init__(self, dbstate, uistate, options_class,
                                       name, callback)

        self.rescan = False
        self.window.run()
            self.rescan = True
