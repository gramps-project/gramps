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

# $Id: _SourceView.py 7138 2006-08-06 06:26:10Z rshura $


from gettext import gettext as _

import const
import gtk

import NameDisplay
import ListModel
import ManagedWindow

_parent_titles = [(_('Father'),-1,200),(_('Mother'),-1,200),('',-1,0)]
_family_titles = [(_('Spouse'),-1,200),(_('Relationship'),-1,200),('',-1,0)]


class Reorder(ManagedWindow.ManagedWindow):
    
    def __init__(self, state, uistate, track, handle):
        xml = gtk.glade.XML(const.gladeFile, "reorder", "gramps")
	top = xml.get_widget('reorder')

	self.dbstate = state
        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)

	self.person = self.dbstate.db.get_person_from_handle(handle)
	self.parent_list = self.person.get_parent_family_handle_list()
	self.family_list = self.person.get_family_handle_list()

	penable = len(self.parent_list) > 1
	fenable = len(self.family_list) > 1

	self.set_window(top, None, _("Reorder Relationships"))

	self.ptree = xml.get_widget('ptree')
        self.pmodel = ListModel.ListModel(self.ptree,_parent_titles)

	self.ftree = xml.get_widget('ftree')
        self.fmodel = ListModel.ListModel(self.ftree,_family_titles)

	xml.get_widget('ok').connect('clicked', self.ok_clicked)
	xml.get_widget('cancel').connect('clicked', self.cancel_clicked)

	fup = xml.get_widget('fup')
	fup.connect('clicked', self.fup_clicked)
	fup.set_sensitive(fenable)

	fdown = xml.get_widget('fdown')
	fdown.connect('clicked', self.fdown_clicked)
	fdown.set_sensitive(fenable)

	pup = xml.get_widget('pup')
	pup.connect('clicked', self.pup_clicked)
	pup.set_sensitive(penable)

	pdown = xml.get_widget('pdown')
	pdown.connect('clicked', self.pdown_clicked)
	pdown.set_sensitive(penable)

	self.fill_data()

	self.show()

    def fill_data(self):
	self.fill_parents()
	self.fill_family()

    def fill_parents(self):
	for handle in self.parent_list:
	    family = self.dbstate.db.get_family_from_handle(handle)
	    fhandle = family.get_father_handle()
	    mhandle = family.get_mother_handle()

	    fname = ""
	    if fhandle:
		father = self.dbstate.db.get_person_from_handle(fhandle)
		if father:
		    fname = NameDisplay.displayer.display(father)

	    mname = ""
	    if mhandle:
		mother = self.dbstate.db.get_person_from_handle(mhandle)
		if mother:
		    mname = NameDisplay.displayer.display(mother)

	    self.pmodel.add([fname, mname, handle])

    def fill_family(self):
	for handle in self.family_list:

	    family = self.dbstate.db.get_family_from_handle(handle)
	    fhandle = family.get_father_handle()
	    mhandle = family.get_mother_handle()

	    name = ""

	    if fhandle and fhandle != self.person.handle:
		spouse = self.dbstate.db.get_person_from_handle(fhandle)
		if spouse:
		    name = NameDisplay.displayer.display(spouse)
	    elif mhandle:
		spouse = self.dbstate.db.get_person_from_handle(mhandle)
		if spouse:
		    name = NameDisplay.displayer.display(spouse)

	    reltype = str(family.get_relationship())

	    self.fmodel.add([name, reltype, handle])

    def cancel_clicked(self, obj):
	self.close()

    def ok_clicked(self, obj):
        trans = self.dbstate.db.transaction_begin()
	self.dbstate.db.commit_person(self.person, trans)
	name = NameDisplay.displayer.display(self.person)
	msg = _("Reorder Relationships: %s") % name
        self.dbstate.db.transaction_commit(trans, msg)

	self.close()

    def pup_clicked(self,obj):
        """Moves the current selection up one row"""
        row = self.pmodel.get_selected_row()
        if not row or row == -1:
            return
        store,the_iter = self.pmodel.get_selected()
        data = self.pmodel.get_data(the_iter,xrange(3))
        self.pmodel.remove(the_iter)
        self.pmodel.insert(row-1,data,None,1)
        handle = self.parent_list.pop(row)
        self.parent_list.insert(row-1,handle)

    def pdown_clicked(self, obj):
        row = self.pmodel.get_selected_row()
        if row + 1 >= self.pmodel.count or row == -1:
            return
        store,the_iter = self.pmodel.get_selected()
        data = self.pmodel.get_data(the_iter,xrange(3))
        self.pmodel.remove(the_iter)
        self.pmodel.insert(row+1,data,None,1)
        handle = self.parent_list.pop(row)
        self.parent_list.insert(row+1,handle)

    def fup_clicked(self, obj):
        row = self.fmodel.get_selected_row()
        if not row or row == -1:
            return
        store,the_iter = self.fmodel.get_selected()
        data = self.fmodel.get_data(the_iter,xrange(3))
        self.fmodel.remove(the_iter)
        self.fmodel.insert(row-1,data,None,1)
        handle = self.family_list.pop(row)
        self.family_list.insert(row-1,handle)


    def fdown_clicked(self, obj):
        row = self.fmodel.get_selected_row()
        if row + 1 >= self.fmodel.count or row == -1:
            return
        store,the_iter = self.fmodel.get_selected()
        data = self.fmodel.get_data(the_iter,xrange(3))
        self.fmodel.remove(the_iter)
        self.fmodel.insert(row+1,data,None,1)
        handle = self.family_list.pop(row)
        self.family_list.insert(row+1,handle)
