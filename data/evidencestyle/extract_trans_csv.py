#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013  Benny Malengier
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
This module parses the evidence csv file and generates the code we need in
Gramps to use the evidence style.
"""

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import csv


#-------------------------------------------------------------------------
#
# Code
#
#-------------------------------------------------------------------------
csvfilename = "evidence_style.csv"
NRCOL = 0
CATCOL = 1
CATTYPECOL = 2
TYPECOL = 3
DESCRCOL= 4
CITETYPECOL = 5
IDENTCOL = 6
LDELCOL = 7  # left delimiter
FIELDCOL = 8
LABELCOL = 9
RDELCOL = 10 # right delimiter
GEDCOMCOL = 11
SHORTERCOL = 12
STYLECOL = 13
PRIVACYCOL = 14
OPTCOL = 15
HINTCOL = 16
TOOLTIPCOL = 17

first = True

trans = {}
with open(csvfilename, 'rb') as csvfile:
   reader = csv.reader(csvfile, delimiter=';')
   for row in reader:
        if first:
            first=False
            continue
        elif row[CATCOL]:
            cat = row[CATCOL].strip()
            cattype = row[CATTYPECOL].strip()
            types = row[TYPECOL].strip()
            descr = row[DESCRCOL].strip()
            
            for val in [cat, cattype, types, descr]:
                if val and val not in trans:
                    trans[val] = '_("' + val + '")'
        val = row[HINTCOL]
        if val and val not in trans:
            trans[val] = '_("' + val + '")'
        val = row[TOOLTIPCOL]
        if val and val not in trans:
            trans[val] = '_("' + val + '")'
        
           

#now generate the python code we need in source attr types
code = "#following translations are generated with extract_trans_csv.py\n"
code += "if False:\n"
code += "    #these translations will only occur when needed first time!\n" 

allkeys = sorted(trans.keys())
for field in allkeys:
    code += "    " + trans[field] + '\n'

with open('csv_trans.py', 'wb') as srcattrfile:
    srcattrfile.write(code)
