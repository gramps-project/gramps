#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007  Donald N. Allingham
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

"""
Class handling language-specific displaying of names.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import re

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.lib import Name
from Errors import NameDisplayError

try:
    import Config
    WITH_GRAMPS_CONFIG=True
except ImportError:
    WITH_GRAMPS_CONFIG=False
    

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_FIRSTNAME = 4
_SURNAME   = 5
_SUFFIX    = 6
_TITLE     = 7
_TYPE      = 8
_PREFIX    = 9
_PATRONYM  = 10
_GROUP     = 11
_SORT      = 12
_DISPLAY   = 13
_CALL      = 14

_ACT = True
_INA = False

_F_NAME = 0  # name of the format
_F_FMT = 1   # the format string
_F_ACT = 2   # if the format is active
_F_FN = 3    # name format function
_F_RAWFN = 4 # name format raw function

#-------------------------------------------------------------------------
#
# Local functions
#
#-------------------------------------------------------------------------
# Because of occurring in an exec(), this couldn't be in a lambda:
def _make_cmp(a,b): return -cmp(a[1], b[1])

#-------------------------------------------------------------------------
#
# NameDisplay class
#
#-------------------------------------------------------------------------
class NameDisplay:
    """
    Base class for displaying of Name instances.
    """

    format_funcs = {}
    raw_format_funcs = {}

    # FIXME: Is this used anywhere? I cannot see that it is.
    sort_field = (Name.get_surname, Name.get_surname,
                  Name.get_first_name, Name.get_patronymic,
                  Name.get_first_name)

    STANDARD_FORMATS = [
        (Name.DEF,_("Default format (defined by GRAMPS preferences)"),'',_ACT),
        (Name.LNFN,_("Family name, Given name Patronymic"),'%p %l, %f %y %s',_ACT),
        (Name.FNLN,_("Given name Family name"),'%f %y %p %l %s',_ACT),
        (Name.PTFN,_("Patronymic, Given name"),'%p %y, %s %f',_ACT),
        (Name.FN,_("Given name"),'%f',_ACT)
    ]
    
    def __init__(self):
        global WITH_GRAMP_CONFIG
        self.name_formats = {}
        self.set_name_format(self.STANDARD_FORMATS)
        
        if WITH_GRAMPS_CONFIG:
            self.default_format = Config.get(Config.NAME_FORMAT)
            if self.default_format == 0:
                self.default_format = Name.LNFN
                Config.set(Config.NAME_FORMAT,self.default_format)
        else:
            self.default_format = 1
            
        self.set_default_format(self.default_format)

    def _format_fn(self,fmt_str):
        return lambda x: self.format_str(x,fmt_str)
    
    def _format_raw_fn(self,fmt_str):
        return lambda x: self.format_str_raw(x,fmt_str)
    
    def _raw_lnfn(self,raw_data):
        result =  "%s %s, %s %s %s" % (raw_data[_PREFIX],
                                       raw_data[_SURNAME],
                                       raw_data[_FIRSTNAME],
                                       raw_data[_PATRONYM],
                                       raw_data[_SUFFIX])
        return ' '.join(result.split())

    def _raw_fnln(self,raw_data):
        result = "%s %s %s %s %s" % (raw_data[_FIRSTNAME],
                                     raw_data[_PATRONYM],
                                     raw_data[_PREFIX],
                                     raw_data[_SURNAME],
                                     raw_data[_SUFFIX])
        return ' '.join(result.split())

    def _raw_ptfn(self,raw_data):
        result = "%s %s, %s %s" % (raw_data[_PREFIX],
                                   raw_data[_PATRONYM],
                                   raw_data[_SUFFIX],
                                   raw_data[_FIRSTNAME])
        return ' '.join(result.split())

    def _raw_fn(self,raw_data):
        result = raw_data[_FIRSTNAME]        
        return ' '.join(result.split())

    def set_name_format(self,formats):
        raw_func_dict = {
            Name.LNFN : self._raw_lnfn,
            Name.FNLN : self._raw_fnln,
            Name.PTFN : self._raw_ptfn,
            Name.FN   : self._raw_fn,
            }

        for (num,name,fmt_str,act) in formats:
            func = self._format_fn(fmt_str)
            func_raw = raw_func_dict.get(num)
            if func_raw == None:
                func_raw = self._format_raw_fn(fmt_str)
            self.name_formats[num] = (name,fmt_str,act,func,func_raw)

    def add_name_format(self,name,fmt_str):
        num = -1
        while num in self.name_formats:
            num -= 1
        self.set_name_format([(num,name,fmt_str,_ACT)])
        return num
    
    def edit_name_format(self,num,name,fmt_str):
        self.set_name_format([(num,name,fmt_str,_ACT)])
        if self.default_format == num:
            self.set_default_format(num)
        
    def del_name_format(self,num):
        try:
            del self.name_formats[num]
        except:
            pass
        
    def set_default_format(self,num):
        if num not in self.name_formats:
            num = Name.LNFN
            
        self.default_format = num
        
        self.name_formats[Name.DEF] = (self.name_formats[Name.DEF][_F_NAME],
                                       self.name_formats[Name.DEF][_F_FMT],
                                       self.name_formats[Name.DEF][_F_ACT],
                                       self.name_formats[num][_F_FN],
                                       self.name_formats[num][_F_RAWFN])
    
    def get_default_format(self):
        return self.default_format

    def set_format_inactive(self,num):
        try:
            self.name_formats[num] = (self.name_formats[num][_F_NAME],
                                      self.name_formats[num][_F_FMT],
                                      _INA,
                                      self.name_formats[num][_F_FN],
                                      self.name_formats[num][_F_RAWFN])
        except:
            pass
        
    def get_name_format(self,also_default=False,
                        only_custom=False,
                        only_active=True):
        """
        Get a list of tuples (num,name,fmt_str,act)
        """
        the_list = []

        keys = self.name_formats.keys()
        keys.sort(self._sort_name_format)
        
        for num in keys:
            if ((also_default or num) and
                (not only_custom or (num < 0)) and
                (not only_active or self.name_formats[num][_F_ACT])):
                the_list.append((num,) + self.name_formats[num][_F_NAME:_F_FN])

        return the_list

    def _sort_name_format(self,x,y):
        if x<0:
            if y<0: return x+y
            else: return -x+y
        else:
            if y<0: return -x+y
            else: return x-y
        
    def _is_format_valid(self,num):
        try:
            if not self.name_formats[num][_F_ACT]:
                num = 0
        except:
            num = 0    
        return num

    #-------------------------------------------------------------------------


    def _gen_raw_func(self, format_str):
        """The job of building the name from a format string is rather
        expensive and it is called lots and lots of times. So it is worth
        going to some length to optimise it as much as possible. 

        This method constructs a new function that is specifically written 
        to format a name given a particualar format string. This is worthwhile
        because the format string itself rarely changes, so by caching the new
        function and calling it directly when asked to format a name to the
        same format string again we can be as quick as possible.

        The new function is of the form:

        def fn(raw_data):
            return "%s %s %s %s %s" % (raw_data[_TITLE],
                   raw_data[_FIRSTNAME],
                   raw_data[_PREFIX],
                   raw_data[_SURNAME],
                   raw_data[_SUFFIX])

        """

        # we need the names of each of the variables or methods that are
        # called to fill in each format flag.
        # Dictionary is "code": ("expression", "keyword", "i18n-keyword")
        d = {"t": ("raw_data[_TITLE]",     "title",      _("title")),
             "f": ("raw_data[_FIRSTNAME]", "given",      _("given")),
             "p": ("raw_data[_PREFIX]",    "prefix",     _("prefix")),
             "l": ("raw_data[_SURNAME]",   "surname",    _("surname")),
             "s": ("raw_data[_SUFFIX]",    "suffix",     _("suffix")),
             "y": ("raw_data[_PATRONYM]",  "patronymic", _("patronymic")),
             "c": ("raw_data[_CALL]",      "call",       _("call")),
             "x": ("(raw_data[_CALL] or raw_data[_FIRSTNAME].split(' ')[0])",
                   "common",
                   _("common")),
             "i": ("''.join([word[0] +'.' for word in ('. ' +" +
                   " raw_data[_FIRSTNAME]).split()][1:])",
                   "initials",
                   _("initials"))
             }
        args = "raw_data"
        return self._make_fn(format_str, d, args)

    def _gen_cooked_func(self, format_str):
        """The job of building the name from a format string is rather
        expensive and it is called lots and lots of times. So it is worth
        going to some length to optimise it as much as possible. 

        This method constructs a new function that is specifically written 
        to format a name given a particualar format string. This is worthwhile
        because the format string itself rarely changes, so by caching the new
        function and calling it directly when asked to format a name to the
        same format string again we can be as quick as possible.

        The new function is of the form:

        def fn(first,surname,prefix,suffix,patronymic,title,call,):
            return "%s %s %s %s %s" % (first,surname,prefix,suffix,patronymic)

        """

        # we need the names of each of the variables or methods that are
        # called to fill in each format flag.
        # Dictionary is "code": ("expression", "keyword", "i18n-keyword")
        d = {"t": ("title",      "title",      _("title")),
             "f": ("first",      "given",      _("given")),
             "p": ("prefix",     "prefix",     _("prefix")),
             "l": ("surname",    "surname",    _("surname")),
             "s": ("suffix",     "suffix",     _("suffix")),
             "y": ("patronymic", "patronymic", _("patronymic")),
             "c": ("call",       "call",       _("call")),
             "x": ("(call or first.split(' ')[0])", "common", _("common")),
             "i": ("''.join([word[0] +'.' for word in ('. ' + first).split()][1:])",
                   "initials", _("initials"))
             }
        args = "first,surname,prefix,suffix,patronymic,title,call"
        return self._make_fn(format_str, d, args)

    def _make_fn(self, format_str, d, args):
        """
        Creates the name display function and handles dependent
        punctuation.
        """
        # First, go through and do internationalization-based
        # key-word replacement. Just replace ikeywords with
        # %codes (ie, replace "irstnamefay" with "%f", and
        # "IRSTNAMEFAY" for %F)
        d_keys = [(code, d[code][2]) for code in d.keys()]
        d_keys.sort(_make_cmp) # reverse sort by ikeyword
        for (code, ikeyword) in d_keys:
            exp, keyword, ikeyword = d[code]
            format_str = format_str.replace(ikeyword,"%"+ code)
            format_str = format_str.replace(ikeyword.title(),"%"+ code)
            format_str = format_str.replace(ikeyword.upper(),"%"+ code.upper())
        # Next, go through and do key-word replacement.
        # Just replace keywords with
        # %codes (ie, replace "firstname" with "%f", and
        # "FIRSTNAME" for %F)
        d_keys = [(code, d[code][1]) for code in d.keys()]
        d_keys.sort(_make_cmp) # reverse sort by keyword
        for (code, keyword) in d_keys:
            exp, keyword, ikeyword = d[code]
            format_str = format_str.replace(keyword,"%"+ code)
            format_str = format_str.replace(keyword.title(),"%"+ code)
            format_str = format_str.replace(keyword.upper(),"%"+ code.upper())
        # Get lower and upper versions of codes:
        codes = d.keys() + [c.upper() for c in d.keys()]
        # Next, list out the matching patterns:
        # If it starts with "!" however, treat the punctuation verbatim:
        if len(format_str) > 0 and format_str[0] == "!":
            format_str = format_str[1:]
            patterns = ["%(" + ("|".join(codes)) + ")",          # %s
                        ]
        else:
            patterns = [",\W*\(%(" + ("|".join(codes)) + ")\)",  # ,\W*(%s)
                        ",\W*%(" + ("|".join(codes)) + ")",      # ,\W*%s
                        "\(%(" + ("|".join(codes)) + ")\)",      # (%s)
                        "%(" + ("|".join(codes)) + ")",          # %s
                        ]

        new_fmt = format_str

        # replace the specific format string flags with a 
        # flag that works in standard python format strings.
        new_fmt = re.sub("|".join(patterns), "%s", new_fmt)

        # find each format flag in the original format string
        # for each one we find the variable name that is needed to 
        # replace it and add this to a list. This list will be used
        # generate the replacement tuple.

        # This compiled pattern should match all of the format codes.
        pat = re.compile("|".join(patterns))
        param = ()
        mat = pat.search(format_str)
        while mat:
            match_pattern = mat.group(0) # the matching pattern
            # prefix, code, suffix:
            p, code, s = re.split("%(.)", match_pattern)
            field = d[code.lower()][0]
            if code.isupper():
                field += ".upper()"
            if p == '' and s == '':
                param = param + (field,)
            else:
                param = param + ("ifNotEmpty(%s,'%s','%s')" % (field,p,s), )
            mat = pat.search(format_str,mat.end())
        s = """
def fn(%s):
    def ifNotEmpty(str,p,s):
        if str == '':
            return ''
        else:
            return p + str + s
    return "%s" %% (%s)""" % (args, new_fmt, ",".join(param))

        exec(s)

        return fn

    def format_str(self,name,format_str):
        return self._format_str_base(name.first_name,name.surname,name.prefix,
                                     name.suffix,name.patronymic,name.title,
                                     name.call,format_str)

    def format_str_raw(self,raw_data,format_str):
        """
        Format a name from the raw name list. To make this as fast as possible
        this uses _gen_raw_func to generate a new method for each new format_string.
        
        Is does not call _format_str_base because it would introduce an extra 
        method call and we need all the speed we can squeeze out of this.
        """
        func = self.__class__.raw_format_funcs.get(format_str)
        if func == None:
            func = self._gen_raw_func(format_str)
            self.__class__.raw_format_funcs[format_str] = func

        s = func(raw_data)
        return ' '.join(s.split())


    def _format_str_base(self,first,surname,prefix,suffix,patronymic,
                         title,call,format_str):
        """
        Generates name from a format string.

        The following substitutions are made:
            %t -> title
            %f -> given name (first name)
            %p -> prefix
            %s -> suffix
            %l -> family name (last name, surname)
            %y -> patronymic
            %c -> call name
        The capital letters are substituted for capitalized name components.
        The %% is substituted with the single % character.
        All the other characters in the fmt_str are unaffected.
        
        """

        func = self.__class__.format_funcs.get(format_str)
        if func == None:
            func = self._gen_cooked_func(format_str)
            self.__class__.format_funcs[format_str] = func

        try:
            s = func(first,surname,prefix,suffix,patronymic,title,call)
        except (ValueError,TypeError,):
            raise NameDisplayError, "Incomplete format string"

        return ' '.join(s.split())
    
    #-------------------------------------------------------------------------

    def sort_string(self,name):
        return u"%-25s%-30s%s" % (name.surname,name.first_name,name.suffix)

    def sorted(self,person):
        """
        Returns a text string representing the L{gen.lib.Person} instance's
        L{Name} in a manner that should be used for displaying a sorted
        name.

        @param person: L{gen.lib.Person} instance that contains the
        L{Name} that is to be displayed. The primary name is used for
        the display.
        @type person: L{gen.lib.Person}
        @returns: Returns the L{gen.lib.Person} instance's name
        @rtype: str
        """
        name = person.get_primary_name()
        return self.sorted_name(name)

    def sorted_name(self,name):
        """
        Returns a text string representing the L{Name} instance
        in a manner that should be used for displaying a sorted
        name.

        @param name: L{Name} instance that is to be displayed.
        @type name: L{Name}
        @returns: Returns the L{Name} string representation
        @rtype: str
        """
        num = self._is_format_valid(name.sort_as)
        return self.name_formats[num][_F_FN](name)

    def raw_sorted_name(self,raw_data):
        """
        Returns a text string representing the L{Name} instance
        in a manner that should be used for displaying a sorted
        name.

        @param name: L{Name} instance that is to be displayed.
        @type name: L{Name}
        @returns: Returns the L{Name} string representation
        @rtype: str
        """
        num = self._is_format_valid(raw_data[_SORT])
        return self.name_formats[num][_F_RAWFN](raw_data)

    def display(self,person):
        """
        Returns a text string representing the L{gen.lib.Person} instance's
        L{Name} in a manner that should be used for normal displaying.

        @param person: L{gen.lib.Person} instance that contains the
        L{Name} that is to be displayed. The primary name is used for
        the display.
        @type person: L{gen.lib.Person}
        @returns: Returns the L{gen.lib.Person} instance's name
        @rtype: str
        """
        name = person.get_primary_name()
        return self.display_name(name)

    def display_formal(self,person):
        """
        Returns a text string representing the L{gen.lib.Person} instance's
        L{Name} in a manner that should be used for normal displaying.

        @param person: L{gen.lib.Person} instance that contains the
        L{Name} that is to be displayed. The primary name is used for
        the display.
        @type person: L{gen.lib.Person}
        @returns: Returns the L{gen.lib.Person} instance's name
        @rtype: str
        """
        # FIXME: At this time, this is just duplicating display() method
        name = person.get_primary_name()
        return self.display_name(name)

    def display_name(self,name):
        """
        Returns a text string representing the L{Name} instance
        in a manner that should be used for normal displaying.

        @param name: L{Name} instance that is to be displayed.
        @type name: L{Name}
        @returns: Returns the L{Name} string representation
        @rtype: str
        """
        if name == None:
            return ""

        num = self._is_format_valid(name.display_as)
        return self.name_formats[num][_F_FN](name)

    def display_given(self,person):
        name = person.get_primary_name()
        return self.format_str(person.get_primary_name(),'%f %y')

    def name_grouping(self,db,person):
        return self.name_grouping_name(db,person.primary_name)

    def name_grouping_name(self,db,pn):
        if pn.group_as:
            return pn.group_as
        sv = pn.sort_as
        if sv == Name.LNFN or sv == Name.DEF:
            return db.get_name_group_mapping(pn.surname)
        elif sv == Name.PTFN:
            return db.get_name_group_mapping(pn.patronymic)
        else:
            return db.get_name_group_mapping(pn.first_name)

    def name_grouping_data(self, db, pn):
        if pn[_GROUP]:
            return pn[_GROUP]
        sv = pn[_SORT]
        if sv == Name.LNFN or sv == Name.DEF:
            return db.get_name_group_mapping(pn[_SURNAME])
        elif sv == Name.PTFN:
            return db.get_name_group_mapping(pn[_PATRONYM])
        else:
            return db.get_name_group_mapping(pn[_FIRSTNAME])

displayer = NameDisplay()
