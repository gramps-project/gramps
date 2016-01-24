#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

import unittest

from .. import DbBsddb, DbTxn
from gramps.cli.clidbman import CLIDbManager
from gramps.gen.dbstate import DbState
from gramps.gen.lib import (Source, RepoRef, Citation, Repository, Person,
                            Family, Event, Place, Media)

class GrampsDbBaseTest(unittest.TestCase):
    """Base class for unittest that need to be able to create
    test databases."""

    def setUp(self):
        def dummy_callback(dummy):
            pass

        self.dbstate = DbState()
        self.dbman = CLIDbManager(self.dbstate)
        dirpath, name = self.dbman.create_new_db_cli("Test: bsddb", dbid="bsddb")
        self._db = self.dbstate.make_database("bsddb")
        self._db.load(dirpath, None)

    def tearDown(self):
        self._db.close()
        self.dbman.remove_database("Test: bsddb")

    def _populate_database(self,
                           num_sources = 1,
                           num_persons = 0,
                           num_families = 0,
                           num_events = 0,
                           num_places = 0,
                           num_media = 0,
                           num_links = 1):
        # start with sources
        sources = []
        for i in range(num_sources):
            sources.append(self._add_source())

        # now for each of the other tables. Give each entry a link
        # to num_link sources, sources are chosen on a round robin
        # basis

        for num, add_func in ((num_persons, self._add_person_with_sources),
                              (num_families, self._add_family_with_sources),
                              (num_events, self._add_event_with_sources),
                              (num_places, self._add_place_with_sources),
                              (num_media, self._add_media_with_sources)):

            source_idx = 1
            for person_idx in range(num):

                # Get the list of sources to link
                lnk_sources = set()
                for i in range(num_links):
                    lnk_sources.add(sources[source_idx-1])
                    source_idx = (source_idx+1) % len(sources)

                try:
                    add_func(lnk_sources)
                except:
                    print ("person_idx = ", person_idx)
                    print ("lnk_sources = ", repr(lnk_sources))
                    raise

        return

    def _add_source(self,repos=None):
        # Add a Source

        with DbTxn("Add Source and Citation", self._db) as tran:
            source = Source()
            if repos is not None:
                repo_ref = RepoRef()
                repo_ref.set_reference_handle(repos.get_handle())
                source.add_repo_reference(repo_ref)
            self._db.add_source(source, tran)
            self._db.commit_source(source, tran)
            citation = Citation()
            citation.set_reference_handle(source.get_handle())
            self._db.add_citation(citation, tran)
            self._db.commit_citation(citation, tran)

        return citation

    def _add_repository(self):
        # Add a Repository

        with DbTxn("Add Repository", self._db) as tran:
            repos = Repository()
            self._db.add_repository(repos, tran)
            self._db.commit_repository(repos, tran)

        return repos


    def _add_object_with_source(self, citations, object_class, add_method,
                                commit_method):

        object = object_class()

        with DbTxn("Add Object", self._db) as tran:
            for citation in citations:
                object.add_citation(citation.get_handle())
            add_method(object, tran)
            commit_method(object, tran)

        return object

    def _add_person_with_sources(self, citations):

        return self._add_object_with_source(citations,
                                            Person,
                                            self._db.add_person,
                                            self._db.commit_person)

    def _add_family_with_sources(self, citations):

        return self._add_object_with_source(citations,
                                            Family,
                                            self._db.add_family,
                                            self._db.commit_family)

    def _add_event_with_sources(self, citations):

        return self._add_object_with_source(citations,
                                            Event,
                                            self._db.add_event,
                                            self._db.commit_event)

    def _add_place_with_sources(self, citations):

        return self._add_object_with_source(citations,
                                            Place,
                                            self._db.add_place,
                                            self._db.commit_place)

    def _add_media_with_sources(self, citations):

        return self._add_object_with_source(citations,
                                            Media,
                                            self._db.add_media,
                                            self._db.commit_media)
