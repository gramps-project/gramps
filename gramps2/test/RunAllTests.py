"""Copyright QinetiQ Ltd (2005) - See LICENSE.TXT for licensing information.

"""

import logging
 
import os
import unittest
from optparse import OptionParser

def make_parser():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-v", "--verbosity", type="int", dest="verbose_level", default=0,
                      help="Level of verboseness")  
    return parser


def getTestSuites():
    
    test_modules = [ i for i in os.listdir('.') if i[-8:] == "_Test.py" ]

    test_suites = []
    for module in test_modules:
        mod = __import__(module[:-3])
        test_suites.append(mod.testSuite())

    return test_suites

def allTheTests():
    return unittest.TestSuite(getTestSuites())

if __name__ == '__main__':

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))

    logger = logging.getLogger('Gramps')
    logger.addHandler(console)
    
    (options,args) = make_parser().parse_args()

    if options.verbose_level == 1:
        logger.setLevel(logging.INFO)
    elif options.verbose_level >= 2:
        logger.setLevel(logging.DEBUG)
        os.environ['GRAMPS_SIGNAL'] = "1"
    elif options.verbose_level >= 3:
        logger.setLevel(logging.NOTSET)
    else:
        logger.setLevel(logging.ERROR)
        
    unittest.TextTestRunner(verbosity=options.verbose_level).run(allTheTests())
