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
import os, sys
from datetime import datetime, date
import calendar, time

# abilty to escape certain characters from output...
from xml.sax.saxutils import escape as _html_escape

from itertools import chain

from decimal import *
getcontext().prec = 4
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
from QuestionDialog import WarningDialog, QuestionDialog, OptionDialog

from gen.ggettext import gettext as _

from gen.plug import Gramplet
from DateHandler import displayer as _dd

import gen.lib
import Utils
from PlaceUtils import conv_lat_lon
from ListModel import ListModel, NOSORT

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

# to be able for people that have pyexiv2-0.1.3 to be able to use this addon also...
LesserVersion = False

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
    LesserVersion = True

# the library is either not installed or does not meet minimum required version for this addon....
if (software_version and (software_version < Min_VERSION)):
    msg = _("The minimum required version for pyexiv2 must be %s \n"
        "or greater.  Or you do not have the python library installed yet.  "
        "You may download it from here: %s\n\n  I recommend getting, %s") % (
         Min_VERSION_str, _DOWNLOAD_LINK, Pref_VERSION_str)
    WarningDialog(msg)
    raise Exception(msg)

# *******************************************************************
#         Determine if we have access to outside Programs
#
# The programs are ImageMagick, and jhead
# * ImageMagick -- Convert and Delete all Exif metadata...
# * jhead       -- re-initialize a jpeg, and other features...
# * del/ rm     -- delete old files from the convert command...
#********************************************************************
# Windows 32bit systems
system_platform = os.sys.platform
if system_platform == "win32":
    _MAGICK_FOUND = "convert.exe" if Utils.search_for("convert.exe") else False
    _JHEAD_FOUND = "jhead.exe" if Utils.search_for("jhead.exe") else False
    _DEL_FOUND = "del.exe" if Utils.search_for("del.exe") else False

elif system_platform == "linux2":
    _MAGICK_FOUND = "convert" if Utils.search_for("convert") else False
    _JHEAD_FOUND = "jhead" if Utils.search_for("jhead") else False
    _DEL_FOUND = "rm" if Utils.search_for("rm") else False

else:
    _MAGICK_FOUND = "convert" if Utils.search_for("convert") else False
    _JHEAD_FOUND = "jhead" if Utils.search_for("jhead") else False
    _DEL_FOUND = "del" if Utils.search_for("del") else False

# if external programs are not found, let the user know about the missing functionality?
if not _MAGICK_FOUND:
    print(_("ImageMagick's convert program was not found on this computer.\n"
        "You may download it from here: %s...") % (
            "http://www.imagemagick.org/script/index.php"))

if not _JHEAD_FOUND:
    print(_("Jhead program was not found on this computer.\n"
        "You may download it from: %s...") % (
            "http://www.sentex.net/~mwandel/jhead/"))

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
# available image types for exiv2 and pyexiv2
_vtypes = [".jpeg", ".jpg", ".jfif", ".exv", ".tiff", ".dng", ".nef", ".pef", ".pgf",
    ".png", ".psd", ".jp2"]

# define tooltips for all entries
_TOOLTIPS = {

    # Description...
    "Description"       : _("Provide a short descripion for this image."),

    # Artist 
    "Artist"            : _("Enter the Artist/ Author of this image.  The person's name or "
        "the company who is responsible for the creation of this image."),

    # Copyright
    "Copyright"         : _("Enter the copyright information for this image. \n"
        "Example: (C) 2010 Smith and Wesson"),

    # GPS Latitude...
    "Latitude"          : _(u"Enter the GPS Latitude Coordinates for your image,\n"
        u"Example: 43.722965, 43 43 22 N, 38° 38′ 03″ N, 38 38 3"),

    # GPS Longitude...
    "Longitude"         : _(u"Enter the GPS Longitude Coordinates for your image,\n"
        u"Example: 10.396378, 10 23 46 E, 105° 6′ 6″ W, -105 6 6") }.items()

# set up Exif keys for Image.exif_keys
_DATAMAP = {
    "Exif.Image.ImageDescription"  : "Description",
    "Exif.Image.DateTime"          : "Modified",
    "Exif.Image.Artist"            : "Artist",
    "Exif.Image.Copyright"         : "Copyright",
    "Exif.Photo.DateTimeOriginal"  : "Original",
    "Exif.Photo.DateTimeDigitized" : "Digitized",
    "Exif.GPSInfo.GPSLatitudeRef"  : "LatitudeRef",
    "Exif.GPSInfo.GPSLatitude"     : "Latitude",
    "Exif.GPSInfo.GPSLongitudeRef" : "LongitudeRef",
    "Exif.GPSInfo.GPSLongitude"    : "Longitude"}
_DATAMAP  = dict( (key, val) for key, val in _DATAMAP.items() )
_DATAMAP.update( (val, key) for key, val in _DATAMAP.items()  )

# Toolt tips for the buttons in the gramplet...
_BUTTONTIPS = {

    # Clear Edit Area button... 
    "Clear"             : _("Clears the Exif metadata from the Edit area."),

    # Calendar date select button...
    "Popup:Select"      : _("Allows you to select a date from a Popup window Calendar. \n"
        "Warning:  You will still need to edit the time..."),

    # Thumbnail Viewing Window button...
    "ThumbnailView"         : _("Will produce a Popup window showing a Thumbnail Viewing Area"),

    # Wiki Help button...
    "Help"              : _("Displays the Gramps Wiki Help page for 'Edit Image Exif Metadata' "
        "in your web browser."),

    # Advanced Display Window button...
    "Advanced"          : _("Will pop open a window with all of the Exif metadata Key/alue pairs."),

    # Save Exif Metadata button...
    "Save"              : _("Saves/ writes the Exif metadata to this image.\n"
        "WARNING: Exif metadata will be erased if you save a blank entry field...") }

# if ImageMagick is installed on this computer then, add button tooltips for Convert button...
if _MAGICK_FOUND:
    _BUTTONTIPS.update( {

        # Convert to .Jpeg button...
        "Convert"           : _("If your image is not a .jpg image, convert it to a .jpg image?") } )

# if ImageMagick's "convert" or jhead is installed, add this button tooltip...
if _MAGICK_FOUND or _JHEAD_FOUND:
    _BUTTONTIPS.update( {

        # Delete/ Erase/ Wipe Exif metadata button...
        "Delete"     : _("WARNING:  This will completely erase all Exif metadata "
            "from this image!  Are you sure that you want to do this?") } )

def _help_page(obj):
    """
    will bring up a Wiki help page.
    """

    GrampsDisplay.help(webpage = "Edit Image Exif Metadata")

_allmonths = list([_dd.short_months[i], _dd.long_months[i], i] for i in range(1, 13))

def _return_month(month):
    """
    returns either an integer of the month number or the abbreviated month name

    @param: rmonth -- can be one of:
        10, "10", "Oct", or "October"
    """

    try:
        month = int(month)

    except ValueError:
        for sm, lm, index in _allmonths:
            if month == sm or month == lm:
                month = int(index)
                break
            elif str(month) == index:
                    month = lm
                    break
    return month

# ------------------------------------------------------------------------
# Gramplet class
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

        vbox = self.build_gui()
        self.connect_signal("Media", self.update)

        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(vbox)
        vbox.show_all()

    def build_gui(self):
        """
        creates the editing area fields.
        """

        main_vbox = gtk.VBox(False, 0)

        # Displays the file name...
        medialabel = gtk.HBox(False)
        label = gtk.Label()
        label.set_alignment(0.0, 0.0)
        label.set_line_wrap(True)
        self.exif_widgets["Media:Label"] = label
        medialabel.pack_start(self.exif_widgets["Media:Label"], expand =False)
        main_vbox.pack_start(medialabel, expand =False)

        # Displays mime type information...
        mimetype = gtk.HBox(False)
        label = gtk.Label()
        label.set_alignment(0.0, 0.0)
        label.set_line_wrap(True)
        self.exif_widgets["Mime:Type"] = label
        mimetype.pack_start(self.exif_widgets["Mime:Type"], expand =False)
        main_vbox.pack_start(mimetype, expand =False)

        # Displays all plugin messages...
        messagearea = gtk.HBox(False)
        label = gtk.Label()
        label.set_alignment(0.5, 0.0)
        label.set_line_wrap(True)
        self.exif_widgets["Message:Area"] = label
        messagearea.pack_start(self.exif_widgets["Message:Area"], expand =False)
        main_vbox.pack_start(messagearea, expand =False)

        # Clear, Thumbnail View, Convert horizontal box
        ctc_box = gtk.HButtonBox()
        ctc_box.set_layout(gtk.BUTTONBOX_START)

        # Clear button...
        ctc_box.add( self.__create_button(
            "Clear", False, [self.clear_metadata], gtk.STOCK_CLEAR) )

        # ThumbnailView View button...
        ctc_box.add(self.__create_button(
            "ThumbnailView", _("Thumbnail(s)"), [self.thumbnail_view] ) )

        # is ImageMagick installed?
        if _MAGICK_FOUND:
            # Convert button...
            ctc_box.add(self.__create_button(
                "Convert", False, [self.__convert_dialog], gtk.STOCK_CONVERT) )
        main_vbox.pack_start(ctc_box, expand =False, fill =False, padding =10)

        # create the data fields and button:
        # ***Description, Artist, Copyright, and Calendar date... 
        for items in [

            # Image Description
            ("Description",     _("Description"),    None, False, [],  True,  0),

            # Artist field
            ("Artist",          _("Artist"),         None, False, [],  True,  0),

            # copyright field
            ("Copyright",       _("Copyright"),      None, False, [],  True,  0),

            # calendar date clickable entry...
            ("Popup",             "",                None, True,
            [("Select",         _("Select Date"),    "button", self.select_date)],
                                                                       True,  0) ]:

            pos, text, choices, readonly, callback, dirty, default = items
            row = self.make_row(pos, text, choices, readonly, callback, dirty, default)
            main_vbox.pack_start(row, False)

        # get current date and time from system...
        now = time.localtime()

        # iso format: Year, Month, Day spinners...
        date_frame = gtk.Frame(_("Creation Date"))
        main_vbox.pack_start(date_frame, expand =True, fill =True, padding =0)

        new_vbox = gtk.VBox(False, 0)
        new_vbox.set_border_width(5)
        date_frame.add(new_vbox)

        new_hbox = gtk.HBox(False, 0)
        new_vbox.pack_start(new_hbox, expand =True, fill =True, padding =5)

        vbox2 = gtk.VBox(False, 0)
        new_hbox.pack_start(vbox2, expand =True, fill =True, padding =5)

        label = gtk.Label(_("Year :"))
        label.set_alignment(0, 0.5)
        vbox2.pack_start(label, expand =False, fill =True, padding =0)
  
        adj = gtk.Adjustment(value=now[0], lower=1826, upper=2100, step_incr=1.0, page_incr=100)
        year_spinner = gtk.SpinButton(adj, climb_rate =1.0, digits =0)
        year_spinner.set_wrap(False)
        year_spinner.set_size_request(55, -1)
        year_spinner.set_numeric(True)
        vbox2.pack_start(year_spinner, expand =False, fill =True, padding =0)

        vbox2 = gtk.VBox(False, 0)
        new_hbox.pack_start(vbox2, expand =True, fill =True, padding =5)
  
        label = gtk.Label(_("Month :"))
        label.set_alignment(0, 0.5)
        vbox2.pack_start(label, expand =False, fill =True, padding =0)

        adj = gtk.Adjustment(value=now[1], lower=1.0, upper=12.0, step_incr=1.0, page_incr=5.0, page_size=0.0)
        month_spinner = gtk.SpinButton(adj, climb_rate =0.0, digits =0)
        month_spinner.set_wrap(True)
        month_spinner.set_numeric(True)
        vbox2.pack_start(month_spinner, expand =False, fill =True, padding =0)

        vbox2 = gtk.VBox(False, 0)
        new_hbox.pack_start(vbox2, expand =True, fill =True, padding =5)

        label = gtk.Label(_("Day :"))
        label.set_alignment(0, 0.5)
        vbox2.pack_start(label, expand =False, fill =True, padding =0)
  
        adj = gtk.Adjustment(value=now[2], lower=1.0, upper=31.0, step_incr=1.0, page_incr=5.0, page_size=0.0)
        day_spinner = gtk.SpinButton(adj, climb_rate =0.0, digits =0)
        day_spinner.set_wrap(True)
        day_spinner.set_numeric(True)
        vbox2.pack_start(day_spinner, expand =False, fill =True, padding =0)

        # define the exif_widgets for these spinners
        self.exif_widgets["Year"] = year_spinner
        self.exif_widgets["Month"] = month_spinner
        self.exif_widgets["Day"] = day_spinner

        # Hour, Minutes, Seconds spinners...
        time_frame = gtk.Frame(_("Creation Time"))
        main_vbox.pack_start(time_frame, expand =True, fill =True, padding =0)

        new_vbox = gtk.VBox(False, 0)
        new_vbox.set_border_width(5)
        time_frame.add(new_vbox)

        new_hbox = gtk.HBox(False, 0)
        new_vbox.pack_start(new_hbox, expand =True, fill =True, padding =5)

        vbox2 = gtk.VBox(False, 0)
        new_hbox.pack_start(vbox2, expand =True, fill =True, padding =5)

        label = gtk.Label(_("Hour :"))
        label.set_alignment(0, 0.5)
        vbox2.pack_start(label, expand =False, fill =True, padding =0)
  
        adj = gtk.Adjustment(value=now[3], lower=0, upper=23, step_incr=1, page_incr=5, page_size=0.0)
        hour_spinner = gtk.SpinButton(adj, climb_rate =0.0, digits =0)
        hour_spinner.set_wrap(False)
        hour_spinner.set_size_request(55, -1)
        hour_spinner.set_numeric(True)
        vbox2.pack_start(hour_spinner, expand =False, fill =True, padding =0)

        vbox2 = gtk.VBox(False, 0)
        new_hbox.pack_start(vbox2, expand =True, fill =True, padding =5)
  
        label = gtk.Label(_("Minutes :"))
        label.set_alignment(0, 0.5)
        vbox2.pack_start(label, expand =False, fill =True, padding =0)

        adj = gtk.Adjustment(value=now[4], lower=0, upper=59, step_incr=1, page_incr=5.0, page_size=0.0)
        minutes_spinner = gtk.SpinButton(adj, climb_rate =0.0, digits =0)
        minutes_spinner.set_wrap(True)
        minutes_spinner.set_numeric(True)
        vbox2.pack_start(minutes_spinner, expand =False, fill =True, padding =0)

        vbox2 = gtk.VBox(False, 0)
        new_hbox.pack_start(vbox2, expand =True, fill =True, padding =5)

        label = gtk.Label(_("Seconds :"))
        label.set_alignment(0, 0.5)
        vbox2.pack_start(label, expand =False, fill =True, padding =0)
  
        adj = gtk.Adjustment(value=now[5], lower=0, upper=59, step_incr=1.0, page_incr=5.0, page_size=0.0)
        seconds_spinner = gtk.SpinButton(adj, climb_rate =0.0, digits =0)
        seconds_spinner.set_wrap(True)
        seconds_spinner.set_numeric(True)
        vbox2.pack_start(seconds_spinner, expand =False, fill =True, padding =0)

        # define the exif_widgets for these spinners
        self.exif_widgets["Hour"] = hour_spinner
        self.exif_widgets["Minutes"] = minutes_spinner
        self.exif_widgets["Seconds"] = seconds_spinner

        # GPS Latitude/ Longitude Coordinates...
        for items in [
  
            # GPS Latitude Reference and Latitude...
            ("Latitude",        _("Latitude"),       None, False, [],  True,  0),

            # GPS Longitude Reference and Longitude...
            ("Longitude",       _("Longitude"),      None, False, [],  True,  0) ]:

            pos, text, choices, readonly, callback, dirty, default = items
            row = self.make_row(pos, text, choices, readonly, callback, dirty, default)
            main_vbox.pack_start(row, False)

        # Help, Save, Delete horizontal box
        hasd_box = gtk.HButtonBox()
        hasd_box.set_layout(gtk.BUTTONBOX_START)
        main_vbox.pack_start(hasd_box, expand =False, fill =False, padding =10)

        # Help button...
        hasd_box.add( self.__create_button(
            "Help", False, [_help_page], gtk.STOCK_HELP, True) )

        # Save button...
        hasd_box.add( self.__create_button(
            "Save", False, [self.__save_dialog], gtk.STOCK_SAVE) )

        # Advanced View Area button...
        hasd_box.add( self.__create_button(
            "Advanced", _("Advanced"), [self.advanced_view] ) )

        if _MAGICK_FOUND:
            # Delete All Metadata button...
            hasd_box.add(self.__create_button(
                "Delete", False, [self.__wipe_dialog], gtk.STOCK_DELETE ) )

        return main_vbox

    def __create_button(self, pos, text, callback =[], icon =False, sensitive =False):
        """
        creates and returns a button for display
        """

        if (icon and not text):
            button = gtk.Button(stock=icon)
        else:
            button = gtk.Button(text)

        if callback is not []:
            for _call in callback:
                button.connect("clicked", _call)

        if not sensitive:
            button.set_sensitive(False)
        self.exif_widgets[pos] = button

        return button

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
        MediaDataTags = _get_exif_keypairs(self.plugin_image)
        if MediaDataTags:
            return True

        return False

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

    def activate_save(self, obj):
        """
        will handle the toggle action of the Save button.

        If there is no Exif metadata, then the data fields are connected to the 
        'changed' signal to be able to activate the Save button once data has been entered
        into the data fields...
        """

        if not self.exif_widgets["Save"].get_sensitive():
            self.activate_buttons(["Save"])

            # set Message Area to Entering Data...
            self.exif_widgets["Message:Area"].set_text(_("Entering data..."))

    def main(self): # return false finishes
        """
        get the active media, mime type, and reads the image metadata
        """
        db = self.dbstate.db

        # clear Edit Area and Labels...
        self.clear_metadata(self.orig_image)

        # De-activate the buttons except for Help...
        self.deactivate_buttons(["Clear", "ThumbnailView", "Save", "Advanced"])

        if _MAGICK_FOUND:
            self.deactivate_buttons(["Convert"])

        if (_MAGICK_FOUND or _HEAD_FOUND): 
            self.deactivate_buttons(["Delete"])

        # set Message Area to Select...
        self.exif_widgets["Message:Area"].set_text(_("Select an image to begin..."))

        active_handle = self.get_active("Media")
        if not active_handle:
            self.set_has_data(False)
            return

        self.orig_image = db.get_object_from_handle(active_handle)
        self.image_path = Utils.media_path_full(db, self.orig_image.get_path() )
        if (not self.orig_image or not os.path.isfile(self.image_path)):
            self.exif_widgets["Message:Area"].set_text(_("Image is either missing or deleted,\n"
                "Please choose a different image..."))
            return

        # check image read privileges...
        _readable = os.access(self.image_path, os.R_OK)
        if not _readable:
            self.exif_widgets["Message:Area"].set_text(_("Image is NOT readable,\n"
                "Please choose a different image..."))
            return

        # check image write privileges...
        _writable = os.access(self.image_path, os.W_OK)
        if not _writable:
            self.exif_widgets["Message:Area"].set_text(_("Image is NOT writable,\n"
                "You will NOT be able to save Exif metadata...."))

        # display file description/ title...
        self.exif_widgets["Media:Label"].set_text(_html_escape(
            self.orig_image.get_description() ) )

        # Mime type information...
        mime_type = self.orig_image.get_mime_type()
        self.exif_widgets["Mime:Type"].set_text(mime_type)

        # disable all data fields and buttons if NOT an exiv2 image type?
        basename, self.extension = os.path.splitext(self.image_path)
        _setup_datafields_buttons(self.extension, self.exif_widgets)

        # determine if it is a mime image object?
        if mime_type:
            if mime_type.startswith("image"):

                # Checks to make sure that ImageMagick is installed on this computer and
                # the image is NOT a (".jpeg", ".jfif", or ".jpg") image...
                # if not, then activate the Convert button?
                if (_MAGICK_FOUND and self.extension not in [".jpeg", ".jpg", ".jfif"] ):
                    self.activate_buttons(["Convert"])

                # setup widget tooltips for all fields and buttons...
                _setup_widget_tips(self.exif_widgets)

                # creates, and reads the plugin image instance...
                self.plugin_image = self.setup_image(self.image_path)

                # Check for ThumbnailViews...
                previews = self.plugin_image.previews
                if (len(previews) > 0):
                    self.activate_buttons(["ThumbnailView"])

                # displays the imge Exif metadata into selected data fields...
                self.EditArea(self.orig_image)

            else:
                self.exif_widgets["Message:Area"].set_text(_("Please choose a different image..."))
                return
        else:
            self.exif_widgets["Message:Area"].set_text(_("Please choose a different image..."))
            return

    def __convert_dialog(self, obj):
        """
        Handles the Convert question Dialog...
        """

        # if ImageMagick and delete has been found on this computer?
        if (_MAGICK_FOUND and _DEL_FOUND):
            OptionDialog(_("Edit Image Exif Metadata"), _("WARNING: You are about to convert this "
                "image into a .jpeg image.  Are you sure that you want to do this?"), 
                _("Convert and Delete original"), self.convertdelete, 
                _("Convert"), self.convert2Jpeg)

        # is ImageMagick is installed?
        elif _MAGICK_FOUND:

            QuestionDialog(_("Edit Image Exif Metadata"), _("Convert this image to a .jpeg image?"),
                _("Convert"), self.convert2Jpeg)

    def __save_dialog(self, obj):
        """
        Handles the Save question Dialog...
        """

        QuestionDialog(_("Edit Image Exif Metadata"), _("Save Exif metadata to this image?"),
            _("Save"), self.save_metadata)

    def __wipe_dialog(self, obj):
        """
        Handles the Delete Dialog...
        """

        QuestionDialog(_("Edit Image Exif Metadata"), _("WARNING!  You are about to completely "
            "delete the Exif metadata from this image?"), _("Delete"),
                self.strip_metadata)

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

    def make_row(self, pos, text, choices=None, readonly=False, callback_list=[],
                 mark_dirty=False, default=0):

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

    def _mark_dirty(self, obj):
        pass

    def _get_value(self, KeyTag):
        """
        gets the value from the Exif Key, and returns it...

        @param: KeyTag -- image metadata key
        """

        KeyValue = ""
        if LesserVersion:
            KeyValue = self.plugin_image[KeyTag]
        else:
            try:
                KeyValue = self.plugin_image[KeyTag].value

            except (KeyError, ValueError, AttributeError):
                pass

        return KeyValue

    def clear_metadata(self, obj, cleartype = "All"):
        """
        clears all data fields to nothing

        @param: cleartype -- 
            "Date" = clears only Date entry fields
            "All" = clears all data fields
        """

        # clear all data fields
        if cleartype == "All":
            for widgetsName in ["Description", "Artist", "Copyright",
                "Latitude", "Longitude", "Media:Label", "Mime:Type", "Message:Area"]:  
                self.exif_widgets[widgetsName].set_text("")

        # clear only the date/ time field
        else:
             self.exif_widgets["Message:Area"].set_text("") 

    def EditArea(self, obj):
        """
        displays the image Exif metadata in the Edit Area...
        """

        # Retrieves all metadata key pairs from this image...
        MediaDataTags = _get_exif_keypairs(self.plugin_image)

        # activate Clear button...
        self.activate_buttons(["Clear"])

        # if no Exif metadata, disable the has_data() functionality?
        if MediaDataTags:
            self.set_has_data(True)

            # Activate Delete button if ImageMagick or jhead is found?...
            if (_MAGICK_FOUND or _JHEAD_FOUND):
                self.activate_buttons(["Delete"])

            imageKeyTags = [KeyTag for KeyTag in MediaDataTags if KeyTag in _DATAMAP]

            # activate Advanced and Save buttons...
            self.activate_buttons(["Advanced", "Save"])

            # set Message Area to Copying...
            self.exif_widgets["Message:Area"].set_text(_("Copying Exif metadata to the Edit Area..."))

            for KeyTag in imageKeyTags:

                # name for matching to exif_widgets 
                widgetsName = _DATAMAP[KeyTag]

                tagValue = self._get_value(KeyTag)
                if tagValue:

                    if widgetsName in ["Description", "Artist", "Copyright"]:
                        self.exif_widgets[widgetsName].set_text(tagValue)

                    # Last Changed/ Modified...
                    elif widgetsName == "Modified":
                        use_date = self._get_value(_DATAMAP["Modified"])
                        use_date = _process_datetime(use_date) if use_date else False
                        if use_date:
                            self.exif_widgets["Message:Area"].set_text(_("Last Changed: %s") % use_date)

                    # Original Creation Date/ Time...
                    elif widgetsName == "Original":
                        use_date = ( self._get_value(_DATAMAP["Original"]) or 
                                     self._get_value(_DATAMAP["Digitized"]) )
                        if use_date:
                            if isinstance(use_date, str):
                                use_date = _get_date_format(use_date)
                                if use_date:
                                    year, month, day, hour, mins, secs = use_date[0:6]
                            elif isinstance(use_date, datetime):
                                year, month, day = use_date.year, use_date.month, use_date.day
                                hour, mins, secs = use_date.hour, use_date.minute, use_date.second
                            else:
                                year = False
                            if year:

                                # split the date/ time into its six pieces...
                                for widget, value in {   
                                    "Year"    : year,
                                    "Month"   : month,
                                    "Day"     : day,
                                    "Hour"    : hour,
                                    "Minutes" : mins,
                                    "Seconds" : secs}.items():

                                    # set the date/ time spin buttons...
                                    self.exif_widgets[widget].set_value(value)
                     
                    # LatitudeRef, Latitude, LongitudeRef, Longitude...
                    elif widgetsName == "Latitude":

                        latitude  =  self._get_value(KeyTag)
                        longitude = self._get_value(_DATAMAP["Longitude"])

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
                                self.exif_widgets["Latitude"].set_text(
                                    """%s° %s′ %s″ %s""" % (latdeg, latmin, latsec, LatRef) )

                                # set display for Longitude GPS Coordinates
                                self.exif_widgets["Longitude"].set_text(
                                    """%s° %s′ %s″ %s""" % (longdeg, longmin, longsec, LongRef) )

        else:

            # set Message Area to None...
            self.exif_widgets["Message:Area"].set_text(_("There is NO Exif metadata for this image yet..."))

            for widget, tooltip in _TOOLTIPS:
                if widget is not "Modified":
                    self.exif_widgets[widget].connect("changed", self.activate_save)

    def convertdelete(self):
        """
        will convert2Jpeg and delete original non-jpeg image.
        """

        self.convert2Jpeg()

        if system_platform == "linux2":
            delete = subprocess.check_call( [_DEL_FOUND, "-rf", self.image_path] )
        else:
            delete = subprocess.check_call( [_DEL_FOUND, "-y", self.image_path] )
        delete_result = str(delete)

        if delete_result:
            self.exif_widgets["Message:Area"].set_text(_("Image has been converted to a .jpg image,\n"
                "and original image has been deleted!"))

    def convert2Jpeg(self):
        """
        Will attempt to convert an image to jpeg if it is not?
        """

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

    def _set_value(self, KeyTag, KeyValue):
        """
        sets the value for the metadata KeyTags
        """

        if LesserVersion:
            self.plugin_image[KeyTag] = KeyValue

        else:
            if "Exif" in KeyTag:
                try: # tag is being modified...
                    self.plugin_image[KeyTag].value = KeyValue

                except KeyError:  # tag is being created...
                    self.plugin_image[KeyTag] = pyexiv2.ExifTag(KeyTag, KeyValue)

                except (ValueError, AttributeError):  # there is an error
                                                      # with either KeyTag or KeyValue
                    pass

            elif "Xmp" in KeyTag:
                try:
                    self.plugin_image[KeyTag].value = KeyValue

                except KeyError:
                    self.plugin_image[KeyTag] = pyexiv2.XmpTag(KeyTag, KeyValue)

                except (ValueError, AttributeError):
                    pass

            else:
                try:
                    self.plugin_image[KeyTag].value = KeyValue

                except KeyError:
                    self.plugin_image[KeyTag] = pyexiv2.IptcTag(KeyTag, KeyValue)

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

# -------------------------------------------------------------------
#          GPS Coordinates functions
# -------------------------------------------------------------------
    def addsymbols2gps(self, latitude =False, longitude =False):
        """
        converts a degrees, minutes, seconds representation of Latitude/ Longitude
        without their symbols to having them...

        @param: latitude -- Latitude GPS Coordinates
        @param: longitude -- Longitude GPS Coordinates
        """
        LatitudeRef, LongitudeRef = "N", "E"

        # check to see if Latitude/ Longitude exits?
        if (latitude and longitude):

            if (latitude.count(".") == 1 and longitude.count(".") == 1):
                self.convert2dms(self.plugin_image)

                # get Latitude/ Longitude from data fields
                # after the conversion
                latitude  =  self.exif_widgets["Latitude"].get_text()
                longitude = self.exif_widgets["Longitude"].get_text()

            # add DMS symbols if necessary?
            # the conversion to decimal format, require the DMS symbols
            elif ( (latitude.count("°") == 0 and longitude.count("°") == 0) and
                (latitude.count("′") == 0 and longitude.count("′") == 0) and
                (latitude.count('″') == 0 and longitude.count('″') == 0) ):

                # is there a direction element here?
                if (latitude.count("N") == 1 or latitude.count("S") == 1):
                    latdeg, latmin, latsec, LatitudeRef = latitude.split(" ", 3)
                else:
                    atitudeRef = "N"
                    latdeg, latmin, latsec = latitude.split(" ", 2)
                    if latdeg[0] == "-":
                        latdeg = latdeg.replace("-", "")
                        LatitudeRef = "S"

                # is there a direction element here?
                if (longitude.count("E") == 1 or longitude.count("W") == 1):
                    longdeg, longmin, longsec, LongitudeRef = longitude.split(" ", 3)
                else:
                    ongitudeRef = "E"
                    longdeg, longmin, longsec = longitude.split(" ", 2)
                    if longdeg[0] == "-":
                        longdeg = longdeg.replace("-", "")
                        LongitudeRef = "W"

                latitude  = """%s° %s′ %s″ %s""" % (latdeg, latmin, latsec, LatitudeRef)
                longitude = """%s° %s′ %s″ %s""" % (longdeg, longmin, longsec, LongitudeRef)

        return latitude, longitude

    def convert2decimal(self, obj):
        """
        will convert a decimal GPS Coordinates into decimal format.

        @param: latitude  -- GPS Latitude Coordinates from data field...
        @param: longitude -- GPS Longitude Coordinates from data field...
        """

        # get Latitude/ Longitude from the data fields
        latitude  =  self.exif_widgets["Latitude"].get_text()
        longitude = self.exif_widgets["Longitude"].get_text()

        # if latitude and longitude exist?
        if (latitude and longitude):

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

    def convert2dms(self, obj):
        """
        will convert a decimal GPS Coordinates into degrees, minutes, seconds
        for display only
        """

        # get Latitude/ Longitude from the data fields
        latitude = self.exif_widgets["Latitude"].get_text()
        longitude = self.exif_widgets["Longitude"].get_text()

        # if Latitude/ Longitude exists?
        if (latitude and longitude):

            # if coordinates are in decimal format?
            if (latitude.count(".") == 1 and longitude.count(".") == 1):

                # convert latitude and longitude to a DMS with separator of ":"
                latitude, longitude = conv_lat_lon(latitude, longitude, "DEG-:")
 
                # remove negative symbol if there is one?
                LatitudeRef = "N"
                if latitude[0] == "-":
                    latitude = latitude.replace("-", "")
                    LatitudeRef = "S"
                latdeg, latmin, latsec = latitude.split(":", 2)

               # remove negative symbol if there is one?
                LongitudeRef = "E"
                if longitude[0] == "-":
                    longitude = longitude.replace("-", "")
                    LongitudeRef = "W"
                longdeg, longmin, longsec = longitude.split(":", 2)

                self.exif_widgets["Latitude"].set_text(
                    """%s° %s′ %s″ %s""" % (latdeg, latmin, latsec, LatitudeRef) )

                self.exif_widgets["Longitude"].set_text(
                    """%s° %s′ %s″ %s""" % (longdeg, longmin, longsec, LongitudeRef) )

    def advanced_view(self, obj):
        """
        Pups up a window with all of the Exif metadata available...
        """

        tip = _("Click the close button when you are finished.")

        advarea = gtk.Window(gtk.WINDOW_TOPLEVEL)
        advarea.tooltip = tip
        advarea.set_title(_("Complete Exif, Xmp, and Iptc metadata"))
        advarea.set_default_size(300, 450)
        advarea.set_border_width(10)
        advarea.connect('destroy', lambda advarea: advarea.destroy() )

        vbox = self.build_advanced()
        vbox.show()
        advarea.add(vbox)
        advarea.show()

        # Update the image Exif metadata...
        MediaDataTags = _get_exif_keypairs(self.plugin_image)

        if LesserVersion:  # prior to pyexiv2-0.2.0
            for KeyTag in MediaDataTags:
                label = self.plugin_image.tagDetails(KeyTag)[0]
                if KeyTag in ("Exif.Image.DateTime",
                           "Exif.Photo.DateTimeOriginal",
                           "Exif.Photo.DateTimeDigitized"):
                    human_value = _format_datetime(self.plugin_image[KeyTag])
                else:
                    human_value = self.plugin_image.interpretedExifValue(KeyTag)
                self.model.add((label, human_value))

        else: # pyexiv2-0.2.0 and above
            for KeyTag in MediaDataTags:
                tag = self.plugin_image[KeyTag]
                if KeyTag in ("Exif.Image.DateTime",
                           "Exif.Photo.DateTimeOriginal",
                           "Exif.Photo.DateTimeDigitized"):
                    label = tag.label
                    human_value = _format_datetime(tag.value)
                elif ("Xmp" in KeyTag or "Iptc" in KeyTag):
                    label = KeyTag
                    human_value = tag.value
                else:
                    label = tag.label
                    human_value = tag.human_value
                self.model.add((label, human_value))

    def build_advanced(self):
        """
        Build the GUI interface.
        """
        top = gtk.TreeView()
        titles = [(_('Key'), 1, 250),
                  (_('Value'), 2, 350)]
        self.model = ListModel(top, titles)
        return top
        
    def save_metadata(self):
        """
        gets the information from the plugin data fields
        and sets the KeyTag = keyvalue image metadata
        """

        # determine if there has been something entered in the data fields?
        datatags = (
            len(self.exif_widgets["Description"].get_text() ) + 
            len(self.exif_widgets["Artist"].get_text() ) + 
            len(self.exif_widgets["Copyright"].get_text() ) +
            len(self.exif_widgets["Latitude"].get_text() ) + 
            len(self.exif_widgets["Longitude"].get_text() ) )

        # Description data field...
        description = self.exif_widgets["Description"].get_text() or ""
        self._set_value(_DATAMAP["Description"],  description)

        # Modify Date/ Time... not a data field, but saved anyway...
        modified = datetime.today()
        self._set_value(_DATAMAP["Modified"], modified)

        # display modified Date/ Time...
        self.exif_widgets["Message:Area"].set_text(_("Last Changed: %s") % _format_datetime(modified) )
 
        # Artist/ Author data field...
        artist = self.exif_widgets["Artist"].get_text()
        self._set_value(_DATAMAP["Artist"], artist)

        # Copyright data field...
        copyright = self.exif_widgets["Copyright"].get_text()
        self._set_value(_DATAMAP["Copyright"], copyright)

        # Original Date/ Time
        year = self.exif_widgets["Year"].get_value_as_int()
        month = self.exif_widgets["Month"].get_value_as_int()
        day = self.exif_widgets["Day"].get_value_as_int()
        hour = self.exif_widgets["Hour"].get_value_as_int()
        minutes = self.exif_widgets["Minutes"].get_value_as_int()
        seconds = self.exif_widgets["Seconds"].get_value_as_int()

        use_date = False
        if year < 1900:
            use_date = "%04d-%s-%02d %02d:%02d:%02d" % (year, _dd.long_months[month], day,
                                                        hour, minutes, seconds)
        else:
            use_date = datetime(year, month, day, hour, minutes, seconds)
        if use_date:
            self._set_value(_DATAMAP["Original"], use_date)

        # Latitude/ Longitude data fields
        latitude  =  self.exif_widgets["Latitude"].get_text()
        longitude = self.exif_widgets["Longitude"].get_text()

        # check to see if Latitude/ Longitude exists?
        if (latitude and longitude):

            # complete some error checking to prevent crashes...
            # if "?" character exist, remove it?
            if "?" in latitude:
                latitude = latitude.replace("?", "")
            if "?" in longitude:
                longitude = longitude.replace("?", "")

            # if "," character exists, remove it?
            if "," in latitude: 
                latitude = latitude.replace(",", "")
            if "," in longitude:
                longitude = longitude.replace(",", "") 

            # if it is in decimal format, convert it to DMS?
            # if not, then do nothing?
            self.convert2dms(self.plugin_image)

            # get Latitude/ Longitude from the data fields
            latitude  =  self.exif_widgets["Latitude"].get_text()
            longitude = self.exif_widgets["Longitude"].get_text()

            # will add (degrees, minutes, seconds) symbols if needed?
            # if not, do nothing...
            latitude, longitude = self.addsymbols2gps(latitude, longitude)

            # set up display
            self.exif_widgets["Latitude"].set_text(latitude)
            self.exif_widgets["Longitude"].set_text(longitude)

            LatitudeRef = " N"
            if "S" in latitude:
                LatitudeRef = " S"
            latitude = latitude.replace(LatitudeRef, "")
            LatitudeRef = LatitudeRef.replace(" ", "")

            LongitudeRef = " E"
            if "W" in longitude:
                LongitudeRef = " W"
            longitude = longitude.replace(LongitudeRef, "")
            LongitudeRef = LongitudeRef.replace(" ", "")

            # remove symbols for saving Latitude/ Longitude GPS Coordinates
            latitude, longitude = _removesymbols4saving(latitude, longitude) 

            # convert (degrees, minutes, seconds) to Rational for saving
            self._set_value(_DATAMAP["LatitudeRef"], LatitudeRef)
            self._set_value(_DATAMAP["Latitude"], coords_to_rational(latitude))

            # convert (degrees, minutes, seconds) to Rational for saving
            self._set_value(_DATAMAP["LongitudeRef"], LongitudeRef)
            self._set_value(_DATAMAP["Longitude"], coords_to_rational(longitude))

        if datatags:
            # set Message Area to Saved...
            self.exif_widgets["Message:Area"].set_text(_("Saving Exif metadata to this image..."))
        else:
            # set Message Area to Cleared...
            self.exif_widgets["Message:Area"].set_text(_("Image Exif metadata has been cleared "
                "from this image..."))

        # writes all Exif Metadata to image even if the fields are all empty...
        self.write_metadata(self.plugin_image)

    def strip_metadata(self):
        """
        Will completely and irrevocably erase all Exif metadata from this image.
        """

        # update the image Exif metadata...
        MediaDataTags = _get_exif_keypairs(self.plugin_image)
        if not MediaDataTags:
            return

        if _MAGICK_FOUND:
            erase = subprocess.check_call( ["convert", self.image_path, "-strip", self.image_path] )
            erase_results = str(erase)

        elif (_JHEAD_FOUND and self.extension in [".jpeg", ".jfif", ".jpg"]):
            erase = subprocess.check_call( ["jhead", "-purejpeg", self.image_path] )

        else:
            if MediaDataTags: 
                for KeyTag in MediaDataTags:
                    del self.plugin_image[KeyTag]
                erase_results = True

                # write wiped metadata to image...
                self.write_metadata(self.plugin_image)

        if erase_results:

            # set Message Area for deleting...
            self.exif_widgets["Message:Area"].set_text(_("Deleting all Exif metadata..."))

            # Clear the Edit Areas
            self.clear_metadata(self.plugin_image)

            # set Message Area to Delete...
            self.exif_widgets["Message:Area"].set_text(_("All Exif metadata has been "
                    "deleted from this image..."))

            self.update()

    def select_date(self, obj):
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

    def double_click(self, obj):
        """
        receives double-clicked and returns the selected date
        widget
        """
        now = time.localtime()

        year, month, day = self.exif_widgets["Calendar"].get_date()

        # close this window
        self.app.destroy()

    def thumbnail_view(self, obj):
        """
        will allow a display area for a thumbnail pop-up window.
        """
 
        tip = _("Click Close to close this ThumbnailView Viewing Area.")

        tbarea = gtk.Window(gtk.WINDOW_TOPLEVEL)
        tbarea.tooltip = tip
        tbarea.set_title(_("ThumbnailView Viewing Area"))
        tbarea.set_default_size(250, 200)
        tbarea.set_border_width(10)

        tbarea.connect('destroy', lambda tbarea: tbarea.destroy() )

        # extract the thumbnail data
        previews = self.plugin_image.previews
        if not previews:
            print(_("This image doesn't contain any ThumbnailViews..."))
            tbarea.destroy()
        else:

            # Get the largest preview available...
            preview = previews[-1]

            # Create a pixbuf loader to read the thumbnail data...
            pbloader = gtk.gdk.PixbufLoader()
            pbloader.write(preview.data)

            # Get the resulting pixbuf and build an image to be displayed...
            pixbuf = pbloader.get_pixbuf()
            pbloader.close()
            imgwidget = gtk.Image()
            imgwidget.set_from_pixbuf(pixbuf)

            # Show the application's main window...
            tbarea.add(imgwidget)
            imgwidget.show()
            tbarea.show()

def _setup_datafields_buttons(extension, exif_widgets):
    """
    disable all data fields and buttons...
        * if file extension is NOT an exiv2 image type?
    """

    goodextension = True if extension in _vtypes else False

    for widget, tooltip in _TOOLTIPS:
        if widget is not "Modified":
            exif_widgets[widget].set_visibility(goodextension)
            exif_widgets[widget].set_editable(goodextension)

    for widget, tooltip in _BUTTONTIPS.items():
        if (widget not in ["Help", "Clear"] and not goodextension):
            exif_widgets[widget].set_sensitive(False)

def _setup_widget_tips(exif_widgets):
    """
    set up widget tooltips...
        * data fields
        * buttons
    """

    # add tooltips for the data entry fields...
    for widget, tooltip in _TOOLTIPS:
        exif_widgets[widget].set_tooltip_text(tooltip)

    # add tooltips for the buttons...
    for widget, tooltip in _BUTTONTIPS.items():
        exif_widgets[widget].set_tooltip_text(tooltip)

def _get_exif_keypairs(plugin_image):
    """
    Will be used to retrieve and update the Exif metadata from the image.
    """
    MediaDataTags = False

    if plugin_image:
        if LesserVersion:  # prior to pyexiv2-0.2.0
            # get all KeyTags for this image for diplay only...
            MediaDataTags = [KeyTag for KeyTag in chain(
                                plugin_image.exifKeys(), plugin_image.xmpKeys(),
                                plugin_image.iptcKeys() ) ]

        else:  # pyexiv2-0.2.0 and above
            # get all KeyTags for this image for diplay only...
            MediaDataTags = [KeyTag for KeyTag in chain(
                                plugin_image.exif_keys, plugin_image.xmp_keys,
                                plugin_image.iptc_keys) ]
    return MediaDataTags

def string_to_rational(coordinate):
    """
    convert string to rational variable for GPS
    """

    if '.' in coordinate:
        value1, value2 = coordinate.split('.')
        return pyexiv2.Rational(int(float(value1 + value2)), 10**len(value2))
    else:
        return pyexiv2.Rational(int(coordinate), 1)

def coords_to_rational(Coordinates):
    """
    returns the GPS coordinates to Latitude/ Longitude
    """

    return [string_to_rational(coordinate) for coordinate in Coordinates.split(" ")]

def convert_value(value):
    """
    will take a value from the coordinates and return its value
    """

    if isinstance(value, (Fraction, pyexiv2.Rational)):

        return str( ( Decimal(value.numerator) / Decimal(value.denominator) ) )

def _removesymbols4saving(latitude, longitude):
    """
    will recieve a DMS with symbols and return it without them

    @param: latitude -- Latitude GPS Coordinates
    @param: longitude -- GPS Longitude Coordinates
    """

    # check to see if latitude/ longitude exist?
    if (latitude and longitude):

        # remove degrees symbol if it exist?
        latitude = latitude.replace("°", "")
        longitude = longitude.replace("°", "")

        # remove minutes symbol if it exist?
        latitude = latitude.replace("′", "")
        longitude = longitude.replace("′", "")

        # remove seconds symbol if it exist?
        latitude = latitude.replace('″', "")
        longitude = longitude.replace('″', "")

    return latitude, longitude

def rational_to_dms(coords):
    """
    takes a rational set of coordinates and returns (degrees, minutes, seconds)

    [Fraction(40, 1), Fraction(0, 1), Fraction(1079, 20)]
    """

    deg, min, sec =     False, False, False
    # coordinates look like:
    #     [Rational(38, 1), Rational(38, 1), Rational(150, 50)]
    # or [Fraction(38, 1), Fraction(38, 1), Fraction(318, 100)]   
    if isinstance(coords, list):
    
        if len(coords) == 3:
            return [convert_value(coordinate) for coordinate in coords]

    return deg, min, sec

def _format_datetime(exif_date):
    """
    Convert a python datetime object into a string for display, using the
    standard Gramps date format.
    """

    if not isinstance(exif_date, datetime):
        return ""

    date_part = gen.lib.Date()
    date_part.set_yr_mon_day(exif_date.year, exif_date.month, exif_date.day)
    date_str = _dd.display(date_part)
    time_str = exif_date.strftime('%H:%M:%S')

    return _('%(date)s %(time)s') % {'date': date_str, 'time': time_str}

def _get_date_format(datestr):
    """
    attempt to retrieve date format from date string
    """

    # attempt to determine the dateformat of the variable passed to it...
    tmpDate = False
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
            tmpDate = time.strptime(datestr, dateformat)
            break

        # datestring format  not found...
        except ValueError:
            pass

    return tmpDate

def _create_datetime(pyear, pmonth, day, hour, minutes, seconds):
    """
    will create and retrun a str or datetime from (
        year, month, day, hour, minutes, and seconds) ...

    if the year is less than 1900, then it will return a string representation...
    """

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
    numdays = [0] + [calendar.monthrange(year, month)[1] for year in [pyear] for month in range(1, 13) ]
    if day > numdays[pmonth]:
        day = numdays[pmonth]
    elif day <= 0:
        day = 1

    if pyear < 1900:
        try:
            tmpDate = "%04d-%s-%02d %02d:%02d:%02d" % (pyear, _dd.long_months[pmonth], day,
                                                       hour, minutes, seconds)
        except ValueError:
            tmpDate = False

    else:
        try:
            tmpDate = datetime(pyear, pmonth, day, hour, minutes, seconds)

        except ValueError:
            tmpDate = False

    if tmpDate is False:
        tmpDate = ""

    return tmpDate

def _process_datetime(tmpDate, exif_type =True):
    """
    will attempt to parse the date/ time Exif metadata entry into its pieces...
        (year, month, day, hour, minutes, seconds)
    """

    if not tmpDate:
        return False

    datetype = type(tmpDate)

    # if variable is already in datetime.datetime() format, return it?
    if datetype == datetime:
        pyear, pmonth, day = tmpDate.year, tmpDate.month, tmpDate.day
        hour, minutes, seconds = tmpDate.hour, tmpDate.minute, tmpDate.second        

    elif any(datetype == value for value in [date, gen.lib.date.Date, list] ):
        hour, minutes, seconds = time.localtime()[3:6]

        # datetime.date format
        if isinstance(tmpDate, date):
            pyear, pmonth, day = tmpDate.year, tmpDate.month, tmpDate.day

        # gen.lib.date.Date format
        elif isinstance(tmpDate, gen.lib.date.Date):
            pyear, pmonth, day = tmpDate.get_year(), tmpDate.get_month(), tmpDate.get_day()

        # list format
        else:
            pyear, pmonth, day = tmpDate[0].year, tmpDate[0].month, tmpDate[0].day

    #  string format...
    elif datetype == str:

        datestr = _get_date_format(tmpDate)
        if datestr is not False:
            pyear, pmonth, day, hour, minutes, seconds = datestr[0:6]

        else:
            pyear, pmonth, day, hour, minutes, seconds = [False]*6

    if (not pyear and not pmonth):
        tmpDate = False

    else:

        # create datetime...
        tmpDate = _create_datetime(pyear, pmonth, day, hour, minutes, seconds)

    if tmpDate is not False:

        if isinstance(tmpDate, datetime):

            # for display only...
            # make datetime displayed as user has set in preferences...
            if exif_type:
                tmpDate = _format_datetime(tmpDate)

    return tmpDate
