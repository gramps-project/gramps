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

Classes:
    NavWebReport - main class that produces the report. Entry point to produce
    the report is write_report
    NavWebOptions - class that defines the options and provides the handling
    interface

"""
# ------------------------------------------------
# python modules
# ------------------------------------------------
import logging
from functools import partial
import os
import sys
import time
import shutil
import tarfile
from io import BytesIO, TextIOWrapper
from collections import defaultdict
from decimal import getcontext

# ------------------------------------------------
# Gramps module
# ------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.const import VERSION_DIR
from gramps.gen.lib import (
    EventType,
    Name,
    Person,
    Family,
    Event,
    Place,
    PlaceName,
    Source,
    Citation,
    Media,
    Repository,
    Note,
    Tag,
)
from gramps.gen.lib.date import Today
from gramps.gen.plug.menu import (
    PersonOption,
    NumberOption,
    StringOption,
    BooleanOption,
    EnumeratedListOption,
    FilterOption,
    NoteOption,
    MediaOption,
    DestinationOption,
)
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.constfunc import win, get_curr_dir
from gramps.gen.config import config
from gramps.gen.datehandler import displayer as _dd
from gramps.gen.display.name import displayer as _nd
from gramps.gen.display.place import displayer as _pd
from gramps.gen.proxy import CacheProxyDb
from gramps.plugins.lib.libhtmlconst import _CHARACTER_SETS, _CC, _COPY_OPTIONS
from gramps.gen.relationship import get_relationship_calculator

# ------------------------------------------------
# specific narrative web import
# ------------------------------------------------
from gramps.plugins.webreport.basepage import BasePage
from gramps.plugins.webreport.person import PersonPages
from gramps.plugins.webreport.family import FamilyPages
from gramps.plugins.webreport.event import EventPages
from gramps.plugins.webreport.media import MediaPages
from gramps.plugins.webreport.place import PlacePages
from gramps.plugins.webreport.source import SourcePages
from gramps.plugins.webreport.repository import RepositoryPages
from gramps.plugins.webreport.citation import CitationPages
from gramps.plugins.webreport.surnamelist import SurnameListPage
from gramps.plugins.webreport.surname import SurnamePage
from gramps.plugins.webreport.thumbnail import ThumbnailPreviewPage
from gramps.plugins.webreport.statistics import StatisticsPage
from gramps.plugins.webreport.updates import UpdatesPage
from gramps.plugins.webreport.multilang import IndexPage
from gramps.plugins.webreport.home import HomePage
from gramps.plugins.webreport.contact import ContactPage
from gramps.plugins.webreport.download import DownloadPage
from gramps.plugins.webreport.introduction import IntroductionPage
from gramps.plugins.webreport.addressbook import AddressBookPage
from gramps.plugins.webreport.addressbooklist import AddressBookListPage
from gramps.plugins.webreport.calendar import CalendarPage

from gramps.plugins.webreport.common import (
    get_gendex_data,
    HTTP,
    HTTPS,
    _WEB_EXT,
    CSS,
    _NARRATIVESCREEN,
    _NARRATIVEPRINT,
    _WRONGMEDIAPATH,
    sort_people,
)

LOG = logging.getLogger(".NarrativeWeb")
_ = glocale.translation.sgettext
getcontext().prec = 8

# ------------------------------------------------
# constants
# ------------------------------------------------
_DEFAULT_MAX_IMG_WIDTH = 800  # resize images that are wider than this
_DEFAULT_MAX_IMG_HEIGHT = 600  # resize images that are taller than this


# The two values above are settable in options.
class NavWebReport(Report):
    """
    Create WebReport object that produces the report.
    """

    def __init__(self, database, options, user):
        """
        @param: database -- The Gramps database instance
        @param: options  -- Instance of the Options class for this report
        @param: user     -- Instance of a gen.user.User()
        """
        Report.__init__(self, database, options, user)
        self.user = user
        menu = options.menu
        self.link_prefix_up = True
        self.options = {}

        for optname in menu.get_all_option_names():
            menuopt = menu.get_option_by_name(optname)
            self.options[optname] = menuopt.get_value()

        self.set_locale(options.menu.get_option_by_name("trans").get_value())
        stdoptions.run_date_format_option(self, menu)
        self.rlocale = self._ = self._locale
        self.the_lang = self.rlocale.language[0]

        stdoptions.run_private_data_option(self, menu)
        stdoptions.run_living_people_option(self, menu)
        self.database = CacheProxyDb(self.database)
        self._db = self.database

        filters_option = menu.get_option_by_name("filter")
        self.filter = filters_option.get_filter()

        self.copyright = self.options["cright"]
        self.target_path = self.options["target"]
        self.ext = self.options["ext"]
        self.css = self.options["css"]
        self.navigation = self.options["navigation"]
        self.citationreferents = self.options["citationreferents"]

        self.inc_tags = self.options["inc_tags"]

        self.title = self.options["title"]

        self.inc_gallery = self.options["gallery"]
        self.inc_unused_gallery = self.options["unused"]
        self.create_thumbs_only = self.options["create_thumbs_only"]
        self.create_thumbs_index = self.options["create_thumbs_index"]
        self.create_images_index = self.options["create_images_index"]

        self.opts = self.options
        self.inc_contact = self.opts["contactnote"] or self.opts["contactimg"]

        # name format options
        self.name_format = self.options["name_format"]

        # include families or not?
        self.inc_families = self.options["inc_families"]

        # create an event pages or not?
        self.inc_events = self.options["inc_events"]

        # create places pages or not?
        self.inc_places = self.options["inc_places"]

        # create sources pages or not?
        self.inc_sources = self.options["inc_sources"]

        # include repository page or not?
        self.inc_repository = self.options["inc_repository"]

        # include GENDEX page or not?
        self.inc_gendex = self.options["inc_gendex"]

        # Download Options Tab
        self.inc_download = self.options["incdownload"]
        self.nb_download = self.options["nbdownload"]
        self.dl_descr = {}
        self.dl_fname = {}
        for count in range(1, self.nb_download + 1):
            fnamex = "down_fname%c" % str(count)
            descrx = "dl_descr%c" % str(count)
            self.dl_fname[count] = self.options[fnamex]
            self.dl_descr[count] = self.options[descrx]

        self.encoding = self.options["encoding"]

        self.use_archive = self.options["archive"]
        self.use_intro = self.options["intronote"] or self.options["introimg"]
        self.use_home = self.options["homenote"] or self.options["homeimg"]
        self.use_contact = self.opts["contactnote"] or self.opts["contactimg"]
        self.inc_stats = self.opts["inc_stats"]
        self.inc_updates = self.opts["updates"]
        self.create_unused_media = self.opts["unused"]

        # Do we need to include this in a CMS?
        self.usecms = self.options["usecms"]
        self.target_uri = self.options["cmsuri"]

        # Do we add an extra page?
        # extrapage is the URI
        # extrapagename is the visible name in the navigation bar.
        self.extrapage = self.options["extrapage"]
        self.extrapagename = self.options["extrapagename"]

        # Do we need to include web calendar?
        self.usecal = self.options["usecal"]
        self.calendar = None

        # Do we need to include news and updates page?
        self.inc_updates = self.options["updates"]

        # either include the gender graphics or not?
        self.ancestortree = self.options["ancestortree"]

        # whether to display children in birthorder or entry order?
        self.birthorder = self.options["birthorder"]

        # get option for Internet Address Book
        self.inc_addressbook = self.options["inc_addressbook"]

        # Place Map tab options
        self.placemappages = self.options["placemappages"]
        self.familymappages = self.options["familymappages"]
        self.mapservice = self.options["mapservice"]
        self.googleopts = self.options["googleopts"]
        self.googlemapkey = self.options["googlemapkey"]
        self.stamenopts = self.options["stamenopts"]
        self.reference_sort = self.options["reference_sort"]

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
        self.cur_fname = None  # Internal use. The name of the output file,
        # to be used for the tar archive.
        self.string_io = None
        if self.use_archive:
            self.html_dir = None
        else:
            self.html_dir = self.target_path
        self.warn_dir = True  # Only give warning once.
        self.obj_dict = None
        self.visited = None
        self.bkref_dict = None
        self.rel_class = None
        self.tab = None
        self.fam_link = {}
        if self.options["securesite"]:
            self.secure_mode = HTTPS
        else:
            self.secure_mode = HTTP
        self.languages = None
        self.default_lang = None
        self.the_title = None
        self.dir = "ltr"

    def write_report(self):
        """
        The first method called to write the Narrative Web after loading options
        """
        # begin performance check initialization
        # import cProfile, pstats, io
        # pr = cProfile.Profile()
        # pr.enable()
        # end performance check
        global _WRONGMEDIAPATH

        _WRONGMEDIAPATH = []
        if not self.use_archive:
            dir_name = self.target_path
            if dir_name is None:
                dir_name = get_curr_dir()
            elif not os.path.isdir(dir_name):
                parent_dir = os.path.dirname(dir_name)
                if not os.path.isdir(parent_dir):
                    msg = _("Neither %(current)s nor %(parent)s " "are directories") % {
                        "current": dir_name,
                        "parent": parent_dir,
                    }
                    self.user.notify_error(msg)
                    return
                else:
                    try:
                        os.mkdir(dir_name)
                    except IOError as value:
                        msg = (
                            _("Could not create the directory: %s") % dir_name
                            + "\n"
                            + value.strerror
                        )
                        self.user.notify_error(msg)
                        return
                    except Exception as exception:
                        LOG.exception(exception)
                        msg = _("Could not create the directory: %s") % dir_name
                        self.user.notify_error(msg)
                        return

            try:
                image_dir_name = os.path.join(dir_name, "images")
                if not os.path.isdir(image_dir_name):
                    os.mkdir(image_dir_name)

                image_dir_name = os.path.join(dir_name, "thumb")
                if not os.path.isdir(image_dir_name):
                    os.mkdir(image_dir_name)
            except IOError as value:
                msg = (
                    _("Could not create the directory: %s") % image_dir_name
                    + "\n"
                    + value.strerror
                )
                self.user.notify_error(msg)
                return
            except Exception as exception:
                LOG.exception(exception)
                msg = (
                    _("Could not create the directory: %s") % image_dir_name
                    + "\n"
                    + str(exception)
                )
                self.user.notify_error(msg)
                return
        else:
            if os.path.isdir(self.target_path):
                self.user.notify_error(
                    _("Invalid file name"),
                    _("The archive file must be a file, not a directory"),
                )
                return
            try:
                self.archive = tarfile.open(self.target_path, "w:gz")
            except (OSError, IOError) as value:
                self.user.notify_error(
                    _("Could not create %s") % self.target_path, str(value)
                )
                return
        config.set(
            "paths.website-directory", os.path.dirname(self.target_path) + os.sep
        )
        if self.usecms:
            config.set("paths.website-cms-uri", os.path.dirname(self.target_uri))

        # for use with discovering biological, half, and step siblings for use
        # in display_ind_parents()...
        self.rel_class = get_relationship_calculator(reinit=True, clocale=self.rlocale)

        #################################################
        #
        # Pass 0 Initialise the plug-ins
        #
        #################################################

        # FIXME: The whole of this section of code should be implemented by the
        # registration process for the Web Page plugins.

        # Note that by use of a dictionary we ensure that at most one Web Page
        # plugin is provided for any object class

        self.tab = {}
        # FIXME: Initialising self.tab in this way means that this code has to
        # run before the Web Page registration - I am not sure whether this is
        # possible, in which case an alternative approach to providing the
        # mapping of object class to Web Page plugin will be needed.
        for obj_class in (
            "Person",
            "Family",
            "Source",
            "Citation",
            "Place",
            "Event",
            "Media",
            "Repository",
        ):
            # FIXME: Would it be better if the Web Page plugins used a different
            # base class rather than BasePage, which is really just for each web
            # page
            self.tab[obj_class] = BasePage(self, None, None)

        # Note that by not initialising any Web Page plugins that are not going
        # to generate pages, we ensure that there is not performance implication
        # for such plugins.
        self.tab["Person"] = PersonPages(self, None, None)
        if self.inc_families:
            self.tab["Family"] = FamilyPages(self, None, None)
        if self.inc_events:
            self.tab["Event"] = EventPages(self, None, None)
        if self.inc_gallery:
            self.tab["Media"] = MediaPages(self, None, None)
        self.tab["Place"] = PlacePages(self, None, None)
        self.tab["Source"] = SourcePages(self, None, None)
        self.tab["Repository"] = RepositoryPages(self, None, None)
        self.tab["Citation"] = CitationPages(self, None, None)

        # FIXME: The following routines that are not run in two passes have not
        # yet been converted to a form suitable for separation into Web Page
        # plugins: SurnamePage, SurnameListPage, IntroductionPage, HomePage,
        # ThumbnailPreviewPage, DownloadPage, ContactPage,AddressBookListPage,
        # AddressBookPage

        #################################################
        #
        # Pass 1 Build the lists of objects to be output
        #
        #################################################

        self._build_obj_dict()

        #################################################
        #
        # Add images for home, contact and introduction pages
        # if they are not associated to any used objects.
        #
        #################################################
        if self.use_home:
            img = self.options["homeimg"]
            if img:
                media = self._db.get_media_from_gramps_id(img)
                if media:
                    self._add_media(media.handle, Media, media.handle)
        if self.inc_contact:
            img = self.options["contactimg"]
            if img:
                media = self._db.get_media_from_gramps_id(img)
                if media:
                    self._add_media(media.handle, Media, media.handle)
        if self.use_intro:
            img = self.options["introimg"]
            if img:
                media = self._db.get_media_from_gramps_id(img)
                if media:
                    self._add_media(media.handle, Media, media.handle)

        #################################################
        #
        # Pass 2 Generate the web pages
        #
        #################################################

        self.languages = []
        self.default_lang = self.options["trans"]
        if self.default_lang == "default":
            self.default_lang = self.rlocale.language[0]
        self.languages.append((self.default_lang, self.options["title"]))
        if self.options["multitrans"]:
            for idx in range(2, 7):
                lang = "lang%c" % str(idx)
                titl = "title%c" % str(idx)
                if self.options[lang] != "default":
                    cur_lang = self.options[lang]
                    cur_title = self.options[titl]
                    self.languages.append((cur_lang, cur_title))

        self.visited = []
        if len(self.languages) > 1:
            IndexPage(self, self.languages)

        for the_lang, the_title in self.languages:
            if len(self.languages) == 1:
                the_lang = None
                the_title = self.title
            if the_lang == "default":
                the_lang = self.rlocale.language[0]
            self.the_lang = the_lang
            self.the_title = the_title
            self.base_pages()

            # build classes IndividualListPage and IndividualPage
            self.tab["Person"].display_pages(the_lang, the_title)

            self.build_gendex(self.obj_dict[Person], the_lang)

            # build classes SurnameListPage and SurnamePage
            self.surname_pages(self.obj_dict[Person], the_lang, the_title)

            # build classes FamilyListPage and FamilyPage
            if self.inc_families:
                self.tab["Family"].display_pages(the_lang, the_title)

            # build classes EventListPage and EventPage
            if self.inc_events:
                self.tab["Event"].display_pages(the_lang, the_title)

            # build classes PlaceListPage and PlacePage
            self.tab["Place"].display_pages(the_lang, the_title)

            # build classes RepositoryListPage and RepositoryPage
            if self.inc_repository:
                self.tab["Repository"].display_pages(the_lang, the_title)

            # build classes MediaListPage and MediaPage
            if self.inc_gallery:
                if not self.create_thumbs_only:
                    self.tab["Media"].display_pages(the_lang, the_title)

                # build Thumbnail Preview Page...
                self.thumbnail_preview_page()

            # build classes AddressBookListPage and AddressBookPage
            if self.inc_addressbook:
                self.addressbook_pages(self.obj_dict[Person])

            # build classes SourceListPage and SourcePage
            self.tab["Source"].display_pages(the_lang, the_title)

            # build calendar for the current year
            if self.usecal:
                self.calendar = CalendarPage(self, the_lang, None)
                self.calendar.display_pages(the_lang, the_title)

            # build classes StatisticsPage
            if self.inc_stats:
                self.statistics_preview_page()

            # build classes Updates
            if self.inc_updates:
                self.updates_preview_page()

        # copy all of the necessary files
        self.copy_narrated_files()

        # if an archive is being used, close it?
        if self.archive:
            self.archive.close()

        if _WRONGMEDIAPATH:
            error = "\n".join(
                [
                    _("ID=%(grampsid)s, path=%(dir)s") % {"grampsid": x[0], "dir": x[1]}
                    for x in _WRONGMEDIAPATH[:10]
                ]
            )
            if len(_WRONGMEDIAPATH) > 10:
                error += "\n ..."
            self.user.warn(_("Missing media objects:"), error)
        self.database.clear_cache()
        # begin print performance check
        # pr.disable()
        # pr.print_stats()
        # end print performance check

    def _build_obj_dict(self):
        """
        Construct the dictionaries of objects to be included in the reports.
        There are two dictionaries, which have the same structure: they are two
        level dictionaries,the first key is the class of object
        (e.g. gen.lib.Person).
        The second key is the handle of the object.

        For the obj_dict, the value is a tuple containing the gramps_id,
        the text name for the object, and the file name for the display.

        For the bkref_dict, the value is a tuple containing the class of object
        and the handle for the object that refers to the 'key' object.
        """
        _obj_class_list = (
            Person,
            Family,
            Event,
            Place,
            Source,
            Citation,
            Media,
            Repository,
            Note,
            Tag,
            PlaceName,
        )

        # setup a dictionary of the required structure
        self.obj_dict = defaultdict(lambda: defaultdict(set))
        self.bkref_dict = defaultdict(lambda: defaultdict(set))

        # initialise the dictionary to empty in case no objects of any
        # particular class are included in the web report
        for obj_class in _obj_class_list:
            self.obj_dict[obj_class] = defaultdict(set)

        ind_list = self._db.iter_person_handles()
        ind_list = self.filter.apply(self._db, ind_list, user=self.user)

        message = _("Constructing list of other objects...")
        pgr_title = self.pgrs_title(None)
        with self.user.progress(pgr_title, message, sum(1 for _ in ind_list)) as step:
            index = 1
            for handle in ind_list:
                self._add_person(handle, "", "")
                step()
                index += 1

        LOG.debug(
            "final object dictionary \n"
            + "".join(("%s: %s\n" % item) for item in self.obj_dict.items())
        )

        LOG.debug(
            "final backref dictionary \n"
            + "".join(("%s: %s\n" % item) for item in self.bkref_dict.items())
        )

    def _add_person(self, person_handle, bkref_class, bkref_handle):
        """
        Add person_handle to the obj_dict, and recursively all referenced
        objects

        @param: person_handle -- The handle for the person to add
        @param: bkref_class   -- The class associated to this handle (person)
        @param: bkref_handle  -- The handle associated to this person
        """
        if self.obj_dict[Person][person_handle]:
            # This person is already in the list of selected people.
            # This can be achieved with associated people.
            return

        person = self._db.get_person_from_handle(person_handle)
        if person:
            person_name = self.get_person_name(person)
            person_fname = (
                self.build_url_fname(person_handle, "ppl", False, init=True) + self.ext
            )
            self.obj_dict[Person][person_handle] = (
                person_fname,
                person_name,
                person.gramps_id,
            )
            self.bkref_dict[Person][person_handle].add((bkref_class, bkref_handle, ""))

            ############### Header section ##############
            for citation_handle in person.get_citation_list():
                self._add_citation(citation_handle, Person, person_handle)

            ############### Name section ##############
            for name in [person.get_primary_name()] + person.get_alternate_names():
                for citation_handle in name.get_citation_list():
                    self._add_citation(citation_handle, Person, person_handle)

            ############### Events section ##############
            # Now tell the events tab to display the individual events
            evt_ref_list = person.get_event_ref_list()
            if evt_ref_list:
                for evt_ref in evt_ref_list:
                    role = evt_ref.get_role().xml_str()
                    event = self._db.get_event_from_handle(evt_ref.ref)
                    if event:
                        self._add_event(evt_ref.ref, Person, person_handle, role)
                        place_handle = event.get_place_handle()
                        if place_handle:
                            self._add_place(place_handle, Person, person_handle, event)
                        # If event pages are not being output, then tell the
                        # media tab to display the person's event media. If
                        # events are being displayed, then the media are linked
                        # from the event tab
                        if not self.inc_events:
                            for media_ref in event.get_media_list():
                                media_handle = media_ref.get_reference_handle()
                                self._add_media(media_handle, Person, person_handle)

                        for citation_handle in event.get_citation_list():
                            self._add_citation(citation_handle, Person, person_handle)
                        for citation_handle in evt_ref.get_citation_list():
                            self._add_citation(citation_handle, Person, person_handle)
                        for attr in evt_ref.get_attribute_list():
                            for citation_handle in attr.get_citation_list():
                                self._add_citation(citation_handle, Event, evt_ref.ref)

            ############### Families section ##############
            # Tell the families tab to display this individuals families
            family_handle_list = person.get_family_handle_list()
            if family_handle_list:
                for family_handle in person.get_family_handle_list():
                    self._add_family(family_handle, Person, person_handle)

                    # Tell the events tab to display the family events which
                    # are referenced from the individual page.
                    family = self._db.get_family_from_handle(family_handle)
                    if family:
                        family_evt_ref_list = family.get_event_ref_list()
                        if family_evt_ref_list:
                            for evt_ref in family_evt_ref_list:
                                role = evt_ref.get_role().xml_str()
                                event = self._db.get_event_from_handle(evt_ref.ref)
                                if event:
                                    self._add_event(
                                        evt_ref.ref, Person, person_handle, "Primary"
                                    )
                                    place_handle = event.get_place_handle()
                                    if place_handle:
                                        self._add_place(
                                            place_handle, Person, person_handle, event
                                        )
                                    for cite_hdl in event.get_citation_list():
                                        self._add_citation(
                                            cite_hdl, Person, person_handle
                                        )
                                    for cite_hdl in evt_ref.get_citation_list():
                                        self._add_citation(
                                            cite_hdl, Person, person_handle
                                        )
                                    # add the family media and the family event media if the
                                    # families page is not being displayed (If it is displayed,
                                    # the media are linked from the families page)
                                    if not self.inc_families:
                                        for m_ref in event.get_media_list():
                                            m_hdl = m_ref.get_reference_handle()
                                            self._add_media(
                                                m_hdl, Person, person_handle
                                            )

                        for lds_ord in family.get_lds_ord_list():
                            for citation_handle in lds_ord.get_citation_list():
                                self._add_citation(
                                    citation_handle, Person, person_handle
                                )

                        for attr in family.get_attribute_list():
                            for citation_handle in attr.get_citation_list():
                                self._add_citation(
                                    citation_handle, Person, person_handle
                                )

                        if not self.inc_families:
                            for media_ref in family.get_media_list():
                                media_handle = media_ref.get_reference_handle()
                                self._add_media(media_handle, Person, person_handle)

            ############### Associations section ##############
            for assoc in person.get_person_ref_list():
                self._add_person(assoc.ref, "", "")

            ############### LDS Ordinance section ##############
            for lds_ord in person.get_lds_ord_list():
                for citation_handle in lds_ord.get_citation_list():
                    self._add_citation(citation_handle, Person, person_handle)

            ############### Attribute section ##############
            for attr in person.get_attribute_list():
                for citation_handle in attr.get_citation_list():
                    self._add_citation(citation_handle, Person, person_handle)

            ############### Address section ##############
            for addr in person.get_address_list():
                for addr_handle in addr.get_citation_list():
                    self._add_citation(addr_handle, Person, person_handle)

            ############### Media section ##############
            # Now tell the Media tab which media objects to display
            # First the person's media objects
            for media_ref in person.get_media_list():
                media_handle = media_ref.get_reference_handle()
                self._add_media(media_handle, Person, person_handle)

    def get_person_name(self, person):
        """
        Return a string containing the person's primary name in the name
        format chosen in the web report options

        @param: person -- person object from database
        """
        name_format = self.options["name_format"]
        primary_name = person.get_primary_name()
        name = Name(primary_name)
        name.set_display_as(name_format)
        return _nd.display_name(name)

    def _add_family(self, family_handle, bkref_class, bkref_handle):
        """
        Add family to the Family object list

        @param: family_handle -- The handle for the family to add
        @param: bkref_class   -- The class associated to this handle (family)
        @param: bkref_handle  -- The handle associated to this family
        """
        family = self._db.get_family_from_handle(family_handle)
        family_name = self.get_family_name(family)
        if self.inc_families:
            family_fname = (
                self.build_url_fname(family_handle, "fam", False, init=True) + self.ext
            )
        else:
            family_fname = ""
        self.obj_dict[Family][family_handle] = (
            family_fname,
            family_name,
            family.gramps_id,
        )
        self.bkref_dict[Family][family_handle].add((bkref_class, bkref_handle, ""))

        if self.inc_gallery:
            for media_ref in family.get_media_list():
                media_handle = media_ref.get_reference_handle()
                self._add_media(media_handle, Family, family_handle)

        ############### Events section ##############
        for evt_ref in family.get_event_ref_list():
            role = evt_ref.get_role().xml_str()
            event = self._db.get_event_from_handle(evt_ref.ref)
            place_handle = event.get_place_handle()
            if place_handle:
                self._add_place(place_handle, Family, family_handle, event)

            if self.inc_events:
                # detail for family events are displayed on the events pages as
                # well as on this family page
                self._add_event(evt_ref.ref, Family, family_handle, role)
            else:
                # There is no event page. Family events are displayed on the
                # family page, but the associated family event media may need to
                # be displayed on the media page
                if self.inc_gallery:
                    for media_ref in event.get_media_list():
                        media_handle = media_ref.get_reference_handle()
                        self._add_media(media_handle, Family, family_handle)

        ############### LDS Ordinance section ##############
        for lds_ord in family.get_lds_ord_list():
            for citation_handle in lds_ord.get_citation_list():
                self._add_citation(citation_handle, Family, family_handle)

        ############### Attributes section ##############
        for attr in family.get_attribute_list():
            for citation_handle in attr.get_citation_list():
                self._add_citation(citation_handle, Family, family_handle)

        ############### Sources section ##############
        for citation_handle in family.get_citation_list():
            self._add_citation(citation_handle, Family, family_handle)

    def get_family_name(self, family):
        """
        Return a string containing the name of the family (e.g. 'Family of John
        Doe and Jane Doe')

        @param: family -- family object from database
        """
        self.rlocale = self.set_locale(self.the_lang)
        self._ = self.rlocale.translation.sgettext
        if isinstance(family, Family):
            husband_handle = family.get_father_handle()
            spouse_handle = family.get_mother_handle()
        else:
            # B13207
            husband_handle = spouse_handle = None

        if husband_handle:
            husband = self._db.get_person_from_handle(husband_handle)
        else:
            husband = None
        if spouse_handle:
            spouse = self._db.get_person_from_handle(spouse_handle)
        else:
            spouse = None

        if husband and spouse:
            husband_name = self.get_person_name(husband)
            spouse_name = self.get_person_name(spouse)
            title_str = self._("Family of %(husband)s and %(spouse)s") % {
                "husband": husband_name,
                "spouse": spouse_name,
            }
        elif husband:
            husband_name = self.get_person_name(husband)
            # Only the name of the husband is known
            title_str = self._("Family of %s") % husband_name
        elif spouse:
            spouse_name = self.get_person_name(spouse)
            # Only the name of the wife is known
            title_str = self._("Family of %s") % spouse_name
        else:
            title_str = ""

        return title_str

    def _add_event(self, event_handle, bkref_class, bkref_handle, role):
        """
        Add event to the Event object list

        @param: event_handle -- The handle for the event to add
        @param: bkref_class  -- The class associated to this handle (event)
        @param: bkref_handle -- The handle associated to this event
        """
        event = self._db.get_event_from_handle(event_handle)
        event_name = event.get_description()
        # The event description can be Y on import from GEDCOM. See the
        # following quote from the GEDCOM spec: "The occurrence of an event is
        # asserted by the presence of either a DATE tag and value or a PLACe tag
        # and value in the event structure. When neither the date value nor the
        # place value are known then a Y(es) value on the parent event tag line
        # is required to assert that the event happened.""
        if event_name == "" or event_name is None or event_name == "Y":
            event_name = str(event.get_type())
            # begin add generated descriptions to media pages
            # (request 7074 : acrider)
            ref_name = ""
            for reference in self._db.find_backlink_handles(event_handle):
                ref_class, ref_handle = reference
                if ref_class == "Person":
                    person = self._db.get_person_from_handle(ref_handle)
                    ref_name = self.get_person_name(person)
                elif ref_class == "Family":
                    family = self._db.get_family_from_handle(ref_handle)
                    ref_name = self.get_family_name(family)
            if ref_name != "":
                # TODO for Arabic, should the next line's comma be translated?
                event_name += ", " + ref_name
            # end descriptions to media pages
        if self.inc_events:
            event_fname = (
                self.build_url_fname(event_handle, "evt", False, init=True) + self.ext
            )
        else:
            event_fname = ""
        self.obj_dict[Event][event_handle] = (event_fname, event_name, event.gramps_id)
        self.bkref_dict[Event][event_handle].add((bkref_class, bkref_handle, role))

        ############### Attribute section ##############
        for attr in event.get_attribute_list():
            for citation_handle in attr.get_citation_list():
                self._add_citation(citation_handle, Event, event_handle)

        ############### Source section ##############
        for citation_handle in event.get_citation_list():
            self._add_citation(citation_handle, Event, event_handle)

        ############### Media section ##############
        if self.inc_gallery:
            for media_ref in event.get_media_list():
                media_handle = media_ref.get_reference_handle()
                self._add_media(media_handle, Event, event_handle)

    def _add_place(self, place_handle, bkref_class, bkref_handle, event):
        """
        Add place to the Place object list

        @param: place_handle -- The handle for the place to add
        @param: bkref_class  -- The class associated to this handle (place)
        @param: bkref_handle -- The handle associated to this place
        """
        place = self._db.get_place_from_handle(place_handle)
        if place is None:
            return
        if bkref_class == Person:
            person = self._db.get_person_from_handle(bkref_handle)
            name = _nd.display(person)
        else:
            family = self._db.get_family_from_handle(bkref_handle)
            husband_handle = family.get_father_handle()
            if husband_handle:
                person = self._db.get_person_from_handle(husband_handle)
                name = _nd.display(person)
            else:
                name = ""
        if config.get("preferences.place-auto"):
            place_name = _pd.display_event(self._db, event, fmt=0)
            if event:
                cplace_name = place_name.split()[-1]
                if len(place_name.split()) > 1:
                    splace_name = place_name.split()[-2]
                else:
                    splace_name = cplace_name
            else:
                cplace_name = None
                splace_name = None
        else:
            place_name = place.get_title()
            cplace_name = place_name
            splace_name = place_name
        if event:
            if self.reference_sort:
                role_or_date = name
            else:
                date = event.get_date_object()
                # calendar is the original date calendar
                calendar = str(date.get_calendar())
                # convert date to Gregorian for a correct sort
                _date = str(date.to_calendar("gregorian"))
                role_or_date = calendar + ":" + _date
        else:
            role_or_date = ""
        place_fname = (
            self.build_url_fname(place_handle, "plc", False, init=True) + self.ext
        )
        self.obj_dict[Place][place_handle] = (
            place_fname,
            place_name,
            place.gramps_id,
            event,
        )
        self.obj_dict[PlaceName][place_name] = (
            place_handle,
            place_name,
            splace_name,
            cplace_name,
            place.gramps_id,
            event,
        )
        self.bkref_dict[Place][place_handle].add(
            (bkref_class, bkref_handle, role_or_date)
        )

        ############### Media section ##############
        if self.inc_gallery:
            for media_ref in place.get_media_list():
                media_handle = media_ref.get_reference_handle()
                self._add_media(media_handle, Place, place_handle)

        ############### Sources section ##############
        for citation_handle in place.get_citation_list():
            self._add_citation(citation_handle, Place, place_handle)

    def _add_source(self, source_handle, bkref_class, bkref_handle):
        """
        Add source to the Source object list

        @param: source_handle -- The handle for the source to add
        @param: bkref_class   -- The class associated to this handle (source)
        @param: bkref_handle  -- The handle associated to this source
        """
        if self.obj_dict[Source][source_handle]:
            for bkref in self.bkref_dict[Source][source_handle]:
                if bkref_handle == bkref[1]:
                    return
        source = self._db.get_source_from_handle(source_handle)
        source_name = source.get_title()
        source_fname = (
            self.build_url_fname(source_handle, "src", False, init=True) + self.ext
        )
        self.obj_dict[Source][source_handle] = (
            source_fname,
            source_name,
            source.gramps_id,
        )
        self.bkref_dict[Source][source_handle].add(
            (bkref_class, bkref_handle, "")  # no role
        )

        ############### Media section ##############
        if self.inc_gallery:
            for media_ref in source.get_media_list():
                media_handle = media_ref.get_reference_handle()
                self._add_media(media_handle, Source, source_handle)

        ############### Repository section ##############
        if self.inc_repository:
            for repo_ref in source.get_reporef_list():
                repo_handle = repo_ref.get_reference_handle()
                self._add_repository(repo_handle, Source, source_handle)

    def _add_citation(self, citation_handle, bkref_class, bkref_handle):
        """
        Add citation to the Citation object list

        @param: citation_handle -- The handle for the citation to add
        @param: bkref_class     -- The class associated to this handle
        @param: bkref_handle    -- The handle associated to this citation
        """
        if self.obj_dict[Citation][citation_handle]:
            for bkref in self.bkref_dict[Citation][citation_handle]:
                if bkref_handle == bkref[1]:
                    return
        citation = self._db.get_citation_from_handle(citation_handle)
        # If Page is none, we want to make sure that a tuple is generated for
        # the source backreference
        citation_name = citation.get_page() or ""
        source_handle = citation.get_reference_handle()
        self.obj_dict[Citation][citation_handle] = (
            "",
            citation_name,
            citation.gramps_id,
        )
        self.bkref_dict[Citation][citation_handle].add(
            (bkref_class, bkref_handle, "")  # no role
        )

        ############### Source section ##############
        self._add_source(source_handle, Citation, citation_handle)

        ############### Media section ##############
        if self.inc_gallery:
            for media_ref in citation.get_media_list():
                media_handle = media_ref.get_reference_handle()
                self._add_media(media_handle, Citation, citation_handle)

    def _add_media(self, media_handle, bkref_class, bkref_handle):
        """
        Add media to the Media object list

        @param: media_handle -- The handle for the media to add
        @param: bkref_class  -- The class associated to this handle (media)
        @param: bkref_handle -- The handle associated to this media
        """
        if self.obj_dict[Media][media_handle]:
            for bkref in self.bkref_dict[Media][media_handle]:
                if bkref_handle == bkref[1]:
                    return
        media_refs = self.bkref_dict[Media].get(media_handle)
        if media_refs and (bkref_class, bkref_handle) in media_refs:
            return
        media = self._db.get_media_from_handle(media_handle)
        # use media title (request 7074 acrider)
        media_name = media.get_description()
        if media_name is None or media_name == "":
            media_name = "Media"
        # end media title
        if self.inc_gallery:
            media_fname = (
                self.build_url_fname(media_handle, "img", False, init=True) + self.ext
            )
        else:
            media_fname = ""
        self.obj_dict[Media][media_handle] = (media_fname, media_name, media.gramps_id)
        self.bkref_dict[Media][media_handle].add(
            (bkref_class, bkref_handle, "")  # no role for a media
        )

        ############### Attribute section ##############
        for attr in media.get_attribute_list():
            for citation_handle in attr.get_citation_list():
                self._add_citation(citation_handle, Media, media_handle)

        ############### Sources section ##############
        for citation_handle in media.get_citation_list():
            self._add_citation(citation_handle, Media, media_handle)

    def _add_repository(self, repos_handle, bkref_class, bkref_handle):
        """
        Add repository to the Repository object list

        @param: repos_handle -- The handle for the repository to add
        @param: bkref_class  -- The class associated to this handle (source)
        @param: bkref_handle -- The handle associated to this source
        """
        if self.obj_dict[Repository][repos_handle]:
            for bkref in self.bkref_dict[Repository][repos_handle]:
                if bkref_handle == bkref[1]:
                    return
        repos = self._db.get_repository_from_handle(repos_handle)
        repos_name = repos.name
        if self.inc_repository:
            repos_fname = (
                self.build_url_fname(repos_handle, "repo", False, init=True) + self.ext
            )
        else:
            repos_fname = ""
        self.obj_dict[Repository][repos_handle] = (
            repos_fname,
            repos_name,
            repos.gramps_id,
        )
        self.bkref_dict[Repository][repos_handle].add(
            (bkref_class, bkref_handle, "")  # no role
        )

    def copy_narrated_files(self):
        """
        Copy all of the CSS, image, and javascript files for Narrative Web
        """
        imgs = []

        # copy all screen style sheet
        for css_f in CSS:
            already_done = []
            for css_fn in ("UsEr_", "Basic", "Mainz", "Nebraska", "Vis"):
                if css_fn in css_f and css_f not in already_done:
                    already_done.append(css_f)
                    fname = CSS[css_f]["filename"]
                    # add images for this css
                    imgs += CSS[css_f]["images"]
                    css_f = css_f.replace("UsEr_", "")
                    self.copy_file(fname, css_f + ".css", "css")

        # copy screen style sheet
        if CSS[self.css]["filename"]:
            fname = CSS[self.css]["filename"]
            self.copy_file(fname, _NARRATIVESCREEN, "css")

        # copy printer style sheet
        fname = CSS["Print-Default"]["filename"]
        self.copy_file(fname, _NARRATIVEPRINT, "css")

        # copy ancestor tree style sheet if tree is being created?
        if self.ancestortree:
            fname = CSS["ancestortree"]["filename"]
            self.copy_file(fname, "ancestortree.css", "css")

        # copy behaviour style sheet
        fname = CSS["behaviour"]["filename"]
        self.copy_file(fname, "behaviour.css", "css")

        # copy lightbox style sheet and javascript
        fname = CSS["lightbox"]["filename"]
        self.copy_file(fname, "lightbox.css", "css")
        fname = CSS["lightbox_js"]["filename"]
        self.copy_file(fname, "lightbox.js", "css")

        # copy Menu Layout Style Sheet if Blue or Visually is being
        # used as the stylesheet?
        if CSS[self.css]["navigation"]:
            if self.navigation == "Horizontal":
                fname = CSS["Horizontal-Menus"]["filename"]
            elif self.navigation == "Vertical":
                fname = CSS["Vertical-Menus"]["filename"]
            elif self.navigation == "Fade":
                fname = CSS["Fade-Menus"]["filename"]
            elif self.navigation == "dropdown":
                fname = CSS["DropDown-Menus"]["filename"]
            self.copy_file(fname, "narrative-menus.css", "css")

        # copy narrative-maps Style Sheet if Place or Family Map pages
        # are being created?
        if self.placemappages or self.familymappages:
            fname = CSS["NarrativeMaps"]["filename"]
            self.copy_file(fname, "narrative-maps.css", "css")

        # Copy the Creative Commons icon if the Creative Commons
        # license is requested
        if 0 < self.copyright <= len(_CC):
            imgs += [CSS["Copyright"]["filename"]]

        # copy Gramps favorite icon #2
        imgs += [CSS["favicon2"]["filename"]]

        # we need the blank image gif needed by behaviour.css
        # add the document.png file for media other than photos
        imgs += CSS["All Images"]["images"]

        # copy Ancestor Tree graphics if needed???
        if self.ancestortree:
            imgs += CSS["ancestortree"]["images"]

        # Anything css-specific:
        imgs += CSS[self.css]["images"]

        # copy all to images subdir:
        for from_path in imgs:
            dummy_fdir, fname = os.path.split(from_path)
            self.copy_file(from_path, fname, "images")

        # copy Gramps marker icon for openstreetmap
        fname = CSS["marker"]["filename"]
        self.copy_file(fname, "marker.png", "images")

    def build_gendex(self, ind_list, the_lang):
        """
        Create a gendex file

        @param: ind_list -- The list of person to use
        @param: the_lang -- The lang to process
        """
        if self.inc_gendex:
            message = _("Creating GENDEX file")
            pgr_title = self.pgrs_title(the_lang)
            with self.user.progress(pgr_title, message, len(ind_list)) as step:
                fp_gendex, gendex_io = self.create_file("gendex", ext=".txt")
                date = 0
                index = 1
                for person_handle in ind_list:
                    step()
                    index += 1
                    person = self._db.get_person_from_handle(person_handle)
                    datex = person.get_change_time()
                    if datex > date:
                        date = datex
                    if self.archive:
                        self.write_gendex(gendex_io, person)
                    else:
                        self.write_gendex(fp_gendex, person)
                self.close_file(fp_gendex, gendex_io, date)

    def write_gendex(self, filep, person):
        """
        Reference|SURNAME|given name /SURNAME/|date of birth|place of birth|
            date of death|place of death|
        * field 1: file name of web page referring to the individual
        * field 2: surname of the individual
        * field 3: full name of the individual
        * field 4: date of birth or christening (optional)
        * field 5: place of birth or christening (optional)
        * field 6: date of death or burial (optional)
        * field 7: place of death or burial (optional)

        @param: filep  -- The GENDEX output filename
        @param: person -- The person to use for GENDEX file
        """
        url = self.build_url_fname_html(person.handle, "ppl")
        surname = person.get_primary_name().get_surname()
        fullname = person.get_primary_name().get_gedcom_name()

        # get birth info:
        dob, pob = get_gendex_data(self._db, person.get_birth_ref())

        # get death info:
        dod, pod = get_gendex_data(self._db, person.get_death_ref())
        linew = "|".join((url, surname, fullname, dob, pob, dod, pod)) + "|\n"
        if self.archive:
            filep.write(bytes(linew, "utf8"))
        else:
            filep.write(linew)

    def surname_pages(self, ind_list, the_lang, the_title):
        """
        Generates the surname-related pages from list of individual
        people.

        @param: ind_list  -- The list of person to use
        @param: the_lang  -- The lang to process
        @param: the_title -- The title page for the lang
        """
        local_list = sort_people(self._db, ind_list, self.rlocale)

        message = _("Creating surname pages")
        pgr_title = self.pgrs_title(the_lang)
        with self.user.progress(pgr_title, message, len(local_list)) as step:
            SurnameListPage(
                self,
                the_lang,
                the_title,
                ind_list,
                SurnameListPage.ORDER_BY_NAME,
                self.surname_fname,
            )

            SurnameListPage(
                self,
                the_lang,
                the_title,
                ind_list,
                SurnameListPage.ORDER_BY_COUNT,
                "surnames_count",
            )

            index = 1
            for surname, handle_list in local_list:
                SurnamePage(self, the_lang, the_title, surname, sorted(handle_list))
                step()
                index += 1

    def thumbnail_preview_page(self):
        """
        creates the thumbnail preview page
        """
        if self.create_unused_media:
            media_count = len(self._db.get_media_handles())
        else:
            media_count = len(self.obj_dict[Media])
        pgr_title = self.pgrs_title(self.the_lang)
        with self.user.progress(
            pgr_title, _("Creating thumbnail preview page..."), media_count
        ) as step:
            ThumbnailPreviewPage(self, self.the_lang, self.the_title, step)

    def statistics_preview_page(self):
        """
        creates the statistics preview page
        """
        pgr_title = self.pgrs_title(self.the_lang)
        with self.user.progress(pgr_title, _("Creating statistics page..."), 1) as step:
            StatisticsPage(self, self.the_lang, self.the_title, step)

    def updates_preview_page(self):
        """
        creates the statistics preview page
        """
        pgr_title = self.pgrs_title(self.the_lang)
        with self.user.progress(pgr_title, _("Creating updates page..."), 1):
            UpdatesPage(self, self.the_lang, self.the_title)

    def addressbook_pages(self, ind_list):
        """
        Create a webpage with a list of address availability for each person
        and the associated individual address pages.

        @param: ind_list -- The list of person to use
        """
        url_addr_res = []

        for person_handle in ind_list:
            person = self._db.get_person_from_handle(person_handle)
            addrlist = person.get_address_list()
            evt_ref_list = person.get_event_ref_list()
            urllist = person.get_url_list()

            add = addrlist or None
            url = urllist or None
            res = []

            for event_ref in evt_ref_list:
                event = self._db.get_event_from_handle(event_ref.ref)
                if event.get_type() == EventType.RESIDENCE:
                    res.append(event)

            if add or res or url:
                primary_name = person.get_primary_name()
                sort_name = "".join(
                    [primary_name.get_surname(), ", ", primary_name.get_first_name()]
                )
                url_addr_res.append((sort_name, person_handle, add, res, url))

        url_addr_res.sort()
        AddressBookListPage(self, self.the_lang, self.the_title, url_addr_res)

        # begin Address Book pages
        addr_size = len(url_addr_res)

        message = _("Creating address book pages ...")
        pgr_title = self.pgrs_title(self.the_lang)
        with self.user.progress(pgr_title, message, addr_size) as step:
            index = 1
            for sort_name, person_handle, add, res, url in url_addr_res:
                AddressBookPage(
                    self, self.the_lang, self.the_title, person_handle, add, res, url
                )
                step()
                index += 1

    def base_pages(self):
        """
        creates HomePage, ContactPage, DownloadPage and IntroductionPage
        if requested by options in plugin
        """
        if self.use_home:
            HomePage(self, self.the_lang, self.the_title)

        if self.inc_contact:
            ContactPage(self, self.the_lang, self.the_title)

        if self.inc_download:
            DownloadPage(self, self.the_lang, self.the_title)

        if self.use_intro:
            IntroductionPage(self, self.the_lang, self.the_title)

    def build_subdirs(self, subdir, fname, uplink=False, image=False, init=False):
        """
        If subdir is given, then two extra levels of subdirectory are inserted
        between 'subdir' and the filename. The reason is to prevent directories
        with too many entries.
        For example, this may return "8/1/aec934857df74d36618"
        @param: subdir -- The subdirectory name to use
        @param: fname  -- The file name for which we need to build the path
        @param: uplink -- If True, then "../../../" is inserted in front of the
                          result.
                          If uplink = None then [./] for use in EventListPage
        @param: image  -- We are processing a thumbnail or an image
        @param: init   -- We are building the objects table.
                          Don't try to manage the lang.
        """
        subdirs = []
        if subdir:
            subdirs.append(subdir)
            subdirs.append(fname[-1].lower())
            subdirs.append(fname[-2].lower())
        if init:
            return subdirs
        nb_dir = 0
        if self.the_lang and image:
            nb_dir = 1

        if self.usecms:
            if subdir:
                if self.the_lang and subdir not in ["css", "images", "thumb"]:
                    subdirs = [self.target_uri] + [self.the_lang] + subdirs
                else:
                    subdirs = [self.target_uri] + subdirs
            elif self.target_uri not in fname:
                if self.the_lang and subdir not in ["css", "images", "thumb"]:
                    subdirs = [self.target_uri] + [self.the_lang] + [fname]
                else:
                    subdirs = [self.target_uri] + [fname]
            else:
                subdirs = []
        else:
            if self.the_lang and image and uplink != 2:
                if subdir and subdir[0:3] not in ["css", "ima", "thu"]:
                    subdirs = [self.the_lang] + subdirs
            if uplink is True:
                nb_dir += 3
                subdirs = [".."] * nb_dir + subdirs

            elif uplink == 2:
                # special case for the add_image method
                if subdir and subdir[0:3] in ["css", "ima", "thu"]:
                    if nb_dir == 1:
                        subdirs = [".."] + subdirs
            elif uplink is None:
                # added for use in EventListPage
                subdirs = ["."] + subdirs
        return subdirs

    def build_path(self, subdir, fname, uplink=False, image=False):
        """
        Return the name of the subdirectory.

        Notice that we DO use os.path.join() here.

        @param: subdir -- The subdirectory name to use
        @param: fname  -- The file name for which we need to build the path
        @param: uplink -- If True, then "../../../" is inserted in front of the
                          result.
        @param: image  -- We are processing a thumbnail or an image
        """
        return os.path.join(*self.build_subdirs(subdir, fname, uplink, image))

    def build_url_lang(self, fname, subdir=None, uplink=False):
        """
        builds a url for an extra language

        @param: fname  -- The file name for which we need to build the path
        @param: subdir -- The subdirectory name to use
        @param: uplink -- If True, then "../../../" is inserted in front of the
                          result.
        """
        subdirs = []
        if uplink:
            nb_dir = 4 if self.the_lang else 3
        else:
            nb_dir = 1
        if self.usecms:
            # remove self.target_uri
            fname = fname.replace(self.target_uri + "/", "")
            # remove the lang
            (dummy_1_field, dummy_sep, second_field) = fname.partition("/")
            fname = second_field
        elif self.the_lang:
            (first_field, dummy_sep, second_field) = fname.partition("/")
            if [(lang, title) for lang, title in self.languages if lang == first_field]:
                # remove the lang
                fname = second_field
        if subdir:
            subdirs.append(subdir)
        if self.usecms:
            if self.target_uri not in subdirs:
                subdirs = [self.target_uri] + subdirs
        else:
            subdirs = [".."] * nb_dir + subdirs
        nname = "/".join(subdirs + [fname])
        if win():
            nname = nname.replace("\\", "/")
        return nname

    def build_url_image(self, fname, subdir=None, uplink=False):
        """
        builds a url from an image

        @param: fname  -- The file name for which we need to build the path
        @param: subdir -- The subdirectory name to use
        @param: uplink -- If True, then "../../../" is inserted in front of the
                          result.
        """
        subdirs = []
        if uplink:
            nb_dir = 4 if self.the_lang else 3
        else:
            nb_dir = 1
        if subdir:
            subdirs.append(subdir)
        if self.usecms:
            if self.target_uri not in fname:
                subdirs = [self.target_uri] + subdirs
        else:
            if uplink:
                subdirs = [".."] * nb_dir + subdirs
        nname = "/".join(subdirs + [fname])
        if win():
            nname = nname.replace("\\", "/")
        return nname

    def build_url_fname_html(self, fname, subdir=None, uplink=False):
        """
        builds a url filename from html

        @param: fname  -- The file name to create
        @param: subdir -- The subdirectory name to use
        @param: uplink -- If True, then "../../../" is inserted in front of the
                          result.
        """
        return self.build_url_fname(fname, subdir, uplink) + self.ext

    def build_link(self, prop, handle, obj_class):
        """
        Build a link to an item.

        @param: prop      -- Property
        @param: handle    -- The handle for which we need to build a link
        @param: obj_class -- The class of the related object.
        """
        if prop == "gramps_id":
            func = self._db.method("get_%s_from_gramps_id", obj_class)
            if func:
                obj = func(handle)
                if obj:
                    handle = obj.handle
                else:
                    raise AttributeError(
                        "gramps_id '%s' not found in '%s'" % handle, obj_class
                    )
            else:
                raise AttributeError(
                    "invalid gramps_id lookup " "in table name '%s'" % obj_class
                )
        uplink = self.link_prefix_up
        # handle, ppl
        if obj_class == "Person":
            if self.person_in_webreport(handle):
                return self.build_url_fname(handle, "ppl", uplink) + self.ext
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
        elif obj_class == "Family":
            subdir = "fam"
        else:
            print("NarrativeWeb ignoring link type '%s'" % obj_class)
            return None
        return self.build_url_fname(handle, subdir, uplink) + self.ext

    def build_url_fname(
        self, fname, subdir=None, uplink=False, image=False, init=False
    ):
        """
        Create part of the URL given the filename and optionally the
        subdirectory. If the subdirectory is given, then two extra levels of
        subdirectory are inserted between 'subdir' and the filename.
        The reason is to prevent directories with too many entries.

        @param: fname  -- The filename to create
        @param: subdir -- The subdirectory name to use
        @param: uplink -- if True, then "../../../" is inserted in front of the
                          result.
        @param: image  -- We are processing a thumbnail or an image
        @param: init   -- We are building the objects table.
                          Don't try to manage the lang.

        The extension is added to the filename as well.

        Notice that we do NOT use os.path.join() because we're creating a URL.
        """
        if not fname:
            return ""
        if win():
            fname = fname.replace("\\", "/")
        if init:
            subdirs = self.build_subdirs(subdir, fname, False, init=init)
            return "/".join(subdirs + [fname])
        fname = fname.replace(self.target_uri + "/", "")
        if self.usecms:
            if self.the_lang:
                if subdir:
                    subdirs = self.build_subdirs(subdir, fname, False, image)
                    if self.target_uri in subdirs and image:
                        subdirs.remove(self.target_uri)
                    if subdir[0:3] in ["css", "img", "ima", "thu"]:
                        subdirs = [self.target_uri] + subdirs
                else:
                    if fname[0:3] in ["css", "img", "ima", "thu"]:
                        subdirs = [self.target_uri]
                    elif fname[3:6] in ["css", "img", "ima", "thu"]:
                        subdirs = [self.target_uri]
                        fname = fname[3:]
                    else:
                        subdirs = [self.target_uri] + [self.the_lang]
            else:
                if subdir:
                    subdirs = self.build_subdirs(subdir, fname, False, image)
                else:
                    subdirs = [self.target_uri]
                # remove None value in subdir. this is related to the lang
                if isinstance(subdirs, list):
                    subdirs = [val for val in subdirs if val is not None]
        elif self.the_lang:
            (dummy_1_field, separator, second_field) = fname.partition("/")
            if separator == "/" and second_field[0:3] in ["ima", "thu"]:
                fname = second_field
                subdirs = self.build_subdirs(subdir, second_field, uplink, image)
                if not uplink:
                    subdirs = [".."] + subdirs
            else:
                subdirs = self.build_subdirs(subdir, fname, uplink, image)
        else:
            subdirs = self.build_subdirs(subdir, fname, uplink, image)
        return "/".join(subdirs + [fname])

    def create_file(self, fname, subdir=None, ext=None):
        """
        will create filename given

        @param: fname  -- Filename to be created
        @param: subdir -- A subdir to be added to filename
        @param: ext    -- An extension to be added to filename
        """
        if ext is None:
            ext = self.ext
        if self.usecms and not subdir:
            if self.the_lang:
                if ext != "index":
                    target = os.path.join(self.target_uri, self.the_lang)
                    self.cur_fname = os.path.join(target, fname) + ext
                else:
                    self.cur_fname = os.path.join(self.target_uri, fname) + self.ext
            else:
                self.cur_fname = os.path.join(self.target_uri, fname) + ext
        else:
            if self.the_lang and self.archive:
                if subdir:
                    if not self.usecms:
                        subdir = os.path.join(self.the_lang, subdir)
                elif ext != "index":
                    fname = os.path.join(self.the_lang, fname)
            if subdir:
                subdir = self.build_path(subdir, fname)
                self.cur_fname = os.path.join(subdir, fname) + ext
            else:
                if ext == "index":
                    self.cur_fname = os.path.join(fname) + self.ext
                else:
                    self.cur_fname = fname + ext
        if self.archive:
            string_io = BytesIO()
            output_file = TextIOWrapper(
                string_io, encoding=self.encoding, errors="xmlcharrefreplace"
            )
        else:
            string_io = None
            if subdir:
                if self.the_lang:
                    subdir = os.path.join(self.html_dir, self.the_lang, subdir)
                else:
                    subdir = os.path.join(self.html_dir, subdir)
            else:
                if self.the_lang:
                    subdir = os.path.join(self.html_dir, self.the_lang)
                else:
                    subdir = os.path.join(self.html_dir)
            if self.the_lang:
                if ext == "index":
                    self.cur_fname = os.path.join(fname) + self.ext
                    fname = os.path.join(self.html_dir, self.cur_fname)
                else:
                    fname = os.path.join(self.html_dir, self.the_lang, self.cur_fname)
            else:
                fname = os.path.join(self.html_dir, self.cur_fname)
            dir_name = os.path.dirname(fname)
            if not os.path.isdir(dir_name):
                os.makedirs(dir_name)
            output_file = open(
                fname, "w", encoding=self.encoding, errors="xmlcharrefreplace"
            )
        return (output_file, string_io)

    def close_file(self, output_file, string_io, date):
        """
        will close any file passed to it

        @param: output_file -- The output file to flush
        @param: string_io   -- The string IO used when we are in archive mode
        @param: date        -- The last modification date for this object
                               If we have "zero", we use the current time.
                               This is related to bug #8950 and very useful
                               when we use rsync.
        """
        if self.archive:
            if self.cur_fname not in self.archive.getnames():
                # The current file not already archived.
                output_file.flush()
                tarinfo = tarfile.TarInfo(self.cur_fname)
                tarinfo.size = len(string_io.getvalue())
                tarinfo.mtime = date if date != 0 else time.time()
                if not win():
                    tarinfo.uid = os.getuid()
                    tarinfo.gid = os.getgid()
                string_io.seek(0)
                self.archive.addfile(tarinfo, string_io)
            output_file.close()
        else:
            output_file.close()
            if date is not None and date > 0:
                os.utime(output_file.name, (date, date))

    def prepare_copy_media(self, photo):
        """
        prepares a media object to copy

        @param: photo -- The photo for which we need a real path
                         and a thumbnail path
        """
        handle = photo.get_handle()
        ext = os.path.splitext(photo.get_path())[1]
        real_path = os.path.join(
            self.build_path("images", handle, uplink=2, image=True), handle + ext
        )
        thumb_path = os.path.join(
            self.build_path("thumb", handle, uplink=2, image=True), handle + ".png"
        )
        return real_path, thumb_path

    def copy_file(self, from_fname, to_fname, to_dir=""):
        """
        Copy a file from a source to a (report) destination.
        If to_dir is not present and if the target is not an archive,
        then the destination directory will be created.

        @param: from_fname -- The path of the file to copy.
        @param: to_fname   -- Will be just a filename, without directory path.
        @param: to_dir     -- Is the relative path name in the destination root.
                              It will be prepended before 'to_fname'.
        """
        if self.usecms:
            to_dir = "/".join([self.target_uri, to_dir])
        LOG.debug("copying '%s' to '%s/%s'", from_fname, to_dir, to_fname)
        mtime = os.stat(from_fname).st_mtime
        if self.archive:

            def set_mtime(tarinfo):
                """
                For each file, we set the last modification time.

                We could also set uid, gid, uname, gname and mode
                #tarinfo.uid = os.getuid()
                #tarinfo.mode = 0660
                #tarinfo.uname = tarinfo.gname = "www-data"
                """
                tarinfo.mtime = mtime
                return tarinfo

            dest = os.path.join(to_dir, to_fname)
            if dest not in self.archive.getnames():
                # The current file not already archived.
                self.archive.add(from_fname, dest, filter=set_mtime)
        else:
            dest = os.path.join(self.html_dir, to_dir, to_fname)

            destdir = os.path.dirname(dest)
            if not os.path.isdir(destdir):
                os.makedirs(destdir)

            if from_fname != dest:
                if not os.path.exists(dest):
                    try:
                        shutil.copyfile(from_fname, dest)
                        os.utime(dest, (mtime, mtime))
                    except Exception as exception:
                        LOG.exception(exception)
                        print("Copying error: %s" % sys.exc_info()[1])
                        print("Continuing...")
            elif self.warn_dir:
                self.user.warn(
                    _("Possible destination error")
                    + "\n"
                    + _(
                        "You appear to have set your target directory "
                        "to a directory used for data storage. This "
                        "could create problems with file management. "
                        "It is recommended that you consider using "
                        "a different directory to store your generated "
                        "web pages."
                    )
                )
                self.warn_dir = False

    def person_in_webreport(self, person_handle):
        """
        Return the handle if we created a page for this person.

        @param: person_handle -- The person we are looking for
        """
        return person_handle in self.obj_dict[Person]

    def pgrs_title(self, the_lang):
        """Set the user progress popup message depending on the lang."""
        if the_lang:
            languages = glocale.get_language_dict()
            lang = "???"
            for language in languages:
                if languages[language] == the_lang:
                    lang = language
                    break
            return _("Narrative Website Report for the %s language") % lang
        else:
            return _("Narrative Website Report")


#################################################
#
#    Creates the NarrativeWeb Report Menu Options
#
#################################################
class NavWebOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dbase):
        """
        @param: name  -- The name of the report
        @param: dbase -- The Gramps database instance
        """
        self.__db = dbase
        self.__archive = None
        self.__target = None
        self.__target_uri = None
        self.__pid = None
        self.__filter = None
        self.__graph = None
        self.__graphgens = None
        self.__living = None
        self.__yearsafterdeath = None
        self.__usecms = None
        self.__cms_uri = None
        self.__usecal = None
        self.__calendar_uri = None
        self.__create_thumbs_only = None
        self.__create_images_index = None
        self.__create_thumbs_index = None
        self.__mapservice = None
        self.__maxinitialimagewidth = None
        self.__citationreferents = None
        self.__incdownload = None
        self.__max_download = 4  # Add 1 to this counter: In reality 3 downloads
        self.__nbdownload = None
        self.__dl_descr = {}
        self.__down_fname = {}
        self.__placemappages = None
        self.__familymappages = None
        self.__stamenopts = None
        self.__googleopts = None
        self.__googlemapkey = None
        self.__stamenmapkey = None
        self.__olv = None
        self.googlemapkeyhelp = None
        self.stamenmapkeyhelp = None
        self.__ancestortree = None
        self.__css = None
        self.__gallery = None
        self.__updates = None
        self.__maxdays = None
        self.__maxupdates = None
        self.__unused = None
        self.__navigation = None
        self.__securesite = False
        self.__extra_page_name = None
        self.__extra_page = None
        self.__relation = False
        self.__prevnext = False
        self.__multitrans = False
        self.__lang_2 = None
        self.__lang_3 = None
        self.__lang_4 = None
        self.__lang_5 = None
        self.__lang_6 = None
        self.__titl_2 = None
        self.__titl_3 = None
        self.__titl_4 = None
        self.__titl_5 = None
        self.__titl_6 = None
        self.__start_dow = None
        self.__maiden_name = None
        self.__makeoneday = None
        self.__birthdays = None
        self.__anniv = None
        self.__alive = None
        self.__toggle = None
        self.__death_anniv = None
        self.__after_year = None
        self.__ext = None
        self.__phpnote = None
        db_options = name + " " + dbase.get_dbname()
        MenuReportOptions.__init__(self, db_options, dbase)

    def add_menu_options(self, menu):
        """
        Add options to the menu for the website.

        @param: menu -- The menu for which we add options
        """
        self.__add_report_options(menu)
        self.__add_report_html(menu)
        self.__add_report_display(menu)
        self.__add_page_generation_options(menu)
        self.__add_more_pages(menu)
        self.__add_images_generation_options(menu)
        self.__add_download_options(menu)
        self.__add_advanced_options(menu)
        self.__add_advanced_options_2(menu)
        self.__add_place_map_options(menu)
        self.__add_others_options(menu)
        self.__add_translations(menu)
        self.__add_calendar_options(menu)

    def __add_report_options(self, menu):
        """
        Options on the "Report Options" tab.

        @param: menu -- The menu for which we add options
        """
        category_name = _("Report Options")
        addopt = partial(menu.add_option, category_name)

        self.__archive = BooleanOption(_("Store website in .tar.gz archive"), False)
        self.__archive.set_help(_("Whether to store the website in an " "archive file"))
        addopt("archive", self.__archive)
        self.__archive.connect("value-changed", self.__archive_changed)

        dbname = self.__db.get_dbname()
        default_dir = dbname + "_" + "NAVWEB"
        self.__target = DestinationOption(
            _("Destination"),
            os.path.join(config.get("paths.website-directory"), default_dir),
        )
        self.__target.set_help(_("The destination directory for the web " "files"))
        addopt("target", self.__target)

        self.__archive_changed()

        title = StringOption(_("Website title"), _("My Family Tree"))
        title.set_help(_("The title of the website"))
        addopt("title", title)

        self.__filter = FilterOption(_("Filter"), 0)
        self.__filter.set_help(
            _("Select filter to restrict people that appear on the website")
        )
        addopt("filter", self.__filter)
        self.__filter.connect("value-changed", self.__filter_changed)

        self.__pid = PersonOption(_("Filter Person"))
        self.__pid.set_help(_("The center person for the filter"))
        addopt("pid", self.__pid)
        self.__pid.connect("value-changed", self.__update_filters)

        self.__relation = BooleanOption(
            _(
                "Show the relationship between the "
                "current person and the active person"
            ),
            False,
        )
        self.__relation.set_help(
            _(
                "For each person page, show the relationship"
                " between this person and the active person."
            )
        )
        addopt("relation", self.__relation)

        self.__pid.connect("value-changed", self.__update_filters)

        self.__update_filters()

        stdoptions.add_living_people_option(menu, category_name)
        stdoptions.add_private_data_option(menu, category_name, default=False)

        addopt = partial(menu.add_option, category_name)

    def __add_report_html(self, menu):
        """
        Html Options for the Report.

        @param: menu -- The menu for which we add options
        """
        category_name = _("HTML Options")
        addopt = partial(menu.add_option, category_name)

        self.__ext = EnumeratedListOption(_("File extension"), ".html")
        for etype in _WEB_EXT:
            self.__ext.add_item(etype, etype)
        self.__ext.set_help(_("The extension to be used for the web files"))
        addopt("ext", self.__ext)
        self.__ext.connect("value-changed", self.__ext_changed)

        cright = EnumeratedListOption(_("Copyright"), 0)
        for index, copt in enumerate(_COPY_OPTIONS):
            cright.add_item(index, copt)
        cright.set_help(_("The copyright to be used for the web files"))
        addopt("cright", cright)

        self.__css = EnumeratedListOption(_("StyleSheet"), CSS["Basic-Ash"]["id"])
        for dummy_fname, gid in sorted(
            [(CSS[key]["translation"], CSS[key]["id"]) for key in list(CSS.keys())]
        ):
            if CSS[gid]["user"]:
                self.__css.add_item(CSS[gid]["id"], CSS[gid]["translation"])
        self.__css.set_help(_("The default stylesheet to be used for" " the pages"))
        addopt("css", self.__css)
        self.__css.connect("value-changed", self.__stylesheet_changed)

        _nav_opts = [
            (_("Horizontal -- Default"), "Horizontal"),
            (_("Vertical   -- Left Side"), "Vertical"),
            (_("Fade       -- WebKit Browsers Only"), "Fade"),
            (_("Drop-Down  -- WebKit Browsers Only"), "dropdown"),
        ]
        self.__navigation = EnumeratedListOption(
            _("Navigation Menu Layout"), _nav_opts[0][1]
        )
        for layout in _nav_opts:
            self.__navigation.add_item(layout[1], layout[0])
        self.__navigation.set_help(
            _("Choose which layout " "for the Navigation Menus.")
        )
        addopt("navigation", self.__navigation)

        self.__stylesheet_changed()

        _cit_opts = [
            (_("Normal Outline Style"), "Outline"),
            (_("Drop-Down  -- WebKit Browsers Only"), "DropDown"),
        ]
        self.__citationreferents = EnumeratedListOption(
            _("Citation Referents Layout"), _cit_opts[0][1]
        )
        for layout in _cit_opts:
            self.__citationreferents.add_item(layout[1], layout[0])
        self.__citationreferents.set_help(
            _(
                "Determine the default layout for the "
                "Source Page's Citation Referents section"
            )
        )
        addopt("citationreferents", self.__citationreferents)

        self.__ancestortree = BooleanOption(_("Include ancestor's tree"), True)
        self.__ancestortree.set_help(
            _("Whether to include an ancestor " "graph on each individual page")
        )
        addopt("ancestortree", self.__ancestortree)
        self.__ancestortree.connect("value-changed", self.__graph_changed)

        self.__prevnext = BooleanOption(_("Add previous/next"), False)
        self.__prevnext.set_help(_("Add previous/next to the navigation bar."))
        addopt("prevnext", self.__prevnext)

        self.__securesite = BooleanOption(_("This is a secure site (HTTPS)"), False)
        self.__securesite.set_help(_("Whether to use http:// or https://"))
        addopt("securesite", self.__securesite)

        self.__toggle = BooleanOption(_("Toggle sections"), False)
        self.__toggle.set_help(_("Check it if you want to open/close" " a section"))
        addopt("toggle", self.__toggle)

    def __add_more_pages(self, menu):
        """
        Add more extra pages to the report

        @param: menu -- The menu for which we add options
        """
        category_name = _("Extra Pages")
        addopt = partial(menu.add_option, category_name)
        default_path_name = config.get("paths.website-extra-page-name")
        self.__extra_page_name = StringOption(_("Extra page name"), default_path_name)
        self.__extra_page_name.set_help(
            _("Your extra page name like it is shown in the menubar")
        )
        self.__extra_page_name.connect("value-changed", self.__extra_page_name_changed)
        addopt("extrapagename", self.__extra_page_name)
        default_path = config.get("paths.website-extra-page-uri")
        self.__extra_page = DestinationOption(_("Your extra page path"), default_path)
        self.__extra_page.set_help(_("Your extra page path without extension"))
        self.__extra_page.connect("value-changed", self.__extra_page_changed)
        addopt("extrapage", self.__extra_page)

    def __add_report_display(self, menu):
        """
        How to display names, datyes, ...

        @param: menu -- The menu for which we add options
        """
        category_name = _("Display")
        addopt = partial(menu.add_option, category_name)

        stdoptions.add_name_format_option(menu, category_name)

        self.__multitrans = BooleanOption(_("Do we use multiple translations?"), False)
        self.__multitrans.set_help(
            _(
                "Whether to display the narrative web in multiple languages."
                "\nSee the translation tab to add new languages to the default"
                " one defined in the next field."
            )
        )
        addopt("multitrans", self.__multitrans)
        self.__multitrans.connect("value-changed", self.__activate_translations)

        locale_opt = stdoptions.add_localization_option(menu, category_name)
        stdoptions.add_date_format_option(menu, category_name, locale_opt)

        stdoptions.add_gramps_id_option(menu, category_name)
        stdoptions.add_tags_option(menu, category_name)

        birthorder = BooleanOption(_("Sort all children in birth order"), False)
        birthorder.set_help(
            _("Whether to display children in birth order or in entry order.")
        )
        addopt("birthorder", birthorder)

        coordinates = BooleanOption(
            _("Do we display coordinates in the places list?"), False
        )
        coordinates.set_help(
            _("Whether to display latitude/longitude in the places list.")
        )
        addopt("coordinates", coordinates)

        reference_sort = BooleanOption(
            _("Sort places references either by date or by name"), False
        )
        reference_sort.set_help(
            _(
                "Sort the places references by date or by name."
                " Not set means by date."
            )
        )
        addopt("reference_sort", reference_sort)

        self.__graphgens = NumberOption(_("Graph generations"), 4, 2, 20)
        self.__graphgens.set_help(
            _("The number of generations to include in " "the ancestor graph")
        )
        addopt("graphgens", self.__graphgens)
        self.__graph_changed()

        notes = BooleanOption(
            _("Include narrative notes just after name, gender"), True
        )
        notes.set_help(
            _(
                "Include narrative notes just after name, gender and"
                " age at death (default) or include them just before"
                " attributes."
            )
        )
        addopt("notes", notes)

    def __add_page_generation_options(self, menu):
        """
        Options on the "Page Generation" tab.

        @param: menu -- The menu for which we add options
        """
        category_name = _("Page Generation")
        addopt = partial(menu.add_option, category_name)

        homenote = NoteOption(_("Home page note"))
        homenote.set_help(_("A note to be used on the home page"))
        addopt("homenote", homenote)

        homeimg = MediaOption(_("Home page image"))
        homeimg.set_help(_("An image to be used on the home page"))
        addopt("homeimg", homeimg)

        intronote = NoteOption(_("Introduction note"))
        intronote.set_help(_("A note to be used as the introduction"))
        addopt("intronote", intronote)

        introimg = MediaOption(_("Introduction image"))
        introimg.set_help(_("An image to be used as the introduction"))
        addopt("introimg", introimg)

        contactnote = NoteOption(_("Publisher contact note"))
        contactnote.set_help(
            _(
                "A note to be used as the publisher contact."
                "\nIf no publisher information is given,"
                "\nno contact page will be created"
            )
        )
        addopt("contactnote", contactnote)

        contactimg = MediaOption(_("Publisher contact image"))
        contactimg.set_help(
            _(
                "An image to be used as the publisher contact."
                "\nIf no publisher information is given,"
                "\nno contact page will be created"
            )
        )
        addopt("contactimg", contactimg)

        headernote = NoteOption(_("HTML user header"))
        headernote.set_help(
            _("A note to be used as the page header" " or a PHP code to insert.")
        )
        addopt("headernote", headernote)

        footernote = NoteOption(_("HTML user footer"))
        footernote.set_help(_("A note to be used as the page footer"))
        addopt("footernote", footernote)

        # This option will be available only if you select ".php" in the
        # "File extension" from the "Html" tab
        self.__phpnote = NoteOption(_("PHP user session"))
        self.__phpnote.set_help(
            _(
                "A note to use for starting the php session."
                "\nThis option will be available only if "
                "the .php file extension is selected."
            )
        )
        addopt("phpnote", self.__phpnote)

    def __add_images_generation_options(self, menu):
        """
        Options on the "Page Generation" tab.

        @param: menu -- The menu for which we add options
        """
        category_name = _("Images Generation")
        addopt = partial(menu.add_option, category_name)

        self.__gallery = BooleanOption(_("Include images and media objects"), True)
        self.__gallery.set_help(_("Whether to include " "a gallery of media objects"))
        addopt("gallery", self.__gallery)
        self.__gallery.connect("value-changed", self.__gallery_changed)

        self.__create_images_index = BooleanOption(_("Create the images index"), False)
        self.__create_images_index.set_help(
            _("This option allows you to create the images index")
        )
        addopt("create_images_index", self.__create_images_index)
        self.__create_images_index.connect("value-changed", self.__gallery_changed)

        self.__unused = BooleanOption(
            _("Include unused images and media objects"), False
        )
        self.__unused.set_help(
            _("Whether to include unused or unreferenced" " media objects")
        )
        addopt("unused", self.__unused)

        self.__create_thumbs_only = BooleanOption(
            _("Create and only use thumbnail- sized images"), False
        )
        self.__create_thumbs_only.set_help(
            _(
                "This option allows you to create only thumbnail images "
                "instead of the full-sized images on the Media Page. "
                "This will allow you to have a much "
                "smaller total upload size to your web hosting site."
            )
        )
        addopt("create_thumbs_only", self.__create_thumbs_only)
        self.__create_thumbs_only.connect("value-changed", self.__gallery_changed)

        self.__create_thumbs_index = BooleanOption(
            _("Create the thumbnail index"), False
        )
        self.__create_thumbs_index.set_help(
            _("This option allows you to create the thumbnail index")
        )
        addopt("create_thumbs_index", self.__create_thumbs_index)
        self.__create_thumbs_index.connect("value-changed", self.__gallery_changed)

        self.__maxinitialimagewidth = NumberOption(
            _("Max width of initial image"), _DEFAULT_MAX_IMG_WIDTH, 0, 2000
        )
        self.__maxinitialimagewidth.set_help(
            _(
                "This allows you to set the maximum width "
                "of the image shown on the media page."
            )
        )
        addopt("maxinitialimagewidth", self.__maxinitialimagewidth)

        self.__gallery_changed()

    def __add_download_options(self, menu):
        """
        Options for the download tab ...

        @param: menu -- The menu for which we add options
        """
        category_name = _("Download")
        addopt = partial(menu.add_option, category_name)

        self.__incdownload = BooleanOption(_("Include download page"), False)
        self.__incdownload.set_help(_("Whether to include a database download option"))
        addopt("incdownload", self.__incdownload)
        self.__incdownload.connect("value-changed", self.__download_changed)

        self.__nbdownload = NumberOption(
            _("How many downloads"), 2, 1, self.__max_download - 1
        )
        self.__nbdownload.set_help(
            _("The number of download files to include " "in the download page")
        )
        addopt("nbdownload", self.__nbdownload)
        self.__nbdownload.connect("value-changed", self.__download_changed)

        for count in range(1, self.__max_download):
            fnamex = "down_fname%c" % str(count)
            descrx = "dl_descr%c" % str(count)
            wdir = os.path.join(config.get("paths.website-directory"), "")
            __down_fname = DestinationOption(
                _("Download Filename #%c") % str(count), wdir
            )
            __down_fname.set_help(_("File to be used for downloading of database"))
            addopt(fnamex, __down_fname)
            self.__down_fname[count] = __down_fname

            __dl_descr = StringOption(
                _("Description for download"), _("Family Tree #%c") % str(count)
            )
            __dl_descr.set_help(_("Give a description for this file."))
            addopt(descrx, __dl_descr)
            self.__dl_descr[count] = __dl_descr

        self.__download_changed()

    def __add_advanced_options(self, menu):
        """
        Options on the "Advanced" tab.

        @param: menu -- The menu for which we add options
        """
        category_name = _("Advanced Options")
        addopt = partial(menu.add_option, category_name)

        encoding = EnumeratedListOption(
            _("Character set encoding"), _CHARACTER_SETS[0][1]
        )
        for eopt in _CHARACTER_SETS:
            encoding.add_item(eopt[1], eopt[0])
        encoding.set_help(_("The encoding to be used for the web files"))
        addopt("encoding", encoding)

        linkhome = BooleanOption(
            _("Include link to active person on every page"), False
        )
        linkhome.set_help(
            _("Include a link to the active person (if they have a webpage)")
        )
        addopt("linkhome", linkhome)

        showbirth = BooleanOption(
            _("Include a column for birth dates on the index pages"), True
        )
        showbirth.set_help(_("Whether to include a birth column"))
        addopt("showbirth", showbirth)

        showdeath = BooleanOption(
            _("Include a column for death dates on the index pages"), False
        )
        showdeath.set_help(_("Whether to include a death column"))
        addopt("showdeath", showdeath)

        showpartner = BooleanOption(
            _("Include a column for partners on the " "index pages"), False
        )
        showpartner.set_help(_("Whether to include a partners column"))
        menu.add_option(category_name, "showpartner", showpartner)

        showparents = BooleanOption(
            _("Include a column for parents on the " "index pages"), False
        )
        showparents.set_help(_("Whether to include a parents column"))
        addopt("showparents", showparents)

        showallsiblings = BooleanOption(
            _("Include half and/or step-siblings on the individual pages"), False
        )
        showallsiblings.set_help(
            _(
                "Whether to include half and/or "
                "step-siblings with the parents and siblings"
            )
        )
        addopt("showhalfsiblings", showallsiblings)

    def __add_advanced_options_2(self, menu):
        """
        Continue options on the "Advanced" tab.

        @param: menu -- The menu for which we add options
        """
        category_name = _("Include")
        addopt = partial(menu.add_option, category_name)

        inc_families = BooleanOption(_("Include family pages"), False)
        inc_families.set_help(_("Whether or not to include family pages."))
        addopt("inc_families", inc_families)

        inc_events = BooleanOption(_("Include event pages"), False)
        inc_events.set_help(_("Add a complete events list and relevant pages or not"))
        addopt("inc_events", inc_events)

        inc_places = BooleanOption(_("Include place pages"), False)
        inc_places.set_help(_("Whether or not to include the place pages."))
        addopt("inc_places", inc_places)

        inc_uplaces = BooleanOption(_("Include unused place pages"), False)
        inc_uplaces.set_help(_("Whether or not to include the unused place pages."))
        addopt("inc_uplaces", inc_uplaces)

        inc_sources = BooleanOption(_("Include source pages"), False)
        inc_sources.set_help(_("Whether or not to include the source pages."))
        addopt("inc_sources", inc_sources)

        inc_repository = BooleanOption(_("Include repository pages"), False)
        inc_repository.set_help(_("Whether or not to include the repository pages."))
        addopt("inc_repository", inc_repository)

        inc_gendex = BooleanOption(_("Include GENDEX file (/gendex.txt)"), False)
        inc_gendex.set_help(_("Whether to include a GENDEX file or not"))
        addopt("inc_gendex", inc_gendex)

        inc_addressbook = BooleanOption(_("Include address book pages"), False)
        inc_addressbook.set_help(
            _(
                "Whether or not to add Address Book pages,"
                "which can include e-mail and website "
                "addresses and personal address/ residence "
                "events."
            )
        )
        addopt("inc_addressbook", inc_addressbook)

        inc_statistics = BooleanOption(_("Include the statistics page"), False)
        inc_statistics.set_help(_("Whether or not to add statistics page"))
        addopt("inc_stats", inc_statistics)

    def __add_place_map_options(self, menu):
        """
        options for the Place Map tab.

        @param: menu -- The menu for which we add options
        """
        category_name = _("Place Map Options")
        addopt = partial(menu.add_option, category_name)

        mapopts = [
            [_("OpenStreetMap"), "OpenStreetMap"],
            [_("Stamen Map"), "StamenMap"],
            [_("Google"), "Google"],
        ]
        self.__mapservice = EnumeratedListOption(_("Map Service"), mapopts[0][1])
        for trans, opt in mapopts:
            self.__mapservice.add_item(opt, trans)
        self.__mapservice.set_help(
            _("Choose your choice of map service for " "creating the Place Map Pages.")
        )
        self.__mapservice.connect("value-changed", self.__placemap_options)
        addopt("mapservice", self.__mapservice)

        self.__placemappages = BooleanOption(
            _("Include Place map on Place Pages"), False
        )
        self.__placemappages.set_help(
            _(
                "Whether to include a place map on the Place Pages, "
                "where Latitude/ Longitude are available."
            )
        )
        self.__placemappages.connect("value-changed", self.__placemap_options)
        addopt("placemappages", self.__placemappages)

        self.__familymappages = BooleanOption(
            _("Include Family Map Pages with " "all places shown on the map"), False
        )
        self.__familymappages.set_help(
            _(
                "Whether or not to add an individual page map "
                "showing all the places on this page. "
                "This will allow you to see how your family "
                "traveled around the country."
            )
        )
        self.__familymappages.connect("value-changed", self.__placemap_options)
        addopt("familymappages", self.__familymappages)

        googleopts = [
            (_("Family Links"), "FamilyLinks"),
            (_("Drop"), "Drop"),
            (_("Markers"), "Markers"),
        ]
        self.__googleopts = EnumeratedListOption(
            _("Google/ FamilyMap Option"), googleopts[0][1]
        )
        for trans, opt in googleopts:
            self.__googleopts.add_item(opt, trans)
        self.__googleopts.set_help(
            _(
                "Select which option that you would like "
                "to have for the Google Maps family-map pages..."
            )
        )
        addopt("googleopts", self.__googleopts)

        self.__googlemapkey = StringOption(_("Google maps API key"), "")
        self.__googlemapkey.set_help(
            _(
                "The API key used for the Google maps.\n"
                "This key is mandatory and must be valid"
            )
        )
        if not config.is_set("paths.website-get-api-key"):
            # The following will be used to change the URL if it changes without
            # creating a patch. We will only need to change gramps.ini
            config.register(
                "paths.website-get-api-key",
                "https://developers.google.com/maps/documentation/javascript/get-api-key",
            )
        keyvalue = config.get("paths.website-get-api-key")
        self.googlemapkeyhelp = StringOption(_("How to get the API key"), keyvalue)
        self.googlemapkeyhelp.connect("value-changed", self.url_changed)
        keytooltip = _(
            "Copy and paste this value in your browser."
            "\nThe Google maps service must be selected."
        )
        self.googlemapkeyhelp.set_help(keytooltip)
        addopt("googlemapkey", self.__googlemapkey)
        addopt("googlemapkeyhelp", self.googlemapkeyhelp)

        stamenopts = [
            (_("Toner"), "toner"),
            (_("Terrain"), "terrain"),
            (_("WaterColor"), "watercolor"),
        ]
        self.__stamenopts = EnumeratedListOption(_("Stamen Option"), stamenopts[0][1])
        for trans, opt in stamenopts:
            self.__stamenopts.add_item(opt, trans)
        self.__stamenopts.set_help(
            _(
                "Select which option that you would like "
                "to have for the Stamen map map-pages..."
            )
        )
        addopt("stamenopts", self.__stamenopts)
        self.__stamenmapkey = StringOption(_("Stamen maps API key"), "")
        self.__stamenmapkey.set_help(
            _(
                "The API key used for the Stamen maps.\n"
                "This key is mandatory and must be valid"
            )
        )
        if not config.is_set("paths.stamen-get-api-key"):
            # The following will be used to change the URL if it changes without
            # creating a patch. We will only need to change gramps.ini
            config.register(
                "paths.stamen-get-api-key",
                "https://stadiamaps.com/stamen/onboarding",
            )
        keyvalue = config.get("paths.stamen-get-api-key")
        self.stamenmapkeyhelp = StringOption(_("How to get the API key"), keyvalue)
        self.stamenmapkeyhelp.connect("value-changed", self.url_changed)
        keytooltip = _(
            "Copy and paste this value in your browser."
            "\nThe Stamen maps service must be selected."
        )
        self.stamenmapkeyhelp.set_help(keytooltip)
        addopt("stamenmapkey", self.__stamenmapkey)
        addopt("stamenmapkeyhelp", self.stamenmapkeyhelp)

        self.__placemap_options()

        openlayers = "external_modules.openlayers_version"
        last_ok_version = "v6.15.1"
        if not config.is_set(openlayers):
            config.register(openlayers, last_ok_version)
        openlayers = "external_modules.openlayers_version"
        olv = config.get(openlayers)
        inipath = os.path.join(VERSION_DIR, "gramps.ini")
        olv = [
            (_("in %(inipth)s (%(val)s)" % {"inipth": inipath, "val": olv}), olv),
            (_("latest"), "latest"),
        ]
        self.__olv = EnumeratedListOption(_("openlayers version to use"), olv[0][1])
        for trans, opt in olv:
            self.__olv.add_item(opt, trans)
        self.__olv.set_help(
            _(
                "You should use this option only if you can't see "
                "the maps in your website for OpenStreetMap or Stamen maps"
                "\nYou can change the value in the specified file."
                " The option name to modify is openlayers_version."
                "\nSee OLDER VERSIONS in https://openlayers.org/"
            )
        )
        addopt("ol_version", self.__olv)

        coord_format = stdoptions.add_coordinates_format_option(menu, category_name)

    def __add_others_options(self, menu):
        """
        Options for the cms tab, web calendar inclusion, PHP ...

        @param: menu -- The menu for which we add options
        """
        category_name = _("Other inclusion (CMS, web calendar, PHP)")
        addopt = partial(menu.add_option, category_name)

        self.__usecms = BooleanOption(
            _("Do we include these pages in a CMS web?"), False
        )
        self.__usecms.connect("value-changed", self.__usecms_changed)
        addopt("usecms", self.__usecms)

        default_dir = "/NAVWEB"
        self.__cms_uri = DestinationOption(
            _("URI"), os.path.join(config.get("paths.website-cms-uri"), default_dir)
        )
        self.__cms_uri.set_help(_("Where do you place your website? default = /NAVWEB"))
        self.__cms_uri.connect("value-changed", self.__cms_uri_changed)
        addopt("cmsuri", self.__cms_uri)

        self.__cms_uri_changed()

        self.__graph_changed()

        self.__updates = BooleanOption(_("Include the news and updates page"), True)
        self.__updates.set_help(_("Whether to include " "a page with the last updates"))
        self.__updates.connect("value-changed", self.__updates_changed)
        addopt("updates", self.__updates)

        self.__maxdays = NumberOption(_("Max days for updates"), 1, 1, 300)
        self.__maxdays.set_help(
            _("You want to see the last updates on how" " many days?")
        )
        addopt("maxdays", self.__maxdays)

        self.__maxupdates = NumberOption(
            _("Max number of updates per object" " to show"), 1, 1, 100
        )
        self.__maxupdates.set_help(_("How many updates do you want to see max"))
        addopt("maxupdates", self.__maxupdates)

    def __add_translations(self, menu):
        """
        Options for selecting multiple languages. The default one is
        displayed in the display tab. If the option "use multiple
        languages" is not selected, all the fields in this menu will be
        grayed out.

        @param: menu -- The menu for which we add options
        """
        category_name = _("Translations")
        addopt = partial(menu.add_option, category_name)

        mess = _("Second language")
        self.__lang_2 = stdoptions.add_extra_localization_option(
            menu, category_name, mess, "lang2"
        )
        self.__titl_2 = StringOption(
            _("Site name for your second language"), _("This site title")
        )
        self.__titl_2.set_help(_("Enter a title in the respective language"))
        addopt("title2", self.__titl_2)
        mess = _("Third language")
        self.__lang_3 = stdoptions.add_extra_localization_option(
            menu, category_name, mess, "lang3"
        )
        self.__titl_3 = StringOption(
            _("Site name for your third language"), _("This site title")
        )
        self.__titl_3.set_help(_("Enter a title in the respective language"))
        addopt("title3", self.__titl_3)
        mess = _("Fourth language")
        self.__lang_4 = stdoptions.add_extra_localization_option(
            menu, category_name, mess, "lang4"
        )
        self.__titl_4 = StringOption(
            _("Site name for your fourth language"), _("This site title")
        )
        self.__titl_4.set_help(_("Enter a title in the respective language"))
        addopt("title4", self.__titl_4)
        mess = _("Fifth language")
        self.__lang_5 = stdoptions.add_extra_localization_option(
            menu, category_name, mess, "lang5"
        )
        self.__titl_5 = StringOption(
            _("Site name for your fifth language"), _("This site title")
        )
        self.__titl_5.set_help(_("Enter a title in the respective language"))
        addopt("title5", self.__titl_5)
        mess = _("Sixth language")
        self.__lang_6 = stdoptions.add_extra_localization_option(
            menu, category_name, mess, "lang6"
        )
        self.__titl_6 = StringOption(
            _("Site name for your sixth language"), _("This site title")
        )
        self.__titl_6.set_help(_("Enter a title in the respective language"))
        addopt("title6", self.__titl_6)

    def __activate_translations(self):
        """
        Make the possible extra languages selectable.
        """
        status = self.__multitrans.get_value()
        self.__lang_2.set_available(status)
        self.__titl_2.set_available(status)
        self.__lang_3.set_available(status)
        self.__titl_3.set_available(status)
        self.__lang_4.set_available(status)
        self.__titl_4.set_available(status)
        self.__lang_5.set_available(status)
        self.__titl_5.set_available(status)
        self.__lang_6.set_available(status)
        self.__titl_6.set_available(status)

    def __updates_changed(self):
        """
        Update the change of storage: archive or directory
        """
        _updates_option = self.__updates.get_value()
        if _updates_option:
            self.__maxupdates.set_available(True)
            self.__maxdays.set_available(True)
        else:
            self.__maxupdates.set_available(False)
            self.__maxdays.set_available(False)

    def __ext_changed(self):
        """
        The file extension changed.
        If .php selected, we must set the PHP user session available
        """
        if self.__ext.get_value()[:4] == ".php":
            self.__phpnote.set_available(True)
        else:
            self.__phpnote.set_available(False)

    def __usecms_changed(self):
        """
        We need to use CMS or not
        If we use a CMS, the storage must be an archive
        """
        if self.__usecms.get_value():
            self.__archive.set_value(True)
        self.__target_uri = self.__cms_uri.get_value()

    def __cms_uri_changed(self):
        """
        Update the change of storage: archive or directory
        """
        self.__target_uri = self.__cms_uri.get_value()

    def __extra_page_name_changed(self):
        """
        Update the change of the extra page name
        """
        extra_page_name = self.__extra_page_name.get_value()
        if extra_page_name != "":
            config.set("paths.website-extra-page-name", extra_page_name)

    def __extra_page_changed(self):
        """
        Update the change of the extra page without extension
        """
        extra_page = self.__extra_page.get_value()
        if extra_page != "":
            config.set("paths.website-extra-page-uri", extra_page)

    def __archive_changed(self):
        """
        Update the change of storage: archive or directory
        """
        if self.__archive.get_value() is True:
            self.__target.set_extension(".tar.gz")
            self.__target.set_directory_entry(False)
        else:
            self.__target.set_directory_entry(True)
            # We don't use an archive. If usecms is True, set it to False
            if self.__usecms:
                self.__usecms.set_value(False)

    def __update_filters(self):
        """
        Update the filter list based on the selected person
        """
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        filter_list = utils.get_person_filters(person, include_single=False)
        self.__filter.set_filters(filter_list)

    def __filter_changed(self):
        """
        Handle filter change. If the filter is not specific to a person,
        disable the "Person" option
        """
        filter_value = self.__filter.get_value()
        if filter_value == 0:  # "Entire Database" (as "include_single=False")
            self.__pid.set_available(False)
        else:
            # The other filters need a center person (assume custom ones too)
            self.__pid.set_available(True)

    def __stylesheet_changed(self):
        """
        Handles the changing nature of the stylesheet
        """
        css_opts = self.__css.get_value()
        if CSS[css_opts]["navigation"]:
            self.__navigation.set_available(True)
        else:
            self.__navigation.set_available(False)
            self.__navigation.set_value("Horizontal")

    def __graph_changed(self):
        """
        Handle enabling or disabling the ancestor graph
        """
        self.__graphgens.set_available(self.__ancestortree.get_value())

    def __gallery_changed(self):
        """
        Handles the changing nature of gallery
        """
        _gallery_option = self.__gallery.get_value()
        _create_thumbs_only_option = self.__create_thumbs_only.get_value()

        # images and media objects to be used, make all opti8ons available...
        if _gallery_option:
            self.__create_thumbs_only.set_available(True)
            self.__maxinitialimagewidth.set_available(True)
            self.__create_images_index.set_available(True)
            self.__create_thumbs_index.set_available(True)
            self.__unused.set_available(True)

            # thumbnail-sized images only...
            if _create_thumbs_only_option:
                self.__maxinitialimagewidth.set_available(False)

            # full- sized images and Media Pages will be created...
            else:
                self.__maxinitialimagewidth.set_available(True)

        # no images or media objects are to be used...
        else:
            self.__create_thumbs_only.set_available(False)
            self.__maxinitialimagewidth.set_available(False)
            self.__create_images_index.set_available(False)
            self.__create_thumbs_index.set_available(False)
            self.__unused.set_available(False)

    def __download_changed(self):
        """
        Handles the changing nature of include download page
        """
        if self.__incdownload.get_value():
            self.__nbdownload.set_available(True)
            for count in range(1, self.__max_download):
                if count <= self.__nbdownload.get_value():
                    self.__down_fname[count].set_available(True)
                    self.__dl_descr[count].set_available(True)
                else:
                    self.__down_fname[count].set_available(False)
                    self.__dl_descr[count].set_available(False)
        else:
            self.__nbdownload.set_available(False)
            for count in range(1, self.__max_download):
                if count <= self.__nbdownload.get_value():
                    self.__down_fname[count].set_available(False)
                    self.__dl_descr[count].set_available(False)
                else:
                    self.__down_fname[count].set_available(False)
                    self.__dl_descr[count].set_available(False)

    def __placemap_options(self):
        """
        Handles the changing nature of the "Place map" options
        """
        # get values for all Place Map Options tab...
        place_active = self.__placemappages.get_value()
        family_active = self.__familymappages.get_value()
        mapservice_opts = self.__mapservice.get_value()
        # google_opts = self.__googleopts.get_value()

        if place_active or family_active:
            self.__mapservice.set_available(True)
        else:
            self.__mapservice.set_available(False)

        if mapservice_opts == "StamenMap":
            self.__stamenopts.set_available(True)
        else:
            self.__stamenopts.set_available(False)

        if family_active and mapservice_opts == "Google":
            self.__googleopts.set_available(True)
            if self.__olv:
                self.__olv.set_available(False)
        else:
            self.__googleopts.set_available(False)
            if self.__olv:
                self.__olv.set_available(True)

        if (place_active or family_active) and mapservice_opts == "Google":
            self.__googlemapkey.set_available(True)
            self.googlemapkeyhelp.set_available(True)
        else:
            self.__googlemapkey.set_available(False)
            self.googlemapkeyhelp.set_available(False)
        if (place_active or family_active) and mapservice_opts == "StamenMap":
            self.__stamenmapkey.set_available(True)
            self.stamenmapkeyhelp.set_available(True)
        else:
            self.__stamenmapkey.set_available(False)
            self.stamenmapkeyhelp.set_available(False)

    def url_changed(self):
        """
        This value must be changed only if the url is modified.
        """
        api_key_url = self.googlemapkeyhelp.get_value()
        if api_key_url != "":
            config.set("paths.website-get-api-key", api_key_url)

    def __add_calendar_options(self, menu):
        """
        Options on the "Calendar Options" tab.
        """
        category_name = _("Calendar Options")
        addopt = partial(menu.add_option, category_name)

        # set to today's date for use in menu, etc.
        today = Today()

        self.__usecal = BooleanOption(_("Do we include the web calendar ?"), False)
        self.__usecal.set_help(
            _("Whether to include " "a calendar for year %s" % today.get_year())
        )
        self.__usecal.connect("value-changed", self.__usecal_changed)
        addopt("usecal", self.__usecal)

        self.__start_dow = EnumeratedListOption(_("First day of week"), 1)
        for count in range(1, 8):
            self.__start_dow.add_item(count, _dd.long_days[count].capitalize())
        self.__start_dow.set_help(
            _("Select the first day of the week " "for the calendar")
        )
        menu.add_option(category_name, "start_dow", self.__start_dow)

        maiden_name = EnumeratedListOption(_("Birthday surname"), "own")
        maiden_name.add_item(
            "spouse_first",
            _("Wives use husband's surname " "(from first family listed)"),
        )
        maiden_name.add_item(
            "spouse_last", _("Wives use husband's surname " "(from last family listed)")
        )
        maiden_name.add_item("own", _("Wives use their own surname"))
        maiden_name.set_help(_("Select married women's displayed surname"))
        menu.add_option(category_name, "maiden_name", maiden_name)
        self.__maiden_name = maiden_name

        self.__makeoneday = BooleanOption(
            _("Create one day event pages for" " Year At A Glance calendar"), False
        )
        self.__makeoneday.set_help(_("Whether to create one day pages or not"))
        menu.add_option(category_name, "makeoneday", self.__makeoneday)

        self.__birthdays = BooleanOption(_("Include birthdays"), True)
        self.__birthdays.set_help(_("Include birthdays in the calendar"))
        menu.add_option(category_name, "birthdays", self.__birthdays)

        self.__anniv = BooleanOption(_("Include anniversaries"), True)
        self.__anniv.set_help(_("Include anniversaries in the calendar"))
        menu.add_option(category_name, "anniversaries", self.__anniv)

        self.__death_anniv = BooleanOption(_("Include death dates"), False)
        self.__death_anniv.set_help(_("Include death anniversaries in " "the calendar"))
        menu.add_option(category_name, "death_anniv", self.__death_anniv)

        self.__alive = BooleanOption(_("Include only living people"), True)
        self.__alive.set_help(_("Include only living people in the calendar"))
        menu.add_option(category_name, "alive", self.__alive)

        default_before = config.get("behavior.max-age-prob-alive")
        self.__after_year = NumberOption(
            _("Show data only after year"),
            (today.get_year() - default_before),
            0,
            today.get_year(),
        )
        self.__after_year.set_help(
            _(
                "Show data only after this year."
                " Default is current year - "
                " 'maximum age probably alive' which is "
                "defined in the dates preference tab."
            )
        )
        menu.add_option(category_name, "after_year", self.__after_year)

    def __usecal_changed(self):
        """
        Do we need to choose calendar options ?
        """
        if self.__usecal.get_value():
            self.__start_dow.set_available(True)
            self.__maiden_name.set_available(True)
            self.__makeoneday.set_available(True)
            self.__birthdays.set_available(True)
            self.__anniv.set_available(True)
            self.__alive.set_available(True)
            self.__death_anniv.set_available(True)
            self.__after_year.set_available(True)
        else:
            self.__start_dow.set_available(False)
            self.__maiden_name.set_available(False)
            self.__makeoneday.set_available(False)
            self.__birthdays.set_available(False)
            self.__anniv.set_available(False)
            self.__alive.set_available(False)
            self.__death_anniv.set_available(False)
            self.__after_year.set_available(False)
