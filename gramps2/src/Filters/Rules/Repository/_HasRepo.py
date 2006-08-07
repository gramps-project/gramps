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
from RelLib import RepositoryType
from Filters.Rules._Rule import Rule

#-------------------------------------------------------------------------
#
# HasEvent
#
#-------------------------------------------------------------------------
class HasRepo(Rule):
    """Rule that checks for a repo with a particular value"""


    labels      = [ _('Name:'), 
                    _('Type:'), 
                    _('Address:'),
                    _('URL:'), 
                    ]
    name        = _('Repositories matching parameters')
    description = _("Matches Repositories with particular parameters")
    category    = _('General filters')

    def apply(self,db,repo):
        if not self.match_substring(0,repo.get_name()):
            return False

        if self.list[1]:
            specified_type = RepositoryType()
            specified_type.set_from_xml_str(self.list[1])
            if repo.type != specified_type:
                return False

        addr_match = False
        for addr in repo.address_list:
            addr_text = addr.city + addr.state + addr.country + addr.postal \
                        + addr.phone + addr.street

            if not self.match_substring(2,addr_text):
                continue

            addr_match = True

        url_match = False
        for url in repo.urls:
            url_text = url.path + url.desc
            if not self.match_substring(3,url_text):
                continue
            url_match = True           

        return (addr_match or url_match)
