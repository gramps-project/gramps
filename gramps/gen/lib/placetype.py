# encoding: utf-8
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2019       Paul Culley
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
Provide the different place types.
With the GEPS045 update we now have over 200 place types.  The original
type numbers and definitions are from http://gov.genealogy.net/types.owl/
The definitions here were in part created via a script that processed the
original file.

The types are subdivided into groups (types.owl called them classes).
These groups are used to make the place types menu a bit easier, and to
allow selection and display of hierarchies and groups for titling.  For
example, Gramps originally had the concept of Country, County, City type
etc.  Since there are now multiple place types which could be described
as countries, we use the ADM0 group as a group designation for Countries.
The same goes for the other ADMx groups.  Some types are also described
as Religious, or just places.

The Groups are encoded into the place types as a bit field in the high
order bits.  This makes identifying a place type as belonging to a group
a simple bitwise 'and' operation.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .grampstype import GrampsType
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext


# _T_ is a gramps-defined keyword -- see po/update_po.py and po/genpot.sh
def _T_(value):  # enable deferred translations (see Python docs 22.1.3.4)
    return value


class PlaceType(GrampsType):

    UNKNOWN = -0x1              #
    CUSTOM = 0x0                #
    AMTVERWALT1 = 0x8000401     # 1,ADM,ADM4
    AMTSBEZIRK = 0x8000402      # 2,ADM,ADM4
    MAGISTRATE3 = 0x8003        # 3,JUDI
    BAUERSCHAFT = 0x10000404    # 4,ADM,ADM5
    DISTRICT = 0x2000405        # 5,ADM,ADM2
    DIOCESE = 0x1006            # 6,RELI
    FEDERALSTATE = 0x1000407    # 7,ADM,ADM1
    CASTLE = 0x20008            # 8,PLACE
    DEANERY = 0x1009            # 9,RELI
    DEPARTMENT = 0x200040a      # 10,ADM,ADM2
    DIOCESE11 = 0x100b          # 11,RELI
    DOMPFARREI = 0x100c         # 12,RELI
    FILIALCHURCH = 0x100d       # 13,RELI
    FLECKENGEB14 = 0x1000040e   # 14,ADM,ADM5
    FIELDNAME = 0x8000f         # 15,UNPOP
    FREESTATE = 0x1000410       # 16,ADM,ADM1
    BUILDING = 0x20011          # 17,PLACE
    MUNICIPALITY = 0x10000412   # 18,ADM,ADM5
    GERICHTSBE19 = 0x8013       # 19,JUDI
    COUNTSHIP = 0x414           # 20,ADM
    MANORBUILD21 = 0x20015      # 21,PLACE
    DOMINION = 0x416            # 22,ADM
    DUCHY = 0x417               # 23,ADM
    FARM = 0x20018              # 24,PLACE
    CANTON25 = 0x1000419        # 25,ADM,ADM1
    CHURCH = 0x101a             # 26,RELI
    KIRCHENKREIS = 0x101b       # 27,RELI
    KIRCHENPRO28 = 0x101c       # 28,RELI
    PARISH29 = 0x101d           # 29,RELI
    MONASTERYB30 = 0x2101e      # 30,RELI,PLACE
    KINGDOM = 0x180041f         # 31,ADM,ADM0,ADM1
    COUNTY = 0x4000420          # 32,ADM,ADM3
    ELECTORATE = 0x1000421      # 33,ADM,ADM1
    STATE34 = 0x1000422         # 34,ADM,ADM1
    NATIONALCH35 = 0x1023       # 35,RELI
    RURALCOUNT36 = 0x4000424    # 36,ADM,ADM3
    OBERAMT = 0x4000425         # 37,ADM,ADM3
    OBLAST = 0xc26              # 38,ADM,CIVIL
    PLACE = 0x20027             # 39,PLACE
    PARTOFPLACE = 0x20028       # 40,PLACE
    PFARRREKTO41 = 0x1029       # 41,RELI
    PARISH42 = 0x102a           # 42,RELI
    PFARRKURATIE = 0x102b       # 43,RELI
    PFARRVERBAND = 0x102c       # 44,RELI
    PROVINCE = 0x300042d        # 45,ADM,ADM1,ADM2
    ADMINISTRA46 = 0x200042e    # 46,ADM,ADM2
    HISTORICAL47 = 0x202f       # 47,GEOG
    SAMTGEMEINDE = 0x8000430    # 48,ADM,ADM4
    SPRENGEL = 0x1031           # 49,RELI
    COUNTRY = 0x800432          # 50,ADM,ADM0
    TOWN = 0x20033              # 51,PLACE
    BOROUGH52 = 0x20000434      # 52,ADM,ADM6
    URBANCOUNT53 = 0x4000435    # 53,ADM,ADM3
    PARTOFTOWN = 0x20036        # 54,PLACE
    VILLAGE = 0x20037           # 55,PLACE
    REPUBLIC = 0x800438         # 56,ADM,ADM0
    AMTDANISCHES = 0x4000439    # 57,ADM,ADM3
    UNIONREPUB58 = 0x100043a    # 58,ADM,ADM1
    VOIVODSHIP = 0x100043b      # 59,ADM,ADM1
    PRINCIPALITY = 0x43c        # 60,ADM
    GRANDDUCHY = 0x43d          # 61,ADM
    MARGRAVATE = 0x43e          # 62,ADM
    RAYON = 0x400043f           # 63,ADM,ADM3
    VORWERK = 0x20040           # 64,PLACE
    PFARRDORF = 0x20041         # 65,PLACE
    VILLAGE66 = 0x20042         # 66,PLACE
    SOLITUDE = 0x20043          # 67,PLACE
    HAUPTORT = 0x20044          # 68,PLACE
    HAMLET = 0x20045            # 69,PLACE
    BAILIWICK = 0x8446          # 70,ADM,JUDI
    CONFEDERAT71 = 0x800447     # 71,ADM,ADM0
    PEOPLESREP72 = 0x800448     # 72,ADM,ADM0
    LANDDROSTEI = 0x449         # 73,ADM
    GUTERDISTR75 = 0x400044b    # 75,ADM,ADM3
    ADELIGESGUT = 0x1000044c    # 76,ADM,ADM5
    REICHSKREIS = 0x44d         # 77,ADM
    AMTADMINIS78 = 0x400044e    # 78,ADM,ADM3
    HUNDRED = 0x844f            # 79,ADM,JUDI
    LANDSCHAFT80 = 0x450        # 80,ADM
    MONASTERY = 0x451           # 81,ADM
    DOMKAPITEL82 = 0x452        # 82,ADM
    HANSEATICC83 = 0x10000453   # 83,ADM,ADM5
    KIRCHSPIEL84 = 0x454        # 84,ADM
    RURALMUNIC85 = 0x10000455   # 85,ADM,ADM5
    PARTPROVINCE = 0x456        # 86,ADM
    MILL = 0x20057              # 87,PLACE
    JUDET = 0x4000458           # 88,ADM,ADM3
    CEMETERY = 0x80859          # 89,CIVIL,UNPOP
    ABANDONEDP90 = 0x8005a      # 90,UNPOP
    BISTUMSREG91 = 0x105b       # 91,RELI
    KIRCHENGEM92 = 0x105c       # 92,RELI
    REICHSSTADT = 0x1000045d    # 93,ADM,ADM5
    VERWALTUNG94 = 0x800045e    # 94,ADM,ADM4
    COUNTYLEVE95 = 0x1c00045f   # 95,ADM,ADM3,ADM4,ADM5
    ARCHBISHOP96 = 0x1060       # 96,RELI
    BURGERMEIS97 = 0x18000461   # 97,ADM,ADM4,ADM5
    VERALTETAM98 = 0x400062     # 98,OTHER
    CAPTAINCY = 0x4000463       # 99,ADM,ADM3
    KREISHAUPT100 = 0x2000464   # 100,ADM,ADM2
    KREISDIREK101 = 0x2000465   # 101,ADM,ADM2
    FORESTERSH102 = 0x20066     # 102,PLACE
    CIVILREGIS103 = 0x867       # 103,CIVIL
    VERALTETST104 = 0x400068    # 104,OTHER
    LANDGERICHT = 0x8069        # 105,JUDI
    ISLAND = 0x286b             # 107,CIVIL,GEOG
    GUTSBEZIRK = 0x1000046c     # 108,ADM,ADM5
    FORSTGUTSB109 = 0x1000046d  # 109,ADM,ADM5
    DISTRICTOF110 = 0x400046e   # 110,ADM,ADM3
    SCHLOSS = 0x2006f           # 111,PLACE
    GESPANSCHAFT = 0x470        # 112,ADM
    COMITATUS = 0x471           # 113,ADM
    VEST = 0x8472               # 114,ADM,JUDI
    FORESTRY = 0x473            # 115,ADM
    OBERFORSTE116 = 0x474       # 116,ADM
    UNTERFORST117 = 0x475       # 117,ADM
    TRAINSTATION = 0x60076      # 118,PLACE,TRANS
    STOPSTATION = 0xc0077       # 119,TRANS,UNPOP
    SETTLEMENT120 = 0x20078     # 120,PLACE
    COLONY = 0x20079            # 121,PLACE
    VERBANDSGE122 = 0x800047a   # 122,ADM,ADM4
    ABBEY = 0x107c              # 124,RELI
    IMPERIALAB125 = 0x47d       # 125,ADM
    SYSSEL = 0x400047e          # 126,ADM,ADM3
    VERWALTUNG127 = 0x800047f   # 127,ADM,ADM4
    LANDGRAFSC128 = 0x480       # 128,ADM
    SETTLEMENT = 0x20081        # 129,PLACE
    STATE = 0x1000482           # 130,ADM,ADM1
    WEICHBILD = 0x483           # 131,ADM
    REGION = 0x1000485          # 133,ADM,ADM1
    ARRONDISSE134 = 0x4000486   # 134,ADM,ADM3
    CANTON = 0x487              # 135,ADM
    COMMUNE = 0x10000488        # 136,ADM,ADM5
    REGION137 = 0x489           # 137,ADM
    OBERLANDRA138 = 0x200048a   # 138,ADM,ADM2
    EINSCHICHT = 0x2008b        # 139,PLACE
    EINHEITSGE140 = 0x1000048c  # 140,ADM,ADM5
    REICHSGAU = 0x100048e       # 142,ADM,ADM1
    KOMMUNE = 0x1000048f        # 143,ADM,ADM5
    ORTSCHAFT = 0x20000490      # 144,ADM,ADM6
    MARKT = 0x10000491          # 145,ADM,ADM5
    BEZIRKSHAU146 = 0x4000492   # 146,ADM,ADM3
    VERALTETPO147 = 0x400093    # 147,OTHER
    ERFULLENDE148 = 0x10000494  # 148,ADM,ADM5
    LANDRATSAMT = 0x4000495     # 149,ADM,ADM3
    CITY = 0x10000496           # 150,ADM,ADM5
    OBERLANDES151 = 0x8097      # 151,JUDI
    LANDBURGER152 = 0x8000498   # 152,ADM,ADM4
    KOMMISSARIAT = 0x1099       # 153,RELI
    HONSCHAFT = 0x1000849a      # 154,ADM,JUDI,ADM5
    REGION155 = 0x109b          # 155,RELI
    GEMEINDEBE156 = 0x2000049c  # 156,ADM,ADM6
    GUBERNIYA = 0x49d           # 157,ADM
    GEMEINDETEIL = 0x2000049e   # 158,ADM,ADM6
    KHUTOR = 0x2009f            # 159,PLACE
    SOVIETREPU160 = 0x10004a0   # 160,ADM,ADM1
    VERWALTUNG161 = 0x20004a1   # 161,ADM,ADM2
    STADTUNDLA162 = 0x100004a2  # 162,ADM,ADM5
    ORTSGEMEINDE = 0x100004a3   # 163,ADM,ADM5
    ORTSBEZIRK = 0x200004a4     # 164,ADM,ADM6
    GNOTSCHAFT = 0x100004a5     # 165,ADM,ADM5
    RUINS = 0x808a6             # 166,CIVIL,UNPOP
    MANDATETER167 = 0x4a7       # 167,ADM
    PROVINZSCH168 = 0x10004a8   # 168,ADM,ADM1
    GEMEINDESC169 = 0x100004a9  # 169,ADM,ADM5
    DISTRICT170 = 0x4aa         # 170,ADM
    STADTHAUPT171 = 0x40004ab   # 171,ADM,ADM3
    KATASTRALG172 = 0x8ac       # 172,CIVIL
    REICHSKOMM173 = 0x4ad       # 173,ADM
    GENERALDIS174 = 0x4ae       # 174,ADM
    KREISGEBIET = 0x4af         # 175,ADM
    PROTECTORATE = 0x4b0        # 176,ADM
    REICHSRITT177 = 0x4b1       # 177,ADM
    RITTERKANTON = 0x4b2        # 178,ADM
    RITTERKREIS = 0x4b3         # 179,ADM
    MARKTGEMEI180 = 0x100004b4  # 180,ADM,ADM5
    ROTTE = 0x200204b5          # 181,ADM,PLACE,ADM6
    ERZSTIFT = 0x4b6            # 182,ADM
    HOCHSTIFT = 0x4b7           # 183,ADM
    KAMMERSCHR184 = 0x4b8       # 184,ADM
    KLOSTERAMT = 0x40004b9      # 185,ADM,ADM3
    RENTKAMMER = 0x40004ba      # 186,ADM,ADM3
    ZUUBERPRUFEN = 0x4000bb     # 187,OTHER
    RITTERORDEN = 0x4bc         # 188,ADM
    GROSSPRIORAT = 0x4bd        # 189,ADM
    BALLEI = 0x4be              # 190,ADM
    KOMMENDE = 0x4bf            # 191,ADM
    ZONEOFOCCU192 = 0x4c0       # 192,ADM
    ALM = 0x200c1               # 193,PLACE
    DISTRIKTSAMT = 0x4c2        # 194,ADM
    VERALTETBU195 = 0x4000c3    # 195,OTHER
    VERALTETLA196 = 0x4000c4    # 196,OTHER
    VERALTETSO197 = 0x4000c5    # 197,OTHER
    VERALTETFR198 = 0x4000c6    # 198,OTHER
    VERALTETFR199 = 0x4000c7    # 199,OTHER
    VERALTETFR200 = 0x4000c8    # 200,OTHER
    LANDESKOMM201 = 0x20004c9   # 201,ADM,ADM2
    AMTSGERICH202 = 0x80ca      # 202,JUDI
    DOMANIALAMT = 0x40004cb     # 203,ADM,ADM3
    RITTERSCHA204 = 0x40004cc   # 204,ADM,ADM3
    SELSOVIET = 0x80004cd       # 205,ADM,ADM4
    REGIONALKI206 = 0x10ce      # 206,RELI
    OBERAMTSBE207 = 0x40004cf   # 207,ADM,ADM3
    KIRCHENBUND = 0x10d2        # 210,RELI
    LANDGEBIET = 0x20004d3      # 211,ADM,ADM2
    LANDHERREN212 = 0x40004d4   # 212,ADM,ADM3
    GORSOVIET = 0x100004d5      # 213,ADM,ADM5
    REALM = 0x8004d6            # 214,ADM,ADM0
    REICHSHALFTE = 0x4d7        # 215,ADM
    LANDESTEIL = 0x4d8          # 216,ADM
    DIREKTIONS217 = 0x20004d9   # 217,ADM,ADM2
    STADTEINHE218 = 0x100004da  # 218,ADM,ADM5
    EXPOSITUR = 0x10db          # 219,RELI
    FYLKE = 0x10004dd           # 221,ADM,ADM1
    KREISMITTL222 = 0x20004de   # 222,ADM,ADM2
    LANDGERICH223 = 0x40084df   # 223,ADM,JUDI,ADM3
    PFLEGGERICHT = 0x84e0       # 224,ADM,JUDI
    RENTAMTALT225 = 0x20004e1   # 225,ADM,ADM2
    OBMANNSCHAFT = 0x80004e2    # 226,ADM,ADM4
    KIRCHSPIEL227 = 0x100004e3  # 227,ADM,ADM5
    GERICHTSAMT = 0x80e4        # 228,JUDI
    GROUPOFHOU229 = 0x200e5     # 229,PLACE
    SCATTEREDS230 = 0x200e6     # 230,PLACE
    HOFE = 0x200e7              # 231,PLACE
    RANDORT = 0x200e8           # 232,PLACE
    FLECKENSIE233 = 0x200e9     # 233,PLACE
    BOROUGH = 0x4ea             # 234,ADM
    UNITARYAUT235 = 0x4eb       # 235,ADM
    HOUSES = 0x200ec            # 236,PLACE
    SIEDLUNGSRAT = 0x4ed        # 237,ADM
    URBANTYPES238 = 0x200ee     # 238,PLACE
    VERWALTUNG239 = 0x40004ef   # 239,ADM,ADM3
    UYEZD = 0x4f0               # 240,ADM
    VOLOST = 0x40004f1          # 241,ADM,ADM3
    KATASTERAMT = 0x8f2         # 242,CIVIL
    PROPSTEI = 0x10f3           # 243,RELI
    NEBENKIRCHE = 0x10f4        # 244,RELI
    CHAPEL = 0x10f5             # 245,RELI
    GROMADA = 0x100004f6        # 246,ADM,ADM5
    ORTSTEILVE247 = 0x200004f7  # 247,ADM,ADM6
    SCHULZENAMT = 0x200004f8    # 248,ADM,ADM6
    ERZBISCHOF249 = 0x10f9      # 249,RELI
    APOSTOLISC250 = 0x10fa      # 250,RELI
    AUTONOMEGE251 = 0x4fb       # 251,ADM
    LOCALGOVER252 = 0x4fc       # 252,ADM
    RELIGIOUSO253 = 0x10fd      # 253,RELI
    OKRUG = 0x4fe               # 254,ADM
    STADTGUT = 0x100004ff       # 255,ADM,ADM5
    LANDESBEZIRK = 0x1000500    # 256,ADM,ADM1
    LANDGEMEIN257 = 0x10000501  # 257,ADM,ADM5
    STADTGEMEI258 = 0x10000502  # 258,ADM,ADM5
    LANDVOGTEI259 = 0x8000503   # 259,ADM,ADM4
    DELEGATURB260 = 0x1104      # 260,RELI
    HOFSCHAFT = 0x20105         # 261,PLACE
    STADTTEILV262 = 0x20000506  # 262,ADM,ADM6
    SPRENGELOB263 = 0x1107      # 263,RELI
    MAIRIE = 0x8000508          # 264,ADM,ADM4
    SULTANATE = 0x509           # 265,ADM
    LANDRATSBE266 = 0x800050a   # 266,ADM,ADM4
    STREET = 0x200              # 512
    LOCALITY = 0x20201          # 513,PLACE
    NUMBER = 0x202              # 514
    NEIGHBORHOOD = 0x20203      # 515,PLACE
    PARISH = 0x8000604          # 516,ADM,ADM4
    ADM0 = 0x800209             # 520,ADM,ADM0
    ADM1 = 0x100020a            # 521,ADM,ADM1
    ADM2 = 0x200020b            # 522,ADM,ADM2
    ADM3 = 0x400020c            # 523,ADM,ADM3
    ADM4 = 0x800020d            # 524,ADM,ADM4
    ADM5 = 0x1000020e           # 525,ADM,ADM5
    ADM6 = 0x2000020f           # 526,ADM,ADM6

    _CUSTOM = CUSTOM
    _DEFAULT = UNKNOWN

    _DATAMAP = [
        (UNKNOWN, _("Unknown"), "Unknown"),
        (CUSTOM, _("Custom"), "Custom"),
        (AMTVERWALT1, _("Amt (verwaltung)"), "Amt (verwaltung)"),
        # Translators: see http://gov.genealogy.net/type/list Type 2
        (AMTSBEZIRK, _("Amtsbezirk"), "Amtsbezirk"),
        # Translators: see http://gov.genealogy.net/type/list Type 3
        (MAGISTRATE3, _("Magistrates' court"), "Magistrates' court"),
        # Translators: see http://gov.genealogy.net/type/list Type 4
        (BAUERSCHAFT, _("Bauerschaft"), "Bauerschaft"),
        # Translators: see http://gov.genealogy.net/type/list Type 5
        (DISTRICT, _("District"), "District"),
        # Translators: see http://gov.genealogy.net/type/list Type 6
        (DIOCESE, _("Diocese"), "Diocese"),
        # Translators: see http://gov.genealogy.net/type/list Type 7
        (FEDERALSTATE, _("Federal state"), "Federal state"),
        # Translators: see http://gov.genealogy.net/type/list Type 8
        (CASTLE, _("Castle"), "Castle"),
        # Translators: see http://gov.genealogy.net/type/list Type 9
        (DEANERY, _("Deanery"), "Deanery"),
        # Translators: see http://gov.genealogy.net/type/list Type 10
        (DEPARTMENT, _("Department"), "Department"),
        # Translators: see http://gov.genealogy.net/type/list Type 11
        (DIOCESE11, _("Diocese"), "Diocese11"),
        # Translators: see http://gov.genealogy.net/type/list Type 12
        (DOMPFARREI, _("Dompfarrei"), "Dompfarrei"),
        # Translators: see http://gov.genealogy.net/type/list Type 13
        (FILIALCHURCH, _("Filial church"), "Filial church"),
        # Translators: see http://gov.genealogy.net/type/list Type 14
        (FLECKENGEB14, _("Flecken (gebietskörperschaft)"),
         "Flecken (gebietskörperschaft)"),
        # Translators: see http://gov.genealogy.net/type/list Type 15
        (FIELDNAME, _("Field name"), "Field name"),
        # Translators: see http://gov.genealogy.net/type/list Type 16
        (FREESTATE, _("Free state"), "Free state"),
        # Translators: see http://gov.genealogy.net/type/list Type 17
        (BUILDING, _("Building"), "Building"),
        # Translators: see http://gov.genealogy.net/type/list Type 18
        (MUNICIPALITY, _("Municipality"), "Municipality"),
        # Translators: see http://gov.genealogy.net/type/list Type 19
        (GERICHTSBE19, _("Gerichtsbezirk"), "Gerichtsbezirk"),
        # Translators: see http://gov.genealogy.net/type/list Type 20
        (COUNTSHIP, _("Countship"), "Countship"),
        # Translators: see http://gov.genealogy.net/type/list Type 21
        (MANORBUILD21, _("Manor (building)"), "Manor (building)"),
        # Translators: see http://gov.genealogy.net/type/list Type 22
        (DOMINION, _("Dominion"), "Dominion"),
        # Translators: see http://gov.genealogy.net/type/list Type 23
        (DUCHY, _("Duchy"), "Duchy"),
        # Translators: see http://gov.genealogy.net/type/list Type 24
        (FARM, _("Farm"), "Farm"),
        # Translators: see http://gov.genealogy.net/type/list Type 25
        (CANTON25, _("Canton"), "Canton25"),
        # Translators: see http://gov.genealogy.net/type/list Type 26
        (CHURCH, _("Church"), "Church"),
        # Translators: see http://gov.genealogy.net/type/list Type 27
        (KIRCHENKREIS, _("Kirchenkreis"), "Kirchenkreis"),
        # Translators: see http://gov.genealogy.net/type/list Type 28
        (KIRCHENPRO28, _("Kirchenprovinz"), "Kirchenprovinz"),
        # Translators: see http://gov.genealogy.net/type/list Type 29
        (PARISH29, _("Parish"), "Parish29"),
        # Translators: see http://gov.genealogy.net/type/list Type 30
        (MONASTERYB30, _("Monastery (building)"), "Monastery (building)"),
        # Translators: see http://gov.genealogy.net/type/list Type 31
        (KINGDOM, _("Kingdom"), "Kingdom"),
        # Translators: see http://gov.genealogy.net/type/list Type 32
        (COUNTY, _("County"), "County"),
        # Translators: see http://gov.genealogy.net/type/list Type 33
        (ELECTORATE, _("Electorate"), "Electorate"),
        # Translators: see http://gov.genealogy.net/type/list Type 34
        (STATE34, _("State"), "State34"),
        # Translators: see http://gov.genealogy.net/type/list Type 35
        (NATIONALCH35, _("National church"), "National church"),
        # Translators: see http://gov.genealogy.net/type/list Type 36
        (RURALCOUNT36, _("Rural county (rural)"), "Rural county (rural)"),
        # Translators: see http://gov.genealogy.net/type/list Type 37
        (OBERAMT, _("Oberamt"), "Oberamt"),
        # Translators: see http://gov.genealogy.net/type/list Type 38
        (OBLAST, _("Oblast"), "Oblast"),
        # Translators: see http://gov.genealogy.net/type/list Type 39
        (PLACE, _("Place"), "Place"),
        # Translators: see http://gov.genealogy.net/type/list Type 40
        (PARTOFPLACE, _("Part of place"), "Part of place"),
        # Translators: see http://gov.genealogy.net/type/list Type 41
        (PFARRREKTO41, _("Pfarr-rektorat"), "Pfarr-rektorat"),
        # Translators: see http://gov.genealogy.net/type/list Type 42
        (PARISH42, _("Parish, group of people"), "Parish42"),
        # Translators: see http://gov.genealogy.net/type/list Type 43
        (PFARRKURATIE, _("Pfarrkuratie"), "Pfarrkuratie"),
        # Translators: see http://gov.genealogy.net/type/list Type 44
        (PFARRVERBAND, _("Pfarrverband"), "Pfarrverband"),
        # Translators: see http://gov.genealogy.net/type/list Type 45
        (PROVINCE, _("Province"), "Province"),
        # Translators: see http://gov.genealogy.net/type/list Type 46
        (ADMINISTRA46, _("Administrative district"),
         "Administrative district"),
        # Translators: see http://gov.genealogy.net/type/list Type 47
        (HISTORICAL47, _("Historical region"), "Historical region"),
        # Translators: see http://gov.genealogy.net/type/list Type 48
        (SAMTGEMEINDE, _("Samtgemeinde"), "Samtgemeinde"),
        # Translators: see http://gov.genealogy.net/type/list Type 49
        (SPRENGEL, _("Sprengel"), "Sprengel"),
        # Translators: see http://gov.genealogy.net/type/list Type 50
        (COUNTRY, _("Country"), "Country"),
        # Translators: see http://gov.genealogy.net/type/list Type 51
        (TOWN, _("Town"), "Town"),
        # Translators: see http://gov.genealogy.net/type/list Type 52
        (BOROUGH52, _("Borough"), "Borough52"),
        # Translators: see http://gov.genealogy.net/type/list Type 53
        (URBANCOUNT53, _("Urban county (city)"), "Urban county (city)"),
        # Translators: see http://gov.genealogy.net/type/list Type 54
        (PARTOFTOWN, _("Part of town"), "Part of town"),
        # Translators: see http://gov.genealogy.net/type/list Type 55
        (VILLAGE, _("Village"), "Village"),
        # Translators: see http://gov.genealogy.net/type/list Type 56
        (REPUBLIC, _("Republic"), "Republic"),
        # Translators: see http://gov.genealogy.net/type/list Type 57
        (AMTDANISCHES, _("Amt (dänisches)"), "Amt (dänisches)"),
        # Translators: see http://gov.genealogy.net/type/list Type 58
        (UNIONREPUB58, _("Union republic"), "Union republic"),
        # Translators: see http://gov.genealogy.net/type/list Type 59
        (VOIVODSHIP, _("Voivodship"), "Voivodship"),
        # Translators: see http://gov.genealogy.net/type/list Type 60
        (PRINCIPALITY, _("Principality"), "Principality"),
        # Translators: see http://gov.genealogy.net/type/list Type 61
        (GRANDDUCHY, _("Grand duchy"), "Grand duchy"),
        # Translators: see http://gov.genealogy.net/type/list Type 62
        (MARGRAVATE, _("Margravate"), "Margravate"),
        # Translators: see http://gov.genealogy.net/type/list Type 63
        (RAYON, _("Rayon"), "Rayon"),
        # Translators: see http://gov.genealogy.net/type/list Type 64
        (VORWERK, _("Vorwerk"), "Vorwerk"),
        # Translators: see http://gov.genealogy.net/type/list Type 65
        (PFARRDORF, _("Pfarrdorf"), "Pfarrdorf"),
        # Translators: see http://gov.genealogy.net/type/list Type 66
        (VILLAGE66, _("Village with church"), "Village66"),
        # Translators: see http://gov.genealogy.net/type/list Type 67
        (SOLITUDE, _("Solitude"), "Solitude"),
        # Translators: see http://gov.genealogy.net/type/list Type 68
        (HAUPTORT, _("Hauptort"), "Hauptort"),
        # Translators: see http://gov.genealogy.net/type/list Type 69
        (HAMLET, _("Hamlet"), "Hamlet"),
        # Translators: see http://gov.genealogy.net/type/list Type 70
        (BAILIWICK, _("Bailiwick"), "Bailiwick"),
        # Translators: see http://gov.genealogy.net/type/list Type 71
        (CONFEDERAT71, _("Confederation"), "Confederation"),
        # Translators: see http://gov.genealogy.net/type/list Type 72
        (PEOPLESREP72, _("People's republic"), "People's republic"),
        # Translators: see http://gov.genealogy.net/type/list Type 73
        (LANDDROSTEI, _("Landdrostei"), "Landdrostei"),
        # Translators: see http://gov.genealogy.net/type/list Type 75
        (GUTERDISTR75, _("Güterdistrikt"), "Güterdistrikt"),
        # Translators: see http://gov.genealogy.net/type/list Type 76
        (ADELIGESGUT, _("Adeliges gut"), "Adeliges gut"),
        # Translators: see http://gov.genealogy.net/type/list Type 77
        (REICHSKREIS, _("Reichskreis"), "Reichskreis"),
        # Translators: see http://gov.genealogy.net/type/list Type 78
        (AMTADMINIS78, _("Amt (administrative division)"),
         "Amt (administrative division)"),
        # Translators: see http://gov.genealogy.net/type/list Type 79
        (HUNDRED, _("Hundred"), "Hundred"),
        # Translators: see http://gov.genealogy.net/type/list Type 80
        (LANDSCHAFT80, _("Landschaft (verwaltung)"),
         "Landschaft (verwaltung)"),
        # Translators: see http://gov.genealogy.net/type/list Type 81
        (MONASTERY, _("Monastery"), "Monastery"),
        # Translators: see http://gov.genealogy.net/type/list Type 82
        (DOMKAPITEL82, _("Domkapitel (herrschaft)"),
         "Domkapitel (herrschaft)"),
        # Translators: see http://gov.genealogy.net/type/list Type 83
        (HANSEATICC83, _("Hanseatic city"), "Hanseatic city"),
        # Translators: see http://gov.genealogy.net/type/list Type 84
        (KIRCHSPIEL84, _("Kirchspielvogtei"), "Kirchspielvogtei"),
        # Translators: see http://gov.genealogy.net/type/list Type 85
        (RURALMUNIC85, _("Rural municipality"), "Rural municipality"),
        # Translators: see http://gov.genealogy.net/type/list Type 86
        (PARTPROVINCE, _("Part province"), "Part province"),
        # Translators: see http://gov.genealogy.net/type/list Type 87
        (MILL, _("Mill"), "Mill"),
        # Translators: see http://gov.genealogy.net/type/list Type 88
        (JUDET, _("Judet"), "Judet"),
        # Translators: see http://gov.genealogy.net/type/list Type 89
        (CEMETERY, _("Cemetery"), "Cemetery"),
        # Translators: see http://gov.genealogy.net/type/list Type 90
        (ABANDONEDP90, _("Abandoned place"), "Abandoned place"),
        # Translators: see http://gov.genealogy.net/type/list Type 91
        (BISTUMSREG91, _("Bistumsregion"), "Bistumsregion"),
        # Translators: see http://gov.genealogy.net/type/list Type 92
        (KIRCHENGEM92, _("Kirchengemeinde"), "Kirchengemeinde"),
        # Translators: see http://gov.genealogy.net/type/list Type 93
        (REICHSSTADT, _("Reichsstadt"), "Reichsstadt"),
        # Translators: see http://gov.genealogy.net/type/list Type 94
        (VERWALTUNG94, _("Verwaltungsgemeinschaft"),
         "Verwaltungsgemeinschaft"),
        # Translators: see http://gov.genealogy.net/type/list Type 95
        (COUNTYLEVE95, _("County-level city"), "County-level city"),
        # Translators: see http://gov.genealogy.net/type/list Type 96
        (ARCHBISHOP96, _("Archbishopric"), "Archbishopric"),
        # Translators: see http://gov.genealogy.net/type/list Type 97
        (BURGERMEIS97, _("Bürgermeisterei"), "Bürgermeisterei"),
        # Translators: see http://gov.genealogy.net/type/list Type 98
        (VERALTETAM98, _("Veraltet (amtsgericht gebäude)"),
         "Veraltet (amtsgericht gebäude)"),
        # Translators: see http://gov.genealogy.net/type/list Type 99
        (CAPTAINCY, _("Captaincy"), "Captaincy"),
        # Translators: see http://gov.genealogy.net/type/list Type 100
        (KREISHAUPT100, _("Kreishauptmannschaft"), "Kreishauptmannschaft"),
        # Translators: see http://gov.genealogy.net/type/list Type 101
        (KREISDIREK101, _("Kreisdirektion"), "Kreisdirektion"),
        # Translators: see http://gov.genealogy.net/type/list Type 102
        (FORESTERSH102, _("Forester's house"), "Forester's house"),
        # Translators: see http://gov.genealogy.net/type/list Type 103
        (CIVILREGIS103, _("Civil registry"), "Civil registry"),
        # Translators: see http://gov.genealogy.net/type/list Type 104
        (VERALTETST104, _("Veraltet (standesamt (gebäude))"),
         "Veraltet (standesamt (gebäude))"),
        # Translators: see http://gov.genealogy.net/type/list Type 105
        (LANDGERICHT, _("Landgericht"), "Landgericht"),
        # Translators: see http://gov.genealogy.net/type/list Type 107
        (ISLAND, _("Island"), "Island"),
        # Translators: see http://gov.genealogy.net/type/list Type 108
        (GUTSBEZIRK, _("Gutsbezirk"), "Gutsbezirk"),
        # Translators: see http://gov.genealogy.net/type/list Type 109
        (FORSTGUTSB109, _("Forstgutsbezirk"), "Forstgutsbezirk"),
        # Translators: see http://gov.genealogy.net/type/list Type 110
        (DISTRICTOF110, _("District office"), "District office"),
        # Translators: see http://gov.genealogy.net/type/list Type 111
        (SCHLOSS, _("Schloss"), "Schloss"),
        # Translators: see http://gov.genealogy.net/type/list Type 112
        (GESPANSCHAFT, _("Gespanschaft"), "Gespanschaft"),
        # Translators: see http://gov.genealogy.net/type/list Type 113
        (COMITATUS, _("Comitatus"), "Comitatus"),
        # Translators: see http://gov.genealogy.net/type/list Type 114
        (VEST, _("Vest"), "Vest"),
        # Translators: see http://gov.genealogy.net/type/list Type 115
        (FORESTRY, _("Forestry"), "Forestry"),
        # Translators: see http://gov.genealogy.net/type/list Type 116
        (OBERFORSTE116, _("Oberförsterei"), "Oberförsterei"),
        # Translators: see http://gov.genealogy.net/type/list Type 117
        (UNTERFORST117, _("Unterförsterei"), "Unterförsterei"),
        # Translators: see http://gov.genealogy.net/type/list Type 118
        (TRAINSTATION, _("Train station"), "Train station"),
        # Translators: see http://gov.genealogy.net/type/list Type 119
        (STOPSTATION, _("Stop station"), "Stop station"),
        # Translators: see http://gov.genealogy.net/type/list Type 120
        (SETTLEMENT120, _("Settlement"), "Settlement120"),
        # Translators: see http://gov.genealogy.net/type/list Type 121
        (COLONY, _("Colony"), "Colony"),
        # Translators: see http://gov.genealogy.net/type/list Type 122
        (VERBANDSGE122, _("Verbandsgemeinde"), "Verbandsgemeinde"),
        # Translators: see http://gov.genealogy.net/type/list Type 124
        (ABBEY, _("Abbey"), "Abbey"),
        # Translators: see http://gov.genealogy.net/type/list Type 125
        (IMPERIALAB125, _("Imperial abbey"), "Imperial abbey"),
        # Translators: see http://gov.genealogy.net/type/list Type 126
        (SYSSEL, _("Syssel"), "Syssel"),
        # Translators: see http://gov.genealogy.net/type/list Type 127
        (VERWALTUNG127, _("Verwaltungsverband"), "Verwaltungsverband"),
        # Translators: see http://gov.genealogy.net/type/list Type 128
        (LANDGRAFSC128, _("Landgrafschaft"), "Landgrafschaft"),
        # Translators: see http://gov.genealogy.net/type/list Type 129
        (SETTLEMENT, _("Settlement, group of residences"), "Settlement"),
        # Translators: see http://gov.genealogy.net/type/list Type 130
        (STATE, _("State, federal"), "State"),
        # Translators: see http://gov.genealogy.net/type/list Type 131
        (WEICHBILD, _("Weichbild"), "Weichbild"),
        # Translators: see http://gov.genealogy.net/type/list Type 133
        (REGION, _("Region"), "Region"),
        # Translators: see http://gov.genealogy.net/type/list Type 134
        (ARRONDISSE134, _("Arrondissement"), "Arrondissement"),
        # Translators: see http://gov.genealogy.net/type/list Type 135
        (CANTON, _("Canton"), "Canton"),
        # Translators: see http://gov.genealogy.net/type/list Type 136
        (COMMUNE, _("Commune"), "Commune"),
        # Translators: see http://gov.genealogy.net/type/list Type 137
        (REGION137, _("Region, for planning"), "Region137"),
        # Translators: see http://gov.genealogy.net/type/list Type 138
        (OBERLANDRA138, _("Oberlandratsbezirk"), "Oberlandratsbezirk"),
        # Translators: see http://gov.genealogy.net/type/list Type 139
        (EINSCHICHT, _("Einschicht"), "Einschicht"),
        # Translators: see http://gov.genealogy.net/type/list Type 140
        (EINHEITSGE140, _("Einheitsgemeinde"), "Einheitsgemeinde"),
        # Translators: see http://gov.genealogy.net/type/list Type 142
        (REICHSGAU, _("Reichsgau"), "Reichsgau"),
        # Translators: see http://gov.genealogy.net/type/list Type 143
        (KOMMUNE, _("Kommune"), "Kommune"),
        # Translators: see http://gov.genealogy.net/type/list Type 144
        (ORTSCHAFT, _("Ortschaft"), "Ortschaft"),
        # Translators: see http://gov.genealogy.net/type/list Type 145
        (MARKT, _("Markt"), "Markt"),
        # Translators: see http://gov.genealogy.net/type/list Type 146
        (BEZIRKSHAU146, _("Bezirkshauptmannschaft"),
         "Bezirkshauptmannschaft"),
        # Translators: see http://gov.genealogy.net/type/list Type 147
        (VERALTETPO147, _("Veraltet (politischer bezirk)"),
         "Veraltet (politischer bezirk)"),
        # Translators: see http://gov.genealogy.net/type/list Type 148
        (ERFULLENDE148, _("Erfüllende gemeinde"), "Erfüllende gemeinde"),
        # Translators: see http://gov.genealogy.net/type/list Type 149
        (LANDRATSAMT, _("Landratsamt"), "Landratsamt"),
        # Translators: see http://gov.genealogy.net/type/list Type 150
        (CITY, _("City"), "City"),
        # Translators: see http://gov.genealogy.net/type/list Type 151
        (OBERLANDES151, _("Oberlandesgericht"), "Oberlandesgericht"),
        # Translators: see http://gov.genealogy.net/type/list Type 152
        (LANDBURGER152, _("Landbürgermeisterei"), "Landbürgermeisterei"),
        # Translators: see http://gov.genealogy.net/type/list Type 153
        (KOMMISSARIAT, _("Kommissariat"), "Kommissariat"),
        # Translators: see http://gov.genealogy.net/type/list Type 154
        (HONSCHAFT, _("Honschaft"), "Honschaft"),
        # Translators: see http://gov.genealogy.net/type/list Type 155
        (REGION155, _("Region, church"), "Region155"),
        # Translators: see http://gov.genealogy.net/type/list Type 156
        (GEMEINDEBE156, _("Gemeindebezirk"), "Gemeindebezirk"),
        # Translators: see http://gov.genealogy.net/type/list Type 157
        (GUBERNIYA, _("Guberniya"), "Guberniya"),
        # Translators: see http://gov.genealogy.net/type/list Type 158
        (GEMEINDETEIL, _("Gemeindeteil"), "Gemeindeteil"),
        # Translators: see http://gov.genealogy.net/type/list Type 159
        (KHUTOR, _("Khutor"), "Khutor"),
        # Translators: see http://gov.genealogy.net/type/list Type 160
        (SOVIETREPU160, _("Soviet republic"), "Soviet republic"),
        # Translators: see http://gov.genealogy.net/type/list Type 161
        (VERWALTUNG161, _("Verwaltungsbezirk"), "Verwaltungsbezirk"),
        # Translators: see http://gov.genealogy.net/type/list Type 162
        (STADTUNDLA162, _("Stadt- und landgemeinde"),
         "Stadt- und landgemeinde"),
        # Translators: see http://gov.genealogy.net/type/list Type 163
        (ORTSGEMEINDE, _("Ortsgemeinde"), "Ortsgemeinde"),
        # Translators: see http://gov.genealogy.net/type/list Type 164
        (ORTSBEZIRK, _("Ortsbezirk"), "Ortsbezirk"),
        # Translators: see http://gov.genealogy.net/type/list Type 165
        (GNOTSCHAFT, _("Gnotschaft"), "Gnotschaft"),
        # Translators: see http://gov.genealogy.net/type/list Type 166
        (RUINS, _("Ruins"), "Ruins"),
        # Translators: see http://gov.genealogy.net/type/list Type 167
        (MANDATETER167, _("Mandate territory"), "Mandate territory"),
        # Translators: see http://gov.genealogy.net/type/list Type 168
        (PROVINZSCH168, _("Provinz (schwedisch)"), "Provinz (schwedisch)"),
        # Translators: see http://gov.genealogy.net/type/list Type 169
        (GEMEINDESC169, _("Gemeinde (schwedisch)"), "Gemeinde (schwedisch)"),
        # Translators: see http://gov.genealogy.net/type/list Type 170
        (DISTRICT170, _("District"), "District170"),
        # Translators: see http://gov.genealogy.net/type/list Type 171
        (STADTHAUPT171, _("Stadthauptmannschaft"), "Stadthauptmannschaft"),
        # Translators: see http://gov.genealogy.net/type/list Type 172
        (KATASTRALG172, _("Katastralgemeinde"), "Katastralgemeinde"),
        # Translators: see http://gov.genealogy.net/type/list Type 173
        (REICHSKOMM173, _("Reichskommissariat"), "Reichskommissariat"),
        # Translators: see http://gov.genealogy.net/type/list Type 174
        (GENERALDIS174, _("General district"), "General district"),
        # Translators: see http://gov.genealogy.net/type/list Type 175
        (KREISGEBIET, _("Kreisgebiet"), "Kreisgebiet"),
        # Translators: see http://gov.genealogy.net/type/list Type 176
        (PROTECTORATE, _("Protectorate"), "Protectorate"),
        # Translators: see http://gov.genealogy.net/type/list Type 177
        (REICHSRITT177, _("Reichsritterschaft"), "Reichsritterschaft"),
        # Translators: see http://gov.genealogy.net/type/list Type 178
        (RITTERKANTON, _("Ritterkanton"), "Ritterkanton"),
        # Translators: see http://gov.genealogy.net/type/list Type 179
        (RITTERKREIS, _("Ritterkreis"), "Ritterkreis"),
        # Translators: see http://gov.genealogy.net/type/list Type 180
        (MARKTGEMEI180, _("Marktgemeinde"), "Marktgemeinde"),
        # Translators: see http://gov.genealogy.net/type/list Type 181
        (ROTTE, _("Rotte"), "Rotte"),
        # Translators: see http://gov.genealogy.net/type/list Type 182
        (ERZSTIFT, _("Erzstift"), "Erzstift"),
        # Translators: see http://gov.genealogy.net/type/list Type 183
        (HOCHSTIFT, _("Hochstift"), "Hochstift"),
        # Translators: see http://gov.genealogy.net/type/list Type 184
        (KAMMERSCHR184, _("Kammerschreiberei"), "Kammerschreiberei"),
        # Translators: see http://gov.genealogy.net/type/list Type 185
        (KLOSTERAMT, _("Klosteramt"), "Klosteramt"),
        # Translators: see http://gov.genealogy.net/type/list Type 186
        (RENTKAMMER, _("Rentkammer"), "Rentkammer"),
        # Translators: see http://gov.genealogy.net/type/list Type 187
        (ZUUBERPRUFEN, _("Zu überprüfen"), "Zu überprüfen"),
        # Translators: see http://gov.genealogy.net/type/list Type 188
        (RITTERORDEN, _("Ritterorden"), "Ritterorden"),
        # Translators: see http://gov.genealogy.net/type/list Type 189
        (GROSSPRIORAT, _("Großpriorat"), "Großpriorat"),
        # Translators: see http://gov.genealogy.net/type/list Type 190
        (BALLEI, _("Ballei"), "Ballei"),
        # Translators: see http://gov.genealogy.net/type/list Type 191
        (KOMMENDE, _("Kommende"), "Kommende"),
        # Translators: see http://gov.genealogy.net/type/list Type 192
        (ZONEOFOCCU192, _("Zone of occupation"), "Zone of occupation"),
        # Translators: see http://gov.genealogy.net/type/list Type 193
        (ALM, _("Alm"), "Alm"),
        # Translators: see http://gov.genealogy.net/type/list Type 194
        (DISTRIKTSAMT, _("Distrikts-amt"), "Distrikts-amt"),
        # Translators: see http://gov.genealogy.net/type/list Type 195
        (VERALTETBU195, _("Veraltet (bundessozialgericht)"),
         "Veraltet (bundessozialgericht)"),
        # Translators: see http://gov.genealogy.net/type/list Type 196
        (VERALTETLA196, _("Veraltet (landessozialgericht)"),
         "Veraltet (landessozialgericht)"),
        # Translators: see http://gov.genealogy.net/type/list Type 197
        (VERALTETSO197, _("Veraltet (sozialgericht)"),
         "Veraltet (sozialgericht)"),
        # Translators: see http://gov.genealogy.net/type/list Type 198
        (VERALTETFR198, _("Veraltet (früher: bundesverwaltungsgericht)"),
         "Veraltet (früher: bundesverwaltungsgericht)"),
        # Translators: see http://gov.genealogy.net/type/list Type 199
        (VERALTETFR199, _("Veraltet (früher: landesverwaltungsgericht)"),
         "Veraltet (früher: landesverwaltungsgericht)"),
        # Translators: see http://gov.genealogy.net/type/list Type 200
        (VERALTETFR200, _("Veraltet (früher: verwaltungsgericht)"),
         "Veraltet (früher: verwaltungsgericht)"),
        # Translators: see http://gov.genealogy.net/type/list Type 201
        (LANDESKOMM201, _("Landeskommissarbezirk"), "Landeskommissarbezirk"),
        # Translators: see http://gov.genealogy.net/type/list Type 202
        (AMTSGERICH202, _("Amtsgerichtsbezirk"), "Amtsgerichtsbezirk"),
        # Translators: see http://gov.genealogy.net/type/list Type 203
        (DOMANIALAMT, _("Domanialamt"), "Domanialamt"),
        # Translators: see http://gov.genealogy.net/type/list Type 204
        (RITTERSCHA204, _("Ritterschaftliches amt"),
         "Ritterschaftliches amt"),
        # Translators: see http://gov.genealogy.net/type/list Type 205
        (SELSOVIET, _("Selsoviet"), "Selsoviet"),
        # Translators: see http://gov.genealogy.net/type/list Type 206
        (REGIONALKI206, _("Regionalkirchenamt"), "Regionalkirchenamt"),
        # Translators: see http://gov.genealogy.net/type/list Type 207
        (OBERAMTSBE207, _("Oberamtsbezirk"), "Oberamtsbezirk"),
        # Translators: see http://gov.genealogy.net/type/list Type 210
        (KIRCHENBUND, _("Kirchenbund"), "Kirchenbund"),
        # Translators: see http://gov.genealogy.net/type/list Type 211
        (LANDGEBIET, _("Landgebiet"), "Landgebiet"),
        # Translators: see http://gov.genealogy.net/type/list Type 212
        (LANDHERREN212, _("Landherrenschaft"), "Landherrenschaft"),
        # Translators: see http://gov.genealogy.net/type/list Type 213
        (GORSOVIET, _("Gorsoviet"), "Gorsoviet"),
        # Translators: see http://gov.genealogy.net/type/list Type 214
        (REALM, _("Realm"), "Realm"),
        # Translators: see http://gov.genealogy.net/type/list Type 215
        (REICHSHALFTE, _("Reichshälfte"), "Reichshälfte"),
        # Translators: see http://gov.genealogy.net/type/list Type 216
        (LANDESTEIL, _("Landesteil"), "Landesteil"),
        # Translators: see http://gov.genealogy.net/type/list Type 217
        (DIREKTIONS217, _("Direktionsbezirk"), "Direktionsbezirk"),
        # Translators: see http://gov.genealogy.net/type/list Type 218
        (STADTEINHE218, _("City, unitary community"),
         "Stadt (einheitsgemeinde)"),
        # Translators: see http://gov.genealogy.net/type/list Type 219
        (EXPOSITUR, _("Expositur"), "Expositur"),
        # Translators: see http://gov.genealogy.net/type/list Type 221
        (FYLKE, _("Fylke"), "Fylke"),
        # Translators: see http://gov.genealogy.net/type/list Type 222
        (KREISMITTL222, _("Kreis (mittlere verwaltungsebene)"),
         "Kreis (mittlere verwaltungsebene)"),
        # Translators: see http://gov.genealogy.net/type/list Type 223
        (LANDGERICH223, _("Landgericht (älterer ordnung)"),
         "Landgericht (älterer ordnung)"),
        # Translators: see http://gov.genealogy.net/type/list Type 224
        (PFLEGGERICHT, _("Pfleggericht"), "Pfleggericht"),
        # Translators: see http://gov.genealogy.net/type/list Type 225
        (RENTAMTALT225, _("Rentamt (älterer ordnung)"),
         "Rentamt (älterer ordnung)"),
        # Translators: see http://gov.genealogy.net/type/list Type 226
        (OBMANNSCHAFT, _("Obmannschaft"), "Obmannschaft"),
        # Translators: see http://gov.genealogy.net/type/list Type 227
        (KIRCHSPIEL227, _("Kirchspielslandgemeinde"),
         "Kirchspielslandgemeinde"),
        # Translators: see http://gov.genealogy.net/type/list Type 228
        (GERICHTSAMT, _("Gerichtsamt"), "Gerichtsamt"),
        # Translators: see http://gov.genealogy.net/type/list Type 229
        (GROUPOFHOU229, _("Group of houses"), "Group of houses"),
        # Translators: see http://gov.genealogy.net/type/list Type 230
        (SCATTEREDS230, _("Scattered settlement"), "Scattered settlement"),
        # Translators: see http://gov.genealogy.net/type/list Type 231
        (HOFE, _("Höfe"), "Höfe"),
        # Translators: see http://gov.genealogy.net/type/list Type 232
        (RANDORT, _("Randort"), "Randort"),
        # Translators: see http://gov.genealogy.net/type/list Type 233
        (FLECKENSIE233, _("Flecken (siedlung)"), "Flecken (siedlung)"),
        # Translators: see http://gov.genealogy.net/type/list Type 234
        (BOROUGH, _("Borough"), "Borough"),
        # Translators: see http://gov.genealogy.net/type/list Type 235
        (UNITARYAUT235, _("Unitary authority"), "Unitary authority"),
        # Translators: see http://gov.genealogy.net/type/list Type 236
        (HOUSES, _("Houses"), "Houses"),
        # Translators: see http://gov.genealogy.net/type/list Type 237
        (SIEDLUNGSRAT, _("Siedlungsrat"), "Siedlungsrat"),
        # Translators: see http://gov.genealogy.net/type/list Type 238
        (URBANTYPES238, _("Urban-type settlement"), "Urban-type settlement"),
        # Translators: see http://gov.genealogy.net/type/list Type 239
        (VERWALTUNG239, _("Verwaltungsamt"), "Verwaltungsamt"),
        # Translators: see http://gov.genealogy.net/type/list Type 240
        (UYEZD, _("Uyezd"), "Uyezd"),
        # Translators: see http://gov.genealogy.net/type/list Type 241
        (VOLOST, _("Volost"), "Volost"),
        # Translators: see http://gov.genealogy.net/type/list Type 242
        (KATASTERAMT, _("Katasteramt"), "Katasteramt"),
        # Translators: see http://gov.genealogy.net/type/list Type 243
        (PROPSTEI, _("Propstei"), "Propstei"),
        # Translators: see http://gov.genealogy.net/type/list Type 244
        (NEBENKIRCHE, _("Nebenkirche"), "Nebenkirche"),
        # Translators: see http://gov.genealogy.net/type/list Type 245
        (CHAPEL, _("Chapel"), "Chapel"),
        # Translators: see http://gov.genealogy.net/type/list Type 246
        (GROMADA, _("Gromada"), "Gromada"),
        # Translators: see http://gov.genealogy.net/type/list Type 247
        (ORTSTEILVE247, _("Ortsteil (verwaltung)"), "Ortsteil (verwaltung)"),
        # Translators: see http://gov.genealogy.net/type/list Type 248
        (SCHULZENAMT, _("Schulzenamt"), "Schulzenamt"),
        # Translators: see http://gov.genealogy.net/type/list Type 249
        (ERZBISCHOF249, _("Erzbischöfliches amt"), "Erzbischöfliches amt"),
        # Translators: see http://gov.genealogy.net/type/list Type 250
        (APOSTOLISC250, _("Apostolische administratur"),
         "Apostolische administratur"),
        # Translators: see http://gov.genealogy.net/type/list Type 251
        (AUTONOMEGE251, _("Autonome gemeinschaft"), "Autonome gemeinschaft"),
        # Translators: see http://gov.genealogy.net/type/list Type 252
        (LOCALGOVER252, _("Local government"), "Local government"),
        # Translators: see http://gov.genealogy.net/type/list Type 253
        (RELIGIOUSO253, _("Religious organization"),
         "Religious organization"),
        # Translators: see http://gov.genealogy.net/type/list Type 254
        (OKRUG, _("Okrug"), "Okrug"),
        # Translators: see http://gov.genealogy.net/type/list Type 255
        (STADTGUT, _("Stadtgut"), "Stadtgut"),
        # Translators: see http://gov.genealogy.net/type/list Type 256
        (LANDESBEZIRK, _("Landesbezirk"), "Landesbezirk"),
        # Translators: see http://gov.genealogy.net/type/list Type 257
        (LANDGEMEIN257, _("Landgemeinde pl"), "Landgemeinde pl"),
        # Translators: see http://gov.genealogy.net/type/list Type 258
        (STADTGEMEI258, _("Stadtgemeinde (pl)"), "Stadtgemeinde (pl)"),
        # Translators: see http://gov.genealogy.net/type/list Type 259
        (LANDVOGTEI259, _("Landvogteibezirk"), "Landvogteibezirk"),
        # Translators: see http://gov.genealogy.net/type/list Type 260
        (DELEGATURB260, _("Delegaturbezirk"), "Delegaturbezirk"),
        # Translators: see http://gov.genealogy.net/type/list Type 261
        (HOFSCHAFT, _("Hofschaft"), "Hofschaft"),
        # Translators: see http://gov.genealogy.net/type/list Type 262
        (STADTTEILV262, _("Stadtteil (verwaltung)"),
         "Stadtteil (verwaltung)"),
        # Translators: see http://gov.genealogy.net/type/list Type 263
        (SPRENGELOB263, _("Sprengel (obere verwaltung)"),
         "Sprengel (obere verwaltung)"),
        # Translators: see http://gov.genealogy.net/type/list Type 264
        (MAIRIE, _("Mairie"), "Mairie"),
        # Translators: see http://gov.genealogy.net/type/list Type 265
        (SULTANATE, _("Sultanate"), "Sultanate"),
        # Translators: see http://gov.genealogy.net/type/list Type 266
        (LANDRATSBE266, _("Landratsbezirk"), "Landratsbezirk"),
        (STREET, _("Street"), "Street"),
        (LOCALITY, _("Locality"), "Locality"),
        (NUMBER, _("Number"), "Number"),
        (NEIGHBORHOOD, _("Neighborhood"), "Neighborhood"),
        (PARISH, _("Parish"), "Parish"),
        (ADM0, _("ADM0"), "ADM0"),
        (ADM1, _("ADM1"), "ADM1"),
        (ADM2, _("ADM2"), "ADM2"),
        (ADM3, _("ADM3"), "ADM3"),
        (ADM4, _("ADM4"), "ADM4"),
        (ADM5, _("ADM5"), "ADM5"),
        (ADM6, _("ADM6"), "ADM6"),
    ]

    _MENU = [
        (_T_("Common"),
         [UNKNOWN, COUNTRY, STATE, COUNTY, CITY, PARISH,
          LOCALITY, STREET, PROVINCE, REGION, DEPARTMENT, NEIGHBORHOOD,
          DISTRICT, BOROUGH, MUNICIPALITY, TOWN, VILLAGE, HAMLET, FARM,
          BUILDING, NUMBER]),
        (_T_("Administrative"),
         [(_T_("ADM0"),
           [ADM0, CONFEDERAT71, COUNTRY, KINGDOM, PEOPLESREP72, REALM,
            REPUBLIC]),
          (_T_("ADM1"),
           [ADM1, CANTON25, ELECTORATE, FEDERALSTATE, FREESTATE, FYLKE,
            KINGDOM, LANDESBEZIRK, PROVINCE, PROVINZSCH168, REGION,
            REICHSGAU, SOVIETREPU160, STATE, STATE34, UNIONREPUB58,
            VOIVODSHIP]),
          (_T_("ADM2"),
           [ADM2, ADMINISTRA46, DEPARTMENT, DIREKTIONS217, DISTRICT,
            KREISDIREK101, KREISHAUPT100, KREISMITTL222, LANDESKOMM201,
            LANDGEBIET, OBERLANDRA138, PROVINCE, RENTAMTALT225,
            VERWALTUNG161]),
          (_T_("ADM3"),
           [ADM3, AMTADMINIS78, AMTDANISCHES, ARRONDISSE134, BEZIRKSHAU146,
            CAPTAINCY, COUNTY, COUNTYLEVE95, DISTRICTOF110, DOMANIALAMT,
            GUTERDISTR75, JUDET, KLOSTERAMT, LANDGERICH223, LANDHERREN212,
            LANDRATSAMT, OBERAMT, OBERAMTSBE207, RAYON, RENTKAMMER]),
          (_T_("ADM3, cont."),
           [RITTERSCHA204, RURALCOUNT36, STADTHAUPT171, SYSSEL, URBANCOUNT53,
            VERWALTUNG239, VOLOST]),
          (_T_("ADM4"),
           [ADM4, AMTSBEZIRK, AMTVERWALT1, BURGERMEIS97, COUNTYLEVE95,
            LANDBURGER152, LANDRATSBE266, LANDVOGTEI259, MAIRIE, OBMANNSCHAFT,
            PARISH, SAMTGEMEINDE, SELSOVIET, VERBANDSGE122, VERWALTUNG127,
            VERWALTUNG94]),
          (_T_("ADM5"),
           [ADELIGESGUT, ADM5, BAUERSCHAFT, BURGERMEIS97, CITY, COMMUNE,
            COUNTYLEVE95, EINHEITSGE140, ERFULLENDE148, FLECKENGEB14,
            FORSTGUTSB109, GEMEINDESC169, GNOTSCHAFT, GORSOVIET, GROMADA,
            GUTSBEZIRK, HANSEATICC83, HONSCHAFT, KIRCHSPIEL227, KOMMUNE]),
          (_T_("ADM5, cont."),
           [LANDGEMEIN257, MARKT, MARKTGEMEI180, MUNICIPALITY, ORTSGEMEINDE,
            REICHSSTADT, RURALMUNIC85, STADTEINHE218, STADTGEMEI258, STADTGUT,
            STADTUNDLA162]),
          (_T_("ADM6"),
           [ADM6, BOROUGH52, GEMEINDEBE156, GEMEINDETEIL, ORTSBEZIRK,
            ORTSCHAFT, ORTSTEILVE247, ROTTE, SCHULZENAMT, STADTTEILV262]),
          (_T_("General"),
           [AUTONOMEGE251, BAILIWICK, BALLEI, BOROUGH, CANTON, COMITATUS,
            COUNTSHIP, DISTRICT170, DISTRIKTSAMT, DOMINION, DOMKAPITEL82,
            DUCHY, ERZSTIFT, FORESTRY, GENERALDIS174, GESPANSCHAFT,
            GRANDDUCHY, GROSSPRIORAT, GUBERNIYA, HOCHSTIFT, HUNDRED]),
          (_T_("General, cont."),
           [IMPERIALAB125, KAMMERSCHR184, KIRCHSPIEL84, KOMMENDE, KREISGEBIET,
            LANDDROSTEI, LANDESTEIL, LANDGRAFSC128, LANDSCHAFT80,
            LOCALGOVER252, MANDATETER167, MARGRAVATE, MONASTERY, OBERFORSTE116,
            OBLAST, OKRUG, PARTPROVINCE, PFLEGGERICHT, PRINCIPALITY]),
          (_T_("General, cont."),
           [PROTECTORATE, REGION137, REICHSHALFTE, REICHSKOMM173, REICHSKREIS,
            REICHSRITT177, RITTERKANTON, RITTERKREIS, RITTERORDEN,
            SIEDLUNGSRAT, SULTANATE, UNITARYAUT235, UNTERFORST117, UYEZD,
            VEST, WEICHBILD, ZONEOFOCCU192])]),
        (_T_("Civil"),
         [CEMETERY, CIVILREGIS103, ISLAND, KATASTERAMT, KATASTRALG172,
          OBLAST, RUINS]),
        (_T_("Geographical"), [HISTORICAL47, ISLAND]),
        (_T_("Judicial"),
         [AMTSGERICH202, BAILIWICK, GERICHTSAMT, GERICHTSBE19, HONSCHAFT,
          HUNDRED, LANDGERICH223, LANDGERICHT, MAGISTRATE3, OBERLANDES151,
          PFLEGGERICHT, VEST]),
        (_T_("OTHER"),
         [VERALTETAM98, VERALTETBU195, VERALTETFR198, VERALTETFR199,
          VERALTETFR200, VERALTETLA196, VERALTETPO147, VERALTETSO197,
          VERALTETST104, ZUUBERPRUFEN]),
        (_T_("Place"),
         [ALM, BUILDING, CASTLE, COLONY, EINSCHICHT, FARM, FLECKENSIE233,
          FORESTERSH102, GROUPOFHOU229, HAMLET, HAUPTORT, HOFE, HOFSCHAFT,
          HOUSES, KHUTOR, LOCALITY, MANORBUILD21, MILL, MONASTERYB30]),
        (_T_("Place, cont."),
         [NEIGHBORHOOD, PARTOFPLACE, PARTOFTOWN, PFARRDORF, PLACE, RANDORT,
          ROTTE, SCATTEREDS230, SCHLOSS, SETTLEMENT, SETTLEMENT120,
          SOLITUDE, TOWN, TRAINSTATION, URBANTYPES238, VILLAGE, VILLAGE66,
          VORWERK]),
        (_T_("Religious"),
         [ABBEY, APOSTOLISC250, ARCHBISHOP96, BISTUMSREG91, CHAPEL, CHURCH,
          DEANERY, DELEGATURB260, DIOCESE, DIOCESE11, DOMPFARREI,
          ERZBISCHOF249, EXPOSITUR, FILIALCHURCH, KIRCHENBUND, KIRCHENGEM92,
          KIRCHENKREIS, KIRCHENPRO28, KOMMISSARIAT, MONASTERYB30]),
        (_T_("Religious, cont."),
         [NATIONALCH35, NEBENKIRCHE, PARISH29, PARISH42, PFARRKURATIE,
          PFARRREKTO41, PFARRVERBAND, PROPSTEI, REGION155, REGIONALKI206,
          RELIGIOUSO253, SPRENGEL, SPRENGELOB263]),
        (_T_("Transportation"), [STOPSTATION, TRAINSTATION]),
        (_T_("Unpopulated Place"),
         [ABANDONEDP90, CEMETERY, FIELDNAME, RUINS, STOPSTATION])]

    OLD_NEW = {  # translate from old type numbers to new ones
        -1 : UNKNOWN,       # Unknown
        0 : CUSTOM,         # Custom
        1 : COUNTRY,        # Country
        2 : STATE,          # State
        3 : COUNTY,         # County
        4 : CITY,           # City
        5 : PARISH,         # Parish
        6 : LOCALITY,       # Locality
        7 : STREET,         # Street
        8 : PROVINCE,       # Province
        9 : REGION,         # Region
        10 : DEPARTMENT,    # Department
        11 : NEIGHBORHOOD,  # Neighborhood
        12 : DISTRICT,      # District
        13 : BOROUGH,       # Borough
        14 : MUNICIPALITY,  # Municipality
        15 : TOWN,          # Town
        16 : VILLAGE,       # Village
        17 : HAMLET,        # Hamlet
        18 : FARM,          # Farm
        19 : BUILDING,      # Building
        20 : NUMBER,        # Number
    }

    G_ADMIN = 0x400
    G_CIVIL = 0x800
    G_RELI = 0x1000
    G_GEOG = 0x2000
    G_CULT = 0x4000
    G_JUDI = 0x8000
    G_PLACE = 0x20000
    G_TRANS = 0x40000
    G_UNPOP = 0x80000
    G_OTHER = 0x400000
    G_ADM0 = 0x800000
    G_ADM1 = 0x1000000
    G_ADM2 = 0x2000000
    G_ADM3 = 0x4000000
    G_ADM4 = 0x8000000
    G_ADM5 = 0x10000000
    G_ADM6 = 0x20000000

    GROUPMAP = [
        (G_ADMIN, _("Administrative")),
        (G_CIVIL, _("Civil")),
        (G_RELI, _("Religious")),
        (G_GEOG, _("Geographical")),
        (G_CULT, _("Cultural")),
        (G_JUDI, _("Judicial")),
        (G_PLACE, _("Place")),
        (G_TRANS, _("Transportation")),
        (G_UNPOP, _("Unpopulated Place"))
    ]

    def __init__(self, value=None):
        GrampsType.__init__(self, value)

    def __and__(self, other):
        """ other is an int.  This allows the '&' between the PlaceType and
        the PlaceType.G_xxx values for testing group membership. """
        return self.value & other
