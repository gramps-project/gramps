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
Onboarding flow for new Gramps users.

To add, remove, or reorder tour steps, edit ``ONBOARDING_STEPS`` at the top
of this module.  Each entry is an ``OnboardingStep`` that specifies the
translatable title and body text, a callable that returns the widget to anchor
the popover to, the popover position, and an optional ``navigate_to`` category
key.  No other changes are needed.

``navigate_to`` is the untranslated internal category key (e.g. ``"People"``)
and causes the view manager to switch to that category before showing the
popover.  The popover is always deferred to an idle callback so the view has
time to finish loading.

A step is silently skipped when:
- ``widget_getter`` raises an exception
- ``widget_getter`` returns ``None``
- the widget is not realized or not mapped (not on screen)
- the widget does not belong to the main application window
- ``navigate_to`` names a category that does not exist
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import logging
from collections.abc import Callable
from dataclasses import dataclass, field

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import GLib, Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

LOG = logging.getLogger(__name__)


# -------------------------------------------------------------------------
#
# OnboardingStep
#
# -------------------------------------------------------------------------
@dataclass
class OnboardingStep:
    """A single step in the onboarding popover sequence."""

    title: str
    body: str
    widget_getter: Callable  # (ViewManager) -> Gtk.Widget | None
    position: Gtk.PositionType = field(default=Gtk.PositionType.BOTTOM)
    navigate_to: str | None = None  # untranslated category key, e.g. "People"


# -------------------------------------------------------------------------
# Onboarding step definitions
#
# Edit this list to change the tour.  Each step's widget_getter receives
# the ViewManager instance and must return a visible Gtk.Widget (or None to
# skip the step when the widget is unavailable).
# -------------------------------------------------------------------------
ONBOARDING_STEPS: list[OnboardingStep] = [
    OnboardingStep(
        title=_("Welcome to Gramps!"),
        body=_(
            "Gramps helps you research, organize, and share your family history. "
            "This short tour introduces the main areas of the interface."
        ),
        widget_getter=lambda vm: vm.statusbar,
        position=Gtk.PositionType.TOP,
    ),
    OnboardingStep(
        title=_("Navigate between views"),
        body=_(
            "The sidebar on the left lets you switch between views: "
            "People, Families, Events, Places, and more."
        ),
        widget_getter=lambda vm: vm.navigator.top,
        position=Gtk.PositionType.RIGHT,
    ),
    OnboardingStep(
        title=_("People view"),
        body=_(
            "The People view lists everyone in your family tree. "
            "Double-click any row to open and edit a person's record."
        ),
        widget_getter=lambda vm: getattr(vm.active_page, "list", None),
        position=Gtk.PositionType.RIGHT,
        navigate_to="People",
    ),
    OnboardingStep(
        title=_("Add a person"),
        body=_("Click the Add button to create a new person in your tree."),
        widget_getter=lambda vm: vm.uimanager.get_widget("AddButton"),
        position=Gtk.PositionType.BOTTOM,
    ),
]


# -------------------------------------------------------------------------
#
# OnboardingFlow
#
# -------------------------------------------------------------------------
class OnboardingFlow:
    """Manages a step-by-step popover tour for first-time Gramps users."""

    CONFIG_KEY = "behavior.onboarding-completed"

    def __init__(self, viewmanager) -> None:
        """
        Initialize the onboarding flow.

        :param viewmanager: The application ViewManager instance.
        """
        self._vm = viewmanager
        self._step: int = 0
        self._active: bool = False
        self._popover: Gtk.Popover | None = None
        self._idle_source: int = 0

    @classmethod
    def should_show(cls) -> bool:
        """Return True if the onboarding tour has not yet been completed."""
        return not config.get(cls.CONFIG_KEY)

    def start(self) -> None:
        """Begin the onboarding flow from the first step."""
        self._active = True
        self._step = 0
        self._show_step()

    def _goto_category(self, category_key: str) -> bool:
        """
        Navigate to the first view in the named category.

        Matches by the untranslated internal key so it works in all locales.

        :returns: True if the category was found and navigation was attempted.
        """
        try:
            for cat_num, cat_views in enumerate(self._vm.views):
                if cat_views and cat_views[0][0].category[0] == category_key:
                    self._vm.goto_page(cat_num, 0)
                    return True
        except Exception:
            LOG.warning(
                "Onboarding: exception navigating to category %r",
                category_key,
                exc_info=True,
            )
        return False

    def _resolve_anchor(self, step: OnboardingStep) -> Gtk.Widget | None:
        """
        Return the anchor widget for a step after all validity checks.

        Returns ``None`` (causing the step to be skipped) when:
        - ``widget_getter`` raises or returns ``None``
        - the widget is not realized
        - the widget is not mapped (off screen or hidden)
        - the widget's toplevel window is not the main application window
        """
        try:
            widget = step.widget_getter(self._vm)
        except Exception:
            LOG.warning(
                "Onboarding step %d: widget_getter raised an exception",
                self._step,
                exc_info=True,
            )
            return None

        if widget is None:
            LOG.debug("Onboarding step %d: widget_getter returned None", self._step)
            return None

        if not widget.get_realized():
            LOG.debug("Onboarding step %d: widget is not realized", self._step)
            return None

        if not widget.get_mapped():
            LOG.debug(
                "Onboarding step %d: widget is not mapped (not visible)", self._step
            )
            return None

        if widget.get_toplevel() is not self._vm.window:
            LOG.debug(
                "Onboarding step %d: widget toplevel is not the main window",
                self._step,
            )
            return None

        return widget

    def _cancel_pending(self) -> None:
        """Cancel any pending idle callback."""
        if self._idle_source:
            GLib.source_remove(self._idle_source)
            self._idle_source = 0

    def _show_step(self) -> None:
        """Navigate (if needed) and schedule the popover for the current step.

        Steps whose ``navigate_to`` category cannot be found are skipped
        immediately in a loop to avoid recursion.
        """
        self._cancel_pending()

        if self._popover is not None:
            self._popover.destroy()
            self._popover = None

        while self._step < len(ONBOARDING_STEPS):
            if not self._active:
                return

            step = ONBOARDING_STEPS[self._step]
            if step.navigate_to is not None:
                if not self._goto_category(step.navigate_to):
                    LOG.warning(
                        "Onboarding step %d: category %r not found, skipping",
                        self._step,
                        step.navigate_to,
                    )
                    self._step += 1
                    continue

            self._idle_source = GLib.idle_add(self._present_step)
            return

        self._complete()

    def _present_step(self) -> bool:
        """Show the popover for the current step; called via GLib.idle_add."""
        self._idle_source = 0

        if not self._active or self._step >= len(ONBOARDING_STEPS):
            return GLib.SOURCE_REMOVE

        step = ONBOARDING_STEPS[self._step]
        anchor = self._resolve_anchor(step)

        if anchor is None:
            LOG.debug("Onboarding step %d: no valid anchor, skipping", self._step)
            self._step += 1
            self._show_step()
            return GLib.SOURCE_REMOVE

        self._popover = self._build_popover(step, anchor)
        self._popover.show_all()
        return GLib.SOURCE_REMOVE

    def _build_popover(self, step: OnboardingStep, anchor: Gtk.Widget) -> Gtk.Popover:
        """Build and return a styled popover for the given step."""
        popover = Gtk.Popover.new(anchor)
        popover.set_position(step.position)
        popover.set_modal(False)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        outer.set_margin_top(12)
        outer.set_margin_bottom(12)
        outer.set_margin_start(12)
        outer.set_margin_end(12)

        title_label = Gtk.Label()
        title_label.set_markup("<b>" + GLib.markup_escape_text(step.title) + "</b>")
        title_label.set_xalign(0.0)
        title_label.set_max_width_chars(40)
        title_label.set_line_wrap(True)
        outer.pack_start(title_label, False, False, 0)

        body_label = Gtk.Label(label=step.body)
        body_label.set_xalign(0.0)
        body_label.set_max_width_chars(40)
        body_label.set_line_wrap(True)
        outer.pack_start(body_label, False, False, 0)

        btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_row.set_halign(Gtk.Align.END)

        skip_btn = Gtk.Button(label=_("Skip tour"))
        skip_btn.connect("clicked", self.cb_skip)
        btn_row.pack_start(skip_btn, False, False, 0)

        is_last = self._step == len(ONBOARDING_STEPS) - 1
        next_btn = Gtk.Button(label=_("Done") if is_last else _("Next"))
        next_btn.get_style_context().add_class("suggested-action")
        next_btn.connect("clicked", self.cb_next)
        btn_row.pack_start(next_btn, False, False, 0)

        outer.pack_start(btn_row, False, False, 0)
        popover.add(outer)
        return popover

    def cb_next(self, _button: Gtk.Button) -> None:
        """Advance to the next onboarding step."""
        self._step += 1
        self._show_step()

    def cb_skip(self, _button: Gtk.Button) -> None:
        """Dismiss the tour without completing all steps."""
        self._active = False
        self._cancel_pending()
        if self._popover is not None:
            self._popover.destroy()
            self._popover = None
        self._complete()

    def _complete(self) -> None:
        """Mark the onboarding as done and deactivate the flow."""
        self._active = False
        config.set(self.CONFIG_KEY, True)
