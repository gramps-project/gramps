#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024  Gramps Development Team
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
Graph utilities for Gramps genealogy data.

This module provides unified functions for traversing family relationships
in genealogical data, combining various BFS algorithms used throughout
the codebase.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations
from typing import Set, List, Tuple, Optional, Iterator
from collections import deque

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..lib import Person
from ..db import Database
from ..types import PersonHandle


def find_ancestors(
    db: Database,
    person_handles: List[PersonHandle],
    min_generation: int = 1,
    max_generation: Optional[int] = None,
    inclusive: bool = False,
    include_all_parent_families: bool = False,
) -> Set[PersonHandle]:
    """
    Find ancestors of one or more people using BFS traversal.

    This function combines the functionality of various ancestor finding
    algorithms used throughout the Gramps codebase into a single, efficient
    implementation. It's optimized to handle multiple starting people by
    sharing the visited set across all searches.

    Args:
        db: The Gramps database
        person_handles: List of person handles to find ancestors for
        min_generation: Minimum generation to include (1 = parents, 2 = grandparents, etc.)
        max_generation: Maximum generation to include (None = no limit)
        inclusive: Whether to include the starting people in results
        include_all_parent_families: Whether to traverse all parent families
                                    (False = only first parent family)

    Returns:
        Set of person handles representing the ancestors

    Examples:
        # Find all ancestors of a single person (equivalent to _isancestorof.py)
        ancestors = find_ancestors(db, [person_handle], inclusive=False)

        # Find ancestors up to 3 generations (equivalent to _islessthannthgenerationancestorof.py)
        ancestors = find_ancestors(db, [person_handle], max_generation=3, inclusive=False)

        # Find ancestors at least 2 generations away (equivalent to _ismorethannthgenerationancestorof.py)
        ancestors = find_ancestors(db, [person_handle], min_generation=2, inclusive=False)

        # Find ancestors including the starting person
        ancestors = find_ancestors(db, [person_handle], inclusive=True)

        # Find ancestors of multiple people (equivalent to _islessthannthgenerationancestorofbookmarked.py)
        ancestors = find_ancestors(db, [person1_handle, person2_handle], inclusive=False)
    """
    # Use the iterative function internally to avoid code duplication
    ancestors: Set[PersonHandle] = set()

    for handle, _ in find_ancestors_iterative(
        db,
        person_handles,
        min_generation,
        max_generation,
        inclusive,
        include_all_parent_families,
    ):
        ancestors.add(handle)

    return ancestors


def find_ancestors_iterative(
    db: Database,
    person_handles: List[PersonHandle],
    min_generation: int = 1,
    max_generation: Optional[int] = None,
    inclusive: bool = False,
    include_all_parent_families: bool = False,
) -> Iterator[Tuple[PersonHandle, int]]:
    """
    Find ancestors of one or more people using BFS traversal, yielding results as they're found.

    This is useful for processing large ancestor trees without storing all results
    in memory at once. It's optimized to handle multiple starting people by
    sharing the visited set across all searches.

    Args:
        db: The Gramps database
        person_handles: List of person handles to find ancestors for
        min_generation: Minimum generation to include (1 = parents, 2 = grandparents, etc.)
        max_generation: Maximum generation to include (None = no limit)
        inclusive: Whether to include the starting people in results
        include_all_parent_families: Whether to traverse all parent families
                                    (False = only first parent family)

    Yields:
        Tuples of (person_handle, generation) for each ancestor found
    """
    if not person_handles:
        return

    # BFS queue: (person_handle, generation)
    queue: deque[Tuple[PersonHandle, int]] = deque()

    # Track visited nodes to avoid cycles (shared across all searches)
    visited: Set[PersonHandle] = set()

    # Add all starting people to the queue
    for person_handle in person_handles:
        if person_handle:
            queue.append((person_handle, 0))

    while queue:
        current_handle, generation = queue.popleft()

        # Skip if already visited
        if current_handle in visited:
            continue

        visited.add(current_handle)

        # Yield if within generation range
        if (generation >= min_generation or (inclusive and generation == 0)) and (
            max_generation is None or generation <= max_generation
        ):
            yield current_handle, generation

        # Stop if we've reached max_generation
        if max_generation is not None and generation >= max_generation:
            continue

        # Get person and their parent families
        try:
            person = db.get_person_from_handle(current_handle)
            if not person:
                continue
        except:
            # Handle non-existent handles gracefully
            continue

        # Determine which parent families to process
        parent_families = person.parent_family_list
        if not include_all_parent_families and parent_families:
            parent_families = [parent_families[0]]  # Only first parent family

        # Process each parent family
        for family_handle in parent_families:
            family = db.get_family_from_handle(family_handle)
            if not family:
                continue

            # Add parents to queue
            if family.father_handle:
                queue.append((family.father_handle, generation + 1))
            if family.mother_handle:
                queue.append((family.mother_handle, generation + 1))


def find_descendants(
    db: Database,
    person_handles: List[PersonHandle],
    min_generation: int = 1,
    max_generation: Optional[int] = None,
    inclusive: bool = False,
    include_all_families: bool = False,
) -> Set[PersonHandle]:
    """
    Find descendants of one or more people using BFS traversal.

    This function combines the functionality of various descendant finding
    algorithms used throughout the Gramps codebase into a single, efficient
    implementation. It's optimized to handle multiple starting people by
    sharing the visited set across all searches.

    Args:
        db: The Gramps database
        person_handles: List of person handles to find descendants for
        min_generation: Minimum generation to include (1 = children, 2 = grandchildren, etc.)
        max_generation: Maximum generation to include (None = no limit)
        inclusive: Whether to include the starting people in results
        include_all_families: Whether to traverse all families
                             (False = only first family)

    Returns:
        Set of person handles representing the descendants

    Examples:
        # Find all descendants of a single person
        descendants = find_descendants(db, [person_handle], inclusive=False)

        # Find descendants up to 3 generations
        descendants = find_descendants(db, [person_handle], max_generation=3, inclusive=False)

        # Find descendants at least 2 generations away
        descendants = find_descendants(db, [person_handle], min_generation=2, inclusive=False)

        # Find descendants including the starting person
        descendants = find_descendants(db, [person_handle], inclusive=True)

        # Find descendants of multiple people
        descendants = find_descendants(db, [person1_handle, person2_handle], inclusive=False)
    """
    # Use the iterative function internally to avoid code duplication
    descendants: Set[PersonHandle] = set()

    for handle, _ in find_descendants_iterative(
        db,
        person_handles,
        min_generation,
        max_generation,
        inclusive,
        include_all_families,
    ):
        descendants.add(handle)

    return descendants


def find_descendants_iterative(
    db: Database,
    person_handles: List[PersonHandle],
    min_generation: int = 1,
    max_generation: Optional[int] = None,
    inclusive: bool = False,
    include_all_families: bool = False,
) -> Iterator[Tuple[PersonHandle, int]]:
    """
    Find descendants of one or more people using BFS traversal, yielding results as they're found.

    This is useful for processing large descendant trees without storing all results
    in memory at once. It's optimized to handle multiple starting people by
    sharing the visited set across all searches.

    Args:
        db: The Gramps database
        person_handles: List of person handles to find descendants for
        min_generation: Minimum generation to include (1 = children, 2 = grandchildren, etc.)
        max_generation: Maximum generation to include (None = no limit)
        inclusive: Whether to include the starting people in results
        include_all_families: Whether to traverse all families
                             (False = only first family)

    Yields:
        Tuples of (person_handle, generation) for each descendant found
    """
    if not person_handles:
        return

    # BFS queue: (person_handle, generation)
    queue: deque[Tuple[PersonHandle, int]] = deque()

    # Track visited nodes to avoid cycles (shared across all searches)
    visited: Set[PersonHandle] = set()

    # Add all starting people to the queue
    for person_handle in person_handles:
        if person_handle:
            queue.append((person_handle, 0))

    while queue:
        current_handle, generation = queue.popleft()

        # Skip if already visited
        if current_handle in visited:
            continue

        visited.add(current_handle)

        # Yield if within generation range
        if (generation >= min_generation or (inclusive and generation == 0)) and (
            max_generation is None or generation <= max_generation
        ):
            yield current_handle, generation

        # Stop if we've reached max_generation
        if max_generation is not None and generation >= max_generation:
            continue

        # Get person and their families
        try:
            person = db.get_person_from_handle(current_handle)
            if not person:
                continue
        except:
            # Handle non-existent handles gracefully
            continue

        # Determine which families to process
        families = person.family_list
        if not include_all_families and families:
            families = [families[0]]  # Only first family

        # Process each family
        for family_handle in families:
            family = db.get_family_from_handle(family_handle)
            if not family:
                continue

            # Add children to queue
            for child_ref in family.child_ref_list:
                if child_ref.ref:
                    queue.append((child_ref.ref, generation + 1))
