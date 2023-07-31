# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2020-      Serge Noiraud
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
Narrative Web index for multi languages
"""
# ------------------------------------------------
# python modules
# ------------------------------------------------
import logging

# ------------------------------------------------
# Gramps module
# ------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.plugins.lib.libhtml import Html

# ------------------------------------------------
# specific narrative web import
# ------------------------------------------------
from gramps.plugins.webreport.basepage import BasePage

_ = glocale.translation.sgettext
LOG = logging.getLogger(".multilang")

REDIRECT = """
function lang() {
  var langs = %s;
  var lang = navigator.languages || navigator.userLanguages || window.navigator.userLanguage;
  var found = langs[0];
  for (i=0; i < lang.length; i++) {
    for (j=0; j < langs.length; j++) {
      if (lang[i] == langs[j]) {
        found = lang[i];
        break;
      };
    };
  };
  location.replace("./"+found+"/index%s");
}
"""


class IndexPage(BasePage):
    """
    This class is responsible for redirecting the user to the good page
    """

    def __init__(self, report, langs):
        """
        Create an index for multi language.
        We will be redirected to the good page depending of the browser
        language. If the browser language is unknown, we use the first
        defined in the display tab of the narrative web configuration.

        @param: report -- The instance of the main report class
                          for this report
        @param: langs  -- The languages to process
        """
        BasePage.__init__(self, report, None, "index")
        output_file, sio = report.create_file("index", ext="index")
        page, head, body = Html.page("index", self.report.encoding, langs[0][0])
        body.attr = ' onload="lang();"'
        my_langs = "["
        for lang in langs:
            my_langs += "'" + lang[0].replace("_", "-")
            my_langs += "', "
        my_langs += "]"
        with Html("script", type="text/javascript") as jsc:
            head += jsc
            jsc += REDIRECT % (my_langs, self.ext)

        # send page out for processing
        # and close the file
        self.xhtml_writer(page, output_file, sio, 0)
        self.report.close_file(output_file, sio, 0)
