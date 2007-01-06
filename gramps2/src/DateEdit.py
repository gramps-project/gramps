#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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
Date editing module for GRAMPS. 

The DateEdit.DateEdit provides visual feedback to the user via a pixamp
to indicate if the assocated GtkEntry box contains a valid date. Green
means complete and regular date. Yellow means a valid, but not a regular date.
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
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".DateEdit")

#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from RelLib import Date
import DateHandler
import const
import GrampsDisplay
import ManagedWindow
from Errors import MaskError, ValidationError

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
    (Date.QUAL_NONE,       _('Regular')), 
    (Date.QUAL_ESTIMATED,  _('Estimated')), 
    (Date.QUAL_CALCULATED, _('Calculated')) )

CAL_TO_MONTHS_NAMES = { 
    Date.CAL_GREGORIAN  : DateHandler.displayer._MONS,
    Date.CAL_JULIAN     : DateHandler.displayer._MONS,
    Date.CAL_HEBREW     : DateHandler.displayer._hebrew,
    Date.CAL_FRENCH     : DateHandler.displayer._french,
    Date.CAL_PERSIAN    : DateHandler.displayer._persian,
    Date.CAL_ISLAMIC    : DateHandler.displayer._islamic }

#-------------------------------------------------------------------------
#
# DateEdit
#
#-------------------------------------------------------------------------
class DateEdit:
    """Class that associates a pixmap with a text widget, providing visual
    feedback that indicates if the text widget contains a valid date"""

    def __init__(self, date_obj, text_obj, button_obj, uistate, track):
        """
        Creates a connection between the date_obj, text_obj and the pixmap_obj.
        Assigns callbacks to parse and change date when the text
        in text_obj is changed, and to invoke Date Editor when the LED
        button_obj is pressed. 
        """
        self.uistate = uistate
        self.track = track
        self.date_obj = date_obj
        self.text_obj = text_obj
        self.button_obj = button_obj

        self.pixmap_obj = button_obj.get_child()
        
        self.text_obj.connect('validate',self.validate)
        self.button_obj.connect('clicked',self.invoke_date_editor)
        
        self.text = unicode(self.text_obj.get_text())
        self.check()

    def check(self):
        """
        Check current date object and display LED indicating the validity.
        """
        if self.date_obj.get_modifier() == Date.MOD_TEXTONLY:
            self.text_obj.set_invalid()
            return False
        else:
            self.text_obj.set_valid()
            return True
        
    def parse_and_check(self,*obj):
        """
        Called with the text box loses focus. Parses the text and calls 
        the check() method ONLY if the text has changed.
        """
        text = unicode(self.text_obj.get_text())
        if text != self.text:
            self.text = text
            self.date_obj.copy(DateHandler.parser.parse(text))
            self.text_obj.set_text(DateHandler.displayer.display(self.date_obj))
            if self.check():
                return None
            else:
                return ValidationError('Bad Date')

    def validate(self, widget, data):
        """
        Called with the text box loses focus. Parses the text and calls 
        the check() method ONLY if the text has changed.
        """
        self.date_obj.copy(DateHandler.parser.parse(unicode(data)))
        if self.check():
            return None
        else:
            return ValidationError('Bad Date')

    def invoke_date_editor(self,obj):
        """
        Invokes Date Editor dialog when the user clicks the LED button.
        If date was in fact built, sets the date_obj to the newly built
        date.
        """
        date_dialog = DateEditorDialog(self.date_obj, self.uistate, self.track)
        the_date = date_dialog.return_date
        self.update_after_editor(the_date)

    def update_after_editor(self,date_obj):
        """
        Update text field and LED button to reflect the given date instance.
        """
        if date_obj:
            self.date_obj.copy(date_obj)
            self.text_obj.set_text(DateHandler.displayer.display(self.date_obj))
            self.check()
        
#-------------------------------------------------------------------------
#
# DateEditorDialog
#
#-------------------------------------------------------------------------
class DateEditorDialog(ManagedWindow.ManagedWindow):
    """
    Dialog allowing to build the date precisely, to correct possible 
    limitations of parsing and/or underlying structure of Date.
    """

    def __init__(self, date, uistate, track):
        """
        Initiate and display the dialog.
        """

        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)
        
        # Create self.date as a copy of the given Date object.
        self.date = Date(date)

        self.top = gtk.glade.XML(const.gladeFile, "date_edit","gramps" )

        self.set_window(
            self.top.get_widget('date_edit'),
            self.top.get_widget('title'),
            _('Date selection'))            
            
        self.calendar_box = self.top.get_widget('calendar_box')
        for name in Date.ui_calendar_names:
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
        
        # The dialog is modal -- since dates don't have names, we don't
        # want to have several open dialogs, since then the user will
        # loose track of which is which. Much like opening files.
        
        self.return_date = None

        self.show()

        while True:
            response = self.window.run()
            if response == gtk.RESPONSE_HELP:
                GrampsDisplay.help('adv-dates')
            elif response == gtk.RESPONSE_DELETE_EVENT:
                return
            else:
                if response == gtk.RESPONSE_OK:
                    (the_quality,the_modifier,the_calendar,
                     the_value,the_text) = self.build_date_from_ui()
                    self.return_date = Date(self.date)
                    self.return_date.set(
                        quality=the_quality,
                        modifier=the_modifier,
                        calendar=the_calendar,
                        value=the_value,
                        text=the_text)
                self.close()
                return

    def build_menu_names(self, obj):
        return (_("Date selection"), None)

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
        Change month names and convert the date based on the calendar 
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
                value=the_value,
                text=the_text)

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
