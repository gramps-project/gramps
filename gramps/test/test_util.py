#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

# test/test_util.py

"""unittest support utility module"""

import os
import sys
import traceback
import tempfile
import shutil
import logging
import contextlib
from io import TextIOWrapper, BytesIO, StringIO

from gramps.gen.dbstate import DbState
from gramps.gen.user import User
from gramps.cli.grampscli import CLIManager
from gramps.cli.argparser import ArgParser
from gramps.cli.arghandler import ArgHandler
from gramps.gen.const import USER_DIRLIST
from gramps.gen.filters import reload_custom_filters
reload_custom_filters()  # so reports with filter options don't fail

# _caller_context is primarily here to support and document the process
# of determining the test-module's directory.
#
# NB: the traceback 0-element is 'limit'-levels back, or earliest calling
# context if that is less than limit.
#  The -1 element is this very function; -2 is its caller, etc.
# A traceback context tuple is:
#  (file, line, active function, text of the call-line)
def _caller_context():
    """Return context of first caller outside this module"""
    lim = 5  #  1 for this function, plus futrher chain within this module
    st = traceback.extract_stack(limit=lim)
    thisfile = __file__.rstrip("co")  # eg, in ".py[co]
    while st and st[-1][0] == thisfile:
        del(st[-1])
    if not st:
        raise TestError("Unexpected function call chain length!")
    return st[-1]


# NB: tb[0] differs between running 'XYZ_test.py' and './XYZ_test.py'
#     so, always take the abspath.
def _caller_dir():
    """Return directory of caller function (caller outside this module)"""
    tb = _caller_context()
    return os.path.dirname(os.path.abspath(tb[0]))


class TestError(Exception):
    """Exception for use by test modules

    Use this, for example, to distuinguish testing errors.

    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def msg(got, exp, msg, pfx=""):
    """Error-report message formatting utility

    This improves unittest failure messages by showing data values
    Usage:
      assertEqual(got,exp, msg(got,exp,"mess" [,prefix])
    The failure message will show as
      [prefix: ] mess
        .....got:repr(value-of-got)
        expected:repr(value-of-exp)

    """
    if pfx:
        pfx += ": "
    return "%s%s\n .....got:%r\n expected:%r" % (pfx, msg, got, exp)


def absdir(path=None):
    """Return absolute dir of the specified path

    The path parm may be dir or file  or missing.
    If a file, the dir of the file is used.
    If missing, the dir of test-module caller is used

    Common usage is
      here = absdir()
      here = absdir(__file__)
    These 2 return the same result

    """
    if not path:
        path = _caller_dir()
    loc = os.path.abspath(path)
    if os.path.isfile(loc):
        loc = os.path.dirname(loc)
    return loc


def path_append_parent(path=None):
    """Append (if required) the parent of a path to the python system path,
    and return the abspath to the parent as a possible convenience

    The path parm may be a dir or a file or missing.
      If a file, the dir of the file is used.
      If missing the test-module caller's dir is used.
    And then the parent of that dir is appended (if not already present)

    Common usage is
      path_append_parent()
      path_append_parent(__file__)
    These 2 produce the same result

    """
    pdir = os.path.dirname(absdir(path))
    if not pdir in sys.path:
        sys.path.append(pdir)
    return pdir


def make_subdir(dir, parent=None):
    """Make (if required) a subdir to a given parent and return its path

    The parent parm may be dir or file or missing
      If a file, the dir of the file us used
      If missing, the test-module caller's dir is used
    Then the subdir dir in the parent dir is created if not already present

    """
    if not parent:
        parent = _caller_dir()
    sdir = os.path.join(parent,dir)
    if not os.path.exists(sdir):
        os.mkdir(sdir)
    return sdir

def delete_tree(dir):
    """Recursively delete directory and content

    WARNING: this is clearly dangerous
      it will only operate on subdirs of the test module dir or of /tmp

    Test writers may explicitly use shutil.rmtree if really needed
    """

    if not os.path.isdir(dir):
        raise TestError("%r is not a dir" % dir)
    sdir = os.path.abspath(dir)
    here = _caller_dir() + os.path.sep
    tmp = tempfile.gettempdir() + os.path.sep
    if not (sdir.startswith(here) or sdir.startswith(tmp)):
        raise TestError("%r is not a subdir of here (%r) or %r"
            % (dir, here, tmp))
    shutil.rmtree(sdir)

### Support for testing CLI

def new_exit(edit_code=None):
    raise SystemExit()

@contextlib.contextmanager
def capture(stdin, bytesio=False):
    oldout, olderr = sys.stdout, sys.stderr
    oldexit = sys.exit
    if stdin:
        oldin = sys.stdin
        sys.stdin = stdin
    logger = logging.getLogger()
    old_level = logger.getEffectiveLevel()
    logger.setLevel(logging.CRITICAL)
    try:
        output = [BytesIO() if bytesio else StringIO(), StringIO()]
        sys.stdout, sys.stderr = output
        sys.exit = new_exit
        yield output
    except SystemExit:
        pass
    finally:
        logger.setLevel(old_level)
        sys.stdout, sys.stderr = oldout, olderr
        sys.exit = oldexit
        if stdin:
            sys.stdin = oldin
        output[0] = output[0].getvalue()
        output[1] = output[1].getvalue()

class Gramps:
    def __init__(self, user=None, dbstate=None):
        ## Setup:
        from gramps.cli.clidbman import CLIDbManager
        self.dbstate = dbstate or DbState()
        #we need a manager for the CLI session
        self.user = user or User()
        self.climanager = CLIManager(self.dbstate, setloader=True, user=self.user)
        self.clidbmanager = CLIDbManager(self.dbstate)

    def run(self, *args, stdin=None, bytesio=False):
        with capture(stdin, bytesio=bytesio) as output:
            try:
                try:    # make sure we have user directories
                    for path in USER_DIRLIST:
                        if not os.path.isdir(path):
                            os.makedirs(path)
                except OSError as msg:
                    print("Error creating user directories: " + str(msg))
                except:
                    print("Error reading configuration.", exc_info=True)
                #load the plugins
                self.climanager.do_reg_plugins(self.dbstate, uistate=None)
                # handle the arguments
                args = [sys.executable] + list(args)
                argparser = ArgParser(args)
                argparser.need_gui()  # initializes some variables
                if argparser.errors:
                    print(argparser.errors, file=sys.stderr)
                argparser.print_help()
                argparser.print_usage()
                handler = ArgHandler(self.dbstate, argparser, self.climanager)
                # create a manager to manage the database
                handler.handle_args_cli()
                if handler.dbstate.is_open():
                    handler.dbstate.db.close()
            except:
                print("Exception in test:")
                print("-" * 60)
                traceback.print_exc(file=sys.stdout)
                print("-" * 60)

        return output

#===eof===
