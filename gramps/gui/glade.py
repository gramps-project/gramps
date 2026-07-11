#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Gerald Britton <gerald.britton@gmail.com>
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

# ------------------------------------------------------------------------
#
# Glade
#
# ------------------------------------------------------------------------

"""
Glade file operations

This module exports the Glade class.

"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
import sys
import os
import re
import xml.etree.ElementTree as ET
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GLADE_DIR, GRAMPS_LOCALE as glocale
from gramps.gen.constfunc import is_quartz

# ------------------------------------------------------------------------
#
# Glade accelerator scanning/override support
#
# ------------------------------------------------------------------------

# Only the modifiers actually used by <accelerator> tags in Gramps' glade
# files need to be here; GDK_META_MASK covers the mac remap below, which
# runs before this and turns GDK_CONTROL_MASK into GDK_META_MASK in the
# text.
_GDK_MASK_TOKENS = {
    "GDK_SHIFT_MASK": "<Shift>",
    "GDK_CONTROL_MASK": "<Primary>",
    "GDK_META_MASK": "<Primary>",
    "GDK_MOD1_MASK": "<Alt>",
    "GDK_SUPER_MASK": "<Super>",
    "GDK_HYPER_MASK": "<Hyper>",
}


def _glade_modifiers_to_prefix(modifiers):
    """Convert a glade `modifiers="GDK_X_MASK|GDK_Y_MASK"` attribute value
    into an accelerator-string modifier prefix, e.g. '<Primary><Shift>'.
    """
    tokens = []
    for name in modifiers.split("|"):
        name = name.strip()
        if name in _GDK_MASK_TOKENS:
            tokens.append(_GDK_MASK_TOKENS[name])
    return "".join(tokens)


def _find_glade_label(obj):
    """Find a human-readable label for a glade <object>: prefer its
    tooltip_text property, fall back to its accessible-name.
    """
    for name in ("tooltip_text", "AtkObject::accessible-name"):
        prop = obj.find('.//property[@name="%s"]' % name)
        if prop is not None and prop.text:
            return prop.text
    return None


def iter_glade_accelerators(xml_text):
    """Yield (object_id, accel, label) for every <accelerator> element in
    a glade XML string.

    :param xml_text: the glade file contents, already read from disk
    :type xml_text: str
    :returns: object_id is the id of the accelerator's enclosing
        <object>; accel is a Gtk accelerator string, e.g. '<Primary>a';
        label is pulled from that object's tooltip or accessible-name,
        falling back to the raw object id
    :rtype: Iterator[tuple[str, str, str]]
    """
    tree = ET.fromstring(xml_text)
    for obj in tree.iter("object"):
        obj_id = obj.get("id")
        if not obj_id:
            continue
        for accel_el in obj.findall("accelerator"):
            key = accel_el.get("key")
            if not key:
                continue
            accel = _glade_modifiers_to_prefix(accel_el.get("modifiers", "")) + key
            label = _find_glade_label(obj) or obj_id
            yield obj_id, accel, label


_ACCEL_TOKEN_RE = re.compile(r"<[A-Za-z]+>")
_ACCEL_TOKEN_TO_MASK = {
    "<Shift>": "GDK_SHIFT_MASK",
    "<Primary>": "GDK_CONTROL_MASK",
    "<Control>": "GDK_CONTROL_MASK",
    "<Ctrl>": "GDK_CONTROL_MASK",
    "<Alt>": "GDK_MOD1_MASK",
    "<Super>": "GDK_SUPER_MASK",
    "<Hyper>": "GDK_HYPER_MASK",
    "<Meta>": "GDK_META_MASK",
}


def _accel_to_glade_key_modifiers(accel):
    """Convert an accelerator string like '<Primary><Shift>a' into the
    (key, modifiers) pair glade's <accelerator> attributes expect, e.g.
    ('a', 'GDK_CONTROL_MASK|GDK_SHIFT_MASK'). Pure string parsing -- does
    not touch Gtk/Gdk, so unlike Gtk.accelerator_parse() it's safe to call
    without a real display connection.

    :param accel: a Gtk accelerator string
    :type accel: str
    :returns: (key, modifiers), or (None, None) if accel has no key part
    :rtype: tuple[str | None, str | None]
    """
    key = _ACCEL_TOKEN_RE.sub("", accel)
    if not key:
        return None, None
    mask_names = []
    for token in _ACCEL_TOKEN_RE.findall(accel):
        mask = _ACCEL_TOKEN_TO_MASK.get(token)
        if mask and mask not in mask_names:
            mask_names.append(mask)
    return key, "|".join(mask_names)


def apply_glade_accel_overrides(xml_text, file_stem):
    """Rewrite <accelerator> key/modifiers attributes in a glade XML
    string to reflect saved user overrides, leaving everything else
    untouched.

    :param xml_text: the glade file contents
    :type xml_text: str
    :param file_stem: the glade file's name without extension, used as
        part of the action id namespace (see iter_glade_accelerators)
    :type file_stem: str
    :returns: the original text, unchanged, if there's no running
        application to read overrides from, or nothing to override;
        otherwise the rewritten XML
    :rtype: str
    """
    if "<accelerator" not in xml_text:
        return xml_text
    app = Gtk.Application.get_default()
    uimanager = getattr(app, "uimanager", None)
    if uimanager is None:
        return xml_text

    tree = ET.fromstring(xml_text)
    changed = False
    for obj in tree.iter("object"):
        obj_id = obj.get("id")
        if not obj_id:
            continue
        for accel_el in obj.findall("accelerator"):
            if not accel_el.get("key"):
                continue
            action_id = f"glade.{file_stem}.{obj_id}"
            override = uimanager.accel_dict.get(action_id)
            if not override:
                continue
            key, modifiers = _accel_to_glade_key_modifiers(override)
            if not key:
                continue
            accel_el.set("key", key)
            accel_el.set("modifiers", modifiers)
            changed = True
    if not changed:
        return xml_text
    return ET.tostring(tree, encoding="unicode")


# ------------------------------------------------------------------------
#
# Glade class. Derived from Gtk.Builder
#
# ------------------------------------------------------------------------


class Glade(Gtk.Builder):
    """
    Glade class: Manage glade files as Gtk.Builder objects
    """

    _ALLOWED_ATTRIBUTES = {
        "__toplevel",
        "__filename",
        "__dirname",
        "_Glade__toplevel",
        "_Glade__filename",
        "_Glade__dirname",
    }

    def __setattr__(self, name, value):
        if not hasattr(self, name) and name not in self._ALLOWED_ATTRIBUTES:
            raise AttributeError(f"Ad-hoc attribute {name} is not permitted.")
        super().__setattr__(name, value)

    def __init__(self, filename=None, dirname=None, toplevel=None, also_load=[]):
        """
        Class Constructor: Returns a new instance of the Glade class

        :type  filename: string or None
        :param filename: The name of the glade file to be used. Defaults to None
        :type  dirname: string or None
        :param dirname: The directory to search for the glade file. Defaults to
                    None which will cause a search for the file in the default
                    directory followed by the directory of the calling module.
        :type  toplevel: string or None
        :param toplevel: The toplevel object to search for in the glade file.
                     Defaults to None, which will cause a search for a toplevel
                     matching the supplied name.
        :type  also_load: list of strings
        :param also_load: Additional toplevel objects to load from the glade
                     file.  These are typically liststore or other objects
                     needed to operate the toplevel object.
                     Defaults to [] (empty list), which will not load
                     additional objects.
        :rtype:   object reference
        :returns:  reference to the newly-created Glade instance

        This operates in two modes; when no toplevel parameter is supplied,
        the entire Glade file is loaded. It is the responsibility of the user
        to make sure ALL toplevel objects are destroyed.

        When a toplevel parameter is supplied, only that object and any
        additional objects requested in the also_load parameter are loaded.
        The user only has to destroy the requested toplevel objects.
        """
        Gtk.Builder.__init__(self)
        self.set_translation_domain(glocale.get_localedomain())

        filename_given = filename is not None
        dirname_given = dirname is not None

        # if filename not given, use module name to derive it

        if not filename_given:
            filename = sys._getframe(1).f_code.co_filename
            filename = os.path.basename(filename)
            filename = filename.rpartition(".")[0] + ".glade"
            filename = filename.lstrip("_").lower()

        # if dirname not given, use current directory

        if not dirname_given:
            dirname = sys._getframe(1).f_code.co_filename
            dirname = os.path.dirname(dirname)

        # try to find the glade file

        if filename_given and dirname_given:  # both given -- use them
            path = os.path.join(dirname, filename)

        elif filename_given:  # try default directory first
            path = os.path.join(GLADE_DIR, filename)
            if not os.path.exists(path):  # then module directory
                path = os.path.join(dirname, filename)

        elif dirname_given:  # dirname given -- use it
            path = os.path.join(dirname, filename)

        # neither filename nor dirname given.  Try:
        # 1. derived filename in default directory
        # 2. derived filename in module directory

        else:
            path = os.path.join(GLADE_DIR, filename)
            if not os.path.exists(path):
                path = os.path.join(dirname, filename)

        # try to build Gtk objects from glade file.  Let exceptions happen

        self.__dirname, self.__filename = os.path.split(path)
        file_stem = os.path.splitext(self.__filename)[0]

        # try to find the toplevel widget

        # toplevel is given
        if toplevel:
            loadlist = [toplevel] + also_load
            with open(path, "r", encoding="utf-8") as builder_file:
                data = builder_file.read()
                if is_quartz():
                    data = data.replace("GDK_CONTROL_MASK", "GDK_META_MASK")
                data = apply_glade_accel_overrides(data, file_stem)
                self.add_objects_from_string(data, loadlist)
            self.__toplevel = self.get_object(toplevel)
        # toplevel not given
        else:
            with open(path, "r", encoding="utf-8") as builder_file:
                data = builder_file.read()
                if is_quartz():
                    data = data.replace("GDK_CONTROL_MASK", "GDK_META_MASK")
                data = apply_glade_accel_overrides(data, file_stem)
                self.add_from_string(data)
            # first, use filename as possible toplevel widget name
            self.__toplevel = self.get_object(filename.rpartition(".")[0])

            # next try lowercase filename as possible widget name
            if not self.__toplevel:
                self.__toplevel = self.get_object(filename.rpartition(".")[0].lower())

                if not self.__toplevel:
                    # if no match found, search for first toplevel widget
                    for obj in self.get_objects():
                        if hasattr(obj, "get_toplevel"):
                            self.__toplevel = obj.get_toplevel()
                            break
                    else:
                        self.__toplevel = None

    @property
    def filename(self):
        """
        filename: return filename of glade file
        :rtype:   string
        :returns:  filename of glade file
        """
        return self.__filename

    @property
    def dirname(self):
        """
        dirname: return directory where glade file found
        :rtype:   string
        :returns:  directory where glade file found
        """
        return self.__dirname

    @property
    def toplevel(self):
        """
        toplevel: return toplevel object
        :rtype:   object
        :returns:  toplevel object
        """
        return self.__toplevel

    @toplevel.setter
    def toplevel(self, toplevel):
        self.__toplevel = self.get_object(toplevel)

    def get_child_object(self, value, toplevel=None):
        """
        get_child_object: search for a child object, by name, within a given
                          toplevel.  If no toplevel argument is supplied, use
                          the toplevel attribute for this instance
        :type  value: string
        :param value: The name of the child object to find
        :type  toplevel: string
        :param toplevel: The name of the toplevel object to us
        :rtype:   object
        :returns:  child object
        """
        if not toplevel:
            toplevel = self.__toplevel
            if not toplevel:
                raise ValueError("Top level object required")

        if isinstance(toplevel, str):
            toplevel = self.get_object(toplevel)

        # Simple Breadth-First Search

        queue = [toplevel]
        while queue:
            obj = queue.pop(0)
            obj_id = Gtk.Buildable.get_name(obj)
            if obj_id == value:
                return obj
            if hasattr(obj, "get_children"):
                queue += obj.get_children()

        return None
