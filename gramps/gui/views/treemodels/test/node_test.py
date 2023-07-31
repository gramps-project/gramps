#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

import unittest
from ..treebasemodel import Node, NodeMap


class NodeTest(unittest.TestCase):
    def test_addremovechildren(self):
        n = Node("1", "", "key_to_sort_on", None, None)
        nm = NodeMap()
        nm.add_node(n)

        n2 = Node("2", "", "key_to_sort_on2", None, None)
        n.add_child(n2, nm)
        nm.add_node(n2)

        n3 = Node("2", "", "", None, None)
        n.add_child(n3, nm)
        nm.add_node(n3)

        n.remove_child(n3, nm)
        nm.del_node(n3)
        n.remove_child(n2, nm)
        nm.del_node(n2)
        self.assertEqual(len(n.children), 0)


if __name__ == "__main__":
    unittest.main()
