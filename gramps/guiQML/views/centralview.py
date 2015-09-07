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
The main view from where other views are started
"""

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------


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
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Classes
#
#-------------------------------------------------------------------------

class DetailView(QtCore.QObject):
    """
    Data known about a detail view that can be launched
    """
    def __init__(self, name):
        QtCore.QObject.__init__(self)
        self.__name = name

    def _name(self):
        return self.__name

    changed = QtCore.Signal()

    #make Model.Column.property available in QML
    name = QtCore.Property(str, _name, notify=changed)

class DetViewSumModel(QtCore.QAbstractListModel):
    """
    A simple ListModel for the different detailed views
    """
    COLUMNS = ('name', )

    def __init__(self, detviews):
        QtCore.QAbstractListModel.__init__(self)
        self._detviews = detviews
        self.setRoleNames(dict(enumerate(DetViewSumModel.COLUMNS)))

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._detviews)

    def data(self, index, role):
        print('role', role, DetViewSumModel.COLUMNS.index('name'))
        if index.isValid() and role == DetViewSumModel.COLUMNS.index('name'):
            return self._detviews[index.row()]
        return None

#-------------------------------------------------------------------------
#
# CentralView
#
#-------------------------------------------------------------------------

class CentralView(QtCore.QObject):
    """
    Manages family tree list widget
    """
    def __init__(self, dbstate, engine, viewshow):
        """
        The manager is initialised with a dbstate on which GRAMPS is
        working, and the engine to use context from.
        """
        self.dbstate = dbstate
        self.__viewshow = viewshow
        QtCore.QObject.__init__(self)
        self.const = {
            'titlelabel': str("%s" % self.dbstate.db.get_dbname()),
            }
        print(self.const['titlelabel'])
        #there is one DeclarativeEngine for global settings
        self.__build_main_window(engine)

    def __build_main_window(self, engine):
        """
        Builds the QML interface
        """
        parentcontext = engine.rootContext()
        #Create a context for the family tree list
        self.centralviewcontext = QtDeclarative.QDeclarativeContext(parentcontext)
        #Create ListModel to use
        detviews = DetViewSumModel([DetailView('People')])

        #register them in the context
        self.centralviewcontext.setContextProperty('Const', self.const)
        self.centralviewcontext.setContextProperty('CentralView', self)
        self.centralviewcontext.setContextProperty('DetViewSumModel', detviews)

        #create a Component to show
        self.centralview = QtDeclarative.QDeclarativeComponent(engine)
        self.centralview.loadUrl(QtCore.QUrl.fromLocalFile(
                os.path.join(ROOT_DIR, "guiQML", 'views', 'centralview.qml')))
        #and obtain the QObject of it
        self.Qcentralview = self.centralview.create(self.centralviewcontext)

    def show(self, graphicsview, mainwindow):
        """
        Paint the Component on the View and put it in the given mainwindow.
        """
        #scene.addItem(self.Qfamtreeview)
        graphicsview.setRootObject(self.Qcentralview)
        graphicsview.show();
        mainwindow.setCentralWidget(graphicsview)
        mainwindow.show()

    @QtCore.Slot(QtCore.QObject)
    def detviewSelected(self, detview):
        """
        We load the selected family tree
        """
        print('User clicked on:', detview.name)
        #now only Person piece to click on, so start that
        from guiQML.views.personview import QMLPersonList
        self.__viewshow(QMLPersonList)
