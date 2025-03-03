# -*- coding: utf-8 -*-
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
    FamilyPage - Family index page and individual Family pages
"""
# ------------------------------------------------
# python modules
# ------------------------------------------------
from collections import defaultdict, OrderedDict
from decimal import getcontext
import unicodedata
import logging

# ------------------------------------------------
# Gramps module
# ------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import EventType, Family, Name
from gramps.gen.plug.report import Bibliography
from gramps.plugins.lib.libhtml import Html

# ------------------------------------------------
# specific narrative web import
# ------------------------------------------------
from gramps.plugins.webreport.basepage import BasePage
from gramps.gen.display.name import displayer as _nd
from gramps.plugins.webreport.common import (
    alphabet_navigation,
    partial_navigation,
    create_indexes_pages,
    html_escape,
    FULLCLEAR,
    AlphabeticIndex,
    get_surname_from_person,
)

_ = glocale.translation.sgettext
LOG = logging.getLogger(".NarrativeWeb")
getcontext().prec = 8


#################################################
#
#    creates the Family List Page and Family Pages
#
#################################################
class FamilyPages(BasePage):
    """
    This class is responsible for displaying information about the 'Family'
    database objects. It displays this information under the 'Families'
    tab. It is told by the 'add_instances' call which 'Family's to display,
    and remembers the list of Family. A single call to 'display_pages'
    displays both the Family List (Index) page and all the Family
    pages.

    The base class 'BasePage' is initialised once for each page that is
    displayed.
    """

    def __init__(self, report, the_lang, the_title):
        """
        @param: report    -- The instance of the main report class
                             for this report
        @param: the_lang  -- The lang to process
        @param: the_title -- The title page related to the language
        """
        BasePage.__init__(self, report, the_lang, the_title)
        self.family_dict = defaultdict(set)
        self.familymappages = None

    def display_pages(self, the_lang, the_title):
        """
        Generate and output the pages under the Family tab, namely the family
        index and the individual family pages.

        @param: the_lang  -- The lang to process
        @param: the_title -- The title page related to the language
        """
        LOG.debug("obj_dict[Family]")
        for item in self.report.obj_dict[Family].items():
            LOG.debug("    %s", str(item))

        message = _("Creating family pages...")
        index = 1
        progress_title = self.report.pgrs_title(the_lang)
        with self.r_user.progress(
            progress_title, message, len(self.report.obj_dict[Family]) + 1
        ) as step:
            for family_handle in self.report.obj_dict[Family]:
                step()
                index += 1
                self.familypage(self.report, the_lang, the_title, family_handle)
            step()
            self.familylistpage(
                self.report, the_lang, the_title, self.report.obj_dict[Family].keys()
            )

    def __output_family(
        self,
        ldatec,
        family_handle,
        person_handle,
        tbody,
        letter,
        first_person,
        first_family,
    ):
        """
        Generate and output the data for a single family

        @param: ldatec          -- Last change date and time (updated)
        @param: family_handle   -- The family_handle to be output
        @param: person_handle   -- The person_handle to be output
        @param: tbody           -- The current HTML body into which the data is
                                   assembled
        @param: letter          -- The AlphabeticIndex bucket for this event
        @param: first_person    -- Whether this is the first person for this
                                   letter
        @param: first_family    -- Whether this is the first family of this
                                   person

        @returns: Returns a tuple of updated (ldatec, first_person,
                                              first_family)
        @rtype: tuple
        """
        family = self.r_db.get_family_from_handle(family_handle)
        if family.get_change_time() > ldatec:
            ldatec = family.get_change_time()

        trow = Html("tr")
        tbody += trow
        tcell = Html("td", class_="ColumnRowLabel")
        trow += tcell
        if first_person:
            first_person = False
            first_family = False
            # Update the ColumnRowLabel cell
            trow.attr = 'class="BeginLetter BeginFamily"'
            ttle = self._("Families beginning with " "letter ")
            tcell += Html("a", letter, name=letter, title=ttle + letter)
            #  and create the populated ColumnPartner for the person
            tcell = Html("td", class_="ColumnPartner")
            tcell += self.new_person_link(person_handle, uplink=self.uplink)
            trow += tcell
        elif first_family:
            first_family = False
            # Update the ColumnRowLabel cell
            trow.attr = 'class ="BeginFamily"'
            #  and create the populated ColumnPartner for the person
            tcell = Html("td", class_="ColumnPartner")
            tcell += self.new_person_link(person_handle, uplink=self.uplink)
            trow += tcell
        else:
            # Create the blank ColumnPartner row for the person
            tcell = Html("td", class_="ColumnPartner")
            tcell += "&nbsp;"
            trow += tcell

        tcell = Html("td", class_="ColumnPartner")
        trow += tcell
        tcell += self.family_link(
            family.get_handle(),
            self.report.get_family_name(family),
            family.get_gramps_id(),
            self.uplink,
        )
        # family events; such as marriage and divorce
        # events
        fam_evt_ref_list = family.get_event_ref_list()
        tcell1 = Html("td", class_="ColumnDate", inline=True)
        tcell2 = Html("td", class_="ColumnDate", inline=True)
        trow += tcell1, tcell2
        if fam_evt_ref_list:
            fam_evt_srt_ref_list = sorted(fam_evt_ref_list, key=self.sort_on_grampsid)
            for evt_ref in fam_evt_srt_ref_list:
                evt = self.r_db.get_event_from_handle(evt_ref.ref)
                if evt:
                    evt_type = evt.get_type()
                    if evt_type in [EventType.MARRIAGE, EventType.DIVORCE]:
                        cell = self.rlocale.get_date(evt.get_date_object())
                        if evt_type == EventType.MARRIAGE:
                            tcell1 += cell
                        else:
                            tcell1 += "&nbsp;"
                        if evt_type == EventType.DIVORCE:
                            tcell2 += cell
                        else:
                            tcell2 += "&nbsp;"

        else:
            tcell1 += "&nbsp;"
            tcell2 += "&nbsp;"
        first_family = False
        return (ldatec, first_person, first_family)

    def part_familylistpage(
        self,
        report,
        index_list,
        name,
        letter,
        family_handle_list,
        part=None,
        subp=None,
        partial_list=None,
    ):
        """
        Create a partial family index
        """
        nav_name = part_name = name
        if part != 0 and subp != 0:
            part_name += str(part)
            nav_name = part_name
        if subp and subp != 0:
            part_name += subp
        output_file, sio = self.report.create_file(part_name)
        result = self.write_header(self._("Families"))
        familieslistpage, dummy_head, dummy_body, outerwrapper = result
        ldatec = 0

        # begin Family Division
        with Html("div", class_="content", id="Relationships") as relationlist:
            outerwrapper += relationlist

            # Families list page message
            msg = self._(
                "This page contains an index of all the "
                "families/ relationships in the "
                "database, sorted by their family name/ surname. "
                "Clicking on a person&#8217;s "
                "name will take you to their "
                "family/ relationship&#8217;s page."
            )
            relationlist += Html("p", msg, id="description")

            # Output the navigation
            # add alphabet navigation
            alpha_nav = alphabet_navigation(
                index_list,
                self.rlocale,
                current=part_name,
                rtl=self.dir,
                new_page="families",
                ext=self.ext,
            )
            if alpha_nav:
                relationlist += alpha_nav

            if part is not None:
                # We need to create a new navigation tab for partial page index.
                partial_nav = partial_navigation(
                    partial_list,
                    self.rlocale,
                    current=part_name,
                    rtl=self.dir,
                    ext=self.ext,
                    new_page=nav_name,
                )
                if partial_nav is not None:
                    relationlist += Html(
                        "div", style="clear: both;"
                    )  # This to align the next div to the left.
                    relationlist += partial_nav

            # begin families table and table head
            with Html("table", class_="infolist relationships " + self.dir) as table:
                relationlist += table

                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                # set up page columns
                trow.extend(
                    Html("th", trans, class_=colclass, inline=True)
                    for trans, colclass in [
                        (self._("Letter"), "ColumnRowLabel"),
                        (self._("Person"), "ColumnPartner"),
                        (self._("Family"), "ColumnPartner"),
                        (self._("Marriage"), "ColumnDate"),
                        (self._("Divorce"), "ColumnDate"),
                    ]
                )

                tbody = Html("tbody")
                table += tbody

                first_person = True
                # family_handle_list = family_handle_list[0][1]
                for person_handle, surname in family_handle_list:
                    person = self.r_db.get_person_from_handle(person_handle)
                    if person:
                        family_list = person.get_family_handle_list()
                        first_family = True
                        for family_handle in family_list:
                            (
                                ldatec,
                                first_person,
                                first_family,
                            ) = self.__output_family(
                                ldatec,
                                family_handle,
                                person_handle,
                                tbody,
                                letter,
                                first_person,
                                first_family,
                            )

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        outerwrapper += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(familieslistpage, output_file, sio, ldatec)

    def familylistpage(self, report, the_lang, the_title, fam_list):
        """
        Create a family index

        @param: report    -- The instance of the main report class for
                             this report
        @param: the_lang  -- The lang to process
        @param: the_title -- The title page related to the language
        @param: fam_list  -- The handle for the place to add
        """
        BasePage.__init__(self, report, the_lang, the_title)
        ldatec = 0

        pers_fam_dict = defaultdict(list)
        for family_handle in fam_list:
            family = self.r_db.get_family_from_handle(family_handle)
            if family:
                if family.get_change_time() > ldatec:
                    ldatec = family.get_change_time()
                husband_handle = family.get_father_handle()
                spouse_handle = family.get_mother_handle()
                if husband_handle:
                    pers_fam_dict[husband_handle].append(family)
                if spouse_handle:
                    pers_fam_dict[spouse_handle].append(family)

        # Assemble all the people, we no longer care about their families
        index = AlphabeticIndex(self.rlocale)
        for person_handle, dummy_family in pers_fam_dict.items():
            person = self.r_db.get_person_from_handle(person_handle)
            surname = get_surname_from_person(self.r_db, person)
            index.addRecord(surname, person_handle)

        # Extract the buckets from the index
        index_list = []
        index.resetBucketIterator()
        # for each bucket, output the people and their families in that
        # bucket
        surname_ppl_handle_dict = OrderedDict()
        while index.nextBucket():
            if index.bucketRecordCount != 0:
                letter = index.bucketLabel
                # Assemble a dict of all the people in this bucket.
                bletter = (
                    unicodedata.normalize("NFKD", letter)[0]
                    if len(letter) > 0
                    else letter
                )
                while index.nextRecord():
                    # The records are returned sorted by recordName,
                    # which is surname. we need to retain that order but
                    # in addition sort by the rest of the name
                    person_surname = index.recordName
                    person_handle = index.recordData
                    if person_surname in surname_ppl_handle_dict.keys():
                        surname_ppl_handle_dict[person_surname].append(person_handle)
                    else:
                        surname_ppl_handle_dict[person_surname] = [person_handle]
        # sort by surname
        surname_handle_list = surname_ppl_handle_dict
        extended_handle_list = defaultdict(list)
        name_format = self.report.options["name_format"]
        max_letter_rows = defaultdict(int)
        index_list = []
        for bletter, hdlel in surname_handle_list.items():
            bletter = (
                unicodedata.normalize("NFKD", bletter)[0]
                if len(bletter) > 0
                else bletter
            )
            bletter = bletter[0] if len(bletter) > 0 else bletter
            bletter = bletter.upper() if bletter.isalpha() else "…"
            if bletter not in index_list:
                index_list.append(bletter)
            max_letter_rows[bletter] = len(hdlel)
            for hdle in hdlel:
                person = self.r_db.get_person_from_handle(hdle)
                primary_name = person.get_primary_name()
                nname = Name(primary_name)
                nname.set_display_as(name_format)
                fname = _nd.display_name(nname)
                extended_handle_list[bletter].append((hdle, fname))
        extended_handle_list = list(extended_handle_list.items())
        create_indexes_pages(
            report,
            "families",
            index_list,
            self.part_familylistpage,
            extended_handle_list,
            locale=self.rlocale,
        )

    def familypage(self, report, the_lang, the_title, family_handle):
        """
        Create a family page

        @param: report        -- The instance of the main report class for
                                 this report
        @param: the_lang      -- The lang to process
        @param: the_title     -- The title page related to the language
        @param: family_handle -- The handle for the family to add
        """
        family = report.database.get_family_from_handle(family_handle)
        if not family:
            return
        BasePage.__init__(self, report, the_lang, the_title, family.get_gramps_id())
        ldatec = family.get_change_time()

        self.bibli = Bibliography()
        self.uplink = True
        family_name = self.report.get_family_name(family)
        self.page_title = family_name

        self.familymappages = report.options["familymappages"]

        output_file, sio = self.report.create_file(family.get_handle(), "fam")
        result = self.write_header(family_name)
        familydetailpage, head, dummy_body, outerwrapper = result

        # begin FamilyDetaill division
        with Html(
            "div", class_="content", id="RelationshipDetail"
        ) as relationshipdetail:
            outerwrapper += relationshipdetail

            # family media list for initial thumbnail
            if self.create_media:
                media_list = family.get_media_list()
                if media_list:
                    if self.the_lang and not self.usecms:
                        fname = "/".join(["..", "css", "lightbox.css"])
                        jsname = "/".join(["..", "css", "lightbox.js"])
                    else:
                        fname = "/".join(["css", "lightbox.css"])
                        jsname = "/".join(["css", "lightbox.js"])
                    url = self.report.build_url_fname(fname, None, self.uplink)
                    head += Html(
                        "link",
                        href=url,
                        type="text/css",
                        media="screen",
                        rel="stylesheet",
                    )
                    url = self.report.build_url_fname(jsname, None, self.uplink)
                    head += Html("script", src=url, type="text/javascript", inline=True)
                # If Event pages are not being created, then we need to display
                # the family event media here
                if not self.inc_events:
                    for evt_ref in family.get_event_ref_list():
                        event = self.r_db.get_event_from_handle(evt_ref.ref)
                        media_list += event.get_media_list()

            relationshipdetail += Html("h2", self.page_title, inline=True) + (
                Html("sup")
                + (Html("small") + self.get_citation_links(family.get_citation_list()))
            )
            # Tags
            tags = self.show_tags(family)
            if tags and self.report.inc_tags:
                trow = Html("table", class_="tags") + (
                    Html("tr")
                    + (
                        Html(
                            "td",
                            self._("Tags") + self._(":"),
                            class_="ColumnAttribute",
                            inline=True,
                        ),
                        Html("td", tags, class_="ColumnValue", inline=True),
                    )
                )
                relationshipdetail += trow

            # display relationships
            families = self.display_family_relationships(family, None)
            if families is not None:
                relationshipdetail += families

            # display additional images as gallery
            if self.create_media:
                addgallery = self.disp_add_img_as_gallery(media_list, family)
                if addgallery:
                    relationshipdetail += addgallery

            # Narrative subsection
            notelist = family.get_note_list()
            if notelist:
                relationshipdetail += self.display_note_list(notelist, Family)

            # display family LDS ordinance...
            family_lds_ordinance_list = family.get_lds_ord_list()
            if family_lds_ordinance_list:
                relationshipdetail += self.display_lds_ordinance(family)

            # get attribute list
            attrlist = family.get_attribute_list()
            if attrlist:
                attrsection, attrtable = self.display_attribute_header()
                self.display_attr_list(attrlist, attrtable)
                relationshipdetail += attrsection

            # for use in family map pages...
            if self.report.options["familymappages"]:
                name_format = self.report.options["name_format"]
                father = mother = None
                with self.create_toggle("map") as h4_head:
                    relationshipdetail += h4_head
                    h4_head += self._("Family Map")
                    disp = "none" if self.report.options["toggle"] else "block"
                    with Html(
                        "div", style="display:%s" % disp, id="toggle_map"
                    ) as toggle:
                        relationshipdetail += toggle
                        mapdetail = Html("br")
                        fhdle = family.get_father_handle()
                        for handle, dummy_url in self.report.fam_link.items():
                            if fhdle == handle:
                                father = self.r_db.get_person_from_handle(fhdle)
                                break
                        if father:
                            primary_name = father.get_primary_name()
                            name = Name(primary_name)
                            name.set_display_as(name_format)
                            fname = html_escape(_nd.display_name(name))
                            mapdetail += self.family_map_link_for_parent(fhdle, fname)
                        mapdetail += Html("br")
                        mhdle = family.get_mother_handle()
                        for handle, dummy_url in self.report.fam_link.items():
                            if mhdle == handle:
                                mother = self.r_db.get_person_from_handle(mhdle)
                                break
                        if mother:
                            primary_name = mother.get_primary_name()
                            name = Name(primary_name)
                            name.set_display_as(name_format)
                            mname = html_escape(_nd.display_name(name))
                            mapdetail += self.family_map_link_for_parent(mhdle, mname)
                        toggle += mapdetail

            # source references
            srcrefs = self.display_ind_sources(family)
            if srcrefs:
                relationshipdetail += srcrefs

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        outerwrapper += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(familydetailpage, output_file, sio, ldatec)

    def family_map_link_for_parent(self, handle, name):
        """
        Creates a link to the family map for the father or the mother

        @param: handle -- The person handle
        @param: name   -- The name for this person to display
        """
        url = self.report.fam_link[handle]
        title = self._("Family Map for %s") % name
        return Html("a", title, href=url, title=title, class_="family_map", inline=True)
