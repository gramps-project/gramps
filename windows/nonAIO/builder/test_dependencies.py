#
# Gramps - a GTK+ based genealogy program
#
# Copyright (C) 2009 Stephen George
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
# $Id:  $

import sys

py_str = 'found %d.%d.%d' %  sys.version_info[:3]

try:
    import gtk
    try:
        gtkver_str = 'found %d.%d.%d' % Gtk.gtk_version 
    except : # any failure to 'get' the version
        gtkver_str = 'unknown version'
    try:
        pygtkver_str = 'found %d.%d.%d' % Gtk.pygtk_version
    except :# any failure to 'get' the version
        pygtkver_str = 'unknown version'
except ImportError:
    gtkver_str = 'not found'
    pygtkver_str = 'not found'
#exept TypeError: To handle back formatting on version split

try:
    import gobject
    try:
        gobjectver_str = 'found %d.%d.%d' % GObject.pygobject_version
    except :# any failure to 'get' the version
        gobjectver_str = 'unknown version'
    
except ImportError:
    gobjectver_str = 'not found'


try:
    import cairo
    try:
        cairover_str = 'found %d.%d.%d' % cairo.version_info 
    except :# any failure to 'get' the version
        cairover_str = 'unknown version'
    
except ImportError:
    cairover_str = 'not found'
    
print 'python:%s;'%py_str
print 'gtk++:%s;'%gtkver_str
print 'pygtk:%s;'%pygtkver_str
print 'gobject:%s;'%gobjectver_str
print 'cairo:%s;'%cairover_str