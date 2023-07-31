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
    DownloadPage
"""
# ------------------------------------------------
# python modules
# ------------------------------------------------
import os
import datetime
from decimal import getcontext
import logging

# ------------------------------------------------
# Gramps module
# ------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.plugins.lib.libhtml import Html

# ------------------------------------------------
# specific narrative web import
# ------------------------------------------------
from gramps.plugins.webreport.basepage import BasePage
from gramps.plugins.webreport.common import FULLCLEAR, html_escape
from gramps.gen.utils.file import create_checksum

_ = glocale.translation.sgettext
LOG = logging.getLogger(".NarrativeWeb")
getcontext().prec = 8


class DownloadPage(BasePage):
    """
    This class is responsible for displaying information about the Download page
    """

    def __init__(self, report, the_lang, the_title):
        """
        @param: report    -- The instance of the main report class
                             for this report
        @param: the_lang  -- The lang to process
        @param: the_title -- The title page related to the language
        """
        BasePage.__init__(self, report, the_lang, the_title)

        # do NOT include a Download Page
        if not self.report.inc_download:
            return

        # menu options for class
        # download and description #n ( 1 <= n < 5 )

        dlfname = self.report.dl_fname
        dldescr = self.report.dl_descr

        # if no filenames at all, return???
        if dlfname:
            output_file, sio = self.report.create_file("download")
            result = self.write_header(self._("Download"))
            downloadpage, dummy_head, dummy_body, outerwrapper = result

            # begin download page and table
            with Html("div", class_="content", id="Download") as download:
                outerwrapper += download

                msg = self._(
                    "This page is for the user/ creator "
                    "of this Family Tree/ Narrative website "
                    "to share a couple of files with you "
                    "regarding their family.  If there are "
                    "any files listed "
                    "below, clicking on them will allow you "
                    "to download them. The "
                    "download page and files have the same "
                    "copyright as the remainder "
                    "of these web pages."
                )
                download += Html("p", msg, id="description")

                # begin download table and table head
                with Html("table", class_="infolist download") as table:
                    download += table

                    thead = Html("thead")
                    table += thead

                    trow = Html("tr")
                    thead += trow

                    trow.extend(
                        Html("th", label, class_="Column" + colclass, inline=True)
                        for (label, colclass) in [
                            (self._("File Name"), "Filename"),
                            (self._("Description"), "Description"),
                            (self._("Last Modified"), "Modified"),
                            (self._("MD5"), "Md5"),
                        ]
                    )
                    # table body
                    tbody = Html("tbody")
                    table += tbody
                    dwnld = 0

                    for fnamex in dlfname:
                        # if fnamex is not None, do we have a file to download?
                        if fnamex:
                            fname = os.path.basename(dlfname[fnamex])
                            # if fname is not None, show it
                            if fname:
                                dwnld += 1
                                trow = Html("tr", id="Row01")
                                tbody += trow
                                fname_lnk = "../" + fname if the_lang else fname
                                dldescrx = dldescr[fnamex]
                                tcell = Html("td", class_="ColumnFilename") + (
                                    Html(
                                        "a",
                                        fname,
                                        href=fname_lnk,
                                        title=html_escape(dldescrx),
                                    )
                                )
                                trow += tcell

                                dldescr1 = dldescrx or "&nbsp;"
                                trow += Html(
                                    "td",
                                    dldescr1,
                                    inline=True,
                                    class_="ColumnDescription",
                                )

                                tcell = Html("td", class_="ColumnModified", inline=True)
                                trow += tcell
                                if os.path.exists(dlfname[fnamex]):
                                    md5 = create_checksum(dlfname[fnamex])
                                    trow += Html(
                                        "td", md5, class_="ColumnMd5", inline=True
                                    )
                                    modified = os.stat(dlfname[fnamex]).st_mtime
                                    last_mod = datetime.datetime.fromtimestamp(modified)
                                    tcell += last_mod
                                    # copy the file only once
                                    if not os.path.exists(fname):
                                        self.report.copy_file(dlfname[fnamex], fname)
                                else:
                                    tcell += self._("Cannot open file")

                    if not dwnld:
                        # We have several files to download
                        # but all file names are empty
                        dldescrx = self._("No file to download")
                        trow = Html("tr", id="Row01")
                        tbody += trow
                        tcell = Html("td", class_="ColumnFilename", colspan=3) + Html(
                            "h4", dldescrx
                        )
                        trow += tcell
            # clear line for proper styling
            # create footer section
            footer = self.write_footer(None)
            outerwrapper += (FULLCLEAR, footer)

            # send page out for processing
            # and close the file
            self.xhtml_writer(downloadpage, output_file, sio, 0)
