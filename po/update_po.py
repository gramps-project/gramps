#! /usr/bin/env python3
#
# update_po - a gramps tool to update translations
#
# Copyright (C) 2006-2006  Kees Bakker
# Copyright (C) 2006       Brian Matherly
# Copyright (C) 2008       Stephen George
# Copyright (C) 2012
# Copyright (C) 2020       Nick Hall
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
from tokenize import tokenize, STRING, COMMENT, NL, TokenError

# Windows OS

if sys.platform in ["linux", "linux2", "darwin", "cygwin"] or shutil.which("msgmerge"):
    msgmergeCmd = "msgmerge"
    msgfmtCmd = "msgfmt"
    msgattribCmd = "msgattrib"
    xgettextCmd = "xgettext"
    pythonCmd = os.path.join(sys.prefix, "bin", "python3")
elif sys.platform == "win32":
    # GetText Win 32 obtained from http://gnuwin32.sourceforge.net/packages/gettext.htm
    # ....\gettext\bin\msgmerge.exe needs to be on the path
    msgmergeCmd = os.path.join(
        "C:", "Program Files(x86)", "gettext", "bin", "msgmerge.exe"
    )
    msgfmtCmd = os.path.join("C:", "Program Files(x86)", "gettext", "bin", "msgfmt.exe")
    msgattribCmd = os.path.join(
        "C:", "Program Files(x86)", "gettext", "bin", "msgattrib.exe"
    )
    xgettextCmd = os.path.join(
        "C:", "Program Files(x86)", "gettext", "bin", "xgettext.exe"
    )
    pythonCmd = os.path.join(sys.prefix, "bin", "python.exe")

# Others OS

elif sys.platform in ["linux", "linux2", "darwin", "cygwin"]:
    msgmergeCmd = "msgmerge"
    msgfmtCmd = "msgfmt"
    msgattribCmd = "msgattrib"
    xgettextCmd = "xgettext"
    pythonCmd = os.path.join(sys.prefix, "bin", "python3")
else:
    print("Found platform %s, OS %s" % (sys.platform, os.name))
    print("Update PO ERROR: unknown system, don't know msgmerge, ... commands")
    sys.exit(0)

# List of available languages, useful for grouped actions

# need files with po extension
LANG = [file for file in os.listdir(".") if file.endswith(".po")]
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
        print("\n====='msgmerge'=(merge our translation)================\n")
        os.system("""%(program)s -V""" % {"program": msgmergeCmd})
    except:
        print(
            "Please, install %(program)s for updating your translation"
            % {"program": msgmergeCmd}
        )

    try:
        print("\n==='msgfmt'=(format our translation for installation)==\n")
        os.system("""%(program)s -V""" % {"program": msgfmtCmd})
    except:
        print(
            "Please, install %(program)s for checking your translation"
            % {"program": msgfmtCmd}
        )

    try:
        print("\n===='msgattrib'==(list groups of messages)=============\n")
        os.system("""%(program)s -V""" % {"program": msgattribCmd})
    except:
        print(
            "Please, install %(program)s for listing groups of messages"
            % {"program": msgattribCmd}
        )

    try:
        print("\n===='xgettext' =(generate a new template)==============\n")
        os.system("""%(program)s -V""" % {"program": xgettextCmd})
    except:
        print(
            "Please, install %(program)s for generating a new template"
            % {"program": xgettextCmd}
        )

    try:
        print("\n=================='python'=============================\n")
        os.system("""%(program)s -V""" % {"program": pythonCmd})
    except:
        print("Please, install python")


def main():
    """
    The utility for handling translation stuff.
    What is need by Gramps, nothing more.
    """

    parser = ArgumentParser(
        description="This program generates a new template and "
        "also provides some common features.",
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        dest="test",
        default=True,
        help="test if 'python' and 'gettext' are properly installed",
    )

    parser.add_argument(
        "-x",
        "--xml",
        action="store_true",
        dest="xml",
        default=False,
        help="extract messages from xml based file formats",
    )
    parser.add_argument(
        "-g",
        "--glade",
        action="store_true",
        dest="glade",
        default=False,
        help="extract messages from glade file format only",
    )
    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        dest="clean",
        default=False,
        help="remove created files",
    )
    parser.add_argument(
        "-p",
        "--pot",
        action="store_true",
        dest="catalog",
        default=False,
        help="create a new catalog",
    )

    update = parser.add_argument_group("Update", "Maintenance around translations")

    # need at least one argument (sv.po, de.po, etc ...)

    # lang.po files maintenance
    update.add_argument(
        "-m", dest="merge", choices=LANG, help="merge lang.po files with last catalog"
    )

    update.add_argument("-k", dest="check", choices=LANG, help="check lang.po files")

    # testing stage
    trans = parser.add_argument_group(
        "Translation", "Display content of translations file"
    )

    # need one argument (eg, de.po)

    trans.add_argument(
        "-u",
        dest="untranslated",
        choices=[file for file in os.listdir(".") if file.endswith(".po")],
        help="list untranslated messages",
    )
    trans.add_argument(
        "-f",
        dest="fuzzy",
        choices=[file for file in os.listdir(".") if file.endswith(".po")],
        help="list fuzzy messages",
    )

    args = parser.parse_args()
    namespace, extra = parser.parse_known_args()

    if args.test:
        tests()

    if args.xml:
        extract_xml()

    if args.glade:
        create_filesfile()
        extract_glade()
        if os.path.isfile("tmpfiles"):
            os.unlink("tmpfiles")

    if args.catalog:
        retrieve()

    if args.clean:
        clean()

    if args.merge:
        # retrieve() windows os?
        if sys.argv[2:] == ["all"]:
            sys.argv[2:] = LANG
        merge(sys.argv[2:])

    if args.check:
        # retrieve() windows os?
        if sys.argv[2:] == ["all"]:
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
    topdir = os.path.normpath(os.path.join(dir, "..", "gramps"))
    lentopdir = len(topdir)
    with open("POTFILES.in") as f:
        infiles = dict(
            ["../" + file.strip(), None]
            for file in f
            if file.strip() and not file[0] == "#"
        )

    with open("POTFILES.skip") as f:
        notinfiles = dict(
            ["../" + file.strip(), None] for file in f if file and not file[0] == "#"
        )

    for dirpath, dirnames, filenames in os.walk(topdir):
        root, subdir = os.path.split(dirpath)
        if subdir.startswith("."):
            # don't continue in this dir
            dirnames[:] = []
            continue
        for dirname in dirnames:
            # Skip hidden and system directories:
            if dirname.startswith(".") or dirname in ["po", "locale"]:
                dirnames.remove(dirname)
        # add the files which are python or glade files
        # if the directory does not exist or is a link, do nothing
        if not os.path.isdir(dirpath) or os.path.islink(dirpath):
            continue

        for filename in os.listdir(dirpath):
            name = os.path.split(filename)[1]
            if name.endswith(".py") or name.endswith(".glade"):
                full_filename = os.path.join(dirpath, filename)
                # Skip the file if in POTFILES.skip
                if full_filename[lentopdir:] in notinfiles:
                    infiles["../gramps" + full_filename[lentopdir:]] = None
    # now we write out all the files in form ../gramps/filename
    with open("tmpfiles", "w") as f:
        for file in sorted(infiles.keys()):
            f.write(file)
            f.write("\n")


def listing(name, extensionlist):
    """
    List files according to extensions.
    Parsing from a textual file (gramps) is faster and easy for maintenance.
    Like POTFILES.in and POTFILES.skip
    """

    with open("tmpfiles") as f:
        files = [file.strip() for file in f if file and not file[0] == "#"]

    with open(name, "w") as temp:
        for entry in files:
            for ext in extensionlist:
                if entry.endswith(ext):
                    temp.write(entry)
                    temp.write("\n")
                    break


def headers():
    """
    Look at existing C file format headers.
    Generated by 'intltool-extract' but want to get rid of this
    dependency (perl, just a set of tools).
    """
    headers = []

    # in.h; extract_xml
    if os.path.isfile("""fragments.pot"""):
        headers.append("""fragments.pot""")

    return headers


def extract_xml():
    """
    Extract translation strings from XML based, mime and desktop files.
    Uses custom ITS rules found in the po/its directory.
    """
    if not os.path.isfile("gramps.pot"):
        create_template()

    for input_file in [
        "../data/holidays.xml",
        "../data/tips.xml",
        "../data/org.gramps_project.Gramps.xml.in",
        "../data/org.gramps_project.Gramps.metainfo.xml.in",
        "../data/org.gramps_project.Gramps.desktop.in",
    ]:
        os.system(
            (
                "GETTEXTDATADIR=. %(xgettext)s -F -j "
                "-o gramps.pot --from-code=UTF-8 %(inputfile)s"
            )
            % {"xgettext": xgettextCmd, "inputfile": input_file}
        )
        print(input_file)


def create_template():
    """
    Create a new file for template, if it does not exist.
    """
    with open("gramps.pot", "w") as template:
        pass


def extract_glade():
    """
    Extract messages from a temp file with all .glade
    """
    if not os.path.isfile("gramps.pot"):
        create_template()

    listing("glade.txt", [".glade"])
    os.system(
        """%(xgettext)s -F --add-comments -j -L Glade """
        """--from-code=UTF-8 -o gramps.pot --files-from=glade.txt"""
        % {"xgettext": xgettextCmd}
    )


def xml_fragments():
    """search through the file for xml fragments that contain the
    'translate="yes">string<' pattern.  These need to be added to the message
    catalog"""
    with open("tmpfiles") as __f:
        files = [
            file.strip()
            for file in __f
            if file and not (file[0] == "#") and file.endswith(".py\n")
        ]
        print("Checking for XML fragments in Python files")
        modop = int(len(files) / 20)
    wfp = open("fragments.pot", "w", encoding="utf-8")
    wfp.write('msgid ""\n')
    wfp.write('msgstr ""\n')
    wfp.write('"Content-Type: text/plain; charset=UTF-8\\n"\n\n')
    for indx, filename in enumerate(files):
        if not indx % modop:
            print(int(indx / len(files) * 100), end="\r")
        fp = open(filename, "rb")
        try:
            tokens = tokenize(fp.readline)
            in_string = False
            for _token, _text, _start, _end, _line in tokens:
                if _text.startswith('"""') or _text.startswith("'''"):
                    _text = _text[3:]
                elif _text.startswith('"') or _text.startswith("'"):
                    _text = _text[1:]
                if _text.endswith('"""') or _text.endswith("'''"):
                    _text = _text[:-3]
                elif _text.endswith('"') or _text.endswith("'"):
                    _text = _text[:-1]
                if _token == STRING and not in_string:
                    in_string = True
                    line_no = _start[0]
                    text = _text
                    continue
                elif _token == STRING and in_string:
                    text += _text
                    continue
                elif _token == COMMENT or _token == NL and in_string:
                    # need to ignore comments and concatinate strings
                    _ml = True
                    continue
                elif in_string:
                    in_string = False
                    end = 0
                    # _find_message_in_xml(text)
                    while True:
                        fnd = text.find('translatable="yes">', end)
                        if fnd == -1:
                            break
                        end = text.find("<", fnd)
                        if end == -1:
                            print(
                                "\nBad xml fragment '%s' at %s line %d"
                                % (text[fnd:], filename, _start[0])
                            )
                            break
                        msg = text[fnd + 19 : end]
                        if "%s" in msg or (msg.startswith("{") and msg.endswith("}")):
                            print(
                                "\n#: %s:%d  Are you sure you want to "
                                'translate the "%%s"???' % (filename, line_no)
                            )
                            break
                        wfp.write(
                            '#: %s:%d\nmsgid "%s"\nmsgstr ""\n'
                            % (filename, line_no, msg)
                        )
        except TokenError as e:
            print(
                "\n%s: %s, line %d, column %d"
                % (e.args[0], filename, e.args[1][0], e.args[1][1]),
                file=sys.stderr,
            )
        finally:
            fp.close()
    wfp.close()


def retrieve():
    """
    Extract messages from all files used by Gramps (python, glade, xml)
    """
    create_template()

    create_filesfile()
    xml_fragments()

    listing("python.txt", [".py", ".py.in"])

    # additional keywords must always be kept in sync with those in genpot.sh
    os.system(
        """%(xgettext)s -F --add-comments=Translators -j """
        """--directory=./ -d gramps -L Python """
        """-o gramps.pot --files-from=python.txt --debug """
        """--keyword=_ --keyword=_:1,2c """
        """--keyword=_T_ --keyword=_T_:1,2c """
        """--keyword=trans_text --keyword=trans_text:1,2c """
        """--keyword=ngettext --keyword=sgettext """
        """--from-code=UTF-8""" % {"xgettext": xgettextCmd}
    )

    extract_glade()
    extract_xml()

    # C format header (.h extension)
    for h in headers():
        print("xgettext for %s" % h)
        os.system(
            """%(xgettext)s -F --add-comments=Translators -j """
            """-o gramps.pot --keyword=N_ --from-code=UTF-8 %(head)s"""
            % {"xgettext": xgettextCmd, "head": h}
        )
    clean()


def clean():
    """
    Remove created files (C format headers, temp listings)
    """
    for h in headers():
        if os.path.isfile(h):
            os.unlink(h)
            print("Remove %(head)s" % {"head": h})

    if os.path.isfile("python.txt"):
        os.unlink("python.txt")
        print("Remove 'python.txt'")

    if os.path.isfile("glade.txt"):
        os.unlink("glade.txt")
        print("Remove 'glade.txt'")

    if os.path.isfile("tmpfiles"):
        os.unlink("tmpfiles")
        print("Remove 'tmpfiles'")


def merge(args):
    """
    Merge messages with 'gramps.pot'
    """
    for arg in args:
        if arg == "all":
            continue
        print("Merge %(lang)s with current template" % {"lang": arg})
        os.system(
            """%(msgmerge)s -U %(lang)s gramps.pot"""
            % {"msgmerge": msgmergeCmd, "lang": arg}
        )
        print("Updated file: '%(lang)s'." % {"lang": arg})


def check(args):
    """
    Check the translation file
    """
    for arg in args:
        if arg == "all":
            continue
        print(
            "Checked file: '%(lang.po)s'. See '%(txt)s.txt'."
            % {"lang.po": arg, "txt": arg[:-3]}
        )
        os.system(
            """%(python)s ./check_po -s %(lang.po)s > %(lang)s.txt"""
            % {"python": pythonCmd, "lang.po": arg, "lang": arg[:-3]}
        )
        os.system(
            """%(msgfmt)s -c -v %(lang.po)s""" % {"msgfmt": msgfmtCmd, "lang.po": arg}
        )


def untranslated(arg):
    """
    List untranslated messages
    """
    os.system(
        """%(msgattrib)s --untranslated %(lang.po)s"""
        % {"msgattrib": msgattribCmd, "lang.po": arg[0]}
    )


def fuzzy(arg):
    """
    List fuzzy messages
    """
    os.system(
        """%(msgattrib)s --only-fuzzy --no-obsolete %(lang.po)s"""
        % {"msgattrib": msgattribCmd, "lang.po": arg[0]}
    )


if __name__ == "__main__":
    main()
