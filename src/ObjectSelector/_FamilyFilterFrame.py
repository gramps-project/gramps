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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

import gtk
import gobject

from GrampsWidgets import IntEdit
from _FilterFrameBase import FilterFrameBase

class FamilyFilterFrame(FilterFrameBase):
    
    __gproperties__ = {}

    __gsignals__ = {
        }

    __default_border_width = 5

    def __init__(self,filter_spec=None,label="Filter"):
	FilterFrameBase.__init__(self,filter_spec,label)

        # Gramps ID
	self._id_check,self._id_label,self._id_edit = \
	    self.make_text_widget("Gramps ID")

        # Name
	self._name_check,self._name_label,self._name_edit = \
	    self.make_text_widget("Name")

        # Mar
	self._mar_check, self._m_edit, \
	    self._m_before, self._m_after, \
	    self._m_unknown  = self.make_year_widget("Marriage Year")

        # Filter
        default_filters = []

	# don't currently support filters that need an attribute.	
	filters = [ filter for filter in default_filters if \
		    not hasattr(filter,'labels') or len(filter.labels) == 0 ]

        self._filter_list = gtk.ListStore(str,object)

        for filter in filters:
	    self._filter_list.append([filter.name,filter])

	self._filter_check,self._filter_label,self._filter_combo = \
	    self.make_combo_widget("Filter",self._filter_list)
        
        self._reset_widgets()

        if filter_spec is not None:
            self._set_filter(filter_spec)


    def _set_filter(filter_spec):
        pass
    
    def on_apply(self,button):
        pass
    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(FamilyFilterFrame)

if __name__ == "__main__":

    w = gtk.Window()
    f = FamilyFilterFrame()
    w.add(f)
    w.show_all()

    gtk.main()
