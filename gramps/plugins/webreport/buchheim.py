# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007       Johan Gonqvist <johan.gronqvist@gmail.com>
# Copyright (C) 2007-2009  Gary Burton <gary.burton@zen.co.uk>
# Copyright (C) 2007-2009  Stephane Charette <stephanecharette@gmail.com>
# Copyright (C) 2008-2009  Brian G. Matherly
# Copyright (C) 2008       Jason M. Simanek <jason@bohemianalps.com>
# Copyright (C) 2008-2011  Rob G. Healey <robhealey1@gmail.com>
# Copyright (C) 2010       Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2010,2015  Serge Noiraud
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2013       Benny Malengier
# Copyright (C) 2018       Paul D.Smith
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

import logging

from gramps.gen.const import GRAMPS_LOCALE as glocale

LOG = logging.getLogger(".NarrativeWeb.BuchheimTree")

_ = glocale.translation.sgettext


# ------------------------------------------------------------
#
# DrawTree - a Buchheim draw tree which implements the
#   tree drawing algorithm of:
#
#   Improving Walker's algorithm to Run in Linear Time
#   Christoph Buchheim, Michael Juenger, and Sebastian Leipert
#
#   Also see:
#
#   Positioning Nodes for General Trees
#   John Q. Walker II
#
# The following modifications are noted:
#
# - The root node is 'west' according to the later nomenclature
#   employed by Walker with the nodes stretching 'east'
# - This reverses the X & Y co-originates of the Buchheim paper
# - The algorithm has been tweaked to track the maximum X and Y
#   as 'width' and 'height' to aid later layout
# - The Buchheim examples track a string identifying the actual
#   node but this implementation tracks the handle of the
#   DB node identifying the person in the Gramps DB.  This is done
#   to minimize occupancy at any one time.
# ------------------------------------------------------------
class DrawTree(object):
    def __init__(self, tree, parent=None, depth=0, number=1):
        self.coord_x = -1.0
        self.coord_y = depth
        self.width = self.coord_x
        self.height = self.coord_y
        self.tree = tree
        self.children = [
            DrawTree(c, self, depth + 1, i + 1) for i, c in enumerate(tree.children)
        ]
        self.parent = parent
        self.thread = None
        self.mod = 0
        self.ancestor = self
        self.change = self.shift = 0
        self._lmost_sibling = None
        # this is the number of the node in its group of siblings 1..n
        self.number = number

    def left(self):
        """
        Return the left most child if it exists.
        """
        return self.thread or len(self.children) and self.children[0]

    def right(self):
        """
        Return the rightmost child if it exists.
        """
        return self.thread or len(self.children) and self.children[-1]

    def lbrother(self):
        """
        Return the sibling to the left of this one.
        """
        brother = None
        if self.parent:
            for node in self.parent.children:
                if node == self:
                    return brother
                else:
                    brother = node
        return brother

    def get_lmost_sibling(self):
        """
        Return the leftmost sibling.
        """
        if not self._lmost_sibling and self.parent and self != self.parent.children[0]:
            self._lmost_sibling = self.parent.children[0]
        return self._lmost_sibling

    lmost_sibling = property(get_lmost_sibling)

    def __str__(self):
        return "%s: x=%s mod=%s" % (self.tree, self.coord_x, self.mod)

    def __repr__(self):
        return self.__str__()

    def handle(self):
        """
        Return the handle of the tree, which is whatever we stored as
        in the tree to reference out data.
        """
        return self.tree.handle


def buchheim(tree, node_width, h_separation, node_height, v_separation):
    """
    Calculate the position of elements of the graph given a minimum
    generation width separation and minimum generation height separation.
    """
    draw_tree = firstwalk(DrawTree(tree), node_height, v_separation)
    min_x = second_walk(draw_tree, 0, node_width + h_separation, 0)
    if min_x < 0:
        third_walk(draw_tree, 0 - min_x)
    top = get_min_coord_y(draw_tree)
    height = get_max_coord_y(draw_tree)

    return (draw_tree, top, height)


def get_min_coord_y(tree, min_value=100.0):
    """Get the minimum coord_y"""
    if tree.coord_y < min_value:
        min_value = tree.coord_y
    for child in tree.children:
        min_v = get_min_coord_y(child, min_value)
        if min_value > min_v:
            min_value = min_v
    return min_value


def get_max_coord_y(tree, max_value=0.0):
    """Get the maximum coord_y"""
    if tree.coord_y > max_value:
        max_value = tree.coord_y
    for child in tree.children:
        max_v = get_max_coord_y(child, max_value)
        if max_value < max_v:
            max_value = max_v
    return max_value


def third_walk(tree, adjust):
    """
    The tree has have wandered into 'negative' co-ordinates so bring it back
    into the piositive domain.
    """
    tree.coord_x += adjust
    tree.width = max(tree.width, tree.coord_x)
    for child in tree.children:
        third_walk(child, adjust)


def firstwalk(tree, node_height, v_separation):
    """
    Determine horizontal positions.
    """
    if not tree.children:
        if tree.lmost_sibling:
            tree.coord_y = tree.lbrother().coord_y + node_height + v_separation
        else:
            tree.coord_y = 0.0
    else:
        default_ancestor = tree.children[0]
        for child in tree.children:
            firstwalk(child, node_height, v_separation)
            default_ancestor = apportion(
                child, default_ancestor, node_height + v_separation
            )
            tree.height = max(tree.height, child.height)
            assert tree.width >= child.width
        execute_shifts(tree)

        midpoint = (tree.children[0].coord_y + tree.children[-1].coord_y) / 2

        brother = tree.lbrother()
        if brother:
            tree.coord_y = brother.coord_y + node_height + v_separation
            tree.mod = tree.coord_y - midpoint
        else:
            tree.coord_y = midpoint

    assert tree.width >= tree.coord_x
    tree.height = max(tree.height, tree.coord_y)
    return tree


def apportion(tree, default_ancestor, v_separation):
    """
    Figure out relative positions of node in a tree.
    """
    brother = tree.lbrother()
    if brother is not None:
        # in buchheim notation:
        # i == inner; o == outer; r == right; l == left; r = +; l = -
        vir = vor = tree
        vil = brother
        vol = tree.lmost_sibling
        sir = sor = tree.mod
        sil = vil.mod
        sol = vol.mod
        while vil.right() and vir.left():
            vil = vil.right()
            vir = vir.left()
            vol = vol.left()
            vor = vor.right()
            vor.ancestor = tree
            shift = (vil.coord_y + sil) - (vir.coord_y + sir) + v_separation
            if shift > 0:
                move_subtree(ancestor(vil, tree, default_ancestor), tree, shift)
                sir = sir + shift
                sor = sor + shift
            sil += vil.mod
            sir += vir.mod
            sol += vol.mod
            sor += vor.mod
        if vil.right() and not vor.right():
            vor.thread = vil.right()
            vor.mod += sil - sor
        else:
            if vir.left() and not vol.left():
                vol.thread = vir.left()
                vol.mod += sir - sol
            default_ancestor = tree
    return default_ancestor


def move_subtree(walk_l, walk_r, shift):
    """
    Determine possible shifts required to accomodate new node, but don't
    perform the shifts yet.
    """
    subtrees = walk_r.number - walk_l.number
    # print wl.tree, "is conflicted with", wr.tree, 'moving',
    # subtrees, 'shift', shift
    # print wl, wr, wr.number, wl.number, shift, subtrees, shift/subtrees
    walk_r.change -= shift / subtrees
    walk_r.shift += shift
    walk_l.change += shift / subtrees
    walk_r.coord_y += shift
    walk_r.mod += shift
    walk_r.height = max(walk_r.height, walk_r.coord_y)


def execute_shifts(tree):
    """
    Shift a tree, and it's subtrees, to allow for the placement of a
    new tree.
    """
    shift = change = 0
    for child in tree.children[::-1]:
        # print "shift:", child, shift, child.change
        child.coord_y += shift
        child.mod += shift
        change += child.change
        shift += child.shift + change
        child.height = max(child.height, child.coord_y)
        tree.height = max(tree.height, child.height)


def ancestor(vil, tree, default_ancestor):
    """
    The relevant text is at the bottom of page 7 of
    Improving Walker's Algorithm to Run in Linear Time" by Buchheim et al
    """
    if vil.ancestor in tree.parent.children:
        return vil.ancestor

    return default_ancestor


def second_walk(tree, modifier=0, h_separation=0, width=0, min_x=None):
    """
    Note that some of this code is modified to orientate the root node 'west'
    instead of 'north' in the Bushheim algorithms.
    """
    tree.coord_y += modifier
    tree.coord_x += width

    if min_x is None or tree.coord_x < min_x:
        min_x = tree.coord_x

    for child in tree.children:
        min_x = second_walk(
            child, modifier + tree.mod, h_separation, width + h_separation, min_x
        )
        tree.width = max(tree.width, child.width)
        tree.height = max(tree.height, child.height)

    tree.width = max(tree.width, tree.coord_x)
    tree.height = max(tree.height, tree.coord_y)
    return min_x
