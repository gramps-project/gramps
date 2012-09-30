# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Douglas S. Blank <doug.blank@gmail.com>
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

""" Unittest for config.py """

import unittest
from config import ConfigManager

def callback(*args):
    # args: self, 0, str(setting), None
    # print "Calling callback with:", args
    # self is ConfigManager
    self = args[0]
    self._x = args[2]

class CompleteCheck(unittest.TestCase):
    
    def testAll(self):
        self.CM = ConfigManager("./temp.ini")
        self.CM.register("section.setting1", 1) # int
        self.CM.register("section.setting2", 3.1415) # float
        self.CM.register("section.setting3", "String") # string
        self.CM.register("section.setting4", False) # boolean
    
        assert self.CM.get("section.setting1") == 1
        assert self.CM.get("section.setting2") == 3.1415
        assert self.CM.get("section.setting3") == "String"
        assert self.CM.get("section.setting4") == False
    
        self.CM.set("section.setting1", 2)
        self.CM.set("section.setting2", 8.6)
        self.CM.set("section.setting3", "Another String")
        self.CM.set("section.setting4", True)
    
        assert self.CM.get("section.setting1") == 2
        assert self.CM.get("section.setting2") == 8.6
        assert self.CM.get("section.setting3") == "Another String"
        assert self.CM.get("section.setting4") == True
    
        try:
            self.CM.set("section.setting1", 2.8)
        except AttributeError:
            pass
        else:
            raise AssertionError
    
        try:
            self.CM.set("section.setting2", 2)
        except AttributeError:
            pass
        else:
            raise AssertionError
    
        try:
            self.CM.set("section.setting3", 6)
        except AttributeError:
            pass
        else:
            raise AssertionError
    
        try:
            self.CM.set("section.setting4", 1)
        except AttributeError:
            pass
        else:
            raise AssertionError
    
        assert self.CM.get("section.setting1") == 2
        assert self.CM.get("section.setting2") == 8.6
        assert self.CM.get("section.setting3") == "Another String"
        assert self.CM.get("section.setting4") == True
    
        # Try to set one that doesn't exist:
        try:
            self.CM.set("section.setting5", 1)
        except AttributeError:
            pass
        else:
            raise AssertionError
    
        self.CM.save()
    
        self.CM.reset() # to defaults
    
        assert self.CM.get("section.setting1") == 1
        assert self.CM.get("section.setting2") == 3.1415, self.CM.get("section.setting2")
        assert self.CM.get("section.setting3") == "String"
        assert self.CM.get("section.setting4") == False
    
        self.CM._x = None
    
        cbid = self.CM.connect("section.setting1", callback)
        assert self.CM._x == None
    
        self.CM.set("section.setting1", 1024)
        assert self.CM._x == "1024", "x was '%s'" % self.CM._x
    
        self.CM.disconnect(cbid)
    
        self.CM.set("section.setting1", -1)
        assert self.CM._x == "1024"
    
        self.CM.reset("section.setting1")
        assert self.CM.get("section.setting1") == 1
    
        # No callback:
        self.CM._x = None
        self.CM.set("section.setting1", 200)
        assert self.CM._x == None
        # Now, set one:
        cbid = self.CM.connect("section.setting1", callback)
        # Now, call it:
        self.CM.emit("section.setting1")
        assert self.CM._x == "200"
    
        self.CM.set("section.setting1", 2)
        self.CM.set("section.setting2", 8.6)
        self.CM.set("section.setting3", "Another String")
        self.CM.set("section.setting4", True)

        self.CM.register("section2.windows-file", r"c:\drive\path\o'malley\file.pdf")
        self.CM.register("section2.list", [1, 2, 3, 4])
        self.CM.register("section2.dict", {'a': "apple", "b": "banana"})
        self.CM.register("section2.unicode", "Raötröme")

        self.CM.save("./test2.ini")
        self.CM.reset()

        assert self.CM.get("section.setting1") == 1, self.CM.get("section.setting1")
        assert self.CM.get("section.setting2") == 3.1415
        assert self.CM.get("section.setting3") == "String"
        assert self.CM.get("section.setting4") == False
    
        self.CM.load("./test2.ini")
    
        assert self.CM.get("section.setting1") == 2, self.CM.get("section.setting1")
        assert self.CM.get("section.setting2") == 8.6
        assert self.CM.get("section.setting3") == "Another String"
        assert self.CM.get("section.setting4") == True
    
        assert self.CM.get("section2.windows-file") == r"c:\drive\path\o'malley\file.pdf"
        assert self.CM.get("section2.list") == [1, 2, 3, 4]
        assert self.CM.get("section2.dict") == {'a': "apple", "b": "banana"}
        assert self.CM.get("section2.unicode") == "Raötröme"

if __name__ == "__main__":
    unittest.main()


