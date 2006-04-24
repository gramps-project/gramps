copy = """#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2006  Donald N. Allingham
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

from xml.parsers.expat import ExpatError, ParserCreate

class SchemaHandler:

    def __init__(self):
        self.tlist = []
        self.type = ""
        self.default = ""
        self.key = ""
        self.short = ""
        self.list = []
        
    def startElement(self,tag,attrs):
        self.tlist = []

    def endElement(self,tag):
        data = ''.join(self.tlist)
        if tag == "type":
            self.type = data
        elif tag == "default":
            self.default = data
        elif tag == "applyto":
            self.key = data
        elif tag == "schema":
            self.list.append((self.key, self.type, self.default))

    def characters(self, data):
        self.tlist.append(data)

    def parse(self, name):

        f = open(name)
        
        self.p = ParserCreate()
        self.p.StartElementHandler = self.startElement
        self.p.EndElementHandler = self.endElement
        self.p.CharacterDataHandler = self.characters
        self.p.ParseFile(f)

        f.close()


if __name__ == "__main__":
    import sys

    type_map = { 'bool' : 0, 'int' : 1 , 'string' : 2 }

    print copy
    
    parser = SchemaHandler()
    parser.parse(sys.argv[1])
    for (key, key_type, default) in parser.list:
        data = key.split('/')
        category = data[3]
        token = data[4]

        print "%-20s = ('%s','%s', %d)" % (token.upper().replace('-','_'),
                                          category,
                                          token,
                                          type_map[key_type])

    print '\n\ndefault_value = {'
    for (key, key_type, default) in parser.list:
        data = key.split('/')
        category = data[3]
        token = data[4]
        tkey = token.upper().replace('-','_')
        if key_type == 'bool':
            if default == "1":
                print "    %-20s : True," % tkey
            else:
                print "    %-20s : False," % tkey
        elif key_type == "int":
            print "    %-20s : %s," % (tkey,default)
        else:
            print "    %-20s : '%s'," % (tkey,default)
            
    print '}'    
        
