#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2004  Donald N. Allingham
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
        self.sref_index = 0
        
    def apply_filter(self,person_handle,index,generation=1):
        if not person_handle or generation >= self.max_generations:
            return
        self.map[index] = (person_handle,generation)

        person = self.database.get_person_from_handle(person_handle)
        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            family = self.database.get_family_from_handle(family_handle)
            self.apply_filter(family.get_father_handle(),index*2,generation+1)
            self.apply_filter(family.get_mother_handle(),(index*2)+1,generation+1)

    def write_report(self):

        if self.newpage:
            self.doc.page_break()

        self.apply_filter(self.start.get_handle(),1)
        
        name = self.start.get_primary_name().get_regular_name()
        self.doc.start_paragraph("FTA-Title")
        title = _("Ancestors of %s") % name
        self.doc.write_text(title)
        self.doc.end_paragraph()
    
        keys = self.map.keys()
        keys.sort()
        old_gen = 0
        for key in keys :
            (person_handle,generation) = self.map[key]
            if old_gen != generation:
                if self.pgbrk and generation > 1:
                    self.doc.page_break()
                self.doc.start_paragraph("FTA-Generation")
                t = _("Generation No. %d") % generation
                self.doc.write_text(t)
                self.doc.end_paragraph()
                old_gen = generation

            person = self.database.get_person_from_handle(person_handle)
            pri_name = person.get_primary_name()
            self.doc.start_paragraph("FTA-Entry","%d." % key)
            name = pri_name.get_regular_name()
            self.doc.start_bold()
            self.doc.write_text(name)
            self.doc.end_bold()

            # Check birth record
        
            birth_handle = person.get_birth_handle()
            if birth_handle:
                birth_valid = 1
                birth = self.database.find_event_from_handle(birth_handle)
                place_handle = birth.get_place_handle()
                if place_handle:
                    bplace = self.database.get_place_from_handle(place_handle).get_title()
                else:
                    bplace = u''
                bdate = birth.get_date()
            else:
                birth_valid = 0
                bplace = u''
                bdate = u''

            death_handle = person.get_death_handle()
            if death_handle:
                death_valid = 1
                death = self.database.find_event_from_handle(death_handle)
                place_handle = death.get_place_handle()
                if place_handle:
                    dplace = self.database.get_place_from_handle(place_handle).get_title()
                else:
                    dplace = u''
                ddate = death.get_date()
            else:
                death_valid = 0
                dplace = u''
                ddate = u''

            if birth_valid or death_valid:
                if person.get_gender() == RelLib.Person.male:
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
            base = self.database.get_source_from_handle(srcref.get_base_handle())
            
            self.doc.start_paragraph('FTA-Endnotes',"%d." % key)
            self.doc.write_text(base.get_title())

            for item in [ base.get_author(), base.get_publication_info(), base.get_abbreviation(),
                          srcref.get_date().get_date(),]:
                if item:
                    self.doc.write_text('; %s' % item)

            item = srcref.get_text()
            if item:
                self.doc.write_text('; ')
                self.doc.write_text(_('Text:'))
                self.doc.write_text(' ')
                self.doc.write_text(item)

            item = srcref.get_comments()
            if item:
                self.doc.write_text('; ')
                self.doc.write_text(_('Comments:'))
                self.doc.write_text(' ')
                self.doc.write_text(item)

            self.doc.write_text('.')
            self.doc.end_paragraph()

    def endnotes(self,obj):
        msg = cStringIO.StringIO()
        slist = obj.get_source_references()
        if slist:
            msg.write('<super>')
            first = 1
            for ref in slist:
                if not first:
                    msg.write(',')
                first = 0
                ref_base = ref.get_base_handle()
                the_key = 0
                for key in self.sref_map.keys():
                    if ref_base == self.sref_map[key].get_base_handle():
                        the_key = key
                        break
                if the_key:
                    msg.write("%d" % the_key)
                else:
                    self.sref_index += 1
                    self.sref_map[self.sref_index] = ref
                    msg.write("%d" % self.sref_index)
            msg.write('</super>')
        str = msg.getvalue()
        msg.close()
        return str

    def print_notes(self,person):
        note = person.get_note()
        if not note.strip():
            return
        self.doc.start_paragraph('FTA-SubEntry')
        self.doc.write_text(_('Notes for %(person)s:') % { 
        	'person' : person.get_primary_name().get_regular_name()} )
        self.doc.end_paragraph()
        format = person.get_note_format()
        self.doc.write_note(note,format,'FTA-Details')
        
    def print_more_about(self,person):

        first = 1
        ncount = 0
        for name in person.get_alternate_names():
            if first:
                self.doc.start_paragraph('FTA-SubEntry')
                self.doc.write_text(_('More about %(person_name)s:') % { 
                	'person_name' : person.get_primary_name().get_regular_name() })
                self.doc.end_paragraph()
                first = 0
            self.doc.start_paragraph('FTA-Details')
            self.doc.write_text(_('Name %(count)d: %(name)s%(endnotes)s') % {
                'count' : ncount, 'name' : name.get_regular_name(),
                'endnotes' : self.endnotes(name),
                })
            self.doc.end_paragraph()
            ncount += 1
            
        for event_handle in person.get_event_list():
            event = self.database.find_event_from_handle(event_handle)
            date = event.get_date()
            place_handle = event.get_place_handle()
            if place_handle:
                place = self.database.get_place_from_handle(place_handle).get_title()
            else:
                place = u''
                
            if not date and not place_handle:
                continue
            if first:
                self.doc.start_paragraph('FTA-SubEntry')
                name = person.get_primary_name().get_regular_name()
                self.doc.write_text(_('More about %(person_name)s:') % { 
                	'person_name' : name })
                self.doc.end_paragraph()
                first = 0

            self.doc.start_paragraph('FTA-Details')
            if date and place:
                self.doc.write_text(_('%(event_name)s: %(date)s, %(place)s%(endnotes)s. ') % {
                    'event_name' : _(event.get_name()),
                    'date' : date,
                    'endnotes' : self.endnotes(event),
                    'place' : place })
            elif date:
                self.doc.write_text(_('%(event_name)s: %(date)s%(endnotes)s. ') % {
                    'event_name' : _(event.get_name()),
                    'endnotes' : self.endnotes(event),
                    'date' : date})
            else:
                self.doc.write_text(_('%(event_name)s: %(place)s%(endnotes)s. ') % {
                    'event_name' : _(event.get_name()),
                    'endnotes' : self.endnotes(event),
                    'place' : place })
            if event.get_description():
                self.doc.write_text(event.get_description())
            self.doc.end_paragraph()

    def print_spouse(self,person):
        family_list = person.get_family_handle_list()
        if not family_list:
            return
        family_handle = family_list[0]
        family = self.database.get_family_from_handle(family_handle)
        if family.get_father_handle() == person.get_handle():
            spouse_id = family.get_mother_handle()
        else:
            spouse_id = family.get_father_handle()
        if not spouse_id:
            return
        spouse = self.database.get_person_from_handle(spouse_id)
        spouse_name = spouse.get_primary_name().get_regular_name()

        for event_handle in family.get_event_list():
            if event_handle:
                event = self.database.find_event_from_handle(event_handle)
                if event.get_name() == "Marriage":
                    break
        else:
            return

        date = event.get_date()
        place_handle = event.get_place_handle()
        if place_handle:
            place = self.database.get_place_from_handle(place_handle).get_title()
        else:
            place = u''

        if date and place:
            if person.get_gender() == RelLib.Person.male:
                self.doc.write_text(_('He married %(spouse)s %(date)s in %(place)s%(endnotes)s.') % {
                    'spouse' : spouse_name,
                    'endnotes' : self.endnotes(event),
                    'date' : date,
                    'place' : place})
            else:
                self.doc.write_text(_('She married %(spouse)s %(date)s in %(place)s%(endnotes)s.') % {
                    'spouse' : spouse_name,
                    'date' : date,
                    'endnotes' : self.endnotes(event),
                    'place' : place})
        elif date:
            if person.get_gender() == RelLib.Person.male:
                self.doc.write_text(_('He married %(spouse)s %(date)s%(endnotes)s.') % {
                    'spouse' : spouse_name,
                    'endnotes' : self.endnotes(event),
                    'date' : date,})
            else:
                self.doc.write_text(_('She married %(spouse)s in %(place)s%(endnotes)s.') % {
                    'spouse' : spouse_name,
                    'endnotes' : self.endnotes(event),
                    'place' : place,})
        elif place:
            if person.get_gender() == RelLib.Person.male:
                self.doc.write_text(_('He married %(spouse)s in %(place)s%(endnotes)s.') % {
                    'spouse' : spouse_name,
                    'endnotes' : self.endnotes(event),
                    'place' : place})
            else:
                self.doc.write_text(_('She married %(spouse)s in %(place)s%(endnotes)s.') % {
                    'spouse' : spouse_name,
                    'endnotes' : self.endnotes(event),
                    'place' : place})
        else:
            if person.get_gender() == RelLib.Person.male:
                self.doc.write_text(_('He married %(spouse)s%(endnotes)s.') % {
                    'spouse' : spouse_name,
                    'endnotes' : self.endnotes(event),
                    })
            else:
                self.doc.write_text(_('She married %(spouse)s%(endnotes)s.') % {
                    'spouse' : spouse_name,
                    'endnotes' : self.endnotes(event),
                    })
        self.doc.write_text(' ')

        death_handle = spouse.get_death_handle()
        if death_handle:
            death_valid = 1
            death = self.database.find_event_from_handle(death_handle)
            ddate = death.get_date()
            place_handle = death.get_place_handle()
            if place_handle:
                dplace = self.database.get_place_from_handle(place_handle).get_title()
            else:
                dplace = u''
        else:
            death_valid = 0
            dplace = u''
            ddate = u''

        birth_handle = spouse.get_birth_handle()
        if birth_handle:
            birth_valid = 1
            birth = self.database.find_event_from_handle(birth_handle)
            bdate = birth.get_date()
            place_handle = birth.get_place_handle()
            if place_handle:
                bplace = self.database.get_place_from_handle(place_handle).get_title()
            else:
                bplace = u''
        else:
            birth_valid = 0
            bplace = u''
            bdate = u''
        
        if birth_valid or death_valid:
            if spouse.get_gender() == RelLib.Person.male:
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
        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            family = self.database.get_family_from_handle(family_handle)
            mother_handle = family.get_mother_handle()
            father_handle = family.get_father_handle()
            if mother_handle:
                mother = self.database.get_person_from_handle(mother_handle)
                mother_name = mother.get_primary_name().get_regular_name()
            if father_handle:
                father = self.database.get_person_from_handle(father_handle)
                father_name = father.get_primary_name().get_regular_name()
                
            if person.get_gender() == RelLib.Person.male:
                if mother_handle and father_handle:
                    if dead:
                        self.doc.write_text(_("He was the son of %(father)s and %(mother)s.") % {
                            'father' : father_name,
                            'mother' : mother_name, })
                    else:
                        self.doc.write_text(_("He is the son of %(father)s and %(mother)s.") % {
                            'father' : father_name,
                            'mother' : mother_name, })
                elif mother_handle:
                    if dead:
                        self.doc.write_text(_("He was the son of %(mother)s.") % {
                            'mother' : mother_name, })
                    else:
                        self.doc.write_text(_("He is the son of %(mother)s.") % {
                            'mother' : mother_name, })
                elif father_handle:
                    if dead:
                        self.doc.write_text(_("He was the son of %(father)s.") % {
                            'father' : father_name, })
                    else:
                        self.doc.write_text(_("He is the son of %(father)s.") % {
                            'father' : father_name, })
            else:
                if mother_handle and father_handle:
                    if dead:
                        self.doc.write_text(_("She was the daughter of %(father)s and %(mother)s.") % {
                            'father' : father_name,
                            'mother' : mother_name, })
                    else:
                        self.doc.write_text(_("She is the daughter of %(father)s and %(mother)s.") % {
                            'father' : father_name,
                            'mother' : mother_name, })
                elif mother_handle:
                    if dead:
                        self.doc.write_text(_("She was the daughter of %(mother)s.") % {
                            'mother' : mother_name, })
                    else:
                        self.doc.write_text(_("She is the daughter of %(mother)s.") % {
                            'mother' : mother_name, })
                elif father_handle:
                    if dead:
                        self.doc.write_text(_("She was the daughter of %(father)s.") % {
                            'father' : father_name, })
                    else:
                        self.doc.write_text(_("She is the daughter of %(father)s.") % {
                            'father' : father_name, })
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

_person_handle = ""
_max_gen = 10
_pg_brk = 0
_options = ( _person_handle, _max_gen, _pg_brk )

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
            self.person = self.db.get_person_from_handle(self.options[0])
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
        self.options = ( self.person.get_handle(), self.max_gen, self.pg_brk )
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
            person = database.get_person_from_handle(options[0])
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
from Plugins import register_report, register_book_item

register_report(
    report,
    _("FTM Style Ancestor Report"),
    category=_("Text Reports"),
    status=(_("Beta")),
    description= _("Produces a textual ancestral report similar to Family Tree Maker."),
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

