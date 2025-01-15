#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2011       Tim G L Lyons
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
This module provides the base class for plugin registration.
It provides an object containing data about the plugin (version, filename, ...)
and a register for the data of all plugins .
"""

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import logging
import os
import re
import sys
import traceback

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ...version import VERSION as GRAMPSVERSION, VERSION_TUPLE
from ..const import IMAGE_DIR
from ..const import GRAMPS_LOCALE as glocale
from ..utils.requirements import Requirements

_ = glocale.translation.gettext

LOG = logging.getLogger("._manager")

# Fix DEBUG for AIO built with cx_Freeze
DEBUG = __debug__ and not hasattr(sys, "frozen")

# -------------------------------------------------------------------------
#
# PluginData
#
# -------------------------------------------------------------------------

# Development status
UNSTABLE = 0
EXPERIMENTAL = 1
BETA = 2
STABLE = 3
STATUS = [UNSTABLE, EXPERIMENTAL, BETA, STABLE]
STATUSTEXT = {
    UNSTABLE: _("Unstable"),
    EXPERIMENTAL: _("Experimental"),
    BETA: _("Beta"),
    STABLE: _("Stable"),
}

# Intended audience
EVERYONE = 0
EXPERT = 1
DEVELOPER = 2
AUDIENCE = [EVERYONE, EXPERT, DEVELOPER]
AUDIENCETEXT = {EVERYONE: _("Everyone"), EXPERT: _("Expert"), DEVELOPER: _("Developer")}

# possible plugin types
REPORT = 0
QUICKREPORT = 1  # deprecated
QUICKVIEW = 1
TOOL = 2
IMPORT = 3
EXPORT = 4
DOCGEN = 5
GENERAL = 6
MAPSERVICE = 7
VIEW = 8
RELCALC = 9
GRAMPLET = 10
SIDEBAR = 11
DATABASE = 12
RULE = 13
THUMBNAILER = 14
CITE = 15
PTYPE = [
    REPORT,
    QUICKREPORT,
    TOOL,
    IMPORT,
    EXPORT,
    DOCGEN,
    GENERAL,
    MAPSERVICE,
    VIEW,
    RELCALC,
    GRAMPLET,
    SIDEBAR,
    DATABASE,
    RULE,
    THUMBNAILER,
    CITE,
]
PTYPE_STR = {
    REPORT: _("Report"),
    QUICKREPORT: _("Quick view"),
    TOOL: _("Tool"),
    IMPORT: _("Importer"),
    EXPORT: _("Exporter"),
    DOCGEN: _("Document creator"),
    GENERAL: _("Plugin library"),
    MAPSERVICE: _("Map service"),
    VIEW: _("View"),
    RELCALC: _("Relationship calculator"),
    GRAMPLET: _("Gramplet"),
    SIDEBAR: _("Sidebar"),
    DATABASE: _("Database"),
    RULE: _("Rule"),
    THUMBNAILER: _("Thumbnailer"),
    CITE: _("Citation formatter"),
}

# possible report categories
CATEGORY_TEXT = 0
CATEGORY_DRAW = 1
CATEGORY_CODE = 2
CATEGORY_WEB = 3
CATEGORY_BOOK = 4
CATEGORY_GRAPHVIZ = 5
CATEGORY_TREE = 6
REPORT_CAT = [
    CATEGORY_TEXT,
    CATEGORY_DRAW,
    CATEGORY_CODE,
    CATEGORY_WEB,
    CATEGORY_BOOK,
    CATEGORY_GRAPHVIZ,
    CATEGORY_TREE,
]
# possible tool categories
TOOL_DEBUG = -1
TOOL_ANAL = 0
TOOL_DBPROC = 1
TOOL_DBFIX = 2
TOOL_REVCTL = 3
TOOL_UTILS = 4
TOOL_CAT = [TOOL_DEBUG, TOOL_ANAL, TOOL_DBPROC, TOOL_DBFIX, TOOL_REVCTL, TOOL_UTILS]

# possible quickreport categories
CATEGORY_QR_MISC = -1
CATEGORY_QR_PERSON = 0
CATEGORY_QR_FAMILY = 1
CATEGORY_QR_EVENT = 2
CATEGORY_QR_SOURCE = 3
CATEGORY_QR_PLACE = 4
CATEGORY_QR_REPOSITORY = 5
CATEGORY_QR_NOTE = 6
CATEGORY_QR_DATE = 7
CATEGORY_QR_MEDIA = 8
CATEGORY_QR_CITATION = 9
CATEGORY_QR_SOURCE_OR_CITATION = 10

# Modes for generating reports
REPORT_MODE_GUI = 1  # Standalone report using GUI
REPORT_MODE_BKI = 2  # Book Item interface using GUI
REPORT_MODE_CLI = 4  # Command line interface (CLI)
REPORT_MODES = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]

# Modes for running tools
TOOL_MODE_GUI = 1  # Standard tool using GUI
TOOL_MODE_CLI = 2  # Command line interface (CLI)
TOOL_MODES = [TOOL_MODE_GUI, TOOL_MODE_CLI]

# possible view orders
START = 1
END = 2


# -------------------------------------------------------------------------
#
# Functions and classes
#
# -------------------------------------------------------------------------
def myint(string):
    """
    Protected version of int()
    """
    try:
        value = int(string)
    except ValueError:
        value = string
    return value


def version(string_version):
    """
    Return the tuple version of a string version.
    """
    return tuple(myint(x or "0") for x in (f"{string_version}..").split("."))


def valid_plugin_version(plugin_version_string):
    """
    Checks to see if string is a valid version string for this version
    of Gramps.
    """
    if not isinstance(plugin_version_string, str):
        return False
    dots = plugin_version_string.count(".")
    if dots == 1:
        plugin_version = tuple(map(int, plugin_version_string.split(".", 1)))
        return plugin_version == VERSION_TUPLE[:2]
    if dots == 2:
        plugin_version = tuple(map(int, plugin_version_string.split(".", 2)))
        return (
            plugin_version[:2] == VERSION_TUPLE[:2] and plugin_version <= VERSION_TUPLE
        )
    return False


class PluginData:
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
       settings.  MUST be in ASCII, with only "_- ().,'" special characters.
    .. attribute:: name
       A friendly name to call this plugin (normally translated)
    .. attribute:: name_accell
       A friendly name to call this plugin (normally translated), with an
       accellerator present (eg '_Descendant report', with D to be accellerator
       key
    .. attribute:: description
       A friendly description of what the plugin does
    .. attribute:: version
       The version of the plugin
    .. attribute:: status
       The development status of the plugin, UNSTABLE, EXPERIMENTAL, BETA or
       STABLE. UNSTABLE is only visible in development code, not in release
    .. attribute:: audience
       The intended audience of the plugin, EVERYONE, DEVELOPER or EXPERT.
    .. attribute:: fname
       The python file where the plugin implementation can be found
    .. attribute:: fpath
       The python path where the plugin implementation can be found
    .. attribute:: ptype
       The plugin type. One of REPORT , QUICKREPORT, TOOL, IMPORT,
        EXPORT, DOCGEN, GENERAL, MAPSERVICE, VIEW, GRAMPLET, DATABASE, RULE
    .. attribute:: authors
       List of authors of the plugin, default=[]
    .. attribute:: authors_email
       List of emails of the authors of the plugin, default=[]
    .. attribute:: maintainers
       List of maintainers of the plugin, default=[]
    .. attribute:: maintainers_email
       List of emails of the maintainers of the plugin, default=[]
    .. attribute:: supported
       Bool value indicating if the plugin is still supported, default=True
    .. attribute:: load_on_reg
       bool value, if True, the plugin is loaded on Gramps startup. Some
       plugins. Only set this value if for testing you want the plugin to be
       loaded immediately on startup. default=False
    .. attribute: icons
       New stock icons to register. A list of tuples (stock_id, icon_label),
       eg:
            [('gramps_myplugin', _('My Plugin')),
            ('gramps_myplugin_open', _('Open Plugin')]
       The icon directory must contain the directories scalable, 48x48, 22x22
       and 16x16 with the icons, eg:
            scalable/gramps_myplugin.svg
            48x48/gramps_myplugin.png
            22x22/gramps_myplugin.png
    .. attribute: icondir
       The directory to use for the icons. If icondir is not set or None, it
       reverts to the plugindirectory itself.
    .. attribute:: help_url
       The URL where documentation for the plugin can be found
    .. attribute:: requires_mod
       A list of required modules that should be importable using the python
       `import` statement.
    .. attribute:: requires_gi
       A list of (module, version) tuples that specify required modules that
       are reuired to be loaded via the GObject introspection system.
       eg: [('GExiv2', '0.10')]
    .. attribute:: requires_exe
       A list of executables required by the plugin. These are searched for in
       the paths specified in the PATH environment variable.

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
       or the view category a plugin belongs to,
           default=("Miscellaneous", _("Miscellaneous"))

    Attributes for REPORT and TOOL and DOCGEN plugins

    .. attribute:: optionclass
       The class in the module that is the option class

    Attributes for TOOL plugins

    .. attribute:: toolclass
       The class in the module that is the tool class
    .. attribute:: tool_modes
       The tool modes: list of TOOL_MODE_GUI, TOOL_MODE_CLI

    Attributes for DOCGEN plugins

    .. attribute :: docclass
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
       Title to use for the gramplet, default = _('Gramplet')
    .. attribute:: navtypes
       Navigation types that the gramplet is appropriate for, default = []

    Attributes for VIEW plugins

    .. attribute:: viewclass
       A class of type ViewCreator that holds the needed info of the
       view to be created: icon, viewclass that derives from pageview, ...
    .. attribute:: stock_category_icon
       The icon used for the view category if there is none
    .. attribute:: stock_icon
       The icon in the toolbar or sidebar used to select the view

    Attributes for SIDEBAR plugins

    .. attribute:: sidebarclass
       The class that defines the sidebar.
    .. attribute:: menu_label
       A label to use on the seltion menu.

    Attributes for VIEW and SIDEBAR plugins

    .. attribute:: order
       order can be START or END. Default is END. For END, on registering,
       the plugin is appended to the list of plugins. If START, then the
       plugin is prepended. Only set START if you want a plugin to be the
       first in the order of plugins

    Attributes for DATABASE plugins

    .. attribute:: databaseclass
       The class in the module that is the database class
    .. attribute:: reset_system
       Boolean to indicate that the system (sys.modules) should
       be reset.

    Attributes for RULE plugins

    .. attribute:: namespace
       The class (Person, Event, Media, etc.) the rule applies to.
    .. attribute:: ruleclass
       The exact class name of the rule; ex: HasSourceParameter

    Attributes for THUMBNAILER plugins

    .. attribute:: thumbnailer
       The exact class name of the thumbnailer
    """

    def __init__(self):
        # read/write attribute
        self.directory = None
        # base attributes
        self._id = None
        self._name = None
        self._name_accell = None
        self._version = None
        self._gramps_target_version = None
        self._description = None
        self._status = UNSTABLE
        self._audience = EVERYONE
        self._fname = None
        self._fpath = None
        self._ptype = None
        self._authors = []
        self._authors_email = []
        self._maintainers = []
        self._maintainers_email = []
        self._supported = True
        self._load_on_reg = False
        self._icons = []
        self._icondir = None
        self._depends_on = []
        self._requires_mod = []
        self._requires_gi = []
        self._requires_exe = []
        self._include_in_listing = True
        self._help_url = None
        # derived var
        self.mod_name = None
        # RELCALC attr
        self._relcalcclass = None
        self._lang_list = None
        # REPORT attr
        self._reportclass = None
        self._require_active = True
        self._report_modes = [REPORT_MODE_GUI]
        # REPORT and TOOL and GENERAL attr
        self._category = None
        # REPORT and TOOL attr
        self._optionclass = None
        # TOOL attr
        self._toolclass = None
        self._tool_modes = [TOOL_MODE_GUI]
        # DOCGEN attr
        self._paper = True
        self._style = True
        self._extension = ""
        # QUICKREPORT attr
        self._runfunc = None
        # MAPSERVICE attr
        self._mapservice = None
        # EXPORT attr
        self._export_function = None
        self._export_options = None
        self._export_options_title = ""
        # IMPORT attr
        self._import_function = None
        # GRAMPLET attr
        self._gramplet = None
        self._height = 200
        self._detached_height = 300
        self._detached_width = 400
        self._expand = False
        self._gramplet_title = _("Gramplet")
        self._navtypes = []
        self._orientation = None
        # VIEW attr
        self._viewclass = None
        self._stock_category_icon = None
        self._stock_icon = None
        # SIDEBAR attr
        self._sidebarclass = None
        self._menu_label = ""
        # VIEW and SIDEBAR attr
        self._order = END
        # DATABASE attr
        self._databaseclass = None
        self._reset_system = False
        # GENERAL attr
        self._data = []
        self._process = None
        # RULE attr
        self._ruleclass = None
        self._namespace = None
        # THUMBNAILER attr
        self._thumbnailer = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, plugin_id):
        self._id = plugin_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def name_accell(self):
        if self._name_accell is None:
            return self._name
        return self._name_accell

    @name_accell.setter
    def name_accell(self, name):
        self._name_accell = name

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, plugin_version):
        self._version = plugin_version

    @property
    def gramps_target_version(self):
        return self._gramps_target_version

    @gramps_target_version.setter
    def gramps_target_version(self, target_version):
        self._gramps_target_version = target_version

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        if status not in STATUS:
            raise ValueError(f"plugin status cannot be {status}")
        self._status = status

    @property
    def audience(self):
        return self._audience

    @audience.setter
    def audience(self, audience):
        if audience not in AUDIENCE:
            raise ValueError(f"plugin audience cannot be {audience}")
        self._audience = audience

    @property
    def fname(self):
        return self._fname

    @fname.setter
    def fname(self, fname):
        self._fname = fname

    @property
    def fpath(self):
        return self._fpath

    @fpath.setter
    def fpath(self, fpath):
        self._fpath = fpath

    @property
    def ptype(self):
        return self._ptype

    @ptype.setter
    def ptype(self, ptype):
        if ptype not in PTYPE:
            raise ValueError(f"Plugin type cannot be {ptype}")
        if self._ptype is not None:
            raise ValueError("Plugin type may not be changed")
        self._ptype = ptype
        if self._ptype == REPORT:
            self._category = CATEGORY_TEXT
        elif self._ptype == TOOL:
            self._category = TOOL_UTILS
        elif self._ptype == QUICKREPORT:
            self._category = CATEGORY_QR_PERSON
        elif self._ptype == VIEW:
            self._category = ("Miscellaneous", _("Miscellaneous"))
        # if self._ptype == DOCGEN:
        #    self._load_on_reg = True

    @property
    def authors(self):
        return self._authors

    @authors.setter
    def authors(self, authors):
        if not authors or not isinstance(authors, list):
            return
        self._authors = authors

    @property
    def authors_email(self):
        return self._authors_email

    @authors_email.setter
    def authors_email(self, authors_email):
        if not authors_email or not isinstance(authors_email, list):
            return
        self._authors_email = authors_email

    @property
    def maintainers(self):
        return self._maintainers

    @maintainers.setter
    def maintainers(self, maintainers):
        if not maintainers or not isinstance(maintainers, list):
            return
        self._maintainers = maintainers

    @property
    def maintainers_email(self):
        return self._maintainers_email

    @maintainers_email.setter
    def maintainers_email(self, maintainers_email):
        if not maintainers_email or not isinstance(maintainers_email, list):
            return
        self._maintainers_email = maintainers_email

    @property
    def supported(self):
        return self._supported

    @supported.setter
    def supported(self, supported):
        if not isinstance(supported, bool):
            raise ValueError("Plugin must have supported=True or False")
        self._supported = supported

    @property
    def load_on_reg(self):
        return self._load_on_reg

    @load_on_reg.setter
    def load_on_reg(self, load_on_reg):
        if not isinstance(load_on_reg, bool):
            raise ValueError("Plugin must have load_on_reg=True or False")
        self._load_on_reg = load_on_reg

    @property
    def icons(self):
        return self._icons

    @icons.setter
    def icons(self, icons):
        if not isinstance(icons, list):
            raise ValueError("Plugin must have icons as a list")
        self._icons = icons

    @property
    def icondir(self):
        return self._icondir

    @icondir.setter
    def icondir(self, icondir):
        self._icondir = icondir

    @property
    def depends_on(self):
        return self._depends_on

    @depends_on.setter
    def depends_on(self, depends):
        if not isinstance(depends, list):
            raise ValueError("Plugin must have depends_on as a list")
        self._depends_on = depends

    @property
    def requires_mod(self):
        return self._requires_mod

    @requires_mod.setter
    def requires_mod(self, requires):
        if not isinstance(requires, list):
            raise ValueError("Plugin must have requires_mod as a list")
        self._requires_mod = requires

    @property
    def requires_gi(self):
        return self._requires_gi

    @requires_gi.setter
    def requires_gi(self, requires):
        if not isinstance(requires, list):
            raise ValueError("Plugin must have requires_gi as a list")
        self._requires_gi = requires

    @property
    def requires_exe(self):
        return self._requires_exe

    @requires_exe.setter
    def requires_exe(self, requires):
        if not isinstance(requires, list):
            raise ValueError("Plugin must have requires_exe as a list")
        self._requires_exe = requires

    @property
    def include_in_listing(self):
        return self._include_in_listing

    @include_in_listing.setter
    def include_in_listing(self, include):
        if not isinstance(include, bool):
            raise ValueError("Plugin must have include_in_listing as a bool")
        self._include_in_listing = include

    @property
    def help_url(self):
        return self._help_url

    @help_url.setter
    def help_url(self, help_url):
        self._help_url = help_url

    def statustext(self):
        """
        Return status text.
        """
        return STATUSTEXT[self.status]

    # type specific plugin attributes

    # RELCALC attributes
    @property
    def relcalcclass(self):
        return self._relcalcclass

    @relcalcclass.setter
    def relcalcclass(self, relcalcclass):
        if self._ptype != RELCALC:
            raise ValueError("relcalcclass may only be set for RELCALC plugins")
        self._relcalcclass = relcalcclass

    @property
    def lang_list(self):
        return self._lang_list

    @lang_list.setter
    def lang_list(self, lang_list):
        if self._ptype != RELCALC:
            raise ValueError("relcalcclass may only be set for RELCALC plugins")
        self._lang_list = lang_list

    # REPORT attributes
    @property
    def require_active(self):
        return self._require_active

    @require_active.setter
    def require_active(self, require_active):
        if self._ptype != REPORT:
            raise ValueError("require_active may only be set for REPORT plugins")
        if not isinstance(require_active, bool):
            raise ValueError("Report must have require_active=True or False")
        self._require_active = require_active

    @property
    def reportclass(self):
        return self._reportclass

    @reportclass.setter
    def reportclass(self, reportclass):
        if self._ptype != REPORT:
            raise ValueError("reportclass may only be set for REPORT plugins")
        self._reportclass = reportclass

    @property
    def report_modes(self):
        return self._report_modes

    @report_modes.setter
    def report_modes(self, report_modes):
        if self._ptype != REPORT:
            raise ValueError("report_modes may only be set for REPORT plugins")
        if not isinstance(report_modes, list):
            raise ValueError("report_modes must be a list")
        self._report_modes = [x for x in report_modes if x in REPORT_MODES]
        if not self._report_modes:
            raise ValueError("report_modes not a valid list of modes")

    # REPORT or TOOL or QUICKREPORT or GENERAL attributes
    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, category):
        if self._ptype not in [REPORT, TOOL, QUICKREPORT, VIEW, GENERAL]:
            raise ValueError(
                "category may only be set for "
                "REPORT/TOOL/QUICKREPORT/VIEW/GENERAL plugins"
            )
        self._category = category

    # REPORT OR TOOL attributes
    @property
    def optionclass(self):
        return self._optionclass

    @optionclass.setter
    def optionclass(self, optionclass):
        if self._ptype not in [REPORT, TOOL, DOCGEN]:
            raise ValueError(
                "optionclass may only be set for REPORT/TOOL/DOCGEN plugins"
            )
        self._optionclass = optionclass

    # TOOL attributes
    @property
    def toolclass(self):
        return self._toolclass

    @toolclass.setter
    def toolclass(self, toolclass):
        if self._ptype != TOOL:
            raise ValueError("toolclass may only be set for TOOL plugins")
        self._toolclass = toolclass

    @property
    def tool_modes(self):
        return self._tool_modes

    @tool_modes.setter
    def tool_modes(self, tool_modes):
        if self._ptype != TOOL:
            raise ValueError("tool_modes may only be set for TOOL plugins")
        if not isinstance(tool_modes, list):
            raise ValueError("tool_modes must be a list")
        self._tool_modes = [x for x in tool_modes if x in TOOL_MODES]
        if not self._tool_modes:
            raise ValueError("tool_modes not a valid list of modes")

    # DOCGEN attributes
    @property
    def paper(self):
        return self._paper

    @paper.setter
    def paper(self, paper):
        if self._ptype != DOCGEN:
            raise ValueError("paper may only be set for DOCGEN plugins")
        if not isinstance(paper, bool):
            raise ValueError("Plugin must have paper=True or False")
        self._paper = paper

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, style):
        if self._ptype != DOCGEN:
            raise ValueError("style may only be set for DOCGEN plugins")
        if not isinstance(style, bool):
            raise ValueError("Plugin must have style=True or False")
        self._style = style

    @property
    def extension(self):
        return self._extension

    @extension.setter
    def extension(self, extension):
        if self._ptype not in [DOCGEN, EXPORT, IMPORT]:
            raise ValueError(
                "extension may only be set for DOCGEN/EXPORT/IMPORT plugins"
            )
        self._extension = extension

    # QUICKREPORT attributes
    @property
    def runfunc(self):
        return self._runfunc

    @runfunc.setter
    def runfunc(self, runfunc):
        if self._ptype != QUICKREPORT:
            raise ValueError("runfunc may only be set for QUICKREPORT plugins")
        self._runfunc = runfunc

    # MAPSERVICE attributes
    @property
    def mapservice(self):
        return self._mapservice

    @mapservice.setter
    def mapservice(self, mapservice):
        if self._ptype != MAPSERVICE:
            raise ValueError("mapservice may only be set for MAPSERVICE plugins")
        self._mapservice = mapservice

    # EXPORT attributes
    @property
    def export_function(self):
        return self._export_function

    @export_function.setter
    def export_function(self, export_function):
        if self._ptype != EXPORT:
            raise ValueError("export_function may only be set for EXPORT plugins")
        self._export_function = export_function

    @property
    def export_options(self):
        return self._export_options

    @export_options.setter
    def export_options(self, export_options):
        if self._ptype != EXPORT:
            raise ValueError("export_options may only be set for EXPORT plugins")
        self._export_options = export_options

    @property
    def export_options_title(self):
        return self._export_options_title

    @export_options_title.setter
    def export_options_title(self, export_options_title):
        if self._ptype != EXPORT:
            raise ValueError("export_options_title may only be set for EXPORT plugins")
        self._export_options_title = export_options_title

    # IMPORT attributes
    @property
    def import_function(self):
        return self._import_function

    @import_function.setter
    def import_function(self, import_function):
        if self._ptype != IMPORT:
            raise ValueError("import_function may only be set for IMPORT plugins")
        self._import_function = import_function

    # GRAMPLET attributes
    @property
    def gramplet(self):
        return self._gramplet

    @gramplet.setter
    def gramplet(self, gramplet):
        if self._ptype != GRAMPLET:
            raise ValueError("gramplet may only be set for GRAMPLET plugins")
        self._gramplet = gramplet

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        if self._ptype != GRAMPLET:
            raise ValueError("height may only be set for GRAMPLET plugins")
        if not isinstance(height, int):
            raise ValueError("Plugin must have height an integer")
        self._height = height

    @property
    def detached_height(self):
        return self._detached_height

    @detached_height.setter
    def detached_height(self, detached_height):
        if self._ptype != GRAMPLET:
            raise ValueError("detached_height may only be set for GRAMPLET plugins")
        if not isinstance(detached_height, int):
            raise ValueError("Plugin must have detached_height an integer")
        self._detached_height = detached_height

    @property
    def detached_width(self):
        return self._detached_width

    @detached_width.setter
    def detached_width(self, detached_width):
        if self._ptype != GRAMPLET:
            raise ValueError("detached_width may only be set for GRAMPLET plugins")
        if not isinstance(detached_width, int):
            raise ValueError("Plugin must have detached_width an integer")
        self._detached_width = detached_width

    @property
    def expand(self):
        return self._expand

    @expand.setter
    def expand(self, expand):
        if self._ptype != GRAMPLET:
            raise ValueError("expand may only be set for GRAMPLET plugins")
        if not isinstance(expand, bool):
            raise ValueError("Plugin must have expand as a bool")
        self._expand = expand

    @property
    def gramplet_title(self):
        return self._gramplet_title

    @gramplet_title.setter
    def gramplet_title(self, gramplet_title):
        if self._ptype != GRAMPLET:
            raise ValueError("gramplet_title may only be set for GRAMPLET plugins")
        if not isinstance(gramplet_title, str):
            raise ValueError(
                f"gramplet_title is type {type(gramplet_title)}, "
                "string or unicode required"
            )
        self._gramplet_title = gramplet_title

    @property
    def navtypes(self):
        return self._navtypes

    @navtypes.setter
    def navtypes(self, navtypes):
        if self._ptype != GRAMPLET:
            raise ValueError("navtypes may only be set for GRAMPLET plugins")
        self._navtypes = navtypes

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, orientation):
        if self._ptype != GRAMPLET:
            raise ValueError("orientation may only be set for GRAMPLET plugins")
        self._orientation = orientation

    @property
    def viewclass(self):
        return self._viewclass

    @viewclass.setter
    def viewclass(self, viewclass):
        if self._ptype != VIEW:
            raise ValueError("viewclass may only be set for VIEW plugins")
        self._viewclass = viewclass

    @property
    def stock_category_icon(self):
        return self._stock_category_icon

    @stock_category_icon.setter
    def stock_category_icon(self, stock_category_icon):
        if self._ptype != VIEW:
            raise ValueError("stock_category_icon may only be set for VIEW plugins")
        self._stock_category_icon = stock_category_icon

    @property
    def stock_icon(self):
        return self._stock_icon

    @stock_icon.setter
    def stock_icon(self, stock_icon):
        if self._ptype != VIEW:
            raise ValueError("stock_icon may only be set for VIEW plugins")
        self._stock_icon = stock_icon

    # SIDEBAR attributes
    @property
    def sidebarclass(self):
        return self._sidebarclass

    @sidebarclass.setter
    def sidebarclass(self, sidebarclass):
        if self._ptype != SIDEBAR:
            raise ValueError("sidebarclass may only be set for SIDEBAR plugins")
        self._sidebarclass = sidebarclass

    @property
    def menu_label(self):
        return self._menu_label

    @menu_label.setter
    def menu_label(self, menu_label):
        if self._ptype != SIDEBAR:
            raise ValueError("menu_label may only be set for SIDEBAR plugins")
        self._menu_label = menu_label

    # VIEW, SIDEBAR and THUMBNAILER attributes
    @property
    def order(self):
        return self._order

    @order.setter
    def order(self, order):
        if self._ptype not in [VIEW, SIDEBAR, THUMBNAILER]:
            raise ValueError(
                "order may only be set for VIEW/SIDEBAR/THUMBNAILER plugins"
            )
        self._order = order

    # DATABASE attributes
    @property
    def databaseclass(self):
        return self._databaseclass

    @databaseclass.setter
    def databaseclass(self, databaseclass):
        if self._ptype != DATABASE:
            raise ValueError("databaseclass may only be set for DATABASE plugins")
        self._databaseclass = databaseclass

    @property
    def reset_system(self):
        return self._reset_system

    @reset_system.setter
    def reset_system(self, reset_system):
        if self._ptype != DATABASE:
            raise ValueError("reset_system may only be set for DATABASE plugins")
        self._reset_system = reset_system

    # GENERAL attr
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        if self._ptype != GENERAL:
            raise ValueError("data may only be set for GENERAL plugins")
        self._data = data

    @property
    def process(self):
        return self._process

    @process.setter
    def process(self, process):
        if self._ptype != GENERAL:
            raise ValueError("process may only be set for GENERAL plugins")
        self._process = process

    # RULE attr
    @property
    def ruleclass(self):
        return self._ruleclass

    @ruleclass.setter
    def ruleclass(self, data):
        if self._ptype != RULE:
            raise ValueError("ruleclass may only be set for RULE plugins")
        self._ruleclass = data

    @property
    def namespace(self):
        return self._namespace

    @namespace.setter
    def namespace(self, data):
        if self._ptype != RULE:
            raise ValueError("namespace may only be set for RULE plugins")
        self._namespace = data

    # THUMBNAILER attr
    @property
    def thumbnailer(self):
        return self._thumbnailer

    @thumbnailer.setter
    def thumbnailer(self, data):
        if self._ptype != THUMBNAILER:
            raise ValueError("thumbnailer may only be set for THUMBNAILER plugins")
        self._thumbnailer = data


def newplugin():
    """
    Function to create a new plugindata object, add it to list of
    registered plugins

    :returns: a newly created PluginData which is already part of the register
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
    :returns: a newly created PluginData which is already part of the register
              and which has kwargs assigned as attributes
    """
    plg = newplugin()
    plg.ptype = ptype
    for prop, value in kwargs.items():
        # check it is a valid attribute with getattr
        getattr(plg, prop)
        # set the value
        setattr(plg, prop, value)
    return plg


def make_environment(**kwargs):
    """
    Prepare environment.
    """
    env = {
        "newplugin": newplugin,
        "register": register,
        "UNSTABLE": UNSTABLE,
        "EXPERIMENTAL": EXPERIMENTAL,
        "BETA": BETA,
        "STABLE": STABLE,
        "EVERYONE": EVERYONE,
        "DEVELOPER": DEVELOPER,
        "EXPERT": EXPERT,
        "REPORT": REPORT,
        "QUICKREPORT": QUICKREPORT,
        "TOOL": TOOL,
        "IMPORT": IMPORT,
        "EXPORT": EXPORT,
        "DOCGEN": DOCGEN,
        "GENERAL": GENERAL,
        "RULE": RULE,
        "MAPSERVICE": MAPSERVICE,
        "VIEW": VIEW,
        "RELCALC": RELCALC,
        "GRAMPLET": GRAMPLET,
        "SIDEBAR": SIDEBAR,
        "THUMBNAILER": THUMBNAILER,
        "CITE": CITE,
        "CATEGORY_TEXT": CATEGORY_TEXT,
        "CATEGORY_DRAW": CATEGORY_DRAW,
        "CATEGORY_CODE": CATEGORY_CODE,
        "CATEGORY_WEB": CATEGORY_WEB,
        "CATEGORY_BOOK": CATEGORY_BOOK,
        "CATEGORY_GRAPHVIZ": CATEGORY_GRAPHVIZ,
        "CATEGORY_TREE": CATEGORY_TREE,
        "TOOL_DEBUG": TOOL_DEBUG,
        "TOOL_ANAL": TOOL_ANAL,
        "TOOL_DBPROC": TOOL_DBPROC,
        "TOOL_DBFIX": TOOL_DBFIX,
        "TOOL_REVCTL": TOOL_REVCTL,
        "TOOL_UTILS": TOOL_UTILS,
        "CATEGORY_QR_MISC": CATEGORY_QR_MISC,
        "CATEGORY_QR_PERSON": CATEGORY_QR_PERSON,
        "CATEGORY_QR_FAMILY": CATEGORY_QR_FAMILY,
        "CATEGORY_QR_EVENT": CATEGORY_QR_EVENT,
        "CATEGORY_QR_SOURCE": CATEGORY_QR_SOURCE,
        "CATEGORY_QR_CITATION": CATEGORY_QR_CITATION,
        "CATEGORY_QR_SOURCE_OR_CITATION": CATEGORY_QR_SOURCE_OR_CITATION,
        "CATEGORY_QR_PLACE": CATEGORY_QR_PLACE,
        "CATEGORY_QR_MEDIA": CATEGORY_QR_MEDIA,
        "CATEGORY_QR_REPOSITORY": CATEGORY_QR_REPOSITORY,
        "CATEGORY_QR_NOTE": CATEGORY_QR_NOTE,
        "CATEGORY_QR_DATE": CATEGORY_QR_DATE,
        "REPORT_MODE_GUI": REPORT_MODE_GUI,
        "REPORT_MODE_BKI": REPORT_MODE_BKI,
        "REPORT_MODE_CLI": REPORT_MODE_CLI,
        "TOOL_MODE_GUI": TOOL_MODE_GUI,
        "TOOL_MODE_CLI": TOOL_MODE_CLI,
        "DATABASE": DATABASE,
        "GRAMPSVERSION": GRAMPSVERSION,
        "START": START,
        "END": END,
        "IMAGE_DIR": IMAGE_DIR,
    }
    env.update(kwargs)
    return env


# -------------------------------------------------------------------------
#
# PluginRegister
#
# -------------------------------------------------------------------------
class PluginRegister:
    """
    PluginRegister is a Singleton which holds plugin data

    .. attribute : stable_only
        Bool, include stable plugins only or not. Default True
    """

    __instance = None

    @staticmethod
    def get_instance():
        """Use this function to get the instance of the PluginRegister"""
        if PluginRegister.__instance is None:
            PluginRegister.__instance = 1  # Set to 1 for __init__()
            PluginRegister.__instance = PluginRegister()
        return PluginRegister.__instance

    def __init__(self):
        """This function should only be run once by get_instance()"""
        if PluginRegister.__instance != 1:
            raise Exception("This class is a singleton. Use the get_instance() method")
        self.stable_only = True
        if DEBUG:
            self.stable_only = False
        self.__plugindata = []
        self.__id_to_pdata = {}
        self.__req = Requirements()

    def add_plugindata(self, plugindata):
        """This is used to add an entry to the registration list.  The way it
        is used, this entry is not yet filled in, so we cannot use the id to
        add to the __id_to_pdata dict at this time."""
        self.__plugindata.append(plugindata)

    def scan_dir(self, directory, filenames, uistate=None):
        """
        The dir name will be scanned for plugin registration code, which will
        be loaded in :class:`PluginData` objects if they satisfy some checks.

        :returns: A list with :class:`PluginData` objects
        """
        # if the directory does not exist, do nothing
        if not (os.path.isdir(directory) or os.path.islink(directory)):
            return []

        ext = r".gpr.py"
        extlen = -len(ext)
        pymod = re.compile(r"^(.*)\.py$")

        for filename in filenames:
            if not filename[extlen:] == ext:
                continue
            lenpd = len(self.__plugindata)
            full_filename = os.path.join(directory, filename)
            try:
                with open(full_filename, "r", encoding="utf-8") as file_descriptor:
                    stream = file_descriptor.read()
            except Exception as msg:
                print(
                    _("ERROR: Failed reading plugin registration %(filename)s")
                    % {"filename": filename}
                )
                print(msg)
                continue
            if os.path.exists(os.path.join(os.path.dirname(full_filename), "locale")):
                try:
                    local_gettext = glocale.get_addon_translator(full_filename).gettext
                except ValueError:
                    print(
                        _(
                            "WARNING: Plugin %(plugin_name)s has no translation"
                            " for any of your configured languages, using US"
                            " English instead"
                        )
                        % {"plugin_name": filename.split(".")[0]}
                    )
                    local_gettext = glocale.translation.gettext
            else:
                local_gettext = glocale.translation.gettext
            try:
                exec(
                    compile(stream, filename, "exec"),
                    make_environment(_=local_gettext),
                    {"uistate": uistate},
                )
                for pdata in self.__plugindata[lenpd:]:
                    if pdata.id in self.__id_to_pdata:
                        # reloading
                        old = self.__id_to_pdata[pdata.id]
                        self.__plugindata.remove(old)
                        lenpd -= 1
                    self.__id_to_pdata[pdata.id] = pdata
            except ValueError as msg:
                print(
                    _("ERROR: Failed reading plugin registration %(filename)s")
                    % {"filename": filename}
                )
                print(msg)
                self.__plugindata = self.__plugindata[:lenpd]
            except:
                print(
                    _("ERROR: Failed reading plugin registration %(filename)s")
                    % {"filename": filename}
                )
                print("".join(traceback.format_exception(*sys.exc_info())))
                self.__plugindata = self.__plugindata[:lenpd]
            # check if:
            #  1. plugin exists, if not remove, otherwise set module name
            #  2. plugin not stable, if stable_only=True, remove
            #  3. TOOL_DEBUG only if DEBUG True
            rmlist = []
            ind = lenpd - 1
            for plugin in self.__plugindata[lenpd:]:
                # LOG.warning("\nPlugin scanned %s at registration", plugin.id)
                ind += 1
                plugin.directory = directory
                if not valid_plugin_version(plugin.gramps_target_version):
                    print(
                        _(
                            "ERROR: Plugin file %(filename)s has a version of "
                            '"%(gramps_target_version)s" which is invalid for Gramps '
                            '"%(gramps_version)s".'
                            % {
                                "filename": os.path.join(directory, plugin.fname),
                                "gramps_version": GRAMPSVERSION,
                                "gramps_target_version": plugin.gramps_target_version,
                            }
                        )
                    )
                    rmlist.append(ind)
                    continue
                if not self.__req.check_plugin(plugin):
                    rmlist.append(ind)
                    continue
                if plugin.status == UNSTABLE and self.stable_only:
                    rmlist.append(ind)
                    continue
                if plugin.ptype == TOOL and plugin.category == TOOL_DEBUG and not DEBUG:
                    rmlist.append(ind)
                    continue
                if plugin.fname is None:
                    continue
                match = pymod.match(plugin.fname)
                if not match:
                    rmlist.append(ind)
                    print(
                        _(
                            "ERROR: Wrong python file %(filename)s in register file "
                            "%(regfile)s"
                        )
                        % {
                            "filename": os.path.join(directory, plugin.fname),
                            "regfile": os.path.join(directory, filename),
                        }
                    )
                    continue
                if not os.path.isfile(os.path.join(directory, plugin.fname)):
                    rmlist.append(ind)
                    print(
                        _(
                            "ERROR: Python file %(filename)s in register file "
                            "%(regfile)s does not exist"
                        )
                        % {
                            "filename": os.path.join(directory, plugin.fname),
                            "regfile": os.path.join(directory, filename),
                        }
                    )
                    continue
                module = match.groups()[0]
                plugin.mod_name = module
                plugin.fpath = directory
                # LOG.warning("\nPlugin added %s at registration", plugin.id)
            rmlist.reverse()
            for ind in rmlist:
                del self.__id_to_pdata[self.__plugindata[ind].id]
                del self.__plugindata[ind]

    def get_plugin(self, plugin_id):
        """
        Return the :class:`PluginData` for the plugin with id
        """
        assert len(self.__id_to_pdata) == len(self.__plugindata)
        # if len(self.__id_to_pdata) != len(self.__plugindata):
        #     print(len(self.__id_to_pdata), len(self.__plugindata))
        return self.__id_to_pdata.get(plugin_id, None)

    def type_plugins(self, ptype):
        """
        Return a list of :class:`PluginData` that are of type ptype
        """
        return [x for x in self.__plugindata if x.ptype == ptype]

    def report_plugins(self, gui=True):
        """
        Return a list of gui or cli :class:`PluginData` that are of type REPORT

        :param gui: bool, if True then gui plugin, otherwise cli plugin
        """
        if gui:
            return [
                x
                for x in self.type_plugins(REPORT)
                if REPORT_MODE_GUI in x.report_modes
            ]
        return [
            x for x in self.type_plugins(REPORT) if REPORT_MODE_CLI in x.report_modes
        ]

    def tool_plugins(self, gui=True):
        """
        Return a list of :class:`PluginData` that are of type TOOL
        """
        if gui:
            return [x for x in self.type_plugins(TOOL) if TOOL_MODE_GUI in x.tool_modes]
        return [x for x in self.type_plugins(TOOL) if TOOL_MODE_CLI in x.tool_modes]

    def bookitem_plugins(self):
        """
        Return a list of REPORT :class:`PluginData` that are can be used as
        bookitem
        """
        return [
            x for x in self.type_plugins(REPORT) if REPORT_MODE_BKI in x.report_modes
        ]

    def quickreport_plugins(self):
        """
        Return a list of :class:`PluginData` that are of type QUICKREPORT
        """
        return self.type_plugins(QUICKREPORT)

    def import_plugins(self):
        """
        Return a list of :class:`PluginData` that are of type IMPORT
        """
        return self.type_plugins(IMPORT)

    def export_plugins(self):
        """
        Return a list of :class:`PluginData` that are of type EXPORT
        """
        return self.type_plugins(EXPORT)

    def docgen_plugins(self):
        """
        Return a list of :class:`PluginData` that are of type DOCGEN
        """
        return self.type_plugins(DOCGEN)

    def general_plugins(self, category=None):
        """
        Return a list of :class:`PluginData` that are of type GENERAL
        """
        plugins = self.type_plugins(GENERAL)
        if category:
            return [plugin for plugin in plugins if plugin.category == category]
        return plugins

    def mapservice_plugins(self):
        """
        Return a list of :class:`PluginData` that are of type MAPSERVICE
        """
        return self.type_plugins(MAPSERVICE)

    def view_plugins(self):
        """
        Return a list of :class:`PluginData` that are of type VIEW
        """
        return self.type_plugins(VIEW)

    def relcalc_plugins(self):
        """
        Return a list of :class:`PluginData` that are of type RELCALC
        """
        return self.type_plugins(RELCALC)

    def gramplet_plugins(self):
        """
        Return a list of :class:`PluginData` that are of type GRAMPLET
        """
        return self.type_plugins(GRAMPLET)

    def sidebar_plugins(self):
        """
        Return a list of :class:`PluginData` that are of type SIDEBAR
        """
        return self.type_plugins(SIDEBAR)

    def database_plugins(self):
        """
        Return a list of :class:`PluginData` that are of type DATABASE
        """
        return self.type_plugins(DATABASE)

    def rule_plugins(self):
        """
        Return a list of :class:`PluginData` that are of type RULE
        """
        return self.type_plugins(RULE)

    def thumbnailer_plugins(self):
        """
        Return a list of :class:`PluginData` that are of type THUMBNAILER
        """
        return self.type_plugins(THUMBNAILER)

    def cite_plugins(self):
        """
        Return a list of :class:`PluginData` that are of type CITE
        """
        return self.type_plugins(CITE)

    def filter_load_on_reg(self):
        """
        Return a list of :class:`PluginData` that have load_on_reg == True
        """
        return [x for x in self.__plugindata if x.load_on_reg is True]
