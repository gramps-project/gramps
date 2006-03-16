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

# $Id$

import gtk
import const

try:
    from gnomevfs import mime_get_short_list_applications, \
         mime_get_description, get_mime_type
except:
    from gnome.vfs import mime_get_short_list_applications, \
         mime_get_description, get_mime_type
    
from TransUtils import sgettext as _

def get_application(type):
    """Returns the application command and application name of the
    specified mime type"""
    try:
        applist = mime_get_short_list_applications(type)
        if applist:
            prog = applist[0]
            return (prog[2],prog[1])
        else:
            return None
    except:
        return None

def get_description(type):
    """Returns the description of the specfied mime type"""
    try:
        return mime_get_description(type)
    except:
        return _("unknown")

def get_type(file):
    """Returns the mime type of the specified file"""
    try:
        return get_mime_type(file)
    except:
        return _('unknown')

def mime_type_is_defined(type):
    """
    Return True if a description for a mime type exists.
    """
    try:
        mime_get_description(type)
        return True
    except:
        return False

_icon_theme = gtk.icon_theme_get_default()

def find_mime_type_pixbuf(mime_type):
    try:
        icontmp = mime_type.replace('/','-')
        newicon = "gnome-mime-%s" % icontmp
        try:
            return _icon_theme.load_icon(newicon,48,0)
        except:
            icontmp = mime_type.split('/')[0]
            try:
                newicon = "gnome-mime-%s" % icontmp
                return _icon_theme.load_icon(newicon,48,0)
            except:
                return gtk.gdk.pixbuf_new_from_file(const.icon)
    except:
        return gtk.gdk.pixbuf_new_from_file(const.icon)
    
