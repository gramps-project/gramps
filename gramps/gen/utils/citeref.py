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
Utility functions to create citation references for Gramps Sources and
Citations.
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from __future__ import print_function
from collections import defaultdict, OrderedDict
import sys

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.lib.srcattrtype import SrcAttributeType

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger('.template')

#-------------------------------------------------------------------------
#
# The functions are passed either a Source object or a Citation object or both.
# They call set_input_dict_and_template to construct a dictionary of template input elements
# to values. This dictionary includes the Date value and any Repository values
# although these are not stored as attributes.
#
# For the GEDCOM fields, the mapping is done immediately. For the bibliographic
# items, 'reference' is called to construct the various citation references.
#
#-------------------------------------------------------------------------

# The predefined template mappings are given names starting with underscore so
# they can be distinguished from CSL mappings.
REF_TYPE_F = "_full" # Full footnote citation to a source
REF_TYPE_S = "_subsequent" # Short footnote citation to a source
REF_TYPE_L = "_bibliography" # Listed reference of the source (no citation info)
GED_AUTHOR = "_GEDCOM_A"
GED_TITLE  = "_GEDCOM_T"
GED_PUBINF = "_GEDCOM_P"
GED_DATE   = "_GEDCOM_D"
GED_PAGE   = "_GEDCOM_PAGE"

refL = None
refF = None
refS = None
input_dict = defaultdict(str)
template_cache = None

def reference_L(db, source=None):
    """
    Return the list reference (bibliography entry) based on the passed source
    If source is None, the same input_dict as before is used.
    """
    global refL
    if source:
        set_input_dict_and_template(db, source)
    if refL is not None:
        return refL
    refL = _reference(db, REF_TYPE_L)
    return refL

def reference_S(db, source=None, citation=None):
    """
    Return the short reference based on the passed source and/or citation
    If both source and citation are None, the same list as before is used.
    """
    global refS
    if source or citation:
        set_input_dict_and_template(db, source, citation)
    if refS is not None:
        return refS
    refS = _reference(db, REF_TYPE_S)
    return refS

def reference_F(db, source=None, citation=None):
    """
    Return the full reference based on the passed source and/or citation
    If both source and citation are None, the same list as before is used.
    """
    global refF
    if source or citation:
        set_input_dict_and_template(db, source, citation)
    if refF is not None:
        return refF
    refF = _reference(db, REF_TYPE_F)
    return refF

def get_gedcom_title(db, source=None):
    global template_cache, source_cache
    if source:
        set_input_dict_and_template(db, source)
    if template_cache is None:
        if source:
            return source.get_name()
        else:
            return source_cache.get_name()
    return (template_cache.get_map_element(GED_TITLE) %
            DefaultKey(input_dict)) or ""

def get_gedcom_author(db, source=None):
    global template_cache, source_cache
    if source:
        set_input_dict_and_template(db, source)
    if template_cache is None:
        return "author not available"
    return (template_cache.get_map_element(GED_AUTHOR) %
            DefaultKey(input_dict)) or ""

def get_gedcom_pubinfo(db, source=None):
    global template_cache, source_cache
    if source:
        set_input_dict_and_template(db, source)
    if template_cache is None:
        return "pubinfo not available"
    return (template_cache.get_map_element(GED_PUBINF) %
            DefaultKey(input_dict)) or ""

def get_gedcom_page(db, citation=None):
    global template_cache
    if citation:
        set_input_dict_and_template(db, source=None, citation=citation)
    if template_cache is None:
        return "page not available"
    return (template_cache.get_map_element(GED_PAGE) %
            DefaultKey(input_dict)) or ""

# http://bugs.python.org/issue6081
class DefaultBlank(dict):
    def __missing__(self, key):
        return ""
 
class DefaultKey(dict):
    def __missing__(self, key):
        return "[" + key + "]"

def empty():
    """
    remove all computed data
    """
    global refL, refF, refS, input_dict, template_cache, source_cache
    refL = None
    refF = None
    refS = None
    input_dict = defaultdict(str)
    template_cache = None
    source_cache = None

def set_input_dict_and_template(db, source=None, citation=None):
    """
    Set the attribute dictionary of this template. Setting once for different
    references saves some time.
    attr_list should be the source attribute list
    If citation given, citation attributes overrule source attributes for 
    the Full and Short references
    The citation date is not stored as attribute, so pass Date() object via
    date_citation if a date is known.
    """
    global refL, refF, refS, input_dict, template_cache, source_cache
    empty()
    
    # Find the template
    if not source and not citation:
        # No source and no citation
        raise NotImplementedError
    elif not source:
        # Citation and no source
        # citation will be used to obtain the source
        source_handle = citation.get_reference_handle()
        source_cache = db.get_source_from_handle(source_handle)
        template_handle = source_cache.get_template()
        if template_handle is None:
            return
        template_cache = db.get_template_from_handle(template_handle)
        attr_list = source_cache.get_attribute_list() + citation.get_attribute_list()
        date_citation = citation.get_date_object()
    elif citation:
        #source and citation are given
        source_cache = source
        # FIXME: as both a source and a citation have been given, they should be
        # connected, so a check for that should be made here. However, in
        # editsource, the 'refernce_handle' for a new citation to an existing
        # source is only set in __base_save when data is saved to the database.
        # Hence the check cannot be done at the moment.
#        if not (citation.get_reference_handle() == source_cache.handle):
#            raise Exception('Citation must be a Citation of the Source being cited')
        template_handle = source_cache.get_template()
        if template_handle is None:
            return
        template_cache = db.get_template_from_handle(template_handle)
        attr_list = source_cache.get_attribute_list() + citation.get_attribute_list()
        date_citation = citation.get_date_object()
    else:
        # Source and no citation
        source_cache = source  
        template_handle = source_cache.get_template()
        if template_handle is None:
            return
        template_cache = db.get_template_from_handle(template_handle)
        attr_list = source_cache.get_attribute_list()
        date_citation = None
       
    # -----------------------------------------------------------------
    # Construct the input dictionary
    # First pre-load the dictionary with default settings for citations
    if not citation:
        for te in [x for x in template_cache.get_template_element_list()
                   if x.get_citation()]:
            name = str(SrcAttributeType(te.get_name())).upper().replace(' ', '_')
            if te.get_display():
                val = te.get_display().upper().replace(' ', '_')
            else:
                val = name
            input_dict[name] = "[" + val + "]"
    
    # Now get the actual attribute values. store attributes in a dict last
    # to first. this overwrites data so first attribute will be the one
    # taken if duplicates are present
    for input_attr in attr_list[::-1]:
        typ = input_attr.get_type()
        if typ.is_custom():
            name = str(typ).upper().replace(' ', '_')
        else:
            name = typ.xml_str().upper().replace(' ', '_')
        input_dict[name] = input_attr.get_value()
        # if we haven't already got a value for the short attribute, we
        # store the long attribute in the short attribute
        if not name.endswith("(SHORT)"):
            short_name = name + "_(SHORT)"
            if input_dict.get(short_name) is None or \
                    (input_dict.get(short_name) and \
                    input_dict[short_name] == ("[" + short_name + "]")):
                input_dict[short_name] = input_dict[name]

    if date_citation and (not date_citation.is_empty()):
        #we store the date of the citation
        name = SrcAttributeType.DATE.upper().replace(' ', '_')
        txt = str(date_citation)
        input_dict[name] = txt
        short_name = name + "_(SHORT)"
        if input_dict.get(short_name) is None or \
                (input_dict.get(short_name) and \
                input_dict[short_name] == ("[" + short_name + "]")):
            input_dict[short_name] = txt

    # FIXME: REPOSITORY, REPOSITORY_ADDRESS and REPOSITORY_CALL_NUMBER all
    # need to be added to the input_dict. See srctemplatetab.py
    # _add_repo_entry()

def _reference(self, reftype):
    """
    Compute the reference based on data present.
    """
    global refL, refF, refS, input_dict, template_cache
   
    if template_cache is None:
        return ""
    
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
                  "".join(("%s: %s\n" % item) for item in list(input_dict.items())))
        for key, val in list(self.get_map_dict().items()):
            if not key.startswith("_"):
                try:
                    self.output_dict[key] = val % DefaultBlank(input_dict)
                except:
                    LOG.warn("key error with key %s; val %s; input_dict %s" %
                             (key, val, input_dict))
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
        return (template_cache.get_map_element(reftype) %
                DefaultKey(input_dict)) or ""

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

