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
# GNOME modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
import gobject

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Utils
import const
import GrampsCfg
import gnome
import QuestionDialog
from gettext import gettext as _
import os

#-------------------------------------------------------------------------
#
# DbPrompter
#
#-------------------------------------------------------------------------
class DbPrompter:
    """Make sure a database is opened"""
    
    def __init__(self,db,want_new,parent=None):
        self.db = db
        opendb = gtk.glade.XML(const.gladeFile, "opendb","gramps")
        top = opendb.get_widget('opendb')
        if parent:
            top.set_transient_for(parent)
        title = opendb.get_widget('title')

        Utils.set_titles(top,title,_('Open a database'))

        new = opendb.get_widget("new")
        new.set_active(want_new)

        while 1:
            response = top.run()
            if response == gtk.RESPONSE_OK:
                if self.chooser(new.get_active()):
                    break
            elif response == gtk.RESPONSE_CANCEL:
                break
            elif response == gtk.RESPONSE_HELP:
                try:
                    gnome.help_display('gramps-manual','choose-db-start')
                except gobject.GError,msg:
                    QuestionDialog.ErrorDialog(_('Help not available'),msg)

        top.destroy()
        if response == gtk.RESPONSE_CANCEL:
            gtk.main_quit()

    def chooser(self,save):
        if save:
            choose = gtk.FileChooserDialog('Create GRAMPS database',
                                           None,
                                           gtk.FILE_CHOOSER_ACTION_SAVE,
                                           (gtk.STOCK_CANCEL,
                                            gtk.RESPONSE_CANCEL,
                                            gtk.STOCK_OPEN,
                                            gtk.RESPONSE_OK))
            self.db.clear_database()
        else:
            choose = gtk.FileChooserDialog('Open GRAMPS database',
                                           None,
                                           gtk.FILE_CHOOSER_ACTION_OPEN,
                                           (gtk.STOCK_CANCEL,
                                            gtk.RESPONSE_CANCEL,
                                            gtk.STOCK_OPEN,
                                            gtk.RESPONSE_OK))
            
        filter = gtk.FileFilter()
        filter.set_name(_('GRAMPS databases'))
        filter.add_pattern('*.grdb')
        choose.add_filter(filter)
        
        filter = gtk.FileFilter()
        filter.set_name(_('All files'))
        filter.add_pattern('*')
        choose.add_filter(filter)
        
        if save and GrampsCfg.lastfile:
            choose.set_filename(GrampsCfg.lastfile)

        response = choose.run()
        if response == gtk.RESPONSE_OK:
            filename = choose.get_filename()
            if save and os.path.splitext(filename)[1] != ".grdb":
                filename = filename + ".grdb"
            self.db.read_file(filename)
            choose.destroy()
            return 1
        else:
            choose.destroy()
            return 0

