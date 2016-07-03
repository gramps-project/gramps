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

from .. import DbReadBase, DbWriteBase, DbBsddbRead, DbBsddb
from gramps.gen.proxy.proxybase import ProxyDbBase
from gramps.gen.proxy import LivingProxyDb

class DbTest(unittest.TestCase):
    READ_METHODS = [
        "close",
        "db_has_bm_changes",
        "find_backlink_handles",
        "find_initial_person",
        "find_next_event_gramps_id",
        "find_next_family_gramps_id",
        "find_next_note_gramps_id",
        "find_next_media_gramps_id",
        "find_next_person_gramps_id",
        "find_next_place_gramps_id",
        "find_next_repository_gramps_id",
        "find_next_source_gramps_id",
        "get_bookmarks",
        "get_child_reference_types",
        "get_default_handle",
        "get_default_person",
        "get_event_attribute_types",
        "get_event_bookmarks",
        "get_event_cursor",
        "get_event_from_gramps_id",
        "get_event_from_handle",
        "get_event_handles",
        "get_event_roles",
        "get_event_types",
        "get_family_attribute_types",
        "get_family_bookmarks",
        "get_family_cursor",
        "get_family_from_gramps_id",
        "get_family_from_handle",
        "get_family_handles",
        "get_family_relation_types",
        "get_gramps_ids",
        "get_media_attribute_types",
        "get_media_bookmarks",
        "get_media_cursor",
        "get_media_handles",
        "get_mediapath",
        "get_name_group_keys",
        "get_name_group_mapping",
        "get_name_types",
        "get_note_bookmarks",
        "get_note_cursor",
        "get_note_from_gramps_id",
        "get_note_from_handle",
        "get_note_handles",
        "get_note_types",
        "get_number_of_events",
        "get_number_of_families",
        "get_number_of_media",
        "get_number_of_notes",
        "get_number_of_people",
        "get_number_of_places",
        "get_number_of_repositories",
        "get_number_of_sources",
        "get_number_of_tags",
        "get_media_from_gramps_id",
        "get_media_from_handle",
        "get_person_attribute_types",
        "get_person_cursor",
        "get_person_from_gramps_id",
        "get_person_from_handle",
        "get_person_handles",
        "get_place_bookmarks",
        "get_place_cursor",
        "get_place_from_gramps_id",
        "get_place_from_handle",
        "get_place_handles",
        "get_raw_event_data",
        "get_raw_family_data",
        "get_raw_note_data",
        "get_raw_media_data",
        "get_raw_person_data",
        "get_raw_place_data",
        "get_raw_repository_data",
        "get_raw_source_data",
        "get_raw_tag_data",
        "get_repo_bookmarks",
        "get_repository_cursor",
        "get_repository_from_gramps_id",
        "get_repository_from_handle",
        "get_repository_handles",
        "get_repository_types",
        "get_researcher",
        "get_save_path",
        "get_source_bookmarks",
        "get_source_cursor",
        "get_source_from_gramps_id",
        "get_source_from_handle",
        "get_source_handles",
        "get_source_media_types",
        "get_tag_cursor",
        "get_tag_from_name",
        "get_tag_from_handle",
        "get_tag_handles",
        "get_surname_list",
        "get_url_types",
        "has_event_handle",
        "has_family_handle",
        "has_gramps_id",
        "has_name_group_key",
        "has_note_handle",
        "has_media_handle",
        "has_person_handle",
        "has_place_handle",
        "has_repository_handle",
        "has_source_handle",
        "has_tag_handle",
        "is_open",
        "iter_event_handles",
        "iter_events",
        "iter_families",
        "iter_family_handles",
        "iter_media_handles",
        "iter_media",
        "iter_note_handles",
        "iter_notes",
        "iter_people",
        "iter_person_handles",
        "iter_place_handles",
        "iter_places",
        "iter_repositories",
        "iter_repository_handles",
        "iter_source_handles",
        "iter_sources",
        "iter_tag_handles",
        "iter_tags",
        "load",
        "report_bm_change",
        "request_rebuild",
        # Prefix:
        "set_event_id_prefix",
        "set_family_id_prefix",
        "set_note_id_prefix",
        "set_media_id_prefix",
        "set_person_id_prefix",
        "set_place_id_prefix",
        "set_prefixes",
        "set_repository_id_prefix",
        "set_source_id_prefix",
        # Other set methods:
        "set_mediapath",
        "set_researcher",
        "set_save_path",
        "version_supported",
        ]

    WRITE_METHODS = [
        "add_event",
        "add_family",
        "add_note",
        "add_media",
        "add_person",
        "add_place",
        "add_repository",
        "add_source",
        "add_tag",
        "add_to_surname_list",
        "build_surname_list",
        "commit_event",
        "commit_family",
        "commit_media",
        "commit_note",
        "commit_person",
        "commit_place",
        "commit_repository",
        "commit_source",
        "commit_tag",
        "rebuild_secondary",
        "reindex_reference_map",
        "remove_event",
        "remove_family",
        "remove_from_surname_list",
        "remove_note",
        "remove_media",
        "remove_person",
        "remove_place",
        "remove_repository",
        "remove_source",
        "remove_tag",
        "set_default_person_handle",
        "set_name_group_mapping",
        "transaction_begin",
        "transaction_commit",
        "write_version",
        ]

    def _verify_readonly(self, db):
        for method in self.READ_METHODS:
            self.assertTrue(hasattr(db, method),
                ("readonly should have a '%s' method" % method))
        for method in self.WRITE_METHODS:
            self.assertFalse(hasattr(db, method),
                ("readonly should NOT have a '%s' method" % method))

    def _verify_readwrite(self, db):
        for method in self.READ_METHODS:
            self.assertTrue(hasattr(db, method),
                ("readwrite should have a '%s' method" % method))
        for method in self.WRITE_METHODS:
            self.assertTrue(hasattr(db, method),
                ("readwrite should have a '%s' method" % method))

    def test_verify_readbase(self):
        db = DbReadBase()
        self._verify_readonly(db)

    def test_verify_writebase(self):
        db = DbWriteBase()
        self._verify_readwrite(db)

    def test_verify_read(self):
        db = DbBsddbRead()
        self._verify_readonly(db)

    def test_verify_write(self):
        db = DbBsddb()
        self._verify_readwrite(db)

    def test_verify_proxy(self):
        gdb = DbBsddb()
        db = ProxyDbBase(gdb)
        self._verify_readonly(db)

    def test_verify_living(self):
        gdb = DbBsddb()
        db = LivingProxyDb(gdb, LivingProxyDb.MODE_EXCLUDE_ALL)
        self._verify_readonly(db)


if __name__ == "__main__":
    unittest.main()
