#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2012       Paul Franklin
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

"""
The core of the Gramps plugin system. This module provides capability to load
plugins from specified directories and provide information about the loaded
plugins.

Plugins are divided into several categories. These are: reports, tools,
importers, exporters, quick reports, and document generators.
"""

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import os
import sys
import re
import logging
import importlib
LOG = logging.getLogger('._manager')
LOG.progagate = True
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ..config import config
from . import PluginRegister, ImportPlugin, ExportPlugin, DocGenPlugin
from ..constfunc import win

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_UNAVAILABLE = _("No description was provided")

#-------------------------------------------------------------------------
#
# BasePluginManager
#
#-------------------------------------------------------------------------
class BasePluginManager:
    """ unique singleton storage class for a :class:`.PluginManager`. """

    __instance = None

    def get_instance():
        """
        Use this function to get the instance of the :class:`.PluginManager`
        """
        if BasePluginManager.__instance is None:
            BasePluginManager.__instance = 1 # Set to 1 for __init__()
            BasePluginManager.__instance = BasePluginManager()
        return BasePluginManager.__instance
    get_instance = staticmethod(get_instance)

    def __init__(self):
        """ This function should only be run once by get_instance() """
        if BasePluginManager.__instance != 1:
            raise Exception("This class is a singleton. "
                            "Use the get_instance() method")

        self.__import_plugins = []
        self.__export_plugins = []
        self.__docgen_plugins = []

        self.__attempt_list = []
        self.__failmsg_list = []
        self.__external_opt_dict = {}
        self.__success_list = []
        self.__docgen_names = []

        self.__mod2text = {}
        self.__modules = {}

        self.__pgr = PluginRegister.get_instance()
        self.__loaded_plugins = {}
        self.__scanned_dirs = []

    def reg_plugins(self, direct, dbstate=None, uistate=None,
                    load_on_reg=False, rescan=False):
        """
        Searches the specified directory, and registers python plugin that
        are being defined in gpr.py files.

        If a relationship calculator for env var LANG is present, it is
        immediately loaded so it is available for all.
        """
        if rescan:
            self.__import_plugins = []
            self.__export_plugins = []
            self.__docgen_plugins = []
            self.__docgen_names = []
            self.__scanned_dirs = []
            self.__pgr._PluginRegister__plugindata = []
            self.__pgr._PluginRegister__id_to_pdata = {}
        # if we've already scanned this directory or if the directory does not
        # exist, we are done.  Should only happen in tests.

        # LOG.warning("\nPlugin manager registration: %s, load_on_reg=%s,"
        #             " been_here=%s, pahte exists:%s", direct, load_on_reg,
        #             direct in self.__scanned_dirs, os.path.isdir(direct))

        if os.path.isdir(direct) and direct not in self.__scanned_dirs:
            self.__scanned_dirs.append(direct)
            for (dirpath, dirnames, filenames) in os.walk(direct,
                                                          topdown=True):
                for dirname in dirnames[:]:
                    # Skip hidden and system directories:
                    if dirname.startswith(".") or dirname in ["po", "locale",
                                                              "__pycache__"]:
                        dirnames.remove(dirname)
                # LOG.warning("Plugin dir scanned: %s", dirpath)
                self.__pgr.scan_dir(dirpath, filenames, uistate=uistate)

        if load_on_reg:
            # Run plugins that request to be loaded on startup and
            # have a load_on_reg callable.
            # first, remove hidden
            plugins_to_load = []
            for plugin in self.__pgr.filter_load_on_reg():
                # LOG.warning("\nFound %s at registration", plugin.id)
                if plugin.id in config.get("plugin.hiddenplugins"):
                    continue
                plugins_to_load.append(plugin)
            # next, sort on dependencies
            # Probably a more efficient method to get dependency graph:
            plugins_sorted = []
            count = 0
            max_count = len(plugins_to_load)
            while plugins_to_load:
                for plugin in plugins_to_load[:]: # copy of list
                    # LOG.warning("\nDependencies for %s at registration",
                    #             plugin.id)
                    delay = False
                    for depend in plugin.depends_on:
                        if depend not in [p.id for p in plugins_sorted]:
                            delay = True
                            break
                    if delay:
                        pass # wait till next loop
                    else:
                        if plugin not in plugins_sorted:
                            plugins_sorted.append(plugin)
                        if plugin in plugins_to_load:
                            plugins_to_load.remove(plugin)
                count += 1
                if count > max_count:
                    print("Cannot resolve the following plugin dependencies:")
                    for plugin in plugins_to_load:
                        print("   Plugin '%s' requires: %s" % (
                            plugin.id, plugin.depends_on))
                    break
            # now load them:
            for plugin in plugins_sorted:
                # next line shouldn't be necessary, but this gets called a lot
                # of times during Travis test; so avoid multiple copies
                plugin.data = []
                mod = self.load_plugin(plugin)
                if hasattr(mod, "load_on_reg"):
                    # LOG.warning("\nRun %s at registration", plugin.id)
                    try:
                        results = mod.load_on_reg(dbstate, uistate, plugin)
                    except:
                        import traceback
                        traceback.print_exc()
                        print("Plugin '%s' did not run; continuing..." % plugin.name)
                        continue
                    try:
                        iter(results)
                        plugin.data += results
                    except:
                        plugin.data = results
        # Get the addon rules and import them and make them findable
        for plugin in self.__pgr.rule_plugins():
            mod = self.load_plugin(plugin)  # load the addon rule
            # get place in rule heirarchy to put the new rule
            obj_rules = importlib.import_module(
                'gramps.gen.filters.rules.' + plugin.namespace.lower())
            # get the new rule class object
            r_class = getattr(mod, plugin.ruleclass)
            # make the new rule findable via import statements
            setattr(obj_rules, plugin.ruleclass, r_class)
            # and add it to the correct fiter editor list
            obj_rules.editor_rule_list.append(r_class)

    def is_loaded(self, pdata_id):
        """
        return True if plugin is already loaded
        """
        if pdata_id in self.__loaded_plugins:
            return True
        return False

    def load_plugin(self, pdata):
        """
        Load a :class:`.PluginData` object. This means import of the python
        module. Plugin directories are added to sys path, so files are found
        """
        if pdata.id in self.__loaded_plugins:
            return self.__loaded_plugins[pdata.id]
        need_reload = False
        filename = pdata.fname
        if filename in self.__modules:
            #filename is loaded already, a different plugin in this module
            _module = self.__modules[filename]
            self.__success_list.append((filename, _module, pdata))
            self.__loaded_plugins[pdata.id] = _module
            self.__mod2text[_module.__name__] += ' - ' + pdata.description
            return _module
        if filename in self.__attempt_list:
            #new load attempt after a fail, a reload needed
            need_reload = True
            #remove previous fail of the plugins in this file
            dellist = []
            for index, data in enumerate(self.__failmsg_list):
                if data[0] == filename:
                    dellist.append(index)
            dellist.reverse()
            for index in dellist:
                del self.__failmsg_list[index]
        else:
            self.__attempt_list.append(filename)
        try:
            _module = self.import_plugin(pdata)
            if need_reload:
                # For some strange reason second importing of a failed plugin
                # results in success. Then reload reveals the actual error.
                # Looks like a bug in Python.
                _module = self.reload(_module, pdata)
            if _module:
                self.__success_list.append((filename, _module, pdata))
                self.__modules[filename] = _module
                self.__loaded_plugins[pdata.id] = _module
                self.__mod2text[_module.__name__] = pdata.description
            return _module
        except:
            import traceback
            traceback.print_exc()
            self.__failmsg_list.append((filename, sys.exc_info(), pdata))

        return None

    def import_plugin(self, pdata):
        """
        Rather than just __import__(id), this will add the pdata.fpath
        to sys.path first (if needed), import, and then reset path.
        """
        module = None
        if isinstance(pdata, str):
            pdata = self.get_plugin(pdata)
        if not pdata:
            return None
        if pdata.fpath not in sys.path:
            if pdata.mod_name:
                sys.path.insert(0, pdata.fpath)
                try:
                    module = __import__(pdata.mod_name)
                except ValueError as err:
                    # Python3 on Windows  work with unicode in sys.path
                    # but they are mbcs encode for checking validity
                    if win():
                        # we don't want to load Gramps core plugin like this
                        # only 3rd party plugins
                        if "gramps"  in pdata.fpath:
                            try:
                                sys.path.insert(0, ".")
                                oldwd = os.getcwd()
                                os.chdir(pdata.fpath)
                                module = __import__(pdata.mod_name)
                                os.chdir(oldwd)
                                sys.path.pop(0)
                            except ValueError as err:
                                LOG.warning("Plugin error (from '%s'): %s"
                                                % (pdata.mod_name, err))
                    else:
                        LOG.warning("Plugin error (from '%s'): %s"
                                        % (pdata.mod_name, err))
                except ImportError as err:
                    LOG.warning("Plugin error (from '%s'): %s"
                                    % (pdata.mod_name, err))
                sys.path.pop(0)
            else:
                print("WARNING: module cannot be loaded")
        else:
            module = __import__(pdata.mod_name)
        return module

    def empty_managed_plugins(self):
        """ For some plugins, managed Plugin are used. These are only
        reobtained from the registry if this method is called
        """
        # TODO: do other lists need to be reset here, too?
        self.__import_plugins = []
        self.__export_plugins = []
        self.__docgen_plugins = []
        self.__docgen_names = []


    def reload_plugins(self):
        """ Reload previously loaded plugins """
        pymod = re.compile(r"^(.*)\.py$")

        oldfailmsg = self.__failmsg_list[:]
        self.__failmsg_list = []

        # attempt to reload all plugins that have succeeded in the past
        self.empty_managed_plugins()
        self.__loaded_plugins = {}

        oldmodules = self.__modules
        self.__modules = {}
        dellist = []
        #reload first modules that loaded successfully previously
        for (index, plugin) in enumerate(self.__success_list):
            filename = plugin[0]
            pdata = plugin[2]
            filename = filename.replace('pyc','py')
            filename = filename.replace('pyo','py')
            if filename in self.__modules:
                #module already reloaded, a second plugin in same module
                continue
            try:
                self.reload(plugin[1], pdata)
                self.__modules[filename] = plugin[1]
                self.__loaded_plugins[pdata.id] = plugin[1]
            except:
                dellist.append(index)
                self.__failmsg_list.append((filename, sys.exc_info(), pdata))

        dellist.reverse()
        for index in dellist:
            del self.__success_list[index]

        # Remove previously good plugins that are now bad
        # from the registered lists
        self.__purge_failed()

        # attempt to load the plugins that have failed in the past
        for (filename, message, pdata) in oldfailmsg:
            self.load_plugin(pdata)

    def reload(self, module, pdata):
        """
        Reloads modules that might not be in the path.
        """
        try:
            import imp
            fp, pathname, description = imp.find_module(pdata.mod_name, [pdata.fpath])
            try:
                module = imp.load_module(pdata.mod_name, fp, pathname,description)
            finally:
                if fp:
                    fp.close()
        except:
            if pdata.mod_name in sys.modules:
                del sys.modules[pdata.mod_name]
            module = self.import_plugin(pdata)
        return module

    def get_fail_list(self):
        """ Return the list of failed plugins. """
        return self.__failmsg_list

    def get_success_list(self):
        """ Return the list of succeeded plugins. """
        return self.__success_list

    def get_plugin(self, id):
        """
        Returns a plugin object from :class:`.PluginRegister` by id.
        """
        return self.__pgr.get_plugin(id)

    def get_reg_reports(self, gui=True):
        """ Return list of registered reports
        :param gui: bool indicating if GUI reports or CLI reports must be
        returned
        """
        return self.__pgr.report_plugins(gui)

    def get_reg_tools(self, gui=True):
        """ Return list of registered tools
        :aram gui: bool indicating if GUI reports or CLI reports must be
        returned
        """
        return self.__pgr.tool_plugins(gui)

    def get_reg_quick_reports(self):
        """ Return list of registered quick reports
        """
        return self.__pgr.quickreport_plugins()

    def get_reg_views(self):
        """ Return list of registered views
        """
        return self.__pgr.view_plugins()

    def get_reg_mapservices(self):
        """ Return list of registered mapservices
        """
        return self.__pgr.mapservice_plugins()

    def get_reg_bookitems(self):
        """ Return list of reports registered as bookitem
        """
        return self.__pgr.bookitem_plugins()

    def get_reg_gramplets(self):
        """ Return list of non hidden gramplets.
        """
        return self.__pgr.gramplet_plugins()

    def get_reg_sidebars(self):
        """ Return list of registered sidebars.
        """
        return self.__pgr.sidebar_plugins()

    def get_reg_databases(self):
        """ Return list of registered database backends
        """
        return self.__pgr.database_plugins()

    def get_external_opt_dict(self):
        """ Return the dictionary of external options. """
        return self.__external_opt_dict

    def get_module_description(self, module):
        """ Given a module name, return the module description. """
        return self.__mod2text.get(module, '')

    def get_reg_importers(self):
        """ Return list of registered importers
        """
        return self.__pgr.import_plugins()

    def get_reg_exporters(self):
        """ Return list of registered exporters
        """
        return self.__pgr.export_plugins()

    def get_reg_docgens(self):
        """ Return list of registered docgen
        """
        return self.__pgr.docgen_plugins()

    def get_reg_general(self, category=None):
        """ Return list of registered general libs
        """
        return self.__pgr.general_plugins(category)

    def load_plugin_category(self, category):
        """
        Make sure all plugins of a type are loaded.
        """
        for plugin in self.__pgr.general_plugins(category):
            if not self.is_loaded(plugin):
                self.load_plugin(plugin)

    def get_plugin_data(self, category):
        """
        Gets all of the data from general plugins of type category.
        plugin.data may be a single item, an iterable, or a callable.

        >>> PLUGMAN.get_plugin_data('CSS')
        <a list of raw data items>
        """
        retval = []
        data = None
        for plugin in self.__pgr.general_plugins(category):
            data = plugin.data
            try:
                iter(data)
                retval.extend(data)
            except:
                retval.append(data)
        return retval

    def process_plugin_data(self, category):
        """
        Gathers all of the data from general plugins of type category,
        and pass it to a single process function from one of those
        plugins.

        >>> PLUGMAN.process_plugin_data('CSS')
        <a list of processed data items>
        """
        retval = []
        data = None
        process = None
        for plugin in self.__pgr.general_plugins(category):
            if plugin.process is not None:
                mod = self.load_plugin(plugin)
                if hasattr(mod, plugin.process):
                    process = getattr(mod, plugin.process)
            data = plugin.data
            if data:
                try:
                    iter(data)
                    retval.extend(data)
                except:
                    retval.append(data)
        # LOG.warning("Process plugin data=%s, %s, items=%s",
        #             process is not None, category, len(retval))
        if process:
            return process(retval)
        return retval

    def get_import_plugins(self):
        """
        Get the list of import plugins.

        :return: :class:`.ImportPlugin` (a list of ImportPlugin instances)
        """
        ## TODO: would it not be better to remove ImportPlugin and use
        ## only PluginData, loading from module when importfunction needed?
        if self.__import_plugins == []:
            #The module still needs to be imported
            for pdata in self.get_reg_importers():
                if pdata.id in config.get("plugin.hiddenplugins"):
                    continue
                mod = self.load_plugin(pdata)
                if mod:
                    imp = ImportPlugin(name=pdata.name,
                        description = pdata.description,
                        import_function = getattr(mod, pdata.import_function),
                        extension = pdata.extension)
                    self.__import_plugins.append(imp)

        return self.__import_plugins

    def get_export_plugins(self):
        """
        Get the list of export plugins.

        :return: :class:`.ExportPlugin` (a list of ExportPlugin instances)
        """
        ## TODO: would it not be better to remove ExportPlugin and use
        ## only PluginData, loading from module when export/options needed?
        if self.__export_plugins == []:
            #The modules still need to be imported
            for pdata in self.get_reg_exporters():
                if pdata.id in config.get("plugin.hiddenplugins"):
                    continue
                mod = self.load_plugin(pdata)
                if mod:
                    options = None
                    if (pdata.export_options and
                        hasattr(mod, pdata.export_options)):
                        options = getattr(mod, pdata.export_options)
                    exp = ExportPlugin(name=pdata.name_accell,
                        description = pdata.description,
                        export_function = getattr(mod, pdata.export_function),
                        extension = pdata.extension,
                        config = (pdata.export_options_title, options))
                    self.__export_plugins.append(exp)

        return self.__export_plugins

    def get_docgen_plugins(self):
        """
        Get the list of docgen plugins.

        :return: :class:`.DocGenPlugin` (a list of DocGenPlugin instances)
        """
        ## TODO: would it not be better to return list of plugindata, and only
        ##       import those docgen that will then actuallly be needed?
        ##       So, only do import when docgen.get_basedoc() is requested
        if self.__docgen_plugins == []:
            #The modules still need to be imported
            hiddenplugins = config.get("plugin.hiddenplugins")
            for pdata in self.get_reg_docgens():
                if pdata.id in hiddenplugins:
                    continue
                mod = self.load_plugin(pdata)
                if mod:
                    oclass = None
                    if pdata.optionclass:
                        oclass = getattr(mod, pdata.optionclass)
                    dgp = DocGenPlugin(name=pdata.name,
                            description = pdata.description,
                            basedoc = getattr(mod, pdata.docclass),
                            paper = pdata.paper,
                            style = pdata.style,
                            extension = pdata.extension,
                            docoptclass = oclass,
                            basedocname = pdata.docclass )
                    self.__docgen_plugins.append(dgp)

        return self.__docgen_plugins

    def get_docgen_names(self):
        """
        Get the list of docgen plugin names.

        :return: a list of :class:`.DocGenPlugin` names
        """
        if self.__docgen_names == []:
            hiddenplugins = config.get("plugin.hiddenplugins")
            for pdata in self.get_reg_docgens():
                if pdata.id not in hiddenplugins:
                    self.__docgen_names.append(pdata.docclass)
        return self.__docgen_names

    def register_option(self, option, guioption):
        """
        Register an external option.

        Register a mapping from option to guioption for an option
        that is not native to Gramps but provided by the plugin writer.
        This should typically be called during initialisation of a
        :class:`.ReportOptions` class.

        :param option:      the option class
        :type option:       class that inherits from gen.plug.menu.Option
        :param guioption:   the gui-option class
        :type guioption:    class that inherits from Gtk.Widget.
        """
        self.__external_opt_dict[option] = guioption;

    def __purge_failed(self):
        """
        Purge the failed plugins from the corresponding lists.
        """
        failed_module_names = [
            os.path.splitext(os.path.basename(filename))[0]
            for filename, msg, pdata in self.__failmsg_list
            ]

        self.__export_plugins[:] = [ item for item in self.__export_plugins
                    if item.get_module_name() not in failed_module_names ][:]
        self.__import_plugins[:] = [ item for item in self.__import_plugins
                    if item.get_module_name() not in failed_module_names ][:]
        self.__docgen_plugins[:] = [ item for item in self.__docgen_plugins
                    if item.get_module_name() not in failed_module_names ][:]
