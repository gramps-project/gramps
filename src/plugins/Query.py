#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
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

"""
Run a query on the tables
"""

from Simple import SimpleAccess, SimpleDoc, SimpleTable
from gettext import gettext as _
from PluginUtils import register_quick_report
import Utils
from ReportBase import CATEGORY_QR_MISC
import DateHandler
import gen.lib
import Config

def cleanup_column_name(column):
    """ Handle column aliases for CSV spreadsheet import and SQL """
    retval = column
    # Title case:
    if retval in ["Lastname", 
                  "Surname", _("Surname")]:
        return "surname"
    elif retval in ["Firstname", 
                    "Given name", _("Given name"), 
                    "Given", _("Given")]:
        return "firstname"
    elif retval in ["Callname", 
                    "Call name", _("Call name"),
                    "Call", _("Call")]:
        return "callname"
    elif retval in ["Title", _("Title")]:
        return "title"
    elif retval in ["Prefix", _("Prefix")]:
        return "prefix"
    elif retval in ["Suffix", _("Suffix")]:
        return "suffix"
    elif retval in ["Gender", _("Gender")]:
        return "gender"
    elif retval in ["Source", _("Source")]:
        return "source"
    elif retval in ["Note", _("Note")]:
        return "note"
    elif retval in ["Birthplace", 
                    "Birth place", _("Birth place")]:
        return "birthplace"
    elif retval in ["Birthdate", 
                    "Birth date", _("Birth date")]:
        return "birthdate"
    elif retval in ["Birthsource", 
                    "Birth source", _("Birth source")]:
        return "birthsource"
    elif retval in ["Deathplace", 
                    "Death place", _("Death place")]:
        return "deathplace"
    elif retval in ["Deathdate", 
                    "Death date", _("Death date")]:
        return "deathdate"
    elif retval in ["Deathsource", 
                    "Death source", _("Death source")]:
        return "deathsource"
    elif retval in ["Deathcause", 
                    "Death cause", _("Death cause")]:
        return "deathcause"
    elif retval in ["Grampsid", "ID",
                    "Gramps id", _("Gramps id")]:
        return "grampsid"
    elif retval in ["Person", _("Person")]:
        return "person"
    # ----------------------------------
    elif retval in ["Child", _("Child")]:
        return "child"
    elif retval in ["Source", _("Source")]:
        return "source"
    elif retval in ["Family", _("Family")]:
        return "family"
    # ----------------------------------
    elif retval in ["Mother", _("Mother"), 
                    "Wife", _("Wife"),
                    "Parent2", _("Parent2")]:
        return "wife"
    elif retval in ["Father", _("Father"), 
                    "Husband", _("Husband"),
                    "Parent1", _("Parent1")]:
        return "husband"
    elif retval in ["Marriage", _("Marriage")]:
        return "marriage"
    elif retval in ["Date", _("Date")]:
        return "date"
    elif retval in ["Place", _("Place")]:
        return "place"
    # lowercase
    elif retval in ["lastname", "last_name", 
                  "surname", _("surname")]:
        return "surname"
    elif retval in ["firstname", "first_name", "given_name",
                    "given name", _("given name"), 
                    "given", _("given")]:
        return "firstname"
    elif retval in ["callname", "call_name",
                    "call name", 
                    "call", _("call")]:
        return "callname"
    elif retval in ["title", _("title")]:
        return "title"
    elif retval in ["prefix", _("prefix")]:
        return "prefix"
    elif retval in ["suffix", _("suffix")]:
        return "suffix"
    elif retval in ["gender", _("gender")]:
        return "gender"
    elif retval in ["source", _("source")]:
        return "source"
    elif retval in ["note", _("note")]:
        return "note"
    elif retval in ["birthplace", "birth_place",
                    "birth place", _("birth place")]:
        return "birthplace"
    elif retval in ["birthdate", "birth_date",
                    "birth date", _("birth date")]:
        return "birthdate"
    elif retval in ["birthsource", "birth_source",
                    "birth source", _("birth source")]:
        return "birthsource"
    elif retval in ["deathplace", "death_place",
                    "death place", _("death place")]:
        return "deathplace"
    elif retval in ["deathdate", "death_date",
                    "death date", _("death date")]:
        return "deathdate"
    elif retval in ["deathsource", "death_source",
                    "death source", _("death source")]:
        return "deathsource"
    elif retval in ["deathcause", "death_cause",
                    "death cause", _("death cause")]:
        return "deathcause"
    elif retval in ["grampsid", "id", "gramps_id", 
                    "gramps id", _("gramps id")]:
        return "grampsid"
    elif retval in ["person", _("person")]:
        return "person"
    # ----------------------------------
    elif retval in ["child", _("child")]:
        return "child"
    elif retval in ["source", _("source")]:
        return "source"
    elif retval in ["family", _("family")]:
        return "family"
    # ----------------------------------
    elif retval in ["mother", _("mother"), 
                    "wife", _("wife"),
                    "parent2", _("parent2")]:
        return "wife"
    elif retval in ["father", _("father"), 
                    "husband", _("husband"),
                    "parent1", _("parent1")]:
        return "husband"
    elif retval in ["marriage", _("marriage")]:
        return "marriage"
    elif retval in ["date", _("date")]:
        return "date"
    elif retval in ["place", _("place")]:
        return "place"
    #----------------------------------------------------
    return retval


class DBI:
    def __init__(self, database, document):
        self.database = database
        self.document = document

    def parse(self, query):
        # select col1, col2 from table where exp;
        # select * from table where exp;
        # delete from table where exp;
        self.query = query
        state = "START"
        data = None
        i = 0
        self.columns = []
        self.command = None
        self.where = None
        self.table = None
        while i < len(query):
            c = query[i]
            #print "STATE:", state, c
            if state == "START":
                if c in [' ', '\n', '\t']: # pre white space
                    pass # skip it
                else:
                    state = "COMMAND"
                    data = c
            elif state == "COMMAND":
                if c in [' ', '\n', '\t']: # ending white space
                    self.command = data.lower()
                    data = ''
                    state = "AFTER-COMMAND"
                else:
                    data += c
            elif state == "AFTER-COMMAND":
                if c in [' ', '\n', '\t']: # pre white space
                    pass
                else:
                    state = "COL_OR_FROM"
                    i -= 1
            elif state == "COL_OR_FROM":
                if c in [' ', '\n', '\t',  ',']: # end white space or comma
                    if data.upper() == "FROM":
                        data = ''
                        state = "PRE-GET-TABLE"
                    else:
                        self.columns.append(data.lower())
                        data = ''
                        state = "AFTER-COMMAND"
                else:
                    data += c
            elif state == "PRE-GET-TABLE":
                if c in [' ', '\n', '\t']: # pre white space
                    pass
                else:
                    state = "GET-TABLE"
                    i -= 1
            elif state == "GET-TABLE":
                if c in [' ', '\n', '\t', ';']: # end white space or colon
                    self.table = data.lower()
                    data = ''
                    state = "PRE-GET-WHERE"
                else:
                    data += c
            elif state == "PRE-GET-WHERE":
                if c in [' ', '\n', '\t']: # pre white space
                    pass
                else:
                    state = "GET-WHERE"
                    i -= 1
            elif state == "GET-WHERE":
                if c in [' ', '\n', '\t']: # end white space
                    if data.upper() != "WHERE":
                        raise AttributeError("expecting WHERE got '%s'" % data)
                    else:
                        data = ''
                        state = "GET-EXP"
                else:
                    data += c
            elif state == "GET-EXP":
                self.where = query[i:]
                self.where = self.where.strip()
                if self.where.endswith(";"):
                    self.where = self.where[:-1]
                i = len(query)
            else:
                raise AttributeError("unknown state: '%s'" % state)
            i += 1
        if self.table == None:
            raise AttributeError("malformed query: no table in '%s'\n" % self.query)

    def close(self):
        try:
            self.progress.close()
        except:
            pass

    def eval(self):
        self.sdb = SimpleAccess(self.database)
        self.stab = SimpleTable(self.sdb)
        self.select = 0
        self.progress = Utils.ProgressMeter(_('Processing Query'))
        # display the title
        if self.command == "select":
            self.select_table()
        if self.select > 0:
            self.sdoc = SimpleDoc(self.document)
            self.sdoc.title(self.query)
            self.sdoc.paragraph("\n")
            self.sdoc.paragraph("%d rows processed.\n" % self.select)
            self.stab.write(self.sdoc)
            self.sdoc.paragraph("")
        return _("[%d rows processed]") % self.select

    def get_columns(self, table):
        if table == "people":
            return ("name", "grampsid", "gender", 
                    "birth_date", "birth_place", 
                    "death_date", "death_place",
                    "change", "marker", "private")
        elif table == "events":
            return ("grampsid", "type", "date", 
                    "description", "place", 
                    "change", "marker", "private")
    
    def select_table(self):
        for col_name in self.columns[:]: # copy
            if col_name == "*":
                self.columns.remove('*')
                self.columns.extend( self.get_columns(self.table))
        self.stab.columns(*map(lambda s: s.replace("_", "__"),
                               self.columns))
        if self.table == "people":
            all_people = [person for person in self.sdb.all_people()]
            if len(all_people) > 100:
                self.progress.set_pass(_('Matching people...'), len(all_people)/50)
            count = 0
            for person in all_people:
                if len(all_people) > 100:
                    if count % 50 == 0:
                        self.progress.step()
                count += 1
                row = []
                sorts = []
                env = {_("Date"): gen.lib.date.Date} # env for py.eval
                for col_name in self.columns:
                    col = cleanup_column_name(col_name)
                    if col == "name":
                        env[col_name] = str(person)
                        row.append(person)
                    elif col == "firstname":
                        env[col_name] = person.get_primary_name().get_first_name()
                        row.append(env[col_name])
                    elif col == "surname":
                        env[col_name] = person.get_primary_name().get_surname()
                        row.append(env[col_name])
                    elif col == "suffix":
                        env[col_name] = person.get_primary_name().get_suffix()
                        row.append(env[col_name])
                    elif col == "title":
                        env[col_name] = person.get_primary_name().get_title()
                        row.append(env[col_name])
                    elif col == "birthdate":
                        env[col_name] = self.sdb.birth_date_obj(person)
                        row.append(env[col_name])
                    elif col == "deathdate":
                        env[col_name] = self.sdb.death_date_obj(person)
                        row.append(env[col_name])
                    elif col == "gender":
                        env[col_name] = self.sdb.gender(person)
                        row.append(env[col_name])
                    elif col == "birthplace":
                        env[col_name] = self.sdb.birth_place(person)
                        row.append(env[col_name])
                    elif col == "deathplace":
                        env[col_name] = self.sdb.death_place(person)
                        row.append(env[col_name])
                    elif col == "change":
                        env[col_name] = person.get_change_display()
                        row.append(env[col_name])
                    elif col == "marker":
                        env[col_name] = person.marker.string
                        row.append(env[col_name])
                    elif col == "private":
                        env[col_name] = {True: "private", False: ""}[person.private]
                        row.append(env[col_name])
                    elif col == "grampsid":
                        env[col_name] = person.gramps_id
                        row.append(env[col_name])
                    else:
                        raise AttributeError("unknown column: '%s'" % col_name)
                #sorts.append((len(row)-1,sortval))
                # should we add it?:
                if self.where:
                    try:
                        result = eval(self.where, env)
                    except:
                        raise AttributeError("malformed where clause: '%s'" % self.where)
                        result = False
                else:
                    result = True
                if result:
                    self.select += 1
                    self.stab.row(*row)
                    for (col, value) in sorts:
                        self.stab.row_sort_val(col, value)


def run(database, document, query):
    """
    """
    retval = ""
    dbi = DBI(database, document)
    try:
        q = dbi.parse(query)
    except AttributeError, msg:
        return msg
    try:
        retval = dbi.eval()
    except AttributeError, msg:
        # dialog?
        retval = msg
    dbi.close()
    return retval

#------------------------------------------------------------------------
#
# Register the report
#
#------------------------------------------------------------------------

register_quick_report(
    name = 'query',
    category = CATEGORY_QR_MISC,
    run_func = run,
    translated_name = _("Query"),
    status = _("Stable"),
    description= _("Display data that matches a query"),
    author_name="Douglas Blank",
    author_email="dblank@cs.brynmawr.edu"
    )

