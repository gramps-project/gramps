#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013  Benny Malengier
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
This module parses the evidence csv file and generates the code we need in
Gramps to use the evidence style.
"""

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import csv


#-------------------------------------------------------------------------
#
# Code
#
#-------------------------------------------------------------------------
csvfilename = "evidence_style.csv"
NRCOL = 0
CATCOL = 1
CATTYPECOL = 2
TYPECOL = 3
DESCRCOL= 4
CITETYPECOL = 5
IDENTCOL = 6
LDELCOL = 7  # left delimiter
FIELDCOL = 8
LABELCOL = 9
RDELCOL = 10 # right delimiter
GEDCOMCOL = 11
SHORTERCOL = 12
STYLECOL = 13
PRIVACYCOL = 14
OPTCOL = 15
HINTCOL = 16
TOOLTIPCOL = 17

CITE_TYPES = {'F': 'REF_TYPE_F', 'L': 'REF_TYPE_L', 'S': 'REF_TYPE_S'}
GEDCOMFIELDS = {'A': 'GED_AUTHOR', 'T': 'GED_TITLE', 
                'P': 'GED_PUBINF', 'D': 'GED_DATE'}
SHORTERALG = {'LOC': 'SHORTERALG_LOC', 'YEAR': 'SHORTERALG_YEAR',
              'ETAL': 'SHORTERALG_ETAL', 'REV.': 'SHORTERALG_REVERT_TO_DOT'}
STYLES = {'Quoted': 'STYLE_QUOTE', 'Italics': 'STYLE_EMPH',
          'QuotedCont': 'STYLE_QUOTECONT', 'Bold': 'STYLE_BOLD'}

#already defined srcattrtypes
KNOWN_FIELDS = ['EVEN_REC', 'EVEN_CITED', 'EVEN_ROLE', 'GEN_BY', 'REPOSITORY',
        'REPOSITORY_ADDRESS', 'REPOSITORY_SHORT_VERSION', 'REPOSITORY_CALL_NUMBER',
        'DATE']

DEFAULT_HINTS = {
    "ACT": "Public Law 12-98",
    "ADDRESS": "Broadway Avenue, New York",
    "AFFILIATION": "Agent of Gramps Software",
    "AUTHOR": "Doe, D.P. & Cameron, E.",
    "AUTHOR_LOCATION": "Chicago",
    "BOOK": "The big example Gramps manual",
    "CASE": "B. Malengier versus N. Hall",
    "CEMETERY": "Greenwich Cemetery Office",
    "CHAPTER": "The first office of T. Rooseveld",
    "CHAPTER_PAGES": "24-55",
    "COLLECTION": "Bruges Lace Collection",
    "COLUMN": "col. 3",
    "COMPILER": "T. Da Silva",
    "CREATION_DATE": "13 Aug 1965",
    "CREATOR": "P. Picasso",
    "CREDIT_LINE": "Based on unnamed document lost in fire",
    "DATE": "17 Sep 1745",
    "DATE_ACCESSED": "18 Jun 2013",
    "DATE_RANGE": "2003-6",
    "DESCRIPTION": "The lace has inscriptions with names of nobility",
    "DISTRICT": "Enumeration district (ED) 14",
    "DIVISION": "Peterburg Post Office, or Portland, ward 4",
    "EDITION": "Second Edition",
    "EDITOR": "Hoover, J.E.",
    "FILE": "Membership application J. Rapinat",
    "FILE_DATE": "15 Jan 1870",
    "FILE_LOCATION": "Accession 7, Box 3",
    "FILE_NO": "1243-EB-98",
    "FILE_UNIT": "Letters to George Washington",
    "FILM_ID": "T345",
    "FILM_PUBLICATION_PLACE": "Kansas City",
    "FILM_PUBLISHER": "NY Genealogy Association",
    "FILM_TYPE": "FHL microfilm",
    "FORMAT": "Digital Images, or Database, or Cards, ...",
    "FRAME": "frames 387-432",
    "GROUP": "Miami Patent Office",
    "HOUSEHOLD": "dwelling 345, family 654",
    "ID": "I50-68, or 1910 U.S. census, or ...",
    "INSTITUTION": "Sorbonne University",
    "INTERVIEWER": "Materley, B.",
    "ISSUE_DATE": "Jun 2004",
    "ISSUE_RANGE": "145-394, scattered issues",
    "ITEM_OF_INTEREST": "entry for G. Galileo, or Doe Household, or A. Einstein Grave ...",
    "JURISDICTION": "Jackson County, Alabama",
    "LOCATION": "Istanbul",
    "NUMBER": "2, or Record Group 34, or ...",
    "NUMBER_6TOTAL9": "5",
    "ORIGINAL_REPOSITORY": "National Archives",
    "ORIGINAL_REPOSITORY_LOCATION": "Washington, D.C.",
    "ORIGINAL_YEAR": "1966",
    "PAGE": "5; or 4,6-8, ...",
    "PAGE_RANGE": "1-13",
    "PART": "Part 3",
    "PLACE_CREATED": "London",
    "POSITION": "written in the left margin, or second row, 3th line",
    "POSTING_DATE": "5 Jul 1799",
    "PROFESSIONAL_CREDENTIALS": "Prof.; or Dr. ...",
    "PROVENANCE": "add provenance of the material",
    "PUBLICATION_FORMAT": "CD-ROM or eprint or ...",
    "PUBLICATION_PLACE": "Berlin",
    "PUBLICATION_TITLE": "Title of Blog, Newsletter, DVD, ...",
    "PUBLICATION_YEAR": "2014",
    "PUBLISHER": "Springer",
    "PUB_INFO": "Springer, Berlin, 2014",
    "RECIPIENT": "J. Ralls",
    "RELATIONSHIP": "Paul's uncle and brother of Erik",
    "REPORT_DATE": "3 May 1999",
    "RESEARCH_COMMENT": "Descriptive detail or provenance or research analysis conclusion, ...",
    "RESEARCH_PROJECT": "Tahiti Natives",
    "ROLL": "176, or rolls 145-160",
    "SCHEDULE": "population schedule or slave schedule or ...",
    "SECTION": "1890 section or ER patients or ...",
    "SERIES": "Carnival County Records",
    "SERIES_NO": "series 34-38",
    "SESSION": "2nd session",
    "SHEET_NO": "sheet 13-C",
    "SUBJECT": "D. Copernicus and close family",
    "SUBSERIES": "",
    "SUBTITLE": "Subtitle of article or magazine ...",
    "TERM": "June Term 1934 or 13th Congress or Reagan Office or ...",
    "TIMESTAMP": "min. 34-36",
    "TITLE": "Diary Title, Message Title, Bible Name, Article Title, ...",
    "TRANSLATION": "A translated version, typically of the title",
    "TYPE": "Letter",
    "URL_6DIGITAL_LOCATION9": "http://gramps-project.org/blog",
    "VOLUME": "4",
    "VOLUME_INFO": "5 volumes",
    "WEBSITE": "gramps-project.org",
    "WEBSITE_CREATOR_OR_OWNER": "Family Historians Inc",
    "YEAR": "1888",
    "YEAR_ACCESSED": "2013",
}

DEFAULT_TOOLTIPS = {
    "ACT": "A statute or law name passed by a legislature",
    "ADDRESS": "Store address information. Set Private if needed! Give"
        " information from lowest to highest level separated by comma's",
    "AFFILIATION": "A relevant affiliation that might influence data in the source",
    "AUTHOR": "Give names in following form: 'FirstAuthorSurname, Given Names & SecondAuthorSurname, Given Names'."
            " Like this Gramps can parse the name and shorten as needed.",
    "AUTHOR_LOCATION": "City where author resides or wrote.",
    "BOOK": "Title of the Book",
    "CASE": "Dispute between opposing parties in a court of law.",
    "CEMETERY": "Name of cemetery or cemetery office with sources.",
    "CHAPTER": "",
    "CHAPTER_PAGES": "The pages in the chapter.",
    "COLLECTION": "",
    "COLUMN": "",
    "COMPILER": "The name of the person who compiled the source.",
    "CREATION_DATE": "",
    "CREATOR": "The name of the creator of the artifact.",
    "CREDIT_LINE": "Acknowledgement of writers and contributors",
    "DATE": "",
    "DATE_ACCESSED": "",
    "DATE_RANGE": "The range of years which are present in the source.",
    "DESCRIPTION": "Some important detail of the source.",
    "DISTRICT": "District as handled by Census",
    "DIVISION": "The subdivision of a larger group that is handled in the source.",
    "EDITION": "",
    "EDITOR": "The Editor of a multi-author book.",
    "FILE": "The title of a specific file in a source.",
    "FILE_DATE": "Date of submitting the document to a clerk or court.",
    "FILE_LOCATION": "Accession method to the file",
    "FILE_NO": "Number to indicate a file",
    "FILE_UNIT": "A grouping unit for a number of files in a source.",
    "FILM_ID": "ID of a Microfilm.",
    "FILM_PUBLICATION_PLACE": "",
    "FILM_PUBLISHER": "",
    "FILM_TYPE": "The type of the microfilm.",
    "FORMAT": "The format of the source.",
    "FRAME": "What frames in the source are relevant.",
    "GROUP": "A larger grouping to which the source belongs.",
    "HOUSEHOLD": "Household of interest on a census.",
    "ID": "ID to identify the source or citation part",
    "INSTITUTION": "Institution that issued the source.",
    "INTERVIEWER": "",
    "ISSUE_DATE": "Date the source was issued.",
    "ISSUE_RANGE": "A range of magazine, journal, ... issues covered in the source",
    "ITEM_OF_INTEREST": "Specific part, item, or person of interest in the source",
    "JURISDICTION": "Area with a set of laws under the control of a system of courts or government entity."
            " Enter this from lowest to highest relevant jurisdiction, separated by comma's.",
    "LOCATION": "City that is relevant.",
    "NUMBER": "A number.",
    "NUMBER_6TOTAL9": "The maximum of entities available.",
    "ORIGINAL_REPOSITORY": "Name of the repository where the original is stored.",
    "ORIGINAL_REPOSITORY_LOCATION": "Address or only city of the repository where the original is stored.",
    "ORIGINAL_YEAR": "Year the original source was published/created",
    "PAGE": "The page or page(s) relevant for the citation",
    "PAGE_RANGE": "The range of the pages in the source. The page given for"
            " a citation must be in this range.",
    "PART": "",
    "PLACE_CREATED": "",
    "POSITION": "Where in or on the source the citation piece can be found.",
    "POSTING_DATE": "",
    "PROFESSIONAL_CREDENTIALS": "",
    "PROVENANCE": "Where the material originated from.",
    "PUBLICATION_FORMAT": "",
    "PUBLICATION_PLACE": "",
    "PUBLICATION_TITLE": "",
    "PUBLICATION_YEAR": "",
    "PUBLISHER": "",
    "PUB_INFO": "Publication Information, such as city and year of publication, name of publisher, ...",
    "RECIPIENT": "The person to who the letter is addressed.",
    "RELATIONSHIP": "The relationship of the author to the person of interest that is the subject.",
    "REPORT_DATE": "Date the report was written/submitted.",
    "RESEARCH_COMMENT": "Descriptive detail or provenance or research analysis conclusion, ...",
    "RESEARCH_PROJECT": "The genealogical or scientific research project.",
    "ROLL": "The Microfilm role.",
    "SCHEDULE": "The census schedule (the type of census table) used, eg population schedule or slave schedule. or ...",
    "SECTION": "The section or subgroup under which filed, eg 'Diplomatic correspondance, 1798-1810'",
    "SERIES": "",
    "SERIES_NO": "",
    "SESSION": "The number of the meeting or series of connected meetings devoted "
        "by a legislature to a single order of business, program, agenda, or announced purpose.",
    "SHEET_NO": "Number of a census sheet.",
    "SUBJECT": "",
    "SUBSERIES": "",
    "SUBTITLE": "",
    "TERM": "Reference to the time a person/group/parliament is in office or session.",
    "TIMESTAMP": "Indication of the time in audio or video where the relevant fragment can be found.",
    "TITLE": "",
    "TRANSLATION": "A translated version, typically of the title",
    "TYPE": "",
    "URL_6DIGITAL_LOCATION9": "Detailed internet address of the content",
    "VOLUME": "",
    "VOLUME_INFO": "Information about the volumes, eg the amount of volumes.",
    "WEBSITE": "The main internet address.",
    "WEBSITE_CREATOR_OR_OWNER": "Organization or person behind a website.",
    "YEAR": "",
    "YEAR_ACCESSED": "",
}


nr = -1
cat = ''
cattype = ''
type = ''
descr = ''
cite_type = ''
ident = ''

TYPE2CITEMAP = {}
FIELDTYPEMAP = {}
FIELDS_SHORT = []
index = 100
indexval = 10
first = True

with open(csvfilename, 'rb') as csvfile:
   reader = csv.reader(csvfile, delimiter=';')
   for row in reader:
        if first:
            #skip first row with headers
            first=False
            continue

        if row[CATCOL]:
            cat = row[CATCOL].strip()
            if cat.startswith('EE '):
                cat = cat[3:]
                EE = True
            else:
                EE = False
            cattype = row[CATTYPECOL].strip()
            types = row[TYPECOL].strip()
            descr = row[DESCRCOL].strip()
            source_type = row[IDENTCOL].strip()
            if descr:
                source_descr = '%s - %s - %s (%s)' % (cat, cattype, types, descr)
                if not EE:
                    source_descr_code = "_('%(first)s - %(sec)s - %(third)s (%(fourth)s)') % { "\
                        " 'first': _('" + cat + "'),"\
                        " 'sec': _('" + cattype + "'),"\
                        " 'third': _('" + types + "'),"\
                        " 'fourth': _('" + descr + "')}"
                else:
                    source_descr_code = "_('EE %(first)s - %(sec)s - %(third)s (%(fourth)s)') % { "\
                        " 'first': _('" + cat + "'),"\
                        " 'sec': _('" + cattype + "'),"\
                        " 'third': _('" + types + "'),"\
                        " 'fourth': _('" + descr + "')}"
            else:
                source_descr = '%s - %s - %s' % (cat, cattype, types)
                if not EE:
                    source_descr_code = "_('%(first)s - %(sec)s - %(third)s') % { "\
                        " 'first': _('" + cat + "'),"\
                        " 'sec': _('" + cattype + "'),"\
                        " 'third': _('" + types + "')}"
                else:
                    source_descr_code = "_('EE %(first)s - %(sec)s - %(third)s') % { "\
                        " 'first': _('" + cat + "'),"\
                        " 'sec': _('" + cattype + "'),"\
                        " 'third': _('" + types + "')}"
            if source_type in TYPE2CITEMAP:
                assert TYPE2CITEMAP[source_type] ['descr'] == source_descr, source_type + ' ' + TYPE2CITEMAP[source_type] ['descr'] + ' NOT ' + source_descr
            else:
                TYPE2CITEMAP[source_type] = {'REF_TYPE_L': [], 'REF_TYPE_F': [],
                            'REF_TYPE_S': [], 
                            'i': indexval, 'descr': source_descr,
                            'descrcode': source_descr_code}
                indexval += 1
            
        if row[CITETYPECOL]:
            #new citation type,
            cite_type = row[CITETYPECOL].strip()
            if cite_type == 'S':
                shortcite = True
            else:
                shortcite = False
            cite_type = CITE_TYPES[cite_type]
        #add field for template to evidence style
        field = row[FIELDCOL].strip()
        field_type = field.replace(' ', '_').replace("'","")\
                     .replace('&','AND').replace('(', '6').replace(')','9')\
                     .replace('[', '').replace(']','').replace('/', '_OR_')\
                     .replace(',', '').replace('.', '').replace(':', '')\
                     .replace('-', '_')
        field_descr =  field.replace('[', '').replace(']','').lower().capitalize()
        field_label = row[LABELCOL].strip()
        field_label = field_label.replace("'", "\\'")
        if field_type in FIELDTYPEMAP:
            assert field_descr == FIELDTYPEMAP[field_type][1], 'Problem %s %s %s' % (field_type, field_descr, FIELDTYPEMAP[field_type][1])
        elif field_type in KNOWN_FIELDS:
            #no need to add it
            pass
        else:
            FIELDTYPEMAP[field_type] = (index, field_descr)
            index += 1
        fielddata = []
        private = 'False'
        if  row[PRIVACYCOL].strip():
            private = 'True'
        optional = 'False'
        if  row[OPTCOL].strip():
            optional = 'True'
        shorteralg = SHORTERALG.get(row[SHORTERCOL].strip()) or 'EMPTY'
        gedcommap = GEDCOMFIELDS.get(row[GEDCOMCOL].strip()) or 'EMPTY'
        style = STYLES.get(row[STYLECOL].strip()) or 'EMPTY'
        hint = row[HINTCOL]
        tooltip = row[TOOLTIPCOL]
        
        TYPE2CITEMAP[source_type][cite_type] += [(row[LDELCOL], field_type, 
                        row[RDELCOL], field_label, style, private, optional, 
                        shorteralg, gedcommap, hint, tooltip)]
        #if shorttype, we store a type for the short version so user can store
        #this
        if shortcite and shorteralg == 'EMPTY':
            field_type_short = field_type + '_SHORT_VERSION'
            if field_type_short in FIELDTYPEMAP or field_type_short in KNOWN_FIELDS:
                pass
            else:
                FIELDTYPEMAP[field_type_short] = (index, field_descr + ' (Short)')
                FIELDS_SHORT.append(field_type_short)
                index += 1

#now generate the python code we need in source attr types
code = "    #following fields are generated with evidencefieldgenerator.py\n" \
       "    #the index starts at 100!\n"
datamap = "\n    _DATAMAP += [\n"
allkeys = sorted(FIELDTYPEMAP.keys())
for field_type in allkeys:
    code += "    " + field_type + ' = %d\n' % FIELDTYPEMAP[field_type][0]
    datamap += '        (' + field_type + ', _("' + FIELDTYPEMAP[field_type][1] \
            +'"), "' + FIELDTYPEMAP[field_type][1] + '"),\n'
code += "\n    _DATAMAPIGNORE = [\n" 
for field in FIELDS_SHORT:
    code += "        " + field + ',\n'
code += '    ]\n\n' + datamap + '        ]\n'

#now add default hints
code += "\n    _DEFAULT_HINTS = {\n"
for key in sorted(DEFAULT_HINTS.keys()):
    if DEFAULT_HINTS[key]:
        code += "        " + key +': _("' +  DEFAULT_HINTS[key] + '"),\n'
code += "    }\n"
#now add default tooltips
code += "\n    _DEFAULT_TOOLTIPS = {\n"
for key in sorted(DEFAULT_TOOLTIPS.keys()):
    if DEFAULT_TOOLTIPS[key]:
        code += "        " + key + ': _("' +  DEFAULT_TOOLTIPS[key] + '"),\n'
code += "    }\n"

with open('srcattrtype_extra.py', 'wb') as srcattrfile:
    srcattrfile.write(code)

#now generate the python code we need in evidencestyle
# we have predefined sourcetypes, and these have a template for formatting
# 

#first an English to internationalized map
code = "    #SRCTEMPLATE has some predefined values which map to citation styles\n"

datamap = "    _SRCTEMPLATEVAL_MAP = [\n"\
        "        (UNKNOWN, _('Unknown'), 'Unknown'),\n"
allkeys = sorted(TYPE2CITEMAP.keys())
for source_type in allkeys:
    code += "    " + source_type + ' = %d\n' % TYPE2CITEMAP[source_type]['i']
    # we use descrcode in to translate string to reduce work for translators
    datamap += "        (" + source_type + ", " + TYPE2CITEMAP[source_type]['descrcode'] \
            +", '" + source_type+ "'),\n"

code += '\n    # Localization of the different source types\n'\
            + datamap + '        ]\n'

code += "\n    #templates for the source types defined\n"\
        "    # F: Full reference\n"\
        "    # S: Short reference (if F used once, use S afterwards)\n" \
        "    # L: List reference (for in bibliography list)\n"
code += '    EVIDENCETEMPLATES = {\n'
for source_type in allkeys:
    code += "        " + source_type + ": {\n"
    for val in ['REF_TYPE_L', 'REF_TYPE_F', 'REF_TYPE_S']:
        code += "            " + val + ": [\n"
        for field in TYPE2CITEMAP[source_type][val]:
            # field is tuple (row[LDELCOL], field_type, row[RDELCOL], 
            # field_label, row[STYLECOL]
            #    , private, optional, shorteralg, gedcommap, hint, tooltip)
            if field[9]:
                hint = '_("' + field[9] + '")'
            else:
                hint = 'None'
            if field[10]:
                tooltip = '_("' + field[10] + '")'
            else:
                tooltip = 'None'
            code += "                ('"+ field[0] + "', SrcAttributeType." + field[1]  + ", _('"\
                    +field[3] + "'), '"+ field[2] + "', " + field[4] + ", " + field[5] + ", "\
                    + field[6] + ", " + field[7] + ", " + field[8] + ",\n" \
                    + "                " +hint + ", " + tooltip + "),\n"
        code += "                ],\n"
    code += "        },\n"
code += "    }\n"

with open('srcattrtype_extraevidence.py', 'wb') as srcattrfile:
    srcattrfile.write(code)