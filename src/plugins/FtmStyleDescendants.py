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

#
# Written by Alex Roitman, largely based on the FtmStyleAncestors.py
# report by Don Allingham
#

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
import string
import cStringIO

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
import Report
import TextDoc
import RelLib
import Errors
import Utils
from QuestionDialog import ErrorDialog
from intl import gettext as _

#------------------------------------------------------------------------
#
# DescendantReport
#
#------------------------------------------------------------------------
class FtmDescendantReport(Report.Report):

    def __init__(self,database,person,output,max,doc,pgbrk):
        self.anc_map = {}
        self.gen_map = {}
        self.database = database
        self.start = person
        self.max_generations = max
        self.pgbrk = pgbrk
        self.doc = doc
        self.doc.open(output)
        self.sref_map = {}
        self.sref_index = 1
        
    def setup(self):
        tbl = TextDoc.TableStyle()
        tbl.set_width(100)
        tbl.set_columns(3)
        tbl.set_column_width(0,10)
        tbl.set_column_width(1,5)
        tbl.set_column_width(2,85)
        self.doc.add_table_style('ChildTable',tbl)

        cell = TextDoc.TableCellStyle()
        self.doc.add_cell_style('Normal',cell)


    def apply_filter(self,person,index,generation=1):

        if person == None or generation > self.max_generations:
            return

        self.anc_map[index] = person
        try:
            self.gen_map[generation].append(index)
        except:
            self.gen_map[generation] = []
            self.gen_map[generation].append(index)

        for family in person.getFamilyList():
            for child in family.getChildList():
                ix = max(self.anc_map.keys())
                self.apply_filter(child,ix+1,generation+1)


    def write_report(self):
        self.setup()
        self.apply_filter(self.start,1)
        
        name = self.start.getPrimaryName().getRegularName()
        self.doc.start_paragraph("Title")
        title = _("Descendants of %s") % name
        self.doc.write_text(title)
        self.doc.end_paragraph()
    
        generations = self.gen_map.keys()
        generations.sort()

        for generation in generations:
            if self.pgbrk and generation > 0:
                self.doc.page_break()
            self.doc.start_paragraph("Generation")
            t = _("Generation No. %d") % generation
            self.doc.write_text(t)
            self.doc.end_paragraph()

            indexlist = self.gen_map[generation]
            indexlist.sort()
            for key in indexlist:
                person = self.anc_map[key]

                pri_name = person.getPrimaryName()
                self.doc.start_paragraph("Entry","%d." % key)
                name = pri_name.getRegularName()
                self.doc.start_bold()
                self.doc.write_text(name)
                self.doc.end_bold()

                # add source information here

                self.doc.write_text(self.endnotes(pri_name))
                    
                # Check birth record
        
                birth = person.getBirth()
                death = person.getDeath()

                birth_valid = birth.getDate() != "" or birth.getPlaceName() != ""
                death_valid = death.getDate() != "" or death.getPlaceName() != ""

                if birth_valid or death_valid:
                    self.doc.write_text(' ')
                else:
                    self.doc.write_text('.')
            
                if birth_valid:
                    date = birth.getDateObj().get_start_date()
                    place = birth.getPlaceName()
                    if place[-1:] == '.':
                        place = place[:-1]
                    if date.getDate() != "":
                        if place != "":
                            t = _("was born %(date)s in %(place)s%(endnotes)s") % {
                                'date' : date.getDate(),
                                'place' : place,
                                'endnotes' : self.endnotes(birth),
                                }
                        else:
                            t = _("was born %(date)s%(endnotes)s") % {
                                'date' : date.getDate(),
                                'endnotes' : self.endnotes(birth),
                                }
                    else:
                        if place != "":
                            t = _("was born in %(place)s%(endnotes)s") % {
                                'place' : place,
                                'endnotes' : self.endnotes(birth),
                                }
                        else:
                            t = ''

                    self.doc.write_text(t)
                    if death_valid:
                        self.doc.write_text(', ')
                    else:
                        self.doc.write_text('. ')
                    
                if death_valid:
                    date = death.getDateObj().get_start_date()
                    place = death.getPlaceName()
                    if place[-1:] == '.':
                        place = place[:-1]
                    if date.getDate() != "":
                        if place != "":
                            t = _("and died %(date)s in %(place)s%(endnotes)s.") % {
                                'date' : date.getDate(),
                                'place' : place,
                                'endnotes' : self.endnotes(death),
                                }
                        else:
                            t = _("and died %(date)s%(endnotes)s.") % {
                                'date' : date.getDate(),
                                'endnotes' : self.endnotes(death),
                                }
                    else:
                        if place != "":
                            t = _("and died in %(place)s%(endnotes)s.") % {
                                'place' : place,
                                'endnotes' : self.endnotes(death),
                                }
                        else:
                            t = '.'
                    self.doc.write_text(t + ' ')

                self.print_parents(person,death_valid)
                self.print_spouse(person)
                self.doc.end_paragraph()

                self.print_notes(person)
                self.print_more_about(person)
                self.print_more_about_families(person)
                if generation < self.max_generations:
                    self.print_children(person)

        self.write_endnotes()
        self.doc.close()

    def write_endnotes(self):
        keys = self.sref_map.keys()
        if not keys:
            return

        self.doc.start_paragraph('Generation')
        self.doc.write_text('Endnotes')
        self.doc.end_paragraph()
        
        keys.sort()
        for key in keys:
            srcref = self.sref_map[key]
            base = srcref.getBase()
            
            self.doc.start_paragraph('Endnotes',"%d." % key)
            self.doc.write_text(base.getTitle())

            for item in [ base.getAuthor(), base.getPubInfo(), base.getCallNumber(),
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
            first = 0
            for ref in slist:
                if first == 1:
                    msg.write(',')
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
        self.doc.start_paragraph('SubEntry')
        self.doc.write_text(_('Notes for %(person)s:') % { 
            'person' : person.getPrimaryName().getRegularName()} )
        self.doc.end_paragraph()
        for line in note.split('\n'):
            self.doc.start_paragraph('Details')
            self.doc.write_text(line.strip())
            self.doc.end_paragraph()
        
    def print_more_about(self,person):

        first = 1
        ncount = 1
        for name in person.getAlternateNames():
            if first:
                self.doc.start_paragraph('SubEntry')
                self.doc.write_text(_('More about %(person_name)s:') % { 
                   'person_name' : person.getPrimaryName().getRegularName() })
                self.doc.end_paragraph()
                first = 0
            self.doc.start_paragraph('Details')
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
                self.doc.start_paragraph('SubEntry')
                name = person.getPrimaryName().getRegularName()
                self.doc.write_text(_('More about %(person_name)s:') % { 'person_name' : name })
                self.doc.end_paragraph()
                first = 0

            self.doc.start_paragraph('Details')
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


    def print_more_about_families(self,person):
        "More about husband and wife"
        
        first = 1

        for family in person.getFamilyList():
            if family.getFather() and family.getMother():
                husband = family.getFather().getPrimaryName().getRegularName()
                wife = family.getMother().getPrimaryName().getRegularName()
            else:
                continue
            for event in family.getEventList():
                date = event.getDate()
                place = event.getPlace()

                if not date and not place:
                    continue
                if first:
                    self.doc.start_paragraph('SubEntry')
                    self.doc.write_text(_('More about %(husband)s and %(wife)s:') % { 'husband' : husband, 'wife' : wife })
                    self.doc.end_paragraph()
                    first = 0

                self.doc.start_paragraph('Details')
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
                        'place' : event.getPlaceName() })
                self.doc.end_paragraph()


    def print_children(self,person):
        "Children of such-and-such"

        name = person.getPrimaryName().getRegularName()
        
        for family in person.getFamilyList():
            first = 1
        
            if family.getFather() == person:
                spouse = family.getMother()
            else:
                spouse = family.getFather()

            child_index = 0
            for child in family.getChildList():
                child_index = child_index + 1
                child_name = child.getPrimaryName().getRegularName()
                for (ind,p) in self.anc_map.items():
                    if p == child:
                        index = ind

                if first:
                    first = 0
                    self.doc.start_paragraph('SubEntry')
                    if spouse:
                        self.doc.write_text(_('Children of %(person_name)s and %(spouse_name)s are:') % { 
                            'person_name' : name,  'spouse_name' : spouse.getPrimaryName().getRegularName() })
                    else:
                        self.doc.write_text(_('Children of %(person_name)s are:') % { 'person_name' : name })
                    self.doc.end_paragraph()
                    self.doc.start_table(family.getId(),'ChildTable')

                self.doc.start_row()
                self.doc.start_cell('Normal')
                self.doc.start_paragraph('Details')
                self.doc.write_text("%d." % index)
                self.doc.end_paragraph()
                self.doc.end_cell()
                
                self.doc.start_cell('Normal')
                self.doc.start_paragraph('Details')
                self.doc.write_text("%s." % string.lower(Utils.roman(child_index)))
                self.doc.end_paragraph()
                self.doc.end_cell()
                
                self.doc.start_cell('Normal')
                self.doc.start_paragraph('Details')

                death = child.getDeath()
                dplace = death.getPlaceName()
                ddate = death.getDate()
        
                birth = child.getBirth()
                bplace = birth.getPlaceName()
                bdate = birth.getDate()
        
                if child.getGender() == RelLib.Person.male:
                    if bdate:
                        if bplace:
                            if ddate:
                                if dplace:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s "
                                        "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                                        "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                                    'male_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_date' : bdate, 'birth_place' : bplace,
                                    'death_date' : ddate,'death_place' : dplace,
                                    'birth_endnotes' : self.endnotes(birth), 
                                    'death_endnotes' : self.endnotes(death) })
                                else:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s "
                                        "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                                        "and died %(death_date)s%(death_endnotes)s.") % {
                                    'male_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_date' : bdate, 'birth_place' : bplace, 'death_date' : ddate,
                                    'birth_endnotes' : self.endnotes(birth), 
                                    'death_endnotes' : self.endnotes(death) })
                            else:
                                if dplace:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s "
                                        "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                                        "and died in %(death_place)s%(death_endnotes)s.") % {
                                    'male_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_date' : bdate, 'birth_place' : bplace, 'death_place' : dplace,
                                    'birth_endnotes' : self.endnotes(birth), 
                                    'death_endnotes' : self.endnotes(death) })
                                else:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s "
                                        "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s.") % {
                                    'male_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_date' : bdate, 'birth_place' : bplace,
                                    'birth_endnotes' : self.endnotes(birth) })
                        else:
                            if ddate:
                                if dplace:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s "
                                        "was born %(birth_date)s%(birth_endnotes)s, "
                                        "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                                    'male_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_date' : bdate, 
                                    'death_date' : ddate,'death_place' : dplace,
                                    'birth_endnotes' : self.endnotes(birth), 
                                    'death_endnotes' : self.endnotes(death) })
                                else:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s "
                                        "was born %(birth_date)s%(birth_endnotes)s, "
                                        "and died %(death_date)s%(death_endnotes)s.") % {
                                    'male_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_date' : bdate, 'death_date' : ddate,
                                    'birth_endnotes' : self.endnotes(birth), 
                                    'death_endnotes' : self.endnotes(death) })
                            else:
                                if dplace:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s "
                                        "was born %(birth_date)s%(birth_endnotes)s, "
                                        "and died in %(death_place)s%(death_endnotes)s.") % {
                                    'male_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_date' : bdate, 'death_place' : dplace,
                                    'birth_endnotes' : self.endnotes(birth), 
                                    'death_endnotes' : self.endnotes(death) })
                                else:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s "
                                        "was born %(birth_date)s%(birth_endnotes)s.") % {
                                    'male_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_date' : bdate, 'birth_endnotes' : self.endnotes(birth) })
                    else:
                        if bplace:
                            if ddate:
                                if dplace:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s "
                                        "was born in %(birth_place)s%(birth_endnotes)s, "
                                        "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                                    'male_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_place' : bplace,
                                    'death_date' : ddate,'death_place' : dplace,
                                    'birth_endnotes' : self.endnotes(birth), 
                                    'death_endnotes' : self.endnotes(death) })
                                else:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s "
                                        "was born in %(birth_place)s%(birth_endnotes)s, "
                                        "and died %(death_date)s%(death_endnotes)s.") % {
                                    'male_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_place' : bplace, 'death_date' : ddate,
                                    'birth_endnotes' : self.endnotes(birth), 
                                    'death_endnotes' : self.endnotes(death) })
                            else:
                                if dplace:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s "
                                        "was born in %(birth_place)s%(birth_endnotes)s, "
                                        "and died in %(death_place)s%(death_endnotes)s.") % {
                                    'male_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_place' : bplace, 'death_place' : dplace,
                                    'birth_endnotes' : self.endnotes(birth), 
                                    'death_endnotes' : self.endnotes(death) })
                                else:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s "
                                        "was born in %(birth_place)s%(birth_endnotes)s.") % {
                                    'male_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_place' : bplace,
                                    'birth_endnotes' : self.endnotes(birth) })
                        else:
                            if ddate:
                                if dplace:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s "
                                        "died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                                    'male_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'death_date' : ddate, 'death_place' : dplace,
                                    'death_endnotes' : self.endnotes(death) })
                                else:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s "
                                        "died %(death_date)s%(death_endnotes)s.") % {
                                    'male_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'death_date' : ddate,
                                    'death_endnotes' : self.endnotes(death) })
                            else:
                                if dplace:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s "
                                        "died in %(death_place)s%(death_endnotes)s.") % {
                                    'male_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'death_place' : dplace,
                                    'death_endnotes' : self.endnotes(death) })
                                else:
                                    self.doc.write_text(_("%(male_name)s%(endnotes)s.") % {
                                    'male_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()) })
                else:
                    if bdate:
                        if bplace:
                            if ddate:
                                if dplace:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s "
                                        "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                                        "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                                    'female_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_date' : bdate, 'birth_place' : bplace,
                                    'death_date' : ddate,'death_place' : dplace,
                                    'birth_endnotes' : self.endnotes(birth), 
                                    'death_endnotes' : self.endnotes(death) })
                                else:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s "
                                        "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                                        "and died %(death_date)s%(death_endnotes)s.") % {
                                    'female_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_date' : bdate, 'birth_place' : bplace, 'death_date' : ddate,
                                    'birth_endnotes' : self.endnotes(birth), 
                                    'death_endnotes' : self.endnotes(death) })
                            else:
                                if dplace:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s "
                                        "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s, "
                                        "and died in %(death_place)s%(death_endnotes)s.") % {
                                    'female_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_date' : bdate, 'birth_place' : bplace, 'death_place' : dplace,
                                    'birth_endnotes' : self.endnotes(birth), 
                                    'death_endnotes' : self.endnotes(death) })
                                else:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s "
                                        "was born %(birth_date)s in %(birth_place)s%(birth_endnotes)s.") % {
                                    'female_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_date' : bdate, 'birth_place' : bplace,
                                    'birth_endnotes' : self.endnotes(birth) })
                        else:
                            if ddate:
                                if dplace:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s "
                                        "was born %(birth_date)s%(birth_endnotes)s, "
                                        "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                                    'female_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_date' : bdate, 
                                    'death_date' : ddate,'death_place' : dplace,
                                    'birth_endnotes' : self.endnotes(birth), 
                                    'death_endnotes' : self.endnotes(death) })
                                else:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s "
                                        "was born %(birth_date)s%(birth_endnotes)s, "
                                        "and died %(death_date)s%(death_endnotes)s.") % {
                                    'female_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_date' : bdate, 'death_date' : ddate,
                                    'birth_endnotes' : self.endnotes(birth), 
                                    'death_endnotes' : self.endnotes(death) })
                            else:
                                if dplace:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s "
                                        "was born %(birth_date)s%(birth_endnotes)s, "
                                        "and died in %(death_place)s%(death_endnotes)s.") % {
                                    'female_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_date' : bdate, 'death_place' : dplace,
                                    'birth_endnotes' : self.endnotes(birth), 
                                    'death_endnotes' : self.endnotes(death) })
                                else:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s "
                                        "was born %(birth_date)s%(birth_endnotes)s.") % {
                                    'female_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_date' : bdate, 'birth_endnotes' : self.endnotes(birth) })
                    else:
                        if bplace:
                            if ddate:
                                if dplace:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s "
                                        "was born in %(birth_place)s%(birth_endnotes)s, "
                                        "and died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                                    'female_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_place' : bplace,
                                    'death_date' : ddate,'death_place' : dplace,
                                    'birth_endnotes' : self.endnotes(birth), 
                                    'death_endnotes' : self.endnotes(death) })
                                else:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s "
                                        "was born in %(birth_place)s%(birth_endnotes)s, "
                                        "and died %(death_date)s%(death_endnotes)s.") % {
                                    'female_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_place' : bplace, 'death_date' : ddate,
                                    'birth_endnotes' : self.endnotes(birth), 
                                    'death_endnotes' : self.endnotes(death) })
                            else:
                                if dplace:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s "
                                        "was born in %(birth_place)s%(birth_endnotes)s, "
                                        "and died in %(death_place)s%(death_endnotes)s.") % {
                                    'female_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_place' : bplace, 'death_place' : dplace,
                                    'birth_endnotes' : self.endnotes(birth), 
                                    'death_endnotes' : self.endnotes(death) })
                                else:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s "
                                        "was born in %(birth_place)s%(birth_endnotes)s.") % {
                                    'female_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'birth_place' : bplace,
                                    'birth_endnotes' : self.endnotes(birth) })
                        else:
                            if ddate:
                                if dplace:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s "
                                        "died %(death_date)s in %(death_place)s%(death_endnotes)s.") % {
                                    'female_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'death_date' : ddate, 'death_place' : dplace,
                                    'death_endnotes' : self.endnotes(death) })
                                else:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s "
                                        "died %(death_date)s%(death_endnotes)s.") % {
                                    'female_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'death_date' : ddate,
                                    'death_endnotes' : self.endnotes(death) })
                            else:
                                if dplace:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s "
                                        "died in %(death_place)s%(death_endnotes)s.") % {
                                    'female_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()),
                                    'death_place' : dplace,
                                    'death_endnotes' : self.endnotes(death) })
                                else:
                                    self.doc.write_text(_("%(female_name)s%(endnotes)s.") % {
                                    'female_name' : child_name, 'endnotes' : self.endnotes(child.getPrimaryName()) })
                self.doc.end_paragraph()
                self.doc.end_cell()
                self.doc.end_row()

            if not first: 
            	self.doc.end_table()
            first = 1

    
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
                        'endnotes' : self.endnotes(event) })
            else:
                    self.doc.write_text(_('She married %(spouse)s%(endnotes)s.') % {
                        'spouse' : spouse.getPrimaryName().getRegularName(),
                        'endnotes' : self.endnotes(event)})
        self.doc.write_text(' ')

        death = spouse.getDeath()
        dplace = death.getPlaceName()
        ddate = death.getDate()
        
        birth = spouse.getBirth()
        bplace = birth.getPlaceName()
        bdate = birth.getDate()
        
        death_valid = ddate != "" or dplace != ""
        birth_valid = bdate != "" or bplace != ""

        if birth_valid and death_valid:
            if spouse.getGender() == RelLib.Person.male:
                if bdate:
                    if bplace:
                        if ddate:
                            if dplace:
                                self.doc.write_text(_("%(male_name)s%(endnotes)s was born %(birth_date)s "
                                            "in %(birth_place)s%(birth_endnotes)s, "
                                            "and died %(death_date)s in %(death_place)s"
                                            "%(death_endnotes)s.") % {
                                    'male_name' : _('He'), 'endnotes' : '',
                                    'birth_date' : bdate, 'birth_place' : bplace,
                                    'death_date' : ddate,'death_place' : dplace,
                                    'birth_endnotes' : self.endnotes(birth),
                                    'death_endnotes' : self.endnotes(death),
                                    })
                            else:
                                self.doc.write_text(_("%(male_name)s%(endnotes)s was born %(birth_date)s "
                                            "in %(birth_place)s%(birth_endnotes)s, "
                                            "and died %(death_date)s%(death_endnotes)s.") % {
                                    'male_name' : _('He'), 'endnotes' : '',
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
                                    'male_name' : _('He'), 'endnotes' : '',
                                    'birth_date' : bdate, 'birth_place' : bplace,
                                    'birth_endnotes' : self.endnotes(birth),
                                    'death_endnotes' : self.endnotes(death),
                                    'death_place' : dplace,
                                    })
                            else:
                                self.doc.write_text(_("%(male_name)s%(endnotes)s was born %(birth_date)s in "
                                                      "%(birth_place)s%(birth_endnotes)s.") % {
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
                                self.doc.write_text(_("%(male_name)s%(endnotes)s was born "
                                        "%(birth_date)s%(birth_endnotes)s.") % {
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
                                self.doc.write_text(_("%(male_name)s%(endnotes)s was born "
                                            "in %(birth_place)s%(birth_endnotes)s.") % {
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
                                self.doc.write_text(_("%(male_name)s%(endnotes)s "
                                        "died %(death_date)s%(death_endnotes)s.") % {
                                    'male_name' : _('He'), 'endnotes' : '',
                                    'death_date' : ddate,
                                    'death_endnotes' : self.endnotes(death),
                                    })
                        else:
                            if dplace:
                                self.doc.write_text(_("%(male_name)s%(endnotes)s died "
                                            "in %(death_place)s%(death_endnotes)s.") % {
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
                                self.doc.write_text(_("%(female_name)s%(endnotes)s was born %(birth_date)s "
                                                "in %(birth_place)s %(birth_endnotes)s.") % {
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
                                self.doc.write_text(_("%(female_name)s%(endnotes)s was "
                                            "born %(birth_date)s%(birth_endnotes)s.") % {
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
                                self.doc.write_text(_("%(female_name)s%(endnotes)s was born "
                                            "in %(birth_place)s%(birth_endnotes)s.") % {
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
                                self.doc.write_text(_("%(female_name)s%(endnotes)s "
                                                "died %(death_date)s%(death_endotes)s.") % {
                                    'female_name' : _('She'), 'endnotes' : '',
                                    'death_endnotes' : self.endnotes(death),
                                    'death_date' : ddate,
                                    })
                        else:
                            if dplace:
                                self.doc.write_text(_("%(female_name)s%(endnotes)s died "
                                            "in %(death_place)s%(death_endnotes)s.") % {
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


#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class FtmDescendantReportDialog(Report.TextReportDialog):
    def __init__(self,database,person):
        Report.TextReportDialog.__init__(self,database,person)

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def get_title(self):
        """The window title for this dialog"""
        return "%s - %s - GRAMPS" % (_("FTM Style Descendant Report"),_("Text Reports"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("FTM Style Descendant Report for %s") % name

    def get_target_browser_title(self):
        """The title of the window created when the 'browse' button is
        clicked in the 'Save As' frame."""
        return _("Save FTM Style Descendant Report")

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return "ftm_descendant_report.xml"
    
    def make_default_style(self):
        """Make the default output style for the FTM Style Descendant report."""
        font = TextDoc.FontStyle()
        font.set(face=TextDoc.FONT_SANS_SERIF,size=16,bold=1,italic=1)
        para = TextDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set_alignment(TextDoc.PARA_ALIGN_CENTER)
        para.set(pad=0.5)
        para.set_description(_('The style used for the title of the page.'))
        self.default_style.add_style("Title",para)
    
        font = TextDoc.FontStyle()
        font.set(face=TextDoc.FONT_SANS_SERIF,size=14,italic=1)
        para = TextDoc.ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set(pad=0.5)
        para.set_alignment(TextDoc.PARA_ALIGN_CENTER)
        para.set_description(_('The style used for the generation header.'))
        self.default_style.add_style("Generation",para)
    
        para = TextDoc.ParagraphStyle()
        para.set(first_indent=-1.0,lmargin=1.0,pad=0.25)
        para.set_description(_('The basic style used for the text display.'))
        self.default_style.add_style("Entry",para)

        para = TextDoc.ParagraphStyle()
        para.set(lmargin=1.0,pad=0.05)
        para.set_description(_('The basic style used for the text display.'))
        self.default_style.add_style("Details",para)

        para = TextDoc.ParagraphStyle()
        para.set(lmargin=1.0,pad=0.25)
        para.set_description(_('The basic style used for the text display.'))
        self.default_style.add_style("SubEntry",para)

        para = TextDoc.ParagraphStyle()
        para.set(pad=0.05)
        para.set_description(_('The basic style used for the text display.'))
        self.default_style.add_style("Endnotes",para)


    def make_report(self):
        """Create the object that will produce the FTM Style Descendant Report.
        All user dialog has already been handled and the output file
        opened."""
        try:
            MyReport = FtmDescendantReport(self.db, self.person, self.target_path,
                                      self.max_gen, self.doc, self.pg_brk)
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
# 
#
#------------------------------------------------------------------------
def report(database,person):
    FtmDescendantReportDialog(database,person)


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
from Plugins import register_report

register_report(
    report,
    _("FTM Style Descendant Report"),
    category=_("Text Reports"),
    status=(_("Beta")),
    description= _("Produces a textual descendant report similar to Family Tree Maker."),
    xpm=get_xpm_image(),
    author_name="Alex Roitman",
    author_email="shura@alex.neuro.umn.edu"
    )

