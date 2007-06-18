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
from Filters.Rules._HasEventBase import HasEventBase

#-------------------------------------------------------------------------
#
# HasEvent
#
#-------------------------------------------------------------------------
class HasEvent(HasEventBase):
    """Rule that checks for a family event with a particular value"""

    labels      = [ _('Family event:'), 
                    _('Date:'), 
                    _('Place:'), 
                    _('Description:') ]
    name        =  _('Families with the <event>')
    description = _("Matches families with an event of a particular value")

    def apply(self,db,family):
        for event_ref in family.get_event_ref_list():
            if not event_ref:
                continue
            event = db.get_event_from_handle(event_ref.ref)
            if HasEventBase.apply(self,db,event):
                return True
        return False
