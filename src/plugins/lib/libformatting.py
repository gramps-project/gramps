# -*- python -*-
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham, Martin Hawlisch
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

# $Id: pedigreeview.py 13528 2009-11-08 16:41:49Z bmcage $

"""Format of commonly used expressions, making use of a cache to not 
recompute
"""
#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from cgi import escape

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import gen.lib
import DateHandler
from BasicUtils import name_displayer
from ReportBase import ReportUtils

#-------------------------------------------------------------------------
#
# FormattingHelper class
#
#-------------------------------------------------------------------------
class FormattingHelper(object):
    """Format of commonly used expressions, making use of a cache to not 
    recompute
    """
    def __init__(self, dbstate):
        self.dbstate = dbstate
        self._text_cache = {}
        self._markup_cache = {}
    
    def format_relation(self, family, line_count):
        """ Format a relation between parents of a family
        """
        text = ""
        for event_ref in family.get_event_ref_list():
            event = self.dbstate.db.get_event_from_handle(event_ref.ref)
            if event and event.get_type() == gen.lib.EventType.MARRIAGE and \
            (event_ref.get_role() == gen.lib.EventRoleType.FAMILY or 
            event_ref.get_role() == gen.lib.EventRoleType.PRIMARY ):
                if line_count < 3:
                    return DateHandler.get_date(event)
                name = str(event.get_type())
                text += name
                text += "\n"
                text += DateHandler.get_date(event)
                text += "\n"
                text += self.get_place_name(event.get_place_handle())
                if line_count < 5:
                    return text
                break
        if not text:
            text = str(family.get_relationship())
        return text

    def get_place_name(self, place_handle):
        """ Obtain a place name
        """
        text = ""
        place = self.dbstate.db.get_place_from_handle(place_handle)
        if place:
            place_title = place.get_title()
            if place_title != "":
                if len(place_title) > 25:
                    text = place_title[:24]+"..."
                else:
                    text = place_title
        return text

    def format_person( self, person, line_count, use_markup=False):
        """fromat how info about a person should be presented
        """
        if not person:
            return ""
        if use_markup:
            if person.handle in self._markup_cache:
                if line_count in self._markup_cache[person.handle]:
                    return self._markup_cache[person.handle][line_count]
            name = escape(name_displayer.display(person))
        else:
            if person.handle in self._text_cache:
                if line_count in self._text_cache[person.handle]:
                    return self._text_cache[person.handle][line_count]
            name = name_displayer.display(person)
        text = name
        if line_count >= 3:
            birth = ReportUtils.get_birth_or_fallback(self.dbstate.db, person)
            if birth and use_markup and birth.get_type() != \
                                                    gen.lib.EventType.BIRTH:
                bdate  = "<i>%s</i>" % escape(DateHandler.get_date(birth))
                bplace = "<i>%s</i>" % escape(self.get_place_name(
                                                    birth.get_place_handle()))
            elif birth and use_markup:
                bdate  = escape(DateHandler.get_date(birth))
                bplace = escape(self.get_place_name(birth.get_place_handle()))
            elif birth:
                bdate  = DateHandler.get_date(birth)
                bplace = self.get_place_name(birth.get_place_handle())
            else:
                bdate = ""
                bplace = ""
            death = ReportUtils.get_death_or_fallback(self.dbstate.db, person)
            if death and use_markup and death.get_type() != \
                                                    gen.lib.EventType.DEATH:
                ddate  = "<i>%s</i>" % escape(DateHandler.get_date(death))
                dplace = "<i>%s</i>" % escape(self.get_place_name(
                                                    death.get_place_handle()))
            elif death and use_markup:
                ddate  = escape(DateHandler.get_date(death))
                dplace = escape(self.get_place_name(death.get_place_handle()))
            elif death:
                ddate  = DateHandler.get_date(death)
                dplace = self.get_place_name(death.get_place_handle())
            else:
                ddate = ""
                dplace = ""
            
            if line_count < 5:
                text = "%s\n* %s\n+ %s" % (name, bdate, ddate)
            else:
                text = "%s\n* %s\n  %s\n+ %s\n  %s" % (name, bdate, bplace,
                                                       ddate, dplace)
        if use_markup:
            if not person.handle in self._markup_cache:
                self._markup_cache[person.handle] = {}
            self._markup_cache[person.handle][line_count] = text
        else:
            if not person.handle in self._text_cache:
                self._text_cache[person.handle] = {}
            self._text_cache[person.handle][line_count] = text
        return text

    def clear_cache( self):
        """clear the cache of kept format strings
        """
        self._text_cache = {}
        self._markup_cache = {}
