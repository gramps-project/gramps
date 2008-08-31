#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Gary Burton
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
from gen.lib import EventType
from Filters.Rules._Rule import Rule

#-------------------------------------------------------------------------
#
# HasBirth
#
#-------------------------------------------------------------------------
class HasData(Rule):
    """Rule that checks for an event containing particular values"""

    labels      = [ _('Event type:'), _('Date:'), _('Place:'),
                    _('Description:') ]
    name        = _('Events with <data>')
    description = _("Matches events with data of a particular value")
    category    = _('General filters')
    
    def __init__(self, list):
        Rule.__init__(self, list)

        self.event_type = self.list[0]
        self.date = self.list[1]
        self.place = self.list[2]
        self.description = self.list[3]

        if self.event_type:
            self.event_type = EventType()
            self.event_type.set_from_xml_str(self.list[0])

        if self.date:
            self.date = DateHandler.parser.parse(self.date)
        
    def apply(self, db, event):
        if self.event_type and event.get_type() != self.event_type:
            # No match
            return False

        ed = event.get_description().upper()
        if self.description and ed.find(self.description.upper()) == -1:
            # No match
            return False

        if self.date and not event.get_date_object().match(self.date):
            # No match
            return False

        if self.place:
            pl_id = event.get_place_handle()
            if pl_id:
                pl = db.get_place_from_handle(pl_id)
                pn = pl.get_title().upper()
                if pn.find(self.place.upper()) == -1:
                    # No match
                    return False
            else:
                # No place attached to event
                return False

        # All conditions matched
        return True
