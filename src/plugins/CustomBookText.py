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

# Written by Alex Roitman, 
# largely based on the SimpleBookTitle.py by Don Allingham

# $Id$

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
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
from PluginUtils import Report, ReportOptions, register_report
import BaseDoc

#------------------------------------------------------------------------
#
# CustomText
#
#------------------------------------------------------------------------
class CustomText(Report.Report):

    def __init__(self,database,person,options_class):
        """
        Creates CustomText object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        top   - Text on the top.
        mid   - Text in the middle.
        bot   - Text on the bottom.
        """
        Report.Report.__init__(self,database,person,options_class)

        self.top_text = options_class.handler.options_dict['top']
        self.middle_text = options_class.handler.options_dict['mid']
        self.bottom_text = options_class.handler.options_dict['bot']
        
    def write_report(self):
        self.doc.start_paragraph('CBT-Initial')
        self.doc.write_text(self.top_text)
        self.doc.end_paragraph()

        self.doc.start_paragraph('CBT-Middle')
        self.doc.write_text(self.middle_text)
        self.doc.end_paragraph()

        self.doc.start_paragraph('CBT-Final')
        self.doc.write_text(self.bottom_text)
        self.doc.end_paragraph()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class CustomTextOptions(ReportOptions.ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.ReportOptions.__init__(self,name,person_id)

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'top'   : '',
            'mid'   : '',
            'bot'   : '',
        }
        self.options_help = {
            'top'   : ("=str","Initial Text",
                            "Whatever String You Wish"),
            'mid'   : ("=str","Middle Text",
                            "Whatever String You Wish"),
            'bot'   : ("=str","Final Text",
                            "Whatever String You Wish"),
        }

    def add_user_options(self,dialog):
        dialog.setup_center_person = dialog.setup_paper_frame
        dialog.notebook = gtk.Notebook()
        dialog.notebook.set_border_width(6)
        dialog.window.vbox.add(dialog.notebook)

        top_sw = gtk.ScrolledWindow()
        middle_sw = gtk.ScrolledWindow()
        bottom_sw = gtk.ScrolledWindow()

        top_sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        middle_sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        bottom_sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)

        self.top_text_view = gtk.TextView()
        self.top_text_view.get_buffer().set_text(self.options_dict['top'])
        self.middle_text_view = gtk.TextView()
        self.middle_text_view.get_buffer().set_text(self.options_dict['mid'])
        self.bottom_text_view = gtk.TextView()
        self.bottom_text_view.get_buffer().set_text(self.options_dict['bot'])

        top_sw.add_with_viewport(self.top_text_view)
        middle_sw.add_with_viewport(self.middle_text_view)
        bottom_sw.add_with_viewport(self.bottom_text_view)

        dialog.add_frame_option(_('Initial Text'),"",top_sw)
        dialog.add_frame_option(_('Middle Text'),"",middle_sw)
        dialog.add_frame_option(_('Final Text'),"",bottom_sw)

    def parse_user_options(self,dialog):
        """
        Parses the custom options that we have added.
        """
        self.options_dict['top'] = unicode(
                self.top_text_view.get_buffer().get_text(
                    self.top_text_view.get_buffer().get_start_iter(),
                    self.top_text_view.get_buffer().get_end_iter(),
                    False
                ) 
            ).replace('\n',' ')

        self.options_dict['mid'] = unicode(
                self.middle_text_view.get_buffer().get_text(
                    self.middle_text_view.get_buffer().get_start_iter(),
                    self.middle_text_view.get_buffer().get_end_iter(),
                    False
                )
            ).replace('\n',' ')

        self.options_dict['bot'] = unicode(
                self.bottom_text_view.get_buffer().get_text(
                    self.bottom_text_view.get_buffer().get_start_iter(),
                    self.bottom_text_view.get_buffer().get_end_iter(),
                    False
                )
            ).replace('\n',' ')

    def make_default_style(self,default_style):
        """Make the default output style for the Custom Text report."""
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=12,bold=0,italic=0)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set(pad=0.5)
        para.set_description(_('The style used for the first portion of the custom text.'))
        default_style.add_style("CBT-Initial",para)

        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=12,bold=0,italic=0)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set(pad=0.5)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set_description(_('The style used for the middle portion of the custom text.'))
        default_style.add_style("CBT-Middle",para)

        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=12,bold=0,italic=0)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set(pad=0.5)
        para.set_description(_('The style used for the last portion of the custom text.'))
        default_style.add_style("CBT-Final",para)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_report(
    name = 'custom_text',
    category = Report.CATEGORY_TEXT,
    report_class = CustomText,
    options_class = CustomTextOptions,
    modes = Report.MODE_BKI,
    translated_name = _("Custom Text"),
    )
