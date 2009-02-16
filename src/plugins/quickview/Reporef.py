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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
# $Id$
#

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------

"""
Display RepoRef for sources related to active repository
"""

from Simple import SimpleDoc
from gettext import gettext as _
from gen.plug import PluginManager
from ReportBase import CATEGORY_QR_REPOSITORY

def run(database, document, repo):
    """
    Display back-references (sources) for this repository.
    """

    sdoc = SimpleDoc(document)

    # First we find repository and add its text

    sdoc.title('%s\n' % repo.get_name())

    # Go over all the sources that refer to this repository

    repo_handle = repo.handle
    source_list = [item[1] for item in
                   database.find_backlink_handles(repo_handle, ['Source'
                   ])]

    for source_handle in source_list:
        src = database.get_source_from_handle(source_handle)

        # Get the list of references from this source to our repo
        # (can be more than one, technically)

        for reporef in src.get_reporef_list():
            if reporef.ref == repo_handle:

                # Determine the text for this source

                media = str(reporef.get_media_type())
                call = reporef.get_call_number()
                sdoc.paragraph('%s, %s' % (media, call))
                sdoc.paragraph('%s\n' % src.get_title())
            else:
                continue


# ------------------------------------------------------------------------
#
#
#
# ------------------------------------------------------------------------

PMGR = PluginManager.get_instance()

PMGR.register_quick_report(
    name='RepoRef',
    category=CATEGORY_QR_REPOSITORY,
    run_func=run,
    translated_name=_('RepoRef'),
    status=_('Stable'),
    description=_('Display RepoRef for sources related to active repository'
                  ),
    author_name="Jerome Rapinat",
    author_email="romjerome@yahoo.fr"
    )
