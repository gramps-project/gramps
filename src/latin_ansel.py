# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import cStringIO

ANSEL_ERROR = "ANSEL Error"

_s1 = { 
    0xC3 : { 0xB8 : 0xF8 , 0x98 : 0xD8},
    0xEA : { ord('A') : 0xC5, ord('a') : 0xE5  },
    0xE8 : { ord('A') : 0xC4, ord('E') : 0xCB, ord('I') : 0xCF,	ord('O') : 0xD6,
             ord('U') : 0xDC, ord('a') : 0xE4, ord('e') : 0xEB, ord('i') : 0xEF,
             ord('o') : 0xF6, ord('u') : 0xFC, ord('y') : 0xFF },
    0xE2 : { ord('A') : 0xC1, ord('E') : 0xC9, ord('I') : 0xCD, ord('O') : 0xD3,
             ord('U') : 0xDA, ord('Y') : 0xDD, ord('a') : 0xE1, ord('e') : 0xE9,
             ord('i') : 0xED, ord('o') : 0xF3, ord('u') : 0xFA, ord('y') : 0xFD },
    0xE1 : { ord('A') : 0xC0, ord('E') : 0xC8, ord('I') : 0xCC, ord('O') : 0xD2,
             ord('U') : 0xD9, ord('a') : 0xE0, ord('e') : 0xE8, ord('i') : 0xEC,
             ord('o') : 0xF2, ord('u') : 0xF9 },
    0xE4 : { ord('A') : 0xC3, ord('N') : 0xD1, ord('O') : 0xD5, ord('a') : 0xE3,
             ord('n') : 0xF1, ord('o') : 0xF5 },
    0xE3 : { ord('A') : 0xC2, ord('E') : 0xCA, ord('I') : 0xCE, ord('O') : 0xD4,
             ord('U') : 0xDB, ord('a') : 0xE3, ord('e') : 0xEA, ord('i') : 0xEE,
             ord('o') : 0xF4, ord('u') : 0xFB },
    0xF0 : { ord('C') : 0xC7, ord('c') : 0xE7 }
}

_t1 = {
    0xC0 : (chr(0xE1), 'A'), 0xC1 : (chr(0xE2), 'A'), 0xC2 : (chr(0xE3), 'A'),
    0xC3 : (chr(0xE4), 'A'), 0xC4 : (chr(0xE8), 'A'), 0xC5 : (chr(0xEA), 'A'),
    0xC7 : (chr(0xF0), 'C'), 0xC8 : (chr(0xE1), 'E'), 0xC9 : (chr(0xE2), 'E'),
    0xCA : (chr(0xE3), 'E'), 0xCB : (chr(0xE8), 'E'), 0xCC : (chr(0xE1), 'I'),
    0xCD : (chr(0xE2), 'I'), 0xCE : (chr(0xE3), 'I'), 0xCF : (chr(0xE8), 'I'),
    0xD1 : (chr(0xE4), 'N'), 0xD2 : (chr(0xE1), 'O'), 0xD3 : (chr(0xE2), 'O'),
    0xD4 : (chr(0xE3), 'O'), 0xD5 : (chr(0xE4), 'O'), 0xD6 : (chr(0xE8), 'O'),
    0xD9 : (chr(0xE1), 'U'), 0xDA : (chr(0xE2), 'U'), 0xDB : (chr(0xE3), 'U'),
    0xDC : (chr(0xE8), 'U'), 0xDD : (chr(0xE2), 'Y'), 0xE0 : (chr(0xE1), 'a'),
    0xE1 : (chr(0xE2), 'a'), 0xE3 : (chr(0xE3), 'a'), 0xE3 : (chr(0xE4), 'a'),
    0xE4 : (chr(0xE8), 'a'), 0xE5 : (chr(0xEA), 'a'), 0xE7 : (chr(0xF0), 'c'),
    0xE8 : (chr(0xE1), 'e'), 0xE9 : (chr(0xE2), 'e'), 0xEA : (chr(0xE3), 'e'),
    0xEB : (chr(0xE8), 'e'), 0xEC : (chr(0xE1), 'i'), 0xED : (chr(0xE2), 'i'),
    0xEE : (chr(0xE3), 'i'), 0xEF : (chr(0xE8), 'i'), 0xF1 : (chr(0xE4), 'n'),
    0xF2 : (chr(0xE1), 'o'), 0xF3 : (chr(0xE2), 'o'), 0xF4 : (chr(0xE3), 'o'),
    0xF5 : (chr(0xE4), 'o'), 0xF6 : (chr(0xE8), 'o'), 0xF9 : (chr(0xE1), 'u'),
    0xFA : (chr(0xE2), 'u'), 0xFB : (chr(0xE3), 'u'), 0xFC : (chr(0xE8), 'u'),
    0xFD : (chr(0xE2), 'y'), 0xFF : (chr(0xE8), 'y'),
    0xF8 : (chr(0xC3), chr(0xB8)),
    0xD8 : (chr(0xC3), chr(0x98)),
}

_s0 = {
    0xCF : 0xDF, 0xA4 : 0xDE, 0xB4 : 0xFE, 0xA2 : 0xD8, 0xC0 : 0xB0,
    0xB3 : 0xF8, 0xA5 : 0xC6, 0xB5 : 0xE6, 0xBA : 0xF0, 0xB2 : 0xF8 }

_t0 = {
    0xDF : chr(0xCF), 0xDE : chr(0xA4), 0xFE : chr(0xB4), 
    0xC6 : chr(0xA5), 0xE6 : chr(0xB5), 0xBA : chr(0xF0),
    0xB0 : chr(0xC0) }

#-------------------------------------------------------------------------
#
# Tasks
#
#-------------------------------------------------------------------------

def ansel_to_latin(s):
    """Converts an ANSEL encoded string to ISO-8859-1"""
    buff = cStringIO.StringIO()
    while s:
        c0 = ord(s[0])
        if c0 <= 31:
            head = ' '
            s = s[1:]
        elif c0 > 127:
            try:
                if c0 >= 0xC0:
                    c1 = ord(s[1])
                    head = chr(_s1[c0][c1])
                    s = s[2:]
                else:
                    head = chr(_s0[c0])
                    s = s[1:]
            except Exception:
                head = s[0]
                s = s[1:]
        else:
            head = s[0]
            s = s[1:]
        buff.write(head)
    ans = buff.getvalue()
    buff.close()
    return ans

def latin_to_ansel(s):
    """converts a iso-8859-1 string to ansel encoding"""
    buff = cStringIO.StringIO()
    orig = s
    while s:
        c = ord(s[0])
        if c <= 127:
            buff.write(s[0])
        else:
            if _t0.has_key(c):
                buff.write(_t0[c])
            else:
                try:
                    ansel = _t1[c]
                    buff.write(ansel[0])
                    buff.write(ansel[1])
                except Exception:
                    print "ANSEL decoding error: %x: %s" % (c,orig)
        s = s[1:]
    ans = buff.getvalue()
    buff.close()
    return ans

