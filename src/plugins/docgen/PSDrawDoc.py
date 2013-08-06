#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013 Vassilii Khachaturov
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

"""PS output generator based on Cairo.
"""

import sys
import cairo
from _cairodoc import CairoDocgen

class PSDrawDoc(CairoDocgen):
    """Render the document into PS file using Cairo.
    """
    EXT = 'ps'
    def create_cairo_surface(self, fobj, width_in_points, height_in_points):
        return cairo.PSSurface(fobj, width_in_points, height_in_points)
