#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001      David R. Hampton
# Copyright (C) 2001-2006 Donald N. Allingham
# Copyright (C) 2007      Brian G. Matherly
# Copyright (C) 2010      Jakim Friant
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

# gen.plug.report.__init__
#

"Report Generation Framework"

from ._constants import *
from ._reportbase import Report

from ._bibliography import Bibliography, Citation

from ._options import MenuReportOptions, ReportOptions, DocOptions

from ._book import BookList, Book, BookItem, append_styles
