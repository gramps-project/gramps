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

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------

from gettext import gettext as _

#-------------------------------------------------------------------------
#
# gtk
#
#-------------------------------------------------------------------------
import gtk
from gtk.gdk import ACTION_COPY, BUTTON1_MASK

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import RelLib
import PeopleModel
import PageView
import GenericFilter
import EditPerson
import NameDisplay
import Utils
import QuestionDialog
import TreeTips

from DdTargets import DdTargets

column_names = [
    _('Name'),
    _('ID') ,
    _('Gender'),
    _('Birth Date'),
    _('Birth Place'),
    _('Death Date'),
    _('Death Place'),
    _('Spouse'),
    _('Last Change'),
    _('Cause of Death'),
    ]


class PersonView(PageView.PersonNavView):

    def __init__(self,dbstate,uistate):
        PageView.PersonNavView.__init__(self,'Person View',dbstate,uistate)
        self.inactive = False
        dbstate.connect('database-changed',self.change_db)
        dbstate.connect('active-changed',self.goto_active_person)
        self.handle_col = len(column_names)+2
        
    def change_page(self):
        self.on_filter_name_changed(None)
        
    def define_actions(self):
        """
        Required define_actions function for PageView. Builds the action
        group information required. We extend beyond the normal here,
        since we want to have more than one action group for the PersonView.
        Most PageViews really won't care about this.

        Special action groups for Forward and Back are created to allow the
        handling of navigation buttons. Forward and Back allow the user to
        advance or retreat throughout the history, and we want to have these
        be able to toggle these when you are at the end of the history or
        at the beginning of the history.
        """

        PageView.PersonNavView.define_actions(self)
        
        self.add_action('Add', gtk.STOCK_ADD, "_Add",
                        callback=self.add)
        self.add_action('Edit', gtk.STOCK_EDIT, "_Edit",
                        callback=self.edit)
        self.add_action('Remove', gtk.STOCK_REMOVE, "_Remove",
                        callback=self.remove)

        self.add_toggle_action('Filter', None, '_Filter', None, None,
                               self.filter_toggle)

    def get_stock(self):
        """
        Returns the name of the stock icon to use for the display.
        This assumes that this icon has already been registered with
        GNOME as a stock icon.
        """
        return 'gramps-person'

    def build_widget(self):
        """
        Builds the interface and returns a gtk.Container type that
        contains the interface. This containter will be inserted into
        a gtk.Notebook page.
        """
        self.vbox = gtk.VBox()
        self.vbox.set_border_width(4)
        self.vbox.set_spacing(4)
        
        self.filterbar = gtk.HBox()
        self.filterbar.set_spacing(4)
        self.filter_text = gtk.Entry()
        self.filter_label = gtk.Label('Label:')
        self.filter_list = gtk.ComboBox()
        self.filter_invert = gtk.CheckButton('Invert')
        self.filter_button = gtk.Button('Apply')
        self.filterbar.pack_start(self.filter_list,False)
        self.filterbar.pack_start(self.filter_label,False)
        self.filterbar.pack_start(self.filter_text,True)
        self.filterbar.pack_start(self.filter_invert,False)
        self.filterbar.pack_end(self.filter_button,False)

        self.filter_text.set_sensitive(False)

        self.tree = gtk.TreeView()
        self.tree.set_rules_hint(True)
        self.tree.set_headers_visible(True)
        self.tree.connect('key-press-event',self.key_press)

        scrollwindow = gtk.ScrolledWindow()
        scrollwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrollwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scrollwindow.add(self.tree)
        scrollwindow.show_all()

        self.vbox.pack_start(self.filterbar,False)
        self.vbox.pack_start(scrollwindow,True)

        self.renderer = gtk.CellRendererText()
        self.inactive = False

        self.columns = []
        self.build_columns()
        self.tree.connect('button-press-event', self.button_press)
        self.tree.connect('drag_data_get', self.drag_data_get)


        self.selection = self.tree.get_selection()
        self.selection.set_mode(gtk.SELECTION_MULTIPLE)
        self.selection.connect('changed',self.row_changed)

        self.vbox.set_focus_chain([self.tree, self.filter_list,
                                   self.filter_text, self.filter_invert,
                                   self.filter_button])

        self.setup_filter()
        return self.vbox
    
    def ui_definition(self):
        """
        Specifies the UIManager XML code that defines the menus and buttons
        associated with the interface.
        """
        return '''<ui>
          <menubar name="MenuBar">
            <menu action="ViewMenu">
              <menuitem action="Filter"/>
            </menu>
            <menu action="GoMenu">
              <placeholder name="CommonGo">
                <menuitem action="Back"/>
                <menuitem action="Forward"/>
                <separator/>
                <menuitem action="HomePerson"/>
                <separator/>
              </placeholder>
            </menu>
            <menu action="EditMenu">
              <placeholder name="CommonEdit">
                <menuitem action="Add"/>
                <menuitem action="Edit"/>
                <menuitem action="Remove"/>
              </placeholder>
            </menu>
          </menubar>
          <toolbar name="ToolBar">
            <placeholder name="CommonNavigation">
              <toolitem action="Back"/>  
              <toolitem action="Forward"/>  
              <toolitem action="HomePerson"/>
            </placeholder>
            <placeholder name="CommonEdit">
              <toolitem action="Add"/>
              <toolitem action="Edit"/>
              <toolitem action="Remove"/>
            </placeholder>
          </toolbar>
          <popup name="Popup">
            <menuitem action="Back"/>
            <menuitem action="Forward"/>
            <menuitem action="HomePerson"/>
            <separator/>
            <menuitem action="Add"/>
            <menuitem action="Edit"/>
            <menuitem action="Remove"/>
          </popup>
        </ui>'''

    def change_db(self,db):
        """
        Callback associated with DbState. Whenenver the database
        changes, this task is called. In this case, we rebuild the
        columns, and connect signals to the connected database. Tere
        is no need to store the database, since we will get the value
        from self.state.db
        """
        self.build_columns()
        db.connect('person-add', self.person_added)
        db.connect('person-update', self.person_updated)
        db.connect('person-delete', self.person_removed)
        db.connect('person-rebuild', self.build_tree)
        self.apply_filter()

    def goto_active_person(self,obj=None):
        """
        Callback (and usable function) that selects the active person
        in the display tree.

        We have a bit of a problem due to the nature of how GTK works.
        We have unselect the previous path and select the new path. However,
        these cause a row change, which calls the row_change callback, which
        can end up calling change_active_person, which can call
        goto_active_person, causing a bit of recusion. Confusing, huh?

        Unforunately, we row_change has to be able to call change_active_person,
        because the can occur from the interface in addition to programatically.

        TO handle this, we set the self.inactive variable that we can check
        in row_change to look for this particular condition.
        """

        # if there is no active person, or if we have been marked inactive,
        # simply return

        if not self.dbstate.active or self.inactive:
            return

        # mark inactive to prevent recusion
        self.inactive = True

        # select the active person in the person view
        p = self.dbstate.active
        try:
            path = self.model.on_get_path(p.get_handle())
            group_name = p.get_primary_name().get_group_name()
            top_name = self.dbstate.db.get_name_group_mapping(group_name)
            top_path = self.model.on_get_path(top_name)
            self.tree.expand_row(top_path,0)

            current = self.model.on_get_iter(path)
            selected = self.selection.path_is_selected(path)
            if current != p.get_handle() or not selected:
                self.selection.unselect_all()
                self.selection.select_path(path)
                self.tree.scroll_to_cell(path,None,1,0.5,0)
        except KeyError:
            self.selection.unselect_all()
            self.uistate.push_message(_("Active person not visible"))
            self.dbstate.active = p

        # disable the inactive flag
        self.inactive = False

        # update history
        self.handle_history(p.handle)
        
    def setup_filter(self):
        """
        Builds the default filters and add them to the filter menu.
        """
        
        cell = gtk.CellRendererText()
        self.filter_list.clear()
        self.filter_list.pack_start(cell,True)
        self.filter_list.add_attribute(cell,'text',0)

        filter_list = []

        self.DataFilter = None

        all = GenericFilter.GenericFilter()
        all.set_name(_("Entire Database"))
        all.add_rule(GenericFilter.Everyone([]))

        all = GenericFilter.GenericFilter()
        all.set_name(_("Entire Database"))
        all.add_rule(GenericFilter.Everyone([]))
        filter_list.append(all)
        
        all = GenericFilter.GenericFilter()
        all.set_name(_("Females"))
        all.add_rule(GenericFilter.IsFemale([]))
        filter_list.append(all)

        all = GenericFilter.GenericFilter()
        all.set_name(_("Males"))
        all.add_rule(GenericFilter.IsMale([]))
        filter_list.append(all)

        all = GenericFilter.GenericFilter()
        all.set_name(_("People with unknown gender"))
        all.add_rule(GenericFilter.HasUnknownGender([]))
        filter_list.append(all)

        all = GenericFilter.GenericFilter()
        all.set_name(_("Disconnected individuals"))
        all.add_rule(GenericFilter.Disconnected([]))
        filter_list.append(all)

        all = GenericFilter.ParamFilter()
        all.set_name(_("People with names containing..."))
        all.add_rule(GenericFilter.SearchName(['']))
        filter_list.append(all)

        all = GenericFilter.GenericFilter()
        all.set_name(_("Adopted people"))
        all.add_rule(GenericFilter.HaveAltFamilies([]))
        filter_list.append(all)

        all = GenericFilter.GenericFilter()
        all.set_name(_("People with images"))
        all.add_rule(GenericFilter.HavePhotos([]))
        filter_list.append(all)

        all = GenericFilter.GenericFilter()
        all.set_name(_("People with incomplete names"))
        all.add_rule(GenericFilter.IncompleteNames([]))
        filter_list.append(all)

        all = GenericFilter.GenericFilter()
        all.set_name(_("People with children"))
        all.add_rule(GenericFilter.HaveChildren([]))
        filter_list.append(all)

        all = GenericFilter.GenericFilter()
        all.set_name(_("People with no marriage records"))
        all.add_rule(GenericFilter.NeverMarried([]))
        filter_list.append(all)

        all = GenericFilter.GenericFilter()
        all.set_name(_("People with multiple marriage records"))
        all.add_rule(GenericFilter.MultipleMarriages([]))
        filter_list.append(all)

        all = GenericFilter.GenericFilter()
        all.set_name(_("People without a known birth date"))
        all.add_rule(GenericFilter.NoBirthdate([]))
        filter_list.append(all)

        all = GenericFilter.GenericFilter()
        all.set_name(_("People with incomplete events"))
        all.add_rule(GenericFilter.PersonWithIncompleteEvent([]))
        filter_list.append(all)

        all = GenericFilter.GenericFilter()
        all.set_name(_("Families with incomplete events"))
        all.add_rule(GenericFilter.FamilyWithIncompleteEvent([]))
        filter_list.append(all)

        all = GenericFilter.ParamFilter()
        all.set_name(_("People probably alive"))
        all.add_rule(GenericFilter.ProbablyAlive(['']))
        filter_list.append(all)

        all = GenericFilter.GenericFilter()
        all.set_name(_("People marked private"))
        all.add_rule(GenericFilter.PeoplePrivate([]))
        filter_list.append(all)

        all = GenericFilter.GenericFilter()
        all.set_name(_("Witnesses"))
        all.add_rule(GenericFilter.IsWitness(['','']))
        filter_list.append(all)

        all = GenericFilter.ParamFilter()
        all.set_name(_("People with records containing..."))
        all.add_rule(GenericFilter.HasTextMatchingSubstringOf(['',0,0]))
        filter_list.append(all)

        all = GenericFilter.ParamFilter()
        all.set_name(_("People with records matching regular expression..."))
        all.add_rule(GenericFilter.HasTextMatchingRegexpOf(['',0,1]))
        filter_list.append(all)

        all = GenericFilter.GenericFilter()
        all.set_name(_("People with notes"))
        all.add_rule(GenericFilter.HasNote([]))
        filter_list.append(all)

        all = GenericFilter.ParamFilter()
        all.set_name(_("People with notes containing..."))
        all.add_rule(GenericFilter.HasNoteMatchingSubstringOf(['']))
        filter_list.append(all)

        self.filter_model = GenericFilter.FilterStore(filter_list)
        self.filter_list.set_model(self.filter_model)
        self.filter_list.set_active(self.filter_model.default_index())
        self.filter_list.connect('changed',self.on_filter_name_changed)
        self.filter_text.set_sensitive(False)

    def build_tree(self):
        """
        Creates a new PeopleModel instance. Essentially creates a complete
        rebuild of the data.
        """
        self.model = PeopleModel.PeopleModel(
            self.dbstate.db, self.DataFilter, self.filter_invert.get_active())
        self.tree.set_model(self.model)

        if self.model.tooltip_column != None:
            self.tooltips = TreeTips.TreeTips(self.tree,self.model.tooltip_column,True)
        self.build_columns()


    def filter_toggle(self,obj):
        if obj.get_active():
            self.filterbar.show()
        else:
            self.filterbar.hide()

    def add(self,obj):
        person = RelLib.Person()
        EditPerson.EditPerson(self.dbstate, self.uistate, [], person)

    def edit(self,obj):
        if self.dbstate.active:
            EditPerson.EditPerson(self.dbstate, self.uistate, [], self.dbstate.active)

    def remove(self,obj):
        mlist = self.get_selected_objects()
        if len(mlist) == 0:
            return
        
        for sel in mlist:
            p = self.dbstate.db.get_person_from_handle(sel)
            self.active_person = p
            name = NameDisplay.displayer.display(p) 

            msg = _('Deleting the person will remove the person '
                             'from the database.')
            msg = "%s %s" % (msg,Utils.data_recover_msg)
            QuestionDialog.QuestionDialog(_('Delete %s?') % name,msg,
                                          _('_Delete Person'),
                                          self.delete_person_response)

    def delete_person_response(self):
        #self.disable_interface()
        trans = self.dbstate.db.transaction_begin()
        
        n = NameDisplay.displayer.display(self.active_person)

        if self.dbstate.db.get_default_person() == self.active_person:
            self.dbstate.db.set_default_person_handle(None)

        for family_handle in self.active_person.get_family_handle_list():
            if not family_handle:
                continue
            family = self.dbstate.db.get_family_from_handle(family_handle)
            family_to_remove = False
            if self.active_person.get_handle() == family.get_father_handle():
                if family.get_mother_handle():
                    family.set_father_handle(None)
                else:
                    family_to_remove = True
            else:
                if family.get_father_handle():
                    family.set_mother_handle(None)
                else:
                    family_to_remove = True
            if family_to_remove:
                for child_handle in family.get_child_handle_list():
                    child = self.dbstate.db.get_person_from_handle(child_handle)
                    child.remove_parent_family_handle(family_handle)
                    self.dbstate.db.commit_person(child,trans)
                self.dbstate.db.remove_family(family_handle,trans)
            else:
                self.dbstate.db.commit_family(family,trans)

        for (family_handle,mrel,frel) in self.active_person.get_parent_family_handle_list():
            if family_handle:
                family = self.dbstate.db.get_family_from_handle(family_handle)
                family.remove_child_handle(self.active_person.get_handle())
                self.dbstate.db.commit_family(family,trans)

        handle = self.active_person.get_handle()

        person = self.active_person
        self.remove_from_person_list(person)
        #self.remove_from_history(handle)
        self.dbstate.db.remove_person(handle, trans)

        if self.uistate.phistory.index >= 0:
            handle = self.uistate.phistory.history[self.index]
            self.active_person = self.dbstate.db.get_person_from_handle(handle)
        else:
            self.dbstate.change_active_person(None)
        self.dbstate.db.transaction_commit(trans,_("Delete Person (%s)") % n)
        #self.redraw_histmenu()
        #self.enable_interface()

    def build_columns(self):
        for column in self.columns:
            self.tree.remove_column(column)
        try:
            column = gtk.TreeViewColumn(_('Name'), self.renderer,text=0,
                                        background=self.model.marker_color_column)
        except AttributeError:
            column = gtk.TreeViewColumn(_('Name'), self.renderer,text=0)
        column.set_resizable(True)
        #column.set_clickable(True)
        #column.connect('clicked',self.sort_clicked)
        column.set_min_width(225)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.tree.append_column(column)
        self.columns = [column]

        for pair in self.dbstate.db.get_person_column_order():
            if not pair[0]:
                continue
            name = column_names[pair[1]]
            try:
                column = gtk.TreeViewColumn(name, self.renderer, markup=pair[1],
                                            background=self.model.marker_color_column)
            except AttributeError:
                column = gtk.TreeViewColumn(name, self.renderer, markup=pair[1])
            column.set_resizable(True)
            column.set_min_width(60)
            column.set_sizing(gtk.TREE_VIEW_COLUMN_GROW_ONLY)
            self.columns.append(column)
            self.tree.append_column(column)

    def row_changed(self,obj):
        """Called with a row is changed. Check the selected objects from
        the person_tree to get the IDs of the selected objects. Set the
        active person to the first person in the list. If no one is
        selected, set the active person to None"""

        selected_ids = self.get_selected_objects()
        if not self.inactive:
            try:
                person = self.dbstate.db.get_person_from_handle(selected_ids[0])
                self.dbstate.change_active_person(person)
            except:
                self.dbstate.change_active_person(None)

        if len(selected_ids) == 1:
            self.tree.drag_source_set(BUTTON1_MASK,
                                             [DdTargets.PERSON_LINK.target()],
                                             ACTION_COPY)
        elif len(selected_ids) > 1:
            self.tree.drag_source_set(BUTTON1_MASK,
                                             [DdTargets.PERSON_LINK_LIST.target()],
                                             ACTION_COPY)
        self.uistate.modify_statusbar()
        
    def drag_data_get(self, widget, context, sel_data, info, time):
        selected_ids = self.get_selected_objects()

        if len(selected_ids) == 1:
            sel_data.set(sel_data.target, 8, selected_ids[0])
        elif len(selected_ids) > 1:
            sel_data.set(DdTargets.PERSON_LINK_LIST.drag_type,8,
                         pickle.dumps(selected_ids))

    def apply_filter_clicked(self):
        index = self.filter_list.get_active()
        self.DataFilter = self.filter_model.get_filter(index)
        if self.DataFilter.need_param:
            qual = unicode(self.filter_text.get_text())
            self.DataFilter.set_parameter(qual)
        self.apply_filter()
        self.goto_active_person()

    def person_added(self,handle_list):
        for node in handle_list:
            person = self.dbstate.db.get_person_from_handle(node)
            top = person.get_primary_name().get_group_name()
            self.model.rebuild_data(self.DataFilter)
            if not self.model.is_visable(node):
                continue
            if (not self.model.sname_sub.has_key(top) or 
                len(self.model.sname_sub[top]) == 1):
                path = self.model.on_get_path(top)
                pnode = self.model.get_iter(path)
                self.model.row_inserted(path,pnode)
            path = self.model.on_get_path(node)
            pnode = self.model.get_iter(path)
            self.model.row_inserted(path,pnode)

    def person_removed(self,handle_list):
        for node in handle_list:
            person = self.dbstate.db.get_person_from_handle(node)
            if not self.model.is_visable(node):
                continue
            top = person.get_primary_name().get_group_name()
            mylist = self.model.sname_sub.get(top,[])
            if mylist:
                try:
                    path = self.model.on_get_path(node)
                    self.model.row_deleted(path)
                    if len(mylist) == 1:
                        path = self.model.on_get_path(top)
                        self.model.row_deleted(path)
                except KeyError:
                    pass
        self.model.rebuild_data(self.DataFilter,skip=node)

    def person_updated(self,handle_list):
        for node in handle_list:
            person = self.dbstate.db.get_person_from_handle(node)
            try:
                oldpath = self.model.iter2path[node]
            except:
                return
            pathval = self.model.on_get_path(node)
            pnode = self.model.get_iter(pathval)

            # calculate the new data

            if person.primary_name.group_as:
                surname = person.primary_name.group_as
            else:
                base = person.primary_name.surname
                surname = self.dbstate.db.get_name_group_mapping(base)

            if oldpath[0] == surname:
                self.model.build_sub_entry(surname)
            else:
                self.model.calculate_data(self.DataFilter)
            
            # find the path of the person in the new data build
            newpath = self.model.temp_iter2path[node]
            
            # if paths same, just issue row changed signal

            if oldpath == newpath:
                self.model.row_changed(pathval,pnode)
            else:
                # paths different, get the new surname list
                
                mylist = self.model.temp_sname_sub.get(oldpath[0],[])
                path = self.model.on_get_path(node)
                
                # delete original
                self.model.row_deleted(pathval)
                
                # delete top node of original if necessar
                if len(mylist)==0:
                    self.model.row_deleted(pathval[0])
                    
                # determine if we need to insert a new top node',
                insert = not self.model.sname_sub.has_key(newpath[0])

                # assign new data
                self.model.assign_data()
                
                # insert new row if needed
                if insert:
                    path = self.model.on_get_path(newpath[0])
                    pnode = self.model.get_iter(path)
                    self.model.row_inserted(path,pnode)

                # insert new person
                path = self.model.on_get_path(node)
                pnode = self.model.get_iter(path)
                self.model.row_inserted(path,pnode)
                
        self.goto_active_person()

    def on_filter_name_changed(self,obj):
        index = self.filter_list.get_active()
        mime_filter = self.filter_model.get_filter(index)
        qual = mime_filter.need_param
        if qual:
            self.filter_text.show()
            self.filter_text.set_sensitive(True)
            self.filter_label.show()
            self.filter_label.set_text(mime_filter.get_rules()[0].labels[0])
        else:
            self.filter_text.hide()
            self.filter_text.set_sensitive(False)
            self.filter_label.hide()

    def apply_filter(self,current_model=None):
        self.uistate.status_text(_('Updating display...'))
        self.build_tree()
        self.uistate.modify_statusbar()

    def get_selected_objects(self):
        (mode,paths) = self.selection.get_selected_rows()
        mlist = []
        for path in paths:
            node = self.model.on_get_iter(path)
            mlist.append(self.model.on_get_value(node, PeopleModel.COLUMN_INT_ID))
        return mlist

    def remove_from_person_list(self,person):
        """Remove the selected person from the list. A person object is
        expected, not an ID"""
        path = self.model.on_get_path(person.get_handle())
        (col,row) = path
        if row > 0:
            self.selection.select_path((col,row-1))
        elif row == 0 and self.model.on_get_iter(path):
            self.selection.select_path(path)

    def button_press(self,obj,event):
        if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            handle = self.first_selected()
            person = self.dbstate.db.get_person_from_handle(handle)
            if person:
                EditPerson.EditPerson(self.dbstate, self.uistate, [], person)
                return True
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            menu = self.uistate.uimanager.get_widget('/Popup')
            if menu:
                menu.popup(None,None,None,event.button,event.time)
                return True
        return False
