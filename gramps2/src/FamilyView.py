#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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
from gtk.gdk import ACTION_COPY, BUTTON1_MASK

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import sort
import Utils
import GrampsCfg
import AddSpouse
import SelectChild
import DisplayTrace
import Marriage
import ChooseParents
import RelLib
import EditPerson

from intl import gettext as _
from QuestionDialog import QuestionDialog,WarningDialog

_BORN = _('b.')
_DIED = _('d.')

pycode_tgts = [('child', 0, 0)]

#-------------------------------------------------------------------------
#
# FamilyView
#
#-------------------------------------------------------------------------
class FamilyView:

    def __init__(self,parent):
        self.parent = parent
        self.top = parent.gtop
        self.ap_data = self.top.get_widget('ap_data')
        self.ap_model = gtk.ListStore(gobject.TYPE_STRING)
        self.ap_data.set_model(self.ap_model)
        column = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
        self.ap_data.append_column(column)
        self.ap_data.connect('button-press-event',self.edit_active_person)

        self.swap_btn = self.top.get_widget('swap_spouse_btn')
        self.add_spouse_btn = self.top.get_widget('add_spouse')
        self.select_spouse_btn = self.top.get_widget('select_spouse')
        self.remove_spouse_btn = self.top.get_widget('remove_spouse')

        self.ap_parents = self.top.get_widget('ap_parents')
        self.ap_parents_model = gtk.ListStore(gobject.TYPE_STRING)
        self.ap_parents.set_model(self.ap_parents_model)
        self.ap_selection = self.ap_parents.get_selection()
        column = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
        self.ap_parents.append_column(column)
        self.ap_parents.connect('button-press-event',self.edit_ap_parents)

        self.sp_parents = self.top.get_widget('sp_parents')
        self.sp_parents_model = gtk.ListStore(gobject.TYPE_STRING)
        self.sp_parents.set_model(self.sp_parents_model)
        self.sp_selection = self.sp_parents.get_selection()
        column = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
        self.sp_parents.append_column(column)
        self.sp_parents.connect('button-press-event',self.edit_sp_parents)

        self.spouse_list = self.top.get_widget('sp_list')
        self.spouse_model = gtk.ListStore(gobject.TYPE_STRING)
        self.spouse_list.set_model(self.spouse_model)
        self.spouse_selection = self.spouse_list.get_selection()
        self.spouse_selection.connect('changed',self.spouse_changed)
        self.spouse_list.connect('button-press-event',self.edit_relationship)

        self.top.get_widget('add_parents').connect('clicked',self.add_parents_clicked)
        self.top.get_widget('del_parents').connect('clicked',self.del_parents_clicked)
        self.top.get_widget('add_spparents').connect('clicked',self.add_sp_parents)
        self.top.get_widget('del_spparents').connect('clicked',self.del_sp_parents)
        self.top.get_widget('fam_back').connect('clicked',self.child_back)
        self.top.get_widget('del_child_btn').connect('clicked',self.remove_child_clicked)
        self.top.get_widget('add_child_btn').connect('clicked',self.add_child_clicked)
        self.top.get_widget('select_child').connect('clicked',self.select_child_clicked)
        
        column = gtk.TreeViewColumn('',gtk.CellRendererText(),text=0)
        self.spouse_list.append_column(column)
        self.selected_spouse = None

        self.child_list = self.top.get_widget('chlist')

        self.child_list.drag_dest_set(gtk.DEST_DEFAULT_ALL,pycode_tgts,ACTION_COPY)
        self.child_list.drag_source_set(BUTTON1_MASK, pycode_tgts, ACTION_COPY)
        self.child_list.connect('drag_data_get', self.drag_data_get)
        self.child_list.connect('drag_begin', self.drag_begin)
        self.child_list.connect('drag_data_received',self.drag_data_received)
        
        self.child_model = gtk.ListStore(gobject.TYPE_INT,   gobject.TYPE_STRING,
                                         gobject.TYPE_STRING,gobject.TYPE_STRING,
                                         gobject.TYPE_STRING,gobject.TYPE_STRING, 
                                         gobject.TYPE_STRING)

        self.child_selection = self.child_list.get_selection()

        self.child_list.connect('button-press-event',self.on_child_list_button_press)

        self.top.get_widget('ap_parents_btn').connect('clicked',self.ap_parents_clicked)
        self.top.get_widget('sp_parents_btn').connect('clicked',self.sp_parents_clicked)
        
        self.swap_btn.connect('clicked',self.spouse_swap)
        self.remove_spouse_btn.connect('clicked',self.remove_spouse)
        self.add_spouse_btn.connect('clicked',self.add_spouse)
        self.select_spouse_btn.connect('clicked',self.select_spouse)

        self.child_list.set_model(self.child_model)
        self.child_list.set_search_column(0)
        self.child_selection = self.child_list.get_selection()

        self.family = None

        Utils.build_columns(self.child_list,
                            [ ('',30,0), (_('Name'),250,-1), (_('ID'),50,-1),
                              (_('Gender'),100,-1), (_('Birth date'),150,6),
                              (_('Status'),100,-1), ('',0,-1) ])

    def edit_active_person(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            self.parent.load_person(self.person)

    def on_child_list_button_press(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            model, iter = self.child_selection.get_selected()
            if iter:
                id = self.child_model.get_value(iter,2)
                self.parent.load_person(self.parent.db.getPerson(id))

    def spouse_changed(self,obj):
        model, iter = obj.get_selected()
        if not iter:
            self.display_marriage(None)
        else:
            row = model.get_path(iter)
            self.display_marriage(self.person.getFamilyList()[row[0]])
            
    def edit_relationship(self,obj,event):
        if event.state & gtk.gdk.SHIFT_MASK and \
           event.type == gtk.gdk.BUTTON_PRESS and \
           event.button == 1 and self.selected_spouse:
            self.parent.load_person(self.selected_spouse)
        elif event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
           if self.person:
               try:
                   if self.selected_spouse:
                       Marriage.Marriage(self.family,self.parent.db,
                                         self.parent.new_after_edit,
                                         self.load_family)
                   else:
                       AddSpouse.AddSpouse(self.parent.db,self.person,
                                           self.load_family,
                                           self.parent.redisplay_person_list,
                                           self.family)
               except:
                   DisplayTrace.DisplayTrace()
        
    def select_spouse(self,obj):
        if not self.person:
            return
        try:
            AddSpouse.AddSpouse(self.parent.db, self.person,
                                self.load_family,
                                self.parent.redisplay_person_list)
        except:
            DisplayTrace.DisplayTrace()

    def add_spouse(self,obj):
        person = RelLib.Person()
        if self.person.getGender() == RelLib.Person.male:
            person.setGender(RelLib.Person.female)
        else:
            person.setGender(RelLib.Person.male)
        try:
            EditPerson.EditPerson(person, self.parent.db, self.spouse_after_edit)
        except:
            DisplayTrace.DisplayTrace()

    def spouse_after_edit(self,epo,plist):
        if epo.person.getId() == "":
            self.parent.db.addPerson(epo.person)
        else:
            self.parent.db.addPersonNoMap(epo.person,epo.person.getId())
        self.parent.db.buildPersonDisplay(epo.person.getId())
        self.parent.add_to_person_list(epo.person,0)

        self.family = self.parent.db.newFamily()
        self.person.addFamily(self.family)
        epo.person.addFamily(self.family)

        if self.person.getGender() == RelLib.Person.male:
            self.family.setMother(epo.person)
            self.family.setFather(self.person)
        else:	
            self.family.setFather(epo.person)
            self.family.setMother(self.person)
        
        self.load_family(self.family)
        
        Marriage.Marriage(self.family,self.parent.db,
                          self.parent.new_after_edit,
                          self.load_family)

    def add_child_clicked(self,obj):
        if not self.person:
            return

        person = RelLib.Person()
        person.setGender(RelLib.Person.female)

        autoname = GrampsCfg.lastnamegen
        
        if autoname == 0:
            name = self.north_american(0)
        elif autoname == 2:
            name = self.latin_american(0)
        elif autoname == 3:
            name = self.icelandic(0)
        else:
            name = ""
        person.getPrimaryName().setSurname(name)

        try:
            EditPerson.EditPerson(person, self.parent.db, self.child_after_edit)
        except:
            DisplayTrace.DisplayTrace()

    def child_after_edit(self,epo,plist):
        if epo.person.getId() == "":
            self.parent.db.addPerson(epo.person)
        else:
            self.parent.db.addPersonNoMap(epo.person,epo.person.getId())
        self.parent.db.buildPersonDisplay(epo.person.getId())
        self.parent.add_to_person_list(epo.person,0)

        self.family.addChild(epo.person)
        epo.person.addAltFamily(self.family,"Birth","Birth")
        self.load_family()

    def select_child_clicked(self,obj):
        if not self.person:
            return
        try:
            SelectChild.SelectChild(self.parent.db, self.family,
                                    self.person, self.load_family,
                                    self.parent.update_person_list)
        except:
            DisplayTrace.DisplayTrace()

    def remove_child_clicked(self,obj):
        if not self.family or not self.person:
            return

        model, iter = self.child_selection.get_selected()
        if not iter:
            return

        id = self.child_model.get_value(iter,2)
        child = self.parent.db.getPerson(id)

        self.family.removeChild(child)
        child.removeAltFamily(self.family)
        
        if len(self.family.getChildList()) == 0:
            if self.family.getFather() == None:
                self.delete_family_from(self.family.getMother())
            elif self.family.getMother() == None:
                self.delete_family_from(self.family.getFather())

        Utils.modified()
        self.load_family()

    def remove_spouse(self,obj):
        if self.selected_spouse:
            nap = GrampsCfg.nameof(self.person)
            nsp = GrampsCfg.nameof(self.selected_spouse)
            QuestionDialog(_('Remove %s as a spouse of %s?') % (nsp,nap),
                           _('Removing a spouse removes the relationship between '
                             'the spouse and the active person. It does not '
                             'remove the spouse from the database'),
                           _('_Remove Spouse'),
                           self.really_remove_spouse)
        elif self.family and not self.family.getChildList():
            self.really_remove_spouse()
                       
    def really_remove_spouse(self):
        """Delete the currently selected spouse from the family"""
        if self.person == None:
            return
        if self.selected_spouse == self.family.getFather():
            self.family.setMother(None)
        else:
            self.family.setFather(None)

        if self.selected_spouse:
            self.selected_spouse.removeFamily(self.family)

        if len(self.family.getChildList()) == 0:
            self.person.removeFamily(self.family)
            self.parent.db.deleteFamily(self.family)
            if len(self.person.getFamilyList()) > 0:
                self.load_family(self.person.getFamilyList()[0])
            else:
                self.load_family()
        else:
            self.load_family()

        if len(self.person.getFamilyList()) <= 1:
            self.spouse_selection.set_mode(gtk.SELECTION_NONE)

        Utils.modified()

    def spouse_swap(self,obj):
        if self.selected_spouse:
            self.parent.active_person = self.selected_spouse
            self.load_family(self.family)

    def ap_parents_clicked(self,obj):
        self.change_families(self.person)
            
    def sp_parents_clicked(self,obj):
        self.change_families(self.selected_spouse)

    def change_families(self,person):
        if not person:
            return
        plist = person.getParentList()

        if len(plist) == 0:
            return
        if len(plist) == 1:
            family,m,r = plist[0]
        else:
            model, iter = self.ap_selection.get_selected()
            path = model.get_path(iter)
            family,m,r = plist[path[0]]

        if family.getFather():
            person = family.getFather()
        else:
            person = family.getMother()
        self.parent.change_active_person(person)
        self.load_family(family)

    def clear(self):
        self.spouse_model.clear()
        self.child_model.clear()
        self.sp_parents_model.clear()
        self.ap_parents_model.clear()
        self.ap_model.clear()

    def load_family(self,family=None):
        self.person = self.parent.active_person
        if not self.person:
            self.clear()
            return

        bd = self.person.getBirth().getDate()
        dd = self.person.getDeath().getDate()

        if bd and dd:
            n = "%s\n\t%s %s\n\t%s %s " % (GrampsCfg.nameof(self.person),
	    	_BORN,bd,_DIED,dd)
        elif bd:
            n = "%s\n\t%s %s" % (GrampsCfg.nameof(self.person),_BORN,bd)
        elif dd:
            n = "%s\n\t%s %s" % (GrampsCfg.nameof(self.person),_DIED,dd)
        else:
            n = GrampsCfg.nameof(self.person)

        self.ap_model.clear()
        self.ap_data.get_selection().set_mode(gtk.SELECTION_NONE)
        iter = self.ap_model.append()
        self.ap_model.set(iter,0,n)

        self.selected_spouse = None
        self.spouse_model.clear()
        self.child_model.clear()
        self.sp_parents_model.clear()
        splist = self.person.getFamilyList()

        if len(splist) > 1:
            self.spouse_selection.set_mode(gtk.SELECTION_SINGLE)
        else:
            self.spouse_selection.set_mode(gtk.SELECTION_NONE)

        flist = {}

        for f in splist:
            if not f:
                continue
            if f.getFather() == self.person:
                sp = f.getMother()
            else:
                sp = f.getFather()

            iter = self.spouse_model.append()
            flist[f.getId()] = iter
                
            if sp:
                if f.getMarriage():
                    mdate = " - %s" % f.getMarriage().getDate()
                else:
                    mdate = ""
                v = "%s\n\t%s%s" % (GrampsCfg.nameof(sp),
                                    f.getRelationship(),mdate)
                self.spouse_model.set(iter,0,v)
            else:
                self.spouse_model.set(iter,0,"unknown\n")

        if family in splist:
            self.display_marriage(family)
            iter = flist[family.getId()]
            self.spouse_selection.select_iter(iter)
        elif len(flist) > 0:
            f = splist[0]
            iter = flist[f.getId()]
            self.spouse_selection.select_iter(iter)
            self.display_marriage(f)
        else:
            self.display_marriage(None)

        self.update_list(self.ap_parents_model,self.ap_parents,self.person)

    def update_list(self,model,tree,person):
        model.clear()
        sel = None
        selection = tree.get_selection()
        list = person.getParentList()

        for (f,mrel,frel) in list:

            father = self.nameof(_("Father"),f.getFather(),frel)
            mother = self.nameof(_("Mother"),f.getMother(),mrel)

            iter = model.append()
            if not sel:
                sel = iter
            v = "%s\n%s" % (father,mother)
            model.set(iter,0,v)
        if len(list) > 1:
            selection.set_mode(gtk.SELECTION_SINGLE)
            selection.select_iter(sel)
        else:
            selection.set_mode(gtk.SELECTION_NONE)
            
    def nameof(self,l,p,mode):
        if p:
            n = GrampsCfg.nameof(p)
            return _("%s: %s\n\tRelationship: %s") % (l,n,mode)
        else:
            return _("%s: unknown") % (l)

    def delete_family_from(self,person):
        person.removeFamily(self.family)
        self.parent.db.deleteFamily(self.family)
        flist = self.person.getFamilyList()
        if len(flist) > 0:
            self.family = flist[0][0]
        else:
            self.family = None

    def display_marriage(self,family):

        self.child_model.clear()
        if not family:
            return
        else:
            self.family = family

        if family.getFather() == self.person:
            self.selected_spouse = family.getMother()
        else:
            self.selected_spouse = family.getFather()

        if self.selected_spouse:
            self.update_list(self.sp_parents_model,self.sp_parents,
                             self.selected_spouse)

        i = 0
        fiter = None
        child_list = list(family.getChildList())
#        child_list.sort(sort.by_birthdate)

        self.child_map = {}

        for child in child_list:
            status = _("Unknown")
            for fam in child.getParentList():
                if fam[0] == family:
                    if self.person == family.getFather():
                        status = "%s/%s" % (_(fam[2]),_(fam[1]))
                    else:
                        status = "%s/%s" % (_(fam[1]),_(fam[2]))

            iter = self.child_model.append()
            self.child_map[iter] = child.getId()
            
            if fiter == None:
                fiter = self.child_model.get_path(iter)
            val = self.parent.db.getPersonDisplay(child.getId())
            self.child_model.set(iter,
                                 0,(i+1),
                                 1,val[0],
                                 2,val[1],
                                 3,val[2],
                                 4,val[3],
                                 5,status,
                                 6,val[6])
                
    def edit_ap_parents(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1: 
            self.parent_editor(self.person,self.ap_selection)

    def edit_sp_parents(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1: 
            self.parent_editor(self.selected_spouse,self.sp_selection)

    def add_parents_clicked(self,obj):
        self.parent_add(self.person)

    def add_sp_parents(self,obj):
        if self.selected_spouse:
            self.parent_add(self.selected_spouse)

    def del_parents_clicked(self,obj):
        if len(self.person.getParentList()) == 0:
            return
        n = GrampsCfg.nameof(self.person)
        QuestionDialog(_('Remove Parents of %s') % n,
                       _('Removing the parents of a person removes the person as a '
                         'child of the parents. The parents are not removed from the '
                         'database, and the relationship between the parents '
                         'is not removed.'),
                       _('_Remove Parents'),
                       self.really_del_parents)
        
    def really_del_parents(self):
        self.parent_deleter(self.person,self.ap_selection)

    def del_sp_parents(self,obj):
        if not self.selected_spouse or len(self.selected_spouse.getParentList()) == 0:
            return
        n = GrampsCfg.nameof(self.selected_spouse)
        QuestionDialog(_('Remove Parents of %s') % n,
                       _('Removing the parents of a person removes the person as a '
                         'child of the parents. The parents are not removed from the '
                         'database, and the relationship between the parents '
                         'is not removed.'),
                       _('_Remove Parents'),
                       self.really_del_sp_parents)

    def really_del_sp_parents(self):
        self.parent_deleter(self.selected_spouse,self.sp_selection)

    def child_back(self,obj):
        """makes the currently select child the active person"""
        model, iter = self.child_selection.get_selected()
        if iter:
            id = self.child_model.get_value(iter,2)
            self.parent.change_active_person(self.parent.db.getPerson(id))
            self.load_family()

    def parent_editor(self,person,selection):
        if not person:
            return

        plist = person.getParentList()

        if len(plist) == 0:
            return
        elif len(plist) == 1:
            parents,mrel,frel = plist[0]
        else:
            model, iter = selection.get_selected()
            if not iter:
                return

            row = model.get_path(iter)
            parents,mrel,frel = plist[row[0]]

        try:
            ChooseParents.ModifyParents(self.parent.db,person,parents,
                                        self.load_family,self.parent.full_update)
        except:
            DisplayTrace.DisplayTrace()

    def parent_add(self,person):
        if not person:
            return
        try:
            ChooseParents.ChooseParents(self.parent.db,person,None,
                                        self.load_family,self.parent.full_update)
        except:
            DisplayTrace.DisplayTrace()
        
    def parent_deleter(self,person,selection):
        if not person:
            return
        plist = person.getParentList()
        if len(plist) == 0:
            return
        if len(plist) == 1:
            person.clearAltFamilyList()
        else:
            model, iter = selection.get_selected()
            if not iter:
                return

            row = model.get_path(iter)
            fam = person.getParentList()[row[0]]
            person.removeAltFamily(fam[0])
        Utils.modified()
        self.load_family()

    def drag_data_received(self,widget,context,x,y,sel_data,info,time):
        path = self.child_list.get_path_at_pos(x,y)
        if path == None:
            row = len(self.family.getChildList())
        else:
            row = path[0][0] -1
        
        if sel_data and sel_data.data:
            exec 'data = %s' % sel_data.data
            exec 'mytype = "%s"' % data[0]
            exec 'person = "%s"' % data[1]

            if mytype != 'child':
                return

            s,i = self.child_selection.get_selected()
            if not i:
                return

            spath = s.get_path(i)
            src = spath[0] 
            list = self.family.getChildList()

            obj = list[src]
            list.remove(obj)
            list.insert(row,obj)
            
            if (birth_dates_in_order(list) == 0):
                WarningDialog(_("Attempt to Reorder Children Failed"),
                              _("Children must be ordered by their birth dates."))
                return
            self.family.setChildList(list)
            self.display_marriage(self.family)
            Utils.modified()
            
    def drag_data_get(self,widget, context, sel_data, info, time):
        store,iter = self.child_selection.get_selected()
        if not iter:
            return
        id = self.child_model.get_value(iter,2)
        bits_per = 8; # we're going to pass a string
        data = str(('child',id));
        sel_data.set(sel_data.target, bits_per, data)

    def north_american(self,val):
        if self.person.getGender() == Person.male:
            return self.person.getPrimaryName().getSurname()
        elif self.family:
            f = self.family.getFather()
            if f:
                return f.getPrimaryName().getSurname()
        return ""

    def no_name(self,val):
        return ""

    def latin_american(self,val):
        if self.family:
            father = self.family.getFather()
            mother = self.family.getMother()
            if not father or not mother:
                return ""
            fsn = father.getPrimaryName().getSurname()
            msn = mother.getPrimaryName().getSurname()
            if not father or not mother:
                return ""
            try:
                return "%s %s" % (fsn.split()[0],msn.split()[0])
            except:
                return ""
        else:
            return ""

    def icelandic(self,val):
        fname = ""
        if self.person.getGender() == Person.male:
            fname = self.person.getPrimaryName().getFirstName()
        elif self.family:
            f = self.family.getFather()
            if f:
                fname = f.getPrimaryName().getFirstName()
        if fname:
            fname = string.split(fname)[0]
        if val == 0:
            return "%ssson" % fname
        elif val == 1:
            return "%sdóttir" % fname
        else:
            return ""

    def drag_begin(self, obj, context):
        return 
#         model, iter = self.child_selection.get_selected()
#         path = model.get_path(iter)
#         pixmap = self.child_list.create_row_drag_icon(path)
#         print "map",pixmap
        
#         myimage = gtk.Image()
#         print "set",pixmap
#         myimage.set_from_pixmap(pixmap,None)

#         print "image"
#         pixbuf = myimage.get_pixbuf()
#         print "buf", pixbuf

#         context.set_icon_pixbuf(pixbuf,0,0)
#         return

#-------------------------------------------------------------------------
# 
# birth_dates_in_order
# 
# Check any *valid* birthdates in the list to insure that they are in
# numerically increasing order.
# 
#-------------------------------------------------------------------------
def birth_dates_in_order(list):
    inorder = 1
    prev_date = "00000000"
    for i in range(len(list)):
        child = list[i]
        bday = child.getBirth().getDateObj()
        child_date = sort.build_sort_date(bday)
        if (child_date == "99999999"):
            continue
        if (prev_date <= child_date):	# <= allows for twins
            prev_date = child_date
        else:
            inorder = 0
    return inorder
