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
import random
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
from ..proxy import LivingProxyDb, PrivateProxyDb
from ..relationship import RelationshipCalculator
from ..relationship_path import (
    ALL_LINKS,
    FamilyLinkGraph,
    LinkType,
    find_connections,
    label_path,
)
from ..types import PersonHandle

M, F = Person.MALE, Person.FEMALE


def _full_graph(db: Any, reverse: bool = False) -> FamilyLinkGraph:
    """
    Build a graph of all people and families at once.

    People and families are read one by one, since proxies only clean what
    they return that way: their ``iter_people()`` and ``iter_families()``
    return private child references, for example.

    :param reverse: Add families, and the children of each family, in
                    reverse database order.
    """
    graph = FamilyLinkGraph()
    for handle in db.iter_person_handles():
        graph.add_person(handle, db.get_person_from_handle(handle).get_gender())
    families = [db.get_family_from_handle(h) for h in db.iter_family_handles()]
    for family in families[::-1] if reverse else families:
        refs = family.get_child_ref_list()
        graph.add_family(
            family.handle,
            family.get_father_handle(),
            family.get_mother_handle(),
            [
                (
                    ref.ref,
                    ref.get_mother_relation() == ChildRefType.BIRTH,
                    ref.get_father_relation() == ChildRefType.BIRTH,
                )
                for ref in (refs[::-1] if reverse else refs)
            ],
        )
    return graph


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
        graphs = [_full_graph(self.db), _full_graph(self.db, reverse=True)]
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

    def test_same_as_full_graph(self) -> None:
        """
        A graph read on demand gives the same paths and labels as a graph
        of the whole tree.
        """
        full = _full_graph(self.db)
        for start in self.people.values():
            for end in self.people.values():
                for blood_only in (False, True):
                    graph = FamilyLinkGraph.from_db(self.db)
                    paths = find_connections(graph, start, end, blood_only=blood_only)
                    expected = find_connections(full, start, end, blood_only=blood_only)
                    self.assertEqual(paths, expected)
                    self.assertEqual(
                        [label_path(self.calc, self.db, graph, p) for p in paths],
                        [label_path(self.calc, self.db, full, p) for p in expected],
                    )
        self.assertEqual(len(full), len(self.people))

    def test_reads_on_demand(self) -> None:
        """
        A search reads only the people within reach.
        """
        graph = FamilyLinkGraph.from_db(self.db)
        self.assertEqual(len(graph), 0)
        find_connections(graph, self.people["me"], self.people["father"], max_depth=1)
        self.assertIn(self.people["mother"], graph._gender)
        self.assertNotIn(self.people["stranger"], graph._gender)
        self.assertNotIn(self.people["son_wife"], graph._gender)
        self.assertLess(len(graph), len(self.people))

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

    def test_living_proxy(self) -> None:
        """
        People hidden by a living proxy are not in the graph.
        """
        db = LivingProxyDb(self.db, LivingProxyDb.MODE_EXCLUDE_ALL)
        graph = FamilyLinkGraph.from_db(db)
        self.assertNotIn(self.people["me"], graph)
        self.assertEqual(
            find_connections(graph, self.people["son"], self.people["father"]), []
        )


# -------------------------------------------------------------------------
#
# LargeTreeTest
#
# -------------------------------------------------------------------------
class _CountingDb:
    """
    A database that records which people and families are read from it.
    """

    def __init__(self, db: Any) -> None:
        self.db = db
        self.people: set[str] = set()
        self.families: set[str] = set()

    def get_raw_person_data(self, handle: str) -> Any:
        self.people.add(handle)
        return self.db.get_raw_person_data(handle)

    def get_raw_family_data(self, handle: str) -> Any:
        self.families.add(handle)
        return self.db.get_raw_family_data(handle)


def _generate_tree(db: Any, seed: int) -> None:
    """
    Add a generated tree of a few thousand people.

    Several generations descend from founding couples. People marry into
    other branches and remarry, some children are adopted, and some people
    and child references are private, so the tree has a densely linked
    core. A few unrelated families stand apart from it.
    """
    rng = random.Random(seed)
    genders: list[int] = []
    private: list[bool] = []
    # (father, mother, [(child, birth child, private reference)])
    families: list[tuple[int, int, list[tuple[int, bool, bool]]]] = []

    def new_person(gender: int) -> int:
        genders.append(gender)
        private.append(rng.random() < 0.08)
        return len(genders) - 1

    def add_children(father: int, mother: int, count: int) -> list[int]:
        children = []
        for _ in range(count):
            child = new_person(rng.choice((M, F)))
            children.append((child, rng.random() < 0.95, rng.random() < 0.05))
        families.append((father, mother, children))
        return [child for child, _, _ in children]

    cohort = [new_person(rng.choice((M, F))) for _ in range(60)]
    for _ in range(7):
        rng.shuffle(cohort)
        unmarried = list(cohort)
        next_cohort: list[int] = []
        while unmarried:
            person = unmarried.pop()
            if rng.random() < 0.15:
                continue
            other = F if genders[person] == M else M
            partner = None
            if rng.random() < 0.3:
                # marry into another branch of the tree
                for index, candidate in enumerate(unmarried):
                    if genders[candidate] == other:
                        partner = unmarried.pop(index)
                        break
            for marriage in range(2 if rng.random() < 0.15 else 1):
                if partner is None or marriage:
                    partner = new_person(other)
                father, mother = (
                    (person, partner) if genders[person] == M else (partner, person)
                )
                next_cohort += add_children(
                    father, mother, rng.choice((0, 1, 2, 2, 3, 3, 4, 5))
                )
        cohort = rng.sample(next_cohort, min(len(next_cohort), 700))
    for _ in range(20):
        add_children(new_person(M), new_person(F), rng.randint(0, 3))

    person_objects = []
    for index, gender in enumerate(genders):
        person = Person()
        person.set_handle(f"P{index:05d}")
        person.set_gramps_id(f"I{index:05d}")
        person.set_gender(gender)
        person.set_privacy(private[index])
        person_objects.append(person)
    family_objects = []
    for index, (father, mother, children) in enumerate(families):
        family = Family()
        handle = f"F{index:05d}"
        family.set_handle(handle)
        family.set_gramps_id(f"F{index:05d}")
        family.set_relationship(FamilyRelType.MARRIED)
        family.set_father_handle(person_objects[father].handle)
        family.set_mother_handle(person_objects[mother].handle)
        person_objects[father].add_family_handle(handle)
        person_objects[mother].add_family_handle(handle)
        for child, birth, private_ref in children:
            ref = ChildRef()
            ref.set_reference_handle(person_objects[child].handle)
            if not birth:
                ref.set_mother_relation(ChildRefType.ADOPTED)
                ref.set_father_relation(ChildRefType.ADOPTED)
            ref.set_privacy(private_ref)
            family.add_child_ref(ref)
            person_objects[child].add_parent_family_handle(handle)
        family_objects.append(family)
    with DbTxn("Generate tree", db) as trans:
        for person in person_objects:
            db.add_person(person, trans)
        for family in family_objects:
            db.add_family(family, trans)


class LargeTreeTest(unittest.TestCase):
    """
    Test searches in a generated tree of a few thousand people.

    Graphs read on demand must give the same results as a graph of the
    whole tree, while reading only the people near the two people searched
    for.
    """

    db: ClassVar[Any]
    full: ClassVar[FamilyLinkGraph]
    pairs: ClassVar[list[tuple[PersonHandle, PersonHandle]]]
    calc: ClassVar[RelationshipCalculator]

    @classmethod
    def setUpClass(cls) -> None:
        cls.db = make_database("sqlite")
        cls.db.load(":memory:")
        _generate_tree(cls.db, seed=1)
        cls.full = _full_graph(cls.db)
        cls.calc = RelationshipCalculator()
        rng = random.Random(2)
        people = sorted(cls.full._gender)
        # the people with the most relatives within 4 links, where a
        # search reaches furthest
        hubs = sorted(
            rng.sample(people, 300),
            key=lambda handle: (-len(cls.full.distances(handle, 4)), handle),
        )[:4]
        pairs = []
        for hub in hubs:
            near = cls.full.distances(hub, 12)
            by_distance: dict[int, list[PersonHandle]] = {}
            for handle, distance in near.items():
                by_distance.setdefault(distance, []).append(handle)
            for distance in (1, 2, 4, 7, 10, 12):
                if distance in by_distance:
                    pairs.append((hub, rng.choice(sorted(by_distance[distance]))))
            unconnected = sorted(set(people) - near.keys())
            if unconnected:
                pairs.append((hub, rng.choice(unconnected)))
        pairs += [(rng.choice(people), rng.choice(people)) for _ in range(10)]
        cls.pairs = pairs

    @classmethod
    def tearDownClass(cls) -> None:
        cls.db.close()

    def test_tree_shape(self) -> None:
        """
        The generated tree is large and has a densely linked core.
        """
        self.assertGreater(len(self.full), 2000)
        hub = self.pairs[0][0]
        self.assertGreater(len(self.full.distances(hub, 10)), len(self.full) // 4)

    def test_same_as_full_graph(self) -> None:
        """
        A graph read on demand finds the same paths as a graph of the whole
        tree, for any depth, number of results and kinds of links.
        """
        for start, end in self.pairs:
            for max_depth in (1, 3, 6, 10):
                for max_results in (1, 5):
                    for kwargs in (
                        {},
                        {"blood_only": True},
                        {"links": {LinkType.PARENT}},
                        {"links": {LinkType.CHILD, LinkType.SPOUSE}},
                    ):
                        with self.subTest(
                            start=start, end=end, max_depth=max_depth, **kwargs
                        ):
                            graph = FamilyLinkGraph.from_db(self.db)
                            self.assertEqual(
                                find_connections(
                                    graph,
                                    start,
                                    end,
                                    max_depth=max_depth,
                                    max_results=max_results,
                                    **kwargs,
                                ),
                                find_connections(
                                    self.full,
                                    start,
                                    end,
                                    max_depth=max_depth,
                                    max_results=max_results,
                                    **kwargs,
                                ),
                            )

    def test_same_labels(self) -> None:
        """
        The paths found on demand are labelled as in the whole tree.
        """
        for start, end in self.pairs:
            graph = FamilyLinkGraph.from_db(self.db)
            paths = find_connections(graph, start, end)
            self.assertEqual(
                [label_path(self.calc, self.db, graph, path) for path in paths],
                [label_path(self.calc, self.db, self.full, path) for path in paths],
            )

    def test_reads_stay_near(self) -> None:
        """
        A search reads only the people within about half of max_depth links
        of the two people, not everyone within max_depth links of either.
        """
        for start, end in self.pairs:
            for max_depth in (4, 7, 10):
                with self.subTest(start=start, end=end, max_depth=max_depth):
                    db = _CountingDb(self.db)
                    find_connections(
                        FamilyLinkGraph.from_db(db), start, end, max_depth=max_depth
                    )
                    radius = (max_depth + 1) // 2 + 1
                    near = set(self.full.distances(start, radius, ALL_LINKS))
                    near |= set(self.full.distances(end, radius, ALL_LINKS))
                    self.assertEqual(sorted(db.people - near - {start, end}), [])

    def test_parent_reads_little(self) -> None:
        """
        Finding a parent of a well-connected person reads a small part of
        the people within max_depth links of them.
        """
        start, end = self.pairs[0]
        self.assertIn(
            end,
            self.full.parents(start)
            + self.full.children(start)
            + self.full.siblings(start)
            + self.full.spouses(start),
        )
        db = _CountingDb(self.db)
        find_connections(FamilyLinkGraph.from_db(db), start, end)
        self.assertLess(len(db.people), len(self.full.distances(end, 10)) // 4)

    def test_private_proxy(self) -> None:
        """
        Through a private proxy, the results are those of the whole visible
        tree, and hidden people are never in the graph.
        """
        db = PrivateProxyDb(self.db)
        full = _full_graph(db)
        hidden = set(self.full._gender) - set(full._gender)
        self.assertTrue(hidden)
        for start, end in self.pairs:
            graph = FamilyLinkGraph.from_db(db)
            for blood_only in (False, True):
                self.assertEqual(
                    find_connections(graph, start, end, blood_only=blood_only),
                    find_connections(full, start, end, blood_only=blood_only),
                )
            self.assertFalse(set(graph._gender) & hidden)


if __name__ == "__main__":
    unittest.main()
