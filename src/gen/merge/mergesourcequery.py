#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
# Copyright (C) 2010       Michiel D. Nauta
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
Provide merge capabilities for sources.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gen.lib import (Person, Family, Event, Place, Source, Repository,
                     MediaObject, Citation)
from gen.db import DbTxn
from gen.ggettext import sgettext as _
from Errors import MergeError

#-------------------------------------------------------------------------
#
# MergeSourceQuery
#
#-------------------------------------------------------------------------
class MergeSourceQuery(object):
    """
    Create database query to merge two sources.
    """
    def __init__(self, dbstate, phoenix, titanic):
        self.database = dbstate.db
        self.phoenix = phoenix
        self.titanic = titanic

    def execute(self):
        """
        Merges to sources into a single source.
        """
        new_handle = self.phoenix.get_handle()
        old_handle = self.titanic.get_handle()

        self.phoenix.merge(self.titanic)

        with DbTxn(_("Merge Source"), self.database) as trans:
            self.database.commit_source(self.phoenix, trans)
            for (class_name, handle) in self.database.find_backlink_handles(
                    old_handle):
                if class_name == Citation.__name__:
                    citation = self.database.get_citation_from_handle(handle)
                    assert(citation.get_reference_handle() == old_handle)
                    citation.set_reference_handle(new_handle)
                    self.database.commit_citation(citation, trans)
                else:
                    raise MergeError("Encounter an object of type %s that has "
                            "a source reference." % class_name)
            self.database.remove_source(old_handle, trans)
