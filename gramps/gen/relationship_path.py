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
and sibling. Made from a database, it reads people and their families when
a search first reaches them, so a search reads only the part of a large
tree near the people searched for. Searches read a whole layer of people
at a time, so the number of database queries depends on how many links
they follow, not on how many people they reach. The graph reads through
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
# The most links a search may follow. A search first reads everyone within
# half of this many links of the end person, which in a densely linked tree
# grows quickly with the depth.
MAX_DEPTH = 15
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

    A graph made by :meth:`from_db` reads a person and their families from
    the database the first time they are needed. Otherwise it contains the
    people and families added with :meth:`add_person` and
    :meth:`add_family`.
    """

    def __init__(self) -> None:
        # the database people are read from as needed, or None
        self._db: DbReadBase | None = None
        # people read so far -> their parent families and own families
        self._person_families: dict[PersonHandle, list[FamilyHandle]] = {}
        # people missing from the database, or hidden by a proxy
        self._missing: set[PersonHandle] = set()
        # families missing from the database, or hidden by a proxy
        self._missing_families: set[FamilyHandle] = set()
        # people whose families have all been read
        self._expanded: set[PersonHandle] = set()
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
        Return a graph that reads people and families from the database
        when they are first needed.

        A search only reads the people within reach of the people searched
        for, rather than the whole tree. People and families are read many
        at a time with ``get_raw_person_data_many`` and
        ``get_raw_family_data_many``, so proxies such as ``PrivateProxyDb``
        and ``LivingProxyDb`` decide which people and links the graph
        contains. The database must stay open while the graph is used.
        """
        graph = cls()
        graph._db = db
        return graph

    def _read_people(self, handles: Iterable[PersonHandle | None]) -> None:
        """
        Read the people not read yet, in one batch.
        """
        if self._db is None:
            return
        todo = [
            handle
            for handle in dict.fromkeys(handles)
            if handle and handle not in self._gender and handle not in self._missing
        ]
        if not todo:
            return
        # each person's data is dropped as soon as it is used, which keeps
        # the garbage collector from having to look at it
        for handle, data in self._db.get_raw_person_data_many(todo):
            self.add_person(handle, data["gender"])
            self._person_families[handle] = [
                *data["parent_family_list"],
                *data["family_list"],
            ]
        self._missing.update(handle for handle in todo if handle not in self._gender)

    def read(self, handles: Iterable[PersonHandle]) -> None:
        """
        Read the families of the given people, and the members of those
        families, so that their links are known.

        Reading many people at once takes a few database queries rather
        than a few per person. Searches read each layer of people they
        reach this way. Does nothing for a graph not made from a database.
        """
        if self._db is None:
            return
        todo = [
            handle for handle in dict.fromkeys(handles) if handle not in self._expanded
        ]
        if not todo:
            return
        self._expanded.update(todo)
        self._read_people(todo)
        family_handles = [
            family_handle
            for family_handle in dict.fromkeys(
                family_handle
                for handle in todo
                for family_handle in self._person_families.get(handle, [])
            )
            if family_handle not in self._families
            and family_handle not in self._missing_families
        ]
        if not family_handles:
            return
        found = {}
        for family_handle, data in self._db.get_raw_family_data_many(family_handles):
            found[family_handle] = (
                data["father_handle"] or None,
                data["mother_handle"] or None,
                [
                    (
                        ref["ref"],
                        ref["mrel"]["value"] == ChildRefType.BIRTH,
                        ref["frel"]["value"] == ChildRefType.BIRTH,
                    )
                    for ref in data["child_ref_list"]
                ],
            )
        # add_family leaves out people not in the graph
        self._read_people(
            member
            for father, mother, children in found.values()
            for member in (father, mother, *(child for child, _, _ in children))
        )
        # in the order the people list them, whatever order they were read in
        for family_handle in family_handles:
            if family_handle in found:
                self.add_family(family_handle, *found[family_handle])
            else:
                self._missing_families.add(family_handle)

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
        if isinstance(handle, str):
            self._read_people([PersonHandle(handle)])
        return handle in self._gender

    def __len__(self) -> int:
        """
        Return the number of people in the graph, or read so far.
        """
        return len(self._gender)

    def gender(self, handle: PersonHandle) -> int:
        """
        Return the gender of a person.
        """
        self._read_people([handle])
        return self._gender.get(handle, Person.UNKNOWN)

    def parents(self, handle: PersonHandle) -> list[PersonHandle]:
        """
        Return the parents of a person, in all their parent families, by handle.
        """
        self.read([handle])
        result: list[PersonHandle] = []
        for family, _, _ in self._parent_families.get(handle, []):
            father, mother, _ = self._families[family]
            for parent in (father, mother):
                if parent and parent not in result:
                    result.append(parent)
        return sorted(result)

    def children(self, handle: PersonHandle) -> list[PersonHandle]:
        """
        Return the children of a person, in all their families, by handle.
        """
        self.read([handle])
        result: list[PersonHandle] = []
        for family in self._spouse_families.get(handle, []):
            for child in self._families[family][2]:
                if child not in result:
                    result.append(child)
        return sorted(result)

    def spouses(self, handle: PersonHandle) -> list[PersonHandle]:
        """
        Return the partners of a person, by handle.
        """
        self.read([handle])
        result: list[PersonHandle] = []
        for family in self._spouse_families.get(handle, []):
            father, mother, _ = self._families[family]
            partner = mother if father == handle else father
            if partner and partner != handle and partner not in result:
                result.append(partner)
        return sorted(result)

    def siblings(self, handle: PersonHandle) -> list[PersonHandle]:
        """
        Return the other children of all parent families of a person, by handle.
        """
        self.read([handle])
        result: list[PersonHandle] = []
        for family, _, _ in self._parent_families.get(handle, []):
            for child in self._families[family][2]:
                if child != handle and child not in result:
                    result.append(child)
        return sorted(result)

    def neighbors(
        self, handle: PersonHandle, links: Iterable[LinkType] = ALL_LINKS
    ) -> Iterator[tuple[PersonHandle, LinkType]]:
        """
        Yield the people linked to a person, blood relatives first.

        Within each kind of link, people come in handle order, so that
        searches give the same results whatever order the database
        returns families in.
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
        self.read([child])
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
        self.read([child])
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
        layer = [handle]
        for depth in range(1, max_depth + 1):
            self.read(layer)
            next_layer = []
            for current in layer:
                for other, _ in self.neighbors(current, links):
                    if other not in result:
                        result[other] = depth
                        next_layer.append(other)
            if not next_layer:
                break
            layer = next_layer
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


class _DistanceToEnd:
    """
    The number of links from people to the end of a search.

    Finding everyone within ``max_depth`` links of the end would read a
    large part of a densely linked tree. Instead, only the people within
    half of ``max_depth`` links of the end are found up front. Any path to
    the end from someone further away passes someone exactly that far from
    the end, so their distance is found by searching from them until they
    reach one, and no further than a search needs. People are thus read
    only near the end, or near the people the search reaches from the start.

    :meth:`prepare` searches from many people together, reading one layer
    of all their searches at a time.
    """

    def __init__(
        self,
        graph: FamilyLinkGraph,
        end: PersonHandle,
        max_depth: int,
        links: frozenset[LinkType],
    ) -> None:
        self._graph = graph
        self._links = links
        self._radius = max_depth // 2
        # following the links backwards gives the distance to the end
        self._near = graph.distances(
            end, self._radius, {link.reverse() for link in links}
        )
        # people further than the radius -> their distance to the end
        self._far: dict[PersonHandle, int] = {}
        # people further than the radius -> no one near within this many links
        self._not_within: dict[PersonHandle, int] = {}

    def prepare(self, handles: Iterable[PersonHandle], limit: int) -> None:
        """
        Find out whether each person is within ``limit`` links of the end,
        so that :meth:`within` needs no more reading for them.
        """
        steps = limit - self._radius
        # person -> (people seen by their search, its last layer)
        searches: dict[PersonHandle, tuple[set[PersonHandle], list[PersonHandle]]] = {
            handle: ({handle}, [handle])
            for handle in dict.fromkeys(handles)
            if handle not in self._near
            and handle not in self._far
            and steps > self._not_within.get(handle, 0)
        }
        for step in range(1, steps + 1):
            if not searches:
                return
            self._graph.read(
                current for _, layer in searches.values() for current in layer
            )
            for handle, (seen, layer) in list(searches.items()):
                if self._step(seen, layer):
                    # the first near person reached is exactly radius links
                    # from the end
                    self._far[handle] = self._radius + step
                    del searches[handle]
                elif not layer:
                    self._not_within[handle] = steps
                    del searches[handle]
        for handle in searches:
            self._not_within[handle] = steps

    def _step(self, seen: set[PersonHandle], layer: list[PersonHandle]) -> bool:
        """
        Advance a search by one layer, in place. Return True if it reached
        a near person.
        """
        next_layer = []
        for current in layer:
            for other, _ in self._graph.neighbors(current, self._links):
                if other in seen:
                    continue
                if other in self._near:
                    return True
                seen.add(other)
                next_layer.append(other)
        layer[:] = next_layer
        return False

    def within(self, handle: PersonHandle, limit: int) -> int | None:
        """
        Return the number of links from a person to the end, or None if it
        is more than ``limit``.
        """
        distance = self._near.get(handle)
        if distance is None:
            distance = self._far.get(handle)
        if distance is None:
            if limit - self._radius <= self._not_within.get(handle, 0):
                return None
            self.prepare([handle], limit)
            distance = self._far.get(handle)
            if distance is None:
                return None
        return distance if distance <= limit else None


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

    To keep the search fast, each person is expanded at most
    ``max_results`` times, so a path that a full search would return can
    occasionally be missed. The results depend only on the tree, not on the
    order the database returns people and families in.

    :param max_depth: The maximum number of links in a path, at most
                      :data:`MAX_DEPTH`.
    :param max_results: The maximum number of paths to return.
    :param links: The kinds of links a path may follow.
    :param blood_only: Only find paths that go up to a common ancestor and
                       down again: parent links, at most one sibling link,
                       then child links.
    """
    if max_depth > MAX_DEPTH:
        raise ValueError(f"max_depth is more than {MAX_DEPTH}")
    if start not in graph or end not in graph or max_results < 1:
        return []
    if start == end:
        return [[(start, None)]]
    links = frozenset(links)
    if blood_only:
        links -= {LinkType.SPOUSE}
    # The distance to the end, so that people who cannot reach it within
    # max_depth are never visited.
    to_end = _DistanceToEnd(graph, end, max_depth, links)
    if to_end.within(start, max_depth) is None:
        return []

    results: list[Path] = []
    expanded: Counter[tuple[PersonHandle, bool]] = Counter()
    # The search goes one layer of paths at a time, all of the same length,
    # so the people of a layer can be read together.
    layer: list[_PathNode] = [(start, None, None, 0)]
    for depth in range(max_depth):
        # Each person is expanded at most max_results times, which bounds
        # the search while still finding that many different paths.
        to_expand = []
        for node in layer:
            going_down = blood_only and _going_down(node)
            if expanded[node[0], going_down] >= max_results:
                continue
            expanded[node[0], going_down] += 1
            to_expand.append((node, going_down))
        graph.read(node[0] for node, _ in to_expand)
        steps = [
            (node, other, link)
            for node, going_down in to_expand
            for other, link in graph.neighbors(node[0], links)
            if not going_down or link == LinkType.CHILD
        ]
        to_end.prepare((other for _, other, _ in steps), max_depth - depth - 1)
        next_layer: list[_PathNode] = []
        for node, other, link in steps:
            if to_end.within(other, max_depth - depth - 1) is None:
                continue
            if _on_path(node, other):
                continue
            new_node: _PathNode = (other, link, node, depth + 1)
            if other == end:
                results.append(_to_path(new_node))
                if len(results) >= max_results:
                    return results
            else:
                next_layer.append(new_node)
        if not next_layer:
            break
        layer = next_layer
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
