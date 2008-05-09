#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  The Gramps Developers
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

"""Custom widgets."""

from grampswidgets import *
from multitypecomboentry import MultiTypeComboEntry
from toolbarwidgets import *
from styledtextbuffer import *
from styledtexteditor import *

from gtk.glade import set_custom_handler

def get_custom_handler(glade, function_name, widget_name, 
                       str1, str2, int1, int2):
    if function_name == 'ValidatableMaskedEntry':
        return ValidatableMaskedEntry()
    if function_name == 'StyledTextEditor':
        return StyledTextEditor()

set_custom_handler(get_custom_handler)
