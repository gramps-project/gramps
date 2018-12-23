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
    PlacePage - Place index page and individual Place pages
"""
#------------------------------------------------
# python modules
#------------------------------------------------
from collections import defaultdict
from decimal import getcontext
import logging

#------------------------------------------------
# Gramps module
#------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import (PlaceType, Place)
from gramps.gen.plug.report import Bibliography
from gramps.plugins.lib.libhtml import Html
from gramps.gen.utils.place import conv_lat_lon
from gramps.gen.utils.location import get_main_location

#------------------------------------------------
# specific narrative web import
#------------------------------------------------
from gramps.plugins.webreport.basepage import BasePage
from gramps.plugins.webreport.common import (get_first_letters, first_letter,
                                             alphabet_navigation, GOOGLE_MAPS,
                                             primary_difference, _KEYPLACE,
                                             get_index_letter, FULLCLEAR,
                                             MARKER_PATH, OSM_MARKERS, MARKERS,
                                             html_escape)

_ = glocale.translation.sgettext
LOG = logging.getLogger(".NarrativeWeb")
getcontext().prec = 8

######################################################
#                                                    #
#                    Place Pages                     #
#                                                    #
######################################################
class PlacePages(BasePage):
    """
    This class is responsible for displaying information about the 'Person'
    database objects. It displays this information under the 'Events'
    tab. It is told by the 'add_instances' call which 'Person's to display,
    and remembers the list of persons. A single call to 'display_pages'
    displays both the Event List (Index) page and all the Event
    pages.

    The base class 'BasePage' is initialised once for each page that is
    displayed.
    """
    def __init__(self, report):
        """
        @param: report -- The instance of the main report class for
                          this report
        """
        BasePage.__init__(self, report, title="")
        self.place_dict = defaultdict(set)
        self.placemappages = None
        self.mapservice = None
        self.person = None
        self.familymappages = None
        self.googlemapkey = None

        # Place needs to display coordinates?
        self.display_coordinates = report.options["coordinates"]

    def display_pages(self, title):
        """
        Generate and output the pages under the Place tab, namely the place
        index and the individual place pages.

        @param: title -- Is the title of the web page
        """
        LOG.debug("obj_dict[Place]")
        for item in self.report.obj_dict[Place].items():
            LOG.debug("    %s", str(item))
        message = _("Creating place pages")
        with self.r_user.progress(_("Narrated Web Site Report"), message,
                                  len(self.report.obj_dict[Place]) + 1
                                 ) as step:
            index = 1
            for place_handle in self.report.obj_dict[Place]:
                step()
                index += 1
                self.placepage(self.report, title, place_handle)
            step()
            self.placelistpage(self.report, title,
                               self.report.obj_dict[Place].keys())

    def placelistpage(self, report, title, place_handles):
        """
        Create a place index

        @param: report        -- The instance of the main report class for
                                 this report
        @param: title         -- Is the title of the web page
        @param: place_handles -- The handle for the place to add
        """
        BasePage.__init__(self, report, title)

        output_file, sio = self.report.create_file("places")
        placelistpage, head, body = self.write_header(self._("Places"))
        ldatec = 0
        prev_letter = " "

        # begin places division
        with Html("div", class_="content", id="Places") as placelist:
            body += placelist

            # place list page message
            msg = self._("This page contains an index of all the places in the "
                         "database, sorted by their title. "
                         "Clicking on a place&#8217;s "
                         "title will take you to that place&#8217;s page.")
            placelist += Html("p", msg, id="description")

            # begin alphabet navigation
            index_list = get_first_letters(self.r_db, place_handles,
                                           _KEYPLACE, rlocale=self.rlocale)
            alpha_nav = alphabet_navigation(index_list, self.rlocale)
            if alpha_nav is not None:
                placelist += alpha_nav

            # begin places table and table head
            with Html("table",
                      class_="infolist primobjlist placelist") as table:
                placelist += table

                # begin table head
                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                if self.display_coordinates:
                    trow.extend(
                        Html("th", label, class_=colclass, inline=True)
                        for (label, colclass) in [
                            [self._("Letter"), "ColumnLetter"],
                            [self._("Place Name | Name"), "ColumnName"],
                            [self._("State/ Province"), "ColumnState"],
                            [self._("Country"), "ColumnCountry"],
                            [self._("Latitude"), "ColumnLatitude"],
                            [self._("Longitude"), "ColumnLongitude"]
                        ]
                    )
                else:
                    trow.extend(
                        Html("th", label, class_=colclass, inline=True)
                        for (label, colclass) in [
                            [self._("Letter"), "ColumnLetter"],
                            [self._("Place Name | Name"), "ColumnName"],
                            [self._("State/ Province"), "ColumnState"],
                            [self._("Country"), "ColumnCountry"]
                        ]
                    )

                # bug 9495 : incomplete display of place hierarchy labels
                def sort_by_place_name(obj):
                    """ sort by lower case place name. """
                    name = self.report.obj_dict[Place][obj][1]
                    return name.lower()

                handle_list = sorted(place_handles,
                                     key=lambda x: sort_by_place_name(x))
                first = True

                # begin table body
                tbody = Html("tbody")
                table += tbody

                for place_handle in handle_list:
                    place = self.r_db.get_place_from_handle(place_handle)
                    if place:
                        if place.get_change_time() > ldatec:
                            ldatec = place.get_change_time()
                        plc_title = self.report.obj_dict[Place][place_handle][1]
                        main_location = get_main_location(self.r_db, place)

                        if plc_title and plc_title != " ":
                            letter = get_index_letter(first_letter(plc_title),
                                                      index_list,
                                                      self.rlocale)
                        else:
                            letter = '&nbsp;'

                        trow = Html("tr")
                        tbody += trow

                        tcell = Html("td", class_="ColumnLetter", inline=True)
                        trow += tcell
                        if first or primary_difference(letter, prev_letter,
                                                       self.rlocale):
                            first = False
                            prev_letter = letter
                            trow.attr = 'class = "BeginLetter"'

                            ttle = self._("Places beginning "
                                          "with letter %s") % letter
                            tcell += Html("a", letter, name=letter, title=ttle)
                        else:
                            tcell += "&nbsp;"

                        trow += Html("td",
                                     self.place_link(
                                         place.get_handle(),
                                         plc_title, place.get_gramps_id()),
                                     class_="ColumnName")

                        trow.extend(
                            Html("td", data or "&nbsp;", class_=colclass,
                                 inline=True)
                            for (colclass, data) in [
                                ["ColumnState",
                                 main_location.get(PlaceType.STATE, '')],
                                ["ColumnCountry",
                                 main_location.get(PlaceType.COUNTRY, '')]
                            ]
                        )

                        if self.display_coordinates:
                            tcell1 = Html("td", class_="ColumnLatitude",
                                          inline=True)
                            tcell2 = Html("td", class_="ColumnLongitude",
                                          inline=True)
                            trow += (tcell1, tcell2)

                            if place.lat and place.long:
                                latitude, longitude = conv_lat_lon(place.lat,
                                                                   place.long,
                                                                   "DEG")
                                tcell1 += latitude
                                tcell2 += longitude
                            else:
                                tcell1 += '&nbsp;'
                                tcell2 += '&nbsp;'

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(placelistpage, output_file, sio, ldatec)

    def placepage(self, report, title, place_handle):
        """
        Create a place page

        @param: report            -- The instance of the main report class for
                                     this report
        @param: title             -- Is the title of the web page
        @param: place_handle -- The handle for the place to add
        """
        place = report.database.get_place_from_handle(place_handle)
        if not place:
            return None
        BasePage.__init__(self, report, title, place.get_gramps_id())
        self.bibli = Bibliography()
        place_name = self.report.obj_dict[Place][place_handle][1]
        ldatec = place.get_change_time()

        output_file, sio = self.report.create_file(place_handle, "plc")
        self.uplink = True
        self.page_title = place_name
        placepage, head, body = self.write_header(_("Places"))

        self.placemappages = self.report.options['placemappages']
        self.mapservice = self.report.options['mapservice']
        self.googlemapkey = self.report.options['googlemapkey']

        # begin PlaceDetail Division
        with Html("div", class_="content", id="PlaceDetail") as placedetail:
            body += placedetail

            if self.create_media:
                media_list = place.get_media_list()
                thumbnail = self.disp_first_img_as_thumbnail(media_list,
                                                             place)
                if thumbnail is not None:
                    placedetail += thumbnail

            # add section title
            placedetail += Html("h3",
                                html_escape(place_name),
                                inline=True)

            # begin summaryarea division and places table
            with Html("div", id='summaryarea') as summaryarea:
                placedetail += summaryarea

                with Html("table", class_="infolist place") as table:
                    summaryarea += table

                    # list the place fields
                    self.dump_place(place, table)

            # place gallery
            if self.create_media:
                placegallery = self.disp_add_img_as_gallery(media_list, place)
                if placegallery is not None:
                    placedetail += placegallery

            # place notes
            notelist = self.display_note_list(place.get_note_list())
            if notelist is not None:
                placedetail += notelist

            # place urls
            urllinks = self.display_url_list(place.get_url_list())
            if urllinks is not None:
                placedetail += urllinks

            # add place map here
            # Link to Gramps marker
            fname = "/".join(['images', 'marker.png'])
            marker_path = self.report.build_url_image("marker.png",
                                                      "images", self.uplink)

            if self.placemappages:
                if place and (place.lat and place.long):
                    latitude, longitude = conv_lat_lon(place.get_latitude(),
                                                       place.get_longitude(),
                                                       "D.D8")
                    placetitle = place_name

                    # add narrative-maps CSS...
                    fname = "/".join(["css", "narrative-maps.css"])
                    url = self.report.build_url_fname(fname, None, self.uplink)
                    head += Html("link", href=url, type="text/css",
                                 media="screen", rel="stylesheet")

                    # add MapService specific javascript code
                    src_js = GOOGLE_MAPS + "api/js?sensor=false"
                    if self.mapservice == "Google":
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
                        src_js += ("ajax.googleapis.com/ajax/libs/jquery/1.9.1/"
                                   "jquery.min.js")
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

                    # section title
                    placedetail += Html("h4", self._("Place Map"), inline=True)

                    # begin map_canvas division
                    with Html("div", id="map_canvas", inline=True) as canvas:
                        placedetail += canvas

                        # Begin inline javascript code because jsc is a
                        # docstring, it does NOT have to be properly indented
                        if self.mapservice == "Google":
                            with Html("script", type="text/javascript",
                                      indent=False) as jsc:
                                head += jsc

                                # Google adds Latitude/ Longitude to its maps...
                                plce = placetitle.replace("'", "\\'")
                                jsc += MARKER_PATH % marker_path
                                jsc += MARKERS % ([[plce,
                                                    latitude,
                                                    longitude,
                                                    1]],
                                                  latitude, longitude,
                                                  10)

                        else:
                            # OpenStreetMap (OSM) adds Longitude/ Latitude
                            # to its maps, and needs a country code in
                            # lowercase letters...
                            with Html("script", type="text/javascript") as jsc:
                                canvas += jsc
                                #param1 = xml_lang()[3:5].lower()
                                jsc += MARKER_PATH % marker_path
                                jsc += OSM_MARKERS % ([[float(longitude),
                                                        float(latitude),
                                                        placetitle]],
                                                      longitude, latitude, 10)

            # add javascript function call to body element
            body.attr += ' onload = "initialize();" '

            # add div for popups.
            with Html("div", id="popup", inline=True) as popup:
                placedetail += popup

            # source references
            srcrefs = self.display_ind_sources(place)
            if srcrefs is not None:
                placedetail += srcrefs

            # References list
            ref_list = self.display_bkref_list(Place, place_handle)
            if ref_list is not None:
                placedetail += ref_list

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        body += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(placepage, output_file, sio, ldatec)
