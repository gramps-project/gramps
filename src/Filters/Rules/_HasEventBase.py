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

# $Id: _HasEvent.py 6635 2006-05-13 03:53:06Z dallingham $

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
from RelLib import EventType
from Filters.Rules._Rule import Rule

#-------------------------------------------------------------------------
#
# HasEvent
#
#-------------------------------------------------------------------------
class HasEventBase(Rule):
    """Rule that checks for an event with a particular value"""


    labels      = [ _('Event type:'), 
                    _('Date:'), 
                    _('Place:'), 
                    _('Description:') ]
    name        =  _('Events matching parameters')
    description =  _("Matches events with particular parameters")
    category    = _('Event filters')
    
    def prepare(self,db):
        self.date = None
        if self.list[0]:
            self.etype = self.list[0]
        else:
            self.etype = None
        try:
            if self.list[1]:
                self.date = DateHandler.parser.parse(self.list[1])
        except: pass

    def apply(self,db,event):
        if self.etype:
            specified_type = EventType()
            specified_type.set_from_xml_str(self.etype)
            if event.type != specified_type:
                return False
        if self.list[3] and event.get_description().upper().find(
                                        self.list[3].upper())==-1:
            return False

        if self.date:
            if not event.get_date_object().match(self.date):
                return False

        if self.list[2]:
            pl_id = event.get_place_handle()
            if pl_id:
                pl = db.get_place_from_handle(pl_id)
                pn = pl.get_title()
                if pn.upper().find(self.list[2].upper()) == -1:
                    return False
            else:
                return False
        return True
