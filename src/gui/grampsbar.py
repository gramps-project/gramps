#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011 Nick Hall
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
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
import gtk
import time
import os

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import ConfigParser
import const
from gui.widgets.grampletpane import (AVAILABLE_GRAMPLETS,
                                      GET_AVAILABLE_GRAMPLETS,
                                      get_gramplet_opts,
                                      get_gramplet_options_by_tname,
                                      get_gramplet_options_by_name,
                                      make_requested_gramplet)
from ListModel import ListModel, NOSORT
from QuestionDialog import ErrorDialog

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
NL = "\n"

#-------------------------------------------------------------------------
#
# GrampsBar class
#
#-------------------------------------------------------------------------
class GrampsBar(object):
    """
    A class which defines the graphical representation of the Gramps bar.
    """
    def __init__(self, dbstate, uistate, configfile, close_callback, defaults):

        self.dbstate = dbstate
        self.uistate  = uistate
        self.configfile = os.path.join(const.VERSION_DIR, "%s.ini" % configfile)
        self.close_callback = close_callback
        self.gramplet_map = {} # title->gramplet
        self.filter_page = 0

        self.notebook = gtk.Notebook()
        self.notebook.set_show_border(False)
        self.notebook.set_scrollable(True)
        self.notebook.connect('switch_page', self.__switch_page)

        self.top = self._build_interface(self.notebook)

        self.default_gramplets = defaults
        config_settings, opts_list = self.load_gramplets()

        opts_list.sort(key=lambda opt: opt["page"])
        for opts in opts_list:
            name = opts["name"]
            all_opts = get_gramplet_opts(name, opts)
            all_opts["layout"] = "tabs"
            gramplet = make_requested_gramplet(self, name, all_opts, 
                                               self.dbstate, self.uistate)
            self.gramplet_map[all_opts["title"]] = gramplet
            self.__add_tab(gramplet)

        if config_settings[0]:
            self.top.show()
        self.notebook.set_current_page(config_settings[1])

    def _build_interface(self, notebook):
        """
        Build the user interface.  Must be implemented in adervied class.
        """
        raise NotImplementedError

    def _make_buttons(self):
        """
        Make the buttons.
        """
        close_button = gtk.Button()
        img = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        close_button.set_image(img)
        close_button.set_relief(gtk.RELIEF_NONE)
        close_button.connect('clicked', self.__close_clicked)
        
        delete_button = gtk.Button()
        img = gtk.image_new_from_stock(gtk.STOCK_REMOVE, gtk.ICON_SIZE_MENU)
        delete_button.set_image(img)
        delete_button.set_relief(gtk.RELIEF_NONE)
        delete_button.connect('clicked', self.__delete_clicked)

        add_button = gtk.Button()
        img = gtk.image_new_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_MENU)
        add_button.set_image(img)
        add_button.set_relief(gtk.RELIEF_NONE)
        add_button.connect('clicked', self.__add_clicked)

        return (close_button, delete_button, add_button)
        
    def load_gramplets(self):
        """
        Load the gramplets from the configuration file.
        """
        retval = []
        visible = False
        default_page = 0
        filename = self.configfile
        if filename and os.path.exists(filename):
            cp = ConfigParser.ConfigParser()
            cp.read(filename)
            for sec in cp.sections():
                if sec == "Bar Options":
                    if "visible" in cp.options(sec):
                        visible = cp.get(sec, "visible") == "True"
                    if "page" in cp.options(sec):
                        default_page = int(cp.get(sec, "page"))
                else:
                    data = {"title": sec}
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
                        data["tname"]= _("Unnamed Gramplet")
                    retval.append(data)
        else:
            # give defaults as currently known
            for name in self.default_gramplets:
                if name in AVAILABLE_GRAMPLETS():
                    retval.append(GET_AVAILABLE_GRAMPLETS(name))
        return ((visible, default_page), retval)

    def save(self):
        """
        Save the gramplet configuration.
        """
        if len(self.gramplet_map) == 0:
            return # something is the matter
        filename = self.configfile
        try:
            fp = open(filename, "w")
        except:
            print "Failed writing '%s'; gramplets not saved" % filename
            return
        fp.write(";; Gramps bar configuration file" + NL)
        fp.write((";; Automatically created at %s" %
                                 time.strftime("%Y/%m/%d %H:%M:%S")) + NL + NL)
        fp.write("[Bar Options]" + NL)
        fp.write(("visible=%s" + NL) % self.top.get_property('visible'))
        fp.write(("page=%d" + NL) % self.notebook.get_current_page())
        fp.write(NL) 

        for page_num in range(self.notebook.get_n_pages()):
            title = get_title(self.notebook, page_num)
            gramplet = self.gramplet_map[title]
            if gramplet is None: continue # filter tab
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
                    elif key == "row": continue
                    elif key == "column": continue
                    elif key == "page": continue
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
                fp.write(("page=%d" + NL) % page_num)
                fp.write(NL)

        fp.close()

    def set_active(self):
        """
        Called with the view is set as active.
        """
        page = self.notebook.get_current_page()
        title = get_title(self.notebook, page)
        if title is not None and self.gramplet_map[title] \
            and self.gramplet_map[title].pui:
            self.gramplet_map[title].pui.active = True
            if self.gramplet_map[title].pui.dirty:
                self.gramplet_map[title].pui.update()

    def set_inactive(self):
        """
        Called with the view is set as inactive.
        """
        page = self.notebook.get_current_page()
        title = get_title(self.notebook, page)
        if title is not None and self.gramplet_map[title] \
            and self.gramplet_map[title].pui:
            if self.gramplet_map[title].state != "detached":
                self.gramplet_map[title].pui.active = False

    def on_delete(self):
        """
        Called when the view is closed.
        """
        gramplets = (g for g in self.gramplet_map.itervalues() 
                        if g is not None)
        for gramplet in gramplets:
            # this is the only place where the gui runs user code directly
            if gramplet.pui:
                gramplet.pui.on_save()
        self.save()

    def get_display(self):
        """
        Return the top container widget for the GUI.
        """
        return self.top

    def show(self):
        """
        Show the bottom bar.
        """
        return self.top.show()

    def hide(self):
        """
        Hide the bottom bar.
        """
        return self.top.hide()

    def is_visible(self):
        """
        Return True if the bar is visible, else return False.
        """
        return self.top.get_property('visible')

    def add_filter(self, filter):
        """
        Add a filter.
        """
        self.gramplet_map[_('Filter')] = None
        self.notebook.prepend_page(filter, gtk.Label(_('Filter')))
        self.notebook.set_tab_reorderable(filter, True)
        self.notebook.set_current_page(0)

    def remove_filter(self):
        """
        Remove the filter.
        """
        for page_num in range(self.notebook.get_n_pages()):
            title = get_title(self.notebook, page_num)
            if title == _('Filter'):
                self.notebook.remove_page(page_num)
                del self.gramplet_map[_('Filter')]
                return

    def __close_clicked(self, button):
        """
        Called when the sidebar is closed.
        """
        self.close_callback()
        
    def __add_clicked(self, button):
        """
        Called when the add button is clicked.
        """
        names = [GET_AVAILABLE_GRAMPLETS(key)["tname"] for key 
                 in AVAILABLE_GRAMPLETS()]
        skip = [gramplet.tname for gramplet in self.gramplet_map.values()
                                if gramplet is not None]
        gramplet_list = [name for name in names if name not in skip]
        gramplet_list.sort()
        dialog = ChooseGrampletDialog(_("Select Gramplet"), gramplet_list)
        tname = dialog.run()
        if not tname:
            return

        all_opts = get_gramplet_options_by_tname(tname)
        all_opts["layout"] = "tabs"
        gramplet = make_requested_gramplet(self, all_opts["name"], all_opts, 
                                           self.dbstate, self.uistate)
        if not gramplet:
            print "Problem creating ", tname
            return

        self.gramplet_map[gramplet.title] = gramplet
        page_num = self.__add_tab(gramplet)
        self.notebook.set_current_page(page_num)

    def __add_tab(self, gramplet):
        """
        Add a tab to the notebook for the given gramplet.
        """
        gramplet.scrolledwindow.set_size_request(-1, gramplet.height)
        label = gtk.Label(gramplet.title)
        label.set_tooltip_text(gramplet.tname)
        page_num = self.notebook.append_page(gramplet.mainframe, label)
        self.notebook.set_tab_reorderable(gramplet.mainframe, True)
        return page_num

    def __delete_clicked(self, button):
        """
        Called when the delete button is clicked.
        """
        page_num = self.notebook.get_current_page()
        title = get_title(self.notebook, page_num)
        if self.gramplet_map[title] is None:
            ErrorDialog(
                _("Cannot remove tab"),
                _("The filter tab cannot be removed"))
        else:
            del self.gramplet_map[title]
            self.notebook.remove_page(page_num)
        
    def __switch_page(self, notebook, unused, new_page):
        """
        Called when the user has switched to a new bottombar page.
        """
        old_page = notebook.get_current_page()
        #print "switch from", old_page, "to", new_page
        if old_page >= 0:
            title = get_title(notebook, old_page)
            if self.gramplet_map[title] and self.gramplet_map[title].pui:
                if self.gramplet_map[title].state != "detached":
                    self.gramplet_map[title].pui.active = False

        title = get_title(notebook, new_page)
        if self.gramplet_map[title] and self.gramplet_map[title].pui:
            self.gramplet_map[title].pui.active = True
            if self.gramplet_map[title].pui.dirty:
                self.gramplet_map[title].pui.update()

def get_title(notebook, page_num):
    """
    Reurn the title of a given page in a notebook.
    """
    page = notebook.get_nth_page(page_num)
    if page is None:
        return None
    else:
        return notebook.get_tab_label_text(page)
        
#-------------------------------------------------------------------------
#
# HBar class
#
#-------------------------------------------------------------------------
class HBar(GrampsBar):
    """
    A class which defines the representation of a horizontal Gramps bar.
    """
    def _build_interface(self, notebook):
        """
        Build the horizontal user interface.
        """
        top = gtk.HBox()
        vbox = gtk.VBox()

        close_button, delete_button, add_button = self._make_buttons()

        vbox.pack_start(close_button, False)
        vbox.pack_end(delete_button, False)
        vbox.pack_end(add_button, False)
        
        top.pack_start(notebook, True)
        top.pack_start(vbox, False)
        
        notebook.show()
        vbox.show_all()

        return top

#-------------------------------------------------------------------------
#
# VBar class
#
#-------------------------------------------------------------------------
class VBar(GrampsBar):
    """
    A class which defines the representation of a vertical Gramps bar.
    """
    def _build_interface(self, notebook):
        """
        Build the vertical user interface.
        """
        top = gtk.VBox()
        hbox = gtk.HBox()

        close_button, delete_button, add_button = self._make_buttons()

        hbox.pack_start(add_button, False)
        hbox.pack_start(delete_button, False)
        hbox.pack_end(close_button, False)
        
        top.pack_start(hbox, False)
        top.pack_start(notebook, True)
        
        notebook.show()
        hbox.show_all()

        return top

#-------------------------------------------------------------------------
#
# Choose Gramplet Dialog
#
#-------------------------------------------------------------------------
class ChooseGrampletDialog(object):
    """
    A dialog to choose a gramplet
    """
    def __init__(self, title, names):
        self.title = title
        self.names = names
        self.namelist = None
        self.namemodel = None
        self.top = self._create_dialog()

    def run(self):
        """
        Run the dialog and return the result.
        """
        self._populate_model()
        response = self.top.run()
        result = None
        if response == gtk.RESPONSE_OK:
            store, iter_ = self.namemodel.get_selected()
            if iter_:
                result = store.get_value(iter_, 0)
        self.top.destroy()
        return result

    def _populate_model(self):
        """
        Populate the model.
        """
        self.namemodel.clear()
        for name in self.names:
            self.namemodel.add([name])
        
    def _create_dialog(self):
        """
        Create a dialog box to organize tags.
        """
        # pylint: disable-msg=E1101
        title = _("%(title)s - Gramps") % {'title': self.title}
        top = gtk.Dialog(title)
        top.set_default_size(400, 350)
        top.set_modal(True)
        top.set_has_separator(False)
        top.vbox.set_spacing(5)
        label = gtk.Label('<span size="larger" weight="bold">%s</span>'
                          % self.title)
        label.set_use_markup(True)
        top.vbox.pack_start(label, 0, 0, 5)
        box = gtk.HBox()
        top.vbox.pack_start(box, 1, 1, 5)
        
        name_titles = [(_('Name'), NOSORT, 200)]
        self.namelist = gtk.TreeView()
        self.namemodel = ListModel(self.namelist, name_titles)

        slist = gtk.ScrolledWindow()
        slist.add_with_viewport(self.namelist)
        slist.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        box.pack_start(slist, 1, 1, 5)
        bbox = gtk.VButtonBox()
        bbox.set_layout(gtk.BUTTONBOX_START)
        bbox.set_spacing(6)
        top.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        top.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        box.pack_start(bbox, 0, 0, 5)
        top.show_all()
        return top

