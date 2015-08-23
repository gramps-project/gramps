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
Some often needed dialogs
"""

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import sys

#-------------------------------------------------------------------------
#
# QT modules
#
#-------------------------------------------------------------------------
from PySide.QtCore import *
from PySide.QtGui import *

#-------------------------------------------------------------------------
#
# Classes for the Dialogs
#
#-------------------------------------------------------------------------
class ErrorDialog(QDialog):
    def __init__(self, msg1, msg2="", parent=None):
        super(ErrorDialog, self).__init__(parent)
        self.setWindowTitle("%s - Gramps" % msg1)
        lbl1 = QLabel(msg1)
        lbl2 = QLabel(msg2)
        layout = QVBoxLayout()
        layout.addWidget(lbl1)
        layout.addWidget(lbl2)
        # Set dialog layout
        self.setLayout(layout)
        self.setMinimumSize(350,300)
        self.show()

def run_dialog_standalone(dlgclass, *args, **keywords):
    app = QApplication(sys.argv)
    QObject.connect(app, SIGNAL('lastWindowClosed()'), app, SLOT('quit()'))

    win = dlgclass(*args, **keywords)
    app.exec_()
