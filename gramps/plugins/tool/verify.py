#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Paul Franklin
# Copyright (C) 2023       Oliver Lehmann
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
A plugin to verify the data against user-adjusted tests.
This is the research tool, not the low-level data ingerity check.

Note that this tool has an old heritage (20-Oct-2002 at least) and
so there are vestages of earlier ways of doing things which have not
been converted to a more-modern way.  For instance the way the tool
options are defined (and read in) is not done the way it would be now.
"""

# pylint: disable=not-callable
# pylint: disable=no-self-use
# pylint: disable=undefined-variable

# ------------------------------------------------------------------------
#
# standard python modules
#
# ------------------------------------------------------------------------

import os
import pickle
import statistics
from hashlib import md5

# ------------------------------------------------------------------------
#
# GNOME/GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GObject

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from gramps.gen.errors import WindowActiveError
from gramps.gen.const import URL_MANUAL_PAGE, USER_DATA_VERSION
from gramps.gen.lib import (
    ChildRefType,
    EventRoleType,
    EventType,
    FamilyRelType,
    NameType,
    Person,
)
from gramps.gen.lib.family import Family
from gramps.gen.lib.date import Today
from gramps.gui.editors import EditPerson, EditFamily
from gramps.gen.utils.db import family_name
from gramps.gen.utils.lru import LRU
from gramps.gui.display import display_help
from gramps.gui.managedwindow import ManagedWindow
from gramps.gen.updatecallback import UpdateCallback
from gramps.gui.plug import tool
from gramps.gui.glade import Glade

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
WIKI_HELP_PAGE = "%s_-_Tools" % URL_MANUAL_PAGE
WIKI_HELP_SEC = _("Verify_the_Data", "manual")


# -------------------------------------------------------------------------
#
# temp storage and related functions
#
# -------------------------------------------------------------------------
class VerifyFamily:
    def __init__(self, db, family: Family):
        self.handle = ""
        self.marr_date = 0
        self.divo_date = 0
        self.events_in_wrong_order = False
        self.events_of_type_unknown = False
        self.name = ""
        self.mother_handle = ""
        self.father_handle = ""
        self.gramps_id = ""
        self.child_ref_list = {}
        self.relationship = None

        if family is None:
            return

        self.handle = family.get_handle()
        self.name = family_name(family, db)
        self.mother_handle = family.get_mother_handle()
        self.father_handle = family.get_father_handle()
        self.gramps_id = family.get_gramps_id()
        self.child_ref_list = family.get_child_ref_list()
        self.relationship = family.get_relationship()

        prev_date = 0
        for event_ref in family.get_event_ref_list():
            event = db.get_event_from_handle(event_ref.ref)
            date_obj = event.get_date_object()
            if date_obj and date_obj.get_day() != 0 and date_obj.get_month() != 0:
                if prev_date > date_obj.get_sort_value() > 0:
                    self.events_in_wrong_order = True
                prev_date = date_obj.get_sort_value()

            if event_ref.get_role() == EventRoleType.UNKNOWN:
                self.events_of_type_unknown = True
                continue
            if (
                event_ref.get_role() == EventRoleType.FAMILY
                or event_ref.get_role() == EventRoleType.PRIMARY
            ):
                etype = event.get_type()
                date_obj = event.get_date_object()
                if etype == EventType.MARRIAGE:
                    self.marr_date = date_obj.get_sort_value()
                elif etype == EventType.DIVORCE:
                    self.divo_date = date_obj.get_sort_value()

    def get_marriage_date(self):
        return self.marr_date

    def get_divorce_date(self):
        return self.divo_date

    def get_mother_handle(self):
        return self.mother_handle

    def get_father_handle(self):
        return self.father_handle

    def is_events_of_type_unknown(self):
        return self.events_of_type_unknown

    def is_events_in_wrong_order(self):
        return self.events_in_wrong_order

    def get_name(self):
        return self.name

    def get_child_ref_list(self):
        return self.child_ref_list

    def get_relationship(self):
        return self.relationship

    def get_handle(self):
        return self.handle


class VerifyPerson:
    def __init__(self, db, person: Person):
        self.handle = ""
        self.birth_date = [0, 0]
        self.death_date = [0, 0]
        self.bapt_date = [0, 0]
        self.bury_date = [0, 0]
        self.death = False
        self.birth_date_invalid = False
        self.death_date_invalid = False
        self.events_of_type_unknown = False
        self.name = ""
        self.surname = ""
        self.name_type = NameType.UNKNOWN
        self.gramps_id = ""
        self.gender = Person.UNKNOWN
        self.family_handle_list = {}
        self.parent_family_handle_list = {}
        self.events_in_wrong_order = False

        if person is None:
            return

        self.handle = person.get_handle()
        self.name = person.get_primary_name().get_name()
        self.surname = person.get_primary_name().get_surname()
        self.gramps_id = person.get_gramps_id()
        self.gender = person.get_gender()
        self.family_handle_list = person.get_family_handle_list()
        self.parent_family_handle_list = person.get_parent_family_handle_list()
        self.death = bool(person.get_death_ref())
        self.name_type = person.get_primary_name().get_type()

        prev_date = 0
        for event_ref in person.get_event_ref_list():
            event = db.get_event_from_handle(event_ref.ref)
            date_obj = event.get_date_object()
            if date_obj and date_obj.get_day() != 0 and date_obj.get_month() != 0:
                if prev_date > date_obj.get_sort_value() > 0:
                    self.events_in_wrong_order = True
                prev_date = date_obj.get_sort_value()

            if event and event_ref.get_role() == EventRoleType.UNKNOWN:
                self.events_of_type_unknown = True
                continue
            if event and event_ref.get_role() == EventRoleType.PRIMARY:
                etype = event.get_type()
                date_obj = event.get_date_object()
                if date_obj:
                    if date_obj.get_day() == 0 or date_obj.get_month() == 0:
                        exact_date = 0
                    else:
                        exact_date = date_obj.get_sort_value()

                    if etype == EventType.BAPTISM or (
                        etype == EventType.CHRISTEN and self.bapt_date[1] == 0
                    ):
                        self.bapt_date[0] = exact_date
                        self.bapt_date[1] = date_obj.get_sort_value()
                    elif etype == EventType.BURIAL:
                        self.bury_date[0] = exact_date
                        self.bury_date[1] = date_obj.get_sort_value()
                    elif etype == EventType.BIRTH:
                        if not date_obj.get_valid():
                            self.birth_date_invalid = True
                        self.birth_date[0] = exact_date
                        self.birth_date[1] = date_obj.get_sort_value()
                    elif etype == EventType.DEATH:
                        if not date_obj.get_valid():
                            self.death_date_invalid = True
                        self.death_date[0] = exact_date
                        self.death_date[1] = date_obj.get_sort_value()

    def get_birth_date(self, estimate=False):
        return self.birth_date[int(estimate)]

    def get_death_date(self, estimate=False):
        return self.death_date[int(estimate)]

    def get_bapt_date(self, estimate=False):
        return self.bapt_date[int(estimate)]

    def get_bury_date(self, estimate=False):
        return self.bury_date[int(estimate)]

    def get_name(self):
        return self.name

    def get_surname(self):
        return self.surname

    def get_name_type(self):
        return self.name_type

    def get_family_handle_list(self):
        return self.family_handle_list

    def get_gender(self):
        return self.gender

    def get_parent_family_handle_list(self):
        return self.parent_family_handle_list

    def get_death(self):
        return self.death

    def is_birth_date_invalid(self):
        return self.birth_date_invalid

    def is_death_date_invalid(self):
        return self.death_date_invalid

    def is_events_of_type_unknown(self):
        return self.events_of_type_unknown

    def is_events_in_wrong_order(self):
        return self.events_in_wrong_order

    def get_gramps_id(self):
        return self.gramps_id

    def get_handle(self):
        return self.handle


_person_cache_size = 20000
_family_cache_size = 10000
_person_cache = LRU(_person_cache_size + 1)
_family_cache = LRU(_family_cache_size + 1)
_today = Today().get_sort_value()


def find_person(db, handle):
    """find a person, given a handle"""
    if handle not in _person_cache:
        person = db.get_person_from_handle(handle)
        verify_person = VerifyPerson(db, person)
        _person_cache[handle] = verify_person
    return _person_cache[handle]


def find_family(db, handle):
    """find a family, given a handle"""
    if handle not in _family_cache:
        family = db.get_family_from_handle(handle)
        verify_family = VerifyFamily(db, family)
        _family_cache[handle] = verify_family
    return _family_cache[handle]


def preload_person_cache(db):
    """puts all existing people in the cache"""
    for person in db.iter_people():
        verify_person = VerifyPerson(db, person)
        _person_cache[person.get_handle()] = verify_person


def preload_family_cache(db):
    """puts all existing families in the cache"""
    for family in db.iter_families():
        verify_family = VerifyFamily(db, family)
        _family_cache[family.get_handle()] = verify_family


def clear_cache():
    """clear the cache"""
    _person_cache.clear()
    _family_cache.clear()


# -------------------------------------------------------------------------
#
# helper functions
#
# -------------------------------------------------------------------------
def get_age_at_death(person, estimate):
    """get a person's age at death"""
    birth_date = person.get_birth_date(estimate)
    death_date = person.get_death_date(estimate)
    if (birth_date > 0) and (death_date > 0):
        return death_date - birth_date
    return 0


def get_father(db, family):
    """get a family's father"""
    if not family:
        return VerifyPerson(None, None)
    father_handle = family.get_father_handle()
    if father_handle:
        return find_person(db, father_handle)
    return VerifyPerson(None, None)


def get_mother(db, family):
    """get a family's mother"""
    if not family:
        return VerifyPerson(None, None)
    mother_handle = family.get_mother_handle()
    if mother_handle:
        return find_person(db, mother_handle)
    return VerifyPerson(None, None)


def get_child_birth_dates(db, family, estimate):
    """get a family's children's birth dates"""
    dates = []
    for child_ref in family.get_child_ref_list():
        child = find_person(db, child_ref.ref)
        child_birth_date = child.get_birth_date(estimate)
        if child_birth_date > 0:
            dates.append(child_birth_date)
    return dates


def get_n_children(db, person):
    """get the number of a family's children"""
    number = 0
    for family_handle in person.get_family_handle_list():
        family = find_family(db, family_handle)
        if family:
            number += len(family.get_child_ref_list())
    return number


# -------------------------------------------------------------------------
#
# Actual tool
#
# -------------------------------------------------------------------------
class Verify(tool.Tool, ManagedWindow, UpdateCallback):
    """
    A plugin to verify the data against user-adjusted tests.
    This is the research tool, not the low-level data ingerity check.
    """

    def __init__(self, dbstate, user, options_class, name, callback=None):
        """initialize things"""
        uistate = user.uistate
        self.label = _("Data Verify tool")
        self.v_r = None
        tool.Tool.__init__(self, dbstate, options_class, name)
        ManagedWindow.__init__(self, uistate, [], self.__class__)
        if uistate:
            UpdateCallback.__init__(self, self.uistate.pulse_progressbar)

        self.dbstate = dbstate
        if uistate:
            self.init_gui()
        else:
            self.add_results = self.add_results_cli
            self.run_the_tool(cli=True)

    def add_results_cli(self, results):
        """print data for the user, no GUI"""
        (msg, gramps_id, name, the_type, rule_id, severity, handle) = results
        severity_str = "S"
        if severity == Rule.WARNING:
            severity_str = "W"
        elif severity == Rule.ERROR:
            severity_str = "E"
        # Translators: needed for French+Arabic, ignore otherwise
        print(
            _("%(severity)s: %(msg)s, %(type)s: %(gid)s, %(name)s")
            % {
                "severity": severity_str,
                "msg": msg,
                "type": the_type,
                "gid": gramps_id,
                "name": name,
            }
        )

    def init_gui(self):
        """Draw dialog and make it handle everything"""
        self.v_r = None
        self.top = Glade()
        self.top.connect_signals(
            {
                "destroy_passed_object": self.close,
                "on_help_clicked": self.on_help_clicked,
                "on_verify_ok_clicked": self.on_apply_clicked,
                "on_delete_event": self.close,
            }
        )

        window = self.top.toplevel
        self.set_window(window, self.top.get_object("title"), self.label)
        self.setup_configs("interface.verify", 650, 400)

        o_dict = self.options.handler.options_dict
        for option in o_dict:
            if option in ["estimate_age", "invdate"]:
                self.top.get_object(option).set_active(o_dict[option])
            else:
                self.top.get_object(option).set_value(o_dict[option])
        self.show()

    def build_menu_names(self, obj):
        """build the menu names"""
        return (_("Tool settings"), self.label)

    def on_help_clicked(self, obj):
        """Display the relevant portion of Gramps manual"""
        display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC)

    def on_apply_clicked(self, obj):
        """event handler for user clicking the OK button: start things"""
        run_button = self.top.get_object("button4")
        close_button = self.top.get_object("button5")
        run_button.set_sensitive(False)
        close_button.set_sensitive(False)
        o_dict = self.options.handler.options_dict
        for option in o_dict:
            if option in ["estimate_age", "invdate"]:
                o_dict[option] = self.top.get_object(option).get_active()
            else:
                o_dict[option] = self.top.get_object(option).get_value_as_int()

        try:
            self.v_r = VerifyResults(
                self.dbstate, self.uistate, self.track, self.top, self.close
            )
            self.add_results = self.v_r.add_results
            self.v_r.load_ignored(self.db.full_name)
        except WindowActiveError:
            pass
        except AttributeError:  # VerifyResults.load_ignored was not run
            self.v_r.ignores = {}

        self.track_ref_for_deletion("v_r")
        self.track_ref_for_deletion("add_results")
        self.track_ref_for_deletion("options")

        self.uistate.set_busy_cursor(True)
        self.uistate.progress.show()
        busy_cursor = Gdk.Cursor.new_for_display(
            Gdk.Display.get_default(), Gdk.CursorType.WATCH
        )
        self.window.get_window().set_cursor(busy_cursor)
        try:
            self.v_r.window.get_window().set_cursor(busy_cursor)
        except AttributeError:
            pass

        self.run_the_tool(cli=False)

        self.uistate.progress.hide()
        self.uistate.set_busy_cursor(False)
        try:
            self.window.get_window().set_cursor(None)
            self.v_r.window.get_window().set_cursor(None)
        except AttributeError:
            pass
        run_button.set_sensitive(True)
        close_button.set_sensitive(True)
        self.reset()

        # Save options
        self.options.handler.save_options()

    def process_family(
        self,
        cli,
        verify_family,
        hwdif,
        yngmar,
        oldmar,
        oldmom,
        yngmom,
        cbspan,
        cspace,
        estimate_age,
    ):
        """runs all family rules on the given family"""
        rule_list = [
            SameSexFamily(self.db, verify_family),
            FemaleHusband(self.db, verify_family),
            MaleWife(self.db, verify_family),
            SameSurnameFamily(self.db, verify_family),
            LargeAgeGapFamily(self.db, verify_family, hwdif, estimate_age),
            MarriageBeforeBirth(self.db, verify_family, estimate_age),
            MarriageAfterDeath(self.db, verify_family, estimate_age),
            EarlyMarriage(self.db, verify_family, yngmar, estimate_age),
            LateMarriage(self.db, verify_family, oldmar, estimate_age),
            OldParent(self.db, verify_family, oldmom, olddad, estimate_age),
            YoungParent(self.db, verify_family, yngmom, yngdad, estimate_age),
            UnbornParent(self.db, verify_family, estimate_age),
            DeadParent(self.db, verify_family, estimate_age),
            LargeChildrenSpan(self.db, verify_family, cbspan, estimate_age),
            LargeChildrenAgeDiff(self.db, verify_family, cspace, estimate_age),
            MarriedRelation(self.db, verify_family),
            ChildrenOrderIncorrect(self.db, verify_family, estimate_age),
            FamilyHasEventsOfTypeUnknown(self.db, verify_family),
            FamilyHasEventsInWrongOrder(self.db, verify_family),
        ]

        for rule in rule_list:
            if rule.broken():
                self.add_results(rule.report_itself())

        if not cli:
            self.update()

    def process_person(
        self,
        cli,
        verify_person,
        oldage,
        wedder,
        oldunm,
        mxchilddad,
        mxchildmom,
        invdate,
        estimate_age,
    ):
        """runs all person rules on the given person"""
        rule_list = [
            BirthAfterBapt(self.db, verify_person),
            DeathBeforeBapt(self.db, verify_person),
            BirthAfterBury(self.db, verify_person),
            DeathAfterBury(self.db, verify_person),
            BirthAfterDeath(self.db, verify_person),
            BaptAfterBury(self.db, verify_person),
            OldAge(self.db, verify_person, oldage, estimate_age),
            OldAgeButNoDeath(self.db, verify_person, oldage, estimate_age),
            UnknownGender(self.db, verify_person),
            MultipleParents(self.db, verify_person),
            MarriedOften(self.db, verify_person, wedder),
            OldUnmarried(self.db, verify_person, oldunm, estimate_age),
            TooManyChildren(self.db, verify_person, mxchilddad, mxchildmom),
            Disconnected(self.db, verify_person),
            InvalidBirthDate(self.db, verify_person, invdate),
            InvalidDeathDate(self.db, verify_person, invdate),
            BirthEqualsDeath(self.db, verify_person),
            BirthEqualsMarriage(self.db, verify_person),
            DeathEqualsMarriage(self.db, verify_person),
            BaptTooLate(self.db, verify_person),
            BuryTooLate(self.db, verify_person),
            FamilyOrderIncorrect(self.db, verify_person, estimate_age),
            PersonHasEventsOfTypeUnknown(self.db, verify_person),
            PersonHasEventsInWrongOrder(self.db, verify_person),
        ]
        for rule in rule_list:
            if rule.broken():
                self.add_results(rule.report_itself())

        if not cli:
            self.update()

    def run_the_tool(self, cli=False):
        """run the tool"""

        n_people = self.db.get_number_of_people()
        n_families = self.db.get_number_of_families()
        if n_people <= _person_cache_size:
            preload_person_cache(self.db)
        if n_families <= _family_cache_size:
            preload_family_cache(self.db)

        for option, value in self.options.handler.options_dict.items():
            exec("%s = %s" % (option, value), globals())
            # TODO my pylint doesn't seem to understand these variables really
            # are defined here, so I have disabled the undefined-variable error

        if self.v_r:
            self.v_r.real_model.clear()

        self.set_total(n_people + n_families)

        family_handles = set(self.db.get_family_handles())

        for person in self.db.iter_people():
            verify_person = VerifyPerson(self.db, person)
            _person_cache[verify_person.get_handle()] = verify_person
            for family_handle in verify_person.get_family_handle_list():
                if family_handle in family_handles:
                    verify_family = find_family(self.db, family_handle)
                    self.process_family(
                        cli,
                        verify_family,
                        hwdif,
                        yngmar,
                        oldmar,
                        oldmom,
                        yngmom,
                        cbspan,
                        cspace,
                        estimate_age,
                    )
                    family_handles.remove(family_handle)

            self.process_person(
                cli,
                verify_person,
                oldage,
                wedder,
                oldunm,
                mxchilddad,
                mxchildmom,
                invdate,
                estimate_age,
            )

        # Family-based rules - for any left over families (families without any spouses)
        for family_handle in family_handles:
            verify_family = find_family(self.db, family_handle)

            self.process_family(
                cli,
                verify_family,
                hwdif,
                yngmar,
                oldmar,
                oldmom,
                yngmom,
                cbspan,
                cspace,
                estimate_age,
            )

        clear_cache()
        self.update = None  # Needed for garbage collection


# -------------------------------------------------------------------------
#
# Display the results
#
# -------------------------------------------------------------------------
class VerifyResults(ManagedWindow):
    """GUI class to show the results in another dialog"""

    IGNORE_COL = 0
    WARNING_COL = 1
    OBJ_ID_COL = 2
    OBJ_NAME_COL = 3
    OBJ_TYPE_COL = 4
    RULE_ID_COL = 5
    OBJ_HANDLE_COL = 6
    FG_COLOR_COL = 7
    TRUE_COL = 8
    SHOW_COL = 9

    def __init__(self, dbstate, uistate, track, glade, closeall):
        """initialize things"""
        self.title = _("Data Verification Results")

        ManagedWindow.__init__(self, uistate, track, self.__class__)

        self.dbstate = dbstate
        self.closeall = closeall
        self._set_filename()
        self.top = glade
        window = self.top.get_object("verify_result")
        self.set_window(window, self.top.get_object("title2"), self.title)
        self.setup_configs("interface.verifyresults", 500, 300)
        window.connect("close", self.close)
        close_btn = self.top.get_object("closebutton1")
        close_btn.connect("clicked", self.close)

        self.warn_tree = self.top.get_object("warn_tree")
        self.warn_tree.connect("button_press_event", self.double_click)

        self.selection = self.warn_tree.get_selection()

        self.hide_button = self.top.get_object("hide_button")
        self.hide_button.connect("toggled", self.hide_toggled)

        self.mark_button = self.top.get_object("mark_all")
        self.mark_button.connect("clicked", self.mark_clicked)

        self.unmark_button = self.top.get_object("unmark_all")
        self.unmark_button.connect("clicked", self.unmark_clicked)

        self.invert_button = self.top.get_object("invert_all")
        self.invert_button.connect("clicked", self.invert_clicked)

        self.parent_iter_cache = {}

        self.real_model = Gtk.TreeStore(
            GObject.TYPE_BOOLEAN,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            object,
            GObject.TYPE_STRING,
            GObject.TYPE_STRING,
            GObject.TYPE_BOOLEAN,
            GObject.TYPE_BOOLEAN,
        )
        self.filt_model = self.real_model.filter_new()
        self.filt_model.set_visible_column(VerifyResults.TRUE_COL)
        if hasattr(self.filt_model, "sort_new_with_model"):
            self.sort_model = self.filt_model.sort_new_with_model()
        else:
            self.sort_model = Gtk.TreeModelSort.new_with_model(self.filt_model)
        self.warn_tree.set_model(self.sort_model)

        self.renderer = Gtk.CellRendererText()
        self.img_renderer = Gtk.CellRendererPixbuf()
        self.bool_renderer = Gtk.CellRendererToggle()
        self.bool_renderer.connect("toggled", self.selection_toggled)
        self.track_ref_for_deletion("bool_renderer")

        # Add ignore column
        ignore_column = Gtk.TreeViewColumn(
            _("Mark"), self.bool_renderer, active=VerifyResults.IGNORE_COL
        )
        ignore_column.set_sort_column_id(VerifyResults.IGNORE_COL)
        self.warn_tree.append_column(ignore_column)

        # Add image column
        img_column = Gtk.TreeViewColumn(None, self.img_renderer)
        img_column.set_cell_data_func(self.img_renderer, self.get_image)
        self.warn_tree.append_column(img_column)

        # Add column with the warning text
        warn_column = Gtk.TreeViewColumn(
            _("Warning"),
            self.renderer,
            text=VerifyResults.WARNING_COL,
            foreground=VerifyResults.FG_COLOR_COL,
        )
        warn_column.set_sort_column_id(VerifyResults.WARNING_COL)
        self.warn_tree.append_column(warn_column)

        # Add column with object gramps_id
        id_column = Gtk.TreeViewColumn(
            _("ID"),
            self.renderer,
            text=VerifyResults.OBJ_ID_COL,
            foreground=VerifyResults.FG_COLOR_COL,
        )
        id_column.set_sort_column_id(VerifyResults.OBJ_ID_COL)
        self.warn_tree.append_column(id_column)

        # Add column with object name
        name_column = Gtk.TreeViewColumn(
            _("Name"),
            self.renderer,
            text=VerifyResults.OBJ_NAME_COL,
            foreground=VerifyResults.FG_COLOR_COL,
        )
        name_column.set_sort_column_id(VerifyResults.OBJ_NAME_COL)
        self.warn_tree.append_column(name_column)

        self.show()
        self.window_shown = False

    def _set_filename(self):
        """set the file where people who will be ignored will be kept"""
        db_filename = self.dbstate.db.get_save_path()
        if isinstance(db_filename, str):
            db_filename = db_filename.encode("utf-8")
        md5sum = md5(db_filename)
        self.ignores_filename = os.path.join(
            USER_DATA_VERSION, md5sum.hexdigest() + os.path.extsep + "vfm"
        )

    def load_ignored(self, db_filename):
        """get ready to load the file with the previously-ignored people"""
        ## a new Gramps major version means recreating the .vfm file.
        ## User can copy over old one, with name of new one, but no guarantee
        ## that will work.
        if not self._load_ignored(self.ignores_filename):
            self.ignores = {}

    def _load_ignored(self, filename):
        """load the file with the people who were previously ignored"""
        try:
            try:
                file = open(filename, "rb")
            except IOError:
                return False
            self.ignores = pickle.load(file)
            file.close()
            return True
        except (IOError, EOFError):
            file.close()
            return False

    def save_ignored(self, new_ignores):
        """get ready to save the file with the ignored people"""
        self.ignores = new_ignores
        self._save_ignored(self.ignores_filename)

    def _save_ignored(self, filename):
        """save the file with the people the user wants to ignore"""
        try:
            with open(filename, "wb") as file:
                pickle.dump(self.ignores, file, 1)
            return True
        except IOError:
            return False

    def get_marking(self, handle, rule_id):
        if handle in self.ignores:
            return rule_id in self.ignores[handle]
        return False

    def get_new_marking(self):
        new_ignores = {}
        for row_num in range(len(self.real_model)):
            path = (row_num,)
            row = self.real_model[path]
            ignore = row[VerifyResults.IGNORE_COL]
            if ignore:
                handle = row[VerifyResults.OBJ_HANDLE_COL]
                rule_id = row[VerifyResults.RULE_ID_COL]
                if handle not in new_ignores:
                    new_ignores[handle] = set()
                new_ignores[handle].add(rule_id)
        return new_ignores

    def close(self, *obj):
        """close the dialog and write out the file"""
        new_ignores = self.get_new_marking()
        self.save_ignored(new_ignores)

        ManagedWindow.close(self, *obj)
        self.closeall()

    def set_parent_text(self, parent_iter, msg, num):
        """update the parent rows message including the number of the children"""
        parent_msg = msg + " (" + str(num) + ")"
        self.real_model.set_value(parent_iter, VerifyResults.WARNING_COL, parent_msg)

    def refresh_all_parent_texts(self):
        """sync all parent texts with the number of currently displayed children"""
        parent_iter = self.filt_model.get_iter_first()
        while parent_iter:
            child_iter = self.filt_model.iter_children(parent_iter)
            if child_iter:
                msg = self.filt_model.get_value(child_iter, VerifyResults.WARNING_COL)
                num = self.filt_model.iter_n_children(parent_iter)
                real_parent_iter = self.filt_model.convert_iter_to_child_iter(
                    parent_iter
                )
                self.set_parent_text(real_parent_iter, msg, num)
            parent_iter = self.filt_model.iter_next(parent_iter)

    def hide_toggled(self, button):
        """either hide the marked rows or show all rows"""
        # memorize all currently expanded rows
        expanded_paths = []
        parent_iter = self.sort_model.get_iter_first()
        while parent_iter:
            sort_path = self.sort_model.get_path(parent_iter)
            if self.warn_tree.row_expanded(sort_path):
                filt_path = self.sort_model.convert_path_to_child_path(sort_path)
                expanded_paths.append(
                    self.filt_model.convert_path_to_child_path(filt_path)
                )
            parent_iter = self.sort_model.iter_next(parent_iter)

        self.filt_model = self.real_model.filter_new()
        if button.get_active():
            button.set_label(_("_Show all"))
            self.filt_model.set_visible_column(VerifyResults.SHOW_COL)
        else:
            button.set_label(_("_Hide marked"))
            self.filt_model.set_visible_column(VerifyResults.TRUE_COL)
        if hasattr(self.filt_model, "sort_new_with_model"):
            self.sort_model = self.filt_model.sort_new_with_model()
        else:
            self.sort_model = Gtk.TreeModelSort.new_with_model(self.filt_model)

        self.refresh_all_parent_texts()

        self.warn_tree.set_model(self.sort_model)

        # expand all not filtered rows which already where expanded
        for real_path in expanded_paths:
            filt_path = self.filt_model.convert_child_path_to_path(real_path)
            if filt_path is not None:
                self.warn_tree.expand_row(filt_path, False)

    def set_row_selection(self, row_iter, value):
        """toggle the given rows checkbox"""
        path = self.real_model.get_path(row_iter)
        self.real_model.set_value(row_iter, VerifyResults.IGNORE_COL, value)
        self.real_model.set_value(row_iter, VerifyResults.SHOW_COL, not value)
        self.real_model.row_changed(path, row_iter)

    def selection_toggled(self, cell, path_string):
        """the rows checkbox click handler"""
        sort_path = tuple(map(int, path_string.split(":")))
        filt_path = self.sort_model.convert_path_to_child_path(Gtk.TreePath(sort_path))
        real_path = self.filt_model.convert_path_to_child_path(filt_path)
        row = self.real_model[real_path]
        the_type = row[VerifyResults.OBJ_TYPE_COL]

        ignore = not row[VerifyResults.IGNORE_COL]
        if the_type == Rule.TYPE_GROUP:
            # (un)select all children when the parent gets activly (un)selected
            child_iter = self.real_model.iter_children(row.iter)
            while child_iter:
                self.set_row_selection(child_iter, ignore)
                child_iter = self.real_model.iter_next(child_iter)
        else:
            parent_iter = self.real_model.iter_parent(row.iter)
            parent_ignore = self.real_model.get_value(
                parent_iter, VerifyResults.IGNORE_COL
            )
            if parent_ignore and not ignore:
                # remove the parents selection when a child becomes no longer selected
                self.set_row_selection(parent_iter, False)
            else:
                all_ignored = True
                child_iter = self.real_model.iter_children(parent_iter)
                while child_iter:
                    # check if all children are selected (or not)
                    if self.real_model.get_path(child_iter) == real_path:
                        # the value of the triggering row is not yet synced into
                        #   the model so we can't read it from there
                        value = ignore
                    else:
                        value = self.real_model.get_value(
                            child_iter, VerifyResults.IGNORE_COL
                        )
                    if not value:
                        all_ignored = False
                        break
                    child_iter = self.real_model.iter_next(child_iter)
                if all_ignored:
                    # select parent when all children become selected
                    self.set_row_selection(parent_iter, True)
                elif self.hide_button.get_active():
                    # update parents warning text when view is in filter mode
                    filt_iter = self.filt_model.get_iter(filt_path)
                    filt_parent_iter = self.filt_model.iter_parent(filt_iter)
                    num_children = self.filt_model.iter_n_children(filt_parent_iter)
                    msg = row[VerifyResults.WARNING_COL]
                    self.set_parent_text(parent_iter, msg, num_children - 1)
        self.set_row_selection(row.iter, ignore)

    def mark_unmark(self, mark):
        """either selects or unselects all rows"""
        parent_iter = self.real_model.get_iter_first()
        while parent_iter:
            ignore = self.real_model.get_value(parent_iter, VerifyResults.IGNORE_COL)
            if (mark and not ignore) or not mark:
                # if the parent should be selected but is already selected skip it
                # if the selection should be removed we must always loop through
                #   all children
                child_iter = self.real_model.iter_children(parent_iter)
                while child_iter:
                    self.set_row_selection(child_iter, mark)
                    child_iter = self.real_model.iter_next(child_iter)
                self.set_row_selection(parent_iter, mark)
            parent_iter = self.real_model.iter_next(parent_iter)
        self.filt_model.refilter()
        self.refresh_all_parent_texts()

    def mark_clicked(self, mark_button):
        """the mark button click handler"""
        self.mark_unmark(True)

    def unmark_clicked(self, unmark_button):
        """the unmark button click handler"""
        self.mark_unmark(False)

    def invert_clicked(self, invert_button):
        """invert the current selection"""
        parent_iter = self.real_model.get_iter_first()
        while parent_iter:
            child_iter = self.real_model.iter_children(parent_iter)
            all_ignored = True
            while child_iter:
                ignore = not self.real_model.get_value(
                    child_iter, VerifyResults.IGNORE_COL
                )
                if not ignore:
                    all_ignored = False
                self.set_row_selection(child_iter, ignore)
                child_iter = self.real_model.iter_next(child_iter)
            self.set_row_selection(parent_iter, all_ignored)
            parent_iter = self.real_model.iter_next(parent_iter)
        self.filt_model.refilter()
        self.refresh_all_parent_texts()

    def double_click(self, obj, event):
        """the user wants to edit the selected person or family"""
        if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS and event.button == 1:
            (model, node) = self.selection.get_selected()
            if not node:
                return
            sort_path = self.sort_model.get_path(node)
            filt_path = self.sort_model.convert_path_to_child_path(sort_path)
            real_path = self.filt_model.convert_path_to_child_path(filt_path)
            row = self.real_model[real_path]
            the_type = row[VerifyResults.OBJ_TYPE_COL]
            handle = row[VerifyResults.OBJ_HANDLE_COL]
            if the_type == Rule.TYPE_PERSON:
                try:
                    person = self.dbstate.db.get_person_from_handle(handle)
                    EditPerson(self.dbstate, self.uistate, self.track, person)
                except WindowActiveError:
                    pass
            elif the_type == Rule.TYPE_FAMILY:
                try:
                    family = self.dbstate.db.get_family_from_handle(handle)
                    EditFamily(self.dbstate, self.uistate, self.track, family)
                except WindowActiveError:
                    pass
            elif the_type == Rule.TYPE_GROUP:
                if self.warn_tree.row_expanded(filt_path):
                    self.warn_tree.collapse_row(filt_path)
                else:
                    self.warn_tree.expand_row(filt_path, False)

    def get_image(self, column, cell, model, iter_, user_data=None):
        """flag whether each line is a person or family"""
        the_type = model.get_value(iter_, VerifyResults.OBJ_TYPE_COL)
        if the_type == Rule.TYPE_PERSON:
            cell.set_property("icon-name", "gramps-person")
        elif the_type == Rule.TYPE_FAMILY:
            cell.set_property("icon-name", "gramps-family")
        else:
            cell.set_property("icon-name", None)

    def add_results(self, results):
        """adds the negative result of an evaluated Rule to the model"""
        (msg, gramps_id, name, the_type, rule_id, severity, handle) = results
        ignore = self.get_marking(handle, rule_id)
        if severity == Rule.ERROR:
            line_color = "red"
        else:
            line_color = None

        parent_iter = None
        # rule_id can't be used because there are rules with dynamic messages
        if msg in self.parent_iter_cache:
            parent_iter = self.parent_iter_cache[msg]
        else:
            parent_iter = self.real_model.append(
                None,
                row=[
                    None,
                    msg,
                    None,
                    None,
                    Rule.TYPE_GROUP,
                    rule_id,
                    None,
                    line_color,
                    True,
                    True,
                ],
            )
            self.parent_iter_cache[msg] = parent_iter

        self.real_model.append(
            parent_iter,
            row=[
                ignore,
                msg,
                gramps_id,
                name,
                the_type,
                rule_id,
                handle,
                line_color,
                True,
                not ignore,
            ],
        )

        num = self.real_model.iter_n_children(parent_iter)
        self.set_parent_text(parent_iter, msg, num)

        if not self.window_shown:
            self.window.show()
            self.window_shown = True

    def build_menu_names(self, obj):
        """build the menu names"""
        return (self.title, self.title)


# ------------------------------------------------------------------------
#
#
#
# ------------------------------------------------------------------------
class VerifyOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, person_id=None):
        """initialize the options"""
        tool.ToolOptions.__init__(self, name, person_id)

        # Options specific for this report
        self.options_dict = {
            "oldage": 90,
            "hwdif": 30,
            "cspace": 8,
            "cbspan": 25,
            "yngmar": 17,
            "oldmar": 50,
            "oldmom": 48,
            "yngmom": 17,
            "yngdad": 18,
            "olddad": 65,
            "wedder": 3,
            "mxchildmom": 12,
            "mxchilddad": 15,
            "lngwdw": 30,
            "oldunm": 99,
            "estimate_age": 0,
            "invdate": 1,
        }
        # TODO these strings are defined in the glade file (more or less, since
        # those have accelerators), and so are not translated here, but that
        # means that a CLI user who runs gramps in a non-English language and
        # says (for instance) "show=oldage" will see "Maximum age" in English
        # (but I think such a CLI use is very unlikely and so is low priority,
        # especially since the tool's normal CLI output will be translated)
        self.options_help = {
            "oldage": ("=num", "Maximum age", "Age in years"),
            "hwdif": (
                "=num",
                "Maximum husband-wife age difference",
                "Age difference in years",
            ),
            "cspace": (
                "=num",
                "Maximum number of years between children",
                "Number of years",
            ),
            "cbspan": (
                "=num",
                "Maximum span of years for all children",
                "Span in years",
            ),
            "yngmar": ("=num", "Minimum age to marry", "Age in years"),
            "oldmar": ("=num", "Maximum age to marry", "Age in years"),
            "oldmom": ("=num", "Maximum age to bear a child", "Age in years"),
            "yngmom": ("=num", "Minimum age to bear a child", "Age in years"),
            "yngdad": ("=num", "Minimum age to father a child", "Age in years"),
            "olddad": ("=num", "Maximum age to father a child", "Age in years"),
            "wedder": (
                "=num",
                "Maximum number of spouses for a person",
                "Number of spouses",
            ),
            "mxchildmom": (
                "=num",
                "Maximum number of children for a woman",
                "Number of children",
            ),
            "mxchilddad": (
                "=num",
                "Maximum  number of children for a man",
                "Number of chidlren",
            ),
            "lngwdw": (
                "=num",
                "Maximum number of consecutive years "
                "of widowhood before next marriage",
                "Number of years",
            ),
            "oldunm": ("=num", "Maximum age for an unmarried person" "Number of years"),
            "estimate_age": (
                "=0/1",
                "Whether to estimate missing or inexact dates",
                ["Do not estimate", "Estimate dates"],
                True,
            ),
            "invdate": (
                "=0/1",
                "Whether to check for invalid dates" "Do not identify invalid dates",
                "Identify invalid dates",
                True,
            ),
        }


# -------------------------------------------------------------------------
#
# Base classes for different tests -- the rules
#
# -------------------------------------------------------------------------
class Rule:
    """
    Basic class for use in this tool.

    Other rules must inherit from this.
    """

    ID = 0
    TYPE = ""

    ERROR = 1
    WARNING = 2

    SEVERITY = WARNING

    TYPE_PERSON = "Person"
    TYPE_FAMILY = "Family"
    TYPE_GROUP = "Group"

    def __init__(self, db, obj):
        """initialize the rule"""
        self.db = db
        self.obj = obj

    def broken(self):
        """
        Return boolean indicating whether this rule is violated.
        """
        return False

    def get_message(self):
        """return the rule's error message"""
        assert False, "Need to be overriden in the derived class"

    def get_name(self):
        """return the persons or families primary name"""
        return self.obj.get_name()

    def get_handle(self):
        """return the object's handle"""
        return self.obj.get_handle()

    def get_id(self):
        """return the object's gramps_id"""
        return self.obj.gramps_id

    def get_rule_id(self):
        """return the rule's identification number, and parameters"""
        params = self._get_params()
        return (self.ID, params)

    def _get_params(self):
        """return the rule's parameters"""
        return tuple()

    def report_itself(self):
        """return the details about a rule"""
        handle = self.get_handle()
        the_type = self.TYPE
        rule_id = self.get_rule_id()
        severity = self.SEVERITY
        name = self.get_name()
        gramps_id = self.get_id()
        msg = self.get_message()
        self.get_message = None  # Needed for garbage collection
        return (msg, gramps_id, name, the_type, rule_id, severity, handle)


class PersonRule(Rule):
    """
    Person-based class.
    """

    TYPE = Rule.TYPE_PERSON


class FamilyRule(Rule):
    """
    Family-based class.
    """

    TYPE = Rule.TYPE_FAMILY


# -------------------------------------------------------------------------
#
# Actual rules for testing
#
# -------------------------------------------------------------------------
class BirthAfterBapt(PersonRule):
    """test if a person was baptised before their birth"""

    ID = 1
    SEVERITY = Rule.ERROR

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        birth_date = self.obj.get_birth_date()
        bapt_date = self.obj.get_bapt_date()
        birth_ok = birth_date > 0 if birth_date is not None else False
        bapt_ok = bapt_date > 0 if bapt_date is not None else False
        return birth_ok and bapt_ok and birth_date > bapt_date

    def get_message(self):
        """return the rule's error message"""
        return _("Baptism before birth")


class DeathBeforeBapt(PersonRule):
    """test if a person died before their baptism"""

    ID = 2
    SEVERITY = Rule.ERROR

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        death_date = self.obj.get_death_date()
        bapt_date = self.obj.get_bapt_date()
        bapt_ok = bapt_date > 0 if bapt_date is not None else False
        death_ok = death_date > 0 if death_date is not None else False
        return death_ok and bapt_ok and bapt_date > death_date

    def get_message(self):
        """return the rule's error message"""
        return _("Death before baptism")


class BirthAfterBury(PersonRule):
    """test if a person was buried before their birth"""

    ID = 3
    SEVERITY = Rule.ERROR

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        birth_date = self.obj.get_birth_date()
        bury_date = self.obj.get_bury_date()
        birth_ok = birth_date > 0 if birth_date is not None else False
        bury_ok = bury_date > 0 if bury_date is not None else False
        return birth_ok and bury_ok and birth_date > bury_date

    def get_message(self):
        """return the rule's error message"""
        return _("Burial before birth")


class DeathAfterBury(PersonRule):
    """test if a person was buried before their death"""

    ID = 4
    SEVERITY = Rule.ERROR

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        death_date = self.obj.get_death_date()
        bury_date = self.obj.get_bury_date()
        death_ok = death_date > 0 if death_date is not None else False
        bury_ok = bury_date > 0 if bury_date is not None else False
        return death_ok and bury_ok and death_date > bury_date

    def get_message(self):
        """return the rule's error message"""
        return _("Burial before death")


class BirthAfterDeath(PersonRule):
    """test if a person died before their birth"""

    ID = 5
    SEVERITY = Rule.ERROR

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        birth_date = self.obj.get_birth_date()
        death_date = self.obj.get_death_date()
        birth_ok = birth_date > 0 if birth_date is not None else False
        death_ok = death_date > 0 if death_date is not None else False
        return birth_ok and death_ok and birth_date > death_date

    def get_message(self):
        """return the rule's error message"""
        return _("Death before birth")


class BaptAfterBury(PersonRule):
    """test if a person was buried before their baptism"""

    ID = 6
    SEVERITY = Rule.ERROR

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        bapt_date = self.obj.get_bapt_date()
        bury_date = self.obj.get_bury_date()
        bapt_ok = bapt_date > 0 if bapt_date is not None else False
        bury_ok = bury_date > 0 if bury_date is not None else False
        return bapt_ok and bury_ok and bapt_date > bury_date

    def get_message(self):
        """return the rule's error message"""
        return _("Burial before baptism")


class OldAge(PersonRule):
    """test if a person died beyond the age the user has set"""

    ID = 7
    SEVERITY = Rule.WARNING

    def __init__(self, db, person, old_age, est):
        """initialize the rule"""
        PersonRule.__init__(self, db, person)
        self.old_age = old_age
        self.est = est

    def _get_params(self):
        """return the rule's parameters"""
        return (self.old_age, self.est)

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        age_at_death = get_age_at_death(self.obj, self.est)
        return age_at_death / 365 > self.old_age

    def get_message(self):
        """return the rule's error message"""
        return _("Old age at death")


class UnknownGender(PersonRule):
    """test if a person is neither a male nor a female"""

    ID = 8
    SEVERITY = Rule.WARNING

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        return self.obj.get_gender() == Person.UNKNOWN

    def get_message(self):
        """return the rule's error message"""
        return _("Unknown gender")


class MultipleParents(PersonRule):
    """test if a person belongs to multiple families"""

    ID = 9
    SEVERITY = Rule.WARNING

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        n_parent_sets = len(self.obj.get_parent_family_handle_list())
        return n_parent_sets > 1

    def get_message(self):
        """return the rule's error message"""
        return _("Multiple parents")


class MarriedOften(PersonRule):
    """test if a person was married 'often'"""

    ID = 10
    SEVERITY = Rule.WARNING

    def __init__(self, db, person, wedder):
        """initialize the rule"""
        PersonRule.__init__(self, db, person)
        self.wedder = wedder

    def _get_params(self):
        """return the rule's parameters"""
        return (self.wedder,)

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        n_spouses = len(self.obj.get_family_handle_list())
        return n_spouses > self.wedder

    def get_message(self):
        """return the rule's error message"""
        return _("Married often")


class OldUnmarried(PersonRule):
    """test if a person was married when they died"""

    ID = 11
    SEVERITY = Rule.WARNING

    def __init__(self, db, person, old_unm, est):
        """initialize the rule"""
        PersonRule.__init__(self, db, person)
        self.old_unm = old_unm
        self.est = est

    def _get_params(self):
        """return the rule's parameters"""
        return (self.old_unm, self.est)

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        age_at_death = get_age_at_death(self.obj, self.est)
        n_spouses = len(self.obj.get_family_handle_list())
        return age_at_death / 365 > self.old_unm and n_spouses == 0

    def get_message(self):
        """return the rule's error message"""
        return _("Old and unmarried")


class TooManyChildren(PersonRule):
    """test if a person had 'too many' children"""

    ID = 12
    SEVERITY = Rule.WARNING

    def __init__(self, db, obj, mx_child_dad, mx_child_mom):
        """initialize the rule"""
        PersonRule.__init__(self, db, obj)
        self.mx_child_dad = mx_child_dad
        self.mx_child_mom = mx_child_mom

    def _get_params(self):
        """return the rule's parameters"""
        return (self.mx_child_dad, self.mx_child_mom)

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        n_child = get_n_children(self.db, self.obj)

        if self.obj.get_gender == Person.MALE and n_child > self.mx_child_dad:
            return True

        if self.obj.get_gender == Person.FEMALE and n_child > self.mx_child_mom:
            return True

        return False

    def get_message(self):
        """return the rule's error message"""
        return _("Too many children")


class SameSexFamily(FamilyRule):
    """test if a family's parents are both male or both female"""

    ID = 13
    SEVERITY = Rule.WARNING

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        mother = get_mother(self.db, self.obj)
        father = get_father(self.db, self.obj)
        same_sex = mother and father and (mother.get_gender() == father.get_gender())
        unknown_sex = mother and (mother.get_gender() == Person.UNKNOWN)
        return same_sex and not unknown_sex

    def get_message(self):
        """return the rule's error message"""
        return _("Same sex marriage")


class FemaleHusband(FamilyRule):
    """test if a family's 'husband' is female"""

    ID = 14
    SEVERITY = Rule.WARNING

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        father = get_father(self.db, self.obj)
        return father and (father.get_gender() == Person.FEMALE)

    def get_message(self):
        """return the rule's error message"""
        return _("Female husband")


class MaleWife(FamilyRule):
    """test if a family's 'wife' is male"""

    ID = 15
    SEVERITY = Rule.WARNING

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        mother = get_mother(self.db, self.obj)
        return mother and (mother.get_gender() == Person.MALE)

    def get_message(self):
        """return the rule's error message"""
        return _("Male wife")


class SameSurnameFamily(FamilyRule):
    """test if a family's parents were born with the same surname"""

    ID = 16
    SEVERITY = Rule.WARNING

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        mother = get_mother(self.db, self.obj)
        father = get_father(self.db, self.obj)
        _broken = False

        # Make sure both mother and father exist.
        if mother and father:
            mname = mother.get_surname()
            fname = father.get_surname()
            # Only compare birth names (not married names).
            if (
                mother.get_name_type() == NameType.BIRTH
                and father.get_name_type() == NameType.BIRTH
            ):
                # Empty names don't count.
                if len(mname) != 0 and len(fname) != 0:
                    # Finally, check if the names are the same.
                    if mname == fname:
                        _broken = True

        return _broken

    def get_message(self):
        """return the rule's error message"""
        return _("Husband and wife with the same surname")


class LargeAgeGapFamily(FamilyRule):
    """test if a family's parents were born far apart"""

    ID = 17
    SEVERITY = Rule.WARNING

    def __init__(self, db, obj, hw_diff, est):
        """initialize the rule"""
        FamilyRule.__init__(self, db, obj)
        self.hw_diff = hw_diff
        self.est = est

    def _get_params(self):
        """return the rule's parameters"""
        return (self.hw_diff, self.est)

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        mother = get_mother(self.db, self.obj)
        father = get_father(self.db, self.obj)
        mother_birth_date = mother.get_birth_date(self.est)
        father_birth_date = father.get_birth_date(self.est)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0
        large_diff = abs(father_birth_date - mother_birth_date) / 365 > self.hw_diff
        return mother_birth_date_ok and father_birth_date_ok and large_diff

    def get_message(self):
        """return the rule's error message"""
        return _("Large age difference between spouses")


class MarriageBeforeBirth(FamilyRule):
    """test if each family's parent was born before the marriage"""

    ID = 18
    SEVERITY = Rule.ERROR

    def __init__(self, db, obj, est):
        """initialize the rule"""
        FamilyRule.__init__(self, db, obj)
        self.est = est

    def _get_params(self):
        """return the rule's parameters"""
        return (self.est,)

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        marr_date = self.obj.get_marriage_date()
        marr_date_ok = marr_date > 0

        mother = get_mother(self.db, self.obj)
        father = get_father(self.db, self.obj)
        mother_birth_date = mother.get_birth_date(self.est)
        father_birth_date = father.get_birth_date(self.est)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0

        father_broken = (
            father_birth_date_ok and marr_date_ok and (father_birth_date > marr_date)
        )
        mother_broken = (
            mother_birth_date_ok and marr_date_ok and (mother_birth_date > marr_date)
        )

        return father_broken or mother_broken

    def get_message(self):
        """return the rule's error message"""
        return _("Marriage before birth")


class MarriageAfterDeath(FamilyRule):
    """test if each family's parent died before the marriage"""

    ID = 19
    SEVERITY = Rule.ERROR

    def __init__(self, db, obj, est):
        """initialize the rule"""
        FamilyRule.__init__(self, db, obj)
        self.est = est

    def _get_params(self):
        """return the rule's parameters"""
        return (self.est,)

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        marr_date = self.obj.get_marriage_date()
        marr_date_ok = marr_date > 0

        mother = get_mother(self.db, self.obj)
        father = get_father(self.db, self.obj)
        mother_death_date = mother.get_death_date(self.est)
        father_death_date = father.get_death_date(self.est)
        mother_death_date_ok = mother_death_date > 0
        father_death_date_ok = father_death_date > 0

        father_broken = (
            father_death_date_ok and marr_date_ok and (father_death_date < marr_date)
        )
        mother_broken = (
            mother_death_date_ok and marr_date_ok and (mother_death_date < marr_date)
        )

        return father_broken or mother_broken

    def get_message(self):
        """return the rule's error message"""
        return _("Marriage after death")


class EarlyMarriage(FamilyRule):
    """test if each family's parent was 'too young' at the marriage"""

    ID = 20
    SEVERITY = Rule.WARNING

    def __init__(self, db, obj, yng_mar, est):
        """initialize the rule"""
        FamilyRule.__init__(self, db, obj)
        self.yng_mar = yng_mar
        self.est = est

    def _get_params(self):
        """return the rule's parameters"""
        return (
            self.yng_mar,
            self.est,
        )

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        marr_date = self.obj.get_marriage_date()
        marr_date_ok = marr_date > 0

        mother = get_mother(self.db, self.obj)
        father = get_father(self.db, self.obj)
        mother_birth_date = mother.get_birth_date(self.est)
        father_birth_date = father.get_birth_date(self.est)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0

        father_broken = (
            father_birth_date_ok
            and marr_date_ok
            and father_birth_date < marr_date
            and ((marr_date - father_birth_date) / 365 < self.yng_mar)
        )
        mother_broken = (
            mother_birth_date_ok
            and marr_date_ok
            and mother_birth_date < marr_date
            and ((marr_date - mother_birth_date) / 365 < self.yng_mar)
        )

        return father_broken or mother_broken

    def get_message(self):
        """return the rule's error message"""
        return _("Early marriage")


class LateMarriage(FamilyRule):
    """test if each family's parent was 'too old' at the marriage"""

    ID = 21
    SEVERITY = Rule.WARNING

    def __init__(self, db, obj, old_mar, est):
        """initialize the rule"""
        FamilyRule.__init__(self, db, obj)
        self.old_mar = old_mar
        self.est = est

    def _get_params(self):
        """return the rule's parameters"""
        return (self.old_mar, self.est)

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        marr_date = self.obj.get_marriage_date()
        marr_date_ok = marr_date > 0

        mother = get_mother(self.db, self.obj)
        father = get_father(self.db, self.obj)
        mother_birth_date = mother.get_birth_date(self.est)
        father_birth_date = father.get_birth_date(self.est)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0

        father_broken = (
            father_birth_date_ok
            and marr_date_ok
            and ((marr_date - father_birth_date) / 365 > self.old_mar)
        )
        mother_broken = (
            mother_birth_date_ok
            and marr_date_ok
            and ((marr_date - mother_birth_date) / 365 > self.old_mar)
        )

        return father_broken or mother_broken

    def get_message(self):
        """return the rule's error message"""
        return _("Late marriage")


class OldParent(FamilyRule):
    """test if each family's parent was 'too old' at a child's birth"""

    ID = 22
    SEVERITY = Rule.WARNING

    def __init__(self, db, obj, old_mom, old_dad, est):
        """initialize the rule"""
        FamilyRule.__init__(self, db, obj)
        self.old_mom = old_mom
        self.old_dad = old_dad
        self.est = est

    def _get_params(self):
        """return the rule's parameters"""
        return (self.old_mom, self.old_dad, self.est)

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        mother = get_mother(self.db, self.obj)
        father = get_father(self.db, self.obj)
        mother_birth_date = mother.get_birth_date(self.est)
        father_birth_date = father.get_birth_date(self.est)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0

        for child_ref in self.obj.get_child_ref_list():
            child = find_person(self.db, child_ref.ref)
            child_birth_date = child.get_birth_date(self.est)
            child_birth_date_ok = child_birth_date > 0
            if not child_birth_date_ok:
                continue
            father_broken = father_birth_date_ok and (
                (child_birth_date - father_birth_date) / 365 > self.old_dad
            )
            if father_broken:
                self.get_message = self.father_message
                return True

            mother_broken = mother_birth_date_ok and (
                (child_birth_date - mother_birth_date) / 365 > self.old_mom
            )
            if mother_broken:
                self.get_message = self.mother_message
                return True
        return False

    def father_message(self):
        """return the rule's error message"""
        return _("Old father")

    def mother_message(self):
        """return the rule's error message"""
        return _("Old mother")


class YoungParent(FamilyRule):
    """test if each family's parent was 'too young' at a child's birth"""

    ID = 23
    SEVERITY = Rule.WARNING

    def __init__(self, db, obj, yng_mom, yng_dad, est):
        """initialize the rule"""
        FamilyRule.__init__(self, db, obj)
        self.yng_dad = yng_dad
        self.yng_mom = yng_mom
        self.est = est

    def _get_params(self):
        """return the rule's parameters"""
        return (self.yng_mom, self.yng_dad, self.est)

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        mother = get_mother(self.db, self.obj)
        father = get_father(self.db, self.obj)
        mother_birth_date = mother.get_birth_date(self.est)
        father_birth_date = father.get_birth_date(self.est)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0

        for child_ref in self.obj.get_child_ref_list():
            child = find_person(self.db, child_ref.ref)
            child_birth_date = child.get_birth_date(self.est)
            child_birth_date_ok = child_birth_date > 0
            if not child_birth_date_ok:
                continue
            father_broken = father_birth_date_ok and (
                (child_birth_date - father_birth_date) / 365 < self.yng_dad
            )
            if father_broken:
                self.get_message = self.father_message
                return True

            mother_broken = mother_birth_date_ok and (
                (child_birth_date - mother_birth_date) / 365 < self.yng_mom
            )
            if mother_broken:
                self.get_message = self.mother_message
                return True
        return False

    def father_message(self):
        """return the rule's error message"""
        return _("Young father")

    def mother_message(self):
        """return the rule's error message"""
        return _("Young mother")


class UnbornParent(FamilyRule):
    """test if each family's parent was not yet born at a child's birth"""

    ID = 24
    SEVERITY = Rule.ERROR

    def __init__(self, db, obj, est):
        """initialize the rule"""
        FamilyRule.__init__(self, db, obj)
        self.est = est

    def _get_params(self):
        """return the rule's parameters"""
        return (self.est,)

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        mother = get_mother(self.db, self.obj)
        father = get_father(self.db, self.obj)
        mother_birth_date = mother.get_birth_date(self.est)
        father_birth_date = father.get_birth_date(self.est)
        mother_birth_date_ok = mother_birth_date > 0
        father_birth_date_ok = father_birth_date > 0

        for child_ref in self.obj.get_child_ref_list():
            child = find_person(self.db, child_ref.ref)
            child_birth_date = child.get_birth_date(self.est)
            child_birth_date_ok = child_birth_date > 0
            if not child_birth_date_ok:
                continue
            father_broken = father_birth_date_ok and (
                father_birth_date > child_birth_date
            )
            if father_broken:
                self.get_message = self.father_message
                return True

            mother_broken = mother_birth_date_ok and (
                mother_birth_date > child_birth_date
            )
            if mother_broken:
                self.get_message = self.mother_message
                return True
        return False

    def father_message(self):
        """return the rule's error message"""
        return _("Unborn father")

    def mother_message(self):
        """return the rule's error message"""
        return _("Unborn mother")


class DeadParent(FamilyRule):
    """test if each family's parent was dead at a child's birth"""

    ID = 25
    SEVERITY = Rule.ERROR

    def __init__(self, db, obj, est):
        """initialize the rule"""
        FamilyRule.__init__(self, db, obj)
        self.est = est

    def _get_params(self):
        """return the rule's parameters"""
        return (self.est,)

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        mother = get_mother(self.db, self.obj)
        father = get_father(self.db, self.obj)
        mother_death_date = mother.get_death_date(self.est)
        father_death_date = father.get_death_date(self.est)
        mother_death_date_ok = mother_death_date > 0
        father_death_date_ok = father_death_date > 0

        for child_ref in self.obj.get_child_ref_list():
            child = find_person(self.db, child_ref.ref)
            child_birth_date = child.get_birth_date(self.est)
            child_birth_date_ok = child_birth_date > 0
            if not child_birth_date_ok:
                continue

            has_birth_rel_to_mother = child_ref.mrel == ChildRefType.BIRTH
            has_birth_rel_to_father = child_ref.frel == ChildRefType.BIRTH

            father_broken = (
                has_birth_rel_to_father
                and father_death_date_ok
                and ((father_death_date + 294) < child_birth_date)
            )
            if father_broken:
                self.get_message = self.father_message
                return True

            mother_broken = (
                has_birth_rel_to_mother
                and mother_death_date_ok
                and (mother_death_date < child_birth_date)
            )
            if mother_broken:
                self.get_message = self.mother_message
                return True
        return False

    def father_message(self):
        """return the rule's error message"""
        return _("Dead father")

    def mother_message(self):
        """return the rule's error message"""
        return _("Dead mother")


class LargeChildrenSpan(FamilyRule):
    """test if a family's first and last children were born far apart"""

    ID = 26
    SEVERITY = Rule.WARNING

    def __init__(self, db, obj, cb_span, est):
        """initialize the rule"""
        FamilyRule.__init__(self, db, obj)
        self.cbs = cb_span
        self.est = est

    def _get_params(self):
        """return the rule's parameters"""
        return (self.cbs, self.est)

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        child_birh_dates = get_child_birth_dates(self.db, self.obj, self.est)
        child_birh_dates.sort()

        return child_birh_dates and (
            (child_birh_dates[-1] - child_birh_dates[0]) / 365 > self.cbs
        )

    def get_message(self):
        """return the rule's error message"""
        return _("Large year span for all children")


class LargeChildrenAgeDiff(FamilyRule):
    """test if any of a family's children were born far apart"""

    ID = 27
    SEVERITY = Rule.WARNING

    def __init__(self, db, obj, c_space, est):
        """initialize the rule"""
        FamilyRule.__init__(self, db, obj)
        self.c_space = c_space
        self.est = est

    def _get_params(self):
        """return the rule's parameters"""
        return (self.c_space, self.est)

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        child_birh_dates = get_child_birth_dates(self.db, self.obj, self.est)
        child_birh_dates_diff = [
            child_birh_dates[i + 1] - child_birh_dates[i]
            for i in range(len(child_birh_dates) - 1)
        ]

        return child_birh_dates_diff and max(child_birh_dates_diff) / 365 > self.c_space

    def get_message(self):
        """return the rule's error message"""
        return _("Large age differences between children")


class Disconnected(PersonRule):
    """test if a person has no children and no parents"""

    ID = 28
    SEVERITY = Rule.WARNING

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        return (
            len(self.obj.get_parent_family_handle_list())
            + len(self.obj.get_family_handle_list())
            == 0
        )

    def get_message(self):
        """return the rule's error message"""
        return _("Disconnected individual")


class InvalidBirthDate(PersonRule):
    """test if a person has an 'invalid' birth date"""

    ID = 29
    SEVERITY = Rule.ERROR

    def __init__(self, db, person, invdate):
        """initialize the rule"""
        PersonRule.__init__(self, db, person)
        self._invdate = invdate

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        if not self._invdate:  # should we check?
            return False
        # if so, let's get the birth date
        return self.obj.is_birth_date_invalid()

    def get_message(self):
        """return the rule's error message"""
        return _("Invalid birth date")


class InvalidDeathDate(PersonRule):
    """test if a person has an 'invalid' death date"""

    ID = 30
    SEVERITY = Rule.ERROR

    def __init__(self, db, person, invdate):
        """initialize the rule"""
        PersonRule.__init__(self, db, person)
        self._invdate = invdate

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        if not self._invdate:  # should we check?
            return False
        # if so, let's get the death date
        return self.obj.is_death_date_invalid()

    def get_message(self):
        """return the rule's error message"""
        return _("Invalid death date")


class MarriedRelation(FamilyRule):
    """test if a family has a marriage date but is not marked 'married'"""

    ID = 31
    SEVERITY = Rule.WARNING

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        marr_date = self.obj.get_marriage_date()
        marr_date_ok = marr_date > 0
        married = self.obj.get_relationship() == FamilyRelType.MARRIED
        if not married and marr_date_ok:
            return self.get_message
        return False

    def get_message(self):
        """return the rule's error message"""
        return _("Marriage date but not married")


class OldAgeButNoDeath(PersonRule):
    """test if a person is 'too old' but is not shown as dead"""

    ID = 32
    SEVERITY = Rule.WARNING

    def __init__(self, db, person, old_age, est):
        """initialize the rule"""
        PersonRule.__init__(self, db, person)
        self.old_age = old_age
        self.est = est

    def _get_params(self):
        """return the rule's parameters"""
        return (self.old_age, self.est)

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        birth_date = self.obj.get_birth_date(self.est)
        dead = self.obj.get_death()
        death_date = self.obj.get_death_date(True)  # or burial date
        if dead or death_date or not birth_date:
            return 0
        age = (_today - birth_date) / 365
        return age > self.old_age

    def get_message(self):
        """return the rule's error message"""
        return _("Old age but no death")


class BirthEqualsDeath(PersonRule):
    """test if a person's birth date is the same as their death date"""

    ID = 33
    SEVERITY = Rule.WARNING

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        birth_date = self.obj.get_birth_date()
        death_date = self.obj.get_death_date()
        birth_ok = birth_date > 0 if birth_date is not None else False
        death_ok = death_date > 0 if death_date is not None else False
        return death_ok and birth_ok and birth_date == death_date

    def get_message(self):
        """return the rule's error message"""
        return _("Birth date equals death date")


class BirthEqualsMarriage(PersonRule):
    """test if a person's birth date is the same as their marriage date"""

    ID = 34
    SEVERITY = Rule.ERROR

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        birth_date = self.obj.get_birth_date()
        birth_ok = birth_date > 0 if birth_date is not None else False
        for fhandle in self.obj.get_family_handle_list():
            family = find_family(self.db, fhandle)
            marr_date = family.get_marriage_date()
            marr_ok = marr_date > 0 if marr_date is not None else False
            return marr_ok and birth_ok and birth_date == marr_date

    def get_message(self):
        """return the rule's error message"""
        return _("Birth date equals marriage date")


class DeathEqualsMarriage(PersonRule):
    """test if a person's death date is the same as their marriage date"""

    ID = 35
    SEVERITY = Rule.WARNING  # it's possible

    def broken(self):
        """return boolean indicating whether this rule is violated"""
        death_date = self.obj.get_death_date()
        death_ok = death_date > 0 if death_date is not None else False
        for fhandle in self.obj.get_family_handle_list():
            family = find_family(self.db, fhandle)
            marr_date = family.get_marriage_date()
            marr_ok = marr_date > 0 if marr_date is not None else False
            return marr_ok and death_ok and death_date == marr_date

    def get_message(self):
        """return the rule's error message"""
        return _("Death date equals marriage date")


class BaptTooLate(PersonRule):
    """test if a person's baptism date is too late considering family tradition"""

    ID = 36
    SEVERITY = Rule.WARNING

    def broken(self):
        parents = self.obj.get_parent_family_handle_list()
        if len(parents) != 1:
            # only check if the person has exactly one parent family
            return False

        family = find_family(self.db, parents[0])
        if not family:
            # family not found?
            return False

        children = family.get_child_ref_list()
        if len(children) <= 1:
            # only one child? nothing to compare with...
            return False

        birth_date = self.obj.get_birth_date()
        bapt_date = self.obj.get_bapt_date()
        birth_ok = birth_date > 0 if birth_date is not None else False
        bapt_ok = bapt_date > 0 if bapt_date is not None else False
        if not birth_ok or not bapt_ok or bapt_date < birth_date:
            # return on invalid or incomplete data of the test subject
            return False
        birth_bapt_distance = bapt_date - birth_date

        child_birth_bapt_distances = []
        for childref in children:
            if int(childref.get_mother_relation()) == ChildRefType.BIRTH:
                child = find_person(self.db, childref.ref)
                if self.obj.get_gramps_id() == child.get_gramps_id():
                    continue
                birth_date = child.get_birth_date()
                bapt_date = child.get_bapt_date()
                birth_ok = birth_date > 0 if birth_date is not None else False
                bapt_ok = bapt_date > 0 if bapt_date is not None else False
                if birth_ok and bapt_ok and bapt_date >= birth_date:
                    # only collect valid and complete data
                    child_birth_bapt_distances.append(bapt_date - birth_date)

        if len(child_birth_bapt_distances) == 0:
            # only continue if we have collected some distances
            return False

        median_birth_bapt_distance = statistics.median(child_birth_bapt_distances)

        if birth_bapt_distance > median_birth_bapt_distance + 120:
            return True

        return False

    def get_message(self):
        """return the rule's error message"""
        return _("Baptism too late according to family tradition")


class BuryTooLate(PersonRule):
    """test if a person's burial date is too late"""

    ID = 37
    SEVERITY = Rule.WARNING

    def broken(self):
        death_date = self.obj.get_death_date()
        bury_date = self.obj.get_bury_date()
        death_ok = death_date > 0 if death_date is not None else False
        bury_ok = bury_date > 0 if bury_date is not None else False
        if not death_ok or not bury_ok or bury_date < death_date:
            return False

        death_bury_distance = bury_date - death_date
        if death_bury_distance > 14:
            return True

        return False

    def get_message(self):
        """return the rule's error message"""
        return _("Burial too late")


class ChildrenOrderIncorrect(FamilyRule):
    """test if children are ordered incorrectly within a family"""

    ID = 38
    SEVERITY = Rule.ERROR

    def __init__(self, db, obj, est):
        """initialize the rule"""
        FamilyRule.__init__(self, db, obj)
        self.est = est

    def _get_params(self):
        """return the rule's parameters"""
        return (self.est,)

    def broken(self):
        children = self.obj.get_child_ref_list()
        if len(children) <= 1:
            # only one child? nothing to do...
            return False

        prev_birth_date = 0
        for childref in children:
            if int(childref.get_mother_relation()) == ChildRefType.BIRTH:
                child = find_person(self.db, childref.ref)
                birth_date = child.get_birth_date(self.est)
                birth_ok = birth_date > 0 if birth_date is not None else False
                if birth_ok and birth_date < prev_birth_date:
                    return True
                prev_birth_date = birth_date

        return False

    def get_message(self):
        return _("Children are not in chronological order")


class FamilyOrderIncorrect(PersonRule):
    """test if Families of a person ordered incorrectly"""

    ID = 39
    SEVERITY = Rule.WARNING

    def __init__(self, db, obj, est):
        """initialize the rule"""
        PersonRule.__init__(self, db, obj)
        self.est = est

    def _get_params(self):
        """return the rule's parameters"""
        return (self.est,)

    def broken(self):
        families = self.obj.get_family_handle_list()
        if len(families) < 2:
            # only check if the person has more than one families
            return False

        prev_compare_date = 0
        for fhandle in families:
            family = find_family(self.db, fhandle)
            if not family:
                # family not found?
                continue

            compare_date = 0
            # first try with marriage date for comparison
            marr_date = family.get_marriage_date()
            marr_ok = marr_date > 0 if marr_date is not None else False
            if marr_ok:
                compare_date = marr_date
            else:
                # if there is no, take the divorce date
                div_date = family.get_divorce_date()
                div_ok = div_date > 0 if div_date is not None else False
                if div_ok:
                    compare_date = div_date
                else:
                    # if there is no, check for the birth date of the oldest child
                    for childref in family.get_child_ref_list():
                        if int(childref.get_mother_relation()) == ChildRefType.BIRTH:
                            child = find_person(self.db, childref.ref)
                            birth_date = child.get_birth_date(self.est)
                            birth_ok = (
                                birth_date > 0 if birth_date is not None else False
                            )
                            if (
                                birth_ok
                                and birth_date < compare_date
                                or compare_date == 0
                            ):
                                compare_date = birth_date
            if compare_date != 0 and compare_date < prev_compare_date:
                return True
            prev_compare_date = compare_date
        return False

    def get_message(self):
        return _("Families are not in chronological order")


class FamilyHasEventsOfTypeUnknown(FamilyRule):
    """test if the family has events with role Unknown"""

    ID = 40
    SEVERITY = Rule.ERROR

    def broken(self):
        return self.obj.is_events_of_type_unknown()

    def get_message(self):
        return _("Family has events with role Unknown")


class PersonHasEventsOfTypeUnknown(PersonRule):
    """test if the Person has events with role Unknown"""

    ID = 41
    SEVERITY = Rule.ERROR

    def broken(self):
        return self.obj.is_events_of_type_unknown()

    def get_message(self):
        return _("Person has events with role Unknown")


class FamilyHasEventsInWrongOrder(FamilyRule):
    """test if the family has events in wrong order"""

    ID = 42
    SEVERITY = Rule.ERROR

    def broken(self):
        return self.obj.is_events_in_wrong_order()

    def get_message(self):
        return _("Family events are not in chronological order")


class PersonHasEventsInWrongOrder(PersonRule):
    """test if the person has events in wrong order"""

    ID = 43
    SEVERITY = Rule.ERROR

    def broken(self):
        return self.obj.is_events_in_wrong_order()

    def get_message(self):
        return _("Person events are not in chronological order")
