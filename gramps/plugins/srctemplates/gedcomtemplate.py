# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
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
Registering GEDCOM srctemplates for GRAMPS.

N.B. This is used both from creating a new database (when the database is in its
normal state), and
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------

from __future__ import print_function

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

from gramps.gen.db import DbTxn

from gramps.gen.utils.id import create_id
from gramps.gen.lib.srctemplate import SrcTemplate
from gramps.gen.lib.templateelement import TemplateElement
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

#
# GEDCOM SrcTemplates distributed with Gramps
#

#name of this style
style = 'GEDCOM'
input_type = 'code'

def load_template(db):
    # Don't load the GEDCOM template twice
    if db.get_GEDCOM_template_handle() is None:
        template = build_GEDCOM_template()
        msg = _("Add template (%s)") % template.get_name()
        with DbTxn(msg, db) as trans:
            db.commit_template(template, trans)
            db.set_GEDCOM_template_handle(template.get_handle())

def build_GEDCOM_template():
    """
    Builds the GEDCOM template. This does not commit the template to the
    database. For Upgrade commit is done in the upgrade code. For new databases,
    commit is done by load_template function.
    """
    EMPTY = 0
    DESCR = -10
    # template to GEDCOM field mapping for L reference fields
    # template to a style mapping
    STYLE_QUOTE      = 1  # add quotes around the field

    DEFAULTS = {
    "Author"  : ("Doe, D.P. & Cameron, E." , "Give names in following form:'FirstAuthorSurname, Given Names & SecondAuthorSurname, Given Names'. Like this Gramps can parse the name and shorten as needed."),
    "Date"  : ("17 Sep 1745" , "The date that this event data was entered into the original source document. ."),
    "Page"  : ("5; or 4,6-8, ..." , "Specific location with in the information referenced. For a published work, this could include the volume of a multi-volume work and the page number(s). For a periodical, it could include volume, issue, and page numbers. For a newspaper, it could include a column number and page number. For an unpublished source, this could be a sheet number, page number, frame number, etc. A census record might have a line number or dwelling and family numbers in addition to the page number. "),
    "Pub_info"  : ("Springer, Berlin, 2014" , "When and where the record was created. For published works, this includes information such as the city of publication, name of the publisher, and year of publication."),
    "Title"  : ("Diary Title, Message Title, Bible Name, Article Title, ..." , "The title of the work, record, or item and, when appropriate, the title of the larger work or series of which it is a part."),
               }

    TEMPLATES = {
            'GEDCOM': {
                REF_TYPE_L: [
                    ('', "Author", '', '.', EMPTY, False, False, EMPTY, GED_AUTHOR,
                    None, None),
                    ('', "Title", '', '.', STYLE_QUOTE, False, False, EMPTY, GED_TITLE,
                    None, None),
                    ('', "Pub_info", '', '', EMPTY, False, False, EMPTY, GED_PUBINF,
                    None, None),
                    ],
                REF_TYPE_F: [
                    ('', "Author", '', ',', EMPTY, False, False, EMPTY, EMPTY,
                    None, None),
                    ('', "Title", '', ',', STYLE_QUOTE, False, False, EMPTY, EMPTY,
                    None, None),
                    ('', "Pub_info", '', '.', EMPTY, False, False, EMPTY, EMPTY,
                    None, None),
                    ('', "Date", '', ' -', EMPTY, False, False, EMPTY, EMPTY,
                    None, None),
                    ('', "Page", 'Page(s)', '.', EMPTY, False, False, EMPTY, EMPTY,
                    None, None),
                    ],
                REF_TYPE_S: [
                    ('', "Author", '', ',', EMPTY, False, False, EMPTY, EMPTY,
                    None, None),
                    ('', "Date", '', ' -', EMPTY, False, False, EMPTY, EMPTY,
                    None, None),
                    ('', "Page", 'Page(s)', '.', EMPTY, False, False, EMPTY, EMPTY,
                    None, None),
                    ],
                DESCR: '%(first)s - %(sec)s - %(third)s' % {  'first': _('Basic'), 'sec': _('GEDCOM Style'), 'third': _('')},
                },
            }

    template = SrcTemplate()
    template.set_name('GEDCOM')
    template.set_descr('%(first)s - %(sec)s - %(third)s' % {  'first': _('Basic'), 'sec': _('GEDCOM Style'), 'third': _('')})
    handle = create_id()
    template.set_handle(handle)

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
                if DEFAULTS.get(field_type):
                    te.set_hint(hint or (DEFAULTS[field_type][0] or ""))
                    te.set_tooltip(tooltip or (DEFAULTS[field_type][1] or ""))
                else:
                    te.set_hint("")
                    te.set_tooltip("")
                if cite_type == REF_TYPE_S:
                    te.set_short(True)
                    if field_type.lower().endswith(' (short)'):
                        te.set_name(field_type)
                    else:
                        te.set_name(field_type + ' (Short)')
                if field_type == "Page" or \
                   field_type == "Date":
                    te.set_citation(True)

    template.set_map_element(GED_AUTHOR, "%(AUTHOR)s")
    template.set_map_element(GED_TITLE, "%(TITLE)s")
    template.set_map_element(GED_PUBINF, "%(PUB_INFO)s")
    template.set_map_element(GED_DATE, "%(DATE)s")
    template.set_map_element(GED_PAGE, "%(PAGE)s")

    template.set_map_element(REF_TYPE_L, "%(AUTHOR)s. %(TITLE)s. %(PUB_INFO)s")
    template.set_map_element(REF_TYPE_F, "%(AUTHOR)s, %(TITLE)s, %(PUB_INFO)s. %(DATE)s - %(PAGE)s")
    template.set_map_element(REF_TYPE_S, "%(AUTHOR_(SHORT))s, %(DATE_(SHORT))s - %(PAGE_(SHORT))s.")

    return template
