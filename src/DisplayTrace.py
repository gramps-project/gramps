#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002  Donald N. Allingham
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
# Standard python modules
#
#-------------------------------------------------------------------------
import cStringIO
import traceback
import sys
import os

#-------------------------------------------------------------------------
#
# GTK/GNOME modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import const
from gettext import gettext as _

_release_files = [
    "/etc/mandrake-release",
    "/etc/redhat-release",
    "/etc/fedora-release",
    "/etc/turbolinux-release",
    "/etc/debian-version",
    "/etc/environment.corel",
    "/etc/debian-release",
    "/etc/SuSE-release",
    "/etc/slackware-release",
    "/etc/slackware-version",
    "/etc/gentoo-release",
    ]

#-------------------------------------------------------------------------
#
# DisplayTrace
#
#-------------------------------------------------------------------------
class DisplayTrace:

    def __init__(self):
        data = sys.exc_info()
        ver = sys.version_info
        
        msg = cStringIO.StringIO()
        msg.write(_('GRAMPS has encountered an internal error.\n'
                    'Please copy the message below and post a bug report\n'
                    'at http://sourceforge.net/projects/gramps or send an\n'
                    'email message to gramps-bugs@lists.sourceforge.net\n\n'))

        msg.write("GRAMPS : %s\n" % const.version)
        if os.environ.has_key('LANG'):
            msg.write("LANG : %s\n" % os.environ['LANG'])
        msg.write("Python : %s.%s.%s %s\n" % (ver[0],ver[1],ver[2],ver[3]))
        msg.write("GTK : %s.%s.%s\n" % gtk.gtk_version)
        msg.write('PyGTK : %d.%d.%d\n' % gtk.pygtk_version)
        for n in _release_files:
            if os.path.isfile(n):
                try:
                    f = open(n)
                    text = f.readline()
                    msg.write("OS : %s\n" % text)
                    f.close()
                    break
                except:
                    pass
        
        traceback.print_exception(data[0],data[1],data[2],None,msg)

        self.glade = gtk.glade.XML(const.pluginsFile,"plugstat","gramps")
        self.top = self.glade.get_widget("plugstat")
        window = self.glade.get_widget("text")
        self.top.set_title("%s - GRAMPS" % _('Internal Error'))

        window.get_buffer().set_text(msg.getvalue())
        print msg.getvalue()
        self.glade.signal_autoconnect({'on_close_clicked':self.close})

    def close(self,obj):
        self.top.destroy()


        
