#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
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

import logging
log = logging.getLogger(".")

import PluginUtils
from BasicUtils import name_displayer
import Utils
import BaseDoc
from _Constants import CATEGORY_TEXT, CATEGORY_DRAW, CATEGORY_BOOK
from _PaperMenu import paper_sizes
import os
import const
from Filters import CustomFilters

#------------------------------------------------------------------------
#
# Command-line report
#
#------------------------------------------------------------------------
class CommandLineReport:
    """
    Provides a way to generate report from the command line.
    
    """

    def __init__(self,database,name,category,option_class,options_str_dict,
                 noopt=False):
        self.database = database
        self.category = category
        self.option_class = option_class(name)
        self.show = options_str_dict.pop('show',None)
        self.options_str_dict = options_str_dict
        self.init_options(noopt)
        self.parse_option_str()
        self.show_options()

    def init_options(self,noopt):
        self.options_dict = {
            'of'        : self.option_class.handler.module_name,
            'off'       : self.option_class.handler.get_format_name(),
            'style'     : \
                    self.option_class.handler.get_default_stylesheet_name(),
            'papers'    : self.option_class.handler.get_paper_name(),
            'papero'    : self.option_class.handler.get_orientation(),
            'template'  : self.option_class.handler.get_template_name(),
            'id'        : ''
            }

        self.options_help = {
            'of'        : ["=filename","Output file name. MANDATORY"],
            'off'       : ["=format","Output file format."],
            'style'     : ["=name","Style name."],
            'papers'    : ["=name","Paper size name."],
            'papero'    : ["=num","Paper orientation number."],
            'template'  : ["=name","Template name (HTML only)."],
            'id'        : ["=ID","Gramps ID of a central person. MANDATORY"],
            'gen'       : ["=num","Number of generations to follow."],
            'pagebbg'   : ["=0/1","Page break between generations."],
            }

        if noopt:
            return

        # Add report-specific options
        for key in self.option_class.handler.options_dict.keys():
            if key not in self.options_dict.keys():
                self.options_dict[key] = \
                                   self.option_class.handler.options_dict[key]

        # Add help for report-specific options
        for key in self.option_class.options_help.keys():
            if key not in self.options_help.keys():
                self.options_help[key] = self.option_class.options_help[key]

    def parse_option_str(self):
        for opt in self.options_str_dict.keys():
            if opt in self.options_dict.keys():
                converter = Utils.get_type_converter(self.options_dict[opt])
                self.options_dict[opt] = converter(self.options_str_dict[opt])
                self.option_class.handler.options_dict[opt] = \
                                                        self.options_dict[opt]
            else:
                print "Ignoring unknown option: %s" % opt

        person_id = self.options_dict['id']
        self.person = self.database.get_person_from_gramps_id(person_id)
        id_list = []
        for person_handle in self.database.get_person_handles():
            person = self.database.get_person_from_handle(person_handle)
            id_list.append("%s\t%s" % (
                person.get_gramps_id(),
                name_displayer.display(person)))
        self.options_help['id'].append(id_list)
        self.options_help['id'].append(False)

        self.option_class.handler.output = self.options_dict['of']
        self.options_help['of'].append(os.path.join(const.user_home,
                                                    "whatever_name"))

        if self.category == CATEGORY_TEXT:
            for item in PluginUtils.textdoc_list:
                if item[7] == self.options_dict['off']:
                    self.format = item[1]
            self.options_help['off'].append(
                [ item[7] for item in PluginUtils.textdoc_list ]
            )
            self.options_help['off'].append(False)
        elif self.category == CATEGORY_DRAW:
            for item in PluginUtils.drawdoc_list:
                if item[6] == self.options_dict['off']:
                    self.format = item[1]
            self.options_help['off'].append(
                [ item[6] for item in PluginUtils.drawdoc_list ]
            )
            self.options_help['off'].append(False)
        elif self.category == CATEGORY_BOOK:
            for item in PluginUtils.bookdoc_list:
                if item[6] == self.options_dict['off']:
                    self.format = item[1]
            self.options_help['off'].append(
                [ item[6] for item in PluginUtils.bookdoc_list ]
            )
            self.options_help['off'].append(False)
        else:
            self.format = None

        for paper in paper_sizes:
            if paper.get_name() == self.options_dict['papers']:
                self.paper = paper
        self.option_class.handler.set_paper(self.paper)
        self.options_help['papers'].append(
            [ paper.get_name() for paper in paper_sizes 
                        if paper.get_name() != 'Custom Size' ] )
        self.options_help['papers'].append(False)

        self.orien = self.options_dict['papero']
        self.options_help['papero'].append([
            "%d\tPortrait" % BaseDoc.PAPER_PORTRAIT,
            "%d\tLandscape" % BaseDoc.PAPER_LANDSCAPE ] )
        self.options_help['papero'].append(False)

        self.template_name = self.options_dict['template']
        self.options_help['template'].append(os.path.join(const.user_home,
                                                          "whatever_name"))

        if self.category in (CATEGORY_TEXT,CATEGORY_DRAW):
            default_style = BaseDoc.StyleSheet()
            self.option_class.make_default_style(default_style)

            # Read all style sheets available for this item
            style_file = self.option_class.handler.get_stylesheet_savefile()
            self.style_list = BaseDoc.StyleSheetList(style_file,default_style)

            # Get the selected stylesheet
            style_name =self.option_class.handler.get_default_stylesheet_name()
            self.selected_style = self.style_list.get_style_sheet(style_name)
            
            self.options_help['style'].append(
                self.style_list.get_style_names() )
            self.options_help['style'].append(False)

    def show_options(self):
        if not self.show:
            return
        elif self.show == 'all':
            print "   Available options:"
            for key in self.options_dict.keys():
                print "      %s" % key
            print \
                "   Use 'show=option' to see description and acceptable values"
        elif self.show in self.options_dict.keys():
            print '   %s%s\t%s' % (self.show,
                                    self.options_help[self.show][0],
                                    self.options_help[self.show][1])
            print "   Available values are:"
            vals = self.options_help[self.show][2]
            if type(vals) in [list,tuple]:
                if self.options_help[self.show][3]:
                    for num in range(len(vals)):
                        print "      %d\t%s" % (num,vals[num])
                else:
                    for val in vals:
                        print "      %s" % val
            else:
                print "      %s" % self.options_help[self.show][2]

        else:
            self.show = None

#------------------------------------------------------------------------
#
# Command-line report generic task
#
#------------------------------------------------------------------------
def cl_report(database,name,category,report_class,
              options_class,options_str_dict):
    
    clr = CommandLineReport(database,name,category,
                            options_class,options_str_dict)

    # Exit here if show option was given
    if clr.show:
        return

    # write report
    try:
        clr.option_class.handler.doc = clr.format(
                    clr.selected_style,
                    BaseDoc.PaperStyle(clr.paper,clr.orien),
                    clr.template_name)
        MyReport = report_class(database, clr.person, clr.option_class)
        MyReport.doc.init()
        MyReport.begin_report()
        MyReport.write_report()
        MyReport.end_report()
    except:
        log.error("Failed to write report.", exc_info=True)
