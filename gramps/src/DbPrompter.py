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
# GNOME modules
#
#-------------------------------------------------------------------------
import libglade
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Utils
import const
import GrampsCfg
import VersionControl
from intl import gettext
_ = gettext

try:
    import ZODB
    _zodb = 1
except:
    _zodb = 0
    
#-------------------------------------------------------------------------
#
# DbPrompter
#
#-------------------------------------------------------------------------
class DbPrompter:
    """Make sure a database is opened"""
    
    def __init__(self,db,want_new):
        self.db = db
        self.want_new = want_new
        self.show()

    def show(self):
        opendb = libglade.GladeXML(const.gladeFile, "opendb")
        opendb.signal_autoconnect({
            "on_open_ok_clicked" : self.open_ok_clicked,
            "on_open_cancel_clicked" : self.open_cancel_clicked,
            "on_opendb_delete_event": self.open_delete_event,
            })
        self.new = opendb.get_widget("new")
        self.zodb = opendb.get_widget("zodb")
        if self.want_new:
            self.new.set_active(1)
        if _zodb:
            self.zodb.show()

    def open_ok_clicked(self,obj):
        if self.new.get_active():
            self.db.clear_database(0)
            self.save_as_activate()
        elif self.zodb.get_active():
            self.db.clear_database(1)
            self.save_as_activate()
        else:
            self.open_activate()
        Utils.destroy_passed_object(obj)

    def save_as_activate(self):
        wFs = libglade.GladeXML (const.gladeFile, "fileselection")
        wFs.signal_autoconnect({
            "on_ok_button1_clicked": self.save_ok_button_clicked,
            "destroy_passed_object": self.cancel_button_clicked,
            })

    def save_ok_button_clicked(self,obj):
        filename = obj.get_filename()
        if filename:
            Utils.destroy_passed_object(obj)
            if GrampsCfg.usevc and GrampsCfg.vc_comment:
                self.db.display_comment_box(filename)
            else:
                self.db.save_file(filename,_("No Comment Provided"))

    def open_activate(self):
        wFs = libglade.GladeXML(const.revisionFile, "dbopen")
        wFs.signal_autoconnect({
            "on_ok_button1_clicked": self.ok_button_clicked,
            "destroy_passed_object": self.cancel_button_clicked,
            })

        self.fileSelector = wFs.get_widget("dbopen")
        self.dbname = wFs.get_widget("dbname")
        self.getoldrev = wFs.get_widget("getoldrev")
        self.dbname.set_default_path(GrampsCfg.db_dir)
        self.getoldrev.set_sensitive(GrampsCfg.usevc)

    def cancel_button_clicked(self,obj):
        Utils.destroy_passed_object(obj)
        self.show()
        
    def ok_button_clicked(self,obj):
        filename = self.dbname.get_full_path(0)

        if not filename:
            return

        Utils.destroy_passed_object(obj)
    
        if self.getoldrev.get_active():
            vc = VersionControl.RcsVersionControl(filename)
            VersionControl.RevisionSelect(self.db.database,filename,vc,
                                          self.db.load_revision,self.show)
        else:
            self.db.read_file(filename)

    def open_delete_event(self,obj,event):
        gtk.mainquit()

    def open_cancel_clicked(self,obj):
        gtk.mainquit()

