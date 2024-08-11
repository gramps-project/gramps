#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001      David R. Hampton
# Copyright (C) 2001-2006 Donald N. Allingham
# Copyright (C) 2007      Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
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
#

"Quick Report Framework"

from ._quickreports import (
    create_web_connect_menu,
    create_quickreport_menu,
    get_quick_report_list,
    run_quick_report_by_name,
    run_quick_report_by_name_direct,
    run_report,
)
from ._quicktable import QuickTable
from ._textbufdoc import TextBufDoc
