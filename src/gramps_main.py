#! /usr/bin/python -O
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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
# Standard python modules
#
#-------------------------------------------------------------------------
import string
import os

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from intl import gettext
_ = gettext

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gnome.ui
import GDK
import GTK
import GdkImlib
import libglade

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from RelLib import *
from PedView import PedigreeView
from PlaceView import PlaceView
from SourceView import SourceView
from MediaView import MediaView

import ReadXML
import Filter
import const
import Plugins
import sort
import Utils
import Bookmarks
import ListColors
import GrampsCfg
import EditPerson
import Marriage
import Find
import VersionControl
import WriteXML

#-------------------------------------------------------------------------
#
# Main GRAMPS class
#
#-------------------------------------------------------------------------
class Gramps:

    def __init__(self,arg):

        self.DataFilter = Filter.Filter("")
        self.active_child = None
        self.active_family = None
        self.active_father = None
        self.active_mother = None
        self.active_parents = None
        self.parents_index = 0
        self.active_person = None
        self.active_spouse = None
        self.bookmarks = None
        self.c_birth_date = 4
        self.c_birth_order = 0
        self.c_details = 6
        self.c_gender = 3
        self.c_id = 2
        self.c_name = 1
        self.c_sort_col = self.c_birth_order
        self.c_sort_dir = GTK.SORT_ASCENDING
        self.sort_col = 0
        self.sort_dir = GTK.SORT_ASCENDING
        self.id2col = {}
        self.alt2col = {}

        gtk.rc_parse(const.gtkrcFile)

        if os.getuid() == 0:
            msg = _("You are running GRAMPS as the 'root' user.\nThis account is not meant for normal application use.")
            gnome.ui.GnomeWarningDialog(msg)

        self.database = GrampsDB()

        (self.sort_col,self.sort_dir) = GrampsCfg.get_sort_cols("person",self.sort_col,self.sort_dir)

        GrampsCfg.loadConfig(self.full_update)
        self.init_interface()

        self.col_map = [ 5, 1, 2, 6, 7 ]
        self.col_arr = [ self.nameArrow, self.idArrow, self.genderArrow,
                         self.dateArrow, self.deathArrow]

        self.change_sort(self.sort_col,self.sort_dir==GTK.SORT_DESCENDING)
        self.set_sort_arrow(self.sort_col,self.sort_dir)

        self.database.set_iprefix(GrampsCfg.iprefix)
        self.database.set_oprefix(GrampsCfg.oprefix)
        self.database.set_fprefix(GrampsCfg.fprefix)
        self.database.set_sprefix(GrampsCfg.sprefix)
        self.database.set_pprefix(GrampsCfg.pprefix)
        
        if arg != None:
            self.read_file(arg)
        elif GrampsCfg.lastfile != None and GrampsCfg.lastfile != "" and GrampsCfg.autoload:
            self.auto_save_load(GrampsCfg.lastfile)
        else:
            import DbPrompter
            DbPrompter.DbPrompter(self,0)

            if GrampsCfg.autosave_int != 0:
                Utils.enable_autosave(self.autosave_database,GrampsCfg.autosave_int)

        self.database.setResearcher(GrampsCfg.get_researcher())

    def init_interface(self):
        """Initializes the GLADE interface, and gets references to the
        widgets that it will need.
        """
        self.gtop = libglade.GladeXML(const.gladeFile, "gramps")

        self.statusbar   = self.gtop.get_widget("statusbar")
        self.topWindow   = self.gtop.get_widget("gramps")
        self.person_list = self.gtop.get_widget("person_list")
        self.filter_list = self.gtop.get_widget("filter_list")
        self.notebook    = self.gtop.get_widget("notebook1")
        self.nameArrow   = self.gtop.get_widget("nameSort")
        self.genderArrow = self.gtop.get_widget("genderSort")
        self.idArrow     = self.gtop.get_widget("idSort")
        self.dateArrow   = self.gtop.get_widget("dateSort")
        self.deathArrow  = self.gtop.get_widget("deathSort")
        self.merge_button= self.gtop.get_widget("merge")
        self.cNameArrow  = self.gtop.get_widget("cNameSort")
        self.cGenderArrow= self.gtop.get_widget("cGenderSort")
        self.cIDArrow    = self.gtop.get_widget("cIDSort")
        self.cDateArrow  = self.gtop.get_widget("cDateSort")
        self.canvas      = self.gtop.get_widget("canvas1")
        self.child_list  = self.gtop.get_widget("child_list")
        self.toolbar = self.gtop.get_widget("toolbar1")
        self.spouse_menu = self.gtop.get_widget("fv_spouse")
        self.person_text = self.gtop.get_widget("fv_person")
        self.spouse_text = self.gtop.get_widget("fv_spouse1")
        self.filter_text = self.gtop.get_widget('filter')
        self.filter_inv  = self.gtop.get_widget("invert")
        self.qual_label  = self.gtop.get_widget("qual")
        self.child_type  = self.gtop.get_widget("childtype")
        self.spouse_tab  = self.gtop.get_widget("lab_or_list")
        self.pref_spouse = self.gtop.get_widget("pref_spouse")
        self.multi_spouse= self.gtop.get_widget("multi_spouse")
        self.spouse_pref = self.gtop.get_widget("prefrel")
        self.spouse_edit = self.gtop.get_widget("edit_sp")
        self.spouse_del  = self.gtop.get_widget("delete_sp")
        self.spouse_combo= self.gtop.get_widget("spouse_combo")
        self.spouse_tab  = self.gtop.get_widget("spouse_tab")

        self.person_list.set_column_visibility(5,0)
        self.person_list.set_column_visibility(6,0)
        self.person_list.set_column_visibility(7,0)
        self.person_list.set_column_visibility(1,GrampsCfg.id_visible)
        self.person_list.column_titles_active()

        self.build_plugin_menus()
        self.init_filters()

        # set the window icon 
        self.topWindow.set_icon(gtk.GtkPixmap(self.topWindow,const.icon))
    
        self.toolbar.set_style(GrampsCfg.toolbar)
        self.notebook.set_show_tabs(GrampsCfg.usetabs)

        self.child_list.set_column_visibility(self.c_details,GrampsCfg.show_detail)
        self.child_list.set_column_justification(self.c_birth_order,GTK.JUSTIFY_RIGHT)

        self.pedigree_view = PedigreeView(self.canvas,
                                          self.modify_statusbar,
                                          self.statusbar,
                                          self.change_active_person,
                                          self.load_person)
        self.place_view  = PlaceView(self.database,self.gtop,self.update_display)
        self.source_view = SourceView(self.database,self.gtop,self.update_display)
        self.media_view  = MediaView(self.database,self.gtop,self.update_display)

        self.gtop.signal_autoconnect({
            "delete_event"                      : self.delete_event,
            "destroy_passed_object"             : Utils.destroy_passed_object,
            "on_preffam_clicked"                : self.on_preferred_fam_toggled,
            "on_family_up_clicked"              : self.family_up_clicked,
            "on_family_down_clicked"            : self.family_down_clicked,
            "on_spouse_list_changed"            : self.spouse_list_changed,
            "on_prefrel_toggled"                : self.on_preferred_rel_toggled,
            "on_about_activate"                 : self.on_about_activate,
            "on_add_bookmark_activate"          : self.on_add_bookmark_activate,
            "on_add_child_clicked"              : self.on_add_child_clicked,
            "on_add_new_child_clicked"          : self.on_add_new_child_clicked,
            "on_add_place_clicked"              : self.place_view.on_add_place_clicked,
            "on_add_source_clicked"             : self.source_view.on_add_source_clicked,
            "on_add_sp_clicked"                 : self.on_add_sp_clicked,
            "on_addperson_clicked"              : self.load_new_person,
            "on_apply_filter_clicked"           : self.on_apply_filter_clicked,
            "on_arrow_left_clicked"             : self.pedigree_view.on_show_child_menu,
            "on_canvas1_event"                  : self.pedigree_view.on_canvas1_event,
            "on_child_list_button_press_event"  : self.on_child_list_button_press_event,
            "on_child_list_select_row"          : self.on_child_list_select_row,
            "on_child_list_click_column"        : self.on_child_list_click_column,
            "on_child_list_row_move"            : self.on_child_list_row_move,
            "on_choose_parents_clicked"         : self.on_choose_parents_clicked, 
            "on_contents_activate"              : self.on_contents_activate,
            "on_default_person_activate"        : self.on_default_person_activate,
            "on_delete_parents_clicked"         : self.on_delete_parents_clicked,
            "on_delete_person_clicked"          : self.on_delete_person_clicked,
            "on_delete_place_clicked"           : self.place_view.on_delete_place_clicked,
            "on_delete_source_clicked"          : self.source_view.on_delete_source_clicked,
            "on_delete_media_clicked"           : self.media_view.on_delete_media_clicked,
            "on_delete_sp_clicked"              : self.on_delete_sp_clicked,
            "on_edit_active_person"             : self.load_active_person,
            "on_edit_selected_people"           : self.load_selected_people,
            "on_edit_bookmarks_activate"        : self.on_edit_bookmarks_activate,
            "on_edit_father_clicked"            : self.on_edit_father_clicked,
            "on_edit_media_clicked"             : self.media_view.on_edit_media_clicked,
            "on_edit_mother_clicked"            : self.on_edit_mother_clicked,
            "on_edit_place_clicked"             : self.place_view.on_edit_place_clicked,
            "on_edit_source_clicked"            : self.source_view.on_edit_source_clicked,
            "on_edit_sp_clicked"                : self.on_edit_sp_clicked,
            "on_edit_spouse_clicked"            : self.on_edit_spouse_clicked,
            "on_exit_activate"                  : self.on_exit_activate,
            "on_family1_activate"               : self.on_family1_activate,
            "on_father_next_clicked"            : self.on_father_next_clicked,
            "on_find_activate"                  : self.on_find_activate,
            "on_findname_activate"              : self.on_findname_activate,
            "on_fv_prev_clicked"                : self.on_fv_prev_clicked,
            "on_home_clicked"                   : self.on_home_clicked,
            "on_mother_next_clicked"            : self.on_mother_next_clicked,
            "on_new_clicked"                    : self.on_new_clicked,
            "on_notebook1_switch_page"          : self.on_notebook1_switch_page,
            "on_ok_button1_clicked"             : self.on_ok_button1_clicked,
            "on_open_activate"                  : self.on_open_activate,
            "on_pedegree1_activate"             : self.on_pedegree1_activate,
            "on_person_list1_activate"          : self.on_person_list1_activate,
            "on_person_list_button_press"       : self.on_person_list_button_press,
            "on_person_list_click_column"       : self.on_person_list_click_column,
            "on_person_list_select_row"         : self.on_person_list_select_row,
            "on_place_list_click_column"        : self.place_view.on_click_column,
            "on_main_key_release_event"         : self.on_main_key_release_event,
            "on_add_media_clicked"              : self.media_view.create_add_dialog,
            "on_media_activate"                 : self.on_media_activate,
            "on_media_list_select_row"          : self.media_view.on_select_row,
            "on_media_list_drag_data_get"       : self.media_view.on_drag_data_get,
            "on_media_list_drag_data_received"  : self.media_view.on_drag_data_received,
            "on_merge_activate"                 : self.on_merge_activate,
            "on_places_activate"                : self.on_places_activate,
            "on_preferences_activate"           : self.on_preferences_activate,
            "on_reload_plugins_activate"        : Plugins.reload_plugins,
            "on_remove_child_clicked"           : self.on_remove_child_clicked,
            "on_reports_clicked"                : self.on_reports_clicked,
            "on_revert_activate"                : self.on_revert_activate,
            "on_save_activate"                  : self.on_save_activate,
            "on_save_as_activate"               : self.on_save_as_activate,
            "on_show_plugin_status"             : self.on_show_plugin_status,
            "on_source_list_button_press_event" : self.source_view.on_button_press_event,
            "on_sources_activate"               : self.on_sources_activate,
            "on_swap_clicked"                   : self.on_swap_clicked,
            "on_tools_clicked"                  : self.on_tools_clicked,
            "on_gramps_home_page_activate"      : self.on_gramps_home_page_activate,
            "on_gramps_report_bug_activate"     : self.on_gramps_report_bug_activate,
            "on_gramps_mailing_lists_activate"  : self.on_gramps_mailing_lists_activate,
            "on_writing_extensions_activate"    : self.on_writing_extensions_activate,
            })	

    def on_show_plugin_status(self,obj):
        Plugins.PluginStatus()

    def build_plugin_menus(self):
        export_menu = self.gtop.get_widget("export1")
        import_menu = self.gtop.get_widget("import1")
        report_menu = self.gtop.get_widget("reports_menu")
        tools_menu  = self.gtop.get_widget("tools_menu")

        Plugins.load_plugins(const.docgenDir)
        Plugins.load_plugins(os.path.expanduser("~/.gramps/docgen"))
        Plugins.load_plugins(const.pluginsDir)
        Plugins.load_plugins(os.path.expanduser("~/.gramps/plugins"))

        Plugins.build_report_menu(report_menu,self.menu_report)
        Plugins.build_tools_menu(tools_menu,self.menu_tools)
        Plugins.build_export_menu(export_menu,self.export_callback)
        Plugins.build_import_menu(import_menu,self.import_callback)

    def init_filters(self):

        Filter.load_filters(const.filtersDir)
        Filter.load_filters(os.path.expanduser("~/.gramps/filters"))

        menu = Filter.build_filter_menu(self.on_filter_name_changed,self.filter_text)

        self.filter_list.set_menu(menu)
        self.filter_text.set_sensitive(0)
        
    def on_find_activate(self,obj):
        """Display the find box"""
        if self.notebook.get_current_page() == 4:
            Find.FindPlace(self.place_view.place_list,self.find_goto_place,
                           self.database.getPlaceMap().values())
        elif self.notebook.get_current_page() == 3:
            Find.FindSource(self.source_view.source_list,self.find_goto_source,
                           self.database.getSourceMap().values())
        elif self.notebook.get_current_page() == 5:
            Find.FindMedia(self.media_view.media_list,self.find_goto_media,
                           self.database.getObjectMap().values())
        else:
            Find.FindPerson(self.person_list,self.find_goto_to,
                            self.database.getPersonMap().values())

    def on_findname_activate(self,obj):
        """Display the find box"""
        pass

    def find_goto_to(self,person):
        """Find callback to jump to the selected person"""
        self.change_active_person(person)
        self.goto_active_person()
        self.update_display(0)

    def find_goto_place(self,row):
        """Find callback to jump to the selected place"""
        self.place_view.moveto(row)

    def find_goto_source(self,row):
        """Find callback to jump to the selected source"""
        self.source_view.moveto(row)

    def find_goto_media(self,row):
        """Find callback to jump to the selected media"""
        self.media_view.moveto(row)

    def on_gramps_home_page_activate(self,obj):
        import gnome.url
        gnome.url.show("http://gramps.sourceforge.net")

    def on_gramps_mailing_lists_activate(self,obj):
        import gnome.url
        gnome.url.show("http://sourceforge.net/mail/?group_id=25770")

    def on_gramps_report_bug_activate(self,obj):
        import gnome.url
        gnome.url.show("http://sourceforge.net/tracker/?group_id=25770&atid=385137")
    
    def on_merge_activate(self,obj):
        """Calls up the merge dialog for the selection"""
        page = self.notebook.get_current_page()
        if page == 0:
            if len(self.person_list.selection) != 2:
                msg = _("Exactly two people must be selected to perform a merge")
                gnome.ui.GnomeErrorDialog(msg)
            else:
                import MergeData
                (p1,x) = self.person_list.get_row_data(self.person_list.selection[0])
                (p2,x) = self.person_list.get_row_data(self.person_list.selection[1])
                MergeData.MergePeople(self.database,p1,p2,self.merge_update,
                                      self.update_after_edit)
        elif page == 4:
            self.place_view.merge()

    def delete_event(self,widget, event):
        """Catch the destruction of the top window, prompt to save if needed"""
        widget.hide()
        self.on_exit_activate(widget)
        return 1

    def on_exit_activate(self,obj):
        """Prompt to save on exit if needed"""
        if Utils.wasModified():
            question = _("Unsaved changes exist in the current database\n") + \
                       _("Do you wish to save the changes?")
            gnome.ui.GnomeQuestionDialog(question,self.save_query)
        else:    
            gtk.mainquit(obj)

    def save_query(self,value):
        """Catch the reponse to the save on exit question"""
        if value == 0:
            self.on_save_activate_quit()
        gtk.mainquit(self.gtop)

    def on_about_activate(self,obj):
        """Displays the about box.  Called from Help menu"""
        gnome.ui.GnomeAbout(const.progName,const.version,const.copyright,
                            const.authors,const.comments,const.logo).show()
    
    def on_contents_activate(self,obj):
        """Display the GRAMPS manual"""
        import gnome.help
	url = gnome.help.file_find_file("gramps-manual","gramps-manual.sgml")
	url = "gnome-help:"+url
        gnome.help.goto(url)

    def on_writing_extensions_activate(self,obj):
        """Display the Extending GRAMPS manual"""
        import gnome.help
        url = gnome.help.file_find_file("extending-gramps","extending-gramps.sgml")
	url = "gnome-help:"+url
        gnome.help.goto(url)
    
    def on_remove_child_clicked(self,obj):
        if not self.active_family or not self.active_child or not self.active_person:
            return

        self.active_family.removeChild(self.active_child)
        self.active_child.removeAltFamily(self.active_child)
        
        if len(self.active_family.getChildList()) == 0:
            if self.active_family.getFather() == None:
                self.delete_family_from(self.active_family.getMother())
            elif self.active_family.getMother() == None:
                self.delete_family_from(self.active_family.getFather())

        Utils.modified()
        self.load_family()

    def delete_family_from(self,person):
        person.removeFamily(self.active_family)
        self.database.deleteFamily(self.active_family)
        flist = self.active_person.getFamilyList()
        if len(flist) > 0:
            self.active_family = flist[0][0]
        else:
            self.active_family = None

    def add_new_cancel(self,obj):
        Utils.destroy_passed_object(self.addornew)

    def add_new_new_relationship(self,obj):
        import AddSpouse
        Utils.destroy_passed_object(self.addornew)
        AddSpouse.AddSpouse(self.database,self.active_person,
                            self.load_family,self.redisplay_person_list)
        
    def on_add_sp_clicked(self,obj):
        """Add a new spouse to the current person"""
        import AddSpouse
        if self.active_person:
            if self.active_family and not self.active_spouse:
                top = libglade.GladeXML(const.gladeFile, "add_or_new")
                top.signal_autoconnect({
                    'on_cancel_clicked' : self.add_new_cancel,
                    'on_add_clicked' : self.add_new_choose_spouse,
                    'on_new_clicked' : self.add_new_new_relationship
                    })
                self.addornew = top.get_widget('add_or_new')
            else:
                AddSpouse.AddSpouse(self.database,self.active_person,
                                    self.load_family,self.redisplay_person_list)
    def add_new_choose_spouse(self,obj):
        import AddSpouse
        Utils.destroy_passed_object(self.addornew)
        AddSpouse.SetSpouse(self.database,self.active_person,self.active_family,
                            self.load_family, self.redisplay_person_list)

    def on_edit_sp_clicked(self,obj):
        """Edit the marriage information for the current family"""
        if self.active_person:
            Marriage.Marriage(self.active_family,self.database,self.new_after_edit)

    def on_delete_sp_clicked(self,obj):
        """Delete the currently selected spouse from the family"""
    
        if self.active_person == None:
            return
        elif self.active_person == self.active_family.getFather():
            person = self.active_family.getMother()
            self.active_family.setMother(None)
        else:
            person = self.active_family.getFather()
            self.active_family.setFather(None)

        if person:
            person.removeFamily(self.active_family)
    
        if len(self.active_family.getChildList()) == 0:
            self.active_person.removeFamily(self.active_family)
            self.database.deleteFamily(self.active_family)
            if len(self.active_person.getFamilyList()) > 0:
                self.load_family(self.active_person.getFamilyList()[0])
            else:
                self.load_family(None)
        else:
            self.load_family()
        Utils.modified()

    def on_mother_next_clicked(self,obj):
        """Makes the current mother the active person"""
        if self.active_parents:
            mother = self.active_parents.getMother()
            if mother:
                self.change_active_person(mother)
                obj.set_sensitive(1)
                self.load_family()
            else:
                obj.set_sensitive(0)
        else:
            obj.set_sensitive(0)

    def on_father_next_clicked(self,obj):
        """Makes the current father the active person"""
        if self.active_parents:
            father = self.active_parents.getFather()
            if father:
                self.change_active_person(father)
                obj.set_sensitive(1)
                self.load_family()
            else:
                obj.set_sensitive(0)
        else:
            obj.set_sensitive(0)

    def on_fv_prev_clicked(self,obj):
        """makes the currently select child the active person"""
        if self.active_child:
            self.change_active_person(self.active_child)
            self.load_family()

    def on_add_child_clicked(self,obj):
        """Select an existing child to add to the active family"""
        import SelectChild
        if self.active_person:
            SelectChild.SelectChild(self.database,self.active_family,
                                    self.active_person,self.load_family)

    def on_add_new_child_clicked(self,obj):
        """Create a new child to add to the existing family"""
        import SelectChild
        if self.active_person:
            SelectChild.NewChild(self.database,self.active_family,
                                 self.active_person,self.update_after_newchild,
                                 GrampsCfg.lastnamegen)

    def on_choose_parents_clicked(self,obj):
        import ChooseParents
        if self.active_person:
            ChooseParents.ChooseParents(self.database,self.active_person,
                                        self.active_parents,self.load_family,
                                        self.full_update)
    
    def on_new_clicked(self,obj):
        """Prompt for permission to close the current database"""
        msg = _("Do you want to close the current database and create a new one?")
        gnome.ui.GnomeQuestionDialog(msg,self.new_database_response)

    def new_database_response(self,val):
        import DbPrompter
        if val == 1:
            return
        self.clear_database()
        DbPrompter.DbPrompter(self,1)
    
    def clear_database(self):
        """Clear out the database if permission was granted"""
        const.personalEvents = const.init_personal_event_list()
        const.personalAttributes = const.init_personal_attribute_list()
        const.marriageEvents = const.init_marriage_event_list()
        const.familyAttributes = const.init_family_attribute_list()
        const.familyRelations = const.init_family_relation_list()
    
        self.database.new()
        self.topWindow.set_title("GRAMPS")
        self.active_person = None
        self.active_father = None
        self.active_family = None
        self.active_mother = None
        self.active_child  = None
        self.active_spouse = None
        self.id2col        = {}
        self.alt2col       = {}

        Utils.clearModified()
        Utils.clear_timer()
        self.change_active_person(None)
        self.person_list.clear()
        self.load_family()
        self.source_view.load_sources()
        self.place_view.load_places()
        self.media_view.load_media()
    
    def tool_callback(self,val):
        if val:
            Utils.modified()
            self.full_update()
        
    def full_update(self):
        """Brute force display update, updating all the pages"""
        self.id2col = {}
        self.alt2col = {}
        self.person_list.clear()
        self.notebook.set_show_tabs(GrampsCfg.usetabs)
        self.child_list.set_column_visibility(self.c_details,GrampsCfg.show_detail)
        self.child_list.set_column_visibility(self.c_id,GrampsCfg.id_visible)
        self.child_list.set_column_visibility(self.c_birth_order,GrampsCfg.index_visible)
        self.apply_filter()
        self.load_family()
        self.source_view.load_sources()
        self.place_view.load_places()
        self.pedigree_view.load_canvas(self.active_person)
        self.media_view.load_media()
        self.toolbar.set_style(GrampsCfg.toolbar)

    def update_display(self,changed):
        """Incremental display update, update only the displayed page"""
        page = self.notebook.get_current_page()
        if page == 0:
            if changed:
                self.apply_filter()
            else:
                self.goto_active_person()
        elif page == 1:
            self.load_family()
        elif page == 2:
            self.pedigree_view.load_canvas(self.active_person)
        elif page == 3:
            self.source_view.load_sources()
        elif page == 4:
            pass
        else:
            self.media_view.load_media()

    def on_tools_clicked(self,obj):
        if self.active_person:
            Plugins.ToolPlugins(self.database,self.active_person,
                                self.tool_callback)

    def on_reports_clicked(self,obj):
        if self.active_person:
            Plugins.ReportPlugins(self.database,self.active_person)

    def on_ok_button1_clicked(self,obj):
    
        dbname = obj.get_data("dbname")
        getoldrev = obj.get_data("getoldrev")
        filename = dbname.get_full_path(0)
        Utils.destroy_passed_object(obj)

        if filename == "" or filename == None:
            return
        
        self.clear_database()
    
        if getoldrev.get_active():
            vc = VersionControl.RcsVersionControl(filename)
            VersionControl.RevisionSelect(self.database,filename,vc,
                                          self.load_revision)
        else:
            self.auto_save_load(filename)

    def auto_save_load(self,filename):
    
        if os.path.isdir(filename):
            dirname = filename
        else:
            dirname = os.path.dirname(filename)
        autosave = "%s/autosave.gramps" % dirname

        if os.path.isfile(autosave):
            q = _("An autosave file exists for %s.\nShould this "
                  "be loaded instead of the last saved version?") % dirname
            self.yname = autosave
            self.nname = filename
            gnome.ui.GnomeQuestionDialog(q,self.autosave_query)
        else:
            self.read_file(filename)

    def autosave_query(self,value):
        if value == 0:
            self.read_file(self.yname)
        else:
            self.read_file(self.nname)
        
    def read_file(self,filename):
        base = os.path.basename(filename)
        if base == const.indexFile:
            filename = os.path.dirname(filename)
        elif base == "autosave.gramps":
            filename = os.path.dirname(filename)
        elif not os.path.isdir(filename):
            self.displayError(_("%s is not a directory") % filename)
            return

        self.statusbar.set_status(_("Loading %s ...") % filename)

        if self.load_database(filename) == 1:
            if filename[-1] == '/':
                filename = filename[:-1]
            name = os.path.basename(filename)
            self.topWindow.set_title("%s - %s" % (name,_("GRAMPS")))
        else:
            self.statusbar.set_status("")
            GrampsCfg.save_last_file("")

    def on_ok_button2_clicked(self,obj):
        filename = obj.get_filename()
        if filename:
            Utils.destroy_passed_object(obj)
            if GrampsCfg.usevc and GrampsCfg.vc_comment:
                self.display_comment_box(filename)
            else:
                self.save_file(filename,_("No Comment Provided"))

    def save_file(self,filename,comment):        

        path = filename
        filename = os.path.normpath(filename)
        autosave = "%s/autosave.gramps" % filename
    
        self.statusbar.set_status(_("Saving %s ...") % filename)

        Utils.clearModified()
        Utils.clear_timer()

        if os.path.exists(filename):
            if os.path.isdir(filename) == 0:
                self.displayError(_("%s is not a directory") % filename)
                return
        else:
            try:
                os.mkdir(filename)
            except (OSError,IOError), msg:
                emsg = _("Could not create %s") % filename + "\n" + str(msg)
                gnome.ui.GnomeErrorDialog(emsg)
                return
            except:
                gnome.ui.GnomeErrorDialog(_("Could not create %s") % filename)
                return
        
        old_file = filename
        filename = filename + os.sep + const.indexFile
        try:
            WriteXML.exportData(self.database,filename,self.load_progress)
        except (OSError,IOError), msg:
            emsg = _("Could not create %s") % filename + "\n" + str(msg)
            gnome.ui.GnomeErrorDialog(emsg)
            return

        self.database.setSavePath(old_file)
        GrampsCfg.save_last_file(old_file)

        if GrampsCfg.usevc:
            vc = VersionControl.RcsVersionControl(path)
            vc.checkin(filename,comment,not GrampsCfg.uncompress)

        filename = self.database.getSavePath()
        if filename[-1] == '/':
            filename = filename[:-1]
        name = os.path.basename(filename)
        self.topWindow.set_title("%s - %s" % (name,_("GRAMPS")))
        self.statusbar.set_status("")
        self.statusbar.set_progress(0)
        if os.path.exists(autosave):
            try:
                os.remove(autosave)
            except:
                pass

    def autosave_database(self):

        path = self.database.getSavePath()
        filename = os.path.normpath(path)
        Utils.clear_timer()

        filename = "%s/autosave.gramps" % (self.database.getSavePath())
    
        self.statusbar.set_status(_("autosaving..."));
        try:
            WriteXML.quick_write(self.database,filename,self.quick_progress)
            self.statusbar.set_status(_("autosave complete"));
        except (IOError,OSError),msg:
            self.statusbar.set_status("%s - %s" % (_("autosave failed"),msg))
        except:
            import traceback
            traceback.print_exc()
        return 0

    def load_selected_people(self,obj):
        """Display the selected people in the EditPerson display"""
        if len(self.person_list.selection) > 5:
            msg = _("You requested too many people to edit at the same time")
            gnome.ui.GnomeErrorDialog(msg)
        else:
            for p in self.person_list.selection:
                (person,x) = self.person_list.get_row_data(p)
                self.load_person(person)

    def load_active_person(self,obj):
        self.load_person(self.active_person)
    
    def on_edit_spouse_clicked(self,obj):
        """Display the active spouse in the EditPerson display"""
        self.load_person(self.active_spouse)

    def on_edit_mother_clicked(self,obj):
        """Display the active mother in the EditPerson display"""
        self.load_person(self.active_mother)

    def on_edit_father_clicked(self,obj):
        """Display the active father in the EditPerson display"""
        self.load_person(self.active_father)

    def load_new_person(self,obj):
        self.active_person = Person()
        EditPerson.EditPerson(self.active_person,self.database,
                              self.new_after_edit)

    def on_delete_person_clicked(self,obj):
        if len(self.person_list.selection) == 1:
            name = GrampsCfg.nameof(self.active_person) 
            msg = _("Do you really wish to delete %s?") % name
            gnome.ui.GnomeQuestionDialog(msg, self.delete_person_response)
        elif len(self.person_list.selection) > 1:
            msg = _("Currently, you can only delete one person at a time")
            gnome.ui.GnomeErrorDialog(msg)

    def delete_person_response(self,val):
        if val == 1:
            return
    
        personmap = self.database.getPersonMap()
        familymap = self.database.getPersonMap()

        for family in self.active_person.getFamilyList():
            if self.active_person.getGender == Person.male:
                if family.getMother() == None:
                    for child in family.getChildList():
                        child.removeAltFamily(family)
                    del familymap[family]
                else:
                    family.setFather(None)
            else:
                if family.getFather() == None:
                    for child in family.getChildList():
                        child.removeAltFamily(family)
                    del familymap[family]
                else:
                    family.setMother(None)

        family = self.active_person.getMainParents()
        if family:
            family.removeChild(self.active_person)
            
        del personmap[self.active_person.getId()]
        self.remove_from_person_list(self.active_person)
        self.person_list.sort()
        self.update_display(0)
        Utils.modified()

    def remove_from_person_list(self,person):
    
        self.person_list.freeze()
        if self.id2col.has_key(person):
            for id in [self.id2col[person]] + self.alt2col[person]:
                row = self.person_list.find_row_from_data(id)
                self.person_list.remove(row)

            del self.id2col[person]
            del self.alt2col[person]

            if row > self.person_list.rows:
                (self.active_person,x) = self.person_list.get_row_data(row)
        self.person_list.thaw()
    
    def merge_update(self,p1,p2):
        self.remove_from_person_list(p1)
        self.remove_from_person_list(p2)
        self.redisplay_person_list(p1)
    
    def on_delete_parents_clicked(self,obj):
        if not self.active_parents:
            return

        self.active_parents.removeChild(self.active_person)
        self.active_person.removeAltFamily(self.active_parents)
        self.load_family()
    
    def on_person_list_select_row(self,obj,row,b,c):
        if row == obj.selection[0]:
            (person,x) = obj.get_row_data(row)
            self.change_active_person(person)

    def on_person_list_click_column(self,obj,column):
        self.change_sort(column)

    def set_sort_arrow(self,column,direct):
        arrow = self.col_arr[column]
        for a in self.col_arr:
            if arrow != a:
                a.hide()
        arrow.show()
        if direct == GTK.SORT_ASCENDING:
            arrow.set(GTK.ARROW_DOWN,2)
        else:
            arrow.set(GTK.ARROW_UP,2)
    
    def change_sort(self,column,change=1):
        arrow = self.col_arr[column]
        for a in self.col_arr:
            if arrow != a:
                a.hide()
        arrow.show()

        self.person_list.set_sort_column(self.col_map[column])
        self.person_list.set_sort_type(self.sort_dir)

        self.sort_person_list()

        if change:
            if self.sort_col == column:
                if self.sort_dir == GTK.SORT_DESCENDING:
                    self.sort_dir = GTK.SORT_ASCENDING
                    arrow.set(GTK.ARROW_DOWN,2)
                else:
                    self.sort_dir = GTK.SORT_DESCENDING
                    arrow.set(GTK.ARROW_UP,2)
            else:
                self.sort_dir = GTK.SORT_ASCENDING
                arrow.set(GTK.ARROW_DOWN,2)
        self.sort_col = column

        if self.id2col.has_key(self.active_person):
            data = self.id2col[self.active_person]
            row = self.person_list.find_row_from_data(data)
            self.person_list.moveto(row)
        GrampsCfg.save_sort_cols("person",self.sort_col,self.sort_dir)
    
    def sort_person_list(self):
        self.person_list.freeze()
        self.person_list.sort()
        self.person_list.sort()
        if ListColors.get_enable():
            try:
                loddbg = ListColors.oddbg
                loddfg = ListColors.oddfg
                levenbg = ListColors.evenbg
                levenfg = ListColors.evenfg

                cmap = self.topWindow.get_colormap()
                oddbg = cmap.alloc(loddbg[0],loddbg[1],loddbg[2])
                oddfg = cmap.alloc(loddfg[0],loddfg[1],loddfg[2])
                evenbg = cmap.alloc(levenbg[0],levenbg[1],levenbg[2])
                evenfg = cmap.alloc(levenfg[0],levenfg[1],levenfg[2])
                rows = self.person_list.rows
                for i in range(0,rows,2):
                    self.person_list.set_background(i,oddbg)
                    self.person_list.set_foreground(i,oddfg)
                    if i != rows:
                        self.person_list.set_background(i+1,evenbg)
                        self.person_list.set_foreground(i+1,evenfg)
            except OverflowError:
                pass
        self.goto_active_person()
        self.person_list.thaw()
    
    def on_child_list_button_press_event(self,obj,event):
        if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
            self.load_person(self.active_child)

    def on_person_list_button_press(self,obj,event):
        if event.button == 1 and event.type == GDK._2BUTTON_PRESS:
            self.load_person(self.active_person)

    def goto_active_person(self,):
        if self.id2col.has_key(self.active_person):
            pos = self.id2col[self.active_person]
            column = self.person_list.find_row_from_data(pos)
            if column != -1:
                self.person_list.unselect_all()
                self.person_list.select_row(column,0)
                self.person_list.moveto(column)
            else:
                if self.person_list.rows > 0:
                    self.person_list.unselect_all()
                    self.person_list.select_row(0,0)
                    self.person_list.moveto(0)
                    (person,x) = self.person_list.get_row_data(0)
                    self.change_active_person(person)	
    
    def change_active_person(self,person):
        self.active_person = person
        self.modify_statusbar()
    
    def modify_statusbar(self):
        if self.active_person == None:
            self.statusbar.set_status("")
        else:
            pname = GrampsCfg.nameof(self.active_person)
            if GrampsCfg.status_bar == 1:
                name = "[%s] %s" % (self.active_person.getId(),pname)
            elif GrampsCfg.status_bar == 2:
                name = pname
                for attr in self.active_person.getAttributeList():
                    if attr.getType() == GrampsCfg.attr_name:
                        name = "[%s] %s" % (attr.getValue(),pname)
                        break
            else:
                name = pname
            self.statusbar.set_status(name)
        return 0
	
    def on_child_list_select_row(self,obj,row,b,c):
        self.active_child = obj.get_row_data(row)

    def on_child_list_click_column(self,clist,column):
        """Called when the user selects a column header on the self.person_list
        window. Change the sort function (column 0 is the name column, and
        column 2 is the birthdate column), set the arrows on the labels to
        the correct orientation, and then call apply_filter to redraw the
        list"""
        if column == self.c_name:
            self.child_change_sort(clist,self.c_name,self.cNameArrow)
        elif column == self.c_gender:
            self.child_change_sort(clist,self.c_gender,self.cGenderArrow)
        elif column == self.c_id:
            self.child_change_sort(clist,self.c_id,self.cIDArrow)
        elif column == self.c_birth_order or column == self.c_birth_date:
            self.child_change_sort(clist,self.c_birth_order,self.cDateArrow)
        else:
            return

        self.sort_child_list(clist)
        if self.id2col.has_key(self.active_child):
            row = clist.find_row_from_data(self.id2col[self.active_child])
            clist.moveto(row)

    def child_change_sort(self,clist,column,arrow):
        self.cNameArrow.hide()
        self.cDateArrow.hide()
        self.cIDArrow.hide()
        self.cGenderArrow.hide()
        arrow.show()
    
        if self.c_sort_col == column:
            if self.c_sort_dir == GTK.SORT_DESCENDING:
                self.c_sort_dir = GTK.SORT_ASCENDING
                arrow.set(GTK.ARROW_DOWN,2)
            else:
                self.c_sort_dir = GTK.SORT_DESCENDING
                arrow.set(GTK.ARROW_UP,2)
        else:
            self.c_sort_dir = GTK.SORT_ASCENDING
        self.c_sort_col = column
        clist.set_sort_type(self.c_sort_dir)
        clist.set_sort_column(self.c_sort_col)
        clist.set_reorderable(self.c_sort_col == self.c_birth_order)

    def sort_child_list(self,clist):
        clist.freeze()
        clist.sort()
        clist.sort()
        if ListColors.get_enable():
            try:
                loddbg = ListColors.oddbg
                loddfg = ListColors.oddfg
                levenbg = ListColors.evenbg
                levenfg = ListColors.evenfg
                lafg = ListColors.ancestorfg

                cmap = self.topWindow.get_colormap()
                oddbg = cmap.alloc(loddbg[0],loddbg[1],loddbg[2])
                oddfg = cmap.alloc(loddfg[0],loddfg[1],loddfg[2])
                evenbg = cmap.alloc(levenbg[0],levenbg[1],levenbg[2])
                evenfg = cmap.alloc(levenfg[0],levenfg[1],levenfg[2])
                ancestorfg = cmap.alloc(lafg[0],lafg[1],lafg[2])
                rows = clist.rows
                for i in range(0,rows):
                    clist.set_background(i,(evenbg,oddbg)[i%2])
                    person = clist.get_row_data(i)
                    if (person.getAncestor()):
                        clist.set_foreground(i,ancestorfg)
                    else:
                        clist.set_foreground(i,(evenfg,oddfg)[i%2])
            except OverflowError:
                pass
        clist.thaw()

    def on_child_list_row_move(self,clist,fm,to):
        """Validate whether or not this child can be moved within the clist.
        This routine is called in the middle of the clist's callbacks, so
        the state can be confusing.  If the code is being debugged, the
        display at this point shows that the list has been reordered when in
        actuality it hasn't.  All accesses to the clist data structure
        reference the state just prior to the move.
        
        This routine must keep/compute its own list indices as the functions
        list.remove(), list.insert(), list.reverse() etc. do not affect the
        values returned from the list.index() routine."""

        family = clist.get_data("f")

        # Create a list based upon the current order of the clist
        clist_order = []
        for i in range(clist.rows):
            clist_order = clist_order + [clist.get_row_data(i)]
        child = clist_order[fm]

        # This function deals with ascending order lists.  Convert if
        # necessary.
        if (self.c_sort_dir == GTK.SORT_DESCENDING):
            clist_order.reverse()
            max_index = len(clist_order) - 1
            fm = max_index - fm
            to = max_index - to
        
        # Create a new list to match the requested order
        desired_order = clist_order[:fm] + clist_order[fm+1:]
        desired_order = desired_order[:to] + [child] + desired_order[to:]

        # Check birth date order in the new list
        if (EditPerson.birth_dates_in_order(desired_order) == 0):
            clist.emit_stop_by_name("row_move")
            msg = _("Invalid move. Children must be ordered by birth date.")
            gnome.ui.GnomeWarningDialog(msg)
            return
           
        # OK, this birth order works too.  Update the family data structures.
        family.setChildList(desired_order)

        # Build a mapping of child item to list position.  This would not
        # be necessary if indices worked properly
        i = 0
        new_order = {}
        for tmp in desired_order:
            new_order[tmp] = i
            i = i + 1

        # Convert the original list back to whatever ordering is being
        # used by the clist itself.
        if (self.c_sort_dir == GTK.SORT_DESCENDING):
            clist_order.reverse()

        # Update the clist indices so any change of sorting works
        i = 0
        for tmp in clist_order:
            clist.set_text(i,self.c_birth_order,"%2d"%(new_order[tmp]+1))
            i = i + 1

        # Need to save the changed order
        Utils.modified()

    def on_open_activate(self,obj):
        wFs = libglade.GladeXML(const.revisionFile, "dbopen")
        wFs.signal_autoconnect({
            "on_ok_button1_clicked": self.on_ok_button1_clicked,
            "destroy_passed_object": Utils.destroy_passed_object
            })

        fileSelector = wFs.get_widget("dbopen")
        dbname = wFs.get_widget("dbname")
        getoldrev = wFs.get_widget("getoldrev")
        fileSelector.set_data("dbname",dbname)
        dbname.set_default_path(GrampsCfg.db_dir)
        fileSelector.set_data("getoldrev",getoldrev)
        getoldrev.set_sensitive(GrampsCfg.usevc)
        fileSelector.show()

    def on_revert_activate(self,obj):
        if self.database.getSavePath() != "":
            msg = _("Do you wish to abandon your changes and "
                    "revert to the last saved database?")
            gnome.ui.GnomeQuestionDialog(msg,self.revert_query)
        else:
            msg = _("Cannot revert to a previous database, since "
                    "one does not exist")
            gnome.ui.GnomeWarningDialog(msg)

    def revert_query(self,value):
        if value == 0:
            const.personalEvents = const.init_personal_event_list()
            const.personalAttributes = const.init_personal_attribute_list()
            const.marriageEvents = const.init_marriage_event_list()
            const.familyAttributes = const.init_family_attribute_list()
            const.familyRelations = const.init_family_relation_list()

            file = self.database.getSavePath()
            self.database.new()
            self.active_person = None
            self.active_father = None
            self.active_family = None
            self.active_mother = None
            self.active_child  = None
            self.active_spouse = None
            self.id2col        = {}
            self.alt2col       = {}
            self.read_file(file)
            Utils.clearModified()
            Utils.clear_timer()

    def on_save_as_activate(self,obj):
        wFs = libglade.GladeXML (const.gladeFile, "fileselection")
        wFs.signal_autoconnect({
            "on_ok_button1_clicked": self.on_ok_button2_clicked,
            "destroy_passed_object": Utils.destroy_passed_object
            })

        fileSelector = wFs.get_widget("fileselection")
        fileSelector.show()

    def on_save_activate(self,obj):
        """Saves the file, first prompting for a comment if revision
        control needs it"""
        if not self.database.getSavePath():
            self.on_save_as_activate(obj)
        else:
            if GrampsCfg.usevc and GrampsCfg.vc_comment:
                self.display_comment_box(self.database.getSavePath())
            else:
                msg = _("No Comment Provided")
                self.save_file(self.database.getSavePath(),msg)

    def on_save_activate_quit(self):
        """Saves the file, first prompting for a comment if revision
        control needs it"""
        if not self.database.getSavePath():
            self.on_save_as_activate(None)
        else:
            if GrampsCfg.usevc and GrampsCfg.vc_comment:
                self.display_comment_box(self.database.getSavePath())
            else:
                msg = _("No Comment Provided")
                self.save_file(self.database.getSavePath(),msg)

    def display_comment_box(self,filename):
        """Displays a dialog box, prompting for a revison control comment"""
        VersionControl.RevisionComment(filename,self.save_file)
    
    def on_person_list1_activate(self,obj):
        """Switches to the person list view"""
        self.notebook.set_page(0)

    def on_family1_activate(self,obj):
        """Switches to the family view"""
        self.notebook.set_page(1)

    def on_pedegree1_activate(self,obj):
        """Switches to the pedigree view"""
        self.notebook.set_page(2)

    def on_sources_activate(self,obj):
        """Switches to the sources view"""
        self.notebook.set_page(3)

    def on_places_activate(self,obj):
        """Switches to the places view"""
        self.notebook.set_page(4)

    def on_media_activate(self,obj):
        """Switches to the media view"""
        self.notebook.set_page(5)

    def on_notebook1_switch_page(self,obj,junk,page):
        """Load the appropriate page after a notebook switch"""
        if page == 0:
            self.goto_active_person()
            self.merge_button.set_sensitive(1)
        elif page == 1:
            self.merge_button.set_sensitive(0)
            self.load_family()
        elif page == 2:
            self.merge_button.set_sensitive(0)
            self.pedigree_view.load_canvas(self.active_person)
        elif page == 3:
            self.merge_button.set_sensitive(0)
            self.source_view.load_sources()
        elif page == 4:
            self.merge_button.set_sensitive(1)
        elif page == 5:
            self.merge_button.set_sensitive(0)
            self.media_view.load_media()
            
    def on_swap_clicked(self,obj):
        if not self.active_person:
            return

        if self.active_spouse:
            self.change_active_person(self.active_spouse)
            self.load_family()

    def on_apply_filter_clicked(self,obj):
        invert_filter = self.filter_inv.get_active()
        qualifer = self.filter_text.get_text()
        mi = self.filter_list.get_menu().get_active()
        class_init = mi.get_data("function")
        self.DataFilter = class_init(qualifer)
        self.DataFilter.set_invert(invert_filter)
        self.apply_filter()

    def on_filter_name_changed(self,obj):
        filter = obj.get_data("filter")
        qual = obj.get_data('qual')
        if qual:
            self.qual_label.show()
            self.qual_label.set_sensitive(1)
            self.qual_label.set_text(obj.get_data("label"))
            filter.show()
        else:
            self.qual_label.hide()
            filter.hide()
        filter.set_sensitive(qual)

    def on_preferred_rel_toggled(self,obj):
        self.active_person.setPreferred(self.active_family)
        self.load_family(self.active_family)
        Utils.modified()

    def on_preferred_fam_toggled(self,obj):
        self.active_person.setMainParents(self.active_parents)
        self.change_parents(self.active_parents)
        Utils.modified()
        
    def new_after_edit(self,epo,plist):
        if epo:
            if epo.person.getId() == "":
                self.database.addPerson(epo.person)
            else:
                self.database.addPersonNoMap(epo.person,epo.person.getId())
            self.change_active_person(epo.person)
            self.redisplay_person_list(epo.person)
        for p in plist:
            self.place_view.new_place_after_edit(p)

    def update_after_newchild(self,family,person,plist):
        self.load_family(family)
        self.redisplay_person_list(person)
        for p in plist:
            self.place_view.new_place_after_edit(p)

    def update_after_edit(self,epo,plist):
        if epo:
            self.remove_from_person_list(epo.person)
            self.redisplay_person_list(epo.person)
        for p in plist:
            self.place_view.new_place_after_edit(p)
        self.update_display(0)

    def redisplay_person_list(self,person):
        pos = (person,0)
        self.id2col[person] = pos
        self.alt2col[person] = []
        gname = Utils.phonebook_from_name
        if self.DataFilter.compare(person):
            if person.getGender() == Person.male:
                gender = const.male
            elif person.getGender() == Person.female:
                gender = const.female
            else:
                gender = const.unknown
            bday = person.getBirth().getDateObj()
            dday = person.getDeath().getDateObj()
            name = person.getPrimaryName()
            self.person_list.insert(0,[gname(name,0),person.getId(),
                                       gender,bday.getQuoteDate(),
                                       dday.getQuoteDate(),
                                       sort.build_sort_name(name),
                                       sort.build_sort_date(bday),
                                       sort.build_sort_date(dday)])

            self.person_list.set_row_data(0,pos)

            if GrampsCfg.hide_altnames == 0:
                for name in person.getAlternateNames():
                    pos2 = (person,0)
                    self.alt2col[person].append(pos2)
                    self.person_list.insert(0,[gname(name,1),person.getId(),
                                               gender,bday.getQuoteDate(),
                                               dday.getQuoteDate(),
                                               sort.build_sort_name(name),
                                               sort.build_sort_date(bday),
                                               sort.build_sort_date(dday)])

                    self.person_list.set_row_data(0,pos2)
        self.sort_person_list()

    def load_person(self,person):
        if person:
            EditPerson.EditPerson(person,self.database,
                                  self.update_after_edit)

    def build_spouse_dropdown(self):
        mymap = {}
        mynmap = {}
        list = []
        sel = None
        for f in self.active_person.getFamilyList():
            if self.active_person == f.getFather():
                sname = self.parent_name(f.getMother())
            else:
                sname = self.parent_name(f.getFather())
            c = self.list_item(sname,f)
            list.append(c)
            if f == self.active_family or sel == None:
                sel = c
            mymap[f] = c
            mynmap[f] = sname
        self.spouse_combo.disable_activate()
        self.spouse_combo.list.clear_items(0,-1)
        self.spouse_combo.list.append_items(list)
            
        for v in mymap.keys():
            self.spouse_combo.set_item_string(mymap[v],mynmap[v])
        self.spouse_combo.list.select_child(sel)

    def list_item(self,label,filter):
        l = gtk.GtkLabel(label)
        l.set_alignment(0,0.5)
        l.show()
        c = gtk.GtkListItem()
        c.add(l)
        c.set_data('d',filter)
        c.show()
        return c
        
    def parent_name(self,person):
        if person == None:
            return _("Unknown")
        else:
            return GrampsCfg.nameof(person)
        
    def load_family(self,family=None):
        if family != None:
            self.active_family = family
        elif self.active_person:
            flist = self.active_person.getFamilyList() 
            if len(flist) > 0:
                self.active_family = flist[0]
                
        if self.active_family:
            flist = self.active_person.getFamilyList()
            if self.active_person != self.active_family.getFather() and \
               self.active_person != self.active_family.getMother():
                if len(flist) > 0:
                    self.active_family = flist[0]
                else:
                    self.active_family = None
            
        family_types = []

        main_family = None
        self.person_text.set_text(GrampsCfg.nameof(self.active_person))

        if self.active_person:
            main_family = self.active_person.getMainParents()
            self.active_parents = main_family
            self.parents_index = 0
            family_types = self.active_person.getParentList()

            if self.active_parents == None and len(family_types) > 0:
                self.active_parents = family_types[0][0]
            if len(family_types) > 1:
                self.gtop.get_widget('multi_parents').show()
                self.gtop.get_widget('preffam').show()
            else:
                self.gtop.get_widget('multi_parents').hide()
                self.gtop.get_widget('preffam').hide()
        else:
            self.active_parents = None

        self.change_parents(self.active_parents)

        if self.active_person:
            flist = self.active_person.getFamilyList()
            number_of_families = len(flist)
            if number_of_families > 1:
                if self.active_family == None:
                    self.active_family = flist[0]

                self.pref_spouse.show()
                self.spouse_tab.set_page(1)
                if self.active_family == flist[0]:
                    self.pref_spouse.set_sensitive(0)
                    msg = _("Preferred Relationship")
                else:
                    msg = _("Relationship")
                    self.pref_spouse.set_sensitive(1)

                self.gtop.get_widget('rel_frame').set_label(msg)
                if self.active_person != self.active_family.getFather():
                    self.active_spouse = self.active_family.getFather()
                else:
                    self.active_spouse = self.active_family.getMother()

                self.build_spouse_dropdown()
                self.spouse_text.set_text(GrampsCfg.nameof(self.active_spouse))
                self.spouse_edit.set_sensitive(1)
                self.spouse_del.set_sensitive(1)
            elif number_of_families == 1:
                self.pref_spouse.hide()
                self.spouse_tab.set_page(0)
                f = self.active_person.getFamilyList()[0]
                if self.active_person != f.getFather():
                    spouse = f.getFather()
                else:
                    spouse = f.getMother()
                self.active_spouse = spouse
                self.spouse_text.set_text(GrampsCfg.nameof(spouse))
                self.spouse_edit.set_sensitive(1)
                self.spouse_del.set_sensitive(1)
                msg = _("Relationship")
                self.gtop.get_widget('rel_frame').set_label(msg)
            else:
                self.pref_spouse.hide()
                self.spouse_tab.set_page(0)
                self.spouse_text.set_text("")
                self.active_spouse = None
                self.spouse_edit.set_sensitive(0)
                self.spouse_del.set_sensitive(0)
                msg = _("No Relationship")
                self.gtop.get_widget('rel_frame').set_label()

            if number_of_families > 0:
                if not family:
                    family = self.active_person.getFamilyList()[0]
                self.display_marriage(family)
            else:
                self.display_marriage(None)
        else:
            self.active_spouse = None
            self.spouse_text.set_text("")
            self.display_marriage(None)

    def change_parents(self,family):
        """Switches to a different set of parents on the Family View"""
        
        if self.active_parents and self.active_parents.getRelationship() == "Partners":
            fn = _("Parent") 
            mn = _("Parent")
        else:
            fn = _("Father")
            mn = _("Mother")

        pframe = self.gtop.get_widget('parent_frame')
        if self.active_parents:
            val = len(self.active_person.getParentList())
            if self.active_parents == self.active_person.getMainParents():
                self.gtop.get_widget('preffam').set_sensitive(0)
                if val > 1:
                    msg = _("Preferred Parents (%d of %d)") % (self.parents_index+1,val)
                else:
                    msg = _("Preferred Parents")
            else:
                self.gtop.get_widget('preffam').set_sensitive(1)
                msg = _("Alternate Parents (%d of %d)") % (self.parents_index+1,val)
            pframe.set_label(msg)
        else:
            self.gtop.get_widget('parent_frame').set_label(_("No Parents"))
            

        self.gtop.get_widget("editFather").children()[0].set_text(fn)
        self.gtop.get_widget("editMother").children()[0].set_text(mn)

        fv_father = self.gtop.get_widget("fv_father")
        fv_mother = self.gtop.get_widget("fv_mother")
        father_next = self.gtop.get_widget("father_next")
        mother_next = self.gtop.get_widget("mother_next")

        self.gtop.get_widget("mrel").set_text('')
        self.gtop.get_widget("frel").set_text('')
    
        if family != None :
            self.active_father = family.getFather()
            if self.active_father != None :
                fv_father.set_text(GrampsCfg.nameof(self.active_father))
                father_next.set_sensitive(1)
            else :
                fv_father.set_text("")
                father_next.set_sensitive(0)

            self.active_mother = family.getMother()
            if self.active_mother != None :
                fv_mother.set_text(GrampsCfg.nameof(self.active_mother))
                mother_next.set_sensitive(1)
            else :
                fv_mother.set_text("")
                mother_next.set_sensitive(0)
            for f in self.active_person.getParentList():
                if f[0] == family:
                    self.gtop.get_widget("mrel").set_text(_(f[1]))
                    self.gtop.get_widget("frel").set_text(_(f[2]))
                    break
        elif self.active_person == None:
            fv_father.set_text("")
            fv_mother.set_text("")
            mother_next.set_sensitive(0)
            father_next.set_sensitive(0)
            self.active_father = None
            self.active_mother = None
        else :
            fv_father.set_text("")
            fv_mother.set_text("")
            mother_next.set_sensitive(0)
            father_next.set_sensitive(0)
            self.active_father = None
            self.active_mother = None

    def display_marriage(self,family):

        if self.active_person == None:
            return
        self.active_family = family
        fv_prev = self.gtop.get_widget("fv_prev")

        self.child_list.clear()
        self.active_child = None
        
        i = 0
        self.child_list.set_sort_type(self.c_sort_dir)
        self.child_list.set_sort_column(self.c_sort_col)
        self.child_list.set_reorderable(self.c_sort_col == self.c_birth_order)

        if family:
            if self.active_person == family.getFather():
                self.active_spouse = family.getMother()
            else:
                self.active_spouse = family.getFather()
            
            child_list = family.getChildList()
            child_list.sort(sort.by_birthdate)

            attr = ""
            for child in child_list:
                status = _("Unknown")
                if child.getGender() == Person.male:
                    gender = const.male
                elif child.getGender() == Person.female:
                    gender = const.female
                else:
                    gender = const.unknown
                for fam in child.getParentList():
                    if fam[0] == family:
                        if self.active_person == family.getFather():
                            status = "%s/%s" % (_(fam[2]),_(fam[1]))
                        else:
                            status = "%s/%s" % (_(fam[1]),_(fam[2]))

                if GrampsCfg.show_detail:
                    attr = ""
                    if child.getNote() != "":
                        attr = attr + "N"
                    if len(child.getEventList())>0:
                        attr = attr + "E"
                    if len(child.getAttributeList())>0:
                        attr = attr + "A"
                    if len(child.getFamilyList()) > 0:
                        for f in child.getFamilyList():
                            if f.getFather() and f.getMother():
                                attr = attr + "M"
                                break
                    if len(child.getPhotoList()) > 0:
                        attr = attr + "P"

                self.child_list.append(["%2d"%(i+1),
                                        GrampsCfg.nameof(child),
                                        child.getId(),
                                        gender,
                                        Utils.birthday(child),
                                        status,
                                        attr])
                self.child_list.set_row_data(i,child)
                i=i+1
                if i != 0:
                    fv_prev.set_sensitive(1)
                    self.child_list.select_row(0,0)
                else:	
                    fv_prev.set_sensitive(0)
            self.child_list.set_data("f",family)
            self.sort_child_list(self.child_list)
        else:
            self.active_spouse = None
            fv_prev.set_sensitive(0)
		
    def load_progress(self,value):
        self.statusbar.set_progress(value)
        while gtk.events_pending():
            gtk.mainiteration()

    def quick_progress(self,value):
        gtk.threads_enter()
        self.statusbar.set_progress(value)
        while gtk.events_pending():
            gtk.mainiteration()
        gtk.threads_leave()

    def post_load(self,name):
        self.database.setSavePath(name)
        res = self.database.getResearcher()
        owner = GrampsCfg.get_researcher()
    
        if res.getName() == "" and owner.getName() != "":
            self.database.setResearcher(owner)
            Utils.modified()

        self.setup_bookmarks()

        mylist = self.database.getPersonEventTypes()
        for type in mylist:
            ntype = const.display_pevent(type)
            if ntype not in const.personalEvents:
                const.personalEvents.append(ntype)

        mylist = self.database.getFamilyEventTypes()
        for type in mylist:
            ntype = const.display_fevent(type)
            if ntype not in const.marriageEvents:
                const.marriageEvents.append(ntype)

        mylist = self.database.getPersonAttributeTypes()
        for type in mylist:
            ntype = const.display_pattr(type)
            if ntype not in const.personalAttributes:
                const.personalAttributes.append(ntype)

        mylist = self.database.getFamilyAttributeTypes()
        for type in mylist:
            if type not in const.familyAttributes:
                const.familyAttributes.append(type)

        mylist = self.database.getFamilyRelationTypes()
        for type in mylist:
            if type not in const.familyRelations:
                const.familyRelations.append(type)

        GrampsCfg.save_last_file(name)
        self.gtop.get_widget("filter").set_text("")
    
        person = self.database.getDefaultPerson()
        if person:
            self.active_person = person
        for person in self.database.getPersonMap().values():
            if self.active_person == None:
                self.active_person = person
            lastname = person.getPrimaryName().getSurname()
            if lastname and lastname not in const.surnames:
                const.surnames.append(lastname)
                const.surnames.sort()

        self.statusbar.set_progress(1.0)
        self.full_update()
        self.statusbar.set_progress(0.0)
        return 1
    
    def load_database(self,name):
        filename = "%s/%s" % (name,const.indexFile)
        if ReadXML.loadData(self.database,filename,self.load_progress) == 0:
            return 0
        return self.post_load(name)

    def load_revision(self,f,name,revision):
        filename = "%s/%s" % (name,const.indexFile)
        if ReadXML.loadRevision(self.database,f,filename,revision,self.load_progress) == 0:
            return 0
        return self.post_load(name)

    def setup_bookmarks(self):
        self.bookmarks = Bookmarks.Bookmarks(self.database.getBookmarks(),
                                             self.gtop.get_widget("jump_to"),
                                             self.bookmark_callback)

    def displayError(self,msg):
        gnome.ui.GnomeErrorDialog(msg)
        self.statusbar.set_status("")

    def apply_filter(self):
        self.person_list.freeze()
        datacomp = self.DataFilter.compare
        gname = Utils.phonebook_from_name
        
        self.person_list.set_column_visibility(1,GrampsCfg.id_visible)
        new_alt2col = {}
    
        bsn = sort.build_sort_name
        bsd = sort.build_sort_date
        for person in self.database.getPersonMap().values():
            if datacomp(person):
                if self.id2col.has_key(person):
                    new_alt2col[person] = self.alt2col[person]
                    continue
                pos = (person,0)
                self.id2col[person] = pos
                new_alt2col[person] = []

                if person.getGender() == Person.male:
                    gender = const.male
                elif person.getGender() == Person.female:
                    gender = const.female
                else:
                    gender = const.unknown

                name = person.getPrimaryName()
                bday = person.getBirth().getDateObj()
                dday = person.getDeath().getDateObj()
                sort_bday = bsd(bday)
                sort_dday = bsd(dday)
                qbday = bday.getQuoteDate()
                qdday = dday.getQuoteDate()
                pid = person.getId()

                values = [gname(name,0), pid, gender, qbday, qdday,
                          bsn(name), sort_bday, sort_dday ]
                self.person_list.insert(0,values)
                self.person_list.set_row_data(0,pos)
                
                if GrampsCfg.hide_altnames:
                    continue

                for name in person.getAlternateNames():
                    pos = (person,1)
                    new_alt2col[person].append(pos)

                    values = [gname(name,1), pid, gender, qbday, qdday,
                              bsn(name), sort_bday, sort_dday]
                    self.person_list.insert(0,values)
                    self.person_list.set_row_data(0,pos)
                    
            else:
                if self.id2col.has_key(person):
                    pid = self.id2col[person]
                    del self.id2col[person]

                    for id in [pid] + self.alt2col[person]:
                        row = self.person_list.find_row_from_data(id)
                        self.person_list.remove(row)

        self.alt2col = new_alt2col
        self.person_list.thaw()
        self.sort_person_list()

    def on_home_clicked(self,obj):
        temp = self.database.getDefaultPerson()
        if temp:
            self.change_active_person(temp)
            self.update_display(0)
        else:
            gnome.ui.GnomeErrorDialog(_("No default/home person has been set"))

    def on_add_bookmark_activate(self,obj):
        self.bookmarks.add(self.active_person)
        name = GrampsCfg.nameof(self.active_person)
        self.statusbar.set_status(_("%s has been bookmarked") % name)
        gtk.timeout_add(5000,self.modify_statusbar)

    def on_edit_bookmarks_activate(self,obj):
        self.bookmarks.edit()
        
    def bookmark_callback(self,obj,person):
        self.change_active_person(person)
        self.update_display(0)
    
    def on_default_person_activate(self,obj):
        if self.active_person:
            name = self.active_person.getPrimaryName().getRegularName()
            msg = _("Do you wish to set %s as the home person?") % name
            gnome.ui.GnomeQuestionDialog(msg,self.set_person)

    def set_person(self,value):
        if not value:
            self.database.setDefaultPerson(self.active_person)
            Utils.modified()

    def family_up_clicked(self,obj):
        if self.active_parents == None:
            return
        flist = self.active_person.getParentList()
        if self.parents_index == 0:
            self.parents_index = len(flist)-1
        else:
            self.parents_index = self.parents_index - 1
        self.active_parents = flist[self.parents_index][0]
        self.change_parents(self.active_parents)

    def family_down_clicked(self,obj):
        if self.active_parents == None:
            return
        flist = self.active_person.getParentList()
        if self.parents_index == len(flist)-1:
            self.parents_index = 0
        else:
            self.parents_index = self.parents_index + 1
        self.active_parents = flist[self.parents_index][0]
        self.change_parents(self.active_parents)

    def spouse_list_changed(self,obj):
        if self.active_family == None:
            return
        select = self.spouse_combo.list.get_selection()
        if len(select) == 0:
            self.active_family = None
        else:
            self.active_family = select[0].get_data('d')

        if self.active_family == self.active_person.getFamilyList()[0]:
            self.pref_spouse.set_sensitive(0)
            msg = _("Preferred Relationship")
        else:
            msg = _("Relationship")
            self.pref_spouse.set_sensitive(1)
            
        self.gtop.get_widget('rel_frame').set_label(msg)
        
        self.display_marriage(self.active_family)

    def export_callback(self,obj,plugin_function):
        """Call the export plugin, with the active person and database"""
        if self.active_person:
            plugin_function(self.database,self.active_person)

    def import_callback(self,obj,plugin_function):
        """Call the import plugin"""
        plugin_function(self.database,self.active_person,self.tool_callback)
        self.topWindow.set_title("Gramps - " + self.database.getSavePath())

    def on_preferences_activate(self,obj):
        GrampsCfg.display_preferences_box(self.database)
    
    def menu_report(self,obj,task):
        """Call the report plugin selected from the menus"""
        if self.active_person:
            task(self.database,self.active_person)

    def menu_tools(self,obj,task):
        """Call the tool plugin selected from the menus"""
        if self.active_person:
            task(self.database,self.active_person,self.tool_callback)
    
    def on_main_key_release_event(self,obj,event):
        """Respond to the insert and delete buttons in the person list"""
        if event.keyval == GDK.Delete:
            self.on_delete_person_clicked(obj)
        elif event.keyval == GDK.Insert:
            self.load_new_person(obj)

#-------------------------------------------------------------------------
#
# Start it all
#
#-------------------------------------------------------------------------
if __name__ == '__main__':
    Gramps(None)
    gtk.mainloop()
