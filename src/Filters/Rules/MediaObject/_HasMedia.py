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
from Filters.Rules._RuleUtils import loose_date_cmp

#-------------------------------------------------------------------------
#
# HasEvent
#
#-------------------------------------------------------------------------
class HasMedia(Rule):
    """Rule that checks for a media with a particular value"""


    labels      = [ _('Title:'), 
                    _('Type:'), 
                    _('Path:'),
                    _('Date:'), 
                    ]
    name        = _('Media objects matching parameters')
    description = _("Matches media objects with particular parameters")
    category    = _('General filters')

    def prepare(self,db):
        self.date = None
        try:
            if self.list[3]:
                self.date = DateHandler.parser.parse(self.list[3])
        except:
            pass

    def apply(self,db,obj):
        if not self.match_substring(0,obj.get_description()):
            return False

        if not self.match_substring(1,obj.get_mime_type()):
            return False

        if not self.match_substring(2,obj.get_path()):
            return False

        if self.date:
            if not loose_date_cmp(self.date,obj.get_date_object()):
                return False

        return True
