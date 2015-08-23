#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006 Donald N. Allingham
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
This package implements unittest support for GRAMPS

It includes a test-running program regrtest.py,
 and various test support utility modules
  (first one created being test_util.py)

Also includes tests for code in the parent (src) directory
and other tests that may be considered top-level tests

Note: tests for utility code in this directory would be in a
subdirectory also named test by convention for gramps testing.

Note: test subdirectories do not normally need to have a
package-enabling module __init__.py, but this one (src/test) does
because it contains utilities used by other test modules.
Thus, this package would allow test code like
  from test import test_util

"""

# This file does not presently contain any code.

#===eof===
