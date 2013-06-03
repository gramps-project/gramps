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

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from .srcattrtype import (SrcAttributeType, REF_TYPE_F, REF_TYPE_S, REF_TYPE_L,
                          GED_AUTHOR, GED_TITLE, GED_PUBINF)

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
                ('', AUTHOR, '.', EMPTY, False, False, EMPTY, GED_AUTHOR),
                ('', TITLE, '.', STYLE_QUOTE, False, False, EMPTY, GED_TITLE),
                ('', PUB_INFO, '', EMPTY, False, False, EMPTY, GED_PUBINF),
                ],
            REF_TYPE_F: [
                ('', AUTHOR, ',', EMPTY, False, False, EMPTY, EMPTY),
                ('', TITLE, ',', STYLE_QUOTE, False, False, EMPTY, EMPTY),
                ('', PUB_INFO, '.', EMPTY, False, False, EMPTY, EMPTY),
                ('', DATE, ' -', EMPTY, False, False, EMPTY, EMPTY),
                ('', PAGE6S9, '.', EMPTY, False, False, EMPTY, EMPTY),
                ],
            REF_TYPE_S: [
                ('', AUTHOR, ',', EMPTY, False, False, EMPTY, EMPTY),
                ('', DATE, ' -', EMPTY, False, False, EMPTY, EMPTY),
                ('', PAGE6S9, '.', EMPTY, False, False, EMPTY, EMPTY),
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

    def __init__(self, template_key):
        """
        Initialize the template from a given key.
        If key is an integer, EVIDENCETEMPLATES is used of SrtAttrType. 
        If Key is string, it is first searched as the Key of EVIDENCETEMPLATES,
        otherwise from xml templates (not implemented yet !!)
        """
        self.set_template_key(template_key)

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
        if template_key == SrcAttributeType.UNKNOWN:
            #for key unknown we use styling according to GEDCOM
            template_key = SrcAttributeType.GEDCOM
            
        if isinstance(template_key, int):
            self.tempstruct = SrcAttributeType.EVIDENCETEMPLATES[template_key]
        else:
            try:
                self.tempstruct = SrcAttributeType.EVIDENCETEMPLATES[
                                            K2I_SRCTEMPLATEMAP[template_key]]
            except:
                #
                print ('SrcTemplate: Keyerror "', template_key,
                           '", custom templates templates not implemented?')
                raise NotImplementedError
        self.template_key = template_key

    def set_attr_list(self, attr_list, attr_list_citation=None):
        """
        Set the attribute list of this template. Setting once for different
        references saves some time.
        attr_list should be the source attribute list
        If citation given, citation attributes overrule source attributes for 
        the Full and Short references
        """
        self.empty()
        self.attr_list = attr_list or []
        self.attr_list_cite = attr_list_citation or []
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
                                attr.get_value(), self.attrmap[key][3])
            else:
                #field only present in citation.
                if lower:
                    #store also in normal already value of short, keep None
                    #for source fields
                    self.attrmap[key] = (None,
                                attr.get_value(), attr.get_value())
                else:
                    self.attrmap[key] = (None,
                                attr.get_value(), None)

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

    def reference_S(self, attr_list=None):
        """
        Return the short reference based on the passed source attribute list
        If attr_list is None, same list as before is used.
        """
        if attr_list:
            self.set_attr_list(attr_list)
        if self.refS is not None:
            return self.refS
        self.refS = self._reference(REF_TYPE_S)
        return self.refS

    def reference_F(self, attr_list=None):
        """
        Return the full reference based on the passed source attribute list
        If attr_list is None, same list as before is used.
        """
        if attr_list:
            self.set_attr_list(attr_list)
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
        # [      ('', AUTHOR, ',', EMPTY, False, False, EMPTY, EMPTY),
        #        ('', TITLE, ',', STYLE_QUOTE, False, False, EMPTY, EMPTY),
        #        ('', PUB_INFO, '.', EMPTY, False, False, EMPTY, EMPTY),
        #        ('', DATE, ' -', EMPTY, False, False, EMPTY, EMPTY),
        #        ('', PAGE6S9, '.', EMPTY, False, False, EMPTY, EMPTY),
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
        for (ldel, field, rdel, style, priv, opt, short, gedcom) in reflist:
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
            if field.strip():
                fieldadded[-1] = True
                ref[-1] += ldeltodo
                if len(ref[-1]) and ref[-1][-1] == '.':
                    ref[-1] += ' ' + field[0].capitalize() + field[1:]
                elif  len(ref[-1]) and ref[-1][-1] in [',', ':', '-']:
                    ref[-1] += ' ' + field
                else:
                    ref[-1] += field
            #right delimiter
            if ')' in rdel:
                if len(ref[-1] [ref[-1].find('('):]) > 0 :
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
                        ref[-1] = ref[-1] + '.'
            elif ']' in rdel:
                if len(ref[-1] [ref[-1].find('['):]) > 0 :
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
                        ref[-1] = ref[-1] + '.'
            elif '}' in rdel:
                if len(ref[-1] [ref[-1].find('{'):]) > 0 :
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
                        ref[-1] = ref[-1] + '.'
            else:
                # we add rdel
                if not ref[-1]:
                    #nothing there, don't add delimiter
                    pass
                elif len(rdel) and rdel[0] == '.':
                    curval = ref[-1]
                    if len(curval) and curval[-1] == '.':
                        pass
                    elif len(curval) and curval[-1] == ',':
                        ref[-1] = ref[-1][:-1] + rdel
                    else:
                        ref[-1] = ref[-1] + rdel
                    #we only add delimiters after this if new fields are added
                    fieldadded[-1] = False
                elif len(rdel) and rdel[0] == ',':
                    curval = ref[-1]
                    if len(curval) and curval[-1] == '.':
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
                    
        ref = ''.join(ref)
        if ref:
            return ref[0].capitalize() + ref[1:]
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
