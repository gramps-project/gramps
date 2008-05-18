#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2008 Lukasz Rymarczyk
# Copyright (C) 2008 Raphael Ackermann
# Copyright (C) 2008 Brian G. Matherly
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


#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import sys

import logging
log = logging.getLogger(".")

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import PluginUtils
import Utils
import BaseDoc
from BasicUtils import name_displayer
from ReportBase import CATEGORY_TEXT, CATEGORY_DRAW, CATEGORY_BOOK, \
    CATEGORY_GRAPHVIZ
from _PaperMenu import paper_sizes
import os
import const

#------------------------------------------------------------------------
#
# Private Functions
#
#------------------------------------------------------------------------
def _validate_options(options, dbase):
    """
    Validate all options by making sure that their values are consistent with
    the database.
    
    menu: The Menu class
    dbase: the database the options will be applied to
    """
    if not hasattr(options, "menu"):
        return
    menu = options.menu
    
    for name in menu.get_all_option_names():
        option = menu.get_option_by_name(name)

        if isinstance(option, PluginUtils.PersonOption):
            pid = option.get_value()
            person = dbase.get_person_from_gramps_id(pid)
            if not person:
                person = dbase.get_default_person()
                if not person:
                    phandle = dbase.get_person_handles()[0]
                    person = dbase.get_person_from_handle(phandle)
                    if not person:
                        print "Please specify a person"
            if person:
                option.set_value(person.get_gramps_id())
            
        elif isinstance(option, PluginUtils.FamilyOption):
            fid = option.get_value()
            family = dbase.get_family_from_gramps_id(fid)
            if not family:
                person = dbase.get_default_person()
                family_list = person.get_family_handle_list()
                if family_list:
                    family_handle = family_list[0]
                else:
                    family_handle = dbase.get_family_handles()[0]
                family = dbase.get_family_from_handle(family_handle)
                option.set_value(family.get_gramps_id())

#------------------------------------------------------------------------
#
# Command-line report
#
#------------------------------------------------------------------------
class CommandLineReport:
    """
    Provide a way to generate report from the command line.
    """

    def __init__(self, database, name, category, option_class, options_str_dict,
                 noopt=False):
        self.database = database
        self.category = category
        self.format = None
        self.option_class = option_class(name, database)
        self.option_class.load_previous_values()
        _validate_options(self.option_class, database)
        self.show = options_str_dict.pop('show', None)
        self.options_str_dict = options_str_dict
        self.init_standard_options(noopt)
        self.init_report_options()
        self.parse_options()
        self.show_options()

    def init_standard_options(self, noopt):
        """
        Initialize the options that are hard-coded into the report system.
        """
        pmgr = PluginUtils.PluginManager.get_instance()
        _textdoc_list = pmgr.get_text_doc_list()
        _drawdoc_list = pmgr.get_draw_doc_list()
        _bookdoc_list = pmgr.get_book_doc_list()
        
        self.options_dict = {
            'of'        : self.option_class.handler.module_name,
            'off'       : self.option_class.handler.get_format_name(),
            'style'     : \
                    self.option_class.handler.get_default_stylesheet_name(),
            'papers'    : self.option_class.handler.get_paper_name(),
            'papero'    : self.option_class.handler.get_orientation(),
            'template'  : self.option_class.handler.get_template_name(),
            }

        self.options_help = {
            'of'        : ["=filename", "Output file name. MANDATORY", "", ""],
            'off'       : ["=format", "Output file format.", "", ""],
            'style'     : ["=name", "Style name.", "", ""],
            'papers'    : ["=name", "Paper size name.", "", ""],
            'papero'    : ["=num", "Paper orientation number.", "", ""],
            'template'  : ["=name", "Template name (HTML only).", "", ""],
            }

        if noopt:
            return

        self.option_class.handler.output = self.options_dict['of']
        self.options_help['of'].append(os.path.join(const.USER_HOME,
                                                    "whatever_name"))

        if self.category == CATEGORY_TEXT:
            for item in _textdoc_list:
                if item[7] == self.options_dict['off']:
                    self.format = item[1]
            if self.format is None:
                # Pick the first one as the default.
                self.format = _textdoc_list[0][1]
            self.options_help['off'][2] = \
                [ item[7] for item in _textdoc_list ]
            self.options_help['off'][3] = False
        elif self.category == CATEGORY_DRAW:
            for item in _drawdoc_list:
                if item[6] == self.options_dict['off']:
                    self.format = item[1]
            if self.format is None:
                # Pick the first one as the default.
                self.format = _drawdoc_list[0][1]
            self.options_help['off'][2] = \
                [ item[6] for item in _drawdoc_list ]
            self.options_help['off'][3] = False
        elif self.category == CATEGORY_BOOK:
            for item in _bookdoc_list:
                if item[6] == self.options_dict['off']:
                    self.format = item[1]
            if self.format is None:
                # Pick the first one as the default.
                self.format = _bookdoc_list[0][1]
            self.options_help['off'][2] = \
                [ item[6] for item in _bookdoc_list ]
            self.options_help['off'][3] = False
        else:
            self.format = None

        for paper in paper_sizes:
            if paper.get_name() == self.options_dict['papers']:
                self.paper = paper
        self.option_class.handler.set_paper(self.paper)
        self.options_help['papers'][2] = \
            [ paper.get_name() for paper in paper_sizes 
                        if paper.get_name() != _("Custom Size") ]
        self.options_help['papers'][3] = False

        self.orien = self.options_dict['papero']
        self.options_help['papero'][2] = [
            "%d\tPortrait" % BaseDoc.PAPER_PORTRAIT,
            "%d\tLandscape" % BaseDoc.PAPER_LANDSCAPE ]
        self.options_help['papero'][3] = False

        self.template_name = self.options_dict['template']
        self.options_help['template'][2] = os.path.join(const.USER_HOME,
                                                          "whatever_name")

        if self.category in (CATEGORY_TEXT, CATEGORY_DRAW):
            default_style = BaseDoc.StyleSheet()
            self.option_class.make_default_style(default_style)

            # Read all style sheets available for this item
            style_file = self.option_class.handler.get_stylesheet_savefile()
            self.style_list = BaseDoc.StyleSheetList(style_file,default_style)

            # Get the selected stylesheet
            style_name = self.option_class.handler.get_default_stylesheet_name()
            self.selected_style = self.style_list.get_style_sheet(style_name)
            
            self.options_help['style'][2] = self.style_list.get_style_names()
            self.options_help['style'][3] = False
            
    def init_report_options(self):
        """
        Initialize the options that are defined by each report.
        """
        if not hasattr(self.option_class, "menu"):
            return
        menu = self.option_class.menu
        for name in menu.get_all_option_names():
            option = menu.get_option_by_name(name)
            self.options_dict[name] = option.get_value()
            self.options_help[name] = [ "", option.get_help() ]
            
            if isinstance(option, PluginUtils.PersonOption):
                id_list = []
                for person_handle in self.database.get_person_handles():
                    person = self.database.get_person_from_handle(person_handle)
                    id_list.append("%s\t%s" % (
                        person.get_gramps_id(),
                        name_displayer.display(person)))
                self.options_help[name].append(id_list)
                self.options_help[name].append(False)
            elif isinstance(option, PluginUtils.FamilyOption):
                id_list = []
                for fhandle in self.database.get_family_handles():
                    family = self.database.get_family_from_handle(fhandle)
                    mname = ""
                    fname = ""
                    mhandle = family.get_mother_handle()
                    if mhandle:
                        mother = self.database.get_person_from_handle(mhandle)
                        if mother:
                            mname = name_displayer.display(mother)
                    fhandle = family.get_father_handle()
                    if fhandle:
                        father = self.database.get_person_from_handle(fhandle)
                        if father:
                            fname = name_displayer.display(father)
                    text = "%s:\t%s, %s" % \
                        (family.get_gramps_id(), fname, mname)
                    id_list.append(text)
                self.options_help[name].append(id_list)
                self.options_help[name].append(False)
            elif isinstance(option, PluginUtils.NoteOption):
                id_list = []
                for nhandle in self.database.get_note_handles():
                    note = self.database.get_note_from_handle(nhandle)
                    id_list.append(note.get_gramps_id())
                self.options_help[name].append(id_list)
                self.options_help[name].append(False)
            elif isinstance(option, PluginUtils.MediaOption):
                id_list = []
                for mhandle in self.database.get_media_object_handles():
                    mobject = self.database.get_object_from_handle(mhandle)
                    id_list.append(mobject.get_gramps_id())
                self.options_help[name].append(id_list)
                self.options_help[name].append(False)
            elif isinstance(option, PluginUtils.PersonListOption):
                self.options_help[name].append("")
                self.options_help[name].append(False)
            elif isinstance(option, PluginUtils.NumberOption):
                self.options_help[name].append("A number")
                self.options_help[name].append(False)
            elif isinstance(option, PluginUtils.BooleanOption):
                self.options_help[name].append(["0\tno", "1\tyes"])
                self.options_help[name].append(False)
            elif isinstance(option, PluginUtils.DestinationOption):
                self.options_help[name].append("A file system path")
                self.options_help[name].append(False)
            elif isinstance(option, PluginUtils.StringOption):
                self.options_help[name].append("Any text")
                self.options_help[name].append(False)
            elif isinstance(option, PluginUtils.TextOption):
                self.options_help[name].append("Any text")
                self.options_help[name].append(False)
            elif isinstance(option, PluginUtils.EnumeratedListOption):
                ilist = []
                for (value, description) in option.get_items():
                    ilist.append("%s\t%s" % (value, description))
                self.options_help[name].append(ilist)
                self.options_help[name].append(False)
            else:
                print "Unknown option: ", option
                
    def parse_options(self):
        """
        Load the options that the user has entered.
        """
        if not hasattr(self.option_class, "menu"):
            return
        menu = self.option_class.menu
        for opt in self.options_str_dict.keys():
            if opt in self.options_dict.keys():
                converter = Utils.get_type_converter(self.options_dict[opt])
                self.options_dict[opt] = converter(self.options_str_dict[opt])
                self.option_class.handler.options_dict[opt] = \
                                                        self.options_dict[opt]
                option = menu.get_option_by_name(opt)
                option.set_value(self.options_dict[opt])
                
            else:
                print "Ignoring unknown option: %s" % opt
                
    def show_options(self):
        """
        Print available options on the CLI.
        """
        if not self.show:
            return
        elif self.show == 'all':
            print "   Available options:"
            for key in self.options_dict.keys():
                if key in self.options_dict.keys():
                # Make the output nicer to read, assume that tab has 8 spaces
                    if len(key) < 10:
                        print "      %s\t\t%s (%s)" % (key, 
                                                    self.options_help[key][1], 
                                                    self.options_help[key][0])
                    else:
                        print "      %s\t%s (%s)" % (key, 
                                                     self.options_help[key][1], 
                                                     self.options_help[key][0])
                else:
                    print " %s" % key
            print "   Use 'show=option' to see description and acceptable values"
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
            #there was a show option given, but the option is invalid
            print ("option %s not valid. Use 'show=all' to see all valid "  
                  "options." % self.show)

#------------------------------------------------------------------------
#
# Command-line report generic task
#
#------------------------------------------------------------------------
def cl_report(database, name, category, report_class, options_class, 
              options_str_dict):
    
    clr = CommandLineReport(database, name, category, options_class, 
                            options_str_dict)

    # Exit here if show option was given
    if clr.show:
        return

    # write report
    try:
        if category in [CATEGORY_TEXT, CATEGORY_DRAW, CATEGORY_BOOK, \
                        CATEGORY_GRAPHVIZ]:
            clr.option_class.handler.doc = clr.format(
                        clr.selected_style,
                        BaseDoc.PaperStyle(clr.paper,clr.orien),
                        clr.template_name)
        MyReport = report_class(database, clr.option_class)
        MyReport.doc.init()
        MyReport.begin_report()
        MyReport.write_report()
        MyReport.end_report()
    except:
        log.error("Failed to write report.", exc_info=True)
