#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2011       Nick Hall
# Copyright (C) 2011       Gary Burton
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
Module that implements the sidebar and bottombar fuctionality.
"""
#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _
import time
import os

#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import ConfigParser
import const
import ManagedWindow
import GrampsDisplay
from gui.widgets.grampletpane import (AVAILABLE_GRAMPLETS,
                                      GET_AVAILABLE_GRAMPLETS,
                                      GET_GRAMPLET_LIST,
                                      get_gramplet_opts,
                                      get_gramplet_options_by_name,
                                      make_requested_gramplet,
                                      GuiGramplet)
from gui.widgets.undoablebuffer import UndoableBuffer
import gui.utils
from QuestionDialog import QuestionDialog

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
WIKI_HELP_PAGE = const.URL_MANUAL_PAGE + '_-_Gramplets'
NL = "\n"

#-------------------------------------------------------------------------
#
# GrampsBar class
#
#-------------------------------------------------------------------------
class GrampsBar(gtk.Notebook):
    """
    A class which defines the graphical representation of the GrampsBar.
    """
    def __init__(self, dbstate, uistate, pageview, configfile, defaults):
        gtk.Notebook.__init__(self)

        self.dbstate = dbstate
        self.uistate = uistate
        self.pageview = pageview
        self.configfile = os.path.join(const.VERSION_DIR, "%s.ini" % configfile)
        self.defaults = defaults
        self.detached_gramplets = []
        self.empty = False

        self.set_group_id(1)
        self.set_show_border(False)
        self.set_scrollable(True)
        self.connect('page-added', self.__page_added)
        self.connect('page-removed', self.__page_removed)
        self.connect('create-window', self.__create_window)
        self.connect('button-press-event', self.__button_press)

        config_settings, opts_list = self.__load(defaults)

        opts_list.sort(key=lambda opt: opt["page"])
        for opts in opts_list:
            if opts["name"] in AVAILABLE_GRAMPLETS():
                all_opts = get_gramplet_opts(opts["name"], opts)
                gramplet = make_requested_gramplet(TabGramplet, self, all_opts, 
                                                   self.dbstate, self.uistate)
                if gramplet:
                    self.__add_tab(gramplet)

        if len(opts_list) == 0:
            self.empty = True
            self.__create_empty_tab()

        if config_settings[0]:
            self.show()
        self.set_current_page(config_settings[1])

        # Connect after gramplets added to prevent making them active
        self.connect('switch-page', self.__switch_page)

    def __load(self, defaults):
        """
        Load the gramplets from the configuration file.
        """
        retval = []
        visible = True
        default_page = 0
        filename = self.configfile
        if filename and os.path.exists(filename):
            cp = ConfigParser.ConfigParser()
            try:
                cp.read(filename)
            except:
                pass
            for sec in cp.sections():
                if sec == "Bar Options":
                    if "visible" in cp.options(sec):
                        visible = cp.get(sec, "visible") == "True"
                    if "page" in cp.options(sec):
                        default_page = int(cp.get(sec, "page"))
                else:
                    data = {}
                    for opt in cp.options(sec):
                        if opt.startswith("data["):
                            temp = data.get("data", {})
                            #temp.append(cp.get(sec, opt).strip())
                            pos = int(opt[5:-1])
                            temp[pos] = cp.get(sec, opt).strip()
                            data["data"] = temp
                        else:
                            data[opt] = cp.get(sec, opt).strip()
                    if "data" in data:
                        data["data"] = [data["data"][key]
                                        for key in sorted(data["data"].keys())]
                    if "name" not in data:
                        data["name"] = "Unnamed Gramplet"
                        data["tname"] = _("Unnamed Gramplet")
                    retval.append(data)
        else:
            # give defaults as currently known
            for name in defaults:
                if name in AVAILABLE_GRAMPLETS():
                    retval.append(GET_AVAILABLE_GRAMPLETS(name))
        return ((visible, default_page), retval)

    def __save(self):
        """
        Save the gramplet configuration.
        """
        filename = self.configfile
        try:
            fp = open(filename, "w")
        except IOError:
            print "Failed writing '%s'; gramplets not saved" % filename
            return
        fp.write(";; Gramps bar configuration file" + NL)
        fp.write((";; Automatically created at %s" %
                                 time.strftime("%Y/%m/%d %H:%M:%S")) + NL + NL)
        fp.write("[Bar Options]" + NL)
        fp.write(("visible=%s" + NL) % self.get_property('visible'))
        fp.write(("page=%d" + NL) % self.get_current_page())
        fp.write(NL) 

        if self.empty:
            gramplet_list = []
        else:
            gramplet_list = [self.get_nth_page(page_num)
                             for page_num in range(self.get_n_pages())]

        for page_num, gramplet in enumerate(gramplet_list):
            opts = get_gramplet_options_by_name(gramplet.gname)
            if opts is not None:
                base_opts = opts.copy()
                for key in base_opts:
                    if key in gramplet.__dict__:
                        base_opts[key] = gramplet.__dict__[key]
                fp.write(("[%s]" + NL) % gramplet.gname)
                for key in base_opts:
                    if key in ["content", "title", "tname", "row", "column", 
                               "page", "version", "gramps"]: # don't save
                        continue
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
                fp.write(("page=%d" + NL) % page_num)
                fp.write(NL)

        fp.close()

    def set_active(self):
        """
        Called with the view is set as active.
        """
        if not self.empty:
            gramplet = self.get_nth_page(self.get_current_page())
            if gramplet and gramplet.pui:
                gramplet.pui.active = True
                if gramplet.pui.dirty:
                    gramplet.pui.update()

    def set_inactive(self):
        """
        Called with the view is set as inactive.
        """
        if not self.empty:
            gramplet = self.get_nth_page(self.get_current_page())
            if gramplet and gramplet.pui:
                gramplet.pui.active = False

    def on_delete(self):
        """
        Called when the view is closed.
        """
        map(self.__dock_gramplet, self.detached_gramplets)
        if not self.empty:
            for page_num in range(self.get_n_pages()):
                gramplet = self.get_nth_page(page_num)
                # this is the only place where the gui runs user code directly
                if gramplet.pui:
                    gramplet.pui.on_save()
        self.__save()

    def add_gramplet(self, gname):
        """
        Add a gramplet by name.
        """
        if self.has_gramplet(gname):
            return
        all_opts = get_gramplet_options_by_name(gname)
        gramplet = make_requested_gramplet(TabGramplet, self, all_opts,
                                           self.dbstate, self.uistate)
        if not gramplet:
            print "Problem creating ", gname
            return

        page_num = self.__add_tab(gramplet)
        self.set_current_page(page_num)

    def remove_gramplet(self, gname):
        """
        Remove a gramplet by name.
        """
        for gramplet in self.detached_gramplets:
            if gramplet.gname == gname:
                self.__dock_gramplet(gramplet)
                self.remove_page(self.page_num(gramplet))
                return

        for page_num in range(self.get_n_pages()):
            gramplet = self.get_nth_page(page_num)
            if gramplet.gname == gname:
                self.remove_page(page_num)
                return

    def has_gramplet(self, gname):
        """
        Return True if the GrampsBar contains the gramplet, else False.
        """
        return gname in self.all_gramplets()

    def all_gramplets(self):
        """
        Return a list of names of all the gramplets in the GrampsBar.
        """
        if self.empty:
            return self.detached_gramplets
        else:
            return [gramplet.gname for gramplet in self.get_children() +
                                                   self.detached_gramplets]

    def restore(self):
        """
        Restore the GrampsBar to its default gramplets.
        """
        map(self.remove_gramplet, self.all_gramplets())
        map(self.add_gramplet, self.defaults)
        self.set_current_page(0)

    def __create_empty_tab(self):
        """
        Create an empty tab to be displayed when the GrampsBar is empty.
        """
        tab_label = gtk.Label(_('Gramps Bar'))
        tab_label.show()
        msg = _('Right-click to the right of the tab to add a gramplet.')
        content = gtk.Label(msg)
        content.show()
        self.append_page(content, tab_label)
        return content

    def __add_tab(self, gramplet):
        """
        Add a tab to the notebook for the given gramplet.
        """
        width = min(int(self.uistate.screen_width() * 0.25), 400)
        height = min(int(self.uistate.screen_height() * 0.20), 400)
        gramplet.set_size_request(width, height)

        page_num = self.append_page(gramplet)
        return page_num

    def __create_tab_label(self, gramplet):
        """
        Create a tab label.
        """
        label = gtk.Label()
        if hasattr(gramplet.pui, "has_data"):
            if gramplet.pui.has_data:
                label.set_text("<b>%s</b>" % gramplet.title)
            else:
                label.set_text(gramplet.title)
        else: # just a function; always show yes it has data
            label.set_text("<b>%s</b>" % gramplet.title)
            
        label.set_use_markup(True)
        label.set_tooltip_text(gramplet.tname)
        label.show_all()
        return label

    def __delete_clicked(self, button, gramplet):
        """
        Called when the delete button is clicked.
        """
        page_num = self.page_num(gramplet)
        self.remove_page(page_num)

    def __switch_page(self, notebook, unused, new_page):
        """
        Called when the user has switched to a new GrampsBar page.
        """
        old_page = notebook.get_current_page()
        if old_page >= 0:
            gramplet = self.get_nth_page(old_page)
            if gramplet and gramplet.pui:
                gramplet.pui.active = False

        gramplet = self.get_nth_page(new_page)
        if not self.empty:
            if gramplet and gramplet.pui:
                gramplet.pui.active = True
                if gramplet.pui.dirty:
                    gramplet.pui.update()

    def __page_added(self, notebook, unused, new_page):
        """
        Called when a new page is added to the GrampsBar.
        """
        gramplet = self.get_nth_page(new_page)
        if self.empty:
            if isinstance(gramplet, TabGramplet):
                self.empty = False
                if new_page == 0:
                    self.remove_page(1)
                else:
                    self.remove_page(0)
            else:
                return
        gramplet.pane = self
        label = self.__create_tab_label(gramplet)
        self.set_tab_label(gramplet, label)
        self.set_tab_reorderable(gramplet, True)
        self.set_tab_detachable(gramplet, True)
        if gramplet in self.detached_gramplets:
            self.detached_gramplets.remove(gramplet)
            self.reorder_child(gramplet, gramplet.page)

    def __page_removed(self, notebook, unused, page_num):
        """
        Called when a page is removed to the GrampsBar.
        """
        if self.get_n_pages() == 0:
            self.empty = True
            self.__create_empty_tab()
        
    def __create_window(self, grampsbar, gramplet, x_pos, y_pos):
        """
        Called when the user has switched to a new GrampsBar page.
        """
        gramplet.page = self.page_num(gramplet)
        self.detached_gramplets.append(gramplet)
        win = DetachedWindow(grampsbar, gramplet, x_pos, y_pos)
        gramplet.detached_window = win
        return win.get_notebook()

    def __dock_gramplet(self, gramplet):
        """
        Dock a detached gramplet.
        """
        gramplet.detached_window.close()
        gramplet.detached_window = None

    def __button_press(self, widget, event):
        """
        Called when a button is pressed in the tabs section of the GrampsBar.
        """
        if gui.utils.is_right_click(event):
            menu = gtk.Menu()

            ag_menu = gtk.MenuItem(_('Add a gramplet'))
            nav_type = self.pageview.navigation_type()
            skip = self.all_gramplets()
            gramplet_list = GET_GRAMPLET_LIST(nav_type, skip)
            gramplet_list.sort()
            self.__create_submenu(ag_menu, gramplet_list, self.__add_clicked)
            ag_menu.show()
            menu.append(ag_menu)

            if not self.empty:
                rg_menu = gtk.MenuItem(_('Remove a gramplet'))
                gramplet_list = [(gramplet.title, gramplet.gname)
                                 for gramplet in self.get_children() +
                                                 self.detached_gramplets]
                gramplet_list.sort()
                self.__create_submenu(rg_menu, gramplet_list,
                                      self.__remove_clicked)
                rg_menu.show()
                menu.append(rg_menu)

            rd_menu = gtk.MenuItem(_('Restore default gramplets'))
            rd_menu.connect("activate", self.__restore_clicked)
            rd_menu.show()
            menu.append(rd_menu)

            menu.popup(None, None, None, 1, event.time)
            return True

        return False

    def __create_submenu(self, main_menu, gramplet_list, callback_func):
        """
        Create a submenu of the context menu.
        """
        if main_menu:
            submenu = main_menu.get_submenu()
            submenu = gtk.Menu()
            for entry in gramplet_list:
                item = gtk.MenuItem(entry[0])
                item.connect("activate", callback_func, entry[1])
                item.show()
                submenu.append(item)
            main_menu.set_submenu(submenu)

    def __add_clicked(self, menu, gname):
        """
        Called when a gramplet is added from the context menu.
        """
        self.add_gramplet(gname)

    def __remove_clicked(self, menu, gname):
        """
        Called when a gramplet is removed from the context menu.
        """
        self.remove_gramplet(gname)

    def __restore_clicked(self, menu):
        """
        Called when restore defaults is clicked from the context menu.
        """
        QuestionDialog(_("Restore to defaults?"),
            _("The Grampsbar will be restored to contain its default "
              "gramplets.  This action cannot be undone."),
            _("OK"),
            self.restore)

    def get_config_funcs(self):
        """
        Return a list of configuration functions.
        """
        funcs = []
        if self.empty:
            gramplets = []
        else:
            gramplets = self.get_children()
        for gramplet in gramplets + self.detached_gramplets:
            gui_options = gramplet.make_gui_options()
            if gui_options:
                funcs.append(self.__build_panel(gramplet.title, gui_options))
        return funcs

    def __build_panel(self, title, gui_options):
        """
        Return a configuration function that returns the title of a page in
        the Configure View dialog and a gtk container defining the page.
        """
        def gramplet_panel(configdialog):
            return title, gui_options
        return gramplet_panel

#-------------------------------------------------------------------------
#
# TabGramplet class
#
#-------------------------------------------------------------------------
class TabGramplet(gtk.ScrolledWindow, GuiGramplet):
    """
    Class that handles the plugin interfaces for the GrampletBar.
    """
    def __init__(self, pane, dbstate, uistate, title, **kwargs):
        """
        Internal constructor for GUI portion of a gramplet.
        """
        gtk.ScrolledWindow.__init__(self)
        GuiGramplet.__init__(self, pane, dbstate, uistate, title, **kwargs)

        self.scrolledwindow = self
        self.textview = gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_wrap_mode(gtk.WRAP_WORD)
        self.buffer = UndoableBuffer()
        self.text_length = 0
        self.textview.set_buffer(self.buffer)
        self.textview.connect("key-press-event", self.on_key_press_event)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add(self.textview)
        self.show_all()
        self.track = []

    def get_title(self):
        return self.title

    def get_container_widget(self):
        """
        Return the top level container widget.
        """
        return self

#-------------------------------------------------------------------------
#
# DetachedWindow class
#
#-------------------------------------------------------------------------
class DetachedWindow(ManagedWindow.ManagedWindow):
    """
    Class for showing a detached gramplet.
    """
    def __init__(self, grampsbar, gramplet, x_pos, y_pos):
        """
        Construct the window.
        """
        self.title = gramplet.title + " " + _("Gramplet")
        self.grampsbar = grampsbar
        self.gramplet = gramplet

        ManagedWindow.ManagedWindow.__init__(self, gramplet.uistate, [],
                                             self.title)
        self.set_window(gtk.Dialog("", gramplet.uistate.window,
                                   gtk.DIALOG_DESTROY_WITH_PARENT,
                                   (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)),
                        None,
                        self.title)
        self.window.move(x_pos, y_pos)
        self.window.set_size_request(gramplet.detached_width,
                                     gramplet.detached_height)
        self.window.add_button(gtk.STOCK_HELP, gtk.RESPONSE_HELP)
        self.window.connect('response', self.handle_response)

        self.notebook = gtk.Notebook()
        self.notebook.set_show_tabs(False)
        self.notebook.set_show_border(False)
        self.notebook.show()
        self.window.vbox.add(self.notebook)
        self.show()

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

    def get_notebook(self):
        """
        Return the notebook.
        """
        return self.notebook

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
        Dock the detached gramplet back in the GrampsBar from where it came.
        """
        size = self.window.get_size()
        self.gramplet.detached_width = size[0]
        self.gramplet.detached_height = size[1]
        self.gramplet.detached_window = None
        self.gramplet.reparent(self.grampsbar)
        ManagedWindow.ManagedWindow.close(self, *args)
