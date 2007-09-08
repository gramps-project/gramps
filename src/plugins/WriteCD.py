#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
import sys
from cStringIO import StringIO
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".WriteCD")

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
import Errors

try:
    import gnome
except ImportError:
    raise Errors.UnavailableError(
        _("Cannot be loaded because python bindings "
          "for GNOME are not installed"))

try:
    from gnomevfs import URI, create, OPEN_WRITE, make_directory, FileExistsError
except:
    from gnome.vfs import URI, create, OPEN_WRITE, make_directory, FileExistsError

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from GrampsDbUtils import XmlWriter
import Mime
import const
import QuestionDialog
import ImgManip
from PluginUtils import register_export

_title_string = _("Export to CD")

#-------------------------------------------------------------------------
#
# writeData
#
#-------------------------------------------------------------------------
def writeData(database,filename,person,option_box=None,callback=None):
    ret = 0
    writer = PackageWriter(database,filename,callback)
    ret = writer.export()
    return ret
    
#-------------------------------------------------------------------------
#
# PackageWriter
#
#-------------------------------------------------------------------------
class PackageWriter:

    def __init__(self,database,filename="",cl=0,callback=None):
        self.db = database
        self.cl = cl
        self.filename = filename
        self.callback = callback

    def export(self):
        if self.cl:
            self.cl_run()
        else:
            self.gui_run()

    def cl_run(self):
        base = os.path.basename(self.filename)

        try:
            uri = URI('burn:///%s' % base)
            make_directory(uri,OPEN_WRITE)
        except FileExistsError, msg:
            QuestionDialog.ErrorDialog(_("CD export preparation failed"),
                                       "1 %s " % str(msg))
            return
        except:
            uri_name = "burn:///" + base
            QuestionDialog.ErrorDialog("CD export preparation failed",
                                       'Could not create %s' % uri_name)
            return

        try:
            uri = URI('burn:///%s/.thumb' % base)
            make_directory(uri,OPEN_WRITE)
        except FileExistsError, msg:
            QuestionDialog.ErrorDialog("CD export preparation failed",
                                       "2 %s " % str(msg))
            return

        for obj_id in self.db.get_media_object_handles():
            obj = self.db.get_object_from_handle(obj_id)
            oldfile = obj.get_path()
            root = os.path.basename(oldfile)
            if os.path.isfile(oldfile):
                self.copy_file(oldfile,'burn:///%s/%s' % (base,root))
                mime_type = obj.get_mime_type()
                if mime_type and mime_type.startswith("image"):
                    self.make_thumbnail(base,root,obj.get_path())
            else:
                print "Warning: media file %s was not found," % root,\
                    "so it was ignored."
            
        # Write XML now
        g = create('burn:///%s/data.gramps' % base,OPEN_WRITE )
        gfile = XmlWriter(self.db,None,2)
        gfile.write_handle(g)
        g.close()

    def gui_run(self):
        missmedia_action = 0

        base = os.path.basename(self.filename)

        try:
            uri = URI('burn:///%s' % base)
            make_directory(uri,OPEN_WRITE)
        except FileExistsError:
            QuestionDialog.ErrorDialog(_("CD export preparation failed"),
                                       "File already exists")
            return
        except:
            uri_name = "burn:///" + base
            QuestionDialog.ErrorDialog(_("CD export preparation failed"),
                                       _('Could not create %s') % uri_name)
            return

        try:
            uri = URI('burn:///%s/.thumb' % base)
            make_directory(uri,OPEN_WRITE)
        except FileExistsError, msg:
            QuestionDialog.ErrorDialog("CD export preparation failed",
                                       "4 %s " % str(msg))
            return
        except:
            uri_name = "burn:///" + base + "/.thumb"
            QuestionDialog.ErrorDialog(_("CD export preparation failed"),
                                       _('Could not create %s') % uri_name)
            return

        #--------------------------------------------------------
        def remove_clicked():
            # File is lost => remove all references and the object itself
            for p_id in self.db.get_family_handles():
                p = self.db.get_family_from_handle(p_id)
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference_handle() == self.object_handle:
                        nl.remove(o) 
                p.set_media_list(nl)
                self.db.commit_family(p,None)
                
            for key in self.db.get_person_handles(sort_handles=False):
                p = self.db.get_person_from_handle(key)
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference_handle() == self.object_handle:
                        nl.remove(o) 
                p.set_media_list(nl)
                self.db.commit_person(p,None)
            for key in self.db.get_source_handles():
                p = self.db.get_source_from_handle(key)
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference_handle() == self.object_handle:
                        nl.remove(o) 
                p.set_media_list(nl)
                self.db.commit_source(p,None)
            for key in self.db.get_place_handles():
                p = self.db.get_place_from_handle(key)
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference_handle() == self.object_handle:
                        nl.remove(o) 
                p.set_media_list(nl)
                self.db.commit_place(p,None)
            for key in self.db.get_event_handles():
                p = self.db.get_event_from_handle(key)
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference_handle() == self.object_handle:
                        nl.remove(o) 
                p.set_media_list(nl)
                self.db.commit_event(p,None)
            self.db.remove_object(self.object_handle,None) 
    
        def leave_clicked():
            # File is lost => do nothing, leave as is
            pass

        def select_clicked():
            # File is lost => select a file to replace the lost one
            def fs_close_window(obj):
                pass

            def fs_ok_clicked(obj):
                newfile = unicode(fs_top.get_filename(),
                                  sys.getfilesystemencoding())
                if os.path.isfile(newfile):
                    self.copy_file(newfile,'burn:///%s/%s' % (base,obase))
                    ntype = Mime.get_type(newfile)
                    if ntype and ntype.startswith("image"):
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

        for obj_id in self.db.get_media_object_handles():
            obj = self.db.get_object_from_handle(obj_id)
            oldfile = obj.get_path()
            root = os.path.basename(oldfile)
            if os.path.isfile(oldfile):
                self.copy_file(oldfile,'burn:///%s/%s' % (base,root))
                mime_type = obj.get_mime_type()
                if mime_type and mime_type.startswith("image"):
                    self.make_thumbnail(base,root,obj.get_path())
            else:
                # File is lost => ask what to do
                self.object_handle = obj.get_handle()
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
        uri = 'burn:///%s/data.gramps' % base
        uri = uri.encode('utf8')
        g = create(uri,OPEN_WRITE)
        gfile = XmlWriter(self.db,self.callback,2)
        gfile.write_handle(g)
        g.close()
        os.system("nautilus --no-desktop burn:///")
        return 1

    def copy_file(self,src,dest):
        original = open(src,"r")
        destobj = URI(dest)
        target = create(destobj,OPEN_WRITE)
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
        data = img.jpg_scale_data(const.THUMBSCALE,const.THUMBSCALE)
        
        uri = URI('burn:///%s/.thumb/%s.jpg' % (dbname,root))
        th = create(uri,OPEN_WRITE)
        th.write(data)
        th.close()

#-------------------------------------------------------------------------
#
# Register the plugin
#
#-------------------------------------------------------------------------
_title = _('Export to CD (p_ortable XML)')
_description = _('Exporting to CD copies all your data and media '
    'object files to the CD Creator. You may later burn the CD '
    'with this data, and that copy will be completely portable '
    'across different machines and binary architectures.')
_config = None
_filename = 'burn'

register_export(writeData,_title,_description,_config,_filename)
