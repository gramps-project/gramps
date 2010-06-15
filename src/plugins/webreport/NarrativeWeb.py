#
# encoding: utf-8
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007       Johan Gonqvist <johan.gronqvist@gmail.com>
# Copyright (C) 2007-2009  Gary Burton <gary.burton@zen.co.uk>
# Copyright (C) 2007-2009  Stephane Charette <stephanecharette@gmail.com>
# Copyright (C) 2008-2009  Brian G. Matherly
# Copyright (C) 2008       Jason M. Simanek <jason@bohemianalps.com>
# Copyright (C) 2008-2010  Rob G. Healey <robhealey1@gmail.com>	
# Copyright (C) 2010       Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2010       Serge Noiraud
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Narrative Web Page generator.
"""
#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from __future__ import print_function
from functools import partial
import gc
import os
import sys
import re
try:
    from hashlib import md5
except ImportError:
    from md5 import md5
import time, datetime
import locale
import shutil
import codecs
import tarfile
import tempfile
from cStringIO import StringIO
from textwrap import TextWrapper
from unicodedata import normalize
from collections import defaultdict

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".NarrativeWeb")

#------------------------------------------------------------------------
# GRAMPS module
#------------------------------------------------------------------------
from gen.ggettext import sgettext as _
import gen.lib
from gen.lib import UrlType, date, FamilyRelType, NoteType, EventRoleType
import const
import Sort
from gen.plug.menu import PersonOption, NumberOption, StringOption, \
                          BooleanOption, EnumeratedListOption, FilterOption, \
                          NoteOption, MediaOption, DestinationOption
from gen.plug.report import ( Report, Bibliography, CSS_FILES )
from gen.plug.report import utils as ReportUtils
from gui.plug.report import MenuReportOptions
                        
import Utils
import constfunc
from gui.utils import ProgressMeter
import ThumbNails
import ImgManip
import gen.mime
from QuestionDialog import ErrorDialog, WarningDialog
from gen.display.name import displayer as _nd 
from DateHandler import displayer as _dd
from gen.proxy import PrivateProxyDb, LivingProxyDb
from libhtmlconst import _CHARACTER_SETS, _CC, _COPY_OPTIONS

# import HTML Class from
# src/plugins/lib/libhtml.py
from libhtml import Html

# import styled notes from
# src/plugins/lib/libhtmlbackend.py
from libhtmlbackend import HtmlBackend

from libgedcom import make_gedcom_date

#------------------------------------------------------------------------
#
# constants
#
#------------------------------------------------------------------------
# Translatable strings for variables within this plugin
# gettext carries a huge footprint with it.
AHEAD = _("Attributes")
BIRTH = _("Birth")
CITY = _("City")
COUNTY = _("County")
COUNTRY = _("Country")
DEATH = _("Death")
DHEAD = _("Date")
DESCRHEAD = _("Description")
_EVENT = _("Event")
GRAMPSID = _("Gramps ID")
LATITUDE = _("Latitude")
LOCATIONS = _("Alternate Locations")
LONGITUDE = _("Longitude")
NHEAD = _("Notes")
PARENTS = _("Parents")
PARISH = _("Church Parish")
_PARTNER = _("Partner")
PHEAD = _("Place")
_PERSON = _("Person")
PHONE = _("Phone")
POSTAL = _("Postal Code")
SHEAD = _("Sources")
ST = _("Status")
STATE = _("State/ Province")
STREET = _("Street")
THEAD = _("Type")
TMPL = _("Temple")
VHEAD = _("Value")

# Events that are usually a family event
_EVENTMAP = [ gen.lib.EventType.MARRIAGE, gen.lib.EventType.MARR_ALT,
              gen.lib.EventType.MARR_SETTL, gen.lib.EventType.MARR_LIC,
              gen.lib.EventType.MARR_CONTR, gen.lib.EventType.MARR_BANNS,
              gen.lib.EventType.ENGAGEMENT, gen.lib.EventType.DIVORCE,
              gen.lib.EventType.DIV_FILING ]
  
# define clear blank line for proper styling
fullclear = Html("div", class_ = "fullclear", inline = True)

# Names for stylesheets
_NARRATIVESCREEN = "narrative-screen.css"
_NARRATIVEPRINT = "narrative-print.css"

# variables for alphabet_navigation()
_KEYPERSON, _KEYPLACE, _KEYEVENT, _ALPHAEVENT = 0, 1, 2, 3

# Web page filename extensions
_WEB_EXT = ['.html', '.htm', '.shtml', '.php', '.php3', '.cgi']

_INCLUDE_LIVING_VALUE = 99 # Arbitrary number
_NAME_COL  = 3

_DEFAULT_MAX_IMG_WIDTH = 800   # resize images that are wider than this (settable in options)
_DEFAULT_MAX_IMG_HEIGHT = 600  # resize images that are taller than this (settable in options)
_WIDTH = 160
_HEIGHT = 50
_VGAP = 10
_HGAP = 30
_SHADOW = 5
_XOFFSET = 5
_WRONGMEDIAPATH = []

wrapper = TextWrapper()
wrapper.break_log_words = True
wrapper.width = 20

_html_dbl_quotes = re.compile(r'([^"]*) " ([^"]*) " (.*)', re.VERBOSE)
_html_sng_quotes = re.compile(r"([^']*) ' ([^']*) ' (.*)", re.VERBOSE)
_html_replacement = {
    "&"  : "&#38;",
    ">"  : "&#62;",
    "<"  : "&#60;",
    }

# This command then defines the 'html_escape' option for escaping
# special characters for presentation in HTML based on the above list.
def html_escape(text):
    """Convert the text and replace some characters with a &# variant."""

    # First single characters, no quotes
    text = ''.join([_html_replacement.get(c, c) for c in text])

    # Deal with double quotes.
    while 1:
        m = _html_dbl_quotes.match(text)
        if not m:
            break
        text = m.group(1) + '&#8220;' + m.group(2) + '&#8221;' + m.group(3)
    # Replace remaining double quotes.
    text = text.replace('"', '&#34;')

    # Deal with single quotes.
    text = text.replace("'s ", '&#8217;s ')
    while 1:
        m = _html_sng_quotes.match(text)
        if not m:
            break
        text = m.group(1) + '&#8216;' + m.group(2) + '&#8217;' + m.group(3)
    # Replace remaining single quotes.
    text = text.replace("'", '&#39;')

    return text

def name_to_md5(text):
    """This creates an MD5 hex string to be used as filename."""
    return md5(text).hexdigest()

def conf_priv(obj):
    if obj.get_privacy() != 0:
        return ' priv="%d"' % obj.get_privacy()
    else:
        return ''

def get_gendex_data(database, event_ref):
    """
    Given an event, return the date and place a strings
    """
    doe = "" # date of event
    poe = "" # place of event
    if event_ref:
        event = database.get_event_from_handle(event_ref.ref)
        if event:
            date = event.get_date_object()
            doe = format_date(date)
            if event.get_place_handle():
                place_handle = event.get_place_handle()
                if place_handle:
                    place = database.get_place_from_handle(place_handle)
                    if place:
                        location = place.get_main_location()
                        if location and not location.is_empty():
                            poe = ", ".join(l for l in
                                            [
                                                location.get_city().strip(),
                                                location.get_state().strip(),
                                                location.get_country().strip()
                                            ] if l)
    return doe, poe

def format_date(date):
    start = date.get_start_date()
    if start != gen.lib.Date.EMPTY:
        cal = date.get_calendar()
        mod = date.get_modifier()
        quality = date.get_quality()
        if mod == gen.lib.Date.MOD_SPAN:
            val = "FROM %s TO %s" % (
                make_gedcom_date(start, cal, mod, quality), 
                make_gedcom_date(date.get_stop_date(), cal, mod, quality))
        elif mod == gen.lib.Date.MOD_RANGE:
            val = "BET %s AND %s" % (
                make_gedcom_date(start, cal, mod, quality), 
                make_gedcom_date(date.get_stop_date(), cal, mod, quality))
        else:
            val = make_gedcom_date(start, cal, mod, quality)
        return val
    return ""

def copy_thumbnail(report, handle, photo, region=None):
    """
    Given a handle (and optional region) make (if needed) an
    up-to-date cache of a thumbnail, and call report.copy_file
    to copy the cached thumbnail to the website.
    Return the new path to the image.
    """
    to_dir = report.build_path('thumb', handle)
    if region:
        to_path = os.path.join(to_dir, handle) + ('%d,%d-%d,%d.png' % region)
    else:
        to_path = os.path.join(to_dir, handle) + '.png'
    if photo.get_mime_type():
        from_path = ThumbNails.get_thumbnail_path(Utils.media_path_full(
                                                  report.database,
                                                  photo.get_path()),
                                                  photo.get_mime_type(),
                                                  region)
        if not os.path.isfile(from_path):
            from_path = os.path.join(const.IMAGE_DIR, "document.png")
    else:
        from_path = os.path.join(const.IMAGE_DIR, "document.png")
    report.copy_file(from_path, to_path)
    return to_path

class BasePage(object):
    """
    This is the base class to write certain HTML pages.
    """
    
    def __init__(self, report, title, gid = None):
        """
        Holds all of the things that each class needs to have...

        @param: report - instance of NavWebReport
        @param: title - text for the title
        @param: gid - Gramps ID
        """
        self.up = False
        # class to do conversion of styled notes to html markup
        self._backend = HtmlBackend()
        self._backend.build_link = report.build_link

        self.report = report
        self.title_str = title
        self.gid = gid
        self.src_list = {}

        self.page_title = ""

        self.author = Utils.get_researcher().get_name()
        if self.author:
            self.author = self.author.replace(',,,', '')

        # TODO. All of these attributes are not necessary, because we have
        # also the options in self.options.  Besides, we need to check which
        # are still required.
        self.html_dir = report.options['target']
        self.ext = report.options['ext']
        self.noid = report.options['nogid']
        self.linkhome = report.options['linkhome']
        self.create_media = report.options['gallery']
        self.inc_events = report.options['inc_events']

        # options for PlaceMaps for PlacePages
        self.placemaps = report.options["placemaps"]

    def _create_place_map(self, placedetail, head, latitude, longitude, place_title):
        """
        will create the place map

        @param: placedetail -- Html instance page
        @param: latitude -- GPS Latitude from place
        @param: Longitude -- GPS Longitude from place
        """

        # add Mapstraction CSS
        fname = "/".join(["styles", "mapstraction.css"])
        url = self.report.build_url_fname(fname, None, self.up)
        head += Html("link", href = url, type = "text/css", media = "screen", 
            rel = "stylesheet", indent = False)

        # add googlev3 specific javascript code
        head += Html("script", type = "text/javascript", 
            src = "http://maps.google.com/maps/api/js?sensor=false", inline = True)

        # add openlayers specific javascript code
        head += Html("script", src = "http://openlayers.org/api/OpenLayers.js", inline = True)

        # add mapstraction javascript code
        fname = "/".join(["mapstraction", "mxn.js"])
        url = self.report.build_url_fname(fname, None, self.up)
        url += "?(googlev3,openlayers)"
        head += Html("script", src = url, inline = True)

        # Place Map division
        with Html("div", id = "mapstraction") as mapstraction:
            placedetail += mapstraction

            # section title
            mapstraction += Html("h4", _("Place Map"), inline = True)

            # begin middle division
            with Html("div", id = "middle") as middle:
                mapstraction += middle

                # begin inline javascript code
                # because jsc is a string, it does NOT have to properly indented
                with Html("script", type = "text/javascript") as jsc:
                    middle += jsc

                    jsc += """
                            //<![CDATA[

                            var map;
                            var pprovider = 'googlev3';
                            var latlon;
                            var icon = 'mainmap';

                            function initialize() {

                                // create mxn object
                                map = new mxn.Mapstraction('googlev3','googlev3');

                                // add map controls to image
                                map.addControls({
                                    pan: true,
                                    zoom: 'large',
                                    scale: true,
                                    map_type: true
                                });

                                latlon = new mxn.LatLonPoint(%s, %s);""" % (latitude, longitude)

                    jsc += """
                                // put map on page
                                map.setCenterAndZoom(latlon, 9);
  
                                //add a marker
                                add_marker();
                            }

                            function add_marker() {
                                var marker;
                                marker = new mxn.Marker(latlon);

                                // openlayers mapstraction problem here : drift if anchor.
                                if ( provider == 'googlev3' ) {
                                    marker.setIcon('../../../images/gramps-geo-' +icon+ '.png',
                                        [22,22],
                                        [0,22]);
                                } else {
                                    marker.setIcon('../../../images/gramps-geo-' +icon+ '.png',
                                        [22,22]);
                                };
                                map.addMarker(marker,true);
                            }

                            function changeprovider() {
                                if ( pprovider == 'googlev3') {
                                    provider = 'openlayers';
                                    icon = 'mainmap';
                                } else {
                                    provider = 'googlev3';
                                    icon = 'altmap';
                                };
                                mao.swap(provider, provider);  
                                add_marker();
                            }

                            //]]>"""
                                 
# there is no need to add an ending "</script>" as it will be added automatically!

                middle += Html("div", id = "googlev3", inline = True)
                middle += Html("div", id = "openlayers", inline = True)

                middle += Html("a", _("change provider"), attr = 'onclick = "changeprovider();"',
                    href = "#", inline = True)

        # return placedetail division back to its callers
        return placedetail, head

    def complete_people(self, tcell, first_person, handle_list):
        """
        completes the person column for classes EventListPage and EventPage

        @param: tcell -- table cell from its caller
        @param: first_person -- variable from its callers
        @param: handle_list -- handle list from the backlink of the event_handle
        """
        for (classname, handle) in handle_list:

            # personal event
            if classname == "Person":

                _obj = self.report.database.get_person_from_handle(handle)
                if _obj:
                    _name = self.get_name(_obj)
                    tcell += _name

                    if not first_person:
                        tcell += ", "
                        first_person = False

            # family event
            else:
                _obj = self.report.database.get_family_from_handle(handle)
                if _obj:

                    # husband and spouse in this example, are called father and mother
                    husband_handle = _obj.get_father_handle() 
                    spouse_handle = _obj.get_mother_handle()
                    husband = self.report.database.get_person_from_handle(husband_handle)
                    spouse = self.report.database.get_person_from_handle(spouse_handle)
                    if husband:
                        husband_name = self.get_name(husband)
                    if spouse:
                        spouse_name = self.get_name(spouse)
                    if spouse and husband:
                        tcell += ( Html("span", husband_name, class_ = "father fatherNmother") +
                            Html("span", spouse_name, class_ = "mother")
                            )
                    elif spouse:
                        tcell += Html("span", spouse_name, class_ = "mother")
                    elif husband:
                        tcell += Html("span", husband_name, class_ = "father")

        # return tcell, and first_person back to its callers
        return tcell, first_person

    def dump_attribute(self, attr):
        """
        dump attribute for object presented in display_attr_list()

        @param: attr = attribute object
        """

        trow = Html("tr")

        # display attribute list
        trow.extend(
            Html("td", data or "&nbsp;", class_ = "Column" + colclass,
                inline = (colclass == "Type" or "Sources"))
            for (colclass, data) in [
                ["Type",    str(attr.get_type()) ],
                ["Value",   attr.get_value() ],
                ["Sources", self.get_citation_links(attr.get_source_references()) ],
                ["Notes",  self.dump_notes(attr.get_note_list()) ] ]
                )

        # return table row to its caller
        return trow

    def get_citation_links(self, source_ref_list):
        """
        get citation link from the source reference list

        @param: source_ref_list = list of source references
        """

        gid_list = []
        lnk = (self.report.cur_fname, self.page_title, self.gid)

        for sref in source_ref_list:
            handle = sref.get_reference_handle()
            gid_list.append(sref)

            if handle in self.src_list:
                if lnk not in self.src_list[handle]:
                    self.src_list[handle].append(lnk)
            else:
                self.src_list[handle] = [lnk]

        text = ""
        if len(gid_list):
            for ref in gid_list:
                index, key = self.bibli.add_reference(ref)
                id_ = "%d%s" % (index+1, key)
                text += ' [<a href="#sref%s ">%s</a>]' % (id_, id_)

        # return citation list text to its callers
        return text

    def get_note_format(self, note, link_prefix_up):
        """
        will get the note from the database, and will return either the 
        styled text or plain note 
        """
        self.report.link_prefix_up = link_prefix_up

        # retrieve the body of the note
        note_text = note.get()
 
        # styled notes
        htmlnotetext = self.styled_note(note.get_styledtext(),
                                        note.get_format(), contains_html = 
                                        note.get_type() == NoteType.HTML_CODE)
        text = htmlnotetext or Html("p", note_text)

        # return text of the note to its callers
        return text

#################################################
#
# Will produce styled notes for NarrativeWeb by using:
# src/plugins/lib/libhtmlbackend.py
#
#################################################

    def styled_note(self, styledtext, format, contains_html=False):
        """
        styledtext : assumed a StyledText object to write
        format : = 0 : Flowed, = 1 : Preformatted
        style_name : name of the style to use for default presentation
        """
        text = str(styledtext)

        if not text:
            return ''

        s_tags = styledtext.get_tags()
        #FIXME: following split should be regex to match \n\s*\n instead?
        markuptext = self._backend.add_markup_from_styled(text, s_tags,
                                                         split='\n\n')
        htmllist = Html("div", id = "grampsstylednote")
        if contains_html:
            htmllist.extend((Html('p') + text))
        elif format == 1:
            #preformatted, retain whitespace.
            #so use \n\n for paragraph detection
            htmllist += Html("pre", indent=None) + markuptext.split('\n\n')

        elif format == 0:
            #flowed, use \n\n for paragraph detection
            htmllist.extend(
                (Html('p') + para.split('\n'))
                    for para in markuptext.split("\n\n"))

        return htmllist

    def dump_notes(self, notelist):
        """
        dump out of list of notes with very little elements of its own

        @param: notelist -- list of notes
        """

        if not notelist:
            return Html("p")

        # begin unordered list
        ul = Html("p")
        for notehandle in notelist:
            ul.extend(
                Html("i", str(self.report.database.get_note_from_handle(notehandle).type))
                )
            ul.extend(
                self.get_note_format(self.report.database.get_note_from_handle(notehandle), 
                                     True)
                )

        # return note list to its callers
        return ul

    def display_event_row(self, evt, evt_ref, subdirs, hyp, omit):
        """
        display the event row for IndividualPage
0

        @param: evt = Event
        @param: evt_ref = event reference
        @param: subdirs = add [".."] * 3 for subdirectories or not
        @param: hyp = add a hyperlink or not
        @params: omit = role to be omitted in output
        """
        db = self.report.database

        # check to see if place is already in self.place_list?
        lnk = (self.report.cur_fname, self.page_title, self.gid)
        place_handle = evt.get_place_handle()
        if place_handle:
            if place_handle in self.place_list:
                if lnk not in self.place_list[place_handle]:
                    self.place_list[place_handle].append(lnk)
            else:
                self.place_list[place_handle] = [lnk]

        # begin event table row
        trow = Html("tr")

        # get event type and hyperlink to it or not?
        etype = str(evt.type)
        if not evt_ref.get_role() == omit:
            etype += " (%s)" % evt_ref.get_role()
        evt_hyper = self.event_link(etype, evt_ref.ref, evt.gramps_id, subdirs) if hyp else etype
        trow += Html("td", evt_hyper, class_ = "ColumnEvent")

        # get event data
        """
        for more information: see get_event_data()
        """
        event_data = self.get_event_data(evt, evt_ref, subdirs)

        trow.extend(
            Html("td", data or "&nbsp;", class_ = "Column" + colclass,
                inline = (not data or colclass == "Date"))
            for (label, colclass, data) in event_data)

        # get event notes
        notelist = evt.get_note_list()
        notelist.extend( evt_ref.get_note_list() )
        if notelist:
            htmllist = self.dump_notes( notelist )
        else:
            htmllist = Html("p")
  
        # if the event or event reference has a attributes attached to it,
        # get the text and format it correctly
        attrlist = evt.get_attribute_list()
        attrlist.extend(evt_ref.get_attribute_list())
        for attr in attrlist:
            htmllist.extend ( Html (
                "p",
                _("%(type)s: %(value)s") % {
                'type'     : Html("b", attr.get_type()),
                'value'    : attr.get_value() } ))
            #also output notes attached to the attributes
            notelist = attr.get_note_list()
            if notelist:
                htmllist.extend (self.dump_notes( notelist ))

        trow += Html("td", htmllist, class_ = "ColumnNotes")

        # get event source references
        srcrefs = self.get_citation_links( evt.get_source_references() ) or "&nbsp;"
        trow += Html("td", srcrefs, class_ = "ColumnSources")

        # return events table row to its callers
        return trow 

    def event_link(self, eventtype, handle, gid = None, up = False):
        """ creates a hyperlink for an event based on its type """

        url = self.report.build_url_fname_html(handle, "evt", up)

        # if event pages are being created, then hyperlink the event type
        if self.inc_events:
            evt_hyper = Html("a", eventtype, href = url, title = eventtype)
            if not self.noid and gid:
                evt_hyper += Html("span", " [%s]" % gid, class_ = "grampsid", 
                    inline = True)

            # return event hyper link to its callers
            return evt_hyper

        # return just the eventtype
        else:
            return eventtype

    def get_event_data(self, evt, evt_ref, up, gid = None):
        """
        retrieve event data from event and evt_ref

        @param: evt = event from database
        @param: evt_ref = eent reference
        @param: up = either True or False; add subdirs or not?
        """
        db = self.report.database

        # get place name
        place = None
        place_handle = evt.get_place_handle()
        if place_handle:
            place = db.get_place_from_handle(place_handle)

        place_hyper = None
        if place: 
            place_name = ReportUtils.place_name(db, place_handle)
            place_hyper = self.place_link(place_handle, place_name, up = up)

        # wrap it all up and return to its callers
        # position 0 = translatable label, position 1 = column class
        # position 2 = data
        info = [
               (DHEAD, "Date", _dd.display(evt.get_date_object() ) ),
               (PHEAD, "Place", place_hyper),
               (DESCRHEAD, "Description", evt.get_description() )
               ]
        return info

    def dump_ordinance(self, db, ldsobj, LDSSealedType = "Person"):
        """
        will dump the LDS Ordinance information for either
        a person or a family ...

        @param: db -- the database in use
        @param: ldsobj -- either person or family
        @param: LDSSealedType = either Sealed to Family or Spouse
        """
        objectldsord = ldsobj.lds_ord_list
        if not objectldsord:
            return None
        numberofords = len(objectldsord)

        # begin LDS ordinance table and table head
        with Html("table", class_ = "infolist ldsordlist") as table:
            thead = Html("thead")
            table += thead

            # begin HTML row
            trow = Html("tr")
            thead += trow

            header_row = [
                [THEAD,           "LDSType"],
                [DHEAD,           "LDSDate"],
                [TMPL,            "LDSTemple"],
                [PHEAD,           "LDSPlace"],
                [ST,              "LDSStatus"],
                [_("Sealed to "), "LDSSealed"],
                [SHEAD,           "LDSSources"]
               ]

            # finish the label's missing piece
            header_row[5][0] += PARENTS if LDSSealedType == "Person" else _("Spouse") 

            trow.extend(
                Html("th", label, class_ = "Column" + colclass, inline = True)
                for (label, colclass) in header_row)

            # start table body
            tbody = Html("tbody")
            table += tbody

            for row in range(1, (numberofords + 1)):

                # get ordinance for this row
                ord = objectldsord[(row - 1)]

                # 0 = column class, 1 = ordinance data
                lds_ord_data = [
                    ["LDSType",     ord.type2xml()],
                    ["LDSDate",     _dd.display(ord.get_date_object() )],
                    ["LDSTemple",   ord.get_temple()],
                    ["LDSPlace",    ReportUtils.place_name(db, ord.get_place_handle() )],
                    ["LDSStatus",   ord.get_status()],
                    ["LDSSealed",   ord.get_family_handle()],
                    ["LDSSources",  self.get_citation_links(ord.get_source_references() )],
                    ]

                # begin ordinance rows
                trow = Html("tr")
                tbody += trow

                trow.extend(
                    Html("td", value or "&nbsp;", class_ = "Column" + colclass,
                        inline = (not value or colclass == "LDSDate"))
                    for (colclass, value) in lds_ord_data)

        # return table to its callers
        return table

    def source_link(self, handle, name, gid = None, up = False):
        """
        creates a link to the source
        """

        url = self.report.build_url_fname_html(handle, "src", up)

        # begin hyperlink
        hyper = Html("a", html_escape(name), href = url, title = html_escape(name))

        # add GRAMPS ID
        if not self.noid and gid:
            hyper += Html("span", ' [%s]' % gid, class_ = "grampsid", inline = True)

        # return hyperlink to its callers
        return hyper

    def display_addr_list(self, addrlist, showsrc):
        """
        display a person's or repository's addresses ...

        @param: addrlist -- a list of address handles
        @param: showsrc -- whether to show sources or not?
        """

        if not addrlist:
            return None

        # begin addresses division and title
        with Html("div", class_ = "subsection", id = "Addresses") as section:
            section += Html("h4", _("Addresses"), inline = True)

            # write out addresses()
            section += self.dump_addresses(addrlist, showsrc)

        # return address division to its caller
        return section

    def dump_addresses(self, addrlist, showsrc):
        """
        will display an object's addresses, url list, note list, 
        and source references.

        @param: addrlist = either person or repository address list
        @param: showsrc = True  --  person
                          False -- repository
                          None  -- do not show sources
        """
        # begin summaryarea division
        with Html("div", id = "summaryarea") as summaryarea: 

            # begin address table
            with Html("table") as table:
                summaryarea += table

                # get table class based on showsrc
                if showsrc == True:
                    table.attr = 'class = "infolist addrlist"'
                elif showsrc == False: 
                    table.attr = 'class = "infolist repolist"'
                else:
                    table.attr = 'class = "infolist addressbook"' 

                # begin table head
                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                addr_header = [
                      [DHEAD,      "Date"],
                      [STREET,     "StreetAddress"],    
                      [CITY,       "City"],
                      [COUNTY,     "County"],
                      [STATE,      "State"],
                      [COUNTRY,    "Cntry"],
                      [POSTAL,     "Postalcode"],
                      [PHONE,      "Phone"] ]

                # if showsrc = True -- an individual's address else repository
                if showsrc:
                    addr_header.append([SHEAD,      "Sources"])

                trow.extend(
                    Html("th", label, class_="Colummn" + colclass, inline = True)
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
                        ["Date",               _dd.display(address.get_date_object() )],
                        ["Streetaddress",      address.get_street()],
                        ["City",               address.get_city()],
                        ["County",             address.get_county()],
                        ["State/ Province",    address.get_state()],
                        ["Cntry",              address.get_country()],
                        ["Postslcode",         address.get_postal_code()],
                        ["Phone",              address.get_phone()] ]

                    # get source citation list
                    if showsrc:
                        addr_data_row.append(["Sources",    self.get_citation_links(
                            address.get_source_references() )])

                    trow.extend(
                        Html("td", value or "&nbsp;", class_="Column" + colclass, inline=True)
                        for (colclass, value) in addr_data_row
                        )
                    
                    # address: notelist
                    if showsrc is not None:
                        notelist = self.display_note_list(address.get_note_list())
                        if notelist is not None:
                            summaryarea += notelist
                   
        # return summaryarea division to its callers
        return summaryarea

    def addressbook_link(self, person_handle, up = False):
        """
        creates a hyperlink for an address book link based on person's handle

        @param: person_handle = person's handle from the database
        #param: up = rather to add subdirs or not?
        """

        url = self.report.build_url_fname_html(person_handle, "addr", up)
        person = self.report.database.get_person_from_handle(person_handle)
        person_name = self.get_name(person)

        # return addressbook hyperlink to its caller
        return Html("a", person_name, href = url, title = html_escape(person_name))

    def get_copyright_license(self, copyright, up = False):
        """
        will return either the text or image of the copyright license
        """

        text = ''
        if copyright == 0:
            if self.author:
                year = date.Today().get_year()
                text = '&copy; %(year)d %(person)s' % {
                    'person' : self.author,
                    'year' : year}
        elif 0 < copyright < len(_CC):
            # Note. This is a URL
            fname = "/".join(["images", "somerights20.gif"])
            url = self.report.build_url_fname(fname, None, up = False)
            text = _CC[copyright] % {'gif_fname' : url}

        # return text or image to its callers
        return text

    def get_name(self, person, maiden_name = None):
        """ I5118

        Return person's name, unless maiden_name given, unless married_name 
        listed. 

        @param: person -- person object from database
        @param: maiden_name -- Female's family surname
        """

        # get name format for displaying names
        name_format = self.report.options['name_format']

        # Get all of a person's names
        primary_name = person.get_primary_name()
        married_name = None
        names = [primary_name] + person.get_alternate_names()
        for name in names:
            if int(name.get_type()) == gen.lib.NameType.MARRIED:
                married_name = name
                break # use first

        # Now, decide which to use:
        if maiden_name is not None:
            if married_name is not None:
                name = gen.lib.Name(married_name)
            else:
                name = gen.lib.Name(primary_name)
                name.set_surname(maiden_name)
        else:
            name = gen.lib.Name(primary_name)
        name.set_display_as(name_format)
        return _nd.display_name(name)

    def display_attr_list(self, attrlist):
        """
        will display a list of attributes

        @param: attrlist -- a list of attributes
        """
        if not attrlist:
            return None

        # begin attributes division and section title
        with Html("div", class_ = "ubsection", id = "attributes") as section:
            section += Html("h4", AHEAD,  inline = True)

            # begin attributes table
            with Html("table", class_ = "infolist attrlist") as table:
                section += table

                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                trow.extend(
                    Html("th", label, class_ = "Column" + colclass, inline = True)
                    for (label, colclass) in [
                        (THEAD,    "Type"),
                        (VHEAD,    "Value"),
                        (SHEAD,    "Sources"),
                        (NHEAD,    "Notes") ]
                        )
                                     
                # begin table body
                tbody = Html("tbody")
                table += tbody

                tbody.extend(
                    self.dump_attribute(attr)
                    for attr in attrlist) 

        # return section to its caller
        return section

    def write_footer(self):
        """
        Will create and display the footer section of each page...

        @param: bottom -- whether to specify location of footer section or not?
        """

        # begin footer division
        with Html("div", id = "footer") as footer:

            footer_note = self.report.options['footernote']
            if footer_note:
                note = self.get_note_format(
                    self.report.database.get_note_from_gramps_id(footer_note),
                    False
                    )
                user_footer = Html("div", id = 'user_footer')
                footer += user_footer
 
                # attach note
                user_footer += note

            msg = _('Generated by <a href = "%(homepage)s">'
                    'Gramps</a> %(version)s on %(date)s') % {
                'date': _dd.display(date.Today()), 
                'homepage' : const.URL_HOMEPAGE,
                'version': const.VERSION}

            # optional "link-home" feature; see bug report #2736
            if self.report.options['linkhome']:
                center_person = self.report.database.get_person_from_gramps_id(self.report.options['pid'])
                if center_person and center_person.handle in self.report.person_handles:
                    center_person_url = self.report.build_url_fname_html(
                        center_person.handle, "ppl", self.up)

                    person_name = self.get_name(center_person)
                    msg += _('<br>Created for <a href = "%s">%s</a>') % (
                                center_person_url, person_name)

            # creation author
            footer += Html("p", msg, id = 'createdate')

            # get copyright license for all pages
            copy_nr = self.report.copyright

            text = ''
            if copy_nr == 0:
                if self.author:
                    year = date.Today().get_year()
                    text = '&copy; %(year)d %(person)s' % {
                               'person' : self.author,
                               'year' : year}
            elif copy_nr < len(_CC):
                # Note. This is a URL
                fname = "/".join(["images", "somerights20.gif"])
                url = self.report.build_url_fname(fname, None, self.up)
                text = _CC[copy_nr] % {'gif_fname' : url}
            footer += Html("p", text, id = 'copyright')

        # return footer to its callers
        return footer

    def write_header(self, title):
        """
        Note. 'title' is used as currentsection in the navigation links and
        as part of the header title.
        """

        # Header constants
        xmllang = Utils.xml_lang()
        _META1 = 'name="generator" content="%s %s %s"' % (
                    const.PROGRAM_NAME, const.VERSION, const.URL_HOMEPAGE
                    )
        _META2 = 'name="author" content="%s"' % self.author

        page, head, body = Html.page('%s - %s' % 
                                    (html_escape(self.title_str), 
                                     html_escape(title)),
                                    self.report.encoding, xmllang )

        # temporary fix for .php parsing error
        if self.ext in [".php", ".php3", ".cgi"]:
            del page[0]

        # create additional meta tags
        meta = (Html("meta", attr = _META1) + 
                Html("meta", attr = _META2, indent = False)
               )

        # Link to media reference regions behaviour stylesheet
        fname = "/".join(["styles", "behaviour.css"])
        url1 = self.report.build_url_fname(fname, None, self.up)

        # Link to _NARRATIVESCREEN  stylesheet
        fname = "/".join(["styles", _NARRATIVESCREEN])
        url2 = self.report.build_url_fname(fname, None, self.up)

        # Link to _NARRATIVEPRINT stylesheet
        fname = "/".join(["styles", _NARRATIVEPRINT])
        url3 = self.report.build_url_fname(fname, None, self.up)

        # Link to GRAMPS favicon
        fname = "/".join(['images', 'favicon2.ico'])
        url4 = self.report.build_url_image("favicon2.ico", "images", self.up)

        # create stylesheet and favicon links
        links = Html("link", href = url4, type = "image/x-icon", rel = "shortcut icon") + (
             Html("link", href = url1, type = "text/css", media = "screen", rel = "stylesheet", indent = False),
             Html("link", href = url2, type = "text/css", media = "screen", rel = "stylesheet", indent = False),
             Html("link", href = url3, type = "text/css", media = 'print',  rel = "stylesheet", indent = False)
             )

        # Link to Navigation Menus stylesheet
        if self.report.css in ["Web_Basic-Blue.css", "Web_Visually.css"]:
            fname = "/".join(["styles", "Web_Navigation-Menus.css"])
            url = self.report.build_url_fname(fname, None, self.up)
            links.extend(
                Html("link", href = url, type = "text/css", media = "screen", rel = "stylesheet", indent = False)
                )
        # add additional meta and link tags
        head += meta
        head += links

        # begin header section
        headerdiv = (Html("div", id = 'header') +
            Html("h1", html_escape(self.title_str), id = "SiteTitle", inline = True)
            )
        body += headerdiv

        header_note = self.report.options['headernote']
        if header_note:
            note = self.get_note_format(
                self.report.database.get_note_from_gramps_id(header_note),
                False
                )
            user_header = Html("div", id = 'user_header')
            headerdiv += user_header  
 
            # attach note
            user_header += note

        # Begin Navigation Menu
        body += self.display_nav_links(title)

        # return to its caller, page and body
        return page, head, body

    def display_nav_links(self, currentsection):
        """
        Creates the navigation menu

        @param: currentsection = which menu item are you on
        """

        # include repositories or not?
        inc_repos = True   
        if not self.report.inc_repository or \
            len(self.report.database.get_repository_handles()) == 0:
                inc_repos = False  

        navs = [
            (self.report.index_fname,   _("Html|Home"),             self.report.use_home),
            (self.report.intro_fname,    _("Introduction"),         self.report.use_intro),
            ('individuals',             _("Individuals"),           True),
            (self.report.surname_fname, _("Surnames"),              True),
            ('places',                  _("Places"),                True),
            ('events',                  _("Events"),                self.report.inc_events), 
            ('media',                   _("Media"),                 self.create_media),
            ('download',                _("Download"),              self.report.inc_download),
            ('contact',                 _("Contact"),               self.report.use_contact),
            ('sources',                 SHEAD,                      True),
            ('repositories',            _("Repositories"),          inc_repos),
            ("addressbook",             _("Address Book"),          self.report.inc_addressbook)
                ]

        navigation = Html("div", id = 'navigation')
        ul = Html("ul")

        navs = ((u, n) for u, n, c in navs if c)
        for url_fname, nav_text in navs:

            if not _has_webpage_extension(url_fname):
                url_fname += self.ext

            url = self.report.build_url_fname(url_fname, None, self.up)

            # Define 'currentsection' to correctly set navlink item CSS id
            # 'CurrentSection' for Navigation styling.
            # Use 'self.report.cur_fname' to determine 'CurrentSection' for individual
            # elements for Navigation styling.

            # Figure out if we need <li class="CurrentSection"> of just plain <li>
            cs = False
            if nav_text == currentsection:
                cs = True
            elif nav_text == _("Surnames"):
                if "srn" in self.report.cur_fname:
                    cs = True
                elif _("Surnames") in currentsection:
                    cs = True
            elif nav_text == _("Individuals"):
                if "ppl" in self.report.cur_fname:
                    cs = True
            elif nav_text == SHEAD:
                if "src" in self.report.cur_fname:
                    cs = True
            elif nav_text == _("Places"):
                if "plc" in self.report.cur_fname:
                    cs = True
            elif nav_text == _("Events"):
                if "evt" in self.report.cur_fname:
                    cs = True 
            elif nav_text == _("Media"):
                if "img" in self.report.cur_fname:
                    cs = True
            elif nav_text == _("Address Book"):
                if "addr" in self.report.cur_fname:
                    cs = True 

            cs = 'class = "CurrentSection"' if cs else ""
            ul += (Html("li", attr = cs, inline = True) +
                   Html("a", nav_text, href = url, title = "Main Navigation Item " + nav_text)
                  )

        navigation += ul

        # return navigation menu bar to its caller
        return navigation

    def add_image(self, option_name, height = 0):
        """
        will add an image (if present) to the page
        """

        pic_id = self.report.options[option_name]
        if pic_id:
            obj = self.report.database.get_object_from_gramps_id(pic_id)
            if obj is None:
                return None
            obj_handle = obj.handle
            mime_type = obj.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                try:

                    newpath, thumb_path = self.report.prepare_copy_media(obj)
                    self.report.copy_file(Utils.media_path_full(
                        self.report.database, obj.get_path()), newpath)

                    # begin image
                    image = Html("img")
                    img_attr = ''
                    if height:
                        img_attr += 'height = "%d"'  % height
                    img_attr += ' src = "%s" alt = "%s" title = "%s"' % (newpath, obj.get_description(),
                        obj.get_description() )

                    # add image attributes to image
                    image.attr = img_attr

                    # return an image
                    return image   

                except (IOError, OSError), msg:
                    WarningDialog(_("Could not add photo to page"), str(msg))

        # no image to return
        return None

    def media_ref_rect_regions(self, handle):

        """
        *************************************
        GRAMPS feature #2634 -- attempt to highlight subregions in media
        objects and link back to the relevant web page.

        This next section of code builds up the "records" we'll need to
        generate the html/css code to support the subregions
        *************************************
        """
        db = self.report.database

        # get all of the backlinks to this media object; meaning all of
        # the people, events, places, etc..., that use this image
        _region_items = set()
        for (classname, newhandle) in db.find_backlink_handles(handle, 
            include_classes = ["Person", "Family", "Event", "Place"]):

            # for each of the backlinks, get the relevant object from the db
            # and determine a few important things, such as a text name we
            # can use, and the URL to a relevant web page
            _obj     = None
            _name    = ""
            _linkurl = "#"
            if classname == "Person":
                # Is this a person for whom we have built a page:
                if newhandle in self.report.person_handles:
                    # If so, let's add a link to them:
                    _obj = db.get_person_from_handle( newhandle )
                    if _obj:
                        # what is the shortest possible name we could use for this person?
                        _name = _obj.get_primary_name().get_call_name()
                        if not _name:
                            _name = _obj.get_primary_name().get_first_name()
                        _linkurl = self.report.build_url_fname_html(_obj.handle, "ppl", True)
            elif classname == "Family":
                _obj = db.get_family_from_handle( newhandle )
                partner1_handle = _obj.get_father_handle()
                partner2_handle = _obj.get_mother_handle()
                partner1 = None
                partner2 = None
                if partner1_handle:
                     partner1 = db.get_person_from_handle(partner1_handle)
                if partner2_handle:
                    partner2 = db.get_person_from_handle(partner2_handle)
                if partner2 and partner1:
                    _name = partner1.get_primary_name().get_first_name()
                    _linkurl = self.report.build_url_fname_html(partner1_handle, "ppl", True)  
                elif partner1:
                    _name = partner1.get_primary_name().get_first_name()
                    _linkurl = self.report.build_url_fname_html(partner1_handle, "ppl", True)  
                elif partner2:
                    _name = partner2.get_primary_name().get_first_name()
                    _linkurl = self.report.build_url_fname_html(partner2_handle, "ppl", True)  
            elif classname == "Event":
                _obj = db.get_event_from_handle( newhandle )
                _name = _obj.get_description()
                _linkurl = self.report.build_url_fname_html(_obj.handle, "evt", True) 
            elif classname == "Place":
                _obj = db.get_place_from_handle(newhandle)
                _name = ReportUtils.place_name(db, newhandle)
                _linkurl = self.report.build_url_fname_html(newhandle, "plc", True)   

            # continue looking through the loop for an object...
            if _obj is None:
                continue

            # get a list of all media refs for this object
            medialist = _obj.get_media_list()

            # go media refs looking for one that points to this image
            for mediaref in medialist:

                # is this mediaref for this image?  do we have a rect?
                if mediaref.ref == handle and mediaref.rect is not None:

                    (x1, y1, x2, y2) = mediaref.rect
                    # GRAMPS gives us absolute coordinates,
                    # but we need relative width + height
                    w = x2 - x1
                    h = y2 - y1

                    # remember all this information, cause we'll need
                    # need it later when we output the <li>...</li> tags
                    item = (_name, x1, y1, w, h, _linkurl)
                    _region_items.add(item)
        """
        *************************************
        end of code that looks for and prepares the media object regions
        *************************************
        """

        # return media rectangles to its callers
        return _region_items

    def media_ref_region_to_object(self, media_handle, obj):
        """
        Return a region of this image if it refers to this object.
        """
        # get a list of all media refs for this object
        for mediaref in obj.get_media_list():
            # is this mediaref for this image?  do we have a rect?
            if (mediaref.ref == media_handle and 
                mediaref.rect is not None):
                return mediaref.rect # (x1, y1, x2, y2)
        return None

    def display_first_image_as_thumbnail(self, photolist, object):
        """
        Return the Html of the first image of photolist that is
        associated with object. First image might be a region in an
        image. Or, the first image might have regions defined in it.
        """

        if not photolist or not self.create_media:
            return None

        photo_handle = photolist[0].get_reference_handle()
        photo = self.report.database.get_object_from_handle(photo_handle)
        mime_type = photo.get_mime_type()

        # begin snapshot division
        with Html("div", class_ = "snapshot") as snapshot:

            if mime_type:

                # add link reference to media
                lnkref = (self.report.cur_fname, self.page_title, self.gid)
                self.report.add_lnkref_to_photo(photo, lnkref)

                region = self.media_ref_region_to_object(photo_handle, object)
                if region:

                    # make a thumbnail of this region
                    newpath = copy_thumbnail(self.report, photo_handle, photo, region)
                    newpath = self.report.build_url_fname(newpath, up = True)

                    snapshot += self.media_link(photo_handle, newpath, '', up = True)
                else:

                    real_path, newpath = self.report.prepare_copy_media(photo)
                    newpath = self.report.build_url_fname(newpath, up = True)
  
                    _region_items = self.media_ref_rect_regions(photo_handle)
                    if len(_region_items):
                        with Html("div", id = "GalleryDisplay") as mediadisplay:
                            snapshot += mediadisplay

                            ordered = Html("ol", class_ = "RegionBox")
                            mediadisplay += ordered
                            while len(_region_items):
                                (name, x, y, w, h, linkurl) = _region_items.pop()
                                ordered += Html("li", 
                                                style="left:%d%%; top:%d%%; width:%d%%; height:%d%%;"
                                                % (x, y, w, h)) + Html("a", name, href = linkurl)
                            # Need to add link to mediadisplay to get the links:
                            mediadisplay += self.media_link(photo_handle, newpath, '', up = True)
                    else:
                        try:

                            # begin hyperlink
                            # description is given only for the purpose of the alt tag in img element
                            snapshot += self.media_link(photo_handle, newpath, '', up = True)

                        except (IOError, OSError), msg:
                            WarningDialog(_("Could not add photo to page"), str(msg))
            else:
                # get media description
                descr = photo.get_description()

                # begin hyperlink
                snapshot += self.doc_link(photo_handle, descr, up = True)

                lnk = (self.report.cur_fname, self.page_title, self.gid)
                # FIXME. Is it OK to add to the photo_list of report?
                photo_list = self.report.photo_list
                if photo_handle in photo_list:
                    if lnk not in photo_list[photo_handle]:
                        photo_list[photo_handle].append(lnk)
                else:
                    photo_list[photo_handle] = [lnk]

        # return snapshot division to its callers
        return snapshot

    def display_additional_images_as_gallery(self, photolist, object):

        if not photolist or not self.create_media:
            return None

        # make referenced images have the same order as in media list:
        photolist_handles = {}
        for mediaref in photolist:
            photolist_handles[mediaref.get_reference_handle()] = mediaref
        photolist_ordered = []
        for photoref in object.get_media_list():
            if photoref.ref in photolist_handles:
                photo = photolist_handles[photoref.ref]
                photolist_ordered.append(photo)
                photolist.remove(photo)
        # and add any that are left (should there be any?)
        photolist_ordered += photolist

        # begin individualgallery division and section title
        with Html("div", class_ = "subsection", id = "indivgallery") as section: 
            section += Html("h4", _("Gallery"), inline = True)

            displayed = []
            for mediaref in photolist_ordered:

                photo_handle = mediaref.get_reference_handle()
                photo = self.report.database.get_object_from_handle(photo_handle)

                if photo_handle in displayed:
                    continue
                mime_type = photo.get_mime_type()

                # get media description
                descr = photo.get_description()

                if mime_type:
                    try:

                        lnkref = (self.report.cur_fname, self.page_title, self.gid)
                        self.report.add_lnkref_to_photo(photo, lnkref)
                        real_path, newpath = self.report.prepare_copy_media(photo)
                        # TODO. Check if build_url_fname can be used.
                        newpath = "/".join(['..']*3 + [newpath])
                        if constfunc.win():
                            newpath = newpath.replace('\\',"/")
 
                        # begin hyperlink
                        section += self.media_link(photo_handle, newpath, descr, True, False)

                    except (IOError, OSError), msg:
                        WarningDialog(_("Could not add photo to page"), str(msg))
                else:
                    try:

                        # begin hyperlink
                        section += self.doc_link(photo_handle, descr, up = True)

                        lnk = (self.report.cur_fname, self.page_title, self.gid)
                        # FIXME. Is it OK to add to the photo_list of report?
                        photo_list = self.report.photo_list
                        if photo_handle in photo_list:
                            if lnk not in photo_list[photo_handle]:
                                photo_list[photo_handle].append(lnk)
                        else:
                            photo_list[photo_handle] = [lnk]
                    except (IOError, OSError), msg:
                        WarningDialog(_("Could not add photo to page"), str(msg))
                displayed.append(photo_handle)

        # add clearline for proper styling
        section += fullclear

        # return indivgallery division to its caller
        return section

    def display_note_list(self, notelist = None):

        if not notelist:
            return None

        # begin narrative division
        with Html("div", class_ = "subsection", id = "narrative") as section:

            for notehandle in notelist:
                note = self.report.database.get_note_from_handle(notehandle)

                if note:
                    note_text = self.get_note_format(note, True)

                    # add section title
                    section += Html("h4", _("Narrative"), inline=True)

                    # attach note
                    section += note_text

        # return notes to its callers
        return section

    def display_url_list(self, urllist = None):

        if not urllist:
            return None

        # begin web links division
        with Html("div", class_ = "subsection", id = "WebLinks") as section:

            # begin web title
            section += Html("h4", _("Web Links"), inline = True)  

            # begin weblinks table
            with Html("table", class_ = "infolist weblinks") as table: 
                section += table

                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                trow.extend(
                    Html('th', label, class_ = "Column" + colclass, inline = True)
                    for (label, colclass) in [
                        (THEAD,          "Type"),
                        (_("Web Path"), "Path"),
                        (DESCRHEAD,     "Description") ]
                    )

                tbody = Html("tbody")
                table += tbody

                for url in urllist:

                    trow = Html("tr")
                    tbody += trow
 
                    _type = url.get_type()
                    uri = url.get_path()
                    descr = url.get_description()

                    # Email address
                    if _type == UrlType.EMAIL:
                        if not uri.startswith("mailto:"):
                            uri = "mailto: %(email)s" % { 'email' : uri }

                    # Web Site address
                    elif _type == UrlType.WEB_HOME:
                        if not (uri.startswith("http://") or 
                                uri.startswith("https://")):
                            uri = "http://%(website)s" % { "website" : uri } 

                    # FTP server address
                    elif _type == UrlType.WEB_FTP:
                        if not uri.startswith("ftp://"):
                            uri = "ftp://%(ftpsite)s" % { "ftpsite" : uri }   

                    uri = Html("a", uri, href = uri, title = html_escape(uri))
                    trow.extend(
                        Html("td", data, class_ = "Column" + colclass, inline = True)
                        for (data, colclass) in [
                            (str(_type), "Type"),
                            (uri,        "Path"),
                            (descr,      "Description") ]
                        ) 
                
        # return weblinks to its caller
        return section

    def display_ind_sources(self, srcobj):
        """
        will create the "Source References" section for an object
        """

        map(self.bibli.add_reference, srcobj.get_source_references())
        sourcerefs = self.display_source_refs(self.bibli)

        # return to its callers
        return sourcerefs

    # Only used in IndividualPage.display_ind_sources(), and MediaPage.display_media_sources()
    def display_source_refs(self, bibli):
        if bibli.get_citation_count() == 0:
            return None

        # local gettext variables
        _PAGE = _("Page")
        _CONFIDENCE = _("Confidence")

        db = self.report.database
        with Html("div", id = "sourcerefs", class_ = "subsection") as section:
            section += Html("h4", _("Source References"), inline = True)

            ordered = Html("ol")

            cindex = 0
            citationlist = bibli.get_citation_list()
            for citation in citationlist:
                cindex += 1

                # Add this source to the global list of sources to be displayed
                # on each source page.
                lnk = (self.report.cur_fname, self.page_title, self.gid)
                shandle = citation.get_source_handle()
                if shandle in self.src_list:
                    if lnk not in self.src_list[shandle]:
                        self.src_list[shandle].append(lnk)
                else:
                    self.src_list[shandle] = [lnk]

                # Add this source and its references to the page
                source = db.get_source_from_handle(shandle)
                title = source.get_title()
                list = Html("li") + (
                    Html("a",
                        self.source_link(source.handle, title, source.gramps_id,
                            up=True), 
                        name="sref%d" % cindex,
                        inline=True)
                    )

                ordered1 = Html("ol")
                citation_ref_list = citation.get_ref_list()
                for key, sref in citation_ref_list:

                    tmp = []
                    confidence = Utils.confidence.get(sref.confidence, _('Unknown'))
                    if confidence == _('Normal'):
                        confidence = None

                    tmp.extend("%s: %s" % (label, data)
                        for (label, data) in [
                            [DHEAD, _dd.display(sref.date)],
                            [_PAGE, sref.page],
                            [_CONFIDENCE, confidence] ]
                        if data)                                                    
                        
                    tmp.extend("%s: %s" %
                                (db.get_note_from_handle(handle).type,
                                self.get_note_format(
                                    db.get_note_from_handle(handle),
                                    True
                                )) for handle in sref.get_note_list())

                    if tmp:
                        list1 = Html("li", inline = True) + (
                            Html("a", "<br/> ".join(tmp),
                                 style="text-decoration: none;",
                                 name="sref%d%s" % (cindex, key))
                            )

                        ordered1 += list1
                if citation_ref_list:
                    list += ordered1
                ordered += list
            section += ordered

        # return section to its caller
        return section

    def display_references(self, handlelist, up = False):

        if not handlelist:
            return None

        # begin references division and title
        with Html("div", class_ = "subsection", id = "references") as section:
            section += Html("h4", _("References"), inline = True)

            ordered = Html("ol")
            section += ordered 
            sortlist = sorted(handlelist, key=lambda x:locale.strxfrm(x[1]))
        
            for (path, name, gid) in sortlist:
                list = Html("li")
                ordered += list

                # Note. 'path' already has a filename extension
                url = self.report.build_url_fname(path, None, self.up)
                list += self.person_link(url, name or _("Unknown"), None, gid = gid)

        # return references division to its caller
        return section

    def person_link(self, url, person, name_style, first = True, gid = None, thumbnailUrl = None):
        """
        creates a hyperlink for a person

        @param: person = person in database
        @param: namestyle = False -- first and suffix only
                          = True  -- name displayed in name_format variable
                          = None -- person is name
        @param: first = show person's name and gramps id if requested and available
        """

        # the only place that this will ever equal False
        # is first there is more than one event for a person
        if first:

            # see above for explanation
            if name_style:
                person_name = self.get_name(person) 
            elif name_style == False:
                person_name = _get_short_name(person.gender, person.primary_name)
            elif name_style is None:    # abnormal specialty situation
                person_name = person

            # 1. start building link to image or person
            hyper = Html("a", href = url)

            # 2. insert thumbnail if there is one, otherwise insert class = "noThumb"
            if thumbnailUrl:
                hyper += (Html("span", class_ = "thumbnail") +
                          Html("img", src = thumbnailUrl, alt = "Image of " + person_name,
                              title = "Image of " + person_name)
                        )
            else:
                hyper.attr += ' class= "noThumb"'

            # 3. insert the person's name
            hyper += person_name

            # 3. insert gramps id if requested and available
            if not self.noid and gid:
                hyper += Html("span", " [%s]" % gid, class_ = "grampsid", inline = True)

        else:
            hyper = "&nbsp;"

        # return hyperlink to its caller
        return hyper

    # TODO. Check img_url of callers
    def media_link(self, handle, img_url, name, up, usedescr = True):
        url = self.report.build_url_fname_html(handle, "img", up)

        # begin thumbnail division
        with Html("div", class_ = "thumbnail") as thumbnail:

            # begin hyperlink
            hyper = (Html("a", href = url, title = name) +
                     Html("img", src = img_url, alt = name) )
            thumbnail += hyper

            if usedescr:
                hyper += Html("p", html_escape(name), inline = True)

        # return thumbnail division to its callers
        return thumbnail

    def doc_link(self, handle, name, up, usedescr = True):
        # TODO. Check extension of handle
        url = self.report.build_url_fname(handle, "img", up)

        # begin thumbnail division
        thumbnail = Html("div", class_ = "thumbnail")

        # begin hyperlink
        hyper = Html("a", href = url, title = name)
        thumbnail += hyper

        url = self.report.build_url_image("document.png", "images", up)
        hyper += Html("img", src = url, alt = html_escape(name), title = html_escape(name))

        if usedescr:
            hyper += Html("p", html_escape(name), inline = True)

        # return thumbnail division to its callers
        return thumbnail

    def repository_link(self, handle, name, cindex, gid = None, up = False):

        url = self.report.build_url_fname_html(handle, 'repo', up)
        # begin hyperlink
        hyper = Html("a", html_escape(name), href = url, title = name)
        if not self.noid and gid:
            hyper += Html("span", '[%s]' % gid, class_ = "grampsid", inline = True)

        # return hyperlink to its callers
        return hyper

    def place_link(self, handle, name, gid = None, up = False):
        url = self.report.build_url_fname_html(handle, "plc", up)

        hyper = Html("a", html_escape(name), href = url, title = name)
        if not self.noid and gid:
            hyper += Html("span", " [%s]" % gid, class_ = "grampsid", inline = True)

        # return hyperlink to its callers
        return hyper

    def dump_place(self, place, table):
        """
        dump a place's information from within the database

        @param: place -- place object from the database
        @param: table -- table from Placedetail
        @param: gid -- place gramps id
        """

        if not place:
            return
 
        # add table body
        tbody = Html("tbody")
        table += tbody

        gid = place.gramps_id
        if not self.noid and gid:
            trow = Html("tr") + (
                Html("td", GRAMPSID, class_ = "ColumnAttribute", inline = True),
                Html("td", gid, class_ = "ColumnValue", inline = True)
                )
            tbody += trow

        if place.main_loc:
            ml = place.get_main_location()
            if ml and not ml.is_empty():
                for (label, data) in [
                    (STREET,    ml.street),
                    (CITY,      ml.city),
                    (PARISH,    ml.parish),
                    (COUNTY,    ml.county),
                    (STATE,     ml.state),
                    (POSTAL,    ml.postal),
                    (COUNTRY,   ml.country),
                    (LOCATIONS, place.get_alternate_locations() ),
                    (LATITUDE,  place.lat),
                    (LONGITUDE, place.long) ]:

                    if data:
                        trow = Html("tr") + (
                            Html("td", label, class_ = "ColumnAttribute", inline = True),
                            Html("td", data, class_ = "ColumnValue", inline = True)
                        )
                        tbody += trow 

        # return place table to its callers
        return table

    def dump_residence(self, has_res):
        """ creates a residence from the daTABASE """

        if not has_res:
            return None

        # begin residence division
        with Html("div", id = "Residence", class_ = "content") as residence:
            residence += Html("h4", _("Residence"), inline = True)

            with Html("table", class_ = "infolist place") as table:
                residence += table

                place_handle = has_res.get_place_handle()
                if place_handle:
                    place = self.report.database.get_place_from_handle(place_handle)
                    if place:
                        self.dump_place(place, table)

            descr = has_res.get_description()
            if descr:

                trow = Html("tr")
                table += trow

                trow.extend(
                    ( Html("td", DESCRHEAD, class_ = "ColumnAttribute", inline = True) +
                    Html("td", descr, class_ = "ColumnValue") )
                )

        # return information to its callers
        return residence

# ---------------------------------------------------------------------------------------
#              # Web Page Fortmatter and writer                   
# ---------------------------------------------------------------------------------------
    def XHTMLWriter(self, htmlinstance, of):
        """
        Will format, write, and close the file

        of -- open file that is being written to
        htmlinstance -- web page created with libhtml
            src/plugins/lib/libhtml.py
        """

        htmlinstance.write(partial(print, file=of)) 

        # closes the file
        self.report.close_file(of)

class IndividualListPage(BasePage):

    def __init__(self, report, title, person_handle_list):
        BasePage.__init__(self, report, title)
        db = report.database

        # handles for this module for use in partner column
        report_handle_list = person_handle_list

        # plugin variables for this module
        showbirth = report.options['showbirth']
        showdeath = report.options['showdeath']
        showpartner = report.options['showpartner']
        showparents = report.options['showparents']

        of = self.report.create_file("individuals")
        indlistpage, head, body = self.write_header(_("Individuals"))

        # begin Individuals division
        with Html("div", class_ = "content", id = "Individuals") as individuallist:
            body += individuallist

            # Individual List page message
            msg = _("This page contains an index of all the individuals in the "
                          "database, sorted by their last names. Selecting the person&#8217;s "
                          "name will take you to that person&#8217;s individual page.")
            individuallist += Html("p", msg, id = "description")

            # add alphabet navigation
            menu_set = get_first_letters(db, person_handle_list, _KEYPERSON) 
            alpha_nav, menu_set = alphabet_navigation(menu_set)
            if alpha_nav is not None:
                individuallist += alpha_nav

            # begin table and table head
            with Html("table", class_ = "infolist IndividualList") as table:
                individuallist += table
                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow    

                # show surname and first name
                trow += ( Html("th", _("Surname"), class_ = "ColumnSurname", inline = True) +
                    Html("th", _("Name"), class_ = "ColumnName", inline = True)
                    )

                if showbirth:
                    trow += Html("th", BIRTH, class_ = "ColumnBirth", inline = True)

                if showdeath:
                    trow += Html("th", DEATH, class_ = "ColumnDeath", inline = True)

                if showpartner:
                    trow += Html("th", _PARTNER, class_ = "ColumnPartner", inline = True)

                if showparents:
                    trow += Html("th", PARENTS, class_ = "ColumnParents", inline = True)

            tbody = Html("tbody")
            table += tbody

            person_handle_list = sort_people(db, person_handle_list)
            for (surname, handle_list) in person_handle_list:
                first = True
                letter = first_letter(surname)
                for person_handle in handle_list:
                    person = db.get_person_from_handle(person_handle)

                    # surname column
                    trow = Html("tr")
                    tbody += trow
                    tcell = Html("td", class_ = "ColumnSurname", inline = True)
                    trow += tcell
                    if first:
                        trow.attr = 'class = "BeginSurname"'
                        if surname:
                            tcell += Html("a", surname, name = letter, 
                                title = "Surname with letter " + letter)
                        else:
                            tcell += "&nbsp;"
                    else:
                        tcell += "&nbsp;"
                    first = False

                    # firstname column
                    url = self.report.build_url_fname_html(person.handle, "ppl")
                    trow += Html("td", self.person_link(url, person, False, gid = person.gramps_id), 
                        class_ = "ColumnName")

                    # birth column
                    if showbirth:
                        tcell = Html("td", class_ = "ColumnBirth", inline = True)
                        trow += tcell

                        birth_date = _find_birth_date(db, person)
                        if birth_date is not None:
                            tcell += _dd.display(birth_date)
                        else:
                            tcell += "&nbsp;"

                    # death column
                    if showdeath:
                        tcell = Html("td", class_ = "ColumnDeath", inline = True)
                        trow += tcell

                        death_date = _find_death_date(db, person)
                        if death_date is not None:
                            tcell += _dd.display(death_date)
                        else:
                            tcell += "&nbsp;"

                    # partner column
                    if showpartner:
                        tcell = Html("td", class_ = "ColumnPartner")
                        trow += tcell

                        family_list = person.get_family_handle_list()
                        first_family = True
                        partner_name = None
                        if family_list:
                            for family_handle in family_list:
                                family = db.get_family_from_handle(family_handle)
                                partner_handle = ReportUtils.find_spouse(person, family)
                                if partner_handle:
                                    partner = db.get_person_from_handle(partner_handle)
                                    partner_name = self.get_name(partner)
                                    if not first_family:
                                        tcell += ", "  
                                    if partner_handle in report_handle_list:
                                        url = self.report.build_url_fname_html(partner_handle, "ppl")
                                        tcell += self.person_link(url, partner, True, gid = partner.gramps_id)
                                    else:
                                        tcell += partner_name
                                    first_family = False
                        else:
                            tcell += "&nbsp;"

                    # parents column
                    if showparents:

                        parent_handle_list = person.get_parent_family_handle_list()
                        if parent_handle_list:
                            parent_handle = parent_handle_list[0]
                            family = db.get_family_from_handle(parent_handle)
                            father_handle = family.get_father_handle()
                            mother_handle = family.get_mother_handle()
                            father = db.get_person_from_handle(father_handle)
                            mother = db.get_person_from_handle(mother_handle)
                            if father:
                                father_name = self.get_name(father)
                            if mother:
                                mother_name = self.get_name(mother)
                            if mother and father:
                                tcell = ( Html("span", father_name, class_ = "father fatherNmother") +
                                    Html("span", mother_name, class_ = "mother")
                                    )
                            elif mother:
                                tcell = Html("span", mother_name, class_ = "mother")
                            elif father:
                                tcell = Html("span", father_name, class_ = "father")
                            samerow = False 
                        else:
                            tcell = "&nbsp;"
                            samerow = True
                        trow += Html("td", tcell, class_ = "ColumnParents", inline = samerow)

        # create clear line for proper styling
        # create footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.XHTMLWriter(indlistpage, of)

class SurnamePage(BasePage):
    """
    This will create a list of individuals with the same surname
    """

    def __init__(self, report, title, surname, person_handle_list, report_handle_list):
        BasePage.__init__(self, report, title)
        db = report.database

        # module variables
        showbirth = report.options['showbirth']
        showdeath = report.options['showdeath']
        showpartner = report.options['showpartner']
        showparents = report.options['showparents']

        of = self.report.create_file(name_to_md5(surname), "srn")
        self.up = True
        surnamepage, head, body = self.write_header("%s - %s" % (_("Surname"), surname))

        # begin SurnameDetail division
        with Html("div", class_ = "content", id = "SurnameDetail") as surnamedetail:
            body += surnamedetail

            # section title
            surnamedetail += Html("h3", html_escape(surname), inline = True)

            msg = _("This page contains an index of all the individuals in the "
                    "database with the surname of %s. Selecting the person&#8217;s name "
                    "will take you to that person&#8217;s individual page.") % surname
            surnamedetail += Html("p", msg, id = "description")

            # begin surname table and thead
            with Html("table", class_ = "infolist surname") as table:
                surnamedetail += table
                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                # Name Column
                trow += Html("th", _("Name"), class_ = "ColumnName", inline = True) 

                if showbirth:
                    trow += Html("th", BIRTH, class_ = "ColumnBirth", inline = True)

                if showdeath:
                    trow += Html("th", DEATH, class_ = "ColumnDeath", inline = True)

                if showpartner:
                    trow += Html("th", _PARTNER, class_ = "ColumnPartner", inline = True)

                if showparents:
                    trow += Html("th", PARENTS, class_ = "ColumnParents", inline = True)

                # begin table body 
                tbody = Html("tbody")
                table += tbody

                for person_handle in person_handle_list:
 
                    person = db.get_person_from_handle(person_handle)
                    trow = Html("tr")
                    tbody += trow

                    # firstname column
                    url = self.report.build_url_fname_html(person.handle, "ppl", True)
                    trow += Html("td", self.person_link(url, person, False, gid = person.gramps_id),
                        class_ = "ColumnName")  

                    # birth column
                    if showbirth:
                        tcell = Html("td", class_ = "ColumnBirth", inline = True)
                        trow += tcell

                        birth_date = _find_birth_date(db, person)
                        if birth_date is not None:
                            tcell += _dd.display(birth_date)
                        else:
                            tcell += "&nbsp;"

                    # death column
                    if showdeath:
                        tcell = Html("td", class_ = "ColumnDeath", inline = True)
                        trow += tcell

                        death_date = _find_death_date(db, person)
                        if death_date is not None:
                            tcell += _dd.display(death_date)
                        else:
                            tcell += "&nbsp;"

                    # partner column
                    if showpartner:
                        tcell = Html("td", class_ = "ColumnPartner")
                        trow += tcell
                        family_list = person.get_family_handle_list()
                        first_family = True
                        if family_list:
                            for family_handle in family_list:
                                family = db.get_family_from_handle(family_handle)
                                partner_handle = ReportUtils.find_spouse(person, family)
                                if partner_handle:
                                    partner = db.get_person_from_handle(partner_handle)
                                    partner_name = self.get_name(partner)
                                    if not first_family:
                                        tcell += ','
                                    if partner_handle in report_handle_list:
                                        url = self.report.build_url_fname_html(partner_handle, "ppl", True) 
                                        tcell += self.person_link(url, partner, True, gid = partner.gramps_id)
                                    else:
                                        tcell += partner_name
                        else:
                            tcell += "&nbsp;"


                    # parents column
                    if showparents:
                        parent_handle_list = person.get_parent_family_handle_list()
                        if parent_handle_list:
                            parent_handle = parent_handle_list[0]
                            family = db.get_family_from_handle(parent_handle)
                            father_id = family.get_father_handle()
                            mother_id = family.get_mother_handle()
                            father = db.get_person_from_handle(father_id)
                            mother = db.get_person_from_handle(mother_id)
                            if father:
                                father_name = self.get_name(father)
                            if mother:
                                mother_name = self.get_name(mother)
                            if mother and father:
                                tcell = ( Html("span", father_name, class_ = "father fatherNmother") +
                                    Html("span", mother_name, class_ = "mother")
                                    )
                            elif mother:
                                tcell = Html("span", mother_name, class_ = "mother", inline = True)
                            elif father:
                                tcell = Html("span", father_name, class_ = "father", inline = True)
                            samerow = False
                        else:
                            tcell = "&nbsp;"
                            samerow = True
                        trow += Html("td", tcell, class_ = "ColumnParents", inline = samerow)

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.XHTMLWriter(surnamepage, of)  

class PlaceListPage(BasePage):

    def __init__(self, report, title, place_handles, src_list):
        BasePage.__init__(self, report, title)
        self.src_list = src_list        # TODO verify that this is correct
        db = report.database

        of = self.report.create_file("places")
        placelistpage, head, body = self.write_header(_("Places"))

        # begin places division
        with Html("div", class_ = "content", id = "Places") as placelist:
            body += placelist

            # place list page message
            msg = _("This page contains an index of all the places in the "
                          "database, sorted by their title. Clicking on a place&#8217;s "
                          "title will take you to that place&#8217;s page.")
            placelist += Html("p", msg, id = "description")

            # begin alphabet navigation
            menu_set = get_first_letters(db, place_handles, _KEYPLACE) 
            alpha_nav, menu_set = alphabet_navigation(menu_set)
            if alpha_nav is not None:
                placelist += alpha_nav

            # begin places table and table head
            with Html("table", class_ = "infolist placelist") as table:
                placelist += table

                # begin table head
                thead = Html("thead")
                table += thead

                trow =  Html("tr")
                thead += trow

                trow.extend(
                    Html("th", label, class_ = "Column" + colclass, inline = True)
                    for (label, colclass) in [
                        ["&nbsp;",               "Letter"],
                        [_("Place Name | Name"), "Name"],
                        [_("State"),             "State"],
                        [_("Country"),           "Country"],
                        [_("Lat."),              "Latitude"],
                        [_("Long."),             "Longitude"] ]
                    )

                sort = Sort.Sort(db)
                handle_list = sorted(place_handles, key = sort.by_place_title_key)
                last_letter = ''

                # begin table body
                tbody = Html("tbody")
                table += tbody

                for handle in handle_list:
                    place = db.get_place_from_handle(handle)
                    place_title = ReportUtils.place_name(db, handle)
                    ml = place.get_main_location()

                    letter = first_letter(place_title)

                    trow = Html("tr")
                    tbody += trow

                    tcell = Html("td", class_ = "ColumnLetter", inline = True)
                    trow += tcell
                    if letter != last_letter:
                        last_letter = letter
                        trow.attr = 'class = "BeginLetter"'

                        tcell += Html("a", last_letter, name = last_letter, 
                                title = _("Places with letter %s" % last_letter))
                    else:
                        tcell += "&nbsp;"

                    trow += Html("td", self.place_link(place.handle, place_title, place.gramps_id), 
                        class_ = "ColumnName")

                    trow.extend(
                        Html("td", data or "&nbsp;", class_ = "Column" + colclass, inline = True)
                        for (colclass, data) in [
                            ["State",     ml.state],
                            ["Country",   ml.country],
                            ["Latitude",  place.lat],
                            ["Longitude", place.long] ]
                        )

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.XHTMLWriter(placelistpage, of)

class PlacePage(BasePage):
    def __init__(self, report, title, place_handle, src_list, place_list):
        """
        creates the individual place pages
        """
        self.bibli = Bibliography()
        db = report.database
        place = db.get_place_from_handle(place_handle)

        # if place exists, but has nothing, return
        if not place:
            return None
        BasePage.__init__(self, report, title, place.gramps_id)

        of = self.report.create_file(place.get_handle(), "plc")
        self.up = True
        self.page_title = ReportUtils.place_name(db, place_handle)
        placepage, head, body = self.write_header(_("Places"))

        # begin PlaceDetail Division
        with Html("div", class_ = "content", id = "PlaceDetail") as placedetail:
            body += placedetail

            media_list = place.get_media_list()
            thumbnail = self.display_first_image_as_thumbnail(media_list, place)
            if thumbnail is not None:
                placedetail += thumbnail

            # add section title
            placedetail += Html("h5", html_escape(self.page_title), inline = True)

            # begin summaryarea division and places table
            with Html("div", id = 'summaryarea') as summaryarea:
                placedetail += summaryarea

                with Html("table", class_ = "infolist place") as table:
                    summaryarea += table

                    # list the place fields
                    self.dump_place(place, table)

            # place gallery
            if self.create_media:
                placegallery = self.display_additional_images_as_gallery(media_list, place)
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
            if self.placemaps:
                if place.lat and place.long:

                    self._create_place_map(placedetail, head, place.lat, place.long, self.page_title)

                    # add javascript function call to body element
                    body.attr = 'onload = "initialize();"'

            # source references
            srcrefs = self.display_ind_sources(place) 
            if srcrefs is not None:
                placedetail += srcrefs

            # place references
            reflist = self.display_references(place_list[place.handle])
            if reflist is not None:
                placedetail += reflist

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.XHTMLWriter(placepage, of)

class EventListPage(BasePage):
    def __init__(self, report, title, event_types, event_handle_list):
        """
        Will create the event list page

        @param: event_types: a list of the type in the events database
        @param: event_handle_list -- a list of event handles
        """
        BasePage.__init__(self, report, title)
        db = report.database

        of = self.report.create_file("events")
        eventslistpage, head, body = self.write_header(_("Events"))

        # begin events list  division
        with Html("div", class_ = "content", id = "EventList") as eventlist:
            body += eventlist

            msg = _("This page contains an index of all the events in the "
                    "database, sorted by their type and date (if one is "
                    "present), Clicking on an event&#8217;s Gramps ID "
                    "will open a page for that event.")
            eventlist += Html("p", msg, id = "description")

            # get alphabet navigation for class EventListPage
            menu_set = get_first_letters(db, event_types, _ALPHAEVENT)
            alpha_nav, menu_set = alphabet_navigation(menu_set)
            if alpha_nav is not None:
                eventlist += alpha_nav

            # begin alphabet event table
            with Html("table", class_ = "infolist alphaevent") as table:
                eventlist += table

                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                trow.extend(
                    Html("th", label, class_ = "Column" + colclass, inline = True)
                    for (label, colclass) in [
                        [_("Letter"),  "Letter"], 
                        [THEAD,        "Type"],
                        [DHEAD,        "Date"],
                        [GRAMPSID,     "GRAMPSID"],
                        [_PERSON,      "Person"] ]
                    ) 

                tbody = Html("tbody")
                table += tbody

                # separate events by their type and then thier event handles
                for (evt_type, datalist) in sort_event_types(db, event_types, event_handle_list):
                    first_letter = True
                    _EVENT_DISPLAYED = []

                    # sort datalist by date of event
                    datalist = sorted(datalist, key = self._getEventDate)
                    first_event = True

                    while datalist:
                        event_handle = datalist[0]
                        event = db.get_event_from_handle(event_handle)
                        _type = event.type
                        gid = event.gramps_id

                        # check to see if we have listed this gramps_id yet?
                        if gid not in _EVENT_DISPLAYED:

                            # family event 
                            if _type in _EVENTMAP:
                                handle_list = db.find_backlink_handles(event_handle, include_classes = ['Family'])

                            # personal event
                            else:
                                handle_list = db.find_backlink_handles(event_handle, include_classes = ['Person'])
                            if handle_list:

                                trow = Html("tr")
                                tbody += trow

                                # set up hyperlinked letter for alphabet_navigation
                                tcell = Html("td", class_ = "ColumnLetter", inline = True)
                                trow += tcell

                                ltr = unicode(evt_type)[0].capitalize()
                                if first_letter:
                                    trow.attr = 'class = "BeginLetter"'
                                    tcell += Html("a", ltr, name = ltr, 
                                        title = _("Event types beginning with letter " + ltr), inline = True)
                                    first_letter = False

                                else:
                                    tcell += "&nbsp;" 
  
                                # display Event type if first in the list
                                tcell = Html("td", class_ = "ColumnType", inline = True)
                                trow += tcell
                                if first_event:
                                    tcell += evt_type
                                else:
                                    tcell += "&nbsp;" 

                                # event date
                                tcell = Html("td", class_ = "ColumnDate", inline = True)
                                trow += tcell
                                date = gen.lib.Date.EMPTY
                                if event:
                                    date = event.get_date_object()
                                    if date and date is not gen.lib.Date.EMPTY:
                                        tcell += _dd.display(date)
                                else:
                                    tcell += "&nbsp;"   

                                # GRAMPS ID
                                trow += ( Html("td", class_ = "ColumnGRAMPSID") +
                                    self.event_grampsid_link(event_handle, gid, None)
                                    )

                                # Person(s) column
                                tcell = Html("td", class_ = "ColumnPerson")
                                trow += tcell

                                # classname can either be a person or a family
                                first_person = True

                                # get person(s) for ColumnPerson
                                self.complete_people(tcell, first_person, handle_list)

                        _EVENT_DISPLAYED.append( gid )
                        first_event = False
                        datalist.remove("%s" % event_handle)

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page ut for processing
        # and close the file
        self.XHTMLWriter(eventslistpage, of)

    def _getEventDate(self, event_handle):
        event_date = gen.lib.Date.EMPTY
        event = self.report.database.get_event_from_handle(event_handle)
        if event:
            date = event.get_date_object()
            if date:

                # returns the date in YYYY-MM-DD format
                return gen.lib.Date(date.get_year(), date.get_month(), date.get_day())

        # return empty date string
        return event_date

    def event_grampsid_link(self, handle, grampsid, up):
        """
        create a hyperlink from event handle, but show grampsid
        """

        url = self.report.build_url_fname_html(handle, "evt", up)

        # return hyperlink to its caller
        return Html("a", grampsid, href = url, alt = grampsid, inline = True)

class EventPage(BasePage):
    def __init__(self, report, title, event_handle):
        """
        Creates the individual event page

        @param: title -- is the title of the web pages
        @param: event_handle -- the event handle for the database
        @param: progressmeter -- progress meter bar
        """
        db = report.database

        event = db.get_event_from_handle(event_handle)
        evt_gid = event.gramps_id
        BasePage.__init__(self, report, title, evt_gid)

        self.up = True
        subdirs = True
        self.bibli = Bibliography()

        of = self.report.create_file(event_handle, "evt")
        eventpage, head, body = self.write_header(_("Events"))

        # start event detail division
        with Html("div", class_ = "content", id = "EventDetail") as eventdetail:
            body += eventdetail

            # display page title
            evt_type = str(event.type)
            title = "%(eventtype)s --> %(eventtype)s" % {'eventtype' : evt_type }
            eventdetail += Html("h3", title, inline = True)

            # begin eventdetail table
            with Html("table", class_ = "infolist eventlist") as table:
                eventdetail += table
 
                tbody = Html("tbody")
                table += tbody

                if not self.noid and evt_gid:
                    trow = Html("tr") + (
                        Html("td", GRAMPSID, class_ = "ColumnAttribute", inline = True),
                        Html("td", evt_gid, class_ = "ColumnGRAMPSID", inline = True)
                        )
                    tbody += trow
  
                # get event data
                """
                for more information: see get_event_data()
                """ 
                event_data = self.get_event_data(event, event_handle, subdirs, evt_gid)

                for (label, colclass, data) in event_data:
                    if data:

                        trow = Html("tr") + (
                            Html("td", label, class_ = "ColumnAttribute", inline = True),
                            Html('td', data, class_ = "Column" + colclass)
                            )
                        tbody += trow

                trow = Html("tr") + (
                    Html("td", _("Person(s)"), class_ = "ColumnAttribute", inline = True)
                    )
                tbody += trow

                tcell = Html("td", class_ = "ColumnPerson")
                trow += tcell

                # Person(s) field
                if event.type in _EVENTMAP:
                    handle_list = db.find_backlink_handles(event_handle, include_classes = ['Family'])
                else:
                    handle_list = db.find_backlink_handles(event_handle, include_classes = ["Person"]) 

                if handle_list:
                    first_person = True

                    # get person(s) for ColumnPerson
                    self.complete_people(tcell, first_person, handle_list)

            # Narrative subsection
            notelist = event.get_note_list()
            notelist = self.display_note_list(notelist)
            if notelist is not None:
                eventdetail += notelist

            # get attribute list
            attrlist = event.get_attribute_list()
            attrlist = self.display_attr_list(attrlist)
            if attrlist is not None:
                eventdetail += attrlist

            # event source references
            srcrefs = self.display_ind_sources(event)
            if srcrefs is not None:
                eventdetail += srcrefs            

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer()
        body += (fullclear, footer) 

        # send page out for processing
        # and close the page
        self.XHTMLWriter(eventpage, of)

class MediaPage(BasePage):

    def __init__(self, report, title, handle, src_list, my_media_list, info):
        (prev, next, page_number, total_pages) = info
        db = report.database

        media = db.get_object_from_handle(handle)
        # TODO. How do we pass my_media_list down for use in BasePage?
        BasePage.__init__(self, report, title, media.gramps_id)

        # get media rectangles
        _region_items = self.media_ref_rect_regions(handle)

        of = self.report.create_file(handle, "img")
        self.up = True

        self.src_list = src_list
        self.bibli = Bibliography()

        # get media type to be used primarily with "img" tags
        mime_type = media.get_mime_type()
        mtype = gen.mime.get_description(mime_type)

        if mime_type:
            note_only = False
            newpath = self.copy_source_file(handle, media)
            target_exists = newpath is not None
        else:
            note_only = True
            target_exists = False

        copy_thumbnail(self.report, handle, media)
        self.page_title = media.get_description()
        mediapage, head, body = self.write_header("%s - %s" % (_("Media"), self.page_title))

        # begin MediaDetail division
        with Html("div", class_ = "content", id = "GalleryDetail") as mediadetail:
            body += mediadetail

            # media navigation
            with Html("div", id = "GalleryNav") as medianav: 
                mediadetail += medianav
                if prev:
                    medianav += self.media_nav_link(prev, _("Previous"), True)
                data = _('<strong id = "GalleryCurrent">%(page_number)d</strong> of '
                         '<strong id = "GalleryTotal">%(total_pages)d</strong>' ) % {
                         'page_number' : page_number, 'total_pages' : total_pages }
                medianav += Html("span", data, id = "GalleryPages")
                if next:
                    medianav += self.media_nav_link(next, _("Next"), True)

            # missing media error message
            errormsg = _("The file has been moved or deleted.")

            # begin summaryarea division
            with Html("div", id = "summaryarea") as summaryarea:
                mediadetail += summaryarea
                if mime_type:
                    if mime_type.startswith("image"):
                        if not target_exists:
                            with Html("div", id = "MediaDisplay") as mediadisplay:
                                summaryarea += mediadisplay
                                mediadisplay += Html("span", errormsg, class_ = "MissingImage")  
 
                        else:
                            # Check how big the image is relative to the requested 'initial'
                            # image size. If it's significantly bigger, scale it down to
                            # improve the site's responsiveness. We don't want the user to
                            # have to await a large download unnecessarily. Either way, set
                            # the display image size as requested.
                            orig_image_path = Utils.media_path_full(db, media.get_path())
                            (width, height) = ImgManip.image_size(orig_image_path)
                            max_width = self.report.options['maxinitialimagewidth']
                            max_height = self.report.options['maxinitialimageheight']
                            if width != 0 and height != 0:
                                scale_w = (float(max_width)/width) or 1    # the 'or 1' is so that
                                                                           # a max of zero is ignored

                                scale_h = (float(max_height)/height) or 1
                            else:
                                scale_w = 1.0
                                scale_h = 1.0
                            scale = min(scale_w, scale_h, 1.0)
                            new_width = int(width*scale)
                            new_height = int(height*scale)
                            if scale < 0.8:
                                # scale factor is significant enough to warrant making a smaller image
                                initial_image_path = '%s_init.jpg' % os.path.splitext(newpath)[0]
                                initial_image_data = ImgManip.resize_to_jpeg_buffer(orig_image_path,
                                        new_width, new_height)
                                if self.report.archive:
                                    filed, dest = tempfile.mkstemp()
                                    os.write(filed, initial_image_data)
                                    os.close(filed)
                                    self.report.archive.add(dest, initial_image_path)
                                else:
                                    filed = open(os.path.join(self.html_dir, initial_image_path), 'w')
                                    filed.write(initial_image_data)
                                    filed.close()
                            else:
                                # not worth actually making a smaller image
                                initial_image_path = newpath

                            # TODO. Convert disk path to URL.
                            url = self.report.build_url_fname(initial_image_path, None, self.up)
                            with Html("div", id="GalleryDisplay", style = 'width: %dpx; height: %dpx' % (new_width, 
                                new_height)) as mediadisplay:
                                summaryarea += mediadisplay

                                # Feature #2634; display the mouse-selectable regions.
                                # See the large block at the top of this function where
                                # the various regions are stored in _region_items
                                if _region_items:
                                    ordered = Html("ol", class_ = "RegionBox")
                                    mediadisplay += ordered
                                    while len(_region_items) > 0:
                                        (name, x, y, w, h, linkurl) = _region_items.pop()
                                        ordered += Html("li", style = "left:%d%%; top:%d%%; width:%d%%; height:%d%%;"
                                            % (x, y, w, h)) + (
                                            Html("a", name, href = linkurl)
                                            )       

                                # display the image
                                if initial_image_path != newpath:
                                    url = self.report.build_url_fname(newpath, 
                                                None, self.up)
                                mediadisplay += Html("a", href = url) + (
                                    Html("img", width = new_width, 
                                         height = new_height, src = url,
                                         alt = html_escape(self.page_title), title = html_escape(self.page_title))
                                        )
                    else:
                        dirname = tempfile.mkdtemp()
                        thmb_path = os.path.join(dirname, "document.png")
                        if ThumbNails.run_thumbnailer(mime_type,
                                                      Utils.media_path_full(db, media.get_path()),
                                                      thmb_path, 320):
                            try:
                                path = self.report.build_path("preview", media.handle)
                                npath = os.path.join(path, media.handle) + ".png"
                                self.report.copy_file(thmb_path, npath)
                                path = npath
                                os.unlink(thmb_path)
                            except IOError:
                                path = os.path.join("images", "document.png")
                        else:
                            path = os.path.join("images", "document.png")
                        os.rmdir(dirname)

                        with Html("div", id = "GalleryDisplay") as mediadisplay:
                            summaryarea += mediadisplay

                            img_url = self.report.build_url_fname(path, None, self.up)
                            if target_exists:
                                # TODO. Convert disk path to URL
                                url = self.report.build_url_fname(newpath, None, self.up)
                                hyper = Html("a", href = url, title = html_escape(self.page_title)) + (
                                    Html("img", src = img_url, alt = html_escape(self.page_title))
                                    )
                                mediadisplay += hyper
                            else:
                                mediadisplay += Html("span", errormsg, class_ = "MissingImage")  
                else:
                    with Html("div", id = "GalleryDisplay") as mediadisplay:
                        summaryarea += mediadisplay
                        url = self.report.build_url_image("document.png", "images", self.up)
                        mediadisplay += Html("img", src = url, alt = html_escape(self.page_title),
                            title = html_escape(self.page_title))

                # media title
                title = Html("h3", html_escape(self.page_title.strip()), inline = True)
                summaryarea += title

                # begin media table
                with Html("table", class_ = "infolist gallery") as table: 
                    summaryarea += table

                    # GRAMPS ID
                    media_gid = media.gramps_id
                    if not self.noid and media_gid:
                        trow = Html("tr") + (
                            Html("td", GRAMPSID, class_ = "ColumnAttribute", inline = True),
                            Html("td", media_gid, class_ = "ColumnValue", inline = True)
                            )
                        table += trow

                    # mime type
                    if mime_type:   
                        trow = Html("tr") + (
                            Html("td", _("File Type"), class_ = "ColumnAttribute", inline = True),
                            Html("td", mime_type, class_ = "ColumnValue", inline = True)
                            )
                        table += trow

                    # media date
                    date = media.get_date_object()
                    if date and date is not gen.lib.Date.EMPTY:
                        trow = Html("tr") + (
                            Html("td", DHEAD, class_ = "ColumnAttribute", inline = True),
                            Html("td", _dd.display(date), class_ = "ColumnValue", inline = True)
                            )
                        table += trow

            # get media notes
            notelist = self.display_note_list(media.get_note_list() )
            if notelist is not None:
                mediadetail += notelist

            # get attribute list
            attrlist = self.display_attr_list(media.get_attribute_list())
            if attrlist is not None:
                mediadetail += attrlist

            # get media sources
            srclist = self.display_media_sources(media)
            if srclist is not None:
                mediadetail += srclist

            # get media references 
            reflist = self.display_references(my_media_list)
            if reflist is not None:
                mediadetail += reflist

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.XHTMLWriter(mediapage, of)

    def media_nav_link(self, handle, name, up = False):

        url = self.report.build_url_fname_html(handle, "img", up)
        img_name = html_escape(name)
        hyper = Html("a", img_name, name = img_name, id = img_name, href = url,  title = img_name, inline = True)

        # return hyperlink to its callers
        return hyper

    def display_media_sources(self, photo):

        map(self.bibli.add_reference, photo.get_source_references())
        sourcerefs = self.display_source_refs(self.bibli)

        # return source references to its caller
        return sourcerefs

    def copy_source_file(self, handle, photo):
        db = self.report.database   

        ext = os.path.splitext(photo.get_path())[1]
        to_dir = self.report.build_path('images', handle)
        newpath = os.path.join(to_dir, handle) + ext

        fullpath = Utils.media_path_full(db, photo.get_path())
        if not os.path.isfile(fullpath):
            _WRONGMEDIAPATH.append([ photo.get_gramps_id(), fullpath])
            return None
        try:
            if self.report.archive:
                self.report.archive.add(fullpath, str(newpath))
            else:
                to_dir = os.path.join(self.html_dir, to_dir)
                if not os.path.isdir(to_dir):
                    os.makedirs(to_dir)
                shutil.copyfile(fullpath,
                                os.path.join(self.html_dir, newpath))
            return newpath
        except (IOError, OSError), msg:
            error = _("Missing media object:") +                               \
                     "%s (%s)" % (photo.get_description(), photo.get_gramps_id())
            WarningDialog(error, str(msg))
            return None

class SurnameListPage(BasePage):

    ORDER_BY_NAME = 0
    ORDER_BY_COUNT = 1

    def __init__(self, report, title, person_handle_list, order_by=ORDER_BY_NAME, filename = "surnames"):
        BasePage.__init__(self, report, title)
        db = report.database

        if order_by == self.ORDER_BY_NAME:
            of = self.report.create_file(filename)
            surnamelistpage, head, body = self.write_header(_('Surnames'))
        else:
            of = self.report.create_file("surnames_count")
            surnamelistpage, head, body = self.write_header(_('Surnames by person count'))

        # begin surnames division
        with Html("div", class_ = "content", id = "surnames") as surnamelist:
            body += surnamelist

            # page message
            msg = _( 'This page contains an index of all the '
                           'surnames in the database. Selecting a link '
                           'will lead to a list of individuals in the '
                           'database with this same surname.')
            surnamelist += Html("p", msg, id = "description")

            # add alphabet navigation...
            # only if surname list not surname count
            if order_by == self.ORDER_BY_NAME:
                menu_set = get_first_letters(db, person_handle_list, _KEYPERSON)
                alpha_nav, menu_set = alphabet_navigation(menu_set)
                if alpha_nav is not None:
                    surnamelist += alpha_nav

            if order_by == self.ORDER_BY_COUNT:
                table_id = 'SortByCount'
            else:
                table_id = 'SortByName'

            # begin surnamelist table and table head 
            with Html("table", class_ = "infolist surnamelist", id = table_id) as table:
                surnamelist += table

                thead = Html("thead")
                table += thead

                trow = ( Html("tr") +
                    Html("th", _("Letter"), class_ = "ColumnLetter", inline = True)
                    )
                thead += trow

                fname = self.report.surname_fname + self.ext
                tcell = Html("th", class_ = "ColumnSurname", inline = True)
                trow += tcell
                hyper = Html("a", _("Surname"), href = fname)
                tcell += hyper

                fname = "surnames_count" + self.ext
                tcell = Html("th", class_ = "ColumnQuantity", inline = True)
                trow += tcell
                hyper = Html("a", _('Number of People'), href = fname)
                tcell += hyper

                # begin table body
                with Html("tbody") as tbody:
                    table += tbody

                    person_handle_list = sort_people(db, person_handle_list)
                    if order_by == self.ORDER_BY_COUNT:
                        temp_list = {}
                        for (surname, data_list) in person_handle_list:
                            index_val = "%90d_%s" % (999999999-len(data_list), surname)
                            temp_list[index_val] = (surname, data_list)

                        person_handle_list = (temp_list[key]
                            for key in sorted(temp_list, key = locale.strxfrm))

                    last_letter = ''
                    last_surname = ''

                    for (surname, data_list) in person_handle_list:
                        if len(surname) == 0:
                            continue

                        letter = first_letter(surname)

                        trow = Html("tr")
                        tbody += trow
                        if letter != last_letter:
                            last_letter = letter
                            trow.attr = 'class = "BeginLetter"'

                            tcell = ( Html("td", class_ = "ColumnLetter") +
                                Html("a", last_letter, name = last_letter, 
                                    title = "Surnames with letter " + last_letter, inline = True)
                                )
                            trow += tcell

                            trow += Html("td", self.surname_link(name_to_md5(surname), surname), 
                                class_ = "ColumnSurname")
                                
                        elif surname != last_surname:
                            trow += ( Html("td", "&nbsp;", class_ = "ColumnLetter") +
                                Html("td", self.surname_link(name_to_md5(surname), surname), 
                                    class_ = "ColumnSurname", inline = True)
                                ) 
                                
                            last_surname = surname
                        trow += Html("td", len(data_list), class_ = "ColumnQuantity", inline = True)

        # create footer section
        # add clearline for proper styling
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.XHTMLWriter(surnamelistpage, of)  

    def surname_link(self, fname, name, opt_val = None, up = False):
        url = self.report.build_url_fname_html(fname, "srn", up)
        hyper = Html("a", name, href = url, title = name, inline = True)
        if opt_val is not None:
            hyper += opt_val

        # return hyperlink to its caller
        return hyper

class IntroductionPage(BasePage):
    """
    This class will create the Introduction page ...
    """

    def __init__(self, report, title):
        BasePage.__init__(self, report, title)
        db = report.database

        of = self.report.create_file(report.intro_fname)
        intropage, head, body = self.write_header(_('Introduction'))

        # begin Introduction division
        with Html("div", class_ = "content", id = "Introduction") as section:
            body += section

            introimg = self.add_image('introimg')
            if introimg is not None:
                section += introimg

            note_id = report.options['intronote']
            if note_id:
                note = db.get_note_from_gramps_id(note_id) 
                note_text = self.get_note_format(note, False)
 
                # attach note
                section += note_text

        # add clearline for proper styling
        # create footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.XHTMLWriter(intropage, of)

class HomePage(BasePage):
    """
    This class will create the Home Page ...
    """

    def __init__(self, report, title):
        BasePage.__init__(self, report, title)
        db = report.database

        of = self.report.create_file("index")
        homepage, head, body = self.write_header(_('Home'))

        # begin home division
        with Html("div", class_ = "content", id = "Home") as section:
            body += section

            homeimg = self.add_image('homeimg')
            if homeimg is not None:
                section += homeimg

            note_id = report.options['homenote']
            if note_id:
                note = db.get_note_from_gramps_id(note_id)
                note_text = self.get_note_format(note, False)

                # attach note
                section += note_text

         # create clear line for proper styling
        # create footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.XHTMLWriter(homepage, of)  

class SourceListPage(BasePage):

    def __init__(self, report, title, handle_set):
        BasePage.__init__(self, report, title)
        db = report.database

        handle_list = list(handle_set)
        source_dict = {}

        of = self.report.create_file("sources")
        sourcelistpage, head, body = self.write_header(_("Sources"))

        # begin source list division
        with Html("div", class_ = "content", id = "Sources") as sourceslist:
            body += sourceslist

            # Sort the sources
            for handle in handle_list:
                source = db.get_source_from_handle(handle)
                key = source.get_title() + str(source.get_gramps_id())
                source_dict[key] = (source, handle)
            
            keys = sorted(source_dict, key=locale.strxfrm)

            msg = _("This page contains an index of all the sources in the "
                         "database, sorted by their title. Clicking on a source&#8217;s "
                         "title will take you to that source&#8217;s page.")
            sourceslist += Html("p", msg, id = "description")

            # begin sourcelist table and table head
            with Html("table", class_ = "infolist sourcelist") as table:
                sourceslist += table 
                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                header_row = [
                    (None, "RowLabel"),
                    (_("Source Name|Name"), "Name") ]

                trow.extend(
                    Html("th", label or "&nbsp;", class_ = "Column" + colclass, inline = True)
                    for (label, colclass) in header_row)
                    
                # begin table body
                tbody = Html("tbody")
                table += tbody

                for index, key in enumerate(keys):
                    (source, handle) = source_dict[key]

                    trow = ( Html("tr") +
                        Html("td", index + 1, class_ = "ColumnRowLabel", inline = True)
                        )
                    tbody += trow
                    trow += Html("td",
                                self.source_link(handle, source.get_title(),
                                    source.gramps_id), 
                                class_ = "ColumnName")

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.XHTMLWriter(sourcelistpage, of)

class SourcePage(BasePage):

    def __init__(self, report, title, handle, src_list, gid = None):
        db = report.database 

        source = db.get_source_from_handle(handle)
        BasePage.__init__(self, report, title, gid)

        of = self.report.create_file(source.get_handle(), "src")
        self.up = True
        sourcepage, head, body = self.write_header(_('Sources'))

        # begin source detail division
        with Html("div", class_ = "content", id = "SourceDetail") as section:
            body += section 

            media_list = source.get_media_list()
            thumbnail = self.display_first_image_as_thumbnail(media_list, source)
            if thumbnail is not None:
                section += thumbnail

            # add section title
            section += Html("h3", html_escape(source.get_title()), inline = True)
 
            # begin sources table
            with Html("table", class_ = "infolist source") as table:
                section += table

                tbody = Html("tbody")
                table += tbody

                grampsid = None
                if not self.noid and gid:
                    grampsid = gid

                for (label, val) in [
                    (GRAMPSID,                     grampsid),
                    (_("Author"),                  source.author),
                    (_("Publication information"), source.pubinfo),
                    (_("Abbreviation"),            source.abbrev) ]:

                    if val:
                        trow = Html("tr") + (
                            Html("td", label, class_ = "ColumnAttribute"),
                            Html("td", val, class_ = "ColumnValue")
                            )
                        tbody += trow

            # additional media
            sourcemedia = self.display_additional_images_as_gallery(media_list, source)
            if sourcemedia is not None:
                section += sourcemedia

            # additional notes
            notelist = self.display_note_list( source.get_note_list() )
            if notelist is not None:
                section += notelist

            # references
            references = self.display_references(src_list[source.handle])
            if references is not None:
                section += references

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.XHTMLWriter(sourcepage, of)

class MediaListPage(BasePage):

    def __init__(self, report, title):
        BasePage.__init__(self, report, title)
        db = report.database

        of = self.report.create_file("media")
        medialistpage, head, body = self.write_header(_('Media'))

        # begin gallery division
        with Html("div", class_ = "content", id = "Gallery") as medialist:
            body += medialist

            msg = _("This page contains an index of all the media objects "
                          "in the database, sorted by their title. Clicking on "
                          "the title will take you to that media object&#8217;s page.  "
                          "If you see media size dimensions above an image, click on the "
                          "image to see the full sized version.  ")
            medialist += Html("p", msg, id = "description")

            # begin gallery table and table head
            with Html("table", class_ = "infolist gallerylist") as table:
                medialist += table

                # begin table head
                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow
                media_header_row = [
                    ["&nbsp;",    "RowLabel"],
                    [_("Media | Name"),  "Name"],
                    [DHEAD,              "Date"],
                    [_("Mime Type"),     "Mime"]
                    ]
                trow.extend(
                    Html("th", label, class_ = "Column" + colclass, inline = True)
                        for (label, colclass) in media_header_row
                    )
  
                # begin table body
                tbody = Html("tbody")
                table += tbody

                index = 1
                sort = Sort.Sort(db)
                mlist = sorted(self.report.photo_list, key=sort.by_media_title_key)
        
                for handle in mlist:
                    media = db.get_object_from_handle(handle)
                    title = media.get_description() or "[untitled]"

                    trow = Html("tr")
                    tbody += trow

                    media_data_row = [
                        [index,                                 "RowLabel"],
                        [self.media_ref_link(handle, title),    "Name"],
                        [_dd.display(media.get_date_object() ), "Date"],
                        [media.get_mime_type(),                 "Mime"]
                        ] 

                    trow.extend(
                        Html("td", data, class_ = "Column" + colclass)
                            for (data, colclass) in media_data_row
                        )  

                    index += 1

        # add footer section
        # add clearline for proper styling
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.XHTMLWriter(medialistpage, of)

    def media_ref_link(self, handle, name, up = False):

        # get media url
        url = self.report.build_url_fname_html(handle, "img", up)

        # get name
        name = html_escape(name)

        # begin hyper link
        hyper = Html("a", name, href = url, title = name)

        # return hyperlink to its callers
        return hyper

class DownloadPage(BasePage):
    """
    This class will produce the Download Page ...
    """

    def __init__(self, report, title):
        BasePage.__init__(self, report, title)
        db = report.database

        # do NOT include a Download Page
        if not self.report.inc_download:
            return None

        # menu options for class
        # download and description #1

        dlfname1 = self.report.dl_fname1
        dldescr1 = self.report.dl_descr1

        # download and description #2
        dlfname2 = self.report.dl_fname2
        dldescr2 = self.report.dl_descr2

        # download copyright
        dlcopy = self.report.dl_copy

        # if no filenames at all, return???
        if dlfname1 or dlfname2:

            of = self.report.create_file("download")
            downloadpage, head, body = self.write_header(_('Download'))

            # begin download page and table
            with Html("div", class_ = "content", id = "Download") as download:
                body += download

                msg = _("This page is for the user/ creator of this Family Tree/ "
                    "Narrative website to share a couple of files with you "
                    "regarding their family.  If there are any files listed "
                    "below, clicking on them will allow you to download them.")
                download += Html("p", msg, id = "description")

                # begin download table and table head
                with Html("table", class_ = "infolist download") as table:
                    download += table

                    thead = Html("thead")
                    table += thead

                    trow = Html("tr")
                    thead += trow

                    trow.extend(
                        Html("th", label, class_ = "Column" + colclass, inline = True)
                        for (label, colclass) in [
                            (_("File Name"),     "Filename"),
                            (DESCRHEAD,          "Description"),
                            (_("Last Modified"), "Modified") ]
                            ) 
                    # table body
                    tbody = Html("tbody")
                    table += tbody

                    # if dlfname1 is not None, show it???
                    if dlfname1:

                        trow = Html("tr", id = 'Row01')
                        tbody += trow

                        fname = os.path.basename(dlfname1)
                        tcell = ( Html("td", class_ = "ColumnFilename") +
                            Html("a", fname, href = dlfname1, title = dldescr1)
                            )
                        trow += tcell

                        dldescr1 = dldescr1 or "&nbsp;"
                        trow += Html("td", dldescr1, class_ = "ColumnDescription", inline = True)

                        tcell = Html("td", class_ = "ColumnModified", inline = True)
                        trow += tcell 
                        if os.path.exists(dlfname1):
                            modified = os.stat(dlfname1).st_mtime
                            last_mod = datetime.datetime.fromtimestamp(modified)
                            tcell += last_mod
                        else:
                            tcell += "&nbsp;"

                    # if download filename #2, show it???
                    if dlfname2:

                        # begin row #2
                        trow = Html("tr", id = 'Row02')
                        tbody += trow

                        fname = os.path.basename(dlfname2)
                        tcell = ( Html("td", class_ = "ColumnFilename") +
                            Html("a", fname, href = dlfname2, alt = dldescr2)
                            )  
                        trow += tcell

                        dldescr2 = dldescr2 or "&nbsp;"
                        trow += Html("td", dldescr2, class_ = "ColumnDescription", inline = True)

                        tcell = Html("td", id = 'Col04', class_ = "ColumnModified",  inline = True)
                        trow += tcell
                        if os.path.exists(dlfname2):
                            modified = os.stat(dlfname2).st_mtime
                            last_mod = datetime.datetime.fromtimestamp(modified)
                            tcell += last_mod
                        else:
                            tcell += "&nbsp;"

        # display Copyright license for these files
        copyright = self.get_copyright_license(dlcopy)
        if copyright: 
            msg = _("The Copyright License for these files are: ")
            download += Html("p", msg, id = "description") 
            download += Html("a", copyright, class_ = "copyright")

        # clear line for proper styling
        # create footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.XHTMLWriter(downloadpage, of)

class ContactPage(BasePage):

    def __init__(self, report, title):
        BasePage.__init__(self, report, title)
        db = report.database

        of = self.report.create_file("contact")
        contactpage, head, body = self.write_header(_('Contact'))

        # begin contact division
        with Html("div", class_ = "content", id = "Contact") as section:
            body += section 

            # begin summaryarea division
            with Html("div", id = 'summaryarea') as summaryarea:
                section  += summaryarea

                contactimg = self.add_image('contactimg', 200)
                if contactimg is not None:
                    summaryarea += contactimg

                # get researcher information
                r = Utils.get_researcher()

                with Html("div", id = 'researcher') as researcher:
                    summaryarea += researcher
                    if r.name:
                        r.name = r.name.replace(',,,', '')
                        researcher += Html("h3", r.name, inline = True)
                    if r.addr:
                        researcher += Html("span", r.addr, id = 'streetaddress')
                    text = "".join([r.city, r.state, r.postal])
                    if text:
                        city = Html("span", r.city, id = 'city', inline = True)
                        state = Html("span", r.state, id = 'state', inline = True)
                        postal = Html("span", r.postal, id = 'postalcode', inline = True)
                        researcher += (city, state, postal)
                    if r.country:
                        researcher += Html("span", r.country, id = 'country', inline = True)
                    if r.email:
                        researcher += ( Html("span", id = 'email') +
                            Html("a", r.email, href = 'mailto:%s?subject="from Gramps Web Site"' 
                                % r.email, inline = True)
                            )

                    # add clear line for proper styling
                    summaryarea += fullclear

                    note_id = report.options['contactnote']
                    if note_id:
                        note = db.get_note_from_gramps_id(note_id)
                        note_text = self.get_note_format(note, False)
 
                        # attach note
                        summaryarea += note_text

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for porcessing
        # and close the file
        self.XHTMLWriter(contactpage, of)

class IndividualPage(BasePage):
    """
    This class is used to write HTML for an individual.
    """
    gender_map = {
        gen.lib.Person.MALE    : _('male'),
        gen.lib.Person.FEMALE  : _('female'),
        gen.lib.Person.UNKNOWN : _('unknown'),
        }

    def __init__(self, report, title, person, ind_list, place_list, src_list, attribute_list):
        BasePage.__init__(self, report, title, person.gramps_id)
        self.person = person
        self.ind_list = ind_list
        self.src_list = src_list        # Used by get_citation_links()
        self.bibli = Bibliography()
        self.place_list = place_list
        self.sort_name = self.get_name(person)
        self.name = self.get_name(person)
        db = report.database

        of = self.report.create_file(person.handle, "ppl")
        self.up = True
        indivdetpage, head, body = self.write_header(self.sort_name)

        # begin individualdetail division
        with Html("div", class_ = "content", id = 'IndividualDetail') as individualdetail:
            body += individualdetail

            # display a person's general data
            thumbnail, name, summary = self.display_ind_general()

            # if there is a thumbnail, add it also?
            if thumbnail is not None:
                individualdetail += thumbnail
            individualdetail += (name, summary)

            # display a person's events
            sect2 = self.display_ind_events()
            if sect2 is not None:
                individualdetail += sect2

            # display parents
            sect3 = self.display_ind_parents()
            if sect3 is not None:
                individualdetail += sect3

            # display relationships
            sect4 = self.display_ind_families()
            if sect4 is not None:
                individualdetail += sect4

            # display LDS ordinance
            sect5 = self.display_lds_ordinance(person)
            if sect5 is not None:
                individualdetail += sect5

            # display address(es) and show sources
            sect6 = self.display_addr_list(self.person.get_address_list(), True)
            if sect6 is not None:
                individualdetail += sect6

            photo_list = self.person.get_media_list()
            media_list = photo_list[:]
            for handle in self.person.get_family_handle_list():
                family = db.get_family_from_handle(handle)
                media_list += family.get_media_list()
                for evt_ref in family.get_event_ref_list():
                    event = db.get_event_from_handle(evt_ref.ref)
                    media_list += event.get_media_list()
            for evt_ref in self.person.get_primary_event_ref_list():
                event = db.get_event_from_handle(evt_ref.ref)
                if event:
                    media_list += event.get_media_list()

            # display additional images as gallery
            sect7 = self.display_additional_images_as_gallery(media_list, self.person)
            if sect7 is not None:
                individualdetail += sect7

            # display Narrative
            notelist = person.get_note_list()
            sect8 = self.display_note_list(notelist)
            if sect8 is not None:
                individualdetail += sect8

            # display attributes
            sect9 = self.display_attr_list(attribute_list)
            if sect9 is not None:
                individualdetail += sect9

            # display web links
            sect10 = self.display_url_list(self.person.get_url_list())
            if sect10 is not None:
                individualdetail += sect10

            # display associations
            assocs = self.person.get_person_ref_list()
            if assocs:
                individualdetail += self.display_ind_associations(assocs)

            # display sources
            sect11 = self.display_ind_sources(self.person)
            if sect11 is not None:
                individualdetail += sect11

            # display pedigree
            sect13 = self.display_ind_pedigree()
            if sect13 is not None:
                individualdetail += sect13

            # display ancestor tree   
            if report.options['graph']:
                sect14 = self.display_tree()
                if sect14 is not None:
                    individualdetail += sect14

        # add clearline for proper styling
        # create footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.XHTMLWriter(indivdetpage, of)

    def draw_box(self, center, col, person):
        db = self.report.database

        top = center - _HEIGHT/2
        xoff = _XOFFSET+col*(_WIDTH+_HGAP)
        sex = person.gender
        if sex == gen.lib.Person.MALE:
            divclass = "male"
        elif sex == gen.lib.Person.FEMALE:
            divclass = "female"
        else:
            divclass = "unknown"
            
        boxbg = Html("div", class_ = "boxbg %s AncCol%s" % (divclass, col),
                    style="top: %dpx; left: %dpx;" % (top, xoff+1)
                   )
                      
        person_name = self.get_name(person)
        if person.handle in self.ind_list:
            thumbnailUrl = None
            if self.create_media and col < 5:
                photolist = person.get_media_list()
                if photolist:
                    photo_handle = photolist[0].get_reference_handle()
                    photo = db.get_object_from_handle(photo_handle)
                    mime_type = photo.get_mime_type()
                    if mime_type:
                        region = self.media_ref_region_to_object(photo_handle, person)
                        if region:
                            # make a thumbnail of this region
                            newpath = copy_thumbnail(self.report, photo_handle, photo, region)
                            # TODO. Check if build_url_fname can be used.
                            newpath = "/".join(['..']*3 + [newpath])
                            if constfunc.win():
                                newpath = newpath.replace('\\',"/")
                            thumbnailUrl = newpath
                            #snapshot += self.media_link(photo_handle, newpath, '', up = True)

                        else:
                            (photoUrl, thumbnailUrl) = self.report.prepare_copy_media(photo)
                            thumbnailUrl = "/".join(['..']*3 + [thumbnailUrl])
                            if constfunc.win():
                                thumbnailUrl = thumbnailUrl.replace('\\',"/")

            url = self.report.build_url_fname_html(person.handle, "ppl", True)
            boxbg += self.person_link(url, person, name_style = True, 
                thumbnailUrl=thumbnailUrl)
        else:
            boxbg += Html("span", person_name, class_ = "unlinked", inline = True)
        shadow = Html("div", class_ = "shadow", inline = True, style="top: %dpx; left: %dpx;"
            % (top+_SHADOW, xoff+_SHADOW) )

        return [boxbg, shadow]

    def extend_line(self, y0, x0):
        style = "top: %dpx; left: %dpx; width: %dpx"
        bv = Html("div", class_ = "bvline", inline = True,
                      style=style % (y0, x0, _HGAP/2)
                    )
        gv = Html("div", class_ = "gvline", inline = True,
                      style=style % (y0+_SHADOW, x0, _HGAP/2+_SHADOW)
                    )  
        return [bv, gv]

    def connect_line(self, y0, y1, col):
        y = min(y0, y1)
        stylew = "top: %dpx; left: %dpx; width: %dpx;"
        styleh = "top: %dpx; left: %dpx; height: %dpx;"
        x0 = _XOFFSET + col * _WIDTH + (col-1)*_HGAP + _HGAP/2
        bv = Html("div", class_ = "bvline", inline = True, style=stylew % (y1, x0, _HGAP/2))
        gv = Html("div", class_ = "gvline", inline = True, style=stylew % 
            (y1+_SHADOW, x0+_SHADOW, _HGAP/2+_SHADOW))
        bh = Html("div", class_ = "bhline", inline = True, style=styleh % (y, x0, abs(y0-y1)))
        gh = Html("div", class_ = "gvline", inline = True, style=styleh %
                 (y+_SHADOW, x0+_SHADOW, abs(y0-y1)))
        return [bv, gv, bh, gh]

    def draw_connected_box(self, center1, center2, col, handle):
        db = self.report.database

        box = []
        if not handle:
            return box
        person = db.get_person_from_handle(handle)
        box = self.draw_box(center2, col, person)
        box += self.connect_line(center1, center2, col)
        return box

    def display_tree(self):
        tree = []
        if not self.person.get_main_parents_family_handle():
            return None

        generations = self.report.options['graphgens']
        max_in_col = 1 << (generations-1)
        max_size = _HEIGHT*max_in_col + _VGAP*(max_in_col+1)
        center = int(max_size/2)

        with Html("div", id = "tree", class_ = "subsection") as tree:
            tree += Html("h4", _('Ancestors'), inline = True)
            with Html("div", id = "treeContainer",
                    style="width:%dpx; height:%dpx;" %
                        (_XOFFSET+(generations)*_WIDTH+(generations-1)*_HGAP, 
                        max_size)
                     ) as container:
                tree += container
                container += self.draw_tree(1, generations, max_size, 
                                            0, center, self.person.handle)
        return tree

    def draw_tree(self, gen_nr, maxgen, max_size, old_center, new_center, phandle):
        db = self.report.database

        tree = []
        if gen_nr > maxgen:
            return tree
        gen_offset = int(max_size / pow(2, gen_nr+1))
        person = db.get_person_from_handle(phandle)
        if not person:
            return tree

        if gen_nr == 1:
            tree = self.draw_box(new_center, 0, person)
        else:
            tree = self.draw_connected_box(old_center, new_center, gen_nr-1, phandle)

        if gen_nr == maxgen:
            return tree

        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            line_offset = _XOFFSET + gen_nr*_WIDTH + (gen_nr-1)*_HGAP
            tree += self.extend_line(new_center, line_offset)

            family = db.get_family_from_handle(family_handle)

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
        display an individual's associations
        """

        # begin Associations division  
        with Html("div", class_ = "subsection", id = "Associations") as section:
            section += Html("h4", _('Associations'), inline = True)

            with Html("table", class_ = "infolist assoclist") as table:
                section += table

                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                assoc_row = [
                    (_("Person"),       'Person'),
                    (_('Relationship'), 'Relationship'),
                    (NHEAD,             'Notes'),
                    (SHEAD,             'Sources'),
                    ]

                trow.extend(
                    Html("th", label, class_="Column" + colclass, inline=True)
                    for (label, colclass) in assoc_row)

                tbody = Html("tbody")
                table += tbody

                for person_ref in assoclist:
                    if person_ref.ref not in self.report.person_handles:
                        continue
                    trow = Html("tr")
                    tbody += trow

                    person = self.report.database.get_person_from_handle(person_ref.ref)
                    url = self.report.build_url_fname_html(person.handle, "ppl", True)
                    person_name = self.get_name(person)
                    person_link = Html("a", person_name, href=url, title=html_escape(person_name))

                    index = 0
                    for data in [
                        person_link,
                        person_ref.get_relation(),
                        self.dump_notes(person_ref.get_note_list()),
                        self.get_citation_links(person_ref.get_source_references()),
                        ]: 

                        # get colclass from assoc_row
                        colclass = assoc_row[index][1]

                        trow += Html("td", data, class_ = "Column" + colclass, 
                            inline = True)  
                        index += 1

        # return section to its callers
        return section

    def display_ind_pedigree(self):
        """
        Display an individual's pedigree
        """
        db = self.report.database

        # Define helper functions
        
        def children_ped(ol):
            if family:
                for child_ref in family.get_child_ref_list():
                    child_handle = child_ref.ref
                    if child_handle == self.person.handle:
                        child_ped(ol)
                    else:
                        child = db.get_person_from_handle(child_handle)
                        ol += Html("li") + self.pedigree_person(child)
            else:
                child_ped(ol)
            return ol
                
        def child_ped(ol):
            ol += Html("li", class_ = "thisperson", inline = True) + self.name
            family = self.pedigree_family()
            if family:
                ol += Html("ol", class_ = "spouselist") + family
            return ol
        
        # End of helper functions

        parent_handle_list = self.person.get_parent_family_handle_list()
        if parent_handle_list:
            parent_handle = parent_handle_list[0]
            family = db.get_family_from_handle(parent_handle)
            father_handle = family.get_father_handle()
            mother_handle = family.get_mother_handle()
            mother = db.get_person_from_handle(mother_handle)
            father = db.get_person_from_handle(father_handle)
        else:
            family = None
            father = None
            mother = None

        with Html("div", id = "pedigree", class_ = "subsection") as ped:
            ped += Html("h4", _('Pedigree'), inline = True)
            with Html("ol", class_ = "pedigreegen") as pedol:
                ped += pedol
                if father and mother:
                    pedfa = Html("li") + self.pedigree_person(father)
                    pedol += pedfa
                    with Html("ol") as pedma:
                        pedfa += pedma
                        pedma += (Html("li", class_ = "spouse") +
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
                    pedol += children_ped(Html("ol"))
        return ped
        
    def display_ind_general(self):
        """
        display an individual's general information...
        """
        db = self.report.database

        self.page_title = self.sort_name
        thumbnail = self.display_first_image_as_thumbnail(self.person.get_media_list(), self.person)
        section_title = Html("h3", self.get_name(self.person), inline = True)

        # begin summaryarea division
        with Html("div", id = 'summaryarea') as summaryarea:

            # begin general details table
            with Html("table", class_ = "infolist") as table:
                summaryarea += table

                primary_name = self.person.get_primary_name()
                all_names = [primary_name] + self.person.get_alternate_names()

                # Names [and their sources]
                for name in all_names:
                    pname =  _nd.display_name(name)
                    if name == primary_name:
                        pname += self.get_citation_links(self.person.get_source_references() ) 
                    pname += self.get_citation_links( name.get_source_references() )

                    # if we have just a firstname, then the name is preceeded by ", "
                    # which doesn't exactly look very nice printed on the web page
                    if pname[:2] == ', ':
                        pname = pname[2:]
                    if name != primary_name:
                        datetext = _dd.display(name.date)
                        if datetext:
                            pname = datetext + ': ' + pname

                    type_ = str( name.get_type() )
                    trow = Html("tr") + (
                        Html("td", type_, class_ = "ColumnAttribute", inline = True)
                        )
                    table += trow
                    tcell = Html("td", pname, class_ = "ColumnValue")
                    trow += tcell

                    # display any notes associated with this name
                    notelist = name.get_note_list()
                    if len(notelist):
                        unordered = Html("ul")
                        tcell += unordered

                        for notehandle in notelist:
                            note = db.get_note_from_handle(notehandle)
                            if note:
                                note_text = self.get_note_format(note, True)
 
                                # attach note
                                unordered += note_text

                # display call name
                first_name = primary_name.get_first_name()
                for name in all_names:
                    call_name = name.get_call_name()
                    if call_name and call_name != first_name:
                        call_name += self.get_citation_links(name.get_source_references() )
                        trow = Html("tr") + (
                            Html("td", _("Call Name"), class_ = "ColumnAttribute", inline = True),
                            Html("td", call_name, class_ = "ColumnValue", inline = True)
                            )
                        table += trow
  
                # display the nickname attribute
                nick_name = self.person.get_nick_name()
                if nick_name and nick_name != first_name:
                    nick_name += self.get_citation_links(self.person.get_source_references() )
                    trow = Html("tr") + (
                        Html("td", _("Nick Name"), class_ = "ColumnAttribute", inline = True),
                        Html("td", nick_name, class_ = "ColumnValue", inline = True)
                        )
                    table += trow 

                # GRAMPS ID
                person_gid = self.person.get_gramps_id()
                if not self.noid and person_gid:
                    trow = Html("tr") + (
                        Html("td", GRAMPSID, class_ = "ColumnAttribute", inline = True),
                        Html("td", person_gid, class_ = "ColumnValue", inline = True)
                        )
                    table += trow

                # Gender
                gender = self.gender_map[self.person.gender]
                trow = Html("tr") + (
                    Html("td", _("Gender"), class_ = "ColumnAttribute", inline = True),
                    Html("td", gender, class_ = "ColumnValue", inline = True)
                    )
                table += trow

                # Age At Death???
                birth_date = gen.lib.Date.EMPTY
                birth_ref = self.person.get_birth_ref()
                if birth_ref:
                    birth = db.get_event_from_handle(birth_ref.ref)
                    if birth: 
                        birth_date = birth.get_date_object()

                if birth_date and birth_date is not gen.lib.Date.EMPTY:
                    alive = Utils.probably_alive(self.person, db, date.Today() )

                    death_date = _find_death_date(db, self.person)
                    if not alive and death_date is not None:
                        nyears = death_date - birth_date
                        nyears.format(precision = 3)
                        trow = Html("tr") + (
                            Html("td", _("Age at Death"), class_ = "ColumnAttribute", inline = True),
                            Html("td", nyears, class_ = "ColumnValue", inline = True)
                            )
                        table += trow

        # return all three pieces to its caller
        # do NOT combine before returning to class IndividualPage
        return thumbnail, section_title, summaryarea

    def display_ind_events(self):
        """
        will create the events table
        """

        evt_ref_list = self.person.get_event_ref_list()

        if not evt_ref_list:
            return None
        db = self.report.database
            
        # begin events division and section title
        with Html("div", id = "events", class_ = "subsection") as section:
            section += Html("h4", _("Events"), inline = True)

            # begin events table
            with Html("table", class_ = "infolist eventlist") as table:
                section += table

                thead = Html("thead")
                table += thead

                thead += self.display_event_header()

                tbody = Html("tbody")
                table += tbody

                for evt_ref in evt_ref_list:
                    event = db.get_event_from_handle(evt_ref.ref)

                    # display event row
                    """
                    @param: event object
                    @param: event_ref = event reference
                    @param: subdirs = True or False
                    @param: hyp = show hyperlinked evt type or not?
                    @params: omit = role to be omitted in output
                    """
                    tbody += self.display_event_row(event, evt_ref, True, True,
                    EventRoleType.PRIMARY)
 
        # return section to its caller
        return section

    def display_lds_ordinance(self, person):
        """
        display LDS information for a person or family
        """

        ldsordlist = person.lds_ord_list
        if not ldsordlist:
            return None
        db = self.report.database

        # begin LDS Ordinance division and section title
        with Html("div", class_ = "subsection", id = "LDSOrdinance") as section:
            section += Html("h4", _("Latter-Day Saints/ LDS Ordinance"), inline = True)

            # ump individual LDS ordinance list
            section += self.dump_ordinance(db, self.person)

        # return section to its caller
        return section

    def display_child_link(self, child_handle):
        """
        display child link ...
        """
        db = self.report.database

        child = db.get_person_from_handle(child_handle)
        gid = child.gramps_id
        list = Html("li")
        if child_handle in self.ind_list:
            url = self.report.build_url_fname_html(child_handle, "ppl", True)
            list += self.person_link(url, child, True, gid = gid)

        else:
            list += self.get_name(child)

        # return list to its caller
        return list

    def display_parent(self, handle, title, rel):
        """
        This will display a parent ...
        """
        db = self.report.database

        person = db.get_person_from_handle(handle)
        tcell1 = Html("td", title, class_ = "ColumnAttribute", inline = True)
        tcell2 = Html("td", class_ = "ColumnValue")

        gid = person.gramps_id
        if handle in self.ind_list:
            url = self.report.build_url_fname_html(handle, "ppl", True)
            tcell2 += self.person_link(url, person, True, gid = gid)
        else:
            person_name = self.get_name(person)
            tcell2 += person_name
        if rel and rel != gen.lib.ChildRefType(gen.lib.ChildRefType.BIRTH):
            tcell2 += '&nbsp;&nbsp;&nbsp;(%s)' % str(rel)

        # return table columns to its caller
        return tcell1, tcell2

    def display_ind_parents(self):
        """
        Display a person's parents
        """

        birthorder = self.report.options['birthorder']
        parent_list = self.person.get_parent_family_handle_list()

        if not parent_list:
            return None

        db = self.report.database

        # begin parents division
        with Html("div", class_ = "subsection", id = "parents") as section:
            section += Html("h4", PARENTS, inline = True)

            # begin parents table
            with Html("table", class_ = "infolist") as table:
                section += table

                first = True
                if parent_list:
                    for family_handle in parent_list:
                        family = db.get_family_from_handle(family_handle)

                        # Get the mother and father relationships
                        frel = None
                        mrel = None
                        sibling = set()
  
                        child_handle = self.person.get_handle()
                        child_ref_list = family.get_child_ref_list()
                        for child_ref in child_ref_list:
                            if child_ref.ref == child_handle:
                                frel = child_ref.get_father_relation()
                                mrel = child_ref.get_mother_relation()
                                break

                        if not first:
                            trow = Html("tr") +(
                                Html("td", "&nbsp;", colspan = 2, inline = True)
                                )
                            table += trow
                        else:
                            first = False

                        father_handle = family.get_father_handle()
                        if father_handle:
                            trow = Html("tr")
                            table += trow

                            tcell1, tcell2 = self.display_parent(father_handle, _("Father"), frel)
                            trow += (tcell1, tcell2)
                        mother_handle = family.get_mother_handle()
                        if mother_handle:
                            trow = Html("tr")
                            table += trow

                            tcell1, tcell2  = self.display_parent(mother_handle, _("Mother"), mrel)
                            trow += (tcell1, tcell2)

                        first = False
                        if len(child_ref_list) > 1:
                            childlist = [child_ref.ref for child_ref in child_ref_list]
                            sibling.update(childlist)

                    # now that we have all siblings in families of the person,
                    # display them...    
                    if sibling:
                        trow = Html("tr") + (
                            Html("td", _("Siblings"), class_ = "ColumnAttribute", inline = True)
                            )
                        table += trow

                        tcell = Html("td", class_ = "ColumnValue")
                        trow += tcell

                        ordered = Html("ol")
                        tcell += ordered 

                        if birthorder:
                            kids = sorted(add_birthdate(db, sibling))
                            ordered.extend(
                                self.display_child_link(child_handle)
                                    for birth_date, child_handle in kids
                                        if child_handle != self.person.handle)

                        else:
                            ordered.extend(
                                self.display_child_link(child_handle)
                                    for child_handle in sibling
                                        if child_handle != self.person.handle)

                    # Also try to identify half-siblings
                    half_siblings = set()

                    ## FOLLOWING CODE IS WRONG, AS showallsiblings = False
                    ## THIS CODE WILL NOT RUN
                    ## TO FIX: the code only works if the user has his
                    ## half/step siblings in a specific way in the database,
                    ## however this way is not the official way
                    ## The official way is:
                    ##    1. step or half siblings _must_ be present 
                    ##       somewhere in the same family. So the search
                    ##       here over other families is wrong
                    ##    2. to determine the relationship, only the child
                    ##       relationship must be looked at, nothing else! 
                    showallsiblings = False #self.report.options['showhalfsiblings']
##                    # if we have a known father...
##                    if father_handle and showallsiblings:
##                        # 1) get all of the families in which this father is involved
##                        # 2) get all of the children from those families
##                        # 3) if the children are not already listed as siblings...
##                        # 4) then remember those children since we're going to list them
##                        father = db.get_person_from_handle(father_handle)
##                        for family_handle in father.get_family_handle_list():
##                            family = db.get_family_from_handle(family_handle)
##                            for half_child_ref in family.get_child_ref_list():
##                                half_child_handle = half_child_ref.ref
##                                if half_child_handle not in sibling:
##                                    if half_child_handle != self.person.handle:
##                                        # we have a new step/half sibling
##                                        half_siblings.add(half_child_handle)
##
##                    # do the same thing with the mother (see "father" just above):
##                    if mother_handle and showallsiblings:
##                        mother = db.get_person_from_handle(mother_handle)
##                        for family_handle in mother.get_family_handle_list():
##                            family = db.get_family_from_handle(family_handle)
##                            for half_child_ref in family.get_child_ref_list():
##                                half_child_handle = half_child_ref.ref
##                                if half_child_handle not in sibling:
##                                    if half_child_handle != self.person.handle:
##                                        # we have a new half sibling
##                                        half_siblings.add(half_child_handle)
##
##                    # now that we have all half- siblings, display them...    
##                    if half_siblings:
##                        trow = Html("tr") + (
##                            Html("td", _("Half Siblings"), class_ = "ColumnAttribute", inline = True)
##                            )
##                        table += trow
##
##                        tcell = Html("td", class_ = "ColumnValue")
##                        trow += tcell
##
##                        ordered = Html("ol")
##                        tcell += ordered
##
##                        if birthorder:
##                            kids = sorted(add_birthdate(db, half_siblings))
##
##                            ordered.extend(
##                                self.display_child_link(child_handle)
##                                for birth_date, child_handle in kids)
##                        else:
##                            ordered += map(self.display_child_link, half_siblings)
##
##                    # get step-siblings
##                    if showallsiblings:
##                        step_siblings = set()
##
##                        # to find the step-siblings, we need to identify
##                        # all of the families that can be linked back to
##                        # the current person, and then extract the children
##                        # from those families
##                        all_family_handles = set()
##                        all_parent_handles = set()
##                        tmp_parent_handles = set()
##
##                        # first we queue up the parents we know about
##                        if mother_handle:
##                            tmp_parent_handles.add(mother_handle)
##                        if father_handle:
##                            tmp_parent_handles.add(father_handle)
##
##                        while len(tmp_parent_handles):
##                            # pop the next parent from the set
##                            parent_handle = tmp_parent_handles.pop()
##
##                            # add this parent to our official list
##                            all_parent_handles.add(parent_handle)
##
##                            # get all families with this parent
##                            parent = db.get_person_from_handle(parent_handle)
##                            for family_handle in parent.get_family_handle_list():
##
##                                all_family_handles.add(family_handle)
##
##                                # we already have 1 parent from this family
##                                # (see "parent" above) so now see if we need
##                                # to queue up the other parent
##                                family = db.get_family_from_handle(family_handle)
##                                tmp_mother_handle = family.get_mother_handle()
##                                if  tmp_mother_handle and \
##                                    tmp_mother_handle != parent and \
##                                    tmp_mother_handle not in tmp_parent_handles and \
##                                    tmp_mother_handle not in all_parent_handles:
##                                    tmp_parent_handles.add(tmp_mother_handle)
##                                tmp_father_handle = family.get_father_handle()
##                                if  tmp_father_handle and \
##                                    tmp_father_handle != parent and \
##                                    tmp_father_handle not in tmp_parent_handles and \
##                                    tmp_father_handle not in all_parent_handles:
##                                    tmp_parent_handles.add(tmp_father_handle)
##
##                        # once we get here, we have all of the families
##                        # that could result in step-siblings; note that
##                        # we can only have step-siblings if the number
##                        # of families involved is > 1
##
##                        if len(all_family_handles) > 1:
##                            while len(all_family_handles):
##                                # pop the next family from the set
##                                family_handle = all_family_handles.pop()
##                                # look in this family for children we haven't yet seen
##                                family = db.get_family_from_handle(family_handle)
##                                for step_child_ref in family.get_child_ref_list():
##                                    step_child_handle = step_child_ref.ref
##                                    if step_child_handle not in sibling and \
##                                           step_child_handle not in half_siblings and \
##                                           step_child_handle != self.person.handle:
##                                        # we have a new step sibling
##                                        step_siblings.add(step_child_handle)
##
##                        # now that we have all step- siblings, display them...    
##                        if len(step_siblings):
##                            trow = Html("tr") + (
##                                Html("td", _("Step Siblings"), class_ = "ColumnAttribute", inline = True)
##                                )
##                            table += trow
##
##                            tcell = Html("td", class_ = "ColumnValue")
##                            trow += tcell
##
##                            ordered = Html("ol")
##                            tcell += ordered
##
##                            if birthorder:
##                                kids = []
##                                kids = sorted(add_birthdate(db, step_siblings))
##
##                                ordered.extend(
##                                    self.display_child_link(child_handle)
##                                        for birth_date, child_handle in kids)
##
##                            else:
##                                ordered += map(self.display_child_link,
##                                                                step_siblings)

        # return parents division to its caller
        return section

    def display_ind_families(self):
        """
        Displays a person's relationships ...
        """

        family_list = self.person.get_family_handle_list()
        if not family_list:
            return None
        db = self.report.database

        # begin families division and section title
        with Html("div", class_ = "subsection", id = "families") as section:
            section += Html("h4", _("Families"), inline = True)

            # begin families table
            with Html("table", class_ = "infolist") as table:
                section += table

                for family_handle in family_list:
                    family = db.get_family_from_handle(family_handle)

                    self.display_partner(family, table)

                    childlist = family.get_child_ref_list()
                    if childlist:
                        trow = Html("tr") + (
                            Html("td", "&nbsp;", class_ = "ColumnType", inline = True),
                            Html("td", _("Children"), class_ = "ColumnAttribute", inline = True)
                            )
                        table += trow

                        tcell = Html("td", class_ = "ColumnValue")
                        trow += tcell

                        ordered = Html("ol")
                        tcell += ordered

                        childlist = [child_ref.ref for child_ref in childlist]

                        if self.report.options['birthorder']:
                            kids = sorted(add_birthdate(db, childlist))

                            ordered.extend(
                                self.display_child_link(child_handle)
                                    for birth_date, child_handle in kids)
                        else:
                            ordered += map(self.display_child_link, childlist)

                    # family LDS ordinance list
                    famldslist = family.lds_ord_list
                    if famldslist:
                        trow = Html("tr") + (
                            Html("td", "&nbsp;", class_ = "ColumnType", inline = True),
                            Html("td", "&nbsp;", class_ = "ColumnAttribute", inline = True),
                            Html("td", self.dump_ordinance(db, family, "Family"), class_ = "ColumnValue")
                            )
                        table += trow

        # return section to its caller
        return section

    def display_partner(self, family, table):
        """
        display an individual's partner
        """

        gender = self.person.gender
        reltype = family.get_relationship()
        db = self.report.database

        if reltype == FamilyRelType.MARRIED:
            if gender == gen.lib.Person.FEMALE:
                relstr = _("Husband")
            elif gender == gen.lib.Person.MALE:
                relstr = _("Wife")
            else:
                relstr = _PARTNER
        else:
            relstr = _PARTNER

        partner_handle = ReportUtils.find_spouse(self.person, family)
        if partner_handle:
            partner = db.get_person_from_handle(partner_handle)
            partner_name = self.get_name(partner)
        else:
            partner_name = _("unknown")

        # family relationship type
        rtype = str(family.get_relationship())
        trow = Html("tr", class_ = "BeginFamily") + (
            Html("td", rtype, class_ = "ColumnType", inline = True),
            Html("td", relstr, class_ = "ColumnAttribute", inline = True)  
            )
        table += trow

        tcell = Html("td", class_ = "ColumnValue")
        trow += tcell

        # display partner's name
        if partner_handle:
            if partner_handle in self.ind_list:
                url = self.report.build_url_fname_html(partner_handle, "ppl", True)
                tcell += self.person_link(url, partner, True, gid = partner.gramps_id)
            else:
                tcell += partner_name

        # display family events; such as marriage and divorce events
        family_events = family.get_event_ref_list()
        if family_events: 
            trow = Html("tr") + (
                Html("td", "&nbsp;", class_ = "ColumnType", inline = True),
                Html("td", "&nbsp;", class_ = "ColumnAttribute", inline = True),
                Html("td", self.format_event(family_events), class_ = "ColumnValue")
                )
            table += trow

    def pedigree_person(self, person):
        """
        will produce a hyperlink for a pedigree person ...
        """

        person_name = self.get_name(person)
        if person.handle in self.ind_list:
            url = self.report.build_url_fname_html(person.handle, "ppl", True)
            hyper = self.person_link(url, person, name_style = True)
        else:
            hyper = person_name

        # return hyperlink to its callers
        # can be an actual hyperlink or just a person's name
        return hyper

    def pedigree_family(self):
        """
        Returns a family pedigree
        """
        db = self.report.database

        ped = []
        for family_handle in self.person.get_family_handle_list():
            rel_family = db.get_family_from_handle(family_handle)
            spouse_handle = ReportUtils.find_spouse(self.person, rel_family)
            if spouse_handle:
                spouse = db.get_person_from_handle(spouse_handle)
                pedsp = (Html("li", class_ = "spouse") +
                         self.pedigree_person(spouse)
                        )
                ped += [pedsp]
            else:
                pedsp = ped
            childlist = rel_family.get_child_ref_list()
            if childlist:
                with Html("ol") as childol:
                    pedsp += [childol]
                    for child_ref in childlist:
                        child = db.get_person_from_handle(child_ref.ref)
                        childol += (Html("li") +
                                    self.pedigree_person(child)
                                   )
        return ped

    def display_event_header(self):
        """
        will print the event header row for display_event_row() and
            format_event()
        """ 

        trow = Html("tr")

        trow.extend(
                Html("th", label, class_ = "Column" + colclass, inline = True)
                for (label, colclass) in  [
                    (_EVENT,          "Event"),
                    (DHEAD,           "Date"),
                    (PHEAD,          "Place"),
                    (DESCRHEAD, "Description"),
                    (NHEAD,         "Notes"),
                    (SHEAD,         "Sources") ]
                )
        return trow

    def format_event(self, eventlist):
        """
        displays the event row for events such as marriage and divorce
        """
        db = self.report.database

        # begin eventlist table and table header
        with Html("table", class_ = "infolist eventlist") as table:
            thead = Html("thead")
            table += thead

            # attach event header row
            thead += self.display_event_header()

            # begin table body
            tbody = Html("tbody")
            table += tbody 
   
            for event_ref in eventlist:
                event = db.get_event_from_handle(event_ref.ref)

                # add event body row
                """
                @param: event object
                @param: event_ref = event reference
                @param: up = True or False: attach subdirs or not?
                @param: hyp = show hyperlinked evt type or not?
                @params: omit = role to be omitted in output
                """
                tbody += self.display_event_row(event, event_ref, True, True,
                EventRoleType.FAMILY)

        # return table to its callers
        return table

class RepositoryListPage(BasePage):
    """
    Will create the repository list page
    """

    def __init__(self, report, title, repos_dict, keys):
        BasePage.__init__(self, report, title)
        db = report.database

        of = self.report.create_file("repositories")
        repolistpage, head, body = self.write_header(_("Repositories"))

        # begin RepositoryList division
        with Html("div", class_ = "content", id = "RepositoryList") as repositorylist:
            body += repositorylist

            msg = _("This page contains an index of all the repositories in the "
                          "database, sorted by their title. Clicking on a repositories&#8217;s "
                          "title will take you to that repositories&#8217;s page.")
            repositorylist += Html("p", msg, id = "description")

            # begin repositories table and table head
            with Html("table", class_ = "infolist repolist") as table:
                repositorylist += table 

                thead = Html("thead")
                table += thead

                trow = Html("tr") + (
                    Html("th", "&nbsp;", class_ = "ColumnRowLabel", inline = True),
                    Html("th", THEAD, class_ = "ColumnType", inline = True),
                    Html("th", _("Repository |Name"), class_ = "ColumnName", inline = True)
                    )
                thead += trow

                # begin table body
                tbody = Html("tbody")
                table += tbody 

                for index, key in enumerate(keys):
                    (repo, handle) = repos_dict[key]

                    trow = Html("tr")
                    tbody += trow

                    # index number
                    trow += Html("td", index + 1, class_ = "ColumnRowLabel", inline = True)

                    # repository type
                    rtype = str(repo.type)
                    trow += Html("td", rtype, class_ = "ColumnType", inline = True)

                    # repository name and hyperlink
                    if repo.name:
                        trow += Html("td", self.repository_link(handle, repo.name, repo.gramps_id), 
                            class_ = "ColumnName")
                    else:
                        trow += Html("td", "&nbsp;", class_ = "ColumnName")

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.XHTMLWriter(repolistpage, of)

class RepositoryPage(BasePage):
    """
    will create the individual Repository Pages
    """

    def __init__(self, report, title, repo, handle, gid = None):
        BasePage.__init__(self, report, title, gid)
        db = report.database

        of = self.report.create_file(handle, 'repo')
        self.up = True
        repositorypage, head, body = self.write_header(_('Repositories'))

        # begin RepositoryDetail division and page title
        with Html("div", class_ = "content", id = "RepositoryDetail") as repositorydetail:
            body += repositorydetail

            # repository name
            repositorydetail += Html("h3", repo.name, inline = True)

            # begin repository table
            with Html("table", class_ = "infolist repolist") as table:
                repositorydetail += table

                tbody = Html("tbody")
                table += tbody
 
                # GRAMPS ID
                if not self.noid and gid:
                    # repo gramps id
                    trow = Html("tr") + (
                        Html("td", GRAMPSID, class_ = "ColumnAttribute", inline = True),
                        Html("td", gid, class_ = "ColumnValue", inline = True)
                        )
                    tbody += trow

                # repository type
                trow = Html("tr") + (
                    Html("td", THEAD, class_ = "ColumnAttribute", inline = True),
                    Html("td", str(repo.type), class_ = "ColumnValue", inline = True)
                    )
                tbody += trow

            # repository: address(es)
            addresses = self.dump_addresses(repo.get_address_list(), False)
            if addresses is not None:
                repositorydetail += addresses

            # repository: urllist
            urllist = self.display_url_list(repo.get_url_list())
            if urllist is not None:
                repositorydetail += urllist

            # reposity: notelist
            notelist = self.display_note_list(repo.get_note_list()) 
            if notelist is not None:
                repositorydetail += notelist

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.XHTMLWriter(repositorypage, of)

class AddressBookListPage(BasePage):

    def __init__(self, report, title, has_url_address):
        """
        Create a list of individual's that have either internet addresses or 
        address/ Residence events

        @param: has_url_address -- a list of (sort_name, person_handle, has_add, has_rtes, and has_url
        """
        BasePage.__init__(self, report, title)
        db = report.database

        # Name the file, and create it
        of = self.report.create_file("addressbook")

        # Add xml, doctype, meta and stylesheets
        addressbooklistpage, head, body = self.write_header("%s - %s" % (title, _("Address Book")))

        # begin AddressBookList division
        with Html("div", class_ = "content", id = "AddressBookList") as addressbooklist:
            body += addressbooklist

            # Internet Address Book Page message
            msg = _("This page contains an index of all the individuals in the "
                "database, sorted by their surname, with one of the "
                "following: Address, Residence, or Web Links. Selecting the "
                "person&#8217;s name will take you to their Address "
                "Book&#8217;s individual page.")
            addressbooklist += Html("p", msg, id = "description")

            # begin Address Book table
            with Html("table", class_ = "infolist addressbook") as table:
                addressbooklist += table

                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                trow.extend(
                    Html("th", label, class_="Column" + colclass, inline=True)
                    for (label, colclass) in [
                        ["&nbsp;",       "RowLabel"],
                        [_("Name"),      "Name"],
                        [_("Address"),   "Address"],
                        [_("Residence"), "Residence"],
                        [_("Web Links"), "WebLinks"] ]
                        )

                tbody = Html("tbody")
                table += tbody

                index = 1
                for (sort_name, person_handle, has_add, has_res, has_url) in has_url_address:

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
                        Html("td", data or "&nbsp;", class_="Column" + colclass, inline = True)
                        for (colclass, data) in [
                            ["RowLabel",  index],
                            ["Name",      self.addressbook_link(person_handle)],
                            ["Address",   address],
                            ["Residence", residence],
                            ["WebLinks",  weblinks] ]
                            )
                    index += 1

        # Add footer and clearline
        footer = self.write_footer()
        body += (fullclear, footer)

        # send the page out for processing
        # and close the file
        self.XHTMLWriter(addressbooklistpage, of)

class AddressBookPage(BasePage):

    def __init__(self, report, title, person_handle, has_add, has_res, has_url):
        """
        Creates the individual address book pages

        @parm: title = title for this report
        @param: has_add -- a list of address handles or None
        @param: has_res -- a residence event or None
        @param: has_url -- list of url handles or None
        """
        db = report.database

        person = db.get_person_from_handle(person_handle)
        BasePage.__init__(self, report, title, person.gramps_id)
        self.up = True

        # set the file name and open file
        of = self.report.create_file(person_handle, "addr")
        addressbookpage, head, body = self.write_header("%s - %s" % (title, _("Address Book")))

        # begin address book page division and section title
        with Html("div", class_ = "content", id = "AddressBookDetail") as addressbookdetail:
            body += addressbookdetail
            addressbookdetail += Html("h3", self.get_name(person), inline = True)

            # individual has an address
            if has_add:
                addressbookdetail += self.display_addr_list(has_add, None)

            # individual has a residence
            if has_res:
                addressbookdetail += self.dump_residence(has_res)

            # individual has a url
            if has_url:
                addressbookdetail += self.display_url_list(has_url)

        # add fullclear for proper styling
        # and footer section to page
        footer = self.write_footer()
        body += (fullclear, footer)

        # send page out for processing
        # and close the file
        self.XHTMLWriter(addressbookpage, of)

class NavWebReport(Report):
    
    def __init__(self, database, options):
        """
        Create WebReport object that produces the report.

        The arguments are:

        database        - the GRAMPS database instance
        options         - instance of the Options class for this report
        """
        Report.__init__(self, database, options)
        menu = options.menu
        self.link_prefix_up = True
        self.options = {}

        for optname in menu.get_all_option_names():
            menuopt = menu.get_option_by_name(optname)
            self.options[optname] = menuopt.get_value()

        if not self.options['incpriv']:
            self.database = PrivateProxyDb(database)
        else:
            self.database = database

        livinginfo = self.options['living']
        yearsafterdeath = self.options['yearsafterdeath']

        if livinginfo != _INCLUDE_LIVING_VALUE:
            self.database = LivingProxyDb(self.database,
                                          livinginfo,
                                          None,
                                          yearsafterdeath)

        filters_option = menu.get_option_by_name('filter')
        self.filter = filters_option.get_filter()

        self.copyright = self.options['cright']
        self.target_path = self.options['target']
        self.ext = self.options['ext']
        self.css = self.options['css']
        self.navigation = self.options["navigation"]

        self.title = self.options['title']
        self.inc_gallery = self.options['gallery']
        self.inc_contact = self.options['contactnote'] or \
                           self.options['contactimg']

        # name format options
        self.name_format = self.options['name_format']

        # create an event pages or not?
        self.inc_events = self.options['inc_events']

        # include repository page or not?
        self.inc_repository = self.options['inc_repository']

        # include GENDEX page or not?
        self.inc_gendex = self.options['inc_gendex']

        # Download Options Tab
        self.inc_download = self.options['incdownload']
        self.dl_fname1 = self.options['down_fname1']
        self.dl_descr1 = self.options['dl_descr1']
        self.dl_fname2 = self.options['down_fname2']
        self.dl_descr2 = self.options['dl_descr2']
        self.dl_copy = self.options['dl_cright']

        self.encoding = self.options['encoding']

        self.use_archive = self.options['archive']
        self.use_intro = self.options['intronote'] or \
                         self.options['introimg']
        self.use_home = self.options['homenote'] or \
                        self.options['homeimg']
        self.use_contact = self.options['contactnote'] or \
                           self.options['contactimg']

        # either include the gender graphics or not?
        self.graph = self.options['graph']

        # whether to display children in birthorder or entry order?
        self.birthorder = self.options['birthorder']

        # get option for Internet Address Book
        self.inc_addressbook = self.options["inc_addressbook"]

        # Place Map tab options
        self.placemaps = self.options["placemaps"]

        if self.use_home:
            self.index_fname = "index"
            self.surname_fname = "surnames"
            self.intro_fname = "introduction"
        elif self.use_intro:
            self.index_fname = None
            self.surname_fname = "surnames"
            self.intro_fname = "index"
        else:
            self.index_fname = None
            self.surname_fname = "index"
            self.intro_fname = None

        self.archive = None
        self.cur_fname = None            # Internal use. The name of the output file, 
                                         # to be used for the tar archive.
        self.string_io = None
        if self.use_archive:
            self.html_dir = None
        else:
            self.html_dir = self.target_path
        self.warn_dir = True        # Only give warning once.
        self.photo_list = {}

    def write_report(self):
        _WRONGMEDIAPATH = []
        if not self.use_archive:
            dir_name = self.target_path
            if dir_name is None:
                dir_name = os.getcwd()
            elif not os.path.isdir(dir_name):
                parent_dir = os.path.dirname(dir_name)
                if not os.path.isdir(parent_dir):
                    ErrorDialog(_("Neither %s nor %s are directories") % \
                                (dir_name, parent_dir))
                    return
                else:
                    try:
                        os.mkdir(dir_name)
                    except IOError, value:
                        ErrorDialog(_("Could not create the directory: %s") % \
                                    dir_name + "\n" + value[1])
                        return
                    except:
                        ErrorDialog(_("Could not create the directory: %s") % \
                                    dir_name)
                        return

            try:
                image_dir_name = os.path.join(dir_name, 'images')
                if not os.path.isdir(image_dir_name):
                    os.mkdir(image_dir_name)

                image_dir_name = os.path.join(dir_name, 'thumb')
                if not os.path.isdir(image_dir_name):
                    os.mkdir(image_dir_name)
            except IOError, value:
                ErrorDialog(_("Could not create the directory: %s") % \
                            image_dir_name + "\n" + value[1])
                return
            except:
                ErrorDialog(_("Could not create the directory: %s") % \
                            image_dir_name)
                return
        else:
            if os.path.isdir(self.target_path):
                ErrorDialog(_('Invalid file name'),
                            _('The archive file must be a file, not a directory'))
                return
            try:
                self.archive = tarfile.open(self.target_path, "w:gz")
            except (OSError, IOError), value:
                ErrorDialog(_("Could not create %s") % self.target_path,
                            value)
                return

        self.progress = ProgressMeter(_("Narrated Web Site Report"), '')

        # Build the person list
        ind_list = self.build_person_list()

        # copy all of the neccessary files
        self.copy_narrated_files()

        place_list = {}
        source_list = {}
        attribute_list = []

        self.base_pages()

        # build classes IndividualListPage and IndividualPage
        self.person_pages(ind_list, place_list, source_list)

        # build classes SurnameListPage and SurnamePage
        self.surname_pages(ind_list)

        # build classes PlaceListPage and PlacePage
        self.place_pages(place_list, source_list)

        # build classes EventListPage and EventPage
        if self.inc_events:
            self.event_pages(ind_list)

        # build classes SourceListPage and SourcePage
        self.source_pages(source_list)

        # build classes MediaListPage and MediaPage
        if self.inc_gallery:
            self.gallery_pages(source_list)

        # Build classes source pages a second time to pick up sources referenced
        # by galleries
        self.source_pages(source_list)

        # build classes RepositoryListPage and RepositoryPage
        if self.inc_repository:
            repolist = self.database.get_repository_handles()
            if len(repolist):
                self.repository_pages(repolist)


        # build classes ddressBookList and AddressBookPage
        if self.inc_addressbook:
            self.addressbook_pages(ind_list)

        # if an archive is being used, close it?
        if self.archive:
            self.archive.close()
        
        if len(_WRONGMEDIAPATH) > 0:
            error = '\n'.join([_('ID=%(grampsid)s, path=%(dir)s') % {
                            'grampsid': x[0],
                            'dir': x[1]} for x in _WRONGMEDIAPATH[:10]])
            if len(_WRONGMEDIAPATH) > 10:
                error += '\n ...'
            WarningDialog(_("Missing media objects:"), error)
        self.progress.close()

    def build_person_list(self):
        """
        Builds the person list. Gets all the handles from the database
        and then applies the chosen filter:
        """

        # gets the person list and applies the requested filter
        self.person_handles = {}
        ind_list = self.database.iter_person_handles()
        self.progress.set_pass(_('Applying Filter...'), self.database.get_number_of_people())
        ind_list = self.filter.apply(self.database, ind_list, self.progress)
        for handle in ind_list:
            self.person_handles[handle] = True
        return ind_list

    def copy_narrated_files(self):
        """
        Copy all of the CSS, image, and javascript files for Narrated Web
        """

        # copy behaviour style sheet
        fname = os.path.join(const.DATA_DIR, "behaviour.css")
        self.copy_file(fname, "behaviour.css", "styles")

        # copy screen style sheet
        if self.css:
            fname = os.path.join(const.DATA_DIR, self.css)
            self.copy_file(fname, _NARRATIVESCREEN, "styles")

        # copy Navigation Menu Layout style sheet if Blue or Visually is being used
        if self.css == "Web_Basic-Blue.css" or "Web_Visually.css":
            if self.navigation == "Horizontal":
                fname = os.path.join(const.DATA_DIR, "Web_Navigation-Horizontal.css")
            else:
                fname = os.path.join(const.DATA_DIR, "Web_Navigation-Vertical.css")
            self.copy_file(fname, "Web_Navigation-Menus.css", "styles")

        # copy Mapstraction style sheet if using Place Maps
        if self.placemaps:
            fname = os.path.join(const.DATA_DIR, "Mapstraction.css")
            self.copy_file(fname, "mapstraction.css", "styles")
 
        # copy printer style sheet
        fname = os.path.join(const.DATA_DIR, "Web_Print-Default.css")
        self.copy_file(fname, _NARRATIVEPRINT, "styles")

        # copy mapstraction files to mapstraction directory
        # if PlacePage or IndividualPage maps will be used
        if self.placemaps:
            js_files = [ "mxn.core.js", "mxn.geocommons.core.js", "mxn.google.core.js",
                         "mxn.google.geocoder.js", "mxn.googlev3.core.js",
                         "mxn.js", "mxn.openlayers.core.js" ] 
            for fname in js_files:
                from_path = os.path.join(const.MAPSTRACTION_DIR, fname)
                self.copy_file(from_path, fname, "mapstraction")
            image_names = [ "gramps-geo-mainmap.png", "gramps-geo-altmap.png" ] 
            for image_name in image_names:
                fname = os.path.join(const.ROOT_DIR,
                                     'images', '22x22',
                                     '%s' % image_name )
                self.copy_file(fname, image_name, "images") 
 
        imgs = []

        # Mainz stylesheet graphics
        # will only be used if Mainz is slected as the stylesheet
        if self.css == "Web_Mainz.css":
            imgs += [ "Web_Mainz_Bkgd.png", "Web_Mainz_Header.png", 
                      "Web_Mainz_Mid.png", "Web_Mainz_MidLight.png" ]

        # Copy the Creative Commons icon if the Creative Commons
        # license is requested
        if 0 < self.copyright <= len(_CC):
            imgs += ["somerights20.gif"]

        # include GRAMPS favicon
        imgs += ["favicon2.ico"]

        # we need the blank image gif neede by behaviour.css
        imgs += ["blank.gif"]

        # add the document.png file for media other than photos
        imgs += ["document.png"]

        # copy Ancestor Tree graphics if needed???
        if self.graph:
            imgs += ["Web_Gender_Female.png",
                     "Web_Gender_Male.png" ]

        for fname in imgs:
            from_path = os.path.join(const.IMAGE_DIR, fname)
            self.copy_file(from_path, fname, "images")

    def build_attributes(self, person):
        """
        build a list of attributes for each person
        """

        # get personal attributes
        attribute_list = person.get_attribute_list()

        for family_handle in person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)

            # get family attributes
            attribute_list.extend(family.get_attribute_list() )

        # return attributes to its caller
        return attribute_list

    def person_pages(self, ind_list, place_list, source_list):
        """
        creates IndividualListPage, IndividualPage, and gendex page if requested
        """

        self.progress.set_pass(_('Creating individual pages'), len(ind_list) + 1)
        self.progress.step()    # otherwise the progress indicator sits at 100%
                                # for a short while from the last step we did,
                                # which was to apply the privacy filter

        IndividualListPage(self, self.title, ind_list)

        for person_handle in ind_list:
            self.progress.step()
            person = self.database.get_person_from_handle(person_handle)

            # get attributes for each person
            attribute_list = self.build_attributes(person)

            IndividualPage(self, self.title, person, ind_list, place_list, source_list, attribute_list)

        if self.inc_gendex:
            self.progress.set_pass(_('Creating GENDEX file'), len(ind_list))
            fp_gendex = self.create_file("gendex", ext=".txt")
            for person_handle in ind_list:
                self.progress.step()
                person = self.database.get_person_from_handle(person_handle)
                self.write_gendex(fp_gendex, person)
            self.close_file(fp_gendex)

    def write_gendex(self, fp, person):
        """
        Reference|SURNAME|given name /SURNAME/|date of birth|place of birth|date of death|
            place of death|
        * field 1: file name of web page referring to the individual
        * field 2: surname of the individual
        * field 3: full name of the individual
        * field 4: date of birth or christening (optional)
        * field 5: place of birth or christening (optional)
        * field 6: date of death or burial (optional)
        * field 7: place of death or burial (optional) 
        """
        url = self.build_url_fname_html(person.handle, "ppl")
        surname = person.get_primary_name().get_surname()
        fullname = person.get_primary_name().get_gedcom_name()

        # get birth info:
        dob, pob = get_gendex_data(self.database, person.get_birth_ref())

        # get death info:
        dod, pod = get_gendex_data(self.database, person.get_death_ref())
        fp.write(
            '|'.join((url, surname, fullname, dob, pob, dod, pod)) + '|\n')

    def surname_pages(self, ind_list):
        """
        Generates the surname related pages from list of individual
        people.
        """

        local_list = sort_people(self.database, ind_list)

        self.progress.set_pass(_("Creating surname pages"), len(local_list))

        SurnameListPage(self, self.title, ind_list, SurnameListPage.ORDER_BY_NAME,
            self.surname_fname)

        SurnameListPage(self, self.title, ind_list, SurnameListPage.ORDER_BY_COUNT,
            "surnames_count")

        for (surname, handle_list) in local_list:
            SurnamePage(self, self.title, surname, handle_list, ind_list)
            self.progress.step()

    def source_pages(self, source_list):
        """
        creates SourceListPage and SourcePage
        """

        self.progress.set_pass(_("Creating source pages"), len(source_list))

        SourceListPage(self, self.title, source_list.keys())

        for key in source_list:
            SourcePage(self, self.title, key, source_list)
            self.progress.step()

    def place_pages(self, place_list, source_list):
        """
        creates PlaceListPage and PlacePage
        """

        self.progress.set_pass(_("Creating place pages"), len(place_list))

        PlaceListPage(self, self.title, place_list, source_list)

        for place in place_list:
            PlacePage(self, self.title, place, source_list, place_list)
            self.progress.step()

    def event_pages(self, ind_list):
        """
        a dump of all the events sorted by event type, date, and surname
        for classes EventListPage and EventPage
        """
        db = self.database

        # set up progress bar for event pages; using ind list
        event_handle_list, event_types = build_event_data(db, ind_list)
        self.progress.set_pass(_("Creating event pages"), len(event_handle_list))

        # send all data to the events list page
        EventListPage(self, self.title, event_types, event_handle_list)

        for event_handle in event_handle_list:

            # create individual event pages
            EventPage(self, self.title, event_handle)

            self.progress.step()

    def gallery_pages(self, source_list):
        """
        creates MediaListPage and MediaPage
        """

        self.progress.set_pass(_("Creating media pages"), len(self.photo_list))

        MediaListPage(self, self.title)

        prev = None
        total = len(self.photo_list)
        sort = Sort.Sort(self.database)
        photo_keys = sorted(self.photo_list, key=sort.by_media_title_key)

        index = 1
        for photo_handle in photo_keys:
            gc.collect() # Reduce memory usage when there are many images.
            next = None if index == total else photo_keys[index]
            # Notice. Here self.photo_list[photo_handle] is used not self.photo_list
            MediaPage(self, self.title, photo_handle, source_list, self.photo_list[photo_handle],
                      (prev, next, index, total))
            self.progress.step()
            prev = photo_handle
            index += 1

    def base_pages(self):
        """
        creates HomePage, ContactPage, DownloadPage, and IntroductionPage
        if requested by options in plugin
        """

        if self.use_home:
            HomePage(self, self.title)

        if self.inc_contact:
            ContactPage(self, self.title)

        if self.inc_download:
            DownloadPage(self, self.title)

        if self.use_intro:
            IntroductionPage(self, self.title)

    def repository_pages(self, repolist):
        """
        will create RepositoryPage() and RepositoryListPage()
        """

        repos_dict = {}

        # Sort the repositories
        for handle in repolist:
            repo = self.database.get_repository_from_handle(handle)
            key = repo.name + str(repo.get_gramps_id())
            repos_dict[key] = (repo, handle)
            
        keys = sorted(repos_dict, key = locale.strxfrm)

        # set progress bar pass for Repositories
        repo_size = len(repos_dict)
        self.progress.set_pass(_('Creating repository pages'), repo_size)

        # RepositoryListPage Class
        RepositoryListPage(self, self.title, repos_dict, keys)

        for index, key in enumerate(keys):
            (repo, handle) = repos_dict[key]

            # RepositoryPage Class
            RepositoryPage(self, self.title, repo, handle, repo.gramps_id)

            # increment progress bar 
            self.progress.step()

    def addressbook_pages(self, ind_list):
        """
        Creates classes AddressBookListPage and AddressBookPage
        """

        has_url_address = []

        for person_handle in ind_list:

            person = self.database.get_person_from_handle(person_handle)
            addrlist = person.get_address_list()
            evt_ref_list = person.get_event_ref_list()
            urllist = person.get_url_list()

            has_add = None
            has_url = None
            has_res = None

            if addrlist:
                has_add = addrlist
            if urllist:
                has_url = urllist

            for event_ref in evt_ref_list:
                event = self.database.get_event_from_handle(event_ref.ref)

                # get event type
                evt_type = str(event.get_type() )
                if evt_type == "Residence":
                    has_res = event
                    break

            if has_add or has_res or has_url:
                primary_name = person.get_primary_name()
                sort_name = ''.join([primary_name.get_surname(), ", ", primary_name.get_first_name()])

                data = (sort_name, person_handle, has_add, has_res, has_url)
                has_url_address.append(data)

        AddressBookListPage(self, self.title, has_url_address)
        # Determine if we build Address Book
        if has_url_address:
            has_url_address.sort()

            addr_size = len(has_url_address) 
            # begin Address Book pages 
            self.progress.set_pass(_("Creating address book pages ..."), addr_size)

            for (sort_name, person_handle, has_add, has_res, has_url) in has_url_address:

                AddressBookPage(self, self.title, person_handle, has_add, has_res, has_url)

                # increment progress bar
                self.progress.step()

    def build_subdirs(self, subdir, fname, up = False):
        """
        If subdir is given, then two extra levels of subdirectory are inserted
        between 'subdir' and the filename. The reason is to prevent directories with
        too many entries.

        For example, this may return "8/1/aec934857df74d36618"

        *** up = None = [./] for use in EventListPage
        """
        subdirs = []
        if subdir:
            subdirs.append(subdir)
            subdirs.append(fname[-1].lower())
            subdirs.append(fname[-2].lower())

        if up == True:
            subdirs = ['..']*3 + subdirs

        # added for use in EventListPage
        elif up is None:
            subdirs = ['.'] + subdirs
        return subdirs

    def build_path(self, subdir, fname, up = False):
        """
        Return the name of the subdirectory.

        Notice that we DO use os.path.join() here.
        """
        return os.path.join(*self.build_subdirs(subdir, fname, up))

    def build_url_image(self, fname, subdir = None, up = False):
        """
        builds a url from an image
        """

        subdirs = []
        if subdir:
            subdirs.append(subdir)
        if up:
            subdirs = ['..']*3 + subdirs
        nname = "/".join(subdirs + [fname])
        if constfunc.win():
            nname = nname.replace('\\',"/")
        return nname

    def build_url_fname_html(self, fname, subdir = None, up = False):
        """
        builds a url filename from html
        """

        return self.build_url_fname(fname, subdir, up) + self.ext

    def build_link(self, prop, handle, obj_class):
        """
        Build a link to an item.
        """
        if prop == "gramps_id":
            if obj_class in self.database.get_table_names():
                obj = self.database.get_table_metadata(obj_class)["gramps_id_func"](handle)
                if obj:
                    handle = obj.handle
                else:
                    raise AttributeError("gramps_id '%s' not found in '%s'" % 
                                         handle, obj_class)
            else:
                raise AttributeError("invalid gramps_id lookup " 
                                     "in table name '%s'" % obj_class)
        up = self.link_prefix_up 
        # handle, ppl
        if obj_class == "Person":
            if handle in self.person_handles:
                return self.build_url_fname(handle, "ppl", up) + self.ext
            else:
                return None
        elif obj_class == "Source":
            subdir = "src"
        elif obj_class == "Place":
            subdir = "plc"
        elif obj_class == "Event":
            subdir = "evt"
        elif obj_class == "Media":
            subdir = "img"
        elif obj_class == "Repository":
            subdir = "repo"
        else:
            raise AttributeError("unknown object type '%s'" % obj_class)
        return self.build_url_fname(handle, subdir, up) + self.ext

    def build_url_fname(self, fname, subdir = None, up = False):
        """
        Create part of the URL given the filename and optionally the subdirectory.
        If the subdirectory is given, then two extra levels of subdirectory are inserted
        between 'subdir' and the filename. The reason is to prevent directories with
        too many entries.
        If 'up' is True, then "../../../" is inserted in front of the result. 

        The extension is added to the filename as well.

        Notice that we do NOT use os.path.join() because we're creating a URL.
        Imagine we run gramps on Windows (heaven forbits), we don't want to
        see backslashes in the URL.
        """
        if constfunc.win():
            fname = fname.replace('\\',"/")
        subdirs = self.build_subdirs(subdir, fname, up)
        return "/".join(subdirs + [fname])

    def create_file(self, fname, subdir = None, ext = None):
        """
        will create filename given

        @param: fname -- file name to be created
        @param: subdir -- a subdir to be added to filename
        @param: ext -- an extension to be added to filename
        """

        if ext is None:
            ext = self.ext
        if subdir:
            subdir = self.build_path(subdir, fname)
            self.cur_fname = os.path.join(subdir, fname) + ext
        else:
            self.cur_fname = fname + ext
        if self.archive:
            self.string_io = StringIO()
            of = codecs.EncodedFile(self.string_io, 'utf-8',
                                    self.encoding, 'xmlcharrefreplace')
        else:
            if subdir:
                subdir = os.path.join(self.html_dir, subdir)
                if not os.path.isdir(subdir):
                    os.makedirs(subdir)
            fname = os.path.join(self.html_dir, self.cur_fname)
            of = codecs.EncodedFile(open(fname, "w"), 'utf-8',
                                    self.encoding, 'xmlcharrefreplace')
        return of

    def close_file(self, of):
        """
        will close any file passed to it
        """

        if self.archive:
            tarinfo = tarfile.TarInfo(self.cur_fname)
            tarinfo.size = len(self.string_io.getvalue())
            tarinfo.mtime = time.time()
            if not constfunc.win():
                tarinfo.uid = os.getuid()
                tarinfo.gid = os.getgid()
            self.string_io.seek(0)
            self.archive.addfile(tarinfo, self.string_io)
            self.string_io = None
            of.close()
        else:
            of.close()
        self.cur_fname = None

    def add_lnkref_to_photo(self, photo, lnkref):
        """
        adds link reference to media object
        """

        handle = photo.get_handle()
        # FIXME. Is it OK to add to the photo_list of report?
        photo_list = self.photo_list
        if handle in photo_list:
            if lnkref not in photo_list[handle]:
                photo_list[handle].append(lnkref)
        else:
            photo_list[handle] = [lnkref]

    def prepare_copy_media(self, photo):
        """
        prepares a media object to copy
        """

        handle = photo.get_handle()
        ext = os.path.splitext(photo.get_path())[1]
        real_path = os.path.join(self.build_path('images', handle), handle + ext)
        thumb_path = os.path.join(self.build_path('thumb', handle), handle + '.png')
        return real_path, thumb_path

    def copy_file(self, from_fname, to_fname, to_dir=''):
        """
        Copy a file from a source to a (report) destination.
        If to_dir is not present and if the target is not an archive,
        then the destination directory will be created.

        Normally 'to_fname' will be just a filename, without directory path.

        'to_dir' is the relative path name in the destination root. It will
        be prepended before 'to_fname'.
        """
        if self.archive:
            dest = os.path.join(to_dir, to_fname)
            self.archive.add(from_fname, dest)
        else:
            dest = os.path.join(self.html_dir, to_dir, to_fname)

            destdir = os.path.dirname(dest)
            if not os.path.isdir(destdir):
                os.makedirs(destdir)

            if from_fname != dest:
                try:
                    shutil.copyfile(from_fname, dest)
                except:
                    print("Copying error: %s" % sys.exc_info()[1])
                    print("Continuing...")
            elif self.warn_dir:
                WarningDialog(
                    _("Possible destination error") + "\n" +
                    _("You appear to have set your target directory "
                      "to a directory used for data storage. This "
                      "could create problems with file management. "
                      "It is recommended that you consider using "
                      "a different directory to store your generated "
                      "web pages."))
                self.warn_dir = False

class NavWebOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dbase):
        self.__db = dbase
        self.__archive = None
        self.__target = None
        self.__pid = None
        self.__filter = None
        self.__graph = None
        self.__graphgens = None
        self.__living = None
        self.__yearsafterdeath = None
        MenuReportOptions.__init__(self, name, dbase)

    def add_menu_options(self, menu):
        """
        Add options to the menu for the web site.
        """
        self.__add_report_options(menu)
        self.__add_page_generation_options(menu)
        self.__add_privacy_options(menu)
        self.__add_download_options(menu) 
        self.__add_advanced_options(menu)

    def __add_report_options(self, menu):
        """
        Options on the "Report Options" tab.
        """
        category_name = _("Report Options")

        self.__archive = BooleanOption(_('Store web pages in .tar.gz archive'),
                                       False)
        self.__archive.set_help(_('Whether to store the web pages in an '
                                  'archive file'))
        menu.add_option(category_name, 'archive', self.__archive)
        self.__archive.connect('value-changed', self.__archive_changed)

        self.__target = DestinationOption(_("Destination"),
                                    os.path.join(const.USER_HOME, "NAVWEB"))
        self.__target.set_help( _("The destination directory for the web "
                                  "files"))
        menu.add_option(category_name, "target", self.__target)

        self.__archive_changed()

        title = StringOption(_("Web site title"), _('My Family Tree'))
        title.set_help(_("The title of the web site"))
        menu.add_option(category_name, "title", title)

        self.__filter = FilterOption(_("Filter"), 0)
        self.__filter.set_help(
               _("Select filter to restrict people that appear on web site"))
        menu.add_option(category_name, "filter", self.__filter)
        self.__filter.connect('value-changed', self.__filter_changed)

        self.__pid = PersonOption(_("Filter Person"))
        self.__pid.set_help(_("The center person for the filter"))
        menu.add_option(category_name, "pid", self.__pid)
        self.__pid.connect('value-changed', self.__update_filters)

        self.__update_filters()

        # We must figure out the value of the first option before we can
        # create the EnumeratedListOption
        fmt_list = _nd.get_name_format()
        name_format = EnumeratedListOption(_("Name format"), fmt_list[0][0])
        for num, name, fmt_str, act in fmt_list:
            name_format.add_item(num, name)
        name_format.set_help(_("Select the format to display names"))
        menu.add_option(category_name, "name_format", name_format)

        ext = EnumeratedListOption(_("File extension"), ".html" )
        for etype in _WEB_EXT:
            ext.add_item(etype, etype)
        ext.set_help( _("The extension to be used for the web files"))
        menu.add_option(category_name, "ext", ext)

        cright = EnumeratedListOption(_('Copyright'), 0 )
        for index, copt in enumerate(_COPY_OPTIONS):
            cright.add_item(index, copt)
        cright.set_help( _("The copyright to be used for the web files"))
        menu.add_option(category_name, "cright", cright)

        self.__css = EnumeratedListOption(_('StyleSheet'), CSS_FILES[0][1])
        for style in CSS_FILES:
            self.__css.add_item(style[1], style[0])
        self.__css.set_help( _('The stylesheet to be used for the web pages'))
        menu.add_option(category_name, "css", self.__css)
        self.__css.connect("value-changed", self.__stylesheet_changed)

        _nav_opts = [
            [_("Horizontal -- No Change"), "Horizontal"],
            [_("Vertical"),                "Vertical"]
            ]
        self.__navigation = EnumeratedListOption(_("Navigation Layout"), _nav_opts[0][1])
        for layout in _nav_opts:
            self.__navigation.add_item(layout[1], layout[0])
        self.__navigation.set_help(_("Choose which layout for the Navigation Menus."))
        menu.add_option(category_name, "navigation", self.__navigation)

        self.__stylesheet_changed()

        self.__graph = BooleanOption(_("Include ancestor graph"), True)
        self.__graph.set_help(_('Whether to include an ancestor graph '
                                      'on each individual page'))
        menu.add_option(category_name, 'graph', self.__graph)
        self.__graph.connect('value-changed', self.__graph_changed)

        self.__graphgens = NumberOption(_("Graph generations"), 4, 2, 5)
        self.__graphgens.set_help( _("The number of generations to include in "
                                     "the ancestor graph"))
        menu.add_option(category_name, "graphgens", self.__graphgens)

        self.__graph_changed()

    def __add_page_generation_options(self, menu):
        """
        Options on the "Page Generation" tab.
        """
        category_name = _("Page Generation")

        homenote = NoteOption(_('Home page note'))
        homenote.set_help( _("A note to be used on the home page"))
        menu.add_option(category_name, "homenote", homenote)

        homeimg = MediaOption(_('Home page image'))
        homeimg.set_help( _("An image to be used on the home page"))
        menu.add_option(category_name, "homeimg", homeimg)

        intronote = NoteOption(_('Introduction note'))
        intronote.set_help( _("A note to be used as the introduction"))
        menu.add_option(category_name, "intronote", intronote)

        introimg = MediaOption(_('Introduction image'))
        introimg.set_help( _("An image to be used as the introduction"))
        menu.add_option(category_name, "introimg", introimg)

        contactnote = NoteOption(_("Publisher contact note"))
        contactnote.set_help( _("A note to be used as the publisher contact."+
                                "\nIf no publisher information is given," +
                                "\nno contact page will be created")
                              )
        menu.add_option(category_name, "contactnote", contactnote)

        contactimg = MediaOption(_("Publisher contact image"))
        contactimg.set_help( _("An image to be used as the publisher contact." +
                               "\nIf no publisher information is given," +
                               "\nno contact page will be created")
                             )
        menu.add_option(category_name, "contactimg", contactimg)

        headernote = NoteOption(_('HTML user header'))
        headernote.set_help( _("A note to be used as the page header"))
        menu.add_option(category_name, "headernote", headernote)

        footernote = NoteOption(_('HTML user footer'))
        footernote.set_help( _("A note to be used as the page footer"))
        menu.add_option(category_name, "footernote", footernote)

        self.__gallery = BooleanOption(_("Include images and media objects"), True)
        self.__gallery.set_help(_('Whether to include a gallery of media objects'))
        menu.add_option(category_name, 'gallery', self.__gallery)
        self.__gallery.connect('value-changed', self.__gallery_changed)

        self.__maxinitialimagewidth = NumberOption(_("Max width of initial image"), 
            _DEFAULT_MAX_IMG_WIDTH, 0, 2000)
        self.__maxinitialimagewidth.set_help(_("This allows you to set the maximum width "
                              "of the image shown on the media page. Set to 0 for no limit."))
        menu.add_option(category_name, 'maxinitialimagewidth', self.__maxinitialimagewidth)

        self.__maxinitialimageheight = NumberOption(_("Max height of initial image"), 
            _DEFAULT_MAX_IMG_HEIGHT, 0, 2000)
        self.__maxinitialimageheight.set_help(_("This allows you to set the maximum height "
                              "of the image shown on the media page. Set to 0 for no limit."))
        menu.add_option(category_name, 'maxinitialimageheight', self.__maxinitialimageheight)

        self.__gallery_changed()

        nogid = BooleanOption(_('Suppress Gramps ID'), False)
        nogid.set_help(_('Whether to include the Gramps ID of objects'))
        menu.add_option(category_name, 'nogid', nogid)

    def __add_privacy_options(self, menu):
        """
        Options on the "Privacy" tab.
        """
        category_name = _("Privacy")

        incpriv = BooleanOption(_("Include records marked private"), False)
        incpriv.set_help(_('Whether to include private objects'))
        menu.add_option(category_name, 'incpriv', incpriv)

        self.__living = EnumeratedListOption(_("Living People"),
                                             _INCLUDE_LIVING_VALUE )
        self.__living.add_item(LivingProxyDb.MODE_EXCLUDE_ALL, 
                               _("Exclude"))
        self.__living.add_item(LivingProxyDb.MODE_INCLUDE_LAST_NAME_ONLY, 
                               _("Include Last Name Only"))
        self.__living.add_item(LivingProxyDb.MODE_INCLUDE_FULL_NAME_ONLY, 
                               _("Include Full Name Only"))
        self.__living.add_item(_INCLUDE_LIVING_VALUE, 
                               _("Include"))
        self.__living.set_help(_("How to handle living people"))
        menu.add_option(category_name, "living", self.__living)
        self.__living.connect('value-changed', self.__living_changed)

        self.__yearsafterdeath = NumberOption(_("Years from death to consider "
                                                 "living"), 30, 0, 100)
        self.__yearsafterdeath.set_help(_("This allows you to restrict "
                                          "information on people who have not "
                                          "been dead for very long"))
        menu.add_option(category_name, 'yearsafterdeath',
                        self.__yearsafterdeath)

        self.__living_changed()

    def __add_download_options(self, menu):
        """
        Options for the download tab ...
        """

        category_name = _("Download")

        self.__incdownload = BooleanOption(_("Include download page"), False)
        self.__incdownload.set_help(_('Whether to include a database download option'))
        menu.add_option(category_name, 'incdownload', self.__incdownload)
        self.__incdownload.connect('value-changed', self.__download_changed)

        self.__down_fname1 = DestinationOption(_("Download Filename"),
            os.path.join(const.USER_HOME, ""))
        self.__down_fname1.set_help(_("File to be used for downloading of database"))
        menu.add_option(category_name, "down_fname1", self.__down_fname1)

        self.__dl_descr1 = StringOption(_("Description for download"), _('Smith Family Tree'))
        self.__dl_descr1.set_help(_('Give a description for this file.'))
        menu.add_option(category_name, 'dl_descr1', self.__dl_descr1)

        self.__down_fname2 = DestinationOption(_("Download Filename"),
            os.path.join(const.USER_HOME, ""))
        self.__down_fname2.set_help(_("File to be used for downloading of database"))
        menu.add_option(category_name, "down_fname2", self.__down_fname2)

        self.__dl_descr2 = StringOption(_("Description for download"), _('Johnson Family Tree'))
        self.__dl_descr2.set_help(_('Give a description for this file.'))
        menu.add_option(category_name, 'dl_descr2', self.__dl_descr2)

        self.__dl_cright = EnumeratedListOption(_('Download Copyright License'), 0 )
        for index, copt in enumerate(_COPY_OPTIONS):
            self.__dl_cright.add_item(index, copt)
        self.__dl_cright.set_help( _("The copyright to be used for this download file?"))
        menu.add_option(category_name, "dl_cright", self.__dl_cright)

        self.__download_changed()

    def __add_advanced_options(self, menu):
        """
        Options on the "Advanced" tab.
        """
        category_name = _("Advanced Options")

        encoding = EnumeratedListOption(_('Character set encoding'), _CHARACTER_SETS[0][1] )
        for eopt in _CHARACTER_SETS:
            encoding.add_item(eopt[1], eopt[0])
        encoding.set_help( _("The encoding to be used for the web files"))
        menu.add_option(category_name, "encoding", encoding)

        linkhome = BooleanOption(_('Include link to active person on every page'), False)
        linkhome.set_help(_('Include a link to the active person (if they have a webpage)'))
        menu.add_option(category_name, 'linkhome', linkhome)

        showbirth = BooleanOption(_("Include a column for birth dates on the index pages"), True)
        showbirth.set_help(_('Whether to include a birth column'))
        menu.add_option(category_name, 'showbirth', showbirth)

        showdeath = BooleanOption(_("Include a column for death dates on the index pages"), False)
        showdeath.set_help(_('Whether to include a death column'))
        menu.add_option(category_name, 'showdeath', showdeath)

        showpartner = BooleanOption(_("Include a column for partners on the "
                                    "index pages"), False)
        showpartner.set_help(_('Whether to include a partners column'))
        menu.add_option(category_name, 'showpartner', showpartner)

        showparents = BooleanOption(_("Include a column for parents on the "
                                      "index pages"), False)
        showparents.set_help(_('Whether to include a parents column'))
        menu.add_option(category_name, 'showparents', showparents)

        # This is programmed wrong, remove
        #showallsiblings = BooleanOption(_("Include half and/ or "
        #                                   "step-siblings on the individual pages"), False)
        #showallsiblings.set_help(_( "Whether to include half and/ or "
        #                            "step-siblings with the parents and siblings"))
        #menu.add_option(category_name, 'showhalfsiblings', showallsiblings)

        birthorder = BooleanOption(_('Sort all children in birth order'), False)
        birthorder.set_help(_('Whether to display children in birth order or in entry order?'))
        menu.add_option(category_name, 'birthorder', birthorder)

        inc_events = BooleanOption(_('Include event pages'), False)
        inc_events.set_help(_('Add a complete events list and relevant pages or not'))
        menu.add_option(category_name, 'inc_events', inc_events)

        inc_repository = BooleanOption(_('Include repository pages'), False)
        inc_repository.set_help(_('Whether to include the Repository Pages or not?'))
        menu.add_option(category_name, 'inc_repository', inc_repository)

        inc_gendex = BooleanOption(_('Include GENDEX file (/gendex.txt)'), False)
        inc_gendex.set_help(_('Whether to include a GENDEX file or not'))
        menu.add_option(category_name, 'inc_gendex', inc_gendex)

        inc_addressbook = BooleanOption(_("Include address book pages"), False)
        inc_addressbook.set_help(_("Whether to add Address Book pages or not "
                                   "which can include e-mail and website "
                                   "addresses and personal address/ residence "
                                   "events?"))
        menu.add_option(category_name, "inc_addressbook", inc_addressbook)

        placemaps = BooleanOption(_("Include Place map on Place Pages"), False)
        placemaps.set_help(_("Whether to include a place map on the Place Pages, "
                             "where Latitude/ Longitude are available."))
        menu.add_option(category_name, "placemaps", placemaps)

    def __archive_changed(self):
        """
        Update the change of storage: archive or directory
        """
        if self.__archive.get_value() == True:
            self.__target.set_extension(".tar.gz")
            self.__target.set_directory_entry(False)
        else:
            self.__target.set_directory_entry(True)

    def __update_filters(self):
        """
        Update the filter list based on the selected person
        """
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        filter_list = ReportUtils.get_person_filters(person, False)
        self.__filter.set_filters(filter_list)

    def __filter_changed(self):
        """
        Handle filter change. If the filter is not specific to a person,
        disable the person option
        """
        filter_value = self.__filter.get_value()
        if filter_value in [1, 2, 3, 4]:
            # Filters 1, 2, 3 and 4 rely on the center person
            self.__pid.set_available(True)
        else:
            # The rest don't
            self.__pid.set_available(False)

    def __stylesheet_changed(self):
        """
        Handles the changing nature of the stylesheet
        """

        css_opts = self.__css.get_value()
        if css_opts in ["Web_Basic-Blue.css", "Web_Visually.css"]:   
            self.__navigation.set_available(True)
        else:
            self.__navigation.set_available(False)

    def __graph_changed(self):
        """
        Handle enabling or disabling the ancestor graph
        """
        self.__graphgens.set_available(self.__graph.get_value())

    def __gallery_changed(self):
        """
        Handles the changing nature of gallery
        """

        if self.__gallery.get_value() == False:
            self.__maxinitialimagewidth.set_available(False)
            self.__maxinitialimageheight.set_available(False)
        else:
            self.__maxinitialimagewidth.set_available(True)
            self.__maxinitialimageheight.set_available(True)

    def __living_changed(self):
        """
        Handle a change in the living option
        """
        if self.__living.get_value() == _INCLUDE_LIVING_VALUE:
            self.__yearsafterdeath.set_available(False)
        else:
            self.__yearsafterdeath.set_available(True)

    def __download_changed(self):
        """
        Handles the changing nature of include download page
        """

        if self.__incdownload.get_value():
            self.__down_fname1.set_available(True)
            self.__dl_descr1.set_available(True)
            self.__down_fname2.set_available(True)
            self.__dl_descr2.set_available(True)
            self.__dl_cright.set_available(True)
        else:
            self.__down_fname1.set_available(False)
            self.__dl_descr1.set_available(False)
            self.__down_fname2.set_available(False)
            self.__dl_descr2.set_available(False)
            self.__dl_cright.set_available(False)

# FIXME. Why do we need our own sorting? Why not use Sort.Sort?
def sort_people(db, handle_list):
    sname_sub = defaultdict(list)
    sortnames = {}

    for person_handle in handle_list:
        person = db.get_person_from_handle(person_handle)
        primary_name = person.get_primary_name()

        if primary_name.group_as:
            surname = primary_name.group_as
        else:
            surname = db.get_name_group_mapping(primary_name.surname)

        sortnames[person_handle] = _nd.sort_string(primary_name)
        sname_sub[surname].append(person_handle)

    sorted_lists = []
    temp_list = sorted(sname_sub, key=locale.strxfrm)
    
    for name in temp_list:
        slist = sorted(((sortnames[x], x) for x in sname_sub[name]), 
                    key=lambda x:locale.strxfrm(x[0]))
        entries = [x[1] for x in slist]
        sorted_lists.append((name, entries))

    return sorted_lists

def sort_event_types(db, event_types, event_handle_list):
    """
    sort a list of event types and their associated event handles

    @param: event_types -- a dict of event types
    @param: event_handle_list -- all event handles in this database
    """

    event_dict = dict( (evt_type, []) for evt_type in event_types)

    for handle in event_handle_list:

        event = db.get_event_from_handle(handle)
        etype = str(event.type)

        # add (gramps_id, date, handle) from this event
        if etype in event_dict:
            event_dict[etype].append( handle )

    for tup_list in event_dict.values():
        tup_list.sort()

    # return a list of sorted tuples, one per event
    retval = [(event_type, event_list) for (event_type, event_list) in event_dict.iteritems()]
    retval.sort(key=lambda item: str(item[0]))
    return retval

# Modified _get_regular_surname from WebCal.py to get prefix, first name, and suffix
def _get_short_name(gender, name):
    """ Will get prefix and suffix for all people passed through it """

    short_name = name.get_first_name()
    prefix = name.get_surname_prefix()
    if prefix:
        short_name = prefix + " " + short_name
    if gender == gen.lib.Person.FEMALE:
        return short_name
    else: 
        suffix = name.get_suffix()
        if suffix:
            short_name = short_name + ", " + suffix
    return short_name

def __get_person_keyname(db, handle):
    """ .... """
    person = db.get_person_from_handle(handle)
    return person.get_primary_name().get_surname()

def __get_place_keyname(db, handle):
    """ ... """

    return ReportUtils.place_name(db, handle)  

def first_letter(string):
    """
    recieves a string and returns the first letter
    """

    if string:
        letter = normalize('NFKC', unicode(string))[0].upper()
    else:
        letter = u' '
    # See : http://www.gramps-project.org/bugs/view.php?id = 2933
    (lang_country, modifier ) = locale.getlocale()
    if lang_country == "sv_SE" and (letter == u'W' or letter == u'V'):
        letter = u'V,W'
    return letter

def get_first_letters(db, menu_set, key):
    """
    get the first letters of the menu_set

    @param: db = report database
    @param: menu_set = one of a handle list for either person or place handles 
        or an evt types list
    @param: key = either a person, place, or event type
    """
 
    first_letters = []

    for menu_item in menu_set:

        if key == _KEYPERSON:
            keyname = __get_person_keyname(db, menu_item)

        elif key == _KEYPLACE:
            keyname = __get_place_keyname(db, menu_item)

        else:
            keyname = menu_item
        ltr = first_letter(keyname)


        if ltr not in [",", " "]:
            first_letters.append(ltr)

    # return menu set letters for alphabet_navigation
    return first_letters

def alphabet_navigation(menu_set):
    """
    Will create the alphabet navigation bar for classes IndividualListPage,
    SurnameListPage, PlaceListPage, and EventList

    @param: menu_set -- a dictionary of either letters or words
    """
    sorted_set = defaultdict(int)
    # The comment below from the glibc locale sv_SE in
    # localedata/locales/sv_SE :
    #
    # % The letter w is normally not present in the Swedish alphabet. It
    # % exists in some names in Swedish and foreign words, but is accounted
    # % for as a variant of 'v'.  Words and names with 'w' are in Swedish
    # % ordered alphabetically among the words and names with 'v'. If two
    # % words or names are only to be distinguished by 'v' or % 'w', 'v' is
    # % placed before 'w'.
    #
    # See : http://www.gramps-project.org/bugs/view.php?id = 2933
    #
    (lang_country, modifier ) = locale.getlocale()

    for menu_item in menu_set:
        sorted_set[menu_item] += 1

    # remove the number of each occurance of each letter
    sorted_alpha_index = sorted(sorted_set, key = locale.strxfrm)

    # if no letters, return None to its callers
    if not sorted_alpha_index:
        return None, []

    num_ltrs = len(sorted_alpha_index)
    num_of_cols = 32
    num_of_rows = ((num_ltrs // num_of_cols) + 1)

    # begin alphabet navigation division
    with Html("div", id = "alphabet") as alphabetnavigation:

        index = 0
        for row in xrange(num_of_rows):
            unordered = Html("ul") 
            alphabetnavigation += unordered

            cols = 0
            while (cols <= num_of_cols and index < num_ltrs):
                li = Html("li", inline = True)
                unordered += li

                menu_item = sorted_alpha_index[index]

                # adding title to hyperlink menu for screen readers and braille writers
                title_str = _("Alphabet Navigation Menu Item " + menu_item)

                if lang_country == "sv_SE" and menu_item == u'V':
                    hyper = Html("a", "V,W", href = "#V,W", alt = "V,W")
                else:
                    hyper = Html("a", menu_item, href = "#%s" % menu_item, alt = menu_item)
                hyper.attr += ' title = "%s"' % title_str
                li += hyper

                # increase letter/ word in sorted_alpha_index
                index += 1
                cols += 1
            num_of_rows -= 1

    # return alphabet navigation, and menu_set to its callers
    # EventListPage will reuse sorted_alpha_index
    return alphabetnavigation, sorted_alpha_index

def _has_webpage_extension(url):
    """
    determine if a filename has an extension or not...

    url = filename to be checked
    """
    return any(url.endswith(ext) for ext in _WEB_EXT) 

def add_birthdate(db, childlist):
    """
    This will sort a list of child handles in birth order
    """

    sorted_children = []
    for child_handle in childlist:
        child = db.get_person_from_handle(child_handle)

        # get birth date: if birth_date equals nothing, then generate a fake one?
        birth_ref = child.get_birth_ref()
        if birth_ref:
            birth = db.get_event_from_handle(birth_ref.ref)
            if birth:
                birth_date = birth.get_date_object()
        else:
            birth_date = gen.lib.Date(2199, 12, 31)
        sorted_children.append((birth_date, child_handle))

    # return the list of child handles and their birthdates
    return sorted_children

def _find_birth_date(db, person):
    """
    will look for a birth date within the person's events
    """

    birth_ref = person.get_birth_ref()
    if birth_ref:
        birth = db.get_event_from_handle(birth_ref.ref)
        return birth.get_date_object()
    else:
        event_list = person.get_primary_event_ref_list()
        for event_ref in event_list:
            event = db.get_event_from_handle(event_ref.ref)
            if event.get_type().is_birth_fallback():
                return event.get_date_object()
    return None

def _find_death_date(db, person):
    """
    will look for a death date within a person's events
    """

    death_ref = person.get_death_ref()
    if death_ref:
        death = db.get_event_from_handle(death_ref.ref)
        if death:
            return death.get_date_object()
    else:
        event_list = person.get_primary_event_ref_list()
        for event_ref in event_list:
            event = db.get_event_from_handle(event_ref.ref)
            if event.get_type().is_death_fallback():
                return event.get_date_object()
    return None

def build_event_data(db, ind_list):
    """
    creates a list of event handles and event types for this database
    """

    event_handle_list = []
    event_types = []

    for person_handle in ind_list:
        person = db.get_person_from_handle(person_handle)

        for evt_ref in person.get_event_ref_list():
            event = db.get_event_from_handle(evt_ref.ref)
            event_types.append( str(event.type) ) 
            event_handle_list.append(evt_ref.ref)

        for fhandle in person.get_family_handle_list():
            family = db.get_family_from_handle(fhandle)

            for evt_ref in family.get_event_ref_list():
                event = db.get_event_from_handle(evt_ref.ref)
                event_types.append( str(event.type) )
                event_handle_list.append(evt_ref.ref)
            
    # return event_handle_list and event types to its caller
    return event_handle_list, event_types
