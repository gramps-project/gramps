# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013       Benny Malengier
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
SrcTemplate class for GRAMPS.
"""

from __future__ import print_function

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
import csv

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from .srcattrtype import *
from .date import Date

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

# the GEDCOM type is predefined and always present. Other templates will be
# loaded via plugins
EVIDENCETEMPLATES = {
        'GEDCOM': {
            REF_TYPE_L: [
                ('', SrcAttributeType.AUTHOR, _(''), '.', EMPTY, False, False, EMPTY, GED_AUTHOR,
                None, None),
                ('', SrcAttributeType.TITLE, _(''), '.', STYLE_QUOTE, False, False, EMPTY, GED_TITLE,
                None, None),
                ('', SrcAttributeType.PUB_INFO, _(''), '', EMPTY, False, False, EMPTY, GED_PUBINF,
                None, None),
                ],
            REF_TYPE_F: [
                ('', SrcAttributeType.AUTHOR, _(''), ',', EMPTY, False, False, EMPTY, EMPTY,
                None, None),
                ('', SrcAttributeType.TITLE, _(''), ',', STYLE_QUOTE, False, False, EMPTY, EMPTY,
                None, None),
                ('', SrcAttributeType.PUB_INFO, _(''), '.', EMPTY, False, False, EMPTY, EMPTY,
                None, None),
                ('', SrcAttributeType.DATE, _(''), ' -', EMPTY, False, False, EMPTY, EMPTY,
                None, None),
                ('', SrcAttributeType.PAGE, _('Page(s)'), '.', EMPTY, False, False, EMPTY, EMPTY,
                None, None),
                ],
            REF_TYPE_S: [
                ('', SrcAttributeType.AUTHOR, _(''), ',', EMPTY, False, False, EMPTY, EMPTY,
                None, None),
                ('', SrcAttributeType.DATE, _(''), ' -', EMPTY, False, False, EMPTY, EMPTY,
                None, None),
                ('', SrcAttributeType.PAGE, _('Page(s)'), '.', EMPTY, False, False, EMPTY, EMPTY,
                None, None),
                ],
            DESCR: '%(first)s - %(sec)s - %(third)s' % {  'first': _('Basic'), 'sec': _('GEDCOM Style'), 'third': _('')},
            },
        UNKNOWN: {
            REF_TYPE_L: [
                ],
            REF_TYPE_F: [
                ],
            REF_TYPE_S: [
                ],
            DESCR: _("Unrecognized Template. Download it's definition."),
            },
        }

def load_srctemplates_data():
    """
    Loads the srctemplates defined, and returns a dict with template data
    """
    from gramps.gen.plug import BasePluginManager
    bpmgr = BasePluginManager.get_instance()
    pdatas = bpmgr.get_reg_srctemplates()
    templatemap = {}
    
    for plugin in pdatas:
        mod = bpmgr.load_plugin(plugin)
        if mod:
            csvfilename = mod.csvfile
            with open(csvfilename, 'rb') as csvfile:
                templatemap.update(load_srctemplate_csv(csvfile))
    return templatemap

def load_srctemplate_csv(csvfile):
    """
    Loads a template csvfile, and returns a dict with template data
    Note: csvfile could be a list containing strings!
    """
    first = True
    TYPE2CITEMAP = {}
    CITE_TYPES = {'F': REF_TYPE_F, 'L': REF_TYPE_L, 'S': REF_TYPE_S}
    GEDCOMFIELDS = {'A': GED_AUTHOR, 'T': GED_TITLE, 
                'P': GED_PUBINF, 'D': GED_DATE}
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
            if source_type in TYPE2CITEMAP:
                if not TYPE2CITEMAP[source_type] [DESCR] == source_descr:
                    raise NotImplementedError, source_type + ' ' + TYPE2CITEMAP[source_type] [DESCR] + ' NOT equal to known description' + source_descr
                if newtempl:
                    #the template is new in this csv, but already defined, probably user error
                    raise NotImplementedError, 'Source template ' + prevtempl + ' is twice defined in the csv.'
            else:
                TYPE2CITEMAP[source_type] = {REF_TYPE_L: [], REF_TYPE_F: [],
                            REF_TYPE_S: [], DESCR: source_descr}

        if row[CITETYPECOL]:
            #new citation type,
            cite_type = row[CITETYPECOL].strip()
            assert cite_type in ['F', 'L', 'S'], str(cite_type)
            if cite_type == 'S':
                shortcite = True
            else:
                shortcite = False
            cite_type = CITE_TYPES[cite_type]
        #add field for template to evidence style
        field = row[FIELDCOL].strip()
        field_type = field.replace('[', '').replace(']','').lower().capitalize()
        #field_type = field.replace(' ', '_').replace("'","")\
        #             .replace('&','AND').replace('(', '6').replace(')','9')\
        #             .replace('[', '').replace(']','').replace('/', '_OR_')\
        #             .replace(',', '').replace('.', '').replace(':', '')\
        #             .replace('-', '_')
        field_type = int(SrcAttributeType(field_type))
        if field_type == SrcAttributeType.CUSTOM:
            raise NotImplementedError, "field must be a known SrcAttributeType"
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
        gedcommap = GEDCOMFIELDS.get(row[GEDCOMCOL].strip()) or EMPTY
        style = STYLES.get(row[STYLECOL].strip()) or EMPTY
        hint = row[HINTCOL]
        tooltip = row[TOOLTIPCOL]

        TYPE2CITEMAP[source_type][cite_type] += [(row[LDELCOL], field_type, 
                        _(field_label), row[RDELCOL], style, private, optional, 
                        shorteralg, gedcommap, _(hint), _(tooltip))]
    return TYPE2CITEMAP

#-------------------------------------------------------------------------
#
#  SrcTemplate class
#
#-------------------------------------------------------------------------

class SrcTemplate(object):
    """
    Sources conform to a certain template, which governs their styling when 
    used in reports.
    
    The SrcTemplate object holds all the logic to do the actual styling.
    Predefined templates themself are stored in SrcAttributeType, or in extra 
    xml files with defenitions

    The structure typically is a dictionary as follows:
        
        {
            REF_TYPE_L: [
                ('', AUTHOR, '.', EMPTY, False, False, EMPTY, GED_AUTHOR, 'hint', 'tooltip'),
                ('', TITLE, '.', STYLE_QUOTE, False, False, EMPTY, GED_TITLE, '', ''),
                ('', PUB_INFO, '', EMPTY, False, False, EMPTY, GED_PUBINF, '', ''),
                ],
            REF_TYPE_F: [
                ('', AUTHOR, ',', EMPTY, False, False, EMPTY, EMPTY, '', ''),
                ('', TITLE, ',', STYLE_QUOTE, False, False, EMPTY, EMPTY, '', ''),
                ('', PUB_INFO, '.', EMPTY, False, False, EMPTY, EMPTY, '', ''),
                ('', DATE, ' -', EMPTY, False, False, EMPTY, EMPTY, '', ''),
                ('', PAGE6S9, '.', EMPTY, False, False, EMPTY, EMPTY, '', ''),
                ],
            REF_TYPE_S: [
                ('', AUTHOR, ',', EMPTY, False, False, EMPTY, EMPTY, '', ''),
                ('', DATE, ' -', EMPTY, False, False, EMPTY, EMPTY, '', ''),
                ('', PAGE6S9, '.', EMPTY, False, False, EMPTY, EMPTY, '', ''),
                ],
        }
        
        This defines the 3 source reference types. A reference type consists of
        a list of tuples with fieldsdescriptions.
        A fielddescription consists of the columns:
        0/ left delimiter
        1/ field, this is a SrcAttributeType
        2/ right delimiter
        3/ style to use
        4/ bool: if field should be private by default on creation
        5/ bool: if optional field
        6/ shortening algorithm to use, EMPTY indicates no transformation
        7/ the REF_TYPE_L reference maps to GEDCOM fields on export via
           this column. GEDCOM contains Title, Author and Pub.Info field
    """
    #on import, only default values present, plugins must still be loaded
    MAP_LOADED = False
    
    UNKNOWN = UNKNOWN
    
    def __init__(self, template_key=None):
        """
        Initialize the template from a given key.
        If key is an integer, EVIDENCETEMPLATES is used of SrtAttrType. 
        If Key is string, it is first searched as the Key of EVIDENCETEMPLATES,
        otherwise from xml templates (not implemented yet !!)
        """
        SrcTemplate.check_loaded()
        if template_key is None:
            template_key = UNKNOWN
        self.set_template_key(template_key)
 
    @staticmethod
    def check_loaded():
        """ we load first the map if needed
        """
        if not SrcTemplate.MAP_LOADED:
            EVIDENCETEMPLATES.update(load_srctemplates_data())
            SrcTemplate.MAP_LOADED = True
            
    @staticmethod
    def get_templatevalue_default():
        return 'GEDCOM'

    @staticmethod
    def template_defined(template_key):
        """
        Return True if the given key is known, False otherwise
        """
        SrcTemplate.check_loaded()
        return template_key in EVIDENCETEMPLATES

    @staticmethod
    def all_templates():
        SrcTemplate.check_loaded()
        return [x for x in EVIDENCETEMPLATES.keys()]

    @staticmethod
    def template_description(template_key):
        """
        Return True if the given key is known, False otherwise
        """
        SrcTemplate.check_loaded()
        return EVIDENCETEMPLATES[template_key][DESCR]

    @staticmethod
    def get_template(template_key):
        """
        Return True if the given key is known, False otherwise
        """
        SrcTemplate.check_loaded()
        return EVIDENCETEMPLATES[template_key]

    def empty(self):
        """
        remove all computed data
        """
        self.refL = None
        self.refF = None
        self.refS = None
        # attrmap will hold mapping of field to normal value and short value
        # short value will be None if not given
        # map is field -> (normal value for ref L, 
        #                  normal value for ref F/S, short value ref S)
        self.attrmap = {}

    def get_template_key(self):
        """
        Obtain the current template key used
        """
        return self.template_key

    def set_template_key(self, template_key):
        """
        Change to the new template key for reference styling
        """
        self.empty()
        if template_key == UNKNOWN:
            #for key unknown we use styling according to GEDCOM
            template_key = 'GEDCOM'
            
        try:
            self.tempstruct = EVIDENCETEMPLATES[template_key]
        except:
            print 
            raise NotImplementedError, 'SrcTemplate: Keyerror "' \
                    + str(template_key) \
                    + '", custom templates templates not implemented!'
        self.template_key = template_key

    def set_attr_list(self, attr_list, attr_list_citation=None, date_citation=None):
        """
        Set the attribute list of this template. Setting once for different
        references saves some time.
        attr_list should be the source attribute list
        If citation given, citation attributes overrule source attributes for 
        the Full and Short references
        The citation date is not stored as attribute, so pass Date() object via
        date_citation if a date is known.
        """
        self.empty()
        self.attr_list = attr_list or []
        self.attr_list_cite = attr_list_citation or []
        self.date_citation = date_citation
        # store attributes in a dict last to first. this overwrites data so first
        # attribute will be the one taken if duplicates are present
        for attr in self.attr_list[::-1]:
            lower = False
            typ = attr.get_type()
            key = int(typ)
            keystr = typ.xml_str().lower()
            if keystr.lower().endswith(' (short)'):
                #a shorter version, we store with base type
                key = int(SrcAttributeType(keystr[:-8]))
                lower = True
            if key == SrcAttributeType.CUSTOM:
                key = str(typ)
            if key in self.attrmap:
                if lower:
                    self.attrmap[key] = (self.attrmap[key][0],
                                self.attrmap[key][0], attr.get_value())
                else:
                    self.attrmap[key] = (attr.get_value(), 
                                attr.get_value(), self.attrmap[key][1])
            else:
                if lower:
                    #store also in normal already value of short
                    self.attrmap[key] = (attr.get_value(),
                                attr.get_value(), attr.get_value())
                else:
                    self.attrmap[key] = (attr.get_value(), 
                                attr.get_value(), None)

        for attr in self.attr_list_cite[::-1]:
            #we do same for citation information, but only update last two
            # values of the attrmap
            lower = False
            typ = attr.get_type()
            key = int(typ)
            keystr = typ.xml_str().lower()
            if keystr.lower().endswith(' (short)'):
                #a shorter version, we store with base type
                key = int(SrcAttributeType(keystr[:-8]))
                lower = True
            if key == SrcAttributeType.CUSTOM:
                key = str(typ)
            if key in self.attrmap:
                if lower:
                    self.attrmap[key] = (self.attrmap[key][0],
                                self.attrmap[key][2], attr.get_value())
                else:
                    self.attrmap[key] = (self.attrmap[key][0],
                                attr.get_value(), self.attrmap[key][2])
            else:
                #field only present in citation.
                if lower:
                    #store also in normal already value of short, keep empty
                    #string for source fields
                    self.attrmap[key] = ('', attr.get_value(), attr.get_value())
                else:
                    self.attrmap[key] = ('', attr.get_value(), None)
        if self.date_citation:
            #we store the date of the citation in attrmap
            key = SrcAttributeType.DATE
            self.attrmap[key] = (None, self.date_citation, None)

    def reference_L(self, attr_list=None):
        """
        Return the list reference based on the passed source attribute list
        If attr_list is None, same list as before is used.
        """
        if attr_list:
            self.set_attr_list(attr_list)
        if self.refL is not None:
            return self.refL
        self.refL = self._reference(REF_TYPE_L)
        return self.refL

    def reference_S(self, attr_list=None, attr_list_citation=None, date_citation=None):
        """
        Return the short reference based on the passed source attribute list
        If attr_list is None, same list as before is used.
        """
        if attr_list or attr_list_citation or date_citation:
            self.set_attr_list(attr_list, attr_list_citation, date_citation)
        if self.refS is not None:
            return self.refS
        self.refS = self._reference(REF_TYPE_S)
        return self.refS

    def reference_F(self, attr_list=None, attr_list_citation=None, date_citation=None):
        """
        Return the full reference based on the passed source attribute list
        If attr_list is None, same list as before is used.
        """
        if attr_list or attr_list_citation or date_citation:
            self.set_attr_list(attr_list, attr_list_citation, date_citation)
        if self.refF is not None:
            return self.refF
        self.refF = self._reference(REF_TYPE_F)
        return self.refF

    def _reference(self, reftype, gedcomfield=None):
        """
        Compute the reference based on data present.
        At the moment no style is applied!
        
        THIS IS UGLY CODE AT THE MOMENT! SHOULD BE ENTIRELY REWRITTEN, FOR 
        NOW IT JUST GIVES ME SOMETHING TO USE IN THE PROTOTYPE !!
        """
        reflist = self.tempstruct[reftype]
        # reflist is typically a list like
        # [      ('', AUTHOR, '', ',', EMPTY, False, False, EMPTY, EMPTY, None, None),
        #        ('', TITLE, '', ',', STYLE_QUOTE, False, False, EMPTY, EMPTY, None, None),
        #        ('', PUB_INFO, '', '.', EMPTY, False, False, EMPTY, EMPTY, None, None),
        #        ('', DATE, '', ' -', EMPTY, False, False, EMPTY, EMPTY, None, None),
        #        ('', PAGE, 'Page(s)', '.', EMPTY, False, False, EMPTY, EMPTY, None, None),
        #        ]
        
        #set col of attrmap to use:
        if reftype == REF_TYPE_L:
            COL_NORMAL = 0
            COL_SHORT = 2
        else:
            COL_NORMAL = 1
            COL_SHORT = 2
        ref = ['']
        fieldadded = [False]
        for (ldel, field, label, rdel, style, priv, opt, short, gedcom,
                hint, tooltip) in reflist:
            if not gedcomfield is None and gedcom != gedcomfield:
                continue
            customshort = False
            #left delimiter
            if ldel in ['(', '[', '{']:
                ref += ['']
                fieldadded += [False]
                ref[-1] += ldel
                ldeltodo = ''
            else:
                ldeltodo = ldel
            val = self.attrmap.get(field)
            #field
            field = ''
            if val is not None:
                if reftype == REF_TYPE_S and val[COL_SHORT] is not None:
                    customshort = True
                    field = val[COL_SHORT]
                else:
                    field = val[COL_NORMAL]
            if short and not customshort:
                #we apply the shortening algorithm
                ## TODO: not implemented yet
                pass
            #if field is a Date object, we now convert to string
            if isinstance(field, Date):
                field = str(field)
            if field.strip():
                fieldadded[-1] = True
                ref[-1] += ldeltodo
                if len(ref[-1]) and ref[-1][-1] == '.':
                    ref[-1] += ' ' + field[0].capitalize() + field[1:]
                elif  len(ref[-1]) and ref[-1][-1] in [',', ':', '-']:
                    ref[-1] += ' ' + field
                elif len(ref[-1]) and ref[-1] != ' ':
                    ref[-1] += ' ' + field
                else:
                    ref[-1] += field
            #right delimiter
            nobracket = True
            for bracketl, bracketr in [('(', ')'), ('[',']'), ('{','}')]:
                if bracketr in rdel:
                    nobracket = False
                    if len(ref[-1] [ref[-1].find(bracketl)+1:]) > 0 :
                        newval = ref[-1] + rdel
                        ref = ref[:-1]
                        fieldadded = fieldadded[:-1]
                        fieldadded[-1] = True
                        ref[-1] += newval
                    else:
                        #no data inside of delimiter, we remove it entirely
                        ref = ref[:-1]
                        fieldadded = fieldadded[:-1]
                        #if . at end of rdel, add it
                        if rdel[-1] == '.':
                            if ref[-1] and ref[-1][-1] in [',', '.']:
                                ref[-1] = ref[-1][:-1]
                            if ref[-1]:
                                ref[-1] = ref[-1] + '.'
                        elif rdel[-1] == ',':
                            if ref[-1] and ref[-1][-1] in [',', '.']:
                                pass
                            elif ref[-1]:
                                ref[-1] = ref[-1] + ','
            if nobracket:
                # we add rdel
                if not ref[-1]:
                    #nothing there, don't add delimiter
                    pass
                elif len(rdel) and rdel[0] == '.':
                    curval = ref[-1]
                    if len(curval) and curval[-1] == '.':
                        pass
                    elif len(curval) and curval[-1] in [',', ';']:
                        ref[-1] = ref[-1][:-1] + rdel
                    else:
                        ref[-1] = ref[-1] + rdel
                    #we only add delimiters after this if new fields are added
                    fieldadded[-1] = False
                elif len(rdel) and rdel[0] == ',':
                    curval = ref[-1]
                    if len(curval) and curval[-1] in ['.', ';']:
                        pass
                    elif len(curval) and curval[-1] == ',':
                        pass
                    elif fieldadded[-1]:
                        ref[-1] = ref[-1] + rdel
                    #we only add delimiters after this if new fields are added
                    fieldadded[-1] = False
                else:
                    if fieldadded[-1]:
                        ref[-1] = ref[-1] + rdel
                        #we only add delimiters after this if new fields are added
                        fieldadded[-1] = False
                    
        ref = ' '.join(ref)
        if ref:
            ref = ref[0].capitalize() + ref[1:]
            ref.replace('  ', ' ')
            return ref
        else:
            return ref

    def author_gedcom(self, attr_list=None):
        if attr_list:
            self.set_attr_list(attr_list)
        return self._reference(REF_TYPE_L, GED_AUTHOR)

    def title_gedcom(self, attr_list=None):
        if attr_list:
            self.set_attr_list(attr_list)
        return self._reference(REF_TYPE_L, GED_TITLE)

    def pubinfo_gedcom(self, attr_list=None):
        if attr_list:
            self.set_attr_list(attr_list)
        return self._reference(REF_TYPE_L, GED_PUBINF)
