#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012       Benny Malengier
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

# $Id: grampsapp.py -1   $

"""
This is a stub to start Gramps. It is provided for the sole reason of being
able to run gramps from the source directory without setting PYTHONPATH

From this position, import gramps works great
"""

# here import gramps works. As __temporary__ workaround, we also put the gramps
# folder itself on the systempath
import sys, os
pathgramps = os.path.dirname(os.path.abspath(__file__))
pathgramps += os.sep + 'gramps'
sys.path.append(pathgramps)

#now start gramps
import gramps.grampsapp as app
app.main()
