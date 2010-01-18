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

# $Id:_ReadGedcom.py 9912 2008-01-22 09:17:46Z acraphae $

"Import from GEDCOM"

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gen.ggettext import gettext as _

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".GedcomImport")

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import Errors
from QuestionDialog import ErrorDialog, DBErrorDialog
from glade import Glade
from libmixin import DbMixin
import libgedcom

try:
    import config
    DEFAULT_SOURCE = config.get('preferences.default-source')
except ImportError:
    LOG.warn("No Config module available using defaults.")
    DEFAULT_SOURCE = False
    
#-------------------------------------------------------------------------
#
# importData
#
#-------------------------------------------------------------------------
def importData(database, filename, callback=None):
    """
    Try to handle ANSEL encoded files that are not really ANSEL encoded
    """

    if DbMixin not in database.__class__.__bases__:
        database.__class__.__bases__ = (DbMixin,) +  \
                                        database.__class__.__bases__

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
        top = Glade()
        code = top.get_object('codeset')
        code.set_active(0)
        dialog = top.toplevel
        dialog.run()
        enc = ['ANSEL', 'ANSEL', 'ANSI', 'ASCII', 'UTF-8']
        code_set = enc[ code.get_active()]
        dialog.destroy()
    else:
        code_set = ""

    assert(isinstance(code_set, basestring))

    try:
        ifile = open(filename, "rU")
        stage_one = libgedcom.GedcomStageOne(ifile)
        stage_one.parse()

        if code_set:
            stage_one.set_encoding(code_set)
        ifile.seek(0)
        gedparse = libgedcom.GedcomParser(database, ifile, filename, callback, 
                                          stage_one, DEFAULT_SOURCE)
    except IOError, msg:
        ErrorDialog(_("%s could not be opened\n") % filename, str(msg))
        return
    except Errors.GedcomError, msg:
        ErrorDialog(_("Invalid GEDCOM file"), 
                    _("%s could not be imported") % filename + "\n" + str(msg))
        return

    try:
        read_only = database.readonly
        database.readonly = False
        gedparse.parse_gedcom_file(False)
        database.readonly = read_only
        ifile.close()
    except IOError, msg:
        msg = _("%s could not be opened\n") % filename
        ErrorDialog(msg, str(msg))
        return
    except Errors.DbError, msg:
        DBErrorDialog(str(msg.value))
        return
    except Errors.GedcomError, msg:
        ErrorDialog(_('Error reading GEDCOM file'), str(msg))
        return
