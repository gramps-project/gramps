#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011 Michiel D. Nauta
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
Unittest that tests that part of the merge process that influences other
objects than the objects merging.
"""
import unittest
import time
import os
from io import BytesIO
import difflib
import copy
import lxml.etree as ET

from gramps.plugins.lib.libgrampsxml import GRAMPS_XML_VERSION
from gramps.test.test_util import Gramps
from gramps.gen.user import User
from gramps.gen.const import DATA_DIR, USER_PLUGINS, TEMP_DIR
from gramps.version import VERSION
from gramps.gen.lib import Name, Surname
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

HAS_CLIMERGE = os.path.isdir(os.path.join(USER_PLUGINS, 'CliMerge'))
HAS_EXPORTRAW = os.path.isdir(os.path.join(USER_PLUGINS, 'ExportRaw'))
NS_G = 'http://gramps-project.org/xml/%s/' % GRAMPS_XML_VERSION
NSP = "{%s}" % NS_G


@unittest.skipUnless(HAS_CLIMERGE and HAS_EXPORTRAW,
                     'These tests need the 3rd-party plugins "CliMerge" '
                     'and "ExportRaw".')
class BaseMergeCheck(unittest.TestCase):
    """ Base class for the merge tests """
    def base_setup(self):
        """Set up code needed by all tests."""
        date = time.localtime(time.time())
        # libxml2.keepBlanksDefault(0)
        self.parser = ET.XMLParser(remove_blank_text=True)
        styledoc = ET.parse(os.path.join(DATA_DIR, "gramps_canonicalize.xsl"),
                            parser=self.parser)
        self.transform = ET.XSLT(styledoc)
        self.basedoc = None
        self.base_str = """<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE database PUBLIC "-//GRAMPS//DTD GRAMPS XML %s//EN"
        "http://gramps-project.org/xml/%s/grampsxml.dtd">
        <database xmlns="http://gramps-project.org/xml/%s/">
        <header>
        <created date="%04d-%02d-%02d" version="%s"/>
        <researcher>\n    </researcher>
        </header>
        """ % (GRAMPS_XML_VERSION, GRAMPS_XML_VERSION, GRAMPS_XML_VERSION,
               date[0], date[1], date[2], VERSION)

    def canonicalize(self, doctxt):
        """
        Return a canonicalized string representation

        :param doctxt: the text to bring in canonical form.
        :type doctxt: either a string or an Xml document.
        :returns: The text but in canonical form.
        :rtype: string
        """
        if isinstance(doctxt, bytes):
            doc = ET.fromstring(doctxt, parser=self.parser)
        elif isinstance(doctxt, ET._Element):
            doc = doctxt
        else:
            raise TypeError
        canonical_doc = self.transform(doc)
        result = ET.tostring(canonical_doc, pretty_print=True)
        #print(str(result, 'utf-8'))
        return result

    def do_case(self, phoenix_id, titanic_id, input_doc, expect_doc,
                test_error_str=''):
        """Do the merge and "assert" the result."""
        gramps = Gramps(user=User())
        result_str, err_str = gramps.run(
            '-d', '.ImportXML', '--config=preferences.eprefix:DEFAULT',
            '-i', '-', '-f', 'gramps', '-a', 'tool', '-p',
            "name=climerge,primary=%s,secondary=%s" % (phoenix_id, titanic_id),
            '-e', '-', '-f', 'gramps', stdin=BytesIO(input_doc), bytesio=True)
        self.check_results(input_doc, expect_doc, result_str, err_str,
                           test_error_str)

    def check_results(self, input_doc, expect_doc, result_str, err_str,
                      test_error_str=''):
        input_file = os.path.join(TEMP_DIR, "merge_test_input.gramps")
        try:
            os.remove(input_file)
        except OSError:
            pass

        if err_str:
            if test_error_str:
                self.assertIn(test_error_str, err_str)
                return
            else:
                if "Traceback (most recent call last):" in err_str:
                    inp = self.canonicalize(input_doc)
                    inpt = open(input_file, mode='wb')
                    inpt.write(inp)
                    inpt.close()
                    raise Exception(err_str)
        result = self.canonicalize(result_str)
        result_file = os.path.join(TEMP_DIR, "merge_test_result.gramps")
        try:
            os.remove(result_file)
        except OSError:
            pass
        expect = self.canonicalize(expect_doc)
        expect_file = os.path.join(TEMP_DIR, "merge_test_expected.gramps")
        try:
            os.remove(expect_file)
        except OSError:
            pass
        if result != expect:
            res = open(result_file, mode='wb')
            res.write(result)
            res.close()
            eres = open(expect_file, mode='wb')
            eres.write(expect)
            eres.close()
            inp = self.canonicalize(input_doc)
            inpt = open(input_file, mode='wb')
            inpt.write(inp)
            inpt.close()
            result = result.decode('utf-8')
            expect = expect.decode('utf-8')
            diff = difflib.ndiff(result, expect)
            msg = ""
            for line in diff:
                msg += line
            self.fail(msg)

    def do_family_case(self, phoenix_id, titanic_id, father_h, mother_h,
                       input_doc, expect_doc, test_error_str=''):
        gramps = Gramps(user=User())
        result_str, err_str = gramps.run(
            '-d', '.ImportXML', '--config=preferences.eprefix:DEFAULT',
            '-i', '-', '-f', 'gramps', '-a', 'tool', '-p',
            "name=climerge,primary=%s,secondary=%s,father_h=%s,mother_h=%s" %
            (phoenix_id, titanic_id, father_h, mother_h),
            '-e', '-', '-f', 'gramps', stdin=BytesIO(input_doc), bytesio=True)
        self.check_results(input_doc, expect_doc, result_str, err_str,
                           test_error_str)

    def raw_contains(self, phoenix_id, titanic_id, input_doc, expect_str,
                     test_error_str=''):
        gramps = Gramps(user=User())
        result_str, err_str = gramps.run(
            '-d', '.ImportXML', '--config=preferences.eprefix:DEFAULT',
            '-i', '-', '-f', 'gramps', '-a', 'tool', '-p',
            "name=climerge,primary=%s,secondary=%s" % (phoenix_id, titanic_id),
            '-e', '-', '-f', 'raw', stdin=BytesIO(input_doc), bytesio=False)
        if err_str:
            if test_error_str:
                self.assertIn(test_error_str, err_str)
                return
        if expect_str not in result_str:
            msg = '\n***** result:\n' + result_str + \
                '\n***** expect:\n' + expect_str
            inp = self.canonicalize(input_doc)
            input_file = os.path.join(TEMP_DIR, "merge_test_input.gramps")
            try:
                os.remove(input_file)
            except OSError:
                pass
            inpt = open(input_file, mode='wb')
            inpt.write(inp)
            inpt.close()
            self.fail(msg)


#-------------------------------------------------------------------------
#
# PersonCheck class
#
#-------------------------------------------------------------------------
class PersonCheck(BaseMergeCheck):
    """Class that checks what the influence is of merger of other primary
    objects on persons."""
    def setUp(self):
        self.base_setup()
        base_str = """
        <events>
          <event handle="_e0000" id="E0000">
            <type>Birth</type>
            <description>Event 0</description>
          </event>
          <event handle="_e0001" id="E0001">
            <type>Birth</type>
            <description>Event 1</description>
          </event>
        </events>
        <people>
          <person handle="_i0000" id="I0000">
            <gender>M</gender>
            <name type="Birth Name">
              <surname>Person 0</surname>
            </name>
            <eventref hlink="_e0000" role="Primary"/>
            <lds_ord type="baptism">
              <place hlink="_p0000"/>
            </lds_ord>
            <objref hlink="_o0000"/>
            <noteref hlink="_n0000"/>
            <citationref hlink="_c0000"/>
          </person>
          <person handle="_i0001" id="I0001">
            <gender>M</gender>
            <name type="Birth Name">
              <surname>Person 1</surname>
            </name>
            <eventref hlink="_e0001" role="Primary"/>
            <lds_ord type="baptism">
              <place hlink="_p0001"/>
            </lds_ord>
            <objref hlink="_o0001"/>
            <noteref hlink="_n0001"/>
            <citationref hlink="_c0001"/>
          </person>
        </people>
        <citations>
          <citation handle="_c0000" id="C0000">
              <page>p.10</page>
              <confidence>2</confidence>
              <sourceref hlink="_s0000"/>
          </citation>
          <citation handle="_c0001" id="C0001">
              <page>p.11</page>
              <confidence>2</confidence>
              <sourceref hlink="_s0001"/>
          </citation>
        </citations>
        <sources>
          <source handle="_s0000" id="S0000">
            <stitle>Source 0</stitle>
          </source>
          <source handle="_s0001" id="S0001">
            <stitle>Source 1</stitle>
          </source>
        </sources>
        <places>
          <placeobj handle="_p0000" id="P0000" type="Country">
            <ptitle>Place 0</ptitle>
            <pname value="Place 0"/>
          </placeobj>
          <placeobj handle="_p0001" id="P0001" type="Country">
            <ptitle>Place 1</ptitle>
            <pname value="Place 1"/>
          </placeobj>
        </places>
        <objects>
          <object handle="_o0000" id="O0000">
            <file src="image0.jpg" mime="image/jpeg" description="Image 0"/>
          </object>
          <object handle="_o0001" id="O0001">
            <file src="image1.jpg" mime="image/jpeg" description="Image 1"/>
          </object>
        </objects>
        <notes>
          <note handle="_n0000" id="N0000" type="Event Note">
            <text>Note 0</text>
          </note>
          <note handle="_n0001" id="N0001" type="Event Note">
            <text>Note 1</text>
          </note>
        </notes>
        </database>"""
        self.basedoc = bytes(bytearray(self.base_str + base_str,
                                       encoding='utf-8'))

    def test_event_merge(self):
        """Merge two events"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        eventref = expect.xpath("//g:person[@handle='_i0001']/g:eventref",
                                namespaces={"g": NS_G})[0]
        eventref.attrib['hlink'] = '_e0000'
        event = expect.xpath("//g:event[@handle='_e0001']",
                             namespaces={"g": NS_G})[0]
        event.getparent().remove(event)
        self.do_case('E0000', 'E0001', self.basedoc, expect)
        #print(str(ET.tostring(expect, pretty_print=True), 'utf-8'))

    def test_place_merge(self):
        """Merge two places"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        place = expect.xpath("//g:person[@handle='_i0001']/g:lds_ord/g:place",
                             namespaces={"g": NS_G})[0]
        place.attrib['hlink'] = '_p0000'
        placeobj = expect.xpath("//g:placeobj[@handle='_p0001']",
                                namespaces={"g": NS_G})[0]
        placeobj.getparent().remove(placeobj)
        placeobj = expect.xpath("//g:placeobj[@handle='_p0000']",
                                namespaces={"g": NS_G})[0]
        ET.SubElement(placeobj, NSP + 'pname', value='Place 1')
        self.do_case('P0000', 'P0001', self.basedoc, expect)

    def test_citation_merge(self):
        """Merge two citations"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        srcref = expect.xpath("//g:person[@handle='_i0001']/g:citationref",
                              namespaces={"g": NS_G})[0]
        srcref.attrib['hlink'] = '_c0000'
        citation = expect.xpath("//g:citation[@handle='_c0001']",
                                namespaces={"g": NS_G})[0]
        citation.getparent().remove(citation)
        self.do_case('C0000', 'C0001', self.basedoc, expect)

    def test_media_merge(self):
        """Merge two media objects"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        objref = expect.xpath("//g:person[@handle='_i0001']/g:objref",
                              namespaces={"g": NS_G})[0]
        objref.attrib['hlink'] = '_o0000'
        object_ = expect.xpath("//g:object[@handle='_o0001']",
                               namespaces={"g": NS_G})[0]
        object_.getparent().remove(object_)
        self.do_case('O0000', 'O0001', self.basedoc, expect)

    def test_note_merge(self):
        """Merge two notes"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        noteref = expect.xpath("//g:person[@handle='_i0001']/g:noteref",
                               namespaces={"g": NS_G})[0]
        noteref.attrib['hlink'] = '_n0000'
        note = expect.xpath("//g:note[@handle='_n0001']",
                            namespaces={"g": NS_G})[0]
        note.getparent().remove(note)
        self.do_case('N0000', 'N0001', self.basedoc, expect)


#-------------------------------------------------------------------------
#
# FamilyCheck class
#
#-------------------------------------------------------------------------
class FamilyCheck(BaseMergeCheck):
    """Class that checks what the influence is of merger of other primary
    objects on families."""
    def setUp(self):
        self.base_setup()
        base_str = """
        <events>
          <event handle="_e0000" id="E0000">
            <type>Birth</type>
            <description>Event 0</description>
          </event>
          <event handle="_e0001" id="E0001">
            <type>Birth</type>
            <description>Event 1</description>
          </event>
        </events>
        <families>
          <family handle="_f0000" id="F0000">
            <rel type="Married"/>
            <eventref hlink="_e0000" role="Family"/>
            <lds_ord type="sealed_to_spouse">
              <place hlink="_p0000"/>
            </lds_ord>
            <objref hlink="_o0000"/>
            <noteref hlink="_n0000"/>
            <citationref hlink="_c0000"/>
          </family>
          <family handle="_f0001" id="F0001">
            <rel type="Married"/>
            <eventref hlink="_e0001" role="Family"/>
            <lds_ord type="sealed_to_spouse">
              <place hlink="_p0001"/>
            </lds_ord>
            <objref hlink="_o0001"/>
            <noteref hlink="_n0001"/>
            <citationref hlink="_c0001"/>
          </family>
        </families>
        <citations>
          <citation handle="_c0000" id="C0000">
              <page>p.10</page>
              <confidence>2</confidence>
              <sourceref hlink="_s0000"/>
          </citation>
          <citation handle="_c0001" id="C0001">
              <page>p.11</page>
              <confidence>2</confidence>
              <sourceref hlink="_s0001"/>
          </citation>
        </citations>
        <sources>
          <source handle="_s0000" id="S0000">
            <stitle>Source 0</stitle>
          </source>
          <source handle="_s0001" id="S0001">
            <stitle>Source 1</stitle>
          </source>
        </sources>
        <places>
          <placeobj handle="_p0000" id="P0000" type="Country">
            <ptitle>Place 0</ptitle>
            <pname value="Place 0"/>
          </placeobj>
          <placeobj handle="_p0001" id="P0001" type="Country">
            <ptitle>Place 1</ptitle>
            <pname value="Place 1"/>
          </placeobj>
        </places>
        <objects>
          <object handle="_o0000" id="O0000">
            <file src="image0.jpg" mime="image/jpeg" description="Image 0"/>
          </object>
          <object handle="_o0001" id="O0001">
            <file src="image1.jpg" mime="image/jpeg" description="Image 1"/>
          </object>
        </objects>
        <notes>
          <note handle="_n0000" id="N0000" type="Event Note">
            <text>Note 0</text>
          </note>
          <note handle="_n0001" id="N0001" type="Event Note">
            <text>Note 1</text>
          </note>
        </notes>
        </database>"""
        self.basedoc = bytes(bytearray(self.base_str + base_str,
                                       encoding='utf-8'))

    def test_event_merge(self):
        """Merge two events"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        eventref = expect.xpath("//g:family[@handle='_f0001']/g:eventref",
                                namespaces={"g": NS_G})[0]
        eventref.attrib['hlink'] = '_e0000'
        event = expect.xpath("//g:event[@handle='_e0001']",
                             namespaces={"g": NS_G})[0]
        event.getparent().remove(event)
        self.do_case('E0000', 'E0001', self.basedoc, expect)

    def test_place_merge(self):
        """Merge two places"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        place = expect.xpath("//g:family[@handle='_f0001']/g:lds_ord/g:place",
                             namespaces={"g": NS_G})[0]
        place.attrib['hlink'] = '_p0000'
        placeobj = expect.xpath("//g:placeobj[@handle='_p0001']",
                                namespaces={"g": NS_G})[0]
        placeobj.getparent().remove(placeobj)
        placeobj = expect.xpath("//g:placeobj[@handle='_p0000']",
                                namespaces={"g": NS_G})[0]
        ET.SubElement(placeobj, NSP + 'pname', value='Place 1')
        self.do_case('P0000', 'P0001', self.basedoc, expect)

    def test_citation_merge(self):
        """Merge two citations"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        citref = expect.xpath("//g:family[@handle='_f0001']/g:citationref",
                              namespaces={"g": NS_G})[0]
        citref.attrib['hlink'] = '_c0000'
        citation = expect.xpath("//g:citation[@handle='_c0001']",
                                namespaces={"g": NS_G})[0]
        citation.getparent().remove(citation)
        self.do_case('C0000', 'C0001', self.basedoc, expect)

    def test_media_merge(self):
        """Merge two media objects"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        objref = expect.xpath("//g:family[@handle='_f0001']/g:objref",
                              namespaces={"g": NS_G})[0]
        objref.attrib['hlink'] = '_o0000'
        object_ = expect.xpath("//g:object[@handle='_o0001']",
                               namespaces={"g": NS_G})[0]
        object_.getparent().remove(object_)
        self.do_case('O0000', 'O0001', self.basedoc, expect)

    def test_note_merge(self):
        """Merge two notes"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        noteref = expect.xpath("//g:family[@handle='_f0001']/g:noteref",
                               namespaces={"g": NS_G})[0]
        noteref.attrib['hlink'] = '_n0000'
        note = expect.xpath("//g:note[@handle='_n0001']",
                            namespaces={"g": NS_G})[0]
        note.getparent().remove(note)
        self.do_case('N0000', 'N0001', self.basedoc, expect)


#-------------------------------------------------------------------------
#
# EventCheck class
#
#-------------------------------------------------------------------------
class EventCheck(BaseMergeCheck):
    """Class that checks what the influence is of merger of other primary
    objects on events."""
    def setUp(self):
        self.base_setup()
        base_str = """
        <events>
          <event handle="_e0000" id="E0000">
            <type>Birth</type>
            <place hlink="_p0000"/>
            <description>Event 0</description>
            <noteref hlink="_n0000"/>
            <citationref hlink="_c0000"/>
            <objref hlink="_o0000"/>
          </event>
          <event handle="_e0001" id="E0001">
            <type>Birth</type>
            <place hlink="_p0001"/>
            <description>Event 1</description>
            <noteref hlink="_n0001"/>
            <citationref hlink="_c0001"/>
            <objref hlink="_o0001"/>
          </event>
        </events>
        <citations>
          <citation handle="_c0000" id="C0000">
              <page>p.10</page>
              <confidence>2</confidence>
              <sourceref hlink="_s0000"/>
          </citation>
          <citation handle="_c0001" id="C0001">
              <page>p.11</page>
              <confidence>2</confidence>
              <sourceref hlink="_s0001"/>
          </citation>
        </citations>
        <sources>
          <source handle="_s0000" id="S0000">
            <stitle>Source 0</stitle>
          </source>
          <source handle="_s0001" id="S0001">
            <stitle>Source 1</stitle>
          </source>
        </sources>
        <places>
          <placeobj handle="_p0000" id="P0000" type = "Country">
            <ptitle>Place 0</ptitle>
            <pname value="Place 0"/>
          </placeobj>
          <placeobj handle="_p0001" id="P0001" type = "Country">
            <ptitle>Place 1</ptitle>
            <pname value="Place 1"/>
          </placeobj>
        </places>
        <objects>
          <object handle="_o0000" id="O0000">
            <file src="image0.jpg" mime="image/jpeg" description="Image 0"/>
          </object>
          <object handle="_o0001" id="O0001">
            <file src="image1.jpg" mime="image/jpeg" description="Image 1"/>
          </object>
        </objects>
        <notes>
          <note handle="_n0000" id="N0000" type="Event Note">
            <text>Note 0</text>
          </note>
          <note handle="_n0001" id="N0001" type="Event Note">
            <text>Note 1</text>
          </note>
        </notes>
        </database>"""
        self.basedoc = bytes(bytearray(self.base_str + base_str,
                                       encoding='utf-8'))

    def test_place_merge(self):
        """Merge two places"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        place = expect.xpath("//g:event[@handle='_e0001']/g:place",
                             namespaces={"g": NS_G})[0]
        place.attrib['hlink'] = '_p0000'
        placeobj = expect.xpath("//g:placeobj[@handle='_p0001']",
                                namespaces={"g": NS_G})[0]
        placeobj.getparent().remove(placeobj)
        placeobj = expect.xpath("//g:placeobj[@handle='_p0000']",
                                namespaces={"g": NS_G})[0]
        ET.SubElement(placeobj, NSP + 'pname', value='Place 1')
        self.do_case('P0000', 'P0001', self.basedoc, expect)

    def test_citation_merge(self):
        """Merge two citations"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        citref = expect.xpath("//g:event[@handle='_e0001']/g:citationref",
                              namespaces={"g": NS_G})[0]
        citref.attrib['hlink'] = '_c0000'
        citation = expect.xpath("//g:citation[@handle='_c0001']",
                                namespaces={"g": NS_G})[0]
        citation.getparent().remove(citation)
        self.do_case('C0000', 'C0001', self.basedoc, expect)

    def test_media_merge(self):
        """Merge two media objects"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        objref = expect.xpath("//g:event[@handle='_e0001']/g:objref",
                              namespaces={"g": NS_G})[0]
        objref.attrib['hlink'] = '_o0000'
        object_ = expect.xpath("//g:object[@handle='_o0001']",
                               namespaces={"g": NS_G})[0]
        object_.getparent().remove(object_)
        self.do_case('O0000', 'O0001', self.basedoc, expect)

    def test_note_merge(self):
        """Merge two notes"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        noteref = expect.xpath("//g:event[@handle='_e0001']/g:noteref",
                               namespaces={"g": NS_G})[0]
        noteref.attrib['hlink'] = '_n0000'
        note = expect.xpath("//g:note[@handle='_n0001']",
                            namespaces={"g": NS_G})[0]
        note.getparent().remove(note)
        self.do_case('N0000', 'N0001', self.basedoc, expect)


#-------------------------------------------------------------------------
#
# PlaceCheck class
#
#-------------------------------------------------------------------------
class PlaceCheck(BaseMergeCheck):
    """Class that checks what the influence is of merger of other primary
    objects on places."""
    def setUp(self):
        self.base_setup()
        base_str = """
        <citations>
          <citation handle="_c0000" id="C0000">
              <page>p.10</page>
              <confidence>2</confidence>
              <sourceref hlink="_s0000"/>
          </citation>
          <citation handle="_c0001" id="C0001">
              <page>p.11</page>
              <confidence>2</confidence>
              <sourceref hlink="_s0001"/>
          </citation>
        </citations>
        <sources>
          <source handle="_s0000" id="S0000">
            <stitle>Source 0</stitle>
          </source>
          <source handle="_s0001" id="S0001">
            <stitle>Source 1</stitle>
          </source>
        </sources>
        <places>
          <placeobj handle="_p0000" id="P0000" type = "Country">
            <ptitle>Place 0</ptitle>
            <pname value="Place 0"/>
            <objref hlink="_o0000"/>
            <noteref hlink="_n0000"/>
            <citationref hlink="_c0000"/>
          </placeobj>
          <placeobj handle="_p0001" id="P0001" type = "Country">
            <ptitle>Place 1</ptitle>
            <pname value="Place 1"/>
            <objref hlink="_o0001"/>
            <noteref hlink="_n0001"/>
            <citationref hlink="_c0001"/>
          </placeobj>
        </places>
        <objects>
          <object handle="_o0000" id="O0000">
            <file src="image0.jpg" mime="image/jpeg" description="Image 0"/>
          </object>
          <object handle="_o0001" id="O0001">
            <file src="image1.jpg" mime="image/jpeg" description="Image 1"/>
          </object>
        </objects>
        <notes>
          <note handle="_n0000" id="N0000" type="Event Note">
            <text>Note 0</text>
          </note>
          <note handle="_n0001" id="N0001" type="Event Note">
            <text>Note 1</text>
          </note>
        </notes>
        </database>"""
        self.basedoc = bytes(bytearray(self.base_str + base_str,
                                       encoding='utf-8'))

    def test_citation_merge(self):
        """Merge two citations"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        citref = expect.xpath("//g:placeobj[@handle='_p0001']/g:citationref",
                              namespaces={"g": NS_G})[0]
        citref.attrib['hlink'] = '_c0000'
        citation = expect.xpath("//g:citation[@handle='_c0001']",
                                namespaces={"g": NS_G})[0]
        citation.getparent().remove(citation)
        self.do_case('C0000', 'C0001', self.basedoc, expect)

    def test_media_merge(self):
        """Merge two media objects"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        objref = expect.xpath("//g:placeobj[@handle='_p0001']/g:objref",
                              namespaces={"g": NS_G})[0]
        objref.attrib['hlink'] = '_o0000'
        object_ = expect.xpath("//g:object[@handle='_o0001']",
                               namespaces={"g": NS_G})[0]
        object_.getparent().remove(object_)
        self.do_case('O0000', 'O0001', self.basedoc, expect)

    def test_note_merge(self):
        """Merge two notes"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        noteref = expect.xpath("//g:placeobj[@handle='_p0001']/g:noteref",
                               namespaces={"g": NS_G})[0]
        noteref.attrib['hlink'] = '_n0000'
        note = expect.xpath("//g:note[@handle='_n0001']",
                            namespaces={"g": NS_G})[0]
        note.getparent().remove(note)
        self.do_case('N0000', 'N0001', self.basedoc, expect)


#-------------------------------------------------------------------------
#
# SourceCheck class
#
#-------------------------------------------------------------------------
class SourceCheck(BaseMergeCheck):
    """Class that checks what the influence is of merger of other primary
    objects on sources."""
    def setUp(self):
        self.base_setup()
        base_str = """
        <citations>
          <citation handle="_c0000" id="C0000">
              <page>p.10</page>
              <confidence>2</confidence>
              <sourceref hlink="_s0000"/>
          </citation>
          <citation handle="_c0001" id="C0001">
              <page>p.11</page>
              <confidence>2</confidence>
              <sourceref hlink="_s0001"/>
          </citation>
        </citations>
        <sources>
          <source handle="_s0000" id="S0000">
            <stitle>Source 0</stitle>
            <noteref hlink="_n0000"/>
            <objref hlink="_o0000"/>
            <reporef hlink="_r0000" medium="Book"/>
          </source>
          <source handle="_s0001" id="S0001">
            <stitle>Source 1</stitle>
            <noteref hlink="_n0001"/>
            <objref hlink="_o0001"/>
            <reporef hlink="_r0001" medium="Book"/>
          </source>
        </sources>
        <objects>
          <object handle="_o0000" id="O0000">
            <file src="image0.jpg" mime="image/jpeg" description="Image 0"/>
          </object>
          <object handle="_o0001" id="O0001">
            <file src="image1.jpg" mime="image/jpeg" description="Image 1"/>
          </object>
        </objects>
        <repositories>
          <repository handle="_r0000" id="R0000">
            <rname>Repo 0</rname>
            <type>Library</type>
          </repository>
          <repository handle="_r0001" id="R0001">
            <rname>Repo 1</rname>
            <type>Library</type>
          </repository>
        </repositories>
        <notes>
          <note handle="_n0000" id="N0000" type="Event Note">
            <text>Note 0</text>
          </note>
          <note handle="_n0001" id="N0001" type="Event Note">
            <text>Note 1</text>
          </note>
        </notes>
        </database>"""
        self.basedoc = bytes(bytearray(self.base_str + base_str,
                                       encoding='utf-8'))

    #def test_citation_merge(self): SEE special cases.

    def test_repo_merge(self):
        """Merge two repositories"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        # Adjust the repository reference in expectation.
        reporef = expect.xpath("//g:source[@handle='_s0001']/g:reporef",
                               namespaces={"g": NS_G})[0]
        reporef.attrib['hlink'] = '_r0000'
        # Remove one repository in expectation.
        repo = expect.xpath("//g:repository[@handle='_r0001']",
                            namespaces={"g": NS_G})[0]
        repo.getparent().remove(repo)
        # Do the actual merger and comparison.
        self.do_case('R0000', 'R0001', self.basedoc, expect)

    def test_media_merge(self):
        """Merge two media objects"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        objref = expect.xpath("//g:source[@handle='_s0001']/g:objref",
                              namespaces={"g": NS_G})[0]
        objref.attrib['hlink'] = '_o0000'
        object_ = expect.xpath("//g:object[@handle='_o0001']",
                               namespaces={"g": NS_G})[0]
        object_.getparent().remove(object_)
        self.do_case('O0000', 'O0001', self.basedoc, expect)

    def test_note_merge(self):
        """Merge two notes"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        noteref = expect.xpath("//g:source[@handle='_s0001']/g:noteref",
                               namespaces={"g": NS_G})[0]
        noteref.attrib['hlink'] = '_n0000'
        note = expect.xpath("//g:note[@handle='_n0001']",
                            namespaces={"g": NS_G})[0]
        note.getparent().remove(note)
        self.do_case('N0000', 'N0001', self.basedoc, expect)


#-------------------------------------------------------------------------
#
# RepoCheck class
#
#-------------------------------------------------------------------------
class RepoCheck(BaseMergeCheck):
    """Class that checks what the influence is of merger of other primary
    objects on repositories."""
    def setUp(self):
        self.base_setup()
        base_str = """
        <citations>
          <citation handle="_c0000" id="C0000">
              <page>p.10</page>
              <confidence>2</confidence>
              <sourceref hlink="_s0000"/>
          </citation>
          <citation handle="_c0001" id="C0001">
              <page>p.11</page>
              <confidence>2</confidence>
              <sourceref hlink="_s0001"/>
          </citation>
        </citations>
        <sources>
          <source handle="_s0000" id="S0000">
            <stitle>Source 0</stitle>
          </source>
          <source handle="_s0001" id="S0001">
            <stitle>Source 1</stitle>
          </source>
        </sources>
        <repositories>
          <repository handle="_r0000" id="R0000">
            <rname>Repo 0</rname>
            <type>Library</type>
            <address>
              <city>Amsterdam</city>
              <citationref hlink="_c0000"/>
            </address>
            <noteref hlink="_n0000"/>
          </repository>
          <repository handle="_r0001" id="R0001">
            <rname>Repo 1</rname>
            <type>Library</type>
            <address>
              <city>Rotterdam</city>
              <citationref hlink="_c0001"/>
            </address>
            <noteref hlink="_n0001"/>
          </repository>
        </repositories>
        <notes>
          <note handle="_n0000" id="N0000" type="Event Note">
            <text>Note 0</text>
          </note>
          <note handle="_n0001" id="N0001" type="Event Note">
            <text>Note 1</text>
          </note>
        </notes>
        </database>"""
        self.basedoc = bytes(bytearray(self.base_str + base_str,
                                       encoding='utf-8'))

    def test_citation_merge(self):
        """Merge two citations"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        citref = expect.xpath("//g:repository[@handle='_r0001']"
                              "/g:address/g:citationref",
                              namespaces={"g": NS_G})[0]
        citref.attrib['hlink'] = '_c0000'
        citation = expect.xpath("//g:citation[@handle='_c0001']",
                                namespaces={"g": NS_G})[0]
        citation.getparent().remove(citation)
        self.do_case('C0000', 'C0001', self.basedoc, expect)

    def test_note_merge(self):
        """Merge two notes"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        noteref = expect.xpath("//g:repository[@handle='_r0001']/g:noteref",
                               namespaces={"g": NS_G})[0]
        noteref.attrib['hlink'] = '_n0000'
        note = expect.xpath("//g:note[@handle='_n0001']",
                            namespaces={"g": NS_G})[0]
        note.getparent().remove(note)
        self.do_case('N0000', 'N0001', self.basedoc, expect)


#-------------------------------------------------------------------------
#
# MediaCheck class
#
#-------------------------------------------------------------------------
class MediaCheck(BaseMergeCheck):
    """Class that checks what the influence is of merger of other primary
    objects on media objects."""
    def setUp(self):
        self.base_setup()
        base_str = """
        <citations>
          <citation handle="_c0000" id="C0000">
              <page>p.10</page>
              <confidence>2</confidence>
              <sourceref hlink="_s0000"/>
          </citation>
          <citation handle="_c0001" id="C0001">
              <page>p.11</page>
              <confidence>2</confidence>
              <sourceref hlink="_s0001"/>
          </citation>
        </citations>
        <sources>
          <source handle="_s0000" id="S0000">
            <stitle>Source 0</stitle>
          </source>
          <source handle="_s0001" id="S0001">
            <stitle>Source 1</stitle>
          </source>
        </sources>
        <objects>
          <object handle="_o0000" id="O0000">
            <file src="image0.jpg" mime="image/jpeg" description="Image 0"/>
            <noteref hlink="_n0000"/>
            <citationref hlink="_c0000"/>
          </object>
          <object handle="_o0001" id="O0001">
            <file src="image1.jpg" mime="image/jpeg" description="Image 1"/>
            <noteref hlink="_n0001"/>
            <citationref hlink="_c0001"/>
          </object>
        </objects>
        <notes>
          <note handle="_n0000" id="N0000" type="Event Note">
            <text>Note 0</text>
          </note>
          <note handle="_n0001" id="N0001" type="Event Note">
            <text>Note 1</text>
          </note>
        </notes>
        </database>"""
        self.basedoc = bytes(bytearray(self.base_str + base_str,
                                       encoding='utf-8'))

    def test_citation_merge(self):
        """Merge two citations"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        citref = expect.xpath("//g:object[@handle='_o0001']/g:citationref",
                              namespaces={"g": NS_G})[0]
        citref.attrib['hlink'] = '_c0000'
        citation = expect.xpath("//g:citation[@handle='_c0001']",
                                namespaces={"g": NS_G})[0]
        citation.getparent().remove(citation)
        self.do_case('C0000', 'C0001', self.basedoc, expect)

    def test_note_merge(self):
        """Merge two notes"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        noteref = expect.xpath("//g:object[@handle='_o0001']/g:noteref",
                               namespaces={"g": NS_G})[0]
        noteref.attrib['hlink'] = '_n0000'
        note = expect.xpath("//g:note[@handle='_n0001']",
                            namespaces={"g": NS_G})[0]
        note.getparent().remove(note)
        self.do_case('N0000', 'N0001', self.basedoc, expect)

#=========================================================================
#
# Special cases
#
#=========================================================================


#-------------------------------------------------------------------------
#
# SourceSourceCheck class
#
#-------------------------------------------------------------------------
class SourceSourceCheck(BaseMergeCheck):
    def setUp(self):
        self.base_setup()
        base_str = """
        <citations>
          <citation handle="_c0000" id="C0000">
              <page>p.10</page>
              <confidence>2</confidence>
              <objref hlink="_o0000">
                <citationref hlink="_c0002"/>
              </objref>
              <sourceref hlink="_s0000"/>
          </citation>
          <citation handle="_c0001" id="C0001">
              <page>p.11</page>
              <confidence>2</confidence>
              <objref hlink="_o0001">
                <citationref hlink="_c0003"/>
              </objref>
              <sourceref hlink="_s0000"/>
          </citation>
          <citation handle="_c0002" id="C0002">
              <page>p.12</page>
              <confidence>2</confidence>
              <sourceref hlink="_s0001"/>
          </citation>
          <citation handle="_c0003" id="C0003">
              <page>p.13</page>
              <confidence>2</confidence>
              <sourceref hlink="_s0001"/>
          </citation>
        </citations>
        <sources>
          <source handle="_s0000" id="S0000">
            <stitle>Source 0</stitle>
          </source>
          <source handle="_s0001" id="S0001">
            <stitle>Source 1</stitle>
          </source>
        </sources>
        <objects>
          <object handle="_o0000" id="O0000">
            <file src="image0.jpg" mime="image/jpeg" description="Image 0"/>
          </object>
          <object handle="_o0001" id="O0001">
            <file src="image1.jpg" mime="image/jpeg" description="Image 1"/>
          </object>
        </objects>
        </database>"""
        self.basedoc = bytes(bytearray(self.base_str + base_str,
                                       encoding='utf-8'))

    def test_citation_merge(self):
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        citrefs = expect.xpath("//g:citation[@handle='_c0001']"
                               "/g:objref/g:citationref",
                               namespaces={"g": NS_G})
        citrefs[0].attrib['hlink'] = '_c0002'
        citations = expect.xpath("//g:citation[@handle='_c0003']",
                                 namespaces={"g": NS_G})
        citations[0].getparent().remove(citations[0])
        self.do_case('C0002', 'C0003', self.basedoc, expect)

    def test_citation_cross_merge(self):
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        input_citrefs = input_ctxt.xpath("//g:citation/g:objref/g:citationref",
                                         namespaces={"g": NS_G})
        input_citrefs[0].attrib['hlink'] = '_c0001'
        input_citrefs[1].attrib['hlink'] = '_c0000'
        rmcit = input_ctxt.xpath("//g:citation[@handle='_c0002']",
                                 namespaces={"g": NS_G})
        rmcit[0].getparent().remove(rmcit[0])
        rmcit = input_ctxt.xpath("//g:citation[@handle='_c0003']",
                                 namespaces={"g": NS_G})
        rmcit[0].getparent().remove(rmcit[0])
        rmsrc = input_ctxt.xpath("//g:source[@handle='_s0001']",
                                 namespaces={"g": NS_G})
        rmsrc[0].getparent().remove(rmsrc[0])
        expect = copy.deepcopy(input_ctxt)
        citrefs = expect.xpath("//g:citation[@handle='_c0000']/g:objref"
                               "/g:citationref", namespaces={"g": NS_G})
        citrefs[0].attrib['hlink'] = '_c0000'
        # add objref
        objref = expect.xpath("//g:citation[@handle='_c0000']/g:objref",
                              namespaces={"g": NS_G})
        objref2 = expect.xpath("//g:citation[@handle='_c0001']/g:objref",
                               namespaces={"g": NS_G})
        #objref[0].addNextSibling(objref2[0])
        objref[0].addnext(objref2[0])
        # remove citation
        citations = expect.xpath("//g:citation[@handle='_c0001']",
                                 namespaces={"g": NS_G})
        citations[0].getparent().remove(citations[0])
        input_doc = ET.tostring(input_ctxt)
        self.do_case('C0000', 'C0001', input_doc, expect)


#-------------------------------------------------------------------------
#
# BirthCheck class
#
#-------------------------------------------------------------------------
class BirthCheck(BaseMergeCheck):
    def setUp(self):
        self.base_setup()
        base_str = """
        <events>
          <event handle="_e0000" id="E0000">
            <type>Baptism</type>
            <description>Event 0</description>
          </event>
          <event handle="_e0001" id="E0001">
            <type>Birth</type>
            <description>Event 1</description>
          </event>
          <event handle="_e0002" id="E0002">
            <type>Death</type>
            <description>Event 2</description>
          </event>
        </events>
        <people>
          <person handle="_i0000" id="I0000">
            <gender>M</gender>
            <name type="Birth Name">
              <surname>Person 0</surname>
            </name>
            <eventref hlink="_e0000" role="Primary"/>
            <eventref hlink="_e0001" role="Primary"/>
            <eventref hlink="_e0002" role="Primary"/>
          </person>
        </people>
        </database>"""
        self.basedoc = bytes(bytearray(self.base_str + base_str,
                                       encoding='utf-8'))
        surname = Surname()
        surname.set_surname("Person 0")
        surname.set_prefix("")
        surname.set_connector("")
        name = Name()
        name.add_surname(surname)
        self.expect_str = "person: i0000 ('i0000', 'I0000', 1, %s, [], " % str(
                          name.serialize())

    def test_birth_loss(self):
        # check that birth_ref_index is -1
        # input_doc = ET.fromstring(self.basedoc, parser=self.parser)
        expect_str = self.expect_str + "1, -1"
        self.raw_contains('E0000', 'E0001', self.basedoc, expect_str)

    def test_second_birth(self):
        # check that birth _ref_index is 2
        input_doc = ET.fromstring(self.basedoc, parser=self.parser)
        events = input_doc.xpath("//g:events",
                                 namespaces={"g": NS_G})[0]
        second_birth = ET.SubElement(events, NSP + 'event',
                                     handle='_e0003', id='E0003')
        birthtype = ET.SubElement(second_birth, NSP + 'type')
        birthtype.text = 'Birth'
        birthdesc = ET.SubElement(second_birth, NSP + 'description')
        birthdesc.text = 'Event 3'
        person = input_doc.xpath("//g:person[@handle='_i0000']",
                                 namespaces={"g": NS_G})[0]
        ET.SubElement(person, NSP + 'eventref', hlink='_e0003', role='Primary')
        expect_str = self.expect_str + "1, 2"
        input_str = ET.tostring(input_doc)
        self.raw_contains('E0000', 'E0001', input_str, expect_str)

    def test_death_merge(self):
        # check that death_ref_index is -1
        expect_str = self.expect_str + "-1, 1"
        self.raw_contains('E0000', 'E0002', self.basedoc, expect_str)

    def test_second_death(self):
        # check that death _ref_index is 2
        input_doc = ET.fromstring(self.basedoc, parser=self.parser)
        events = input_doc.xpath("//g:events",
                                 namespaces={"g": NS_G})[0]
        second_death = ET.SubElement(events, NSP + 'event',
                                     handle='_e0003', id='E0003')
        deathtype = ET.SubElement(second_death, NSP + 'type')
        deathtype.text = 'Death'
        deathdesc = ET.SubElement(second_death, NSP + 'description')
        deathdesc.text = 'Event 3'
        person = input_doc.xpath("//g:person[@handle='_i0000']",
                                 namespaces={"g": NS_G})[0]
        ET.SubElement(person, NSP + 'eventref', hlink='_e0003', role='Primary')
        expect_str = self.expect_str + "2, 1"
        input_str = ET.tostring(input_doc)
        self.raw_contains('E0000', 'E0002', input_str, expect_str)


#-------------------------------------------------------------------------
#
# PersonPersonCheck class
#
#-------------------------------------------------------------------------
class PersonPersonCheck(BaseMergeCheck):
    def setUp(self):
        self.base_setup()
        base_str = """
        <people>
          <person handle="_i0000" id="I0000">
            <gender>M</gender>
            <name type="Birth Name">
              <surname>Person 0</surname>
            </name>
          </person>
          <person handle="_i0001" id="I0001">
            <gender>M</gender>
            <name type="Birth Name">
              <surname>Person 1</surname>
            </name>
          </person>
        </people>
        </database>"""
        self.basedoc = bytes(bytearray(self.base_str + base_str,
                                       encoding='utf-8'))

    def test_person_merge(self):
        """There is a person not involved in merger that references Titanic."""
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        people = input_ctxt.xpath("//g:people",
                                  namespaces={"g": NS_G})[0]
        person = ET.SubElement(people, NSP + 'person',
                               handle='_i0002', id='I0002')
        ET.SubElement(person, NSP + 'gender').text = 'M'
        name = ET.SubElement(person, NSP + 'name', type='Birth Name')
        ET.SubElement(name, NSP + 'surname').text = 'Person 2'
        ET.SubElement(person, NSP + 'personref',
                      hlink='_i0001', rel='Neighbour')
        expect = copy.deepcopy(input_ctxt)
        personref = expect.xpath("//g:personref",
                                 namespaces={"g": NS_G})[0]
        personref.attrib['hlink'] = '_i0000'
        person = expect.xpath("//g:person[@handle='_i0000']",
                              namespaces={"g": NS_G})[0]
        altname = ET.SubElement(person, NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 1'
        ET.SubElement(person, NSP + 'attribute',
                      type='Merged Gramps ID', value='I0001')
        person = expect.xpath("//g:person[@handle='_i0001']",
                              namespaces={"g": NS_G})[0]
        person.getparent().remove(person)
        input_doc = ET.tostring(input_ctxt)
        self.do_case('I0000', 'I0001', input_doc, expect)

    def test_person_cross(self):
        """Phoenix has ref to Titanic and vice versa"""
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        persons = input_ctxt.xpath("//g:person",
                                   namespaces={"g": NS_G})
        ET.SubElement(persons[0], NSP + 'personref',
                      hlink='_i0001', rel='Neighbour East')
        ET.SubElement(persons[1], NSP + 'personref',
                      hlink='_i0000', rel='Neighbour West')

        expect = copy.deepcopy(input_ctxt)
        personref = expect.xpath("//g:person[@handle='_i0000']/g:personref",
                                 namespaces={"g": NS_G})[0]
        personref.attrib['hlink'] = '_i0000'
        person = expect.xpath("//g:person[@handle='_i0000']",
                              namespaces={"g": NS_G})[0]
        altname = ET.SubElement(person, NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 1'
        ET.SubElement(person, NSP + 'attribute',
                      type='Merged Gramps ID', value='I0001')
        person.append(personref)  # restore order of elements
        personref = ET.SubElement(person, NSP + 'personref',
                                  hlink='_i0000', rel='Neighbour West')
        person = expect.xpath("//g:person[@handle='_i0001']",
                              namespaces={"g": NS_G})[0]
        person.getparent().remove(person)
        input_doc = ET.tostring(input_ctxt)
        self.do_case('I0000', 'I0001', input_doc, expect)

    def test_person_self(self):
        """Titanic references itself"""
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        person = input_ctxt.xpath("//g:person[@handle='_i0001']",
                                  namespaces={"g": NS_G})[0]
        ET.SubElement(person, NSP + 'personref',
                      hlink='_i0001', rel='Neighbour')
        expect = copy.deepcopy(input_ctxt)
        person = expect.xpath("//g:person[@handle='_i0000']",
                              namespaces={"g": NS_G})[0]
        altname = ET.SubElement(person, NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 1'
        ET.SubElement(person, NSP + 'attribute',
                      type='Merged Gramps ID', value='I0001')
        ET.SubElement(person, NSP + 'personref',
                      hlink='_i0000', rel='Neighbour')
        person = expect.xpath("//g:person[@handle='_i0001']",
                              namespaces={"g": NS_G})[0]
        person.getparent().remove(person)
        input_doc = ET.tostring(input_ctxt)
        self.do_case('I0000', 'I0001', input_doc, expect)


#-------------------------------------------------------------------------
#
# ParentFamilyPersonCheck class
#
#-------------------------------------------------------------------------
class ParentFamilyPersonCheck(BaseMergeCheck):
    def setUp(self):
        self.base_setup()
        base_str = """
        <people>
          <person handle="_i0000" id="I0000">
            <gender>M</gender>
            <name type="Birth Name">
              <surname>Person 0</surname>
            </name>
            <childof hlink="_f0000"/>
          </person>
          <person handle="_i0001" id="I0001">
            <gender>M</gender>
            <name type="Birth Name">
              <surname>Person 1</surname>
            </name>
            <childof hlink="_f0001"/>
          </person>
        </people>
        <families>
          <family handle="_f0000" id="F0000">
            <rel type="Unknown"/>
            <childref hlink="_i0000"/>
          </family>
          <family handle="_f0001" id="F0001">
            <rel type="Unknown"/>
            <childref hlink="_i0001"/>
          </family>
        </families>
        </database>"""
        self.basedoc = bytes(bytearray(self.base_str + base_str,
                                       encoding='utf-8'))

    def test_person_merge(self):
        """Merge two persons that are children in some family"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        childref = expect.xpath("//g:family[@handle='_f0001']/g:childref",
                                namespaces={"g": NS_G})[0]
        childref.attrib['hlink'] = '_i0000'

        persons = expect.xpath("//g:person",
                               namespaces={"g": NS_G})
        altname = ET.SubElement(persons[0], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 1'
        attr = ET.SubElement(persons[0], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0001')
        childof = expect.xpath("//g:person[@handle='_i0000']/g:childof",
                               namespaces={"g": NS_G})[0]
        attr.addnext(childof)  # restore order of elements
        childof = ET.SubElement(persons[0], NSP + 'childof', hlink='_f0001')
        persons[1].getparent().remove(persons[1])
        self.do_case('I0000', 'I0001', self.basedoc, expect)


#-------------------------------------------------------------------------
#
# FamilyPersonCheck class
#
#-------------------------------------------------------------------------
class FamilyPersonCheck(BaseMergeCheck):
    """Merge two persons that are parents in families"""
    def setUp(self):
        self.base_setup()
        base_str = """
        <people>
          <person handle="_i0000" id="I0000">
            <gender>M</gender>
            <name type="Birth Name">
              <surname>Person 0</surname>
            </name>
            <parentin hlink="_f0000"/>
          </person>
          <person handle="_i0001" id="I0001">
            <gender>F</gender>
            <name type="Birth Name">
              <surname>Person 1</surname>
            </name>
            <parentin hlink="_f0000"/>
          </person>
          <person handle="_i0002" id="I0002">
            <gender>M</gender>
            <name type="Birth Name">
              <surname>Person 2</surname>
            </name>
          </person>
          <person handle="_i0003" id="I0003">
            <gender>F</gender>
            <name type="Birth Name">
              <surname>Person 3</surname>
            </name>
          </person>
        </people>
        <families>
          <family handle="_f0000" id="F0000">
            <rel type="Unknown"/>
            <father hlink="_i0000"/>
            <mother hlink="_i0001"/>
          </family>
          <family handle="_f0001" id="F0001">
            <rel type="Unknown"/>
          </family>
        </families>
        </database>"""
        self.basedoc = bytes(bytearray(self.base_str + base_str,
                                       encoding='utf-8'))

    def test_titanic_no_fam(self):
        "Test merge of two persons where titanic is not a parent in a family"
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        persons = expect.xpath("//g:person",
                               namespaces={"g": NS_G})
        altname = ET.SubElement(persons[0], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 2'
        attr = ET.SubElement(persons[0], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0002')
        parentref = expect.xpath("//g:person[@handle='_i0000']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        persons[2].getparent().remove(persons[2])
        self.do_case('I0000', 'I0002', self.basedoc, expect)

    def test_no_fam_merge(self):
        """Test merge of two persons, both parents in a family, but such that
        the families will not merge."""
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        person = input_ctxt.xpath("//g:person[@handle='_i0002']",
                                  namespaces={"g": NS_G})[0]
        ET.SubElement(person, NSP + 'parentin', hlink='_f0001')
        family = input_ctxt.xpath("//g:family[@handle='_f0001']",
                                  namespaces={"g": NS_G})[0]
        ET.SubElement(family, NSP + 'father', hlink='_i0002')
        expect = copy.deepcopy(input_ctxt)
        persons = expect.xpath("//g:person",
                               namespaces={"g": NS_G})
        altname = ET.SubElement(persons[0], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 2'
        attr = ET.SubElement(persons[0], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0002')
        parentref = expect.xpath("//g:person[@handle='_i0000']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        ET.SubElement(persons[0], NSP + 'parentin', hlink='_f0001')
        father = expect.xpath("//g:family[@handle='_f0001']/g:father",
                              namespaces={"g": NS_G})[0]
        father.attrib['hlink'] = '_i0000'
        persons[2].getparent().remove(persons[2])
        input_doc = ET.tostring(input_ctxt)
        self.do_case('I0000', 'I0002', input_doc, expect)

    def test_multi_rel(self):
        """Merge two persons where titanic has multiple family relationships
        with his partner, this should raise an error."""
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        expect = copy.deepcopy(input_ctxt)
        persons = expect.xpath("//g:person",
                               namespaces={"g": NS_G})
        altname = ET.SubElement(persons[0], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 2'
        attr = ET.SubElement(persons[0], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0002')
        parentref = expect.xpath("//g:person[@handle='_i0000']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        ET.SubElement(persons[0], NSP + 'parentin', hlink='_f0001')
        ET.SubElement(persons[3], NSP + 'parentin', hlink='_f0001')
        ET.SubElement(persons[0], NSP + 'parentin', hlink='_f0002')
        ET.SubElement(persons[3], NSP + 'parentin', hlink='_f0002')
        family = expect.xpath("//g:family[@handle='_f0001']",
                              namespaces={"g": NS_G})[0]
        ET.SubElement(family, NSP + 'father', hlink='_i0000')
        ET.SubElement(family, NSP + 'mother', hlink='_i0003')
        families = expect.xpath("//g:families",
                                namespaces={"g": NS_G})[0]
        family = ET.SubElement(families, NSP + 'family',
                               handle='_f0002', id='F0002')
        ET.SubElement(family, NSP + 'rel', type='Married')
        ET.SubElement(family, NSP + 'father', hlink='_i0000')
        ET.SubElement(family, NSP + 'mother', hlink='_i0003')
        persons[2].getparent().remove(persons[2])

        persons = input_ctxt.xpath("//g:person",
                                   namespaces={"g": NS_G})
        ET.SubElement(persons[2], NSP + 'parentin', hlink='_f0001')
        ET.SubElement(persons[3], NSP + 'parentin', hlink='_f0001')
        ET.SubElement(persons[2], NSP + 'parentin', hlink='_f0002')
        ET.SubElement(persons[3], NSP + 'parentin', hlink='_f0002')
        family = input_ctxt.xpath("//g:family[@handle='_f0001']",
                                  namespaces={"g": NS_G})[0]
        ET.SubElement(family, NSP + 'father', hlink='_i0002')
        ET.SubElement(family, NSP + 'mother', hlink='_i0003')
        families = input_ctxt.xpath("//g:families",
                                    namespaces={"g": NS_G})[0]
        family = ET.SubElement(families, NSP + 'family',
                               handle='_f0002', id='F0002')
        ET.SubElement(family, NSP + 'rel', type='Married')
        ET.SubElement(family, NSP + 'father', hlink='_i0002')
        ET.SubElement(family, NSP + 'mother', hlink='_i0003')
        input_doc = ET.tostring(input_ctxt)
        self.do_case('I0000', 'I0002', input_doc, expect,
                     test_error_str="")

    def test_merge_fam(self):
        """Merge two persons such that also the families in which they are
        parents get merged."""
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        persons = input_ctxt.xpath("//g:person",
                                   namespaces={"g": NS_G})
        ET.SubElement(persons[1], NSP + 'parentin', hlink='_f0001')
        ET.SubElement(persons[2], NSP + 'parentin', hlink='_f0001')
        family = input_ctxt.xpath("//g:family[@handle='_f0001']",
                                  namespaces={"g": NS_G})[0]
        ET.SubElement(family, NSP + 'father', hlink='_i0002')
        ET.SubElement(family, NSP + 'mother', hlink='_i0001')
        expect = copy.deepcopy(input_ctxt)
        persons = expect.xpath("//g:person",
                               namespaces={"g": NS_G})
        altname = ET.SubElement(persons[0], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 2'
        attr = ET.SubElement(persons[0], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0002')
        parentref = expect.xpath("//g:person[@handle='_i0000']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        persons[2].getparent().remove(persons[2])
        family = expect.xpath("//g:family[@handle='_f0001']",
                              namespaces={"g": NS_G})[0]
        family.getparent().remove(family)
        parentin = expect.xpath("//g:person[@handle='_i0001']/g:parentin",
                                namespaces={"g": NS_G})[1]
        parentin.getparent().remove(parentin)
        input_doc = ET.tostring(input_ctxt)
        self.do_case('I0000', 'I0002', input_doc, expect)

    def test_fam_none_merge(self):
        """Merge two persons, both father in families without mothers."""
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        parentin = input_ctxt.xpath("//g:person[@handle='_i0001']/g:parentin",
                                    namespaces={"g": NS_G})[0]
        parentin.getparent().remove(parentin)
        mother = input_ctxt.xpath("//g:family[@handle='_f0000']/g:mother",
                                  namespaces={"g": NS_G})[0]
        mother.getparent().remove(mother)
        family = input_ctxt.xpath("//g:family[@handle='_f0001']",
                                  namespaces={"g": NS_G})[0]
        ET.SubElement(family, NSP + 'father', hlink='_i0002')
        person = input_ctxt.xpath("//g:person[@handle='_i0002']",
                                  namespaces={"g": NS_G})[0]
        parentin = ET.SubElement(person, NSP + 'parentin', hlink='_f0001', )
        expect = copy.deepcopy(input_ctxt)
        persons = expect.xpath("//g:person",
                               namespaces={"g": NS_G})
        altname = ET.SubElement(persons[0], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 2'
        attr = ET.SubElement(persons[0], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0002')
        parentref = expect.xpath("//g:person[@handle='_i0000']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        persons[2].getparent().remove(persons[2])
        family = expect.xpath("//g:family[@handle='_f0001']",
                              namespaces={"g": NS_G})[0]
        family.getparent().remove(family)
        input_doc = ET.tostring(input_ctxt)
        self.do_case('I0000', 'I0002', input_doc, expect)

    # Can't think of a testcase that would merge multiple families.

    def test_fam_mother_merge(self):
        """Merge two persons that are mothers in their respective families."""
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        persons = input_ctxt.xpath("//g:person",
                                   namespaces={"g": NS_G})
        ET.SubElement(persons[0], NSP + 'parentin', hlink='_f0001')
        ET.SubElement(persons[3], NSP + 'parentin', hlink='_f0001')
        family = input_ctxt.xpath("//g:family[@handle='_f0001']",
                                  namespaces={"g": NS_G})[0]
        ET.SubElement(family, NSP + 'father', hlink='_i0000')
        ET.SubElement(family, NSP + 'mother', hlink='_i0003')
        expect = copy.deepcopy(input_ctxt)
        persons = expect.xpath("//g:person",
                               namespaces={"g": NS_G})
        altname = ET.SubElement(persons[1], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 3'
        attr = ET.SubElement(persons[1], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0003')
        parentref = expect.xpath("//g:person[@handle='_i0001']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        persons[3].getparent().remove(persons[3])
        family = expect.xpath("//g:family[@handle='_f0001']",
                              namespaces={"g": NS_G})[0]
        family.getparent().remove(family)
        parentin = expect.xpath("//g:person[@handle='_i0000']/g:parentin",
                                namespaces={"g": NS_G})[1]
        parentin.getparent().remove(parentin)
        input_doc = ET.tostring(input_ctxt)
        self.do_case('I0001', 'I0003', input_doc, expect)

    def test_childref_notyet(self):
        """Merge two people leading to merger of families that have children.
        """
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        parentin = input_ctxt.xpath("//g:person[@handle='_i0001']/g:parentin",
                                    namespaces={"g": NS_G})[0]
        parentin.getparent().remove(parentin)
        mother = input_ctxt.xpath("//g:family[@handle='_f0000']/g:mother",
                                  namespaces={"g": NS_G})[0]
        mother.getparent().remove(mother)
        persons = input_ctxt.xpath("//g:person",
                                   namespaces={"g": NS_G})
        ET.SubElement(persons[1], NSP + 'childof', hlink='_f0000')
        families = input_ctxt.xpath("//g:family",
                                    namespaces={"g": NS_G})
        ET.SubElement(families[0], NSP + 'childref', hlink='_i0001')
        parentin = ET.SubElement(persons[2], NSP + 'parentin', hlink='_f0001')
        ET.SubElement(families[1], NSP + 'father', hlink='_i0002')
        ET.SubElement(persons[3], NSP + 'childof', hlink='_f0001')
        ET.SubElement(families[1], NSP + 'childref', hlink='_i0003')
        expect = copy.deepcopy(input_ctxt)
        persons = expect.xpath("//g:person",
                               namespaces={"g": NS_G})
        altname = ET.SubElement(persons[0], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 2'
        attr = ET.SubElement(persons[0], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0002')
        parentref = expect.xpath("//g:person[@handle='_i0000']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        persons[2].getparent().remove(persons[2])
        families = expect.xpath("//g:family",
                                namespaces={"g": NS_G})
        families[1].getparent().remove(families[1])
        childof = expect.xpath("//g:person[@handle='_i0003']/g:childof",
                               namespaces={"g": NS_G})[0]
        childof.attrib['hlink'] = '_f0000'
        ET.SubElement(families[0], NSP + 'childref', hlink='_i0003')
        input_doc = ET.tostring(input_ctxt)
        self.do_case('I0000', 'I0002', input_doc, expect)

    def test_childref_already(self):
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        parentin = input_ctxt.xpath("//g:person[@handle='_i0001']/g:parentin",
                                    namespaces={"g": NS_G})[0]
        parentin.getparent().remove(parentin)
        mother = input_ctxt.xpath("//g:family[@handle='_f0000']/g:mother",
                                  namespaces={"g": NS_G})[0]
        mother.getparent().remove(mother)
        persons = input_ctxt.xpath("//g:person",
                                   namespaces={"g": NS_G})
        ET.SubElement(persons[1], NSP + 'childof', hlink='_f0000')
        ET.SubElement(persons[1], NSP + 'childof', hlink='_f0001')
        families = input_ctxt.xpath("//g:family",
                                    namespaces={"g": NS_G})
        ET.SubElement(families[0], NSP + 'childref', hlink='_i0001')
        parentin = ET.SubElement(persons[2], NSP + 'parentin', hlink='_f0001')
        ET.SubElement(families[1], NSP + 'father', hlink='_i0002')
        ET.SubElement(families[1], NSP + 'childref', hlink='_i0001')
        expect = copy.deepcopy(input_ctxt)
        persons = expect.xpath("//g:person",
                               namespaces={"g": NS_G})
        altname = ET.SubElement(persons[0], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 2'
        attr = ET.SubElement(persons[0], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0002')
        parentref = expect.xpath("//g:person[@handle='_i0000']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        persons[2].getparent().remove(persons[2])
        families = expect.xpath("//g:family",
                                namespaces={"g": NS_G})
        families[1].getparent().remove(families[1])
        childof = expect.xpath("//g:person[@handle='_i0001']/g:childof",
                               namespaces={"g": NS_G})
        childof[1].getparent().remove(childof[1])
        input_doc = ET.tostring(input_ctxt)
        self.do_case('I0000', 'I0002', input_doc, expect)

    def test_ldsord(self):
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        parentin = input_ctxt.xpath("//g:person[@handle='_i0001']/g:parentin",
                                    namespaces={"g": NS_G})[0]
        parentin.getparent().remove(parentin)
        mother = input_ctxt.xpath("//g:family[@handle='_f0000']/g:mother",
                                  namespaces={"g": NS_G})[0]
        mother.getparent().remove(mother)
        persons = input_ctxt.xpath("//g:person",
                                   namespaces={"g": NS_G})
        parentin = ET.SubElement(persons[2], NSP + 'parentin', hlink='_f0001')
        family = input_ctxt.xpath("//g:family[@handle='_f0001']",
                                  namespaces={"g": NS_G})[0]
        ET.SubElement(family, NSP + 'father', hlink='_i0002')
        ldsord = ET.SubElement(persons[3], NSP + 'lds_ord',
                               type='sealed_to_parents')
        ET.SubElement(ldsord, NSP + 'sealed_to', hlink='_f0001')
        expect = copy.deepcopy(input_ctxt)
        persons = expect.xpath("//g:person",
                               namespaces={"g": NS_G})
        altname = ET.SubElement(persons[0], NSP + 'name', alt='1',
                                type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 2'
        attr = ET.SubElement(persons[0], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0002')
        parentref = expect.xpath("//g:person[@handle='_i0000']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        persons[2].getparent().remove(persons[2])
        families = expect.xpath("//g:family",
                                namespaces={"g": NS_G})
        families[1].getparent().remove(families[1])
        sealedto = expect.xpath("//g:sealed_to",
                                namespaces={"g": NS_G})[0]
        sealedto.attrib['hlink'] = '_f0000'
        input_doc = ET.tostring(input_ctxt)
        self.do_case('I0000', 'I0002', input_doc, expect)

    # This test fails because the assigment of family ids shifts F0000 to F0001
    # and F0001 to F0002!
    def test_ldsord_cross(self):
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        parentin = input_ctxt.xpath("//g:person[@handle='_i0001']/g:parentin",
                                    namespaces={"g": NS_G})[0]
        parentin.getparent().remove(parentin)
        mother = input_ctxt.xpath("//g:family[@handle='_f0000']/g:mother",
                                  namespaces={"g": NS_G})[0]
        mother.getparent().remove(mother)
        persons = input_ctxt.xpath("//g:person",
                                   namespaces={"g": NS_G})
        parentin = ET.SubElement(persons[2], NSP + 'parentin', hlink='_f0001')
        family = input_ctxt.xpath("//g:family[@handle='_f0001']",
                                  namespaces={"g": NS_G})[0]
        ET.SubElement(family, NSP + 'father', hlink='_i0002')
        ldsord = ET.SubElement(persons[0], NSP + 'lds_ord',
                               type='sealed_to_parents')
        ET.SubElement(ldsord, NSP + 'sealed_to', hlink='_f0001')
        expect = copy.deepcopy(input_ctxt)
        persons = expect.xpath("//g:person",
                               namespaces={"g": NS_G})
        altname = ET.SubElement(persons[0], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 2'
        ldsord = expect.xpath("//g:lds_ord",
                              namespaces={"g": NS_G})[0]
        altname.addnext(ldsord)  # restore order of elements
        attr = ET.SubElement(persons[0], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0002')
        parentref = expect.xpath("//g:person[@handle='_i0000']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        persons[2].getparent().remove(persons[2])
        families = expect.xpath("//g:family",
                                namespaces={"g": NS_G})
        families[1].getparent().remove(families[1])
        sealedto = expect.xpath("//g:sealed_to",
                                namespaces={"g": NS_G})[0]
        sealedto.attrib['hlink'] = '_f0000'
        input_doc = ET.tostring(input_ctxt)
        self.do_case('I0000', 'I0002', input_doc, expect)

    def test_ldsord_self(self):
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        parentin = input_ctxt.xpath("//g:person[@handle='_i0001']/g:parentin",
                                    namespaces={"g": NS_G})[0]
        parentin.getparent().remove(parentin)
        mother = input_ctxt.xpath("//g:family[@handle='_f0000']/g:mother",
                                  namespaces={"g": NS_G})[0]
        mother.getparent().remove(mother)
        persons = input_ctxt.xpath("//g:person",
                                   namespaces={"g": NS_G})
        parentin = ET.SubElement(persons[2], NSP + 'parentin', hlink='_f0001')
        family = input_ctxt.xpath("//g:family[@handle='_f0001']",
                                  namespaces={"g": NS_G})[0]
        ET.SubElement(family, NSP + 'father', hlink='_i0002')
        ldsord = ET.SubElement(persons[2], NSP + 'lds_ord',
                               type='sealed_to_parents')
        ET.SubElement(ldsord, NSP + 'sealed_to', hlink='_f0001')
        expect = copy.deepcopy(input_ctxt)
        persons = expect.xpath("//g:person",
                               namespaces={"g": NS_G})
        altname = ET.SubElement(persons[0], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 2'
        ldsord = expect.xpath("//g:lds_ord",
                              namespaces={"g": NS_G})[0]
        altname.addnext(ldsord)  # restore order of elements
        attr = ET.SubElement(persons[0], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0002')
        parentref = expect.xpath("//g:person[@handle='_i0000']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        persons[2].getparent().remove(persons[2])
        families = expect.xpath("//g:family",
                                namespaces={"g": NS_G})
        families[1].getparent().remove(families[1])
        sealedto = expect.xpath("//g:sealed_to",
                                namespaces={"g": NS_G})[0]
        sealedto.attrib['hlink'] = '_f0000'
        input_doc = ET.tostring(input_ctxt)
        self.do_case('I0000', 'I0002', input_doc, expect)


#-------------------------------------------------------------------------
#
# FamilyMergeCheck class
#
#-------------------------------------------------------------------------
class FamilyMergeCheck(BaseMergeCheck):
    def setUp(self):
        self.base_setup()
        base_str = """
        <people>
          <person handle="_i0000" id="I0000">
            <gender>M</gender>
            <name type="Birth Name">
              <surname>Person 0</surname>
            </name>
            <parentin hlink="_f0000"/>
          </person>
          <person handle="_i0001" id="I0001">
            <gender>F</gender>
            <name type="Birth Name">
              <surname>Person 1</surname>
            </name>
            <parentin hlink="_f0000"/>
          </person>
          <person handle="_i0002" id="I0002">
            <gender>M</gender>
            <name type="Birth Name">
              <surname>Person 2</surname>
            </name>
            <parentin hlink="_f0001"/>
          </person>
          <person handle="_i0003" id="I0003">
            <gender>F</gender>
            <name type="Birth Name">
              <surname>Person 3</surname>
            </name>
            <parentin hlink="_f0001"/>
          </person>
        </people>
        <families>
          <family handle="_f0000" id="F0000">
            <rel type="Unknown"/>
            <father hlink="_i0000"/>
            <mother hlink="_i0001"/>
          </family>
          <family handle="_f0001" id="F0001">
            <rel type="Unknown"/>
            <father hlink="_i0002"/>
            <mother hlink="_i0003"/>
          </family>
        </families>
        </database>"""
        self.basedoc = bytes(bytearray(self.base_str + base_str,
                                       encoding='utf-8'))

    def test_father_son_merge(self):
        """Merge two families where the fathers have a father-son relationship
        so that an error is raised."""
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        person = input_ctxt.xpath("//g:person[@handle='_i0002']",
                                  namespaces={"g": NS_G})[0]
        ET.SubElement(person, NSP + 'childof', hlink='_f0000')
        family = input_ctxt.xpath("//g:family[@handle='_f0000']",
                                  namespaces={"g": NS_G})[0]
        ET.SubElement(family, NSP + 'childref', hlink='_i0002')
        input_doc = expect = ET.tostring(input_ctxt)
        self.do_family_case(
            'F0000', 'F0001', 'i0000', 'i0001', input_doc, expect,
            test_error_str=_("A parent and child cannot be merged. To merge "
                             "these people, you must first break the "
                             "relationship between them."))

    def test_child_parent_merge_no_father(self):
        """Merge two families where the phoenix family has no father and
        the father of the titanic family is a child of the phoenix family.
        """
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        parentin = input_ctxt.xpath("//g:person[@handle='_i0002']/g:parentin",
                                    namespaces={"g": NS_G})[0]
        parentin.getparent().remove(parentin)
        father = input_ctxt.xpath("//g:family[@handle='_f0001']/g:father",
                                  namespaces={"g": NS_G})[0]
        father.getparent().remove(father)
        person = input_ctxt.xpath("//g:person[@handle='_i0000']",
                                  namespaces={"g": NS_G})[0]
        ET.SubElement(person, NSP + 'childof', hlink='_f0001')
        family = input_ctxt.xpath("//g:family[@handle='_f0001']",
                                  namespaces={"g": NS_G})[0]
        ET.SubElement(family, NSP + 'childref', hlink='_i0000')
        input_doc = expect = ET.tostring(input_ctxt)
        self.do_family_case(
            'F0000', 'F0001', 'i0000', 'i0001', input_doc, expect,
            test_error_str=_("A parent and child cannot be merged. To merge "
                             "these people, you must first break the "
                             "relationship between them."))

    def test_child_parent_merge_no_father_swapped(self):
        """Merge two families where the phoenix family has no father and
        the father of the titanic family, which is the phoenix-father, is a
        child of the phoenix family."""
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        parentin = input_ctxt.xpath("//g:person[@handle='_i0000']/g:parentin",
                                    namespaces={"g": NS_G})[0]
        parentin.getparent().remove(parentin)
        father = input_ctxt.xpath("//g:family[@handle='_f0000']/g:father",
                                  namespaces={"g": NS_G})[0]
        father.getparent().remove(father)
        person = input_ctxt.xpath("//g:person[@handle='_i0002']",
                                  namespaces={"g": NS_G})[0]
        ET.SubElement(person, NSP + 'childof', hlink='_f0000')
        family = input_ctxt.xpath("//g:family[@handle='_f0000']",
                                  namespaces={"g": NS_G})[0]
        ET.SubElement(family, NSP + 'childref', hlink='_i0002')
        input_doc = expect = ET.tostring(input_ctxt)
        self.do_family_case(
            'F0000', 'F0001', 'i0002', 'i0001', input_doc, expect,
            test_error_str=_("A parent and child cannot be merged. To merge "
                             "these people, you must first break the "
                             "relationship between them."))

    def test_regular_merge(self):
        """Merge two families succesfully"""
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        persons = expect.xpath("//g:person",
                               namespaces={"g": NS_G})
        altname = ET.SubElement(persons[0], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 2'
        attr = ET.SubElement(persons[0], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0002')
        parentref = expect.xpath("//g:person[@handle='_i0000']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)   # restore order of elements
        persons[2].getparent().remove(persons[2])
        altname = ET.SubElement(persons[1], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 3'
        attr = ET.SubElement(persons[1], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0003')
        parentref = expect.xpath("//g:person[@handle='_i0001']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        persons[3].getparent().remove(persons[3])
        family = expect.xpath("//g:family[@handle='_f0001']",
                              namespaces={"g": NS_G})[0]
        family.getparent().remove(family)
        self.do_family_case('F0000', 'F0001', 'i0000', 'i0001',
                            self.basedoc, expect)

    def test_father_swapped(self):
        "Merge two families where the phoenix-father is of the titanic family."
        expect = ET.fromstring(self.basedoc, parser=self.parser)
        persons = expect.xpath("//g:person",
                               namespaces={"g": NS_G})
        altname = ET.SubElement(persons[2], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 0'
        attr = ET.SubElement(persons[2], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0000')
        parentref = expect.xpath("//g:person[@handle='_i0002']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        parentref.attrib['hlink'] = '_f0000'
        attr.addnext(parentref)  # restore order of elements
        persons[0].getparent().remove(persons[0])
        altname = ET.SubElement(persons[1], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 3'
        attr = ET.SubElement(persons[1], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0003')
        parentref = expect.xpath("//g:person[@handle='_i0001']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        persons[3].getparent().remove(persons[3])
        family = expect.xpath("//g:family[@handle='_f0001']",
                              namespaces={"g": NS_G})[0]
        family.getparent().remove(family)
        father = expect.xpath("//g:family[@handle='_f0000']/g:father",
                              namespaces={"g": NS_G})[0]
        father.attrib['hlink'] = '_i0002'
        self.do_family_case('F0000', 'F0001', 'i0002', 'i0001',
                            self.basedoc, expect)

    #def test_mother_swapped(self):

    def test_no_father(self):
        """Merge two families, where one family has not father"""
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        parentin = input_ctxt.xpath("//g:person[@handle='_i0002']/g:parentin",
                                    namespaces={"g": NS_G})[0]
        parentin.getparent().remove(parentin)
        father = input_ctxt.xpath("//g:family[@handle='_f0001']/g:father",
                                  namespaces={"g": NS_G})[0]
        father.getparent().remove(father)
        expect = copy.deepcopy(input_ctxt)
        persons = expect.xpath("//g:person",
                               namespaces={"g": NS_G})
        altname = ET.SubElement(persons[1], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 3'
        attr = ET.SubElement(persons[1], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0003')
        parentref = expect.xpath("//g:person[@handle='_i0001']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        persons[3].getparent().remove(persons[3])
        family = expect.xpath("//g:family[@handle='_f0001']",
                              namespaces={"g": NS_G})[0]
        family.getparent().remove(family)
        input_doc = ET.tostring(input_ctxt)
        self.do_family_case('F0000', 'F0001', 'i0000', 'i0001',
                            input_doc, expect)

    def test_no_mother_swapped(self):
        """Merge two families where one family has no mother and the
        phoenix-mother is from the titanic family."""
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        parentin = input_ctxt.xpath("//g:person[@handle='_i0001']/g:parentin",
                                    namespaces={"g": NS_G})[0]
        parentin.getparent().remove(parentin)
        mother = input_ctxt.xpath("//g:family[@handle='_f0000']/g:mother",
                                  namespaces={"g": NS_G})[0]
        mother.getparent().remove(mother)
        expect = copy.deepcopy(input_ctxt)
        persons = expect.xpath("//g:person",
                               namespaces={"g": NS_G})
        altname = ET.SubElement(persons[0], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 2'
        attr = ET.SubElement(persons[0], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0002')
        parentref = expect.xpath("//g:person[@handle='_i0000']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        persons[2].getparent().remove(persons[2])
        parentin = expect.xpath("//g:person[@handle='_i0003']/g:parentin",
                                namespaces={"g": NS_G})[0]
        parentin.attrib['hlink'] = '_f0000'
        family = expect.xpath("//g:family[@handle='_f0001']",
                              namespaces={"g": NS_G})[0]
        family.getparent().remove(family)
        family = expect.xpath("//g:family[@handle='_f0000']",
                              namespaces={"g": NS_G})[0]
        mother = ET.SubElement(family, NSP + 'mother', hlink='_i0003')
        input_doc = ET.tostring(input_ctxt)
        self.do_family_case('F0000', 'F0001', 'i0000', 'i0003',
                            input_doc, expect)

    #def test_no_parents(self):

    def test_childref_notyet(self):
        """Merge two families with non-duplicate child references."""
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        people = input_ctxt.xpath("//g:people",
                                  namespaces={"g": NS_G})[0]
        person = ET.SubElement(people, NSP + 'person',
                               handle='_i0004', id='_I0004')
        ET.SubElement(person, NSP + 'gender').text = 'M'
        name = ET.SubElement(person, NSP + 'name', type='Birth Name')
        ET.SubElement(name, NSP + 'surname').text = 'Person 4'
        ET.SubElement(person, NSP + 'childof', hlink='_f0001')
        family = input_ctxt.xpath("//g:family[@handle='_f0001']",
                                  namespaces={"g": NS_G})[0]
        ET.SubElement(family, NSP + 'childref', hlink='_i0004')
        expect = copy.deepcopy(input_ctxt)
        persons = expect.xpath("//g:person",
                               namespaces={"g": NS_G})
        altname = ET.SubElement(persons[0], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 2'
        attr = ET.SubElement(persons[0], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0002')
        parentref = expect.xpath("//g:person[@handle='_i0000']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        persons[2].getparent().remove(persons[2])
        altname = ET.SubElement(persons[1], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 3'
        attr = ET.SubElement(persons[1], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0003')
        parentref = expect.xpath("//g:person[@handle='_i0001']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        persons[3].getparent().remove(persons[3])
        family = expect.xpath("//g:family[@handle='_f0001']",
                              namespaces={"g": NS_G})[0]
        family.getparent().remove(family)
        childof = expect.xpath("//g:person[@handle='_i0004']/g:childof",
                               namespaces={"g": NS_G})[0]
        childof.attrib['hlink'] = '_f0000'
        family = expect.xpath("//g:family[@handle='_f0000']",
                              namespaces={"g": NS_G})[0]
        ET.SubElement(family, NSP + 'childref', hlink='_i0004')
        input_doc = ET.tostring(input_ctxt)
        self.do_family_case('F0000', 'F0001', 'i0000', 'i0001',
                            input_doc, expect)

    def test_childref_already(self):
        """Merge two families with duplicate child references."""
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        people = input_ctxt.xpath("//g:people",
                                  namespaces={"g": NS_G})[0]
        person = ET.SubElement(people, NSP + 'person',
                               handle='_i0004', id='_I0004')
        ET.SubElement(person, NSP + 'gender').text = 'M'
        name = ET.SubElement(person, NSP + 'name', type='Birth Name')
        ET.SubElement(name, NSP + 'surname').text = 'Person 4'
        ET.SubElement(person, NSP + 'childof', hlink='_f0000')
        ET.SubElement(person, NSP + 'childof', hlink='_f0001')
        family = input_ctxt.xpath("//g:family[@handle='_f0000']",
                                  namespaces={"g": NS_G})[0]
        ET.SubElement(family, NSP + 'childref', hlink='_i0004')
        family = input_ctxt.xpath("//g:family[@handle='_f0001']",
                                  namespaces={"g": NS_G})[0]
        ET.SubElement(family, NSP + 'childref', hlink='_i0004')
        expect = copy.deepcopy(input_ctxt)
        persons = expect.xpath("//g:person",
                               namespaces={"g": NS_G})
        altname = ET.SubElement(persons[0], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 2'
        attr = ET.SubElement(persons[0], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0002')
        parentref = expect.xpath("//g:person[@handle='_i0000']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        persons[2].getparent().remove(persons[2])
        altname = ET.SubElement(persons[1], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 3'
        attr = ET.SubElement(persons[1], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0003')
        parentref = expect.xpath("//g:person[@handle='_i0001']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        persons[3].getparent().remove(persons[3])
        family = expect.xpath("//g:family[@handle='_f0001']",
                              namespaces={"g": NS_G})[0]
        family.getparent().remove(family)
        childof = expect.xpath("//g:person[@handle='_i0004']/g:childof",
                               namespaces={"g": NS_G})[1]
        childof.getparent().remove(childof)
        input_doc = ET.tostring(input_ctxt)
        self.do_family_case('F0000', 'F0001', 'i0000', 'i0001',
                            input_doc, expect)

    # this test fails because the families get IDs F0001 and F0002!
    def test_ldsord(self):
        """Merge two families where one person has a reference to the
        titanic family."""
        input_ctxt = ET.fromstring(self.basedoc, parser=self.parser)
        person = input_ctxt.xpath("//g:person[@handle='_i0000']",
                                  namespaces={"g": NS_G})[0]
        ldsord = ET.SubElement(person, NSP + 'lds_ord',
                               type='sealed_to_parents')
        ET.SubElement(ldsord, NSP + 'sealed_to', hlink='_f0001')
        parentin = input_ctxt.xpath("//g:person[@handle='_i0000']/g:parentin",
                                    namespaces={"g": NS_G})[0]
        ldsord.addnext(parentin)
        expect = copy.deepcopy(input_ctxt)
        persons = expect.xpath("//g:person",
                               namespaces={"g": NS_G})
        altname = ET.SubElement(persons[0], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 2'
        ldsord = expect.xpath("//g:lds_ord",
                              namespaces={"g": NS_G})[0]
        altname.addnext(ldsord)  # restore order of elements
        attr = ET.SubElement(persons[0], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0002')
        parentref = expect.xpath("//g:person[@handle='_i0000']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        persons[2].getparent().remove(persons[2])
        altname = ET.SubElement(persons[1], NSP + 'name',
                                alt='1', type='Birth Name')
        ET.SubElement(altname, NSP + 'surname').text = 'Person 3'
        attr = ET.SubElement(persons[1], NSP + 'attribute',
                             type='Merged Gramps ID', value='I0003')
        parentref = expect.xpath("//g:person[@handle='_i0001']/g:parentin",
                                 namespaces={"g": NS_G})[0]
        attr.addnext(parentref)  # restore order of elements
        persons[3].getparent().remove(persons[3])
        family = expect.xpath("//g:family[@handle='_f0001']",
                              namespaces={"g": NS_G})[0]
        family.getparent().remove(family)
        sealedto = expect.xpath("//g:sealed_to",
                                namespaces={"g": NS_G})[0]
        sealedto.attrib['hlink'] = '_f0000'
        input_doc = ET.tostring(input_ctxt)
        self.do_family_case('F0000', 'F0001', 'i0000', 'i0001',
                            input_doc, expect)


if __name__ == "__main__":
    import sys
    if not HAS_CLIMERGE:
        print('This program needs the third party "CliMerge" plugin.',
              file=sys.stderr)
        sys.exit(1)
    if not HAS_EXPORTRAW:
        print('This program needs the third party "ExportRaw" plugin.',
              file=sys.stderr)
        sys.exit(1)
    unittest.main()
