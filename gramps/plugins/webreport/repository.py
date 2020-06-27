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
    RepositoryPage - Repository index page and individual Repository pages
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
from gramps.gen.lib import Repository
from gramps.plugins.lib.libhtml import Html

#------------------------------------------------
# specific narrative web import
#------------------------------------------------
from gramps.plugins.webreport.basepage import BasePage
from gramps.plugins.webreport.common import (FULLCLEAR, html_escape)

_ = glocale.translation.sgettext
LOG = logging.getLogger(".NarrativeWeb")
getcontext().prec = 8

#################################################
#
#    creates the Repository List Page and Repository Pages
#
#################################################
class RepositoryPages(BasePage):
    """
    This class is responsible for displaying information about the 'Repository'
    database objects. It displays this information under the 'Individuals'
    tab. It is told by the 'add_instances' call which 'Repository's to display,
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
        self.repos_dict = defaultdict(set)

    def display_pages(self, the_lang, the_title):
        """
        Generate and output the pages under the Repository tab, namely the
        repository index and the individual repository pages.

        @param: the_lang  -- The lang to process
        @param: the_title -- The title page related to the language
        """
        LOG.debug("obj_dict[Person]")
        for item in self.report.obj_dict[Repository].items():
            LOG.debug("    %s", str(item))

        # set progress bar pass for Repositories
        message = _('Creating repository pages')
        progress_title = self.report.pgrs_title(the_lang)
        with self.r_user.progress(progress_title, message,
                                  len(self.report.obj_dict[Repository]) + 1
                                 ) as step:
            # Sort the repositories
            repos_dict = {}
            for repo_handle in self.report.obj_dict[Repository]:
                repository = self.r_db.get_repository_from_handle(repo_handle)
                key = repository.get_name() + str(repository.get_gramps_id())
                repos_dict[key] = (repository, repo_handle)

            keys = sorted(repos_dict, key=self.rlocale.sort_key)

            # RepositoryListPage Class
            self.repositorylistpage(self.report, the_lang, the_title,
                                    repos_dict, keys)

            idx = 1
            for dummy_index, key in enumerate(keys):
                (repo, handle) = repos_dict[key]
                step()
                idx += 1
                self.repositorypage(self.report, the_lang, the_title,
                                    repo, handle)

    def repositorylistpage(self, report, the_lang, the_title, repos_dict, keys):
        """
        Create Index for repositories

        @param: report     -- The instance of the main report class
                              for this report
        @param: the_lang   -- The lang to process
        @param: the_title  -- The title page related to the language
        @param: repos_dict -- The dictionary for all repositories
        @param: keys       -- The keys used to access repositories
        """
        BasePage.__init__(self, report, the_lang, the_title)
        #inc_repos = self.report.options["inc_repository"]

        output_file, sio = self.report.create_file("repositories")
        result = self.write_header(_("Repositories"))
        repolistpage, dummy_head, dummy_body, outerwrapper = result

        ldatec = 0
        # begin RepositoryList division
        with Html("div", class_="content",
                  id="RepositoryList") as repositorylist:
            outerwrapper += repositorylist

            msg = self._("This page contains an index of "
                         "all the repositories in the "
                         "database, sorted by their title. "
                         "Clicking on a repositories&#8217;s title "
                         "will take you to that repositories&#8217;s page.")
            repositorylist += Html("p", msg, id="description")

            # begin repositories table and table head
            with Html("table", class_="infolist primobjlist repolist") as table:
                repositorylist += table

                thead = Html("thead")
                table += thead

                trow = Html("tr") + (
                    Html("th", "&nbsp;", class_="ColumnRowLabel", inline=True),
                    Html("th", self._("Type"), class_="ColumnType",
                         inline=True),
                    Html("th", self._("Name", "Repository "),
                         class_="ColumnName",
                         inline=True)
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
                    trow += Html("td", index + 1, class_="ColumnRowLabel",
                                 inline=True)

                    # repository type
                    rtype = self._(repo.type.xml_str())
                    trow += Html("td", rtype, class_="ColumnType", inline=True)

                    # repository name and hyperlink
                    if repo.get_name():
                        trow += Html("td",
                                     self.repository_link(handle,
                                                          repo.get_name(),
                                                          repo.get_gramps_id(),
                                                          self.uplink),
                                     class_="ColumnName")
                        ldatec = repo.get_change_time()
                    else:
                        trow += Html("td", "[ untitled ]", class_="ColumnName")

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        outerwrapper += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(repolistpage, output_file, sio, ldatec)

    def repositorypage(self, report, the_lang, the_title, repo, handle):
        """
        Create one page for one repository.

        @param: report    -- The instance of the main report class
                             for this report
        @param: the_lang  -- The lang to process
        @param: the_title -- The title page related to the language
        @param: repo      -- the repository to use
        @param: handle    -- the handle to use
        """
        gid = repo.get_gramps_id()
        BasePage.__init__(self, report, the_lang, the_title, gid)
        ldatec = repo.get_change_time()

        output_file, sio = self.report.create_file(handle, 'repo')
        self.uplink = True
        result = self.write_header(_('Repositories'))
        repositorypage, dummy_head, dummy_body, outerwrapper = result

        # begin RepositoryDetail division and page title
        with Html("div", class_="content",
                  id="RepositoryDetail") as repositorydetail:
            outerwrapper += repositorydetail

            # repository name
            repositorydetail += Html("h3", html_escape(repo.name),
                                     inline=True)

            # begin repository table
            with Html("table", class_="infolist repolist") as table:
                repositorydetail += table

                tbody = Html("tbody")
                table += tbody

                if not self.noid and gid:
                    trow = Html("tr") + (
                        Html("td", self._("Gramps ID"),
                             class_="ColumnAttribute",
                             inline=True),
                        Html("td", gid, class_="ColumnValue", inline=True)
                    )
                    tbody += trow

                trow = Html("tr") + (
                    Html("td", self._("Type"), class_="ColumnAttribute",
                         inline=True),
                    Html("td", self._(repo.get_type().xml_str()),
                         class_="ColumnValue",
                         inline=True)
                )
                tbody += trow

            # Tags
            tags = self.show_tags(repo)
            if tags and self.report.inc_tags:
                trow = Html("tr") + (
                    Html("td", self._("Tags"),
                         class_="ColumnAttribute", inline=True),
                    Html("td", tags,
                         class_="ColumnValue", inline=True)
                    )
                tbody += trow

            # repository: address(es)...
            # repository addresses do NOT have Sources
            repo_address = self.display_addr_list(repo.get_address_list(),
                                                  False)
            if repo_address is not None:
                repositorydetail += repo_address

            # repository: urllist
            urllist = self.display_url_list(repo.get_url_list())
            if urllist is not None:
                repositorydetail += urllist

            # reposity: notelist
            notelist = self.display_note_list(repo.get_note_list(), Repository)
            if notelist is not None:
                repositorydetail += notelist

            # display Repository Referenced Sources...
            ref_list = self.display_bkref_list(Repository, repo.get_handle())
            if ref_list is not None:
                repositorydetail += ref_list

        # add clearline for proper styling
        # add footer section
        footer = self.write_footer(ldatec)
        outerwrapper += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        self.xhtml_writer(repositorypage, output_file, sio, ldatec)
