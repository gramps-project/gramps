# encoding:utf-8
#
# Copyright (C) 2015 Christian Schulze
#

#------------------------------------------------------------------------
#
# Geography view
#
#------------------------------------------------------------------------

MODULE_VERSION="5.1" 

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
