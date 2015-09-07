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
The listview with all people in the database
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
from gramps.gen.const import ROOT_DIR
from gramps.gui.views.treemodels import conv_unicode_tosrtkey
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.lib import Name
##TODO: follow must be refractored so as not to require GTK
from gramps.gui.views.treemodels.flatbasemodel import FlatNodeMap

#-------------------------------------------------------------------------
#
# Classes
#
#-------------------------------------------------------------------------

## Copied from gui/views/models/peoplemodel, we need a GTK independent base!
COLUMN_NAME   = 3

class QMLPerson(QtCore.QObject):
    """
    Person object encapsulated for QML
    We only store handle and ref to database, obtain data from db as needed
    """
    def __init__(self, db, personhandle):
        QtCore.QObject.__init__(self)
        self.__handle = personhandle
        self.__db = db

    def _name(self):
        return name_displayer.display(self.__db.get_person_from_handle(self.__handle))

    #dummy signal for things that change must not be tracked
    dummychanged = QtCore.Signal()

    #make Model.Column.property available in QML
    name = QtCore.Property(str, _name, notify=dummychanged)

class QMLPersonListModel(QtCore.QAbstractListModel):
    """
    A simple ListModel for the People in the database
    """
    ROLE_NAME_COL = 0
    COLUMNS = ((ROLE_NAME_COL, 'name'), )

    def __init__(self, db):
        QtCore.QAbstractListModel.__init__(self)
        self.__db = db
        self.gen_cursor = db.get_person_cursor
        self.sort_func = self.sort_name
        self.node_map = FlatNodeMap()
        self._reverse = False
        #build node map with all peopls
        allkeys = self.sort_keys()
        ident = True
        dlist = allkeys
        self.node_map.set_path_map(dlist, allkeys, identical=ident,
                                   reverse=self._reverse)

        #every column has a role from 0 to nrcol-1, and name as in COLUMNS
        self.setRoleNames(dict(QMLPersonListModel.COLUMNS))
        #we create an array with all the QMLPerson that we need so
        #that we can match a rowindex with correct QMLPerson
        self._qmlpersons = []
        for _, handle in self.node_map.full_srtkey_hndl_map():
            self._qmlpersons.append(QMLPerson(self.__db, handle))

    def sort_keys(self):
        """
        Return the (sort_key, handle) list of all data that can maximally
        be shown.
        This list is sorted ascending, via localized string sort.
        conv_unicode_tosrtkey which uses strxfrm, which is apparently
        broken in Win ?? --> they should fix base lib, we need strxfrm, fix it
        in the Utils module.
        """
        # use cursor as a context manager
        with self.gen_cursor() as cursor:
            #loop over database and store the sort field, and the handle
            return sorted((list(map(conv_unicode_tosrtkey,
                           self.sort_func(data))), key) for key, data in cursor)

    def sort_name(self, data):
        n = Name()
        n.unserialize(data[COLUMN_NAME])
        return (n.get_primary_surname().get_surname(), n.get_first_name())

    def rowCount(self, parent=QtCore.QModelIndex()):
        return self.__db.get_number_of_people()

    def data(self, index, role):
        """
        Obtain QMLPerson to show. Role is a number that corresponds to a column,
        different columns can obtain data from different objects
        """
        if index.isValid() and role <= QMLPersonListModel.ROLE_NAME_COL:
            return self._qmlpersons[index.row()]
        return None

#-------------------------------------------------------------------------
#
# CentralView
#
#-------------------------------------------------------------------------

class QMLPersonList(QtCore.QObject):
    """
    Manages family tree list widget
    """
    def __init__(self, dbstate, engine):
        """
        The manager is initialised with a dbstate on which GRAMPS is
        working, and the engine to use context from.
        """
        self.dbstate = dbstate
        QtCore.QObject.__init__(self)
        self.const = {
            'titlelabel': "%s" % self.dbstate.db.get_dbname(),
            }
        #there is one DeclarativeEngine for global settings
        self.__build_main_window(engine)

    def __build_main_window(self, engine):
        """
        Builds the QML interface
        """
        parentcontext = engine.rootContext()
        #Create a context for the family tree list
        self.qmlpersonlistcontext = QtDeclarative.QDeclarativeContext(parentcontext)
        #Create ListModel to use
        personlistmodel = QMLPersonListModel(self.dbstate.db)

        #register them in the context
        self.qmlpersonlistcontext.setContextProperty('Const', self.const)
        self.qmlpersonlistcontext.setContextProperty('QMLPersonList', self)
        self.qmlpersonlistcontext.setContextProperty('QMLPersonListModel', personlistmodel)

        #create a Component to show
        self.qmlpersonlist = QtDeclarative.QDeclarativeComponent(engine)
        self.qmlpersonlist.loadUrl(QtCore.QUrl.fromLocalFile(
                os.path.join(ROOT_DIR, "guiQML", 'views', 'peopleview.qml')))
        #and obtain the QObject of it
        self.Qpersonlist = self.qmlpersonlist.create(self.qmlpersonlistcontext)

    def show(self, graphicsview, mainwindow):
        """
        Paint the Component on the View and put it in the given mainwindow.
        """
        #scene.addItem(self.Qfamtreeview)
        graphicsview.setRootObject(self.Qpersonlist)
        graphicsview.show();
        mainwindow.setCentralWidget(graphicsview)
        mainwindow.show()

    @QtCore.Slot(QtCore.QObject)
    def detailsSelected(self, qmlperson):
        """
        We load the selected family tree
        """
        print('User clicked on:', qmlperson.name)
