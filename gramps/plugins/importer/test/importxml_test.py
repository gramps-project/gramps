# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011 Michiel D. Nauta
# Copyright (C) 2013 Vassilii Khachaturov
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
Test XML import.
"""
from __future__ import print_function, unicode_literals

import unittest
import time
import os
import subprocess
import libxml2
import libxslt

from gramps.plugins.lib.libgrampsxml import GRAMPS_XML_VERSION
from gramps.gen.const import ROOT_DIR, USER_PLUGINS
from gramps.version import VERSION

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

@unittest.skipUnless(HAS_EXPORTRAW,
        'These tests need the 3rd-party plugin "ExportRaw".')
class BaseImportTest(unittest.TestCase):
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

    def do_case(self, input_doc, expect_doc,
                test_error_str='', debug=False):
        """Do the import and "assert" the result."""
        process = subprocess.Popen('python Gramps.py -d .Date -d .ImportXML '
                                   '--config=preferences.eprefix:DEFAULT '
                                   '-i - -f gramps '
                                   '-e - -f gramps',
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
            print('err_str:', err_str)
            print('input :', self.canonicalize(input_doc))
            print('result:', self.canonicalize(result_str))
            print('expect:', self.canonicalize(expect_doc))
        self.assertEqual(self.canonicalize(result_str),
                         self.canonicalize(expect_doc))

class DateTest(BaseImportTest):
    def setUp(self):
        self.base_setup()
        self.events_str = """
        <events>
          <event handle="_e0000" id="E0000">
            <type>Birth</type>
            {datexml}
            <description>Event 0</description>
          </event>
        </events>
        </database>"""
        self.datexml_src = self.datexml_trg = None

    def tearDown(self):
        self.basedoc = libxml2.readDoc(
                self.base_str + self.events_str.format(datexml=self.datexml_src),
                '', None, libxml2.XML_PARSE_NONET)
        expect = libxml2.readDoc(
                self.base_str + self.events_str.format(datexml=self.datexml_trg),
                '', None, libxml2.XML_PARSE_NONET)
        try:
            self.do_case(self.basedoc, expect)
        except:
            raise
        finally:
            expect.freeDoc()

    def test_correct_dateval_passed_verbatim(self):
        self.datexml_trg = self.datexml_src = \
                '<dateval val="1787-05-20"/>'

    def test_correct_daterange_passed_verbatim(self):
        self.datexml_trg = self.datexml_src = \
                '<daterange start="1746" stop="1755"/>'

    def test_dateval_long_Feb_converted_to_datestr(self):
        self.datexml_src = '<dateval val="1787-02-30"/>'
        self.datexml_trg = '<datestr val="&lt;dateval val=&quot;1787-02-30&quot;/&gt;"/>'

    def test_datespan_long_Feb_converted_to_datestr(self):
        self.datexml_src = '<datespan start="1746-02-30" stop="2000"/>'
        self.datexml_trg = '<datestr val="&lt;datespan start=&quot;1746-02-30&quot; stop=&quot;2000&quot;/&gt;"/>'


if __name__ == "__main__":
    import sys
    if not HAS_EXPORTRAW:
        print('This program needs the third party "ExportRaw" plugin.', file=sys.stderr)
        sys.exit(1)
    unittest.main()
