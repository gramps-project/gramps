""" GR_test.py

This is a first try at some gedcom read testing that does not
require running a gramps CLI

The biggest difficulty is that every test fragment needs custom
test code. Maybe that's unavoidable, and the best that can be
done is to group similar tests together, so that setUp can be
shared.

Maybe more can be shared: one commonly used test recipe is
to develop a data structure that can be looped over to test
similar fragments with the same piece of test code, putting
fragments and possible control or other validation information
in the data structure.

A controlling principle for such structures is that they should be
designed for maximum ease (and intuitiveness) of data declaration
"""

import sys, os, os.path as op

import unittest as U
import re

from test import test_util as tu
from test import gedread_util as gr


# NoteSource_frag
#  tests structure: NOTE > SOUR
#  using the 2 formats of the SOUR element
# bug #(?) does not properly ignore the SOUR
# test by looking for warning messages resulting
# from parse_record seeing the non-skipped SOUR 
#
# SB: the NOTE data should contain the SOUR or xref
#  but this is NYI (SOUR is ignored within NOTE)
# -----------------------------------------------


#
# numcheck based testing
#   verifies the number of db items via a get_number_of_X() call
#   returns an error string or None 
#
# ? candidate for inclusion in gedread_util.py
#
class nc():
    """nc object -- creates a numcheck function
    
    instantiate a nc object as follows
      c = nc("people", 4)
    and call, passing the database, as follows
      err = c(db)
    which will check for exactly 4 people in the db
    and return a displayable message on error, else None

    NB: name _must_ match the X names in db get_number_of_X
    """
    def dbncheck(s, dbcall):
        err = None
        got = dbcall()
        if not got == s.num:
            err = "%s: got %d, expected %d" % (s.name, got, s.num)
        return err    
    def __init__(s, name, num):
        s.name = name
        s.num = num
        s.getname = "get_number_of_" + name       
    def __call__(s, db):
        dbcall = getattr(db,s.getname)
        s.dbncheck(dbcall)

class fnci():
    """fnci (frag-numcheckset item) is a data container for:
    a fragment of gedcom 
    a sequence of nc items to check
    """
    def __init__(s, frag, ncset):
        s.frag = frag
        s.ncset = ncset

# test data table for Test1.test1a_numchecks
fnumchecks = (
    fnci("""0 @N1@ NOTE Note containing embedded source
1 SOUR embedded source""", 
            (nc("notes", 1),)
        ),
    fnci("""0 @N2@ NOTE Note containing referenced source
1 SOUR @SOUR1@
0 @SOUR1@ SOUR 
1 TITL Phoney source title""",
            (nc("notes", 1), nc("sources",1),)
        ),
    )#end fnumchecks


#
# ? candidate for inclusion in test_util.py
#
def _checklog(tlogger, pat=None):
    # look for absence of specific messages in log
    matches = 0
    ltext = tlogger.logfile_getlines()
    if ltext:
        if pat is None:
            matches = len(ltext)
        else:
            pat = re.compile(pat)
            for l in ltext:
                match = re.match(pat, l) 
                if match:
                    matches += 1
                    # debugging
                    print "(%d) %r" % (matches, match)
    return matches
        


class Test1(U.TestCase):
    def setUp(s):
        # make a test subdir and compose some pathnames
        s.tdir = tu.make_subdir("RG_test")
        s.tdb = op.join(s.tdir,"test_db")
        s.ifil = op.join(s.tdir,"test_in.ged")
        s.lfil = op.join(s.tdir,"test.log")

    def test1a_numchecks(s):
        tl = tu.TestLogger()
        for i,f in enumerate(fnumchecks):
            gr.make_gedcom_input(s.ifil, f.frag)
            db = gr.create_empty_db(s.tdb)
            tl.logfile_init(s.lfil)
            gr.gread(db,s.ifil)
            errs = _checklog(tl, r"Line \d+")
            s.assertEquals(errs, 0,
                "ncset(%d): got %d unexpected log messages" %
                (i,errs))
            # ok, no log error message, check db counts
            for call in f.ncset:
                err = call(db)
                s.assertFalse(err, err)

if __name__ == "__main__":
    U.main()
