#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009 Benny Malengier
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

""" This contains the main class corresponding to a running gramps process """

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import sys
import os
import logging
LOG = logging.getLogger(".grampsgui")

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from gramps.gen.config import config
from gramps.gen.const import DATA_DIR, IMAGE_DIR, GTK_GETTEXT_DOMAIN
from gramps.gen.constfunc import has_display, lin
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Miscellaneous initialization
#
#-------------------------------------------------------------------------

MIN_PYGOBJECT_VERSION = (3, 12, 0)
PYGOBJ_ERR = False
MIN_GTK_VERSION = (3, 10)

try:
    #import gnome introspection, part of pygobject
    import gi
    GIVERSION = gi.require_version
except:
    print(_("Your version of gi (gnome-introspection) seems to be too old. "
            "You need a version which has the function 'require_version' "
            "to start Gramps"))
    sys.exit(1)

if not PYGOBJ_ERR:
    try:
        from gi.repository import GObject, GLib
        if not GObject.pygobject_version >= MIN_PYGOBJECT_VERSION:
            PYGOBJ_ERR = True
    except:
        PYGOBJ_ERR = True

if PYGOBJ_ERR:
    print(_("Your pygobject version does not meet the requirements.\n"
            "At least pygobject %(major)d.%(feature)d.%(minor)d "
            "is needed to start Gramps with a GUI.\n\n"
            "Gramps will terminate now."
           ) % {'major'   : MIN_PYGOBJECT_VERSION[0],
                'feature' : MIN_PYGOBJECT_VERSION[1],
                'minor'   : MIN_PYGOBJECT_VERSION[2]})
    sys.exit(1)

try:
    gi.require_version('Pango', '1.0')
    gi.require_version('PangoCairo', '1.0')
    gi.require_version('Gtk', '3.0')
    #It is important to import Pango before Gtk, or some things start to go
    #wrong in GTK3 !
    from gi.repository import Pango, PangoCairo
    from gi.repository import Gtk, Gdk
except (ImportError, ValueError):
    print(_("Gdk, Gtk, Pango or PangoCairo typelib not installed.\n"
            "Install Gnome Introspection, and "
            "pygobject version 3.12 or later.\n"
            "Then install introspection data for Gdk, Gtk, Pango and "
            "PangoCairo\n\n"
            "Gramps will terminate now."))
    sys.exit(1)

GTK_MAJOR = Gtk.get_major_version()
GTK_MINOR = Gtk.get_minor_version()
if (GTK_MAJOR, GTK_MINOR) < MIN_GTK_VERSION:
    print(_("Your Gtk version does not meet the requirements.\n"
            "At least %(major)d.%(minor)d "
            "is needed to start Gramps with a GUI.\n\n"
            "Gramps will terminate now."
           ) % {'major' : MIN_GTK_VERSION[0],
                'minor' : MIN_GTK_VERSION[1]})
    sys.exit(1)

try:
    import cairo
except ImportError:
    print(_("\ncairo python support not installed. "
            "Install cairo for your version of python\n\n"
            "Gramps will terminate now."))
    sys.exit(1)

#-------------------------------------------------------------------------
#
# Functions
#
#-------------------------------------------------------------------------

def _display_welcome_message(parent=None):
    """
    Display a welcome message to the user.
    (This docstring seems very legacy/historical, not accurate.)
    """
    _display_generic_message("master", 'behavior.betawarn', parent=parent)

def _display_generic_message(warning_type, config_key, parent=None):
    """
    Display a generic warning message to the user, with the
    warning_type in it -- if the config_key key is not set

    :param warning_type: the general name of the warning, e.g. "master"
    :type warning_type: str
    :param config_key: name of gramps.ini config key, e.g. "behavior.betawarn"
    :type config_key: str
    """
    if not config.get(config_key):
        from .dialog import WarningDialog
        WarningDialog(
            _('Danger: This is unstable code!'),
            _("This Gramps ('%s') is a development release.\n"
             ) % warning_type +
            _("This version is not meant for normal usage. Use "
              "at your own risk.\n"
              "\n"
              "This version may:\n"
              "1) Work differently than you expect.\n"
              "2) Fail to run at all.\n"
              "3) Crash often.\n"
              "4) Corrupt your data.\n"
              "5) Save data in a format that is incompatible with the "
              "official release.\n"
              "\n"
              "%(bold_start)sBACKUP%(bold_end)s "
              "your existing databases before opening "
              "them with this version, and make sure to export your "
              "data to XML every now and then."
             ) % {'bold_start' : '<b>',
                  'bold_end'   : '</b>'},
            parent=parent)
        config.set('behavior.autoload', False)
        config.set(config_key, True)

def _display_gtk_gettext_message(parent=None):
    """
    Display a GTK-translations-missing message to the user.

    Note: the warning dialog below will likely have wrong stock icons!
    """
    LOG.warning("GTK translations missing, GUI will be broken, "
                "especially for RTL languages!")
    from .dialog import WarningDialog
    WarningDialog(_("Gramps detected "
                    "an incomplete GTK installation"),
                  _("GTK translations for the current language (%(language)s) "
                    "are missing.\n"
                    "%(bold_start)sGramps%(bold_end)s will "
                    "proceed nevertheless.\n"
                    "The GUI will likely be broken "
                    "as a result, especially for RTL languages!\n\n"
                    "See the Gramps README documentation for installation "
                    "prerequisites,\n"
                    "typically located in "
                    "/usr/share/doc/gramps.\n"
                   ) % {'language'   : glocale.lang,
                        'bold_start' : '<b>',
                        'bold_end'   : '</b>'},
                  parent=parent)

def _display_translator_message(parent=None):
    """
    Display a translator-wanted message to the user.
    """
    if config.get('behavior.translator-needed'):
        config.set('behavior.translator-needed', False)
        from gramps.gen.utils.grampslocale import INCOMPLETE_TRANSLATIONS
        language = None
        if glocale.lang in INCOMPLETE_TRANSLATIONS:
            language = glocale.lang
        elif glocale.lang[:2] in INCOMPLETE_TRANSLATIONS:
            language = glocale.lang[:2]
        if language:
            from .dialog import WarningDialog
            from gramps.gen.const import URL_MAILINGLIST
            # we are looking for a translator so leave this in English
            WarningDialog("This Gramps has an incomplete translation",
                          "The translation for the "
                          "current language (%(language)s) is incomplete.\n\n"
                          "%(bold_start)sGramps%(bold_end)s "
                          "will start anyway, but if you would like "
                          "to improve\nGramps by doing some translating, "
                          "please contact us!\n\n"
                          "Subscribe to gramps-devel at\n%(mailing_list_url)s"
                          "\n" % {'language'         : language,
                                  'bold_start'       : '<b>',
                                  'bold_end'         : '</b>',
                                  'mailing_list_url' : URL_MAILINGLIST},
                          parent=parent)

#-------------------------------------------------------------------------
#
# Main Gramps class
#
#-------------------------------------------------------------------------
class Gramps:
    """
    Main class corresponding to a running gramps process.

    There can be only one instance of this class per gramps application
    process. It may spawn several windows and control several databases.
    """

    def __init__(self, argparser):
        from gramps.gen.dbstate import DbState
        from . import viewmanager
        from .viewmanager import ViewManager
        from gramps.cli.arghandler import ArgHandler
        from .tipofday import TipOfDay
        import gettext

        # Append image directory to the theme search path
        theme = Gtk.IconTheme.get_default()
        theme.append_search_path(IMAGE_DIR)

        dbstate = DbState()
        self._vm = ViewManager(dbstate,
                               config.get("interface.view-categories"))

        if (lin()
                and glocale.lang != 'C'
                and not gettext.find(GTK_GETTEXT_DOMAIN)):
            _display_gtk_gettext_message(parent=self._vm.window)

        #_display_welcome_message(parent=self._vm.window)

        _display_translator_message(parent=self._vm.window)

        self._vm.init_interface()

        #act based on the given arguments
        arg_h = ArgHandler(dbstate, argparser, self._vm, self.argerrorfunc,
                           gui=True)
        arg_h.handle_args_gui()
        if arg_h.open or arg_h.imp_db_path:
            # if we opened or imported something, only show the interface
            self._vm.post_init_interface(show_manager=False)
        elif (config.get('paths.recent-file')
              and config.get('behavior.autoload')):
            # if we need to autoload last seen file, do so
            filename = config.get('paths.recent-file')
            if (os.path.isdir(filename)
                    and os.path.isfile(os.path.join(filename, "name.txt"))
                    and arg_h.check_db(filename)):
                self._vm.post_init_interface(show_manager=False)
                self._vm.open_activate(filename)
            else:
                self._vm.post_init_interface()
        else:
            # open without fam tree loaded
            self._vm.post_init_interface()

        if config.get('behavior.use-tips'):
            TipOfDay(self._vm.uistate)

    def argerrorfunc(self, string):
        """ Show basic errors in argument handling in GUI fashion"""
        from .dialog import ErrorDialog
        parent = None
        if hasattr(self, '_vm'):
            if hasattr(self._vm, 'window'):
                parent = self._vm.window
        ErrorDialog(_("Error parsing arguments"), string,
                    parent=parent)

#-------------------------------------------------------------------------
#
# Main startup functions
#
#-------------------------------------------------------------------------

def __startgramps(errors, argparser):
    """
    Main startup function started via GObject.timeout_add
    First action inside the gtk loop
    """
    try:
        from .dialog import ErrorDialog
        #handle first existing errors in GUI fashion
        if errors:
            for error in errors:
                ErrorDialog(error[0], error[1]) # TODO no-parent
            Gtk.main_quit()
            sys.exit(1)

        if argparser.errors:
            for error in argparser.errors:
                ErrorDialog(error[0], error[1]) # TODO no-parent
            Gtk.main_quit()
            sys.exit(1)

        # add gui logger
        from .logger import RotateHandler, GtkHandler
        form = logging.Formatter(
            fmt="%(relativeCreated)d: %(levelname)s: "
                "%(filename)s: line %(lineno)d: %(message)s")
        # Create the log handlers
        rot_h = RotateHandler(capacity=20)
        rot_h.setFormatter(form)
        # Only error and critical log records should
        # trigger the GUI handler.
        gtkh = GtkHandler(rotate_handler=rot_h)
        gtkh.setFormatter(form)
        gtkh.setLevel(logging.ERROR)
        logger = logging.getLogger()
        logger.addHandler(rot_h)
        logger.addHandler(gtkh)

    except:
        #make sure there is a clean exit if there is an error in above steps
        quit_now = True
        exit_code = 1
        LOG.error(_("\nGramps failed to start. "
                    "Please report a bug about this.\n"
                    "This could be because of an error "
                    "in a (third party) View on startup.\n"
                    "To use another view, don't load a Family Tree, "
                    "change view, and then load your Family Tree.\n"
                    "You can also change manually "
                    "the startup view in the gramps.ini file \n"
                    "by changing the last-view parameter.\n"
                   ), exc_info=True)

    # start Gramps, errors stop the gtk loop
    try:
        quit_now = False
        exit_code = 0
        if has_display():
            Gramps(argparser)
        else:
            print(_("Gramps terminated because of no DISPLAY"))
            quit_now = True
            exit_code = 1
    except SystemExit as err:
        quit_now = True
        if err.code:
            exit_code = err.code
            if isinstance(err.code, str):
                LOG.error(err.code, exc_info=False)
            else:
                LOG.error("Gramps terminated with exit code: %d.", err.code,
                          exc_info=False)
    except OSError as err:
        quit_now = True
        exit_code = err.errno or 1
        try:
            fname = err.filename
        except AttributeError:
            fname = ""
        LOG.error("Gramps terminated because of OS Error\n" +
                  "Error details: %s %s", repr(err), fname, exc_info=True)
    except:
        quit_now = True
        exit_code = 1
        LOG.error(_("\nGramps failed to start. "
                    "Please report a bug about this.\n"
                    "This could be because of an error "
                    "in a (third party) View on startup.\n"
                    "To use another view, don't load a Family Tree, "
                    "change view, and then load your Family Tree.\n"
                    "You can also change manually "
                    "the startup view in the gramps.ini file \n"
                    "by changing the last-view parameter.\n"
                   ), exc_info=True)

    if quit_now:
        #stop gtk loop and quit
        Gtk.main_quit()
        sys.exit(exit_code)

    #function finished, return False to stop the timeout_add function calls
    return False

def startgtkloop(errors, argparser):
    """
    We start the gtk loop and run the function to start up Gramps
    """
    GLib.timeout_add(100, __startgramps, errors, argparser, priority=100)
    if os.path.exists(os.path.join(DATA_DIR, "gramps.accel")):
        Gtk.AccelMap.load(os.path.join(DATA_DIR, "gramps.accel"))
    Gtk.main()
