#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Benny Malengier
# Copyright (C) 2009-2010  Stephen George
# Copyright (C) 2010       Doug Blank <doug.blank@gmail.com>
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
import const
import signal
import gettext
_ = gettext.gettext
import locale
import logging

LOG = logging.getLogger(".")

from subprocess import Popen, PIPE

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.mime import mime_type_is_defined
import TransUtils
import constfunc
#-------------------------------------------------------------------------
#
# Load internationalization setup
#
#-------------------------------------------------------------------------

#the order in which bindtextdomain on gettext and on locale is called
#appears important, so we refrain from doing first all gettext.
#
#TransUtils.setup_gettext()
gettext.bindtextdomain(TransUtils.LOCALEDOMAIN, TransUtils.LOCALEDIR)
try:
    locale.setlocale(locale.LC_ALL,'C')
    locale.setlocale(locale.LC_ALL,'')
except locale.Error:
    pass
except ValueError:
    pass

gettext.textdomain(TransUtils.LOCALEDOMAIN)
gettext.install(TransUtils.LOCALEDOMAIN, localedir=None, unicode=1) #None is sys default locale

if not constfunc.win():
    try:
        locale.bindtextdomain(TransUtils.LOCALEDOMAIN, TransUtils.LOCALEDIR)
        #locale.textdomain(TransUtils.LOCALEDOMAIN)
    except locale.Error:
        print 'No translation in some gtk.Builder strings, '
else:
    TransUtils.setup_windows_gettext()

LOG.debug('Using locale:', locale.getlocale())


#-------------------------------------------------------------------------
#
# Minimum version check
#
#-------------------------------------------------------------------------

MIN_PYTHON_VERSION = (2, 6, 0, '', 0)
if not sys.version_info >= MIN_PYTHON_VERSION :
    print (_("Your Python version does not meet the "
             "requirements. At least python %d.%d.%d is needed to"
             " start Gramps.\n\n"
             "Gramps will terminate now.") % (
            MIN_PYTHON_VERSION[0], 
            MIN_PYTHON_VERSION[1],
            MIN_PYTHON_VERSION[2]))
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

    # Setup a formatter
    form = logging.Formatter(fmt="%(relativeCreated)d: %(levelname)s: %(filename)s: line %(lineno)d: %(message)s")
    
    # Create the log handlers
    stderrh = logging.StreamHandler(sys.stderr)
    stderrh.setFormatter(form)
    stderrh.setLevel(logging.DEBUG)

    # Setup the base level logger, this one gets
    # everything.
    l = logging.getLogger()
    l.setLevel(logging.WARNING)
    l.addHandler(stderrh)

    # put a hook on to catch any completely unhandled exceptions.
    def exc_hook(type, value, tb):
        if type == KeyboardInterrupt:
            # Ctrl-C is not a bug.
            return
        if type == IOError:
            # strange Windows logging error on close
            return
        import traceback
        LOG.error("Unhandled exception\n" +
                  "".join(traceback.format_exception(type, value, tb)))

    sys.excepthook = exc_hook
    
def build_user_paths():
    """ check/make user-dirs on each Gramps session"""
    for path in const.USER_DIRLIST:
        if os.path.islink(path):
            pass # ok
        elif not os.path.isdir(path):
            os.mkdir(path)

def show_settings():
    """
    Shows settings of all of the major components.
    """
    py_str = '%d.%d.%d' % sys.version_info[:3]
    try:
        import gtk
        try:
            gtkver_str = '%d.%d.%d' % gtk.gtk_version 
        except : # any failure to 'get' the version
            gtkver_str = 'unknown version'
        try:
            pygtkver_str = '%d.%d.%d' % gtk.pygtk_version
        except :# any failure to 'get' the version
            pygtkver_str = 'unknown version'
    except ImportError:
        gtkver_str = 'not found'
        pygtkver_str = 'not found'
    #exept TypeError: To handle back formatting on version split

    try:
        import gobject
        try:
            gobjectver_str = '%d.%d.%d' % gobject.pygobject_version
        except :# any failure to 'get' the version
            gobjectver_str = 'unknown version'

    except ImportError:
        gobjectver_str = 'not found'

    try:
        import cairo
        try:
            cairover_str = '%d.%d.%d' % cairo.version_info 
        except :# any failure to 'get' the version
            cairover_str = 'unknown version'

    except ImportError:
        cairover_str = 'not found'

    try:
        import pyexiv2
        try:
            pyexiv2_str = '%d.%d.%d' % pyexiv2.version_info 
        except :# any failure to 'get' the version
            pyexiv2_str = 'unknown version'

    except ImportError:
        pyexiv2_str = 'not found'

    import config
    usebsddb3 = config.get('preferences.use-bsddb3')
    try:
        if usebsddb3:
            import bsddb3 as bsddb
        else:
            import bsddb
        bsddb_str = bsddb.__version__
        bsddb_db_str = str(bsddb.db.version())
    except:
        bsddb_str = 'not found'
        bsddb_db_str = 'not found'

    try: 
        import const
        gramps_str = const.VERSION
    except:
        gramps_str = 'not found'

    if hasattr(os, "uname"):
        operating_system = os.uname()[0]
        kernel = os.uname()[2]
    else:
        operating_system = sys.platform
        kernel = None

    lang_str = os.environ.get('LANG','not set')
    language_str = os.environ.get('LANGUAGE','not set')
    grampsi18n_str = os.environ.get('GRAMPSI18N','not set')
    grampsdir_str = os.environ.get('GRAMPSDIR','not set')

    try:
        dotversion_str = Popen(['dot', '-V'], stderr=PIPE).communicate(input=None)[1]
        if dotversion_str:
            dotversion_str = dotversion_str.replace('\n','')
    except:
        dotversion_str = 'Graphviz not in system PATH'

    try:
        if constfunc.win():
            gsversion_str = Popen(['gswin32c', '--version'], stdout=PIPE).communicate(input=None)[0]
        else:
            gsversion_str = Popen(['gs', '--version'], stdout=PIPE).communicate(input=None)[0]
        if gsversion_str:
            gsversion_str = gsversion_str.replace('\n', '')
    except:
        gsversion_str = 'Ghostcript not in system PATH'

    os_path = os.environ.get('PATH','not set')
    os_path = os_path.split(os.pathsep)
    
    print "Gramps Settings:"
    print "----------------"
    print ' python    : %s' % py_str
    print ' gramps    : %s' % gramps_str
    print ' gtk++     : %s' % gtkver_str
    print ' pygtk     : %s' % pygtkver_str
    print ' gobject   : %s' % gobjectver_str
    if usebsddb3:
        print ' Using bsddb3'
    else:
        print ' Not using bsddb3'
    print ' bsddb     : %s' % bsddb_str
    print ' bsddb.db  : %s' % bsddb_db_str
    print ' cairo     : %s' % cairover_str
    print ' pyexiv2   : %s' % pyexiv2_str
    print ' o.s.      : %s' % operating_system
    if kernel:
        print ' kernel    : %s' % kernel
    print
    print "Environment settings:"
    print "---------------------"
    print ' LANG      : %s' % lang_str
    print ' LANGUAGE  : %s' % language_str
    print ' GRAMPSI18N: %s' % grampsi18n_str
    print ' GRAMPSDIR : %s' % grampsdir_str
    print ' PYTHONPATH:'
    for folder in sys.path:
        print "   ", folder
    print
    print "Non-python dependencies:"
    print "------------------------"
    print ' Graphviz  : %s' % dotversion_str
    print ' Ghostscr. : %s' % gsversion_str
    print
    print "System PATH env variable:"
    print "-------------------------"
    for folder in os_path:
        print "    ", folder
    print

def run():
    error = []
    
    setup_logging()
    
    try:
        build_user_paths()   
    except OSError, msg:
        error += [(_("Configuration error"), str(msg))]
        return error
    except msg:
        LOG.error("Error reading configuration.", exc_info=True)
        return [(_("Error reading configuration"), str(msg))]
        
    if not mime_type_is_defined(const.APP_GRAMPS):
        error += [(_("Configuration error"), 
                    _("A definition for the MIME-type %s could not "
                      "be found \n\n Possibly the installation of Gramps "
                      "was incomplete. Make sure the MIME-types "
                      "of Gramps are properly installed.")
                    % const.APP_GRAMPS)]
    
    #we start with parsing the arguments to determine if we have a cli or a
    # gui session

    if "-v" in sys.argv or "--version" in sys.argv:
        show_settings()
        return error

    from cli.argparser import ArgParser
    argpars = ArgParser(sys.argv)
    
    if argpars.need_gui():
        #A GUI is needed, set it up
        if "--qml" in sys.argv:
            from guiQML.grampsqml import startqml
            startqml(error, argpars)
        else:
            from gui.grampsgui import startgtkloop
            startgtkloop(error, argpars)
    else:
        #CLI use of GRAMPS
        argpars.print_help()
        argpars.print_usage()
        from cli.grampscli import startcli
        startcli(error, argpars)

errors = run()
if errors and isinstance(errors, list):
    for error in errors:
        print error[0], error[1]
