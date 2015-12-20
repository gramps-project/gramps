# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009-2012 Douglas S. Blank <doug.blank@gmail.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Creates a JSON representation of data for Django's fixture
architecture. We could have done this in Python, or SQL,
but this makes it useful for all Django-based backends
but still puts it into their syncdb API.
"""
import time
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "default_settings"
import default_settings

from gramps.gen.config import config
from gramps.gen.lib.nametype import NameType
from gramps.gen.lib.nameorigintype import NameOriginType
from gramps.gen.lib.attrtype import AttributeType
from gramps.gen.lib.urltype import UrlType
from gramps.gen.lib.childreftype import ChildRefType
from gramps.gen.lib.repotype import RepositoryType
from gramps.gen.lib.placetype import PlaceType
from gramps.gen.lib.eventtype import EventType
from gramps.gen.lib.familyreltype import FamilyRelType
from gramps.gen.lib.srcmediatype import SourceMediaType
from gramps.gen.lib.eventroletype import EventRoleType
from gramps.gen.lib.notetype import NoteType
from gramps.gen.lib.styledtexttagtype import StyledTextTagType

from gramps.webapp.grampsdb.models import (GenderType, LdsType, LdsStatus,
                                           NameFormatType, NameOriginType,
                                           ThemeType)

def get_datamap(x):
    """
    Returns (code, Name) for a Gramps type tuple.
    """
    return (x[0],x[2])

print("[")
for table, entries in [("grampsdb.config",
                        [(("setting", "\"sitename\""),
                          ("description", "\"site name of family tree\""),
                          ("value_type", "\"str\""),
                          ("value", "\"Gramps-Connect\"")),
                         (("setting", "\"db_version\""),
                          ("description", "\"database scheme version\""),
                          ("value_type", "\"str\""),
                          ("value", "\"0.6.1\"")),
                         (("setting", "\"db_created\""),
                          ("description", "\"database creation date/time\""),
                          ("value_type", "\"str\""),
                          ("value", ('"%s"' % time.strftime("%Y-%m-%d %H:%M")))),
                         ]),
                       ("grampsdb.report",
                        [(("name", '"Ahnentafel Report"'),
                          ('gramps_id', '"R0001"'),
                          ("handle", '"ancestor_report"'),
                          ("report_type", '"report"')),
                         (("name", '"birthday_report"'),
                          ('gramps_id', '"R0002"'),
                          ("handle", '"birthday_report"'),
                          ("report_type", '"report"')),
                         (("name", '"custom_text"'),
                          ('gramps_id', '"R0003"'),
                          ("handle", '"custom_text"'),
                          ("report_type", '"report"')),
                         (("name", '"descend_report"'),
                          ('gramps_id', '"R0004"'),
                          ("handle", '"descend_report"'),
                          ("report_type", '"report"')),
                         (("name", '"det_ancestor_report"'),
                          ('gramps_id', '"R0005"'),
                          ("handle", '"det_ancestor_report"'),
                          ("report_type", '"report"')),
                         (("name", '"det_descendant_report"'),
                          ('gramps_id', '"R0006"'),
                          ("handle", '"det_descendant_report"'),
                          ("report_type", '"report"')),
                         (("name", '"endofline_report"'),
                          ('gramps_id', '"R0007"'),
                          ("handle", '"endofline_report"'),
                          ("report_type", '"report"')),
                         (("name", '"family_group"'),
                          ('gramps_id', '"R0008"'),
                          ("handle", '"family_group"'),
                          ("report_type", '"report"')),
                         (("name", '"indiv_complete"'),
                          ('gramps_id', '"R0009"'),
                          ("handle", '"indiv_complete"'),
                          ("report_type", '"report"')),
                         (("name", '"kinship_report"'),
                          ('gramps_id', '"R0010"'),
                          ("handle", '"kinship_report"'),
                          ("report_type", '"report"')),
                         (("name", '"tag_report"'),
                          ('gramps_id', '"R0011"'),
                          ("handle", '"tag_report"'),
                          ("report_type", '"report"')),
                         (("name", '"number_of_ancestors"'),
                          ('gramps_id', '"R0012"'),
                          ("handle", '"number_of_ancestors"'),
                          ("report_type", '"report"')),
                         (("name", '"place_report"'),
                          ('gramps_id', '"R0013"'),
                          ("handle", '"place_report"'),
                          ("report_type", '"report"')),
                         (("name", '"simple_book_title"'),
                          ('gramps_id', '"R0014"'),
                          ("handle", '"simple_book_title"'),
                          ("report_type", '"report"')),
                         (("name", '"summary"'),
                          ('gramps_id', '"R0015"'),
                          ("handle", '"summary"'),
                          ("report_type", '"report"')),
                         (("name", '"Export"'),
                          ('gramps_id', '"R0016"'),
                          ("handle", '"gedcom_export"'),
                          ("options", '"off=ged"'),
                          ("report_type", '"export"')),
                         (("name", '"Gramps XML Export"'),
                          ('gramps_id', '"R0017"'),
                          ("handle", '"ex_gpkg"'),
                          ("options", '"off=gramps"'),
                          ("report_type", '"export"')),
                         (("name", '"Import"'),
                          ('gramps_id', '"R0018"'),
                          ("handle", '"im_ged"'),
                          ("options", '"iff=ged\\ni=http://arborvita.free.fr/Kennedy/Kennedy.ged"'),
                          ("report_type", '"import"')),
                         (("name", '"Gramps package (portable XML) Import"'),
                          ('gramps_id', '"R0019"'),
                          ("handle", '"im_gpkg"'),
                          ("options", '"iff=gramps\\ni=https://raw.githubusercontent.com/gramps-project/gramps/master/example/gramps/example.gramps"'),
                          ("report_type", '"import"')),
                         ])]:
    entry_count = 0
    for entry in entries:
        print("   {")
        print("      \"model\": \"%s\"," % table)
        print("      \"pk\": %d," % (entry_count + 1))
        print("      \"fields\":")
        print("         {")
        key_count = 0
        for items in entry:
            key, value = items
            print(("            \"%s\"   : %s" % (key, value)), end=' ')
            key_count += 1
            if key_count < len(entry):
                print(",")
            else:
                print()
        print("         }")
        print("   },")
        entry_count += 1

pk = 4
for section in config.get_sections():
    for setting in config.get_section_settings(section):
        key = "%s.%s" % (section, setting)
        value = config.get_default(key)
        print("   {")
        print("      \"model\": \"grampsdb.config\",")
        print("      \"pk\": %d," % pk)
        print("      \"fields\":")
        print("         {")
        print("            \"setting\"   : \"%s\"," % key)
        print("            \"value_type\"   : \"%s\"," % type(value).__name__)
        print("            \"value\": \"%s\"" % value)
        print("         }")
        print("   },", end=' ')
        pk += 1

## Add the data for the type models:

type_models = [NameType, NameOriginType, AttributeType, UrlType, ChildRefType,
               RepositoryType, EventType, FamilyRelType, SourceMediaType,
               EventRoleType, NoteType, GenderType, LdsType, LdsStatus,
               NameFormatType, StyledTextTagType, ThemeType, PlaceType]
for type in type_models:
    count = 1
    # Add each code:
    for tuple in type._DATAMAP:
        if len(tuple) == 3: # Gramps BSDDB style
            val, name = get_datamap(tuple)
        else: # NEW SQL based
            val, name = tuple
        print("   {")
        print("      \"model\": \"grampsdb.%s\"," % type.__name__.lower())
        print("      \"pk\": %d," % count)
        print("      \"fields\":")
        print("         {")
        print("            \"val\"   : %d," % val)
        print("            \"name\": \"%s\"" % name)
        print("         }")
        print("   }", end=' ')
        # if it is the last one of the last one, no comma
        if type == type_models[-1] and count == len(type._DATAMAP):
            print()
        else:
            print(",")
        count += 1
print("]")
