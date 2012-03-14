#! /usr/bin/env python
#
# update_po - a gramps tool to update a po file
#
# Copyright (C) 2006-2006  Kees Bakker
# Copyright (C) 2012
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


import os
import sys
from optparse import OptionParser



def main():
    
    parser = OptionParser( 
                         description='This program updates the PO file(s) for Gramps,'
                                      ' by generating a new file for tanslator: "update.po".',
                         usage='%prog [options] lang.po'
                         )
                         
    parser.add_option("-a", "--all",
			  action="store_true", dest="all", default=False,
			  help="update all translations (not active)")
    
    (options, args) = parser.parse_args()
    
    if options.all:
        print('Not implemented yet')

    try:
        os.system('''intltool-update -g gramps -o gramps.pot -p''')
    except:
        continue
    
    for po in args:    
        os.system('''msgmerge --no-wrap %s gramps.pot -o update.po''' % po)


if __name__ == "__main__":
	main()
