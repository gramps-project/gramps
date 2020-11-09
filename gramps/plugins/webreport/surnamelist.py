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
    SurnameListPage - Index for first letters of surname
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
from gramps.gen.display.name import displayer as _nd
from gramps.plugins.webreport.common import (get_first_letters, _KEYPERSON,
                                             alphabet_navigation, html_escape,
                                             sort_people, name_to_md5,
                                             first_letter, get_index_letter,
                                             primary_difference, FULLCLEAR)

_ = glocale.translation.sgettext
LOG = logging.getLogger(".NarrativeWeb")
getcontext().prec = 8

#################################################
#
#    Creates the Surname List page
#
#################################################
class SurnameListPage(BasePage):
    """
    This class is responsible for displaying the list of Surnames
    """
    ORDER_BY_NAME = 0
    ORDER_BY_COUNT = 1

    def __init__(self, report, the_lang, the_title, ppl_handle_list,
                 order_by=ORDER_BY_NAME, filename="surnames"):
        """
        @param: report          -- The instance of the main report class for
                                   this report
        @param: the_lang        -- The lang to process
        @param: the_title       -- The title page related to the language
        @param: ppl_handle_list -- The list of people for whom we need to create
                                   a page.
        @param: order_by        -- The way to sort surnames :
                                   Surnames or Surnames count
        @param: filename        -- The name to use for the Surnames page
        """
        BasePage.__init__(self, report, the_lang, the_title)
        prev_surname = ""
        prev_letter = " "

        if order_by == self.ORDER_BY_NAME:
            output_file, sio = self.report.create_file(filename)
            result = self.write_header(self._('Surnames'))
        else:
            output_file, sio = self.report.create_file("surnames_count")
            result = self.write_header(self._('Surnames by person count'))
        surnamelistpage, dummy_head, dummy_body, outerwrapper = result

        # begin surnames division
        with Html("div", class_="content", id="surnames") as surnamelist:
            outerwrapper += surnamelist

            # page message
            msg = self._('This page contains an index of all the '
                         'surnames in the database. Selecting a link '
                         'will lead to a list of individuals in the '
                         'database with this same surname.')
            surnamelist += Html("p", msg, id="description")

            # add alphabet navigation...
            # only if surname list not surname count
            if order_by == self.ORDER_BY_NAME:
                index_list = get_first_letters(self.r_db, ppl_handle_list,
                                               _KEYPERSON, rlocale=self.rlocale)
                alpha_nav = alphabet_navigation(index_list, self.rlocale)
                if alpha_nav is not None:
                    surnamelist += alpha_nav

            if order_by == self.ORDER_BY_COUNT:
                table_id = 'SortByCount'
            else:
                table_id = 'SortByName'

            # begin surnamelist table and table head
            with Html("table", class_="infolist primobjlist surnamelist",
                      id=table_id) as table:
                surnamelist += table

                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                trow += Html("th", self._("Letter"), class_="ColumnLetter",
                             inline=True)

                # create table header surname hyperlink
                fname = self.report.surname_fname + self.ext
                tcell = Html("th", class_="ColumnSurname", inline=True)
                trow += tcell
                hyper = Html("a", self._("Surname"),
                             href=fname, title=self._("Surnames"))
                tcell += hyper

                # create table header number of people hyperlink
                fname = "surnames_count" + self.ext
                tcell = Html("th", class_="ColumnQuantity", inline=True)
                trow += tcell
                num_people = self._("Number of People")
                hyper = Html("a", num_people, href=fname, title=num_people)
                tcell += hyper

                name_format = self.report.options['name_format']
                # begin table body
                with Html("tbody") as tbody:
                    table += tbody

                    ppl_handle_list = sort_people(self.r_db, ppl_handle_list,
                                                  self.rlocale)
                    if order_by == self.ORDER_BY_COUNT:
                        temp_list = {}
                        for (surname, data_list) in ppl_handle_list:
                            index_val = "%90d_%s" % (999999999-len(data_list),
                                                     surname)
                            temp_list[index_val] = (surname, data_list)

                        lkey = self.rlocale.sort_key
                        ppl_handle_list = (temp_list[key]
                                           for key in sorted(temp_list,
                                                             key=lkey))

                    first = True
                    first_surname = True

                    for (surname, data_list) in ppl_handle_list:

                        if surname and not surname.isspace():
                            letter = first_letter(surname)
                            if order_by == self.ORDER_BY_NAME:
                                # There will only be an alphabetic index list if
                                # the ORDER_BY_NAME page is being generated
                                letter = get_index_letter(letter, index_list,
                                                          self.rlocale)
                        else:
                            letter = '&nbsp;'
                            surname = self._("<absent>")

                        trow = Html("tr")
                        tbody += trow

                        tcell = Html("td", class_="ColumnLetter", inline=True)
                        trow += tcell

                        if first or primary_difference(letter, prev_letter,
                                                       self.rlocale):
                            first = False
                            prev_letter = letter
                            trow.attr = 'class = "BeginLetter"'
                            ttle = self._("Surnames beginning with "
                                          "letter %s") % letter
                            hyper = Html("a", letter, name=letter,
                                         title=ttle, inline=True)
                            tcell += hyper
                        elif first_surname or surname != prev_surname:
                            first_surname = False
                            tcell += "&nbsp;"
                            prev_surname = surname

                        # In case the user choose a format name like "*SURNAME*"
                        # We must display this field in upper case. So we use
                        # the english format of format_name to find if this is
                        # the case.
                        # name_format = self.report.options['name_format']
                        nme_format = _nd.name_formats[name_format][1]
                        if "SURNAME" in nme_format:
                            surnamed = surname.upper()
                        else:
                            surnamed = surname
                        trow += Html("td",
                                     self.surname_link(name_to_md5(surname),
                                                       surnamed),
                                     class_="ColumnSurname", inline=True)

                        trow += Html("td", len(data_list),
                                     class_="ColumnQuantity", inline=True)

        # create footer section
        # add clearline for proper styling
        footer = self.write_footer(None)
        outerwrapper += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(surnamelistpage,
                          output_file, sio, 0) # 0 => current date modification

    def surname_link(self, fname, name, opt_val=None, uplink=False):
        """
        Create a link to the surname page.

        @param: fname   -- Path to the file name
        @param: name    -- Name to see in the link
        @param: opt_val -- Option value to use
        @param: uplink  -- If True, then "../../../" is inserted in front of
                           the result.
        """
        url = self.report.build_url_fname_html(fname, "srn", uplink)
        hyper = Html("a", html_escape(name), href=url,
                     title=name, inline=True)
        if opt_val is not None:
            hyper += opt_val

        # return hyperlink to its caller
        return hyper
