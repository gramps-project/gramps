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
import exceptions
import logging

log = logging.getLogger(".")

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
import gobject

# setup import path

gobject.threads_init()

sys.path.append(os.path.abspath(os.path.basename(__file__)))

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

try:
    signal.signal(signal.SIGCHLD, signal.SIG_DFL)
except:
    pass

args = sys.argv

def setup_logging():
    """Setup basic logging support."""

    import logging
    from GrampsLogger import RotateHandler, GtkHandler

    # Setup a formatter
    form = logging.Formatter(fmt="%(relativeCreated)d: %(levelname)s: %(filename)s: line %(lineno)d: %(message)s")
    
    # Create the log handlers
    rh = RotateHandler(capacity=20)
    rh.setFormatter(form)

    # Only error and critical log records should
    # trigger the GUI handler.
    gtkh = GtkHandler(rotate_handler=rh)
    gtkh.setFormatter(form)
    gtkh.setLevel(logging.ERROR)
    
    stderrh = logging.StreamHandler(sys.stderr)
    stderrh.setFormatter(form)
    stderrh.setLevel(logging.DEBUG)

    # Setup the base level logger, this one gets
    # everything.
    l = logging.getLogger()
    l.setLevel(logging.DEBUG)
    l.addHandler(rh)
    l.addHandler(gtkh)
    l.addHandler(stderrh)

    # put a hook on to catch any completly unhandled exceptions.
    def exc_hook(type, value, tb):
        if type == KeyboardInterrupt:
            # Ctrl-C is not a bug.
            return
        import traceback
        log.error("Unhandled exception\n" +
                  "".join(traceback.format_exception(type, value, tb)))
      
    sys.excepthook = exc_hook
    
def run():

    setup_logging()
    
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
        log.error("Gramps failed to start.", exc_info=True)

gobject.timeout_add(100, run, priority=100)
gtk.main()
