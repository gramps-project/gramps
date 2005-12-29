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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
import sys
import os
import locale
import signal
import gettext

#-------------------------------------------------------------------------
#
# pygtk
#
#-------------------------------------------------------------------------
try:
    import pygtk
    pygtk.require('2.0')
except ImportError:
    pass

import gtk.gdk
import gtk
import gtk.glade

#-------------------------------------------------------------------------
#
# Load internationalization setup
#
#-------------------------------------------------------------------------
if os.environ.has_key("GRAMPSI18N"):
    loc = os.environ["GRAMPSI18N"]
else:
    loc = "/usr/share/locale"

try:
    locale.setlocale(locale.LC_ALL,'C')
    locale.setlocale(locale.LC_ALL,'')
except locale.Error:
    pass
except ValueError:
    pass

gettext.bindtextdomain("gramps",loc)
gtk.glade.bindtextdomain("gramps",loc)

try:
    gtk.glade.textdomain("gramps")
except:
    pass

gettext.textdomain("gramps")
gettext.install("gramps",loc,unicode=1)

#-------------------------------------------------------------------------
#
# gramps libraries
#
#-------------------------------------------------------------------------
import gramps_main 
import gobject

signal.signal(signal.SIGCHLD, signal.SIG_DFL)

args = sys.argv

def run():
    try:
        import gnome
        self.program = gnome.program_init('gramps',const.version, 
                                          gnome.libgnome_module_info_get(),
                                          args, const.popt_table)
        
        self.program.set_property('app-libdir',
                                  '%s/lib' % const.prefixdir)
        self.program.set_property('app-datadir',
                                  '%s/share/gramps' % const.prefixdir)
        self.program.set_property('app-sysconfdir',
                                  '%s/etc' % const.prefixdir)
        self.program.set_property('app-prefix', const.prefixdir)
    except:
        pass

    try:
        import StartupDialog
        
        if StartupDialog.need_to_run():
            StartupDialog.StartupDialog(gramps_main.Gramps,args)
        else:
            gramps_main.Gramps(args)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

gobject.timeout_add(100, run, priority=100)
gtk.main()
