#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gobject
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
from intl import gettext as _

#-------------------------------------------------------------------------
#
# WitnessTab
#
#-------------------------------------------------------------------------
class WitnessTab:
    def __init__(self,srclist,parent,top,clist,add_btn,edit_btn,del_btn):
        self.db = parent.db
        self.parent = parent
        self.list = srclist
        self.top = top
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
                id = s.get_value()
                if self.db.getPersonMap().has_key(id):
                    n = self.db.getPerson(id).getPrimaryName().getName()
                else:
                    n = _('Unknown')
                self.model.add([n,s.get_value()],s)
            else:
                self.model.add([s.get_value(),''],s)

    def update_clist(self):
        self.redraw()
        self.parent.lists_changed = 1

    def edit_clicked(self,obj):
        store,iter = self.selection.get_selected()
        if iter:
            objs = self.model.get_selected_objects()
            src = objs[0]
            WitnessEditor(src,self.db,self.update_clist,self)

    def add_clicked(self,obj):
        WitnessEditor(None,self.db,self.update_clist,self)

    def add_ref(self,inst,ref):
        self.parent.lists_changed = 1
        inst.list.append(ref)
        inst.redraw()

    def del_clicked(self,obj):
        (store,iter) = self.selection.get_selected()
        if iter:
            path = store.get_path(iter)
            del self.list[path[0]]
            self.redraw()

#-------------------------------------------------------------------------
#
# WitnessEditor
#
#-------------------------------------------------------------------------
class WitnessEditor:

    def __init__(self,ref,database,update=None,parent=None):

        self.db = database
        self.parent = parent
        self.update = update
        self.ref = ref
        self.show_witness = gtk.glade.XML(const.dialogFile, "witness_edit")
        self.show_witness.signal_autoconnect({
            "ok_clicked"   : self.ok_clicked,
            "on_toggled"   : self.on_toggled,
            "on_id_changed" : self.on_id_changed,
            "cancel_clicked" : self.cancel_clicked,
            })

        self.name = self.show_witness.get_widget("name")
        self.id = self.show_witness.get_widget("id")
        self.ok = self.show_witness.get_widget("ok")
        self.in_db = self.show_witness.get_widget("in_db")
        self.comment = self.show_witness.get_widget("comment")

        if self.ref:
            if self.ref.get_type():
                self.id.set_text(self.ref.get_value())
                self.in_db.set_active(1)
            else:
                self.name.set_text(self.ref.get_value())
                self.in_db.set_active(0)
            self.comment.get_buffer().set_text(self.ref.get_comment())

        self.on_toggled(None)
        Utils.set_titles(self.show_witness.get_widget('witness_edit'),
                         self.show_witness.get_widget('title'),
                         _('Witness Editor'))

    def on_id_changed(self,obj):
        self.check_valid_id()
        
    def check_valid_id(self):
        if self.in_db.get_active():
            id = self.id.get_text()
            if self.db.getPersonMap().has_key(id):
                person = self.db.getPerson(id)
                self.name.set_text(person.getPrimaryName().getName())
                self.ok.set_sensitive(1)
            else:
                self.ok.set_sensitive(0)
        else:
                self.ok.set_sensitive(1)

    def on_toggled(self,obj):
        if self.in_db.get_active():
            self.name.set_editable(0)
            self.name.set_sensitive(0)
            self.id.set_editable(1)
            self.id.set_sensitive(1)
        else:
            self.name.set_editable(1)
            self.name.set_sensitive(1)
            self.id.set_editable(0)
            self.id.set_sensitive(0)
        self.check_valid_id()
        
    def cancel_clicked(self,obj):
        self.show_witness.get_widget('witness_edit').destroy()
        
    def ok_clicked(self,obj):
        if not self.ref:
            if self.in_db.get_active():
                self.ref = RelLib.Witness(RelLib.Event.ID)
            else:
                self.ref = RelLib.Witness(RelLib.Event.NAME)
            self.parent.list.append(self.ref)

        if self.in_db.get_active():
            self.ref.set_value(self.id.get_text())
        else:
            self.ref.set_value(self.name.get_text())

        c = self.comment.get_buffer()
        self.ref.set_comment(c.get_text(c.get_start_iter(),c.get_end_iter(),gtk.FALSE))
        if self.update:
            self.update()
        self.cancel_clicked(obj)
        

        
