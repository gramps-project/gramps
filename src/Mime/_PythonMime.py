#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

import mimetypes
import const
import gtk
from gettext import gettext as _

_type_map = {
    'application/x-gramps' : 'GRAMPS database',
    'application/x-gramps-xml' : 'GRAMPS XML database',
    'application/x-gedcom' : 'GEDCOM database',
    'application/x-gramps-package': 'GRAMPS package',
    'image/jpeg' : 'JPEG image',
    'application/pdf' : 'PDF document',
    'text/rtf' : 'Rich Text File',
}

mimetypes.add_type('application/x-gramps','.grdb')
mimetypes.add_type('application/x-gramps','.GRDB')
mimetypes.add_type('application/x-gramps-xml','.gramps')
mimetypes.add_type('application/x-gramps-xml','.GRAMPS')
mimetypes.add_type('application/x-gedcom','.ged')
mimetypes.add_type('application/x-gedcom','.GED')

def get_application(mime_type):
    """Returns the application command and application name of the
    specified mime type"""
    return None

def get_description(mime_type):
    """Returns the description of the specfied mime type"""
    return _type_map.get(mime_type,_("unknown"))

def get_type(filename):
    """Returns the mime type of the specified file"""
    value = mimetypes.guess_type(filename)
    if value:
        return value[0]
    else:
        return _('unknown')
    
def mime_type_is_defined(mime_type):
    """
    Return True if a description for a mime type exists.
    """
    return _type_map.has_key(mime_type)

def find_mime_type_pixbuf(mime_type):
    return gtk.gdk.pixbuf_new_from_file(const.icon)
