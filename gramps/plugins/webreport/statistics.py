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
    StatisticsPage
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
from gramps.gen.lib import Person, Family, Event, Place, Source, Citation, Repository
from gramps.gen.plug.report import Bibliography
from gramps.gen.utils.file import media_path_full
from gramps.plugins.lib.libhtml import Html

# ------------------------------------------------
# specific narrative web import
# ------------------------------------------------
from gramps.plugins.webreport.basepage import BasePage
from gramps.plugins.webreport.common import FULLCLEAR

LOG = logging.getLogger(".NarrativeWeb")
getcontext().prec = 8
_ = glocale.translation.sgettext


class StatisticsPage(BasePage):
    """
    Create one page for statistics
    """

    def __init__(self, report, the_lang, the_title, step):
        """
        @param: report        -- The instance of the main report class
                                 for this report
        @param: the_lang      -- The lang to process
        @param: the_title     -- The title page related to the language
        @param: step          -- Use to continue the progess bar
        """
        import os

        BasePage.__init__(self, report, the_lang, the_title)
        self.bibli = Bibliography()
        self.uplink = False
        self.report = report
        # set the file name and open file
        output_file, sio = self.report.create_file("statistics")
        result = self.write_header(_("Statistics"))
        addressbookpage, dummy_head, dummy_body, outerwrapper = result
        (males, females, others, unknown) = self.get_gender(
            report.database.iter_person_handles()
        )

        step()
        mobjects = report.database.get_number_of_media()
        npersons = report.database.get_number_of_people()
        nfamilies = report.database.get_number_of_families()
        nsurnames = len(set(report.database.surname_list))
        notfound = []
        total_media = 0
        mbytes = "0"
        chars = 0
        for media in report.database.iter_media():
            total_media += 1
            fullname = media_path_full(report.database, media.get_path())
            try:
                chars += os.path.getsize(fullname)
                length = len(str(chars))
                if chars <= 999999:
                    mbytes = self._("less than 1")
                else:
                    mbytes = str(chars)[: (length - 6)]
            except OSError:
                notfound.append(media.get_path())

        with Html("div", class_="content", id="EventDetail") as section:
            section += Html("h3", self._("Database overview"), inline=True)
        outerwrapper += section
        with Html("div", class_="content", id="subsection narrative") as sec11:
            sec11 += Html("h4", self._("Individuals"), inline=True)
        outerwrapper += sec11
        with Html("div", class_="content", id="subsection narrative") as sec1:
            sec1 += Html(
                "br",
                self._("Number of individuals") + self.colon + "%d" % npersons,
                inline=True,
            )
            sec1 += Html("br", self._("Males") + self.colon + "%d" % males, inline=True)
            sec1 += Html(
                "br", self._("Females") + self.colon + "%d" % females, inline=True
            )
            sec1 += Html(
                "br",
                self._("Individuals with other gender") + self.colon + "%d" % others,
                inline=True,
            )
            sec1 += Html(
                "br",
                self._("Individuals with unknown gender") + self.colon + "%d" % unknown,
                inline=True,
            )
        outerwrapper += sec1
        with Html("div", class_="content", id="subsection narrative") as sec2:
            sec2 += Html("h4", self._("Family Information"), inline=True)
            sec2 += Html(
                "br",
                self._("Number of families") + self.colon + "%d" % nfamilies,
                inline=True,
            )
            sec2 += Html(
                "br",
                self._("Unique surnames") + self.colon + "%d" % nsurnames,
                inline=True,
            )
        outerwrapper += sec2
        with Html("div", class_="content", id="subsection narrative") as sec3:
            sec3 += Html("h4", self._("Media Objects"), inline=True)
            sec3 += Html(
                "br",
                self._("Total number of media object references")
                + self.colon
                + "%d" % total_media,
                inline=True,
            )
            sec3 += Html(
                "br",
                self._("Number of unique media objects") + self.colon + "%d" % mobjects,
                inline=True,
            )
            sec3 += Html(
                "br",
                self._("Total size of media objects")
                + self.colon
                + "%8s %s" % (mbytes, self._("MB", "Megabyte")),
                inline=True,
            )
            sec3 += Html(
                "br",
                self._("Missing Media Objects") + self.colon + "%d" % len(notfound),
                inline=True,
            )
        outerwrapper += sec3
        with Html("div", class_="content", id="subsection narrative") as sec4:
            sec4 += Html("h4", self._("Miscellaneous"), inline=True)
            sec4 += Html(
                "br",
                self._("Number of events")
                + self.colon
                + "%d" % report.database.get_number_of_events(),
                inline=True,
            )
            sec4 += Html(
                "br",
                self._("Number of places")
                + self.colon
                + "%d" % report.database.get_number_of_places(),
                inline=True,
            )
            nsources = report.database.get_number_of_sources()
            sec4 += Html(
                "br",
                self._("Number of sources") + self.colon + "%d" % nsources,
                inline=True,
            )
            ncitations = report.database.get_number_of_citations()
            sec4 += Html(
                "br",
                self._("Number of citations") + self.colon + "%d" % ncitations,
                inline=True,
            )
            nrepo = report.database.get_number_of_repositories()
            sec4 += Html(
                "br",
                self._("Number of repositories") + self.colon + "%d" % nrepo,
                inline=True,
            )
        outerwrapper += sec4

        (males, females, others, unknown) = self.get_gender(
            self.report.bkref_dict[Person].keys()
        )

        origin = " :<br/>" + report.filter.get_name(self.rlocale)
        with Html("div", class_="content", id="EventDetail") as section:
            section += Html(
                "h3", self._("Narrative web content report for") + origin, inline=True
            )
        outerwrapper += section
        with Html("div", class_="content", id="subsection narrative") as sec5:
            sec5 += Html("h4", self._("Individuals"), inline=True)
            sec5 += Html(
                "br",
                self._("Number of individuals")
                + self.colon
                + "%d" % len(self.report.bkref_dict[Person]),
                inline=True,
            )
            sec5 += Html("br", self._("Males") + self.colon + "%d" % males, inline=True)
            sec5 += Html(
                "br", self._("Females") + self.colon + "%d" % females, inline=True
            )
            sec5 += Html(
                "br",
                self._("Individuals with other gender") + self.colon + "%d" % others,
                inline=True,
            )
            sec5 += Html(
                "br",
                self._("Individuals with unknown gender") + self.colon + "%d" % unknown,
                inline=True,
            )
        outerwrapper += sec5
        with Html("div", class_="content", id="subsection narrative") as sec6:
            sec6 += Html("h4", self._("Family Information"), inline=True)
            sec6 += Html(
                "br",
                self._("Number of families")
                + self.colon
                + "%d" % len(self.report.bkref_dict[Family]),
                inline=True,
            )
        outerwrapper += sec6
        with Html("div", class_="content", id="subsection narrative") as sec7:
            sec7 += Html("h4", self._("Miscellaneous"), inline=True)
            sec7 += Html(
                "br",
                self._("Number of events")
                + self.colon
                + "%d" % len(self.report.bkref_dict[Event]),
                inline=True,
            )
            sec7 += Html(
                "br",
                self._("Number of places")
                + self.colon
                + "%d" % len(self.report.bkref_dict[Place]),
                inline=True,
            )
            sec7 += Html(
                "br",
                self._("Number of sources")
                + self.colon
                + "%d" % len(self.report.bkref_dict[Source]),
                inline=True,
            )
            sec7 += Html(
                "br",
                self._("Number of citations")
                + self.colon
                + "%d" % len(self.report.bkref_dict[Citation]),
                inline=True,
            )
            sec7 += Html(
                "br",
                self._("Number of repositories")
                + self.colon
                + "%d" % len(self.report.bkref_dict[Repository]),
                inline=True,
            )
        outerwrapper += sec7

        # add fullclear for proper styling
        # and footer section to page
        footer = self.write_footer(None)
        outerwrapper += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(addressbookpage, output_file, sio, 0)

    def get_gender(self, person_list):
        """
        This function return the number of males, females, others and unknown
        gender from a person list.

        @param: person_list -- The list to process
        """
        males = 0
        females = 0
        others = 0
        unknown = 0
        for person_handle in person_list:
            person = self.report.database.get_person_from_handle(person_handle)
            gender = person.get_gender()
            if gender == Person.MALE:
                males += 1
            elif gender == Person.FEMALE:
                females += 1
            elif gender == Person.OTHER:
                others += 1
            else:
                unknown += 1
        return (males, females, others, unknown)
