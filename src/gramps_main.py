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
import PedView
import MediaView
import PlaceView
import FamilyView
import SourceView
import PeopleView

from QuestionDialog import QuestionDialog, ErrorDialog, WarningDialog, SaveDialog, OptionDialog, MissingMediaDialog

import DisplayTrace
import Filter
import const
import Plugins
import Utils
import Bookmarks
import GrampsCfg
import EditPerson
import Find
import VersionControl
import ReadXML

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_HOMEPAGE  = "http://gramps.sourceforge.net"
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
class Gramps:

    def __init__(self,args):

        self.program = gnome.program_init('gramps',const.version)
        self.program.set_property('app-libdir','%s/lib' % const.prefixdir)
        self.program.set_property('app-datadir','%s/share/gramps' % const.prefixdir)
        self.program.set_property('app-sysconfdir','%s/etc' % const.prefixdir)
        self.program.set_property('app-prefix', const.prefixdir)

        self.parents_index = 0
        self.active_person = None
        self.place_loaded = 0
        self.bookmarks = None
        self.c_details = 6
        self.cl = 0

        gtk.rc_parse(const.gtkrcFile)

        if os.getuid() == 0:
            WarningDialog(_("GRAMPS is being run as the 'root' user."),
                         _("This account is not meant for normal appication use. "
                           "Running user applications in the administrative account "
                           "is rarely a wise idea, and can open up potential "
                           "security risks."))

        # This will never contain data - It will be replaced by either
        # a GrampsXML

        self.history = []
        self.mhistory = []
        self.hindex = -1
                
        self.db = RelLib.GrampsDB()
        self.db.set_iprefix(GrampsCfg.iprefix)
        self.db.set_oprefix(GrampsCfg.oprefix)
        self.db.set_fprefix(GrampsCfg.fprefix)
        self.db.set_sprefix(GrampsCfg.sprefix)
        self.db.set_pprefix(GrampsCfg.pprefix)

        GrampsCfg.loadConfig(self.pref_callback)
        self.RelClass = Plugins.relationship_class
        self.relationship = self.RelClass(self.db)
        self.init_interface()

        if args:
            import ArgHandler
            ArgHandler.ArgHandler(self,args)
        elif GrampsCfg.lastfile and GrampsCfg.autoload:
            self.auto_save_load(GrampsCfg.lastfile)
        else:
            import DbPrompter
            DbPrompter.DbPrompter(self,0,self.topWindow)

        self.db.set_researcher(GrampsCfg.get_researcher())

    def pref_callback(self,val):
        self.db.rebuild_person_table()
        self.modify_statusbar()
        self.family_view.init_interface()
        self.update_display(1)
        self.goto_active_person()
        self.toolbar.set_style(GrampsCfg.toolbar)

    def init_interface(self):
        """Initializes the GLADE interface, and gets references to the
        widgets that it will need.
        """

        self.gtop = gtk.glade.XML(const.gladeFile, "gramps", "gramps")
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

        self.filter_list = self.gtop.get_widget("filter_list")
        self.views    = self.gtop.get_widget("views")
        self.merge_button= self.gtop.get_widget("merge")
        self.canvas      = self.gtop.get_widget("canvas1")
        self.toolbar     = self.gtop.get_widget("toolbar1")
        self.toolbardock = self.gtop.get_widget("dockitem2")
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

        self.use_sidebar = GrampsCfg.get_view()
        self.sidebar_btn.set_active(self.use_sidebar)

        self.use_filter = GrampsCfg.get_filter()
        self.filter_btn.set_active(self.use_filter)

        self.use_toolbar = GrampsCfg.get_toolbar_on()
        self.toolbar_btn.set_active(self.use_toolbar)

        self.child_model = gtk.ListStore(
            gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_STRING,
            gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING, 
            gobject.TYPE_STRING,
            )

        self.build_plugin_menus()
        self.init_filters()

        self.toolbar.set_style(GrampsCfg.toolbar)
        self.views.set_show_tabs(0)

        self.family_view = FamilyView.FamilyView(self)
        self.people_view = PeopleView.PeopleView(self)
        
        self.pedigree_view = PedView.PedigreeView(self,
            self.canvas, self.modify_statusbar, self.statusbar,
            self.change_active_person, self.load_person
            )
        
        self.place_view  = PlaceView.PlaceView(self,self.db,self.gtop,self.update_display)
        self.source_view = SourceView.SourceView(self,self.db,self.gtop,self.update_display)
        self.media_view  = MediaView.MediaView(self,self.db,self.gtop,self.update_display)

        self.add_button = self.gtop.get_widget('addbtn')
        self.add_item = self.gtop.get_widget('add_item')
        self.backbtn = self.gtop.get_widget('back_btn')
        self.fwdbtn = self.gtop.get_widget('fwd_btn')
        self.gomenuitem = self.gtop.get_widget("go1")

        self.wins = self.gtop.get_widget("windows1")
        self.wins.set_submenu(gtk.Menu())
        self.winsmenu = self.wins.get_submenu()
        self.child_windows = {}

        self.gtop.signal_autoconnect({
            "on_column_order_activate": self.column_order,
            "on_back_clicked" : self.back_clicked,
            "on_back_pressed" : self.back_pressed,
            "on_fwd_clicked" : self.fwd_clicked,
            "on_fwd_pressed" : self.fwd_pressed,
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
            "on_find_activate" : self.on_find_activate,
            "on_findname_activate" : self.on_findname_activate,
            "on_home_clicked" : self.on_home_clicked,
            "on_new_clicked" : self.on_new_clicked,
            "on_notebook1_switch_page" : self.on_views_switch_page,
            "on_ok_button1_clicked" : self.on_ok_button1_clicked,
            "on_open_activate" : self.on_open_activate,
            "on_pedigree1_activate" : self.on_pedigree1_activate,
            "on_person_list1_activate" : self.on_person_list1_activate,
            "on_main_key_release_event" : self.on_main_key_release_event,
            "on_media_activate" : self.on_media_activate,
            "on_media_list_select_row" : self.media_view.on_select_row,
            "on_media_list_drag_data_get" : self.media_view.on_drag_data_get,
            "on_media_list_drag_data_received" : self.media_view.on_drag_data_received,
            "on_merge_activate" : self.on_merge_activate,
            "on_sidebar1_activate" : self.on_sidebar_activate,
            "on_toolbar2_activate" : self.on_toolbar_activate,
            "on_filter1_activate" : self.on_filter_activate,
            "on_places_activate" : self.on_places_activate,
            "on_preferences1_activate" : self.on_preferences_activate,
            "on_reload_plugins_activate" : Plugins.reload_plugins,
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


        self.enable_filter(self.use_filter)
        self.enable_sidebar(self.use_sidebar)
        self.find_place = None
        self.find_person = None
        self.find_source = None
        self.find_media = None

        if GrampsCfg.defaultview == 0:
            self.views.set_current_page(PERSON_VIEW)
        elif GrampsCfg.familyview == 0:
            self.views.set_current_page(FAMILY_VIEW1)
        else:
            self.views.set_current_page(FAMILY_VIEW2)
      
        self.accel_group = gtk.AccelGroup()
        self.topWindow.add_accel_group(self.accel_group)
        self.back = gtk.ImageMenuItem(gtk.STOCK_GO_BACK)
        self.forward = gtk.ImageMenuItem(gtk.STOCK_GO_FORWARD)

        self.topWindow.show()
        self.enable_toolbar(self.use_toolbar)

    def set_column_order(self,list):
        self.db.set_column_order(list)
        self.people_view.build_columns()

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
            ColumnOrder.ColumnOrder(self.db.get_column_order(),
                                    PeopleView.column_names,
                                    self.set_column_order)
        elif cpage == SOURCE_VIEW:
            print self.db.get_source_column_order()
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
                        person = self.db.get_person(pid)
                        item = gtk.MenuItem("_%d. %s [%s]" % 
                                            (num,person.get_primary_name().get_name(),pid))
                        item.connect("activate",self.bookmark_callback,person.get_id())
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
                person = self.db.find_person_from_id(pid)
                item = gtk.MenuItem("%s. %s [%s]" % 
                    (hotkey,person.get_primary_name().get_name(),pid))
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
                person = self.db.get_person(pid)
                item = gtk.MenuItem("%s. %s [%s]" % 
                    (hotkey,person.get_primary_name().get_name(),pid))
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
        
    def back_clicked(self,obj,step=1):
        if self.hindex > 0:
            try:
                self.hindex -= step
                self.active_person = self.db.get_person(self.history[self.hindex])
                self.modify_statusbar()
                self.update_display(0)
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

    def fwd_clicked(self,obj,step=1):
        if self.hindex+1 < len(self.history):
            try:
                self.hindex += step
                self.active_person = self.db.get_person(self.history[self.hindex])
                self.modify_statusbar()
                self.update_display(0)
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
        self.add_button.set_sensitive(val)
        self.remove_button.set_sensitive(val)
        self.edit_button.set_sensitive(val)
        self.add_item.set_sensitive(val)
        self.remove_item.set_sensitive(val)
        self.edit_item.set_sensitive(val)
            
    def on_show_plugin_status(self,obj):
        Plugins.PluginStatus()

    def on_sidebar_activate(self,obj):
        val = obj.get_active()
        self.enable_sidebar(val)

    def enable_sidebar(self,val):
        if val:
            self.sidebar.show()
            self.views.set_show_tabs(0)
        else:
            self.sidebar.hide()
            self.views.set_show_tabs(1)
        GrampsCfg.save_view(val)

    def enable_filter(self,val):
        if val:
            self.filterbar.show()
        else:
            self.filterbar.hide()
        
    def on_filter_activate(self,obj):
        self.enable_filter(obj.get_active())
        GrampsCfg.save_filter(obj.get_active())

    def on_toolbar_activate(self,obj):
        val = obj.get_active()
        self.enable_toolbar(val)

    def enable_toolbar(self,val):
        if val:
            self.toolbardock.show()
        else:
            self.toolbardock.hide()
        GrampsCfg.save_toolbar_on(val)

    def build_plugin_menus(self):
        export_menu = self.gtop.get_widget("export1")
        import_menu = self.gtop.get_widget("import1")
        self.report_menu = self.gtop.get_widget("reports_menu")
        self.tools_menu  = self.gtop.get_widget("tools_menu")

        self.report_menu.set_sensitive(0)
        self.tools_menu.set_sensitive(0)
        
        Plugins.load_plugins(const.docgenDir)
        Plugins.load_plugins(os.path.expanduser("~/.gramps/docgen"))
        Plugins.load_plugins(const.pluginsDir)
        Plugins.load_plugins(os.path.expanduser("~/.gramps/plugins"))
        Plugins.load_plugins(const.calendarDir)
        Plugins.load_plugins(os.path.expanduser("~/.gramps/calendars"))

        Plugins.build_report_menu(self.report_menu,self.menu_report)
        Plugins.build_tools_menu(self.tools_menu,self.menu_tools)
        Plugins.build_export_menu(export_menu,self.export_callback)
        Plugins.build_import_menu(import_menu,self.import_callback)

        self.RelClass = Plugins.relationship_class
        self.relationship = self.RelClass(self.db)

    def init_filters(self):

        Filter.load_filters(const.filtersDir)
        Filter.load_filters(os.path.expanduser("~/.gramps/filters"))

        menu = Filter.build_filter_menu(self.on_filter_name_changed,self.filter_text)

        self.filter_list.set_menu(menu)
        self.filter_text.set_sensitive(0)
        
    def on_find_activate(self,obj):
        """Display the find box"""
        if self.views.get_current_page() == PLACE_VIEW:
            if self.find_place:
                self.find_place.show()
            else:
                self.find_place = Find.FindPlace(self.find_goto_place,self.db)
        elif self.views.get_current_page() == SOURCE_VIEW:
            if self.find_source:
                self.find_source.show()
            else:
                Find.FindSource(self.find_goto_source,self.db)
        elif self.views.get_current_page() == MEDIA_VIEW:
            if self.find_media:
                self.find_media.show()
            else:
                Find.FindMedia(self.find_goto_media,self.db)
        else:
            if self.find_person:
                self.find_person.show()
            else:
                self.find_person = Find.FindPerson(self.find_goto_person,self.db,
                                                   self.people_view.id2col)

    def on_findname_activate(self,obj):
        """Display the find box"""
        pass

    def find_goto_person(self,id):
        """Find callback to jump to the selected person"""
        self.change_active_person(id)
        self.goto_active_person()
        self.update_display(0)

    def find_goto_place(self,id):
        """Find callback to jump to the selected place"""
        self.place_view.goto(id)

    def find_goto_source(self,id):
        """Find callback to jump to the selected source"""
        self.source_view.goto(id)

    def find_goto_media(self,row):
        """Find callback to jump to the selected media"""
        self.media_view.goto(row)

    def home_page_activate(self,obj):
        gnome.url_show(_HOMEPAGE)

    def mailing_lists_activate(self,obj):
        gnome.url_show(_MAILLIST)

    def report_bug_activate(self,obj):
        gnome.url_show(_BUGREPORT)

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
                import MergeData
                p1 = self.db.get_person(mlist[0])
                p2 = self.db.get_person(mlist[1])
                MergeData.MergePeople(self,self.db,p1,p2,self.merge_update,
                                      self.update_after_edit)
        elif page == PLACE_VIEW:
            self.place_view.merge()

    def delete_event(self,widget, event):
        """Catch the destruction of the top window, prompt to save if needed"""
        self.on_exit_activate(widget)
        return 1

    def on_exit_activate(self,obj):
        """Prompt to save on exit if needed"""
        self.delete_abandoned_photos()
        self.db.close()
        gtk.mainquit()

    def save_query(self):
        """Catch the reponse to the save on exit question"""
        self.on_save_activate_quit()
        self.delete_abandoned_photos()
        self.db.close()
        gtk.mainquit()

    def save_query_noquit(self):
        """Catch the reponse to the save question, no quitting"""
        self.on_save_activate_quit()
        self.delete_abandoned_photos()
        self.db.close()

    def quit(self):
        """Catch the reponse to the save on exit question"""
        self.delete_abandoned_photos()
        self.db.close()
        gtk.mainquit()
        
    def close_noquit(self):
        """Close database and delete abandoned photos, no quit"""
        self.delete_abandoned_photos()
        self.db.close()
        if GrampsCfg.lastfile:
            self.delete_autosave(GrampsCfg.lastfile)

    def delete_abandoned_photos(self):
        """
        We only want to delete local objects, not external objects, however, we
        can delete any thumbnail images. The thumbnails may or may not exist, depending
        on if the image was previewed.
        """
        pass

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
        gnome.help_display('gramps-manual','index')

    def on_faq_activate(self,obj):
        """Display FAQ"""
        gnome.help_display('gramps-manual','faq')

    def on_new_clicked(self,obj):
        """Prompt for permission to close the current database"""
        
        QuestionDialog(_('Create a New Database'),
                       _('Creating a new database will close the existing database, '
                         'discarding any unsaved changes. You will then be prompted '
                         'to create a new database'),
                       _('_Create New Database'),
                       self.new_database_response,self.topWindow)
                       
    def new_database_response(self):
        import DbPrompter
        DbPrompter.DbPrompter(self,1,self.topWindow)

    def clear_database(self):
        """Clear out the database if permission was granted"""

        return
        const.personalEvents = const.init_personal_event_list()
        const.personalAttributes = const.init_personal_attribute_list()
        const.marriageEvents = const.init_marriage_event_list()
        const.familyAttributes = const.init_family_attribute_list()
        const.familyRelations = const.init_family_relation_list()

        self.history = []
        self.mhistory = []
        self.hindex = -1
        self.redraw_histmenu()

        self.relationship.set_db(self.db)

        self.place_view.change_db(self.db)
        self.people_view.change_db(self.db)
        self.source_view.change_db(self.db)
        self.media_view.change_db(self.db)

        if not self.cl:
            self.topWindow.set_title("GRAMPS")
            self.active_person = None

            Utils.clear_timer()
            self.change_active_person(None)
            self.people_view.clear()
            self.family_view.clear()
            self.family_view.load_family()
            self.pedigree_view.clear()
            self.source_view.load_sources()
            self.place_view.load_places()
            self.place_loaded = 0
            self.media_view.load_media()
    
    def tool_callback(self,val):
        if val:
            self.import_tool_callback()

    def import_tool_callback(self):
        if Utils.wasHistory_broken():
            self.clear_history()
	    Utils.clearHistory_broken()
        self.full_update()
        self.goto_active_person()
        if not self.active_person:
            self.change_active_person(self.find_initial_person())
            
    def full_update(self):
        """Brute force display update, updating all the pages"""
        self.update_display(1)
        self.toolbar.set_style(GrampsCfg.toolbar)

    def update_display(self,changed):
        """Incremental display update, update only the displayed page"""
        page = self.views.get_current_page()
        if page == PERSON_VIEW:
            if changed:
                self.people_view.apply_filter()
            else:
                self.goto_active_person()
        elif page == FAMILY_VIEW1 or page == FAMILY_VIEW2:
            self.family_view.load_family()
        elif page == PEDIGREE_VIEW:
            self.pedigree_view.load_canvas(self.active_person)
        elif page == SOURCE_VIEW:
            self.source_view.load_sources()
        elif page == PLACE_VIEW:
            if len(self.db.get_place_id_keys()) > 2000:
                self.status_text(_('Updating display - this may take a few seconds...'))
            else:
                self.status_text(_('Updating display...'))
            self.place_view.load_places()
            self.modify_statusbar()
            self.place_loaded = 1
        else:
            self.media_view.load_media()

    def on_tools_clicked(self,obj):
        if self.active_person:
            Plugins.ToolPlugins(self,self.db,self.active_person,
                                self.tool_callback)

    def on_reports_clicked(self,obj):
        if self.active_person:
            Plugins.ReportPlugins(self,self.db,self.active_person)

    def on_ok_button1_clicked(self,obj):
    
        dbname = obj.get_data("dbname")
        getoldrev = obj.get_data("getoldrev")
        filename = dbname.get_full_path(0)

        if filename == "" or filename == None:
            return
        filename = os.path.normpath(os.path.abspath(filename))
        
        self.clear_database()
    
        if getoldrev.get_active():
            vc = VersionControl.RcsVersionControl(filename)
            VersionControl.RevisionSelect(self.db,filename,vc,
                                          self.load_revision)
        else:
            self.auto_save_load(filename)

    def on_help_dbopen_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','open-db')
        self.dbopen_button = self.dbopen_fs.run()

    def auto_save_load(self,filename):

        filename = os.path.normpath(os.path.abspath(filename))
        if os.path.isdir(filename):
            dirname = filename
        else:
            dirname = os.path.dirname(filename)
        autosave = "%s/autosave.gramps" % dirname

        if os.path.isfile(autosave):
            self.yname = autosave
            self.nname = filename

            OptionDialog(_('An autosave file was detected'),
                         _('GRAMPS has detected an autosave file for the '
                           'selected database. This file is more recent than '
                           'the last saved database. This typically happens '
                           'when GRAMPS was unexpected shutdown before the '
                           'data was saved. You may load this file to try to '
                           'recover any missing data.'),
                         _('_Load autosave file'),
                         self.autosave_query,
                         _('Load _saved database'),
                         self.loadsaved_file)
        else:
            self.active_person = None
            self.place_loaded = 0
            self.read_file(filename)

    def autosave_query(self):
        self.read_file(self.yname)

    def loadsaved_file(self):
        self.read_file(self.nname)

    def read_gedcom(self,filename):
        import ReadGedcom
        
        filename = os.path.normpath(os.path.abspath(filename))
        self.topWindow.set_title("%s - GRAMPS" % filename)
        try:
            ReadGedcom.importData(self.db,filename)
        except:
            DisplayTrace.DisplayTrace()
        self.full_update()

    def read_file(self,filename):
        self.topWindow.set_resizable(gtk.FALSE)
        filename = os.path.normpath(os.path.abspath(filename))
        if self.load_database(filename) == 1:
            if filename[-1] == '/':
                filename = filename[:-1]
            name = os.path.basename(filename)
            self.topWindow.set_title("%s - GRAMPS" % name)
        else:
            GrampsCfg.save_last_file("")
        self.topWindow.set_resizable(gtk.TRUE)
        self.people_view.apply_filter()

    def on_ok_button2_clicked(self,obj):
        filename = obj.get_filename()
        filename = os.path.normpath(os.path.abspath(filename))
        if filename:
            Utils.destroy_passed_object(obj)
            self.save_media(filename)
            self.save_file(filename,_("No Comment Provided"))

    def save_media(self,filename):
        import RelImage
        missmedia_action = 0
        #-------------------------------------------------------------------------
        def remove_clicked():
            # File is lost => remove all references and the object itself
            mobj = self.db.find_object_from_id(ObjectId)
            for p in self.db.get_family_id_map().values():
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference_id() == ObjectId:
                        nl.remove(o) 
                p.set_media_list(nl)
            for key in self.db.get_person_keys():
                p = self.db.get_person(key)
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference_id() == ObjectId:
                        nl.remove(o) 
                p.set_media_list(nl)
            for key in self.db.get_source_keys():
                p = self.db.get_source(key)
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference_id() == ObjectId:
                        nl.remove(o) 
                p.set_media_list(nl)
            for key in self.db.get_place_id_keys():
                p = self.db.get_place_id(key)
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference_id() == ObjectId:
                        nl.remove(o) 
                p.set_media_list(nl)
            self.db.remove_object(ObjectId) 
    
        def leave_clicked():
            # File is lost => do nothing, leave as is
            pass

        def select_clicked():
            # File is lost => select a file to replace the lost one
            def fs_close_window(obj):
                fs_top.destroy()

            def fs_ok_clicked(obj):
                name = fs_top.get_filename()
                if os.path.isfile(name):
                    RelImage.import_media_object(name,filename,base)
                    object = self.db.find_object_from_id(ObjectId)
                    object.set_path(newfile)
                Utils.destroy_passed_object(fs_top)

            fs_top = gtk.FileSelection("%s - GRAMPS" % _("Select file"))
            fs_top.hide_fileop_buttons()
            fs_top.ok_button.connect('clicked',fs_ok_clicked)
            fs_top.cancel_button.connect('clicked',fs_close_window)
            fs_top.show()
            fs_top.run()

        #-------------------------------------------------------------------------
        for ObjectId in self.db.get_object_keys():
            object = self.db.find_object_from_id(ObjectId)
            if 0:
                oldfile = object.get_path()
                (base,ext) = os.path.splitext(os.path.basename(oldfile))
                newfile = os.path.join(filename,os.path.basename(oldfile))
                object.set_path(newfile)
                if os.path.isfile(oldfile):
                    RelImage.import_media_object(oldfile,filename,base)
                else:
                    if self.cl:
                        print "Warning: media file %s was not found," \
                            % os.path.basename(oldfile), "so it was ignored."
                    else:
                        # File is lost => ask what to do
                        if missmedia_action == 0:
                            mmd = MissingMediaDialog(_("Media object could not be found"),
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

    def save_file(self,filename,comment):        

        path = filename
        filename = os.path.normpath(os.path.abspath(filename))
        self.status_text(_("Saving %s ...") % filename)

        Utils.clear_timer()

        if os.path.exists(filename):
            if not os.path.isdir(filename):
                import DbPrompter
                DbPrompter.DbPrompter(self,0,self.topWindow)
                self.displayError(_("Database could not be opened"),
                                  _("%s is not a directory.") % filename + ' ' + \
                                  _("You should select a directory that contains a "
                                "data.gramps file."))
                return
        else:
            try:
                os.mkdir(filename)
            except (OSError,IOError), msg:
                emsg = _("Could not create %s") % filename
                ErrorDialog(emsg,_("An error was detected while attempting to create the file. ",
                                   'The operating system reported "%s"' % str(msg)))
                return
            except:
                ErrorDialog(_("Could not create %s") % filename,
                            _("An error was detected while trying to create the file"))
                return
        
        old_file = filename
        filename = "%s/%s" % (filename,self.db.get_base())
        try:
            self.db.clear_added_media_objects()
        except (OSError,IOError), msg:
            emsg = _("Could not create %s") % filename
            ErrorDialog(emsg,msg)
            return
        
        self.db.set_save_path(old_file)
        GrampsCfg.save_last_file(old_file)

        if GrampsCfg.usevc:
            vc = VersionControl.RcsVersionControl(path)
            vc.checkin(filename,comment,not GrampsCfg.uncompress)

        filename = self.db.get_save_path()
        if filename[-1] == '/':
            filename = filename[:-1]
        name = os.path.basename(filename)
        self.topWindow.set_title("%s - GRAMPS" % name)
        self.status_text("")
        self.statusbar.set_progress_percentage(0.0)
        self.delete_autosave(old_file)

    def delete_autosave(self,filename):
        autosave = "%s/autosave.gramps" % filename
        if os.path.exists(autosave):
            try:
                os.remove(autosave)
            except:
                pass

    def autosave_database(self):
        path = self.db.get_save_path()
        if not path:
            return 1
        
        Utils.clear_timer()

        filename = "%s/autosave.gramps" % (path)
    
        self.status_text(_("autosaving..."));
        try:
            self.db.save(filename,self.quick_progress)
            self.status_text(_("autosave complete"))
            gtk.timeout_add(5000,self.modify_statusbar)
            self.load_progress(0)
        except (IOError,OSError),msg:
            self.status_text("%s - %s" % (_("autosave failed"),msg))
        except:
            DisplayTrace.DisplayTrace()
        return 0

    def load_selected_people(self,obj):
        """Display the selected people in the EditPerson display"""
        mlist = self.people_view.get_selected_objects()
        if mlist and self.active_person.get_id() == mlist[0]:
            self.load_person(self.active_person)

    def load_active_person(self,obj):
        self.load_person(self.active_person)

    def update_person_list(self,person):
        self.people_view.add_to_person_list(person,0)
    
    def load_new_person(self,obj):
        self.active_person = RelLib.Person()
        try:
            EditPerson.EditPerson(self,self.active_person,self.db,
                                  self.new_after_edit)
        except:
            DisplayTrace.DisplayTrace()

    def delete_person_clicked(self,obj):
        cpage = self.views.get_current_page()
        if cpage == PERSON_VIEW:
            mlist = self.people_view.get_selected_objects()
        else:
            mlist = [ self.active_person.get_id() ]

        for sel in mlist:
            p = self.db.get_person(sel)
            self.active_person = p
            name = GrampsCfg.nameof(p) 

            QuestionDialog(_('Delete %s?') % name,
                           _('Deleting the person will remove the person '
                             'from the database. The data can only be '
                             'recovered by closing the database without saving '
                             'changes. This change will become permanent '
                             'after you save the database.'),
                           _('_Delete Person'),
                           self.delete_person_response)

        self.update_display(0)

    def delete_person_response(self):

        if self.db.get_default_person() == self.active_person:
            self.db.set_default_person(None)

        for family_id in self.active_person.get_family_id_list():
            if not family_id:
                continue
            family = self.db.find_family_from_id(family_id)
            if self.active_person.get_id() == family.get_father_id():
                if family.get_mother_id() == None:
                    for child_id in family.get_child_id_list():
                        child = self.db.find_person_from_id(child_id)
                        child.remove_parent_family_id(family.get_id())
                    self.db.delete_family(family.get_id())
                else:
                    family.set_father_id(None)
            else:
                if family.get_father_id() == None:
                    for child_id in family.get_child_id_list():
                        child = self.db.find_person_from_id(child_id)
                        child.remove_parent_family_id(family)
                    self.db.delete_family(family)
                else:
                    family.set_mother_id(None)

        for (family_id,mrel,frel) in self.active_person.get_parent_family_id_list():
            if family_id:
                family = self.db.find_family_from_id(family_id)
                family.remove_child_id(self.active_person.get_id())
            
        self.people_view.remove_from_history(self.active_person)
        self.db.remove_person_id(self.active_person.get_id())
        self.people_view.remove_from_person_list(self.active_person)
        #self.people_view.person_model.sort_column_changed()

        if self.hindex >= 0:
            self.active_person = self.db.get_person(self.history[self.hindex])
        else:
            self.change_active_person(None)
        self.redraw_histmenu()

    def merge_update(self,p1,p2,old_id):
        self.people_view.remove_from_person_list(p1,old_id)
        self.people_view.remove_from_person_list(p2)
        self.people_view.remove_from_history(p1,old_id)
        self.people_view.remove_from_history(p2)
        self.redraw_histmenu()
        self.people_view.redisplay_person_list(p1)
        self.update_display(0)
    
    def goto_active_person(self,first=0):
        self.people_view.goto_active_person(first)
            
    def change_active_person(self,person):
        if person != self.active_person:
            self.active_person = person
            self.modify_statusbar()
            if person:
                if self.hindex+1 < len(self.history):
                    self.history = self.history[0:self.hindex+1]

                self.history.append(person.get_id())
                self.mhistory.append(person.get_id())
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

        if person:
            self.set_buttons(1)
        else:
            self.set_buttons(0)
        
    def modify_statusbar(self):
        
        if self.active_person == None:
            self.status_text("")
        else:
            if GrampsCfg.status_bar <= 1:
                pname = GrampsCfg.nameof(self.active_person)
                name = "[%s] %s" % (self.active_person.get_id(),pname)
            else:
                name = self.display_relationship()
            self.status_text(name)
        return 0

    def display_relationship(self):
        default_person = self.db.get_default_person()
        if not default_person:
            return u''
        try:
            pname = GrampsCfg.nameof(default_person)
            (name,plist) = self.relationship.get_relationship(
                                    default_person,
                                    self.active_person)
            if name:
                if plist == None:
                    return name
                else:
                    return _("%(relationship)s of %(person)s") % {
                        'relationship' : name, 'person' : pname }
            else:
                return ""
        except:
            DisplayTrace.DisplayTrace()
            return ""
	
    def on_open_activate(self,obj):
        wFs = gtk.glade.XML(const.revisionFile, "dbopen","gramps")
        
        self.dbopen_fs = wFs.get_widget("dbopen")
        
        Utils.set_titles(self.dbopen_fs, wFs.get_widget('title'),
                         _('Open a database'))
        
        dbname = wFs.get_widget("dbname")
        getoldrev = wFs.get_widget("getoldrev")
        self.dbopen_fs.set_data("dbname",dbname)
        dbname.set_default_path(GrampsCfg.db_dir)
        dbname.set_filename(GrampsCfg.db_dir)
        dbname.gtk_entry().set_position(len(GrampsCfg.db_dir))
        
        self.dbopen_fs.set_data("getoldrev",getoldrev)
        getoldrev.set_sensitive(GrampsCfg.usevc)
        self.dbopen_fs.set_transient_for(self.topWindow)
        self.dbopen_fs.show()
        self.dbopen_button = self.dbopen_fs.run()
        if self.dbopen_button == gtk.RESPONSE_OK:
            self.on_ok_button1_clicked(self.dbopen_fs)
        elif self.dbopen_button == gtk.RESPONSE_HELP:
            self.on_help_dbopen_clicked(obj)
        self.dbopen_fs.destroy()

    def on_revert_activate(self,obj):
        pass
        
    def on_save_as_activate(self,obj):
        wFs = gtk.glade.XML (const.gladeFile, "fileselection","gramps")
        fileSelector = wFs.get_widget("fileselection")
        fileSelector.set_title('%s - GRAMPS' % _('Save database'))
        fileSelector.set_transient_for(self.topWindow)
        fileSelector.show()
        button = fileSelector.run()
        if button == gtk.RESPONSE_OK:
            self.on_ok_button2_clicked(fileSelector)
        fileSelector.destroy()

    def display_comment_box(self,filename):
        """Displays a dialog box, prompting for a revison control comment"""
        filename = os.path.normpath(os.path.abspath(filename))
        VersionControl.RevisionComment(filename,self.save_file)
    
    def on_person_list1_activate(self,obj):
        """Switches to the person list view"""
        self.views.set_current_page(PERSON_VIEW)

    def on_family_activate(self,obj):
        """Switches to the family view"""
        if GrampsCfg.familyview == 0:
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
        if len(self.db.get_place_id_keys()) > 2000:
            self.status_text(_('Updating display - this may take a few seconds...'))
        else:
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
        elif page == FAMILY_VIEW1 or page == FAMILY_VIEW2:
            self.enable_buttons(1)
            self.merge_button.set_sensitive(0)
            self.family_view.load_family()
        elif page == PEDIGREE_VIEW:
            self.enable_buttons(0)
            self.merge_button.set_sensitive(0)
            self.pedigree_view.load_canvas(self.active_person)
        elif page == SOURCE_VIEW:
            self.enable_buttons(1)
            self.merge_button.set_sensitive(0)
            self.source_view.load_sources()
        elif page == PLACE_VIEW:
            self.enable_buttons(1)
            self.place_view.load_places()
            self.merge_button.set_sensitive(1)
        elif page == MEDIA_VIEW:
            self.enable_buttons(1)
            self.merge_button.set_sensitive(0)
            self.media_view.load_media()
            
    def on_apply_filter_clicked(self,obj):
        self.people_view.apply_filter_clicked()

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

    def new_after_edit(self,epo):
        if epo:
            if epo.person.get_id() == "":
                self.db.add_person(epo.person)
            else:
                self.db.add_person_no_map(epo.person,epo.person.get_id())
            self.db.build_person_display(epo.person.get_id())
            self.change_active_person(epo.person)
            self.people_view.redisplay_person_list(epo.person)
        if self.views.get_current_page() in [FAMILY_VIEW1,FAMILY_VIEW2]:
            self.family_view.load_family()

    def update_after_newchild(self,family,person,plist):
        self.family_view.load_family(family)
        self.people_view.redisplay_person_list(person)
        for p in plist:
            self.place_view.new_place_after_edit(p)

    def update_after_edit(self,epo,change=1):
        if epo:
            if change:
                print "change"
                self.people_view.redisplay_person_list(epo.person)
            else:
                print "no change"
                iter = self.people_view.person_model.get_iter((0,))
                id = epo.person.get_id()
                path = self.people_view.person_model.find_path(id)
                self.people_view.person_model.row_changed(path,iter)
        self.update_display(0)

    def update_after_merge(self,person,old_id):
        if person:
            self.people_view.redisplay_person_list(person)
        self.update_display(0)

    def load_person(self,person):
        if person:
            try:
                EditPerson.EditPerson(self, person, self.db, self.update_after_edit)
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
            return GrampsCfg.nameof(person)
		
    def load_progress(self,value):
        self.statusbar.set_progress_percentage(value)
        while gtk.events_pending():
            gtk.mainiteration()

    def status_text(self,text):
        self.statusbar.set_status(text)
        while gtk.events_pending():
            gtk.mainiteration()
        
    def quick_progress(self,value):
        gtk.threads_enter()
        self.statusbar.set_progress_percentage(value)
        while gtk.events_pending():
            gtk.mainiteration()
        gtk.threads_leave()

    def post_load(self,name):
        self.db.set_save_path(name)
        res = self.db.get_researcher()
        owner = GrampsCfg.get_researcher()
    
        if res.get_name() == "" and owner.get_name():
            self.db.set_researcher(owner)

        self.setup_bookmarks()

        try:
            mylist = self.db.get_person_event_types()
            for type in mylist:
                ntype = const.display_pevent(type)
                if ntype not in const.personalEvents:
                    const.personalEvents.append(ntype)
                    
            mylist = self.db.get_family_event_types()
            for type in mylist:
                ntype = const.display_fevent(type)
                if ntype not in const.marriageEvents:
                    const.marriageEvents.append(ntype)

            mylist = self.db.get_person_attribute_types()
            for type in mylist:
                ntype = const.display_pattr(type)
                if ntype not in const.personalAttributes:
                    const.personalAttributes.append(ntype)

            mylist = self.db.get_family_attribute_types()
            for type in mylist:
                ntype = const.display_fattr(type)
                if ntype not in const.familyAttributes:
                    const.familyAttributes.append(ntype)

            mylist = self.db.get_family_relation_types()
            for type in mylist:
                ntype = const.display_frel(type)
                if ntype not in const.familyRelations:
                    const.familyRelations.append(ntype)
        except:
            pass

        GrampsCfg.save_last_file(name)
        self.gtop.get_widget("filter").set_text("")
    
        self.statusbar.set_progress_percentage(1.0)

        self.people_view.change_db(self.db)
        self.place_view.change_db(self.db)
        self.source_view.change_db(self.db)
        self.media_view.change_db(self.db)
        #self.full_update()

        self.change_active_person(self.find_initial_person())
        self.goto_active_person()
        self.statusbar.set_progress_percentage(0.0)
        return 1

    def find_initial_person(self):
        person = self.db.get_default_person()
        if not person:
            the_ids = self.db.get_person_keys()
            if the_ids:
                the_ids.sort()
                person = self.db.get_person(the_ids[0])
        return person
    
    def load_database(self,name):

        filename = name
        #self.clear_database()

        self.status_text(_("Loading %s...") % name)
        if self.db.load(filename,self.load_progress) == 0:
            self.status_text('')
            return 0
        self.status_text('')
        self.db.clear_added_media_objects()
        return self.post_load(name)

    def load_revision(self,f,name,revision):
        filename = "%s/%s" % (name,self.db.get_base())
        self.status_text(_('Loading %s...' % name))
        if ReadXML.loadRevision(self.db,f,filename,revision,self.load_progress) == 0:
            return 0
        self.db.clear_added_media_objects()
        return self.post_load(name)

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
        else:
            ErrorDialog(_("No Home Person has been set."),
                        _("The Home Person may be set from the Settings menu."))

    def on_add_bookmark_activate(self,obj):
        if self.active_person:
            self.bookmarks.add(self.active_person)
            name = GrampsCfg.nameof(self.active_person)
            self.status_text(_("%s has been bookmarked") % name)
            gtk.timeout_add(5000,self.modify_statusbar)
        else:
            WarningDialog(_("Could Not Set a Bookmark"),
                          _("A bookmark could not be set because no one was selected."))

    def on_edit_bookmarks_activate(self,obj):
        self.bookmarks.edit()
        
    def bookmark_callback(self,obj,person_id):
        old_person = self.active_person
        person = self.db.find_person_from_id(person_id)
        try:
            self.change_active_person(person)
            self.update_display(0)
        except TypeError:
            WarningDialog(_("Could not go to a Person"),
                          _("Either stale bookmark or broken history caused by IDs reorder."))
            self.clear_history()
            self.change_active_person(old_person)
            self.update_display(0)
    
    def on_default_person_activate(self,obj):
        if self.active_person:
            name = self.active_person.get_primary_name().get_regular_name()
            QuestionDialog(_('Set %s as the Home Person') % name,
                           _('Once a Home Person is defined, pressing the '
                             'Home button on the toolbar will make the home '
                             'person the active person.'),
                           _('_Set Home Person'),
                           self.set_person)
            
    def set_person(self):
        self.db.set_default_person(self.active_person)

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
        self.topWindow.set_title("%s - GRAMPS" % self.db.get_save_path())

    def on_preferences_activate(self,obj):
        GrampsCfg.display_preferences_box(self.db)
    
    def menu_report(self,obj,task):
        """Call the report plugin selected from the menus"""
        if self.active_person:
            task(self.db,self.active_person)

    def menu_tools(self,obj,task):
        """Call the tool plugin selected from the menus"""
        if self.active_person:
            task(self.db,self.active_person,self.tool_callback)
    
    def on_main_key_release_event(self,obj,event):
        """Respond to the insert and delete buttons in the person list"""
        pass
        #if event.keyval == GDK.Delete:
        #    self.on_delete_person_clicked(obj)
        #elif event.keyval == GDK.Insert:
        #    self.load_new_person(obj)

    def open_example(self,obj):
        if Utils.wasModified():
            self.delobj = obj
            SaveDialog(_('Save Changes Made to the Database?'),
                       _("Unsaved changes exist in the current database. If you "
                         "close without saving, the changes you have made will "
                         "be lost."),
                       self.close_noquit,
                       self.save_query_noquit)

        if not Utils.wasModified():
            import shutil
            dest = os.path.expanduser("~/.gramps/example")
            if not os.path.isdir(dest):
                try:
                    os.mkdir(dest)
                except IOError,msg:
                    ErrorDialog(_('Could not create database'),
                        _('The directory ~/.gramps/example could not '
                        'be created.') + '\n' + str(msg) )
                except OSError,msg:
                    ErrorDialog(_('Could not create database'),
                        _('The directory ~/.gramps/example could not '
                        'be created.') + '\n' + str(msg) )
                except:
                    ErrorDialog(_('Could not create database'),
                        _('The directory ~/.gramps/example could not '
                        'be created.'))
                try:
                    dir = "%s/share/gramps/example" % const.prefixdir
                    for file in os.listdir(dir):
                        shutil.copyfile("%s/%s" % (dir,file), 
                            "%s/%s" % (dest,file) )
                        try:
                            shutil.copystat("%s/%s" % (dir,file),
                                "%s/%s" % (dest,file))
                        except:
                            pass
                except IOError,msg:
                    ErrorDialog(_('Example database not created'),str(msg))
                except OSError,msg:
                    ErrorDialog(_('Example database not created'),str(msg))

            self.read_file(dest)

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
    gtk.mainloop()
