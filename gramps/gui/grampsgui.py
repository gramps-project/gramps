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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from __future__ import print_function

import sys
import os
import logging
LOG = logging.getLogger(".grampsgui")

#-------------------------------------------------------------------------
#
# GRAMPS Modules
#
#-------------------------------------------------------------------------
from gramps.gen.config import config
from gramps.gen.const import DATA_DIR, IMAGE_DIR
from gramps.gen.constfunc import has_display, win
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.get_translation().gettext

#-------------------------------------------------------------------------
#
# Miscellaneous initialization
#
#-------------------------------------------------------------------------

MIN_PYGOBJECT_VERSION = (3, 3, 2)
PYGOBJ_ERR = False

try:
    #import gnome introspection, part of pygobject
    import gi
    giversion = gi.version_info
except:
    PYGOBJ_ERR = True

if not PYGOBJ_ERR:
    try:
        from gi.repository import GObject
        if not GObject.pygobject_version >= MIN_PYGOBJECT_VERSION :
            PYGOBJ_ERR = True
    except:
        PYGOBJ_ERR = True

if PYGOBJ_ERR:
    print((_("Your pygobject version does not meet the "
             "requirements. At least pygobject "
             "%(major)d.%(feature)d.%(minor)d is needed to"
             " start Gramps with a GUI.\n\n"
             "Gramps will terminate now.") % 
            {'major':MIN_PYGOBJECT_VERSION[0], 
            'feature':MIN_PYGOBJECT_VERSION[1],
            'minor':MIN_PYGOBJECT_VERSION[2]}))
    sys.exit(0)

try:
    gi.require_version('Gtk', '3.0')
    #It is important to import Pango before Gtk, or some things start to go
    #wrong in GTK3 !
    from gi.repository import Pango
    from gi.repository import Gtk, Gdk
except (ImportError, ValueError):
    print((_("Gdk, Gtk or Pango typelib not installed.\n"
             "Install Gnome Introspection, and "
             "pygobject version 3.3.2 or later.\n"
             "Install then instrospection data for Gdk, Gtk and Pango\n\n"
             "Gramps will terminate now.")))
    sys.exit(0)

try:
    import cairo
except ImportError:
    print((_("\ncairo python support not installed. Install cairo for your "
             "version of python\n\n"
             "Gramps will terminate now.")))
    sys.exit(0)

#-------------------------------------------------------------------------
#
# Functions
#
#-------------------------------------------------------------------------

def register_stock_icons ():
    """
    Add the gramps names for its icons (eg gramps-person) to the GTK icon
    factory. This allows all gramps modules to call up the icons by their name
    """
    from .pluginmanager import base_reg_stock_icons

    #iconpath to the base image. The front of the list has highest priority
    if win():
        iconpaths = [
                    (os.path.join(IMAGE_DIR, '48x48'), '.png'),
                    (IMAGE_DIR, '.png'),
                    ]
    else :
        iconpaths = [
                    (os.path.join(IMAGE_DIR, 'scalable'), '.svg'),
                    (IMAGE_DIR, '.svg'), (IMAGE_DIR, '.png'),
                    ]

    #sizes: menu=16, small_toolbar=18, large_toolbar=24,
    #       button=20, dnd=32, dialog=48
    #add to the back of this list to overrule images set at beginning of list
    extraiconsize = [
                    (os.path.join(IMAGE_DIR, '22x22'),
                            Gtk.IconSize.LARGE_TOOLBAR),
                    (os.path.join(IMAGE_DIR, '16x16'),
                            Gtk.IconSize.MENU),
                    (os.path.join(IMAGE_DIR, '22x22'),
                            Gtk.IconSize.BUTTON),
                    ]

    items = [
        ('gramps-db', _('Family Trees'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-address', _('Address'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-attribute', _('Attribute'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        #('gramps-bookmark', _('Bookmarks'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        #('gramps-bookmark-delete', _('Delete bookmark'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-bookmark-new', _('_Add bookmark'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-bookmark-edit', _('Organize Bookmarks'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-config', _('Configure'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-date', _('Date'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-date-edit', _('Edit Date'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-event', _('Events'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-family', _('Family'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-fanchart', _('Fan Chart'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-fanchartdesc', _('Descendant Fan Chart'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-font', _('Font'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-font-color', _('Font Color'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-font-bgcolor', _('Font Background Color'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-gramplet', _('Gramplets'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-geo', _('Geography'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-geo-mainmap', _('Geography'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-geo-altmap', _('Geography'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('geo-show-person', _('GeoPerson'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('geo-show-family', _('GeoFamily'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('geo-show-event', _('GeoEvents'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('geo-show-place', _('GeoPlaces'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-lock', _('Public'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-media', _('Media'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-merge', _('Merge'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-notes', _('Notes'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-parents', _('Parents'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-parents-add', _('Add Parents'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-parents-open', _('Select Parents'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-pedigree', _('Pedigree'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-person', _('Person'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-place', _('Places'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-relation', _('Relationships'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-reports', _('Reports'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-repository', _('Repositories'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-source', _('Sources'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-spouse', _('Add Spouse'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-tag', _('Tag'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-tag-new', _('New Tag'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-tools', _('Tools'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-tree-group', _('Grouped List'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-tree-list', _('List'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-tree-select', _('Select'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-unlock', _('Private'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-view', _('View'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-viewmedia', _('View'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-zoom-in', _('Zoom In'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-zoom-out', _('Zoom Out'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-zoom-fit-width', _('Fit Width'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-zoom-best-fit', _('Fit Page'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ('gramps-citation', _('Citations'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ]
    # the following icons are not yet in new directory structure
    # they should be ported in the near future
    items_legacy = [
         ('gramps-export', _('Export'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
         ('gramps-import', _('Import'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
         ('gramps-undo-history', _('Undo History'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
         ('gramps-url', _('URL'), Gdk.ModifierType.CONTROL_MASK, 0, ''),
        ]

    base_reg_stock_icons(iconpaths, extraiconsize, items+items_legacy)

def _display_welcome_message():
    """
    Display a welcome message to the user.
    """
    if not config.get('behavior.betawarn'):
        from .dialog import WarningDialog
        WarningDialog(
            _('Danger: This is unstable code!'),
            _("This Gramps 3.x-trunk is a development release. "
              "This version is not meant for normal usage. Use "
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
              "<b>BACKUP</b> your existing databases before opening "
              "them with this version, and make sure to export your "
              "data to XML every now and then."))
        config.set('behavior.autoload', False)
#        config.set('behavior.betawarn', True)
        config.set('behavior.betawarn', config.get('behavior.betawarn'))

#-------------------------------------------------------------------------
#
# Main Gramps class
#
#-------------------------------------------------------------------------
class Gramps(object):
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

        register_stock_icons()

        dbstate = DbState()
        self.vm = ViewManager(dbstate, config.get("interface.view-categories"))
        self.vm.init_interface()

        #act based on the given arguments
        ah = ArgHandler(dbstate, argparser, self.vm, self.argerrorfunc,
                        gui=True)
        ah.handle_args_gui()
        if ah.open or ah.imp_db_path:
            # if we opened or imported something, only show the interface
            self.vm.post_init_interface(show_manager=False)
        elif config.get('paths.recent-file') and config.get('behavior.autoload'):
            # if we need to autoload last seen file, do so
            filename = config.get('paths.recent-file')
            if os.path.isdir(filename) and \
                    os.path.isfile(os.path.join(filename, "name.txt")) and \
                    ah.check_db(filename):
                self.vm.post_init_interface(show_manager=False)
                self.vm.open_activate(filename)
            else:
                self.vm.post_init_interface()
        else:
            # open without fam tree loaded
            self.vm.post_init_interface()

        if config.get('behavior.use-tips'):
            TipOfDay(self.vm.uistate)

    def argerrorfunc(self, string):
        from .dialog import ErrorDialog
        """ Show basic errors in argument handling in GUI fashion"""
        ErrorDialog(_("Error parsing arguments"), string)

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
    from .dialog import ErrorDialog
    #handle first existing errors in GUI fashion
    if errors:
        for error in errors:
            ErrorDialog(error[0], error[1])
        Gtk.main_quit()
        sys.exit(1)

    if argparser.errors:
        for error in argparser.errors:
            ErrorDialog(error[0], error[1])
        Gtk.main_quit()
        sys.exit(1)

    # add gui logger
    from .logger import RotateHandler, GtkHandler
    form = logging.Formatter(fmt="%(relativeCreated)d: %(levelname)s: "
                                "%(filename)s: line %(lineno)d: %(message)s")
    # Create the log handlers
    rh = RotateHandler(capacity=20)
    rh.setFormatter(form)
    # Only error and critical log records should
    # trigger the GUI handler.
    gtkh = GtkHandler(rotate_handler=rh)
    gtkh.setFormatter(form)
    gtkh.setLevel(logging.ERROR)
    l = logging.getLogger()
    l.addHandler(rh)
    l.addHandler(gtkh)

    # start GRAMPS, errors stop the gtk loop
    try:
        quit_now = False
        exit_code = 0
        if has_display():
            Gramps(argparser)
        else:
            print("Gramps terminated because of no DISPLAY")
            sys.exit(exit_code)

    except SystemExit as e:
        quit_now = True
        if e.code:
            exit_code = e.code
            LOG.error("Gramps terminated with exit code: %d." \
                      % e.code, exc_info=True)
    except OSError as e:
        quit_now = True
        exit_code = e[0] or 1
        try:
            fn = e.filename
        except AttributeError:
            fn = ""
        LOG.error("Gramps terminated because of OS Error\n" +
            "Error details: %s %s" % (repr(e), fn), exc_info=True)

    except:
        quit_now = True
        exit_code = 1
        LOG.error(_(
    "\nGramps failed to start. Please report a bug about this.\n"
    "This could be because of an error in a (third party) View on startup.\n"
    "To use another view, don't load a family tree, change view, and then load"
    " your family tree.\n"
    "You can also change manually the startup view in the gramps.ini file \n"
    "by changing the last-view parameter.\n"
                   ), exc_info=True)

    if quit_now:
        #stop gtk loop and quit
        Gtk.main_quit()
        sys.exit(exit_code)

    #function finished, return False to stop the timeout_add function calls
    return False

def startgtkloop(errors, argparser):
    """ We start the gtk loop and run the function to start up GRAMPS
    """
    GObject.threads_init()

    GObject.timeout_add(100, __startgramps, errors, argparser, priority=100)
    if os.path.exists(os.path.join(DATA_DIR, "gramps.accel")):
        Gtk.AccelMap.load(os.path.join(DATA_DIR, "gramps.accel"))
    Gtk.main()
