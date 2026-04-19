# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024-2025  Gabriel Rios
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

from __future__ import annotations

from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import EventType
from gramps.gen.lib import PlaceType

_ = glocale.translation.gettext

MAX_PERSONS = 200

# https://www.familysearch.org/developers/docs/guides/facts
# https://github.com/FamilySearch/gedcomx/blob/master/specifications/fact-types-specification.md
GEDCOMX_TO_GRAMPS_FACTS = {
    # direct mappings to Gramps predefined event types
    "http://gedcomx.org/Adoption": EventType.ADOPT,
    "http://gedcomx.org/AdultChristening": EventType.ADULT_CHRISTEN,
    "http://gedcomx.org/Annulment": EventType.ANNULMENT,
    "http://gedcomx.org/Baptism": EventType.BAPTISM,
    "http://gedcomx.org/BarMitzvah": EventType.BAR_MITZVAH,
    "http://gedcomx.org/BatMitzvah": EventType.BAS_MITZVAH,
    "http://gedcomx.org/Birth": EventType.BIRTH,
    "http://gedcomx.org/Blessing": EventType.BLESS,
    "http://gedcomx.org/Burial": EventType.BURIAL,
    "http://gedcomx.org/Census": EventType.CENSUS,
    "data:,Census": EventType.CENSUS,
    "data:,http://gedcomx.org/Census": EventType.CENSUS,
    "http://gedcomx.org/Christening": EventType.CHRISTEN,
    "http://gedcomx.org/CommonLawMarriage": EventType.MARR_ALT,
    "http://gedcomx.org/Confirmation": EventType.CONFIRMATION,
    "http://gedcomx.org/Cremation": EventType.CREMATION,
    "http://gedcomx.org/Death": EventType.DEATH,
    "http://gedcomx.org/Divorce": EventType.DIVORCE,
    "http://gedcomx.org/DivorceFiling": EventType.DIV_FILING,
    "http://gedcomx.org/Education": EventType.EDUCATION,
    "http://gedcomx.org/Emigration": EventType.EMIGRATION,
    "http://gedcomx.org/Engagement": EventType.ENGAGEMENT,
    "http://gedcomx.org/FirstCommunion": EventType.FIRST_COMMUN,
    "http://gedcomx.org/Graduation": EventType.GRADUATION,
    "http://gedcomx.org/Immigration": EventType.IMMIGRATION,
    "http://gedcomx.org/MilitaryService": EventType.MILITARY_SERV,
    "http://gedcomx.org/Marriage": EventType.MARRIAGE,
    "data:,Marriage Banns": EventType.MARR_BANNS,
    "http://gedcomx.org/MarriageBanns": EventType.MARR_BANNS,
    "http://gedcomx.org/MarriageContract": EventType.MARR_CONTR,
    "http://gedcomx.org/MarriageLicense": EventType.MARR_LIC,
    "http://gedcomx.org/Medical": EventType.MED_INFO,
    "http://gedcomx.org/Naturalization": EventType.NATURALIZATION,
    "http://gedcomx.org/NumberOfMarriages": EventType.NUM_MARRIAGES,
    "http://gedcomx.org/Occupation": EventType.OCCUPATION,
    "http://gedcomx.org/Ordination": EventType.ORDINATION,
    "http://gedcomx.org/Probate": EventType.PROBATE,
    "data:,http://gedcomx.org/Property": EventType.PROPERTY,
    "http://gedcomx.org/Religion": EventType.RELIGION,
    "http://gedcomx.org/Residence": EventType.RESIDENCE,
    "http://gedcomx.org/Retirement": EventType.RETIREMENT,
    "http://gedcomx.org/Stillbirth": EventType.STILLBIRTH,
    "data:,http://gedcomx.org/Will": EventType.WILL,
    "http://familysearch.org/v1/TitleOfNobility": EventType.NOB_TITLE,
    # common pseudo/extra labels
    "http://familysearch.org/v1/LifeSketch": _("LifeSketch"),
    "data:,Birth Registration": _("Birth Registration"),
    "data:,Birth+Registration": _("Birth Registration"),
    "data:,Death Registration": _("Death Registration"),
    "data:,Death+Registration": _("Death Registration"),
    "data:,Obituary": _("Obituary"),
    "data:,Citizenship": _("Citizenship"),
}

EXTRA_FACTS = {
    "data:,Profession": EventType.OCCUPATION,
    "data:,Baptism": EventType.CHRISTEN,
    "data:,Will": EventType.WILL,
    "data:,Testament": EventType.WILL,
}


def _reversed_dict(d):
    return {val: key for key, val in d.items()}


GRAMPS_TO_GEDCOMX_FACTS = _reversed_dict(GEDCOMX_TO_GRAMPS_FACTS)

GEDCOMX_TO_GRAMPS_FACTS.update(EXTRA_FACTS)

GEDCOMX_TO_GRAMPS_PLACES = {
    "https://www.familysearch.org/platform/places/types/580": PlaceType.COUNTRY,
    "https://www.familysearch.org/platform/places/types/362": PlaceType.STATE,
    "https://www.familysearch.org/platform/places/types/209": PlaceType.COUNTY,
    "https://www.familysearch.org/platform/places/types/521": PlaceType.COUNTY,
    "https://www.familysearch.org/platform/places/types/186": PlaceType.CITY,
    "https://www.familysearch.org/platform/places/types/520": PlaceType.CITY,
    "https://www.familysearch.org/platform/places/types/312": PlaceType.PARISH,
    "https://www.familysearch.org/platform/places/types/323": PlaceType.LOCALITY,
    "https://www.familysearch.org/platform/places/types/337": PlaceType.REGION,
    "https://www.familysearch.org/platform/places/types/215": PlaceType.DEPARTMENT,
    "https://www.familysearch.org/platform/places/types/308": PlaceType.NEIGHBORHOOD,
    "https://www.familysearch.org/platform/places/types/221": PlaceType.DISTRICT,
    "https://www.familysearch.org/platform/places/types/171": PlaceType.BOROUGH,
    "https://www.familysearch.org/platform/places/types/201": PlaceType.MUNICIPALITY,
    "https://www.familysearch.org/platform/places/types/376": PlaceType.TOWN,
    "https://www.familysearch.org/platform/places/types/391": PlaceType.VILLAGE,
    "https://www.familysearch.org/platform/places/types/266": PlaceType.HAMLET,
    "https://www.familysearch.org/platform/places/types/38": PlaceType.FARM,
    "https://www.familysearch.org/platform/places/types/23": PlaceType.BUILDING,
    "https://www.familysearch.org/platform/places/types/61": PlaceType.BUILDING,
    "https://www.familysearch.org/platform/places/types/115": PlaceType.BUILDING,
    "https://www.familysearch.org/platform/places/types/142": PlaceType.BUILDING,
}

__all__ = [
    "MAX_PERSONS",
    "GEDCOMX_TO_GRAMPS_FACTS",
    "GRAMPS_TO_GEDCOMX_FACTS",
    "GEDCOMX_TO_GRAMPS_PLACES",
]
