#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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
import re
from ...const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from . import Rule

#-------------------------------------------------------------------------
#
# HasIdOf
#
#-------------------------------------------------------------------------
class RegExpIdBase(Rule):
    """
    Rule that checks for an object whose GRAMPS ID matches regular expression.
    """

    labels      = [ _('Regular expression:') ]
    name        = 'Objects with <Id>'
    description = "Matches objects whose Gramps ID matches " \
                   "the regular expression"
    category    = _('General filters')

    def __init__(self, list, use_regex=False):
        Rule.__init__(self, list, use_regex)
        
        try:
            self.match = re.compile(list[0], re.I|re.U|re.L)
        except:
            self.match = re.compile('')

    def apply(self, db, obj):
        return self.match.search(obj.gramps_id) is not None
