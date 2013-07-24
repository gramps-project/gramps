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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# test/GrampsDb/GrampsDbTestBase.py
# $Id$

import unittest
import logging
import os
import tempfile
import shutil
import time
import traceback
import sys

sys.path.append('../gramps')

try:
    set()
except NameError:
    from sets import Set as set
    
from gramps.gen.db import DbBsddb
from gramps.cli.clidbman import CLIDbManager
import gramps.gen.const
import gramps.gen.lib

logger = logging.getLogger('Gramps.GrampsDbTestBase')

class GrampsDbBaseTest(unittest.TestCase):
    """Base class for unittest that need to be able to create
    test databases."""
    
    def setUp(self):        
        def dummy_callback(dummy):
            pass
        self._tmpdir = tempfile.mkdtemp()
        #self._filename = os.path.join(self._tmpdir,'test.grdb')
        
        self._db = DbBsddb()
        dbman = CLIDbManager(None)
        self._filename, title = dbman.create_new_db_cli(title="Test")
        self._db.load(self._filename, dummy_callback, "w")

    def tearDown(self):
        self._db.close()
        shutil.rmtree(self._tmpdir)

    def _populate_database(self,
                           num_sources = 1,
                           num_persons = 0,
                           num_families = 0,
                           num_events = 0,
                           num_places = 0,
                           num_media_objects = 0,
                           num_links = 1):

        # start with sources
        sources = []
        for i in xrange(0, num_sources):
            sources.append(self._add_source())

        # now for each of the other tables. Give each entry a link
        # to num_link sources, sources are chosen on a round robin
        # basis

        for num, add_func in ((num_persons, self._add_person_with_sources),
                              (num_families, self._add_family_with_sources),
                              (num_events, self._add_event_with_sources),
                              (num_places, self._add_place_with_sources),
                              (num_media_objects, self._add_media_object_with_sources)):
                                   
            source_idx = 1
            for person_idx in xrange(0, num):

                # Get the list of sources to link
                lnk_sources = set()
                for i in xrange(0, num_links):
                    lnk_sources.add(sources[source_idx-1])
                    source_idx = (source_idx+1) % len(sources)

                try:
                    add_func(lnk_sources)
                except:
                    print "person_idx = ", person_idx
                    print "lnk_sources = ", repr(lnk_sources)
                    raise

        return

    def _add_source(self,repos=None):
        # Add a Source
        
        tran = self._db.transaction_begin()
        source = gen.lib.Source()
        if repos is not None:
            repo_ref = gen.lib.RepoRef()
            repo_ref.set_reference_handle(repos.get_handle())
            source.add_repo_reference(repo_ref)
        self._db.add_source(source,tran)
        self._db.commit_source(source,tran)
        self._db.transaction_commit(tran, "Add Source")

        return source

    def _add_repository(self):
        # Add a Repository
        
        tran = self._db.transaction_begin()
        repos = gen.lib.Repository()
        self._db.add_repository(repos,tran)
        self._db.commit_repository(repos,tran)
        self._db.transaction_commit(tran, "Add Repository")

        return repos

                           
    def _add_object_with_source(self,sources, object_class,add_method,commit_method):

        object = object_class()

        for source in sources:
            src_ref = gen.lib.SourceRef()
            src_ref.set_reference_handle(source.get_handle())
            object.add_source_reference(src_ref)


        tran = self._db.transaction_begin()
        add_method(object,tran)
        commit_method(object,tran)
        self._db.transaction_commit(tran, "Add Object")

        return object

    def _add_person_with_sources(self,sources):

        return self._add_object_with_source(sources,
                                            gen.lib.Person,
                                            self._db.add_person,
                                            self._db.commit_person)

    def _add_family_with_sources(self,sources):

        return self._add_object_with_source(sources,
                                            gen.lib.Family,
                                            self._db.add_family,
                                            self._db.commit_family)

    def _add_event_with_sources(self,sources):

        return self._add_object_with_source(sources,
                                            gen.lib.Event,
                                            self._db.add_event,
                                            self._db.commit_event)

    def _add_place_with_sources(self,sources):

        return self._add_object_with_source(sources,
                                            gen.lib.Place,
                                            self._db.add_place,
                                            self._db.commit_place)

    def _add_media_object_with_sources(self,sources):

        return self._add_object_with_source(sources,
                                            gen.lib.MediaObject,
                                            self._db.add_object,
                                            self._db.commit_media_object)
