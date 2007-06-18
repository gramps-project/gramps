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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

# Written by Richard Taylor

"""
Testing framework for performing a variety of unttests for GRAMPS.
"""

import logging
 
import os
import sys
import unittest
from optparse import OptionParser

sys.path.append('../src')

def make_parser():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-v", "--verbosity", type="int", dest="verbose_level", default=0,
                      help="Level of verboseness")  
    parser.add_option("-p", "--performance", action="store_true", dest="performance", default=False,
                      help="Run the performance tests.")  
    return parser


def getTestSuites():
    # Sorry about this line, but it is the easiest way of doing it.
    # It just walks the filetree from '.' downwards and returns
    # a tuple per directory of (dirpatch,filelist) if the directory
    # contains any test files.
    
    paths = [(f[0],f[2]) for f in os.walk('.') \
             if len ([i for i in f[2] \
                      if i[-8:] == "_Test.py"]) ]

    for (dir,test_modules) in paths:
        sys.path.append(dir)

        test_suites = []
        perf_suites = []
        for module in test_modules:
            if module[-8:] != "_Test.py":
                break
            mod = __import__(module[:-3])
            test_suites.append(mod.testSuite())
            try:
                perf_suites.append(mod.perfSuite())
            except:
                pass

    return (test_suites,perf_suites)

def allTheTests():
    return unittest.TestSuite(getTestSuites()[0])

def perfTests():
    return unittest.TestSuite(getTestSuites()[1])
    
if __name__ == '__main__':

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))

    logger = logging.getLogger('Gramps')
    logger.addHandler(console)
    
    (options,args) = make_parser().parse_args()

    if options.verbose_level == 1:
        logger.setLevel(logging.INFO)
        console.setLevel(logging.INFO)
    elif options.verbose_level == 2:
        logger.setLevel(logging.DEBUG)
        console.setLevel(logging.DEBUG)
    elif options.verbose_level == 3:
        logger.setLevel(logging.NOTSET)
        console.setLevel(logging.NOTSET)
    elif options.verbose_level >= 4:
        logger.setLevel(logging.NOTSET)
        console.setLevel(logging.NOTSET)
        os.environ['GRAMPS_SIGNAL'] = "1"
    else:
        logger.setLevel(logging.ERROR)
        console.setLevel(logging.ERROR)


    if options.performance:
        unittest.TextTestRunner(verbosity=options.verbose_level).run(perfTests())
    else:
        unittest.TextTestRunner(verbosity=options.verbose_level).run(allTheTests())
