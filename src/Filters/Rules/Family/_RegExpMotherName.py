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
from Filters.Rules.Person import RegExpName
from _MemberBase import mother_base

#-------------------------------------------------------------------------
#
# RegExpMotherName
#
#-------------------------------------------------------------------------
class RegExpMotherName(RegExpName):
    """Rule that checks for full or partial name matches"""

    name        = _('Families with mother matching the <regex_name>')
    description = _("Matches families whose mother has a name "
                    "matching a specified regular expression")
    category    = _('Mother filters')
    base_class = RegExpName
    apply = mother_base
