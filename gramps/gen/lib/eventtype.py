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

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .grampstype import GrampsType

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
    UNKNOWN        = -1
    CUSTOM         = 0
    MARRIAGE       = 1
    MARR_SETTL     = 2
    MARR_LIC       = 3
    MARR_CONTR     = 4
    MARR_BANNS     = 5
    ENGAGEMENT     = 6
    DIVORCE        = 7
    DIV_FILING     = 8
    ANNULMENT      = 9
    MARR_ALT       = 10
    ADOPT          = 11
    BIRTH          = 12
    DEATH          = 13
    ADULT_CHRISTEN = 14
    BAPTISM        = 15
    BAR_MITZVAH    = 16
    BAS_MITZVAH    = 17
    BLESS          = 18
    BURIAL         = 19
    CAUSE_DEATH    = 20
    CENSUS         = 21
    CHRISTEN       = 22
    CONFIRMATION   = 23
    CREMATION      = 24
    DEGREE         = 25
    EDUCATION      = 26
    ELECTED        = 27
    EMIGRATION     = 28
    FIRST_COMMUN   = 29
    IMMIGRATION    = 30
    GRADUATION     = 31
    MED_INFO       = 32
    MILITARY_SERV  = 33
    NATURALIZATION = 34
    NOB_TITLE      = 35
    NUM_MARRIAGES  = 36
    OCCUPATION     = 37
    ORDINATION     = 38
    PROBATE        = 39
    PROPERTY       = 40
    RELIGION       = 41
    RESIDENCE      = 42
    RETIREMENT     = 43
    WILL           = 44

    # _T_ is a gramps-defined keyword -- see po/update_po.py and po/genpot.sh
    def _T_(value): # enable deferred translations (see Python docs 22.1.3.4)
        return value

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
        (UNKNOWN         , _("Unknown"),              "Unknown"),
        (CUSTOM          , _("Custom"),               "Custom"),
        (ADOPT           , _("Adopted"),              "Adopted"),
        (BIRTH           , _("Birth"),                "Birth"),
        (DEATH           , _("Death"),                "Death"),
        (ADULT_CHRISTEN  , _("Adult Christening"),    "Adult Christening"),
        (BAPTISM         , _("Baptism"),              "Baptism"),
        (BAR_MITZVAH     , _("Bar Mitzvah"),          "Bar Mitzvah"),
        (BAS_MITZVAH     , _("Bat Mitzvah"),          "Bas Mitzvah"),
        (BLESS           , _("Blessing"),             "Blessing"),
        (BURIAL          , _("Burial"),               "Burial"),
        (CAUSE_DEATH     , _("Cause Of Death"),       "Cause Of Death"),
        (CENSUS          , _("Census"),               "Census"),
        (CHRISTEN        , _("Christening"),          "Christening"),
        (CONFIRMATION    , _("Confirmation"),         "Confirmation"),
        (CREMATION       , _("Cremation"),            "Cremation"),
        (DEGREE          , _("Degree"),               "Degree"),
        (EDUCATION       , _("Education"),            "Education"),
        (ELECTED         , _("Elected"),              "Elected"),
        (EMIGRATION      , _("Emigration"),           "Emigration"),
        (FIRST_COMMUN    , _("First Communion"),      "First Communion"),
        (IMMIGRATION     , _("Immigration"),          "Immigration"),
        (GRADUATION      , _("Graduation"),           "Graduation"),
        (MED_INFO        , _("Medical Information"),  "Medical Information"),
        (MILITARY_SERV   , _("Military Service"),     "Military Service"),
        (NATURALIZATION  , _("Naturalization"),       "Naturalization"),
        (NOB_TITLE       , _("Nobility Title"),       "Nobility Title"),
        (NUM_MARRIAGES   , _("Number of Marriages"),  "Number of Marriages"),
        (OCCUPATION      , _("Occupation"),           "Occupation"),
        (ORDINATION      , _("Ordination"),           "Ordination"),
        (PROBATE         , _("Probate"),              "Probate"),
        (PROPERTY        , _("Property"),             "Property"),
        (RELIGION        , _("Religion"),             "Religion"),
        (RESIDENCE       , _("Residence"),            "Residence"),
        (RETIREMENT      , _("Retirement"),           "Retirement"),
        (WILL            , _("Will"),                 "Will"),
        (MARRIAGE        , _("Marriage"),             "Marriage"),
        (MARR_SETTL      , _("Marriage Settlement"),  "Marriage Settlement"),
        (MARR_LIC        , _("Marriage License"),     "Marriage License"),
        (MARR_CONTR      , _("Marriage Contract"),    "Marriage Contract"),
        (MARR_BANNS      , _("Marriage Banns"),       "Marriage Banns"),
        (ENGAGEMENT      , _("Engagement"),           "Engagement"),
        (DIVORCE         , _("Divorce"),              "Divorce"),
        (DIV_FILING      , _("Divorce Filing"),       "Divorce Filing"),
        (ANNULMENT       , _("Annulment"),            "Annulment"),
        (MARR_ALT        , _("Alternate Marriage"),   "Alternate Marriage"),
        ]

    _ABBREVIATIONS = {
        BIRTH: _T_("birth abbreviation|b."),
        DEATH: _T_("death abbreviation|d."),
        MARRIAGE: _T_("marriage abbreviation|m."),
        UNKNOWN: _T_("Unknown abbreviation|unkn."),
        CUSTOM: _T_("Custom abbreviation|cust."),
        ADOPT: _T_("Adopted abbreviation|adop."),
        ADULT_CHRISTEN : _T_("Adult Christening abbreviation|a.chr."),
        BAPTISM: _T_("Baptism abbreviation|bap."),
        BAR_MITZVAH : _T_("Bar Mitzvah abbreviation|bar."),
        BAS_MITZVAH : _T_("Bat Mitzvah abbreviation|bat."),
        BLESS: _T_("Blessing abbreviation|bles."),
        BURIAL: _T_("Burial abbreviation|bur."),
        CAUSE_DEATH : _T_("Cause Of Death abbreviation|d.cau."),
        CENSUS: _T_("Census abbreviation|cens."),
        CHRISTEN: _T_("Christening abbreviation|chr."),
        CONFIRMATION: _T_("Confirmation abbreviation|conf."),
        CREMATION: _T_("Cremation abbreviation|crem."),
        DEGREE: _T_("Degree abbreviation|deg."),
        EDUCATION: _T_("Education abbreviation|edu."),
        ELECTED: _T_("Elected abbreviation|elec."),
        EMIGRATION: _T_("Emigration abbreviation|em."),
        FIRST_COMMUN: _T_("First Communion abbreviation|f.comm."),
        IMMIGRATION: _T_("Immigration abbreviation|im."),
        GRADUATION: _T_("Graduation abbreviation|grad."),
        MED_INFO: _T_("Medical Information abbreviation|medinf."),
        MILITARY_SERV: _T_("Military Service abbreviation|milser."),
        NATURALIZATION: _T_("Naturalization abbreviation|nat."),
        NOB_TITLE: _T_("Nobility Title abbreviation|nob."),
        NUM_MARRIAGES: _T_("Number of Marriages abbreviation|n.o.mar."),
        OCCUPATION: _T_("Occupation abbreviation|occ."),
        ORDINATION: _T_("Ordination abbreviation|ord."),
        PROBATE: _T_("Probate abbreviation|prob."),
        PROPERTY: _T_("Property abbreviation|prop."),
        RELIGION: _T_("Religion abbreviation|rel."),
        RESIDENCE: _T_("Residence abbreviation|res."),
        RETIREMENT: _T_("Retirement abbreviation|ret."),
        WILL: _T_("Will abbreviation|will."),
        MARR_SETTL: _T_("Marriage Settlement abbreviation|m.set."),
        MARR_LIC: _T_("Marriage License abbreviation|m.lic."),
        MARR_CONTR: _T_("Marriage Contract abbreviation|m.con."),
        MARR_BANNS: _T_("Marriage Banns abbreviation|m.ban."),
        MARR_ALT: _T_("Alternate Marriage abbreviation|alt.mar."),
        ENGAGEMENT: _T_("Engagement abbreviation|engd."),
        DIVORCE: _T_("Divorce abbreviation|div."),
        DIV_FILING: _T_("Divorce Filing abbreviation|div.f."),
        ANNULMENT: _T_("Annulment abbreviation|annul.")
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
                return ".".join([letter[0].lower() for letter in abbrev.split()]) + "."
            else:
                return abbrev[:3].lower() + "."
