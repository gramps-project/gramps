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
    parser.add_option("-p", "--performance", action="store_true", dest="performance", default=False,
                      help="Run the performance tests.")  
    return parser


def getTestSuites():
    
    test_modules = [ i for i in os.listdir('.') if i[-8:] == "_Test.py" ]

    test_suites = []
    perf_suites = []
    for module in test_modules:
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
