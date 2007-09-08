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

"""
Handles ANSEL/Unicode conversions
"""

import cStringIO

ONEBYTE = {
    '\x8D' : u'\x20\x0D', '\x8E' : u'\x20\x0C', '\xA1' : u'\x01\x41',
    '\xA2' : u'\xD8',     '\xA3' : u'\xD0',     '\xA4' : u'\xDE',
    '\xA5' : u'\xC6',     '\xA6' : u'\x01\x52', '\xA7' : u'\x02\xB9',
    '\xA8' : u'\xB7',     '\xA9' : u'\x26\x6D', '\xAA' : u'\xAE',
    '\xAB' : u'\xB1',     '\xAC' : u'\x01\xA0', '\xAD' : u'\x01\xAF',
    '\xAE' : u'\x02\xBE', '\xB0' : u'\x02\xBF', '\xB1' : u'\x01\x42',
    '\xB2' : u'\xF8',     '\xB3' : u'\x01\x11', '\xB4' : u'\xFE',
    '\xB5' : u'\xE6',     '\xB6' : u'\x01\x53', '\xB7' : u'\x02\xBA',
    '\xB8' : u'\x01\x31', '\xB9' : u'\xA3',     '\xBA' : u'\xF0',
    '\xBC' : u'\x01\xA1', '\xBD' : u'\x01\xB0', '\xC0' : u'\xB0',
    '\xC1' : u'\x21\x13', '\xC2' : u'\x21\x17', '\xC3' : u'\xA9',
    '\xC4' : u'\x26\x6F', '\xC5' : u'\xBF',     '\xC6' : u'\xA1',
    '\xCF' : u'\xDF',     '\xE0' : u'\x03\x09', '\xE1' : u'\x03',
    '\xE2' : u'\x03\x01', '\xE3' : u'\x03\x02', '\xE4' : u'\x03\x03',
    '\xE5' : u'\x03\x04', '\xE6' : u'\x03\x06', '\xE7' : u'\x03\x07',
    '\xE9' : u'\x03\x0C', '\xEA' : u'\x03\x0A', '\xEB' : u'\xFE\x20',
    '\xEC' : u'\xFE\x21', '\xED' : u'\x03\x15', '\xEE' : u'\x03\x0B',
    '\xEF' : u'\x03\x10', '\xF0' : u'\x03\x27', '\xF1' : u'\x03\x28',
    '\xF2' : u'\x03\x23', '\xF3' : u'\x03\x24', '\xF4' : u'\x03\x25',
    '\xF5' : u'\x03\x33', '\xF6' : u'\x03\x32', '\xF7' : u'\x03\x26',
    '\xF8' : u'\x03\x1C', '\xF9' : u'\x03\x2E', '\xFA' : u'\xFE\x22',
    '\xFB' : u'\xFE\x23', '\xFE' : u'\x03\x13',
    }

TWOBYTE = {
    '\xe1a' : u'\xe0',     '\xf2T' : u'\x1el',    '\xf2V' : u'\x1e~',
    '\xe9z' : u'\x01~',    '\xe1e' : u'\xe8',     '\xeau' : u'\x01o',
    '\xf2S' : u'\x1eb',    '\xe1i' : u'\xec',     '\xe9s' : u'\x01a',
    '\xe9r' : u'\x01Y',    '\xe9u' : u'\x01\xd4', '\xe9t' : u'\x01e',
    '\xe1o' : u'\xf2',     '\xe9i' : u'\x01\xd0', '\xf2E' : u'\x1e\xb8',
    '\xe9k' : u'\x01\xe9', '\xe9j' : u'\x01\xf0', '\xe1u' : u'\xf9',
    '\xe9l' : u'\x01>',    '\xe1w' : u'\x1e\x81', '\xe9n' : u'\x01H',
    '\xe1y' : u'\x1e\xf3', '\xf2M' : u'\x1eB',    '\xe9c' : u'\x01\r',
    '\xf2O' : u'\x1e\xcc', '\xe9e' : u'\x01\x1b', '\xe9d' : u'\x01\x0f',
    '\xe9g' : u'\x01\xe7', '\xeaA' : u'\xc5',     '\xe1A' : u'\xc0',
    '\xf2u' : u'\x1e\xe5', '\xf2v' : u'\x1e\x7f', '\xe9Z' : u'\x01}',
    '\xe1E' : u'\xc8',     '\xf2R' : u'\x1eZ',    '\xf2r' : u'\x1e[',
    '\xf0c' : u'\xe7',     '\xe1I' : u'\xcc',     '\xe9S' : u'\x01`',
    '\xe9R' : u'\x01X',    '\xe9U' : u'\x01\xd3', '\xe9T' : u'\x01d',
    '\xe1O' : u'\xd2',     '\xeaa' : u'\xe5',     '\xe9I' : u'\x01\xcf',
    '\xf2e' : u'\x1e\xb9', '\xe9K' : u'\x01\xe8', '\xe1U' : u'\xd9',
    '\xe9L' : u'\x01=',    '\xe1W' : u'\x1e\x80', '\xe9N' : u'\x01G',
    '\xe1Y' : u'\x1e\xf2', '\xf0h' : u'\x1e)',    '\xe9C' : u'\x01\x0c',
    '\xf2o' : u'\x1e\xcd', '\xe9E' : u'\x01\x1a', '\xe9D' : u'\x01\x0e',
    '\xe9G' : u'\x01\xe6', '\xf0g' : u'\x01#',    '\xe2e' : u'\xe9',
    '\xe2g' : u'\x01\xf5', '\xe2a' : u'\xe1',     '\xe2c' : u'\x01\x07',
    '\xe2l' : u'\x01:',    '\xe2m' : u'\x1e?',    '\xe2n' : u'\x01D',
    '\xe2o' : u'\xf3',     '\xe2i' : u'\xed',     '\xf3U' : u'\x1er',
    '\xe2k' : u'\x1e1',    '\xe2u' : u'\xfa',     '\xe2w' : u'\x1e\x83',
    '\xe2p' : u'\x1eU',    '\xf2Z' : u'\x1e\x92', '\xe2r' : u'\x01U',
    '\xe2s' : u'\x01[',    '\xe2y' : u'\xfd',     '\xe2z' : u'\x01z',
    '\xe2E' : u'\xc9',     '\xe2G' : u'\x01\xf4', '\xe2A' : u'\xc1',
    '\xe2C' : u'\x01\x06', '\xe2L' : u'\x019',    '\xe2M' : u'\x1e>',
    '\xe2N' : u'\x01C',    '\xe2O' : u'\xd3',     '\xe2I' : u'\xcd',
    '\xf3u' : u'\x1es',    '\xe2K' : u'\x1e0',    '\xe2U' : u'\xda',
    '\xe2W' : u'\x1e\x82', '\xe2P' : u'\x1eT',    '\xf0l' : u'\x01<',
    '\xe2R' : u'\x01T',    '\xe2S' : u'\x01Z',    '\xea\xad' : u'\x01n',
    '\xf0k' : u'\x017',    '\xe2Y' : u'\xdd',     '\xe2Z' : u'\x01y',
    '\xf2A' : u'\x1e\xa0', '\xe7w' : u'\x1e\x87', '\xe2\xa5' : u'\x01\xfc',
    '\xe7t' : u'\x1ek',    '\xe7s' : u'\x1ea',    '\xe7r' : u'\x1eY',
    '\xf0G' : u'\x01"',    '\xe7p' : u'\x1eW',    '\xf2k' : u'\x1e3',
    '\xf2I' : u'\x1e\xca', '\xe7z' : u'\x01|',    '\xe7y' : u'\x1e\x8f',
    '\xe7x' : u'\x1e\x8b', '\xe7g' : u'\x01!',    '\xe2\xb5' : u'\x01\xfd',
    '\xe7e' : u'\x01\x17', '\xe7d' : u'\x1e\x0b', '\xe7c' : u'\x01\x0b',
    '\xe7b' : u'\x1e\x03', '\xf0D' : u'\x1e\x10', '\xe7n' : u'\x1eE',
    '\xe7m' : u'\x1eA',    '\xf0N' : u'\x01E',    '\xf2N' : u'\x1eF',
    '\xf0L' : u'\x01;',    '\xe7h' : u'\x1e#',    '\xe7W' : u'\x1e\x86',
    '\xf0s' : u'\x01_',    '\xe7T' : u'\x1ej',    '\xe7S' : u'\x1e`',
    '\xe7R' : u'\x1eX',    '\xf0t' : u'\x01c',    '\xe7P' : u'\x1eV',
    '\xf2H' : u'\x1e$',    '\xf2Y' : u'\x1e\xf4', '\xe7Z' : u'\x01{',
    '\xe7Y' : u'\x1e\x8e', '\xe7X' : u'\x1e\x8a', '\xe7G' : u'\x01 ',
    '\xe7F' : u'\x1e\x1e', '\xe7E' : u'\x01\x16', '\xe7D' : u'\x1e\n',
    '\xe7C' : u'\x01\n',   '\xe7B' : u'\x1e\x02', '\xf0d' : u'\x1e\x11',
    '\xe7N' : u'\x1eD',    '\xe7M' : u'\x1e@',    '\xf2K' : u'\x1e2',
    '\xf0n' : u'\x01F',    '\xe7I' : u'\x010',    '\xe7H' : u'\x1e"',
    '\xf2t' : u'\x1em',    '\xe8x' : u'\x1e\x8d', '\xe0a' : u'\x1e\xa3',
    '\xf1U' : u'\x01r',    '\xe0e' : u'\x1e\xbb', '\xe0i' : u'\x1e\xc9',
    '\xf9h' : u'\x1e+',    '\xe0o' : u'\x1e\xcf', '\xe8t' : u'\x1e\x97',
    '\xe8u' : u'\xfc',     '\xf1A' : u'\x01\x04', '\xe8h' : u"\x1e'",
    '\xe8i' : u'\xef',     '\xf1E' : u'\x01\x18', '\xe8o' : u'\xf6',
    '\xe0u' : u'\x1e\xe7', '\xf1I' : u'\x01.',    '\xe0y' : u'\x1e\xf7',
    '\xf1O' : u'\x01\xea', '\xe8e' : u'\xeb',     '\xf9H' : u'\x1e*',
    '\xe8X' : u'\x1e\x8c', '\xe0A' : u'\x1e\xa2', '\xf1u' : u'\x01s',
    '\xe0E' : u'\x1e\xba', '\xe0I' : u'\x1e\xc8', '\xe0O' : u'\x1e\xce',
    '\xe8U' : u'\xdc',     '\xf1a' : u'\x01\x05', '\xe8H' : u'\x1e&',
    '\xe8I' : u'\xcf',     '\xf1e' : u'\x01\x19', '\xe8O' : u'\xd6',
    '\xe0U' : u'\x1e\xe6', '\xf1i' : u'\x01/',    '\xe0Y' : u'\x1e\xf6',
    '\xf0r' : u'\x01W',    '\xf1o' : u'\x01\xeb', '\xe8E' : u'\xcb',
    '\xf0R' : u'\x01V',    '\xe5o' : u'\x01M',    '\xe5i' : u'\x01+',
    '\xf2D' : u'\x1e\x0c', '\xeeO' : u'\x01P',    '\xe5e' : u'\x01\x13',
    '\xe5g' : u'\x1e!',    '\xe5a' : u'\x01\x01', '\xf2y' : u'\x1e\xf5',
    '\xe8w' : u'\x1e\x85', '\xf2z' : u'\x1e\x93', '\xe5\xb5' : u'\x01\xe3',  
    '\xe5u' : u'\x01k',    '\xeeU' : u'\x01p',    '\xf2d' : u'\x1e\r',
    '\xe5O' : u'\x01L',    '\xe8a' : u'\xe4',     '\xe5I' : u'\x01*',
    '\xf0T' : u'\x01b',    '\xeeo' : u'\x01Q',    '\xe5E' : u'\x01\x12',
    '\xe5G' : u'\x1e ',    '\xe5A' : u'\x01',     '\xf2l' : u'\x1e7',
    '\xf0C' : u'\xc7',     '\xf0S' : u'\x01^',    '\xe5U' : u'\x01j',
    '\xf2B' : u'\x1e\x04', '\xeeu' : u'\x01q',    '\xf2a' : u'\x1e\xa1',
    '\xf2w' : u'\x1e\x89', '\xf2U' : u'\x1e\xe4', '\xe6u' : u'\x01m',
    '\xe6a' : u'\x01\x03', '\xe8Y' : u'\x01x',    '\xe6e' : u'\x01\x15',
    '\xe6g' : u'\x01\x1f', '\xe6i' : u'\x01-',    '\xf2n' : u'\x1eG',
    '\xe6o' : u'\x01O',    '\xe6U' : u'\x01l',    '\xe7f' : u'\x1e\x1f',
    '\xf2h' : u'\x1e%',    '\xf2i' : u'\x1e\xcb', '\xe6A' : u'\x01\x02',
    '\xe6E' : u'\x01\x14', '\xe6G' : u'\x01\x1e', '\xe6I' : u'\x01,',
    '\xe9O' : u'\x01\xd1', '\xe6O' : u'\x01N',    '\xf2W' : u'\x1e\x88',
    '\xe3j' : u'\x015',    '\xe3i' : u'\xee',     '\xe3h' : u'\x01%',
    '\xe3o' : u'\xf4',     '\xe3c' : u'\x01\t',   '\xe3a' : u'\xe2',
    '\xe3g' : u'\x01\x1d', '\xe3e' : u'\xea',     '\xe8W' : u'\x1e\x84',
    '\xe3z' : u'\x1e\x91', '\xe3y' : u'\x01w',    '\xf0K' : u'\x016',
    '\xe3s' : u'\x01]',    '\xe3w' : u'\x01u',    '\xf0H' : u'\x1e(',
    '\xe3u' : u'\xfb',     '\xeay' : u'\x1e\x99', '\xe3J' : u'\x014',
    '\xe3I' : u'\xce',     '\xe3H' : u'\x01$',    '\xe3O' : u'\xd4',
    '\xe3C' : u'\x01\x08', '\xe3A' : u'\xc2',     '\xe3G' : u'\x01\x1c',
    '\xf0 ' : u'\xb8',     '\xe3E' : u'\xca',     '\xe3Z' : u'\x1e\x90',
    '\xe3Y' : u'\x01v',    '\xe9A' : u'\x01\xcd', '\xe3S' : u'\x01\\',
    '\xf2s' : u'\x1ec',    '\xe9o' : u'\x01\xd2', '\xf4A' : u'\x1e',
    '\xe3W' : u'\x01t',    '\xe3U' : u'\xdb',     '\xf4a' : u'\x1e\x01',
    '\xe4n' : u'\xf1',     '\xe4o' : u'\xf5',     '\xeaw' : u'\x1e\x98',
    '\xe4i' : u'\x01)',    '\xf2b' : u'\x1e\x05', '\xe5\xa5' : u'\x01\xe2', 
    '\xe4e' : u'\x1e\xbd', '\xf2L' : u'\x1e6',    '\xe4a' : u'\xe3',
    '\xf2m' : u'\x1eC',    '\xe4y' : u'\x1e\xf9', '\xe4v' : u'\x1e}',
    '\xe4u' : u'\x01i',    '\xe4N' : u'\xd1',     '\xe4O' : u'\xd5',
    '\xe8A' : u'\xc4',     '\xe8y' : u'\xff',     '\xe4I' : u'\x01(',
    '\xe4E' : u'\x1e\xbc', '\xe4A' : u'\xc3',     '\xe9a' : u'\x01\xce',
    '\xe4Y' : u'\x1e\xf8', '\xe4V' : u'\x1e|',    '\xe4U' : u'\x01h',
}

UTOA = {
    u'\xfe ' : '\xeb',     u'\xcb' : '\xe8E',     u'\xdb' : '\xe3U',
    u'\xeb' : '\xe8e',     u'\xfb' : '\xe3u',     u'\x01\x04' : '\xf1A',
    u'\xb0' : '\xc0',      u'\xc0' : '\xe1A',     u'\xd0' : '\xa3',
    u'\xe0' : '\xe1a',     u'\xf0' : '\xba',      u'\x01\x14' : '\xe6E',
    u'\xa1' : '\xc6',      u'\xdc' : '\xe8U',     u'\x01\xaf' : '\xad', 
    u'\xb1' : '\xab',      u'\xc1' : '\xe2A',     u'\xd1' : '\xe4N',
    u'\x01$' : '\xe3H',    u'\xe1' : '\xe2a',     u'\xf1' : '\xe4n',
    u'\x01' : '\xe5A',     u'\x03\t' : '\xe0',    u'\x014' : '\xe3J',
    u'\xc6' : '\xa5',      u'\xd6' : '\xe8O',     u'\xe6' : '\xb5',
    u'\xfc' : '\xe8u',     u'\xf6' : '\xe8o',     u'\x1e\xc8' : '\xe0I',
    u'\x1e\xc9' : '\xe0i', u'\x1e\xca' : '\xf2I', u'\x1e\xcb' : '\xf2i',
    u'\x1e\xcc' : '\xf2O', u'\x1e\xcd' : '\xf2o', u'\x1e\xce' : '\xe0O',
    u'\x1e\xcf' : '\xe0o', u'\x1e\xf8' : '\xe4Y', u'\x1e\xf9' : '\xe4y',
    u'\x1e\xf2' : '\xe1Y', u'\x1e\xf3' : '\xe1y', u'\x1e\xf4' : '\xf2Y',
    u'\x1e\xf5' : '\xf2y', u'\x1e\xf6' : '\xe0Y', u'\x1e\xf7' : '\xe0y',
    u'\xb7' : '\xa8',      u'\x1e\xe4' : '\xf2U', u'\x1e\xe5' : '\xf2u',
    u'\x1e\xe6' : '\xe0U', u'\x1e\xe7' : '\xe0u', u'\x1e\x98' : '\xeaw',
    u'\x1e\x99' : '\xeay', u'\xc7' : '\xf0C',     u'\x1e\x90' : '\xe3Z',
    u'\x1e\x91' : '\xe3z', u'\x1e\x92' : '\xf2Z', u'\x1e\x93' : '\xf2z',
    u'\x1e\x97' : '\xe8t', u'\x1e\x88' : '\xf2W', u'\x1e\x89' : '\xf2w',
    u'\x1e\x8a' : '\xe7X', u'\x1e\x8b' : '\xe7x', u'\x1e\x8c' : '\xe8X',
    u'\x1e\x8d' : '\xe8x', u'\x1e\x8e' : '\xe7Y', u'\x1e\x8f' : '\xe7y',
    u'\x1e\x80' : '\xe1W', u'\x1e\x81' : '\xe1w', u'\x1e\x82' : '\xe2W',
    u'\x1e\x83' : '\xe2w', u'\x1e\x84' : '\xe8W', u'\x1e\x85' : '\xe8w',
    u'\x1e\x86' : '\xe7W', u'\x1e\x87' : '\xe7w', u'\x1e\xb8' : '\xf2E',
    u'\x1e\xb9' : '\xf2e', u'\x1e\xba' : '\xe0E', u'\x1e\xbb' : '\xe0e',
    u'\x1e\xbc' : '\xe4E', u'\x1e\xbd' : '\xe4e', u'\xe7' : '\xf0c',
    u'\x1e\xa0' : '\xf2A', u'\x1e\xa1' : '\xf2a', u'\x1e\xa2' : '\xe0A',
    u'\x1e\xa3' : '\xe0a', u'\x1eX' : '\xe7R',    u'\x1eY' : '\xe7r',
    u'\x1eZ' : '\xf2R',    u'\x1e[' : '\xf2r',    u'\x1eT' : '\xe2P',
    u'\x1eU' : '\xe2p',    u'\x1eV' : '\xe7P',    u'\x1eW' : '\xe7p',
    u'\x1e@' : '\xe7M',    u'\x1eA' : '\xe7m',    u'\x1eB' : '\xf2M',
    u'\x1eC' : '\xf2m',    u'\x1eD' : '\xe7N',    u'\x1eE' : '\xe7n',
    u'\x1eF' : '\xf2N',    u'\x1eG' : '\xf2n',    u'\x1e|' : '\xe4V',
    u'\x1e}' : '\xe4v',    u'\x1e~' : '\xf2V',    u'\x1e\x7f' : '\xf2v',
    u'\x1er' : '\xf3U',    u'\x1es' : '\xf3u',    u'\x1ej' : '\xe7T',
    u'\x1ek' : '\xe7t',    u'\x1el' : '\xf2T',    u'\x1em' : '\xf2t',
    u'\x1e`' : '\xe7S',    u'\x1ea' : '\xe7s',    u'\x1eb' : '\xf2S',
    u'\x1ec' : '\xf2s',    u'\x1e\x1e' : '\xe7F', u'\x1e\x1f' : '\xe7f',
    u'\x1e\x10' : '\xf0D', u'\x1e\x11' : '\xf0d', u'\xcc' : '\xe1I',
    u'\x1e\n' : '\xe7D',   u'\x1e\x0b' : '\xe7d', u'\x1e\x0c' : '\xf2D',
    u'\x1e\r' : '\xf2d',   u'\x1e\x01' : '\xf4a', u'\x1e\x02' : '\xe7B',
    u'\x1e\x03' : '\xe7b', u'\x1e\x04' : '\xf2B', u'\x1e\x05' : '\xf2b',
    u'\x1e>' : '\xe2M',    u'\x1e?' : '\xe2m',    u'\x1e0' : '\xe2K',
    u'\x1e1' : '\xe2k',    u'\x1e2' : '\xf2K',    u'\x1e3' : '\xf2k',
    u'\xec'  : '\xe1i',    u'\x1e6' : '\xf2L',    u'\x1e7' : '\xf2l',
    u'\x1e(' : '\xf0H',    u'\x1e)' : '\xf0h',    u'\x1e*' : '\xf9H',
    u'\x1e+' : '\xf9h',    u'\x1e ' : '\xe5G',    u'\x1e!' : '\xe5g',
    u'\x1e"' : '\xe7H',    u'\x1e#' : '\xe7h',    u'\x1e$' : '\xf2H',
    u'\x1e%' : '\xf2h',    u'\x1e&' : '\xe8H',    u"\x1e'" : '\xe8h',
    u'\xcd' : '\xe2I',     u'\xdd' : '\xe2Y',     u'\xed' : '\xe2i',
    u'\xfd' : '\xe2y',     u'\xc2' : '\xe3A',     u'\xd2' : '\xe1O',
    u'\xe2' : '\xe3a',     u'\xf2' : '\xe1o',     u'\xa3' : '\xb9',
    u'\x03\x0b' : '\xee',  u'\x03\n' : '\xea',    u'\xc3' : '\xe4A',
    u'\x03\x0c' : '\xe9',  u'\x03\x03' : '\xe4',  u'\x03\x02' : '\xe3',
    u'\x03\x01' : '\xe2',  u'\x03\x07' : '\xe7',  u'\x03\x06' : '\xe6',
    u'\x03\x04' : '\xe5',  u'\xd3' : '\xe2O',     u'\x03\x1c' : '\xf8',
    u'\x03\x13' : '\xfe',  u'\x03\x10' : '\xef',  u'\x03\x15' : '\xed',
    u'\xe3' : '\xe4a',     u'\x03(' : '\xf1',     u'\x03.' : '\xf9',
    u'\x03#' : '\xf2',     u"\x03'" : '\xf0',     u'\x03&' : '\xf7',
    u'\x03%' : '\xf4',     u'\x03$' : '\xf3',     u'\xf3' : '\xe2o',
    u'\x033' : '\xf5',     u'\x032' : '\xf6',     u'\x03' : '\xe1',
    u'\xb8' : '\xf0 ',     u'\xc8' : '\xe1E',     u'\xd8' : '\xa2',
    u'\xe8' : '\xe1e',     u'\xf8' : '\xb2',      u'\x1e' : '\xf4A',
    u'\xa9' : '\xc3',      u'\x02\xbe' : '\xae',  u'\x02\xbf' : '\xb0',
    u'\x02\xb9' : '\xa7',  u'\x02\xba' : '\xb7',  u'\xc9' : '\xe2E',
    u'\xd9' : '\xe1U',     u'\xfe!' : '\xec',     u'\xfe"' : '\xfa',
    u'\xfe#' : '\xfb',     u'\xe9' : '\xe2e',     u'\xf9' : '\xe1u',
    u'\xae' : '\xaa',      u'\xce' : '\xe3I',     u'\xde' : '\xa4',
    u'\xee' : '\xe3i',     u'\xfe' : '\xb4',      u'\x01\xcd' : '\xe9A',
    u'\x01\xcf' : '\xe9I', u'\x01\xce' : '\xe9a', u'\x01\xd1' : '\xe9O',
    u'\x01\xd0' : '\xe9i', u'\x01\xd3' : '\xe9U', u'\x01\xd2' : '\xe9o',
    u'\x01\xd4' : '\xe9u', u'\x01\xe9' : '\xe9k', u'\x01\xe3' : '\xe5\xb5', 
    u'\x01\xe7' : '\xe9g', u'\x01\xe6' : '\xe9G', u'\x01\xe2' : '\xe5\xa5',
    u'\x01\xe8' : '\xe9K', u'\x01\xeb' : '\xf1o', u'\x01\xea' : '\xf1O',
    u'\x01\xf0' : '\xe9j', u'\x01\xf5' : '\xe2g', u'\x01\xf4' : '\xe2G',
    u'\xbf' : '\xc5',      u'\x01\xa1' : '\xbc',  u'\x01\xfd' : '\xe2\xb5', 
    u'\xcf' : '\xe8I',     u'\xdf' : '\xcf',      u'\x01\xfc' : '\xe2\xa5', 
    u'\x01\xa0' : '\xac',  u'\xef' : '\xe8i',     u'\x01\xb0' : '\xbd',
    u'\xff' : '\xe8y',     u'\x01A' : '\xa1',     u'\x01C' : '\xe2N',
    u'\x01B' : '\xb1',     u'\x01E' : '\xf0N',    u'\x01D' : '\xe2n',
    u'\x01G' : '\xe9N',    u'\x01F' : '\xf0n',    u'\x01H' : '\xe9n',
    u'\x01M' : '\xe5o',    u'\x01L' : '\xe5O',    u'\x01O' : '\xe6o',
    u'\x01N' : '\xe6O',    u'\x01Q' : '\xeeo',    u'\x01P' : '\xeeO',
    u'\x01S' : '\xb6',     u'\x01R' : '\xa6',     u'\x01U' : '\xe2r',
    u'\x01T' : '\xe2R',    u'\x01W' : '\xf0r',    u'\x01V' : '\xf0R',
    u'\x01Y' : '\xe9r',    u'\x01X' : '\xe9R',    u'\x01[' : '\xe2s',
    u'\x01Z' : '\xe2S',    u'\x01]' : '\xe3s',    u'\x01\\' : '\xe3S',
    u'\x01_' : '\xf0s',    u'\x01^' : '\xf0S',    u'\x01a' : '\xe9s',
    u'\x01`' : '\xe9S',    u'\x01c' : '\xf0t',    u'\x01b' : '\xf0T',
    u'\x01e' : '\xe9t',    u'\x01d' : '\xe9T',    u'\x01i' : '\xe4u',
    u'\x01h' : '\xe4U',    u'\x01k' : '\xe5u',    u'\x01j' : '\xe5U',
    u'\x01m' : '\xe6u',    u'\x01l' : '\xe6U',    u'\x01o' : '\xeau',
    u'\x01n' : '\xea\xad', u'\x01q' : '\xeeu',    u'\x01p' : '\xeeU',
    u'\x01s' : '\xf1u',    u'\x01r' : '\xf1U',    u'\x01u' : '\xe3w',
    u'\x01t' : '\xe3W',    u'\x01w' : '\xe3y',    u'\x01v' : '\xe3Y',
    u'\x01y' : '\xe2Z',    u'\x01x' : '\xe8Y',    u'\x01{' : '\xe7Z',
    u'\x01z' : '\xe2z',    u'\x01}' : '\xe9Z',    u'\x01|' : '\xe7z',
    u'\x01~' : '\xe9z',    u'\x01\x01' : '\xe5a', u'\x01\x03' : '\xe6a',
    u'\x01\x02' : '\xe6A', u'\x01\x05' : '\xf1a', u'\xc4' : '\xe8A',
    u'\x01\x07' : '\xe2c', u'\x01\x06' : '\xe2C', u'\x01\t' : '\xe3c',
    u'\x01\x08' : '\xe3C', u'\x01\x0b' : '\xe7c', u'\x01\n' : '\xe7C',
    u'\x01\r' : '\xe9c',   u'\x01\x0c' : '\xe9C', u'\x01\x0f' : '\xe9d',
    u'\x01\x0e' : '\xe9D', u'\x01\x11' : '\xb3',  u'\x01\x10' : '\xa3',
    u'\x01\x13' : '\xe5e', u'\x01\x12' : '\xe5E', u'\x01\x15' : '\xe6e',
    u'\xd4' : '\xe3O',     u'\x01\x17' : '\xe7e', u'\x01\x16' : '\xe7E',
    u'\x01\x19' : '\xf1e', u'\x01\x18' : '\xf1E', u'\x01\x1b' : '\xe9e',
    u'\x01\x1a' : '\xe9E', u'\x01\x1d' : '\xe3g', u'\x01\x1c' : '\xe3G',
    u'\x01\x1f' : '\xe6g', u'\x01\x1e' : '\xe6G', u'\x01!' : '\xe7g',
    u'\x01 '  : '\xe7G',   u'\x01#' : '\xf0g',    u'\x01"' : '\xf0G',
    u'\x01%' : '\xe3h',    u'\xe4' : '\xe8a',     u'\x01)' : '\xe4i',
    u'\x01(' : '\xe4I',    u'\x01+' : '\xe5i',    u'\x01*' : '\xe5I',
    u'\x01-' : '\xe6i',    u'\x01,' : '\xe6I',    u'\x01/' : '\xf1i',
    u'\x01.' : '\xf1I',    u'\x011' : '\xb8',     u'\x010' : '\xe7I',
    u'\x015' : '\xe3j',    u'\xf4' : '\xe3o',     u'\x017' : '\xf0k',
    u'\x016' : '\xf0K',    u'\x019' : '\xe2L',    u'\x01;' : '\xf0L',
    u'\x01:' : '\xe2l',    u'\x01=' : '\xe9L',    u'\x01<' : '\xf0l',
    u'\x01>' : '\xe9l',    u'\xc5' : '\xeaA',     u'\xd5' : '\xe4O',
    u'\xe5' : '\xeaa',     u'\xf5' : '\xe4o',     u'\xca' : '\xe3E',
    u'\xda' : '\xe2U',     u'\xea' : '\xe3e',     u'\xfa' : '\xe2u',
    }

#-------------------------------------------------------------------------
#
# ansel_to_utf8
#
#-------------------------------------------------------------------------
def ansel_to_utf8(inp):
    """Converts an ANSEL encoded string to UTF8"""

    buff = cStringIO.StringIO()
    while inp:
        char0 = ord(inp[0])
        if char0 <= 31:
            head = u' '
            inp = inp[1:]
        elif char0 > 127:
            char2 = inp[0:2]
            char1 = inp[0]
            if TWOBYTE.has_key(char2):
                head = TWOBYTE[char2]
                inp = inp[2:]
            elif ONEBYTE.has_key(char1):
                head = ONEBYTE[char1]
                inp = inp[1:]
            else:
                head = u'\xff\xfd'
                inp = inp[1:]
        else:
            head = inp[0]
            inp = inp[1:]
        buff.write(head)
    ans = unicode(buff.getvalue())
    buff.close()
    return ans

#-------------------------------------------------------------------------
#
# utf8_to_ansel
#
#-------------------------------------------------------------------------
def utf8_to_ansel(inp):
    """Converts an UTF8 encoded string to ANSEL"""
    
    if type(inp) != unicode:
        inp = unicode(inp)
    buff = cStringIO.StringIO()
    while inp:
        char0 = ord(inp[0])
        if char0 <= 3 or char0 == 0x1e or char0 >= 0xf3:
            try:
                head = UTOA[inp[0:2]]
                inp = inp[2:]
            except:
                try:
                    head = UTOA[inp[0:1]]
                    inp = inp[1:]
                except:
                    head = '?'
                    inp = inp[1:]
        elif char0 > 127:
            try:
                head = UTOA[inp[0:1]]
                inp = inp[1:]
            except:
                head = '?'
                inp = inp[1:]
        else:
            head = inp[0]
            inp = inp[1:]
        buff.write(head)
    ans = buff.getvalue()
    buff.close()
    return ans

