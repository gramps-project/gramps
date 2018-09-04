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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Unittest for export to VCard
"""
import unittest
import time
import subprocess
import sys
import os
import xml.etree.ElementTree as ET

from ...lib.libgrampsxml import GRAMPS_XML_VERSION
from gramps.version import VERSION
from ..exportvcard import VCardWriter

class VCardCheck(unittest.TestCase):
    def setUp(self):
        self.expect = ["BEGIN:VCARD", "VERSION:3.0",
                       "PRODID:-//Gramps//NONSGML Gramps %s//EN" % VERSION,
                       "FN:Lastname", "N:Lastname;;;;",
                       "SORT-STRING:" + "Lastname".ljust(55), "END:VCARD"]
        date = time.localtime(time.time())
        self.input_list = ["BEGIN:VCARD", "VERSION:3.0", "FN:Lastname",
                           "N:Lastname;;;;", "END:VCARD"]
        self.header = """<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE database PUBLIC "-//GRAMPS//DTD GRAMPS XML %s//EN"
            "http://gramps-project.org/xml/%s/grampsxml.dtd">""" % \
            (GRAMPS_XML_VERSION, GRAMPS_XML_VERSION)
        strng = """<database xmlns="http://gramps-project.org/xml/%s/">
            <header>
            <created date="%04d-%02d-%02d" version="%s"/>
            <researcher/>
            </header>
            <people>
            <person id="I0000" handle="_0000">
            <name type="Birth Name">
            <surname>Lastname</surname>
            </name>
            </person>
            </people>
            </database>""" % \
            (GRAMPS_XML_VERSION, date[0], date[1], date[2], VERSION)
        namespace = "http://gramps-project.org/xml/%s/" % GRAMPS_XML_VERSION
        ET.register_namespace("", namespace)
        self.database = ET.XML(strng)
        self.people = self.database[1]
        self.person = self.people[0]
        self.name = self.person[0]
        self.lastname = self.name[0]

    def do_case(self, input_doc, expect_str, debug=False):
        if debug:
            print(ET.tostring(input_doc))

        gcmd = [sys.executable, 'Gramps.py',
                '-i', '-', '-f', 'gramps',
                '-e', '-', '-f', 'vcf']
        process = subprocess.Popen(gcmd,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   env=os.environ)
        input_str = (self.header.encode('utf-8') +
                     ET.tostring(input_doc, encoding='utf-8'))
        result_str, err_str = process.communicate(input_str)

        separator = '\r' + os.linesep
        expect_str = separator.join(expect_str) + (separator * 2)

        if debug:
            print(err_str)
            print(result_str)
            print(expect_str)
        self.assertEqual(result_str, expect_str.encode('utf-8'))

    def test_base(self):
        self.do_case(self.database,
                     self.expect)

    def test_esc_string_none(self):
        self.assertEqual(VCardWriter.esc("nothing"), "nothing")

    def test_esc_string_all(self):
        self.assertEqual(VCardWriter.esc("backslash\\_comma,_semicolon;"),
                         "backslash\\\\_comma\\,_semicolon\\;")

    def test_esc_string_list(self):
        self.assertEqual(VCardWriter.esc(["comma,", "semicolon;"]),
                                         ["comma\\,", "semicolon\\;"])

    def test_esc_string_tuple(self):
        self.assertEqual(VCardWriter.esc(("comma,", "semicolon;")),
                                         ("comma\\,", "semicolon\\;"))

    def test_esc_string_wrongtype(self):
        self.assertRaises(TypeError, VCardWriter.esc,
                          {"comma,":"semicolon;"})

    def test_write_formatted_name_title(self):
        ET.SubElement(self.name, "title").text = 'Sir.'
        self.expect[3] = "FN:Sir. Lastname"
        self.expect[4] = "N:Lastname;;;Sir.;"
        self.do_case(self.database, self.expect)

    def test_write_name_multiple_surname(self):
        self.lastname.text = "Oranje"
        self.lastname.set("prefix", "van")
        ET.SubElement(self.name, "surname").text = "Nassau"
        self.expect[3] = "FN:van Oranje Nassau"
        self.expect[4] = "N:van Oranje,Nassau;;;;"
        self.expect[5] = "SORT-STRING:" + "Oranje".ljust(55)
        self.do_case(self.database, self.expect)

    def test_write_name_callname(self):
        # callname not in first names!
        ET.SubElement(self.name, "first").text = "B C"
        ET.SubElement(self.name, "call").text = "A"
        self.expect[3] = "FN:B C Lastname"
        self.expect[4] = "N:Lastname;A;B,C;;"
        self.expect[5] = "SORT-STRING:" + "Lastname".ljust(25) + "B C".ljust(30)
        self.do_case(self.database, self.expect)

    def test_write_name_callname_in_addnames(self):
        ET.SubElement(self.name, "first").text = "A B C"
        ET.SubElement(self.name, "call").text = "B"
        self.expect[3] = "FN:A B C Lastname"
        self.expect[4] = "N:Lastname;B;A,C;;"
        self.expect[5] = "SORT-STRING:" + "Lastname".ljust(25) + "A B C".ljust(30)
        self.do_case(self.database, self.expect)

    def test_write_name_no_callname(self):
        ET.SubElement(self.name, "first").text = "A B C"
        self.expect[3] = "FN:A B C Lastname"
        self.expect[4] = "N:Lastname;A;B,C;;"
        self.expect[5] = "SORT-STRING:" + "Lastname".ljust(25) + "A B C".ljust(30)
        self.do_case(self.database, self.expect)

    def test_write_name_no_additional_names(self):
        ET.SubElement(self.name, "first").text = "A"
        self.expect[3] = "FN:A Lastname"
        self.expect[4] = "N:Lastname;A;;;"
        self.expect[5] = "SORT-STRING:" + "Lastname".ljust(25) + "A".ljust(30)
        self.do_case(self.database, self.expect)

    def test_write_name_honprefix(self):
        ET.SubElement(self.name, "title").text = "Sir"
        self.expect[3] = "FN:Sir Lastname"
        self.expect[4] = "N:Lastname;;;Sir;"
        self.expect[5] = "SORT-STRING:" + "Lastname".ljust(55)
        self.do_case(self.database, self.expect)

    def test_write_name_honsuffix(self):
        ET.SubElement(self.name, "suffix").text = "Jr."
        self.expect[3] = "FN:Lastname\\, Jr."
        self.expect[4] = "N:Lastname;;;;Jr."
        self.expect[5] = "SORT-STRING:" + "Lastname".ljust(55)+ "Jr."
        self.do_case(self.database, self.expect)


    def test_nicknames_regular(self):
        attribs = {'type': 'Birth Name', 'alt': '1'}
        name = ET.SubElement(self.person, "name", attrib=attribs)
        ET.SubElement(name, 'nick').text = 'Nick'
        name = ET.SubElement(self.person, "name", attrib=attribs)
        ET.SubElement(name, 'nick').text = 'N.'
        self.expect.insert(6, "NICKNAME:Nick,N.")
        self.do_case(self.database, self.expect)

    def test_nicknames_primary_nick(self):
        ET.SubElement(self.name, 'nick').text = 'Nick'
        attribs = {'type': 'Birth Name', 'alt': '1'}
        name = ET.SubElement(self.person, "name", attrib=attribs)
        ET.SubElement(name, 'nick').text = 'N.'
        self.expect.insert(6, "NICKNAME:Nick,N.")
        self.do_case(self.database, self.expect)

    def test_write_birthdate_regular(self):
        events = ET.Element('events')
        self.database.insert(1, events)
        attribs = {'handle': '_e0000', 'id': 'E0000'}
        event = ET.SubElement(events, 'event', attrib=attribs)
        ET.SubElement(event, 'type').text = 'Birth'
        ET.SubElement(event, 'dateval', val='2001-02-28')
        attribs = {'hlink': '_e0000', 'role': 'Primary'}
        ET.SubElement(self.person, 'eventref', attrib=attribs)
        self.expect.insert(6, "BDAY:2001-02-28")
        self.do_case(self.database, self.expect)

    def test_write_birthdate_empty(self):
        events = ET.Element('events')
        self.database.insert(1, events)
        attribs = {'handle': '_e0000', 'id': 'E0000'}
        event = ET.SubElement(events, 'event', attrib=attribs)
        ET.SubElement(event, 'type').text = 'Birth'
        attribs = {'hlink': '_e0000', 'role': 'Primary'}
        ET.SubElement(self.person, 'eventref', attrib=attribs)
        self.do_case(self.database, self.expect)

    def test_write_birhtdate_textonly(self):
        events = ET.Element('events')
        self.database.insert(1, events)
        attribs = {'handle': '_e0000', 'id': 'E0000'}
        event = ET.SubElement(events, 'event', attrib=attribs)
        ET.SubElement(event, 'type').text = 'Birth'
        ET.SubElement(event, 'dateval', val='Christmas 2001')
        attribs = {'hlink': '_e0000', 'role': 'Primary'}
        ET.SubElement(self.person, 'eventref', attrib=attribs)
        self.do_case(self.database, self.expect)

    def test_write_birthdate_span(self):
        events = ET.Element('events')
        self.database.insert(1, events)
        attribs = {'handle': '_e0000', 'id': 'E0000'}
        event = ET.SubElement(events, 'event', attrib=attribs)
        ET.SubElement(event, 'type').text = 'Birth'
        attribs = {'start': '2001-02-28', 'stop': '2002-02-28'}
        ET.SubElement(event, 'datespan', attrib=attribs)
        attribs = {'hlink': '_e0000', 'role': 'Primary'}
        ET.SubElement(self.person, 'eventref', attrib=attribs)
        self.do_case(self.database, self.expect)

    def test_write_birthdate_range(self):
        events = ET.Element('events')
        self.database.insert(1, events)
        attribs = {'handle': '_e0000', 'id': 'E0000'}
        event = ET.SubElement(events, 'event', attrib=attribs)
        ET.SubElement(event, 'type').text = 'Birth'
        attribs = {'start': '2001-02-28', 'stop': '2002-02-28'}
        ET.SubElement(event, 'daterange', attrib=attribs)
        attribs = {'hlink': '_e0000', 'role': 'Primary'}
        ET.SubElement(self.person, 'eventref', attrib=attribs)
        self.do_case(self.database, self.expect)

    def test_write_addresses_regular(self):
        address = ET.SubElement(self.person, 'address')
        ET.SubElement(address, 'street').text = 'pobox bis street'
        ET.SubElement(address, 'city').text = 'place'
        ET.SubElement(address, 'country').text = 'country'
        ET.SubElement(address, 'state').text = 'province'
        ET.SubElement(address, 'postal').text = 'zip'
        self.expect.insert(6, "ADR:;;pobox bis street;place;province;zip;country")
        self.do_case(self.database, self.expect)

    def test_write_addresses_phone(self):
        address = ET.SubElement(self.person, 'address')
        ET.SubElement(address, 'phone').text = '01234-56789'
        self.expect.insert(6, "TEL:01234-56789")
        self.do_case(self.database, self.expect)

    def test_write_urls_email(self):
        attribs = {'type': 'E-mail', 'href': 'me@example.com'}
        ET.SubElement(self.person, 'url', attrib=attribs)
        self.expect.insert(6, "EMAIL:me@example.com")
        self.do_case(self.database, self.expect)

    def test_write_urls_emial_mailto(self):
        attribs = {'type': 'E-mail', 'href': 'mailto:me@example.com'}
        ET.SubElement(self.person, 'url', attrib=attribs)
        self.expect.insert(6, "EMAIL:me@example.com")
        self.do_case(self.database, self.expect)

    def test_write_urls_url(self):
        attribs = {'type': 'Web Home', 'href': 'http://www.example.org'}
        ET.SubElement(self.person, 'url', attrib=attribs)
        self.expect.insert(6, "URL:http://www.example.org")
        self.do_case(self.database, self.expect)

    def test_write_occupation_regular(self):
        events = ET.Element('events')
        self.database.insert(1, events)
        attribs = {'handle': '_e0000', 'id': 'E0000'}
        event = ET.SubElement(events, 'event', attrib=attribs)
        ET.SubElement(event, 'type').text = 'Occupation'
        ET.SubElement(event, 'description').text = 'carpenter'
        attribs = {'hlink': '_e0000', 'role': 'Primary'}
        ET.SubElement(self.person, 'eventref', attrib=attribs)
        self.expect.insert(6, "ROLE:carpenter")
        self.do_case(self.database, self.expect)

    def test_write_occupation_lastdate(self):
        events = ET.Element('events')
        self.database.insert(1, events)
        attribs = {'handle': '_e0000', 'id': 'E0000'}
        event = ET.SubElement(events, 'event', attrib=attribs)
        ET.SubElement(event, 'type').text = 'Occupation'
        ET.SubElement(event, 'dateval', val='2011-02-28')
        ET.SubElement(event, 'description').text = 'foreman'
        attribs = {'handle': '_e0001', 'id': 'E0001'}
        event = ET.SubElement(events, 'event', attrib=attribs)
        ET.SubElement(event, 'type').text = 'Occupation'
        ET.SubElement(event, 'dateval', val='2000-09-21')
        ET.SubElement(event, 'description').text = 'carpenter'
        attribs = {'hlink': '_e0000', 'role': 'Primary'}
        ET.SubElement(self.person, 'eventref', attrib=attribs)
        attribs = {'hlink': '_e0001', 'role': 'Primary'}
        ET.SubElement(self.person, 'eventref', attrib=attribs)
        self.expect.insert(6, "ROLE:foreman")
        self.do_case(self.database, self.expect)

if __name__ == "__main__":
    unittest.main()
