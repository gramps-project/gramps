# encoding:utf-8
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2015 Christian Schulze
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

#------------------------------------------------------------------------
#
# Geography view
#
#------------------------------------------------------------------------

MODULE_VERSION="4.2" 

from gi import Repository

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger("Geography")

# Attempting to import OsmGpsMap gives an error dialog if OsmGpsMap is not
# available so test first and log just a warning to the console instead.
    # Load the view only if osmgpsmap library is present.
register(VIEW, 
             id    = 'geoIDplaceCoordinateGramplet',
             name  = _("Place Coordinate Gramplet view"),
             description =  _("View for the place coordinate gramplet."),
             version = '1.0',
             gramps_target_version = MODULE_VERSION,
             status = STABLE,
             fname = 'PlaceCoordinateGeoView.py',
             authors = ["Christian Schulze"],
             authors_email = [""],
             category = ("Geography", _("Geography")),
             viewclass = 'PlaceCoordinateGeoView',
             #order = START,
             stock_icon = 'geo-place-add',
      )
