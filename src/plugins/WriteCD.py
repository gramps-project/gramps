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

"Export to CD (nautilus)"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
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
import gnome.vfs

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import WriteXML
import Utils
import const
import QuestionDialog
import ImgManip

from gettext import gettext as _

_title_string = _("Export to CD")

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

    def __init__(self,database,cl=0,name=""):
        self.db = database
        self.cl = cl
        self.name = name
	
        if self.cl:
	    self.cl_run()
        else:
            base = os.path.dirname(__file__)
            glade_file = "%s/%s" % (base,"cdexport.glade")
        
            dic = {
                "destroy_passed_object" : Utils.destroy_passed_object,
                "on_ok_clicked" : self.on_ok_clicked,
                "on_help_clicked" : self.on_help_clicked
                }
        
            self.top = gtk.glade.XML(glade_file,"packageExport","gramps")

            Utils.set_titles(self.top.get_widget('packageExport'),
                         self.top.get_widget('title'),_title_string)
        
            self.top.signal_autoconnect(dic)
            self.top.get_widget("packageExport").show()

    def copy_file(self,src,dest):
        original = open(src,"r")
        destobj = gnome.vfs.URI(dest)
        target = gnome.vfs.create(destobj,gnome.vfs.OPEN_WRITE)
        done = 0
        while 1:
            buf = original.read(2048)
            if buf == '':
                break
            else:
                target.write(buf)
        target.close()
        original.close()

    def make_thumbnail(self,dbname,root,path):
        img = ImgManip.ImgManip(path)
        data = img.jpg_scale_data(const.thumbScale,const.thumbScale)
        
        uri = gnome.vfs.URI('burn:///%s/.thumb/%s.jpg' % (dbname,root))
        th = gnome.vfs.create(uri,gnome.vfs.OPEN_WRITE)
        th.write(data)
        th.close()
                       
    def cl_run(self):
        base = os.path.basename(self.name)

        try:
            uri = gnome.vfs.URI('burn:///%s' % base)
            gnome.vfs.make_directory(uri,gnome.vfs.OPEN_WRITE)
        except gnome.vfs.FileExistsError, msg:
            QuestionDialog.ErrorDialog(_("CD export preparation failed"),
                                       "1 %s " % str(msg))
            return
        except:
            QuestionDialog.ErrorDialog("CD export preparation failed",
                                       'Could not create burn:///%s' % base)
            return

        try:
            uri = gnome.vfs.URI('burn:///%s/.thumb' % base)
            gnome.vfs.make_directory(uri,gnome.vfs.OPEN_WRITE)
        except gnome.vfs.FileExistsError, msg:
            QuestionDialog.ErrorDialog("CD export preparation failed",
                                       "2 %s " % str(msg))
            return

        for obj_id in self.db.get_object_keys():
            obj = self.db.try_to_find_object_from_id(obj_id)
            oldfile = obj.get_path()
            root = os.path.basename(oldfile)
            if os.path.isfile(oldfile):
                self.copy_file(oldfile,'burn:///%s/%s' % (base,root))
                if obj.get_mime_type()[0:5] == "image":
                    self.make_thumbnail(base,root,obj.get_path())
            else:
                print "Warning: media file %s was not found," % root,\
                    "so it was ignored."
            
        # Write XML now
        g = gnome.vfs.create('burn:///%s/data.gramps' % base,gnome.vfs.OPEN_WRITE )
        gfile = WriteXML.XmlWriter(self.db,None,1)
        gfile.write_handle(g)
        g.close()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','export-data')

    def on_ok_clicked(self,obj):
        Utils.destroy_passed_object(obj)
        missmedia_action = 0

        base = os.path.basename(self.db.get_save_path())

        try:
            uri = gnome.vfs.URI('burn:///%s' % base)
            gnome.vfs.make_directory(uri,gnome.vfs.OPEN_WRITE)
        except gnome.vfs.FileExistsError:
            QuestionDialog.ErrorDialog(_("CD export preparation failed"),
                                       "File already exists")
            return
        except:
            QuestionDialog.ErrorDialog(_("CD export preparation failed"),
                                       _('Could not create burn:///%s') % base)
            return

        try:
            uri = gnome.vfs.URI('burn:///%s/.thumb' % base)
            gnome.vfs.make_directory(uri,gnome.vfs.OPEN_WRITE)
        except gnome.vfs.FileExistsError, msg:
            QuestionDialog.ErrorDialog("CD export preparation failed",
                                       "4 %s " % str(msg))
            return
        except:
            QuestionDialog.ErrorDialog(_("CD export preparation failed"),
                                       _('Could not create burn:///%s/.thumb') % base)
            return

        #--------------------------------------------------------
        def remove_clicked():
            # File is lost => remove all references and the object itself
            mobj = self.db.get_object(self.object_id)
            for p_id in self.db.get_family_keys:
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
            self.db.remove_object(self.object_id) 
    
        def leave_clicked():
            # File is lost => do nothing, leave as is
            pass

        def select_clicked():
            # File is lost => select a file to replace the lost one
            def fs_close_window(obj):
                pass

            def fs_ok_clicked(obj):
                newfile = fs_top.get_filename()
                if os.path.isfile(newfile):
                    self.copy_file(newfile,'burn:///%s/%s' % (base,obase))
    	    	    ntype = Utils.get_mime_type(newfile)
		    if ntype[0:5] == "image":
                        self.make_thumbnail(base,obase,newfile)
		    
            fs_top = gtk.FileSelection("%s - GRAMPS" % _("Select file"))
            fs_top.hide_fileop_buttons()
            fs_top.ok_button.connect('clicked',fs_ok_clicked)
            fs_top.cancel_button.connect('clicked',fs_close_window)
            fs_top.run()
            fs_top.destroy()

        #----------------------------------------------------------

        # Write media files first, since the database may be modified 
        # during the process (i.e. when removing object)

        for obj_id in self.db.get_object_keys():
            obj = self.db.try_to_find_object_from_id(obj_id)
            oldfile = obj.get_path()
            root = os.path.basename(oldfile)
            if os.path.isfile(oldfile):
                self.copy_file(oldfile,'burn:///%s/%s' % (base,root))
                if obj.get_mime_type()[0:5] == "image":
                    self.make_thumbnail(base,root,obj.get_path())
            else:
                # File is lost => ask what to do
                self.object_id = obj.get_id()
                if missmedia_action == 0:
                    mmd = QuestionDialog.MissingMediaDialog(_("Media object could not be found"),
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
        g = gnome.vfs.create('burn:///%s/data.gramps' % base,gnome.vfs.OPEN_WRITE )
        gfile = WriteXML.XmlWriter(self.db,None,1)
        gfile.write_handle(g)
        g.close()
        os.system("nautilus --no-desktop burn:///")
    
#-------------------------------------------------------------------------
#
# Register the plugin
#
#-------------------------------------------------------------------------
from Plugins import register_export

register_export(writeData,_title_string)
