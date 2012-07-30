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

MODULE_VERSION="4.0" 

try :
    NEWGTK = False
    from gi.repository import Gtk
    if Gtk.get_major_version() >= 3:
        OSMGPSMAP = False
        NEWGTK = True
    if not NEWGTK:
        # current osmgpsmap does not support GTK3
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
    import logging
    logging.warning(_("WARNING: osmgpsmap module not loaded. "
                      "Geography functionality will not be available."))

if OSMGPSMAP:
    # Load the view only if osmgpsmap library is present.
    register(VIEW, 
             id    = 'geo1',
             name  = _("All known places for one Person"),
             description =  _("A view showing the places visited by "
                              "one person during his life."),
             version = '1.0',
             gramps_target_version = MODULE_VERSION,
             status = STABLE,
             fname = 'geoperson.py',
             authors = [u"Serge Noiraud"],
             authors_email = [""],
             category = ("Geography", _("Geography")),
             viewclass = 'GeoPerson',
             #order = START,
             stock_icon = 'geo-show-person',
      )
    
    register(VIEW, 
             id    = 'geo2',
             name  = _("All known places for one Family"),
             description =  _("A view showing the places visited by "
                              "one family during all their life."),
             version = '1.0',
             gramps_target_version = MODULE_VERSION,
             status = STABLE,
             fname = 'geofamily.py',
             authors = [u"Serge Noiraud"],
             authors_email = [""],
             category = ("Geography", _("Geography")),
             viewclass = 'GeoFamily',
             #order = START,
             stock_icon = 'geo-show-family',
      )
    
    register(VIEW, 
             id    = 'geo3',
             name  = _("All displacements for one person and their descendants"),
             description =  _("A view showing all the places visited by "
                              "all persons during their life."
                              "\nThis is for one person and their descendant."
                              "\nYou can see the dates corresponding to the period."),
             version = '1.0',
             gramps_target_version = MODULE_VERSION,
             status = STABLE,
             fname = 'geomoves.py',
             authors = [u"Serge Noiraud"],
             authors_email = [""],
             category = ("Geography", _("Geography")),
             viewclass = 'GeoMoves',
             #order = START,
             stock_icon = 'geo-show-family',
      )

    register(VIEW, 
             id    = 'geo4',
             name  = _("Have these two families been able to meet?"),
             description =  _("A view showing the places visited by "
                              "all family's members during their life: "
                              "have these two people been able to meet?"),
             version = '1.0.1',
             gramps_target_version = MODULE_VERSION,
             status = STABLE,
             fname = 'geofamclose.py',
             authors = [u"Serge Noiraud"],
             authors_email = [""],
             category = ("Geography", _("Geography")),
             viewclass = 'GeoFamClose',
             #order = START,
             stock_icon = 'geo-show-family',
      )
    
    register(VIEW, 
             id    = 'geo5',
             name  = _("Have they been able to meet?"),
             description =  _("A view showing the places visited by "
                              "two persons during their life: "
                              "have these two people been able to meet?"),
             version = '1.0.1',
             gramps_target_version = MODULE_VERSION,
             status = STABLE,
             fname = 'geoclose.py',
             authors = [u"Serge Noiraud"],
             authors_email = [""],
             category = ("Geography", _("Geography")),
             viewclass = 'GeoClose',
             #order = START,
             stock_icon = 'gramps-relation',
      )
    
    register(VIEW, 
             id    = 'geo6',
             name  = _("All known Places"),
             description =  _("A view showing all places of the database."),
             version = '1.0',
             gramps_target_version = MODULE_VERSION,
             status = STABLE,
             fname = 'geoplaces.py',
             authors = [u"Serge Noiraud"],
             authors_email = [""],
             category = ("Geography", _("Geography")),
             viewclass = 'GeoPlaces',
             #order = START,
             stock_icon = 'geo-show-place',
      )
    
    register(VIEW, 
             id    = 'geo7',
             name  = _("All places related to Events"),
             description =  _("A view showing all the event "
                              "places of the database."),
             version = '1.0',
             gramps_target_version = MODULE_VERSION,
             status = STABLE,
             fname = 'geoevents.py',
             authors = [u"Serge Noiraud"],
             authors_email = [""],
             category = ("Geography", _("Geography")),
             viewclass = 'GeoEvents',
             #order = START,
             stock_icon = 'geo-show-event',
      )
    
