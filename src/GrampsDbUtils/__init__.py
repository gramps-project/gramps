#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006 Donald N. Allingham
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

"""
This package implements additions to the the GrampsDb database. 

This package should be used for code that extended GrampsDb but also 
depends on Gtk.

A number of importers and exporters are provided to convert between
the different backend formats.

To obtain a class that implements writers use the gramps_db_writer_factory
method and for readers use the gramps_db_reader_factory method. For information
on using these factories see the _GrampsDbUtilsFactories.py file comments.

"""


from _GrampsDbWRFactories import \
     gramps_db_writer_factory, \
     gramps_db_reader_factory
     

from _ReadGedcom import GedcomParser
from _WriteGedcom import GedcomWriter

from _WriteXML import XmlWriter

