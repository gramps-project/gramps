# -*- coding: utf-8 -*-
 #!/usr/bin/python
# -*- coding: utf-8 -*-
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

# ************************************************************************
# Python Modules
# ************************************************************************
import os
from datetime import datetime, date
import calendar, time


# abilty to escape certain characters from output...
from xml.sax.saxutils import escape as _html_escape

from itertools import chain

from decimal import Decimal, getcontext
getcontext().prec = 4
from fractions import Fraction

import subprocess

# ------------------------------------------------------------------------
# GTK modules
# ------------------------------------------------------------------------
import gtk

# ------------------------------------------------------------------------
# GRAMPS modules
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# GRAMPS modules
# ------------------------------------------------------------------------
import GrampsDisplay

from gen.plug import Gramplet
from DateHandler import displayer as _dd

import gen.lib
import gen.mime
import Utils
from PlaceUtils import conv_lat_lon

from QuestionDialog import WarningDialog, QuestionDialog

from gen.ggettext import gettext as _

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

# to be able for people that have pyexiv2-0.1.3... 
LesserVersion = False

try:
    import pyexiv2
    software_version = pyexiv2.version_info

except ImportError, msg:
    WarningDialog(_("You need to install, %s or greater, for this addon "
        "to work. \n  I would recommend installing, %s, and it may be "
        "downloaded from here: \n%s") % ( Min_VERSION_str, Pref_VERSION_str,
        _DOWNLOAD_LINK), str(msg))
    raise Exception(_("Failed to load 'Edit Image Exif Metadata'..."))
               
# This only happends if the user has pyexiv2-0.1.3 installed
except AttributeError:
    LesserVersion = True

# the library is either not installed or does not meet 
# minimum required version for this addon....
if (software_version and (software_version < Min_VERSION)):
    msg = _("The minimum required version for pyexiv2 must be %s \n"
        "or greater.  Or you do not have the python library "
        "installed yet.  You may download it from here: %s\n\n "
        "I recommend getting, %s") % (Min_VERSION_str,
        _DOWNLOAD_LINK, Pref_VERSION_str)
    WarningDialog(msg)
    raise Exception(msg)

# *******************************************************************
#         Determine if we have access to outside Programs
#
# The programs are ImageMagick, and jhead
# * ImageMagick -- Convert and Delete all Exif metadata...
# * jhead       -- re-initialize a jpeg, and other features...
#********************************************************************
# Windows 32bit systems
system_platform = os.sys.platform
MAGICK_FOUND_ = False
JHEAD_FOUND_ = False
if system_platform == "win32":
    if Utils.search_for("convert.exe"):
        MAGICK_FOUND_ = "convert.exe"

    if Utils.search_for("jhead.exe"):
        _JHEAD_FOUND_ = "jhead.exe"

elif system_platform == "linux2":
    if Utils.search_for("convert"):
        MAGICK_FOUND_ = "convert"

    if Utils.search_for("jhead"):
        JHEAD_FOUND_ = "jhead"

else:
    if Utils.search_for("convert"):
        MAGICK_FOUND_ = "convert"

    if Utils.search_for("jhead"):
        JHEAD_FOUND_ = "jhead"

# if external programs are not found, let the user know about 
# the missing functionality?
if not MAGICK_FOUND_:
    print(_("ImageMagick's convert program was not found "
        "on this computer.\n  You may download it from "
        "here: %s...") % ("http://www.imagemagick.org/script/index.php"))

if not JHEAD_FOUND_:
    print(_("Jhead program was not found on this computer.\n"
        "You may download it from: %s...") % (
            "http://www.sentex.net/~mwandel/jhead/"))

# ------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------
# available image types for exiv2 and pyexiv2
# ["jpeg", "jpg", "exv", "tiff", "dng", "nef", "pef", "pgf", "png", "psd", "jp2"]

# define tooltips for all entries
_TOOLTIPS = {

    # Description...
    "Description"       : _("Provide a short descripion for this image."),

    # Artist 
    "Artist"            : _("Enter the Artist/ Author of this image.  The "
        "person's name or the company who is responsible for the creation "
        "of this image."),

    # Copyright
    "Copyright" : _("Enter the copyright information for this image. \n"
        "Example: (C) 2010 Smith and Wesson"),

    # Original Date/ Time... 
    "DateTime" : _("Original Date/ Time of this image.\n"
        "Example: 1826-Apr-12 14:30:00, 1826-April-12, 1998-01-31 13:30:00"),

    # GPS Latitude...
    "Latitude" : _(u"Enter the GPS Latitude coordinates for your image,\n"
        u"Example: 43.722965, 43 43 22 N, 38° 38′ 03″ N, 38 38 3"),

    # GPS Longitude...
    "Longitude" : _(u"Enter the GPS Longitude coordinates for your image,\n"
        u"Example: 10.396378, 10 23 46 E, 105° 6′ 6″ W, -105 6 6") }
_TOOLTIPS = dict( [widget, tooltip] for widget, tooltip in _TOOLTIPS.items() )

# set up Exif keys for Image.exif_keys
_DATAMAP = {
    "Exif.Image.ImageDescription"  : "Description",
    "Exif.Image.DateTime"          : "Modified",
    "Exif.Image.Artist"            : "Artist",
    "Exif.Image.Copyright"         : "Copyright",
    "Exif.Photo.DateTimeOriginal"  : "DateTime",
    "Exif.GPSInfo.GPSLatitudeRef"  : "LatitudeRef",
    "Exif.GPSInfo.GPSLatitude"     : "Latitude",
    "Exif.GPSInfo.GPSLongitudeRef" : "LongitudeRef",
    "Exif.GPSInfo.GPSLongitude"    : "Longitude"}
_DATAMAP  = dict( (key, val) for key, val in _DATAMAP.items() )
_DATAMAP.update( (val, key) for key, val in _DATAMAP.items()  )

# Toolt tips for the buttons in the gramplet...
_BUTTONTIPS = {

    # copyto button...
    "CopyTo" : _("Copies information from the Display area to the Edit area."),

    # Clear Edit Area button... 
    "Clear" : _("Clears the Exif metadata from the Edit area."),

    # Wiki Help button...
    "Help" : _("Displays the Gramps Wiki Help page for 'Edit Image "
        "Exif Metadata' in your web browser."),

    # Save Exif Metadata button...
    "Save" : _("Saves/ writes the Exif metadata to this image.\n"
        "WARNING: Exif metadata will be erased if you save a blank entry field...") }

# if ImageMagick is installed on this computer then, add button 
# tooltips for these two buttons...
if MAGICK_FOUND_:
    _BUTTONTIPS.update( {

        # Convert to .Jpeg button...
        "Convert" : _("If your image is not a jpeg image, convert it to jpeg?"),

        # Delete/ Erase/ Wipe Exif metadata button...
        "Delete" : _("WARNING:  This will completely erase all Exif metadata "
            "from this image!  Are you sure that you want to do this?") } )
_BUTTONTIPS = dict( [widget, tooltip] for widget, tooltip in _BUTTONTIPS.items() )

# ------------------------------------------------------------------------
#
# 'Edit Image Exif metadata' Gramplet class...
#
# ------------------------------------------------------------------------
class EditExifMetadata(Gramplet):

    def init(self):

        self.exif_column_width = 12
        self.exif_widgets = {}

        # set all dirty variables to False to begin this addon...
        self._dirty = False

        self.orig_image    = False
        self.image_path    = False
        self.plugin_image  = False

        self.connect_signal("Media", self.update)
        vbox = self.__build_gui()

        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(vbox)
        vbox.show_all()

        # provide tooltips for all fields and buttons...
        _setup_widget_tooltips(self.exif_widgets)

    def __build_gui(self):

        vbox = gtk.VBox()

        medialabel = gtk.HBox(False)
        self.exif_widgets["Media:Label"] = gtk.Label()
        self.exif_widgets["Media:Label"].set_alignment(0.0, 0.0)
        medialabel.pack_start(self.exif_widgets["Media:Label"], expand =False)
        vbox.pack_start(medialabel, expand =False)

        mimetype = gtk.HBox(False)
        self.exif_widgets["Mime:Type"] = gtk.Label()
        self.exif_widgets["Mime:Type"].set_alignment(0.0, 0.0)
        mimetype.pack_start(self.exif_widgets["Mime:Type"], expand =False)
        vbox.pack_start(mimetype, expand =False)

        messagearea = gtk.HBox(False)
        self.exif_widgets["Message:Area"] = gtk.Label(_("Click an image to begin..."))
        self.exif_widgets["Message:Area"].set_alignment(0.5, 0.0)
        messagearea.pack_start(self.exif_widgets["Message:Area"], expand =False)
        vbox.pack_start(messagearea, expand =False)

        self.model = gtk.ListStore(object, str, str)
        view = gtk.TreeView(self.model)

        # Key Column
        view.append_column( self.__create_column(_("Key"), 1) )

        # Value Column
        view.append_column( self.__create_column(_("Value"), 2) )

        # copyto, Clear, Convert horizontal box
        ccc_box = gtk.HButtonBox()
        ccc_box.set_layout(gtk.BUTTONBOX_START)
        vbox.pack_start(ccc_box, expand =False, fill =False, padding =10)

        # Copy To Edit Area button...
        ccc_box.add( self.__create_button(
            "CopyTo", False, [self.copyto], gtk.STOCK_COPY, False) )

        # Clear button...
        ccc_box.add( self.__create_button(
            "Clear", False, [self.clear_metadata], gtk.STOCK_CLEAR, False) )

        # is ImageMagick installed?
        if MAGICK_FOUND_:
            # Convert button...
            ccc_box.add( self.__create_button(
                "Convert", False, [self.__convert_dialog],
                    gtk.STOCK_CONVERT, False) )

        for items in [

            # Image Description
            ("Description",     _("Description"),     None, False, [],  True,  0),

            # Last Modified Date/ Time
            ("Modified",        _("Last Changed"),    None, True,  [],  True,  0),

            # Artist field
            ("Artist",          _("Artist"),          None, False, [],  True,  0),

            # copyright field
            ("Copyright",       _("Copyright"),       None, False, [],  True,  0),

            # calendar date clickable entry
            ("Date",            "",                   None, True,
            [("Select",         _("Select Date"),  "button", self.select_date)],
                                                                     True,  0),
            # Original Date/ Time Entry, 1826-April-12 14:06:00
            ("DateTime",         _("Date/ Time"),     None, False, [], True, 0),

            # Convert GPS coordinates
            ("GPSFormat",       _("Convert GPS"),     None, True,
            [("Decimal",        _("Decimal"),         "button", self.convert2decimal),
             ("DMS",            _("Deg. Min. Sec."),  "button", self.convert2dms)], 
                                                                       False, 0),    
  
            # Latitude and Longitude for this image 
            ("Latitude",        _("Latitude"),        None, False, [],  True,  0),
            ("Longitude",       _("Longitude"),       None, False, [],  True,  0) ]:

            pos, text, choices, readonly, callback, dirty, default = items
            row = self.make_row(pos, text, choices, readonly, callback, dirty, default)
            vbox.pack_start(row, False)

        # Help, Save, Delete horizontal box
        hsd_box = gtk.HButtonBox()
        hsd_box.set_layout(gtk.BUTTONBOX_START)
        vbox.pack_start(hsd_box, expand =False, fill =False, padding =10)

        # Help button...
        hsd_box.add( self.__create_button(
            "Help", False, [self._help_page], gtk.STOCK_HELP) )

        # Save button...
        hsd_box.add( self.__create_button(
            "Save", False, [self.save_metadata, self.update, self.display_exif_tags, self.copyto],
                gtk.STOCK_SAVE, False))

        if MAGICK_FOUND_:
            # Delete All Metadata button...
            hsd_box.add(self.__create_button(
                "Delete", False, [self.__delete_dialog], gtk.STOCK_DELETE, False))

        # adds Exif Metadata Viewing Area
        vbox.pack_start(view, padding =10)

        return vbox

    def update_has_data(self):
        active_handle = self.get_active('Media')
        active = self.dbstate.db.get_object_from_handle(active_handle)
        self.set_has_data(self.get_has_data(active))

    def get_has_data(self, media):
        """
        Return True if the gramplet has data, else return False.
        """
        if media is None:
            return False

        full_path = Utils.media_path_full(self.dbstate.db, media.get_path() )
        if not os.path.isfile(full_path):
            return False

        if LesserVersion: # prior to v0.2.0
            metadata = pyexiv2.Image(full_path)
            try:
                metadata.readMetadata()
            except (IOError, OSError):
                return False

            if metadata.exifKeys():
                return True

        else: # v0.2.0 and above
            metadata = pyexiv2.ImageMetadata(full_path)
            try:
                metadata.read()
            except (IOError, OSError):
                return False

            if metadata.exif_keys:
                return True

        return False

    def _help_page(self):
        """
        will bring up a Wiki help page.
        """

        GrampsDisplay.help(webpage = "Edit Image Exif Metadata")

    def activate_buttons(self, ButtonList):
        """
        Enable/ activate the buttons that are in ButtonList
        """

        for ButtonName in ButtonList:
            self.exif_widgets[ButtonName].set_sensitive(True)

    def deactivate_buttons(self, ButtonList):
        """
        disable/ de-activate buttons in ButtonList
        """
        for ButtonName in ButtonList:
            self.exif_widgets[ButtonName].set_sensitive(False)

    def main(self): # return false finishes
        """
        get the active media, mime type, and reads the image metadata
        """
        db = self.dbstate.db

        # clear Display and Edit Areas
        self.clear_metadata(self.orig_image)
        self.model.clear()

        # De-activate the buttons except for Help...
        self.deactivate_buttons(["CopyTo", "Clear", "Save"])

        # de-activate the Convert and Delete buttons...
        if MAGICK_FOUND_:
            self.deactivate_buttons(["Convert", "Delete"])

        # Re-post initial image message...
        self.exif_widgets["Message:Area"].set_text(_("Select an "
            "image to begin..."))

        active_handle = self.get_active("Media")
        if not active_handle:
            self.set_has_data(False)
            return

        self.orig_image = db.get_object_from_handle(active_handle)
        self.image_path = Utils.media_path_full(db, self.orig_image.get_path() )
        if (not self.orig_image or not os.path.isfile(self.image_path)):

            # set Message Area to Missing/ Delete...
            self.exif_widgets["Message:Area"].set_text(_("Image is either "
                "missing or deleted,\n  Choose a different image..."))
            return

        # check image read privileges...
        _readable = os.access(self.image_path, os.R_OK)
        if not _readable:
            self.exif_widgets["Message:Area"].set_text(_("Image is NOT readable,\n"
                "Choose a different image..."))
            return

        # check image write privileges...
        _writable = os.access(self.image_path, os.W_OK)
        if not _writable:
            self.exif_widgets["Message:Area"].set_text(_("Image is NOT writable,\n"
                "You will NOT be able to save Exif metadata...."))

        # display file description/ title...
        self.exif_widgets["Media:Label"].set_text( _html_escape(
            self.orig_image.get_description()) )

        # Mime type information...
        mime_type = self.orig_image.get_mime_type()
        _mtype = gen.mime.get_description(mime_type)
        self.exif_widgets["Mime:Type"].set_text(_mtype)

        # determine if it is a mime image object?
        if mime_type:
            if mime_type.startswith("image"):
                self.activate_buttons(["Save"])

                # set all data fields to editable...
                for widget in _TOOLTIPS.keys():
                    self.exif_widgets[widget].set_editable(True)

                # will create the image and read it...
                self.setup_image(self.image_path, True)

                # Checks to make sure that ImageMagick is installed on 
                # this computer and the image is NOT a jpeg image...
                if MAGICK_FOUND_:
                    basename, extension = os.path.splitext(self.image_path)
                    if extension not in [".jpeg", ".jpg", ".jfif"]:
                        self.activate_buttons(["Convert"])

                # displays the imge Exif metadata
                self.display_exif_tags()
                imagefile = True

            else:
                self.exif_widgets["Message:Area"].set_text(_("Choose a "
                    "different image..."))
                imagefile = False
        else:
            self.exif_widgets["Message:Area"].set_text(_("Choose a "
                "different image..."))
            imagefile = False

        if not imagefile:

            # set all data fields to not editable and set a connect to the data fields...
            for widget in _TOOLTIPS.keys():
                self.exif_widgets[widget].set_editable(False)

    def __create_column(self, name, colnum, fixed =True):
        """
        will create the column for the column row...
        """

        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(name, renderer, text =colnum)

        if fixed:
            column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
            column.set_expand(True)

        else:
            column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
            column.set_expand(False)

        column.set_alignment(0.0)
        column.set_sort_column_id(colnum)

        return column

    def __create_button(self, pos, text, callback =False , icon =False, sensitive = True):
        """
        creates and returns a button for display
        """

        if (icon and not text):
            button = gtk.Button(stock=icon)
        else:
            button = gtk.Button(text)

        if callback is not []:
            for call_ in callback:
                button.connect("clicked", call_)

        if not sensitive:
            button.set_sensitive(False)
        self.exif_widgets[pos] = button

        return button

    def __convert_dialog(self, object):
        """
        Handles the Convert question Dialog...
        """

        # is ImageMagick installled?
        if MAGICK_FOUND_:
            QuestionDialog(_("Edit Image Exif Metadata"), _("Convert this "
                "image to a .jpeg image?"), _("Convert"), self.convert2Jpeg)

    def __delete_dialog(self, object):
        """
        Handles the Delete Dialog...
        """

        QuestionDialog(_("Edit Image Exif Metadata"), _("WARNING!  You are "
            "about to completely delete the Exif metadata from this image?"),
            _("Delete"), self.strip_metadata)

    def setup_image(self, full_path, createimage =False):
        """
        will return an image instance and read the Exif metadata.

        if createimage is True, it will create the pyexiv2 image instance...

        LesserVersion -- prior to pyexiv2-0.2.0
                      -- pyexiv2-0.2.0 and above...
        """

        if createimage:
            if LesserVersion:
                self.plugin_image = pyexiv2.Image(full_path)
            else:
                self.plugin_image = pyexiv2.ImageMetadata(full_path)

        if LesserVersion:
            try:
                self.plugin_image.readMetadata()
            except (IOError, OSError):
                self.set_has_data(False)
                return 

        else:
            try:
                self.plugin_image.read()
            except (IOError, OSError):
                self.set_has_data(False)
                return

    def make_row(self, pos, text, choices=None, readonly=False, 
        callback_list =[], mark_dirty=False, default=0):

        # Edit Image Exif Metadata
        row = gtk.HBox()
        label = gtk.Label()
        if readonly:
            label.set_text("<b>%s</b>" % text)
            label.set_width_chars(self.exif_column_width)
            label.set_use_markup(True)
            self.exif_widgets[pos] = gtk.Label()
            self.exif_widgets[pos].set_alignment(0.0, 0.5)
            self.exif_widgets[pos].set_use_markup(True)
            label.set_alignment(0.0, 0.5)
            row.pack_start(label, False)
            row.pack_start(self.exif_widgets[pos], False)
        else:
            label.set_text("%s: " % text)
            label.set_width_chars(self.exif_column_width)
            label.set_alignment(1.0, 0.5) 
            if choices == None:
                self.exif_widgets[pos] = gtk.Entry()
                if mark_dirty:
                    self.exif_widgets[pos].connect("changed", self._mark_dirty)
                row.pack_start(label, False)
                row.pack_start(self.exif_widgets[pos], True)
            else:
                eventBox = gtk.EventBox()
                self.exif_widgets[pos] = gtk.combo_box_new_text()
                eventBox.add(self.exif_widgets[pos])
                for add_type in choices:
                    self.exif_widgets[pos].append_text(add_type)
                self.exif_widgets[pos].set_active(default) 
                if mark_dirty:
                    self.exif_widgets[pos].connect("changed", self._mark_dirty)
                row.pack_start(label, False)
                row.pack_start(eventBox, True)
        for name, text, cbtype, callback in callback_list:
            if cbtype == "button":
                label = gtk.Label()
                label.set_text(text)
                self.exif_widgets[pos + ":" + name + ":Label"] = label
                row.pack_start(label, False)
                icon = gtk.STOCK_EDIT
                size = gtk.ICON_SIZE_MENU
                button = gtk.Button()
                image = gtk.Image()
                image.set_from_stock(icon, size)
                button.add(image)
                button.set_relief(gtk.RELIEF_NONE)
                button.connect("clicked", callback)
                self.exif_widgets[pos + ":" + name] = button
                row.pack_start(button, False)
            elif cbtype == "checkbox":
                button = gtk.CheckButton(text)
                button.set_active(True)
                button.connect("clicked", callback)
                self.exif_widgets[pos + ":" + name] = button
                row.pack_start(button, False)
        row.show_all()
        return row

# -----------------------------------------------
# Error Checking functions
# -----------------------------------------------
    def _mark_dirty(self, object):
        pass

    def _get_value(self, keytag):
        """
        gets the value from the Exif Key, and returns it...

        @param: keytag -- image metadata key
        """

        KeyValue = ""
        if LesserVersion:
            KeyValue = self.plugin_image[keytag]
        else:
            try:
                KeyValue = self.plugin_image[keytag].value

            except (KeyError, ValueError, AttributeError):
                pass

        return KeyValue

    def display_exif_tags(self, mediadatatags_ =None):
        """
        once the pyexiv2.Image has been created, we display
            all of the image Exif metadata...
        """

        self.model.clear()

        mediadatatags_ = _get_exif_keypairs(self.plugin_image)
        if mediadatatags_:

            # set has data flag...
            self.set_has_data(True)

            # Activate Clear and Save buttons...
            self.activate_buttons(["Clear", "Save", "CopyTo"])

            # set Message Area to Display...
            self.exif_widgets["Message:Area"].set_text(_("Displaying image "
                "Exif metadata..."))

            for keytag in mediadatatags_:

                if LesserVersion:
                    label = self.plugin_image.tagDetails(keytag)[0]
                    human_value = self.plugin_image.interpretedExifValue(keytag)
                else:
                    try:
                        tag = self.plugin_image[keytag]
                        label = tag.label
                        human_value = tag.human_value
                    except AttributeError:
                        human_value = False

                if keytag in ("Exif.Image.DateTime",
                    "Exif.Photo.DateTimeOriginal",
                    "Exif.Photo.DateTimeDigitized"):
                    human_value = _process_datetime(self._get_value(keytag))

                if human_value is not False:
                    self.model.append((self.plugin_image, label, human_value))

        # there is no Exif metadata for this image yet...
        else:

            self.set_has_data(False)

            # set Message Area to None...
            self.exif_widgets["Message:Area"].set_text(_("No Exif metadata for "
                "this image not yet..."))

    def copyto(self, imagekeytags_ =None):
        """
        reads the image metadata after the pyexiv2.Image has been created
        """

        imagekeytags_ = _get_exif_keypairs(self.plugin_image)

        if imagekeytags_:
            imagekeytags_ = [keytag for keytag in imagekeytags_ if keytag in _DATAMAP]

            self.exif_widgets["Message:Area"].set_text(_("Copying Exif "
                "metadata to the Edit Area..."))

        for keytag in imagekeytags_:

            # name for matching to exif_widgets 
            widgetsName = _DATAMAP[keytag]

            tagvalue_ = self._get_value(keytag)
            if tagvalue_:

                if widgetsName in ["Description", "Artist", "Copyright"]:
                    self.exif_widgets[widgetsName].set_text(tagvalue_)

                # Original Date of the image...
                elif widgetsName == "DateTime":
                    use_date = self._get_value(keytag)
                    use_date = _process_datetime(use_date) if use_date else False
                    if use_date is not False:
                        self.exif_widgets[widgetsName].set_text(use_date)

                # latituderef, Latitude, longituderef, Longitude...
                elif widgetsName == "Latitude":

                    latitude  =  self._get_value(keytag)
                    longitude = self._get_value(_DATAMAP["Longitude"] )

                    # if latitude and longitude exist, display them?
                    if (latitude and longitude):

                        # split latitude metadata into (degrees, minutes, 
                        # and seconds) from Rational
                        latdeg, latmin, latsec = rational_to_dms(latitude)

                        # split longitude metadata into degrees, minutes, and seconds
                        longdeg, longmin, longsec = rational_to_dms(longitude)

                        # check to see if we have valid GPS coordinates?
                        latfail = any(coords == False for coords in [latdeg, latmin, latsec])
                        longfail = any(coords == False for coords in [longdeg, longmin, longsec])
                        if (not latfail and not longfail):

                            # Latitude Direction Reference
                            latituderef = self._get_value(_DATAMAP["LatitudeRef"] )

                            # Longitude Direction Reference
                            longituderef = self._get_value(_DATAMAP["LongitudeRef"] )

                            # set display for Latitude GPS coordinates
                            self.exif_widgets["Latitude"].set_text(
                                """%s° %s′ %s″ %s""" % (latdeg, latmin, latsec, latituderef))

                            # set display for Longitude GPS coordinates
                            self.exif_widgets["Longitude"].set_text(
                                """%s° %s′ %s″ %s""" % (longdeg, longmin, longsec, longituderef))

        # enable Save button after metadata has been "Copied to Edit Area"...
        self.activate_buttons(["Save"])

        if MAGICK_FOUND_:
            self.activate_buttons(["Delete"])

        # Clear the Message Area...
        self.exif_widgets["Message:Area"].set_text("")

    def clear_metadata(self, obj, cleartype = "All"):
        """
        clears all data fields to nothing

        @param: cleartype -- 
            "Date" = clears only Date entry fields
            "All" = clears all data fields
        """

        # set Message Area text...
        self.exif_widgets["Message:Area"].set_text(_("Edit area has been cleared..."))

        # clear all data fields
        if cleartype == "All":
            for widgetsName in ["Description", "Artist", "Copyright", "DateTime",
                "Latitude", "Longitude"]:  
                self.exif_widgets[widgetsName].set_text("")

        # clear only the date/ time field
        else:
             self.exif_widgets["DateTime"].set_text("")

    def convert2Jpeg(self):
        """
        Will attempt to convert an image to jpeg if it is not?
        """

        # if ImageMagick's convert is installed...
        if MAGICK_FOUND_:

            filepath, basename = os.path.split(self.image_path)
            basename, oldext = os.path.splitext(self.image_path)
            newextension = ".jpeg"

            convert = subprocess.check_call(["convert", self.image_path, 
                    os.path.join(filepath, basename + newextension) ] )
            if str(convert):

                # set Message Area to Convert...
                self.exif_widgets["Message:Area"].set_text(_("Converting image,\n"
                    "You will need to delete the original image file..."))

                self.deactivate_buttons(["Convert"])

    def _set_exif_keytag(self, keytag, KeyValue):
        """
        sets the value for the metadata keytags
        """

        if LesserVersion:
            self.plugin_image[keytag] = KeyValue

        else:
            try:  # tag is being modified...
                self.plugin_image[keytag] = KeyValue

            except KeyError:  # tag has not been set...
                self.plugin_image[keytag] = pyexiv2.ExifTag(keytag, KeyValue)

            except (ValueError, AttributeError):  # there is an issue with 
                                                  # either keytag or KeyValue
                pass

    def write_metadata(self, imageinstance):
        """
        writes the Exif metadata to the image.

        LesserVersion -- prior to pyexiv2-0.2.0
                      -- pyexiv2-0.2.0 and above... 
        """
        if LesserVersion:
            imageinstance.writeMetadata()

        else:
            imageinstance.write()

    def addsymbols2gps(self, latitude =False, longitude =False):
        """
        converts a degrees, minutes, seconds representation of 
        Latitude/ Longitude
        without their symbols to having them...
        """

        if not latitude and not longitude:
            return [False]*2

        latituderef, longituderef = "N", "E"

        if (latitude.count(".") == 1 and longitude.count(".") == 1):
            latitude, longitude = self.convert2dms(latitude, longitude)

        # add DMS symbols if necessary?
        # the conversion to decimal format, require the DMS symbols
        elif ( (latitude.count("°") == 0 and longitude.count("°") == 0) and
            (latitude.count("′") == 0 and longitude.count("′") == 0) and
            (latitude.count('″') == 0 and longitude.count('″') == 0) ):

            # is there a direction element here?
            if (latitude.count("N") == 1 or latitude.count("S") == 1):
                latdeg, latmin, latsec, latituderef = latitude.split(" ", 3)
            else:
                atitudeRef = "N"
                latdeg, latmin, latsec = latitude.split(" ", 2)
                if latdeg[0] == "-":
                    latdeg = latdeg.replace("-", "")
                    latituderef = "S"

            # is there a direction element here?
            if (longitude.count("E") == 1 or longitude.count("W") == 1):
                longdeg, longmin, longsec, longituderef = longitude.split(" ", 3)
            else:
                longituderef = "E"
                longdeg, longmin, longsec = longitude.split(" ", 2)
                if longdeg[0] == "-":
                    longdeg = longdeg.replace("-", "")
                    longituderef = "W"

            latitude  = """%s° %s′ %s″ %s""" % (latdeg, latmin, latsec, latituderef)
            longitude = """%s° %s′ %s″ %s""" % (longdeg, longmin, longsec, longituderef)

        return latitude, longitude

    def convert2decimal(self, object):
        """
        will convert a decimal GPS coordinates into decimal format.

        @param: latitude  -- GPS Latitude coordinates from data field...
        @param: longitude -- GPS Longitude coordinates from data field...
        """

        latitude  =  self.exif_widgets["Latitude"].get_text()
        longitude = self.exif_widgets["Longitude"].get_text()

        if not latitude and not longitude:
            return

        # is Latitude/ Longitude are in DMS format?
        if (latitude.count(" ") >= 2 and longitude.count(" ") >= 2): 

            # add DMS symbols if necessary?
            # the conversion to decimal format, require the DMS symbols 
            if ( (latitude.count("°") == 0 and longitude.count("°") == 0) and
                (latitude.count("′") == 0 and longitude.count("′") == 0) and
                (latitude.count('″') == 0 and longitude.count('″') == 0) ):

                latitude, longitude = self.addsymbols2gps(latitude, longitude)

            # convert degrees, minutes, seconds w/ symbols to an 8 point decimal
            latitude, longitude = conv_lat_lon( unicode(latitude),
                                                unicode(longitude), "D.D8")

            self.exif_widgets["Latitude"].set_text(latitude)
            self.exif_widgets["Longitude"].set_text(longitude)
        return latitude, longitude

    def convert2dms(self, latitude =False, longitude =False):
        """
        will convert a decimal GPS coordinates into degrees, minutes, seconds
        for display only
        """

        latitude  =  self.exif_widgets["Latitude"].get_text()
        longitude = self.exif_widgets["Longitude"].get_text()

        if not latitude and not longitude:
            return [False]*2

        latituderef, longituderef = "N", "E"

        # if coordinates are in decimal format?
        if ((latitude.find(".") <= 6) and (longitude.find(".") <= 6)):

            # convert latitude and longitude to a DMS with separator of ":"
            latitude, longitude = conv_lat_lon(latitude, longitude, "DEG-:")
 
            # remove negative symbol if there is one?
            if latitude[0] == "-":
                latitude = latitude.replace("-", "")
                latituderef = "S"
            latdeg, latmin, latsec = latitude.split(":", 2)

           # remove negative symbol if there is one?
            if longitude[0] == "-":
                longitude = longitude.replace("-", "")
                longituderef = "W"
            longdeg, longmin, longsec = longitude.split(":", 2)

            latitude = """%s° %s′ %s″ %s""" % (latdeg, latmin, latsec, latituderef)
            self.exif_widgets["Latitude"].set_text(latitude)

            longitude = """%s° %s′ %s″ %s""" % (longdeg, longmin, longsec, longituderef)
            self.exif_widgets["Longitude"].set_text(longitude)
        return latitude, longitude

    def save_metadata(self, datatags =False):
        """
        gets the information from the plugin data fields
        and sets the keytag = keyvalue image metadata
        """

        # determine if there has been something entered in the data fields?
        datatags = (self.exif_widgets["Description"].get_text(), 
                    self.exif_widgets["Artist"].get_text(), 
                    self.exif_widgets["Copyright"].get_text(),
                    self.exif_widgets["DateTime"].get_text(),
                    self.exif_widgets["Latitude"].get_text(),
                    self.exif_widgets["Longitude"].get_text() )

        # Description data field
        description = self.exif_widgets["Description"].get_text() 
        self._set_exif_keytag(_DATAMAP["Description"], description)

        # Modify Date/ Time... not a data field, but saved anyway...
        self._set_exif_keytag(_DATAMAP["Modified"], datetime.now() )

        # display modified Date/ Time
        self.exif_widgets["Modified"].set_text(
                _format_datetime(datetime.now() ) )
 
        # Artist/ Author data field
        artist = self.exif_widgets["Artist"].get_text()
        self._set_exif_keytag(_DATAMAP["Artist"], artist)

        # Copyright data field
        copyright = self.exif_widgets["Copyright"].get_text()
        self._set_exif_keytag(_DATAMAP["Copyright"], copyright)

        # Original Date/ Time data field
        datetime_ = self.exif_widgets["DateTime"].get_text()
        if datetime_:
            datetime_ = _process_datetime(datetime_, False)
            if datetime_ is not False:
                self._set_exif_keytag(_DATAMAP["DateTime"], datetime_)

        # Latitude/ Longitude data fields...
        latitude  =  self.exif_widgets["Latitude"].get_text()
        longitude = self.exif_widgets["Longitude"].get_text()
        self.__process_lat_long(latitude, longitude)

        if datatags:
            # set Message Area to Saved...
            self.exif_widgets["Message:Area"].set_text(_("Saving Exif "
                    "metadata to the image..."))

        else:
            # set Message Area to Cleared...
            self.exif_widgets["Message:Area"].set_text(_("Image Exif "
                "metadata has been cleared from this image..."))

        # writes all Exif Metadata to image even if the fields are all empty.
        self.write_metadata(self.plugin_image)

        # Activate Delete button...
        if MAGICK_FOUND_:
            self.activate_buttons(["Delete"])

    def __process_lat_long(self, latitude, longitude):
        """
        process the latitude/ longitude for saving...
        """

        if (latitude and longitude):

            # remove leading and trailing whitespace...
            latitude  =  latitude.strip()
            longitude = longitude.strip()

            for chrs in ["/", ","]:
                if chrs in latitude:
                    latitude = latitude.replace(chrs, "")
                if chrs in longitude:
                    longitude = longitude.replace(chrs, "")

            # if there is no spaces then convert to DMS?
            if (latitude.find(" ") == longitude.find(" ") == -1):
                if ("." in latitude and "." in longitude):
                    latitude, longitude = self.convert2dms(latitude, longitude)

            # DMS is True...
            if ((latitude.find(" ") is not -1) and (longitude.find(" ") is not -1)):

                if latitude.find("N") > -1:
                    latituderef = "N"
                    latitude = latitude.replace("N", "")

                elif latitude.find(_("S")) > -1:
                    latituderef = "S"
                    latitude = latitude.replace("S", "")

                elif ((latitude.find(_("N")) == -1) and (latitude.find(_("S")) == -1)):
                    if latitude.find("-") == -1:
                        latituderef = "N"
                    else:
                        latituderef = "S"
                        latitude = latitude.replace("-", "")

                if longitude.find("E") > -1:
                    longituderef = "E"
                    longitude = longitude.replace("E", "")

                elif longitude.find("W") > -1:
                    longituderef = "W"
                    longitude = longitude.replace("W", "")

                elif ((longitude.find("E") == -1) and (longitude.find("W") == -1)):
                    if longitude.find("-") == -1:
                        longituderef = "E"
                    else:
                        longituderef = "W"
                        longitude = longitude.replace("-", "")

                # remove leading and trailing whitespace...
                latitude  =  latitude.strip()
                longitude = longitude.strip()

                # remove symbols before saving Latitude/ Longitude GPS coordinates
                latitude, longitude = _removesymbolsb4saving(latitude, longitude) 

                # convert to pyexiv2.Rational for saving...
                latitude  =  coords_to_rational(latitude)
                longitude = coords_to_rational(longitude)

            # save empty strings to delete Latitude, Longitude...
            else:
                latitude, latituderef = "", ""
                longitude, longituderef = "", ""

            # save Latitude and LatitudeRef
            self._set_exif_keytag(_DATAMAP["Latitude"], latitude)
            self._set_exif_keytag(_DATAMAP["LatitudeRef"], latituderef)

            # save Longitude and LongitudeRef
            self._set_exif_keytag(_DATAMAP["Longitude"], longitude)
            self._set_exif_keytag(_DATAMAP["LongitudeRef"], longituderef)

    def strip_metadata(self, erase_results =None):
        """
        Will completely and irrevocably erase all Exif metadata from this image.
        """

        if MAGICK_FOUND_:
            erase = subprocess.check_call( ["convert", self.image_path,
                "-strip", self.image_path] )
            erase_results = str(erase)

        else:
            mediadatatags_ = _get_exif_keypairs(self.plugin_image)
            if mediadatatags_: 
                for keytag in mediadatatags_:
                    del self.plugin_image[keytag]
                erase_results = True

                # write wiped metadata to image...
                self.write_metadata(self.plugin_image)

        if erase_results:

            # set Message Area for deleting...
            self.exif_widgets["Message:Area"].set_text(_("Deleting all Exif metadata..."))

            # Clear the Display and Edit Areas
            self.clear_metadata(self.plugin_image)
            self.model.clear()

            # Notify the User...
            self.exif_widgets["Message:Area"].set_text(_("All Exif metadata has been "
                    "deleted from this image..."))
            self.update()

            # re- initialize the image...
            if JHEAD_FOUND_:
                reinit = subprocess.check_call( ["jhead", "-purejpg", self.image_path] )
                reinitialize = str(reinit)
                if reinitialize:
                    self.exif_widgets["Message:Area"].set_text(_("Image has "
                    "be re- initialized for Exif metadata..."))

# -----------------------------------------------
#              Date Calendar functions
# -----------------------------------------------
    def select_date(self, object):
        """
        will allow you to choose a date from the calendar widget
        """
 
        tip = _("Double click a day to return the date.")

        self.app = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.app.tooltip = tip
        self.app.set_title(_("Select Date"))
        self.app.set_default_size(450, 200)
        self.app.set_border_width(10)
        self.exif_widgets["Calendar"] = gtk.Calendar()
        self.exif_widgets["Calendar"].connect('day-selected-double-click', self.double_click)
        self.app.add(self.exif_widgets["Calendar"])
        self.exif_widgets["Calendar"].show()
        self.app.show()

    def double_click(self, object):
        """
        receives double-clicked and returns the selected date
        widget
        """
        now = time.localtime()

        year, month, day = self.exif_widgets["Calendar"].get_date()
        self.exif_widgets["DateTime"].set_text( "%04d-%s-%02d %02d:%02d:%02d" % (
            year, _dd.long_months[month + 1], day, now[3], now[4], now[5]) )

        # close this window
        self.app.destroy()

    
def string_to_rational(coordinate):
    """
    convert string to rational variable for GPS
    """

    if '.' in coordinate:
        value1, value2 = coordinate.split('.')
        return pyexiv2.Rational(int(float(value1 + value2)), 10**len(value2))
    else:
        return pyexiv2.Rational(int(coordinate), 1)

def _get_exif_keypairs(plugin_image):
    """
    Will be used to retrieve and update the Exif metadata from the image.
    """

    if not plugin_image:
        return False
     
    mediadatatags_ = False
    if LesserVersion:  # prior to pyexiv2-0.2.0

        # get all keytags for this image for diplay only...
        mediadatatags_ = [keytag for keytag in plugin_image.exifKeys() ]

    else:  # pyexiv2-0.2.0 and above

        # get all keytags for this image for diplay only...
        mediadatatags_ = [keytag for keytag in chain(
            plugin_image.exif_keys, plugin_image.xmp_keys,
            plugin_image.iptc_keys) ]

    return mediadatatags_

def coords_to_rational(coordinates):
    """
    returns the GPS coordinates to Latitude/ Longitude
    """

    return [string_to_rational(coordinate) for coordinate in coordinates.split(" ")]

def convert_value(value):
    """
    will take a value from the coordinates and return its value
    """

    if isinstance(value, (Fraction, pyexiv2.Rational)):

        return str( ( Decimal(value.numerator) / Decimal(value.denominator) ) )

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
        for symbol in ["°", "#", "′", "'", '″', '"']:

            if symbol in latitude:
                latitude = latitude.replace(symbol, "")

            if symbol in longitude:
                longitude = longitude.replace(symbol, "")

    # remove leading and trailing whitespace...
    latitude  =  latitude.strip()
    longitude = longitude.strip()

    return latitude, longitude

def rational_to_dms(coords):
    """
    takes a rational set of coordinates and returns (degrees, minutes, seconds)

    [Fraction(40, 1), Fraction(0, 1), Fraction(1079, 20)]
    """

    degrees, minutes, seconds = [False]*3
    # coordinates look like:
    #     [Rational(38, 1), Rational(38, 1), Rational(150, 50)]
    # or [Fraction(38, 1), Fraction(38, 1), Fraction(318, 100)]   
    if isinstance(coords, list):
    
        if len(coords) == 3:
            return [convert_value(coordinate) for coordinate in coords]

    return degrees, minutes, seconds

def _format_datetime(exif_dt):
    """
    Convert a python datetime object into a string for display, using the
    standard Gramps date format.
    """

    date_part = gen.lib.Date()
    if isinstance(exif_dt, datetime):
        date_part.set_yr_mon_day(exif_dt.year, exif_dt.month, exif_dt.day)
        date_str = _dd.display(date_part)
        time_str = _('%(hr)02d:%(min)02d:%(sec)02d') % {'hr': exif_dt.hour,
                                                        'min': exif_dt.minute,
                                                        'sec': exif_dt.second}
    elif isinstance(exif_dt, str):
        exif_dt = _get_date_format(exif_dt)
        if exif_dt == False:
            return False

        date_part.set_yr_mon_day(exif_dt[0], exif_dt[1], exif_dt[2])
        date_str = _dd.display(date_part)
        time_str = _('%(hr)02d:%(min)02d:%(sec)02d') % {'hr' : exif_dt[3],
                                                        'min': exif_dt[4],
                                                        'sec': exif_dt[5]}
    return _('%(date)s %(time)s') % {'date': date_str, 'time': time_str}

def _get_date_format(datestr):
    """
    attempt to retrieve date format from date string
    """

    # attempt to determine the dateformat of the variable passed to it...
    tmpdate = False
    for dateformat in ["%Y-%m-%d %H:%M:%S", "%Y %m %d %H:%M:%S",
                       "%Y-%b-%d %H:%M:%S", "%Y %b %d %H:%M:%S",
                       "%Y-%B-%d %H:%M:%S", "%Y %B %d %H:%M:%S",
                       "%d-%m-%Y %H:%M:%S", "%d %m %Y %H:%M:%S",
                       "%d-%b-%Y %H:%M:%S", "%d %b %Y %H:%M:%S",
                       "%d-%B-%Y %H:%M:%S", "%d %B %Y %H:%M:%S",
                       "%m-%d-%Y %H:%M:%S", "%m %d %Y %H:%M:%S",
                       "%b-%d-%Y %H:%M:%S", "%b %d %Y %H:%M:%S",
                       "%B-%d-%Y %H:%M:%S", "%B %d %Y %H:%M:%S"]:

        # find date string format
        try:
            tmpdate = time.strptime(datestr, dateformat)
            break

        # datestring format  not found...
        except ValueError:
            pass

    return tmpdate

def _create_datetime(date_elements):
    """
    will create and retrun a str or datetime from (
        year, month, day, hour, minutes, and seconds) ...

    if the year is less than 1900, then it will return a string representation...
    """
    pyear, pmonth, day, hour, minutes, seconds = date_elements

    # do some error trapping...
    if pmonth > 12:
        pmonth = 12
    elif pmonth <= 0:
        pmonth = 1

    if hour >= 24:
        hour = 23
    elif hour < 0:
        hour = 0

    if minutes > 59:
        minutes = 59
    elif minutes < 0:
        minutes = 0
 
    if seconds > 59:
        seconds = 59
    elif seconds < 0:
        seconds = 0

    # get the number of days in year for all months
    numdays = [0] + [calendar.monthrange(year, month)[1] for year in [pyear] 
        for month in range(1, 13) ]

    if day > numdays[pmonth]:
        day = numdays[pmonth]
    elif day <= 0:
        day = 1

    if pyear < 1900:
        try:
            tmpdate = "%(yr)04d:%(mon)02d:%(dy)02d %(hr)02d:%(mins)02d:%(secs)02d" % {
                        'yr' : pyear, 'mon' : pmonth, 'dy' : day,
                        'hr' : hour, 'mins' : minutes, 'secs' : seconds }

        except ValueError:
            tmpdate = False

    else:
        try:
            tmpdate = datetime(pyear, pmonth, day, hour, minutes, seconds)

        except ValueError:
            tmpdate = False

    if tmpdate is False:
        tmpdate = ""

    return tmpdate

def _process_datetime(tmpdate, exif_type =True):
    """
    will attempt to parse the date/ time Exif metadata entry into its pieces...
        (year, month, day, hour, minutes, seconds)
    """

    if not tmpdate:
        return False

    datetype = type(tmpdate)

    # if variable is already in datetime.datetime() format, return it?
    if datetype == datetime:
        pyear, pmonth, day = tmpdate.year, tmpdate.month, tmpdate.day
        hour, minutes, seconds = tmpdate.hour, tmpdate.minute, tmpdate.second        

    elif any(datetype == value for value in [date, gen.lib.date.Date, list] ):
        hour, minutes, seconds = time.localtime()[3:6]

        # datetime.date format
        if isinstance(tmpdate, date):
            pyear, pmonth, day = tmpdate.year, tmpdate.month, tmpdate.day

        # gen.lib.date.Date format
        elif isinstance(tmpdate, gen.lib.date.Date):
            pyear, pmonth, day = tmpdate.get_year(), tmpdate.get_month(), tmpdate.get_day()

        # list format
        else:
            pyear, pmonth, day = tmpdate[0].year, tmpdate[0].month, tmpdate[0].day

    #  string format...
    elif datetype == str:

        datestr = _get_date_format(tmpdate)
        if datestr is not False:
            pyear, pmonth, day, hour, minutes, seconds = datestr[0:6]

        else:
            pyear, pmonth, day, hour, minutes, seconds = [False]*6

    if (not pyear and not pmonth):
        tmpdate = False

    else:

        # create datetime...
        tmpdate = _create_datetime([pyear, pmonth, day, hour, minutes, seconds])

    if tmpdate is not False:

        if isinstance(tmpdate, datetime):

            # for display only...
            # make datetime displayed as user has set in preferences...
            if exif_type:
                tmpdate = _format_datetime(tmpdate)

    return tmpdate

def _setup_widget_tooltips(exif_widgets):
    """
    setup tooltips for each entry field and button.
    """

    # add tooltips for the data entry fields...
    for widget, tooltip in _TOOLTIPS.items():
        exif_widgets[widget].set_tooltip_text(tooltip)

    # add tooltips for the buttons...
    for widget, tooltip in _BUTTONTIPS.items():
        exif_widgets[widget].set_tooltip_text(tooltip)
