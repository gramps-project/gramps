#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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
Package providing filtering framework for Gramps.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ._genericfilter import GenericFilter
from ..errors import FilterError

#-------------------------------------------------------------------------
#
# ParamFilter
#
#-------------------------------------------------------------------------
class ParamFilter(GenericFilter):

    def __init__(self, source=None):
        GenericFilter.__init__(self, source)
        self.need_param = 1
        self.param_list = []

    def set_parameter(self, param):
        self.param_list = [param]

    def apply(self, db, id_list=None, user=None):
        for rule in self.flist:
            #rule.set_list(self.param_list)
            #
            # The above breaks filters with more than one param
            # Need to change existing params one by one to keep
            # the correct number of arguments
            new_list = rule.list[:]
            for ix in range(len(self.param_list)):
                new_list[ix] = self.param_list[ix]
            rule.set_list(new_list)
        for rule in self.flist:
            if rule.nrprepare > 0:
                raise FilterError('Custom filters can not twice be used' \
                                   ' in a parameter filter')
            rule.requestprepare(db, user)
        result = GenericFilter.apply(self, db, id_list)
        for rule in self.flist:
            rule.requestreset()
        return result
