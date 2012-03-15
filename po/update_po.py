#! /usr/bin/env python
#
# update_po - a gramps tool to update translations
#
# Copyright (C) 2006-2006  Kees Bakker
# Copyright (C) 2006       Brian Matherly
# Copyright (C) 2008       Stephen George
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


if sys.platform == 'win32':          
    # GetText Win 32 obtained from http://gnuwin32.sourceforge.net/packages/gettext.htm
    # ....\gettext\bin\msgmerge.exe needs to be on the path
    msgmergeCmd = 'msgmerge.exe'
    msgfmtCmd = 'msgfmt.exe'
    pythonCmd = 'python.exe'
elif sys.platform == 'linux2':
    msgmergeCmd = 'msgmerge'
    msgfmtCmd = 'msgfmt'
    pythonCmd = 'python'

def tests():
    """
    Testing installed programs.
    We made tests (-t flag) by displaying versions of tools if properly
    installed. Cannot run all commands without 'gettext' and 'python'.
    """
    
    try:
        print("====='msgmerge'=(merge our translation)=================")
        os.system('''%(program)s -V''' % {'program': msgmergeCmd})
    except:
        print('Please, install %(program)s for updating your translation' % {'program': msgmergeCmd})
        
    try:
        print("===='msgfmt'=(format our translation for installation)==")
        os.system('''%(program)s -V''' % {'program': msgfmtCmd})
    except:
        print('Please, install %(program)s for checking your translation' % {'program': msgfmtCmd})
        
    try:
        print("=================='python'============================")
        os.system('''%(program)s -V''' % {'program': pythonCmd})
    except:
        print('Please, install python')

    
def XMLParse(filename, mark):
    """
    Experimental alternative to 'intltool-extract' for XML based files.
    """
    
    # in progress ...
    from xml.etree import ElementTree
    
    tree = ElementTree.parse(filename)
    root = tree.getroot()
    
    tips = names = []
                
    for key in root:
        if key.tag == mark:
            tips.append((key.attrib, ElementTree.tostring(key, encoding="UTF-8")))
                       
    if mark == '_tip':
        for tip in tips:
            print(tip)
        
    if mark == '_name':
        print(names)
    

def main():
    """
    The utility for handling translation stuff.
    What is need by Gramps, nothing more.
    """
    
    parser = OptionParser( 
                         description='This program generates a new template and '
                                      'also provide some common features.', 
                         usage='%prog [options]'
                         )
                         
    parser.add_option("-t", "--test",
			  action="store_true", dest="test", default=False,
			  help="test if 'python' and 'gettext' are properly installed")
                         
    parser.add_option("-x", "--xml",
			  action="store_true", dest="xml", default=False,
			  help="extract messages from xml based file formats")
    parser.add_option("-g", "--glade",
			  action="store_true", dest="glade", default=False,
			  help="extract messages from glade file format only")
    parser.add_option("-c", "--clean",
			  action="store_true", dest="clean", default=False,
			  help="remove created files")
    parser.add_option("-p", "--pot",
			  action="store_true", dest="catalog", default=False,
			  help="create a new catalog")
              
    # need at least one argument (sv.po, de.po, etc ...)
    parser.add_option("-m", "--merge",
			  action="store_true", dest="merge", default=False,
			  help="merge lang.po files with last catalog")
    parser.add_option("-k", "--check",
			  action="store_true", dest="check", default=False,
			  help="check lang.po files")
    
    (options, args) = parser.parse_args()
    
    if options.test:
        tests()
       
    if options.xml:
        extract_xml()
        
    if options.glade:
        extract_glade()
        
    if options.catalog:
        retrieve()
        
    if options.clean:
        clean()
        
    if options.merge:
        merge(args)
        
    if options.check:
        check(args)
                
def listing(name, extension):
    """
    List files according to extensions.
    Parsing from a textual file (gramps) is faster and easy for maintenance.
    Like POTFILES.in and POTFILES.skip
    """
    
    f = open('gramps')
    files = [file.strip() for file in f]
    f.close()
    
    temp = open(name, 'w')
    
    for entry in files:
        (module, ext) = os.path.splitext(entry)
        if ext == extension:
            temp.write(entry)
            temp.write('\n')
    
    temp.close()
                        
    
def headers():
    """
    Look at existing C file format headers.
    Generated by 'intltool-extract' but want to get rid of this 
    dependency (perl, just a set of tools).
    """
       
    headers = []
           
    # in.h; extract_xml
    if os.path.isfile('''../src/data/tips.xml.in.h'''):
        headers.append('''../src/data/tips.xml.in.h''')
    if os.path.isfile('''../src/plugins/lib/holidays.xml.in.h'''):
        headers.append('''../src/plugins/lib/holidays.xml.in.h''')
        
    # cosmetic
    if os.path.isfile('''../data/gramps.xml.in.h'''):
        headers.append('''../data/gramps.xml.in.h''')
    if os.path.isfile('''../data/gramps.desktop.in.h'''):
        headers.append('''../data/gramps.desktop.in.h''')
    if os.path.isfile('''../data/gramps.keys.in.h'''):
        headers.append('''../data/gramps.keys.in.h''')
    
    return headers
    
               
def extract_xml():
    """
    Extract translation strings from XML based, keys, mime and desktop
    files. Still performed by 'intltool-update'.
    Need to look at own XML files parsing and custom translation marks.
    """
    
    os.system('''intltool-extract --type=gettext/xml ../src/data/tips.xml.in''')
    #XMLParse('../src/data/tips.xml.in', '_tip')
    os.system('''intltool-extract --type=gettext/xml ../src/plugins/lib/holidays.xml.in''')
    #XMLParse('../src/data/tips.xml.in', '_name')
    
    # cosmetic
    # could be simple copies without .in extension
    os.system('''intltool-extract --type=gettext/xml ../data/gramps.xml.in''')
    os.system('''intltool-extract --type=gettext/ini ../data/gramps.desktop.in''')
    os.system('''intltool-extract --type=gettext/keys ../data/gramps.keys.in''')
    
    
def create_template():
    """
    Create a new file for template, if it does not exist.
    """
    
    template = open('gramps.pot', 'w')
    template.close()
    
    
def extract_glade():
    """
    Extract messages from a temp file with all .glade
    """
    
    if not os.path.isfile('gramps.pot'):
        create_template()

    listing('glade.txt', '.glade')
    os.system('''xgettext --add-comments -j -L Glade '''
              '''--from-code=UTF-8 -o gramps.pot --files-from=glade.txt'''
             )
             

def retrieve():
    """
    Extract messages from all files used by Gramps (python, glade, xml)
    """
    
    extract_xml()
    
    if not os.path.isfile('gramps.pot'):
        create_template()
        
    listing('python.txt', '.py')
    os.system('''xgettext --add-comments -j --directory=. -d gramps '''
              '''-L Python -o gramps.pot --files-from=python.txt '''
              '''--keyword=_ --keyword=ngettext '''
              '''--keyword=sgettext --from-code=UTF-8'''
             )
             
    extract_glade()
                
    # C format header (.h extension)
    for h in headers():
        print('xgettext for %s') % h
        os.system('''xgettext --add-comments -j -o gramps.pot '''
                  '''--keyword=N_ --from-code=UTF-8 %(head)s''' % {'head': h}
                  )
                          
    clean()
    
                
def clean():
    """
    Remove created files (C format headers, temp listings)
    """
    
    for h in headers():
        if os.path.isfile(h):
            os.system('''rm %s''' % h)
            print('Remove %(head)s' % {'head': h})
            
    if os.path.isfile('python.txt'):
        os.system('''rm python.txt''')
        print("Remove 'python.txt'")
        
    if os.path.isfile('glade.txt'):
        os.system('''rm glade.txt''')
        print("Remove 'glade.txt'")
        
            
def merge(args):
    """
    Merge messages with 'gramps.pot'
    """
    
    if not args:
        print('Please, add at least one argument (sv.po, de.po).')
            
    for arg in args: 
        if arg[-3:] == '.po':
            print('Merge %(lang)s with current template' % {'lang': arg})
            os.system('''%(msgmerge)s --no-wrap %(lang)s gramps.pot -o updated_%(lang)s''' \
                     % {'msgmerge': msgmergeCmd, 'lang': arg})
            print("Updated file: 'updated_%(lang)s'." % {'lang': arg})
        else:
            print("Please, try to set an argument with .po extension like '%(arg)s.po'." % {'arg': arg})
        
        
def check(args):
    """
    Check the translation file
    """
    
    if not args:
        print('Please, add at least one argument (sv.po, de.po).')
    
    for arg in args:
        if arg[-3:] == '.po':
            print("Checked file: '%(lang.po)s'. See '%(txt)s.txt'." \
                 % {'lang.po': arg, 'txt': arg[:2]})
            os.system('''%(python)s ./check_po ./%(lang.po)s > %(lang)s.txt''' \
                     % {'python': pythonCmd, 'lang.po': arg, 'lang': arg[:2]})
            os.system('''%(msgfmt)s -c -v %(lang.po)s''' % {'msgfmt': msgfmtCmd, 'lang.po': arg})
        else:
            print("Please, try to set an argument with .po extension like '%(arg)s.po'." % {'arg': arg})

if __name__ == "__main__":
	main()
