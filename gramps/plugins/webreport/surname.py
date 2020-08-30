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
    SurnamePage - creates list of individuals with same surname
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
from gramps.gen.display.name import displayer as _nd
from gramps.gen.plug.report import utils
from gramps.plugins.lib.libhtml import Html

#------------------------------------------------
# specific narrative web import
#------------------------------------------------
from gramps.plugins.webreport.basepage import BasePage
from gramps.plugins.webreport.common import (name_to_md5,
                                             _find_birth_date, _find_death_date,
                                             FULLCLEAR, html_escape)

_ = glocale.translation.sgettext
LOG = logging.getLogger(".NarrativeWeb")
getcontext().prec = 8

#################################################
#
#    create the page from SurnameListPage
#
#################################################
class SurnamePage(BasePage):
    """
    This will create a list of individuals with the same surname
    """
    def __init__(self, report, the_lang, the_title, surname, ppl_handle_list):
        """
        @param: report          -- The instance of the main report class for
                                   this report
        @param: the_lang        -- The lang to process
        @param: the_title       -- The title page related to the language
        @param: surname         -- The surname to use
        @param: ppl_handle_list -- The list of people for whom we need to create
                                   a page.
        """
        BasePage.__init__(self, report, the_lang, the_title)

        # module variables
        showbirth = report.options['showbirth']
        showdeath = report.options['showdeath']
        showpartner = report.options['showpartner']
        showparents = report.options['showparents']

        if surname == '':
            surname = self._("<absent>")

        output_file, sio = self.report.create_file(name_to_md5(surname), "srn")
        self.uplink = True
        result = self.write_header("%s - %s" % (self._("Surname"), surname))
        surnamepage, dummy_head, dummy_body, outerwrapper = result
        ldatec = 0

        # begin SurnameDetail division
        with Html("div", class_="content", id="SurnameDetail") as surnamedetail:
            outerwrapper += surnamedetail

            # section title
            # In case the user choose a format name like "*SURNAME*"
            # We must display this field in upper case. So we use
            # the english format of format_name to find if this is
            # the case.
            name_format = self.report.options['name_format']
            nme_format = _nd.name_formats[name_format][1]
            if "SURNAME" in nme_format:
                surnamed = surname.upper()
            else:
                surnamed = surname
            surnamedetail += Html("h3", html_escape(surnamed), inline=True)

            # feature request 2356: avoid genitive form
            msg = self._("This page contains an index of all the individuals "
                         "in the database with the surname of %s. "
                         "Selecting the person&#8217;s name "
                         "will take you to that person&#8217;s "
                         "individual page.") % html_escape(surname)
            surnamedetail += Html("p", msg, id="description")

            # begin surname table and thead
            with Html("table", class_="infolist primobjlist surname") as table:
                surnamedetail += table
                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                # Name Column
                trow += Html("th", self._("Name"), class_="ColumnName",
                             inline=True)

                if showbirth:
                    trow += Html("th", self._("Birth"), class_="ColumnDate",
                                 inline=True)

                if showdeath:
                    trow += Html("th", self._("Death"), class_="ColumnDate",
                                 inline=True)

                if showpartner:
                    trow += Html("th", self._("Partner"),
                                 class_="ColumnPartner",
                                 inline=True)

                if showparents:
                    trow += Html("th", self._("Parents"),
                                 class_="ColumnParents",
                                 inline=True)

                # begin table body
                tbody = Html("tbody")
                table += tbody

                for person_handle in sorted(ppl_handle_list,
                                            key=self.sort_on_given_and_birth):

                    person = self.r_db.get_person_from_handle(person_handle)
                    if person.get_change_time() > ldatec:
                        ldatec = person.get_change_time()
                    trow = Html("tr")
                    tbody += trow

                    # firstname column
                    link = self.new_person_link(person_handle, uplink=True,
                                                person=person)
                    trow += Html("td", link, class_="ColumnName")

                    # birth column
                    if showbirth:
                        tcell = Html("td", class_="ColumnBirth", inline=True)
                        trow += tcell

                        birth_date = _find_birth_date(self.r_db, person)
                        if birth_date is not None:
                            if birth_date.fallback:
                                tcell += Html('em',
                                              self.rlocale.get_date(birth_date),
                                              inline=True)
                            else:
                                tcell += self.rlocale.get_date(birth_date)
                        else:
                            tcell += "&nbsp;"

                    # death column
                    if showdeath:
                        tcell = Html("td", class_="ColumnDeath", inline=True)
                        trow += tcell

                        death_date = _find_death_date(self.r_db, person)
                        if death_date is not None:
                            if death_date.fallback:
                                tcell += Html('em',
                                              self.rlocale.get_date(death_date),
                                              inline=True)
                            else:
                                tcell += self.rlocale.get_date(death_date)
                        else:
                            tcell += "&nbsp;"

                    # partner column
                    if showpartner:
                        tcell = Html("td", class_="ColumnPartner")
                        trow += tcell
                        family_list = person.get_family_handle_list()
                        if family_list:
                            fam_count = 0
                            for family_handle in family_list:
                                fam_count += 1
                                family = self.r_db.get_family_from_handle(
                                    family_handle)
                                partner_handle = utils.find_spouse(
                                    person, family)
                                if partner_handle:
                                    link = self.new_person_link(partner_handle,
                                                                uplink=True)
                                    if fam_count < len(family_list):
                                        if isinstance(link, Html):
                                            link.inside += ","
                                        else:
                                            link += ','
                                    tcell += link
                        else:
                            tcell += "&nbsp;"

                    # parents column
                    if showparents:
                        parent_hdl_list = person.get_parent_family_handle_list()
                        if parent_hdl_list:
                            parent_hdl = parent_hdl_list[0]
                            fam = self.r_db.get_family_from_handle(parent_hdl)
                            f_id = fam.get_father_handle()
                            m_id = fam.get_mother_handle()
                            mother = father = None
                            if f_id:
                                father = self.r_db.get_person_from_handle(f_id)
                                if father:
                                    father_name = self.get_name(father)
                            if m_id:
                                mother = self.r_db.get_person_from_handle(m_id)
                                if mother:
                                    mother_name = self.get_name(mother)
                            if mother and father:
                                tcell = Html("span", father_name,
                                             class_="father fatherNmother")
                                tcell += Html("span", mother_name,
                                              class_="mother")
                            elif mother:
                                tcell = Html("span", mother_name,
                                             class_="mother", inline=True)
                            elif father:
                                tcell = Html("span", father_name,
                                             class_="father", inline=True)
                            samerow = False
                        else:
                            tcell = "&nbsp;"
                            samerow = True
                        trow += Html("td", tcell,
                                     class_="ColumnParents", inline=samerow)

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        outerwrapper += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(surnamepage, output_file, sio, ldatec)
