#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Eduard Ralph
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

"""Unit test for ``SelectionWidget._button_release_event`` — Mantis 13059.

Mantis 0013059 (dup of 0012659): in Photo Tagging, after dragging a box
edge to resize and releasing, a subsequent single CLICK (not drag) inside
that same box raises ``TypeError: set_coords() argument after * must be an
iterable, not NoneType`` from
``gramps/gui/widgets/selectionwidget.py:_button_release_event``.

The release-event handler enters its ``else: # update current selection``
branch (grabber is ``INSIDE``, not a corner / edge grabber and not ``None``
either), then unconditionally calls
``self.current.set_coords(*self.selection)``. On that specific path
``self.selection`` is ``None``: the prior resize-release set
``self.grabber = INSIDE`` and the click that followed never rebuilt
``self.selection``.

The fix guards both ``set_coords(*self.selection)`` call sites in the
release handler with ``if self.selection is not None``. This test
reproduces the buggy path without any GTK display by constructing a
``SelectionWidget`` instance via ``__new__`` (bypassing ``__init__``,
which would require a real ``Gtk.Builder`` / GTK loop), wiring just the
attributes the release handler reads, and asserting that the bug-13059
sequence no longer raises.
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

# Gramps targets GTK 3 throughout (see ``gramps/grampsapp.py``); the
# ``IconSize.MENU`` enum the widgets module touches at import time is
# GTK 3-only. Pin the introspected version BEFORE any ``gramps.gui``
# import so the module chain loads against the right ABI.
import gi  # noqa: E402

gi.require_version("Gtk", "3.0")  # noqa: E402

from gi.repository import Gdk  # noqa: E402

from gramps.gui.widgets.grabbers import INSIDE  # noqa: E402
from gramps.gui.widgets.selectionwidget import (  # noqa: E402
    Region,
    SelectionWidget,
)


# -----------------------------------------------------------
#
# _FakeEvent
#
# -----------------------------------------------------------
class _FakeEvent:
    """Minimal Gdk.EventButton stand-in for the release handler.

    Only ``button``, ``x`` and ``y`` are read by ``_button_release_event``.
    """

    def __init__(self, x: float, y: float) -> None:
        self.button = 1  # left mouse button
        self.x = x
        self.y = y


# -----------------------------------------------------------
#
# SelectionWidgetClickAfterResizeTest
#
# -----------------------------------------------------------
class SelectionWidgetClickAfterResizeTest(unittest.TestCase):
    """Regression test for Mantis 13059 (and its 0012659 duplicate)."""

    def _make_widget(self) -> SelectionWidget:
        """Construct a ``SelectionWidget`` without running ``__init__``.

        ``SelectionWidget.__init__`` builds a full ``Gtk.ScrolledWindow``
        and a builder-loaded image area — that needs a live GTK display.
        The release-event handler under test only reads a small set of
        attributes; setting them directly is enough to exercise the path
        without any display.
        """
        widget = SelectionWidget.__new__(SelectionWidget)
        widget.loaded = True  # is_image_loaded() reads cls.loaded
        widget.start_point_screen = (5.0, 5.0)
        widget.multiple_selection = False
        widget.image = MagicMock()  # refresh() does image.queue_draw()
        # emit() is a Gtk method — bypass with a counting stub so the
        # test sees which signals would have fired.
        widget.emit = MagicMock()
        return widget

    def test_click_after_resize_with_none_selection_does_not_raise(self) -> None:
        """Mantis 13059 repro path: ``grabber == INSIDE`` + ``selection is
        None`` must NOT raise ``TypeError`` on left-button release.

        Before the fix, the ``else: # update current selection`` branch
        in ``_button_release_event`` called
        ``self.current.set_coords(*self.selection)`` unconditionally; with
        ``self.selection is None`` Python raised ``TypeError`` from the
        ``*None`` unpack before ``set_coords`` could even be invoked.
        """
        widget = self._make_widget()
        widget.current = Region(0, 0, 10, 10)
        widget.selection = None  # ← the bug condition
        widget.grabber = INSIDE  # picks the else-branch in the handler

        try:
            widget._button_release_event(MagicMock(), _FakeEvent(5.0, 5.0))
        except TypeError as exc:
            self.fail(
                f"_button_release_event raised TypeError on the bug-13059 "
                f"path (current set, selection=None, grabber=INSIDE): {exc!r}"
            )

        # The region's stored coords must not have been disturbed when
        # selection was None — the safe no-op for this branch.
        self.assertEqual((widget.current.x1, widget.current.y1), (0, 0))
        self.assertEqual((widget.current.x2, widget.current.y2), (10, 10))

    def test_grabber_edge_release_with_none_selection_does_not_raise(self) -> None:
        """Defense in depth: the grabber-edge branch (line 770-ish) also
        calls ``set_coords(*self.selection)``. Even though
        ``_modify_selection`` is supposed to populate ``self.selection``,
        a future regression there shouldn't crash gramps -- guard both
        call sites the same way.
        """
        widget = self._make_widget()
        widget.current = Region(0, 0, 10, 10)
        widget.selection = None
        widget.grabber = 1  # any non-INSIDE, non-None grabber value

        # ``_modify_selection`` would normally write to widget.selection.
        # Stub it to a no-op so the guard's contribution is what's tested.
        # The instance was built via ``__new__`` — no live widget exists
        # to ``patch.object`` against — so a direct attribute assignment
        # is the simplest stub. mypy flags this as ``[method-assign]``
        # against the typed SelectionWidget._modify_selection; the
        # ignore is justified by the deliberate fixture-only context.
        widget._modify_selection = MagicMock(return_value=1)  # type: ignore[method-assign]

        try:
            widget._button_release_event(MagicMock(), _FakeEvent(5.0, 5.0))
        except TypeError as exc:
            self.fail(
                f"_button_release_event raised TypeError on the grabber-edge "
                f"branch with selection=None: {exc!r}"
            )

    def test_click_with_valid_selection_still_updates_region(self) -> None:
        """Sanity check that the guard is conservative — when
        ``selection`` IS set the normal update path still runs.
        """
        widget = self._make_widget()
        widget.current = Region(0, 0, 10, 10)
        widget.selection = (2, 3, 12, 14)
        widget.grabber = INSIDE

        widget._button_release_event(MagicMock(), _FakeEvent(5.0, 5.0))

        self.assertEqual(widget.current.x1, 2)
        self.assertEqual(widget.current.y1, 3)
        self.assertEqual(widget.current.x2, 12)
        self.assertEqual(widget.current.y2, 14)
        widget.emit.assert_any_call("region-modified")


# -----------------------------------------------------------
#
# _FakeScrollEvent
#
# -----------------------------------------------------------
class _FakeScrollEvent:
    """Minimal Gdk.EventScroll stand-in for the scroll handler."""

    def __init__(
        self,
        direction: Gdk.ScrollDirection,
        delta_y: float = 0.0,
        emulated: bool = False,
        is_stop: bool = False,
    ) -> None:
        self.direction = direction
        self.delta_x = 0.0
        self.delta_y = delta_y
        self.is_stop = is_stop
        self._emulated = emulated

    def get_pointer_emulated(self) -> bool:
        """Mirror ``Gdk.Event.get_pointer_emulated``."""
        return self._emulated


# -----------------------------------------------------------
#
# SelectionWidgetScrollZoomTest
#
# -----------------------------------------------------------
class SelectionWidgetScrollZoomTest(unittest.TestCase):
    """Tests for zooming via ``SelectionWidget._motion_scroll_event``.

    Touchpads deliver many small smooth scroll events per swipe, and some
    backends (notably quartz on macOS) also deliver an emulated legacy
    UP/DOWN event alongside each smooth one. Zooming a full step on every
    event made the zoom far too fast and erratic.
    """

    def setUp(self) -> None:
        """Construct a ``SelectionWidget`` without running ``__init__``.

        ``zoom_in`` / ``zoom_out`` are stubbed so the tests can count zoom
        steps without needing a loaded pixbuf or a display.
        """
        self.widget = SelectionWidget.__new__(SelectionWidget)
        self.widget.loaded = True
        self.widget.scroll_zoom_step = 1.0
        self.widget.scroll_accumulator = 0.0
        self.zoom_in = MagicMock()
        self.zoom_out = MagicMock()
        self.widget.zoom_in = self.zoom_in  # type: ignore[method-assign]
        self.widget.zoom_out = self.zoom_out  # type: ignore[method-assign]

    def _scroll(self, event: _FakeScrollEvent) -> bool:
        """Deliver a scroll event to the widget under test."""
        return self.widget._motion_scroll_event(self.widget, event)  # type: ignore[arg-type]

    def test_no_image_propagates_event(self) -> None:
        """Without an image the event is left for the scrolled window."""
        widget = self.widget
        widget.loaded = False
        event = _FakeScrollEvent(Gdk.ScrollDirection.UP)
        self.assertFalse(self._scroll(event))
        self.zoom_in.assert_not_called()

    def test_legacy_directions_zoom_one_step_and_stop_event(self) -> None:
        """A real wheel notch zooms one step and stops propagation, so the
        scrolled window does not also scroll the viewport."""
        result = self._scroll(_FakeScrollEvent(Gdk.ScrollDirection.UP))
        self.assertTrue(result)
        self.zoom_in.assert_called_once()
        self._scroll(_FakeScrollEvent(Gdk.ScrollDirection.DOWN))
        self.zoom_out.assert_called_once()

    def test_emulated_events_are_ignored(self) -> None:
        """Emulated UP/DOWN duplicates of smooth events must not zoom."""
        result = self._scroll(_FakeScrollEvent(Gdk.ScrollDirection.UP, emulated=True))
        self.assertTrue(result)
        self.zoom_in.assert_not_called()
        self.zoom_out.assert_not_called()

    def test_smooth_deltas_accumulate_to_one_step(self) -> None:
        """Small smooth deltas only zoom once a full step is accumulated."""
        widget = self.widget
        for _ in range(4):
            self._scroll(_FakeScrollEvent(Gdk.ScrollDirection.SMOOTH, delta_y=-0.3))
        self.zoom_in.assert_called_once()
        self.zoom_out.assert_not_called()
        self.assertAlmostEqual(widget.scroll_accumulator, -0.2)

    def test_smooth_step_size_is_respected(self) -> None:
        """Backends with pixel deltas use a larger ``scroll_zoom_step``, and a
        large delta produces the corresponding number of steps."""
        widget = self.widget
        widget.scroll_zoom_step = 50.0
        self._scroll(_FakeScrollEvent(Gdk.ScrollDirection.SMOOTH, delta_y=130.0))
        self.assertEqual(self.zoom_out.call_count, 2)
        self.assertAlmostEqual(widget.scroll_accumulator, 30.0)

    def test_horizontal_smooth_scroll_does_not_zoom(self) -> None:
        """Sideways trackpad movement (delta_y == 0) must not zoom out."""
        widget = self.widget
        widget.scroll_accumulator = 0.7
        event = _FakeScrollEvent(Gdk.ScrollDirection.SMOOTH, delta_y=0.0)
        event.delta_x = 3.0
        self._scroll(event)
        self.zoom_out.assert_not_called()
        self.zoom_in.assert_not_called()
        self.assertEqual(widget.scroll_accumulator, 0.0)

    def test_stop_event_resets_accumulator(self) -> None:
        """Lifting the fingers discards any partial step."""
        widget = self.widget
        widget.scroll_accumulator = 0.9
        self._scroll(_FakeScrollEvent(Gdk.ScrollDirection.SMOOTH, is_stop=True))
        self.assertEqual(widget.scroll_accumulator, 0.0)
        self.zoom_out.assert_not_called()


if __name__ == "__main__":
    unittest.main()
