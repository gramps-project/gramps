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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from __future__ import print_function
from collections import defaultdict, OrderedDict
import sys

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
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
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
        self.mapdict = defaultdict(str)
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
            self.mapdict,
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
                "mapdict" : self.mapdict,
                }

    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name
        
    def get_descr(self):
        return self.descr
    
    def set_descr(self, descr):
        self.descr = descr
        
    def get_map_dict(self):
        """Return the map for the template"""
        return self.mapdict
    
    def set_map_dict(self, templmap):
        """Set the map for the template"""
        self.mapdict = templmap
    
    def set_map_element(self, key, value):
        self.mapdict[key] =  value
        
    def get_map_element(self, key):
        return self.mapdict[key]
        
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
        self.input_dict = defaultdict(str)

    def set_attr_list(self, attr_list, attr_list_citation=None, date_citation=None):
        """
        Set the attribute list of this template. Setting once for different
        references saves some time.
        attr_list should be the source attribute list
        If citation given, citation attrib
        utes overrule source attributes for 
        the Full and Short references
        The citation date is not stored as attribute, so pass Date() object via
        date_citation if a date is known.
        """
        self.empty()
        self.attrmap = {}
        self.input_dict = defaultdict(str)
        self.attr_list = attr_list or []
        self.attr_list_cite = attr_list_citation or []
        self.date_citation = date_citation
        
        # -----------------------------------------------------------------
        # Construct the input dictionary
        # First pre-load the dictionary with default settings for citations
        if not attr_list_citation:
            for te in [x for x in self.get_template_element_list()
                       if x.get_citation()]:
                name = str(SrcAttributeType(te.get_name())).upper().replace(' ', '_')
                if te.get_display():
                    val = te.get_display().upper().replace(' ', '_')
                else:
                    val = name
                self.input_dict[name] = "[" + val + "]"
        
        # Now get the actual attribute values. store attributes in a dict last
        # to first. this overwrites data so first attribute will be the one
        # taken if duplicates are present
        for input_attr in ((attr_list or []) + (attr_list_citation or []))[::-1]:
            typ = input_attr.get_type()
            if int(typ) == SrcAttributeType.CUSTOM:
                name = str(typ).upper().replace(' ', '_')
            else:
                name = typ.xml_str().upper().replace(' ', '_')
            self.input_dict[name] = input_attr.get_value()
            # if we haven't already got a value for the short attribute, we
            # store the long attribute in the short attribute
            if not name.endswith("(SHORT)"):
                short_name = name + "_(SHORT)"
                if self.input_dict.get(short_name) is None or \
                        (self.input_dict.get(short_name) and \
                        self.input_dict[short_name] == ("[" + short_name + "]")):
                    self.input_dict[short_name] = self.input_dict[name]

        if self.date_citation:
            #we store the date of the citation in attrmap
            name = SrcAttributeType(SrcAttributeType.DATE).xml_str().upper().replace(' ', '_')
            self.input_dict[name] = str(self.date_citation)
            short_name = name + "_(SHORT)"
            if self.input_dict.get(short_name) is None or \
                    (self.input_dict.get(short_name) and \
                    self.input_dict[short_name] == ("[" + short_name + "]")):
                self.input_dict[short_name] = self.input_dict[name]

        # FIXME: REPOSITORY, REPOSITORY_ADDRESS and REPOSITORY_CALL_NUMBER all
        # need to be added to the self.input_dict. See srctemplatetab.py
        # _add_repo_entry()
    
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
        If attr_list is None, same list as
         before is used.
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
        """
        # http://bugs.python.org/issue6081
        class DefaultBlank(dict):
            def __missing__(self, key):
                return ""
         
        class DefaultKey(dict):
            def __missing__(self, key):
                return "[" + key + "]"
       
        ged_table = {
                 GED_AUTHOR : "GEDCOM_A",
                 GED_TITLE : "GEDCOM_T",
                 GED_PUBINF : "GEDCOM_P",
                 GED_DATE : "GEDCOM_D",
                 GED_PAGE : "GEDCOM_PAGE",
                 }
        if gedcomfield:
            return (self.get_map_element(ged_table[gedcomfield]) %
                    DefaultKey(self.input_dict)) or ""
        
        use_CSL = False
        try:
            import citeproc
            if sys.version_info[0] >= 3:
                use_CSL = True
        except:
            pass
        
        if use_CSL:
            # -----------------------------------------------------------------
            # Construct the standard output-elements
            self.output_dict = OrderedDict()
            LOG.debug(self.get_map_dict())
            LOG.debug("input_attributes \n" +
                      "".join(("%s: %s\n" % item) for item in list(self.input_dict.items())))
            for key, val in list(self.get_map_dict().items()):
                if key[0].islower():
                    try:
                        self.output_dict[key] = val % DefaultBlank(self.input_dict)
                    except:
                        LOG.warn("key error with key %s; val %s; input_dict %s" %
                                 (key, val, self.input_dict))
                        self.output_dict[key] = ""
            
            LOG.debug("CSL_attributes \n" +
                      "".join(("%s: %s\n" % item) for item in list(self.output_dict.items())))
            
            # Temporary fix for not implemented yet templates
            if len(self.output_dict) == 0:
                return ""
            
            # Now fix CSL attributes that need special sub-elements
            for name in ["author", "container_author", "some other name"]:
                if name in self.output_dict:
                    self.output_dict[name] = [{"family": self.output_dict[name],
                                       "given": ""}]
            # -----------------------------------------------------------------
            # Modify the output-elements to allow the standard Chicago style to
            # format the citations close to Evidence Style
            
            # literal dates are not specially treated. Date accessed is converted to
            # a literal publication date to conform to how ESM formats the accessed
            # date
            if "accessed" in self.output_dict:
                self.output_dict["issued"] = {'literal' : "accessed " + self.output_dict['accessed']}
                del self.output_dict['accessed']
            # Website is rendered as publisher_place to conform to how ESM renders
            # it.
            if "url" in self.output_dict:
                self.output_dict["publisher_place"] = \
                    self.output_dict["publisher_place"] if "publisher_place" in self.output_dict \
                                else "" + self.output_dict["url"]
            LOG.debug("self.output_dictibutes modified \n" +
                      "".join(("    %s: %s\n" % item) for item in self.output_dict.items()))
                
            try:
                (refF, refS, refL) = self.get_CSL_references(self.output_dict)
                if reftype == REF_TYPE_F:
                    return refF
                elif reftype == REF_TYPE_S:
                    return refS
                else:
                    return refL
            except:
                print(sys.exc_info()[0], sys.exc_info()[1])
                return ""
        
        else:
            # -----------------------------------------------------------------
            # Construct the standard output-elements
            ref_table = {
                     REF_TYPE_L : "EE_L",
                     REF_TYPE_F : "EE_F",
                     REF_TYPE_S : "EE_S",
                     }
            return (self.get_map_element(ref_table[reftype]) %
                    DefaultKey(self.input_dict)) or ""
    
    def get_CSL_references(self, CSL_attributes):
        # Import the citeproc-py classes we'll use below.
        from citeproc import CitationStylesStyle, CitationStylesBibliography
        from citeproc import Citation, CitationItem
        from citeproc import formatter, Locator
        from citeproc.source.json import CiteProcJSON

        # Process the JSON data to generate a citeproc-py BibliographySource.
        if 'locator' in CSL_attributes:
            loc = Locator("page", CSL_attributes["locator"])
        
        import copy
        c1 = copy.deepcopy(CSL_attributes)
        c2 = copy.deepcopy(CSL_attributes)
             
        bib_source = {"full": c1, "subs" : c2}
        bib_source = {"full": c1}
        
#        for key, entry in bib_source.items():
#            print(key)
#            for name, value in entry.items():
#                print('    {}: {}'.format(name, value))
        
        # load a CSL style (from the current directory)
        
        bib_style = CitationStylesStyle('chicago-fullnote-bibliography-no-ibid.csl')
        
        # Create the citeproc-py bibliography, passing it the:
        # * CitationStylesStyle,
        # * BibliographySource (CiteProcJSON in this case), and
        # * a formatter (plain, html, or you can write a custom formatter)
        
        bibliography = CitationStylesBibliography(bib_style, bib_source, formatter.plain)
        
        
        # Processing citations in a document need to be done in two passes as for some
        # CSL styles, a citation can depend on the order of citations in the
        # bibliography and thus on citations following the current one.
        # For this reason, we first need to register all citations with the
        # CitationStylesBibliography.
        
        if loc:
            citation1 = Citation([CitationItem('full', locator=loc)])
            citation2 = Citation([CitationItem('subs', locator=loc)])
        else:
            citation1 = Citation([CitationItem('full')])
            citation2 = Citation([CitationItem('subs')])
            
        citation1 = Citation([CitationItem('full')])
        
        bibliography.register(citation1)
        bibliography.register(citation2)
        
        
        # In the second pass, CitationStylesBibliography can generate citations.
        # CitationStylesBibliography.cite() requires a callback function to be passed
        # along to be called in case a CitationItem's key is not present in the
        # bilbiography.
        
        def warn(citation_item):
            print("WARNING: Reference with key '{}' not found in the bibliography."
                  .format(citation_item.key))
        
        print('Citations')
        print('---------')
        
        print(bibliography.cite(citation1, warn))
        print(bibliography.cite(citation2, warn))
        
        
        # And finally, the bibliography can be rendered.
        
        print('')
        print('Bibliography')
        print('------------')
        
        print(bibliography.bibliography())   

        return(bibliography.cite(citation1, warn),
               bibliography.cite(citation2, warn),
               bibliography.bibliography())     
    
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
        else:
            self.name = ""
            self.display = ""
            self.hint = ""
            self.tooltip = ""
            self.citation = False
            self.short = False
            self.short_alg = ""
        
    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (self.name,
                self.display,
                self.hint,
                self.tooltip,
                self.citation,
                self.short,
                self.short_alg
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
                "citation": cuni(self.citation),
                "short": cuni(self.short),
                "short_alg": cuni(self.short_alg),
                }

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (self.name, self.display, self.hint, self.tooltip, self.citation,
         self.short, self.short_alg) = data
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
