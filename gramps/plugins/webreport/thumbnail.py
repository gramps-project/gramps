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
    ThumbnailPreviewPage
"""
#------------------------------------------------
# python modules
#------------------------------------------------
from decimal import getcontext
import logging

#------------------------------------------------
# Gramps module
#------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import Media
from gramps.plugins.lib.libhtml import Html

#------------------------------------------------
# specific narrative web import
#------------------------------------------------
from gramps.plugins.webreport.basepage import BasePage
from gramps.plugins.webreport.common import (FULLCLEAR, html_escape)

_ = glocale.translation.sgettext
LOG = logging.getLogger(".NarrativeWeb")
getcontext().prec = 8

class ThumbnailPreviewPage(BasePage):
    """
    This class is responsible for displaying information about
    the Thumbnails page.
    """
    def __init__(self, report, the_lang, the_title, cb_progress):
        """
        @param: report      -- The instance of the main report class
                               for this report
        @param: the_lang    -- Is the lang to process.
        @param: title       -- Is the title of the web page
        @param: cb_progress -- The step used for the progress bar.
        """
        BasePage.__init__(self, report, the_lang, the_title)
        self.create_thumbs_only = report.options['create_thumbs_only']
        self.create_thumbs_index = self.report.options['create_thumbs_index']
        # bug 8950 : it seems it's better to sort on desc + gid.
        def sort_by_desc_and_gid(obj):
            """
            Sort by media description and gramps ID
            """
            return (obj.desc, obj.gramps_id)

        self.photo_keys = sorted(self.report.obj_dict[Media],
                                 key=lambda x: sort_by_desc_and_gid(
                                     self.r_db.get_media_from_handle(x)))

        if self.create_unused_media:
            # add unused media
            media_list = self.r_db.get_media_handles()
            for media_ref in media_list:
                if media_ref not in self.report.obj_dict[Media]:
                    self.photo_keys.append(media_ref)

        media_list = []
        for person_handle in self.photo_keys:
            photo = self.r_db.get_media_from_handle(person_handle)
            if photo:
                if photo.get_mime_type().startswith("image"):
                    media_list.append((photo.get_description(), person_handle,
                                       photo))

                    if self.create_thumbs_only:
                        self.copy_thumbnail(person_handle, photo)

        media_list.sort(key=lambda x: self.rlocale.sort_key(x[0]))

        # Create thumbnail preview page...
        if self.create_thumbs_index:
            output_file, sio = self.report.create_file("thumbnails")
        result = self.write_header(self._("Thumbnails"))
        thumbnailpage, dummy_head, body, outerwrapper = result

        with Html("div", class_="content", id="Preview") as previewpage:
            outerwrapper += previewpage

            msg = self._("This page displays a indexed list "
                         "of all the media objects "
                         "in this database.  It is sorted by media title.  "
                         "There is an index "
                         "of all the media objects in this database.  "
                         "Clicking on a thumbnail "
                         "will take you to that image&#8217;s page.")
            previewpage += Html("p", msg, id="description")

        with Html("div", id="gallery") as gallery:
            previewpage += gallery
            index, indexpos = 1, 0
            num_of_images = len(media_list)
            while index <= num_of_images:
                ptitle = media_list[indexpos][0]
                person_handle = media_list[indexpos][1]
                photo = media_list[indexpos][2]

                # begin table cell and attach to table row(trow)...
                gallerycell = Html("div", class_="gallerycell")
                gallery += gallerycell

                # attach index number...
                numberdiv = Html("div", class_="indexno")
                gallerycell += numberdiv

                # attach anchor name to date cell in upper right
                # corner of grid...
                numberdiv += Html("a", index, name=index, title=index,
                                  inline=True)

                # create thumbnail
                (dummy_real_path,
                 newpath) = self.report.prepare_copy_media(photo)
                newpath = self.report.build_url_fname(newpath, image=True)
                newpathc = newpath

                # attach thumbnail to list...
                gallerycell += self.thumb_hyper_image(newpathc, "img",
                                                      person_handle, ptitle)

                index += 1
                indexpos += 1

        # begin Thumbnail Reference section...
        with Html("div", class_="content", id="references") as section:
            outerwrapper += section
            section += Html("h4", self._("References"), inline=True)

            with Html("table", class_="infolist") as table:
                section += table

                tbody = Html("tbody")
                table += tbody

                index = 1
                for ptitle, person_handle, photo in media_list:
                    trow = Html("tr")
                    tbody += trow

                    tcell1 = Html("td",
                                  self.thumbnail_link(ptitle, index),
                                  class_="ColumnRowLabel")
                    tcell2 = Html("td", ptitle, class_="ColumnName")
                    trow += (tcell1, tcell2)

                    # increase progress meter...
                    cb_progress()

                    # increase index for row number...
                    index += 1


        # add body id element
        body.attr = 'id ="ThumbnailPreview"'

        # add footer section
        # add clearline for proper styling
        footer = self.write_footer(None)
        outerwrapper += (FULLCLEAR, footer)

        # send page out for processing
        # and close the file
        if self.create_thumbs_index:
            self.xhtml_writer(thumbnailpage, output_file, sio, 0)


    def thumbnail_link(self, name, index):
        """
        creates a hyperlink for Thumbnail Preview Reference...

        @param: name    -- The image description
        @param: index   -- The image index
        """
        return Html("a", index, title=html_escape(name),
                    href="#%d" % index)

    def thumb_hyper_image(self, thumbnail_url, subdir, fname, name):
        """
        replaces media_link() because it doesn't work for this instance

        @param: thumnail_url -- The url for this thumbnail
        @param: subdir       -- The subdir prefix to add
        @param: fname        -- The file name for this image
        @param: name         -- The image description
        """
        name = html_escape(name)
        url = "/".join(self.report.build_subdirs(subdir,
                                                 fname) + [fname]) + self.ext
        with Html("div", class_="thumbnail") as thumbnail:
                    #snapshot += thumbnail

            if not self.create_thumbs_only:
                thumbnail_link = Html("a", href=url, title=name) + (
                    Html("img", src=thumbnail_url, alt=name)
                )
            else:
                thumbnail_link = Html("img", src=thumbnail_url,
                                      alt=name)
            thumbnail += thumbnail_link
        return thumbnail
