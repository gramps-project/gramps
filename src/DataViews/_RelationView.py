# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
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
import cgi

try:
    set()
except:
    from sets import Set as set
    
#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import RelLib
import PageView
import NameDisplay
import DateHandler
import ImgManip
import Config
import GrampsWidgets
import Errors
import GrampsDb

from ReportBase import ReportUtils

_GenderCode = {
    RelLib.Person.MALE    : u'\u2642', 
    RelLib.Person.FEMALE  : u'\u2640', 
    RelLib.Person.UNKNOWN : u'\u2650', 
    }

_NAME_START   = 0
_LABEL_START  = 1
_LABEL_STOP   = 2
_DATA_START   = _LABEL_STOP
_DATA_STOP    = _DATA_START+1
_BTN_START    = _DATA_STOP
_BTN_STOP     = _BTN_START+2
_PLABEL_START = 2
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
_ALABEL_START = 1
_ALABEL_STOP  = _ALABEL_START+1
_ADATA_START  = _ALABEL_STOP
_ADATA_STOP   = _ADATA_START+3
_SDATA_START  = 3
_SDATA_STOP   = 5

class AttachList:

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

class RelationshipView(PageView.PersonNavView):

    def __init__(self, dbstate, uistate):
        
        PageView.PersonNavView.__init__(
            self, _('Relationships'), dbstate, uistate)
        
        dbstate.connect('database-changed', self.change_db)
        self.show_siblings = Config.get(Config.FAMILY_SIBLINGS)
        self.show_details = Config.get(Config.FAMILY_DETAILS)
        self.connect_to_db(dbstate.db)
        self.redrawing = False
        self.use_shade = Config.get(Config.RELATION_SHADE)
        self.toolbar_visible = Config.get(Config.TOOLBAR_ON)
        self.color = gtk.TextView().style.white
        self.child = None
        Config.client.notify_add("/apps/gramps/preferences/relation-shade",
                                 self.shade_update)
        Config.client.notify_add("/apps/gramps/interface/editbutton",
                                 self.config_update)
        Config.client.notify_add("/apps/gramps/interface/toolbar-on",
                                 self.shade_update)
	self.reorder_sensitive = False

    def set_active(self):
        PageView.PersonNavView.set_active(self)
        self.key_active_changed = self.dbstate.connect('active-changed',
                                                       self.redraw)
        self.build_tree()
    
    def set_inactive(self):
        PageView.PersonNavView.set_inactive(self)
        self.dbstate.disconnect(self.key_active_changed)
        
    def shade_update(self, client, cnxn_id, entry, data):
        self.use_shade = Config.get(Config.RELATION_SHADE)
        self.toolbar_visible = Config.get(Config.TOOLBAR_ON)
        self.uistate.modify_statusbar(self.dbstate)
        self.redraw()

    def config_update(self, client, cnxn_id, entry, data):
        self.redraw()

    def build_tree(self):
        self.redraw()
            
    def connect_to_db(self, db):
        db.connect('person-update', self.person_update)
        db.connect('person-rebuild', self.person_rebuild)
        db.connect('family-update', self.family_update)
        db.connect('family-add',    self.family_add)
        db.connect('family-delete', self.family_delete)
        db.connect('family-rebuild', self.family_rebuild)

    def person_update(self, handle_list):
        if self.dbstate.active:
            while not self.change_person(self.dbstate.active.handle):
                pass
        else:
            self.change_person(None)

    def person_rebuild(self):
        if self.dbstate.active:
            while not self.change_person(self.dbstate.active.handle):
                pass
        else:
            self.change_person(None)

    def family_update(self, handle_list):
        if self.dbstate.active:
            while not self.change_person(self.dbstate.active.handle):
                pass
        else:
            self.change_person(None)

    def family_add(self, handle_list):
        if self.dbstate.active:
            while not self.change_person(self.dbstate.active.handle):
                pass
        else:
            self.change_person(None)

    def family_delete(self, handle_list):
        if self.dbstate.active:
            while not self.change_person(self.dbstate.active.handle):
                pass
        else:
            self.change_person(None)

    def family_rebuild(self):
        if self.dbstate.active:
            while not self.change_person(self.dbstate.active.handle):
                pass
        else:
            self.change_person(None)
            
    def get_stock(self):
        """
        Returns the name of the stock icon to use for the display.
        This assumes that this icon has already been registered with
        GNOME as a stock icon.
        """
        return 'gramps-family'

    def build_widget(self):

        container = gtk.VBox()
        container.set_border_width(12)

        self.vbox = gtk.VBox()
        self.vbox.show()

        self.header = gtk.VBox()
        self.header.show()

        self.child = None

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.show()
        
        vp = gtk.Viewport()
        vp.set_shadow_type(gtk.SHADOW_NONE)
        vp.add(self.vbox)

        scroll.add(vp)
        scroll.show_all()

        container.set_spacing(6)
        container.pack_start(self.header, False, False)
        container.pack_start(gtk.HSeparator(), False, False)
        container.add(scroll)
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
              <menuitem action="AddParents"/>
              <menuitem action="AddSpouse"/>
              <menuitem action="ShareFamily"/>
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
        PageView.PersonNavView.define_actions(self)

        self.order_action = gtk.ActionGroup(self.title + '/ChangeOrder')
        self.order_action.add_actions([
            ('ChangeOrder', gtk.STOCK_SORT_ASCENDING, _('_Reorder'), None ,
	     _("Reorder the relationships"), self.reorder),
            ])

        self.family_action = gtk.ActionGroup(self.title + '/Family')
        self.family_action.add_actions([
            ('AddSpouse', 'gramps-spouse', _('Add Spouse'), None ,
	     _("Adds a new relationship"), self.add_spouse),
            ('AddParents', 'gramps-parents', _('Add Parents'), None ,
	     _("Adds a new set of parents"), self.add_parents),
            ('ShareFamily', 'gramps-sharefamily', _('Share Parents'), None ,
	     _("Adds an existing set of parents"), self.select_parents),
            ])

        self.add_action_group(self.order_action)
        self.add_action_group(self.family_action)

        self.add_toggle_action('Details', None, _('Show details'), 
                               None, None, self.details_toggle, 
                               self.show_details)
        self.add_toggle_action('Siblings', None, _('Show siblings'), 
                               None, None, self.siblings_toggle, 
                               self.show_siblings)

	self.order_action.set_sensitive(self.reorder_sensitive)

    def siblings_toggle(self, obj):
        self.show_siblings = obj.get_active()
        self.change_person(self.dbstate.active.handle)
        Config.set(Config.FAMILY_SIBLINGS,self.show_siblings)

    def details_toggle(self, obj):
        self.show_details = obj.get_active()
        self.change_person(self.dbstate.active.handle)
        Config.set(Config.FAMILY_DETAILS,self.show_details)

    def change_db(self, db):
        self.connect_to_db(db)
        if self.child:
            for old_child in self.vbox.get_children():
                self.vbox.remove(old_child)
            for old_child in self.header.get_children():
                self.header.remove(old_child)
            self.child = None
        self.dbstate.db.connect('family-update', self.redraw)
        self.dbstate.db.connect('family-add', self.redraw)
        self.dbstate.db.connect('family-delete', self.redraw)
        self.dbstate.db.connect('person-update', self.redraw)
        self.dbstate.db.connect('person-add', self.redraw)
        self.dbstate.db.connect('person-delete', self.redraw)
        self.bookmarks.update_bookmarks(db.get_bookmarks())
        self.bookmarks.redraw()
        self.redraw()

    def get_name(self, handle, use_gender=False):
        if handle:
            p = self.dbstate.db.get_person_from_handle(handle)
            name = NameDisplay.displayer.display(p)
            if use_gender:
                gender = _GenderCode[p.gender]
            else:
                gender = ""
            return (name, gender)
        else:
            return (_(u"Unknown"), "")

    def redraw(self, *obj):
        if self.dbstate.active:
            self.handle_history(self.dbstate.active.handle)
            self.change_person(self.dbstate.active.handle)
        else:
            self.change_person(None)
        
    def change_person(self, obj):
        if self.redrawing:
            return False
        self.redrawing = True
        self.tooltips = gtk.Tooltips()

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
                    self.write_parents(family_handle)
        else:
            self.write_label("%s:" % _('Parents'), None, True)
            self.row += 1
                
        family_handle_list = person.get_family_handle_list()
	
        if not self.reorder_sensitive:
            self.reorder_sensitive = len(family_handle_list)> 1

        if family_handle_list:
            for family_handle in family_handle_list:
                if family_handle:
                    self.write_family(family_handle)
        else:
            self.write_label("%s:" % _('Family'), None, False)
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
        self.child.set_row_spacings(9)

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
        self.redrawing = False
        self.uistate.modify_statusbar(self.dbstate)

        self.order_action.set_sensitive(self.reorder_sensitive)

        return True

    def write_title(self, person):

        for old_child in self.header.get_children():
            self.header.remove(old_child)

        table = gtk.Table(2,3)
        table.set_col_spacings(12)
        table.set_row_spacings(6)
        
        # name and edit button
        name = NameDisplay.displayer.display(person)
        fmt = '<span size="larger" weight="bold">%s</span>'
        text = fmt % cgi.escape(name)
        label = GrampsWidgets.DualMarkupLabel(text, _GenderCode[person.gender])
        if Config.get(Config.RELEDITBTN):
            button = GrampsWidgets.IconButton(self.edit_button_press,person.handle)
            self.tooltips.set_tip(button,_('Edit %s') % name)
        else:
            button = None
        hbox = GrampsWidgets.LinkBox(label, button)

        table.attach(hbox, 0, 2, 0, 1)

        eventbox = gtk.EventBox()
        if self.use_shade:
            eventbox.modify_bg(gtk.STATE_NORMAL, self.color)
        table.attach(eventbox, 1, 2, 1, 2)
        subtbl = gtk.Table(3, 3)
        subtbl.set_col_spacings(12)
        subtbl.set_row_spacings(6)
        eventbox.add(subtbl)
                
        # GRAMPS ID

        subtbl.attach(GrampsWidgets.BasicLabel("%s:" % _('ID')),
                      1, 2, 0, 1, xoptions=gtk.FILL, yoptions=0)
        subtbl.attach(GrampsWidgets.BasicLabel(person.gramps_id),
                      2, 3, 0, 1, yoptions=0)

        # Birth event.
        birth = ReportUtils.get_birth_or_fallback(self.dbstate.db,person)
        if birth:
            birth_title = birth.get_type()
        else:
            birth_title = _("Birth")

        subtbl.attach(GrampsWidgets.BasicLabel("%s:" % birth_title),
                      1, 2, 1, 2, xoptions=gtk.FILL, yoptions=0)
        subtbl.attach(GrampsWidgets.BasicLabel(self.format_event(birth)),
                      2, 3, 1, 2, yoptions=0)

        death = ReportUtils.get_death_or_fallback(self.dbstate.db,person)
        if death:
            death_title = death.get_type()
        else:
            death_title = _("Death")

        subtbl.attach(GrampsWidgets.BasicLabel("%s:" % death_title),
                      1, 2, 2, 3, xoptions=gtk.FILL, yoptions=0)
        subtbl.attach(GrampsWidgets.BasicLabel(self.format_event(death)),
                      2, 3, 2, 3, yoptions=0)


        mbox = gtk.HBox()
        mbox.add(table)

        # image
        image_list = person.get_media_list()
        if image_list:
            mobj = self.dbstate.db.get_object_from_handle(image_list[0].ref)
            if mobj.get_mime_type()[0:5] == "image":
                pixbuf = ImgManip.get_thumbnail_image(mobj.get_path())
                image = gtk.Image()
                image.set_from_pixbuf(pixbuf)
                image.show()
                mbox.pack_end(image,False)

        mbox.show_all()
        self.header.pack_start(mbox,False)

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
        self.attach.attach(GrampsWidgets.BasicLabel(title), _ALABEL_START, 
                           _ALABEL_STOP, self.row, self.row+1, 
                           xoptions=gtk.FILL|gtk.SHRINK)
        self.attach.attach(GrampsWidgets.BasicLabel(data), 
                           _ADATA_START, _ADATA_STOP, 
                           self.row, self.row+1)
        self.row += 1

    def write_label(self, title, family, is_parent):
        msg = "<i><b>%s</b></i>" % cgi.escape(title)
        self.attach.attach(GrampsWidgets.MarkupLabel(msg), 
                           _LABEL_START, _LABEL_STOP, 
                           self.row, self.row+1, gtk.SHRINK|gtk.FILL)

        if family:
            value = family.gramps_id
        else:
            value = ""
        self.attach.attach(GrampsWidgets.BasicLabel(value), 
                           _DATA_START, _DATA_STOP, 
                           self.row, self.row+1, gtk.SHRINK|gtk.FILL)

        hbox = gtk.HBox()
        hbox.set_spacing(12)
        if is_parent:
            call_fcn = self.add_parent_family
            del_fcn = self.delete_parent_family
            add_msg = _('Add parents')
            sel_msg = _('Select existing parents')
            edit_msg = _('Edit parents')
            del_msg = _('Remove parents')
        else:
            add_msg = _('Add spouse')
            sel_msg = _('Select spouse')
            edit_msg = _('Edit family')
            del_msg = _('Remove from family')
            call_fcn = self.add_family
            del_fcn = self.delete_family
        
        if not self.toolbar_visible:
            # Show edit-Buttons if toolbar is not visible
            if self.reorder_sensitive:
                add = GrampsWidgets.IconButton(self.reorder, None, 
					       gtk.STOCK_SORT_ASCENDING)
                self.tooltips.set_tip(add, _('Reorder families'))
                hbox.pack_start(add, False)

            add = GrampsWidgets.IconButton(call_fcn, None, gtk.STOCK_ADD)
            self.tooltips.set_tip(add, add_msg)
            hbox.pack_start(add, False)
    
            if is_parent:
                add = GrampsWidgets.IconButton(self.select_family, None, gtk.STOCK_INDEX)
                self.tooltips.set_tip(add, sel_msg)
                hbox.pack_start(add, False)

        if family:
            edit = GrampsWidgets.IconButton(self.edit_family, family.handle, 
                                            gtk.STOCK_EDIT)
            self.tooltips.set_tip(edit, edit_msg)
            hbox.pack_start(edit, False)
            delete = GrampsWidgets.IconButton(del_fcn, family.handle, 
                                              gtk.STOCK_REMOVE)
            self.tooltips.set_tip(delete, del_msg)
            hbox.pack_start(delete, False)
        self.attach.attach(hbox, _BTN_START, _BTN_STOP, self.row, self.row+1)
        self.row += 1
        
######################################################################

    def write_parents(self, family_handle):
        family = self.dbstate.db.get_family_from_handle(family_handle)
        if not family:
            return
        self.write_label("%s:" % _('Parents'), family, True)
        self.write_person(_('Father'), family.get_father_handle())
        self.write_person(_('Mother'), family.get_mother_handle())

        if self.show_siblings:
            active = self.dbstate.active.handle

            child_list = [ref.ref for ref in family.get_child_ref_list()\
                          if ref.ref != active]

            if child_list:
                eventbox = gtk.EventBox()
                if self.use_shade:
                    eventbox.modify_bg(gtk.STATE_NORMAL, self.color)
                vbox = gtk.VBox()
                label_cell = self.build_label_cell(_('Siblings'))
                label_cell.set_alignment(0, 0)
                self.attach.attach(
                    label_cell, _CLABEL_START, _CLABEL_STOP, self.row, 
                    self.row+1, xoptions=gtk.FILL|gtk.SHRINK,
                    yoptions=gtk.FILL)

                i = 1
                for child_handle in child_list:
                    self.write_child(vbox, child_handle, i)
                    i += 1

                eventbox.add(vbox)
                self.attach.attach(
                    eventbox, _CDATA_START, _CDATA_STOP, self.row,
                    self.row+1)
                
        self.row += 1

    def write_person(self, title, handle):
        if title:
            format = '<span weight="bold">%s: </span>'
        else:
            format = "%s"

        label = GrampsWidgets.MarkupLabel(format % cgi.escape(title))
        label.set_alignment(0,0)
        if Config.get(Config.RELEDITBTN):
            label.set_padding(0,5)
        self.attach.attach(label, _PLABEL_START, _PLABEL_STOP, self.row, 
                           self.row+1, xoptions=gtk.FILL|gtk.SHRINK,
                           yoptions=gtk.FILL|gtk.SHRINK)

        vbox = gtk.VBox()
        
        if handle:
            name = self.get_name(handle, True)
            link_label = GrampsWidgets.LinkLabel(name, 
                                                 self.button_press, handle)
            if self.use_shade:
                link_label.modify_bg(gtk.STATE_NORMAL, self.color)
            if Config.get(Config.RELEDITBTN):
                button = GrampsWidgets.IconButton(self.edit_button_press, handle)
                self.tooltips.set_tip(button, _('Edit %s') % name[0])
            else:
                button = None
            vbox.pack_start(GrampsWidgets.LinkBox(link_label, button))
        else:
            link_label = gtk.Label(_('Unknown'))
            link_label.set_alignment(0, 1)
            link_label.show()
            vbox.pack_start(link_label)
            
        if self.show_details:
            value = self.info_string(handle)
            if value:
                vbox.pack_start(GrampsWidgets.MarkupLabel(value))

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

        lbl = GrampsWidgets.MarkupLabel(format % cgi.escape(title))
        if Config.get(Config.RELEDITBTN):
            lbl.set_padding(0,5)
        return lbl

    def write_child(self, vbox, handle, index):
        link_label = GrampsWidgets.LinkLabel(self.get_name(handle, True),
                                             self.button_press, handle)
        if self.use_shade:
            link_label.modify_bg(gtk.STATE_NORMAL, self.color)
        link_label.set_padding(3, 0)
        if Config.get(Config.RELEDITBTN):
            button = GrampsWidgets.IconButton(self.edit_button_press, handle)
        else:
            button = None

        hbox = gtk.HBox()
        hbox.pack_start(GrampsWidgets.BasicLabel("%d." % index),
                        False, False, 0)
        hbox.pack_start(GrampsWidgets.LinkBox(link_label, button),
                        False, False, 4)
        hbox.show()
        vbox.pack_start(hbox)

        if self.show_details:
            value = self.info_string(handle)
            if value:
                l = GrampsWidgets.MarkupLabel(value)
                l.set_padding(16, 0)
                vbox.add(l)
        
    def write_data(self, box, title, start_col=_SDATA_START,
                   stop_col=_SDATA_STOP):
        box.add(GrampsWidgets.BasicLabel(title))

    def info_string(self, handle):
        child = self.dbstate.db.get_person_from_handle(handle)
        if not child:
            return None

        birth = ReportUtils.get_birth_or_fallback(self.dbstate.db, child)
        if birth and birth.get_type != RelLib.EventType.BIRTH:
            bdate  = "<i>%s</i>" % DateHandler.get_date(birth)
        elif birth:
            bdate  = DateHandler.get_date(birth)
        else:
            bdate = ""

        death = ReportUtils.get_death_or_fallback(self.dbstate.db, child)
        if death and death.get_type != RelLib.EventType.DEATH:
            ddate  = "<i>%s</i>" % DateHandler.get_date(death)
        elif death:
            ddate  = DateHandler.get_date(death)
        else:
            ddate = ""

        if bdate and ddate:
            value = _("b. %s, d. %s") % (bdate, ddate)
        elif bdate:
            value = _("b. %s") % (bdate)
        elif ddate:
            value = _("d. %s") % (ddate)
        else:
            value = ""
        return value

    def button_press(self, obj, event, handle):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            self.dbstate.change_active_handle(handle)
	elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
	    myMenu = gtk.Menu()
	    myMenu.append(self.build_menu_item(handle))
	    myMenu.popup(None, None, None, event.button, event.time)

    def build_menu_item(self, handle):
	person = self.dbstate.db.get_person_from_handle(handle)
	name = NameDisplay.displayer.display(person)

	item = gtk.ImageMenuItem(None)
	image = gtk.image_new_from_stock(gtk.STOCK_EDIT, gtk.ICON_SIZE_MENU)
	image.show()
	label = gtk.Label(_("Edit %s") % name)
	label.show()
	label.set_alignment(0,0)

	item.set_image(image)
	item.add(label)

	item.connect('activate',self.edit_menu, handle)
	item.show()
	return item

    def edit_menu(self, obj, handle):
	from Editors import EditPerson
	person = self.dbstate.db.get_person_from_handle(handle)
	try:
	    EditPerson(self.dbstate, self.uistate, [], person)
	except Errors.WindowActiveError:
	    pass

    def write_relationship(self, box, family):
        msg = _('Relationship type: %s') % str(family.get_relationship())
        box.add(GrampsWidgets.MarkupLabel(msg))

    def place_name(self, handle):
        p = self.dbstate.db.get_place_from_handle(handle)
        return p.get_title()

    def write_marriage(self, vbox, family):
        value = False
        for event_ref in family.get_event_ref_list():
            handle = event_ref.ref
            event = self.dbstate.db.get_event_from_handle(handle)
            if event.get_type() == RelLib.EventType.MARRIAGE:
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

    def write_family(self, family_handle):
        family = self.dbstate.db.get_family_from_handle(family_handle)
        if family == None:
            from QuestionDialog import WarningDialog
            WarningDialog(
                _('Broken family detected'),
                _('Please run the Check and Repair Database tool'))
            return
        
        father_handle = family.get_father_handle()
        mother_handle = family.get_mother_handle()
        if self.dbstate.active.handle == father_handle:
            handle = mother_handle
        else:
            handle = father_handle

        self.write_label("%s:" % _('Family'), family, False)
        if handle:
            box = self.write_person(_('Spouse'), handle)

            if not self.write_marriage(box, family):
                self.write_relationship(box, family)
        
        child_list = family.get_child_ref_list()
        if child_list:
            eventbox = gtk.EventBox()
            if self.use_shade:
                eventbox.modify_bg(gtk.STATE_NORMAL, self.color)
            vbox = gtk.VBox()
            label_cell = self.build_label_cell(_('Children'))
            label_cell.set_alignment(0,0)
            self.attach.attach(
                label_cell, _CLABEL_START, _CLABEL_STOP, self.row, 
                self.row+1, xoptions=gtk.FILL|gtk.SHRINK,
                yoptions=gtk.FILL)

            i = 1
            for child_ref in child_list:
                self.write_child(vbox, child_ref.ref, i)
                i += 1

            eventbox.add(vbox)
            self.attach.attach(
                eventbox, _CDATA_START, _CDATA_STOP, self.row,
                self.row+1)

        self.row += 1

    def edit_button_press(self, obj, event, handle):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            from Editors import EditPerson
            person = self.dbstate.db.get_person_from_handle(handle)
            try:
                EditPerson(self.dbstate, self.uistate, [], person)
            except Errors.WindowActiveError:
                pass
        
    def edit_person(self, obj, handle):
        from Editors import EditPerson
        person = self.dbstate.db.get_person_from_handle(handle)
        try:
            EditPerson(self.dbstate, self.uistate, [], person)
        except Errors.WindowActiveError:
            pass

    def edit_family(self, obj, event, handle):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            from Editors import EditFamily
            family = self.dbstate.db.get_family_from_handle(handle)
            try:
                EditFamily(self.dbstate, self.uistate, [], family)
            except Errors.WindowActiveError:
                pass

    def add_family(self, obj, event, handle):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            from Editors import EditFamily
            family = RelLib.Family()
            person = self.dbstate.active
            
            if person.gender == RelLib.Person.MALE:
                family.set_father_handle(person.handle)
            else:
                family.set_mother_handle(person.handle)
                
            try:
                EditFamily(self.dbstate, self.uistate, [], family)
            except Errors.WindowActiveError:
                pass

    def add_spouse(self, obj):
        from Editors import EditFamily
        family = RelLib.Family()
        person = self.dbstate.active
            
        if person.gender == RelLib.Person.MALE:
            family.set_father_handle(person.handle)
        else:
            family.set_mother_handle(person.handle)
                
        try:
            EditFamily(self.dbstate, self.uistate, [], family)
        except Errors.WindowActiveError:
            pass

    def select_family(self, obj, event, handle):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            from Selectors import selector_factory
            SelectFamily = selector_factory('Family')

            phandle = self.dbstate.get_active_person().handle
            person = self.dbstate.db.get_person_from_handle(phandle)
            skip = set(person.get_family_handle_list())
            
            dialog = SelectFamily(self.dbstate, self.uistate, skip=skip)
            family = dialog.run()

            if family:
                active_handle = self.dbstate.active.handle
                child = self.dbstate.db.get_person_from_handle(active_handle)

                GrampsDb.add_child_to_family(
                    self.dbstate.db,
                    family,
                    child)

    def select_parents(self, obj):
        from Selectors import selector_factory
        SelectFamily = selector_factory('Family')

        phandle = self.dbstate.get_active_person().handle
        person = self.dbstate.db.get_person_from_handle(phandle)
        skip = set(person.get_family_handle_list())
            
        dialog = SelectFamily(self.dbstate, self.uistate, skip=skip)
        family = dialog.run()

        if family:
            active_handle = self.dbstate.active.handle
            child = self.dbstate.db.get_person_from_handle(active_handle)
            
            GrampsDb.add_child_to_family(
                self.dbstate.db,
                family,
                child)

    def add_parents(self, obj):
        from Editors import EditFamily
        family = RelLib.Family()
        person = self.dbstate.active

        ref = RelLib.ChildRef()
        ref.ref = person.handle
        family.add_child_ref(ref)
        
        try:
            EditFamily(self.dbstate, self.uistate, [], family)
        except Errors.WindowActiveError:
            pass
            
    def add_parent_family(self, obj, event, handle):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            from Editors import EditFamily
            family = RelLib.Family()
            person = self.dbstate.active

            ref = RelLib.ChildRef()
            ref.ref = person.handle
            family.add_child_ref(ref)
                
            try:
                EditFamily(self.dbstate, self.uistate, [], family)
            except Errors.WindowActiveError:
                pass

    def delete_family(self, obj, event, handle):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            GrampsDb.remove_parent_from_family(self.dbstate.db, 
                                               self.dbstate.active.handle, 
                                               handle)

    def delete_parent_family(self, obj, event, handle):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            GrampsDb.remove_child_from_family(self.dbstate.db, 
                                              self.dbstate.active.handle, 
                                              handle)

    def change_to(self, obj, handle):
        self.dbstate.change_active_handle(handle)

    def reorder(self,obj,dumm1=None,dummy2=None):
        if self.dbstate.active:
            try:
		import Reorder
		Reorder.Reorder(self.dbstate, self.uistate, [],
				self.dbstate.active.handle)
            except Errors.WindowActiveError:
                pass
