#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
# Python modules
#
#-------------------------------------------------------------------------
import sys
import os
import locale
import const
import signal
import gettext
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

#-------------------------------------------------------------------------
#
# Miscellaneous initialization
#
#-------------------------------------------------------------------------
import gtk
from gtk import glade
import gobject

gobject.threads_init()

#-------------------------------------------------------------------------
#
# Load internationalization setup
#
#-------------------------------------------------------------------------
if os.environ.has_key("GRAMPSI18N"):
    loc = os.environ["GRAMPSI18N"]
elif os.path.exists( os.path.join(const.ROOT_DIR, "lang") ):
    loc = os.path.join(const.ROOT_DIR, "lang")
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
glade.bindtextdomain("gramps",loc)

try:
    glade.textdomain("gramps")
except:
    pass

gettext.textdomain("gramps")
gettext.install("gramps",loc,unicode=1)

#-------------------------------------------------------------------------
#
# Minimum version check
#
#-------------------------------------------------------------------------

MIN_PYTHON_VERSION = (2, 5, 0, '', 0)
if not sys.version_info >= MIN_PYTHON_VERSION :
    print gettext.gettext("Your Python version does not meet the "
                  "requirements. At least python %d.%d.%d is needed to"
                  " start GRAMPS.\n\n"
                  "GRAMPS will terminate now.") % (
                                        MIN_PYTHON_VERSION[0], 
                                        MIN_PYTHON_VERSION[1],
                                        MIN_PYTHON_VERSION[2])
    sys.exit(1)

#-------------------------------------------------------------------------
#
# gramps libraries
#
#-------------------------------------------------------------------------
try:
    signal.signal(signal.SIGCHLD, signal.SIG_DFL)
except:
    pass

args = sys.argv

def setup_logging():
    """Setup basic logging support."""

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
    l.setLevel(logging.WARNING)
    l.addHandler(rh)
    l.addHandler(gtkh)
    l.addHandler(stderrh)

    # put a hook on to catch any completly unhandled exceptions.
    def exc_hook(type, value, tb):
        if type == KeyboardInterrupt:
            # Ctrl-C is not a bug.
            return
        if type == IOError:
            # strange Windows logging error on close
            return
        import traceback
        log.error("Unhandled exception\n" +
                  "".join(traceback.format_exception(type, value, tb)))

    sys.excepthook = exc_hook
    
def run():

    setup_logging()

    try:
        #This is GNOME initialization code that is necessary for use 
        # with the other GNOME libraries. 
        #It only gets called if the user has gnome installed on his/her system.
        #There is *no* requirement for it.
        #If you don't call this, you are not guaranteed that the other GNOME
        #libraries will function properly. I learned this the hard way.
        import gnome
        program = gnome.program_init('gramps',const.VERSION, 
                                     gnome.libgnome_module_info_get(),
                                     args, const.POPT_TABLE)
    
        program.set_property('app-libdir',
                             '%s/lib' % const.PREFIXDIR)
        program.set_property('app-datadir',
                             '%s/share' % const.PREFIXDIR)
        program.set_property('app-sysconfdir',const.SYSCONFDIR)
        program.set_property('app-prefix', const.PREFIXDIR)
    except:
        pass

    try:        
        quit_now = False
        exit_code = 0
        import gramps_main 
        gramps_main.Gramps(args)
        # TODO: check for returns from gramps_main.Gramps.__init__()
        #  that perhaps should have raised an exception to be caught here

    except SystemExit, e:
        quit_now = True
        if e.code:
            exit_code = e.code
            log.error("Gramps terminated with exit code: %d." \
                      % e.code, exc_info=True)
    except OSError, e:
        quit_now = True
        exit_code = e[0] or 1
        try:
            fn = e.filename
        except AttributeError:
            fn = ""
        log.error("Gramps terminated because of OS Error\n" +
            "Error details: %s %s" % (repr(e), fn), exc_info=True)
    except:
        quit_now = True
        exit_code = 1
        log.error("Gramps failed to start.", exc_info=True)

    if quit_now:
        gtk.main_quit()
        sys.exit(exit_code)
        
    return False
        
gobject.timeout_add(100, run, priority=100)
gtk.main()
