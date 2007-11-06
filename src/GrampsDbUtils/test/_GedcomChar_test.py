#!/usr/bin/env python
import unittest
import os, os.path
import codecs
import struct

from test import test_util as tu
m = tu.msg

par = tu.path_append_parent()
here = tu.absdir()

import _GedcomChar as G

cdir = tu.make_subdir("test_data")

# unicode block "latin1 supplement" chars
utest_chars = "".join(map(unichr, range(0xA0,0x100))) + "\n"

# 12 ansel test chars (raw 8-bit bytes, here)
atest_list = range(0xa1,0xa7) + range(0xb1,0xb7) + [0x0a,]
atest_bytes = struct.pack("B"*13, *atest_list)

# unicode mappings of above (http://www.gymel.com/charsets/ANSEL.html)
a2u = u"".join(map(unichr, (
    0x141, 0xd8, 0x110, 0xde, 0xc6, 0x152,
    0x142, 0xf8, 0x111, 0xfe, 0xe6, 0x153,
    0x0a, )))

def gen_chars(filename, encoding):
    """write generic test chars as given file and encoding"""
    if not os.path.exists(filename):
        codecs.open(filename, "wb", encoding).write(utest_chars)
    
class Test1_ansi(unittest.TestCase):
    enc = "latin-1"
    fil = os.path.join(cdir,enc)
    exp  = utest_chars
    
    def setUp(s):
        gen_chars(s.fil, s.enc)

    def test1a_read_ansi(s):        
        f = open(s.fil)
        ra= G.AnsiReader(f)
        got = ra.readline()
        s.assertEquals(got,s.exp, m(got,s.exp, "AnsiReader"))

    def test1b_read_codec_latin1(s):
        got=codecs.open(s.fil, encoding=s.enc).read()
        s.assertEquals(got,s.exp, m(got,s.exp, "using codec %s" % s.enc))

class Test2_ansel(unittest.TestCase):
    enc = "ansel"
    afil = os.path.join(cdir,enc)
    exp  = a2u
    
    def setUp(s):
        open(s.afil, "wb").write(atest_bytes)

    def test2a_read_ansel(s):
        f = open(s.afil)
        ra = G.AnselReader(f)
        got = ra.readline()
        s.assertEquals(got,s.exp, m(got,s.exp, "AnselReader"))
       

if __name__ == "__main__":
    unittest.main()

#===eof===
