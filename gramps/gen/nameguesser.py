#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025 Christina Rauscher
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

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
import logging

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .lib import Name, Surname
from .utils.db import preset_name
from .plug import PluginRegister, BasePluginManager
from .const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

LOG = logging.getLogger("gen.relationship")
LOG.addHandler(logging.StreamHandler())


# -------------------------------------------------------------------------
#
# NameGuesser
#
# -------------------------------------------------------------------------
class NameGuesser:
    """
    The name guesser guesses the names of a person based on their family members' names.
    """

    def fathers_surname_from_child(self, db, family):
        """
        Find a child and return their name for the father.
        """
        # for each child, find one with a last name
        name = Name()
        # the editor requires a surname
        name.add_surname(Surname())
        name.set_primary_surname(0)
        for ref in family.get_child_ref_list():
            child = db.get_person_from_handle(ref.ref)
            if child:
                preset_name(child, name)
                return name

        return name

    def mothers_surname_from_child(self, db, family):
        """
        Mother's surname cannot be guessed in the default locale, return empty name.
        """
        name = Name()
        # the editor requires a surname
        name.add_surname(Surname())
        name.set_primary_surname(0)

        return name

    def childs_surname(self, db, family):
        """
        Child inherits name from father.
        """
        name = Name()
        name.add_surname(Surname())
        name.set_primary_surname(0)
        father_handle = family.get_father_handle()
        if father_handle:
            father = db.get_person_from_handle(father_handle)
            preset_name(father, name)

        return name


# -------------------------------------------------------------------------
#
# define the default nameguesser
#
# -------------------------------------------------------------------------

__NAMEGUESSER_CLASS = None


def get_nameguesser(reinit=False, clocale=glocale):
    """
    Return the name guesser for the current language.

    If clocale is passed in (a GrampsLocale) then that language will be used.

    :param clocale: allow selection of the language
    :type clocale: a GrampsLocale instance

    """
    global __NAMEGUESSER_CLASS

    if __NAMEGUESSER_CLASS is None or reinit:
        lang = clocale.language[0]
        __NAMEGUESSER_CLASS = NameGuesser
        # If lang not set default to English name guesser
        # See if lang begins with en_, English_ or english_
        # If so return standard name guesser.
        if lang.startswith("en") or lang == "C":
            return __NAMEGUESSER_CLASS()
        # Set correct non English name guesser based on lang
        nameguesser_translation_found = False
        for plugin in PluginRegister.get_instance().nameguesser_plugins():
            if lang in plugin.lang_list:
                pmgr = BasePluginManager.get_instance()
                # The loaded module is put in variable mod
                mod = pmgr.load_plugin(plugin)
                if mod:
                    __NAMEGUESSER_CLASS = getattr(mod, plugin.nameguesserclass)
                    nameguesser_translation_found = True
                    break
        if not nameguesser_translation_found and len(
            PluginRegister.get_instance().nameguesser_plugins()
        ):
            LOG.warning(
                _(
                    "Name guesser not available for "
                    "language '%s'. Using 'english' instead."
                ),
                lang,
            )
    return __NAMEGUESSER_CLASS()
