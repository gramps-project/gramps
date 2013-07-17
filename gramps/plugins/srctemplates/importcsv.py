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

# the GEDCOM type is predefined and always present. Other templates will be
# loaded via plugins
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
    LOG.debug("**** importcsv.load_srctemplate_cvs called")
    first = True
    TYPE2CITEMAP = {}
    TYPE2TEMPLATEMAP = {}
    tlist = SrcTemplateList()
    CITE_TYPES = {'F': REF_TYPE_F, 'L': REF_TYPE_L, 'S': REF_TYPE_S}
    GEDCOMFIELDS = {'A': GED_AUTHOR, 'T': GED_TITLE, 
                'P': GED_PUBINF, 'D': GED_DATE}
    SHORTERALG = {'LOC': SHORTERALG_LOC, 'YEAR': SHORTERALG_YEAR,
              'ETAL': SHORTERALG_ETAL, 'REV.': SHORTERALG_REVERT_TO_DOT}
    STYLES = {'Quoted': STYLE_QUOTE, 'Italics': STYLE_EMPH,
          'QuotedCont': STYLE_QUOTECONT, 'Bold': STYLE_BOLD}

    template = SrcTemplate()
    template.set_name('GEDCOM')
    template.set_descr('%(first)s - %(sec)s - %(third)s' % {  'first': _('Basic'), 'sec': _('GEDCOM Style'), 'third': _('')})
    handle = create_id()
    template.set_handle(handle)
    TYPE2TEMPLATEMAP['GEDCOM'] = template
    tlist = SrcTemplateList()
    tlist.add_template(handle, template)

    for (cite_type, slist) in TEMPLATES['GEDCOM'].iteritems():
        if cite_type != DESCR:
            for struct in slist:
                LOG.debug(struct)
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
                te = TemplateElement()
                te.set_name(field_type)
                te.set_display(field_label)
                te.set_hint(hint or SrcAttributeType.get_default_hint(field_type))
                te.set_tooltip(tooltip or SrcAttributeType.get_default_tooltip(field_type))
                template.add_template_element(te)
                template.add_structure_element(cite_type, [(ldel, field_type, 
                                field_label, rdel, style, private, optional, 
                                shorteralg, gedcommap, hint, tooltip)])

    template = SrcTemplate()
    template.set_name(UNKNOWN)
    template.set_descr(_("Unrecognized Template. Download it's definition."))
    handle = create_id()
    template.set_handle(handle)
    TYPE2TEMPLATEMAP[UNKNOWN] = template
    tlist = SrcTemplateList()
    tlist.add_template(handle, template)
    
    for cite_type in (REF_TYPE_F, REF_TYPE_L, REF_TYPE_S):
        template.add_structure_element(cite_type, [])
           
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
                    raise NotImplementedError, source_type + ' ' + TYPE2TEMPLATEMAP[source_type].get_descr() + ' NOT equal to known description' + source_descr
                if newtempl:
                    #the template is new in this csv, but already defined, probably user error
                    raise NotImplementedError, 'Source template ' + prevtempl + ' is twice defined in the csv.'
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
        
        #we need to force English SrcAttributeType
        ifield_type = SrcAttributeType()
        ifield_type.set_from_xml_str(field_type)
        ifield_type = int(SrcAttributeType(ifield_type))
        if ifield_type == SrcAttributeType.CUSTOM:
            raise NotImplementedError, "field must be a known SrcAttributeType, is " + str(SrcAttributeType(field_type))
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
        gedcommap = GEDCOMFIELDS.get(row[GEDCOMCOL].strip()) or EMPTY
        style = STYLES.get(row[STYLECOL].strip()) or EMPTY
        hint = row[HINTCOL]
        tooltip = row[TOOLTIPCOL]
        te = TemplateElement()
        te.set_name(field_type)
        te.set_display(_(field_label))
        te.set_hint(_(hint) or SrcAttributeType.get_default_hint(field_type))
        te.set_tooltip(_(tooltip) or SrcAttributeType.get_default_tooltip(field_type))

        if source_type in TYPE2TEMPLATEMAP:
            template = TYPE2TEMPLATEMAP[source_type]
        else:
            template = SrcTemplate()
            handle = create_id()
            template.set_handle(handle)
            TYPE2TEMPLATEMAP[source_type] = template
            tlist.add_template(handle, template)
        # FIXME: If the template element is already present, don't add it again
        template.add_template_element(te)
        template.add_structure_element(cite_type, [(row[LDELCOL], field_type, 
                        _(field_label), row[RDELCOL], style, private, optional, 
                        shorteralg, gedcommap, _(hint), _(tooltip))])
        
    LOG.debug(tlist.get_template_list())
    for handle in tlist.get_template_list():
        LOG.debug(tlist.get_template_from_handle(handle).to_struct())
    return TYPE2CITEMAP
