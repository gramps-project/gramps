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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

#------------------------------------------------------------------------
#
# Geography view
#
#------------------------------------------------------------------------

MODULE_VERSION="5.0"

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
OSMGPSMAP = False
repository = Repository.get_default()
if repository.enumerate_versions("OsmGpsMap"):
    try :
        # current osmgpsmap support GTK3
        import gi
        gi.require_version('OsmGpsMap', '1.0')
        from gi.repository import OsmGpsMap as osmgpsmap
        OSMGPSMAP = True
    except:
        pass

if not OSMGPSMAP:
    from gramps.gen.config import config
    if not config.get('interface.ignore-osmgpsmap'):
        from gramps.gen.constfunc import has_display
        if has_display():
            from gramps.gui.dialog import MessageHideDialog
            from gramps.gen.const import URL_WIKISTRING
            osmgps_dict = { 'gramps_wiki_build_osmgps_url' :
                                URL_WIKISTRING +
                                    "GEPS_029:_GTK3-GObject_introspection"
                                    "_Conversion#OsmGpsMap_for_Geography" }
            title = _("OsmGpsMap module not loaded.")
            message = _("Geography functionality will not be available.\n"
                       "To build it for Gramps see "
                       "%(gramps_wiki_build_osmgps_url)s") % osmgps_dict
            MessageHideDialog(title, message, 'interface.ignore-osmgpsmap')
else:
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
             authors = ["Serge Noiraud"],
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
             authors = ["Serge Noiraud"],
             authors_email = [""],
             category = ("Geography", _("Geography")),
             viewclass = 'GeoFamily',
             #order = START,
             stock_icon = 'geo-show-family',
      )

    register(VIEW,
             id    = 'geo3',
             name  = _("Every residence or move for a person and any descendants"),
             description =  _("A view showing all the places visited by "
                              "all persons during their life."
                              "\nThis is for a person and any descendant."
                              "\nYou can see the dates corresponding to the period."),
             version = '1.0',
             gramps_target_version = MODULE_VERSION,
             status = STABLE,
             fname = 'geomoves.py',
             authors = ["Serge Noiraud"],
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
             authors = ["Serge Noiraud"],
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
             authors = ["Serge Noiraud"],
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
             authors = ["Serge Noiraud"],
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
             authors = ["Serge Noiraud"],
             authors_email = [""],
             category = ("Geography", _("Geography")),
             viewclass = 'GeoEvents',
             #order = START,
             stock_icon = 'geo-show-event',
      )

