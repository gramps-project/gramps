import os

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------

if os.environ.has_key('USERPROFILE'):
    user_home = os.environ['USERPROFILE'] 
    home_dir = os.path.join(user_home,'gramps')
else:
    user_home = os.environ['HOME'] 
    home_dir = os.path.join(user_home,'.gramps')

bsddbenv_dir   = os.path.join(home_dir,"bsddbenv")
env_dir        = os.path.join(home_dir,"env")


app_gramps          = "application/x-gramps"
app_gramps_xml      = "application/x-gramps-xml"
app_gedcom          = "application/x-gedcom"
app_gramps_package  = "application/x-gramps-package"
app_geneweb         = "application/x-geneweb"
app_vcard           = ["text/x-vcard","text/x-vcalendar"]


PERSON_KEY     = 0
FAMILY_KEY     = 1
SOURCE_KEY     = 2
EVENT_KEY      = 3
MEDIA_KEY      = 4
PLACE_KEY      = 5
REPOSITORY_KEY = 6
REFERENCE_KEY  = 7

PERSON_COL_KEY      = 'columns'
CHILD_COL_KEY       = 'child_columns'
PLACE_COL_KEY       = 'place_columns'
SOURCE_COL_KEY      = 'source_columns'
MEDIA_COL_KEY       = 'media_columns'
REPOSITORY_COL_KEY  = 'repository_columns'
EVENT_COL_KEY       = 'event_columns'
FAMILY_COL_KEY      = 'family_columns'
