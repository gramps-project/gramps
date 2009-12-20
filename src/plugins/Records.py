# encoding:utf-8
#
# Gramps - a GTK+/GNOME based genealogy program - Records plugin
#
# Copyright (C) 2008 Reinhard Müller
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

# $Id: $

#------------------------------------------------------------------------
#
# Standard Python modules
#
#------------------------------------------------------------------------
import datetime
from TransUtils import sgettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import gen.lib
from gen.lib import ChildRefType, Date, Name
from gen.plug.docgen import FontStyle, ParagraphStyle, FONT_SANS_SERIF
from BasicUtils import name_displayer
from gen.plug import Gramplet
from gen.plug.menu import (BooleanOption, EnumeratedListOption, 
                           FilterOption, PersonOption)
from ReportBase import Report, ReportUtils, MenuReportOptions
from Utils import probably_alive

#------------------------------------------------------------------------
#
# Global functions
#
#------------------------------------------------------------------------

def _good_date(date):
    if date:
        if RecordsReportOptions.REGULAR_DATES_ONLY:
            return date.is_regular()
        else:
            return date.is_valid()
    else:
        return False


def _find_death_date(db, person):
    death_ref = person.get_death_ref()
    if death_ref:
        death = db.get_event_from_handle(death_ref.ref)
        return death.get_date_object()
    else:
        event_list = person.get_primary_event_ref_list()
        for event_ref in event_list:
            event = db.get_event_from_handle(event_ref.ref)
            if event.get_type().is_death_fallback():
                return event.get_date_object()
    return None


def _find_records(db, filter, callname):

    today = datetime.date.today()
    today_date = Date(today.year, today.month, today.day)

    # Person records
    person_youngestliving = []
    person_oldestliving = []
    person_youngestdied = []
    person_oldestdied = []
    person_youngestmarried = []
    person_oldestmarried = []
    person_youngestdivorced = []
    person_oldestdivorced = []
    person_youngestfather = []
    person_youngestmother = []
    person_oldestfather = []
    person_oldestmother = []

    person_handle_list = db.iter_person_handles()

    if filter:
        person_handle_list = filter.apply(db, person_handle_list)

    for person_handle in person_handle_list:
        person = db.get_person_from_handle(person_handle)

        birth_ref = person.get_birth_ref()

        if not birth_ref:
            # No birth event, so we can't calculate any age.
            continue

        birth = db.get_event_from_handle(birth_ref.ref)
        birth_date = birth.get_date_object()

        death_date = _find_death_date(db, person)

        if not _good_date(birth_date):
            # Birth date unknown or incomplete, so we can't calculate any age.
            continue

        name = _person_get_display_name(person, callname)

        if death_date is None:
            if probably_alive(person, db):
                # Still living, look for age records
                _record(person_youngestliving, person_oldestliving,
                        today_date - birth_date, name, 'Person', person_handle)
        elif _good_date(death_date):
            # Already died, look for age records
            _record(person_youngestdied, person_oldestdied,
                    death_date - birth_date, name, 'Person', person_handle)

        for family_handle in person.get_family_handle_list():
            family = db.get_family_from_handle(family_handle)

            marriage_date = None
            divorce_date = None
            for event_ref in family.get_event_ref_list():
                event = db.get_event_from_handle(event_ref.ref)
                if (event.get_type().is_marriage() and 
                    (event_ref.get_role().is_family() or 
                     event_ref.get_role().is_primary())):
                    marriage_date = event.get_date_object()
                elif (event.get_type().is_divorce() and 
                      (event_ref.get_role().is_family() or 
                       event_ref.get_role().is_primary())):
                    divorce_date = event.get_date_object()

            if _good_date(marriage_date):
                _record(person_youngestmarried, person_oldestmarried,
                        marriage_date - birth_date,
                        name, 'Person', person_handle)

            if _good_date(divorce_date):
                _record(person_youngestdivorced, person_oldestdivorced,
                        divorce_date - birth_date,
                        name, 'Person', person_handle)

            for child_ref in family.get_child_ref_list():
                if person.get_gender() == person.MALE:
                    relation = child_ref.get_father_relation()
                elif person.get_gender() == person.FEMALE:
                    relation = child_ref.get_mother_relation()
                else:
                    continue
                if relation != ChildRefType.BIRTH:
                    continue

                child = db.get_person_from_handle(child_ref.ref)

                child_birth_ref = child.get_birth_ref()
                if not child_birth_ref:
                    continue

                child_birth = db.get_event_from_handle(child_birth_ref.ref)
                child_birth_date = child_birth.get_date_object()

                if not _good_date(child_birth_date):
                    continue

                if person.get_gender() == person.MALE:
                    _record(person_youngestfather, person_oldestfather,
                            child_birth_date - birth_date,
                            name, 'Person', person_handle)
                elif person.get_gender() == person.FEMALE:
                    _record(person_youngestmother, person_oldestmother,
                            child_birth_date - birth_date,
                            name, 'Person', person_handle)


    # Family records
    family_mostchildren = []
    family_youngestmarried = []
    family_oldestmarried = []
    family_shortest = []
    family_longest = []

    for family in db.iter_families():
        #family = db.get_family_from_handle(family_handle)

        father_handle = family.get_father_handle()
        if not father_handle:
            continue
        mother_handle = family.get_mother_handle()
        if not mother_handle:
            continue

        # Test if either father or mother are in filter
        if filter:
            if not filter.apply(db, [father_handle, mother_handle]):
                continue

        father = db.get_person_from_handle(father_handle)
        mother = db.get_person_from_handle(mother_handle)

        name = _("%s and %s") % (
                _person_get_display_name(father, callname),
                _person_get_display_name(mother, callname))

        _record(None, family_mostchildren,
                len(family.get_child_ref_list()),
                name, 'Family', family.handle)

        marriage_date = None
        divorce_date = None
        for event_ref in family.get_event_ref_list():
            event = db.get_event_from_handle(event_ref.ref)
            if (event.get_type().is_marriage() and 
                (event_ref.get_role().is_family() or 
                 event_ref.get_role().is_primary())):
                marriage_date = event.get_date_object()
            if (event and event.get_type().is_divorce() and 
                (event_ref.get_role().is_family() or 
                 event_ref.get_role().is_primary())):
                divorce_date = event.get_date_object()

        father_death_date = _find_death_date(db, father)
        mother_death_date = _find_death_date(db, mother)

        if not _good_date(marriage_date):
            # Not married or marriage date unknown
            continue

        if divorce_date is None and father_death_date is None and mother_death_date is None:
            # Still married and alive
            if probably_alive(father, db) and probably_alive(mother, db):
                _record(family_youngestmarried, family_oldestmarried,
                        today_date - marriage_date,
                        name, 'Family', family.handle)
        elif (_good_date(divorce_date) or 
              _good_date(father_death_date) or 
              _good_date(mother_death_date)):
            end = None
            if _good_date(father_death_date) and _good_date(mother_death_date):
                end = min(father_death_date, mother_death_date)
            elif _good_date(father_death_date):
                end = father_death_date
            elif _good_date(mother_death_date):
                end = mother_death_date
            if _good_date(divorce_date):
                if end:
                    end = min(end, divorce_date)
                else:
                    end = divorce_date
            duration = end - marriage_date

            _record(family_shortest, family_longest,
                    duration, name, 'Family', family.handle)

    return [(text, varname, locals()[varname]) for (text, varname, default) in RECORDS]


def _person_get_display_name(person, callname):

    # Make a copy of the name object so we don't mess around with the real
    # data.
    n = Name(source=person.get_primary_name())

    if n.call:
        if callname == RecordsReportOptions.CALLNAME_REPLACE:
            n.first_name = n.call
        elif callname == RecordsReportOptions.CALLNAME_UNDERLINE_ADD:
            if n.call in n.first_name:
                (before, after) = n.first_name.split(n.call)
                n.first_name = "%(before)s<u>%(call)s</u>%(after)s" % {
                        'before': before,
                        'call': n.call,
                        'after': after}
            else:
                n.first_name = "\"%(call)s\" (%(first)s)" % {
                        'call':  n.call,
                        'first': n.first_name}

    return name_displayer.display_name(n)


def _record(lowest, highest, value, text, handle_type, handle):

    if lowest is not None:
        lowest.append((value, text, handle_type, handle))
        lowest.sort(lambda a,b: cmp(a[0], b[0]))
        for i in range(RecordsReportOptions.TOP_SIZE, len(lowest)):
            if lowest[i-1][0] < lowest[i][0]:
                del lowest[i:]
                break

    if highest is not None:
        highest.append((value, text, handle_type, handle))
        highest.sort(reverse=True)
        for i in range(RecordsReportOptions.TOP_SIZE, len(highest)):
            if highest[i-1][0] > highest[i][0]:
                del highest[i:]
                break


def _output(value):
    return str(value)


#------------------------------------------------------------------------
#
# The Gramplet
#
#------------------------------------------------------------------------
class RecordsGramplet(Gramplet):

    def init(self):
        self.set_use_markup(True)
        self.set_tooltip(_("Double-click name for details"))
        self.set_text(_("No Family Tree loaded."))

    def db_changed(self):
        self.dbstate.db.connect('person-rebuild', self.update)
        self.dbstate.db.connect('family-rebuild', self.update)

    def main(self):
        self.set_text(_("Processing...") + "\n")
        yield True
        records = _find_records(self.dbstate.db, None,
                RecordsReportOptions.CALLNAME_DONTUSE)
        self.set_text("")
        for (text, varname, top) in records:
            yield True
            self.render_text("<b>%s</b>" % text)
            last_value = None
            rank = 0
            for (number, (value, name, handletype, handle)) in enumerate(top):
                if value != last_value:
                    last_value = value
                    rank = number
                self.append_text("\n  %s. " % (rank+1))
                self.link(name, handletype, handle)
                self.append_text(" (%s)" % _output(value))
            self.append_text("\n")
        self.append_text("", scroll_to='begin')
        yield False


#------------------------------------------------------------------------
#
# The Report
#
#------------------------------------------------------------------------
class RecordsReport(Report):

    def __init__(self, database, options_class):

        Report.__init__(self, database, options_class)
        menu = options_class.menu

        self.filter_option =  menu.get_option_by_name('filter')
        self.filter = self.filter_option.get_filter()

        self.callname = menu.get_option_by_name('callname').get_value()

        self.include = {}
        for (text, varname, default) in RECORDS:
            self.include[varname] = menu.get_option_by_name(varname).get_value()


    def write_report(self):
        """
        Build the actual report.
        """

        records = _find_records(self.database, self.filter, self.callname)

        self.doc.start_paragraph('REC-Title')
        self.doc.write_text(_("Records"))
        self.doc.end_paragraph()

        for (text, varname, top) in records:
            if not self.include[varname]:
                continue

            self.doc.start_paragraph('REC-Heading')
            self.doc.write_text(text)
            self.doc.end_paragraph()

            last_value = None
            rank = 0
            for (number, (value, name, handletype, handle)) in enumerate(top):
                if value != last_value:
                    last_value = value
                    rank = number
                self.doc.start_paragraph('REC-Normal')
                self.doc.write_text(_("%(number)s. %(name)s (%(value)s)") % {
                    'number': rank+1,
                    'name': name,
                    'value': _output(value)})
                self.doc.end_paragraph()


#------------------------------------------------------------------------
#
# MenuReportOptions
#
#------------------------------------------------------------------------
class RecordsReportOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
    """

    CALLNAME_DONTUSE = 0
    CALLNAME_REPLACE = 1
    CALLNAME_UNDERLINE_ADD = 2
    REGULAR_DATES_ONLY = True
    TOP_SIZE = 3

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
        
        self.__update_filters()

        callname = EnumeratedListOption(_("Use call name"), self.CALLNAME_DONTUSE)
        callname.set_items([
            (self.CALLNAME_DONTUSE, _("Don't use call name")),
            (self.CALLNAME_REPLACE, _("Replace first name with call name")),
            (self.CALLNAME_UNDERLINE_ADD, _("Underline call name in first name / add call name to first name"))])
        menu.add_option(category_name, "callname", callname)

        for (text, varname, default) in RECORDS:
            option = BooleanOption(text, default)
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
        filter_list = ReportUtils.get_person_filters(person, False)
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
        font.set_size(10)
        font.set_bold(0)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style('REC-Normal', para)

        font = FontStyle()
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(10)
        font.set_bold(1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_description(_('The style used for headings.'))
        default_style.add_paragraph_style('REC-Heading', para)

        font = FontStyle()
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(12)
        font.set_bold(1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_description(_("The style used for the report title."))
        default_style.add_paragraph_style('REC-Title', para)

#------------------------------------------------------------------------
#
# List of records (must be defined after declaration of _())
#
#------------------------------------------------------------------------
RECORDS = [
        (_("Youngest living person"),          'person_youngestliving',   True),
        (_("Oldest living person"),            'person_oldestliving',     True),
        (_("Person died at youngest age"),     'person_youngestdied',     False),
        (_("Person died at oldest age"),       'person_oldestdied',       True),
        (_("Person married at youngest age"),  'person_youngestmarried',  True),
        (_("Person married at oldest age"),    'person_oldestmarried',    True),
        (_("Person divorced at youngest age"), 'person_youngestdivorced', False),
        (_("Person divorced at oldest age"),   'person_oldestdivorced',   False),
        (_("Youngest father"),                 'person_youngestfather',   True),
        (_("Youngest mother"),                 'person_youngestmother',   True),
        (_("Oldest father"),                   'person_oldestfather',     True),
        (_("Oldest mother"),                   'person_oldestmother',     True),
        (_("Couple with most children"),       'family_mostchildren',     True),
        (_("Living couple married most recently"),    'family_youngestmarried',  True),
        (_("Living couple married most long ago"),    'family_oldestmarried',    True),
        (_("Shortest past marriage"),          'family_shortest',         False),
        (_("Longest past marriage"),           'family_longest',          True)]
