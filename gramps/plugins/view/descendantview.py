#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  The Gramps project
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

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import logging

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.const import CUSTOM_FILTERS, URL_MANUAL_PAGE, URL_WIKISTRING
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import ChildRef, ChildRefType, Family
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.utils.db import find_children, find_parents, find_witnessed_people
from gramps.gen.utils.libformatting import FormattingHelper
from gramps.gui.display import display_help
from gramps.gui.dialog import RunDatabaseRepair
from gramps.gui.editors import EditFamily, EditPerson, FilterEditor
from gramps.gui.utils import is_right_click
from gramps.gui.views.bookmarks import PersonBookmarks
from gramps.gui.views.navigationview import NavigationView
from gramps.plugins.view.pedigreeview import PersonBoxWidgetCairo

_ = glocale.translation.sgettext

LOG = logging.getLogger(__name__)

WIKI_PAGE = URL_WIKISTRING + URL_MANUAL_PAGE + "_-_Categories#Descendant_View"

# Connector stroke widths. Vertical rails are drawn inset from the widget
# edge by half their width so the full stroke stays visible (Cairo clips
# strokes centered on the path; drawing at x=width would hide half of it).
_H_LINE_WIDTH = 3
_V_LINE_WIDTH = 4

# Y offset from the top/bottom of a family cell to the vertical center of
# the primary person box (and symmetrically the spouse box). Matches the
# family container's top/bottom margin plus roughly half a person box.
_PERSON_CENTER_Y = 24


# ------------------------------------------------------------
#
# ParentOutboundLine
#
# ------------------------------------------------------------
class ParentOutboundLine(Gtk.DrawingArea):
    """
    Draws a vertical coupling backbone on the right side to join couples
    together, extending a single horizontal connector stub cleanly outward
    to the LEFT.
    """

    def __init__(
        self,
        num_spouses: int = 0,
        person_boxes: list | None = None,
    ) -> None:
        Gtk.DrawingArea.__init__(self)
        self.num_spouses = num_spouses
        self.person_boxes = person_boxes or []
        self.set_size_request(20, -1)
        self.connect("draw", self.draw_line)

    def delivery_y(self) -> float:
        """
        Return the Y coordinate (in this widget's coordinates) where the
        outbound lineage delivery line leaves this widget's left edge.
        """
        centers = []
        for box in self.person_boxes:
            center = self._box_center_y(box)
            centers.append(center if center is not None else _PERSON_CENTER_Y)

        if self.num_spouses > 0 and len(centers) >= 2:
            return (centers[0] + centers[1]) / 2
        return centers[0] if centers else _PERSON_CENTER_Y

    def _box_center_y(self, box) -> float | None:
        """
        Return the vertical center of box in this widget's coordinates.

        Returns None if the box is not yet realized, in which case the
        caller falls back to a fixed offset.
        """
        if box is None or not box.get_realized():
            return None
        coords = box.translate_coordinates(self, 0, 0)
        if coords is None:
            return None
        _x, y = coords
        return y + box.get_allocated_height() / 2

    def draw_line(self, widget: Gtk.DrawingArea, context) -> bool:
        alloc = self.get_allocation()
        context.set_source_rgb(0.0, 0.0, 0.0)

        right_edge = alloc.width
        # Junction X for the couple backbone / outbound stub
        spine_x = right_edge / 2

        # Compute the actual vertical center of each person box so the
        # horizontal stubs line up perfectly with the boxes.
        centers = []
        for box in self.person_boxes:
            center = self._box_center_y(box)
            centers.append(center if center is not None else _PERSON_CENTER_Y)

        if self.num_spouses > 0 and len(centers) >= 2:
            person1_center_y = centers[0]
            spouse_center_y = centers[1]
            mid_y = (person1_center_y + spouse_center_y) / 2

            # Draw horizontal lines poking into both the person and the spouse
            context.set_line_width(_H_LINE_WIDTH)
            context.move_to(right_edge, person1_center_y)
            context.line_to(spine_x, person1_center_y)

            context.move_to(right_edge, spouse_center_y)
            context.line_to(spine_x, spouse_center_y)

            # Outbound lineage delivery line centered on the couple branch
            context.move_to(spine_x, mid_y)
            context.line_to(0, mid_y)
            context.stroke()

            # Vertical coupling backbone, thicker than the horizontals
            context.set_line_width(_V_LINE_WIDTH)
            context.move_to(spine_x, person1_center_y)
            context.line_to(spine_x, spouse_center_y)
            context.stroke()
        else:
            # Single person: aim at the person box center
            person1_center_y = centers[0] if centers else _PERSON_CENTER_Y
            context.set_line_width(_H_LINE_WIDTH)
            context.move_to(right_edge, person1_center_y)
            context.line_to(0, person1_center_y)
            context.stroke()

        return False


# ------------------------------------------------------------
#
# ChildInboundLine
#
# ------------------------------------------------------------
class ChildInboundLine(Gtk.DrawingArea):
    """
    Draws seamless, unbroken vertical tracking rails from the first sibling's
    horizontal line down to the last sibling's horizontal line.
    """

    def __init__(
        self,
        is_first_child: bool,
        is_last_child: bool,
        has_spouse: bool = False,
        person_boxes: list | None = None,
        is_birth: bool = True,
        draw_pin: bool = True,
    ) -> None:
        Gtk.DrawingArea.__init__(self)
        self.is_first_child = is_first_child
        self.is_last_child = is_last_child
        self.has_spouse = has_spouse
        self.is_birth = is_birth
        self.draw_pin = draw_pin
        self.person_boxes = person_boxes or []
        self.parent_line: ParentOutboundLine | None = None
        # Rails of the non-birth children in this sibling group.  Every
        # row widget in the group gets the same list so it can split its
        # solid spine around their connector runs and dash those runs.
        self.nonbirth_rails: list = []
        self.set_size_request(20, -1)
        self.connect("draw", self.draw_lines)

    def _box_center_y(self, box) -> float | None:
        """
        Return the vertical center of box in this widget's coordinates.

        Returns None if the box is not yet realized, in which case the
        caller falls back to a fixed offset.
        """
        if box is None or not box.get_realized():
            return None
        coords = box.translate_coordinates(self, 0, 0)
        if coords is None:
            return None
        _x, y = coords
        return y + box.get_allocated_height() / 2

    def pin_y(self) -> float:
        """Return this row's pin Y (the person box center) in own coords."""
        center = self._box_center_y(self.person_boxes[0]) if self.person_boxes else None
        return center if center is not None else _PERSON_CENTER_Y

    def _delivery_in_own_coords(self) -> float | None:
        """Return the parents' delivery Y translated into own coords."""
        if self.parent_line is None or not self.parent_line.get_realized():
            return None
        coords = self.parent_line.translate_coordinates(
            self, 0, self.parent_line.delivery_y()
        )
        return coords[1] if coords else None

    def _dashed_intervals(self) -> list[tuple[float, float]]:
        """
        Return merged, sorted spine intervals carrying the non-birth
        children's connector runs (pin to the parents' delivery point).
        """
        delivery = self._delivery_in_own_coords()
        if delivery is None:
            return []
        intervals = []
        for rail in self.nonbirth_rails:
            if not rail.get_realized():
                continue
            coords = rail.translate_coordinates(self, 0, rail.pin_y())
            if not coords:
                continue
            lo, hi = sorted((coords[1], delivery))
            if hi - lo > 0.5:
                intervals.append((lo, hi))
        merged: list[list[float]] = []
        for lo, hi in sorted(intervals):
            if merged and lo <= merged[-1][1] + 0.5:
                merged[-1][1] = max(merged[-1][1], hi)
            else:
                merged.append([lo, hi])
        return [(lo, hi) for lo, hi in merged]

    def draw_lines(self, widget: Gtk.DrawingArea, context) -> bool:
        alloc = self.get_allocation()
        context.set_source_rgb(0.0, 0.0, 0.0)

        # Inset so the full vertical stroke remains visible; its outer edge
        # still meets the adjacent parent-outbound connector at the cell edge.
        spine_x = alloc.width - _V_LINE_WIDTH / 2

        # Aim at the actual vertical center of the primary person box so
        # the horizontal pin lines up perfectly with the box.
        target_y = self.pin_y()

        # Spine intervals carrying non-birth children's connectors; drawn
        # dashed, with the solid rails split around them so no solid
        # stroke hides underneath the dashes.
        intervals = self._dashed_intervals()

        context.set_line_width(_V_LINE_WIDTH)

        def stroke_solid(a: float, b: float) -> None:
            """Stroke [a, b] minus the dashed intervals, clipped to widget."""
            cursor = max(a, 0.0)
            end = min(b, alloc.height)
            for lo, hi in intervals:
                if hi <= cursor + 0.5:
                    continue
                if lo >= end - 0.5:
                    break
                if lo - cursor > 0.5:
                    context.move_to(spine_x, cursor)
                    context.line_to(spine_x, lo)
                    context.stroke()
                cursor = max(cursor, hi)
            if end - cursor > 0.5:
                context.move_to(spine_x, cursor)
                context.line_to(spine_x, end)
                context.stroke()

        # Solid sibling rails (edge-gated), split around dashed intervals.
        if not self.is_first_child:
            stroke_solid(0.0, target_y)
        if not self.is_last_child:
            stroke_solid(target_y, alloc.height)

        # Only child (first and last): the edge-gated spine draws nothing,
        # so bridge the pin to the parents' delivery line explicitly when
        # they share this row.  Non-birth children are already covered by
        # their dashed connector run.
        if self.is_first_child and self.is_last_child and self.is_birth:
            delivery = self._delivery_in_own_coords()
            if delivery is not None:
                lo, hi = sorted((target_y, delivery))
                if hi - lo > 0.5:
                    context.move_to(spine_x, lo)
                    context.line_to(spine_x, hi)
                    context.stroke()

        # Dashed connector runs for the non-birth children.
        for lo, hi in intervals:
            y0 = max(lo, 0.0)
            y1 = min(hi, alloc.height)
            if y1 - y0 > 0.5:
                context.set_dash([9.0], 1)  # DASH
                context.move_to(spine_x, y0)
                context.line_to(spine_x, y1)
                context.stroke()
                context.set_dash([], 0)  # SOLID

        # Horizontal connector pin running into the right side of the
        # child box. Dashed when the child's relationship to the primary
        # person is not by birth (matching pedigree view behavior).
        if self.draw_pin:
            context.set_line_width(_H_LINE_WIDTH)
            if self.is_birth:
                context.set_dash([], 0)  # SOLID
            else:
                context.set_dash([9.0], 1)  # DASH
            context.move_to(spine_x, target_y)
            context.line_to(0, target_y)
            context.stroke()
            context.set_dash([], 0)  # SOLID

        return False


# ------------------------------------------------------------
#
# DescendantView
#
# ------------------------------------------------------------
class DescendantView(NavigationView):
    """
    A view that displays descendants branching from right (root) to left
    (descendants), grouping spouses side-by-side inside family cells with
    zero line breaking gaps.
    """

    CONFIGSETTINGS = (
        ("interface.descrtl-tree-size", 4),
        ("interface.descrtl-show-images", True),
        ("interface.descrtl-show-tags", False),
    )

    FLEUR_CURSOR = Gdk.Cursor.new_for_display(
        Gdk.Display.get_default(), Gdk.CursorType.FLEUR
    )

    additional_ui = [
        """
      <placeholder id="CommonGo">
      <section>
        <item>
          <attribute name="action">win.Back</attribute>
          <attribute name="label" translatable="yes">_Back</attribute>
        </item>
        <item>
          <attribute name="action">win.Forward</attribute>
          <attribute name="label" translatable="yes">_Forward</attribute>
        </item>
      </section>
      <section>
        <item>
          <attribute name="action">win.HomePerson</attribute>
          <attribute name="label" translatable="yes">_Home</attribute>
        </item>
      </section>
      </placeholder>
""",
        """
      <section id="AddEditBook">
        <item>
          <attribute name="action">win.AddBook</attribute>
          <attribute name="label" translatable="yes">_Add Bookmark</attribute>
        </item>
        <item>
          <attribute name="action">win.EditBook</attribute>
          <attribute name="label" translatable="no">%s...</attribute>
        </item>
      </section>
""" % _("Organize Bookmarks"),
        """
        <placeholder id='otheredit'>
        <item>
          <attribute name="action">win.FilterEdit</attribute>
          <attribute name="label" translatable="yes">"""
        """Person Filter Editor</attribute>
        </item>
        </placeholder>
""",
        """
    <placeholder id='CommonNavigation'>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-previous</property>
        <property name="action-name">win.Back</property>
        <property name="tooltip_text" translatable="yes">"""
        """Go to the previous object in the history</property>
        <property name="label" translatable="yes">_Back</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-next</property>
        <property name="action-name">win.Forward</property>
        <property name="tooltip_text" translatable="yes">"""
        """Go to the next object in the history</property>
        <property name="label" translatable="yes">_Forward</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-home</property>
        <property name="action-name">win.HomePerson</property>
        <property name="tooltip_text" translatable="yes">"""
        """Go to the home person</property>
        <property name="label" translatable="yes">_Home</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
    """,
    ]

    def __init__(self, pdata, dbstate, uistate, nav_group: int = 0) -> None:
        NavigationView.__init__(
            self,
            _("Descendant RTL"),
            pdata,
            dbstate,
            uistate,
            PersonBookmarks,
            nav_group,
        )
        self.dbstate = dbstate
        self.uistate = uistate
        self.dbstate.connect("database-changed", self.change_db)
        uistate.connect("nameformat-changed", self.refresh_view)
        uistate.connect("font-changed", self.refresh_view)
        self.format_helper = FormattingHelper(self.dbstate, self.uistate)
        self.tree_depth = self._config.get("interface.descrtl-tree-size")
        self.show_images = self._config.get("interface.descrtl-show-images")
        self.show_tags = self._config.get("interface.descrtl-show-tags")
        self.scrolledwindow = None
        self.table = None
        self.additional_uis.append(self.additional_ui)
        # Variables for drag-scroll
        self._last_x = 0
        self._last_y = 0
        self._in_move = False

    def define_actions(self) -> None:
        """Build the action group information for navigation shortcuts."""
        NavigationView.define_actions(self)
        self._add_action("FilterEdit", self.cb_filter_editor)
        self._add_action("F2", self.kb_goto_home, "F2")
        self._add_action("PRIMARY-J", self.jump, "<PRIMARY>J")

    def cb_filter_editor(self, *obj) -> None:
        """Display the person filter editor."""
        try:
            FilterEditor("Person", CUSTOM_FILTERS, self.dbstate, self.uistate)
        except WindowActiveError:
            return

    def kb_goto_home(self, *obj) -> None:
        """Goto home person from keyboard."""
        self.cb_home(None)

    def get_handle_from_gramps_id(self, gid: str):
        """Return the handle of the specified person."""
        obj = self.dbstate.db.get_person_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        return None

    def get_stock(self) -> str:
        """Return the category stock icon."""
        return "gramps-pedigree"

    def get_viewtype_stock(self) -> str:
        """Return the view type stock icon."""
        return "gramps-pedigree"

    def navigation_type(self) -> str:
        """Return the navigation type."""
        return "Person"

    def can_configure(self) -> bool:
        """Allow configuration of the view."""
        return True

    def on_delete(self) -> None:
        """Save config on shutdown."""
        self._config.save()
        NavigationView.on_delete(self)

    def on_help_clicked(self, dummy) -> None:
        """Display the relevant portion of Gramps manual."""
        display_help(self.uistate.window, WIKI_PAGE)

    def _connect_db_signals(self) -> None:
        """Connect database signals."""
        self._add_db_signal("person-add", self.refresh_view)
        self._add_db_signal("person-update", self.refresh_view)
        self._add_db_signal("person-delete", self.refresh_view)
        self._add_db_signal("person-rebuild", self.refresh_view)
        self._add_db_signal("family-update", self.refresh_view)
        self._add_db_signal("family-add", self.refresh_view)
        self._add_db_signal("family-delete", self.refresh_view)
        self._add_db_signal("family-rebuild", self.refresh_view)
        self._add_db_signal("event-update", self.refresh_view)

    def build_widget(self):
        """Build the interface and return a Gtk.Container."""
        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        self.scrolledwindow.add_events(Gdk.EventMask.SCROLL_MASK)
        event_box = Gtk.EventBox()
        event_box.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.BUTTON1_MOTION_MASK
        )
        event_box.connect("button-press-event", self.cb_bg_button_press)
        event_box.connect("button-release-event", self.cb_bg_button_release)
        event_box.connect("motion-notify-event", self.cb_bg_motion_notify_event)
        self.scrolledwindow.add(event_box)

        self.table = Gtk.Grid()
        self.table.set_direction(Gtk.TextDirection.LTR)
        event_box.add(self.table)
        event_box.get_parent().set_shadow_type(Gtk.ShadowType.NONE)
        self.table.set_row_spacing(0)
        self.table.set_column_spacing(0)
        return self.scrolledwindow

    def change_page(self) -> None:
        """Called when the page changes."""
        NavigationView.change_page(self)
        self.uistate.clear_filter_results()
        if self.dirty:
            self.build_tree()

    def change_db(self, db) -> None:
        """Handle database change callback."""
        self._change_db(db)
        if self.active:
            self.bookmarks.redraw()
        self.build_tree()

    def refresh_view(self, dummy=None) -> None:
        """Refresh the view when data changes."""
        self.format_helper.clear_cache()
        self.dirty = True
        if self.active:
            self.build_tree()

    def goto_handle(self, handle=None) -> None:
        """Rebuild the tree with the given person handle as root."""
        self.dirty = True
        if handle:
            person = self.dbstate.db.get_person_from_handle(handle)
            if person:
                self.build_tree()
            else:
                return
        else:
            self.build_tree()
        self.uistate.modify_statusbar(self.dbstate)

    def cb_childmenu_changed(self, obj, person_handle) -> bool:
        """Callback for pulldown menu selection."""
        self.change_active(person_handle)
        return True

    def cb_on_show_child_menu(self, obj, person_handle) -> int:
        """Show a popup menu of children for the given person."""
        from html import escape

        person = self.dbstate.db.get_person_from_handle(person_handle)
        if person:
            childlist = find_children(self.dbstate.db, person)
            if len(childlist) == 1:
                child = self.dbstate.db.get_person_from_handle(childlist[0])
                if child:
                    self.change_active(childlist[0])
            elif len(childlist) > 1:
                self.my_menu = Gtk.Menu()
                self.my_menu.set_reserve_toggle_size(False)
                for child_handle in childlist:
                    child = self.dbstate.db.get_person_from_handle(child_handle)
                    cname = escape(name_displayer.display(child))
                    if find_children(self.dbstate.db, child):
                        label = Gtk.Label(label="<b><i>%s</i></b>" % cname)
                    else:
                        label = Gtk.Label(label=cname)
                    label.set_use_markup(True)
                    label.show()
                    label.set_halign(Gtk.Align.START)
                    menuitem = Gtk.MenuItem()
                    menuitem.add(label)
                    self.my_menu.append(menuitem)
                    menuitem.connect(
                        "activate", self.cb_childmenu_changed, child_handle
                    )
                    menuitem.show()
                self.my_menu.popup_at_pointer(None)
            return 1
        return 0

    def cb_on_show_parent_menu(self, obj, person_handle) -> int:
        """Show a popup menu of parents for the given person."""
        from html import escape

        person = self.dbstate.db.get_person_from_handle(person_handle)
        if person:
            parentlist = find_parents(self.dbstate.db, person)
            if len(parentlist) == 1:
                parent = self.dbstate.db.get_person_from_handle(parentlist[0])
                if parent:
                    self.change_active(parentlist[0])
            elif len(parentlist) > 1:
                self.my_menu = Gtk.Menu()
                self.my_menu.set_reserve_toggle_size(False)
                for parent_handle in parentlist:
                    parent = self.dbstate.db.get_person_from_handle(parent_handle)
                    if not parent:
                        continue
                    pname = escape(name_displayer.display(parent))
                    if find_parents(self.dbstate.db, parent):
                        label = Gtk.Label(label="<b><i>%s</i></b>" % pname)
                    else:
                        label = Gtk.Label(label=pname)
                    label.set_use_markup(True)
                    label.show()
                    label.set_halign(Gtk.Align.START)
                    menuitem = Gtk.MenuItem()
                    menuitem.add(label)
                    self.my_menu.append(menuitem)
                    menuitem.connect(
                        "activate", self.cb_childmenu_changed, parent_handle
                    )
                    menuitem.show()
                self.my_menu.popup_at_pointer(None)
            return 1
        return 0

    def build_tree(self) -> None:
        """Build the descendant tree from the active person."""
        try:
            active_handle = self.get_active()
            if not active_handle:
                return

            if self.table is None:
                return

            for child in self.table.get_children():
                child.destroy()

            person = self.dbstate.db.get_person_from_handle(active_handle)
            if person:
                population_map: dict[int, list] = {}
                self.map_descendants(
                    person,
                    current_depth=0,
                    max_depth=self.tree_depth,
                    generation_dict=population_map,
                )
                self.render_rtl_grid(population_map)
            self.dirty = False
        except AttributeError as msg:
            RunDatabaseRepair(str(msg), parent=self.uistate.window)

    def map_descendants(
        self,
        person,
        current_depth: int,
        max_depth: int,
        generation_dict: dict,
        next_row: int = 0,
        is_birth: bool = True,
    ) -> int:
        """Recursively map descendants into a generation dictionary."""
        if current_depth >= max_depth or not person:
            return next_row

        if current_depth not in generation_dict:
            generation_dict[current_depth] = []

        spouses = []
        for family_handle in person.get_family_handle_list():
            family = self.dbstate.db.get_family_from_handle(family_handle)
            if family:
                orig_father = family.get_father_handle()
                orig_mother = family.get_mother_handle()
                spouse_handle = None
                if person.handle == orig_father and orig_mother:
                    spouse_handle = orig_mother
                elif person.handle == orig_mother and orig_father:
                    spouse_handle = orig_father
                if spouse_handle:
                    spouse_obj = self.dbstate.db.get_person_from_handle(spouse_handle)
                    if spouse_obj and spouse_obj not in spouses:
                        spouses.append(spouse_obj)

        current_node_row = next_row
        # Layout: [row, person, spouses, is_first, is_last, is_birth]
        node_payload = [current_node_row, person, spouses, True, True, is_birth]
        generation_dict[current_depth].append(node_payload)

        child_start_row = next_row
        child_nodes_in_family: list = []

        for family_handle in person.get_family_handle_list():
            family = self.dbstate.db.get_family_from_handle(family_handle)
            if family:
                valid_children = []
                for child_ref in family.get_child_ref_list():
                    child_person = self.dbstate.db.get_person_from_handle(child_ref.ref)
                    if child_person:
                        # Relationship is judged on the primary person's own
                        # link to the child (frel if primary is the father,
                        # mrel if the mother), mirroring pedigree view.
                        if person.handle == family.get_father_handle():
                            child_is_birth = child_ref.frel == ChildRefType.BIRTH
                        elif person.handle == family.get_mother_handle():
                            child_is_birth = child_ref.mrel == ChildRefType.BIRTH
                        else:
                            child_is_birth = (
                                child_ref.frel == ChildRefType.BIRTH
                                and child_ref.mrel == ChildRefType.BIRTH
                            )
                        valid_children.append((child_person, child_is_birth))

                for idx, (child_person, child_is_birth) in enumerate(valid_children):
                    target_gen = current_depth + 1

                    # Children at the max depth boundary are not added to
                    # the generation dict, so skip them entirely to avoid
                    # out-of-range errors further down.
                    if target_gen < max_depth:
                        if idx > 0 or len(child_nodes_in_family) > 0:
                            next_row += 2

                        if target_gen not in generation_dict:
                            generation_dict[target_gen] = []
                        target_list_idx = len(generation_dict[target_gen])

                        next_row = self.map_descendants(
                            child_person,
                            current_depth + 1,
                            max_depth,
                            generation_dict,
                            next_row,
                            child_is_birth,
                        )

                        is_first_sibling = idx == 0 and len(child_nodes_in_family) == 0
                        child_nodes_in_family.append(
                            (target_gen, target_list_idx, is_first_sibling)
                        )

        if child_nodes_in_family:
            for t_gen, t_idx, _t_first in child_nodes_in_family:
                generation_dict[t_gen][t_idx][3] = False
                generation_dict[t_gen][t_idx][4] = False

            first_gen, first_idx, _ = child_nodes_in_family[0]
            generation_dict[first_gen][first_idx][3] = True

            last_gen, last_idx, _ = child_nodes_in_family[-1]
            generation_dict[last_gen][last_idx][4] = True

            center_row = (child_start_row + next_row) // 2
            node_payload[0] = center_row

        return next_row

    def render_rtl_grid(self, population_map: dict) -> None:
        """Render the descendant tree into the GTK grid."""
        if not population_map:
            return

        table = self.table
        assert table is not None

        max_seen_depth = max(population_map.keys())
        size_groups_by_column: dict[int, Gtk.SizeGroup] = {}
        # Offset columns by 1 to reserve column 0 for child nav buttons
        col_offset = 1

        # Person/spouse boxes keyed for nav-button height matching.
        # deepest: grid_row -> [primary_box, spouse_box, ...]
        # root: [primary_box, spouse_box, ...]
        deepest_person_boxes: dict[int, list] = {}
        root_person_boxes: list = []
        # All cell boxes by grid row, used to center connector lines.
        cell_boxes_by_row: dict[int, list] = {}
        # Outbound connector widgets keyed by (column, row); wired into
        # the adjacent child rails after all widgets are rendered.
        outbound_stubs_by_pos: dict[tuple[int, int], ParentOutboundLine] = {}

        # Step 1: Render all Person and Spouse boxes to establish columns
        for depth_level, people_nodes in population_map.items():
            grid_column = (max_seen_depth - depth_level) * 3 + col_offset

            if grid_column not in size_groups_by_column:
                size_groups_by_column[grid_column] = Gtk.SizeGroup(
                    mode=Gtk.SizeGroupMode.HORIZONTAL
                )
            column_size_group = size_groups_by_column[grid_column]

            for (
                grid_row,
                person,
                spouses,
                _is_first,
                _is_last,
                _is_birth,
            ) in people_nodes:
                family_container = Gtk.Box(
                    orientation=Gtk.Orientation.VERTICAL, spacing=2
                )
                family_container.set_margin_top(6)
                family_container.set_margin_bottom(6)
                family_container.set_valign(Gtk.Align.START)

                cell_boxes: list = []

                is_alive = not person.get_death_ref()
                primary_box = PersonBoxWidgetCairo(
                    view=self,
                    format_helper=self.format_helper,
                    dbstate=self.dbstate,
                    person=person,
                    alive=is_alive,
                    maxlines=3,
                    image=self.show_images,
                    tags=self.show_tags,
                )
                family_container.pack_start(primary_box, False, False, 0)
                column_size_group.add_widget(primary_box)
                cell_boxes.append(primary_box)

                # Connect button-press for context menu and double-click edit
                fam_h = None
                for family_handle in person.get_family_handle_list():
                    fam = self.dbstate.db.get_family_from_handle(family_handle)
                    if fam:
                        fam_h = family_handle
                        break
                primary_box.connect(
                    "button-press-event",
                    self.cb_person_button_press,
                    person.get_handle(),
                    fam_h,
                )

                for spouse in spouses:
                    spouse_alive = not spouse.get_death_ref()
                    spouse_box = PersonBoxWidgetCairo(
                        view=self,
                        format_helper=self.format_helper,
                        dbstate=self.dbstate,
                        person=spouse,
                        alive=spouse_alive,
                        maxlines=3,
                        image=self.show_images,
                        tags=self.show_tags,
                    )
                    spouse_box.set_margin_top(10)
                    family_container.pack_start(spouse_box, False, False, 0)
                    column_size_group.add_widget(spouse_box)
                    cell_boxes.append(spouse_box)

                    # Connect button-press for spouse context menu
                    sp_fam_h = None
                    for family_handle in person.get_family_handle_list():
                        fam = self.dbstate.db.get_family_from_handle(family_handle)
                        if fam and (
                            fam.get_father_handle() == spouse.get_handle()
                            or fam.get_mother_handle() == spouse.get_handle()
                        ):
                            sp_fam_h = family_handle
                            break
                    spouse_box.connect(
                        "button-press-event",
                        self.cb_person_button_press,
                        spouse.get_handle(),
                        sp_fam_h,
                    )

                if depth_level == max_seen_depth:
                    deepest_person_boxes[grid_row] = cell_boxes
                if depth_level == 0:
                    root_person_boxes = cell_boxes
                cell_boxes_by_row[grid_row] = cell_boxes

                table.attach(family_container, grid_column, grid_row, 1, 1)

                if depth_level < max_seen_depth:
                    # Only draw the outbound connector when this cell
                    # actually has children; otherwise it dangles.
                    has_children = bool(find_children(self.dbstate.db, person))
                    if not has_children:
                        for spouse in spouses:
                            if find_children(self.dbstate.db, spouse):
                                has_children = True
                                break

                    if has_children:
                        outbound_stub = ParentOutboundLine(
                            num_spouses=len(spouses),
                            person_boxes=cell_boxes,
                        )
                        outbound_stub.set_vexpand(True)
                        outbound_stub.set_valign(Gtk.Align.FILL)
                        table.attach(outbound_stub, grid_column - 1, grid_row, 1, 1)
                        outbound_stubs_by_pos[(grid_column - 1, grid_row)] = (
                            outbound_stub
                        )

        # Step 2: Render continuous, gap-free vertical lines for siblings
        for depth_level in range(1, max_seen_depth + 1):
            grid_column = (max_seen_depth - depth_level) * 3 + col_offset
            current_generation_nodes = population_map[depth_level]

            sibling_groups = []
            current_group = []

            for node in current_generation_nodes:
                current_group.append(node)
                if node[4]:
                    sibling_groups.append(list(current_group))
                    current_group = []

            for group in sibling_groups:
                if not group:
                    continue

                start_row = group[0][0]
                end_row = group[-1][0]
                people_rows_map = {node[0]: node for node in group}

                # All rows of the group (person rows and gap rows) get a
                # rail widget sharing one non-birth rail list, so each
                # widget splits its solid spine around and dashes exactly
                # the non-birth children's connector runs.  Gap rows have
                # no pin; they just carry the spine through.
                group_nonbirth: list = []
                group_rails: list[ChildInboundLine] = []
                for current_row in range(start_row, end_row + 1):
                    row_boxes = cell_boxes_by_row.get(current_row, [])
                    node_data = people_rows_map.get(current_row)
                    if node_data is not None:
                        rail = ChildInboundLine(
                            is_first_child=node_data[3],
                            is_last_child=node_data[4],
                            has_spouse=len(node_data[2]) > 0,
                            person_boxes=row_boxes,
                            is_birth=node_data[5],
                        )
                        if not node_data[5]:
                            group_nonbirth.append(rail)
                    else:
                        rail = ChildInboundLine(
                            is_first_child=False,
                            is_last_child=False,
                            has_spouse=False,
                            person_boxes=[],
                            draw_pin=False,
                        )
                    group_rails.append(rail)

                # The outbound stub lives in the parents' grid row, which is
                # one of the group's rows but generally not the same row as
                # each child.  Find it once for the whole group so every
                # rail (including the non-couple rows) can compute the
                # dashed connector runs up to the delivery line.
                group_stub = None
                for r in range(start_row, end_row + 1):
                    stub = outbound_stubs_by_pos.get((grid_column + 2, r))
                    if stub is not None:
                        group_stub = stub
                        break

                for offset, rail in enumerate(group_rails):
                    current_row = start_row + offset
                    rail.nonbirth_rails = group_nonbirth
                    rail.set_vexpand(True)
                    rail.set_valign(Gtk.Align.FILL)
                    table.attach(rail, grid_column + 1, current_row, 1, 1)
                    # Wire every rail in the group to the group's stub: the
                    # rail reads the stub's delivery Y so the dashed
                    # connector runs all end exactly on the delivery line.
                    rail.parent_line = group_stub
                    # The rail may have drawn before the stub was realized,
                    # in which case it fell back to an all-solid spine;
                    # redraw now that the delivery point is available, and
                    # again when the stub first draws if it wasn't realized
                    # yet.
                    rail.queue_draw()
                    if group_stub is not None and not group_stub.get_realized():
                        group_stub.connect(
                            "draw", lambda _w, _c, r=rail: r.queue_draw()
                        )

        # Step 3: Add navigation arrow buttons.  Each button sits in a
        # slot that is height-matched to its person/spouse box via a
        # vertical SizeGroup, so the button stays centered on that box
        # even when box heights differ (e.g. with/without images).
        active_handle = self.get_active()
        if active_handle and root_person_boxes:
            person = self.dbstate.db.get_person_from_handle(active_handle)
            if person:
                root_node = population_map[0][0]
                root_row = root_node[0]
                root_spouses = root_node[2]

                parent_button_box = Gtk.Box(
                    orientation=Gtk.Orientation.VERTICAL, spacing=2
                )
                parent_button_box.set_margin_top(6)
                parent_button_box.set_margin_bottom(6)
                parent_button_box.set_valign(Gtk.Align.START)

                # Primary person's parents
                parentlist = find_parents(self.dbstate.db, person)
                self._pack_nav_button(
                    parent_button_box,
                    root_person_boxes[0],
                    "go-next-symbolic",
                    parentlist,
                    self.cb_on_show_parent_menu,
                    active_handle,
                    _("Jump to parent..."),
                    _("No parents"),
                    margin_top=0,
                )

                # Spouses' parents
                for idx, spouse in enumerate(root_spouses):
                    spouse_parentlist = find_parents(self.dbstate.db, spouse)
                    box_idx = idx + 1
                    person_box = (
                        root_person_boxes[box_idx]
                        if box_idx < len(root_person_boxes)
                        else root_person_boxes[0]
                    )
                    self._pack_nav_button(
                        parent_button_box,
                        person_box,
                        "go-next-symbolic",
                        spouse_parentlist,
                        self.cb_on_show_parent_menu,
                        spouse.get_handle(),
                        _("Jump to parent..."),
                        _("No parents"),
                        margin_top=10,
                    )

                table.attach(
                    parent_button_box,
                    (max_seen_depth * 3) + col_offset + 1,
                    root_row,
                    1,
                    1,
                )

        # Child navigation arrows on the left of deepest-generation persons.
        deepest_nodes = population_map.get(max_seen_depth, [])
        for grid_row, person, spouses, _is_first, _is_last, _is_birth in deepest_nodes:
            button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            button_box.set_margin_top(6)
            button_box.set_margin_bottom(6)
            button_box.set_valign(Gtk.Align.START)

            cell_boxes = deepest_person_boxes.get(grid_row, [])
            persons_handles = [person.get_handle()] + [
                spouse.get_handle() for spouse in spouses
            ]

            for idx, handle in enumerate(persons_handles):
                if idx > 0:
                    person_obj = self.dbstate.db.get_person_from_handle(handle)
                    if not person_obj:
                        continue
                    childlist = find_children(self.dbstate.db, person_obj)
                else:
                    childlist = find_children(self.dbstate.db, person)

                person_box = cell_boxes[idx] if idx < len(cell_boxes) else None
                self._pack_nav_button(
                    button_box,
                    person_box,
                    "go-previous-symbolic",
                    childlist,
                    self.cb_on_show_child_menu,
                    handle,
                    _("Jump to child..."),
                    _("No children"),
                    margin_top=10 if idx > 0 else 0,
                )

            table.attach(button_box, 0, grid_row, 1, 1)

        # Add a spacer in column 0 to ensure the column has visible width
        # even when no child navigation buttons are present.
        spacer = Gtk.Label()
        spacer.set_size_request(24, 1)
        table.attach(spacer, 0, 0, 1, 1)

        table.show_all()

    ####################################################################
    # Context menu and navigation
    ####################################################################
    def cb_home(self, menuitem) -> None:
        """Change root person to default person for database."""
        defperson = self.dbstate.db.get_default_person()
        if defperson:
            self.change_active(defperson.get_handle())

    def cb_set_home(self, menuitem, handle) -> None:
        """Set the root person to current person for database."""
        active = self.uistate.get_active("Person")
        if active:
            self.dbstate.db.set_default_person_handle(handle)
        self.cb_home(None)

    def cb_edit_person(self, obj, person_handle) -> bool:
        """Open edit person window for person_handle."""
        person = self.dbstate.db.get_person_from_handle(person_handle)
        if person:
            try:
                EditPerson(self.dbstate, self.uistate, [], person)
            except WindowActiveError:
                return True
            return True
        return False

    def cb_edit_family(self, obj, family_handle) -> bool:
        """Open edit family window for family_handle."""
        family = self.dbstate.db.get_family_from_handle(family_handle)
        if family:
            try:
                EditFamily(self.dbstate, self.uistate, [], family)
            except WindowActiveError:
                return True
            return True
        return False

    def cb_add_parents(self, obj, person_handle, family_handle) -> None:
        """Edit not full family."""
        if family_handle:
            family = self.dbstate.db.get_family_from_handle(family_handle)
        else:
            family = Family()
            childref = ChildRef()
            childref.set_reference_handle(person_handle)
            family.add_child_ref(childref)
        try:
            EditFamily(self.dbstate, self.uistate, [], family)
        except WindowActiveError:
            return

    def cb_copy_person_to_clipboard(self, obj, person_handle) -> bool:
        """Copy person data to clipboard."""
        person = self.dbstate.db.get_person_from_handle(person_handle)
        if person:
            clipboard = Gtk.Clipboard.get_for_display(
                Gdk.Display.get_default(), Gdk.SELECTION_CLIPBOARD
            )
            clipboard.set_text(self.format_helper.format_person(person, 11), -1)
            return True
        return False

    def cb_copy_family_to_clipboard(self, obj, family_handle) -> bool:
        """Copy family data to clipboard."""
        family = self.dbstate.db.get_family_from_handle(family_handle)
        if family:
            clipboard = Gtk.Clipboard.get_for_display(
                Gdk.Display.get_default(), Gdk.SELECTION_CLIPBOARD
            )
            clipboard.set_text(self.format_helper.format_relation(family, 11), -1)
            return True
        return False

    def cb_person_button_press(self, obj, event, person_handle, family_handle) -> bool:
        """Handle button press on person box."""
        if is_right_click(event):
            self.cb_build_full_nav_menu(obj, event, person_handle, family_handle)
            return True
        elif event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS and event.button == 1:
            self.cb_edit_person(obj, person_handle)
            return True
        return True

    def cb_bg_button_press(self, widget, event) -> bool:
        """Enter scroll mode or show option menu on background press."""
        if event.button == 1 and event.type == Gdk.EventType.BUTTON_PRESS:
            widget.get_window().set_cursor(self.FLEUR_CURSOR)
            self._last_x = event.x
            self._last_y = event.y
            self._in_move = True
            return True
        elif is_right_click(event):
            self.cb_on_show_option_menu(widget, event)
            return True
        return False

    def cb_bg_button_release(self, widget, event) -> bool:
        """Exit scroll mode on button release."""
        if event.button == 1 and event.type == Gdk.EventType.BUTTON_RELEASE:
            self.cb_bg_motion_notify_event(widget, event)
            widget.get_window().set_cursor(None)
            self._in_move = False
            return True
        return False

    def cb_bg_motion_notify_event(self, widget, event) -> bool:
        """Handle drag-scroll motion."""
        if self._in_move and (
            event.type == Gdk.EventType.MOTION_NOTIFY
            or event.type == Gdk.EventType.BUTTON_RELEASE
        ):
            window = widget.get_parent()
            hadjustment = window.get_hadjustment()
            vadjustment = window.get_vadjustment()
            self.update_scrollbar_positions(
                vadjustment,
                vadjustment.get_value() - (event.y - self._last_y),
            )
            self.update_scrollbar_positions(
                hadjustment,
                hadjustment.get_value() - (event.x - self._last_x),
            )
            return True
        return False

    def update_scrollbar_positions(self, adjustment, value) -> bool:
        """Control value then try setup in scrollbar."""
        if value > (adjustment.get_upper() - adjustment.get_page_size()):
            adjustment.set_value(adjustment.get_upper() - adjustment.get_page_size())
        else:
            adjustment.set_value(value)
        return True

    def cb_on_show_option_menu(self, obj, event, data=None) -> bool:
        """Right click option menu on background."""
        self.menu = Gtk.Menu()
        self.menu.set_reserve_toggle_size(False)
        self.add_nav_portion_to_menu(self.menu, None)
        self.add_settings_to_menu(self.menu)
        self.menu.popup_at_pointer(event)
        return True

    def add_nav_portion_to_menu(self, menu, person_handle) -> None:
        """Add history-navigation portion to the context menu."""
        hobj = self.uistate.get_history(self.navigation_type(), self.navigation_group())
        home_sensitivity = True
        if not self.dbstate.db.get_default_person():
            home_sensitivity = False
        entries = [
            (_("Pre_vious"), self.back_clicked, not hobj.at_front()),
            (_("_Next"), self.fwd_clicked, not hobj.at_end()),
            (_("_Home"), self.cb_home, home_sensitivity),
        ]

        for label, callback, sensitivity in entries:
            item = Gtk.MenuItem.new_with_mnemonic(label)
            item.set_sensitive(sensitivity)
            if callback is not None:
                item.connect("activate", callback)
            item.show()
            menu.append(item)
        item = Gtk.MenuItem.new_with_mnemonic(_("Set _Home Person"))
        item.connect("activate", self.cb_set_home, person_handle)
        if person_handle is None:
            item.set_sensitive(False)
        item.show()
        menu.append(item)

    def add_settings_to_menu(self, menu) -> None:
        """Add settings to the context menu."""
        item = Gtk.SeparatorMenuItem()
        item.show()
        menu.append(item)

        item = Gtk.MenuItem(label=_("About Descendant View"))
        item.connect("activate", self.on_help_clicked)
        item.show()
        menu.append(item)

    def cb_build_full_nav_menu(self, obj, event, person_handle, family_handle) -> int:
        """Build the full context menu for a person."""
        from html import escape

        self.menu = Gtk.Menu()
        self.menu.set_reserve_toggle_size(False)

        person = self.dbstate.db.get_person_from_handle(person_handle)
        if not person:
            return 0

        go_item = Gtk.MenuItem(label=name_displayer.display(person))
        go_item.connect("activate", self.cb_childmenu_changed, person_handle)
        go_item.show()
        self.menu.append(go_item)

        edit_item = Gtk.MenuItem.new_with_mnemonic(_("_Edit"))
        edit_item.connect("activate", self.cb_edit_person, person_handle)
        edit_item.show()
        self.menu.append(edit_item)

        clipboard_item = Gtk.MenuItem.new_with_mnemonic(_("_Copy"))
        clipboard_item.connect(
            "activate", self.cb_copy_person_to_clipboard, person_handle
        )
        clipboard_item.show()
        self.menu.append(clipboard_item)

        # Go over spouses and build their menu
        item = Gtk.MenuItem(label=_("Spouses"))
        fam_list = person.get_family_handle_list()
        no_spouses = 1
        for fam_id in fam_list:
            family = self.dbstate.db.get_family_from_handle(fam_id)
            if family.get_father_handle() == person.get_handle():
                sp_id = family.get_mother_handle()
            else:
                sp_id = family.get_father_handle()
            spouse = None
            if sp_id:
                spouse = self.dbstate.db.get_person_from_handle(sp_id)
            if not spouse:
                continue

            if no_spouses:
                no_spouses = 0
                item.set_submenu(Gtk.Menu())
                sp_menu = item.get_submenu()
                sp_menu.set_reserve_toggle_size(False)

            sp_item = Gtk.MenuItem(label=name_displayer.display(spouse))
            sp_item.connect("activate", self.cb_childmenu_changed, sp_id)
            sp_item.show()
            sp_menu.append(sp_item)

        if no_spouses:
            item.set_sensitive(0)
        item.show()
        self.menu.append(item)

        # Go over siblings and build their menu
        item = Gtk.MenuItem(label=_("Siblings"))
        pfam_list = person.get_parent_family_handle_list()
        no_siblings = 1
        for pfam in pfam_list:
            fam = self.dbstate.db.get_family_from_handle(pfam)
            sib_list = fam.get_child_ref_list()
            for sib_ref in sib_list:
                sib_id = sib_ref.ref
                if sib_id == person.get_handle():
                    continue
                sib = self.dbstate.db.get_person_from_handle(sib_id)
                if not sib:
                    continue

                if no_siblings:
                    no_siblings = 0
                    item.set_submenu(Gtk.Menu())
                    sib_menu = item.get_submenu()
                    sib_menu.set_reserve_toggle_size(False)

                if find_children(self.dbstate.db, sib):
                    label = Gtk.Label(
                        label="<b><i>%s</i></b>" % escape(name_displayer.display(sib))
                    )
                else:
                    label = Gtk.Label(label=escape(name_displayer.display(sib)))

                sib_item = Gtk.MenuItem()
                label.set_use_markup(True)
                label.show()
                label.set_halign(Gtk.Align.START)
                sib_item.add(label)
                sib_item.connect("activate", self.cb_childmenu_changed, sib_id)
                sib_item.show()
                sib_menu.append(sib_item)

        if no_siblings:
            item.set_sensitive(0)
        item.show()
        self.menu.append(item)

        # Go over children and build their menu
        item = Gtk.MenuItem(label=_("Children"))
        no_children = 1
        childlist = find_children(self.dbstate.db, person)
        for child_handle in childlist:
            child = self.dbstate.db.get_person_from_handle(child_handle)
            if not child:
                continue

            if no_children:
                no_children = 0
                item.set_submenu(Gtk.Menu())
                child_menu = item.get_submenu()
                child_menu.set_reserve_toggle_size(False)

            if find_children(self.dbstate.db, child):
                label = Gtk.Label(
                    label="<b><i>%s</i></b>" % escape(name_displayer.display(child))
                )
            else:
                label = Gtk.Label(label=escape(name_displayer.display(child)))

            child_item = Gtk.MenuItem()
            label.set_use_markup(True)
            label.show()
            label.set_halign(Gtk.Align.START)
            child_item.add(label)
            child_item.connect("activate", self.cb_childmenu_changed, child_handle)
            child_item.show()
            child_menu.append(child_item)

        if no_children:
            item.set_sensitive(0)
        item.show()
        self.menu.append(item)

        # Go over parents and build their menu
        item = Gtk.MenuItem(label=_("Parents"))
        no_parents = 1
        par_list = find_parents(self.dbstate.db, person)
        for par_id in par_list:
            par = None
            if par_id:
                par = self.dbstate.db.get_person_from_handle(par_id)
            if not par:
                continue

            if no_parents:
                no_parents = 0
                item.set_submenu(Gtk.Menu())
                par_menu = item.get_submenu()
                par_menu.set_reserve_toggle_size(False)

            if find_parents(self.dbstate.db, par):
                label = Gtk.Label(
                    label="<b><i>%s</i></b>" % escape(name_displayer.display(par))
                )
            else:
                label = Gtk.Label(label=escape(name_displayer.display(par)))

            par_item = Gtk.MenuItem()
            label.set_use_markup(True)
            label.show()
            label.set_halign(Gtk.Align.START)
            par_item.add(label)
            par_item.connect("activate", self.cb_childmenu_changed, par_id)
            par_item.show()
            par_menu.append(par_item)

        if no_parents:
            item.set_sensitive(0)
        item.show()
        self.menu.append(item)

        # Go over related (witnessed) people
        item = Gtk.MenuItem(label=_("Related"))
        no_related = 1
        for p_id in find_witnessed_people(self.dbstate.db, person):
            per = self.dbstate.db.get_person_from_handle(p_id)
            if not per:
                continue

            if no_related:
                no_related = 0
                item.set_submenu(Gtk.Menu())
                per_menu = item.get_submenu()
                per_menu.set_reserve_toggle_size(False)

            label = Gtk.Label(label=escape(name_displayer.display(per)))

            per_item = Gtk.MenuItem()
            label.set_use_markup(True)
            label.show()
            label.set_halign(Gtk.Align.START)
            per_item.add(label)
            per_item.connect("activate", self.cb_childmenu_changed, p_id)
            per_item.show()
            per_menu.append(per_item)

        if no_related:
            item.set_sensitive(0)
        item.show()
        self.menu.append(item)

        # Add separator line
        item = Gtk.SeparatorMenuItem()
        item.show()
        self.menu.append(item)

        # Add history-based navigation
        self.add_nav_portion_to_menu(self.menu, person_handle)
        self.add_settings_to_menu(self.menu)
        self.menu.popup_at_pointer(event)
        return 1

    ####################################################################
    # Configuration
    ####################################################################
    def config_connect(self) -> None:
        """Connect to config changes."""
        self._config.connect(
            "interface.descrtl-show-images", self.cb_update_show_images
        )
        self._config.connect("interface.descrtl-show-tags", self.cb_update_show_tags)
        self._config.connect("interface.descrtl-tree-size", self.cb_update_tree_size)

    def cb_update_show_tags(self, client, cnxn_id, entry, data) -> None:
        """Called when tags setting changes."""
        self.show_tags = entry == "True"
        self.build_tree()

    def cb_update_show_images(self, client, cnxn_id, entry, data) -> None:
        """Called when images setting changes."""
        self.show_images = entry == "True"
        self.build_tree()

    def cb_update_tree_size(self, client, cnxn_id, entry, data) -> None:
        """Called when tree size setting changes."""
        self.tree_depth = int(entry)
        self.build_tree()

    def _pack_nav_button(
        self,
        button_box,
        person_box,
        icon_name: str,
        target_list,
        callback,
        handle,
        tooltip: str,
        tooltip_disabled: str,
        margin_top: int,
    ) -> None:
        """
        Add a navigation button aligned with its corresponding person box.

        A vertical SizeGroup ties the button slot to the person box height
        so the button stays centered on that box even when box heights
        differ (e.g. persons with and without images).
        """
        button = Gtk.Button.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        button.set_size_request(24, 24)
        if target_list:
            button.connect("clicked", callback, handle)
            button.set_tooltip_text(tooltip)
        else:
            button.set_sensitive(False)
            button.set_tooltip_text(tooltip_disabled)
        button.set_halign(Gtk.Align.CENTER)
        button.set_valign(Gtk.Align.CENTER)
        if margin_top:
            button.set_margin_top(margin_top)

        if person_box is not None:
            slot = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            size_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.VERTICAL)
            size_group.add_widget(slot)
            size_group.add_widget(person_box)
            slot.pack_start(button, True, True, 0)
            button_box.pack_start(slot, False, False, 0)
        else:
            button_box.pack_start(button, False, False, 0)

    def _get_configure_page_funcs(self) -> list:
        """Return config page functions."""
        return [self.config_panel]

    def config_panel(self, configdialog):
        """Build the configuration dialog widget."""
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)

        configdialog.add_checkbox(
            grid, _("Show images"), 0, "interface.descrtl-show-images"
        )
        configdialog.add_checkbox(
            grid, _("Show tags"), 1, "interface.descrtl-show-tags"
        )
        configdialog.add_slider(
            grid, _("Tree size"), 2, "interface.descrtl-tree-size", (2, 9)
        )

        return _("Layout"), grid
