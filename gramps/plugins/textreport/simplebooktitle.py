# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
# Copyright (C) 2008,2012  Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Paul Franklin
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

""" Simple Book Title for the book report """

# ------------------------------------------------------------------------
#
# python modules
#
# ------------------------------------------------------------------------
import time
import os

# ------------------------------------------------------------------------
#
# gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from gramps.gen.plug.menu import StringOption, MediaOption, NumberOption
from gramps.gen.utils.file import media_path_full
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.docgen import (
    FontStyle,
    ParagraphStyle,
    FONT_SANS_SERIF,
    PARA_ALIGN_CENTER,
)


# ------------------------------------------------------------------------
#
# SimpleBookTitle
#
# ------------------------------------------------------------------------
class SimpleBookTitle(Report):
    """This report class generates a title page for a book."""

    def __init__(self, database, options, user):
        """
        Create SimpleBookTitle object that produces the report.

        The arguments are:

        database        - the Gramps database instance
        options         - instance of the Options class for this report
        user            - a gen.user.User() instance

        This report needs the following parameters (class variables)
        that come in the options class.

        title     - Title string.
        subtitle  - Subtitle string.
        imgid     - Gramps ID of the media object to use as an image.
        imgsize   - Size for the image.
        footer    - Footer string.
        """
        Report.__init__(self, database, options, user)
        self._user = user

        menu = options.menu
        self.title_string = menu.get_option_by_name("title").get_value()
        self.image_size = menu.get_option_by_name("imgsize").get_value()
        self.subtitle_string = menu.get_option_by_name("subtitle").get_value()
        self.footer_string = menu.get_option_by_name("footer").get_value()
        self.media_id = menu.get_option_by_name("imgid").get_value()

    def write_report(self):
        """Generate the contents of the report"""
        self.doc.start_paragraph("SBT-Title")
        self.doc.write_text(self.title_string)
        self.doc.end_paragraph()

        self.doc.start_paragraph("SBT-Subtitle")
        self.doc.write_text(self.subtitle_string)
        self.doc.end_paragraph()

        if self.media_id:
            the_object = self.database.get_media_from_gramps_id(self.media_id)
            filename = media_path_full(self.database, the_object.get_path())
            if os.path.exists(filename):
                if self.image_size:
                    image_size = self.image_size
                else:
                    image_size = min(
                        0.8 * self.doc.get_usable_width(),
                        0.7 * self.doc.get_usable_height(),
                    )
                self.doc.add_media(filename, "center", image_size, image_size)
            else:
                self._user.warn(
                    _("Could not add photo to page"),
                    _("File %s does not exist") % filename,
                )

        self.doc.start_paragraph("SBT-Footer")
        self.doc.write_text(self.footer_string)
        self.doc.end_paragraph()


# ------------------------------------------------------------------------
#
# SimpleBookTitleOptions
#
# ------------------------------------------------------------------------
class SimpleBookTitleOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dbase):
        self.__db = dbase
        MenuReportOptions.__init__(self, name, dbase)

    def get_subject(self):
        """Return a string that describes the subject of the report."""
        return self.__title.get_value()

    def add_menu_options(self, menu):
        """Add the options for this report"""
        category_name = _("Report Options")

        self.__title = StringOption(_("Title"), _("Title of the Book", "book"))
        self.__title.set_help(_("Title string for the book."))
        menu.add_option(category_name, "title", self.__title)

        subtitle = StringOption(_("Subtitle"), _("Subtitle of the Book"))
        subtitle.set_help(_("Subtitle string for the book."))
        menu.add_option(category_name, "subtitle", subtitle)

        dateinfo = time.localtime(time.time())
        rname = self.__db.get_researcher().get_name()
        footer_string = _("Copyright %(year)d %(name)s") % {
            "year": dateinfo[0],
            "name": rname,
        }
        footer = StringOption(_("Footer"), footer_string)
        footer.set_help(_("Footer string for the page."))
        menu.add_option(category_name, "footer", footer)

        imgid = MediaOption(_("Image"))
        imgid.set_help(_("Gramps ID of the media object to use as an image."))
        menu.add_option(category_name, "imgid", imgid)

        imgsize = NumberOption(_("Image Size"), 0, 0, 20, 0.1)
        imgsize.set_help(
            _(
                "Size of the image in cm. A value of 0 indicates "
                "that the image should be fit to the page."
            )
        )
        menu.add_option(category_name, "imgsize", imgsize)

    def make_default_style(self, default_style):
        """Make the default output style for the Simple Book Title report."""
        font = FontStyle()
        font.set(face=FONT_SANS_SERIF, size=16, bold=1, italic=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set(pad=0.5)
        para.set_description(_("The style used for the title."))
        default_style.add_paragraph_style("SBT-Title", para)

        font = FontStyle()
        font.set(face=FONT_SANS_SERIF, size=14, italic=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set(pad=0.5)
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_description(_("The style used for the subtitle."))
        default_style.add_paragraph_style("SBT-Subtitle", para)

        font = FontStyle()
        font.set(face=FONT_SANS_SERIF, size=10, italic=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set(pad=0.5)
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_description(_("The style used for the footer."))
        default_style.add_paragraph_style("SBT-Footer", para)
