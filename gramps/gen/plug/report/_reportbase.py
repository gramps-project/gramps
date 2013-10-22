#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001  David R. Hampton
# Copyright (C) 2001-2006  Donald N. Allingham
# Copyright (C) 2007       Brian G. Matherly
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

#-------------------------------------------------------------------------
#
# Report
#
#-------------------------------------------------------------------------
from gramps.gen.utils.grampslocale import GrampsLocale

class Report(object):
    """
    The Report base class.  This is a base class for generating
    customized reports.  It cannot be used as is, but it can be easily
    sub-classed to create a functional report generator.
    """

    def __init__(self, database, options_class, user):
        self.database = database
        self.options_class = options_class

        self.doc = options_class.get_document()

        creator = database.get_researcher().get_name()
        self.doc.set_creator(creator)

        output = options_class.get_output()
        if output:
            self.standalone = True
            self.doc.open(options_class.get_output())
        else:
            self.standalone = False

    def begin_report(self):
        pass

    def set_locale(self, language):
        """
        Set the translator to one selected with
        stdoptions.add_localization_option().
        """
        if language == GrampsLocale.DEFAULT_TRANSLATION_STR:
            language = None
        locale = GrampsLocale(lang=language)
        self._ = locale.translation.gettext
        self._get_date = locale.get_date
        self._get_type = locale.get_type
        self._dd = locale.date_displayer
        return locale

    def write_report(self):
        pass

    def end_report(self):
        if self.standalone:
            self.doc.close()

