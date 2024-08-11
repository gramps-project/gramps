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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Provide the interface to allow a person to add a media object to the database.
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------
import os

# -------------------------------------------------------------------------
#
# internationalization
#
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import GdkPixbuf

# -------------------------------------------------------------------------
#
# gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from gramps.gen.const import ICON, THUMBSCALE, USER_HOME
from gramps.gen.config import config
from gramps.gen.utils.file import media_path_full, media_path, relative_path, find_file
from gramps.gen.mime import get_type
from gramps.gen.utils.thumbnails import get_thumbnail_image
from ..display import display_help
from ..managedwindow import ManagedWindow
from ..dialog import ErrorDialog, WarningDialog
from ..glade import Glade
from gramps.gen.const import URL_MANUAL_SECT2

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
WIKI_HELP_PAGE = URL_MANUAL_SECT2
WIKI_HELP_SEC = _("Select_a_media_selector", "manual")


# -------------------------------------------------------------------------
#
# AddMedia
#
# -------------------------------------------------------------------------
class AddMedia(ManagedWindow):
    """
    Displays the Add Media Dialog window, allowing the user to select
    a file from the file system, while providing a description.
    """

    def __init__(self, dbstate, uistate, track, media, callback=None):
        """
        Create and displays the dialog box

        db - the database in which the new object is to be stored
        The media is updated with the information, and on save, the
        callback function is called
        """
        ManagedWindow.__init__(self, uistate, track, self, modal=True)

        self.dbase = dbstate.db
        self.obj = media
        self.callback = callback

        self.last_directory = config.get("behavior.addmedia-image-dir")
        self.relative_path = config.get("behavior.addmedia-relative-path")

        self.glade = Glade()
        self.set_window(
            self.glade.toplevel,
            self.glade.get_object("title"),
            _("Select a media object"),
        )
        self.setup_configs("interface.addmedia", 700, 500)

        self.description = self.glade.get_object("photoDescription")
        self.image = self.glade.get_object("image")
        self.file_text = self.glade.get_object("fname")
        if not (self.last_directory and os.path.isdir(self.last_directory)):
            self.last_directory = USER_HOME
        # if existing path, use dir of path
        if not self.obj.get_path() == "":
            fullname = media_path_full(self.dbase, self.obj.get_path())
            dir = os.path.dirname(fullname)
            if os.path.isdir(dir):
                self.last_directory = dir
                self.file_text.select_filename(fullname)
            else:
                self.file_text.set_current_folder(self.last_directory)
        else:
            self.file_text.set_current_folder(self.last_directory)
        if not self.obj.get_description() == "":
            self.description.set_text(self.obj.get_description())

        self.relpath = self.glade.get_object("relpath")
        self.relpath.set_active(self.relative_path)
        self.temp_name = ""
        self.object = None

        self.glade.get_object("fname").connect("update_preview", self.on_name_changed)
        self.ok_button = self.glade.get_object("button79")
        self.help_button = self.glade.get_object("button103")
        self.cancel_button = self.glade.get_object("button81")
        self.ok_button.connect("clicked", self.save)
        self.ok_button.set_sensitive(not self.dbase.readonly)
        self.help_button.connect(
            "clicked",
            lambda x: display_help(webpage=WIKI_HELP_PAGE, section=WIKI_HELP_SEC),
        )
        self.cancel_button.connect("clicked", self.close)
        self.show()

    def build_menu_names(self, obj):
        """
        Build the menu name for the window manager.
        """
        return (_("Select media object"), None)

    def save(self, *obj):
        """
        Callback function called when the save button is pressed.
        The media object is updated, and callback called.
        """
        description = str(self.description.get_text())

        if self.file_text.get_filename() is None:
            msgstr = _("Import failed")
            msgstr2 = _("The filename supplied could not be found.")
            ErrorDialog(msgstr, msgstr2, parent=self.window)
            return

        filename = self.file_text.get_filename()
        full_file = filename

        if self.relpath.get_active():
            pname = str(media_path(self.dbase))
            if not os.path.exists(pname):
                msgstr = _("Cannot import %s")
                msgstr2 = _(
                    "Directory specified in preferences: "
                    "Base path for relative media paths: "
                    "%s does not exist. Change preferences "
                    "or do not use relative path when importing"
                )
                ErrorDialog(msgstr % filename, msgstr2 % pname, parent=self.window)
                return
            filename = relative_path(filename, pname)

        mtype = get_type(full_file)
        description = description or os.path.basename(filename)

        self.obj.set_description(description)
        self.obj.set_mime_type(mtype)
        name = filename
        self.obj.set_path(name)

        self.last_directory = os.path.dirname(full_file)
        self.relative_path = self.relpath.get_active()

        self._cleanup_on_exit()
        if self.callback:
            self.callback(self.obj)
        self.close()

    def on_name_changed(self, *obj):
        """
        Called anytime the filename text window changes. Checks to
        see if the file exists. If it does, the image is loaded into
        the preview window.
        """
        fname = self.file_text.get_filename()
        if not fname:
            return
        filename = fname
        basename = os.path.basename(filename)
        (root, ext) = os.path.splitext(basename)
        old_title = self.description.get_text()

        if old_title == "" or old_title == self.temp_name:
            self.description.set_text(root)
        self.temp_name = root

        filename = find_file(filename)
        if filename:
            mtype = get_type(filename)
            image = get_thumbnail_image(filename, mtype)
            self.image.set_from_pixbuf(image)

    def _cleanup_on_exit(self):
        config.set("behavior.addmedia-image-dir", self.last_directory)
        config.set("behavior.addmedia-relative-path", self.relative_path)
        config.save()

    # -------------------------------------------------------------------------
    #
    # scale_image
    #
    # -------------------------------------------------------------------------
    def scale_image(self, path, size):
        """
        Scales the image to the specified size
        """

        title_msg = _("Cannot display %s") % path
        detail_msg = _(
            "Gramps is not able to display the image file. "
            "This may be caused by a corrupt file."
        )

        try:
            image1 = GdkPixbuf.Pixbuf.new_from_file(path)
            width = image1.get_width()
            height = image1.get_height()
            scale = size / float(max(width, height))
            return image1.scale_simple(
                int(scale * width), int(scale * height), GdkPixbuf.InterpType.BILINEAR
            )
        except:
            WarningDialog(title_msg, detail_msg, parent=self.window)
            return GdkPixbuf.Pixbuf.new_from_file(ICON)
