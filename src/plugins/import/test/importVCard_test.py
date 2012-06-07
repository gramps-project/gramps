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
Unittest of import of VCard

To be called from src directory.
"""

# in case of a failing test, add True as last parameter to do_test to see the output.

from cStringIO import StringIO
import time
import unittest
import sys
import os
sys.path.append(os.curdir)
sys.path.append(os.path.join(os.curdir, 'plugins','import'))
sys.path.append(os.path.join(os.curdir, 'plugins', 'lib'))
import subprocess
import libxml2
import libxslt

from libgrampsxml import GRAMPS_XML_VERSION

from const import ROOT_DIR, VERSION
import ImportVCard
from ImportVCard import VCardParser

class VCardCheck(unittest.TestCase):
    def setUp(self):
        date = time.localtime(time.time())
        libxml2.keepBlanksDefault(0)
        styledoc = libxml2.parseFile(os.path.join(ROOT_DIR,
            "../data/gramps_canonicalize.xsl"))
        self.style = libxslt.parseStylesheetDoc(styledoc)
        self.header = """<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE database PUBLIC "-//GRAMPS//DTD GRAMPS XML %s//EN"
            "http://gramps-project.org/xml/%s/grampsxml.dtd">
            <database xmlns="http://gramps-project.org/xml/%s/">
            <header>
            <created date="%04d-%02d-%02d" version="%s"/>
            <researcher/>
            </header>""" % \
            (GRAMPS_XML_VERSION, GRAMPS_XML_VERSION, GRAMPS_XML_VERSION,
                    date[0], date[1], date[2], VERSION)
        expect_str = self.header + """<people><person handle="I0000" """ \
                """id="I0000"><gender>U</gender><name type="Birth Name">""" \
                """<surname>Lastname</surname></name></person></people></database>"""
        self.gramps = libxml2.readDoc(expect_str, '', None, libxml2.XML_PARSE_NONET)
        self.person = self.gramps.getRootElement().firstElementChild().\
                         nextElementSibling().firstElementChild()
        self.name = self.person.firstElementChild().nextElementSibling()
        self.vcard = ["BEGIN:VCARD", "VERSION:3.0", "FN:Lastname",
                      "N:Lastname;;;;", "END:VCARD"]

    def tearDown(self):
        self.style.freeStylesheet()
        #self.gramps.freeDoc() # makes is crash

    def string2canonicalxml(self, input_str, buf):
        if type(input_str) == type('string'):
            doc = libxml2.readDoc(input_str, '', None, libxml2.XML_PARSE_NONET)
        elif isinstance(input_str, libxml2.xmlDoc):
            doc = input_str
        else:
            raise TypeError
        param = {'replace_handles':"'ID'"}
        canonical_doc = self.style.applyStylesheet(doc, param)
        canonical_doc.saveFormatFileTo(buf, 'UTF-8', 1)
        doc.freeDoc()
        canonical_doc.freeDoc()
        return

    def do_test(self, input_str, expect_str, debug=False):
        expect_canonical_strfile = StringIO()
        buf = libxml2.createOutputBuffer(expect_canonical_strfile, 'UTF-8')
        self.string2canonicalxml(expect_str, buf)

        process = subprocess.Popen('python gramps.py '
            '--config=preferences.eprefix:DEFAULT -i - -f vcf -e - -f gramps',
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        result_str, err_str = process.communicate(input_str)
        if err_str:
            print err_str
        result_canonical_strfile = StringIO()
        buf2 = libxml2.createOutputBuffer(result_canonical_strfile, 'UTF-8')
        self.string2canonicalxml(result_str, buf2)

        if debug:
            print result_canonical_strfile.getvalue()
            print expect_canonical_strfile.getvalue()
        self.assertEqual(result_canonical_strfile.getvalue(),
                         expect_canonical_strfile.getvalue())
        expect_canonical_strfile.close()
        result_canonical_strfile.close()

    def test_base(self):
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_splitof_nameprefix_noprefix(self):
        self.assertEqual(ImportVCard.splitof_nameprefix("Noprefix"), ('',"Noprefix"))

    def test_splitof_nameprefix_prefix(self):
        self.assertEqual(ImportVCard.splitof_nameprefix("van Prefix"), ('van',"Prefix"))

    def test_splitof_nameprefix_doublespace(self):
        self.assertEqual(ImportVCard.splitof_nameprefix("van  Prefix"), ('van',"Prefix"))

    def test_fitin_regular(self):
        self.assertEqual(ImportVCard.fitin("Mr. Gaius Julius Caesar",
                                           "Gaius Caesar", "Julius"), 6)

    def test_fitin_wrong_receiver(self):
        self.assertEqual(ImportVCard.fitin("A B C", "A D", "B"), -1)

    def test_fitin_wrong_element(self):
        self.assertRaises(ValueError, ImportVCard.fitin, "A B C", "A C", "D")

    def test_fitin_last_element(self):
        self.assertRaises(IndexError, ImportVCard.fitin, "A B C", "A B", "C")

    def test_name_value_split_begin_colon(self):
        self.vcard.insert(4, ":email@example.com")
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_name_value_split_quoted_colon(self):
        self.vcard.insert(4, 'TEL;TYPE="FANCY:TYPE":01234-56789')
        address = self.person.newChild(None, 'address', None)
        address.newChild(None, 'phone', '01234-56789')
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_name_value_split_grouped(self):
        self.vcard[1] = "group." + self.vcard[1]
        self.vcard[3] = "group." + self.vcard[3]
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_unesc_string(self):
        self.assertEqual(VCardParser.unesc("TEL:012\\\\345\\,67\\;89"),
                         "TEL:012\\345,67;89")

    def test_unesc_list(self):
        self.assertEqual(VCardParser.unesc(["Last\,name", "First\;name"]),
                         ["Last,name", "First;name"])

    def test_unesc_tuple(self):
        self.assertRaises(TypeError, VCardParser.unesc, ("Last\,name", "First\;name"))

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
        address = self.person.newChild(None, 'address', None)
        address.newChild(None, 'phone', '01234-56789')
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_get_next_line_cr(self):
        self.vcard.insert(4, "TEL:01234-56789\r")
        address = self.person.newChild(None, 'address', None)
        address.newChild(None, 'phone', '01234-56789')
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_get_next_line_strip(self):
        self.vcard.insert(4, "TEL:01234-56789  ")
        address = self.person.newChild(None, 'address', None)
        address.newChild(None, 'phone', '01234-56789')
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_get_next_line_none(self):
        self.vcard.insert(4, "")
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_parse_vCard_file_no_colon(self):
        self.vcard.insert(4, "TEL;01234-56789")
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_parse_vCard_file_lowercase(self):
        self.vcard.insert(4, "tel:01234-56789")
        address = self.person.newChild(None, 'address', None)
        address.newChild(None, 'phone', '01234-56789')
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_parse_vCard_unknown_property(self):
        self.vcard.insert(4, "TELEPHONE:01234-56789")
        self.gramps = self.gramps
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_next_person_no_end(self):
        self.vcard[4] = "BEGIN:VCARD"
        self.vcard.extend(["VERSION:3.0", "FN:Another", "N:Another;;;;", "END:VCARD"])
        people = self.gramps.getRootElement().firstElementChild().nextElementSibling()
        person = people.newChild(None, 'person', None)
        person.newProp('handle', 'I0001')
        person.newProp('id', 'I0001')
        person.newChild(None, 'gender', 'U')
        name = person.newChild(None, 'name', None)
        name.newProp('type', 'Birth Name')
        name.newChild(None, 'surname', 'Another')
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_check_version(self):
        self.vcard.extend(["BEGIN:VCARD", "VERSION:3.7", "FN:Another",
                             "N:Another;;;;", "END:VCARD"])
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_formatted_name_twice(self):
        self.vcard[2] = "FN:Lastname B A"
        self.vcard[3] = "N:Lastname;A;B;;"
        self.vcard.insert(4, "FN:Lastname A B")
        name = self.person.firstElementChild().nextElementSibling()
        surname = name.firstElementChild()
        firstname = name.newChild(None, "first", "B A")
        callname = name.newChild(None, "call", "A")
        callname.addNextSibling(surname)
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_name_parts_twice(self):
        self.vcard.insert(4, "N:Another;;;;")
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_name_regular(self):
        self.vcard[2] = "FN:Mr. Firstname Middlename Lastname Jr."
        self.vcard[3] = "N:Lastname;Firstname;Middlename;Mr.;Jr."
        name = self.person.firstElementChild().nextElementSibling()
        surname = name.firstElementChild()
        firstname = name.newChild(None, 'first', 'Firstname Middlename')
        firstname.addNextSibling(surname)
        name.newChild(None, 'suffix', 'Jr.')
        name.newChild(None, 'title', 'Mr.')
        self.do_test("\r\n".join(self.vcard), self.gramps)
        
    def test_add_name_multisurname(self):
        self.vcard[2] = "FN:Lastname Lastname2"
        self.vcard[3] = "N:Lastname,Lastname2;;;;"
        surname = self.name.newChild(None, 'surname', 'Lastname2')
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_name_prefixsurname(self):
        self.vcard[2] = "FN:van d'Alembert"
        self.vcard[3] = "N:van d'Alembert;;;;"
        surname = self.name.firstElementChild()
        surname.setContent('Alembert')
        surname.newProp('prefix', "van d'")
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_name_only_surname(self):
        self.vcard[3] = "N:Lastname"
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_name_upto_firstname(self):
        self.vcard[2] = "FN:Firstname Lastname"
        self.vcard[3] = "N:Lastname; Firstname;"
        surname = self.name.firstElementChild()
        first = self.name.newChild(None, 'first', 'Firstname')
        first.addNextSibling(surname)
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_name_empty(self):
        self.vcard[2] = "FN:Lastname"
        self.vcard[3] = "N: "
        people = self.gramps.getRootElement().firstElementChild().nextElementSibling()
        people.unlinkNode()
        people.freeNode()
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_firstname_regular(self):
        self.vcard[2] = "FN:A B Lastname"
        self.vcard[3] = "N:Lastname;A;B;;"
        surname = self.name.firstElementChild()
        firstname = self.name.newChild(None, 'first', 'A B')
        firstname.addNextSibling(surname)
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_firstname_callname(self):
        self.vcard[2] = "FN:A B Lastname"
        self.vcard[3] = "N:Lastname;B;A;;"
        surname = self.name.firstElementChild()
        firstname = self.name.newChild(None, 'first', 'A B')
        callname = self.name.newChild(None, 'call', 'B')
        callname.addNextSibling(surname)
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_firstname_incomplete_fn(self):
        self.vcard[2] = "FN:A Lastname"
        self.vcard[3] = "N:Lastname;A;B;;"
        surname = self.name.firstElementChild()
        firstname = self.name.newChild(None, 'first', 'A B')
        firstname.addNextSibling(surname)
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_firstname_middle(self):
        self.vcard[2] = "FN:A B C Lastname"
        self.vcard[3] = "N:Lastname;B;A C;;"
        surname = self.name.firstElementChild()
        firstname = self.name.newChild(None, 'first', 'A B C')
        callname = self.name.newChild(None, 'call', 'B')
        callname.addNextSibling(surname)
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_firstname_fn_not_given(self):
        self.vcard[2] = "FN:B Lastname"
        self.vcard[3] = "N:Lastname;A;B;;"
        surname = self.name.firstElementChild()
        firstname = self.name.newChild(None, 'first', 'A B')
        firstname.addNextSibling(surname)
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_firstname_no_addnames(self):
        self.vcard[2] = "FN:A Lastname"
        self.vcard[3] = "N:Lastname;A;;;"
        surname = self.name.firstElementChild()
        firstname = self.name.newChild(None, 'first', 'A')
        firstname.addNextSibling(surname)
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_firstname_no_givenname(self):
        self.vcard[2] = "FN:A Lastname"
        self.vcard[3] = "N:Lastname;;A;;"
        surname = self.name.firstElementChild()
        firstname = self.name.newChild(None, 'first', 'A')
        firstname.addNextSibling(surname)
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_firstname_no_fn(self):
        self.vcard[2] = "FN:"
        self.vcard[3] = "N:Lastname;;A;;"
        surname = self.name.firstElementChild()
        firstname = self.name.newChild(None, 'first', 'A')
        firstname.addNextSibling(surname)
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_nicknames_single(self):
        self.vcard.insert(4, "NICKNAME:Ton")
        name = self.person.newChild(None, "name", None)
        name.newProp("alt", "1")
        name.newProp("type", "Birth Name")
        name.newChild(None, "nick", "Ton")
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_nicknames_empty(self):
        self.vcard.insert(4, "NICKNAME:")
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_nicknames_multiple(self):
        self.vcard.insert(4, "NICKNAME:A,B\,C")
        name = self.person.newChild(None, "name", None)
        name.newProp("alt", "1")
        name.newProp("type", "Birth Name")
        name.newChild(None, "nick", "A")
        name = self.person.newChild(None, "name", None)
        name.newProp("alt", "1")
        name.newProp("type", "Birth Name")
        name.newChild(None, "nick", "B,C")
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_address_all(self):
        self.vcard.insert(4, "ADR:box 1;bis;Broadway 11; New York; New York; NY1234; USA")
        address = self.person.newChild(None, 'address', None)
        address.newChild(None, 'street', 'box 1 bis Broadway 11')
        address.newChild(None, 'city', 'New York')
        address.newChild(None, 'state', 'New York')
        address.newChild(None, 'country', 'USA')
        address.newChild(None, 'postal', 'NY1234')
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_address_too_many(self):
        self.vcard.insert(4, "ADR:;;Broadway 11; New\,York; ;; USA; Earth")
        address = self.person.newChild(None, 'address', None)
        address.newChild(None, 'street', 'Broadway 11')
        address.newChild(None, 'city', 'New,York')
        address.newChild(None, 'country', 'USA')
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_address_too_few(self):
        self.vcard.insert(4, "ADR:;;Broadway 11; New York")
        address = self.person.newChild(None, 'address', None)
        address.newChild(None, 'street', 'Broadway 11')
        address.newChild(None, 'city', 'New York')
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_address_empty(self):
        self.vcard.insert(4, "ADR: ")
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_phone_regular(self):
        self.vcard.insert(4, "TEL:01234-56789")
        address = self.person.newChild(None, 'address', None)
        address.newChild(None, 'phone', '01234-56789')
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_phone_empty(self):
        self.vcard.insert(4, "TEL: ")
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_birthday_regular(self):
        self.vcard.insert(4, 'BDAY:2001-09-28')
        eventref = self.person.newChild(None, 'eventref', None)
        eventref.newProp('hlink', 'E0000')
        eventref.newProp('role', 'Primary')
        events = self.gramps.getRootElement().newChild(None, 'events', None)
        event = events.newChild(None, 'event', None)
        event.newProp('handle', 'E0000')
        event.newProp('id', 'E0000')
        event.newChild(None, 'type', 'Birth')
        date = event.newChild(None, 'dateval', None)
        date.newProp('val', '2001-09-28')
        people = self.gramps.getRootElement().firstElementChild().nextElementSibling()
        events.addNextSibling(people)
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_birthday_datetime(self):
        self.vcard.insert(4, 'BDAY:2001-09-28T09:23:47Z')
        eventref = self.person.newChild(None, 'eventref', None)
        eventref.newProp('hlink', 'E0000')
        eventref.newProp('role', 'Primary')
        events = self.gramps.getRootElement().newChild(None, 'events', None)
        event = events.newChild(None, 'event', None)
        event.newProp('handle', 'E0000')
        event.newProp('id', 'E0000')
        event.newChild(None, 'type', 'Birth')
        date = event.newChild(None, 'dateval', None)
        date.newProp('val', '2001-09-28')
        people = self.gramps.getRootElement().firstElementChild().nextElementSibling()
        events.addNextSibling(people)
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_birthday_no_dash(self):
        self.vcard.insert(4, 'BDAY:20010928')
        eventref = self.person.newChild(None, 'eventref', None)
        eventref.newProp('hlink', 'E0000')
        eventref.newProp('role', 'Primary')
        events = self.gramps.getRootElement().newChild(None, 'events', None)
        event = events.newChild(None, 'event', None)
        event.newProp('handle', 'E0000')
        event.newProp('id', 'E0000')
        event.newChild(None, 'type', 'Birth')
        date = event.newChild(None, 'dateval', None)
        date.newProp('val', '2001-09-28')
        people = self.gramps.getRootElement().firstElementChild().nextElementSibling()
        events.addNextSibling(people)
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_birthday_one_dash(self):
        self.vcard.insert(4, 'BDAY:2001-0928')
        eventref = self.person.newChild(None, 'eventref', None)
        eventref.newProp('hlink', 'E0000')
        eventref.newProp('role', 'Primary')
        events = self.gramps.getRootElement().newChild(None, 'events', None)
        event = events.newChild(None, 'event', None)
        event.newProp('handle', 'E0000')
        event.newProp('id', 'E0000')
        event.newChild(None, 'type', 'Birth')
        date = event.newChild(None, 'dateval', None)
        date.newProp('val', '2001-09-28')
        people = self.gramps.getRootElement().firstElementChild().nextElementSibling()
        events.addNextSibling(people)
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_birthday_ddmmyyyy(self):
        self.vcard.insert(4, "BDAY:28-09-2001")
        self.do_test("\r\n".join(self.vcard), self.gramps)

    #def test_add_birthday_non_existant(self):
    #    # This test fails, I think gen.lib.date.set_yr_mon_day should raise
    #    # an error if a wrong date is entered.
    #    self.vcard.insert(4, 'BDAY:2001-13-28')
    #    self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_birthday_empty(self):
        self.vcard.insert(4, "BDAY: ")
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_occupation_regular(self):
        self.vcard.insert(4, "ROLE:scarecrow")
        eventref = self.person.newChild(None, 'eventref', None)
        eventref.newProp('hlink', 'E0000')
        eventref.newProp('role', 'Primary')
        events = self.gramps.getRootElement().newChild(None, 'events', None)
        event = events.newChild(None, 'event', None)
        event.newProp('handle', 'E0000')
        event.newProp('id', 'E0000')
        event.newChild(None, 'type', 'Occupation')
        event.newChild(None, 'description', 'scarecrow')
        people = self.gramps.getRootElement().firstElementChild().nextElementSibling()
        events.addNextSibling(people)
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_occupation_empty(self):
        self.vcard.insert(4, "ROLE: ")
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_url_regular(self):
        self.vcard.insert(4, "URL:http://www.example.com")
        url = self.person.newChild(None, 'url', None)
        url.newProp('href', 'http://www.example.com')
        url.newProp('type', 'Unknown')
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_url_empty(self):
        self.vcard.insert(4, "URL: ")
        self.do_test("\r\n".join(self.vcard), self.gramps)

    def test_add_email(self):
        self.vcard.insert(4, "EMAIL:me@example.org")
        url = self.person.newChild(None, 'url', None)
        url.newProp('href', 'me@example.org')
        url.newProp('type', 'E-mail')
        self.do_test("\r\n".join(self.vcard), self.gramps)


if __name__ == "__main__":
    unittest.main()
