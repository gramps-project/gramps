#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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
# python modules
#
#-------------------------------------------------------------------------
import cPickle as pickle
from TransUtils import sgettext as _

#-------------------------------------------------------------------------
#
# 2.4 provides a built in set. We want to use this, but need to handle 
# older versions of python as well
#
#-------------------------------------------------------------------------
try:
    set()
except:
    from sets import Set as set

#-------------------------------------------------------------------------
#
# enable logging for error handling
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".")

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
import NameDisplay
import Spell
import GrampsDisplay
import RelLib
import AutoComp
import Config
import Errors

from _EditPrimary import EditPrimary
from PluginUtils import ReportUtils
from DdTargets import DdTargets
from DisplayTabs import *
from GrampsWidgets import *

from ObjectSelector import PersonSelector,PersonFilterSpec

from SelectPerson import SelectPerson

class ChildEmbedList(EmbeddedList):
    """
    The child embed list is specific to the Edit Family dialog, so it
    is contained here instead of in DisplayTabs.
    """

    _HANDLE_COL = 10
    _DND_TYPE = DdTargets.PERSON_LINK

    _column_names = [
        (_('#'),0) ,
        (_('ID'),1) ,
        (_('Name'),9),
        (_('Gender'),3),
        (_('Paternal'),12),
        (_('Maternal'),13),
        (_('Birth Date'),10),
        (_('Death Date'),11),
        (_('Birth Place'),6),
        (_('Death Place'),7),
        ]
    
    def __init__(self,dbstate,uistate,track,family):
        """
        Create the object, storing the passed family value
        """
        self.family = family
        EmbeddedList.__init__(self, dbstate, uistate, track,
                              _('Children'), ChildModel, True)

    def find_index(self,obj):
        """
        returns the index of the object within the associated data
        """
        return self.family.get_child_handle_list().index(obj)

    def _find_row(self,x,y):
        row = self.tree.get_path_at_pos(x,y)
        if row == None:
            return len(self.family.get_child_handle_list())
        else:
            return row[0][0]

    def _handle_drag(self, row, obj):
        self.family.get_child_handle_list().insert(row,obj)
        self.changed = True
        self.rebuild()

    def _move(self, row_from, row_to, obj):
        dlist = self.family.get_child_handle_list()
        if row_from < row_to:
            dlist.insert(row_to,obj)
            del dlist[row_from]
        else:
            del dlist[row_from]
            dlist.insert(row_to-1,obj)
        self.changed = True
        self.rebuild()

    def build_columns(self):
        """
        We can't use the default build_columns in the base class, because
        we are using the custom TypeCellRenderer to handle father parent
        relationships. The Paternal and Maternal columns (columns 4 and 5)
        use this.
        """
        for column in self.columns:
            self.tree.remove_column(column)
        self.columns = []

        for pair in self.column_order():
            if not pair[0]:
                continue
            name = self._column_names[pair[1]][0]
            if pair[1] == 4 or pair[1] == 5:
                render = TypeCellRenderer(Utils.child_relations)
                column = gtk.TreeViewColumn(name, render, text=pair[1])
            else:
                render = gtk.CellRendererText()
                column = gtk.TreeViewColumn(name, render, text=pair[1])

            column.set_resizable(True)
            column.set_min_width(40)
            column.set_sort_column_id(self._column_names[pair[1]][1])
            self.columns.append(column)
            self.tree.append_column(column)

    def get_icon_name(self):
        return 'gramps-family'

    def is_empty(self):
        """
        The list is considered empty if the child list is empty.
        """
        return len(self.family.get_child_handle_list()) == 0

    def get_data(self):
        """
        Normally, get_data returns a list. However, we return family
        object here instead.
        """
        return self.family

    def column_order(self):
        return [(1,0),(1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(0,8),(0,9)]

    def add_button_clicked(self,obj):
        from Editors import EditPerson

        person = RelLib.Person()
        autoname = Config.get_lastnamegen()
        if autoname == 0:
            name = self.north_american()
        elif autoname == 2:
            name = self.latin_american()
        else:
            name = self.no_name()
        person.get_primary_name().set_surname(name[1])
        person.get_primary_name().set_surname_prefix(name[0])

        EditPerson(self.dbstate,self.uistate,[],person, self.new_child_added)

    def new_child_added(self, person):
        self.family.add_child_handle(person.get_handle())
        self.rebuild()

    def share_button_clicked(self,obj):
        from SelectPerson import SelectPerson

        # it only makes sense to skip those who are already in the family
        
        skip = [self.family.get_father_handle(),
                self.family.get_mother_handle()] + self.family.get_child_handle_list()

        sel = SelectPerson(self.dbstate.db, "Select Child",
                           skip=[ x for x in skip if x])
        person = sel.run()
        
        if person:
            self.family.add_child_handle(person.get_handle())
            self.rebuild()

#     def add_button_clicked(self,obj):
#         # we could workout the death years of the parents here and
#         # set a suitable filter_spec on the PersonSelector
#         # we might also be able to set a filter that only includes
#         # people that are not already listed as children in another
#         # family.
#         selector = PersonSelector(self.dbstate,self.uistate,self.track)

#         # this need the window handle of the main EditFamily window
#         # to make the PersonSelector transient to it. I am not sure
#         # want the best way is to get that handle from here.
#         #selector.set_transient_for(self.window)

#         # Connect this to the method used to add a new child.
#         #selector.connect('add-object',self.on_add_child)
        
#         selector.connect('add-object',self.on_change_child)

#     def on_change_child(self, selector_window, obj):
#         if obj.__class__ == RelLib.Person:
#             try:
#                 person = obj
#                 self.family.add_child_handle(person.get_handle())
#                 self.rebuild()
#             except:
#                 log.warn(
#                     "Failed to update child: \n"
#                     "obj returned from selector was: %s\n"
#                     % (repr(obj),))
#                 raise
#         else:
#             log.warn(
#                 "Object selector returned obj.__class__ = %s, it should "
#                 "have been of type %s." % (obj.__class__.__name__,
#                                            RelLib.Person.__name__))
#         selector_window.close()

    def run(self,skip):
        SelectPerson(self.dbstate.db, "Select Child",
                     skip=[ x for x in skip if x])

    def del_button_clicked(self,obj):
        handle = self.get_selected()
        if handle:
            self.family.remove_child_handle(handle)
            self.rebuild()

    def edit_button_clicked(self,obj):
        handle = self.get_selected()
        if handle:
            from _EditPerson import EditPerson
            try:
                person = self.dbstate.db.get_person_from_handle(handle)
                EditPerson(self.dbstate,self.uistate,self.track,person)
            except Errors.WindowActiveError:
                pass

    def north_american(self):
        father_handle = self.family.get_father_handle()
        if father_handle:
            father = self.dbstate.db.get_person_from_handle(father_handle)
            pname = father.get_primary_name()
            return (pname.get_surname_prefix(),pname.get_surname())
        return ("","")

    def no_name(self):
        return ("","")

    def latin_american(self):
        if self.family:
            father_handle = self.family.get_father_handle()
            mother_handle = self.family.get_mother_handle()
            if not father_handle or not mother_handle:
                return ("","")
            father = self.db.db.get_person_from_handle(father_handle)
            mother = self.db.db.get_person_from_handle(mother_handle)
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

class FastMaleFilter:

    def __init__(self,db):
        self.db = db

    def match(self, handle):
        value = self.db.get_raw_person_data(handle)
        return value[2] == RelLib.Person.MALE

class FastFemaleFilter:

    def __init__(self,db):
        self.db = db

    def match(self, handle):
        value = self.db.get_raw_person_data(handle)
        return value[2] == RelLib.Person.FEMALE

#-------------------------------------------------------------------------
#
# EditFamily
#
#-------------------------------------------------------------------------
class EditFamily(EditPrimary):

    def __init__(self,dbstate,uistate,track,family):
        EditPrimary.__init__(self, dbstate, uistate, track,
                             family, dbstate.db.get_family_from_handle)

        # look for the scenerio of a child and no parents on a new
        # family
        
        if self.added and self.obj.get_father_handle() == None and \
           self.obj.get_mother_handle() == None and \
           len(self.obj.get_child_handle_list()) == 1:
            self.add_parent = True
            if not Config.get_family_warn():
                for i in self.hidden:
                    i.set_sensitive(False)

                glade = gtk.glade.XML(const.gladeFile,'family_warn')
                dialog = glade.get_widget('family_warn')
                dialog.run()
                if glade.get_widget('dont_show').get_active():
                    Config.save_family_warn(True)
                dialog.destroy()
        else:
            self.add_parent = False

    def empty_object(self):
        return RelLib.Family()

    def _local_init(self):
        self.build_interface()

        self.mname  = None
        self.fname  = None

        self._add_db_signal('person-update', self.check_for_change)
        self._add_db_signal('person-delete', self.check_for_change)
        self._add_db_signal('person-rebuild', self.reload_people)
        
        self.added = self.obj.handle == None
        if self.added:
            self.obj.handle = Utils.create_id()
            
        self.load_data()

    def check_for_change(self,handles):
        for node in handles:
            if node in self.phandles:
                self.reload_people()
                break;

    def reload_people(self):
        fhandle = self.obj.get_father_handle()
        self.update_father(fhandle)

        mhandle = self.obj.get_mother_handle()
        self.update_mother(mhandle)
        self.child_list.rebuild()

    def build_menu_names(self,obj):
        return ('Edit Family','Undefined Submenu')

    def build_interface(self):

        self.top = gtk.glade.XML(const.gladeFile,"family_editor","gramps")

        self.define_top_level(self.top.get_widget("family_editor"),
                              None,_('Family Editor'))

        self.fbirth = self.top.get_widget('fbirth')
        self.fdeath = self.top.get_widget('fdeath')
        
        self.mbirth = self.top.get_widget('mbirth')
        self.mdeath = self.top.get_widget('mdeath')

        self.mbutton= self.top.get_widget('mbutton')
        self.fbutton= self.top.get_widget('fbutton')

        self.mbox   = self.top.get_widget('mbox')
        self.fbox   = self.top.get_widget('fbox')

    def _connect_signals(self):
        self.define_ok_button(self.top.get_widget('ok'), self.save)
        self.define_cancel_button(self.top.get_widget('cancel'))

    def _can_be_replaced(self):
        pass

    def _setup_fields(self):
        
        self.private= PrivacyButton(
            self.top.get_widget('private'),
            self.obj,
            self.db.readonly)

        self.gid = MonitoredEntry(
            self.top.get_widget('gid'),
            self.obj.set_gramps_id,
            self.obj.get_gramps_id,
            self.db.readonly)
        
        self.data_type = MonitoredType(
            self.top.get_widget('marriage_type'),
            self.obj.set_relationship,
            self.obj.get_relationship,
            dict(Utils.family_relations),
            RelLib.Family.CUSTOM)

    def load_data(self):
        fhandle = self.obj.get_father_handle()
        self.update_father(fhandle)

        mhandle = self.obj.get_mother_handle()
        self.update_mother(mhandle)

        self.phandles = [mhandle, fhandle] + self.obj.get_child_handle_list()
        self.phandles = [handle for handle in self.phandles if handle]

        self.mbutton.connect('clicked',self.mother_clicked)
        self.fbutton.connect('clicked',self.father_clicked)

    def _create_tabbed_pages(self):

        notebook = gtk.Notebook()

        self.child_list = self._add_tab(
            notebook,
            ChildEmbedList(self.dbstate,self.uistate, self.track, self.obj))
        
        self.event_list = self._add_tab(
            notebook,
            EventEmbedList(self.dbstate,self.uistate, self.track,self.obj))
            
        self.src_list = self._add_tab(
            notebook,
            SourceEmbedList(self.dbstate,self.uistate,
                            self.track,self.obj.source_list))
            
        self.attr_list = self._add_tab(
            notebook,
            FamilyAttrEmbedList(self.dbstate, self.uistate, self.track,
                                self.obj.get_attribute_list()))
            
        self.note_tab = self._add_tab(
            notebook,
            NoteTab(self.dbstate, self.uistate, self.track,
                    self.obj.get_note_object()))
            
        self.gallery_tab = self._add_tab(
            notebook,
            GalleryTab(self.dbstate, self.uistate, self.track,
                       self.obj.get_media_list()))

        notebook.show_all()

        self.hidden = (notebook, self.top.get_widget('info'))
        self.top.get_widget('vbox').pack_start(notebook,True)

    def update_father(self,handle):
        self.load_parent(handle, self.fbox, self.fbirth,
                         self.fdeath, self.fbutton)

    def update_mother(self,handle):
        self.load_parent(handle, self.mbox, self.mbirth,
                         self.mdeath, self.mbutton)

    def on_change_mother(self, selector_window, obj):
        if obj.__class__ == RelLib.Person:
            try:
                person = obj
                self.obj.set_mother_handle(person.get_handle()) 
                self.update_mother(person.get_handle())                    
            except:
                log.warn(
                    "Failed to update mother: \n"
                    "obj returned from selector was: %s\n"
                    % (repr(obj),))
                raise
        else:
            log.warn(
                "Object selector returned obj.__class__ = %s, it should "
                "have been of type %s." % (obj.__class__.__name__,
                                           RelLib.Person.__name__))
            
        selector_window.close()

            
    def mother_clicked(self, obj):
        for i in self.hidden:
            i.set_sensitive(True)

        handle = self.obj.get_mother_handle()

        if handle:
            self.obj.set_mother_handle(None)
            self.update_mother(None)
        else:
            from SelectPerson import SelectPerson

            data_filter = FastFemaleFilter(self.dbstate.db)
            sel = SelectPerson(self.dbstate.db, "Select Mother",
                               filter=data_filter,
                               skip=self.obj.get_child_handle_list())
            person = sel.run()

            if person:
                self.check_for_existing_family(self.obj.get_father_handle(),
                                               person.handle,
                                               self.obj.handle)

                self.obj.set_mother_handle(person.handle) 
                self.update_mother(person.handle)

#     def mother_clicked(self,obj):
#         handle = self.obj.get_mother_handle()
#         if handle:
#             self.obj.set_mother_handle(None)
#             self.update_mother(None)
#         else:
#             filter_spec = PersonFilterSpec()
#             filter_spec.set_gender(RelLib.Person.FEMALE)
            
#             child_birth_years = []
#             for person_handle in self.obj.get_child_handle_list():
#                 person = self.db.get_person_from_handle(person_handle)
#                 event_ref = person.get_birth_ref()
#                 if event_ref and event_ref.ref:
#                     event = self.db.get_event_from_handle(event_ref.ref)
#                     child_birth_years.append(event.get_date_object().get_year())
                    
#             if len(child_birth_years) > 0:
#                 filter_spec.set_birth_year(min(child_birth_years))
#                 filter_spec.set_birth_criteria(PersonFilterSpec.BEFORE)
                

#             selector = PersonSelector(self.dbstate,self.uistate,
#                                       self.track,filter_spec=filter_spec)
#             selector.connect('add-object',self.on_change_mother)
            
    def on_change_father(self, selector_window, obj):
        if  obj.__class__ == RelLib.Person:
            try:
                person = obj
                self.obj.set_father_handle(person.get_handle()) 
                self.update_father(person.get_handle())                    
            except:
                log.warn("Failed to update father: \n"
                         "obj returned from selector was: %s\n"
                         % (repr(obj),))                
                raise
            
        else:
            log.warn(
                "Object selector returned obj.__class__ = %s, it should "
                "have been of type %s." % (obj.__class__.__name__,
                                           RelLib.Person.__name__))
            
        selector_window.close()

    def father_clicked(self, obj):
        for i in self.hidden:
            i.set_sensitive(True)

        handle = self.obj.get_father_handle()
        if handle:
            self.obj.set_father_handle(None)
            self.update_father(None)
        else:
            from SelectPerson import SelectPerson

            data_filter = FastMaleFilter(self.dbstate.db)
            sel = SelectPerson(self.dbstate.db, "Select Father",
                               filter=data_filter,
                               skip=self.obj.get_child_handle_list())
            person = sel.run()

            if person:

                self.check_for_existing_family(person.handle,
                                               self.obj.get_mother_handle(),
                                               self.obj.handle)
            
                self.obj.set_father_handle(person.handle) 
                self.update_father(person.handle)

    def check_for_existing_family(self, father_handle, mother_handle,
                                  family_handle):

        if father_handle:
            father = self.dbstate.db.get_person_from_handle(father_handle)
            ffam = set(father.get_family_handle_list())
            if mother_handle:
                mother = self.dbstate.db.get_person_from_handle(mother_handle)
                mfam = set(mother.get_family_handle_list())
                common = list(mfam.intersection(ffam))
                if len(common) > 0:
                    if self.add_parent:
                        clist = self.obj.get_child_handle_list()
                        self.obj = self.dbstate.db.get_family_from_handle(common[0])
                        self.obj.add_child_handle(clist[0])
                        self.close_window()
                        try:
                            EditFamily(self.dbstate,self.uistate,[],self.obj)
                        except Errors.WindowActiveError:
                            pass
                    elif self.obj.handle not in common:
                        import QuestionDialog
                        QuestionDialog.WarningDialog(
                            _('Duplicate Family'),
                            _('A family with these parents already exists '
                              'in the database. If you save, you will create '
                              'a duplicate family.'))
            else:
                for fh in father.get_family_handle_list():
                    fam = self.dbstate.db.get_family_from_handle(fh)
                    if fam.get_mother_handle() == None:
                        self.close_window()
                        try:
                            clist = self.obj.get_child_handle_list()
                            fam.add_child_handle(clist[-1])
                            EditFamily(self.dbstate,self.uistate,[],fam)
                        except Errors.WindowActiveError:
                            pass
        elif mother_handle:
            mother = self.dbstate.db.get_person_from_handle(mother_handle)
            for fh in mother.get_family_handle_list():
                fam = self.dbstate.db.get_family_from_handle(fh)
                if fam.get_father_handle() == None:
                    self.close_window()
                    try:
                        clist = self.obj.get_child_handle_list()
                        fam.add_child_handle(clist[-1])
                        EditFamily(self.dbstate,self.uistate,[],fam)
                    except Errors.WindowActiveError:
                        pass


#     def father_clicked(self,obj):
#         handle = self.obj.get_father_handle()
#         if handle:
#             self.obj.set_father_handle(None)
#             self.update_father(None)
#         else:
#             filter_spec = PersonFilterSpec()
#             filter_spec.set_gender(RelLib.Person.MALE)

#             child_birth_years = []
#             for person_handle in self.obj.get_child_handle_list():
#                 person = self.db.get_person_from_handle(person_handle)
#                 event_ref = person.get_birth_ref()
#                 if event_ref and event_ref.ref:
#                     event = self.db.get_event_from_handle(event_ref.ref)
#                     child_birth_years.append(event.get_date_object().get_year())
                    
#             if len(child_birth_years) > 0:
#                 filter_spec.set_birth_year(min(child_birth_years))
#                 filter_spec.set_birth_criteria(PersonFilterSpec.BEFORE)
                
#             selector = PersonSelector(self.dbstate,self.uistate,
#                                       self.track,filter_spec=filter_spec)
#             selector.connect('add-object',self.on_change_father)

    def edit_person(self,obj,event,handle):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            from _EditPerson import EditPerson
            try:
                person = self.db.get_person_from_handle(handle)
                EditPerson(self.dbstate, self.uistate,
                                      self.track, person)
            except Errors.WindowActiveError:
                pass

    def load_parent(self,handle,box,birth_obj,death_obj,btn_obj):

        is_used = handle != None

        for i in box.get_children():
            box.remove(i)

        try:
            btn_obj.remove(btn_obj.get_children()[0])
        except IndexError:
            pass
        
        if is_used:
            db = self.db
            person = db.get_person_from_handle(handle)
            name = "%s [%s]" % (NameDisplay.displayer.display(person),
                                person.gramps_id)
            data = ReportUtils.get_birth_death_strings(db,person)
            birth = data[0]
            death = data[4]

            del_image = gtk.Image()
            del_image.show()
            del_image.set_from_stock(gtk.STOCK_REMOVE,gtk.ICON_SIZE_BUTTON)
            btn_obj.add(del_image)

            box.pack_start(LinkBox(
                BasicLabel(name),
                IconButton(self.edit_person,person.handle)
                ))
        else:
            name = ""
            birth = ""
            death = ""

            add_image = gtk.Image()
            add_image.show()
            add_image.set_from_stock(gtk.STOCK_ADD,gtk.ICON_SIZE_BUTTON)
            btn_obj.add(add_image)

        birth_obj.set_text(birth)
        death_obj.set_text(death)

    def fix_parent_handles(self,orig_handle, new_handle, trans):
        if orig_handle != new_handle:
            if orig_handle:
                person = self.db.get_person_from_handle(orig_handle)
                person.family_list.remove(self.obj.handle)
                self.db.commit_person(person,trans)
            if new_handle:
                person = self.db.get_person_from_handle(orig_handle)
                if self.obj.handle not in person.family_list:
                    person.family_list.append(self.obj.handle)
                self.db.commit_person(person,trans)

    def save(self,*obj):
        if not self.added:
            original = self.db.get_family_from_handle(self.obj.handle)
        else:
            original = None

        if not original and not self.object_is_empty():
            print self.obj.serialize()
            trans = self.db.transaction_begin()

            # find the father, add the family handle to the father
            handle = self.obj.get_father_handle()
            if handle:
                parent = self.db.get_person_from_handle(handle)
                parent.add_family_handle(self.obj.handle)
                self.db.commit_person(parent,trans)

            # find the mother, add the family handle to the mother
            handle = self.obj.get_mother_handle()
            if handle:
                parent = self.db.get_person_from_handle(handle)
                parent.add_family_handle(self.obj.handle)
                self.db.commit_person(parent,trans)
                
            # for each child, add the family handle to the child
            for handle in self.obj.get_child_handle_list():
                child = self.db.get_person_from_handle(handle)
                # fix - relationships need to be extracted from the list
                child.add_parent_family_handle(self.obj.handle,
                                               (RelLib.Person.CHILD_BIRTH,''),
                                               (RelLib.Person.CHILD_BIRTH,''),
                                               )
                self.db.commit_person(child,trans)

            self.db.add_family(self.obj,trans)
            self.db.transaction_commit(trans,_("Add Family"))
        elif not original and self.object_is_empty():
            from QuestionDialog import ErrorDialog
            ErrorDialog(_("Cannot save family"),
                        _("No data exists for this family. Please "
                          "enter data or cancel the edit."))
            return
        elif cmp(original.serialize(),self.obj.serialize()):

            trans = self.db.transaction_begin()

            self.fix_parent_handles(original.get_father_handle(),
                                    self.obj.get_father_handle(),trans)
            self.fix_parent_handles(original.get_mother_handle(),
                                    self.obj.get_mother_handle(),trans)

            orig_set = set(original.get_child_handle_list())
            new_set = set(self.obj.get_child_handle_list())

            # remove the family from children which have been removed
            for handle in orig_set.difference(new_set):
                person = self.db.get_person_from_handle(handle)
                person.remove_parent_family_handle(self.obj.handle)
                self.db.commit_person(person,trans)
            
            # add the family from children which have been addedna
            for handle in new_set.difference(orig_set):
                person = self.db.get_person_from_handle(handle)
                person.add_parent_family_handle(self.obj.handle,
                                               (RelLib.Person.CHILD_BIRTH,''),
                                               (RelLib.Person.CHILD_BIRTH,''),
                                               )
                self.db.commit_person(person,trans)

            if self.object_is_empty():
                self.db.remove_family(self.obj.handle,trans)
            else:
                self.db.commit_family(self.obj,trans)
            self.db.transaction_commit(trans,_("Edit Family"))
        self.close_window()

