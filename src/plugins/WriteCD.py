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

"Export to CD (nautilus)"

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
import gnome.vfs

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import WriteXML
import Utils
import const
from QuestionDialog import MissingMediaDialog
import RelImage

from intl import gettext as _

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
        
        base = os.path.dirname(__file__)
        glade_file = "%s/%s" % (base,"cdexport.glade")
        
        
        dic = {
            "destroy_passed_object" : Utils.destroy_passed_object,
            "on_ok_clicked" : self.on_ok_clicked
            }
        
        self.top = gtk.glade.XML(glade_file,"packageExport")

        Utils.set_titles(self.top.get_widget('packageExport'),
                         self.top.get_widget('title'),
                         _('Export to CD'))
        
        self.top.signal_autoconnect(dic)
        self.top.get_widget("packageExport").show()

    def vfs_copy(self,dir_name,filename,newfilename=""):
    	# Everything has to be ascii for the CD
	dir_name = dir_name.encode('ascii')
    	filename = filename.encode('ascii')
    	newfilename = newfilename.encode('ascii')

    	orig_file = open(filename,"r")
	if not newfilename:
	    newfilename = filename
	new_vfsname = 'burn:///%s/%s' % (dir_name,newfilename)
	new_file = gnome.vfs.create(new_vfsname,gnome.vfs.OPEN_WRITE) 
    	buf = orig_file.read()
    	new_file.write(buf)
    	orig_file.close()
    	new_file.close()

    def on_ok_clicked(self,obj):
        Utils.destroy_passed_object(obj)

        base = os.path.basename(self.db.getSavePath())
        thumb_base = os.path.join(base,'.thumb')

        gnome.vfs.make_directory('burn:///%s' % base,gnome.vfs.OPEN_WRITE)
        gnome.vfs.make_directory('burn:///%s' % thumb_base,gnome.vfs.OPEN_WRITE)

        #--------------------------------------------------------
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
            Utils.modified() 
    
        def leave_clicked():
            # File is lost => do nothing, leave as is
            pass

        def select_clicked():
            # File is lost => select a file to replace the lost one
            def fs_close_window(obj):
                fs_top.destroy()

            def fs_ok_clicked(obj):
                newfile = fs_top.get_filename()
                fs_top.destroy()
                if os.path.isfile(newfile):
    	    	    nbase = os.path.basename(newfile)
		    self.vfs_copy(base,newfile,obase)
    	    	    ntype = Utils.get_mime_type(newfile)
		    if ntype[0:5] == "image":
		    	(oname,oext) = os.path.splitext(obase)
		    	thumb_name = "%s.jpg" % oname 
			thumb_dest = "%s/.thumb/%s" % (opath,thumb_name)
		    	RelImage.check_thumb(newfile,thumb_dest,const.thumbScale)
		    	self.vfs_copy(thumb_base,thumb_dest,thumb_name)
		    
            fs_top = gtk.FileSelection("%s - GRAMPS" % _("Select file"))
            fs_top.hide_fileop_buttons()
            fs_top.ok_button.connect('clicked',fs_ok_clicked)
            fs_top.cancel_button.connect('clicked',fs_close_window)
            fs_top.show()
            fs_top.run()

        #----------------------------------------------------------

        # Write media files first, since the database may be modified 
        # during the process (i.e. when removing object)
	ObjectMap = self.db.getObjectMap()
        for ObjectId in ObjectMap.keys():
            oldfile = ObjectMap[ObjectId].getPath()
            opath = os.path.dirname(oldfile)
	    obase = os.path.basename(oldfile)
            if os.path.isfile(oldfile):
    	    	self.vfs_copy(base,oldfile,obase)
    	    	otype = Utils.get_mime_type(oldfile)
		if otype[0:5] == "image":
		    (oname,oext) = os.path.splitext(obase)
		    thumb_name = "%s.jpg" % oname 
		    thumb_dest = "%s/.thumb/%s" % (opath,thumb_name)
		    RelImage.check_thumb(oldfile,thumb_dest,const.thumbScale)
		    self.vfs_copy(thumb_base,thumb_dest,thumb_name)
            else:
                # File is lost => ask what to do
                MissingMediaDialog(_("Media object could not be found"),
	            _("%(file_name)s is referenced in the database, but no longer exists. " 
                        "The file may have been deleted or moved to a different location. " 
                        "You may choose to either remove the reference from the database, " 
                        "keep the reference to the missing file, or select a new file." 
                        ) % { 'file_name' : oldfile },
                    remove_clicked, leave_clicked, select_clicked)


        # Write XML now
        g = gnome.vfs.create('burn:///%s/data.gramps' % base,gnome.vfs.OPEN_WRITE )
        gfile = WriteXML.XmlWriter(self.db,None,1)
        gfile.write_handle(g)
        g.close()

    
#-------------------------------------------------------------------------
#
# Register the plugin
#
#-------------------------------------------------------------------------
from Plugins import register_export

register_export(writeData,_("Export to CD (nautilus)"))
