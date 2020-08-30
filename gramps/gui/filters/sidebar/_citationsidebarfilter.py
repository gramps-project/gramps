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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

#-------------------------------------------------------------------------
#
# gtk
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

from ...widgets import MonitoredMenu, DateEntry, BasicEntry
from gramps.gen.lib import Citation
from .. import build_filter_model
from . import SidebarFilter
from gramps.gen.filters import GenericFilterFactory, rules
from gramps.gen.filters.rules.citation import (RegExpIdOf, HasCitation, HasTag,
                                               HasNoteRegexp, MatchesFilter,
                                               HasSource, RegExpSourceIdOf,
                                               HasSourceNoteRegexp)
from gramps.gen.utils.string import conf_strings
GenericCitationFilter = GenericFilterFactory('Citation')
#-------------------------------------------------------------------------
#
# CitationSidebarFilter class
#
#-------------------------------------------------------------------------
class CitationSidebarFilter(SidebarFilter):

    def __init__(self, dbstate, uistate, clicked):
        self.clicked_func = clicked
        self.filter_src_id = BasicEntry()
        self.filter_src_title = BasicEntry()
        self.filter_src_author = BasicEntry()
        self.filter_src_abbr = BasicEntry()
        self.filter_src_pub = BasicEntry()
        self.filter_src_note = BasicEntry()
        self.filter_id = Gtk.Entry()
        self.filter_page = Gtk.Entry()
        self.filter_date = DateEntry(uistate, [])

        self.filter_conf = Gtk.ComboBox()
        model = Gtk.ListStore(str)
        for conf_value in sorted(conf_strings.keys()):
            model.append((_(conf_strings[conf_value]),))
        self.filter_conf.set_model(model)
        self.filter_conf.set_active(Citation.CONF_NORMAL)

        self.filter_note = Gtk.Entry()

        self.filter_regex = Gtk.CheckButton(label=_('Use regular expressions'))

        self.tag = Gtk.ComboBox()
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

        cell = Gtk.CellRendererText()
        cell.set_property('width', self._FILTER_WIDTH)
        cell.set_property('ellipsize', self._FILTER_ELLIPSIZE)
        self.tag.pack_start(cell, True)
        self.tag.add_attribute(cell, 'text', 0)

        self.add_heading(_('Source:'))
        self.add_text_entry(_('ID'), self.filter_src_id)
        self.add_text_entry(_('Title'), self.filter_src_title)
        self.add_text_entry(_('Author'), self.filter_src_author)
        self.add_text_entry(_('Abbreviation'), self.filter_src_abbr)
        self.add_text_entry(_('Publication'), self.filter_src_pub)
        self.add_text_entry(_('Note'), self.filter_src_note)
        self.add_heading(_('Citation:'))
        self.add_text_entry(_('ID'), self.filter_id)
        self.add_text_entry(_('Volume/Page'), self.filter_page)
        self.add_text_entry(_('Date'), self.filter_date)
        self.add_entry(_('Min. Conf.', 'Citation: Minimum Confidence'), self.filter_conf)
        self.add_text_entry(_('Note'), self.filter_note)
        self.add_entry(_('Tag'), self.tag)
        self.add_filter_entry(_('Custom filter'), self.generic)
        self.add_entry(None, self.filter_regex)

    def clear(self, obj):
        self.filter_src_id.set_text('')
        self.filter_src_title.set_text('')
        self.filter_src_author.set_text('')
        self.filter_src_abbr.set_text('')
        self.filter_src_pub.set_text('')
        self.filter_src_note.set_text('')
        self.filter_id.set_text('')
        self.filter_page.set_text('')
        self.filter_date.set_text('')
        self.filter_conf.set_active(Citation.CONF_NORMAL)
        self.filter_note.set_text('')
        self.tag.set_active(0)
        self.generic.set_active(0)

    def get_filter(self):
        src_id = str(self.filter_src_id.get_text()).strip()
        src_title = str(self.filter_src_title.get_text()).strip()
        src_author = str(self.filter_src_author.get_text()).strip()
        src_abbr = str(self.filter_src_abbr.get_text()).strip()
        src_pub = str(self.filter_src_pub.get_text()).strip()
        src_note = str(self.filter_src_note.get_text()).strip()
        gid = str(self.filter_id.get_text()).strip()
        page = str(self.filter_page.get_text()).strip()
        date = str(self.filter_date.get_text()).strip()
        conf = str(self.filter_conf.get_active())
        note = str(self.filter_note.get_text()).strip()
        regex = self.filter_regex.get_active()
        tag = self.tag.get_active() > 0
        gen = self.generic.get_active() > 0

        empty = not (src_id or src_title or src_author or src_abbr or src_pub or
                     src_note or
                     gid or page or date or conf or note or regex or gen)
        if empty:
            generic_filter = None
        else:
            generic_filter = GenericCitationFilter()
            if gid:
                rule = RegExpIdOf([gid], use_regex=regex)
                generic_filter.add_rule(rule)

            rule = HasCitation([page, date, conf], use_regex=regex)
            generic_filter.add_rule(rule)

            if src_id:
                rule = RegExpSourceIdOf([src_id], use_regex=regex)
                generic_filter.add_rule(rule)

            rule = HasSource([src_title, src_author, src_abbr, src_pub],
                             use_regex=regex)
            generic_filter.add_rule(rule)

            if note:
                rule = HasNoteRegexp([note], use_regex=regex)
                generic_filter.add_rule(rule)

            if src_note:
                rule = HasSourceNoteRegexp([src_note], use_regex=regex)
                generic_filter.add_rule(rule)

            # check the Tag
            if tag:
                model = self.tag.get_model()
                node = self.tag.get_active_iter()
                attr = model.get_value(node, 0)
                rule = HasTag([attr])
                generic_filter.add_rule(rule)

            if self.generic.get_active() != 0:
                model = self.generic.get_model()
                node = self.generic.get_active_iter()
                obj = str(model.get_value(node, 0))
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

    def on_tags_changed(self, tag_list):
        """
        Update the list of tags in the tag filter.
        """
        model = Gtk.ListStore(str)
        model.append(('',))
        for tag_name in tag_list:
            model.append((tag_name,))
        self.tag.set_model(model)
        self.tag.set_active(0)
