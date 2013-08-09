#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011 Helge Herz
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
# Filters/Rules/Source/_HasRepositoryCallNumberRef.py
# $Id$
#

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
from Filters.Rules import Rule

#-------------------------------------------------------------------------
# "Sources which reference repositories by a special Call Name"
#-------------------------------------------------------------------------
class HasRepositoryCallNumberRef(Rule):
    """Sources which reference repositories by a special Call Number"""

    labels      = [ _('Text:')]
    name        = _('Sources with repository reference containing <text> in "Call Number"')
    description = _("Matches sources with a repository reference\n"
                    "containing a substring in \"Call Number\"")
    category    = _('General filters')
    allow_regex = True
      
    def apply(self, db, obj):
        for repo_ref in obj.get_reporef_list():
            if self.match_substring(0, repo_ref.call_number):
                return True			
        return False
