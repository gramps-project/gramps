#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Martin Hawlisch, Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2013       Vassilii Khachaturov
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

"Import from GeneWeb"

# -------------------------------------------------------------------------
#
# standard python modules
#
# -------------------------------------------------------------------------
import re
import time

# ------------------------------------------------------------------------
#
# Set up logging
#
# ------------------------------------------------------------------------
import logging

LOG = logging.getLogger(".ImportGeneWeb")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.utils.libformatting import ImportInfo

_ = glocale.translation.gettext
ngettext = glocale.translation.ngettext  # else "nearby" comments are ignored
from gramps.gen.errors import GedcomError, GrampsImportError
from gramps.gen.lib import (
    Attribute,
    AttributeType,
    ChildRef,
    Citation,
    Date,
    DateError,
    Event,
    EventRef,
    EventRoleType,
    EventType,
    Family,
    FamilyRelType,
    Name,
    NameType,
    Note,
    Person,
    PersonRef,
    Place,
    PlaceName,
    Source,
    LdsOrd,
)
from gramps.gen.db import DbTxn
from html.entities import name2codepoint

_date_parse = re.compile(
    r"([kmes~?<>]+)?([0-9/]+)([J|H|F])?(\.\.)?([0-9/]+)?([J|H|F])?"
)
_text_parse = re.compile(r"0\((.*)\)")

_mod_map = {
    ">": Date.MOD_AFTER,
    "<": Date.MOD_BEFORE,
    "~": Date.MOD_ABOUT,
}

_cal_map = {
    "J": Date.CAL_JULIAN,
    "H": Date.CAL_HEBREW,
    "F": Date.CAL_FRENCH,
}

pevents_map = {
    "#birt": EventType.BIRTH,  # Epers_Birth
    "#bapt": EventType.BAPTISM,  # Epers_Baptism
    "#deat": EventType.DEATH,  # Epers_Death
    "#buri": EventType.BURIAL,  # Epers_Burial
    "#crem": EventType.CREMATION,
    "#acco": EventType((EventType.CUSTOM, _("Accomplishment"))),
    "#acqu": EventType((EventType.CUSTOM, _("Acquisition"))),
    "#adhe": EventType((EventType.CUSTOM, _("Adhesion"))),
    "#awar": EventType((EventType.CUSTOM, _("Award"))),
    "#bapl": LdsOrd.BAPTISM,  # Epers_BaptismLDS
    "#barm": EventType.BAR_MITZVAH,  # Epers_BarMitzvah
    "#basm": EventType.BAS_MITZVAH,  # Epers_BatMitzvah
    "#bles": EventType.BLESS,  # Epers_Benediction
    "#cens": EventType.CENSUS,
    "#chgn": EventType((EventType.CUSTOM, _("Change Name"))),
    "#circ": EventType((EventType.CUSTOM, _("Circumcision"))),
    "#conf": EventType.CONFIRMATION,  # Epers_Confirmation
    "#conl": LdsOrd.CONFIRMATION,  # Epers_ConfirmationLDS
    "#degr": EventType.DEGREE,
    "#demm": EventType((EventType.CUSTOM, _("Military Demobilisation"))),
    "#dist": EventType((EventType.CUSTOM, _("Award"))),
    "#dotl": LdsOrd.ENDOWMENT,  # Epers_DotationLDS
    "#educ": EventType.EDUCATION,  # Epers_Education
    "#elec": EventType.ELECTED,  # Epers_Election
    "#emig": EventType.EMIGRATION,
    "#endl": EventType((EventType.CUSTOM, _("Dotation"))),
    "#exco": EventType((EventType.CUSTOM, _("Excommunication"))),
    "#fcom": EventType.FIRST_COMMUN,
    "#flkl": EventType((EventType.CUSTOM, _("LDS Family Link"))),
    "#fune": EventType((EventType.CUSTOM, _("Funeral"))),
    "#grad": EventType.GRADUATION,
    "#hosp": EventType((EventType.CUSTOM, _("Hospitalisation"))),
    "#illn": EventType((EventType.CUSTOM, _("Illness"))),
    "#immi": EventType.IMMIGRATION,
    "#lpas": EventType((EventType.CUSTOM, _("List Passenger"))),
    "#mdis": EventType((EventType.CUSTOM, _("Military Distinction"))),
    "#mobm": EventType((EventType.CUSTOM, _("Militaty Mobilisation"))),
    "#mpro": EventType((EventType.CUSTOM, _("Military Promotion"))),
    "#mser": EventType.MILITARY_SERV,  # Epers_MilitaryService
    "#natu": EventType.NATURALIZATION,  # Epers_Naturalisation
    "#occu": EventType.OCCUPATION,  # Epers_Occupation
    "#ordn": EventType.ORDINATION,  # Epers_Ordination
    "#prop": EventType.PROPERTY,  # Epers_Property
    "#resi": EventType.RESIDENCE,  # Epers_Residence
    "#reti": EventType.RETIREMENT,
    "#slgc": EventType(
        (EventType.CUSTOM, _("LDS Seal to child"))
    ),  # Epers_ScellentChildLDS
    "#slgp": LdsOrd.SEAL_TO_PARENTS,  # Epers_ScellentParentLDS
    "#slgs": LdsOrd.SEAL_TO_SPOUSE,
    "#vteb": EventType((EventType.CUSTOM, _("Sold property"))),  # Epers_VenteBien
    "#will": EventType.WILL,  # Epers_Will
}

fevents_map = {
    "#marr": EventType.MARRIAGE,  # Efam_Marriage
    "#nmar": EventType.NUM_MARRIAGES,
    "#nmen": EventType((EventType.CUSTOM, _("No mention"))),  # Efam_NoMention
    "#enga": EventType.ENGAGEMENT,  # Efam_Engage
    "#div": EventType.DIVORCE,
    "#sep": EventType((EventType.CUSTOM, _("Separated"))),  # Efam_Separated
    "#anul": EventType.ANNULMENT,  # Efam_Annulation
    "#marb": EventType.MARR_BANNS,  # Efam_MarriageBann
    "#marc": EventType.MARR_CONTR,  # Efam_MarriageContract)
    "#marl": EventType.MARR_LIC,  # Efam_MarriageLicense)
    "#resi": EventType.RESIDENCE,  # Efam_Residence)
}


# -------------------------------------------------------------------------
#
#
#
# -------------------------------------------------------------------------
def importData(database, filename, user):
    global callback

    try:
        g = GeneWebParser(database, filename)
    except IOError as msg:
        user.notify_error(_("%s could not be opened\n") % filename, str(msg))
        return

    try:
        status = g.parse_geneweb_file()
    except IOError as msg:
        errmsg = _("%s could not be opened\n") % filename
        user.notify_error(errmsg, str(msg))
        return
    return ImportInfo({_("Results"): _("done")})


# -------------------------------------------------------------------------
# For a description of the file format see
# http://cristal.inria.fr/~ddr/GeneWeb/en/gwformat.htm
# https://github.com/geneanet/geneweb/issues/315
# -------------------------------------------------------------------------
class GeneWebParser:
    def __init__(self, dbase, file):
        self.db = dbase
        if file:  # Unit tests can create the parser w/o underlying file
            self.f = open(file, "rb")
            self.filename = file
            self.encoding = "iso-8859-1"
            self.gwplus = False

    def get_next_line(self):
        self.lineno += 1
        line = self.f.readline()

        try:
            line = line.decode("utf-8")
        except GrampsImportError as err:
            self.errmsg(str(err))

        if line:
            try:
                line = str(line.strip())
            except UnicodeDecodeError:
                line = line.decode(self.encoding).strip()
        else:
            line = None
        return line

    def parse_geneweb_file(self):
        with DbTxn(_("GeneWeb import"), self.db, batch=True) as self.trans:
            self.db.disable_signals()
            t = time.time()
            self.lineno = 0
            self.index = 0
            self.fam_count = 0
            self.indi_count = 0

            self.fkeys = []
            self.ikeys = {}
            self.pkeys = {}
            self.skeys = {}

            self.current_mode = None
            self.current_family = None
            self.current_husband_handle = None
            self.current_child_birthplace_handle = None
            self.current_child_source_handle = None
            try:
                while 1:
                    line = self.get_next_line()
                    if line is None:
                        break
                    if line == "":
                        continue

                    fields = line.split(" ")

                    LOG.debug("LINE: %s" % line)

                    if fields[0] == "gwplus":
                        self.gwplus = True
                        self.encoding = "utf-8"
                    elif fields[0] == "encoding:":
                        self.encoding = fields[1]
                    elif fields[0] == "fam":
                        self.current_mode = "fam"
                        self.read_family_line(line, fields)
                    elif fields[0] == "rel":
                        self.current_mode = "rel"
                        self.read_relationship_person(line, fields)
                    elif fields[0] == "src":
                        self.read_source_line(line, fields)
                    elif fields[0] in ("wit", "wit:"):
                        self.read_witness_line(line, fields)
                    elif fields[0] == "cbp":
                        self.read_children_birthplace_line(line, fields)
                    elif fields[0] == "csrc":
                        self.read_children_source_line(line, fields)
                    elif fields[0] == "beg" and self.current_mode == "fam":
                        self.read_children_lines()
                    elif fields[0] == "beg" and self.current_mode == "rel":
                        self.read_relation_lines()
                    elif fields[0] == "comm":
                        self.read_family_comment(line, fields)
                    elif fields[0] == "notes":
                        self.read_person_notes_lines(line, fields)
                    elif fields[0] == "fevt" and self.current_mode == "fam":
                        # self.read_fevent_line(self.get_next_line())
                        pass
                    elif fields[0] == "pevt":
                        # self.read_pevent_line(self.get_next_line(), fields)
                        pass
                    elif fields[0] == "notes-db":
                        self.read_database_notes_lines(line, fields)
                    elif fields[0] == "pages-ext" or "wizard-note":
                        pass
                    elif fields[0] == "end":
                        self.current_mode = None
                    else:
                        LOG.warning(
                            "parse_geneweb_file(): Token >%s< unknown. line %d skipped: %s"
                            % (fields[0], self.lineno, line)
                        )
            except GedcomError as err:
                self.errmsg(str(err))

            t = time.time() - t
            # Translators: leave all/any {...} untranslated
            msg = ngettext(
                "Import Complete: {number_of} second",
                "Import Complete: {number_of} seconds",
                t,
            ).format(number_of=t)

        self.db.enable_signals()
        self.db.request_rebuild()

        LOG.debug(msg)
        LOG.debug("Families: %d" % len(self.fkeys))
        LOG.debug("Individuals: %d" % len(self.ikeys))
        return None

    def read_family_line(self, line, fields):
        self.current_husband_handle = None
        self.current_child_birthplace_handle = None
        self.current_child_source_handle = None
        self.current_family = Family()
        self.db.add_family(self.current_family, self.trans)
        # self.db.commit_family(self.current_family,self.trans)
        self.fkeys.append(self.current_family.get_handle())
        idx = 1

        LOG.debug("\nHusband:")
        (idx, husband) = self.parse_person(fields, idx, Person.MALE, None)
        if husband:
            self.current_husband_handle = husband.get_handle()
            self.current_family.set_father_handle(husband.get_handle())
            self.db.commit_family(self.current_family, self.trans)
            husband.add_family_handle(self.current_family.get_handle())
            self.db.commit_person(husband, self.trans)
        LOG.debug("Marriage:")
        idx = self.parse_marriage(fields, idx)
        LOG.debug("Wife:")
        (idx, wife) = self.parse_person(fields, idx, Person.FEMALE, None)
        if wife:
            self.current_family.set_mother_handle(wife.get_handle())
            self.db.commit_family(self.current_family, self.trans)
            wife.add_family_handle(self.current_family.get_handle())
            self.db.commit_person(wife, self.trans)
        return None

    def read_relationship_person(self, line, fields):
        LOG.debug(r"\Relationships:")
        (idx, person) = self.parse_person(fields, 1, Person.UNKNOWN, None)
        if person:
            self.current_relationship_person_handle = person.get_handle()

    def read_relation_lines(self):
        if not self.current_relationship_person_handle:
            LOG.warning("Unknown person for relationship in line %d!" % self.lineno)
            return None
        rel_person = self.db.get_person_from_handle(
            self.current_relationship_person_handle
        )
        while 1:
            line = self.get_next_line()
            if line is None or line == "end":
                break
            if line == "":
                continue

            # match relationship type and related person
            line_re = re.compile("^- ([^:]+): (.*)$")
            matches = line_re.match(line)
            if matches:
                # split related person into fields
                fields = matches.groups()[1].split(" ")
                if fields:
                    (idx, asso_p) = self.parse_person(fields, 0, Person.UNKNOWN, None)
                    pref = PersonRef()
                    pref.set_relation(matches.groups()[0])
                    LOG.warning("TODO: Handle association types properly")
                    pref.set_reference_handle(asso_p.get_handle())
                    rel_person.add_person_ref(pref)
                    self.db.commit_person(rel_person, self.trans)
                else:
                    LOG.warning("Invalid name of person in line %d" % self.lineno)
            else:
                LOG.warning("Invalid relationship in line %d" % self.lineno)
                break
        self.current_mode = None
        return None

    def read_source_line(self, line, fields):
        if not self.current_family:
            LOG.warning("Unknown family of child in line %d!" % self.lineno)
            return None
        source = self.get_or_create_source(self.decode(fields[1]))
        self.current_family.add_citation(source.get_handle())
        self.db.commit_family(self.current_family, self.trans)
        return None

    def read_witness_line(self, line, fields):
        LOG.debug("Witness:")
        if fields[1] == "m:":
            (idx, wit_p) = self.parse_person(fields, 2, Person.MALE, None)
        elif fields[1] == "f:":
            (idx, wit_p) = self.parse_person(fields, 2, Person.FEMALE, None)
        else:
            (idx, wit_p) = self.parse_person(fields, 1, None, None)
        if wit_p:
            mev = None
            # search marriage event
            for evr in self.current_family.get_event_ref_list():
                ev = self.db.get_event_from_handle(evr.get_reference_handle())
                if ev.get_type() == EventType.MARRIAGE:
                    mev = ev  # found.
            if not mev:  # No marriage event found create a new one
                mev = self.create_event(EventType.MARRIAGE, None, None, None, None)
                mar_ref = EventRef()
                mar_ref.set_reference_handle(mev.get_handle())
                self.current_family.add_event_ref(mar_ref)
            wit_ref = EventRef()
            wit_ref.set_role(EventRoleType(EventRoleType.WITNESS))
            wit_ref.set_reference_handle(mev.get_handle())
            wit_p.add_event_ref(wit_ref)
            self.db.commit_person(wit_p, self.trans)
        return None

    def read_children_lines(self):
        father_surname = "Dummy"
        if not self.current_husband_handle:
            LOG.warning("Unknown father for child in line %d!" % self.lineno)
            return None
        husb = self.db.get_person_from_handle(self.current_husband_handle)
        father_surname = husb.get_primary_name().get_surname()
        if not self.current_family:
            LOG.warning("Unknown family of child in line %d!" % self.lineno)
            return None
        while 1:
            line = self.get_next_line()
            if line is None:
                break
            if line == "":
                continue

            fields = line.split(" ")
            if fields[0] == "-":
                LOG.debug("Child:")
                child = None
                if fields[1] == "h":
                    (idx, child) = self.parse_person(
                        fields, 2, Person.MALE, father_surname
                    )
                elif fields[1] == "f":
                    (idx, child) = self.parse_person(
                        fields, 2, Person.FEMALE, father_surname
                    )
                else:
                    (idx, child) = self.parse_person(
                        fields, 1, Person.UNKNOWN, father_surname
                    )

                if child:
                    childref = ChildRef()
                    childref.set_reference_handle(child.get_handle())
                    self.current_family.add_child_ref(childref)
                    self.db.commit_family(self.current_family, self.trans)
                    child.add_parent_family_handle(self.current_family.get_handle())
                    if self.current_child_birthplace_handle:
                        birth = None
                        birth_ref = child.get_birth_ref()
                        if birth_ref:
                            birth = self.db.get_event_from_handle(birth_ref.ref)
                        if not birth:
                            birth = self.create_event(EventType.BIRTH)
                            birth_ref = EventRef()
                            birth_ref.set_reference_handle(birth.get_handle())
                            child.set_birth_ref(birth_ref)
                        birth.set_place_handle(self.current_child_birthplace_handle)
                        self.db.commit_event(birth, self.trans)
                    if self.current_child_source_handle:
                        child.add_citation(self.current_child_source_handle)
                    self.db.commit_person(child, self.trans)
            else:
                break
        self.current_mode = None
        return None

    def read_children_birthplace_line(self, line, fields):
        cbp = self.get_or_create_place(self.decode(fields[1]))
        if cbp:
            self.current_child_birthplace_handle = cbp.get_handle()
        return None

    def read_children_source_line(self, line, fields):
        csrc = self.get_or_create_source(self.decode(fields[1]))
        self.current_child_source_handle = csrc.handle
        return None

    def read_family_comment(self, line, fields):
        if not self.current_family:
            LOG.warning("Unknown family of child in line %d!" % self.lineno)
            return None
        n = Note()
        n.set(line)
        self.db.add_note(n, self.trans)
        self.current_family.add_note(n.handle)
        self.db.commit_family(self.current_family, self.trans)
        return None

    def _read_notes_lines(self, note_tag):
        note_txt = ""
        while True:
            line = self.get_next_line()
            if line is None:
                break

            fields = line.split(" ")
            if fields[0] == "end" and fields[1] == note_tag:
                break
            elif fields[0] == "beg":
                continue
            else:
                if note_txt:
                    note_txt = note_txt + "\n" + line
                else:
                    note_txt = note_txt + line
        if note_txt:
            n = Note()
            n.set(note_txt)
            self.db.add_note(n, self.trans)
            return n.handle
        return None

    def read_person_notes_lines(self, line, fields):
        (idx, person) = self.parse_person(fields, 1, None, None)
        note_handle = self._read_notes_lines(fields[0])
        if note_handle:
            person.add_note(note_handle)
            self.db.commit_person(person, self.trans)

    def read_database_notes_lines(self, line, fields):
        note_handle = self._read_notes_lines(fields[0])

    def parse_marriage(self, fields, idx):
        mariageDataRe = re.compile("^[+#-0-9].*$")

        mar_date = None
        mar_place = None
        mar_source = None

        sep_date = None
        div_date = None

        married = 1
        engaged = 0

        # skip to marriage date in case person contained unmatches tokens
        # Alex: this failed when fields[idx] was an empty line. Fixed.
        # while idx < len(fields) and not fields[idx][0] == "+":
        while idx < len(fields) and not (fields[idx] and fields[idx][0] == "+"):
            if fields[idx]:
                LOG.warning(
                    ("parse_marriage(): Unknown field: " + "'%s' in line %d!")
                    % (fields[idx], self.lineno)
                )
            idx += 1

        while idx < len(fields) and mariageDataRe.match(fields[idx]):
            field = fields[idx]
            idx += 1
            if field.startswith("+"):
                field = field[1:]
                mar_date = self.parse_date(self.decode(field))
                LOG.debug(" Married at: %s" % field)
            elif field.startswith("-"):
                field = field[1:]
                div_date = self.parse_date(self.decode(field))
                LOG.debug(" Div at: %s" % field)
            elif field == "#mp" and idx < len(fields):
                mar_place = self.get_or_create_place(self.decode(fields[idx]))
                LOG.debug(" Marriage place: %s" % fields[idx])
                idx += 1
            elif field == "#ms" and idx < len(fields):
                mar_source = self.get_or_create_source(self.decode(fields[idx]))
                LOG.debug(" Marriage source: %s" % fields[idx])
                idx += 1
            elif field == "#sep" and idx < len(fields):
                sep_date = self.parse_date(self.decode(fields[idx]))
                LOG.debug(" Seperated since: %s" % fields[idx])
                idx += 1
            elif field == "#nm":
                LOG.debug(" Are not married.")
                married = 0
            elif field == "#noment":
                LOG.debug(" Not mentioned.")
            elif field == "#eng":
                LOG.debug(" Are engaged.")
                engaged = 1
            else:
                LOG.warning(
                    ("parse_marriage(): Unknown field " + "'%s'for mariage in line %d!")
                    % (field, self.lineno)
                )

        if mar_date or mar_place or mar_source:
            mar = self.create_event(
                EventType.MARRIAGE, None, mar_date, mar_place, mar_source
            )
            mar_ref = EventRef()
            mar_ref.set_reference_handle(mar.get_handle())
            mar_ref.set_role(EventRoleType.FAMILY)
            self.current_family.add_event_ref(mar_ref)
            self.current_family.set_relationship(FamilyRelType(FamilyRelType.MARRIED))

        if div_date:
            div = self.create_event(EventType.DIVORCE, None, div_date, None, None)
            div_ref = EventRef()
            div_ref.set_reference_handle(div.get_handle())
            div_ref.set_role(EventRoleType.FAMILY)
            self.current_family.add_event_ref(div_ref)

        if sep_date or engaged:
            sep = self.create_event(EventType.ENGAGEMENT, None, sep_date, None, None)
            sep_ref = EventRef()
            sep_ref.set_reference_handle(sep.get_handle())
            sep_ref.set_role(EventRoleType.FAMILY)
            self.current_family.add_event_ref(sep_ref)

        if not married:
            self.current_family.set_relationship(FamilyRelType(FamilyRelType.UNMARRIED))

        self.db.commit_family(self.current_family, self.trans)
        return idx

    def parse_person(self, fields, idx, gender, father_surname):
        if not father_surname:
            if not idx < len(fields):
                LOG.warning("Missing surname of person in line %d!" % self.lineno)
                surname = ""
            else:
                surname = self.decode(fields[idx])
            idx += 1
        else:
            surname = father_surname

        if not idx < len(fields):
            LOG.warning("Missing firstname of person in line %d!" % self.lineno)
            firstname = ""
        else:
            firstname = self.decode(fields[idx])
        idx += 1
        if idx < len(fields) and father_surname:
            noSurnameRe = re.compile(r"^[({\[~><?0-9#].*$")
            if not noSurnameRe.match(fields[idx]):
                surname = self.decode(fields[idx])
                idx += 1

        LOG.debug("Person: %s %s" % (firstname, surname))
        person = self.get_or_create_person(firstname, surname)
        name = Name()
        name.set_type(NameType(NameType.BIRTH))
        name.set_first_name(firstname)
        surname_obj = name.get_primary_surname()
        surname_obj.set_surname(surname)
        person.set_primary_name(name)
        if person.get_gender() == Person.UNKNOWN and gender is not None:
            person.set_gender(gender)
        self.db.commit_person(person, self.trans)
        personDataRe = re.compile(r"^[kmes0-9<>~#\[({!].*$")
        dateRe = re.compile("^[kmes0-9~<>?]+.*$")

        source = None
        birth_parsed = False
        birth_date = None
        birth_place = None
        birth_source = None

        bapt_date = None
        bapt_place = None
        bapt_source = None

        death_date = None
        death_place = None
        death_source = None
        death_cause = None

        crem_date = None
        bur_date = None
        bur_place = None
        bur_source = None

        public_name = None
        firstname_aliases = []
        nick_names = []
        name_aliases = []
        surname_aliases = []

        while idx < len(fields) and personDataRe.match(fields[idx]):
            field = fields[idx]
            idx += 1
            if field.startswith("("):
                LOG.debug("Public Name: %s" % field)
                public_name = self.decode(field[1:-1])
            elif field.startswith("{"):
                LOG.debug("Firstsname Alias: %s" % field)
                firstname_aliases.append(self.decode(field[1:-1]))
            elif field.startswith("["):
                LOG.debug("Title: %s" % field)
                titleparts = self.decode(field[1:-1]).split(":")
                tname = ttitle = tplace = tstart = tend = tnth = None
                try:
                    tname = titleparts[0]
                    ttitle = titleparts[1]
                    if titleparts[2]:
                        tplace = self.get_or_create_place(titleparts[2])
                    tstart = self.parse_date(titleparts[3])
                    tend = self.parse_date(titleparts[4])
                    tnth = titleparts[5]
                except IndexError:  # not all parts are written all the time
                    pass
                if tnth:  # Append title numer to title
                    # TODO for Arabic, should the next comma be translated?
                    ttitle += ", " + tnth
                title = self.create_event(EventType.NOB_TITLE, ttitle, tstart, tplace)
                # TODO: Geneweb has a start date and an end date, and therefore
                # supports stuff like: FROM about 1955 TO between 1998 and 1999
                # gramps only supports one single date or range.
                if tname and tname != "*":
                    n = Note()
                    n.set(tname)
                    self.db.add_note(n, self.trans)
                    title.add_note(n.handle)
                title_ref = EventRef()
                title_ref.set_reference_handle(title.get_handle())
                person.add_event_ref(title_ref)
            elif field == "#nick" and idx < len(fields):
                LOG.debug("Nick Name: %s" % fields[idx])
                nick_names.append(self.decode(fields[idx]))
                idx += 1
            elif field == "#occu" and idx < len(fields):
                LOG.debug("Occupation: %s" % fields[idx])
                occu = self.create_event(EventType.OCCUPATION, self.decode(fields[idx]))
                occu_ref = EventRef()
                occu_ref.set_reference_handle(occu.get_handle())
                person.add_event_ref(occu_ref)
                idx += 1
            elif field == "#alias" and idx < len(fields):
                LOG.debug("Name Alias: %s" % fields[idx])
                name_aliases.append(self.decode(fields[idx]))
                idx += 1
            elif field == "#salias" and idx < len(fields):
                LOG.debug("Surname Alias: %s" % fields[idx])
                surname_aliases.append(self.decode(fields[idx]))
                idx += 1
            elif field == "#image" and idx < len(fields):
                LOG.debug("Image: %s" % fields[idx])
                idx += 1
            elif field == "#src" and idx < len(fields):
                LOG.debug("Source: %s" % fields[idx])
                source = self.get_or_create_source(self.decode(fields[idx]))
                idx += 1
            elif field == "#bs" and idx < len(fields):
                LOG.debug("Birth Source: %s" % fields[idx])
                birth_source = self.get_or_create_source(self.decode(fields[idx]))
                idx += 1
            elif field[0] == "!":
                LOG.debug("Baptize at: %s" % field[1:])
                bapt_date = self.parse_date(self.decode(field[1:]))
            elif field == "#bp" and idx < len(fields):
                LOG.debug("Birth Place: %s" % fields[idx])
                birth_place = self.get_or_create_place(self.decode(fields[idx]))
                idx += 1
            elif field == "#pp" and idx < len(fields):
                LOG.debug("Baptize Place: %s" % fields[idx])
                bapt_place = self.get_or_create_place(self.decode(fields[idx]))
                idx += 1
            elif field == "#ps" and idx < len(fields):
                LOG.debug("Baptize Source: %s" % fields[idx])
                bapt_source = self.get_or_create_source(self.decode(fields[idx]))
                idx += 1
            elif field == "#dp" and idx < len(fields):
                LOG.debug("Death Place: %s" % fields[idx])
                death_place = self.get_or_create_place(self.decode(fields[idx]))
                idx += 1
            elif field == "#ds" and idx < len(fields):
                LOG.debug("Death Source: %s" % fields[idx])
                death_source = self.get_or_create_source(self.decode(fields[idx]))
                idx += 1
            elif field == "#buri" and idx < len(fields):
                if fields[idx][0] != "#":  # bug in GeneWeb: empty #buri fields
                    LOG.debug("Burial Date: %s" % fields[idx])
                    bur_date = self.parse_date(self.decode(fields[idx]))
                    idx += 1
            elif field == "#crem" and idx < len(fields):
                LOG.debug("Cremention Date: %s" % fields[idx])
                crem_date = self.parse_date(self.decode(fields[idx]))
                idx += 1
            elif field == "#rp" and idx < len(fields):
                LOG.debug("Burial Place: %s" % fields[idx])
                bur_place = self.get_or_create_place(self.decode(fields[idx]))
                idx += 1
            elif field == "#rs" and idx < len(fields):
                LOG.debug("Burial Source: %s" % fields[idx])
                bur_source = self.get_or_create_source(self.decode(fields[idx]))
                idx += 1
            elif field == "#apubl":
                LOG.debug("This is a public record")
            elif field == "#apriv":
                LOG.debug("This is a private record")
                person.set_privacy(True)
            elif field == "#h":
                LOG.debug("This is a restricted record")
                # TODO: Gramps does currently not feature this level
                person.set_privacy(True)
            elif dateRe.match(field):
                if not birth_parsed:
                    LOG.debug("Birth Date: %s" % field)
                    birth_date = self.parse_date(self.decode(field))
                    birth_parsed = True
                else:
                    LOG.debug("Death Date: %s" % field)
                    death_date = self.parse_date(self.decode(field))
                    if field == "mj":
                        death_cause = "Died joung"
                    elif field.startswith("k"):
                        death_cause = "Killed"
                    elif field.startswith("m"):
                        death_cause = "Murdered"
                    elif field.startswith("e"):
                        death_cause = "Executed"
                    elif field.startswith("d"):
                        death_cause = "Disappeared"
                    # TODO: Set special death types more properly
            else:
                LOG.warning(
                    ("parse_person(): Unknown field " + "'%s' for person in line %d!")
                    % (field, self.lineno)
                )

        if public_name:
            name = person.get_primary_name()
            name.set_type(NameType(NameType.BIRTH))
            person.add_alternate_name(name)
            name = Name()
            name.set_type(NameType(NameType.AKA))
            name.set_first_name(public_name)
            surname_obj = name.get_primary_surname()
            surname_obj.set_surname(surname)
            person.set_primary_name(name)

        for aka in nick_names:
            name = Attribute()
            name.set_type(AttributeType(AttributeType.NICKNAME))
            name.set_value(aka)
            person.add_attribute(name)

        for aka in firstname_aliases:
            name = Name()
            name.set_type(NameType(NameType.AKA))
            name.set_first_name(aka)
            surname_obj = name.get_primary_surname()
            surname_obj.set_surname(surname)
            person.add_alternate_name(name)

        for aka in name_aliases:
            name = Name()
            name.set_type(NameType(NameType.AKA))
            name.set_first_name(aka)
            surname_obj = name.get_primary_surname()
            surname_obj.set_surname(surname)
            person.add_alternate_name(name)

        for aka in surname_aliases:
            name = Name()
            name.set_type(NameType(NameType.AKA))
            if public_name:
                name.set_first_name(public_name)
            else:
                name.set_first_name(firstname)
            surname_obj = name.get_primary_surname()
            surname_obj.set_surname(aka)
            person.add_alternate_name(name)

        if source:
            person.add_citation(source.get_handle())

        if birth_date or birth_place or birth_source:
            birth = self.create_event(
                EventType.BIRTH, None, birth_date, birth_place, birth_source
            )
            birth_ref = EventRef()
            birth_ref.set_reference_handle(birth.get_handle())
            person.set_birth_ref(birth_ref)

        if bapt_date or bapt_place or bapt_source:
            babt = self.create_event(
                EventType.BAPTISM, None, bapt_date, bapt_place, bapt_source
            )
            babt_ref = EventRef()
            babt_ref.set_reference_handle(babt.get_handle())
            person.add_event_ref(babt_ref)

        if death_date or death_place or death_source or death_cause:
            death = self.create_event(
                EventType.DEATH, None, death_date, death_place, death_source
            )
            if death_cause:
                death.set_description(death_cause)
                self.db.commit_event(death, self.trans)
            death_ref = EventRef()
            death_ref.set_reference_handle(death.get_handle())
            person.set_death_ref(death_ref)

        if bur_date:
            bur = self.create_event(
                EventType.BURIAL, None, bur_date, bur_place, bur_source
            )
            bur_ref = EventRef()
            bur_ref.set_reference_handle(bur.get_handle())
            person.add_event_ref(bur_ref)

        if crem_date:
            crem = self.create_event(
                EventType.CREMATION, None, crem_date, bur_place, bur_source
            )
            crem_ref = EventRef()
            crem_ref.set_reference_handle(crem.get_handle())
            person.add_event_ref(crem_ref)

        self.db.commit_person(person, self.trans)

        return (idx, person)

    def parse_date(self, field):
        if field == "0":
            return None
        date = Date()
        matches = _text_parse.match(field)
        if matches:
            groups = matches.groups()
            date.set_as_text(groups[0])
            date.set_modifier(Date.MOD_TEXTONLY)
            return date

        matches = _date_parse.match(field)
        if matches:
            groups = matches.groups()
            mod = _mod_map.get(groups[0], Date.MOD_NONE)
            if groups[3] == "..":
                if groups[4] == "0":
                    mod = Date.MOD_FROM
                    cal1 = _cal_map.get(groups[2], Date.CAL_GREGORIAN)
                    sub1 = self.sub_date(groups[1])
                    sub2 = (0, 0, 0)
                elif groups[1] == "0":
                    mod = Date.MOD_TO
                    cal1 = _cal_map.get(groups[5], Date.CAL_GREGORIAN)
                    sub1 = self.sub_date(groups[4])
                    sub2 = (0, 0, 0)
                else:
                    mod = Date.MOD_SPAN
                    cal1 = _cal_map.get(groups[2], Date.CAL_GREGORIAN)
                    cal2 = _cal_map.get(groups[5], Date.CAL_GREGORIAN)
                    sub1 = self.sub_date(groups[1])
                    sub2 = self.sub_date(groups[4])
            else:
                cal1 = _cal_map.get(groups[2], Date.CAL_GREGORIAN)
                sub1 = self.sub_date(groups[1])
                sub2 = (0, 0, 0)
            try:
                date.set(
                    Date.QUAL_NONE,
                    mod,
                    cal1,
                    (sub1[0], sub1[1], sub1[2], 0, sub2[0], sub2[1], sub2[2], 0),
                )
            except DateError as e:
                # Translators: leave the {date} and {gw_snippet} untranslated
                # in the format string, but you may re-order them if needed.
                LOG.warning(
                    _(
                        "Invalid date {date} in {gw_snippet}, "
                        "preserving date as text."
                    ).format(date=e.date.__dict__, gw_snippet=field)
                )
                date.set(modifier=Date.MOD_TEXTONLY, text=field)
            return date
        else:
            return None

    def sub_date(self, data):
        vals = data.split("/")
        if len(vals) == 1:
            return (0, 0, int(vals[0]))
        elif len(vals) == 2:
            return (0, int(vals[0]), int(vals[1]))
        else:
            return (int(vals[0]), int(vals[1]), int(vals[2]))

    def create_event(self, type, desc=None, date=None, place=None, source=None):
        event = Event()
        if type:
            event.set_type(EventType(type))
        if desc:
            event.set_description(desc)
        if date:
            event.set_date_object(date)
        if place:
            event.set_place_handle(place.get_handle())
        if source:
            event.add_citation(source.get_handle())
        self.db.add_event(event, self.trans)
        self.db.commit_event(event, self.trans)
        return event

    def get_or_create_person(self, firstname, lastname):
        person = None
        mykey = firstname + lastname
        if mykey in self.ikeys and firstname != "?" and lastname != "?":
            person = self.db.get_person_from_handle(self.ikeys[mykey])
        else:
            person = Person()
            self.db.add_person(person, self.trans)
            self.db.commit_person(person, self.trans)
            self.ikeys[mykey] = person.get_handle()
        return person

    def get_or_create_place(self, place_name):
        place = None
        if place_name in self.pkeys:
            place = self.db.get_place_from_handle(self.pkeys[place_name])
        else:
            place = Place()
            place.name = PlaceName(value=place_name)
            place.set_title(place_name)
            self.db.add_place(place, self.trans)
            self.db.commit_place(place, self.trans)
            self.pkeys[place_name] = place.get_handle()
        return place

    def get_or_create_source(self, source_name):
        source = None
        if source_name in self.skeys:
            source = self.db.get_source_from_handle(self.skeys[source_name])
        else:
            source = Source()
            source.set_title(source_name)
            self.db.add_source(source, self.trans)
            self.db.commit_source(source, self.trans)
            self.skeys[source_name] = source.get_handle()
        citation = Citation()
        citation.set_reference_handle(source.get_handle())
        self.db.add_citation(citation, self.trans)
        self.db.commit_citation(citation, self.trans)
        return citation

    def read_fevent_line(self, event):
        if fevents_map.get(event[0:5]) == None:
            return  # need to fix custom event types not in the map

        fev = None
        # get events for the current family
        for evr in self.current_family.get_event_ref_list():
            ev = self.db.get_event_from_handle(evr.get_reference_handle())
            if ev.get_type() == fevents_map.get(event[0:5]):
                fev = ev  # found. Need to also check EventRef role
                return
            if not fev:  # No event found create a new one
                if evr.get_role() != EventRoleType(EventRoleType.FAMILY):
                    continue
                else:
                    LOG.info((ev.get_type(), self.current_family.handle))
                    self.new_gwplus_fevent(event)
        while True:
            line = self.get_next_line()
            if line and line[0:5] in fevents_map:
                self.new_gwplus_fevent(line)
            elif line and line[0:4] == "wit:":
                continue
            else:
                self.current_mode = None
                # self.db.commit_family(self.current_family,self.trans)
                break

    def read_pevent_line(self, event, fields):
        name = fields[2] + fields[1]

        try:
            self.person = self.ikeys[name]
        # check key on {ikey}
        except:
            self.person = "(TO_CHECK: %s)" % fields[1:]
            # GrampsImportError()

        lastname = fields[1]
        firstname = fields[2]
        self.current_person = self.get_or_create_person(firstname, lastname)

        # name = Name()
        # name.set_type(NameType(NameType.BIRTH))
        # name.set_first_name(firstname)
        # surname_obj = name.get_primary_surname()
        # surname_obj.set_surname(surname)
        # self.current_person.set_primary_name(name)

        if pevents_map.get(event[0:5]) == None:
            return  # need to fix custom event types not in the map

        self.current_event = None
        # get events for the current person
        for evr in self.current_person.get_event_ref_list():
            ev = self.db.get_event_from_handle(evr.get_reference_handle())
            if ev.get_type() == pevents_map.get(event[0:5]):
                self.current_event = ev  # found. Need to also check EventRef role
            if not self.current_event:  # No event found create a new one
                self.current_event = self.new_gwplus_pevent(event)
        while True:
            line = self.get_next_line()
            if line and line[0:5] in pevents_map:
                self.current_mode = "person_event"
                self.current_event = self.new_gwplus_pevent(line)
            elif line and line[0:4] == "note":
                n = Note()
                n.set(line[5:])
                self.db.add_note(n, self.trans)
                if self.current_event:
                    self.current_event.add_note(n.handle)
                    self.db.commit_event(self.current_event, self.trans)
                else:
                    print("note", n.handle)
            else:
                self.current_mode = None
                # self.db.commit_person(self.current_person,self.trans)
                break

    def new_gwplus_fevent(self, line):
        source = place = note = type = None
        date = self.parse_date(self.decode(line[6:]))

        idx = 0
        LOG.info((line, fevents_map.get(line[0:5])))
        type = fevents_map.get(line[0:5])
        data = line.split()
        date = self.parse_date(self.decode(line[6:]))
        for part in data:
            idx += 1
            if part == "#p":
                place = self.get_or_create_place(self.decode(data[idx]))
            if part == "#s":
                source = self.get_or_create_source(self.decode(data[idx]))
        self.current_event = self.create_event(type, None, None, None, None)
        print("new event", self.current_event.handle)
        if date:
            print(date)
            self.current_event.set_date_object(date)
        if place:
            print("place", place.handle)
            self.current_event.set_place_handle(place.get_handle())
        if source:
            print("source", source.handle)
            self.current_event.add_citation(source.get_handle())
        self.db.commit_event(self.current_event, self.trans)
        nev_ref = EventRef()
        nev_ref.set_reference_handle(self.current_event.get_handle())
        self.current_family.add_event_ref(nev_ref)
        self.db.commit_family(self.current_family, self.trans)
        return self.current_event

    def new_gwplus_pevent(self, line):
        source = place = note = type = None
        date = self.parse_date(self.decode(line[6:]))

        idx = 0
        LOG.info((self.person, line, pevents_map.get(line[0:5])))
        type = pevents_map.get(line[0:5])
        data = line.split()
        date = self.parse_date(self.decode(line[6:]))
        for part in data:
            idx += 1
            if part == "#p":
                place = self.get_or_create_place(self.decode(data[idx]))
            if part == "#s":
                source = self.get_or_create_source(self.decode(data[idx]))
        self.current_event = self.create_event(type, None, None, None, None)
        print("new event", self.current_event.handle)
        if date:
            print(date)
            self.current_event.set_date_object(date)
        if place:
            print("place", place.handle)
            self.current_event.set_place_handle(place.get_handle())
        if source:
            print("source", source.handle)
            self.current_event.add_citation(source.get_handle())
        self.db.commit_event(self.current_event, self.trans)
        nev_ref = EventRef()
        nev_ref.set_reference_handle(self.current_event.get_handle())
        self.current_person.add_event_ref(nev_ref)
        self.db.commit_person(self.current_person, self.trans)
        return self.current_event

    def decode(self, s):
        s = s.replace("_", " ")
        charref_re = re.compile("(&#)(x?)([0-9a-zA-Z]+)(;)")
        for match in charref_re.finditer(s):
            try:
                if match.group(2):  # HEX
                    nchar = chr(int(match.group(3), 16))
                else:  # Decimal
                    nchar = chr(int(match.group(3)))
                s = s.replace(match.group(0), nchar)
            except UnicodeDecodeError:
                pass

        # replace named entities
        entref_re = re.compile("(&)([a-zA-Z]+)(;)")
        for match in entref_re.finditer(s):
            try:
                if match.group(2) in name2codepoint:
                    nchar = chr(name2codepoint[match.group(2)])
                s = s.replace(match.group(0), nchar)
            except UnicodeDecodeError:
                pass

        return s

    def debug(self, txt):
        LOG.debug(txt)
