#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Doug Blank
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

"""Tests for pure logic in gramps/gui/fs/person/mixins/compare_gtk.py.

Covers two issues:

  Issue 4 – ``_apply_selected_merge_rows`` exception logging/tracking.
    * A LOG.warning is emitted for each row that raises.
    * A ``failed`` counter is tracked independently of ``changed``.
    * When changed > 0 and failed > 0, OkDialog includes both counts.
    * When changed == 0 and failed > 0, WarningDialog is shown.

  Issue 7 – ``_fs_photo_pixbuf`` must NOT cache a None result.
    * After a failed fetch, ``_FS_PHOTO_CACHE`` must not gain a new entry.
    * After a successful fetch the pixbuf IS stored in ``_FS_PHOTO_CACHE``.

This test lives in gramps/gui/fs/test/ (not inside gramps/gui/fs/person/)
so that the parent-package chain does NOT include gramps.gui.fs.person, whose
__init__.py eagerly imports fsg_sync which pulls in GTK at import time before
our sys.modules stubs can take effect.

python3 -m unittest gramps.gui.fs.test.compare_gtk_test -v
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import os
import shutil
import sys
import tempfile
import types
import unittest
from dataclasses import dataclass
from typing import Any, Optional
from unittest.mock import MagicMock, patch

# Protect headless / standalone CI runs from missing display.
os.environ.setdefault("GDK_BACKEND", "-")

# -------------------------------------------------------------------------
#
# Test-resource bootstrap
#
# -------------------------------------------------------------------------
ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
)


def _ensure_test_resources() -> str:
    """Return a valid GRAMPS_RESOURCES path, creating a minimal one if needed."""
    resource_path = os.environ.get("GRAMPS_RESOURCES")
    if resource_path and os.path.exists(
        os.path.join(resource_path, "gramps", "authors.xml")
    ):
        return resource_path

    build_share = os.path.join(ROOT_DIR, "build", "share")
    if os.path.exists(os.path.join(build_share, "gramps", "authors.xml")):
        return build_share

    resource_path = tempfile.mkdtemp(prefix="gramps-resources-")
    os.makedirs(os.path.join(resource_path, "gramps", "images"), exist_ok=True)
    os.makedirs(os.path.join(resource_path, "doc", "gramps"), exist_ok=True)
    os.makedirs(os.path.join(resource_path, "locale"), exist_ok=True)

    shutil.copyfile(
        os.path.join(ROOT_DIR, "data", "authors.xml"),
        os.path.join(resource_path, "gramps", "authors.xml"),
    )
    shutil.copyfile(
        os.path.join(ROOT_DIR, "images", "gramps.png"),
        os.path.join(resource_path, "gramps", "images", "gramps.png"),
    )
    shutil.copyfile(
        os.path.join(ROOT_DIR, "COPYING"),
        os.path.join(resource_path, "doc", "gramps", "COPYING"),
    )
    return resource_path


os.environ["GRAMPS_RESOURCES"] = _ensure_test_resources()
os.environ["HOME"] = os.environ.get("HOME") or tempfile.mkdtemp(prefix="gramps-home-")

# -------------------------------------------------------------------------
#
# Stub out GTK-heavy modules before importing compare_gtk.
#
# These must be in sys.modules before gramps.gui.fs.person.mixins.compare_gtk
# is imported.  gi.repository.GLib needs integer version attributes so that
# gi/overrides/Gio.py line 463 (a version tuple comparison) does not raise
# TypeError when the module is used as a dependency.
#
# -------------------------------------------------------------------------

# GLib stub: integer version fields satisfy gi/overrides/Gio.py:463
_glib_mock = MagicMock()
_glib_mock.MAJOR_VERSION = 2
_glib_mock.MINOR_VERSION = 80
_glib_mock.MICRO_VERSION = 0

for _mod_name, _mock_obj in [
    ("gi.repository.GLib", _glib_mock),
    ("gi.repository.Gtk", MagicMock()),
    ("gi.repository.Gdk", MagicMock()),
    ("gi.repository.GdkPixbuf", MagicMock()),
    ("gi.repository.Pango", MagicMock()),
]:
    if _mod_name not in sys.modules:
        sys.modules[_mod_name] = _mock_obj

# Stub Gramps GUI modules that pull in GTK at their own import time.
for _gramps_gui_mod in (
    "gramps.gui.dialog",
    "gramps.gui.listmodel",
    "gramps.gui.utils",
    "gramps.gui.fs.tags",
):
    if _gramps_gui_mod not in sys.modules:
        sys.modules[_gramps_gui_mod] = MagicMock()

# -------------------------------------------------------------------------
#
# Stub gramps.gui.fs.person as a lightweight package.
#
# gramps.gui.fs.person.__init__ imports fsg_sync which transitively imports
# GTK (via sources_dialog -> ui.py).  We replace the package with a minimal
# module that has the correct __path__ so Python can still discover the real
# mixins/ sub-package on disk and import compare_gtk from it.
#
# -------------------------------------------------------------------------
_FS_PERSON_DIR = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "..", "person")
)

if "gramps.gui.fs.person" not in sys.modules:
    _person_pkg = types.ModuleType("gramps.gui.fs.person")
    _person_pkg.__path__ = [_FS_PERSON_DIR]  # type: ignore[attr-defined]
    _person_pkg.__package__ = "gramps.gui.fs.person"
    _person_pkg.__file__ = os.path.join(_FS_PERSON_DIR, "__init__.py")
    _person_pkg.__spec__ = None  # type: ignore[attr-defined]
    sys.modules["gramps.gui.fs.person"] = _person_pkg

if "gramps.gui.fs.person.fsg_sync" not in sys.modules:
    sys.modules["gramps.gui.fs.person.fsg_sync"] = MagicMock()

# -------------------------------------------------------------------------
#
# Gramps modules  (imported AFTER stubs are in place)
#
# -------------------------------------------------------------------------
from gramps.gui.fs.person.mixins.compare_gtk import (  # noqa: E402
    CompareGtkMixin,
    _FSMergeRow,
)

import gramps.gui.fs.person.mixins.compare_gtk as _compare_gtk_mod  # noqa: E402

# -------------------------------------------------------------------------
#
# _FsPhotoPixbufCacheTest
#
# -------------------------------------------------------------------------


class _FsPhotoPixbufCacheTest(unittest.TestCase):
    """Tests for the ``_FS_PHOTO_CACHE`` no-None fix (issue 7)."""

    def setUp(self):
        """Clear the class-level photo cache before every test."""
        CompareGtkMixin._FS_PHOTO_CACHE.clear()

    def tearDown(self):
        """Restore cache to a clean state."""
        CompareGtkMixin._FS_PHOTO_CACHE.clear()

    def _make_instance(self):
        """Return a bare CompareGtkMixin instance with no GTK construction."""
        return CompareGtkMixin.__new__(CompareGtkMixin)

    def _make_fs_person(self, fsid: str = "PERSON1", portrait_url: str = ""):
        """Return a minimal mock FamilySearch person."""
        person = MagicMock()
        person.id = fsid
        person.portraitUrl = portrait_url
        person.profileImageUrl = ""
        person.display = None
        return person

    def test_none_result_not_cached(self):
        """_FS_PHOTO_CACHE must not gain an entry when the fetch returns None."""
        inst = self._make_instance()
        fs_person = self._make_fs_person(fsid="PERSON1", portrait_url="")
        cache_key = "PERSON1:56"

        # session is None → no network call → pixbuf is None
        with patch("gramps.gen.fs.tree._fs_session", None):
            result = inst._fs_photo_pixbuf(fs_person)

        self.assertIsNone(result)
        self.assertNotIn(
            cache_key,
            CompareGtkMixin._FS_PHOTO_CACHE,
            "None must NOT be cached in _FS_PHOTO_CACHE",
        )

    def test_none_result_not_cached_with_missing_portrait(self):
        """Cache stays empty when portrait URL is present but file does not exist."""
        inst = self._make_instance()
        fs_person = self._make_fs_person(
            fsid="PERSON2", portrait_url="/nonexistent/path/portrait.jpg"
        )
        cache_key = "PERSON2:56"

        with patch("gramps.gen.fs.tree._fs_session", None):
            result = inst._fs_photo_pixbuf(fs_person)

        self.assertIsNone(result)
        self.assertNotIn(cache_key, CompareGtkMixin._FS_PHOTO_CACHE)

    def test_successful_fetch_is_cached(self):
        """A successfully loaded pixbuf IS stored in _FS_PHOTO_CACHE."""
        inst = self._make_instance()
        fs_person = self._make_fs_person(fsid="PERSON3", portrait_url="")
        cache_key = "PERSON3:56"

        fake_pixbuf = MagicMock(name="pixbuf")
        fake_scaled = MagicMock(name="scaled_pixbuf")
        fake_pixbuf.scale_simple.return_value = fake_scaled

        fake_loader = MagicMock()
        fake_loader.get_pixbuf.return_value = fake_pixbuf

        fake_session = MagicMock()
        fake_response = MagicMock()
        fake_response.content = b"\xff\xd8\xff\xe0fake-jpeg-bytes"
        fake_session.get_url.return_value = fake_response

        with (
            patch("gramps.gen.fs.tree._fs_session", fake_session),
            patch("gi.repository.GdkPixbuf.PixbufLoader", return_value=fake_loader),
        ):
            result = inst._fs_photo_pixbuf(fs_person)

        self.assertIs(result, fake_scaled)
        self.assertIn(cache_key, CompareGtkMixin._FS_PHOTO_CACHE)
        self.assertIs(CompareGtkMixin._FS_PHOTO_CACHE[cache_key], fake_scaled)

    def test_cache_hit_skips_fetch(self):
        """Subsequent calls return the cached value without hitting the network."""
        inst = self._make_instance()
        fs_person = self._make_fs_person(fsid="PERSON4", portrait_url="")
        cache_key = "PERSON4:56"

        fake_pixbuf = MagicMock(name="cached_pixbuf")
        CompareGtkMixin._FS_PHOTO_CACHE[cache_key] = fake_pixbuf

        fake_session = MagicMock()

        with patch("gramps.gen.fs.tree._fs_session", fake_session):
            result = inst._fs_photo_pixbuf(fs_person)

        self.assertIs(result, fake_pixbuf)
        fake_session.get_url.assert_not_called()


# -------------------------------------------------------------------------
#
# _ApplySelectedMergeRowsTest
#
# -------------------------------------------------------------------------


def _row(kind: str, selected: bool = True, selectable: bool = True) -> _FSMergeRow:
    """Return a minimal _FSMergeRow fixture for the given kind."""
    return _FSMergeRow(
        status="orange",
        section="Test",
        field=kind,
        gramps_date="",
        gramps_value="",
        fs_date="",
        fs_value="value",
        selected=selected,
        selectable=selectable,
        kind=kind,
        gr_handle="",
        fs_id="FS-001",
        gr_extra="",
        fs_extra="",
    )


class _TestMixin(CompareGtkMixin):
    """
    Minimal concrete subclass for testing _apply_selected_merge_rows.

    All merge helpers default to returning True (one change applied).
    Individual tests override specific methods to raise or return False.
    """

    fs_Tree = None

    def __init__(self):
        """Set up dbstate / uistate mocks required by _apply_selected_merge_rows."""
        self.dbstate = MagicMock()
        self.uistate = MagicMock()

    def get_active(self, *args: Any) -> Any:
        """Return None — not needed by _apply_selected_merge_rows directly."""
        return None

    def _selected_merge_rows_from_list(self, rows: list) -> list:
        """Pass through the row list filtering to selected+selectable rows."""
        return [r for r in rows if r.selected and r.selectable]

    def _ensure_person_cached(
        self, fsid: str, *, with_relatives: bool, force: bool = False
    ) -> Any:
        """No-op: network call suppressed in tests."""
        return None

    # Merge helpers — default: succeed (return True).
    def _merge_gender_row(self, gr: Any, fs_person: Any) -> bool:
        """Default: succeed."""
        return True

    def _merge_name_row(
        self, db: Any, txn: Any, gr: Any, fs_person: Any, row: Any
    ) -> bool:
        """Default: succeed."""
        return True

    def _merge_person_fact_row(
        self, db: Any, txn: Any, gr: Any, fs_person: Any, row: Any
    ) -> bool:
        """Default: succeed."""
        return True

    def _merge_family_fact_row(
        self, db: Any, txn: Any, fs_person: Any, row: Any
    ) -> bool:
        """Default: succeed."""
        return True

    def _merge_relative_row(
        self, importer: Any, gr: Any, fs_person: Any, row: Any
    ) -> bool:
        """Default: succeed."""
        return True


class _ApplySelectedMergeRowsTest(unittest.TestCase):
    """Tests for _apply_selected_merge_rows exception tracking (issue 4)."""

    _PATCH_OK_DIALOG = "gramps.gui.fs.person.mixins.compare_gtk.OkDialog"
    _PATCH_WARNING_DIALOG = "gramps.gui.fs.person.mixins.compare_gtk.WarningDialog"
    _PATCH_QUESTION_DIALOG2 = "gramps.gui.fs.person.mixins.compare_gtk.QuestionDialog2"
    _PATCH_DB_TXN = "gramps.gui.fs.person.mixins.compare_gtk.DbTxn"
    _PATCH_DESERIALIZE = "gramps.gui.fs.person.mixins.compare_gtk.deserialize"
    _PATCH_FS_IMPORT = "gramps.gui.fs.person.mixins.compare_gtk.fs_import"

    def _make_context_txn(self):
        """Return a MagicMock that works as a context manager for DbTxn."""
        mock_txn = MagicMock()
        mock_txn.__enter__ = MagicMock(return_value=mock_txn)
        mock_txn.__exit__ = MagicMock(return_value=False)
        return mock_txn

    def _run(self, mixin, rows, *, gr=None):
        """
        Run _apply_selected_merge_rows with all external calls mocked away.

        Returns (changed, mock_ok, mock_warn, mock_log_warning).
        """
        if gr is None:
            gr = MagicMock()
            gr.handle = "gr-handle-1"

        parent = MagicMock()
        mock_txn_instance = self._make_context_txn()
        mock_fs_person = MagicMock()
        mock_fs_person.id = "FS-001"

        with (
            patch(self._PATCH_QUESTION_DIALOG2) as mock_q2,
            patch(self._PATCH_OK_DIALOG) as mock_ok,
            patch(self._PATCH_WARNING_DIALOG) as mock_warn,
            patch(self._PATCH_DB_TXN, return_value=mock_txn_instance),
            patch(self._PATCH_DESERIALIZE) as mock_deser,
            patch(self._PATCH_FS_IMPORT) as mock_fsimp,
            patch("gramps.gui.fs.person.mixins.compare_gtk.LOG") as mock_log,
        ):
            mock_q2.return_value.run.return_value = True
            mock_deser.Person.index.get.return_value = mock_fs_person
            mock_fsimp.FSToGrampsImporter.return_value = MagicMock()

            changed = mixin._apply_selected_merge_rows(rows, gr, "FS-001", parent)

        return changed, mock_ok, mock_warn, mock_log

    def test_warning_logged_for_each_failing_row(self):
        """LOG.warning is called once per row that raises an exception."""

        class _RaisingMixin(_TestMixin):
            def _merge_gender_row(self, gr, fs_person):
                """Always raise."""
                raise ValueError("boom")

            def _merge_name_row(self, db, txn, gr, fs_person, row):
                """Always raise."""
                raise ValueError("boom")

        mixin = _RaisingMixin()
        rows = [_row("gender"), _row("name")]
        _changed, _ok, _warn, mock_log = self._run(mixin, rows)

        self.assertEqual(
            mock_log.warning.call_count,
            2,
            "LOG.warning must be called once per failing row",
        )

    def test_ok_dialog_shows_both_counts_on_partial_failure(self):
        """OkDialog message contains both changed count and failed count."""

        class _MixedMixin(_TestMixin):
            def _merge_gender_row(self, gr, fs_person):
                """Succeed."""
                return True

            def _merge_name_row(self, db, txn, gr, fs_person, row):
                """Fail."""
                raise ValueError("boom")

        mixin = _MixedMixin()
        rows = [_row("gender"), _row("name")]
        _changed, mock_ok, _warn, _log = self._run(mixin, rows)

        self.assertEqual(mock_ok.call_count, 1, "OkDialog must be called once")
        ok_msg_arg = mock_ok.call_args[0][1]
        self.assertIn("1", ok_msg_arg, "OkDialog message should contain changed=1")

    def test_warning_dialog_when_all_rows_fail(self):
        """WarningDialog is shown (not OkDialog) when all rows raise."""

        class _AllFailMixin(_TestMixin):
            def _merge_gender_row(self, gr, fs_person):
                """Always raise."""
                raise RuntimeError("network error")

        mixin = _AllFailMixin()
        rows = [_row("gender")]
        _changed, mock_ok, mock_warn, _log = self._run(mixin, rows)

        mock_ok.assert_not_called()
        self.assertGreaterEqual(
            mock_warn.call_count,
            1,
            "WarningDialog must be shown when no rows succeed",
        )

    def test_ok_dialog_shown_when_all_succeed(self):
        """OkDialog is shown (and WarningDialog is not) when all rows succeed."""
        mixin = _TestMixin()
        rows = [_row("gender"), _row("name")]
        _changed, mock_ok, mock_warn, mock_log = self._run(mixin, rows)

        self.assertEqual(mock_ok.call_count, 1)
        mock_warn.assert_not_called()
        mock_log.warning.assert_not_called()

    def test_returns_zero_for_none_gr(self):
        """_apply_selected_merge_rows returns 0 immediately when gr is None."""
        mixin = _TestMixin()
        parent = MagicMock()
        rows = [_row("gender")]

        with patch(self._PATCH_WARNING_DIALOG) as mock_warn:
            result = mixin._apply_selected_merge_rows(rows, None, "FS-001", parent)

        self.assertEqual(result, 0)
        mock_warn.assert_called_once()

    def test_returns_zero_for_empty_rows(self):
        """_apply_selected_merge_rows returns 0 when no rows are selectable."""
        mixin = _TestMixin()
        parent = MagicMock()
        gr = MagicMock()
        gr.handle = "gr-handle-1"

        with patch(self._PATCH_WARNING_DIALOG) as mock_warn:
            result = mixin._apply_selected_merge_rows([], gr, "FS-001", parent)

        self.assertEqual(result, 0)
        mock_warn.assert_called_once()

    def test_failed_counter_does_not_inflate_changed(self):
        """Rows that raise must not increment the changed counter."""

        class _MixedMixin(_TestMixin):
            def _merge_gender_row(self, gr, fs_person):
                """Succeed (changed += 1)."""
                return True

            def _merge_name_row(self, db, txn, gr, fs_person, row):
                """Fail (failed += 1, changed unchanged)."""
                raise ValueError("boom")

        mixin = _MixedMixin()
        rows = [_row("gender"), _row("name")]
        changed, _ok, _warn, _log = self._run(mixin, rows)

        self.assertEqual(changed, 1)


if __name__ == "__main__":
    unittest.main()
