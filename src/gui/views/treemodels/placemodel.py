#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009    Nick Hall
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
# $Id:_PlaceModel.py 9912 2008-01-22 09:17:46Z acraphae $

"""
Place Model.
"""
#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger(".gui.views.treemodels.placemodel")

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gui.views.treemodels.placebasemodel import PlaceBaseModel
from gui.views.treemodels.flatbasemodel import FlatBaseModel

#-------------------------------------------------------------------------
#
# PlaceModel
#
#-------------------------------------------------------------------------
class PlaceModel(PlaceBaseModel, FlatBaseModel):
    """
    Flat place model.  (Original code in PlaceBaseModel).
    """
    def __init__(self, db, scol=0, order=gtk.SORT_ASCENDING, search=None,
                 skip=set(), sort_map=None):

        PlaceBaseModel.__init__(self, db)
        FlatBaseModel.__init__(self, db, scol, order, tooltip_column=13,
                           search=search, skip=skip, sort_map=sort_map)
