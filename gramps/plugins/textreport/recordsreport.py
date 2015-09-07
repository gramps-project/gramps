# encoding:utf-8
#
# Gramps - a GTK+/GNOME based genealogy program - Records plugin
#
# Copyright (C) 2008-2011 Reinhard Müller
# Copyright (C) 2010      Jakim Friant
# Copyright (C) 2013-2015 Paul Franklin
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

#------------------------------------------------------------------------
#
# Standard Python modules
#
#------------------------------------------------------------------------

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.plugins.lib.librecords import (RECORDS, find_records,
                                           CALLNAME_DONTUSE, CALLNAME_REPLACE,
                                           CALLNAME_UNDERLINE_ADD)
from gramps.gen.plug.docgen import (FontStyle, ParagraphStyle,
                                    FONT_SANS_SERIF, PARA_ALIGN_CENTER,
                                    IndexMark, INDEX_TYPE_TOC)
from gramps.gen.plug.menu import (BooleanOption, EnumeratedListOption,
                                  FilterOption, NumberOption,
                                  PersonOption, StringOption)
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils as ReportUtils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.lib import Span

#------------------------------------------------------------------------
#
# Records Report
#
#------------------------------------------------------------------------
class RecordsReport(Report):

    def __init__(self, database, options, user):
        """
        This report needs the following parameters (class variables)
        that come in the options class.

        incl_private    - Whether to include private data
        """

        Report.__init__(self, database, options, user)
        menu = options.menu

        stdoptions.run_private_data_option(self, menu)

        self.filter_option =  menu.get_option_by_name('filter')
        self.filter = self.filter_option.get_filter()

        self.top_size = menu.get_option_by_name('top_size').get_value()
        self.callname = menu.get_option_by_name('callname').get_value()

        self.footer = menu.get_option_by_name('footer').get_value()

        self.include = {}
        for (text, varname, default) in RECORDS:
            self.include[varname] = menu.get_option_by_name(varname).get_value()

        self._lang = options.menu.get_option_by_name('trans').get_value()
        self._locale = self.set_locale(self._lang)

        self._nf = stdoptions.run_name_format_option(self, menu)

    def write_report(self):
        """
        Build the actual report.
        """

        records = find_records(self.database, self.filter,
                               self.top_size, self.callname,
                               trans_text=self._, name_format=self._nf)

        self.doc.start_paragraph('REC-Title')
        title = self._("Records")
        mark = IndexMark(title, INDEX_TYPE_TOC, 1)
        self.doc.write_text(title, mark)
        self.doc.end_paragraph()

        self.doc.start_paragraph('REC-Subtitle')
        self.doc.write_text(self.filter.get_name(self._locale))
        self.doc.end_paragraph()

        for (text, varname, top) in records:
            if not self.include[varname]:
                continue

            self.doc.start_paragraph('REC-Heading')
            self.doc.write_text(self._(text))
            self.doc.end_paragraph()

            last_value = None
            rank = 0
            for (number,
                 (sort, value, name, handletype, handle)) in enumerate(top):
                # FIXME check whether person or family, if a family mark BOTH
                person = self.database.get_person_from_handle(handle)
                mark = ReportUtils.get_person_mark(self.database, person)
                if value != last_value:
                    last_value = value
                    rank = number
                self.doc.start_paragraph('REC-Normal')
                # FIXME this won't work for RTL languages:
                self.doc.write_text(self._("%(number)s. ") % {'number': rank+1})
                self.doc.write_markup(str(name), name.get_tags(), mark)
                if isinstance(value, Span):
                    tvalue = value.get_repr(dlocale=self._locale)
                else:
                    tvalue = value
                self.doc.write_text(" (%s)" % tvalue)
                self.doc.end_paragraph()

        self.doc.start_paragraph('REC-Footer')
        self.doc.write_text(self.footer)
        self.doc.end_paragraph()


#------------------------------------------------------------------------
#
# Records Report Options
#
#------------------------------------------------------------------------
class RecordsReportOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dbase):

        self.__pid = None
        self.__filter = None
        self.__db = dbase
        MenuReportOptions.__init__(self, name, dbase)


    def add_menu_options(self, menu):

        category_name = _("Report Options")

        self.__filter = FilterOption(_("Filter"), 0)
        self.__filter.set_help(
                      _("Determines what people are included in the report."))
        menu.add_option(category_name, "filter", self.__filter)
        self.__filter.connect('value-changed', self.__filter_changed)

        self.__pid = PersonOption(_("Filter Person"))
        self.__pid.set_help(_("The center person for the filter"))
        menu.add_option(category_name, "pid", self.__pid)
        self.__pid.connect('value-changed', self.__update_filters)

        self._nf = stdoptions.add_name_format_option(menu, category_name)
        self._nf.connect('value-changed', self.__update_filters)

        self.__update_filters()

        stdoptions.add_private_data_option(menu, category_name)

        top_size = NumberOption(_("Number of ranks to display"), 3, 1, 100)
        menu.add_option(category_name, "top_size", top_size)

        callname = EnumeratedListOption(_("Use call name"), CALLNAME_DONTUSE)
        callname.set_items([
            (CALLNAME_DONTUSE, _("Don't use call name")),
            (CALLNAME_REPLACE, _("Replace first names with call name")),
            (CALLNAME_UNDERLINE_ADD, _("Underline call name in first names / add call name to first name"))])
        menu.add_option(category_name, "callname", callname)

        footer = StringOption(_("Footer text"), "")
        menu.add_option(category_name, "footer", footer)

        stdoptions.add_localization_option(menu, category_name)

        for (text, varname, default) in RECORDS:
            option = BooleanOption(_(text), default)
            if varname.startswith('person'):
                category_name = _("Person Records")
            elif varname.startswith('family'):
                category_name = _("Family Records")
            menu.add_option(category_name, varname, option)

    def __update_filters(self):
        """
        Update the filter list based on the selected person
        """
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        nfv = self._nf.get_value()
        filter_list = ReportUtils.get_person_filters(person,
                                                     include_single=False,
                                                     name_format=nfv)
        self.__filter.set_filters(filter_list)

    def __filter_changed(self):
        """
        Handle filter change. If the filter is not specific to a person,
        disable the person option
        """
        filter_value = self.__filter.get_value()
        if filter_value in [1, 2, 3, 4]:
            # Filters 1, 2, 3 and 4 rely on the center person
            self.__pid.set_available(True)
        else:
            # The rest don't
            self.__pid.set_available(False)

    def make_default_style(self, default_style):

        #Paragraph Styles
        font = FontStyle()
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(16)
        font.set_bold(True)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_description(_("The style used for the report title."))
        default_style.add_paragraph_style('REC-Title', para)

        font = FontStyle()
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(12)
        font.set_bold(True)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_bottom_border(True)
        para.set_bottom_margin(ReportUtils.pt2cm(8))
        para.set_description(_("The style used for the report subtitle."))
        default_style.add_paragraph_style('REC-Subtitle', para)

        font = FontStyle()
        font.set_size(12)
        font.set_bold(True)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_top_margin(ReportUtils.pt2cm(6))
        para.set_description(_('The style used for headings.'))
        default_style.add_paragraph_style('REC-Heading', para)

        font = FontStyle()
        font.set_size(10)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_left_margin(0.5)
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style('REC-Normal', para)

        font = FontStyle()
        font.set_size(8)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_top_border(True)
        para.set_top_margin(ReportUtils.pt2cm(8))
        para.set_description(_('The style used for the footer.'))
        default_style.add_paragraph_style('REC-Footer', para)
