# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
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

"""
Relationship View
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from TransUtils import sgettext as _
from gettext import ngettext
import cgi

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import pango

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import gen.lib
from gui.views.navigationview import NavigationView
from gui.editors import EditPerson, EditFamily
from BasicUtils import name_displayer
from Utils import media_path_full, probably_alive
import DateHandler
import ThumbNails
import config
from gui import widgets
from gui.selectors import SelectorFactory
import Errors
import Bookmarks
import const

from gen.utils import get_birth_or_fallback, get_death_or_fallback

_GenderCode = {
    gen.lib.Person.MALE    : u'\u2642', 
    gen.lib.Person.FEMALE  : u'\u2640', 
    gen.lib.Person.UNKNOWN : u'\u2650', 
    }

_NAME_START   = 0
_LABEL_START  = 0
_LABEL_STOP   = 1
_DATA_START   = _LABEL_STOP
_DATA_STOP    = _DATA_START+1
_BTN_START    = _DATA_STOP
_BTN_STOP     = _BTN_START+2
_PLABEL_START = 1 
_PLABEL_STOP  = _PLABEL_START+1
_PDATA_START  = _PLABEL_STOP
_PDATA_STOP   = _PDATA_START+2
_PDTLS_START  = _PLABEL_STOP
_PDTLS_STOP   = _PDTLS_START+2
_CLABEL_START = _PLABEL_START+1
_CLABEL_STOP  = _CLABEL_START+1
_CDATA_START  = _CLABEL_STOP
_CDATA_STOP   = _CDATA_START+1
_CDTLS_START  = _CDATA_START
_CDTLS_STOP   = _CDTLS_START+1
_ALABEL_START = 0
_ALABEL_STOP  = _ALABEL_START+1
_ADATA_START  = _ALABEL_STOP
_ADATA_STOP   = _ADATA_START+3
_SDATA_START  = 2
_SDATA_STOP   = 4
_RETURN = gtk.gdk.keyval_from_name("Return")
_KP_ENTER = gtk.gdk.keyval_from_name("KP_Enter")
_LEFT_BUTTON = 1
_RIGHT_BUTTON = 3

class AttachList(object):

    def __init__(self):
        self.list = []
        self.max_x = 0
        self.max_y = 0

    def attach(self, widget, x0, x1, y0, y1, xoptions=gtk.EXPAND|gtk.FILL, 
               yoptions=gtk.EXPAND|gtk.FILL):
        assert(widget)
        assert(x1>x0)
        self.list.append((widget, x0, x1, y0, y1, xoptions, yoptions))
        self.max_x = max(self.max_x, x1)
        self.max_y = max(self.max_y, y1)

class RelationshipView(NavigationView):

    def __init__(self, dbstate, uistate, nav_group=0):
        NavigationView.__init__(self, _('Relationships'),
                                      dbstate, uistate, 
                                      dbstate.db.get_bookmarks(), 
                                      Bookmarks.PersonBookmarks,
                                      nav_group)        

        self.func_list = {
            '<CONTROL>J' : self.jump,
            }

        dbstate.connect('database-changed', self.change_db)
        self.show_siblings = config.get('preferences.family-siblings')
        self.show_details = config.get('preferences.family-details')
        self.redrawing = False
        self.use_shade = config.get('preferences.relation-shade')
        self.toolbar_visible = config.get('interface.toolbar-on')

        self.color = gtk.TextView().style.white
        self.child = None
        self.old_handle = None

        config.connect("preferences.relation-shade",
                          self.shade_update)
        config.connect("interface.releditbtn",
                          self.config_update)
        config.connect("interface.toolbar-on",
                          self.shade_update)
        self.reorder_sensitive = False
        self.collapsed_items = {}

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

    def navigation_type(self):
        return 'Person'

    def goto_handle(self, handle):
        self.redraw()

    def shade_update(self, client, cnxn_id, entry, data):
        self.use_shade = config.get('preferences.relation-shade')
        self.toolbar_visible = config.get('interface.toolbar-on')
        self.uistate.modify_statusbar(self.dbstate)
        self.redraw()

    def config_update(self, client, cnxn_id, entry, data):
        self.redraw()

    def build_tree(self):
        self.redraw()

    def person_update(self, handle_list):
        person  = self.get_active()
        if person:
            while not self.change_person(person):
                pass
        else:
            self.change_person(None)

    def person_rebuild(self):
        """Large change to person database"""
        if self.active:
            self.bookmarks.redraw()
        person  = self.get_active()
        if person:
            while not self.change_person(person):
                pass
        else:
            self.change_person(None)

    def family_update(self, handle_list):
        person  = self.get_active()
        if person:
            while not self.change_person(person):
                pass
        else:
            self.change_person(None)

    def family_add(self, handle_list):
        person  = self.get_active()
        if person:
            while not self.change_person(person):
                pass
        else:
            self.change_person(None)

    def family_delete(self, handle_list):
        person  = self.get_active()
        if person:
            while not self.change_person(person):
                pass
        else:
            self.change_person(None)

    def family_rebuild(self):
        person  = self.get_active()
        if person:
            while not self.change_person(person):
                pass
        else:
            self.change_person(None)

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

        container = gtk.VBox()
        container.set_border_width(12)

        self.vbox = gtk.VBox()
        self.vbox.show()

        self.header = gtk.VBox()
        self.header.show()

        self.child = None

        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scroll.show()
        
        vp = gtk.Viewport()
        vp.set_shadow_type(gtk.SHADOW_NONE)
        vp.add(self.vbox)

        self.scroll.add(vp)
        self.scroll.show_all()

        container.set_spacing(6)
        container.pack_start(self.header, False, False)
        container.pack_start(gtk.HSeparator(), False, False)
        container.add(self.scroll)
        container.show_all()
        return container

    def ui_definition(self):
        """
        Specifies the UIManager XML code that defines the menus and buttons
        associated with the interface.
        """
        return '''<ui>
          <menubar name="MenuBar">
            <menu action="GoMenu">
              <placeholder name="CommonGo">
                <menuitem action="Back"/>
                <menuitem action="Forward"/>
                <separator/>
                <menuitem action="HomePerson"/>
                <separator/>
              </placeholder>
            </menu>
            <menu action="EditMenu">
              <menuitem action="Edit"/>
              <menuitem action="AddParentsMenu"/>
              <menuitem action="ShareFamilyMenu"/>
              <menuitem action="AddSpouseMenu"/>
              <menuitem action="ChangeOrder"/>
              <menuitem action="FilterEdit"/>
            </menu>
            <menu action="BookMenu">
              <placeholder name="AddEditBook">
                <menuitem action="AddBook"/>
                <menuitem action="EditBook"/>
              </placeholder>
            </menu>
            <menu action="ViewMenu">
              <menuitem action="Siblings"/>
              <menuitem action="Details"/>
            </menu>
          </menubar>
          <toolbar name="ToolBar">
            <placeholder name="CommonNavigation">
              <toolitem action="Back"/>  
              <toolitem action="Forward"/>  
              <toolitem action="HomePerson"/>
            </placeholder>
            <placeholder name="CommonEdit">
              <toolitem action="Edit"/>
              <toolitem action="AddParents"/>
              <toolitem action="ShareFamily"/>
              <toolitem action="AddSpouse"/>
              <toolitem action="ChangeOrder"/>
            </placeholder>
          </toolbar>
          <popup name="Popup">
            <menuitem action="Back"/>
            <menuitem action="Forward"/>
            <menuitem action="HomePerson"/>
            <separator/>
          </popup>
        </ui>'''

    def define_actions(self):
        NavigationView.define_actions(self)

        self.order_action = gtk.ActionGroup(self.title + '/ChangeOrder')
        self.order_action.add_actions([
            ('ChangeOrder', gtk.STOCK_SORT_ASCENDING, _('_Reorder'), None ,
            _("Change order of parents and families"), self.reorder),
            ])

        self.family_action = gtk.ActionGroup(self.title + '/Family')
        self.family_action.add_actions([
            ('Edit', gtk.STOCK_EDIT, _('Edit...'), "<control>Return",
                _("Edit the active person"), self.edit_active),
            ('AddSpouse', 'gramps-spouse', _('Partner'), None ,
                _("Add a new family with person as parent"), self.add_spouse),
            ('AddSpouseMenu', 'gramps-spouse', _('Add Partner...'), None ,
                _("Add a new family with person as parent"), self.add_spouse),
            ('AddParents', 'gramps-parents-add', _('Add'), None ,
                _("Add a new set of parents"), self.add_parents),
            ('AddParentsMenu', 'gramps-parents-add', _('Add New Parents...'), 
                None, _("Add a new set of parents"), self.add_parents),
            ('ShareFamily', 'gramps-parents-open', _('Share'), 
                None , _("Add person as child to an existing family"), 
                self.select_parents),
            ('ShareFamilyMenu', 'gramps-parents-open', 
                _('Add Existing Parents...'), None , 
                _("Add person as child to an existing family"), 
                self.select_parents),
            ])
            
        self._add_action('FilterEdit',  None, _('Person Filter Editor'), 
                        callback=self.filter_editor)
                        
        self._add_action_group(self.order_action)
        self._add_action_group(self.family_action)

        self._add_toggle_action('Details', None, _('Show Details'), 
                                None, None, self.details_toggle, 
                                self.show_details)
        self._add_toggle_action('Siblings', None, _('Show Siblings'), 
                                None, None, self.siblings_toggle, 
                                self.show_siblings)

        self.order_action.set_sensitive(self.reorder_sensitive)
        self.family_action.set_sensitive(False)

    def filter_editor(self, obj):
        from FilterEditor import FilterEditor

        try:
            FilterEditor('Person', const.CUSTOM_FILTERS, 
                         self.dbstate, self.uistate)
        except Errors.WindowActiveError:
            return

    def siblings_toggle(self, obj):
        self.show_siblings = obj.get_active()
        self.change_person(self.get_active())
        config.set('preferences.family-siblings', self.show_siblings)

    def details_toggle(self, obj):
        self.show_details = obj.get_active()
        self.change_person(self.get_active())
        config.set('preferences.family-details', self.show_details)

    def change_db(self, db):
        #reset the connects
        self._change_db(db)
        if self.child:
            for old_child in self.vbox.get_children():
                self.vbox.remove(old_child)
            for old_child in self.header.get_children():
                self.header.remove(old_child)
            self.child = None
        self.bookmarks.update_bookmarks(db.get_bookmarks())
        if self.active:
                self.bookmarks.redraw()
        self.redraw()

    def get_name(self, handle, use_gender=False):
        if handle:
            person = self.dbstate.db.get_person_from_handle(handle)
            name = name_displayer.display(person)
            if use_gender:
                gender = _GenderCode[person.gender]
            else:
                gender = ""
            return (name, gender)
        else:
            return (_(u"Unknown"), "")

    def redraw(self, *obj):
        active_person = self.get_active()
        if active_person:
            self.change_person(active_person)
        else:
            self.change_person(None)
        
    def change_person(self, obj):
        try:
            return self._change_person(obj)
        except AttributeError, msg:
            from QuestionDialog import RunDatabaseRepair
            RunDatabaseRepair(msg)
            return True

    def _change_person(self, obj):
        if obj == self.old_handle:
            #same object, keep present scroll position
            old_vadjust = self.scroll.get_vadjustment().value
            self.old_handle = obj
        else:
            #different object, scroll to top
            old_vadjust = self.scroll.get_vadjustment().lower
            self.old_handle = obj
        self.scroll.get_vadjustment().value = \
                            self.scroll.get_vadjustment().lower
        if self.redrawing:
            return False
        self.redrawing = True

        for old_child in self.vbox.get_children():
            self.vbox.remove(old_child)
        for old_child in self.header.get_children():
            self.header.remove(old_child)

        person = self.dbstate.db.get_person_from_handle(obj)
        if not person:
            self.family_action.set_sensitive(False)
            self.order_action.set_sensitive(False)
            self.redrawing = False
            return
        self.family_action.set_sensitive(True)

        self.write_title(person)

        self.attach = AttachList()
        self.row = 0

        family_handle_list = person.get_parent_family_handle_list()

        self.reorder_sensitive = len(family_handle_list)> 1

        if family_handle_list:
            for family_handle in family_handle_list:
                if family_handle:
                    self.write_parents(family_handle, person)
        else:
            self.write_label("%s:" % _('Parents'), None, True, person)
            self.row += 1
                
        family_handle_list = person.get_family_handle_list()
        
        if not self.reorder_sensitive:
            self.reorder_sensitive = len(family_handle_list)> 1

        if family_handle_list:
            for family_handle in family_handle_list:
                if family_handle:
                    self.write_family(family_handle, person)
        else:
            self.write_label("%s:" % _('Family'), None, False, person)
            self.row += 1

        self.row = 0

        # Here it is necessary to beat GTK into submission. For some
        # bizzare reason, if you have an empty column that is spanned, 
        # you lose the appropriate FILL handling. So, we need to see if
        # column 3 is unused (usually if there is no siblings or children.
        # If so, we need to subtract one index of each x coord > 3.
                
        found = False
        for d in self.attach.list:
            if d[1] == 4 or d[2] == 4:
                found = True

        if found:
            cols = self.attach.max_x
        else:
            cols = self.attach.max_x-1

        self.child = gtk.Table(self.attach.max_y, cols)
        self.child.set_border_width(12)
        self.child.set_col_spacings(12)
        self.child.set_row_spacings(0)

        for d in self.attach.list:
            x0 = d[1]
            x1 = d[2]
            if not found:
                if x0 > 4:
                    x0 -= 1
                if x1 > 4:
                    x1 -= 1
            self.child.attach(d[0], x0, x1, d[3], d[4], d[5], d[6])

        self.child.show_all()

        self.vbox.pack_start(self.child, False)
        #reset scroll position as it was before
        self.scroll.get_vadjustment().value = old_vadjust
        self.redrawing = False
        self.uistate.modify_statusbar(self.dbstate)

        self.order_action.set_sensitive(self.reorder_sensitive)

        return True

    def write_title(self, person):

        for old_child in self.header.get_children():
            self.header.remove(old_child)

        table = gtk.Table(2, 3)
        table.set_col_spacings(12)
        table.set_row_spacings(0)

        # name and edit button
        name = name_displayer.display(person)
        fmt = '<span size="larger" weight="bold">%s</span>'
        text = fmt % cgi.escape(name)
        label = widgets.DualMarkupLabel(text, _GenderCode[person.gender],
                                        x_align=1, y_align=0)
        if config.get('interface.releditbtn'):
            button = widgets.IconButton(self.edit_button_press, 
                                        person.handle)
            button.set_tooltip_text(_('Edit %s') % name)
        else:
            button = None
        hbox = widgets.LinkBox(label, button)

        table.attach(hbox, 0, 2, 0, 1)

        eventbox = gtk.EventBox()
        if self.use_shade:
            eventbox.modify_bg(gtk.STATE_NORMAL, self.color)
        table.attach(eventbox, 1, 2, 1, 2)
        subtbl = gtk.Table(3, 3)
        subtbl.set_col_spacings(12)
        subtbl.set_row_spacings(0)
        eventbox.add(subtbl)
                
        # GRAMPS ID

        subtbl.attach(widgets.BasicLabel("%s:" % _('ID')),
                      1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0)
        subtbl.attach(widgets.BasicLabel(person.gramps_id),
                      2, 3, 0, 1, yoptions=0)

        # Birth event.
        birth = get_birth_or_fallback(self.dbstate.db, person)
        if birth:
            birth_title = birth.get_type()
        else:
            birth_title = _("Birth")

        subtbl.attach(widgets.BasicLabel("%s:" % birth_title),
                      1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0)
        subtbl.attach(widgets.BasicLabel(self.format_event(birth)),
                      2, 3, 1, 2, yoptions=0)

        death = get_death_or_fallback(self.dbstate.db, person)
        if death:
            death_title = death.get_type()
        else:
            death_title = _("Death")

        showed_death = False
        if birth:
            birth_date = birth.get_date_object()
            if (birth_date and birth_date.get_valid()):
                if death:
                    death_date = death.get_date_object()
                    if (death_date and death_date.get_valid()):
                        age = death_date - birth_date
                        subtbl.attach(widgets.BasicLabel("%s:" % death_title),
                                      1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0)
                        subtbl.attach(widgets.BasicLabel("%s (%s)" % 
                                                         (self.format_event(death), age),
                                                         pango.ELLIPSIZE_END),
                                      2, 3, 2, 3, yoptions=0)
                        showed_death = True
                if not showed_death:
                    age = gen.lib.date.Today() - birth_date
                    if probably_alive(person, self.dbstate.db):
                        subtbl.attach(widgets.BasicLabel("%s:" % _("Alive")),
                                      1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0)
                        subtbl.attach(widgets.BasicLabel("(%s)" % age, pango.ELLIPSIZE_END),
                                      2, 3, 2, 3, yoptions=0)
                    else:
                        subtbl.attach(widgets.BasicLabel("%s:" % _("Death")),
                                      1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0)
                        subtbl.attach(widgets.BasicLabel("%s (%s)" % (_("unknown"), age), 
                                                         pango.ELLIPSIZE_END),
                                      2, 3, 2, 3, yoptions=0)
                    showed_death = True

        if not showed_death:
            subtbl.attach(widgets.BasicLabel("%s:" % death_title),
                          1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0)
            subtbl.attach(widgets.BasicLabel(self.format_event(death)),
                          2, 3, 2, 3, yoptions=0)

        mbox = gtk.HBox()
        mbox.add(table)

        # image
        image_list = person.get_media_list()
        if image_list:
            mobj = self.dbstate.db.get_object_from_handle(image_list[0].ref)
            if mobj and mobj.get_mime_type()[0:5] == "image":
                pixbuf = ThumbNails.get_thumbnail_image(
                                media_path_full(self.dbstate.db, 
                                                mobj.get_path()),
                                rectangle=image_list[0].get_rectangle())
                image = gtk.Image()
                image.set_from_pixbuf(pixbuf)
                image.show()
                mbox.pack_end(image, False)

        mbox.show_all()
        self.header.pack_start(mbox, False)

    def write_person_event(self, ename, event):
        if event:
            dobj = event.get_date_object()
            phandle = event.get_place_handle()
            if phandle:
                pname = self.place_name(phandle)
            else:
                pname = None

            value = {
                'date' : DateHandler.displayer.display(dobj), 
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
                pname = self.place_name(phandle)
            else:
                pname = None

            value = {
                'date' : DateHandler.displayer.display(dobj), 
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
        self.attach.attach(widgets.BasicLabel(title), _ALABEL_START, 
                           _ALABEL_STOP, self.row, self.row+1, 
                           xoptions=gtk.FILL|gtk.SHRINK)
        self.attach.attach(widgets.BasicLabel(data), 
                           _ADATA_START, _ADATA_STOP, 
                           self.row, self.row+1)
        self.row += 1

    def write_label(self, title, family, is_parent, person = None):
        msg = '<span style="italic" weight="heavy">%s</span>' % cgi.escape(title)
        hbox = gtk.HBox()
        label = widgets.MarkupLabel(msg, x_align=1)
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
            arrow = gtk.Arrow(gtk.ARROW_RIGHT, gtk.SHADOW_OUT)
        hbox.pack_start(arrow, False)
        hbox.pack_start(label, True)
        self.attach.attach(hbox,
                           _LABEL_START, _LABEL_STOP, 
                           self.row, self.row+1, gtk.SHRINK|gtk.FILL)

        if family:
            value = family.gramps_id
        else:
            value = ""
        self.attach.attach(widgets.BasicLabel(value), 
                           _DATA_START, _DATA_STOP, 
                           self.row, self.row+1, gtk.SHRINK|gtk.FILL)

        if family and self.check_collapsed(person.handle, family.handle):
            # show family names later
            pass
        else:
            hbox = gtk.HBox()
            hbox.set_spacing(12)
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

            if not self.toolbar_visible and not self.dbstate.db.readonly:
                # Show edit-Buttons if toolbar is not visible
                if self.reorder_sensitive:
                    add = widgets.IconButton(self.reorder_button_press, None, 
                                             gtk.STOCK_SORT_ASCENDING)
                    add.set_tooltip_text(ord_msg)
                    hbox.pack_start(add, False)

                add = widgets.IconButton(call_fcn, None, gtk.STOCK_ADD)
                add.set_tooltip_text(add_msg)
                hbox.pack_start(add, False)

                if is_parent:
                    add = widgets.IconButton(self.select_family, None,
                                             gtk.STOCK_INDEX)
                    add.set_tooltip_text(sel_msg)
                    hbox.pack_start(add, False)

            if family:
                edit = widgets.IconButton(self.edit_family, family.handle, 
                                          gtk.STOCK_EDIT)
                edit.set_tooltip_text(edit_msg)
                hbox.pack_start(edit, False)
                if not self.dbstate.db.readonly:
                    delete = widgets.IconButton(del_fcn, family.handle, 
                                                gtk.STOCK_REMOVE)
                    delete.set_tooltip_text(del_msg)
                    hbox.pack_start(delete, False)
            self.attach.attach(hbox, _BTN_START, _BTN_STOP, self.row, self.row+1)
        self.row += 1
        
######################################################################

    def write_parents(self, family_handle, person = None):
        family = self.dbstate.db.get_family_from_handle(family_handle)
        if not family:
            return
        if person and self.check_collapsed(person.handle, family_handle):
            # don't show rest
            self.write_label("%s:" % _('Parents'), family, True, person)
            self.row -= 1 # back up one row for summary names
            active = self.ui.get_active()
            child_list = [ref.ref for ref in family.get_child_ref_list()
                          if ref.ref != active]
            if child_list:
                count = len(child_list)
            else:
                count = 0
            if count > 1 :
                childmsg = ngettext(" (%d sibling)", " (%d siblings)", count) % count
            elif count == 1 :
                gender = self.dbstate.db.get_person_from_handle(\
                                        child_list[0]).gender
                if gender == gen.lib.Person.MALE :
                    childmsg = _(" (1 brother)")
                elif gender == gen.lib.Person.FEMALE :
                    childmsg = _(" (1 sister)")
                else :
                    childmsg = _(" (1 sibling)")
            else :
                childmsg = _(" (only child)")
            box = self.get_people_box(family.get_father_handle(),
                                      family.get_mother_handle(),
                                      post_msg=childmsg)
            eventbox = gtk.EventBox()
            if self.use_shade:
                eventbox.modify_bg(gtk.STATE_NORMAL, self.color)
            eventbox.add(box)
            self.attach.attach(
                eventbox, _PDATA_START, _PDATA_STOP,
                self.row, self.row+1)
            self.row += 1 # now advance it
        else:
            self.write_label("%s:" % _('Parents'), family, True, person)
            self.write_person(_('Father'), family.get_father_handle())
            self.write_person(_('Mother'), family.get_mother_handle())

            if self.show_siblings:
                active = self.get_active()
                hbox = gtk.HBox()
                if self.check_collapsed(person.handle, "SIBLINGS"):
                    arrow = widgets.ExpandCollapseArrow(True,
                                                        self.expand_collapse_press,
                                                        (person, "SIBLINGS"))
                else:
                    arrow = widgets.ExpandCollapseArrow(False,
                                                        self.expand_collapse_press,
                                                        (person, "SIBLINGS"))
                hbox.pack_start(arrow, False)
                label_cell = self.build_label_cell(_('Siblings'))
                hbox.pack_start(label_cell, True)
                self.attach.attach(
                    hbox, _CLABEL_START-1, _CLABEL_STOP-1, self.row, 
                    self.row+1, xoptions=gtk.FILL|gtk.SHRINK,
                    yoptions=gtk.FILL)

                if self.check_collapsed(person.handle, "SIBLINGS"):
                    hbox = gtk.HBox()
                    child_list = [ref.ref for ref in family.get_child_ref_list()
                                  if ref.ref != active]
                    if child_list:
                        count = len(child_list)
                    else:
                        count = 0
                    if count > 1 :
                        childmsg = ngettext(" (%d sibling)"," (%d siblings)", count) % count
                    elif count == 1 :
                        gender = self.dbstate.db.get_person_from_handle(\
                                                child_list[0]).gender
                        if gender == gen.lib.Person.MALE :
                            childmsg = _(" (1 brother)")
                        elif gender == gen.lib.Person.FEMALE :
                            childmsg = _(" (1 sister)")
                        else :
                            childmsg = _(" (1 sibling)")
                    else :
                        childmsg = _(" (only child)")
                    box = self.get_people_box(post_msg=childmsg)
                    eventbox = gtk.EventBox()
                    if self.use_shade:
                        eventbox.modify_bg(gtk.STATE_NORMAL, self.color)
                    eventbox.add(box)
                    self.attach.attach(
                        eventbox, _PDATA_START, _PDATA_STOP,
                        self.row, self.row+1)
                    self.row += 1 # now advance it
                else:
                    hbox = gtk.HBox()
                    addchild = widgets.IconButton(self.add_child_to_fam, 
                                                  family.handle, 
                                                  gtk.STOCK_ADD)
                    addchild.set_tooltip_text(_('Add new child to family'))
                    selchild = widgets.IconButton(self.sel_child_to_fam, 
                                                  family.handle, 
                                                  gtk.STOCK_INDEX)
                    selchild.set_tooltip_text(_('Add existing child to family'))
                    hbox.pack_start(addchild, False)
                    hbox.pack_start(selchild, False)

                    self.attach.attach(
                        hbox, _CLABEL_START, _CLABEL_STOP, self.row, 
                        self.row+1, xoptions=gtk.FILL|gtk.SHRINK,
                        yoptions=gtk.FILL)

                    self.row += 1
                    vbox = gtk.VBox()
                    i = 1
                    child_list = [ref.ref for ref in family.get_child_ref_list()]
                    for child_handle in child_list:
                        child_should_be_linked = (child_handle != active)
                        self.write_child(vbox, child_handle, i, child_should_be_linked)
                        i += 1
                    eventbox = gtk.EventBox()
                    if self.use_shade:
                        eventbox.modify_bg(gtk.STATE_NORMAL, self.color)
                    eventbox.add(vbox)
                    self.attach.attach(
                        eventbox, _CDATA_START-1, _CDATA_STOP, self.row,
                        self.row+1)

            self.row += 1

    def get_people_box(self, *handles, **kwargs):
        vbox = gtk.HBox()
        initial_name = True
        for handle in handles:
            if not initial_name:
                link_label = gtk.Label(" %s " % _('and'))
                link_label.show()
                vbox.pack_start(link_label, expand=False)
            initial_name = False
            if handle:
                name = self.get_name(handle, True)
                link_label = widgets.LinkLabel(name, self._button_press, handle)
                if self.use_shade:
                    link_label.modify_bg(gtk.STATE_NORMAL, self.color)
                if config.get('interface.releditbtn'):
                    button = widgets.IconButton(self.edit_button_press, 
                                                handle)
                    button.set_tooltip_text(_('Edit %s') % name[0])
                else:
                    button = None
                vbox.pack_start(widgets.LinkBox(link_label, button),
                                expand=False)
            else:
                link_label = gtk.Label(_('Unknown'))
                link_label.show()
                vbox.pack_start(link_label, expand=False)
        if "post_msg" in kwargs and kwargs["post_msg"]:
            link_label = gtk.Label(kwargs["post_msg"])
            link_label.show()
            vbox.pack_start(link_label, expand=False)
        return vbox

    def write_person(self, title, handle):
        if title:
            format = '<span weight="bold">%s: </span>'
        else:
            format = "%s"

        label = widgets.MarkupLabel(format % cgi.escape(title),
                                    x_align=1, y_align=0)
        if config.get('interface.releditbtn'):
            label.set_padding(0, 5)
        self.attach.attach(label, _PLABEL_START, _PLABEL_STOP, self.row, 
                           self.row+1, xoptions=gtk.FILL|gtk.SHRINK,
                           yoptions=gtk.FILL|gtk.SHRINK)

        vbox = gtk.VBox()
        
        if handle:
            name = self.get_name(handle, True)
            person = self.dbstate.db.get_person_from_handle(handle)
            parent = len(person.get_parent_family_handle_list()) > 0
            format = ''
            relation_display_theme = config.get('preferences.relation-display-theme')
            if parent:
                if relation_display_theme == "CLASSIC":
                    format = 'underline="single" weight="heavy" style="italic"'
                elif relation_display_theme == "WEBPAGE":
                    format = 'foreground="blue" weight="heavy"'
            else:
                if relation_display_theme == "CLASSIC":
                    format = 'underline="single"'
                elif relation_display_theme == "WEBPAGE":
                    format = 'foreground="blue"'
            link_label = widgets.LinkLabel(name, self._button_press, 
                                           handle, format)
            if self.use_shade:
                link_label.modify_bg(gtk.STATE_NORMAL, self.color)
            if config.get('interface.releditbtn'):
                button = widgets.IconButton(self.edit_button_press, handle)
                button.set_tooltip_text(_('Edit %s') % name[0])
            else:
                button = None
            vbox.pack_start(widgets.LinkBox(link_label, button))
        else:
            link_label = gtk.Label(_('Unknown'))
            link_label.set_alignment(0, 1)
            link_label.show()
            vbox.pack_start(link_label)
            
        if self.show_details:
            value = self.info_string(handle)
            if value:
                vbox.pack_start(widgets.MarkupLabel(value))

        eventbox = gtk.EventBox()
        if self.use_shade:
            eventbox.modify_bg(gtk.STATE_NORMAL, self.color)
        eventbox.add(vbox)
        
        self.attach.attach(eventbox, _PDATA_START, _PDATA_STOP,
                           self.row, self.row+1)
        self.row += 1
        return vbox

    def build_label_cell(self, title):
        if title:
            format = '<span weight="bold">%s: </span>'
        else:
            format = "%s"

        lbl = widgets.MarkupLabel(format % cgi.escape(title),
                                  x_align=1, y_align=.5)
        if config.get('interface.releditbtn'):
            lbl.set_padding(0, 5)
        return lbl

    def write_child(self, vbox, handle, index, child_should_be_linked):
        if not child_should_be_linked:
            original_vbox = vbox
            vbox = gtk.VBox()
            frame = gtk.Frame()
            frame.set_shadow_type(gtk.SHADOW_ETCHED_IN)
            if self.use_shade:
                ev = gtk.EventBox()
                ev.modify_bg(gtk.STATE_NORMAL, self.color)
                ev.add(vbox)
                frame.add(ev)
            else:
                frame.add(vbox)
            original_vbox.add(frame)
        
        parent = has_children(self.dbstate.db,
                              self.dbstate.db.get_person_from_handle(handle))

        format = ''
        relation_display_theme = config.get('preferences.relation-display-theme')
        if child_should_be_linked and parent:
            if relation_display_theme == "CLASSIC":
                format = 'underline="single" weight="heavy" style="italic"'
            elif relation_display_theme == "WEBPAGE":
                format = 'foreground="blue" weight="heavy"'
            else:
                raise AttributeError("invalid relation-display-theme: '%s'" % relation_display_theme)
        elif child_should_be_linked and not parent:
            if relation_display_theme == "CLASSIC":
                format = 'underline="single"'
            elif relation_display_theme == "WEBPAGE":
                format = 'foreground="blue"'
            else:
                raise AttributeError("invalid relation-display-theme: '%s'" % relation_display_theme)
        elif parent and not child_should_be_linked:
            format = 'weight="heavy"'

        if child_should_be_linked:
            link_func = self._button_press
        else:
            link_func = None

        name = self.get_name(handle, True)
        link_label = widgets.LinkLabel(name, link_func, handle, format)

        if self.use_shade:
            link_label.modify_bg(gtk.STATE_NORMAL, self.color)
        link_label.set_padding(3, 0)
        if child_should_be_linked and config.get('interface.releditbtn'):
            button = widgets.IconButton(self.edit_button_press, handle)
            button.set_tooltip_text(_('Edit %s') % name[0])
        else:
            button = None

        hbox = gtk.HBox()
        l = widgets.BasicLabel("%d." % index)
        l.set_width_chars(3)
        l.set_alignment(1.0, 0.5)
        hbox.pack_start(l, False, False, 0)
        hbox.pack_start(widgets.LinkBox(link_label, button),
                        False, False, 4)
        hbox.show()
        vbox.pack_start(hbox)

        if self.show_details:
            value = self.info_string(handle)
            if value:
                l = widgets.MarkupLabel(value)
                l.set_padding(48, 0)
                vbox.add(l)

    def write_data(self, box, title, start_col=_SDATA_START,
                   stop_col=_SDATA_STOP):
        box.add(widgets.BasicLabel(title))

    def info_string(self, handle):
        person = self.dbstate.db.get_person_from_handle(handle)
        if not person:
            return None

        birth = get_birth_or_fallback(self.dbstate.db, person)
        if birth and birth.get_type() != gen.lib.EventType.BIRTH:
            sdate = DateHandler.get_date(birth)
            if sdate:
                bdate  = "<i>%s</i>" % cgi.escape(sdate)
            else:
                bdate = ""
        elif birth:
            bdate  = cgi.escape(DateHandler.get_date(birth))
        else:
            bdate = ""

        death = get_death_or_fallback(self.dbstate.db, person)
        if death and death.get_type() != gen.lib.EventType.DEATH:
            sdate = DateHandler.get_date(death)
            if sdate:
                ddate  = "<i>%s</i>" % cgi.escape(sdate)
            else:
                ddate = ""
        elif death:
            ddate  = cgi.escape(DateHandler.get_date(death))
        else:
            ddate = ""

        if bdate and ddate:
            value = _("b. %(birthdate)s, d. %(deathdate)s") % {
                'birthdate' : bdate, 
                'deathdate' : ddate
                }
        elif bdate:
            value = _("short for born|b. %s") % (bdate)
        elif ddate:
            value = _("short for dead|d. %s") % (ddate)
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
            myMenu = gtk.Menu()
            myMenu.append(self.build_menu_item(handle))
            myMenu.popup(None, None, None, event.button, event.time)

    def build_menu_item(self, handle):
        person = self.dbstate.db.get_person_from_handle(handle)
        name = name_displayer.display(person)

        item = gtk.ImageMenuItem(None)
        image = gtk.image_new_from_stock(gtk.STOCK_EDIT, gtk.ICON_SIZE_MENU)
        image.show()
        label = gtk.Label(_("Edit %s") % name)
        label.show()
        label.set_alignment(0, 0)

        item.set_image(image)
        item.add(label)

        item.connect('activate', self.edit_menu, handle)
        item.show()
        return item

    def edit_menu(self, obj, handle):
        person = self.dbstate.db.get_person_from_handle(handle)
        try:
            EditPerson(self.dbstate, self.uistate, [], person)
        except Errors.WindowActiveError:
            pass

    def write_relationship(self, box, family):
        msg = _('Relationship type: %s') % cgi.escape(str(family.get_relationship()))
        box.add(widgets.MarkupLabel(msg))

    def place_name(self, handle):
        p = self.dbstate.db.get_place_from_handle(handle)
        return p.get_title()

    def write_marriage(self, vbox, family):
        value = False
        for event_ref in family.get_event_ref_list():
            handle = event_ref.ref
            event = self.dbstate.db.get_event_from_handle(handle)
            if event and event.get_type() == gen.lib.EventType.MARRIAGE and \
            (event_ref.get_role() == gen.lib.EventRoleType.FAMILY or 
            event_ref.get_role() == gen.lib.EventRoleType.PRIMARY ):
                self.write_event_ref(vbox, _('Marriage'), event)
                value = True
        return value

    def write_event_ref(self, vbox, ename, event, start_col=_SDATA_START, 
                        stop_col=_SDATA_STOP):
        if event:
            dobj = event.get_date_object()
            phandle = event.get_place_handle()
            if phandle:
                pname = self.place_name(phandle)
            else:
                pname = None

            value = {
                'date' : DateHandler.displayer.display(dobj), 
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
                    vbox, _('%(event_type)s: %(date)s in %(place)s') %
                    value, start_col, stop_col)
            else:
                self.write_data(
                    vbox, _('%(event_type)s: %(date)s') % value, 
                    start_col, stop_col)
        elif pname:
            self.write_data(
                vbox, _('%(event_type)s: %(place)s') % value,
                start_col, stop_col)
        else:
            self.write_data(
                vbox, '%(event_type)s:' % value, start_col, stop_col)

    def write_family(self, family_handle, person = None):
        family = self.dbstate.db.get_family_from_handle(family_handle)
        if family is None:
            from QuestionDialog import WarningDialog
            WarningDialog(
                _('Broken family detected'),
                _('Please run the Check and Repair Database tool'))
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
            self.write_label("%s:" % _('Family'), family, False, person)
            self.row -= 1 # back up
            child_list = family.get_child_ref_list()
            if child_list:
                count = len(child_list)
            else:
                count = 0
            if count >= 1 :
                childmsg = ngettext(" (%d child)"," (%d children)", count) % count
            else :
                childmsg = _(" (no children)")
            box = self.get_people_box(handle, post_msg=childmsg)
            eventbox = gtk.EventBox()
            if self.use_shade:
                eventbox.modify_bg(gtk.STATE_NORMAL, self.color)
            eventbox.add(box)
            self.attach.attach(
                eventbox, _PDATA_START, _PDATA_STOP,
                self.row, self.row+1)
            self.row += 1 # now advance it
        else:
            # show "V Family: ..." and the rest
            self.write_label("%s:" % _('Family'), family, False, person)
            if handle:
                box = self.write_person(_('Spouse'), handle)

                if not self.write_marriage(box, family):
                    self.write_relationship(box, family)

            hbox = gtk.HBox()
            if self.check_collapsed(family.handle, "CHILDREN"):
                arrow = widgets.ExpandCollapseArrow(True,
                                                    self.expand_collapse_press,
                                                    (family, "CHILDREN"))
            else:
                arrow = widgets.ExpandCollapseArrow(False,
                                                    self.expand_collapse_press,
                                                    (family, "CHILDREN"))
            hbox.pack_start(arrow, False)
            label_cell = self.build_label_cell(_('Children'))
            hbox.pack_start(label_cell, True)
            self.attach.attach(
                hbox, _CLABEL_START-1, _CLABEL_STOP-1, self.row, 
                self.row+1, xoptions=gtk.FILL|gtk.SHRINK,
                yoptions=gtk.FILL)

            if self.check_collapsed(family.handle, "CHILDREN"):
                hbox = gtk.HBox()
                child_list = family.get_child_ref_list()
                if child_list:
                    count = len(child_list)
                else:
                    count = 0
                if count >= 1 :
                    childmsg = ngettext(" (%d child)"," (%d children)", count) % count
                else :
                    childmsg = _(" (no children)")
                box = self.get_people_box(post_msg=childmsg)
                eventbox = gtk.EventBox()
                if self.use_shade:
                    eventbox.modify_bg(gtk.STATE_NORMAL, self.color)
                eventbox.add(box)
                self.attach.attach(
                    eventbox, _PDATA_START, _PDATA_STOP,
                    self.row, self.row+1)
                self.row += 1 # now advance it
            else:
                hbox = gtk.HBox()
                addchild = widgets.IconButton(self.add_child_to_fam, 
                                              family.handle, 
                                              gtk.STOCK_ADD)
                addchild.set_tooltip_text(_('Add new child to family'))
                selchild = widgets.IconButton(self.sel_child_to_fam, 
                                              family.handle, 
                                              gtk.STOCK_INDEX)
                selchild.set_tooltip_text(_('Add existing child to family'))                                  
                hbox.pack_start(addchild, False)
                hbox.pack_start(selchild, False)
                self.attach.attach(
                    hbox, _CLABEL_START, _CLABEL_STOP, self.row, 
                    self.row+1, xoptions=gtk.FILL|gtk.SHRINK,
                    yoptions=gtk.FILL)

                vbox = gtk.VBox()
                i = 1
                child_list = family.get_child_ref_list()
                for child_ref in child_list:
                    self.write_child(vbox, child_ref.ref, i, True)
                    i += 1

                self.row += 1
                eventbox = gtk.EventBox()
                if self.use_shade:
                    eventbox.modify_bg(gtk.STATE_NORMAL, self.color)
                eventbox.add(vbox)
                self.attach.attach(
                    eventbox, _CDATA_START-1, _CDATA_STOP, self.row,
                    self.row+1)
                self.row += 1

    def edit_button_press(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            self.edit_person(obj, handle)
        
    def edit_person(self, obj, handle):
        person = self.dbstate.db.get_person_from_handle(handle)
        try:
            EditPerson(self.dbstate, self.uistate, [], person)
        except Errors.WindowActiveError:
            pass

    def edit_family(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            family = self.dbstate.db.get_family_from_handle(handle)
            try:
                EditFamily(self.dbstate, self.uistate, [], family)
            except Errors.WindowActiveError:
                pass

    def add_family(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            family = gen.lib.Family()
            person = self.dbstate.db.get_person_from_handle(self.get_active())
            if not person:
                return
            
            if person.gender == gen.lib.Person.MALE:
                family.set_father_handle(person.handle)
            else:
                family.set_mother_handle(person.handle)
                
            try:
                EditFamily(self.dbstate, self.uistate, [], family)
            except Errors.WindowActiveError:
                pass

    def add_spouse(self, obj):
        family = gen.lib.Family()
        person = self.dbstate.db.get_person_from_handle(self.get_active())

        if not person:
            return
            
        if person.gender == gen.lib.Person.MALE:
            family.set_father_handle(person.handle)
        else:
            family.set_mother_handle(person.handle)
                
        try:
            EditFamily(self.dbstate, self.uistate, [], family)
        except Errors.WindowActiveError:
            pass

    def edit_active(self, obj):
        phandle = self.get_active()
        self.edit_person(obj, phandle)

    def add_child_to_fam(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            callback = lambda x: self.callback_add_child(x, handle)
            person = gen.lib.Person()
            family = self.dbstate.db.get_family_from_handle(handle)
            father = self.dbstate.db.get_person_from_handle(
                                        family.get_father_handle())
            if father:
                name = father.get_primary_name().get_surname()
                person.get_primary_name().set_surname(name)
            try:
                EditPerson(self.dbstate, self.uistate, [], person, 
                           callback=callback)
            except Errors.WindowActiveError:
                pass

    def callback_add_child(self, person, family_handle):
        ref = gen.lib.ChildRef()
        ref.ref = person.get_handle()
        family = self.dbstate.db.get_family_from_handle(family_handle)
        family.add_child_ref(ref)
        
        trans = self.dbstate.db.transaction_begin()
        #add parentref to child
        person.add_parent_family_handle(family_handle)
        #default relationship is used
        self.dbstate.db.commit_person(person, trans)
        #add child to family
        self.dbstate.db.commit_family(family, trans)
        self.dbstate.db.transaction_commit(trans, _("Add Child to Family"))

    def sel_child_to_fam(self, obj, event, handle, surname=None):
        if button_activated(event, _LEFT_BUTTON):
            SelectPerson = SelectorFactory('Person')
            family = self.dbstate.db.get_family_from_handle(handle)
            # it only makes sense to skip those who are already in the family
            skip_list = [family.get_father_handle(), \
                         family.get_mother_handle()] + \
                        [x.ref for x in family.get_child_ref_list() ]

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

    def select_parents(self, obj):
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

    def add_parents(self, obj):
        family = gen.lib.Family()
        person = self.dbstate.db.get_person_from_handle(self.get_active())

        if not person:
            return

        ref = gen.lib.ChildRef()
        ref.ref = person.handle
        family.add_child_ref(ref)
        
        try:
            EditFamily(self.dbstate, self.uistate, [], family)
        except Errors.WindowActiveError:
            pass
            
    def add_parent_family(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            family = gen.lib.Family()
            person = self.dbstate.db.get_person_from_handle(self.get_active())

            ref = gen.lib.ChildRef()
            ref.ref = person.handle
            family.add_child_ref(ref)
                
            try:
                EditFamily(self.dbstate, self.uistate, [], family)
            except Errors.WindowActiveError:
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
            
    def reorder(self, obj, dumm1=None, dummy2=None):
        if self.get_active():
            try:
                import Reorder
                Reorder.Reorder(self.dbstate, self.uistate, [],
                                self.get_active())
            except Errors.WindowActiveError:
                pass

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
        childlist = family.get_child_ref_list()
        if childlist and len(childlist) > 0:
            return True
    return False

def button_activated(event, mouse_button):
    if (event.type == gtk.gdk.BUTTON_PRESS and \
        event.button == mouse_button) or \
       (event.type == gtk.gdk.KEY_PRESS and \
        event.keyval in (_RETURN, _KP_ENTER)):
        return True
    else:
        return False

