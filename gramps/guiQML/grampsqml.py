#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Benny Malengier
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#

"""
main file to start the QML application
"""
#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import sys, os

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".grampsqml")

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.constfunc import has_display
from gramps.gen.config import config

#-------------------------------------------------------------------------
#
# Main Gramps class
#
#-------------------------------------------------------------------------
class GrampsQML(object):
    """
    Main class corresponding to a running gramps process.

    There can be only one instance of this class per gramps application
    process. It may spawn several windows and control several databases.
    """

    def __init__(self, argparser):
        from gramps.gen.dbstate import DbState
        from guiQML.viewmanager import ViewManager
        from gramps.cli.arghandler import ArgHandler

        from PySide import QtGui
        self.app = QtGui.QApplication(sys.argv)
        dbstate = DbState()
        self.vm = ViewManager(dbstate)

        #act based on the given arguments
        ah = ArgHandler(dbstate, argparser, self.vm, self.argerrorfunc,
                        gui=True)
        ah.handle_args_gui()
        if ah.open or ah.imp_db_path:
            # if we opened or imported something, only show the interface
            self.vm.post_init_interface()
        elif config.get('paths.recent-file') and config.get('behavior.autoload'):
            # if we need to autoload last seen file, do so
            filename = config.get('paths.recent-file')
            if os.path.isdir(filename) and \
                    os.path.isfile(os.path.join(filename, "name.txt")) and \
                    ah.check_db(filename):
                self.vm.open_activate(filename)
                self.vm.post_init_interface()
            else:
                self.vm.post_init_interface()
        else:
            # open without fam tree loaded
            self.vm.post_init_interface()

        #start the QT loop
        self.app.exec_()

    def argerrorfunc(self, string):
        from guiQML.questiondialog import ErrorDialog
        """ Show basic errors in argument handling in GUI fashion"""
        ErrorDialog(_("Error parsing arguments"), string)

def startqml(errors, argparser):
    """
    Main startup function started via GObject.timeout_add
    First action inside the gtk loop
    """
    from guiQML.questiondialog import ErrorDialog, run_dialog_standalone

    #handle first existing errors in GUI fashion
    if errors:
        run_dialog_standalone(ErrorDialog,errors[0], errors[1])
        sys.exit()

    if argparser.errors:
        run_dialog_standalone(ErrorDialog, argparser.errors[0],
                              argparser.errors[1])
        sys.exit()

    # add gui logger
    from gui.logger import RotateHandler
    form = logging.Formatter(fmt="%(relativeCreated)d: %(levelname)s: "
                                "%(filename)s: line %(lineno)d: %(message)s")
    # Create the log handlers
    rh = RotateHandler(capacity=20)
    rh.setFormatter(form)
    # Only error and critical log records should
    # trigger the GUI handler.
    #qmlh = QMLHandler(rotate_handler=rh)
    #qmlh.setFormatter(form)
    #qmlh.setLevel(logging.ERROR)
    l = logging.getLogger()
    l.addHandler(rh)
    #l.addHandler(gmlh)

    # start GRAMPS, errors stop the gtk loop
    try:
        quit_now = False
        openGL = True
        exit_code = 0
        if has_display():
            GrampsQML(argparser)
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
        LOG.error("Gramps failed to start.", exc_info=True)

    if quit_now:
        #quit
        sys.exit(exit_code)

    #function finished, return False to stop the timeout_add function calls
    return False
