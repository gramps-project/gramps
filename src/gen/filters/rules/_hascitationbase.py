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
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import gen.datehandler
from gen.filters.rules import Rule

#-------------------------------------------------------------------------
#
# HasCitation
#
#-------------------------------------------------------------------------
class HasCitationBase(Rule):
    """Rule that checks for a citation with a particular value
    
    First parameter is [Volume/page, Date, Confidence]
    """


    labels      = [ 'Volume/Page:', 
                    'Date:', 
                    'Confidence:' ]
    name        = 'Citations matching parameters'
    description = "Matches citations with particular parameters"
    category    = _('Citation/source filters')

    def prepare(self, db):
        self.date = None
        try:
            if self.list[1]:
                self.date = gen.datehandler.parser.parse(self.list[1])
        except:
            pass

    def apply(self,db,citation):
        if not self.match_substring(0,citation.get_page()):
            return False

        if self.date:
            if not citation.get_date_object().match(self.date):
                return False
        
        if self.list[2]:
            if citation.get_confidence_level() < int(self.list[2]):
                return False

        return True
