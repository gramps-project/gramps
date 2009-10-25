#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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
# $Id: _manager.py 13403 2009-10-24 20:27:10Z bmcage $

"""
The core of the GRAMPS plugin system. This module provides capability to load
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


#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import gen.utils
from gen.plug import BasePluginManager, PluginRegister
import config

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
# GuiPluginManager
#
#-------------------------------------------------------------------------
class GuiPluginManager(gen.utils.Callback):
    """ PluginManager is a Singleton which manages plugins. 
    It is the gui implementation using a unique BasePluginmanager. 
    This class adds the possibility to hide plugins in the GUI via a config 
    setting
    """
    __instance = None
    __signals__ = { 'plugins-reloaded' : None }
    
    def get_instance():
        """ Use this function to get the instance of the PluginManager """
        if GuiPluginManager.__instance is None:
            GuiPluginManager.__instance = 1 # Set to 1 for __init__()
            GuiPluginManager.__instance = GuiPluginManager()
        return GuiPluginManager.__instance
    get_instance = staticmethod(get_instance)
            
    def __init__(self):
        """ This function should only be run once by get_instance() """
        if GuiPluginManager.__instance is not 1:
            raise Exception("This class is a singleton. "
                            "Use the get_instance() method")
        
        gen.utils.Callback.__init__(self)
        self.basemgr = BasePluginManager.get_instance()
        self.__hidden_plugins = set([])
        for id in config.get('plugin.hiddenplugins'):
            self.__hidden_plugins.add(id)
        self.__hidden_changed()
    
    def reload_plugins(self):
        self.basemgr.reload_plugins()
        self.emit('plugins-reloaded')
    
    def __getattr__(self, name):
        return getattr(self.basemgr, name)
    
    def __hidden_changed(self, *args):
        #if hidden changed, stored data must be emptied as it could contain
        #something that now must be hidden
        self.empty_managed_plugins()
        #objects that need to know if the plugins available changed, are 
        #listening to this signal to update themselves. If a plugin becomes
        #(un)hidden, this should happen, so we emit.
        self.emit('plugins-reloaded')

    def get_hidden_plugin_ids(self):
        """
        Returns copy of the set hidden plugin ids
        """
        return self.__hidden_plugins.copy()

    def hide_plugin(self, id):
        """ Hide plugin with given id. This will hide the plugin so queries do
        not return it anymore, and write this change to the config.
        Note that config will then emit a signal
        """ 
        self.__hidden_plugins.add(id)
        hideset = [x for x in self.__hidden_plugins]
        config.set('plugin.hiddenplugins', hideset)
        config.save()
        self.__hidden_changed()
    
    def unhide_plugin(self, id):
        """ Unhide plugin with given id. This will unhide the plugin so queries
        return it again, and write this change to the config
        """
        self.__hidden_plugins.remove(id)
        hideset = [x for x in self.__hidden_plugins]
        config.set('plugin.hiddenplugins', hideset)
        config.save()
        self.__hidden_changed()

    def get_reg_reports(self, gui=True):
        """ Return list of non hidden registered reports
        :Param gui: bool indicating if GUI reports or CLI reports must be
            returned
        """
        return [plg for plg in self.basemgr.get_reg_reports(gui)
                                if plg.id not in self.__hidden_plugins]
    
    def get_reg_tools(self, gui=True):
        """ Return list of non hidden  registered tools
        :Param gui: bool indicating if GUI reports or CLI reports must be
            returned
        """
        return [plg for plg in self.basemgr.get_reg_tools(gui)
                                if plg.id not in self.__hidden_plugins]
    
    def get_reg_quick_reports(self):
        """ Return list of non hidden  registered quick reports
        """
        return [plg for plg in self.basemgr.get_reg_quick_reports()
                                if plg.id not in self.__hidden_plugins]
    
    def get_reg_mapservices(self):
        """ Return list of non hidden  registered mapservices
        """
        return [plg for plg in self.basemgr.get_reg_mapservices()
                                if plg.id not in self.__hidden_plugins]

    def get_reg_bookitems(self):
        """ Return list of non hidden  reports registered as bookitem
        """
        return [plg for plg in self.basemgr.get_reg_bookitems()
                                if plg.id not in self.__hidden_plugins]

    def get_reg_gramplets(self):
        """ Return list of non hidden  reports registered as bookitem
        """
        return [plg for plg in self.basemgr.get_reg_gramplets() 
                                if plg.id not in self.__hidden_plugins]

    def get_reg_importers(self):
        """ Return list of registered importers
        """
        return [plg for plg in self.basemgr.get_reg_importers()
                                if plg.id not in self.__hidden_plugins]
    
    def get_reg_exporters(self):
        """ Return list of registered exporters
        """
        return [plg for plg in self.basemgr.get_reg_exporters()
                                if plg.id not in self.__hidden_plugins]
    
    def get_reg_docgens(self):
        """ Return list of registered docgen
        """
        return [plg for plg in self.basemgr.get_reg_docgens()
                                if plg.id not in self.__hidden_plugins]
