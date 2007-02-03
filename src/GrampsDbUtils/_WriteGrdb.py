#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2006  Donald N. Allingham
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

# Written by Alex Roitman

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import os
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from _GrampsBSDDB import GrampsBSDDB
from QuestionDialog import ErrorDialog
from _DbUtils import db_copy

#-------------------------------------------------------------------------
#
# Importing data into the currently open database. 
#
#-------------------------------------------------------------------------
def cli_callback(val):
    pass

def exportData(database, filename, person=None, callback=None, cl=False):
    
    if callback == None:
        callback = cli_callback

    filename = os.path.normpath(filename)
    new_database = GrampsBSDDB()
    try:
        new_database.load(filename,callback)
    except:
        if cl:
            print "Error: %s could not be opened. Exiting." % filename
        else:
            ErrorDialog(_("%s could not be opened") % filename)
        return
    
    # copy all data from new_database to database
    db_copy(database,new_database,callback)

    new_database.close()
