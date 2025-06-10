#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012,2020,2025  Nick Hall
# Copyright (C) 2012            Rob G. Healey
# Copyright (C) 2012            Benny Malengier
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

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
import subprocess
import codecs
import os
import sys
from shutil import copy2, copytree, ignore_patterns, rmtree

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


# ------------------------------------------------------------------------
#
# GrampsBuildHook class
#
# ------------------------------------------------------------------------
class GrampsBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):

        build_dir = os.path.join(self.root, "build")
        if os.path.isdir(build_dir):
            rmtree(build_dir)

        self.build_trans(build_dir)
        self.build_intl(build_dir)
        if sys.platform != "win32":
            self.build_man(build_dir)
        self.copy_files(build_dir)

    def get_linguas(self):
        """
        Read the po/LINGUAS file to get a list of all linguas.
        """
        all_linguas = []
        with open(
            os.path.join(self.root, "po", "LINGUAS"), "r", encoding="utf-8"
        ) as linguas:
            for line in linguas:
                line = line.split("#", maxsplit=1)[0]
                all_linguas.extend(line.split())
        return all_linguas

    def build_trans(self, build_dir):
        """
        Translate the language files into gramps.mo
        """
        self.app.display_info(" Compiling translations ...")
        for lang in self.get_linguas():
            po_file = os.path.join(self.root, "po", lang + ".po")
            mo_file = os.path.join(
                build_dir, "share", "locale", lang, "LC_MESSAGES", "gramps.mo"
            )

            mo_dir = os.path.dirname(mo_file)
            os.makedirs(mo_dir, exist_ok=True)

            if newer(po_file, mo_file):
                self.app.display_info(f"  - {lang}")
                cmd = ["msgfmt", po_file, "-o", mo_file]
                if subprocess.call(cmd) != 0:
                    if os.path.exists(mo_file):
                        os.remove(mo_file)
                    msg = "ERROR: Building language translation files failed."
                    ask = msg + "\n Continue building y/n [y] "
                    reply = input(ask)
                    if reply in ["n", "N"]:
                        self.app.abort(msg)

    def build_intl(self, build_dir):
        """
        Merge translation files into desktop and mime files
        """
        self.app.display_info(" Merging metadata files ...")
        merge_files = (
            ("org.gramps_project.Gramps.desktop", "applications", "--desktop"),
            (
                "org.gramps_project.Gramps.xml",
                os.path.join("mime", "packages"),
                "--xml",
            ),
            ("org.gramps_project.Gramps.metainfo.xml", "metainfo", "--xml"),
        )

        for filename, target, option in merge_files:
            filenamelocal = os.path.join(self.root, "data", filename)
            newfile = os.path.join(build_dir, "share", target, filename)
            newdir = os.path.dirname(newfile)
            os.makedirs(newdir, exist_ok=True)
            self.app.display_info(f"  - {filename}")
            self.merge(filenamelocal + ".in", newfile, option)

    def merge(self, in_file, out_file, option, po_dir="po"):
        """
        Run the msgfmt command.
        """
        po_dir = os.path.join(self.root, po_dir)
        if not os.path.exists(out_file) and os.path.exists(in_file):
            cmd = [
                "msgfmt",
                option,
                "--template",
                in_file,
                "-d",
                po_dir,
                "-o",
                out_file,
            ]
            if subprocess.call(cmd, env={**os.environ, "GETTEXTDATADIR": po_dir}) != 0:
                msg = (
                    "ERROR: %s was not merged into the translation files!\n" % out_file
                )
                self.app.abort(msg)

    def build_man(self, build_dir):
        """
        Compresses Gramps manual files
        """
        self.app.display_info(" Processing manual pages ...")
        for man_dir, dirs, files in os.walk(os.path.join(self.root, "data", "man")):
            if "gramps.1.in" in files:
                filename = os.path.join(man_dir, "gramps.1.in")
                head, tail = os.path.split(man_dir)
                if tail == "man":
                    lang = ""
                else:
                    lang = tail
                newdir = os.path.join(build_dir, "share", "man", lang, "man1")
                os.makedirs(newdir, exist_ok=True)

                newfile = os.path.join(newdir, "gramps.1")
                subst_vars = (("@VERSION@", self.metadata.version),)
                substitute_variables(filename, newfile, subst_vars)

                src = "gramps.1"
                if "NO_COMPRESS_MANPAGES" not in os.environ:
                    import gzip

                    src += ".gz"
                    man_file_gz = os.path.join(newdir, src)
                    if os.path.exists(man_file_gz):
                        if newer(filename, man_file_gz):
                            os.remove(man_file_gz)
                        else:
                            filename = False
                            os.remove(newfile)

                    if filename:
                        # Binary io, so open is OK
                        with (
                            open(newfile, "rb") as f_in,
                            gzip.open(man_file_gz, "wb") as f_out,
                        ):
                            f_out.writelines(f_in)
                            self.app.display_info(f"  - {lang}/{src}")

                        os.remove(newfile)
                        filename = False

    def copy_files(self, build_dir):
        """
        Copy shared data files into the correct file structure.
        """
        source = os.path.join(self.root, "images")
        destination = os.path.join(build_dir, "share", "gramps", "images")
        ignore = ignore_patterns("apps", "mimetypes", "source", "128x128", "256x256")
        copytree(source, destination, ignore=ignore)

        source = os.path.join(self.root, "images", "hicolor")
        destination = os.path.join(build_dir, "share", "icons", "hicolor")
        ignore = ignore_patterns("actions", "source")
        copytree(source, destination, ignore=ignore)

        source = os.path.join(self.root, "example")
        destination = os.path.join(build_dir, "share", "doc", "gramps", "example")
        copytree(source, destination)

        source = os.path.join(self.root, "data", "css")
        destination = os.path.join(build_dir, "share", "gramps", "css")
        copytree(source, destination)

        doc_files = [
            "AUTHORS",
            "COPYING",
            "FAQ",
            "INSTALL",
            "NEWS",
            "README.md",
            "TODO",
        ]
        for file in doc_files:
            source = os.path.join(self.root, file)
            destination = os.path.join(build_dir, "share", "doc", "gramps", file)
            copy2(source, destination)

        data_files = [
            "gramps.css",
            "grampsxml.rng",
            "grampsxml.dtd",
            "gramps_canonicalize.xsl",
            "authors.xml",
            "holidays.xml",
            "lds.xml",
            "papersize.xml",
            "tips.xml",
        ]
        for file in data_files:
            source = os.path.join(self.root, "data", file)
            destination = os.path.join(build_dir, "share", "gramps", file)
            copy2(source, destination)


# ------------------------------------------------------------------------
#
# Utility functions
#
# ------------------------------------------------------------------------


def newer(source, target):
    """
    Determines if a target file needs to be rebuilt.

    Returns True if the target file doesn't exist or if the source file is
    newer than the target file.
    """
    if not os.path.exists(target):
        return True
    return os.path.getmtime(source) > os.path.getmtime(target)


def substitute_variables(filename_in, filename_out, subst_vars):
    """
    Substitute variables in a file.
    """
    f_in = codecs.open(filename_in, encoding="utf-8")
    f_out = codecs.open(filename_out, encoding="utf-8", mode="w")
    for line in f_in:
        for variable, substitution in subst_vars:
            line = line.replace(variable, substitution)
        f_out.write(line)
    f_in.close()
    f_out.close()
