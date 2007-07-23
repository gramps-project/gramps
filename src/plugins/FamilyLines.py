#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Stephane Charette
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Pubilc License as published by
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

"""
Family Lines, a plugin for Gramps.
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
import time
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".FamilyLines")

#------------------------------------------------------------------------
#
# GNOME/gtk
#
#------------------------------------------------------------------------
import gtk
import gobject

#------------------------------------------------------------------------
#
# GRAMPS module
#
#------------------------------------------------------------------------
import RelLib
import Config
import Errors
import Utils
import ImgManip
import DateHandler
import GrampsWidgets
import ManagedWindow
from PluginUtils import register_report
from ReportBase import Report, ReportUtils, ReportOptions, CATEGORY_CODE, MODE_GUI, MODE_CLI
from ReportBase._ReportDialog import ReportDialog
from QuestionDialog import ErrorDialog, WarningDialog

#from NameDisplay import displayer as _nd       # Gramps version <  3.0
from BasicUtils import name_displayer as _nd    # Gramps version >= 3.0

from DateHandler import displayer as _dd
from DateHandler import parser
from Selectors import selector_factory

#------------------------------------------------------------------------
#
# FamilyLinesReport -- created once the user presses 'OK' to actually
# go ahead and create the full report
#
#------------------------------------------------------------------------
class FamilyLinesReport(Report):
    def __init__(self, database, person, options):
        """
        Creates FamilyLinesReport object that produces the report.
        
        The arguments are:

        database    - the GRAMPS database instance
        person      - currently selected person
        options     - instance of the Options class for this report
        """

        self.start_person       = person
        self.options            = options
        self.db                 = database
        self.peopleToOutput     = set() # handle of people we need in the report
        self.familiesToOutput   = set() # handle of families we need in the report

        self.deletedPeople      = 0
        self.deletedFamilies    = 0

        self.filename           = options.handler.options_dict['FLfilename'             ]
        self.width              = options.handler.options_dict['FLwidth'                ]
        self.height             = options.handler.options_dict['FLheight'               ]
        self.dpi                = options.handler.options_dict['FLdpi'                  ]
        self.rowSep             = options.handler.options_dict['FLrowSep'               ]
        self.colSep             = options.handler.options_dict['FLcolSep'               ]
        self.direction          = options.handler.options_dict['FLdirection'            ]
        self.ratio              = options.handler.options_dict['FLratio'                ]
        self.followParents      = options.handler.options_dict['FLfollowParents'        ]
        self.followChildren     = options.handler.options_dict['FLfollowChildren'       ]
        self.removeExtraPeople  = options.handler.options_dict['FLremoveExtraPeople'    ]
        self.gidlist            = options.handler.options_dict['FLgidlist'              ]
        self.colourMales        = options.handler.options_dict['FLcolourMales'          ]
        self.colourFemales      = options.handler.options_dict['FLcolourFemales'        ]
        self.colourUnknown      = options.handler.options_dict['FLcolourUnknown'        ]
        self.colourFamilies     = options.handler.options_dict['FLcolourFamilies'       ]
        self.limitParents       = options.handler.options_dict['FLlimitParents'         ]
        self.maxParents         = options.handler.options_dict['FLmaxParents'           ]
        self.limitChildren      = options.handler.options_dict['FLlimitChildren'        ]
        self.maxChildren        = options.handler.options_dict['FLmaxChildren'          ]
        self.includeImages      = options.handler.options_dict['FLincludeImages'        ]
        self.imageOnTheSide     = options.handler.options_dict['FLimageOnTheSide'       ]
        self.includeDates       = options.handler.options_dict['FLincludeDates'         ] 
        self.includePlaces      = options.handler.options_dict['FLincludePlaces'        ]
        self.includeNumChildren = options.handler.options_dict['FLincludeNumChildren'   ]
        self.includeResearcher  = options.handler.options_dict['FLincludeResearcher'    ]
        self.includePrivate     = options.handler.options_dict['FLincludePrivate'       ]

        # the gidlist is annoying for us to use since we always have to convert
        # the GIDs to either Person or to handles, so we may as well convert the
        # entire list right now and not have to deal with it ever again
        self.interestSet = set()
        for gid in self.gidlist.split():
            person = self.db.get_person_from_gramps_id(gid)
            self.interestSet.add(person.get_handle())

        # convert the 'surnameColours' string to a dictionary of names and colours
        self.surnameColours = {}
        tmp = options.handler.options_dict['FLsurnameColours'].split()
        while len(tmp) > 1:
            surname = tmp.pop(0).encode('iso-8859-1','xmlcharrefreplace')
            colour = tmp.pop(0)
            self.surnameColours[surname] = colour


    def write(self, text):
#        self.of.write(text.encode('iso-8859-1', 'strict'))
        self.of.write(text.encode('iso-8859-1','xmlcharrefreplace'))


    def writeDotHeader(self):
        self.write('# Researcher:  %s\n' % Config.get(Config.RESEARCHER_NAME))
        self.write('# Generated on %s\n' % time.strftime('%c')             )
        self.write('# Number of people in database:    %d\n' % self.db.get_number_of_people())
        self.write('# Number of people of interest:    %d\n' % len(self.peopleToOutput))
        self.write('# Number of families in database:  %d\n' % self.db.get_number_of_families())
        self.write('# Number of families of interest:  %d\n' % len(self.familiesToOutput))

        if self.removeExtraPeople:
            self.write('# Additional people removed:       %d\n' % self.deletedPeople)
            self.write('# Additional families removed:     %d\n' % self.deletedFamilies)

        self.write('# Initial list of people of interest:\n')
        for handle in self.interestSet:
            person = self.db.get_person_from_handle(handle)
            name = person.get_primary_name().get_regular_name()
            self.write('#   -> %s\n' % name)
        self.write('\n')

        if self.limitParents:
            self.write('# NOTE:  Option has been set to limit the output to %d parents.\n' % self.maxParents)
            self.write('\n')

        if self.limitParents:
            self.write('# NOTE:  Option has been set to limit the output to %d children.\n' % self.maxChildren)
            self.write('\n')

        self.write('digraph FamilyLines\n'                                      )
        self.write('{\n'                                                        )
        self.write('  bgcolor="white";\n'                                       )
        self.write('  center="true";\n'                                         )
        self.write('  charset="iso-8859-1";\n'                                  )
        self.write('  concentrate="false";\n'                                   )
        self.write('  dpi="%d";\n'                  % self.dpi                  )
        self.write('  graph [fontsize=12];\n'                                   )
        self.write('  mclimit="99";\n'                                          )
        self.write('  nodesep="%.2f";\n'            % self.rowSep               )
        self.write('  outputorder="edgesfirst";\n'                              )
        self.write('  page="%.2f,%.2f";\n'          % (self.width, self.height) )
        self.write('# pagedir="BL";\n'                                          )
        self.write('  rankdir="%s";\n'              % self.direction            )
        self.write('  ranksep="%.2f";\n'            % self.colSep               )
        self.write('  ratio="%s";\n'                % self.ratio                )
        self.write('  rotate="0";\n'                                            )
        self.write('  searchsize="100";\n'                                      )
        self.write('  size="%.2f,%.2f";\n'          % (self.width, self.height) )
        self.write('  splines="true";\n'                                        )
        self.write('\n'                                                         )
        self.write('  edge [len=0.5 style=solid arrowhead=none arrowtail=normal fontsize=12];\n')
        self.write('  node [style=filled fontname="FreeSans" fontsize=12];\n'   )
        self.write('\n'                                                         )


    def writeDotFooter(self):
        if self.includeResearcher:
            name    = Config.get(Config.RESEARCHER_NAME)
            email   = Config.get(Config.RESEARCHER_EMAIL)
            date    = DateHandler.parser.parse(time.strftime('%b %d %Y'))
            label   = ''
            if name:
                label += '%s\\n' % name
            if email:
                label += '%s\\n' % email
            label += '%s' % _dd.display(date)
            self.write('\n')
            self.write('  labelloc="b";\n')
            self.write('  label="%s";\n' % label)

        self.write('}\n')


    def findParents(self):
        # we need to start with all of our "people of interest"
        ancestorsNotYetProcessed = set(self.interestSet)

        # now we find all the immediate ancestors of our people of interest

        while len(ancestorsNotYetProcessed) > 0:
            handle = ancestorsNotYetProcessed.pop()
            self.progress.step()

            # One of 2 things can happen here:
            #   1) we've already know about this person and he/she is already in our list
            #   2) this is someone new, and we need to remember him/her
            #
            # In the first case, there isn't anything else to do, so we simply go back
            # to the top and pop the next person off the list.
            #
            # In the second case, we need to add this person to our list, and then go
            # through all of the parents this person has to find more people of interest.

            if handle not in self.peopleToOutput:

                person = self.db.get_person_from_handle(handle)

                # if this is a private record, and we're not
                # including private records, then go back to the
                # top of the while loop to get the next person
                if person.private and not self.includePrivate:
                    continue

                # remember this person!
                self.peopleToOutput.add(handle)

                # see if a family exists between this person and someone else
                # we have on our list of people we're going to output -- if
                # there is a family, then remember it for when it comes time
                # to link spouses together
                for familyHandle in person.get_family_handle_list():
                    family = self.db.get_family_from_handle(familyHandle)
                    spouseHandle = ReportUtils.find_spouse(person, family)
                    if spouseHandle:
                        if spouseHandle in self.peopleToOutput or spouseHandle in ancestorsNotYetProcessed:
                            self.familiesToOutput.add(familyHandle)

                # if we have a limit on the number of people, and we've
                # reached that limit, then don't attempt to find any
                # more ancestors
                if self.limitParents and (self.maxParents < (len(ancestorsNotYetProcessed) + len(self.peopleToOutput))):
                    # get back to the top of the while loop so we can finish
                    # processing the people queued up in the "not yet processed" list
                    continue

                # queue the parents of the person we're processing
                for familyHandle in person.get_parent_family_handle_list():
                    family = self.db.get_family_from_handle(familyHandle)

                    if (family.private and self.includePrivate) or not family.private:

                        father = self.db.get_person_from_handle(family.get_father_handle())
                        mother = self.db.get_person_from_handle(family.get_mother_handle())
                        if father:
                            if (father.private and self.includePrivate) or not father.private:
                                ancestorsNotYetProcessed.add(family.get_father_handle())
                                self.familiesToOutput.add(familyHandle)
                        if mother:
                            if (mother.private and self.includePrivate) or not mother.private:
                                ancestorsNotYetProcessed.add(family.get_mother_handle())
                                self.familiesToOutput.add(familyHandle)


    def removeUninterestingParents(self):
        # start with all the people we've already identified
        parentsNotYetProcessed = set(self.peopleToOutput)

        while len(parentsNotYetProcessed) > 0:
            handle = parentsNotYetProcessed.pop()
            self.progress.step()
            person = self.db.get_person_from_handle(handle)

            # There are a few things we're going to need,
            # so look it all up right now; such as:
            # - who is the child?
            # - how many children?
            # - parents?
            # - spouse?
            # - is a person of interest?
            # - spouse of a person of interest?
            # - same surname as a person of interest?
            # - spouse has the same surname as a person of interest?

            childHandle = None
            numberOfChildren = 0
            spouseHandle = None
            numberOfSpouse = 0
            fatherHandle = None
            motherHandle = None
            spouseFatherHandle = None
            spouseMotherHandle = None
            spouseSurname = ""
            surname = person.get_primary_name().get_surname().encode('iso-8859-1','xmlcharrefreplace')

            # first we get the person's father and mother
            for familyHandle in person.get_parent_family_handle_list():
                family = self.db.get_family_from_handle(familyHandle)
                handle = family.get_father_handle()
                if handle in self.peopleToOutput:
                    fatherHandle = handle
                handle = family.get_mother_handle()
                if handle in self.peopleToOutput:
                    motherHandle = handle

            # now see how many spouses this person has
            for familyHandle in person.get_family_handle_list():
                family = self.db.get_family_from_handle(familyHandle)
                handle = ReportUtils.find_spouse(person, family)
                if handle in self.peopleToOutput:
                    numberOfSpouse += 1
                    spouse = self.db.get_person_from_handle(handle)
                    spouseHandle = handle
                    spouseSurname = spouse.get_primary_name().get_surname().encode('iso-8859-1','xmlcharrefreplace')

                    # see if the spouse has parents
                    if spouseFatherHandle == None and spouseMotherHandle == None:
                        for familyHandle in spouse.get_parent_family_handle_list():
                            family = self.db.get_family_from_handle(familyHandle)
                            handle = family.get_father_handle()
                            if handle in self.peopleToOutput:
                                spouseFatherHandle = handle
                            handle = family.get_mother_handle()
                            if handle in self.peopleToOutput:
                                spouseMotherHandle = handle

            # get the number of children that we think might be interesting
            for familyHandle in person.get_family_handle_list():
                family = self.db.get_family_from_handle(familyHandle)
                for childRef in family.get_child_ref_list():
                    if childRef.ref in self.peopleToOutput:
                        numberOfChildren += 1
                        childHandle = childRef.ref

            # we now have everything we need -- start looking for reasons
            # why this is a person we need to keep in our list, and loop
            # back to the top as soon as a reason is discovered

            # if this person has many children of interest, then we
            # automatically keep this person
            if numberOfChildren > 1:
                continue

            # if this person has many spouses of interest, then we
            # automatically keep this person
            if numberOfSpouse > 1:
                continue

            # if this person has parents, then we automatically keep
            # this person
            if fatherHandle != None or motherHandle != None:
                continue

            # if the spouse has parents, then we automatically keep
            # this person
            if spouseFatherHandle != None or spouseMotherHandle != None:
                continue;

            # if this is a person of interest, then we automatically keep
            if person.get_handle() in self.interestSet:
                continue;

            # if the spouse is a person of interest, then we keep
            if spouseHandle in self.interestSet:
                continue

            # if the surname (or the spouse's surname) matches a person
            # of interest, then we automatically keep this person
            bKeepThisPerson = False
            for personOfInterestHandle in self.interestSet:
                personOfInterest = self.db.get_person_from_handle(personOfInterestHandle)
                surnameOfInterest = personOfInterest.get_primary_name().get_surname().encode('iso-8859-1','xmlcharrefreplace')
                if surnameOfInterest == surname or surnameOfInterest == spouseSurname:
                    bKeepThisPerson = True
                    break

            if bKeepThisPerson:
                continue

            # if we have a special colour to use for this person,
            # then we automatically keep this person
            if surname in self.surnameColours:
                continue

            # if we have a special colour to use for the spouse,
            # then we automatically keep this person
            if spouseSurname in self.surnameColours:
                continue

            # took us a while, but if we get here, then we can remove this person
            self.deletedPeople += 1
            self.peopleToOutput.remove(person.get_handle())

            # we can also remove any families to which this person belonged
            for familyHandle in person.get_family_handle_list():
                if familyHandle in self.familiesToOutput:
                    self.deletedFamilies += 1
                    self.familiesToOutput.remove(familyHandle)

            # if we have a spouse, then ensure we queue up the spouse
            if spouseHandle:
                if spouseHandle not in parentsNotYetProcessed:
                    parentsNotYetProcessed.add(spouseHandle)

            # if we have a child, then ensure we queue up the child
            if childHandle:
                if childHandle not in parentsNotYetProcessed:
                    parentsNotYetProcessed.add(childHandle)


    def findChildren(self):
        # we need to start with all of our "people of interest"
        childrenNotYetProcessed = set(self.interestSet)
        childrenToInclude = set()

        # now we find all the children of our people of interest

        while len(childrenNotYetProcessed) > 0:
            handle = childrenNotYetProcessed.pop()
            self.progress.step()

            if handle not in childrenToInclude:

                person = self.db.get_person_from_handle(handle)

                # if this is a private record, and we're not
                # including private records, then go back to the
                # top of the while loop to get the next person
                if person.private and not self.includePrivate:
                    continue

                # remember this person!
                childrenToInclude.add(handle)

                # if we have a limit on the number of people, and we've
                # reached that limit, then don't attempt to find any
                # more children
                if self.limitChildren and (self.maxChildren < ( len(childrenNotYetProcessed) + len(childrenToInclude))):
                    # get back to the top of the while loop so we can finish
                    # processing the people queued up in the "not yet processed" list
                    continue

                # iterate through this person's families
                for familyHandle in person.get_family_handle_list():
                    family = self.db.get_family_from_handle(familyHandle)
                    if (family.private and self.includePrivate) or not family.private:

                        # queue up any children from this person's family
                        for childRef in family.get_child_ref_list():
                            child = self.db.get_person_from_handle(childRef.ref)
                            if (child.private and self.includePrivate) or not child.private:
                                childrenNotYetProcessed.add(child.get_handle())
                                self.familiesToOutput.add(familyHandle)

                        # include the spouse from this person's family
                        spouseHandle = ReportUtils.find_spouse(person, family)
                        if spouseHandle:
                            spouse = self.db.get_person_from_handle(spouseHandle)
                            if (spouse.private and self.includePrivate) or not spouse.private:
                                childrenToInclude.add(spouseHandle)
                                self.familiesToOutput.add(familyHandle)

        # we now merge our temp set "childrenToInclude" into our master set
        self.peopleToOutput.update(childrenToInclude)


    def writePeople(self):
        # if we're going to attempt to include images, then use the HTML style of .dot file
        bUseHtmlOutput = False
        if self.includeImages:
            bUseHtmlOutput = True

        # loop through all the people we need to output
        for handle in self.peopleToOutput:
            self.progress.step()
            person = self.db.get_person_from_handle(handle)
            name = person.get_primary_name().get_regular_name()

            # figure out what colour to use
            colour = self.colourUnknown
            if person.get_gender() ==  RelLib.Person.MALE:
                colour = self.colourMales
            if person.get_gender() ==  RelLib.Person.FEMALE:
                colour = self.colourFemales

            # see if we have surname colours that match this person
            surname = person.get_primary_name().get_surname().encode('iso-8859-1','xmlcharrefreplace')
            if surname in self.surnameColours:
                colour = self.surnameColours[surname]

            # see if we have a birth date we can use
            birthStr = None
            if self.includeDates and person.get_birth_ref():
                event = self.db.get_event_from_handle(person.get_birth_ref().ref)
                if (event.private and self.includePrivate) or not event.private:
                    date = event.get_date_object()
                    if date.get_day_valid() and date.get_month_valid() and date.get_year_valid():
                        birthStr = _dd.display(date)
                    elif date.get_year_valid():
                        birthStr = '%d' % date.get_year()

            # see if we have a birth place (one of:  city, state, or country) we can use
            birthplace = None
            if self.includePlaces and person.get_birth_ref():
                event = self.db.get_event_from_handle(person.get_birth_ref().ref)
                if (event.private and self.includePrivate) or not event.private:
                    place = self.db.get_place_from_handle(event.get_place_handle())
                    if place:
                        location = place.get_main_location()
                        if location.get_city:
                            birthplace = location.get_city()
                        elif location.get_state:
                            birthplace = location.get_state()
                        elif location.get_country:
                            birthplace = location.get_country()

            # see if we have a deceased date we can use
            deathStr = None
            if self.includeDates and person.get_death_ref():
                event = self.db.get_event_from_handle(person.get_death_ref().ref)
                if (event.private and self.includePrivate) or not event.private:
                    date = event.get_date_object()
                    if date.get_day_valid() and date.get_month_valid() and date.get_year_valid():
                        deathStr = _dd.display(date)
                    elif date.get_year_valid():
                        deathStr = '%d' % date.get_year()

            # see if we have a place of death (one of:  city, state, or country) we can use
            deathplace = None
            if self.includePlaces and person.get_death_ref():
                event = self.db.get_event_from_handle(person.get_death_ref().ref)
                if (event.private and self.includePrivate) or not event.private:
                    place = self.db.get_place_from_handle(event.get_place_handle())
                    if place:
                        location = place.get_main_location()
                        if location.get_city:
                            deathplace = location.get_city()
                        elif location.get_state:
                            deathplace = location.get_state()
                        elif location.get_country:
                            deathplace = location.get_country()

            # see if we have an image to use for this person
            imagePath = None
            if self.includeImages:
                mediaList = person.get_media_list()
                if len(mediaList) > 0:
                    mediaHandle = mediaList[0].get_reference_handle()
                    media = self.db.get_object_from_handle(mediaHandle)
                    mediaMimeType = media.get_mime_type()
                    if mediaMimeType[0:5] == "image":
                        imagePath = os.path.abspath(ImgManip.get_thumbnail_path(media.get_path()))

            # put the label together and ouput this person
            label = u""
            lineDelimiter = '\\n'
            if bUseHtmlOutput:
                lineDelimiter = '<BR/>'

            # if we have an image, then start an HTML table; remember to close the table afterwards!
            if imagePath:
                label = u'<TABLE BORDER="0" CELLSPACING="2" CELLPADDING="0" CELLBORDER="0"><TR><TD><IMG SRC="%s"/></TD>'  % imagePath
                if self.imageOnTheSide == 0:
                    label += u'</TR><TR>'
                label += '<TD>'

            # at the very least, the label must have the person's name
            label += name

            if birthStr or deathStr:
                label += ' %s(' % lineDelimiter
                if birthStr:
                    label += '%s' % birthStr
                label += ' - '
                if deathStr:
                    label += '%s' % deathStr
                label += ')'
            if birthplace or deathplace:
                if birthplace == deathplace:
                    deathplace = None    # no need to print the same name twice
                label += ' %s' % lineDelimiter
                if birthplace:
                    label += '%s' % birthplace
                if birthplace and deathplace:
                    label += ' / '
                if deathplace:
                    label += '%s' % deathplace

            # see if we have a table that needs to be terminated
            if imagePath:
                label += '</TD></TR></TABLE>'

            if bUseHtmlOutput:
                label = '<%s>' % label
            else:
                label = '"%s"' % label
            self.write('  %s [shape="box", fillcolor="%s", label=%s];\n' % (person.get_gramps_id(), colour, label))

    def writeFamilies(self):
        # loop through all the families we need to output
        for familyHandle in self.familiesToOutput:
            self.progress.step()
            family = self.db.get_family_from_handle(familyHandle)
            fgid = family.get_gramps_id()

            # figure out a wedding date or placename we can use
            weddingDate = None
            weddingPlace = None
            if self.includeDates or self.includePlaces:
                for event_ref in family.get_event_ref_list():
                    event = self.db.get_event_from_handle(event_ref.ref)
                    if event.get_type() == RelLib.EventType.MARRIAGE:
                        # get the wedding date
                        if (event.private and self.includePrivate) or not event.private:
                            if self.includeDates:
                                date = event.get_date_object()
                                if date.get_day_valid() and date.get_month_valid() and date.get_year_valid():
                                    weddingDate = _dd.display(date)
                                elif date.get_year_valid():
                                    weddingDate = '%d' % date.get_year()
                            # get the wedding location
                            if self.includePlaces:
                                place = self.db.get_place_from_handle(event.get_place_handle())
                                if place:
                                    location = place.get_main_location()
                                    if location.get_city:
                                        weddingPlace = location.get_city()
                                    elif location.get_state:
                                        weddingPlace = location.get_state()
                                    elif location.get_country:
                                        weddingPlace = location.get_country()
                        break

            # figure out the number of children (if any)
            childrenStr = None
            if self.includeNumChildren:
                numberOfChildren = len(family.get_child_ref_list())
#                if numberOfChildren == 1:
#                    childrenStr = _('1 child')
                if numberOfChildren > 1:
                    childrenStr = _('%d children') % numberOfChildren

            label = ''
            if weddingDate:
                if label != '':
                    label += '\\n'
                label += '%s' % weddingDate
            if weddingPlace:
                if label != '':
                    label += '\\n'
                label += '%s' % weddingPlace
            if childrenStr:
                if label != '':
                    label += '\\n'
                label += '%s' % childrenStr
            self.write('  %s [shape="ellipse", fillcolor="%s", label="%s"];\n' % (fgid, self.colourFamilies, label))

        # now that we have the families written, go ahead and link the parents and children to the families
        for familyHandle in self.familiesToOutput:
            self.progress.step()
            self.write('\n')

            # get the parents for this family
            family = self.db.get_family_from_handle(familyHandle)
            fgid = family.get_gramps_id()

            # see if we have a father to link to this family
            fatherHandle = family.get_father_handle()
            if fatherHandle:
                if fatherHandle in self.peopleToOutput:
                    father = self.db.get_person_from_handle(fatherHandle)
                    self.write('  %s -> %s // father: %s\n' % (fgid, father.get_gramps_id(), father.get_primary_name().get_regular_name()))

            # see if we have a mother to link to this family
            motherHandle = family.get_mother_handle()
            if motherHandle:
                if motherHandle in self.peopleToOutput:
                    mother = self.db.get_person_from_handle(motherHandle)
                    self.write('  %s -> %s // mother: %s\n' % (fgid, mother.get_gramps_id(), mother.get_primary_name().get_regular_name()))

            # link the children to the family
            for childRef in family.get_child_ref_list():
                if childRef.ref in self.peopleToOutput:
                    child = self.db.get_person_from_handle(childRef.ref)
                    self.write('  %s -> %s // child:  %s\n' % (child.get_gramps_id(), fgid, child.get_primary_name().get_regular_name()))


    def write_report(self):

        # see if we're going to have problems writing the file
        if os.path.isdir(self.filename):
            ErrorDialog(_('Invalid file name'), _('The archive file must be a file, not a directory'))
            return

        try:
            self.of = open(self.filename, "w")
        except (OSError,IOError),value:
            ErrorDialog(_("Could not create %s") % self.filename)
            return

        self.progress = Utils.ProgressMeter(_('Generate family lines'),_('Starting'))

        # starting with the people of interest, we then add parents and children:
        self.peopleToOutput.clear()
        self.familiesToOutput.clear()
        self.progress.set_pass(_('Finding ancestors and children'), self.db.get_number_of_people())
        if self.followParents:
            self.findParents()

            if self.removeExtraPeople:
                self.removeUninterestingParents()

        # ...and/or we add children:
        if self.followChildren:
            self.findChildren()

        # write out the report now that we know who we want

        # since we know the exact number of people and families,
        # we can then restart the progress bar with the exact
        # number
        self.progress.set_pass(_('Writing family lines'),
            len(self.peopleToOutput) +      # every person needs to be written
            len(self.familiesToOutput) +    # every family needs to be written
            len(self.familiesToOutput))     # every family needs people assigned to it

        self.writeDotHeader()
        self.writePeople()
        self.writeFamilies()
        self.writeDotFooter()
        self.of.close()
        self.progress.close()


#------------------------------------------------------------------------
#
# Create all of the GUI controls that we're going to need.
# (...and setup the default values for all those GUI controls...)
#
#------------------------------------------------------------------------
class FamilyLinesOptions(ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dialog):
        ReportOptions.__init__(self, name, None)
        self.dialog = dialog

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'FLfilename'            : 'familylines.dot',
            'FLwidth'               : 48.00,
            'FLheight'              : 36.00,
            'FLdpi'                 : 75,
            'FLrowSep'              : 0.20,
            'FLcolSep'              : 0.20,
            'FLdirection'           : 'RL',
            'FLratio'               : 'compress',
            'FLfollowParents'       : 0,
            'FLfollowChildren'      : 0,
            'FLremoveExtraPeople'   : 1,
            'FLgidlist'             : '',
            'FLcolourMales'         : '#e0e0ff',    # blue
            'FLcolourFemales'       : '#ffe0e0',    # pink
            'FLcolourUnknown'       : '#e0e0e0',    # gray
            'FLcolourFamilies'      : '#ffffe0',    # yellow
            'FLsurnameColours'      : '',
            'FLlimitParents'        : 0,
            'FLmaxParents'          : 75,
            'FLlimitChildren'       : 0,
            'FLmaxChildren'         : 75,
            'FLincludeImages'       : 1,
            'FLimageOnTheSide'      : 1,
            'FLincludeDates'        : 1,
            'FLincludePlaces'       : 1,
            'FLincludeNumChildren'  : 1,
            'FLincludeResearcher'   : 1,
            'FLincludePrivate'      : 0
        }

#        self.options_help = {
#        }

#    def enable_options(self):
#        # Semi-common options that should be enabled for this report
#        self.enable_dict = {
#        }

    def add_user_options(self, dialog):
        """called from base class to allow us the opportunity to create some UI controls"""

#        self.dialog.target_fileentry.set_filename(self.options_dict['FLfilename'])

        # ******** GRAPHVIZ OPTIONS **********
        title = _("GraphViz Options")
        widthAdj        = gtk.Adjustment(value=self.options_dict['FLwidth'  ], lower=8.00, upper=1000.00, step_incr=0.25)
        heightAdj       = gtk.Adjustment(value=self.options_dict['FLheight' ], lower=8.00, upper=1000.00, step_incr=0.25)
        dpiAdj          = gtk.Adjustment(value=self.options_dict['FLdpi'    ], lower=20, upper=1200, step_incr=1)
        rowSepAdj       = gtk.Adjustment(value=self.options_dict['FLrowSep' ], lower=0.01, upper=5, step_incr=0.01)
        colSepAdj       = gtk.Adjustment(value=self.options_dict['FLcolSep' ], lower=0.01, upper=5, step_incr=0.01)

        self.width      = gtk.SpinButton(adjustment=widthAdj,   digits=2)
        self.height     = gtk.SpinButton(adjustment=heightAdj,  digits=2)
        self.dpi        = gtk.SpinButton(adjustment=dpiAdj,     digits=0)
        self.rowSep     = gtk.SpinButton(adjustment=rowSepAdj,  digits=2)
        self.colSep     = gtk.SpinButton(adjustment=colSepAdj,  digits=2)

        self.direction  = gtk.combo_box_new_text()
        self.ratio      = gtk.combo_box_new_text()

        direction_options = [_('left to right'), _('right to left'), _('top to bottom'), _('bottom to top')]
        for text in direction_options:
            self.direction.append_text(text)
        direction_text = self.options_dict['FLdirection']
        if direction_text == 'LR':
            self.direction.set_active(direction_options.index(_('left to right')))
        elif direction_text == 'RL':
            self.direction.set_active(direction_options.index(_('right to left')))
        elif direction_text == 'TB':
            self.direction.set_active(direction_options.index(_('top to bottom')))
        else:
            self.direction.set_active(direction_options.index(_('bottom to top')))

        ratio_options = ['auto', 'compress', 'expand', 'fill']
        for text in ratio_options:
            self.ratio.append_text(text)
        ratio_text = self.options_dict['FLratio']
        if ratio_text in ratio_options:
            self.ratio.set_active(ratio_options.index(ratio_text))
        else:
            self.ratio.set_active(0)

        dialog.add_frame_option(title, _('Width'            ), self.width       , _('Width of the graph in inches.  Final image size may be smaller than this if ratio type is "Compress".'))
        dialog.add_frame_option(title, _('Height'           ), self.height      , _('Height of the graph in inches.  Final image size may be smaller than this if ratio type is "Compress".'))
        dialog.add_frame_option(title, _('DPI'              ), self.dpi         , _('Dots per inch.  When planning to create .gif or .png files for the web, try numbers such as 75 or 100 DPI.'))
        dialog.add_frame_option(title, _('Row spacing'      ), self.rowSep      , _('The minimum amount of free space, in inches, between individual rows.'))
        dialog.add_frame_option(title, _('Columns spacing'  ), self.colSep      , _('The minimum amount of free space, in inches, between individual columns.'))
        dialog.add_frame_option(title, _('Graph direction'  ), self.direction   , _('Left-to-right means oldest ancestors on the left, youngest on the right. Top-to-bottom means oldest ancestors on the top, youngest on the botom.'))
        dialog.add_frame_option(title, _('Ratio'            ), self.ratio       , _('See the GraphViz documentation for details on the use of "ratio".  '))

        # ******** PEOPLE OF INTEREST **********
        title = _("People of Interest")

        # build up a container to display all of the people of interest
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.treeView = gtk.TreeView(self.model)
        self.treeView.set_size_request(150, 150)
        col1 = gtk.TreeViewColumn(_('Name'), gtk.CellRendererText(), text=0)
        col2 = gtk.TreeViewColumn(_('ID'), gtk.CellRendererText(), text=1)
        col1.set_resizable(True)
        col2.set_resizable(True)
        col1.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        col2.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        col1.set_sort_column_id(0)
        col2.set_sort_column_id(1)
        self.treeView.append_column(col1)
        self.treeView.append_column(col2)
        self.scrolledWindow = gtk.ScrolledWindow()
        self.scrolledWindow.add(self.treeView)
        self.scrolledWindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scrolledWindow.set_shadow_type(gtk.SHADOW_OUT)
        self.hbox = gtk.HBox()
        self.hbox.pack_start(self.scrolledWindow, expand=True, fill=True)

        for gid in self.options_dict['FLgidlist'].split():
            person = self.dialog.database.get_person_from_gramps_id(gid)
            if person:
                name = _nd.display(person)
                self.model.append([name, gid])

        # now setup the '+' and '-' pushbutton for adding/removing people from the container
        self.addPerson = GrampsWidgets.SimpleButton(gtk.STOCK_ADD, self.dialog.addPersonClicked)
        self.delPerson = GrampsWidgets.SimpleButton(gtk.STOCK_REMOVE, self.dialog.delPersonClicked)
        self.vbbox = gtk.VButtonBox()
        self.vbbox.add(self.addPerson)
        self.vbbox.add(self.delPerson)
        self.vbbox.set_layout(gtk.BUTTONBOX_SPREAD)
        self.hbox.pack_end(self.vbbox, expand=False)

        self.followParents = gtk.CheckButton(_("Follow parents to determine family lines"))
        self.followChildren = gtk.CheckButton(_("Follow children to determine family lines"))
        self.removeExtraPeople = gtk.CheckButton(_("Try to remove extra people and families"))

        self.followParents.set_active(self.options_dict['FLfollowParents'])
        self.followChildren.set_active(self.options_dict['FLfollowChildren'])
        self.removeExtraPeople.set_active(self.options_dict['FLremoveExtraPeople'])

        dialog.add_frame_option(title, _('People\nof\ninterest'), self.hbox, _('People of interest are used as a starting point when determining \"family lines\".'))
        dialog.add_frame_option(title, None, self.followParents, _('Parents and their ancestors will be considered when determining "family lines".'))
        dialog.add_frame_option(title, None, self.followChildren, _('Children will be considered when determining "family lines".'))
        dialog.add_frame_option(title, None, self.removeExtraPeople, _('People and families not directly related to people of interest will be removed when determining "family lines".'))

        # ******** FAMILY COLOURS **********
        title = _("Family Colours")

        self.familyLinesModel = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        self.familyLinesTreeView = gtk.TreeView(self.familyLinesModel)
        self.familyLinesTreeView.set_size_request(150, 150)
        self.familyLinesTreeView.connect('row-activated', self.dialog.familyLinesClicked)
        col1 = gtk.TreeViewColumn(_('Surname'), gtk.CellRendererText(), text=0)
        col2 = gtk.TreeViewColumn(_('Colour'), gtk.CellRendererText(), text=1)
        col1.set_resizable(True)
        col2.set_resizable(True)
        col1.set_sort_column_id(0)
        col1.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        col2.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.familyLinesTreeView.append_column(col1)
        self.familyLinesTreeView.append_column(col2)
        self.familyLinesScrolledWindow = gtk.ScrolledWindow()
        self.familyLinesScrolledWindow.add(self.familyLinesTreeView)
        self.familyLinesScrolledWindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.familyLinesScrolledWindow.set_shadow_type(gtk.SHADOW_OUT)
        self.familyLinesHbox = gtk.HBox()
        self.familyLinesHbox.pack_start(self.familyLinesScrolledWindow, expand=True, fill=True)

        self.addSurname = GrampsWidgets.SimpleButton(gtk.STOCK_ADD, self.dialog.addSurnameClicked)
        self.delSurname = GrampsWidgets.SimpleButton(gtk.STOCK_REMOVE, self.dialog.delSurnameClicked)
        self.familyLinesVbbox = gtk.VButtonBox()
        self.familyLinesVbbox.add(self.addSurname)
        self.familyLinesVbbox.add(self.delSurname)
        self.familyLinesVbbox.set_layout(gtk.BUTTONBOX_SPREAD)
        self.familyLinesHbox.pack_end(self.familyLinesVbbox, expand=False)

        dialog.add_frame_option(title, None, self.familyLinesHbox)

        # populate the surname/colour treeview
        tmp = self.options_dict['FLsurnameColours'].split()
        while len(tmp) > 1:
            surname = tmp.pop(0)
            colour = tmp.pop(0)
            self.familyLinesModel.append([surname, colour])

        # ******** INDIVIDUALS **********
        title = _("Individuals")
        self.colourMales = gtk.ColorButton(gtk.gdk.color_parse(self.options_dict['FLcolourMales']))
        self.colourFemales = gtk.ColorButton(gtk.gdk.color_parse(self.options_dict['FLcolourFemales']))
        self.colourUnknown = gtk.ColorButton(gtk.gdk.color_parse(self.options_dict['FLcolourUnknown']))
        self.colourFamilies = gtk.ColorButton(gtk.gdk.color_parse(self.options_dict['FLcolourFamilies']))

        self.limitParents   = gtk.CheckButton(_('Limit the number of parents'))
        maxParentsAdj       = gtk.Adjustment(value=self.options_dict['FLmaxParents' ], lower=10, upper=9999, step_incr=1)
        self.maxParents     = gtk.SpinButton(adjustment=maxParentsAdj, digits=0)
        self.limitChildren  = gtk.CheckButton(_('Limit the number of children'))
        maxChildrenAdj      = gtk.Adjustment(value=self.options_dict['FLmaxChildren' ], lower=10, upper=9999, step_incr=1)
        self.maxChildren    = gtk.SpinButton(adjustment=maxChildrenAdj, digits=0)
        self.limitParents.set_active(self.options_dict['FLlimitParents'])
        self.limitChildren.set_active(self.options_dict['FLlimitChildren'])

        dialog.add_frame_option(title, _('Males'), self.colourMales)
        dialog.add_frame_option(title, _('Females'), self.colourFemales)
        dialog.add_frame_option(title, _('Unknown'), self.colourUnknown)
        dialog.add_frame_option(title, _('Families'), self.colourFamilies)
        dialog.add_frame_option(title, None, self.limitParents)
        dialog.add_frame_option(title, None, self.maxParents, _('The maximum number of ancestors to include.'))
        dialog.add_frame_option(title, None, self.limitChildren)
        dialog.add_frame_option(title, None, self.maxChildren, _('The maximum number of children to include.'))

        # ******** IMAGES ********
        title = _("Images")
        self.includeImages = gtk.CheckButton(_('Include thumbnail images of people'))
        self.imageLocation = gtk.combo_box_new_text()
        self.imageLocation.append_text(_('place the thumbnail image above the name'))
        self.imageLocation.append_text(_('place the thumbnail image beside the name'))

        self.includeImages.set_active(self.options_dict['FLincludeImages'])
        self.imageLocation.set_active(self.options_dict['FLimageOnTheSide'])

        dialog.add_frame_option(title, None, self.includeImages, _("Whether to include thumbnails of people."))
        dialog.add_frame_option(title, None, self.imageLocation, _("Whether the thumbnails and the names are side-by-side, or one above the other."))

        # ******** OPTIONS *********
        title = _("Options")
        self.includeDates = gtk.CheckButton(_('Include dates'))
        self.includePlaces = gtk.CheckButton(_('Include places'))
        self.includeNumChildren = gtk.CheckButton(_('Include the number of children'))
        self.includeResearcher = gtk.CheckButton(_('Include researcher and date'))
        self.includePrivate = gtk.CheckButton(_('Include private records'))
        self.graphviz = gtk.Label(_(
            'This report will generate a .dot format file which can then be '
            'processed with the Graphviz package to generate various file '
            'formats such as .pdf, .gif, .svg, and many others. Additional '
            'Graphviz information is available from:\n'
            '    http://www.graphviz.org/\n'
            '\n'
            'Quick reference:  a .png file can be created using:\n'
            '    dot -Tpng -oexample.png familylines.dot'))
        self.graphviz.set_line_wrap(True)
        self.graphviz.set_single_line_mode(False)
        self.graphviz.set_selectable(True)

        self.includeDates.set_active(       self.options_dict['FLincludeDates'      ])
        self.includePlaces.set_active(      self.options_dict['FLincludePlaces'     ])
        self.includeNumChildren.set_active( self.options_dict['FLincludeNumChildren'])
        self.includeResearcher.set_active(  self.options_dict['FLincludeResearcher' ])
        self.includePrivate.set_active(     self.options_dict['FLincludePrivate'    ])

        dialog.add_frame_option(title, None, self.includeDates,         _("Whether to include dates for people and families."                                                     ))
        dialog.add_frame_option(title, None, self.includePlaces,        _("Whether to include placenames for people and families."                                                ))
        dialog.add_frame_option(title, None, self.includeNumChildren,   _("Whether to include the number of children for families with more than 1 child."                        ))
        dialog.add_frame_option(title, None, self.includeResearcher,    _("Whether to include at the bottom the researcher's name, e-mail, and the date the report was generated."))
        dialog.add_frame_option(title, None, self.includePrivate,       _("Whether to include names, dates, and families that are considered private."                            ))
        dialog.add_frame_option(title, None, self.graphviz)

        self.includeImages.connect( 'toggled', self.toggled)
        self.followParents.connect( 'toggled', self.toggled)
        self.followChildren.connect('toggled', self.toggled)
        self.limitParents.connect(  'toggled', self.toggled)
        self.limitChildren.connect( 'toggled', self.toggled)
        self.toggled(self.limitParents)


    def parse_user_options(self,dialog):
        # Save the user selected choices for later use.
        filename = self.dialog.target_fileentry.get_full_path(0)
        if os.path.isdir(filename):
            if filename[-1:] != '/':
                filename += '/'
            filename += 'familylines.dot'
            self.dialog.target_fileentry.set_filename(filename)
        if filename[-4:] != '.dot':
            filename += '.dot'
            self.dialog.target_fileentry.set_filename(filename)
        self.options_dict['FLfilename'          ] = filename
        self.options_dict['FLwidth'             ] = self.width.get_value()
        self.options_dict['FLheight'            ] = self.height.get_value()
        self.options_dict['FLdpi'               ] = int(self.dpi.get_value())
        self.options_dict['FLrowSep'            ] = self.rowSep.get_value()
        self.options_dict['FLcolSep'            ] = self.colSep.get_value()
        if self.direction.get_active_text() == _('left to right'):
            self.options_dict['FLdirection'     ] = 'LR'
        elif self.direction.get_active_text() == _('right to left'):
            self.options_dict['FLdirection'     ] = 'RL'
        elif self.direction.get_active_text() == _('top to bottom'):
            self.options_dict['FLdirection'     ] = 'TB'
        else:
            self.options_dict['FLdirection'     ] = 'BT'
        self.options_dict['FLratio'             ] = self.ratio.get_active_text()
        self.options_dict['FLfollowParents'     ] = int(self.followParents.get_active()     )
        self.options_dict['FLfollowChildren'    ] = int(self.followChildren.get_active()    )
        self.options_dict['FLremoveExtraPeople' ] = int(self.removeExtraPeople.get_active() )
        self.options_dict['FLlimitParents'      ] = int(self.limitParents.get_active()      )
        self.options_dict['FLmaxParents'        ] = int(self.maxParents.get_value()         )
        self.options_dict['FLlimitChildren'     ] = int(self.limitChildren.get_active()     )
        self.options_dict['FLmaxChildren'       ] = int(self.maxChildren.get_value()        )
        self.options_dict['FLincludeImages'     ] = int(self.includeImages.get_active()     )
        self.options_dict['FLimageOnTheSide'    ] = int(self.imageLocation.get_active()     )
        self.options_dict['FLincludeDates'      ] = int(self.includeDates.get_active()      )
        self.options_dict['FLincludePlaces'     ] = int(self.includePlaces.get_active()     )
        self.options_dict['FLincludeNumChildren'] = int(self.includeNumChildren.get_active())
        self.options_dict['FLincludeResearcher' ] = int(self.includeResearcher.get_active() )
        self.options_dict['FLincludePrivate'    ] = int(self.includePrivate.get_active()    )

        # we have a list of usernames & IDs -- save the IDs for next time
        gidlist = ''
        iter = self.model.get_iter_first()
        while (iter):
            gid = self.model.get_value(iter, 1)
            gidlist = gidlist + gid + ' '
            iter = self.model.iter_next(iter)
        self.options_dict['FLgidlist'           ] = gidlist

        colour = self.colourMales.get_color()
        colourName = '#%02x%02x%02x' % (
            int(colour.red  *256/65536),
            int(colour.green*256/65536),
            int(colour.blue *256/65536))
        self.options_dict['FLcolourMales'] = colourName

        colour = self.colourFemales.get_color()
        colourName = '#%02x%02x%02x' % (
            int(colour.red  *256/65536),
            int(colour.green*256/65536),
            int(colour.blue *256/65536))
        self.options_dict['FLcolourFemales'] = colourName

        colour = self.colourUnknown.get_color()
        colourName = '#%02x%02x%02x' % (
            int(colour.red  *256/65536),
            int(colour.green*256/65536),
            int(colour.blue *256/65536))
        self.options_dict['FLcolourUnknown'] = colourName

        colour = self.colourFamilies.get_color()
        colourName = '#%02x%02x%02x' % (
            int(colour.red  *256/65536),
            int(colour.green*256/65536),
            int(colour.blue *256/65536))
        self.options_dict['FLcolourFamilies'] = colourName

        surnameColours = ''
        iter = self.familyLinesModel.get_iter_first()
        while (iter):
            surname = self.familyLinesModel.get_value(iter, 0) # .encode('iso-8859-1','xmlcharrefreplace')
            colour = self.familyLinesModel.get_value(iter, 1)
            # tried to use a dictionary, and tried to save it as a tuple,
            # but coulnd't get this to work right -- this is lame, but now
            # the surnames and colours are saved as a plain text string
            surnameColours += surname + ' ' + colour + ' '
            iter = self.familyLinesModel.iter_next(iter)
        self.options_dict['FLsurnameColours'] = surnameColours

    def toggled(self, togglebutton):
        if not self.followParents.get_active():
            self.limitParents.set_active(False)
            self.removeExtraPeople.set_active(False)
        if not self.followChildren.get_active():
            self.limitChildren.set_active(False)

        self.imageLocation.set_sensitive(       self.includeImages.get_active() )
        self.removeExtraPeople.set_sensitive(   self.followParents.get_active() )
        self.limitParents.set_sensitive(        self.followParents.get_active() )
        self.limitChildren.set_sensitive(       self.followChildren.get_active())
        self.maxParents.set_sensitive(          self.limitParents.get_active()  )
        self.maxChildren.set_sensitive(         self.limitChildren.get_active() )

    def make_default_style(self,default_style):
        """Make the default output style for the Web Pages Report."""
        pass

#------------------------------------------------------------------------
#
# Dialog window used to select a surname
#
#------------------------------------------------------------------------
class LastNameDialog(ManagedWindow.ManagedWindow):

    def __init__(self, database, uistate, track, surnames, skipList=set()):

        self.title = _('Select surname')
        ManagedWindow.ManagedWindow.__init__(self, uistate, track, self)
        self.dlg = gtk.Dialog(
            None,
            uistate.window,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        self.dlg.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.set_window(self.dlg, None, self.title)
        self.window.set_default_size(400,400)

        # build up a container to display all of the people of interest
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_INT)
        self.treeView = gtk.TreeView(self.model)
        col1 = gtk.TreeViewColumn(_('Surname'), gtk.CellRendererText(), text=0)
        col2 = gtk.TreeViewColumn(_('Count'), gtk.CellRendererText(), text=1)
        col1.set_resizable(True)
        col2.set_resizable(True)
        col1.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        col2.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        col1.set_sort_column_id(0)
        col2.set_sort_column_id(1)
        self.treeView.append_column(col1)
        self.treeView.append_column(col2)
        self.scrolledWindow = gtk.ScrolledWindow()
        self.scrolledWindow.add(self.treeView)
        self.scrolledWindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scrolledWindow.set_shadow_type(gtk.SHADOW_OUT)
        self.dlg.vbox.pack_start(self.scrolledWindow, expand=True, fill=True)
        self.scrolledWindow.show_all()

        if len(surnames) == 0:
            # we could use database.get_surname_list(), but if we do that
            # all we get is a list of names without a count...therefore
            # we'll traverse the entire database ourself and build up a
            # list that we can use
#            for name in database.get_surname_list():
#                self.model.append([name, 0])

            # build up the list of surnames, keeping track of the count for each name
            # (this can be a lengthy process, so by passing in the dictionary we can
            # be certain we only do this once)
            progress = Utils.ProgressMeter(_('Family Lines'))
            progress.set_pass(_('Finding surnames'), database.get_number_of_people())
            for personHandle in database.get_person_handles(False):
                progress.step()
                person = database.get_person_from_handle(personHandle)
                key = person.get_primary_name().get_surname()
                count = 0
                if key in surnames:
                    count = surnames[key]
                surnames[key] = count + 1
            progress.close()

        # insert the names and count into the model
        for key in surnames:
            if key.encode('iso-8859-1','xmlcharrefreplace') not in skipList:
                self.model.append([key, surnames[key]])

        # keep the list sorted starting with the most popular last name
        self.model.set_sort_column_id(1, gtk.SORT_DESCENDING)

        # the "OK" button should be enabled/disabled based on the selection of a row
        self.treeSelection = self.treeView.get_selection()
        self.treeSelection.set_mode(gtk.SELECTION_MULTIPLE)
        self.treeSelection.select_path(0)

    def run(self):
        response = self.dlg.run()
        surnameSet = set()
        if response == gtk.RESPONSE_ACCEPT:
            (mode, paths) = self.treeSelection.get_selected_rows()
            for path in paths:
                iter = self.model.get_iter(path)
                surname = self.model.get_value(iter, 0)
                surnameSet.add(surname)
        self.dlg.destroy()
        return surnameSet

#------------------------------------------------------------------------
#
# class ReportDialog is in _ReportDialog.py, which in turn is derived
# from BaseReportDialog in _BaseReportDialog.py
#
# this is where we need to create the dialog window with all of the
# GUI controls
#
#------------------------------------------------------------------------
class FamilyLinesDialog(ReportDialog):

    HELP_TOPIC = None

    def __init__(self, dbstate, uistate, person):
        self.database = dbstate.db
        self.person = person
        name = "familylines"
        translated_name = _("Family Lines")
        self.options = FamilyLinesOptions(name, self)   # class which derives from ReportOptions (_ReportOptions.py)
        self.category = CATEGORY_CODE
        ReportDialog.__init__(self, dbstate, uistate, person, self.options, name, translated_name)
        self.style_name = None

        self.surnames = {}  # list of surnames and count

        while True:
            response = self.window.run()
            if response == gtk.RESPONSE_OK:
                self.make_report()
                break
            elif response != gtk.RESPONSE_HELP:
                break
        self.close()

    def addPersonClicked(self, obj):

        # people we already have in our list must be excluded
        # so we don't end up having people listed mutliple times
        skipList = set()
        iter = self.options.model.get_iter_first()
        while (iter):
            gid = self.options.model.get_value(iter, 1) # get the GID stored in column #1
            person = self.database.get_person_from_gramps_id(gid)
            skipList.add(person.get_handle())
            iter = self.options.model.iter_next(iter)

        SelectPerson = selector_factory('Person')
        sel = SelectPerson(self.dbstate, self.uistate, self.track, skip=skipList)
        person = sel.run()
        if person:
            name = _nd.display(person)
            gid = person.get_gramps_id()
            self.options.model.append([name, gid])

            # if this person has a spouse, ask if we should include the spouse
            # in the list of "people of interest"
            familyList = person.get_family_handle_list()
            if familyList:
                for familyHandle in familyList:
                    family = self.database.get_family_from_handle(familyHandle)
                    spouseHandle = ReportUtils.find_spouse(person, family)
                    if spouseHandle:
                        if spouseHandle not in skipList:
                            spouse = self.database.get_person_from_handle(spouseHandle)
                            text = _('Also include %s as a person of interest?') % spouse.get_primary_name().get_regular_name()
                            prompt = gtk.MessageDialog(parent=self.window, flags=gtk.DIALOG_MODAL, type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_YES_NO, message_format=text)
                            prompt.set_default_response(gtk.RESPONSE_YES)
                            prompt.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
                            prompt.set_title(_('Family Lines'))
                            button = prompt.run()
                            prompt.destroy()
                            if button == gtk.RESPONSE_YES:
                                name = _nd.display(spouse)
                                gid = spouse.get_gramps_id()
                                self.options.model.append([name, gid])


    def delPersonClicked(self, obj):
        (path, column) = self.options.treeView.get_cursor()
        if (path):
            iter = self.options.model.get_iter(path)
            self.options.model.remove(iter)


    def familyLinesClicked(self, treeview, path, column):
        # get the surname and colour value for this family
        iter = self.options.familyLinesModel.get_iter(path)
        surname = self.options.familyLinesModel.get_value(iter, 0)
        colour = gtk.gdk.color_parse(self.options.familyLinesModel.get_value(iter, 1))

        colourDialog = gtk.ColorSelectionDialog('Select colour for %s' % surname)
        colourDialog.colorsel.set_current_color(colour)
        response = colourDialog.run()

        if response == gtk.RESPONSE_OK:
            colour = colourDialog.colorsel.get_current_color()
            colourName = '#%02x%02x%02x' % (
                int(colour.red  *256/65536),
                int(colour.green*256/65536),
                int(colour.blue *256/65536))
            self.options.familyLinesModel.set_value(iter, 1, colourName)

        colourDialog.destroy()


    def addSurnameClicked(self, obj):
        skipList = set()
        iter = self.options.familyLinesModel.get_iter_first()
        while (iter):
            surname = self.options.familyLinesModel.get_value(iter, 0)
            skipList.add(surname.encode('iso-8859-1','xmlcharrefreplace'))
            iter = self.options.familyLinesModel.iter_next(iter)

        ln = LastNameDialog(self.database, self.uistate, self.track, self.surnames, skipList)
        surnameSet = ln.run()
        for surname in surnameSet:
            self.options.familyLinesModel.append([surname, '#ffffff'])


    def delSurnameClicked(self, obj):
        (path, column) = self.options.familyLinesTreeView.get_cursor()
        if (path):
            iter = self.options.familyLinesModel.get_iter(path)
            self.options.familyLinesModel.remove(iter)


    def setup_style_frame(self):
        """The style frame is not used in this dialog."""
        pass

    def parse_style_frame(self):
        """The style frame is not used in this dialog."""
        pass

    def get_target_is_directory(self):
        """This report creates a single file."""
        return None

#    def get_default_directory(self):
#        """Get the name of the directory to which the target dialog
#        box should default.  This value can be set in the preferences
#        panel."""
#        return '.'

    def make_document(self):
        """Do Nothing.  This document will be created in the
        make_report routine."""
        pass

    def setup_format_frame(self):
        """Do nothing, since we don't want a format frame"""
        pass
    
    def setup_post_process(self):
        """The format frame is not used in this dialog.  Hide it, and
        set the output notebook to always display the html template
        page."""
        pass

    def parse_format_frame(self):
        """The format frame is not used in this dialog."""
        pass

    def make_report(self):
        """Create the object that will produce the .dot output file."""
        try:
            MyReport = FamilyLinesReport(self.database, self.person, self.options)
            MyReport.write_report()
        except Errors.FilterError, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)

#------------------------------------------------------------------------
#
# register_report() is defined in _PluginMgr.py and
# is used to hook the plugin into GRAMPS so that it
# appears in the "Reports" menu options
#
#------------------------------------------------------------------------
register_report(
    name            = 'familylines',
    modes           = MODE_GUI,
    status          = _("Stable"),
    category        = CATEGORY_CODE,
    description     =_("Generates family line graphs using GraphViz."),
    author_name     = "Stephane Charette",
    author_email    = "stephanecharette@gmail.com",
    report_class    = FamilyLinesDialog,                    # class which will create everything needed for the report
    options_class   = None,
    translated_name = _("Family Lines Graph"),
    )

