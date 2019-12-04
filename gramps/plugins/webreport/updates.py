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
from gramps.plugins.webreport.common import (FULLCLEAR, _EVENTMAP)
from gramps.gen.lib import (Person, Family, Event, Place, Source, Repository,
                            Media)
from gramps.gen.lib.date import Date

_ = glocale.translation.sgettext
LOG = logging.getLogger(".NarrativeWeb")
getcontext().prec = 8

class UpdatesPage(BasePage):
    """
    This class is responsible for displaying information about the Home page.
    """
    def __init__(self, report, title):
        """
        @param: report -- The instance of the main report class for
                          this report
        @param: title  -- Is the title of the web page
        """
        BasePage.__init__(self, report, title)
        ldatec = 0

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
            description = ("This page contains the last updated objects in the"
                           " database in the last %(days)d days and for a "
                           "maximum of %(nb)d objects per object type." % {
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

            if self.report.options['inc_families']:
                header = self._("Families")
                section += Html("h4", header)
                families = self.list_people_changed(Family)
                if families is not None:
                    section += families

            if self.report.options['inc_events']:
                header = self._("Events")
                section += Html("h4", header)
                events = self.list_people_changed(Event)
                if events is not None:
                    section += events

            if self.report.options['inc_places']:
                header = self._("Places")
                section += Html("h4", header)
                places = self.list_people_changed(Place)
                if places is not None:
                    section += places

            if self.report.options['inc_sources']:
                header = self._("Sources")
                section += Html("h4", header)
                sources = self.list_people_changed(Source)
                if sources is not None:
                    section += sources

            if self.report.options['inc_repository']:
                header = self._("Repositories")
                section += Html("h4", header)
                repos = self.list_people_changed(Repository)
                if repos is not None:
                    section += repos

            if (self.report.options['gallery'] and not
                    self.report.options['create_thumbs_only']):
                header = self._("Media")
                section += Html("h4", header)
                media = self.list_people_changed(Media)
                if media is not None:
                    section += media

        # create clear line for proper styling
        # create footer section
        footer = self.write_footer(ldatec)
        outerwrapper += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(homepage, output_file, sio, ldatec)

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
                row = Html("tr")
                section += row
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
                        row += Html("td", date, class_="date")
                        row += Html("td", name)
        return section
