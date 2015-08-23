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
import subprocess
import libxml2
import libxslt

from gramps.plugins.lib.libgrampsxml import GRAMPS_XML_VERSION
from ...const import ROOT_DIR, USER_PLUGINS
from gramps.version import VERSION
from ...lib import Name, Surname
from ...const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

HAS_CLIMERGE = os.path.isdir(os.path.join(USER_PLUGINS, 'CliMerge'))
HAS_EXPORTRAW = os.path.isdir(os.path.join(USER_PLUGINS, 'ExportRaw'))

class CopiedDoc(object):
    """Context manager that creates a deep copy of an libxml-xml document."""
    def __init__(self, xmldoc):
        self.xmldoc = xmldoc
        self.copy = libxml2.readDoc(str(self.xmldoc), '', None,
                                    libxml2.XML_PARSE_NONET)

    def __enter__(self):
        return self.copy

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.copy.freeDoc()
        return False

class XpathContext(object):
    """Context manager that creates a libxml2 xpath context that allows
       evaluation of xpath expressions."""
    def __init__(self, xmldoc):
        self.xmldoc = xmldoc
        self.ctxt = self.xmldoc.xpathNewContext()
        self.ctxt.xpathRegisterNs('g', 'http://gramps-project.org/xml/%s/' %
                                  GRAMPS_XML_VERSION)

    def __enter__(self):
        return self.ctxt

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ctxt.xpathFreeContext()
        return False

@unittest.skipUnless(HAS_CLIMERGE and HAS_EXPORTRAW,
        'These tests need the 3rd-party plugins "CliMerge" and "ExportRaw".')
class BaseMergeCheck(unittest.TestCase):
    def base_setup(self):
        """Set up code needed by all tests."""
        date = time.localtime(time.time())
        libxml2.keepBlanksDefault(0)
        styledoc = libxml2.parseFile(os.path.join(ROOT_DIR,
            "../data/gramps_canonicalize.xsl"))
        self.style = libxslt.parseStylesheetDoc(styledoc)
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

    def tearDown(self):
        self.basedoc.freeDoc()

    def canonicalize(self, doctxt):
        """
        Return a canonicalized string representation

        :param doctxt: the text to bring in canonical form.
        :type doctxt: either a string or an Xml document.
        :returns: The text but in canonical form.
        :rtype: string
        """
        result = ''
        if isinstance(doctxt, basestring):
            doc = libxml2.readDoc(doctxt, '', None, libxml2.XML_PARSE_NONET)
        elif isinstance(doctxt, libxml2.xmlDoc):
            doc = doctxt
        else:
            raise TypeError
        param = {}
        canonical_doc = self.style.applyStylesheet(doc, param)
        result = self.style.saveResultToString(canonical_doc)
        canonical_doc.freeDoc()
        if isinstance(doctxt, basestring):
            doc.freeDoc()
        return result

    def do_case(self, phoenix_id, titanic_id, input_doc, expect_doc,
                test_error_str='', debug=False):
        """Do the merge and "assert" the result."""
        process = subprocess.Popen('python Gramps.py -d .ImportXML '
                                   '--config=preferences.eprefix:DEFAULT '
                                   '-i - -f gramps -a tool '
                                   '-p "name=climerge,primary=%s,secondary=%s" '
                                   '-e - -f gramps' % (phoenix_id, titanic_id),
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, shell=True)
        result_str, err_str = process.communicate(str(input_doc))
        if err_str:
            if test_error_str:
                self.assertIn(test_error_str, err_str)
                return
            else:
                if "Traceback (most recent call last):" in err_str:
                    raise Exception(err_str)
        if debug:
            print('input :', self.canonicalize(input_doc))
            print('result:', self.canonicalize(result_str))
            print('expect:', self.canonicalize(expect_doc))
        self.assertEqual(self.canonicalize(result_str),
                         self.canonicalize(expect_doc))

    def do_family_case(self, phoenix_id, titanic_id, father_h, mother_h,
                       input_doc, expect_doc, test_error_str='', debug=False):
        process = subprocess.Popen('python Gramps.py -d .ImportXML '
                                   '--config=preferences.eprefix:DEFAULT '
                                   '-i - -f gramps -a tool '
                                   '-p "name=climerge,primary=%s,secondary=%s,father_h=%s,mother_h=%s" '
                                   '-e - -f gramps' % (phoenix_id, titanic_id, father_h, mother_h),
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, shell=True)
        result_str, err_str = process.communicate(str(input_doc))
        if err_str:
            if test_error_str:
                self.assertIn(test_error_str, err_str)
                return
        if debug:
            print('input :', self.canonicalize(input_doc))
            print('result:', self.canonicalize(result_str))
            print('expect:', self.canonicalize(expect_doc))
        self.assertEqual(self.canonicalize(result_str),
                         self.canonicalize(expect_doc))

    def raw_contains(self, phoenix_id, titanic_id, input_doc, expect_str,
                test_error_str='', debug=False):
        process = subprocess.Popen('python Gramps.py -d .ImportXML '
                                   '--config=preferences.eprefix:DEFAULT '
                                   '-i - -f gramps -a tool '
                                   '-p "name=climerge,primary=%s,secondary=%s" '
                                   '-e - -f raw' % (phoenix_id, titanic_id),
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, shell=True)
        result_str, err_str = process.communicate(str(input_doc))
        if err_str:
            if test_error_str:
                self.assertIn(test_error_str, err_str)
                return
        if debug:
            print('input :', self.canonicalize(input_doc))
            print('result:', result_str)
            print('expect:', expect_str)
        # should I order/canonicalise things?
        self.assertIn(expect_str, result_str)
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
          <placeobj handle="_p0000" id="P0000" name="Place 0" type="Country">
            <ptitle>Place 0</ptitle>
          </placeobj>
          <placeobj handle="_p0001" id="P0001" name="Place 1" type="Country">
            <ptitle>Place 1</ptitle>
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
        self.basedoc = libxml2.readDoc(self.base_str + base_str, '', None,
                                       libxml2.XML_PARSE_NONET)

    def test_event_merge(self):
        """Merge two events"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                eventref = ctxt.xpathEval(
                        "//g:person[@handle='_i0001']/g:eventref")[0]
                eventref.setProp('hlink', '_e0000')
                event = ctxt.xpathEval("//g:event[@handle='_e0001']")[0]
                event.unlinkNode()
                event.freeNode()
                self.do_case('E0000', 'E0001', self.basedoc, expect)

    def test_place_merge(self):
        """Merge two places"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                place = ctxt.xpathEval(
                        "//g:person[@handle='_i0001']/g:lds_ord/g:place")[0]
                place.setProp('hlink', '_p0000')
                placeobj = ctxt.xpathEval("//g:placeobj[@handle='_p0001']")[0]
                placeobj.unlinkNode()
                placeobj.freeNode()
                placeobj = ctxt.xpathEval("//g:placeobj[@handle='_p0000']")[0]
                placeobj.newChild(None, 'alt_name', 'Place 1')
                self.do_case('P0000', 'P0001', self.basedoc, expect)

    def test_citation_merge(self):
        """Merge two citations"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                srcref = ctxt.xpathEval(
                        "//g:person[@handle='_i0001']/g:citationref")[0]
                srcref.setProp('hlink', '_c0000')
                citation = ctxt.xpathEval("//g:citation[@handle='_c0001']")[0]
                citation.unlinkNode()
                citation.freeNode()
                self.do_case('C0000', 'C0001', self.basedoc, expect)

    def test_media_merge(self):
        """Merge two media objects"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                objref = ctxt.xpathEval(
                        "//g:person[@handle='_i0001']/g:objref")[0]
                objref.setProp('hlink', '_o0000')
                object_ = ctxt.xpathEval("//g:object[@handle='_o0001']")[0]
                object_.unlinkNode()
                object_.freeNode()
                self.do_case('O0000', 'O0001', self.basedoc, expect)

    def test_note_merge(self):
        """Merge two notes"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                noteref = ctxt.xpathEval(
                        "//g:person[@handle='_i0001']/g:noteref")[0]
                noteref.setProp('hlink', '_n0000')
                note = ctxt.xpathEval("//g:note[@handle='_n0001']")[0]
                note.unlinkNode()
                note.freeNode()
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
          <placeobj handle="_p0000" id="P0000" name="Place 0" type="Country">
            <ptitle>Place 0</ptitle>
          </placeobj>
          <placeobj handle="_p0001" id="P0001" name="Place 1" type="Country">
            <ptitle>Place 1</ptitle>
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
        self.basedoc = libxml2.readDoc(self.base_str + base_str, '', None,
                                       libxml2.XML_PARSE_NONET)

    def test_event_merge(self):
        """Merge two events"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                eventref = ctxt.xpathEval(
                        "//g:family[@handle='_f0001']/g:eventref")[0]
                eventref.setProp('hlink', '_e0000')
                event = ctxt.xpathEval("//g:event[@handle='_e0001']")[0]
                event.unlinkNode()
                event.freeNode()
                self.do_case('E0000', 'E0001', self.basedoc, expect)

    def test_place_merge(self):
        """Merge two places"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                place = ctxt.xpathEval(
                        "//g:family[@handle='_f0001']/g:lds_ord/g:place")[0]
                place.setProp('hlink', '_p0000')
                placeobj = ctxt.xpathEval("//g:placeobj[@handle='_p0001']")[0]
                placeobj.unlinkNode()
                placeobj.freeNode()
                placeobj = ctxt.xpathEval("//g:placeobj[@handle='_p0000']")[0]
                placeobj.newChild(None, 'alt_name', 'Place 1')
                self.do_case('P0000', 'P0001', self.basedoc, expect)

    def test_citation_merge(self):
        """Merge two citations"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                citref = ctxt.xpathEval(
                        "//g:family[@handle='_f0001']/g:citationref")[0]
                citref.setProp('hlink', '_c0000')
                citation = ctxt.xpathEval("//g:citation[@handle='_c0001']")[0]
                citation.unlinkNode()
                citation.freeNode()
                self.do_case('C0000', 'C0001', self.basedoc, expect)

    def test_media_merge(self):
        """Merge two media objects"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                objref = ctxt.xpathEval(
                        "//g:family[@handle='_f0001']/g:objref")[0]
                objref.setProp('hlink', '_o0000')
                object_ = ctxt.xpathEval("//g:object[@handle='_o0001']")[0]
                object_.unlinkNode()
                object_.freeNode()
                self.do_case('O0000', 'O0001', self.basedoc, expect)

    def test_note_merge(self):
        """Merge two notes"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                noteref = ctxt.xpathEval(
                        "//g:family[@handle='_f0001']/g:noteref")[0]
                noteref.setProp('hlink', '_n0000')
                note = ctxt.xpathEval("//g:note[@handle='_n0001']")[0]
                note.unlinkNode()
                note.freeNode()
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
          <placeobj handle="_p0000" id="P0000" name="Place 0" type = "Country">
            <ptitle>Place 0</ptitle>
          </placeobj>
          <placeobj handle="_p0001" id="P0001" name="Place 1" type = "Country">
            <ptitle>Place 1</ptitle>
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
        self.basedoc = libxml2.readDoc(self.base_str + base_str, '', None,
                                       libxml2.XML_PARSE_NONET)

    def test_place_merge(self):
        """Merge two places"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                place = ctxt.xpathEval(
                        "//g:event[@handle='_e0001']/g:place")[0]
                place.setProp('hlink', '_p0000')
                placeobj = ctxt.xpathEval("//g:placeobj[@handle='_p0001']")[0]
                placeobj.unlinkNode()
                placeobj.freeNode()
                placeobj = ctxt.xpathEval("//g:placeobj[@handle='_p0000']")[0]
                placeobj.newChild(None, 'alt_name', 'Place 1')
                self.do_case('P0000', 'P0001', self.basedoc, expect)

    def test_citation_merge(self):
        """Merge two citations"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                citref = ctxt.xpathEval(
                        "//g:event[@handle='_e0001']/g:citationref")[0]
                citref.setProp('hlink', '_c0000')
                citation = ctxt.xpathEval("//g:citation[@handle='_c0001']")[0]
                citation.unlinkNode()
                citation.freeNode()
                self.do_case('C0000', 'C0001', self.basedoc, expect)

    def test_media_merge(self):
        """Merge two media objects"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                objref = ctxt.xpathEval(
                        "//g:event[@handle='_e0001']/g:objref")[0]
                objref.setProp('hlink', '_o0000')
                object_ = ctxt.xpathEval("//g:object[@handle='_o0001']")[0]
                object_.unlinkNode()
                object_.freeNode()
                self.do_case('O0000', 'O0001', self.basedoc, expect)

    def test_note_merge(self):
        """Merge two notes"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                noteref = ctxt.xpathEval(
                        "//g:event[@handle='_e0001']/g:noteref")[0]
                noteref.setProp('hlink', '_n0000')
                note = ctxt.xpathEval("//g:note[@handle='_n0001']")[0]
                note.unlinkNode()
                note.freeNode()
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
          <placeobj handle="_p0000" id="P0000" name="Place 0" type = "Country">
            <ptitle>Place 0</ptitle>
            <objref hlink="_o0000"/>
            <noteref hlink="_n0000"/>
            <citationref hlink="_c0000"/>
          </placeobj>
          <placeobj handle="_p0001" id="P0001" name="Place 1" type = "Country">
            <ptitle>Place 1</ptitle>
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
        self.basedoc = libxml2.readDoc(self.base_str + base_str, '', None,
                                       libxml2.XML_PARSE_NONET)

    def test_citation_merge(self):
        """Merge two citations"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                citref = ctxt.xpathEval(
                        "//g:placeobj[@handle='_p0001']/g:citationref")[0]
                citref.setProp('hlink', '_c0000')
                citation = ctxt.xpathEval("//g:citation[@handle='_c0001']")[0]
                citation.unlinkNode()
                citation.freeNode()
                self.do_case('C0000', 'C0001', self.basedoc, expect)

    def test_media_merge(self):
        """Merge two media objects"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                objref = ctxt.xpathEval(
                        "//g:placeobj[@handle='_p0001']/g:objref")[0]
                objref.setProp('hlink', '_o0000')
                object_ = ctxt.xpathEval("//g:object[@handle='_o0001']")[0]
                object_.unlinkNode()
                object_.freeNode()
                self.do_case('O0000', 'O0001', self.basedoc, expect)

    def test_note_merge(self):
        """Merge two notes"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                noteref = ctxt.xpathEval(
                        "//g:placeobj[@handle='_p0001']/g:noteref")[0]
                noteref.setProp('hlink', '_n0000')
                note = ctxt.xpathEval("//g:note[@handle='_n0001']")[0]
                note.unlinkNode()
                note.freeNode()
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
        self.basedoc = libxml2.readDoc(self.base_str + base_str, '', None,
                                       libxml2.XML_PARSE_NONET)

    #def test_citation_merge(self): SEE special cases.

    def test_repo_merge(self):
        """Merge two repositories"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                # Adjust the repository reference in expectation.
                reporef = ctxt.xpathEval(
                        "//g:source[@handle='_s0001']/g:reporef")[0]
                reporef.setProp('hlink', '_r0000')
                # Remove one repository in expectation.
                repo = ctxt.xpathEval("//g:repository[@handle='_r0001']")[0]
                repo.unlinkNode()
                repo.freeNode()
                # Do the actual merger and comparison.
                self.do_case('R0000', 'R0001', self.basedoc, expect)

    def test_media_merge(self):
        """Merge two media objects"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                objref = ctxt.xpathEval(
                        "//g:source[@handle='_s0001']/g:objref")[0]
                objref.setProp('hlink', '_o0000')
                object_ = ctxt.xpathEval("//g:object[@handle='_o0001']")[0]
                object_.unlinkNode()
                object_.freeNode()
                self.do_case('O0000', 'O0001', self.basedoc, expect)

    def test_note_merge(self):
        """Merge two notes"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                noteref = ctxt.xpathEval(
                        "//g:source[@handle='_s0001']/g:noteref")[0]
                noteref.setProp('hlink', '_n0000')
                note = ctxt.xpathEval("//g:note[@handle='_n0001']")[0]
                note.unlinkNode()
                note.freeNode()
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
        self.basedoc = libxml2.readDoc(self.base_str + base_str, '', None,
                                       libxml2.XML_PARSE_NONET)

    def test_citation_merge(self):
        """Merge two citations"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                citref = ctxt.xpathEval(
                    "//g:repository[@handle='_r0001']/g:address/g:citationref")[0]
                citref.setProp('hlink', '_c0000')
                citation = ctxt.xpathEval("//g:citation[@handle='_c0001']")[0]
                citation.unlinkNode()
                citation.freeNode()
                self.do_case('C0000', 'C0001', self.basedoc, expect)

    def test_note_merge(self):
        """Merge two notes"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                noteref = ctxt.xpathEval(
                        "//g:repository[@handle='_r0001']/g:noteref")[0]
                noteref.setProp('hlink', '_n0000')
                note = ctxt.xpathEval("//g:note[@handle='_n0001']")[0]
                note.unlinkNode()
                note.freeNode()
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
        self.basedoc = libxml2.readDoc(self.base_str + base_str, '', None,
                                       libxml2.XML_PARSE_NONET)

    def test_citation_merge(self):
        """Merge two citations"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                citref = ctxt.xpathEval(
                        "//g:object[@handle='_o0001']/g:citationref")[0]
                citref.setProp('hlink', '_c0000')
                citation = ctxt.xpathEval("//g:citation[@handle='_c0001']")[0]
                citation.unlinkNode()
                citation.freeNode()
                self.do_case('C0000', 'C0001', self.basedoc, expect)

    def test_note_merge(self):
        """Merge two notes"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                noteref = ctxt.xpathEval(
                        "//g:object[@handle='_o0001']/g:noteref")[0]
                noteref.setProp('hlink', '_n0000')
                note = ctxt.xpathEval("//g:note[@handle='_n0001']")[0]
                note.unlinkNode()
                note.freeNode()
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
        self.basedoc = libxml2.readDoc(self.base_str + base_str, '', None,
                                       libxml2.XML_PARSE_NONET)

    def test_citation_merge(self):
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                citrefs = ctxt.xpathEval(
                        "//g:citation[@handle='_c0001']/g:objref/g:citationref")
                citrefs[0].setProp('hlink', '_c0002')
                citations = ctxt.xpathEval("//g:citation[@handle='_c0003']")
                citations[0].unlinkNode()
                citations[0].freeNode()
                self.do_case('C0002', 'C0003', self.basedoc, expect)

    def test_citation_cross_merge(self):
        with XpathContext(self.basedoc) as input_ctxt:
            input_citrefs = input_ctxt.xpathEval(
                    "//g:citation/g:objref/g:citationref")
            input_citrefs[0].setProp('hlink', '_c0001')
            input_citrefs[1].setProp('hlink', '_c0000')
            rmcit = input_ctxt.xpathEval("//g:citation[@handle='_c0002']")
            rmcit[0].unlinkNode()
            rmcit[0].freeNode()
            rmcit = input_ctxt.xpathEval("//g:citation[@handle='_c0003']")
            rmcit[0].unlinkNode()
            rmcit[0].freeNode()
            rmsrc = input_ctxt.xpathEval("//g:source[@handle='_s0001']")
            rmsrc[0].unlinkNode()
            rmsrc[0].freeNode()
            with CopiedDoc(self.basedoc) as expect:
                with XpathContext(expect) as ctxt:
                    citrefs = ctxt.xpathEval(
                        "//g:citation[@handle='_c0000']/g:objref/g:citationref")
                    citrefs[0].setProp('hlink', '_c0000')
                    # add objref
                    objref = ctxt.xpathEval("//g:citation[@handle='_c0000']/g:objref")
                    objref2 = ctxt.xpathEval("//g:citation[@handle='_c0001']/g:objref")
                    objref[0].addNextSibling(objref2[0])
                    # remove citation
                    citations = ctxt.xpathEval("//g:citation[@handle='_c0001']")
                    citations[0].unlinkNode()
                    citations[0].freeNode()
                    self.do_case('C0000', 'C0001', self.basedoc, expect)

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
        self.basedoc = libxml2.readDoc(self.base_str + base_str, '', None,
                                       libxml2.XML_PARSE_NONET)
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
        expect_str = self.expect_str + "1, -1"
        self.raw_contains('E0000', 'E0001', self.basedoc, expect_str)

    def test_second_birth(self):
        # check that birth _ref_index is 2
        with XpathContext(self.basedoc) as ctxt:
            events = ctxt.xpathEval("//g:events")
            second_birth = events[0].newChild(None, 'event', None)
            second_birth.newProp('handle', '_e0003')
            second_birth.newProp('id', 'E0003')
            second_birth.newChild(None, 'type', 'Birth')
            second_birth.newChild(None, 'description', 'Event 3')
            person = ctxt.xpathEval("//g:person[@handle='_i0000']")
            eventref = person[0].newChild(None, 'eventref', None)
            eventref.newProp('hlink', '_e0003')
            eventref.newProp('role', 'Primary')
            expect_str = self.expect_str + "1, 2"
            self.raw_contains('E0000', 'E0001', self.basedoc, expect_str)

    def test_death_merge(self):
        # check that death_ref_index is -1
        expect_str = self.expect_str + "-1, 1"
        self.raw_contains('E0000', 'E0002', self.basedoc, expect_str)

    def test_second_death(self):
        # check that death _ref_index is 2
        with XpathContext(self.basedoc) as ctxt:
            events = ctxt.xpathEval("//g:events")
            second_death = events[0].newChild(None, 'event', None)
            second_death.newProp('handle', '_e0003')
            second_death.newProp('id', 'E0003')
            second_death.newChild(None, 'type', 'Death')
            second_death.newChild(None, 'description', 'Event 3')
            person = ctxt.xpathEval("//g:person[@handle='_i0000']")
            eventref = person[0].newChild(None, 'eventref', None)
            eventref.newProp('hlink', '_e0003')
            eventref.newProp('role', 'Primary')
            expect_str = self.expect_str + "2, 1"
            self.raw_contains('E0000', 'E0002', self.basedoc, expect_str)

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
        self.basedoc = libxml2.readDoc(self.base_str + base_str, '', None,
                                       libxml2.XML_PARSE_NONET)

    def test_person_merge(self):
        """There is a person not involved in merger that references Titanic."""
        with XpathContext(self.basedoc) as input_ctxt:
            people = input_ctxt.xpathEval("//g:people")[0]
            person = people.newChild(None, 'person', None)
            person.newProp('handle', '_i0002')
            person.newProp('id', 'I0002')
            person.newChild(None, 'gender', 'M')
            name = person.newChild(None, 'name', None)
            name.newProp('type', 'Birth Name')
            name.newChild(None, 'surname', 'Person 2')
            personref = person.newChild(None, 'personref', None)
            personref.newProp('hlink', '_i0001')
            personref.newProp('rel', 'Neighbour')
            with CopiedDoc(self.basedoc) as expect:
                with XpathContext(expect) as ctxt:
                    personref = ctxt.xpathEval("//g:personref")[0]
                    personref.setProp('hlink', '_i0000')
                    person = ctxt.xpathEval("//g:person[@handle='_i0000']")[0]
                    altname = person.newChild(None, 'name', None)
                    altname.newProp('alt', '1')
                    altname.newProp('type', 'Birth Name')
                    altname.newChild(None, 'surname', 'Person 1')
                    attr = person.newChild(None, 'attribute', None)
                    attr.newProp('type', 'Merged Gramps ID')
                    attr.newProp('value', 'I0001')
                    person = ctxt.xpathEval("//g:person[@handle='_i0001']")[0]
                    person.unlinkNode()
                    person.freeNode()
                    self.do_case('I0000', 'I0001', self.basedoc, expect)

    def test_person_cross(self):
        """Phoenix has ref to Titanic and vice versa"""
        with XpathContext(self.basedoc) as input_ctxt:
            persons = input_ctxt.xpathEval("//g:person")
            personref = persons[0].newChild(None, 'personref', None)
            personref.newProp('hlink', '_i0001')
            personref.newProp('rel','Neighbour East')
            personref = persons[1].newChild(None, 'personref', None)
            personref.newProp('hlink', '_i0000')
            personref.newProp('rel','Neighbour West')
            with CopiedDoc(self.basedoc) as expect:
                with XpathContext(expect) as ctxt:

                    personref = ctxt.xpathEval("//g:person[@handle='_i0000']/g:personref")[0]
                    personref.setProp('hlink', '_i0000')
                    person = ctxt.xpathEval("//g:person[@handle='_i0000']")[0]
                    altname = person.newChild(None, 'name', None)
                    altname.newProp('alt', '1')
                    altname.newProp('type', 'Birth Name')
                    altname.newChild(None, 'surname', 'Person 1')
                    attr = person.newChild(None, 'attribute', None)
                    attr.newProp('type', 'Merged Gramps ID')
                    attr.newProp('value', 'I0001')
                    attr.addNextSibling(personref) # restore order of elements
                    personref = person.newChild(None, 'personref', None)
                    personref.newProp('hlink', '_i0000')
                    personref.newProp('rel', 'Neighbour West')
                    person = ctxt.xpathEval("//g:person[@handle='_i0001']")[0]
                    person.unlinkNode()
                    person.freeNode()
                    self.do_case('I0000', 'I0001', self.basedoc, expect)

    def test_person_self(self):
        """Titanic references itself"""
        with XpathContext(self.basedoc) as input_ctxt:
            person = input_ctxt.xpathEval("//g:person[@handle='_i0001']")[0]
            personref = person.newChild(None, 'personref', None)
            personref.newProp('hlink', '_i0001')
            personref.newProp('rel', 'Neighbour')
            with CopiedDoc(self.basedoc) as expect:
                with XpathContext(expect) as ctxt:
                    person = ctxt.xpathEval("//g:person[@handle='_i0000']")[0]
                    altname = person.newChild(None, 'name', None)
                    altname.newProp('alt', '1')
                    altname.newProp('type', 'Birth Name')
                    altname.newChild(None, 'surname', 'Person 1')
                    attr = person.newChild(None, 'attribute', None)
                    attr.newProp('type', 'Merged Gramps ID')
                    attr.newProp('value', 'I0001')
                    personref = person.newChild(None, 'personref', None)
                    personref.newProp('hlink', '_i0000')
                    personref.newProp('rel', 'Neighbour')
                    person = ctxt.xpathEval("//g:person[@handle='_i0001']")[0]
                    person.unlinkNode()
                    person.freeNode()
                    self.do_case('I0000', 'I0001', self.basedoc, expect)

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
        self.basedoc = libxml2.readDoc(self.base_str + base_str, '', None,
                                       libxml2.XML_PARSE_NONET)

    def test_person_merge(self):
        """Merge two persons that are children in some family"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                childref = ctxt.xpathEval("//g:family[@handle='_f0001']/g:childref")[0]
                childref.setProp('hlink', '_i0000')

                persons = ctxt.xpathEval("//g:person")
                altname = persons[0].newChild(None, 'name', None)
                altname.newProp('alt', '1')
                altname.newProp('type', 'Birth Name')
                altname.newChild(None, 'surname', 'Person 1')
                attr = persons[0].newChild(None, 'attribute', None)
                attr.newProp('type', 'Merged Gramps ID')
                attr.newProp('value', 'I0001')
                childof = ctxt.xpathEval("//g:person[@handle='_i0000']/g:childof")[0]
                attr.addNextSibling(childof) # restore order of elements
                childof = persons[0].newChild(None, 'childof', None)
                childof.newProp('hlink', '_f0001')
                persons[1].unlinkNode()
                persons[1].freeNode()
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
        self.basedoc = libxml2.readDoc(self.base_str + base_str, '', None,
                                       libxml2.XML_PARSE_NONET)

    def test_titanic_no_fam(self):
        "Test merge of two persons where titanic is not a parent in a family"
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                persons = ctxt.xpathEval("//g:person")
                altname = persons[0].newChild(None, 'name', None)
                altname.newProp('alt', '1')
                altname.newProp('type', 'Birth Name')
                altname.newChild(None, 'surname', 'Person 2')
                attr = persons[0].newChild(None, 'attribute', None)
                attr.newProp('type', 'Merged Gramps ID')
                attr.newProp('value', 'I0002')
                parentref = ctxt.xpathEval("//g:person[@handle='_i0000']/g:parentin")[0]
                attr.addNextSibling(parentref) # restore order of elements
                persons[2].unlinkNode()
                persons[2].freeNode()
                self.do_case('I0000', 'I0002', self.basedoc, expect)

    def test_no_fam_merge(self):
        """Test merge of two persons, both parents in a family, but such that
        the families will not merge."""
        with XpathContext(self.basedoc) as input_ctxt:
            person = input_ctxt.xpathEval("//g:person[@handle='_i0002']")[0]
            parentin = person.newChild(None, 'parentin', None)
            parentin.newProp('hlink', '_f0001')
            family = input_ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
            father = family.newChild(None, 'father', None)
            father.newProp('hlink', '_i0002')
            with CopiedDoc(self.basedoc) as expect:
                with XpathContext(expect) as ctxt:
                    persons = ctxt.xpathEval("//g:person")
                    altname = persons[0].newChild(None, 'name', None)
                    altname.newProp('alt', '1')
                    altname.newProp('type', 'Birth Name')
                    altname.newChild(None, 'surname', 'Person 2')
                    attr = persons[0].newChild(None, 'attribute', None)
                    attr.newProp('type', 'Merged Gramps ID')
                    attr.newProp('value', 'I0002')
                    parentref = ctxt.xpathEval("//g:person[@handle='_i0000']/g:parentin")[0]
                    attr.addNextSibling(parentref) # restore order of elements
                    parentin = persons[0].newChild(None, 'parentin', None)
                    parentin.newProp('hlink', '_f0001')
                    father = ctxt.xpathEval("//g:family[@handle='_f0001']/g:father")[0]
                    father.setProp('hlink', '_i0000')
                    persons[2].unlinkNode()
                    persons[2].freeNode()
                    self.do_case('I0000', 'I0002', self.basedoc, expect)

    def test_multi_rel(self):
        """Merge two persons where titanic has multiple family relationships
        with his partner, this should raise an error."""
        with XpathContext(self.basedoc) as input_ctxt:
            persons = input_ctxt.xpathEval("//g:person")
            parentin = persons[2].newChild(None, 'parentin', None)
            parentin.newProp('hlink', '_f0001')
            parentin = persons[3].newChild(None, 'parentin', None)
            parentin.newProp('hlink', '_f0001')
            parentin = persons[2].newChild(None, 'parentin', None)
            parentin.newProp('hlink', '_f0002')
            parentin = persons[3].newChild(None, 'parentin', None)
            parentin.newProp('hlink', '_f0002')
            family = input_ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
            father = family.newChild(None, 'father', None)
            father.newProp('hlink', '_i0002')
            mother = family.newChild(None, 'mother', None)
            mother.newProp('hlink', '_i0003')
            families = input_ctxt.xpathEval("//g:families")[0]
            family = families.newChild(None, 'family', None)
            family.newProp('handle', '_f0002')
            family.newProp('id', 'F0002')
            rel = family.newChild(None, 'rel', None)
            rel.newProp('type', 'Married')
            father = family.newChild(None, 'father', None)
            father.newProp('hlink', '_i0002')
            mother = family.newChild(None, 'mother', None)
            mother.newProp('hlink', '_i0003')
            with CopiedDoc(self.basedoc) as expect:
                self.do_case('I0000', 'I0002', self.basedoc, expect,
                        test_error_str=_("A person with multiple relations "
                        "with the same spouse is about to be merged. This is "
                        "beyond the capabilities of the merge routine. The "
                        "merge is aborted."))

    def test_merge_fam(self):
        """Merge two persons such that also the families in which they are
        parents get merged."""
        with XpathContext(self.basedoc) as input_ctxt:
            persons = input_ctxt.xpathEval("//g:person")
            parentin = persons[1].newChild(None, 'parentin', None)
            parentin.newProp('hlink', '_f0001')
            parentin = persons[2].newChild(None, 'parentin', None)
            parentin.newProp('hlink', '_f0001')
            family = input_ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
            father = family.newChild(None, 'father', None)
            father.newProp('hlink', '_i0002')
            mother = family.newChild(None, 'mother', None)
            mother.newProp('hlink', '_i0001')
            with CopiedDoc(self.basedoc) as expect:
                with XpathContext(expect) as ctxt:
                    persons = ctxt.xpathEval("//g:person")
                    altname = persons[0].newChild(None, 'name', None)
                    altname.newProp('alt', '1')
                    altname.newProp('type', 'Birth Name')
                    altname.newChild(None, 'surname', 'Person 2')
                    attr = persons[0].newChild(None, 'attribute', None)
                    attr.newProp('type', 'Merged Gramps ID')
                    attr.newProp('value', 'I0002')
                    parentref = ctxt.xpathEval("//g:person[@handle='_i0000']/g:parentin")[0]
                    attr.addNextSibling(parentref) # restore order of elements
                    persons[2].unlinkNode()
                    persons[2].freeNode()
                    family = ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
                    family.unlinkNode()
                    family.freeNode()
                    parentin = ctxt.xpathEval("//g:person[@handle='_i0001']/g:parentin")[1]
                    parentin.unlinkNode()
                    parentin.freeNode()
                    self.do_case('I0000', 'I0002', self.basedoc, expect)

    def test_fam_none_merge(self):
        """Merge two persons, both father in families without mothers."""
        with XpathContext(self.basedoc) as input_ctxt:
            parentin = input_ctxt.xpathEval("//g:person[@handle='_i0001']/g:parentin")[0]
            parentin.unlinkNode()
            parentin.freeNode()
            mother = input_ctxt.xpathEval("//g:family[@handle='_f0000']/g:mother")[0]
            mother.unlinkNode()
            mother.freeNode()
            family = input_ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
            father = family.newChild(None, 'father', None)
            father.newProp('hlink', '_i0002')
            person = input_ctxt.xpathEval("//g:person[@handle='_i0002']")[0]
            parentin = person.newChild(None, 'parentin', None)
            parentin.newProp('hlink', '_f0001')
            with CopiedDoc(self.basedoc) as expect:
                with XpathContext(expect) as ctxt:
                    persons = ctxt.xpathEval("//g:person")
                    altname = persons[0].newChild(None, 'name', None)
                    altname.newProp('alt', '1')
                    altname.newProp('type', 'Birth Name')
                    altname.newChild(None, 'surname', 'Person 2')
                    attr = persons[0].newChild(None, 'attribute', None)
                    attr.newProp('type', 'Merged Gramps ID')
                    attr.newProp('value', 'I0002')
                    parentref = ctxt.xpathEval("//g:person[@handle='_i0000']/g:parentin")[0]
                    attr.addNextSibling(parentref) # restore order of elements
                    persons[2].unlinkNode()
                    persons[2].freeNode()
                    family = ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
                    family.unlinkNode()
                    family.freeNode()
                    self.do_case('I0000', 'I0002', self.basedoc, expect)

    # Can't think of a testcase that would merge multiple families.

    def test_fam_mother_merge(self):
        """Merge two persons that are mothers in their respective families."""
        with XpathContext(self.basedoc) as input_ctxt:
            persons = input_ctxt.xpathEval("//g:person")
            parentin = persons[0].newChild(None, 'parentin', None)
            parentin.newProp('hlink', '_f0001')
            parentin = persons[3].newChild(None, 'parentin', None)
            parentin.newProp('hlink', '_f0001')
            family = input_ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
            father = family.newChild(None, 'father', None)
            father.newProp('hlink', '_i0000')
            mother = family.newChild(None, 'mother', None)
            mother.newProp('hlink', '_i0003')
            with CopiedDoc(self.basedoc) as expect:
                with XpathContext(expect) as ctxt:
                    persons = ctxt.xpathEval("//g:person")
                    altname = persons[1].newChild(None, 'name', None)
                    altname.newProp('alt', '1')
                    altname.newProp('type', 'Birth Name')
                    altname.newChild(None, 'surname', 'Person 3')
                    attr = persons[1].newChild(None, 'attribute', None)
                    attr.newProp('type', 'Merged Gramps ID')
                    attr.newProp('value', 'I0003')
                    parentref = ctxt.xpathEval("//g:person[@handle='_i0001']/g:parentin")[0]
                    attr.addNextSibling(parentref) # restore order of elements
                    persons[3].unlinkNode()
                    persons[3].freeNode()
                    family = ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
                    family.unlinkNode()
                    family.freeNode()
                    parentin = ctxt.xpathEval("//g:person[@handle='_i0000']/g:parentin")[1]
                    parentin.unlinkNode()
                    parentin.freeNode()
                    self.do_case('I0001', 'I0003', self.basedoc, expect)

    def test_childref_notyet(self):
        """Merge two people leading to merger of families that have children."""
        with XpathContext(self.basedoc) as input_ctxt:
            parentin = input_ctxt.xpathEval("//g:person[@handle='_i0001']/g:parentin")[0]
            parentin.unlinkNode()
            parentin.freeNode()
            mother = input_ctxt.xpathEval("//g:family[@handle='_f0000']/g:mother")[0]
            mother.unlinkNode()
            mother.freeNode()
            persons = input_ctxt.xpathEval("//g:person")
            childof = persons[1].newChild(None, 'childof', None)
            childof.newProp('hlink', '_f0000')
            families = input_ctxt.xpathEval("//g:family")
            childref = families[0].newChild(None, 'childref', None)
            childref.newProp('hlink', '_i0001')
            parentin = persons[2].newChild(None, 'parentin', None)
            parentin.newProp('hlink', '_f0001')
            father = families[1].newChild(None, 'father', None)
            father.newProp('hlink', '_i0002')
            childof = persons[3].newChild(None, 'childof', None)
            childof.newProp('hlink', '_f0001')
            childref = families[1].newChild(None, 'childref', None)
            childref.newProp('hlink', '_i0003')
            with CopiedDoc(self.basedoc) as expect:
                with XpathContext(expect) as ctxt:
                    persons = ctxt.xpathEval("//g:person")
                    altname = persons[0].newChild(None, 'name', None)
                    altname.newProp('alt', '1')
                    altname.newProp('type', 'Birth Name')
                    altname.newChild(None, 'surname', 'Person 2')
                    attr = persons[0].newChild(None, 'attribute', None)
                    attr.newProp('type', 'Merged Gramps ID')
                    attr.newProp('value', 'I0002')
                    parentref = ctxt.xpathEval("//g:person[@handle='_i0000']/g:parentin")[0]
                    attr.addNextSibling(parentref) # restore order of elements
                    persons[2].unlinkNode()
                    persons[2].freeNode()
                    families = ctxt.xpathEval("//g:family")
                    families[1].unlinkNode()
                    families[1].freeNode()
                    childof = ctxt.xpathEval("//g:person[@handle='_i0003']/g:childof")[0]
                    childof.setProp('hlink', '_f0000')
                    childref = families[0].newChild(None, 'childref', None)
                    childref.newProp('hlink', '_i0003')
                    self.do_case('I0000', 'I0002', self.basedoc, expect)

    def test_childref_already(self):
        with XpathContext(self.basedoc) as input_ctxt:
            parentin = input_ctxt.xpathEval("//g:person[@handle='_i0001']/g:parentin")[0]
            parentin.unlinkNode()
            parentin.freeNode()
            mother = input_ctxt.xpathEval("//g:family[@handle='_f0000']/g:mother")[0]
            mother.unlinkNode()
            mother.freeNode()
            persons = input_ctxt.xpathEval("//g:person")
            childof = persons[1].newChild(None, 'childof', None)
            childof.newProp('hlink', '_f0000')
            childof = persons[1].newChild(None, 'childof', None)
            childof.newProp('hlink', '_f0001')
            families = input_ctxt.xpathEval("//g:family")
            childref = families[0].newChild(None, 'childref', None)
            childref.newProp('hlink', '_i0001')
            parentin = persons[2].newChild(None, 'parentin', None)
            parentin.newProp('hlink', '_f0001')
            father = families[1].newChild(None, 'father', None)
            father.newProp('hlink', '_i0002')
            childref = families[1].newChild(None, 'childref', None)
            childref.newProp('hlink', '_i0001')
            with CopiedDoc(self.basedoc) as expect:
                with XpathContext(expect) as ctxt:
                    persons = ctxt.xpathEval("//g:person")
                    altname = persons[0].newChild(None, 'name', None)
                    altname.newProp('alt', '1')
                    altname.newProp('type', 'Birth Name')
                    altname.newChild(None, 'surname', 'Person 2')
                    attr = persons[0].newChild(None, 'attribute', None)
                    attr.newProp('type', 'Merged Gramps ID')
                    attr.newProp('value', 'I0002')
                    parentref = ctxt.xpathEval("//g:person[@handle='_i0000']/g:parentin")[0]
                    attr.addNextSibling(parentref) # restore order of elements
                    persons[2].unlinkNode()
                    persons[2].freeNode()
                    families = ctxt.xpathEval("//g:family")
                    families[1].unlinkNode()
                    families[1].freeNode()
                    childof = ctxt.xpathEval("//g:person[@handle='_i0001']/g:childof")
                    childof[1].unlinkNode()
                    childof[1].freeNode()
                    self.do_case('I0000', 'I0002', self.basedoc, expect)

    def test_ldsord(self):
        with XpathContext(self.basedoc) as input_ctxt:
            parentin = input_ctxt.xpathEval("//g:person[@handle='_i0001']/g:parentin")[0]
            parentin.unlinkNode()
            parentin.freeNode()
            mother = input_ctxt.xpathEval("//g:family[@handle='_f0000']/g:mother")[0]
            mother.unlinkNode()
            mother.freeNode()
            persons = input_ctxt.xpathEval("//g:person")
            parentin = persons[2].newChild(None, 'parentin', None)
            parentin.newProp('hlink', '_f0001')
            family = input_ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
            father = family.newChild(None, 'father', None)
            father.newProp('hlink', '_i0002')
            ldsord = persons[3].newChild(None, 'lds_ord', None)
            ldsord.newProp('type', 'sealed_to_parents')
            sealedto = ldsord.newChild(None, 'sealed_to', None)
            sealedto.newProp('hlink', '_f0001')
            with CopiedDoc(self.basedoc) as expect:
                with XpathContext(expect) as ctxt:
                    persons = ctxt.xpathEval("//g:person")
                    altname = persons[0].newChild(None, 'name', None)
                    altname.newProp('alt', '1')
                    altname.newProp('type', 'Birth Name')
                    altname.newChild(None, 'surname', 'Person 2')
                    attr = persons[0].newChild(None, 'attribute', None)
                    attr.newProp('type', 'Merged Gramps ID')
                    attr.newProp('value', 'I0002')
                    parentref = ctxt.xpathEval("//g:person[@handle='_i0000']/g:parentin")[0]
                    attr.addNextSibling(parentref) # restore order of elements
                    persons[2].unlinkNode()
                    persons[2].freeNode()
                    families = ctxt.xpathEval("//g:family")
                    families[1].unlinkNode()
                    families[1].freeNode()
                    sealedto = ctxt.xpathEval("//g:sealed_to")[0]
                    sealedto.setProp('hlink', '_f0000')
                    self.do_case('I0000', 'I0002', self.basedoc, expect)

    # This test fails because the assigment of family ids shifts F0000 to F0001
    # and F0001 to F0002!
    #def test_ldsord_cross(self):
    #    with XpathContext(self.basedoc) as input_ctxt:
    #        parentin = input_ctxt.xpathEval("//g:person[@handle='_i0001']/g:parentin")[0]
    #        parentin.unlinkNode()
    #        parentin.freeNode()
    #        mother = input_ctxt.xpathEval("//g:family[@handle='_f0000']/g:mother")[0]
    #        mother.unlinkNode()
    #        mother.freeNode()
    #        persons = input_ctxt.xpathEval("//g:person")
    #        parentin = persons[2].newChild(None, 'parentin', None)
    #        parentin.newProp('hlink', '_f0001')
    #        family = input_ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
    #        father = family.newChild(None, 'father', None)
    #        father.newProp('hlink', '_i0002')
    #        ldsord = persons[0].newChild(None, 'lds_ord', None)
    #        ldsord.newProp('type', 'sealed_to_parents')
    #        sealedto = ldsord.newChild(None, 'sealed_to', None)
    #        sealedto.newProp('hlink', '_f0001')
    #        with CopiedDoc(self.basedoc) as expect:
    #            with XpathContext(expect) as ctxt:
    #                persons = ctxt.xpathEval("//g:person")
    #                altname = persons[0].newChild(None, 'name', None)
    #                altname.newProp('alt', '1')
    #                altname.newProp('type', 'Birth Name')
    #                altname.newChild(None, 'surname', 'Person 2')
    #                ldsord = ctxt.xpathEval("//g:lds_ord")[0]
    #                altname.addNextSibling(ldsord) # restore order of elements
    #                attr = persons[0].newChild(None, 'attribute', None)
    #                attr.newProp('type', 'Merged Gramps ID')
    #                attr.newProp('value', 'I0002')
    #                parentref = ctxt.xpathEval("//g:person[@handle='_i0000']/g:parentin")[0]
    #                attr.addNextSibling(parentref) # restore order of elements
    #                persons[2].unlinkNode()
    #                persons[2].freeNode()
    #                families = ctxt.xpathEval("//g:family")
    #                families[1].unlinkNode()
    #                families[1].freeNode()
    #                sealedto = ctxt.xpathEval("//g:sealed_to")[0]
    #                sealedto.setProp('hlink', '_f0000')
    #                self.do_case('I0000', 'I0002', self.basedoc, expect)

    def test_ldsord_self(self):
        with XpathContext(self.basedoc) as input_ctxt:
            parentin = input_ctxt.xpathEval("//g:person[@handle='_i0001']/g:parentin")[0]
            parentin.unlinkNode()
            parentin.freeNode()
            mother = input_ctxt.xpathEval("//g:family[@handle='_f0000']/g:mother")[0]
            mother.unlinkNode()
            mother.freeNode()
            persons = input_ctxt.xpathEval("//g:person")
            parentin = persons[2].newChild(None, 'parentin', None)
            parentin.newProp('hlink', '_f0001')
            family = input_ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
            father = family.newChild(None, 'father', None)
            father.newProp('hlink', '_i0002')
            ldsord = persons[2].newChild(None, 'lds_ord', None)
            ldsord.newProp('type', 'sealed_to_parents')
            sealedto = ldsord.newChild(None, 'sealed_to', None)
            sealedto.newProp('hlink', '_f0001')
            with CopiedDoc(self.basedoc) as expect:
                with XpathContext(expect) as ctxt:
                    persons = ctxt.xpathEval("//g:person")
                    altname = persons[0].newChild(None, 'name', None)
                    altname.newProp('alt', '1')
                    altname.newProp('type', 'Birth Name')
                    altname.newChild(None, 'surname', 'Person 2')
                    ldsord = ctxt.xpathEval("//g:lds_ord")[0]
                    altname.addNextSibling(ldsord) # restore order of elements
                    attr = persons[0].newChild(None, 'attribute', None)
                    attr.newProp('type', 'Merged Gramps ID')
                    attr.newProp('value', 'I0002')
                    parentref = ctxt.xpathEval("//g:person[@handle='_i0000']/g:parentin")[0]
                    attr.addNextSibling(parentref) # restore order of elements
                    persons[2].unlinkNode()
                    persons[2].freeNode()
                    families = ctxt.xpathEval("//g:family")
                    families[1].unlinkNode()
                    families[1].freeNode()
                    sealedto = ctxt.xpathEval("//g:sealed_to")[0]
                    sealedto.setProp('hlink', '_f0000')
                    self.do_case('I0000', 'I0002', self.basedoc, expect)

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
        self.basedoc = libxml2.readDoc(self.base_str + base_str, '', None,
                                       libxml2.XML_PARSE_NONET)

    def test_father_son_merge(self):
        """Merge two families where the fathers have a father-son relationship
        so that an error is raised."""
        with XpathContext(self.basedoc) as input_ctxt:
            person = input_ctxt.xpathEval("//g:person[@handle='_i0002']")[0]
            childof = person.newChild(None, 'childof', None)
            childof.newProp('hlink', '_f0000')
            family = input_ctxt.xpathEval("//g:family[@handle='_f0000']")[0]
            childref = family.newChild(None, 'childref', None)
            childref.newProp('hlink', '_i0002')
            with CopiedDoc(self.basedoc) as expect:
                self.do_family_case('F0000', 'F0001', 'i0000', 'i0001',
                        self.basedoc, expect, test_error_str=_("A parent and "
                        "child cannot be merged. To merge these people, you "
                        "must first break the relationship between them."))

    def test_child_parent_merge_no_father(self):
        """Merge two families where the phoenix family has no father and
        the father of the titanic family is a child of the phoenix family."""
        with XpathContext(self.basedoc) as input_ctxt:
            parentin = input_ctxt.xpathEval("//g:person[@handle='_i0002']/g:parentin")[0]
            parentin.unlinkNode()
            parentin.freeNode()
            father = input_ctxt.xpathEval("//g:family[@handle='_f0001']/g:father")[0]
            father.unlinkNode()
            father.freeNode()
            person = input_ctxt.xpathEval("//g:person[@handle='_i0000']")[0]
            childof = person.newChild(None, 'childof', None)
            childof.newProp('hlink', '_f0001')
            family = input_ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
            childref = family.newChild(None, 'childref', None)
            childref.newProp('hlink', '_i0000')
            with CopiedDoc(self.basedoc) as expect:
                self.do_family_case('F0000', 'F0001', 'i0000', 'i0001',
                        self.basedoc, expect, test_error_str=_("A parent and "
                        "child cannot be merged. To merge these people, you "
                        "must first break the relationship between them."))

    def test_child_parent_merge_no_father_swapped(self):
        """Merge two families where the phoenix family has no father and
        the father of the titanic family, which is the phoenix-father, is a
        child of the phoenix family."""
        with XpathContext(self.basedoc) as input_ctxt:
            parentin = input_ctxt.xpathEval("//g:person[@handle='_i0000']/g:parentin")[0]
            parentin.unlinkNode()
            parentin.freeNode()
            father = input_ctxt.xpathEval("//g:family[@handle='_f0000']/g:father")[0]
            father.unlinkNode()
            father.freeNode()
            person = input_ctxt.xpathEval("//g:person[@handle='_i0002']")[0]
            childof = person.newChild(None, 'childof', None)
            childof.newProp('hlink', '_f0000')
            family = input_ctxt.xpathEval("//g:family[@handle='_f0000']")[0]
            childref = family.newChild(None, 'childref', None)
            childref.newProp('hlink', '_i0002')
            with CopiedDoc(self.basedoc) as expect:
                self.do_family_case('F0000', 'F0001', 'i0002', 'i0001',
                        self.basedoc, expect, test_error_str=_("A parent and "
                        "child cannot be merged. To merge these people, you "
                        "must first break the relationship between them."))

    def test_regular_merge(self):
        """Merge two families succesfully"""
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                persons = ctxt.xpathEval("//g:person")
                altname = persons[0].newChild(None, 'name', None)
                altname.newProp('alt', '1')
                altname.newProp('type', 'Birth Name')
                altname.newChild(None, 'surname', 'Person 2')
                attr = persons[0].newChild(None, 'attribute', None)
                attr.newProp('type', 'Merged Gramps ID')
                attr.newProp('value', 'I0002')
                parentref = ctxt.xpathEval("//g:person[@handle='_i0000']/g:parentin")[0]
                attr.addNextSibling(parentref) # restore order of elements
                persons[2].unlinkNode()
                persons[2].freeNode()
                altname = persons[1].newChild(None, 'name', None)
                altname.newProp('alt', '1')
                altname.newProp('type', 'Birth Name')
                altname.newChild(None, 'surname', 'Person 3')
                attr = persons[1].newChild(None, 'attribute', None)
                attr.newProp('type', 'Merged Gramps ID')
                attr.newProp('value', 'I0003')
                parentref = ctxt.xpathEval("//g:person[@handle='_i0001']/g:parentin")[0]
                attr.addNextSibling(parentref) # restore order of elements
                persons[3].unlinkNode()
                persons[3].freeNode()
                family = ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
                family.unlinkNode()
                family.freeNode()
                self.do_family_case('F0000', 'F0001', 'i0000', 'i0001', self.basedoc, expect)

    def test_father_swapped(self):
        "Merge two families where the phoenix-father is of the titanic family."
        with CopiedDoc(self.basedoc) as expect:
            with XpathContext(expect) as ctxt:
                persons = ctxt.xpathEval("//g:person")
                altname = persons[2].newChild(None, 'name', None)
                altname.newProp('alt', '1')
                altname.newProp('type', 'Birth Name')
                altname.newChild(None, 'surname', 'Person 0')
                attr = persons[2].newChild(None, 'attribute', None)
                attr.newProp('type', 'Merged Gramps ID')
                attr.newProp('value', 'I0000')
                parentref = ctxt.xpathEval("//g:person[@handle='_i0002']/g:parentin")[0]
                parentref.setProp('hlink', '_f0000')
                attr.addNextSibling(parentref) # restore order of elements
                persons[0].unlinkNode()
                persons[0].freeNode()
                altname = persons[1].newChild(None, 'name', None)
                altname.newProp('alt', '1')
                altname.newProp('type', 'Birth Name')
                altname.newChild(None, 'surname', 'Person 3')
                attr = persons[1].newChild(None, 'attribute', None)
                attr.newProp('type', 'Merged Gramps ID')
                attr.newProp('value', 'I0003')
                parentref = ctxt.xpathEval("//g:person[@handle='_i0001']/g:parentin")[0]
                attr.addNextSibling(parentref) # restore order of elements
                persons[3].unlinkNode()
                persons[3].freeNode()
                family = ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
                family.unlinkNode()
                family.freeNode()
                father = ctxt.xpathEval("//g:family[@handle='_f0000']/g:father")[0]
                father.setProp('hlink', '_i0002')
                self.do_family_case('F0000', 'F0001', 'i0002', 'i0001', self.basedoc, expect)

    #def test_mother_swapped(self):

    def test_no_father(self):
        """Merge two families, where one family has not father"""
        with XpathContext(self.basedoc) as input_ctxt:
            parentin = input_ctxt.xpathEval("//g:person[@handle='_i0002']/g:parentin")[0]
            parentin.unlinkNode()
            parentin.freeNode()
            father = input_ctxt.xpathEval("//g:family[@handle='_f0001']/g:father")[0]
            father.unlinkNode()
            father.freeNode()
            with CopiedDoc(self.basedoc) as expect:
                with XpathContext(expect) as ctxt:
                    persons = ctxt.xpathEval("//g:person")
                    altname = persons[1].newChild(None, 'name', None)
                    altname.newProp('alt', '1')
                    altname.newProp('type', 'Birth Name')
                    altname.newChild(None, 'surname', 'Person 3')
                    attr = persons[1].newChild(None, 'attribute', None)
                    attr.newProp('type', 'Merged Gramps ID')
                    attr.newProp('value', 'I0003')
                    parentref = ctxt.xpathEval("//g:person[@handle='_i0001']/g:parentin")[0]
                    attr.addNextSibling(parentref) # restore order of elements
                    persons[3].unlinkNode()
                    persons[3].freeNode()
                    family = ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
                    family.unlinkNode()
                    family.freeNode()
                    self.do_family_case('F0000', 'F0001', 'i0000', 'i0001',
                                        self.basedoc, expect)

    def test_no_mother_swapped(self):
        """Merge two families where one family has no mother and the
        phoenix-mother is from the titanic family."""
        with XpathContext(self.basedoc) as input_ctxt:
            parentin = input_ctxt.xpathEval("//g:person[@handle='_i0001']/g:parentin")[0]
            parentin.unlinkNode()
            parentin.freeNode()
            mother = input_ctxt.xpathEval("//g:family[@handle='_f0000']/g:mother")[0]
            mother.unlinkNode()
            mother.freeNode()
            with CopiedDoc(self.basedoc) as expect:
                with XpathContext(expect) as ctxt:
                    persons = ctxt.xpathEval("//g:person")
                    altname = persons[0].newChild(None, 'name', None)
                    altname.newProp('alt', '1')
                    altname.newProp('type', 'Birth Name')
                    altname.newChild(None, 'surname', 'Person 2')
                    attr = persons[0].newChild(None, 'attribute', None)
                    attr.newProp('type', 'Merged Gramps ID')
                    attr.newProp('value', 'I0002')
                    parentref = ctxt.xpathEval("//g:person[@handle='_i0000']/g:parentin")[0]
                    attr.addNextSibling(parentref) # restore order of elements
                    persons[2].unlinkNode()
                    persons[2].freeNode()
                    parentin = ctxt.xpathEval("//g:person[@handle='_i0003']/g:parentin")[0]
                    parentin.setProp('hlink', '_f0000')
                    family = ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
                    family.unlinkNode()
                    family.freeNode()
                    family = ctxt.xpathEval("//g:family[@handle='_f0000']")[0]
                    mother = family.newChild(None, 'mother', None)
                    mother.newProp('hlink', '_i0003')
                    self.do_family_case('F0000', 'F0001', 'i0000', 'i0003',
                                        self.basedoc, expect)

    #def test_no_parents(self):

    def test_childref_notyet(self):
        """Merge two families with non-duplicate child references."""
        with XpathContext(self.basedoc) as input_ctxt:
            people = input_ctxt.xpathEval("//g:people")[0]
            person = people.newChild(None, 'person', None)
            person.newProp('handle', '_i0004')
            person.newProp('id', '_I0004')
            person.newChild(None, 'gender', 'M')
            name = person.newChild(None, 'name', None)
            name.newProp('type', 'Birth Name')
            name.newChild(None, 'surname', 'Person 4')
            childof = person.newChild(None, 'childof', None)
            childof.newProp('hlink', '_f0001')
            family = input_ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
            childref = family.newChild(None, 'childref', None)
            childref.newProp('hlink', '_i0004')
            with CopiedDoc(self.basedoc) as expect:
                with XpathContext(expect) as ctxt:
                    persons = ctxt.xpathEval("//g:person")
                    altname = persons[0].newChild(None, 'name', None)
                    altname.newProp('alt', '1')
                    altname.newProp('type', 'Birth Name')
                    altname.newChild(None, 'surname', 'Person 2')
                    attr = persons[0].newChild(None, 'attribute', None)
                    attr.newProp('type', 'Merged Gramps ID')
                    attr.newProp('value', 'I0002')
                    parentref = ctxt.xpathEval("//g:person[@handle='_i0000']/g:parentin")[0]
                    attr.addNextSibling(parentref) # restore order of elements
                    persons[2].unlinkNode()
                    persons[2].freeNode()
                    altname = persons[1].newChild(None, 'name', None)
                    altname.newProp('alt', '1')
                    altname.newProp('type', 'Birth Name')
                    altname.newChild(None, 'surname', 'Person 3')
                    attr = persons[1].newChild(None, 'attribute', None)
                    attr.newProp('type', 'Merged Gramps ID')
                    attr.newProp('value', 'I0003')
                    parentref = ctxt.xpathEval("//g:person[@handle='_i0001']/g:parentin")[0]
                    attr.addNextSibling(parentref) # restore order of elements
                    persons[3].unlinkNode()
                    persons[3].freeNode()
                    family = ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
                    family.unlinkNode()
                    family.freeNode()
                    childof = ctxt.xpathEval("//g:person[@handle='_i0004']/g:childof")[0]
                    childof.setProp('hlink', '_f0000')
                    family = ctxt.xpathEval("//g:family[@handle='_f0000']")[0]
                    childref = family.newChild(None, 'childref', None)
                    childref.newProp('hlink', '_i0004')
                    self.do_family_case('F0000', 'F0001', 'i0000', 'i0001',
                                        self.basedoc, expect)

    def test_childref_already(self):
        """Merge two families with duplicate child references."""
        with XpathContext(self.basedoc) as input_ctxt:
            people = input_ctxt.xpathEval("//g:people")[0]
            person = people.newChild(None, 'person', None)
            person.newProp('handle', '_i0004')
            person.newProp('id', '_I0004')
            person.newChild(None, 'gender', 'M')
            name = person.newChild(None, 'name', None)
            name.newProp('type', 'Birth Name')
            name.newChild(None, 'surname', 'Person 4')
            childof = person.newChild(None, 'childof', None)
            childof.newProp('hlink', '_f0000')
            childof = person.newChild(None, 'childof', None)
            childof.newProp('hlink', '_f0001')
            family = input_ctxt.xpathEval("//g:family[@handle='_f0000']")[0]
            childref = family.newChild(None, 'childref', None)
            childref.newProp('hlink', '_i0004')
            family = input_ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
            childref = family.newChild(None, 'childref', None)
            childref.newProp('hlink', '_i0004')
            with CopiedDoc(self.basedoc) as expect:
                with XpathContext(expect) as ctxt:
                    persons = ctxt.xpathEval("//g:person")
                    altname = persons[0].newChild(None, 'name', None)
                    altname.newProp('alt', '1')
                    altname.newProp('type', 'Birth Name')
                    altname.newChild(None, 'surname', 'Person 2')
                    attr = persons[0].newChild(None, 'attribute', None)
                    attr.newProp('type', 'Merged Gramps ID')
                    attr.newProp('value', 'I0002')
                    parentref = ctxt.xpathEval("//g:person[@handle='_i0000']/g:parentin")[0]
                    attr.addNextSibling(parentref) # restore order of elements
                    persons[2].unlinkNode()
                    persons[2].freeNode()
                    altname = persons[1].newChild(None, 'name', None)
                    altname.newProp('alt', '1')
                    altname.newProp('type', 'Birth Name')
                    altname.newChild(None, 'surname', 'Person 3')
                    attr = persons[1].newChild(None, 'attribute', None)
                    attr.newProp('type', 'Merged Gramps ID')
                    attr.newProp('value', 'I0003')
                    parentref = ctxt.xpathEval("//g:person[@handle='_i0001']/g:parentin")[0]
                    attr.addNextSibling(parentref) # restore order of elements
                    persons[3].unlinkNode()
                    persons[3].freeNode()
                    family = ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
                    family.unlinkNode()
                    family.freeNode()
                    childof = ctxt.xpathEval("//g:person[@handle='_i0004']/g:childof")[1]
                    childof.unlinkNode()
                    childof.freeNode()
                    self.do_family_case('F0000', 'F0001', 'i0000', 'i0001',
                                        self.basedoc, expect)

    # this test fails because the families get IDs F0001 and F0002!
    #def test_ldsord(self):
    #    """Merge two families where one person has a reference to the
    #    titanic family."""
    #    with XpathContext(self.basedoc) as input_ctxt:
    #        person = input_ctxt.xpathEval("//g:person[@handle='_i0000']")[0]
    #        ldsord = person.newChild(None, 'lds_ord', None)
    #        ldsord.newProp('type', 'sealed_to_parents')
    #        sealedto = ldsord.newChild(None, 'sealed_to', None)
    #        sealedto.newProp('hlink', '_f0001')
    #        parentin = input_ctxt.xpathEval("//g:person[@handle='_i0000']/g:parentin")[0]
    #        ldsord.addNextSibling(parentin)
    #        with CopiedDoc(self.basedoc) as expect:
    #            with XpathContext(expect) as ctxt:
    #                persons = ctxt.xpathEval("//g:person")
    #                altname = persons[0].newChild(None, 'name', None)
    #                altname.newProp('alt', '1')
    #                altname.newProp('type', 'Birth Name')
    #                altname.newChild(None, 'surname', 'Person 2')
    #                ldsord = ctxt.xpathEval("//g:lds_ord")[0]
    #                altname.addNextSibling(ldsord) # restore order of elements
    #                attr = persons[0].newChild(None, 'attribute', None)
    #                attr.newProp('type', 'Merged Gramps ID')
    #                attr.newProp('value', 'I0002')
    #                parentref = ctxt.xpathEval("//g:person[@handle='_i0000']/g:parentin")[0]
    #                attr.addNextSibling(parentref) # restore order of elements
    #                persons[2].unlinkNode()
    #                persons[2].freeNode()
    #                altname = persons[1].newChild(None, 'name', None)
    #                altname.newProp('alt', '1')
    #                altname.newProp('type', 'Birth Name')
    #                altname.newChild(None, 'surname', 'Person 3')
    #                attr = persons[1].newChild(None, 'attribute', None)
    #                attr.newProp('type', 'Merged Gramps ID')
    #                attr.newProp('value', 'I0003')
    #                parentref = ctxt.xpathEval("//g:person[@handle='_i0001']/g:parentin")[0]
    #                attr.addNextSibling(parentref) # restore order of elements
    #                persons[3].unlinkNode()
    #                persons[3].freeNode()
    #                family = ctxt.xpathEval("//g:family[@handle='_f0001']")[0]
    #                family.unlinkNode()
    #                family.freeNode()
    #                sealedto = ctxt.xpathEval("//g:sealed_to")[0]
    #                sealedto.setProp('hlink', '_f0000')
    #                self.do_family_case('F0000', 'F0001', 'i0000', 'i0001',
    #                                    self.basedoc, expect)


if __name__ == "__main__":
    import sys
    if not HAS_CLIMERGE:
        print('This program needs the third party "CliMerge" plugin.', file=sys.stderr)
        sys.exit(1)
    if not HAS_EXPORTRAW:
        print('This program needs the third party "ExportRaw" plugin.', file=sys.stderr)
        sys.exit(1)
    unittest.main()
