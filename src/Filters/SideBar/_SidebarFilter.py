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

from gen.ggettext import gettext as _
from bisect import insort_left
import gtk
import pango

from gui import widgets
from gui.dbguielement import DbGUIElement
import config

_RETURN = gtk.gdk.keyval_from_name("Return")
_KP_ENTER = gtk.gdk.keyval_from_name("KP_Enter")

class SidebarFilter(DbGUIElement):
    _FILTER_WIDTH = 200
    _FILTER_ELLIPSIZE = pango.ELLIPSIZE_END

    def __init__(self, dbstate, uistate, namespace):
        self.signal_map = {
            'tag-add'     : self._tag_add,
            'tag-delete'  : self._tag_delete,
            'tag-update'  : self._tag_update,
            'tag-rebuild' : self._tag_rebuild
            }
        DbGUIElement.__init__(self, dbstate.db)

        self.position = 1
        self.table = gtk.Table(4, 11)
        self.table.set_border_width(6)
        self.table.set_row_spacings(6)
        self.table.set_col_spacing(0, 6)
        self.table.set_col_spacing(1, 6)
        self.apply_btn = gtk.Button(stock=gtk.STOCK_FIND)
        self.clear_btn = gtk.Button()
        
        self._init_interface()
        uistate.connect('filters-changed', self.on_filters_changed)
        dbstate.connect('database-changed', self._db_changed)
        self.uistate = uistate
        self.dbstate = dbstate
        self.namespace = namespace
        self.__tag_list = []
        self._tag_rebuild()       

    def _init_interface(self):
        self.table.attach(widgets.MarkupLabel(_('<b>Filter</b>')),
                          0, 2, 0, 1, xoptions=gtk.FILL|gtk.EXPAND, yoptions=0)
        btn = gtk.Button()
        img = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        box = gtk.HBox()
        btn.set_image(img)
        btn.set_relief(gtk.RELIEF_NONE)
        btn.set_alignment(1.0, 0.5)
        box.pack_start(gtk.Label(''), expand=True, fill=True)
        box.pack_end(btn, fill=False, expand=False)
        box.show_all()
        self.table.attach(box, 2, 4, 0, 1, yoptions=0)
        btn.connect('clicked', self.btn_clicked)

        self.create_widget()

        self.apply_btn.connect('clicked', self.clicked)

        hbox = gtk.HBox()
        hbox.show()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_UNDO, gtk.ICON_SIZE_BUTTON)
        image.show()
        label = gtk.Label(_('Reset'))
        label.show()
        hbox.pack_start(image, False, False)
        hbox.pack_start(label, False, True)
        hbox.set_spacing(4)
        
        self.clear_btn.add(hbox)
        self.clear_btn.connect('clicked', self.clear)

        hbox = gtk.HBox()
        hbox.set_spacing(6)
        hbox.add(self.apply_btn)
        hbox.add(self.clear_btn)
        hbox.show()
        self.table.attach(hbox, 2, 4, self.position, self.position+1,
                          xoptions=gtk.FILL, yoptions=0)

    def btn_clicked(self, obj):
        config.set('interface.filter', False)
        config.save()

    def get_widget(self):
        return self.table

    def create_widget(self):
        pass

    def clear(self, obj):
        pass

    def clicked(self, obj):
        self.uistate.set_busy_cursor(1)
        self.clicked_func()
        self.uistate.set_busy_cursor(0)

    def clicked_func(self):
        pass

    def get_filter(self):
        pass

    def add_text_entry(self, name, widget, tooltip=None):
        self.add_entry(name, widget)
        widget.connect('key-press-event', self.key_press)
        if tooltip:
            widget.set_tooltip_text(tooltip)

    def key_press(self, obj, event):
        if not event.state or event.state in (gtk.gdk.MOD2_MASK,):
            if event.keyval in (_RETURN, _KP_ENTER):
                self.clicked(obj)
        return False

    def add_entry(self, name, widget):
        if name:
            self.table.attach(widgets.BasicLabel(name),
                              1, 2, self.position, self.position+1,
                              xoptions=gtk.FILL, yoptions=0)
        self.table.attach(widget, 2, 4, self.position, self.position+1,
                          xoptions=gtk.FILL, yoptions=0)
        self.position += 1

    def on_filters_changed(self, namespace):
        """
        Called when filters are changed.
        """
        pass
        
    def _db_changed(self, db):
        """
        Called when the database is changed.
        """
        self._change_db(db)
        self.on_db_changed(db)
        self._tag_rebuild()

    def on_db_changed(self, db):
        """
        Called when the database is changed.
        """
        pass

    def _connect_db_signals(self):
        """
        Connect database signals defined in the signal map.
        """
        for sig in self.signal_map:
            self.callman.add_db_signal(sig, self.signal_map[sig])        

    def _tag_add(self, handle_list):
        """
        Called when tags are added.
        """
        for handle in handle_list:
            tag = self.dbstate.db.get_tag_from_handle(handle)
            insort_left(self.__tag_list, (tag.get_name(), handle))
        self.on_tags_changed([item[0] for item in self.__tag_list])
        
    def _tag_update(self, handle_list):
        """
        Called when tags are updated.
        """
        for handle in handle_list:
            item = [item for item in self.__tag_list if item[1] == handle][0]
            self.__tag_list.remove(item)
            tag = self.dbstate.db.get_tag_from_handle(handle)
            insort_left(self.__tag_list, (tag.get_name(), handle))
        self.on_tags_changed([item[0] for item in self.__tag_list])
        
    def _tag_delete(self, handle_list):
        """
        Called when tags are deleted.
        """
        for handle in handle_list:
            tag = self.dbstate.db.get_tag_from_handle(handle)
            self.__tag_list.remove((tag.get_name(), handle))
        self.on_tags_changed([item[0] for item in self.__tag_list])
        
    def _tag_rebuild(self):
        """
        Called when the tag list needs to be rebuilt.
        """
        self.__tag_list = []
        for handle in self.dbstate.db.get_tag_handles():
            tag = self.dbstate.db.get_tag_from_handle(handle)
            self.__tag_list.append((tag.get_name(), handle))
        self.on_tags_changed([item[0] for item in self.__tag_list])
        
    def on_tags_changed(self, tag_list):
        """
        Called when tags are changed.
        """
        pass

    def add_filter_entry(self, text, widget):
        """
        Adds the text and widget to GUI, with an Edit button.
        """
        hbox = gtk.HBox()
        hbox.pack_start(widget)
        hbox.pack_start(widgets.SimpleButton(gtk.STOCK_EDIT, self.edit_filter))
        self.add_entry(text, hbox)

    def edit_filter(self, obj):
        """
        Callback which invokes the EditFilter dialog. Will create new
        filter if called if none is selected.
        """
        from gui.filtereditor import EditFilter
        from Filters import FilterList, GenericFilterFactory
        import const
        the_filter = None
        filterdb = FilterList(const.CUSTOM_FILTERS)
        filterdb.load()
        if self.generic.get_active() != 0:
            model = self.generic.get_model()
            node = self.generic.get_active_iter()
            if node:
                sel_filter = model.get_value(node, 1)
                # the_filter needs to be a particular object for editor
                for filt in filterdb.get_filters(self.namespace):
                    if filt.get_name() == sel_filter.get_name():
                        the_filter = filt
        else:
            the_filter = GenericFilterFactory(self.namespace)()
        if the_filter:
            EditFilter(self.namespace, self.dbstate, self.uistate, [],
                       the_filter, filterdb,
                       lambda : self.edit_filter_save(filterdb))

    def edit_filter_save(self, filterdb):
        """
        If a filter changed, save them all. Reloads, and also calls callback.
        """
        from Filters import reload_custom_filters
        filterdb.save()
        reload_custom_filters()
        self.on_filters_changed(self.namespace)
