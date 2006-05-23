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

from _PersonView import PersonView
from _RelationView import RelationshipView
from _FamilyList import FamilyListView
from _PedigreeView import PedigreeView
from _EventView import EventView
from _SourceView import SourceView
from _PlaceView import PlaceView
from _MediaView import MediaView
from _MapView import MapView
from _RepositoryView import RepositoryView

def get_views():
    return [PersonView, RelationshipView, FamilyListView, PedigreeView,
            EventView, SourceView, PlaceView, MediaView,
            MapView, RepositoryView]
