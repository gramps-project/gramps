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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Filter rule to match citation with a particular source.
"""
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
from .._hassourcebase import HasSourceBase

#-------------------------------------------------------------------------
#
# HasEvent
#
#-------------------------------------------------------------------------
class HasSource(HasSourceBase):
    """Rule that checks for an citation with a particular value"""

    labels = [ _('Title:'),
                    _('Author:'),
                    _('Abbreviation:'),
                    _('Publication:') ]
    name = _('Sources matching parameters')
    description = _("Matches citations with a source of a particular "
                    "value")
    category = _('Source filters')

    def apply(self, dbase, citation):
        source = dbase.get_source_from_handle(
                                    citation.get_reference_handle())
        if HasSourceBase.apply(self, dbase, source):
            return True
        return False
