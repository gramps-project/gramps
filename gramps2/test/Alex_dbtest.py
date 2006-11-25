import os
import tempfile
import shutil
import sys

sys.path.append('../src')

import GrampsDb
import const
import RelLib

def dummy_callback(dummy):
    pass

def add_person( db,firstname,lastname,commit=True,fail=False):
    tran = db.transaction_begin()
    db.disable_signals()
    p = RelLib.Person()
    db.add_person(p,tran)
    n = RelLib.Name()
    n.set_first_name(firstname)
    n.set_surname(lastname)
    p.set_primary_name(n)
    if fail:
        return # Fail here
    db.commit_person(p,tran)
    db.enable_signals()
    if commit:
        db.transaction_commit(tran, "Add Person")

def print_db_content(db):
    for h in db.get_person_handles():
        print "DB contains: person %s" % h
    for h in db.get_source_handles():
        print "DB contains: source %s" % h

tmpdir = tempfile.mkdtemp()
try:
    filename1 = os.path.join(tmpdir,'test1.grdb')
    print "\nUsing Database file: %s" % filename1
    db = GrampsDb.gramps_db_factory(const.app_gramps)()
    db.load( filename1, dummy_callback, "w")
    print "Add person 1"
    add_person( db,"Anton", "Albers",True,False)
    print_db_content( db)    
    #print "Closing Database file: %s" % filename1
    #db.close()
finally:
    print "Exit. Cleaning up."
    shutil.rmtree(tmpdir)
