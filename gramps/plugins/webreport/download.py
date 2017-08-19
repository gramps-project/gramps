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
    DownloadPage
"""
#------------------------------------------------
# python modules
#------------------------------------------------
import os
import datetime
from decimal import getcontext
import logging

#------------------------------------------------
# Gramps module
#------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.plugins.lib.libhtml import Html

#------------------------------------------------
# specific narrative web import
#------------------------------------------------
from gramps.plugins.webreport.basepage import BasePage
from gramps.plugins.webreport.common import (FULLCLEAR, html_escape)

_ = glocale.translation.sgettext
LOG = logging.getLogger(".NarrativeWeb")
getcontext().prec = 8

class DownloadPage(BasePage):
    """
    This class is responsible for displaying information about the Download page
    """
    def __init__(self, report, title):
        """
        @param: report -- The instance of the main report class for this report
        @param: title  -- Is the title of the web page
        """
        BasePage.__init__(self, report, title)

        # do NOT include a Download Page
        if not self.report.inc_download:
            return

        # menu options for class
        # download and description #1

        dlfname1 = self.report.dl_fname1
        dldescr1 = self.report.dl_descr1

        # download and description #2
        dlfname2 = self.report.dl_fname2
        dldescr2 = self.report.dl_descr2

        # if no filenames at all, return???
        if dlfname1 or dlfname2:

            output_file, sio = self.report.create_file("download")
            downloadpage, head, body = self.write_header(self._('Download'))

            # begin download page and table
            with Html("div", class_="content", id="Download") as download:
                body += download

                msg = self._("This page is for the user/ creator "
                             "of this Family Tree/ Narrative website "
                             "to share a couple of files with you "
                             "regarding their family.  If there are "
                             "any files listed "
                             "below, clicking on them will allow you "
                             "to download them. The "
                             "download page and files have the same "
                             "copyright as the remainder "
                             "of these web pages.")
                download += Html("p", msg, id="description")

                # begin download table and table head
                with Html("table", class_="infolist download") as table:
                    download += table

                    thead = Html("thead")
                    table += thead

                    trow = Html("tr")
                    thead += trow

                    trow.extend(
                        Html("th", label, class_="Column" + colclass,
                             inline=True)
                        for (label, colclass) in [
                            (self._("File Name"), "Filename"),
                            (self._("Description"), "Description"),
                            (self._("Last Modified"), "Modified")])
                    # table body
                    tbody = Html("tbody")
                    table += tbody

                    # if dlfname1 is not None, show it???
                    if dlfname1:

                        trow = Html("tr", id='Row01')
                        tbody += trow

                        fname = os.path.basename(dlfname1)
                        # TODO dlfname1 is filename, convert disk path to URL
                        tcell = Html("td", class_="ColumnFilename") + (
                            Html("a", fname, href=dlfname1,
                                 title=html_escape(dldescr1))
                        )
                        trow += tcell

                        dldescr1 = dldescr1 or "&nbsp;"
                        trow += Html("td", dldescr1,
                                     class_="ColumnDescription", inline=True)

                        tcell = Html("td", class_="ColumnModified", inline=True)
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
                        trow = Html("tr", id='Row02')
                        tbody += trow

                        fname = os.path.basename(dlfname2)
                        tcell = Html("td", class_="ColumnFilename") + (
                            Html("a", fname, href=dlfname2,
                                 title=html_escape(dldescr2))
                        )
                        trow += tcell

                        dldescr2 = dldescr2 or "&nbsp;"
                        trow += Html("td", dldescr2,
                                     class_="ColumnDescription", inline=True)

                        tcell = Html("td", id='Col04',
                                     class_="ColumnModified", inline=True)
                        trow += tcell
                        if os.path.exists(dlfname2):
                            modified = os.stat(dlfname2).st_mtime
                            last_mod = datetime.datetime.fromtimestamp(modified)
                            tcell += last_mod
                        else:
                            tcell += "&nbsp;"

            # clear line for proper styling
            # create footer section
            footer = self.write_footer(None)
            body += (FULLCLEAR, footer)

            # send page out for processing
            # and close the file
            self.xhtml_writer(downloadpage, output_file, sio, 0)
