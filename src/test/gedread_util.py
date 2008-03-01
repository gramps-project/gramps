"""unittest support utilities for reading gedcom

see gedread_test.py for sample usage

"""

import os.path
import shutil

from test import test_util as tu
from GrampsDbUtils import _ReadGedcom as RG
import DbState
import gen.db
import Config

# extraneous leading newlines do not seem to cause problems
# (and actually make it convenient reading the test files!)
# future: may need to remove such lines here if problems develop

# These ged-chunks provide/observe the following requirements
# - minimum required header elements
# - a trailer
# - and one record (spec minimum), using a SUBM 
# Note: not all specified requirements seem strongly enforcced
#    eg: at least one record, also nonexistent references seem
#    ok by design, so the SUBM could have been missing 
# Also note that the 'tail' containing the SUBM record referenced
#  in the header causes a line of console output because we
#  presently do not process SUBM records at all
#  (seems like a bug to me -- to be dealt with later)
# ---------------------------------------------------------------

# _head is presently simply a header with minimum content
_head ="""
0 HEAD
1 SOUR test_gedread_System_ID
1 SUBM @SUBM1@
1 GEDC
2 VERS 5.5
2 FORM LINEAGE-LINKED
1 CHAR ASCII
"""

# _tail is presently a single (SUBM) record plus the trailer
# to satisfy the "one or more records" in the spec
# it also provides a target for the xref in the header
# it also gives a "skipping 1 subordinate.." message error
#   which presumeably will be fixed someday
_tail = """
0 @SUBM1@ SUBM
1 NAME test /gedread/
0 TRLR
"""

def make_gedcom_input(gfile, fragment):
    """create gedcom file with 'fragment' between our head & tail

    fragment would normally be 1 or more complete records
    fragment could be an empty string ("")

    """
    fh = open(gfile,"w")
    for txt in (_head, fragment, _tail):
        fh.write(txt)
    fh.close()


# code patterned after contents of ReadGedcom.import2,
#  but avoiding the occurrence of a popup DialogError.
# NOTE: may need rewrite to track mods in ReadGedcom 
#  test this code via src/test/test/gedread_util_test.py 
# -------------------------------------------------------
def gread(db, fname):
    """read gedcom file into a test db

    NB: test modules may want to consider also, the simplified 
    test logging (from test_util) which is especially helpful
    for testing gedcom support

    """
    cback = None
    DEF_SRC = False
    ifile = open(fname,"rU")
    try:
        try:
            s1 = RG.StageOne(ifile)
            s1.parse()
        except Exception,e:
            raise tu.TestError("stage1 error %r" % e)

        useTrans = False
        ifile.seek(0)
        try:
            gp = RG.GedcomParser(db, ifile, fname, cback, s1, DEF_SRC)
        except Exception, e:
            raise tu.TestError("parser init error %r" % e)

        ##ro = db.readonly
        ##db.readonly = False  # why?
        try:
            gp.parse_gedcom_file(useTrans)
            err = ""
        except Exception, e:
            raise tu.TestError("parse error %r" %e)
        ##db.readonly = ro
    finally:
        ifile.close()


# test db creation
#
#   This may deserve it's own module, but for now it is only used here
#
#    state doesn't seem to be necessary for testing
#    let's try just returning the db
#----------------------------------------------------
def create_empty_db(dbpath):
    """create an empty db for the test caller"""
    state =  DbState.DbState()
    dbclass = gen.db.dbdir.GrampsDBDir
    state.change_database(dbclass(Config.get(Config.TRANSACTIONS)))
    # create empty db (files) via load()
    cback = None
    mode = "rw"
    if os.path.isdir(dbpath):
        shutil.rmtree(dbpath)
    state.db.load(dbpath, cback, mode)
    return state.db

#===eof===
