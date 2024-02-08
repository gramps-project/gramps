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
    AddressBookListPage
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
from gramps.plugins.lib.libhtml import Html

# ------------------------------------------------
# specific narrative web import
# ------------------------------------------------
from gramps.plugins.webreport.basepage import BasePage
from gramps.plugins.webreport.common import FULLCLEAR

LOG = logging.getLogger(".NarrativeWeb")
_ = glocale.translation.sgettext
getcontext().prec = 8


class AddressBookListPage(BasePage):
    """
    Create the index for addresses.
    """

    def __init__(self, report, the_lang, the_title, has_url_addr_res):
        """
        @param: report           -- The instance of the main report class
                                    for this report
        @param: the_lang         -- The lang to process
        @param: the_title        -- The title page related to the language
        @param: has_url_addr_res -- The url, address and residence to use
                                    for the report
        """
        BasePage.__init__(self, report, the_lang, the_title)

        # Name the file, and create it
        output_file, sio = self.report.create_file("addressbook")

        # Add xml, doctype, meta and stylesheets
        result = self.write_header(_("Address Book"))
        addressbooklistpage, dummy_head, dummy_body, outerwrapper = result

        # begin AddressBookList division
        with Html("div", class_="content", id="AddressBookList") as addressbooklist:
            outerwrapper += addressbooklist

            # Address Book Page message
            msg = self._(
                "This page contains an index of all the individuals "
                "in the database, sorted by their surname, with one "
                "of the following: Address, Residence, or Web Links. "
                "Selecting the person&#8217;s name will take you "
                "to their individual Address Book page."
            )
            addressbooklist += Html("p", msg, id="description")

            # begin Address Book table
            with Html(
                "table", class_="infolist primobjlist addressbook " + self.dir
            ) as table:
                addressbooklist += table

                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                trow.extend(
                    Html("th", label, class_=colclass, inline=True)
                    for (label, colclass) in [
                        ["&nbsp;", "ColumnRowLabel"],
                        [self._("Full Name"), "ColumnName"],
                        [self._("Address"), "ColumnAddress"],
                        [self._("Residence"), "ColumnResidence"],
                        [self._("Web Links"), "ColumnWebLinks"],
                    ]
                )

                tbody = Html("tbody")
                table += tbody

                index = 1
                for (
                    dummy_sort_name,
                    person_handle,
                    has_add,
                    has_res,
                    has_url,
                ) in has_url_addr_res:
                    address = None
                    residence = None
                    weblinks = None

                    # has address but no residence event
                    if has_add and not has_res:
                        address = "X"

                    # has residence, but no addresses
                    elif has_res and not has_add:
                        residence = "X"

                    # has residence and addresses too
                    elif has_add and has_res:
                        address = "X"
                        residence = "X"

                    # has Web Links
                    if has_url:
                        weblinks = "X"

                    trow = Html("tr")
                    tbody += trow

                    trow.extend(
                        Html("td", data or "&nbsp;", class_=colclass, inline=True)
                        for (colclass, data) in [
                            ["ColumnRowLabel", index],
                            ["ColumnName", self.addressbook_link(person_handle)],
                            ["ColumnAddress", address],
                            ["ColumnResidence", residence],
                            ["ColumnWebLinks", weblinks],
                        ]
                    )
                    index += 1

        # Add footer and clearline
        footer = self.write_footer(None)
        outerwrapper += (FULLCLEAR, footer)

        # send the page out for processing
        # and close the file
        self.xhtml_writer(addressbooklistpage, output_file, sio, 0)
