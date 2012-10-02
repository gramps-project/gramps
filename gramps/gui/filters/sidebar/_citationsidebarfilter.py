#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2011       Tim G L Lyons
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
from gramps.gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# gtk
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gramps.gui.widgets import MonitoredMenu
from gramps.gen.lib import Citation
from gramps.gui.filters import build_filter_model
from gramps.gui.filters.sidebar import SidebarFilter
from gramps.gen.filters import GenericFilterFactory, rules
from gramps.gen.filters.rules.citation import (RegExpIdOf, HasIdOf, HasCitation, 
                                        HasNoteMatchingSubstringOf, 
                                        HasNoteRegexp, MatchesFilter)
from gramps.gen.utils.string import confidence
GenericCitationFilter = GenericFilterFactory('Citation')
#-------------------------------------------------------------------------
#
# CitationSidebarFilter class
#
#-------------------------------------------------------------------------
class CitationSidebarFilter(SidebarFilter):

    def __init__(self, dbstate, uistate, clicked):
        self.clicked_func = clicked
        self.filter_id = Gtk.Entry()
        self.filter_page = Gtk.Entry()       
        self.filter_date = Gtk.Entry()
        
        self.filter_conf = Gtk.ComboBox()
        model = Gtk.ListStore(str)
        for conf_value in sorted(confidence.keys()):
            model.append((confidence[conf_value],))
        self.filter_conf.set_model(model)
        self.filter_conf.set_active(2)  # Citation.CONF_NORMAL
        
        self.filter_note = Gtk.Entry()

        self.filter_regex = Gtk.CheckButton(_('Use regular expressions'))

        self.generic = Gtk.ComboBox()

        SidebarFilter.__init__(self, dbstate, uistate, "Citation")

    def create_widget(self):
        cell = Gtk.CellRendererText()
        cell.set_property('width', self._FILTER_WIDTH)
        cell.set_property('ellipsize', self._FILTER_ELLIPSIZE)
        self.generic.pack_start(cell, True)
        self.generic.add_attribute(cell, 'text', 0)
        self.on_filters_changed('Citation')

        cell = Gtk.CellRendererText()
        cell.set_property('width', self._FILTER_WIDTH)
        cell.set_property('ellipsize', self._FILTER_ELLIPSIZE)
        self.filter_conf.pack_start(cell, True)
        self.filter_conf.add_attribute(cell, 'text', 0)

        self.add_text_entry(_('ID'), self.filter_id)
        self.add_text_entry(_('Volume/Page'), self.filter_page)
        self.add_text_entry(_('Date'), self.filter_date)
        self.add_entry(_('Confidence'), self.filter_conf)
        self.add_text_entry(_('Note'), self.filter_note)
        self.add_filter_entry(_('Custom filter'), self.generic)
        self.add_entry(None, self.filter_regex)

    def clear(self, obj):
        self.filter_id.set_text('')
        self.filter_page.set_text('')
        self.filter_date.set_text('')
        self.filter_conf.set_active(2)
        self.filter_note.set_text('')
        self.generic.set_active(0)

    def get_filter(self):
        gid = unicode(self.filter_id.get_text()).strip()
        page = unicode(self.filter_page.get_text()).strip()
        date = unicode(self.filter_date.get_text()).strip()
        model = self.filter_conf.get_model()
        node = self.filter_conf.get_active_iter()
        conf_name = model.get_value(node, 0)  # The value is actually the text
        conf = 2
        for i in confidence.keys():
            if confidence[i] == conf_name:
                conf = i
                break
#        conf = self.citn.get_confidence_level()
        note = unicode(self.filter_note.get_text()).strip()
        regex = self.filter_regex.get_active()
        gen = self.generic.get_active() > 0

        empty = not (gid or page or date or conf or note or regex or gen)
        if empty:
            generic_filter = None
        else:
            generic_filter = GenericCitationFilter()
            if gid:
                if regex:
                    rule = RegExpIdOf([gid])
                else:
                    rule = HasIdOf([gid])
                generic_filter.add_rule(rule)

            rule = HasCitation([page, date, conf], use_regex=regex)
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
            obj = unicode(model.get_value(node, 0))
            rule = MatchesFilter([obj])
            generic_filter.add_rule(rule)

        return generic_filter

    def on_filters_changed(self, name_space):
        if name_space == 'Citation':
            all_filter = GenericCitationFilter()
            all_filter.set_name(_("None"))
            all_filter.add_rule(rules.citation.AllCitations([]))
            self.generic.set_model(build_filter_model('Citation', [all_filter]))
            self.generic.set_active(0)
