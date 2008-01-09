"""unittest support utility module"""

import os
import sys
import traceback
import tempfile
import shutil
import logging


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
    tb =  _caller_context()
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
      If a file, the the dir of the file is used. 
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

# simplified logging
# gramps-independent but gramps-compatible
#
# I don't see any need to inherit from logging.Logger
# (at present, test code needs nothing fancy)
# but that might be considered for future needs
# NB: current code reflects limited expertise on the 
# uses of the logging module
# ---------------------------------------------------------
class TestLogger():
    """this class mainly just encapsulates some globals
    namely lfname, lfh  for a file log name and handle

    provides simplified logging setup for test modules
    that need to setup logging for modules under test
    (just instantiate a TestLogger to avoid error 
     messages about logging handlers not available)

    There is also a simple logfile capability, to allow
    test modules to capture gramps logging output

    Note that existing logging will still occur, possibly
    resulting in console messages and popup dialogs
    """
    def __init__(self, lvl=logging.WARN):
        logging.basicConfig(level=lvl)
        
    def logfile_init(self, lfname):
        """init or re-init a logfile"""
        if getattr(self, "lfh", None):
            logging.getLogger().handlers.remove(self.lfh)
        if os.path.isfile(lfname):
            os.unlink(lfname)
        self.lfh = logging.FileHandler(lfname)
        logging.getLogger().addHandler(self.lfh)
        self.lfname = lfname
    
    def logfile_getlines(self):
        """get current content of logfile as list of lines"""
        txt = []
        if self.lfname and os.path.isfile(self.lfname):
           txt = open(self.lfname).readlines() 
        return txt

#===eof===
