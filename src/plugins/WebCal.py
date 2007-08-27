#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Thom Sturgill
# Copyright (C) 2007  Brian G. Matherly
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Pubilc License as published by
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

"""
Web Calendar generator.
Created 4/22/07 by Thom Sturgill based on Calendar.py (with patches) 
by Doug Blank with input dialog based on NarrativeWeb.py by Don Allingham.
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
import time
import datetime
import const
import codecs
import locale
import shutil
from gettext import gettext as _
from xml.parsers import expat


try:
    set()
except:
    from sets import Set as set

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".WebPage")

#------------------------------------------------------------------------
#
# GNOME/gtk
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# GRAMPS module
#
#------------------------------------------------------------------------
import RelLib
import const
import BaseDoc
from GrampsCfg import get_researcher
from PluginUtils import register_report
from ReportBase import Report, ReportUtils, ReportOptions, \
     CATEGORY_WEB, CATEGORY_TEXT, MODE_GUI
from ReportBase._ReportDialog import ReportDialog
import Errors
import Utils
import ImgManip
import GrampsLocale
from QuestionDialog import ErrorDialog, WarningDialog
from Utils import probably_alive
from FontScale import string_trim, string_width


#------------------------------------------------------------------------
#
# constants
#
#------------------------------------------------------------------------
_CALENDAR = "calendar.css"

_character_sets = [
    [_('Unicode (recommended)'), 'utf-8'],
    ['ISO-8859-1',  'iso-8859-1' ],
    ['ISO-8859-2',  'iso-8859-2' ],
    ['ISO-8859-3',  'iso-8859-3' ],
    ['ISO-8859-4',  'iso-8859-4' ],
    ['ISO-8859-5',  'iso-8859-5' ],
    ['ISO-8859-6',  'iso-8859-6' ],
    ['ISO-8859-7',  'iso-8859-7' ],
    ['ISO-8859-8',  'iso-8859-8' ],
    ['ISO-8859-9',  'iso-8859-9' ],
    ['ISO-8859-10', 'iso-8859-10' ],
    ['ISO-8859-13', 'iso-8859-13' ],
    ['ISO-8859-14', 'iso-8859-14' ],
    ['ISO-8859-15', 'iso-8859-15' ],
    ['koi8_r',      'koi8_r',     ],
    ]

_cc = [
    '<a rel="license" href="http://creativecommons.org/licenses/by/2.5/"><img alt="Creative Commons License - By attribution" title="Creative Commons License - By attribution" src="somerights20.gif" /></a>',
    '<a rel="license" href="http://creativecommons.org/licenses/by-nd/2.5/"><img alt="Creative Commons License - By attribution, No derivations" title="Creative Commons License - By attribution, No derivations" src="somerights20.gif" /></a>',
    '<a rel="license" href="http://creativecommons.org/licenses/by-sa/2.5/"><img alt="Creative Commons License - By attribution, Share-alike" title="Creative Commons License - By attribution, Share-alike" src="somerights20.gif" /></a>',
    '<a rel="license" href="http://creativecommons.org/licenses/by-nc/2.5/"><img alt="Creative Commons License - By attribution, Non-commercial" title="Creative Commons License - By attribution, Non-commercial" src="somerights20.gif" /></a>',
    '<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/2.5/"><img alt="Creative Commons License - By attribution, Non-commercial, No derivations" title="Creative Commons License - By attribution, Non-commercial, No derivations" src="somerights20.gif" /></a>',
    '<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/2.5/"><img alt="Creative Commons License - By attribution, Non-commerical, Share-alike" title="Creative Commons License - By attribution, Non-commerical, Share-alike" src="somerights20.gif" /></a>',
    ]

#------------------------------------------------------------------------
#
# WebReport
#
#------------------------------------------------------------------------
class WebReport(Report):
    def __init__(self,database,person,options):
        """
        Creates WebReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        filter        Surname
        od        Country
        WCext        Year
        WCencoding    Alive
        WCod        Birthday
        WCcopyright    Anniv
        Month_image    Month_repeat
        WCtitle
        Note_text1
        Note_text2
        Note_text3
        Note_text4
        Note_text5
        Note_text6
        Note_text7
        Note_text8
        Note_text9
        Note_text10
        Note_text11
        Note_text12
        """
        
        self.database = database
        self.start_person = person
        self.options = options

        filter_num = options.handler.options_dict['WCfilter']
        filters = ReportUtils.get_person_filters(person)
        self.filter = filters[filter_num]

        self.ext = options.handler.options_dict['WCext']
        self.html_dir = options.handler.options_dict['WCod']
        self.copy = options.handler.options_dict['WCcopyright']
        self.encoding = options.handler.options_dict['WCencoding']
        self.Title_text  = options.handler.options_dict['WCtitle']
        self.Note  = [options.handler.options_dict['Note_text1'],options.handler.options_dict['Note_text2'],
             options.handler.options_dict['Note_text3'], options.handler.options_dict['Note_text4'],
             options.handler.options_dict['Note_text5'], options.handler.options_dict['Note_text6'],
             options.handler.options_dict['Note_text7'], options.handler.options_dict['Note_text8'],
             options.handler.options_dict['Note_text9'], options.handler.options_dict['Note_text10'],
             options.handler.options_dict['Note_text11'],options.handler.options_dict['Note_text12']]
        self.Month_image = options.handler.options_dict['Month_image']
        self.Month_repeat = options.handler.options_dict['Month_repeat']
        self.Country = options.handler.options_dict['Country']
        self.Year = options.handler.options_dict['Year']
        self.Surname = options.handler.options_dict['Surname']
        self.Alive = options.handler.options_dict['alive']
        self.Birthday = options.handler.options_dict['birthdays']
        self.Anniv = options.handler.options_dict['anniversaries']
        self.Serif_fonts = options.handler.options_dict['Serif_fonts']
        self.SanSerif_fonts = options.handler.options_dict['SanSerif_fonts']
        self.Home_link = options.handler.options_dict['Home_link']

    def get_short_name(self, person, maiden_name = None):
        """ Returns person's name, unless maiden_name given, unless married_name listed. """
        # Get all of a person's names:
        primary_name = person.get_primary_name()
        married_name = None
        names = [primary_name] + person.get_alternate_names()
        for n in names:
            if int(n.get_type()) == RelLib.NameType.MARRIED:
                married_name = n
        # Now, decide which to use:
        if maiden_name != None:
            if married_name != None:
                first_name, family_name = married_name.get_first_name(), married_name.get_surname()
                call_name = married_name.get_call_name()
            else:
                first_name, family_name = primary_name.get_first_name(), maiden_name
                call_name = primary_name.get_call_name()
        else:
            first_name, family_name = primary_name.get_first_name(), primary_name.get_surname()
            call_name = primary_name.get_call_name()
        # If they have a nickname use it
        if call_name != None and call_name.strip() != "":
            first_name = call_name.strip()
        else: # else just get the first name:
            first_name = first_name.strip()
            if " " in first_name:
                first_name, rest = first_name.split(" ", 1) # just one split max
        return ("%s %s" % (first_name, family_name)).strip()

    def add_day_item(self, text, year, month, day):
        month_dict = self.calendar.get(month, {})
        day_list = month_dict.get(day, [])
        day_list.append(text)
        month_dict[day] = day_list
        self.calendar[month] = month_dict

    def get_holidays(self, year, country = "United States"):
        """ Looks in multiple places for holidays.xml files """
        locations = [const.pluginsDir,
                     os.path.join(const.home_dir,"plugins")]
        holiday_file = 'holidays.xml'
        for dir in locations:
            holiday_full_path = os.path.join(dir, holiday_file)
            if os.path.exists(holiday_full_path):
                self.process_holiday_file(holiday_full_path, year, country)

    def process_holiday_file(self, filename, year, country):
        """ This will process a holiday file """
        parser = Xml2Obj()
        element = parser.Parse(filename)
        calendar = Holidays(element, country)
        date = datetime.date(year, 1, 1)
        while date.year == year:
            holidays = calendar.check_date( date )
            for text in holidays:
                self.add_day_item(text, date.year, date.month, date.day)
            date = date.fromordinal( date.toordinal() + 1)

    def write_css(self):
        """
        Create the CSS file.
        """
        # simplify the style and weight printing
        font_style = ['normal','italic']
        font_weight = ['normal','bold']
        
        # use user defined font families
        font_family = [self.SanSerif_fonts,self.Serif_fonts]
        
        default_style = BaseDoc.StyleSheet()
        self.options.make_default_style(default_style)

        # Read all style sheets available for this item
        style_file = self.options.handler.get_stylesheet_savefile()
        self.style_list = BaseDoc.StyleSheetList(style_file,default_style)

        # Get the selected stylesheet
        style_name = self.options.handler.get_default_stylesheet_name()
        self.selected_style = self.style_list.get_style_sheet(style_name)
        default_style = BaseDoc.StyleSheet(self.selected_style)
        #
        # NAVIGATION BLOCK
        #
        of = self.create_file(_CALENDAR)
        of.write('ul#navlist { padding: 0;\n\tmargin: 0;\n\tlist-style-type: none;')
        of.write('\n\tfloat: left;\n\twidth: 100%;')
        of.write('\n\tcolor: #FFFFFF;\n\tbackground-color: #003366;\n\t}\n')
        of.write('ul#navlist li { display: inline; }\n')
        of.write('ul#navlist li a { float: left;\n\twidth: 2.8em;')
        of.write('\n\tcolor: #FFFFFF;\n\tbackground-color: #003366;')
        of.write('\n\tpadding: 0.2em 1em;\n\ttext-decoration: none;')
        of.write('\n\tborder-right: 1px solid #FFFFFF;\n\t}\n')
        of.write('ul#navlist li a:hover { background-color: #336699;')
        of.write('\n\tcolor: #FFFFFF;\n\t}\n')
        #
        # HEADER / BODY BACKGROUND 
        #
        of.write('h1 {')
        style = default_style.get_paragraph_style("WC-Title")
        font = style.get_font()
        italic =  font_style[font.get_italic()]
        bold =  font_weight[font.get_bold()]
        family = font_family[font.get_type_face()]
        color = "#%02X%02X%02X" % font.get_color()
        of.write('\tfont-family: %s;\n\tfont-size: %dpt;\n'
         '\tfont-style: %s;\n\tfont-weight: %s;\n'
         '\tcolor: %s;\n\ttext-align: %s;\n\t}\n'
                 % (family, font.get_size(), italic, bold,
                    color, style.get_alignment_text()))
        of.write('body { background-color: #%02X%02X%02X;\n}\n' % style.get_background_color() )
        #
        # CALENDAR TABLE
        #
        of.write('.calendar { ') 
        style = default_style.get_paragraph_style("WC-Table")
        font = style.get_font()
        italic =  font_style[font.get_italic()]
        bold =  font_weight[font.get_bold()]
        family = font_family[font.get_type_face()]
        color = "#%02X%02X%02X" % font.get_color()
        of.write('font-family: %s;\n\tfont-size: %dpt;\n'
                 '\tfont-style: %s;\n\tfont-weight: %s;\n'
                 '\tcolor: %s;\n\ttext-align: %s;\n'
                 % (family, font.get_size(), italic, bold, 
                    color, style.get_alignment_text()))
        of.write('\tbackground-color: #%02X%02X%02X;\n}\n' % style.get_background_color() )
        #
        # MONTH NAME
        #
        style = default_style.get_paragraph_style("WC-Month")
        of.write('.cal_month { border-bottom-width: 0;\n')
        font = style.get_font()
        italic =  font_style[font.get_italic()]
        bold =  font_weight[font.get_bold()]
        family = font_family[font.get_type_face()]
        color = "#%02X%02X%02X" % font.get_color()
        mon_backcolor = "#%02X%02X%02X" % style.get_background_color()
        of.write('\tfont-family:%s;\n\tfont-size: %dpt;\n'
         '\tfont-style: %s;\n\tfont-weight: %s;\n'
         '\tcolor: %s;\n\ttext-align: %s;\n'
                 % (family, font.get_size(), italic, bold, color, style.get_alignment_text()))
        if self.Month_image.strip() != "":
            of.write('\tbackground-image: URL( %s );\n' % self.Month_image)
            of.write('\tbackground-repeat: %s;\n' % self.options.repeat_options[self.Month_repeat] )
        of.write('\tbackground-color: %s;\n}\n' % mon_backcolor )
        #
        # WEEKDAY NAMES
        #
        of.write('.cal_sun { border-top-width: 0;\n\tborder-right-width: 0;')
        of.write('\n\tborder-style: solid;  ')
        of.write('background-color: %s }\n' % mon_backcolor )
        of.write('.cal_weekday { border-top-width: 0;\n\tborder-left-width: 0;\n\tborder-right-width: 0;  ')
        of.write('\n\tborder-style: solid;\n\tbackground-color: %s }\n' % mon_backcolor )
        of.write('.cal_sat { border-top-width: 0;\n\tborder-left-width: 0;\n')
        of.write('\tborder-right-width: 0;\n\tborder-style: solid;')
        of.write('\n\tbackground-color: %s }\n' % mon_backcolor )
        #of.write('.cal_day_num { text-align: right;\n\tfont-size: x-large;\n\tfont-weight: bold;}\n')
        #
        # CALENDAR ENTRY TEXT
        #
        style = default_style.get_paragraph_style("WC-Text")
        of.write('.cal_text { vertical-align:bottom;\n')
        font = style.get_font()
        italic =  font_style[font.get_italic()]
        bold =  font_weight[font.get_bold()]
        family = font_family[font.get_type_face()]
        color = "#%02X%02X%02X" % font.get_color()
        msg_backcolor = "#%02X%02X%02X" % style.get_background_color()
        of.write('\tfont-family:%s;\n\tfont-size: %dpt;\n'
         '\tfont-style: %s;\n\tfont-weight: %s;\n'
         '\tcolor: %s;\n\ttext-align: %s;\n\t}\n'
                 % (family, font.get_size(), italic, bold, color, style.get_alignment_text()))
        of.write('.cal_row { height: 70px;\n\tborder-style: solid;\n\t}\n')
        of.write('.cal_cell_hilite {background-color: %s;}\n' % msg_backcolor )
        #
        # CALENDAR NOTE TEXT
        #
        style = default_style.get_paragraph_style("WC-Note")
        font = style.get_font()
        italic =  font_style[font.get_italic()]
        bold =  font_weight[font.get_bold()]
        family = font_family[font.get_type_face()]
        color = "#%02X%02X%02X" % font.get_color()
        backcolor = "#%02X%02X%02X" % style.get_background_color()
        of.write('.cal_cell { background-color: %s;}\n' % backcolor )
        of.write('.cal_note {\n')
        of.write('\tfont-family:%s;\n\tfont-size: %dpt;\n'
         '\tfont-style: %s;\n\tfont-weight: %s;\n'
         '\tcolor: %s;\n\ttext-align: %s;\n'
         '\tbackground-color: %s;\n\t}\n'
                 % (family, font.get_size(), italic, bold, color, style.get_alignment_text(), backcolor))
        # 
        # FOOTER AND DONE
        #
        of.write('.footer { text-align: center;\n\tfont-size:small; }\n')
        of.write('img { border: 0; }\n')
        of.close()


    def write_footer(self,of):
        author = get_researcher().get_name()
        value = unicode(time.strftime('%x',time.localtime(time.time())),
                        GrampsLocale.codeset)
        msg = _('Generated by <a href="http://gramps-project.org">'
                'GRAMPS</a> on %(date)s') % { 'date' : value }
        of.write('    </table>\n')
        of.write('   <div class="footer">')
        of.write(msg)
        of.write('<p><a href="http://validator.w3.org/check?uri=referer"><img ')
        of.write('src="http://www.w3.org/Icons/valid-xhtml10" ')
        of.write('alt="Valid XHTML 1.0 Transitional" height="31" width="88" /></a></p>\n')
        if self.copy > 0 and self.copy <= 6:
            text = _cc[self.copy-1]
            from_path = os.path.join(const.image_dir,"somerights20.gif")
            shutil.copyfile(from_path,os.path.join(self.html_dir,"somerights20.gif"))
        else:
            text = "&copy; %s %s" % (time.localtime()[0], author) 
        of.write(text)
        of.write('</div>\n')
        of.write('  </body>\n')
        of.write('</html>\n')

    def write_header(self,of):
        author = get_researcher().get_name()
        of.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"\n')
        of.write('        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-loose.dtd">\n')
        #xmllang = Utils.xml_lang()
        of.write('<html>\n')
        of.write('<head>\n  <title>%s</title>\n' % self.Title_text)
        of.write('  <meta http-equiv="Content-Type" content="text/html;charset=%s" />\n' % self.encoding)
        of.write('  <meta name="robots" content="noindex" />\n')
        of.write('  <meta name="generator" content="GRAMPS 2.26" />\n')
        of.write('  <meta name="author" content="%s" />\n' % author)
        of.write('  <link href="%s" ' % _CALENDAR)
        of.write('rel="stylesheet" type="text/css" media="screen" />\n')
        of.write('  <link href="/favicon.ico" rel="Shortcut Icon" />\n')
        #of.write('<!-- %sId%s -->\n' % ('$','$'))
        of.write('</head>\n')
        of.write('<body>\n')
        of.write('    <ul id="navlist">\n')
        if self.Home_link.strip() != "":
            of.write('      <li><a href="%s">HOME</a></li>\n' % self.Home_link)      
        for month in range(1, 13):
            of.write('      <li><a href="Calendar_%s%d.html">%s</a></li>\n' % (GrampsLocale.short_months[month],self.Year,GrampsLocale.short_months[month]))
        of.write('    </ul>\n')

    def create_file(self,name):
        page_name = os.path.join(self.html_dir,name)
        of = codecs.EncodedFile(open(page_name, "w"),'utf-8',self.encoding,'xmlcharrefreplace')
        return of

    def close_file(self,of):
        of.close()

    def write_report(self):
        """ The short method that runs through each month and creates a page. """
        # initialize the dict to fill:
        self.calendar = {}
        self.progress = Utils.ProgressMeter(_("Generate HTML calendars"),'')

        # Generate the CSS file
        self.write_css()

        # get the information, first from holidays:
        if self.Country != 0: # Don't include holidays
            self.get_holidays(self.Year, _countries[self.Country]) # _country is currently global
        # get data from database:
        self.collect_data()
        # generate the report:
        self.progress.set_pass(_("Creating Calendar pages"),12)

        for month in range(1, 13):
            self.progress.step()
            self.print_page(month)
        self.progress.close()

    def print_page(self, month):
        """
        This method actually writes the calendar page.
        """
        year = self.Year
        title = "%s %d" % (GrampsLocale.long_months[month], year)
        cal_file = "Calendar_%s%d.html" % (GrampsLocale.short_months[month], year)
        of = self.create_file(cal_file)
        self.write_header(of)
        of.write(' <h1>%s</h1>\n' % self.Title_text)
        of.write('<table border="1px" cellspacing="0" cellpadding="1" width="100%" class="calendar">\n')
        of.write('  <tr>\n    <td  colspan="7" align="center" class="cal_month">\n')
        of.write('      %s</td></tr>\n   <tr>\n' % title)

        current_date = datetime.date(year, month, 1)
        if current_date.isoweekday() != 7: # start dow here is 7, sunday
            current_ord = current_date.toordinal() - current_date.isoweekday()
        else:
            current_ord = current_date.toordinal()
        of.write('    <td width="14%" align="center" class="cal_sun">') 
        of.write(GrampsLocale.short_days[1])
        of.write('</td>\n')
        for day_col in range(5):
            of.write('    <td width="14%" align="center" class="cal_weekday">') 
            of.write(GrampsLocale.short_days[day_col+2])
            of.write('</td>\n')
        of.write('    <td width="14%" align="center" class="cal_sat">')
        of.write(GrampsLocale.short_days[7])
        of.write('</td>\n   </tr>\n')

        for week_row in range(6):
            first = True
            last = True
            of.write('     <tr valign="top" class="cal_row">\n')
            something_this_week = 0
            colspan = 0
            for day_col in range(7):
                colspan += 1
                thisday = current_date.fromordinal(current_ord)
                if thisday.month == month:
                    list = self.calendar.get(month, {}).get(thisday.day, [])
                    if list > []:
                        cellclass = "cal_cell_hilite"
                    else:
                        cellclass = "cal_cell"
                    if first:
                        first = False
                        if day_col > 1:
                           of.write('      <td colspan="%s" class="cal_cell">&nbsp;</td>\n' % str(day_col))
                        elif day_col == 1:
                           of.write('      <td class="cal_cell">&nbsp;</td>\n')
                    of.write('      <td class="%s">%s' % (cellclass,str(thisday.day)))
                    something_this_week = 1
                    if list > []:
                        of.write('<div class="cal_text">')
                        for p in list:
                            lines = p.count("\n") + 1 # lines in the text
                            current = 0
                            for line in p.split("\n"):
                                of.write(line)
                                of.write('<br />')
                                current += 1
                        of.write('</div>')
                    of.write('</td>\n')
                else:
                    # at bottom of calendar
                    if thisday.month > month and thisday.year >= year:
                        # only do it once per row
                        if last == True:
                            last = False
                            of.write('      <td colspan="')
                            of.write(str(7 - day_col))
                            of.write('"')
                            if week_row == 4:
                                of.write(' class="cal_cell">&nbsp;</td>\n')
                                continue
                            if week_row == 5:
                                of.write(' class="cal_note">')
                                if self.Note[month-1].strip() != '':
                                   of.write(self.Note[month-1])
                                else:
                                    of.write("&nbsp;")
                                of.write('</td>\n')
                                continue
                            of.write('</div></td>\n')
                        continue
                #of.write('\n')
                current_ord += 1
            if week_row == 5 and month == 12:
                of.write('      <td colspan="%s" class="cal_note">' % str(colspan))
                if self.Note[month-1].strip() != '':
                    of.write(self.Note[month-1])
                else:
                    of.write("&nbsp;")
                of.write('</td>\n')
            of.write('     </tr>\n')
        self.write_footer(of)
        self.close_file(of)

    def collect_data(self):
        """
        This method runs through the data, and collects the relevant dates
        and text.
        """
        people = self.filter.apply(self.database,
                                   self.database.get_person_handles(sort_handles=False))
        for person_handle in people:
            person = self.database.get_person_from_handle(person_handle)
            birth_ref = person.get_birth_ref()
            birth_date = None
            if birth_ref:
                birth_event = self.database.get_event_from_handle(birth_ref.ref)
                birth_date = birth_event.get_date_object()
            living = probably_alive(person, self.database, self.Year, 0)
            if self.Birthday and birth_date != None and ((self.Alive and living) or not self.Alive):
                year = birth_date.get_year()
                month = birth_date.get_month()
                day = birth_date.get_day()
                age = self.Year - year
                # add some things to handle maiden name:
                father_lastname = None # husband, actually
                if self.Surname == 0: # get husband's last name:
                    if person.get_gender() == RelLib.Person.FEMALE:
                        family_list = person.get_family_handle_list()
                        if len(family_list) > 0:
                            fhandle = family_list[0] # first is primary
                            fam = self.database.get_family_from_handle(fhandle)
                            father_handle = fam.get_father_handle()
                            mother_handle = fam.get_mother_handle()
                            if mother_handle == person_handle:
                                if father_handle:
                                    father = self.database.get_person_from_handle(father_handle)
                                    if father != None:
                                        father_lastname = father.get_primary_name().get_surname()
                short_name = self.get_short_name(person, father_lastname)
                self.add_day_item("%s, %d" % (short_name, age), year, month, day)
            if self.Anniv and ((self.Alive and living) or not self.Alive):
                family_list = person.get_family_handle_list()
                for fhandle in family_list:
                    fam = self.database.get_family_from_handle(fhandle)
                    father_handle = fam.get_father_handle()
                    mother_handle = fam.get_mother_handle()
                    if father_handle == person.get_handle():
                        spouse_handle = mother_handle
                    else:
                        continue # with next person if this was the marriage event
                    if spouse_handle:
                        spouse = self.database.get_person_from_handle(spouse_handle)
                        if spouse:
                            spouse_name = self.get_short_name(spouse)
                            short_name = self.get_short_name(person)
                            if self.Alive:
                                if not probably_alive(spouse, self.database, self.Year, 0):
                                    continue
                            married = True
                            for event_ref in fam.get_event_ref_list():
                                event = self.database.get_event_from_handle(event_ref.ref)
                    if event and int(event.get_type()) in [RelLib.EventType.DIVORCE,
                                                           RelLib.EventType.ANNULMENT,
                                                            RelLib.EventType.DIV_FILING]:
                            married = False
                            if married:
                                for event_ref in fam.get_event_ref_list():
                                    event = self.database.get_event_from_handle(event_ref.ref)
                                    event_obj = event.get_date_object()
                                    year = event_obj.get_year()
                                    month = event_obj.get_month()
                                    day = event_obj.get_day()
                                    years = self.Year - year
                                    text = _("%(spouse)s and\n %(person)s, %(nyears)d") % {
                                        'spouse' : spouse_name,
                                        'person' : short_name,
                                        'nyears' : years,
                                        }
                                    self.add_day_item(text, year, month, day)

        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class WebReportOptions(ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,database=None,person_id=None):
        ReportOptions.__init__(self,name,person_id)
        self.db = database
        
    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
             'WCfilter'        : 0,
             'WCod'            : os.path.join(const.user_home,"WEBCAL"),
             'WCcopyright'     : 0,
             'WCtitle'         : _('My Family Calendar'), 
             'WCext'           : 'html',
             'WCencoding'      : 'utf-8',
             'Month_image'     : '',
             'Month_repeat'    : 1,
             'Note_text1'      : 'This prints in January',                 
             'Note_text2'      : 'This prints in February',
             'Note_text3'      : 'This prints in March',
             'Note_text4'      : 'This prints in April',
             'Note_text5'      : 'This prints in May',
             'Note_text6'      : 'This prints in June',
             'Note_text7'      : 'This prints in July',
             'Note_text8'      : 'This prints in August',
             'Note_text9'      : 'This prints in September',
             'Note_text10'     : 'This prints in October',
             'Note_text11'     : 'This prints in November',
             'Note_text12'     : 'This prints in December',
             'Year'            : time.localtime()[0],
             'Country'         : 4,
             'Surname'         : 1,
             'alive'           : 1,
             'birthdays'       : 1,
             'anniversaries'   : 1,
             'SanSerif_fonts'  : '"Verdana","Helvetica","Arial",sans-serif',
             'Serif_fonts'     : '"Georgia","Times New Roman","Times",serif',
             'Home_link'       : '../index.html',
        }

        self.options_help = {
        }

    def add_user_options(self,dialog):

        ext_msg = _("File extension")

        self.ext = gtk.combo_box_new_text()
        self.ext_options = ['.html','.htm','.shtml','.php','.php3','.cgi']
        for text in self.ext_options:
            self.ext.append_text(text)

        self.copy = gtk.combo_box_new_text()
        self.copy_options = [
            _('Standard copyright'),
            _('Creative Commons - By attribution'),
            _('Creative Commons - By attribution, No derivations'),
            _('Creative Commons - By attribution, Share-alike'),
            _('Creative Commons - By attribution, Non-commercial'),
            _('Creative Commons - By attribution, Non-commercial, No derivations'),
            _('Creative Commons - By attribution, Non-commercial, Share-alike'),
            _('No copyright notice'),
            ]
        for text in self.copy_options:
            self.copy.append_text(text)

        def_ext = "." + self.options_dict['WCext']
        self.ext.set_active(self.ext_options.index(def_ext))

        index = self.options_dict['WCcopyright']
        self.copy.set_active(index)

        cset_node = None
        cset = self.options_dict['WCencoding']

        store = gtk.ListStore(str,str)
        for data in _character_sets:
            if data[1] == cset:
                cset_node = store.append(row=data)
            else:
                store.append(row=data)
        self.encoding = GrampsNoteComboBox(store,cset_node)

        dialog.add_option(ext_msg,self.ext)
        dialog.add_option(_('Character set encoding'),self.encoding)
        dialog.add_option(_('Copyright'),self.copy)


        title = _("Content Options")

        year_msg = "Year of calendar"
        country_msg = "Country for holidays"
        surname_msg = "Birthday surname"
        alive_msg = "Only include living people"
        birthday_msg = "Include birthdays"
        anniversary_msg = "Include anniversaries"
        
        filter_index = self.options_dict['WCfilter']
        filter_list = ReportUtils.get_person_filters(dialog.person)
        self.filter_menu = gtk.combo_box_new_text()
        for filter in filter_list:
            self.filter_menu.append_text(filter.get_name())
        if filter_index > len(filter_list):
            filter_index = 0
        self.filter_menu.set_active(filter_index)

        self.year = gtk.SpinButton()
        self.year.set_digits(0)
        self.year.set_increments(1,2)
        self.year.set_range(0,2100)
        self.year.set_numeric(True)
        self.year.set_value(self.options_dict['Year'])

        self.Country_options = map(lambda c: ("", c, c), _countries)
        self.Country = gtk.ComboBox()
        store = gtk.ListStore(str)
        self.Country.set_model(store)
        cell = gtk.CellRendererText()
        self.Country.pack_start(cell,True)
        self.Country.add_attribute(cell,'text',0)
        for item in self.Country_options:
            store.append(row=[item[2]])
        self.Country.set_active(self.options_dict['Country'])

        self.alive = gtk.CheckButton(_('Check to include ONLY the living'))
        self.alive.set_active(self.options_dict['alive'])

        self.surname = gtk.CheckButton(_('Check for wives to use maiden name'))
        self.surname.set_active(self.options_dict['Surname'])

        self.birthday = gtk.CheckButton(_('Check to include birthdays'))
        self.birthday.set_active(self.options_dict['birthdays'])

        self.anniversary = gtk.CheckButton(_('Check to include anniversaries'))
        self.anniversary.set_active(self.options_dict['anniversaries'])

        dialog.add_frame_option(title,_('Filter'),self.filter_menu)
        dialog.add_frame_option(title,year_msg,self.year)
        dialog.add_frame_option(title,country_msg,self.Country)
        dialog.add_frame_option(title,surname_msg,self.surname)
        dialog.add_frame_option(title,alive_msg,self.alive)
        dialog.add_frame_option(title,birthday_msg,self.birthday)
        dialog.add_frame_option(title,anniversary_msg,self.anniversary)


        title = _("Misc Options")
    
        self.Serif_fonts = gtk.Entry()
        self.Serif_fonts.set_text(str(self.options_dict['Serif_fonts']))

        self.SanSerif_fonts = gtk.Entry()
        self.SanSerif_fonts.set_text(str(self.options_dict['SanSerif_fonts']))

        self.Month_image = gtk.Entry()
        self.Month_image.set_text(str(self.options_dict['Month_image']))

        self.Home_link = gtk.Entry()
        self.Home_link.set_text(str(self.options_dict['Home_link']))

        self.repeat_options = [_('no-repeat'),_('repeat'),
                               _('repeat-x'),_('repeat-y')]
        self.Month_repeat = gtk.combo_box_new_text()
        for text in self.repeat_options:
            self.Month_repeat.append_text(text)
        index = self.options_dict['Month_repeat']
        self.Month_repeat.set_active(index)

        self.Title_text = gtk.Entry()
        self.Title_text.set_text(self.options_dict['WCtitle'])

        dialog.add_frame_option(title,_('Calendar Title'),self.Title_text)
        dialog.add_frame_option(title,_('Home link'),self.Home_link)
        dialog.add_frame_option(title,_('Serif font family'),self.Serif_fonts)
        dialog.add_frame_option(title,_('San-Serif font family'),self.SanSerif_fonts)
        dialog.add_frame_option(title,_('Background Image'),self.Month_image)
        dialog.add_frame_option(title,_('Image Repeat'),self.Month_repeat)

    
        title = _("Mos. 1-6 Notes")

        note_msg  = [_('Jan Note'),_('Feb Note'),_('Mar Note'),_('Apr Note'),
                     _('May Note'),_('Jun Note'),_('Jul Note'),_('Aug Note'),
                     _('Sep Note'),_('Oct Note'),_('Nov Note'),_('Dec Note')]

        self.Note_text1 = gtk.Entry()
        self.Note_text1.set_text(str(self.options_dict['Note_text1']))
    
        self.Note_text2 = gtk.Entry()
        self.Note_text2.set_text(str(self.options_dict['Note_text2']))
    
        self.Note_text3 = gtk.Entry()
        self.Note_text3.set_text(str(self.options_dict['Note_text3']))
    
        self.Note_text4 = gtk.Entry()
        self.Note_text4.set_text(str(self.options_dict['Note_text4']))
    
        self.Note_text5 = gtk.Entry()
        self.Note_text5.set_text(str(self.options_dict['Note_text5']))
    
        self.Note_text6 = gtk.Entry()
        self.Note_text6.set_text(str(self.options_dict['Note_text6']))

        dialog.add_frame_option(title,note_msg[0],self.Note_text1)
        dialog.add_frame_option(title,note_msg[1],self.Note_text2)
        dialog.add_frame_option(title,note_msg[2],self.Note_text3)
        dialog.add_frame_option(title,note_msg[3],self.Note_text4)
        dialog.add_frame_option(title,note_msg[4],self.Note_text5)
        dialog.add_frame_option(title,note_msg[5],self.Note_text6)
    
        title = _("Mos. 7-12 Notes")

        self.Note_text7 = gtk.Entry()
        self.Note_text7.set_text(str(self.options_dict['Note_text7']))
    
        self.Note_text8 = gtk.Entry()
        self.Note_text8.set_text(str(self.options_dict['Note_text8']))
    
        self.Note_text9 = gtk.Entry()
        self.Note_text9.set_text(str(self.options_dict['Note_text9']))
    
        self.Note_text10 = gtk.Entry()
        self.Note_text10.set_text(str(self.options_dict['Note_text10']))
    
        self.Note_text11 = gtk.Entry()
        self.Note_text11.set_text(str(self.options_dict['Note_text11']))
    
        self.Note_text12 = gtk.Entry()
        self.Note_text12.set_text(str(self.options_dict['Note_text12']))
    
        dialog.add_frame_option(title,note_msg[6],self.Note_text7)
        dialog.add_frame_option(title,note_msg[7],self.Note_text8)
        dialog.add_frame_option(title,note_msg[8],self.Note_text9)
        dialog.add_frame_option(title,note_msg[9],self.Note_text10)
        dialog.add_frame_option(title,note_msg[10],self.Note_text11)
        dialog.add_frame_option(title,note_msg[11],self.Note_text12)

    def parse_user_options(self,dialog):
        """ Save the user selected choices for later use."""
        
        index = self.ext.get_active()
        if index >= 0:
            html_ext = self.ext_options[index]
        else:
            html_ext = "html"
        if html_ext[0] == '.':
            html_ext = html_ext[1:]
        self.options_dict['WCext']           = html_ext
        self.options_dict['WCfilter']        = int(self.filter_menu.get_active())
        self.options_dict['WCencoding']      = self.encoding.get_handle()
        self.options_dict['WCod']            = dialog.target_path
        self.options_dict['WCcopyright']     = self.copy.get_active()
        self.options_dict['WCtitle']         = unicode(self.Title_text.get_text())
        self.options_dict['Note_text1']      = unicode(self.Note_text1.get_text())
        self.options_dict['Note_text2']      = unicode(self.Note_text2.get_text())
        self.options_dict['Note_text3']      = unicode(self.Note_text3.get_text())
        self.options_dict['Note_text4']      = unicode(self.Note_text4.get_text())
        self.options_dict['Note_text5']      = unicode(self.Note_text5.get_text())
        self.options_dict['Note_text6']      = unicode(self.Note_text6.get_text())
        self.options_dict['Note_text7']      = unicode(self.Note_text7.get_text())
        self.options_dict['Note_text8']      = unicode(self.Note_text8.get_text())
        self.options_dict['Note_text9']      = unicode(self.Note_text9.get_text())
        self.options_dict['Note_text10']     = unicode(self.Note_text10.get_text())
        self.options_dict['Note_text11']     = unicode(self.Note_text11.get_text())
        self.options_dict['Note_text12']     = unicode(self.Note_text12.get_text())
        self.options_dict['Year']            = self.year.get_value_as_int()
        self.options_dict['Country']         = self.Country.get_active()
        self.options_dict['Surname']         = int(self.surname.get_active())
        self.options_dict['alive']           = int(self.alive.get_active())
        self.options_dict['birthdays']       = int(self.birthday.get_active())
        self.options_dict['anniversaries']   = int(self.anniversary.get_active())
        self.options_dict['SanSerif_fonts']  = unicode(self.SanSerif_fonts.get_text())
        self.options_dict['Serif_fonts']     = unicode(self.Serif_fonts.get_text())
        self.options_dict['Home_link']       = unicode(self.Home_link.get_text())

    #------------------------------------------------------------------------
    #
    # Callback functions from the dialog
    #
    #------------------------------------------------------------------------
    def make_default_style(self,default_style):
        """Make the default output style for the Web Calendar
        There are 5 named styles for this report.

        WC-Title - The header for the page.
        WC-Month - The Month name block for the calendar.
        WC-Text  - The text format for the body of the calendar. 
        WC-Note  - The text placed at the bottom of each calendar.
        WC-Table - controls the overall appearance of the calendar table.

    """
        #
        # WC-Title
        #
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SERIF,size=24,bold=1,italic=1,color=(0x80,0x0,0x0))
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set(bgcolor=((0xb0,0xc4,0xde)))
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set_description(_('The style used for the title ("My Family Calendar") of the page. The background color sets the PAGE background. Borders DO NOT work.'))
        default_style.add_paragraph_style("WC-Title",para)
        #
        # WC-Month
        #
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SERIF,size=48,bold=1,italic=1,color=((0x80,0x0,0x0)))
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set(bgcolor=((0xf0,0xe6,0x8c)))
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set_description(_('The style used for the month name and year, it controls the font face, size, style, color and the background color of the block, including the day-name area. Inclusion of a graphic does not cover the day-name area.'))
        default_style.add_paragraph_style("WC-Month",para)
        #
        # WC-Text
        #
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SERIF,size=16,italic=1,color=((0x80,0x0,0x0)))
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set(bgcolor=((0xf0,0xf8,0xff)))
        para.set_alignment(BaseDoc.PARA_ALIGN_LEFT)
        para.set_description(_('The style used for text in the body of the calendar, it controls font size, face, style, color, and alignment. The background color is used ONLY for cells containing text, allowing for high-lighting of dates.'))
        default_style.add_paragraph_style("WC-Text",para)
        #
        # WC-Note
        #
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF,size=16,color=((0x0,0x0,0x0)))
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set(bgcolor=((0xff,0xff,0xff)))
        para.set_alignment(BaseDoc.PARA_ALIGN_LEFT)
        para.set_description(_('The style used for notes at the bottom of the calendar, it controls font size, face, style, color and positioning. The background color setting affect all EMPTY calendar cells.'))
        default_style.add_paragraph_style("WC-Note",para)
        #
        # WC-Table
        #
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SERIF,size=24,color=((0x80,0x0,0x0)))
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set(bgcolor=((0xff,0xff,0xff)))
        para.set_alignment(BaseDoc.PARA_ALIGN_RIGHT)
        para.set_description(_('The style used for the table itself. This affects the color of the table lines and the color, font, size, and positioning of the calendar date numbers. It also controls the color of the day names.'))
        default_style.add_paragraph_style("WC-Table",para)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class WebReportDialog(ReportDialog):

    HELP_TOPIC = "rep-web"

    def __init__(self,dbstate,uistate,person):
        self.database = dbstate.db
        self.person = person
        name = "WebCal"
        translated_name = _("Generate Web Calendar")
        self.options = WebReportOptions(name,self.database)
        self.category = CATEGORY_WEB
         
        ReportDialog.__init__(self,dbstate,uistate,person,self.options,
                              name,translated_name)
        # test - ths
    #self.style_name = None

        while True:
            response = self.window.run()
            if response == gtk.RESPONSE_OK:
                self.make_report()
                break
            elif response != gtk.RESPONSE_HELP:
                break
        self.close()

    def parse_html_frame(self):
        pass
    
    def parse_paper_frame(self):
        pass
    
    def setup_html_frame(self):
        pass

    def dummy_toggle(self,obj):
        pass

    def setup_paper_frame(self):
        pass

    def get_title(self):
        """The window title for this dialog"""
        return "%s - GRAMPS" % (_("Generate Web Calendar"))

    def get_target_browser_title(self):
        """The title of the window created when the 'browse' button is
        clicked in the 'Save As' frame."""
        return _("Target Directory")

    def get_target_is_directory(self):
        """This report creates a directory full of files, not a single file."""
        return 1
    
    def get_default_directory(self):
        """Get the name of the directory to which the target dialog
        box should default.  This value can be set in the preferences
        panel."""
        return self.options.handler.options_dict['WCod']    

    def make_document(self):
        """Do Nothing.  This document will be created in the
        make_report routine."""
        pass

    def setup_format_frame(self):
        """Do nothing, since we don't want a format frame """
        pass
    
    def setup_post_process(self):
        """The format frame is not used in this dialog.  Hide it, and
        set the output notebook to always display the html template
        page."""
        pass

    def parse_format_frame(self):
        """The format frame is not used in this dialog."""
        self.options.handler.set_format_name("html")

    def make_report(self):
        """Create the object that will produce the web pages."""

        try:
            MyReport = WebReport(self.database,self.person,
                                 self.options)
            MyReport.write_report()
        except Errors.FilterError, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class Element:
    """ A parsed XML element """
    def __init__(self,name,attributes):
        'Element constructor'
        # The element's tag name
        self.name = name
        # The element's attribute dictionary
        self.attributes = attributes
        # The element's cdata
        self.cdata = ''
        # The element's child element list (sequence)
        self.children = []

    def AddChild(self,element):
        'Add a reference to a child element'
        self.children.append(element)

    def getAttribute(self,key):
        'Get an attribute value'
        return self.attributes.get(key)

    def getData(self):
        'Get the cdata'
        return self.cdata

    def getElements(self,name=''):
        'Get a list of child elements'
        #If no tag name is specified, return the all children
        if not name:
            return self.children
        else:
            # else return only those children with a matching tag name
            elements = []
            for element in self.children:
                if element.name == name:
                    elements.append(element)
            return elements

    def toString(self, level=0):
        retval = " " * level
        retval += "<%s" % self.name
        for attribute in self.attributes:
            retval += " %s=\"%s\"" % (attribute, self.attributes[attribute])
        c = ""
        for child in self.children:
            c += child.toString(level+1)
        if c == "":
            retval += "/>\n"
        else:
            retval += ">\n" + c + ("</%s>\n" % self.name)
        return retval



class Xml2Obj:
    """ XML to Object """
    def __init__(self):
        self.root = None
        self.nodeStack = []

    def StartElement(self,name,attributes):
        'SAX start element even handler'
        # Instantiate an Element object
        element = Element(name.encode(),attributes)
        # Push element onto the stack and make it a child of parent
        if len(self.nodeStack) > 0:
            parent = self.nodeStack[-1]
            parent.AddChild(element)
        else:
            self.root = element
        self.nodeStack.append(element)

    def EndElement(self,name):
        'SAX end element event handler'
        self.nodeStack = self.nodeStack[:-1]

    def CharacterData(self,data):
        'SAX character data event handler'
        if data.strip():
            data = data.encode()
            element = self.nodeStack[-1]
            element.cdata += data
            return

    def Parse(self,filename):
        # Create a SAX parser
        Parser = expat.ParserCreate()
        # SAX event handlers
        Parser.StartElementHandler = self.StartElement
        Parser.EndElementHandler = self.EndElement
        Parser.CharacterDataHandler = self.CharacterData
        # Parse the XML File
        ParserStatus = Parser.Parse(open(filename,'r').read(), 1)
        return self.root

class Holidays:
    """ Class used to read XML holidays to add to calendar. """
    def __init__(self, elements, country="US"):
        self.debug = 0
        self.elements = elements
        self.Country = country
        self.dates = []
        self.initialize()
    def set_country(self, country):
        self.Country = country
        self.dates = []
        self.initialize()
    def initialize(self):
        # parse the date objects
        for country_set in self.elements.children:
            if country_set.name == "country" and country_set.attributes["name"] == self.Country:
                for date in country_set.children:
                    if date.name == "date":
                        data = {"value" : "",
                                "name" : "",
                                "offset": "",
                                "type": "",
                                "if": "",
                                } # defaults
                        for attr in date.attributes:
                            data[attr] = date.attributes[attr]
                        self.dates.append(data)
    def get_daynames(self, y, m, dayname):
        if self.debug: print "%s's in %d %d..." % (dayname, m, y)
        retval = [0]
        dow = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'].index(dayname)
        for d in range(1, 32):
            try:
                date = datetime.date(y, m, d)
            except ValueError:
                continue
            if date.weekday() == dow:
                retval.append( d )
        if self.debug: print "dow=", dow, "days=", retval
        return retval
    def check_date(self, date):
        retval = []
        for rule in self.dates:
            if self.debug: print "Checking ", rule["name"], "..."
            offset = 0
            if rule["offset"] != "":
                if rule["offset"].isdigit():
                    offset = int(rule["offset"])
                elif rule["offset"][0] in ["-","+"] and rule["offset"][1:].isdigit():
                    offset = int(rule["offset"])
                else:
                    # must be a dayname
                    offset = rule["offset"]
            if rule["value"].count("/") == 3: # year/num/day/month, "3rd wednesday in april"
                y, num, dayname, mon = rule["value"].split("/")
                if y == "*":
                    y = date.year
                else:
                    y = int(y)
                if mon.isdigit():
                    m = int(mon)
                elif mon == "*":
                    m = date.month
                else:
                    m = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                         'jul', 'aug', 'sep', 'oct', 'nov', 'dec'].index(mon) + 1
                dates_of_dayname = self.get_daynames(y, m, dayname)
                if self.debug: print "num =", num
                d = dates_of_dayname[int(num)]
            elif rule["value"].count("/") == 2: # year/month/day
                y, m, d = rule["value"].split("/")
                if y == "*":
                    y = date.year
                else:
                    y = int(y)
                if m == "*":
                    m = date.month
                else:
                    m = int(m)
                if d == "*":
                    d = date.day
                else:
                    d = int(d)
            ndate = datetime.date(y, m, d)
            if self.debug: print ndate, offset, type(offset)
            if type(offset) == int:
                if offset != 0:
                    ndate = ndate.fromordinal(ndate.toordinal() + offset)
            elif type(offset) in [type(u''), str]:
                dir = 1
                if offset[0] == "-":
                    dir = -1
                    offset = offset[1:]
                if offset in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
                    # next tuesday you come to, including this one
                    dow = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'].index(offset)
                    ord = ndate.toordinal()
                    while ndate.fromordinal(ord).weekday() != dow:
                        ord += dir
                    ndate = ndate.fromordinal(ord)
            if self.debug: print "ndate:", ndate, "date:", date
            if ndate == date:
                if rule["if"] != "":
                    if not eval(rule["if"]):
                        continue
                retval.append(rule["name"])
        return retval

def get_countries():
    """ Looks in multiple places for holidays.xml files """
    locations = [const.pluginsDir,
                 os.path.join(const.home_dir,"plugins")]
    holiday_file = 'holidays.xml'
    country_list = []
    for dir in locations:
        holiday_full_path = os.path.join(dir, holiday_file)
        if os.path.exists(holiday_full_path):
            cs = process_holiday_file(holiday_full_path)
            for c in cs:
                if c not in country_list:
                    country_list.append(c)
    country_list.sort()
    country_list.insert(0, _("Don't include holidays"))
    return country_list

def process_holiday_file(filename):
    """ This will process a holiday file for country names """
    parser = Xml2Obj()
    element = parser.Parse(filename)
    country_list = []
    for country_set in element.children:
        if country_set.name == "country":
            if country_set.attributes["name"] not in country_list:
                country_list.append(country_set.attributes["name"])
    return country_list

## Currently reads the XML file on load. Could move this someplace else
## so it only loads when needed.

_countries = get_countries()

#------------------------------------------------------------------------
#
# Empty class to keep the BaseDoc-targeted format happy
#
#------------------------------------------------------------------------
class EmptyDoc:
    def __init__(self,styles,type,template,orientation,source=None):
        pass

    def init(self):
        pass

#-------------------------------------------------------------------------
#
# GrampsNoteComboBox
#
#-------------------------------------------------------------------------
class GrampsNoteComboBox(gtk.ComboBox):
    """
    Derived from the ComboBox, this widget provides handling of Report
    Styles.
    """

    def __init__(self,model=None,node=None):
        """
        Initializes the combobox, building the display column.
        """
        gtk.ComboBox.__init__(self,model)
        cell = gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)
        if node:
            self.set_active_iter(node)
        else:
            self.set_active(0)
        self.local_store = model

    def get_handle(self):
        """
        Returns the selected key (style sheet name).

        @returns: Returns the name of the selected style sheet
        @rtype: str
        """
        active = self.get_active_iter()
        handle = u""
        if active:
            handle = self.local_store.get_value(active,1)
        return handle

def mk_combobox(media_list,select_value):
    store = gtk.ListStore(str,str)
    node = None
    
    for data in media_list:
        if data[1] == select_value:
            node = store.append(row=data)
        else:
            store.append(row=data)
    widget = GrampsNoteComboBox(store,node)
    if len(media_list) == 0:
        widget.set_sensitive(False)
    return widget
    
#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
register_report(
    name = 'WebCal',
    category = CATEGORY_WEB,
    report_class = WebReportDialog,
    options_class = WebReportOptions,
    modes = MODE_GUI,
    translated_name = _("Web Calendar"),
    status = _("Beta"),
    author_name="Thom Sturgill",
    author_email="thsturgill@yahoo.com",
    description=_("Generates web (HTML) calendars."),
    )
