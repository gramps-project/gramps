#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007      Thom Sturgill
# Copyright (C) 2007-2008 Brian G. Matherly
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

Reports/Web Page/Web Calendar
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
import time
import datetime
#import const
import codecs
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
# GRAMPS module
#
#------------------------------------------------------------------------
import gen.lib
import const
import BaseDoc
from GrampsCfg import get_researcher
from PluginUtils import register_report
from ReportBase import (Report, ReportUtils, MenuReportOptions, CATEGORY_WEB, 
                        MODE_GUI)
from PluginUtils import FilterOption, EnumeratedListOption, PersonOption, \
    BooleanOption, NumberOption, StringOption, DestinationOption, StyleOption
import Utils
import GrampsLocale
from QuestionDialog import ErrorDialog
from Utils import probably_alive

#------------------------------------------------------------------------
#
# constants
#
#------------------------------------------------------------------------
_CALENDAR = "calendar.css"

_CHARACTER_SETS = [
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

_CC = [
    '<a rel="license" href="http://creativecommons.org/licenses/by/2.5/">'
    '<img alt="Creative Commons License - By attribution" title="Creative '
    'Commons License - By attribution" src="somerights20.gif" /></a>',
    
    '<a rel="license" href="http://creativecommons.org/licenses/by-nd/2.5/">'
    '<img alt="Creative Commons License - By attribution, No derivations" '
    'title="Creative Commons License - By attribution, No derivations" '
    'src="somerights20.gif" /></a>',
    
    '<a rel="license" href="http://creativecommons.org/licenses/by-sa/2.5/">'
    '<img alt="Creative Commons License - By attribution, Share-alike" '
    'title="Creative Commons License - By attribution, Share-alike" '
    'src="somerights20.gif" /></a>',
    
    '<a rel="license" href="http://creativecommons.org/licenses/by-nc/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commercial" '
    'title="Creative Commons License - By attribution, Non-commercial" '
    'src="somerights20.gif" /></a>',
    
    '<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commercial, No '
    'derivations" title="Creative Commons License - By attribution, '
    'Non-commercial, No derivations" src="somerights20.gif" /></a>',
    
    '<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/2.5/">'
    '<img alt="Creative Commons License - By attribution, Non-commerical, '
    'Share-alike" title="Creative Commons License - By attribution, '
    'Non-commerical, Share-alike" src="somerights20.gif" /></a>'
    ]

_COPY_OPTIONS = [
        _('Standard copyright'),
        _('Creative Commons - By attribution'),
        _('Creative Commons - By attribution, No derivations'),
        _('Creative Commons - By attribution, Share-alike'),
        _('Creative Commons - By attribution, Non-commercial'),
        _('Creative Commons - By attribution, Non-commercial, No derivations'),
        _('Creative Commons - By attribution, Non-commercial, Share-alike'),
        _('No copyright notice'),
        ]

def make_date(year, month, day):
    """
    Return a Date object of the particular year/month/day.
    """
    retval = gen.lib.Date()
    retval.set_yr_mon_day(year, month, day)
    return retval

#------------------------------------------------------------------------
#
# WebCalReport
#
#------------------------------------------------------------------------
class WebCalReport(Report):
    """
    Create WebCalReport object that produces the report.
    """
    def __init__(self, database, options):
        Report.__init__(self, database, options)
        menu = options.menu
        
        self.database = database
        self.options = options
        
        self.html_dir = menu.get_option_by_name('target').get_value()
        filter_option =  menu.get_option_by_name('filter')
        self.filter = filter_option.get_filter()
        self.ext = menu.get_option_by_name('ext').get_value()
        self.copy = menu.get_option_by_name('cright').get_value()
        self.encoding = menu.get_option_by_name('encoding').get_value()
        self.Country = menu.get_option_by_name('country').get_value()
        self.Year = menu.get_option_by_name('year').get_value()
        self.Surname = menu.get_option_by_name('surname').get_value()
        self.Alive = menu.get_option_by_name('alive').get_value()
        self.Birthday = menu.get_option_by_name('birthdays').get_value()
        self.Anniv = menu.get_option_by_name('anniversaries').get_value()
        self.Title_text  = menu.get_option_by_name('title').get_value()
        self.Month_image = menu.get_option_by_name('background').get_value()
        self.Month_repeat = menu.get_option_by_name('repeat').get_value()
        self.Serif_fonts = menu.get_option_by_name('serif_fonts').get_value()
        self.SanSerif_fonts = \
                        menu.get_option_by_name('sanserif_fonts').get_value()
        self.Home_link = menu.get_option_by_name('home_link').get_value()
        
        self.Note  = [ menu.get_option_by_name('note_jan').get_value(), 
                       menu.get_option_by_name('note_feb').get_value(),
                       menu.get_option_by_name('note_mar').get_value(),
                       menu.get_option_by_name('note_apr').get_value(),
                       menu.get_option_by_name('note_may').get_value(),
                       menu.get_option_by_name('note_jun').get_value(),
                       menu.get_option_by_name('note_jul').get_value(),
                       menu.get_option_by_name('note_aug').get_value(),
                       menu.get_option_by_name('note_sep').get_value(),
                       menu.get_option_by_name('note_oct').get_value(),
                       menu.get_option_by_name('note_nov').get_value(),
                       menu.get_option_by_name('note_dec').get_value()]
        
        self.__style = menu.get_option_by_name("style").get_style()

    def get_short_name(self, person, maiden_name = None):
        """ Return person's name, unless maiden_name given, unless married_name listed. """
        # Get all of a person's names:
        primary_name = person.get_primary_name()
        married_name = None
        names = [primary_name] + person.get_alternate_names()
        for n in names:
            if int(n.get_type()) == gen.lib.NameType.MARRIED:
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
        locations = [const.PLUGINS_DIR, const.USER_PLUGINS]
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
        style = self.__style.get_paragraph_style("WC-Title")
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
        style = self.__style.get_paragraph_style("WC-Table")
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
        style = self.__style.get_paragraph_style("WC-Month")
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
        style = self.__style.get_paragraph_style("WC-Text")
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
        style = self.__style.get_paragraph_style("WC-Note")
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


    def write_footer(self, of):
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
            text = _CC[self.copy-1]
            from_path = os.path.join(const.IMAGE_DIR,"somerights20.gif")
            shutil.copyfile(from_path, os.path.join(self.html_dir,"somerights20.gif"))
        else:
            text = "&copy; %s %s" % (time.localtime()[0], author) 
        of.write(text)
        of.write('</div>\n')
        of.write('  </body>\n')
        of.write('</html>\n')

    def write_header(self, of):
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

    def create_file(self, name):
        page_name = os.path.join(self.html_dir, name)
        of = codecs.EncodedFile(open(page_name, "w"),'utf-8',self.encoding,'xmlcharrefreplace')
        return of

    def close_file(self, of):
        of.close()

    def write_report(self):
        """ The short method that runs through each month and creates a page. """
        if not os.path.isdir(self.html_dir):
            parent_dir = os.path.dirname(self.html_dir)
            if not os.path.isdir(parent_dir):
                ErrorDialog(_("Neither %s nor %s are directories") % \
                            (self.html_dir,parent_dir))
                return
            else:
                try:
                    os.mkdir(self.html_dir)
                except IOError, value:
                    ErrorDialog(_("Could not create the directory: %s") % \
                                self.html_dir + "\n" + value[1])
                    return
                except:
                    ErrorDialog(_("Could not create the directory: %s") % \
                                self.html_dir)
                    return
        
        # initialize the dict to fill:
        self.calendar = {}
        self.progress = Utils.ProgressMeter(_("Generate HTML Calendars"),'')

        # Generate the CSS file
        self.write_css()

        # get the information, first from holidays:
        if self.Country != 0: # Don't include holidays
            self.get_holidays(self.Year, _COUNTRIES[self.Country]) # _country is currently global
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
                        if last:
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
            living = probably_alive(person, self.database, make_date(self.Year, 1, 1), 0)
            if self.Birthday and birth_date != None and ((self.Alive and living) or not self.Alive):
                year = birth_date.get_year()
                month = birth_date.get_month()
                day = birth_date.get_day()
                age = self.Year - year
                # add some things to handle maiden name:
                father_lastname = None # husband, actually
                if self.Surname == 0: # get husband's last name:
                    if person.get_gender() == gen.lib.Person.FEMALE:
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
                                if not probably_alive(spouse, self.database, make_date(self.Year, 1, 1), 0):
                                    continue
                            married = True
                            for event_ref in fam.get_event_ref_list():
                                event = self.database.get_event_from_handle(event_ref.ref)
                                if event and int(event.get_type()) in [gen.lib.EventType.DIVORCE,
                                                                       gen.lib.EventType.ANNULMENT,
                                                                       gen.lib.EventType.DIV_FILING]:
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
# WebCalOptions
#
#------------------------------------------------------------------------
class WebCalOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
    """
    
    def __init__(self, name, dbase):
        self.__db = dbase
        self.__pid = None
        self.__filter = None
        MenuReportOptions.__init__(self, name, dbase)

    def add_menu_options(self, menu):
        """
        Add options to the menu for the web calendar.
        """
        self.__add_report_options(menu)
        self.__add_content_options(menu)
        self.__add_misc_options(menu)
        self.__add_notes_options(menu)
    
    def __add_report_options(self, menu):
        """
        Options on the "Report Options" tab.
        """
        category_name = _("Report Options")
        
        target = DestinationOption( _("Destination"), 
                                    os.path.join(const.USER_HOME,"WEBCAL"))
        target.set_help( _("The destination directory for the web files"))
        target.set_directory_entry(True)
        menu.add_option(category_name, "target", target)
        
        ext = EnumeratedListOption(_("File extension"), ".html" )
        for etype in ['.html', '.htm', '.shtml', '.php', '.php3', '.cgi']:
            ext.add_item(etype, etype)
        ext.set_help( _("The extension to be used for the web files"))
        menu.add_option(category_name, "ext", ext)
        
        cright = EnumeratedListOption(_('Copyright'), 0 )
        index = 0
        for copt in _COPY_OPTIONS:
            cright.add_item(index, copt)
            index += 1
        cright.set_help( _("The copyright to be used for the web files"))
        menu.add_option(category_name, "cright", cright)
        
        encoding = EnumeratedListOption(_('Character set encoding'), 'utf-8' )
        for eopt in _CHARACTER_SETS:
            encoding.add_item(eopt[1], eopt[0])
        encoding.set_help( _("The encoding to be used for the web files"))
        menu.add_option(category_name, "encoding", encoding)
        
        default_style = BaseDoc.StyleSheet()
        self.__make_default_style(default_style)
        style = StyleOption("Style", default_style, "WebCal")
        style.set_help( _("The style to be used for the web files"))
        menu.add_option(category_name, "style", style)
        
    def __add_content_options(self, menu):
        """
        Options on the "Content Options" tab.
        """
        category_name = _("Content Options")
        
        year = NumberOption(_("Year of calendar"), time.localtime()[0], 
                            1000, 3000)
        year.set_help(_("Year of calendar"))
        menu.add_option(category_name, "year", year)

        self.__filter = FilterOption(_("Filter"), 0)
        self.__filter.set_help(
               _("Select filter to restrict people that appear on calendar"))
        menu.add_option(category_name, "filter", self.__filter)
        self.__filter.connect('value-changed', self.__filter_changed)
        
        self.__pid = PersonOption(_("Filter Person"))
        self.__pid.set_help(_("The center person for the filter"))
        menu.add_option(category_name, "pid", self.__pid)
        self.__pid.connect('value-changed', self.__update_filters)
        
        self.__update_filters()

        country = EnumeratedListOption(_('Country for holidays'), 0 )
        index = 0
        for item in _COUNTRIES:
            country.add_item(index, item)
            index += 1
        country.set_help( _("Holidays will be included for the selected "
                            "country"))
        menu.add_option(category_name, "country", country)

        alive = BooleanOption(_("Include only living people"), True)
        alive.set_help(_("Include only living people in the calendar"))
        menu.add_option(category_name, "alive", alive)

        birthdays = BooleanOption(_("Include birthdays"), True)
        birthdays.set_help(_("Include birthdays in the calendar"))
        menu.add_option(category_name, "birthdays", birthdays)

        anniversaries = BooleanOption(_("Include anniversaries"), True)
        anniversaries.set_help(_("Include anniversaries in the calendar"))
        menu.add_option(category_name, "anniversaries", anniversaries)
        
        surname = BooleanOption(_('Check for wives to use maiden name'), True)
        surname.set_help(_("Attempt to use maiden names of women"))
        menu.add_option(category_name, "surname", surname)

    def __add_misc_options(self, menu):
        """
        Options on the "Misc Options" tab.
        """
        category_name = _("Misc Options")
        
        title = StringOption(_('Calendar Title'), _('My Family Calendar')) 
        title.set_help(_("The title of the calendar"))
        menu.add_option(category_name, "title", title)
        
        home_link = StringOption(_('Home link'), '../index.html') 
        home_link.set_help(_("The link to be included to direct the user to "
                         "the main page of the web site"))
        menu.add_option(category_name, "home_link", home_link)
        
        serif_fonts = StringOption(_('Serif font family'), 
                             '"Georgia","Times New Roman","Times",serif') 
        serif_fonts.set_help(_("Serif font family"))
        menu.add_option(category_name, "serif_fonts", serif_fonts)
    
        sanserif_fonts = StringOption(_('San-Serif font family'), 
                             '"Verdana","Helvetica","Arial",sans-serif') 
        sanserif_fonts.set_help(_('San-Serif font family'))
        menu.add_option(category_name, "sanserif_fonts", sanserif_fonts)
        
        background = StringOption(_('Background Image'), "") 
        background.set_help(_('The image to be used as the page background'))
        menu.add_option(category_name, "background", background)

        repeat = EnumeratedListOption(_('Image Repeat'), 1 )
        repeat.add_item(0, _('no-repeat'))
        repeat.add_item(1, _('repeat'))
        repeat.add_item(2, _('repeat-x'))
        repeat.add_item(3, _('repeat-y'))
        repeat.set_help( _("Whether to repeat the background image"))
        menu.add_option(category_name, "repeat", repeat)
        
    def __add_notes_options(self, menu):
        """
        Options on the "Months Notes" tabs.
        """
        category_name = _("Months 1-6 Notes")

        note_jan = StringOption(_('Jan Note'), _('This prints in January')) 
        note_jan.set_help(_("The note for the month of January"))
        menu.add_option(category_name, "note_jan", note_jan)
        
        note_feb = StringOption(_('Feb Note'), _('This prints in February')) 
        note_feb.set_help(_("The note for the month of February"))
        menu.add_option(category_name, "note_feb", note_feb)
        
        note_mar = StringOption(_('Mar Note'), _('This prints in March')) 
        note_mar.set_help(_("The note for the month of March"))
        menu.add_option(category_name, "note_mar", note_mar)
        
        note_apr = StringOption(_('Apr Note'), _('This prints in April')) 
        note_apr.set_help(_("The note for the month of April"))
        menu.add_option(category_name, "note_apr", note_apr)
        
        note_may = StringOption(_('May Note'), _('This prints in May')) 
        note_may.set_help(_("The note for the month of May"))
        menu.add_option(category_name, "note_may", note_may)
        
        note_jun = StringOption(_('Jun Note'), _('This prints in June')) 
        note_jun.set_help(_("The note for the month of June"))
        menu.add_option(category_name, "note_jun", note_jun)
        
        category_name = _("Months 7-12 Notes")

        note_jul = StringOption(_('Jul Note'), _('This prints in July')) 
        note_jul.set_help(_("The note for the month of July"))
        menu.add_option(category_name, "note_jul", note_jul)
        
        note_aug = StringOption(_('Aug Note'), _('This prints in August')) 
        note_aug.set_help(_("The note for the month of August"))
        menu.add_option(category_name, "note_aug", note_aug)
        
        note_sep = StringOption(_('Sep Note'), _('This prints in September')) 
        note_sep.set_help(_("The note for the month of September"))
        menu.add_option(category_name, "note_sep", note_sep)
        
        note_oct = StringOption(_('Oct Note'), _('This prints in October')) 
        note_oct.set_help(_("The note for the month of October"))
        menu.add_option(category_name, "note_oct", note_oct)
        
        note_nov = StringOption(_('Nov Note'), _('This prints in November')) 
        note_nov.set_help(_("The note for the month of November"))
        menu.add_option(category_name, "note_nov", note_nov)
        
        note_dec = StringOption(_('Dec Note'), _('This prints in December')) 
        note_dec.set_help(_("The note for the month of December"))
        menu.add_option(category_name, "note_dec", note_dec)

    def __update_filters(self):
        """
        Update the filter list based on the selected person
        """
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        filter_list = ReportUtils.get_person_filters(person, False)
        self.__filter.set_filters(filter_list)
        
    def __filter_changed(self):
        """
        Handle filter change. If the filter is not specific to a person,
        disable the person option
        """
        filter_value = self.__filter.get_value()
        if filter_value in [1, 2, 3, 4]:
            # Filters 1, 2, 3 and 4 rely on the center person
            self.__pid.set_available(True)
        else:
            # The rest don't
            self.__pid.set_available(False)

    def __make_default_style(self, default_style):
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
        font.set(face=BaseDoc.FONT_SERIF, size=24, bold=1, 
                 italic=1, color=(0x80, 0x0, 0x0))
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set(bgcolor=((0xb0, 0xc4, 0xde)))
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set_description(_('The style used for the title ("My Family '
                               'Calendar") of the page. The background color '
                               'sets the PAGE background. Borders DO NOT '
                               'work.'))
        default_style.add_paragraph_style("WC-Title", para)
        #
        # WC-Month
        #
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SERIF, size=48, bold=1, 
                 italic=1, color=((0x80, 0x0, 0x0)))
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set(bgcolor=((0xf0, 0xe6, 0x8c)))
        para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        para.set_description(_('The style used for the month name and year, it'
                               ' controls the font face, size, style, color '
                               'and the background color of the block, '
                               'including the day-name area. Inclusion of a '
                               'graphic does not cover the day-name area.'))
        default_style.add_paragraph_style("WC-Month", para)
        #
        # WC-Text
        #
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SERIF, size=16, 
                 italic=1, color=((0x80, 0x0, 0x0)))
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set(bgcolor=((0xf0, 0xf8, 0xff)))
        para.set_alignment(BaseDoc.PARA_ALIGN_LEFT)
        para.set_description(_('The style used for text in the body of the '
                               'calendar, it controls font size, face, style, '
                               'color, and alignment. The background color is '
                               'used ONLY for cells containing text, allowing '
                               'for high-lighting of dates.'))
        default_style.add_paragraph_style("WC-Text", para)
        #
        # WC-Note
        #
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SANS_SERIF, size=16, color=((0x0, 0x0, 0x0)))
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set(bgcolor=((0xff, 0xff, 0xff)))
        para.set_alignment(BaseDoc.PARA_ALIGN_LEFT)
        para.set_description(_('The style used for notes at the bottom of the '
                               'calendar, it controls font size, face, style, '
                               'color and positioning. The background color '
                               'setting affect all EMPTY calendar cells.'))
        default_style.add_paragraph_style("WC-Note", para)
        #
        # WC-Table
        #
        font = BaseDoc.FontStyle()
        font.set(face=BaseDoc.FONT_SERIF, size=24, color=((0x80, 0x0, 0x0)))
        para = BaseDoc.ParagraphStyle()
        para.set_font(font)
        para.set(bgcolor=((0xff, 0xff, 0xff)))
        para.set_alignment(BaseDoc.PARA_ALIGN_RIGHT)
        para.set_description(_('The style used for the table itself. This '
                               'affects the color of the table lines and the '
                               'color, font, size, and positioning of the '
                               'calendar date numbers. It also controls the '
                               'color of the day names.'))
        default_style.add_paragraph_style("WC-Table", para)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class Element:
    """ A parsed XML element """
    def __init__(self, name,attributes):
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

    def getElements(self, name=''):
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

    def StartElement(self, name,attributes):
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

    def EndElement(self, name):
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

def _get_countries():
    """ Looks in multiple places for holidays.xml files """
    locations = [const.PLUGINS_DIR, const.USER_PLUGINS]
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

# TODO: Only load this once the first time it is actually needed so Gramps 
# doesn't take so long to start up.
_COUNTRIES = _get_countries()

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
register_report(
    name = 'WebCal',
    category = CATEGORY_WEB,
    report_class = WebCalReport,
    options_class = WebCalOptions,
    modes = MODE_GUI,
    translated_name = _("Web Calendar"),
    status = _("Stable"),
    author_name = "Thom Sturgill",
    author_email = "thsturgill@yahoo.com",
    description = _("Produces web (HTML) calendars."),
    )
