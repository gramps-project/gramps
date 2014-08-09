#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008       Steve Hall
# Copyright (C) 2008       Stephen George
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
import sys

fn = sys.argv[1]
f = open(fn,"w")

f.write('[tests]\n')

try:
    from gi.repository import Gtk
    f.write('gtk=yes\n')
    f.write('gtkver=%d.%d.%d\n' % Gtk.gtk_version)
    f.write('pygtk=yes\n')
    f.write('pygtkver=%d.%d.%d\n' % Gtk.pygtk_version)
except ImportError:
    f.write('gtk=no\n')
    f.write('gtkver=no\n')
    f.write('pygtk=no\n')
    f.write('pygtkver=no\n')

try:
    import cairo
    f.write('pycairo=yes\n')
    #f.write('pycairover=%s\n' % cairo.version_info)
    f.write('pycairover=%s\n' % str(cairo.version_info) )
except ImportError:
    f.write('pycairo=no\n')
    f.write('pycairover=no\n')
f.close()

