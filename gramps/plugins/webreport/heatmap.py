#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021    Matthias Kemmer
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
"""Heatmap web report."""


# ------------------------------------------------
# python modules
# ------------------------------------------------
import logging
from string import Template
from decimal import Decimal, getcontext


# ------------------------------------------------------------------------
#
# GRAMPS modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.utils.place import conv_lat_lon
from gramps.plugins.lib.libhtml import Html
from gramps.gen.display.name import displayer as _nd
from gramps.gen.display.place import displayer as _pd

# ------------------------------------------------
# specific narrative web import
# ------------------------------------------------
from gramps.plugins.webreport.basepage import BasePage
from gramps.gen.lib import (
    EventType,
    Event,
    Family,
    Name,
    Person,
)
from gramps.plugins.webreport.common import (
    alphabet_navigation,
    FULLCLEAR,
    AlphabeticIndex,
    MARKER_PATH,
    OPENLAYER,
    OSM_MARKERS,
    html_escape,
)
from gramps.plugins.webreport.multiselect import (
    get_surnames_list,
    get_tags_list,
)

_ = glocale.translation.sgettext
LOG = logging.getLogger(".Heatmap")
getcontext().prec = 8

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext


# ------------------------------------------------------------------------
#
# HeatmapPlaces Class
#
# ------------------------------------------------------------------------
class HeatmapPlace:
    """Class storing heatmap place data."""

    def __init__(self, name, latitude, longitude, count, titlename):
        self.name = name  # gramps_id
        self.lat = latitude
        self.lon = longitude
        self.count = count
        self.title_name = titlename
        self.events = []

    def to_list(self):
        return [self.lat, self.lon, self.count]

    def add_event(self, event_ID):
        self.events.append(event_ID)

    def get_all(self):
        return [self.name, self.lat, self.lon, self.count, self.title_name, self.events]


# ------------------------------------------------------------------------
#
# Heatmap Report Class
#
# ------------------------------------------------------------------------
class HeatmapPage(BasePage):
    """
    This class is responsible for displaying information about Heatmaps

    The base class 'BasePage' is initialised once for each page that is
    displayed.
    """

    def __init__(self, report, the_lang, the_title, the_filter):
        """
        @param: report    -- The instance of the main report class
                             for this report
        @param: the_lang  -- The lang to process
        @param: the_title -- The title page related to the language
        """
        BasePage.__init__(self, report, the_lang, the_title, the_filter)
        self.report = report
        self.sort_name = None
        self.person = None
        self.rel_class = None
        self.events = []
        self.places = []
        self.count = 0
        self.radius = int(report.options["radius"])
        self.blur = int(report.options["blur"])
        self.vallat = float(0.0)
        self.vallon = float(0.0)
        self.lookingfor = None
        self.selected_filter = the_filter
        self.display_pages(the_lang, the_title)

    def display_pages(self, the_lang, the_title):
        """
        Generate and output the pages under the Individuals tab, namely the
        individual index and the individual pages.

        @param: the_lang  -- The lang to process
        @param: the_title -- The title page related to the language
        """
        default_types = [name[1] for name in EventType._DATAMAP]  # Initial local name
        custom_types = [name for name in self.r_db.get_event_types()]
        sorted_default_types = sorted([*default_types, *custom_types])
        selected = self.report.options["selected_evts"]

        def in_standard_event(value):
            result = False
            for evt in EventType._DATAMAP:
                if value == evt[1]:
                    result = True
            return result

        saved_evts = []
        for evt in selected:
            index = 0
            for typ in sorted_default_types:
                if index == int(evt) and not in_standard_event(typ):
                    self.events.append(typ)
                if index == int(evt):
                    # Save the local name
                    saved_evts.append(typ)
                index += 1
        default_types = [name for name in EventType._DATAMAP]  # Initial local name
        for evt in saved_evts:
            index = 0
            for typ in default_types:
                if typ[1] == evt:
                    self.events.append(typ[2])
                index += 1
        if "All Events" not in self.events:
            self.events.append("All Events")  # All events
        self.event_types = sorted([*default_types])

        self.heatmaplistpage(self.report, the_lang, the_title, self.events)
        progress_title = self.report.pgrs_title(the_lang)
        message = _("Creating heatmap pages for events")
        nbs = len(self.events)
        with self.r_user.progress(progress_title, message, nbs) as step:
            for event_type in sorted(self.events):
                step()
                self.heatmappage(
                    self.report, the_lang, the_title, event_type=event_type
                )
            step()

    def heatmaplistpage(self, report, the_lang, the_title, events):
        """Heatmap report class."""
        date = 0
        output_file, sio = self.report.create_file("heatmaps")
        self.uplink = False
        result = self.write_header(self._("Heatmaps"))
        indlistpage, dummy_head, dummy_body, outerwrapper = result
        self.cur_fname = self.report.cur_fname

        # begin events division
        with Html("div", class_="content", id="Events") as eventlist:
            outerwrapper += eventlist
            # Individual List page message
            msg = self._(
                "The next section contains an index of all the events for an Heatmap map."
            )
            eventlist += Html("p", msg, id="description")

            # Assemble the alphabeticIndex
            index = AlphabeticIndex(self.rlocale)
            for event in self.events:
                index.addRecord(self._(event), None)

            # Extract the buckets from the index
            index_list = []
            index.resetBucketIterator()
            while index.nextBucket():
                if index.bucketRecordCount != 0:
                    index_list.append(index.bucketLabel)
            # Output the navigation
            href_label = "event"
            alpha_nav = alphabet_navigation(
                index_list,
                self.rlocale,
                rtl=self.dir,
            )
            if alpha_nav:
                eventlist += alpha_nav

            # begin events table
            with Html(
                "table", class_="infolist primobjlist eventlist " + self.dir
            ) as table:
                eventlist += table

                # begin table head
                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                trow.extend(
                    Html("th", label, class_=colclass, inline=True)
                    for (label, colclass) in [
                        [self._("Letter"), "ColumnLetter"],
                        [self._("Name", "Event Name"), "ColumnName"],
                        [self._("Description"), "ColumnDescription"],
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
                        # Assemble all the events in this bucket into a dict for
                        # sorting
                        event_dict = {}
                        first_event = True
                        while index.nextRecord():
                            event_name = index.recordName
                            value = index.recordData
                            event_dict[event_name] = value

                            letter = bucket_letter
                            for event in events:
                                if self._(event) != event_name:
                                    continue
                                trow = Html("tr")
                                tbody += trow
                                tcell = Html("td", class_="ColumnLetter", inline=True)
                                trow += tcell
                                if first_event:
                                    first_event = False
                                    trow.attr = 'class = "BeginLetter"'
                                    ttle = (
                                        self._("Places beginning " "with letter %s")
                                        % letter
                                    )
                                    tcell += Html(
                                        "a",
                                        letter,
                                        name="%s_%s" % (href_label, letter),
                                        title=ttle,
                                        id_=bucket_link,
                                    )
                                else:
                                    tcell += "&nbsp;"
                                trow += Html(
                                    "td",
                                    self.heatmap_link(event),
                                    class_="ColumnName",
                                )
                                dname = self._(
                                    "Heatmap for %s within the selected filter"
                                ) % self._(event)
                                trow.extend(
                                    Html(
                                        "td",
                                        data or "&nbsp;",
                                        class_=colclass,
                                        inline=True,
                                    )
                                    for (colclass, data) in [
                                        ["ColumnDescription", dname],
                                    ]
                                )

        people = self.report.options["selected_surnames"]
        if people:
            # begin surnames division
            with Html("div", class_="content", id="Surnames") as surnamelist:
                outerwrapper += surnamelist
                msg = self._(
                    "The next section contains an index of all the surnames for an Heatmap map."
                )
                surnamelist += Html("p", msg, id="description")
                selected_people = get_surnames_list(self.r_db)
                index1 = AlphabeticIndex(self.rlocale)
                surnames = []
                for item in people:
                    index = 0
                    for value in sorted(
                        selected_people, key=lambda x: x[1], reverse=True
                    ):
                        if int(item) == index:
                            surnames.append(value[0])
                            index1.addRecord(value[0], None)
                            self.heatmappage(
                                self.report, the_lang, the_title, surname=value
                            )
                        index += 1

                # Extract the buckets from the index
                index_list = []
                index1.resetBucketIterator()
                while index1.nextBucket():
                    if index1.bucketRecordCount != 0:
                        index_list.append(index1.bucketLabel)
                # Output the navigation
                href_label = "surname"
                alpha_nav = alphabet_navigation(
                    index_list,
                    self.rlocale,
                    rtl=self.dir,
                )
                if alpha_nav:
                    surnamelist += alpha_nav

                # begin surnames table1
                with Html(
                    "table", class_="infolist primobjlist surnamelist " + self.dir
                ) as table1:
                    surnamelist += table1

                    # begin table1 head
                    thead = Html("thead")
                    table1 += thead

                    trow = Html("tr")
                    thead += trow

                    trow.extend(
                        Html("th", label, class_=colclass, inline=True)
                        for (label, colclass) in [
                            [self._("Letter"), "ColumnLetter"],
                            [self._("Surname", "Name"), "ColumnName"],
                            [self._("Description"), "ColumnDescription"],
                        ]
                    )

                    # begin table1 body
                    tbody = Html("tbody")
                    table1 += tbody

                    # For each bucket, output the places in that bucket
                    index1.resetBucketIterator()
                    output = []
                    dup_index = 0
                    while index1.nextBucket():
                        if index1.bucketRecordCount != 0:
                            bucket_letter = index1.bucketLabel
                            bucket_link = bucket_letter
                            if bucket_letter in output:
                                bucket_link = "%s (%i)" % (bucket_letter, dup_index)
                                dup_index += 1
                            output.append(bucket_letter)
                            # Assemble all the surnames in this bucket into a dict for
                            # sorting
                            surname_dict = {}
                            first_surname = True
                            while index1.nextRecord():
                                surname_name = index1.recordName
                                value = index1.recordData
                                surname_dict[surname_name] = value

                                letter = bucket_letter
                                for surname in surnames:
                                    if self._(surname) != surname_name:
                                        continue
                                    trow = Html("tr")
                                    tbody += trow
                                    tcell = Html(
                                        "td", class_="ColumnLetter", inline=True
                                    )
                                    trow += tcell
                                    if first_surname:
                                        first_surname = False
                                        trow.attr = 'class = "BeginLetter"'
                                        ttle = (
                                            self._("Places beginning " "with letter %s")
                                            % letter
                                        )
                                        tcell += Html(
                                            "a",
                                            letter,
                                            name="%s_%s" % (href_label, letter),
                                            title=ttle,
                                            id_=bucket_link,
                                        )
                                    else:
                                        tcell += "&nbsp;"
                                    trow += Html(
                                        "td",
                                        self.heatmap_link(surname),
                                        class_="ColumnName",
                                    )
                                    dname = self._(
                                        "Heatmap for %s within the selected filter"
                                    ) % self._(surname)
                                    trow.extend(
                                        Html(
                                            "td",
                                            data or "&nbsp;",
                                            class_=colclass,
                                            inline=True,
                                        )
                                        for (colclass, data) in [
                                            ["ColumnDescription", dname],
                                        ]
                                    )

        sel_tags = self.report.options["selected_tags"]
        if sel_tags:
            # begin tags division
            with Html("div", class_="content", id="Surnames") as taglist:
                outerwrapper += taglist
                msg = self._(
                    "The next section contains an index of all the tags for an Heatmap map."
                )
                taglist += Html("p", msg, id="description")
                selected_tags = get_tags_list(self.r_db)
                index2 = AlphabeticIndex(self.rlocale)
                tags = []
                for item in sel_tags:
                    index = 0
                    for value in selected_tags:
                        if int(item) == index:
                            tags.append(value[0])
                            index2.addRecord(value[0], None)
                            self.heatmappage(
                                self.report, the_lang, the_title, tag=value
                            )
                        index += 1

                # Extract the buckets from the index
                index_list = []
                index2.resetBucketIterator()
                while index2.nextBucket():
                    if index2.bucketRecordCount != 0:
                        index_list.append(index2.bucketLabel)
                # Output the navigation
                href_label = "tag"
                alpha_nav = alphabet_navigation(
                    index_list,
                    self.rlocale,
                    rtl=self.dir,
                )
                if alpha_nav:
                    taglist += alpha_nav

                # begin tags table1
                with Html(
                    "table", class_="infolist primobjlist taglist " + self.dir
                ) as table1:
                    taglist += table1

                    # begin table1 head
                    thead = Html("thead")
                    table1 += thead

                    trow = Html("tr")
                    thead += trow

                    trow.extend(
                        Html("th", label, class_=colclass, inline=True)
                        for (label, colclass) in [
                            [self._("Letter"), "ColumnLetter"],
                            [self._("Tag"), "ColumnName"],
                            [self._("Description"), "ColumnDescription"],
                        ]
                    )

                    # begin table1 body
                    tbody = Html("tbody")
                    table1 += tbody

                    # For each bucket, output the places in that bucket
                    index2.resetBucketIterator()
                    output = []
                    dup_index = 0
                    while index2.nextBucket():
                        if index2.bucketRecordCount != 0:
                            bucket_letter = index2.bucketLabel
                            bucket_link = bucket_letter
                            if bucket_letter in output:
                                bucket_link = "%s (%i)" % (bucket_letter, dup_index)
                                dup_index += 1
                            output.append(bucket_letter)
                            # Assemble all the tags in this bucket into a dict for
                            # sorting
                            tag_dict = {}
                            first_tag = True
                            while index2.nextRecord():
                                tag_name = index2.recordName
                                value = index2.recordData
                                tag_dict[tag_name] = value

                                letter = bucket_letter
                                for tag in tags:
                                    if self._(tag) != self._(tag_name):
                                        continue
                                    trow = Html("tr")
                                    tbody += trow
                                    tcell = Html(
                                        "td", class_="ColumnLetter", inline=True
                                    )
                                    trow += tcell
                                    if first_tag:
                                        first_tag = False
                                        trow.attr = 'class = "BeginLetter"'
                                        ttle = (
                                            self._("Places beginning " "with letter %s")
                                            % letter
                                        )
                                        tcell += Html(
                                            "a",
                                            letter,
                                            name="%s_%s" % (href_label, letter),
                                            title=ttle,
                                            id_=bucket_link,
                                        )
                                    else:
                                        tcell += "&nbsp;"
                                    trow += Html(
                                        "td",
                                        self.heatmap_link(tag),
                                        class_="ColumnName",
                                    )
                                    dname = self._(
                                        "Heatmap for %s within the selected filter"
                                    ) % self._(tag)
                                    trow.extend(
                                        Html(
                                            "td",
                                            data or "&nbsp;",
                                            class_=colclass,
                                            inline=True,
                                        )
                                        for (colclass, data) in [
                                            ["ColumnDescription", dname],
                                        ]
                                    )

        # create footer section
        footer = self.write_footer(date)
        outerwrapper += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.report.cur_fname = self.cur_fname
        self.xhtml_writer(indlistpage, output_file, sio, date)

    def heatmappage(
        self, report, the_lang, the_title, event_type=None, surname=None, tag=None
    ):
        """Heatmap report class."""
        date = 0
        self.places = []
        self.tracelife = []
        self.count = 0
        self.vallat = float(0.0)
        self.vallon = float(0.0)
        self.uplink = True
        if event_type:
            self.lookingfor = self._(event_type)
            output_file, sio = self.report.create_file(
                event_type.replace(" ", ""), "heat"
            )
            result = self.write_header(event_type)
            events = self.get_all_events(event_type)
            msg = self._(
                "This section contains the map for all people with the event: {event_type} ({selected_filter})"
            ).format(event_type=event_type, selected_filter=self.selected_filter)
            if not len(self.places):
                msg += self._(" which has no event for the selected filter.")
            tracelife = self.create_tracelife(self.places, events)
        elif surname:
            selected = []
            output_file, sio = self.report.create_file(
                surname[0].replace(" ", ""), "heat"
            )
            result = self.write_header(surname[0])
            selected = self.get_surname_events(surname[2])
            msg = self._(
                "This section contains the map of all events for: {surname} ({selected_filter})"
            ).format(surname=surname[0], selected_filter=self.selected_filter)
            if not len(self.places):
                msg += self._(" which has no event for the selected filter.")
            tracelife = self.create_tracelife(self.places, selected)
        elif tag:
            output_file, sio = self.report.create_file(tag[0].replace(" ", ""), "heat")
            result = self.write_header(tag[0])
            selected = self.get_tag_events(tag)
            msg = self._(
                "This section contains the map for all people, events with the tag: {tag} ({selected_filter})"
            ).format(tag=tag[0], selected_filter=self.selected_filter)
            if not len(self.places):
                msg += self._(" which has no event for the selected filter.")
            tracelife = self.create_tracelife(self.places, tag)
        heatmappage, head, dummy_body, outerwrapper = result

        minx, maxx = Decimal("0.00000001"), Decimal("0.00000001")
        miny, maxy = Decimal("0.00000001"), Decimal("0.00000001")
        xwidth, yheight = [], []
        midx_, midy_, dummy_spanx, spany = [None] * 4

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

        # add MapService specific javascript code. We use only OSM maps.
        src_js = "https://"
        src_js += "ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"
        head += Html("script", type="text/javascript", src=src_js, inline=True)
        olv = self.report.options["ol_version"]
        build = "legacy"
        if olv < "v7.0.0":
            build = "build"
        if olv == "latest":
            build = "legacy"
        src_js = ("https://openlayers.org/en/" "%(ver)s/%(bld)s/ol.js") % {
            "ver": olv,
            "bld": build,
        }
        head += Html("script", type="text/javascript", src=src_js, inline=True)
        css = "legacy"
        if olv < "v7.0.0":
            css = "css"
        if olv == "latest":
            css = "legacy"
        url = ("https://openlayers.org/en/" "%(ver)s/%(css)s/ol.css") % {
            "ver": olv,
            "css": css,
        }
        head += Html("link", href=url, type="text/css", rel="stylesheet")

        src_js = ("https://openlayers.org/en/" "%(ver)s/%(bld)s/ol.js") % {
            "ver": olv,
            "bld": build,
        }
        head += Html("script", href=url, type="text/javascript", rel="stylesheet")

        # begin events division
        with Html("div", class_="content", id="events") as taglist:
            outerwrapper += taglist
            # Individual List page message
            taglist += Html("p", msg, id="description")

        # this is the style element where the Map is held in the CSS...
        with Html("div", id="map_canvas") as canvas:
            outerwrapper += canvas

        # add div for popups.
        with Html("div", id="popup", class_="ol-popup", inline=True) as popup:
            outerwrapper += popup
            popup += Html("a", href="#", id="popup-closer", class_="ol-popup-closer")
            popup += Html("div", id="popup-title", class_="ol-popup-title")
            popup += Html("div", id="popup-content", class_="ol-popup-content")
        with Html("div", id="tooltip", class_="ol-popup", inline=True) as tooltip:
            outerwrapper += tooltip
            tooltip += Html("div", id="tooltip-content")

        start_zoom = self.report.options["start_zoom"]

        # Collect heatmap coordinates
        heatmap_data = [place.to_list() for place in self.places]

        # Substitute the HTML template source code with heatmap report data
        if self.count:
            start_lat = self.vallat / self.count
            start_lon = self.vallon / self.count
        else:
            start_lat = 0.0
            start_lon = 0.0

        # begin javascript inline code...
        with Html(
            "script",
            deter="deter",
            style="width =100%; height =100%;",
            type="text/javascript",
            indent=False,
        ) as jsc:
            outerwrapper += jsc

            # Link to Gramps marker
            fname = "/".join(["images", "marker.png"])
            marker_path = self.report.build_url_image(
                "marker.png", "images", self.uplink
            )

            latitude = start_lat
            longitude = start_lon
            jsc += MARKER_PATH % marker_path
            # we are using OpenStreetMap
            if midy_ is None:
                jsc += OSM_MARKERS % (
                    "heatmap",
                    tracelife,
                    longitude,
                    latitude,
                    start_zoom,
                    self.radius,
                    self.blur,
                )
            else:
                jsc += OSM_MARKERS % (
                    "heatmap",
                    tracelife,
                    midy_,
                    midx_,
                    start_zoom,
                    self.radius,
                    self.blur,
                )
            jsc += OPENLAYER

        # create footer section
        footer = self.write_footer(date)
        outerwrapper += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(heatmappage, output_file, sio, date)

    def get_all_events(self, event_type):
        """Get all relevant events from the current filter."""
        if self.lookingfor == self._("All Events"):
            for event_hdl in sorted(self.report.obj_dict[Event]):
                event = self.r_db.get_event_from_handle(event_hdl)
                self.select_event(event, evt=None)
        else:
            for index, name in enumerate(self.event_types):
                for event_hdl in sorted(self.report.obj_dict[Event]):
                    event = self.r_db.get_event_from_handle(event_hdl)
                    self.select_event(event, evt=event_type)

    def get_tag_events(self, tag):
        """Get all relevant tags."""
        selected = []
        for handle in self.report.obj_dict[Person]:
            person = self.r_db.get_person_from_handle(handle)
            if person:
                tags_list = person.get_tag_list()
                if tag[1] in tags_list:
                    selected.append((Person, handle))
                    self.get_place(person.get_event_ref_list())
        for handle in self.report.obj_dict[Family]:
            family = self.r_db.get_family_from_handle(handle)
            if family:
                tags_list = family.get_tag_list()
                if tag[1] in tags_list:
                    selected.append((Family, handle))
                    fam_evt_ref_list = family.get_event_ref_list()
                    if fam_evt_ref_list:
                        self.get_place(fam_evt_ref_list)
        for handle in self.report.obj_dict[Event]:
            event = self.r_db.get_event_from_handle(handle)
            if event:
                tags_list = event.get_tag_list()
                if tag[1] in tags_list:
                    selected.append((Event, handle))
                    self.get_place([event])
        return selected

    def get_surname_events(self, person_handle):
        selected_surname = []
        for handle in person_handle:
            if handle not in self.report.obj_dict[Person]:
                continue
            selected_surname.append(handle)
            events = self.get_events(handle)
            if events:
                self.get_place(events)
        return selected_surname

    def select_event(self, event, evt=None):
        if evt:
            if event.get_type().xml_str() == evt:
                handle = event.get_place_handle()
                if handle:
                    place = self.r_db.get_place_from_handle(handle)
                    self.check_place(place, event)
        else:
            handle = event.get_place_handle()
            if handle:
                place = self.r_db.get_place_from_handle(handle)
                self.check_place(place, event)

    def get_events(self, person_h, force=False):
        """Get all relevant events of a person."""
        person = self.r_db.get_person_from_handle(person_h)
        event_list = []
        for event_ref in person.get_event_ref_list():
            event = self.r_db.get_event_from_handle(event_ref.ref)
            event_list.append(event_ref)
        # select all events for the associated families
        fam_handle_list = person.get_family_handle_list()
        if fam_handle_list:
            for family_handle in fam_handle_list:
                family = self.r_db.get_family_from_handle(family_handle)
                if family:
                    fam_evt_ref_list = family.get_event_ref_list()
                    if fam_evt_ref_list:
                        for evt_ref in fam_evt_ref_list:
                            event_list.append(evt_ref)
        return event_list

    def get_place(self, events):
        """Get an event places and call check_place."""
        for event_ref in events:
            if not isinstance(event_ref, Event):
                event = self.r_db.get_event_from_handle(event_ref.ref)
            else:
                event = event_ref
            handle = event.get_place_handle()
            if handle:
                place = self.r_db.get_place_from_handle(handle)
                self.check_place(place, event)

    def check_place(self, place, event):
        """Check the place for latitude and longitude."""
        lat, lon = conv_lat_lon(place.get_latitude(), place.get_longitude(), "D.D8")
        name = place.get_gramps_id()
        placetitle = _pd.display(self.r_db, place, fmt=0)
        eid = event.get_gramps_id()

        if lat and lon:
            for placex in self.places:
                if name == placex.name:
                    placex.count += 1
                    if not (eid in placex.events):
                        placex.add_event(event.get_gramps_id())
                        self.vallat += float(lat)
                        self.vallon += float(lon)
                        self.count += 1
            found = None
            for placex in self.places:
                if name == placex.name:
                    found = placex
            if not found:
                self.places.append(HeatmapPlace(name, lat, lon, 1, placetitle))
                for placex in self.places:
                    if name == placex.name:
                        self.count += 1
                        placex.add_event(event.get_gramps_id())
                        self.vallat += float(lat)
                        self.vallon += float(lon)
        else:
            for place_ref in place.get_placeref_list():
                place_new = self.r_db.get_place_from_handle(place_ref.ref)
                self.check_place(place_new, event)

    def create_tracelife(self, places, handles):
        number_markers = len(places)
        places_list = []
        for place in places:
            places_list.append(place.get_all())
        sorted_places = sorted(places_list, key=lambda x: x[0])
        placetitle = "unknown"
        tracelife = "["
        if number_markers > 0:
            for index in range(0, number_markers):
                (name, latitude, longitude, count, placetitle, events) = sorted_places[
                    index
                ]
                debug = 0
                links = "''"
                for event_ID in events:
                    event = self.r_db.get_event_from_gramps_id(event_ID)
                    if event:
                        handle = event.get_place_handle()
                        if handle:
                            place = self.r_db.get_place_from_handle(handle)
                            placename = _pd.display(self.r_db, place, fmt=0)
                            p_fname = (
                                self.report.build_url_fname(handle, "plc", self.uplink)
                                + self.ext
                            )
                            placetitle = ' <a href="%s">%s</a>' % (p_fname, placename)

                        bkref_list = self.report.bkref_dict[Event][event.handle]
                        for ref in bkref_list:
                            (bkref_class, bkref_hdle, role) = ref
                            if bkref_class == Person:
                                person = self.r_db.get_person_from_handle(bkref_hdle)
                                links = self.__create_links_tracelife(
                                    links,
                                    person,
                                    placetitle,
                                    latitude,
                                    longitude,
                                    ref,
                                    event,
                                )
                debug = 0
                tracelife = self._create_family_tracelife(
                    tracelife, placetitle, latitude, longitude, links
                )
            tracelife += "]"
        else:
            tracelife += "]"
        return tracelife

    def _create_family_tracelife(
        self, tracelife, placetitle, latitude, longitude, links
    ):
        """
        creates individual family tracelife map events

        @param: tracelife  -- The family event list
        @param: placetitle -- The place title to add to the event list
        @param: latitude   -- The latitude for this place
        @param: longitude  -- The longitude for this place
        @param: links      -- Used to add links in the popup html page
        """
        tracelife += """[%f, %f, \'%s\', %s],""" % (
            float(longitude),
            float(latitude),
            placetitle.replace("'", "\\'"),
            links,
        )
        return tracelife

    def __create_links_tracelife(
        self, links, person, placetitle, latitude, longitude, ref, event
    ):
        """
        creates individual family events for a marker

        @param: links      -- Used to add links in the popup html page
        @param: person     -- family for this person
        @param: placetitle -- The place title to add to the event list
        @param: latitude   -- The latitude for this place
        @param: longitude  -- The longitude for this place
        @param: event      -- The event for which we are working
        @param: ref        -- The back reference and role for the event
        """
        if not person:
            return links
        url_fct = self.report.build_url_fname_html
        ppl_fct = self.r_db.get_person_from_handle
        ln_str = "<a href='%s' title='%s' target='_self'>%s</a>"
        ppl_lnk = ""
        (bkref_class, bkref_hdle, role) = ref
        if role == "Marriage" or role == "Divorce" or role == "Family":
            url = url_fct(bkref_hdle, "fam", self.uplink)
            fam_fct = self.r_db.get_family_from_handle
            fam = fam_fct(bkref_hdle)
            fam_name = self.report.get_family_name(fam)
            ppl_lnk = ln_str % (url, fam.get_gramps_id(), fam_name)
            if "<p>" in links:
                links += ' + "<br>%s"' % ppl_lnk
            else:
                links = '"<p>%s"' % ppl_lnk
        elif bkref_class == Person:
            pers = ppl_fct(bkref_hdle)
            url = url_fct(bkref_hdle, "ppl", self.uplink)
            ppl_lnk = ln_str % (
                url,
                pers.get_gramps_id(),
                self.get_name(pers).replace('"', ""),
            )
            evt_type = self._(event.get_type().xml_str())
            evt_date = self.rlocale.get_date(event.get_date_object())
            if self.report.options["inc_events"]:
                url = url_fct(event.get_handle(), "evt", self.uplink)
                evt_lnk = ln_str % (url, evt_date, evt_type)
            else:
                evt_lnk = evt_type
            if evt_date:
                evt_lnk += " (" + evt_date + ")"
            if "<p>" in links:
                links += ' + "<br>%s"' % (ppl_lnk + self._(":") + " " + evt_lnk)
            else:
                links = '"<p>%s"' % (ppl_lnk + self._(":") + " " + evt_lnk)
        return links
