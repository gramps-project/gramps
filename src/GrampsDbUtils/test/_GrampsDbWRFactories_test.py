#!/usr/bin/env python
import unittest

from test import test_util as tu
par = tu.path_append_parent()

###
class Test1(unittest.TestCase):
    """Test imports which are buried within functions
    otherwise they may not get timely test coverage
    
    NB: if any test fails, check imports within that module

    """
    def test1a_buried_imports(self):
        import sys
        self.assertTrue(par in sys.path, 
            "par %r has to be in path!" % par)
        ilist = (
            "_WriteXML",
            "_WriteGedcom",
            "_ReadXML",
            "_ReadGedcom",
        )
        for m in ilist:
            try:
                mod = __import__(m)
            except ImportError:
                mod = None
            self.assertTrue(mod, "try import of module %r" % m)

if __name__ == "__main__":
    unittest.main()
#===eof===
