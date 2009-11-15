#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009       Benny Malengier
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
This module provides the base class for plugin registration. 
It provides an object containing data about the plugin (version, filename, ...)
and a register for the data of all plugins .
"""
#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import os
import sys
import re
import traceback
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from const import VERSION as GRAMPSVERSION
from TransUtils import get_addon_translator

#-------------------------------------------------------------------------
#
# PluginData
#
#-------------------------------------------------------------------------

#a plugin is stable or unstable
STABLE   = 0
UNSTABLE = 1
STATUS   = [STABLE, UNSTABLE]
STATUSTEXT = {STABLE: _('Stable'), UNSTABLE: _('Unstable')}
#possible plugin types
REPORT      = 0
QUICKREPORT = 1 # deprecated
QUICKVIEW   = 1
TOOL        = 2
IMPORT      = 3
EXPORT      = 4
DOCGEN      = 5
GENERAL     = 6
MAPSERVICE  = 7
VIEW        = 8
RELCALC     = 9
GRAMPLET    = 10
PTYPE       = [ REPORT , QUICKREPORT, TOOL, IMPORT,
                EXPORT, DOCGEN, GENERAL, MAPSERVICE, VIEW, RELCALC, GRAMPLET]
PTYPE_STR   = {
        REPORT: _('Report') , 
        QUICKREPORT: _('Quickreport'), 
        TOOL: _('Tool'), 
        IMPORT: _('Importer'),
        EXPORT: _('Exporter'), 
        DOCGEN: _('Doc creator'), 
        GENERAL: _('Plugin lib'), 
        MAPSERVICE: _('Map service'), 
        VIEW: _('GRAMPS View'), 
        RELCALC: _('Relationships'), 
        GRAMPLET: _('Gramplet'),
        }

#possible report categories
CATEGORY_TEXT       = 0
CATEGORY_DRAW       = 1
CATEGORY_CODE       = 2
CATEGORY_WEB        = 3
CATEGORY_BOOK       = 4
CATEGORY_GRAPHVIZ   = 5
REPORT_CAT          = [ CATEGORY_TEXT, CATEGORY_DRAW, CATEGORY_CODE,
                        CATEGORY_WEB, CATEGORY_BOOK, CATEGORY_GRAPHVIZ]
#possible tool categories
TOOL_DEBUG  = -1
TOOL_ANAL   = 0
TOOL_DBPROC = 1
TOOL_DBFIX  = 2
TOOL_REVCTL = 3
TOOL_UTILS  = 4
TOOL_CAT    = [ TOOL_DEBUG, TOOL_ANAL, TOOL_DBPROC, TOOL_DBFIX, TOOL_REVCTL,
                TOOL_UTILS]

#possible view categories
VIEW_MISC    = 0
VIEW_PERSON  = 1
VIEW_REL     = 2
VIEW_FAMILY  = 3
VIEW_PEDI    = 4
VIEW_EVENT   = 5
VIEW_PLACE   = 6
VIEW_SOURCE  = 7
VIEW_REPO    = 8
VIEW_MEDIA   = 9
VIEW_NOTE    = 10
VIEW_GEO     = 11
VIEW_CAT    = [VIEW_MISC, VIEW_PERSON, VIEW_REL, VIEW_FAMILY, VIEW_EVENT,
               VIEW_PEDI, VIEW_PLACE, VIEW_SOURCE, VIEW_REPO, VIEW_MEDIA, 
               VIEW_NOTE, VIEW_GEO]

#possible quickreport categories
CATEGORY_QR_MISC       = -1
CATEGORY_QR_PERSON     = 0
CATEGORY_QR_FAMILY     = 1
CATEGORY_QR_EVENT      = 2
CATEGORY_QR_SOURCE     = 3
CATEGORY_QR_PLACE      = 4
CATEGORY_QR_REPOSITORY = 5
CATEGORY_QR_NOTE       = 6
CATEGORY_QR_DATE       = 7

# Modes for generating reports
REPORT_MODE_GUI = 1    # Standalone report using GUI
REPORT_MODE_BKI = 2    # Book Item interface using GUI
REPORT_MODE_CLI = 4    # Command line interface (CLI)
REPORT_MODES    = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]
    
# Modes for running tools
TOOL_MODE_GUI = 1    # Standard tool using GUI
TOOL_MODE_CLI = 2    # Command line interface (CLI)
TOOL_MODES    = [TOOL_MODE_GUI, TOOL_MODE_CLI]

# possible view orders
START = 1
END   = 2
        
class PluginData(object):
    """
    This is the base class for all plugin data objects.
    The workflow is: 
    1. plugin manager reads all register files, and stores plugin data
       objects in a plugin register
    2. when plugin is needed, the plugin register creates the plugin, and 
       the manager stores this, after which it can be executed.
    
    Attributes present for all plugins
    .. attribute:: id
       A unique identifier for the plugin. This is eg used to store the plugin
       settings.
    .. attribute:: name
       A friendly name to call this plugin (normally translated)
    .. attribute:: description
       A friendly description of what the plugin does
    .. attribute:: version
       The version of the plugin
    .. attribute:: status
       The status of the plugin, STABLE or UNSTABLE
       UNSTABLE is only visible in development code, not in release
    .. attribute:: fname
       The python file where the plugin implementation can be found
    .. attribute:: fpath
       The python path where the plugin implementation can be found
    .. attribute:: ptype
       The plugin type. One of REPORT , QUICKREPORT, TOOL, IMPORT,
        EXPORT, DOCGEN, GENERAL, MAPSERVICE, VIEW, GRAMPLET
    .. attribute:: authors
       List of authors of the plugin, default=[]
    .. attribute:: authors_email
       List of emails of the authors of the plugin, default=[]
    .. attribute:: supported
       Bool value indicating if the plugin is still supported, default=True
    .. attribute:: load_on_reg
       bool value, if True, the plugin is loaded on GRAMPS startup. Some 
       plugins. Only set this value if for testing you want the plugin to be
       loaded immediately on startup. default=False
    
    Attributes for RELCALC plugins:
    .. attribute:: relcalcclass 
       The class in the module that is the relationcalc class 
    .. attribute:: lang_list
       List of languages this plugin handles
    
    Attributes for REPORT plugins:
    .. attribute:: require_active
       Bool, If the reports requries an active person to be set or not
    .. attribute:: reportclass
       The class in the module that is the report class
    .. attribute:: report_modes
       The report modes: list of REPORT_MODE_GUI ,REPORT_MODE_BKI,REPORT_MODE_CLI
    
    Attributes for REPORT and TOOL and QUICKREPORT and VIEW plugins
    .. attribute:: category
       Or the report category the plugin belongs to, default=CATEGORY_TEXT
       or the tool category a plugin belongs to, default=TOOL_UTILS
       or the quickreport category a plugin belongs to, default=CATEGORY_QR_PERSON
       or the view category a plugin belongs to, default=VIEW_MISC
    
    Attributes for REPORT and TOOL plugins
    .. attribute:: optionclass
       The class in the module that is the option class
    
    Attributes for TOOL plugins
    .. attribute:: toolclass
       The class in the module that is the tool class
    .. attribute:: tool_modes
       The tool modes: list of TOOL_MODE_GUI, TOOL_MODE_CLI
    
    Attributes for DOCGEN plugins
    .. attribute :: basedocclass
       The class in the module that is the BaseDoc defined
    .. attribute :: paper
       bool, Indicates whether the plugin uses paper or not, default=True
    .. attribute :: style
       bool, Indicates whether the plugin uses styles or not, default=True
    
    Attribute for DOCGEN, EXPORT plugins
    .. attribute :: extension
       str, The file extension to use for output produced by the docgen/export,
       default=''
    
    Attributes for QUICKREPORT plugins
    .. attribute:: runfunc
       The function that executes the quick report
    
    Attributes for MAPSERVICE plugins
    .. attribute:: mapservice
       The class in the module that is a mapservice
    
    Attributes for EXPORT plugins
    .. attribute:: export_function
       Function that produces the export
    .. attribute:: export_options
       Class to set options
    .. attribute:: export_options_title
       Title for the option page
    
    Attributes for IMPORT plugins
    .. attribute:: import_function
       Function that starts an import
    
    Attributes for GRAMPLET plugins
    .. attribute:: gramplet
       The function or class that defines the gramplet.
    .. attribute:: height
       The height the gramplet should have in a column on GrampletView, 
       default = 200
    .. attribute:: detached_height
       The height the gramplet should have detached, default 300
    .. attribute:: detached_width
       The width the gramplet should have detached, default 400
    .. attribute:: expand
       If the attributed should be expanded on start, default False
    .. attribute:: gramplet_title
       Title to use for the gramplet, default = 'Gramplet'
    .. attribute:: help_url
       The URL where documentation for the URL can be found

    Attributes for VIEW plugins
    .. attribute:: viewclass
       A class of type ViewCreator that holds the needed info of the
       view to be created: icon, viewclass that derives from pageview, ...
    .. attribute:: order
       order can be START or END. Default is END. For END, on registering, 
       the view is appended to the list of views. If START, then the view is
       prepended. Only set START if you want a view to be the first in the
       order of views
    """

    def __init__(self):
        self._id = None
        self._name = None
        self._version = None
        self._description = None
        self._status = UNSTABLE
        self._fname = None
        self._fpath = None
        self._ptype = None
        self._authors = []
        self._authors_email = []
        self._supported = True
        self._load_on_reg = False
        #derived var
        self.mod_name = None
        #RELCALC attr
        self._relcalcclass = None
        self._lang_list = None
        #REPORT attr
        self._reportclass = None
        self._require_active = True
        self._report_modes = [REPORT_MODE_GUI]
        #REPORT and TOOL attr
        self._category = None
        self._optionclass = None
        #TOOL attr
        self._toolclass = None
        self._tool_modes = [TOOL_MODE_GUI]
        #DOCGEN attr
        self._basedocclass = None
        self._paper = True
        self._style = True  
        self._extension = ''
        #QUICKREPORT attr
        self._runfunc = None
        #MAPSERVICE attr
        self._mapservice = None
        #EXPORT attr
        self._export_function = None
        self._export_options = None
        self._export_options_title = ''
        #IMPORT attr
        self._import_function = None
        #GRAMPLET attr
        self._gramplet = None
        self._height = 200
        self._detached_height = 300
        self._detached_width = 400
        self._expand = False
        self._gramplet_title = _('Gramplet')
        self._help_url = None
        #VIEW attr
        self._viewclass = None
        self._order = END
    
    def _set_id(self, id):
       self._id = id

    def _get_id(self):
        return self._id

    def _set_name(self, name):
        self._name = name

    def _get_name(self):
        return self._name
    
    def _set_description(self, description):
        self._description = description

    def _get_description(self):
        return self._description

    def _set_version(self, version):
       self._version = version

    def _get_version(self):
        return self._version

    def _set_status(self, status):
        if status not in STATUS:
            raise ValueError, 'plugin status cannot be %s' % str(status)
        self._status = status

    def _get_status(self):
        return self._status
    
    def _set_fname(self, fname):
        self._fname = fname

    def _get_fname(self):
        return self._fname
    
    def _set_fpath(self, fpath):
        self._fpath = fpath

    def _get_fpath(self):
        return self._fpath
    
    def _set_ptype(self, ptype):
        if ptype not in PTYPE:
            raise ValueError, 'Plugin type cannot be %s' % str(ptype)
        elif self._ptype is not None:
            raise ValueError, 'Plugin type may not be changed'
        self._ptype = ptype
        if self._ptype == REPORT:
            self._category = CATEGORY_TEXT
        elif self._ptype == TOOL:
            self._category = TOOL_UTILS
        elif self._ptype == QUICKREPORT:
            self._category = CATEGORY_QR_PERSON
        elif self._ptype == VIEW:
            self._category = VIEW_MISC
        #if self._ptype == DOCGEN:
        #    self._load_on_reg = True

    def _get_ptype(self):
        return self._ptype

    def _set_authors(self, authors):
        if not authors or not isinstance(authors, list):
            return
        self._authors = authors

    def _get_authors(self):
        return self._authors

    def _set_authors_email(self, authors_email):
        if not authors_email or not isinstance(authors_email, list):
            return
        self._authors_email = authors_email

    def _get_authors_email(self):
        return self._authors_email
    
    def _set_supported(self, supported):
        if not isinstance(supported, bool):
            raise ValueError, 'Plugin must have supported=True or False'
        self._supported = supported
    
    def _get_supported(self):
        return self._supported

    def _get_load_on_reg(self):
        return self._load_on_reg
    
    def _set_load_on_reg(self, load_on_reg):
        if not isinstance(load_on_reg, bool):
            raise ValueError, 'Plugin must have load_on_reg=True or False'
        self._load_on_reg = load_on_reg
        
    id = property(_get_id, _set_id)   
    name = property(_get_name, _set_name)
    description = property(_get_description, _set_description) 
    version = property(_get_version, _set_version) 
    status = property(_get_status, _set_status)
    fname = property(_get_fname, _set_fname)
    fpath = property(_get_fpath, _set_fpath)
    ptype = property(_get_ptype, _set_ptype)
    authors = property(_get_authors, _set_authors)
    authors_email = property(_get_authors_email, _set_authors_email)
    supported = property(_get_supported, _set_supported)
    load_on_reg = property(_get_load_on_reg, _set_load_on_reg)
    
    def statustext(self):
        return STATUSTEXT[self.status]
    
    #type specific plugin attributes
    
    #RELCALC attributes
    def _set_relcalcclass(self, relcalcclass):
        if not self._ptype == RELCALC:
            raise ValueError, 'relcalcclass may only be set for RELCALC plugins'
        self._relcalcclass = relcalcclass

    def _get_relcalcclass(self):
        return self._relcalcclass
    
    def _set_lang_list(self, lang_list):
        if not self._ptype == RELCALC:
            raise ValueError, 'relcalcclass may only be set for RELCALC plugins'
        self._lang_list = lang_list

    def _get_lang_list(self):
        return self._lang_list

    relcalcclass = property(_get_relcalcclass, _set_relcalcclass)
    lang_list = property(_get_lang_list, _set_lang_list)
    
    #REPORT attributes
    def _set_require_active(self, require_active):
        if not self._ptype == REPORT:
            raise ValueError, 'require_active may only be set for REPORT plugins'
        if not isinstance(require_active, bool):
            raise ValueError, 'Report must have require_active=True or False'
        self._require_active = require_active

    def _get_require_active(self):
        return self._require_active

    def _set_reportclass(self, reportclass):
        if not self._ptype == REPORT:
            raise ValueError, 'reportclass may only be set for REPORT plugins'
        self._reportclass = reportclass

    def _get_reportclass(self):
        return self._reportclass

    def _set_report_modes(self, report_modes):
        if not self._ptype == REPORT:
            raise ValueError, 'report_modes may only be set for REPORT plugins'
        if not isinstance(report_modes, list):
            raise ValueError, 'report_modes must be a list'
        self._report_modes = [x for x in report_modes if x in REPORT_MODES]
        if not self._report_modes:
            raise ValueError, 'report_modes not a valid list of modes'

    def _get_report_modes(self):
        return self._report_modes

    #REPORT OR TOOL OR QUICKREPORT attributes
    def _set_category(self, category):
        if not (self._ptype == REPORT or self._ptype == TOOL or
        self._ptype == QUICKREPORT or self._ptype == VIEW):
            raise ValueError, 'category may only be set for ' \
                              'REPORT/TOOL/QUICKREPORT/VIEW plugins'
        self._category = category

    def _get_category(self):
        return self._category

    #REPORT OR TOOL attributes
    def _set_optionclass(self, optionclass):
        if not (self._ptype == REPORT or self.ptype == TOOL):
            raise ValueError, 'optionclass may only be set for REPORT/TOOL plugins'
        self._optionclass = optionclass

    def _get_optionclass(self):
        return self._optionclass

    #TOOL attributes
    def _set_toolclass(self, toolclass):
        if not self._ptype == TOOL:
            raise ValueError, 'toolclass may only be set for TOOL plugins'
        self._toolclass = toolclass
    
    def _get_toolclass(self):
        return self._toolclass

    def _set_tool_modes(self, tool_modes):
        if not self._ptype == TOOL:
            raise ValueError, 'tool_modes may only be set for TOOL plugins'
        if not isinstance(tool_modes, list):
            raise ValueError, 'tool_modes must be a list'
        self._tool_modes = [x for x in tool_modes if x in TOOL_MODES]
        if not self._tool_modes:
            raise ValueError, 'tool_modes not a valid list of modes'

    def _get_tool_modes(self):
        return self._tool_modes
    
    require_active = property(_get_require_active, _set_require_active)
    reportclass = property(_get_reportclass, _set_reportclass)
    report_modes = property(_get_report_modes, _set_report_modes)
    category = property(_get_category, _set_category)
    optionclass = property(_get_optionclass, _set_optionclass)
    toolclass = property(_get_toolclass, _set_toolclass)
    tool_modes = property(_get_tool_modes, _set_tool_modes)

    #DOCGEN attributes
    def _set_basedocclass(self, basedocclass):
        if not self._ptype == DOCGEN:
            raise ValueError, 'basedocclass may only be set for DOCGEN plugins'
        self._basedocclass = basedocclass
    
    def _get_basedocclass(self):
        return self._basedocclass
    
    def _set_paper(self, paper):
        if not self._ptype == DOCGEN:
            raise ValueError, 'paper may only be set for DOCGEN plugins'
        if not isinstance(paper, bool):
            raise ValueError, 'Plugin must have paper=True or False'
        self._paper = paper
    
    def _get_paper(self):
        return self._paper
    
    def _set_style(self, style):
        if not self._ptype == DOCGEN:
            raise ValueError, 'style may only be set for DOCGEN plugins'
        if not isinstance(style, bool):
            raise ValueError, 'Plugin must have style=True or False'
        self._style = style
    
    def _get_style(self):
        return self._style
    
    def _set_extension(self, extension):
        if not (self._ptype == DOCGEN or self._ptype == EXPORT 
                or self._ptype == IMPORT):
            raise ValueError, 'extension may only be set for DOCGEN/EXPORT/'\
                              'IMPORT plugins'
        self._extension = extension
    
    def _get_extension(self):
        return self._extension
    
    basedocclass = property(_get_basedocclass, _set_basedocclass)
    paper = property(_get_paper, _set_paper)
    style = property(_get_style, _set_style)    
    extension = property(_get_extension, _set_extension)
    
    #QUICKREPORT attributes
    def _set_runfunc(self, runfunc):
        if not self._ptype == QUICKREPORT:
            raise ValueError, 'runfunc may only be set for QUICKREPORT plugins'
        self._runfunc = runfunc
    
    def _get_runfunc(self):
        return self._runfunc
    
    runfunc = property(_get_runfunc, _set_runfunc)
    
    #MAPSERVICE attributes
    def _set_mapservice(self, mapservice):
        if not self._ptype == MAPSERVICE:
            raise ValueError, 'mapservice may only be set for MAPSERVICE plugins'
        self._mapservice = mapservice
    
    def _get_mapservice(self):
        return self._mapservice
    
    mapservice = property(_get_mapservice, _set_mapservice)

    #EXPORT attributes
    def _set_export_function(self, export_function):
        if not self._ptype == EXPORT:
            raise ValueError, 'export_function may only be set for EXPORT plugins'
        self._export_function = export_function
    
    def _get_export_function(self):
        return self._export_function
    
    def _set_export_options(self, export_options):
        if not self._ptype == EXPORT:
            raise ValueError, 'export_options may only be set for EXPORT plugins'
        self._export_options = export_options
    
    def _get_export_options(self):
        return self._export_options
    
    def _set_export_options_title(self, export_options_title):
        if not self._ptype == EXPORT:
            raise ValueError, 'export_options_title may only be set for EXPORT plugins'
        self._export_options_title = export_options_title
    
    def _get_export_options_title(self):
        return self._export_options_title

    export_function = property(_get_export_function, _set_export_function)
    export_options = property(_get_export_options, _set_export_options)
    export_options_title = property(_get_export_options_title, 
                                    _set_export_options_title)
    
    #IMPORT attributes
    def _set_import_function(self, import_function):
        if not self._ptype == IMPORT:
            raise ValueError, 'import_function may only be set for IMPORT plugins'
        self._import_function = import_function
    
    def _get_import_function(self):
        return self._import_function
    
    import_function = property(_get_import_function, _set_import_function)

    #GRAMPLET attributes
    def _set_gramplet(self, gramplet):
        if not self._ptype == GRAMPLET:
            raise ValueError, 'gramplet may only be set for GRAMPLET plugins'
        self._gramplet = gramplet
    
    def _get_gramplet(self):
        return self._gramplet
    
    def _set_height(self, height):
        if not self._ptype == GRAMPLET:
            raise ValueError, 'height may only be set for GRAMPLET plugins'
        if not isinstance(height, int):
            raise ValueError, 'Plugin must have height an integer'
        self._height = height
    
    def _get_height(self):
        return self._height
    
    def _set_detached_height(self, detached_height):
        if not self._ptype == GRAMPLET:
            raise ValueError, 'detached_height may only be set for GRAMPLET plugins'
        if not isinstance(detached_height, int):
            raise ValueError, 'Plugin must have detached_height an integer'
        self._detached_height = detached_height
    
    def _get_detached_height(self):
        return self._detached_height
    
    def _set_detached_width(self, detached_width):
        if not self._ptype == GRAMPLET:
            raise ValueError, 'detached_width may only be set for GRAMPLET plugins'
        if not isinstance(detached_width, int):
            raise ValueError, 'Plugin must have detached_width an integer'
        self._detached_width = detached_width
    
    def _get_detached_width(self):
        return self._detached_width

    def _set_expand(self, expand):
        if not self._ptype == GRAMPLET:
            raise ValueError, 'expand may only be set for GRAMPLET plugins'
        if not isinstance(expand, bool):
            raise ValueError, 'Plugin must have expand as a bool'
        self._expand = expand
    
    def _get_expand(self):
        return self._expand
    
    def _set_gramplet_title(self, gramplet_title):
        if not self._ptype == GRAMPLET:
            raise ValueError, 'gramplet_title may only be set for GRAMPLET plugins'
        if not isinstance(gramplet_title, str):
            raise ValueError, 'Plugin must have a string as gramplet_title'
        self._gramplet_title = gramplet_title
    
    def _get_gramplet_title(self):
        return self._gramplet_title

    def _set_help_url(self, help_url):
        if not self._ptype == GRAMPLET:
            raise ValueError, 'help_url may only be set for GRAMPLET plugins'
        self._help_url = help_url

    def _get_help_url(self):
        return self._help_url
    
    gramplet = property(_get_gramplet, _set_gramplet)
    height = property(_get_height, _set_height)
    detached_height = property(_get_detached_height, _set_detached_height)
    detached_width = property(_get_detached_width, _set_detached_width)
    expand = property(_get_expand, _set_expand)
    gramplet_title = property(_get_gramplet_title, _set_gramplet_title)
    help_url = property(_get_help_url, _set_help_url)

    def _set_viewclass(self, viewclass):
        if not self._ptype == VIEW:
            raise ValueError, 'viewclass may only be set for VIEW plugins'
        self._viewclass = viewclass

    def _get_viewclass(self):
        return self._viewclass
  
    def _set_order(self, order):
        if not self._ptype == VIEW:
            raise ValueError, 'order may only be set for VIEW plugins'
        self._order = order

    def _get_order(self):
        return self._order

    viewclass = property(_get_viewclass, _set_viewclass)
    order     = property(_get_order, _set_order)

def newplugin():
    """
    Function to create a new plugindata object, add it to list of 
    registered plugins
    :Returns: a newly created PluginData which is already part of the register
    """
    gpr = PluginRegister.get_instance()
    pgd = PluginData()
    gpr.add_plugindata(pgd)
    return pgd

def register(ptype, **kwargs):
    """
    Convenience function to register a new plugin using a dictionary as input.
    The register functions will call newplugin() function, and use the 
    dictionary kwargs to assign data to the PluginData newplugin() created, 
    as in: plugindata.key = data
    :param ptype: the plugin type, one of REPORT, TOOL, ...
    :param kwargs: dictionary with keys attributes of the plugin, and data 
        the value
    
    :Returns: a newly created PluginData which is already part of the register
        and which has kwargs assigned as attributes
    """
    plg = newplugin()
    plg.ptype = ptype
    for prop in kwargs:
        #check it is a valid attribute with getattr
        getattr(plg, prop)
        #set the value
        setattr(plg, prop, kwargs[prop])
    return plg

#-------------------------------------------------------------------------
#
# PluginRegister
#
#-------------------------------------------------------------------------
class PluginRegister(object):
    """ PluginRegister is a Singleton which holds plugin data
        .. attribute : stable_only
            Bool, include stable plugins only or not. Default True
    """
    __instance = None
    
    def get_instance():
        """ Use this function to get the instance of the PluginRegister """
        if PluginRegister.__instance is None:
            PluginRegister.__instance = 1 # Set to 1 for __init__()
            PluginRegister.__instance = PluginRegister()
        return PluginRegister.__instance
    get_instance = staticmethod(get_instance)
            
    def __init__(self):
        """ This function should only be run once by get_instance() """
        if PluginRegister.__instance is not 1:
            raise Exception("This class is a singleton. "
                            "Use the get_instance() method")
        self.stable_only = True
        if __debug__:
            self.stable_only = False
        self.__plugindata  = []

    def add_plugindata(self, plugindata):
        self.__plugindata.append(plugindata)
        
    def scan_dir(self, dir):
        """
        The dir name will be scanned for plugin registration code, which will
        be loaded in PluginData objects if they satisfy some checks.
        
        :Returns: A list with PluginData objects
        """
        # if the directory does not exist, do nothing
        if not os.path.isdir(dir):
            return []
        
        ext = r".gpr.py"
        extlen = -len(ext)
        pymod = re.compile(r"^(.*)\.py$")
        
        for filename in os.listdir(dir):
            name = os.path.split(filename)[1]
            if not name[extlen:] == ext:
                continue
            lenpd = len(self.__plugindata)
            full_filename = os.path.join(dir, filename)
            local_gettext = get_addon_translator(full_filename).gettext
            try:
                execfile(full_filename,
                   {'_': local_gettext,
                    'newplugin': newplugin,
                    'register': register,
                    'STABLE': STABLE,
                    'UNSTABLE': UNSTABLE,
                    'REPORT': REPORT,
                    'QUICKREPORT': QUICKREPORT,
                    'TOOL': TOOL,
                    'IMPORT': IMPORT,
                    'EXPORT': EXPORT,
                    'DOCGEN': DOCGEN,
                    'GENERAL': GENERAL,
                    'MAPSERVICE': MAPSERVICE,
                    'VIEW': VIEW,
                    'RELCALC': RELCALC,
                    'GRAMPLET': GRAMPLET,
                    'CATEGORY_TEXT': CATEGORY_TEXT,
                    'CATEGORY_DRAW': CATEGORY_DRAW,
                    'CATEGORY_CODE': CATEGORY_CODE,
                    'CATEGORY_WEB': CATEGORY_WEB,
                    'CATEGORY_BOOK': CATEGORY_BOOK,
                    'CATEGORY_GRAPHVIZ': CATEGORY_GRAPHVIZ,
                    'TOOL_DEBUG': TOOL_DEBUG,
                    'TOOL_ANAL': TOOL_ANAL,
                    'TOOL_DBPROC': TOOL_DBPROC,
                    'TOOL_DBFIX': TOOL_DBFIX,
                    'TOOL_REVCTL': TOOL_REVCTL,
                    'TOOL_UTILS': TOOL_UTILS,
                    'VIEW_MISC': VIEW_MISC,
                    'VIEW_PERSON': VIEW_PERSON,
                    'VIEW_REL': VIEW_REL,
                    'VIEW_FAMILY': VIEW_FAMILY,
                    'VIEW_PEDI': VIEW_PEDI,
                    'VIEW_EVENT': VIEW_EVENT,
                    'VIEW_PLACE': VIEW_PLACE,
                    'VIEW_SOURCE': VIEW_SOURCE,
                    'VIEW_REPO': VIEW_REPO,
                    'VIEW_MEDIA': VIEW_MEDIA,
                    'VIEW_NOTE': VIEW_NOTE,
                    'VIEW_GEO': VIEW_GEO,
                    'CATEGORY_QR_MISC': CATEGORY_QR_MISC,
                    'CATEGORY_QR_PERSON': CATEGORY_QR_PERSON,
                    'CATEGORY_QR_FAMILY': CATEGORY_QR_FAMILY,
                    'CATEGORY_QR_EVENT': CATEGORY_QR_EVENT,
                    'CATEGORY_QR_SOURCE': CATEGORY_QR_SOURCE,
                    'CATEGORY_QR_PLACE': CATEGORY_QR_PLACE,
                    'CATEGORY_QR_REPOSITORY': CATEGORY_QR_REPOSITORY,
                    'CATEGORY_QR_NOTE': CATEGORY_QR_NOTE,
                    'CATEGORY_QR_DATE': CATEGORY_QR_DATE,
                    'REPORT_MODE_GUI': REPORT_MODE_GUI, 
                    'REPORT_MODE_BKI': REPORT_MODE_BKI, 
                    'REPORT_MODE_CLI': REPORT_MODE_CLI,
                    'TOOL_MODE_GUI': TOOL_MODE_GUI, 
                    'TOOL_MODE_CLI': TOOL_MODE_CLI,
                    'GRAMPSVERSION': GRAMPSVERSION,
                    'START': START,
                    'END': END,
                   },
                   {})
            except ValueError, msg:
                print _('Failed reading plugin registration %(filename)s') % \
                            {'filename' : filename}
                print msg
                self.__plugindata = self.__plugindata[:lenpd]
            except:
                print _('Failed reading plugin registration %(filename)s') % \
                            {'filename' : filename}
                print "".join(traceback.format_exception(*sys.exc_info()))
                self.__plugindata = self.__plugindata[:lenpd]
            #check if: 
            #  1. plugin exists, if not remove, otherwise set module name
            #  2. plugin not stable, if stable_only=True, remove
            #  3. TOOL_DEBUG only if __debug__ True
            rmlist = []
            ind = lenpd-1
            for plugin in self.__plugindata[lenpd:]:
                ind += 1
                if not plugin.status == STABLE and self.stable_only:
                    rmlist.append(ind)
                    continue
                if plugin.ptype == TOOL and plugin.category == TOOL_DEBUG \
                and not __debug__:
                    rmlist.append(ind)
                    continue
                match = pymod.match(plugin.fname)
                if not match:
                    rmlist.append(ind)
                    print _('Wrong python file %(filename)s in register file '
                            '%(regfile)s')  % {
                               'filename': os.path.join(dir, plugin.fname),
                               'regfile': os.path.join(dir, filename)
                            }
                    continue
                if not os.path.isfile(os.path.join(dir, plugin.fname)):
                    rmlist.append(ind)
                    print _('Python file %(filename)s in register file '
                            '%(regfile)s does not exist')  % {
                               'filename': os.path.join(dir, plugin.fname),
                               'regfile': os.path.join(dir, filename)
                            }
                    continue
                module = match.groups()[0]
                plugin.mod_name = module
                plugin.fpath = dir
            rmlist.reverse()
            for ind in rmlist:
                del self.__plugindata[ind]

    def get_plugin(self, id):
        """Return the PluginData for the plugin with id"""
        for x in self.__plugindata:
            if x.id == id:
                return x
        return None

    def type_plugins(self, ptype):
        """Return a list of PluginData that are of type ptype
        """
        return [x for x in self.__plugindata if x.ptype == ptype]

    def report_plugins(self, gui=True):
        """Return a list of gui or cli PluginData that are of type REPORT
           :param gui: bool, if True then gui plugin, otherwise cli plugin
        """
        if gui:
            return [x for x in self.type_plugins(REPORT) if REPORT_MODE_GUI
                                        in x.report_modes]
        else:
            return [x for x in self.type_plugins(REPORT) if REPORT_MODE_CLI
                                        in x.report_modes]

    def tool_plugins(self, gui=True):
        """Return a list of PluginData that are of type TOOL
        """
        if gui:
            return [x for x in self.type_plugins(TOOL) if TOOL_MODE_GUI
                                        in x.tool_modes]
        else:
            return [x for x in self.type_plugins(TOOL) if TOOL_MODE_CLI
                                        in x.tool_modes]

    
    def bookitem_plugins(self):
        """Return a list of REPORT PluginData that are can be used as bookitem
        """
        return [x for x in self.type_plugins(REPORT) if REPORT_MODE_BKI
                                        in x.report_modes]

    def quickreport_plugins(self):
        """Return a list of PluginData that are of type QUICKREPORT
        """
        return self.type_plugins(QUICKREPORT)

    def import_plugins(self):
        """Return a list of PluginData that are of type IMPORT
        """
        return self.type_plugins(IMPORT)

    def export_plugins(self):
        """Return a list of PluginData that are of type EXPORT
        """
        return self.type_plugins(EXPORT)

    def docgen_plugins(self):
        """Return a list of PluginData that are of type DOCGEN
        """
        return self.type_plugins(DOCGEN)

    def general_plugins(self):
        """Return a list of PluginData that are of type GENERAL
        """
        return self.type_plugins(GENERAL)

    def mapservice_plugins(self):
        """Return a list of PluginData that are of type MAPSERVICE
        """
        return self.type_plugins(MAPSERVICE)

    def view_plugins(self):
        """Return a list of PluginData that are of type VIEW
        """
        return self.type_plugins(VIEW)

    def relcalc_plugins(self):
        """Return a list of PluginData that are of type RELCALC
        """
        return self.type_plugins(RELCALC)

    def gramplet_plugins(self):
        """Return a list of PluginData that are of type GRAMPLET
        """
        return self.type_plugins(GRAMPLET)

    def filter_load_on_reg(self):
        """Return a list of PluginData that have load_on_reg == True
        """
        return [x for x in self.__plugindata if x.load_on_reg == True]
