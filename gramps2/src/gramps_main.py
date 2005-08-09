#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2005  Donald N. Allingham
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

import gtk
import ViewManager
import PersonView
import ArgHandler
import DisplayTrace
import GrampsKeys
import GrampsCfg
import const
import Errors
import PluginMgr

from GrampsMime import mime_type_is_defined
from QuestionDialog import ErrorDialog

import gnome


iconpaths = ["/usr/share/gramps","~/devel/srcx"]

def register_stock_icons ():
    import os
    items = {
        'people48.png': ('gramps-person', 'Person', gtk.gdk.CONTROL_MASK, 0, ''),
        'family48.png': ('gramps-family', 'Family', gtk.gdk.CONTROL_MASK, 0, ''),
        'repos.png'   : ('gramps-repository', 'Repositories', gtk.gdk.CONTROL_MASK, 0, ''),
        'sources.png' : ('gramps-source', 'Sources', gtk.gdk.CONTROL_MASK, 0, ''),
        'events.png'  : ('gramps-event', 'Events', gtk.gdk.CONTROL_MASK, 0, ''),
        'place.png'   : ('gramps-place', 'Places', gtk.gdk.CONTROL_MASK, 0, ''),
        }
    
    # Register our stock items
    gtk.stock_add (items.values())
    
    # Add our custom icon factory to the list of defaults
    factory = gtk.IconFactory ()
    factory.add_default ()

    
    keys = items.keys()
    for key in keys:

        for dirname in iconpaths:
            icon_file = os.path.expanduser(os.path.join(dirname,key))
            if os.path.isfile(icon_file):
                break
        else:
            icon_file = os.path.join(iconpaths[0],'gramps.png')
            
        pixbuf = gtk.gdk.pixbuf_new_from_file (icon_file)
        pixbuf = pixbuf.add_alpha(True, chr(0xff), chr(0xff), chr(0xff))

        # Register icon to accompany stock item
        if pixbuf:
            icon_set = gtk.IconSet (pixbuf)
            factory.add (items[key][0], icon_set)
        else:
            print 'failed to load GTK logo for toolbar'

# class EventView(ListView):

#     def __init__(self):
#         PageView.__init__(self,'Events')

#     def define_actions(self):
#         self.add_action('Add',   gtk.STOCK_ADD,   '_Add', callback=self.add),
#         self.add_action('Edit',  gtk.STOCK_EDIT,  "_Edit")
#         self.add_action('Remove',gtk.STOCK_REMOVE,"_Remove")

#     def get_stock(self):
#         return 'gramps-event'
    
#     def ui_definition(self):
#         return '''<ui>
#           <menubar name="MenuBar">
#             <menu action="EditMenu">
#               <placeholder name="CommonEdit">
#                 <menuitem action="Add"/>
#                 <menuitem action="Edit"/>
#                 <menuitem action="Remove"/>
#               </placeholder>
#             </menu>
#           </menubar>
#           <toolbar name="ToolBar">
#             <placeholder name="CommonEdit">
#               <toolitem action="Add"/>
#               <toolitem action="Edit"/>
#               <toolitem action="Remove"/>
#             </placeholder>
#           </toolbar>
#         </ui>'''

#     def add(self,obj):
#         print "Event Add"



class Gramps:

    def __init__(self,args):

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

        try:
            GrampsCfg.loadConfig()
            self.welcome()    
        except OSError, msg:
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
#        GrampsKeys.client.notify_add("/apps/gramps/interface/toolbar",
##                                    self.toolbar_key_update)
#        GrampsKeys.client.notify_add("/apps/gramps/interface/toolbar-on",
#                                    self.toolbar_on_key_update)
#        GrampsKeys.client.notify_add("/apps/gramps/interface/filter",
#                                    self.filter_key_update)
#        GrampsKeys.client.notify_add("/apps/gramps/interface/view",
#                                    self.sidebar_key_update)
#        GrampsKeys.client.notify_add("/apps/gramps/interface/familyview",
#                                    self.familyview_key_update)
#        GrampsKeys.client.notify_add("/apps/gramps/preferences/name-format",
#                                    self.familyview_key_update)
#        GrampsKeys.client.notify_add("/apps/gramps/preferences/date-format",
#                                    self.date_format_key_update)

        register_stock_icons()
        a = ViewManager.ViewManager()
        a.register_view(PersonView.PersonView)
        a.init_interface()
        
        if GrampsKeys.get_usetips():
            TipOfDay.TipOfDay(self)

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

    def researcher_key_update(self,client,cnxn_id,entry,data):
        pass
#         self.db.set_person_id_prefix(GrampsKeys.get_person_id_prefix())
#         self.db.set_family_id_prefix(GrampsKeys.get_family_id_prefix())
#         self.db.set_source_id_prefix(GrampsKeys.get_source_id_prefix())
#         self.db.set_object_id_prefix(GrampsKeys.get_object_id_prefix())
#         self.db.set_place_id_prefix(GrampsKeys.get_place_id_prefix())
#         self.db.set_event_id_prefix(GrampsKeys.get_event_id_prefix())

    def statusbar_key_update(self,client,cnxn_id,entry,data):
        self.modify_statusbar()

    def toolbar_key_update(self,client,cnxn_id,entry,data):
        the_style = GrampsKeys.get_toolbar()
        if the_style == -1:
            self.toolbar.unset_style()
        else:
            self.toolbar.set_style(the_style)



    

