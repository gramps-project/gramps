#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Brian Caudill
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

"""
Tests for the "show age" option of the ancestor and descendant tree reports.

A small family tree is built in an in-memory database and the text that both
tree reports put into their boxes is generated and checked.  This covers the
ages at death and the marriage durations shown by the reports without needing
a graphical backend.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import os
import re
import shutil
import tempfile
import unittest

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn
from gramps.gen.db.utils import make_database
from gramps.gen.display.name import displayer as _nd
from gramps.gen.lib import (
    ChildRef,
    Date,
    Event,
    EventRef,
    EventType,
    Family,
    Name,
    Person,
    Surname,
)
from gramps.gen.types import FamilyHandle, PersonHandle

from gramps.plugins.drawreport import ancestortree, descendtree

# -------------------------------------------------------------------------
#
# The test family tree
#
# -------------------------------------------------------------------------
# Oldest generation - married until death.
OLD_MAN = ("I001", "George", "Olden", Person.MALE, 1900, 1975)
OLD_WOMAN = ("I002", "Alice", "Young", Person.FEMALE, 1903, 1980)

# Middle generation - the man marries, divorces and remarries.
MID_MAN = ("I003", "Bernard", "Olden", Person.MALE, 1928, 2000)
MID_WIFE_1 = ("I004", "Claire", "New", Person.FEMALE, 1930, 2010)
MID_WIFE_2 = ("I005", "Dana", "Reid", Person.FEMALE, 1935, 2015)
# The middle generation woman remarries as well.
MID_HUSBAND_2 = ("I006", "Ernest", "Other", Person.MALE, 1925, 1990)

# Youngest generation - married with two children, still alive.
YOUNG_WOMAN = ("I008", "Ellen", "Olden", Person.FEMALE, 1972, None)
YOUNG_MAN = ("I007", "Frank", "Smith", Person.MALE, 1970, None)
CHILD_1 = ("I009", "Peter", "Smith", Person.MALE, 1996, None)
CHILD_2 = ("I010", "Lucy", "Smith", Person.FEMALE, 1999, None)

# A child of the middle generation who never married.
MID_CHILD = ("I012", "Nora", "Olden", Person.FEMALE, 1975, None)

# A person without any birth or death information.
UNKNOWN = ("I011", "Sam", "NoDate", Person.MALE, None, None)

PEOPLE = (
    OLD_MAN,
    OLD_WOMAN,
    MID_MAN,
    MID_WIFE_1,
    MID_WIFE_2,
    MID_HUSBAND_2,
    YOUNG_MAN,
    YOUNG_WOMAN,
    CHILD_1,
    CHILD_2,
    MID_CHILD,
    UNKNOWN,
)


def build_tree() -> tuple[object, dict[str, PersonHandle]]:
    """
    Build the test family tree in an in-memory database.

    :returns: The database and a mapping of Gramps IDs to handles.
    """
    db = make_database("sqlite")
    db.load(":memory:")
    # The application normally sets this when a tree is opened.
    db.db_name = "displayage"
    handles: dict[str, PersonHandle] = {}

    def make_event(event_type: EventType, year: int) -> Event:
        event = Event()
        event.set_type(event_type)
        date = Date()
        date.set_yr_mon_day(year, 0, 0)
        event.set_date_object(date)
        return event

    def add_person(
        spec: tuple[str, str, str, int, int | None, int | None],
    ) -> PersonHandle:
        """
        Add one person described by a (gid, first, surname, gender, b, d) tuple.
        """
        gid, first, surname, gender, birth, death = spec
        person = Person()
        person.set_gramps_id(gid)
        person.set_gender(gender)
        name = Name()
        name.set_first_name(first)
        surname_obj = Surname()
        surname_obj.set_surname(surname)
        name.add_surname(surname_obj)
        person.set_primary_name(name)
        with DbTxn("test", db) as trans:
            refs: dict[str, EventRef] = {}
            for event_type, year in (
                (EventType(EventType.BIRTH), birth),
                (EventType(EventType.DEATH), death),
            ):
                if year is None:
                    continue
                ref = EventRef()
                ref.set_reference_handle(
                    db.add_event(make_event(event_type, year), trans)
                )
                refs[event_type.value] = ref
            if EventType(EventType.BIRTH).value in refs:
                person.set_birth_ref(refs[EventType(EventType.BIRTH).value])
            if EventType(EventType.DEATH).value in refs:
                person.set_death_ref(refs[EventType(EventType.DEATH).value])
            handles[gid] = db.add_person(person, trans)
        return handles[gid]

    def add_family(gid, father, mother, children, events) -> None:
        """
        Add one family with the given partners, children and dated events.
        """
        family = Family()
        family.set_gramps_id(gid)
        family.set_father_handle(handles[father])
        family.set_mother_handle(handles[mother])
        with DbTxn("test", db) as trans:
            for event_type, year in events:
                event_ref = EventRef()
                event_ref.set_reference_handle(
                    db.add_event(make_event(event_type, year), trans)
                )
                family.add_event_ref(event_ref)
            for child in children:
                child_ref = ChildRef()
                child_ref.set_reference_handle(handles[child])
                family.add_child_ref(child_ref)
            handles[gid] = db.add_family(family, trans)
        # The partners and the children must point back at their family,
        # otherwise the reports cannot find the marriage information.
        with DbTxn("test", db) as trans:
            for partner in (father, mother):
                person = db.get_person_from_handle(handles[partner])
                person.add_family_handle(handles[gid])
                db.commit_person(person, trans)
            for child in children:
                person = db.get_person_from_handle(handles[child])
                person.add_parent_family_handle(handles[gid])
                db.commit_person(person, trans)

    for spec in PEOPLE:
        add_person(spec)

    # Oldest generation, married 1925 until his death in 1975.
    add_family("F001", "I001", "I002", ["I003"], [(EventType.MARRIAGE, 1925)])
    # Middle generation, first marriage 1950, divorced 1965, no children.
    add_family(
        "F002",
        "I003",
        "I004",
        [],
        [(EventType.MARRIAGE, 1950), (EventType.DIVORCE, 1965)],
    )
    # Middle generation, second marriage 1970, ended by his death in 2000.
    add_family("F003", "I003", "I005", ["I008", "I012"], [(EventType.MARRIAGE, 1970)])
    # The middle generation woman remarried in 1968, ended by his death.
    add_family("F004", "I006", "I004", [], [(EventType.MARRIAGE, 1968)])
    # Youngest generation, married 1995 and still married, two children.
    add_family("F005", "I007", "I008", ["I009", "I010"], [(EventType.MARRIAGE, 1995)])

    return db, handles


# -------------------------------------------------------------------------
#
# Report text helpers
#
# -------------------------------------------------------------------------
def joined(lines: list[str]) -> str:
    """
    Return the text of a report box as a single searchable string.
    """
    return " ".join(lines)


def descendant_person_box(db, handle: PersonHandle, family=None) -> str:
    """
    Return the text of a descendant person box of the descendant report.
    """
    gui = descendtree.GuiConnect()
    calc = gui.calc_lines(db)
    lines = calc.calc_lines(handle, family, gui.get_val("descend_disp"))
    items = gui.calc_items(db, calc)
    items._clean_tuple_artifacts(lines)
    items._add_age_at_death(lines, handle, family)
    return joined(lines)


def descendant_marriage_box(db, person: PersonHandle, family: FamilyHandle) -> str:
    """
    Return the text of a marriage box of the descendant report.
    """
    gui = descendtree.GuiConnect()
    calc = gui.calc_lines(db)
    lines = calc.calc_lines(person, family, [gui.get_val("marr_disp")])
    items = gui.calc_items(db, calc)
    items._clean_tuple_artifacts(lines)
    items._add_marriage_span(lines, person, family)
    return joined(lines)


def ancestor_person_box(db, handle: PersonHandle, family=None) -> str:
    """
    Return the text of a person box of the ancestor report.
    """
    return joined(ancestortree.CalcItems(db).calc_person((1, 1), handle, family))


def ancestor_marriage_box(db, handle: PersonHandle, family) -> str:
    """
    Return the text of a marriage box of the ancestor report.
    """
    return joined(ancestortree.CalcItems(db).calc_marriage(handle, family))


# -------------------------------------------------------------------------
#
# Full report rendering
#
# -------------------------------------------------------------------------
def render_svg(options_class, report_class, report_id, subject, directory, name) -> str:
    """
    Run a whole tree report and write it out as an SVG file.

    The SVG backend is used because it is pure Python, so the reports can be
    rendered on a machine without Cairo, GTK or Pango installed.  The PDF
    backend (cairodoc) needs all of those.

    :returns: The path of the generated file.
    """
    from gramps.gen.plug.docgen import StyleSheet
    from gramps.gen.utils.grampslocale import GrampsLocale
    from gramps.gen.plug.docgen.paperstyle import (
        PAPER_PORTRAIT,
        PaperSize,
        PaperStyle,
    )
    from gramps.gen.proxy import CacheProxyDb
    from gramps.gen.user import User
    from gramps.plugins.docgen.svgdrawdoc import SvgDrawDoc

    db, _handles = build_tree()
    options = options_class(report_id, db)
    options.load_previous_values()
    styles = StyleSheet()
    options.make_default_style(styles)
    options.menu.get_option_by_name("pid").set_value(subject)
    options.menu.get_option_by_name("show_age").set_value(True)
    options.menu.get_option_by_name("maxgen").set_value(5)

    output = os.path.join(directory, name)
    doc = SvgDrawDoc(styles, "svg")
    doc.paper = PaperStyle(PaperSize("Letter", 27.94, 21.59), PAPER_PORTRAIT)
    doc.open(output)
    options.set_document(doc)
    options.set_output(output)

    report = report_class.__new__(report_class)
    report.database = CacheProxyDb(db)
    report.doc = doc
    report.options = options
    report._user = User()
    report.standalone = True
    report.set_locale(GrampsLocale.DEFAULT_TRANSLATION_STR)
    report._nd = report._name_display
    report.begin_report()
    report.write_report()
    doc.close()
    return output + ".svg"


def svg_text(path: str) -> list[str]:
    """
    Return the visible strings of a generated SVG file.
    """
    with open(path, encoding="utf-8") as svg_file:
        content = svg_file.read()
    return re.findall(r">([^<>]+)</(?:text|tspan)>", content)


# -------------------------------------------------------------------------
#
# TreeTestBase
#
# -------------------------------------------------------------------------
class TreeTestBase(unittest.TestCase):
    """
    Provide the test tree and the configured report options.
    """

    show_age = True

    @classmethod
    def setUpClass(cls):
        """
        Build the test tree and configure both reports.
        """
        cls.db, cls.handles = build_tree()
        cls.grandfather = cls.handles["I001"]
        cls.grandmother = cls.handles["I002"]
        cls.father = cls.handles["I003"]
        cls.second_wife = cls.handles["I005"]
        cls.second_husband = cls.handles["I006"]
        cls.grandchild = cls.handles["I008"]
        cls.grandson = cls.handles["I007"]
        cls.never_married = cls.handles["I012"]
        cls.no_dates = cls.handles["I011"]
        cls.old_family = cls.handles["F001"]
        cls.divorced_family = cls.handles["F002"]
        cls.remarried_family = cls.handles["F003"]
        cls.remarried_family_2 = cls.handles["F004"]
        cls.young_family = cls.handles["F005"]

    def setUp(self):
        """
        Configure both reports with the show age setting of this test.
        """
        descend_options = descendtree.DescendTreeOptions("descend_chart", self.db)
        descend_options.menu.get_option_by_name("show_age").set_value(self.show_age)
        descendtree.GuiConnect().set__opts(
            descend_options.menu, "descend_chart", glocale, _nd
        )

        ancestor_options = ancestortree.AncestorTreeOptions("ancestor_chart", self.db)
        ancestor_options.menu.get_option_by_name("show_age").set_value(self.show_age)
        ancestortree.GUIConnect().set__opts(ancestor_options.menu, glocale, _nd)


# -------------------------------------------------------------------------
#
# DescendantTreeShowAgeTest
#
# -------------------------------------------------------------------------
class DescendantTreeShowAgeTest(TreeTestBase):
    """
    Check the descendant tree boxes with the show age option turned on.
    """

    show_age = True

    def test_descendant_age_at_death(self):
        """
        A dead person gets an age at death added to the death line.
        """
        text = descendant_person_box(self.db, self.grandfather)
        self.assertIn("1900", text)
        self.assertIn("1975", text)
        self.assertIn("(age 75)", text)

    def test_descendant_age_omitted_when_dates_missing(self):
        """
        A person without dates gets no age and no empty age placeholder.
        """
        text = descendant_person_box(self.db, self.no_dates)
        self.assertNotIn("age", text.lower())

    def test_descendant_alive_person_has_no_age(self):
        """
        A living person gets no age at death.
        """
        text = descendant_person_box(self.db, self.grandchild)
        self.assertNotIn("age", text.lower())
        self.assertNotIn("d.", text)

    def test_descendant_marriage_ended_by_death(self):
        """
        A marriage ended by a death shows the number of years married.
        """
        text = descendant_marriage_box(self.db, self.grandfather, self.old_family)
        self.assertIn("1925", text)
        self.assertIn("(50 yrs)", text)

    def test_descendant_marriage_ended_by_divorce(self):
        """
        A marriage ended by a divorce shows the number of years married.
        """
        text = descendant_marriage_box(self.db, self.father, self.divorced_family)
        self.assertIn("1950", text)
        self.assertIn("1965", text)
        self.assertIn("(15 yrs)", text)

    def test_descendant_remarriage_ended_by_death(self):
        """
        The second marriage of the middle generation ends at his death.
        """
        text = descendant_marriage_box(self.db, self.father, self.remarried_family)
        self.assertIn("1970", text)
        self.assertIn("(30 yrs)", text)

    def test_descendant_remarriage_of_the_other_spouse(self):
        """
        The middle generation woman remarried and that marriage also ends.
        """
        text = descendant_marriage_box(
            self.db, self.second_husband, self.remarried_family_2
        )
        self.assertIn("1968", text)
        self.assertIn("(22 yrs)", text)

    def test_descendant_no_span_for_living_marriage(self):
        """
        A marriage with living partners and no divorce shows no duration.
        """
        text = descendant_marriage_box(self.db, self.grandson, self.young_family)
        self.assertIn("1995", text)
        self.assertNotIn("yrs", text)


# -------------------------------------------------------------------------
#
# AncestorTreeShowAgeTest
#
# -------------------------------------------------------------------------
class AncestorTreeShowAgeTest(TreeTestBase):
    """
    Check the ancestor tree boxes with the show age option turned on.
    """

    show_age = True

    def test_ancestor_age_at_death(self):
        """
        The ancestor report also adds the age at death.
        """
        text = ancestor_person_box(self.db, self.grandfather)
        self.assertIn("(age 75)", text)

    def test_ancestor_age_at_death_of_grandmother(self):
        """
        The age at death is calculated for the female ancestors too.
        """
        text = ancestor_person_box(self.db, self.grandmother)
        self.assertIn("(age 77)", text)

    def test_ancestor_marriage_box_shows_duration(self):
        """
        The ancestor marriage box shows the years married.
        """
        text = ancestor_marriage_box(self.db, self.grandfather, self.old_family)
        self.assertIn("1925", text)
        self.assertIn("(50 yrs)", text)

    def test_ancestor_divorced_marriage_box(self):
        """
        The ancestor report shows a marriage ended by divorce.
        """
        text = ancestor_marriage_box(self.db, self.father, self.divorced_family)
        self.assertIn("1950", text)
        self.assertIn("(15 yrs)", text)

    def test_ancestor_never_married_person(self):
        """
        A person who never married gets an age but no marriage duration.
        """
        text = ancestor_person_box(self.db, self.never_married)
        self.assertIn("Nora", text)
        self.assertNotIn("yrs", text)


# -------------------------------------------------------------------------
#
# ShowAgeDisabledTest
#
# -------------------------------------------------------------------------
class ShowAgeDisabledTest(TreeTestBase):
    """
    Check that nothing is added when the show age option is turned off.
    """

    show_age = False

    def test_descendant_age_at_death(self):
        """
        No age is shown when the option is off.
        """
        text = descendant_person_box(self.db, self.grandfather)
        self.assertNotIn("age", text.lower())
        self.assertIn("1975", text)

    def test_descendant_marriage_ended_by_death(self):
        """
        No marriage duration is shown when the option is off.
        """
        text = descendant_marriage_box(self.db, self.grandfather, self.old_family)
        self.assertIn("1925", text)
        self.assertNotIn("yrs", text)

    def test_ancestor_age_at_death(self):
        """
        No age is shown in the ancestor report either.
        """
        text = ancestor_person_box(self.db, self.grandfather)
        self.assertNotIn("age", text.lower())
        self.assertIn("1975", text)

    def test_ancestor_never_married_person(self):
        """
        A person without dates renders only their name.
        """
        text = ancestor_person_box(self.db, self.no_dates)
        self.assertIn("Sam", text)
        self.assertNotIn("age", text.lower())


# -------------------------------------------------------------------------
#
# RenderedReportTest
#
# -------------------------------------------------------------------------
class RenderedReportTest(unittest.TestCase):
    """
    Run both reports in full and check the SVG files they write to disk.
    """

    def setUp(self):
        """
        Create a directory to hold the generated reports.
        """
        self.directory = tempfile.mkdtemp(prefix="gramps_tree_report")
        self.addCleanup(shutil.rmtree, self.directory, True)

    def test_descendant_report_is_written_to_disk(self):
        """
        The descendant report produces a file containing ages and durations.
        """
        path = render_svg(
            descendtree.DescendTreeOptions,
            descendtree.DescendTree,
            "family_descend_chart",
            "F001",
            self.directory,
            "descendant",
        )
        self.assertTrue(os.path.exists(path))
        text = svg_text(path)
        self.assertIn("d. 1975 (age 75)", text)
        self.assertIn("m. 1925  (50 yrs)", text)
        self.assertIn("m. 1950 / v. 1965 (15 yrs)", text)
        self.assertIn("m. 1970  (30 yrs)", text)

    def test_ancestor_report_is_written_to_disk(self):
        """
        The ancestor report produces a file containing ages and durations.
        """
        path = render_svg(
            ancestortree.AncestorTreeOptions,
            ancestortree.AncestorTree,
            "ancestor_chart",
            "I009",
            self.directory,
            "ancestor",
        )
        self.assertTrue(os.path.exists(path))
        text = svg_text(path)
        self.assertIn("d. 1975 (age 75)", text)
        self.assertIn("m. 1925 (50 yrs)", text)
        self.assertIn("m. 1970 (30 yrs)", text)
