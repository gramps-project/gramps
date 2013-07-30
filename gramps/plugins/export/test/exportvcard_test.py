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
from __future__ import print_function

import unittest
import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO
import time
import subprocess
import libxml2

from gramps.plugins.lib.libgrampsxml import GRAMPS_XML_VERSION
from gramps.version import VERSION
from gramps.plugins.export.exportvcard import VCardWriter

class VCardCheck(unittest.TestCase):
    def setUp(self):
        self.expect = ["BEGIN:VCARD", "VERSION:3.0", 
                       "PRODID:-//Gramps//NONSGML Gramps %s//EN" % VERSION, 
                       "FN:Lastname", "N:Lastname;;;;", 
                       "SORT-STRING:" + "Lastname".ljust(55), "END:VCARD"]
        date = time.localtime(time.time())
        self.input_list = ["BEGIN:VCARD", "VERSION:3.0", "FN:Lastname", 
                           "N:Lastname;;;;", "END:VCARD"]
        strng = """<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE database PUBLIC "-//GRAMPS//DTD GRAMPS XML %s//EN"
            "http://gramps-project.org/xml/%s/grampsxml.dtd">
            <database xmlns="http://gramps-project.org/xml/%s/">
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
            (GRAMPS_XML_VERSION, GRAMPS_XML_VERSION, GRAMPS_XML_VERSION,
                    date[0], date[1], date[2], VERSION)
        self.input_ = libxml2.readDoc(strng, '', None, libxml2.XML_PARSE_NONET)
        self.database = self.input_.getRootElement()
        self.people = self.database.firstElementChild().nextElementSibling()
        self.person = self.people.firstElementChild()
        self.name = self.person.firstElementChild()
        self.lastname = self.name.firstElementChild()

    def do_test(self, input_doc, expect_str, debug=False):
        input_strfile = StringIO()
        buf = libxml2.createOutputBuffer(input_strfile, 'UTF-8')
        input_doc.saveFormatFileTo(buf, 'UTF-8', 1)
        if debug:
            print(input_strfile.getvalue())

        process = subprocess.Popen('python Gramps.py '
                                   '-i - -f gramps -e - -f vcf',
                                   stdin=subprocess.PIPE, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   shell=True)
        result_str, err_str = process.communicate(input_strfile.getvalue())
        if debug:
            print(err_str)
            print(result_str)
            print(expect_str)
        self.assertEqual(result_str, expect_str)

    def test_base(self):
        self.do_test(self.input_,
                     "\r\n".join(self.expect) + '\r\n\r\n')

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
        self.name.newTextChild(None, 'title', 'Sir.')
        self.expect[3] = "FN:Sir. Lastname"
        self.expect[4] = "N:Lastname;;;Sir.;"
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_name_multiple_surname(self):
        self.lastname.setContent("Oranje")
        self.lastname.newProp("prefix", "van")
        self.name.newTextChild(None, "surname", "Nassau")
        self.expect[3] = "FN:van Oranje Nassau"
        self.expect[4] = "N:van Oranje,Nassau;;;;"
        self.expect[5] = "SORT-STRING:" + "Oranje".ljust(55)
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_name_callname(self):
        # callname not in first names!
        self.name.newTextChild(None, "first", "B C")
        self.name.newTextChild(None, "call", "A")
        self.expect[3] = "FN:B C Lastname"
        self.expect[4] = "N:Lastname;A;B,C;;"
        self.expect[5] = "SORT-STRING:" + "Lastname".ljust(25) + "B C".ljust(30)
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_name_callname_in_addnames(self):
        self.name.newTextChild(None, "first", "A B C")
        self.name.newTextChild(None, "call", "B")
        self.expect[3] = "FN:A B C Lastname"
        self.expect[4] = "N:Lastname;B;A,C;;"
        self.expect[5] = "SORT-STRING:" + "Lastname".ljust(25) + "A B C".ljust(30)
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_name_no_callname(self):
        self.name.newTextChild(None, "first", "A B C")
        self.expect[3] = "FN:A B C Lastname"
        self.expect[4] = "N:Lastname;A;B,C;;"
        self.expect[5] = "SORT-STRING:" + "Lastname".ljust(25) + "A B C".ljust(30)
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_name_no_additional_names(self):
        self.name.newTextChild(None, "first", "A")
        self.expect[3] = "FN:A Lastname"
        self.expect[4] = "N:Lastname;A;;;"
        self.expect[5] = "SORT-STRING:" + "Lastname".ljust(25) + "A".ljust(30)
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_name_honprefix(self):
        self.name.newTextChild(None, 'title', 'Sir')
        self.expect[3] = "FN:Sir Lastname"
        self.expect[4] = "N:Lastname;;;Sir;"
        self.expect[5] = "SORT-STRING:" + "Lastname".ljust(55)
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_name_honsuffix(self):
        self.name.newTextChild(None, 'suffix', 'Jr.')
        self.expect[3] = "FN:Lastname\, Jr."
        self.expect[4] = "N:Lastname;;;;Jr."
        self.expect[5] = "SORT-STRING:" + "Lastname".ljust(55)+ "Jr."
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')


    def test_nicknames_regular(self):
        name = self.person.newChild(None, 'name', '')
        name.newProp('type', 'Birth Name')
        name.newProp('alt', '1')
        name.newTextChild(None, 'nick', 'Nick')
        name = self.person.newChild(None, 'name', '')
        name.newProp('type', 'Birth Name')
        name.newProp('alt', '1')
        name.newTextChild(None, 'nick', 'N.')
        self.expect.insert(6, "NICKNAME:Nick,N.")
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')

    def test_nicknames_primary_nick(self):
        self.name.newTextChild(None, 'nick', 'Nick')
        name = self.person.newChild(None, 'name', '')
        name.newProp('type', 'Birth Name')
        name.newProp('alt', '1')
        name.newTextChild(None, 'nick', 'N.')
        self.expect.insert(6, "NICKNAME:Nick,N.")
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')
    
    def test_write_birthdate_regular(self):
        events = self.database.newChild(None, 'events', None)
        event = events.newChild(None, 'event', None)
        event.newProp('handle', '_e0000')
        event.newProp('id', 'E0000')
        event.newTextChild(None, 'type', 'Birth')
        dateval = event.newChild(None, 'dateval', None)
        dateval.newProp('val', '2001-02-28')
        evtref = self.person.newChild(None, 'eventref', None)
        evtref.newProp('hlink', '_e0000')
        evtref.newProp('role', 'Primary')
        self.people.addPrevSibling(events)
        self.expect.insert(6, "BDAY:2001-02-28")
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_birthdate_empty(self):
        events = self.database.newChild(None, 'events', None)
        event = events.newChild(None, 'event', None)
        event.newProp('handle', '_e0000')
        event.newProp('id', 'E0000')
        event.newTextChild(None, 'type', 'Birth')
        evtref = self.person.newChild(None, 'eventref', None)
        evtref.newProp('hlink', '_e0000')
        evtref.newProp('role', 'Primary')
        self.people.addPrevSibling(events)
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_birhtdate_textonly(self):
        events = self.database.newChild(None, 'events', None)
        event = events.newChild(None, 'event', None)
        event.newProp('handle', '_e0000')
        event.newProp('id', 'E0000')
        event.newTextChild(None, 'type', 'Birth')
        datestr = event.newChild(None, 'datestr', None)
        datestr.newProp('val', 'Christmas 2001')
        evtref = self.person.newChild(None, 'eventref', None)
        evtref.newProp('hlink', '_e0000')
        evtref.newProp('role', 'Primary')
        self.people.addPrevSibling(events)
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_birthdate_span(self):
        events = self.database.newChild(None, 'events', None)
        event = events.newChild(None, 'event', None)
        event.newProp('handle', '_e0000')
        event.newProp('id', 'E0000')
        event.newTextChild(None, 'type', 'Birth')
        datespan = event.newChild(None, 'datespan', None)
        datespan.newProp('start', '2001-02-28')
        datespan.newProp('stop', '2002-02-28')
        evtref = self.person.newChild(None, 'eventref', None)
        evtref.newProp('hlink', '_e0000')
        evtref.newProp('role', 'Primary')
        self.people.addPrevSibling(events)
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_birthdate_range(self):
        events = self.database.newChild(None, 'events', None)
        event = events.newChild(None, 'event', None)
        event.newProp('handle', '_e0000')
        event.newProp('id', 'E0000')
        event.newTextChild(None, 'type', 'Birth')
        daterange = event.newChild(None, 'daterange', None)
        daterange.newProp('start', '2001-02-28')
        daterange.newProp('stop', '2002-02-28')
        evtref = self.person.newChild(None, 'eventref', None)
        evtref.newProp('hlink', '_e0000')
        evtref.newProp('role', 'Primary')
        self.people.addPrevSibling(events)
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_addresses_regular(self):
        address = self.person.newChild(None, 'address', None)
        address.newChild(None, 'street', 'pobox bis street')
        address.newChild(None, 'city', 'place')
        address.newChild(None, 'country', 'country')
        address.newChild(None, 'state', 'province')
        address.newChild(None, 'postal', 'zip')
        self.expect.insert(6, "ADR:;;pobox bis street;place;province;zip;country")
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_addresses_phone(self):
        address = self.person.newChild(None, 'address', None)
        address.newChild(None, 'phone', '01234-56789')
        self.expect.insert(6, "TEL:01234-56789")
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_urls_email(self):
        url = self.person.newChild(None, 'url', None)
        url.newProp('type', 'E-mail')
        url.newProp('href', 'me@example.com')
        self.expect.insert(6, "EMAIL:me@example.com")
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_urls_emial_mailto(self):
        url = self.person.newChild(None, 'url', None)
        url.newProp('type', 'E-mail')
        url.newProp('href', 'mailto:me@example.com')
        self.expect.insert(6, "EMAIL:me@example.com")
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_urls_url(self):
        url = self.person.newChild(None, 'url', None)
        url.newProp('type', 'Web Home')
        url.newProp('href', 'http://www.example.org')
        self.expect.insert(6, "URL:http://www.example.org")
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_occupation_regular(self):
        events = self.database.newChild(None, 'events', None)
        event = events.newChild(None, 'event', None)
        event.newProp('handle', '_e0000')
        event.newProp('id', 'E0000')
        event.newChild(None, 'type', 'Occupation')
        event.newChild(None, 'description', 'carpenter')
        evtref = self.person.newChild(None, 'eventref', None)
        evtref.newProp('hlink', '_e0000')
        evtref.newProp('role', 'Primary')
        self.people.addPrevSibling(events)
        self.expect.insert(6, "ROLE:carpenter")
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')

    def test_write_occupation_lastdate(self):
        events = self.database.newChild(None, 'events', None)
        event = events.newChild(None, 'event', None)
        event.newProp('handle', '_e0000')
        event.newProp('id', 'E0000')
        event.newChild(None, 'type', 'Occupation')
        dateval = event.newChild(None, 'dateval', None)
        dateval.newProp('val', '2011-02-28')
        event.newChild(None, 'description', 'foreman')
        event = events.newChild(None, 'event', None)
        event.newProp('handle', '_e0001')
        event.newProp('id', 'E0001')
        event.newChild(None, 'type', 'Occupation')
        dateval = event.newChild(None, 'dateval', None)
        dateval.newProp('val', '2000-09-21')
        event.newChild(None, 'description', 'carpenter')
        evtref = self.person.newChild(None, 'eventref', None)
        evtref.newProp('hlink', '_e0000')
        evtref.newProp('role', 'Primary')
        evtref = self.person.newChild(None, 'eventref', None)
        evtref.newProp('hlink', '_e0001')
        evtref.newProp('role', 'Primary')
        self.people.addPrevSibling(events)
        self.expect.insert(6, "ROLE:foreman")
        self.do_test(self.input_, "\r\n".join(self.expect) + '\r\n\r\n')

if __name__ == "__main__":
    unittest.main()
