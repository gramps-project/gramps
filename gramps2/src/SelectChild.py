# -*- coding: utf-8 -*-
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

    def __init__(self,db,family,person,redraw,add_person):
        self.db = db
        self.person = person
        self.family = family
        self.redraw = redraw
        self.add_person = add_person
        self.xml = gtk.glade.XML(const.gladeFile,"select_child","gramps")
    
        if person:
            self.default_name = person.getPrimaryName().getSurname().upper()
        else:
            self.default_name = ""

        self.xml.signal_autoconnect({
            "on_save_child_clicked"    : self.on_save_child_clicked,
            "on_child_help_clicked"    : self.on_child_help_clicked,
            "on_show_toggled"          : self.on_show_toggled,
            "destroy_passed_object"    : self.close
            })

        self.select_child_list = {}
        self.top = self.xml.get_widget("select_child")
        title_label = self.xml.get_widget('title')

        Utils.set_titles(self.top,title_label,_('Add Child to Family'))
        
        self.add_child = self.xml.get_widget("childlist")

        if (self.family):
            father = self.family.getFather()
            mother = self.family.getMother()

            if father != None:
                fname = father.getPrimaryName().getName()
                label = _("Relationship to %(father)s") % {
                    'father' : fname
                    }
                self.xml.get_widget("flabel").set_text(label)

            if mother != None:
                mname = mother.getPrimaryName().getName()
                label = _("Relationship to %(mother)s") % {
                    'mother' : mname
                    }
                self.xml.get_widget("mlabel").set_text(label)
        else:
            fname = self.person.getPrimaryName().getName()
            label = _("Relationship to %s") % fname
            
            if self.person.getGender() == RelLib.Person.male:
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

    def on_child_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','gramps-edit-quick')

    def close(self,obj):
        self.top.destroy()
        
    def redraw_child_list(self,filter):
        self.refmodel.clear()
        self.refmodel.new_model()
        bday = self.person.getBirth().getDateObj()
        dday = self.person.getDeath().getDateObj()

        slist = {}
        for f in self.person.getParentList():
            if f:
                if f[0].getFather():
                    slist[f[0].getFather().getId()] = 1
                elif f[0].getMother():
                    slist[f[0].getMother().getId()] = 1
                for c in f[0].getChildList():
                    slist[c.getId()] = 1
            
        person_list = []
        for key in self.db.sortPersonKeys():
            person = self.db.getPerson(key)
            if filter:
                if slist.has_key(key) or person.getMainParents():
                    continue
            
                pdday = person.getDeath().getDateObj()
                pbday = person.getBirth().getDateObj()

        	if bday.getYearValid():
                    if pbday.getYearValid():
                        # reject if child birthdate < parents birthdate + 10
                        if pbday.getLowYear() < bday.getHighYear()+10:
                            continue

                        # reject if child birthdate > parents birthdate + 90
                        if pbday.getLowYear() > bday.getHighYear()+90:
                            continue

                    if pdday.getYearValid():
                        # reject if child deathdate < parents birthdate+ 10
                        if pdday.getLowYear() < bday.getHighYear()+10:
                            continue
                
                if dday.getYearValid():
                    if pbday.getYearValid():
                        # reject if childs birth date > parents deathday + 3
                        if pbday.getLowYear() > dday.getHighYear()+3:
                            continue

                    if pdday.getYearValid():
                        # reject if childs death date > parents deathday + 150
                        if pdday.getLowYear() > dday.getHighYear() + 150:
                            continue
        
            person_list.append(person.getId())

        iter = None
        for idval in person_list:
            dinfo = self.db.getPersonDisplay(idval)
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
        select_child = self.db.getPerson(id)
        if self.family == None:
            self.family = self.db.newFamily()
            self.person.addFamily(self.family)
            if self.person.getGender() == RelLib.Person.male:
                self.family.setFather(self.person)
            else:	
                self.family.setMother(self.person)
                
        self.family.addChild(select_child)
		
        mrel = const.childRelations[unicode(self.mrel.get_text())]
        mother = self.family.getMother()
        if mother and mother.getGender() != RelLib.Person.female:
            if mrel == "Birth":
                mrel = "Unknown"
                
        frel = const.childRelations[unicode(self.frel.get_text())]
        father = self.family.getFather()
        if father and father.getGender() !=RelLib. Person.male:
            if frel == "Birth":
                frel = "Unknown"

        select_child.addAltFamily(self.family,mrel,frel)

        Utils.modified()
        self.top.destroy()
        self.redraw(self.family)
        
    def on_show_toggled(self,obj):
        self.redraw_child_list(not obj.get_active())

    def north_american(self,val):
        if self.person.getGender() == Person.male:
            return self.person.getPrimaryName().getSurname()
        elif self.family:
            f = self.family.getFather()
            if f:
                pname = f.getPrimaryName()
                return (pname.getSurnamePrefix(),pname.getSurname())
        return ("","")

    def no_name(self,val):
        return ("","")

    def latin_american(self,val):
        if self.family:
            father = self.family.getFather()
            mother = self.family.getMother()
            if not father or not mother:
                return ("","")
            fsn = father.getPrimaryName().getSurname()
            msn = mother.getPrimaryName().getSurname()
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
        if self.person.getGender() == Person.male:
            fname = self.person.getPrimaryName().getFirstName()
        elif self.family:
            f = self.family.getFather()
            if f:
                fname = f.getPrimaryName().getFirstName()
        if fname:
            fname = fname.split()[0]
        if val == 0:
            return ("","%ssson" % fname)
        elif val == 1:
            return ("","%sdóttir" % fname)
        else:
            return ("","")

class EditRel:

    def __init__(self,child,family,update):
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

        name = child.getPrimaryName().getName()
        Utils.set_titles(self.top,self.xml.get_widget('title'),
                         _('Relationships of %s') % name)

        father = self.family.getFather()
        mother = self.family.getMother()

        if father:
            fname = father.getPrimaryName().getName()
            val = _("Relationship to %(father)s") % {
                'father' : fname }
            self.fdesc.set_text('<b>%s</b>' % val)
            self.fcombo.set_sensitive(1)
        else:
            val = _("Relationship to father")
            self.fdesc.set_text('<b>%s</b>' % val)
            self.fcombo.set_sensitive(0)

        if mother:
            mname = mother.getPrimaryName().getName()
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

        f = self.child.has_family(self.family)
        self.fentry.set_text(_(f[2]))
        self.mentry.set_text(_(f[1]))
        
        self.fdesc.set_use_markup(gtk.TRUE)
        self.mdesc.set_use_markup(gtk.TRUE)
        self.top.show()

    def close(self,obj):
        self.top.destroy()

    def on_ok_clicked(self,obj):
        mrel = const.childRelations[unicode(self.mentry.get_text())]
        mother = self.family.getMother()
        if mother and mother.getGender() != RelLib.Person.female:
            if mrel == "Birth":
                mrel = "Unknown"
                
        frel = const.childRelations[unicode(self.fentry.get_text())]
        father = self.family.getFather()
        if father and father.getGender() !=RelLib. Person.male:
            if frel == "Birth":
                frel = "Unknown"

        self.child.changeAltFamily(self.family,mrel,frel)
        self.update()
        self.top.destroy()
