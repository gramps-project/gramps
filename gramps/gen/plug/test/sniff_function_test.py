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

"""
Tests for the sniff_function dispatch mechanism on ImportPlugin.
"""

# ------------------------
# Python modules
# ------------------------
import unittest

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.plug._import import ImportPlugin


def _make_plugin(name, extension, sniff_fn=None):
    """Return a minimal ImportPlugin for testing."""

    def _import(db, filename, user):
        """Stub import function."""

    _import.__module__ = "test"
    return ImportPlugin(
        name=name,
        description="",
        import_function=_import,
        extension=extension,
        sniff_function=sniff_fn,
    )


def _choose(plugins, extension, filename):
    """Re-implementation of the dispatch logic under test."""
    candidates = [p for p in plugins if extension == p.get_extension()]
    for plugin in candidates:
        sniff = plugin.get_sniff_function()
        if sniff is not None:
            try:
                if sniff(filename):
                    return plugin
            except Exception:  # pylint: disable=broad-except
                pass
    for plugin in candidates:
        if plugin.get_sniff_function() is None:
            return plugin
    return None


class TestImportPluginSniffFunction(unittest.TestCase):
    """Tests for ImportPlugin.get_sniff_function()."""

    def test_no_sniff_function_returns_none(self):
        """
        A plugin created without a sniff_function returns None from
        get_sniff_function().
        """
        plugin = _make_plugin("Legacy", "ged")
        self.assertIsNone(plugin.get_sniff_function())

    def test_sniff_function_stored_and_returned(self):
        """
        A plugin created with a sniff_function returns that callable from
        get_sniff_function().
        """
        sniff = lambda f: True
        plugin = _make_plugin("Modern", "ged", sniff_fn=sniff)
        self.assertIs(plugin.get_sniff_function(), sniff)


class TestChooseImportPlugin(unittest.TestCase):
    """Tests for the sniff-aware plugin selection logic."""

    def test_fallback_when_no_sniff_plugins(self):
        """
        When no plugin has a sniff function the first extension match is
        returned.
        """
        p1 = _make_plugin("A", "ged")
        p2 = _make_plugin("B", "ged")
        result = _choose([p1, p2], "ged", "family.ged")
        self.assertIs(result, p1)

    def test_sniff_winner_beats_fallback(self):
        """
        A plugin whose sniff function returns True is preferred over a
        fallback plugin that has no sniff function.
        """
        fallback = _make_plugin("Legacy", "ged")
        winner = _make_plugin("Modern", "ged", sniff_fn=lambda f: True)
        result = _choose([fallback, winner], "ged", "family.ged")
        self.assertIs(result, winner)

    def test_sniff_false_falls_through_to_fallback(self):
        """
        A plugin whose sniff function returns False does not win; the
        fallback (no sniff function) is returned instead.
        """
        rejector = _make_plugin("Modern", "ged", sniff_fn=lambda f: False)
        fallback = _make_plugin("Legacy", "ged")
        result = _choose([rejector, fallback], "ged", "family.ged")
        self.assertIs(result, fallback)

    def test_sniff_exception_falls_through(self):
        """
        If the sniff function raises an exception the plugin is skipped and
        the fallback is used.
        """

        def _bad_sniff(filename):
            """Sniff function that always raises."""
            raise RuntimeError("sniff failed")

        rejector = _make_plugin("Broken", "ged", sniff_fn=_bad_sniff)
        fallback = _make_plugin("Legacy", "ged")
        result = _choose([rejector, fallback], "ged", "family.ged")
        self.assertIs(result, fallback)

    def test_no_matching_extension_returns_none(self):
        """When no plugin matches the extension, None is returned."""
        plugin = _make_plugin("CSV", "csv")
        result = _choose([plugin], "ged", "family.ged")
        self.assertIsNone(result)

    def test_all_sniff_false_no_fallback_returns_none(self):
        """
        When every candidate has a sniff function that returns False and
        there is no fallback plugin, None is returned.
        """
        p1 = _make_plugin("A", "ged", sniff_fn=lambda f: False)
        p2 = _make_plugin("B", "ged", sniff_fn=lambda f: False)
        result = _choose([p1, p2], "ged", "family.ged")
        self.assertIsNone(result)

    def test_first_sniff_true_wins_among_multiple_sniffers(self):
        """
        When multiple plugins have sniff functions that return True, the
        first one encountered wins.
        """
        p1 = _make_plugin("First", "ged", sniff_fn=lambda f: True)
        p2 = _make_plugin("Second", "ged", sniff_fn=lambda f: True)
        result = _choose([p1, p2], "ged", "family.ged")
        self.assertIs(result, p1)

    def test_sniff_receives_filename(self):
        """The sniff function is called with the filename argument."""
        received = []

        def _record_sniff(filename):
            """Record the filename passed to the sniff function."""
            received.append(filename)
            return True

        plugin = _make_plugin("Recorder", "ged", sniff_fn=_record_sniff)
        _choose([plugin], "ged", "/path/to/family.ged")
        self.assertEqual(received, ["/path/to/family.ged"])


if __name__ == "__main__":
    unittest.main()
