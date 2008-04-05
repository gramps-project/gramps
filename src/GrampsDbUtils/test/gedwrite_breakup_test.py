"""gedwrite_breakup_test tests the breakup function in GedcomWrite"""
import unittest as U

from test.test_util import msg, path_append_parent
path_append_parent();
import _WriteGedcom as WG

class Test1(U.TestCase):
    def test1a_common(s):
        #txt, limit, [split-results]
        L=4
        dat = (
            ##0123456 
            ("a",  L, ["a",]),
            ("abc",  L, ["abc",]),
            ("abcd",  L, ["abcd",]),
            ("abcde",  L, ["abcd","e"]),
            ("1234567",  L, ["1234","567"]),
            ("12345678",  L, ["1234","5678"]),
            ("123456789",  L, ["1234","5678", "9"]),
        )
        for (t,l,r) in dat:
            g = WG.breakup(t,l)
            s.assertEquals(g,r, msg(g,r, "breakup(%r,%d) results" % (t,l)))

    def test1b_spaces(s):
        #txt, limit, [split-results]
        L=4
        dat = (
            ##0123456 
            ("a b ",  L, ["a b ",]),
            (" a b",  L, [" a b",]),
            ("asdf g", L, ["asd", "f g"]),
            ("    z", L, ["    ", "z"]),
            ("     z", L, ["    ", " z"]),
            ("      A", 2, ["  ", "  ", "  ", "A"]),
        )
        for (t,l,r) in dat:
            g = WG.breakup(t,l)
            s.assertEquals(g,r, msg(g,r, "breakup(%r,%d) results" % (t,l)))

    def test1c_unusual(s):
        #just documenting behavior for unlikely input
        #txt, limit, [split-results]
        dat = (
            ##0123456 
            ("",  4, []),
            ("xyz", 1, ["x", "y", "z"]),
        )
        for (t,l,r) in dat:
            g = WG.breakup(t,l)
            s.assertEquals(g,r, msg(g,r, "breakup(%r,%d) results" % (t,l)))
        s.assertRaises(ValueError, WG.breakup, "xy",0)

if __name__ == "__main__":
    U.main()
#===eof===
