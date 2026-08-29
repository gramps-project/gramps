#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gramps developers
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""Regression test for bug #12260.

Creating a *new* linked object from the Link Editor must not crash when the
inner editor's "new object created" callback emits a bare handle *string*
instead of an object.  EditCitation (``editcitation.py`` ``save`` →
``self.callback(self.obj.get_handle())``) does exactly that, so driving
``EditLink._on_new_callback`` with a ``str`` reproduced
``AttributeError: 'str' object has no attribute 'handle'``.

The test exercises the *production* ``EditLink._on_new_callback`` directly (an
instance built with ``__new__`` so no GTK toplevel is realised), not a copy of
it.
"""

import unittest
from unittest.mock import Mock

from gramps.gen.lib import Note
from gramps.gui.editors.editlink import EditLink, NOTE


def _make_editlink(active):
    """Build an EditLink without running its GTK __init__.

    Only the attributes ``_on_new_callback`` touches are stubbed, so the test
    drives the real method on a real EditLink instance.
    """
    link = EditLink.__new__(EditLink)
    link.uri_list = Mock()
    link.uri_list.get_active.return_value = active
    link.selected = Mock()
    link.url_link = Mock()
    link.simple_access = Mock()
    link.simple_access.display.return_value = "displayed"
    return link


class TestOnNewCallback(unittest.TestCase):
    def test_handle_string_callback_builds_link(self):
        """A handle *string* (as EditCitation/EditNote emit) must not raise."""
        link = _make_editlink(NOTE)
        # Pre-fix this raised AttributeError: 'str' object has no attribute
        # 'handle'.
        link._on_new_callback("abc123handle")
        link.url_link.set_text.assert_called_once_with(
            "gramps://Note/handle/abc123handle"
        )
        link.selected.set_text.assert_called_once_with("displayed")

    def test_object_callback_still_builds_link(self):
        """Object-passing editors (the majority) keep working unchanged."""
        link = _make_editlink(NOTE)
        note = Note()
        note.set_handle("objhandle")
        link._on_new_callback(note)
        link.url_link.set_text.assert_called_once_with("gramps://Note/handle/objhandle")


if __name__ == "__main__":
    unittest.main()
