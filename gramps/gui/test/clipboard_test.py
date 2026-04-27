"""Tests for clipboard save/load persistence (save_clipboard, load_clipboard)."""

import base64
import json
import os
import pickle
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Stub out GTK/GI imports before anything else touches them.
# ---------------------------------------------------------------------------
for _mod in (
    "gi",
    "gi.repository",
    "gi.repository.GObject",
    "gi.repository.Gdk",
    "gi.repository.Gtk",
    "gi.repository.GdkPixbuf",
    "gi.repository.Pango",
    "cairo",
):
    sys.modules.setdefault(_mod, MagicMock())

# Gtk.ListStore must be a real class so ClipboardListModel can subclass it.
sys.modules["gi.repository.Gtk"].ListStore = object


# ---------------------------------------------------------------------------
# Provide real stub classes for the Gramps GUI modules that clipboard.py
# imports, so that class inheritance works correctly.
# ---------------------------------------------------------------------------


class _FakeManagedWindow:
    def __init__(self, *args, **kwargs):
        pass


_fake_mw_mod = MagicMock()
_fake_mw_mod.ManagedWindow = _FakeManagedWindow
sys.modules["gramps.gui.managedwindow"] = _fake_mw_mod

for _mod in (
    "gramps.gui.widgets.multitreeview",
    "gramps.gui.glade",
    "gramps.gui.ddtargets",
    "gramps.gui.makefilter",
    "gramps.gui.display",
    "gramps.gui.utils",
):
    sys.modules.setdefault(_mod, MagicMock())

# Minimal DdTargets stub so _build_drag_type_map() can build its dict.
_dd = MagicMock()


def _make_target(drag_type):
    t = MagicMock()
    t.drag_type = drag_type
    return t


_dd.ADDRESS = _make_target("address")
_dd.LOCATION = _make_target("location")
_dd.EVENT = _make_target("pevent")
_dd.PLACE_LINK = _make_target("place-link")
_dd.NOTE_LINK = _make_target("note-link")
_dd.FAMILY_EVENT = _make_target("family-event")
_dd.URL = _make_target("url")
_dd.ATTRIBUTE = _make_target("attribute")
_dd.FAMILY_ATTRIBUTE = _make_target("family-attribute")
_dd.CITATION_LINK = _make_target("citation-link")
_dd.REPOREF = _make_target("reporef")
_dd.EVENTREF = _make_target("eventref")
_dd.PLACEREF = _make_target("placeref")
_dd.NAME = _make_target("name")
_dd.PLACENAME = _make_target("placename")
_dd.SURNAME = _make_target("surname")
_dd.MEDIAOBJ = _make_target("media")
_dd.MEDIAREF = _make_target("mediaref")
_dd.PERSONREF = _make_target("personref")
_dd.CHILDREF = _make_target("childref")
_dd.PERSON_LINK = _make_target("person-link")
_dd.FAMILY_LINK = _make_target("family-link")
_dd.SOURCE_LINK = _make_target("source-link")
_dd.REPO_LINK = _make_target("repo-link")
_dd.TEXT = _make_target("TEXT")
_dd.LINK_LIST = _make_target("link-list")
_dd.RAW_LIST = _make_target("raw-list")
_dd.HANDLE_LIST = _make_target("handle-list")
_dd.all_targets = MagicMock(return_value=[])
_dd.all_text = MagicMock(return_value=[_dd.TEXT])
sys.modules["gramps.gui.ddtargets"].DdTargets = _dd

# ---------------------------------------------------------------------------
# Now import the module under test.
# ---------------------------------------------------------------------------
import gramps.gui.clipboard as clipboard_module
from gramps.gui.clipboard import (
    ClipboardWindow,
    ClipObjWrapper,
    _build_drag_type_map,
)

# ---------------------------------------------------------------------------
# Lightweight test helpers
# ---------------------------------------------------------------------------


def _make_handle_wrapper(
    drag_type="person-link",
    handle="HANDLE001",
    dbid="db-A",
    dbname="Tree A",
    title="P0001",
    value="Smith, John",
):
    """Return a mock that looks like a ClipHandleWrapper row entry."""
    raw = pickle.dumps((drag_type, 0, handle, 0))
    w = MagicMock()
    w._obj = raw
    w._pickle = raw
    w._title = title
    w._value = value
    w._type = "Person"
    w._dbid = dbid
    w._dbname = dbname
    # isinstance(w, ClipObjWrapper) must be False
    w.__class__ = MagicMock  # not ClipObjWrapper
    return w, drag_type, raw


def _make_obj_wrapper(
    drag_type="address",
    dbid="db-B",
    dbname="Tree B",
    title="1900-01-01",
    value="123 Main St",
):
    """Return a mock that looks like a ClipObjWrapper row entry."""
    raw = pickle.dumps((drag_type, 0, "some-obj", 0))
    w = MagicMock()
    w._obj = MagicMock()  # unpickled Gramps object — NOT bytes
    w._pickle = raw  # original bytes — what save_clipboard should use
    w._title = title
    w._value = value
    w._type = "Address"
    w._dbid = dbid
    w._dbname = dbname
    w.__class__ = ClipObjWrapper  # isinstance check must be True
    return w, drag_type, raw


class FakeRow:
    def __init__(self, drag_type, wrapper):
        self._data = [drag_type, wrapper]

    def __getitem__(self, i):
        return self._data[i]


class FakeModel:
    def __init__(self, rows=()):
        self._rows = list(rows)

    def __iter__(self):
        return iter(self._rows)

    def __len__(self):
        return len(self._rows)

    def append(self, row):
        self._rows.append(row)


# ---------------------------------------------------------------------------
# Tests for _build_drag_type_map
# ---------------------------------------------------------------------------


class TestBuildDragTypeMap(unittest.TestCase):

    def test_returns_dict(self):
        self.assertIsInstance(_build_drag_type_map(), dict)

    def test_person_link_present(self):
        self.assertIn("person-link", _build_drag_type_map())

    def test_text_present(self):
        self.assertIn("TEXT", _build_drag_type_map())

    def test_no_none_keys(self):
        self.assertNotIn(None, _build_drag_type_map())


# ---------------------------------------------------------------------------
# Tests for save_clipboard / load_clipboard
# ---------------------------------------------------------------------------


class TestSaveLoadRoundTrip(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        self._tmp.close()
        self._orig_file = clipboard_module.CLIPBOARD_FILE
        clipboard_module.CLIPBOARD_FILE = self._tmp.name
        self._orig_otree = ClipboardWindow.otree

    def tearDown(self):
        clipboard_module.CLIPBOARD_FILE = self._orig_file
        ClipboardWindow.otree = self._orig_otree
        if os.path.exists(self._tmp.name):
            os.unlink(self._tmp.name)

    # helpers

    def _save_with(self, rows):
        ClipboardWindow.otree = FakeModel(rows)
        ClipboardWindow.save_clipboard()
        with open(self._tmp.name) as f:
            return json.load(f)

    def _write_file(self, items):
        with open(self._tmp.name, "w") as f:
            json.dump(items, f)

    def _load_with_mock_wrapper(
        self,
        drag_type,
        raw,
        saved_dbid,
        saved_dbname,
        saved_title,
        saved_value,
        constructor_dbid="db-CURRENT",
    ):
        """Load from file using a mock wrapper class, return the appended row."""
        self._write_file(
            [
                {
                    "drag_type": drag_type,
                    "data": base64.b64encode(raw).decode("ascii"),
                    "title": saved_title,
                    "value": saved_value,
                    "dbid": saved_dbid,
                    "dbname": saved_dbname,
                }
            ]
        )
        ClipboardWindow.otree = FakeModel()
        mock_wrapper = MagicMock()
        mock_wrapper._type = "Person"
        mock_wrapper._title = "Unavailable"
        mock_wrapper._value = "Unavailable"
        mock_wrapper._dbid = constructor_dbid
        mock_wrapper._dbname = "Current Tree"
        wrapper_class_mock = MagicMock(return_value=mock_wrapper)
        wrapper_class_mock.DRAG_TARGET.drag_type = drag_type
        with patch("gramps.gui.clipboard._build_drag_type_map") as mock_map:
            mock_map.return_value = {drag_type: wrapper_class_mock}
            ClipboardWindow.load_clipboard()
        return ClipboardWindow.otree._rows[0]

    # --- save tests ---

    def test_save_handle_wrapper_encodes_raw_bytes(self):
        w, dt, raw = _make_handle_wrapper()
        saved = self._save_with([FakeRow(dt, w)])
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0]["drag_type"], dt)
        self.assertEqual(base64.b64decode(saved[0]["data"]), raw)

    def test_save_preserves_title_value_dbid_dbname(self):
        w, dt, _ = _make_handle_wrapper(
            dbid="db-X", dbname="Other Tree", title="P999", value="Doe, Jane"
        )
        saved = self._save_with([FakeRow(dt, w)])
        self.assertEqual(saved[0]["dbid"], "db-X")
        self.assertEqual(saved[0]["dbname"], "Other Tree")
        self.assertEqual(saved[0]["title"], "P999")
        self.assertEqual(saved[0]["value"], "Doe, Jane")

    def test_save_obj_wrapper_uses_pickle_not_obj(self):
        """For ClipObjWrapper, _pickle (original bytes) must be saved, not _obj."""
        w, dt, raw = _make_obj_wrapper()
        saved = self._save_with([FakeRow(dt, w)])
        self.assertEqual(len(saved), 1)
        self.assertEqual(base64.b64decode(saved[0]["data"]), raw)

    def test_save_empty_model_writes_empty_list(self):
        self.assertEqual(self._save_with([]), [])

    def test_save_multiple_items(self):
        w1, dt1, _ = _make_handle_wrapper(drag_type="person-link", dbid="db-A")
        w2, dt2, _ = _make_obj_wrapper(drag_type="address", dbid="db-B")
        saved = self._save_with([FakeRow(dt1, w1), FakeRow(dt2, w2)])
        self.assertEqual(len(saved), 2)
        self.assertEqual(saved[0]["dbid"], "db-A")
        self.assertEqual(saved[1]["dbid"], "db-B")

    def test_save_skips_item_with_none_raw(self):
        w, dt, _ = _make_handle_wrapper()
        w._obj = None
        w.__class__ = MagicMock  # not ClipObjWrapper, so _obj is used
        saved = self._save_with([FakeRow(dt, w)])
        self.assertEqual(saved, [])

    def test_save_none_otree_leaves_file_unchanged(self):
        with open(self._tmp.name, "w") as f:
            f.write("sentinel")
        ClipboardWindow.otree = None
        ClipboardWindow.save_clipboard()
        with open(self._tmp.name) as f:
            self.assertEqual(f.read(), "sentinel")

    # --- load tests ---

    def test_load_restores_dbid_from_another_database(self):
        """Items from another db must keep their original dbid, not the current one."""
        _, dt, raw = _make_handle_wrapper()
        row = self._load_with_mock_wrapper(
            dt,
            raw,
            saved_dbid="db-OTHER",
            saved_dbname="Foreign Tree",
            saved_title="P0001",
            saved_value="Smith, John",
            constructor_dbid="db-CURRENT",  # constructor would stamp this wrong
        )
        self.assertEqual(row[5], "db-OTHER")
        self.assertEqual(row[6], "Foreign Tree")

    def test_load_restores_title_and_value(self):
        # col 3 = wrapper._type ("Person"), col 4 = wrapper._value.
        # _title lives on the wrapper object, not in a model column.
        _, dt, raw = _make_handle_wrapper()
        row = self._load_with_mock_wrapper(
            dt,
            raw,
            saved_dbid="db-A",
            saved_dbname="Tree A",
            saved_title="Saved Title",
            saved_value="Saved Value",
        )
        self.assertEqual(row[4], "Saved Value")  # value in col 4
        self.assertEqual(row[1]._title, "Saved Title")  # title on wrapper

    def test_load_skips_unknown_drag_type(self):
        self._write_file(
            [
                {
                    "drag_type": "no-such-type",
                    "data": base64.b64encode(b"x").decode("ascii"),
                    "title": "T",
                    "value": "V",
                    "dbid": "x",
                    "dbname": "y",
                }
            ]
        )
        ClipboardWindow.otree = FakeModel()
        ClipboardWindow.load_clipboard()
        self.assertEqual(len(ClipboardWindow.otree), 0)

    def test_load_missing_file_does_nothing(self):
        os.unlink(self._tmp.name)
        ClipboardWindow.otree = FakeModel()
        ClipboardWindow.load_clipboard()
        self.assertEqual(len(ClipboardWindow.otree), 0)

    def test_load_corrupt_json_does_nothing(self):
        with open(self._tmp.name, "w") as f:
            f.write("not valid json {{{")
        ClipboardWindow.otree = FakeModel()
        ClipboardWindow.load_clipboard()
        self.assertEqual(len(ClipboardWindow.otree), 0)

    def test_save_then_load_round_trip(self):
        """Full round-trip: save a wrapper, load it back, check all fields."""
        w, dt, raw = _make_handle_wrapper(
            dbid="db-B", dbname="Tree B", title="P0042", value="Jones, Bob"
        )
        self._save_with([FakeRow(dt, w)])

        row = self._load_with_mock_wrapper(
            dt,
            raw,
            saved_dbid="db-B",
            saved_dbname="Tree B",
            saved_title="P0042",
            saved_value="Jones, Bob",
            constructor_dbid="db-A",  # current db differs — must still restore B
        )
        self.assertEqual(row[0], dt)
        self.assertEqual(row[4], "Jones, Bob")
        self.assertEqual(row[5], "db-B")
        self.assertEqual(row[6], "Tree B")


if __name__ == "__main__":
    unittest.main()
