#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2005  Donald N. Allingham
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

# $Id$

# ANSEL references:
#  http://lcweb2.loc.gov/diglib/codetables/45.html
#  http://www.gymel.com/charsets/ANSEL.html

# Note that cStringIO stores 8-bit strings (bytes not unicode)
# utf8 will do, since that looks just like bytes 
import cStringIO

# list of ANSEL codes that replicate ASCII
# note that DEL (127=0x7F) is a control char
# Note: spec allows control-chars that Gramps probably doesn't use
#  but 10=0x0A _is_ needed (!)
# ---
# Also: there are two additional control chars 0x98,0x9c (unicode same)
#  which we also ignore for now (start/emd of string (or sort sequence)
# ---
# TODO: should we allow TAB, as a Gramps extension?
_printable_ascii = map(chr, range(32,127)) # note: up thru 126
_use_ASCII = map(chr, [10, 27, 29 ,30, 31]) + _printable_ascii

# mappings of single byte ANSEL codes to unicode
_onebyte = {
     '\xA1' : u'\u0141',   '\xA2' : u'\u00d8',   '\xA3' : u'\u0110',   
     '\xA4' : u'\u00de',   '\xA5' : u'\u00c6',   '\xA6' : u'\u0152',   
     '\xA7' : u'\u02b9',   '\xA8' : u'\u00b7',   '\xA9' : u'\u266d',   
     '\xAA' : u'\u00ae',   '\xAB' : u'\u00b1',   '\xAC' : u'\u01a0',   
     '\xAD' : u'\u01af',   '\xAE' : u'\u02be',   '\xB0' : u'\u02bb',   
     '\xB1' : u'\u0142',   '\xB2' : u'\u00f8',   '\xB3' : u'\u0111',   
     '\xB4' : u'\u00fe',   '\xB5' : u'\u00e6',   '\xB6' : u'\u0153',   
     '\xB7' : u'\u02ba',   '\xB8' : u'\u0131',   '\xB9' : u'\u00a3',   
     '\xBA' : u'\u00f0',   '\xBC' : u'\u01a1',   '\xBD' : u'\u01b0',   
     '\xC0' : u'\u00b0',   '\xC1' : u'\u2113',   '\xC2' : u'\u2117',   
     '\xC3' : u'\u00a9',   '\xC4' : u'\u266f',   '\xC5' : u'\u00bf',   
     '\xC6' : u'\u00a1',   '\xC7' : u'\u00df',   '\xC8' : u'\u20ac',  
    }

# combining forms (in ANSEL, they precede the modified ASCII character
# whereas the unicode combining term follows the character modified
# Note: unicode allows multiple modifiers, but ANSEL may not (TDB?), 
# so we ignore multiple combining forms in this module
#  8d & 8e are zero-width joiner (ZWJ), and zero-width non-joiner ZWNJ
#  (strange things) probably not commonly found in our needs, unless one
#   starts writing persian (or???) poetry in ANSEL
_acombiners = {
     '\x8D' : u'\u200d',   '\x8E' : u'\u200c',   '\xE0' : u'\u0309',   
     '\xE1' : u'\u0300',   '\xE2' : u'\u0301',   '\xE3' : u'\u0302',   
     '\xE4' : u'\u0303',   '\xE5' : u'\u0304',   '\xE6' : u'\u0306',   
     '\xE7' : u'\u0307',   '\xE8' : u'\u0308',   '\xE9' : u'\u030c',   
     '\xEA' : u'\u030a',   '\xEB' : u'\ufe20',   '\xEC' : u'\ufe21',   
     '\xED' : u'\u0315',   '\xEE' : u'\u030b',   '\xEF' : u'\u0310',   
     '\xF0' : u'\u0327',   '\xF1' : u'\u0328',   '\xF2' : u'\u0323',   
     '\xF3' : u'\u0324',   '\xF4' : u'\u0325',   '\xF5' : u'\u0333',   
     '\xF6' : u'\u0332',   '\xF7' : u'\u0326',   '\xF8' : u'\u031c',   
     '\xF9' : u'\u032e',   '\xFA' : u'\ufe22',   '\xFB' : u'\ufe23',   
     '\xFE' : u'\u0313',  
   }

# mappings of two byte (precomposed forms) ANSEL codes to unicode
_twobyte = {
     '\xE0\x41' : u'\u1ea2',   '\xE0\x45' : u'\u1eba',   '\xE0\x49' : u'\u1ec8',   
     '\xE0\x4F' : u'\u1ece',   '\xE0\x55' : u'\u1ee6',   '\xE0\x59' : u'\u1ef6',   
     '\xE0\x61' : u'\u1ea3',   '\xE0\x65' : u'\u1ebb',   '\xE0\x69' : u'\u1ec9',   
     '\xE0\x6F' : u'\u1ecf',   '\xE0\x75' : u'\u1ee7',   '\xE0\x79' : u'\u1ef7',   
     '\xE1\x41' : u'\u00c0',   '\xE1\x45' : u'\u00c8',   '\xE1\x49' : u'\u00cc',   
     '\xE1\x4F' : u'\u00d2',   '\xE1\x55' : u'\u00d9',   '\xE1\x57' : u'\u1e80',   
     '\xE1\x59' : u'\u1ef2',   '\xE1\x61' : u'\u00e0',   '\xE1\x65' : u'\u00e8',   
     '\xE1\x69' : u'\u00ec',   '\xE1\x6F' : u'\u00f2',   '\xE1\x75' : u'\u00f9',   
     '\xE1\x77' : u'\u1e81',   '\xE1\x79' : u'\u1ef3',   '\xE2\x41' : u'\u00c1',   
     '\xE2\x43' : u'\u0106',   '\xE2\x45' : u'\u00c9',   '\xE2\x47' : u'\u01f4',   
     '\xE2\x49' : u'\u00cd',   '\xE2\x4B' : u'\u1e30',   '\xE2\x4C' : u'\u0139',   
     '\xE2\x4D' : u'\u1e3e',   '\xE2\x4E' : u'\u0143',   '\xE2\x4F' : u'\u00d3',   
     '\xE2\x50' : u'\u1e54',   '\xE2\x52' : u'\u0154',   '\xE2\x53' : u'\u015a',   
     '\xE2\x55' : u'\u00da',   '\xE2\x57' : u'\u1e82',   '\xE2\x59' : u'\u00dd',   
     '\xE2\x5A' : u'\u0179',   '\xE2\x61' : u'\u00e1',   '\xE2\x63' : u'\u0107',   
     '\xE2\x65' : u'\u00e9',   '\xE2\x67' : u'\u01f5',   '\xE2\x69' : u'\u00ed',   
     '\xE2\x6B' : u'\u1e31',   '\xE2\x6C' : u'\u013a',   '\xE2\x6D' : u'\u1e3f',   
     '\xE2\x6E' : u'\u0144',   '\xE2\x6F' : u'\u00f3',   '\xE2\x70' : u'\u1e55',   
     '\xE2\x72' : u'\u0155',   '\xE2\x73' : u'\u015b',   '\xE2\x75' : u'\u00fa',   
     '\xE2\x77' : u'\u1e83',   '\xE2\x79' : u'\u00fd',   '\xE2\x7A' : u'\u017a',   
     '\xE2\xA5' : u'\u01fc',   '\xE2\xB5' : u'\u01fd',   '\xE3\x41' : u'\u00c2',   
     '\xE3\x43' : u'\u0108',   '\xE3\x45' : u'\u00ca',   '\xE3\x47' : u'\u011c',   
     '\xE3\x48' : u'\u0124',   '\xE3\x49' : u'\u00ce',   '\xE3\x4A' : u'\u0134',   
     '\xE3\x4F' : u'\u00d4',   '\xE3\x53' : u'\u015c',   '\xE3\x55' : u'\u00db',   
     '\xE3\x57' : u'\u0174',   '\xE3\x59' : u'\u0176',   '\xE3\x5A' : u'\u1e90',   
     '\xE3\x61' : u'\u00e2',   '\xE3\x63' : u'\u0109',   '\xE3\x65' : u'\u00ea',   
     '\xE3\x67' : u'\u011d',   '\xE3\x68' : u'\u0125',   '\xE3\x69' : u'\u00ee',   
     '\xE3\x6A' : u'\u0135',   '\xE3\x6F' : u'\u00f4',   '\xE3\x73' : u'\u015d',   
     '\xE3\x75' : u'\u00fb',   '\xE3\x77' : u'\u0175',   '\xE3\x79' : u'\u0177',   
     '\xE3\x7A' : u'\u1e91',   '\xE4\x41' : u'\u00c3',   '\xE4\x45' : u'\u1ebc',   
     '\xE4\x49' : u'\u0128',   '\xE4\x4E' : u'\u00d1',   '\xE4\x4F' : u'\u00d5',   
     '\xE4\x55' : u'\u0168',   '\xE4\x56' : u'\u1e7c',   '\xE4\x59' : u'\u1ef8',   
     '\xE4\x61' : u'\u00e3',   '\xE4\x65' : u'\u1ebd',   '\xE4\x69' : u'\u0129',   
     '\xE4\x6E' : u'\u00f1',   '\xE4\x6F' : u'\u00f5',   '\xE4\x75' : u'\u0169',   
     '\xE4\x76' : u'\u1e7d',   '\xE4\x79' : u'\u1ef9',   '\xE5\x41' : u'\u0100',   
     '\xE5\x45' : u'\u0112',   '\xE5\x47' : u'\u1e20',   '\xE5\x49' : u'\u012a',   
     '\xE5\x4F' : u'\u014c',   '\xE5\x55' : u'\u016a',   '\xE5\x61' : u'\u0101',   
     '\xE5\x65' : u'\u0113',   '\xE5\x67' : u'\u1e21',   '\xE5\x69' : u'\u012b',   
     '\xE5\x6F' : u'\u014d',   '\xE5\x75' : u'\u016b',   '\xE5\xA5' : u'\u01e2',   
     '\xE5\xB5' : u'\u01e3',   '\xE6\x41' : u'\u0102',   '\xE6\x45' : u'\u0114',   
     '\xE6\x47' : u'\u011e',   '\xE6\x49' : u'\u012c',   '\xE6\x4F' : u'\u014e',   
     '\xE6\x55' : u'\u016c',   '\xE6\x61' : u'\u0103',   '\xE6\x65' : u'\u0115',   
     '\xE6\x67' : u'\u011f',   '\xE6\x69' : u'\u012d',   '\xE6\x6F' : u'\u014f',   
     '\xE6\x75' : u'\u016d',   '\xE7\x42' : u'\u1e02',   '\xE7\x43' : u'\u010a',   
     '\xE7\x44' : u'\u1e0a',   '\xE7\x45' : u'\u0116',   '\xE7\x46' : u'\u1e1e',   
     '\xE7\x47' : u'\u0120',   '\xE7\x48' : u'\u1e22',   '\xE7\x49' : u'\u0130',   
     '\xE7\x4D' : u'\u1e40',   '\xE7\x4E' : u'\u1e44',   '\xE7\x50' : u'\u1e56',   
     '\xE7\x52' : u'\u1e58',   '\xE7\x53' : u'\u1e60',   '\xE7\x54' : u'\u1e6a',   
     '\xE7\x57' : u'\u1e86',   '\xE7\x58' : u'\u1e8a',   '\xE7\x59' : u'\u1e8e',   
     '\xE7\x5A' : u'\u017b',   '\xE7\x62' : u'\u1e03',   '\xE7\x63' : u'\u010b',   
     '\xE7\x64' : u'\u1e0b',   '\xE7\x65' : u'\u0117',   '\xE7\x66' : u'\u1e1f',   
     '\xE7\x67' : u'\u0121',   '\xE7\x68' : u'\u1e23',   '\xE7\x6D' : u'\u1e41',   
     '\xE7\x6E' : u'\u1e45',   '\xE7\x70' : u'\u1e57',   '\xE7\x72' : u'\u1e59',   
     '\xE7\x73' : u'\u1e61',   '\xE7\x74' : u'\u1e6b',   '\xE7\x77' : u'\u1e87',   
     '\xE7\x78' : u'\u1e8b',   '\xE7\x79' : u'\u1e8f',   '\xE7\x7A' : u'\u017c',   
     '\xE8\x41' : u'\u00c4',   '\xE8\x45' : u'\u00cb',   '\xE8\x48' : u'\u1e26',   
     '\xE8\x49' : u'\u00cf',   '\xE8\x4F' : u'\u00d6',   '\xE8\x55' : u'\u00dc',   
     '\xE8\x57' : u'\u1e84',   '\xE8\x58' : u'\u1e8c',   '\xE8\x59' : u'\u0178',   
     '\xE8\x61' : u'\u00e4',   '\xE8\x65' : u'\u00eb',   '\xE8\x68' : u'\u1e27',   
     '\xE8\x69' : u'\u00ef',   '\xE8\x6F' : u'\u00f6',   '\xE8\x74' : u'\u1e97',   
     '\xE8\x75' : u'\u00fc',   '\xE8\x77' : u'\u1e85',   '\xE8\x78' : u'\u1e8d',   
     '\xE8\x79' : u'\u00ff',   '\xE9\x41' : u'\u01cd',   '\xE9\x43' : u'\u010c',   
     '\xE9\x44' : u'\u010e',   '\xE9\x45' : u'\u011a',   '\xE9\x47' : u'\u01e6',   
     '\xE9\x49' : u'\u01cf',   '\xE9\x4B' : u'\u01e8',   '\xE9\x4C' : u'\u013d',   
     '\xE9\x4E' : u'\u0147',   '\xE9\x4F' : u'\u01d1',   '\xE9\x52' : u'\u0158',   
     '\xE9\x53' : u'\u0160',   '\xE9\x54' : u'\u0164',   '\xE9\x55' : u'\u01d3',   
     '\xE9\x5A' : u'\u017d',   '\xE9\x61' : u'\u01ce',   '\xE9\x63' : u'\u010d',   
     '\xE9\x64' : u'\u010f',   '\xE9\x65' : u'\u011b',   '\xE9\x67' : u'\u01e7',   
     '\xE9\x69' : u'\u01d0',   '\xE9\x6A' : u'\u01f0',   '\xE9\x6B' : u'\u01e9',   
     '\xE9\x6C' : u'\u013e',   '\xE9\x6E' : u'\u0148',   '\xE9\x6F' : u'\u01d2',   
     '\xE9\x72' : u'\u0159',   '\xE9\x73' : u'\u0161',   '\xE9\x74' : u'\u0165',   
     '\xE9\x75' : u'\u01d4',   '\xE9\x7A' : u'\u017e',   '\xEA\x41' : u'\u00c5',   
     '\xEA\x61' : u'\u00e5',   '\xEA\x75' : u'\u016f',   '\xEA\x77' : u'\u1e98',   
     '\xEA\x79' : u'\u1e99',   '\xEA\xAD' : u'\u016e',   '\xEE\x4F' : u'\u0150',   
     '\xEE\x55' : u'\u0170',   '\xEE\x6F' : u'\u0151',   '\xEE\x75' : u'\u0171',   
     '\xF0\x20' : u'\u00b8',   '\xF0\x43' : u'\u00c7',   '\xF0\x44' : u'\u1e10',   
     '\xF0\x47' : u'\u0122',   '\xF0\x48' : u'\u1e28',   '\xF0\x4B' : u'\u0136',   
     '\xF0\x4C' : u'\u013b',   '\xF0\x4E' : u'\u0145',   '\xF0\x52' : u'\u0156',   
     '\xF0\x53' : u'\u015e',   '\xF0\x54' : u'\u0162',   '\xF0\x63' : u'\u00e7',   
     '\xF0\x64' : u'\u1e11',   '\xF0\x67' : u'\u0123',   '\xF0\x68' : u'\u1e29',   
     '\xF0\x6B' : u'\u0137',   '\xF0\x6C' : u'\u013c',   '\xF0\x6E' : u'\u0146',   
     '\xF0\x72' : u'\u0157',   '\xF0\x73' : u'\u015f',   '\xF0\x74' : u'\u0163',   
     '\xF1\x41' : u'\u0104',   '\xF1\x45' : u'\u0118',   '\xF1\x49' : u'\u012e',   
     '\xF1\x4F' : u'\u01ea',   '\xF1\x55' : u'\u0172',   '\xF1\x61' : u'\u0105',   
     '\xF1\x65' : u'\u0119',   '\xF1\x69' : u'\u012f',   '\xF1\x6F' : u'\u01eb',   
     '\xF1\x75' : u'\u0173',   '\xF2\x41' : u'\u1ea0',   '\xF2\x42' : u'\u1e04',   
     '\xF2\x44' : u'\u1e0c',   '\xF2\x45' : u'\u1eb8',   '\xF2\x48' : u'\u1e24',   
     '\xF2\x49' : u'\u1eca',   '\xF2\x4B' : u'\u1e32',   '\xF2\x4C' : u'\u1e36',   
     '\xF2\x4D' : u'\u1e42',   '\xF2\x4E' : u'\u1e46',   '\xF2\x4F' : u'\u1ecc',   
     '\xF2\x52' : u'\u1e5a',   '\xF2\x53' : u'\u1e62',   '\xF2\x54' : u'\u1e6c',   
     '\xF2\x55' : u'\u1ee4',   '\xF2\x56' : u'\u1e7e',   '\xF2\x57' : u'\u1e88',   
     '\xF2\x59' : u'\u1ef4',   '\xF2\x5A' : u'\u1e92',   '\xF2\x61' : u'\u1ea1',   
     '\xF2\x62' : u'\u1e05',   '\xF2\x64' : u'\u1e0d',   '\xF2\x65' : u'\u1eb9',   
     '\xF2\x68' : u'\u1e25',   '\xF2\x69' : u'\u1ecb',   '\xF2\x6B' : u'\u1e33',   
     '\xF2\x6C' : u'\u1e37',   '\xF2\x6D' : u'\u1e43',   '\xF2\x6E' : u'\u1e47',   
     '\xF2\x6F' : u'\u1ecd',   '\xF2\x72' : u'\u1e5b',   '\xF2\x73' : u'\u1e63',   
     '\xF2\x74' : u'\u1e6d',   '\xF2\x75' : u'\u1ee5',   '\xF2\x76' : u'\u1e7f',   
     '\xF2\x77' : u'\u1e89',   '\xF2\x79' : u'\u1ef5',   '\xF2\x7A' : u'\u1e93',   
     '\xF3\x55' : u'\u1e72',   '\xF3\x75' : u'\u1e73',   '\xF4\x41' : u'\u1e00',   
     '\xF4\x61' : u'\u1e01',   '\xF9\x48' : u'\u1e2a',   '\xF9\x68' : u'\u1e2b',  
   }

# mappings of unicode to ANSEL codes
# note: a char u'\u00A1' is internally remembered & represented as u'\xA1'
#  so do NOT blindly use 4-hexdigit keys for those cases
#  or the conversion function will fail
_utoa = { 
     u'\xa1'   : '\xC6',       u'\xa3'   : '\xB9',       u'\xa9'   : '\xC3',       
     u'\xae'   : '\xAA',       u'\xb0'   : '\xC0',       u'\xb1'   : '\xAB',       
     u'\xb7'   : '\xA8',       u'\xb8'   : '\xF0\x20',   u'\xbf'   : '\xC5',       
     u'\xc0'   : '\xE1\x41',   u'\xc1'   : '\xE2\x41',   u'\xc2'   : '\xE3\x41',   
     u'\xc3'   : '\xE4\x41',   u'\xc4'   : '\xE8\x41',   u'\xc5'   : '\xEA\x41',   
     u'\xc6'   : '\xA5',       u'\xc7'   : '\xF0\x43',   u'\xc8'   : '\xE1\x45',   
     u'\xc9'   : '\xE2\x45',   u'\xca'   : '\xE3\x45',   u'\xcb'   : '\xE8\x45',   
     u'\xcc'   : '\xE1\x49',   u'\xcd'   : '\xE2\x49',   u'\xce'   : '\xE3\x49',   
     u'\xcf'   : '\xE8\x49',   u'\xd1'   : '\xE4\x4E',   u'\xd2'   : '\xE1\x4F',   
     u'\xd3'   : '\xE2\x4F',   u'\xd4'   : '\xE3\x4F',   u'\xd5'   : '\xE4\x4F',   
     u'\xd6'   : '\xE8\x4F',   u'\xd8'   : '\xA2',       u'\xd9'   : '\xE1\x55',   
     u'\xda'   : '\xE2\x55',   u'\xdb'   : '\xE3\x55',   u'\xdc'   : '\xE8\x55',   
     u'\xdd'   : '\xE2\x59',   u'\xde'   : '\xA4',       u'\xdf'   : '\xC7',       
     u'\xe0'   : '\xE1\x61',   u'\xe1'   : '\xE2\x61',   u'\xe2'   : '\xE3\x61',   
     u'\xe3'   : '\xE4\x61',   u'\xe4'   : '\xE8\x61',   u'\xe5'   : '\xEA\x61',   
     u'\xe6'   : '\xB5',       u'\xe7'   : '\xF0\x63',   u'\xe8'   : '\xE1\x65',   
     u'\xe9'   : '\xE2\x65',   u'\xea'   : '\xE3\x65',   u'\xeb'   : '\xE8\x65',   
     u'\xec'   : '\xE1\x69',   u'\xed'   : '\xE2\x69',   u'\xee'   : '\xE3\x69',   
     u'\xef'   : '\xE8\x69',   u'\xf0'   : '\xBA',       u'\xf1'   : '\xE4\x6E',   
     u'\xf2'   : '\xE1\x6F',   u'\xf3'   : '\xE2\x6F',   u'\xf4'   : '\xE3\x6F',   
     u'\xf5'   : '\xE4\x6F',   u'\xf6'   : '\xE8\x6F',   u'\xf8'   : '\xB2',       
     u'\xf9'   : '\xE1\x75',   u'\xfa'   : '\xE2\x75',   u'\xfb'   : '\xE3\x75',   
     u'\xfc'   : '\xE8\x75',   u'\xfd'   : '\xE2\x79',   u'\xfe'   : '\xB4',       
     u'\xff'   : '\xE8\x79',   u'\u0100' : '\xE5\x41',   u'\u0101' : '\xE5\x61',   
     u'\u0102' : '\xE6\x41',   u'\u0103' : '\xE6\x61',   u'\u0104' : '\xF1\x41',   
     u'\u0105' : '\xF1\x61',   u'\u0106' : '\xE2\x43',   u'\u0107' : '\xE2\x63',   
     u'\u0108' : '\xE3\x43',   u'\u0109' : '\xE3\x63',   u'\u010a' : '\xE7\x43',   
     u'\u010b' : '\xE7\x63',   u'\u010c' : '\xE9\x43',   u'\u010d' : '\xE9\x63',   
     u'\u010e' : '\xE9\x44',   u'\u010f' : '\xE9\x64',   u'\u0110' : '\xA3',       
     u'\u0111' : '\xB3',       u'\u0112' : '\xE5\x45',   u'\u0113' : '\xE5\x65',   
     u'\u0114' : '\xE6\x45',   u'\u0115' : '\xE6\x65',   u'\u0116' : '\xE7\x45',   
     u'\u0117' : '\xE7\x65',   u'\u0118' : '\xF1\x45',   u'\u0119' : '\xF1\x65',   
     u'\u011a' : '\xE9\x45',   u'\u011b' : '\xE9\x65',   u'\u011c' : '\xE3\x47',   
     u'\u011d' : '\xE3\x67',   u'\u011e' : '\xE6\x47',   u'\u011f' : '\xE6\x67',   
     u'\u0120' : '\xE7\x47',   u'\u0121' : '\xE7\x67',   u'\u0122' : '\xF0\x47',   
     u'\u0123' : '\xF0\x67',   u'\u0124' : '\xE3\x48',   u'\u0125' : '\xE3\x68',   
     u'\u0128' : '\xE4\x49',   u'\u0129' : '\xE4\x69',   u'\u012a' : '\xE5\x49',   
     u'\u012b' : '\xE5\x69',   u'\u012c' : '\xE6\x49',   u'\u012d' : '\xE6\x69',   
     u'\u012e' : '\xF1\x49',   u'\u012f' : '\xF1\x69',   u'\u0130' : '\xE7\x49',   
     u'\u0131' : '\xB8',       u'\u0134' : '\xE3\x4A',   u'\u0135' : '\xE3\x6A',   
     u'\u0136' : '\xF0\x4B',   u'\u0137' : '\xF0\x6B',   u'\u0139' : '\xE2\x4C',   
     u'\u013a' : '\xE2\x6C',   u'\u013b' : '\xF0\x4C',   u'\u013c' : '\xF0\x6C',   
     u'\u013d' : '\xE9\x4C',   u'\u013e' : '\xE9\x6C',   u'\u0141' : '\xA1',       
     u'\u0142' : '\xB1',       u'\u0143' : '\xE2\x4E',   u'\u0144' : '\xE2\x6E',   
     u'\u0145' : '\xF0\x4E',   u'\u0146' : '\xF0\x6E',   u'\u0147' : '\xE9\x4E',   
     u'\u0148' : '\xE9\x6E',   u'\u014c' : '\xE5\x4F',   u'\u014d' : '\xE5\x6F',   
     u'\u014e' : '\xE6\x4F',   u'\u014f' : '\xE6\x6F',   u'\u0150' : '\xEE\x4F',   
     u'\u0151' : '\xEE\x6F',   u'\u0152' : '\xA6',       u'\u0153' : '\xB6',       
     u'\u0154' : '\xE2\x52',   u'\u0155' : '\xE2\x72',   u'\u0156' : '\xF0\x52',   
     u'\u0157' : '\xF0\x72',   u'\u0158' : '\xE9\x52',   u'\u0159' : '\xE9\x72',   
     u'\u015a' : '\xE2\x53',   u'\u015b' : '\xE2\x73',   u'\u015c' : '\xE3\x53',   
     u'\u015d' : '\xE3\x73',   u'\u015e' : '\xF0\x53',   u'\u015f' : '\xF0\x73',   
     u'\u0160' : '\xE9\x53',   u'\u0161' : '\xE9\x73',   u'\u0162' : '\xF0\x54',   
     u'\u0163' : '\xF0\x74',   u'\u0164' : '\xE9\x54',   u'\u0165' : '\xE9\x74',   
     u'\u0168' : '\xE4\x55',   u'\u0169' : '\xE4\x75',   u'\u016a' : '\xE5\x55',   
     u'\u016b' : '\xE5\x75',   u'\u016c' : '\xE6\x55',   u'\u016d' : '\xE6\x75',   
     u'\u016e' : '\xEA\xAD',   u'\u016f' : '\xEA\x75',   u'\u0170' : '\xEE\x55',   
     u'\u0171' : '\xEE\x75',   u'\u0172' : '\xF1\x55',   u'\u0173' : '\xF1\x75',   
     u'\u0174' : '\xE3\x57',   u'\u0175' : '\xE3\x77',   u'\u0176' : '\xE3\x59',   
     u'\u0177' : '\xE3\x79',   u'\u0178' : '\xE8\x59',   u'\u0179' : '\xE2\x5A',   
     u'\u017a' : '\xE2\x7A',   u'\u017b' : '\xE7\x5A',   u'\u017c' : '\xE7\x7A',   
     u'\u017d' : '\xE9\x5A',   u'\u017e' : '\xE9\x7A',   u'\u01a0' : '\xAC',       
     u'\u01a1' : '\xBC',       u'\u01af' : '\xAD',       u'\u01b0' : '\xBD',       
     u'\u01cd' : '\xE9\x41',   u'\u01ce' : '\xE9\x61',   u'\u01cf' : '\xE9\x49',   
     u'\u01d0' : '\xE9\x69',   u'\u01d1' : '\xE9\x4F',   u'\u01d2' : '\xE9\x6F',   
     u'\u01d3' : '\xE9\x55',   u'\u01d4' : '\xE9\x75',   u'\u01e2' : '\xE5\xA5',   
     u'\u01e3' : '\xE5\xB5',   u'\u01e6' : '\xE9\x47',   u'\u01e7' : '\xE9\x67',   
     u'\u01e8' : '\xE9\x4B',   u'\u01e9' : '\xE9\x6B',   u'\u01ea' : '\xF1\x4F',   
     u'\u01eb' : '\xF1\x6F',   u'\u01f0' : '\xE9\x6A',   u'\u01f4' : '\xE2\x47',   
     u'\u01f5' : '\xE2\x67',   u'\u01fc' : '\xE2\xA5',   u'\u01fd' : '\xE2\xB5',   
     u'\u02b9' : '\xA7',       u'\u02ba' : '\xB7',       u'\u02bb' : '\xB0',       
     u'\u02be' : '\xAE',       u'\u1e00' : '\xF4\x41',   u'\u1e01' : '\xF4\x61',   
     u'\u1e02' : '\xE7\x42',   u'\u1e03' : '\xE7\x62',   u'\u1e04' : '\xF2\x42',   
     u'\u1e05' : '\xF2\x62',   u'\u1e0a' : '\xE7\x44',   u'\u1e0b' : '\xE7\x64',   
     u'\u1e0c' : '\xF2\x44',   u'\u1e0d' : '\xF2\x64',   u'\u1e10' : '\xF0\x44',   
     u'\u1e11' : '\xF0\x64',   u'\u1e1e' : '\xE7\x46',   u'\u1e1f' : '\xE7\x66',   
     u'\u1e20' : '\xE5\x47',   u'\u1e21' : '\xE5\x67',   u'\u1e22' : '\xE7\x48',   
     u'\u1e23' : '\xE7\x68',   u'\u1e24' : '\xF2\x48',   u'\u1e25' : '\xF2\x68',   
     u'\u1e26' : '\xE8\x48',   u'\u1e27' : '\xE8\x68',   u'\u1e28' : '\xF0\x48',   
     u'\u1e29' : '\xF0\x68',   u'\u1e2a' : '\xF9\x48',   u'\u1e2b' : '\xF9\x68',   
     u'\u1e30' : '\xE2\x4B',   u'\u1e31' : '\xE2\x6B',   u'\u1e32' : '\xF2\x4B',   
     u'\u1e33' : '\xF2\x6B',   u'\u1e36' : '\xF2\x4C',   u'\u1e37' : '\xF2\x6C',   
     u'\u1e3e' : '\xE2\x4D',   u'\u1e3f' : '\xE2\x6D',   u'\u1e40' : '\xE7\x4D',   
     u'\u1e41' : '\xE7\x6D',   u'\u1e42' : '\xF2\x4D',   u'\u1e43' : '\xF2\x6D',   
     u'\u1e44' : '\xE7\x4E',   u'\u1e45' : '\xE7\x6E',   u'\u1e46' : '\xF2\x4E',   
     u'\u1e47' : '\xF2\x6E',   u'\u1e54' : '\xE2\x50',   u'\u1e55' : '\xE2\x70',   
     u'\u1e56' : '\xE7\x50',   u'\u1e57' : '\xE7\x70',   u'\u1e58' : '\xE7\x52',   
     u'\u1e59' : '\xE7\x72',   u'\u1e5a' : '\xF2\x52',   u'\u1e5b' : '\xF2\x72',   
     u'\u1e60' : '\xE7\x53',   u'\u1e61' : '\xE7\x73',   u'\u1e62' : '\xF2\x53',   
     u'\u1e63' : '\xF2\x73',   u'\u1e6a' : '\xE7\x54',   u'\u1e6b' : '\xE7\x74',   
     u'\u1e6c' : '\xF2\x54',   u'\u1e6d' : '\xF2\x74',   u'\u1e72' : '\xF3\x55',   
     u'\u1e73' : '\xF3\x75',   u'\u1e7c' : '\xE4\x56',   u'\u1e7d' : '\xE4\x76',   
     u'\u1e7e' : '\xF2\x56',   u'\u1e7f' : '\xF2\x76',   u'\u1e80' : '\xE1\x57',   
     u'\u1e81' : '\xE1\x77',   u'\u1e82' : '\xE2\x57',   u'\u1e83' : '\xE2\x77',   
     u'\u1e84' : '\xE8\x57',   u'\u1e85' : '\xE8\x77',   u'\u1e86' : '\xE7\x57',   
     u'\u1e87' : '\xE7\x77',   u'\u1e88' : '\xF2\x57',   u'\u1e89' : '\xF2\x77',   
     u'\u1e8a' : '\xE7\x58',   u'\u1e8b' : '\xE7\x78',   u'\u1e8c' : '\xE8\x58',   
     u'\u1e8d' : '\xE8\x78',   u'\u1e8e' : '\xE7\x59',   u'\u1e8f' : '\xE7\x79',   
     u'\u1e90' : '\xE3\x5A',   u'\u1e91' : '\xE3\x7A',   u'\u1e92' : '\xF2\x5A',   
     u'\u1e93' : '\xF2\x7A',   u'\u1e97' : '\xE8\x74',   u'\u1e98' : '\xEA\x77',   
     u'\u1e99' : '\xEA\x79',   u'\u1ea0' : '\xF2\x41',   u'\u1ea1' : '\xF2\x61',   
     u'\u1ea2' : '\xE0\x41',   u'\u1ea3' : '\xE0\x61',   u'\u1eb8' : '\xF2\x45',   
     u'\u1eb9' : '\xF2\x65',   u'\u1eba' : '\xE0\x45',   u'\u1ebb' : '\xE0\x65',   
     u'\u1ebc' : '\xE4\x45',   u'\u1ebd' : '\xE4\x65',   u'\u1ec8' : '\xE0\x49',   
     u'\u1ec9' : '\xE0\x69',   u'\u1eca' : '\xF2\x49',   u'\u1ecb' : '\xF2\x69',   
     u'\u1ecc' : '\xF2\x4F',   u'\u1ecd' : '\xF2\x6F',   u'\u1ece' : '\xE0\x4F',   
     u'\u1ecf' : '\xE0\x6F',   u'\u1ee4' : '\xF2\x55',   u'\u1ee5' : '\xF2\x75',   
     u'\u1ee6' : '\xE0\x55',   u'\u1ee7' : '\xE0\x75',   u'\u1ef2' : '\xE1\x59',   
     u'\u1ef3' : '\xE1\x79',   u'\u1ef4' : '\xF2\x59',   u'\u1ef5' : '\xF2\x79',   
     u'\u1ef6' : '\xE0\x59',   u'\u1ef7' : '\xE0\x79',   u'\u1ef8' : '\xE4\x59',   
     u'\u1ef9' : '\xE4\x79',   u'\u20ac' : '\xC8',       u'\u2113' : '\xC1',       
     u'\u2117' : '\xC2',       u'\u266d' : '\xA9',       u'\u266f' : '\xC4',      
   }


# unicode combining forms mapped to ANSEL 
_ucombiners = {
     u'\u0300' : '\xE1',       u'\u0301' : '\xE2',       u'\u0302' : '\xE3',       
     u'\u0303' : '\xE4',       u'\u0304' : '\xE5',       u'\u0306' : '\xE6',       
     u'\u0307' : '\xE7',       u'\u0308' : '\xE8',       u'\u0309' : '\xE0',       
     u'\u030a' : '\xEA',       u'\u030b' : '\xEE',       u'\u030c' : '\xE9',       
     u'\u0310' : '\xEF',       u'\u0313' : '\xFE',       u'\u0315' : '\xED',       
     u'\u031c' : '\xF8',       u'\u0323' : '\xF2',       u'\u0324' : '\xF3',       
     u'\u0325' : '\xF4',       u'\u0326' : '\xF7',       u'\u0327' : '\xF0',       
     u'\u0328' : '\xF1',       u'\u032e' : '\xF9',       u'\u0332' : '\xF6',       
     u'\u0333' : '\xF5',       u'\u200c' : '\x8E',       u'\u200d' : '\x8D',       
     u'\ufe20' : '\xEB',       u'\ufe21' : '\xEC',       u'\ufe22' : '\xFA',       
     u'\ufe23' : '\xFB',      
}
 
# TODO: change name to ansel_to_unicode (it does NOT return utf-8)
# ALSO: I think I'd prefer full pass-through of ANSEL's ASCII subset,
#  with substitutions and deletions handled at a higher level
def ansel_to_utf8(s):
    """ Convert an ANSEL encoded string to unicode """

    buff = cStringIO.StringIO()
    while s:
        if ord(s[0]) < 128:
            if s[0] in _use_ASCII:
                head = s[0]
            else:
                # substitute space for disallowed (control) chars
                head = ' '
            s = s[1:]
        else:
            if _twobyte.has_key(s[0:2]):
                head = _twobyte[s[0:2]]
                s = s[2:]
            elif _onebyte.has_key(s[0]):
                head = _onebyte[s[0]]
                s = s[1:]
            elif s[0] in _acombiners.keys():
                c =  _acombiners[s[0]]
                # always consume the combiner
                s = s[1:]
                next = s[0]
                if next in _printable_ascii:
                    # consume next as well
                    s = s[1:]
                    # unicode: combiner follows base-char
                    head = next + c
                else:
                    # just drop the unexpected combiner
                    continue 
            else:
                head = u'\ufffd' # "Replacement Char"
                s = s[1:]
        # note: cStringIO handles 8-bit strings, only (no unicode)
        buff.write(head.encode("utf-8"))
    ans = unicode(buff.getvalue(), "utf-8")
    buff.close()
    return ans


# TODO: change name to unicode_to_ansel (it does NOT process utf-8 input) 
def utf8_to_ansel(s):
    """ Convert a unicode string to ANSEL """
   
    buff = cStringIO.StringIO()
    while s:
        if ord(s[0]) < 128:
            head = s[0].encode('ascii')
            if not head in _use_ASCII:
                head = ' '
        else:
            if s[0] in _utoa.keys():
                head = _utoa[s[0]]
            elif s[0] in _ucombiners.keys():
                c = _ucombiners[s[0]]
                # head happens to have last conversion to ansel
                if len(head) == 1 and head[-1] in _printable_ascii:
                    last = head[-1]
                    head = head[:-1] + c + last
                    buff.seek(-1,2)
                    buff.truncate()
                else:
                    # ignore mpultiple combiners
                    # but always consume the combiner
                    s = s[1:]
                    continue
            else:
                head = '?'
        s = s[1:]
        buff.write(head)
    ans = buff.getvalue()
    buff.close()
    return ans
