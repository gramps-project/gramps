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
The main view
"""

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
OPENGL = True

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
LOG = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# QT modules
#
#-------------------------------------------------------------------------
from PySide import QtCore
from PySide import QtGui
from PySide import QtDeclarative
from PySide import QtOpenGL

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import ROOT_DIR
from gramps.cli.grampscli import CLIManager, CLIDbLoader
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from guiQML.views.dbman import DbManager
from guiQML.questiondialog import ErrorDialog

#-------------------------------------------------------------------------
#
# ViewManager
#
#-------------------------------------------------------------------------

class ViewManager(CLIManager):
    """
    Manages main widget by holding what state it is in.
    """
    def __init__(self, dbstate, user = None):
        """
        The viewmanager is initialised with a dbstate on which GRAMPS is
        working.
        """
        self.__centralview = None
        CLIManager.__init__(self, dbstate, setloader=False, user=user)
        self.db_loader = CLIDbLoader(self.dbstate)
        #there is one DeclarativeEngine for global settings
        self.__build_main_window()
        from .questiondialog import ErrorDialog
        if self.user is None:
            self.user = User(error=ErrorDialog,
                    callback=self.uistate.pulse_progressbar,
                    uistate=self.uistate)

    def __build_main_window(self):
        """
        Builds the QML interface
        """
        self.mainwindow = QtGui.QMainWindow()
        self.mainview = QtDeclarative.QDeclarativeView()
        if OPENGL:
            glw = QtOpenGL.QGLWidget()
            self.mainview.setViewport(glw)
        self.mainview.setResizeMode(QtDeclarative.QDeclarativeView.SizeRootObjectToView)
        self.engine = self.mainview.engine()
        self.engine.rootContext().setBaseUrl(QtCore.QUrl.fromLocalFile(
                            os.path.join(ROOT_DIR, "guiQML")))

        #set up the family tree list to select from
        self.dbman = DbManager(self.dbstate, self.engine, self.load_db)

    def post_init_interface(self):
        """
        Showing the main window is deferred so that
        ArgHandler can work without it always shown
        """
        if not self.dbstate.db.is_open():
            self.__open_dbman(None)
        else:
            self.__open_centralview(None)

    def __open_dbman(self, obj):
        """
        Called when the Open button is clicked, opens the DbManager
        """
        self.dbman.show(self.mainview, self.mainwindow)

    def _errordialog(self, title, errormessage):
        """
        Show the error.
        In the GUI, the error is shown, and a return happens
        """
        ErrorDialog(title, errormessage, parent=self.mainwindow)
        return 1

    def load_db(self, path):
        """
        Load the db and set the interface to the central widget
        """
        self.db_loader.read_file(path)
        self.__open_centralview(None)

    def __open_centralview(self, obj):
        """
        set interface to the central widget
        """
        if not self.__centralview:
            from guiQML.views.centralview import CentralView
            self.__centralview = CentralView(self.dbstate, self.engine,
                            self.open_view)
        self.__centralview.show(self.mainview, self.mainwindow)

    def open_view(self, viewclass, *args):
        """
        set interface to the given view:
        """
        ##we should destroy views that are double
        ##we should do some caching of views so as to move quickly?
        newview = viewclass(self.dbstate, self.engine, *args)
        newview.show(self.mainview, self.mainwindow)
