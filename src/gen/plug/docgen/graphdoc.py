#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2002       Gary Shao
# Copyright (C) 2007       Brian G. Matherly
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2009       Gary Burton
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

# $Id: basedoc.py 12591 2009-05-29 22:25:44Z bmcage $


#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------


#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".graphdoc")

#-------------------------------------------------------------------------------
#
# GVDoc
#
#-------------------------------------------------------------------------------
class GVDoc(object):
    """
    Abstract Interface for Graphviz document generators. Output formats
    for Graphviz reports must implement this interface to be used by the
    report system.
    """
    def add_node(self, node_id, label, shape="", color="", 
                 style="", fillcolor="", url="", htmloutput=False):
        """
        Add a node to this graph. Nodes can be different shapes like boxes and
        circles.
        
        @param node_id: A unique identification value for this node.
            Example: "p55"
        @type node_id: string
        @param label: The text to be displayed in the node.
            Example: "John Smith"
        @type label: string
        @param shape: The shape for the node.
            Examples: "box", "ellipse", "circle"
        @type shape: string
        @param color: The color of the node line.
            Examples: "blue", "lightyellow"
        @type color: string
        @param style: The style of the node.
        @type style: string
        @param fillcolor: The fill color for the node.
            Examples: "blue", "lightyellow"
        @type fillcolor: string
        @param url: A URL for the node.
        @type url: string
        @param htmloutput: Whether the label contains HTML.
        @type htmloutput: boolean
        @return: nothing
        """
        raise NotImplementedError

    def add_link(self, id1, id2, style="", head="", tail="", comment=""):
        """
        Add a link between two nodes.
        
        @param id1: The unique identifier of the starting node.
            Example: "p55"
        @type id1: string
        @param id2: The unique identifier of the ending node.
            Example: "p55"
        @type id2: string
        @param comment: A text string displayed at the end of the link line.
            Example: "person C is the son of person A and person B"
        @type comment: string
        @return: nothing
        """
        raise NotImplementedError

    def add_comment(self, comment):
        """
        Add a comment to the source file.

        @param comment: A text string to add as a comment.
            Example: "Next comes the individuals."
        @type comment: string
        @return: nothing
        """
        raise NotImplementedError

    def start_subgraph(self, graph_id):
        """
        Start a subgraph in this graph.
        
        @param id: The unique identifier of the subgraph.
            Example: "p55"
        @type id1: string
        @return: nothing
        """
        raise NotImplementedError

    def end_subgraph(self):
        """
        End a subgraph that was previously started in this graph.

        @return: nothing
        """
        raise NotImplementedError
