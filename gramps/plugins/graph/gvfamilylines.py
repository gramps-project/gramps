#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008  Stephane Charette
# Copyright (C) 2007-2008  Brian G. Matherly
# Copyright (C) 2009-2010  Gary Burton
# Contribution 2009 by     Bob Ham <rah@bash.sh>
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011-2014  Paul Franklin
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
Family Lines, a Graphviz-based plugin for Gramps.
"""

# ------------------------------------------------------------------------
#
# python modules
#
# ------------------------------------------------------------------------
from functools import partial
import html

# ------------------------------------------------------------------------
#
# Set up logging
#
# ------------------------------------------------------------------------
import logging

LOG = logging.getLogger(".FamilyLines")

# ------------------------------------------------------------------------
#
# Gramps module
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gen.lib import EventRoleType, EventType, Person, PlaceType, Date
from gramps.gen.utils.file import media_path_full
from gramps.gen.utils.thumbnails import get_thumbnail_path, SIZE_NORMAL, SIZE_LARGE
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.plug.menu import (
    NumberOption,
    ColorOption,
    BooleanOption,
    EnumeratedListOption,
    PersonListOption,
    SurnameColorOption,
)
from gramps.gen.utils.db import get_birth_or_fallback, get_death_or_fallback
from gramps.gen.proxy import CacheProxyDb
from gramps.gen.errors import ReportError
from gramps.gen.display.place import displayer as _pd

# ------------------------------------------------------------------------
#
# Constant options items
#
# ------------------------------------------------------------------------
_COLORS = [
    {"name": _("B&W outline"), "value": "outline"},
    {"name": _("Colored outline"), "value": "colored"},
    {"name": _("Color fill"), "value": "filled"},
]

_ARROWS = [
    {"name": _("Descendants <- Ancestors"), "value": "d"},
    {"name": _("Descendants -> Ancestors"), "value": "a"},
    {"name": _("Descendants <-> Ancestors"), "value": "da"},
    {"name": _("Descendants - Ancestors"), "value": ""},
]

_CORNERS = [
    {"name": _("None"), "value": ""},
    {"name": _("Female"), "value": "f"},
    {"name": _("Male"), "value": "m"},
    {"name": _("Both"), "value": "fm"},
]

# ------------------------------------------------------------------------
#
# A quick overview of the classes we'll be using:
#
#   class FamilyLinesOptions(MenuReportOptions)
#       - this class is created when the report dialog comes up
#       - all configuration controls for the report are created here
#
#   class FamilyLinesReport(Report)
#       - this class is created only after the user clicks on "OK"
#       - the actual report generation is done by this class
#
# ------------------------------------------------------------------------


class FamilyLinesOptions(MenuReportOptions):
    """
    Defines all of the controls necessary
    to configure the FamilyLines report.
    """

    def __init__(self, name, dbase):
        self.limit_parents = None
        self.max_parents = None
        self.limit_children = None
        self.max_children = None
        self.include_images = None
        self.image_location = None
        self.justyears = None
        self.include_dates = None
        MenuReportOptions.__init__(self, name, dbase)

    def add_menu_options(self, menu):
        # ---------------------
        category_name = _("Report Options")
        add_option = partial(menu.add_option, category_name)
        # ---------------------

        followpar = BooleanOption(
            _("Follow parents to determine " '"family lines"'), True
        )
        followpar.set_help(
            _(
                "Parents and their ancestors will be "
                'considered when determining "family lines".'
            )
        )
        add_option("followpar", followpar)

        followchild = BooleanOption(
            _("Follow children to determine " '"family lines"'), True
        )
        followchild.set_help(
            _("Children will be considered when " 'determining "family lines".')
        )
        add_option("followchild", followchild)

        remove_extra_people = BooleanOption(
            _("Try to remove extra " "people and families"), True
        )
        remove_extra_people.set_help(
            _(
                "People and families not directly "
                "related to people of interest will "
                "be removed when determining "
                '"family lines".'
            )
        )
        add_option("removeextra", remove_extra_people)

        arrow = EnumeratedListOption(_("Arrowhead direction"), "d")
        for i in range(0, len(_ARROWS)):
            arrow.add_item(_ARROWS[i]["value"], _ARROWS[i]["name"])
        arrow.set_help(_("Choose the direction that the arrows point."))
        add_option("arrow", arrow)

        color = EnumeratedListOption(_("Graph coloring"), "filled")
        for COLOR in _COLORS:
            color.add_item(COLOR["value"], COLOR["name"])
        color.set_help(
            _(
                "Males will be shown with blue, females "
                "with red, unless otherwise set above for filled. "
                "If the sex of an individual "
                "is unknown it will be shown with gray."
            )
        )
        add_option("color", color)

        roundedcorners = EnumeratedListOption(_("Rounded corners"), "")
        for i in range(0, len(_CORNERS)):
            roundedcorners.add_item(_CORNERS[i]["value"], _CORNERS[i]["name"])
        roundedcorners.set_help(
            _("Use rounded corners e.g. to differentiate " "between women and men.")
        )
        add_option("useroundedcorners", roundedcorners)

        stdoptions.add_gramps_id_option(menu, category_name, ownline=True)

        # ---------------------
        category_name = _("Report Options (2)")
        add_option = partial(menu.add_option, category_name)
        # ---------------------

        stdoptions.add_name_format_option(menu, category_name)

        stdoptions.add_private_data_option(menu, category_name, default=False)

        stdoptions.add_living_people_option(menu, category_name)

        locale_opt = stdoptions.add_localization_option(menu, category_name)

        stdoptions.add_date_format_option(menu, category_name, locale_opt)

        use_subgraphs = BooleanOption(_("Use subgraphs"), True)
        use_subgraphs.set_help(
            _(
                "Subgraphs can help Graphviz position "
                "spouses together, but with non-trivial "
                "graphs will result in longer lines and "
                "larger graphs."
            )
        )
        add_option("usesubgraphs", use_subgraphs)

        # --------------------------------
        add_option = partial(menu.add_option, _("People of Interest"))
        # --------------------------------

        person_list = PersonListOption(_("People of interest"))
        person_list.set_help(
            _(
                "People of interest are used as a starting "
                'point when determining "family lines".'
            )
        )
        add_option("gidlist", person_list)

        self.limit_parents = BooleanOption(_("Limit the number of ancestors"), False)
        self.limit_parents.set_help(_("Whether to " "limit the number of ancestors."))
        add_option("limitparents", self.limit_parents)
        self.limit_parents.connect("value-changed", self.limit_changed)

        self.max_parents = NumberOption("", 50, 10, 9999)
        self.max_parents.set_help(_("The maximum number " "of ancestors to include."))
        add_option("maxparents", self.max_parents)

        self.limit_children = BooleanOption(
            _("Limit the number " "of descendants"), False
        )
        self.limit_children.set_help(
            _("Whether to " "limit the number of descendants.")
        )
        add_option("limitchildren", self.limit_children)
        self.limit_children.connect("value-changed", self.limit_changed)

        self.max_children = NumberOption("", 50, 10, 9999)
        self.max_children.set_help(
            _("The maximum number " "of descendants to include.")
        )
        add_option("maxchildren", self.max_children)

        # --------------------
        category_name = _("Include")
        add_option = partial(menu.add_option, category_name)
        # --------------------

        self.include_dates = BooleanOption(_("Include dates"), True)
        self.include_dates.set_help(
            _("Whether to include dates for people " "and families.")
        )
        add_option("incdates", self.include_dates)
        self.include_dates.connect("value-changed", self.include_dates_changed)

        self.justyears = BooleanOption(_("Limit dates to years only"), False)
        self.justyears.set_help(
            _(
                "Prints just dates' year, neither "
                "month or day nor date approximation "
                "or interval are shown."
            )
        )
        add_option("justyears", self.justyears)

        include_places = BooleanOption(_("Include places"), True)
        include_places.set_help(
            _("Whether to include placenames for people " "and families.")
        )
        add_option("incplaces", include_places)

        include_num_children = BooleanOption(
            _("Include the number of " "children"), True
        )
        include_num_children.set_help(
            _(
                "Whether to include the number of "
                "children for families with more "
                "than 1 child."
            )
        )
        add_option("incchildcnt", include_num_children)

        self.include_images = BooleanOption(
            _("Include " "thumbnail images of people"), True
        )
        self.include_images.set_help(
            _("Whether to " "include thumbnail images of people.")
        )
        add_option("incimages", self.include_images)
        self.include_images.connect("value-changed", self.images_changed)

        self.image_location = EnumeratedListOption(_("Thumbnail location"), 0)
        self.image_location.add_item(0, _("Above the name"))
        self.image_location.add_item(1, _("Beside the name"))
        self.image_location.set_help(
            _("Where the thumbnail image " "should appear relative to the name")
        )
        add_option("imageonside", self.image_location)

        self.image_size = EnumeratedListOption(_("Thumbnail size"), SIZE_NORMAL)
        self.image_size.add_item(SIZE_NORMAL, _("Normal"))
        self.image_size.add_item(SIZE_LARGE, _("Large"))
        self.image_size.set_help(_("Size of the thumbnail image"))
        add_option("imagesize", self.image_size)

        # ----------------------------
        add_option = partial(menu.add_option, _("Family Colors"))
        # ----------------------------

        surname_color = SurnameColorOption(_("Family colors"))
        surname_color.set_help(_("Colors to use for various family lines."))
        add_option("surnamecolors", surname_color)

        # -------------------------
        add_option = partial(menu.add_option, _("Individuals"))
        # -------------------------

        color_males = ColorOption(_("Males"), "#e0e0ff")
        color_males.set_help(_("The color to use to display men."))
        add_option("colormales", color_males)

        color_females = ColorOption(_("Females"), "#ffe0e0")
        color_females.set_help(_("The color to use to display women."))
        add_option("colorfemales", color_females)

        color_other = ColorOption(_("Other"), "#94ef9e")
        color_other.set_help(
            _("The color to use to display people who are " "neither men nor women.")
        )
        add_option("colorother", color_other)

        color_unknown = ColorOption(_("Unknown"), "#e0e0e0")
        color_unknown.set_help(_("The color to use " "when the gender is unknown."))
        add_option("colorunknown", color_unknown)

        color_family = ColorOption(_("Families"), "#ffffe0")
        color_family.set_help(_("The color to use to display families."))
        add_option("colorfamilies", color_family)

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
        self.image_size.set_available(self.include_images.get_value())

    def include_dates_changed(self):
        """
        Enable/disable menu items if dates are required
        """
        if self.include_dates.get_value():
            self.justyears.set_available(True)
        else:
            self.justyears.set_available(False)


# ------------------------------------------------------------------------
#
# FamilyLinesReport -- created once the user presses 'OK'
#
# ------------------------------------------------------------------------
class FamilyLinesReport(Report):
    """FamilyLines report"""

    def __init__(self, database, options, user):
        """
        Create FamilyLinesReport object that eventually produces the report.

        The arguments are:

        database     - the Gramps database instance
        options      - instance of the FamilyLinesOptions class for this report
        user         - a gen.user.User() instance
        name_format  - Preferred format to display names
        incl_private - Whether to include private data
        inc_id       - Whether to include IDs.
        living_people - How to handle living people
        years_past_death - Consider as living this many years after death
        """
        Report.__init__(self, database, options, user)

        menu = options.menu
        get_option_by_name = menu.get_option_by_name
        get_value = lambda name: get_option_by_name(name).get_value()

        self.set_locale(menu.get_option_by_name("trans").get_value())

        stdoptions.run_date_format_option(self, menu)

        stdoptions.run_private_data_option(self, menu)
        stdoptions.run_living_people_option(self, menu, self._locale)
        self.database = CacheProxyDb(self.database)
        self._db = self.database

        # initialize several convenient variables
        self._people = set()  # handle of people we need in the report
        self._families = set()  # handle of families we need in the report
        self._deleted_people = 0
        self._deleted_families = 0
        self._user = user

        self._followpar = get_value("followpar")
        self._followchild = get_value("followchild")
        self._removeextra = get_value("removeextra")
        self._gidlist = get_value("gidlist")
        self._colormales = get_value("colormales")
        self._colorfemales = get_value("colorfemales")
        self._colorother = get_value("colorother")
        self._colorunknown = get_value("colorunknown")
        self._colorfamilies = get_value("colorfamilies")
        self._limitparents = get_value("limitparents")
        self._maxparents = get_value("maxparents")
        self._limitchildren = get_value("limitchildren")
        self._maxchildren = get_value("maxchildren")
        self._incimages = get_value("incimages")
        self._imageonside = get_value("imageonside")
        self._imagesize = get_value("imagesize")
        self._useroundedcorners = get_value("useroundedcorners")
        self._usesubgraphs = get_value("usesubgraphs")
        self._incdates = get_value("incdates")
        self._just_years = get_value("justyears")
        self._incplaces = get_value("incplaces")
        self._incchildcount = get_value("incchildcnt")
        self.includeid = get_value("inc_id")

        arrow_str = get_value("arrow")
        if "d" in arrow_str:
            self._arrowheadstyle = "normal"
        else:
            self._arrowheadstyle = "none"
        if "a" in arrow_str:
            self._arrowtailstyle = "normal"
        else:
            self._arrowtailstyle = "none"

        # the gidlist is annoying for us to use since we always have to convert
        # the GIDs to either Person or to handles, so we may as well convert the
        # entire list right now and not have to deal with it ever again
        self._interest_set = set()
        if not self._gidlist:
            raise ReportError(_("Empty report"), _("You did not specify anybody"))
        for gid in self._gidlist.split():
            person = self._db.get_person_from_gramps_id(gid)
            if person:
                # option can be from another family tree, so person can be None
                self._interest_set.add(person.get_handle())

        stdoptions.run_name_format_option(self, menu)

        # convert the 'surnamecolors' string to a dictionary of names and colors
        self._surnamecolors = {}
        tmp = get_value("surnamecolors")
        if tmp.find("\xb0") >= 0:
            # new style delimiter (see bug report #2162)
            tmp = tmp.split("\xb0")
        else:
            # old style delimiter
            tmp = tmp.split(" ")

        while len(tmp) > 1:
            surname = tmp.pop(0).encode("iso-8859-1", "xmlcharrefreplace")
            colour = tmp.pop(0)
            self._surnamecolors[surname] = colour

        self._colorize = get_value("color")

    def begin_report(self):
        """
        Inherited method; called by report() in _ReportDialog.py

        This is where we'll do all of the work of figuring out who
        from the database is going to be output into the report
        """

        # starting with the people of interest, we then add parents:
        self._people.clear()
        self._families.clear()
        if self._followpar:
            self.find_parents()

            if self._removeextra:
                self.remove_uninteresting_parents()

        # ...and/or with the people of interest we add their children:
        if self._followchild:
            self.find_children()
        # once we get here we have a full list of people
        # and families that we need to generate a report

    def write_report(self):
        """
        Inherited method; called by report() in _ReportDialog.py
        """

        # now that begin_report() has done the work, output what we've
        # obtained into whatever file or format the user expects to use

        self.doc.add_comment(
            "# %s %d"
            % (self._("Number of people in database:"), self._db.get_number_of_people())
        )
        self.doc.add_comment(
            "# %s %d" % (self._("Number of people of interest:"), len(self._people))
        )
        self.doc.add_comment(
            "# %s %d"
            % (
                self._("Number of families in database:"),
                self._db.get_number_of_families(),
            )
        )
        self.doc.add_comment(
            "# %s %d" % (self._("Number of families of interest:"), len(self._families))
        )
        if self._removeextra:
            self.doc.add_comment(
                "# %s %d" % (self._("Additional people removed:"), self._deleted_people)
            )
            self.doc.add_comment(
                "# %s %d"
                % (self._("Additional families removed:"), self._deleted_families)
            )
        self.doc.add_comment("# %s" % self._("Initial list of people of interest:"))
        for handle in self._interest_set:
            person = self._db.get_person_from_handle(handle)
            gid = person.get_gramps_id()
            name = person.get_primary_name().get_regular_name()
            # Translators: needed for Arabic, ignore otherwise
            id_n = self._("%(str1)s, %(str2)s") % {"str1": gid, "str2": name}
            self.doc.add_comment("# -> " + id_n)

        self.write_people()
        self.write_families()

    def find_parents(self):
        """find the parents"""
        # we need to start with all of our "people of interest"
        ancestors_not_yet_processed = set(self._interest_set)

        # now we find all the immediate ancestors of our people of interest

        while ancestors_not_yet_processed:
            handle = ancestors_not_yet_processed.pop()

            # One of 2 things can happen here:
            #   1) we already know about this person and he/she is already
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

                # remember this person!
                self._people.add(handle)

                # see if a family exists between this person and someone else
                # we have on our list of people we're going to output -- if
                # there is a family, then remember it for when it comes time
                # to link spouses together
                for family_handle in person.get_family_handle_list():
                    family = self._db.get_family_from_handle(family_handle)
                    if not family:
                        continue
                    spouse_handle = utils.find_spouse(person, family)
                    if spouse_handle:
                        if (
                            spouse_handle in self._people
                            or spouse_handle in ancestors_not_yet_processed
                        ):
                            self._families.add(family_handle)

                # if we have a limit on the number of people, and we've
                # reached that limit, then don't attempt to find any
                # more ancestors
                if self._limitparents and (
                    self._maxparents
                    < len(ancestors_not_yet_processed) + len(self._people)
                ):
                    # get back to the top of the while loop so we can finish
                    # processing the people queued up in the "not yet
                    # processed" list
                    continue

                # queue the parents of the person we're processing
                for family_handle in person.get_parent_family_handle_list():
                    family = self._db.get_family_from_handle(family_handle)

                    father_handle = family.get_father_handle()
                    if father_handle:
                        father = self._db.get_person_from_handle(father_handle)
                        if father:
                            ancestors_not_yet_processed.add(father_handle)
                            self._families.add(family_handle)

                    mother_handle = family.get_mother_handle()
                    if mother_handle:
                        mother = self._db.get_person_from_handle(mother_handle)
                        if mother:
                            ancestors_not_yet_processed.add(mother_handle)
                            self._families.add(family_handle)

    def remove_uninteresting_parents(self):
        """remove any uninteresting parents"""
        # start with all the people we've already identified
        unprocessed_parents = set(self._people)

        while len(unprocessed_parents) > 0:
            handle = unprocessed_parents.pop()
            person = self._db.get_person_from_handle(handle)
            if not person:
                continue

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
            surname = surname.encode("iso-8859-1", "xmlcharrefreplace")

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
                handle = utils.find_spouse(person, family)
                if handle in self._people:
                    spouse_count += 1
                    spouse = self._db.get_person_from_handle(handle)
                    spouse_handle = handle
                    spouse_surname = spouse.get_primary_name().get_surname()
                    spouse_surname = spouse_surname.encode(
                        "iso-8859-1", "xmlcharrefreplace"
                    )

                    # see if the spouse has parents
                    if not spouse_father_handle and not spouse_mother_handle:
                        for family_handle in spouse.get_parent_family_handle_list():
                            family = self._db.get_family_from_handle(family_handle)
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
            keep_this_person = False
            for person_of_interest_handle in self._interest_set:
                person_of_interest = self._db.get_person_from_handle(
                    person_of_interest_handle
                )
                surname_of_interest = person_of_interest.get_primary_name()
                surname_of_interest = surname_of_interest.get_surname().encode(
                    "iso-8859-1", "xmlcharrefreplace"
                )
                if (
                    surname_of_interest == surname
                    or surname_of_interest == spouse_surname
                ):
                    keep_this_person = True
                    break

            if keep_this_person:
                continue

            # if we have a special colour to use for this person,
            # then we automatically keep this person
            if surname in self._surnamecolors:
                continue

            # if we have a special colour to use for the spouse,
            # then we automatically keep this person
            if spouse_surname in self._surnamecolors:
                continue

            # took us a while,
            # but if we get here then we can remove this person
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

    def find_children(self):
        """find any children"""
        # we need to start with all of our "people of interest"
        children_not_yet_processed = set(self._interest_set)
        children_to_include = set()

        # now we find all the children of our people of interest

        while len(children_not_yet_processed) > 0:
            handle = children_not_yet_processed.pop()

            if handle not in children_to_include:
                person = self._db.get_person_from_handle(handle)

                # remember this person!
                children_to_include.add(handle)

                # if we have a limit on the number of people, and we've
                # reached that limit, then don't attempt to find any
                # more children
                if self._limitchildren and (
                    self._maxchildren
                    < len(children_not_yet_processed) + len(children_to_include)
                ):
                    # get back to the top of the while loop
                    # so we can finish processing the people
                    # queued up in the "not yet processed" list
                    continue

                # iterate through this person's families
                for family_handle in person.get_family_handle_list():
                    family = self._db.get_family_from_handle(family_handle)

                    # queue up any children from this person's family
                    for childref in family.get_child_ref_list():
                        child = self._db.get_person_from_handle(childref.ref)
                        children_not_yet_processed.add(child.get_handle())
                        self._families.add(family_handle)

                    # include the spouse from this person's family
                    spouse_handle = utils.find_spouse(person, family)
                    if spouse_handle:
                        children_to_include.add(spouse_handle)
                        self._families.add(family_handle)

        # we now merge our temp set "children_to_include" into our master set
        self._people.update(children_to_include)

    def write_people(self):
        """write the people"""

        self.doc.add_comment("")

        # If we're going to attempt to include images, then use the HTML style
        # of .gv file.
        use_html_output = False
        if self._incimages:
            use_html_output = True

        # loop through all the people we need to output
        for handle in sorted(self._people):  # enable a diff
            person = self._db.get_person_from_handle(handle)
            name = self._name_display.display(person)
            p_id = person.get_gramps_id()

            # figure out what colour to use
            gender = person.get_gender()
            colour = self._colorunknown
            if gender == Person.MALE:
                colour = self._colormales
            elif gender == Person.FEMALE:
                colour = self._colorfemales
            elif gender == Person.OTHER:
                colour = self._colorother

            # see if we have surname colours that match this person
            surname = person.get_primary_name().get_surname()
            surname = surname.encode("iso-8859-1", "xmlcharrefreplace")
            if surname in self._surnamecolors:
                colour = self._surnamecolors[surname]

            # see if we have a birth/death or fallback dates we can use
            if self._incdates or self._incplaces:
                bth_event = get_birth_or_fallback(self._db, person)
                dth_event = get_death_or_fallback(self._db, person)
            else:
                bth_event = None
                dth_event = None

            # output the birth or fallback event
            birth_str = None
            if bth_event and self._incdates:
                date = bth_event.get_date_object()
                if self._just_years and date.get_year_valid():
                    birth_str = self.get_date(Date(date.get_year()))  # localized year
                else:
                    birth_str = self.get_date(date)

            # get birth place (one of:  hamlet, village, town, city, parish,
            # county, province, region, state or country)
            birthplace = None
            if bth_event and self._incplaces:
                birthplace = self.get_event_place(bth_event)

            # see if we have a deceased date we can use
            death_str = None
            if dth_event and self._incdates:
                date = dth_event.get_date_object()
                if self._just_years and date.get_year_valid():
                    death_str = self.get_date(Date(date.get_year()))  # localized year
                else:
                    death_str = self.get_date(date)

            # get death place (one of:  hamlet, village, town, city, parish,
            # county, province, region, state or country)
            deathplace = None
            if dth_event and self._incplaces:
                deathplace = self.get_event_place(dth_event)

            # see if we have an image to use for this person
            image_path = None
            if self._incimages:
                media_list = person.get_media_list()
                if len(media_list) > 0:
                    media_handle = media_list[0].get_reference_handle()
                    media = self._db.get_media_from_handle(media_handle)
                    media_mime_type = media.get_mime_type()
                    if media_mime_type[0:5] == "image":
                        image_path = get_thumbnail_path(
                            media_path_full(self._db, media.get_path()),
                            rectangle=media_list[0].get_rectangle(),
                            size=self._imagesize,
                        )

            # put the label together and output this person
            label = ""
            line_delimiter = "\\n"
            if use_html_output:
                line_delimiter = "<BR/>"

            # if we have an image, then start an HTML table;
            # remember to close the table afterwards!
            if image_path:
                label = (
                    '<TABLE BORDER="0" CELLSPACING="2" CELLPADDING="0" '
                    'CELLBORDER="0"><TR><TD><IMG SRC="%s"/></TD>' % image_path
                )
                if self._imageonside == 0:
                    label += "</TR><TR>"
                label += "<TD>"

            # at the very least, the label must have the person's name
            label += html.escape(name)
            if self.includeid == 1:  # same line
                label += " (%s)" % p_id
            elif self.includeid == 2:  # own line
                label += "%s(%s)" % (line_delimiter, p_id)

            if birth_str or death_str:
                label += "%s(" % line_delimiter
                if birth_str:
                    label += "%s" % birth_str
                label += " – "
                if death_str:
                    label += "%s" % death_str
                label += ")"
            if birthplace or deathplace:
                if birthplace == deathplace:
                    deathplace = None  # no need to print the same name twice
                label += "%s" % line_delimiter
                if birthplace:
                    label += "%s" % birthplace
                if birthplace and deathplace:
                    label += " / "
                if deathplace:
                    label += "%s" % deathplace

            # see if we have a table that needs to be terminated
            if image_path:
                label += "</TD></TR></TABLE>"
            else:
                # non html label is enclosed by "" so escape other "
                label = label.replace('"', '\\"')

            shape = "box"
            style = "solid"
            border = colour
            fill = colour

            # do not use colour if this is B&W outline
            if self._colorize == "outline":
                border = ""
                fill = ""

            if gender == person.FEMALE and ("f" in self._useroundedcorners):
                style = "rounded"
            elif gender == person.MALE and ("m" in self._useroundedcorners):
                style = "rounded"
            elif gender == person.UNKNOWN:
                shape = "hexagon"

            # if we're filling the entire node:
            if self._colorize == "filled":
                style += ",filled"
                border = ""

            # we're done -- add the node
            self.doc.add_node(
                p_id,
                label=label,
                shape=shape,
                color=border,
                style=style,
                fillcolor=fill,
                htmloutput=use_html_output,
            )

    def write_families(self):
        """write the families"""

        self.doc.add_comment("")
        ngettext = self._locale.translation.ngettext  # to see "nearby" comments

        # loop through all the families we need to output
        for family_handle in sorted(self._families):  # enable a diff
            family = self._db.get_family_from_handle(family_handle)
            fgid = family.get_gramps_id()

            # figure out a wedding date or placename we can use
            wedding_date = None
            wedding_place = None
            if self._incdates or self._incplaces:
                for event_ref in family.get_event_ref_list():
                    event = self._db.get_event_from_handle(event_ref.ref)
                    if event.get_type() == EventType.MARRIAGE and (
                        event_ref.get_role() == EventRoleType.FAMILY
                        or event_ref.get_role() == EventRoleType.PRIMARY
                    ):
                        # get the wedding date
                        if self._incdates:
                            date = event.get_date_object()
                            if self._just_years and date.get_year_valid():
                                wedding_date = self.get_date(  # localized year
                                    Date(date.get_year())
                                )
                            else:
                                wedding_date = self.get_date(date)
                        # get the wedding location
                        if self._incplaces:
                            wedding_place = self.get_event_place(event)
                        break

            # figure out the number of children (if any)
            children_str = None
            if self._incchildcount:
                child_count = len(family.get_child_ref_list())
                if child_count >= 1:
                    # Translators: leave all/any {...} untranslated
                    children_str = ngettext(
                        "{number_of} child", "{number_of} children", child_count
                    ).format(number_of=child_count)

            label = ""
            fgid_already = False
            if wedding_date:
                if label != "":
                    label += "\\n"
                label += "%s" % wedding_date
                if self.includeid == 1 and not fgid_already:  # same line
                    label += " (%s)" % fgid
                    fgid_already = True
            if wedding_place:
                if label != "":
                    label += "\\n"
                label += "%s" % wedding_place
                if self.includeid == 1 and not fgid_already:  # same line
                    label += " (%s)" % fgid
                    fgid_already = True
            if self.includeid == 1 and not label:
                label = "(%s)" % fgid
                fgid_already = True
            elif self.includeid == 2 and not label:  # own line
                label = "(%s)" % fgid
                fgid_already = True
            elif self.includeid == 2 and label and not fgid_already:
                label += "\\n(%s)" % fgid
                fgid_already = True
            if children_str:
                if label != "":
                    label += "\\n"
                label += "%s" % children_str
                if self.includeid == 1 and not fgid_already:  # same line
                    label += " (%s)" % fgid
                    fgid_already = True

            shape = "ellipse"
            style = "solid"
            border = self._colorfamilies
            fill = self._colorfamilies

            # do not use colour if this is B&W outline
            if self._colorize == "outline":
                border = ""
                fill = ""

            # if we're filling the entire node:
            if self._colorize == "filled":
                style += ",filled"
                border = ""

            # we're done -- add the node
            self.doc.add_node(fgid, label, shape, border, style, fill)

        # now that we have the families written,
        # go ahead and link the parents and children to the families
        for family_handle in self._families:
            # get the parents for this family
            family = self._db.get_family_from_handle(family_handle)
            fgid = family.get_gramps_id()
            father_handle = family.get_father_handle()
            mother_handle = family.get_mother_handle()

            self.doc.add_comment("")

            if self._usesubgraphs and father_handle and mother_handle:
                self.doc.start_subgraph(fgid)

            # see if we have a father to link to this family
            if father_handle:
                if father_handle in self._people:
                    father = self._db.get_person_from_handle(father_handle)
                    father_rn = father.get_primary_name().get_regular_name()
                    comment = self._("father: %s") % father_rn
                    self.doc.add_link(
                        father.get_gramps_id(),
                        fgid,
                        "",
                        self._arrowheadstyle,
                        self._arrowtailstyle,
                        comment=comment,
                    )

            # see if we have a mother to link to this family
            if mother_handle:
                if mother_handle in self._people:
                    mother = self._db.get_person_from_handle(mother_handle)
                    mother_rn = mother.get_primary_name().get_regular_name()
                    comment = self._("mother: %s") % mother_rn
                    self.doc.add_link(
                        mother.get_gramps_id(),
                        fgid,
                        "",
                        self._arrowheadstyle,
                        self._arrowtailstyle,
                        comment=comment,
                    )

            if self._usesubgraphs and father_handle and mother_handle:
                self.doc.end_subgraph()

            # link the children to the family
            for childref in family.get_child_ref_list():
                if childref.ref in self._people:
                    child = self._db.get_person_from_handle(childref.ref)
                    child_rn = child.get_primary_name().get_regular_name()
                    comment = self._("child: %s") % child_rn
                    self.doc.add_link(
                        fgid,
                        child.get_gramps_id(),
                        "",
                        self._arrowheadstyle,
                        self._arrowtailstyle,
                        comment=comment,
                    )

    def get_event_place(self, event):
        """get the place of the event"""
        place_text = ""
        place_handle = event.get_place_handle()
        if place_handle:
            place = self._db.get_place_from_handle(place_handle)
            if place:
                place_text = _pd.display(self._db, place)
                place_text = html.escape(place_text)
        return place_text

    def get_date(self, date):
        """return a formatted date"""
        return html.escape(self._get_date(date))
