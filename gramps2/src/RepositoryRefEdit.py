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

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
from gtk.gdk import ACTION_COPY, BUTTON1_MASK, INTERP_BILINEAR, pixbuf_new_from_file
from gobject import TYPE_PYOBJECT
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
import AutoComp
import GrampsDisplay

#-------------------------------------------------------------------------
#
# Repository Reference Editor
#
# This is used by both the RepositoryEditor and the SourceEditor
# the UI is slightly different in each case. The subclasses look after
# the difference and the common parts of the UI managed by the base class
#
#-------------------------------------------------------------------------

class RepositoryRefEditBase:

    def __init__(self, reposref, dbstate, update, parent):

        self.dbstate = dbstate
        self.db = dbstate.db
        self.parent = parent
        # FIXME: window manangement
        # if self.parent.__dict__.has_key('child_windows'):
#             self.win_parent = self.parent
#         else:
#             self.win_parent = self.parent.parent
#         if reposref:
#             if self.win_parent.child_windows.has_key(reposref):
#                 self.win_parent.child_windows[reposref].present(None)
#                 return
#             else:
#                 self.win_key = reposref
#         else:
#             self.win_key = self
        self.update = update
        self.repos_ref = reposref
        self.child_windows = {}

    def init_widget(self,top, title):
    
        self.top = top

        Utils.set_titles(self.top,
                         self.top_window.get_widget('title'),
                         title)
        
        self.top_window.signal_autoconnect({
            "on_help_repos_ref_edit_clicked"    : self.on_help_clicked,
            "on_ok_repos_ref_edit_clicked"      : self.on_ok_clicked,
            "on_cancel_repos_ref_edit_clicked"  : self.close,
            "on_repos_ref_edit_delete_event" : self.on_delete_event,
            })
        
        
        self.media_type = self.get_widget("repos_ref_media_type")
        self.media_type_selector = AutoComp.StandardCustomSelector( \
            Utils.source_media_types,self.media_type,
            RelLib.RepoRef.CUSTOM,RelLib.RepoRef.MANUSCRIPT)
        
        self.call_number = self.get_widget("repos_ref_callnumber")
        self.note = self.get_widget("repos_ref_note")

        self.ok = self.get_widget("repos_ref_ok_button")

    def post_init(self):
        self.add_itself_to_menu()
        self.top.show()


    def on_delete_event(self,obj,b):
        self.close_child_windows()
        self.remove_itself_from_menu()

    def close(self,obj):
        self.close_child_windows()
        self.remove_itself_from_menu()
        self.top.destroy()

    def close_child_windows(self):
        for child_window in self.child_windows.values():
            child_window.close(None)
        self.child_windows = {}

    def add_itself_to_menu(self):
        # FIXME
        return
        self.win_parent.child_windows[self.win_key] = self
        label = _('Repository Reference')
        self.parent_menu_item = gtk.MenuItem(label)
        self.parent_menu_item.set_submenu(gtk.Menu())
        self.parent_menu_item.show()
        self.win_parent.winsmenu.append(self.parent_menu_item)
        self.winsmenu = self.parent_menu_item.get_submenu()
        self.menu_item = gtk.MenuItem(_('Repository Information'))
        self.menu_item.connect("activate",self.present)
        self.menu_item.show()
        self.winsmenu.append(self.menu_item)

    def remove_itself_from_menu(self):
        #FIXME
        return
        del self.win_parent.child_windows[self.win_key]
        self.menu_item.destroy()
        self.winsmenu.destroy()
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.top.present()


    def get_widget(self,name):
        """returns the widget associated with the specified name"""
        return self.top_window.get_widget(name)


    def update_display(self,source):
        #self.draw(source,fresh=False)
        pass




class RepositoryRefEdit(RepositoryRefEditBase):

    def __init__(self, reposref, dbstate, update, parent):
        RepositoryRefEditBase.__init__(self, reposref,
                                       dbstate, update,
                                       parent)

        self.top_window = gtk.glade.XML(const.gladeFile,"repositoryRefEditor","gramps")
        self.top = self.top_window.get_widget("repositoryRefEditor")

        self.init_widget(self.top,_('Repository Information'))        
        
        # setup menu
        self.repos_menu = self.get_widget("rep_sel_repository_list")
        cell = gtk.CellRendererText()
        self.repos_menu.pack_start(cell,True)
        self.repos_menu.add_attribute(cell,'text',0)
        self.repos_menu.connect('changed',self.on_source_changed)

        self.type = self.get_widget("repos_ref_type")

        if self.repos_ref:
            handle = self.repos_ref.get_reference_handle()
            self.active_repos = self.db.get_repository_from_handle(handle)
        else:
            self.active_repos = None


        self.draw(self.active_repos,fresh=True)
        self.set_button()
        #if self.parent:
        #    self.top.set_transient_for(self.parent)

        self.db.connect('repository-add', self.rebuild_menu)

        self.top_window.signal_autoconnect({
            "on_add_repos_clicked"            : self.add_repos_clicked
            })

        self.post_init()
        
    def rebuild_menu(self,handle_list):
        self.build_repository_menu(handle_list[0])


    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-si')

    def set_button(self):
        if self.active_repos:
            self.ok.set_sensitive(1)
        else:
            self.ok.set_sensitive(0)
        pass

    def draw(self,sel=None,fresh=False):
        if self.repos_ref and fresh:            
            self.call_number.set_text(self.repos_ref.get_call_number())
            self.note.get_buffer().set_text(self.repos_ref.get_note())

            idval = self.repos_ref.get_reference_handle()
            repos = self.db.get_repository_from_handle(idval)
            self.active_repos = repos
            if repos:
                self.type.set_text(repos.get_type()[1])
            else:
                self.type.set_text("")
            
        self.active_repos = sel
        if sel:
            self.build_repository_menu(sel.get_handle())
        else:
            self.build_repository_menu(None)
        pass

    def build_repository_menu(self,selected_handle):
        keys = self.db.get_repository_handles()
        keys.sort()
        store = gtk.ListStore(str)

        sel_child = None
        index = 0
        sel_index = 0
        self.handle_list = []
        for repos_id in keys:
            repos = self.db.get_repository_from_handle(repos_id)
            name = repos.get_name()
            gid = repos.get_gramps_id()
            store.append(row=["%s [%s]" % (name,gid)])
            self.handle_list.append(repos_id)
            if selected_handle == repos_id:
                sel_index = index
            index += 1
        self.repos_menu.set_model(store)

        if index > 0:
            self.repos_menu.set_sensitive(1)
            self.repos_menu.set_active(sel_index)
        else:
            self.repos_menu.set_sensitive(0)

    def on_ok_clicked(self,obj):
        
        shandle = self.repos_ref.get_reference_handle()
        if self.active_repos != self.db.get_repository_from_handle(shandle):
            self.repos_ref.set_reference_handle(self.active_repos.get_handle())

        # handle type here.
        the_type = self.media_type_selector.get_values()
        if the_type != self.repos_ref.get_media_type():
            self.repos_ref.set_media_type(the_type)
        
        buf = self.note.get_buffer()
        note = unicode(buf.get_text(buf.get_start_iter(),
                                     buf.get_end_iter(),False))
        if note != self.repos_ref.get_note():
            self.repos_ref.set_note(note)
        
        callnumber = unicode(self.call_number.get_text())
        if callnumber != self.repos_ref.get_call_number():
            self.repos_ref.set_call_number(callnumber)

        self.update(self.repos_ref)
        self.close(obj)

    def on_source_changed(self,obj):
        handle = self.handle_list[obj.get_active()]
        self.active_repos = self.db.get_repository_from_handle(handle)
        self.type.set_text(self.active_repos.get_type()[1])
        self.set_button()
        pass

    def add_repos_clicked(self,obj):
        import EditRepository
        EditRepository.EditRepository(RelLib.Repository(),self.dbstate, self)



class RepositoryRefSourceEdit(RepositoryRefEditBase):
    """Edit a Repository Reference from the perspective of the Repository."""

    def __init__(self, reposref, source, dbstate, update, parent):
        RepositoryRefEditBase.__init__(self, reposref,
                                       dbstate, update,
                                       parent)

        self.top_window = gtk.glade.XML(const.gladeFile,"repositoryRefSourceEditor","gramps")
        self.top = self.top_window.get_widget("repositoryRefSourceEditor")

        self.init_widget(self.top,_('Source Information'))        
        
        # setup menu
        self.source_menu = self.get_widget("rep_sel_source_list")
        cell = gtk.CellRendererText()
        self.source_menu.pack_start(cell,True)
        self.source_menu.add_attribute(cell,'text',0)
        self.source_menu.connect('changed',self.on_source_changed)

        self.author = self.get_widget("rep_sel_source_author")
        self.pub_info = self.get_widget("rep_sel_source_pub_info")

        self.original_source = source
        self.active_source = source


        self.draw(self.active_source,fresh=True)
        self.set_button()
        #if self.parent:
        #    self.top.set_transient_for(self.parent)

        self.db.connect('source-add', self.rebuild_menu)
        self.top_window.signal_autoconnect({
            "on_add_source_clicked"            : self.add_source_clicked
            })

        self.post_init()
        
    def rebuild_menu(self,handle_list):
        self.build_source_menu(handle_list[0])


    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-si')

    def set_button(self):
        if self.active_source:
            self.ok.set_sensitive(1)
        else:
            self.ok.set_sensitive(0)
        pass

    def draw(self,sel=None,fresh=False):
        if self.repos_ref and fresh:
            self.call_number.set_text(self.repos_ref.get_call_number())
            self.note.get_buffer().set_text(self.repos_ref.get_note())
            
            if self.active_source:
                self.author.set_text(self.active_source.get_author())
                self.pub_info.set_text(self.active_source.get_publication_info())
        else:
            self.author.set_text("")
            self.pub_info.set_text("")

            
        if sel:
            self.active_source = sel
            self.build_source_menu(sel.get_handle())
        else:
            self.build_source_menu(None)
        pass

    def build_source_menu(self,selected_handle):
        keys = self.db.get_source_handles()
        keys.sort()
        store = gtk.ListStore(str)

        sel_child = None
        index = 0
        sel_index = 0
        self.handle_list = []
        for source_id in keys:
            source = self.db.get_source_from_handle(source_id)
            name = source.get_title()
            gid = source.get_gramps_id()
            store.append(row=["%s [%s]" % (name,gid)])
            self.handle_list.append(source_id)
            if selected_handle == source_id:
                sel_index = index
            index += 1
        self.source_menu.set_model(store)

        if index > 0:
            self.source_menu.set_sensitive(1)
            self.source_menu.set_active(sel_index)
        else:
            self.source_menu.set_sensitive(0)

    def on_ok_clicked(self,obj):

        # handle type here.
        
        buf = self.note.get_buffer()
        note = unicode(buf.get_text(buf.get_start_iter(),
                                     buf.get_end_iter(),False))
        if note != self.repos_ref.get_note():
            self.repos_ref.set_note(note)
        
        callnumber = unicode(self.call_number.get_text())
        if callnumber != self.repos_ref.get_call_number():
            self.repos_ref.set_call_number(callnumber)

        self.update(self.active_source,self.repos_ref,self.original_source)
        self.close(obj)

    def on_source_changed(self,obj):
        source_hdl = self.handle_list[obj.get_active()]
        self.active_source = self.db.get_source_from_handle(source_hdl)
        self.author.set_text(self.active_source.get_author())
        self.pub_info.set_text(self.active_source.get_publication_info())
        self.set_button()
        
    def add_source_clicked(self,obj):
        import EditSource
        EditSource.EditSource(RelLib.Source(),self.dbstate, self.parent)
