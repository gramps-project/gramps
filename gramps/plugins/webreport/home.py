# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007       Johan Gonqvist <johan.gronqvist@gmail.com>
# Copyright (C) 2007-2009  Gary Burton <gary.burton@zen.co.uk>
# Copyright (C) 2007-2009  Stephane Charette <stephanecharette@gmail.com>
# Copyright (C) 2008-2009  Brian G. Matherly
# Copyright (C) 2008       Jason M. Simanek <jason@bohemianalps.com>
# Copyright (C) 2008-2011  Rob G. Healey <robhealey1@gmail.com>
# Copyright (C) 2010       Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2010-2017  Serge Noiraud
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2013       Benny Malengier
# Copyright (C) 2016       Allen Crider
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
Narrative Web Page generator.

Classe:
    HomePage
"""
#------------------------------------------------
# python modules
#------------------------------------------------
from decimal import getcontext
import logging

#------------------------------------------------
# Gramps module
#------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.plugins.lib.libhtml import Html

#------------------------------------------------
# specific narrative web import
#------------------------------------------------
from gramps.plugins.webreport.basepage import BasePage
from gramps.plugins.webreport.common import FULLCLEAR

_ = glocale.translation.sgettext
LOG = logging.getLogger(".NarrativeWeb")
getcontext().prec = 8

class HomePage(BasePage):
    """
    This class is responsible for displaying information about the Home page.
    """
    def __init__(self, report, title):
        """
        @param: report -- The instance of the main report class for
                          this report
        @param: title  -- Is the title of the web page
        """
        BasePage.__init__(self, report, title)
        ldatec = 0

        output_file, sio = self.report.create_file("index")
        homepage, head, body = self.write_header(self._('Home'))

        # begin home division
        with Html("div", class_="content", id="Home") as section:
            body += section

            homeimg = self.add_image('homeimg')
            if homeimg is not None:
                section += homeimg

            note_id = report.options['homenote']
            if note_id:
                note = self.r_db.get_note_from_gramps_id(note_id)
                note_text = self.get_note_format(note, False)

                # attach note
                section += note_text

                # last modification of this note
                ldatec = note.get_change_time()

        # create clear line for proper styling
        # create footer section
        footer = self.write_footer(ldatec)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(homepage, output_file, sio, ldatec)
