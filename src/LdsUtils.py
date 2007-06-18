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

temples = (
    # Temple Name                  , Code   , [Old Codes...]
    ("Aba, Nigeria"                , "ABA",   ),
    ("Accra, Ghana"                , "ACCRA", ),
    ("Adelaide, Australia"         , "ADELA", ),
    ("Albuquerque, New Mexico"     , "ALBUQ", ),
    ("Anchorage, Alaska"           , "ANCHO", ),
    ("Apia, Samoa"                 , "APIA", "SAMOA", "AP"),
    ("Asuncion, Paraguay"          , "ASUNC", ),
    ("Atlanta, Georgia"            , "ATLAN", "AT"),
    ("Baton Rouge, Louisiana"      , "BROUG", ),
    ("Bern, Switzerland"           , "SWISS", "SW"),
    ("Billings, Montana"           , "BILLI", ),
    ("Birmingham, Alabama"         , "BIRMI", ),
    ("Bismarck, North Dakota"      , "BISMA", ),
    ("Bogota, Columbia"            , "BOGOT", "BG"),
    ("Boise, Idaho"                , "BOISE", "BO"),
    ("Boston, Massachusetts"       , "BOSTO", ),
    ("Bountiful, Utah"             , "BOUNT", ),
    ("Brisbane, Australia"         , "BRISB", ),
    ("Buenos Aires, Argentina"     , "BAIRE", "BA"),
    ("Campinas, Brazil"            , "CAMPI", ),
    ("Caracas, Venezuela"          , "CARAC", ),
    ("Cardston, Alberta"           , "ALBER", "AL", "ALBR"),
    ("Cebu, Philippines"           , "CEBU",  ),
    ("Chicago, Illinois"           , "CHICA", "CH"),
    ("Ciudad Juarez, Mexico"       , "CIUJU", ),
    ("Cochabamba, Boliva"          , "COCHA", ),
    ("Colonia Juarez, Chihuahua, Mexico" , "COLJU", ),
    ("Columbia, South Carolina"    , "COLSC", ),
    ("Columbia River, Washington"  , "CRIVE", ),
    ("Columbus, Ohio"              , "COLUM", ),
    ("Copenhagen, Denmark"         , "COPEN", ),
    ("Curitiba, Brazil"            , "CURIT", ),
    ("Dallas, Texas"               , "DALLA", "DA"),
    ("Denver, Colorado"            , "DENVE", "DV"),
    ("Detroit, Michigan"           , "DETRO", ),
    ("Draper, Utah"                , "DRAPE", ),
    ("Edmonton, Alberta"           , "EDMON", ),
    ("Frankfurt, Germany"          , "FRANK", "FR"),
    ("Freiberg, Germany"           , "FREIB", "FD"),
    ("Fresno, California"          , "FRESN", ),
    ("Fukuoka, Japan"              , "FUKUO", ),
    ("Guadalajara, Mexico"         , "GUADA", ),
    ("Guatemala City, Guatemala"   , "GUATE", "GA", "GU"),
    ("Guayaquil, Ecuador"          , "GUAYA", "GY"),
    ("Halifax, Nova Scotia"        , "HALIF", ),
    ("Hamilton, New Zealand"       , "NZEAL", "NZ"),
    ("Harrison, New York"          , "HARRI", "NYORK"),
    ("Hartford, Connecticut"       , "HARTF", ),
    ("Helsinki, Finland"           , "HELSI", ),
    ("Hermosillo, Sonora, Mexico"  , "HERMO", ),
    ("Hong Kong, China"            , "HKONG", ),
    ("Houston, Texas"              , "HOUST", ),
    ("Idaho Falls, Idaho"          , "IFALL", "IF"),
    ("Johannesburg, South Africa"  , "JOHAN", "JO"),
    ("Jordan River, Utah"          , "JRIVE", "JR"),
    ("Kona, Hawaii"                , "KONA",  ),
    ("Kiev, Ukraine"               , "KIEV",  ),
    ("Kirtland, Ohio"              , "KIRTL", ),
    ("Laie, Hawaii"                , "HAWAI", "HA"),
    ("Las Vegas, Nevada"           , "LVEGA", "LV"),
    ("Lima, Peru"                  , "LIMA" , "LI"),
    ("Logan, Utah"                 , "LOGAN", "LG"),
    ("London, England"             , "LONDO", "LD"),
    ("Los Angeles, California"     , "LANGE", "LA"),
    ("Louisville, Kentucky"        , "LOUIS", ),
    ("Lubbock, Texas"              , "LUBBO", ),
    ("Madrid, Spain"               , "MADRI", ),
    ("Manhattan, New York"         , "MANHA", ),
    ("Manila, Philippines"         , "MANIL", "MA"),
    ("Manti, Utah"                 , "MANTI", "MT"),
    ("Medford, Oregon"             , "MEDFO", ),
    ("Melbourne, Australia"        , "MELBO", ),
    ("Memphis, Tennessee"          , "MEMPH", ),
    ("Merida, Mexico"              , "MERID", ),
    ("Mesa, Arizona"               , "ARIZO", "AZ"),
    ("Mexico City, Mexico"         , "MEXIC", "MX"),
    ("Monterrey, Mexico"           , "MONTE", ),
    ("Montevideo, Uruguay"         , "MNTVD", ),
    ("Monticello, Utah"            , "MONTI", ),
    ("Montreal, Quebec"            , "MONTR", ),
    ("Mt. Timpanogos, Utah"        , "MTIMP", ),
    ("Nashville, Tennessee"        , "NASHV", ),
    ("Nauvoo, Illinois"            , "NAUVO", "NV"),
    ("Nauvoo, Illinois (New)"      , "NAUV2", ),
    ("Newport Beach, California"   , "NBEAC", ),
    ("Nuku'alofa, Tonga"           , "NUKUA", "TG"),
    ("Oakland, California"         , "OAKLA", "OK"),
    ("Oaxaca, Mexico"              , "OAXAC", ),
    ("Ogden, Utah"                 , "OGDEN", "OG"),
    ("Oklahoma City, Oklahoma"     , "OKLAH", ),
    ("Oquirrh Mountain, Utah"      , "OMOUN", ),
    ("Orlando, Florida"            , "ORLAN", ),
    ("Palmyra, New York"           , "PALMY", ),
    ("Panama City, Panama"         , "PANAM", ),
    ("Papeete, Tahiti"             , "PAPEE", "TA"),
    ("Perth, Australia"            , "PERTH", ),
    ("Portland, Oregon"            , "PORTL", "PT"),
    ("Porto Alegre, Brazil"        , "PALEG", ),
    ("Preston, England"            , "PREST", ),
    ("Provo, Utah"                 , "PROVO", "PV"),
    ("Quetzaltenango, Guatemala"   , "QUETZ", ),
    ("Raleigh, North Carolina"     , "RALEI", ),
    ("Recife, Brazil"              , "RECIF", ),
    ("Redlands, California"        , "REDLA", ),
    ("Regina, Saskatchewan"        , "REGIN", ),
    ("Reno, Nevada"                , "RENO",  ),
    ("Rexburg, Idaho"              , "REXBU", ),
    ("Sacramento, California"      , "SACRA", ),
    ("St. George, Utah"            , "SGEOR", "SG"),
    ("St. Louis, Missouri"         , "SLOUI", ),
    ("St. Paul, Minnesota"         , "SPMIN", ),
    ("Salt Lake City, Utah"        , "SLAKE", "SL"),
    ("San Antonio, Texas"          , "SANTO", ),
    ("San Diego, California"       , "SDIEG", "SA"),
    ("San Jose, Costa Rica"        , "SJOSE", ),
    ("Santiago, Chile"             , "SANTI", "SN"),
    ("Santo Domingo, Dominican Republic" , "SDOMI", ),
    ("Sao Paulo, Brazil"           , "SPAUL", "SP"),
    ("Seattle, Washington"         , "SEATT", "SE"),
    ("Seoul, South Korea"          , "SEOUL", "SO"),
    ("Snowflake, Arizona"          , "SNOWF", ),
    ("Spokane, Washington"         , "SPOKA", ),
    ("Stockholm, Sweden"           , "STOCK", "ST"),
    ("Suva, Fiji"                  , "SUVA",  ),
    ("Sydney, Australia"           , "SYDNE", "SD"),
    ("Taipei, Taiwan"              , "TAIPE", "TP"),
    ("Tampico, Mexico"             , "TAMPI", ),
    ("Tegucigalpa, Honduras"       , "TEGUC", ),
    ("The Hague, Netherlands"      , "HAGUE", ),
    ("Tokyo, Japan"                , "TOKYO", "TK"),
    ("Toronto, Ontario"            , "TORON", "TORNO", "TR"),
    ("Tuxtla Gutierrez, Mexico"    , "TGUTI", ),
    ("Twin Falls, Idaho"           , "TFALL", "TWINF"),
    ("Vancouver, British Columbia" , "VANCO", ),
    ("Veracruz, Mexico"            , "VERAC", ),
    ("Vernal, Utah"                , "VERNA", ),
    ("Villahermosa, Mexico"        , "VILLA", ),
    ("Washington, D.C."            , "WASHI", "WA"),
    ("Winter Quarters, Nebraska"   , "WINTE", "WQUAR"),

# Other places.  Not temples.
    ("Endowment House"             , "EHOUS", "EH"),
    ("President's Office"          , "POFFI", "PO"),
    ("Historian's Office"          , "HOFFI", "HO"),
    ("Other"                       , "OTHER", ),
)

temple_codes = {}
for x in temples:
    temple_codes[x[0]] = x[1]

temple_to_abrev = {}
for x in temples:
    for y in x[1:]:
        temple_to_abrev[y] = x[0]
