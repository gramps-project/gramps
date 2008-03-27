""" unittest for grampstype """

import unittest as U

from test.test_util import msg
from gen.lib.grampstype import GrampsType, _init_map

# some simple map items to test with
vals = "zz ab cd ef".split()
keys = range(len(vals))
MAP = [ (k,v*2,v) for (k,v) in zip(keys, vals) ]

class GT0(GrampsType):
    _DEFAULT  = 1 # just avoiding the pre-coded 0
    _CUSTOM   = 3 # just avoiding the pre-coded 0
    _DATAMAP = MAP

class Test1(U.TestCase):

    # some basic tests
    def test1a(s):
        s.gt=GT0()
        s.assertTrue(isinstance(s.gt, GrampsType))
        # spot-check that MAPs get built
        e= len(keys)
        g= len(s.gt._E2IMAP)
        s.assertEquals(g,e, msg(g,e, "expected length of E2IMAP"))

    # init sets values for int, str, tuple 
    # (we ignore instance here -- maybe SB tested, too?)
    # this test depends on having _DEFAULT=1, _CUSTOM=3
    # NB: tuple tests w/ lengths < 2 fail before release 10403
    def test1b(s):
        for i,v,u in ( 
                (None, 1,u''),      # all DEFAULT
                (0, 0,u''), 
                (1, 1,u''), 
                ('efef', 3,'efef'), # matches CUSTOM
                ('zzzz', 0,u''),
                (u'x',   3,u'x'),   # nomatch gives CUSTOM   
                ('',     3,''),     # nomatch gives CUSTOM   
                ((0,'zero'), 0,'zero'), # normal behavior
                ((2,),       2,u''),    # DEFAULT-string, just like int 
                ((),         1,u''),    # DEFAULT-pair      
                ):
            s.gt = GT0(i)
            g= s.gt.val
            s.assertEquals(g,v, 
                msg(g,v, "initialization val from '%s'" % `i`))
            g= s.gt.string
            s.assertEquals(g,u, 
                msg(g,u, "initialization string from '%s'" % `i`))

if __name__ == "__main__":
    U.main()

