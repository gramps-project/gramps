# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

__author__ = "Douglas Blank <Doug.Blank@gmail.com>"
__version__ = "$Revision$"

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _
import datetime, time
from xml.parsers import expat
import const
import os
import locale

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import BaseDoc
from PluginUtils import Report, ReportOptions, ReportUtils, register_report
pt2cm = ReportUtils.pt2cm
from Filters import CustomFilters, GenericFilter, ParamFilter, Rules
from DateHandler import DateDisplay
import RelLib

# _days could be added to DateDisplay:
_codeset = locale.nl_langinfo(locale.CODESET)
# slightly different from _months; this is zero based
_days = (
    unicode(locale.nl_langinfo(locale.DAY_1),_codeset),
    unicode(locale.nl_langinfo(locale.DAY_2),_codeset),
    unicode(locale.nl_langinfo(locale.DAY_3),_codeset),
    unicode(locale.nl_langinfo(locale.DAY_4),_codeset),
    unicode(locale.nl_langinfo(locale.DAY_5),_codeset),
    unicode(locale.nl_langinfo(locale.DAY_6),_codeset),
    unicode(locale.nl_langinfo(locale.DAY_7),_codeset),
    )
_language, _country = "en", "US"
(_language_country, _encoding) = locale.getlocale()
if _language_country != None and _language_country.count("_") == 1:
    (_language, _country) = _language_country.split("_")

#------------------------------------------------------------------------
#
# The one and only GUI, unfortunately. This will be able to be moved to
# Widget once it is created.
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# Support functions
#
#------------------------------------------------------------------------
def easter(year):
    """
    Computes the year/month/day of easter. Currently hardcoded in
    holidays.xml. Based on work by J.-M. Oudin (1940) and is reprinted in
    the "Explanatory Supplement to the Astronomical Almanac", ed. P. K.
    Seidelmann (1992).
    Note: Ash Wednesday is 46 days before Easter Sunday.
    """
    c = year / 100
    n = year - 19 * (year / 19)
    k = (c - 17) / 25
    i = c - c / 4 - (c - k) / 3 + 19 * n + 15
    i = i - 30 * (i / 30)
    i = i - (i / 28) * (1 - (i / 28) * (29 / (i + 1))
                           * ((21 - n) / 11))
    j = year + year / 4 + i + 2 - c + c / 4
    j = j - 7 * (j / 7)
    l = i - j
    month = 3 + (l + 40) / 44
    day = l + 28 - 31 * ( month / 4 )
    return "%d/%d/%d" % (year, month, day)

#------------------------------------------------------------------------
#
# Calendar
#
#------------------------------------------------------------------------
class Calendar(Report.Report):
    """
    Creates the Calendar object that produces the report.
    """
    def __getitem__(self, item):
        """ Used to get items from various places. Could be moved up to Report. """
        if item in self.doc.style_list:
            # font is the only element people refer to in writing reports
            # from the style_list:
            return self.doc.style_list[item].get_font() 
        elif item in self.options_class.options_dict:
            # otherwise it is a option:
            return self.options_class.options_dict[item]
        else:
            raise AttributeError, ("no widget named '%s'" % item)

    def define_graphics_styles(self):
        """ Set up the report. Could be moved up to Report. """
        for widget in self.options_class.widgets:
            if widget.__class__.__name__ == "StyleWidget":
                widget.define_graphics_style(self.doc)

    def get_short_name(self, person, maiden_name = None):
        """ Is there a better, built-in way of getting a short, personal name? """
        nickname = person.get_nick_name()
        if nickname:
            first_name = nickname
        else:
            first_name = person.get_primary_name().get_first_name()
            if first_name:
                first_name = first_name.split()[0] # not middle name
        if nickname.strip().count(" ") > 0: # HACK: first and last name assumed
            family_name = ""
        elif maiden_name != None:
            family_name = maiden_name
        else:
            family_name = person.get_primary_name().get_surname()
        return ("%s %s" % (first_name, family_name)).strip()
        
    def draw_rectangle(self, style, sx, sy, ex, ey):
        """ This should be in BaseDoc """
        self.doc.draw_line(style, sx, sy, sx, ey)
        self.doc.draw_line(style, sx, sy, ex, sy)
        self.doc.draw_line(style, ex, sy, ex, ey)
        self.doc.draw_line(style, sx, ey, ex, ey)

### The rest of these all have to deal with calendar specific things

    def add_day_item(self, text, year, month, day):
        month_dict = self.calendar.get(month, {})
        day_list = month_dict.get(day, [])
        day_list.append(text)
        month_dict[day] = day_list
        self.calendar[month] = month_dict

    def get_holidays(self, year, country = "US"):
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

    def write_report(self):
        """ The short method that runs through each month and creates a page. """
        # initialize the dict to fill:
        self.calendar = {}
        # get the information, first from holidays:
        if self["holidays"]:
            self.get_holidays(self["year"], _country) # currently global
        # get data from database:
        self.collect_data()
        # generate the report:
        for month in range(1, 13):
            self.print_page(month)

    def print_page(self, month):
        """
        This method actually writes the calendar page.
        """
        self.doc.start_page()
        width = self.doc.get_usable_width()
        height = self.doc.get_usable_height()
        header = self.doc.tmargin
        self.draw_rectangle("border", 0, 0, width, height)
        self.doc.draw_bar("title", 0, 0, width, header)
        self.doc.draw_line("border", 0, header, width, header)
        year = self["year"]
        title = "%s %d" % (DateDisplay._months[month], year)
        font_height = pt2cm(1.25 * self["title"].get_size())
        self.doc.center_text("title", title, width/2, font_height + self["offset"]) # 1.0
        cell_width = width / 7
        cell_height = (height - header)/ 6
        current_date = datetime.date(year, month, 1)
        spacing = pt2cm(1.25 * self["text"].get_size()) # 158
        if current_date.isoweekday() != 7: # start dow here is 7, sunday
            current_ord = current_date.toordinal() - current_date.isoweekday()
        else:
            current_ord = current_date.toordinal()
        for day_col in range(7):
            self.doc.center_text("daynames", _days[day_col], # global
                                 day_col * cell_width + cell_width/2,
                                 header - font_height/3.0 + self["offset"]) # .35 
        for week_row in range(6):
            something_this_week = 0
            for day_col in range(7):
                thisday = current_date.fromordinal(current_ord)
                if thisday.month == month:
                    something_this_week = 1
                    self.draw_rectangle("border", day_col * cell_width,
                                        header + week_row * cell_height,
                                        (day_col + 1) * cell_width,
                                        header + (week_row + 1) * cell_height)
                    last_edge = (day_col + 1) * cell_width
                    self.doc.center_text("numbers", str(thisday.day),
                                         day_col * cell_width + cell_width/2,
                                         header + week_row * cell_height + .5 + self["offset"])
                    list = self.calendar.get(month, {}).get(thisday.day, [])
                    position = 0.0 
                    for p in list:
                        lines = p.count("\n") + 1 # lines in the text
                        position += (lines  * spacing)
                        current = 0
                        for line in p.split("\n"):
                            self.doc.write_at("text", line, 
                                              day_col * cell_width + .1,
                                              header + (week_row + 1) * cell_height - position + (current * spacing) + self["offset"])
                            current += 1
                current_ord += 1
        if not something_this_week:
            last_edge = 0
        font_height = pt2cm(1.25 * self["text1style"].get_size())
        self.doc.center_text("text1style", self["text1"], last_edge + (width - last_edge)/2, height - font_height * 3 + self["offset"]) # - 1.5
        self.doc.center_text("text2style", self["text2"], last_edge + (width - last_edge)/2, height - font_height * 2 + self["offset"]) # - 0.78
        self.doc.center_text("text3style", self["text3"], last_edge + (width - last_edge)/2, height - font_height * 1 + self["offset"]) # - 0.30
        self.doc.end_page()

    def collect_data(self):
        """
        This method runs through the data, and collects the relevant dates
        and text.
        """
        filter_num = self.options_class.get_filter_number()
        filters = self.options_class.get_report_filters(self.start_person)
        filters.extend(CustomFilters.get_filters())
        self.filter = filters[filter_num]
        people = self.filter.apply(self.database,
                                   self.database.get_person_handles(sort_handles=False))
        for person_handle in people:
            person = self.database.get_person_from_handle(person_handle)
            birth_ref = person.get_birth_ref()
            birth_date = None
            if birth_ref:
                birth_event = self.database.get_event_from_handle(birth_ref.ref)
                birth_date = birth_event.get_date_object()
                    
            death_ref = person.get_death_ref()
            death_date = None
            if death_ref:
                death_event = self.database.get_event_from_handle(death_ref.ref)
                death_date = death_event.get_date_object()
            if death_date == None:
                alive = True # well, until we get probably_alive in here
            else:
                alive = False
            if self["birthdays"] and birth_date != None and ((self["alive"] and alive) or not self["alive"]):
                year = birth_date.get_year()
                month = birth_date.get_month()
                day = birth_date.get_day()
                age = self["year"] - year
                # add some things to handle maiden name:
                father_lastname = None # husband, actually
                if self["maiden_name"] == 0: # get husband's last name:
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
            if self["anniversaries"] and ((self["alive"] and alive) or not self["alive"]):
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
                            if self["alive"]:
                                spouse_death_ref = spouse.get_death_ref()
                                if spouse_death_ref:
                                    # there is a death event, maybe empty though
                                    spouse_death_event = self.database.get_event_from_handle(spouse_death_ref.ref)
                                    if spouse_death_event != None:
                                        spouse_death_date = spouse_death_event.get_date_object()
                                        if spouse_death_date: # BUG: couldn't remove event
                                            continue
                            for event_ref in fam.get_event_ref_list():
                                event = self.database.get_event_from_handle(event_ref.ref)
                                event_obj = event.get_date_object()
                                year = event_obj.get_year()
                                month = event_obj.get_month()
                                day = event_obj.get_day()
                                years = self["year"] - year
                                text = _("%(spouse)s and\n %(person)s, %(nyears)d") % {
                                    'spouse' : spouse_name,
                                    'person' : short_name,
                                    'nyears' : years,
                                    }
                                self.add_day_item(text, year, month, day)

###################################################################################
# These classes are a suggested of how to rework the graphics out of reports. It also
# makes these items abstractions, which makes it easy to change the report
# infrastructure without having everyone rewrite their reports each time.
#
# This builds on the current document code, so no changes are needed.
###################################################################################
class Widget:
    """ A Widget virtual base class. This contains no graphics specifics. """
    commonDefaults = {
        "wtype"      : None,
        "name"       : None,
        "label"      : None,
        "help"       : None,
        "wtype"      : None,
        "valid_text" : None,
        "frame"      : None,
        "value"      : None,
        }
    defaults = {}
    def __init__(self, option_object, **args):
        self.option_object = option_object
        self.setup(args)
        self.register()
    def __getitem__(self, key):
        if key in self.settings:
            return self.settings[key]
        else:
            raise AttributeError, ("no widget attribute named '%s'" % key)
    def __setitem__(self, key, value):
        self.settings[key] = value
    def setup(self, args = {}):
        # start with the base defaults common to all:
        self.settings = self.commonDefaults.copy()
        # now add those from the subclass:
        self.settings.update(self.defaults)
        # ad finally, those from the user:
        self.settings.update(args)
    def register(self):
        className = self.__class__.__name__
        if className == "FilterWidget":
            self.option_object.enable_dict['filter'] =  0
        elif className == "StyleWidget":
            self.option_object[self["name"]] = self["value"]
        else:
            self.option_object[self["name"]] = self["value"]
            self.option_object.options_help[self["name"]] = (
                self["wtype"], self["help"], self["valid_text"])
    def add_gui(self, dialog): pass
    def update(self): pass
class SpinWidget(Widget):
    """ A spinner number selector widget for GTK. """
    defaults = {
        "wtype"     : "=num",
        "help"      : "Numeric option",
        "valid_text": "Any number",
        }
    def add_gui(self, dialog):
        keyword = self["name"]
        obj = self.option_object.__dict__
        obj[keyword] = gtk.SpinButton()
        obj[keyword].set_digits(0)
        obj[keyword].set_increments(1,2)
        obj[keyword].set_range(0,2100)
        obj[keyword].set_numeric(True)
        obj[keyword].set_value(self.option_object[keyword])
        if self["frame"] != None:
            dialog.add_frame_option(self["frame"], self["label"], obj[keyword])
        else:
            dialog.add_option(self["label"], obj[keyword])
    def update(self):
        dict = self.option_object.__dict__
        keyword = self["name"]
        self.option_object[keyword] = dict[keyword].get_value_as_int()
        self[keyword] = dict[keyword].get_value_as_int()
class CheckWidget(Widget):
    """ A check box widget for GTK. """
    defaults = {
        "wtype"     : "=0/1",
        "help"      : "Yes/No option",
        "valid_text": "1 for yes, 0 for no",
        }
    def add_gui(self, dialog):
        keyword = self["name"]
        obj = self.option_object.__dict__        
        obj[keyword] = gtk.CheckButton(self["label"])
        obj[keyword].set_active(self.option_object[keyword])
        if self["frame"] != None:
            dialog.add_frame_option(self["frame"], "", obj[keyword])
        else:
            dialog.add_option("", obj[keyword])
    def update(self):
        dict = self.option_object.__dict__
        keyword = self["name"]
        self.option_object[keyword] = int(dict[keyword].get_active())
        self[keyword] = int(dict[keyword].get_active())
class EntryWidget(Widget):
    """ A text widget for GTK. """
    defaults = {
        "wtype"     : "=str",
        "help"      : "String option",
        "valid_text": "Any textual data",
        }
    def add_gui(self, dialog):
        keyword = self["name"]
        obj = self.option_object.__dict__
        obj[keyword] = gtk.Entry()
        obj[keyword].set_text(self.option_object[keyword])
        if self["frame"] != None:
            dialog.add_frame_option(self["frame"], self["label"], obj[keyword])
        else:
            dialog.add_option(self["label"], obj[keyword])            
    def update(self):
        dict = self.option_object.__dict__
        keyword = self["name"]
        self.option_object[keyword] = unicode(dict[keyword].get_text())
        self[keyword] = unicode(dict[keyword].get_text())
class NumberWidget(EntryWidget):
    """ A number widget for GTK. """
    defaults = {
        "wtype"     : "=num",
        "help"      : "Numeric option",
        "valid_text": "Any number",
        }
    def add_gui(self, dialog):
        keyword = self["name"]
        obj = self.option_object.__dict__
        obj[keyword] = gtk.Entry()
        obj[keyword].set_text(str(self.option_object[keyword]))
        if self["frame"] != None:
            dialog.add_frame_option(self["frame"], self["label"], obj[keyword])
        else:
            dialog.add_option(self["label"], obj[keyword])            
    def update(self):
        dict = self.option_object.__dict__
        keyword = self["name"]
        self.option_object[keyword] = float(dict[keyword].get_text())
        self[keyword] = float(dict[keyword].get_text())
class StyleWidget(Widget):
    defaults = {
        "size"      : 8,
        "bold"      : 0,
        "italics"   : 0,
        "type_face" : BaseDoc.FONT_SERIF,
        "fill_color": None,
        }
    def make_default_style(self, default_style):
        f = BaseDoc.FontStyle()
        f.set_size(self["size"])
        f.set_italic(self["italics"])
        f.set_bold(self["bold"])
        f.set_type_face(self["type_face"])
        p = BaseDoc.ParagraphStyle()
        p.set_font(f)
        p.set_description(self["label"])
        default_style.add_style(self["name"],p)
    def define_graphics_style(self, document):
        g = BaseDoc.GraphicsStyle()
        g.set_paragraph_style(self["name"])
        if self["fill_color"]:
            g.set_fill_color(self["fill_color"])
        # FIXME: add all other graphics items (color, etc) here
        document.add_draw_style(self["name"],g)
class FilterWidget(Widget):
    """
    A filter widget. This doesn't have the GTK code here, but should.
    This class takes names of the filters and does everything for you.
    "all filters" - all of them
    "everyone" - all people in table
    "descendents" - direct descendents
    "descendent familes" - direct descendents and their familes
    "ancestors" - all ancestors of person
    "common ancestors" - all common ancestors
    "calendar attribute" - experimental filter for tagging people
    """
    def get_filters(self, person):
        """Set up the list of possible content filters."""
        if person:
            name = person.get_primary_name().get_name()
            gramps_id = person.get_gramps_id()
        else:
            name = 'PERSON'
            gramps_id = ''
        retval = []
        for filter in self["filters"]:
            if filter in ["everyone", "all filters"]:
                f = GenericFilter()
                f.set_name(_("Entire Database"))
                f.add_rule(Rules.Person.Everyone([]))
                retval.append(f)
            if filter in ["descendants", "all filters"]:
                f = GenericFilter()
                f.set_name(_("Descendants of %s") % name)
                f.add_rule(Rules.Person.IsDescendantOf([gramps_id,1]))
                retval.append(f)
            if filter in ["descendant families", "all filters"]:
                f = GenericFilter()
                f.set_name(_("Descendant Families of %s") % name)
                f.add_rule(Rules.Person.IsDescendantFamilyOf([gramps_id]))
                retval.append(f)
            if filter in ["ancestors", "all filters"]:
                f = GenericFilter()
                f.set_name(_("Ancestors of %s") % name)
                f.add_rule(Rules.Person.IsAncestorOf([gramps_id,1]))
                retval.append(f)
            if filter in ["common ancestors", "all filters"]:
                f = GenericFilter()
                f.set_name(_("People with common ancestor with %s") % name)
                f.add_rule(Rules.Person.HasCommonAncestorWith([gramps_id]))
                retval.append(f)
            if filter in ["calendar attribute", "all filters"]:
                f = ParamFilter()
                f.set_name(_("People with a Calendar attribute"))
                f.add_rule(Rules.Person.HasTextMatchingSubstringOf(['Calendar',0,0]))
                retval.append(f)
        return retval

# -----------------------------------------------------------------
# The following could all be moved to the parent class, if you wanted
# to adopt this report reworking. Even if you didn't want to use them
# it would be ok to put there, because self.widgets would be empty.
# -----------------------------------------------------------------

class NewReportOptions(ReportOptions.ReportOptions):
    """
    Defines options and provides code to handling the interface.
    This is free of any graphics specifics.
    """
    def __getitem__(self, keyword):
        """ This could be moved up to ReportOptions """
        if keyword in self.options_dict:
            return self.options_dict[keyword]
        else:
            raise AttributeError, ("no widget named '%s'" % keyword)

    def __setitem__(self, keyword, value):
        """ This could be moved up to ReportOptions """
        self.options_dict[keyword] = value

    def add_user_options(self,dialog):
        for widget in self.widgets:
            widget.add_gui(dialog)

    def parse_user_options(self,dialog):
        for widget in self.widgets:
            widget.update()
        
    def get_report_filters(self,person):
        for widget in self.widgets:
            if widget.__class__.__name__ == "FilterWidget":
                return widget.get_filters(person)

    def make_default_style(self,default_style):
        for widget in self.widgets:
            if widget.__class__.__name__ == "StyleWidget":
                widget.make_default_style(default_style)

class CalendarOptions(NewReportOptions):
    def enable_options(self):
        self.enable_dict = {}
        self.widgets = [
            FilterWidget(self, label = _("Filter"),
                         name = "filter",
                         filters = ["all filters"]),
            EntryWidget(self, label = _("Text 1"),
                        name  = "text1",
                        value = "My Calendar",
                        help  = "Large text area",
                        valid_text = "Any text",
                        frame = _("Text Options")
                        ),                       
            EntryWidget(self, label = _("Text 2"),
                        name  = "text2",
                        value = "Produced with GRAMPS",
                        help  = "Medium size text",
                        valid_text = "Any text",
                        frame = _("Text Options")
                        ),                       
            EntryWidget(self, label = _("Text 3"),
                        name  = "text3",
                        value = "http://gramps-project.org/",
                        help  = "Small text area",
                        valid_text = "Any text",
                        frame = _("Text Options")
                        ),                       
            SpinWidget(self, label = _("Year of calendar"),
                       name  = "year",
                       value = time.localtime()[0], # the current year
                       help  = "Year of calendar",
                       valid_text = "Any year",
                       ),
            CheckWidget(self, label = _("Use maiden names"),
                        name = "maiden_name",
                        value = 1,
                        help = "Use married women's maiden name.",
                        valid_text = "Select to use married women's maiden name.",
                        ),
            CheckWidget(self, label = _("Only include living people"),
                        name = "alive",
                        value = 1,
                        help = "Include only living people",
                        valid_text = "Select to only include living people",
                        ),
            CheckWidget(self, label = _("Include birthdays"),
                        name = "birthdays",
                        value = 1,
                        help = "Include birthdays",
                        valid_text = "Select to include birthdays",
                        ),
            CheckWidget(self, label = _("Include anniversaries"),
                        name = "anniversaries",
                        value = 1,
                        help = "Include anniversaries",
                        valid_text = "Select to include anniversaries",
                        ),
            CheckWidget(self, label = _("Include holidays"),
                        name = "holidays",
                        value = 1,
                        help = "Include holidays",
                        valid_text = "Select to include holidays",
                        ),
            NumberWidget(self, label = _("Offset"),
                        name  = "offset",
                        value = -0.5,
                        help  = "Distance to move text on page",
                        valid_text = "Any number",
                        frame = "Text Options"
                        ),                       
            StyleWidget(self, label = _('Title text and background color.'),
                        name = "title",
                        size = 20,
                        italics = 1,
                        bold = 1,
                        fill_color = (0xEA,0xEA,0xEA),
                        type_face = BaseDoc.FONT_SERIF,
                        ),
            StyleWidget(self, label = _('Border lines of calendar boxes.'),
                        name = "border",
                        ),
            StyleWidget(self, label = _('Calendar day numbers.'),
                        name = "numbers",
                        size = 13,
                        bold = 1,
                        type_face = BaseDoc.FONT_SERIF,
                        ),
            StyleWidget(self, label = _('Daily text display.'),
                        name = "text",
                        size = 9,
                        type_face = BaseDoc.FONT_SERIF,
                        ),
            StyleWidget(self, label = _('Days of the week text.'),
                        name = "daynames",
                        size = 12,
                        italics = 1,
                        bold = 1,
                        type_face = BaseDoc.FONT_SERIF,
                        ),
            StyleWidget(self, label = _('Text at bottom, line 1.'),
                        name = "text1style",
                        size = 12,
                        type_face = BaseDoc.FONT_SERIF,
                        ),
            StyleWidget(self, label = _('Text at bottom, line 2.'),
                        name = "text2style",
                        size = 12,
                        type_face = BaseDoc.FONT_SERIF,
                        ),
            StyleWidget(self, label = _('Text at bottom, line 3.'),
                        name = "text3style",
                        size = 9,
                        type_face = BaseDoc.FONT_SERIF,
                        ),
            ]

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
        self.country = country
        self.dates = []
        self.initialize()
    def set_country(self, country):
        self.country = country
        self.dates = []
        self.initialize()        
    def initialize(self):
        # parse the date objects
        for country_set in self.elements.children:
            if country_set.name == "country" and country_set.attributes["name"] == self.country:
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

#------------------------------------------------------------------------
#
# Register this plugin
#
#------------------------------------------------------------------------
register_report(
    name = 'calendar',
    category = Report.CATEGORY_DRAW,
    report_class = Calendar,
    options_class = CalendarOptions,
    modes = Report.MODE_GUI | Report.MODE_BKI | Report.MODE_CLI,
    translated_name = _("Calendar"),
    status = _("Experimental"),
    author_name = "Douglas S. Blank",
    author_email = "Doug.Blank@gmail.com",
    description = _("Produces a graphical calendar"),
    )
