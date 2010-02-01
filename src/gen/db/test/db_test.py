from gen.db import (DbReadBase, DbWriteBase, 
                    DbBsddbRead, DbBsddb)
from gen.proxy.proxybase import ProxyDbBase
from gen.proxy import LivingProxyDb

class DbTest(object):
    READ_METHODS = [
        "all_handles",
        "close",
        "create_id",
        "db_has_bm_changes",
        "find_backlink_handles",
        "find_initial_person",
        "find_next_event_gramps_id",
        "find_next_family_gramps_id",
        "find_next_note_gramps_id",
        "find_next_object_gramps_id",
        "find_next_person_gramps_id",
        "find_next_place_gramps_id",
        "find_next_repository_gramps_id",
        "find_next_source_gramps_id",
        "get_bookmarks",
        "get_child_reference_types",
        "get_default_handle",
        "get_default_person",
        "get_event_bookmarks",
        "get_event_cursor",
        "get_event_from_gramps_id",
        "get_event_from_handle",
        "get_event_handles",
        "get_event_roles",
        "get_family_attribute_types",
        "get_family_bookmarks",
        "get_family_cursor",
        "get_family_event_types",
        "get_family_from_gramps_id",
        "get_family_from_handle",
        "get_family_handles",
        "get_family_relation_types",
        "get_from_handle",
        "get_gramps_ids",
        "get_marker_types",
        "get_media_attribute_types",
        "get_media_bookmarks",
        "get_media_cursor",
        "get_media_object_handles",
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
        "get_number_of_media_objects",
        "get_number_of_notes",
        "get_number_of_people",
        "get_number_of_places",
        "get_number_of_repositories",
        "get_number_of_sources",
        "get_object_from_gramps_id",
        "get_object_from_handle",
        "get_person_attribute_types",
        "get_person_cursor",
        "get_person_event_types",
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
        "get_raw_object_data",
        "get_raw_person_data",
        "get_raw_place_data",
        "get_raw_repository_data",
        "get_raw_source_data",
        "get_reference_map_cursor",
        "get_reference_map_primary_cursor",
        "get_reference_map_referenced_cursor",
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
        "get_surname_list",
        "get_url_types",
        "gramps_upgrade",
        "has_event_handle",
        "has_family_handle",
        "has_gramps_id",
        "has_name_group_key",
        "has_note_handle",
        "has_object_handle",
        "has_person_handle",
        "has_place_handle",
        "has_repository_handle",
        "has_source_handle",
        "is_open",
        "iter_event_handles",
        "iter_events",
        "iter_families",
        "iter_family_handles",
        "iter_media_object_handles",
        "iter_media_objects",
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
        "load",
        "report_bm_change",
        "request_rebuild",
        # Prefix:
        "set_event_id_prefix",
        "set_family_id_prefix",
        "set_note_id_prefix",
        "set_object_id_prefix",
        "set_person_id_prefix",
        "set_place_id_prefix",
        "set_prefixes",
        "set_repository_id_prefix",
        "set_source_id_prefix",
        # Other set methods:
        "set_mediapath",
        "set_redo_callback",
        "set_researcher",
        "set_save_path",
        "set_undo_callback",

        "version_supported",
        ]

    WRITE_METHODS = [
        "add_event",
        "add_family",
        "add_family_event",
        "add_note",
        "add_object",
        "add_person",
        "add_person_event",
        "add_place",
        "add_repository",
        "add_source",
        "add_to_surname_list",
        "build_surname_list",
        "commit_base",
        "commit_event",
        "commit_family",
        "commit_family_event",
        "commit_media_object",
        "commit_note",
        "commit_person",
        "commit_personal_event",
        "commit_place",
        "commit_repository",
        "commit_source",
        "delete_primary_from_reference_map",
        "need_upgrade",
        "rebuild_secondary",
        "reindex_reference_map",
        "remove_event",
        "remove_family",
        "remove_from_surname_list",
        "remove_note",
        "remove_object",
        "remove_person",
        "remove_place",
        "remove_repository",
        "remove_source",
        "set_auto_remove",
        "set_default_person_handle",
        "set_name_group_mapping",
        "sort_surname_list",
        "transaction_begin",
        "transaction_commit",
        "update_reference_map",
        "write_version",
        ]

    def __init__(self, db):
        self.db = db

    def _verify_readonly(self):
        print "Verifying readonly", self.db.__class__.__name__
        for method in self.READ_METHODS:
            assert hasattr(self.db, method), \
                ("readonly should have a '%s' method" % method)
        for method in self.WRITE_METHODS:
            assert not hasattr(self.db, method), \
                ("readonly should NOT have a '%s' method" % method)
        print "passed!"

    def _verify_readwrite(self):
        print "Verifying readwrite", self.db.__class__.__name__
        for method in self.READ_METHODS:
            assert hasattr(self.db, method), \
                ("readwrite should have a '%s' method" % method)
        for method in self.WRITE_METHODS:
            assert hasattr(self.db, method), \
                ("readwrite should have a '%s' method" % method)
        print "passed!"

db1 = DbTest(DbReadBase())
db1._verify_readonly()

db2 = DbTest(DbWriteBase())
db2._verify_readwrite()

from gen.db import DbBsddbRead
db3 = DbTest(DbBsddbRead())
db3._verify_readonly()

from gen.db import DbBsddb
db4 = DbTest(DbBsddb())
db4._verify_readwrite()

from gen.proxy.proxybase import ProxyDbBase
gdb = DbBsddb()
db5 = DbTest(ProxyDbBase(gdb))
db5._verify_readonly()

from gen.proxy import LivingProxyDb
gdb = DbBsddb()
db6 = DbTest(LivingProxyDb(gdb, LivingProxyDb.MODE_EXCLUDE_ALL))
db6._verify_readonly()
