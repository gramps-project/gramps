#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2006-2007  Alex Roitman
# Copyright (C) 2007-2009  Jerome Rapinat
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
# plugins/quickview/Reporef.py

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------

"""
Display RepoRef for sources related to active repository
"""

from gramps.gen.simple import SimpleAccess, SimpleDoc
from gramps.gui.plug.quick import QuickTable
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

def run(database, document, repo):
    """
    Display back-references (sources) for this repository.
    """

    # setup the simple access functions

    sdb = SimpleAccess(database)
    sdoc = SimpleDoc(document)
    stab = QuickTable(sdb)

    # First we find repository and add its text

    sdoc.title('%s\n' % repo.get_name())

    # Go over all the sources that refer to this repository

    repo_handle = repo.handle
    source_list = [item[1] for item in
                   database.find_backlink_handles(repo_handle, ['Source'
                   ])]

    stab.columns(_("Source"), _("Type of media"), _("Call number"))
    document.has_data = False
    for source_handle in source_list:
        src = database.get_source_from_handle(source_handle)

        # Get the list of references from this source to our repo
        # (can be more than one, technically)

        for reporef in src.get_reporef_list():
            if reporef.ref == repo_handle:

                # Determine the text for this source

                media = str(reporef.get_media_type())
                call = reporef.get_call_number()

                stab.row(src.get_title(), media, call)
                document.has_data = True
    if document.has_data:
        stab.write(sdoc)
    else:
        sdoc.header1(_("Not found"))
