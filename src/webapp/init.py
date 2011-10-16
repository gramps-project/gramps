# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009         Douglas S. Blank <doug.blank@gmail.com>
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
#

"""
Creates a JSON representation of data for Django's fixture
architecture. We could have done this in Python, or SQL, 
but this makes it useful for all Django-based backends
but still puts it into their syncdb API.
"""

import time
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
import settings

from gen.lib.nametype import NameType
from gen.lib.nameorigintype import NameOriginType
from gen.lib.attrtype import AttributeType
from gen.lib.urltype import UrlType
from gen.lib.childreftype import ChildRefType
from gen.lib.repotype import RepositoryType
from gen.lib.eventtype import EventType
from gen.lib.familyreltype import FamilyRelType
from gen.lib.srcmediatype import SourceMediaType
from gen.lib.eventroletype import EventRoleType
from gen.lib.notetype import NoteType

from grampsdb.models import (GenderType, LdsType, LdsStatus, 
                             NameFormatType, NameOriginType, ThemeType)

def get_datamap(x):
    """
    Returns (code, Name) for a Gramps type tuple.
    """
    return (x[0],x[2])

print "["
for table, entries in [("grampsdb.config", 
                        [(("setting", "\"db_version\""), 
                          ("description", "\"database scheme version\""),
                          ("value_type", "\"str\""), 
                          ("value", "\"0.5.1\"")),
                         (("setting", "\"db_created\""), 
                          ("description", "\"database creation date/time\""),
                          ("value_type", "\"str\""), 
                          ("value", ('"%s"' % time.strftime("%Y-%m-%d %H:%M")))),
                         ]),
                       ("grampsdb.report",
                        [(("name", '"Ahnentafel Report"'),
                          ("handle", '"ancestor_report"'),
                          ("report_type", '"textreport"')),
                         (("name", '"birthday_report"'),
                          ("handle", '"birthday_report"'),
                          ("report_type", '"textreport"')),
                         (("name", '"custom_text"'),
                          ("handle", '"custom_text"'),
                          ("report_type", '"textreport"')),
                         (("name", '"descend_report"'),
                          ("handle", '"descend_report"'),
                          ("report_type", '"textreport"')),
                         (("name", '"det_ancestor_report"'),
                          ("handle", '"det_ancestor_report"'),
                          ("report_type", '"textreport"')),
                         (("name", '"det_descendant_report"'),
                          ("handle", '"det_descendant_report"'),
                          ("report_type", '"textreport"')),
                         (("name", '"endofline_report"'),
                          ("handle", '"endofline_report"'),
                          ("report_type", '"textreport"')),
                         (("name", '"family_group"'),
                          ("handle", '"family_group"'),
                          ("report_type", '"textreport"')),
                         (("name", '"indiv_complete"'),
                          ("handle", '"indiv_complete"'),
                          ("report_type", '"textreport"')),
                         (("name", '"kinship_report"'),
                          ("handle", '"kinship_report"'),
                          ("report_type", '"textreport"')),
                         (("name", '"tag_report"'),
                          ("handle", '"tag_report"'),
                          ("report_type", '"textreport"')),
                         (("name", '"number_of_ancestors_report"'),
                          ("handle", '"number_of_ancestors_report"'),
                          ("report_type", '"textreport"')),
                         (("name", '"place_report"'),
                          ("handle", '"place_report"'),
                          ("report_type", '"textreport"')),
                         (("name", '"simple_book_title"'),
                          ("handle", '"simple_book_title"'),
                          ("report_type", '"textreport"')),
                         (("name", '"summary"'),
                          ("handle", '"summary"'),
                          ("report_type", '"textreport"')),
                         (("name", '"GEDCOM Export"'),
                          ("handle", '"gedcom_export"'),
                          ("options", '"off=ged"'),
                          ("report_type", '"export"')),
                         (("name", '"Gramps XML Export"'),
                          ("handle", '"ex_gpkg"'),
                          ("options", '"off=gramps"'),
                          ("report_type", '"export"')),
                         (("name", '"GEDCOM Import"'),
                          ("handle", '"im_ged"'),
                          ("options", '"iff=ged i=http://arborvita.free.fr/Kennedy/Kennedy.ged"'),
                          ("report_type", '"import"')),
                         (("name", '"Gramps package (portable XML) Import"'),
                          ("handle", '"im_gpkg"'),
                          ("options", '"iff=gramps i=http://gramps.svn.sourceforge.net/viewvc/gramps/trunk/example/gramps/example.gramps?revision=18333"'),
                          ("report_type", '"import"')),
                         ])]:
    entry_count = 0
    for entry in entries:
        print "   {"
        print "      \"model\": \"%s\"," % table
        print "      \"pk\": %d," % (entry_count + 1)
        print "      \"fields\":"
        print "         {"
        key_count = 0
        for items in entry:
            key, value = items
            print ("            \"%s\"   : %s" % (key, value)),
            key_count += 1
            if key_count < len(entry):
                print ","
            else:
                print
        print "         }"
        print "   },"
        entry_count += 1

## Add the data for the type models:

type_models = [NameType, NameOriginType, AttributeType, UrlType, ChildRefType, 
               RepositoryType, EventType, FamilyRelType, SourceMediaType, 
               EventRoleType, NoteType, GenderType, LdsType, LdsStatus,
               NameFormatType]
for type in type_models:
    count = 1
    # Add each code:
    for tuple in type._DATAMAP:
        if len(tuple) == 3: # GRAMPS BSDDB style
            val, name = get_datamap(tuple)
        else: # NEW SQL based
            val, name = tuple
        print "   {"
        print "      \"model\": \"grampsdb.%s\"," % type.__name__.lower()
        print "      \"pk\": %d," % count
        print "      \"fields\":"
        print "         {"
        print "            \"val\"   : %d," % val
        print "            \"name\": \"%s\"" % name
        print "         }"
        print "   }",
        # if it is the last one of the last one, no comma
        if type == type_models[-1] and count == len(type._DATAMAP):
            print
        else:
            print ","
        count += 1
print "]"
