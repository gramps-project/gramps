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
# $Id$

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
import os
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.utils.callback import Callback
from gen.plug import BasePluginManager, PluginRegister
from gen.constfunc import win
from gen.config import config
import const

#-------------------------------------------------------------------------
#
# Functions
#
#-------------------------------------------------------------------------

def base_reg_stock_icons(iconpaths, extraiconsize, items):
    """
    Reusable base to register stock icons in Gramps
    ..attribute iconpaths: list of main directory of the base icon, and
      extension, eg:
      [(os.path.join(const.IMAGE_DIR, 'scalable'), '.svg')]
    ..attribute extraiconsize: list of dir with extra prepared icon sizes and
      the gtk size to use them for, eg:
      [(os.path.join(const.IMAGE_DIR, '22x22'), gtk.ICON_SIZE_LARGE_TOOLBAR)]
    ..attribute items: list of icons to register, eg:
      [('gramps-db', _('Family Trees'), gtk.gdk.CONTROL_MASK, 0, '')]
    """
    
    # Register our stock items
    gtk.stock_add (items)
    
    # Add our custom icon factory to the list of defaults
    factory = gtk.IconFactory ()
    factory.add_default ()
    
    for data in items:
        pixbuf = 0
        for (dirname, ext) in iconpaths:
            icon_file = os.path.expanduser(os.path.join(dirname, data[0]+ext))
            if os.path.isfile(icon_file):
                try:
                    pixbuf = gtk.gdk.pixbuf_new_from_file (icon_file)
                    break
                except:
                    pass
                  
        if not pixbuf :
            icon_file = os.path.join(const.IMAGE_DIR, 'gramps.png')
            pixbuf = gtk.gdk.pixbuf_new_from_file (icon_file)
            
        ## FIXME from gtk 2.17.3/2.15.2 change this to 
        ## FIXME  pixbuf = pixbuf.add_alpha(True, 255, 255, 255)
        pixbuf = pixbuf.add_alpha(True, chr(0xff), chr(0xff), chr(0xff))
        icon_set = gtk.IconSet (pixbuf)
        #add different sized icons, always png type!
        for size in extraiconsize :
            pixbuf = 0
            icon_file = os.path.expanduser(
                    os.path.join(size[0], data[0]+'.png'))
            if os.path.isfile(icon_file):
                try:
                    pixbuf = gtk.gdk.pixbuf_new_from_file (icon_file)
                except:
                    pass
                    
            if pixbuf :
                source = gtk.IconSource()
                source.set_size_wildcarded(False)
                source.set_size(size[1])
                source.set_pixbuf(pixbuf)
                icon_set.add_source(source)
            
        factory.add (data[0], icon_set)

#-------------------------------------------------------------------------
#
# GuiPluginManager
#
#-------------------------------------------------------------------------
class GuiPluginManager(Callback):
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
        
        Callback.__init__(self)
        self.basemgr = BasePluginManager.get_instance()
        self.__hidden_plugins = set(config.get('plugin.hiddenplugins'))
        self.__hidden_changed()

    def load_plugin(self, pdata):
        if not self.is_loaded(pdata.id):
            #load stock icons before import, only gui needs this
            if pdata.icons:
                if pdata.icondir and os.path.isdir(pdata.icondir):
                    dir = pdata.icondir
                else:
                    #use the plugin directory
                    dir = pdata.directory
                self.load_icons(pdata.icons, dir)
        return self.basemgr.load_plugin(pdata)

    def reload_plugins(self):
        self.basemgr.reload_plugins()
        self.emit('plugins-reloaded')
    
    def __getattr__(self, name):
        return getattr(self.basemgr, name)

    def load_icons(self, icons, dir):
        """
        Load icons in the iconfactory of gramps, so they can be used in the
        plugin.
        
        ..attribute icons: 
          New stock icons to register. A list of tuples (stock_id, icon_label), 
          eg: 
            [('gramps_myplugin', _('My Plugin')), 
            ('gramps_myplugin_open', _('Open Plugin'))]
          The plugin directory must contain the directories scalable, 48x48, 22x22
          and 16x16 with the icons, eg in dir we have:
            scalable/gramps_myplugin.svg
            48x48/gramps_myplugin.png
            22x22/gramps_myplugin.png
        ..attribute dir: directory from where to load the icons
        """
        if win():
            iconpaths = [
                        (os.path.join(dir, '48x48'), '.png'), 
                        (dir, '.png'), 
                        ]
        else :
            iconpaths = [
                        (os.path.join(dir, 'scalable'), '.svg'), 
                        (dir, '.svg'), (dir, '.png'), 
                        ]
        
        #sizes: menu=16, small_toolbar=18, large_toolbar=24, 
        #       button=20, dnd=32, dialog=48
        #add to the back of this list to overrule images set at beginning of list
        extraiconsize = [
                        (os.path.join(dir, '22x22'), gtk.ICON_SIZE_LARGE_TOOLBAR), 
                        (os.path.join(dir, '16x16'), gtk.ICON_SIZE_MENU), 
                        (os.path.join(dir, '22x22'), gtk.ICON_SIZE_BUTTON), 
                        ]

        items = []
        for stock_id, label in icons:
            items.append((stock_id, label, gtk.gdk.CONTROL_MASK, 0, ''))
        
        base_reg_stock_icons(iconpaths, extraiconsize, items)


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
        config.set('plugin.hiddenplugins', list(self.__hidden_plugins))
        config.save()
        self.__hidden_changed()
    
    def unhide_plugin(self, id):
        """ Unhide plugin with given id. This will unhide the plugin so queries
        return it again, and write this change to the config
        """
        self.__hidden_plugins.remove(id)
        config.set('plugin.hiddenplugins', list(self.__hidden_plugins))
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

    def get_reg_views(self):
        """ Return list of non hidden registered views
        """
        return [plg for plg in self.basemgr.get_reg_views()
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

    def get_reg_sidebars(self):
        """ Return list of non hidden registered sidebars
        """
        return [plg for plg in self.basemgr.get_reg_sidebars()
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

    def get_reg_general(self, category=None):
        return [plg for plg in self.basemgr.get_reg_general(category)
                                if plg.id not in self.__hidden_plugins]

