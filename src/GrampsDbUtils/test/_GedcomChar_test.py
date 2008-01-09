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
    
    def setUp(self):
        gen_chars(self.fil, self.enc)

    def test1a_read_ansi(self):        
        f = open(self.fil)
        ra= G.AnsiReader(f)
        got = ra.readline()
        self.assertEquals(got,self.exp, m(got,self.exp, "AnsiReader"))

    def test1b_read_codec_latin1(self):
        got=codecs.open(self.fil, encoding=self.enc).read()
        self.assertEquals(got,self.exp, m(got,self.exp, "using codec %s" % self.enc))

    def test1c_read_codec_cp1252(self):
        got=codecs.open(self.fil, encoding=self.cp).read()
        self.assertEquals(got,self.exp, m(got,self.exp, "using codec %s" % self.cp))

###
class Test2_ansel(unittest.TestCase):
    """Test original AnselReader (later: ansel codec)"""
    enc = "ansel"
    afil = os.path.join(cdir,enc)
    exp  = a2u
    
    def setUp(self):
        open(self.afil, "wb").write(atest_bytes)

    def test2a_read_ansel(self):
        f = open(self.afil)
        ra = G.AnselReader(f)
        got = ra.readline()
        self.assertEquals(got,self.exp, m(got,self.exp, "AnselReader"))

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
    
    def setUp(self):
        gen_chars(self.ufil, self.enc)
        if not os.path.exists(self.f1byte):
            open(self.f1byte, "wb").write("1")
 
    def test3a_u8_UTF8Reader_NO_BOM_sig(self):
        f=open(self.ufil)
        ra=G.UTF8Reader(f)
        g = ra.readline()
        self.assertEquals(g,self.exp, m(g,self.exp, "orig UTF8Reader"))
        r2 = G.UTF8Reader(open(self.f1byte))
        g = r2.readline()
        self.assertEquals(g,"1", 
            m(g,"1", "read 1-byte file"))
  
    # NB: utf_8 reads data and never expects a BOM-sig
    def test3b_utf8_codec_NO_BOM_sig_as_expected(self):
        g=codecs.open(self.ufil, encoding=self.enc).read()
        self.assertEquals(g,self.exp, m(g,self.exp, "codec utf8"))
        g=codecs.open(self.f1byte, encoding=self.enc).read()
        self.assertEquals(g,"1", m(g,"1", "codec utf8"))
  
    # NB: utf_8_sig reads data even absent a BOM-sig (GOOD!)
    def test3c_utf8_sig_codec_NO_BOM_sig_tolerated_GOOD(self):
        g=codecs.open(self.ufil, encoding=self.enc_sig).read()
        self.assertEquals(g,self.exp, 
            m(g,self.exp, "codec utf_8_sig NO sig input"))
        g=codecs.open(self.f1byte, encoding=self.enc_sig).read()
        self.assertEquals(g,"1", 
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
    
    def setUp(self):
        gen_chars(self.ufil, self.enc_sig)
 
    def test4a_u8_UTF8Reader_WITH_BOM_sig(self):
        f=open(self.ufil)
        ra=G.UTF8Reader(f)
        g = ra.readline()
        self.assertEquals(g,self.exp, m(g,self.exp, "orig UTF8Reader"))
   
    # utf_8 reads an initial BOM-sig as data -- oops, pity
    #  write the test to verify this known codec behavior 
    # ==> Recommend: do not use utf8 as input codec (use utf_8_sig)
    def test4b_utf8_codec_WITH_BOM_sig_reads_as_data_PITY(self):
        g=codecs.open(self.ufil, encoding=self.enc).read()
        e0=u'\ufeff'
        self.assertEquals(g[0], e0, 
            m(g[0],e0, "codec utf8 reads 'BOM'-sig as data" ))
        g = g[1:]
        self.assertEquals(g,self.exp, 
            m(g,self.exp, "codec utf8 reads rest of data ok"))
  
    # utf_8_sig reads and ignores the BOM-sig
    def test4c_utf8_sig_codec_WITH_BOM_sig_as_expected(self):
        g=codecs.open(self.ufil, encoding=self.enc_sig).read()
        self.assertEquals(g,self.exp, 
            m(g,self.exp, "codec utf_8_sig NO sig input"))

###



if __name__ == "__main__":
    unittest.main()

#===eof===
