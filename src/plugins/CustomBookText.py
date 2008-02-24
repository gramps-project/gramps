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
from gettext import gettext as _

#------------------------------------------------------------------------
#
# gtk
#
#------------------------------------------------------------------------

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
from PluginUtils import register_report, TextOption
from ReportBase import Report, MenuReportOptions, CATEGORY_TEXT, MODE_BKI
import BaseDoc

#------------------------------------------------------------------------
#
# CustomText
#
#------------------------------------------------------------------------
class CustomText(Report):

    def __init__(self, database, options_class):
        """
        Create CustomText object that produces the report.
        
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
        Report.__init__(self, database, options_class)

        menu = options_class.menu
        self.top_text = menu.get_option_by_name('top').get_value()
        self.middle_text = menu.get_option_by_name('mid').get_value()
        self.bottom_text = menu.get_option_by_name('bot').get_value()
        
    def write_report(self):
        self.doc.start_paragraph('CBT-Initial')
        for line in self.top_text:
            self.doc.write_text(line)
            self.doc.write_text("\n")
        self.doc.end_paragraph()

        self.doc.start_paragraph('CBT-Middle')
        for line in self.middle_text:
            self.doc.write_text(line)
            self.doc.write_text("\n")
        self.doc.end_paragraph()

        self.doc.start_paragraph('CBT-Final')
        for line in self.bottom_text:
            self.doc.write_text(line)
            self.doc.write_text("\n")
        self.doc.end_paragraph()

#------------------------------------------------------------------------
#
# CustomTextOptions
#
#------------------------------------------------------------------------
class CustomTextOptions(MenuReportOptions):

    """
    Defines options and provides handling interface.
    """
    
    def __init__(self, name, dbase):
        MenuReportOptions.__init__(self, name, dbase)
        
    def add_menu_options(self, menu):
        
        category_name = _("Text")
        
        top = TextOption(_("Initial Text"), [""] )
        top.set_help(_("Text to display at the top."))
        menu.add_option(category_name,"top",top)
        
        mid = TextOption(_("Middle Text"), [""] )
        mid.set_help(_("Text to display in the middle"))
        menu.add_option(category_name,"mid",mid)
        
        bot = TextOption(_("Final Text"), [""] )
        bot.set_help(_("Text to display last."))
        menu.add_option(category_name,"bot",bot)

    def make_default_style(self,default_style):
        """Make the default output style for the Custom Text report."""
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=12,bold=0,italic=0)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set(pad=0.5)
        para.set_description(_('The style used for the first portion of the custom text.'))
        default_style.add_paragraph_style("CBT-Initial",para)

        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=12,bold=0,italic=0)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set(pad=0.5)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set_description(_('The style used for the middle portion of the custom text.'))
        default_style.add_paragraph_style("CBT-Middle",para)

        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=12,bold=0,italic=0)
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set(pad=0.5)
        para.set_description(_('The style used for the last portion of the custom text.'))
        default_style.add_paragraph_style("CBT-Final",para)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_report(
    name = 'custom_text',
    category = CATEGORY_TEXT,
    report_class = CustomText,
    options_class = CustomTextOptions,
    modes = MODE_BKI,
    translated_name = _("Custom Text"),
    )
