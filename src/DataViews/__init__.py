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

# $Id$

"""
Package init for the DataViews package.
"""

from GrampletView import GrampletView, register, Gramplet
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

geopresent = True
try:
    from GeoView import HtmlView, GeoView
except:
    geopresent = False

try:
    import Config
    dv = Config.get(Config.DATA_VIEWS)
    #remove GeoView so we do not try to eval it if import fails
    if not geopresent and not dv.find('GeoView') == -1:
        dv = dv.replace('GeoView','').replace(',,',',')
    DATA_VIEWS = eval("["+dv+"]")
    #add or remove GeoView if config says so
    if geopresent and Config.get(Config.GEOVIEW) and \
                not GeoView in DATA_VIEWS:
        DATA_VIEWS.append(GeoView)
        Config.set(Config.DATA_VIEWS,
                Config.get(Config.DATA_VIEWS)+",GeoView")
    elif geopresent and not Config.get(Config.GEOVIEW) and \
                GeoView in DATA_VIEWS:
        DATA_VIEWS.remove(GeoView)
        newval = Config.get(Config.DATA_VIEWS).replace('GeoView','')\
                                                .replace(',,',',')
        if newval[-1] == ',':
            newval = newval[:-1]
        Config.set(Config.DATA_VIEWS, newval)
except AttributeError:
    # Fallback if bad config line, or if no Config system
    DATA_VIEWS = [
        GrampletView,
        PersonView,
        RelationshipView,
        FamilyListView,
        PedigreeView,
        EventView,
        SourceView,
        PlaceView,
        MediaView,
        RepositoryView,
        NoteView,
        ]
    if geopresent:
       DATA_VIEWS.append(GeoView)

def get_views():
    """
    Return a list of PageView instances, in order
    """
    return DATA_VIEWS
