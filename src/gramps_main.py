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
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import os
import platform

import logging
log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GTK+/GNOME modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS  modules
#
#-------------------------------------------------------------------------
import ViewManager
import GrampsDb
import ArgHandler
import Config
import const
import Errors
import TipOfDay
import DataViews
from Mime import mime_type_is_defined
from QuestionDialog import ErrorDialog

#-------------------------------------------------------------------------
#
# helper functions
#
#-------------------------------------------------------------------------
iconpaths = [const.image_dir,"."]

if platform.system() == "Windows":
    person_icon = "person.png"
    relation_icon = "relation.png"
else:
    person_icon = "person.svg"
    relation_icon = "relation.svg"

def register_stock_icons ():
    items = [
        (os.path.join(const.image_dir,person_icon),
         ('gramps-person',_('Person'),gtk.gdk.CONTROL_MASK,0,'')),
        (os.path.join(const.image_dir,relation_icon),
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
        (os.path.join(const.image_dir,'stock_export.png'),
         ('gramps-export',_('Map'),gtk.gdk.CONTROL_MASK,0,'')),
        (os.path.join(const.image_dir,'stock_undo-history.png'),
         ('gramps-undo-history',_('Undo History'),gtk.gdk.CONTROL_MASK,0,'')),
        (os.path.join(const.image_dir,'stock_add-bookmark.png'),
         ('gramps-add-bookmark',_('Add bookmark'),gtk.gdk.CONTROL_MASK,0,'')),
        (os.path.join(const.image_dir,'stock_edit-bookmark.png'),
         ('gramps-edit-bookmark',_('Edit bookmarks'),gtk.gdk.CONTROL_MASK,0,'')),
        (os.path.join(const.image_dir,'stock_insert-url.png'),
         ('gramps-url',_('URL'),gtk.gdk.CONTROL_MASK,0,'')),
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


def build_user_paths():
    user_paths = [const.home_dir,
                  os.path.join(const.home_dir,"filters"),
                  os.path.join(const.home_dir,"plugins"),
                  os.path.join(const.home_dir,"templates"),
                  os.path.join(const.home_dir,"thumb")]
    
    for path in user_paths:
        if not os.path.isdir(path):
            os.mkdir(path)

#-------------------------------------------------------------------------
#
# Main Gramps class
#
#-------------------------------------------------------------------------
class Gramps:
    """
    Main class corresponding to a running gramps process.

    There can be only one instance of this class per gramps application
    process. It may spawn several windows and control several databases.
    """

    def __init__(self,args):
        try:
            build_user_paths()
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
        self.vm = ViewManager.ViewManager(state)
        for view in DataViews.get_views():
            self.vm.register_view(view)

        self.vm.init_interface()

        # Depending on the nature of this session,
        # we may need to change the order of operation
        ah = ArgHandler.ArgHandler(state,self.vm,args)
        if ah.need_gui():
            self.vm.post_init_interface()
            ah.handle_args()
        else:
            ah.handle_args()
            self.vm.post_init_interface()

        state.db.request_rebuild()
        state.change_active_person(state.db.get_default_person())
        
        if Config.get(Config.USE_TIPS):
            TipOfDay.TipOfDay(self.vm.uistate)


    def welcome(self):
        if not Config.get(Config.BETAWARN):
            from QuestionDialog import WarningDialog
            WarningDialog(
                _('Danger: This is unstable code!'),
                _("The GRAMPS 2.1 release is an early, experimental "
                  "branch of the future 2.2 release. This version is "
                  "not meant for normal usage. Use at your own risk.\n\n"
                  "This version may:\n1) Fail to run properly\n"
                  "2) Corrupt your data\n3) Cause your hair to turn "
                  "pink and fall out.\n\nAny databases opened by this "
                  "version will <b>NO LONGER WORK</b> in older versions of "
                  "GRAMPS, and <b>MAY NOT WORK</b> in with future "
                  "releases of GRAMPS. <b>BACKUP</b> your existing databases "
                  "before opening them with this version, and make "
                  "sure to export your data to XML every now and then."))
            Config.set(Config.AUTOLOAD,False)
            Config.set(Config.BETAWARN,True)
                            
        return
