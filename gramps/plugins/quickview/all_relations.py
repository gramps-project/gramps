#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  B. Malengier
# Copyright (C) 2008  Brian G. Matherly
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
#

"""
Display a person's relations to the home person
"""
# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------

from gramps.gen.simple import SimpleAccess, SimpleDoc
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gen.relationship import get_relationship_calculator

# define the formatting string once as a constant. Since this is reused

_FMT = "%-3d %s"
_FMT_VOID = "    %s"
_FMT_DET1 = "%-3s %-15s"
_FMT_DET2 = "%-30s %-15s\t%-10s %-2s"


def run(database, document, person):
    """
    Create the report class, and produce the quick report
    """
    report = AllRelReport(database, document, person)
    report.run()


class AllRelReport:
    """
    Obtains all relationships, displays the relations, and in details, the
    relation path
    """

    def __init__(self, database, document, person):
        self.database = database
        self.person = person
        self.sdb = SimpleAccess(database)
        self.sdoc = SimpleDoc(document)
        self.rel_class = get_relationship_calculator(glocale)

        self.msg_list = []

    def run(self):
        # get home_person
        self.home_person = self.database.get_default_person()
        if not self.home_person:
            self.sdoc.paragraph(_("Home person not set."))
            return

        self.print_title()

        p2 = self.sdb.name(self.home_person)
        p1 = self.sdb.name(self.person)
        if self.person.handle == self.home_person.handle:
            self.sdoc.paragraph(
                _FMT_VOID
                % (_("%(person)s and %(active_person)s are the same person."))
                % {"person": p1, "active_person": p2}
            )
            return

        # check if not a family too:
        is_spouse = self.rel_class.is_spouse(
            self.database, self.home_person, self.person
        )
        if is_spouse:
            rel_string = is_spouse
            rstr = _("%(person)s is the %(relationship)s of %(active_person)s.") % {
                "person": p1,
                "relationship": rel_string,
                "active_person": p2,
            }
            self.sdoc.paragraph(_FMT_VOID % (rstr))
            self.sdoc.paragraph("")

        # obtain all relationships, assume home person has largest tree
        common, self.msg_list = self.rel_class.get_relationship_distance_new(
            self.database,
            self.person,
            self.home_person,
            all_families=True,
            all_dist=True,
            only_birth=False,
        )
        # all relations
        if (not common or common[0][0] == -1) and not is_spouse:
            rstr = _(
                "%(person)s and %(active_person)s are not " "directly related."
            ) % {"person": p2, "active_person": p1}
            self.sdoc.paragraph(_FMT_VOID % (rstr))
            self.sdoc.paragraph("")

        # collapse common so parents of same fam in common are one line
        commonnew = self.rel_class.collapse_relations(common)
        self.print_details_header(
            commonnew, self.home_person, self.person, skip_list_text=None
        )
        self.print_details_path(commonnew, self.home_person, self.person)
        self.print_details_path(commonnew, self.home_person, self.person, first=False)

        if not common or common[0][0] == -1:
            self.remarks(self.msg_list)
            self.msg_list = []
            # check inlaw relation next
        else:
            # stop
            return

        # we check the inlaw relationships if not partners.
        if is_spouse:
            return
        handles_done = [(self.person.handle, self.home_person.handle)]
        inlaws_pers = [self.person] + self.get_inlaws(self.person)
        inlaws_home = [self.home_person] + self.get_inlaws(self.home_person)
        # remove overlap:
        inlaws_home = [x for x in inlaws_home if x not in inlaws_pers]
        inlawwritten = False
        skiplist = []
        commonnew = []
        for inlawpers in inlaws_pers:
            for inlawhome in inlaws_home:
                if (inlawpers, inlawhome) in handles_done:
                    continue
                else:
                    handles_done.append((inlawpers, inlawhome))
                common, msg = self.rel_class.get_relationship_distance_new(
                    self.database,
                    inlawpers,
                    inlawhome,
                    all_families=True,
                    all_dist=True,
                    only_birth=False,
                )
                if msg:
                    self.msg_list += msg
                if common and not common[0][0] == -1:
                    if not inlawwritten:
                        rstr = _(
                            "%(person)s and %(active_person)s have "
                            "following in-law relations:"
                        ) % {"person": p2, "active_person": p1}
                        self.sdoc.paragraph(_FMT_VOID % (rstr))
                        self.sdoc.paragraph("")
                        inlawwritten = True
                else:
                    continue
                inlawb = not inlawpers.handle == self.person.handle
                inlawa = not inlawhome.handle == self.home_person.handle
                commonnew.append(
                    (
                        inlawa,
                        inlawb,
                        inlawhome,
                        inlawpers,
                        self.rel_class.collapse_relations(common),
                    )
                )
        skip = []
        skip_text = []
        count = 1
        for inlawa, inlawb, inlawhome, inlawpers, commonrel in commonnew:
            count = self.print_details_header(
                commonrel,
                inlawhome,
                inlawpers,
                inlawa=inlawa,
                inlawb=inlawb,
                count=count,
                skip_list=skip,
                skip_list_text=skip_text,
            )
        count = 1
        for inlawa, inlawb, inlawhome, inlawpers, commonrel in commonnew:
            self.print_details_path(
                commonrel,
                inlawhome,
                inlawpers,
                inlawa=inlawa,
                inlawb=inlawb,
                count=count,
                skip_list=skip,
            )
            count = self.print_details_path(
                commonrel,
                inlawhome,
                inlawpers,
                inlawa=inlawa,
                inlawb=inlawb,
                count=count,
                skip_list=skip,
                first=False,
            )
        self.remarks(self.msg_list, True)

    def get_inlaws(self, person):
        inlaws = []
        family_handles = person.get_family_handle_list()
        for handle in family_handles:
            fam = self.database.get_family_from_handle(handle)
            if fam.father_handle and not fam.father_handle == person.handle:
                inlaws.append(self.database.get_person_from_handle(fam.father_handle))
            elif fam.mother_handle and not fam.mother_handle == person.handle:
                inlaws.append(self.database.get_person_from_handle(fam.mother_handle))
        return inlaws

    def print_title(self):
        """print the title"""
        p2 = self.sdb.name(self.home_person)
        p1 = self.sdb.name(self.person)
        self.sdoc.title(
            _("Relationships of %(person)s to %(active_person)s")
            % {"person": p1, "active_person": p2}
        )
        self.sdoc.paragraph("")

    def print_details_header(
        self,
        relations,
        pers1,
        pers2,
        inlawa=False,
        inlawb=False,
        count=1,
        skip_list=[],
        skip_list_text=[],
    ):
        if not relations or relations[0][0] == -1:
            return count

        sdoc = self.sdoc
        rel_class = self.rel_class
        for relation in relations:
            birth = self.rel_class.only_birth(
                relation[2]
            ) and self.rel_class.only_birth(relation[4])
            distorig = len(relation[4])
            distother = len(relation[2])
            if distorig == distother == 1 and not inlawa and not inlawb:
                rel_str = self.rel_class.get_sibling_relationship_string(
                    self.rel_class.get_sibling_type(self.database, pers1, pers2),
                    self.home_person.get_gender(),
                    self.person.get_gender(),
                )
            else:
                rel_str = self.rel_class.get_single_relationship_string(
                    distorig,
                    distother,
                    self.home_person.get_gender(),
                    self.person.get_gender(),
                    relation[4],
                    relation[2],
                    only_birth=birth,
                    in_law_a=inlawa,
                    in_law_b=inlawb,
                )
            if skip_list_text is not None:
                if rel_str in skip_list_text:
                    skip_list.append(count)
                else:
                    skip_list_text.append(rel_str)
                    sdoc.paragraph(_FMT % (count - len(skip_list), rel_str))
            else:
                sdoc.paragraph(_FMT % (count, rel_str))
            count += 1
        return count

    def print_details_path(
        self,
        relations,
        pers1,
        pers2,
        inlawa=False,
        inlawb=False,
        count=1,
        skip_list=[],
        first=True,
    ):
        if not relations or relations[0][0] == -1:
            return count

        sdoc = self.sdoc
        rel_class = self.rel_class
        p2 = self.sdb.name(self.home_person)
        p1 = self.sdb.name(self.person)
        pers = p2
        inlaw = inlawa
        if first:
            pers = p1
            inlaw = inlawb

        if count == 1:
            sdoc.paragraph("")
            sdoc.header1(
                _("Detailed path from %(person)s to common ancestor") % {"person": pers}
            )
            sdoc.paragraph("")
            sdoc.header2(_FMT_DET1 % ("   ", _("Name Common ancestor")))
            sdoc.header2(_FMT_DET2 % (" ", _("Parent"), _("Birth"), _("Family")))
            sdoc.paragraph("")
        for relation in relations:
            if count in skip_list:
                count += 1
                continue
            counter = str(count - len([x for x in range(count) if x + 1 in skip_list]))
            name = _("Unknown")
            if relation[1]:
                name = self.sdb.name(
                    self.database.get_person_from_handle(relation[1][0])
                )
                for handle in relation[1][1:]:
                    name += (
                        " "
                        + _("and")
                        + " "
                        + self.sdb.name(self.database.get_person_from_handle(handle))
                    )
            sdoc.paragraph(_FMT_DET1 % (counter, name))
            if inlaw:
                sdoc.paragraph(_FMT_DET2 % (" ", _("Partner"), " ", " "))
            if first:
                ind1 = 2
                ind2 = 3
            else:
                ind1 = 4
                ind2 = 5
            for rel, fam in zip(relation[ind1], relation[ind2]):
                par_str = _("Unknown")  # when sibling, parent is unknown
                if rel == rel_class.REL_MOTHER or rel == rel_class.REL_MOTHER_NOTBIRTH:
                    par_str = _("Mother")
                if rel == rel_class.REL_FATHER or rel == rel_class.REL_FATHER_NOTBIRTH:
                    par_str = _("Father")
                if (
                    rel == rel_class.REL_FAM_BIRTH
                    or rel == rel_class.REL_FAM_NONBIRTH
                    or rel == rel_class.REL_FAM_BIRTH_MOTH_ONLY
                    or rel == rel_class.REL_FAM_BIRTH_FATH_ONLY
                ):
                    par_str = _("Parents")
                birth_str = _("Yes")
                if (
                    rel == rel_class.REL_MOTHER_NOTBIRTH
                    or rel == rel_class.REL_FATHER_NOTBIRTH
                    or rel == rel_class.REL_FAM_NONBIRTH
                ):
                    birth_str = _("No")
                elif (
                    rel == rel_class.REL_FAM_BIRTH_FATH_ONLY
                    or rel == rel_class.REL_FAM_BIRTH_MOTH_ONLY
                ):
                    birth_str = _("Partial")
                famstr = ""
                if isinstance(fam, list):
                    famstr = str(fam[0] + 1)
                    for val in fam[1:]:
                        # TODO for Arabic, should the next comma be translated?
                        famstr += ", " + str(val + 1)
                else:
                    famstr = str(fam + 1)
                sdoc.paragraph(_FMT_DET2 % (" ", par_str, birth_str, famstr))
                counter = ""
                name = ""
            count += 1
        return count

    def remarks(self, msg_list, inlaw=False):
        if msg_list:
            sdoc = self.sdoc
            sdoc.paragraph("")
            if inlaw:
                sdoc.header1(_("Remarks with inlaw family"))
            else:
                sdoc.header1(_("Remarks"))
            sdoc.paragraph("")
            sdoc.paragraph(_("The following problems were encountered:"))

            list(map(sdoc.paragraph, msg_list))
            sdoc.paragraph("")
            sdoc.paragraph("")
