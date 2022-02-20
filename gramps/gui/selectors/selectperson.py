#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
#               2009       Gary Burton
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
# internationalization
#
#-------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from ..views.treemodels import PeopleBaseModel, PersonTreeModel
from .baseselector import BaseSelector
from gramps.gen.const import URL_MANUAL_SECT1

PERSON_DATE = '2016-12-01'

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------


#-------------------------------------------------------------------------
#
# SelectPerson
#
#-------------------------------------------------------------------------
class SelectPerson(BaseSelector):
    
    namespace = 'Person'

    def __init__(self, dbstate, uistate, track=[], title=None, filter=None,
                 skip=set(), show_search_bar=False, default=None):

        # SelectPerson may have a title passed to it which should be used
        # instead of the default defined for get_window_title()
        if title is not None:
            self.title = title
        self.WIKI_HELP_PAGE = URL_MANUAL_SECT1
        if title == _("Select Father"):
            self.WIKI_HELP_SEC = _('Select_Father_selector', 'manual')
        elif title == _("Select Mother"):
            self.WIKI_HELP_SEC = _('Select_Mother_selector', 'manual')
        elif title == _("Select Child"):
            self.WIKI_HELP_SEC = _('Select_Child_selector', 'manual')
        else:
            self.WIKI_HELP_SEC = _('Select_Person_selector', 'manual')
        
        history = uistate.get_history(self.namespace).mru

        # see gui.plug._guioptions

        from gramps.gen.filters import GenericFilterFactory, rules

        # Baseselector?
        # Create a filter for the person selector.
        sfilter = GenericFilterFactory(self.namespace)()
        sfilter.set_logical_op('or')
        sfilter.add_rule(rules.person.IsBookmarked([]))

        # Add the database home person if one exists.
        default_person = dbstate.db.get_default_person()
        if default_person:
            gid = default_person.get_gramps_id()
            sfilter.add_rule(rules.person.HasIdOf([gid]))

        # Add the selected person if one exists.
        active_handle = uistate.get_active(self.namespace)
        if active_handle:
            active_person = dbstate.db.get_person_from_handle(active_handle)
            gid = active_person.get_gramps_id()
            sfilter.add_rule(rules.person.HasIdOf([gid]))

        # Add last edited people.
        sfilter.add_rule(rules.person.ChangedSince([PERSON_DATE, ""]))
        
        family_handle = active_person.get_main_parents_family_handle()
        if family_handle:
            family = dbstate.db.get_family_from_handle(family_handle)
            father_handle = family.get_father_handle()
            if father_handle:
                father = dbstate.db.get_person_from_handle(father_handle)
                fid = father.get_gramps_id()
                sfilter.add_rule(rules.person.HasIdOf([fid]))
            mother_handle = family.get_mother_handle()
            if mother_handle:
                mother = dbstate.db.get_person_from_handle(mother_handle)
                mid = mother.get_gramps_id()
                sfilter.add_rule(rules.person.HasIdOf([mid]))
            sib_list = family.get_child_ref_list()
            for sib_ref in sib_list:
                sibling = dbstate.db.get_person_from_handle(sib_ref.ref)
                sbid = sibling.get_gramps_id()
                sfilter.add_rule(rules.person.HasIdOf([sbid]))

        # Add recent people.
        for handle in history:
            recent = dbstate.db.get_person_from_handle(handle)
            gid = recent.get_gramps_id()
            sfilter.add_rule(rules.person.HasIdOf([gid]))

        # Add bookmarked people.
        for handle in dbstate.db.get_bookmarks().get():
            marked = dbstate.db.get_person_from_handle(handle)
            gid = marked.get_gramps_id()
            sfilter.add_rule(rules.person.HasIdOf([gid]))

        if filter is not None and active_handle:
            BaseSelector.__init__(self, dbstate, uistate, track, filter,
                              skip, show_search_bar, active_handle)
        else:
            BaseSelector.__init__(self, dbstate, uistate, track, sfilter,
                              skip, show_search_bar)

    def _local_init(self):
        """
        Perform local initialisation for this class
        """
        self.setup_configs('interface.person-sel', 600, 450)
        self.tree.connect('key-press-event', self._key_press)
        SWITCH = self.switch.get_state() # nothing set yet

    def get_window_title(self):
        return _("Select Person")

    def get_model_class(self):
        return PersonTreeModel

    def get_column_titles(self):
        return [
            (_('Name'),         250, BaseSelector.TEXT,   0),
            (_('ID'),            75, BaseSelector.TEXT,   1),
            (_('Gender'),        75, BaseSelector.TEXT,   2),
            (_('Birth Date'),   150, BaseSelector.MARKUP, 3),
            (_('Birth Place'),  150, BaseSelector.MARKUP, 4),
            (_('Death Date'),   150, BaseSelector.MARKUP, 5),
            (_('Death Place'),  150, BaseSelector.MARKUP, 6),
            (_('Spouse'),       150, BaseSelector.TEXT,   7),
            #(_('Last Change'),  150, BaseSelector.TEXT,   14)
            ]

    def get_from_handle_func(self):
        return self.db.get_person_from_handle

    def exact_search(self):
        """
        Returns a tuple indicating columns requiring an exact search
        """
        return (2,) # Gender ('female' contains the string 'male')

    def _on_row_activated(self, treeview, path, view_col):
        store, paths = self.selection.get_selected_rows()
        if paths and len(paths[0].get_indices()) == 2 :
            self.window.response(Gtk.ResponseType.OK)

    def _key_press(self, obj, event):
        if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            store, paths = self.selection.get_selected_rows()
            if paths and len(paths[0].get_indices()) == 1 :
                if self.tree.row_expanded(paths[0]):
                    self.tree.collapse_row(paths[0])
                else:
                    self.tree.expand_row(paths[0], 0)
                return True
        return False
