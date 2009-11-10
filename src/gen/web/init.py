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

from gen.lib.markertype import MarkerType
from gen.lib.nametype import NameType
from gen.lib.attrtype import AttributeType
from gen.lib.urltype import UrlType
from gen.lib.childreftype import ChildRefType
from gen.lib.repotype import RepositoryType
from gen.lib.eventtype import EventType
from gen.lib.familyreltype import FamilyRelType
from gen.lib.srcmediatype import SourceMediaType
from gen.lib.eventroletype import EventRoleType
from gen.lib.notetype import NoteType

from grampsdb.models import GenderType, LdsType, LdsStatus

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
                          ("value", "\"0.5.0\"")),
                         (("setting", "\"db_created\""), 
                          ("description", "\"database creation date/time\""),
                          ("value_type", "\"str\""), 
                          ("value", ('"%s"' % time.strftime("%Y-%m-%d %H:%M")))),
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

type_models = [MarkerType, NameType, AttributeType, UrlType, ChildRefType, 
               RepositoryType, EventType, FamilyRelType, SourceMediaType, 
               EventRoleType, NoteType, GenderType, LdsType, LdsStatus]
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
