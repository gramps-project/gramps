#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013-2014  Nick Hall
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""
Location utility functions
"""

#-------------------------------------------------------------------------
#
# get_location_list
#
#-------------------------------------------------------------------------
def get_location_list(db, place):
    """
    Return a list of place names for display.
    """
    visited = [place.handle]
    lines = [place.name]
    while len(place.get_placeref_list()) > 0:
        handle = place.get_placeref_list()[0].ref
        if handle in visited:
            break
        else:
            visited.append(handle)
        place = db.get_place_from_handle(handle)
        lines.append(place.name)
    return lines

#-------------------------------------------------------------------------
#
# get_main_location
#
#-------------------------------------------------------------------------
def get_main_location(db, place):
    """
    Find all places in the hierarchy above the given place, and return the
    result as a dictionary of place types and names.
    """
    visited = [place.handle]
    items = {int(place.get_type()): place.name}
    while len(place.get_placeref_list()) > 0:
        handle = place.get_placeref_list()[0].ref
        if handle in visited:
            break
        else:
            visited.append(handle)
        place = db.get_place_from_handle(handle)
        items[int(place.get_type())] = place.name
    return items
    
#-------------------------------------------------------------------------
#
# get_locations
#
#-------------------------------------------------------------------------
def get_locations(db, place):
    """
    Determine each possible route up the place hierarchy, and return a list
    containing dictionaries of place types and names.
    """
    locations = []
    todo = [(place, [(int(place.get_type()), place.get_all_names())],
            [place.handle])]
    while len(todo):
        place, tree, visited = todo.pop()
        for parent in place.get_placeref_list():
            if parent.ref not in visited:
                parent_place = db.get_place_from_handle(parent.ref)
                parent_tree = tree + [(int(parent_place.get_type()), 
                                       parent_place.get_all_names())]
                parent_visited = visited + [parent.ref]
                todo.append((parent_place, parent_tree, parent_visited))
        if len(place.get_placeref_list()) == 0:
            locations.append(dict(tree))
    return locations
