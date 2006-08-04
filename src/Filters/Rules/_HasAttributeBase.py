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

# $Id: _HasAttributeBase.py,v 1.1 2006/08/04 23:08:14 shura Exp $

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
from RelLib import AttributeType
from Filters.Rules._Rule import Rule

#-------------------------------------------------------------------------
#
# HasAttribute
#
#-------------------------------------------------------------------------
class HasAttributeBase(Rule):
    """Rule that checks for an object with a particular attribute"""

    labels      = [ _('Attribute:'), _('Value:') ]
    name        = _('Objects with the <attribute>')
    description = _("Matches objects with the given attribute "
                    "of a particular value")
    category    = _('General filters')

    def apply(self,db,obj):
        if not self.list[0]:
            return False
        for attr in obj.get_attribute_list():
            specified_type = AttributeType()
            specified_type.set_from_xml_str(self.list[0])
            name_match = attr.get_type() == specified_type

            value_match = \
                    attr.get_value().upper().find(self.list[1].upper()) != -1
            if name_match and value_match:
                return True
        return False
