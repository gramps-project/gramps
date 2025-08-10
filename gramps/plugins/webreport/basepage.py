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
# Copyright (C) 2018       Theo van Rijn
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
    BasePage - super class for producing a web page. This class is instantiated
    once for each page. Provdes various common functions.
"""
# ------------------------------------------------
# python modules
# ------------------------------------------------
from functools import partial
import os
import calendar
import copy
import datetime
from decimal import getcontext
from unicodedata import normalize

# ------------------------------------------------
# Set up logging
# ------------------------------------------------
import logging

from gi.repository import Gdk

# ------------------------------------------------
# Gramps module
# ------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import (
    FamilyRelType,
    NoteType,
    NameType,
    Person,
    UrlType,
    Name,
    PlaceType,
    EventRoleType,
    Source,
    Attribute,
    Media,
    Repository,
    Event,
    Family,
    Citation,
    Place,
    Date,
)
from gramps.gen.lib.date import Today
from gramps.gen.mime import is_image_type
from gramps.gen.const import PROGRAM_NAME, URL_HOMEPAGE
from gramps.version import VERSION
from gramps.gen.plug.report import Bibliography
from gramps.gen.plug.report import utils
from gramps.gen.utils.config import get_researcher
from gramps.gen.utils.string import conf_strings
from gramps.gen.utils.file import media_path_full
from gramps.gen.utils.thumbnails import get_thumbnail_path
from gramps.gen.display.name import displayer as _nd
from gramps.gen.display.place import displayer as _pd
from gramps.plugins.lib.libhtmlconst import _CC
from gramps.gen.utils.db import (
    get_birth_or_fallback,
    get_death_or_fallback,
    get_event_person_referents,
    get_event_family_referents,
)
from gramps.gen.datehandler import parser as _dp
from gramps.plugins.lib.libhtml import Html, xml_lang
from gramps.plugins.lib.libhtmlbackend import HtmlBackend, process_spaces
from gramps.gen.utils.place import conv_lat_lon, coord_formats
from gramps.gen.utils.location import get_main_location
from gramps.plugins.webreport.common import (
    _NAME_STYLE_DEFAULT,
    HTTP,
    HTTPS,
    add_birthdate,
    CSS,
    html_escape,
    _NARRATIVESCREEN,
    _NARRATIVEPRINT,
    FULLCLEAR,
    _has_webpage_extension,
)

_ = glocale.translation.sgettext
LOG = logging.getLogger(".NarrativeWeb")
getcontext().prec = 8

TOGGLE = """
<script type="text/javascript">
function toggleContent(elem, icon) {
  // Get the DOM reference
  var contentId = document.getElementById(elem);
  var icon = document.getElementById(icon);
  // Toggle
  if (contentId.style.display == "block") {
    contentId.style.display = "none";
    icon.className = 'icon icon-close';
  } else {
    contentId.style.display = "block";
    icon.className = 'icon icon-open';
  };
}
</script>
"""

GOTOTOP = """
<script>
//Get the button
var gototop = document.getElementById("gototop");

// When the user scrolls down 200px from the top of the document,
// show the button
window.onscroll = function() {scroll()};

function scroll() {
  if (document.body.scrollTop > 200 ||
      document.documentElement.scrollTop > 200) {
    gototop.style.display = "block";
  } else {
    gototop.style.display = "none";
  }
}

// When the user clicks on the button, scroll to the top of the document
function GoToTop() {
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
}
</script>
"""


class BasePage:
    """
    Manages all the functions, variables, and everything needed
    for all of the classes contained within this plugin
    """

    def __init__(self, report, the_lang, the_title, gid=None):
        """
        @param: report    -- The instance of the main report class for
                             this report
        @param: the_lang  -- Is the lang to process
        @param: the_title -- Is the title of the web page
        @param: gid       -- The family gramps ID
        """
        self.uplink = False
        # class to do conversion of styled notes to html markup
        self._backend = HtmlBackend()
        self._backend.build_link = report.build_link

        self.report = report
        self.r_db = report.database
        self.r_user = report.user
        self.title_str = the_title
        self.gid = gid
        self.bibli = Bibliography()
        self.the_lang = the_lang
        self.the_title = the_title
        self.not_holiday = True

        self.page_title = ""

        self.author = get_researcher().get_name()
        if self.author:
            self.author = self.author.replace(",,,", "")

        # TODO. All of these attributes are not necessary, because we have
        # also the options in self.options.  Besides, we need to check which
        # are still required.
        self.html_dir = report.options["target"]
        self.ext = report.options["ext"]
        self.noid = not report.options["inc_id"]
        self.inc_tags = report.options["inc_tags"]
        self.linkhome = report.options["linkhome"]
        self.create_media = report.options["gallery"]
        self.create_unused_media = report.options["unused"]
        self.create_thumbs_only = report.options["create_thumbs_only"]
        self.create_images_index = report.options["create_images_index"]
        self.create_thumbs_index = report.options["create_thumbs_index"]
        self.inc_families = report.options["inc_families"]
        self.inc_events = report.options["inc_events"]
        self.inc_other_roles = report.options["inc_other_roles"]
        self.usecms = report.options["usecms"]
        self.prevnext = report.options["prevnext"]
        self.target_uri = report.options["cmsuri"]
        self.usecal = report.options["usecal"]
        self.extrapage = report.options["extrapage"]
        self.extrapagename = report.options["extrapagename"]
        self.familymappages = None
        self.reference_sort = report.options["reference_sort"]
        if the_lang:
            self.rlocale = report.set_locale(the_lang)
        else:
            self.rlocale = report.set_locale(report.options["trans"])
        self.dir = "rtl" if self.rlocale.rtl_locale else "ltr"
        self._ = self.rlocale.translation.sgettext
        self.colon = self._(":")  # Translators: needed for French, else ignore

        if report.options["securesite"]:
            self.secure_mode = HTTPS
        else:
            self.secure_mode = HTTP
        self.target_cal_uri = "cal/%s/index" % Today().get_year()

    # Functions used when no Web Page plugin is provided
    def add_instance(self, *param):
        """
        Add an instance
        """
        pass

    def display_pages(self, the_lang, the_title):
        """
        Display the pages
        """
        pass

    def sort_by_event_date(self, handle):
        """Used to sort events by date."""
        event = self.r_db.get_event_from_handle(handle.ref)
        date = event.get_date_object().to_calendar("gregorian")
        # we need to remove abt, bef, aft, ...
        if date.get_year() > 0:
            if len(str(date).split(" ")) > 1:
                modif = str(date).split(" ")[0]
                year = date.get_year()
                month = date.get_month()
                if year == 0:
                    year = datetime.date.today().year
                if month == 0:
                    month = 1
                day = date.get_day()
                if day == 0:
                    day = 1
                ddd = datetime.date(year, month, day)
                if modif == "bef":
                    ddd = ddd - datetime.timedelta(days=1)
                elif modif == "aft":
                    ddd = ddd + datetime.timedelta(days=1)
                date = Date(ddd.year, ddd.month, ddd.day)
            return date
        else:
            # if we have no date, we'll put the event at the
            # end of the list
            return Date(9999, 1, 1)

    def sort_on_name_and_grampsid(self, handle):
        """Used to sort on name and gramps ID."""
        person = self.r_db.get_person_from_handle(handle)
        name = normalize("NFD", _nd.display(person))
        return (name, person.get_gramps_id())

    def sort_on_given_and_birth(self, handle):
        """Used to sort on given name and birth date."""
        person = self.r_db.get_person_from_handle(handle)
        name = _nd.display_given(person)
        bd_event = get_birth_or_fallback(self.r_db, person)
        birth = ""
        if bd_event:
            birth_iso = str(bd_event.get_date_object()).replace("abt ", "")
            # we need to remove abt, bef, aft, ...
            birth = birth_iso.replace("aft ", "").replace("bef ", "")
        return (name, birth)

    def sort_on_grampsid(self, event_ref):
        """
        Sort on gramps ID
        """
        evt = self.r_db.get_event_from_handle(event_ref.ref)
        return evt.get_gramps_id()

    def copy_thumbnail(self, handle, photo, region=None):
        """
        Given a handle (and optional region) make (if needed) an
        up-to-date cache of a thumbnail, and call report.copy_file
        to copy the cached thumbnail to the website.
        Return the new path to the image.

        @param: handle -- The handle for this thumbnail
        @param: photo  -- The image related to this thumbnail
        @param: region -- The image region to associate
        """
        to_dir = self.report.build_path("thumb", handle)
        to_path = os.path.join(to_dir, handle) + (
            ("%d,%d-%d,%d.png" % region) if region else ".png"
        )

        if photo.get_mime_type():
            full_path = media_path_full(self.r_db, photo.get_path())
            from_path = get_thumbnail_path(full_path, photo.get_mime_type(), region)
            if not os.path.isfile(from_path):
                from_path = CSS["Document"]["filename"]
        else:
            from_path = CSS["Document"]["filename"]
        if self.the_lang is None or self.the_lang == self.report.languages[0][0]:
            # if multi languages, copy the thumbnail only for the first lang.
            self.report.copy_file(from_path, to_path)
        return to_path

    def get_nav_menu_hyperlink(self, url_fname, nav_text, cal=0):
        """
        Returns the navigation menu hyperlink
        """
        uplink = self.uplink
        sub_cal = cal if cal > 0 else 1

        # check for web page file extension?
        if not _has_webpage_extension(url_fname):
            url_fname += self.ext

        # get menu item url and begin hyperlink...
        if self.usecms:
            if self.the_lang:
                url_name = "/".join([self.target_uri, self.the_lang, url_fname])
            else:
                url_name = "/".join([self.target_uri, url_fname])
        else:
            if cal > 0:
                url_fname = "/".join(([".."] * sub_cal + [url_fname]))
            url_name = self.report.build_url_fname(url_fname, None, uplink)
        return Html("a", nav_text, href=url_name, title=nav_text, inline=True)

    def get_column_data(self, unordered, data_list, column_title):
        """
        Returns the menu column for Drop Down Menus and Drop Down Citations
        """
        if not data_list:
            return

        elif len(data_list) == 1:
            url_fname, nav_text = data_list[0][0], data_list[0][1]
            hyper = self.get_nav_menu_hyperlink(url_fname, nav_text)
            unordered.extend(Html("li", hyper, inline=True))
        else:
            col_list = Html("li") + (
                Html("a", column_title, href="#", title=column_title, inline=True)
            )
            unordered += col_list

            unordered1 = Html("ul")
            col_list += unordered1

            for url_fname, nav_text in data_list:
                hyper = self.get_nav_menu_hyperlink(url_fname, nav_text)
                unordered1.extend(Html("li", hyper, inline=True))

    def display_relationships(self, individual, place_lat_long):
        """
        Displays a person's relationships ...

        @param: family_handle_list -- families in this report database
        @param: place_lat_long     -- for use in Family Map Pages.
                                      This will be None if called from
                                      Family pages, which do not create
                                      a Family Map
        """
        family_list = individual.get_family_handle_list()
        if not family_list:
            return None

        with Html("div", class_="subsection", id="families") as section:
            with self.create_toggle("families") as h4_head:
                section += h4_head
                h4_head += self._("Families")

            table_class = "infolist"
            if len(family_list) > 1:
                table_class += " fixed_subtables"
            disp = "none" if self.report.options["toggle"] else "block"
            with Html(
                "table",
                class_=table_class,
                id="toggle_families",
                style="display:%s" % disp,
            ) as table:
                section += table

                for family_handle in family_list:
                    family = self.r_db.get_family_from_handle(family_handle)
                    if family:
                        fam_name = self.report.get_family_name(family)
                        link = self.family_link(
                            family_handle,
                            fam_name,
                            gid=family.get_gramps_id(),
                            uplink=True,
                        )
                        link1 = Html("H4", link, class_="subsection")
                        trow = Html("tr", class_="BeginFamily") + (
                            Html(
                                "td",
                                link1,
                                class_="ColumnValue",
                                colspan=3,
                                inline=True,
                            )
                        )
                        table += trow
                        # find the spouse of the principal individual and
                        # display that person
                        sp_hdl = utils.find_spouse(individual, family)
                        if sp_hdl:
                            spouse = self.r_db.get_person_from_handle(sp_hdl)
                            if spouse:
                                table += self.display_spouse(
                                    spouse, family, place_lat_long
                                )

                        details = self.display_family_details(family, place_lat_long)
                        if details is not None:
                            table += details
        return section

    def display_family_relationships(self, family, place_lat_long):
        """
        Displays a family's relationships ...

        @param: family         -- the family to be displayed
        @param: place_lat_long -- for use in Family Map Pages. This will
                                  be None if called from Family pages, which
                                  do not create a Family Map
        """
        with Html("div", class_="subsection", id="families") as section:
            section += Html("h4", self._("Families"), inline=True)

            table_class = "infolist"
            with Html("table", class_=table_class) as table:
                section += table
                for person_hdl in [
                    family.get_father_handle(),
                    family.get_mother_handle(),
                ]:
                    person = None
                    if person_hdl:
                        person = self.r_db.get_person_from_handle(person_hdl)
                    if person:
                        table += self.display_spouse(person, family, place_lat_long)

                details = self.display_family_details(family, place_lat_long)
                if details is not None:
                    table += details
        return section

    def display_family_details(self, family, place_lat_long):
        """
        Display details about one family: family events, children, family LDS
        ordinances, family attributes

        @param: family         -- The family
        @param: place_lat_long -- For use in Family Map Pages. This will be
                                  None if called from Family pages, which do
                                  not create a Family Map
        """
        table = None
        birthorder = self.report.options["birthorder"]
        # display family events; such as marriage and divorce...
        family_events = family.get_event_ref_list()
        if family_events:
            trow = Html("tr") + (
                Html("td", "&nbsp;", class_="ColumnType", inline=True),
                Html(
                    "td",
                    self.format_family_events(family_events, place_lat_long),
                    class_="ColumnValue",
                    colspan=2,
                ),
            )
            table = trow

        # If the families pages are not output, display family notes
        if not self.inc_families:
            notelist = family.get_note_list()
            for notehandle in notelist:
                note = self.r_db.get_note_from_handle(notehandle)
                if note:
                    trow = Html("tr") + (
                        Html("td", "&nbsp;", class_="ColumnType", inline=True),
                        Html(
                            "td",
                            self._("Narrative"),
                            class_="ColumnAttribute",
                            inline=True,
                        ),
                        Html(
                            "td", self.get_note_format(note, True), class_="ColumnValue"
                        ),
                    )
                    table = table + trow if table is not None else trow

        childlist = family.get_child_ref_list()
        if childlist:
            trow = Html("tr") + (
                Html("td", self._("Children"), class_="ColumnAttribute", inline=True)
            )
            table = table + trow if table is not None else trow

            tcell = Html("td", class_="ColumnValue Child", close=False, colspan=2)
            trow += tcell

            with Html("table", class_="infolist eventlist " + self.dir) as table2:
                thead = Html("thead")
                table2 += thead
                header = Html("tr")

                header.extend(
                    Html("th", label, class_=colclass, inline=True)
                    for (label, colclass) in [
                        [self._("Name"), "ColumnName"],
                        [self._("Birth Date"), "ColumnDate"],
                        [self._("Death Date"), "ColumnDate"],
                    ]
                )
                thead += header

                # begin table body
                tbody = Html("tbody")
                table2 += tbody

                childlist = [child_ref.ref for child_ref in childlist]

                # add individual's children event places to family map...
                if self.familymappages:
                    for handle in childlist:
                        child = self.r_db.get_person_from_handle(handle)
                        if child:
                            self._get_event_place(child, place_lat_long)

                children = add_birthdate(self.r_db, childlist, self.rlocale)
                if birthorder:
                    children = sorted(children)

                tbody.extend(
                    (
                        Html("tr", inline=True)
                        + Html("td", inline=True, close=False)
                        + self.display_child_link(chandle)
                        + Html("td", birth, inline=True)
                        + Html("td", death, inline=True)
                    )
                    for birth_date, birth, death, chandle in children
                )
            trow += table2

        # family LDS ordinance list
        family_lds_ordinance_list = family.get_lds_ord_list()
        if family_lds_ordinance_list:
            trow = Html("tr") + (
                Html("td", "&nbsp;", class_="ColumnType", inline=True),
                Html(
                    "td", self._("LDS Ordinance"), class_="ColumnAttribute", inline=True
                ),
                Html(
                    "td",
                    self.dump_ordinance(family, "Family", toggle=False),
                    class_="ColumnValue",
                ),
            )
            table = table + trow if table is not None else trow

        # Family Attribute list
        family_attribute_list = family.get_attribute_list()
        if family_attribute_list:
            trow = Html("tr") + (
                Html("td", "&nbsp;", class_="ColumnType", inline=True),
                Html("td", self._("Attributes"), class_="ColumnAttribute", inline=True),
            )
            table = table + trow if table is not None else trow

            tcell = Html("td", class_="ColumnValue")
            trow += tcell

            # we do not need the section variable for this instance
            # of Attributes...
            dummy, attrtable = self.display_attribute_header(toggle=False)
            tcell += attrtable
            self.display_attr_list(family_attribute_list, attrtable)
        return table

    def complete_people(self, tcell, first_person, handle_list, uplink=True):
        """
        completes the person column for classes EventListPage and EventPage

        @param: tcell        -- table cell from its caller
        @param: first_person -- Not used any more, done via css
        @param: handle_list  -- handle list from the backlink of
                                the event_handle
        @param: uplink       -- If True, then "../../../" is inserted in
                                front of the result.
        """
        dummy_first_person = first_person
        for classname, handle in handle_list:
            # personal event
            if classname == "Person":
                tcell += Html(
                    "span",
                    self.new_person_link(handle, uplink),
                    class_="person",
                    inline=True,
                )

            # family event
            else:
                _obj = self.r_db.get_family_from_handle(handle)
                if _obj:
                    # husband and spouse in this example,
                    # are called father and mother
                    husband_handle = _obj.get_father_handle()
                    if husband_handle:
                        hlink = self.new_person_link(husband_handle, uplink)
                    spouse_handle = _obj.get_mother_handle()
                    if spouse_handle:
                        slink = self.new_person_link(spouse_handle, uplink)

                    if spouse_handle and husband_handle:
                        tcell += Html("span", hlink, class_="father", inline=True)
                        tcell += Html("span", slink, class_="mother", inline=True)
                    elif spouse_handle:
                        tcell += Html("span", slink, class_="mother", inline=True)
                    elif husband_handle:
                        tcell += Html("span", hlink, class_="father", inline=True)
        return tcell

    def dump_attribute(self, attr):
        """
        dump attribute for object presented in display_attr_list()

        @param: attr = attribute object
        """
        trow = Html("tr")

        trow.extend(
            Html(
                "td",
                data or "&nbsp;",
                class_=colclass,
                inline=True if (colclass == "Type" or "Sources") else False,
            )
            for (data, colclass) in [
                (str(attr.get_type()), "ColumnType"),
                (attr.get_value(), "ColumnValue"),
                (self.dump_notes(attr.get_note_list(), Attribute), "ColumnNotes"),
                (self.get_citation_links(attr.get_citation_list()), "ColumnSources"),
            ]
        )
        return trow

    def get_citation_links(self, citation_handle_list):
        """
        get citation link from the citation handle list

        @param: citation_handle_list = list of gen/lib/Citation
        """
        text = ""
        for citation_handle in citation_handle_list:
            citation = self.r_db.get_citation_from_handle(citation_handle)
            if citation:
                index, key = self.bibli.add_reference(citation)
                id_ = "%d%s" % (index + 1, key)
                text += ' <a href="#sref%s">%s</a>' % (id_, id_)
        return text

    def get_note_format(self, note, uplink):
        """
        will get the note from the database, and will return either the
        styled text or plain note

        @param: note   -- the note to process
        @param: uplink -- If True, then "../../../" is inserted in
                          front of the result.
        """
        self.report.link_prefix_up = uplink

        text = ""
        if note is not None:
            # retrieve the body of the note
            note_text = note.get()

            # styled notes
            htmlnotetext = self.styled_note(
                note.get_styledtext(),
                note.get_format(),
                contains_html=(note.get_type() == NoteType.HTML_CODE),
            )
            text = htmlnotetext or Html("p", note_text)

        # return text of the note to its callers
        return text

    def styled_note(self, styledtext, styled_format, contains_html=False):
        """
        @param: styledtext    --  assumed a StyledText object to write
        @param: styled_format --  = 0 : Flowed, = 1 : Preformatted
        @param: style_name    --  name of the style to use for default
                                  presentation
        """
        text = str(styledtext)

        if not text:
            return ""

        s_tags = styledtext.get_tags()
        htmllist = Html("div", class_="grampsstylednote")
        if contains_html:
            markuptext = self._backend.add_markup_from_styled(
                text, s_tags, split="\n", escape=False
            )
            htmllist += markuptext
        else:
            markuptext = self._backend.add_markup_from_styled(text, s_tags, split="\n")
            linelist = []
            linenb = 1
            for line in markuptext.split("\n"):
                [line, sigcount] = process_spaces(line, styled_format)
                if sigcount == 0:
                    # The rendering of an empty paragraph '<p></p>'
                    # is undefined so we use a non-breaking space
                    if linenb == 1:
                        linelist.append("&nbsp;")
                    htmllist.extend(Html("p") + linelist)
                    linelist = []
                    linenb = 1
                else:
                    if linenb > 1:
                        linelist[-1] += "<br />"
                    linelist.append(line)
                    linenb += 1
            if linenb > 1:
                htmllist.extend(Html("p") + linelist)
            # if the last line was blank, then as well as outputting
            # the previous para, which we have just done,
            # we also output a new blank para
            if sigcount == 0:
                linelist = ["&nbsp;"]
                htmllist.extend(Html("p") + linelist)
        return htmllist

    def show_tags(self, obj):
        """
        Show all tags associated to an object (Person, Family, Media,...)

        @param: obj -- the object for which we show tags
        """
        tags_text = ""
        if obj is None:
            return tags_text
        tags = []

        for tag_handle in obj.get_tag_list():
            tags.append(self.r_db.get_tag_from_handle(tag_handle))
        if tags and self.report.inc_tags:
            for tag in tags:
                if tags_text:
                    tags_text += ", "
                # convert tag color to html format: #RRGGBB
                rgba = Gdk.RGBA()
                rgba.parse(tag.get_color())
                color = "#%02x%02x%02x" % (
                    int(rgba.red * 255),
                    int(rgba.green * 255),
                    int(rgba.blue * 255),
                )
                tags_text += "<span style='background-color:%s;'>" "%s</span>" % (
                    color,
                    self._(tag.get_name()),
                )
        return tags_text

    def dump_notes(self, notelist, parent=None):
        """
        dump out of list of notes with very little elements of its own

        @param: notelist -- list of notes
        @param: parent   -- The parent object (Person, Family, Media,...)
        """
        if not notelist:
            return Html("div")

        # begin unordered list
        notesection = Html("div")
        idx = 0
        for notehandle in notelist:
            this_note = self.r_db.get_note_from_handle(notehandle)
            title = self._(this_note.type.xml_str())
            if this_note is not None:
                idx += 1
                if len(notelist) > 1:
                    if (
                        self.default_note(parent, int(this_note.type))
                        or int(this_note.type) == NoteType.HTML_CODE
                    ):
                        title_text = self._("Note: %s") % str(idx)
                    else:
                        title = " (" + title + ")"
                        title_text = self._("Note: %s") % str(idx) + title
                else:
                    if (
                        self.default_note(parent, int(this_note.type))
                        or int(this_note.type) == NoteType.HTML_CODE
                    ):
                        title_text = self._("Note")
                    else:
                        title_text = title

                # Tags
                if parent:
                    tags = self.show_tags(this_note)
                    if tags and self.report.inc_tags:
                        title_text += " (" + tags + ")"

                notesection.extend(Html("i", title_text, class_="NoteType"))
                notesection.extend(self.get_note_format(this_note, True))
        return notesection

    def event_header_row(self):
        """
        creates the event header row for all events
        """
        trow = Html("tr", close=None)
        trow.extend(
            Html("th", trans, class_=colclass, inline=True)
            for trans, colclass in [
                (self._("Event"), "ColumnEvent"),
                (self._("Date"), "ColumnDate"),
                (self._("Place"), "ColumnPlace"),
                (self._("Description"), "ColumnDescription"),
                (self._("Sources"), "ColumnSources"),
            ]
        )
        trow += Html("/tr", close=None)
        return trow

    def display_event_other_person_role(
        self, skip_event_ref, uplink, htmllist, refering_person
    ):
        """
        Display the role of the refering person to this event.
        Skip the role for the specified skip_event_ref because it is already
        displayed with the primary role.

        @param self            This report page.
        @param skip_event_ref  This event_ref can be skipped. It is already displayed.
        @param uplink          If True, then "../../../" is inserted in front of the result.
        @param htmllist        The HTML list to which text has to be appended.
        @param refering_person The person that has a role in the event.
        """
        event_refs = refering_person.get_event_ref_list()
        for event_ref in event_refs:
            if (
                event_ref.get_reference_handle()
                != skip_event_ref.get_reference_handle()
            ):
                # Refering to an other event.
                continue
            elif event_ref.is_equal(skip_event_ref):
                # This event_ref is already displayed.
                continue
            role = event_ref.get_role()
            # Get the person name with a link to it.
            person_name = self.new_person_link(
                refering_person.get_handle(), uplink, refering_person
            )
            # Add the person name and role to the page.
            htmllist.extend(
                Html(
                    "p",
                    _("(%(str1)s) %(str2)s")
                    % {
                        "str1": Html("b", role),
                        "str2": person_name,
                    },
                )
            )

    def display_event_other_person_roles(self, event, skip_event_ref, uplink, htmllist):
        """
        Display all the other persons with their role to this event.
        Skip the person with the specified skip_event_ref, because he is already
        displayed with the primary role.

        @param self           This report page.
        @param event          The event that is concerned.
        @param skip_event_ref This event_ref can be skipped. It is already displayed.
        @param uplink         If True, then "../../../" is inserted in front of the result.
        @param htmllist       The HTML list to which text has to be appended.

        @return void
        """
        refering_person_handles = get_event_person_referents(
            event.get_handle(), self.r_db
        )
        for refering_person_handle in refering_person_handles:
            refering_person = self.r_db.get_person_from_handle(refering_person_handle)
            if not refering_person:
                continue
            self.display_event_other_person_role(
                skip_event_ref, uplink, htmllist, refering_person
            )

    def display_event_other_family_role(
        self, skip_event_ref, uplink, htmllist, refering_family
    ):
        """
        Display the role of the refering family to this event.
        Skip the role for the specified skip_event_ref because it is already
        displayed with the primary role.

        @param self            This report page.
        @param skip_event_ref  This event_ref can be skipped. It is already displayed.
        @param uplink          If True, then "../../../" is inserted in front of the result.
        @param htmllist        The HTML list to which text has to be appended.
        @param refering_family The family that has a role in the event.
        """
        event_refs = refering_family.get_event_ref_list()
        for event_ref in event_refs:
            if (
                event_ref.get_reference_handle()
                != skip_event_ref.get_reference_handle()
            ):
                # Refering to an other event.
                continue
            elif event_ref.is_equal(skip_event_ref):
                # This event_ref is already displayed.
                continue
            role = event_ref.get_role()
            plain_family_name = self.report.get_family_name(refering_family)
            family_name = self.family_link(
                refering_family.get_handle(),
                plain_family_name,
                gid=refering_family.get_gramps_id(),
                uplink=uplink,
            )
            # Add the family name and role to the page.
            htmllist.extend(
                Html(
                    "p",
                    _("(%(str1)s) %(str2)s")
                    % {
                        "str1": Html("b", role),
                        "str2": family_name,
                    },
                )
            )

    def display_event_other_family_roles(self, event, skip_event_ref, uplink, htmllist):
        """
        Display all the other families with their role to this event.
        Skip the family with the specified skip_event_ref, because it is already
        displayed with the primary role.

        @param self           This report page.
        @param event          The event that is concerned.
        @param skip_event_ref This event_ref can be skipped. It is already displayed.
        @param uplink         If True, then "../../../" is inserted in front of the result.
        @param htmllist       The HTML list to which text has to be appended.

        @return void
        """
        refering_family_handles = get_event_family_referents(
            event.get_handle(), self.r_db
        )
        for refering_family_handle in refering_family_handles:
            refering_family = self.r_db.get_family_from_handle(refering_family_handle)
            if not refering_family:
                continue
            self.display_event_other_family_role(
                skip_event_ref, uplink, htmllist, refering_family
            )

    def display_event_row(
        self, event, event_ref, place_lat_long, uplink, hyperlink, omit
    ):
        """
        display the event row for IndividualPage

        @param: evt            -- Event object from report database
        @param: evt_ref        -- Event reference
        @param: place_lat_long -- For use in Family Map Pages. This will be
                                  None if called from Family pages, which do
                                  not create a Family Map
        @param: uplink         -- If True, then "../../../" is inserted in
                                  front of the result.
        @param: hyperlink      -- Add a hyperlink or not
        @param: omit           -- Role to be omitted in output
        """
        event_gid = event.get_gramps_id()

        place_handle = event.get_place_handle()
        if place_handle:
            place = self.r_db.get_place_from_handle(place_handle)
            if place:
                self.append_to_place_lat_long(place, event, place_lat_long)

        # begin event table row
        trow = Html("tr")

        # get event type and hyperlink to it or not?
        etype = self._(event.get_type().xml_str())

        event_role = event_ref.get_role()
        if not event_role == omit:
            etype += " (%s)" % event_role
        event_hyper = (
            self.event_link(event_ref.ref, etype, event_gid, uplink)
            if hyperlink
            else etype
        )
        trow += Html("td", event_hyper, class_="ColumnEvent", rowspan=2)

        # get event data
        event_data = self.get_event_data(event, event_ref, uplink)

        trow.extend(
            Html(
                "td",
                data or "&nbsp;",
                class_=colclass,
                inline=(not data or colclass == "ColumnDate"),
            )
            for (label, colclass, data) in event_data
        )

        trow2 = Html("tr")
        # get event source references
        srcrefs = (
            self.get_citation_links(
                event.get_citation_list() + event_ref.get_citation_list()
            )
            or "&nbsp;"
        )
        if not self.report.options["inc_sources"]:
            srcrefs = "&nbsp;"
        trow += Html("td", srcrefs, class_="ColumnSources", rowspan=2)

        # get event notes
        notelist = event.get_note_list()
        # cached original
        htmllist = self.dump_notes(notelist, Event)

        # if the event or event reference has an attribute attached to it,
        # get the text and format it correctly?
        attrlist = event.get_attribute_list()[:]  # we don't want to modify
        # cached original
        attrlist.extend(event_ref.get_attribute_list())
        for attr in attrlist:
            attrrefs = self.get_citation_links(attr.get_citation_list())
            attrdesc = self._("%(str1)s: %(str2)s") % {
                "str1": Html("b", attr.get_type()),
                "str2": attr.get_value(),
            }
            attr_row = (
                Html("tr")
                + Html("td", "&nbsp")
                + Html("td", attrdesc, colspan=3)
                + Html("td", attrrefs)
            )
            htmllist.extend(attr_row)

            # also output notes attached to the attributes
            notelist = attr.get_note_list()
            if notelist:
                htmllist.extend(self.dump_notes(notelist, Event))

        if self.inc_other_roles:
            self.display_event_other_person_roles(event, event_ref, uplink, htmllist)
            self.display_event_other_family_roles(event, event_ref, uplink, htmllist)

        trow2 += Html("td", htmllist, class_="ColumnNotes", colspan=3)

        trow += trow2
        # return events table row to its callers
        return trow

    def append_to_place_lat_long(self, place, event, place_lat_long):
        """
        Create a list of places with coordinates.

        @param: place_lat_long -- for use in Family Map Pages. This will be
                                  None if called from Family pages, which do
                                  not create a Family Map
        """
        if place_lat_long is None:
            return
        place_handle = place.get_handle()
        event_date = event.get_date_object()

        # 0 = latitude, 1 = longitude, 2 - placetitle,
        # 3 = place handle, 4 = event
        found = any(
            data[3] == place_handle and data[4] == event_date for data in place_lat_long
        )
        if not found:
            placetitle = _pd.display(self.r_db, place, fmt=0)
            latitude = place.get_latitude()
            longitude = place.get_longitude()
            if latitude and longitude:
                latitude, longitude = conv_lat_lon(latitude, longitude, "D.D8")
                if latitude is not None:
                    place_lat_long.append(
                        [latitude, longitude, placetitle, place_handle, event]
                    )

    def _get_event_place(self, person, place_lat_long):
        """
        Retrieve from a person their events, and places for family map

        @param: person         -- Person object from the database
        @param: place_lat_long -- For use in Family Map Pages. This will be
                                  None if called from Family pages, which do
                                  not create a Family Map
        """
        if not person:
            return

        # check to see if this person is in the report database?
        use_link = self.report.person_in_webreport(person.get_handle())
        if use_link:
            evt_ref_list = person.get_event_ref_list()
            if evt_ref_list:
                for evt_ref in evt_ref_list:
                    event = self.r_db.get_event_from_handle(evt_ref.ref)
                    if event:
                        pl_handle = event.get_place_handle()
                        if pl_handle:
                            place = self.r_db.get_place_from_handle(pl_handle)
                            if place:
                                self.append_to_place_lat_long(
                                    place, event, place_lat_long
                                )

    def family_link(self, family_handle, name, gid=None, uplink=False):
        """
        Create the url and link for FamilyPage

        @param: family_handle -- The handle for the family to link
        @param: name          -- The family name
        @param: gid           -- The family gramps ID
        @param: uplink        -- If True, then "../../../" is inserted in
                                 front of the result.
        """
        name = html_escape(name)
        if not self.noid and gid:
            gid_html = Html("span", " [%s]" % gid, class_="grampsid", inline=True)
        else:
            gid_html = ""

        result = self.report.obj_dict.get(Family).get(family_handle)
        if result is None:
            # the family is not included in the webreport
            return name + str(gid_html)

        url = self.report.build_url_fname(result[0], uplink=uplink)
        hyper = Html("a", name, href=url, title=name)
        hyper += gid_html
        return hyper

    def event_link(self, event_handle, event_title, gid=None, uplink=False):
        """
        Creates a hyperlink for an event based on its type

        @param: event_handle -- Event handle
        @param: event_title  -- Event title
        @param: gid          -- The gramps ID for the event
        @param: uplink       -- If True, then "../../../" is inserted in front
                                of the result.
        """
        if not self.inc_events:
            return event_title

        url = self.report.build_url_fname_html(event_handle, "evt", uplink)
        hyper = Html("a", event_title, href=url, title=event_title)

        if not self.noid and gid:
            hyper += Html("span", " [%s]" % gid, class_="grampsid", inline=True)
        return hyper

    def format_family_events(self, event_ref_list, place_lat_long):
        """
        displays the event row for events such as marriage and divorce

        @param: event_ref_list -- List of events reference
        @param: place_lat_long -- For use in Family Map Pages. This will be
                                  None if called from Family pages, which do
                                  not create a Family Map
        """
        with Html("table", class_="infolist eventlist " + self.dir) as table:
            thead = Html("thead")
            table += thead

            # attach event header row
            thead += self.event_header_row()

            # begin table body
            tbody = Html("tbody")
            table += tbody

            for evt_ref in event_ref_list:
                event = self.r_db.get_event_from_handle(evt_ref.ref)

                # add event body row
                tbody += self.display_event_row(
                    event,
                    evt_ref,
                    place_lat_long,
                    uplink=True,
                    hyperlink=True,
                    omit=EventRoleType.FAMILY,
                )
        return table

    def get_event_data(self, evt, evt_ref, uplink, gid=None):
        """
        retrieve event data from event and evt_ref

        @param: evt     -- Event from database
        @param: evt_ref -- Event reference
        @param: uplink  -- If True, then "../../../" is inserted in front of
                           the result.
        """
        dummy_evt_ref = evt_ref
        dummy_gid = gid
        place = None
        place_handle = evt.get_place_handle()
        if place_handle:
            place = self.r_db.get_place_from_handle(place_handle)

        place_hyper = None
        if place:
            place_name = _pd.display(self.r_db, place, evt.get_date_object(), fmt=0)
            place_hyper = self.place_link(place_handle, place_name, uplink=uplink)

        evt_desc = evt.get_description()

        # wrap it all up and return to its callers
        # position 0 = translatable label, position 1 = column class
        # position 2 = data
        return [
            (
                self._("Date"),
                "ColumnDate",
                self.rlocale.get_date(evt.get_date_object()),
            ),
            (self._("Place"), "ColumnPlace", place_hyper),
            (self._("Description"), "ColumnDescription", evt_desc),
        ]

    def dump_ordinance(self, ldsobj, ldssealedtype, toggle=True):
        """
        will dump the LDS Ordinance information for either
        a person or a family ...

        @param: ldsobj        -- Either person or family
        @param: ldssealedtype -- Either Sealed to Family or Spouse
        """
        dummy_ldssealedtype = ldssealedtype
        objectldsord = ldsobj.get_lds_ord_list()
        if not objectldsord:
            return None

        if toggle:
            disp = "none" if self.report.options["toggle"] else "block"
            ordin = Html(
                "table",
                class_="infolist ldsordlist " + self.dir,
                id="toggle_lds",
                style="display:%s" % disp,
            )
        else:
            ordin = Html("table", class_="infolist ldsordlist " + self.dir)
        # begin LDS ordinance table and table head
        with ordin as table:
            thead = Html("thead")
            table += thead

            # begin HTML row
            trow = Html("tr")
            thead += trow

            trow.extend(
                Html("th", label, class_=colclass, inline=True)
                for (label, colclass) in [
                    [self._("Type"), "ColumnLDSType"],
                    [self._("Date"), "ColumnDate"],
                    [self._("Temple"), "ColumnLDSTemple"],
                    [self._("Place"), "ColumnLDSPlace"],
                    [self._("Status"), "ColumnLDSStatus"],
                    [self._("Sources"), "ColumnLDSSources"],
                ]
            )

            # start table body
            tbody = Html("tbody")
            table += tbody

            for ordobj in objectldsord:
                place_hyper = "&nbsp;"
                place_handle = ordobj.get_place_handle()
                if place_handle:
                    place = self.r_db.get_place_from_handle(place_handle)
                    if place:
                        place_title = _pd.display(self.r_db, place, fmt=0)
                        place_hyper = self.place_link(
                            place_handle,
                            place_title,
                            place.get_gramps_id(),
                            uplink=True,
                        )

                # begin ordinance rows
                trow = Html("tr")

                trow.extend(
                    Html(
                        "td",
                        value or "&nbsp;",
                        class_=colclass,
                        inline=(not value or colclass == "ColumnDate"),
                    )
                    for (value, colclass) in [
                        (ordobj.type2xml(), "ColumnType"),
                        (self.rlocale.get_date(ordobj.get_date_object()), "ColumnDate"),
                        (ordobj.get_temple(), "ColumnLDSTemple"),
                        (place_hyper, "ColumnLDSPlace"),
                        (ordobj.get_status(), "ColumnLDSStatus"),
                        (
                            self.get_citation_links(ordobj.get_citation_list()),
                            "ColumnSources",
                        ),
                    ]
                )
                tbody += trow
        return table

    def write_srcattr(self, srcattr_list):
        """
        Writes out the srcattr for the different objects

        @param: srcattr_list -- List of source attributes
        """
        if not srcattr_list:
            return None

        # begin data map division and section title...
        with Html("div", class_="subsection", id="data_map") as section:
            with self.create_toggle("srcattr") as h4_head:
                section += h4_head
                h4_head += self._("Attributes")

            disp = "none" if self.report.options["toggle"] else "block"
            with Html(
                "table",
                class_="infolist " + self.dir,
                id="toggle_srcattr",
                style="display:%s" % disp,
            ) as table:
                section += table

                thead = Html("thead")
                table += thead

                trow = Html("tr") + (
                    Html("th", self._("Key"), class_="ColumnAttribute", inline=True),
                    Html("th", self._("Value"), class_="ColumnValue", inline=True),
                )
                thead += trow

                tbody = Html("tbody")
                table += tbody

                for srcattr in srcattr_list:
                    trow = Html("tr") + (
                        Html(
                            "td",
                            str(srcattr.get_type()),
                            class_="ColumnAttribute",
                            inline=True,
                        ),
                        Html(
                            "td", srcattr.get_value(), class_="ColumnValue", inline=True
                        ),
                    )
                    tbody += trow
        return section

    def source_link(
        self, source_handle, source_title, gid=None, cindex=None, uplink=False
    ):
        """
        Creates a link to the source object

        @param: source_handle -- Source handle from database
        @param: source_title  -- Title from the source object
        @param: gid           -- Source gramps id from the source object
        @param: cindex        -- Count index
        @param: uplink        -- If True, then "../../../" is inserted in
                                 front of the result.
        """
        url = self.report.build_url_fname_html(source_handle, "src", uplink)
        hyper = Html("a", source_title, href=url, title=source_title)

        # if not None, add name reference to hyperlink element
        if cindex:
            hyper.attr += ' name ="sref%d"' % cindex

        # add Gramps ID
        if not self.noid and gid:
            hyper += Html("span", " [%s]" % gid, class_="grampsid", inline=True)
        return hyper

    def display_addr_list(self, addrlist, showsrc):
        """
        Display a person's or repository's addresses ...

        @param: addrlist -- a list of address handles
        @param: showsrc  -- True = show sources
                            False = do not show sources
                            None = djpe
        """
        if not addrlist:
            return None

        # begin addresses division and title
        with Html("div", class_="subsection", id="Addresses") as section:
            with self.create_toggle("addr") as h4_head:
                section += h4_head
                h4_head += self._("Addresses")

            # write out addresses()
            section += self.dump_addresses(addrlist, showsrc)

        # return address division to its caller
        return section

    def dump_addresses(self, addrlist, showsrc):
        """
        will display an object's addresses, url list, note list,
        and source references.

        @param: addrlist = either person or repository address list
        @param: showsrc = True  --  person and their sources
                          False -- repository with no sources
                          None  -- Address Book address with sources
        """
        if not addrlist:
            return None

        # begin summaryarea division
        disp = "none" if self.report.options["toggle"] else "block"
        with Html(
            "div", class_="AddressTable", id="toggle_addr", style="display:%s" % disp
        ) as summaryarea:
            # begin address table
            with Html("table") as table:
                summaryarea += table

                # get table class based on showsrc
                if showsrc is True:
                    table.attr = 'class = "infolist addrlist ' + self.dir + '"'
                elif showsrc is False:
                    table.attr = 'class = "infolist repolist ' + self.dir + '"'
                else:
                    table.attr = 'class = "infolist addressbook ' + self.dir + '"'

                # begin table head
                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                addr_header = [
                    [self._("Date"), "Date"],
                    [self._("Street"), "StreetAddress"],
                    [self._("Locality"), "Locality"],
                    [self._("City"), "City"],
                    [self._("State/ Province"), "State"],
                    [self._("County"), "County"],
                    [self._("Postal Code"), "Postalcode"],
                    [self._("Country"), "Cntry"],
                    [self._("Phone"), "Phone"],
                ]

                # True, False, or None ** see docstring for explanation
                if showsrc in [True, None]:
                    addr_header.append([self._("Sources"), "Sources"])

                trow.extend(
                    Html("th", self._(label), class_="Colummn" + colclass, inline=True)
                    for (label, colclass) in addr_header
                )

                # begin table body
                tbody = Html("tbody")
                table += tbody

                # get address list from an object; either repository or person
                for address in addrlist:
                    trow = Html("tr")
                    tbody += trow

                    addr_data_row = [
                        (
                            self.rlocale.get_date(address.get_date_object()),
                            "ColumnDate",
                        ),
                        (address.get_street(), "ColumnStreetAddress"),
                        (address.get_locality(), "ColumnLocality"),
                        (address.get_city(), "ColumnCity"),
                        (address.get_state(), "ColumnState"),
                        (address.get_county(), "ColumnCounty"),
                        (address.get_postal_code(), "ColumnPostalCode"),
                        (address.get_country(), "ColumnCntry"),
                        (address.get_phone(), "ColumnPhone"),
                    ]

                    # get source citation list
                    if showsrc in [True, None]:
                        addr_data_row.append(
                            [
                                self.get_citation_links(address.get_citation_list()),
                                "ColumnSources",
                            ]
                        )

                    trow.extend(
                        Html("td", value or "&nbsp;", class_=colclass, inline=True)
                        for (value, colclass) in addr_data_row
                    )

                    # address: notelist
                    if showsrc is not None:
                        notelist = self.display_note_list(
                            address.get_note_list(), toggle=False
                        )
                        if notelist is not None:
                            summaryarea += notelist
        return summaryarea

    def addressbook_link(self, person_handle, uplink=False):
        """
        Creates a hyperlink for an address book link based on person's handle

        @param: person_handle -- Person's handle from the database
        @param: uplink        -- If True, then "../../../" is inserted in
                                 front of the result.
        """
        url = self.report.build_url_fname_html(person_handle, "addr", uplink)
        person = self.r_db.get_person_from_handle(person_handle)
        person_name = self.get_name(person)

        # return addressbook hyperlink to its caller
        return Html("a", person_name, href=url, title=html_escape(person_name))

    def get_name(self, person, maiden_name=None):
        """I5118

        Return person's name, unless maiden_name given, unless married_name
        listed.

        @param: person      -- person object from database
        @param: maiden_name -- Female's family surname
        """
        # get name format for displaying names
        name_format = self.report.options["name_format"]

        # Get all of a person's names
        primary_name = person.get_primary_name()
        married_name = None
        names = [primary_name] + person.get_alternate_names()
        for name in names:
            if int(name.get_type()) == NameType.MARRIED:
                married_name = name
                break  # use first

        # Now, decide which to use:
        if maiden_name is not None:
            if married_name is not None:
                name = Name(married_name)
            else:
                name = Name(primary_name)
                surname_obj = name.get_primary_surname()
                surname_obj.set_surname(maiden_name)
        else:
            name = Name(primary_name)
        name.set_display_as(name_format)
        return _nd.display_name(name)

    def display_attribute_header(self, toggle=True):
        """
        Display the attribute section and its table header
        """
        # begin attributes division and section title
        if toggle:
            with Html("div", class_="subsection", id="attributes") as section:
                with self.create_toggle("attr") as h4_head:
                    section += h4_head
                    h4_head += self._("Attributes")
            disp = "none" if self.report.options["toggle"] else "block"
            head = Html(
                "table",
                class_="infolist attrlist",
                id="toggle_attr",
                style="display:%s" % disp,
            )
        else:
            section = Html("h4", self._("Attributes"), inline=True)
            head = Html("table", class_="infolist attrlist")

        # begin attributes table
        with head as attrtable:
            section += attrtable

            thead = Html("thead")
            attrtable += thead

            trow = Html("tr")
            thead += trow

            trow.extend(
                Html("th", label, class_=colclass, inline=True)
                for (label, colclass) in [
                    (self._("Type"), "ColumnType"),
                    (self._("Value"), "ColumnValue"),
                    (self._("Notes"), "ColumnNotes"),
                    (self._("Sources"), "ColumnSources"),
                ]
            )
        return section, attrtable

    def display_attr_list(self, attrlist, attrtable):
        """
        Will display a list of attributes

        @param: attrlist  -- a list of attributes
        @param: attrtable -- the table element that is being added to
        """
        tbody = Html("tbody")
        attrtable += tbody

        tbody.extend(self.dump_attribute(attr) for attr in attrlist)

    def write_footer(self, date, cal=0):
        """
        Will create and display the footer section of each page...

        @param: bottom -- whether to specify location of footer section
                          or not?
        """
        # begin footer division
        with Html("div", id="footer") as footer:
            footer_note = self.report.options["footernote"]
            if footer_note:
                note = self.get_note_format(
                    self.r_db.get_note_from_gramps_id(footer_note), False
                )
                user_footer = Html("div", id="user_footer")
                footer += user_footer

                # attach note
                user_footer += note

            msg = self._(
                "Generated by %(gramps_home_html_start)s"
                "Gramps%(html_end)s %(version)s"
            ) % {
                "gramps_home_html_start": '<a href="' + URL_HOMEPAGE + '">',
                "html_end": "</a>",
                "version": VERSION,
            }
            if date is not None and date > 0:
                msg += "<br />"
                last_modif = datetime.datetime.fromtimestamp(date).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                msg += self._("Last change was the %(date)s") % {"date": last_modif}
            else:
                dat_txt = self._(" on %(date)s")
                msg += dat_txt % {"date": self.rlocale.get_date(Today())}

            origin1 = self.report.filter.get_name(self.rlocale)
            filt_number = self.report.options["filter"]
            # optional "link-home" feature; see bug report #2736
            if self.report.options["linkhome"]:
                center_person = self.r_db.get_person_from_gramps_id(
                    self.report.options["pid"]
                )
                if center_person and self.report.person_in_webreport(
                    center_person.handle
                ):
                    if cal > 0 and not self.usecms:
                        prfx = "/".join(([".."] * 2 + ["ppl"]))
                    else:
                        prfx = "ppl"
                    center_person_url = self.report.build_url_fname_html(
                        center_person.handle, prfx, uplink=False
                    )

                    # person_name = self.get_name(center_person)
                    if filt_number > 0 and filt_number < 5:
                        subject_url = '<a href="' + center_person_url + '">'
                        subject_url += origin1 + "</a>"
                    else:
                        subject_url = origin1
                    msg += self._("%(http_break)sCreated for %(subject_url)s") % {
                        "http_break": "<br />",
                        "subject_url": subject_url,
                    }
                else:
                    msg += self._("%(http_break)sCreated for %(subject_url)s") % {
                        "http_break": "<br />",
                        "subject_url": origin1,
                    }

            # creation author
            footer += Html("p", msg, id="createdate")

            # get copyright license for all pages
            copy_nr = self.report.copyright

            text = ""
            if copy_nr == 0:
                if self.author:
                    year = Today().get_year()
                    text = "&copy; %(year)d %(person)s" % {
                        "person": self.author,
                        "year": year,
                    }
            elif copy_nr < len(_CC):
                # Note. This is a URL
                sub_cal = cal + 1 if cal > 0 else 1
                if self.usecms:
                    fname = "/".join(["images", "somerights20.gif"])
                elif self.the_lang:
                    fname = "/".join(
                        ([".."] * sub_cal + ["images", "somerights20.gif"])
                    )
                else:
                    fname = "/".join(["images", "somerights20.gif"])
                url = self.report.build_url_fname(fname, None, self.uplink, image=True)
                text = _CC[copy_nr] % {"gif_fname": url}
            footer += Html("p", text, id="copyright")

        # return footer to its callers
        return footer

    def write_header(self, the_title, cal=0):
        """
        Note. 'title' is used as currentsection in the navigation links and
        as part of the header title.

        @param: title -- Is the title of the web page
        @param: cal   -- The number of directories to use
        """
        # If .php extension and a note selected, add it to the head section.
        phpnote = self.report.options["phpnote"]
        note = None
        if phpnote and self.ext == ".php":
            # This is used to give the ability to have a php init session.
            # This note must not contains formatting
            # and should only contains php code. ie:
            # <? php session_start (); ?>
            note = self.r_db.get_note_from_gramps_id(phpnote).get()

        # begin each html page...
        if self.the_lang:
            xmllang = self.the_lang.replace("_", "-")
        else:
            xmllang = xml_lang()
        page, head, body = Html.page(
            "%s - %s" % (html_escape(self.title_str.strip()), html_escape(the_title)),
            self.report.encoding,
            xmllang,
            cms=self.usecms,
            php_session=note,
            dir=self.dir,
        )

        # temporary fix for .php parsing error
        if self.ext in [".php", ".cgi"]:
            del page[0]  # remove the "DOCTYPE" directive

        # Header constants
        _meta1 = 'name ="viewport" content="width=device-width, '
        _meta1 += "height=device-height, initial-scale=1.0, "
        _meta1 += 'minimum-scale=0.5, maximum-scale=10.0, user-scalable=yes"'
        _meta2 = 'name ="apple-mobile-web-app-capable" content="yes"'
        _meta3 = 'name="generator" content="%s %s %s"' % (
            PROGRAM_NAME,
            VERSION,
            URL_HOMEPAGE,
        )
        _meta4 = 'name="author" content="%s"' % self.author
        _meta5 = 'name="robots" content="noindex"'
        _meta6 = 'name="googlebot" content="noindex"'

        # create additional meta tags
        meta = Html("meta", attr=_meta1) + (
            Html("meta", attr=_meta2, indent=False),
            Html("meta", attr=_meta3, indent=False),
            Html("meta", attr=_meta4, indent=False),
            Html("meta", attr=_meta5, indent=False),
            Html("meta", attr=_meta6, indent=False),
        )

        # Link to _NARRATIVESCREEN  stylesheet
        sub_cal = cal + 1 if cal > 0 else 1
        if self.usecms:
            fname = "/".join(["css", _NARRATIVESCREEN])
        elif self.the_lang:
            fname = "/".join(([".."] * sub_cal + ["css", _NARRATIVESCREEN]))
        elif cal > 0:
            fname = "/".join(([".."] * cal + ["css", _NARRATIVESCREEN]))
        else:
            fname = "/".join(["css", _NARRATIVESCREEN])
        url2 = self.report.build_url_fname(fname, None, self.uplink)

        # Link to _NARRATIVEPRINT stylesheet
        if self.usecms:
            fname = "/".join(["css", _NARRATIVEPRINT])
        elif self.the_lang:
            fname = "/".join(([".."] * sub_cal + ["css", _NARRATIVEPRINT]))
        elif cal > 0:
            fname = "/".join(([".."] * cal + ["css", _NARRATIVEPRINT]))
        else:
            fname = "/".join(["css", _NARRATIVEPRINT])
        url3 = self.report.build_url_fname(fname, None, self.uplink)

        # Link to Gramps favicon
        if self.usecms:
            fname = "/".join(["images", "favicon2.ico"])
        elif self.the_lang:
            fname = "/".join(([".."] * sub_cal + ["images", "favicon2.ico"]))
        elif cal > 0:
            fname = "/".join(([".."] * cal + ["images", "favicon2.ico"]))
        else:
            fname = "/".join(["images", "favicon2.ico"])
        url4 = self.report.build_url_fname(fname, None, self.uplink, image=True)

        # create stylesheet and favicon links
        links = Html("link", type="image/x-icon", href=url4, rel="shortcut icon")
        # attach the ancestortree style sheet if ancestor
        # graph is being created?
        if self.report.options["ancestortree"]:
            if self.usecms:
                fname = "/".join(["css", "ancestortree.css"])
            elif self.the_lang:
                fname = "/".join(([".."] * sub_cal + ["css", "ancestortree.css"]))
            elif cal > 0:
                fname = "/".join(([".."] * cal + ["css", "ancestortree.css"]))
            else:
                fname = "/".join(["css", "ancestortree.css"])
            url5 = self.report.build_url_fname(fname, None, self.uplink)
            links += Html(
                "link",
                type="text/css",
                href=url5,
                media="screen",
                rel="stylesheet",
                indent=False,
            )
        links += Html(
            "link",
            type="text/css",
            href=url3,
            media="print",
            rel="stylesheet",
            indent=False,
        )
        links += Html(
            "link",
            type="text/css",
            href=url2,
            media="screen",
            rel="stylesheet",
            indent=False,
        )
        # create all alternate stylesheets
        # Cannot use it on local files (file://)
        for css_f in CSS:
            already_done = []
            for css_fn in ("UsEr_", "Basic", "Mainz", "Nebraska"):
                if css_fn in css_f and css_f not in already_done:
                    css_f = css_f.replace("UsEr_", "")
                    already_done.append(css_f)
                    if self.usecms:
                        fname = "/".join(["css", css_f + ".css"])
                    elif self.the_lang:
                        fname = "/".join(([".."] * sub_cal + ["css", css_f + ".css"]))
                    elif cal > 0:
                        fname = "/".join(([".."] * cal + ["css", css_f + ".css"]))
                    else:
                        fname = "/".join(["css", css_f + ".css"])
                    urlx = self.report.build_url_fname(fname, None, self.uplink)
                    links += Html(
                        "link",
                        rel="alternate stylesheet",
                        title=self._(css_f),
                        indent=False,
                        media="screen",
                        type="text/css",
                        href=urlx,
                    )

        # Link to Navigation Menus stylesheet
        if CSS[self.report.css]["navigation"]:
            if self.the_lang and not self.usecms:
                fname = "/".join(["..", "css", "narrative-menus.css"])
            else:
                fname = "/".join(["css", "narrative-menus.css"])
            url = self.report.build_url_fname(fname, None, self.uplink)
            links += Html(
                "link",
                type="text/css",
                href=url,
                media="screen",
                rel="stylesheet",
                indent=False,
            )

        # add additional meta and link tags
        head += meta
        head += links

        # Add the script to control the menu
        menuscript = Html(
            "<script>function navFunction() { "
            'var x = document.getElementById("dropmenu"); '
            'if (x.className === "nav") { x.className += "'
            ' responsive"; } else { x.className = "nav"; }'
            " }</script>"
        )
        head += menuscript

        # add outerwrapper to set the overall page width
        outerwrapperdiv = Html("div", id="outerwrapper")
        body += outerwrapperdiv

        # begin header section
        headerdiv = Html("div", id="header", class_=self.dir) + (
            Html(
                '<button href="javascript:void(0);" class="navIcon"'
                ' onclick="navFunction()">&#8801;</button>'
            )
        )
        headerdiv += Html(
            "h1", html_escape(self.title_str), class_="nav", id="SiteTitle", inline=True
        )
        outerwrapperdiv += headerdiv

        header_note = self.report.options["headernote"]
        if header_note:
            note = self.get_note_format(
                self.r_db.get_note_from_gramps_id(header_note), False
            )

            user_header = Html("div", id="user_header")
            headerdiv += user_header

            # attach note
            user_header += note

        # Begin Navigation Menu--
        # is the style sheet either Basic-Blue or Visually Impaired,
        # and menu layout is Drop Down?
        if (
            self.report.css == _("Basic-Blue")
            or self.report.css == _("Visually Impaired")
        ) and self.report.navigation == "dropdown":
            outerwrapperdiv += self.display_drop_menu()
        else:
            outerwrapperdiv += self.display_nav_links(the_title, cal=cal)

        if self.report.options["toggle"]:
            head += TOGGLE

        # Create a button to go to the top of the page
        viewbox = "0 0 100 100"
        points = "0,100 100,100, 50,10"
        svg = Html("svg", viewBox=viewbox, class_="triangle", inline=False)
        svg += Html("polygon", points=points)
        outerwrapperdiv += Html(
            "button", svg, id="gototop", title=_("Go to top"), onclick="GoToTop()"
        )
        outerwrapperdiv += GOTOTOP  # This must be positioned
        # after the button for it to work

        # message for Codacy :
        # body is used in some modules to add functions like onload(),
        # initialize(), ...
        # some modules doesn't need that, so body is an unused variable
        # in these modules.
        # return page, head, and body to its classes...
        return page, head, body, outerwrapperdiv

    def display_nav_links(self, currentsection, cal=0):
        """
        Creates the navigation menu

        @param: currentsection = which menu item are you on
        """
        # include repositories or not?
        inc_repos = True
        if not self.report.inc_repository or not self.r_db.get_repository_handles():
            inc_repos = False

        # create media pages...
        if self.create_media:
            _create_media_link = True
            if self.create_thumbs_only:
                _create_media_link = False

        # Determine which menu items will be available?
        # Menu items have been adjusted to concide with Gramps Navigation
        # Sidebar order...

        navs = [
            (self.report.index_fname, self._("Home", "Html"), self.report.use_home),
            (self.report.intro_fname, self._("Introduction"), self.report.use_intro),
            (self.report.extrapage, self.extrapagename, (self.extrapage != "")),
            ("individuals", self._("Individuals"), True),
            (self.report.surname_fname, self._("Surnames"), True),
            ("families", self._("Families"), self.report.inc_families),
            ("events", self._("Events"), self.report.inc_events),
            ("places", self._("Places"), self.report.inc_places),
            ("heatmaps", self._("Heatmaps"), self.report.inc_heatmaps),
            ("sources", self._("Sources"), self.report.inc_sources),
            ("repositories", self._("Repositories"), inc_repos),
            (
                "media",
                self._("Media"),
                self.create_images_index
                and self.report.inc_gallery
                and not self.report.create_thumbs_only,
            ),
            (
                "thumbnails",
                self._("Thumbnails"),
                self.create_thumbs_index and self.report.inc_gallery,
            ),
            ("download", self._("Download"), self.report.inc_download),
            ("addressbook", self._("Address Book"), self.report.inc_addressbook),
            ("contact", self._("Contact"), self.report.use_contact),
            ("updates", self._("Updates"), self.report.inc_updates),
            ("statistics", self._("Statistics"), self.report.inc_stats),
            (self.target_cal_uri, self._("Web Calendar"), self.usecal),
        ]

        # Remove menu sections if they are not being created?
        navs = ((url_text, nav_text) for url_text, nav_text, cond in navs if cond)
        menu_items = [[url, text] for url, text in navs]
        number_items = len(menu_items)

        # begin navigation menu division...
        with Html(
            "div", class_="wrappernav " + self.dir, id="nav", role="navigation"
        ) as navigation:
            with Html("div", class_="container") as container:
                index = 0
                unordered = Html("ul", class_="nav", id="dropmenu")
                while index < number_items:
                    url_fname, nav_text = menu_items[index]
                    hyper = self.get_nav_menu_hyperlink(url_fname, nav_text, cal=cal)

                    # Define 'currentsection' to correctly set navlink item
                    # CSS id 'CurrentSection' for Navigation styling.
                    # Use 'self.report.cur_fname' to determine
                    # 'CurrentSection' for individual elements for
                    # Navigation styling.

                    # Figure out if we need <li class = "CurrentSection">
                    # or just <li>

                    check_cs = False
                    if nav_text == currentsection:
                        check_cs = True
                    elif nav_text == self._("Home", "Html"):
                        if "index" in self.report.cur_fname:
                            check_cs = True
                    elif nav_text == self._("Surnames"):
                        if "srn" in self.report.cur_fname:
                            check_cs = True
                        elif self._("Surnames") in currentsection:
                            check_cs = True
                    elif nav_text == self._("Individuals"):
                        if "ppl" in self.report.cur_fname:
                            check_cs = True
                    elif nav_text == self._("Families"):
                        if "fam" in self.report.cur_fname:
                            check_cs = True
                    elif nav_text == self._("Sources"):
                        if "src" in self.report.cur_fname:
                            check_cs = True
                    elif nav_text == self._("Repositories"):
                        if "repo" in self.report.cur_fname:
                            check_cs = True
                    elif nav_text == self._("Places"):
                        if "plc" in self.report.cur_fname:
                            check_cs = True
                    elif nav_text == self._("Heatmap"):
                        if "heat" in self.report.cur_fname:
                            check_cs = True
                    elif nav_text == self._("Events"):
                        if "evt" in self.report.cur_fname:
                            check_cs = True
                    elif nav_text == self._("Media"):
                        if "img" in self.report.cur_fname:
                            check_cs = True
                    elif nav_text == self._("Address Book"):
                        if "addr" in self.report.cur_fname:
                            check_cs = True
                    elif nav_text == self._("Updates"):
                        if "updates" in self.report.cur_fname:
                            check_cs = True
                    elif nav_text == self._("Statistics"):
                        if "statistics" in self.report.cur_fname:
                            check_cs = True
                    elif nav_text == self._("Web Calendar"):
                        if "cal/" in self.report.cur_fname:
                            check_cs = True
                    temp_cs = 'class = "CurrentSection"'
                    check_cs = temp_cs if check_cs else False
                    if check_cs:
                        unordered.extend(Html("li", hyper, attr=check_cs, inline=True))
                    else:
                        if self.report.extrapage != "":
                            if url_fname[:4] == "http" or url_fname[:1] == "/":
                                hyper = Html(
                                    "a", nav_text, href=url_fname, title=nav_text
                                )
                            elif self.report.extrapagename == nav_text:
                                if cal > 0:
                                    url_fname = "/".join(([".."] * cal + [url_fname]))
                                hyper = Html(
                                    "a", nav_text, href=url_fname, title=nav_text
                                )
                        unordered.extend(Html("li", hyper, inline=True))
                    index += 1

                if self.report.options["multitrans"] and self.not_holiday:
                    langs = Html("li", self._("Language"), class_="lang")
                    en_locale = self.report.set_locale("en")
                    languages = en_locale.get_language_dict()
                    choice = Html("ul", class_="lang")
                    langs += choice
                    for language in languages:
                        for extra_lang, dummy_title in self.report.languages:
                            if languages[language] == extra_lang:
                                def_locale = self.report.set_locale(extra_lang)
                                local_lang = def_locale.translation.sgettext(language)
                                if local_lang == self._(language):
                                    lang_txt = html_escape(self._(language))
                                else:
                                    lang_txt = (
                                        html_escape(self._(language))
                                        + "&#8239;("
                                        + local_lang
                                        + ")"
                                    )
                                n_lang = languages[language]
                                nfname = self.report.cur_fname
                                if "event" in nfname:
                                    nfname = "".join(("events", self.ext))
                                if "cal" in nfname:
                                    (dummy_field, dummy_sep, field2) = nfname.partition(
                                        "cal/"
                                    )
                                    sub_cal = 3 if self.the_lang else 2
                                    url = "/".join(
                                        ([".."] * sub_cal + [n_lang, "cal", field2])
                                    )
                                else:
                                    upl = self.uplink
                                    url = self.report.build_url_lang(
                                        nfname, n_lang, upl
                                    )
                                lnk = Html(
                                    "a",
                                    lang_txt,
                                    href=url,
                                    title=lang_txt,
                                    style="white-space:nowrap;",
                                )
                                choice += Html("li", lnk, inline=True)
                    unordered.extend(langs)

                if self.prevnext:
                    prv = Html(
                        '<a onclick="history.go(-1);">%s</a>' % self._("Previous")
                    )
                    nxt = Html('<a onclick="history.go(+1);">%s</a>' % self._("Next"))
                    unordered.extend(Html("li", prv, inline=True))
                    unordered.extend(Html("li", nxt, inline=True))
                container += unordered
            navigation += container
        return navigation

    def display_drop_menu(self):
        """
        Creates the Drop Down Navigation Menu
        """
        # include repositories or not?
        inc_repos = True
        if not self.report.inc_repository or not self.r_db.get_repository_handles():
            inc_repos = False

        # create media pages...
        _create_media_link = False
        if self.create_media:
            _create_media_link = True
            if self.create_thumbs_only:
                _create_media_link = False

        personal = [
            (self.report.intro_fname, self._("Introduction"), self.report.use_intro),
            ("individuals", self._("Individuals"), True),
            (self.report.surname_fname, self._("Surnames"), True),
            ("families", self._("Families"), self.report.inc_families),
        ]
        personal = (
            (url_text, nav_text) for url_text, nav_text, cond in personal if cond
        )
        personal = [[url, text] for url, text in personal]

        navs1 = [
            ("events", self._("Events"), self.report.inc_events),
            ("places", self._("Places"), True),
            ("sources", self._("Sources"), True),
            ("repositories", self._("Repositories"), inc_repos),
        ]
        navs1 = ((url_text, nav_text) for url_text, nav_text, cond in navs1 if cond)
        navs1 = [[url, text] for url, text in navs1]

        media = [
            ("media", self._("Media"), _create_media_link),
            ("thumbnails", self._("Thumbnails"), True),
        ]
        media = ((url_text, nav_text) for url_text, nav_text, cond in media if cond)
        media = [[url, text] for url, text in media]

        misc = [
            ("download", self._("Download"), self.report.inc_download),
            ("addressbook", self._("Address Book"), self.report.inc_addressbook),
        ]
        misc = ((url_text, nav_text) for url_text, nav_text, cond in misc if cond)
        misc = [[url, text] for url, text in misc]

        contact = [("contact", self._("Contact"), self.report.use_contact)]
        contact = ((url_text, nav_text) for url_text, nav_text, cond in contact if cond)
        contact = [[url, text] for url, text in contact]

        # begin navigation menu division...
        with Html("div", class_="wrapper", id="nav", role="navigation") as navigation:
            with Html("div", class_="container") as container:
                unordered = Html("ul", class_="menu", id="dropmenu")

                if self.report.use_home:
                    list_html = Html(
                        "li",
                        self.get_nav_menu_hyperlink(
                            self.report.index_fname, self._("Home", "Html")
                        ),
                    )
                    unordered += list_html

                # add personal column
                self.get_column_data(unordered, personal, self._("Personal"))

                if navs1:
                    for url_fname, nav_text in navs1:
                        unordered.extend(
                            Html(
                                "li",
                                self.get_nav_menu_hyperlink(url_fname, nav_text),
                                inline=True,
                            )
                        )

                # add media column
                self.get_column_data(unordered, media, self._("Media"))

                # add miscellaneous column
                self.get_column_data(unordered, misc, self._("Miscellaneous"))

                # add contact column
                self.get_column_data(unordered, contact, _("Contact"))

                container += unordered
            navigation += container
        return navigation

    def add_image(self, option_name, head, height=0):
        """
        Will add an image (if present) to the page
        If this image contains regions, try to add them.

        @param: option_name -- The name of the report option
        @param: height      -- Height of the image
        """
        pic_id = self.report.options[option_name]
        if pic_id:
            obj = self.r_db.get_media_from_gramps_id(pic_id)
            if obj is None:
                return None
            # get media rectangles
            _region_items = self.media_ref_rect_regions(
                obj.get_handle(), linkurl=self.uplink
            )

            # if there are media rectangle regions, attach behaviour style sheet
            if _region_items:
                if self.the_lang and not self.usecms:
                    fname = "/".join(["..", "css", "behaviour.css"])
                else:
                    fname = "/".join(["css", "behaviour.css"])
                url = self.report.build_url_fname(fname, None, self.uplink)
                head += Html(
                    "link", href=url, type="text/css", media="screen", rel="stylesheet"
                )
            mime_type = obj.get_mime_type()
            if mime_type and is_image_type(mime_type):
                try:
                    newpath, dummy_tpath = self.report.prepare_copy_media(obj)
                    newpathc = newpath
                    if self.the_lang and self.report.archive:
                        (dummy_1_field, dummy_sep, second_field) = newpath.partition(
                            "/"
                        )
                        newpathc = second_field
                    if self.usecms:
                        newpathc = newpathc.replace(self.target_uri + "/", "")
                        # In some case, we have the target_uri without
                        # the leading "/"
                        newpathc = newpathc.replace(self.target_uri[1:] + "/", "")
                    self.report.copy_file(
                        media_path_full(self.r_db, obj.get_path()), newpathc
                    )

                    # begin image
                    with Html(
                        "div", id="GalleryDisplay", style="width: auto; height: auto"
                    ) as image:
                        if _region_items:
                            # add all regions and links to persons
                            regions = Html("ol", class_="RegionBox")
                            while _region_items:
                                (
                                    name,
                                    coord_x,
                                    coord_y,
                                    width,
                                    height,
                                    linkurl,
                                ) = _region_items.pop()
                                regions += Html(
                                    "li",
                                    style="left:%d%%; "
                                    "top:%d%%; "
                                    "width:%d%%; "
                                    "height:%d%%;" % (coord_x, coord_y, width, height),
                                ) + (Html("a", name, href=linkurl))
                            image += regions

                        # add image
                        imag = Html("img")
                        imag.attr = ""
                        if height:
                            imag.attr += 'height = "%d"' % height

                        descr = html_escape(obj.get_description())
                        newpath = self.report.build_url_fname(newpath, image=True)
                        imag.attr += ' src = "%s" alt = "%s"' % (newpath, descr)
                        fname = (
                            self.report.build_url_fname(
                                obj.get_handle(),
                                "img",
                                uplink=2,
                                image=True,
                            )
                            + self.ext
                        )
                        inc_gallery = self.report.options["gallery"]
                        if not self.create_thumbs_only and inc_gallery:
                            img_link = Html("a", href=fname, title=descr) + (
                                Html("img", src=newpath, alt=descr)
                            )
                        else:
                            # We can't show the image html page.
                            # This page doesn't exist.
                            img_link = Html("img", src=newpath, alt=descr)
                        image += img_link

                    return image

                except (IOError, OSError) as msg:
                    self.r_user.warn(_("Could not add photo to page"), str(msg))

        # no image to return
        return None

    def media_ref_rect_regions(self, handle, linkurl=True):
        """
        Gramps feature #2634 -- attempt to highlight subregions in media
        objects and link back to the relevant web page.

        This next section of code builds up the "records" we'll need to
        generate the html/css code to support the subregions

        @param: handle -- The media handle to use
        """
        # get all of the backlinks to this media object; meaning all of
        # the people, events, places, etc..., that use this image
        _region_items = set()
        for classname, newhandle in self.r_db.find_backlink_handles(
            handle, include_classes=["Person", "Family", "Event", "Place"]
        ):
            # for each of the backlinks, get the relevant object from the db
            # and determine a few important things, such as a text name we
            # can use, and the URL to a relevant web page
            _obj = None
            _name = ""
            _linkurl = "#"
            if classname == "Person":
                # Is this a person for whom we have built a page:
                if self.report.person_in_webreport(newhandle):
                    # If so, let's add a link to them:
                    _obj = self.r_db.get_person_from_handle(newhandle)
                    if _obj:
                        # What is the shortest possible name we could use
                        # for this person?
                        _name = (
                            _obj.get_primary_name().get_call_name()
                            or _obj.get_primary_name().get_first_name()
                            or self._("Unknown")
                        )
                        _linkurl = self.report.build_url_fname_html(
                            _obj.handle, "ppl", linkurl
                        )
            elif classname == "Family" and self.inc_families:
                _obj = self.r_db.get_family_from_handle(newhandle)
                partner1_handle = _obj.get_father_handle()
                partner2_handle = _obj.get_mother_handle()
                partner1 = None
                partner2 = None
                if partner1_handle:
                    partner1 = self.r_db.get_person_from_handle(partner1_handle)
                if partner2_handle:
                    partner2 = self.r_db.get_person_from_handle(partner2_handle)
                if partner2 and partner1:
                    _name = partner1.get_primary_name().get_first_name()
                    _linkurl = self.report.build_url_fname_html(
                        partner1_handle, "ppl", True
                    )
                elif partner1:
                    _name = partner1.get_primary_name().get_first_name()
                    _linkurl = self.report.build_url_fname_html(
                        partner1_handle, "ppl", True
                    )
                elif partner2:
                    _name = partner2.get_primary_name().get_first_name()
                    _linkurl = self.report.build_url_fname_html(
                        partner2_handle, "ppl", True
                    )
                if not _name:
                    _name = self._("Unknown")
            elif classname == "Event" and self.inc_events:
                _obj = self.r_db.get_event_from_handle(newhandle)
                _name = _obj.get_description()
                if not _name:
                    _name = self._("Unknown")
                _linkurl = self.report.build_url_fname_html(_obj.handle, "evt", True)
            elif classname == "Place":
                _obj = self.r_db.get_place_from_handle(newhandle)
                _name = _pd.display(self.r_db, _obj, fmt=0)
                if not _name:
                    _name = self._("Unknown")
                _linkurl = self.report.build_url_fname_html(newhandle, "plc", True)

            # continue looking through the loop for an object...
            if _obj is None:
                continue

            # get a list of all media refs for this object
            media_list = _obj.get_media_list()

            # go media refs looking for one that points to this image
            for mediaref in media_list:
                # is this mediaref for this image?  do we have a rect?
                if mediaref.ref == handle and mediaref.rect is not None:
                    (coord_x1, coord_y1, coord_x2, coord_y2) = mediaref.rect
                    # Gramps gives us absolute coordinates,
                    # but we need relative width + height
                    width = coord_x2 - coord_x1
                    height = coord_y2 - coord_y1

                    # remember all this information, cause we'll need
                    # need it later when we output the <li>...</li> tags
                    item = (_name, coord_x1, coord_y1, width, height, _linkurl)
                    _region_items.add(item)

        # End of code that looks for and prepares the media object regions

        return sorted(_region_items)

    def media_ref_region_to_object(self, media_handle, obj):
        """
        Return a region of this image if it refers to this object.

        @param: media_handle -- The media handle to use
        @param: obj          -- The object reference
        """
        # get a list of all media refs for this object
        for mediaref in obj.get_media_list():
            # is this mediaref for this image?  do we have a rect?
            if mediaref.ref == media_handle and mediaref.rect is not None:
                return mediaref.rect  # (x1, y1, x2, y2)
        return None

    def disp_first_img_as_thumbnail(self, photolist, object_):
        """
        Return the Html of the first image of photolist that is
        associated with object. First image might be a region in an
        image. Or, the first image might have regions defined in it.

        @param: photolist -- The list of media
        @param: object_   -- The object reference
        """
        if not photolist or not self.create_media:
            return None

        photo_handle = photolist[0].get_reference_handle()
        photo = self.r_db.get_media_from_handle(photo_handle)
        mime_type = photo.get_mime_type()
        descr = photo.get_description()

        # begin snapshot division
        with Html("div", class_="snapshot") as snapshot:
            if mime_type and is_image_type(mime_type):
                region = self.media_ref_region_to_object(photo_handle, object_)
                if region:
                    # make a thumbnail of this region
                    newpath = self.copy_thumbnail(photo_handle, photo, region)
                    newpath = self.report.build_url_fname(
                        newpath, uplink=True, image=True
                    )
                    snapshot += self.media_link(
                        photo_handle, newpath, descr, uplink=self.uplink, usedescr=False
                    )
                else:
                    dummy_rpath, newpath = self.report.prepare_copy_media(photo)
                    newpath = self.report.build_url_fname(
                        newpath, image=True, uplink=self.uplink
                    )
                    snapshot += self.media_link(
                        photo_handle, newpath, descr, uplink=self.uplink, usedescr=False
                    )
            else:
                # begin hyperlink
                snapshot += self.doc_link(
                    photo_handle, descr, uplink=self.uplink, usedescr=False
                )

        # return snapshot division to its callers
        return snapshot

    def disp_add_img_as_gallery(self, photolist, object_):
        """
        Display additional image as gallery

        @param: photolist -- The list of media
        @param: object_   -- The object reference
        """
        if not photolist or not self.create_media:
            return None

        # make referenced images have the same order as in media list:
        photolist_handles = {}
        self.max_img = 0
        for mediaref in photolist:
            photolist_handles[mediaref.get_reference_handle()] = mediaref
            photo_handle = mediaref.get_reference_handle()
            photo = self.r_db.get_media_from_handle(photo_handle)
            mime_type = photo.get_mime_type()
            if "image" in mime_type:
                self.max_img += 1
        photolist_ordered = []
        for photoref in copy.copy(photolist):
            if photoref.ref in photolist_handles:
                photo = photolist_handles[photoref.ref]
                photolist_ordered.append(photo)

        # begin individualgallery division and section title
        with Html("div", class_="subsection", id="indivgallery") as section:
            with self.create_toggle("media") as h4_head:
                section += h4_head
                h4_head += self._("Media")

            disp = "none" if self.report.options["toggle"] else "block"
            with Html("div", style="display:%s" % disp, id="toggle_media") as toggle:
                section += toggle
                with Html("div", id="medias") as medias:
                    displayed = []
                    # Create the list of media for lightbox
                    for mediaref in photolist_ordered:
                        photo_handle = mediaref.get_reference_handle()
                        photo = self.r_db.get_media_from_handle(photo_handle)
                        if photo_handle in displayed:
                            continue
                        # get media description
                        descr = photo.get_description()
                        mime_type = photo.get_mime_type()
                        if mime_type and "image" not in mime_type:
                            try:
                                # create thumbnail url
                                # extension needs to be added as it is not
                                # already there
                                url_thumb = (
                                    self.report.build_url_fname(
                                        photo_handle, "thumb", True, image=True
                                    )
                                    + ".png"
                                )
                                # begin hyperlink
                                medias += self.media_link(
                                    photo_handle,
                                    url_thumb,
                                    descr,
                                    uplink=self.uplink,
                                    usedescr=True,
                                )
                            except (IOError, OSError) as msg:
                                self.r_user.warn(
                                    _("Could not add photo to page"), str(msg)
                                )
                        elif not mime_type:
                            try:
                                # begin hyperlink
                                medias += self.doc_link(
                                    photo_handle, descr, uplink=self.uplink
                                )
                            except (IOError, OSError) as msg:
                                self.r_user.warn(
                                    _("Could not add photo to page"), str(msg)
                                )
                # First part for lightbox
                lightbox = 0
                with Html("div", class_="MediaRow") as lightboxes_1:
                    for mediaref in photolist_ordered:
                        photo_handle = mediaref.get_reference_handle()
                        photo = self.r_db.get_media_from_handle(photo_handle)
                        mime_type = photo.get_mime_type()
                        if mime_type and "image" in mime_type:
                            with Html("div", class_="MediaColumn " + self.dir) as boxes:
                                lightboxes_1 += boxes
                                try:
                                    url_thumb = (
                                        self.report.build_url_fname(
                                            photo_handle, "thumb", True, image=True
                                        )
                                        + ".png"
                                    )
                                    # begin hyperlink
                                    lightbox += 1
                                    boxes += Html(
                                        "img",
                                        src=url_thumb,
                                        inline=True,
                                        onclick="openModal();currentSlide(%d)"
                                        % lightbox,
                                        class_="hover-shadow",
                                    )
                                except (IOError, OSError) as msg:
                                    self.r_user.warn(
                                        _("Could not add photo to page"), str(msg)
                                    )
                # Second part for lightbox
                lightbox = 0
                with Html("div", id="MediaModal", class_="ModalClass") as lightboxes_2:
                    lightboxes_2 += Html(
                        "span",
                        "&times;",
                        onclick="closeModal()",
                        class_="MediaClose MediaCursor",
                        inline=True,
                    )
                    with Html("div", class_="ModalContent") as lb_content:
                        lightboxes_2 += lb_content
                        lb_content += Html(
                            "a",
                            "&#10094;",
                            class_="MediaPrev",
                            onclick="plusSlides(-1)",
                        )
                        lb_content += Html(
                            "a", "&#10095;", class_="MediaNext", onclick="plusSlides(1)"
                        )
                        for mediaref in photolist_ordered:
                            photo_handle = mediaref.get_reference_handle()
                            photo = self.r_db.get_media_from_handle(photo_handle)
                            mime_type = photo.get_mime_type()
                            if mime_type and "image" in mime_type:
                                with Html("div", class_="MediaSlide") as box:
                                    lb_content += box
                                    lightbox += 1
                                    image_number = "%d/%d - %s" % (
                                        lightbox,
                                        self.max_img,
                                        photo.get_description(),
                                    )
                                    box += Html(
                                        "div", image_number, class_="MediaNumber"
                                    )
                                    try:
                                        thb_img = (
                                            self.report.build_url_fname(
                                                photo_handle, "img", True, image=True
                                            )
                                            + self.ext
                                        )
                                        fname_, ext = os.path.splitext(photo.get_path())
                                        url_img = (
                                            self.report.build_url_fname(
                                                photo_handle, "images", True, image=True
                                            )
                                            + ext
                                        )

                                        box += Html("a", href=thb_img) + (
                                            Html("img", src=url_img, style="width:100%")
                                        )
                                    except (IOError, OSError) as msg:
                                        self.r_user.warn(
                                            _("Could not add photo to page"), str(msg)
                                        )
                    displayed.append(photo_handle)
                if lightboxes_1:
                    toggle += lightboxes_1
                    toggle += lightboxes_2
                    if lightbox < len(photolist):
                        toggle += Html(
                            "h3", self._("Other media: videos, pdfs..."), inline=True
                        )
                if medias:
                    toggle += medias

            # add fullclear for proper styling
            section += FULLCLEAR

            # return indivgallery division to its caller
            return section

    def default_note(self, parent, notetype):
        """
        return true if the notetype is the same as the parent

        @param: parent   -- The parent object (Person, Family, Media,...)
        @param: notetype -- The type for the current note
        """
        if parent == Person and notetype == NoteType.PERSON:
            return True
        elif parent == Family and notetype == NoteType.FAMILY:
            return True
        elif parent == Media and notetype == NoteType.MEDIA:
            return True
        elif parent == Repository and notetype == NoteType.REPO:
            return True
        elif parent == Source and notetype == NoteType.SOURCE:
            return True
        elif parent == Event and notetype == NoteType.EVENT:
            return True
        elif parent == Place and notetype == NoteType.PLACE:
            return True
        elif parent == Citation and notetype == NoteType.CITATION:
            return True
        elif parent == Attribute and notetype == NoteType.ATTRIBUTE:
            return True
        return False

    def display_note_list(self, notelist=None, parent=None, toggle=True):
        """
        Display note list

        @param: notelist -- The list of notes
        @param: parent   -- The parent object (Person, Family, Media,...)
        """
        if not notelist:
            return None

        # begin LDS ordinance table and table head
        if toggle:
            with Html("div", class_="subsection narrative") as hdiv:
                with self.create_toggle("note") as h4_head:
                    hdiv += h4_head
                    h4_head += self._("Notes")
                disp = "none" if self.report.options["toggle"] else "block"
                with Html(
                    "div",
                    class_="subsection narrative",
                    id="toggle_note",
                    style="display:%s" % disp,
                ) as section:
                    hdiv += section
        else:
            with Html("div", class_="subsection narrative") as section:
                hdiv = section
        idx = 0
        for notehandle in notelist:
            note = self.r_db.get_note_from_handle(notehandle)
            title = self._(note.type.xml_str())

            if note:
                note_text = self.get_note_format(note, True)
                idx += 1
                if len(notelist) > 1:
                    if (
                        self.default_note(parent, int(note.type))
                        or int(note.type) == NoteType.HTML_CODE
                    ):
                        title_text = self._("Note: %s") % str(idx)
                    else:
                        title = " (" + title + ")"
                        title_text = self._("Note: %s") % str(idx) + title
                else:
                    if (
                        self.default_note(parent, int(note.type))
                        or int(note.type) == NoteType.HTML_CODE
                    ):
                        title_text = self._("Note")
                    else:
                        title_text = title

                # Tags
                if parent:
                    tags = self.show_tags(note)
                    if tags and self.report.inc_tags:
                        title_text += " (" + tags + ")"

                # add section title
                section += Html("h4", title_text, inline=True)

                # attach note
                section += note_text

        # return notes to its callers
        return hdiv

    def display_url_list(self, urllist=None):
        """
        Display URL list

        @param: urllist -- The list of urls
        """
        if not urllist:
            return None

        # begin web links division
        with Html("div", class_="subsection", id="WebLinks") as section:
            with self.create_toggle("links") as h4_head:
                section += h4_head
                h4_head += self._("Web Links")

            disp = "none" if self.report.options["toggle"] else "block"
            with Html(
                "table",
                class_="infolist weblinks " + self.dir,
                id="toggle_links",
                style="display:%s" % disp,
            ) as table:
                section += table

                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                trow.extend(
                    Html("th", label, class_=colclass, inline=True)
                    for (label, colclass) in [
                        (self._("Type"), "ColumnType"),
                        (self._("Description"), "ColumnDescription"),
                    ]
                )

                tbody = Html("tbody")
                table += tbody

                for url in urllist:
                    trow = Html("tr")
                    tbody += trow

                    _type = self._(url.get_type().xml_str())
                    uri = url.get_path()
                    descr = url.get_description()

                    # Email address
                    if _type == UrlType.EMAIL:
                        if not uri.startswith("mailto:"):
                            uri = "mailto:%(email)s" % {"email": uri}

                    # Web Site address
                    elif _type == UrlType.WEB_HOME:
                        if not uri.startswith(("http://", "https://")):
                            url = self.secure_mode
                            uri = url + "%(website)s" % {"website": uri}

                    # FTP server address
                    elif _type == UrlType.WEB_FTP:
                        if not uri.startswith(("ftp://", "ftps://")):
                            uri = "ftp://%(ftpsite)s" % {"ftpsite": uri}

                    descr = Html("p", html_escape(descr)) + (
                        Html("a", self._(" [Click to Go]"), href=uri, title=uri)
                    )

                    trow.extend(
                        Html("td", data, class_=colclass, inline=True)
                        for (data, colclass) in [
                            (str(_type), "ColumnType"),
                            (descr, "ColumnDescription"),
                        ]
                    )
        return section

    def display_lds_ordinance(self, db_obj_):
        """
        Display LDS information for a person or family

        @param: db_obj_ -- The database object
        """
        ldsordlist = db_obj_.lds_ord_list
        if not ldsordlist:
            return None

        # begin LDS Ordinance division and section title
        with Html("div", class_="subsection", id="LDSOrdinance") as section:
            with self.create_toggle("lds") as h4_head:
                section += h4_head
                h4_head += self._("Latter-Day Saints/ LDS Ordinance")

            # dump individual LDS ordinance list
            section += self.dump_ordinance(db_obj_, "Person")

        # return section to its caller
        return section

    def display_ind_sources(self, srcobj):
        """
        Will create the "Source References" section for an object

        @param: srcobj -- Sources object
        """
        list(
            map(
                lambda i: self.bibli.add_reference(
                    self.r_db.get_citation_from_handle(i)
                ),
                srcobj.get_citation_list(),
            )
        )
        sourcerefs = self.display_source_refs(self.bibli)

        # return to its callers
        return sourcerefs

    # Only used in IndividualPage.display_ind_sources(),
    # and MediaPage.display_media_sources()
    def display_source_refs(self, bibli):
        """
        Display source references

        @param: bibli -- List of sources
        """
        if bibli.get_citation_count() == 0:
            return None

        with Html("div", class_="subsection", id="sourcerefs") as section:
            section += Html("h4", self._("Source References"), inline=True)

            ordered = Html("ol", id="srcr")

            cindex = 0
            citationlist = bibli.get_citation_list()
            for citation in citationlist:
                cindex += 1
                # Add this source and its references to the page
                source = self.r_db.get_source_from_handle(citation.get_source_handle())
                if source is not None:
                    if source.get_author():
                        authorstring = source.get_author() + ": "
                    else:
                        authorstring = ""
                    list_html = Html(
                        "li",
                        self.source_link(
                            source.get_handle(),
                            authorstring + source.get_title(),
                            source.get_gramps_id(),
                            cindex,
                            uplink=self.uplink,
                        ),
                    )
                else:
                    list_html = Html("li", "None")

                ordered1 = Html("ol", id="citr")
                citation_ref_list = citation.get_ref_list()
                for key, sref in citation_ref_list:
                    cit_ref_li = Html("li", id="sref%d%s" % (cindex, key))
                    tmp = Html("ul")
                    conf = conf_strings.get(sref.confidence, self._("Unknown"))
                    if conf == conf_strings[Citation.CONF_NORMAL]:
                        conf = None
                    else:
                        conf = self._(conf)
                    for label, data in [
                        [self._("Date"), self.rlocale.get_date(sref.date)],
                        [self._("Page"), sref.page],
                        [self._("Confidence"), conf],
                    ]:
                        if data:
                            tmp += Html(
                                "li",
                                self._("%(str1)s: %(str2)s")
                                % {"str1": label, "str2": data},
                            )
                    if self.create_media:
                        for media_ref in sref.get_media_list():
                            media_handle = media_ref.get_reference_handle()
                            media = self.r_db.get_media_from_handle(media_handle)
                            if media:
                                mime_type = media.get_mime_type()
                                if mime_type:
                                    if mime_type.startswith("image/"):
                                        (
                                            real_path,
                                            new_path,
                                        ) = self.report.prepare_copy_media(media)
                                        newpath = self.report.build_url_fname(
                                            new_path, uplink=self.uplink
                                        )
                                        self.report.copy_file(
                                            media_path_full(
                                                self.r_db, media.get_path()
                                            ),
                                            real_path,
                                        )

                                        tmp += Html(
                                            "li",
                                            self.media_link(
                                                media_handle,
                                                newpath,
                                                media.get_description(),
                                                self.uplink,
                                                usedescr=False,
                                            ),
                                            inline=True,
                                        )

                                    else:
                                        tmp += Html(
                                            "li",
                                            self.doc_link(
                                                media_handle,
                                                media.get_description(),
                                                self.uplink,
                                                usedescr=False,
                                            ),
                                            inline=True,
                                        )
                    for handle in sref.get_note_list():
                        this_note = self.r_db.get_note_from_handle(handle)
                        if this_note is not None:
                            note_format = self.get_note_format(this_note, True)
                            tmp += Html(
                                "li",
                                self._("%(str1)s: %(str2)s")
                                % {
                                    "str1": str(this_note.get_type()),
                                    "str2": note_format,
                                },
                            )
                    if tmp:
                        cit_ref_li += tmp
                        ordered1 += cit_ref_li

                if citation_ref_list:
                    list_html += ordered1
                ordered += list_html
            section += ordered

        # return section to its caller
        return section

    def family_map_link(self, handle, url):
        """
        Creates a link to the family map

        @param: handle -- The family handle
        @param: url    -- url to be linked
        """
        self.report.fam_link[handle] = url
        return Html(
            "a",
            self._("Family Map"),
            href=url,
            title=self._("Family Map"),
            class_="familymap",
            inline=True,
        )

    def display_spouse(self, partner, family, place_lat_long):
        """
        Display an individual's partner

        @param: partner        -- The partner
        @param: family         -- The family
        @param: place_lat_long -- For use in Family Map Pages. This will be
                                  None if called from Family pages, which do
                                  not create a Family Map
        """
        gender = partner.get_gender()
        reltype = family.get_relationship()

        rtype = self._(str(family.get_relationship().xml_str()))

        if reltype == FamilyRelType.MARRIED:
            if gender == Person.FEMALE:
                relstr = self._("Wife")
            elif gender == Person.MALE:
                relstr = self._("Husband")
            else:
                relstr = self._("Partner")
        else:
            relstr = self._("Partner")

        # display family relationship status, and add spouse to FamilyMapPages
        if self.familymappages:
            self._get_event_place(partner, place_lat_long)

        trow = Html("tr", class_="BeginFamily") + (
            Html("td", rtype, class_="ColumnType", inline=True),
            Html("td", relstr, class_="ColumnAttribute", inline=True),
        )

        tcell = Html("td", class_="ColumnValue")
        trow += tcell

        tcell += self.new_person_link(partner.get_handle(), uplink=True, person=partner)
        birth = death = ""
        bd_event = get_birth_or_fallback(self.r_db, partner)
        if bd_event:
            birth = self.rlocale.get_date(bd_event.get_date_object())
        dd_event = get_death_or_fallback(self.r_db, partner)
        if dd_event:
            death = self.rlocale.get_date(dd_event.get_date_object())

        if death == "":
            death = "..."
        tcell += " ( * ", birth, " + ", death, " )"

        return trow

    def display_child_link(self, chandle):
        """
        display child link ...

        @param: chandle -- Child handle
        """
        return self.new_person_link(chandle, uplink=True)

    def new_person_link(
        self, person_handle, uplink=False, person=None, name_style=_NAME_STYLE_DEFAULT
    ):
        """
        creates a link for a person. If a page is generated for the person, a
        hyperlink is created, else just the name of the person. The returned
        vale will be an Html object if a hyperlink is generated, otherwise
        just a string

        @param: person_handle -- Person in database
        @param: uplink        -- If True, then "../../../" is inserted in
                                 front of the result
        @param: person        -- Person object. This does not need to be
                                 passed. It should be passed if the person
                                 object has already been retrieved, as it
                                 will be used to improve performance
        """
        result = self.report.obj_dict.get(Person).get(person_handle)

        # construct link, name and gid
        if result is None:
            # The person is not included in the webreport
            link = ""
            if person is None:
                person = self.r_db.get_person_from_handle(person_handle)
            if person:
                name = self.report.get_person_name(person)
                gid = person.get_gramps_id()
            else:
                name = self._("Unknown")
                gid = ""
        else:
            # The person has been encountered in the web report, but this does
            # not necessarily mean that a page has been generated
            (link, name, gid) = result

        name = html_escape(name)
        # construct the result
        if not self.noid and gid != "":
            gid_html = Html("span", " [%s]" % gid, class_="grampsid", inline=True)
        else:
            gid_html = ""

        if link != "":
            url = self.report.build_url_fname(link, uplink=uplink)
            hyper = Html("a", name, gid_html, href=url, inline=True)
        else:
            hyper = name + str(gid_html)

        return hyper

    def media_link(self, media_handle, img_url, name, uplink=False, usedescr=True):
        """
        creates and returns a hyperlink to the thumbnail image

        @param: media_handle -- Photo handle from report database
        @param: img_url      -- Thumbnail url
        @param: name         -- Photo description
        @param: uplink       -- If True, then "../../../" is inserted in front
                                of the result.
        @param: usedescr     -- Add media description
        """
        url = (
            self.report.build_url_fname(media_handle, "img", uplink, image=True)
            + self.ext
        )
        name = html_escape(name)

        # begin thumbnail division
        with Html("div", class_="thumbnail") as thumbnail:
            # begin hyperlink
            if not self.create_thumbs_only:
                hyper = Html("a", href=url, title=name) + (
                    Html("img", src=img_url, alt=name)
                )
            else:
                hyper = Html("img", src=img_url, alt=name)
            thumbnail += hyper

            if usedescr:
                hyper += Html("p", name, inline=True)
        return thumbnail

    def doc_link(self, handle, name, uplink=False, usedescr=True):
        """
        create a hyperlink for the media object and returns it

        @param: handle   -- Document handle
        @param: name     -- Document name
        @param: uplink   -- If True, then "../../../" is inserted in front of
                            the result.
        @param: usedescr -- Add description to hyperlink
        """
        url = self.report.build_url_fname_html(handle, "img", uplink)
        name = html_escape(name)

        # begin thumbnail division
        with Html("div", class_="thumbnail") as thumbnail:
            document_url = self.report.build_url_image("document.png", "images", uplink)

            if not self.create_thumbs_only:
                document_link = Html("a", href=url, title=name) + (
                    Html("img", src=document_url, alt=name)
                )
            else:
                document_link = Html("img", src=document_url, alt=name)

            if usedescr:
                document_link += Html("br") + (Html("span", name, inline=True))
            thumbnail += document_link
        return thumbnail

    def heatmap_link(self, name, uplink=False):
        """
        Returns a hyperlink for heatmap link

        @param: name   -- repository title
        @param: uplink -- If True, then "../../../" is inserted in front of
                          the result.
        """
        url = self.report.build_url_fname_html(name, "heat", uplink)

        hyper = Html(
            "a",
            html_escape(self._(name)),
            href=url.replace(" ", ""),
            title=html_escape(self._(name)),
        )

        # return hyperlink to its callers
        return hyper

    def place_link(self, handle, name, gid=None, uplink=False):
        """
        Returns a hyperlink for place link

        @param: handle -- repository handle from report database
        @param: name   -- repository title
        @param: gid    -- gramps id
        @param: uplink -- If True, then "../../../" is inserted in front of
                          the result.
        """
        url = self.report.build_url_fname_html(handle, "plc", uplink)

        hyper = Html("a", html_escape(name), href=url, title=html_escape(name))
        if not self.noid and gid:
            hyper += Html("span", " [%s]" % gid, class_="grampsid", inline=True)

        # return hyperlink to its callers
        return hyper

    def dump_place(self, place, table):
        """
        Dump a place's information from within the database

        @param: place -- Place object from the database
        @param: table -- Table from Placedetail
        """
        # add table body
        tbody = Html("tbody")
        table += tbody

        gid = place.gramps_id
        if not self.noid and gid:
            trow = Html("tr") + (
                Html("td", self._("Gramps ID"), class_="ColumnAttribute", inline=True),
                Html("td", gid, class_="ColumnValue", inline=True),
            )
            tbody += trow

        data = place.get_latitude()
        v_lat, v_lon = conv_lat_lon(
            data, "0.0", coord_formats[self.report.options["coord_format"]]
        )
        if data and not v_lat:
            data += self._(":")
            # We use the same message as in:
            # gramps/gui/editors/editplace.py
            # gramps/gui/editors/editplaceref.py
            data += self._(
                "Invalid latitude\n(syntax: 18\\u00b09'48.21\"S,"
                " -18.2412 or -18:9:48.21)"
            )
            # We need to convert "\\u00b0" to "&deg;" for html
            data = data.replace("\\u00b0", "&deg;")
        if data != "":
            trow = Html("tr") + (
                Html("td", self._("Latitude"), class_="ColumnAttribute", inline=True),
                Html("td", v_lat, class_="ColumnValue", inline=True),
            )
            tbody += trow
        data = place.get_longitude()
        v_lat, v_lon = conv_lat_lon(
            "0.0", data, coord_formats[self.report.options["coord_format"]]
        )
        if data and not v_lon:
            data += self._(":")
            # We use the same message as in:
            # gramps/gui/editors/editplace.py
            # gramps/gui/editors/editplaceref.py
            data += self._(
                "Invalid longitude\n(syntax: 18\\u00b09'48.21\"E,"
                " -18.2412 or -18:9:48.21)"
            )
            # We need to convert "\\u00b0" to "&deg;" for html
            data = data.replace("\\u00b0", "&deg;")
        if data != "":
            trow = Html("tr") + (
                Html("td", self._("Longitude"), class_="ColumnAttribute", inline=True),
                Html("td", v_lon, class_="ColumnValue", inline=True),
            )
            tbody += trow

        mlocation = get_main_location(self.r_db, place)
        for label, data in [
            (self._("Street"), mlocation.get(PlaceType.STREET, "")),
            (self._("Locality"), mlocation.get(PlaceType.LOCALITY, "")),
            (self._("City"), mlocation.get(PlaceType.CITY, "")),
            (self._("Church Parish"), mlocation.get(PlaceType.PARISH, "")),
            (self._("County"), mlocation.get(PlaceType.COUNTY, "")),
            (self._("State/ Province"), mlocation.get(PlaceType.STATE, "")),
            (self._("Postal Code"), place.get_code()),
            (self._("Province"), mlocation.get(PlaceType.PROVINCE, "")),
            (self._("Country"), mlocation.get(PlaceType.COUNTRY, "")),
        ]:
            if data:
                trow = Html("tr") + (
                    Html("td", label, class_="ColumnAttribute", inline=True),
                    Html("td", data, class_="ColumnValue", inline=True),
                )
                tbody += trow

        # display all related locations
        for placeref in place.get_placeref_list():
            place_date = self.rlocale.get_date(placeref.get_date_object())
            if place_date != "":
                parent_place = self.r_db.get_place_from_handle(placeref.ref)
                parent_name = parent_place.get_name().get_value()
                trow = Html("tr") + (
                    Html(
                        "td", self._("Locations"), class_="ColumnAttribute", inline=True
                    ),
                    Html("td", parent_name, class_="ColumnValue", inline=True),
                    Html("td", place_date, class_="ColumnValue", inline=True),
                )
                tbody += trow

        altloc = place.get_alternative_names()
        if altloc:
            tbody += Html("tr") + Html("td", "&nbsp;", colspan=2)
            date_msg = self._("Date range in which the name is valid.")
            trow = Html("tr") + (
                Html(
                    "th",
                    self._("Alternate Names"),
                    colspan=1,
                    class_="ColumnAttribute",
                    inline=True,
                ),
                Html(
                    "th",
                    self._("Language"),
                    colspan=1,
                    class_="ColumnAttribute",
                    inline=True,
                ),
                Html("th", date_msg, colspan=1, class_="ColumnAttribute", inline=True),
            )
            tbody += trow
            for loc in altloc:
                place_date = self.rlocale.get_date(loc.date)
                trow = Html("tr") + (
                    Html("td", loc.get_value(), class_="ColumnValue", inline=True),
                    Html("td", loc.get_language(), class_="ColumnValue", inline=True),
                    Html("td", place_date, class_="ColumnValue", inline=True),
                )
                tbody += trow

        altloc = place.get_alternate_locations()
        if altloc:
            tbody += Html("tr") + Html("td", "&nbsp;", colspan=2)
            trow = Html("tr") + (
                Html(
                    "th",
                    self._("Alternate Locations"),
                    colspan=2,
                    class_="ColumnAttribute",
                    inline=True,
                ),
            )
            tbody += trow
            for loc in (nonempt for nonempt in altloc if not nonempt.is_empty()):
                for label, data in [
                    (self._("Street"), loc.street),
                    (self._("Locality"), loc.locality),
                    (self._("City"), loc.city),
                    (self._("Church Parish"), loc.parish),
                    (self._("County"), loc.county),
                    (self._("State/ Province"), loc.state),
                    (self._("Postal Code"), loc.postal),
                    (self._("Country"), loc.country),
                ]:
                    if data:
                        trow = Html("tr") + (
                            Html("td", label, class_="ColumnAttribute", inline=True),
                            Html("td", data, class_="ColumnValue", inline=True),
                        )
                        tbody += trow
                tbody += Html("tr") + Html("td", "&nbsp;", colspan=2)

        # Tags
        tags = self.show_tags(place)
        if tags and self.report.inc_tags:
            trow = Html("tr") + (
                Html("td", self._("Tags"), class_="ColumnAttribute", inline=True),
                Html("td", tags, class_="ColumnValue", inline=True),
            )
            tbody += trow

        # enclosed by
        tbody += Html("tr") + Html("td", "&nbsp;")
        trow = Html("tr") + (
            Html("th", self._("Enclosed By"), class_="ColumnAttribute", inline=True),
        )
        tbody += trow

        def sort_by_enclosed_by(obj):
            """
            Sort by enclosed by
            """
            place_name = ""
            parent_place = self.r_db.get_place_from_handle(obj.ref)
            if parent_place:
                place_name = parent_place.get_name().get_value()
            return normalize("NFD", place_name)

        def sort_by_encl(obj):
            """
            Sort by encloses
            """
            return normalize("NFD", obj[0])

        for placeref in sorted(place.get_placeref_list(), key=sort_by_enclosed_by):
            parent_place = self.r_db.get_place_from_handle(placeref.ref)
            if parent_place:
                place_name = parent_place.get_name().get_value()
                if parent_place.handle in self.report.obj_dict[Place]:
                    place_hyper = self.place_link(
                        parent_place.handle, place_name, uplink=self.uplink
                    )
                else:
                    place_hyper = place_name
                trow = Html("tr") + (
                    Html("td", place_hyper, class_="ColumnPlace", inline=True)
                )
                tbody += trow

        # enclose
        tbody += Html("tr") + Html("td", "&nbsp;")
        trow = Html("tr") + (
            Html("th", self._("Place Encloses"), class_="ColumnAttribute", inline=True),
        )
        tbody += trow
        encloses = []
        for link in self.r_db.find_backlink_handles(
            place.handle, include_classes=["Place"]
        ):
            child_place = self.r_db.get_place_from_handle(link[1])
            placeref = None
            for placeref in child_place.get_placeref_list():
                if placeref.ref == place.handle:
                    place_name = child_place.get_name().get_value()
                    if link[1] in self.report.obj_dict[Place]:
                        encloses.append((place_name, link[1]))
                    else:
                        encloses.append((place_name, ""))
        for name, handle in sorted(encloses, key=sort_by_encl):
            place_name = child_place.get_name().get_value()
            if handle and handle in self.report.obj_dict[Place]:
                place_hyper = self.place_link(handle, name, uplink=self.uplink)
            else:
                place_hyper = name
            trow = Html("tr") + (
                Html("td", place_hyper, class_="ColumnPlace", inline=True)
            )
            tbody += trow

        # return place table to its callers
        return table

    def repository_link(self, repository_handle, name, gid=None, uplink=False):
        """
        Returns a hyperlink for repository links

        @param: repository_handle -- repository handle from report database
        @param: name              -- repository title
        @param: gid               -- gramps id
        @param: uplink            -- If True, then "../../../" is inserted in
                                     front of the result.
        """
        url = self.report.build_url_fname_html(repository_handle, "repo", uplink)
        name = html_escape(name)

        hyper = Html("a", name, href=url, title=name)

        if not self.noid and gid:
            hyper += Html("span", "[%s]" % gid, class_="grampsid", inline=True)
        return hyper

    def dump_repository_ref_list(self, repo_ref_list):
        """
        Dumps the repository

        @param: repo_ref_list -- The list of repositories references
        """
        if not repo_ref_list:
            return None
        # Repository list division...
        with Html("div", class_="subsection", id="repositories") as repositories:
            repositories += Html("h4", self._("Repositories"), inline=True)

            with Html("table", class_="infolist " + self.dir) as table:
                repositories += table

                thead = Html("thead")
                table += thead

                trow = Html("tr") + (
                    Html("th", self._("Number"), class_="ColumnRowLabel", inline=True),
                    Html("th", self._("Title"), class_="ColumnName", inline=True),
                    Html("th", self._("Type"), class_="ColumnName", inline=True),
                    Html("th", self._("Call number"), class_="ColumnName", inline=True),
                )
                thead += trow

                tbody = Html("tbody")
                table += tbody

                index = 1
                for repo_ref in repo_ref_list:
                    repo = self.r_db.get_repository_from_handle(repo_ref.ref)
                    if repo:
                        trow = Html("tr") + (
                            Html("td", index, class_="ColumnRowLabel", inline=True),
                            Html(
                                "td",
                                self.repository_link(
                                    repo_ref.ref,
                                    repo.get_name(),
                                    repo.get_gramps_id(),
                                    self.uplink,
                                ),
                            ),
                            Html(
                                "td",
                                self._(repo_ref.get_media_type().xml_str()),
                                class_="ColumnName",
                            ),
                            Html("td", repo_ref.get_call_number(), class_="ColumnName"),
                        )
                        tbody += trow
                        index += 1
        return repositories

    def dump_residence(self, has_res):
        """
        Creates a residence from the database

        @param: has_res -- The residence to use
        """
        if not has_res:
            return None

        # begin residence division
        with Html("div", class_="content Residence") as residence:
            residence += Html("h4", self._("Residence"), inline=True)

            with Html("table", class_="infolist place") as table:
                residence += table

                place_handle = has_res.get_place_handle()
                if place_handle:
                    place = self.r_db.get_place_from_handle(place_handle)
                    if place:
                        self.dump_place(place, table)

                descr = has_res.get_description()
                if descr:
                    trow = Html("tr")
                    if len(table) == 3:
                        # append description row to tbody element
                        # of dump_place
                        table[-2] += trow
                    else:
                        # append description row to table element
                        table += trow

                    trow.extend(
                        Html(
                            "td",
                            self._("Description"),
                            class_="ColumnAttribute",
                            inline=True,
                        )
                    )
                    trow.extend(Html("td", descr, class_="ColumnValue", inline=True))

        # return information to its callers
        return residence

    def display_bkref(self, bkref_list, depth):
        """
        Display a reference list for an object class

        @param: bkref_list -- The reference list
        @param: depth      -- The style of list to use
        """
        list_style = "1", "a", "I", "A", "i"
        ordered = Html("ol", class_="Col1", role="Volume-n-Page")
        ordered.attr += " type=%s" % list_style[depth]
        if depth > len(list_style):
            return ""

        # Sort by the role of the object at the bkref_class, bkref_handle
        def sort_by_role(obj):
            """
            Sort by role
            """
            if obj[2] == "Primary":
                role = "0"
            elif obj[2] == "Family":
                role = "1"
            else:
                if self.reference_sort:
                    role = obj[2]  # name
                elif len(obj[2].split(":")) > 1:
                    dummy_cal, role = obj[2].split(":")  # date in ISO format
                    # dummy_cal is the original calendar. remove it.
                    if len(role.split(" ")) == 2:
                        # for sort, remove the modifier before, after...
                        (dummy_modifier, role) = role.split(" ")
                else:
                    role = "3"
            return role

        for bkref_class, bkref_handle, role in sorted(
            bkref_list, key=lambda x: sort_by_role(x)
        ):
            list_html = Html("li")
            path = self.report.obj_dict[bkref_class][bkref_handle][0]
            name = self.report.obj_dict[bkref_class][bkref_handle][1]
            gid = self.report.obj_dict[bkref_class][bkref_handle][2]
            if role != "":
                if self.reference_sort:
                    role = self.birth_death_dates(gid)
                elif role[1:2] == ":":
                    # format of role is role_type:ISO date string
                    if role.count(":") > 1:
                        print(
                            "Invalid date :",
                            role[2:],
                            " for individual with ID:",
                            gid,
                            ". Please, use the 'verify the data' tool to correct this.",
                        )
                        cal, role = role.split(":", 1)
                    else:
                        cal, role = role.split(":")

                    # cal is the original calendar

                    # convert ISO date to Date for translation.
                    # all modifiers are in english, so convert them
                    # to the local language
                    if len(role.split(" - ")) > 1:
                        (date1, date2) = role.split(" - ")
                        role = self._("between") + " " + date1 + " "
                        role += self._("and") + " " + date2
                    elif len(role.split(" ")) == 2:
                        (pref, date) = role.split(" ")
                        if "aft" in pref:
                            role = self._("after") + " " + date
                        elif "bef" in pref:
                            role = self._("before") + " " + date
                        elif pref in ("abt", "about"):
                            role = self._("about") + " " + date
                        elif "c" in pref:
                            role = self._("circa") + " " + date
                        elif "around" in pref:
                            role = self._("around") + " " + date
                    # parse is done in the default language
                    date = _dp.parse(role)
                    # reset the date to the original calendar
                    cdate = date.to_calendar(Date.calendar_names[int(cal)])
                    ldate = self.rlocale.get_date(cdate)
                    evtype = self.event_for_date(gid, cdate)
                    if evtype:
                        evtype = " " + evtype
                    role = " (%s) " % (ldate + evtype)
                else:
                    role = " (%s) " % self._(role)
            ordered += list_html
            if path == "":
                list_html += name
                list_html += self.display_bkref(
                    self.report.bkref_dict[bkref_class][bkref_handle], depth + 1
                )
            else:
                url = self.report.build_url_fname(path, uplink=self.uplink)
                if not self.noid and gid != "":
                    gid_html = Html(
                        "span", " [%s]" % gid, class_="grampsid", inline=True
                    )
                else:
                    gid_html = ""
                list_html += Html("a", href=url) + name + role + gid_html
        return ordered

    def event_for_date(self, gid, date):
        """
        return the event type

        @param: gid  -- the person gramps ID
        @param: date -- the event to look for this date
        """
        pers = self.r_db.get_person_from_gramps_id(gid)
        if pers:
            evt_ref_list = pers.get_event_ref_list()
            if evt_ref_list:
                for evt_ref in evt_ref_list:
                    evt = self.r_db.get_event_from_handle(evt_ref.ref)
                    if evt:
                        evdate = evt.get_date_object()
                        # convert date to gregorian
                        _date = str(evdate.to_calendar("gregorian"))
                        if _date == str(date):
                            return self._(str(evt.get_type()))
        return ""

    def birth_death_dates(self, gid):
        """
        return the birth and death date for the person

        @param: gid  -- the person gramps ID
        """
        pers = self.r_db.get_person_from_gramps_id(gid)
        if pers:
            birth = death = ""
            evt_birth = get_birth_or_fallback(self.r_db, pers)
            if evt_birth:
                birthd = evt_birth.get_date_object()
                # convert date to gregorian to avoid strange years
                birth = str(birthd.to_calendar("gregorian").get_year())
            evt_death = get_death_or_fallback(self.r_db, pers)
            if evt_death:
                deathd = evt_death.get_date_object()
                # convert date to gregorian to avoid strange years
                death = str(deathd.to_calendar("gregorian").get_year())
            return "(%s-%s)" % (birth, death)
        else:
            return ""

    def display_bkref_list(self, obj_class, obj_handle):
        """
        Display a reference list for an object class

        @param: obj_class  -- The object class to use
        @param: obj_handle -- The handle to use
        """
        bkref_list = self.report.bkref_dict[obj_class][obj_handle]
        if not bkref_list:
            return None
        # begin references division and title
        with Html("div", class_="subsection", id="references") as section:
            section += Html("h4", self._("References"), inline=True)
            depth = 0
            ordered = self.display_bkref(bkref_list, depth)
            section += ordered
        return section

    # -----------------------------------------------------------------------
    #              # Web Page Fortmatter and writer
    # -----------------------------------------------------------------------
    def xhtml_writer(self, htmlinstance, output_file, sio, date):
        """
        Will format, write, and close the file

        @param: output_file  -- Open file that is being written to
        @param: htmlinstance -- Web page created with libhtml
                                gramps/plugins/lib/libhtml.py
        """
        htmlinstance.write(partial(print, file=output_file))

        # closes the file
        self.report.close_file(output_file, sio, date)

    def create_toggle(self, element):
        """
        will produce a toggle button

        @param: element -- The html element name
        """
        use_toggle = self.report.options["toggle"]
        if use_toggle:
            viewbox = "0 0 100 100"
            points = "5.9,88.2 50,11.8 94.1,88.2"
            svg = Html("svg", viewBox=viewbox, class_="triangle", inline=False)
            svg += Html("polygon", points=points)
            toggle_name = "toggle_" + element
            id_name = "icon_" + element
            with Html(
                "h4", onclick="toggleContent('" + toggle_name + "', '" + id_name + "');"
            ) as toggle:
                toggle += Html("button", svg, id=id_name, class_="icon")
        else:
            toggle = Html("h4", inline=True)
        return toggle
