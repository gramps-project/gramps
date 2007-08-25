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

# $Id: _MatchesFilter.py 6932 2006-06-21 16:30:35Z dallingham $

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
import Filters
from Filters.Rules._MatchesFilterBase import MatchesFilterBase

#-------------------------------------------------------------------------
#
# MatchesFilter
#
#-------------------------------------------------------------------------
class MatchesPersonFilter(MatchesFilterBase):
    """
    Rule that checks against another filter.

    This is a base rule for subclassing by specific objects.
    Subclasses need to define the namespace class attribute.
    """

    labels      = [_('Person filter name:'), _('Include Family events:')]
    name        = _('Events of persons matching the <person filter>')
    description = _("Matches events of persons matched by the specified "
                    "person filter name")
    category    = _('General filters')
    # we want to have this filter show person filters
    namespace   = 'Person'
    
    def prepare(self,db):
        MatchesFilterBase.prepare(self, db)
        
        try :
            if int(self.list[1]):
                self.MPF_famevents = True
            else:
                self.MPF_famevents = False
        except IndexError:
            self.MPF_famevents = False


    def apply(self,db,event):
        filt = self.find_filter()
        if filt:
            for (classname, handle) in db.find_backlink_handles(
                                            event.get_handle(), ['Person']):
                if filt.check(db, handle):
                    return True
            if self.MPF_famevents :
                #also include if family event of the person
                for (classname, handle) in db.find_backlink_handles(
                                            event.get_handle(), ['Family']):
                    family = db.get_family_from_handle(handle)
                    if family.father_handle and filt.check(db, 
                                                    family.father_handle) :
                        return True
                    if family.mother_handle and filt.check(db, 
                                                    family.mother_handle) :
                        return True
           
        return False
