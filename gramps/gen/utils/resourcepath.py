#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2013       John Ralls <jralls@ceridwen.us>
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
import sys
import os
import logging
LOG = logging.getLogger("ResourcePath")
_hdlr = logging.StreamHandler()
_hdlr.setFormatter(logging.Formatter(fmt="%(name)s.%(levelname)s: %(message)s"))
LOG.addHandler(_hdlr)

from ..constfunc import get_env_var

class ResourcePath:
    """
    ResourcePath is a singleton, meaning that only one of them is ever
    created.  At startup it finds the paths to Gramps's resource files and
    caches them for future use.

    It should be called only by const.py; other code should retrieve the
    paths from there.
    """
    instance = None
    def __new__(cls):
        if not cls.instance:
            cls.instance = super(ResourcePath, cls).__new__(cls)
            cls.instance.initialized = False

        return cls.instance

    def __init__(self):
        if self.initialized:
            return
        resource_file = os.path.join(os.path.abspath(os.path.dirname(
            __file__)), 'resource-path')
        installed = os.path.exists(resource_file)
        if installed:
            test_path = os.path.join("gramps", "authors.xml")
        else:
            test_path = os.path.join("data", "authors.xml")
        resource_path = None
        tmp_path = get_env_var('GRAMPS_RESOURCES')
        if (tmp_path and os.path.exists(os.path.join(tmp_path, test_path))):
            resource_path = tmp_path
        elif installed:
            try:
                with open(resource_file, encoding='utf-8',
                                errors='strict') as fp:
                    resource_path = fp.readline()
            except UnicodeError as err:
                LOG.exception("Encoding error while parsing resource path", err)
                sys.exit(1)
            except IOError as err:
                LOG.exception("Failed to open resource file", err)
                sys.exit(1)
            if not os.path.exists(os.path.join(resource_path, test_path)):
                LOG.error("Resource Path %s is invalid", resource_path)
                sys.exit(1)
        else:
            # Let's try to run from source without env['GRAMPS_RESOURCES']:
            resource_path = os.path.join(os.path.abspath(os.path.dirname(
                __file__)), '..', "..", "..")
            test_path = os.path.join("data", "authors.xml")
            if (not os.path.exists(os.path.join(resource_path, test_path))):
                LOG.error("Unable to determine resource path")
                sys.exit(1)

        resource_path = os.path.abspath(resource_path)
        if installed:
            self.locale_dir = os.path.join(resource_path, 'locale')
            self.data_dir = os.path.join(resource_path, 'gramps')
            self.image_dir = os.path.join(resource_path, 'gramps', 'images')
            self.doc_dir = os.path.join(resource_path, 'doc', 'gramps')

        else:
            self.locale_dir = os.path.join(resource_path, 'build', 'mo')
            self.image_dir = os.path.join(resource_path, 'images')
            self.data_dir = os.path.join(resource_path, 'data')
            self.doc_dir = os.path.join(resource_path, 'build', 'data')

        self.initialized = True


