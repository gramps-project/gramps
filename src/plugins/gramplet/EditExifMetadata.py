# -*- coding: utf-8 -*-
#!/usr/bin/python
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009-2011 Rob G. Healey <robhealey1@gmail.com>
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

# $Id$

# *****************************************************************************
# Python Modules
# *****************************************************************************
import os
from datetime import datetime
import calendar
import time
from PIL import Image, ImageEnhance, ImageFilter

# abilty to escape certain characters from output...
from xml.sax.saxutils import escape as _html_escape

from itertools import chain

from decimal import Decimal, getcontext
getcontext().prec = 6
from fractions import Fraction

import subprocess

# -----------------------------------------------------------------------------
# GTK modules
# -----------------------------------------------------------------------------
import gtk

# -----------------------------------------------------------------------------
# GRAMPS modules
# -----------------------------------------------------------------------------
import GrampsDisplay

from gen.ggettext import gettext as _

from DateHandler import displayer as _dd
from DateHandler import parser as _dp
from gen.lib.date import Date

from gen.plug import Gramplet

from gui.widgets import ValidatableMaskedEntry
from Errors import ValidationError
from QuestionDialog import WarningDialog, QuestionDialog, OptionDialog

import gen.lib
import gen.mime
import Utils
from PlaceUtils import conv_lat_lon

from gen.db import DbTxn

from ListModel import ListModel

#####################################################################
#               Check for pyexiv2 library...
#####################################################################
# pyexiv2 download page (C) Olivier Tilloy
_DOWNLOAD_LINK = "http://tilloy.net/dev/pyexiv2/download.html"

# make sure the pyexiv2 library is installed and at least a minimum version
software_version = False
Min_VERSION = (0, 1, 3)
Min_VERSION_str = "pyexiv2-%d.%d.%d" % Min_VERSION
Pref_VERSION_str = "pyexiv2-%d.%d.%d" % (0, 3, 0)

try:
    import pyexiv2
    software_version = pyexiv2.version_info

except ImportError, msg:
    WarningDialog(_("You need to install, %s or greater, for this addon to work...\n"
                    "I would recommend installing, %s, and it may be downloaded from here: \n%s") % (
                        Min_VERSION_str, Pref_VERSION_str, _DOWNLOAD_LINK), str(msg))
    raise Exception(_("Failed to load 'Edit Image Exif Metadata'..."))
               
# This only happends if the user has pyexiv2-0.1.3 installed on their computer...
except AttributeError:
    software_version = pyexiv2.__version__

# v0.1 has a different API than v0.2 and above...
if hasattr(pyexiv2, 'version_info'):
    LesserVersion = False
else:
    # version_info attribute does not exist prior to v0.2.0
    LesserVersion = True

# the library is either not installed or does not meet minimum required version for this addon....
if (software_version and (software_version < Min_VERSION)):
    msg = _("The minimum required version for pyexiv2 must be %s \n"
        "or greater.  Or you do not have the python library installed yet.  "
        "You may download it from here: %s\n\n  I recommend getting, %s") % (
         Min_VERSION_str, _DOWNLOAD_LINK, Pref_VERSION_str)
    WarningDialog(msg)
    raise Exception(msg)

# check to make sure that exiv2 is installed and some kind of delete command...
system_platform = os.sys.platform
if system_platform == "Win32":
    EXIV2_OUND_ = "exiv2.exe" if Utils.search_for("exiv2.exe") else False
elif system_platform == "linux2":
    EXIV2_FOUND_ = "exiv2" if Utils.search_for("exiv2") else False
else:
    EXIV2_FOUND_ = "exiv2" if Utils.search_for("exiv2") else False

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
# available image types for exiv2 and pyexiv2
_vtypes = [".tiff", ".jpeg", ".png", ".exv", ".dng", ".bmp", ".nef", ".psd", ".jp2", ".pef", ".srw", ".pgf"]
_vtypes.sort()
_VTYPEMAP = dict( (index, imgtype_) for index, imgtype_ in enumerate(_vtypes) )

# valid converting types for PIL.Image...
_validconvert = list( (".bmp", ".gif", ".jpg", ".msp", ".pcx", ".png", ".ppm", ".tiff", ".xbm") )

# set up Exif keys for Image Exif metadata keypairs...
_DATAMAP = {
    "Xmp.xmp.Label"                : "ExifLabel",
    "Exif.Image.ImageDescription"  : "Description",
    "Exif.Image.DateTime"          : "Modified",
    "Exif.Image.Artist"            : "Artist",
    "Exif.Image.Copyright"         : "Copyright",
    "Exif.Photo.DateTimeOriginal"  : "Original",
    "Exif.Photo.DateTimeDigitized" : "Digitized",
    "Xmp.xmp.ModifyDate"           : "ModifyDate",
    "Exif.GPSInfo.GPSLatitudeRef"  : "LatitudeRef",
    "Exif.GPSInfo.GPSLatitude"     : "Latitude",
    "Exif.GPSInfo.GPSLongitudeRef" : "LongitudeRef",
    "Exif.GPSInfo.GPSLongitude"    : "Longitude",
    "Exif.GPSInfo.GPSAltitudeRef"  : "AltitudeRef",
    "Exif.GPSInfo.GPSAltitude"     : "Altitude"}
_DATAMAP  = dict((key, val) for key, val in _DATAMAP.items() )
_DATAMAP.update( (val, key) for key, val in _DATAMAP.items() )

# define tooltips for all data entry fields...
_TOOLTIPS = {

    # Exif Label/ Title...
    "ExifLabel" : _("This is equivalent to the Title field in the media object editor."),

    # Description...
    "Description" : _("Provide a short descripion for this image."),

    # Last Change/ Modify Date/ Time...
    "Modified" : _("This is the date/ time that the image was last changed/ modified.\n"
        "Example: 2011-05-24 14:30:00"),

    # Artist...
    "Artist" : _("Enter the Artist/ Author of this image.  The person's name or "
        "the company who is responsible for the creation of this image."),

    # Copyright...
    "Copyright" : _("Enter the copyright information for this image. \n"),

    # Original Date/ Time...
    "Original" : _("The original date/ time when the image was first created/ taken as in a photograph.\n"
        "Example: 1830-01-1 09:30:59"),

    # GPS Latitude Coordinates...
    "Latitude" : _("Enter the Latitude GPS Coordinates for this image,\n"
        "Example: 43.722965, 43 43 22 N, 38° 38′ 03″ N, 38 38 3"),

    # GPS Longitude Coordinates...
    "Longitude" : _("Enter the Longitude GPS Coordinates for this image,\n"
        "Example: 10.396378, 10 23 46 E, 105° 6′ 6″ W, -105 6 6"),

    # GPS Altitude (in meters)...
    "Altitude" : _("This is the measurement of Above or Below Sea Level.  It is measured in meters."
        "Example: 200.558, -200.558") }

_TOOLTIPS  = dict( (key, tooltip) for key, tooltip in _TOOLTIPS.items() )

# define tooltips for all buttons...
# common buttons for all images...
_BUTTONTIPS = {

    # Wiki Help button...
    "Help" : _("Displays the Gramps Wiki Help page for 'Edit Image Exif Metadata' "
        "in your web browser."),

    # Edit screen button...
    "Edit" : _("This will open up a new window to allow you to edit/ modify "
        "this image's Exif metadata.\n  It will also allow you to be able to "
        "Save the modified metadata."),

    # Thumbnail Viewing Window button...
    "Thumbnail" : _("Will produce a Popup window showing a Thumbnail Viewing Area"),

    # Image Type button...
    "ImageType" : _("Select from a drop- down box the image file type that you "
        "would like to convert your non- Exiv2 compatible media object to."),

    # Convert to different image type...
    "Convert" : _("If your image is not of an image type that can have "
        "Exif metadata read/ written to/from, convert it to a type that can?"),

    # Delete/ Erase/ Wipe Exif metadata button...
    "Delete" : _("WARNING:  This will completely erase all Exif metadata "
        "from this image!  Are you sure that you want to do this?") }

# ------------------------------------------------------------------------
#
# 'Edit Image Exif metadata' Class
#
# ------------------------------------------------------------------------
class EditExifMetadata(Gramplet):
    """
    Special symbols...

    degrees symbol = [Ctrl] [Shift] u \00b0
    minutes symbol =                  \2032
    seconds symbol =                  \2033
    """
    def init(self):

        self.exif_widgets = {}
        self.dates = {}
        self.coordinates = {}

        self.image_path   = False
        self.orig_image   = False
        self.plugin_image = False

        vbox = self.__build_gui()
        self.connect_signal("Media", self.update)

        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(vbox)

        # display all button tooltips only...
        # 1st argument is for Fields, 2nd argument is for Buttons...
        self._setup_widget_tips([False, True])

    def __build_gui(self):
        """
        will display all exif metadata and all buttons.
        """

        main_vbox = gtk.VBox(False, 0)
        main_vbox.set_border_width(10)

        # Displays the file name...
        medialabel = gtk.HBox(False)
        label = self.__create_label("MediaLabel", False, False, False) 
        medialabel.pack_start(label, expand =False)
        main_vbox.pack_start(medialabel, expand =False, fill =False, padding =2)
        label.show()

        # Displays mime type information...
        mimetype = gtk.HBox(False)
        label = self.__create_label("MimeType", False, False, False)
        mimetype.pack_start(label, expand =False)
        main_vbox.pack_start(mimetype, expand =False, fill =False, padding =2)
        label.show()

        # image dimensions...
        imagesize = gtk.HBox(False)
        label = self.__create_label("ImageSize", False, False, False)
        imagesize.pack_start(label, expand =False, fill =False, padding =0)
        main_vbox.pack_start(imagesize, expand =False, fill =True, padding =5)
        label.hide()

        # Displays all plugin messages...
        messagearea = gtk.HBox(False)
        label = self.__create_label("MessageArea", False, False, False)
        messagearea.pack_start(label, expand =False)
        main_vbox.pack_start(messagearea, expand =False, fill =False, padding =2)
        label.show()

        # Separator line before the buttons...
        main_vbox.pack_start(gtk.HSeparator(), expand =False, fill =False, padding =2)

        # Thumbnail, ImageType, and Convert horizontal box...
        new_hbox = gtk.HBox()
        main_vbox.pack_start(new_hbox, expand =False, fill =False, padding =0)
        new_hbox.show()

        # Thumbnail button...
        event_box = gtk.EventBox()
        event_box.set_size_request(90, 35)
        new_hbox.pack_start(event_box, expand =False, fill =False, padding =0)
        event_box.show()

        button = self.__create_button(
            "Thumbnail", _("Thumbnail"), [self.thumbnail_view])
        event_box.add(button)
        button.show()

        # Image Type...
        event_box = gtk.EventBox()
        event_box.set_size_request(165, 35)
        new_hbox.pack_start(event_box, expand =False, fill =False, padding =0)
        self.exif_widgets["ImageTypeBox"] = event_box
        event_box.show()

        combo_box = gtk.combo_box_new_text()
        combo_box.append_text(_("--Image Formats--"))
        combo_box.set_active(0)
        combo_box.set_sensitive(False)
        event_box.add(combo_box)
        self.exif_widgets["ImageType"] = combo_box
        combo_box.show()

        # Convert button...
        event_box = gtk.EventBox()
        event_box.set_size_request(100, 35)
        new_hbox.pack_start(event_box, expand =False, fill =False, padding =0)
        event_box.show()        

        button = self.__create_button(
            "Convert", False, [self.__convert_dialog], gtk.STOCK_CONVERT)
        event_box.add(button)
        button.show()

        # Connect the changed signal to ImageType...
        self.exif_widgets["ImageType"].connect("changed", self.changed_cb)

        # Help, Edit, and Delete horizontal box
        hed_box = gtk.HButtonBox()
        hed_box.set_layout(gtk.BUTTONBOX_START)
        main_vbox.pack_start(hed_box, expand =False, fill =False, padding =5)

        # Help button...
        hed_box.add( self.__create_button(
            "Help", False, [self.__help_page], gtk.STOCK_HELP, True) )

        # Edit button...
        hed_box.add( self.__create_button(
            "Edit", False, [self.display_edit_window], gtk.STOCK_EDIT) )

        if EXIV2_FOUND_:
            # Delete All Metadata button...
            hed_box.add(self.__create_button(
                "Delete", False, [self.__wipe_dialog], gtk.STOCK_DELETE) )

        new_vbox = self.build_shaded_display()
        main_vbox.pack_start(new_vbox, expand =False, fill =False, padding =10)

        # number of key/value pairs shown...
        label = self.__create_label("Total", False, False, False)
        main_vbox.pack_start(label, expand =False, fill =False, padding =10)
        label.show()

        main_vbox.show_all()
        return main_vbox

    def db_changed(self):
        self.dbstate.db.connect('media-update', self.update)
        self.connect_signal('Media', self.update)
        self.update()

    def main(self): # return false finishes
        """
        get the active media, mime type, and reads the image metadata

        *** disable all buttons at first, then activate as needed...
            # Help will never be disabled...
        """
        db = self.dbstate.db

        # clears all labels and display area...
        for widgetname_ in ["MediaLabel", "MimeType", "ImageSize", "MessageArea", "Total"]:
            self.exif_widgets[widgetname_].set_text("")
        self.model.clear()

        # deactivate Convert and ImageType buttons...
        self.deactivate_buttons(["Convert", "ImageType"])

        # set Message Ares to Select...
        self.exif_widgets["MessageArea"].set_text(_("Select an image to begin..."))

        active_handle = self.get_active("Media")
        if not active_handle:
            self.set_has_data(False)
            return

        # get image from database...
        self.orig_image = db.get_object_from_handle(active_handle)
        if not self.orig_image:
            self.set_has_data(False)
            return

        # get file path and attempt to find it?
        self.image_path = Utils.media_path_full(db, self.orig_image.get_path() )
        if not os.path.isfile(self.image_path):
            self.set_has_data(False)
            return

        # get dirpath/ basename, and extension...
        self.basename, self.extension = os.path.splitext(self.image_path)

        # remove the extension out of the list of convertible image types...
        # What would make sense to be able to convert to your current image type?
        PILConvert = _validconvert
        if self.extension in PILConvert:
            PILConvert.remove(self.extension)
        PILConvert.sort()
        self._VCONVERTMAP = dict( (index, imgtype_) for index, imgtype_ in enumerate(PILConvert) )
        for imgtype_ in self._VCONVERTMAP.values():
            self.exif_widgets["ImageType"].append_text(imgtype_)
        self.exif_widgets["ImageType"].set_active(0)

        # check image read privileges...
        _readable = os.access(self.image_path, os.R_OK)
        if not _readable:
            self.exif_widgets["MessageArea"].set_text(_("Image is NOT readable,\n"
                "Please choose a different image..."))
            return

        # check image write privileges...
        _writable = os.access(self.image_path, os.W_OK)
        if not _writable:
            self.exif_widgets["MessageArea"].set_text(_("Image is NOT writable,\n"
                "You will NOT be able to save Exif metadata...."))
            self.deactivate_buttons(["Edit"])

        # Mime type information...
        mime_type = self.orig_image.get_mime_type()
        self.exif_widgets["MimeType"].set_text(gen.mime.get_description(mime_type))

        # if image file type is not an Exiv2 acceptable image type,
        # offer to convert it....
        if self.extension not in _VTYPEMAP.values():
            self.activate_buttons(["ImageType"])

        # determine if it is a mime image object?
        if mime_type:
            if mime_type.startswith("image"):

                # display file description/ title...
                self.exif_widgets["MediaLabel"].set_text(_html_escape(
                    self.orig_image.get_description() ) )

                # creates, and reads the plugin image instance...
                self.plugin_image = self.setup_image(self.image_path)

                if LesserVersion:  # prior to pyexiv2-0.2.0
                    try:
                        ttype, tdata = self.plugin_image.getThumbnailData()
                        width, height = tdata.dimensions
                        thumbnail = True
                    except (IOError, OSError):
                        thumbnail = False

                else:  # pyexiv2-0.2.0 and above
                    try:
                        previews = self.plugin_image.previews
                        thumbnail = True
                        if not previews:
                            thumbnail = False
                    except (IOError, OSError):
                        thumbnail = False

                # if a thumbnail exists, then activate the buttton?
                if thumbnail:
                    self.activate_buttons(["Thumbnail"])

                # Activate the Edit button...
                self.activate_buttons(["Edit"])

                # display all exif metadata...
                mediadatatags = _get_exif_keypairs(self.plugin_image)
                if mediadatatags:
                    self.display_metadata(mediadatatags)

                else:
                    # set Message Area to None...
                    self.exif_widgets["MessageArea"].set_text(_("No Exif metadata for this image..."))

            # has mime, but not an image...
            else:
                self.exif_widgets["MessageArea"].set_text(_("Please choose a different image..."))
                return

        # has no mime...
        else:
            self.exif_widgets["MessageArea"].set_text(_("Please choose a different image..."))
            return

    def changed_cb(self, object):
        """
        will show the Convert Button once an Image Type has been selected, and if
            image extension is not an Exiv2- compatible image?
        """

        if self.extension not in _VTYPEMAP.values():

            if not self.exif_widgets["Convert"].get_sensitive():
                self.activate_buttons(["Convert"])
 
    def _setup_widget_tips(self, _ttypes):
        """
        set up widget tooltips...
            * data fields
            * buttons
        """
        fields, buttons = _ttypes

        # if True, setup tooltips for all Data Entry Fields...
        if fields:
            for widget, tooltip in _TOOLTIPS.items():
                self.exif_widgets[widget].set_tooltip_text(tooltip)

        # if True, setup tooltips for all Buttons...
        if buttons:
            for widget, tooltip in _BUTTONTIPS.items():
                self.exif_widgets[widget].set_tooltip_text(tooltip)

    def setup_image(self, full_path):
        """
        This will:
            * create the plugin image instance if needed,
            * setup the tooltips for the data fields,
            * setup the tooltips for the buttons,
        """

        if LesserVersion:  # prior to pyexiv2-0.2.0
            metadata = pyexiv2.Image(full_path)
            try:
                metadata.readMetadata()
            except (IOError, OSError):
                self.set_has_data(False)
                return 

        else:  # pyexiv2-0.2.0 and above
            metadata = pyexiv2.ImageMetadata(full_path)
            try:
                metadata.read()
            except (IOError, OSError):
                self.set_has_data(False)
                return

        return metadata

    def update_has_data(self):
        active_handle = self.get_active('Media')
        active = self.dbstate.db.get_object_from_handle(active_handle)
        self.set_has_data(self.get_has_data(active))

    def get_has_data(self, media):
        """
        Return True if the gramplet has data, else return False.
        """
        db = self.dbstate.db

        if media is None:
            return False

        full_path = Utils.media_path_full(db, media.get_path() )
        if not os.path.isfile(full_path):
            return False

        if LesserVersion: # prior to pyexiv2-0.2.0
            metadata = pyexiv2.Image(full_path)
            try:
                metadata.readMetadata()
            except (IOError, OSError):
                return False

        else: # pyexiv2-0.2.0 and above
            metadata = pyexiv2.ImageMetadata(full_path)
            try:
                metadata.read()
            except (IOError, OSError):
                return False

        # update image Exif metadata...
        mediadatatags_ = _get_exif_keypairs(self.plugin_image)
        if mediadatatags_:
            return True

        return False

    def display_metadata(self, mediadatatags_ =None):
        """
        displays all of the image's Exif metadata in a grey-shaded tree view...
        """

        # clear display area...
        self.model.clear()

        # get All Exif metadata...
        metadatatags_ = _get_exif_keypairs(self.plugin_image)
        if not metadatatags_:
            self.exif_widgets["MessageArea"].set_text(_("No Exif metadata to display..."))
            return

        # set Message Area to Display...
        self.exif_widgets["MessageArea"].set_text(_("Displaying all Exif metadata keypairs..."))

        if not LesserVersion:  # pyexiv2-0.2.0 and above...

            # image Dimensions...
            self.exif_widgets["ImageSize"].show()
            width, height = self.plugin_image.dimensions
            self.exif_widgets["ImageSize"].set_text(_("Image Size : %04d x %04d pixels") % (width, height))

        # Activate Delete button if ImageMagick or jhead is found?...
        self.activate_buttons(["Delete"])

        for keytag_ in metadatatags_: 
            if LesserVersion:  # prior to pyexiv2-0.2.0
                label = metadata.tagDetails(keytag_)[0]

                # if keytag_ is one of the dates, display as the user wants it in preferences
                if keytag_ in [_DATAMAP["Modified"], _DATAMAP["Original"], _DATAMAP["Digitized"] ]:
                    human_value = _format_datetime(self.plugin_image[keytag_])
                else:
                    human_value = self.plugin_image.interpretedExifValue(keytag_)

            else:  # pyexiv2-0.2.0 and above
                tag = self.plugin_image[keytag_]

                # if keytag_ is one of the dates, display as the user wants it in preferences
                if keytag_ in [_DATAMAP["Modified"], _DATAMAP["Original"], _DATAMAP["Digitized"] ]:
                    _value = self._get_value(keytag_)
                    if _value:
                        label = tag.label
                        human_value = _format_datetime(_value)
                    else:
                        human_value = False

                elif ("Xmp" in keytag_ or "Iptc" in keytag_):
                    label = self.plugin_image[keytag_]
                    human_value = self._get_value(keytag_)

                else:
                    label = tag.label
                    human_value = tag.human_value

            if human_value:

                # add to model for display...
                self.model.add((label, human_value))
                
        self.set_has_data(self.model.count > 0)
        self.exif_widgets["Total"].set_text(_("Number of Key/ Value pairs : %04d") % self.model.count)

    def __create_button(self, pos, text, callback =[], icon =False, sensitive =False):
        """
        creates and returns a button for display
        """

        if (icon and not text):
            button = gtk.Button(stock =icon)
        else:
            button = gtk.Button(text)

        if callback is not []:
            for call_ in callback:
                button.connect("clicked", call_)

        # attach a addon widget to the button for manipulation...
        self.exif_widgets[pos] = button

        if not sensitive:
            button.set_sensitive(False)
        else:
            button.set_sensitive(True)

        return button

    def __create_label(self, widget, text, width, height, wrap =True):
        """
        creates a label for this addon.
        """

        label = gtk.Label()
        label.set_alignment(0.0, 0.0)

        if wrap:
            label.set_line_wrap(True)

        if (width and height):
            label.set_size_request(width, height)

        if text:
            label.set_text(text)

        if widget:
            self.exif_widgets[widget] = label

        return label

    def build_shaded_display(self):
        """
        Build the GUI interface.
        """

        top = gtk.TreeView()
        titles = [(_('Key'), 1, 180),
                  (_('Value'), 2, 310)]
        self.model = ListModel(top, titles)

        return top

    def thumbnail_view(self, object):
        """
        will allow a display area for a thumbnail pop-up window.
        """
 
        dirpath, filename = os.path.split(self.image_path)

        if LesserVersion:  # prior to pyexiv2-0.2.0
            try:
               ttype, tdata = self.plugin_image.getThumbnailData()
               width, height = tdata.dimensions

            except (IOError, OSError):
                print(_('Error: %s does not contain an EXIF thumbnail.') % filename)
                self.close_window(self.tbarea)

            # Create a GTK pixbuf loader to read the thumbnail data
            pbloader = gtk.gdk.PixbufLoader()
            pbloader.write(tdata)

        else:  # pyexiv2-0.2.0 and above
            try:
                previews = self.plugin_image.previews
                if not previews:
                    print(_('Error: %s does not contain an EXIF thumbnail.') % filename)
                    self.close_window(self.tbarea)

            except (IOError, OSError):
                print(_('Error: %s does not contain an EXIF thumbnail.') % filename)
                self.close_window(self.tbarea)

            # Get the largest preview available...
            preview = previews[-1]
            width, height = preview.dimensions

            # Create a GTK pixbuf loader to read the thumbnail data
            pbloader = gtk.gdk.PixbufLoader()
            pbloader.write(preview.data)

        tip = _("Click Close to close this Thumbnail Viewing Area.")

        self.tbarea = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.tbarea.tooltip = tip
        self.tbarea.set_title(_("Thumbnail Viewing Area"))
        self.tbarea.set_default_size((width + 40), (height + 40))
        self.tbarea.set_border_width(10)
        self.tbarea.connect('destroy', lambda w: self.tbarea.destroy() )

        new_vbox = self.build_thumbnail_gui(pbloader, width, height)
        self.tbarea.add(new_vbox)
        self.tbarea.show()

    def build_thumbnail_gui(self, pbloader, width, height):
        """
        builds the thumbnail viewing area.
        """

        main_vbox = gtk.VBox()
        main_vbox.set_size_request((width - 30), (height - 30))

        hbox = gtk.HBox(False, 0)
        main_vbox.pack_start(hbox, expand =False, fill =False, padding =5)
        hbox.show()

        # Get the resulting pixbuf and build an image to be displayed...
        pixbuf = pbloader.get_pixbuf()
        pbloader.close()

        imgwidget = gtk.Image()
        imgwidget.set_from_pixbuf(pixbuf)
        hbox.pack_start(imgwidget, expand = False, fill =True, padding =0)
        imgwidget.show()

        main_vbox.show_all()
        return main_vbox

    def __convert_dialog(self, object):
        """
        Handles the Convert question Dialog...
        """

        # Convert and delete original file...
        if EXIV2_FOUND_:
            OptionDialog(_("Edit Image Exif Metadata"), _("WARNING: You are about to convert this "
                "image into a .jpeg image.  Are you sure that you want to do this?"), 
                _("Convert and Delete"), self.__convert_delete, _("Convert"), self.__convert_file)

    def __convert_file(self, full_path =None):
        """
        Will attempt to convert an image to jpeg if it is not?
        """

        if full_path is None:
            full_path = self.image_path

        # get image filepath and its filename...
        filepath, basename = os.path.split(self.basename)
        
        # get extension selected for converting this image...
        ext_type = self.exif_widgets["ImageType"].get_active()
        if ext_type >= 1:
            basename += self._VCONVERTMAP[ext_type]

            # new file name and dirpath...
            dest_file = os.path.join(filepath, basename)

            # Convert the file based upon image file suffix...
            i = Image.open(full_path)
            if i.mode == "RGB":
                im = i.filter(ImageFilter.SHARPEN)
                i1 = im.filter(ImageFilter.DETAIL)  
                i1.save(dest_file)
            else:
                i.save(dest_file) 

            if LesserVersion:  # prior to pyexiv2-0.2.0...
                src_meta = pyexiv2.Image(full_path)

                # Copy the image metadata...
                dest_meta = pyexiv2.Image(dest_file)
                dest_meta.readMetadata()
                src_meta.readMetadata()
                src_meta.copy(dest_meta, comment =False)
                dest_meta.writeMetadata()

            else:  # pyexiv2-0.2.0 and above...
                src_meta = pyexiv2.ImageMetadata(full_path)

                # Copy the image metadata...
                dest_meta = pyexiv2.ImageMetadata(dest_file)
                src_meta.read()
                dest_meta.read()
                src_meta.copy(dest_meta, comment =False)
                dest_meta.write()

        return dest_file

    def __convert_delete(self, full_path =None):
        """
        will convert an image file and delete original non-jpeg image.
        """
        db = self.dbstate.db

        if full_path is None:
            full_path = self.image_path

        # Convert image and copy over it's Exif metadata (if any?)
        newfilepath = self.__convert_file(full_path)

        # delete original file from this computer and set new filepath...
        try:
            os.remove(full_path)
            delete_results = True

        except (IOError, OSError):
            delete_results = False

        if delete_results:

            # update media object path...
            if (newfilepath is not False and os.path.isfile(newfilepath) ):

                # begin database tranaction to save media object new path...
                with DbTxn(_("Media Path Update"), db) as trans:
                    self.orig_image.set_path(newfilepath)

                    db.disable_signals()
                    db.commit_media_object(self.orig_image, trans)

                    db.enable_signals()
                    db.request_rebuild()

                # notify user about the convert, delete, and new filepath...
                self.exif_widgets["MessageArea"].set_text(_("Your image has been "
                    "converted and the original file has been deleted, and "
                    "the full path has been updated!"))

    def __help_page(self, object):
        """
        will bring up a Wiki help page.
        """

        GrampsDisplay.help(webpage = "Edit Image Exif Metadata")

    def activate_buttons(self, ButtonList):
        """
        Enable/ activate the buttons that are in ButtonList
        """

        for widgetname_ in ButtonList:
            self.exif_widgets[widgetname_].set_sensitive(True)

    def deactivate_buttons(self, ButtonList):
        """
        disable/ de-activate buttons in ButtonList

        *** if All, then disable ALL buttons in the current display...
        """

        for widgetname_ in ButtonList:
            self.exif_widgets[widgetname_].set_sensitive(False)

    def active_buttons(self, obj):
        """
        will handle the toggle action of the Edit button.

        If there is no Exif metadata, then the data fields are connected to the 
        'changed' signal to be able to activate the Edit button once data has been entered
        into the data fields...

        Activate these buttons once info has been entered into the data fields...
        """

        if not self.exif_widgets["Edit"].get_sensitive():
            self.activate_buttons(["Edit"])

            # set Message Area to Entering Data...
            self.exif_widgets["MessageArea"].set_text(_("Entering data..."))

        if EXIV2_FOUND_:
            if not self.exif_widgets["Delete"].get_sensitive():
                self.activate_buttons(["Delete"])

        # if Save is in the list of button tooltips, then check it too?
        if "Save" in _BUTTONTIPS.keys():
            if not self.exif_widgets["Save"].get_sensitive():
                self.activate_buttons(["Save"])  

    def display_edit_window(self, object):
        """
        creates the editing area fields.
        """

        tip = _("Click the close button when you are finished modifying this "
                "image's Exif metadata.")

        self.edtarea = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.edtarea.tooltip = tip
        self.edtarea.set_title( self.orig_image.get_description() )
        self.edtarea.set_default_size(600, 582)
        self.edtarea.set_border_width(10)
        self.edtarea.connect("destroy", lambda w: self.edtarea.destroy() )

        # create a new scrolled window.
        scrollwindow = gtk.ScrolledWindow()
        scrollwindow.set_border_width(10)
        scrollwindow.set_size_request(600, 500)
        scrollwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        self.edtarea.add(scrollwindow)
        scrollwindow.show()

        vbox = self.__build_edit_gui()
        scrollwindow.add_with_viewport(vbox)
        self.edtarea.show()

        # display all fields and button tooltips...
        # need to add Save and Close over here...
        _BUTTONTIPS.update( (key, tip) for key, tip in {

            # Add the Save button...
            "Save" : _("Saves a copy of the data fields into the image's Exif metadata."),

            # Add the Close button...
            "Close" : _("Closes this popup Edit window.\n"
                "WARNING: This action will NOT Save any changes/ modification made to this "
                "image's Exif metadata."),

            # Clear button...
            "Clear" : _("This button will clear all of the data fields shown here."),

            # Re- display the data fields button...
            "Copy" : _("Re -display the data fields that were cleared from the Edit Area."), 

            # Convert 2 Decimal button...
            "Decimal" : _("Convert GPS Latitude/ Longitude Coordinates to Decimal representation."),

            # Convert 2 Degrees, Minutes, Seconds button...
            "DMS" : _("Convert GPS Latitude/ Longitude Coordinates to "
                "(Degrees, Minutes, Seconds) Representation.") }.items() )

        # True, True -- all data fields and button tooltips will be displayed...
        self._setup_widget_tips([True, True])
 
        # display all data fields and their values...
        self.EditArea(self.plugin_image)

    def __build_edit_gui(self):
        """
        will build the edit screen ...
        """
        main_vbox = gtk.VBox()
        main_vbox.set_border_width(10)
        main_vbox.set_size_request(560, 500)

        label = self.__create_label("Edit:Message", False, False, False)
        main_vbox.pack_start(label, expand =False, fill =False, padding =0)
        label.show()

        # create the data fields...
        # ***Label/ Title, Description, Artist, and Copyright
        gen_frame = gtk.Frame(_("General Data"))
        gen_frame.set_size_request(550, 200)
        main_vbox.pack_start(gen_frame, expand =False, fill =True, padding =10)
        gen_frame.show()

        new_vbox = gtk.VBox(False, 0)
        gen_frame.add(new_vbox)
        new_vbox.show()

        for widget, text in [
            ("ExifLabel",   _("Exif Label :") ),
            ("Description", _("Description :") ),
            ("Artist",      _("Artist :") ),
            ("Copyright",   _("Copyright :") ) ]:
 
            new_hbox = gtk.HBox(False, 0)
            new_vbox.pack_start(new_hbox, expand =False, fill =False, padding =5)
            new_hbox.show()

            label = self.__create_label(False, text, width =90, height =25)
            new_hbox.pack_start(label, expand =False, fill =False, padding =0)
            label.show()

            event_box = gtk.EventBox()
            event_box.set_size_request(430, 30)
            new_hbox.pack_start(event_box, expand =False, fill =False, padding =0)
            event_box.show()

            entry = gtk.Entry(max =100)
            event_box.add(entry)
            self.exif_widgets[widget] = entry
            entry.show()

        # iso format: Year, Month, Day spinners...
        datetime_frame = gtk.Frame(_("Date/ Time"))
        datetime_frame.set_size_request(550, 110)
        main_vbox.pack_start(datetime_frame, expand =False, fill =False, padding =0)
        datetime_frame.show()

        new_vbox = gtk.VBox(False, 0)
        new_vbox.set_border_width(5)
        datetime_frame.add(new_vbox)
        new_vbox.show()

        new_hbox = gtk.HBox(False, 0)
        new_vbox.pack_start(new_hbox, expand =False, fill =False, padding =0)
        new_hbox.show()

        for widget, text in [
            ("Original",     _("Original Date/ Time :") ),
            ("Modified",     _("Last Changed :") ) ]:

            vbox2 = gtk.VBox(False, 0)
            new_hbox.pack_start(vbox2, expand =False, fill =False, padding =5)
            vbox2.show()

            label = self.__create_label(widget, text, width =150, height =25)
            vbox2.pack_start(label, expand =False, fill =False, padding =0)
            label.show()

            event_box = gtk.EventBox()
            event_box.set_size_request(250, 30)
            vbox2.pack_start(event_box, expand =False, fill =False, padding =0)
            event_box.show()

            entry = ValidatableMaskedEntry()
            entry.connect('validate', self.validate_datetime, widget)
#            entry.connect('content-changed', self.set_datetime, widget)
            event_box.add(entry)
            self.exif_widgets[widget] = entry
            entry.show()

            self.dates[widget] = None

        # if there is text in the modified Date/ Time field, disable editing...
        if self.exif_widgets["Modified"].get_text():
            self.exif_widgets["Modified"].set_editable(False)

        # GPS Coordinates...
        latlong_frame = gtk.Frame(_("Latitude/ Longitude/ Altitude GPS Coordinates"))
        latlong_frame.set_size_request(550, 125)
        main_vbox.pack_start(latlong_frame, expand =False, fill =False, padding =0)
        latlong_frame.show()

        new_vbox = gtk.VBox(False, 0)
        latlong_frame.add(new_vbox)
        new_vbox.show()

        new_hbox = gtk.HBox(False, 0)
        new_vbox.pack_start(new_hbox, expand =False, fill =False, padding =0)
        new_hbox.show()

        for widget, text in [
            ("Latitude",  _("Latitude :") ),
            ("Longitude", _("Longitude :") ),
            ("Altitude",  _("Altitude :") ) ]:

            vbox2 = gtk.VBox(False, 0)
            new_hbox.pack_start(vbox2, expand =False, fill =False, padding =5)
            vbox2.show()

            label = self.__create_label(widget, text, width =90, height =25)
            vbox2.pack_start(label, expand =False, fill =False, padding =0)
            label.show()

            event_box = gtk.EventBox()
            event_box.set_size_request(167, 30)
            vbox2.pack_start(event_box, expand =False, fill =False, padding =0)
            event_box.show()

            entry = ValidatableMaskedEntry()
            entry.connect('validate', self.validate_coordinate, widget)
            event_box.add(entry)
            self.exif_widgets[widget] = entry
            entry.show()

        # add an empty row for spacing...
        new_hbox = gtk.HBox(False, 0)
        new_vbox.pack_start(new_hbox, expand =False, fill =False, padding =5)
        new_hbox.show()

        new_hbox = gtk.HBox(False, 0)
        new_vbox.pack_start(new_hbox, expand =False, fill =False, padding =0)
        new_hbox.show()

        label = self.__create_label(
            False, _("Convert GPS :"), 100, 25)
        new_hbox.pack_start(label, expand =False, fill =False, padding =0)
        label.show()

        # Convert2decimal and DMS buttons...
        decdms_box = gtk.HButtonBox()
        decdms_box.set_layout(gtk.BUTTONBOX_END)
        new_vbox.pack_end(decdms_box, expand =False, fill =False, padding =0)
        decdms_box.show()

        # Decimal button...
        decdms_box.add(self.__create_button(
            "Decimal", _("Decimal"), [self.__decimalbutton], False, True) )

        # Degrees, Minutes, Seconds button...
        decdms_box.add(self.__create_button(
            "DMS", _("Deg., Mins., Secs."), [self.__dmsbutton], False, True) ) 

        # Help, Save, Clear, Copy, and Close horizontal box
        hsccc_box = gtk.HButtonBox()
        hsccc_box.set_layout(gtk.BUTTONBOX_START)
        main_vbox.pack_start(hsccc_box, expand =False, fill =False, padding =10)
        hsccc_box.show()

        # Help button...
        hsccc_box.add(self.__create_button(
            "Help", False, [self.__help_page], gtk.STOCK_HELP, True) )

        # Save button...
        hsccc_box.add(self.__create_button(
            "Save", False, [self.save_metadata, self.update, self.display_metadata],
                gtk.STOCK_SAVE, True) )

        # Clear button...
        hsccc_box.add(self.__create_button(
            "Clear", False, [self.clear_metadata], gtk.STOCK_CLEAR, True) )

        # Re -display the edit area button...
        hsccc_box.add(self.__create_button(
            "Copy", False, [self.EditArea], gtk.STOCK_COPY, True) )

        # Close button...
        hsccc_box.add(self.__create_button(
            "Close", False, [lambda w: self.edtarea.destroy() ], gtk.STOCK_CLOSE, True) )

        main_vbox.show_all()
        return main_vbox

    def set_datetime(self, widget, field):
        """
        Parse date and time from text entry
        """
        value = _parse_datetime(unicode(widget.get_text()))
        if value is not None:
            self.dates[field] = "%04d:%02d:%02d %02d:%02d:%02d" % (
                                    value.year, value.month, value.day,
                                    value.hour, value.minute, value.second)
        else:
            self.dates[field] = None

    def validate_datetime(self, widget, data, field):
        """
        Validate current date and time in text entry
        """
        if self.dates[field] is None:
            return ValidationError(_('Bad Date/Time'))

    def validate_coordinate(self, widget, data, field):
        """
        Validate current latitude or longitude in text entry
        """
        if field == "Latitude" and not conv_lat_lon(data, "0", "ISO-D"):
            return ValidationError(_(u"Invalid latitude (syntax: 18\u00b09'") +
                                   _('48.21"S, -18.2412 or -18:9:48.21)'))
        if field == "Longitude" and not conv_lat_lon("0", data, "ISO-D"):
            return ValidationError(_(u"Invalid longitude (syntax: 18\u00b09'") +
                                   _('48.21"E, -18.2412 or -18:9:48.21)'))

    def __wipe_dialog(self, object):
        """
        Handles the Delete Dialog...
        """

        QuestionDialog(_("Edit Image Exif Metadata"), _("WARNING!  You are about to completely "
            "delete the Exif metadata from this image?"), _("Delete"),
                self.strip_metadata)

    def _get_value(self, keytag_):
        """
        gets the value from the Exif Key, and returns it...

        @param: keytag_ -- image metadata key
        """

        if LesserVersion:
            keyvalue_ = self.plugin_image[keytag_]

        else:
            try:
                valu_ = self.plugin_image.__getitem__(keytag_)
                keyvalue_ = valu_.value

            except (KeyError, ValueError, AttributeError):
                keyvalue_ = False

        return keyvalue_

    def clear_metadata(self, object):
        """
        clears all data fields to nothing
        """

        for widget in _TOOLTIPS.keys():
            self.exif_widgets[widget].set_text("")

    def EditArea(self, mediadatatags_ =None):
        """
        displays the image Exif metadata in the Edit Area...
        """

        mediadatatags_ = _get_exif_keypairs(self.plugin_image)
        if mediadatatags_:
            mediadatatags_ = [keytag_ for keytag_ in mediadatatags_ if keytag_ in _DATAMAP]

            for keytag_ in mediadatatags_:
                widgetname_ = _DATAMAP[keytag_]

                tagValue = self._get_value(keytag_)
                if tagValue:

                    if widgetname_ in ["ExifLabel", "Description", "Artist", "Copyright"]:
                        self.exif_widgets[widgetname_].set_text(tagValue)

                    # Last Changed/ Modified...
                    elif widgetname_ in ["Modified", "Original"]:
                        use_date = _format_datetime(tagValue)
                        if use_date:
                            self.exif_widgets[widgetname_].set_text(use_date)
                            self.exif_widgets["Modified"].set_editable(False)
                        else:
                            self.exif_widgets["Modified"].set_editable(True) 

                    # LatitudeRef, Latitude, LongitudeRef, Longitude...
                    elif widgetname_ == "Latitude":

                        latitude, longitude = tagValue, self._get_value(_DATAMAP["Longitude"])

                        # if latitude and longitude exist, display them?
                        if (latitude and longitude):

                            # split latitude metadata into (degrees, minutes, and seconds)
                            latdeg, latmin, latsec = rational_to_dms(latitude)

                            # split longitude metadata into degrees, minutes, and seconds
                            longdeg, longmin, longsec = rational_to_dms(longitude)

                            # check to see if we have valid GPS Coordinates?
                            latfail = any(coords == False for coords in [latdeg, latmin, latsec])
                            longfail = any(coords == False for coords in [longdeg, longmin, longsec])
                            if (not latfail and not longfail):

                                # Latitude Direction Reference
                                LatRef = self._get_value(_DATAMAP["LatitudeRef"] )

                                # Longitude Direction Reference
                                LongRef = self._get_value(_DATAMAP["LongitudeRef"] )

                                # set display for Latitude GPS Coordinates
                                latitude = """%s° %s′ %s″ %s""" % (latdeg, latmin, latsec, LatRef)
                                self.exif_widgets["Latitude"].set_text(latitude)

                                # set display for Longitude GPS Coordinates
                                longitude = """%s° %s′ %s″ %s""" % (longdeg, longmin, longsec, LongRef)
                                self.exif_widgets["Longitude"].set_text(longitude)

#                                latitude, longitude = self.__convert2dms(self.plugin_image)
 
                                self.exif_widgets["Latitude"].validate()
                                self.exif_widgets["Longitude"].validate()

                    elif widgetname_ == "Altitude":
                        altitude = tagValue
                        AltitudeRef = self._get_value(_DATAMAP["AltitudeRef"])
 
                        if (altitude and AltitudeRef):
                            altitude = convert_value(altitude)
                            if altitude:
                                if AltitudeRef == "1":
                                    altitude = "-" + altitude
                                self.exif_widgets[widgetname_].set_text(altitude)

        else:
            # set Edit Message Area to None...
            self.exif_widgets["Edit:Message"].set_text(_("There is NO Exif metadata for this image."))

            for widget in _TOOLTIPS.keys():

                # once the user types in that field,
                # the Edit, Clear, and Delete buttons will become active...
                self.exif_widgets[widget].connect("changed", self.active_buttons)

    def _set_value(self, keytag_, keyvalue_):
        """
        sets the value for the metadata keytag_s
        """

        tagclass_ = keytag_[0:4]
        if LesserVersion:
            self.plugin_image[keytag_] = keyvalue_

        else:
            try:
                self.plugin_image.__setitem__(keytag_, keyvalue_)
            except KeyError:
                if tagclass_ == "Exif":
                    self.plugin_image[keytag_] = pyexiv2.ExifTag(keytag_, keyvalue_)

                elif tagclass_ == "Xmp.":
                    self.plugin_image[keytag_] =  pyexiv2.XmpTag(keytag_, keyvalue_)

                elif tagclass_ == "Iptc":
                    self.plugin_image[keytag_] = IptcTag(keytag_, keyvalue_)

            except (ValueError, AttributeError):
                pass

    def write_metadata(self, plugininstance):
        """
        writes the Exif metadata to the image.

        LesserVersion -- prior to pyexiv2-0.2.0
                      -- pyexiv2-0.2.0 and above... 
        """
        if LesserVersion:
            plugininstance.writeMetadata()

        else:
            plugininstance.write()

    def close_window(self, widgetWindow):
        """
        closes the window title by widgetWindow.
        """

        lambda w: widgetWindow.destroy()

    def convert_format(self, latitude, longitude, format):
        """
        Convert GPS Coordinates into a specified format.
        """

        if (not latitude and not longitude):
            return [False]*2

        latitude, longitude = conv_lat_lon(  unicode(latitude),
                                            unicode(longitude),
                                            format)
        return latitude, longitude

    def __decimalbutton(self):

        latitude  =  self.exif_widgets["Latitude"].get_text()
        longitude = self.exif_widgets["Longitude"].get_text()

        latitude, longitude = self.__convert2decimal(latitude, longitude, True)

    def __dmsbutton(self):

        latitude  =  self.exif_widgets["Latitude"].get_text()
        longitude = self.exif_widgets["Longitude"].get_text()

        latitude, longitude = self.__convert2dms(latitude, longitude, True)

    def __convert2decimal(self, latitude =False, longitude =False, display =False):
        """
        will convert a decimal GPS Coordinates into decimal format.
        """

        if (not latitude and not longitude):
            return [False]*2

        latitude, longitude = self.convert_format(latitude, longitude, "D.D8")

        # display the results only if the convert gps buttons are pressed...
        if display:
            self.exif_widgets["Latitude"].set_text(latitude)
            self.exif_widgets["Longitude"].set_text(longitude)

        return latitude, longitude

    def __convert2dms(self, latitude =False, longitude =False, display =False):
        """
        will convert a decimal GPS Coordinates into degrees, minutes, seconds
        for display only
        """

        if (not latitude and not longitude):
            return [False]*2

        latitude, longitude = self.convert_format(latitude, longitude, "DEG-:")

        # display the results only if the convert gps buttons are pressed...
        if display:
            self.exif_widgets["Latitude"].set_text(latitude)
            self.exif_widgets["Longitude"].set_text(longitude)

        return latitude, longitude

    def save_metadata(self, datatags_ =None):
        """
        gets the information from the plugin data fields
        and sets the keytag_ = keyvalue image metadata
        """
        db = self.dbstate.db

        # get a copy of all the widgets...
        datatags_ = ( (widget, self.exif_widgets[widget].get_text() ) for widget in _TOOLTIPS.keys() )

        for widgetname_, widgetvalue_ in datatags_:

            # Exif Label, Description, Artist, Copyright...
            if widgetname_ in ["ExifLabel", "Description", "Artist", "Copyright"]:
                self._set_value(_DATAMAP[widgetname_], widgetvalue_)

            # Modify Date/ Time...
            elif widgetname_ == "Modified":
                date1 = self.dates["Modified"]
                widgetvalue_ = date1 if date1 is not None else datetime.now()
                self._set_value(_DATAMAP[widgetname_], widgetvalue_)

                # display modified date in its cell...
                displayed = _format_datetime(widgetvalue_)
                if displayed:
                    self.exif_widgets[widgetname_].set_text(displayed)
 
            # Original Date/ Time...
            elif widgetname_ == "Original":
                widgetvalue_ = self.dates["Original"]
                if widgetvalue_ is not None:
                    self._set_value(_DATAMAP[widgetname_], widgetvalue_)

                    # modify the media object date if it is not already set?
                    mediaobj_date = self.orig_image.get_date_object()
                    if mediaobj_date.is_empty():
                        objdate = Date()
                        try:
                            objdate.set_yr_mon_day(widgetvalue_.get_year(),
                                                   widgetvalue_.get_month(),
                                                   widgetvalue_.get_day() )
                            gooddate = True
                        except ValueError:
                            gooddate = False

                        if gooddate:

                            # begin database tranaction to save media object's date...
                            with DbTxn(_("Create Date Object"), db) as trans:
                                self.orig_image.set_date_object(objdate)

                                db.disable_signals()
                                db.commit_media_object(self.orig_image, trans)

                                db.enable_signals()
                                db.request_rebuild()

            # Latitude/ Longitude...
            elif widgetname_ == "Latitude":
                latitude  =  self.exif_widgets["Latitude"].get_text()
                longitude = self.exif_widgets["Longitude"].get_text()
                if (latitude and longitude):
                    if (latitude.count(" ") == longitude.count(" ") == 0):
                        latitude, longitude = self.__convert2dms(latitude, longitude)

                    if (latitude.count(":") == longitude.count(":") >= 1):

                        # remove symbols before saving...
                        latitude, longitude = _removesymbolsb4saving(
                                self.exif_widgets["Latitude"].get_text(),
                                self.exif_widgets["Longitude"].get_text() )

                        latref = "N"
                        if latitude[0] == "-":
                            latitude = latitude.replace("-", '')
                            latref = "S"

                        longref = "E"
                        if longitude[0] == "-":
                            longitude = longitude.replace("-", '')
                            longref = "W"

                    # convert Latitude/ Longitude into pyexiv2.Rational()...
                    latitude  =  coords_to_rational(latitude)
                    longitude = coords_to_rational(longitude)
                    print(latitude, longitude)

                    # save LatitudeRef/ Latitude... 
                    self._set_value(_DATAMAP["LatitudeRef"], latref)
                    self._set_value(_DATAMAP["Latitude"], latitude)

                    # save LongitudeRef/ Longitude...
                    self._set_value(_DATAMAP["LongitudeRef"], longref)
                    self._set_value(_DATAMAP["Longitude"], longitude) 

            # Altitude, and Altitude Reference...
            elif widgetname_ == "Altitude":
                altitude = widgetvalue_ 
                if altitude:
                    if "-" in altitude:
                        altitude = altitude.replace("-", "")
                        altituderef = "1"
                    else:
                        altituderef = "0"
                    altitude = coords_to_rational(altitude)

                    # convert altitude to pyexiv2.Rational for saving... 
                    self._set_value(_DATAMAP["AltitudeRef"], altituderef)
                    self._set_value(_DATAMAP[widgetname_], altitude)

        # writes all Exif Metadata to image even if the fields are all empty so as to remove the value...
        self.write_metadata(self.plugin_image)

        if datatags_:
            # set Message Area to Saved...
            self.exif_widgets["Edit:Message"].set_text(_("Saving Exif metadata to this image..."))
        else:
            # set Edit Message to Cleared...
            self.exif_widgets["Edit:Message"].set_text(_("All Exif metadata has been cleared..."))

    def strip_metadata(self, mediadatatags =None):
        """
        Will completely and irrevocably erase all Exif metadata from this image.
        """

        # make sure the image has Exif metadata...
        mediadatatags_ = _get_exif_keypairs(self.plugin_image)
        if not mediadatatags_:
            return

        if EXIV2_FOUND_:
            try:
                erase = subprocess.check_call( [EXIV2_FOUND_, "delete", self.image_path] )
                erase_results = str(erase) 

            except subprocess.CalledProcessError:
                erase_results = False

        else:
            if mediadatatags_: 
                for keytag_ in mediadatatags_:
                    del self.plugin_image[keytag_]
                erase_results = True

                # write wiped metadata to image...
                self.write_metadata(self.plugin_image)

        if erase_results:

            for widget in ["MediaLabel", "MimeType", "ImageSize", "MessageArea", "Total"]:
                self.exif_widgets[widget].set_text("") 

            # Clear the Viewing Area...
            self.model.clear()

            self.exif_widgets["MessageArea"].set_text(_("All Exif metadata "
                "has been deleted from this image..."))
            self.update()

        else:
            self.exif_widgets["MessageArea"].set_text(_("There was an error "
                "in stripping the Exif metadata from this image..."))

def _get_exif_keypairs(plugin_image):
    """
    Will be used to retrieve and update the Exif metadata from the image.
    """

    if not plugin_image:
        return False
     
    mediadatatags_ = [keytag_ for keytag_ in (plugin_image.exifKeys() if LesserVersion
        else chain( plugin_image.exif_keys,
                    plugin_image.xmp_keys,
                    plugin_image.iptc_keys) ) ]

    return mediadatatags_

def _removesymbolsb4saving(latitude, longitude):
    """
    will recieve a DMS with symbols and return it without them

    @param: latitude  --  Latitude GPS coordinates
    @param: longitude -- GPS Longitude coordinates
    """

    # check to see if latitude/ longitude exist?
    if (latitude and longitude):

        # remove degrees, minutes, seconds symbols if they exist in 
        # Latitude/ Longitude...
        for symbol in ["°", "#", "먊", "′", "'", '″', '"']:

            if symbol in latitude:
                latitude = latitude.replace(symbol, "")

            if symbol in longitude:
                longitude = longitude.replace(symbol, "")

    return latitude, longitude

def string_to_rational(coordinate):
    """
    convert string to rational variable for GPS
    """

    if coordinate:

        if '.' in coordinate:
            value1, value2 = coordinate.split('.')
            return pyexiv2.Rational(int(float(value1 + value2)), 10**len(value2))
        else:
            return pyexiv2.Rational(int(coordinate), 1)

def coords_to_rational(Coordinates):
    """
    returns the rational equivalent for Latitude/ Longitude,
    and Altitude...
    """

    # Latitude, Longitude...
    if " " in Coordinates:
        Coordinates = [string_to_rational(coordinate) for coordinate in Coordinates.split(" ")]

    if ":" in Coordinates:
        Coordinates = [string_to_rational(coordinate) for coordinate in Coordinates.split(":")]

    # Altitude...
    else:
        Coordinates = [string_to_rational(Coordinates)]

    return Coordinates

def convert_value(value):
    """
    will take a value from the coordinates and return its value
    """
    if isinstance(value, (Fraction, pyexiv2.Rational)):
        return str((Decimal(value.numerator) / Decimal(value.denominator)))

def rational_to_dms(coords):
    """
    takes a rational set of coordinates and returns (degrees, minutes, seconds)

    [Fraction(40, 1), Fraction(0, 1), Fraction(1079, 20)]
    """
    # coordinates look like:
    #     [Rational(38, 1), Rational(38, 1), Rational(150, 50)]
    # or [Fraction(38, 1), Fraction(38, 1), Fraction(318, 100)]   
    if isinstance(coords, list):
        if len(coords) == 3:
            return [convert_value(coordinate) for coordinate in coords]

    elif isinstance(coords, (Fraction, pyexiv2.Rational)):
        if len(coords) == 1:
            return convert_value(coords)

    return [False]*3

def _parse_datetime(value):
    """
    Parse date and time and return a datetime object.
    """
    value = value.rstrip()
    if not value:
        return None

    if value.find(u':') >= 0:
        # Time part present
        if value.find(u' ') >= 0:
            # Both date and time part
            date_text, time_text = value.rsplit(u' ', 1)
        else:
            # Time only
            date_text = u''
            time_text = value
    else:
        # Date only
        date_text = value
        time_text = u'00:00:00'

    date_part = _dp.parse(date_text)
    try:
        time_part = time.strptime(time_text, "%H:%M:%S")
    except ValueError:
        time_part = None

    if date_part.get_modifier() == Date.MOD_NONE and time_part is not None:
        return datetime(date_part.get_year(), 
                        date_part.get_month(),
                        date_part.get_day(),
                        time_part.tm_hour,
                        time_part.tm_min,
                        time_part.tm_sec)
    else:
        return None

def _format_datetime(value):
    """
    Convert a python datetime object into a string for display, using the
    standard Gramps date format.
    """
    if type(value) != datetime:
        return ''
    date_part = gen.lib.Date()
    date_part.set_yr_mon_day(value.year, value.month, value.day)
    date_str = _dd.display(date_part)
    time_str = _('%(hr)02d:%(min)02d:%(sec)02d') % {'hr': value.hour,
                                                    'min': value.minute,
                                                    'sec': value.second}
    return _('%(date)s %(time)s') % {'date': date_str, 'time': time_str}
