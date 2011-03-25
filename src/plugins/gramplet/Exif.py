# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011      Nick Hall
# Copyright (C) 2011      Rob G. Healey <robhealey1@gmail.com>
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
#

from ListModel import ListModel, NOSORT
from gen.plug import Gramplet
from gen.ggettext import gettext as _
import gtk
import Utils
import sys

# pyexiv2 download page (C) Olivier Tilloy
_DOWNLOAD_LINK = "http://tilloy.net/dev/pyexiv2/download.html"

# make sure the pyexiv2 library is installed and at least a minimum version
pyexiv2_req_install = True
Min_VERSION = (0, 1, 3)
Min_VERSION_str = "pyexiv2-%d.%d.%d" % Min_VERSION
PrefVersion_str = "pyexiv2-%d.%d.%d" % (0, 3, 0)

# v0.1 has a different API to v0.2 and above
LesserVersion = False

try:
    import pyexiv2
    if pyexiv2.version_info < Min_VERSION:
        pyexiv2_req_install = False

except ImportError:
    pyexiv2_req_install = False
               
except AttributeError:
    # version_info attribute does not exist prior to v0.2.0
    LesserVersion = True

# the library is either not installed or does not meet 
# minimum required version for this addon....
if not pyexiv2_req_install:
    raise Exception((_("The minimum required version for pyexiv2 must be %s "
        "or greater.\n  Or you do not have the python library installed yet.\n"
        "You may download it from here: %s\n\n  I recommend getting, %s") % (
         Min_VERSION_str, _DOWNLOAD_LINK, PrefVersion_str)
         ).encode(sys.getfilesystemencoding()) )

class Exif(Gramplet):
    """
    Displays the exif tags of an image.
    """
    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.gui.WIDGET)
        self.gui.WIDGET.show()
        self.connect_signal('Media', self.update)

    def build_gui(self):
        """
        Build the GUI interface.
        """
        top = gtk.TreeView()
        titles = [(_('Key'), 1, 250),
                  (_('Value'), 2, 350)]
        self.model = ListModel(top, titles)
        return top
        
    def main(self):
        active_handle = self.get_active('Media')
        media = self.dbstate.db.get_object_from_handle(active_handle)

        self.model.clear()
        if media:
            self.display_exif_tags(media)

    def display_exif_tags(self, media):
        """
        Display the exif tags.
        """
        full_path = Utils.media_path_full(self.dbstate.db, media.get_path())
        
        if LesserVersion: # prior to v0.2.0
            try:
                metadata = pyexiv2.Image(full_path)
            except IOError:
                return
            metadata.readMetadata()
            for key in metadata.exifKeys():
                label = metadata.tagDetails(key)[0]
                human_value = metadata.interpretedExifValue(key)
                self.model.add((label, human_value))

        else: # v0.2.0 and above
            metadata = pyexiv2.ImageMetadata(full_path)
            try:
                metadata.read()
            except IOError:
                return
            for key in metadata.exif_keys:
                tag = metadata[key]
                self.model.add((tag.label, tag.human_value))
