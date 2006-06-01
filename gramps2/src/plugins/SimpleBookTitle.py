# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2006  Donald N. Allingham
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
import os
import time
from TransUtils import sgettext as _

#------------------------------------------------------------------------
#
# gtk
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
from PluginUtils import register_report
from ReportBase import Report, ReportOptions, CATEGORY_TEXT, MODE_BKI
import BaseDoc
from Selectors import selector_factory
SelectObject = selector_factory('MediaObject')
import AddMedia
import ImgManip

#------------------------------------------------------------------------
#
# SimpleBookTitle
#
#------------------------------------------------------------------------
class SimpleBookTitle(Report):

    def __init__(self,database,person,options_class):
        """
        Creates SimpleBookTitle object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        title     - Title string.
        subtitle  - Subtitle string.
        imgid     - Gramps ID of the media object to use as an image.
        imgsize   - Size for the image.
        footer    - Footer string.
        """

        Report.__init__(self,database,person,options_class)

        self.title_string = options_class.handler.options_dict['title']
        self.image_size = options_class.handler.options_dict['imgsize']
        self.subtitle_string = options_class.handler.options_dict['subtitle']
        self.footer_string = options_class.handler.options_dict['footer']
        self.object_id = options_class.handler.options_dict['imgid']
        
    def write_report(self):

        self.doc.start_paragraph('SBT-Title')
        self.doc.write_text(self.title_string)
        self.doc.end_paragraph()

        self.doc.start_paragraph('SBT-Subtitle')
        self.doc.write_text(self.subtitle_string)
        self.doc.end_paragraph()

        if self.object_id:
            the_object = self.database.get_object_from_gramps_id(self.object_id)
            name = the_object.get_path()
            if self.image_size:
                image_size = self.image_size
            else:
                image_size = min(
                        0.8 * self.doc.get_usable_width(), 
                        0.7 * self.doc.get_usable_height() )
            self.doc.add_media_object(name,'center',image_size,image_size)

        self.doc.start_paragraph('SBT-Footer')
        self.doc.write_text(self.footer_string)
        self.doc.end_paragraph()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class SimpleBookTitleOptions(ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.__init__(self,name,person_id)

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'title'     : _('Title of the Book'),
            'subtitle'  : _('Subtitle of the Book'),
            'imgid'     : '',
            'imgsize'   : 0.0,
            'footer'    : '',
        }
        self.options_help = {
            'title'     : ("=str","Title string for the report",
                            "Whatever String You Wish"),
            'subtitle'  : ("=str","Subtitle string for the report",
                            "Whatever String You Wish"),
            'footer'    : ("=str","Footer string for the report",
                            "Whatever String You Wish"),
            'imgid'     : ("=ID","Gramps ID of the media object to use as an image.",
                            "Valid GRAMPS ID of an image."),
            'imgsize'   : ("=num","Size of the image.",
                            ["Floating point value (in cm)", 
                             "0 (to fit the page)."],
                            False),
        }

    def add_user_options(self,dialog):
        dialog.setup_center_person = dialog.setup_paper_frame
        dialog.notebook = gtk.Notebook()
        dialog.notebook.set_border_width(6)
        dialog.window.vbox.add(dialog.notebook)

        self.title_entry = gtk.Entry()
        self.title_entry.set_text(self.options_dict['title'])
        
        self.subtitle_entry = gtk.Entry()
        self.subtitle_entry.set_text(self.options_dict['subtitle'])

        footer_string = self.options_dict['footer']
        if not footer_string:
            dateinfo = time.localtime(time.time())
            name = dialog.db.get_researcher().get_name()
            footer_string = _('Copyright %d %s') % (dateinfo[0], name)
        self.footer_entry = gtk.Entry()
        self.footer_entry.set_text(footer_string)

        dialog.add_frame_option(_('Text'),_('book|Title'),self.title_entry)
        dialog.add_frame_option(_('Text'),_('Subtitle'),self.subtitle_entry)
        dialog.add_frame_option(_('Text'),_('Footer'),self.footer_entry)
        
        frame = gtk.Frame()
        frame.set_size_request(96,96)
        self.preview = gtk.Image()
        frame.add(self.preview)

        self.obj_title = gtk.Label('')

        self.remove_obj_button = gtk.Button(None,gtk.STOCK_REMOVE)
        self.remove_obj_button.connect('clicked',self.remove_obj)

        preview_table = gtk.Table(2,1)
        preview_table.set_row_spacings(10)
        preview_table.attach(frame,0,1,1,2,gtk.SHRINK|gtk.FILL,gtk.SHRINK|gtk.FILL)
        preview_table.attach(self.obj_title,0,1,0,1,gtk.SHRINK|gtk.FILL,gtk.SHRINK|gtk.FILL)

        select_obj_button = gtk.Button(_('From gallery...'))
        select_obj_button.connect('clicked',self.select_obj,dialog.db)
        select_file_button = gtk.Button(_('From file...'))
        select_file_button.connect('clicked',self.select_file,dialog.db)
        select_table = gtk.Table(1,3)
        select_table.set_col_spacings(10)
        select_table.attach(select_obj_button,
                0,1,0,1,gtk.SHRINK|gtk.FILL,gtk.SHRINK|gtk.FILL)
        select_table.attach(select_file_button,
                1,2,0,1,gtk.SHRINK|gtk.FILL,gtk.SHRINK|gtk.FILL)
        select_table.attach(self.remove_obj_button,
                2,3,0,1,gtk.SHRINK|gtk.FILL,gtk.SHRINK|gtk.FILL)

        self.size = gtk.SpinButton()
        self.size.set_digits(2)
        self.size.set_increments(1,2)
        self.size.set_range(0,20)
        self.size.set_numeric(True)
        self.size.set_value(self.options_dict['imgsize'])

        dialog.add_frame_option(_('Image'),_('Preview'),preview_table)
        dialog.add_frame_option(_('Image'),_('Select'),select_table)
        dialog.add_frame_option(_('Image'),_('Size'),self.size)

        object_id = self.options_dict['imgid']
        if object_id and dialog.db.get_object_from_gramps_id(object_id):
            the_object = dialog.db.get_object_from_gramps_id(object_id)
            self.setup_object(dialog.db,the_object)
        else:
            self.remove_obj_button.set_sensitive(False)
            self.size.set_sensitive(False)

    def parse_user_options(self,dialog):
        """
        Parses the custom options that we have added.
        """
        self.options_dict['title'] = unicode(self.title_entry.get_text())
        self.options_dict['subtitle'] = unicode(self.subtitle_entry.get_text())
        self.options_dict['footer'] = unicode(self.footer_entry.get_text())
        self.options_dict['imgsize'] = self.size.get_value()

    def remove_obj(self, obj):
        self.options_dict['imgid'] = ""
        self.obj_title.set_text('')
        self.preview.set_from_pixbuf(None)
        self.remove_obj_button.set_sensitive(False)
        self.size.set_sensitive(False)

    def select_obj(self,obj,database):
        s_o = SelectObject.SelectObject(database,_("Select an Object"))
        the_object = s_o.run()
        self.setup_object(database,the_object)

    def select_file(self,obj,database):
        a_o = AddMedia.AddMediaObject(database)
        the_object = a_o.run()
        self.setup_object(database,the_object)

    def setup_object(self,database,the_object):
        if not the_object:
            return
        self.options_dict['imgid'] = the_object.get_gramps_id()
        self.obj_title.set_text(the_object.get_description())
        icon_image = ImgManip.get_thumbnail_image(the_object.get_path(),
                                                  the_object.get_mime_type())
        self.preview.set_from_pixbuf(icon_image)
        self.remove_obj_button.set_sensitive(True)
        self.size.set_sensitive(True)

    def make_default_style(self,default_style):
        """Make the default output style for the Simple Boot Title report."""
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=16,bold=1,italic=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set(pad=0.5)
        para.set_description(_('The style used for the title of the page.'))
        default_style.add_style("SBT-Title",para)
    
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=14,italic=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set(pad=0.5)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set_description(_('The style used for the subtitle.'))
        default_style.add_style("SBT-Subtitle",para)

        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=10,italic=1)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set(pad=0.5)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set_description(_('The style used for the footer.'))
        default_style.add_style("SBT-Footer",para)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_report(
    name = 'simple_book_title',
    category = CATEGORY_TEXT,
    report_class = SimpleBookTitle,
    options_class = SimpleBookTitleOptions,
    modes = MODE_BKI,
    translated_name = _("Title Page"),
    )
