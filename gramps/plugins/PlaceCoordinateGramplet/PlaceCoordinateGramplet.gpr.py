#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2020 Christian Schulze
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

#------------------------------------------------------------------------
#
# Register Gramplet
#
#------------------------------------------------------------------------
register(GRAMPLET,
         id="Place Coordinates",
         name=_("Place Coordinates"),
         description=_(
             "Gramplet that simplifies setting the coordinates of a place"),
         version='1.1.0',
         gramps_target_version="5.1",
         status=STABLE,
         fname="PlaceCoordinateGramplet.py",
         height=280,
         gramplet='PlaceCoordinateGramplet',
         gramplet_title=_("Place Coordinates"),
         navtypes=["Place"],
         )
