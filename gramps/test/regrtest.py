#! /usr/bin/env python
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# test/regrtest.py
# Original: RunAllTests.py Written by Richard Taylor
# (jgs: revised for embedded "test" subdirs as regrtest.py )

"""
Testing framework for performing a variety of unttests for Gramps.
"""

# TODO: review whether logging is really useful for unittest
#  it does seem to work .. try -v5
import logging

import os
import sys
import unittest
from optparse import OptionParser

from .test import test_util as tu

gramps_root = tu.path_append_parent()


def make_parser():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option(
        "-v",
        "--verbosity",
        type="int",
        dest="verbose_level",
        default=0,
        help="Level of verboseness",
    )
    parser.add_option(
        "-p",
        "--performance",
        action="store_true",
        dest="performance",
        default=False,
        help="Run the performance tests.",
    )
    return parser


def getTestSuites(loc=gramps_root):
    # in a developer's checkout, it is worth filtering-out .git
    #  and we only need to look inside test subdirs
    #   (this might change)
    # this is not so performance critical that we can't afford
    # a couple of function calls to make it readable
    # TODO: handle parts of a module (see unittest.py)

    ldr = unittest.defaultTestLoader

    test_dirname = "test"
    test_suffix = "_test.py"

    def test_mod(p, ds):
        """test for path p=test dir; removes a dir '.git' in ds"""
        if ".git" in ds:
            ds.remove(".git")
        return os.path.basename(p) == test_dirname

    def match_mod(fs):
        """test for any test modules; deletes all non-tests"""
        # NB: do not delete fs elements within a "for f in fs"
        dels = [f for f in fs if not f.endswith(test_suffix)]
        for f in dels:
            fs.remove(f)
        return len(fs) > 0

    test_suites = []
    perf_suites = []
    # note that test_mod and match_mod modify passed-in lists
    paths = [
        (path, files)
        for path, dirs, files in os.walk(loc)
        if test_mod(path, dirs) and match_mod(files)
    ]

    ## NO -- see explanation below
    ##  oldpath = list(sys.path)
    for dir, test_modules in paths:
        sys.path.append(dir)

        for module in test_modules:
            if not module.endswith(test_suffix):
                raise ValueError
            mod = __import__(module[: -len(".py")])
            if getattr(mod, "suite", None):
                test_suites.append(mod.suite())
            else:
                test_suites.append(ldr.loadTestsFromModule(mod))
            try:
                perf_suites.append(mod.perfSuite())
            except:
                pass
        # NO: was: remove temporary paths added
        # this seems like it should be reasonable,
        # but it causes failure in _GrampsDbWRFactories_test.py
        #  (I suspect it is an actual bug in the runner
        #   but the easiest fix is to keep the imports,
        #   which is what other loaders seem to do)
        # ==>  this aspect of test frameworks is *hard*
        ## NO -- do NOT:
        ## remove temporary paths added
        ## sys.path = list(oldpath)
    return (test_suites, perf_suites)


if __name__ == "__main__":

    def logging_init():
        global logger
        global console
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(
            logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
        )
        logger = logging.getLogger("Gramps")
        logger.addHandler(console)
        return console, logger

    def logging_adjust(verbose_level):
        if verbose_level == 1:
            logger.setLevel(logging.INFO)
            console.setLevel(logging.INFO)
        elif verbose_level == 2:
            logger.setLevel(logging.DEBUG)
            console.setLevel(logging.DEBUG)
        elif verbose_level == 3:
            logger.setLevel(logging.NOTSET)
            console.setLevel(logging.NOTSET)
        elif verbose_level >= 4:
            logger.setLevel(logging.NOTSET)
            console.setLevel(logging.NOTSET)
            os.environ["GRAMPS_SIGNAL"] = "1"
        else:
            logger.setLevel(logging.ERROR)
            console.setLevel(logging.ERROR)

    console, logger = logging_init()
    options, args = make_parser().parse_args()
    logging_adjust(options.verbose_level)

    # TODO allow multiple subdirs, modules, or testnames
    #  (see unittest.py)
    # hmmm this is starting to look like a unittest.Testprog
    # (maybe with a custom TestLoader)
    if args and os.path.isdir(args[0]):
        loc = args[0].rstrip(os.path.sep)
    else:
        loc = gramps_root

    utests, ptests = getTestSuites(loc)
    if options.performance:
        suite = unittest.TestSuite(ptests)
    else:
        suite = unittest.TestSuite(utests)

    unittest.TextTestRunner(verbosity=options.verbose_level).run(suite)

# ===eof===
