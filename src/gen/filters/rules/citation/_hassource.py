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

"""
Filter rule to match citation with a particular source.
"""
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
from gen.filters.rules._hassourcebase import HasSourceBase

#-------------------------------------------------------------------------
#
# HasEvent
#
#-------------------------------------------------------------------------
class HasSource(HasSourceBase):
    """Rule that checks for an citation with a particular value"""

    labels      = [ _('Title:'), 
                    _('Author:'), 
                    _('Publication:') ]
    name        = _('Sources matching parameters')
    description = _("Matches citations with a source of a particular "
                    "value")
    category    = _('Source filters')
    
    def apply(self, dbase, citation):
        source = dbase.get_source_from_handle(
                                    citation.get_reference_handle())
        if HasSourceBase.apply(self, dbase, source):
            return True
        return False
