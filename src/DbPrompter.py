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

#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
import gnome

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Utils
import const
import GrampsCfg
import VersionControl
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# DbPrompter
#
#-------------------------------------------------------------------------
class DbPrompter:
    """Make sure a database is opened"""
    
    def __init__(self,db,want_new,parent=None):
        self.db = db
        self.want_new = want_new
        self.parent = parent
        self.show()

    def show(self):
        opendb = gtk.glade.XML(const.gladeFile, "opendb","gramps")
        top = opendb.get_widget('opendb')
        if self.parent:
            top.set_transient_for(self.parent)
        title = opendb.get_widget('title')

        Utils.set_titles(top,title,_('Open a database'))
        
        opendb.signal_autoconnect({
            "on_open_ok_clicked" : self.open_ok_clicked,
            "on_open_help_clicked" : self.open_help_clicked,
            "on_open_cancel_clicked" : self.open_cancel_clicked,
            "on_opendb_delete_event": self.open_delete_event,
            })
        
        self.new = opendb.get_widget("new")
        if self.want_new:
            self.new.set_active(1)

    def open_ok_clicked(self,obj):
        if self.new.get_active():
            self.db.clear_database()
            self.save_as_activate()
        else:
            self.open_activate()
        Utils.destroy_passed_object(obj)

    def open_help_clicked(self,obj):
        """Display the GRAMPS manual"""
        gnome.help_display('gramps-manual','choose-db-start')

    def save_as_activate(self):
        wFs = gtk.glade.XML (const.gladeFile, "fileselection","gramps")
        wFs.signal_autoconnect({
            "on_ok_button1_clicked": self.save_ok_button_clicked,
            "destroy_passed_object": self.cancel_button_clicked,
            })
        filesel = wFs.get_widget('fileselection')
        filesel.set_title('%s - GRAMPS' % _('Create database'))

    def save_ok_button_clicked(self,obj):
        filename = obj.get_filename().encode('iso8859-1')
        if filename:
            Utils.destroy_passed_object(obj)
            self.db.read_file(filename)

    def open_activate(self):

        wFs = gtk.glade.XML (const.gladeFile, "fileselection","gramps")
        wFs.signal_autoconnect({
            "on_ok_button1_clicked": self.ok_button_clicked,
            "destroy_passed_object": self.cancel_button_clicked,
            })
        self.filesel = wFs.get_widget('fileselection')
        self.filesel.set_title('%s - GRAMPS' % _('Open database'))
        if GrampsCfg.lastfile:
            self.filesel.set_filename(GrampsCfg.lastfile)
        return
    
        wFs = gtk.glade.XML(const.revisionFile, "dbopen","gramps")
        wFs.signal_autoconnect({
            "on_ok_button1_clicked": self.ok_button_clicked,
            "destroy_passed_object": self.cancel_button_clicked,
            })

        self.fileSelector = wFs.get_widget("dbopen")
        Utils.set_titles(self.fileSelector,wFs.get_widget('title'),
                         _('Open a database'))

        self.dbname = wFs.get_widget("dbname")
        self.getoldrev = wFs.get_widget("getoldrev")
        if GrampsCfg.db_dir:
            self.dbname.set_default_path(GrampsCfg.db_dir)

        if GrampsCfg.lastfile:
            self.dbname.set_filename(GrampsCfg.lastfile)
            self.dbname.gtk_entry().set_position(len(GrampsCfg.lastfile))
        elif GrampsCfg.db_dir:
            self.dbname.set_filename(GrampsCfg.db_dir)
            self.dbname.gtk_entry().set_position(len(GrampsCfg.db_dir))
            
        self.getoldrev.set_sensitive(GrampsCfg.usevc)

    def cancel_button_clicked(self,obj):
        Utils.destroy_passed_object(obj)
        self.show()
        
    def ok_button_clicked(self,obj):
        filename = self.filesel.get_filename()

        if not filename:
            return
        Utils.destroy_passed_object(obj)
        self.db.read_file(filename)

    def open_delete_event(self,obj,event):
        gtk.mainquit()

    def open_cancel_clicked(self,obj):
        gtk.mainquit()

