#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
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
import os

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
import gtk
import pango
import gobject

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import ManagedWindow
import Errors
from gen.plug import PluginRegister, PTYPE_STR, make_environment
from gen.ggettext import gettext as _
from gui.utils import open_file_with_default_application
from gui.pluginmanager import GuiPluginManager
import _Tool as Tool
from QuestionDialog import InfoDialog
from gui.editors import EditPerson
import Utils
import const
import config

def version_str_to_tup(sversion, positions):
    """
    Given a string version and positions count, returns a tuple of
    integers.

    >>> version_str_to_tup("1.02.9", 2)
    (1, 2)
    """
    try:
        tup = tuple(([int(n) for n in 
                      sversion.split(".", sversion.count("."))] + 
                     [0] * positions)[0:positions])
    except:
        tup = (0,) * positions
    return tup

def register(ptype, **kwargs):
    """
    Fake registration. Side-effect sets register_results to kwargs.
    """
    retval = {"ptype": ptype}
    retval.update(kwargs)
    # Get the results back to calling function
    if "register_results" in globals():
        globals()["register_results"].append(retval)
    else:
        globals()["register_results"] = [retval]

class Zipfile(object):
    """
    Class to duplicate the methods of tarfile.TarFile, for Python 2.5.
    """
    def __init__(self, buffer):
        import zipfile
        self.buffer = buffer
        self.zip_obj = zipfile.ZipFile(buffer)

    def extractall(self, path, members=None):
        """
        Extract all of the files in the zip into path.
        """
        names = self.zip_obj.namelist()
        for name in self.get_paths(names):
            fullname = os.path.join(path, name)
            if not os.path.exists(fullname): 
                os.mkdir(fullname)
        for name in self.get_files(names):
            fullname = os.path.join(path, name)
            outfile = file(fullname, 'wb')
            outfile.write(self.zip_obj.read(name))
            outfile.close()

    def extractfile(self, name):
        """
        Extract a name from the zip file.

        >>> Zipfile(buffer).extractfile("Dir/dile.py").read()
        <Contents>
        """
        class ExtractFile(object):
            def __init__(self, zip_obj, name):
                self.zip_obj = zip_obj
                self.name = name
            def read(self):
                data = self.zip_obj.read(self.name)
                del self.zip_obj
                return data
        return ExtractFile(self.zip_obj, name)

    def close(self):
        """
        Close the zip object.
        """
        self.zip_obj.close()

    def getnames(self):
        """
        Get the files and directories of the zipfile.
        """
        return self.zip_obj.namelist()

    def get_paths(self, items):
        """
        Get the directories from the items.
        """
        return (name for name in items if self.is_path(name) and not self.is_file(name))

    def get_files(self, items):
        """
        Get the files from the items.
        """
        return (name for name in items if self.is_file(name))

    def is_path(self, name):
        """
        Is the name a path?
        """
        return os.path.split(name)[0]

    def is_file(self, name):
        """
        Is the name a directory?
        """
        return os.path.split(name)[1]

#-------------------------------------------------------------------------
#
# PluginStatus: overview of all plugins
#
#-------------------------------------------------------------------------
class PluginStatus(ManagedWindow.ManagedWindow):
    """Displays a dialog showing the status of loaded plugins"""
    HIDDEN = '<span color="red">%s</span>' % _('Hidden')
    AVAILABLE = '<span weight="bold" color="blue">%s</span>'\
                                % _('Visible')
    
    def __init__(self, uistate, track=[]):
        self.__uistate = uistate
        self.title = _("Plugin Manager")
        ManagedWindow.ManagedWindow.__init__(self, uistate, track,
                                             self.__class__)

        self.__pmgr = GuiPluginManager.get_instance()
        self.__preg = PluginRegister.get_instance()
        self.set_window(gtk.Dialog("", uistate.window,
                                   gtk.DIALOG_DESTROY_WITH_PARENT,
                                   (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)),
                        None, self.title)
        self.window.set_size_request(600, 400)
        self.window.connect('response', self.close)
        
        notebook = gtk.Notebook()
        
        #first page with all registered plugins
        vbox_reg = gtk.VBox()
        scrolled_window_reg =  gtk.ScrolledWindow()
        self.list_reg =  gtk.TreeView()
        #  model: plugintype, hidden, pluginname, plugindescr, pluginid
        self.model_reg = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, 
                gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.selection_reg = self.list_reg.get_selection()
        self.list_reg.set_model(self.model_reg)
        self.list_reg.set_rules_hint(True)
        self.list_reg.connect('button-press-event', self.button_press_reg)
        col0_reg = gtk.TreeViewColumn(_('Type'), gtk.CellRendererText(), text=0)
        col0_reg.set_sort_column_id(0)
        self.list_reg.append_column(col0_reg)
        col = gtk.TreeViewColumn(_('Status'), gtk.CellRendererText(), markup=1)
        col.set_sort_column_id(1)
        self.list_reg.append_column(col)
        col2_reg = gtk.TreeViewColumn(_('Name'), gtk.CellRendererText(), text=2)
        col2_reg.set_sort_column_id(2)
        self.list_reg.append_column(col2_reg)
        col = gtk.TreeViewColumn(_('Description'), gtk.CellRendererText(), text=3)
        col.set_sort_column_id(3)
        self.list_reg.append_column(col)
        self.list_reg.set_search_column(2)

        scrolled_window_reg.add(self.list_reg)
        vbox_reg.pack_start(scrolled_window_reg)
        hbutbox = gtk.HButtonBox()
        hbutbox.set_layout(gtk.BUTTONBOX_SPREAD)
        self.__info_btn = gtk.Button(_("Info"))
        hbutbox.add(self.__info_btn)
        self.__info_btn.connect('clicked', self.__info, self.list_reg, 4) # id_col
        self.__hide_btn = gtk.Button(_("Hide/Unhide"))
        hbutbox.add(self.__hide_btn)
        self.__hide_btn.connect('clicked', self.__hide, 
                                self.list_reg, 4, 1) # list, id_col, hide_col
        if __debug__:
            self.__edit_btn = gtk.Button(_("Edit"))
            hbutbox.add(self.__edit_btn)
            self.__edit_btn.connect('clicked', self.__edit, self.list_reg, 4) # id_col
            self.__load_btn = gtk.Button(_("Load"))
            hbutbox.add(self.__load_btn)
            self.__load_btn.connect('clicked', self.__load, self.list_reg, 4) # id_col
        vbox_reg.pack_start(hbutbox, expand=False, padding=5)
        
        notebook.append_page(vbox_reg, 
                             tab_label=gtk.Label(_('Registered Plugins')))
        
        #second page with loaded plugins
        vbox_loaded = gtk.VBox()
        scrolled_window = gtk.ScrolledWindow()
        self.list = gtk.TreeView()
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, 
                                   gobject.TYPE_STRING, object, 
                                   gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.selection = self.list.get_selection()
        self.list.set_model(self.model)
        self.list.set_rules_hint(True)
        self.list.connect('button-press-event', self.button_press)
        col = gtk.TreeViewColumn(_('Loaded'), gtk.CellRendererText(),
                                 markup=0)
        col.set_sort_column_id(0)
        self.list.append_column(col)
        col1 = gtk.TreeViewColumn(_('File'), gtk.CellRendererText(), 
                                  text=1)
        col1.set_sort_column_id(1)
        self.list.append_column(col1)
        col = gtk.TreeViewColumn(_('Status'), gtk.CellRendererText(), 
                                 markup=5)
        col.set_sort_column_id(5)
        self.list.append_column(col)
        col2 = gtk.TreeViewColumn(_('Message'), gtk.CellRendererText(), text=2)
        col2.set_sort_column_id(2)
        self.list.append_column(col2)
        self.list.set_search_column(1)

        scrolled_window.add(self.list)
        vbox_loaded.pack_start(scrolled_window)
        hbutbox = gtk.HButtonBox()
        hbutbox.set_layout(gtk.BUTTONBOX_SPREAD)
        self.__info_btn = gtk.Button(_("Info"))
        hbutbox.add(self.__info_btn)
        self.__info_btn.connect('clicked', self.__info, self.list, 4) # id_col
        self.__hide_btn = gtk.Button(_("Hide/Unhide"))
        hbutbox.add(self.__hide_btn)
        self.__hide_btn.connect('clicked', self.__hide,
                                self.list, 4, 5) # list, id_col, hide_col

        if __debug__:
            self.__edit_btn = gtk.Button(_("Edit"))
            hbutbox.add(self.__edit_btn)
            self.__edit_btn.connect('clicked', self.__edit, self.list, 4) # id_col
            self.__load_btn = gtk.Button(_("Load"))
            hbutbox.add(self.__load_btn)
            self.__load_btn.connect('clicked', self.__load, self.list, 4) # id_col
        vbox_loaded.pack_start(hbutbox, expand=False, padding=5)
        notebook.append_page(vbox_loaded, 
                             tab_label=gtk.Label(_('Loaded Plugins')))

        #third page with method to install plugin
        install_page = gtk.VBox()
        scrolled_window = gtk.ScrolledWindow()
        self.addon_list = gtk.TreeView()
        # model: help_name, name, ptype, image, desc, use, rating, contact, download, url
        self.addon_model = gtk.ListStore(gobject.TYPE_STRING, 
                                         gobject.TYPE_STRING, 
                                         gobject.TYPE_STRING, 
                                         gobject.TYPE_STRING, 
                                         gobject.TYPE_STRING, 
                                         gobject.TYPE_STRING, 
                                         gobject.TYPE_STRING, 
                                         gobject.TYPE_STRING, 
                                         gobject.TYPE_STRING, 
                                         gobject.TYPE_STRING)
        self.addon_list.set_model(self.addon_model)
        self.addon_list.set_rules_hint(True)
        #self.addon_list.connect('button-press-event', self.button_press)
        col = gtk.TreeViewColumn(_('Addon Name'), gtk.CellRendererText(),
                                 text=1)
        col.set_sort_column_id(1)
        self.addon_list.append_column(col)
        col = gtk.TreeViewColumn(_('Type'), gtk.CellRendererText(),
                                 text=2)
        col.set_sort_column_id(2)
        self.addon_list.append_column(col)
        col = gtk.TreeViewColumn(_('Description'), gtk.CellRendererText(),
                                 text=4)
        col.set_sort_column_id(4)
        self.addon_list.append_column(col)
        self.addon_list.connect('cursor-changed', self.button_press_addon)

        install_row = gtk.HBox()
        install_row.pack_start(gtk.Label(_("Path to Addon:")), expand=False)
        self.install_addon_path = gtk.Entry()

        button = gtk.Button()
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_OPEN, gtk.ICON_SIZE_BUTTON)
        button.add(img)
        button.connect('clicked', self.__select_file)
        install_row.pack_start(self.install_addon_path, expand=True)
        install_row.pack_start(button, expand=False, fill=False)

        scrolled_window.add(self.addon_list)
        install_page.pack_start(scrolled_window)
        install_page.pack_start(install_row, expand=True, fill=False)

        hbutbox = gtk.HButtonBox()
        hbutbox.set_layout(gtk.BUTTONBOX_SPREAD)
        self.__add_btn = gtk.Button(_("Install Addon"))
        hbutbox.add(self.__add_btn)
        self.__add_btn.connect('clicked', self.__get_addon) 
        self.__add_all_btn = gtk.Button(_("Install All Addons"))
        hbutbox.add(self.__add_all_btn)
        self.__add_all_btn.connect('clicked', self.__get_all_addons) 
        self.__refresh_btn = gtk.Button(_("Refresh Addon List"))
        hbutbox.add(self.__refresh_btn)
        self.__refresh_btn.connect('clicked', self.__refresh_addon_list) 
        install_page.pack_start(hbutbox, expand=False, padding=5)
        notebook.append_page(install_page, 
                             tab_label=gtk.Label(_('Install Addons')))

        #add the notebook to the window
        self.window.vbox.add(notebook)
        
        if __debug__:
            # Only show the "Reload" button when in debug mode 
            # (without -O on the command line)
            self.__reload_btn = gtk.Button(_("Reload"))
            self.window.action_area.add(self.__reload_btn)
            self.__reload_btn.connect('clicked', self.__reload)
        
        #obtain hidden plugins from the pluginmanager
        self.hidden = self.__pmgr.get_hidden_plugin_ids()
        
        self.window.show_all()
        self.__populate_lists()

    def __refresh_addon_list(self, obj):
        """
        Reloads the addons from the wiki into the list.
        """
        import urllib
        URL = "%s%s" % (const.URL_WIKISTRING, const.WIKI_EXTRAPLUGINS_RAWDATA)
        fp = urllib.urlopen(URL)
        state = "read"
        rows = []
        row = []
        for line in fp.readlines():
            if line.startswith("|-") or line.startswith("|}"):
                if row != []:
                    rows.append(row)
                state = "row"
                row = []
            elif state == "row":
                if line.startswith("|"):
                    row.append(line[1:].strip())
            else:
                state = "read"
        fp.close()
        rows.sort(key=lambda row: (row[1], row[0]))
        self.addon_model.clear()
        # clear the config list:
        config.get('plugin.addonplugins')[:] = []
        for row in rows:
            try:
                # from wiki:
                help_name, ptype, image, desc, use, rating, contact, download = row
            except:
                continue
            help_url = _("Unknown Help URL")
            if help_name.startswith("[[") and help_name.endswith("]]"):
                name = help_name[2:-2]
                if "|" in name:
                    help_url, name = name.split("|", 1)
            elif help_name.startswith("[") and help_name.endswith("]"):
                name = help_name[1:-1]
                if " " in name:
                    help_url, name = name.split(" ", 1)
            else:
                name = help_name
            url = _("Unknown URL")
            if download.startswith("[[") and download.endswith("]]"):
                # Not directly possible to get the URL:
                url = download[2:-2]
                if "|" in url:
                    url, text = url.split("|", 1)
                # need to get a page that says where it is:
                fp = urllib.urlopen("%s%s%s" % (const.URL_WIKISTRING, url, 
                                                "&action=edit&externaledit=true&mode=file"))
                for line in fp:
                    if line.startswith("URL="):
                        junk, url = line.split("=", 1)
                        break
                fp.close()
            elif download.startswith("[") and download.endswith("]"):
                url = download[1:-1]
                if " " in url:
                    url, text = url.split(" ", 1)
            if (url.endswith(".zip") or 
                url.endswith(".ZIP") or 
                url.endswith(".tar.gz") or 
                url.endswith(".tgz")):
                # Then this is ok:
                self.addon_model.append(row=[help_name, name, ptype, image, desc, use, 
                                             rating, contact, download, url])
                config.get('plugin.addonplugins').append([help_name, name, ptype, image, desc, use, 
                                                          rating, contact, download, url])
        config.save()

    def __get_all_addons(self, obj):
        """
        Get all addons from the wiki and install them.
        """
        import urllib
        for row in self.addon_model:
            (help_name, name, ptype, image, desc, use, rating, contact, 
             download, url) = row
            messages = self.__load_addon_file(url)
            # FIXME: display messages
            for message in messages:
                print message
        self.__rebuild_load_list()
        self.__rebuild_reg_list()

    def __get_addon(self, obj):
        """
        Get an addon from the wiki or file system and install it.
        """
        path = self.install_addon_path.get_text()
        messages = self.__load_addon_file(path)
        # FIXME: display messages
        for message in messages:
            print message
        self.__rebuild_load_list()
        self.__rebuild_reg_list()

    def __load_addon_file(self, path):
        """
        Load an addon from a particular path (from URL or file system).
        """
        import urllib
        import tarfile
        import cStringIO
        if (path.startswith("http://") or
            path.startswith("https://") or
            path.startswith("ftp://")):
            fp = urllib.urlopen(path)
        else:
            fp = open(path)
        buffer = cStringIO.StringIO(fp.read())
        fp.close()
        # file_obj is either Zipfile or TarFile
        if path.endswith(".zip") or path.endswith(".ZIP"):
            file_obj = Zipfile(buffer)
        elif path.endswith(".tar.gz") or path.endswith(".tgz"):
            file_obj = tarfile.open(None, fileobj=buffer)
        else:
            return [("Error: unknown file type: '%s'") % path]
        # First, see what versions we have/are getting:
        good_gpr = set()
        messages = []
        for gpr_file in [name for name in file_obj.getnames() if name.endswith(".gpr.py")]:
            contents = file_obj.extractfile(gpr_file).read()
            # Put a fake register and _ function in environment:
            env = make_environment(register=register, _=lambda text: text)
            # clear out the result variable:
            globals()["register_results"] = []
            # evaluate the contents:
            try:
                exec(contents, env)
            except:
                messages += [_("Error in '%s' file: cannot load.") % gpr_file]
                continue
            # There can be multiple addons per gpr file:
            for results in globals()["register_results"]:
                for_gramps = results.get("for_gramps", None)
                if for_gramps:
                    vtup = version_str_to_tup(for_gramps, 2)
                    # Is it for the right version of gramps?
                    if vtup == const.VERSION_TUPLE[0:2]:
                        # If this version is not installed, or > installed, install it
                        good_gpr.add(gpr_file)
                        messages += [_("'%s' is for this version of Gramps.") % gpr_file]
                else:
                    # another register function doesn't have for_gramps
                    if gpr_file in good_gpr:
                        s.remove(gpr_file)
                    messages += [_("Error: missing for_gramps = '3.2' in '%s'...") % gpr_file]
        if len(good_gpr) > 0:
            # Now, install the ok ones
            file_obj.extractall(const.USER_PLUGINS)
            messages += [_("Installing '%s'...") % path]
            gpr_files = set([os.path.split(os.path.join(const.USER_PLUGINS, name))[0]
                             for name in good_gpr])
            for gpr_file in gpr_files:
                messages += [_("Registered '%s'") % gpr_file]
                self.__pmgr.reg_plugins(gpr_file)

        file_obj.close()
        return messages
    
    def __select_file(self, obj):
        """
        Select a file from the file system.
        """
        fcd = gtk.FileChooserDialog(_("Load Addon"), 
                                    buttons=(gtk.STOCK_CANCEL,
                                             gtk.RESPONSE_CANCEL,
                                             gtk.STOCK_OPEN,
                                             gtk.RESPONSE_OK))
        name = os.path.abspath(self.install_addon_path.get_text())
        fcd.set_current_name(name)
        if name:
            fcd.set_filename(name)

        status = fcd.run()
        if status == gtk.RESPONSE_OK:
            path = Utils.get_unicode_path(fcd.get_filename())
            if path:
                self.install_addon_path.set_text(path)
        fcd.destroy()

    def __populate_lists(self):
        """ Build the lists of plugins """
        self.__populate_load_list()
        self.__populate_reg_list()
        self.__populate_addon_list()

    def __populate_addon_list(self):
        """
        Build the list of addons from the config setting.
        """
        self.addon_model.clear()
        for row in config.get('plugin.addonplugins'):
            try:
                help_name, name, ptype, image, desc, use, rating, contact, download, url = row
            except:
                continue
            self.addon_model.append(row=[help_name, name, ptype, image, desc, use, 
                                         rating, contact, download, url])

    def __populate_load_list(self):
        """ Build list of loaded plugins"""
        fail_list = self.__pmgr.get_fail_list()
        
        for i in fail_list:
            # i = (filename, (exception-type, exception, traceback), pdata)
            err = i[1][0]
            pdata = i[2]
            hidden = pdata.id in self.hidden
            if hidden:
                hiddenstr = self.HIDDEN
            else:
                hiddenstr = self.AVAILABLE
            if err == Errors.UnavailableError:
                self.model.append(row=[
                    '<span color="blue">%s</span>' % _('Unavailable'),
                    i[0], str(i[1][1]), None, pdata.id, hiddenstr])
            else:
                self.model.append(row=[
                    '<span weight="bold" color="red">%s</span>' % _('Fail'),
                    i[0], str(i[1][1]), i[1], pdata.id, hiddenstr])

        success_list = self.__pmgr.get_success_list()
        for i in success_list:
            # i = (filename, module, pdata)
            pdata = i[2]
            modname = i[1].__name__
            descr = self.__pmgr.get_module_description(modname)
            hidden = pdata.id in self.hidden
            if hidden:
                hiddenstr = self.HIDDEN
            else:
                hiddenstr = self.AVAILABLE
            self.model.append(row=[
                '<span weight="bold" color="#267726">%s</span>' % _("OK"),
                i[0], descr, None, pdata.id, hiddenstr])
        
    def __populate_reg_list(self):
        """ Build list of registered plugins"""
        for (type, typestr) in PTYPE_STR.iteritems():
            for pdata in self.__preg.type_plugins(type):
                #  model: plugintype, hidden, pluginname, plugindescr, pluginid
                hidden = pdata.id in self.hidden
                if hidden:
                    hiddenstr = self.HIDDEN
                else:
                    hiddenstr = self.AVAILABLE
                self.model_reg.append(row=[
                    typestr, hiddenstr, pdata.name, pdata.description, 
                    pdata.id])

    def __rebuild_load_list(self):
        self.model.clear()
        self.__populate_load_list()
    
    def __rebuild_reg_list(self):
        self.model_reg.clear()
        self.__populate_reg_list()

    def button_press(self, obj, event):
        """ Callback function from the user clicking on a line """
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            model, node = self.selection.get_selected()
            data = model.get_value(node, 3)
            name = model.get_value(node, 1)
            if data:
                PluginTrace(self.uistate, [], data, name)
                
    def button_press_reg(self, obj, event):
        """ Callback function from the user clicking on a line in reg plugin
        """
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.__info(obj, self.list_reg, 4)
    
    def button_press_addon(self, obj):
        """ Callback function from the user clicking on a line in reg plugin
        """
        import urllib
        selection = self.addon_list.get_selection()
        model, node = selection.get_selected()
        if node:
            url = model.get_value(node, 9)
            self.install_addon_path.set_text(url)
    
    def build_menu_names(self, obj):
        return (self.title, "")
    
    def __reload(self, obj):
        """ Callback function from the "Reload" button """
        self.__pmgr.reload_plugins()
        self.__rebuild_load_list()
        self.__rebuild_reg_list()
    
    def __info(self, obj, list_obj, id_col):
        """ Callback function from the "Info" button
        """
        selection = list_obj.get_selection()
        model, node = selection.get_selected()
        if not node:
            return
        id = model.get_value(node, id_col)
        pdata = self.__preg.get_plugin(id)
        typestr = pdata.ptype
        auth = ' - '.join(pdata.authors)
        email = ' - '.join(pdata.authors_email)
        if len(auth) > 60: 
            auth = auth[:60] + '...'
        if len(email) > 60: 
            email = email[:60] + '...'
        if pdata:
            infotxt = """Plugin name: %(name)s [%(typestr)s]

Description:  %(descr)s
Authors:  %(authors)s
Email:  %(email)s
Filename:  %(fname)s
Location: %(fpath)s
""" % {
            'name': pdata.name,
            'typestr': typestr,
            'descr': pdata.description,
            'authors': auth,
            'email': email,
            'fname': pdata.fname,
            'fpath': pdata.fpath,
            }
            InfoDialog('Detailed Info', infotxt, parent=self.window)
    
    def __hide(self, obj, list_obj, id_col, hide_col):
        """ Callback function from the "Hide" button
        """
        selection = list_obj.get_selection()
        model, node = selection.get_selected()
        if not node:
            return
        id = model.get_value(node, id_col)
        if id in self.hidden:
            #unhide
            self.hidden.remove(id)
            model.set_value(node, hide_col, self.AVAILABLE)
            self.__pmgr.unhide_plugin(id)
        else:
            #hide
            self.hidden.add(id)
            model.set_value(node, hide_col, self.HIDDEN)
            self.__pmgr.hide_plugin(id)
    
    def __load(self, obj, list_obj, id_col):
        """ Callback function from the "Load" button
        """
        selection = list_obj.get_selection()
        model, node = selection.get_selected()
        if not node:
            return
        id = model.get_value(node, id_col)
        pdata = self.__preg.get_plugin(id)
        self.__pmgr.load_plugin(pdata)
        self.__rebuild_load_list()

    def __edit(self, obj, list_obj, id_col):
        """ Callback function from the "Load" button
        """
        selection = list_obj.get_selection()
        model, node = selection.get_selected()
        if not node:
            return
        id = model.get_value(node, id_col)
        pdata = self.__preg.get_plugin(id)
        open_file_with_default_application(
            os.path.join(pdata.fpath, pdata.fname)
            )

#-------------------------------------------------------------------------
#
# Details for an individual plugin that failed
#
#-------------------------------------------------------------------------
class PluginTrace(ManagedWindow.ManagedWindow):
    """Displays a dialog showing the status of loaded plugins"""
    
    def __init__(self, uistate, track, data, name):
        self.name = name
        title = "%s: %s" % (_("Plugin Error"), name)
        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)

        self.set_window(gtk.Dialog("", uistate.window,
                                   gtk.DIALOG_DESTROY_WITH_PARENT,
                                   (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)),
                        None, title)
        self.window.set_size_request(600, 400)
        self.window.connect('response', self.close)
        
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.text = gtk.TextView()
        scrolled_window.add(self.text)
        self.text.get_buffer().set_text(
            "".join(traceback.format_exception(data[0],data[1],data[2])))

        self.window.vbox.add(scrolled_window)
        self.window.show_all()

    def build_menu_names(self, obj):
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
        self.set_window(window, None, self.get_title())
        #self.window.set_has_separator(False)

        #self.window.connect('response', self.close)
        self.cancel = self.window.add_button(gtk.STOCK_CLOSE,
                                             gtk.RESPONSE_CANCEL)
        self.cancel.connect('clicked', self.close)

        self.ok = self.window.add_button(gtk.STOCK_EXECUTE, gtk.RESPONSE_OK)
        self.ok.connect('clicked', self.on_ok_clicked)

        self.window.set_default_size(600, -1)

        # Set up and run the dialog.  These calls are not in top down
        # order when looking at the dialog box as there is some
        # interaction between the various frames.

        self.setup_title()
        self.setup_header()
        #self.tbl = gtk.Table(4, 4, False)
        #self.tbl.set_col_spacings(12)
        #self.tbl.set_row_spacings(6)
        #self.tbl.set_border_width(6)
        #self.col = 0
        #self.window.vbox.add(self.tbl)

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
    def on_cancel(self, *obj):
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
                _window = view.get_window(gtk.TEXT_WINDOW_TEXT)
                _window.set_cursor(self.link_cursor)
                return False # handle event further, if necessary
        view.get_window(gtk.TEXT_WINDOW_TEXT).set_cursor(self.standard_cursor)
        return False # handle event further, if necessary

    def on_button_press(self, view, event):
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
        self.results_text.scroll_to_mark(mark, 0)
        buffer.insert_at_cursor(text)
        buffer.delete_mark_by_name("end")        

    def write_to_page(self, page, text):
        buffer = page.get_buffer()
        mark = buffer.create_mark("end", buffer.get_end_iter())
        self.results_text.scroll_to_mark(mark, 0)
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
        from gui.utils import ProgressMeter
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
        self.window.vbox.pack_start(label, False, False, self.border_pad)

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
        return self.results_text

    def add_page(self, frame_name="Help"):
        if frame_name not in self.frames:
            text = gtk.TextView() 
            text.set_wrap_mode(gtk.WRAP_WORD)
            window = gtk.ScrolledWindow()
            window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            window.add(text)
            window.set_shadow_type(gtk.SHADOW_IN)
            self.frames[frame_name] = [[frame_name, window]] 
            self.frame_names.append(frame_name)
            l = gtk.Label("<b>%s</b>" % _(frame_name))
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
            table = gtk.Table(3, len(flist))
            table.set_col_spacings(12)
            table.set_row_spacings(6)
            table.set_border_width(6)
            l = gtk.Label("<b>%s</b>" % key)
            l.set_use_markup(True)
            self.notebook.append_page(table, l)
            row = 0
            for (text, widget) in flist:
                if text:
                    text_widget = gtk.Label('%s:' % text)
                    text_widget.set_alignment(0.0, 0.5)
                    table.attach(text_widget, 1, 2, row, row+1,
                                 gtk.SHRINK|gtk.FILL, gtk.SHRINK)
                    table.attach(widget, 2, 3, row, row+1,
                                 yoptions=gtk.SHRINK)
                else:
                    table.attach(widget, 2, 3, row, row+1,
                                 yoptions=gtk.SHRINK)
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
        self.options.add_user_options(self)

    def build_menu_names(self, obj):
        return (_('Main window'), self.get_title())



class ToolManagedWindowBatch(Tool.BatchTool, ToolManagedWindowBase):
    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        # This constructor will ask a question, set self.fail:
        self.dbstate = dbstate
        self.uistate = uistate
        Tool.BatchTool.__init__(self, dbstate, options_class, name)
        if not self.fail:
            ToolManagedWindowBase.__init__(self, dbstate, uistate, 
                                           options_class, name, callback)

class ToolManagedWindow(Tool.Tool, ToolManagedWindowBase):
    def __init__(self, dbstate, uistate, options_class, name, callback=None):
        self.dbstate = dbstate
        self.uistate = uistate
        Tool.Tool.__init__(self, dbstate, options_class, name)
        ToolManagedWindowBase.__init__(self, dbstate, uistate, options_class, 
                                       name, callback)
