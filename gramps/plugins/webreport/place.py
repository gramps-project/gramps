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
    PlacePage - Place index page and individual Place pages
"""
# ------------------------------------------------
# python modules
# ------------------------------------------------
from collections import defaultdict
from decimal import getcontext
import logging

# ------------------------------------------------
# Gramps module
# ------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import PlaceType, Place, PlaceName, Media
from gramps.gen.plug.report import Bibliography
from gramps.gen.mime import is_image_type
from gramps.plugins.lib.libhtml import Html
from gramps.gen.utils.place import conv_lat_lon, coord_formats
from gramps.gen.utils.location import get_main_location
from gramps.gen.display.place import displayer as _pd

# ------------------------------------------------
# specific narrative web import
# ------------------------------------------------
from gramps.plugins.webreport.basepage import BasePage
from gramps.plugins.webreport.common import (
    alphabet_navigation,
    GOOGLE_MAPS,
    FULLCLEAR,
    MARKER_PATH,
    OPENLAYER,
    OSM_MARKERS,
    STAMEN_MARKERS,
    MARKERS,
    html_escape,
    sort_places,
    AlphabeticIndex,
)

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

    def __init__(self, report, the_lang, the_title):
        """
        @param: report    -- The instance of the main report class
                             for this report
        @param: the_lang  -- The lang to process
        @param: the_title -- The title page related to the language
        """
        BasePage.__init__(self, report, the_lang, the_title)
        self.place_dict = defaultdict(set)
        self.placemappages = None
        self.mapservice = None
        self.person = None
        self.familymappages = None
        self.googlemapkey = None
        self.stamenopts = None

        # Place needs to display coordinates?
        self.display_coordinates = report.options["coordinates"]

    def display_pages(self, the_lang, the_title):
        """
        Generate and output the pages under the Place tab, namely the place
        index and the individual place pages.

        @param: the_lang  -- The lang to process
        @param: the_title -- The title page related to the language
        """
        LOG.debug("obj_dict[Place]")
        for item in self.report.obj_dict[Place].items():
            LOG.debug("    %s", str(item))
        message = _("Creating place pages")
        progress_title = self.report.pgrs_title(the_lang)
        if self.report.options["inc_uplaces"]:
            place_count = len(self.r_db.get_place_handles())
        else:
            place_count = len(self.report.obj_dict[Place])
        with self.r_user.progress(progress_title, message, place_count + 1) as step:
            if self.report.options["inc_uplaces"]:
                # add unused place
                place_list = self.r_db.get_place_handles()
                for place_ref in place_list:
                    if place_ref not in self.report.obj_dict[Place]:
                        place = self.r_db.get_place_from_handle(place_ref)
                        if place:
                            place_name = place.get_title()
                            p_fname = self.report.build_url_fname(
                                place_ref, "plc", False, init=True
                            )
                            p_fname += self.ext
                            plc_dict = (p_fname, place_name, place.gramps_id, None)
                            self.report.obj_dict[Place][place_ref] = plc_dict
                            p_name = _pd.display(self.r_db, place, fmt=0)
                            cplace_name = p_name.split()[-1]
                            if len(place_name.split()) > 1:
                                splace_name = place_name.split()[-2]
                            else:
                                splace_name = cplace_name
                            plc_dict = (
                                place_ref,
                                p_name,
                                splace_name,
                                cplace_name,
                                place.gramps_id,
                                None,
                            )
                            self.report.obj_dict[PlaceName][p_name] = plc_dict

        with self.r_user.progress(
            progress_title, message, len(self.report.obj_dict[Place]) + 1
        ) as step:
            index = 1
            for place_name in self.report.obj_dict[PlaceName].keys():
                step()
                p_handle = self.report.obj_dict[PlaceName][place_name]
                index += 1
                if isinstance(p_handle, tuple):
                    self.placepage(
                        self.report, the_lang, the_title, p_handle[0], place_name
                    )
            step()
        self.placelistpage(self.report, the_lang, the_title)

    def __output_place(
        self,
        ldatec,
        tbody,
        first_place,
        pname,
        sname,
        cname,
        place_handle,
        letter,
        bucket_link,
    ):
        place = None
        if place_handle:
            place = self.r_db.get_place_from_handle(place_handle)
        if place:
            if place.get_change_time() > ldatec:
                ldatec = place.get_change_time()
            nbrs = len(pname.split(","))
            plc_title = pname
            if nbrs == 3:
                plc_title = ", ".join(pname.split(",")[:1])
            elif nbrs == 4:
                plc_title = ", ".join(pname.split(",")[:2])
            elif nbrs == 5:
                plc_title = ", ".join(pname.split(",")[:3])
            elif nbrs == 6:
                plc_title = ", ".join(pname.split(",")[:4])
            main_location = get_main_location(self.r_db, place)
            if not plc_title or plc_title == " ":
                letter = "&nbsp;"
            trow = Html("tr")
            tbody += trow
            tcell = Html("td", class_="ColumnLetter", inline=True)
            trow += tcell
            if first_place:
                # or primary_difference(letter, prev_letter, self.rlocale):
                first_place = False
                # prev_letter = letter
                trow.attr = 'class = "BeginLetter"'
                ttle = self._("Places beginning " "with letter %s") % letter
                tcell += Html("a", letter, name=letter, title=ttle, id_=bucket_link)
            else:
                tcell += "&nbsp;"
            trow += Html(
                "td",
                self.place_link(place.get_handle(), plc_title, place.get_gramps_id()),
                class_="ColumnName",
            )
            trow.extend(
                Html("td", data or "&nbsp;", class_=colclass, inline=True)
                for (colclass, data) in [
                    # Use the two last field of a place
                    # We could have strange values if we
                    # have a placename like:
                    # city, province, country, mainland, planet...
                    # mainland and planet are custom types
                    ["ColumnState", sname],
                    ["ColumnCountry", cname],
                ]
            )
            if self.display_coordinates:
                tcell1 = Html("td", class_="ColumnLatitude", inline=True)
                tcell2 = Html("td", class_="ColumnLongitude", inline=True)
                trow += tcell1, tcell2
                if place.lat and place.long:
                    latitude, longitude = conv_lat_lon(
                        place.lat,
                        place.long,
                        coord_formats[self.report.options["coord_format"]],
                    )
                    tcell1 += latitude
                    tcell2 += longitude
                else:
                    tcell1 += "&nbsp;"
                    tcell2 += "&nbsp;"
        return (ldatec, first_place)

    def placelistpage(self, report, the_lang, the_title):
        """
        Create a place index

        @param: report        -- The instance of the main report class
                                 for this report
        @param: the_lang      -- The lang to process
        @param: the_title     -- The title page related to the language
        """
        BasePage.__init__(self, report, the_lang, the_title)

        output_file, sio = self.report.create_file("places")
        result = self.write_header(self._("Places"))
        placelistpage, dummy_head, dummy_body, outerwrapper = result
        ldatec = 0

        # begin places division
        with Html("div", class_="content", id="Places") as placelist:
            outerwrapper += placelist

            # place list page message
            msg = self._(
                "This page contains an index of all the places in the "
                "database, sorted by their title. "
                "Clicking on a place&#8217;s "
                "title will take you to that place&#8217;s page."
            )
            placelist += Html("p", msg, id="description")

            # begin alphabet navigation
            # Assemble all the places
            index = AlphabeticIndex(self.rlocale)
            # self.report.obj_dict[PlaceName] is a dict with key place_name and
            # values (place_fname, place_name, place.gramps_id, event)
            for place_name, value in self.report.obj_dict[PlaceName].items():
                index.addRecord(place_name, value)

            # Extract the buckets from the index
            index_list = []
            index.resetBucketIterator()
            while index.nextBucket():
                if index.bucketRecordCount != 0:
                    index_list.append(index.bucketLabel)
            # Output the navigation
            alpha_nav = alphabet_navigation(index_list, self.rlocale, rtl=self.dir)
            if alpha_nav:
                placelist += alpha_nav

            # begin places table and table head
            with Html(
                "table", class_="infolist primobjlist placelist " + self.dir
            ) as table:
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
                            [self._("Name", "Place Name"), "ColumnName"],
                            [self._("State/Province"), "ColumnState"],
                            [self._("Country"), "ColumnCountry"],
                            [self._("Latitude"), "ColumnLatitude"],
                            [self._("Longitude"), "ColumnLongitude"],
                        ]
                    )
                else:
                    trow.extend(
                        Html("th", label, class_=colclass, inline=True)
                        for (label, colclass) in [
                            [self._("Letter"), "ColumnLetter"],
                            [self._("Name", "Place Name"), "ColumnName"],
                            [self._("State/Province"), "ColumnState"],
                            [self._("Country"), "ColumnCountry"],
                        ]
                    )

                # begin table body
                tbody = Html("tbody")
                table += tbody

                # For each bucket, output the places in that bucket
                index.resetBucketIterator()
                output = []
                dup_index = 0
                while index.nextBucket():
                    if index.bucketRecordCount != 0:
                        bucket_letter = index.bucketLabel
                        bucket_link = bucket_letter
                        if bucket_letter in output:
                            bucket_link = "%s (%i)" % (bucket_letter, dup_index)
                            dup_index += 1
                        output.append(bucket_letter)
                        # Assemble all the places in this bucket into a dict for
                        # sorting
                        place_dict = dict()
                        while index.nextRecord():
                            place_name = index.recordName
                            value = index.recordData
                            place_dict[place_name] = value

                        handle_list = sort_places(self.r_db, place_dict, self.rlocale)
                        first_place = True
                        for pname, place_handle in handle_list:
                            if not pname:
                                continue
                            val = self.report.obj_dict[PlaceName][pname]
                            nbelem = len(val)
                            if val and nbelem > 3:
                                if isinstance(place_handle, tuple):
                                    place = self.r_db.get_place_from_handle(
                                        place_handle[0]
                                    )
                                else:
                                    place = self.r_db.get_place_from_handle(
                                        place_handle
                                    )
                                main_location = get_main_location(self.r_db, place)
                                sname = main_location.get(PlaceType.STATE, "")
                                cname = main_location.get(PlaceType.COUNTRY, "")
                            elif nbelem == 3:
                                cname = val[3]
                                sname = val[2]
                            else:
                                val = [""]
                                cname = ""
                                sname = ""
                            (ldatec, first_place) = self.__output_place(
                                ldatec,
                                trow,
                                first_place,
                                pname,
                                sname,
                                cname,
                                val[0],
                                bucket_letter,
                                bucket_link,
                            )

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        outerwrapper += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(placelistpage, output_file, sio, ldatec)

    def placepage(self, report, the_lang, the_title, place_handle, place_name):
        """
        Create a place page

        @param: report       -- The instance of the main report class
                                for this report
        @param: the_lang     -- The lang to process
        @param: the_title    -- The title page related to the language
        @param: place_handle -- The handle for the place to add
        @param: place_name   -- The alternate place name
        """
        place = report.database.get_place_from_handle(place_handle)
        if not place:
            return
        BasePage.__init__(self, report, the_lang, the_title, place.get_gramps_id())
        self.bibli = Bibliography()
        ldatec = place.get_change_time()
        apname = _pd.display(self.r_db, place, fmt=0)

        # if place_name:  # != apname: # store only the primary named page
        output_file, sio = self.report.create_file(place_handle, "plc")
        self.uplink = True
        self.page_title = place_name
        (placepage, head, dummy_body, outerwrapper) = self.write_header(_("Places"))

        self.placemappages = self.report.options["placemappages"]
        self.mapservice = self.report.options["mapservice"]
        self.googlemapkey = self.report.options["googlemapkey"]
        self.stamenopts = self.report.options["stamenopts"]

        # begin PlaceDetail Division
        with Html("div", class_="content", id="PlaceDetail") as placedetail:
            outerwrapper += placedetail

            media_list = place.get_media_list()
            if media_list and self.create_media:
                if self.the_lang and not self.usecms:
                    fname = "/".join(["..", "css", "lightbox.css"])
                    jsname = "/".join(["..", "css", "lightbox.js"])
                else:
                    fname = "/".join(["css", "lightbox.css"])
                    jsname = "/".join(["css", "lightbox.js"])
                url = self.report.build_url_fname(fname, None, self.uplink)
                head += Html(
                    "link", href=url, type="text/css", media="screen", rel="stylesheet"
                )
                url = self.report.build_url_fname(jsname, None, self.uplink)
                head += Html("script", src=url, type="text/javascript", inline=True)
                thumbnail = self.disp_first_img_as_thumbnail(media_list, place)
                if thumbnail is not None:
                    if media_list[0].ref in self.report.obj_dict[Media]:
                        placedetail += thumbnail

            # add section title
            placedetail += Html("h3", html_escape(place_name), inline=True)

            # begin summaryarea division and places table
            with Html("div", id="summaryarea") as summaryarea:
                placedetail += summaryarea

                with Html("table", class_="infolist place") as table:
                    summaryarea += table

                    # list the place fields
                    self.dump_place(place, table)

            # place gallery
            if self.create_media and not self.report.options["inc_uplaces"]:
                # Don't diplay media for unused places. It generates
                # "page not found" if they are not collected in pass 1.
                placegallery = self.disp_add_img_as_gallery(media_list, place)
                if placegallery is not None:
                    placedetail += placegallery

            # place notes
            notelist = self.display_note_list(place.get_note_list(), Place)
            if notelist is not None:
                placedetail += notelist

            # place urls
            urllinks = self.display_url_list(place.get_url_list())
            if urllinks is not None:
                placedetail += urllinks

            # add place map here
            # Link to Gramps marker
            fname = "/".join(["images", "marker.png"])
            marker_path = self.report.build_url_image(
                "marker.png", "images", self.uplink
            )

            if self.placemappages:
                if place and (place.lat and place.long):
                    placetitle = place_name

                    # add narrative-maps CSS...
                    if the_lang and not self.usecms:
                        fname = "/".join(["..", "css", "narrative-maps.css"])
                    else:
                        fname = "/".join(["css", "narrative-maps.css"])
                    url = self.report.build_url_fname(fname, None, self.uplink)
                    head += Html(
                        "link",
                        href=url,
                        type="text/css",
                        media="screen",
                        rel="stylesheet",
                    )

                    # add MapService specific javascript code
                    src_js = GOOGLE_MAPS + "api/js"
                    if self.mapservice == "Google":
                        if self.googlemapkey:
                            src_js += "?key=" + self.googlemapkey
                        head += Html(
                            "script", type="text/javascript", src=src_js, inline=True
                        )
                    else:  # OpenStreetMap, Stamen...
                        src_js = self.secure_mode
                        src_js += (
                            "ajax.googleapis.com/ajax/libs/jquery/1.9.1/"
                            "jquery.min.js"
                        )
                        head += Html(
                            "script", type="text/javascript", src=src_js, inline=True
                        )
                        olv = self.report.options["ol_version"]
                        build = "legacy"
                        if olv < "v7.0.0":
                            build = "build"
                        if olv == "latest":
                            build = "legacy"
                        src_js = (
                            "https://openlayers.org/en/" "%(ver)s/%(bld)s/ol.js"
                        ) % {"ver": olv, "bld": build}
                        head += Html(
                            "script", type="text/javascript", src=src_js, inline=True
                        )
                        css = "legacy"
                        if olv < "v7.0.0":
                            css = "css"
                        if olv == "latest":
                            css = "legacy"
                        url = (
                            "https://openlayers.org/en/" "%(ver)s/%(css)s/ol.css"
                        ) % {"ver": olv, "css": css}
                        head += Html(
                            "link", href=url, type="text/css", rel="stylesheet"
                        )

                    # section title
                    placedetail += Html("h4", self._("Place Map"), inline=True)

                    # begin map_canvas division
                    with Html("div", id="map_canvas", inline=True) as canvas:
                        placedetail += canvas

            # add div for popups.
            if self.mapservice == "Google":
                with Html("div", id="popup", inline=True) as popup:
                    placedetail += popup
            else:
                with Html("div", id="popup", class_="ol-popup", inline=True) as popup:
                    placedetail += popup
                    popup += Html(
                        "a", href="#", id="popup-closer", class_="ol-popup-closer"
                    )
                    popup += Html("div", id="popup-title", class_="ol-popup-title")
                    popup += Html("div", id="popup-content")
                with Html(
                    "div", id="tooltip", class_="ol-popup", inline=True
                ) as tooltip:
                    placedetail += tooltip
                    tooltip += Html("div", id="tooltip-content")

            # source references
            if not self.report.options["inc_uplaces"]:
                # We can't display source reference when we display
                # unused places. These info are not in the collected objects.
                # This is to avoid "page not found" errors.
                srcrefs = self.display_ind_sources(place)
                if srcrefs is not None:
                    placedetail += srcrefs

            # References list
            ref_list = self.display_bkref_list(Place, place_handle)
            if ref_list is not None:
                placedetail += ref_list

            # Begin inline javascript code because jsc is a
            # docstring, it does NOT have to be properly indented
            latitude, longitude = conv_lat_lon(
                place.get_latitude(), place.get_longitude(), "D.D8"
            )
            if not (latitude and longitude):
                # We have incorrect longitude and/or latitude for this place.
                latitude = longitude = 0.0
            if self.placemappages:
                if place and (place.lat and place.long):
                    tracelife = " "
                    if self.create_media and media_list:
                        for fmedia in media_list:
                            photo_hdle = fmedia.get_reference_handle()
                            photo = self.r_db.get_media_from_handle(photo_hdle)
                            mime_type = photo.get_mime_type()
                            descr = photo.get_description()

                            if mime_type and is_image_type(mime_type):
                                uplnk = self.uplink
                                (pth, dummy_) = self.report.prepare_copy_media(photo)
                                srbuf = self.report.build_url_fname
                                newpath = srbuf(pth, image=True, uplink=uplnk)
                                imglnk = self.media_link(
                                    photo_hdle,
                                    newpath,
                                    descr,
                                    uplink=uplnk,
                                    usedescr=False,
                                )
                                if photo_hdle in self.report.obj_dict[Media]:
                                    tracelife += str(imglnk)
                                break  # We show only the first image
                    with Html("script", type="text/javascript", indent=False) as jsc:
                        if self.mapservice == "Google":
                            # scripts += jsc
                            # Google adds Latitude/ Longitude to its maps...
                            plce = placetitle.replace("'", "\\'")
                            jsc += MARKER_PATH % marker_path
                            jsc += MARKERS % (
                                [[plce, latitude, longitude, 1, tracelife]],
                                latitude,
                                longitude,
                                10,
                            )
                        elif self.mapservice == "OpenStreetMap":
                            jsc += MARKER_PATH % marker_path
                            jsc += OSM_MARKERS % (
                                [
                                    [
                                        float(longitude),
                                        float(latitude),
                                        placetitle,
                                        tracelife,
                                    ]
                                ],
                                longitude,
                                latitude,
                                10,
                            )
                            jsc += OPENLAYER
                        else:  # STAMEN
                            jsc += MARKER_PATH % marker_path
                            jsc += STAMEN_MARKERS % (
                                [
                                    [
                                        float(longitude),
                                        float(latitude),
                                        placetitle,
                                        tracelife,
                                    ]
                                ],
                                self.stamenopts,
                                longitude,
                                latitude,
                                10,
                            )
                            jsc += OPENLAYER
                    placedetail += jsc

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        outerwrapper += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        # if place_name:  # != apname: # store only the primary named page
        self.xhtml_writer(placepage, output_file, sio, ldatec)
