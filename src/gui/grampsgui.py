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
import sys
import os
from gen.ggettext import gettext as _
import logging
LOG = logging.getLogger(".grampsgui")

#-------------------------------------------------------------------------
#
# pygtk
#
#-------------------------------------------------------------------------
try:
    import pygtk
    pygtk.require('2.0')
except ImportError:
    pass

#-------------------------------------------------------------------------
#
# Miscellaneous initialization
#
#-------------------------------------------------------------------------
import gtk
import gobject

#-------------------------------------------------------------------------
#
# GRAMPS Modules
#
#-------------------------------------------------------------------------
from gen.config import config
from gen.const import DATA_DIR, IMAGE_DIR
from gen.constfunc import has_display, win

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
    from gui.pluginmanager import base_reg_stock_icons

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
                            gtk.ICON_SIZE_LARGE_TOOLBAR),
                    (os.path.join(IMAGE_DIR, '16x16'),
                            gtk.ICON_SIZE_MENU),
                    (os.path.join(IMAGE_DIR, '22x22'),
                            gtk.ICON_SIZE_BUTTON),
                    ]

    items = [
        ('gramps-db', _('Family Trees'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-address', _('Address'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-attribute', _('Attribute'), gtk.gdk.CONTROL_MASK, 0, ''),
        #('gramps-bookmark', _('Bookmarks'), gtk.gdk.CONTROL_MASK, 0, ''),
        #('gramps-bookmark-delete', _('Delete bookmark'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-bookmark-new', _('_Add bookmark'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-bookmark-edit', _('Organize Bookmarks'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-config', _('Configure'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-date', _('Date'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-date-edit', _('Edit Date'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-event', _('Events'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-family', _('Family'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-fanchart', _('Fan Chart'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-font', _('Font'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-font-color', _('Font Color'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-font-bgcolor', _('Font Background Color'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-gramplet', _('Gramplets'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-geo', _('Geography'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-geo-mainmap', _('Geography'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-geo-altmap', _('Geography'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('geo-show-person', _('GeoPerson'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('geo-show-family', _('GeoFamily'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('geo-show-event', _('GeoEvents'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('geo-show-place', _('GeoPlaces'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-lock', _('Public'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-media', _('Media'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-merge', _('Merge'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-notes', _('Notes'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-parents', _('Parents'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-parents-add', _('Add Parents'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-parents-open', _('Select Parents'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-pedigree', _('Pedigree'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-person', _('Person'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-place', _('Places'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-relation', _('Relationships'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-reports', _('Reports'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-repository', _('Repositories'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-source', _('Sources'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-spouse', _('Add Spouse'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-tag', _('Tag'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-tag-new', _('New Tag'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-tools', _('Tools'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-tree-group', _('Grouped List'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-tree-list', _('List'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-tree-select', _('Select'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-unlock', _('Private'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-view', _('View'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-viewmedia', _('View'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-zoom-in', _('Zoom In'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-zoom-out', _('Zoom Out'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-zoom-fit-width', _('Fit Width'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-zoom-best-fit', _('Fit Page'), gtk.gdk.CONTROL_MASK, 0, ''),
        ('gramps-citation', _('Citations'), gtk.gdk.CONTROL_MASK, 0, ''),
        ]
    # the following icons are not yet in new directory structure
    # they should be ported in the near future
    items_legacy = [
         ('gramps-export', _('Export'), gtk.gdk.CONTROL_MASK, 0, ''),
         ('gramps-import', _('Import'), gtk.gdk.CONTROL_MASK, 0, ''),
         ('gramps-undo-history', _('Undo History'), gtk.gdk.CONTROL_MASK, 0, ''),
         ('gramps-url', _('URL'), gtk.gdk.CONTROL_MASK, 0, ''),
        ]

    base_reg_stock_icons(iconpaths, extraiconsize, items+items_legacy)

def _display_welcome_message():
    """
    Display a welcome message to the user.
    """
    if not config.get('behavior.betawarn'):
        from gui.dialog import WarningDialog
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
        from gen.dbstate import DbState
        from viewmanager import ViewManager
        from cli.arghandler import ArgHandler
        from gui.tipofday import TipOfDay

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
        from gui.dialog import ErrorDialog
        """ Show basic errors in argument handling in GUI fashion"""
        ErrorDialog(_("Error parsing arguments"), string)

#-------------------------------------------------------------------------
#
# Main startup functions
#
#-------------------------------------------------------------------------

def __startgramps(errors, argparser):
    """
    Main startup function started via gobject.timeout_add
    First action inside the gtk loop
    """
    from gui.dialog import ErrorDialog
    #handle first existing errors in GUI fashion
    if errors:
        ErrorDialog(errors[0], errors[1])
        gtk.main_quit()
        sys.exit(1)

    if argparser.errors:
        ErrorDialog(argparser.errors[0], argparser.errors[1])
        gtk.main_quit()
        sys.exit(1)

    # add gui logger
    from gui.logger import RotateHandler, GtkHandler
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

    except SystemExit, e:
        quit_now = True
        if e.code:
            exit_code = e.code
            LOG.error("Gramps terminated with exit code: %d." \
                      % e.code, exc_info=True)
    except OSError, e:
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
        LOG.error("Gramps failed to start.", exc_info=True)

    if quit_now:
        #stop gtk loop and quit
        gtk.main_quit()
        sys.exit(exit_code)

    #function finished, return False to stop the timeout_add function calls
    return False

def startgtkloop(errors, argparser):
    """ We start the gtk loop and run the function to start up GRAMPS
    """
    gobject.threads_init()

    gobject.timeout_add(100, __startgramps, errors, argparser, priority=100)
    if os.path.exists(os.path.join(DATA_DIR, "gramps.accel")):
        gtk.accel_map_load(os.path.join(DATA_DIR, "gramps.accel"))
    gtk.main()
