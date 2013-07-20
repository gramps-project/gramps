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

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger('.template')

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from .srcattrtype import *
from .date import Date
from .tableobj import TableObject
from .secondaryobj import SecondaryObject
from .handle import Handle
from ..constfunc import cuni

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

#-------------------------------------------------------------------------
#
#  SrcTemplate class
#
#-------------------------------------------------------------------------

class SrcTemplate(TableObject):
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
    UNKNOWN = UNKNOWN
    
    def __init__(self, template_key=None):
        """
        Create a new Template instance. 
        
        After initialization, most data items have empty or null values,
        including the database handle.
        """
        TableObject.__init__(self)
        self.handle = ""
        self.name = ""
        self.descr = ""
        self.template_element_list = []
        self.mapping_list = []
        self.structure = {REF_TYPE_L: [], REF_TYPE_F: [],
                          REF_TYPE_S: []}
        self.empty()
 
    def serialize(self):
        """
        Convert the data held in the Template to a Python tuple that
        represents all the data elements. 
        
        This method is used to convert the object into a form that can easily 
        be saved to a database.

        These elements may be primitive Python types (string, integers), 
        complex Python types (lists or tuples, or Python objects. If the
        target database cannot handle complex types (such as objects or
        lists), the database is responsible for converting the data into
        a form that it can use.

        :returns: Returns a python tuple containing the data that should
            be considered persistent.
        :rtype: tuple
        """
        return (
            self.handle,
            self.name,
            self.descr,
            [template_element.serialize() for template_element in self.template_element_list],
            [mapping.serialize() for mapping in self.mapping_list],
           )

    def to_struct(self):
        """
        Convert the data held in this object to a structure (eg,
        struct) that represents all the data elements.
        
        This method is used to recursively convert the object into a
        self-documenting form that can easily be used for various
        purposes, including diffs and queries.

        These structures may be primitive Python types (string,
        integer, boolean, etc.) or complex Python types (lists,
        tuples, or dicts). If the return type is a dict, then the keys
        of the dict match the fieldname of the object. If the return
        struct (or value of a dict key) is a list, then it is a list
        of structs. Otherwise, the struct is just the value of the
        attribute.

        :returns: Returns a struct containing the data of the object.
        :rtype: dict
        """
        return {"handle": Handle("Srctemplate", self.handle), 
                "name": cuni(self.name),
                "descr": cuni(self.descr),
                "elements": [e.to_struct() for e in self.template_element_list],
                "structure": (("%s: %s" % (s, self.structure[s])) for s in self.structure)
                }

    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name
        
    def get_descr(self):
        return self.descr
    
    def set_descr(self, descr):
        self.descr = descr
        
    def get_mapping_types_list(self):
        return self.mapping_types_list
    
    def set_mapping_list(self, mapping_list):
        self.mapping_list = mapping_list
        
    def add_mapping(self, mapping):
        self.mapping_list.append(mapping)
        
    def get_template_element_list(self):
        return self.template_element_list
    
    def set_template_element_list(self, template_element_list):
        self.template_element_list = template_element_list

    def add_template_element(self, template_element):
        self.template_element_list.append(template_element)

    def add_structure_element(self, cite_type, slist):
        self.structure[cite_type] += slist
        
    def get_structure(self):
        return self.structure
        
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

    def __ged_page_reflist(self):
        """
        Construct a derived template reflist for use to construct the gedcom
        page field
        """
        reflist_F = self.structure[REF_TYPE_F]
        reflist_L_fields = [field[1] for field in self.structure[REF_TYPE_L]]
        result = []
        for entry in reflist_F:
            if entry[1] in reflist_L_fields:
                continue
            if entry[1] == SrcAttributeType.DATE:
                continue
            result.append(entry)

    def _reference(self, reftype, gedcomfield=None):
        """
        Compute the reference based on data present.
        At the moment no style is applied!
        
        THIS IS UGLY CODE AT THE MOMENT! SHOULD BE ENTIRELY REWRITTEN, FOR 
        NOW IT JUST GIVES ME SOMETHING TO USE IN THE PROTOTYPE !!
        """
        if gedcomfield == GED_PAGE:
            self.__ged_page_reflist()
        else:
            reflist = self.structure[reftype]
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

    def page_gedcom(self, attr_list=None):
        if attr_list:
            self.set_attr_list(attr_list)
        return self._reference(REF_TYPE_F, GED_PAGE)
    
class TemplateElement(SecondaryObject):        
    """
    TemplateEelement class.

    This class is for keeping information about each template-element.
    
    TemplateElement:

     - template_element_name - English name of the element exactly as it appears
       in Yates e.g. [WRITER FIRST]

     - name to be displayed in the user interface e.g. 'Name of the first
       author'

     - hint e.g. "Doe, D.P. & Cameron, E."

     - tooltip e.g. "Give names in following form: 'FirstAuthorSurname, Given
       Names & SecondAuthorSurname, Given Names'. Like this Gramps can parse the
       name and shorten as needed."

     - citation - True if this element appears in a citation (false for a source
       element)
       
     - short - True if this element is an optional short element
     
     - short_alg - algorithm to shorten the field.
     
     - list of Mappings - there would always be a GEDCOM mapping. Also we would
       expect a CSL mapping

    """

    def __init__(self, source=None):
        """
        Create a new TemplateEelement instance, copying from the source if present.
        """
        if source:
            self.name = source.name
            self.display = source.display
            self.hint = source.hint
            self.tooltip = source.tooltip
            self.citation = source.citation
            self.short - source.short
            self.short_alg = source.short_alg
            self.template_mapping_list = source.template_mapping_list
        else:
            self.name = ""
            self.display = ""
            self.hint = ""
            self.tooltip = ""
            self.citation = False
            self.short = False
            self.short_alg = ""
            self.template_mapping_list = []
        
    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (self.name,
                self.display,
                self.hint,
                self.tooltip,
#                [template_mapping.serialize() for template_mapping in self.template_mapping_list]
               )

    def to_struct(self):
        """
        Convert the data held in this object to a structure (eg,
        struct) that represents all the data elements.
        
        This method is used to recursively convert the object into a
        self-documenting form that can easily be used for various
        purposes, including diffs and queries.

        These structures may be primitive Python types (string,
        integer, boolean, etc.) or complex Python types (lists,
        tuples, or dicts). If the return type is a dict, then the keys
        of the dict match the fieldname of the object. If the return
        struct (or value of a dict key) is a list, then it is a list
        of structs. Otherwise, the struct is just the value of the
        attribute.

        :returns: Returns a struct containing the data of the object.
        :rtype: dict
        """
        return {"name": cuni(self.name),
                "display": cuni(self.display),
                "hint": cuni(self.hint),
                "tooltip": cuni(self.tooltip),
                }

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (self.name, self.type) = data
        return self

    def get_name(self):
        """
        Return the name for the Template element.
        """
        return self.name

    def set_name(self, name):
        """
        Set the name for the Template element according to the given argument.
        """
        self.name = name

    def get_hint(self):
        """
        Return the hint for the Template element.
        """
        return self.hint

    def set_hint(self, hint):
        """
        Set the hint for the Template element according to the given argument.
        """
        self.hint = hint

    def get_display(self):
        """
        Return the display form for the Template element.
        """
        return self.display

    def set_display(self, display):
        """
        Set the display form for the Template element according to the given
        argument.
        """
        self.display = display
        
    def get_tooltip(self):
        """
        Return the tooltip for the Template element.
        """
        return self.tooltip

    def set_tooltip(self, tooltip):
        """
        Set the tooltip for the Template element according to the given argument.
        """
        self.tooltip = tooltip
        
    def get_citation(self):
        """
        Return the citation for the Template element.
        """
        return self.citation

    def set_citation(self, citation):
        """
        Set the citation for the Template element according to the given argument.
        """
        self.citation = citation
        
    def get_short(self):
        """
        Return the short for the Template element.
        """
        return self.short

    def set_short(self, short):
        """
        Set the short for the Template element according to the given argument.
        """
        self.short = short
        
    def get_short_alg(self):
        """
        Return the short_alg for the Template element.
        """
        return self.short_alg

    def set_short_alg(self, short_alg):
        """
        Set the short_alg for the Template element according to the given argument.
        """
        self.short_alg = short_alg
        
    def get_template_mapping_list(self):
        return self.template_mapping_list
    
    def set_template_mapping_list(self, template_mapping_list):
        self.template_mapping_list = template_mapping_list

    def add_template_mapping(self, template_mapping):
        self.template_mapping_list.append(template_mapping)
        
class MappingElement(SecondaryObject):        
    """
    TemplateEelement class.

    This class is for keeping information about how each [input] Template
    Element is mapped to an Output form.
    
    Mapping:

     - Mapping_name - English name of the mapping. One mapping GEDCOM would
       always be present. Other mappings are optional, but as we have decided
       that (at least initially) we would use the CSL mapping, then this should
       also be present). (The mappings should be the same as in the
       MappingType).

     - map_target - the English interchange-element name onto which this
       template-element is mapped. e.g. [WRITER FIRST] is mapped onto Recipient,
       so this would contain recipient.

     - Mapping_order the sequence number for this mapping. So [WRITER LAST],
       [WRITER FIRST] both map to 'Recipient', [WRITER FIRST] is 2, [WRITER
       LAST] is 1

     - separator - the separator after this element if there is another one
       following, e.g.", "
    """

    def __init__(self, source=None):
        """
        Create a new MappingEelement instance, copying from the source if
        present.
        """
        if source:
            self.name = source.name
            self.target = source.target
            self.order = source.order
            self.separator = source.separator
        else:
            self.name = ""
            self.target = ""
            self.order = ""
            self.separator = ""
        
    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (self.name,
                self.target,
                self.order,
                self.separator
               )

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (self.name, self.type) = data
        return self

    def get_name(self):
        """
        Return the name for the mapping element.
        """
        return self.name

    def set_name(self, name):
        """
        Set the role according to the given argument.
        """
        self.name = name

    def get_target(self):
        """
        Return the tuple corresponding to the preset role.
        """
        return self.target

    def set_target(self, target):
        """
        Set the role according to the given argument.
        """
        self.target = target
