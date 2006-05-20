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
        self.list = []
        self.clean()

    def clean(self):
        self.tlist = []
        self.type = ""
        self.default = ""
        self.key = ""
        self.include = False
        self.short = ""
        self.long = ""
        
    def startElement(self,tag,attrs):
        pass

    def endElement(self,tag):
        data = ''.join(self.tlist).strip()
        if tag == "type":
            self.type = data
        elif tag == "default":
            self.default = data
        elif tag == "include":
            self.include = int(data)
        elif tag == "short":
            self.short = data
        elif tag == "long":
            self.long = data.replace('\n','')
        elif tag == "applyto":
            self.key = data
        elif tag == "schema":
            self.list.append((self.key, self.type, self.default,
                              self.long, self.short, self.include))
            self.clean()
        self.tlist = []

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

    parser = SchemaHandler()
    parser.parse(sys.argv[1])

    f = open("_GrampsConfigKeys.py","w")
    
    for (key, key_type, default, long, short, include) in parser.list:
        data = key.split('/')
        category = data[3]
        token = data[4]
        tkey = token.upper().replace('-','_')
        tmap = type_map[key_type]

        f.write("%-20s = ('%s','%s', %d)\n" % (tkey,
                                               category,
                                               token,
                                               tmap))

    f.write('\n\ndefault_value = {\n')
    for (key, key_type, default, long, short, include) in parser.list:
        data = key.split('/')
        category = data[3]
        token = data[4]
        tkey = token.upper().replace('-','_')
        if key_type == 'bool':
            if default == "1":
                f.write("    %-20s : True,\n" % tkey)
            else:
                f.write("    %-20s : False,\n" % tkey)
        elif key_type == "int":
            f.write("    %-20s : %s,\n" % (tkey,default))
        else:
            f.write("    %-20s : '%s',\n" % (tkey,default))
            
    f.write('}\n')
    f.close()
