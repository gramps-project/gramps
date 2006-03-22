#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
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
# GTK+/GNOME modules
#
#-------------------------------------------------------------------------
import gtk
import logging

log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GRAMPS  modules
#
#-------------------------------------------------------------------------
import ViewManager
import GrampsDb
import ArgHandler
import Config
import GrampsCfg
import const
import Errors
import TipOfDay
import DataViews
from Mime import mime_type_is_defined
from QuestionDialog import ErrorDialog
from TransUtils import sgettext as _

iconpaths = [const.image_dir,"."]

def register_stock_icons ():
    import os
    items = [
        (os.path.join(const.image_dir,'person.svg'),
         ('gramps-person',_('Person'),gtk.gdk.CONTROL_MASK,0,'')),
        (os.path.join(const.image_dir,'relation.svg'),
         ('gramps-family',_('Relationships'),gtk.gdk.CONTROL_MASK,0,'')),
        (os.path.join(const.image_dir,'flist.svg'),
         ('gramps-family-list',_('Family List'),gtk.gdk.CONTROL_MASK,0,'')),
        (os.path.join(const.image_dir,'media.svg'),
         ('gramps-media',_('Media'),gtk.gdk.CONTROL_MASK,0,'')),
        (os.path.join(const.image_dir,'ped24.png'),
         ('gramps-pedigree',_('Pedigree'),gtk.gdk.CONTROL_MASK,0,'')),
        (os.path.join(const.image_dir,'repos.png'),
         ('gramps-repository',_('Repositories'),gtk.gdk.CONTROL_MASK,0,'')),
        (os.path.join(const.image_dir,'sources.png'),
         ('gramps-source',_('Sources'),gtk.gdk.CONTROL_MASK,0,'')),
        (os.path.join(const.image_dir,'events.png'),
         ('gramps-event',_('Events'),gtk.gdk.CONTROL_MASK,0,'')),
        (os.path.join(const.image_dir,'place.png'),
         ('gramps-place',_('Places'),gtk.gdk.CONTROL_MASK,0,'')),
        (os.path.join(const.image_dir,'place.png'),
         ('gramps-map',_('Map'),gtk.gdk.CONTROL_MASK,0,'')),
        ]
    
    # Register our stock items
    gtk.stock_add (map(lambda x: x[1],items))
    
    # Add our custom icon factory to the list of defaults
    factory = gtk.IconFactory ()
    factory.add_default ()
    
    for (key,data) in items:

        for dirname in iconpaths:
            icon_file = os.path.expanduser(os.path.join(dirname,key))
            if os.path.isfile(icon_file):
                try:
                    pixbuf = gtk.gdk.pixbuf_new_from_file (icon_file)
                    break
                except:
                    pass
        else:
            icon_file = os.path.join(const.image_dir,'gramps.png')
            pixbuf = gtk.gdk.pixbuf_new_from_file (icon_file)
            
        pixbuf = pixbuf.add_alpha(True, chr(0xff), chr(0xff), chr(0xff))

        icon_set = gtk.IconSet (pixbuf)
        factory.add (data[0], icon_set)

class Gramps:
    """
    Main class corresponding to a running gramps process.

    There can be only one instance of this class per gramps application
    process. It may spawn several windows and control several databases.
    """

    def __init__(self,args):
        try:
            GrampsCfg.loadConfig()
            self.welcome()    
        except OSError, msg:
            ErrorDialog(_("Configuration error"),str(msg))
            return
        except Errors.GConfSchemaError, val:
            ErrorDialog(_("Configuration error"),str(val) +
                        _("\n\nPossibly the installation of GRAMPS "
                          "was incomplete. Make sure the GConf schema "
                          "of GRAMPS is properly installed."))
            gtk.main_quit()
            return
        except:
            log.error("Error reading configuration.", exc_info=True)
            return
            
        if not mime_type_is_defined(const.app_gramps):
            ErrorDialog(_("Configuration error"),
                        _("A definition for the MIME-type %s could not "
                          "be found \n\nPossibly the installation of GRAMPS "
                          "was incomplete. Make sure the MIME-types "
                          "of GRAMPS are properly installed.")
                        % const.app_gramps)
            gtk.main_quit()
            return


        register_stock_icons()
        
        state = GrampsDb.DbState()
        vm = ViewManager.ViewManager(state)
        for view in DataViews.get_views():
            vm.register_view(view)

        ArgHandler.ArgHandler(state,vm,args)

        vm.init_interface()
        state.db.request_rebuild()
        state.change_active_person(state.db.get_default_person())
        
        # Don't show main window until ArgHandler is done.
        # This prevents a window from annoyingly popping up when
        # the command line args are sufficient to operate without it.
        Config.client.notify_add("/apps/gramps/researcher",
                                    self.researcher_key_update)
        Config.client.notify_add("/apps/gramps/interface/statusbar",
                                    self.statusbar_key_update)
#        Config.client.notify_add("/apps/gramps/interface/toolbar",
##                                    self.toolbar_key_update)
#        Config.client.notify_add("/apps/gramps/interface/toolbar-on",
#                                    self.toolbar_on_key_update)
#        Config.client.notify_add("/apps/gramps/interface/filter",
#                                    self.filter_key_update)
#        Config.client.notify_add("/apps/gramps/interface/view",
#                                    self.sidebar_key_update)
#        Config.client.notify_add("/apps/gramps/interface/familyview",
#                                    self.familyview_key_update)
#        Config.client.notify_add("/apps/gramps/preferences/name-format",
#                                    self.familyview_key_update)
#        Config.client.notify_add("/apps/gramps/preferences/date-format",
#                                    self.date_format_key_update)

        if Config.get_usetips():
            TipOfDay.TipOfDay(vm.uistate)

##         # FIXME: THESE will have to be added (ViewManager?)
##         # once bookmarks work again
##         self.db.set_researcher(GrampsCfg.get_researcher())
##         self.db.connect('person-delete',self.on_remove_bookmark)
##         self.db.connect('person-update',self.on_update_bookmark)

    def welcome(self):
        if Config.get_welcome() >= 200:
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

        Config.save_welcome(200)
        Config.sync()

    def researcher_key_update(self,client,cnxn_id,entry,data):
        pass
#         self.db.set_person_id_prefix(Config.get_person_id_prefix())
#         self.db.set_family_id_prefix(Config.get_family_id_prefix())
#         self.db.set_source_id_prefix(Config.get_source_id_prefix())
#         self.db.set_object_id_prefix(Config.get_object_id_prefix())
#         self.db.set_place_id_prefix(Config.get_place_id_prefix())
#         self.db.set_event_id_prefix(Config.get_event_id_prefix())

    def statusbar_key_update(self,client,cnxn_id,entry,data):
        self.modify_statusbar()

    def toolbar_key_update(self,client,cnxn_id,entry,data):
        the_style = Config.get_toolbar()
        if the_style == -1:
            self.toolbar.unset_style()
        else:
            self.toolbar.set_style(the_style)
