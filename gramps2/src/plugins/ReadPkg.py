#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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

# Written by Alex Roitman, largely based on ReadNative.py by Don Allingham 

"Import from Gramps package"

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import os
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GNOME/GTK+ modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
import ReadXML
from QuestionDialog import ErrorDialog
import TarFile

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def impData(database, name,cb=None,cl=0):
    # Create tempdir, if it does not exist, then check for writability
    tmpdir_path = os.path.expanduser("~/.gramps/tmp" )
    if not os.path.isdir(tmpdir_path):
        try:
            os.mkdir(tmpdir_path,0700)
        except:
            ErrorDialog( _("Could not create temporary directory %s") % 
                            tmpdir_path )
            return
    elif not os.access(tmpdir_path,os.W_OK):
        ErrorDialog( _("Temporary directory %s is not writable") % tmpdir_path )
        return
    else:    # tempdir exists and writable -- clean it up if not empty
        files = os.listdir(tmpdir_path) ;
        for filename in files:
            os.remove( os.path.join(tmpdir_path,filename) )

    try:
        t = TarFile.ReadTarFile(name,tmpdir_path)
        t.extract()
        t.close()
    except:
        ErrorDialog(_("Error extracting into %s") % tmpdir_path )
        return

    dbname = os.path.join(tmpdir_path,const.xmlFile)  

    try:
        ReadXML.importData(database,dbname,cb)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

    # Clean up tempdir after ourselves
    files = os.listdir(tmpdir_path) 
    for filename in files:
        os.remove(os.path.join(tmpdir_path,filename))

    os.rmdir(tmpdir_path)

#------------------------------------------------------------------------
#
# Register with the plugin system
#
#------------------------------------------------------------------------
_mime_type = 'application/x-gramps-package'
_filter = gtk.FileFilter()
_filter.set_name(_('GRAMPS packages'))
_filter.add_mime_type(_mime_type)
_format_name = _('GRAMPS package')

from PluginMgr import register_import
register_import(impData,_filter,_mime_type,0,_format_name)
