# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013       Benny Malengier
# Copyright (C) 2013       Tim G L Lyons
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
Import SrcTemplates for GRAMPS.
"""

from __future__ import print_function

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
import csv
import collections
import sys

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gramps.gen.db import DbTxn
from gramps.gen.utils.id import create_id
from gramps.gen.lib.srcattrtype import *
from gramps.gen.lib.date import Date
from gramps.gen.lib.srctemplate import SrcTemplate, TemplateElement
from gramps.gen.utils.citeref import (REF_TYPE_L, REF_TYPE_S, REF_TYPE_F,
                                      GED_TITLE, GED_AUTHOR, GED_PUBINF,
                                      GED_DATE, GED_PAGE)

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger('.template')

#columns in a csv file defining templates
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

UNKNOWN = 'UNKNOWN'
DESCR = -10


# This contains the default hints and tooltips
DEFAULTS = {
    "Act"  : ("Public Law 12-98" , "A statute or law name passed by a legislature"),
    "Address"  : ("Broadway Avenue, New York" , "Store address information. Set Private if needed! Give information from lowest to highest level separated by comma's"),
    "Affiliation"  : ("Agent of Gramps Software" , "A relevant affiliation that might influence data in the source"),
    "Author"  : ("Doe, D.P. & Cameron, E." , "Give names in following form:'FirstAuthorSurname, Given Names & SecondAuthorSurname, Given Names'. Like this Gramps can parse the name and shorten as needed."),
    "Author location"  : ("Chicago" , "City where author resides or wrote."),
    "Book"  : ("The big example Gramps manual" , "Title of the Book"),
    "Case"  : ("B. Malengier versus N. Hall" , "Dispute between opposing parties in a court of law."),
    "Cemetery"  : ("Greenwich Cemetery Office" , "Name of cemetery or cemetery office with sources."),
    "Chapter"  : ("The first office of T. Rooseveld" , None),
    "Chapter pages"  : ("24-55" , "The pages in the chapter."),
    "Collection"  : ("Bruges Lace Collection" , "The name of the person who compiled the source."),
    "Column"  : ("col. 3" , "The name of the creator of the artifact."),
    "Compiler"  : ("T. Da Silva" , None),
    "Creation date"  : ("13 Aug 1965" , None),
    "Creator"  : ("P. Picasso" , None),
    "Credit line"  : ("Based on unnamed document lost in fire" , "Acknowledgement of writers and contributors"),
    "Date"  : ("17 Sep 1745" , "The range of years which are present in the source."),
    "Date accessed"  : ("18 Jun 2013" , "Some important detail of the source."),
    "Date range"  : ("2003-6" , None),
    "Description"  : ("The lace has inscriptions with names of nobility" , None),
    "District"  : ("Enumeration district (ED) 14" , "District as handled by Census"),
    "Division"  : ("Peterburg Post Office, or Portland, ward 4" , "The subdivision of a larger group that is handled in the source."),
    "Edition"  : ("Second Edition" , None),
    "Editor"  : ("Hoover, J.E." , "The Editor of a multi-author book."),
    "File"  : ("Membership application J. Rapinat" , "The title of a specific file in a source."),
    "File date"  : ("15 Jan 1870" , "Date of submitting the document to a clerk or court."),
    "File location"  : ("Accession 7, Box 3" , "Accession method to the file"),
    "File no."  : ("1243-EB-98" , "Number to indicate a file"),
    "File unit"  : ("Letters to George Washington" , "A grouping unit for a number of files in a source."),
    "Film id"  : ("T345" , "ID of a Microfilm."),
    "Film publication place"  : ("Kansas City" , None),
    "Film publisher"  : ("NY Genealogy Association" , None),
    "Film type"  : ("FHL microfilm" , "The type of the microfilm."),
    "Format"  : ("Digital Images, or Database, or Cards, ..." , "The format of the source."),
    "Frame"  : ("frames 387-432" , "What frames in the source are relevant."),
    "Group"  : ("Miami Patent Office" , "A larger grouping to which the source belongs."),
    "Household"  : ("dwelling 345, family 654" , "Household of interest on a census."),
    "Id"  : ("I50-68, or 1910 U.S. census, or ..." , "ID to identify the source or citation part"),
    "Institution"  : ("Sorbonne University" , "Institution that issued the source."),
    "Interviewer"  : ("Materley, B." , None),
    "Issue date"  : ("Jun 2004" , "Date the source was issued."),
    "Issue range"  : ("145-394, scattered issues" , "A range of magazine, journal, ... issues covered in the source"),
    "Item of interest"  : ("entry for G. Galileo, or Doe Household, or A. Einstein Grave ..." , "Specific part, item, or person of interest in the source"),
    "Jurisdiction"  : ("Jackson County, Alabama" , "Area with a set of laws under the control of a system of courts or government entity. Enter this from lowest to highest relevant jurisdiction, separated by comma's."),
    "Location"  : ("Istanbul" , "City that is relevant."),
    "Number"  : ("2, or Record Group 34, or ..." , "A number."),
    "Number (total)"  : ("5" , "The maximum of entities available."),
    "Original repository"  : ("National Archives" , "Name of the repository where the original is stored."),
    "Original repository location"  : ("Washington, D.C." , "Address or only city of the repository where the original is stored."),
    "Original year"  : ("1966" , "Year the original source was published/created"),
    "Page"  : ("5; or 4,6-8, ..." , "The page or page(s) relevant for the citation"),
    "Page range"  : ("1-13" , "The range of the pages in the source. The page given for a citation must be in this range."),
    "Part"  : ("Part 3" , None),
    "Place created"  : ("London" , None),
    "Position"  : ("written in the left margin, or second row, 3th line" , "Where in or on the source the citation piece can be found."),
    "Posting date"  : ("5 Jul 1799" , None),
    "Professional credentials"  : ("Prof.; or Dr. ..." , None),
    "Provenance"  : ("add provenance of the material" , "Where the material originated from."),
    "Publication format"  : ("CD-ROM or eprint or ..." , None),
    "Publication place"  : ("Berlin" , None),
    "Publication title"  : ("Title of Blog, Newsletter, DVD, ..." , None),
    "Publication year"  : ("2014" , None),
    "Publisher"  : ("Springer" , None),
    "Pub_info"  : ("Springer, Berlin, 2014" , "Publication Information, such as city and year of publication, name of publisher, ..."),
    "Recipient"  : ("J. Ralls" , "The person to who the letter is addressed."),
    "Relationship"  : ("Paul's uncle and brother of Erik" , "The relationship of the author to the person of interest that is the subject."),
    "Report date"  : ("3 May 1999" , "Date the report was written/submitted."),
    "Research comment"  : ("Descriptive detail or provenance or research analysis conclusion, ..." , "Descriptive detail or provenance or research analysis conclusion, ..."),
    "Research project"  : ("Tahiti Natives" , "The genealogical or scientific research project."),
    "Roll"  : ("176, or rolls 145-160" , "The Microfilm role."),
    "Schedule"  : ("population schedule or slave schedule or ..." , "The census schedule (the type of census table) used, eg population schedule or slave schedule. or ..."),
    "Section"  : ("1890 section or ER patients or ..." , "The section or subgroup under which filed, eg 'Diplomatic correspondance, 1798-1810'"),
    "Series"  : ("Carnival County Records" , None),
    "Series no."  : ("series 34-38" , None),
    "Session"  : ("2nd session" , "The number of the meeting or series of connected meetings devoted by a legislature to a single order of business, program, agenda, or announced purpose."),
    "Sheet no."  : ("sheet 13-C" , "Number of a census sheet."),
    "Subject"  : ("D. Copernicus and close family" , None),
    "Subseries" : (None , None),
    "Subtitle"  : ("Subtitle of article or magazine ..." , None),
    "Term"  : ("June Term 1934 or 13th Congress or Reagan Office or ..." , "Reference to the time a person/group/parliament is in office or session."),
    "Timestamp"  : ("min. 34-36" , "Indication of the time in audio or video where the relevant fragment can be found."),
    "Title"  : ("Diary Title, Message Title, Bible Name, Article Title, ..." , None),
    "Translation"  : ("A translated version, typically of the title" , "A translated version, typically of the title"),
    "Type"  : ("Letter" , None),
    "Url (digital location)"  : ("http//gramps-project.org/blog" , "Detailed internet address of the content"),
    "Volume"  : ("4" , None),
    "Volume info"  : ("5 volumes" , "Information about the volumes, eg the amount of volumes."),
    "Website"  : ("gramps-project.org" , "The main internet address."),
    "Website creator/owner"  : ("Family Historians Inc" , "Organization or person behind a website."),
    "Year"  : ("1888" , None),
    "Year accessed"  : ("2013" , None),
            
            }


def load_srctemplates_data(db):
    """
    Loads the srctemplates defined, and returns a dict with template data
    """
    LOG.debug("**** load_srctemplate_data. Starting")
    
    from gramps.gen.plug import BasePluginManager
    bpmgr = BasePluginManager.get_instance()
    pdatas = bpmgr.get_reg_srctemplates()
    
    for plugin in pdatas:
        mod = bpmgr.load_plugin(plugin)
        if mod:
            if mod.input_type == 'csv':
                csvfilename = mod.csvfile
                LOG.debug("**** load_srctemplate_data. Loading csv from %s" % csvfilename)
                if sys.version_info[0] <3:
                    with open(csvfilename, 'rb') as csvfile:
                        load_srctemplate_csv(csvfile, db)
                else:
                    with open(csvfilename, 'r') as csvfile:
                        load_srctemplate_csv(csvfile, db)
                            
                LOG.debug("**** load_srctemplate_data. csv data loaded")
            elif mod.input_type == 'code':
                mod.load_template(db)
                LOG.debug("**** load_srctemplate_data. GEDCOM loaded")

    for handle in db.get_template_handles():
        LOG.debug("handle %s" % handle)
        template = db.get_template_from_handle(handle)
        LOG.debug("source_type: %s; handle %s" % (template.get_name(), template.get_handle()))
        for te in template.get_template_element_list():
            LOG.debug("    name: %s; display: %s; hint: %s; tooltip: %s; citation %s; "
                      "short %s; short_alg %s" %
                      (te.get_name(),
                       te.get_display(), te.get_hint(),
                       te.get_tooltip(), te.get_citation(),
                       te.get_short(), te.get_short_alg()
                      ))
        for target in template.get_map_dict():
            LOG.debug("Type %s; target %s; map %s" %
                      (template.get_name(), target, template.get_map_element(target)))
    LOG.debug("**** load_srctemplate_data. finished")

def load_srctemplate_csv(csvfile, db):
    """
    Loads a template csvfile, and returns a dict with template data
    Note: csvfile could be a list containing strings!
    """
    first = True
    TYPE2CITEMAP = {}
    TYPE2TEMPLATEMAP = {}
    TYPE2FIELDS = collections.defaultdict(lambda: collections.defaultdict(list))
    CITE_TYPES = {'F': REF_TYPE_F, 'L': REF_TYPE_L, 'S': REF_TYPE_S}
    GEDCOMFIELDS = {'A': GED_AUTHOR, 'T': GED_TITLE, 
                'P': GED_PUBINF, 'D': GED_DATE}
    EMPTY = 0
    # template to a shortening algorithm mapping for predefined algorithms
    SHORTERALG_LOC  = 1   # reduce a location to a shorter format (typically city level)
    SHORTERALG_YEAR = 2   # reduce a date to only the year part
    SHORTERALG_ETAL = 3   # reduce an author list to "first author et al."
    SHORTERALG_REVERT_TO_DOT = 4  # change a list of first, second, third to 
                                  # a list third. second. first.
    # template to a style mapping
    STYLE_QUOTE      = 1  # add quotes around the field
    STYLE_QUOTECONT  = 2  # add quotes around this field combined with other
                          # QUOTECONT fields around it
    STYLE_EMPH       = 3  # emphasize field
    STYLE_BOLD       = 4  # make field bold
    SHORTERALG = {'LOC': SHORTERALG_LOC, 'YEAR': SHORTERALG_YEAR,
              'ETAL': SHORTERALG_ETAL, 'REV.': SHORTERALG_REVERT_TO_DOT}
    STYLES = {'Quoted': STYLE_QUOTE, 'Italics': STYLE_EMPH,
          'QuotedCont': STYLE_QUOTECONT, 'Bold': STYLE_BOLD}
    
    reader = csv.reader(csvfile, delimiter=';')
    
    prevtempl = ''
    newtempl = True
    for row in reader:
        if first:
            #skip first row with headers
            first=False
            continue

        if row[CATCOL]:
            cat = row[CATCOL].strip()
            cattype = row[CATTYPECOL].strip()
            types = row[TYPECOL].strip()
            descr = row[DESCRCOL].strip()
            source_type = row[IDENTCOL].strip()
            if prevtempl != source_type:
                newtempl = True
                prevtempl = source_type
            else:
                newtempl = False
            if descr:
                source_descr = '%s - %s - %s (%s)' % (_(cat), _(cattype),
                                        _(types), _(descr))
            else:
                source_descr = '%s - %s - %s' % (_(cat), _(cattype), _(types))
            if source_type in TYPE2TEMPLATEMAP:
                if not TYPE2TEMPLATEMAP[source_type].get_descr() == source_descr:
                    raise NotImplementedError(source_type + ' ' + TYPE2TEMPLATEMAP[source_type].get_descr() + ' NOT equal to known description' + source_descr)
                if newtempl:
                    #the template is new in this csv, but already defined, probably user error
                    raise NotImplementedError('Source template ' + prevtempl + ' is twice defined in the csv.')
            else:
                template = SrcTemplate()
                template.set_name(source_type)
                template.set_descr(source_descr)
                handle = create_id()
                template.set_handle(handle)
                TYPE2TEMPLATEMAP[source_type] = template
#                TYPE2CITEMAP[source_type] = {REF_TYPE_L: [], REF_TYPE_F: [],
#                            REF_TYPE_S: [], DESCR: source_descr}

        if row[CITETYPECOL]:
            #new citation type,
            cite_type_text = row[CITETYPECOL].strip()
            assert cite_type_text in ['F', 'L', 'S'], str(cite_type_text)
            if cite_type_text == 'S':
                shortcite = True
            else:
                shortcite = False
            cite_type = CITE_TYPES[cite_type_text]
        #add field for template to evidence style
        field = row[FIELDCOL].strip()
        field_type = field.replace('[', '').replace(']','').lower().capitalize()
        #field_type = field.replace(' ', '_').replace("'","")\
        #             .replace('&','AND').replace('(', '6').replace(')','9')\
        #             .replace('[', '').replace(']','').replace('/', '_OR_')\
        #             .replace(',', '').replace('.', '').replace(':', '')\
        #             .replace('-', '_')
        
#        #we need to force English SrcAttributeType
#        ifield_type = SrcAttributeType()
#        ifield_type.set_from_xml_str(field_type)
#        ifield_type = int(SrcAttributeType(ifield_type))
#        if ifield_type == SrcAttributeType.CUSTOM:
#            raise NotImplementedError("field must be a known SrcAttributeType, is " + str(SrcAttributeType(field_type)))
#        field_type = ifield_type
        #field_descr =  field.replace('[', '').replace(']','').lower().capitalize()
        field_label = row[LABELCOL].strip()
        #field_label = field_label.replace("'", "\\'")
        private = False
        if  row[PRIVACYCOL].strip():
            private = True
        optional = False
        if  row[OPTCOL].strip():
            optional = True
        shorteralg = SHORTERALG.get(row[SHORTERCOL].strip()) or EMPTY
        gedcom_type_text = row[GEDCOMCOL].strip()
        gedcommap = GEDCOMFIELDS.get(row[GEDCOMCOL].strip()) or EMPTY
        style = STYLES.get(row[STYLECOL].strip()) or EMPTY

        if source_type in TYPE2TEMPLATEMAP:
            template = TYPE2TEMPLATEMAP[source_type]
        else:
            template = SrcTemplate()
            handle = create_id()
            template.set_handle(handle)
            TYPE2TEMPLATEMAP[source_type] = template
            tlist.add_template(handle, template)
        
        if cite_type == REF_TYPE_L or REF_TYPE_F:
            elem = [x for x in template.get_template_element_list()
                        if x.get_name()==field_type and x.get_short()==False]
            if elem:
                te = elem[0]
            else:
                te = TemplateElement()
                template.add_template_element(te)
            hint = row[HINTCOL]
            tooltip = row[TOOLTIPCOL]
            te.set_name(field_type)
            te.set_display(field_label)
            te.set_hint(hint or te.get_hint())
            te.set_tooltip(tooltip or te.get_tooltip())
            te.set_short_alg(shorteralg)
        if cite_type == REF_TYPE_S:
            te = TemplateElement()
            te.set_name(field_type)
            te.set_short_alg(shorteralg)
            te.set_short(True)
            lblval = field_label
            if lblval:
                te.set_display(_('%(normal_version_label)s (Short)') % {
                                    'normal_version_label': lblval})
            template.add_template_element(te)
        TYPE2FIELDS[source_type][cite_type].append(field_type)
        
        # Setup the mapping. A typical mapping would look like:
        # ('EE_Full'  : '%(COMPILER)s, "%(TITLE)s", %(TYPE)s, %(WEBSITE CREATOR/OWNER)s, <i>%(WEBSITE)s</i>, (%(URL (DIGITAL LOCATION))s: accessed %(DATE ACCESSED)s), %(ITEM OF INTEREST)s; %(CREDIT LINE)s.')
        target = "EE_" + cite_type_text
        if te.get_short():
            if field_type.lower().endswith(' (short)'):
                txt = field_type
            else:
                txt = field_type + ' (Short)'
        else:
            txt = field_type
        txt = row[LDELCOL] + "%(" + \
              txt.upper().replace(' ', '_') + \
               ")s" + row[RDELCOL]
        if len(row[RDELCOL]) and row[RDELCOL][-1] in ['.', ',', ':', ';', '-']:
            txt += ' '
        if style == STYLE_QUOTE:
            txt = '"' + txt + '"'
        elif style == STYLE_QUOTECONT:
            if template.get_map_element(target)[-1] == '"':
                template.set_map_element(target, template.get_map_element(target)[:-1])
                txt = txt + '"'
            else:
                txt = '"' + txt + '"'
        elif style == STYLE_EMPH:
            txt = "<i>" + txt + "</i>"
        elif style == STYLE_BOLD:
            txt = "<b>" + txt + "</b>"
        template.set_map_element(target, template.get_map_element(target) + txt)
        
        # Setup the GEDCOM fields. These are only stored in the L template
        if cite_type == REF_TYPE_L and gedcom_type_text:
            target = "GEDCOM_" + gedcom_type_text
            if style == STYLE_QUOTECONT:
                if template.get_map_element(target) and template.get_map_element(target)[-1] == '"':
                    template.set_map_element(target, template.get_map_element(target)[:-1])
            template.set_map_element(target, template.get_map_element(target) + txt)
        
        msg = _("Add template (%s)") % template.get_name()
        with DbTxn(msg, db) as trans:
            db.commit_template(template, trans)
        
    # Now we adjust some fields that could not be changed till all the data had
    # been read in
    for source_type in TYPE2FIELDS:
        template = TYPE2TEMPLATEMAP[source_type]
        # First we determine which are citation fields
        cite_fields = [field for field in 
                            TYPE2FIELDS[source_type][REF_TYPE_F] +
                            TYPE2FIELDS[source_type][REF_TYPE_S]
                       if field not in TYPE2FIELDS[source_type][REF_TYPE_L]]
        for te in template.get_template_element_list():
            # Set the boolean if this is a citation field
            if te.get_name() in cite_fields:
                te.set_citation(True)
            
            # Set the hint and tooltip to default if not already set
            if DEFAULTS.get(te.get_name()):
                te.set_hint(hint or (DEFAULTS[te.get_name()][0] or ""))
                te.set_tooltip(tooltip or (DEFAULTS[te.get_name()][1] or ""))
            else:
                te.set_hint("")
                te.set_tooltip("")
            
            # If this is a short version, set the name accordingly. This could
            # not be done earlier because we needed to keep the old 'non-short'
            # name to find which fields belonged to citations as opposed to
            # sources
            if te.get_short() == True:
                if te.get_name().lower().endswith(' (short)'):
                    te.set_name(te.get_name())
                else:
                    te.set_name(te.get_name() + ' (Short)')
        msg = _("Add template (%s)") % template.get_name()
        with DbTxn(msg, db) as trans:
            db.commit_template(template, trans)
    
    # Finally we setup the GEDCOM page fields
    for source_type in TYPE2FIELDS:
        template = TYPE2TEMPLATEMAP[source_type]
        for te in [x for x in template.get_template_element_list()
                   if x.get_citation() and not x.get_short()]:
            target = "GEDCOM_PAGE"
            template.set_map_element(target,
                            ", ".join((template.get_map_element(target), txt)))
        msg = _("Add template (%s)") % template.get_name()
        with DbTxn(msg, db) as trans:
            db.commit_template(template, trans)
            
    # Proof of concept for CSL mapping
    template = TYPE2TEMPLATEMAP.get('ESM254')
    if template:
        amap = {
                  'type' : 'chapter',
                  'author'  : '%(COMPILER)s',
                  'title'  : '%(TITLE)s',
                  'edition'  : '%(TYPE)s',
                  'container_author'  : '%(WEBSITE_CREATOR/OWNER)s',
                  'container_title'  : '%(WEBSITE)s',
                  'url'  : '%(URL_(DIGITAL_LOCATION))s',
                  'locator'  : '%(ITEM_OF_INTEREST)s; %(CREDIT_LINE)s',
                  'accessed' : '%(DATE_ACCESSED)s',
                  'page' : '1-7'
               }
        for key, val in list(amap.items()):
            template.set_map_element(key, val)
        msg = _("Add template (%s)") % template.get_name()
        with DbTxn(msg, db) as trans:
            db.commit_template(template, trans)

#    for source_type in TYPE2FIELDS:
#        LOG.debug("source_type: %s; handle %s" % (template.get_name(), template.get_handle()))
#        template = TYPE2TEMPLATEMAP[source_type]
#        for te in template.get_template_element_list():
#            LOG.debug("    name: %s; display: %s; hint: %s; tooltip: %s; "
#                      "citation %s; short %s; short_alg %s" %
#                      (te.get_name(),
#                       te.get_display(), te.get_hint(),
#                       te.get_tooltip(), te.get_citation(),
#                       te.get_short(), te.get_short_alg()
#                      ))
#        for target in template.get_map_dict():
#            LOG.debug("Type %s; target %s; map %s" %
#                      (source_type, target, template.get_map_element(target)))
            
        
        
#    LOG.debug(tlist.get_template_list())
#    for handle in tlist.get_template_list():
#        LOG.debug(tlist.get_template_from_handle(handle).to_struct())
