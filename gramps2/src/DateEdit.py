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
The DateEdit module provides classes. 

The DateEdit.DateEdit provides two visual feedback to the user via a pixamp
to indicate if the assocated GtkEntry box contains a valid date. Green
means complete and valid date. Yellow means a valid, but incomplete date.
Red means that the date is not valid, and will be viewed as a text string
instead of a date.

The DateEdit.DateEditor provides a dialog in which the date can be 
unambiguously built using UI controls such as menus and spin buttons.
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
import gobject

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Date
import DateParser
import DateDisplay
import const
import Utils

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
MOD_TEXT = ( 
    (Date.MOD_NONE       , _('Regular')),
    (Date.MOD_BEFORE     , _('Before')),
    (Date.MOD_AFTER      , _('After')),
    (Date.MOD_ABOUT      , _('About')),
    (Date.MOD_RANGE      , _('Range')),
    (Date.MOD_SPAN       , _('Span')),
    (Date.MOD_TEXTONLY   , _('Text only')) )

QUAL_TEXT = (
    (Date.QUAL_NONE, _('Regular')), 
    (Date.QUAL_ESTIMATED, _('Estimated')), 
    (Date.QUAL_CALCULATED, _('Calculated')) )

CAL_TO_MONTHS_NAMES = { 
    Date.CAL_GREGORIAN  : DateDisplay.DateDisplay._MONS,
    Date.CAL_JULIAN     : DateDisplay.DateDisplay._MONS,
    Date.CAL_HEBREW     : DateDisplay.DateDisplay._hebrew,
    Date.CAL_FRENCH     : DateDisplay.DateDisplay._french,
    Date.CAL_PERSIAN    : DateDisplay.DateDisplay._persian,
    Date.CAL_ISLAMIC    : DateDisplay.DateDisplay._islamic }

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
    
    def __init__(self,text_obj,button_obj):
        """Creates a connection between the text_obj and the pixmap_obj"""

        self.dp = DateParser.DateParser()
        self.text_obj = text_obj
        self.button_obj = button_obj
        self.pixmap_obj = button_obj.get_child()
        self.text_obj.connect('focus-out-event',self.check)
        self.check(None,None)
        self.button_obj.connect('clicked',self.invoke_date_editor)

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
    
    def invoke_date_editor(self,obj):
        date_dialog = DateEditorDialog(self.checkval)
        the_date = date_dialog.get_date()
        self.text_obj.set_text(str(the_date))
        print "The date was built as follows:", the_date
        
#-------------------------------------------------------------------------
#
# DateEditorDialog
#
#-------------------------------------------------------------------------
class DateEditorDialog:
    """
    Dialog allowing to build the date precisely, to correct possible 
    limitations of parsing and/or underlying structure of Date.
    """

    def __init__(self,date):
        """
        Initiate and display the dialog.
        """

        # Create self.date as a copy of the given Date object.
        self.date = Date.Date(date)
        # Keep the given Date object safe as self.old_date 
        # until we're happy with modifying and want to commit.
        self.old_date = date

        self.top = gtk.glade.XML(const.dialogFile, "date_edit","gramps" )
        self.top_window = self.top.get_widget('date_edit')
        title = self.top.get_widget('title')
        Utils.set_titles(self.top_window,title,_('Date selection'))

        self.calendar_box = self.top.get_widget('calendar_box')
        for name in Date.Date.calendar_names:
            self.calendar_box.append_text(name)
        self.calendar_box.set_active(self.date.get_calendar())
        self.calendar_box.connect('changed',self.switch_calendar)

        self.quality_box = self.top.get_widget('quality_box')
        for item_number in range(len(QUAL_TEXT)):
            self.quality_box.append_text(QUAL_TEXT[item_number][1])
            if self.date.get_quality() == QUAL_TEXT[item_number][0]:
                self.quality_box.set_active(item_number)

        self.type_box = self.top.get_widget('type_box')
        for item_number in range(len(MOD_TEXT)):
            self.type_box.append_text(MOD_TEXT[item_number][1])
            if self.date.get_modifier() == MOD_TEXT[item_number][0]:
                self.type_box.set_active(item_number)
        self.type_box.connect('changed',self.switch_type)

        self.start_month_box = self.top.get_widget('start_month_box')
        self.stop_month_box = self.top.get_widget('stop_month_box')
        month_names = CAL_TO_MONTHS_NAMES[self.date.get_calendar()]
        for name in month_names:
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
        
        # Disable second date controls if not compound date
        if not self.date.is_compound():
            self.stop_day.set_sensitive(0)
            self.stop_month_box.set_sensitive(0)
            self.stop_year.set_sensitive(0)

        # Disable the rest of controls if a text-only date
        if self.date.get_modifier() == Date.MOD_TEXTONLY:
            self.start_day.set_sensitive(0)
            self.start_month_box.set_sensitive(0)
            self.start_year.set_sensitive(0)
            self.calendar_box.set_sensitive(0)
            self.quality_box.set_sensitive(0)

        self.text_entry = self.top.get_widget('date_text_entry')
        self.text_entry.set_text(self.date.get_text())
        
        # The dialog is modal -- since dates don't have name, we don't
        # want to have several open dialogs, since then the user will
        # loose track of which is which.
        response = self.top_window.run()
        self.top_window.destroy()

        if response == gtk.RESPONSE_HELP:
            # Here be help :-)
            print "Help is not hooked up yet, sorry. Exiting now."
        elif response == gtk.RESPONSE_OK:
            (the_quality,the_modifier,the_calendar,the_value,the_text) = \
                                        self.build_date_from_ui()
            self.old_date.set(
                quality=the_quality,
                modifier=the_modifier,
                calendar=the_calendar,
                value=the_value)
            self.old_date.set_text_value(the_text)

    def get_date(self):
        """
        Return the current date.
        """
        return self.date

    def build_date_from_ui(self):
        """
        Collect information from the UI controls and return 
        5-tuple of (quality,modifier,calendar,value,text) 
        """
        # It is important to not set date based on these controls. 
        # For example, changing the caledar makes the date inconsistent
        # until the callback of the calendar menu is finished. 
        # We need to be able to use this function from that callback,
        # so here we just report on the state of all widgets, without
        # actually modifying the date yet.
        
        modifier = MOD_TEXT[self.type_box.get_active()][0]
        text = self.text_entry.get_text()

        if modifier == Date.MOD_TEXTONLY:
            date.set_as_text(self.text_entry.get_text())
            return (Date.QUAL_NONE,Date.MOD_TEXTONLY,Date.CAL_GREGORIAN,
                                            Date.EMPTY,text)

        quality = QUAL_TEXT[self.quality_box.get_active()][0]

        if modifier in (Date.MOD_RANGE,Date.MOD_SPAN):
            value = (
                self.start_day.get_value_as_int(),
                self.start_month_box.get_active(),
                self.start_year.get_value_as_int(),
                False,
                self.stop_day.get_value_as_int(),
                self.stop_month_box.get_active(),
                self.stop_year.get_value_as_int(),
                False)
        else:
            value = (
                self.start_day.get_value_as_int(),
                self.start_month_box.get_active(),
                self.start_year.get_value_as_int(),
                False)
        calendar = self.calendar_box.get_active()
        return (quality,modifier,calendar,value,text)

    def switch_type(self,obj):
        """
        Disable/enable various date controls depending on the date 
        type selected via the menu.
        """

        the_modifier = MOD_TEXT[self.type_box.get_active()][0]
        
        # Disable/enable second date controls based on whether
        # the type allows compound dates
        if the_modifier in (Date.MOD_RANGE,Date.MOD_SPAN):
            stop_date_sensitivity = 1
        else:
            stop_date_sensitivity = 0
        self.stop_day.set_sensitive(stop_date_sensitivity)
        self.stop_month_box.set_sensitive(stop_date_sensitivity)
        self.stop_year.set_sensitive(stop_date_sensitivity)

        # Disable/enable the rest of the controls if the type is text-only.
        date_sensitivity = not the_modifier == Date.MOD_TEXTONLY
        self.start_day.set_sensitive(date_sensitivity)
        self.start_month_box.set_sensitive(date_sensitivity)
        self.start_year.set_sensitive(date_sensitivity)
        self.calendar_box.set_sensitive(date_sensitivity)
        self.quality_box.set_sensitive(date_sensitivity)

    def switch_calendar(self,obj):
        """
        Change month names and convert the date on the calendar 
        selected via the menu.
        """
        
        old_cal = self.date.get_calendar()
        new_cal = self.calendar_box.get_active()

        (the_quality,the_modifier,the_calendar,the_value,the_text) = \
                                        self.build_date_from_ui()
        self.date.set(
                quality=the_quality,
                modifier=the_modifier,
                calendar=old_cal,
                value=the_value)
        self.date.set_text_value(the_text)

        self.date.convert_calendar(new_cal)
        
        self.start_month_box.get_model().clear()
        self.stop_month_box.get_model().clear()
        month_names = CAL_TO_MONTHS_NAMES[new_cal]
        for name in month_names:
            self.start_month_box.append_text(name)
            self.stop_month_box.append_text(name)

        self.start_day.set_value(self.date.get_day())
        self.start_month_box.set_active(self.date.get_month())
        self.start_year.set_value(self.date.get_year())
        self.stop_day.set_value(self.date.get_stop_day())
        self.stop_month_box.set_active(self.date.get_stop_month())
        self.stop_year.set_value(self.date.get_stop_year())
