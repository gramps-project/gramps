#!/usr/bin/python -tt

# Instructions for use
# --------------------
# Eventually, this code might use a testing infrastructure (conventions TBD)
# but, at present this is intended for use as a manual operation by placing
# this file (temporarily) in the same dir as the module it tests.
#
# Running 
#   ./test-ansel_utf8.py [-v]
# should report 'OK'
#   the -v option shows individual results for each test function
# ---------------------------------------------------------------------------

# TODO
# ---------------------------------------------------------
# make table of test cases for readability
# ansel U+xxxx UTF8 char-name string (char where appl)
# ---------------------------------------------------------

import ansel_utf8 as A
import unittest

# debugging provision to capture some strings for exernal examination
# note that this debug output is ASCII, by virture of using `` (repr)
OUT=0
if OUT > 0:
    import sys
#  set output levels 1,2,4 (or-ing ok) for string (repr) in tests 1a,1b,2a
#  then manipulate that data with separate tools for additional validation
# tools refs:
#    http://search.cpan.org/~esummers/MARC-Charset-0.98/lib/MARC/Charset.pm
#    http://pypi.python.org/pypi/pymarc
# --- 
# (perl) MARC::Charset
# (python) pymarc omits eszett,euro (patchable); only does ansel-to-utf8 
# shell: echo -e 'utf-8 encoded chars' works well
# ==> NB: when examining unicode characters (rather than hexdump) externally,
# it is absolutely essential to use a good unicode terminal for correct
# display of combining forms (other than precomposed)    
#    (eg: use xterm rather than konsole or gnome-terminal)
# ==> and of course, use a locale with the UTF-8 charset


# test convwenience utility extends python by showing got & expected (like perl)
#  useful at least for the commonly used assertEquals()
# conventions:
#  dup the expected and got parms from the assertEquals and add a message
#  (and an optional prefix to distinguish sub-tests)
# ==> code the assert as assertEquals(got, exp, msg(got,exp,mess,pfx))
def msg(got, expect, msgbase, prefix=""):
    if prefix:
        prefix += ": "
    return "%s%s\n .....got %s\n expected %s" % (prefix, msgbase, `got`, `expect`)


class Test1(unittest.TestCase):
    """ test basic ansel_to_unicode and inversion """

    def test_1a(self):
        """ 1a: map ansel onebyte to unicode and inverse """
        # no combining chars here .. see later test for those
        count = 0
        sans  = ""
        suni  = u""
        for acode in sorted(A._onebyte.keys()):
            count += 1
            sans += acode
            suni += A._onebyte[acode] 
        if OUT & 1:    
            print "test1a: %d codes" % count
            print " ansel:%s" % `sans`
            print " utf-8:%s" % `suni.encode("utf-8")`  # U8 for debugging
            sys.stdout.flush()
        a2u = A.ansel_to_utf8(sans)
        self.assertEquals(a2u,suni, msg(a2u,suni, "map onebyte ansel to unicode"))
        u2a = A.utf8_to_ansel(suni)
        self.assertEquals(u2a,sans, msg(u2a, sans, "invert onebyte to unicode mapping"))

    def test_1b(self):
        """ 1b: map ansel twobyte to unicode and inverse """
        # these are the precomposed combining forms
        count = 0
        sans  = ""
        suni  = u""
        for acode in sorted(A._twobyte.keys()):
            count += 1
            sans += acode
            suni += A._twobyte[acode] 
        if OUT & 2:    
            print "test1b: %d codes" % count
            print " ansel:%s" % `sans`
            print " utf-8:%s" % `suni.encode("utf-8")` # U8
            sys.stdout.flush()
        a2u = A.ansel_to_utf8(sans)
        self.assertEquals(a2u,suni, msg(a2u,suni,"map twobyte ansel to unicode"))
        u2a = A.utf8_to_ansel(suni)
        self.assertEquals(u2a,sans, msg(u2a,sans, "invert twobyte to unicode mapping"))
        
class Test2(unittest.TestCase):
    """ test unicode_to_ansel (basic precomposed forms) and inversion """

    def test_2a(self):
        """ 2a: unicode to ansel and inverse """
        count = 0
        sans  = ""
        suni  = u""
        for ucode in sorted(A._utoa.keys()):
            count += 1
            suni += ucode
            sans += A._utoa[ucode] 
        if OUT & 4:    
            print "test2a: %d codes" % count
            print " utf-8:%s" % `suni.encode("utf-8")` # U8
            print " ansel:%s" % `sans`
            sys.stdout.flush()
        u2a = A.utf8_to_ansel(suni)
        self.assertEquals(u2a,sans, msg(u2a,sans, "map unicode to ansel"))
        a2u = A.ansel_to_utf8(sans)
        self.assertEquals(a2u,suni, msg(a2u,suni, "invert unicode to ansel mapping"))

class Test3(unittest.TestCase):
    """ test pass-through for matches with ansel ascii-subset """

    def test3a(self):
        """ 3a: ansel to unicode for matches with ascii and inverse """
        ascii_ok = "".join(A._use_ASCII)
        ascii_uni =  unicode(ascii_ok)
        a2u = A.ansel_to_utf8(ascii_ok)
        # could match with lengths wrong? can't hurt to test
        la = len(ascii_ok)
        la2u = len(a2u)
        self.assertEquals(la2u, la, msg(la2u, la, "ascii subset ansel to unicode lengths match"))
        self.assertEquals(a2u, ascii_uni, 
            msg(a2u, ascii_uni, "ascii subset ansel to unicode strings match"))
        a2u2a = A.utf8_to_ansel(a2u)
        self.assertEquals(a2u2a, ascii_ok, 
            msg(a2u2a, ascii_ok, "invert ascii subset ansel to unicode"))

    def test3b(self):
        """ 3b: (sample) non-matching ascii control chars map to space """
        for x in [0,1,8,9,11,26,28,127]:
            a2u = A.ansel_to_utf8(chr(x))
            self.assertEquals(a2u, unicode(' '), 
                msg(a2u, unicode(' '), "map disallowed ASCII to unicode space"))
            u2a = A.utf8_to_ansel(unichr(x))
            self.assertEquals(u2a, ' ',
                msg(u2a, ' ', "map unicode to space for disallowed ASCII"))
    
    def test3c(self):
        """ 3c: (sample) no-match ansel to unicode cases """
        for x in [0x80,0x87,0x9F,0xFF]:
            a2u = A.ansel_to_utf8(chr(x))
            self.assertEquals(a2u, u'\ufffd',
                msg(a2u, u'\ufffd', "ansel no-match should return unicode Replacement Char"))

    def test3d(self):
        """ 3d: (sample) no-match unicode to ansel cases """
        for x in [1024,4096, 65535]:
            u2a = A.utf8_to_ansel(unichr(x))
            self.assertEquals(u2a, '?', 
                msg(u2a, '?', "unicode no-match should return question mark"))

class Test4(unittest.TestCase):
    """ test some special cases """

    def test4a(self):
        """ 4a: empty strings should return empty strings """
        self.assertEquals(A.ansel_to_utf8(""), u"", "empty a2u")
        self.assertEquals(A.utf8_to_ansel(u""), "", "empty u2a")

    def test4b_unmapped_combos(self):
        """ 4b: (sample) unmapped (non-precomposed) combinations """
        samples = ( 
            # ansel, unicode, failure-report-message .. see function msg()
            ("b\xE5Ze", u"bZ\u0304e", "b Z+macron e"),
            ( "\xE5Z",   u"Z\u0304", "Z+macron"),
            ("b\xE5Z\xE9Xe", u"bZ\u0304X\u030ce", "b Z+macron X+caron e"),
            ( "\xE5Z\xE9X",   u"Z\u0304X\u030c", "Z+macron X+caron"),
        )
        for a,u,m in samples:
            # ansel to unicode and inverse
            a2u=A.ansel_to_utf8(a)
            self.assertEquals(a2u, u, msg(a2u, u, m, "a2u"))
            a2u2a = A.utf8_to_ansel(a2u)
            self.assertEquals(a2u2a, a, msg(a2u2a, a, m, "a2u2a"))

            # unicode to ansel and inverse
            u2a = A.utf8_to_ansel(u)
            self.assertEquals(u2a, a, msg(u2a, a, m, "u2a"))
            u2a2u = A.ansel_to_utf8(u2a)
            self.assertEquals(u2a2u, u, msg(u2a2u, u, m, "u2a2u"))
        
    def test4c_multiple_combos(self):
        """ 4c: (a2u) ignore multiple combinations (include precomposed) """
        samples = (
            ("b\xF0\xE5Ze", u"bZ\u0304e", "b <cedilla> Z+macron e"),
            ( "\xF0\xE5Z",   u"Z\u0304", "<cedilla> Z+macron"),
            ("\xF0\xE5Z\xE9X", u"Z\u0304X\u030c", "<cedilla> Z+macron X+caron"),
            ("\xE5Z\xF0\xE9X", u"Z\u0304X\u030c", "Z+macron <cedilla> X+caron"),
            ('\xF0\xE5A', u'\u0100', "<cedilla> A+macron"),
            ("\xE5Z\xE5\xF0\xE9X", u"Z\u0304X\u030c", "Z+macron <macron> <cedilla> X+caron"),
        )
        for a,u,m in samples:
            a2u=A.ansel_to_utf8(a)
            self.assertEquals(a2u, u, msg(a2u,u,m, "a2u drop extra <combiners>"))

    def test4d_multiple_combos(self):
        """ 4c: (u2a) ignore multiple combinations (include precomposed) """
        samples = (
            ("b\xE5Ze", u"bZ\u0304\u0327e", "b Z+macron <cedilla> e"),
            ("\xE5Z\xE5A", u"Z\u0304\u0327\u0100", "Z+macron <cedilla> A+macron"),
            ("\xE5A\xE5Z", u"\u0100\u0327\u030cZ\u0304", "A+macron <cedilla> <caron> Z+macron"),
        )
        for a,u,m in samples:
            u2a=A.utf8_to_ansel(u)
            self.assertEquals(u2a, a, msg(u2a,a,m, "u2a drop extra <combiners>"))

class Test99(unittest.TestCase):
    """ test regression cases """
    
    def test_99a(self):
        """ 99a: sanity check on counts """
        n1B= len(A._onebyte)
        n2B= len(A._twobyte)
        na = n1B+n2B
        nu = len(A._utoa)
        self.assertEquals(na, nu, msg(na, nu, "basic counts: a2u=u2a"))
        nac = len(A._acombiners)
        nuc = len(A._ucombiners)
        self.assertEquals(nac, nuc, msg(nac, nuc, "combiner counts: a2u=u2a"))

    def test_99b(self):
        """ 99b: fix incorrect mapping for ansel 0xAE
        
        It used-to-be U+02be but was changed March 2005 to U+02bc
        Note : the other revs per notes make double-wide combining
        char halves into an ambiguous mess -- let's ignore that!
            http://lcweb2.loc.gov/diglib/codetables/45.html
        might as well add validation of other additions, though
        """
        
        # (ansel, uni, msg)
        revs = (
            ('\xAE', u'\u02bc', "modifier right-half ring is now modifier Apostrophe"),
            ('\xC7', u'\xdf',   "added code for eszet"),
            ('\xC8', u'\u20ac', "added code for euro"),
        )
        for a, u, m in revs:
            g = A.ansel_to_utf8(a)
            self.assertEquals(g,u, 
            msg(g, u, m, "spec change"))

if __name__ == '__main__':
    unittest.main()

#===eof===
