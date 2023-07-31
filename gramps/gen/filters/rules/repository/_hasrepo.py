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

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ....lib.repotype import RepositoryType
from .. import Rule


# -------------------------------------------------------------------------
#
# HasRepo
#
# -------------------------------------------------------------------------
class HasRepo(Rule):
    """Rule that checks for a repo with a particular value"""

    labels = [
        _("Name:", "repo"),
        _("Type:"),
        _("Address:"),
        _("URL:"),
    ]
    name = _("Repositories matching parameters")
    description = _("Matches Repositories with particular parameters")
    category = _("General filters")
    allow_regex = True

    def prepare(self, db, user):
        if self.list[1]:
            self.rtype = RepositoryType()
            self.rtype.set_from_xml_str(self.list[1])
        else:
            self.rtype = None

    def apply(self, db, repo):
        if not self.match_substring(0, repo.get_name()):
            return False

        if self.rtype:
            if self.rtype.is_custom() and self.use_regex:
                if self.regex[1].search(str(repo.type)) is None:
                    return False
            elif repo.type != self.rtype:
                return False

        if self.list[2]:
            addr_match = False
            for addr in repo.address_list:
                # TODO for Arabic, should the next line's comma be translated?
                addr_text = ", ".join(addr.get_text_data_list())
                if self.match_substring(2, addr_text):
                    addr_match = True
                    break
            if not addr_match:
                return False

        if self.list[3]:
            url_match = False
            for url in repo.urls:
                # TODO for Arabic, should the next line's comma be translated?
                url_text = ", ".join(url.get_text_data_list())
                if self.match_substring(3, url_text):
                    url_match = True
                    break
            if not url_match:
                return False

        return True
