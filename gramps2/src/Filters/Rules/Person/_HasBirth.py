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
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import DateHandler
from Filters.Rules._Rule import Rule
from Filters.Rules._RuleUtils import date_cmp

#-------------------------------------------------------------------------
#
# HasBirth
#
#-------------------------------------------------------------------------
class HasBirth(Rule):
    """Rule that checks for a person with a birth of a particular value"""

    labels      = [ _('Date:'), _('Place:'), _('Description:') ]
    name        = _('People with the <birth data>')
    description = _("Matches people with birth data of a particular value")
    category    = _('Event filters')
    
    def __init__(self,list):
        Rule.__init__(self,list)
        if self.list[0]:
            self.date = DateHandler.parser.parse(self.list[0])
        else:
            self.date = None
        
    def apply(self,db,person):
        event_ref = person.get_birth_ref()
        if not event_ref:
            return False
        event = db.get_event_from_handle(event_ref.ref)
        ed = event.get_description().upper()
        if self.list[2] \
               and ed.find(self.list[2].upper())==-1:
            return False
        if self.date:
            if date_cmp(self.date,event.get_date_object()) == 0:
                return False
        if self.list[1]:
            pl_id = event.get_place_handle()
            if pl_id:
                pl = db.get_place_from_handle(pl_id)
                pn = pl.get_title().upper()
                if pn.find(self.list[1].upper()) == -1:
                    return False
            else:
                return False
        return True
