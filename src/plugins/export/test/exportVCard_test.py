#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011      Michiel D. Nauta
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
Unittest for export to VCard

To be called from src directory.
"""

# Uses vcf for input, would be better to use Gramps-XML, but import of
# Gramps-XML via stdin is hard.

import unittest
import sys
import os
sys.path.append(os.curdir)
sys.path.append(os.path.join(os.curdir, 'plugins', 'export'))
import subprocess

from const import VERSION
import Errors
import ExportVCard

class VCardCheck(unittest.TestCase):
    def setUp(self):
        self.expect = ["BEGIN:VCARD", "VERSION:3.0", "PRODID:-//Gramps//NONSGML Gramps %s//EN" % VERSION, "FN:Lastname", "N:Lastname;;;;", "SORT-STRING:" + "Lastname".ljust(55), "END:VCARD"]
        self.input_list = ["BEGIN:VCARD", "VERSION:3.0", "FN:Lastname", "N:Lastname;;;;", "END:VCARD"]

    def do_test(self, input_str, expect_str, debug=False):
        process = subprocess.Popen('python gramps.py -i - -f vcf -e - -f vcf',
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        result_str, err_str = process.communicate(input_str)
        if err_str:
            print err_str
        if debug:
            print result_str
            print expect_str
        self.assertEqual(result_str, expect_str)

    def test_base(self):
        self.do_test("\r\n".join(self.input_list),
                     "\r\n".join(self.expect) + '\r\n\r\n')

    def test_esc_string_none(self):
        self.assertEqual(ExportVCard.VCardWriter.esc("nothing"), "nothing")

    def test_esc_string_all(self):
        self.assertEqual(ExportVCard.VCardWriter.esc("backslash\\_comma,_semicolon;"),
                         "backslash\\\\_comma\\,_semicolon\\;")

    def test_esc_string_list(self):
        self.assertEqual(ExportVCard.VCardWriter.esc(["comma,", "semicolon;"]),["comma\\,", "semicolon\\;"])

    def test_esc_string_tuple(self):
        self.assertEqual(ExportVCard.VCardWriter.esc(("comma,", "semicolon;")),("comma\\,", "semicolon\\;"))

    def test_esc_string_wrongtype(self):
        self.assertRaises(TypeError, ExportVCard.VCardWriter.esc,
                          {"comma,":"semicolon;"})

    def test_write_formatted_name_title(self):
        self.input_list[3] = "N:Lastname;;;Sir.;"
        self.expect[3] = "FN:Sir. Lastname"
        self.expect[4] = "N:Lastname;;;Sir.;"
        self.do_test("\r\n".join(self.input_list),
                     "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_name_multiple_surname(self):
        self.input_list[3] = "N:van Oranje,Nassau;;;;"
        self.expect[3] = "FN:van Oranje Nassau"
        self.expect[4] = "N:van Oranje,Nassau;;;;"
        self.expect[5] = "SORT-STRING:" + "Oranje".ljust(55)
        self.do_test("\r\n".join(self.input_list),
                     "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_name_callname(self):
        self.input_list[2] = "FN:A B C Lastname"
        self.input_list[3] = "N:Lastname;B;A,C;;"
        self.expect[3] = "FN:A B C Lastname"
        self.expect[4] = "N:Lastname;B;A,C;;"
        self.expect[5] = "SORT-STRING:" + "Lastname".ljust(25) + "A B C".ljust(30)
        self.do_test("\r\n".join(self.input_list),
                     "\r\n".join(self.expect) + '\r\n\r\n')

    #def test_write_name_callname_in_addnames(self):
        # impossible to test with VCF input, need XML

    def test_write_name_no_callname(self):
        self.input_list[2] = "FN:A B C Lastname"
        self.input_list[3] = "N:Lastname;A;B,C;;"
        self.expect[3] = "FN:A B C Lastname"
        self.expect[4] = "N:Lastname;A;B,C;;"
        self.expect[5] = "SORT-STRING:" + "Lastname".ljust(25) + "A B C".ljust(30)
        self.do_test("\r\n".join(self.input_list),
                     "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_name_no_additional_names(self):
        self.input_list[2] = "FN:A Lastname"
        self.input_list[3] = "N:Lastname;A;;;"
        self.expect[3] = "FN:A Lastname"
        self.expect[4] = "N:Lastname;A;;;"
        self.expect[5] = "SORT-STRING:" + "Lastname".ljust(25) + "A".ljust(30)
        self.do_test("\r\n".join(self.input_list),
                     "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_name_honprefix(self):
        self.input_list[3] = "N:Lastname;;;Sir;"
        self.expect[3] = "FN:Sir Lastname"
        self.expect[4] = "N:Lastname;;;Sir;"
        self.expect[5] = "SORT-STRING:" + "Lastname".ljust(55)
        self.do_test("\r\n".join(self.input_list),
                     "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_name_honsuffix(self):
        self.input_list[3] = "N:Lastname;;;;Jr."
        self.expect[3] = "FN:Lastname\, Jr."
        self.expect[4] = "N:Lastname;;;;Jr."
        self.expect[5] = "SORT-STRING:" + "Lastname".ljust(55)+ "Jr."
        self.do_test("\r\n".join(self.input_list),
                     "\r\n".join(self.expect) + '\r\n\r\n')


    def test_nicknames_regular(self):
        self.input_list.insert(4, "NICKNAME:Nick,N.")
        self.expect.insert(6, "NICKNAME:Nick,N.")
        self.do_test("\r\n".join(self.input_list),
                     "\r\n".join(self.expect) + '\r\n\r\n')

    #def test_nicknames_primary_nick(self)
        # impossible to test with VCF input, need XML
    
    def test_write_birthdate_regular(self):
        self.input_list.insert(4, "BDAY:2001-02-28")
        self.expect.insert(6, "BDAY:2001-02-28")
        self.do_test("\r\n".join(self.input_list),
                     "\r\n".join(self.expect) + '\r\n\r\n')

    #def test_write_birthdate_empty(self):
    #def test_write_birhtdate_textonly(self):
    #def test_write_birthdate_span(self):
    #def test_write_birthdate_range(self):
        # impossible to test with VCF input, need XML

    def test_write_addresses_regular(self):
        self.input_list.insert(4, "ADR:pobox;bis;street;place;province;zip;country")
        self.expect.insert(6, "ADR:;;pobox bis street;place;province;zip;country")
        self.do_test("\r\n".join(self.input_list),
                     "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_addresses_phone(self):
        self.input_list.insert(4, "TEL:01234-56789")
        self.expect.insert(6, "TEL:01234-56789")
        self.do_test("\r\n".join(self.input_list),
                     "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_urls_email(self):
        self.input_list.insert(4, "EMAIL:me@example.com")
        self.expect.insert(6, "EMAIL:me@example.com")
        self.do_test("\r\n".join(self.input_list),
                     "\r\n".join(self.expect) + '\r\n\r\n')

    #def test_write_urls_emial_mailto(self):
        # impossible to test with VCF input, need XML

    def test_write_urls_url(self):
        self.input_list.insert(4, "URL:http://www.example.org")
        self.expect.insert(6, "URL:http://www.example.org")
        self.do_test("\r\n".join(self.input_list),
                     "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_occupation_regular(self):
        self.input_list.insert(4, "ROLE:carpenter")
        self.expect.insert(6, "ROLE:carpenter")
        self.do_test("\r\n".join(self.input_list),
                     "\r\n".join(self.expect) + '\r\n\r\n')

    #def test_write_occupation_lastdate(self):
        # impossible to test with VCF input, need XML

if __name__ == "__main__":
    unittest.main()
