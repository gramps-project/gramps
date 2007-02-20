#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

"Import from GEDCOM"

import os
import gtk

import Errors
from _GedcomParse import GedcomParser, StageOne
from QuestionDialog import ErrorDialog
from bsddb import db


#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def importData(database, filename, callback=None, use_trans=False):

    try:
        ifile = open(filename, "r")
    except IOError:
        return

    ansel = False
    gramps = False
    for index in range(50):
        line = ifile.readline().split()
        if len(line) == 0:
            break
        if len(line) > 2 and line[1][0:4] == 'CHAR' and line[2] == "ANSEL":
            ansel = True
        if len(line) > 2 and line[1][0:4] == 'SOUR' and line[2] == "GRAMPS":
            gramps = True
    ifile.close()

    if not gramps and ansel:
        glade_file = "%s/gedcomimport.glade" % os.path.dirname(__file__)
        top = gtk.glade.XML(glade_file, 'encoding','gramps')
        code = top.get_widget('codeset')
        code.set_active(0)
        dialog = top.get_widget('encoding')
        dialog.run()
        code_set = code.get_active()
        dialog.destroy()
    else:
        code_set = None
    import2(database, filename, callback, code_set, use_trans)
        

def import2(database, filename, callback, code_set, use_trans):
    # add some checking here
    import time
    t = time.time()
    try:
        ifile = open(filename,"rU")
        np = StageOne(ifile)
	np.parse()
	print np.get_encoding()
	ifile.seek(0)
        gedparse = GedcomParser(database, ifile, filename, callback, np)
    except IOError, msg:
        ErrorDialog(_("%s could not be opened\n") % filename, str(msg))
        return


    if database.get_number_of_people() == 0:
        use_trans = False

    try:
        read_only = database.readonly
        database.readonly = False
        close = gedparse.parse_gedcom_file(use_trans)
        database.readonly = read_only
        ifile.close()
    except IOError, msg:
        msg = _("%s could not be opened\n") % filename
        ErrorDialog(msg, str(msg))
        return
    except db.DBSecondaryBadError, msg:
        WarningDialog(_('Database corruption detected'),
                      _('A problem was detected with the database. Please '
                        'run the Check and Repair Database tool to fix the '
                        'problem.'))
        return
    except Errors.GedcomError, msg:
        ErrorDialog(_('Error reading GEDCOM file'), str(msg))
        return
    print time.time()-t

def import_from_string(database, text, callback, code_set, use_trans):
    # add some checking here

    from cStringIO import StringIO

    ifile = StringIO(text)

    try:
        np = NoteParser(ifile, False, code_set)
        ifile.seek(0)
        gedparse = GedcomParser(database, ifile, "inline-string", callback, 
                                code_set, np.get_map(), np.get_lines(), 
                                np.get_persons())
    except IOError, msg:
        ErrorDialog(_("%s could not be opened\n") % "inline-string", str(msg))
        return

    if database.get_number_of_people() == 0:
        use_trans = False

    try:
        read_only = database.readonly
        database.readonly = False
        gedparse.parse_gedcom_file(use_trans)
        database.readonly = read_only
        ifile.close()
    except IOError, msg:
        msg = _("%s could not be opened\n") % 'inline-string'
        ErrorDialog(msg, str(msg))
        return
    except db.DBSecondaryBadError, msg:
        WarningDialog(_('Database corruption detected'),
                      _('A problem was detected with the database. Please '
                        'run the Check and Repair Database tool to fix the '
                        'problem.'))
        return
    except Errors.GedcomError, msg:
        ErrorDialog(_('Error reading GEDCOM file'), str(msg))
        return

