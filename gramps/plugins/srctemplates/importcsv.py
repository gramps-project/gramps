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
from gramps.gen.utils.id import create_id
from gramps.gen.lib.srcattrtype import *
from gramps.gen.lib.date import Date
from gramps.gen.lib.srctemplate import SrcTemplate, TemplateElement
from gramps.gen.lib.srctemplatelist import SrcTemplateList

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


def load_srctemplates_data():
    """
    Loads the srctemplates defined, and returns a dict with template data
    """
    LOG.debug("**** load_srctemplate_data. Starting")
    load_srctemplate_gedcom()
    LOG.debug("**** load_srctemplate_data. GEDCOM and UNKNOWN loaded")
    
    
    from gramps.gen.plug import BasePluginManager
    bpmgr = BasePluginManager.get_instance()
    pdatas = bpmgr.get_reg_srctemplates()
    
    for plugin in pdatas:
        mod = bpmgr.load_plugin(plugin)
        if mod:
            csvfilename = mod.csvfile
            LOG.debug("**** load_srctemplate_data. Loading csv from %s" % csvfilename)
            if sys.version_info[0] <3:
                with open(csvfilename, 'rb') as csvfile:
                    load_srctemplate_csv(csvfile)
            else:
                with open(csvfilename, 'r') as csvfile:
                    load_srctemplate_csv(csvfile)
                        
            LOG.debug("**** load_srctemplate_data. csv data loaded")

def load_srctemplate_gedcom():
    """
    Loads the GEDCOM and UNKNOWN templates which are always pre-defined
    """
    TEMPLATES = {
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

    template = SrcTemplate()
    template.set_name('GEDCOM')
    template.set_descr('%(first)s - %(sec)s - %(third)s' % {  'first': _('Basic'), 'sec': _('GEDCOM Style'), 'third': _('')})
    handle = create_id()
    template.set_handle(handle)
    tlist = SrcTemplateList()
    tlist.add_template(handle, template)

    for (cite_type, slist) in list(TEMPLATES['GEDCOM'].items()):
        if cite_type != DESCR:
            for struct in slist:
                if cite_type == REF_TYPE_L or cite_type == REF_TYPE_F:
                    elem = [x for x in template.get_template_element_list()
                                if x.get_name()==struct[1] and x.get_short()==False]
                    if elem:
                        te = elem[0]
                    else:
                        te = TemplateElement()
                        template.add_template_element(te)
                elif cite_type == REF_TYPE_S:
                    te = TemplateElement()
                    template.add_template_element(te)
                ldel = struct[0]
                field_type = struct[1]
                field_label = struct[2]
                rdel = struct[3]
                style = struct[4]
                private = struct[5]
                optional = struct[6]
                shorteralg = struct[7]
                gedcommap = struct[8]
                hint = struct[9]
                tooltip = struct[10]
                te.set_name(field_type)
                te.set_display(field_label)
                te.set_hint(hint or SrcAttributeType.get_default_hint(field_type))
                te.set_tooltip(tooltip or SrcAttributeType.get_default_tooltip(field_type))
                if cite_type == REF_TYPE_S:
                    te.set_short(True)
                    te.set_name(int(SrcAttributeType().short_version(te.get_name())))
                if field_type == SrcAttributeType.PAGE or \
                   field_type == SrcAttributeType.DATE:
                    te.set_citation(True)
                template.add_structure_element(cite_type, [(ldel, field_type, 
                                field_label, rdel, style, private, optional, 
                                shorteralg, gedcommap, hint, tooltip)])

    template.set_map_element("GEDCOM_A", "AUTHOR")
    template.set_map_element("GEDCOM_T", "TITLE")
    template.set_map_element("GEDCOM_P", "PUB_INFO")
    template.set_map_element("GEDCOM_D", "DATE")
    template.set_map_element("GEDCOM_PAGE", "PAGE")

    template.set_map_element("EE_L", "%(AUTHOR)s. %(TITLE)s. %(PUB_INFO)s")
    template.set_map_element("EE_F", "%(AUTHOR)s, %(TITLE)s, %(PUB_INFO)s. %(DATE)s - %(PAGE)s")
    template.set_map_element("EE_S", "%(AUTHOR_(SHORT))s, %(DATE_(SHORT))s - %(PAGE_(SHORT))s.")

    for handle in SrcTemplateList().get_template_list():
        template = SrcTemplateList().get_template_from_handle(handle)
        LOG.debug("source_type: %s" % template.get_name())
        for te in template.get_template_element_list():
            LOG.debug("    name: %s; display: %s; hint: %s; tooltip: %s; citation %s; "
                      "short %s; short_alg %s" %
                      (SrcAttributeType(te.get_name()).xml_str(),
                       te.get_display(), te.get_hint(),
                       te.get_tooltip(), te.get_citation(),
                       te.get_short(), te.get_short_alg()
                      ))

    # Now load the UNKNOWN template
    template = SrcTemplate()
    template.set_name(UNKNOWN)
    template.set_descr(_("Unrecognized Template. Download it's definition."))
    handle = create_id()
    template.set_handle(handle)
    tlist = SrcTemplateList()
    tlist.add_template(handle, template)
    
    for cite_type in (REF_TYPE_F, REF_TYPE_L, REF_TYPE_S):
        template.add_structure_element(cite_type, [])
           
def load_srctemplate_csv(csvfile):
    """
    Loads a template csvfile, and returns a dict with template data
    Note: csvfile could be a list containing strings!
    """
    first = True
    TYPE2CITEMAP = {}
    TYPE2TEMPLATEMAP = {}
    TYPE2FIELDS = collections.defaultdict(lambda: collections.defaultdict(list))
    tlist = SrcTemplateList()
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
                tlist = SrcTemplateList()
                tlist.add_template(handle, template)
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
        
        #we need to force English SrcAttributeType
        ifield_type = SrcAttributeType()
        ifield_type.set_from_xml_str(field_type)
        ifield_type = int(SrcAttributeType(ifield_type))
        if ifield_type == SrcAttributeType.CUSTOM:
            raise NotImplementedError("field must be a known SrcAttributeType, is " + str(SrcAttributeType(field_type)))
        field_type = ifield_type
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
#            field_type = int(SrcAttributeType().short_version(field_type))
            te.set_name(field_type)
            te.set_short_alg(shorteralg)
            te.set_short(True)
            lblval = field_label
            if lblval:
                te.set_display(_('%(normal_version_label)s (Short)') % {
                                    'normal_version_label': lblval})
            template.add_template_element(te)
        TYPE2FIELDS[source_type][cite_type].append(field_type)
        template.add_structure_element(cite_type, [(row[LDELCOL], field_type, 
                        _(field_label), row[RDELCOL], style, private, optional, 
                        shorteralg, gedcommap, _(hint), _(tooltip))])
        
        # Setup the mapping. A typical mapping would look like:
        # ('EE_Full'  : '%(COMPILER)s, "%(TITLE)s", %(TYPE)s, %(WEBSITE CREATOR/OWNER)s, <i>%(WEBSITE)s</i>, (%(URL (DIGITAL LOCATION))s: accessed %(DATE ACCESSED)s), %(ITEM OF INTEREST)s; %(CREDIT LINE)s.')
        target = "EE_" + cite_type_text
        if te.get_short():
            txt = int(SrcAttributeType().short_version(field_type))
        else:
            txt = field_type
        txt = row[LDELCOL] + "%(" + \
              SrcAttributeType(txt).xml_str().upper().replace(' ', '_') + \
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
            if not te.get_hint():
                te.set_hint(SrcAttributeType.get_default_hint(te.get_name()))
            if not te.get_tooltip():
                te.set_tooltip(SrcAttributeType.get_default_tooltip(te.get_name()))
            
            # If this is a short version, set the name accordingly. This could
            # not be done earlier because we needed to keep the old 'non-short'
            # name to find which fields belonged to citations as opposed to
            # sources
            if te.get_short() == True:
                te.set_name(int(SrcAttributeType().short_version(te.get_name())))
    
    # Finally we setup the GEDCOM page fields
    for source_type in TYPE2FIELDS:
        template = TYPE2TEMPLATEMAP[source_type]
        for te in [x for x in template.get_template_element_list()
                   if x.get_citation() and not x.get_short()]:
            target = "GEDCOM_PAGE"
            template.set_map_element(target,
                            ", ".join((template.get_map_element(target), txt)))
            
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

#    for source_type in TYPE2FIELDS:
#        LOG.debug("source_type: %s" % source_type)
#        template = TYPE2TEMPLATEMAP[source_type]
#        for te in template.get_template_element_list():
#            LOG.debug("    name: %s; display: %s; hint: %s; tooltip: %s; "
#                      "citation %s; short %s; short_alg %s" %
#                      (SrcAttributeType(te.get_name()).xml_str(),
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
