#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2016       Tim G L Lyons
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

# test/LosHawlos_dbtest.py

"""
Simple test for bsdbd. Minimal adaptations made (2016) from original version to
make the code compile and run under nosetests (unittest). This runs from the
root github directory with a command line like:
nosetests gramps test
where gramps is the directory containing most of the Gramps code, and this file
is in the directory 'test'
"""
import os
import tempfile
import shutil
import sys

from gramps.gen.dbstate import DbState
from gramps.cli.clidbman import CLIDbManager
from gramps.gen.db.base import DbTxn
from gramps.gen.db.utils import make_database
from gramps.gen.errors import DbError, HandleError
import gramps.gen.const as const
import gramps.gen.lib as RelLib

print(sys.path)

tran = None

def dummy_callback(dummy):
    pass

def add_source( db,title,commit=True,fail=False):
    global tran
    if tran is None:
        tran = db.transaction_begin(DbTxn("add source", db))
    db.disable_signals()
    s = RelLib.Source()
    db.add_source(s,tran)
    s.set_title(title)
    if fail:
        return # Fail here
    db.commit_source(s,tran)
    db.enable_signals()
    if commit:
        db.transaction_commit(tran)
        tran = None

def add_person( db,firstname,lastname,commit=True,fail=False):
    global tran
    if tran is None:
        tran = db.transaction_begin(DbTxn("add person", db))
    db.disable_signals()
    p = RelLib.Person()
    db.add_person(p,tran)
    n = RelLib.Name()
    n.set_first_name(firstname)
    s = RelLib.Surname()
    s.set_surname(lastname)
    n.add_surname(s)
    p.set_primary_name(n)
    if fail:
        return # Fail here
    db.commit_person(p,tran)
    db.enable_signals()
    if commit:
        db.transaction_commit(tran)
        tran = None

def print_db_content(db):
    for h in db.get_person_handles():
        print("DB contains: person %s" % h)
    for h in db.get_source_handles():
        print("DB contains: source %s" % h)

tmpdir = tempfile.mkdtemp()
try:
    filename1 = os.path.join(tmpdir,'test1.grdb')
    filename2 = os.path.join(tmpdir,'test2.grdb')
    print("\nUsing Database file: %s" % filename1)
    dbstate = DbState()
    dbman = CLIDbManager(dbstate)
    dirpath, name = dbman.create_new_db_cli(filename1, dbid="bsddb")
    db = make_database("bsddb")
    db.load(dirpath, None)
    print("Add person 1")
    add_person( db,"Anton", "Albers",True,False)
    print("Add source")
    add_source( db,"A short test",True,False)
    print("Add person 2 without commit")
    add_person( db,"Bernd","Beta",False,False)
    print("Add source")
    add_source( db,"A short test",True,False)
    print("Add person 3")
    add_person( db,"Chris","Connor",True,False)
    print_db_content( db)
    print("Closing Database file: %s" % filename1)
    db.close()
    tran = None

    print("\nUsing Database file: %s" % filename1)
    dbstate = DbState()
    dbman = CLIDbManager(dbstate)
    dirpath, name = dbman.create_new_db_cli(filename1, dbid="bsddb")
    db = make_database("bsddb")
    db.load(dirpath, None)
    print("Add person 4")
    add_person( db,"Felix", "Fowler",True,False)
    print ("Add person 4")
    add_person( db,"Felix", "Fowler",False,False)
    print_db_content( db)
    print("Closing Database file: %s" % filename1)
    db.close()
    tran = None

    print("\nUsing Database file: %s" % filename2)
    dbstate = DbState()
    dbman = CLIDbManager(dbstate)
    dirpath, name = dbman.create_new_db_cli(filename2, dbid="bsddb")
    db = make_database("bsddb")
    db.load(dirpath, None)

    print("Add source")
    add_source( db,"A short test",False,False)
    # actually, adding a second source while the first transaction is not
    # committed will just add the second source to the first transaction, so
    # nothing special will fail.
    print("Add source 2 will fail; but I don't see why it should")
    add_source( db,"Bang bang bang",True,True)

    print_db_content( db)
    print("Closing Database file: %s" % filename2)
    db.close()
finally:
    print("Exit. Cleaning up.")
    shutil.rmtree(tmpdir)
