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
    PersonPage - Person index page and individual `Person pages
"""
#------------------------------------------------
# python modules
#------------------------------------------------
from collections import defaultdict
from operator import itemgetter
from decimal import Decimal, getcontext
import logging

#------------------------------------------------
# Gramps module
#------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import (ChildRefType, Date, Name, Person, EventRoleType,
                            EventType)
from gramps.gen.lib.date import Today
from gramps.gen.plug.report import Bibliography
from gramps.gen.plug.report import utils
from gramps.gen.utils.alive import probably_alive
from gramps.gen.constfunc import win
from gramps.gen.display.name import displayer as _nd
from gramps.gen.utils.db import get_birth_or_fallback, get_death_or_fallback
from gramps.plugins.lib.libhtml import Html
from gramps.gen.utils.place import conv_lat_lon
from gramps.gen.proxy import LivingProxyDb

#------------------------------------------------
# specific narrative web import
#------------------------------------------------
from gramps.plugins.webreport.basepage import BasePage
from gramps.plugins.webreport.common import (get_first_letters, _KEYPERSON,
                                             alphabet_navigation, sort_people,
                                             _NAME_STYLE_FIRST, first_letter,
                                             get_index_letter, add_birthdate,
                                             primary_difference, FULLCLEAR,
                                             _find_birth_date, _find_death_date,
                                             MARKER_PATH, OSM_MARKERS,
                                             GOOGLE_MAPS, MARKERS, html_escape,
                                             DROPMASTERS, FAMILYLINKS)

_ = glocale.translation.sgettext
LOG = logging.getLogger(".NarrativeWeb")
getcontext().prec = 8

_WIDTH = 160
_HEIGHT = 120
_VGAP = 10
_HGAP = 30
_SHADOW = 5
_XOFFSET = 5

#################################################
#
#    creates the Individual List Page and IndividualPages
#
#################################################
class PersonPages(BasePage):
    """
    This class is responsible for displaying information about the 'Person'
    database objects. It displays this information under the 'Individuals'
    tab. It is told by the 'add_instances' call which 'Person's to display,
    and remembers the list of persons. A single call to 'display_pages'
    displays both the Individual List (Index) page and all the Individual
    pages.

    The base class 'BasePage' is initialised once for each page that is
    displayed.
    """
    def __init__(self, report):
        """
        @param: report -- The instance of the main report class for this report
        """
        BasePage.__init__(self, report, title="")
        self.ind_dict = defaultdict(set)
        self.mapservice = None
        self.sort_name = None
        self.googleopts = None
        self.googlemapkey = None
        self.birthorder = None
        self.person = None
        self.familymappages = None
        self.rel_class = None
        self.placemappages = None
        self.name = None

    def display_pages(self, title):
        """
        Generate and output the pages under the Individuals tab, namely the
        individual index and the individual pages.

        @param: title -- Is the title of the web page
        """
        LOG.debug("obj_dict[Person]")
        for item in self.report.obj_dict[Person].items():
            LOG.debug("    %s", str(item))
        message = _('Creating individual pages')
        with self.r_user.progress(_("Narrated Web Site Report"), message,
                                  len(self.report.obj_dict[Person]) + 1
                                 ) as step:
            index = 1
            for person_handle in sorted(self.report.obj_dict[Person]):
                step()
                index += 1
                person = self.r_db.get_person_from_handle(person_handle)
                self.individualpage(self.report, title, person)
            step()
            self.individuallistpage(self.report, title,
                                    self.report.obj_dict[Person].keys())

#################################################
#
#    creates the Individual List Page
#
#################################################
    def individuallistpage(self, report, title, ppl_handle_list):
        """
        Creates an individual page

        @param: report          -- The instance of the main report class
                                   for this report
        @param: title           -- Is the title of the web page
        @param: ppl_handle_list -- The list of people for whom we need
                                   to create a page.
        """
        BasePage.__init__(self, report, title)
        prev_letter = " "

        # plugin variables for this module
        showbirth = report.options['showbirth']
        showdeath = report.options['showdeath']
        showpartner = report.options['showpartner']
        showparents = report.options['showparents']

        output_file, sio = self.report.create_file("individuals")
        indlistpage, head, body = self.write_header(self._("Individuals"))
        date = 0

        # begin Individuals division
        with Html("div", class_="content", id="Individuals") as individuallist:
            body += individuallist

            # Individual List page message
            msg = self._("This page contains an index of all the individuals "
                         "in the database, sorted by their last names. "
                         "Selecting the person&#8217;s "
                         "name will take you to that "
                         "person&#8217;s individual page.")
            individuallist += Html("p", msg, id="description")

            # add alphabet navigation
            index_list = get_first_letters(self.r_db, ppl_handle_list,
                                           _KEYPERSON, rlocale=self.rlocale)
            alpha_nav = alphabet_navigation(index_list, self.rlocale)
            if alpha_nav is not None:
                individuallist += alpha_nav

            # begin table and table head
            with Html("table",
                      class_="infolist primobjlist IndividualList") as table:
                individuallist += table
                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                # show surname and first name
                trow += Html("th", self._("Surname"), class_="ColumnSurname",
                             inline=True)
                trow += Html("th", self._("Given Name"), class_="ColumnName",
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

            tbody = Html("tbody")
            table += tbody

            ppl_handle_list = sort_people(self.r_db, ppl_handle_list,
                                          self.rlocale)
            first = True
            for (surname, handle_list) in ppl_handle_list:

                if surname and not surname.isspace():
                    letter = get_index_letter(first_letter(surname), index_list,
                                              self.rlocale)
                else:
                    letter = '&nbsp'
                    surname = self._("<absent>")

                first_surname = True
                for person_handle in sorted(handle_list,
                                            key=self.sort_on_name_and_grampsid):
                    person = self.r_db.get_person_from_handle(person_handle)
                    if person.get_change_time() > date:
                        date = person.get_change_time()

                    # surname column
                    trow = Html("tr")
                    tbody += trow
                    tcell = Html("td", class_="ColumnSurname", inline=True)
                    trow += tcell

                    if first or primary_difference(letter, prev_letter,
                                                   self.rlocale):
                        first = False
                        first_surname = False
                        prev_letter = letter
                        trow.attr = 'class = "BeginSurname"'
                        ttle = self._("Surnames %(surname)s beginning "
                                      "with letter %(letter)s" %
                                      {'surname' : surname,
                                       'letter' : letter})
                        tcell += Html(
                            "a", html_escape(surname), name=letter,
                            id_=letter,
                            title=ttle)
                    elif first_surname:
                        first_surname = False
                        tcell += Html("a", html_escape(surname),
                                      title=self._("Surnames") + " " + surname)
                    else:
                        tcell += "&nbsp;"

                    # firstname column
                    link = self.new_person_link(person_handle, person=person,
                                                name_style=_NAME_STYLE_FIRST)
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

                        family_list = person.get_family_handle_list()
                        first_family = True
                        #partner_name = None
                        tcell = () # pylint: disable=R0204
                        if family_list:
                            for family_handle in family_list:
                                family = self.r_db.get_family_from_handle(
                                    family_handle)
                                partner_handle = utils.find_spouse(
                                    person, family)
                                if partner_handle:
                                    if not first_family:
                                        # have to do this to get the comma on
                                        # the same line as the link
                                        if isinstance(tcell[-1], Html):
                                            # tcell is an instance of Html (or
                                            # of a subclass thereof)
                                            tcell[-1].inside += ","
                                        else:
                                            tcell = tcell[:-1] + (
                                                # TODO for Arabic, translate?
                                                (tcell[-1] + ", "),)
                                    # Have to manipulate as tuples so that
                                    # subsequent people are not nested
                                    # within the first link
                                    tcell += (
                                        self.new_person_link(partner_handle),)
                                    first_family = False
                        else:
                            tcell = "&nbsp;"
                        trow += Html("td", class_="ColumnPartner") + tcell

                    # parents column
                    if showparents:

                        parent_hdl_list = person.get_parent_family_handle_list()
                        if parent_hdl_list:
                            parent_handle = parent_hdl_list[0]
                            family = self.r_db.get_family_from_handle(
                                parent_handle)
                            father_handle = family.get_father_handle()
                            mother_handle = family.get_mother_handle()
                            if father_handle:
                                father = self.r_db.get_person_from_handle(
                                    father_handle)
                            else:
                                father = None
                            if mother_handle:
                                mother = self.r_db.get_person_from_handle(
                                    mother_handle)
                            else:
                                mother = None
                            if father:
                                father_name = self.get_name(father)
                            if mother:
                                mother_name = self.get_name(mother)
                            samerow = False
                            if mother and father:
                                tcell = (Html("span", father_name,
                                              class_="father fatherNmother",
                                              inline=True),
                                         Html("span", mother_name,
                                              class_="mother", inline=True))
                            elif mother:
                                tcell = Html("span", mother_name,
                                             class_="mother", inline=True)
                            elif father:
                                tcell = Html("span", father_name,
                                             class_="father", inline=True)
                            else:
                                tcell = "&nbsp;"
                                samerow = True
                        else:
                            tcell = "&nbsp;"
                            samerow = True
                        trow += Html("td", class_="ColumnParents",
                                     inline=samerow) + tcell

        # create clear line for proper styling
        # create footer section
        footer = self.write_footer(date)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(indlistpage, output_file, sio, date)

#################################################
#
#    creates an Individual Page
#
#################################################
    gender_map = {
        Person.MALE    : _('male'),
        Person.FEMALE  : _('female'),
        Person.UNKNOWN : _('unknown'),
        }

    def individualpage(self, report, title, person):
        """
        Creates an individual page

        @param: report -- The instance of the main report class for this report
        @param: title  -- Is the title of the web page
        @param: person -- The person to use for this page.
        """
        BasePage.__init__(self, report, title, person.get_gramps_id())
        place_lat_long = []

        self.person = person
        self.bibli = Bibliography()
        self.sort_name = self.get_name(person)
        self.name = self.get_name(person)

        date = self.person.get_change_time()

        # to be used in the Family Map Pages...
        self.familymappages = self.report.options['familymappages']
        self.placemappages = self.report.options['placemappages']
        self.mapservice = self.report.options['mapservice']
        self.googleopts = self.report.options['googleopts']
        self.googlemapkey = self.report.options['googlemapkey']

        # decide if we will sort the birth order of siblings...
        self.birthorder = self.report.options['birthorder']

        # get the Relationship Calculator so that we can determine
        # bio, half, step- siblings for use in display_ind_parents() ...
        self.rel_class = self.report.rel_class

        output_file, sio = self.report.create_file(person.get_handle(), "ppl")
        self.uplink = True
        indivdetpage, head, body = self.write_header(self.sort_name)

        # attach the ancestortree style sheet if ancestor
        # graph is being created?
        if self.report.options["ancestortree"]:
            if self.usecms:
                fname = "/".join([self.target_uri, "css", "ancestortree.css"])
            else:
                fname = "/".join(["css", "ancestortree.css"])
            url = self.report.build_url_fname(fname, None, self.uplink)
            head += Html("link", href=url, type="text/css", media="screen",
                         rel="stylesheet")

        # begin individualdetail division
        with Html("div", class_="content",
                  id='IndividualDetail') as individualdetail:
            body += individualdetail

            # display a person's general data
            thumbnail, name, summary = self.display_ind_general()
            if thumbnail is not None:
                individualdetail += thumbnail
            individualdetail += (name, summary)

            # display a person's events
            sect2 = self.display_ind_events(place_lat_long)
            if sect2 is not None:
                individualdetail += sect2

            # display relationship to the center person
            sect3 = self.display_ind_center_person()
            if sect3 is not None:
                individualdetail += sect3

            # display parents
            sect4 = self.display_ind_parents()
            if sect4 is not None:
                individualdetail += sect4

            # display relationships
            relationships = self.display_relationships(self.person,
                                                       place_lat_long)
            if relationships is not None:
                individualdetail += relationships

            # display LDS ordinance
            sect5 = self.display_lds_ordinance(self.person)
            if sect5 is not None:
                individualdetail += sect5

            # display address(es) and show sources
            sect6 = self.display_addr_list(self.person.get_address_list(), True)
            if sect6 is not None:
                individualdetail += sect6

            photo_list = self.person.get_media_list()
            media_list = photo_list[:]

            # if Family Pages are not being created, then include the Family
            # Media objects? There is no reason to add these objects to the
            # Individual Pages...
            if not self.inc_families:
                for handle in self.person.get_family_handle_list():
                    family = self.r_db.get_family_from_handle(handle)
                    if family:
                        media_list += family.get_media_list()
                        for evt_ref in family.get_event_ref_list():
                            event = self.r_db.get_event_from_handle(evt_ref.ref)
                            media_list += event.get_media_list()

            # if the Event Pages are not being created, then include the Event
            # Media objects? There is no reason to add these objects to the
            # Individual Pages...
            if not self.inc_events:
                for evt_ref in self.person.get_primary_event_ref_list():
                    event = self.r_db.get_event_from_handle(evt_ref.ref)
                    if event:
                        media_list += event.get_media_list()

            # display additional images as gallery
            sect7 = self.disp_add_img_as_gallery(media_list, person)
            if sect7 is not None:
                individualdetail += sect7

            # display Narrative Notes
            notelist = person.get_note_list()
            sect8 = self.display_note_list(notelist)
            if sect8 is not None:
                individualdetail += sect8

            # display attributes
            attrlist = person.get_attribute_list()
            if attrlist:
                attrsection, attrtable = self.display_attribute_header()
                self.display_attr_list(attrlist, attrtable)
                individualdetail += attrsection

            # display web links
            sect10 = self.display_url_list(self.person.get_url_list())
            if sect10 is not None:
                individualdetail += sect10

            # display associations
            assocs = person.get_person_ref_list()
            if assocs:
                individualdetail += self.display_ind_associations(assocs)

            # for use in family map pages...
            if len(place_lat_long) > 0:
                if self.report.options["familymappages"]:
                    # save output_file, string_io and cur_fname
                    # before creating a new page
                    sof = output_file
                    sstring_io = sio
                    sfname = self.report.cur_fname
                    individualdetail += self.__display_family_map(
                        person, place_lat_long)
                    # restore output_file, string_io and cur_fname
                    # after creating a new page
                    output_file = sof
                    sio = sstring_io
                    self.report.cur_fname = sfname

            # display pedigree
            sect13 = self.display_ind_pedigree()
            if sect13 is not None:
                individualdetail += sect13

            # display ancestor tree
            if report.options['ancestortree']:
                sect14 = self.display_tree()
                if sect14 is not None:
                    individualdetail += sect14

            # display source references
            sect14 = self.display_ind_sources(person)
            if sect14 is not None:
                individualdetail += sect14

        # add clearline for proper styling
        # create footer section
        footer = self.write_footer(date)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(indivdetpage, output_file, sio, date)

    def __create_family_map(self, person, place_lat_long):
        """
        creates individual family map page

        @param: person -- person from database
        @param: place_lat_long -- for use in Family Map Pages
        """
        if not place_lat_long:
            return

        output_file, sio = self.report.create_file(person.get_handle(), "maps")
        self.uplink = True
        familymappage, head, body = self.write_header(self._("Family Map"))

        minx, maxx = Decimal("0.00000001"), Decimal("0.00000001")
        miny, maxy = Decimal("0.00000001"), Decimal("0.00000001")
        xwidth, yheight = [], []
        midx_, midy_, spanx, spany = [None]*4

        number_markers = len(place_lat_long)
        if number_markers > 1:
            for (latitude, longitude, placetitle, handle,
                 date, etype) in place_lat_long:
                xwidth.append(latitude)
                yheight.append(longitude)
            xwidth.sort()
            yheight.sort()

            minx = xwidth[0] if xwidth[0] else minx
            maxx = xwidth[-1] if xwidth[-1] else maxx
            minx, maxx = Decimal(minx), Decimal(maxx)
            midx_ = str(Decimal((minx + maxx) /2))

            miny = yheight[0] if yheight[0] else miny
            maxy = yheight[-1] if yheight[-1] else maxy
            miny, maxy = Decimal(miny), Decimal(maxy)
            midy_ = str(Decimal((miny + maxy) /2))

            midx_, midy_ = conv_lat_lon(midx_, midy_, "D.D8")

            # get the integer span of latitude and longitude
            spanx = int(maxx - minx)
            spany = int(maxy - miny)

        # set zoom level based on span of Longitude?
        tinyset = [value for value in (-3, -2, -1, 0, 1, 2, 3)]
        smallset = [value for value in (-4, -5, -6, -7, 4, 5, 6, 7)]
        middleset = [value for value in (-8, -9, -10, -11, 8, 9, 10, 11)]
        largeset = [value for value in (-11, -12, -13, -14, -15, -16,
                                        -17, 11, 12, 13, 14, 15, 16, 17)]

        if spany in tinyset or spany in smallset:
            zoomlevel = 6
        elif spany in middleset:
            zoomlevel = 5
        elif spany in largeset:
            zoomlevel = 4
        else:
            zoomlevel = 3

        # 0 = latitude, 1 = longitude, 2 = place title,
        # 3 = handle, and 4 = date, 5 = event type...
        # being sorted by date, latitude, and longitude...
        place_lat_long = sorted(place_lat_long, key=itemgetter(4, 0, 1))

        # for all plugins
        # if family_detail_page
        # if active
        # call_(report, up, head)

        # add narrative-maps style sheet
        if self.usecms:
            fname = "/".join([self.target_uri, "css", "narrative-maps.css"])
        else:
            fname = "/".join(["css", "narrative-maps.css"])
        url = self.report.build_url_fname(fname, None, self.uplink)
        head += Html("link", href=url, type="text/css", media="screen",
                     rel="stylesheet")

        # add MapService specific javascript code
        if self.mapservice == "Google":
            src_js = GOOGLE_MAPS + "api/js?sensor=false"
            if self.googlemapkey:
                src_js += "&key=" + self.googlemapkey
            head += Html("script", type="text/javascript",
                         src=src_js, inline=True)
        else:
            url = self.secure_mode
            url += ("maxcdn.bootstrapcdn.com/bootstrap/3.3.7/"
                    "css/bootstrap.min.css")
            head += Html("link", href=url, type="text/javascript",
                         rel="stylesheet")
            src_js = self.secure_mode
            src_js += "ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"
            head += Html("script", type="text/javascript",
                         src=src_js, inline=True)
            src_js = self.secure_mode
            src_js += "openlayers.org/en/latest/build/ol.js"
            head += Html("script", type="text/javascript",
                         src=src_js, inline=True)
            url = self.secure_mode
            url += "openlayers.org/en/latest/css/ol.css"
            head += Html("link", href=url, type="text/javascript",
                         rel="stylesheet")
            src_js = self.secure_mode
            src_js += ("maxcdn.bootstrapcdn.com/bootstrap/3.3.7/"
                       "js/bootstrap.min.js")
            head += Html("script", type="text/javascript",
                         src=src_js, inline=True)

        if number_markers > 0:
            tracelife = "["
            seq_ = 1

            for index in range(0, (number_markers - 1)):
                (latitude, longitude, placetitle, handle, date,
                 etype) = place_lat_long[index]

                # are we using Google?
                if self.mapservice == "Google":

                    # are we creating Family Links?
                    if self.googleopts == "FamilyLinks":
                        tracelife += """
    new google.maps.LatLng(%s, %s),""" % (latitude, longitude)

                    # are we creating Drop Markers or Markers?
                    elif self.googleopts in ["Drop", "Markers"]:
                        tracelife += """
    ['%s', %s, %s, %d],""" % (placetitle.replace("'", "\\'"), latitude,
                              longitude, seq_)

                # are we using OpenStreetMap?
                else:
                    tracelife += """
    [%f, %f, \'%s\'],""" % (float(longitude), float(latitude),
                            placetitle.replace("'", "\\'"))

                seq_ += 1
            # FIXME: The last element in the place_lat_long list is treated
            # specially, and the code above is apparently repeated so as to
            # avoid a comma at the end, and get the right closing. This is very
            # ugly.
            (latitude, longitude, placetitle, handle, date,
             etype) = place_lat_long[-1]

            # are we using Google?
            if self.mapservice == "Google":

                # are we creating Family Links?
                if self.googleopts == "FamilyLinks":
                    tracelife += """
    new google.maps.LatLng(%s, %s)
  ];""" % (latitude, longitude)

                # are we creating Drop Markers or Markers?
                elif self.googleopts in ["Drop", "Markers"]:
                    tracelife += """
    ['%s', %s, %s, %d]
  ];""" % (placetitle.replace("'", "\\'"), latitude, longitude, seq_)

            # are we using OpenStreetMap?
            elif self.mapservice == "OpenStreetMap":
                tracelife += """
    [%f, %f, \'%s\']
  ];""" % (float(longitude), float(latitude), placetitle.replace("'", "\\'"))

        # begin MapDetail division...
        with Html("div", class_="content", id="FamilyMapDetail") as mapdetail:
            body += mapdetail

            # add page title
            mapdetail += Html("h3",
                              html_escape(self._("Tracking %s")
                                          % self.get_name(person)),
                              inline=True)

            # page description
            msg = self._("This map page represents that person "
                         "and any descendants with all of their event/ places. "
                         "If you place your mouse over "
                         "the marker it will display the place name. "
                         "The markers and the Reference "
                         "list are sorted in date order (if any?). "
                         "Clicking on a place&#8217;s "
                         "name in the Reference section will take you "
                         "to that place&#8217;s page.")
            mapdetail += Html("p", msg, id="description")

            # this is the style element where the Map is held in the CSS...
            with Html("div", id="map_canvas") as canvas:
                mapdetail += canvas

                # begin javascript inline code...
                with Html("script", deter="deter",
                          style='width =100%; height =100%;',
                          type="text/javascript", indent=False) as jsc:
                    head += jsc

                    # Link to Gramps marker
                    fname = "/".join(['images', 'marker.png'])
                    marker_path = self.report.build_url_image("marker.png",
                                                              "images",
                                                              self.uplink)

                    jsc += MARKER_PATH % marker_path
                    # are we using Google?
                    if self.mapservice == "Google":

                        # are we creating Family Links?
                        if self.googleopts == "FamilyLinks":
                            if midy_ is None:
                                jsc += FAMILYLINKS % (tracelife, latitude,
                                                      longitude, int(10))
                            else:
                                jsc += FAMILYLINKS % (tracelife, midx_, midy_,
                                                      zoomlevel)

                        # are we creating Drop Markers?
                        elif self.googleopts == "Drop":
                            if midy_ is None:
                                jsc += DROPMASTERS % (tracelife, latitude,
                                                      longitude, int(10))
                            else:
                                jsc += DROPMASTERS % (tracelife, midx_, midy_,
                                                      zoomlevel)

                        # we are creating Markers only...
                        else:
                            if midy_ is None:
                                jsc += MARKERS % (tracelife, latitude,
                                                  longitude, int(10))
                            else:
                                jsc += MARKERS % (tracelife, midx_, midy_,
                                                  zoomlevel)

                    # we are using OpenStreetMap...
                    else:
                        if midy_ is None:
                            jsc += OSM_MARKERS % (tracelife,
                                                  longitude,
                                                  latitude, 10)
                        else:
                            jsc += OSM_MARKERS % (tracelife, midy_, midx_,
                                                  zoomlevel)

            # if Google and Drop Markers are selected,
            # then add "Drop Markers" button?
            if self.mapservice == "Google" and self.googleopts == "Drop":
                mapdetail += Html("button", _("Drop Markers"),
                                  id="drop", onclick="drop()", inline=True)

            # add div for popups.
            with Html("div", id="popup", inline=True) as popup:
                mapdetail += popup

            # begin place reference section and its table...
            with Html("div", class_="subsection", id="references") as section:
                mapdetail += section
                section += Html("h4", self._("References"), inline=True)

                with Html("table", class_="infolist") as table:
                    section += table

                    thead = Html("thead")
                    table += thead

                    trow = Html("tr")
                    thead += trow

                    trow.extend(
                        Html("th", label, class_=colclass, inline=True)
                        for (label, colclass) in [
                            (_("Date"), "ColumnDate"),
                            (_("Place Title"), "ColumnPlace"),
                            (_("Event Type"), "ColumnType")
                        ]
                    )

                    tbody = Html("tbody")
                    table += tbody

                    for (latitude, longitude, placetitle, handle, date,
                         etype) in place_lat_long:
                        trow = Html("tr")
                        tbody += trow

                        trow.extend(
                            Html("td", data, class_=colclass, inline=True)
                            for data, colclass in [
                                (date, "ColumnDate"),
                                (self.place_link(handle, placetitle,
                                                 uplink=True),
                                 "ColumnPlace"),
                                (str(etype), "ColumnType")
                            ]
                        )

        # add body id for this page...
        body.attr = 'id ="FamilyMap" onload ="initialize()"'

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(None)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(familymappage, output_file, sio, 0)

    def __display_family_map(self, person, place_lat_long):
        """
        Create the family map link

        @param: person         -- The person to set in the box
        @param: place_lat_long -- The center of the box
        """
        # create family map page
        self.__create_family_map(person, place_lat_long)

        # begin family map division plus section title
        with Html("div", class_="subsection", id="familymap") as familymap:
            familymap += Html("h4", self._("Family Map"), inline=True)

            # add family map link
            person_handle = person.get_handle()
            url = self.report.build_url_fname_html(person_handle, "maps", True)
            familymap += self.family_map_link(person_handle, url)

        # return family map link to its caller
        return familymap

    def draw_box(self, center, col, person):
        """
        Draw the box around the AncestorTree Individual name box...

        @param: center -- The center of the box
        @param: col    -- The generation number
        @param: person -- The person to set in the box
        """
        top = center - _HEIGHT/2
        xoff = _XOFFSET+col*(_WIDTH+_HGAP)
        sex = person.gender
        if sex == Person.MALE:
            divclass = "male"
        elif sex == Person.FEMALE:
            divclass = "female"
        else:
            divclass = "unknown"

        boxbg = Html("div", class_="boxbg %s AncCol%s" % (divclass, col),
                     style="top: %dpx; left: %dpx;" % (top, xoff+1)
                    )

        person_name = self.get_name(person)
        # This does not use [new_]person_link because the requirements are
        # unique
        result = self.report.obj_dict.get(Person).get(person.handle)
        if result is None or result[0] == "":
            # The person is not included in the webreport or there is no link
            # to them
            boxbg += Html("span", person_name, class_="unlinked", inline=True)
        else:
            thumbnail_url = None
            if self.create_media and col < 5:
                photolist = person.get_media_list()
                if photolist:
                    photo_handle = photolist[0].get_reference_handle()
                    photo = self.r_db.get_media_from_handle(photo_handle)
                    mime_type = photo.get_mime_type()
                    if mime_type:
                        region = self.media_ref_region_to_object(photo_handle,
                                                                 person)
                        if region:
                            # make a thumbnail of this region
                            newpath = self.copy_thumbnail(
                                photo_handle, photo, region)
                            # TODO. Check if build_url_fname can be used.
                            newpath = "/".join(['..']*3 + [newpath])
                            if win():
                                newpath = newpath.replace('\\', "/")
                            thumbnail_url = newpath
                        else:
                            (photo_url,
                             thumbnail_url) = self.report.prepare_copy_media(
                                 photo)
                            thumbnail_url = "/".join(['..']*3 + [thumbnail_url])
                            if win():
                                thumbnail_url = thumbnail_url.replace('\\', "/")
            url = self.report.build_url_fname_html(person.handle, "ppl", True)
            birth = death = ""
            bd_event = get_birth_or_fallback(self.r_db, person)
            if bd_event:
                birth = self.rlocale.get_date(bd_event.get_date_object())
            dd_event = get_death_or_fallback(self.r_db, person)
            if dd_event:
                death = self.rlocale.get_date(dd_event.get_date_object())
            if death == "":
                death = "..."
            value = person_name + "<br/>*", birth, "<br/>+", death
            if thumbnail_url is None:
                boxbg += Html("a", href=url, class_="noThumb") + value
            else:
                thumb = Html("span", class_="thumbnail") + (
                    Html("img", src=thumbnail_url, alt="Image: " + person_name))
                boxbg += Html("a", href=url) + thumb + value
        shadow = Html(
            "div", class_="shadow", inline=True,
            style="top: %dpx; left: %dpx;" % (top + _SHADOW, xoff + _SHADOW))

        return [boxbg, shadow]

    def extend_line(self, coord_y0, coord_x0):
        """
        Draw and extended line

        @param: coord_y0 -- The starting point
        @param: coord_x0 -- The end of the line
        """
        style = "top: %dpx; left: %dpx; width: %dpx"
        ext_bv = Html("div", class_="bvline", inline=True,
                      style=style % (coord_y0, coord_x0, _HGAP/2)
                     )
        ext_gv = Html("div", class_="gvline", inline=True,
                      style=style % (coord_y0+_SHADOW,
                                     coord_x0, _HGAP/2+_SHADOW)
                     )
        return [ext_bv, ext_gv]

    def connect_line(self, coord_y0, coord_y1, col):
        """
        We need to draw a line between to points

        @param: coord_y0 -- The starting point
        @param: coord_y1 -- The end of the line
        @param: col      -- The generation number
        """
        coord_y = min(coord_y0, coord_y1)
        stylew = "top: %dpx; left: %dpx; width: %dpx;"
        styleh = "top: %dpx; left: %dpx; height: %dpx;"
        coord_x0 = _XOFFSET + col * _WIDTH + (col-1)*_HGAP + _HGAP/2
        cnct_bv = Html("div", class_="bvline", inline=True,
                       style=stylew % (coord_y1, coord_x0, _HGAP/2))
        cnct_gv = Html("div", class_="gvline", inline=True,
                       style=stylew % (coord_y1+_SHADOW,
                                       coord_x0+_SHADOW,
                                       _HGAP/2+_SHADOW))
        cnct_bh = Html("div", class_="bhline", inline=True,
                       style=styleh % (coord_y, coord_x0,
                                       abs(coord_y0-coord_y1)))
        cnct_gh = Html("div", class_="gvline", inline=True,
                       style=styleh % (coord_y+_SHADOW,
                                       coord_x0+_SHADOW,
                                       abs(coord_y0-coord_y1)))
        return [cnct_bv, cnct_gv, cnct_bh, cnct_gh]

    def draw_connected_box(self, center1, center2, col, handle):
        """
        Draws the connected box for Ancestor Tree on the Individual Page

        @param: center1 -- The first box to connect
        @param: center2 -- The destination box to draw
        @param: col     -- The generation number
        @param: handle  -- The handle of the person to set in the new box
        """
        box = []
        if not handle:
            return box
        person = self.r_db.get_person_from_handle(handle)
        box = self.draw_box(center2, col, person)
        box += self.connect_line(center1, center2, col)
        return box

    def display_tree(self):
        """
        Display the Ancestor Tree
        """
        tree = []
        if not self.person.get_main_parents_family_handle():
            return None

        generations = self.report.options['graphgens']
        max_in_col = 1 << (generations-1)
        max_size = _HEIGHT*max_in_col + _VGAP*(max_in_col+1)
        center = int(max_size/2)

        with Html("div", id="tree", class_="subsection") as tree:
            tree += Html("h4", self._('Ancestors'), inline=True)
            with Html("div", id="treeContainer",
                      style="width:%dpx; height:%dpx;" % (
                          _XOFFSET+(generations)*_WIDTH+(generations-1)*_HGAP,
                          max_size)
                     ) as container:
                tree += container
                container += self.draw_tree(1, generations, max_size,
                                            0, center, self.person.handle)
        return tree

    def draw_tree(self, gen_nr, maxgen, max_size, old_center,
                  new_center, person_handle):
        """
        Draws the Ancestor Tree

        @param: gen_nr        -- The generation number to draw
        @param: maxgen        -- The maximum number of generations to draw
        @param: max_size      -- The maximum size of the drawing area
        @param: old_center    -- The position of the old box
        @param: new_center    -- The position of the new box
        @param: person_handle -- The handle of the person to draw
        """
        tree = []
        if gen_nr > maxgen:
            return tree
        gen_offset = int(max_size / pow(2, gen_nr+1))
        if person_handle:
            person = self.r_db.get_person_from_handle(person_handle)
        else:
            person = None
        if not person:
            return tree

        if gen_nr == 1:
            tree = self.draw_box(new_center, 0, person)
        else:
            tree = self.draw_connected_box(old_center, new_center,
                                           gen_nr-1, person_handle)

        if gen_nr == maxgen:
            return tree

        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            line_offset = _XOFFSET + gen_nr*_WIDTH + (gen_nr-1)*_HGAP
            tree += self.extend_line(new_center, line_offset)

            family = self.r_db.get_family_from_handle(family_handle)

            f_center = new_center-gen_offset
            f_handle = family.get_father_handle()
            tree += self.draw_tree(gen_nr+1, maxgen, max_size,
                                   new_center, f_center, f_handle)

            m_center = new_center+gen_offset
            m_handle = family.get_mother_handle()
            tree += self.draw_tree(gen_nr+1, maxgen, max_size,
                                   new_center, m_center, m_handle)
        return tree

    def display_ind_associations(self, assoclist):
        """
        Display an individual's associations

        @param: assoclist -- The list of persons for association
        """
        # begin Associations division
        with Html("div", class_="subsection", id="Associations") as section:
            section += Html("h4", self._('Associations'), inline=True)

            with Html("table", class_="infolist assoclist") as table:
                section += table

                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                assoc_row = [
                    (self._("Person"), 'Person'),
                    (self._('Relationship'), 'Relationship'),
                    (self._("Notes"), 'Notes'),
                    (self._("Sources"), 'Sources'),
                    ]

                trow.extend(
                    Html("th", label, class_="Column" + colclass, inline=True)
                    for (label, colclass) in assoc_row)

                tbody = Html("tbody")
                table += tbody

                for person_ref in assoclist:
                    trow = Html("tr")
                    tbody += trow

                    person_lnk = self.new_person_link(person_ref.ref,
                                                      uplink=True)

                    index = 0
                    for data in [
                            person_lnk,
                            person_ref.get_relation(),
                            self.dump_notes(person_ref.get_note_list()),
                            self.get_citation_links(
                                person_ref.get_citation_list()),
                        ]:

                        # get colclass from assoc_row
                        colclass = assoc_row[index][1]

                        trow += Html("td", data, class_="Column" + colclass,
                                     inline=True)
                        index += 1

        # return section to its callers
        return section

    def display_ind_pedigree(self):
        """
        Display an individual's pedigree
        """
        birthorder = self.report.options["birthorder"]

        # Define helper functions
        def children_ped(ol_html):
            """
            Create a children list

            @param: ol_html -- The html element to complete
            """
            if family:
                childlist = family.get_child_ref_list()

                childlist = [child_ref.ref for child_ref in childlist]
                children = add_birthdate(self.r_db, childlist, self.rlocale)

                if birthorder:
                    children = sorted(children)

                for birthdate, birth, death, handle in children:
                    if handle == self.person.get_handle():
                        child_ped(ol_html)
                    elif handle:
                        child = self.r_db.get_person_from_handle(handle)
                        if child:
                            ol_html += Html("li") + self.pedigree_person(child)
            else:
                child_ped(ol_html)
            return ol_html

        def child_ped(ol_html):
            """
            Create a child element list

            @param: ol_html -- The html element to complete
            """
            with Html("li", self.name, class_="thisperson") as pedfam:
                family = self.pedigree_family()
                if family:
                    pedfam += Html("ol", class_="spouselist") + family
            return ol_html + pedfam
        # End of helper functions

        parent_handle_list = self.person.get_parent_family_handle_list()
        if parent_handle_list:
            parent_handle = parent_handle_list[0]
            family = self.r_db.get_family_from_handle(parent_handle)
            father_handle = family.get_father_handle()
            mother_handle = family.get_mother_handle()
            if mother_handle:
                mother = self.r_db.get_person_from_handle(mother_handle)
            else:
                mother = None
            if father_handle:
                father = self.r_db.get_person_from_handle(father_handle)
            else:
                father = None
        else:
            family = None
            father = None
            mother = None

        with Html("div", id="pedigree", class_="subsection") as ped:
            ped += Html("h4", self._('Pedigree'), inline=True)
            with Html("ol", class_="pedigreegen") as pedol:
                ped += pedol
                if father and mother:
                    pedfa = Html("li") + self.pedigree_person(father)
                    pedol += pedfa
                    with Html("ol") as pedma:
                        pedfa += pedma
                        pedma += (Html("li", class_="spouse") +
                                  self.pedigree_person(mother) +
                                  children_ped(Html("ol"))
                                 )
                elif father:
                    pedol += (Html("li") + self.pedigree_person(father) +
                              children_ped(Html("ol"))
                             )
                elif mother:
                    pedol += (Html("li") + self.pedigree_person(mother) +
                              children_ped(Html("ol"))
                             )
                else:
                    pedol += (Html("li") + children_ped(Html("ol")))
        return ped

    def display_ind_general(self):
        """
        display an individual's general information...
        """
        self.page_title = self.sort_name
        thumbnail = self.disp_first_img_as_thumbnail(
            self.person.get_media_list(), self.person)
        section_title = Html("h3", html_escape(self.page_title),
                             inline=True) + (
                                 Html('sup') + (
                                     Html('small') +
                                     self.get_citation_links(
                                         self.person.get_citation_list())))

        # begin summaryarea division
        with Html("div", id='summaryarea') as summaryarea:

            # begin general details table
            with Html("table", class_="infolist") as table:
                summaryarea += table

                primary_name = self.person.get_primary_name()
                all_names = [primary_name] + self.person.get_alternate_names()
                # if the callname or the nickname is the same as the 'first
                # name' (given name), then they are not displayed.
                first_name = primary_name.get_first_name()

                # Names [and their sources]
                for name in all_names:
                    pname = html_escape(_nd.display_name(name))
                    pname += self.get_citation_links(name.get_citation_list())

                    # if we have just a firstname, then the name is preceeded
                    # by ", " which doesn't exactly look very nice printed on
                    # the web page
                    if pname[:2] == ', ': # TODO for Arabic, translate this?
                        pname = pname[2:]
                    if name != primary_name:
                        datetext = self.rlocale.get_date(name.date)
                        if datetext:
                            pname = datetext + ': ' + pname

                    type_ = self._(name.get_type().xml_str())

                    trow = Html("tr") + (
                        Html("td", type_, class_="ColumnAttribute",
                             inline=True)
                        )

                    tcell = Html("td", pname, class_="ColumnValue")
                    # display any notes associated with this name
                    notelist = name.get_note_list()
                    if len(notelist):
                        unordered = Html("ul")

                        for notehandle in notelist:
                            note = self.r_db.get_note_from_handle(notehandle)
                            if note:
                                note_text = self.get_note_format(note, True)

                                # attach note
                                unordered += note_text
                        tcell += unordered
                    trow += tcell
                    table += trow

                    # display the callname associated with this name.
                    call_name = name.get_call_name()
                    if call_name and call_name != first_name:
                        trow = Html("tr") + (
                            Html("td", _("Call Name"), class_="ColumnAttribute",
                                 inline=True),
                            Html("td", call_name, class_="ColumnValue",
                                 inline=True)
                            )
                        table += trow

                    # display the nickname associated with this name. Note that
                    # this no longer displays the Nickname attribute (if
                    # present), because the nickname attribute is deprecated in
                    # favour of the nick_name property of the name structure
                    # (see http://gramps.1791082.n4.nabble.com/Where-is-
                    # nickname-stored-tp4469779p4484272.html), and also because
                    # the attribute is (normally) displayed lower down the
                    # wNarrative Web report.
                    nick_name = name.get_nick_name()
                    if nick_name and nick_name != first_name:
                        trow = Html("tr") + (
                            Html("td", self._("Nick Name"),
                                 class_="ColumnAttribute",
                                 inline=True),
                            Html("td", nick_name, class_="ColumnValue",
                                 inline=True)
                            )
                        table += trow

                # Gramps ID
                person_gid = self.person.get_gramps_id()
                if not self.noid and person_gid:
                    trow = Html("tr") + (
                        Html("td", self._("Gramps ID"),
                             class_="ColumnAttribute",
                             inline=True),
                        Html("td", person_gid, class_="ColumnValue",
                             inline=True)
                        )
                    table += trow

                # Gender
                gender = self._(self.gender_map[self.person.gender])
                trow = Html("tr") + (
                    Html("td", self._("Gender"), class_="ColumnAttribute",
                         inline=True),
                    Html("td", gender, class_="ColumnValue", inline=True)
                    )
                table += trow

                # Age At Death???
                birth_date = Date.EMPTY
                birth_ref = self.person.get_birth_ref()
                if birth_ref:
                    birth = self.r_db.get_event_from_handle(birth_ref.ref)
                    if birth:
                        birth_date = birth.get_date_object()

                if birth_date and birth_date is not Date.EMPTY:
                    alive = probably_alive(self.person, self.r_db, Today())

                    death_date = _find_death_date(self.r_db, self.person)
                    if not alive and death_date is not None:
                        nyears = death_date - birth_date
                        nyears = nyears.format(precision=3,
                                               dlocale=self.rlocale)
                        trow = Html("tr") + (
                            Html("td", self._("Age at Death"),
                                 class_="ColumnAttribute", inline=True),
                            Html("td", nyears,
                                 class_="ColumnValue", inline=True)
                            )
                        table += trow

        # return all three pieces to its caller
        # do NOT combine before returning
        return thumbnail, section_title, summaryarea

    def display_ind_events(self, place_lat_long):
        """
        will create the events table

        @param: place_lat_long -- For use in Family Map Pages. This will be None
                                  if called from Family pages, which do not
                                  create a Family Map
        """
        event_ref_list = self.person.get_event_ref_list()
        if not event_ref_list:
            return None

        # begin events division and section title
        with Html("div", id="events", class_="subsection") as section:
            section += Html("h4", self._("Events"), inline=True)

            # begin events table
            with Html("table", class_="infolist eventlist") as table:
                section += table

                thead = Html("thead")
                table += thead

                # attach event header row
                thead += self.event_header_row()

                tbody = Html("tbody")
                table += tbody

                for evt_ref in event_ref_list:
                    event = self.r_db.get_event_from_handle(evt_ref.ref)
                    if event:

                        # display event row
                        tbody += self.display_event_row(event, evt_ref,
                                                        place_lat_long,
                                                        True, True,
                                                        EventRoleType.PRIMARY)
        return section

    def display_parent(self, handle, title, rel):
        """
        This will display a parent ...

        @param: handle -- The person handle
        @param: title  -- Is the title of the web page
        @param: rel    -- The relation
        """
        tcell1 = Html("td", title, class_="ColumnAttribute", inline=True)
        tcell2 = Html("td", class_="ColumnValue", close=False, inline=True)

        tcell2 += self.new_person_link(handle, uplink=True)

        if rel and rel != ChildRefType(ChildRefType.BIRTH):
            tcell2 += ''.join(['&nbsp;'] *3 + ['(%s)']) % str(rel)

        person = self.r_db.get_person_from_handle(handle)
        birth = death = ""
        if person:
            bd_event = get_birth_or_fallback(self.r_db, person)
            if bd_event:
                birth = self.rlocale.get_date(bd_event.get_date_object())
            dd_event = get_death_or_fallback(self.r_db, person)
            if dd_event:
                death = self.rlocale.get_date(dd_event.get_date_object())

        tcell3 = Html("td", birth, class_="ColumnDate",
                      inline=False, close=False, indent=False)

        tcell4 = Html("td", death, class_="ColumnDate",
                      inline=True, close=False, indent=False)

        tcell2 += tcell3
        tcell2 += tcell4

        # return table columns to its caller
        return tcell1, tcell2

    def get_reln_in_family(self, ind, family):
        """
        Display the relation of the indiv in the family

        @param: ind    -- The person to use
        @param: family -- The family
        """
        child_handle = ind.get_handle()
        child_ref_list = family.get_child_ref_list()
        for child_ref in child_ref_list:
            if child_ref.ref == child_handle:
                return (child_ref.get_father_relation(),
                        child_ref.get_mother_relation())
        return (None, None)

    def display_ind_parent_family(self, birthmother, birthfather, family,
                                  table,
                                  first=False):
        """
        Display the individual parent family

        @param: birthmother -- The birth mother
        @param: birthfather -- The birth father
        @param: family      -- The family
        @param: table       -- The html document to complete
        @param: first       -- Is this the first indiv ?
        """
        if not first:
            trow = Html("tr") + (Html("td", "&nbsp;", colspan=3,
                                      inline=True))
            table += trow

        # get the father
        father_handle = family.get_father_handle()
        if father_handle:
            if father_handle == birthfather:
                # The parent may not be birth father in ths family, because it
                # may be a step family. However, it will be odd to display the
                # parent as anything other than "Father"
                reln = self._("Father")
            else:
                if self.step_or_not(family, father_handle):
                    reln = self._("Stepfather")
                else:
                    reln = ""
            trow = Html("tr") + (self.display_parent(father_handle, reln, None))
            table += trow

        # get the mother
        mother_handle = family.get_mother_handle()
        if mother_handle:
            if mother_handle == birthmother:
                reln = self._("Mother")
            else:
                if self.step_or_not(family, mother_handle):
                    reln = self._("Stepmother")
                else:
                    reln = ""
            trow = Html("tr") + (self.display_parent(mother_handle, reln, None))
            table += trow

        for child_ref in family.get_child_ref_list():
            child_handle = child_ref.ref
            child = self.r_db.get_person_from_handle(child_handle)
            if child:
                if child == self.person:
                    reln = ""
                else:
                    try:
                        # We have a try except block here, because the two
                        # people MUST be siblings for the called Relationship
                        # routines to work. Depending on your definition of
                        # sibling, we cannot necessarily guarantee that.
                        sibling_type = self.rel_class.get_sibling_type(
                            self.r_db, self.person, child)

                        reln = self.rel_class.get_sibling_relationship_string(
                            sibling_type, self.person.gender, child.gender)
                        # We have a problem here : reln is never in the choosen
                        # language but in the default language.
                        # Does get_sibling_relationship_string work ?
                        reln = reln[0].upper() + reln[1:]
                    except:
                        reln = self._("Not siblings")

                val1 = "&nbsp;&nbsp;&nbsp;&nbsp;"
                reln = val1 + reln
                # Now output reln, child_link, (frel, mrel)
                frel = child_ref.get_father_relation()
                mrel = child_ref.get_mother_relation()
                if frel != ChildRefType.BIRTH or mrel != ChildRefType.BIRTH:
                    frelmrel = "(%s, %s)" % (str(frel), str(mrel))
                else:
                    frelmrel = ""
                trow = Html("tr") + (
                    Html("td", reln, class_="ColumnAttribute", inline=True))

                tcell = Html("td", val1, class_="ColumnValue", inline=True)
                tcell += self.display_child_link(child_handle)

                birth = death = ""
                bd_event = get_birth_or_fallback(self.r_db, child)
                if bd_event:
                    birth = self.rlocale.get_date(bd_event.get_date_object())
                dd_event = get_death_or_fallback(self.r_db, child)
                if dd_event:
                    death = self.rlocale.get_date(dd_event.get_date_object())

                tcell2 = Html("td", birth, class_="ColumnDate",
                              inline=True)

                tcell3 = Html("td", death, class_="ColumnDate",
                              inline=True)

                trow += tcell
                trow += tcell2
                trow += tcell3

                tcell = Html("td", frelmrel, class_="ColumnValue",
                             inline=True)
                trow += tcell
                table += trow

    def step_or_not(self, family, handle):
        """
        Quickly check to see if this person is a stepmother or stepfather

        We assume this is not a stepmother or a stepfather if :
         1 - The father or mother died before the child birth
         2 - The father or the mother divorced before the child birth
         3 - The father or the mother married after the child death

        In all other cases, they are stepfather or stepmother.

        @param: family The family we examine
        @param: handle The handle of the father or the mother
        self.person    The child for whom we need this result
        """
        bd_date = Today()
        bd_event = get_birth_or_fallback(self.r_db, self.person)
        if bd_event:
            bd_date = bd_event.get_date_object()
        for event_ref in family.get_event_ref_list():
            event = self.r_db.get_event_from_handle(event_ref.ref)
            if (event.type == EventType.DIVORCE and
                    event_ref.get_role() in (EventRoleType.FAMILY,
                                             EventRoleType.PRIMARY)):
                dv_date = event.get_date_object()
                if bd_date > dv_date:
                    # We have a divorce before the child birth
                    return False
            if (event.type == EventType.MARRIAGE and
                    event_ref.get_role() in (EventRoleType.FAMILY,
                                             EventRoleType.PRIMARY)):
                dm_date = event.get_date_object()
                dd_date = Today()
                dd_event = get_death_or_fallback(self.r_db, self.person)
                if dd_event:
                    dd_date = dd_event.get_date_object()
                if dd_date < dm_date:
                    # We have a child death before the marriage
                    return False
        pers = self.r_db.get_person_from_handle(handle)
        death_date = Today()
        death_event = get_death_or_fallback(self.r_db, pers)
        if death_event:
            death_date = death_event.get_date_object()
        if bd_date > death_date:
            # We have a death before the child birth
            return False
        return True

    def display_step_families(self, parent_handle,
                              family,
                              all_family_handles,
                              birthmother, birthfather,
                              table):
        """
        Display step families

        @param: parent_handle      -- The family parent handle to display
        @param: family             -- The family
        @param: all_family_handles -- All known family handles
        @param: birthmother        -- The birth mother
        @param: birthfather        -- The birth father
        @param: table              -- The html document to complete
        """
        if parent_handle:
            parent = self.r_db.get_person_from_handle(parent_handle)
            for parent_family_handle in parent.get_family_handle_list():
                if parent_family_handle not in all_family_handles:
                    parent_family = self.r_db.get_family_from_handle(
                        parent_family_handle)
                    self.display_ind_parent_family(birthmother, birthfather,
                                                   parent_family, table)
                    all_family_handles.append(parent_family_handle)

    def display_ind_center_person(self):
        """
        Display the person's relationship to the center person
        """
        center_person = self.r_db.get_person_from_gramps_id(
            self.report.options['pid'])
        if center_person is None:
            return
        if (int(self.report.options['living_people']) !=
            LivingProxyDb.MODE_INCLUDE_ALL):
            if probably_alive(center_person, self.r_db, Today()):
                return
        relationship = self.rel_class.get_one_relationship(self.r_db,
                                                           center_person,
                                                           self.person)
        if relationship == "": # No relation to display
            return

        # begin center_person division
        section = ""
        with Html("div", class_="subsection", id="parents") as section:
            message = self._("Relation to the center person")
            message += " ("
            name_format = self.report.options['name_format']
            primary_name = center_person.get_primary_name()
            name = Name(primary_name)
            name.set_display_as(name_format)
            message += _nd.display_name(name)
            message += ") : "
            message += relationship
            section += Html("h4", message, inline=True)
        return section

    def display_ind_parents(self):
        """
        Display a person's parents
        """
        parent_list = self.person.get_parent_family_handle_list()
        if not parent_list:
            return None

        # begin parents division
        with Html("div", class_="subsection", id="parents") as section:
            section += Html("h4", self._("Parents"), inline=True)

            # begin parents table
            with Html("table", class_="infolist") as table:
                section += table

                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                trow.extend(
                    Html("th", label, class_=colclass, inline=True)
                    for (label, colclass) in [
                        (self._("Relation to main person"), "ColumnAttribute"),
                        (self._("Name"), "ColumnValue"),
                        (self._("Birth date"), "ColumnValue"),
                        (self._("Death date"), "ColumnValue"),
                        (self._("Relation within this family "
                                "(if not by birth)"),
                         "ColumnValue")
                    ]
                )

                tbody = Html("tbody")

                all_family_handles = list(parent_list)
                (birthmother, birthfather) = self.rel_class.get_birth_parents(
                    self.r_db, self.person)

                first = True
                for family_handle in parent_list:
                    family = self.r_db.get_family_from_handle(family_handle)
                    if family:
                        # Display this family
                        self.display_ind_parent_family(birthmother,
                                                       birthfather,
                                                       family, tbody, first)
                        first = False

                        if self.report.options['showhalfsiblings']:
                            # Display all families in which the parents are
                            # involved. This displays half siblings and step
                            # siblings
                            self.display_step_families(
                                family.get_father_handle(), family,
                                all_family_handles,
                                birthmother, birthfather, tbody)
                            self.display_step_families(
                                family.get_mother_handle(), family,
                                all_family_handles,
                                birthmother, birthfather, tbody)
                table += tbody
        return section

    def pedigree_person(self, person):
        """
        will produce a hyperlink for a pedigree person ...

        @param: person -- The person
        """
        hyper = self.new_person_link(person.handle, person=person, uplink=True)
        return hyper

    def pedigree_family(self):
        """
        Returns a family pedigree
        """
        ped = []
        for family_handle in self.person.get_family_handle_list():
            rel_family = self.r_db.get_family_from_handle(family_handle)
            spouse_handle = utils.find_spouse(self.person, rel_family)
            if spouse_handle:
                spouse = self.r_db.get_person_from_handle(spouse_handle)
                pedsp = (Html("li", class_="spouse") +
                         self.pedigree_person(spouse)
                        )
            else:
                pedsp = (Html("li", class_="spouse"))
            ped += [pedsp]
            childlist = rel_family.get_child_ref_list()
            if childlist:
                with Html("ol") as childol:
                    pedsp += [childol]
                    for child_ref in childlist:
                        child = self.r_db.get_person_from_handle(child_ref.ref)
                        if child:
                            childol += (Html("li") +
                                        self.pedigree_person(child)
                                       )
        return ped
