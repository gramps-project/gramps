#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2008  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2008       Gary Burton
# Copyright (C) 2008       Robert Cheramy <robert@cheramy.net>
# Copyright (C) 2010       Jakim Friant
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"Export to Gramps package"

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import time
import shutil
import os
import tarfile
from io import StringIO, BytesIO
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".WritePkg")

#-------------------------------------------------------------------------
#
# GNOME/GTK modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gui.plug.export import WriterOptionBox
from gramps.plugins.export.exportxml import XmlWriter
from gramps.gen.utils.file import media_path_full
from gramps.gen.constfunc import win

#-------------------------------------------------------------------------
#
# writeData
#
#-------------------------------------------------------------------------
def writeData(database, filename, user, option_box=None):

# Rename file, if it exists already, with <filename>.bak
# as it it for normal XML export.

    if os.path.isfile(filename):
        try:
            shutil.copyfile(filename, filename + ".bak")
            shutil.copystat(filename, filename + ".bak")
        except:
            pass

    if option_box:
        option_box.parse_options()
        database = option_box.get_filtered_database(database)

    writer = PackageWriter(database, filename, user)
    return writer.export()


def fix_mtime(tarinfo):
    """ this fixes a bug in the python tarfile GNU_FORMAT where if mtime has
    a fractional component, it fails."""
    tarinfo.mtime = int(tarinfo.mtime)
    return tarinfo
#-------------------------------------------------------------------------
#
# PackageWriter
#
#-------------------------------------------------------------------------
class PackageWriter:

    def __init__(self, database, filename, user):
        self.db = database
        self.user = user
        self.filename = filename

    def export(self):
#        missmedia_action = 0
        #--------------------------------------------------------------
        # def remove_clicked():
        #     # File is lost => remove all references and the object itself
        #     for p_id in self.db.iter_family_handles():
        #         p = self.db.get_family_from_handle(p_id)
        #         nl = p.get_media_list()
        #         for o in nl:
        #             if o.get_reference_handle() == m_id:
        #                 nl.remove(o)
        #         p.set_media_list(nl)
        #         self.db.commit_family(p,None)
        #     for key in self.db.iter_person_handles():
        #         p = self.db.get_person_from_handle(key)
        #         nl = p.get_media_list()
        #         for o in nl:
        #             if o.get_reference_handle() == m_id:
        #                 nl.remove(o)
        #         p.set_media_list(nl)
        #         self.db.commit_person(p,None)
        #     for key in self.db.get_source_handles():
        #         p = self.db.get_source_from_handle(key)
        #         nl = p.get_media_list()
        #         for o in nl:
        #             if o.get_reference_handle() == m_id:
        #                 nl.remove(o)
        #         p.set_media_list(nl)
        #         self.db.commit_source(p,None)
        #     for key in self.db.get_place_handles():
        #         p = self.db.get_place_from_handle(key)
        #         nl = p.get_media_list()
        #         for o in nl:
        #             if o.get_reference_handle() == m_id:
        #                 nl.remove(o)
        #         p.set_media_list(nl)
        #         self.db.commit_place(p,None)
        #     for key in self.db.get_event_handles():
        #         p = self.db.get_event_from_handle(key)
        #         nl = p.get_media_list()
        #         for o in nl:
        #             if o.get_reference_handle() == m_id:
        #                 nl.remove(o)
        #         p.set_media_list(nl)
        #         self.db.commit_event(p,None)
        #     self.db.remove_media(m_id,None)

        # def leave_clicked():
        #     # File is lost => do nothing, leave as is
        #     pass

        # def select_clicked():
        #     # File is lost => select a file to replace the lost one
        #     def fs_close_window(obj):
        #         pass

        #     def fs_ok_clicked(obj):
        #         name = fs_top.get_filename()
        #         if os.path.isfile(name):
        #             archive.add(name)

        #     fs_top = gtk.FileChooserDialog("%s - GRAMPS" % _("Select file"),
        #                 buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
        #                          gtk.STOCK_OK, Gtk.ResponseType.OK)
        #                 )
        #     response = fs_top.run()
        #     if response == Gtk.ResponseType.OK:
        #         fs_ok_clicked(fs_top)
        #     elif response == gtk.RESPONSE_CANCEL:
        #         fs_close_window(fs_top)

        #     fs_top.destroy()
        #---------------------------------------------------------------

        try:
            with tarfile.open(self.filename, 'w:gz') as archive:

                # Write media files first, since the database may be modified
                # during the process (i.e. when removing object)
                handles = self.db.get_media_handles(sort_handles=True)
                for indx, m_id in enumerate(handles):
                    self.user.callback(indx * 100 / len(handles))
                    mobject = self.db.get_media_from_handle(m_id)
                    filename = media_path_full(self.db, mobject.get_path())
                    archname = str(mobject.get_path())
                    if os.path.isfile(filename) and os.access(filename,
                                                              os.R_OK):
                        archive.add(filename, archname, filter=fix_mtime)

                # Write XML now
                with BytesIO() as g:
                    gfile = XmlWriter(self.db, self.user, 2)
                    gfile.write_handle(g)
                    tarinfo = tarfile.TarInfo('data.gramps')
                    tarinfo.size = len(g.getvalue())
                    tarinfo.mtime = time.time()
                    if not win():
                        tarinfo.uid = os.getuid()
                        tarinfo.gid = os.getgid()
                    g.seek(0)
                    archive.addfile(tarinfo, g)

                return True
        except (EnvironmentError, OSError) as msg:
            log.warning(str(msg))
            self.user.notify_error(_('Failure writing %s') % self.filename, str(msg))
            return 0
