#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2011       Tim G L Lyons
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

"""
Debugging utilities
"""
import cProfile
import pstats
import sys


#-------------------------------------------------------------------------
#
# Debugging utilities
#
#-------------------------------------------------------------------------
def profile(func, *args, **kwargs):

    prf = cProfile.Profile()
    print("Start")
    r = prf.runcall(func, *args, **kwargs)
    print("Finished")
    print("Loading profile")
    stats = pstats.Stats(prf, stream=sys.stdout)
    print("done")
    stats.strip_dirs()
    stats.sort_stats('time', 'calls')
    stats.print_stats(100)
    stats.print_callers(100)
    return r

def format_exception(tb_type=None, tb_value=None, tb=None):
    """
    Get the usual traceback information, followed by a listing of all the
    local variables in each frame.
    Based on:
    code.activestate.com/recipes/52215-get-more-information-from-tracebacks
    """
    import sys
    import traceback
    if tb_type is None:
        tb_type = sys.exc_type
    if tb_value is None:
        tb_value = sys.exc_value
    if tb is None:
        tb = sys.exc_info()[2]
    retval = traceback.format_exception(tb_type, tb_value, tb) + ["\n"]
    while tb.tb_next:
        tb = tb.tb_next
    stack = []
    f = tb.tb_frame
    while f:
        stack.append(f)
        f = f.f_back
    stack.reverse()
    retval.append("Local variables (most recent frame last):\n")
    for frame in stack:
        retval.append(" Frame %s, File \"%s\", line %s:\n" % (frame.f_code.co_name,
                                                              frame.f_code.co_filename,
                                                              frame.f_lineno))
        for key, value in frame.f_locals.items():
            if key.startswith("__"):
                continue
            #We have to be careful not to cause a new error in our error
            #handler! Calling str() on an unknown object could cause an
            #error we don't want.
            try:
                line = "  %s = %s\n" % (key, str(value))
            except:
                line = "  %s = %s\n" % (key, "<ERROR PRINTING VALUE>")
            retval.append(line)
    return retval
