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
        if gtk.pygtk_version[1] >= 3:
            choose = gtk.FileChooserDialog('Create GRAMPS database',
                                           None,
                                           gtk.FILE_CHOOSER_ACTION_SAVE,
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

            response = choose.run()
            if response == gtk.RESPONSE_OK:
                filename = choose.get_filename()
                self.db.read_file(filename)
            choose.destroy()
        else:
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
            if self.db.read_file(filename) == 1:
                Utils.destroy_passed_object(obj)

    def open_activate(self):
        if gtk.pygtk_version[1] >= 3:
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

            if GrampsCfg.lastfile:
                choose.set_filename(GrampsCfg.lastfile)

            response = choose.run()
            if response == gtk.RESPONSE_OK:
                filename = choose.get_filename()
                self.db.read_file(filename)
            choose.destroy()
        else:
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
    
    def cancel_button_clicked(self,obj):
        Utils.destroy_passed_object(obj)
        self.show()
        
    def ok_button_clicked(self,obj):
        filename = self.filesel.get_filename()

        if not filename:
            return
        if self.db.read_file(filename) == 1:
            Utils.destroy_passed_object(obj)

    def open_delete_event(self,obj,event):
        gtk.mainquit()

    def open_cancel_clicked(self,obj):
        gtk.mainquit()

