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

"Export to GRAMPS package"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import time
import os
from cStringIO import StringIO

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
import gnome

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import WriteXML
import TarFile
import Utils
from QuestionDialog import MissingMediaDialog

from gettext import gettext as _

_title_string = _("Export to GRAMPS package")
#-------------------------------------------------------------------------
#
# writeData
#
#-------------------------------------------------------------------------
def writeData(database,person):
    try:
        PackageWriter(database)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()
    
#-------------------------------------------------------------------------
#
# PackageWriter
#
#-------------------------------------------------------------------------
class PackageWriter:

    def __init__(self,database):
        self.db = database

        choose = gtk.FileChooserDialog(_('Save GRAMPS Package'),
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_SAVE,
                                       (gtk.STOCK_CANCEL,
                                        gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_OPEN,
                                        gtk.RESPONSE_OK))
        
        choose.set_local_only(gtk.FALSE)
        filter = gtk.FileFilter()
        filter.set_name(_('GRAMPS package'))
        filter.add_pattern('*.gpkg')
        choose.add_filter(filter)

        response = choose.run()

        if response == gtk.RESPONSE_OK:
            name = choose.get_filename()
            if os.path.splitext(name)[1] != ".gpkg":
                name = name + ".gpkg"
            choose.destroy()
            self.export(name)
        else:
            choose.destroy()
            
    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','export-data')

    def export(self, filename):
        missmedia_action = 0
        #--------------------------------------------------------------
        def remove_clicked():
            # File is lost => remove all references and the object itself
            mobj = self.db.find_family_from_id(ObjectId)
            for p_id in self.db.get_family_keys():
                p = self.db.find_family_from_id(p_id)
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference() == mobj:
                        nl.remove(o) 
                p.set_media_list(nl)
            for key in self.db.get_person_keys():
                p = self.db.try_to_find_person_from_id(key)
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference() == mobj:
                        nl.remove(o) 
                p.set_media_list(nl)
            for key in self.db.get_source_keys():
                p = self.db.try_to_find_source_from_id(key)
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference() == mobj:
                        nl.remove(o) 
                p.set_media_list(nl)
            for key in self.db.get_place_id_keys():
                p = self.db.try_to_find_place_from_id(key)
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference() == mobj:
                        nl.remove(o) 
                p.set_media_list(nl)
            self.db.remove_object(ObjectId)

        def leave_clicked():
            # File is lost => do nothing, leave as is
            pass


        def select_clicked():
            # File is lost => select a file to replace the lost one
            def fs_close_window(obj):
                pass

            def fs_ok_clicked(obj):
                name = fs_top.get_filename()
                if os.path.isfile(name):
                    g = open(name,"rb")
                    t.add_file(base,mtime,g)
                    g.close()

            fs_top = gtk.FileSelection("%s - GRAMPS" % _("Select file"))
            fs_top.hide_fileop_buttons()
            fs_top.ok_button.connect('clicked',fs_ok_clicked)
            fs_top.cancel_button.connect('clicked',fs_close_window)
            fs_top.run()
            fs_top.destroy()
        #---------------------------------------------------------------

        t = TarFile.TarFile(filename)
        mtime = time.time()
        
        # Write media files first, since the database may be modified 
        # during the process (i.e. when removing object)
        for ObjectId in self.db.get_object_keys():
            oldfile = self.db.try_to_find_object_from_id(ObjectId).get_path()
            base = os.path.basename(oldfile)
            if os.path.isfile(oldfile):
                g = open(oldfile,"rb")
                t.add_file(base,mtime,g)
                g.close()
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
        
        # Write XML now
        g = StringIO()
        gfile = WriteXML.XmlWriter(self.db,None,1)
        gfile.write_handle(g)
        mtime = time.time()
        t.add_file("data.gramps",mtime,g)
        g.close()

        t.close()
    
#-------------------------------------------------------------------------
#
# Register the plugin
#
#-------------------------------------------------------------------------
from Plugins import register_export

register_export(writeData,_title_string)
