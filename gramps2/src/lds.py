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

# $Id$

#-------------------------------------------------------------------------
#
# Standard python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#Updated LDS Temple Codes from:
#http://www.geocities.com/rgpassey/temple/abclist.htm
#Confirmed against Temple Codes list recieved from Raliegh Temple
#Last update: 1/12/02
#-------------------------------------------------------------------------
temples = (
    # Temple Name                 , Code   , [Old Codes...]
    ("Aba, Nigeria"               , "ABA",   ),
    ("Accra, Ghana"               , "ACCRA", ),
    ("Adelaide, Australia"        , "ADELA", ),
    ("Albuquerque, New Mexico"    , "ALBUQ", ),
    ("Anchorage, Alaska"          , "ANCHO", ),
    ("Apia, Samoa"                , "APIA",  "AP"),
    ("Asuncion, Paraguay"         , "ASUNC", ),
    ("Atlanta, Georgia"           , "ATLAN", "AT"),
    ("Baton Rouge, Louisiana"     , "BROUG", ),
    ("Bern, Switzerland"          , "SWISS", "SW"),
    ("Billings, Montana"          , "BILLI", ),
    ("Birmingham, Alabama"        , "BIRMI", ),
    ("Bismarck, North Dakota"     , "BISMA", ),
    ("Bogota, Columbia"           , "BOGOT", "BG"),
    ("Boise, Idaho"               , "BOISE", "BO"),
    ("Boston, Massachusetts"      , "BOSTO", ),
    ("Bountiful, Utah"            , "BOUNT", ),
    ("Brisban, Australia"         , "BRISB", ),
    ("Buenos Aires, Argentina"    , "BAIRE", "BA"),
    ("Campinas, Brazil"           , "CAMPI", ),
    ("Caracas, Venezuela"         , "CARAC", ),
    ("Cardston, Alberta"          , "ALBER", "AL", "ALBR"),
    ("Chicago, Illinois"          , "CHICA", "CH"),
    ("Ciudad Juarez, Chihuahua"   , "CIUJU", ),
    ("Cochabamba, Boliva"         , "COCHA", ),
    ("Colonia Juarez, Chihuahua"  , "COLJU", ),
    ("Columbia, South Carolina"   , "COLSC", ),
    ("Columbia River, Washington" , "CRIVE", ),
    ("Columbus, Ohio"             , "COLUM", ),
    ("Copenhagen, Denmark"        , "COPEN", ),
    ("Curitiba, Brazil"           , "CURIT", ),
    ("Manhattan, New York"        , "MANHA", ),
    ("Panama City, Panama"        , "PCITY", ),
    ("Dallas, Texas"              , "DALLA", "DA"),
    ("Denver, Colorado"           , "DENVE", "DV"),
    ("Detroit, Michigan"          , "DETRO", ),
    ("Edmonton, Alberta"          , "EDMON", ),
    ("Frankfurt, Germany"         , "FRANK", "FR"),
    ("Fresno, California"         , "FRESN", ),
    ("Freiberg, Germany"          , "FREIB", "FD"),
    ("Fukuoka, Japan"             , "FUKUO", ),
    ("Guadalajara, Jalisco"       , "GUADA", ),
    ("Guatamala City, Guatamala"  , "GUATE", "GA"),
    ("Guayaquil, Ecuador"         , "GUAYA", "GY"),
    ("Halifax, Noca Scotia"       , "HALIF", ),
    ("Hamilton, New Zealand"      , "NZEAL", "NZ"),
    ("Harrison, New York"         , "NYORK", ),
    ("Hartford, Connecticut"      , "HARTF", ),
    ("Helsinki, Finland"          , "HELSI", ),
    ("Hermosillo, Sonora"         , "HERMO", ),
    ("Hong Kong, China"           , "HKONG", ),
    ("Houston, Texas"             , "HOUST", ),
    ("Idaho Falls, Idaho"         , "IFALL", ),
    ("Johannesburg, South Africa" , "JOHAN", "JO"),
    ("Jordan River, Utah"         , "JRIVE", "JR"),
    ("Kialua Kona, Hawaii"        , "KONA",  ),
    ("Kiev, Ukraine"              , "KIEV",  ),
    ("Laie, Hawaii"               , "HAWAI", "HA"),
    ("Las Vegas, Nevada"          , "LVEGA", "LV"),
    ("Lima, Peru"                 , "LIMA" , "LI"),
    ("Logan, Utah"                , "LOGAN", "LG"),
    ("London, England"            , "LONDO", "LD"),
    ("Los Angeles, California"    , "LANGE", "LA"),
    ("Louisville, Kentucky"       , "LOUIS", ),
    ("Lubbock, Texas"             , "LUBBO", ),
    ("Madrid, Spain"              , "MADRI", ),
    ("Manila, Philippines"        , "MANIL", "MA"),
    ("Manti, Utah"                , "MANTI", "MT"),
    ("Medford, Oregon"            , "MEDFO", ),
    ("Melbourne, Australia"       , "MELBO", ),
    ("Melphis, Tennessee"         , "MEMPH", ),
    ("Merida, Yucatan"            , "MERID", ),
    ("Mesa, Arizona"              , "ARIZO", "AZ"),
    ("Mexico City, Mexico"        , "MEXIC", "MX"),
    ("Monterrey, Nuevo Leon"      , "MONTE", ),
    ("Montevideo, Uruguay"        , "MNTVD", ),
    ("Monticello, Utah"           , "MONTI", ),
    ("Montreal, Quebec"           , "MONTR", ),
    ("Mt. Timpanogos, Utah"       , "MTIMP", ),
    ("Nashville, Tennessee"       , "NASHV", ),
    ("Nauvoo, Illinois"           , "NAUVO", ),
    ("Nauvoo, Illinois (New),"     , "NAUV2", ),
    ("Newport Beach, California"  , "NBEAC", ),
    ("Nuku'alofa, Tonga"          , "NUKUA", "TG"),
    ("Oakland, California"        , "OAKLA", "OK"),
    ("Oaxaca, Oaxaca"             , "OAKAC", ),
    ("Ogden, Utah"                , "OGDEN", "OG"),
    ("Oklahoma City, Oklahoma"    , "OKLAH", ),
    ("Orlando, Florida"           , "ORLAN", ),
    ("Palmayra, New York"         , "PALMY", ),
    ("Papeete, Tahiti"            , "PAPEE", "TA"),
    ("Perth, Australia"           , "PERTH", ),
    ("Portland, Oregon"           , "PORTL", "PT"),
    ("Porto Alegre, Brazil"       , "PALEG", ),
    ("Preston, England"           , "PREST", ),
    ("Provo, Utah"                , "PROVO", "PV"),
    ("Raleigh, North Carolina"    , "RALEI", ),
    ("Recife, Brazil"             , "RECIF", ),
    ("Redlands, California"       , "REDLA", ),
    ("Regina, Saskatchewan"       , "REGIN", ),
    ("Reno, Nevada"               , "RENO",  ),
    ("Sacramento, California"     , "SACRA", ),
    ("St. George, Utah"           , "SGEOR", "SG"),
    ("St. Louis, Missouri"        , "SLOUI", ),
    ("St. Paul, Minnesota"        , "SPMIN", ),
    ("Salt Lake City, Utah"       , "SLAKE", "SL"),
    ("San Diego, California"      , "SDIEG", "SA"),
    ("San Antonio, Texas"         , "ANTON", ),
    ("San Jose, Costa Rica"       , "SJOSE", ),
    ("Santiago, Chile"            , "SANTI", "SN"),
    ("Santo Domingo, Dominican Republic" , "SDOMI", ),
    ("Sao Paulo, Brazil"          , "SPAUL", "SP"),
    ("Seattle, Washington"        , "SEATT", "SE"),
    ("Seoul, South Korea"         , "SEOUL", "SO"),
    ("Snowflake, Arizona"         , "SNOWF", ),
    ("Spokane, Washington"        , "SPOKA", ),
    ("Stockholm, Sweden"          , "STOCK", "ST"),
    ("Suva, Fiji"                 , "SUVA",  ),
    ("Sydney, Australia"          , "SYDNE", "SD"),
    ("Taipei, Taiwan"             , "TAIPE", "TP"),
    ("Tampico, Tamaulipas"        , "TAMPI", ),
    ("The Hague, Netherlands"     , "HAGUE", ),
    ("Tokyo, Japan"               , "TOKYO", "TK"),
    ("Toronto, Ontario"           , "TORNO", "TR"),
    ("Tuxtla Gutierrez, Chiapas"  , "TGUTI", ),
    ("Vera Cruz, Vera Cruz"       , "VERAC", ),
    ("Vernal, Utah"               , "VERNA", ),
    ("Villahermosa, Tabasco"      , "VILLA", ),
    ("Washington, D.C."           , "WASHI", "WA"),
    ("Winter Quarters, Nebraska"  , "WINTE", ),

#Other Places, Not temples.
    ("Endowment House"            , "EHOUS", "EH"),
    ("President's Office"         , "POFFI", ),
)

temple_codes = {}
for x in temples:
    temple_codes[x[0]] = x[1]

temple_to_abrev = {}
for x in temples:
    for y in x[1:]:
        temple_to_abrev[y] = x[0]

ord_type = {
    0 : _('Baptism'),
    1 : _('Endowment'),
    2 : _('Sealed to Parents'),
    3 : _('Sealed to Spouse'),
    }

ord_status = [
    _("<No Status>"),
    _("BIC"),
    _("Canceled"),
    _("Child"),
    _("Cleared"),
    _("Completed"),
    _("DNS"),
    _("Infant"),
    _("Pre-1970"),
    _("Qualified"),
    _("DNS/CAN"),
    _("Stillborn"),
    _("Submitted"),
    _("Uncleared"),
    ]
