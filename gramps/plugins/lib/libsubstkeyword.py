#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Peter G. Landgren
# Copyright (C) 2010       Craig J. Anderson
# Copyright (C) 2014       Paul Franklin
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Provide the SubstKeywords class that will replace keywords in a passed
string with information about the person/marriage/spouse. For example:

foo = SubstKeywords(database, person_handle)
print foo.replace_and_clean(['$n was born on $b.'])

Will return a value such as:

Mary Smith was born on 3/28/1923.
"""

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.lib import EventType, PlaceType, Location
from gramps.gen.utils.db import get_birth_or_fallback, get_death_or_fallback
from gramps.gen.utils.location import get_main_location
from gramps.gen.display.place import displayer as _pd
from gramps.gen.const import GRAMPS_LOCALE as glocale


#------------------------------------------------------------------------
#
# Local constants
#
#------------------------------------------------------------------------
class TextTypes:
    """Four enumerations that are used to for the four main parts of a string.

    and used for states.  Separator is not used in states.
    text   -> remove or display
    remove -> display
    """
    separator, text, remove, display = list(range(4))
TXT = TextTypes()


#------------------------------------------------------------------------
#
# Formatting classes
#
#------------------------------------------------------------------------
class GenericFormat:
    """A Generic parsing class.  Will be subclassed by specific format strings
    """

    def __init__(self, string_in, qlocale=glocale):
        self.string_in = string_in
        self._locale = qlocale

    def _default_format(self, item):
        """ The default format if there is no format string """
        pass

    def is_blank(self, item):
        """ if the information is not known (item is None), remove the format
        string information from the input string if any.
        """
        if item is None:
            self.string_in.remove_start_end("(", ")")
            return True
        return False

    def generic_format(self, item, code, uppr, function):
        """the main parsing engine.

        Needed are the following:  the input string
        code - List of one character (string) codes (all lowercase)
        uppr - list of one character (string) codes that can be uppercased
            each needs to have a lowercase equivalent in code
        function - list of functions.
        there is a one to one relationship with character codes and functions.
        """
        if self.string_in.this != "(":
            return self._default_format(item)
        self.string_in.step()

        main = VarString()
        separator = SeparatorParse(self.string_in)
        #code given in args
        #function given in args

        while self.string_in.this and self.string_in.this != ")":
            #Check to see if _in.this is in code
            to_upper = False
            if uppr.find(self.string_in.this) != -1:
                #and the result should be uppercased.
                to_upper = True
                where = code.find(self.string_in.this.lower())
            else:
                where = code.find(self.string_in.this)
            if where != -1:
                self.string_in.step()
                tmp = function[where]()
                if to_upper:
                    tmp = tmp.upper()
                if tmp == "" or tmp is None:
                    main.add_remove()
                elif isinstance(tmp, VarString):  # events cause this
                    main.extend(tmp)
                else:
                    main.add_variable(tmp)
            elif separator.is_a():
                main.add_separator(separator.parse_format())
            else:
                main.add_text(self.string_in.parse_format())

        if self.string_in.this == ")":
            self.string_in.step()

        return main


#------------------------------------------------------------------------
# Name Format strings
#------------------------------------------------------------------------
class NameFormat(GenericFormat):
    """ The name format class.
    If no format string, the name is displayed as per preference options
    otherwise, parse through a format string and put the name parts in
    """

    def __init__(self, _in, locale, name_displayer):
        GenericFormat.__init__(self, _in, locale)
        self._nd = name_displayer

    def get_name(self, person, aka):
        """ A helper method for retrieving the person's name """
        name = None
        if person:
            if aka is None:
                name = person.get_primary_name()
            else:
                for names in person.get_alternate_names():
                    if names.get_type() == aka:
                        name = names
                        break
        return name

    def _default_format(self, name):
        """ display the name as set in preferences """
        return self._nd.sorted_name(name)

    def parse_format(self, name):
        """ Parse the name """
        if self.is_blank(name):
            return

        def common():
            """ return the common name of the person """
            return (name.get_call_name() or
                    name.get_first_name().split(' ')[0])

        code = "tfcnxslg"
        upper = code.upper()
        function = [name.get_title,            # t
                    name.get_first_name,       # f
                    name.get_call_name,        # c
                    name.get_nick_name,        # n
                    common,                    # x
                    name.get_suffix,           # s
                    name.get_surname,          # l
                    name.get_family_nick_name  # g
                   ]

        return self.generic_format(name, code, upper, function)


#------------------------------------------------------------------------
# Date Format strings
#------------------------------------------------------------------------
class DateFormat(GenericFormat):
    """ The date format class.
    If no format string, the date is displayed as per preference options
    otherwise, parse through a format string and put the date parts in
    """

    def get_date(self, event):
        """ A helper method for retrieving a date from an event """
        if event:
            return event.get_date_object()
        return None

    def _default_format(self, date):
        return self._locale.date_displayer.display(date)

    def __count_chars(self, char, max_amount):
        """ count the year/month/day codes """
        count = 1  # already have seen/passed one
        while count < max_amount and self.string_in.this == char:
            self.string_in.step()
            count = count +1
        return count

    def parse_format(self, date):
        """ Parse the name """

        if self.is_blank(date):
            return

        def year(year, count):
            """  The year part only """
            year = str(year)
            if year == "0":
                return

            if count == 1:  # found 'y'
                if len(year) == 1:
                    return year
                elif year[-2] == "0":
                    return year[-1]
                else:
                    return year[-2:]
            elif count == 2:  # found 'yy'
                tmp = "0" + year
                return tmp[-2:]
            elif count == 3:  # found 'yyy'
                if len(year) > 2:
                    return year
                else:
                    tmp = "00" + year
                    return tmp[-3:]
            else:  # count == 4  # found 'yyyy'
                tmp = "000" + year
                return tmp[-4:]

        def month(month, count):
            """  The month part only """
            month = str(month)
            if month == "0":
                return

            if count == 1:
                return month
            elif count == 2:  # found 'mm'
                tmp = "0" + month
                return tmp[-2:]
            elif count == 3:   # found 'mmm'
                return self._locale.date_displayer.short_months[int(month)]
            else:  # found 'mmmm'
                return self._locale.date_displayer.long_months[int(month)]

        def day(day, count):
            """  The day part only """
            day = str(day)
            if day == "0":  # 0 means not defined!
                return

            if count == 1:  # found 'd'
                return day
            else:  # found 'dd'
                tmp = "0" + day
                return tmp[-2:]

        def text():
            return date.get_text()

        def s_year():
            return year(date.get_year(), self.__count_chars("y", 4))

        def s_month():
            return month(date.get_month(), self.__count_chars("m", 4))

        def su_month():
            return month(date.get_month(), self.__count_chars("M", 4)).upper()

        def s_day():
            return day(date.get_day(), self.__count_chars("d", 2))

        def e_year():
            return year(date.get_stop_year(), self.__count_chars("z", 4))

        def e_month():
            return month(date.get_stop_month(), self.__count_chars("n", 4))

        def eu_month():
            return month(date.get_stop_month(),
                         self.__count_chars("N", 4)).upper()

        def e_day():
            return day(date.get_stop_day(), self.__count_chars("e", 2))

        def modifier():
            #ui_mods taken from date.py def lookup_modifier(self, modifier):
            # trans_text is a defined keyword (in po/update_po.py, po/genpot.sh)
            trans_text = self._locale.translation.gettext
            ui_mods = ["", trans_text("before"), trans_text("after"),
                       trans_text("about"), "", "", ""]
            return ui_mods[date.get_modifier()]


        code = "ymMd" + "znNe" + "ot"
        upper = "OT"
        function = [s_year, s_month, su_month, s_day,
                    e_year, e_month, eu_month, e_day,
                    modifier, text]

        return self.generic_format(date, code, upper, function)


#------------------------------------------------------------------------
# Place Format strings
#------------------------------------------------------------------------
class PlaceFormat(GenericFormat):
    """ The place format class.
    If no format string, the place is displayed as per preference options
    otherwise, parse through a format string and put the place parts in
    """

    def __init__(self, database, _in):
        self.database = database
        GenericFormat.__init__(self, _in)

    def get_place(self, database, event):
        """ A helper method for retrieving a place from an event """
        if event:
            bplace_handle = event.get_place_handle()
            if bplace_handle:
                return database.get_place_from_handle(bplace_handle)
        return None

    def _default_format(self, place):
        return _pd.display(self.database, place)

    def parse_format(self, database, place):
        """ Parse the place """

        if self.is_blank(place):
            return

        code = "elcuspn" + "oitxy"
        upper = code.upper()

        main_loc = get_main_location(database, place)
        location = Location()
        location.set_street(main_loc.get(PlaceType.STREET, ''))
        location.set_locality(main_loc.get(PlaceType.LOCALITY, ''))
        location.set_parish(main_loc.get(PlaceType.PARISH, ''))
        location.set_city(main_loc.get(PlaceType.CITY, ''))
        location.set_county(main_loc.get(PlaceType.COUNTY, ''))
        location.set_state(main_loc.get(PlaceType.STATE, ''))
        location.set_postal_code(main_loc.get(PlaceType.STREET, ''))
        location.set_country(main_loc.get(PlaceType.COUNTRY, ''))

        function = [location.get_street,
                    location.get_locality,
                    location.get_city,
                    location.get_county,
                    location.get_state,
                    place.get_code,
                    location.get_country,

                    location.get_phone,
                    location.get_parish,
                    place.get_title,
                    place.get_longitude,
                    place.get_latitude
                   ]

        return self.generic_format(place, code, upper, function)


#------------------------------------------------------------------------
# Event Format strings
#------------------------------------------------------------------------
class EventFormat(GenericFormat):
    """ The event format class.
    If no format string, the event description is displayed
    otherwise, parse through the format string and put in the parts
        dates and places can have their own format strings
    """

    def __init__(self, database, _in, locale):
        self.database = database
        GenericFormat.__init__(self, _in, locale)

    def _default_format(self, event):
        if event is None:
            return
        else:
            return event.get_description()

    def __empty_format(self):
        """ clear out a sub format string """
        self.string_in.remove_start_end("(", ")")
        return

    def __empty_attrib(self):
        """ clear out an attribute name """
        self.string_in.remove_start_end("[", "]")
        return

    def parse_format(self, event):
        """ Parse the event format string.
        let the date or place classes handle any sub-format strings """

        if self.is_blank(event):
            return

        def format_date():
            """ start formatting a date in this event """
            date_format = DateFormat(self.string_in, self._locale)
            return date_format.parse_format(date_format.get_date(event))

        def format_place():
            """ start formatting a place in this event """
            place_format = PlaceFormat(self.database, self.string_in)
            place = place_format.get_place(self.database, event)
            return place_format.parse_format(self.database, place)

        def format_attrib():
            """ Get the name and then get the attributes value """
            #Event's Atribute
            attrib_parse = AttributeParse(self.string_in)
            #self.string_in.step()
            name = attrib_parse.get_name()
            if name:
                return attrib_parse.get_attribute(event.get_attribute_list(),
                                                  name)
            else:
                return

        code = "ndDia"
        upper = ""
        function = [event.get_description,
                    format_date,
                    format_place,
                    event.get_gramps_id,
                    format_attrib
                   ]

        return self.generic_format(event, code, upper, function)

    def parse_empty(self):
        """ remove the format string """

        code = "dDa"
        function = [self.__empty_format, self.__empty_format,
                    self.__empty_attrib]

        return self.generic_format(None, code, "", function)


#------------------------------------------------------------------------
# gramps info Format strings
#------------------------------------------------------------------------
class GrampsFormat:
    """ The Gramps Info Format class.
        This only polls information from system information.
    """

    def __init__(self, _in, _db):
        self.string_in = _in
        self.db = _db

    def parse_format(self):
        """ Parse the Gramps format string.
        let the date or place classes handle any sub-format strings """
        from gramps.version import VERSION

        from gramps.gen.utils.config import get_researcher
        owner = get_researcher()

        code = "vtd" + "elcspn" + "om"
        info = [VERSION,
                owner.get_name(),
                self.db.get_dbname(),

                owner.get_address(),
                owner.get_locality(),
                owner.get_city(),
                owner.get_state(),
                owner.get_postal_code(),
                owner.get_country(),

                owner.get_phone(),
                owner.get_email()
               ]

        where = code.find(self.string_in.this)
        if where != -1:
            self.string_in.step()
            return info[where]
        return "$G"


#------------------------------------------------------------------------
# Gallery Format strings
#------------------------------------------------------------------------
class GalleryFormat(GenericFormat):
    """ The gallery format class.
    If no format string, the photo description is displayed
    otherwise, parse through the format string and put in the parts
        dates (no places) can have their own format strings
    """

    def __init__(self, database, _in, locale):
        self.database = database
        GenericFormat.__init__(self, _in, locale)

    def _default_format(self, photo):
        if photo is None:
            return
        else:
            return photo.get_description()

    def __empty_format(self):
        """ clear out a sub format string """
        self.string_in.remove_start_end("(", ")")
        return

    def __empty_attrib(self):
        """ clear out an attribute name """
        self.string_in.remove_start_end("[", "]")
        return

    def parse_format(self, photo):
        """ Parse the photo format string.
        let the date or place classes handle any sub-format strings """

        if self.is_blank(photo):
            return

        def format_date():
            """ start formatting a date in this photo """
            date_format = DateFormat(self.string_in, self._locale)
            return date_format.parse_format(date_format.get_date(photo))

        def format_attrib():
            """ Get the name and then get the attributes value """
            #photo's Atribute
            attrib_parse = AttributeParse(self.string_in)
            name = attrib_parse.get_name()
            if name:
                return attrib_parse.get_attribute(photo.get_attribute_list(),
                                                  name)
            else:
                return

        code = "ndia"
        upper = ""
        function = [photo.get_description,
                    format_date,
                    photo.get_gramps_id,
                    format_attrib
                   ]

        return self.generic_format(photo, code, upper, function)

    def parse_empty(self):
        """ remove the format string """

        code = "da"
        function = [self.__empty_format, self.__empty_attrib]

        return self.generic_format(None, code, "", function)


#------------------------------------------------------------------------
#
# ConsumableString - The Input string class
#
#------------------------------------------------------------------------
class ConsumableString:
    """
    A simple string implementation with extras to help with parsing.

    This will contain the string to be parsed.  or string in.
    There will only be one of these for each processed line.
    """
    def __init__(self, string):
        self.__this_string = string
        self.__setup()

    def __setup(self):
        """ update class attributes this and next """
        if len(self.__this_string) > 0:
            self.this = self.__this_string[0]
        else:
            self.this = None
        if len(self.__this_string) > 1:
            self.next = self.__this_string[1]
        else:
            self.next = None

    def step(self):
        """ remove the first char from the string """
        self.__this_string = self.__this_string[1:]
        self.__setup()
        return self.this

    def step2(self):
        """ remove the first two chars from the string """
        self.__this_string = self.__this_string[2:]
        self.__setup()
        return self.this

    def remove_start_end(self, start, end):
        """ Removes a start, end block from the string if there """
        if self.this == start:
            self.text_to_next(end)

    def __get_a_char_of_text(self):
        """ Removes one char of TEXT from the string and returns it. """
        if self.this == "\\":
            if self.next is None:
                rtrn = "\\"
            else:
                rtrn = self.next
            self.step2()
        else:
            rtrn = self.this
            self.step()
        return rtrn

    def text_to_next(self, char):
        """ return/remove a format strings from here """
        new_str = ""
        while self.this is not None and self.this != char:
            new_str += self.__get_a_char_of_text()
        if self.this == char:
            self.step()
        return new_str

    def is_a(self):
        return True

    def parse_format(self):
        rtrn = self.__get_a_char_of_text()

        if rtrn:
            return rtrn
        return ''


#------------------------------------------------------------------------
#
# VarString class  - The Output string class
#
#------------------------------------------------------------------------
class VarString:
    """
    The current state of the entire string (integer from TextTypes)
    A list to hold tuple object (integer from TextTypes, string)

    This will contain the string that will be displayed.  or string out.
    it is used for groups and format strings.
    """
    def __init__(self, start_state=TXT.remove):
        self.state = start_state  # overall state of the string.
        self._text = []  # list of tuples (TXT.?, string)

    def __update_state(self, new_status):
        if new_status > self.state:
            self.state = new_status

    def add_text(self, text):
        self._text.append((TXT.text, text))

    def add_variable(self, text):
        self.state = TXT.display
        self._text.append((TXT.text, text))

    def add_remove(self):
        self.__update_state(TXT.remove)
        self._text.append((TXT.remove, ""))

    def add_separator(self, text):
        self._text.append((TXT.separator, text))

    def get_final(self):
        #if self.state == TXT.remove:
        #    return (TXT.remove, "")

        curr_string = ""
        index = 0

        while index < len(self._text):

            if self._text[index][0] == TXT.text:
                curr_string += self._text[index][1]
                index = index + 1
                continue  # while self._text:
            if index +1 == len(self._text):
                if self._text[index][0] == TXT.separator and curr_string != '':
                    curr_string += self._text[index][1]
                index = index + 1
                break  # while self._text:

            type_0_1 = (self._text[index][0], self._text[index+1][0])

            #if   type_0_1 == (TXT.remove, TXT.remove):
            #    pass
            if type_0_1 == (TXT.remove, TXT.separator):
                index = index + 1
            #elif type_0_1 == (TXT.remove, TXT.text):
            #    pass
            elif type_0_1 == (TXT.separator, TXT.remove):
                index = index + 1
            #elif type_0_1 == (TXT.separator, TXT.separator):
            #    pass
            elif type_0_1 == (TXT.separator, TXT.text):
                curr_string += self._text[index][1]
            #else:
            #    print "#oops  Should never get here."
            index = index + 1

        #return what we have
        return (self.state, curr_string)
        #print("===" + str(self.state) + " '" + str(curr_string) + "'")

    def extend(self, acquisition):
        """
            acquisition is a VarString object
            Merge the content of acquisition into this place.
        """
        self.__update_state(acquisition.state)

        if acquisition.state != TXT.display:
            #The sub {} was TXT.remove.  We don't want to simply ignore it.
            self.add_remove() # add a remove que here to note it.
            return

        self._text.extend(acquisition._text)


#------------------------------------------------------------------------
#
# Parsers
#
#------------------------------------------------------------------------
#------------------------------------------------------------------------
# SeparatorParse
#------------------------------------------------------------------------
class SeparatorParse:
    """ parse out a separator """
    def __init__(self, consumer_in):
        self._in = consumer_in

    def is_a(self):
        return self._in.this == "<"

    def parse_format(self):
        if not self.is_a():
            return
        """ get the text and return it """
        self._in.step()
        return self._in.text_to_next(">")

#------------------------------------------------------------------------
# AttributeParse
#------------------------------------------------------------------------
class AttributeParse:
    """  Parse attributes """

    def __init__(self, consumer_in):
        self._in = consumer_in

    def get_name(self):
        """ Gets a name inside a [] block """
        if self._in.this != "[":
            return
        self._in.step()
        return self._in.text_to_next("]")

    def get_attribute(self, attrib_list, attrib_name):
        """ Get an attribute by name """
        if attrib_name == "":
            return
        for attr in attrib_list:
            if str(attr.get_type()) == attrib_name:
                return str(attr.get_value())
        return

    def is_a(self):
        """ check """
        return self._in.this == "a"

    def parse_format(self, attrib_list):
        """ Get the attribute and add it to the string out """
        name = self.get_name()
        return self.get_attribute(attrib_list, name)

#------------------------------------------------------------------------
# VariableParse
#------------------------------------------------------------------------
class VariableParse:
    """ Parse the individual variables """

    def __init__(self, friend, database, consumer_in, locale, name_displayer):
        self.friend = friend
        self.database = database
        self._in = consumer_in
        self._locale = locale
        self._nd = name_displayer

    def is_a(self):
        """ check """
        return self._in.this == "$" and self._in.next is not None and \
                              "nsijbBdDmMvVauetTpPG".find(self._in.next) != -1

    def get_event_by_type(self, marriage, e_type):
        """ get an event from a type """
        if marriage is None:
            return None
        for e_ref in marriage.get_event_ref_list():
            if not e_ref:
                continue
            event = self.friend.database.get_event_from_handle(e_ref.ref)
            if event.get_type() == e_type:
                return event
        return None

    def get_event_by_name(self, person, event_name):
        """ get an event from a name. """
        if not person:
            return None
        for e_ref in person.get_event_ref_list():
            if not e_ref:
                continue
            event = self.friend.database.get_event_from_handle(e_ref.ref)
            if str(event.get_type()) == event_name:
                return event
        return None

    def empty_item(self, item):
        """ return false if there is a valid item(date or place).
        Otherwise
            add a TXT.remove marker in the output string
            remove any format strings from the input string
        """
        if item is not None:
            return False

        self._in.remove_start_end("(", ")")
        return True

    def empty_attribute(self, person):
        """ return false if there is a valid person.
        Otherwise
            add a TXT.remove marker in the output string
            remove any attribute name from the input string
        """
        if person:
            return False

        self._in.remove_start_end("[", "]")
        return True

    def __parse_date(self, event):
        """ sub to process a date
        Given an event, get the date object, process the format,
        return the result """
        date_f = DateFormat(self._in, self._locale)
        date = date_f.get_date(event)
        if self.empty_item(date):
            return
        return date_f.parse_format(date)

    def __parse_place(self, event):
        """ sub to process a date
        Given an event, get the place object, process the format,
        return the result """
        place_f = PlaceFormat(self.database, self._in)
        place = place_f.get_place(self.database, event)
        if self.empty_item(place):
            return
        return place_f.parse_format(self.database, place)

    def __parse_name(self, person, attrib_parse):
        name_format = NameFormat(self._in, self._locale, self._nd)
        name = name_format.get_name(person, attrib_parse.get_name())
        return name_format.parse_format(name)

    def __parse_id(self, first_class_object):
        if first_class_object is not None:
            return first_class_object.get_gramps_id()
        else:
            return

    def __parse_event(self, person, attrib_parse):
        event = self.get_event_by_name(person, attrib_parse.get_name())
        event_f = EventFormat(self.database, self._in, self._locale)
        if event:
            return event_f.parse_format(event)
        else:
            event_f.parse_empty()
            return

    def __get_photo(self, person_or_marriage):
        """ returns the first photo in the media list or None """
        media_list = person_or_marriage.get_media_list()
        for media_ref in media_list:
            media_handle = media_ref.get_reference_handle()
            media = self.database.get_media_from_handle(media_handle)
            mime_type = media.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                return media
        return None

    def __parse_photo(self, person_or_marriage):
        photo_f = GalleryFormat(self.database, self._in, self._locale)
        if person_or_marriage is None:
            return photo_f.parse_empty()
        photo = self.__get_photo(person_or_marriage)
        if photo:
            return photo_f.parse_format(photo)
        else:
            return photo_f.parse_empty()

    def parse_format(self):
        """Parse the $ variables. """
        if not self.is_a():
            return

        attrib_parse = AttributeParse(self._in)
        next_char = self._in.next
        self._in.step2()

        if next_char == "n":
            #Person's name
            return self.__parse_name(self.friend.person, attrib_parse)
        elif next_char == "s":
            #Souses name
            return self.__parse_name(self.friend.spouse, attrib_parse)

        elif next_char == "i":
            #Person's Id
            return self.__parse_id(self.friend.person)
        elif next_char == "j":
            #Marriage Id
            return self.__parse_id(self.friend.family)

        elif next_char == "b":
            #Person's Birth date
            if self.empty_item(self.friend.person):
                return
            return self.__parse_date(
                get_birth_or_fallback(self.friend.database, self.friend.person))
        elif next_char == "d":
            #Person's Death date
            if self.empty_item(self.friend.person):
                return
            return self.__parse_date(
                get_death_or_fallback(self.friend.database, self.friend.person))
        elif next_char == "m":
            #Marriage date
            if self.empty_item(self.friend.family):
                return
            return self.__parse_date(
                self.get_event_by_type(self.friend.family,
                                       EventType.MARRIAGE))
        elif next_char == "v":
            #Divorce date
            if self.empty_item(self.friend.family):
                return
            return self.__parse_date(
                self.get_event_by_type(self.friend.family,
                                       EventType.DIVORCE))
        elif next_char == "T":
            #Todays date
            date_f = DateFormat(self._in)
            from gramps.gen.lib.date import Today
            date = Today()
            if self.empty_item(date):
                return
            return date_f.parse_format(date)

        elif next_char == "B":
            #Person's birth place
            if self.empty_item(self.friend.person):
                return
            return self.__parse_place(
                get_birth_or_fallback(self.friend.database, self.friend.person))
        elif next_char == "D":
            #Person's death place
            if self.empty_item(self.friend.person):
                return
            return self.__parse_place(
                get_death_or_fallback(self.friend.database, self.friend.person))
        elif next_char == "M":
            #Marriage place
            if self.empty_item(self.friend.family):
                return
            return self.__parse_place(
                self.get_event_by_type(self.friend.family,
                                       EventType.MARRIAGE))
        elif next_char == "V":
            #Divorce place
            if self.empty_item(self.friend.family):
                return
            return self.__parse_place(
                self.get_event_by_type(self.friend.family,
                                       EventType.DIVORCE))

        elif next_char == "a":
            #Person's Atribute
            if self.empty_attribute(self.friend.person):
                return
            return attrib_parse.parse_format(
                self.friend.person.get_attribute_list())
        elif next_char == "u":
            #Marriage Atribute
            if self.empty_attribute(self.friend.family):
                return
            return attrib_parse.parse_format(
                self.friend.family.get_attribute_list())

        elif next_char == "e":
            #person event
            return self.__parse_event(self.friend.person, attrib_parse)
        elif next_char == "t":
            #family event
            return self.__parse_event(self.friend.family, attrib_parse)

        elif next_char == 'p':
            #photo for the person
            return self.__parse_photo(self.friend.person)
        elif next_char == 'P':
            #photo for the marriage
            return self.__parse_photo(self.friend.family)

        elif next_char == "G":
            gramps_format = GrampsFormat(self._in, self.database)
            return gramps_format.parse_format()


#------------------------------------------------------------------------
#
# SubstKeywords
#
#------------------------------------------------------------------------
class SubstKeywords:
    """Accepts a person/family with format lines and returns a new set of lines
    using variable substitution to make it.

    The individual variables are defined with the classes that look for them.

    Needed:
        Database object
        person_handle
            This will be the center person for the display
        family_handle
            this will specify the specific family/spouse to work with.
            If none given, then the first/preferred family/spouse is used
    """
    def __init__(self, database, locale, name_displayer,
                 person_handle, family_handle=None):
        """get the person and find the family/spouse to use for this display"""

        self.database = database
        self.family = None
        self.spouse = None
        self.line = None   # Consumable_string - set below
        self._locale = locale
        self._nd = name_displayer

        self.person = None
        if person_handle is not None:
            self.person = database.get_person_from_handle(person_handle)
        if self.person is None:
            return

        fam_hand_list = self.person.get_family_handle_list()
        if fam_hand_list:
            if family_handle in fam_hand_list:
                self.family = database.get_family_from_handle(family_handle)
            else:
                #Error.  fam_hand_list[0] below may give wrong marriage info.
                #only here because of OLD specifications.  Specs read:
                # * $S/%S
                #   Displays the name of the person's preferred ...
                # 'preferred' means FIRST.
                #The first might not be the correct marriage to display.
                #else: clause SHOULD be removed.
                self.family = database.get_family_from_handle(fam_hand_list[0])

            father_handle = self.family.get_father_handle()
            mother_handle = self.family.get_mother_handle()
            self.spouse = None
            if father_handle == person_handle:
                if mother_handle:
                    self.spouse = database.get_person_from_handle(mother_handle)
            else:
                if father_handle:
                    self.spouse = database.get_person_from_handle(father_handle)

    def __parse_line(self):
        """parse each line of text and return the new displayable line

        There are four things we can find here
            A {} group which will make/end as needed.
            A <> separator
            A $  variable - Handled separately
            or text
        """
        stack_var = []
        curr_var = VarString(TXT.text)

        #First we are going take care of all variables/groups
        #break down all {} (groups) and $ (vars) into either
        #(TXT.text, resulting_string) or (TXT.remove, '')
        variable = VariableParse(self, self.database, self.line,
                                 self._locale, self._nd)

        while self.line.this:
            if self.line.this == "{":
                #Start of a group
                #push what we have onto the stack
                stack_var.append(curr_var)
                #Setup
                curr_var = VarString()
                #step
                self.line.step()

            elif self.line.this == "}" and len(stack_var) > 0: #End of a group
                #add curr to what is on the (top) stack and pop into current
                #or pop the stack into current and add TXT.remove
                direction = curr_var.state
                if direction == TXT.display:
                    #add curr onto the top slot of the stack
                    stack_var[-1].extend(curr_var)

                #pop what we have on the stack
                curr_var = stack_var.pop()

                if direction == TXT.remove:
                    #add remove que
                    curr_var.add_remove()
                #step
                self.line.step()

            elif variable.is_a():  # $  (variables)
                rtrn = variable.parse_format()
                if rtrn is None:
                    curr_var.add_remove()
                elif isinstance(rtrn, VarString):
                    curr_var.extend(rtrn)
                else:
                    curr_var.add_variable(rtrn)

            elif self.line.this == "<":  # separator
                self.line.step()
                curr_var.add_separator(self.line.text_to_next(">"))

            else:  #regular text
                curr_var.add_text(self.line.parse_format())

        #the stack is for groups/subgroup and may contain items
        #if the user does not close his/her {}
        #squash down the stack
        while stack_var:
            direction = curr_var.state
            if direction == TXT.display:
                #add curr onto the top slot of the stack
                stack_var[-1].extend(curr_var)

            #pop what we have on the stack
            curr_var = stack_var.pop()

            if direction == TXT.remove:
                #add remove que
                curr_var.add_remove()
            #step
            self.line.step()

        #return what we have
        return curr_var.get_final()


    def __main_level(self):
        #Check only if the user wants to not display the line if TXT.remove
        remove_line_tag = False
        if self.line.this == "-":
            remove_line_tag = True
            self.line.step()

        state, line = self.__parse_line()

        if state is TXT.remove and remove_line_tag:
            return None
        return line

    def replace_and_clean(self, lines):
        """
        return a new array of lines with all of the substitutions done
        """
        new = []
        for this_line in lines:
            if this_line == "":
                new.append(this_line)
                continue
            #print "- ", this_line
            self.line = ConsumableString(this_line)
            new_line = self.__main_level()
            #print "+ ", new_line
            if new_line is not None:
                new.append(new_line)

        if new == []:
            new = [""]
        return new


#Acts 20:35 (New International Version)
#In everything I did, I showed you that by this kind of hard work
#we must help the weak, remembering the words the Lord Jesus himself
#said: 'It is more blessed to give than to receive.'


if __name__ == '__main__':
#-------------------------------------------------------------------------
#
# For Testing everything except VariableParse, SubstKeywords and EventFormat
# apply it as a script:
#
#     ==> in command line do "PYTHONPATH=??? python libsubstkeyword.py"
#
# You will need to put in your own path to the src directory
#
#-------------------------------------------------------------------------
    # pylint: disable=C0103

    def combinations(c, r):
        # combinations('ABCD', 2) --> AB AC AD BC BD CD
        # combinations(range(4), 3) --> 012 013 023 123
        pool = tuple(range(c))
        n = len(pool)
        if r > n:
            return
        indices = list(range(r))
        yield tuple(pool[i] for i in indices)
        while True:
            for i in reversed(list(range(r))):
                if indices[i] != i + n - r:
                    break
            else:
                return
            indices[i] += 1
            for j in range(i+1, r):
                indices[j] = indices[j-1] + 1
            yield tuple(pool[i] for i in indices)

    def main_level_test(_in, testing_class, testing_what):
        """This is a mini def __main_level(self):
        """
        main = _in
        sepa = SeparatorParse(_in)
        test = testing_class(_in)

        while _in.this:
            if main.is_a():
                main.parse_format(_in)
            elif sepa.is_a():
                sepa.parse_format(main)
            elif _in.this == "$":
                _in.step()
                main.add_variable(
                    test.parse_format(testing_what))
            else:
                _in.parse_format(main)

        main.combine_all()

        state, line = main.get_string()
        if state is TXT.remove:
            return None
        else:
            return line


    from gramps.gen.lib.date import Date
    y_or_n = ()
    date_to_test = Date()

    def date_set():
        date_to_test.set_yr_mon_day(
            1970 if 0 in y_or_n else 0,
            9 if 1 in y_or_n else 0,
            3 if 2 in y_or_n else 0
            )
        #print date_to_test

    line_in = "<Z>$(yyy) <a>$(<Z>Mm)<b>$(mm){<c>$(d)}{<d>$(yyyy)<e>}<f>$(yy)"
    consume_str = ConsumableString(line_in)

    print(line_in)
    print("#None are known")
    tmp = main_level_test(consume_str, DateFormat, date_to_test)
    print(tmp)
    print("Good" if tmp == " " else "!! bad !!")


    print()
    print()
    print("#One is known")
    answer = []
    for y_or_n in combinations(3, 1):
        date_set()
        consume_str = ConsumableString(line_in)
        tmp = main_level_test(consume_str, DateFormat, date_to_test)
        print(tmp)
        answer.append(tmp)
    print("Good" if answer == [
        "1970 d1970f70",
        " a99b09",
        " c3"
        ] else "!! bad !!")


    print()
    print()
    print("#Two are known")
    answer = []
    for y_or_n in combinations(3, 2):
        date_set()
        consume_str = ConsumableString(line_in)
        tmp = main_level_test(consume_str, DateFormat, date_to_test)
        print(tmp)
        answer.append(tmp)
    print("Good" if answer == [
        "1970 a99b09d1970f70",
        "1970 c3d1970f70",
        " a99b09c3"
        ] else "!! bad !!")


    print()
    print()
    print("#All are known")
    answer = []
    y_or_n = (0, 1, 2)
    date_set()
    consume_str = ConsumableString(line_in)
    tmp = main_level_test(consume_str, DateFormat, date_to_test)
    print(tmp)
    answer.append(tmp)
    print("Good" if answer == [
        "1970 a99b09c3d1970f70"
        ] else "!! bad !!")

    import sys
    sys.exit()
    print()
    print()
    print("=============")
    print("=============")

    from gramps.gen.lib.name import Name
    y_or_n = ()
    name_to_test = Name()

    def name_set():
        #code = "tfcnxslg"
        name_to_test.set_call_name("Bob" if 0 in y_or_n else "")
        name_to_test.set_title("Dr." if 1 in y_or_n else "")
        name_to_test.set_first_name("Billy" if 2 in y_or_n else "")
        name_to_test.set_nick_name("Buck" if 3 in y_or_n else "")
        name_to_test.set_suffix("IV" if 4 in y_or_n else "")
        #now can we put something in for the last name?
        name_to_test.set_family_nick_name("The Clubs" if 5 in y_or_n else "")

    line_in = "{$(c)$(t)<1>{<2>$(f)}{<3>$(n){<0> "
    line_in = line_in + "<0>}<4>$(x)}$(s)<5>$(l)<6>$(g)<0>"
    consume_str = ConsumableString(line_in)

    print()
    print()
    print(line_in)
    print("#None are known")
    tmp = main_level_test(consume_str, NameFormat, name_to_test)
    print(tmp)
    print("Good" if tmp is None else "!! bad !!")


    print()
    print()
    print("#Two are known")
    answer = []
    for y_or_n in combinations(6, 2):
        name_set()
        consume_str = ConsumableString(line_in)
        tmp = main_level_test(consume_str, NameFormat, name_to_test)
        print(tmp)
        answer.append(tmp)
    print("Good" if answer == [
        "BobDr.4Bob",
        "Bob2Billy4Bob",
        "Bob3Buck4Bob",
        "Bob4BobIV",
        "Bob4BobThe Clubs",
        "Dr.2Billy4Billy",
        "Dr.3Buck",
        "Dr.1IV",
        "Dr.6The Clubs",
        "Billy3Buck4Billy",
        "Billy4BillyIV",
        "Billy4BillyThe Clubs",
        "BuckIV",
        "BuckThe Clubs",
        "IV6The Clubs"
        ] else "!! bad !!")


    print()
    print()
    print("#All are known")
    y_or_n = (0, 1, 2, 3, 4, 5)
    name_set()
    consume_str = ConsumableString(line_in)
    answer = main_level_test(consume_str, NameFormat, name_to_test)
    print(answer)
    print("Good" if answer == "BobDr.2Billy3Buck4BobIV6The Clubs"
          else "!! bad !!")


    print()
    print()
    print("=============")
    print("=============")

    from gramps.gen.lib.place import Place
    y_or_n = ()
    place_to_test = Place()

    def place_set():
        #code = "elcuspnitxy"
        main_loc = place_to_test.get_main_location()
        main_loc.set_street(
            "Lost River Ave." if 0 in y_or_n else ""
        )
        main_loc.set_locality(
            "Second district" if 1 in y_or_n else ""
        )
        main_loc.set_city(
            "Arco" if 2 in y_or_n else ""
        )
        main_loc.set_county(
            "Butte" if 3 in y_or_n else ""
        )
        main_loc.set_state(
            "Idaho" if 4 in y_or_n else ""
        )
        main_loc.set_postal_code(
            "83213" if 5 in y_or_n else ""
        )
        main_loc.set_country(
            "USA" if 6 in y_or_n else ""
        )
        main_loc.set_parish(
            "St Anns" if 7 in y_or_n else ""
        )
        place_to_test.set_title(
            "Atomic City" if 8 in y_or_n else ""
        )
        place_to_test.set_longitude(
            "N43H38'5\"N" if 9 in y_or_n else ""
        )
        place_to_test.set_latitude(
            "W113H18'5\"W" if 10 in y_or_n else ""
        )

    #code = "txy"
    line_in = "$(e)<1>{<2>$(l) <3> $(c)<4><0><5>{$(s)<6>$(p)<7>" + \
              "{<1>$(n)<2>}<3>$(i<0>)<4>}<5>$(t)<6>$(x)<7>}<8>$(y)"
    consume_str = ConsumableString(line_in)

    print()
    print()
    print(line_in)
    print("#None are known")
    tmp = main_level_test(consume_str, PlaceFormat, place_to_test)
    print(tmp)
    print("Good" if tmp == "" else "!! bad !!")


    print()
    print()
    print("#Three are known (string lengths only)")
    answer = []
    for y_or_n in combinations(11, 4):
        place_set()
        consume_str = ConsumableString(line_in)
        tmp = main_level_test(consume_str, PlaceFormat, place_to_test)
        #print tmp
        answer.append(len(tmp))
    print(answer)
    print("Good" if answer == [
        38, 44, 44, 42, 46, 50, 49, 50, 40, 40, 38, 42,
        46, 45, 46, 46, 44, 48, 52, 51, 52, 44, 48, 52, 51, 52, 46, 50, 49, 50,
        54, 53, 54, 57, 58, 57, 28, 28, 26, 30, 34, 33, 34, 34, 32, 36, 40, 39,
        40, 32, 36, 40, 39, 40, 34, 38, 37, 38, 42, 41, 42, 45, 46, 45, 30, 28,
        32, 36, 35, 36, 28, 32, 36, 35, 36, 30, 34, 33, 34, 38, 37, 38, 41, 42,
        41, 34, 38, 42, 41, 42, 36, 40, 39, 40, 44, 43, 44, 47, 48, 47, 36, 40,
        39, 40, 44, 43, 44, 47, 48, 47, 42, 41, 42, 45, 46, 45, 49, 50, 49, 53,
        28, 28, 26, 30, 34, 33, 34, 34, 32, 36, 40, 39, 40, 32, 36, 40, 39, 40,
        34, 38, 37, 38, 42, 41, 42, 45, 46, 45, 30, 28, 32, 36, 35, 36, 28, 32,
        36, 35, 36, 30, 34, 33, 34, 38, 37, 38, 41, 42, 41, 34, 38, 42, 41, 42,
        36, 40, 39, 40, 44, 43, 44, 47, 48, 47, 36, 40, 39, 40, 44, 43, 44, 47,
        48, 47, 42, 41, 42, 45, 46, 45, 49, 50, 49, 53, 19, 17, 21, 25, 24, 25,
        17, 21, 25, 24, 25, 19, 23, 22, 23, 27, 26, 27, 30, 31, 30, 23, 27, 31,
        30, 31, 25, 29, 28, 29, 33, 32, 33, 36, 37, 36, 25, 29, 28, 29, 33, 32,
        33, 36, 37, 36, 31, 30, 31, 34, 35, 34, 38, 39, 38, 42, 19, 23, 27, 26,
        27, 21, 25, 24, 25, 29, 28, 29, 32, 33, 32, 21, 25, 24, 25, 29, 28, 29,
        32, 33, 32, 27, 26, 27, 30, 31, 30, 34, 35, 34, 38, 27, 31, 30, 31, 35,
        34, 35, 38, 39, 38, 33, 32, 33, 36, 37, 36, 40, 41, 40, 44, 33, 32, 33,
        36, 37, 36, 40, 41, 40, 44, 38, 39, 38, 42, 46] else "!! bad !!")

