#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2011       Tim G L Lyons
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

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from ...const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from . import Rule
from gramps.gen.utils.citeref import (get_gedcom_title, get_gedcom_author,
                                      get_gedcom_pubinfo)

#-------------------------------------------------------------------------
#
# HasSource
#
#-------------------------------------------------------------------------
class HasSourceBase(Rule):
    """Rule that checks for a source with a particular value"""


    labels      = [ 'Title:', 
                    'Author:', 
                    'Abbreviation:',
                    'Publication:' ]
    name        = 'Sources matching parameters'
    description = "Matches sources with particular parameters"
    category    = _('Citation/source filters')
    allow_regex = True

    def apply(self,db,source):
        if not self.match_substring(0, get_gedcom_title(db, source)):
            return False

        if not self.match_substring(1, get_gedcom_author(db, source)):
            return False

        if not self.match_substring(2,source.get_abbreviation()):
            return False

        if not self.match_substring(3, get_gedcom_pubinfo(db, source)):
            return False

        return True
