"""Unittest for glade.py

Regression test for the ``Glade.__setattr__`` guard introduced by
f8c1fc0f50 ("Don't use slots on GObject-derived classes."), which made every
``Glade()`` construction abort GUI startup (testbed #1):

  1. The guard whitelisted the *unmangled* names ``__toplevel``/``__filename``/
     ``__dirname``, but ``__init__`` assigns ``self.__dirname`` etc., which
     Python name-mangles to ``_Glade__dirname`` -- so the guard rejected the
     class's own assignments with ``AttributeError`` at the very first
     ``self.__dirname, self.__filename = os.path.split(path)`` line.
  2. ``super().__setattr__(self, name, value)`` passed ``self`` twice to an
     already-bound ``super()`` method, raising ``TypeError`` once the guard was
     satisfied.

The test drives the *real* ``Glade.__init__`` path end-to-end -- it loads an
actual ``.glade`` file through ``Gtk.Builder`` -- so the fix is exercised the
way GUI startup uses it, not via a synthetic ``__setattr__`` bypass. To stay
runnable under the headless C4 unittest runner (no display / D-Bus / AT-SPI),
the loaded glade file contains a single *non-widget* toplevel (a
``GtkListStore``): building it needs the GObject type system but no display.
"""

import os
import tempfile
import unittest

from gramps.gui.glade import Glade

# A minimal, display-free glade file: one non-widget toplevel object so that
# Gtk.Builder can build it on a headless box (no realised widgets).
_GLADE_LISTSTORE = """<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <object class="GtkListStore" id="test_store">
    <columns>
      <column type="gchararray"/>
    </columns>
  </object>
</interface>
"""


class GladeConstructionTest(unittest.TestCase):
    """Constructing a Glade must run __init__'s guarded assignments cleanly."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._dirname = self._tmpdir.name
        self._filename = "regtest.glade"
        with open(
            os.path.join(self._dirname, self._filename), "w", encoding="utf-8"
        ) as handle:
            handle.write(_GLADE_LISTSTORE)

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_real_construction_succeeds(self):
        # The real __init__ path. Pre-fix this aborts with AttributeError
        # ("Ad-hoc attribute _Glade__dirname is not permitted.") at the first
        # `self.__dirname, self.__filename = os.path.split(path)` assignment,
        # or TypeError from the doubled `self` once the whitelist is corrected.
        # Post-fix it loads the file and assigns all three mangled privates.
        glade = Glade(
            filename=self._filename,
            dirname=self._dirname,
            toplevel="test_store",
        )
        # The three private attributes __init__ assigns via the guarded
        # __setattr__, exposed through the public @property getters.
        self.assertEqual(glade.dirname, self._dirname)
        self.assertEqual(glade.filename, self._filename)
        self.assertIsNotNone(glade.toplevel)
        self.assertIsNotNone(glade.get_object("test_store"))

    def test_adhoc_attr_still_rejected(self):
        # The guard's purpose -- rejecting genuinely unexpected attributes --
        # must be preserved by the fix.
        glade = Glade(
            filename=self._filename,
            dirname=self._dirname,
            toplevel="test_store",
        )
        with self.assertRaises(AttributeError):
            glade.some_unexpected_attr = 1


if __name__ == "__main__":
    unittest.main()
