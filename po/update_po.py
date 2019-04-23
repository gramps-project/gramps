#! /usr/bin/env python3
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
update_po.py for Gramps translations.

Examples:
   python update_po.py -t

      Tests if 'gettext' and 'python' are well configured.

   python update_po.py -h

      Calls help and command line interface.

   python update_po.py -p

      Generates a new template/catalog (gramps.pot).

   python update_po.py -m de.po

      Merges 'de.po' file with 'gramps.pot'.

   python update_po.py -k de.po

      Checks 'de.po' file, tests to compile and generates a textual resume.
"""

from __future__ import print_function

import os
import sys
import shutil
from argparse import ArgumentParser

# Windows OS

if sys.platform in ['linux', 'linux2', 'darwin', 'cygwin'] or shutil.which('msgmerge'):
    msgmergeCmd = 'msgmerge'
    msgfmtCmd = 'msgfmt'
    msgattribCmd = 'msgattrib'
    xgettextCmd = 'xgettext'
    pythonCmd = os.path.join(sys.prefix, 'bin', 'python3')
elif sys.platform == 'win32':
    # GetText Win 32 obtained from http://gnuwin32.sourceforge.net/packages/gettext.htm
    # ....\gettext\bin\msgmerge.exe needs to be on the path
    msgmergeCmd = os.path.join('C:', 'Program Files(x86)', 'gettext', 'bin', 'msgmerge.exe')
    msgfmtCmd = os.path.join('C:', 'Program Files(x86)', 'gettext', 'bin', 'msgfmt.exe')
    msgattribCmd = os.path.join('C:', 'Program Files(x86)', 'gettext', 'bin', 'msgattrib.exe')
    xgettextCmd = os.path.join('C:', 'Program Files(x86)', 'gettext', 'bin', 'xgettext.exe')
    pythonCmd = os.path.join(sys.prefix, 'bin', 'python.exe')

# Others OS

elif sys.platform in ['linux', 'linux2', 'darwin', 'cygwin']:
    msgmergeCmd = 'msgmerge'
    msgfmtCmd = 'msgfmt'
    msgattribCmd = 'msgattrib'
    xgettextCmd = 'xgettext'
    pythonCmd = os.path.join(sys.prefix, 'bin', 'python3')
else:
    print("Found platform %s, OS %s" % (sys.platform, os.name))
    print ("Update PO ERROR: unknown system, don't know msgmerge, ... commands")
    sys.exit(0)

# List of available languages, useful for grouped actions

# need files with po extension
LANG = [file for file in os.listdir('.') if file.endswith('.po')]
# add a special 'all' argument (for 'check' and 'merge' arguments)
LANG.append("all")
# visual polish on the languages list
LANG.sort()

def tests():
    """
    Testing installed programs.
    We made tests (-t flag) by displaying versions of tools if properly
    installed. Cannot run all commands without 'gettext' and 'python'.
    """
    try:
        print ("\n====='msgmerge'=(merge our translation)================\n")
        os.system('''%(program)s -V''' % {'program': msgmergeCmd})
    except:
        print ('Please, install %(program)s for updating your translation'
                    % {'program': msgmergeCmd})

    try:
        print ("\n==='msgfmt'=(format our translation for installation)==\n")
        os.system('''%(program)s -V''' % {'program': msgfmtCmd})
    except:
        print ('Please, install %(program)s for checking your translation'
                    % {'program': msgfmtCmd})

    try:
        print ("\n===='msgattrib'==(list groups of messages)=============\n")
        os.system('''%(program)s -V''' % {'program': msgattribCmd})
    except:
        print ('Please, install %(program)s for listing groups of messages'
                    % {'program': msgattribCmd})

    try:
        print("\n===='xgettext' =(generate a new template)==============\n")
        os.system('''%(program)s -V''' % {'program': xgettextCmd})
    except:
        print ('Please, install %(program)s for generating a new template'
                    % {'program': xgettextCmd})

    try:
        print("\n=================='python'=============================\n")
        os.system('''%(program)s -V''' % {'program': pythonCmd})
    except:
        print ('Please, install python')

def TipsParse(filename, mark):
    """
    Experimental alternative to 'intltool-extract' for 'tips.xml'.
    """
    from xml.etree import ElementTree

    tree = ElementTree.parse(filename)
    root = tree.getroot()

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

    char *s = N_("<b>Working with Dates</b><br/>A range of dates can be
    given by using the format &quot;between January 4, 2000 and March 20,
    2003&quot;. You can also indicate the level of confidence in a date
    and even choose between seven different calendars. Try the button
    next to the date field in the Events Editor.");

    gramps.pot:
    msgid ""
    "<b>Working with Dates</b><br/>A range of dates can be given by using the "
    "format &quot;between January 4, 2000 and March 20, 2003&quot;. You can also "
    "indicate the level of confidence in a date and even choose between seven "
    "different calendars. Try the button next to the date field in the Events "
    "Editor."
    '''

    with open('../data/tips.xml.in.h', 'w', encoding='utf-8') as tips:
        marklist = root.iter(mark)
        for key in marklist:
            tip = ElementTree.tostring(key, encoding="UTF-8", method="xml")
            if sys.version_info[0] < 3:
                tip = tip.replace("<?xml version='1.0' encoding='UTF-8'?>", "")
                tip = tip.replace('\n<_tip number="%(number)s">' % key.attrib, "")
            else: # python3 support
                tip = tip.decode("utf-8")
                tip = tip.replace('<_tip number="%(number)s">' % key.attrib, "")
            tip = tip.replace("<br />", "<br/>")
            #tip = tip.replace("\n</_tip>\n", "</_tip>\n") # special case tip 7
            #tip = tip.replace("\n<b>", "<b>") # special case tip 18
            tip = tip.replace("</_tip>\n\n", "")
            tip = tip.replace('"', '&quot;')
            tips.write('char *s = N_("%s");\n' % tip)
    print ('Wrote ../data/tips.xml.in.h')
    root.clear()

def HolidaysParse(filename, mark):
    """
    Experimental alternative to 'intltool-extract' for 'holidays.xml'.
    """
    from xml.etree import ElementTree

    tree = ElementTree.parse(filename)
    root = tree.getroot()
    ellist = root.iter()

    '''
    <?xml version="1.0" encoding="utf-8"?>
      calendar>
        <country _name="Bulgaria">
          ..
        <country _name="Jewish Holidays">
          <date _name="Yom Kippur" value="> passover(y)" offset="172"/>

    char *s = N_("Bulgaria");
    char *s = N_("Jewish Holidays");
    char *s = N_("Yom Kippur");

    gramps.pot:
    msgid "Bulgaria"
    msgid "Jewish Holidays"
    msgid "Yom Kippur"
    '''
    with open('../data/holidays.xml.in.h', 'w') as holidays:
        for key in ellist:
            if key.attrib.get(mark):
                line = key.attrib
                string = line.items
                # mapping via the line dict (_name is the key)
                name = 'char *s = N_("%(_name)s");\n' % line
                holidays.write(name)
    print ('Wrote ../data/holidays.xml.in.h')
    root.clear()


def XmlParse(filename, mark):
    """
    Experimental alternative to 'intltool-extract' for 'file.xml.in'.
    """
    from xml.etree import ElementTree

    tree = ElementTree.parse(filename)
    root = tree.getroot()

    '''
    <?xml version="1.0" encoding="UTF-8"?>

    <mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
      <mime-type type="application/x-gramps">
        <_comment>Gramps database</_comment>
          <glob pattern="*.grdb"/>
      </mime-type>
      <mime-type type="application/x-gedcom">
        <_comment>GEDCOM</_comment>
          <glob pattern="*.ged"/>
          <glob pattern="*.gedcom"/>
          <glob pattern="*.GED"/>
          <glob pattern="*.GEDCOM"/>

    msgid "Gramps database"
    msgid "GEDCOM"

    <description>
    <_p> Gramps is a free software project and community.
    We strive to produce a genealogy program that is both intuitive for hobbyists
    and feature-complete for professional genealogists.
    </p>
    </description>
    '''

    with open(filename + '.h', 'w') as head:
        for key in root.iter():
            if key.tag == '{http://www.freedesktop.org/standards/shared-mime-info}%s' % mark:
                comment = 'char *s = N_("%s");\n' % key.text
                head.write(comment)
            if key.tag == mark: #appdata
                comment = 'char *s = N_("%s");\n' % key.text
                head.write(comment)

        if root.tag == 'application':
            for key in root.iter():
                if key.tag == mark:
                    comment = 'char *s = N_("%s");\n' % key.text
                    head.write(comment)

    print ('Wrote %s' % filename)
    root.clear()

def DesktopParse(filename):
    """
    Experimental alternative to 'intltool-extract' for 'gramps.desktop'.
    """

    '''
    [Desktop Entry]
    _Name=Gramps
    _GenericName=Genealogy System
    _X-GNOME-FullName=Gramps Genealogy System
    _Comment=Manage genealogical information,
             perform genealogical research and analysis

    msgid "Gramps"
    msgid "Genealogy System"
    msgid "Gramps Genealogy System"
    msgid ""
          "Manage genealogical information,
           perform genealogical research and analysis"
    '''
    with open('../data/gramps.desktop.in.h', 'w') as desktop:

        with open(filename) as f:
            lines = [file.strip() for file in f]

        for line in lines:
            if line[0] == '_':
                for i in range(len(line)):
                    if line[i] == '=':
                        val = 'char *s = N_("%s");\n' % line[i+1:len(line)]
                        desktop.write(val)

    print ('Wrote ../data/gramps.desktop.in.h')

def KeyParse(filename, mark):
    """
    Experimental alternative to 'intltool-extract' for 'gramps.keys'.
    """

    '''
    application/x-gramps-xml:
    _description=Gramps XML database
    default_action_type=application
    short_list_application_ids=gramps
    short_list_application_ids_for_novice_user_level=gramps
    short_list_application_ids_for_intermediate_user_level=gramps
    short_list_application_ids_for_advanced_user_level=gramps
    category=Documents/Genealogy
    icon-filename=/usr/share/gramps/gramps.png
    open=gramps %f

    application/x-gedcom:
    _description=GEDCOM
    default_action_type=application

    msgid "Gramps XML database"
    msgid "GEDCOM"
    '''
    with open('../data/gramps.keys.in.h', 'w') as key:

        with open(filename) as f:
            lines = [file for file in f]

        temp = []

        for line in lines:
            for i in range(len(line)):
                if line[i:i+12] == mark:
                    temp.append(line.strip())

        for t in temp:
            for i in range(len(t)):
                if t[i] == '=':
                    val = 'char *s = N_("%s");\n' % t[i+1:len(t)]
                    key.write(val)

    print ('Wrote ../data/gramps.keys.in.h')

def main():
    """
    The utility for handling translation stuff.
    What is need by Gramps, nothing more.
    """

    parser = ArgumentParser(
                         description='This program generates a new template and '
                                      'also provides some common features.',
                         )
    parser.add_argument("-t", "--test",
            action="store_true", dest="test",  default=True,
            help="test if 'python' and 'gettext' are properly installed")

    parser.add_argument("-x", "--xml",
            action="store_true", dest="xml",  default=False,
            help="extract messages from xml based file formats")
    parser.add_argument("-g", "--glade",
            action="store_true", dest="glade",  default=False,
            help="extract messages from glade file format only")
    parser.add_argument("-c", "--clean",
            action="store_true", dest="clean",  default=False,
            help="remove created files")
    parser.add_argument("-p", "--pot",
            action="store_true", dest="catalog",  default=False,
            help="create a new catalog")

    update = parser.add_argument_group('Update', 'Maintenance around translations')

    # need at least one argument (sv.po, de.po, etc ...)

    # lang.po files maintenance
    update.add_argument("-m", dest="merge",
            choices=LANG,
            help="merge lang.po files with last catalog")

    update.add_argument("-k", dest="check",
            choices=LANG,
            help="check lang.po files")

    # testing stage
    trans = parser.add_argument_group('Translation', 'Display content of translations file')

    # need one argument (eg, de.po)

    trans.add_argument("-u", dest="untranslated",
            choices=[file for file in os.listdir('.') if file.endswith('.po')],
            help="list untranslated messages")
    trans.add_argument("-f", dest="fuzzy",
            choices=[file for file in os.listdir('.') if file.endswith('.po')],
            help="list fuzzy messages")

    args = parser.parse_args()
    namespace, extra = parser.parse_known_args()

    if args.test:
        tests()

    if args.xml:
        extract_xml()

    if args.glade:
        create_filesfile()
        extract_glade()
        if os.path.isfile('tmpfiles'):
            os.unlink('tmpfiles')

    if args.catalog:
        retrieve()

    if args.clean:
        clean()

    if args.merge:
        #retrieve() windows os?
        if sys.argv[2:] == ['all']:
            sys.argv[2:] = LANG
        merge(sys.argv[2:])

    if args.check:
        #retrieve() windows os?
        if sys.argv[2:] == ['all']:
            sys.argv[2:] = LANG
        check(sys.argv[2:])

    if args.untranslated:
        untranslated(sys.argv[2:])

    if args.fuzzy:
        fuzzy(sys.argv[2:])

def create_filesfile():
    """
    Create a file with all files that we should translate.
    These are all python files not in POTFILES.skip added with those in
    POTFILES.in
    """
    dir = os.getcwd()
    topdir = os.path.normpath(os.path.join(dir, '..', 'gramps'))
    lentopdir = len(topdir)
    with open('POTFILES.in') as f:
        infiles = dict(['../' + file.strip(), None] for file in f if file.strip()
                                                            and not file[0]=='#')

    with open('POTFILES.skip') as f:
        notinfiles = dict(['../' + file.strip(), None] for file in f if file
                                                            and not file[0]=='#')

    for (dirpath, dirnames, filenames) in os.walk(topdir):
            root, subdir = os.path.split(dirpath)
            if subdir.startswith("."):
                #don't continue in this dir
                dirnames[:] = []
                continue
            for dirname in dirnames:
                # Skip hidden and system directories:
                if dirname.startswith(".") or dirname in ["po", "locale"]:
                    dirnames.remove(dirname)
            #add the files which are python or glade files
            # if the directory does not exist or is a link, do nothing
            if not os.path.isdir(dirpath) or os.path.islink(dirpath):
                continue

            for filename in os.listdir(dirpath):
                name = os.path.split(filename)[1]
                if name.endswith('.py') or name.endswith('.glade'):
                    full_filename = os.path.join(dirpath, filename)
                    #Skip the file if in POTFILES.skip
                    if full_filename[lentopdir:] in notinfiles:
                        infiles['../gramps' + full_filename[lentopdir:]] = None
    #now we write out all the files in form ../gramps/filename
    with open('tmpfiles', 'w') as f:
        for file in sorted(infiles.keys()):
            f.write(file)
            f.write('\n')

def listing(name, extensionlist):
    """
    List files according to extensions.
    Parsing from a textual file (gramps) is faster and easy for maintenance.
    Like POTFILES.in and POTFILES.skip
    """

    with open('tmpfiles') as f:
        files = [file.strip() for file in f if file and not file[0]=='#']

    with open(name, 'w') as temp:
        for entry in files:
            for ext in extensionlist:
                if entry.endswith(ext):
                    temp.write(entry)
                    temp.write('\n')
                    break

def headers():
    """
    Look at existing C file format headers.
    Generated by 'intltool-extract' but want to get rid of this
    dependency (perl, just a set of tools).
    """
    headers = []

    # in.h; extract_xml
    if os.path.isfile('''../data/tips.xml.in.h'''):
        headers.append('''../data/tips.xml.in.h''')
    if os.path.isfile('''../data/holidays.xml.in.h'''):
        headers.append('''../data/holidays.xml.in.h''')
    if os.path.isfile('''../data/gramps.xml.in.h'''):
        headers.append('''../data/gramps.xml.in.h''')
    if os.path.isfile('''../data/gramps.desktop.in.h'''):
        headers.append('''../data/gramps.desktop.in.h''')
    if os.path.isfile('''../data/gramps.keys.in.h'''):
        headers.append('''../data/gramps.keys.in.h''')
    if os.path.isfile('''../data/gramps.appdata.xml.in.h'''):
        headers.append('''../data/gramps.appdata.xml.in.h''')
    if os.path.isfile('''gtklist.h'''):
        headers.append('''gtklist.h''')

    return headers

def extract_xml():
    """
    Extract translation strings from XML based, keys, mime and desktop
    files. Own XML files parsing and custom translation marks.
    """
    HolidaysParse('../data/holidays.xml.in', '_name')
    TipsParse('../data/tips.xml.in', '_tip')
    XmlParse('../data/gramps.xml.in', '_comment')
    XmlParse('../data/gramps.appdata.xml.in', '_p')
    DesktopParse('../data/gramps.desktop.in')
    KeyParse('../data/gramps.keys.in', '_description')

def create_template():
    """
    Create a new file for template, if it does not exist.
    """
    with open('gramps.pot', 'w') as template:
        pass

def extract_glade():
    """
    Extract messages from a temp file with all .glade
    """
    if not os.path.isfile('gramps.pot'):
        create_template()

    listing('glade.txt', ['.glade'])
    os.system('''%(xgettext)s -F --add-comments -j -L Glade '''
              '''--from-code=UTF-8 -o gramps.pot --files-from=glade.txt'''
             % {'xgettext': xgettextCmd}
             )

def extract_gtkbuilder():
    """
    Temp workaround for xgettext bug (< gettext 0.18.3)
    https://savannah.gnu.org/bugs/index.php?29216
    See bug reports #6595, #5621
    """

    from xml.etree import ElementTree

    '''
    <?xml version="1.0" encoding="UTF-8"?>
    <interface>
    <!-- interface-requires gtk+ 3.0 -->

    <object class="GtkListStore" id="model1">
    <columns>
      <!-- column-name gchararray -->
      <column type="gchararray"/>
    </columns>
    <data>
      <row>
        <col id="0" translatable="yes">All rules must apply</col>
      </row>
      <row>
        <col id="0" translatable="yes">At least one rule must apply</col>
      </row>
      <row>
        <col id="0" translatable="yes">Exactly one rule must apply</col>
      </row>
    </data>
  </object>

    msgid "All rules must apply"
    msgid "At least one rule must apply"
    msgid "Exactly one rule must apply"
    '''

    files = ['../gramps/plugins/importer/importgedcom.glade', '../gramps/gui/glade/rule.glade']
    with open('gtklist.h', 'w') as temp:
        for filename in files:
            tree = ElementTree.parse(filename)
            root = tree.getroot()
            for line in root.iter():
                att = line.attrib
                if att == {'id': '0', 'translatable': 'yes'}:
                    col = 'char *s = N_("%s");\n' % line.text
                    temp.write(col)
            root.clear()

    print ('Wrote gtklist.h')

def retrieve():
    """
    Extract messages from all files used by Gramps (python, glade, xml)
    """
    extract_xml()

    extract_gtkbuilder()

    create_template()

    create_filesfile()
    listing('python.txt', ['.py', '.py.in'])

    # additional keywords must always be kept in sync with those in genpot.sh
    os.system('''%(xgettext)s -F -c -j --directory=./ -d gramps '''
              '''-L Python -o gramps.pot --files-from=python.txt '''
              '''--debug --keyword=_ --keyword=ngettext '''
              '''--keyword=_T_ --keyword=trans_text '''
              '''--keyword=sgettext --from-code=UTF-8''' % {'xgettext': xgettextCmd}
             )

    extract_glade()

    # C format header (.h extension)
    for h in headers():
        print ('xgettext for %s' % h)
        os.system('''%(xgettext)s -F --add-comments -j -o gramps.pot '''
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
            print ('Remove %(head)s' % {'head': h})

    if os.path.isfile('python.txt'):
        os.unlink('python.txt')
        print ("Remove 'python.txt'")

    if os.path.isfile('glade.txt'):
        os.unlink('glade.txt')
        print ("Remove 'glade.txt'")

    if os.path.isfile('tmpfiles'):
        os.unlink('tmpfiles')
        print ("Remove 'tmpfiles'")

def merge(args):
    """
    Merge messages with 'gramps.pot'
    """
    for arg in args:
        if arg == 'all':
            continue
        print ('Merge %(lang)s with current template' % {'lang': arg})
        os.system('''%(msgmerge)s -U %(lang)s gramps.pot''' \
                    % {'msgmerge': msgmergeCmd, 'lang': arg})
        print ("Updated file: '%(lang)s'." % {'lang': arg})

def check(args):
    """
    Check the translation file
    """
    for arg in args:
        if arg == 'all':
            continue
        print ("Checked file: '%(lang.po)s'. See '%(txt)s.txt'." \
                    % {'lang.po': arg, 'txt': arg[:-3]})
        os.system('''%(python)s ./check_po -s %(lang.po)s > %(lang)s.txt''' \
                    % {'python': pythonCmd, 'lang.po': arg, 'lang': arg[:-3]})
        os.system('''%(msgfmt)s -c -v %(lang.po)s'''
                    % {'msgfmt': msgfmtCmd, 'lang.po': arg})

def untranslated(arg):
    """
    List untranslated messages
    """
    os.system('''%(msgattrib)s --untranslated %(lang.po)s''' % {'msgattrib': msgattribCmd, 'lang.po': arg[0]})

def fuzzy(arg):
    """
    List fuzzy messages
    """
    os.system('''%(msgattrib)s --only-fuzzy --no-obsolete %(lang.po)s''' % {'msgattrib': msgattribCmd, 'lang.po': arg[0]})

if __name__ == "__main__":
    main()
