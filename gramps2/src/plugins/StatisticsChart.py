#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2004  Donald N. Allingham
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
# Statistics plugin (w) 2004-2005 by Eero Tamminen.
# Partially based on code from the Timeline graph plugin.
#
# $Id$

"""
Statistics Chart report
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
import time
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GNOME/gtk
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from Utils import pt2cm
import const	# gender and report type names
import RelLib	# need Person internals for getting gender / gender name
import Utils
import Report
import BaseDoc
import GenericFilter
import ReportOptions
import Date

#------------------------------------------------------------------------
#
# Module globals
#
#------------------------------------------------------------------------

# sort type identifiers
_SORT_VALUE = 0
_SORT_KEY = 1

# needs to be global for the lookup_value_compare()
_lookup_items = {}

# needs to be global for python sort
def lookup_value_compare(a, b):
    "compare given keys according to corresponding _lookup_items values"
    if _lookup_items[a] < _lookup_items[b]:
	return -1
    if _lookup_items[a] == _lookup_items[b]:
	return 0
    return 1

#------------------------------------------------------------------------
#
# Data extraction methods from the database
#
#------------------------------------------------------------------------

class Extract:

    def __init__(self):
        """Methods for extracting statistical data from the database"""
	self.extractors = [
	    (_("Titles"), self.title),
	    (_("Forenames"), self.forename),
	    (_("Birth years"), self.birth_year),
	    (_("Death years"), self.death_year),
	    (_("Birth months"), self.birth_month),
	    (_("Death months"), self.death_month),
	    (_("Estimated ages at death"), self.death_age),
	    #(_("TODO: Estimated (first) marriage ages"), self.marriage_age),
	    #(_("TODO: Estimated ages for bearing the first child"), self.first_child_age),
	    #(_("TODO: Estimated Ages for bearing the last child"), self.last_child_age),
	    #(_("TODO: Number of children"), self.child_count),
	    #(_("TODO: Cause of death"), self.death_cause),
	    (_("Genders"), self.gender)
	]

    def estimate_age(self, person, date):
	"""Utility method to estimate person's age at given date:
	person -- person whose age is to be estimated
	date -- date at which the age should be estimated
	This expects that Person's birth and the date argument are
	using the same calendar and that between those two dates
	there haven't been any calendar discontinuations."""
	birth = person.getBirth().getDateObj()
	if not (date.getYearValid() and birth.getYearValid()):
	    return _("Missing date(s)")
	age = date.getYear() - birth.getYear()
	if date.getMonthValid() and birth.getMonthValid():
	    if date.getMonth() < birth.getMonth():
		age -= 1
	    else:
		if (date.getMonth() == birth.getMonth() and
		date.getDayValid() and birth.getDayValid() and
		date.getDay() < birth.getDay()):
		    age -= 1
	if age >= 0:
	    return str(age)
	else:
	    return _("Invalid date(s)")

    def title(self, person):
	title = person.getPrimaryName().getTitle()
	if title:
	    return [title]
	else:
	    return [_("Person's missing (preferred) title")]
	
    def forename(self, person):
	# because this returns list, other methods return list too
	firstnames = person.getPrimaryName().getFirstName().strip()
	if firstnames:
	    return [name.capitalize() for name in firstnames.split()]
	else:
	    return [_("Person's missing (preferred) forename")]

    def birth_year(self, person):
	year = person.getBirth().getDateObj().getYear()
	if year != Date.UNDEF:
	    return [str(year)]
	else:
	    return [_("Person's missing birth year")]

    def death_year(self, person):
	year = person.getDeath().getDateObj().getYear()
	if year != Date.UNDEF:
	    return [str(year)]
	else:
	    return [_("Person's missing death year")]
        
    def birth_month(self, person):
	month = person.getBirth().getDateObj().start
	if month.getMonthValid():
	    return [month.getMonthStr()]
	else:
	    return [_("Person's missing birth month")]

    def death_month(self, person):
	month = person.getDeath().getDateObj().start
	if month.getMonthValid():
	    return [month.getMonthStr()]
	else:
	    return [_("Person's missing death month")]

    def death_age(self, person):
	return [self.estimate_age(person, person.getDeath().getDateObj())]

    def marriage_age(self, person):
	return "Marriage age stat unimplemented"

    def first_child_age(self, person):
	return "First child bearing age stat unimplemented"

    def last_child_age(self, person):
	return "Last child bearing age stat unimplemented"

    def child_count(self, person):
	return "Child count stat unimplemented"

    def death_cause(self, person):
	return "Death cause stat unimplemented"
	
    def gender(self, person):
	# TODO: why there's no Person.getGenderName?
	# It could be used by getDisplayInfo & this...
	Person = RelLib.Person
	if person.gender == Person.male:
	    gender = const.male
	elif person.gender == Person.female:
	    gender = const.female
	else:
	    gender = const.unknown
	return [gender]
    
    def collect_data(self, db, filter_func, extract_func, genders,
                     year_from, year_to, no_years):
        """goes through the database and collects the selected personal
	data persons fitting the filter and birth year criteria. The
	arguments are:
	db           - the GRAMPS database
        filter_func  - filtering function selected by the StatisticsDialog
	extract_func - extraction method selected by the StatisticsDialog
	genders      - which gender(s) to include into statistics
	year_from    - use only persons who've born this year of after
	year_to      - use only persons who've born this year or before
	no_years     - use also people without any birth year
	"""
	Person = RelLib.Person
	items = {}
	# go through the people and collect data
	for person in filter_func.apply(db, db.getPersonMap().values()):

	    # check whether person has suitable gender
	    if person.gender != genders and genders != Person.unknown:
		continue
	    
	    # check whether birth year is within required range
	    birth = person.getBirth().getDateObj()
	    if birth.getYearValid():
		year = birth.getYear()
		if not (year >= year_from and year <= year_to):
		    continue
	    else:
		# if death before range, person's out of range too...
		death = person.getDeath().getDateObj()
		if death.getYearValid() and death.getYear() < year_from:
		    continue
		if not no_years:
		    # do not accept people who are not known to be in range
		    continue

	    # get the information
	    value = extract_func(person)
	    # list of information found
	    for key in value:
		if key in items.keys():
		    items[key] += 1
		else:
		    items[key] = 1
	return items

# GLOBAL: ready instance for others to use
_Extract = Extract()

#------------------------------------------------------------------------
#
# Statistics report
#
#------------------------------------------------------------------------
class StatisticsChart(Report.Report):

    def __init__(self, database, person, options_class):
        """
        Creates the Statistics object that produces the report.
	Uses the Extractor class to extract the data from the database.

        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

	To see what the options are, check the options help in the options class.
        """
        Report.Report.__init__(self,database,person,options_class)
	
        filter_num = options_class.get_filter_number()
        filters = options_class.get_report_filters(person)
        filters.extend(GenericFilter.CustomFilters.get_filters())
        filterfun = filters[filter_num]

	year_from = options_dict['year_from']
	year_to = options_dict['year_to']
	gender = options_dict['gender']

	extract = _Extract.extractors[options_dict['extract']]
	# extract requested items from the database and count them
	self.items = extractor.collect_data(self.db, filterfun, extract[1], gender,
		year_from, year_to, options_dict['no_years'])
	# generate sorted item lookup index index
	self.index_items(options_dict['sort'], options_dict['reverse'])

	# title needs both data extraction method name + gender name
	Person = RelLib.Person
	if gender == Person.male:
	    genderstr = _("men")
	elif gender == Person.female:
	    genderstr = _("women")
	else:
	    genderstr = None

	if genderstr:
	    self.title = "%s (%s): %04d-%04d" % (extract[0], genderstr, year_from, year_to)
	else:
	    self.title = "%s: %04d-%04d" % (extract[0], year_from, year_to)

	self.setup()

	    
    def index_items(self, sort, reverse):
	"""creates & stores a sorted index for the items"""
	global _lookup_items

	# sort by item keys
	index = self.items.keys()
	index.sort()
	if reverse:
	    index.reverse()

	if sort == _SORT_VALUE:
	    # set for the sorting function
	    _lookup_items = self.items
	    
	    # then sort by value
	    index.sort(lookup_value_compare)
	    if reverse:
		index.reverse()

	self.index = index

	
    def setup(self):
        """
        Define the graphics styles used by the report. Paragraph definitions
        have already been defined in the document. The styles used are:

        SC-bar - A red bar with 0.5pt black line.
        SC-text  - Contains the SC-Name paragraph style used for
                the individual's name
        SC-title - Contains the SC-Title paragraph style used for
                the title of the document
        """
	g = BaseDoc.GraphicsStyle()
        g.set_line_width(0.8)
        g.set_color((0,0,0))
        g.set_fill_color((255,0,0))
        self.doc.add_draw_style("SC-bar",g)

        g = BaseDoc.GraphicsStyle()
        g.set_paragraph_style("SC-Text")
        g.set_color((0,0,0))
        g.set_fill_color((255,255,255))
        g.set_line_width(0)
        self.doc.add_draw_style("SC-text",g)

        g = BaseDoc.GraphicsStyle()
        g.set_paragraph_style("SC-Title")
        g.set_color((0,0,0))
        g.set_fill_color((255,255,255))
        g.set_line_width(0)
        g.set_width(self.doc.get_usable_width())
        self.doc.add_draw_style("SC-title",g)

	
    def write_report(self):
	"output the selected statistics..."

        font = self.doc.style_list['SC-Text'].get_font()

	# set layout variables
	width = self.doc.get_usable_width()
        row_h = pt2cm(font.get_size())
	max_y = self.doc.get_usable_height() - row_h
        pad =  row_h * 0.5
        
	# calculate maximum key string size
        max_size = 0
	max_value = 0
        for key in self.index:
            max_size = max(self.doc.string_width(font, key), max_size)
	    max_value = max(self.items[key], max_value)
	# horizontal area for the gfx bars
        start = pt2cm(max_size) + 1.0
        size = width - 1.5 - start

	# start page
        self.doc.start_page()

	# start output
	self.doc.center_text('SC-title', self.title, width/2, 0)
	#print self.title

	yoffset = pt2cm(self.doc.style_list['SC-Title'].get_font().get_size())
	for key in self.index:
	    yoffset += (row_h + pad)
	    if yoffset > max_y:
		# for graphical report, page_break() doesn't seem to work
		self.doc.end_page()
		self.doc.start_page()
		yoffset = 0

	    # right align the text to the value
	    x = start - pt2cm(self.doc.string_width(font, key)) - 1.0
            self.doc.draw_text('SC-text', key, x, yoffset)
	    #print key + ":",
	    
	    value = self.items[key]
	    stop = start + (size * value / max_value)
	    path = ((start, yoffset),
		    (stop, yoffset),
		    (stop, yoffset + row_h),
		    (start, yoffset + row_h))
	    self.doc.draw_path('SC-bar', path)
            self.doc.draw_text('SC-text', str(value), stop + 0.5, yoffset)
	    #print "%d/%d" % (value, max_value)
            
        self.doc.end_page()    

	return


#------------------------------------------------------------------------
#
# Statistics report options
#
#------------------------------------------------------------------------
class StatisticsChartOptions(ReportOptions.ReportOptions):
    """
    Defines options and provides their handling interface.
    """
    _sorts = [
    	(_SORT_VALUE, _("Item count")),
	(_SORT_KEY, _("Item name"))
    ]
    _genders = [
    	(RelLib.Person.unknown, _("Both")),
	(RelLib.Person.male, _("Men")),
	(RelLib.Person.female, _("Women"))
    ]

    def __init__(self,name, person_id=None):
        ReportOptions.ReportOptions.__init__(self, name, person_id)

    def set_new_options(self):
	# Options specific for this report
        self.options_dict = {
            'year_to'   : time.localtime()[0],
            'year_from' : 1700,
	    'no_years'  : 0,
	    'extract'   : 0,
	    'gender'    : 0,
	    'sort'      : _SORT_VALUE,
	    'reverse'   : 0
        }
        self.options_help = {
            'year_to'   : ("=num", _("Birth year until which to include people"),
	    			   _("smaller than %d") % self.options_dict['year_to']),
            'year_from' : ("=num", _("Birth year from which to include people"),
	    			   _("earlier than 'year_to' value")),
	    'no_years'  : ("=num", _("Include people without birth years"), [_("No"), _("Yes")]),
	    'gender'    : ("=num", _('Genders included'), self._genders),
	    'extract'   : ("=num", _('Data to show'), [item[0] for item in _Extract.extractors]),
	    'sort'      : ("=num", _('Sorted by'), self._sorts),
	    'reverse'   : ("=num", _("Sort in reverse order"), [_("Yes"), _("No")])
        }

    def enable_options(self):
        # Semi-common options that should be enabled for this report
        self.enable_dict = {
            'filter'    : 0,
        }
	
    def make_default_style(self, default_style):
	"""Make the default output style for the Statistics report."""
	f = BaseDoc.FontStyle()
	f.set_size(10)
	f.set_type_face(BaseDoc.FONT_SERIF)
	p = BaseDoc.ParagraphStyle()
	p.set_font(f)
	p.set_alignment(BaseDoc.PARA_ALIGN_RIGHT)
	p.set_description(_("The style used for the items and values."))
	default_style.add_style("SC-Text",p)
	
	f = BaseDoc.FontStyle()
	f.set_size(14)
	f.set_type_face(BaseDoc.FONT_SANS_SERIF)
	p = BaseDoc.ParagraphStyle()
	p.set_font(f)
	p.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
	p.set_description(_("The style used for the title of the page."))
	default_style.add_style("SC-Title",p)

    def get_report_filters(self, person):
	"""Set up the list of possible content filters."""
	
	name = person.getPrimaryName().getName()
	
	all = GenericFilter.GenericFilter()
	all.set_name(_("Entire Database"))
	all.add_rule(GenericFilter.Everyone([]))
	
	des = GenericFilter.GenericFilter()
	des.set_name(_("Descendants of %s") % name)
	des.add_rule(GenericFilter.IsDescendantOf([person.getId(), 1]))
	
	ans = GenericFilter.GenericFilter()
	ans.set_name(_("Ancestors of %s") % name)
	ans.add_rule(GenericFilter.IsAncestorOf([person.getId(), 1]))
	
	com = GenericFilter.GenericFilter()
	com.set_name(_("People with common ancestor with %s") % name)
	com.add_rule(GenericFilter.HasCommonAncestorWith([person.getId()]))
	
	return [all, des, ans, com]

    def add_user_options(self, dialog):
        """
        Override the base class add_user_options task to add
	report specific options
        """
	# what data to extract from database
        self.extract_menu = gtk.Menu()
	idx = 0
	for item in _Extract.extractors:
            menuitem = gtk.MenuItem(item[0])
            menuitem.set_data('extract', idx)
            self.extract_menu.append(menuitem)
	    idx += 1
	self.extract_menu.show_all()

	tip = _("Select which data is collected and which statistics is shown.")
	extract_style = gtk.OptionMenu()
        extract_style.set_menu(self.extract_menu)
        dialog.add_option(self.options_help['extract'][1], extract_style, tip)

	# how to sort the data
        self.sort_menu = gtk.Menu()
	for item in self._sorts:
            menuitem = gtk.MenuItem(item[1])
            menuitem.set_data('sort', item[0])
            self.sort_menu.append(menuitem)
	self.sort_menu.show_all()

	tip = _("Select how the statistical data is sorted.")
	sort_style = gtk.OptionMenu()
        sort_style.set_menu(self.sort_menu)
        dialog.add_option(self.options_help['sort'][1], sort_style, tip)

	# sorting order
	tip = _("Check to reverse the sorting order.")
        self.reverse = gtk.CheckButton(self.options_help['reverse'][1])
        self.reverse.set_active(0)
        dialog.add_option(None, self.reverse, tip)
        self.reverse.show()

	# year range
        self.from_box = gtk.Entry(4)
        self.from_box.set_text(str(self.options_dict['year_from']))
        self.to_box = gtk.Entry(4)
        self.to_box.set_text(str(self.options_dict['year_to']))

	box = gtk.HBox()
	box.add(self.from_box)
	box.add(gtk.Label("-"))
	box.add(self.to_box)
	tip = _("Select year range within which people need to be born to be selected for statistics.")
        dialog.add_option(_('People born between'), box, tip)
        box.show_all()

	# include people without birth year?
	tip = _("Check this if you want people who have no birth date or year to be accounted also in the statistics.")
        self.no_years = gtk.CheckButton(self.options_help['no_years'][1])
        self.no_years.set_active(0)
        dialog.add_option(None, self.no_years, tip)
        self.no_years.show()

	# gender selection
	Person = RelLib.Person
        self.gender_menu = gtk.Menu()
	for item in self._genders:
            menuitem = gtk.MenuItem(item[1])
            menuitem.set_data('gender', item[0])
            self.gender_menu.append(menuitem)
	self.gender_menu.show_all()

	tip = _("Select which genders are included into statistics.")
	genders = gtk.OptionMenu()
        genders.set_menu(self.gender_menu)
        dialog.add_option(self.options_help['gender'][1], genders, tip)

    def parse_user_options(self, dialog):
        """
        Parses the custom options that we have added.
        """
	self.options_dict['year_to'] = int(self.to_box.get_text())
        self.options_dict['year_from'] = int(self.from_box.get_text())
	self.options_dict['no_years'] = self.no_years.get_active()
        self.options_dict['gender'] = self.gender_menu.get_active().get_data('gender')
        self.options_dict['extract'] = self.extract_menu.get_active().get_data('extract')
	self.options_dict['sort'] = self.sort_menu.get_active().get_data('sort')
	self.options_dict['reverse'] = self.reverse.get_active()


#------------------------------------------------------------------------
#
# Register report/options
#
#------------------------------------------------------------------------
from PluginMgr import register_report

register_report(
    name = 'statisticschart',
    category = const.CATEGORY_DRAW,
    report_class = StatisticsChart,
    options_class = StatisticsChartOptions,
    modes = Report.MODE_GUI | Report.MODE_BKI | Report.MODE_CLI,
    translated_name = _("Statistics Chart"),
    status = (_("Alpha")),
    author_name="Eero Tamminen",
    author_email="",
    description= _("Generates statistical bar graphs.")
    )
