# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk.glade
import gnome

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import RelLib
import const
import Utils
import ListModel
import GrampsCfg
from RelLib import Person

#-------------------------------------------------------------------------
#
# SelectChild
#
#-------------------------------------------------------------------------
class SelectChild:

    def __init__(self,parent,db,family,person,redraw,add_person):
        self.parent = parent
        self.db = db
        self.person = person
        self.family = family
        self.redraw = redraw
        self.add_person = add_person
        self.xml = gtk.glade.XML(const.gladeFile,"select_child","gramps")
    
        if person:
            self.default_name = person.get_primary_name().get_surname().upper()
        else:
            self.default_name = ""

        self.xml.signal_autoconnect({
            "on_save_child_clicked"    : self.on_save_child_clicked,
            "on_child_help_clicked"    : self.on_child_help_clicked,
            "on_show_toggled"          : self.on_show_toggled,
            "destroy_passed_object"    : self.close,
            "on_select_child_delete_event" : self.on_delete_event,
            })

        self.select_child_list = {}
        self.top = self.xml.get_widget("select_child")
        title_label = self.xml.get_widget('title')

        Utils.set_titles(self.top,title_label,_('Add Child to Family'))
        
        self.add_child = self.xml.get_widget("childlist")

        if (self.family):
            father = self.db.find_person_from_id(self.family.get_father_id())
            mother = self.db.find_person_from_id(self.family.get_mother_id())

            if father != None:
                fname = father.get_primary_name().get_name()
                label = _("Relationship to %(father)s") % {
                    'father' : fname
                    }
                self.xml.get_widget("flabel").set_text(label)

            if mother != None:
                mname = mother.get_primary_name().get_name()
                label = _("Relationship to %(mother)s") % {
                    'mother' : mname
                    }
                self.xml.get_widget("mlabel").set_text(label)
        else:
            fname = self.person.get_primary_name().get_name()
            label = _("Relationship to %s") % fname
            
            if self.person.get_gender() == RelLib.Person.male:
                self.xml.get_widget("flabel").set_text(label)
                self.xml.get_widget("mrel_combo").set_sensitive(0)
            else:
                self.xml.get_widget("mlabel").set_text(label)
                self.xml.get_widget("frel_combo").set_sensitive(0)

        self.mrel = self.xml.get_widget("mrel")
        self.frel = self.xml.get_widget("frel")
        self.mrel.set_text(_("Birth"))

        self.frel.set_text(_("Birth"))

        titles = [(_('Name'),3,150),(_('ID'),1,50), (_('Birth date'),4,100),
                  ('',-1,0),('',-1,0)]
        
        self.refmodel = ListModel.ListModel(self.add_child,titles)
        self.redraw_child_list(2)
        self.add_itself_to_menu()
        self.top.show()

    def on_delete_event(self,obj,b):
        self.remove_itself_from_menu()

    def close(self,obj):
        self.remove_itself_from_menu()
        self.top.destroy()

    def add_itself_to_menu(self):
        self.parent.child_windows[self] = self
        self.parent_menu_item = gtk.MenuItem(_('Add Child to Family'))
        self.parent_menu_item.connect("activate",self.present)
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)

    def remove_itself_from_menu(self):
        del self.parent.child_windows[self]
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.top.present()

    def on_child_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-quick')

    def redraw_child_list(self,filter):
        self.refmodel.clear()
        self.refmodel.new_model()
        birth = self.db.find_event_from_id(self.person.get_birth_id())
        death = self.db.find_event_from_id(self.person.get_death_id())
        if birth:
            bday = birth.get_date_object()
        else:
            bday = None
        if death:
            dday = death.get_date_object()
        else:
            dday = None

        slist = {}
        for f in self.person.get_parent_family_id_list():
            if f:
                family = self.db.find_family_no_map(f[0])
                if family.get_father_id():
                    slist[family.get_father_id()] = 1
                elif family.get_mother_id():
                    slist[ffamily.get_mother_id()] = 1
                for c in family.get_child_id_list():
                    slist[c] = 1
            
        person_list = []
        for key in self.db.sort_person_keys():
            person = self.db.get_person(key)
            if filter:
                if slist.has_key(key) or person.get_main_parents_family_id():
                    continue
            
                birth_event = self.db.find_event_from_id(person.get_birth_id())
                if birth_event:
                    pbday = birth_event.get_date_object()
                else:
                    pbday = None

                death_event = self.db.find_event_from_id(person.get_death_id())
                if death_event:
                    pdday = death_event.get_date_object()
                else:
                    pdday = None
 
                if bday and bday.getYearValid():
                    if pbday and pbday.getYearValid():
                        # reject if child birthdate < parents birthdate + 10
                        if pbday.getLowYear() < bday.getHighYear()+10:
                            continue

                        # reject if child birthdate > parents birthdate + 90
                        if pbday.getLowYear() > bday.getHighYear()+90:
                            continue

                    if pdday and pdday.getYearValid():
                        # reject if child deathdate < parents birthdate+ 10
                        if pdday.getLowYear() < bday.getHighYear()+10:
                            continue
                
                if dday and dday.getYearValid():
                    if pbday and pbday.getYearValid():
                        # reject if childs birth date > parents deathday + 3
                        if pbday.getLowYear() > dday.getHighYear()+3:
                            continue

                    if pdday and pdday.getYearValid():
                        # reject if childs death date > parents deathday + 150
                        if pdday.getLowYear() > dday.getHighYear() + 150:
                            continue
        
            person_list.append(person.get_id())

        iter = None
        for idval in person_list:
            dinfo = self.db.get_person_display(idval)
            rdata = [dinfo[0],dinfo[1],dinfo[3],dinfo[5],dinfo[6]]
            new_iter = self.refmodel.add(rdata)
            names = dinfo[0].split(',')
            if len(names):
                ln = names[0].upper()
                if self.default_name and ln == self.default_name and not iter:
                    iter = new_iter

        self.refmodel.connect_model()

        if iter:
            self.refmodel.selection.select_iter(iter)
            path = self.refmodel.model.get_path(iter)
            col = self.add_child.get_column(0)
            self.add_child.scroll_to_cell(path,col,1,0.5,0.0)


    def on_save_child_clicked(self,obj):
        store,iter = self.refmodel.selection.get_selected()

        if not iter:
            return

        id = self.refmodel.model.get_value(iter,1)
        select_child = self.db.get_person(id)
        if self.family == None:
            self.family = self.db.new_family()
            self.person.add_family_id(self.family.get_id())
            if self.person.get_gender() == RelLib.Person.male:
                self.family.set_father_id(self.person)
            else:	
                self.family.set_mother_id(self.person)
                
        self.family.add_child_id(select_child.get_id())
		
        mrel = const.child_relations.find_value(self.mrel.get_text())
        mother = self.db.find_person_from_id(self.family.get_mother_id())
        if mother and mother.get_gender() != RelLib.Person.female:
            if mrel == "Birth":
                mrel = "Unknown"
                
        frel = const.child_relations.find_value(self.frel.get_text())
        father = self.db.find_person_from_id(self.family.get_father_id())
        if father and father.get_gender() !=RelLib. Person.male:
            if frel == "Birth":
                frel = "Unknown"

        select_child.add_parent_family_id(self.family.get_id(),mrel,frel)

        self.db.commit_person(select_child)
        self.redraw(self.family)
        self.close(obj)
        
    def on_show_toggled(self,obj):
        self.redraw_child_list(not obj.get_active())

    def north_american(self,val):
        if self.person.get_gender() == Person.male:
            return self.person.get_primary_name().get_surname()
        elif self.family:
            f = self.family.get_father_id()
            if f:
                pname = f.get_primary_name()
                return (pname.get_surname_prefix(),pname.get_surname())
        return ("","")

    def no_name(self,val):
        return ("","")

    def latin_american(self,val):
        if self.family:
            father = self.family.get_father_id()
            mother = self.family.get_mother_id()
            if not father or not mother:
                return ("","")
            fsn = father.get_primary_name().get_surname()
            msn = mother.get_primary_name().get_surname()
            if not father or not mother:
                return ("","")
            try:
                return ("","%s %s" % (fsn.split()[0],msn.split()[0]))
            except:
                return ("","")
        else:
            return ("","")

    def icelandic(self,val):
        fname = ""
        if self.person.get_gender() == Person.male:
            fname = self.person.get_primary_name().get_first_name()
        elif self.family:
            f = self.family.get_father_id()
            if f:
                fname = f.get_primary_name().get_first_name()
        if fname:
            fname = fname.split()[0]
        if val == 0:
            return ("","%ssson" % fname)
        elif val == 1:
            return ("","%sdóttir" % fname)
        else:
            return ("","")

class EditRel:

    def __init__(self,db,child,family,update):
        self.db = db
        self.update = update
        self.child = child
        self.family = family

        self.xml = gtk.glade.XML(const.gladeFile,"editrel","gramps")
        self.top = self.xml.get_widget('editrel')
        self.mdesc = self.xml.get_widget('mrel_desc')
        self.fdesc = self.xml.get_widget('frel_desc')
        self.mentry = self.xml.get_widget('mrel')
        self.fentry = self.xml.get_widget('frel')
        self.mcombo = self.xml.get_widget('mrel_combo')
        self.fcombo = self.xml.get_widget('frel_combo')

        name = child.get_primary_name().get_name()
        Utils.set_titles(self.top,self.xml.get_widget('title'),
                         _('Relationships of %s') % name)

        father = self.db.find_person_from_id(self.family.get_father_id())
        mother = self.db.find_person_from_id(self.family.get_mother_id())

        if father:
            fname = father.get_primary_name().get_name()
            val = _("Relationship to %(father)s") % {
                'father' : fname }
            self.fdesc.set_text('<b>%s</b>' % val)
            self.fcombo.set_sensitive(1)
        else:
            val = _("Relationship to father")
            self.fdesc.set_text('<b>%s</b>' % val)
            self.fcombo.set_sensitive(0)

        if mother:
            mname = mother.get_primary_name().get_name()
            val = _("Relationship to %(mother)s") % {
                'mother' : mname }
            self.mdesc.set_text('<b>%s</b>' % val)
            self.mcombo.set_sensitive(1)
        else:
            val = _("Relationship to mother")
            self.mdesc.set_text('<b>%s</b>' % val)
            self.mcombo.set_sensitive(0)

        self.xml.signal_autoconnect({
            "on_ok_clicked"    : self.on_ok_clicked,
            "destroy_passed_object"    : self.close
            })

        f = self.child.has_family(self.family.get_id())
        self.fentry.set_text(_(f[2]))
        self.mentry.set_text(_(f[1]))
        
        self.fdesc.set_use_markup(gtk.TRUE)
        self.mdesc.set_use_markup(gtk.TRUE)
        self.top.show()

    def close(self,obj):
        self.top.destroy()

    def on_ok_clicked(self,obj):
        mrel = const.child_relations.find_value(self.mentry.get_text())
        mother = self.db.find_person_from_id(self.family.get_mother_id())
        if mother and mother.get_gender() != RelLib.Person.female:
            if mrel == "Birth":
                mrel = "Unknown"
                
        frel = const.child_relations.find_value(self.fentry.get_text())
        father = self.db.find_person_from_id(self.family.get_father_id())
        if father and father.get_gender() !=RelLib. Person.male:
            if frel == "Birth":
                frel = "Unknown"

        self.child.change_parent_family_id(self.family.get_id(),mrel,frel)
        self.db.commit_person(self.child)
        self.update()
        self.top.destroy()
