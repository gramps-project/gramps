#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Raphael Ackermann
# Copyright (C) 2010       Benny Malengier
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2017       Paul Culley <paulr2787_at_gmail.com>
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
""" This module implements the Addon manager """
#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import sys
import os
import traceback
import logging
from operator import itemgetter
import shutil
#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import GObject  # pylint: disable=import-error
from gi.repository import Gdk      # pylint: disable=import-error
from gi.repository import Gtk      # pylint: disable=import-error

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.plug.utils import available_updates
from gramps.gen.config import config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.const import URL_MANUAL_PAGE, VERSION_DIR
from gramps.gen.utils.configmanager import safe_eval
from gramps.gen.plug import PluginRegister, PTYPE_STR, VIEW, GRAMPLET
from gramps.gen.plug import load_addon_file, version_str_to_tup
from gramps.cli.grampscli import CLIManager
from .managedwindow import ManagedWindow
from .pluginmanager import GuiPluginManager
from .listmodel import ListModel, NOSORT, TOGGLE
from .display import display_help
from .utils import open_file_with_default_application
from .configure import ConfigureDialog
from .widgets import BasicLabel
from .dialog import OkDialog, QuestionDialog2
from .glade import Glade
from .widgets.progressdialog import (LongOpStatus, ProgressMonitor,
                                     GtkProgressDialog)
#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
LOG = logging.getLogger(".gui.plug")

# some static data, available across instantiations
static = sys.modules[__name__]
static.check_done = False
static.panel = 0

_ = glocale.translation.gettext
ngettext = glocale.translation.ngettext  # else "nearby" comments are ignored

RELOAD = 777    # A custom Gtk response_type for the Reload button
IGNORE = 888    # A custom Gtk response_type for the checkboxes

# status bit mask values
INSTALLED = 1   # INSTALLED, AVAILABLE, and BUILTIN are mutually exclusive
AVAILABLE = 2   # set = available
BUILTIN = 4     # set = builtin
HIDDEN = 8      # set = hidden
UPDATE = 16     # set = Update available

# addons model column numbers
R_TYPE = 0
R_STAT_S = 1
R_NAME = 2
R_DESC = 3
R_ID = 4
R_STAT = 5

# the following removes a class of pylint errors that are not properly ignored;
# supposed to be fixed in pylint v1.7
# pylint: disable=unused-argument


#-------------------------------------------------------------------------
#
# AddonManagerPreferences
#
#-------------------------------------------------------------------------
class AddonManager(ConfigureDialog):
    """ Addon manager related preferences and loading controls """

    WIKI_HELP_PAGE = _('%s_Addons') % URL_MANUAL_PAGE

    def __init__(self, uistate, dbstate):
        self._hide_builtins = None
        self._hide_hidden = None
        page_funcs = (self.add_addoncheckupdates_panel,
                      self.registered_addons_panel)
        self.title = _("Addon Manager")
        ConfigureDialog.__init__(self, uistate, dbstate, page_funcs,
                                 AddonManager, config,
                                 dialogtitle=self.title)
        self._pmgr = GuiPluginManager.get_instance()
        self._preg = PluginRegister.get_instance()
        #obtain hidden addons from the pluginmanager
        self.hidden = self._pmgr.get_hidden_plugin_ids()
        self.setup_configs('interface.pluginstatus', 750, 400)

        if __debug__:
            # Only show the "Reload" button when in debug mode
            # (without -O on the command line)
            reload_btn = self.window.add_button(  # pylint: disable=no-member
                _("Reload"), RELOAD)
            btn_box = reload_btn.get_parent()
            btn_box.set_child_non_homogeneous(reload_btn, True)
        self.panel.set_current_page(static.panel)
        self.page_changed(None, None, static.panel)
        self.__populate_reg_list()
        self.restart_needed = False
        self.panel.connect('switch-page', self.page_changed)

    def done(self, dialog, response_id):
        if response_id == RELOAD:
            self.__reload(dialog)
            return
        elif response_id == IGNORE:
            return
        else:   # response_id == CLOSE or response_id == DELETE_EVENT
            if self.restart_needed:
                OkDialog(_("Restart..."),
                         _("Please Restart Gramps so that your addon changes "
                           "can be safely completed."),
                         parent=self.window)
            self.close(dialog)

    def __reload(self, _obj):
        """ Callback function from the "Reload" button """
        self._pmgr.reload_plugins()
        self.__rebuild_reg_list('0')

    def page_changed(self, _notebook, _page, page_num):
        """ The tab is changed """
        static.panel = page_num

    def __hide_check(self, obj):
        """ Callback from Hide hidden checkbox """
        self._hide_hidden = obj.get_active()
        config.set('behavior.do-not-show-hidden-addons',
                   bool(self._hide_hidden))
        self.__rebuild_reg_list('0', rescan=False)

    def __hide_builtins(self, obj):
        """ Callback from Hide builtins checkbox """
        self._hide_builtins = obj.get_active()
        config.set('behavior.do-not-show-builtins',
                   bool(self._hide_builtins))
        self.__rebuild_reg_list('0', rescan=False)

    def __info(self, _obj, list_obj):
        """ Callback function from the "Info" button
        """
        model, node = list_obj.get_selection().get_selected()
        if not node:
            return
        pid = model.get_value(node, R_ID)
        pdata = self._preg.get_plugin(pid)
        if pdata:
            name = pdata.name
            typestr = PTYPE_STR[pdata.ptype]
            desc = pdata.description
            vers = pdata.version
            auth = ' - '.join(pdata.authors)
            email = ' - '.join(pdata.authors_email)
            fname = pdata.fname
            fpath = pdata.fpath
        else:
            for addon in self.addons:
                if addon['i'] == pid:
                    name = addon['n']
                    typestr = addon['t']
                    desc = addon['d']
                    vers = addon['v']
                    auth = ''
                    email = ''
                    fname = addon['z']
                    fpath = ''
                    break

        if len(auth) > 60:
            auth = auth[:60] + '...'
        if len(email) > 60:
            email = email[:60] + '...'
        infotxt = (
            "%(plugnam)s: %(name)s [%(typestr)s]\n\n"
            "%(plug_id)s: %(id)s\n"
            "%(plugdes)s: %(descr)s\n%(plugver)s: %(version)s\n"
            "%(plugaut)s: %(authors)s\n%(plugmel)s: %(email)s\n"
            "%(plugfil)s: %(fname)s\n%(plugpat)s: %(fpath)s\n\n" % {
                'id': pid,
                'name': name,
                'typestr': typestr,
                'descr': desc,
                'version': vers,
                'authors': auth,
                'email': email,
                'fname': fname,
                'fpath': fpath,
                'plug_id': _("Id"),
                'plugnam': _("Plugin name"),
                'plugdes': _("Description"),
                'plugver': _("Version"),
                'plugaut': _("Authors"),
                'plugmel': _("Email"),
                'plugfil': _("Filename"),
                'plugpat': _("Location")})
        success_list = self._pmgr.get_success_list()
        if pdata:
            for i in success_list:
                if pdata.id == i[2].id:
                    infotxt += _('Loaded') + ' '
                    break
        if pid in self.hidden:
            infotxt += _('Hidden')
        fail_list = self._pmgr.get_fail_list()
        for i in fail_list:
            # i = (filename, (exception-type, exception, traceback), pdata)
            if pdata == i[2]:
                infotxt += '\n\n' + _('Failed') + '\n\n' + str(i[1][0]) + \
                    '\n' + str(i[1][1]) + '\n' + ''.join(
                        traceback.format_exception(i[1][0], i[1][1], i[1][2]))
                break
        PluginInfo(self.uistate, self.track, infotxt, name)

    def __hide(self, _obj, list_obj):
        """ Callback function from the "Hide" button
        """
        selection = list_obj.get_selection()
        model, node = selection.get_selected()
        if not node:
            return
        pid = model.get_value(node, R_ID)
        status = model.get_value(node, R_STAT)
        status_str = model.get_value(node, R_STAT_S)
        if pid in self.hidden:
            #unhide
            self.hidden.remove(pid)
            self._pmgr.unhide_plugin(pid)
            status = model.get_value(node, R_STAT)
            status_str = status_str.replace("<s>", '').replace("</s>", '')
            status &= ~ HIDDEN
            model.set_value(node, R_STAT, status)
            self._hide_btn.set_label(_("Hide"))
        else:
            #hide
            self.hidden.add(pid)
            self._pmgr.hide_plugin(pid)
            if self._hide_hidden:
                model.remove(node)
                return
            status |= HIDDEN
            status_str = "<s>%s</s>" % status_str
            self._hide_btn.set_label(_("Unhide"))
        model.set_value(node, R_STAT, status)
        model.set_value(node, R_STAT_S, status_str)

    def __load(self, _obj, list_obj):
        """ Callback function from the "Load" button
        """
        selection = list_obj.get_selection()
        model, node = selection.get_selected()
        if not node:
            return
        idv = model.get_value(node, R_ID)
        pdata = self._preg.get_plugin(idv)
        if self._pmgr.load_plugin(pdata):
            self._load_btn.set_sensitive(False)
        else:
            path = model.get_path(node)
            self.__rebuild_reg_list(path, rescan=False)

    def __edit(self, _obj, list_obj):
        """ Callback function from the "Edit" button
        """
        selection = list_obj.get_selection()
        model, node = selection.get_selected()
        if not node:
            return
        pid = model.get_value(node, R_ID)
        pdata = self._preg.get_plugin(pid)
        if pdata.fpath and pdata.fname:
            open_file_with_default_application(
                os.path.join(pdata.fpath, pdata.fname),
                self.uistate)

    def __install(self, _obj, _list_obj):
        """ Callback function from the "Install" button
        """
        model, node = self._selection_reg.get_selected()
        if not node:
            return
        path = model.get_path(node)
        pid = model.get_value(node, R_ID)
        status = model.get_value(node, R_STAT)
        if (status & INSTALLED) and not (status & UPDATE):
            self.__uninstall(pid, path)
            return
        for addon in self.addons:
            if addon['i'] == pid:
                name = addon['n']
                fname = addon['z']
        url = "%s/download/%s" % (config.get("behavior.addons-url"), fname)
        load_ok = load_addon_file(url, callback=LOG.debug)
        if not load_ok:
            OkDialog(_("Installation Errors"),
                     _("The following addons had errors: ") +
                     name,
                     parent=self.window)
            return
        self.__rebuild_reg_list(path)
        pdata = self._pmgr.get_plugin(pid)
        if (status & UPDATE) and (pdata.ptype == VIEW or
                                  pdata.ptype == GRAMPLET):
            self.restart_needed = True

    def __uninstall(self, pid, path):
        """ Uninstall the plugin """
        pdata = self._pmgr.get_plugin(pid)
        try:
            shutil.rmtree(pdata.fpath)
            self.__rebuild_reg_list(path)
            self.restart_needed = True
        except:  # pylint: disable=bare-except
            OkDialog(_("Error"),
                     _("Error removing the '%s' directory, The uninstall may "
                       "have failed") % pdata.fpath,
                     parent=self.window)

    def _check_for_type_changed(self, obj):
        active = obj.get_active()
        if active == 0:  # update
            config.set('behavior.check-for-addon-update-types', ["update"])
        elif active == 1:  # update
            config.set('behavior.check-for-addon-update-types', ["new"])
        elif active == 2:  # update
            config.set('behavior.check-for-addon-update-types',
                       ["update", "new"])

    def _toggle_hide_previous_addons(self, obj):
        active = obj.get_active()
        config.set('behavior.do-not-show-previously-seen-addon-updates',
                   bool(active))

    def _check_for_updates_changed(self, obj):
        active = obj.get_active()
        config.set('behavior.check-for-addon-updates', active)

    def add_addoncheckupdates_panel(self, _configdialog):
        """ This implements the gui portion of the check and preferences panel
        """
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        grid.set_column_homogeneous(True)

        current_line = 0
        label = _(
            '<b>Third-party Addons, unless stated, are not officially part of '
            'Gramps.</b>\n\n'
            'Please use carefully on Family Trees that are backed up.\n\n'
            'Note: Some Addons have prerequisites that need to be installed '
            'before they can be used.\n\n')
        text = Gtk.Label(hexpand=False)
        text.set_line_wrap(True)
        text.set_halign(Gtk.Align.CENTER)
        text.set_markup(label)
        grid.attach(text, 1, current_line, 2, 1)

        current_line += 1
        button = Gtk.Button(label=_("Webpage Help on Addons"),
                            halign=Gtk.Align.CENTER, hexpand=False)
        button.connect("clicked", self._web_help)
        grid.attach(button, 1, current_line, 1, 1)
        button = Gtk.Button(label=_("Check for updated addons now"),
                            halign=Gtk.Align.CENTER, hexpand=False)
        button.connect("clicked", self._check_for_updates)
        grid.attach(button, 2, current_line, 1, 1)

        current_line += 1
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        grid.attach(sep, 1, current_line, 2, 1)

        current_line += 1
        label = _(
            '\n<b><big>Preferences for checking on Third-party Addon '
            'updates.</big></b>\n\n')
        text = Gtk.Label(hexpand=False)
        text.set_line_wrap(True)
        text.set_halign(Gtk.Align.CENTER)
        text.set_markup(label)
        grid.attach(text, 1, current_line, 2, 1)

        current_line += 1
        # Check for addon updates:
        obox = Gtk.ComboBoxText()
        formats = [_("Never"),
                   _("Once a month"),
                   _("Once a week"),
                   _("Once a day"),
                   _("Always"), ]
        for i in formats:
            obox.append_text(i)
        active = config.get('behavior.check-for-addon-updates')
        obox.set_active(active)
        obox.connect('changed', self._check_for_updates_changed)
        lwidget = BasicLabel("%s: " % _('Check for addon updates'))
        grid.attach(lwidget, 1, current_line, 1, 1)
        grid.attach(obox, 2, current_line, 1, 1)

        current_line += 1
        whattype_box = Gtk.ComboBoxText()
        formats = [_("Updated addons only"),
                   _("New addons only"),
                   _("New and updated addons"), ]
        for i in formats:
            whattype_box.append_text(i)
        whattype = config.get('behavior.check-for-addon-update-types')
        if "new" in whattype and "update" in whattype:
            whattype_box.set_active(2)
        elif "new" in whattype:
            whattype_box.set_active(1)
        elif "update" in whattype:
            whattype_box.set_active(0)
        whattype_box.connect('changed', self._check_for_type_changed)
        lwidget = BasicLabel("%s: " % _('What to check'))
        grid.attach(lwidget, 1, current_line, 1, 1)
        grid.attach(whattype_box, 2, current_line, 1, 1)

        current_line += 1
        self.add_entry(grid, _('Where to check'), current_line,
                       'behavior.addons-url', col_attach=1)

        current_line += 1
        checkbutton = Gtk.CheckButton(
            label=_("Do not ask about previously notified addons"))
        checkbutton.set_active(config.get(
            'behavior.do-not-show-previously-seen-addon-updates'))
        checkbutton.connect("toggled", self._toggle_hide_previous_addons)
        grid.attach(checkbutton, 1, current_line, 2, 1)

        return _('Updates'), grid

    def registered_addons_panel(self, _configdialog):
        """ This implements the gui portion of the Addons panel """
        vbox_reg = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scrolled_window_reg = Gtk.ScrolledWindow()
        self._list_reg = Gtk.TreeView()
        self._list_reg.set_grid_lines(Gtk.TreeViewGridLines.HORIZONTAL)
        #  model: plugintype, hidden, pluginname, plugindescr, pluginid
        self._model_reg = Gtk.ListStore(
            GObject.TYPE_STRING, GObject.TYPE_STRING, GObject.TYPE_STRING,
            GObject.TYPE_STRING, GObject.TYPE_STRING, int)
        self._selection_reg = self._list_reg.get_selection()
        self._list_reg.set_model(self._model_reg)
        self._list_reg.connect('button-press-event', self.button_press_reg)
        self._cursor_hndlr = self._selection_reg.connect('changed',
                                                         self._cursor_changed)
        col0_reg = Gtk.TreeViewColumn(
            title=_('Type'), cell_renderer=Gtk.CellRendererText(),
            text=R_TYPE)
        col0_reg.set_sort_column_id(R_TYPE)
        col0_reg.set_resizable(True)
        self._list_reg.append_column(col0_reg)
        col = Gtk.TreeViewColumn(
            title=_('Status'),
            cell_renderer=Gtk.CellRendererText(wrap_mode=2, wrap_width=60),
            markup=R_STAT_S)
        col0_reg.set_resizable(True)
        col.set_sort_column_id(R_STAT_S)
        self._list_reg.append_column(col)
        col2_reg = Gtk.TreeViewColumn(
            title=_('Name'),
            cell_renderer=Gtk.CellRendererText(wrap_mode=2, wrap_width=150),
            markup=R_NAME)
        col2_reg.set_sort_column_id(R_NAME)
        col2_reg.set_resizable(True)
        self._list_reg.append_column(col2_reg)
        col = Gtk.TreeViewColumn(
            title=_('Description'),
            cell_renderer=Gtk.CellRendererText(wrap_mode=2, wrap_width=400),
            markup=R_DESC)
        col.set_sort_column_id(R_DESC)
        col.set_resizable(True)
        self._list_reg.append_column(col)
        self._list_reg.set_search_column(2)

        scrolled_window_reg.add(self._list_reg)
        vbox_reg.pack_start(scrolled_window_reg, True, True, 0)
        # panel button box
        hbutbox = Gtk.ButtonBox()
        hbutbox.set_layout(Gtk.ButtonBoxStyle.SPREAD)

        __info_btn = Gtk.Button(label=_("Info"))
        hbutbox.add(__info_btn)
        __info_btn.connect('clicked', self.__info, self._list_reg)
        self._hide_btn = Gtk.Button(label=_("Hide"))
        hbutbox.add(self._hide_btn)
        self._hide_btn.connect('clicked', self.__hide, self._list_reg)
        self._install_btn = Gtk.Button(label=_("Install"))
        hbutbox.add(self._install_btn)
        self._install_btn.connect('clicked', self.__install, self._list_reg)
        self._edit_btn = Gtk.Button(label=_("Edit"))
        self._edit_btn.connect('clicked', self.__edit, self._list_reg)
        self._load_btn = Gtk.Button(label=_("Load"))
        self._load_btn.connect('clicked', self.__load, self._list_reg)
        if __debug__:
            hbutbox.add(self._edit_btn)
            hbutbox.add(self._load_btn)
        vbox_reg.pack_start(hbutbox, False, False, 0)
        # checkbox row
        hbutbox = Gtk.ButtonBox()
        hbutbox.set_layout(Gtk.ButtonBoxStyle.SPREAD)

        _hide_check_btn = Gtk.CheckButton.new_with_label(
            _("Remove hidden items from view"))
        hbutbox.add(_hide_check_btn)
        self._hide_hidden = config.get('behavior.do-not-show-hidden-addons')
        _hide_check_btn.set_active(self._hide_hidden)
        _hide_check_btn.connect('clicked', self.__hide_check)

        _hide_builtin_btn = Gtk.CheckButton.new_with_label(
            _("Remove Built-in items from view"))
        hbutbox.add(_hide_builtin_btn)
        self._hide_builtins = config.get('behavior.do-not-show-builtins')
        _hide_builtin_btn.set_active(self._hide_builtins)
        _hide_builtin_btn.connect('clicked', self.__hide_builtins)

        vbox_reg.pack_start(hbutbox, False, False, 0)

        return _('Addons'), vbox_reg

    def button_press_reg(self, obj, event):
        """ Callback function from the user clicking on a line in reg plugin
        """
        # pylint: disable=protected-access
        if event.type == Gdk.EventType._2BUTTON_PRESS and event.button == 1:
            self.__info(obj, self._list_reg)

    def __rebuild_reg_list(self, path=None, rescan=True):
        self._selection_reg.handler_block(self._cursor_hndlr)
        self._model_reg.clear()
        if rescan:
            CLIManager.do_reg_plugins(self, self.dbstate, self.uistate,
                                      rescan=True)
        self.__populate_reg_list()
        self._selection_reg.handler_unblock(self._cursor_hndlr)
        if not path or int(str(path)) >= len(self._model_reg):
            path = '0'
        self._selection_reg.select_path(path)
        if len(self._model_reg):
            self._list_reg.scroll_to_cell(path, None, True, 0.5, 0)

    def _cursor_changed(self, obj):
        model, node = obj.get_selected()
        if not node:
            return
        status = model.get_value(node, R_STAT)
        pid = model.get_value(node, R_ID)
        if (status & (INSTALLED | BUILTIN)) and (
                VIEW == self._pmgr.get_plugin(pid).ptype):
            self._hide_btn.set_sensitive(False)
        else:
            self._hide_btn.set_sensitive(True)
            if status & HIDDEN:
                self._hide_btn.set_label(_("Unhide"))
            else:
                self._hide_btn.set_label(_("Hide"))
        show_load = False
        if status & (INSTALLED | BUILTIN):
            show_load = True
            self._edit_btn.set_sensitive(True)
            success_list = self._pmgr.get_success_list()
            for i in success_list:
                if pid == i[2].id:
                    show_load = False
                    break
        else:
            self._edit_btn.set_sensitive(False)
        self._load_btn.set_sensitive(show_load)
        if status & (AVAILABLE | UPDATE):
            self._install_btn.set_label(_("Install"))
            self._install_btn.set_sensitive(True)
        elif status & INSTALLED:
            self._install_btn.set_label(_("Uninstall"))
            self._install_btn.set_sensitive(True)
        else:
            self._install_btn.set_sensitive(False)

    def _check_for_updates(self, _button):
        """ handle the check for updates button """
        try:
            addon_update_list = available_updates()
        except:  # pylint: disable=bare-except
            OkDialog(_("Checking Addons Failed"),
                     _("The addon repository appears to be unavailable. "
                       "Please try again later."),
                     parent=self.window)
            return

        if len(addon_update_list) > 0:
            rescan = UpdateAddons(self.uistate, self.track,
                                  addon_update_list).rescan
            self.__rebuild_reg_list(rescan=rescan)
        else:
            check_types = config.get('behavior.check-for-addon-update-types')
            OkDialog(
                _("There are no available addons of this type"),
                _("Checked for '%s'") % _("' and '").join(
                    [_(t) for t in check_types]),
                parent=self.window)

    def _web_help(self, _button):
        display_help(self.WIKI_HELP_PAGE)

    def __populate_reg_list(self):
        """ Build list of addons"""
        self.addons = []
        new_addons_file = os.path.join(VERSION_DIR, "new_addons.txt")
        if not os.path.isfile(new_addons_file) and not static.check_done:
            if QuestionDialog2(self.title,
                               _("3rd party addons are not shown until the "
                                 "addons update list is downloaded.  Would "
                                 "you like to check for updated addons now?"),
                               _("Yes"), _("No"),
                               parent=self.window).run():
                self._check_for_updates(None)
            else:
                static.check_done = True
        try:
            with open(new_addons_file,
                      encoding='utf-8') as filep:
                for line in filep:
                    try:
                        plugin_dict = safe_eval(line)
                        if not isinstance(plugin_dict, dict):
                            raise TypeError("Line with addon metadata is not "
                                            "a dictionary")
                    except:  # pylint: disable=bare-except
                        LOG.warning("Skipped a line in the addon listing: " +
                                    str(line))
                        continue
                    self.addons.append(plugin_dict)
        except FileNotFoundError:
            pass
        except Exception as err:  # pylint: disable=broad-except
            LOG.warning("Failed to open addon status file: %s", err)

        addons = []
        updateable = []
        for plugin_dict in self.addons:
            pid = plugin_dict["i"]
            plugin = self._pmgr.get_plugin(pid)
            if plugin:  # check for an already registered addon
                LOG.debug("Comparing %s > %s",
                          version_str_to_tup(plugin_dict["v"], 3),
                          version_str_to_tup(plugin.version, 3))
                # Check for a update
                if (version_str_to_tup(plugin_dict["v"], 3) >
                        version_str_to_tup(plugin.version, 3)):
                    LOG.debug("Update for '%s'...", plugin_dict["z"])
                    updateable.append(pid)
                else:  # current plugin is up to date.
                    LOG.debug("   '%s' is up to date", plugin_dict["n"])
            else:  # new addon
                LOG.debug("   '%s' is not installed", plugin_dict["n"])
                hidden = pid in self.hidden
                status_str = _("3rd Party")
                status = AVAILABLE
                if hidden:
                    status_str = "<s>%s</s>" % status_str
                    status |= HIDDEN
                row = [plugin_dict["t"], status_str, plugin_dict["n"],
                       plugin_dict["d"], plugin_dict["i"], status]
                addons.append(row)

        fail_list = self._pmgr.get_fail_list()
        for (_type, typestr) in PTYPE_STR.items():
            for pdata in self._preg.type_plugins(_type):
                #  model: plugintype, hidden, pluginname, plugindescr, pluginid
                if 'gramps/plugins' in pdata.fpath.replace('\\', '/'):
                    status_str = _("Built-in")
                    status = BUILTIN
                    if self._hide_builtins:
                        continue
                else:
                    status_str = _("3rd Party Installed")
                    status = INSTALLED
                # i = (filename, (exception-type, exception, traceback), pdata)
                for i in fail_list:
                    if pdata == i[2]:
                        status_str += ', ' + '<span color="red">%s</span>' % \
                            _("Failed")
                        break
                if pdata.id in updateable:
                    status_str += ', ' + _("Update Available")
                    status |= UPDATE
                hidden = pdata.id in self.hidden
                if hidden:
                    status_str = "<s>%s</s>" % status_str
                    status |= HIDDEN
                addons.append([typestr, status_str, pdata.name,
                               pdata.description, pdata.id, status])
        for row in sorted(addons, key=itemgetter(R_TYPE, R_NAME)):
            if not self._hide_hidden or (row[R_ID] not in self.hidden):
                self._model_reg.append(row)

    def build_menu_names(self, obj):
        return (self.title, ' ')


#-------------------------------------------------------------------------
#
# Details for an individual plugin
#
#-------------------------------------------------------------------------
class PluginInfo(ManagedWindow):
    """Displays a dialog showing the status of addons"""

    def __init__(self, uistate, track, data, name):
        self.name = name
        title = _("%(str1)s: %(str2)s") % {'str1': _("Detailed Info"),
                                           'str2': name}
        ManagedWindow.__init__(self, uistate, track, self)

        dlg = Gtk.Dialog(title="", transient_for=uistate.window,
                         destroy_with_parent=True)
        dlg.add_button(_('_Close'), Gtk.ResponseType.CLOSE)
        self.set_window(dlg, None, title)
        self.setup_configs('interface.plugininfo', 720, 520)
        self.window.connect('response',  # pylint: disable=no-member
                            self.close)

        scrolled_window = Gtk.ScrolledWindow(expand=True)
#         scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC,
#                                    Gtk.PolicyType.AUTOMATIC)
        self.text = Gtk.TextView()
        scrolled_window.add(self.text)
        self.text.get_buffer().set_text(data)

        # pylint: disable=no-member
        self.window.get_content_area().add(scrolled_window)
        self.show()

    def build_menu_names(self, obj):
        return (self.name, None)


#-------------------------------------------------------------------------
#
# UpdateAddons
#
#-------------------------------------------------------------------------
class UpdateAddons(ManagedWindow):
    """ This displays the available addons (all, new, or updated) after the
    'check for updates' has been run
    """
    def __init__(self, uistate, track, addon_update_list):
        self.title = _('Available Gramps Updates for Addons')

        ManagedWindow.__init__(self, uistate, track, self, modal=True)
        glade = Glade("updateaddons.glade")
        self.set_window(glade.toplevel, None, None)
        self.window.set_title(self.title)  # pylint: disable=no-member
        self.setup_configs("interface.updateaddons", 750, 400)
        self.rescan = False

        apply_button = glade.get_object('apply')
        cancel_button = glade.get_object('cancel')
        select_all = glade.get_object('select_all')
        select_all.connect("clicked", self.select_all_clicked)
        select_none = glade.get_object('select_none')
        select_none.connect("clicked", self.select_none_clicked)
        apply_button.connect("clicked", self.install_addons)
        cancel_button.connect("clicked", self.close)

        self.list = ListModel(
            glade.get_object("list"), [
                # name, click?, width, toggle
                {"name": _('Select'),
                 "width": 60,
                 "type": TOGGLE,
                 "visible_col": 6,
                 "editable": True},                         # 0 selected?
                (_('Type'), 1, 180),                        # 1 new gramplet
                (_('Name'), 2, 200),                        # 2 name (version)
                (_('Description'), 3, 200),                 # 3 description
                ('', NOSORT, 0),                            # 4 url
                ('', NOSORT, 0),                            # 5 id
                {"name": '', "type": TOGGLE}, ],            # 6 visible? bool
            list_mode="tree")
        pos = None
        addon_update_list.sort(key=lambda x: "%s %s" % (x[0], x[2]["t"]))
        last_category = None
        for (status, plugin_url, plugin_dict) in addon_update_list:
            # what was the following used for??
            # count = get_count(addon_update_list, plugin_dict["t"])
            category = _("%(adjective)s: %(addon)s") % {
                "adjective": status,
                "addon": _(plugin_dict["t"])}
            if last_category != category:
                last_category = category
                node = self.list.add([False,  # initially selected?
                                      category,
                                      "",
                                      "",
                                      "",
                                      "",
                                      False])  # checkbox visible?
            m_iter = self.list.add([False,  # initially selected?
                                    "%s %s" % (status, _(plugin_dict["t"])),
                                    "%s (%s)" % (plugin_dict["n"],
                                                 plugin_dict["v"]),
                                    plugin_dict["d"],
                                    plugin_url,
                                    plugin_dict["i"],
                                    True], node=node)
            if pos is None:
                pos = m_iter
        if pos:
            self.list.selection.select_iter(pos)

        self.show()
        self.window.run()  # pylint: disable=no-member

    def build_menu_names(self, obj):
        return (self.title, " ")

    def select_all_clicked(self, _widget):
        """
        Select all of the addons for download.
        """
        self.list.model.foreach(update_rows, True)
        self.list.tree.expand_all()

    def select_none_clicked(self, _widget):
        """
        Select none of the addons for download.
        """
        self.list.model.foreach(update_rows, False)
        self.list.tree.expand_all()

    def install_addons(self, obj):
        """
        Process all of the selected addons.
        """
        self.window.hide()  # pylint: disable=no-member
        model = self.list.model

        m_iter = model.get_iter_first()
        length = 0
        while m_iter:
            m_iter = model.iter_next(m_iter)
            if m_iter:
                length += model.iter_n_children(m_iter)

        longop = LongOpStatus(
            _("Downloading and installing selected addons..."),
            length, 1,  # total, increment-by
            can_cancel=True)
        _pm = ProgressMonitor(GtkProgressDialog, (
            "Title", self.parent_window, Gtk.DialogFlags.MODAL))
        _pm.add_op(longop)
        count = 0
        if not config.get('behavior.do-not-show-previously-'
                          'seen-addon-updates'):
            # reset list
            config.get('behavior.previously-seen-addon-updates')[:] = []

        m_iter = model.get_iter_first()
        errors = []
        while m_iter:
            for rowcnt in range(model.iter_n_children(m_iter)):
                child = model.iter_nth_child(m_iter, rowcnt)
                row = [model.get_value(child, n) for n in range(6)]
                if longop.should_cancel():
                    break
                elif row[0]:  # toggle on
                    _ok = load_addon_file(row[4], callback=LOG.debug)
                    if _ok:
                        count += 1
                    else:
                        errors.append(row[2])
                else:  # add to list of previously seen, but not installed
                    if row[5] not in config.get('behavior.previously-seen-'
                                                'addon-updates'):
                        config.get('behavior.previously-seen-'
                                   'addon-updates').append(row[5])
                longop.heartbeat()
            m_iter = model.iter_next(m_iter)

        if not longop.was_cancelled():
            longop.end()
        if errors:
            OkDialog(_("Installation Errors"),
                     _("The following addons had errors: ") +
                     ", ".join(errors),
                     parent=self.parent_window)
        if count:
            self.rescan = True
            OkDialog(_("Done downloading and installing addons"),
                     # translators: leave all/any {...} untranslated
                     "%s %s" % (ngettext("{number_of} addon was installed.",
                                         "{number_of} addons were installed.",
                                         count).format(number_of=count),
                                _("If you have installed a 'Gramps View', you "
                                  "will need to restart Gramps.")),
                     parent=self.parent_window)
        else:
            OkDialog(_("Done downloading and installing addons"),
                     _("No addons were installed."),
                     parent=self.parent_window)
        self.close()


#-------------------------------------------------------------------------
#
# Local Functions
#
#-------------------------------------------------------------------------
def update_rows(model, path, m_iter, user_data):
    """
    Update the rows of a model.
    """
    #path: (8,)   iter: <GtkTreeIter at 0xbfa89fa0>
    #path: (8, 0) iter: <GtkTreeIter at 0xbfa89f60>
    if len(path.get_indices()) == 2:
        row = model[path]
        row[0] = user_data
        model.row_changed(path, m_iter)


def get_count(addon_update_list, category):
    """
    Get the count of matching category items.
    """
    count = 0
    for (dummy, plugin_url, plugin_dict) in addon_update_list:
        if plugin_dict["t"] == category and plugin_url:
            count += 1
    return count
