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

"""
Rule that checks for a repo with a particular value.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ....const import GRAMPS_LOCALE as glocale
from ....lib.repotype import RepositoryType
from .. import Rule

# -------------------------------------------------------------------------
#
# Typing modules
#
# -------------------------------------------------------------------------
from ....lib import Repository
from ....db import Database


_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# HasRepo
#
# -------------------------------------------------------------------------
class HasRepo(Rule):
    """
    Rule that checks for a repo with a particular value.
    """

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

    def __init__(self, arg, use_regex=False, use_case=False):
        super().__init__(arg, use_regex, use_case)
        self.rtype = None

    def prepare(self, db: Database, user):
        """
        Prepare the rule. Things we only want to do once.
        """
        if self.list[1]:
            self.rtype = RepositoryType()
            self.rtype.set_from_xml_str(self.list[1])

    def apply_to_one(self, _db: Database, obj: Repository) -> bool:
        """
        Apply the rule. Return True on a match.
        """
        if not self.match_substring(0, obj.name):
            return False

        if self.rtype:
            if self.rtype.is_custom() and self.use_regex:
                if self.regex[1].search(str(obj.type)) is None:
                    return False
            elif obj.type != self.rtype:
                return False

        if self.list[2]:
            addr_match = False
            for addr in obj.address_list:
                # TODO for Arabic, should the next line's comma be translated?
                addr_text = ", ".join(addr.get_text_data_list())
                if self.match_substring(2, addr_text):
                    addr_match = True
                    break
            if not addr_match:
                return False

        if self.list[3]:
            url_match = False
            for url in obj.urls:
                # TODO for Arabic, should the next line's comma be translated?
                url_text = ", ".join(url.get_text_data_list())
                if self.match_substring(3, url_text):
                    url_match = True
                    break
            if not url_match:
                return False

        return True
