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
# Standard python modules
#
#-------------------------------------------------------------------------
import os

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
import gobject
import gtk
import gnome
import gnome.ui
import gtk.glade
import gtk.gdk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import RelLib
import GrampsDbBase
import GrampsBSDDB
import PedView
import MediaView
import PlaceView
import FamilyView
import SourceView
import PeopleView
import GenericFilter
import DisplayTrace
import const
import Plugins
import PluginMgr
import Utils
import Bookmarks
import GrampsKeys
import GrampsCfg
import EditPerson
import DbPrompter
import TipOfDay
import ArgHandler
import Exporter
import RelImage
import RecentFiles
import NameDisplay
import Errors
import GrampsDBCallback

from GrampsMime import mime_type_is_defined
from QuestionDialog import *
from bsddb import db

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_HOMEPAGE  = "http://gramps-project.org"
_MAILLIST  = "http://sourceforge.net/mail/?group_id=25770"
_BUGREPORT = "http://sourceforge.net/tracker/?group_id=25770&atid=385137"

PERSON_VIEW   = 0
FAMILY_VIEW1  = 1
FAMILY_VIEW2  = 2
PEDIGREE_VIEW = 3
SOURCE_VIEW   = 4
PLACE_VIEW    = 5
MEDIA_VIEW    = 6

#-------------------------------------------------------------------------
#
# Main GRAMPS class
#
#-------------------------------------------------------------------------
class Gramps(GrampsDBCallback.GrampsDBCallback):

    __signals__ = {
        'database-changed' : (GrampsDbBase.GrampsDbBase,),
        'active-changed' : (str,),
        }

    def __init__(self,args):

        GrampsDBCallback.GrampsDBCallback.__init__(self)
        
        try:
            self.program = gnome.program_init('gramps',const.version, 
                                              gnome.libgnome_module_info_get(),
                                              args, const.popt_table)
        except:
            self.program = gnome.program_init('gramps',const.version)
        self.program.set_property('app-libdir','%s/lib' % const.prefixdir)
        self.program.set_property('app-datadir','%s/share/gramps' % const.prefixdir)
        self.program.set_property('app-sysconfdir','%s/etc' % const.prefixdir)
        self.program.set_property('app-prefix', const.prefixdir)

        self.parents_index = 0
        self.active_person = None
        self.bookmarks = None
        self.c_details = 6
        self.cl = 0
        self.lock_history = False

        self.history = []
        self.mhistory = []
        self.hindex = -1

        self.undo_active = False
                
        self.db = GrampsBSDDB.GrampsBSDDB()

        try:
            GrampsCfg.loadConfig()
                
            self.welcome()    
            self.RelClass = PluginMgr.relationship_class
            self.relationship = self.RelClass(self.db)
            self.gtop = gtk.glade.XML(const.gladeFile, "gramps", "gramps")
        
            self.init_interface()
            
        except OSError,msg:
            ErrorDialog(_("Configuration error"),str(msg))
            return
        except Errors.GConfSchemaError, val:
            ErrorDialog(_("Configuration error"),
                        str(val) + _("\n\nPossibly the installation of GRAMPS was incomplete."
                          " Make sure the GConf schema of GRAMPS is properly installed."))
            gtk.main_quit()
            return
        except:
            DisplayTrace.DisplayTrace()
            return
            
        if not mime_type_is_defined(const.app_gramps):
            ErrorDialog(_("Configuration error"),
                        _("A definition for the MIME-type %s could not be found"
                          "\n\nPossibly the installation of GRAMPS was incomplete."
                          " Make sure the MIME-types of GRAMPS are properly installed.") % const.app_gramps)
            gtk.main_quit()
            return

        ArgHandler.ArgHandler(self,args)

        # Don't show main window until ArgHandler is done.
        # This prevents a window from annoyingly popping up when
        # the command line args are sufficient to operate without it.
        GrampsKeys.client.notify_add("/apps/gramps/researcher",
                                    self.researcher_key_update)
        GrampsKeys.client.notify_add("/apps/gramps/interface/statusbar",
                                    self.statusbar_key_update)
        GrampsKeys.client.notify_add("/apps/gramps/interface/toolbar",
                                    self.toolbar_key_update)
        GrampsKeys.client.notify_add("/apps/gramps/interface/toolbar-on",
                                    self.toolbar_on_key_update)
        GrampsKeys.client.notify_add("/apps/gramps/interface/filter",
                                    self.filter_key_update)
        GrampsKeys.client.notify_add("/apps/gramps/interface/view",
                                    self.sidebar_key_update)
        GrampsKeys.client.notify_add("/apps/gramps/interface/familyview",
                                    self.familyview_key_update)
        GrampsKeys.client.notify_add("/apps/gramps/preferences/name-format",
                                    self.familyview_key_update)
        GrampsKeys.client.notify_add("/apps/gramps/preferences/date-format",
                                    self.date_format_key_update)
        self.topWindow.show()
        
        if GrampsKeys.get_usetips():
            TipOfDay.TipOfDay(self)

        self.db.set_researcher(GrampsCfg.get_researcher())
        self.db.connect('person-delete',self.on_remove_bookmark)
        self.db.connect('person-update',self.on_update_bookmark)

    def welcome(self):
        if GrampsKeys.get_welcome() >= 200:
            return

        glade = gtk.glade.XML(const.gladeFile,'scrollmsg')
        top = glade.get_widget('scrollmsg')
        msg = glade.get_widget('msg')
        msg.get_buffer().set_text(
            _("Welcome to the 2.0.x series of GRAMPS!\n"
              "\n"
              "This version drastically differs from the 1.0.x branch\n"
              "in a few ways. Please read carefully, as this may affect\n"
              "the way you are using the program.\n"
              "\n"
              "1. This version works with the Berkeley database backend.\n"
              "   Because of this, changes are written to disk immediately.\n"
              "   There is NO Save function anymore!\n"
              "2. The Media object files are not managed by GRAMPS.\n"
              "   There is no concept of local objects, all objects\n"
              "   are external. You are in charge of keeping track of\n"
              "   your files. If you delete the image file from disk,\n"
              "   it will be lost!\n"
              "3. The version control provided by previous GRAMPS\n"
              "   versions has been removed. You may set up the versioning\n"
              "   system on your own if you'd like, but it will have to be\n"
              "   outside of GRAMPS.\n"
              "4. It is possible to directly open GRAMPS XML databases\n"
              "   (used by previous versions) as well as GEDCOM files.\n"
              "   However, any changes will be written to the disk when\n"
              "   you quit GRAMPS. In case of GEDCOM files, this may lead\n"
              "   to a data loss because some GEDCOM files contain data\n"
              "   that does not comply with the GEDCOM standard and cannot\n"
              "   be parsed by GRAMPS. If unsure, set up an empty grdb\n"
              "   database (new GRAMPS format) and import GEDCOM into it.\n"
              "   This will keep the original GEDCOM untouched.\n"
              "\n"
              "Enjoy!\n"
              "The GRAMPS project\n"))
        top.run()
        top.destroy()

        GrampsKeys.save_welcome(200)
        GrampsKeys.sync()

    def date_format_key_update(self,client,cnxn_id,entry,data):
        GrampsCfg.set_calendar_date_format()
        self.familyview_key_update(client,cnxn_id,entry,data)

    def researcher_key_update(self,client,cnxn_id,entry,data):
        self.db.set_person_id_prefix(GrampsKeys.get_person_id_prefix())
        self.db.set_family_id_prefix(GrampsKeys.get_family_id_prefix())
        self.db.set_source_id_prefix(GrampsKeys.get_source_id_prefix())
        self.db.set_object_id_prefix(GrampsKeys.get_object_id_prefix())
        self.db.set_place_id_prefix(GrampsKeys.get_place_id_prefix())
        self.db.set_event_id_prefix(GrampsKeys.get_event_id_prefix())

    def statusbar_key_update(self,client,cnxn_id,entry,data):
        self.modify_statusbar()

    def toolbar_key_update(self,client,cnxn_id,entry,data):
        the_style = GrampsKeys.get_toolbar()
        if the_style == -1:
            self.toolbar.unset_style()
        else:
            self.toolbar.set_style(the_style)

    def toolbar_on_key_update(self,client,cnxn_id,entry,data):
        is_on = GrampsKeys.get_toolbar_on()
        self.toolbar_btn.set_active(is_on)
        self.enable_toolbar(is_on)

    def filter_key_update(self,client,cnxn_id,entry,data):
        is_on = GrampsKeys.get_filter()
        self.filter_btn.set_active(is_on)
        self.enable_filter(is_on)

    def sidebar_key_update(self,client,cnxn_id,entry,data):
        is_on = GrampsKeys.get_view()
        self.sidebar_btn.set_active(is_on)
        self.enable_sidebar(is_on)

    def familyview_key_update(self,client,cnxn_id,entry,data):
        self.family_view.init_interface()
        self.update_display(1)
        self.goto_active_person()

    def init_interface(self):
        """Initializes the GLADE interface, and gets references to the
        widgets that it will need.
        """

        self.topWindow   = self.gtop.get_widget("gramps")

        self.report_button = self.gtop.get_widget("reports")
        self.tool_button  = self.gtop.get_widget("tools")
        self.remove_button  = self.gtop.get_widget("removebtn")
        self.edit_button  = self.gtop.get_widget("editbtn")
        self.remove_item  = self.gtop.get_widget("remove_item")
        self.edit_item  = self.gtop.get_widget("edit_item")
        self.sidebar = self.gtop.get_widget('side_event')
        self.filterbar = self.gtop.get_widget('filterbar')

        self.tool_button.set_sensitive(0)
        self.report_button.set_sensitive(0)
        self.remove_button.set_sensitive(0)
        self.edit_button.set_sensitive(0)
        self.remove_item.set_sensitive(0)
        self.edit_item.set_sensitive(0)

        set_panel(self.sidebar)
        set_panel(self.gtop.get_widget('side_people'))
        set_panel(self.gtop.get_widget('side_family'))
        set_panel(self.gtop.get_widget('side_pedigree'))
        set_panel(self.gtop.get_widget('side_sources'))
        set_panel(self.gtop.get_widget('side_places'))
        set_panel(self.gtop.get_widget('side_media'))

        self.sidebar_btn = self.gtop.get_widget("sidebar1")
        self.filter_btn  = self.gtop.get_widget("filter1")
        self.toolbar_btn = self.gtop.get_widget("toolbar2")
        self.statusbar   = self.gtop.get_widget("statusbar")
        self.progress    = self.statusbar.get_children()[0]
        self.progress.set_pulse_step(0.01)

        self.filter_list = self.gtop.get_widget("filter_list")
        self.views       = self.gtop.get_widget("views")
        self.merge_button= self.gtop.get_widget("merge")
        self.canvas      = self.gtop.get_widget("canvas1")
        self.toolbar     = self.gtop.get_widget("toolbar1")
        self.toolbardock = self.gtop.get_widget("dockitem2")
        self.filter_text = self.gtop.get_widget('filter')
        self.filter_label= self.gtop.get_widget('filter_label')
        self.filter_invert= self.gtop.get_widget('filter_invert')
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
        self.undolabel   = self.gtop.get_widget('undolabel')
        #self.redolabel   = self.gtop.get_widget('redolabel')
        self.open_recent = self.gtop.get_widget('open_recent1')

        self.child_model = gtk.ListStore(
            gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_STRING,
            gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, 
            gobject.TYPE_STRING,
            )

        self.build_plugin_menus()
        self.init_filters()

        self.build_recent_menu()

        the_style = GrampsKeys.get_toolbar()
        if the_style == -1:
            self.toolbar.unset_style()
        else:
            self.toolbar.set_style(the_style)
        self.views.set_show_tabs(0)

        self.family_view = FamilyView.FamilyView(self)
        self.people_view = PeopleView.PeopleView(self)
        
        self.pedigree_view = PedView.PedigreeView(
            self, self.canvas, self.modify_statusbar, self.statusbar,
            self.load_person
            )
        
        self.place_view  = PlaceView.PlaceView(self,self.db,self.gtop)
        self.source_view = SourceView.SourceView(self,self.db,self.gtop)
        self.media_view  = MediaView.MediaView(self,self.db,self.gtop,
                                               self.update_display)

        self.add_button = self.gtop.get_widget('addbtn')
        self.add_item = self.gtop.get_widget('add_item')
        self.backbtn = self.gtop.get_widget('back_btn')
        self.fwdbtn = self.gtop.get_widget('fwd_btn')
        self.gomenuitem = self.gtop.get_widget("go1")

        # FIXME: Horrible and ugly hack that works around a bug in
        # either gtk or libglade: button-press-event does not propagate
        # from ToolButton to the child.
        self.backbtn.get_children()[0].connect("button-press-event",self.back_pressed)
        self.fwdbtn.get_children()[0].connect("button-press-event",self.fwd_pressed)

        self.wins = self.gtop.get_widget("windows1")
        self.wins.set_submenu(gtk.Menu())
        self.winsmenu = self.wins.get_submenu()
        self.child_windows = {}

        self.gtop.signal_autoconnect({
            "on_undo_activate" : self.undo,
            "on_abandon_activate" : self.exit_and_undo,
            "on_column_order_activate": self.column_order,
            "on_back_clicked" : self.back_clicked,
            "on_scratchpad_clicked" : self.scratchpad_clicked,
            # FIXME: uncomment when fixed
            #"on_back_pressed" : self.back_pressed,
            "on_fwd_clicked" : self.fwd_clicked,
            # FIXME: uncomment when fixed
            #"on_fwd_pressed" : self.fwd_pressed,
            "on_editbtn_clicked" : self.edit_button_clicked,
            "on_addbtn_clicked" : self.add_button_clicked,
            "on_removebtn_clicked" : self.remove_button_clicked,
            "delete_event" : self.delete_event,
            "destroy_passed_object" : Utils.destroy_passed_object,
            "on_about_activate" : self.on_about_activate,
            "on_add_bookmark_activate" : self.on_add_bookmark_activate,
            "on_add_place_clicked" : self.place_view.on_add_place_clicked,
            "on_add_source_clicked" : self.source_view.on_add_clicked,
            "on_addperson_clicked" : self.load_new_person,
            "on_apply_filter_clicked" : self.on_apply_filter_clicked,
            "on_arrow_left_clicked" : self.pedigree_view.on_show_child_menu,
            "on_canvas1_event" : self.pedigree_view.on_canvas1_event,
            "on_contents_activate" : self.on_contents_activate,
            "on_faq_activate" : self.on_faq_activate,
            "on_default_person_activate" : self.on_default_person_activate,
            "on_delete_person_clicked" : self.delete_person_clicked,
            "on_delete_place_clicked" : self.place_view.on_delete_clicked,
            "on_delete_source_clicked" : self.source_view.on_delete_clicked,
            "on_delete_media_clicked" : self.media_view.on_delete_clicked,
            "on_edit_active_person" : self.load_active_person,
            "on_edit_selected_people" : self.load_selected_people,
            "on_edit_bookmarks_activate" : self.on_edit_bookmarks_activate,
            "on_exit_activate" : self.on_exit_activate,
            "on_family_activate" : self.on_family_activate,
            "on_family1_activate" : self.on_family1_activate,
            "on_family2_activate" : self.on_family2_activate,
            "on_home_clicked" : self.on_home_clicked,
            "on_new_clicked" : self.on_new_clicked,
            "on_notebook1_switch_page" : self.on_views_switch_page,
            "on_open_activate" : self.on_open_activate,
            "on_import_activate" : self.on_import_activate,
            "on_export_activate" : self.on_export_activate,
            "on_saveas_activate" : self.on_saveas_activate,
            "on_pedigree1_activate" : self.on_pedigree1_activate,
            "on_person_list1_activate" : self.on_person_list1_activate,
            "on_media_activate" : self.on_media_activate,
            "on_media_list_select_row" : self.media_view.on_select_row,
            "on_media_list_drag_data_get" : self.media_view.on_drag_data_get,
            "on_media_list_drag_data_received" : self.media_view.on_drag_data_received,
            "on_merge_activate" : self.on_merge_activate,
            "on_fast_merge1_activate" : self.on_fast_merge_activate,
            "on_sidebar1_activate" : self.on_sidebar_activate,
            "on_toolbar2_activate" : self.on_toolbar_activate,
            "on_filter1_activate" : self.on_filter_activate,
            "on_places_activate" : self.on_places_activate,
            "on_preferences1_activate" : self.on_preferences_activate,
            "on_reports_clicked" : self.on_reports_clicked,
            "on_revert_activate" : self.on_revert_activate,
            "on_show_plugin_status" : self.on_show_plugin_status,
            "on_source_list_button_press" : self.source_view.button_press,
            "on_sources_activate" : self.on_sources_activate,
            "on_tools_clicked" : self.on_tools_clicked,
            "on_gramps_home_page_activate" : self.home_page_activate,
            "on_gramps_report_bug_activate" : self.report_bug_activate,
            "on_gramps_mailing_lists_activate" : self.mailing_lists_activate,
            "on_open_example" : self.open_example,
            })

        self.filter_btn.set_active(GrampsKeys.get_filter())
        self.enable_filter(GrampsKeys.get_filter())
        self.toolbar_btn.set_active(GrampsKeys.get_toolbar_on())
        self.enable_toolbar(GrampsKeys.get_toolbar_on())

        if not GrampsKeys.get_screen_size_checked():
            GrampsKeys.save_screen_size_checked(1)
            if gtk.gdk.screen_width() <= 900:
                GrampsKeys.save_view(0)
        self.sidebar_btn.set_active(GrampsKeys.get_view())
        self.enable_sidebar(GrampsKeys.get_view())

        self.find_place = None
        self.find_source = None
        self.find_media = None

        if GrampsKeys.get_default_view() == 0:
            self.views.set_current_page(PERSON_VIEW)
        elif GrampsKeys.get_family_view() == 0:
            self.views.set_current_page(FAMILY_VIEW1)
        else:
            self.views.set_current_page(FAMILY_VIEW2)
      
        self.accel_group = gtk.AccelGroup()
        self.topWindow.add_accel_group(self.accel_group)
        self.back = gtk.ImageMenuItem(gtk.STOCK_GO_BACK)
        self.forward = gtk.ImageMenuItem(gtk.STOCK_GO_FORWARD)

    def build_recent_menu(self):
        gramps_rf = RecentFiles.GrampsRecentFiles()
        gramps_rf.gramps_recent_files.sort()
        gramps_rf.gramps_recent_files.reverse()
        recent_menu = gtk.Menu()
        recent_menu.show()
        index = 0
        for item in gramps_rf.gramps_recent_files:
            index = index + 1
            name = os.path.basename(item.get_path())
            if gtk.pygtk_version < (2,4,0):
                menu_item = gtk.MenuItem(name)
            else:
                menu_item = gtk.MenuItem(name,False)
            menu_item.connect("activate",self.recent_callback,
                            item.get_path(),item.get_mime())
            menu_item.show()
            recent_menu.append(menu_item)
        self.open_recent.set_submenu(recent_menu)

    def recent_callback(self,obj,filename,filetype):
        if os.path.exists(filename):
            DbPrompter.open_native(self,filename,filetype)
        else:
            ErrorDialog(_('File does not exist'),
                    _("The file %s cannot be found. "
                    "It will be removed from the list of recent files.") % filename )
            RecentFiles.remove_filename(filename)
            self.build_recent_menu()

    def undo_callback(self,text):
        self.undolabel.set_sensitive(bool(text))
        label = self.undolabel.get_children()[0]
        if text:
            label.set_text(text)
        else:
            label.set_text(_("_Undo"))
        label.set_use_underline(1)

    def redo_callback(self,text):
	return
        #self.redolabel.set_sensitive(bool(text))
        #label = self.redolabel.get_children()[0]
        #if text:
        #    label.set_text(text)
        #else:
        #    label.set_text(_("_Redo"))
        #label.set_use_underline(1)

    def undo(self,*args):
        """
        Undo signal handler - it is possible to reenter this routine too quickly if
        the user presses the C-z signal too quickly. So, we need to check to make sure
        we aren't already active.
        """
        if self.undo_active:
            return
        self.undo_active = True
        self.db.disable_signals()
        self.db.undo()
        self.db.enable_signals()
        self.db.request_rebuild()
        self.bookmarks.redraw()
        if self.active_person:
            p = self.db.get_person_from_handle(self.active_person.get_handle())
            self.change_active_person(p)
        self.undo_active = False

    def exit_and_undo(self,*args):
        self.db.disable_signals()
        self.db.abort_changes()
        gtk.main_quit()

    def set_person_column_order(self,list):
        self.db.set_person_column_order(list)
        self.people_view.build_columns()

    def set_child_column_order(self,list):
        self.db.set_child_column_order(list)
        self.family_view.build_columns()

    def set_place_column_order(self,list):
        self.db.set_place_column_order(list)
        self.place_view.build_columns()

    def set_source_column_order(self,list):
        self.db.set_source_column_order(list)
        self.source_view.build_columns()

    def set_media_column_order(self,list):
        self.db.set_media_column_order(list)
        self.media_view.build_columns()

    def column_order(self,obj):
        import ColumnOrder

        cpage = self.views.get_current_page()
        if cpage == PERSON_VIEW:
            ColumnOrder.ColumnOrder(self.db.get_person_column_order(),
                                    PeopleView.column_names,
                                    self.set_person_column_order)
        elif cpage == FAMILY_VIEW1 or cpage == FAMILY_VIEW2:
            ColumnOrder.ColumnOrder(self.db.get_child_column_order(),
                                    map(lambda x: x[0], FamilyView.column_names),
                                    self.set_child_column_order)
        elif cpage == SOURCE_VIEW:
            ColumnOrder.ColumnOrder(self.db.get_source_column_order(),
                                    SourceView.column_names,
                                    self.set_source_column_order)
        elif cpage == PLACE_VIEW:
            ColumnOrder.ColumnOrder(self.db.get_place_column_order(),
                                    PlaceView.column_names,
                                    self.set_place_column_order)
        elif cpage == MEDIA_VIEW:
            ColumnOrder.ColumnOrder(self.db.get_media_column_order(),
                                    MediaView.column_names,
                                    self.set_media_column_order)
        
    def clear_history(self):
        self.history = []
        self.mhistory = []
        self.hindex = -1
        self.back.set_sensitive(0)
        self.forward.set_sensitive(0)
        self.backbtn.set_sensitive(0)
        self.fwdbtn.set_sensitive(0)
        self.redraw_histmenu()

    def redraw_histmenu(self):
        """Create the history submenu of the Go menu"""

        # Start a brand new menu and create static items: 
        # back, forward, separator, home.
        gomenu = gtk.Menu()

        self.back.destroy()
        self.forward.destroy()

        self.back = gtk.ImageMenuItem(gtk.STOCK_GO_BACK)
        self.back.connect("activate",self.back_clicked)
        self.back.add_accelerator("activate", self.accel_group, 
                    gtk.gdk.keyval_from_name("Left"), 
                    gtk.gdk.MOD1_MASK, gtk.ACCEL_VISIBLE)
        self.back.show()
        gomenu.append(self.back)

        self.forward = gtk.ImageMenuItem(gtk.STOCK_GO_FORWARD)
        self.forward.connect("activate",self.fwd_clicked)
        self.forward.add_accelerator("activate", self.accel_group, 
                    gtk.gdk.keyval_from_name("Right"), 
                    gtk.gdk.MOD1_MASK, gtk.ACCEL_VISIBLE)
        self.forward.show()
        gomenu.append(self.forward)

        item = gtk.MenuItem()
        item.show()
        gomenu.append(item)

        #FIXME: revert to stock item when German gtk translation is fixed
        #item = gtk.ImageMenuItem(gtk.STOCK_HOME)
        item = gtk.ImageMenuItem(_("Home"))
        im = gtk.image_new_from_stock(gtk.STOCK_HOME,gtk.ICON_SIZE_MENU)
        im.show()
        item.set_image(im)
        item.connect("activate",self.on_home_clicked)
        item.add_accelerator("activate", self.accel_group, 
                    gtk.gdk.keyval_from_name("Home"), 
                    gtk.gdk.MOD1_MASK, gtk.ACCEL_VISIBLE)
        item.show()
        gomenu.append(item)

        try:
            if len(self.history) > 0:
                # Draw separator
                item = gtk.MenuItem()
                item.show()
                gomenu.append(item)
                
                pids = self.mhistory[:]
                pids.reverse()
                num = 0
                haveit = []
                for pid in pids:
                    if num >= 10:
                        break
                    if pid not in haveit:
                        haveit.append(pid)
                        person = self.db.get_person_from_handle(pid)
                        item = gtk.MenuItem("_%d. %s [%s]" % 
                                            (num,
                                             NameDisplay.displayer.display(person),
                                             person.get_gramps_id()))
                        item.connect("activate",self.bookmark_callback,
                                     person.get_handle())
                        item.show()
                        gomenu.append(item)
                        num = num + 1
            else:
                self.back.set_sensitive(0)
                self.forward.set_sensitive(0)
        except:
            self.clear_history()

        self.gomenuitem.remove_submenu()
        self.gomenuitem.set_submenu(gomenu)

    def build_backhistmenu(self,event):
        """Builds and displays the menu with the back portion of the history"""
        if self.hindex > 0:
            backhistmenu = gtk.Menu()
            backhistmenu.set_title(_('Back Menu'))
            pids = self.history[:self.hindex]
            pids.reverse()
            num = 1
            for pid in pids:
                if num <= 10:
                    f,r = divmod(num,10)
                    hotkey = "_%d" % r
                elif num <= 20:
                    hotkey = "_%s" % chr(ord('a')+num-11)
                elif num >= 21:
                    break
                person = self.db.get_person_from_handle(pid)
                item = gtk.MenuItem("%s. %s [%s]" % 
                    (hotkey,
                     NameDisplay.displayer.display(person),
                     person.get_gramps_id()))
                item.connect("activate",self.back_clicked,num)
                item.show()
                backhistmenu.append(item)
                num = num + 1
            backhistmenu.popup(None,None,None,event.button,event.time)

    def back_pressed(self,obj,event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_backhistmenu(event)

    def build_fwdhistmenu(self,event):
        """Builds and displays the menu with the forward portion of the history"""
        if self.hindex < len(self.history)-1:
            fwdhistmenu = gtk.Menu()
            fwdhistmenu.set_title(_('Forward Menu'))
            pids = self.history[self.hindex+1:]
            num = 1
            for pid in pids:
                if num <= 10:
                    f,r = divmod(num,10)
                    hotkey = "_%d" % r
                elif num <= 20:
                    hotkey = "_%s" % chr(ord('a')+num-11)
                elif num >= 21:
                    break
                person = self.db.get_person_from_handle(pid)
                item = gtk.MenuItem("%s. %s [%s]" % 
                    (hotkey,
                     NameDisplay.displayer.display(person),
                     person.get_gramps_id()))
                item.connect("activate",self.fwd_clicked,num)
                item.show()
                fwdhistmenu.append(item)
                num = num + 1
            fwdhistmenu.popup(None,None,None,event.button,event.time)

    def fwd_pressed(self,obj,event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            self.build_fwdhistmenu(event)

    def set_buttons(self,val):
        self.report_menu.set_sensitive(val)
        self.tools_menu.set_sensitive(val)
        self.report_button.set_sensitive(val)
        self.tool_button.set_sensitive(val)
        if self.views.get_current_page() == PERSON_VIEW:
            self.remove_button.set_sensitive(val)
            self.edit_button.set_sensitive(val)
            self.remove_item.set_sensitive(val)
            self.edit_item.set_sensitive(val)
        
    def scratchpad_clicked(self,obj):
        import ScratchPad
        ScratchPad.ScratchPadWindow(self.db, self)

    def back_clicked(self,obj,step=1):
        self.lock_history = True
        if self.hindex > 0:
            try:
                self.hindex -= step
                handle = str(self.history[self.hindex])
                self.active_person = self.db.get_person_from_handle(handle)
                self.modify_statusbar()
                self.emit('active-changed',(handle,))
                self.mhistory.append(self.history[self.hindex])
                self.redraw_histmenu()
                self.set_buttons(1)
                if self.hindex == 0:
                    self.backbtn.set_sensitive(0)
                    self.back.set_sensitive(0)
                else:
                    self.backbtn.set_sensitive(1)
                    self.back.set_sensitive(1)
                self.fwdbtn.set_sensitive(1)
                self.forward.set_sensitive(1)
            except:
                self.clear_history()
        else:
            self.backbtn.set_sensitive(0)
            self.back.set_sensitive(0)
            self.fwdbtn.set_sensitive(1)
            self.forward.set_sensitive(1)
        self.goto_active_person()
        self.lock_history = False

    def fwd_clicked(self,obj,step=1):
        self.lock_history = True
        if self.hindex+1 < len(self.history):
            try:
                self.hindex += step
                handle = str(self.history[self.hindex])
                self.active_person = self.db.get_person_from_handle(handle)
                self.modify_statusbar()
                self.emit('active-changed',(handle,))
                self.mhistory.append(self.history[self.hindex])
                self.redraw_histmenu()
                self.set_buttons(1)
                if self.hindex == len(self.history)-1:
                    self.fwdbtn.set_sensitive(0)
                    self.forward.set_sensitive(0)
                else:
                    self.fwdbtn.set_sensitive(1)
                    self.forward.set_sensitive(1)
                self.backbtn.set_sensitive(1)
                self.back.set_sensitive(1)
            except:
                self.clear_history()
        else:
            self.fwdbtn.set_sensitive(0)
            self.forward.set_sensitive(0)
            self.backbtn.set_sensitive(1)
            self.back.set_sensitive(1)
        self.goto_active_person()
        self.lock_history = False

    def edit_button_clicked(self,obj):
        cpage = self.views.get_current_page()
        if cpage == PERSON_VIEW:
            self.load_selected_people(obj)
        elif cpage == FAMILY_VIEW2 or cpage == FAMILY_VIEW1:
            self.load_person(self.active_person)
        elif cpage == SOURCE_VIEW:
            self.source_view.on_edit_clicked(obj)
        elif cpage == PLACE_VIEW:
            self.place_view.on_edit_clicked(obj)
        elif cpage == MEDIA_VIEW:
            self.media_view.on_edit_clicked(obj)

    def add_button_clicked(self,obj):
        cpage = self.views.get_current_page()
        if cpage == PERSON_VIEW or cpage == FAMILY_VIEW2 or cpage == FAMILY_VIEW1:
            self.load_new_person(obj)
        elif cpage == SOURCE_VIEW:
            self.source_view.on_add_clicked(obj)
        elif cpage == PLACE_VIEW:
            self.place_view.on_add_place_clicked(obj)
        elif cpage == MEDIA_VIEW:
            self.media_view.on_add_clicked(obj)

    def remove_button_clicked(self,obj):
        cpage = self.views.get_current_page()
        if cpage == PERSON_VIEW or cpage == FAMILY_VIEW2 or cpage == FAMILY_VIEW1:
            self.delete_person_clicked(obj)
        elif cpage == SOURCE_VIEW:
            self.source_view.on_delete_clicked(obj)
        elif cpage == PLACE_VIEW:
            self.place_view.on_delete_clicked(obj)
        elif cpage == MEDIA_VIEW:
            self.media_view.on_delete_clicked(obj)

    def enable_buttons(self,val):
        if self.db.readonly:
            mode = False
        else:
            mode = val
        self.add_button.set_sensitive(mode)
        self.remove_button.set_sensitive(mode)
        self.add_item.set_sensitive(mode)
        self.remove_item.set_sensitive(mode)

        self.edit_button.set_sensitive(val)
        self.edit_item.set_sensitive(val)
            
    def on_show_plugin_status(self,obj):
        Plugins.PluginStatus(self)

    def on_sidebar_activate(self,obj):
        self.enable_sidebar(obj.get_active())
        GrampsKeys.save_view(obj.get_active())

    def enable_sidebar(self,val):
        if val:
            self.sidebar.show()
            self.views.set_show_tabs(0)
        else:
            self.sidebar.hide()
            self.views.set_show_tabs(1)

    def enable_filter(self,val):
        if val:
            self.filterbar.show()
        else:
            self.filterbar.hide()
        
    def on_filter_activate(self,obj):
        GrampsKeys.save_filter(obj.get_active())

    def on_toolbar_activate(self,obj):
        GrampsKeys.save_toolbar_on(obj.get_active())

    def enable_toolbar(self,val):
        if val:
            self.toolbardock.show()
        else:
            self.toolbardock.hide()

    def build_plugin_menus(self):
        self.report_menu = self.gtop.get_widget("reports_menu")
        self.tools_menu  = self.gtop.get_widget("tools_menu")

        self.report_menu.set_sensitive(0)
        self.tools_menu.set_sensitive(0)

        error  = PluginMgr.load_plugins(const.docgenDir)
        error |= PluginMgr.load_plugins(os.path.expanduser("~/.gramps/docgen"))
        error |= PluginMgr.load_plugins(const.pluginsDir)
        error |= PluginMgr.load_plugins(os.path.expanduser("~/.gramps/plugins"))

        if GrampsKeys.get_pop_plugin_status() and error:
            Plugins.PluginStatus(self)
        Plugins.build_report_menu(self.report_menu,self.menu_report)
        Plugins.build_tools_menu(self.tools_menu,self.menu_tools)

        self.RelClass = PluginMgr.relationship_class
        self.relationship = self.RelClass(self.db)

    def init_filters(self):

        cell = gtk.CellRendererText()
        self.filter_list.clear()
        self.filter_list.pack_start(cell,True)
        self.filter_list.add_attribute(cell,'text',0)

        filter_list = []

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
        self.filter_text.set_sensitive(0)
        
    def home_page_activate(self,obj):
        gnome.url_show(_HOMEPAGE)

    def mailing_lists_activate(self,obj):
        gnome.url_show(_MAILLIST)

    def report_bug_activate(self,obj):
        gnome.url_show(_BUGREPORT)

    def on_fast_merge_activate(self,obj):
        """Calls up the merge dialog for the selection"""
        page = self.views.get_current_page()
        if page == PERSON_VIEW:

            mlist = self.people_view.get_selected_objects()

            if len(mlist) != 2:
                msg = _("Cannot merge people.")
                msg2 = _("Exactly two people must be selected to perform a merge. "
                         "A second person can be selected by holding down the "
                         "control key while clicking on the desired person.")
                ErrorDialog(msg,msg2)
            else:
                import MergePeople
                p1 = self.db.get_person_from_handle(mlist[0])
                p2 = self.db.get_person_from_handle(mlist[1])
                if p1 and p2:
                    merger = MergePeople.MergePeopleUI(self.db,p1,p2,self.merge_update)
                else:
                    msg = _("Cannot merge people.")
                    msg2 = _("Exactly two people must be selected to perform a merge. "
                             "A second person can be selected by holding down the "
                             "control key while clicking on the desired person.")
                    ErrorDialog(msg,msg2)
        elif page == PLACE_VIEW:
            self.place_view.merge()
        elif page == SOURCE_VIEW:
            self.source_view.merge()

    def on_merge_activate(self,obj):
        """Calls up the merge dialog for the selection"""
        page = self.views.get_current_page()
        if page == PERSON_VIEW:

            mlist = self.people_view.get_selected_objects()

            if len(mlist) != 2:
                msg = _("Cannot merge people.")
                msg2 = _("Exactly two people must be selected to perform a merge. "
                         "A second person can be selected by holding down the "
                         "control key while clicking on the desired person.")
                ErrorDialog(msg,msg2)
            else:
                import MergePeople
                p1 = self.db.get_person_from_handle(mlist[0])
                p2 = self.db.get_person_from_handle(mlist[1])
                if p1 and p2:
                    merger = MergePeople.Compare(self.db,p1,p2,self.merge_update)
                else:
                    msg = _("Cannot merge people.")
                    msg2 = _("Exactly two people must be selected to perform a merge. "
                             "A second person can be selected by holding down the "
                             "control key while clicking on the desired person.")
                    ErrorDialog(msg,msg2)
        elif page == PLACE_VIEW:
            self.place_view.merge()
        elif page == SOURCE_VIEW:
            self.source_view.merge()

    def delete_event(self,widget, event):
        """Catch the destruction of the top window, prompt to save if needed"""
        self.on_exit_activate(widget)
        return 1

    def on_exit_activate(self,obj):
        """Prompt to save on exit if needed"""
        self.db.close()
        gtk.main_quit()

    def quit(self):
        """Catch the reponse to the save on exit question"""
        self.db.close()
        gtk.main_quit()
        
    def close_noquit(self):
        """Close database and delete abandoned photos, no quit"""
        self.db.close()

    def on_about_activate(self,obj):
        """Displays the about box.  Called from Help menu"""
        pixbuf = gtk.gdk.pixbuf_new_from_file(const.logo)

        if const.translators[0:11] == "TRANSLATORS":
            trans = ''
        else:
            trans = const.translators
        
        gnome.ui.About(const.progName,
                       const.version,
                       const.copyright,
                       const.comments,
                       const.authors,
                       const.documenters,
                       trans,
                       pixbuf).show()
    
    def on_contents_activate(self,obj):
        """Display the GRAMPS manual"""
        try:
            gnome.help_display('gramps-manual','index')
        except gobject.GError, msg:
            ErrorDialog(_("Could not open help"),str(msg))

    def on_faq_activate(self,obj):
        """Display FAQ"""
        try:
            gnome.help_display('gramps-manual','faq')
        except gobject.GError, msg:
            ErrorDialog(_("Could not open help"),str(msg))

    def on_new_clicked(self,obj):
        """Prompt for permission to close the current database"""
        prompter = DbPrompter.NewNativeDbPrompter(self,self.topWindow)
        prompter.chooser()

    def clear_database(self):
        """Clear out the database if permission was granted"""
        return
    
    def tool_callback(self,epo,val):
        if val:
            self.import_tool_callback()

    def import_tool_callback(self):
        home = self.db.get_default_person()
        if home:
            self.change_active_person(home)
            self.update_display(0)
            self.goto_active_person()
        self.full_update()
            
    def full_update(self):
        """Brute force display update, updating all the pages"""
        if Utils.wasHistory_broken():
            self.clear_history()
            Utils.clearHistory_broken()
        self.emit('database-changed',(self.db,))
        if not self.active_person:
            self.change_active_person(self.find_initial_person())
        self.goto_active_person()

    def update_display(self,changed=True):
        """Incremental display update, update only the displayed page"""
        page = self.views.get_current_page()
        if page == PERSON_VIEW:
            self.people_view.apply_filter()
        elif page == PEDIGREE_VIEW:
            self.pedigree_view.load_canvas(self.active_person)

    def on_tools_clicked(self,obj):
        if self.active_person:
            Plugins.ToolPlugins(self,self.db,self.active_person,
                                self.tool_callback)

    def on_reports_clicked(self,obj):
        if self.active_person:
            Plugins.ReportPlugins(self,self.db,self.active_person)

    def read_pkg(self,filename):
        # Create tempdir, if it does not exist, then check for writability
        tmpdir_path = os.path.expanduser("~/.gramps/tmp" )
        if not os.path.isdir(tmpdir_path):
            try:
                os.mkdir(tmpdir_path,0700)
            except:
                DisplayTrace.DisplayTrace()
                return
        elif not os.access(tmpdir_path,os.W_OK):
            ErrorDialog( _("Cannot unpak archive"),
                        _("Temporary directory %s is not writable") % tmpdir_path )
            return
        else:    # tempdir exists and writable -- clean it up if not empty
            files = os.listdir(tmpdir_path) ;
            for fn in files:
                os.remove( os.path.join(tmpdir_path,fn) )

        try:
            import TarFile
            t = TarFile.ReadTarFile(filename,tmpdir_path)
            t.extract()
            t.close()
        except:
            DisplayTrace.DisplayTrace()
            return

        dbname = os.path.join(tmpdir_path,const.xmlFile)  

        try:
            import ReadXML
            ReadXML.importData(self.db,dbname,self.update_bar)
        except:
            DisplayTrace.DisplayTrace()

        # Clean up tempdir after ourselves
        files = os.listdir(tmpdir_path) 
        for fn in files:
            os.remove(os.path.join(tmpdir_path,fn))
        os.rmdir(tmpdir_path)
        self.import_tool_callback()

    def update_bar(self,percent):
        if percent:
            self.progress.pulse()
        else:
            self.progress.set_fraction(0)

    def read_file(self,filename,callback=None):
        mode = "w"
        filename = os.path.normpath(os.path.abspath(filename))
        
        if os.path.isdir(filename):
            ErrorDialog(_('Cannot open database'),
                        _('The selected file is a directory, not '
                          'a file.\nA GRAMPS database must be a file.'))
            return 0
        elif os.path.exists(filename):
            if not os.access(filename,os.R_OK):
                ErrorDialog(_('Cannot open database'),
                            _('You do not have read access to the selected '
                              'file.'))
                return 0
            elif not os.access(filename,os.W_OK):
                mode = "r"
                WarningDialog(_('Read only database'),
                              _('You do not have write access to the selected '
                                'file.'))

        try:
            if self.load_database(filename,callback,mode=mode) == 1:
                if filename[-1] == '/':
                    filename = filename[:-1]
                name = os.path.basename(filename)
                if self.db.readonly:
                    self.topWindow.set_title("%s (%s) - GRAMPS" % (name,_('Read Only')))
                else:
                    self.topWindow.set_title("%s - GRAMPS" % name)
            else:
                GrampsKeys.save_last_file("")
                ErrorDialog(_('Cannot open database'),
                            _('The database file specified could not be opened.'))
                return 0
        except ( IOError, OSError, Errors.FileVersionError), msg:
            ErrorDialog(_('Cannot open database'),str(msg))
            return 0
        except (db.DBAccessError,db.DBError), msg:
            ErrorDialog(_('Cannot open database'),
                        _('%s could not be opened.' % filename) + '\n' + msg[1])
            return 0
        except Exception:
            DisplayTrace.DisplayTrace()
            return 0
        
        # Undo/Redo always start with standard labels and insensitive state
        self.undo_callback(None)
        self.redo_callback(None)
        # The rest depends on readonly-ness of the database
        self.gtop.get_widget('import1').set_sensitive(not self.db.readonly)
        self.gtop.get_widget('abandon').set_sensitive(not self.db.readonly)
        self.gtop.get_widget('add_item').set_sensitive(not self.db.readonly)
        self.gtop.get_widget('remove_item').set_sensitive(not self.db.readonly)
        self.gtop.get_widget('merge').set_sensitive(not self.db.readonly)
        self.gtop.get_widget('fast_merge1').set_sensitive(not self.db.readonly)
        self.gtop.get_widget('default_person1').set_sensitive(not self.db.readonly)
        self.gtop.get_widget('add_bookmark').set_sensitive(not self.db.readonly)
        self.gtop.get_widget('edit_bookmarks').set_sensitive(not self.db.readonly)
        self.gtop.get_widget('tools_menu').set_sensitive(not self.db.readonly)
        self.gtop.get_widget('tools').set_sensitive(not self.db.readonly)

        self.goto_active_person()
        return 1

    def save_media(self,filename):
        missmedia_action = 0
        #-------------------------------------------------------------------------
        def remove_clicked():
            # File is lost => remove all references and the object itself
            for p in self.db.get_family_handle_map().values():
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference_handle() == ObjectId:
                        nl.remove(o) 
                p.set_media_list(nl)
            for key in self.db.get_person_handles(sort_handles=False):
                p = self.db.get_person_from_handle(key)
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference_handle() == ObjectId:
                        nl.remove(o) 
                p.set_media_list(nl)
            for key in self.db.get_source_handles():
                p = self.db.get_source_from_handle(key)
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference_handle() == ObjectId:
                        nl.remove(o) 
                p.set_media_list(nl)
            for key in self.db.get_place_handles():
                p = self.db.get_place_from_handle(key)
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference_handle() == ObjectId:
                        nl.remove(o) 
                p.set_media_list(nl)

            trans = self.db.transaction_begin()
            self.db.remove_object(ObjectId)
            self.db.transaction_commit(trans,_("Save Media Object"))
    
        def leave_clicked():
            # File is lost => do nothing, leave as is
            pass

        def select_clicked():
            choose = gtk.FileChooserDialog('Open GRAMPS database',
                                           None,
                                           gtk.FILE_CHOOSER_ACTION_OPEN,
                                           (gtk.STOCK_CANCEL,
                                            gtk.RESPONSE_CANCEL,
                                            gtk.STOCK_OPEN,
                                            gtk.RESPONSE_OK))
            
            mime_filter = gtk.FileFilter()
            mime_filter.set_name(_('All files'))
            mime_filter.add_pattern('*')
            choose.add_filter(mime_filter)
        
            response = choose.run()
            if response == gtk.RESPONSE_OK:
                name = choose.get_filename()
                if os.path.isfile(name):
                    obj = self.db.get_object_from_handle(ObjectId)
                    obj.set_path(name)
            choose.destroy()

        #-------------------------------------------------------------------------
        for ObjectId in self.db.get_media_object_handles():
            obj = self.db.get_object_from_handle(ObjectId)
            if 0:
                oldfile = obj.get_path()
                (base,ext) = os.path.splitext(os.path.basename(oldfile))
                newfile = os.path.join(filename,os.path.basename(oldfile))
                obj.set_path(newfile)
                if os.path.isfile(oldfile):
                    RelImage.import_media_object(oldfile,filename,base)
                else:
                    if self.cl:
                        print "Warning: media file %s was not found," \
                            % os.path.basename(oldfile), "so it was ignored."
                    else:
                        # File is lost => ask what to do
                        if missmedia_action == 0:
                            mmd = MissingMediaDialog(
                                _("Media object could not be found"),
                                _("%(file_name)s is referenced in the database, but no longer exists. " 
                                  "The file may have been deleted or moved to a different location. " 
                                  "You may choose to either remove the reference from the database, " 
                                  "keep the reference to the missing file, or select a new file." 
                                  ) % { 'file_name' : oldfile },
                                remove_clicked, leave_clicked, select_clicked)
                            missmedia_action = mmd.default_action
                        elif missmedia_action == 1:
                            remove_clicked()
                        elif missmedia_action == 2:
                            leave_clicked()
                        elif missmedia_action == 3:
                            select_clicked()

    def load_selected_people(self,obj):
        """Display the selected people in the EditPerson display"""
        mlist = self.people_view.get_selected_objects()
        if mlist and self.active_person.get_handle() == mlist[0]:
            self.load_person(self.active_person)

    def load_active_person(self,obj):
        self.load_person(self.active_person)

    def load_new_person(self,obj):
        person = RelLib.Person()
        try:
            EditPerson.EditPerson(self, person, self.db,
                                  self.new_after_edit)
        except:
            DisplayTrace.DisplayTrace()

    def delete_person_clicked(self,obj):
        cpage = self.views.get_current_page()
        if cpage == PERSON_VIEW:
            mlist = self.people_view.get_selected_objects()
        else:
            mlist = [ self.active_person.get_handle() ]

        if len(mlist) == 0:
            return
        
        for sel in mlist:
            p = self.db.get_person_from_handle(sel)
            self.active_person = p
            name = NameDisplay.displayer.display(p) 

            msg = _('Deleting the person will remove the person '
                             'from the database.')
            msg = "%s %s" % (msg,Utils.data_recover_msg)
            QuestionDialog(_('Delete %s?') % name,msg,
                           _('_Delete Person'),
                           self.delete_person_response)

    def disable_interface(self):
        self.remove_button.set_sensitive(False)
        self.edit_button.set_sensitive(False)
        self.add_button.set_sensitive(False)
    
    def enable_interface(self):
        self.remove_button.set_sensitive(True)
        self.edit_button.set_sensitive(True)
        self.add_button.set_sensitive(True)

    def delete_person_response(self):
        self.disable_interface()
        trans = self.db.transaction_begin()
        
        n = NameDisplay.displayer.display(self.active_person)

        if self.db.get_default_person() == self.active_person:
            self.db.set_default_person_handle(None)

        for family_handle in self.active_person.get_family_handle_list():
            if not family_handle:
                continue
            family = self.db.get_family_from_handle(family_handle)
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
                    child = self.db.get_person_from_handle(child_handle)
                    child.remove_parent_family_handle(family_handle)
                    self.db.commit_person(child,trans)
                self.db.remove_family(family_handle,trans)
            else:
                self.db.commit_family(family,trans)

        for (family_handle,mrel,frel) in self.active_person.get_parent_family_handle_list():
            family = self.db.get_family_from_handle(family_handle)
            if family:
                family.remove_child_handle(self.active_person.get_handle())
                self.db.commit_family(family,trans)
                
                # Purge empty family
                if len(family.get_child_handle_list()) == 0:
                    if not family.get_father_handle():
                        mother = self.db.get_person_from_handle( family.get_mother_handle())
                        if mother:
                            mother.remove_family_handle( family_handle)
                            self.db.commit_person( mother,trans)
                            self.db.remove_family(family_handle,trans)
                    if not family.get_mother_handle():
                        father = self.db.get_person_from_handle( family.get_father_handle())
                        if father:
                            father.remove_family_handle( family_handle)
                            self.db.commit_person( father,trans)
                            self.db.remove_family(family_handle,trans)

        handle = self.active_person.get_handle()

        person = self.active_person
        self.people_view.remove_from_person_list(person)
        self.people_view.remove_from_history(handle)
        self.db.remove_person(handle, trans)

        if self.hindex >= 0:
            self.active_person = self.db.get_person_from_handle(self.history[self.hindex])
        else:
            self.change_active_person(None)
            self.goto_active_person()
        self.db.transaction_commit(trans,_("Delete Person (%s)") % n)
        self.redraw_histmenu()
        self.enable_interface()

    def merge_update(self):
        self.redraw_histmenu()
    
    def goto_active_person(self):
        self.people_view.goto_active_person()
            
    def change_active_person(self,person,force=0):
        nph = ""
        if person:
            nph = person.get_handle()
        oph = ""
        if self.active_person:
            oph = self.active_person.get_handle()
        if nph == oph:  # no need to change to the current active person again
            return
        
        if person == None:
            self.set_buttons(0)
            self.active_person = None
            self.modify_statusbar()
            self.emit('active-changed',("",))
        elif (self.active_person == None or
              person.get_handle() != self.active_person.get_handle()):
            self.active_person = self.db.get_person_from_handle(person.get_handle())
            self.modify_statusbar()
            self.set_buttons(1)
            if person and not self.lock_history:
                if self.hindex+1 < len(self.history):
                    self.history = self.history[0:self.hindex+1]

                self.history.append(person.get_handle())
                self.mhistory.append(person.get_handle())
                self.hindex += 1
                self.redraw_histmenu()

                if self.hindex+1 < len(self.history):
                    self.fwdbtn.set_sensitive(1)
                    self.forward.set_sensitive(1)
                else:
                    self.fwdbtn.set_sensitive(0)
                    self.forward.set_sensitive(0)

                if self.hindex > 0:
                    self.backbtn.set_sensitive(1)
                    self.back.set_sensitive(1)
                else:
                    self.backbtn.set_sensitive(0)
                    self.back.set_sensitive(0)
            self.emit('active-changed',(str(person.get_handle()),))
        else:
            self.active_person = self.db.get_person_from_handle(person.get_handle())
            self.set_buttons(1)
            self.emit('active-changed',(str(person.get_handle()),))
        
    def modify_statusbar(self):
        
        if self.active_person == None:
            self.status_text("")
        else:
            if GrampsKeys.get_statusbar() <= 1:
                pname = NameDisplay.displayer.display(self.active_person)
                name = "[%s] %s" % (self.active_person.get_gramps_id(),pname)
            else:
                name = self.display_relationship()
            self.status_text(name)
        return 0

    def display_relationship(self):
        default_person = self.db.get_default_person()
        active = self.active_person
        if default_person == None or active == None:
            return u''
        try:
            pname = NameDisplay.displayer.display(default_person)
            (name,plist) = self.relationship.get_relationship(
                                    default_person,active)

            if name:
                if plist == None:
                    return name
                return _("%(relationship)s of %(person)s") % {
                    'relationship' : name, 'person' : pname }
            else:
                return u""
        except:
            DisplayTrace.DisplayTrace()
            return u""

    def on_open_activate(self,obj):
        prompter = DbPrompter.ExistingDbPrompter(self,self.topWindow)
        prompter.chooser()
        
    def on_import_activate(self,obj):
        prompter = DbPrompter.ImportDbPrompter(self,self.topWindow)
        prompter.chooser()

    def on_saveas_activate(self,obj):
        prompter = DbPrompter.NewSaveasDbPrompter(self,self.topWindow)
        prompter.chooser()

    def on_export_activate(self,obj):
        Exporter.Exporter(self,self.topWindow)

    def on_revert_activate(self,obj):
        pass
        
    def on_person_list1_activate(self,obj):
        """Switches to the person list view"""
        self.views.set_current_page(PERSON_VIEW)

    def on_family_activate(self,obj):
        """Switches to the family view"""
        if GrampsKeys.get_family_view() == 0:
            self.on_family1_activate(obj)
        else:
            self.on_family2_activate(obj)

    def on_family1_activate(self,obj):
        """Switches to the family view"""
        self.views.set_current_page(FAMILY_VIEW1)

    def on_family2_activate(self,obj):
        """Switches to the family view"""
        self.views.set_current_page(FAMILY_VIEW2)

    def on_pedigree1_activate(self,obj):
        """Switches to the pedigree view"""
        self.views.set_current_page(PEDIGREE_VIEW)

    def on_sources_activate(self,obj):
        """Switches to the sources view"""
        self.views.set_current_page(SOURCE_VIEW)

    def on_places_activate(self,obj):
        """Switches to the places view"""
        self.status_text(_('Updating display...'))
        self.views.set_current_page(PLACE_VIEW)
        self.modify_statusbar()

    def on_media_activate(self,obj):
        """Switches to the media view"""
        self.views.set_current_page(MEDIA_VIEW)

    def on_views_switch_page(self,obj,junk,page):
        """Load the appropriate page after a notebook switch"""
        if page == PERSON_VIEW:
            self.enable_buttons(1)
            self.people_view.goto_active_person()
            self.merge_button.set_sensitive(1)
            self.gtop.get_widget('add_bookmark').set_sensitive(not self.db.readonly)
        elif page == FAMILY_VIEW1 or page == FAMILY_VIEW2:
            self.enable_buttons(1)
            self.merge_button.set_sensitive(0)
            self.family_view.load_family()
            self.gtop.get_widget('add_bookmark').set_sensitive(not self.db.readonly)
        elif page == PEDIGREE_VIEW:
            self.enable_buttons(0)
            self.merge_button.set_sensitive(0)
            self.pedigree_view.load_canvas(self.active_person)
            self.gtop.get_widget('add_bookmark').set_sensitive(not self.db.readonly)
        elif page == SOURCE_VIEW:
            self.enable_buttons(1)
            self.merge_button.set_sensitive(1)
            self.gtop.get_widget('add_bookmark').set_sensitive(0)
        elif page == PLACE_VIEW:
            self.enable_buttons(1)
            self.merge_button.set_sensitive(1)
            self.gtop.get_widget('add_bookmark').set_sensitive(0)
        elif page == MEDIA_VIEW:
            self.enable_buttons(1)
            self.merge_button.set_sensitive(0)
            self.gtop.get_widget('add_bookmark').set_sensitive(0)
            
    def on_apply_filter_clicked(self,obj):
        self.people_view.apply_filter_clicked()

    def on_filter_name_changed(self,obj):
        index = self.filter_list.get_active()
        mime_filter = self.filter_model.get_filter(index)
        qual = mime_filter.need_param
        if qual:
            self.filter_text.show()
            self.filter_text.set_sensitive(1)
            self.filter_label.show()
            self.filter_label.set_text(mime_filter.get_rules()[0].labels[0])
        else:
            self.filter_text.hide()
            self.filter_text.set_sensitive(0)
            self.filter_label.hide()

    def new_after_edit(self,epo,val):
        self.change_active_person(epo.person)
        self.family_view.load_family()
        self.goto_active_person()
        
    def update_after_edit(self,epo,change=1):
        self.change_active_person(epo.person)
        self.goto_active_person()
        
    def load_person(self,person):
        if person:
            try:
                EditPerson.EditPerson(self, person, self.db,
                                      self.update_after_edit)
            except:
                DisplayTrace.DisplayTrace()

    def list_item(self,label,filter):
        l = gtk.Label(label)
        l.set_alignment(0,0.5)
        l.show()
        c = gtk.ListItem()
        c.add(l)
        c.set_data('d',filter)
        c.show()
        return c
        
    def parent_name(self,person):
        if person == None:
            return _("Unknown")
        else:
            return NameDisplay.displayer.display(person)

    def status_text(self,text):
        self.statusbar.set_status(text)
        while gtk.events_pending():
            gtk.main_iteration()
        
    def post_load(self,name,callback=None):
        if not self.db.version_supported():
            raise Errors.FileVersionError(
                    "The database version is not supported by this version of GRAMPS.\n"
                    "Please upgrade to the corresponding version or use XML for porting data between different database versions.")
        
        self.db.set_save_path(name)

        res = self.db.get_researcher()
        owner = GrampsCfg.get_researcher()
        if res.get_name() == "" and owner.get_name():
            self.db.set_researcher(owner)

        self.setup_bookmarks()

        self.db.set_undo_callback(self.undo_callback)
        self.db.set_redo_callback(self.redo_callback)

        if self.db.need_upgrade():
            if callback:
                callback(_('Upgrading database...'))
            self.db.upgrade()

        GrampsKeys.save_last_file(name)
        self.gtop.get_widget("filter").set_text("")
    
        self.relationship = self.RelClass(self.db)
        self.emit("database-changed", (self.db,))

        self.change_active_person(self.find_initial_person())
        self.goto_active_person()
        
        if callback:
            callback(_('Setup complete'))
        self.enable_buttons(True)
        return 1

    def find_initial_person(self):
        person = self.db.get_default_person()
        if not person:
            the_ids = self.db.get_person_handles(sort_handles=False)
            if the_ids:
                the_ids.sort()
                person = self.db.get_person_from_handle(the_ids[0])
        return person
    
    def load_database(self,name,callback=None,mode="w"):

        filename = name

        self.status_text(_("Loading %s...") % name)

        if callback:
            callback(_('Opening database...'))
            
        if self.db.load(filename,callback,mode) == 0:
            self.status_text('')
            return 0
        self.status_text('')

        val = self.post_load(name,callback)
        return val

    def setup_bookmarks(self):
        self.bookmarks = Bookmarks.Bookmarks(self.db,self.db.get_bookmarks(),
                                             self.gtop.get_widget("jump_to"),
                                             self.bookmark_callback)

    def displayError(self,msg,msg2):
        ErrorDialog(msg,msg2)
        self.status_text("")

    def complete_rebuild(self):
        self.people_view.apply_filter()
        self.goto_active_person()
        self.modify_statusbar()

    def on_home_clicked(self,obj):
        temp = self.db.get_default_person()
        if temp:
            self.change_active_person(temp)
            self.update_display(0)
            self.goto_active_person()
        else:
            ErrorDialog(_("No Home Person has been set."),
                        _("The Home Person may be set from the Edit menu."))

    def on_add_bookmark_activate(self,obj):
        if self.active_person:
            self.bookmarks.add(self.active_person.get_handle())
            name = NameDisplay.displayer.display(self.active_person)
            self.status_text(_("%s has been bookmarked") % name)
            gobject.timeout_add(5000,self.modify_statusbar)
        else:
            WarningDialog(_("Could Not Set a Bookmark"),
                          _("A bookmark could not be set because "
                            "no one was selected."))

    def on_remove_bookmark(self,handle_list):
        """
        Callback to remove people from bookmark lists *outside*
        the Bookmark Editor.
        """
        self.bookmarks.remove_people(handle_list)

    def on_update_bookmark(self,handle_list):
        """
        Callback to update the labels on the Bookmark menu,
        in case name was changed on the bookmarked people.
        """
        if [handle for handle in handle_list
            if handle in self.bookmarks.bookmarks]:
            self.bookmarks.redraw()

    def on_edit_bookmarks_activate(self,obj):
        self.bookmarks.edit()
        
    def bookmark_callback(self,obj,person_handle):
        old_person = self.active_person
        person = self.db.get_person_from_handle(person_handle)
        try:
            self.change_active_person(person)
            self.update_display(0)
            self.goto_active_person()
        except TypeError:
            WarningDialog(_("Could not go to a Person"),
                          _("Either stale bookmark or broken history "
                            "caused by IDs reorder."))
            self.clear_history()
            self.change_active_person(old_person)
            self.update_display(0)
            self.goto_active_person()
    
    def on_default_person_activate(self,obj):
        if self.active_person:
            name = NameDisplay.displayer.display(self.active_person)
            QuestionDialog(_('Set %s as the Home Person') % name,
                           _('Once a Home Person is defined, pressing the '
                             'Home button on the toolbar will make the home '
                             'person the active person.'),
                           _('_Set Home Person'),
                           self.set_person)
            
    def set_person(self):
        self.db.set_default_person_handle(self.active_person.get_handle())

    def export_callback(self,obj,plugin_function):
        """Call the export plugin, with the active person and database"""
        if self.active_person:
            plugin_function(self.db,self.active_person)
        else:
            ErrorDialog(_('A person must be selected to export'),
                        _('Exporting requires that an active person be selected. '
                          'Please select a person and try again.'))

    def import_callback(self,obj,plugin_function):
        """Call the import plugin"""
        plugin_function(self.db,self.active_person,self.import_tool_callback)
        self.people_view.person_model.rebuild_data()
        self.topWindow.set_title("%s - GRAMPS" % self.db.get_save_path())

    def on_preferences_activate(self,obj):
        GrampsCfg.display_preferences_box(self.db)
    
    def menu_report(self,obj,task,report_class,options_class,
                    translated_name,name,category):
        """Call the report plugin selected from the menus"""
        if self.active_person:
            task(self.db,self.active_person,report_class,
                 options_class,translated_name,name,category)

    def menu_tools(self,obj,task):
        """Call the tool plugin selected from the menus"""
        if self.active_person:
            task(self.db,self.active_person,self.tool_callback,self)
    
    def open_example(self,obj):
        import shutil
        dest = os.path.expanduser("~/.gramps/example")
        if not os.path.isdir(dest):
            try:
                os.mkdir(dest)
            except IOError,msg:
                ErrorDialog(_('Could not create example database'),
                    _('The directory ~/.gramps/example could not '
                    'be created.') + '\n' + str(msg) )
            except OSError,msg:
                ErrorDialog(_('Could not create example database'),
                    _('The directory ~/.gramps/example could not '
                    'be created.') + '\n' + str(msg) )
            except:
                ErrorDialog(_('Could not create example database'),
                    _('The directory ~/.gramps/example could not '
                    'be created.'))
            try:
                example_dir = "%s/share/gramps/example" % const.prefixdir
                for filename in os.listdir(example_dir):
                    shutil.copyfile("%s/%s" % (example_dir,filename), 
                        "%s/%s" % (dest,filename) )
                    try:
                        shutil.copystat("%s/%s" % (example_dir,filename),
                            "%s/%s" % (dest,filename))
                    except:
                        pass
            except IOError,msg:
                ErrorDialog(_('Could not create example database'),str(msg))
            except OSError,msg:
                ErrorDialog(_('Could not create example database'),str(msg))

        filename = "%s/%s" % (dest,const.xmlFile)
        DbPrompter.open_native(self,filename,const.app_gramps_xml)

DARKEN = 1.4

def ms_shift_color_component (component, shift_by):
    if shift_by > 1.0 :
        result = int(component * (2 - shift_by))
    else:
        result = 0xffff - shift_by * (0xffff - component)
    return (result & 65535)

def modify_color(color):
    red = ms_shift_color_component(color.red,DARKEN)
    green = ms_shift_color_component(color.green,DARKEN)
    blue = ms_shift_color_component(color.blue,DARKEN)
    return (red,green,blue)

def set_panel(obj):
    style = obj.get_style().copy()
    color = style.bg[gtk.STATE_NORMAL]
    (r,g,b) = modify_color(color)
    new_color = obj.get_colormap().alloc_color(r,g,b)
    style.bg[gtk.STATE_NORMAL] = new_color
    style.bg[gtk.STATE_PRELIGHT] = new_color
    style.bg[gtk.STATE_ACTIVE] = new_color
    style.bg[gtk.STATE_INSENSITIVE] = new_color
    style.bg[gtk.STATE_SELECTED] = new_color
    obj.set_style(style)

#-------------------------------------------------------------------------
#
# Start it all
#
#-------------------------------------------------------------------------
if __name__ == '__main__':
    Gramps(None)
    gtk.main()
