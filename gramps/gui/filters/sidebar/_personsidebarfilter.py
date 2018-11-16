#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2010       Nick Hall
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
# Python modules
#
#-------------------------------------------------------------------------

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
_ = glocale.translation.gettext
from ... import widgets
from gramps.gen.lib import Date, Event, EventType
from gramps.gen.datehandler import displayer
from .. import build_filter_model
from . import SidebarFilter
from gramps.gen.filters import GenericFilter, rules
from gramps.gen.filters.rules.person import (RegExpName, RegExpIdOf, IsMale,
                                             IsFemale, HasUnknownGender,
                                             HasEvent, HasTag, HasBirth,
                                             HasDeath, HasNoteRegexp,
                                             MatchesFilter)

def extract_text(entry_widget):
    """
    Extract the text from the entry widget, strips off any extra spaces,
    and converts the string to unicode.

    For some strange reason a gtk bug prevents the extracted string from being
    of type unicode.

    """
    return str(entry_widget.get_text().strip())

#-------------------------------------------------------------------------
#
# PersonSidebarFilter class
#
#-------------------------------------------------------------------------
class PersonSidebarFilter(SidebarFilter):

    def __init__(self, dbstate, uistate, clicked):
        self.clicked_func = clicked
        self.filter_name = widgets.BasicEntry()
        self.filter_id = widgets.BasicEntry()
        self.filter_birth = widgets.DateEntry(uistate, [])
        self.filter_death = widgets.DateEntry(uistate, [])
        self.filter_event = Event()
        self.filter_event.set_type((EventType.CUSTOM, ''))
        self.etype = Gtk.ComboBox(has_entry=True)
        if dbstate.is_open():
            self.custom_types = dbstate.db.get_event_types()
        else:
            self.custom_types = []
        self.event_menu = widgets.MonitoredDataType(
            self.etype,
            self.filter_event.set_type,
            self.filter_event.get_type,
            custom_values=self.custom_types)

        self.filter_note = widgets.BasicEntry()
        self.filter_gender = Gtk.ComboBoxText()
        list(map(self.filter_gender.append_text,
            [ _('any'), _('male'), _('female'), _('unknown') ]))
        self.filter_gender.set_active(0)

        self.filter_regex = Gtk.CheckButton(label=_('Use regular expressions'))

        self.tag = Gtk.ComboBox()
        self.generic = Gtk.ComboBox()

        SidebarFilter.__init__(self, dbstate, uistate, "Person")

    def create_widget(self):
        cell = Gtk.CellRendererText()
        cell.set_property('width', self._FILTER_WIDTH)
        cell.set_property('ellipsize', self._FILTER_ELLIPSIZE)
        self.generic.pack_start(cell, True)
        self.generic.add_attribute(cell, 'text', 0)
        self.on_filters_changed('Person')

        cell = Gtk.CellRendererText()
        cell.set_property('width', self._FILTER_WIDTH)
        cell.set_property('ellipsize', self._FILTER_ELLIPSIZE)
        self.tag.pack_start(cell, True)
        self.tag.add_attribute(cell, 'text', 0)

        self.etype.get_child().set_width_chars(5)

        exdate1 = Date()
        exdate2 = Date()
        exdate1.set(Date.QUAL_NONE, Date.MOD_RANGE,
                    Date.CAL_GREGORIAN, (0, 0, 1800, False,
                                                0, 0, 1900, False))
        exdate2.set(Date.QUAL_NONE, Date.MOD_BEFORE,
                    Date.CAL_GREGORIAN, (0, 0, 1850, False))

        msg1 = displayer.display(exdate1)
        msg2 = displayer.display(exdate2)

        self.add_text_entry(_('Name'), self.filter_name)
        self.add_text_entry(_('ID'), self.filter_id)
        self.add_entry(_('Gender'), self.filter_gender)
        self.add_text_entry(_('Birth date'), self.filter_birth,
                            _('example: "%(msg1)s" or "%(msg2)s"') % {'msg1':msg1, 'msg2':msg2})
        self.add_text_entry(_('Death date'), self.filter_death,
                            _('example: "%(msg1)s" or "%(msg2)s"') % {'msg1':msg1, 'msg2':msg2})
        self.add_entry(_('Event'), self.etype)
        self.add_text_entry(_('Note'), self.filter_note)
        self.add_entry(_('Tag'), self.tag)
        self.add_filter_entry(_('Custom filter'), self.generic)
        self.add_regex_entry(self.filter_regex)

    def clear(self, obj):
        self.filter_name.set_text('')
        self.filter_id.set_text('')
        self.filter_birth.set_text('')
        self.filter_death.set_text('')
        self.filter_note.set_text('')
        self.filter_gender.set_active(0)
        self.etype.get_child().set_text('')
        self.tag.set_active(0)
        self.generic.set_active(0)

    def get_filter(self):
        """
        Extracts the text strings from the sidebar, and uses them to build up
        a new filter.
        """

        # extract text values from the entry widgets
        name = extract_text(self.filter_name)
        gid = extract_text(self.filter_id)
        birth = extract_text(self.filter_birth)
        death = extract_text(self.filter_death)
        note = extract_text(self.filter_note)

        # extract remaining data from the menus
        etype = self.filter_event.get_type().xml_str()
        gender = self.filter_gender.get_active()
        regex = self.filter_regex.get_active()
        tag = self.tag.get_active() > 0
        generic = self.generic.get_active() > 0

        # check to see if the filter is empty. If it is empty, then
        # we don't build a filter

        empty = not (name or gid or birth or death or etype
                     or note or gender or regex or tag or generic)
        if empty:
            generic_filter = None
        else:
            # build a GenericFilter
            generic_filter = GenericFilter()

            # if the name is not empty, choose either the regular expression
            # version or the normal text match
            if name:
                rule = RegExpName([name], use_regex=regex)
                generic_filter.add_rule(rule)

            # if the id is not empty, choose either the regular expression
            # version or the normal text match
            if gid:
                rule = RegExpIdOf([gid], use_regex=regex)
                generic_filter.add_rule(rule)

            # check the gender, and select the right rule based on gender
            if gender > 0:
                if gender == 1:
                    generic_filter.add_rule(IsMale([]))
                elif gender == 2:
                    generic_filter.add_rule(IsFemale([]))
                else:
                    generic_filter.add_rule(HasUnknownGender([]))

            # Build an event filter if needed
            if etype:
                rule = HasEvent([etype, '', '', '', '', '1'], use_regex=regex)
                generic_filter.add_rule(rule)

            # Build birth event filter if needed
            # Arguments for the HasBirth filter are Date, Place, and Description
            # Since the value we extracted to the "birth" variable is the
            # request date, we pass it as the first argument
            if birth:
                rule = HasBirth([birth, '', ''])
                generic_filter.add_rule(rule)

            # Build death event filter if needed
            if death:
                rule = HasDeath([death, '', ''])
                generic_filter.add_rule(rule)

            # Build note filter if needed
            if note:
                rule = HasNoteRegexp([note], use_regex=regex)
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
        if name_space == 'Person':
            all_filter = GenericFilter()
            all_filter.set_name(_("None"))
            all_filter.add_rule(rules.person.Everyone([]))
            self.generic.set_model(build_filter_model('Person', [all_filter]))
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
