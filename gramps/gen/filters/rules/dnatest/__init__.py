#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Ian Davis
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Package providing filter rules for DNA tests.
"""

from ._regexpidof import RegExpIdOf
from ._hastag import HasTag
from ._hasdnatest import HasDNATest
from ._hasprovider import HasProvider
from ._hastesttype import HasTestType
from ._isunidentified import IsUnidentified

editor_rule_list = []
