#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
import os

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
from QuestionDialog import ErrorDialog, WarningDialog

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import const
from TransUtils import sgettext as _

#-------------------------------------------------------------------------
#
# import_media_object
#
#-------------------------------------------------------------------------
def import_media_object(filename,path,base):
    if not os.path.exists(filename):
        ErrorDialog(_("Could not import %s") % filename,
                    _("The file has been moved or deleted"))
        return ""
    return filename

#-------------------------------------------------------------------------
#
# scale_image
#
#-------------------------------------------------------------------------
def scale_image(path,size):
    try:
        image1 = gtk.gdk.pixbuf_new_from_file(path)
    except:
        WarningDialog(_("Cannot display %s") % path,
                      _('GRAMPS is not able to display the image file. '
                        'This may be caused by a corrupt file.'))
        return gtk.gdk.pixbuf_new_from_file(const.icon)
    
    width  = image1.get_width()
    height = image1.get_height()

    scale = size / float(max(width,height))
    try:
        return image1.scale_simple(int(scale*width), int(scale*height),
                                   gtk.gdk.INTERP_BILINEAR)
    except:
        WarningDialog(_("Cannot display %s") % path,
                      _('GRAMPS is not able to display the image file. '
                        'This may be caused by a corrupt file.'))
        return gtk.gdk.pixbuf_new_from_file(const.icon)


