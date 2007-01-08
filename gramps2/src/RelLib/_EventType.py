#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

"""
Provides the different event types
"""

__revision__ = "$Revision$"

from _GrampsType import GrampsType, init_map
from gettext import gettext as _

class EventType(GrampsType):

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

    _CUSTOM = CUSTOM
    _DEFAULT = BIRTH

    _DATAMAP = [
        (UNKNOWN         , _("Unknown"), "Unknown"),
        (CUSTOM          , _("Custom"), "Custom"),
        (ADOPT           , _("Adopted"), "Adopted"),
        (BIRTH           , _("Birth"), "Birth"),
        (DEATH           , _("Death"), "Death"),
        (ADULT_CHRISTEN  , _("Adult Christening"), "Adult Christening"),
        (BAPTISM         , _("Baptism"), "Baptism"),
        (BAR_MITZVAH     , _("Bar Mitzvah"), "Bar Mitzvah"),
        (BAS_MITZVAH     , _("Bas Mitzvah"), "Bas Mitzvah"),
        (BLESS           , _("Blessing"), "Blessing"),
        (BURIAL          , _("Burial"), "Burial"),
        (CAUSE_DEATH     , _("Cause Of Death"), "Cause Of Death"),
        (CENSUS          , _("Census"), "Census"),
        (CHRISTEN        , _("Christening"), "Christening"),
        (CONFIRMATION    , _("Confirmation"), "Confirmation"),
        (CREMATION       , _("Cremation"), "Cremation"),
        (DEGREE          , _("Degree"), "Degree"),
        (EDUCATION       , _("Education"), "Education"),
        (ELECTED         , _("Elected"), "Elected"),
        (EMIGRATION      , _("Emigration"), "Emigration"),
        (FIRST_COMMUN    , _("First Communion"), "First Communion"),
        (IMMIGRATION     , _("Immigration"), "Immigration"),
        (GRADUATION      , _("Graduation"), "Graduation"),
        (MED_INFO        , _("Medical Information"), "Medical Information"),
        (MILITARY_SERV   , _("Military Service"),  "Military Service"),
        (NATURALIZATION  , _("Naturalization"), "Naturalization"),
        (NOB_TITLE       , _("Nobility Title"), "Nobility Title"),
        (NUM_MARRIAGES   , _("Number of Marriages"), "Number of Marriages"),
        (OCCUPATION      , _("Occupation"), "Occupation"),
        (ORDINATION      , _("Ordination"), "Ordination"),
        (PROBATE         , _("Probate"), "Probate"),
        (PROPERTY        , _("Property"), "Property"),
        (RELIGION        , _("Religion"), "Religion"),
        (RESIDENCE       , _("Residence"), "Residence"),
        (RETIREMENT      , _("Retirement"), "Retirement"),
        (WILL            , _("Will"), "Will"),
        (MARRIAGE        , _("Marriage"), "Marriage"),
        (MARR_SETTL      , _("Marriage Settlement"), "Marriage Settlement"),
        (MARR_LIC        , _("Marriage License"), "Marriage License"),
        (MARR_CONTR      , _("Marriage Contract"), "Marriage Contract"),
        (MARR_BANNS      , _("Marriage Banns"), "Marriage Banns"),
        (ENGAGEMENT      , _("Engagement"), "Engagement"),
        (DIVORCE         , _("Divorce"), "Divorce"),
        (DIV_FILING      , _("Divorce Filing"), "Divorce Filing"),
        (ANNULMENT       , _("Annulment"), "Annulment"),
        (MARR_ALT        , _("Alternate Marriage"), "Alternate Marriage"),
        ]

    _I2SMAP = init_map(_DATAMAP, 0, 1)
    _S2IMAP = init_map(_DATAMAP, 1, 0)
    _I2EMAP = init_map(_DATAMAP, 0, 2)
    _E2IMAP = init_map(_DATAMAP, 2, 0)

    def __init__(self, value=None):
        GrampsType.__init__(self, value)
        

