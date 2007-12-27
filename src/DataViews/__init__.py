# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2005  Donald N. Allingham
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

# $Id: __init__.py 6067 2006-03-04 05:24:16Z dallingham $

"""
Package init for the DataView package
"""

__author__ = "Don Allingham"
__revision__ = "$Revision: $"

from MyGrampsView import MyGrampsView, register, Gadget
from PersonView import PersonView
from RelationView import RelationshipView
from FamilyList import FamilyListView
from PedigreeView import PedigreeView
from EventView import EventView
from SourceView import SourceView
from PlaceView import PlaceView
from MediaView import MediaView
from RepositoryView import RepositoryView
from NoteView import NoteView

try:
    import Config
    DATA_VIEWS = eval("["+Config.get(Config.DATA_VIEWS)+"]")
except:
    # Fallback if bad config line, or if no Config system
    print "Ignoring malformed 'data-views' entry"
    DATA_VIEWS = [
        #MyGrampsView,
        PersonView,
        RelationshipView,
        FamilyListView,
        PedigreeView,
        EventView,
        SourceView,
        PlaceView,
        MediaView,
        #MapView,
        RepositoryView,
        NoteView,
        ]

def get_views():
    """
    Returns a list of PageView instances, in order
    """
    return DATA_VIEWS
