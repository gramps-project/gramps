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
    AddressBookPage
"""
# ------------------------------------------------
# python modules
# ------------------------------------------------
from decimal import getcontext
import logging

# ------------------------------------------------
# Gramps module
# ------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.plug.report import Bibliography
from gramps.plugins.lib.libhtml import Html

# ------------------------------------------------
# specific narrative web import
# ------------------------------------------------
from gramps.plugins.webreport.basepage import BasePage
from gramps.plugins.webreport.common import FULLCLEAR

_ = glocale.translation.sgettext
LOG = logging.getLogger(".NarrativeWeb")
getcontext().prec = 8


class AddressBookPage(BasePage):
    """
    Create one page for one Address
    """

    def __init__(
        self, report, the_lang, the_title, person_handle, has_add, has_res, has_url
    ):
        """
        @param: report        -- The instance of the main report class
                                 for this report
        @param: the_lang      -- The lang to process
        @param: the_title     -- The title page related to the language
        @param: person_handle -- the url, address and residence to use
                                 for the report
        @param: has_add       -- the address to use for the report
        @param: has_res       -- the residence to use for the report
        @param: has_url       -- the url to use for the report
        """
        person = report.database.get_person_from_handle(person_handle)
        BasePage.__init__(self, report, the_lang, the_title, person.gramps_id)
        self.bibli = Bibliography()

        self.uplink = True

        # set the file name and open file
        output_file, sio = self.report.create_file(person_handle, "addr")
        result = self.write_header(_("Address Book"))
        addressbookpage, dummy_head, dummy_body, outerwrapper = result

        # begin address book page division and section title
        with Html("div", class_="content", id="AddressBookDetail") as addressbookdetail:
            outerwrapper += addressbookdetail

            link = self.new_person_link(person_handle, uplink=True, person=person)
            addressbookdetail += Html("h3", link)

            # individual has an address
            if has_add:
                addressbookdetail += self.display_addr_list(has_add, None)

            # individual has a residence
            if has_res:
                addressbookdetail.extend(self.dump_residence(res) for res in has_res)

            # individual has a url
            if has_url:
                addressbookdetail += self.display_url_list(has_url)

        # add fullclear for proper styling
        # and footer section to page
        footer = self.write_footer(None)
        outerwrapper += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(addressbookpage, output_file, sio, 0)
