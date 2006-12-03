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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# gtk
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import GrampsWidgets
import RelLib

from _SidebarFilter import SidebarFilter
from Filters import GenericFilterFactory, build_filter_model, Rules
from Filters.Rules.Place import *

GenericPlaceFilter = GenericFilterFactory('Place')
#-------------------------------------------------------------------------
#
# PersonSidebarFilter class
#
#-------------------------------------------------------------------------
class PlaceSidebarFilter(SidebarFilter):

    def __init__(self,uistate, clicked):
        SidebarFilter.__init__(self,uistate)
        self.clicked_func = clicked

    def create_widget(self):
        self.filter_id = gtk.Entry()
        self.filter_title = gtk.Entry()       
        self.filter_parish = gtk.Entry()
        self.filter_zip = gtk.Entry()
        self.filter_city = gtk.Entry()
        self.filter_county = gtk.Entry()
        self.filter_state = gtk.Entry()
        self.filter_country = gtk.Entry()

        self.filter_note = gtk.Entry()

        self.filter_regex = gtk.CheckButton(_('Use regular expressions'))

	self.generic = gtk.ComboBox()
	cell = gtk.CellRendererText()
	self.generic.pack_start(cell, True)
	self.generic.add_attribute(cell, 'text', 0)
        self.on_filters_changed('Place')

        self.add_text_entry(_('ID'), self.filter_id)
        self.add_text_entry(_('Name'), self.filter_title)
        self.add_text_entry(_('Church parish'), self.filter_parish)
        self.add_text_entry(_('Zip/Postal code'), self.filter_zip)
        self.add_text_entry(_('City'), self.filter_city)
        self.add_text_entry(_('County'), self.filter_county)
        self.add_text_entry(_('State'), self.filter_state)
        self.add_text_entry(_('Country'), self.filter_country)
        self.add_text_entry(_('Note'), self.filter_note)
        self.add_entry(_('Custom filter'), self.generic)
        self.add_entry(None, self.filter_regex)

    def clear(self, obj):
        self.filter_id.set_text('')
        self.filter_title.set_text('')
        self.filter_parish.set_text('')
        self.filter_zip.set_text('')
        self.filter_city.set_text('')
        self.filter_county.set_text('')
        self.filter_state.set_text('')
        self.filter_country.set_text('')
        self.filter_note.set_text('')
        self.generic.set_active(0)

    def get_filter(self):
        gid = unicode(self.filter_id.get_text()).strip()
        title = unicode(self.filter_title.get_text()).strip()
        parish = unicode(self.filter_parish.get_text()).strip()
        zipc = unicode(self.filter_zip.get_text()).strip()
        city = unicode(self.filter_city.get_text()).strip()
        county = unicode(self.filter_county.get_text()).strip()
        state = unicode(self.filter_state.get_text()).strip()
        country = unicode(self.filter_country.get_text()).strip()
        note = unicode(self.filter_note.get_text()).strip()
        regex = self.filter_regex.get_active()
	gen = self.generic.get_active() > 0

        empty = not (gid or title or parish or zipc or city or county
                     or state or country or note or regex or gen)
        if empty:
            generic_filter = None
        else:
            generic_filter = GenericPlaceFilter()
            if gid:
                if regex:
                    rule = RegExpIdOf([gid])
                else:
                    rule = HasIdOf([gid])
                generic_filter.add_rule(rule)

            rule = HasPlace([title,parish,zipc,city,county,state,country])
            generic_filter.add_rule(rule)
                
            if note:
                if regex:
                    rule = HasNoteRegexp([note])
                else:
                    rule = HasNoteMatchingSubstringOf([note])
                generic_filter.add_rule(rule)

	    if self.generic.get_active() != 0:
		model = self.generic.get_model()
		iter = self.generic.get_active_iter()
		obj = model.get_value(iter, 0)
		rule = MatchesFilter([obj])
		generic_filter.add_rule(rule)

        return generic_filter

    def on_filters_changed(self,name_space):
        if name_space == 'Place':
            all = GenericPlaceFilter()
            all.set_name(_("None"))
            all.add_rule(Rules.Place.AllPlaces([]))
            self.generic.set_model(build_filter_model('Place', [all]))
            self.generic.set_active(0)
