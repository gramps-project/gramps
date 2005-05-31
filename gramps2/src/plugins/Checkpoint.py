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

"Database Processing/Extract information from names"

#-------------------------------------------------------------------------
#
# python modules
#
#-------------------------------------------------------------------------
import os
import popen2
import locale
import time
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# gnome/gtk
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from QuestionDialog import OkDialog, ErrorDialog
import WriteXML

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
def runTool(database,active_person,callback,parent=None):
    try:
        Checkpoint(database,callback,parent)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

#-------------------------------------------------------------------------
#
# Checkpoint
#
#-------------------------------------------------------------------------
class Checkpoint:

    def __init__(self,db,callback,parent):
        self.cb = callback
        self.db = db
        self.parent = parent

        self.parent.status_text(_("Checkpointing database..."))

        # RCS will be a builtin command, since we can handle all
        # configuration on our own. This isn't true for most versioning
        # systems, which usually require external setup, and external
        # communication
        self.rcs()
        
        self.parent.progress.set_fraction(0)
        self.parent.modify_statusbar()

    def timestamp(self):
        format = locale.nl_langinfo(locale.D_T_FMT)
        return unicode(time.strftime(format,time.localtime(time.time())))

    def rcs(self):

        (archive_base,ext) = os.path.splitext(self.db.get_save_path())

        archive = archive_base + ",v"
        if not os.path.exists(archive):
            proc = popen2.Popen3('rcs -i -U -q -t-"GRAMPS database" %s' % archive,True)
            proc.tochild.write(comment)
            proc.tochild.close()
            status = proc.wait()
            if status:
                ErrorDialog(_("Checkpoint failed"),
                            "\n".join(proc.childerr.readlines()))
            del proc
            return
        
        xmlwrite = WriteXML.XmlWriter(self.db,self.callback,False,False)
        xmlwrite.write(archive_base)

        comment = self.timestamp()

        proc = popen2.Popen3("ci %s" % archive_base,True)
        proc.tochild.write(comment)
        proc.tochild.close()
        status = proc.wait()
        if status:
            ErrorDialog(_("Checkpoint failed"),
                        "\n".join(proc.childerr.readlines()))
        del proc

    def callback(self,value):
        self.parent.progress.set_fraction(value)
        while(gtk.events_pending()):
            gtk.main_iteration()
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from PluginMgr import register_tool

register_tool(
    runTool,
    _("Checkpoint the database"),
    category=_("Database Processing"),
    description=_("Store a snapshot of the current database into "
                  "a revision control system"))
