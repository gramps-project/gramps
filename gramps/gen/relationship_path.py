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
Find and label chains of family links between two people.

A :class:`FamilyLinkGraph` holds only who is whose parent, child, partner
and sibling, so it is small enough to keep in memory for large trees and
holds no reference to the database it was built from. It is built through
the public database interface, so proxies such as ``PrivateProxyDb`` and
``LivingProxyDb`` decide which people and links it contains.

:func:`find_connections` finds chains of links between two people, shortest
first, and :func:`label_path` describes each person on a chain by their
relationship to the first person, using the strings of a
:class:`~gramps.gen.relationship.RelationshipCalculator`.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations

from collections import Counter, deque
from collections.abc import Iterable, Iterator
from enum import Enum

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .db.base import DbReadBase
from .lib import ChildRefType, Person
from .relationship import RelationshipCalculator
from .types import FamilyHandle, PersonHandle

DEFAULT_MAX_DEPTH = 10
DEFAULT_MAX_RESULTS = 5


# -------------------------------------------------------------------------
#
# LinkType
#
# -------------------------------------------------------------------------
class LinkType(str, Enum):
    """
    How a person on a path is linked to the person before them.
    """

    PARENT = "parent"
    CHILD = "child"
    SPOUSE = "spouse"
    SIBLING = "sibling"

    def reverse(self) -> LinkType:
        """
        Return the link seen from the other person.
        """
        if self is LinkType.PARENT:
            return LinkType.CHILD
        if self is LinkType.CHILD:
            return LinkType.PARENT
        return self


ALL_LINKS = frozenset(LinkType)

PathStep = tuple[PersonHandle, LinkType | None]
Path = list[PathStep]

# A path being searched, as (handle, link, previous node, depth).
_PathNode = tuple[PersonHandle, LinkType | None, "_PathNode | None", int]


# -------------------------------------------------------------------------
#
# FamilyLinkGraph
#
# -------------------------------------------------------------------------
class FamilyLinkGraph:
    """
    The family links between people, kept in memory.
    """

    def __init__(self) -> None:
        self._gender: dict[PersonHandle, int] = {}
        # child -> [(family, birth child of mother, birth child of father)]
        self._parent_families: dict[
            PersonHandle, list[tuple[FamilyHandle, bool, bool]]
        ] = {}
        self._spouse_families: dict[PersonHandle, list[FamilyHandle]] = {}
        # family -> (father, mother, children)
        self._families: dict[
            FamilyHandle,
            tuple[PersonHandle | None, PersonHandle | None, list[PersonHandle]],
        ] = {}

    @classmethod
    def from_db(cls, db: DbReadBase) -> FamilyLinkGraph:
        """
        Build the graph from all people and families in the database.
        """
        graph = cls()
        for person in db.iter_people():
            graph.add_person(person.handle, person.get_gender())
        for family in db.iter_families():
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
                    for ref in family.get_child_ref_list()
                ],
            )
        return graph

    def add_person(self, handle: PersonHandle, gender: int) -> None:
        """
        Add a person with the given gender.
        """
        self._gender[handle] = gender

    def add_family(
        self,
        handle: FamilyHandle,
        father: PersonHandle | None,
        mother: PersonHandle | None,
        children: Iterable[tuple[PersonHandle, bool, bool]],
    ) -> None:
        """
        Add a family. Members that were not added as people are left out.

        :param children: (child, birth child of mother, birth child of father)
        """
        father = father if father in self._gender else None
        mother = mother if mother in self._gender else None
        child_list = []
        for child, mother_birth, father_birth in children:
            if child not in self._gender:
                continue
            child_list.append(child)
            self._parent_families.setdefault(child, []).append(
                (handle, mother_birth, father_birth)
            )
        for parent in (father, mother):
            if parent:
                self._spouse_families.setdefault(parent, []).append(handle)
        self._families[handle] = (father, mother, child_list)

    def __contains__(self, handle: object) -> bool:
        return handle in self._gender

    def __len__(self) -> int:
        return len(self._gender)

    def gender(self, handle: PersonHandle) -> int:
        """
        Return the gender of a person.
        """
        return self._gender.get(handle, Person.UNKNOWN)

    def parents(self, handle: PersonHandle) -> list[PersonHandle]:
        """
        Return the parents of a person, in all their parent families.
        """
        result: list[PersonHandle] = []
        for family, _, _ in self._parent_families.get(handle, []):
            father, mother, _ = self._families[family]
            for parent in (father, mother):
                if parent and parent not in result:
                    result.append(parent)
        return result

    def children(self, handle: PersonHandle) -> list[PersonHandle]:
        """
        Return the children of a person, in all their families.
        """
        result: list[PersonHandle] = []
        for family in self._spouse_families.get(handle, []):
            for child in self._families[family][2]:
                if child not in result:
                    result.append(child)
        return result

    def spouses(self, handle: PersonHandle) -> list[PersonHandle]:
        """
        Return the partners of a person.
        """
        result: list[PersonHandle] = []
        for family in self._spouse_families.get(handle, []):
            father, mother, _ = self._families[family]
            partner = mother if father == handle else father
            if partner and partner != handle and partner not in result:
                result.append(partner)
        return result

    def siblings(self, handle: PersonHandle) -> list[PersonHandle]:
        """
        Return the other children of all parent families of a person.
        """
        result: list[PersonHandle] = []
        for family, _, _ in self._parent_families.get(handle, []):
            for child in self._families[family][2]:
                if child != handle and child not in result:
                    result.append(child)
        return result

    def neighbors(
        self, handle: PersonHandle, links: Iterable[LinkType] = ALL_LINKS
    ) -> Iterator[tuple[PersonHandle, LinkType]]:
        """
        Yield the people linked to a person, blood relatives first.
        """
        links = frozenset(links)
        if LinkType.PARENT in links:
            for other in self.parents(handle):
                yield other, LinkType.PARENT
        if LinkType.CHILD in links:
            for other in self.children(handle):
                yield other, LinkType.CHILD
        if LinkType.SIBLING in links:
            for other in self.siblings(handle):
                yield other, LinkType.SIBLING
        if LinkType.SPOUSE in links:
            for other in self.spouses(handle):
                yield other, LinkType.SPOUSE

    def parent_code(
        self, calc: RelationshipCalculator, child: PersonHandle, parent: PersonHandle
    ) -> str:
        """
        Return the calculator's code for the step from a child to a parent.
        """
        found = ""
        for family, mother_birth, father_birth in self._parent_families.get(child, []):
            father, mother, _ = self._families[family]
            if parent == father:
                if father_birth:
                    return calc.REL_FATHER
                found = found or calc.REL_FATHER_NOTBIRTH
            if parent == mother:
                if mother_birth:
                    return calc.REL_MOTHER
                found = found or calc.REL_MOTHER_NOTBIRTH
        return found

    def family_code(
        self, calc: RelationshipCalculator, child: PersonHandle, sibling: PersonHandle
    ) -> str:
        """
        Return the calculator's code for the step from a child to the family
        it shares with a sibling.
        """
        found = ""
        for family, mother_birth, father_birth in self._parent_families.get(child, []):
            if sibling not in self._families[family][2]:
                continue
            if mother_birth and father_birth:
                return calc.REL_FAM_BIRTH
            if mother_birth:
                found = found or calc.REL_FAM_BIRTH_MOTH_ONLY
            elif father_birth:
                found = found or calc.REL_FAM_BIRTH_FATH_ONLY
            else:
                found = found or calc.REL_FAM_NONBIRTH
        return found

    def distances(
        self,
        handle: PersonHandle,
        max_depth: int,
        links: Iterable[LinkType] = ALL_LINKS,
    ) -> dict[PersonHandle, int]:
        """
        Return the number of links from each person within ``max_depth``
        links of the given person.
        """
        result = {handle: 0}
        queue = deque([handle])
        while queue:
            current = queue.popleft()
            depth = result[current]
            if depth >= max_depth:
                continue
            for other, _ in self.neighbors(current, links):
                if other not in result:
                    result[other] = depth + 1
                    queue.append(other)
        return result


# -------------------------------------------------------------------------
#
# Searching
#
# -------------------------------------------------------------------------
def _on_path(node: _PathNode | None, handle: PersonHandle) -> bool:
    """
    Return True if the person is already on the path ending at node.
    """
    while node is not None:
        if node[0] == handle:
            return True
        node = node[2]
    return False


def _going_down(node: _PathNode) -> bool:
    """
    Return True if the path ending at node has passed a common ancestor.
    """
    return node[1] in (LinkType.CHILD, LinkType.SIBLING)


def _to_path(node: _PathNode | None) -> Path:
    """
    Return the path ending at node, starting with the first person.
    """
    path: Path = []
    while node is not None:
        path.append((node[0], node[1]))
        node = node[2]
    path.reverse()
    return path


def find_connections(
    graph: FamilyLinkGraph,
    start: PersonHandle,
    end: PersonHandle,
    *,
    max_depth: int = DEFAULT_MAX_DEPTH,
    max_results: int = DEFAULT_MAX_RESULTS,
    links: Iterable[LinkType] = ALL_LINKS,
    blood_only: bool = False,
) -> list[Path]:
    """
    Find chains of family links from one person to another.

    Each path is a list of ``(handle, link)`` steps, where ``link`` says how
    the person is linked to the person before them, and is ``None`` for the
    first person. Paths never visit a person twice and are returned
    shortest first.

    :param max_depth: The maximum number of links in a path.
    :param max_results: The maximum number of paths to return.
    :param links: The kinds of links a path may follow.
    :param blood_only: Only find paths that go up to a common ancestor and
                       down again: parent links, at most one sibling link,
                       then child links.
    """
    if start not in graph or end not in graph or max_results < 1:
        return []
    if start == end:
        return [[(start, None)]]
    links = frozenset(links)
    if blood_only:
        links -= {LinkType.SPOUSE}
    # Distance of every person to the end, following the links backwards,
    # so that people who cannot reach it within max_depth are never visited.
    to_end = graph.distances(end, max_depth, {link.reverse() for link in links})
    if start not in to_end:
        return []

    results: list[Path] = []
    expanded: Counter[tuple[PersonHandle, bool]] = Counter()
    queue: deque[_PathNode] = deque([(start, None, None, 0)])
    while queue:
        node = queue.popleft()
        handle, depth = node[0], node[3]
        going_down = blood_only and _going_down(node)
        # Each person is expanded at most max_results times, which bounds
        # the search while still finding that many different paths.
        if expanded[handle, going_down] >= max_results:
            continue
        expanded[handle, going_down] += 1
        for other, link in graph.neighbors(handle, links):
            if going_down and link != LinkType.CHILD:
                continue
            remaining = to_end.get(other)
            if remaining is None or depth + 1 + remaining > max_depth:
                continue
            if _on_path(node, other):
                continue
            new_node: _PathNode = (other, link, node, depth + 1)
            if other == end:
                results.append(_to_path(new_node))
                if len(results) >= max_results:
                    return results
            else:
                queue.append(new_node)
    return results


# -------------------------------------------------------------------------
#
# Labelling
#
# -------------------------------------------------------------------------
def _parse_blood(
    calc: RelationshipCalculator,
    graph: FamilyLinkGraph,
    people: list[PersonHandle],
    links: list[LinkType],
) -> tuple[int, int, str, str] | None:
    """
    Return (Ga, Gb, path code of a, path code of b) for a chain of up
    steps, at most one sibling step, and then down steps.

    ``links[i]`` is how ``people[i + 1]`` is linked to ``people[i]``.
    """
    index = 0
    rel_a = ""
    while index < len(links) and links[index] == LinkType.PARENT:
        rel_a += graph.parent_code(calc, people[index], people[index + 1])
        index += 1
    top = index
    sibling = index < len(links) and links[index] == LinkType.SIBLING
    if sibling:
        index += 1
    downs = index
    while index < len(links) and links[index] == LinkType.CHILD:
        index += 1
    if index != len(links):
        return None
    rel_b = ""
    for pos in range(len(links), downs, -1):
        rel_b += graph.parent_code(calc, people[pos], people[pos - 1])
    if sibling:
        rel_a += graph.family_code(calc, people[top], people[top + 1])
        rel_b += graph.family_code(calc, people[top + 1], people[top])
    return top + sibling, len(links) - downs + sibling, rel_a, rel_b


def _label(
    calc: RelationshipCalculator,
    db: DbReadBase,
    graph: FamilyLinkGraph,
    people: list[PersonHandle],
    links: list[LinkType],
) -> str | None:
    """
    Return the relationship of the last person to the first, or None.
    """
    first, last = people[0], people[-1]
    if not links:
        return ""
    if links == [LinkType.SPOUSE]:
        return calc.is_spouse(
            db, db.get_person_from_handle(first), db.get_person_from_handle(last)
        )
    in_law_a = links[0] == LinkType.SPOUSE
    in_law_b = links[-1] == LinkType.SPOUSE
    if in_law_a and in_law_b:
        return None
    core_people = people[1:] if in_law_a else people
    core_people = core_people[:-1] if in_law_b else core_people
    core_links = links[1:] if in_law_a else links
    core_links = core_links[:-1] if in_law_b else core_links
    if LinkType.SPOUSE in core_links:
        return None
    parsed = _parse_blood(calc, graph, core_people, core_links)
    if parsed is None:
        return None
    dist_a, dist_b, rel_a, rel_b = parsed
    only_birth = calc.only_birth(rel_a) and calc.only_birth(rel_b)
    # A descendant of a partner is a step child, and a partner of an
    # ancestor is a step parent, rather than an in-law.
    if (in_law_a and dist_a == 0) or (in_law_b and dist_b == 0):
        in_law_a = in_law_b = only_birth = False
    gender_a = graph.gender(first)
    gender_b = graph.gender(last)
    if dist_a == dist_b == 1:
        sib_type = calc.get_sibling_type(
            db,
            db.get_person_from_handle(core_people[0]),
            db.get_person_from_handle(core_people[-1]),
        )
        return calc.get_sibling_relationship_string(
            sib_type, gender_a, gender_b, in_law_a, in_law_b
        )
    return calc.get_single_relationship_string(
        dist_a,
        dist_b,
        gender_a,
        gender_b,
        rel_a,
        rel_b,
        only_birth=only_birth,
        in_law_a=in_law_a,
        in_law_b=in_law_b,
    )


def label_path(
    calc: RelationshipCalculator,
    db: DbReadBase,
    graph: FamilyLinkGraph,
    path: Path,
) -> list[str | None]:
    """
    Describe each person on a path by their relationship to the first person.

    The label of the first person is an empty string. A label is ``None``
    when the relationship along the path has no name, for example through
    more than one marriage; the link to the person before can be shown
    instead.

    :param calc: The calculator whose language the labels are in.
    :param db: The database the graph was built from, used to look up
               partner and sibling types.
    """
    people = [handle for handle, _ in path]
    links = [link for _, link in path[1:] if link is not None]
    return [
        _label(calc, db, graph, people[: index + 1], links[:index])
        for index in range(len(path))
    ]
