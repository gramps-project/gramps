# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
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

"""
Relationship View
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from html import escape
import pickle

#-------------------------------------------------------------------------
#
# Set up logging
#
#-------------------------------------------------------------------------
import logging
_LOG = logging.getLogger("plugin.relview")

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Pango

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
ngettext = glocale.translation.ngettext # else "nearby" comments are ignored
from gramps.gen.lib import (ChildRef, EventRoleType, EventType, Family,
                            FamilyRelType, Name, Person, Surname)
from gramps.gen.lib.date import Today
from gramps.gen.db import DbTxn
from gramps.gui.views.navigationview import NavigationView
from gramps.gui.uimanager import ActionGroup
from gramps.gui.editors import EditPerson, EditFamily
from gramps.gui.editors import FilterEditor
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.utils.file import media_path_full
from gramps.gen.utils.alive import probably_alive
from gramps.gui.utils import open_file_with_default_application
from gramps.gen.datehandler import displayer, get_date
from gramps.gen.utils.thumbnails import get_thumbnail_image
from gramps.gen.config import config
from gramps.gui import widgets
from gramps.gui.widgets.reorderfam import Reorder
from gramps.gui.selectors import SelectorFactory
from gramps.gen.errors import WindowActiveError
from gramps.gui.views.bookmarks import PersonBookmarks
from gramps.gen.const import CUSTOM_FILTERS
from gramps.gen.utils.db import (get_birth_or_fallback, get_death_or_fallback,
                          preset_name)
from gramps.gui.ddtargets import DdTargets
from gramps.gen.utils.symbols import Symbols

_NAME_START = 0
_LABEL_START = 0
_LABEL_STOP = 1
_DATA_START = _LABEL_STOP
_DATA_STOP = _DATA_START+1
_BTN_START = _DATA_STOP
_BTN_STOP = _BTN_START+2
_PLABEL_START = 1
_PLABEL_STOP = _PLABEL_START+1
_PDATA_START = _PLABEL_STOP
_PDATA_STOP = _PDATA_START+2
_PDTLS_START = _PLABEL_STOP
_PDTLS_STOP = _PDTLS_START+2
_CLABEL_START = _PLABEL_START+1
_CLABEL_STOP = _CLABEL_START+1
_CDATA_START = _CLABEL_STOP
_CDATA_STOP = _CDATA_START+1
_CDTLS_START = _CDATA_START
_CDTLS_STOP = _CDTLS_START+1
_ALABEL_START = 0
_ALABEL_STOP = _ALABEL_START+1
_ADATA_START = _ALABEL_STOP
_ADATA_STOP = _ADATA_START+3
_SDATA_START = 2
_SDATA_STOP = 4
_RETURN = Gdk.keyval_from_name("Return")
_KP_ENTER = Gdk.keyval_from_name("KP_Enter")
_SPACE = Gdk.keyval_from_name("space")
_LEFT_BUTTON = 1
_RIGHT_BUTTON = 3

class RelationshipView(NavigationView):
    """
    View showing a textual representation of the relationships of the
    active person
    """
    #settings in the config file
    CONFIGSETTINGS = (
        ('preferences.family-siblings', True),
        ('preferences.family-details', True),
        ('preferences.relation-display-theme', "CLASSIC"),
        ('preferences.relation-shade', True),
        ('preferences.releditbtn', True),
        )

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        NavigationView.__init__(self, _('Relationships'),
                                      pdata, dbstate, uistate,
                                      PersonBookmarks,
                                      nav_group)

        dbstate.connect('database-changed', self.change_db)
        uistate.connect('nameformat-changed', self.build_tree)
        uistate.connect('placeformat-changed', self.build_tree)
        uistate.connect('font-changed', self.font_changed)
        self.redrawing = False

        self.child = None
        self.old_handle = None

        self.reorder_sensitive = False
        self.collapsed_items = {}

        self.additional_uis.append(self.additional_ui)

        self.show_siblings = self._config.get('preferences.family-siblings')
        self.show_details = self._config.get('preferences.family-details')
        self.use_shade = self._config.get('preferences.relation-shade')
        self.theme = self._config.get('preferences.relation-display-theme')
        self.toolbar_visible = config.get('interface.toolbar-on')
        self.age_precision = config.get('preferences.age-display-precision')
        self.symbols = Symbols()
        self.reload_symbols()

    def get_handle_from_gramps_id(self, gid):
        """
        returns the handle of the specified object
        """
        obj = self.dbstate.db.get_person_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        else:
            return None

    def _connect_db_signals(self):
        """
        implement from base class DbGUIElement
        Register the callbacks we need.
        """
        # Add a signal to pick up event changes, bug #1416
        self.callman.add_db_signal('event-update', self.family_update)

        self.callman.add_db_signal('person-update', self.person_update)
        self.callman.add_db_signal('person-rebuild', self.person_rebuild)
        self.callman.add_db_signal('family-update', self.family_update)
        self.callman.add_db_signal('family-add',    self.family_add)
        self.callman.add_db_signal('family-delete', self.family_delete)
        self.callman.add_db_signal('family-rebuild', self.family_rebuild)

        self.callman.add_db_signal('person-delete', self.redraw)

    def reload_symbols(self):
        if self.uistate and self.uistate.symbols:
            gsfs = self.symbols.get_symbol_for_string
            self.male = gsfs(self.symbols.SYMBOL_MALE)
            self.female = gsfs(self.symbols.SYMBOL_FEMALE)
            self.bth = gsfs(self.symbols.SYMBOL_BIRTH)
            self.bptsm = gsfs(self.symbols.SYMBOL_BAPTISM)
            self.marriage = gsfs(self.symbols.SYMBOL_MARRIAGE)
            self.marr = gsfs(self.symbols.SYMBOL_HETEROSEXUAL)
            self.homom = gsfs(self.symbols.SYMBOL_MALE_HOMOSEXUAL)
            self.homof = gsfs(self.symbols.SYMBOL_LESBIAN)
            self.divorce = gsfs(self.symbols.SYMBOL_DIVORCE)
            self.unmarr = gsfs(self.symbols.SYMBOL_UNMARRIED_PARTNERSHIP)
            death_idx = self.uistate.death_symbol
            self.dth = self.symbols.get_death_symbol_for_char(death_idx)
            self.burial = gsfs(self.symbols.SYMBOL_BURIED)
            self.cremation = gsfs(self.symbols.SYMBOL_CREMATED)
        else:
            gsf = self.symbols.get_symbol_fallback
            self.male = gsf(self.symbols.SYMBOL_MALE)
            self.female = gsf(self.symbols.SYMBOL_FEMALE)
            self.bth = gsf(self.symbols.SYMBOL_BIRTH)
            self.bptsm = gsf(self.symbols.SYMBOL_BAPTISM)
            self.marriage = gsf(self.symbols.SYMBOL_MARRIAGE)
            self.marr = gsf(self.symbols.SYMBOL_HETEROSEXUAL)
            self.homom = gsf(self.symbols.SYMBOL_MALE_HOMOSEXUAL)
            self.homof = gsf(self.symbols.SYMBOL_LESBIAN)
            self.divorce = gsf(self.symbols.SYMBOL_DIVORCE)
            self.unmarr = gsf(self.symbols.SYMBOL_UNMARRIED_PARTNERSHIP)
            death_idx = self.symbols.DEATH_SYMBOL_LATIN_CROSS
            self.dth = self.symbols.get_death_symbol_fallback(death_idx)
            self.burial = gsf(self.symbols.SYMBOL_BURIED)
            self.cremation = gsf(self.symbols.SYMBOL_CREMATED)

    def font_changed(self):
        self.reload_symbols()
        self.build_tree()

    def navigation_type(self):
        return 'Person'

    def can_configure(self):
        """
        See :class:`~gui.views.pageview.PageView
        :return: bool
        """
        return True

    def goto_handle(self, handle):
        self.change_person(handle)

    def shade_update(self, client, cnxn_id, entry, data):
        self.use_shade = self._config.get('preferences.relation-shade')
        self.toolbar_visible = config.get('interface.toolbar-on')
        self.uistate.modify_statusbar(self.dbstate)
        self.redraw()

    def config_update(self, client, cnxn_id, entry, data):
        self.show_siblings = self._config.get('preferences.family-siblings')
        self.show_details = self._config.get('preferences.family-details')
        self.redraw()

    def build_tree(self):
        self.redraw()

    def person_update(self, handle_list):
        if self.active:
            person = self.get_active()
            if person:
                while not self.change_person(person):
                    pass
            else:
                self.change_person(None)
        else:
            self.dirty = True

    def person_rebuild(self):
        """Large change to person database"""
        if self.active:
            self.bookmarks.redraw()
            person = self.get_active()
            if person:
                while not self.change_person(person):
                    pass
            else:
                self.change_person(None)
        else:
            self.dirty = True

    def family_update(self, handle_list):
        if self.active:
            person = self.get_active()
            if person:
                while not self.change_person(person):
                    pass
            else:
                self.change_person(None)
        else:
            self.dirty = True

    def family_add(self, handle_list):
        if self.active:
            person = self.get_active()
            if person:
                while not self.change_person(person):
                    pass
            else:
                self.change_person(None)
        else:
            self.dirty = True

    def family_delete(self, handle_list):
        if self.active:
            person = self.get_active()
            if person:
                while not self.change_person(person):
                    pass
            else:
                self.change_person(None)
        else:
            self.dirty = True

    def family_rebuild(self):
        if self.active:
            person = self.get_active()
            if person:
                while not self.change_person(person):
                    pass
            else:
                self.change_person(None)
        else:
            self.dirty = True

    def change_page(self):
        NavigationView.change_page(self)
        self.uistate.clear_filter_results()

    def get_stock(self):
        """
        Return the name of the stock icon to use for the display.
        This assumes that this icon has already been registered with
        GNOME as a stock icon.
        """
        return 'gramps-relation'

    def get_viewtype_stock(self):
        """Type of view in category
        """
        return 'gramps-relation'

    def build_widget(self):
        """
        Build the widget that contains the view, see
        :class:`~gui.views.pageview.PageView
        """
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        container.set_border_width(12)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.vbox.show()

        self.header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.header.show()

        self.child = None

        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.AUTOMATIC,
                               Gtk.PolicyType.AUTOMATIC)
        self.scroll.show()

        vp = Gtk.Viewport()
        vp.set_shadow_type(Gtk.ShadowType.NONE)
        vp.add(self.vbox)

        self.scroll.add(vp)
        self.scroll.show_all()

        container.set_spacing(6)
        container.pack_start(self.header, False, False, 0)
        container.pack_start(Gtk.Separator(), False, False, 0)
        container.pack_start(self.scroll, True, True, 0)
        container.show_all()
        return container

    additional_ui = [  # Defines the UI string for UIManager
        '''
      <placeholder id="CommonGo">
      <section>
        <item>
          <attribute name="action">win.Back</attribute>
          <attribute name="label" translatable="yes">_Add Bookmark</attribute>
        </item>
        <item>
          <attribute name="action">win.Forward</attribute>
          <attribute name="label" translatable="yes">'''
        '''Organize Bookmarks...</attribute>
        </item>
      </section>
      <section>
        <item>
          <attribute name="action">win.HomePerson</attribute>
          <attribute name="label" translatable="yes">_Home</attribute>
        </item>
      </section>
      </placeholder>
''',
        '''
      <placeholder id='otheredit'>
        <item>
          <attribute name="action">win.Edit</attribute>
          <attribute name="label" translatable="yes">Edit...</attribute>
        </item>
        <item>
          <attribute name="action">win.AddParents</attribute>
          <attribute name="label" translatable="yes">'''
        '''Add New Parents...</attribute>
        </item>
        <item>
          <attribute name="action">win.ShareFamily</attribute>
          <attribute name="label" translatable="yes">'''
        '''Add Existing Parents...</attribute>
        </item>
        <item>
          <attribute name="action">win.AddSpouse</attribute>
          <attribute name="label" translatable="yes">Add Partner...</attribute>
        </item>
        <item>
          <attribute name="action">win.ChangeOrder</attribute>
          <attribute name="label" translatable="yes">_Reorder</attribute>
        </item>
        <item>
          <attribute name="action">win.FilterEdit</attribute>
          <attribute name="label" translatable="yes">'''
        '''Person Filter Editor</attribute>
        </item>
      </placeholder>
''',
        '''
      <section id="AddEditBook">
        <item>
          <attribute name="action">win.AddBook</attribute>
          <attribute name="label" translatable="yes">_Add Bookmark</attribute>
        </item>
        <item>
          <attribute name="action">win.EditBook</attribute>
          <attribute name="label" translatable="no">%s...</attribute>
        </item>
      </section>
''' % _('Organize Bookmarks'),  # Following are the Toolbar items
        '''
    <placeholder id='CommonNavigation'>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-previous</property>
        <property name="action-name">win.Back</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Go to the previous object in the history</property>
        <property name="label" translatable="yes">_Back</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-next</property>
        <property name="action-name">win.Forward</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Go to the next object in the history</property>
        <property name="label" translatable="yes">_Forward</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-home</property>
        <property name="action-name">win.HomePerson</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Go to the home person</property>
        <property name="label" translatable="yes">_Home</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
''',
        '''
    <placeholder id='BarCommonEdit'>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">gtk-edit</property>
        <property name="action-name">win.Edit</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Edit the active person</property>
        <property name="label" translatable="yes">Edit...</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-parents-add</property>
        <property name="action-name">win.AddParents</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Add a new set of parents</property>
        <property name="label" translatable="yes">Add</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-parents-open</property>
        <property name="action-name">win.ShareFamily</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Add person as child to an existing family</property>
        <property name="label" translatable="yes">Share</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-spouse</property>
        <property name="action-name">win.AddSpouse</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Add a new family with person as parent</property>
        <property name="label" translatable="yes">Partner</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">view-sort-ascending</property>
        <property name="action-name">win.ChangeOrder</property>
        <property name="tooltip_text" translatable="yes">'''
        '''Change order of parents and families</property>
        <property name="label" translatable="yes">_Reorder</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
     ''']

    def define_actions(self):
        NavigationView.define_actions(self)

        self.order_action = ActionGroup(name=self.title + '/ChangeOrder')
        self.order_action.add_actions([
            ('ChangeOrder', self.reorder)])

        self.family_action = ActionGroup(name=self.title + '/Family')
        self.family_action.add_actions([
            ('Edit', self.edit_active, "<PRIMARY>Return"),
            ('AddSpouse', self.add_spouse),
            ('AddParents', self.add_parents),
            ('ShareFamily', self.select_parents)])

        self._add_action('FilterEdit', callback=self.filter_editor)
        self._add_action('PRIMARY-J', self.jump, '<PRIMARY>J')

        self._add_action_group(self.order_action)
        self._add_action_group(self.family_action)

        self.uimanager.set_actions_sensitive(self.order_action,
                                             self.reorder_sensitive)
        self.uimanager.set_actions_sensitive(self.family_action, False)

    def filter_editor(self, *obj):
        try:
            FilterEditor('Person', CUSTOM_FILTERS,
                         self.dbstate, self.uistate)
        except WindowActiveError:
            return

    def change_db(self, db):
        #reset the connects
        self._change_db(db)
        if self.child:
            list(map(self.vbox.remove, self.vbox.get_children()))
            list(map(self.header.remove, self.header.get_children()))
            self.child = None
        if self.active:
                self.bookmarks.redraw()
        self.redraw()

    def get_name(self, handle, use_gender=False):
        if handle:
            person = self.dbstate.db.get_person_from_handle(handle)
            name = name_displayer.display(person)
            if use_gender:
                gender = self.symbols.get_symbol_for_string(person.gender)
            else:
                gender = ""
            return (name, gender)
        else:
            return (_("Unknown"), "")

    def redraw(self, *obj):
        active_person = self.get_active()
        if active_person:
            self.change_person(active_person)
        else:
            self.change_person(None)

    def change_person(self, obj):
        self.change_active(obj)
        try:
            return self._change_person(obj)
        except AttributeError as msg:
            import traceback
            exc = traceback.format_exc()
            _LOG.error(str(msg) +"\n" + exc)
            from gramps.gui.dialog import RunDatabaseRepair
            RunDatabaseRepair(str(msg),
                              parent=self.uistate.window)
            self.redrawing = False
            return True

    def _change_person(self, obj):
        if obj == self.old_handle:
            #same object, keep present scroll position
            old_vadjust = self.scroll.get_vadjustment().get_value()
            self.old_handle = obj
        else:
            #different object, scroll to top
            old_vadjust = self.scroll.get_vadjustment().get_lower()
            self.old_handle = obj
        self.scroll.get_vadjustment().set_value(
                            self.scroll.get_vadjustment().get_lower())
        if self.redrawing:
            return False
        self.redrawing = True

        for old_child in self.vbox.get_children():
            self.vbox.remove(old_child)
        for old_child in self.header.get_children():
            self.header.remove(old_child)

        person = None
        if obj:
            person = self.dbstate.db.get_person_from_handle(obj)
        if not person:
            self.uimanager.set_actions_sensitive(self.family_action, False)
            self.uimanager.set_actions_sensitive(self.order_action, False)
            self.redrawing = False
            return
        self.uimanager.set_actions_sensitive(self.family_action, True)

        self.write_title(person)

        self.child = Gtk.Grid()
        self.child.set_border_width(12)
        self.child.set_column_spacing(12)
        self.child.set_row_spacing(0)
        self.row = 0

        family_handle_list = person.get_parent_family_handle_list()

        self.reorder_sensitive = len(family_handle_list)> 1

        if family_handle_list:
            for family_handle in family_handle_list:
                if family_handle:
                    self.write_parents(family_handle, person)
        else:
            self.write_label(_("%s:") % _('Parents'), None, True, person)
            self.row += 1

        family_handle_list = person.get_family_handle_list()

        if not self.reorder_sensitive:
            self.reorder_sensitive = len(family_handle_list)> 1

        if family_handle_list:
            for family_handle in family_handle_list:
                if family_handle:
                    self.write_family(family_handle, person)

        self.child.show_all()

        self.vbox.pack_start(self.child, False, True, 0)
        #reset scroll position as it was before
        self.scroll.get_vadjustment().set_value(old_vadjust)
        self.redrawing = False
        self.uistate.modify_statusbar(self.dbstate)

        self.uimanager.set_actions_sensitive(self.order_action,
                                             self.reorder_sensitive)
        self.dirty = False

        return True

    def write_title(self, person):

        list(map(self.header.remove, self.header.get_children()))
        grid = Gtk.Grid()
        grid.set_column_spacing(12)
        grid.set_row_spacing(0)

        # name and edit button
        name = name_displayer.display(person)
        fmt = '<span size="larger" weight="bold">%s</span>'
        text = fmt % escape(name)
        gender_code = self.symbols.get_symbol_for_string(person.gender)
        label = widgets.DualMarkupLabel(text, gender_code,
                                        halign=Gtk.Align.END)
        if self._config.get('preferences.releditbtn'):
            button = widgets.IconButton(self.edit_button_press,
                                        person.handle)
            button.set_tooltip_text(_('Edit Person (%s)') % name)
        else:
            button = None
        eventbox = Gtk.EventBox()
        eventbox.set_visible_window(False)
        self._set_draggable_person(eventbox, person.get_handle())
        hbox = widgets.LinkBox(label, button)
        eventbox.add(hbox)

        grid.attach(eventbox, 0, 0, 2, 1)

        eventbox = widgets.ShadeBox(self.use_shade)
        grid.attach(eventbox, 1, 1, 1, 1)
        subgrid = Gtk.Grid()
        subgrid.set_column_spacing(12)
        subgrid.set_row_spacing(0)
        eventbox.add(subgrid)
        self._set_draggable_person(eventbox, person.get_handle())
        # Gramps ID

        subgrid.attach(widgets.BasicLabel(_("%s:") % _('ID')), 1, 0, 1, 1)
        label = widgets.BasicLabel(person.gramps_id)
        label.set_hexpand(True)
        subgrid.attach(label, 2, 0, 1, 1)

        # Birth event.
        birth = get_birth_or_fallback(self.dbstate.db, person)
        if birth:
            if birth.get_type() == EventType.BAPTISM:
                birth_title = self.bptsm
            else:
                birth_title = self.bth
        else:
            birth_title = self.bth

        subgrid.attach(widgets.BasicLabel(_("%s") % birth_title), 1, 1, 1, 1)
        birthwidget = widgets.BasicLabel(self.format_event(birth))
        birthwidget.set_selectable(True)
        subgrid.attach(birthwidget, 2, 1, 1, 1)

        death = get_death_or_fallback(self.dbstate.db, person)
        if death:
            if death.get_type() == EventType.BURIAL:
                death_title = self.burial
            elif death.get_type() == EventType.CREMATION:
                death_title = self.cremation
            else:
                death_title = self.dth
        else:
            death_title = self.dth

        showed_death = False
        if birth:
            birth_date = birth.get_date_object()
            if (birth_date and birth_date.get_valid()):
                if death:
                    death_date = death.get_date_object()
                    if (death_date and death_date.get_valid()):
                        age = (death_date - birth_date).format(
                            precision=self.age_precision)
                        subgrid.attach(widgets.BasicLabel(
                            _("%s") % death_title), 1, 2, 1, 1)
                        deathwidget = widgets.BasicLabel(
                            "%s (%s)" % (self.format_event(death), age),
                            Pango.EllipsizeMode.END)
                        deathwidget.set_selectable(True)
                        subgrid.attach(deathwidget, 2, 2, 1, 1)
                        showed_death = True
                if not showed_death:
                    age = (Today() - birth_date).format(
                        precision=self.age_precision)
                    if probably_alive(person, self.dbstate.db):
                        subgrid.attach(widgets.BasicLabel(
                            _("%s:") % _("Alive")), 1, 2, 1, 1)
                        subgrid.attach(widgets.BasicLabel(
                            "(%s)" % age, Pango.EllipsizeMode.END), 2, 2, 1, 1)
                    else:
                        subgrid.attach(widgets.BasicLabel(
                            _("%s") % self.dth), 1, 2, 1, 1)
                        subgrid.attach(widgets.BasicLabel(
                            "%s (%s)" % (_("unknown"), age),
                            Pango.EllipsizeMode.END), 2, 2, 1, 1)
                    showed_death = True

        if not showed_death:
            subgrid.attach(widgets.BasicLabel(_("%s") % death_title),
                          1, 2, 1, 1)
            deathwidget = widgets.BasicLabel(self.format_event(death))
            deathwidget.set_selectable(True)
            subgrid.attach(deathwidget,
                          2, 2, 1, 1)

        mbox = Gtk.Box()
        mbox.add(grid)

        # image
        image_list = person.get_media_list()
        if image_list:
            mobj = self.dbstate.db.get_media_from_handle(image_list[0].ref)
            if mobj and mobj.get_mime_type()[0:5] == "image":
                pixbuf = get_thumbnail_image(
                                media_path_full(self.dbstate.db,
                                                mobj.get_path()),
                                rectangle=image_list[0].get_rectangle())
                image = Gtk.Image()
                image.set_from_pixbuf(pixbuf)
                button = Gtk.Button()
                button.add(image)
                button.connect("clicked", lambda obj: self.view_photo(mobj))
                mbox.pack_end(button, False, True, 0)

        mbox.show_all()
        self.header.pack_start(mbox, False, True, 0)

    def view_photo(self, photo):
        """
        Open this picture in the default picture viewer.
        """
        photo_path = media_path_full(self.dbstate.db, photo.get_path())
        open_file_with_default_application(photo_path, self.uistate)

    def write_person_event(self, ename, event):
        if event:
            dobj = event.get_date_object()
            phandle = event.get_place_handle()
            if phandle:
                pname = place_displayer.display_event(self.dbstate.db, event)
            else:
                pname = None

            value = {
                'date' : displayer.display(dobj),
                'place' : pname,
                }
        else:
            pname = None
            dobj = None

        if dobj:
            if pname:
                self.write_person_data(ename,
                                       _('%(date)s in %(place)s') % value)
            else:
                self.write_person_data(ename, '%(date)s' % value)
        elif pname:
            self.write_person_data(ename, pname)
        else:
            self.write_person_data(ename, '')

    def format_event(self, event):
        if event:
            dobj = event.get_date_object()
            phandle = event.get_place_handle()
            if phandle:
                pname = place_displayer.display_event(self.dbstate.db, event)
            else:
                pname = None

            value = {
                'date' : displayer.display(dobj),
                'place' : pname,
                }
        else:
            pname = None
            dobj = None

        if dobj:
            if pname:
                return _('%(date)s in %(place)s') % value
            else:
                return '%(date)s' % value
        elif pname:
            return pname
        else:
            return ''

    def write_person_data(self, title, data):
        self.child.attach(widgets.BasicLabel(title), _ALABEL_START, self.row,
                          _ALABEL_STOP-_ALABEL_START, 1)
        self.child.attach(widgets.BasicLabel(data), _ADATA_START, self.row,
                          _ADATA_STOP-_ADATA_START, 1)
        self.row += 1

    def marriage_symbol(self, family, markup=True):
        if family:
            father = mother = None
            hdl1 = family.get_father_handle()
            if hdl1:
                father = self.dbstate.db.get_person_from_handle(hdl1).gender
            hdl2 = family.get_mother_handle()
            if hdl2:
                mother = self.dbstate.db.get_person_from_handle(hdl2).gender
            if father != mother:
                symbol = self.marr
            elif father == Person.MALE:
                symbol = self.homom
            else:
                symbol = self.homof
            if markup:
                msg = '<span size="12000" >%s</span>' % symbol
            else:
                msg = symbol
        else:
            msg = ""
        return msg

    def write_label(self, title, family, is_parent, person = None):
        """
        Write a Family header row
        Shows following elements:
        (collapse/expand arrow, Parents/Family title label, Family gramps_id, and add-choose-edit-delete buttons)
        """
        msg = '<span style="italic" weight="heavy">%s</span>' % escape(title)
        hbox = Gtk.Box()
        label = widgets.MarkupLabel(msg, halign=Gtk.Align.END)
        # Draw the collapse/expand button:
        if family is not None:
            if self.check_collapsed(person.handle, family.handle):
                arrow = widgets.ExpandCollapseArrow(True,
                                                    self.expand_collapse_press,
                                                    (person, family.handle))
            else:
                arrow = widgets.ExpandCollapseArrow(False,
                                                    self.expand_collapse_press,
                                                    (person, family.handle))
        else :
            arrow = Gtk.Arrow(arrow_type=Gtk.ArrowType.RIGHT,
                                        shadow_type=Gtk.ShadowType.OUT)
        hbox.pack_start(arrow, False, True, 0)
        hbox.pack_start(label, True, True, 0)
        # Allow to drag this family
        eventbox = Gtk.EventBox()
        if family is not None:
            self._set_draggable_family(eventbox, family.handle)
        eventbox.add(hbox)
        self.child.attach(eventbox, _LABEL_START, self.row,
                          _LABEL_STOP-_LABEL_START, 1)

        if family:
            value = family.gramps_id
        else:
            value = ""
        eventbox = Gtk.EventBox()
        if family is not None:
            self._set_draggable_family(eventbox, family.handle)
        eventbox.add(widgets.BasicLabel(value))
        self.child.attach(eventbox, _DATA_START, self.row,
                          _DATA_STOP-_DATA_START, 1)

        if family and self.check_collapsed(person.handle, family.handle):
            # show family names later
            pass
        else:
            hbox = Gtk.Box()
            hbox.set_spacing(12)
            hbox.set_hexpand(True)
            if self.uistate and self.uistate.symbols:
                msg = self.marriage_symbol(family)
                marriage = widgets.MarkupLabel(msg)
                hbox.pack_start(marriage, False, True, 0)
            if is_parent:
                call_fcn = self.add_parent_family
                del_fcn = self.delete_parent_family
                add_msg = _('Add a new set of parents')
                sel_msg = _('Add person as child to an existing family')
                edit_msg = _('Edit parents')
                ord_msg = _('Reorder parents')
                del_msg = _('Remove person as child of these parents')
            else:
                add_msg = _('Add a new family with person as parent')
                sel_msg = None
                edit_msg = _('Edit family')
                ord_msg = _('Reorder families')
                del_msg = _('Remove person as parent in this family')
                call_fcn = self.add_family
                del_fcn = self.delete_family

            if not self.dbstate.db.readonly:
                # Show edit-Buttons only if db is not readonly
                if self.reorder_sensitive:
                    add = widgets.IconButton(self.reorder_button_press, None,
                                             'view-sort-ascending')
                    add.set_tooltip_text(ord_msg)
                    hbox.pack_start(add, False, True, 0)

                add = widgets.IconButton(call_fcn, None, 'list-add')
                add.set_tooltip_text(add_msg)
                hbox.pack_start(add, False, True, 0)

                if is_parent:
                    add = widgets.IconButton(self.select_family, None,
                                             'gtk-index')
                    add.set_tooltip_text(sel_msg)
                    hbox.pack_start(add, False, True, 0)

            if family:
                edit = widgets.IconButton(self.edit_family, family.handle,
                                          'gtk-edit')
                edit.set_tooltip_text(edit_msg)
                hbox.pack_start(edit, False, True, 0)
                if not self.dbstate.db.readonly:
                    delete = widgets.IconButton(del_fcn, family.handle,
                                                'list-remove')
                    delete.set_tooltip_text(del_msg)
                    hbox.pack_start(delete, False, True, 0)

            eventbox = Gtk.EventBox()
            if family is not None:
                self._set_draggable_family(eventbox, family.handle)
            eventbox.add(hbox)
            self.child.attach(eventbox, _BTN_START, self.row,
                              _BTN_STOP-_BTN_START, 1)
        self.row += 1

######################################################################

    def write_parents(self, family_handle, person = None):
        family = self.dbstate.db.get_family_from_handle(family_handle)
        if not family:
            return
        if person and self.check_collapsed(person.handle, family_handle):
            # don't show rest
            self.write_label(_("%s:") % _('Parents'), family, True, person)
            self.row -= 1 # back up one row for summary names
            active = self.get_active()
            child_list = [ref.ref for ref in family.get_child_ref_list()
                          if ref.ref != active]
            if child_list:
                count = len(child_list)
            else:
                count = 0
            if count > 1 :
                # translators: leave all/any {...} untranslated
                childmsg = ngettext(" ({number_of} sibling)",
                                    " ({number_of} siblings)", count
                                   ).format(number_of=count)
            elif count == 1 :
                gender = self.dbstate.db.get_person_from_handle(
                                        child_list[0]).gender
                if gender == Person.MALE :
                    childmsg = _(" (1 brother)")
                elif gender == Person.FEMALE :
                    childmsg = _(" (1 sister)")
                else :
                    childmsg = _(" (1 sibling)")
            else :
                childmsg = _(" (only child)")
            self.family = family
            box = self.get_people_box(family.get_father_handle(),
                                      family.get_mother_handle(),
                                      post_msg=childmsg)
            eventbox = widgets.ShadeBox(self.use_shade)
            eventbox.add(box)
            self.child.attach(eventbox, _PDATA_START, self.row,
                               _PDATA_STOP-_PDATA_START, 1)
            self.row += 1 # now advance it
        else:
            self.write_label(_("%s:") % _('Parents'), family, True, person)
            self.write_person(_('Father'), family.get_father_handle())
            self.write_person(_('Mother'), family.get_mother_handle())

            if self.show_siblings:
                active = self.get_active()
                hbox = Gtk.Box()
                if self.check_collapsed(person.handle, "SIBLINGS"):
                    arrow = widgets.ExpandCollapseArrow(True,
                                                        self.expand_collapse_press,
                                                        (person, "SIBLINGS"))
                else:
                    arrow = widgets.ExpandCollapseArrow(False,
                                                        self.expand_collapse_press,
                                                        (person, "SIBLINGS"))
                hbox.pack_start(arrow, False, True, 0)
                label_cell = self.build_label_cell(_('Siblings'))
                hbox.pack_start(label_cell, True, True, 0)
                self.child.attach(hbox, _CLABEL_START-1, self.row,
                                  _CLABEL_STOP-_CLABEL_START, 1)

                if self.check_collapsed(person.handle, "SIBLINGS"):
                    hbox = Gtk.Box()
                    child_list = [ref.ref for ref in family.get_child_ref_list()
                                  if ref.ref != active]
                    if child_list:
                        count = len(child_list)
                    else:
                        count = 0
                    if count > 1 :
                        # translators: leave all/any {...} untranslated
                        childmsg = ngettext(" ({number_of} sibling)",
                                            " ({number_of} siblings)", count
                                           ).format(number_of=count)
                    elif count == 1 :
                        gender = self.dbstate.db.get_person_from_handle(
                                                child_list[0]).gender
                        if gender == Person.MALE :
                            childmsg = _(" (1 brother)")
                        elif gender == Person.FEMALE :
                            childmsg = _(" (1 sister)")
                        else :
                            childmsg = _(" (1 sibling)")
                    else :
                        childmsg = _(" (only child)")
                    self.family = None
                    box = self.get_people_box(post_msg=childmsg)
                    eventbox = widgets.ShadeBox(self.use_shade)
                    eventbox.add(box)
                    self.child.attach(eventbox, _PDATA_START, self.row,
                                      _PDATA_STOP-_PDATA_START, 1)
                    self.row += 1 # now advance it
                else:
                    hbox = Gtk.Box()
                    addchild = widgets.IconButton(self.add_child_to_fam,
                                                  family.handle,
                                                  'list-add')
                    addchild.set_tooltip_text(_('Add new child to family'))
                    selchild = widgets.IconButton(self.sel_child_to_fam,
                                                  family.handle,
                                                  'gtk-index')
                    selchild.set_tooltip_text(_('Add existing child to family'))
                    hbox.pack_start(addchild, False, True, 0)
                    hbox.pack_start(selchild, False, True, 0)

                    self.child.attach(hbox, _CLABEL_START, self.row,
                                      _CLABEL_STOP-_CLABEL_START, 1)
                    self.row += 1
                    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                    i = 1
                    child_list = [ref.ref for ref in family.get_child_ref_list()]
                    for child_handle in child_list:
                        child_should_be_linked = (child_handle != active)
                        self.write_child(vbox, child_handle, i, child_should_be_linked)
                        i += 1
                    eventbox = widgets.ShadeBox(self.use_shade)
                    eventbox.add(vbox)
                    self.child.attach(eventbox, _CDATA_START-1, self.row,
                                      _CDATA_STOP-_CDATA_START+1, 1)

            self.row += 1

    def get_people_box(self, *handles, **kwargs):
        hbox = Gtk.Box()
        initial_name = True
        if self.uistate and self.uistate.symbols:
            msg = self.marriage_symbol(self.family) + " "
            marriage = widgets.MarkupLabel(msg)
            hbox.pack_start(marriage, False, True, 0)
        for handle in handles:
            if not initial_name:
                link_label = Gtk.Label(label=" %s " % _('and'))
                link_label.show()
                hbox.pack_start(link_label, False, True, 0)
            initial_name = False
            if handle:
                name = self.get_name(handle, True)
                link_label = widgets.LinkLabel(name, self._button_press,
                                               handle, theme=self.theme)
                if self._config.get('preferences.releditbtn'):
                    button = widgets.IconButton(self.edit_button_press,
                                                handle)
                    button.set_tooltip_text(_('Edit Person (%s)') % name[0])
                else:
                    button = None
                hbox.pack_start(widgets.LinkBox(link_label, button),
                                False, True, 0)
            else:
                link_label = Gtk.Label(label=_('Unknown'))
                link_label.show()
                hbox.pack_start(link_label, False, True, 0)
        if "post_msg" in kwargs and kwargs["post_msg"]:
            link_label = Gtk.Label(label=kwargs["post_msg"])
            link_label.show()
            hbox.pack_start(link_label, False, True, 0)
        return hbox

    def write_person(self, title, handle):
        """
        Create and show a person cell with a "Father/Mother/Spouse" label in the GUI at the current row
        @param title: left column label ("Father/Mother/Spouse")
        @param handle: person handle
        """
        if title:
            format = '<span weight="bold">%s: </span>'
        else:
            format = "%s"

        label = widgets.MarkupLabel(format % escape(title),
                                    halign=Gtk.Align.END)
        if self._config.get('preferences.releditbtn'):
            label.set_margin_end(5)

        eventbox = Gtk.EventBox()
        if handle is not None:
            self._set_draggable_person(eventbox, handle)
        eventbox.add(label)
        self.child.attach(eventbox, _PLABEL_START, self.row,
                          _PLABEL_STOP-_PLABEL_START, 1)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        eventbox = widgets.ShadeBox(self.use_shade)
        if handle:
            name = self.get_name(handle, True)
            person = self.dbstate.db.get_person_from_handle(handle)
            parent = len(person.get_parent_family_handle_list()) > 0
            format = ''
            relation_display_theme = self._config.get(
                                    'preferences.relation-display-theme')
            if parent:
                emph = True
            else:
                emph = False
            link_label = widgets.LinkLabel(name, self._button_press,
                                           handle, emph, theme=self.theme)
            if self._config.get('preferences.releditbtn'):
                button = widgets.IconButton(self.edit_button_press, handle)
                button.set_tooltip_text(_('Edit Person (%s)') % name[0])
            else:
                button = None
            vbox.pack_start(widgets.LinkBox(link_label, button), True, True, 0)
            self._set_draggable_person(eventbox, handle)
        else:
            link_label = Gtk.Label(label=_('Unknown'))
            link_label.set_halign(Gtk.Align.START)
            link_label.show()
            vbox.pack_start(link_label, True, True, 0)

        if self.show_details and handle:
            value = self.info_string(handle)
            if value:
                vbox.pack_start(widgets.MarkupLabel(value), True, True, 0)

        eventbox.add(vbox)

        self.child.attach(eventbox, _PDATA_START, self.row,
                          _PDATA_STOP-_PDATA_START, 1)
        self.row += 1
        return vbox

    def _set_draggable_person(self, eventbox, person_handle):
        """
        Register the given eventbox as a drag_source with given person_handle
        """
        self._set_draggable(eventbox, person_handle, DdTargets.PERSON_LINK, 'gramps-person')

    def _set_draggable_family(self, eventbox, family_handle):
        """
        Register the given eventbox as a drag_source with given person_handle
        """
        self._set_draggable(eventbox, family_handle, DdTargets.FAMILY_LINK, 'gramps-family')

    def _set_draggable(self, eventbox, object_h, dnd_type, stock_icon):
        """
        Register the given eventbox as a drag_source with given object_h
        """
        eventbox.drag_source_set(Gdk.ModifierType.BUTTON1_MASK,
                                 [dnd_type.target()], Gdk.DragAction.COPY)
        eventbox.drag_source_set_icon_name(stock_icon)
        eventbox.connect('drag_data_get',
                         self._make_drag_data_get_func(object_h, dnd_type))

    def _make_drag_data_get_func(self, object_h, dnd_type):
        """
        Generate at runtime a drag_data_get function returning the given dnd_type and object_h
        """
        def drag_data_get(widget, context, sel_data, info, time):
            if info == dnd_type.app_id:
                data = (dnd_type.drag_type, id(self), object_h, 0)
                sel_data.set(dnd_type.atom_drag_type, 8, pickle.dumps(data))
        return drag_data_get

    def build_label_cell(self, title):
        if title:
            format = '<span weight="bold">%s: </span>'
        else:
            format = "%s"

        lbl = widgets.MarkupLabel(format % escape(title),
                                  halign=Gtk.Align.END)
        if self._config.get('preferences.releditbtn'):
            lbl.set_margin_end(5)
        return lbl

    def write_child(self, vbox, handle, index, child_should_be_linked):
        """
        Write a child cell (used for children and siblings of active person)
        """
        original_vbox = vbox
        # Always create a transparent eventbox to allow dnd drag
        ev = Gtk.EventBox()
        ev.set_visible_window(False)
        if handle:
            self._set_draggable_person(ev, handle)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        ev.add(vbox)

        if not child_should_be_linked:
            frame = Gtk.Frame()
            frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
            frame.add(ev)
            original_vbox.pack_start(frame, True, True, 0)
        else:
            original_vbox.pack_start(ev, True, True, 0)

        parent = has_children(self.dbstate.db,
                              self.dbstate.db.get_person_from_handle(handle))

        format = ''
        relation_display_theme = self._config.get(
                                        'preferences.relation-display-theme')
        emph = False
        if child_should_be_linked and parent:
            emph = True
        elif child_should_be_linked and not parent:
            emph = False
        elif parent and not child_should_be_linked:
            emph = None

        if child_should_be_linked:
            link_func = self._button_press
        else:
            link_func = None

        name = self.get_name(handle, True)
        link_label = widgets.LinkLabel(name, link_func, handle, emph,
                                       theme=self.theme)
        link_label.set_padding(3, 0)

        if child_should_be_linked and self._config.get(
            'preferences.releditbtn'):
            button = widgets.IconButton(self.edit_button_press, handle)
            button.set_tooltip_text(_('Edit Person (%s)') % name[0])
        else:
            button = None

        hbox = Gtk.Box()
        l = widgets.BasicLabel("%d." % index)
        l.set_width_chars(3)
        l.set_halign(Gtk.Align.END)
        hbox.pack_start(l, False, False, 0)
        hbox.pack_start(widgets.LinkBox(link_label, button),
                        False, False, 4)
        hbox.show()
        vbox.pack_start(hbox, True, True, 0)

        if self.show_details:
            value = self.info_string(handle)
            if value:
                l = widgets.MarkupLabel(value)
                l.set_margin_start(48)
                vbox.add(l)

    def write_data(self, box, title, start_col=_SDATA_START,
                   stop_col=_SDATA_STOP, selectable=False):
        label=widgets.BasicLabel(title)
        label.set_selectable(selectable)
        box.add(label)

    def info_string(self, handle):
        person = self.dbstate.db.get_person_from_handle(handle)
        if not person:
            return None

        birth = get_birth_or_fallback(self.dbstate.db, person)
        if birth:
            if birth.get_type() == EventType.BAPTISM:
                s_birth = self.bptsm
            else:
                s_birth = self.bth
        if birth and birth.get_type() != EventType.BIRTH:
            sdate = get_date(birth)
            if sdate:
                bdate = "<i>%s</i>" % escape(sdate)
            else:
                bdate = ""
        elif birth:
            bdate = escape(get_date(birth))
        else:
            bdate = ""

        death = get_death_or_fallback(self.dbstate.db, person)
        if death:
            if death.get_type() == EventType.BURIAL:
                s_death = self.burial
            elif death.get_type() == EventType.CREMATION:
                s_death = self.cremation
            else:
                s_death = self.dth
        if death and death.get_type() != EventType.DEATH:
            sdate = get_date(death)
            if sdate:
                ddate = "<i>%s</i>" % escape(sdate)
            else:
                ddate = ""
        elif death:
            ddate = escape(get_date(death))
        else:
            ddate = ""

        if bdate and ddate:
            value = _("%(birthabbrev)s %(birthdate)s, %(deathabbrev)s %(deathdate)s") % {
                'birthabbrev': s_birth,
                'deathabbrev': s_death,
                'birthdate' : bdate,
                'deathdate' : ddate
                }
        elif bdate:
            value = _("%(event)s %(date)s") % {'event': s_birth, 'date': bdate}
        elif ddate:
            value = _("%(event)s %(date)s") % {'event': s_death, 'date': ddate}
        else:
            value = ""
        return value

    def check_collapsed(self, person_handle, handle):
        """ Return true if collapsed. """
        return (handle in self.collapsed_items.get(person_handle, []))

    def expand_collapse_press(self, obj, event, pair):
        """ Calback function for ExpandCollapseArrow, user param is
            pair, which is a tuple (object, handle) which handles the
            section of which the collapse state must change, so a
            parent, siblings id, family id, family children id, etc.
            NOTE: object must be a thing that has a handle field.
        """
        if button_activated(event, _LEFT_BUTTON):
            object, handle = pair
            if object.handle in self.collapsed_items:
                if handle in self.collapsed_items[object.handle]:
                    self.collapsed_items[object.handle].remove(handle)
                else:
                    self.collapsed_items[object.handle].append(handle)
            else:
                self.collapsed_items[object.handle] = [handle]
            self.redraw()

    def _button_press(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            self.change_active(handle)
        elif button_activated(event, _RIGHT_BUTTON):
            self.my_menu = Gtk.Menu()
            self.my_menu.set_reserve_toggle_size(False)
            self.my_menu.append(self.build_menu_item(handle))
            self.my_menu.popup(None, None, None, None, event.button, event.time)

    def build_menu_item(self, handle):
        person = self.dbstate.db.get_person_from_handle(handle)
        name = name_displayer.display(person)

        item = Gtk.MenuItem()
        label = Gtk.Label(label=_("Edit Person (%s)") % name)
        label.show()
        label.set_halign(Gtk.Align.START)

        item.add(label)

        item.connect('activate', self.edit_menu, handle)
        item.show()
        return item

    def edit_menu(self, obj, handle):
        person = self.dbstate.db.get_person_from_handle(handle)
        try:
            EditPerson(self.dbstate, self.uistate, [], person)
        except WindowActiveError:
            pass

    def write_relationship(self, box, family):
        msg = _('Relationship type: %s') % escape(str(family.get_relationship()))
        box.add(widgets.MarkupLabel(msg))

    def write_relationship_events(self, vbox, family):
        value = False
        for event_ref in family.get_event_ref_list():
            handle = event_ref.ref
            event = self.dbstate.db.get_event_from_handle(handle)
            if (event and event.get_type().is_relationship_event() and
                (event_ref.get_role() == EventRoleType.FAMILY or
                 event_ref.get_role() == EventRoleType.PRIMARY)):
                if event.get_type() ==  EventType.MARRIAGE:
                    etype = self.marriage
                elif event.get_type() ==  EventType.DIVORCE:
                    etype = self.divorce
                else:
                    etype = event.get_type().string
                self.write_event_ref(vbox, etype, event)
                value = True
        return value

    def write_event_ref(self, vbox, ename, event, start_col=_SDATA_START,
                        stop_col=_SDATA_STOP):
        if event:
            dobj = event.get_date_object()
            phandle = event.get_place_handle()
            if phandle:
                pname = place_displayer.display_event(self.dbstate.db, event)
            else:
                pname = None

            value = {
                'date' : displayer.display(dobj),
                'place' : pname,
                'event_type' : ename,
                }
        else:
            pname = None
            dobj = None
            value = { 'event_type' : ename, }

        if dobj:
            if pname:
                self.write_data(
                    vbox, _('%(event_type)s %(date)s in %(place)s') %
                    value, start_col, stop_col, True)
            else:
                self.write_data(
                    vbox, _('%(event_type)s %(date)s') % value,
                    start_col, stop_col)
        elif pname:
            self.write_data(
                vbox, _('%(event_type)s %(place)s') % value,
                start_col, stop_col)
        else:
            self.write_data(
                vbox, '%(event_type)s' % value, start_col, stop_col)

    def write_family(self, family_handle, person = None):
        family = self.dbstate.db.get_family_from_handle(family_handle)
        if family is None:
            from gramps.gui.dialog import WarningDialog
            WarningDialog(
                _('Broken family detected'),
                _('Please run the Check and Repair Database tool'),
                parent=self.uistate.window)
            return

        father_handle = family.get_father_handle()
        mother_handle = family.get_mother_handle()
        if self.get_active() == father_handle:
            handle = mother_handle
        else:
            handle = father_handle

        # collapse button
        if self.check_collapsed(person.handle, family_handle):
            # show "> Family: ..." and nothing else
            self.write_label(_("%s:") % _('Family'), family, False, person)
            self.row -= 1 # back up
            child_list = family.get_child_ref_list()
            if child_list:
                count = len(child_list)
            else:
                count = 0
            if count >= 1 :
                # translators: leave all/any {...} untranslated
                childmsg = ngettext(" ({number_of} child)",
                                    " ({number_of} children)", count
                                   ).format(number_of=count)
            else :
                childmsg = _(" (no children)")
            self.family = family
            box = self.get_people_box(handle, post_msg=childmsg)
            eventbox = widgets.ShadeBox(self.use_shade)
            eventbox.add(box)
            self.child.attach(eventbox, _PDATA_START, self.row,
                              _PDATA_STOP-_PDATA_START, 1)
            self.row += 1 # now advance it
        else:
            # show "V Family: ..." and the rest
            self.write_label(_("%s:") % _('Family'), family, False, person)
            if (handle or
                    family.get_relationship() != FamilyRelType.UNKNOWN):
                box = self.write_person(_('Spouse'), handle)

                if not self.write_relationship_events(box, family):
                    self.write_relationship(box, family)

            hbox = Gtk.Box()
            if self.check_collapsed(family.handle, "CHILDREN"):
                arrow = widgets.ExpandCollapseArrow(True,
                                                    self.expand_collapse_press,
                                                    (family, "CHILDREN"))
            else:
                arrow = widgets.ExpandCollapseArrow(False,
                                                    self.expand_collapse_press,
                                                    (family, "CHILDREN"))
            hbox.pack_start(arrow, False, True, 0)
            label_cell = self.build_label_cell(_('Children'))
            hbox.pack_start(label_cell, True, True, 0)
            self.child.attach(hbox, _CLABEL_START-1, self.row,
                              _CLABEL_STOP-_CLABEL_START, 1)

            if self.check_collapsed(family.handle, "CHILDREN"):
                hbox = Gtk.Box()
                child_list = family.get_child_ref_list()
                if child_list:
                    count = len(child_list)
                else:
                    count = 0
                if count >= 1 :
                    # translators: leave all/any {...} untranslated
                    childmsg = ngettext(" ({number_of} child)",
                                        " ({number_of} children)", count
                                       ).format(number_of=count)
                else :
                    childmsg = _(" (no children)")
                self.family = None
                box = self.get_people_box(post_msg=childmsg)
                eventbox = widgets.ShadeBox(self.use_shade)
                eventbox.add(box)
                self.child.attach(eventbox, _PDATA_START, self.row,
                                  _PDATA_STOP-_PDATA_START, 1)
                self.row += 1 # now advance it
            else:
                hbox = Gtk.Box()
                addchild = widgets.IconButton(self.add_child_to_fam,
                                              family.handle,
                                              'list-add')
                addchild.set_tooltip_text(_('Add new child to family'))
                selchild = widgets.IconButton(self.sel_child_to_fam,
                                              family.handle,
                                              'gtk-index')
                selchild.set_tooltip_text(_('Add existing child to family'))
                hbox.pack_start(addchild, False, True, 0)
                hbox.pack_start(selchild, False, True, 0)
                self.child.attach(hbox, _CLABEL_START, self.row,
                                  _CLABEL_STOP-_CLABEL_START, 1)

                vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                i = 1
                child_list = family.get_child_ref_list()
                for child_ref in child_list:
                    self.write_child(vbox, child_ref.ref, i, True)
                    i += 1

                self.row += 1
                eventbox = widgets.ShadeBox(self.use_shade)
                eventbox.add(vbox)
                self.child.attach(eventbox, _CDATA_START-1, self.row,
                                  _CDATA_STOP-_CDATA_START+1, 1)
                self.row += 1

    def edit_button_press(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            self.edit_person(obj, handle)

    def edit_person(self, obj, handle):
        person = self.dbstate.db.get_person_from_handle(handle)
        try:
            EditPerson(self.dbstate, self.uistate, [], person)
        except WindowActiveError:
            pass

    def edit_family(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            family = self.dbstate.db.get_family_from_handle(handle)
            try:
                EditFamily(self.dbstate, self.uistate, [], family)
            except WindowActiveError:
                pass

    def add_family(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            family = Family()
            person = self.dbstate.db.get_person_from_handle(self.get_active())
            if not person:
                return

            if person.gender == Person.MALE:
                family.set_father_handle(person.handle)
            else:
                family.set_mother_handle(person.handle)

            try:
                EditFamily(self.dbstate, self.uistate, [], family)
            except WindowActiveError:
                pass

    def add_spouse(self, *obj):
        family = Family()
        person = self.dbstate.db.get_person_from_handle(self.get_active())

        if not person:
            return

        if person.gender == Person.MALE:
            family.set_father_handle(person.handle)
        else:
            family.set_mother_handle(person.handle)

        try:
            EditFamily(self.dbstate, self.uistate, [], family)
        except WindowActiveError:
            pass

    def edit_active(self, obj, value):
        phandle = self.get_active()
        self.edit_person(obj, phandle)

    def add_child_to_fam(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            callback = lambda x: self.callback_add_child(x, handle)
            person = Person()
            name = Name()
            #the editor requires a surname
            name.add_surname(Surname())
            name.set_primary_surname(0)
            family = self.dbstate.db.get_family_from_handle(handle)
            father_h = family.get_father_handle()
            if father_h:
                father = self.dbstate.db.get_person_from_handle(father_h)
                if father:
                    preset_name(father, name)
            person.set_primary_name(name)
            try:
                EditPerson(self.dbstate, self.uistate, [], person,
                           callback=callback)
            except WindowActiveError:
                pass

    def callback_add_child(self, person, family_handle):
        ref = ChildRef()
        ref.ref = person.get_handle()
        family = self.dbstate.db.get_family_from_handle(family_handle)
        family.add_child_ref(ref)

        with DbTxn(_("Add Child to Family"), self.dbstate.db) as trans:
            #add parentref to child
            person.add_parent_family_handle(family_handle)
            #default relationship is used
            self.dbstate.db.commit_person(person, trans)
            #add child to family
            self.dbstate.db.commit_family(family, trans)

    def sel_child_to_fam(self, obj, event, handle, surname=None):
        if button_activated(event, _LEFT_BUTTON):
            SelectPerson = SelectorFactory('Person')
            family = self.dbstate.db.get_family_from_handle(handle)
            # it only makes sense to skip those who are already in the family
            skip_list = [family.get_father_handle(),
                         family.get_mother_handle()]
            skip_list.extend(x.ref for x in family.get_child_ref_list())

            sel = SelectPerson(self.dbstate, self.uistate, [],
                               _("Select Child"), skip=skip_list)
            person = sel.run()

            if person:
                self.callback_add_child(person, handle)

    def select_family(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            SelectFamily = SelectorFactory('Family')

            phandle = self.get_active()
            person = self.dbstate.db.get_person_from_handle(phandle)
            skip = set(person.get_family_handle_list())

            dialog = SelectFamily(self.dbstate, self.uistate, skip=skip)
            family = dialog.run()

            if family:
                child = self.dbstate.db.get_person_from_handle(self.get_active())

                self.dbstate.db.add_child_to_family(family, child)

    def select_parents(self, *obj):
        SelectFamily = SelectorFactory('Family')

        phandle = self.get_active()
        person = self.dbstate.db.get_person_from_handle(phandle)
        skip = set(person.get_family_handle_list()+
                   person.get_parent_family_handle_list())

        dialog = SelectFamily(self.dbstate, self.uistate, skip=skip)
        family = dialog.run()

        if family:
            child = self.dbstate.db.get_person_from_handle(self.get_active())

            self.dbstate.db.add_child_to_family(family, child)

    def add_parents(self, *obj):
        family = Family()
        person = self.dbstate.db.get_person_from_handle(self.get_active())

        if not person:
            return

        ref = ChildRef()
        ref.ref = person.handle
        family.add_child_ref(ref)

        try:
            EditFamily(self.dbstate, self.uistate, [], family)
        except WindowActiveError:
            pass

    def add_parent_family(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            family = Family()
            person = self.dbstate.db.get_person_from_handle(self.get_active())

            ref = ChildRef()
            ref.ref = person.handle
            family.add_child_ref(ref)

            try:
                EditFamily(self.dbstate, self.uistate, [], family)
            except WindowActiveError:
                pass

    def delete_family(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            self.dbstate.db.remove_parent_from_family(self.get_active(), handle)

    def delete_parent_family(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            self.dbstate.db.remove_child_from_family(self.get_active(), handle)

    def change_to(self, obj, handle):
        self.change_active(handle)

    def reorder_button_press(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            self.reorder(obj)

    def reorder(self, *obj):
        if self.get_active():
            try:
                Reorder(self.dbstate, self.uistate, [], self.get_active())
            except WindowActiveError:
                pass

    def config_connect(self):
        """
        Overwriten from  :class:`~gui.views.pageview.PageView method
        This method will be called after the ini file is initialized,
        use it to monitor changes in the ini file
        """
        self._config.connect("preferences.relation-shade",
                          self.shade_update)
        self._config.connect("preferences.releditbtn",
                          self.config_update)
        self._config.connect("preferences.relation-display-theme",
                          self.config_update)
        self._config.connect("preferences.family-siblings",
                          self.config_update)
        self._config.connect("preferences.family-details",
                          self.config_update)
        config.connect("interface.toolbar-on",
                          self.shade_update)

    def config_panel(self, configdialog):
        """
        Function that builds the widget in the configuration dialog
        """
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)

        configdialog.add_checkbox(grid,
                _('Use shading'),
                0, 'preferences.relation-shade')
        configdialog.add_checkbox(grid,
                _('Display edit buttons'),
                1, 'preferences.releditbtn')
        checkbox = Gtk.CheckButton(label=_('View links as website links'))
        theme = self._config.get('preferences.relation-display-theme')
        checkbox.set_active(theme == 'WEBPAGE')
        checkbox.connect('toggled', self._config_update_theme)
        grid.attach(checkbox, 1, 2, 8, 1)

        return _('Layout'), grid

    def content_panel(self, configdialog):
        """
        Function that builds the widget in the configuration dialog
        """
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        configdialog.add_checkbox(grid,
                _('Show Details'),
                0, 'preferences.family-details')
        configdialog.add_checkbox(grid,
                _('Show Siblings'),
                1, 'preferences.family-siblings')

        return _('Content'), grid

    def _config_update_theme(self, obj):
        """
        callback from the theme checkbox
        """
        if obj.get_active():
            self.theme = 'WEBPAGE'
            self._config.set('preferences.relation-display-theme',
                              'WEBPAGE')
        else:
            self.theme = 'CLASSIC'
            self._config.set('preferences.relation-display-theme',
                              'CLASSIC')

    def _get_configure_page_funcs(self):
        """
        Return a list of functions that create gtk elements to use in the
        notebook pages of the Configure dialog

        :return: list of functions
        """
        return [self.content_panel, self.config_panel]

#-------------------------------------------------------------------------
#
# Function to return if person has children
#
#-------------------------------------------------------------------------
def has_children(db,p):
    """
    Return if a person has children.
    """
    for family_handle in p.get_family_handle_list():
        family = db.get_family_from_handle(family_handle)
        if not family:
            continue
        childlist = family.get_child_ref_list()
        if childlist and len(childlist) > 0:
            return True
    return False

def button_activated(event, mouse_button):
    if (event.type == Gdk.EventType.BUTTON_PRESS and
        event.button == mouse_button) or \
       (event.type == Gdk.EventType.KEY_PRESS and
        event.keyval in (_RETURN, _KP_ENTER, _SPACE)):
        return True
    else:
        return False

