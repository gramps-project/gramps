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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ....datehandler import parser
from ....display.place import displayer as place_displayer
from ....lib.eventtype import EventType
from .. import Rule

#-------------------------------------------------------------------------
#
# HasFamilyEvent
#
#-------------------------------------------------------------------------
class HasFamilyEvent(Rule):
    """Rule that checks for a person who has a relationship event
    with a particular value"""

    labels = [ _('Family event:'),
                    _('Date:'),
                    _('Place:'),
                    _('Description:') ]
    name = _('People with the family <event>')
    description = _("Matches people with a family event of a particular value")
    category = _('Event filters')
    allow_regex = True

    def prepare(self, db, user):
        self.date = None
        try:
            if self.list[1]:
                self.date = parser.parse(self.list[1])
        except:
            pass

    def apply(self,db,person):
        for f_id in person.get_family_handle_list():
            f = db.get_family_from_handle(f_id)
            if not f:
                continue
            for event_ref in f.get_event_ref_list():
                if not event_ref:
                    continue
                event_handle = event_ref.ref
                event = db.get_event_from_handle(event_handle)
                val = 1
                if self.list[0]:
                    specified_type = EventType()
                    specified_type.set_from_xml_str(self.list[0])
                    if event.type != specified_type:
                        val = 0
                if self.list[3]:
                    if not self.match_substring(3, event.get_description()):
                        val = 0
                if self.date:
                    if not event.get_date_object().match(self.date):
                        val = 0
                if self.list[2]:
                    place_id = event.get_place_handle()
                    if place_id:
                        place = db.get_place_from_handle(place_id)
                        place_title = place_displayer.display(db, place)
                        if not self.match_substring(2, place_title):
                            val = 0
                    else:
                        val = 0

                if val == 1:
                    return True
        return False
