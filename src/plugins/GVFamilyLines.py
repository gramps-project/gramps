#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008  Stephane Charette
# Copyright (C) 2007-2008  Brian G. Matherly
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

# $Id$

"""
Family Lines, a GraphViz-based plugin for Gramps.
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
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
# GRAMPS module
#
#------------------------------------------------------------------------
import gen.lib
import Utils
import ThumbNails
from DateHandler import displayer as _dd
from ReportBase import Report, ReportUtils, MenuReportOptions, CATEGORY_GRAPHVIZ
from gen.plug import PluginManager
from gen.plug.menu import NumberOption, ColorOption, BooleanOption, \
                          EnumeratedListOption, PersonListOption, \
                          SurnameColorOption

#------------------------------------------------------------------------
#
# Constant options items
#
#------------------------------------------------------------------------
_COLORS = [ { 'name' : _("B&W outline"),     'value' : "outline" },
            { 'name' : _("Coloured outline"), 'value' : "colored" },
            { 'name' : _("Colour fill"),      'value' : "filled"  }]

#------------------------------------------------------------------------
#
# A quick overview of the classes we'll be using:
#
#   class FamilyLinesOptions(MenuReportOptions)
#       - this class is created when the report dialog comes up
#       - all configuration controls for the report are created here
#       - see src/ReportBase/_ReportOptions.py for more information
#
#   class FamilyLinesReport(Report)
#       - this class is created only after the user clicks on "OK"
#       - the actual report generation is done by this class
#       - see src/ReportBase/_Report.py for more information
#
# Likely to be of additional interest is register_report() at the
# very bottom of this file.
#
#------------------------------------------------------------------------

class FamilyLinesOptions(MenuReportOptions):
    """
    Defines all of the controls necessary
    to configure the FamilyLines reports.
    """
    def __init__(self, name, dbase):
        self.limit_parents = None
        self.max_parents = None
        self.limit_children = None
        self.max_children = None
        self.include_images = None
        self.image_location = None
        MenuReportOptions.__init__(self, name, dbase)

    def add_menu_options(self, menu):

        # --------------------------------
        category = _('People of Interest')
        # --------------------------------

        person_list = PersonListOption(_('People of interest'))
        person_list.set_help(_('People of interest are used as a starting ' \
                              'point when determining "family lines".'))
        menu.add_option(category, 'gidlist', person_list)

        followpar = BooleanOption(
                           _('Follow parents to determine family lines'), True)
        followpar.set_help(_('Parents and their ancestors will be ' \
                             'considered when determining "family lines".'))
        menu.add_option(category, 'followpar', followpar)

        followchild = BooleanOption(_('Follow children to determine ' \
                                      '"family lines"'), True)
        followchild.set_help(_('Children will be considered when ' \
                                   'determining "family lines".'))
        menu.add_option(category, 'followchild', followchild)

        remove_extra_people = BooleanOption(
                             _('Try to remove extra people and families'), True)
        remove_extra_people.set_help(_('People and families not directly '   \
                                       'related to people of interest will ' \
                                       'be removed when determining '        \
                                       '"family lines".'))
        menu.add_option(category, 'removeextra', remove_extra_people)

        # ----------------------------
        category = _('Family Colours')
        # ----------------------------

        surname_color = SurnameColorOption(_('Family colours'))
        surname_color.set_help(_('Colours to use for various family lines.'))
        menu.add_option(category, 'surnamecolors', surname_color)

        # -------------------------
        category = _('Individuals')
        # -------------------------

        color_males = ColourOption(_('Males'), '#e0e0ff')
        color_males.set_help(_('The colour to use to display men.'))
        menu.add_option(category, 'colormales', color_males)

        color_females = ColourOption(_('Females'), '#ffe0e0')
        color_females.set_help(_('The colour to use to display women.'))
        menu.add_option(category, 'colorfemales', color_females)

        color_unknown = ColourOption(_('Unknown'), '#e0e0e0')
        color_unknown.set_help(_('The colour to use when the gender is ' \
                                 'unknown.'))
        menu.add_option(category, 'colorunknown', color_unknown)

        color_family = ColourOption(_('Families'), '#ffffe0')
        color_family.set_help(_('The colour to use to display families.'))
        menu.add_option(category, 'colorfamilies', color_family)

        self.limit_parents = BooleanOption(_('Limit the number of parents'), 
                                           False)
        self.limit_parents.set_help(
                            _('The maximum number of ancestors to include.'))
        menu.add_option(category, 'limitparents', self.limit_parents)
        self.limit_parents.connect('value-changed', self.limit_changed)

        self.max_parents = NumberOption('', 50, 10, 9999)
        self.max_parents.set_help(
                            _('The maximum number of ancestors to include.'))
        menu.add_option(category, 'maxparents', self.max_parents)

        self.limit_children = BooleanOption(_('Limit the number of children'), 
                                            False)
        self.limit_children.set_help(
                            _('The maximum number of children to include.'))
        menu.add_option(category, 'limitchildren', self.limit_children)
        self.limit_children.connect('value-changed', self.limit_changed)

        self.max_children = NumberOption('', 50, 10, 9999)
        self.max_children.set_help(
                            _('The maximum number of children to include.'))
        menu.add_option(category, 'maxchildren', self.max_children)

        # --------------------
        category = _('Images')
        # --------------------

        self.include_images = BooleanOption(
                                _('Include thumbnail images of people'), True)
        self.include_images.set_help(
                                _('The maximum number of children to include.'))
        menu.add_option(category, 'incimages', self.include_images)
        self.include_images.connect('value-changed', self.images_changed)

        self.image_location = EnumeratedListOption(_('Thumbnail location'), 0)
        self.image_location.add_item(0, _('Above the name'))
        self.image_location.add_item(1, _('Beside the name'))
        self.image_location.set_help(
             _('Where the thumbnail image should appear relative to the name'))
        menu.add_option(category, 'imageonside', self.image_location)

        # ---------------------
        category = _('Options')
        # ---------------------

        color = EnumeratedListOption(_("Graph coloring"), "filled")
        for i in range( 0, len(_COLORS) ):
            color.add_item(_COLORS[i]["value"], _COLORS[i]["name"])
        color.set_help(_("Males will be shown with blue, females "
                         "with red, unless otherwise set above for filled."
                         " If the sex of an individual "
                         "is unknown it will be shown with gray."))
        menu.add_option(category, "color", color)

        use_roundedcorners = BooleanOption(_('Use rounded corners'), False)
        use_roundedcorners.set_help(_('Use rounded corners to differentiate '
                                      'between women and men.'))
        menu.add_option(category, "useroundedcorners", use_roundedcorners)

        use_subgraphs = BooleanOption(_('Use subgraphs'), False)
        use_subgraphs.set_help(_("Subgraphs can help GraphViz position "
                                "certain linked nodes closer together, "
                                "but with non-trivial graphs will result "
                                "in longer lines and larger graphs."))
        menu.add_option(category, "usesubgraphs", use_subgraphs)

        include_dates = BooleanOption(_('Include dates'), True)
        include_dates.set_help(_('Whether to include dates for people and ' \
                                'families.'))
        menu.add_option(category, 'incdates', include_dates)

        include_places = BooleanOption(_('Include places'), True)
        include_places.set_help(_('Whether to include placenames for people ' \
                                  'and families.'))
        menu.add_option(category, 'incplaces', include_places)

        include_num_children = BooleanOption(
                                      _('Include the number of children'), True)
        include_num_children.set_help(_('Whether to include the number of ' \
                                        'children for families with more ' \
                                        'than 1 child.'))
        menu.add_option(category, 'incchildcnt', include_num_children)

        include_private = BooleanOption(_('Include private records'), False)
        include_private.set_help(_('Whether to include names, dates, and ' \
                                  'families that are marked as private.'))
        menu.add_option(category, 'incprivate', include_private)
        
        self.limit_changed()
        self.images_changed()

    def limit_changed(self):
        """
        Handle the change of limiting parents and children.
        """
        self.max_parents.set_available(self.limit_parents.get_value())
        self.max_children.set_available(self.limit_children.get_value())

    def images_changed(self):
        """
        Handle the change of including images.
        """
        self.image_location.set_available(self.include_images.get_value())

#------------------------------------------------------------------------
#
# FamilyLinesReport -- created once the user presses 'OK'
#
#------------------------------------------------------------------------
class FamilyLinesReport(Report):
    def __init__(self, database, options):
        """
        Create FamilyLinesReport object that eventually produces the report.
        
        The arguments are:

        database    - the GRAMPS database instance
        person      - currently selected person
        options     - instance of the FamilyLinesOptions class for this report
        """
        Report.__init__(self, database, options)

        # initialize several convenient variables
        self._db = database
        self._people = set() # handle of people we need in the report
        self._families = set() # handle of families we need in the report
        self._deleted_people = 0
        self._deleted_families = 0
        
        menu = options.menu
        
        _opt = menu.get_option_by_name('followpar')
        self._followpar = _opt.get_value()
        
        _opt = menu.get_option_by_name('followchild')
        self._followchild = _opt.get_value()
        
        _opt = menu.get_option_by_name('removeextra')
        self._removeextra = _opt.get_value()
        
        _opt = menu.get_option_by_name('gidlist')
        self._gidlist = _opt.get_value()
        
        _opt = menu.get_option_by_name('colormales')
        self._colormales = _opt.get_value()
        
        _opt = menu.get_option_by_name('colorfemales')
        self._colorfemales = _opt.get_value()
        
        _opt = menu.get_option_by_name('colorunknown')
        self._colorunknown = _opt.get_value()
        
        _opt = menu.get_option_by_name('colorfamilies')
        self._colorfamilies = _opt.get_value()
        
        _opt = menu.get_option_by_name('limitparents')
        self._limitparents = _opt.get_value()
        
        _opt = menu.get_option_by_name('maxparents')
        self._maxparents = _opt.get_value()
        
        _opt = menu.get_option_by_name('limitchildren')
        self._limitchildren = _opt.get_value()
        
        _opt = menu.get_option_by_name('maxchildren')
        self._maxchildren = _opt.get_value()
        
        _opt = menu.get_option_by_name('incimages')
        self._incimages = _opt.get_value()
        
        _opt = menu.get_option_by_name('imageonside')
        self._imageonside = _opt.get_value()

        _opt = menu.get_option_by_name('useroundedcorners')
        self._useroundedcorners = _opt.get_value()

        _opt = menu.get_option_by_name('usesubgraphs')
        self._usesubgraphs = _opt.get_value()
        
        _opt = menu.get_option_by_name('incdates')
        self._incdates = _opt.get_value()
        
        _opt = menu.get_option_by_name('incplaces')
        self._incplaces = _opt.get_value()
        
        _opt = menu.get_option_by_name('incchildcnt')
        self._incchildcount = _opt.get_value()
        
        _opt = menu.get_option_by_name('incprivate')
        self._incprivate = _opt.get_value()

        # the gidlist is annoying for us to use since we always have to convert
        # the GIDs to either Person or to handles, so we may as well convert the
        # entire list right now and not have to deal with it ever again
        self._interest_set = set()
        for gid in self._gidlist.split():
            person = self._db.get_person_from_gramps_id(gid)
            self._interest_set.add(person.get_handle())

        # convert the 'surnamecolors' string to a dictionary of names and colors
        self._surnamecolors = {}
        _opt = menu.get_option_by_name('surnamecolors')
        tmp = _opt.get_value()
        if (tmp.find(u'\xb0') >= 0):
            tmp = tmp.split(u'\xb0')    # new style delimiter (see bug report #2162)
        else:
            tmp = tmp.split(' ')        # old style delimiter

        while len(tmp) > 1:
            surname = tmp.pop(0).encode('iso-8859-1', 'xmlcharrefreplace')
            colour = tmp.pop(0)
            self._surnamecolors[surname] = colour

        self._colorize = menu.get_option_by_name('color').get_value()

    def begin_report(self):
        """
        Inherited method; called by report() in _ReportDialog.py
        
        This is where we'll do all of the work of figuring out who
        from the database is going to be output into the report
        """

        self.progress = Utils.ProgressMeter(_('Generating Family Lines'),
                                            _('Starting'))

        # starting with the people of interest, we then add parents:
        self._people.clear()
        self._families.clear()
        self.progress.set_pass(_('Finding ancestors and children'), 
                               self._db.get_number_of_people())
        if self._followpar:
            self.findParents()

            if self._removeextra:
                self.removeUninterestingParents()

        # ...and/or with the people of interest we add their children:
        if self._followchild:
            self.findChildren()
        # once we get here we have a full list of people
        # and families that we need to generate a report


    def write_report(self):
        """
        Inherited method; called by report() in _ReportDialog.py

        Since we know the exact number of people and families,
        we can then restart the progress bar with the exact number
        """
        
        self.progress.set_pass(_('Writing family lines'),
            len(self._people     ) + # every person needs to be written
            len(self._families   ) + # every family needs to be written
            len(self._families   ))  # every family needs people assigned to it

        # now that begin_report() has done the work, output what we've
        # obtained into whatever file or format the user expects to use

        self.doc.add_comment('# Number of people in database:    %d' 
                             % self._db.get_number_of_people())
        self.doc.add_comment('# Number of people of interest:    %d' 
                             % len(self._people))
        self.doc.add_comment('# Number of families in database:  %d' 
                             % self._db.get_number_of_families())
        self.doc.add_comment('# Number of families of interest:  %d' 
                             % len(self._families))
        if self._removeextra:
            self.doc.add_comment('# Additional people removed:       %d' 
                                 % self._deleted_people)
            self.doc.add_comment('# Additional families removed:     %d' 
                                 % self._deleted_families)
        self.doc.add_comment('# Initial list of people of interest:')
        for handle in self._interest_set:
            person = self._db.get_person_from_handle(handle)
            gid = person.get_gramps_id()
            name = person.get_primary_name().get_regular_name()
            self.doc.add_comment('# -> %s, %s' % (gid, name))

        self.writePeople()
        self.writeFamilies()
        self.progress.close()


    def findParents(self):
        # we need to start with all of our "people of interest"
        ancestorsNotYetProcessed = set(self._interest_set)

        # now we find all the immediate ancestors of our people of interest

        while len(ancestorsNotYetProcessed) > 0:
            handle = ancestorsNotYetProcessed.pop()
            self.progress.step()

            # One of 2 things can happen here:
            #   1) we've already know about this person and he/she is already 
            #      in our list
            #   2) this is someone new, and we need to remember him/her
            #
            # In the first case, there isn't anything else to do, so we simply 
            # go back to the top and pop the next person off the list.
            #
            # In the second case, we need to add this person to our list, and 
            # then go through all of the parents this person has to find more 
            # people of interest.

            if handle not in self._people:

                person = self._db.get_person_from_handle(handle)

                # if this is a private record, and we're not
                # including private records, then go back to the
                # top of the while loop to get the next person
                if person.private and not self._incprivate:
                    continue

                # remember this person!
                self._people.add(handle)

                # see if a family exists between this person and someone else
                # we have on our list of people we're going to output -- if
                # there is a family, then remember it for when it comes time
                # to link spouses together
                for family_handle in person.get_family_handle_list():
                    family = self._db.get_family_from_handle(family_handle)
                    spouse_handle = ReportUtils.find_spouse(person, family)
                    if spouse_handle:
                        if spouse_handle in self._people or \
                           spouse_handle in ancestorsNotYetProcessed:
                            self._families.add(family_handle)

                # if we have a limit on the number of people, and we've
                # reached that limit, then don't attempt to find any
                # more ancestors
                if self._limitparents and \
                  ( self._maxparents < \
                    ( len(ancestorsNotYetProcessed) + len(self._people) ) ):
                    # get back to the top of the while loop so we can finish
                    # processing the people queued up in the "not yet 
                    # processed" list
                    continue

                # queue the parents of the person we're processing
                for family_handle in person.get_parent_family_handle_list():
                    family = self._db.get_family_from_handle(family_handle)

                    if (family.private and self._incprivate) or \
                       not family.private:

                        father = self._db.get_person_from_handle(
                                                     family.get_father_handle())
                        mother = self._db.get_person_from_handle(
                                                     family.get_mother_handle())
                        if father:
                            if (father.private and self._incprivate) or \
                               not father.private:
                                ancestorsNotYetProcessed.add(
                                                     family.get_father_handle())
                                self._families.add(family_handle)
                        if mother:
                            if (mother.private and self._incprivate) or \
                               not mother.private:
                                ancestorsNotYetProcessed.add(
                                                     family.get_mother_handle())
                                self._families.add(family_handle)

    def removeUninterestingParents(self):
        # start with all the people we've already identified
        unprocessed_parents = set(self._people)

        while len(unprocessed_parents) > 0:
            handle = unprocessed_parents.pop()
            self.progress.step()
            person = self._db.get_person_from_handle(handle)

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

            child_handle = None
            child_count = 0
            spouse_handle = None
            spouse_count = 0
            father_handle = None
            mother_handle = None
            spouse_father_handle = None
            spouse_mother_handle = None
            spouse_surname = ""
            surname = person.get_primary_name().get_surname()
            surname = surname.encode('iso-8859-1','xmlcharrefreplace')

            # first we get the person's father and mother
            for family_handle in person.get_parent_family_handle_list():
                family = self._db.get_family_from_handle(family_handle)
                handle = family.get_father_handle()
                if handle in self._people:
                    father_handle = handle
                handle = family.get_mother_handle()
                if handle in self._people:
                    mother_handle = handle

            # now see how many spouses this person has
            for family_handle in person.get_family_handle_list():
                family = self._db.get_family_from_handle(family_handle)
                handle = ReportUtils.find_spouse(person, family)
                if handle in self._people:
                    spouse_count += 1
                    spouse = self._db.get_person_from_handle(handle)
                    spouse_handle = handle
                    spouse_surname = spouse.get_primary_name().get_surname()
                    spouse_surname = spouse_surname.encode('iso-8859-1',
                                                           'xmlcharrefreplace')

                    # see if the spouse has parents
                    if spouse_father_handle is None and \
                       spouse_mother_handle is None:
                        for family_handle in \
                          spouse.get_parent_family_handle_list():
                            family = self._db.get_family_from_handle(
                                                                  family_handle)
                            handle = family.get_father_handle()
                            if handle in self._people:
                                spouse_father_handle = handle
                            handle = family.get_mother_handle()
                            if handle in self._people:
                                spouse_mother_handle = handle

            # get the number of children that we think might be interesting
            for family_handle in person.get_family_handle_list():
                family = self._db.get_family_from_handle(family_handle)
                for child_ref in family.get_child_ref_list():
                    if child_ref.ref in self._people:
                        child_count += 1
                        child_handle = child_ref.ref

            # we now have everything we need -- start looking for reasons
            # why this is a person we need to keep in our list, and loop
            # back to the top as soon as a reason is discovered

            # if this person has many children of interest, then we
            # automatically keep this person
            if child_count > 1:
                continue

            # if this person has many spouses of interest, then we
            # automatically keep this person
            if spouse_count > 1:
                continue

            # if this person has parents, then we automatically keep
            # this person
            if father_handle is not None or mother_handle is not None:
                continue

            # if the spouse has parents, then we automatically keep
            # this person
            if spouse_father_handle is not None or spouse_mother_handle is not None:
                continue

            # if this is a person of interest, then we automatically keep
            if person.get_handle() in self._interest_set:
                continue

            # if the spouse is a person of interest, then we keep
            if spouse_handle in self._interest_set:
                continue

            # if the surname (or the spouse's surname) matches a person
            # of interest, then we automatically keep this person
            bKeepThisPerson = False
            for personOfInterestHandle in self._interest_set:
                personOfInterest = self._db.get_person_from_handle(personOfInterestHandle)
                surnameOfInterest = personOfInterest.get_primary_name().get_surname().encode('iso-8859-1','xmlcharrefreplace')
                if surnameOfInterest == surname or surnameOfInterest == spouse_surname:
                    bKeepThisPerson = True
                    break

            if bKeepThisPerson:
                continue

            # if we have a special colour to use for this person,
            # then we automatically keep this person
            if surname in self._surnamecolors:
                continue

            # if we have a special colour to use for the spouse,
            # then we automatically keep this person
            if spouse_surname in self._surnamecolors:
                continue

            # took us a while, but if we get here, then we can remove this person
            self._deleted_people += 1
            self._people.remove(person.get_handle())

            # we can also remove any families to which this person belonged
            for family_handle in person.get_family_handle_list():
                if family_handle in self._families:
                    self._deleted_families += 1
                    self._families.remove(family_handle)

            # if we have a spouse, then ensure we queue up the spouse
            if spouse_handle:
                if spouse_handle not in unprocessed_parents:
                    unprocessed_parents.add(spouse_handle)

            # if we have a child, then ensure we queue up the child
            if child_handle:
                if child_handle not in unprocessed_parents:
                    unprocessed_parents.add(child_handle)


    def findChildren(self):
        # we need to start with all of our "people of interest"
        childrenNotYetProcessed = set(self._interest_set)
        childrenToInclude = set()

        # now we find all the children of our people of interest

        while len(childrenNotYetProcessed) > 0:
            handle = childrenNotYetProcessed.pop()
            self.progress.step()

            if handle not in childrenToInclude:

                person = self._db.get_person_from_handle(handle)

                # if this is a private record, and we're not
                # including private records, then go back to the
                # top of the while loop to get the next person
                if person.private and not self._incprivate:
                    continue

                # remember this person!
                childrenToInclude.add(handle)

                # if we have a limit on the number of people, and we've
                # reached that limit, then don't attempt to find any
                # more children
                if self._limitchildren and (self._maxchildren < ( len(childrenNotYetProcessed) + len(childrenToInclude))):
                    # get back to the top of the while loop so we can finish
                    # processing the people queued up in the "not yet processed" list
                    continue

                # iterate through this person's families
                for family_handle in person.get_family_handle_list():
                    family = self._db.get_family_from_handle(family_handle)
                    if (family.private and self._incprivate) or not family.private:

                        # queue up any children from this person's family
                        for childRef in family.get_child_ref_list():
                            child = self._db.get_person_from_handle(childRef.ref)
                            if (child.private and self._incprivate) or not child.private:
                                childrenNotYetProcessed.add(child.get_handle())
                                self._families.add(family_handle)

                        # include the spouse from this person's family
                        spouse_handle = ReportUtils.find_spouse(person, family)
                        if spouse_handle:
                            spouse = self._db.get_person_from_handle(spouse_handle)
                            if (spouse.private and self._incprivate) or not spouse.private:
                                childrenToInclude.add(spouse_handle)
                                self._families.add(family_handle)

        # we now merge our temp set "childrenToInclude" into our master set
        self._people.update(childrenToInclude)


    def writePeople(self):

        self.doc.add_comment('')

        # if we're going to attempt to include images, then use the HTML style of .dot file
        bUseHtmlOutput = False
        if self._incimages:
            bUseHtmlOutput = True

        # loop through all the people we need to output
        for handle in self._people:
            self.progress.step()
            person = self._db.get_person_from_handle(handle)
            name = person.get_primary_name().get_regular_name()

            # figure out what colour to use
            gender = person.get_gender()
            colour = self._colorunknown
            if gender == gen.lib.Person.MALE:
                colour = self._colormales
            elif gender == gen.lib.Person.FEMALE:
                colour = self._colorfemales

            # see if we have surname colours that match this person
            surname = person.get_primary_name().get_surname().encode('iso-8859-1','xmlcharrefreplace')
            if surname in self._surnamecolors:
                colour = self._surnamecolors[surname]

            # see if we have a birth/death or fallback dates we can use
            if self._incdates or self._incplaces:
                bth_event = ReportUtils.get_birth_or_fallback(self._db, person)
                dth_event = ReportUtils.get_death_or_fallback(self._db, person)
            else:
                bth_event = None
                dth_event = None

            # output the birth or fallback event
            birthStr = None
            if bth_event and self._incdates:
                if (bth_event.private and self._incprivate) or \
                        not bth_event.private:
                    date = bth_event.get_date_object()
                    birthStr = _dd.display(date)

            # get birth place (one of:  city, state, or country) we can use
            birthplace = None
            if bth_event and self._incplaces:
                if (bth_event.private and self._incprivate) or \
                        not bth_event.private:
                    place = self._db.get_place_from_handle(bth_event.get_place_handle())
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
            if dth_event and self._incdates:
                if (dth_event.private and self._incprivate) or \
                        not dth_event.private:
                    date = dth_event.get_date_object()
                    deathStr = _dd.display(date)

            # get death place (one of:  city, state, or country) we can use
            deathplace = None
            if dth_event and self._incplaces:
                if (dth_event.private and self._incprivate) or \
                        not dth_event.private:
                    place = self._db.get_place_from_handle(dth_event.get_place_handle())
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
            if self._incimages:
                mediaList = person.get_media_list()
                if len(mediaList) > 0:
                    mediaHandle = mediaList[0].get_reference_handle()
                    media = self._db.get_object_from_handle(mediaHandle)
                    mediaMimeType = media.get_mime_type()
                    if mediaMimeType[0:5] == "image":
                        imagePath = ThumbNails.get_thumbnail_path(
                                        Utils.media_path_full(self._db, 
                                                              media.get_path())
                                                                 )

            # put the label together and ouput this person
            label = u""
            lineDelimiter = '\\n'
            if bUseHtmlOutput:
                lineDelimiter = '<BR/>'

            # if we have an image, then start an HTML table; remember to close the table afterwards!
            if imagePath:
                label = u'<TABLE BORDER="0" CELLSPACING="2" CELLPADDING="0" CELLBORDER="0"><TR><TD><IMG SRC="%s"/></TD>'  % imagePath
                if self._imageonside == 0:
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

            shape   = "box"
            style   = "solid"
            border  = colour
            fill    = colour

            # do not use colour if this is B&W outline
            if self._colorize == 'outline':
                border  = ""
                fill    = ""

            if gender == person.FEMALE and self._useroundedcorners:
                style = "rounded"
            elif gender == person.UNKNOWN:
                shape = "hexagon"

            # if we're filling the entire node:
            if self._colorize == 'filled':
                style += ",filled"
                border = ""

            # we're done -- add the node
            self.doc.add_node(person.get_gramps_id(),
                 label=label,
                 shape=shape,
                 color=border,
                 style=style,
                 fillcolor=fill,
                 htmloutput=bUseHtmlOutput)

    def writeFamilies(self):

        self.doc.add_comment('')

        # loop through all the families we need to output
        for family_handle in self._families:
            self.progress.step()
            family = self._db.get_family_from_handle(family_handle)
            fgid = family.get_gramps_id()

            # figure out a wedding date or placename we can use
            weddingDate = None
            weddingPlace = None
            if self._incdates or self._incplaces:
                for event_ref in family.get_event_ref_list():
                    event = self._db.get_event_from_handle(event_ref.ref)
                    if event.get_type() == gen.lib.EventType.MARRIAGE:
                        # get the wedding date
                        if (event.private and self._incprivate) or not event.private:
                            if self._incdates:
                                date = event.get_date_object()
                                weddingDate = _dd.display(date)
                            # get the wedding location
                            if self._incplaces:
                                place = self._db.get_place_from_handle(event.get_place_handle())
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
            if self._incchildcount:
                child_count = len(family.get_child_ref_list())
#                if child_count == 1:
#                    childrenStr = _('1 child')
                if child_count > 1:
                    childrenStr = _('%d children') % child_count

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

            shape   = "ellipse"
            style   = "solid"
            border  = self._colorfamilies
            fill    = self._colorfamilies

            # do not use colour if this is B&W outline
            if self._colorize == 'outline':
                border  = ""
                fill    = ""

            # if we're filling the entire node:
            if self._colorize == 'filled':
                style += ",filled"
                border = ""

            # we're done -- add the node
            self.doc.add_node(fgid, label, shape, border, style, fill)

        # now that we have the families written, go ahead and link the parents and children to the families
        for family_handle in self._families:
            self.progress.step()

            # get the parents for this family
            family = self._db.get_family_from_handle(family_handle)
            fgid = family.get_gramps_id()
            father_handle = family.get_father_handle()
            mother_handle = family.get_mother_handle()

            self.doc.add_comment('')

            if self._usesubgraphs and father_handle and mother_handle:
                self.doc.start_subgraph(fgid)

            # see if we have a father to link to this family
            if father_handle:
                if father_handle in self._people:
                    father = self._db.get_person_from_handle(father_handle)
                    comment = "father: %s" % father.get_primary_name().get_regular_name()
                    self.doc.add_link(fgid, father.get_gramps_id(), comment=comment)

            # see if we have a mother to link to this family
            if mother_handle:
                if mother_handle in self._people:
                    mother = self._db.get_person_from_handle(mother_handle)
                    comment = "mother: %s" % mother.get_primary_name().get_regular_name()
                    self.doc.add_link(fgid, mother.get_gramps_id(), comment=comment)

            if self._usesubgraphs and father_handle and mother_handle:
                self.doc.end_subgraph()

            # link the children to the family
            for childRef in family.get_child_ref_list():
                if childRef.ref in self._people:
                    child = self._db.get_person_from_handle(childRef.ref)
                    comment = "child:  %s" % child.get_primary_name().get_regular_name()
                    self.doc.add_link(child.get_gramps_id(), fgid, comment=comment)


#------------------------------------------------------------------------
#
# register_report() is defined in _PluginMgr.py and
# is used to hook the plugin into GRAMPS so that it
# appears in the "Reports" menu options
#
#------------------------------------------------------------------------
pmgr = PluginManager.get_instance()
pmgr.register_report(
    name            = 'familylines_graph',
    translated_name = _("Family Lines Graph"),
    category        = CATEGORY_GRAPHVIZ,
    report_class    = FamilyLinesReport,
    options_class   = FamilyLinesOptions,
    modes           = PluginManager.REPORT_MODE_GUI | \
                      PluginManager.REPORT_MODE_CLI,
    status          = _("Stable"),
    author_name     = "Stephane Charette",
    author_email    = "stephanecharette@gmail.com",
    description     = _("Produces family line graphs using GraphViz"),
    )

