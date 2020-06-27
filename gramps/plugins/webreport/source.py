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
    SourcePage - Source index page and individual Source pages
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
from gramps.gen.lib import Source
from gramps.plugins.lib.libhtml import Html

#------------------------------------------------
# specific narrative web import
#------------------------------------------------
from gramps.plugins.webreport.basepage import BasePage
from gramps.plugins.webreport.common import (FULLCLEAR, html_escape)

_ = glocale.translation.sgettext
LOG = logging.getLogger(".NarrativeWeb.source")
getcontext().prec = 8

#################################################
#
#    creates the Source List Page and Source Pages
#
#################################################
class SourcePages(BasePage):
    """
    This class is responsible for displaying information about the 'Source'
    database objects. It displays this information under the 'Sources'
    tab. It is told by the 'add_instances' call which 'Source's to display,
    and remembers the list of persons. A single call to 'display_pages'
    displays both the Individual List (Index) page and all the Individual
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
        self.source_dict = defaultdict(set)
        self.navigation = None
        self.citationreferents = None

    def display_pages(self, the_lang, the_title):
        """
        Generate and output the pages under the Sources tab, namely the sources
        index and the individual sources pages.

        @param: the_lang  -- The lang to process
        @param: the_title -- The title page related to the language
        """
        LOG.debug("obj_dict[Source]")
        for item in self.report.obj_dict[Source].items():
            LOG.debug("    %s", str(item))
        message = _("Creating source pages")
        progress_title = self.report.pgrs_title(the_lang)
        with self.r_user.progress(progress_title, message,
                                  len(self.report.obj_dict[Source]) + 1
                                 ) as step:
            self.sourcelistpage(self.report, the_lang, the_title,
                                self.report.obj_dict[Source].keys())

            index = 1
            for source_handle in self.report.obj_dict[Source]:
                step()
                index += 1
                self.sourcepage(self.report, the_lang, the_title, source_handle)

    def sourcelistpage(self, report, the_lang, the_title, source_handles):
        """
        Generate and output the Sources index page.

        @param: report         -- The instance of the main report class for
                                  this report
        @param: the_lang       -- The lang to process
        @param: the_title      -- The title page related to the language
        @param: source_handles -- A list of the handles of the sources to be
                                  displayed
        """
        BasePage.__init__(self, report, the_lang, the_title)

        source_dict = {}

        output_file, sio = self.report.create_file("sources")
        result = self.write_header(self._("Sources"))
        sourcelistpage, dummy_head, dummy_body, outerwrapper = result

        # begin source list division
        with Html("div", class_="content", id="Sources") as sourceslist:
            outerwrapper += sourceslist

            # Sort the sources
            for handle in source_handles:
                source = self.r_db.get_source_from_handle(handle)
                if source is not None:
                    key = source.get_title() + source.get_author()
                    key += str(source.get_gramps_id())
                    source_dict[key] = (source, handle)

            keys = sorted(source_dict, key=self.rlocale.sort_key)

            msg = self._("This page contains an index of all the sources "
                         "in the database, sorted by their title. "
                         "Clicking on a source&#8217;s "
                         "title will take you to that source&#8217;s page.")
            sourceslist += Html("p", msg, id="description")

            # begin sourcelist table and table head
            with Html("table",
                      class_="infolist primobjlist sourcelist") as table:
                sourceslist += table
                thead = Html("thead")
                table += thead

                trow = Html("tr")
                thead += trow

                header_row = [
                    (self._("Number"), "ColumnRowLabel"),
                    (self._("Author"), "ColumnAuthor"),
                    (self._("Name", "Source Name"), "ColumnName")]

                trow.extend(
                    Html("th", label or "&nbsp;", class_=colclass, inline=True)
                    for (label, colclass) in header_row
                )

                # begin table body
                tbody = Html("tbody")
                table += tbody

                for index, key in enumerate(keys):
                    source, source_handle = source_dict[key]

                    trow = Html("tr") + (
                        Html("td", index + 1, class_="ColumnRowLabel",
                             inline=True)
                    )
                    tbody += trow
                    trow.extend(
                        Html("td", source.get_author(), class_="ColumnAuthor",
                             inline=True)
                    )
                    trow.extend(
                        Html("td", self.source_link(source_handle,
                                                    source.get_title(),
                                                    source.get_gramps_id()),
                             class_="ColumnName")
                    )

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(None)
        outerwrapper += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(sourcelistpage, output_file, sio, 0)

    def sourcepage(self, report, the_lang, the_title, source_handle):
        """
        Generate and output an individual Source page.

        @param: report        -- The instance of the main report class
                                 for this report
        @param: the_lang      -- The lang to process
        @param: the_title     -- The title page related to the language
        @param: source_handle -- The handle of the source to be output
        """
        source = report.database.get_source_from_handle(source_handle)
        BasePage.__init__(self, report, the_lang, the_title,
                          source.get_gramps_id())
        if not source:
            return

        self.page_title = source.get_title()

        inc_repositories = self.report.options["inc_repository"]
        self.navigation = self.report.options['navigation']
        self.citationreferents = self.report.options['citationreferents']

        output_file, sio = self.report.create_file(source_handle, "src")
        self.uplink = True
        result = self.write_header("%s - %s" % (self._('Sources'),
                                                self.page_title))
        sourcepage, dummy_head, dummy_body, outerwrapper = result

        ldatec = 0
        # begin source detail division
        with Html("div", class_="content", id="SourceDetail") as sourcedetail:
            outerwrapper += sourcedetail

            media_list = source.get_media_list()
            if self.create_media and media_list:
                thumbnail = self.disp_first_img_as_thumbnail(media_list,
                                                             source)
                if thumbnail is not None:
                    sourcedetail += thumbnail

            # add section title
            sourcedetail += Html("h3", html_escape(source.get_title()),
                                 inline=True)

            # begin sources table
            with Html("table", class_="infolist source") as table:
                sourcedetail += table

                tbody = Html("tbody")
                table += tbody

                source_gid = False
                if not self.noid and self.gid:
                    source_gid = source.get_gramps_id()

                    # last modification of this source
                    ldatec = source.get_change_time()

                for (label, value) in [(self._("Gramps ID"), source_gid),
                                       (self._("Author"), source.get_author()),
                                       (self._("Abbreviation"),
                                        source.get_abbreviation()),
                                       (self._("Publication information"),
                                        source.get_publication_info())]:
                    if value:
                        trow = Html("tr") + (
                            Html("td", label, class_="ColumnAttribute",
                                 inline=True),
                            Html("td", value, class_="ColumnValue", inline=True)
                        )
                        tbody += trow

            # Tags
            tags = self.show_tags(source)
            if tags and self.report.inc_tags:
                trow = Html("tr") + (
                    Html("td", self._("Tags"),
                         class_="ColumnAttribute", inline=True),
                    Html("td", tags,
                         class_="ColumnValue", inline=True)
                    )
                tbody += trow

            # Source notes
            notelist = self.display_note_list(source.get_note_list(), Source)
            if notelist is not None:
                sourcedetail += notelist

            # additional media from Source (if any?)
            if self.create_media and media_list:
                sourcemedia = self.disp_add_img_as_gallery(media_list, source)
                if sourcemedia is not None:
                    sourcedetail += sourcemedia

            # Source Data Map...
            src_data_map = self.write_srcattr(source.get_attribute_list())
            if src_data_map is not None:
                sourcedetail += src_data_map

            # Source Repository list
            if inc_repositories:
                repo_list = self.dump_repository_ref_list(
                    source.get_reporef_list())
                if repo_list is not None:
                    sourcedetail += repo_list

            # Source references list
            ref_list = self.display_bkref_list(Source, source_handle)
            if ref_list is not None:
                sourcedetail += ref_list

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        outerwrapper += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(sourcepage, output_file, sio, ldatec)
