#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003  Donald N. Allingham
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

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
import cStringIO

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
import Report
import BaseDoc
import RelLib
import Errors
from QuestionDialog import ErrorDialog
from gettext import gettext as _

#------------------------------------------------------------------------
#
# AncestorReport
#
#------------------------------------------------------------------------
class FtmAncestorReport(Report.Report):

    def __init__(self,database,person,max,pgbrk,doc,output,newpage=0):
        self.map = {}
        self.database = database
        self.start = person
        self.max_generations = max
        self.pgbrk = pgbrk
        self.doc = doc
        self.newpage = newpage
        if output:
            self.standalone = 1
            self.doc.open(output)
            self.doc.init()
        else:
            self.standalone = 0
        self.sref_map = {}
        self.sref_index = 1
        
    def apply_filter(self,person,index,generation=1):
        if person == None or generation > self.max_generations:
            return
        self.map[index] = (person,generation)
    
        family = person.getMainParents()
        if family != None:
            self.apply_filter(family.getFather(),index*2,generation+1)
            self.apply_filter(family.getMother(),(index*2)+1,generation+1)

    def write_report(self):

        if self.newpage:
            self.doc.page_break()

        self.apply_filter(self.start,1)
        
        name = self.start.getPrimaryName().getRegularName()
        self.doc.start_paragraph("FTA-Title")
        title = _("Ancestors of %s") % name
        self.doc.write_text(title)
        self.doc.end_paragraph()
    
        keys = self.map.keys()
        keys.sort()
        old_gen = 0
        for key in keys :
            (person,generation) = self.map[key]
            if old_gen != generation:
                if self.pgbrk and generation > 1:
                    self.doc.page_break()
                self.doc.start_paragraph("FTA-Generation")
                t = _("Generation No. %d") % generation
                self.doc.write_text(t)
                self.doc.end_paragraph()
                old_gen = generation

            pri_name = person.getPrimaryName()
            self.doc.start_paragraph("FTA-Entry","%d." % key)
            name = pri_name.getRegularName()
            self.doc.start_bold()
            self.doc.write_text(name)
            self.doc.end_bold()

            # Check birth record
        
            birth = person.getBirth()
            bplace = birth.getPlaceName()
            bdate = birth.getDate()

            death = person.getDeath()
            dplace = death.getPlaceName()
            ddate = death.getDate()

            birth_valid = bdate != "" or bplace != ""
            death_valid = ddate != "" or dplace != ""

            if birth_valid or death_valid:
                if person.getGender() == RelLib.Person.male:
                    if bdate:
                        if bplace:
                            if ddate:
                                if dplace:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s was born %(birth_date)s "
                                                "in %(birth_place)s%(birth_endnotes)s, "
                                                "and died %(death_date)s in %(death_place)s"
                                                "%(death_endnotes)s.") % {
                                        'male_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_date' : bdate, 'birth_place' : bplace,
                                        'death_date' : ddate,'death_place' : dplace,
                                        'birth_endnotes' : self.endnotes(birth),
                                        'death_endnotes' : self.endnotes(death),
                                        })
                                else:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s was born %(birth_date)s "
                                                "in %(birth_place)s%(birth_endnotes)s, "
                                                "and died %(death_date)s%(death_endnotes)s.") % {
                                        'male_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_date' : bdate, 'birth_place' : bplace,
                                        'death_date' : ddate,
                                        'birth_endnotes' : self.endnotes(birth),
                                        'death_endnotes' : self.endnotes(death),                                    
                                        })
                            else:
                                if dplace:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s was born %(birth_date)s "
                                            "in %(birth_place)s %(birth_endnotes)s, "
                                            "and died in %(death_place)s%(death_endnotes)s.") % {
                                        'male_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_date' : bdate, 'birth_place' : bplace,
                                        'birth_endnotes' : self.endnotes(birth),
                                        'death_endnotes' : self.endnotes(death),
                                        'death_place' : dplace,
                                        })
                                else:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s was born %(birth_date)s in "
                                                        "%(birth_place)s%(birth_endnotes)s.") % {
                                        'male_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_date' : bdate, 'birth_place' : bplace,
                                        'birth_endnotes' : self.endnotes(birth),
                                        })
                        else:
                            if ddate:
                                if dplace:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s was born %(birth_date)s%(birth_endnotes)s, "
                                                        "and died %(death_date)s in %(death_place)s"
                                                        "%(death_endnotes)s.") % {
                                        'male_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_date' : bdate, 'death_date' : ddate,
                                        'death_place' : dplace,
                                        'birth_endnotes' : self.endnotes(birth),
                                        'death_endnotes' : self.endnotes(death),
                                        })
                                else:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s was born %(birth_date)s%(birth_endnotes)s, "
                                                        "and died %(death_date)s%(death_endnotes)s.") % {
                                        'male_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_date' : bdate, 'death_date' : ddate,
                                        'birth_endnotes' : self.endnotes(birth),
                                        'death_endnotes' : self.endnotes(death),
                                        })
                            else:
                                if dplace:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s was born %(birth_date)s%(birth_endnotes)s, "
                                                        "and died in %(death_place)s%(death_endnotes)s.") % {
                                        'male_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_date' : bdate, 'death_place' : dplace,
                                        'birth_endnotes' : self.endnotes(birth),
                                        'death_endnotes' : self.endnotes(death),
                                        })
                                else:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s was born "
                                            "%(birth_date)s%(birth_endnotes)s.") % {
                                        'male_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_date' : bdate,
                                        'birth_endnotes' : self.endnotes(birth),
                                        })
                    else:
                        if bplace:
                            if ddate:
                                if dplace:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s was born in %(birth_place)s%(birth_endnotes)s, "
                                                        "and died %(death_date)s in %(death_place)s"
                                                        "%(death_endnotes)s.") % {
                                        'male_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_place' : bplace, 'death_date' : ddate, 'death_place' : dplace,
                                        'birth_endnotes' : self.endnotes(birth),
                                        'death_endnotes' : self.endnotes(death),
                                        })
                                else:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s was born in %(birth_place)s%(birth_endnotes)s, "
                                                        "and died %(death_date)s%(death_endnotes)s.") % {
                                        'male_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_endnotes' : self.endnotes(birth),
                                        'death_endnotes' : self.endnotes(death),
                                        'birth_place' : bplace, 'death_date' : ddate,
                                        })
                            else:
                                if dplace:
                                   self.doc.write_text(_("%(male_name)s%(endnotes)s was born in %(birth_place)s%(birth_endnotes)s, "
                                                        "and died in %(death_place)s%(death_endnotes)s.") % {
                                        'male_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_place' : bplace,'death_place' : dplace,
                                        'birth_endnotes' : self.endnotes(birth),
                                        'death_endnotes' : self.endnotes(death),
                                        })
                                else:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s was born "
                                                "in %(birth_place)s%(birth_endnotes)s.") % {
                                        'male_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_place' : bplace,
                                        'birth_endnotes' : self.endnotes(birth),
                                        })
                        else:
                            if ddate:
                                if dplace:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s died %(death_date)s in "
                                                        "%(death_place)s%(death_endnotes)s.") % {
                                        'male_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'death_date' : ddate, 'death_place' : dplace,
                                        'death_endnotes' : self.endnotes(death),
                                        })
                                else:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s "
                                            "died %(death_date)s%(death_endnotes)s.") % {
                                        'male_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'death_date' : ddate,
                                        'death_endnotes' : self.endnotes(death),
                                        })
                            else:
                                if dplace:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s died "
                                                "in %(death_place)s%(death_endnotes)s.") % {
                                        'male_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'death_endnotes' : self.endnotes(death),
                                        'death_place' : dplace,
                                        })
                else:
                    if bdate:
                        if bplace:
                            if ddate:
                                if dplace:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s was born %(birth_date)s in %(birth_place)s"
                                                        "%(birth_endnotes)s, "
                                                        "and died %(death_date)s in %(death_place)s"
                                                        "%(death_endnotes)s.") % {
                                        'female_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_date' : bdate, 'birth_place' : bplace,
                                        'death_date' : ddate,'death_place' : dplace,
                                        'birth_endnotes' : self.endnotes(birth),
                                        'death_endnotes' : self.endnotes(death),
                                        })
                                else:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s was born %(birth_date)s in %(birth_place)s"
                                                        "%(birth_endnotes)s, "
                                                        "and died %(death_date)s%(death_endnotes)s.") % {
                                        'female_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_date' : bdate, 'birth_place' : bplace,
                                        'birth_endnotes' : self.endnotes(birth),
                                        'death_endnotes' : self.endnotes(death),
                                        'death_date' : ddate,
                                        })
                            else:
                                if dplace:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s was born %(birth_date)s in %(birth_place)s"
                                                        "%(birth_endnotes)s, "
                                                        "and died in %(death_place)s%(death_endnotes)s.") % {
                                        'female_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_date' : bdate, 'birth_place' : bplace,
                                        'death_place' : dplace,
                                        'birth_endnotes' : self.endnotes(birth),
                                        'death_endnotes' : self.endnotes(death),
                                        })
                                else:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s was born %(birth_date)s "
                                                    "in %(birth_place)s %(birth_endnotes)s.") % {
                                        'female_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_endnotes' : self.endnotes(birth),
                                        'birth_date' : bdate, 'birth_place' : bplace,
                                        })
                        else:
                            if ddate:
                                if dplace:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s was born %(birth_date)s%(birth_endnotes)s, "
                                                        "and died %(death_date)s in %(death_place)s"
                                                        "%(death_endnotes)s.") % {
                                        'female_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_date' : bdate, 'death_date' : ddate,
                                        'birth_endnotes' : self.endnotes(birth),
                                        'death_endnotes' : self.endnotes(death),
                                        'death_place' : dplace,
                                        })
                                else:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s was born %(birth_date)s%(birth_endnotes)s, "
                                                        "and died %(death_date)s%(death_endnotes)s.") % {
                                        'female_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_endnotes' : self.endnotes(birth),
                                        'death_endnotes' : self.endnotes(death),
                                        'birth_date' : bdate, 'death_date' : ddate,
                                        })
                            else:
                                if dplace:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s was born %(birth_date)s%(birth_endnotes)s, "
                                                        "and died in %(death_place)s%(death_endnotes)s.") % {
                                        'female_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_endnotes' : self.endnotes(birth),
                                        'death_endnotes' : self.endnotes(death),
                                        'birth_date' : bdate, 'death_place' : dplace,
                                        })
                                else:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s was "
                                                "born %(birth_date)s%(birth_endnotes)s.") % {
                                        'female_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_endnotes' : self.endnotes(birth),
                                        'birth_date' : bdate,
                                        })
                    else:
                        if bplace:
                            if ddate:
                                if dplace:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s was born in %(birth_place)s%(birth_endnotes)s, "
                                                        "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                                        'female_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_endnotes' : self.endnotes(birth),
                                        'death_endnotes' : self.endnotes(death),
                                        'birth_place' : bplace, 'death_date' : ddate, 'death_place' : dplace,
                                        })
                                else:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s was born in %(birth_place)s%(birth_endnotes)s, "
                                                        "and died %(death_date)s%(death_endnotes)s.") % {
                                        'female_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_endnotes' : self.endnotes(birth),
                                        'death_endnotes' : self.endnotes(death),
                                        'birth_place' : bplace, 'death_date' : ddate,
                                        })
                            else:
                                if dplace:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s was born in %(birth_place)s%(birth_endnotes)s, "
                                                        "and died in %(death_place)s%(death_endnotes)s.") % {
                                        'female_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_endnotes' : self.endnotes(birth),
                                        'death_endnotes' : self.endnotes(death),
                                        'birth_place' : bplace,'death_place' : dplace,
                                        })
                                else:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s was born "
                                                "in %(birth_place)s%(birth_endnotes)s.") % {
                                        'female_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'birth_endnotes' : self.endnotes(birth),
                                        'birth_place' : bplace,
                                        })
                        else:
                            if ddate:
                                if dplace:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s died %(death_date)s in "
                                                        "%(death_place)s%(death_endnotes)s.") % {
                                        'female_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'death_endnotes' : self.endnotes(death),
                                        'death_date' : ddate, 'death_place' : dplace,
                                        })
                                else:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s "
                                                    "died %(death_date)s%(death_endnotes)s.") % {
                                        'female_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'death_endnotes' : self.endnotes(death),
                                        'death_date' : ddate,
                                        })
                            else:
                                if dplace:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s died "
                                                "in %(death_place)s%(death_endnotes)s.") % {
                                        'female_name' : '', 'endnotes' : self.endnotes(pri_name),
                                        'death_endnotes' : self.endnotes(death),
                                        'birth_date' : bdate, 'death_place' : dplace,
                                        })
            else:
                self.doc.write_text( "%s." % self.endnotes(pri_name) )
                    
            self.doc.write_text(' ')
            self.print_parents(person,death_valid)
            self.print_spouse(person)
            self.doc.end_paragraph()

            self.print_notes(person)
            self.print_more_about(person)

        self.write_endnotes()
        if self.standalone:
            self.doc.close()

    def write_endnotes(self):
        keys = self.sref_map.keys()
        if not keys:
            return

        self.doc.start_paragraph('FTA-Generation')
        self.doc.write_text(_('Endnotes'))
        self.doc.end_paragraph()
        
        keys.sort()
        for key in keys:
            srcref = self.sref_map[key]
            base = srcref.getBase()
            
            self.doc.start_paragraph('FTA-Endnotes',"%d." % key)
            self.doc.write_text(base.getTitle())

            for item in [ base.getAuthor(), base.getPubInfo(), base.getAbbrev(),
                          srcref.getDate().getDate(),]:
                if item:
                    self.doc.write_text('; %s' % item)

            item = srcref.getText()
            if item:
                self.doc.write_text('; ')
                self.doc.write_text(_('Text:'))
                self.doc.write_text(' ')
                self.doc.write_text(item)

            item = srcref.getComments()
            if item:
                self.doc.write_text('; ')
                self.doc.write_text(_('Comments:'))
                self.doc.write_text(' ')
                self.doc.write_text(item)

            self.doc.write_text('.')
            self.doc.end_paragraph()

    def endnotes(self,obj):
        msg = cStringIO.StringIO()
        slist = obj.getSourceRefList()
        if slist:
            msg.write('<super>')
            first = 1
            for ref in slist:
                if not first:
                    msg.write(',')
                first = 0
                msg.write("%d" % self.sref_index)
                self.sref_map[self.sref_index] = ref
                self.sref_index += 1
            msg.write('</super>')
        str = msg.getvalue()
        msg.close()
        return str

    def print_notes(self,person):
        note = person.getNote()
        if not note.strip():
            return
        self.doc.start_paragraph('FTA-SubEntry')
        self.doc.write_text(_('Notes for %(person)s:') % { 
        	'person' : person.getPrimaryName().getRegularName()} )
        self.doc.end_paragraph()
        format = person.getNoteFormat()
        self.doc.write_note(note,format,'FTA-Details')
        
    def print_more_about(self,person):

        first = 1
        ncount = 0
        for name in person.getAlternateNames():
            if first:
                self.doc.start_paragraph('FTA-SubEntry')
                self.doc.write_text(_('More about %(person_name)s:') % { 
                	'person_name' : person.getPrimaryName().getRegularName() })
                self.doc.end_paragraph()
                first = 0
            self.doc.start_paragraph('FTA-Details')
            self.doc.write_text(_('Name %(count)d: %(name)s%(endnotes)s') % {
                'count' : ncount, 'name' : name.getRegularName(),
                'endnotes' : self.endnotes(name),
                })
            self.doc.end_paragraph()
            ncount += 1
            
        for event in person.getEventList():
            date = event.getDate()
            place = event.getPlace()

            if not date and not place:
                continue
            if first:
                self.doc.start_paragraph('FTA-SubEntry')
                name = person.getPrimaryName().getRegularName()
                self.doc.write_text(_('More about %(person_name)s:') % { 
                	'person_name' : name })
                self.doc.end_paragraph()
                first = 0

            self.doc.start_paragraph('FTA-Details')
            if date and place:
                self.doc.write_text(_('%(event_name)s: %(date)s, %(place)s%(endnotes)s') % {
                    'event_name' : event.getName(),
                    'date' : event.getDate(),
                    'endnotes' : self.endnotes(event),
                    'place' : event.getPlaceName() })
            elif date:
                self.doc.write_text(_('%(event_name)s: %(date)s%(endnotes)s') % {
                    'event_name' : event.getName(),
                    'endnotes' : self.endnotes(event),
                    'date' : event.getDate()})
            else:
                self.doc.write_text(_('%(event_name)s: %(place)s%(endnotes)s') % {
                    'event_name' : event.getName(),
                    'endnotes' : self.endnotes(event),
                    'place' : event.getPlaceName() })
            self.doc.end_paragraph()

    def print_spouse(self,person):
        family_list = person.getFamilyList()
        if not family_list:
            return
        family = family_list[0]
        if family.getFather() == person:
            spouse = family.getMother()
        else:
            spouse = family.getFather()
        if not spouse:
            return
        event = family.getMarriage()
        if not event:
            return
        date = event.getDate()
        place = event.getPlaceName()

        if date and place:
            if person.getGender() == RelLib.Person.male:
                self.doc.write_text(_('He married %(spouse)s %(date)s in %(place)s%(endnotes)s.') % {
                    'spouse' : spouse.getPrimaryName().getRegularName(),
                    'endnotes' : self.endnotes(event),
                    'date' : date,
                    'place' : place})
            else:
                self.doc.write_text(_('She married %(spouse)s %(date)s in %(place)s%(endnotes)s.') % {
                    'spouse' : spouse.getPrimaryName().getRegularName(),
                    'date' : date,
                    'endnotes' : self.endnotes(event),
                    'place' : place})
        elif date:
            if person.getGender() == RelLib.Person.male:
                self.doc.write_text(_('He married %(spouse)s %(date)s%(endnotes)s.') % {
                    'spouse' : spouse.getPrimaryName().getRegularName(),
                    'endnotes' : self.endnotes(event),
                    'date' : date,})
            else:
                self.doc.write_text(_('She married %(spouse)s in %(place)s%(endnotes)s.') % {
                    'spouse' : spouse.getPrimaryName().getRegularName(),
                    'endnotes' : self.endnotes(event),
                    'place' : place,})
        elif place:
            if person.getGender() == RelLib.Person.male:
                self.doc.write_text(_('He married %(spouse)s in %(place)s%(endnotes)s.') % {
                    'spouse' : spouse.getPrimaryName().getRegularName(),
                    'endnotes' : self.endnotes(event),
                    'place' : place})
            else:
                self.doc.write_text(_('She married %(spouse)s in %(place)s%(endnotes)s.') % {
                    'spouse' : spouse.getPrimaryName().getRegularName(),
                    'endnotes' : self.endnotes(event),
                    'place' : place})
        else:
            if person.getGender() == RelLib.Person.male:
                self.doc.write_text(_('He married %(spouse)s%(endnotes)s.') % {
                    'spouse' : spouse.getPrimaryName().getRegularName(),
                    'endnotes' : self.endnotes(event),
                    })
            else:
                self.doc.write_text(_('She married %(spouse)s%(endnotes)s.') % {
                    'spouse' : spouse.getPrimaryName().getRegularName(),
                    'endnotes' : self.endnotes(event),
                    })
        self.doc.write_text(' ')

        death = spouse.getDeath()
        dplace = death.getPlaceName()
        ddate = death.getDate()
        
        birth = spouse.getBirth()
        bplace = birth.getPlaceName()
        bdate = birth.getDate()
        
        death_valid = ddate != "" or dplace != ""
        birth_valid = bdate != "" or bplace != ""

        if birth_valid or death_valid:
            if spouse.getGender() == RelLib.Person.male:
                if bdate:
                    if bplace:
                        if ddate:
                            if dplace:
                                self.doc.write_text(_("%(male_name)s%(endnotes)s was born %(birth_date)s in %(birth_place)s"
                                                      "%(birth_endnotes)s, "
                                                      "and died %(death_date)s in %(death_place)s"
                                                      "%(death_endnotes)s.") % {
                                    'male_name' : _('He'), 'endnotes' : '',
                                    'birth_date' : bdate, 'birth_place' : bplace,
                                    'death_date' : ddate,'death_place' : dplace,
                                    'birth_endnotes' : self.endnotes(birth),
                                    'death_endnotes' : self.endnotes(death),
                                    })
                            else:
                                self.doc.write_text(_("%(male_name)s%(endnotes)s was born %(birth_date)s in %(birth_place)s"
                                                      "%(birth_endnotes)s, "
                                                      "and died %(death_date)s%(death_endnotes)s.") % {
                                    'male_name' : _('He'), 'endnotes' : '',
                                    'birth_date' : bdate, 'birth_place' : bplace,
                                    'death_date' : ddate,
                                    'birth_endnotes' : self.endnotes(birth),
                                    'death_endnotes' : self.endnotes(death),                                    
                                    })
                        else:
                            if dplace:
                                self.doc.write_text(_("%(male_name)s%(endnotes)s was born %(birth_date)s in %(birth_place)s"
                                                      "%(birth_endnotes)s, "
                                                      "and died in %(death_place)s%(death_endnotes)s.") % {
                                    'male_name' : _('He'), 'endnotes' : '',
                                    'birth_date' : bdate, 'birth_place' : bplace,
                                    'birth_endnotes' : self.endnotes(birth),
                                    'death_endnotes' : self.endnotes(death),
                                    'death_place' : dplace,
                                    })
                            else:
                                self.doc.write_text(_("%(male_name)s%(endnotes)s was born %(birth_date)s in "
                                                      "%(birth_place)s%(birth_endnotes)s. ") % {
                                    'male_name' : _('He'), 'endnotes' : '',
                                    'birth_date' : bdate, 'birth_place' : bplace,
                                    'birth_endnotes' : self.endnotes(birth),
                                    })
                    else:
                        if ddate:
                            if dplace:
                                self.doc.write_text(_("%(male_name)s%(endnotes)s was born %(birth_date)s%(birth_endnotes)s, "
                                                      "and died %(death_date)s in %(death_place)s"
                                                      "%(death_endnotes)s.") % {
                                    'male_name' : _('He'), 'endnotes' : '',
                                    'birth_date' : bdate, 'death_date' : ddate,
                                    'death_place' : dplace,
                                    'birth_endnotes' : self.endnotes(birth),
                                    'death_endnotes' : self.endnotes(death),
                                    })
                            else:
                                self.doc.write_text(_("%(male_name)s%(endnotes)s was born %(birth_date)s%(birth_endnotes)s, "
                                                      "and died %(death_date)s%(death_endnotes)s.") % {
                                    'male_name' : _('He'), 'endnotes' : '',
                                    'birth_date' : bdate, 'death_date' : ddate,
                                    'birth_endnotes' : self.endnotes(birth),
                                    'death_endnotes' : self.endnotes(death),
                                    })
                        else:
                            if dplace:
                                self.doc.write_text(_("%(male_name)s%(endnotes)s was born %(birth_date)s%(birth_endnotes)s, "
                                                      "and died in %(death_place)s%(death_endnotes)s.") % {
                                    'male_name' : _('He'), 'endnotes' : '',
                                    'birth_date' : bdate, 'death_place' : dplace,
                                    'birth_endnotes' : self.endnotes(birth),
                                    'death_endnotes' : self.endnotes(death),
                                    })
                            else:
                                self.doc.write_text(_("%(male_name)s%(endnotes)s was born %(birth_date)s%(birth_endnotes)s. ") % {
                                    'male_name' : _('He'), 'endnotes' : '',
                                    'birth_date' : bdate,
                                    'birth_endnotes' : self.endnotes(birth),
                                    })
                else:
                    if bplace:
                        if ddate:
                            if dplace:
                                self.doc.write_text(_("%(male_name)s%(endnotes)s was born in %(birth_place)s%(birth_endnotes)s, "
                                                      "and died %(death_date)s in %(death_place)s"
                                                      "%(death_endnotes)s.") % {
                                    'male_name' : _('He'), 'endnotes' : '',
                                    'birth_place' : bplace, 'death_date' : ddate, 'death_place' : dplace,
                                    'birth_endnotes' : self.endnotes(birth),
                                    'death_endnotes' : self.endnotes(death),
                                    })
                            else:
                                self.doc.write_text(_("%(male_name)s%(endnotes)s was born in %(birth_place)s%(birth_endnotes)s, "
                                                      "and died %(death_date)s%(death_endnotes)s.") % {
                                    'male_name' : _('He'), 'endnotes' : '',
                                    'birth_endnotes' : self.endnotes(birth),
                                    'death_endnotes' : self.endnotes(death),
                                    'birth_place' : bplace, 'death_date' : ddate,
                                    })
                        else:
                            if dplace:
                                self.doc.write_text(_("%(male_name)s%(endnotes)s was born in %(birth_place)s%(birth_endnotes)s, "
                                                      "and died in %(death_place)s%(death_endnotes)s.") % {
                                    'male_name' : _('He'), 'endnotes' : '',
                                    'birth_place' : bplace,'death_place' : dplace,
                                    'birth_endnotes' : self.endnotes(birth),
                                    'death_endnotes' : self.endnotes(death),
                                    })
                            else:
                                self.doc.write_text(_("%(male_name)s%(endnotes)s was born in %(birth_place)s%(birth_endnotes)s. ") % {
                                    'male_name' : _('He'), 'endnotes' : '',
                                    'birth_place' : bplace,
                                    'birth_endnotes' : self.endnotes(birth),
                                    })
                    else:
                        if ddate:
                            if dplace:
                                self.doc.write_text(_("%(male_name)s%(endnotes)s died %(death_date)s in "
                                                      "%(death_place)s%(death_endnotes)s.") % {
                                    'male_name' : _('He'), 'endnotes' : '',
                                    'death_date' : ddate, 'death_place' : dplace,
                                    'death_endnotes' : self.endnotes(death),
                                    })
                            else:
                                self.doc.write_text(_("%(male_name)s%(endnotes)s died %(death_date)s%(death_endnotes)s.") % {
                                    'male_name' : _('He'), 'endnotes' : '',
                                    'death_date' : ddate,
                                    'death_endnotes' : self.endnotes(death),
                                    })
                        else:
                            if dplace:
                                self.doc.write_text(_("%(male_name)s%(endnotes)s died in %(death_place)s%(death_endnotes)s.") % {
                                    'male_name' : _('He'), 'endnotes' : '',
                                    'death_endnotes' : self.endnotes(death),
                                    'death_place' : dplace,
                                    })
            else:
                if bdate:
                    if bplace:
                        if ddate:
                            if dplace:
                                self.doc.write_text(_("%(female_name)s%(endnotes)s was born %(birth_date)s in %(birth_place)s"
                                                      "%(birth_endnotes)s, "
                                                      "and died %(death_date)s in %(death_place)s"
                                                      "%(death_endnotes)s.") % {
                                    'female_name' : _('She'), 'endnotes' : '',
                                    'birth_date' : bdate, 'birth_place' : bplace,
                                    'death_date' : ddate,'death_place' : dplace,
                                    'birth_endnotes' : self.endnotes(birth),
                                    'death_endnotes' : self.endnotes(death),
                                    })
                            else:
                                self.doc.write_text(_("%(female_name)s%(endnotes)s was born %(birth_date)s in %(birth_place)s"
                                                      "%(birth_endnotes)s, "
                                                      "and died %(death_date)s%(death_endnotes)s.") % {
                                    'female_name' : _('She'), 'endnotes' : '',
                                    'birth_date' : bdate, 'birth_place' : bplace,
                                    'birth_endnotes' : self.endnotes(birth),
                                    'death_endnotes' : self.endnotes(death),
                                    'death_date' : ddate,
                                    })
                        else:
                            if dplace:
                                self.doc.write_text(_("%(female_name)s%(endnotes)s was born %(birth_date)s in %(birth_place)s"
                                                      "%(birth_endnotes)s, "
                                                      "and died in %(death_place)s%(death_endnotes)s.") % {
                                    'female_name' : _('She'), 'endnotes' : '',
                                    'birth_date' : bdate, 'birth_place' : bplace,
                                    'death_place' : dplace,
                                    'birth_endnotes' : self.endnotes(birth),
                                    'death_endnotes' : self.endnotes(death),
                                    })
                            else:
                                self.doc.write_text(_("%(female_name)s%(endnotes)s was born %(birth_date)s in %(birth_place)s"
                                                      "%(birth_endnotes)s. ") % {
                                    'female_name' : _('She'), 'endnotes' : '',
                                    'birth_endnotes' : self.endnotes(birth),
                                    'birth_date' : bdate, 'birth_place' : bplace,
                                    })
                    else:
                        if ddate:
                            if dplace:
                                self.doc.write_text(_("%(female_name)s%(endnotes)s was born %(birth_date)s%(birth_endnotes)s, "
                                                      "and died %(death_date)s in %(death_place)s"
                                                      "%(death_endnotes)s.") % {
                                    'female_name' : _('She'), 'endnotes' : '',
                                    'birth_date' : bdate, 'death_date' : ddate,
                                    'birth_endnotes' : self.endnotes(birth),
                                    'death_endnotes' : self.endnotes(death),
                                    'death_place' : dplace,
                                    })
                            else:
                                self.doc.write_text(_("%(female_name)s%(endnotes)s was born %(birth_date)s%(birth_endnotes)s, "
                                                      "and died %(death_date)s%(death_endnotes)s.") % {
                                    'female_name' : _('She'), 'endnotes' : '',
                                    'birth_endnotes' : self.endnotes(birth),
                                    'death_endnotes' : self.endnotes(death),
                                    'birth_date' : bdate, 'death_date' : ddate,
                                    })
                        else:
                            if dplace:
                                self.doc.write_text(_("%(female_name)s%(endnotes)s was born %(birth_date)s%(birth_endnotes)s, "
                                                      "and died in %(death_place)s%(death_endnotes)s.") % {
                                    'female_name' : _('She'), 'endnotes' : '',
                                    'birth_endnotes' : self.endnotes(birth),
                                    'death_endnotes' : self.endnotes(death),
                                    'birth_date' : bdate, 'death_place' : dplace,
                                    })
                            else:
                                self.doc.write_text(_("%(female_name)s%(endnotes)s was born %(birth_date)s%(birth_endnotes)s. ") % {
                                    'female_name' : _('She'), 'endnotes' : '',
                                    'birth_endnotes' : self.endnotes(birth),
                                    'birth_date' : bdate,
                                    })
                else:
                    if bplace:
                        if ddate:
                            if dplace:
                                self.doc.write_text(_("%(female_name)s%(endnotes)s was born in %(birth_place)s%(birth_endnotes)s, "
                                                      "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                                    'female_name' : _('She'), 'endnotes' : '',
                                    'birth_endnotes' : self.endnotes(birth),
                                    'death_endnotes' : self.endnotes(death),
                                    'birth_place' : bplace, 'death_date' : ddate, 'death_place' : dplace,
                                    })
                            else:
                                self.doc.write_text(_("%(female_name)s%(endnotes)s was born in %(birth_place)s%(birth_endnotes)s, "
                                                      "and died %(death_date)s%(death_endnotes)s.") % {
                                    'female_name' : _('She'), 'endnotes' : '',
                                    'birth_endnotes' : self.endnotes(birth),
                                    'death_endnotes' : self.endnotes(death),
                                    'birth_place' : bplace, 'death_date' : ddate,
                                    })
                        else:
                            if dplace:
                                self.doc.write_text(_("%(female_name)s%(endnotes)s was born in %(birth_place)s%(birth_endnotes)s, "
                                                      "and died in %(death_place)s%(death_endnotes)s.") % {
                                    'female_name' : _('She'), 'endnotes' : '',
                                    'birth_endnotes' : self.endnotes(birth),
                                    'death_endnotes' : self.endnotes(death),
                                    'birth_place' : bplace,'death_place' : dplace,
                                    })
                            else:
                                self.doc.write_text(_("%(female_name)s%(endnotes)s was born in %(birth_place)s%(birth_endnotes)s. ") % {
                                    'female_name' : _('She'), 'endnotes' : '',
                                    'birth_endnotes' : self.endnotes(birth),
                                    'birth_place' : bplace,
                                    })
                    else:
                        if ddate:
                            if dplace:
                                self.doc.write_text(_("%(female_name)s%(endnotes)s died %(death_date)s in "
                                                      "%(death_place)s%(death_endnotes)s.") % {
                                    'female_name' : _('She'), 'endnotes' : '',
                                    'death_endnotes' : self.endnotes(death),
                                    'death_date' : ddate, 'death_place' : dplace,
                                    })
                            else:
                                self.doc.write_text(_("%(female_name)s%(endnotes)s died %(death_date)s%(death_endnotes)s.") % {
                                    'female_name' : _('She'), 'endnotes' : '',
                                    'death_endnotes' : self.endnotes(death),
                                    'death_date' : ddate,
                                    })
                        else:
                            if dplace:
                                self.doc.write_text(_("%(female_name)s%(endnotes)s died in %(death_place)s%(death_endnotes)s.") % {
                                    'female_name' : _('She'), 'endnotes' : '',
                                    'death_endnotes' : self.endnotes(death),
                                    'birth_date' : bdate, 'death_place' : dplace,
                                    })
                 
            self.doc.write_text(' ')
        self.print_parents(spouse,death_valid)


    def print_parents(self,person,dead):
        family = person.getMainParents()
        if family:
            mother = family.getMother()
            father = family.getFather()
            if person.getGender() == RelLib.Person.male:
                if mother and father:
                    if dead:
                        self.doc.write_text(_("He was the son of %(father)s and %(mother)s.") % {
                            'father' : father.getPrimaryName().getRegularName(),
                            'mother' : mother.getPrimaryName().getRegularName(), })
                    else:
                        self.doc.write_text(_("He is the son of %(father)s and %(mother)s.") % {
                            'father' : father.getPrimaryName().getRegularName(),
                            'mother' : mother.getPrimaryName().getRegularName(), })
                elif mother:
                    if dead:
                        self.doc.write_text(_("He was the son of %(mother)s.") % {
                            'mother' : mother.getPrimaryName().getRegularName(), })
                    else:
                        self.doc.write_text(_("He is the son of %(mother)s.") % {
                            'mother' : mother.getPrimaryName().getRegularName(), })
                elif father:
                    if dead:
                        self.doc.write_text(_("He was the son of %(father)s.") % {
                            'father' : father.getPrimaryName().getRegularName(), })
                    else:
                        self.doc.write_text(_("He is the son of %(father)s.") % {
                            'father' : father.getPrimaryName().getRegularName(), })
            else:
                if mother and father:
                    if dead:
                        self.doc.write_text(_("She was the daughter of %(father)s and %(mother)s.") % {
                            'father' : father.getPrimaryName().getRegularName(),
                            'mother' : mother.getPrimaryName().getRegularName(), })
                    else:
                        self.doc.write_text(_("She is the daughter of %(father)s and %(mother)s.") % {
                            'father' : father.getPrimaryName().getRegularName(),
                            'mother' : mother.getPrimaryName().getRegularName(), })
                elif mother:
                    if dead:
                        self.doc.write_text(_("She was the daughter of %(mother)s.") % {
                            'mother' : mother.getPrimaryName().getRegularName(), })
                    else:
                        self.doc.write_text(_("She is the daughter of %(mother)s.") % {
                            'mother' : mother.getPrimaryName().getRegularName(), })
                elif father:
                    if dead:
                        self.doc.write_text(_("She was the daughter of %(father)s.") % {
                            'father' : father.getPrimaryName().getRegularName(), })
                    else:
                        self.doc.write_text(_("She is the daughter of %(father)s.") % {
                            'father' : father.getPrimaryName().getRegularName(), })
            self.doc.write_text(' ');


def _make_default_style(default_style):
    """Make the default output style for the FTM Style Ancestral report."""
    font = BaseDoc.FontStyle()
    font.set(face=BaseDoc.FONT_SANS_SERIF,size=16,bold=1,italic=1)
    para = BaseDoc.ParagraphStyle()
    para.set_font(font)
    para.set_header_level(1)
    para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
    para.set(pad=0.5)
    para.set_description(_('The style used for the title of the page.'))
    default_style.add_style("FTA-Title",para)
    
    font = BaseDoc.FontStyle()
    font.set(face=BaseDoc.FONT_SANS_SERIF,size=14,italic=1)
    para = BaseDoc.ParagraphStyle()
    para.set_font(font)
    para.set_header_level(2)
    para.set(pad=0.5)
    para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
    para.set_description(_('The style used for the generation header.'))
    default_style.add_style("FTA-Generation",para)
    
    para = BaseDoc.ParagraphStyle()
    para.set(first_indent=-1.0,lmargin=1.0,pad=0.25)
    para.set_description(_('The basic style used for the text display.'))
    default_style.add_style("FTA-Entry",para)

    para = BaseDoc.ParagraphStyle()
    para.set(lmargin=1.0,pad=0.05)
    para.set_description(_('The basic style used for the text display.'))
    default_style.add_style("FTA-Details",para)

    para = BaseDoc.ParagraphStyle()
    para.set(lmargin=1.0,pad=0.25)
    para.set_description(_('The basic style used for the text display.'))
    default_style.add_style("FTA-SubEntry",para)

    para = BaseDoc.ParagraphStyle()
    para.set(pad=0.05)
    para.set_description(_('The basic style used for the text display.'))
    default_style.add_style("FTA-Endnotes",para)


#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class FtmAncestorReportDialog(Report.TextReportDialog):

    report_options = {}

    def __init__(self,database,person):
        Report.TextReportDialog.__init__(self,database,person,self.report_options)

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def get_title(self):
        """The window title for this dialog"""
        return "%s - %s - GRAMPS" % (_("FTM Style Ancestral Report"),_("Text Reports"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("FTM Style Ancestral Report for %s") % name

    def get_target_browser_title(self):
        """The title of the window created when the 'browse' button is
        clicked in the 'Save As' frame."""
        return _("Save Ancestor Report")

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return "ftm_ancestor_report.xml"
    
    def make_default_style(self):
        _make_default_style(self.default_style)

    def make_report(self):
        """Create the object that will produce the FTM Style Ancestral Report.
        All user dialog has already been handled and the output file
        opened."""
        try:
            MyReport = FtmAncestorReport(self.db, self.person,
                self.max_gen, self.pg_brk, self.doc, self.target_path)
            MyReport.write_report()
        except Errors.ReportError, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)
        except Errors.FilterError, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)
        except:
            import DisplayTrace
            DisplayTrace.DisplayTrace()

#------------------------------------------------------------------------
#
# Standalone report function
#
#------------------------------------------------------------------------
def report(database,person):
    FtmAncestorReportDialog(database,person)

#------------------------------------------------------------------------
#
# Set up sane defaults for the book_item
#
#------------------------------------------------------------------------
_style_file = "ftm_ancestor_report.xml"
_style_name = "default" 

_person_id = ""
_max_gen = 10
_pg_brk = 0
_options = ( _person_id, _max_gen, _pg_brk )

#------------------------------------------------------------------------
#
# Book Item Options dialog
#
#------------------------------------------------------------------------
class FtmAncestorBareReportDialog(Report.BareReportDialog):

    def __init__(self,database,person,opt,stl):

        self.options = opt
        self.db = database
        if self.options[0]:
            self.person = self.db.getPerson(self.options[0])
        else:
            self.person = person
        self.style_name = stl

        Report.BareReportDialog.__init__(self,database,self.person)

        self.max_gen = int(self.options[1]) 
        self.pg_brk = int(self.options[2])
        self.new_person = None

        self.generations_spinbox.set_value(self.max_gen)
        self.pagebreak_checkbox.set_active(self.pg_brk)
        
        self.window.run()

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def make_default_style(self):
        _make_default_style(self.default_style)

    def get_title(self):
        """The window title for this dialog"""
        return "%s - GRAMPS Book" % (_("FTM Style Ancestor Report"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("FTM Style Ancestor Report for GRAMPS Book") 

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return _style_file
    
    def on_cancel(self, obj):
        pass

    def on_ok_clicked(self, obj):
        """The user is satisfied with the dialog choices. Parse all options
        and close the window."""

        # Preparation
        self.parse_style_frame()
        self.parse_report_options_frame()
        
        if self.new_person:
            self.person = self.new_person
        self.options = ( self.person.getId(), self.max_gen, self.pg_brk )
        self.style_name = self.selected_style.get_name() 
   

#------------------------------------------------------------------------
#
# Function to write Book Item 
#
#------------------------------------------------------------------------
def write_book_item(database,person,doc,options,newpage=0):
    """Write the FTM Style Ancestor Report options set.
    All user dialog has already been handled and the output file opened."""
    try:
        if options[0]:
            person = database.getPerson(options[0])
        max_gen = int(options[1])
        pg_brk = int(options[2])
        return FtmAncestorReport(database, person, max_gen, pg_brk, doc, None, newpage )
    except Errors.ReportError, msg:
        (m1,m2) = msg.messages()
        ErrorDialog(m1,m2)
    except Errors.FilterError, msg:
        (m1,m2) = msg.messages()
        ErrorDialog(m1,m2)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_xpm_image():
    return [
        "48 48 33 1",
        " 	c None",
        ".	c #1A1A1A",
        "+	c #847B6E",
        "@	c #B7AC9C",
        "#	c #D1D1D0",
        "$	c #EEE2D0",
        "%	c #6A655C",
        "&	c #868686",
        "*	c #F1EADF",
        "=	c #5C5854",
        "-	c #B89C73",
        ";	c #E2C8A1",
        ">	c #55524C",
        ",	c #F5EEE6",
        "'	c #4F4E4C",
        ")	c #A19C95",
        "!	c #B3966E",
        "~	c #CDC8BF",
        "{	c #F6F2ED",
        "]	c #A6A5A4",
        "^	c #413F3F",
        "/	c #D8D1C5",
        "(	c #968977",
        "_	c #BAB9B6",
        ":	c #FAFAF9",
        "<	c #BEA27B",
        "[	c #E9DAC2",
        "}	c #9D9385",
        "|	c #E4E3E3",
        "1	c #7A7062",
        "2	c #E6D3B4",
        "3	c #BAA488",
        "4	c #322E2B",
        "                                                ",
        "                                                ",
        "             (+(+++++111%1%%%%===%1             ",
        "             +______________@_@)&==1            ",
        "             +_::::::::::::::*|#_&&}>           ",
        "             &_:::::::::::::::{|#]1~}^          ",
        "             +_::::::::::::::::{|#=|~&4         ",
        "             +_::::]]]]]]]]:::::|{':|~&4        ",
        "             +_::::::::::::::::::{'::|~&4       ",
        "             +_:::::::::::::::::::'*::|~&^      ",
        "             +_:::::::::::::::::::'|*::|~}>     ",
        "             1_::::]]]]]]]]]]]]:::'~|{::|_}%    ",
        "             1_:::::::::::::::::::'..4^'=1+%1   ",
        "             +_::::]]]]]]]]]]]]:::|__])&+%=^%   ",
        "             1_::::::::::::::::::::|#__)&&+'^   ",
        "             1_::::]]]]]]]]]::::::::|#~_])&%^   ",
        "             1_::::::::::::::::::::{||#~_])14   ",
        "             1_::::]]]]]]]]]]]]]]]]]]&}#~_]+4   ",
        "             1_::::::::::::::::::{{{{||#~~@&4   ",
        "             %_::::]]]]]]]]]]]]]]]])))}(~~~&4   ",
        "             %_:::::::::::::::::{{{{{*|#/~_(4   ",
        "             %_::::]]]]]]]]]]]]]]])))))}2;/}4   ",
        "             %_:::::::::::::::{{{{{***||[#~}4   ",
        "             %_::::]]]]]]]]]])]))))))))}2/;)4   ",
        "             %_::::::::::::::{{{{{**|$$[/2~!4   ",
        "             %_::::]]]]]]]]){{{{******$$[2/}4   ",
        "             %_::::::::::::{{{{****$$$$$[2/!4   ",
        "             =_::::]]]]]]])]))))))))})}}[2/!4   ",
        "             %_:::::::::{{{{{{**|$$$$$$[[2;)4   ",
        "             =_::::]]]])]]))))))))))}}}}[22!4   ",
        "             %_::::::::{{{{{|**|$$[$[[[[[22}4   ",
        "             =_::::]]])])))))))))}}}}}}}222-4   ",
        "             =_:::::{{{{{|{*|$$$$$[[[[22222!4   ",
        "             =_::::)]])))))))))}}}}}}(}(2;2-4   ",
        "             =_:::{{{{{{***|$$$$$[[[[22222;-4   ",
        "             =_:::{])))))))))}}}}}}}(}((2;;<4   ",
        "             >_:{{{{{{**|$$$$$[[[[22222;2;;-4   ",
        "             >_{{{{)))))))}}}}}}}(!(((((;;;-4   ",
        "             >_{{{{|**|*$$$$$[[[[22222;;;;;!4   ",
        "             '_{{{{****$$$$$2[[222222;2;;;;-4   ",
        "             '@{{****$$$$$[[[2[222;;2;;;;;;!4   ",
        "             >]{******$$$[$[2[[2222;;;;;;;;!4   ",
        "             '_****$$$$[$[[[[2222;2;;;;;;;;!4   ",
        "             '@__@@@@@@@33<3<<<<<<-<-!!!!!!!4   ",
        "             44444444444444444444444444444444   ",
        "                                                ",
        "                                                ",
        "                                                "]

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_report, register_book_item

register_report(
    report,
    _("FTM Style Ancestor Report"),
    category=_("Text Reports"),
    status=(_("Beta")),
    description= _("Produces a textual ancestral report similar to Family Tree Maker."),
    xpm=get_xpm_image(),
    author_name="Donald N. Allingham",
    author_email="dallingham@users.sourceforge.net"
    )

# (name,category,options_dialog,write_book_item,options,style_name,style_file,make_default_style)
register_book_item( 
    _("FTM Style Ancestor Report"), 
    _("Text"),
    FtmAncestorBareReportDialog,
    write_book_item,
    _options,
    _style_name,
    _style_file,
    _make_default_style
   )

