#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
import gc

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
from gtk.gdk import ACTION_COPY, BUTTON1_MASK, INTERP_BILINEAR, pixbuf_new_from_file
import cPickle as pickle

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import RelLib
import DateEdit
import DateHandler
import GrampsDisplay
import Spell
import DisplayState

from DdTargets import DdTargets
from WindowUtils import GladeIf

#-------------------------------------------------------------------------
#
# SourceEditor
#
#-------------------------------------------------------------------------
class SourceEditor(DisplayState.ManagedWindow):

    def __init__(self, state, uistate, track, srcref, update):

        self.db = state.db 
        self.state = state
        self.track = track
        self.uistate = uistate
        if srcref:
            submenu_label = _('Source Reference')
        else:
            submenu_label = _('New Source Reference')
            
        DisplayState.ManagedWindow.__init__(self, uistate, self.track, srcref)

        self.update = update
        self.source_ref = srcref
        self.showSource = gtk.glade.XML(const.gladeFile,
                                        "sourceDisplay","gramps")
        self.window = self.get_widget("sourceDisplay")

        Utils.set_titles(self.window,
                         self.showSource.get_widget('title'),
                         _('Source Information'))

        self.gladeif = GladeIf(self.showSource)
        self.gladeif.connect('sourceDisplay','delete_event', self.on_delete_event)
        self.gladeif.connect('button95','clicked',self.close)
        self.gladeif.connect('ok','clicked',self.on_sourceok_clicked)
        self.gladeif.connect('button144','clicked', self.on_help_clicked)
        self.gladeif.connect('button143','clicked',self.add_src_clicked)
        addbtn = self.get_widget('button143')
        addbtn.set_sensitive(not self.db.readonly)
        
        self.source_field = self.get_widget("sourceList")

        # setup menu
        self.title_menu = self.get_widget("source_title")
        cell = gtk.CellRendererText()
        self.title_menu.pack_start(cell,True)
        self.title_menu.add_attribute(cell,'text',0)
        self.title_menu.connect('changed',self.on_source_changed)
        self.conf_menu = self.get_widget("conf")
        self.conf_menu.set_sensitive(not self.db.readonly)
        self.private = self.get_widget("priv")
        self.private.set_sensitive(not self.db.readonly)
        self.ok = self.get_widget("ok")
        self.conf_menu.set_active(srcref.get_confidence_level())

        self.author_field = self.get_widget("sauthor")
        self.pub_field = self.get_widget("spubinfo")

        self.date_entry_field = self.get_widget("sdate")
        self.date_entry_field.set_editable(not self.db.readonly)

        if self.source_ref:
            handle = self.source_ref.get_base_handle()
            self.active_source = self.db.get_source_from_handle(handle)
            self.date_obj = self.source_ref.get_date_object()
            date_str = DateHandler.displayer.display(self.date_obj)
            self.date_entry_field.set_text(date_str)
            self.private.set_active(self.source_ref.get_privacy())
        else:
            self.date_obj = RelLib.Date()
            self.active_source = None

        date_stat = self.get_widget("date_stat")
        date_stat.set_sensitive(not self.db.readonly)
        self.date_check = DateEdit.DateEdit(
            self.date_obj, self.date_entry_field,
            date_stat, self.window)

        self.spage = self.get_widget("spage")
        self.spage.set_editable(not self.db.readonly)
        self.scom = self.get_widget("scomment")
        self.scom.set_editable(not self.db.readonly)
        self.spell1 = Spell.Spell(self.scom)
        self.stext = self.get_widget("stext")
        self.stext.set_editable(not self.db.readonly)
        self.spell2 = Spell.Spell(self.stext)

        self.draw(self.active_source,fresh=True)
        self.set_button()
        self.db.connect('source-add', self.rebuild_menu)
        self.show()

    def build_menu_names(self,srcref):
        if srcref:
            submenu_label = _('Source Reference')
        else:
            submenu_label = _('New Source Reference')
        return (_('Source Reference Editor'),submenu_label)

    def rebuild_menu(self,handle_list):
        self.build_source_menu(handle_list[0])

    def on_delete_event(self,obj,b):
        self.gladeif.close()
        gc.collect()

    def close(self,obj):
        self.gladeif.close()
        self.window.destroy()
        gc.collect()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-si')

    def set_button(self):
        if self.active_source:
            self.ok.set_sensitive(not self.db.readonly)
        else:
            self.ok.set_sensitive(False)

    def get_widget(self,name):
        """returns the widget associated with the specified name"""
        return self.showSource.get_widget(name)

    def draw(self,sel=None,fresh=False):
        if self.source_ref and fresh:
            self.spage.get_buffer().set_text(self.source_ref.get_page())

            self.stext.get_buffer().set_text(self.source_ref.get_text())
            self.scom.get_buffer().set_text(self.source_ref.get_note())
            idval = self.source_ref.get_base_handle()
            src = self.db.get_source_from_handle(idval)
            self.active_source = src
            if src:
                self.author_field.set_text(src.get_author())
                self.pub_field.set_text(src.get_publication_info())
        else:
            self.author_field.set_text("")
            self.pub_field.set_text("")
        self.active_source = sel
        if sel:
            self.build_source_menu(sel.get_handle())
        else:
            self.build_source_menu(None)

    def build_source_menu(self,selected_handle):
        keys = self.db.get_source_handles()
        keys.sort(self.db._sortbysource)

        store = gtk.ListStore(str)

        sel_child = None
        index = 0
        sel_index = 0
        self.handle_list = []
        for src_id in keys:
            src = self.db.get_source_from_handle(src_id)
            title = src.get_title()
            gid = src.get_gramps_id()

            if len(title) > 40:
                title = title[0:37] + "..."
            
            store.append(row=["%s [%s]" % (title,gid)])
            self.handle_list.append(src_id)
            if selected_handle == src_id:
                sel_index = index
            index += 1
        self.title_menu.set_model(store)

        if index > 0:
            self.title_menu.set_sensitive(not self.db.readonly)
            self.title_menu.set_active(sel_index)
        else:
            self.title_menu.set_sensitive(0)

    def on_sourceok_clicked(self,obj):

        shandle = self.source_ref.get_base_handle()
        if self.active_source != self.db.get_source_from_handle(shandle):
            self.source_ref.set_base_handle(self.active_source.get_handle())
        
        conf = self.get_widget("conf").get_active()

        buf = self.scom.get_buffer()
        comments = unicode(buf.get_text(buf.get_start_iter(),
                                        buf.get_end_iter(),False))

        buf = self.stext.get_buffer()
        text = unicode(buf.get_text(buf.get_start_iter(),
                                    buf.get_end_iter(),False))

        buf = self.spage.get_buffer()
        page = unicode(buf.get_text(buf.get_start_iter(),
                                    buf.get_end_iter(),False))

        self.source_ref.set_page(page)
        self.source_ref.set_date_object(self.date_obj)
        self.source_ref.set_text(text)
        self.source_ref.set_note(comments)
        self.source_ref.set_confidence_level(conf)
        self.source_ref.set_privacy(self.private.get_active())

        self.update(self.source_ref)
        self.close(obj)

    def on_source_changed(self,obj):
        handle = self.handle_list[obj.get_active()]
        self.active_source = self.db.get_source_from_handle(handle)
        self.author_field.set_text(self.active_source.get_author())
        self.pub_field.set_text(self.active_source.get_publication_info())
        self.set_button()

    def update_display(self,source):
        self.draw(source,fresh=False)

    def add_src_clicked(self,obj):
        import EditSource
        EditSource.EditSource(self.state, self.uistate, self.track, RelLib.Source())
