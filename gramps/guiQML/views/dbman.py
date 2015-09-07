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
from gramps.gen.const import IMAGE_DIR, ROOT_DIR
from gramps.cli.clidbman import CLIDbManager, NAME_FILE, time_val
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
OPENGL = True

#-------------------------------------------------------------------------
#
# Classes
#
#-------------------------------------------------------------------------

#open_icon = QtGui.QIcon.fromTheme('open')
FAMTREE_ICONPATH = os.path.join(IMAGE_DIR, 'hicolor', '22x22', 'actions',
                                'gramps.png')

class FamTreeWrapper(QtCore.QObject):
    """
    A QObject wrapper
    """
    def __init__(self, thing, dbman):
        QtCore.QObject.__init__(self)
        self.__dbman = dbman
        self.__name = thing[CLIDbManager.IND_NAME]
        self.__path = thing[CLIDbManager.IND_PATH]
        self.__path_namefile = thing[CLIDbManager.IND_PATH_NAMEFILE]
        self.__last_access = thing[CLIDbManager.IND_TVAL_STR]
        self.__use_icon = thing[CLIDbManager.IND_USE_ICON_BOOL]
        self.__icon = thing[CLIDbManager.IND_STOCK_ID]

    changed = QtCore.Signal()
    changed_name = QtCore.Signal()

    def _name(self): return self.__name
    def _path(self): return self.__path
    def _last_access(self): return self.__last_access
    def _use_icon(self): return self.__use_icon
    def _icon(self): return self.__icon

    def _set_name(self, name):
        self.__name = name
        self.__dbman.rename_database(self.__path_namefile, name)
        self.changed_name.emit()

    name = QtCore.Property(str, _name, _set_name, notify=changed_name)
    path = QtCore.Property(str, _path, notify=changed)
    last_access = QtCore.Property(str, _last_access, notify=changed)
    use_icon = QtCore.Property(bool, _use_icon, notify=changed)
    icon = QtCore.Property(str, _icon, notify=changed)

class FamTreeListModel(QtCore.QAbstractListModel):
    """
    A simple ListModel
    """
    COLUMNS = ('name', 'path', 'last_access', 'use_icon', 'icon')

    def __init__(self, famtrees):
        QtCore.QAbstractListModel.__init__(self)
        self._famtrees = famtrees
        self.setRoleNames(dict(enumerate(FamTreeListModel.COLUMNS)))

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._famtrees)

    def data(self, index, role):
        if index.isValid() and role == FamTreeListModel.COLUMNS.index('name'):
            return self._famtrees[index.row()]
        return None

    def append_famtree(self, famtree):
        """
        Append a FamTreeWrapper to the family tree litsmodel
        """
        self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
        self._famtrees.append(famtree)
        self.endInsertRows()

#-------------------------------------------------------------------------
#
# DbManager
#
#-------------------------------------------------------------------------

class DbManager(CLIDbManager, QtCore.QObject):
    """
    Manages family tree list widget
    """
    def __init__(self, dbstate, engine, onselectcallback):
        """
        The manager is initialised with a dbstate on which GRAMPS is
        working, and the engine to use context from.
        """
        self.__busy = False
        self.__onselect = onselectcallback
        QtCore.QObject.__init__(self)
        CLIDbManager.__init__(self, dbstate)
        #constants needed in the QML
        self.const = {
            'titlelabel': "Gramps - %s" % _("Family Trees"),
            'addbtnlbl': _("Add a Family Tree"),
            'famtreeicon': FAMTREE_ICONPATH
            }
        #there is one DeclarativeEngine for global settings
        self.__build_main_window(engine)

    def __build_main_window(self, engine):
        """
        Builds the QML interface
        """
        parentcontext = engine.rootContext()
        #Create a context for the family tree list
        self.famtreecontext = QtDeclarative.QDeclarativeContext(parentcontext)
        #Create ListModel to use
        famtreesQT = [FamTreeWrapper(obj, self) for obj in self.current_names]
        self.famtrees = FamTreeListModel(famtreesQT)

        #register them in the context
        self.famtreecontext.setContextProperty('Const', self.const)
        self.famtreecontext.setContextProperty('DbManager', self)
        self.famtreecontext.setContextProperty('FamTreeListModel', self.famtrees)

        #create a Component to show
        self.famtreeview = QtDeclarative.QDeclarativeComponent(engine)
        self.famtreeview.loadUrl(QtCore.QUrl.fromLocalFile(
                os.path.join(ROOT_DIR, "guiQML", 'views', 'dbman.qml')))
        #and obtain the QObject of it
        self.Qfamtreeview = self.famtreeview.create(self.famtreecontext)

    def show(self, graphicsview, mainwindow):
        """
        Paint the Component on the View and put it in the given mainwindow.
        """
        #scene.addItem(self.Qfamtreeview)
        graphicsview.setRootObject(self.Qfamtreeview)
        graphicsview.show();
        mainwindow.setCentralWidget(graphicsview)
        mainwindow.show()

    @QtCore.Slot(QtCore.QObject)
    def famtreeSelected(self, wrapper):
        """
        We load the selected family tree
        """
        if self.__busy:
            return
        self.__busy = True
        self.__onselect(wrapper._path())
        self.__busy = False

    @QtCore.Slot(QtCore.QObject)
    def addfamtree(self, _):
        """
        We add a family tree
        """
        if self.__busy:
            return
        self.__busy = True
        print('User clicked on:', 'add fam tree')
        new_path, title = self.create_new_db_cli(None)
        path_name = os.path.join(new_path, NAME_FILE)
        (tval, last) = time_val(new_path)
        self.famtrees.append_famtree(FamTreeWrapper([title, new_path, path_name,
                                        last, tval, False, '']))
        self.__busy = False

