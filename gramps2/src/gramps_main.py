#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allinghamg
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
import getopt

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from intl import gettext as _

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
import ListModel
import GrampsXML

try:
    import GrampsZODB
    zodb_ok = 1
except:
    zodb_ok = 0

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_HOMEPAGE  = "http://gramps.sourceforge.net"
_MAILLIST  = "http://sourceforge.net/mail/?group_id=25770"
_BUGREPORT = "http://sourceforge.net/tracker/?group_id=25770&atid=385137"

_sel_mode = gtk.SELECTION_MULTIPLE

#-------------------------------------------------------------------------
#
# Main GRAMPS class
#
#-------------------------------------------------------------------------
class Gramps:

    def __init__(self,args):

        self.pl_titles  = [ (_('Name'),5,250), (_('ID'),1,50),(_('Gender'),2,70),
                            (_('Birth date'),6,150),(_('Death date'),7,150), ('',5,0),
                            ('',6,0), ('',7,0) ]

        self.program = gnome.program_init('gramps',const.version)
        self.program.set_property('app-libdir','%s/lib' % const.prefixdir)
        self.program.set_property('app-datadir','%s/share/gramps' % const.prefixdir)
        self.program.set_property('app-sysconfdir','%s/etc' % const.prefixdir)
        self.program.set_property('app-prefix', const.prefixdir)

        self.DataFilter = Filter.Filter("")
        self.parents_index = 0
        self.active_person = None
        self.place_loaded = 0
        self.bookmarks = None
        self.c_details = 6
        self.id2col = {}

        gtk.rc_parse(const.gtkrcFile)

        if os.getuid() == 0:
            WarningDialog(_("GRAMPS is being run as the 'root' user."),
                         _("This account is not meant for normal appication use. "
                           "Running user applications in the administrative account "
                           "is rarely a wise idea, and can open up potential "
                           "security risks."))

        # This will never contain data - It will be replaced by either
        # a GrampsXML or GrampsZODB
        
        self.db = RelLib.GrampsDB()
        self.db.set_iprefix(GrampsCfg.iprefix)
        self.db.set_oprefix(GrampsCfg.oprefix)
        self.db.set_fprefix(GrampsCfg.fprefix)
        self.db.set_sprefix(GrampsCfg.sprefix)
        self.db.set_pprefix(GrampsCfg.pprefix)

        GrampsCfg.loadConfig(self.full_update)
        self.relationship = Plugins.relationship_function()
        self.init_interface()

        self.cl = 1
        if args:
            options,leftargs = getopt.getopt(args,
                const.shortopts,const.longopts)
            if leftargs:
                print "Unrecognized option: %s" % leftargs[0]
                os._exit(1)
            outfname = ''
            action = ''
	    imports = []
            for opt_ix in range(len(options)):
                o = options[opt_ix][0][1]
                if o == '-':
                    continue
                elif o == 'i':
                    fname = options[opt_ix][1]
                    if opt_ix<len(options)-1 and options[opt_ix+1][0][1]=='f': 
                        format = options[opt_ix+1][1]
                        if format not in [ 'gedcom', 'gramps', 'gramps-pkg' ]:
                            print "Invalid format:  %s" % format
                            os._exit(1)
                    elif string.upper(fname[-3:]) == "GED":
                        format = 'gedcom'
                    elif string.upper(fname[-3:]) == "TGZ":
                        format = 'gramps-pkg'
                    elif os.path.isdir(fname):
                        format = 'gramps'
                    else:
                        print "Unrecognized format for input file %s" % fname
                        os._exit(1)
		    imports.append((fname,format))
                elif o == 'o':
                    outfname = options[opt_ix][1]
                    if opt_ix<len(options)-1 and options[opt_ix+1][0][1]=='f': 
                        outformat = options[opt_ix+1][1]
                        if outformat not in [ 'gedcom', 'gramps', 'gramps-pkg', 'iso' ]:
                            print "Invalid format:  %s" % outformat
                            os._exit(1)
                    elif string.upper(outfname[-3:]) == "GED":
                        outformat = 'gedcom'
                    elif string.upper(outfname[-3:]) == "TGZ":
                        outformat = 'gramps-pkg'
                    elif os.path.isdir(outfname):
                        outformat = 'gramps'
                    else:
                        print "Unrecognized format for output file %s" % outfname
                        os._exit(1)
                elif o == 'a':
                    action = options[opt_ix][1]
                    if action not in [ 'check', 'summary' ]:
                        print "Unknown action: %s." % action
                        os._exit(1)
            
            if not (outfname or action):
                self.cl = 0

            if imports:
                # Create dir for imported database(s)
                self.impdir_path = os.path.expanduser("~/.gramps/import" )
                if not os.path.isdir(self.impdir_path):
                    try:
                        os.mkdir(self.impdir_path,0700)
                    except:
                        print "Could not create import directory %s" % impdir_path 
                        return
                elif not os.access(self.impdir_path,os.W_OK):
                    print "Import directory %s is not writable" % self.impdir_path 
                    return
                # and clean it up before use
                files = os.listdir(self.impdir_path) ;
                for fn in files:
                    if os.path.isfile(fn):
                        os.remove( os.path.join(self.impdir_path,fn) )

                self.clear_database(0)
                self.db.setSavePath(self.impdir_path)
                for imp in imports:
                    print "Importing: file %s, format %s." % (imp[0],imp[1])
                    self.cl_import(imp[0],imp[1])

            if outfname:
                print "Exporting: file %s, format %s." % (outfname,outformat)
                self.cl_export(outfname,outformat)

            if action:
                print "Performing action: %s." % action
                self.cl_action(action)
            
            if self.cl:
                print "Exiting."
                os._exit(0)

        elif GrampsCfg.lastfile and GrampsCfg.autoload:
            self.auto_save_load(GrampsCfg.lastfile)
        else:
            import DbPrompter
            DbPrompter.DbPrompter(self,0)

        if self.db.need_autosave() and GrampsCfg.autosave_int != 0:
            Utils.enable_autosave(self.autosave_database,
                                  GrampsCfg.autosave_int)

        self.db.setResearcher(GrampsCfg.get_researcher())

    def init_interface(self):
        """Initializes the GLADE interface, and gets references to the
        widgets that it will need.
        """
        self.gtop = gtk.glade.XML(const.gladeFile, "gramps")
        self.topWindow   = self.gtop.get_widget("gramps")

        self.report_button = self.gtop.get_widget("reports")
        self.tool_button  = self.gtop.get_widget("tools")
        self.remove_button  = self.gtop.get_widget("removebtn")
        self.edit_button  = self.gtop.get_widget("editbtn")
        self.sidebar = self.gtop.get_widget('side_event')
        self.filterbar = self.gtop.get_widget('filterbar')

        self.tool_button.set_sensitive(0)
        self.report_button.set_sensitive(0)
        self.remove_button.set_sensitive(0)
        self.edit_button.set_sensitive(0)

        set_panel(self.sidebar)
        set_panel(self.gtop.get_widget('side_people'))
        set_panel(self.gtop.get_widget('side_family'))
        set_panel(self.gtop.get_widget('side_pedigree'))
        set_panel(self.gtop.get_widget('side_sources'))
        set_panel(self.gtop.get_widget('side_places'))
        set_panel(self.gtop.get_widget('side_media'))

        self.sidebar_btn = self.gtop.get_widget("sidebar1")
        self.filter_btn  = self.gtop.get_widget("filter1")
        self.statusbar   = self.gtop.get_widget("statusbar")

        self.ptabs       = self.gtop.get_widget("ptabs")
        self.pl_other    = self.gtop.get_widget("pl_other")

        self.ptabs.set_show_tabs(0)

        self.pl_page = [
            ListModel.ListModel(self.pl_other, self.pl_titles, self.row_changed,
                                self.alpha_event, _sel_mode),
            ]

        self.person_tree = self.pl_page[0]
        self.person_list = self.pl_page[0].tree
        self.person_model = self.pl_page[0].model
        
        self.default_list = self.pl_page[-1]

        self.alpha_page = {}
        self.model2page = {}
        self.model_used = {}
        self.tab_list = []
        
        self.filter_list = self.gtop.get_widget("filter_list")
        self.views    = self.gtop.get_widget("views")
        self.merge_button= self.gtop.get_widget("merge")
        self.canvas      = self.gtop.get_widget("canvas1")
        self.toolbar     = self.gtop.get_widget("toolbar1")
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

        self.pedigree_view = PedView.PedigreeView(
            self.canvas, self.modify_statusbar, self.statusbar,
            self.change_active_person, self.load_person
            )
        
        self.place_view  = PlaceView.PlaceView(self.db,self.gtop,self.update_display)
        self.source_view = SourceView.SourceView(self.db,self.gtop,self.update_display)
        self.media_view  = MediaView.MediaView(self.db,self.gtop,self.update_display)

        self.addbtn = self.gtop.get_widget('addbtn')
        self.removebtn = self.gtop.get_widget('removebtn')
        self.editbtn = self.gtop.get_widget('editbtn')

        self.gtop.signal_autoconnect({
            "on_editbtn_clicked" : self.edit_button_clicked,
            "on_addbtn_clicked" : self.add_button_clicked,
            "on_removebtn_clicked" : self.remove_button_clicked,
            "on_alpha_switch_page" : self.change_alpha_page,
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
            "on_default_person_activate" : self.on_default_person_activate,
            "on_delete_person_clicked" : self.delete_person_clicked,
            "on_delete_place_clicked" : self.place_view.on_delete_clicked,
            "on_delete_source_clicked" : self.source_view.on_delete_clicked,
            "on_delete_media_clicked" : self.media_view.on_delete_clicked,
            "on_edit_active_person" : self.load_active_person,
            "on_edit_selected_people" : self.load_selected_people,
            "on_edit_bookmarks_activate" : self.on_edit_bookmarks_activate,
            "on_exit_activate" : self.on_exit_activate,
            "on_family1_activate" : self.on_family1_activate,
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
            "on_filter1_activate" : self.on_filter_activate,
            "on_places_activate" : self.on_places_activate,
            "on_preferences1_activate" : self.on_preferences_activate,
            "on_reload_plugins_activate" : Plugins.reload_plugins,
            "on_reports_clicked" : self.on_reports_clicked,
            "on_revert_activate" : self.on_revert_activate,
            "on_save_activate" : self.on_save_activate,
            "on_save_as_activate" : self.on_save_as_activate,
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
        self.topWindow.show()
        
    def change_alpha_page(self,obj,junk,page):
        self.person_tree = self.pl_page[page]
        self.person_list = self.pl_page[page].tree
        self.person_model = self.pl_page[page].model
        if not self.model_used.has_key(self.person_tree) or self.model_used[self.person_tree] == 0:
            self.model_used[self.person_tree] = 1
            self.apply_filter(self.person_tree)
        
    def edit_button_clicked(self,obj):
        cpage = self.views.get_current_page()
        if cpage == 0:
            self.load_selected_people(obj)
        elif cpage == 3:
            self.source_view.on_edit_clicked(obj)
        elif cpage == 4:
            self.place_view.on_edit_clicked(obj)
        elif cpage == 5:
            self.media_view.on_edit_clicked(obj)

    def add_button_clicked(self,obj):
        cpage = self.views.get_current_page()
        if cpage == 0:
            self.load_new_person(obj)
        elif cpage == 3:
            self.source_view.on_add_clicked(obj)
        elif cpage == 4:
            self.place_view.on_add_place_clicked(obj)
        elif cpage == 5:
            self.media_view.on_add_clicked(obj)

    def remove_button_clicked(self,obj):
        cpage = self.views.get_current_page()
        if cpage == 0:
            self.delete_person_clicked(obj)
        elif cpage == 3:
            self.source_view.on_delete_clicked(obj)
        elif cpage == 4:
            self.place_view.on_delete_clicked(obj)
        elif cpage == 5:
            self.media_view.on_delete_clicked(obj)

    def enable_buttons(self,val):
        self.addbtn.set_sensitive(val)
        self.removebtn.set_sensitive(val)
        self.editbtn.set_sensitive(val)
            
    def row_changed(self,obj):
        mlist = self.person_tree.get_selected_objects()
        if mlist:
            try:
                self.change_active_person(self.db.getPerson(mlist[0]))
            except:
                self.change_active_person(None)
                self.person_tree.unselect()

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

        self.relationship = Plugins.relationship_function()

    def init_filters(self):

        Filter.load_filters(const.filtersDir)
        Filter.load_filters(os.path.expanduser("~/.gramps/filters"))

        menu = Filter.build_filter_menu(self.on_filter_name_changed,self.filter_text)

        self.filter_list.set_menu(menu)
        self.filter_text.set_sensitive(0)
        
    def on_find_activate(self,obj):
        """Display the find box"""
        if self.views.get_current_page() == 4:
            if self.find_place:
                self.find_place.show()
            else:
                self.find_place = Find.FindPlace(self.find_goto_place,self.db)
        elif self.views.get_current_page() == 3:
            if self.find_source:
                self.find_source.show()
            else:
                Find.FindSource(self.find_goto_source,self.db)
        elif self.views.get_current_page() == 5:
            if self.find_media:
                self.find_media.show()
            else:
                Find.FindMedia(self.find_goto_media,self.db)
        else:
            if self.find_person:
                self.find_person.show()
            else:
                self.find_person = Find.FindPerson(self.find_goto_person,self.db)

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
        if page == 0:

            mlist = self.person_tree.get_selected_objects()

            if len(mlist) != 2:
                msg = _("Cannot merge people.")
                msg2 = _("Exactly two people must be selected to perform a merge. "
                         "A second person can be selected by holding down the "
                         "control key while clicking on a the desired person.")
                ErrorDialog(msg,msg2)
            else:
                import MergeData
                p1 = self.db.getPerson(mlist[0])
                p2 = self.db.getPerson(mlist[1])
                MergeData.MergePeople(self.db,p1,p2,self.merge_update,
                                      self.update_after_edit)
        elif page == 4:
            self.place_view.merge()

    def delete_event(self,widget, event):
        """Catch the destruction of the top window, prompt to save if needed"""
        self.on_exit_activate(widget)
        return 1

    def on_exit_activate(self,obj):
        """Prompt to save on exit if needed"""
        if Utils.wasModified():
            self.delobj = obj
            SaveDialog(_('Save Changes Made to the Database?'),
                       _("Unsaved changes exist in the current database. If you "
                         "close without saving, the changes you have made will "
                         "be lost."),
                       self.quit,
                       self.save_query)
        else:
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
	Utils.clearModified()

    def quit(self):
        """Catch the reponse to the save on exit question"""
        self.delete_abandoned_photos()
        self.db.close()
        gtk.mainquit()
        
    def close_noquit(self):
        """Close database and delete abandoned photos, no quit"""
        self.delete_abandoned_photos()
        self.db.close()
	Utils.clearModified()

    def delete_abandoned_photos(self):
        """
        We only want to delete local objects, not external objects, however, we
        can delete any thumbnail images. The thumbnails may or may not exist, depending
        on if the image was previewed.
        """
        for obj in self.db.get_added_media_objects():
            if obj.getLocal():
                try:
                    os.unlink(obj.getPath())
                except IOError:
                    pass
                except:
                    DisplayTrace.DisplayTrace()
            thumb = "%s/.thumb/%s.jpg" % (self.db.getSavePath(),obj.getId())
            if os.path.isfile(thumb):
                try:
                    os.unlink(thumb)
                except IOError:
                    pass
                except:
                    DisplayTrace.DisplayTrace()

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

    def on_new_clicked(self,obj):
        """Prompt for permission to close the current database"""
        
        QuestionDialog(_('Create a New Database'),
                       _('Creating a new database will close the existing database, '
                         'discarding any unsaved changes. You will then be prompted '
                         'to create a new database'),
                       _('_Create New Database'),
                       self.new_database_response)
                       
    def new_database_response(self):
        import DbPrompter
        self.clear_database(2)
        DbPrompter.DbPrompter(self,1)

    def clear_person_tabs(self):

        for i in range(0,len(self.tab_list)):
            self.ptabs.remove_page(0)
        self.ptabs.set_show_tabs(0)
        self.id2col = {}
        self.tab_list = []
        self.alpha_page = {}
        self.model2page = {}
        self.model_used = {}

        self.default_list.clear()
        self.pl_page = [
            self.default_list
            ]

        self.person_tree = self.pl_page[-1]
        self.person_list = self.pl_page[-1].tree
        self.person_model = self.pl_page[-1].model
    
    def clear_database(self,zodb=1):
        """Clear out the database if permission was granted"""
        const.personalEvents = const.init_personal_event_list()
        const.personalAttributes = const.init_personal_attribute_list()
        const.marriageEvents = const.init_marriage_event_list()
        const.familyAttributes = const.init_family_attribute_list()
        const.familyRelations = const.init_family_relation_list()

        self.clear_person_tabs()
        
        if zodb == 1:
            self.db = GrampsZODB.GrampsZODB()
        elif zodb == 2:
            self.db = RelLib.GrampsDB()
        else:
            self.db = GrampsXML.GrampsXML()
        self.db.set_iprefix(GrampsCfg.iprefix)
        self.db.set_oprefix(GrampsCfg.oprefix)
        self.db.set_fprefix(GrampsCfg.fprefix)
        self.db.set_sprefix(GrampsCfg.sprefix)
        self.db.set_pprefix(GrampsCfg.pprefix)

        self.place_view.change_db(self.db)
        self.source_view.change_db(self.db)
        self.media_view.change_db(self.db)

        if not self.cl:
            self.topWindow.set_title("GRAMPS")
            self.active_person = None
            self.id2col = {}

            Utils.clearModified()
            Utils.clear_timer()
            self.change_active_person(None)
            for model in self.pl_page:
                model.clear()
            self.family_view.clear()
            self.family_view.load_family()
            self.pedigree_view.clear()
            self.source_view.load_sources()
            self.place_view.load_places()
            self.place_loaded = 0
            self.media_view.load_media()
    
    def tool_callback(self,val):
        if val:
            Utils.modified()
            self.clear_person_tabs()
            self.full_update()
            
    def full_update(self):
        """Brute force display update, updating all the pages"""

        self.complete_rebuild()
        page = self.views.get_current_page()
        
        if page == 1:
            self.family_view.load_family()
        elif page == 2:
            self.pedigree_view.load_canvas(self.active_person)
        elif page == 3:
            self.source_view.load_sources()
        elif page == 4:
            if len(self.db.getPlaceKeys()) > 2000:
                self.status_text(_('Updating display - this may take a few seconds...'))
            else:
                self.status_text(_('Updating display...'))
            self.place_view.load_places()
            self.modify_statusbar()
            self.place_loaded = 1
        elif page == 5:
            self.media_view.load_media()
        self.toolbar.set_style(GrampsCfg.toolbar)

    def update_display(self,changed):
        """Incremental display update, update only the displayed page"""
        page = self.views.get_current_page()
        
        if page == 0:
            if changed:
                self.apply_filter()
            else:
                self.goto_active_person()
        elif page == 1:
            self.family_view.load_family()
        elif page == 2:
            self.pedigree_view.load_canvas(self.active_person)
        elif page == 3:
            self.source_view.load_sources()
        elif page == 4:
            if len(self.db.getPlaceKeys()) > 2000:
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
            Plugins.ToolPlugins(self.db,self.active_person,
                                self.tool_callback)

    def on_reports_clicked(self,obj):
        if self.active_person:
            Plugins.ReportPlugins(self.db,self.active_person)

    def on_ok_button1_clicked(self,obj):
    
        dbname = obj.get_data("dbname")
        getoldrev = obj.get_data("getoldrev")
        filename = dbname.get_full_path(0)
        Utils.destroy_passed_object(obj)

        if filename == "" or filename == None:
            return
        filename = os.path.normpath(os.path.abspath(filename))
        
        self.clear_database(0)
    
        if getoldrev.get_active():
            vc = VersionControl.RcsVersionControl(filename)
            VersionControl.RevisionSelect(self.db,filename,vc,
                                          self.load_revision)
        else:
            self.auto_save_load(filename)

    def auto_save_load(self,filename):

        filename = os.path.normpath(os.path.abspath(filename))
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

        base = os.path.basename(filename)
        if base == const.xmlFile:
            filename = os.path.dirname(filename)
        elif base == "autosave.gramps":
            filename = os.path.dirname(filename)
        elif not os.path.isdir(filename):
            self.displayError(_("Database could not be opened"),
                              _("%s is not a directory.") % filename + ' ' + \
                              _("You should select a directory that contains a "
                                "data.gramps file or a gramps.zodb file."))
            return

        if self.load_database(filename) == 1:
            if filename[-1] == '/':
                filename = filename[:-1]
            name = os.path.basename(filename)
            self.topWindow.set_title("%s - GRAMPS" % name)
        else:
            GrampsCfg.save_last_file("")
        self.topWindow.set_resizable(gtk.TRUE)
        
    def cl_import(self,filename,format):
        if format == 'gedcom':
            import ReadGedcom
            filename = os.path.normpath(os.path.abspath(filename))
            try:
                g = ReadGedcom.GedcomParser(self.db,filename,None)
                g.parse_gedcom_file()
                g.resolve_refns()
                del g
            except:
                print "Error importing %s" % filename
                os._exit(1)
        elif format == 'gramps':
            try:
                dbname = os.path.join(filename,const.xmlFile)
                ReadXML.importData(self.db,dbname,None)
            except:
                print "Error importing %s" % filename
        elif format == 'gramps-pkg':
            # Create tempdir, if it does not exist, then check for writability
            tmpdir_path = os.path.expanduser("~/.gramps/tmp" )
            if not os.path.isdir(tmpdir_path):
                try:
                    os.mkdir(tmpdir_path,0700)
                except:
                    print "Could not create temporary directory %s" % tmpdir_path 
                    os._exit(1)
            elif not os.access(tmpdir_path,os.W_OK):
                print "Temporary directory %s is not writable" % tmpdir_path 
                os._exit(1)
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
                print "Error extracting into %s" % tmpdir_path 
                os._exit(1)

            dbname = os.path.join(tmpdir_path,const.xmlFile)  

            try:
                ReadXML.importData(self.db,dbname,None)
            except:
                print "Error importing %s" % filename
            # Clean up tempdir after ourselves
            files = os.listdir(tmpdir_path) 
            for fn in files:
                os.remove(os.path.join(tmpdir_path,fn))
            os.rmdir(tmpdir_path)
        else:
            print "Invalid format:  %s" % format
            os._exit(1)
        if not self.cl:
            return self.post_load(self.impdir_path)

    def cl_export(self,filename,format):
        if format == 'gedcom':
            print "Command-line export to gedcom is not implemented yet."
            os._exit(0)
        elif format == 'gramps':
            filename = os.path.normpath(os.path.abspath(filename))
            dbname = os.path.join(filename,const.xmlFile)
            if filename:
                self.save_media(filename)
                self.db.save(dbname,None)
        elif format == 'gramps-pkg':
            import TarFile
            import time
            import WriteXML
            from cStringIO import StringIO

            t = TarFile.TarFile(filename)
            mtime = time.time()
        
            # Write media files first, since the database may be modified 
            # during the process (i.e. when removing object)
            ObjectMap = self.db.getObjectMap()
            for ObjectId in ObjectMap.keys():
                oldfile = ObjectMap[ObjectId].getPath()
                base = os.path.basename(oldfile)
                if os.path.isfile(oldfile):
                    g = open(oldfile,"rb")
                    t.add_file(base,mtime,g)
                    g.close()

            # Write XML now
            g = StringIO()
            gfile = WriteXML.XmlWriter(self.db,None,1)
            gfile.write_handle(g)
            mtime = time.time()
            t.add_file("data.gramps",mtime,g)
            g.close()
            t.close()
        elif format == 'iso':
            print "Command-line export to iso is not implemented yet."
            os._exit(0)
        else:
            print "Invalid format:  %s" % format
            os._exit(1)

    def cl_action(self,action):
        if action == 'check':
            import Check
            checker = Check.CheckIntegrity(self.db)
            checker.check_for_broken_family_links()
            checker.cleanup_missing_photos()
            checker.check_parent_relationships()
            checker.cleanup_empty_families(0)
            errs = checker.build_report(1)
            if errs:
                checker.report(1)
        elif action == 'summary':
            print "Command-line summary is not implemented yet."
            os._exit(0)
        else:
            print "Unknown action: %s." % action
            os._exit(1)

    def on_ok_button2_clicked(self,obj):
        filename = obj.get_filename()
        filename = os.path.normpath(os.path.abspath(filename))
        if filename:
            Utils.destroy_passed_object(obj)
            self.save_media(filename)
            if GrampsCfg.usevc and GrampsCfg.vc_comment:
                self.display_comment_box(filename)
            else:
                self.save_file(filename,_("No Comment Provided"))

    def save_media(self,filename):
        import RelImage
        #-------------------------------------------------------------------------
        def remove_clicked():
            # File is lost => remove all references and the object itself
            mobj = ObjectMap[ObjectId]
            for p in self.db.getFamilyMap().values():
                nl = p.getPhotoList()
                for o in nl:
                    if o.getReference() == mobj:
                        nl.remove(o) 
                p.setPhotoList(nl)
            for key in self.db.getPersonKeys():
                p = self.db.getPerson(key)
                nl = p.getPhotoList()
                for o in nl:
                    if o.getReference() == mobj:
                        nl.remove(o) 
                p.setPhotoList(nl)
            for key in self.db.getSourceKeys():
                p = self.db.getSource(key)
                nl = p.getPhotoList()
                for o in nl:
                    if o.getReference() == mobj:
                        nl.remove(o) 
                p.setPhotoList(nl)
            for key in self.db.getPlaceKeys():
                p = self.db.getPlace(key)
                nl = p.getPhotoList()
                for o in nl:
                    if o.getReference() == mobj:
                        nl.remove(o) 
                p.setPhotoList(nl)
            self.db.removeObject(ObjectId) 
    
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
                    ObjectMap[ObjectId].setPath(newfile)
                Utils.destroy_passed_object(fs_top)

            fs_top = gtk.FileSelection("%s - GRAMPS" % _("Select file"))
            fs_top.hide_fileop_buttons()
            fs_top.ok_button.connect('clicked',fs_ok_clicked)
            fs_top.cancel_button.connect('clicked',fs_close_window)
            fs_top.show()
            fs_top.run()

        #-------------------------------------------------------------------------
        ObjectMap = self.db.getObjectMap()
        for ObjectId in ObjectMap.keys():
            if ObjectMap[ObjectId].getLocal():
                oldfile = ObjectMap[ObjectId].getPath()
                (base,ext) = os.path.splitext(os.path.basename(oldfile))
                newfile = os.path.join(filename,os.path.basename(oldfile))
                ObjectMap[ObjectId].setPath(newfile)
                if os.path.isfile(oldfile):
                    RelImage.import_media_object(oldfile,filename,base)
                else:
                    # File is lost => ask what to do
                    MissingMediaDialog(_("Media object could not be found"),
	                _("%(file_name)s is referenced in the database, but no longer exists. " 
                            "The file may have been deleted or moved to a different location. " 
                            "You may choose to either remove the reference from the database, " 
                            "keep the reference to the missing file, or select a new file." 
                            ) % { 'file_name' : oldfile },
                        remove_clicked, leave_clicked, select_clicked)

    def save_file(self,filename,comment):        

        path = filename
        filename = os.path.normpath(os.path.abspath(filename))
        autosave = "%s/autosave.gramps" % filename
    
        self.status_text(_("Saving %s ...") % filename)

        Utils.clearModified()
        Utils.clear_timer()

        if os.path.exists(filename):
            if not os.path.isdir(filename):
                self.displayError(_("Database could not be opened"),
                                  _("%s is not a directory.") % filename + ' ' + \
                                  _("The file you should attempt to open should be "
                                    "a directory that contains a data.gramps file or "
                                    "a gramps.zodb file."))
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
            self.db.save(filename,self.load_progress)
            self.db.clear_added_media_objects()
        except (OSError,IOError), msg:
            emsg = _("Could not create %s") % filename
            ErrorDialog(emsg,_("An error was detected while trying to create the file"))
            return
        
        self.db.setSavePath(old_file)
        GrampsCfg.save_last_file(old_file)

        if GrampsCfg.usevc:
            vc = VersionControl.RcsVersionControl(path)
            vc.checkin(filename,comment,not GrampsCfg.uncompress)

        filename = self.db.getSavePath()
        if filename[-1] == '/':
            filename = filename[:-1]
        name = os.path.basename(filename)
        self.topWindow.set_title("%s - GRAMPS" % name)
        self.status_text("")
        self.statusbar.set_progress_percentage(0.0)
        if os.path.exists(autosave):
            try:
                os.remove(autosave)
            except:
                pass

    def autosave_database(self):
        path = self.db.getSavePath()
        if not path:
            return 1
        
        Utils.clear_timer()

        filename = "%s/autosave.gramps" % (path)
    
        self.status_text(_("autosaving..."));
        try:
            self.db.save(filename,self.quick_progress)
            self.status_text(_("autosave complete"));
        except (IOError,OSError),msg:
            self.status_text("%s - %s" % (_("autosave failed"),msg))
        except:
            DisplayTrace.DisplayTrace()
        return 0

    def load_selected_people(self,obj):
        """Display the selected people in the EditPerson display"""
        if self.active_person:
            self.load_person(self.active_person)

    def load_active_person(self,obj):
        self.load_person(self.active_person)
    
    def load_new_person(self,obj):
        self.active_person = RelLib.Person()
        try:
            EditPerson.EditPerson(self.active_person,self.db,
                                  self.new_after_edit)
        except:
            DisplayTrace.DisplayTrace()

    def delete_person_clicked(self,obj):
        mlist = self.person_tree.get_selected_objects()

        for sel in mlist:
            p = self.db.getPerson(sel)
            name = GrampsCfg.nameof(p) 

            QuestionDialog(_('Delete %s?') % name,
                           _('Deleting the person will remove the person from '
                             'from the database. The data can only be '
                             'recovered by closing the database without saving '
                             'changes. This change will become permanent '
                             'after you save the database.'),
                           _('_Delete Person'),
                           self.delete_person_response)

    def delete_person_response(self):
        for family in self.active_person.getFamilyList():
            if self.active_person == family.getFather():
                if family.getMother() == None:
                    for child in family.getChildList():
                        child.removeAltFamily(family)
                    self.db.deleteFamily(family)
                else:
                    family.setFather(None)
            else:
                if family.getFather() == None:
                    for child in family.getChildList():
                        child.removeAltFamily(family)
                    self.db.deleteFamily(family)
                else:
                    family.setMother(None)

        family = self.active_person.getMainParents()
        if family:
            family.removeChild(self.active_person)
            
        self.db.removePerson(self.active_person.getId())
        self.remove_from_person_list(self.active_person)
        self.person_model.sort_column_changed()
        self.update_display(0)
        Utils.modified()

    def remove_from_person_list(self,person,old_id=None):
        pid = person.getId()
        if old_id:
            del_id = old_id
        else:
            del_id = pid

        if self.id2col.has_key(del_id):
            (model,iter) = self.id2col[del_id]
            model.remove(iter)
            del self.id2col[del_id]
            
            if person == self.active_person:
                self.active_person = None
    
    def merge_update(self,p1,p2,old_id):
        self.remove_from_person_list(p1,old_id)
        self.remove_from_person_list(p2)
        self.redisplay_person_list(p1)
        self.update_display(0)
    
    def alpha_event(self,obj):
        self.load_person(self.active_person)

    def goto_active_person(self):
        if not self.active_person:
            self.person_tree = self.pl_page[0]
            self.person_list = self.pl_page[0].tree
            self.person_model = self.pl_page[0].model
            self.ptabs.set_current_page(0)
            return
        
        id = self.active_person.getId()
        if self.id2col.has_key(id):
            (model,iter) = self.id2col[id]
        else:
            val = self.db.getPersonDisplay(id)
            pg = val[5]
            if pg and pg != '@':
                pg = pg[0]
            else:
                pg = ''
            model = self.alpha_page[pg]
            iter = None

        self.ptabs.set_current_page(self.model2page[model])

        if not self.model_used.has_key(model) or self.model_used[model] == 0 or not iter:
            self.model_used[model] = 1
            self.apply_filter(model)
            (model,iter) = self.id2col[id]
            
        model.selection.unselect_all()
        model.selection.select_iter(iter);
        itpath = model.model.get_path(iter)
        col = model.tree.get_column(0)
        model.tree.scroll_to_cell(itpath,col,1,0.5,0)
            
    def change_active_person(self,person):
        if person != self.active_person:
            self.active_person = person
            self.modify_statusbar()
        if person:
            val = 1
        else:
            val = 0
        
        self.report_menu.set_sensitive(val)
        self.tools_menu.set_sensitive(val)
        self.report_button.set_sensitive(val)
        self.tool_button.set_sensitive(val)
        self.remove_button.set_sensitive(val)
        self.edit_button.set_sensitive(val)
    
    def modify_statusbar(self):
        
        if self.active_person == None:
            self.status_text("")
        else:
            if GrampsCfg.status_bar == 0:
                name = GrampsCfg.nameof(self.active_person)
            elif GrampsCfg.status_bar == 1:
                pname = GrampsCfg.nameof(self.active_person)
                name = "[%s] %s" % (self.active_person.getId(),pname)
            else:
                name = self.display_relationship()
            self.status_text(name)
        return 0

    def display_relationship(self):
        try:
            pname = GrampsCfg.nameof(self.db.getDefaultPerson())
            (name,plist) = self.relationship(self.db.getDefaultPerson(),
                                             self.active_person)

            if name:
                return _("%(relationship)s of %(person)s") % {
                    'relationship' : name, 'person' : pname }
            else:
                return ""
        except:
            DisplayTrace.DisplayTrace()
	
    def on_open_activate(self,obj):
        if Utils.wasModified():
            self.delobj = obj
            SaveDialog(_('Save Changes Made to the Database?'),
                       _("Unsaved changes exist in the current database. If you "
                         "close without saving, the changes you have made will "
                         "be lost."),
                       self.close_noquit,
                       self.save_query_noquit)

        if not Utils.wasModified():
            wFs = gtk.glade.XML(const.revisionFile, "dbopen")
            wFs.signal_autoconnect({
                "on_ok_button1_clicked": self.on_ok_button1_clicked,
                "destroy_passed_object": Utils.destroy_passed_object
                })

            fileSelector = wFs.get_widget("dbopen")

            Utils.set_titles(fileSelector, wFs.get_widget('title'),
                             _('Open a database'))
        
            dbname = wFs.get_widget("dbname")
            getoldrev = wFs.get_widget("getoldrev")
            fileSelector.set_data("dbname",dbname)
            dbname.set_default_path(GrampsCfg.db_dir)
            fileSelector.set_data("getoldrev",getoldrev)
            getoldrev.set_sensitive(GrampsCfg.usevc)
            fileSelector.show()

    def on_revert_activate(self,obj):
        
        if self.db.getSavePath() != "":
            QuestionDialog(_('Revert to last saved database?'),
                           _('Reverting to the last saved database '
                             'will cause all unsaved changes to be lost, and '
                             'the last saved database will be loaded.'),
                           _('_Revert'),
                           self.revert_query)
        else:
            WarningDialog(_('Could Not Revert to the Previous Database.'),
                          _('GRAMPS could not find a previous version of '
                            'the database'))

    def revert_query(self):
        const.personalEvents = const.init_personal_event_list()
        const.personalAttributes = const.init_personal_attribute_list()
        const.marriageEvents = const.init_marriage_event_list()
        const.familyAttributes = const.init_family_attribute_list()
        const.familyRelations = const.init_family_relation_list()
        
        file = self.db.getSavePath()
        self.db.new()
        self.active_person = None
        self.place_loaded = 0
        self.id2col = {}
        self.read_file(file)
        Utils.clearModified()
        Utils.clear_timer()
        
    def on_save_as_activate(self,obj):
        wFs = gtk.glade.XML (const.gladeFile, "fileselection")
        wFs.signal_autoconnect({
            "on_ok_button1_clicked": self.on_ok_button2_clicked,
            "destroy_passed_object": Utils.destroy_passed_object
            })

        fileSelector = wFs.get_widget("fileselection")
        fileSelector.set_title('%s - GRAMPS' % _('Save database'))
        fileSelector.show()

    def on_save_activate(self,obj):
        """Saves the file, first prompting for a comment if revision
        control needs it"""
        if not self.db.getSavePath():
            self.on_save_as_activate(obj)
        else:
            if GrampsCfg.usevc and GrampsCfg.vc_comment:
                self.display_comment_box(self.db.getSavePath())
            else:
                msg = _("No Comment Provided")
                self.save_file(self.db.getSavePath(),msg)

    def on_save_activate_quit(self):
        """Saves the file, first prompting for a comment if revision
        control needs it"""
        if not self.db.getSavePath():
            self.on_save_as_activate(None)
        else:
            if GrampsCfg.usevc and GrampsCfg.vc_comment:
                self.display_comment_box(self.db.getSavePath())
            else:
                msg = _("No Comment Provided")
                self.save_file(self.db.getSavePath(),msg)

    def display_comment_box(self,filename):
        """Displays a dialog box, prompting for a revison control comment"""
        filename = os.path.normpath(os.path.abspath(filename))
        VersionControl.RevisionComment(filename,self.save_file)
    
    def on_person_list1_activate(self,obj):
        """Switches to the person list view"""
        self.views.set_current_page(0)

    def on_family1_activate(self,obj):
        """Switches to the family view"""
        self.views.set_current_page(1)

    def on_pedigree1_activate(self,obj):
        """Switches to the pedigree view"""
        self.views.set_current_page(2)

    def on_sources_activate(self,obj):
        """Switches to the sources view"""
        self.views.set_current_page(3)

    def on_places_activate(self,obj):
        """Switches to the places view"""
        if len(self.db.getPlaceKeys()) > 2000:
            self.status_text(_('Updating display - this may take a few seconds...'))
        else:
            self.status_text(_('Updating display...'))
        if self.place_loaded == 0:
            self.place_view.load_places()
            self.place_loaded = 1
        self.modify_statusbar()
        self.views.set_current_page(4)

    def on_media_activate(self,obj):
        """Switches to the media view"""
        self.views.set_current_page(5)

    def on_views_switch_page(self,obj,junk,page):
        """Load the appropriate page after a notebook switch"""
        if page == 0:
            self.enable_buttons(1)
            self.goto_active_person()
            self.merge_button.set_sensitive(1)
        elif page == 1:
            self.enable_buttons(0)
            self.merge_button.set_sensitive(0)
            self.family_view.load_family()
        elif page == 2:
            self.enable_buttons(0)
            self.merge_button.set_sensitive(0)
            self.pedigree_view.load_canvas(self.active_person)
        elif page == 3:
            self.enable_buttons(1)
            self.merge_button.set_sensitive(0)
            self.source_view.load_sources()
        elif page == 4:
            self.enable_buttons(1)
            self.merge_button.set_sensitive(1)
        elif page == 5:
            self.enable_buttons(1)
            self.merge_button.set_sensitive(0)
            self.media_view.load_media()
            
    def on_apply_filter_clicked(self,obj):
        invert_filter = self.filter_inv.get_active()
        qualifer = self.filter_text.get_text()
        mi = self.filter_list.get_menu().get_active()
        class_init = mi.get_data("function")
        self.DataFilter = class_init(qualifer)
        self.DataFilter.set_invert(invert_filter)
        self.model_used = {}
        self.apply_filter(self.person_model)

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

    def new_after_edit(self,epo,plist):
        if epo:
            if epo.person.getId() == "":
                self.db.addPerson(epo.person)
            else:
                self.db.addPersonNoMap(epo.person,epo.person.getId())
            self.db.buildPersonDisplay(epo.person.getId())
            self.change_active_person(epo.person)
            self.redisplay_person_list(epo.person)
        if self.views.get_current_page() == 1:
            self.family_view.load_family()
        for p in plist:
            self.place_view.new_place_after_edit(p)

    def update_after_newchild(self,family,person,plist):
        self.family_view.load_family(family)
        self.redisplay_person_list(person)
        for p in plist:
            self.place_view.new_place_after_edit(p)

    def update_after_edit(self,epo,plist):
        if epo:
            self.db.buildPersonDisplay(epo.person.getId(),epo.original_id)
            self.remove_from_person_list(epo.person,epo.original_id)
            self.redisplay_person_list(epo.person)
        for p in plist:
            self.place_view.new_place_after_edit(p)
        self.update_display(0)

    def update_after_merge(self,person,old_id):
        if person:
            self.remove_from_person_list(person,old_id)
            self.redisplay_person_list(person)
        self.update_display(0)

    def add_to_person_list(self,person,change):
        key = person.getId()
        val = self.db.getPersonDisplay(person.getId())
        pg = unicode(val[5])
        pg = pg[0]
        if self.DataFilter.compare(person):

            if pg and pg != '@':
                if not self.alpha_page.has_key(pg):
                    self.create_new_panel(pg)
                model = self.alpha_page[pg]
            else:
                model = self.default_list
            
            iter = model.add([val[0],val[1],val[2],val[3],val[4],val[5],
                              val[6],val[7]],key)

            self.id2col[key] = (model,iter)

            if change:
                self.change_active_person(person)
                self.goto_active_person()
            model.sort()
        
    def redisplay_person_list(self,person):
        self.add_to_person_list(person,1)

    def update_person_list(self,person):
        self.add_to_person_list(person,0)
            
    def load_person(self,person):
        if person:
            try:
                EditPerson.EditPerson(person, self.db, self.update_after_edit)
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
        self.db.setSavePath(name)
        res = self.db.getResearcher()
        owner = GrampsCfg.get_researcher()
    
        if res.getName() == "" and owner.getName():
            self.db.setResearcher(owner)
            Utils.modified()

        self.setup_bookmarks()

        try:
            mylist = self.db.getPersonEventTypes()
            for type in mylist:
                ntype = const.display_pevent(type)
                if ntype not in const.personalEvents:
                    const.personalEvents.append(ntype)
                    
            mylist = self.db.getFamilyEventTypes()
            for type in mylist:
                ntype = const.display_fevent(type)
                if ntype not in const.marriageEvents:
                    const.marriageEvents.append(ntype)

            mylist = self.db.getPersonAttributeTypes()
            for type in mylist:
                ntype = const.display_pattr(type)
                if ntype not in const.personalAttributes:
                    const.personalAttributes.append(ntype)

            mylist = self.db.getFamilyAttributeTypes()
            for type in mylist:
                if type not in const.familyAttributes:
                    const.familyAttributes.append(type)

            mylist = self.db.getFamilyRelationTypes()
            for type in mylist:
                if type not in const.familyRelations:
                    const.familyRelations.append(type)
        except:
            pass

        GrampsCfg.save_last_file(name)
        self.gtop.get_widget("filter").set_text("")
    
        self.statusbar.set_progress_percentage(1.0)

        person = self.db.getDefaultPerson()
        if person:
            self.active_person = person

        self.full_update()
        self.statusbar.set_progress_percentage(0.0)
        return 1
    
    def load_database(self,name):

        filename = "%s/%s" % (name,const.xmlFile)
        if not os.path.isfile(filename) and zodb_ok:
            filename = "%s/%s" % (name,const.zodbFile)
            self.clear_database(1)
        else:
            self.clear_database(0)

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
        self.bookmarks = Bookmarks.Bookmarks(self.db.getBookmarks(),
                                             self.gtop.get_widget("jump_to"),
                                             self.bookmark_callback)

    def displayError(self,msg,msg2):
        ErrorDialog(msg,msg2)
        self.status_text("")

    def complete_rebuild(self):
        self.topWindow.set_resizable(gtk.FALSE)
        self.apply_filter()
        self.goto_active_person()
        self.modify_statusbar()
        self.topWindow.set_resizable(gtk.TRUE)

    def apply_filter(self,current_model=None):

        self.status_text(_('Updating display...'))

        datacomp = self.DataFilter.compare
        if current_model == None:
            self.id2col = {}

        for key in self.db.getPersonKeys():
            person = self.db.getPerson(key)
            val = self.db.getPersonDisplay(key)
            pg = val[5]
            if pg and pg != '@':
                pg = pg[0]
            else:
                pg = ''

            if datacomp(person):
                if self.id2col.has_key(key):
                    continue
                if pg and pg != '@':
                    if not self.alpha_page.has_key(pg):
                        self.create_new_panel(pg)
                    model = self.alpha_page[pg]
                else:
                    model = self.default_list

                if current_model == model:
                    iter = model.add([val[0],val[1],val[2],val[3],val[4],val[5],
                                      val[6],val[7]],key)
                    self.id2col[key] = (model,iter)
            else:
                if self.id2col.has_key(key):
                    (model,iter) = self.id2col[key]
                    model.remove(iter)

        for i in self.pl_page:
            i.sort()
        self.modify_statusbar()

    def create_new_panel(self,pg):
        display = gtk.ScrolledWindow()
        display.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        tree = gtk.TreeView()
        tree.show()
        display.add(tree)
        display.show()
        model = ListModel.ListModel(tree,self.pl_titles,self.row_changed,
                                    self.alpha_event,_sel_mode)
        self.alpha_page[pg] = model
        for index in range(0,len(self.tab_list)):
            try:
                if pg < self.tab_list[index]:
                    self.ptabs.insert_page(display,gtk.Label(pg),index)
                    self.ptabs.set_show_tabs(1)
                    self.tab_list.insert(index,pg)
                    self.pl_page.insert(index,model)
                    break
            except:
                print index
        else:
            #added by EARNEY on 5/5/2003
            #modified the block below because sometimes certain
            #letters under people panel
            #will not load properly after a quick add
            #(ie, adding a parent under the family panel)
            index=len(self.tab_list)
            self.ptabs.insert_page(display,gtk.Label(pg),index)
            self.ptabs.set_show_tabs(1)
            self.tab_list.insert(index,pg)
            self.pl_page.insert(index,model)

            #instead of the following..
            #self.ptabs.insert_page(display,gtk.Label(pg),len(self.tab_list))
            #self.ptabs.set_show_tabs(1)
            #self.tab_list.append(pg)
            #self.pl_page = self.pl_page[0:-1] + [model,self.default_list]


        for index in range(0,len(self.tab_list)):
            model = self.alpha_page[self.tab_list[index]]
            self.model2page[model] = index
            self.model_used[model] = 0
        self.model2page[self.default_list] = len(self.tab_list)
        self.model_used[self.default_list] = 0

    def on_home_clicked(self,obj):
        temp = self.db.getDefaultPerson()
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
            WarningDialog(_("Could Not Set a Bookmark."),
                          _("A bookmark could not be set because no one was selected."))

    def on_edit_bookmarks_activate(self,obj):
        self.bookmarks.edit()
        
    def bookmark_callback(self,obj,person):
        self.change_active_person(person)
        self.update_display(0)
    
    def on_default_person_activate(self,obj):
        if self.active_person:
            name = self.active_person.getPrimaryName().getRegularName()
            QuestionDialog(_('Set %s as the Home Person') % name,
                           _('Once a Home Person is defined, pressing the '
                             'Home button on the toolbar will make the home '
                             'person the active person.'),
                           _('_Set Home Person'),
                           self.set_person)
            
    def set_person(self):
        self.db.setDefaultPerson(self.active_person)
        Utils.modified()

    def export_callback(self,obj,plugin_function):
        """Call the export plugin, with the active person and database"""
        if self.active_person:
            plugin_function(self.db,self.active_person)

    def import_callback(self,obj,plugin_function):
        """Call the import plugin"""
        plugin_function(self.db,self.active_person,self.tool_callback)
        self.topWindow.set_title("%s - GRAMPS" % self.db.getSavePath())

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
                        'be created.' + '\n' + str(msg) ))
                except OSError,msg:
                    ErrorDialog(_('Could not create database'),
                        _('The directory ~/.gramps/example could not '
                        'be created.' + '\n' + str(msg) ))
                except:
                    ErrorDialog(_('Could not create database'),
                        _('The directory ~/.gramps/example could not '
                        'be created.'))
                try:
                    dir = "%s/share/gramps/example" % const.prefixdir
                    for file in os.listdir(dir):
                        shutil.copy("%s/%s" % (dir,file), dest)
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
