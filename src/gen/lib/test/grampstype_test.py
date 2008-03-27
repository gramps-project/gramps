""" unittest for grampstype """

import unittest as U

from test.test_util import msg
from gen.lib.grampstype import GrampsType, _init_map

# some simple map items to test with
vals = "zz ab cd ef".split()
keys = range(len(vals))
MAP  = [ (k,v*2,v) for (k,v) in zip(keys, vals) ]
BLIST= [1,3]

class GT0(GrampsType):
    _DEFAULT  = 1 # just avoiding the pre-coded 0
    _CUSTOM   = 3 # just avoiding the pre-coded 0
    _DATAMAP = MAP

# NOTE: this type of code might be used in a migration utility
#   to allow conversions or other handling of retired type-values 
# A migration utility might instantiate several of these with
#   varying blacklist-specs
class GT1(GT0):
    _BLACKLIST = BLIST

class GT2(GT1):
    _BLACKLIST=None

class Test1(U.TestCase):

    # some basic tests
    def test1a_basic(s):
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
    def test1b_init_value(s):
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

# test blacklist functionality added to enable fix of bug #1680
class Test2(U.TestCase):
    def test2a_blacklist(s):
        s.gt=GT1()
        # check that MAPs have lengths reduced by blacklist 
        e= len(keys) - len(BLIST) 
        g= len(s.gt._E2IMAP)
        s.assertEquals(g,e, msg(g,e, "expected length of blacklisted MAP"))

        s.ub=GT2()
        # check that these MAPS are now un-blacklisted
        e= len(keys) 
        g= len(s.ub._E2IMAP)
        s.assertEquals(g,e, msg(g,e, "expected length of un-blacklisted MAP"))


if __name__ == "__main__":
    U.main()

