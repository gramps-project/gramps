#                                                     -*- python -*-
# -*- coding: utf-8 -*-
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

# $Id: const.py.in 6156 2006-03-16 20:25:15Z rshura $

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from TransUtils import sgettext as _

#-------------------------------------------------------------------------
#
# 
#
#-------------------------------------------------------------------------

#
#Updated LDS Temple Codes from:
#http://www.geocities.com/rgpassey/temple/abclist.htm
#Confirmed against Temple Codes list recieved from Raliegh Temple
#Last update: 1/12/02
#

lds_temple_codes = {
    "Aba, Nigeria"               : "ABA",   #1 Added
    "Accra, Ghana"               : "ACCRA", #2 Added
    "Adelaide, Australia"        : "ADELA", #3 Added
    "Albuquerque, New Mexico"    : "ALBUQ", #4 Added
    "Anchorage, Alaska"          : "ANCHO", #6 Added
    "Apia, Samoa"                : "APIA",  #7
    "Asuncion, Paraguay"         : "ASUNC", #8 Added
    "Atlanta, Georgia"           : "ATLAN", #9
    "Baton Rouge, Louisiana"     : "BROUG", #10 Added
    "Bern, Switzerland"          : "SWISS", #11
    "Billings, Montana"          : "BILLI", #12 Added
    "Birmingham, Alabama"        : "BIRMI", #13 Added
    "Bismarck, North Dakota"     : "BISMA", #14 Added
    "Bogota, Columbia"           : "BOGOT", #15
    "Boise, Idaho"               : "BOISE", #16
    "Boston, Massachusetts"      : "BOSTO", #17 Added
    "Bountiful, Utah"            : "BOUNT", #18
    "Brisban, Australia"         : "BRISB", #19 Added
    "Buenos Aires, Argentina"    : "BAIRE", #20
    "Campinas, Brazil"           : "CAMPI", #21 Added
    "Caracas, Venezuela"         : "CARAC", #22 Added
    "Cardston, Alberta"          : "ALBER", #23
    "Chicago, Illinois"          : "CHICA", #24
    "Ciudad Juarez, Chihuahua"   : "CIUJU", #25 Added
    "Cochabamba, Boliva"         : "COCHA", #26
    "Colonia Juarez, Chihuahua"  : "COLJU", #27 Added
    "Columbia, South Carolina"   : "COLSC", #28 Added
    "Columbia River, Washington" : "CRIVE", #121 Added
    "Columbus, Ohio"             : "COLUM", #29 Added
    "Copenhagen, Denmark"        : "COPEN", #30 Added
    "Curitiba, Brazil"           : "CURIT",
    "Manhattan, New York"        : "MANHA",
    "Panama City, Panama"        : "PCITY",
    "Dallas, Texas"              : "DALLA", #31
    "Denver, Colorado"           : "DENVE", #32
    "Detroit, Michigan"          : "DETRO", #33 Added
    "Edmonton, Alberta"          : "EDMON", #34 Added
    "Frankfurt, Germany"         : "FRANK", #35
    "Fresno, California"         : "FRESN", #36 Added
    "Freiberg, Germany"          : "FREIB", #37
    "Fukuoka, Japan"             : "FUKUO", #38 Added
    "Guadalajara, Jalisco"       : "GUADA", #39 Added
    "Guatamala City, Guatamala"  : "GUATE", #40
    "Guayaquil, Ecuador"         : "GUAYA", #41
    "Halifax, Noca Scotia"       : "HALIF", #42 Added
    "Hamilton, New Zealand"      : "NZEAL", #43
    "Harrison, New York"         : "NYORK", #44 Added
    "Hartford, Connecticut"      : "HARTF", #Can not find in list used. ?
    "Helsinki, Finland"          : "HELSI", #45 Added
    "Hermosillo, Sonora"         : "HERMO", #46 Added
    "Hong Kong, China"           : "HKONG", #47
    "Houston, Texas"             : "HOUST", #48 Added
    "Idaho Falls, Idaho"         : "IFALL", #49
    "Johannesburg, South Africa" : "JOHAN", #50
    "Jordan River, Utah"         : "JRIVE", #111
    "Kialua Kona, Hawaii"        : "KONA",  #51 Added
    "Kiev, Ukraine"              : "KIEV",  #52 Added
    "Laie, Hawaii"               : "HAWAI", #54
    "Las Vegas, Nevada"          : "LVEGA", #55
    "Lima, Peru"                 : "LIMA" , #56
    "Logan, Utah"                : "LOGAN", #57
    "London, England"            : "LONDO", #58
    "Los Angeles, California"    : "LANGE", #59
    "Louisville, Kentucky"       : "LOUIS", #60 Added
    "Lubbock, Texas"             : "LUBBO", #61 Added
    "Madrid, Spain"              : "MADRI", #62
    "Manila, Philippines"        : "MANIL", #63
    "Manti, Utah"                : "MANTI", #64
    "Medford, Oregon"            : "MEDFO", #65 Added
    "Melbourne, Australia"       : "MELBO", #66 Added
    "Melphis, Tennessee"         : "MEMPH", #67 Added
    "Merida, Yucatan"            : "MERID", #68 Added
    "Mesa, Arizona"              : "ARIZO", #69
    "Mexico City, Mexico"        : "MEXIC", #70
    "Monterrey, Nuevo Leon"      : "MONTE", #71 Added
    "Montevideo, Uruguay"        : "MNTVD", #72
    "Monticello, Utah"           : "MONTI", #73 Added
    "Montreal, Quebec"           : "MONTR", #74 Added
    "Mt. Timpanogos, Utah"       : "MTIMP", #5
    "Nashville, Tennessee"       : "NASHV", #75
    "Nauvoo, Illinois"           : "NAUVO", #76
    "Nauvoo, Illinois (New)"     : "NAUV2", #Rebuilt Added
    "Newport Beach, California"  : "NBEAC", #77 Added
    "Nuku'alofa, Tonga"          : "NUKUA", #78
    "Oakland, California"        : "OAKLA", #79
    "Oaxaca, Oaxaca"             : "OAKAC", #80 Added
    "Ogden, Utah"                : "OGDEN", #81
    "Oklahoma City, Oklahoma"    : "OKLAH", #82 Added
    "Orlando, Florida"           : "ORLAN", #84
    "Palmayra, New York"         : "PALMY", #85 Added
    "Papeete, Tahiti"            : "PAPEE", #86
    "Perth, Australia"           : "PERTH", #87 Added
    "Portland, Oregon"           : "PORTL", #88
    "Porto Alegre, Brazil"       : "PALEG", #89 Added
    "Preston, England"           : "PREST", #90
    "Provo, Utah"                : "PROVO", #91
    "Raleigh, North Carolina"    : "RALEI", #92 Added
    "Recife, Brazil"             : "RECIF", #93
    "Redlands, California"       : "REDLA", #94 Added
    "Regina, Saskatchewan"       : "REGIN", #95 Added
    "Reno, Nevada"               : "RENO",  #96 Added
    "Sacramento, California"     : "SACRA", #97 Added
    "St. George, Utah"           : "SGEOR", #98
    "St. Louis, Missouri"        : "SLOUI", #99
    "St. Paul, Minnesota"        : "SPMIN", #100 Added
    "Salt Lake City, Utah"       : "SLAKE", #101
    "San Diego, California"      : "SDIEG", #102
    "San Antonio, Texas"         : "ANTON", #103 Added
    "San Jose, Costa Rica"       : "SJOSE", #104 Added
    "Santiago, Chile"            : "SANTI", #105
    "Santo Domingo, Dominican Republic" : "SDOMI", #106
    "Sao Paulo, Brazil"          : "SPAUL", #107
    "Seattle, Washington"        : "SEATT", #108
    "Seoul, South Korea"         : "SEOUL", #109
    "Snowflake, Arizona"         : "SNOWF", #110 Added
    "Spokane, Washington"        : "SPOKA", #112
    "Stockholm, Sweden"          : "STOCK", #113
    "Suva, Fiji"                 : "SUVA",  #114 Added
    "Sydney, Australia"          : "SYDNE", #115
    "Taipei, Taiwan"             : "TAIPE", #116
    "Tampico, Tamaulipas"        : "TAMPI", #117 Added
    "The Hague, Netherlands"     : "HAGUE", #118 Added
    "Tokyo, Japan"               : "TOKYO", #119
    "Toronto, Ontario"           : "TORNO", #120
    "Tuxtla Gutierrez, Chiapas"  : "TGUTI", #122 Added
    "Vera Cruz, Vera Cruz"       : "VERAC", #123 Added
    "Vernal, Utah"               : "VERNA", #124
    "Villahermosa, Tabasco"      : "VILLA", #125 Added
    "Washington, D.C."           : "WASHI", #126
    "Winter Quarters, Nebraska"  : "WINTE", #83 Added
#Other Places
    "Endowment House"            : "EHOUS", #Not a temple per se
    "President's Office"         : "POFFI", #Not a temple per se


}

lds_temple_to_abrev = {}
for (name,abbr) in lds_temple_codes.iteritems():
    lds_temple_to_abrev[abbr] = name

status = {
    "BIC"         : 1,    "CANCELED"    : 1,    "CHILD"       : 1,
    "CLEARED"     : 2,    "COMPLETED"   : 3,    "DNS"         : 4,
    "INFANT"      : 4,    "PRE-1970"    : 5,    "QUALIFIED"   : 6,
    "DNS/CAN"     : 7,    "STILLBORN"   : 7,    "SUBMITTED"   : 8,
    "UNCLEARED"   : 9,
    }

csealing = [
    _("<No Status>"),  _("BIC"),       _("Cleared"),    _("Completed"),
    _("DNS"),          _("Pre-1970"),  _("Qualified"),  _("Stillborn"),
    _("Submitted"),    _("Uncleared"),
    ]

ssealing = [
    _("<No Status>"),  _("Canceled"),  _("Cleared"),    _("Completed"),
    _("DNS"),          _("Pre-1970"),  _("Qualified"),  _("DNS/CAN"),
    _("Submitted"),    _("Uncleared"),
    ]
    
