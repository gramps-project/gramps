# encoding:utf-8
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011 Serge Noiraud
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

#------------------------------------------------------------------------
#
# Geography view
#
#------------------------------------------------------------------------

try :
    import osmgpsmap
    OSMGPSMAP = True
    if osmgpsmap.__version__ < '0.7.0':
        OSMGPSMAP = False
        import logging
        logging.warning( _("WARNING: osmgpsmap module not loaded. "
                           "osmgpsmap must be >= 0.7.0. yours is %s") %
                        osmgpsmap.__version__)
except:
    OSMGPSMAP = False
    import config
    if not config.get('interface.ignore-osmgpsmap'):
        from QuestionDialog import MessageHideDialog
        title = _("OsmGpsMap module not loaded.")
        message = _("Geography functionality will not be available.")
        MessageHideDialog(title, message, 'interface.ignore-osmgpsmap')

if OSMGPSMAP:
    # Load the view only if osmgpsmap library is present.
    register(VIEW, 
             id    = 'personmap',
             name  = _("Person"),
             description =  _("A view showing the places visited by "
                              "one person during his life."),
             version = '1.0',
             gramps_target_version = '3.4',
             status = STABLE,
             fname = 'geoperson.py',
             authors = [u"Serge Noiraud"],
             authors_email = [""],
             category = ("Geography", _("Geography")),
             viewclass = 'GeoPerson',
             order = START,
             stock_icon = 'geo-show-person',
      )
    
    register(VIEW, 
             id    = 'placesmap',
             name  = _("Places"),
             description =  _("A view showing all places of the database."),
             version = '1.0',
             gramps_target_version = '3.4',
             status = STABLE,
             fname = 'geoplaces.py',
             authors = [u"Serge Noiraud"],
             authors_email = [""],
             category = ("Geography", _("Geography")),
             viewclass = 'GeoPlaces',
             stock_icon = 'geo-show-place',
      )
    
    register(VIEW, 
             id    = 'eventsmap',
             name  = _("Events"),
             description =  _("A view showing all the event "
                              "places of the database."),
             version = '1.0',
             gramps_target_version = '3.4',
             status = STABLE,
             fname = 'geoevents.py',
             authors = [u"Serge Noiraud"],
             authors_email = [""],
             category = ("Geography", _("Geography")),
             viewclass = 'GeoEvents',
             stock_icon = 'geo-show-event',
      )
    
    register(VIEW, 
             id    = 'familymap',
             name  = _("Family"),
             description =  _("A view showing the places visited by "
                              "one family during all their life."),
             version = '1.0',
             gramps_target_version = '3.4',
             status = STABLE,
             order = START,
             fname = 'geofamily.py',
             authors = [u"Serge Noiraud"],
             authors_email = [""],
             category = ("Geography", _("Geography")),
             viewclass = 'GeoFamily',
             stock_icon = 'geo-show-family',
      )
    
