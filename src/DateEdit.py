#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002  Donald N. Allingham
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
# GNOME modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.gdk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Date
import DateParser
import const

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
            
        
