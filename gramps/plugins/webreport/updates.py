# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2019-      Serge Noiraud
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
    UpdatesPage
"""
#------------------------------------------------
# python modules
#------------------------------------------------
from decimal import getcontext
import logging
from time import (strftime, time, localtime)

#------------------------------------------------
# Gramps module
#------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.plugins.lib.libhtml import Html

#------------------------------------------------
# specific narrative web import
#------------------------------------------------
from gramps.plugins.webreport.basepage import BasePage
from gramps.gen.display.place import displayer as _pd
from gramps.plugins.webreport.common import (FULLCLEAR, _EVENTMAP, html_escape)
from gramps.gen.lib import (Person, Family, Event, Place, Source, Repository,
                            Media, Citation)
from gramps.gen.lib.date import Date

_ = glocale.translation.sgettext
LOG = logging.getLogger(".NarrativeWeb")
getcontext().prec = 8

class UpdatesPage(BasePage):
    """
    This class is responsible for displaying information about the Home page.
    """
    def __init__(self, report, the_lang, the_title):
        """
        @param: report    -- The instance of the main report class
                             for this report
        @param: the_lang  -- The lang to process
        @param: the_title -- The title page related to the language
        """
        BasePage.__init__(self, report, the_lang, the_title)
        ldatec = 0
        self.inc_repository = self.report.options['inc_repository']
        self.inc_families = self.report.options['inc_families']
        self.inc_events = self.report.options['inc_events']
        self.inc_places = self.report.options['inc_places']
        self.inc_sources = self.report.options['inc_sources']
        self.inc_gallery = False

        output_file, sio = self.report.create_file("updates")
        result = self.write_header(self._('New and updated objects'))
        homepage, dummy_head, dummy_body, outerwrapper = result
        self.days = self.report.options['maxdays']
        self.nbr = self.report.options['maxupdates']
        cur_time = int(time())
        self.maxdays = cur_time - (86400 * self.days)

        # begin updates division
        with Html("div", class_="content", id="Updates") as section:
            outerwrapper += section
            description = self._("This page contains the last updated objects "
                                 "in the database in the last %(days)d days and"
                                 " for a maximum of %(nb)d objects per object "
                                 "type." % {
                                     'days' : self.days,
                                     'nb' : self.nbr
                                     }
                                )
            section += Html("p", description)

            header = self._("People")
            section += Html("h4", header)
            people = self.list_people_changed(Person)
            if people is not None:
                section += people

            if self.inc_families:
                header = self._("Families")
                section += Html("h4", header)
                families = self.list_people_changed(Family)
                if families is not None:
                    section += families

            if self.inc_events:
                header = self._("Events")
                section += Html("h4", header)
                events = self.list_people_changed(Event)
                if events is not None:
                    section += events

            if self.inc_places:
                header = self._("Places")
                section += Html("h4", header)
                places = self.list_people_changed(Place)
                if places is not None:
                    section += places

            if self.inc_sources:
                header = self._("Sources")
                section += Html("h4", header)
                sources = self.list_people_changed(Source)
                if sources is not None:
                    section += sources

            if self.inc_repository:
                header = self._("Repositories")
                section += Html("h4", header)
                repos = self.list_people_changed(Repository)
                if repos is not None:
                    section += repos

            if (self.report.options['gallery'] and not
                    self.report.options['create_thumbs_only']):
                self.inc_gallery = True
                header = self._("Media")
                section += Html("h4", header)
                media = self.list_people_changed(Media)
                if media is not None:
                    section += media

            header = self._("Notes")
            section += Html("h4", header)
            events = self.list_notes()
            if events is not None:
                section += events

        # create clear line for proper styling
        # create footer section
        footer = self.write_footer(ldatec)
        outerwrapper += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(homepage, output_file, sio, ldatec)

    def list_notes(self):
        """
        List all notes with last change date
        """
        nb_items = 0
        section = ""

        def sort_on_change(handle):
            """ sort records based on the last change time """
            fct = self.report.database.get_note_from_handle
            obj = fct(handle)
            timestamp = obj.get_change_time()
            return timestamp

        note_list = self.report.database.get_note_handles()
        obj_list = sorted(note_list, key=sort_on_change, reverse=True)
        with Html("table", class_="list", id="list") as section:
            for handle in obj_list:
                show = False
                date = obj = None
                obj = self.report.database.get_note_from_handle(handle)
                if obj:
                    text = html_escape(obj.get()[:50])
                    timestamp = obj.get_change_time()
                    if timestamp - self.maxdays > 0:
                        handle_list = set(
                            self.report.database.find_backlink_handles(
                                handle,
                                include_classes=['Person', 'Family', 'Event',
                                                 'Place', 'Media', 'Source',
                                                 'Citation', 'Repository',
                                                ]))
                        tims = localtime(timestamp)
                        odat = Date(tims.tm_year, tims.tm_mon, tims.tm_mday)
                        date = self.rlocale.date_displayer.display(odat)
                        date += strftime(' %X', tims)
                        if handle_list:
                            srbd = self.report.database
                            srbkref = self.report.bkref_dict
                            for obj_t, r_handle in handle_list:
                                if obj_t == 'Person':
                                    if r_handle in srbkref[Person]:
                                        name = self.new_person_link(r_handle)
                                        show = True
                                elif obj_t == 'Family':
                                    if r_handle in srbkref[Family]:
                                        fam = srbd.get_family_from_handle(
                                            r_handle)
                                        fam = self._("Family")
                                        name = self.family_link(r_handle, fam)
                                        if self.inc_families:
                                            show = True
                                elif obj_t == 'Place':
                                    if r_handle in srbkref[Place]:
                                        plc = srbd.get_place_from_handle(
                                            r_handle)
                                        plcn = _pd.display(self.report.database,
                                                           plc)
                                        name = self.place_link(r_handle, plcn)
                                        if self.inc_places:
                                            show = True
                                elif obj_t == 'Event':
                                    if r_handle in srbkref[Event]:
                                        evt = srbd.get_event_from_handle(
                                            r_handle)
                                        evtn = self._(evt.get_type().xml_str())
                                        name = self.event_link(r_handle, evtn)
                                        if self.inc_events:
                                            show = True
                                elif obj_t == 'Media':
                                    if r_handle in srbkref[Media]:
                                        media = srbd.get_media_from_handle(
                                            r_handle)
                                        evtn = media.get_description()
                                        name = self.media_link(r_handle, evtn,
                                                               evtn,
                                                               usedescr=False)
                                        if self.inc_gallery:
                                            show = True
                                elif obj_t == 'Citation':
                                    if r_handle in srbkref[Citation]:
                                        cit = srbd.get_event_from_handle(
                                            r_handle)
                                        citsrc = cit.source_handle
                                        evtn = self._("Citation")
                                        name = self.source_link(citsrc, evtn)
                                        if self.inc_sources:
                                            show = True
                                elif obj_t == 'Source':
                                    if r_handle in srbkref[Source]:
                                        src = srbd.get_source_from_handle(
                                            r_handle)
                                        evtn = src.get_title()
                                        name = self.source_link(r_handle, evtn)
                                        if self.inc_sources:
                                            show = True
                                elif obj_t == 'Repository':
                                    if r_handle in srbkref[Repository]:
                                        rep = srbd.get_repository_from_handle(
                                            r_handle)
                                        evtn = rep.get_name()
                                        name = self.repository_link(r_handle,
                                                                    evtn)
                                        if self.inc_repository:
                                            show = True
                        if show:
                            row = Html("tr")
                            section += row
                            row += Html("td", date, class_="date")
                            row += Html("td", text)
                            row += Html("td", name)
                            nb_items += 1
                            if nb_items > self.nbr:
                                break
        return section

    def list_people_changed(self, object_type):
        """
        List all records with last change date
        """
        nb_items = 0

        def sort_on_change(handle):
            """ sort records based on the last change time """
            obj = fct(handle)
            timestamp = obj.get_change_time()
            return timestamp

        if object_type == Person:
            fct = self.report.database.get_person_from_handle
            fct_link = self.new_person_link
        elif object_type == Family:
            fct = self.report.database.get_family_from_handle
            fct_link = self.family_link
        elif object_type == Event:
            fct = self.report.database.get_event_from_handle
        elif object_type == Place:
            fct = self.report.database.get_place_from_handle
            fct_link = self.place_link
        elif object_type == Source:
            fct = self.report.database.get_place_from_handle
            fct_link = self.source_link
        elif object_type == Repository:
            fct = self.report.database.get_place_from_handle
            fct_link = self.repository_link
        elif object_type == Media:
            fct = self.report.database.get_place_from_handle
        obj_list = sorted(self.report.obj_dict[object_type],
                          key=sort_on_change, reverse=True)
        with Html("table", class_="list", id="list") as section:
            for handle in obj_list:
                date = obj = None
                name = ""
                obj = fct(handle)
                if object_type == Person:
                    name = fct_link(handle)
                elif object_type == Family:
                    name = self.report.get_family_name(obj)
                    name = fct_link(handle, name)
                elif object_type == Event:
                    otype = obj.get_type()
                    date = obj.get_date_object()
                    if int(otype) in _EVENTMAP:
                        handle_list = set(
                            self.report.database.find_backlink_handles(
                                handle,
                                include_classes=['Family', 'Person']))
                    else:
                        handle_list = set(
                            self.report.database.find_backlink_handles(
                                handle,
                                include_classes=['Person']))
                    if handle_list:
                        name = Html("span", self._(otype.xml_str())+" ")
                        for obj_t, r_handle in handle_list:
                            if obj_t == 'Person':
                                name += self.new_person_link(r_handle)
                            else:
                                srbd = self.report.database
                                fam = srbd.get_family_from_handle(r_handle)
                                srgfn = self.report.get_family_name
                                name += self.family_link(r_handle, srgfn(fam))
                elif object_type == Place:
                    name = _pd.display(self.report.database, obj)
                    name = fct_link(handle, name)
                elif object_type == Source:
                    name = obj.get_title()
                    name = fct_link(handle, name)
                elif object_type == Repository:
                    name = obj.get_name()
                    name = fct_link(handle, name)
                elif object_type == Media:
                    name = obj.get_description()
                    url = self.report.build_url_fname_html(handle, "img")
                    name = Html("a", name, href=url, title=name)
                if obj:
                    timestamp = obj.get_change_time()
                    if timestamp - self.maxdays > 0:
                        nb_items += 1
                        if nb_items > self.nbr:
                            break
                        tims = localtime(timestamp)
                        odat = Date(tims.tm_year, tims.tm_mon, tims.tm_mday)
                        date = self.rlocale.date_displayer.display(odat)
                        date += strftime(' %X', tims)
                        row = Html("tr")
                        section += row
                        row += Html("td", date, class_="date")
                        row += Html("td", name)
        return section
