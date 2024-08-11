#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2007  Donald N. Allingham
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
Provide Error objects
"""


class FilterError(Exception):
    """Error used to report Filter errors"""

    def __init__(self, value, value2=""):
        Exception.__init__(self)
        self.value = value
        self.value2 = value2

    def __str__(self):
        "Return string representation"
        return self.value

    def messages(self):
        "Return the messages"
        return (self.value, self.value2)


class DateError(Exception):
    """Error used to report Date errors

    Might have a .date attribute holding an invalid Date object
    that triggered the error.
    """

    def __init__(self, value=""):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        "Return string representation"
        return self.value


class DatabaseError(Exception):
    """Error used to report database errors"""

    def __init__(self, value=""):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        "Return string representation"
        return self.value


class ReportError(Exception):
    """Error used to report Report errors."""

    def __init__(self, value, value2=""):
        Exception.__init__(self)
        self.value = value
        self.value2 = value2

    def __str__(self):
        "Return string representation"
        return self.value

    def messages(self):
        "Return the messages"
        return (self.value, self.value2)


class GedcomError(Exception):
    """Error used to report GEDCOM errors"""

    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        "Return string representation"
        return self.value


class GrampsImportError(Exception):
    """Error used to report mistakes during import of files into Gramps"""

    def __init__(self, value, value2=""):
        Exception.__init__(self)
        self.value = value
        self.value2 = value2

    def __str__(self):
        "Return string representation"
        return self.value

    def messages(self):
        "Return the messages"
        return (self.value, self.value2)


class PluginError(Exception):
    """Error used to report plugin errors"""

    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        "Return string representation"
        return self.value


class HandleError(Exception):
    """Error used to report wrong database handle errors"""

    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        "Return string representation"
        return self.value


class WindowActiveError(Exception):
    """Error used to report that the request window is already displayed."""

    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        "Return string representation"
        return self.value


class UnavailableError(Exception):
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        "Return string representation"
        return self.value


class MaskError(Exception):
    pass


class ValidationError(Exception):
    pass


class DbError(Exception):
    """Error used to report BerkeleyDB errors."""

    def __init__(self, value):
        Exception.__init__(self)
        try:
            (errnum, errmsg) = value
            self.value = errmsg
        except:
            self.value = value

    def __str__(self):
        "Return string representation"
        return self.value


class MergeError(Exception):
    """Error used to report merge errors"""

    def __init__(self, value=""):
        Exception.__init__(self)
        self.value = value

    def __str__(self):
        "Return string representation"
        return self.value
