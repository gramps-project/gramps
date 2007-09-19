#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

# $Id: _ReadGedcom.py 8032 2007-02-03 17:11:05Z hippy $

"""
Import from GEDCOM
"""

__revision__ = "$Revision: $"
__author__   = "Don Allingham"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import codecs
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import Errors

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".GedcomImport")

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
BAD_UTF16 = _("Your GEDCOM file is corrupted. "
              "The file appears to be encoded using the UTF16 "
              "character set, but is missing the BOM marker.")
EMPTY_GED = _("Your GEDCOM file is empty.")

#-------------------------------------------------------------------------
#
# is_xref_value
#
#-------------------------------------------------------------------------
def is_xref_value(value):
    """
    Returns True if value is in the form of a XREF value. We assume that
    if we have a leading '@' character, then we are okay.
    """
    return value and value[0] == '@'

#-------------------------------------------------------------------------
#
# add_to_list
#
#-------------------------------------------------------------------------
def add_to_list(table, key, value):
    """
    Adds the value to the table entry associated with key. If the entry 
    does not exist, it is added.
    """
    if table.has_key(key):
        table[key].append(value)
    else:
        table[key] = [value]

#-------------------------------------------------------------------------
#
# StageOne
#
#-------------------------------------------------------------------------
class StageOne:
    """
    The StageOne parser scans the file quickly, looking for a few things. This
    includes:

    1. Character set encoding
    2. Number of people and families in the list
    3. Child to family references, since Ancestry.com creates GEDCOM files 
       without the FAMC references.
    """
    def __init__(self, ifile):
        self.ifile = ifile
        self.famc = {}
        self.fams = {}
        self.enc = ""
        self.pcnt = 0
        self.lcnt = 0

    def __detect_file_decoder(self, input_file):
        """
        Detects the file encoding of the file by looking for a BOM 
        (byte order marker) in the GEDCOM file. If we detect a UTF-16
        encoded file, we must connect to a wrapper using the codecs
        package.
        """
        line = input_file.read(2)
        if line == "\xef\xbb":
            input_file.read(1)
            self.enc = "UTF8"
            return input_file
        elif line == "\xff\xfe":
            self.enc = "UTF16"
            input_file.seek(0)
            return codecs.EncodedFile(input_file, 'utf8', 'utf16')
        elif not line :
            raise Errors.GedcomError(EMPTY_GED)
        elif line[0] == "\x00" or line[1] == "\x00":
            raise Errors.GedcomError(BAD_UTF16)
        else:
            input_file.seek(0)
            return input_file

    def parse(self):
        """
        Parse the input file.
        """
        current_family_id = ""
        
        reader = self.__detect_file_decoder(self.ifile)

        for line in reader:
            line = line.strip()
            if not line:
                continue
            self.lcnt += 1

            data = line.split(None, 2) + ['']
            try:
                (level, key, value) = data[:3]
                value = value.strip()
                level = int(level)
                key = key.strip()
            except:
                LOG.warn(_("Invalid line %d in GEDCOM file.") % self.lcnt)
                continue

            if level == 0 and key[0] == '@':
                if value == ("FAM", "FAMILY") :
                    current_family_id = key.strip()[1:-1]
                elif value == ("INDI", "INDIVIDUAL"):
                    self.pcnt += 1
            elif key in ("HUSB", "HUSBAND", "WIFE") and is_xref_value(value):
                add_to_list(self.fams, value[1:-1], current_family_id)
            elif key in ("CHIL", "CHILD") and is_xref_value(value):
                add_to_list(self.famc, value[1:-1], current_family_id)
            elif key == 'CHAR' and not self.enc:
                assert(type(value) == str or type(value) == unicode)
                self.enc = value

    def get_famc_map(self):
        """
        Returns the Person to Child Family map
        """
        return self.famc

    def get_fams_map(self):
        """
        Returns the Person to Family map (where the person is a spouse)
        """
        return self.fams

    def get_encoding(self):
        """
        Returns the detected encoding
        """
        return self.enc.upper()

    def set_encoding(self, enc):
        """
        Forces the encoding
        """
        assert(type(enc) == str or type(enc) == unicode)
        self.enc = enc

    def get_person_count(self):
        """
        Returns the number of INDI records found
        """
        return self.pcnt

    def get_line_count(self):
        """
        Returns the number of lines in the file
        """
        return self.lcnt
