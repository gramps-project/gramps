#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001  David R. Hampton
# Copyright (C) 2001-2006  Donald N. Allingham
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

"Report Generation Framework"

__author__ =  "David R. Hampton, Donald N. Allingham"
__version__ = "$Revision$"

from _Constants import *

from _Report import Report

from _ReportDialog import report
from _CommandLineReport import cl_report
from _DrawReportDialog import DrawReportDialog
from _TextReportDialog import TextReportDialog

from _ReportOptions import ReportOptions
import _ReportUtils as ReportUtils

from _PrintTools import run_print_dialog
