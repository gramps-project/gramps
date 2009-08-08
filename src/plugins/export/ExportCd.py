#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2008  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Contributions 2009 by    Brad Crittenden <brad [AT] bradcrittenden.net>
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
#
# $Id$
#

"Export to CD (nautilus)."

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import os
import sys
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
import Errors

#This is a GNOME only plugin
_gnome_session = os.getenv('GNOME_DESKTOP_SESSION_ID')
if not _gnome_session:
    raise Errors.UnavailableError(
        _("WriteCD is a GNOME plugin and you are not running GNOME"))
        
try:
    import gnome
except ImportError:
    raise Errors.UnavailableError(
        _("Cannot be loaded because python bindings "
          "for GNOME are not installed"))

try:
    from gnomevfs import (URI, create, OPEN_WRITE, make_directory, 
                          FileExistsError)
except:
    from gnome.vfs import (URI, create, OPEN_WRITE, make_directory, 
                           FileExistsError)
    
#This plugin only works if the 'burn://' scheme is supported.
try:
    uri = URI('burn:///test.txt')
except TypeError:
    raise Errors.UnavailableError(
        _("Cannot be loaded because the 'burn://' scheme "
          "is not supported."))

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from ExportXml import XmlWriter
from Utils import media_path_full
from QuestionDialog import ErrorDialog, MissingMediaDialog
from gen.plug import PluginManager, ExportPlugin

_title_string = _("Export to CD")

#-------------------------------------------------------------------------
#
# writeData
#
#-------------------------------------------------------------------------
def writeData(database, filename, option_box=None, callback=None):
    writer = PackageWriter(database, filename, callback)
    return writer.export()
    
#-------------------------------------------------------------------------
#
# PackageWriter
#
#-------------------------------------------------------------------------
class PackageWriter(object):

    def __init__(self, database, filename="", cl=0, callback=None):
        self.db = database
        self.cl = cl
        self.filename = filename
        self.callback = callback

    def export(self):
        if self.cl:
            return self.cl_run()
        else:
            return self.gui_run()

    def cl_run(self):
        base = os.path.basename(self.filename)

        try:
            uri = URI('burn:///%s' % base)
            make_directory(uri, OPEN_WRITE)
        except FileExistsError, msg:
            ErrorDialog(_("CD export preparation failed"), 
                                       "1 %s " % str(msg))
            return False
        except:
            uri_name = "burn:///" + base
            ErrorDialog("CD export preparation failed", 
                                       'Could not create %s' % uri_name)
            return False

        for obj_id in self.db.get_media_object_handles():
            obj = self.db.get_object_from_handle(obj_id)
            oldfile = media_path_full(self.db, obj.get_path())
            root = os.path.basename(oldfile)
            if os.path.isfile(oldfile):
                self.copy_file(oldfile, 'burn:///%s/%s' % (base, root))
            else:
                print "Warning: media file %s was not found, " % root, \
                    "so it was ignored."
            
        # Write XML now
        g = create('burn:///%s/data.gramps' % base, OPEN_WRITE )
        gfile = XmlWriter(self.db, None, 2)
        gfile.write_handle(g)
        g.close()
        return True

    def gui_run(self):
        missmedia_action = 0

        base = os.path.basename(self.filename)

        try:
            uri = URI('burn:///%s' % base)
            make_directory(uri, OPEN_WRITE)
        except FileExistsError:
            ErrorDialog(_("CD export preparation failed"), 
                                       "File already exists")
            return False
        except:
            uri_name = "burn:///" + base
            ErrorDialog(_("CD export preparation failed"), 
                                       _('Could not create %s') % uri_name)
            return False

        try:
            uri = URI('burn:///%s/.thumb' % base)
            make_directory(uri, OPEN_WRITE)
        except FileExistsError, msg:
            ErrorDialog("CD export preparation failed", 
                                       "4 %s " % str(msg))
            return False
        except:
            uri_name = "burn:///" + base + "/.thumb"
            ErrorDialog(_("CD export preparation failed"), 
                                       _('Could not create %s') % uri_name)
            return False

        #--------------------------------------------------------
        def remove_clicked():
            # File is lost => remove all references and the object itself
            for p_id in self.db.iter_family_handles():
                p = self.db.get_family_from_handle(p_id)
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference_handle() == self.object_handle:
                        nl.remove(o) 
                p.set_media_list(nl)
                self.db.commit_family(p, None)
                
            for key in self.db.iter_person_handles():
                p = self.db.get_person_from_handle(key)
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference_handle() == self.object_handle:
                        nl.remove(o) 
                p.set_media_list(nl)
                self.db.commit_person(p, None)
            for key in self.db.get_source_handles():
                p = self.db.get_source_from_handle(key)
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference_handle() == self.object_handle:
                        nl.remove(o) 
                p.set_media_list(nl)
                self.db.commit_source(p, None)
            for key in self.db.get_place_handles():
                p = self.db.get_place_from_handle(key)
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference_handle() == self.object_handle:
                        nl.remove(o) 
                p.set_media_list(nl)
                self.db.commit_place(p, None)
            for key in self.db.get_event_handles():
                p = self.db.get_event_from_handle(key)
                nl = p.get_media_list()
                for o in nl:
                    if o.get_reference_handle() == self.object_handle:
                        nl.remove(o) 
                p.set_media_list(nl)
                self.db.commit_event(p, None)
            self.db.remove_object(self.object_handle, None) 
    
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
                    self.copy_file(newfile, 'burn:///%s/%s' % (base, obase))
                    
            fs_top = gtk.FileChooserDialog("%s - GRAMPS" % _("Select file"),
                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                 gtk.STOCK_OK, gtk.RESPONSE_OK)
                        )
                        
            response = fs_top.run()
            if response == gtk.RESPONSE_OK:
                fs_ok_clicked(fs_top)
            elif response == gtk.RESPONSE_CANCEL:
                fs_close_window(fs_top)                    

            fs_top.destroy()

        #----------------------------------------------------------

        # Write media files first, since the database may be modified 
        # during the process (i.e. when removing object)

        for obj_id in self.db.get_media_object_handles():
            obj = self.db.get_object_from_handle(obj_id)
            oldfile = media_path_full(self.db, obj.get_path())
            root = os.path.basename(oldfile)
            if os.path.isfile(oldfile):
                self.copy_file(oldfile, 'burn:///%s/%s' % (base, root))
            else:
                # File is lost => ask what to do
                self.object_handle = obj.get_handle()
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
        uri = 'burn:///%s/data.gramps' % base
        uri = uri.encode('utf8')
        g = create(uri, OPEN_WRITE)
        gfile = XmlWriter(self.db, self.callback, 2)
        gfile.write_handle(g)
        g.close()
        os.system("nautilus --no-desktop burn:///")
        return True

    def copy_file(self, src, dest):
        original = open(src, "r")
        destobj = URI(dest)
        target = create(destobj, OPEN_WRITE)
        done = 0
        while 1:
            buf = original.read(2048)
            if buf == '':
                break
            else:
                target.write(buf)
        target.close()
        original.close()

#-------------------------------------------------------------------------
#
# Register the plugin
#
#-------------------------------------------------------------------------
_description = _('Exporting to CD copies all your data and media object files '
                 'to the CD Creator. You may later burn the CD with this data, '
                 'and that copy will be completely portable across different '
                 'machines and binary architectures.')

pmgr = PluginManager.get_instance()
plugin = ExportPlugin(name            = _('_Export to CD (portable XML)'), 
                      description     = _description,
                      export_function = writeData,
                      extension       = "burn",
                      config          = None )
pmgr.register_plugin(plugin)
