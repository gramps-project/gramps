# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
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

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import time
from TransUtils import sgettext as _

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
from gen.plug import PluginManager
from gen.plug.menu import StringOption, MediaOption, NumberOption
from Utils import media_path_full
from ReportBase import Report, MenuReportOptions, CATEGORY_TEXT
import BaseDoc

#------------------------------------------------------------------------
#
# SimpleBookTitle
#
#------------------------------------------------------------------------
class SimpleBookTitle(Report):
    """ This report class generates a title page for a book. """
    def __init__(self, database, options_class):
        """
        Create SimpleBookTitle object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        title     - Title string.
        subtitle  - Subtitle string.
        imgid     - Gramps ID of the media object to use as an image.
        imgsize   - Size for the image.
        footer    - Footer string.
        """
        Report.__init__(self, database, options_class)

        menu = options_class.menu
        self.title_string = menu.get_option_by_name('title').get_value()
        self.image_size = menu.get_option_by_name('imgsize').get_value()
        self.subtitle_string = menu.get_option_by_name('subtitle').get_value()
        self.footer_string = menu.get_option_by_name('footer').get_value()
        self.object_id = menu.get_option_by_name('imgid').get_value()
        
    def write_report(self):
        """ Generate the contents of the report """
        self.doc.start_paragraph('SBT-Title')
        self.doc.write_text(self.title_string)
        self.doc.end_paragraph()

        self.doc.start_paragraph('SBT-Subtitle')
        self.doc.write_text(self.subtitle_string)
        self.doc.end_paragraph()

        if self.object_id:
            the_object = self.database.get_object_from_gramps_id(self.object_id)
            name = media_path_full(self.database, the_object.get_path())
            if self.image_size:
                image_size = self.image_size
            else:
                image_size = min(
                        0.8 * self.doc.get_usable_width(), 
                        0.7 * self.doc.get_usable_height() )
            self.doc.add_media_object(name, 'center', image_size, image_size)

        self.doc.start_paragraph('SBT-Footer')
        self.doc.write_text(self.footer_string)
        self.doc.end_paragraph()

#------------------------------------------------------------------------
#
# SimpleBookTitleOptions
#
#------------------------------------------------------------------------
class SimpleBookTitleOptions(MenuReportOptions):

    """
    Defines options and provides handling interface.
    """
    
    def __init__(self, name, dbase):
        self.__db = dbase
        MenuReportOptions.__init__(self, name, dbase)
        
    def add_menu_options(self, menu):
        """ Add the options for this report """
        category_name = _("Report Options")
        
        title = StringOption(_('book|Title'), _('Title of the Book') )
        title.set_help(_("Title string for the book."))
        menu.add_option(category_name, "title", title)
        
        subtitle = StringOption(_('Subtitle'), _('Subtitle of the Book') )
        subtitle.set_help(_("Subtitle string for the book."))
        menu.add_option(category_name, "subtitle", subtitle)
        
        dateinfo = time.localtime(time.time())
        rname = self.__db.get_researcher().get_name()
        footer_string = _('Copyright %d %s') % (dateinfo[0], rname)
        footer = StringOption(_('Footer'), footer_string )
        footer.set_help(_("Footer string for the page."))
        menu.add_option(category_name, "footer", footer)
        
        imgid = MediaOption(_('Image'))
        imgid.set_help( _("Gramps ID of the media object to use as an image."))
        menu.add_option(category_name, "imgid", imgid)
        
        imgsize = NumberOption(_('Image Size'), 0, 0, 20, 0.1)
        imgsize.set_help(_("Size of the image in cm. A value of 0 indicates "
                           "that the image should be fit to the page."))
        menu.add_option(category_name, "imgsize", imgsize)

    def make_default_style(self, default_style):
        """Make the default output style for the Simple Boot Title report."""
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF, size=16, bold=1, italic=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set(pad=0.5)
        para.set_description(_('The style used for the title of the page.'))
        default_style.add_paragraph_style("SBT-Title", para)
    
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF, size=14, italic=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set(pad=0.5)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set_description(_('The style used for the subtitle.'))
        default_style.add_paragraph_style("SBT-Subtitle", para)

        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF, size=10, italic=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set(pad=0.5)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set_description(_('The style used for the footer.'))
        default_style.add_paragraph_style("SBT-Footer", para)

#------------------------------------------------------------------------
#
# register_report
#
#------------------------------------------------------------------------
pmgr = PluginManager.get_instance()
pmgr.register_report(
    name = 'simple_book_title',
    category = CATEGORY_TEXT,
    report_class = SimpleBookTitle,
    options_class = SimpleBookTitleOptions,
    modes = PluginManager.REPORT_MODE_BKI,
    translated_name = _("Title Page"),
    status = _("Stable"),
    description = _("Produces a title page for book reports."),
    author_name = "Brian G. Matherly",
    author_email = "brian@gramps-project.org"
    )
