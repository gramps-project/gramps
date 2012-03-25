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
from optparse import OptionParser, OptionGroup


if sys.platform == 'win32':          
    # GetText Win 32 obtained from http://gnuwin32.sourceforge.net/packages/gettext.htm
    # ....\gettext\bin\msgmerge.exe needs to be on the path
    msgmergeCmd = 'C:\Program Files(x86)\gettext\bin\msgmerge.exe'
    msgfmtCmd = 'C:\Program Files(x86)\gettext\bin\msgfmt.exe'
    msgattribCmd = 'C:\Program Files(x86)\gettext\bin\msgattrib.exe'
    xgettextCmd = os.path.join('C:', 'Program Files(x86)', 'gettext', 'bin', 'xgettext.exe')
    pythonCmd = 'C:\Program Files(x86)\python\bin\python.exe'
elif sys.platform == 'linux2' or os.name == 'darwin':
    msgmergeCmd = 'msgmerge'
    msgfmtCmd = 'msgfmt'
    msgattribCmd = 'msgattrib'
    xgettextCmd = 'xgettext'
    pythonCmd = 'python'

def tests():
    """
    Testing installed programs.
    We made tests (-t flag) by displaying versions of tools if properly
    installed. Cannot run all commands without 'gettext' and 'python'.
    """
    
    try:
        print("\n====='msgmerge'=(merge our translation)================\n")
        os.system('''%(program)s -V''' % {'program': msgmergeCmd})
    except:
        print('Please, install %(program)s for updating your translation' % {'program': msgmergeCmd})
        
    try:
        print("\n==='msgfmt'=(format our translation for installation)==\n")
        os.system('''%(program)s -V''' % {'program': msgfmtCmd})
    except:
        print('Please, install %(program)s for checking your translation' % {'program': msgfmtCmd})
        
    try:
        print("\n===='msgattrib'==(list groups of messages)=============\n")
        os.system('''%(program)s -V''' % {'program': msgattribCmd})
    except:
        print('Please, install %(program)s for listing groups of messages' % {'program': msgattribCmd})
        
    
    try:
        print("\n===='xgettext' =(generate a new template)==============\n")
        os.system('''%(program)s -V''' % {'program': xgettextCmd})
    except:
        print('Please, install %(program)s for generating a new template' % {'program': xgettextCmd})
    
    try:
        print("\n=================='python'=============================\n")
        os.system('''%(program)s -V''' % {'program': pythonCmd})
    except:
        print('Please, install python')
        
        
# See also 'get_string' from Gramps 2.0 (sample with SAX)
        
def XMLParse(filename, mark):
    """
    Experimental alternative to 'intltool-extract' for XML based files.
    """
    
    # in progress ...
    from xml.etree import ElementTree
    
    tree = ElementTree.parse(filename)
    root = tree.getroot()

    python_v = sys.version_info
    
    #if python_v[1] != 6:    
    
    # python 2.7
    # iter() is the new name for getiterator; 
    # in ET 1.3, it is implemented as a generator method,
    # but is otherwise identical
        
    '''
    <?xml version="1.0" encoding="UTF-8"?>
      <tips>
        <_tip number="1">
          <b>Working with Dates</b>
            <br/>
        A range of dates can be given by using the format &quot;between 
        January 4, 2000 and March 20, 2003&quot;. You can also indicate 
        the level of confidence in a date and even choose between seven 
        different calendars. Try the button next to the date field in the
        Events Editor.
        </_tip>
    gramps.pot:
    msgid ""
    "<b>Working with Dates</b><br/>A range of dates can be given by using the "
    "format &quot;between January 4, 2000 and March 20, 2003&quot;. You can also "
    "indicate the level of confidence in a date and even choose between seven "
    "different calendars. Try the button next to the date field in the Events "
    "Editor."
    '''
    
    for key in root.getiterator(mark):
        tip = ElementTree.tostring(key, encoding="UTF-8")
        tip = tip.replace("<?xml version='1.0' encoding='UTF-8'?>", "")
        tip = tip.replace('<_tip number="%(number)s">' % key.attrib, "")
        tip = tip.replace("<br />", "<br/>")
        tip = tip.replace("</_tip>\n\n", "")
        print('_("%s")' % tip)
                
    '''
    <?xml version="1.0" encoding="utf-8"?>
      calendar>
        <country _name="Bulgaria">
          ..
        <country _name="Jewish Holidays">
          <date _name="Yom Kippur" value="> passover(y)" offset="172"/>
    gramps.pot:
    msgid "Bulgaria"
    msgid "Jewish Holidays"
    msgid "Yom Kippur"
    '''
            
    for key in root.getiterator():
        if key.attrib.get(mark):
            line = key.attrib
            string = line.items
            name = '_("%(_name)s")' % line
            print(name)
           

def main():
    """
    The utility for handling translation stuff.
    What is need by Gramps, nothing more.
    """
    
    parser = OptionParser( 
                         description='This program generates a new template and '
                                      'also provides some common features.', 
                         usage='%prog [options]'
                         )
                         
    extract = OptionGroup(
                          parser, 
                          "Extract Options", 
                          "Everything around extraction for message strings."
                          )   
    parser.add_option_group(extract)
    
    update = OptionGroup(
                          parser, 
                          "Update Options", 
                          "Everything around update for translation files."
                          )   
    parser.add_option_group(update)
    
    trans = OptionGroup(
                          parser, 
                          "Translation Options", 
                          "Some informations around translation."
                          )   
    parser.add_option_group(trans)
                         
    parser.add_option("-t", "--test",
			  action="store_true", dest="test", default=False,
			  help="test if 'python' and 'gettext' are properly installed")
                                       
    extract.add_option("-x", "--xml",
			  action="store_true", dest="xml", default=False,
			  help="extract messages from xml based file formats")
    extract.add_option("-g", "--glade",
			  action="store_true", dest="glade", default=False,
			  help="extract messages from glade file format only")
    extract.add_option("-c", "--clean",
			  action="store_true", dest="clean", default=False,
			  help="remove created files")
    extract.add_option("-p", "--pot",
			  action="store_true", dest="catalog", default=False,
			  help="create a new catalog")
              
    # need at least one argument (sv.po, de.po, etc ...)
    update.add_option("-m", "--merge",
			  action="store_true", dest="merge", default=False,
			  help="merge lang.po files with last catalog")
    update.add_option("-k", "--check",
			  action="store_true", dest="check", default=False,
			  help="check lang.po files")
              
    # testing stage
    trans.add_option("-u", "--untranslated",
			  action="store_true", dest="untranslated", default=False,
			  help="list untranslated messages")
    trans.add_option("-f", "--fuzzy",
			  action="store_true", dest="fuzzy", default=False,
			  help="list fuzzy messages")
    
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
        
    if options.untranslated:
        untranslated(args)
        
    if options.fuzzy:
        fuzzy(args)
                
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
    os.system('''intltool-extract --type=gettext/xml ../src/plugins/lib/holidays.xml.in''')
    
    XMLParse('../src/data/tips.xml.in', '_tip')
    XMLParse('../src/plugins/lib/holidays.xml.in', '_name')
        
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
    os.system('''%(xgettext)s --add-comments -j -L Glade '''
              '''--from-code=UTF-8 -o gramps.pot --files-from=glade.txt'''
             % {'xgettext': xgettextCmd}
             )
             

def retrieve():
    """
    Extract messages from all files used by Gramps (python, glade, xml)
    """
    
    extract_xml()
    
    if not os.path.isfile('gramps.pot'):
        create_template()
        
    listing('python.txt', '.py')
    os.system('''%(xgettext)s --add-comments -j --directory=. -d gramps '''
              '''-L Python -o gramps.pot --files-from=python.txt '''
              '''--keyword=_ --keyword=ngettext '''
              '''--keyword=sgettext --from-code=UTF-8''' % {'xgettext': xgettextCmd}
             )
             
    extract_glade()
                
    # C format header (.h extension)
    for h in headers():
        print('xgettext for %s') % h
        os.system('''%(xgettext)s --add-comments -j -o gramps.pot '''
                  '''--keyword=N_ --from-code=UTF-8 %(head)s''' 
                  % {'xgettext': xgettextCmd, 'head': h}
                  )
                          
    clean()
    
                
def clean():
    """
    Remove created files (C format headers, temp listings)
    """
    
    for h in headers():
        if os.path.isfile(h):
            os.unlink(h)
            print('Remove %(head)s' % {'head': h})
            
    if os.path.isfile('python.txt'):
        os.unlink('python.txt')
        print("Remove 'python.txt'")
        
    if os.path.isfile('glade.txt'):
        os.unlink('glade.txt')
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
            os.system('''%(python)s ./check_po --skip-fuzzy ./%(lang.po)s > %(lang)s.txt''' \
                     % {'python': pythonCmd, 'lang.po': arg, 'lang': arg[:2]})
            os.system('''%(msgfmt)s -c -v %(lang.po)s''' % {'msgfmt': msgfmtCmd, 'lang.po': arg})
        else:
            print("Please, try to set an argument with .po extension like '%(arg)s.po'." % {'arg': arg})

def untranslated(args):
    """
    List untranslated messages
    """
    
    if len(args) > 1:
        print('Please, use only one argument (ex: fr.po).')
        return
    
    os.system('''%(msgattrib)s --untranslated %(lang.po)s''' % {'msgattrib': msgattribCmd, 'lang.po': args[0]})
     
def fuzzy(args):
    """
    List fuzzy messages
    """
    
    if len(args) > 1:
        print('Please, use only one argument (ex: fr.po).')
        return
    
    os.system('''%(msgattrib)s --only-fuzzy --no-obsolete %(lang.po)s''' % {'msgattrib': msgattribCmd, 'lang.po': args[0]})
     
if __name__ == "__main__":
	main()
