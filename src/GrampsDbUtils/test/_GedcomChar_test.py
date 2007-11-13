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

###
class Test1_ansi(unittest.TestCase):
    """Test original "ANSI" reader and codecs: latin, cp1252"""
    enc = "latin-1"
    cp = "cp1252"
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

    def test1c_read_codec_cp1252(s):
        got=codecs.open(s.fil, encoding=s.cp).read()
        s.assertEquals(got,s.exp, m(got,s.exp, "using codec %s" % s.cp))

###
class Test2_ansel(unittest.TestCase):
    """Test original AnselReader (later: ansel codec)"""
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

###
class Test3(unittest.TestCase):
    """Test otriginal UTF8Reader and codecs: utf_8, utf_8_sig 
    with no 'BOM' (sig) in input (the common case) 

    out of curiosity, verify behavior reading a 1-byte file
    """
    enc = "utf_8"
    enc_sig = enc + "_sig"
    ufil = os.path.join(cdir, "chars.utf8")
    f1byte = os.path.join(cdir, "1byte")
    exp  = utest_chars
    
    def setUp(s):
        gen_chars(s.ufil, s.enc)
        if not os.path.exists(s.f1byte):
            open(s.f1byte, "wb").write("1")
 
    def test3a_u8_UTF8Reader_NO_BOM_sig(s):
        f=open(s.ufil)
        ra=G.UTF8Reader(f)
        g = ra.readline()
        s.assertEquals(g,s.exp, m(g,s.exp, "orig UTF8Reader"))
        r2 = G.UTF8Reader(open(s.f1byte))
        g = r2.readline()
        s.assertEquals(g,"1", 
            m(g,"1", "read 1-byte file"))
  
    # NB: utf_8 reads data and never expects a BOM-sig
    def test3b_utf8_codec_NO_BOM_sig_as_expected(s):
        g=codecs.open(s.ufil, encoding=s.enc).read()
        s.assertEquals(g,s.exp, m(g,s.exp, "codec utf8"))
        g=codecs.open(s.f1byte, encoding=s.enc).read()
        s.assertEquals(g,"1", m(g,"1", "codec utf8"))
  
    # NB: utf_8_sig reads data even absent a BOM-sig (GOOD!)
    def test3c_utf8_sig_codec_NO_BOM_sig_tolerated_GOOD(s):
        g=codecs.open(s.ufil, encoding=s.enc_sig).read()
        s.assertEquals(g,s.exp, 
            m(g,s.exp, "codec utf_8_sig NO sig input"))
        g=codecs.open(s.f1byte, encoding=s.enc_sig).read()
        s.assertEquals(g,"1", 
            m(g,"1", "codec utf_8_sig NO sig input"))

###
class Test4(unittest.TestCase):
    """Test otriginal UTF8Reader and codecs: utf_8, utf_8_sig
    with 'BOM' (sig) in input (uncommon, [some?] MS Windows only?) 
    """
    enc = "utf_8"
    enc_sig = enc + "_sig"
    ufil = os.path.join(cdir, "chars.utf8_sig")
    exp  = utest_chars
    
    def setUp(s):
        gen_chars(s.ufil, s.enc_sig)
 
    def test4a_u8_UTF8Reader_WITH_BOM_sig(s):
        f=open(s.ufil)
        ra=G.UTF8Reader(f)
        g = ra.readline()
        s.assertEquals(g,s.exp, m(g,s.exp, "orig UTF8Reader"))
   
    # utf_8 reads an initial BOM-sig as data -- oops, pity
    #  write the test to verify this known codec behavior 
    # ==> Recommend: do not use utf8 as input codec (use utf_8_sig)
    def test4b_utf8_codec_WITH_BOM_sig_reads_as_data_PITY(s):
        g=codecs.open(s.ufil, encoding=s.enc).read()
        e0=u'\ufeff'
        s.assertEquals(g[0], e0, 
            m(g[0],e0, "codec utf8 reads 'BOM'-sig as data" ))
        g = g[1:]
        s.assertEquals(g,s.exp, 
            m(g,s.exp, "codec utf8 reads rest of data ok"))
  
    # utf_8_sig reads and ignores the BOM-sig
    def test4c_utf8_sig_codec_WITH_BOM_sig_as_expected(s):
        g=codecs.open(s.ufil, encoding=s.enc_sig).read()
        s.assertEquals(g,s.exp, 
            m(g,s.exp, "codec utf_8_sig NO sig input"))

###



if __name__ == "__main__":
    unittest.main()

#===eof===
