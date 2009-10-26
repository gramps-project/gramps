#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Benny Malengier
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

# $Id: $

#------------------------------------------------------------------------
#
# EniroMaps
#
#------------------------------------------------------------------------

register(MAPSERVICE, 
id    = 'EniroMaps',
name  = _("EniroMaps"),
description =  _("Opens on kartor.eniro.se"),
version = '1.0',
status = STABLE,
fname = 'eniroswedenmap.py',
authors = ["Peter Landgren"],
authors_email = ["peter.talken@telia.com"],
mapservice = 'EniroSVMapService'
  )

#------------------------------------------------------------------------
#
# GoogleMaps
#
#------------------------------------------------------------------------

register(MAPSERVICE, 
id    = 'GoogleMaps',
name  = _("GoogleMaps"),
description =  _("Open on maps.google.com"),
version = '1.0',
status = STABLE,
fname = 'googlemap.py',
authors = ["Benny Malengier"],
authors_email = ["benny.malengier@gramps-project.org"],
mapservice = 'GoogleMapService'
  )

#------------------------------------------------------------------------
#
# OpenStreetMap
#
#------------------------------------------------------------------------

register(MAPSERVICE, 
id    = 'OpenStreetMap',
name  = _("OpenStreetMap"),
description =  _("Open on openstreetmap.org"),
version = '1.0',
status = STABLE,
fname = 'openstreetmap.py',
authors = ["Benny Malengier"],
authors_email = ["benny.malengier@gramps-project.org"],
mapservice = 'OpensStreetMapService'
  )
