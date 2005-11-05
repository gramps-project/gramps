#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2005  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Utils
import RelLib
import ListModel
import NameDisplay
import GrampsDisplay
from WindowUtils import GladeIf

#-------------------------------------------------------------------------
#
# WitnessTab
#
#-------------------------------------------------------------------------
class WitnessTab:
    def __init__(self,srclist,parent,top,window,clist,add_btn,edit_btn,del_btn):
        self.db = parent.db
        self.parent = parent
        self.list = srclist
        self.top = top
        self.window = window
        self.slist = clist
        self.selection = clist.get_selection()
        titles = [ (_('Witness'),0,300),(_('ID'),1,100)]
        self.model = ListModel.ListModel(clist,titles,event_func=self.edit_clicked);

        add_btn.connect('clicked', self.add_clicked)
        edit_btn.connect('clicked', self.edit_clicked)
        del_btn.connect('clicked', self.del_clicked)

        self.redraw()

    def redraw(self):
        self.model.clear()
        for s in self.list:
            if s.get_type() == RelLib.Event.ID:
                handle = s.get_value()
                if self.db.has_person_handle(handle):
                    person = self.db.get_person_from_handle(handle)
                    n = NameDisplay.displayer.sorted(person)
                    the_id = person.get_gramps_id()
                else:
                    n = _('Unknown')
                    the_id = ''
                self.model.add([n,the_id],s)
            else:
                self.model.add([s.get_value(),''],s)
        if self.list:
            Utils.bold_label(self.parent.witnesses_label)
        else:
            Utils.unbold_label(self.parent.witnesses_label)

    def update_clist(self):
        self.redraw()
        self.parent.lists_changed = 1

    def edit_clicked(self,obj):
        store,node = self.selection.get_selected()
        if node:
            objs = self.model.get_selected_objects()
            src = objs[0]
            WitnessEditor(src,self.db,self,self.update_clist,self.window)

    def add_clicked(self,obj):
        WitnessEditor(None,self.db,self,self.update_clist,self.window)

    def add_ref(self,inst,ref):
        self.parent.lists_changed = 1
        inst.list.append(ref)
        inst.redraw()

    def del_clicked(self,obj):
        (store,node) = self.selection.get_selected()
        if node:
            path = store.get_path(node)
            del self.list[path[0]]
            self.redraw()

#-------------------------------------------------------------------------
#
# WitnessEditor
#
#-------------------------------------------------------------------------
class WitnessEditor:

    def __init__(self,ref,database,parent,update=None,parent_window=None):

        self.db = database
        self.parent = parent
        if ref:
            if self.parent.parent.child_windows.has_key(ref):
                self.parent.parent.child_windows[ref].present(None)
                return
            else:
                self.win_key = ref
        else:
            self.win_key = self
        self.update = update
        self.ref = ref
        self.show_witness = gtk.glade.XML(const.dialogFile,
                                          "witness_edit","gramps")
        self.gladeif = GladeIf(self.show_witness)

        self.gladeif.connect('witness_edit','delete_event',
                             self.on_delete_event)
        self.gladeif.connect('cancelbutton1','clicked',self.close)
        self.gladeif.connect('ok','clicked',self.ok_clicked)
        self.gladeif.connect('button132','clicked',self.on_help_clicked)
        self.gladeif.connect('in_db','toggled',self.on_toggled)
        
        self.window = self.show_witness.get_widget('witness_edit')
        self.name = self.show_witness.get_widget("name")
        self.private = self.show_witness.get_widget("priv")
        self.select = self.show_witness.get_widget("select")
        self.select.connect('clicked',self.choose)
        self.ok = self.show_witness.get_widget("ok")
        self.in_db = self.show_witness.get_widget("in_db")
        self.comment = self.show_witness.get_widget("comment")

        if self.ref:
            if self.ref.get_type():
                self.idval = self.ref.get_value()
                if self.db.has_person_handle(self.idval):
                    person = self.db.get_person_from_handle(self.idval)
                    name = NameDisplay.displayer.display(person)
                    self.name.set_text(name)
                    self.in_db.set_active(True)
                else:
                    self.name.set_text(_("Unknown"))
                    self.in_db.set_active(False)
            else:
                self.name.set_text(self.ref.get_value())
                self.in_db.set_active(False)
            self.comment.get_buffer().set_text(self.ref.get_comment())
            self.private.set_active(self.ref.get_privacy())

        self.on_toggled(None)
        Utils.set_titles(self.show_witness.get_widget('witness_edit'),
                         self.show_witness.get_widget('title'),
                         _('Witness Editor'))

        if parent_window:
            self.window.set_transient_for(parent_window)
        self.add_itself_to_menu()
        self.window.show()

    def on_delete_event(self,obj,b):
        self.gladeif.close()
        self.remove_itself_from_menu()
        gc.collect()

    def close(self,obj):
        self.gladeif.close()
        self.remove_itself_from_menu()
        self.window.destroy()
        gc.collect()

    def add_itself_to_menu(self):
        self.parent.parent.child_windows[self.win_key] = self
        self.parent_menu_item = gtk.MenuItem(_('Witness Editor'))
        self.parent_menu_item.connect("activate",self.present)
        self.parent_menu_item.show()
        self.parent.parent.winsmenu.append(self.parent_menu_item)

    def remove_itself_from_menu(self):
        del self.parent.parent.child_windows[self.win_key]
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        GrampsDisplay.help('adv-wit')

    def choose(self,obj):
        import SelectPerson
        sel_person = SelectPerson.SelectPerson(self.db,_('Select Person'),
                                               parent_window=self.window)
        new_person = sel_person.run()
        if new_person:
            self.new_person = new_person
            self.idval = new_person.get_handle()
            new_name = NameDisplay.displayer.display(new_person)
            if new_name:
                self.name.set_text(new_name)
        
    def on_toggled(self,obj):
        if self.in_db.get_active():
            self.name.set_editable(False)
            self.name.set_sensitive(False)
            self.select.set_sensitive(True)
        else:
            self.name.set_editable(True)
            self.name.set_sensitive(True)
            self.select.set_sensitive(False)
        
    def ok_clicked(self,obj):
        if not self.ref:
            if self.in_db.get_active():
                self.ref = RelLib.Witness(RelLib.Event.ID)
            else:
                self.ref = RelLib.Witness(RelLib.Event.NAME)
            self.parent.list.append(self.ref)

        if self.in_db.get_active():
            try:
                self.ref.set_value(self.idval)
                self.ref.set_type(RelLib.Event.ID)
            except AttributeError:
                import QuestionDialog
                QuestionDialog.ErrorDialog(
                            _("Witness selection error"),
                            _("Since you have indicated that the person is "
                            "in the database, you need to actually select "
                            "the person by pressing the Select button.\n\n"
                            "Please try again. The witness has not been changed."),
                            self.window)
        else:
            self.ref.set_value(unicode(self.name.get_text()))
            self.ref.set_type(RelLib.Event.NAME)

        c = self.comment.get_buffer()
        self.ref.set_comment(unicode(c.get_text(c.get_start_iter(),c.get_end_iter(),False)))
        self.ref.set_privacy(self.private.get_active())

        if self.update:
            self.update()
        self.close(obj)
