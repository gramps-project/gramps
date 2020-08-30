#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2013       Paul Franklin
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
Provide the different event types
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .grampstype import GrampsType
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

class EventType(GrampsType):
    """
    Event types.

    .. attribute UNKNOWN:    Unknown
    .. attribute CUSTOM:    Custom
    .. attribute ADOPT:     Adopted
    .. attribute BIRTH:     Birth
    .. attribute DEATH:     Death
    .. attribute ADULT_CHRISTEN: Adult Christening
    .. attribute BAPTISM:      Baptism
    .. attribute BAR_MITZVAH:  Bar Mitzvah
    .. attribute BAS_MITZVAH:  Bas Mitzvah
    .. attribute BLESS:        Blessing
    .. attribute BURIAL:       Burial
    .. attribute CAUSE_DEATH:   Cause Of Death
    .. attribute CENSUS:        Census
    .. attribute CHRISTEN:      Christening
    .. attribute CONFIRMATION:   Confirmation
    .. attribute CREMATION:      Cremation
    .. attribute DEGREE:         Degree
    .. attribute EDUCATION:     Education
    .. attribute ELECTED:       Elected
    .. attribute EMIGRATION:    Emigration
    .. attribute FIRST_COMMUN:  First Communion
    .. attribute IMMIGRATION:   Immigration
    .. attribute GRADUATION:   Graduation
    .. attribute MED_INFO:     Medical Information
    .. attribute MILITARY_SERV:   Military Service
    .. attribute NATURALIZATION: Naturalization
    .. attribute NOB_TITLE:     Nobility Title
    .. attribute NUM_MARRIAGES:   Number of Marriages
    .. attribute OCCUPATION:      Occupation
    .. attribute ORDINATION:     Ordination
    .. attribute PROBATE:        Probate
    .. attribute PROPERTY:      Property
    .. attribute RELIGION:      Religion
    .. attribute RESIDENCE:    Residence
    .. attribute RETIREMENT:    Retirement
    .. attribute WILL:           Will
    .. attribute MARRIAGE:     Marriage
    .. attribute MARR_SETTL:     Marriage Settlement
    .. attribute MARR_LIC:       Marriage License
    .. attribute MARR_CONTR:     Marriage Contract
    .. attribute MARR_BANNS:     Marriage Banns
    .. attribute ENGAGEMENT:     Engagement
    .. attribute DIVORCE:        Divorce
    .. attribute DIV_FILING:     Divorce Filing
    .. attribute ANNULMENT:      Annulment
    .. attribute MARR_ALT:        Alternate Marriage
    """
    UNKNOWN = -1
    CUSTOM = 0
    MARRIAGE = 1
    MARR_SETTL = 2
    MARR_LIC = 3
    MARR_CONTR = 4
    MARR_BANNS = 5
    ENGAGEMENT = 6
    DIVORCE = 7
    DIV_FILING = 8
    ANNULMENT = 9
    MARR_ALT = 10
    ADOPT = 11
    BIRTH = 12
    DEATH = 13
    ADULT_CHRISTEN = 14
    BAPTISM = 15
    BAR_MITZVAH = 16
    BAS_MITZVAH = 17
    BLESS = 18
    BURIAL = 19
    CAUSE_DEATH = 20
    CENSUS = 21
    CHRISTEN = 22
    CONFIRMATION = 23
    CREMATION = 24
    DEGREE = 25
    EDUCATION = 26
    ELECTED = 27
    EMIGRATION = 28
    FIRST_COMMUN = 29
    IMMIGRATION = 30
    GRADUATION = 31
    MED_INFO = 32
    MILITARY_SERV = 33
    NATURALIZATION = 34
    NOB_TITLE = 35
    NUM_MARRIAGES = 36
    OCCUPATION = 37
    ORDINATION = 38
    PROBATE = 39
    PROPERTY = 40
    RELIGION = 41
    RESIDENCE = 42
    RETIREMENT = 43
    WILL = 44

    # _T_ is a gramps-defined keyword -- see po/update_po.py and po/genpot.sh
    def _T_(value, context=''): # enable deferred translations
        return "%s\x04%s" % (context, value) if context else value

    _MENU = [[_T_('Life Events'),
              [BIRTH, BAPTISM, DEATH, BURIAL, CREMATION, ADOPT]],
             [_T_('Family'),
              [ENGAGEMENT, MARRIAGE, DIVORCE, ANNULMENT, MARR_SETTL, MARR_LIC,
               MARR_CONTR, MARR_BANNS, DIV_FILING, MARR_ALT]],
             [_T_('Religious'),
              [CHRISTEN, ADULT_CHRISTEN, CONFIRMATION, FIRST_COMMUN, BLESS,
               BAR_MITZVAH, BAS_MITZVAH, RELIGION]],
             [_T_('Vocational'),
              [OCCUPATION, RETIREMENT, ELECTED, MILITARY_SERV, ORDINATION]],
             [_T_('Academic'),
              [EDUCATION, DEGREE, GRADUATION]],
             [_T_('Travel'),
              [EMIGRATION, IMMIGRATION, NATURALIZATION]],
             [_T_('Legal'),
              [PROBATE, WILL]],
             [_T_('Residence'),
              [RESIDENCE, CENSUS, PROPERTY]],
             [_T_('Other'),
              [CAUSE_DEATH, MED_INFO, NOB_TITLE, NUM_MARRIAGES]]]

    _CUSTOM = CUSTOM
    _DEFAULT = BIRTH

    _DATAMAP = [
        (UNKNOWN, _("Unknown"), "Unknown"),
        (CUSTOM, _("Custom"), "Custom"),
        (ADOPT, _("Adopted"), "Adopted"),
        (BIRTH, _("Birth"), "Birth"),
        (DEATH, _("Death"), "Death"),
        (ADULT_CHRISTEN, _("Adult Christening"), "Adult Christening"),
        (BAPTISM, _("Baptism"), "Baptism"),
        (BAR_MITZVAH, _("Bar Mitzvah"), "Bar Mitzvah"),
        (BAS_MITZVAH, _("Bat Mitzvah"), "Bas Mitzvah"),
        (BLESS, _("Blessing"), "Blessing"),
        (BURIAL, _("Burial"), "Burial"),
        (CAUSE_DEATH, _("Cause Of Death"), "Cause Of Death"),
        (CENSUS, _("Census"), "Census"),
        (CHRISTEN, _("Christening"), "Christening"),
        (CONFIRMATION, _("Confirmation"), "Confirmation"),
        (CREMATION, _("Cremation"), "Cremation"),
        (DEGREE, _("Degree"), "Degree"),
        (EDUCATION, _("Education"), "Education"),
        (ELECTED, _("Elected"), "Elected"),
        (EMIGRATION, _("Emigration"), "Emigration"),
        (FIRST_COMMUN, _("First Communion"), "First Communion"),
        (IMMIGRATION, _("Immigration"), "Immigration"),
        (GRADUATION, _("Graduation"), "Graduation"),
        (MED_INFO, _("Medical Information"), "Medical Information"),
        (MILITARY_SERV, _("Military Service"), "Military Service"),
        (NATURALIZATION, _("Naturalization"), "Naturalization"),
        (NOB_TITLE, _("Nobility Title"), "Nobility Title"),
        (NUM_MARRIAGES, _("Number of Marriages"), "Number of Marriages"),
        (OCCUPATION, _("Occupation"), "Occupation"),
        (ORDINATION, _("Ordination"), "Ordination"),
        (PROBATE, _("Probate"), "Probate"),
        (PROPERTY, _("Property"), "Property"),
        (RELIGION, _("Religion"), "Religion"),
        (RESIDENCE, _("Residence"), "Residence"),
        (RETIREMENT, _("Retirement"), "Retirement"),
        (WILL, _("Will"), "Will"),
        (MARRIAGE, _("Marriage"), "Marriage"),
        (MARR_SETTL, _("Marriage Settlement"), "Marriage Settlement"),
        (MARR_LIC, _("Marriage License"), "Marriage License"),
        (MARR_CONTR, _("Marriage Contract"), "Marriage Contract"),
        (MARR_BANNS, _("Marriage Banns"), "Marriage Banns"),
        (ENGAGEMENT, _("Engagement"), "Engagement"),
        (DIVORCE, _("Divorce"), "Divorce"),
        (DIV_FILING, _("Divorce Filing"), "Divorce Filing"),
        (ANNULMENT, _("Annulment"), "Annulment"),
        (MARR_ALT, _("Alternate Marriage"), "Alternate Marriage"),
        ]

    _ABBREVIATIONS = {
        BIRTH: _T_("b.", "birth abbreviation"),
        DEATH: _T_("d.", "death abbreviation"),
        MARRIAGE: _T_("m.", "marriage abbreviation"),
        UNKNOWN: _T_("unkn.", "Unknown abbreviation"),
        CUSTOM: _T_("cust.", "Custom abbreviation"),
        ADOPT: _T_("adop.", "Adopted abbreviation"),
        ADULT_CHRISTEN : _T_("a.chr.", "Adult Christening abbreviation"),
        BAPTISM: _T_("bap.", "Baptism abbreviation"),
        BAR_MITZVAH : _T_("bar.", "Bar Mitzvah abbreviation"),
        BAS_MITZVAH : _T_("bat.", "Bat Mitzvah abbreviation"),
        BLESS: _T_("bles.", "Blessing abbreviation"),
        BURIAL: _T_("bur.", "Burial abbreviation"),
        CAUSE_DEATH : _T_("d.cau.", "Cause Of Death abbreviation"),
        CENSUS: _T_("cens.", "Census abbreviation"),
        CHRISTEN: _T_("chr.", "Christening abbreviation"),
        CONFIRMATION: _T_("conf.", "Confirmation abbreviation"),
        CREMATION: _T_("crem.", "Cremation abbreviation"),
        DEGREE: _T_("deg.", "Degree abbreviation"),
        EDUCATION: _T_("edu.", "Education abbreviation"),
        ELECTED: _T_("elec.", "Elected abbreviation"),
        EMIGRATION: _T_("em.", "Emigration abbreviation"),
        FIRST_COMMUN: _T_("f.comm.", "First Communion abbreviation"),
        IMMIGRATION: _T_("im.", "Immigration abbreviation"),
        GRADUATION: _T_("grad.", "Graduation abbreviation"),
        MED_INFO: _T_("medinf.", "Medical Information abbreviation"),
        MILITARY_SERV: _T_("milser.", "Military Service abbreviation"),
        NATURALIZATION: _T_("nat.", "Naturalization abbreviation"),
        NOB_TITLE: _T_("nob.", "Nobility Title abbreviation"),
        NUM_MARRIAGES: _T_("n.o.mar.", "Number of Marriages abbreviation"),
        OCCUPATION: _T_("occ.", "Occupation abbreviation"),
        ORDINATION: _T_("ord.", "Ordination abbreviation"),
        PROBATE: _T_("prob.", "Probate abbreviation"),
        PROPERTY: _T_("prop.", "Property abbreviation"),
        RELIGION: _T_("rel.", "Religion abbreviation"),
        RESIDENCE: _T_("res.", "Residence abbreviation"),
        RETIREMENT: _T_("ret.", "Retirement abbreviation"),
        WILL: _T_("will.", "Will abbreviation"),
        MARR_SETTL: _T_("m.set.", "Marriage Settlement abbreviation"),
        MARR_LIC: _T_("m.lic.", "Marriage License abbreviation"),
        MARR_CONTR: _T_("m.con.", "Marriage Contract abbreviation"),
        MARR_BANNS: _T_("m.ban.", "Marriage Banns abbreviation"),
        MARR_ALT: _T_("alt.mar.", "Alternate Marriage abbreviation"),
        ENGAGEMENT: _T_("engd.", "Engagement abbreviation"),
        DIVORCE: _T_("div.", "Divorce abbreviation"),
        DIV_FILING: _T_("div.f.", "Divorce Filing abbreviation"),
        ANNULMENT: _T_("annul.", "Annulment abbreviation")
        }

    def __init__(self, value=None):
        GrampsType.__init__(self, value)

    def is_birth(self):
        """
        Returns True if EventType is BIRTH, False
        otherwise.
        """
        return self.value == self.BIRTH

    def is_baptism(self):
        """
        Returns True if EventType is BAPTISM, False
        otherwise.
        """
        return self.value == self.BAPTISM

    def is_death(self):
        """
        Returns True if EventType is DEATH, False
        otherwise.
        """
        return self.value == self.DEATH

    def is_burial(self):
        """
        Returns True if EventType is BURIAL, False
        otherwise.
        """
        return self.value == self.BURIAL

    def is_birth_fallback(self):
        """
        Returns True if EventType is a birth fallback, False
        otherwise.
        """
        return self.value in [self.CHRISTEN,
                              self.BAPTISM]

    def is_death_fallback(self):
        """
        Returns True if EventType is a death fallback, False
        otherwise.
        """
        return self.value in [self.BURIAL,
                              self.CREMATION,
                              self.CAUSE_DEATH]
    def is_marriage(self):
        """
        Returns True if EventType is MARRIAGE, False otherwise.
        """
        return self.value == self.MARRIAGE

    def is_marriage_fallback(self):
        """
        Returns True if EventType is a marriage fallback, False
        otherwise.
        """
        return self.value in [self.ENGAGEMENT,
                              self.MARR_ALT]

    def is_divorce(self):
        """
        Returns True if EventType is DIVORCE, False otherwise.
        """
        return self.value == self.DIVORCE

    def is_divorce_fallback(self):
        """
        Returns True if EventType is a divorce fallback, False
        otherwise.
        """
        return self.value in [self.ANNULMENT,
                              self.DIV_FILING]

    def is_relationship_event(self):
        """
        Returns True is EventType is a relationship type event.
        """
        return self.value in [self.DIVORCE, self.MARRIAGE, self.ANNULMENT]

    def is_type(self, event_name):
        """
        Returns True if EventType has name EVENT_NAME, False otherwise.
        """
        event_type = [tup for tup in self._DATAMAP if tup[2] == event_name]
        if len(event_type) > 0:
            return self.value == event_type[0][0] # first one, the code
        return False

    def get_abbreviation(self, trans_text=glocale.translation.sgettext):
        """
        Returns the abbreviation for this event. Uses the explicitly
        given abbreviations, or first letter of each word, or the first
        three letters. Appends a period after the abbreviation,
        but not if string is in _ABBREVIATIONS.

        If trans_text is passed in (a GrampsLocale sgettext instance)
        then the translated abbreviation will be returned instead.
        """
        if self.value in self._ABBREVIATIONS:
            return trans_text(self._ABBREVIATIONS[self.value])
        else:
            abbrev = str(self)
            if " " in abbrev:
                return ".".join([letter[0].lower()
                                 for letter in abbrev.split()]) + "."
            else:
                return abbrev[:3].lower() + "."
