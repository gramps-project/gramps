# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Martin Hawlisch, Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
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

"""
Validate localized date parser and displayer.

Tools/Debug/Check Localized Date Parser and Displayer
"""

#-------------------------------------------------------------------------
#
# standard python modules
#
#-------------------------------------------------------------------------
import traceback
import sys
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.lib import Date, Event, EventRef, EventType, Name, Person, Surname, Tag
from gramps.gen.db import DbTxn
from gramps.gui.plug import tool
from gramps.gui.utils import ProgressMeter
from gramps.gui.dialog import QuestionDialog
from gramps.gen.datehandler import parser as _dp
from gramps.gen.datehandler import displayer as _dd

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class DateParserDisplayTest(tool.Tool):

    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate

        tool.Tool.__init__(self, dbstate, options_class, name)
        if uistate:
            # Running with gui -> Show message
            self.parent_window = uistate.window
            QuestionDialog(_("Start date test?"),
                _("This test will create many persons and events " \
                    "in the current database. Do you really want to " \
                    "run this test?"),
                _("Run test"),
                self.run_tool,
                parent=self.parent_window)
        else:
            self.parent_window = None
            self.run_tool()


    def run_tool(self):
        self.progress = ProgressMeter(_('Running Date Test'), '',
                                      parent=self.parent_window)
        self.progress.set_pass(_('Generating dates'),
                               4)
        dates = []
        # first some valid dates
        calendar = Date.CAL_GREGORIAN
        for quality in (Date.QUAL_NONE, Date.QUAL_ESTIMATED,
                        Date.QUAL_CALCULATED):
            for modifier in (Date.MOD_NONE, Date.MOD_BEFORE,
                             Date.MOD_AFTER, Date.MOD_ABOUT):
                for slash1 in (False,True):
                    for month in range(0,13):
                        for day in (0,5,27):
                            if not month and day:
                                continue
                            d = Date()
                            d.set(quality,modifier,calendar,(day,month,1789,slash1),"Text comment")
                            dates.append( d)
            for modifier in (Date.MOD_RANGE, Date.MOD_SPAN):
                for slash1 in (False,True):
                    for slash2 in (False,True):
                        for month in range(0,13):
                            for day in (0,5,27):
                                if not month and day:
                                    continue

                                d = Date()
                                d.set(quality,modifier,calendar,(day,month,1789,slash1,day,month,1876,slash2),"Text comment")
                                dates.append( d)

                                if not month:
                                    continue

                                d = Date()
                                d.set(quality,modifier,calendar,(day,month,1789,slash1,day,13-month,1876,slash2),"Text comment")
                                dates.append( d)

                                if not day:
                                    continue

                                d = Date()
                                d.set(quality,modifier,calendar,(day,month,1789,slash1,32-day,month,1876,slash2),"Text comment")
                                dates.append( d)
                                d = Date()
                                d.set(quality,modifier,calendar,(day,month,1789,slash1,32-day,13-month,1876,slash2),"Text comment")
                                dates.append( d)
            modifier = Date.MOD_TEXTONLY
            d = Date()
            d.set(quality,modifier,calendar,Date.EMPTY,
                  "This is a textual date")
            dates.append( d)
            self.progress.step()

        # test invalid dates
        #dateval = (4,7,1789,False,5,8,1876,False)
        #for l in range(1,len(dateval)):
        #    d = Date()
        #    try:
        #        d.set(Date.QUAL_NONE,Date.MOD_NONE,
        #              Date.CAL_GREGORIAN,dateval[:l],"Text comment")
        #        dates.append( d)
        #    except DateError, e:
        #        d.set_as_text("Date identified value correctly as invalid.\n%s" % e)
        #        dates.append( d)
        #    except:
        #        d = Date()
        #        d.set_as_text("Date.set Exception %s" % ("".join(traceback.format_exception(*sys.exc_info())),))
        #        dates.append( d)
        #for l in range(1,len(dateval)):
        #    d = Date()
        #    try:
        #        d.set(Date.QUAL_NONE,Date.MOD_SPAN,Date.CAL_GREGORIAN,dateval[:l],"Text comment")
        #        dates.append( d)
        #    except DateError, e:
        #        d.set_as_text("Date identified value correctly as invalid.\n%s" % e)
        #        dates.append( d)
        #    except:
        #        d = Date()
        #        d.set_as_text("Date.set Exception %s" % ("".join(traceback.format_exception(*sys.exc_info())),))
        #        dates.append( d)
        #self.progress.step()
        #d = Date()
        #d.set(Date.QUAL_NONE,Date.MOD_NONE,
        #      Date.CAL_GREGORIAN,(44,7,1789,False),"Text comment")
        #dates.append( d)
        #d = Date()
        #d.set(Date.QUAL_NONE,Date.MOD_NONE,
        #      Date.CAL_GREGORIAN,(4,77,1789,False),"Text comment")
        #dates.append( d)
        #d = Date()
        #d.set(Date.QUAL_NONE,Date.MOD_SPAN,
        #      Date.CAL_GREGORIAN,
        #      (4,7,1789,False,55,8,1876,False),"Text comment")
        #dates.append( d)
        #d = Date()
        #d.set(Date.QUAL_NONE,Date.MOD_SPAN,
        #      Date.CAL_GREGORIAN,
        #      (4,7,1789,False,5,88,1876,False),"Text comment")
        #dates.append( d)

        with DbTxn(_("Date Test Plugin"), self.db, batch=True) as self.trans:
            self.db.disable_signals()
            self.progress.set_pass(_('Generating dates'),
                                   len(dates))

            # create pass and fail tags
            pass_handle = self.create_tag(_('Pass'), '#0000FFFF0000')
            fail_handle = self.create_tag(_('Fail'), '#FFFF00000000')

            # now add them as birth to new persons
            i = 1
            for dateval in dates:
                person = Person()
                surname = Surname()
                surname.set_surname("DateTest")
                name = Name()
                name.add_surname(surname)
                name.set_first_name("Test %d" % i)
                person.set_primary_name(name)
                self.db.add_person(person, self.trans)
                bevent = Event()
                bevent.set_type(EventType.BIRTH)
                bevent.set_date_object(dateval)
                bevent.set_description("Date Test %d (source)" % i)
                bevent_h = self.db.add_event(bevent, self.trans)
                bevent_ref = EventRef()
                bevent_ref.set_reference_handle(bevent_h)
                # for the death event display the date as text and parse it back to a new date
                ndate = None
                try:
                    datestr = _dd.display( dateval)
                    try:
                        ndate = _dp.parse( datestr)
                        if not ndate:
                            ndate = Date()
                            ndate.set_as_text("DateParser None")
                            person.add_tag(fail_handle)
                        else:
                            person.add_tag(pass_handle)
                    except:
                        ndate = Date()
                        ndate.set_as_text("DateParser Exception %s" % ("".join(traceback.format_exception(*sys.exc_info())),))
                        person.add_tag(fail_handle)
                    else:
                        person.add_tag(pass_handle)
                except:
                    ndate = Date()
                    ndate.set_as_text("DateDisplay Exception: %s" % ("".join(traceback.format_exception(*sys.exc_info())),))
                    person.add_tag(fail_handle)

                if dateval.get_modifier() != Date.MOD_TEXTONLY \
                       and ndate.get_modifier() == Date.MOD_TEXTONLY:
                    # parser was unable to correctly parse the string
                    ndate.set_as_text( "TEXTONLY: "+ndate.get_text())
                    person.add_tag(fail_handle)
                if dateval.get_modifier() == Date.MOD_TEXTONLY \
                        and dateval.get_text().count("Traceback") \
                        and pass_handle in person.get_tag_list():
                    person.add_tag(fail_handle)

                devent = Event()
                devent.set_type(EventType.DEATH)
                devent.set_date_object(ndate)
                devent.set_description("Date Test %d (result)" % i)
                devent_h = self.db.add_event(devent, self.trans)
                devent_ref = EventRef()
                devent_ref.set_reference_handle(devent_h)
                person.set_birth_ref(bevent_ref)
                person.set_death_ref(devent_ref)
                self.db.commit_person(person, self.trans)
                i = i + 1
                self.progress.step()
        self.db.enable_signals()
        self.db.request_rebuild()
        self.progress.close()

    def create_tag(self, tag_name, tag_color):
        """
        Create a tag if it doesn't already exist.
        """
        tag = self.db.get_tag_from_name(tag_name)
        if tag is None:
            tag = Tag()
            tag.set_name(tag_name)
            if tag_color is not None:
                tag.set_color(tag_color)
            tag.set_priority(self.db.get_number_of_tags())
            tag_handle = self.db.add_tag(tag, self.trans)
        else:
            tag_handle = tag.get_handle()
        return tag_handle

#------------------------------------------------------------------------
#
# DateParserDisplayTestOptions
#
#------------------------------------------------------------------------
class DateParserDisplayTestOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """
    def __init__(self, name, person_id=None):
        """ Initialize the options class """
        tool.ToolOptions.__init__(self, name, person_id)
