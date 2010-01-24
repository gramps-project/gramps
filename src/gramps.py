#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009 Benny Malengier
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
_ = gettext.gettext
import logging

LOG = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.mime import mime_type_is_defined
import TransUtils

#-------------------------------------------------------------------------
#
# Load internationalization setup
#
#-------------------------------------------------------------------------
try:
    locale.setlocale(locale.LC_ALL,'C')
    locale.setlocale(locale.LC_ALL,'')
except locale.Error:
    pass
except ValueError:
    pass

LOG.debug('Using locale:', locale.getlocale())
TransUtils.setup_gettext()

#-------------------------------------------------------------------------
#
# Minimum version check
#
#-------------------------------------------------------------------------

MIN_PYTHON_VERSION = (2, 5, 0, '', 0)
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
    from cli.argparser import ArgParser
    argpars = ArgParser(sys.argv)
    
    if argpars.need_gui():
        #A GUI is needed, set it up 
        from gui.grampsgui import startgtkloop
        startgtkloop(error, argpars)
    else:
        #CLI use of GRAMPS
        argpars.print_help()
        from cli.grampscli import startcli
        startcli(error, argpars)

errors = run()
if errors and isinstance(errors, list):
    for error in errors:
        print error[0], error[1]
