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
from RelLib import Repository, RepositoryType

from _SidebarFilter import SidebarFilter
from Filters import GenericFilterFactory, build_filter_model, Rules
from Filters.Rules.Repository import *

GenericRepoFilter = GenericFilterFactory('Repository')
#-------------------------------------------------------------------------
#
# PersonSidebarFilter class
#
#-------------------------------------------------------------------------
class RepoSidebarFilter(SidebarFilter):

    def __init__(self,uistate, clicked):
        SidebarFilter.__init__(self,uistate)
        self.clicked_func = clicked

    def create_widget(self):
        self.filter_id = gtk.Entry()
        self.filter_title = gtk.Entry()       
        self.filter_address = gtk.Entry()
        self.filter_url = gtk.Entry()

        self.repo = Repository()
        self.repo.set_type((RepositoryType.CUSTOM,''))
        self.rtype = gtk.ComboBoxEntry()
        self.event_menu = GrampsWidgets.MonitoredDataType(
            self.rtype,
            self.repo.set_type,
            self.repo.get_type)

        self.filter_note = gtk.Entry()

        self.filter_regex = gtk.CheckButton(_('Use regular expressions'))

	self.generic = gtk.ComboBox()
	cell = gtk.CellRendererText()
	self.generic.pack_start(cell, True)
	self.generic.add_attribute(cell, 'text', 0)
        self.on_filters_changed('Repository')

        self.add_text_entry(_('ID'), self.filter_id)
        self.add_text_entry(_('Name'), self.filter_title)
        self.add_entry(_('Type'), self.rtype)
        self.add_text_entry(_('Address'), self.filter_address)
        self.add_text_entry(_('URL'), self.filter_url)
        self.add_text_entry(_('Note'), self.filter_note)
        self.add_entry(_('Custom filter'), self.generic)
        self.add_entry(None, self.filter_regex)

    def clear(self, obj):
        self.filter_id.set_text('')
        self.filter_title.set_text('')
        self.filter_address.set_text('')
        self.filter_url.set_text('')
        self.rtype.child.set_text('')
        self.filter_note.set_text('')
        self.generic.set_active(0)

    def get_filter(self):
        gid = unicode(self.filter_id.get_text()).strip()
        title = unicode(self.filter_title.get_text()).strip()
        address = unicode(self.filter_address.get_text()).strip()
        url = unicode(self.filter_url.get_text()).strip()
        rtype = self.repo.get_type().xml_str()
        note = unicode(self.filter_note.get_text()).strip()
        regex = self.filter_regex.get_active()
	gen = self.generic.get_active() > 0

        empty = not (gid or title or address or url or rtype
                     or note or regex or gen)
        if empty:
            generic_filter = None
        else:
            generic_filter = GenericRepoFilter()
            if gid:
                if regex:
                    rule = RegExpIdOf([gid])
                else:
                    rule = HasIdOf([gid])
                generic_filter.add_rule(rule)

            rule = HasRepo([title,rtype,address,url])
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
        if name_space == 'Repository':
            all = GenericRepoFilter()
            all.set_name(_("None"))
            all.add_rule(Rules.Repository.AllRepos([]))
            self.generic.set_model(build_filter_model('Repository', [all]))
            self.generic.set_active(0)
