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
# Copyright (C) 2010-      Serge Noiraud
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2013       Benny Malengier
# Copyright (C) 2016       Allen Crider
# Copyright (C) 2018       Theo van Rijn
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
    ContactPage
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
from gramps.gen.utils.config import get_researcher
from gramps.plugins.lib.libhtml import Html

#------------------------------------------------
# specific narrative web import
#------------------------------------------------
from gramps.plugins.webreport.basepage import BasePage
from gramps.plugins.webreport.common import FULLCLEAR

_ = glocale.translation.sgettext
LOG = logging.getLogger(".NarrativeWeb")
getcontext().prec = 8

class ContactPage(BasePage):
    """
    This class is responsible for displaying information about the 'Researcher'
    """
    def __init__(self, report, the_lang, the_title):
        """
        @param: report    -- The instance of the main report class for
                             this report
        @param: the_lang  -- The lang to process
        @param: the_title -- The title page related to the language
        """
        BasePage.__init__(self, report, the_lang, the_title)

        output_file, sio = self.report.create_file("contact")
        result = self.write_header(self._('Contact'))
        contactpage, head, dummy_body, outerwrapper = result
        ldatec = 0

        # begin contact division
        with Html("div", class_="content", id="Contact") as section:
            outerwrapper += section

            # begin summaryarea division
            with Html("div", id='summaryarea') as summaryarea:
                section += summaryarea

                contactimg = self.add_image('contactimg', head, 200)
                if contactimg is not None:
                    summaryarea += contactimg

                # get researcher information
                res = get_researcher()

                with Html("div", id='researcher') as researcher:
                    summaryarea += researcher

                    if res.name:
                        res.name = res.name.replace(',,,', '')
                        researcher += Html("h3", res.name, inline=True)
                    if res.addr:
                        researcher += Html("span", res.addr,
                                           id='streetaddress', inline=True)
                    if res.locality:
                        researcher += Html("span", res.locality,
                                           id="locality", inline=True)
                    text = "".join([res.city, res.state, res.postal])
                    if text:
                        city = Html("span", res.city, id='city', inline=True)
                        state = Html("span", res.state, id='state', inline=True)
                        postal = Html("span", res.postal, id='postalcode',
                                      inline=True)
                        researcher += (city, state, postal)
                    if res.country:
                        researcher += Html("span", res.country,
                                           id='country', inline=True)
                    if res.email:
                        researcher += Html("span", id='email') + (
                            Html("a", res.email,
                                 href='mailto:%s' % res.email, inline=True)
                        )

                    # add clear line for proper styling
                    summaryarea += FULLCLEAR

                    note_id = report.options['contactnote']
                    if note_id:
                        note = self.r_db.get_note_from_gramps_id(note_id)
                        if note:
                            note_text = self.get_note_format(note, False)

                            # attach note
                            summaryarea += note_text

                            # last modification of this note
                            ldatec = note.get_change_time()

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        outerwrapper += (FULLCLEAR, footer)

        # send page out for porcessing
        # and close the file
        self.xhtml_writer(contactpage, output_file, sio, 0)
