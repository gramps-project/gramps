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
from Filters.Rules.MediaObject import *

GenericMediaFilter = GenericFilterFactory('MediaObject')
#-------------------------------------------------------------------------
#
# PersonSidebarFilter class
#
#-------------------------------------------------------------------------
class MediaSidebarFilter(SidebarFilter):

    def __init__(self,uistate, clicked):
        SidebarFilter.__init__(self,uistate)
        self.clicked_func = clicked

    def create_widget(self):
        self.filter_id = gtk.Entry()
        self.filter_title = gtk.Entry()       
        self.filter_type = gtk.Entry()
        self.filter_path = gtk.Entry()
        self.filter_date = gtk.Entry()

        self.filter_note = gtk.Entry()

        self.filter_regex = gtk.CheckButton(_('Use regular expressions'))

	self.generic = gtk.ComboBox()
	cell = gtk.CellRendererText()
	self.generic.pack_start(cell, True)
	self.generic.add_attribute(cell, 'text', 0)
        self.on_filters_changed('MediaObject')

        self.add_text_entry(_('ID'), self.filter_id)
        self.add_text_entry(_('Title'), self.filter_title)
        self.add_text_entry(_('Type'), self.filter_type)
        self.add_text_entry(_('Path'), self.filter_path)
        self.add_text_entry(_('Date'), self.filter_date)
        self.add_text_entry(_('Note'), self.filter_note)
        self.add_entry(_('Custom filter'), self.generic)
        self.add_entry(None, self.filter_regex)

    def clear(self, obj):
        self.filter_id.set_text('')
        self.filter_title.set_text('')
        self.filter_type.set_text('')
        self.filter_path.set_text('')
        self.filter_date.set_text('')
        self.filter_note.set_text('')
        self.generic.set_active(0)

    def get_filter(self):
        gid = unicode(self.filter_id.get_text()).strip()
        title = unicode(self.filter_title.get_text()).strip()
        mime = unicode(self.filter_type.get_text()).strip()
        path = unicode(self.filter_path.get_text()).strip()
        date = unicode(self.filter_date.get_text()).strip()
        note = unicode(self.filter_note.get_text()).strip()
        regex = self.filter_regex.get_active()
	gen = self.generic.get_active() > 0

        empty = not (gid or title or mime or path or date
                     or note or regex or gen)
        if empty:
            generic_filter = None
        else:
            generic_filter = GenericMediaFilter()
            if gid:
                if regex:
                    rule = RegExpIdOf([gid])
                else:
                    rule = HasIdOf([gid])
                generic_filter.add_rule(rule)

            rule = HasMedia([title,mime,path,date])
            generic_filter.add_rule(rule)
                
            if note:
                if regex:
                    rule = HasNoteRegexp([note])
                else:
                    rule = HasNoteMatchingSubstringOf([note])
                generic_filter.add_rule(rule)

	    if self.generic.get_active() != 0:
		model = self.generic.get_model()
		node = self.generic.get_active_iter()
		obj = model.get_value(node, 0)
		rule = MatchesFilter([obj])
		generic_filter.add_rule(rule)

        return generic_filter

    def on_filters_changed(self,name_space):
        if name_space == 'MediaObject':
            all = GenericMediaFilter()
            all.set_name(_("None"))
            all.add_rule(Rules.MediaObject.AllMedia([]))
            self.generic.set_model(build_filter_model('MediaObject', [all]))
            self.generic.set_active(0)
