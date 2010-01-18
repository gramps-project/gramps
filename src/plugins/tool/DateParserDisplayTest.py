# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Martin Hawlisch, Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
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
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import gen.lib
from PluginUtils import Tool
from gui.utils import ProgressMeter
from QuestionDialog import QuestionDialog
from DateHandler import parser as _dp
from DateHandler import displayer as _dd

#-------------------------------------------------------------------------
#
#
#
#-------------------------------------------------------------------------
class DateParserDisplayTest(Tool.Tool):

    def __init__(self, dbstate, uistate, options_class, name, callback=None):

        Tool.Tool.__init__(self, dbstate, options_class, name)
        if uistate:
            # Running with gui -> Show message
            QuestionDialog(_("Start date test?"),_("This test will create many persons and events in the current database. Do you really want to run this test?"),_("Run test"),self.run_tool)
        else:
            self.run_tool()


    def run_tool(self):
        self.progress = ProgressMeter(_('Running Date Test'),'')
        self.progress.set_pass(_('Generating dates'),
                               4)
        dates = []
        # first some valid dates
        calendar = gen.lib.Date.CAL_GREGORIAN
        for quality in (gen.lib.Date.QUAL_NONE, gen.lib.Date.QUAL_ESTIMATED,
                        gen.lib.Date.QUAL_CALCULATED):
            for modifier in (gen.lib.Date.MOD_NONE, gen.lib.Date.MOD_BEFORE,
                             gen.lib.Date.MOD_AFTER, gen.lib.Date.MOD_ABOUT):
                for slash1 in (False,True):
                    for month in range(1,13):
                        for day in (5,27):
                            d = gen.lib.Date()
                            d.set(quality,modifier,calendar,(day,month,1789,slash1),"Text comment")
                            dates.append( d)
            for modifier in (gen.lib.Date.MOD_RANGE, gen.lib.Date.MOD_SPAN):
                for slash1 in (False,True):
                    for slash2 in (False,True):
                        for month in range(1,13):
                            for day in (5,27):
                                d = gen.lib.Date()
                                d.set(quality,modifier,calendar,(day,month,1789,slash1,day,month,1876,slash2),"Text comment")
                                dates.append( d)
                                d = gen.lib.Date()
                                d.set(quality,modifier,calendar,(day,month,1789,slash1,day,13-month,1876,slash2),"Text comment")
                                dates.append( d)
                                d = gen.lib.Date()
                                d.set(quality,modifier,calendar,(day,month,1789,slash1,32-day,month,1876,slash2),"Text comment")
                                dates.append( d)
                                d = gen.lib.Date()
                                d.set(quality,modifier,calendar,(day,month,1789,slash1,32-day,13-month,1876,slash2),"Text comment")
                                dates.append( d)
            modifier = gen.lib.Date.MOD_TEXTONLY
            d = gen.lib.Date()
            d.set(quality,modifier,calendar,gen.lib.Date.EMPTY,
                  "This is a textual date")
            dates.append( d)
            self.progress.step()
        
        # test invalid dates
        #dateval = (4,7,1789,False,5,8,1876,False)
        #for l in range(1,len(dateval)):
        #    d = gen.lib.Date()
        #    try:
        #        d.set(gen.lib.Date.QUAL_NONE,gen.lib.Date.MOD_NONE,
        #              gen.lib.Date.CAL_GREGORIAN,dateval[:l],"Text comment")
        #        dates.append( d)
        #    except Errors.DateError, e:
        #        d.set_as_text("Date identified value correctly as invalid.\n%s" % e)
        #        dates.append( d)
        #    except:
        #        d = gen.lib.Date()
        #        d.set_as_text("Date.set Exception %s" % ("".join(traceback.format_exception(*sys.exc_info())),))
        #        dates.append( d)
        #for l in range(1,len(dateval)):
        #    d = gen.lib.Date()
        #    try:
        #        d.set(gen.lib.Date.QUAL_NONE,gen.lib.Date.MOD_SPAN,gen.lib.Date.CAL_GREGORIAN,dateval[:l],"Text comment")
        #        dates.append( d)
        #    except Errors.DateError, e:
        #        d.set_as_text("Date identified value correctly as invalid.\n%s" % e)
        #        dates.append( d)
        #    except:
        #        d = gen.lib.Date()
        #        d.set_as_text("Date.set Exception %s" % ("".join(traceback.format_exception(*sys.exc_info())),))
        #        dates.append( d)
        #self.progress.step()
        #d = gen.lib.Date()
        #d.set(gen.lib.Date.QUAL_NONE,gen.lib.Date.MOD_NONE,
        #      gen.lib.Date.CAL_GREGORIAN,(44,7,1789,False),"Text comment")
        #dates.append( d)
        #d = gen.lib.Date()
        #d.set(gen.lib.Date.QUAL_NONE,gen.lib.Date.MOD_NONE,
        #      gen.lib.Date.CAL_GREGORIAN,(4,77,1789,False),"Text comment")
        #dates.append( d)
        #d = gen.lib.Date()
        #d.set(gen.lib.Date.QUAL_NONE,gen.lib.Date.MOD_SPAN,
        #      gen.lib.Date.CAL_GREGORIAN,
        #      (4,7,1789,False,55,8,1876,False),"Text comment")
        #dates.append( d)
        #d = gen.lib.Date()
        #d.set(gen.lib.Date.QUAL_NONE,gen.lib.Date.MOD_SPAN,
        #      gen.lib.Date.CAL_GREGORIAN,
        #      (4,7,1789,False,5,88,1876,False),"Text comment")
        #dates.append( d)
        
        trans = self.db.transaction_begin("",batch=True)
        self.db.disable_signals()
        self.progress.set_pass(_('Generating dates'),
                               len(dates))
        # now add them as birth to new persons
        i = 1
        for dateval in dates:
            person = gen.lib.Person()
            name = gen.lib.Name()
            name.set_surname("DateTest")
            name.set_first_name("Test %d" % i)
            person.set_primary_name( name)
            self.db.add_person(person,trans)
            bevent = gen.lib.Event()
            bevent.set_type(gen.lib.EventType.BIRTH)
            bevent.set_date_object(dateval)
            bevent.set_description("Date Test %d (source)" % i)
            bevent_h = self.db.add_event(bevent,trans)
            bevent_ref = gen.lib.EventRef()
            bevent_ref.set_reference_handle(bevent_h)
            # for the death event display the date as text and parse it back to a new date
            ndate = None
            try:
                datestr = _dd.display( dateval)
                try:
                    ndate = _dp.parse( datestr)
                    if not ndate:
                        ndate = gen.lib.Date()
                        ndate.set_as_text("DateParser None")
                        person.set_marker(gen.lib.MarkerType.TODO_TYPE)
                    else:
                        person.set_marker(gen.lib.MarkerType.COMPLETE)
                except:
                    ndate = gen.lib.Date()
                    ndate.set_as_text("DateParser Exception %s" % ("".join(traceback.format_exception(*sys.exc_info())),))
                    person.set_marker(gen.lib.MarkerType.TODO_TYPE)
            except:
                ndate = gen.lib.Date()
                ndate.set_as_text("DateDisplay Exception: %s" % ("".join(traceback.format_exception(*sys.exc_info())),))
                person.set_marker(gen.lib.MarkerType.TODO_TYPE)
            
            if dateval.get_modifier() != gen.lib.Date.MOD_TEXTONLY \
                   and ndate.get_modifier() == gen.lib.Date.MOD_TEXTONLY:
                # parser was unable to correctly parse the string
                ndate.set_as_text( "TEXTONLY: "+ndate.get_text())
                person.set_marker(gen.lib.MarkerType.TODO_TYPE)
            if dateval.get_modifier() == gen.lib.Date.MOD_TEXTONLY \
                    and dateval.get_text().count("Traceback") \
                    and person.get_marker() == gen.lib.MarkerType.COMPLETE:
                person.set_marker(gen.lib.MarkerType.TODO_TYPE)
            
            devent = gen.lib.Event()
            devent.set_type(gen.lib.EventType.DEATH)
            devent.set_date_object(ndate)
            devent.set_description("Date Test %d (result)" % i)
            devent_h = self.db.add_event(devent,trans)
            devent_ref = gen.lib.EventRef()
            devent_ref.set_reference_handle(devent_h)
            person.set_birth_ref(bevent_ref)
            person.set_death_ref(devent_ref)
            self.db.commit_person(person,trans)
            i = i + 1
            self.progress.step()
        self.db.transaction_commit(trans, _("Date Test Plugin"))
        self.db.enable_signals()
        self.db.request_rebuild()
        self.progress.close()

#------------------------------------------------------------------------
#
# DateParserDisplayTestOptions
#
#------------------------------------------------------------------------
class DateParserDisplayTestOptions(Tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """
    def __init__(self, name, person_id=None):
        """ Initialize the options class """
        Tool.ToolOptions.__init__(self, name, person_id)
