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
Unittest for relationship_path.py
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import unittest
from typing import Any, ClassVar

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..db import DbTxn
from ..db.utils import make_database
from ..lib import ChildRef, ChildRefType, Family, FamilyRelType, Person
from ..proxy import PrivateProxyDb
from ..relationship import RelationshipCalculator
from ..relationship_path import (
    FamilyLinkGraph,
    LinkType,
    find_connections,
    label_path,
)
from ..types import PersonHandle

M, F = Person.MALE, Person.FEMALE
P, C, S, SP = LinkType.PARENT, LinkType.CHILD, LinkType.SIBLING, LinkType.SPOUSE


# -------------------------------------------------------------------------
#
# RelationshipPathTest
#
# -------------------------------------------------------------------------
class RelationshipPathTest(unittest.TestCase):
    """
    Test finding and labelling paths between people.

    The tree, seen from "me"::

        gf + gm ............................. grandparents
        father + mother, father + second ..... parents, stepmother
        aunt + uncle, aunt's child cousin
        me + wife, sister + sister_husband, adopted, half (with second)
        wife's parents wife_father + wife_mother, wife_brother + his wife
        wife + ex, their child stepdaughter
        son + son_wife
        private child of wife_brother, stranger
    """

    db: ClassVar[Any]
    people: ClassVar[dict[str, PersonHandle]]
    graph: ClassVar[FamilyLinkGraph]
    calc: ClassVar[RelationshipCalculator]

    @classmethod
    def setUpClass(cls) -> None:
        cls.db = make_database("sqlite")
        cls.db.load(":memory:")
        cls.people = {}
        with DbTxn("Create tree", cls.db) as trans:
            for name, gender in [
                ("gf", M),
                ("gm", F),
                ("father", M),
                ("mother", F),
                ("second", F),
                ("aunt", F),
                ("uncle", M),
                ("cousin", F),
                ("me", M),
                ("sister", F),
                ("sister_husband", M),
                ("adopted", M),
                ("half", M),
                ("wife", F),
                ("ex", M),
                ("stepdaughter", F),
                ("wife_father", M),
                ("wife_mother", F),
                ("wife_brother", M),
                ("wife_brother_wife", F),
                ("son", M),
                ("son_wife", F),
                ("private", F),
                ("stranger", M),
            ]:
                person = Person()
                person.set_gender(gender)
                person.set_privacy(name == "private")
                cls.people[name] = cls.db.add_person(person, trans)
            cls._family(trans, "gf", "gm", ["father", "aunt"])
            cls._family(trans, "father", "mother", ["me", "sister", "adopted"])
            cls._family(trans, "father", "second", ["half"])
            cls._family(trans, "uncle", "aunt", ["cousin"])
            cls._family(trans, "me", "wife", ["son"])
            cls._family(trans, "ex", "wife", ["stepdaughter"])
            cls._family(trans, "sister_husband", "sister", [])
            cls._family(trans, "wife_father", "wife_mother", ["wife", "wife_brother"])
            cls._family(trans, "wife_brother", "wife_brother_wife", ["private"])
            cls._family(trans, "son", "son_wife", [])
        cls.graph = FamilyLinkGraph.from_db(cls.db)
        cls.calc = RelationshipCalculator()

    @classmethod
    def _family(
        cls, trans: DbTxn, father: str, mother: str, children: list[str]
    ) -> None:
        """
        Add a family; "adopted" is an adopted child of both parents.
        """
        family = Family()
        family.set_relationship(FamilyRelType.MARRIED)
        family.set_father_handle(cls.people[father])
        family.set_mother_handle(cls.people[mother])
        for child in children:
            ref = ChildRef()
            ref.set_reference_handle(cls.people[child])
            if child == "adopted":
                ref.set_mother_relation(ChildRefType.ADOPTED)
                ref.set_father_relation(ChildRefType.ADOPTED)
            family.add_child_ref(ref)
        family_handle = cls.db.add_family(family, trans)
        for parent in (father, mother):
            person = cls.db.get_person_from_handle(cls.people[parent])
            person.add_family_handle(family_handle)
            cls.db.commit_person(person, trans)
        for child in children:
            person = cls.db.get_person_from_handle(cls.people[child])
            person.add_parent_family_handle(family_handle)
            cls.db.commit_person(person, trans)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.db.close()

    def _names(self, path: list) -> list[tuple[str, LinkType | None]]:
        """
        Return a path with names instead of handles.
        """
        names = {handle: name for name, handle in self.people.items()}
        return [(names[handle], link) for handle, link in path]

    def _first(self, start: str, end: str, **kwargs) -> list:
        """
        Return the shortest path between two people, with names.
        """
        paths = find_connections(
            self.graph, self.people[start], self.people[end], **kwargs
        )
        self.assertTrue(paths)
        return paths[0]

    def _labels(self, start: str, end: str) -> list[str | None]:
        """
        Return the labels of the shortest path between two people.
        """
        return label_path(self.calc, self.db, self.graph, self._first(start, end))

    def test_graph_links(self) -> None:
        """
        The graph knows each kind of link.
        """
        people = self.people
        self.assertEqual(
            set(self.graph.parents(people["me"])), {people["father"], people["mother"]}
        )
        self.assertEqual(self.graph.children(people["me"]), [people["son"]])
        self.assertEqual(
            self.graph.spouses(people["wife"]), sorted([people["me"], people["ex"]])
        )
        self.assertEqual(
            set(self.graph.siblings(people["me"])),
            {people["sister"], people["adopted"]},
        )
        self.assertEqual(self.graph.gender(people["wife"]), F)
        self.assertIn(people["stranger"], self.graph)
        self.assertEqual(len(self.graph), len(self.people))

    def test_ancestor_chain(self) -> None:
        """
        A chain to a grandparent is labelled step by step.
        """
        path = self._first("me", "gf")
        self.assertEqual(self._names(path), [("me", None), ("father", P), ("gf", P)])
        self.assertEqual(
            label_path(self.calc, self.db, self.graph, path),
            ["", "father", "grandfather"],
        )

    def test_descendant_chain(self) -> None:
        """
        A chain down to a grandchild is labelled.
        """
        self.assertEqual(
            self._labels("gm", "son"), ["", "son", "grandson", "great grandson"]
        )

    def test_cousin_chain(self) -> None:
        """
        A chain through a sibling link agrees with the calculator.
        """
        path = self._first("me", "cousin")
        self.assertEqual(
            self._names(path),
            [("me", None), ("father", P), ("aunt", S), ("cousin", C)],
        )
        labels = label_path(self.calc, self.db, self.graph, path)
        for (handle, _), label in zip(path[1:], labels[1:]):
            self.assertEqual(
                label,
                self.calc.get_one_relationship(
                    self.db,
                    self.db.get_person_from_handle(self.people["me"]),
                    self.db.get_person_from_handle(handle),
                ),
            )

    def test_sibling_types(self) -> None:
        """
        Half and adopted siblings agree with the calculator.
        """
        me_person = self.db.get_person_from_handle(self.people["me"])
        for name in ("sister", "half", "adopted"):
            other = self.db.get_person_from_handle(self.people[name])
            self.assertEqual(
                self._labels("me", name)[-1],
                self.calc.get_one_relationship(self.db, me_person, other),
            )
        self.assertEqual(self._labels("me", "half")[-1], "half-brother")

    def test_non_birth_parent(self) -> None:
        """
        An adoptive parent is not labelled as a birth parent.
        """
        self.assertEqual(self._labels("adopted", "father"), ["", "stepfather"])

    def test_spouse(self) -> None:
        """
        A partner is labelled with the partner type.
        """
        self.assertEqual(self._labels("me", "wife"), ["", "wife"])

    def test_in_laws(self) -> None:
        """
        Relatives of a partner and partners of relatives are in-laws.
        """
        self.assertEqual(
            self._labels("me", "wife_father"), ["", "wife", "father-in-law"]
        )
        self.assertEqual(
            self._labels("me", "wife_brother"), ["", "wife", "brother-in-law"]
        )
        self.assertEqual(
            self._labels("me", "sister_husband"), ["", "sister", "brother-in-law"]
        )
        self.assertEqual(self._labels("me", "son_wife"), ["", "son", "daughter-in-law"])

    def test_step_relatives(self) -> None:
        """
        A partner's child and a parent's partner are step relatives.
        """
        self.assertEqual(
            self._labels("me", "stepdaughter"), ["", "wife", "stepdaughter"]
        )
        self.assertEqual(self._labels("me", "second"), ["", "father", "stepmother"])

    def test_unnamed_relationship(self) -> None:
        """
        A chain through two marriages has no label.
        """
        path = self._first("me", "wife_brother_wife")
        self.assertEqual([link for _handle, link in path], [None, SP, S, SP])
        self.assertIsNone(label_path(self.calc, self.db, self.graph, path)[-1])

    def test_same_person(self) -> None:
        """
        The path from a person to themselves is just that person.
        """
        self.assertEqual(
            find_connections(self.graph, self.people["me"], self.people["me"]),
            [[(self.people["me"], None)]],
        )

    def test_no_connection(self) -> None:
        """
        Unconnected and unknown people have no paths.
        """
        self.assertEqual(
            find_connections(self.graph, self.people["me"], self.people["stranger"]), []
        )
        self.assertEqual(
            find_connections(self.graph, self.people["me"], PersonHandle("missing")), []
        )

    def test_max_depth(self) -> None:
        """
        Paths longer than max_depth are not returned.
        """
        people = self.people
        self.assertEqual(
            find_connections(self.graph, people["me"], people["gf"], max_depth=1), []
        )
        self.assertEqual(
            len(
                find_connections(self.graph, people["me"], people["gf"], max_depth=2)[0]
            ),
            3,
        )

    def test_max_results(self) -> None:
        """
        Several different paths are returned, shortest first.
        """
        paths = find_connections(
            self.graph, self.people["me"], self.people["cousin"], max_results=3
        )
        self.assertEqual(len(paths), 3)
        lengths = [len(path) for path in paths]
        self.assertEqual(lengths, sorted(lengths))
        self.assertEqual(len({tuple(path) for path in paths}), 3)
        for path in paths:
            handles = [handle for handle, _link in path]
            self.assertEqual(len(handles), len(set(handles)))

    def test_blood_links_only(self) -> None:
        """
        Blood relationships leave out relatives by marriage and paths
        through a child's other parent.
        """
        people = self.people
        self.assertEqual(
            find_connections(
                self.graph, people["me"], people["wife_father"], blood_only=True
            ),
            [],
        )
        self.assertTrue(
            find_connections(
                self.graph, people["me"], people["cousin"], blood_only=True
            )
        )

    def test_one_way_links(self) -> None:
        """
        Following only parent links finds ancestors but not descendants.
        """
        people = self.people
        self.assertTrue(
            find_connections(self.graph, people["me"], people["gf"], links={P})
        )
        self.assertEqual(
            find_connections(self.graph, people["gf"], people["me"], links={P}), []
        )

    def test_family_order(self) -> None:
        """
        The results do not depend on the order families were added in.
        """
        people = self.people
        # families and children in database order, and reversed
        families = [
            (family.handle, family.father_handle, family.mother_handle, family)
            for family in self.db.iter_families()
        ]
        graphs = []
        for order in (families, families[::-1]):
            graph = FamilyLinkGraph()
            for person in self.db.iter_people():
                graph.add_person(person.handle, person.get_gender())
            for handle, father, mother, family in order:
                graph.add_family(
                    handle,
                    father,
                    mother,
                    [
                        (
                            ref.ref,
                            ref.get_mother_relation() == ChildRefType.BIRTH,
                            ref.get_father_relation() == ChildRefType.BIRTH,
                        )
                        for ref in family.get_child_ref_list()[::-1]
                    ],
                )
            graphs.append(graph)
        for handle in people.values():
            self.assertEqual(
                list(graphs[0].neighbors(handle)), list(graphs[1].neighbors(handle))
            )
        for start in people.values():
            for end in people.values():
                for blood_only in (False, True):
                    results = [
                        find_connections(
                            graph, start, end, max_results=1, blood_only=blood_only
                        )
                        for graph in graphs
                    ]
                    self.assertEqual(results[0], results[1])

    def test_private_proxy(self) -> None:
        """
        People hidden by a proxy are not in the graph.
        """
        graph = FamilyLinkGraph.from_db(PrivateProxyDb(self.db))
        self.assertNotIn(self.people["private"], graph)
        self.assertEqual(graph.children(self.people["wife_brother"]), [])
        self.assertEqual(
            find_connections(graph, self.people["me"], self.people["private"]), []
        )


if __name__ == "__main__":
    unittest.main()
