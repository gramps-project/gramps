#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2004  Donald N. Allingham
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
The DateEdit interface provides visual feedback to the user via a pixamp
to indicate if the assocated GtkEntry box contains a valid date. Green
means complete and valid date. Yellow means a valid, but incomplete date.
Red means that the date is not valid, and will be viewed as a text string
instead of a date.
"""

__author__ = "Donald N. Allingham"
__version__ = "$Revision$"

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.gdk
import gtk.glade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Date
import DateParser
import DateDisplay
import const

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
MOD_TEXT = ( 
    _('Regular'), _('Before'), _('After'), _('About'), 
    _('Range'), _('Span'), _('Text only') )
QUAL_TEXT = ( _('Regular'), _('Estimated'), _('Calculated') )
MONTHS_NAMES = ( 
    DateDisplay.DateDisplay._MONS,
    DateDisplay.DateDisplay._MONS,
    DateDisplay.DateDisplay._hebrew,
    DateDisplay.DateDisplay._french,
    DateDisplay.DateDisplay._persian,
    DateDisplay.DateDisplay._islamic,
    )

#-------------------------------------------------------------------------
#
# DateEdit
#
#-------------------------------------------------------------------------
class DateEdit:
    """Class that associates a pixmap with a text widget, providing visual
    feedback that indicates if the text widget contains a valid date"""

    good = gtk.gdk.pixbuf_new_from_file(const.good_xpm)
    bad = gtk.gdk.pixbuf_new_from_file(const.bad_xpm)
    caution = gtk.gdk.pixbuf_new_from_file(const.caution_xpm)
    
    def __init__(self,text_obj,pixmap_obj):
        """Creates a connection between the text_obj and the pixmap_obj"""

        self.dp = DateParser.DateParser()
        self.text_obj = text_obj
        self.pixmap_obj = pixmap_obj
        self.text_obj.connect('focus-out-event',self.check)
        self.check(None,None)

    def set_calendar(self,cobj):
        self.check(None,None)
        
    def check(self,obj,val):
        """Called with the text box loses focus. If the string contains a
        valid date, sets the appropriate pixmap"""

        text = unicode(self.text_obj.get_text())
        self.checkval = self.dp.parse(text)
        if self.checkval.get_modifier() == Date.MOD_TEXTONLY:
            self.pixmap_obj.set_from_pixbuf(DateEdit.bad)
#        elif self.checkval.get_incomplete():
#            self.pixmap_obj.set_from_pixbuf(DateEdit.caution)
        else:
            self.pixmap_obj.set_from_pixbuf(DateEdit.good)
        
#-------------------------------------------------------------------------
#
# DateEditorDialog
#
#-------------------------------------------------------------------------
class DateEditorDialog:
    """
    Dialog allowing to build the date precisely, to correct defficiencies
    of parsing.
    """

    def __init__(self,date):
        """
        Initiate and display the dialog.
        """

        self.date = date

        self.top = gtk.glade.XML(const.dialogFile, "date_edit","gramps" )
        self.top_window = self.top.get_widget('date_edit')

        self.calendar_box = self.top.get_widget('calendar_box')
        for name in Date.Date.calendar_names:
            self.calendar_box.append_text(name)
        self.calendar_box.set_active(self.date.get_calendar())

        self.quality_box = self.top.get_widget('quality_box')
        for name in QUAL_TEXT:
            self.quality_box.append_text(name)
        self.quality_box.set_active(self.date.get_quality())

        self.type_box = self.top.get_widget('type_box')
        for name in MOD_TEXT:
            self.type_box.append_text(name)
        self.type_box.set_active(self.date.get_modifier())
        self.type_box.connect('changed',self.switch_type)

        self.start_month_box = self.top.get_widget('start_month_box')
        self.stop_month_box = self.top.get_widget('stop_month_box')
        for name in MONTHS_NAMES[self.date.get_calendar()]:
            self.start_month_box.append_text(name)
            self.stop_month_box.append_text(name)
        self.start_month_box.set_active(self.date.get_month())
        self.stop_month_box.set_active(self.date.get_stop_month())
        
        self.start_day = self.top.get_widget('start_day')
        self.start_day.set_value(self.date.get_day())
        self.start_year = self.top.get_widget('start_year')
        self.start_year.set_value(self.date.get_year())

        self.stop_day = self.top.get_widget('stop_day')
        self.stop_day.set_value(self.date.get_stop_day())
        self.stop_year = self.top.get_widget('stop_year')
        self.stop_year.set_value(self.date.get_stop_year())
        
        if not self.date.is_compound():
            self.stop_day.set_sensitive(0)
            self.stop_month_box.set_sensitive(0)
            self.stop_year.set_sensitive(0)

        if self.date.get_modifier() == Date.MOD_TEXTONLY:
            self.start_day.set_sensitive(0)
            self.start_month_box.set_sensitive(0)
            self.start_year.set_sensitive(0)
            self.calendar_box.set_sensitive(0)
            self.quality_box.set_sensitive(0)

        self.text_entry = self.top.get_widget('date_text_entry')
        self.text_entry.set_text(self.date.get_text())

        response = self.top_window.run()

        if response == gtk.RESPONSE_HELP:
            print "Help is not hooked up yet, sorry. Exiting now."
        elif response == gtk.RESPONSE_OK:
            self.build_date_from_ui()
        self.top_window.destroy()

    def get_date(self):
        return self.date

    def build_date_from_ui(self):
        if self.type_box.get_active() == Date.MOD_TEXTONLY:
            self.date.set_as_text(self.text_entry.get_text())
            return

        if self.type_box.get_active() in (Date.MOD_RANGE,Date.MOD_SPAN):
            date_tuple = (
                self.start_day.get_value_as_int(),
                self.start_month_box.get_active(),
                self.start_year.get_value_as_int(),
                False,
                self.stop_day.get_value_as_int(),
                self.stop_month_box.get_active(),
                self.stop_year.get_value_as_int(),
                False)
        else:
            date_tuple = (
                self.start_day.get_value_as_int(),
                self.start_month_box.get_active(),
                self.start_year.get_value_as_int(),
                False)
        self.date.set(
            quality=self.quality_box.get_active(),
            modifier=self.type_box.get_active(),
            calendar=self.calendar_box.get_active(),
            value=date_tuple)
        self.date.set_text_value(self.text_entry.get_text())

    def switch_type(self,obj):
        """
        Disable/enable various date controls depending on the date 
        type selected via the menu.
        """
        if self.type_box.get_active() in (Date.MOD_RANGE,Date.MOD_SPAN):
            stop_date_sensitivity = 1
        else:
            stop_date_sensitivity = 0
        self.stop_day.set_sensitive(stop_date_sensitivity)
        self.stop_month_box.set_sensitive(stop_date_sensitivity)
        self.stop_year.set_sensitive(stop_date_sensitivity)

        date_sensitivity = not self.type_box.get_active() == Date.MOD_TEXTONLY
        self.start_day.set_sensitive(date_sensitivity)
        self.start_month_box.set_sensitive(date_sensitivity)
        self.start_year.set_sensitive(date_sensitivity)
        self.calendar_box.set_sensitive(date_sensitivity)
        self.quality_box.set_sensitive(date_sensitivity)
