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
Unittest of import of VCard
"""

# in case of a failing test, add True as last parameter to do_case to see the output.

import unittest
import sys
import os
import time
import subprocess
import xml.etree.ElementTree as ET

from gramps.plugins.lib.libgrampsxml import GRAMPS_XML_VERSION
from gramps.version import VERSION
from gramps.plugins.importer.importvcard import VCardParser, fitin, splitof_nameprefix

class VCardCheck(unittest.TestCase):
    def setUp(self):
        date = time.localtime(time.time())
        self.header = """<database xmlns="http://gramps-project.org/xml/%s/">
            <header>
            <created date="%04d-%02d-%02d" version="%s"/>
            <researcher/>
            </header>""" % \
            (GRAMPS_XML_VERSION, date[0], date[1], date[2], VERSION)
        expect_str = self.header + """<people><person handle="I0000" """ \
                """id="I0000"><gender>U</gender><name type="Birth Name">""" \
                """<surname>Lastname</surname></name></person></people></database>"""
        namespace = "http://gramps-project.org/xml/%s/" % GRAMPS_XML_VERSION
        ET.register_namespace("", namespace)
        self.gramps = ET.XML(expect_str)
        self.person = self.gramps[1][0]
        self.name = self.person[1]
        self.vcard = ["BEGIN:VCARD", "VERSION:3.0", "FN:Lastname",
                      "N:Lastname;;;;", "END:VCARD"]

    def canonicalize(self, doc):
        handles = {}
        for element in doc.iter("*"):
            gramps_id = element.get('id')
            if gramps_id is not None:
                handles[element.get('handle')] = gramps_id
                element.set('handle', gramps_id)
            hlink = element.get('hlink')
            if hlink is not None:
                element.set('hlink', handles.get(hlink))
            if element.get('change') is not None:
                del element.attrib['change']
            if element.text is not None and not element.text.strip():
                element.text = ''
            if element.tail is not None and not element.tail.strip():
                element.tail = ''

        return ET.tostring(doc, encoding='utf-8')

    def do_case(self, input_str, expect_doc, debug=False):
        if debug:
            print(input_str)

        gcmd = [sys.executable, 'Gramps.py',
                '-d', '.Date', '-d', '.ImportVCard',
                '--config=preferences.eprefix:DEFAULT',
                '-i', '-', '-f', 'vcf',
                '-e', '-', '-f', 'gramps']
        process = subprocess.Popen(gcmd,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   env=os.environ)
        result_str, err_str = process.communicate(input_str.encode("utf-8"))
        if debug:
            print(err_str)
        result_doc = ET.XML(result_str)

        if debug:
            print(self.canonicalize(result_doc))
            print(self.canonicalize(expect_doc))
        self.assertEqual(self.canonicalize(result_doc),
                         self.canonicalize(expect_doc))

    def test_base(self):
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_splitof_nameprefix_noprefix(self):
        self.assertEqual(splitof_nameprefix("Noprefix"), ('',"Noprefix"))

    def test_splitof_nameprefix_prefix(self):
        self.assertEqual(splitof_nameprefix("van Prefix"), ('van',"Prefix"))

    def test_splitof_nameprefix_doublespace(self):
        self.assertEqual(splitof_nameprefix("van  Prefix"), ('van',"Prefix"))

    def test_fitin_regular(self):
        self.assertEqual(fitin("Mr. Gaius Julius Caesar",
                                           "Gaius Caesar", "Julius"), 6)

    def test_fitin_wrong_receiver(self):
        self.assertEqual(fitin("A B C", "A D", "B"), -1)

    def test_fitin_wrong_element(self):
        self.assertRaises(ValueError, fitin, "A B C", "A C", "D")

    def test_fitin_last_element(self):
        self.assertRaises(IndexError, fitin, "A B C", "A B", "C")

    def test_name_value_split_begin_colon(self):
        self.vcard.insert(4, ":email@example.com")
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_name_value_split_quoted_colon(self):
        self.vcard.insert(4, 'TEL;TYPE="FANCY:TYPE":01234-56789')
        address = ET.SubElement(self.person, "address")
        ET.SubElement(address, 'phone').text = '01234-56789'
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_name_value_split_grouped(self):
        self.vcard[1] = "group." + self.vcard[1]
        self.vcard[3] = "group." + self.vcard[3]
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_unesc_string(self):
        self.assertEqual(VCardParser.unesc("TEL:012\\\\345\\,67\\;89"),
                         "TEL:012\\345,67;89")

    def test_unesc_list(self):
        self.assertEqual(VCardParser.unesc([r"Last\,name", r"First\;name"]),
                         ["Last,name", "First;name"])

    def test_unesc_tuple(self):
        self.assertRaises(TypeError, VCardParser.unesc,
                          (r"Last\,name", r"First\;name"))

    def test_count_escapes_null(self):
        self.assertEqual(VCardParser.count_escapes("Lastname"), 0)

    def test_count_escapes_one(self):
        self.assertEqual(VCardParser.count_escapes("Lastname\\"), 1)

    def test_count_escapes_two(self):
        self.assertEqual(VCardParser.count_escapes(r"Lastname\\"), 2)

    def test_split_unescaped_regular(self):
        self.assertEqual(VCardParser.split_unescaped("Lastname;Firstname", ';'),
                         ["Lastname", "Firstname"])

    def test_split_unescaped_one(self):
        self.assertEqual(VCardParser.split_unescaped("Lastname\\;Firstname", ';'),
                         ["Lastname\\;Firstname",])

    def test_split_unescaped_two(self):
        self.assertEqual(VCardParser.split_unescaped("Lastname\\\\;Firstname", ';'),
                         ["Lastname\\\\", "Firstname",])

    def test_split_unescaped_three(self):
        self.assertEqual(VCardParser.split_unescaped(r"Lastname\\\;Firstname", ';'),
                         [r"Lastname\\\;Firstname",])

    def test_get_next_line_continuation(self):
        self.vcard.insert(4, "TEL:01234-\r\n 56789")
        address = ET.SubElement(self.person, "address")
        ET.SubElement(address, 'phone').text = '01234-56789'
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_get_next_line_cr(self):
        self.vcard.insert(4, "TEL:01234-56789\r")
        address = ET.SubElement(self.person, "address")
        ET.SubElement(address, 'phone').text = '01234-56789'
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_get_next_line_strip(self):
        self.vcard.insert(4, "TEL:01234-56789  ")
        address = ET.SubElement(self.person, "address")
        ET.SubElement(address, 'phone').text = '01234-56789'
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_get_next_line_none(self):
        self.vcard.insert(4, "")
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_parse_vCard_file_no_colon(self):
        self.vcard.insert(4, "TEL;01234-56789")
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_parse_vCard_file_lowercase(self):
        self.vcard.insert(4, "tel:01234-56789")
        address = ET.SubElement(self.person, "address")
        ET.SubElement(address, 'phone').text = '01234-56789'
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_parse_vCard_unknown_property(self):
        self.vcard.insert(4, "TELEPHONE:01234-56789")
        self.gramps = self.gramps
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_next_person_no_end(self):
        self.vcard[4] = "BEGIN:VCARD"
        self.vcard.extend(["VERSION:3.0", "FN:Another", "N:Another;;;;", "END:VCARD"])
        attribs = {'handle': 'I0001', 'id': 'I0001'}
        person = ET.SubElement(self.gramps[1], "person", attribs)
        ET.SubElement(person, 'gender').text = 'U'
        name = ET.SubElement(person, 'name', {'type': 'Birth Name'})
        ET.SubElement(name, 'surname').text = 'Another'
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_check_version(self):
        self.vcard = ["BEGIN:VCARD", "VERSION:3.7", "FN:Another",
                      "N:Another;;;;", "END:VCARD"]
        expected = ET.XML(self.header + "</database>")
        self.do_case("\r\n".join(self.vcard), expected)

    def test_add_formatted_name_twice(self):
        self.vcard[2] = "FN:Lastname B A"
        self.vcard[3] = "N:Lastname;A;B;;"
        self.vcard.insert(4, "FN:Lastname A B")
        name = self.person[1]
        first = ET.Element("first")
        first.text = "B A"
        name.insert(0, first)
        call = ET.Element("call")
        call.text = "A"
        name.insert(1, call)
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_name_parts_twice(self):
        self.vcard.insert(4, "N:Another;;;;")
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_name_regular(self):
        self.vcard[2] = "FN:Mr. Firstname Middlename Lastname Jr."
        self.vcard[3] = "N:Lastname;Firstname;Middlename;Mr.;Jr."
        first = ET.Element('first')
        first.text = 'Firstname Middlename'
        self.name.insert(0, first)
        ET.SubElement(self.name, 'suffix').text = 'Jr.'
        ET.SubElement(self.name, 'title').text = 'Mr.'
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_name_multisurname(self):
        self.vcard[2] = "FN:Lastname Lastname2"
        self.vcard[3] = "N:Lastname,Lastname2;;;;"
        surname = ET.SubElement(self.name, 'surname')
        surname.text = 'Lastname2'
        surname.set('prim', '0')
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_name_prefixsurname(self):
        self.vcard[2] = "FN:van d'Alembert"
        self.vcard[3] = "N:van d'Alembert;;;;"
        surname = self.name[0]
        surname.text = 'Alembert'
        surname.set('prefix', "van d'")
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_name_only_surname(self):
        self.vcard[3] = "N:Lastname"
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_name_upto_firstname(self):
        self.vcard[2] = "FN:Firstname Lastname"
        self.vcard[3] = "N:Lastname; Firstname;"
        first = ET.Element('first')
        first.text = 'Firstname'
        self.name.insert(0, first)
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_name_empty(self):
        self.vcard[2] = "FN:Lastname"
        self.vcard[3] = "N: "
        self.gramps.remove(self.gramps[1])
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_firstname_regular(self):
        self.vcard[2] = "FN:A B Lastname"
        self.vcard[3] = "N:Lastname;A;B;;"
        first = ET.Element('first')
        first.text = 'A B'
        self.name.insert(0, first)
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_firstname_callname(self):
        self.vcard[2] = "FN:A B Lastname"
        self.vcard[3] = "N:Lastname;B;A;;"
        first = ET.Element('first')
        first.text = 'A B'
        self.name.insert(0, first)
        call = ET.Element('call')
        call.text = 'B'
        self.name.insert(1, call)
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_firstname_incomplete_fn(self):
        self.vcard[2] = "FN:A Lastname"
        self.vcard[3] = "N:Lastname;A;B;;"
        first = ET.Element('first')
        first.text = 'A B'
        self.name.insert(0, first)
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_firstname_middle(self):
        self.vcard[2] = "FN:A B C Lastname"
        self.vcard[3] = "N:Lastname;B;A C;;"
        first = ET.Element('first')
        first.text = 'A B C'
        self.name.insert(0, first)
        call = ET.Element('call')
        call.text = 'B'
        self.name.insert(1, call)
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_firstname_fn_not_given(self):
        self.vcard[2] = "FN:B Lastname"
        self.vcard[3] = "N:Lastname;A;B;;"
        first = ET.Element('first')
        first.text = 'A B'
        self.name.insert(0, first)
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_firstname_no_addnames(self):
        self.vcard[2] = "FN:A Lastname"
        self.vcard[3] = "N:Lastname;A;;;"
        first = ET.Element('first')
        first.text = 'A'
        self.name.insert(0, first)
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_firstname_no_givenname(self):
        self.vcard[2] = "FN:A Lastname"
        self.vcard[3] = "N:Lastname;;A;;"
        first = ET.Element('first')
        first.text = 'A'
        self.name.insert(0, first)
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_firstname_no_fn(self):
        self.vcard[2] = "FN:"
        self.vcard[3] = "N:Lastname;;A;;"
        first = ET.Element('first')
        first.text = 'A'
        self.name.insert(0, first)
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_nicknames_single(self):
        self.vcard.insert(4, "NICKNAME:Ton")
        attribs = {"alt": "1", "type": "Birth Name"}
        name = ET.SubElement(self.person, 'name', attribs)
        ET.SubElement(name, 'nick').text = "Ton"
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_nicknames_empty(self):
        self.vcard.insert(4, "NICKNAME:")
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_nicknames_multiple(self):
        self.vcard.insert(4, r"NICKNAME:A,B\,C")
        attribs = {"alt": "1", "type": "Birth Name"}
        name = ET.SubElement(self.person, 'name', attribs)
        ET.SubElement(name, 'nick').text = "A"
        attribs = {"alt": "1", "type": "Birth Name"}
        name = ET.SubElement(self.person, 'name', attribs)
        ET.SubElement(name, 'nick').text = "B,C"
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_address_all(self):
        self.vcard.insert(4, "ADR:box 1;bis;Broadway 11; New York; New York; NY1234; USA")
        address = ET.SubElement(self.person, 'address')
        ET.SubElement(address, 'street').text = 'box 1 bis Broadway 11'
        ET.SubElement(address, 'city').text = 'New York'
        ET.SubElement(address, 'state').text = 'New York'
        ET.SubElement(address, 'country').text = 'USA'
        ET.SubElement(address, 'postal').text = 'NY1234'
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_address_too_many(self):
        self.vcard.insert(4, r"ADR:;;Broadway 11; New\,York; ;; USA; Earth")
        address = ET.SubElement(self.person, 'address')
        ET.SubElement(address, 'street').text = 'Broadway 11'
        ET.SubElement(address, 'city').text = 'New,York'
        ET.SubElement(address, 'country').text = 'USA'
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_address_too_few(self):
        self.vcard.insert(4, "ADR:;;Broadway 11; New York")
        address = ET.SubElement(self.person, 'address')
        ET.SubElement(address, 'street').text = 'Broadway 11'
        ET.SubElement(address, 'city').text = 'New York'
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_address_empty(self):
        self.vcard.insert(4, "ADR: ")
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_phone_regular(self):
        self.vcard.insert(4, "TEL:01234-56789")
        address = ET.SubElement(self.person, 'address')
        ET.SubElement(address, 'phone').text = '01234-56789'
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_phone_empty(self):
        self.vcard.insert(4, "TEL: ")
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_birthday_regular(self):
        self.vcard.insert(4, 'BDAY:2001-09-28')
        attribs = {'hlink': 'E0000', 'role': 'Primary'}
        eventref = ET.SubElement(self.person, 'eventref', attribs)
        events = ET.Element('events')
        self.gramps.insert(1, events)
        attribs = {'handle': 'E0000', 'id': 'E0000'}
        event = ET.SubElement(events, 'event', attribs)
        ET.SubElement(event, 'type').text = 'Birth'
        ET.SubElement(event, 'dateval', {'val': '2001-09-28'})
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_birthday_datetime(self):
        self.vcard.insert(4, 'BDAY:2001-09-28T09:23:47Z')
        attribs = {'hlink': 'E0000', 'role': 'Primary'}
        eventref = ET.SubElement(self.person, 'eventref', attribs)
        events = ET.Element('events')
        self.gramps.insert(1, events)
        attribs = {'handle': 'E0000', 'id': 'E0000'}
        event = ET.SubElement(events, 'event', attribs)
        ET.SubElement(event, 'type').text = 'Birth'
        ET.SubElement(event, 'dateval', {'val': '2001-09-28'})
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_birthday_no_dash(self):
        self.vcard.insert(4, 'BDAY:20010928')
        attribs = {'hlink': 'E0000', 'role': 'Primary'}
        eventref = ET.SubElement(self.person, 'eventref', attribs)
        events = ET.Element('events')
        self.gramps.insert(1, events)
        attribs = {'handle': 'E0000', 'id': 'E0000'}
        event = ET.SubElement(events, 'event', attribs)
        ET.SubElement(event, 'type').text = 'Birth'
        ET.SubElement(event, 'dateval', {'val': '2001-09-28'})
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_birthday_long_Feb_converted_to_datestr(self):
        self.vcard.insert(4, 'BDAY:20010229')
        attribs = {'hlink': 'E0000', 'role': 'Primary'}
        eventref = ET.SubElement(self.person, 'eventref', attribs)
        events = ET.Element('events')
        self.gramps.insert(1, events)
        attribs = {'handle': 'E0000', 'id': 'E0000'}
        event = ET.SubElement(events, 'event', attribs)
        ET.SubElement(event, 'type').text = 'Birth'
        ET.SubElement(event, 'datestr', {'val': '20010229'})
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_birthday_invalid_format_converted_to_datestr(self):
        self.vcard.insert(4, 'BDAY:unforgettable')
        attribs = {'hlink': 'E0000', 'role': 'Primary'}
        eventref = ET.SubElement(self.person, 'eventref', attribs)
        events = ET.Element('events')
        self.gramps.insert(1, events)
        attribs = {'handle': 'E0000', 'id': 'E0000'}
        event = ET.SubElement(events, 'event', attribs)
        ET.SubElement(event, 'type').text = 'Birth'
        ET.SubElement(event, 'datestr', {'val': 'unforgettable'})
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_birthday_one_dash(self):
        self.vcard.insert(4, 'BDAY:2001-0928')
        attribs = {'hlink': 'E0000', 'role': 'Primary'}
        eventref = ET.SubElement(self.person, 'eventref', attribs)
        events = ET.Element('events')
        self.gramps.insert(1, events)
        attribs = {'handle': 'E0000', 'id': 'E0000'}
        event = ET.SubElement(events, 'event', attribs)
        ET.SubElement(event, 'type').text = 'Birth'
        ET.SubElement(event, 'dateval', {'val': '2001-09-28'})
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_birthday_empty(self):
        self.vcard.insert(4, "BDAY: ")
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_occupation_regular(self):
        self.vcard.insert(4, "ROLE:scarecrow")
        attribs = {'hlink': 'E0000', 'role': 'Primary'}
        eventref = ET.SubElement(self.person, 'eventref', attribs)
        events = ET.Element('events')
        self.gramps.insert(1, events)
        attribs = {'handle': 'E0000', 'id': 'E0000'}
        event = ET.SubElement(events, 'event', attribs)
        ET.SubElement(event, 'type').text = 'Occupation'
        ET.SubElement(event, 'description').text = 'scarecrow'
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_occupation_empty(self):
        self.vcard.insert(4, "ROLE: ")
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_url_regular(self):
        self.vcard.insert(4, "URL:http://www.example.com")
        attribs = {'href': 'http://www.example.com', 'type': 'Unknown'}
        ET.SubElement(self.person, 'url', attribs)
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_url_empty(self):
        self.vcard.insert(4, "URL: ")
        self.do_case("\r\n".join(self.vcard), self.gramps)

    def test_add_email(self):
        self.vcard.insert(4, "EMAIL:me@example.org")
        attribs = {'href': 'me@example.org', 'type': 'E-mail'}
        ET.SubElement(self.person, 'url', attribs)
        self.do_case("\r\n".join(self.vcard), self.gramps)


if __name__ == "__main__":
    unittest.main()
