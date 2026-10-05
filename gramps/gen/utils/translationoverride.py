# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Doug Blank
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

"""
User-defined translation overrides.

Lets a user replace a specific translated string (e.g. a calendar month
lexeme such as "Nisan") with their own preferred spelling, without editing
any installed .po/.mo file. Overrides are stored in a single JSON file
that is independent of the Gramps version directory, so it survives
upgrades, and are shaped like a PO/Weblate translation unit
(language, context, msgid, msgstr) to keep the door open for future
interoperability with Gramps' Weblate-hosted translations.
"""

from __future__ import annotations

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import json
import logging
import os

LOG = logging.getLogger(".gen.utils.translationoverride")


def _default_filename() -> str:
    """
    Return the default custom translations file path.

    Imported lazily to avoid a circular import: gramps.gen.const imports
    gramps.gen.utils.grampslocale, which imports this module.
    """
    from ..const import CUSTOM_TRANSLATIONS

    return CUSTOM_TRANSLATIONS


def _primary_subtag(lang: str) -> str:
    """
    Return the primary language subtag of a language code, e.g. "fr" for
    both "fr" and "fr_FR.UTF-8".
    """
    return lang.split(".")[0].split("_")[0].lower()


def load_custom_translations(filename: str | None = None) -> list[dict]:
    """
    Load the raw list of custom translation override entries from disk.

    :returns: the entries found in the file, or an empty list if the file
              doesn't exist or can't be parsed as a JSON list.
    :rtype: list[dict]
    """
    if filename is None:
        filename = _default_filename()
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, "r", encoding="utf-8") as fp:
            data = json.load(fp)
    except (OSError, ValueError) as err:
        LOG.warning("Unable to read custom translations file %s: %s", filename, err)
        return []
    if not isinstance(data, list):
        LOG.warning(
            "Custom translations file %s does not contain a JSON list; ignoring",
            filename,
        )
        return []
    return data


def save_custom_translations(entries: list[dict], filename: str | None = None) -> None:
    """
    Write the list of custom translation override entries to disk.

    :param entries: entries with "language", "context", "msgid", and
                     "msgstr" keys.
    :type entries: list[dict]
    """
    if filename is None:
        filename = _default_filename()
    with open(filename, "w", encoding="utf-8") as fp:
        json.dump(entries, fp, indent=2, ensure_ascii=False)


def get_overrides_for_language(
    active_lang: str, filename: str | None = None
) -> dict[tuple[str, str], str]:
    """
    Resolve the custom translation entries that apply to one active
    language.

    An entry whose "language" is an exact match for ``active_lang`` takes
    precedence over one that only matches the primary language subtag
    (e.g. an "en_GB" entry wins over an "en" entry when ``active_lang``
    is "en_GB").

    :param active_lang: the language code of the translation currently in
                         use, e.g. "fr_FR" or "en".
    :type active_lang: str
    :returns: mapping of (context, msgid) to the user's replacement text,
              ready to pass to
              :meth:`~gramps.gen.utils.grampstranslation.TranslationOverrideMixin.set_overrides`.
    :rtype: dict[tuple[str, str], str]
    """
    active_subtag = _primary_subtag(active_lang)
    exact: dict[tuple[str, str], str] = {}
    by_subtag: dict[tuple[str, str], str] = {}
    for entry in load_custom_translations(filename):
        try:
            lang = entry["language"]
            context = entry.get("context", "")
            msgid = entry["msgid"]
            msgstr = entry["msgstr"]
        except (KeyError, TypeError):
            LOG.warning("Skipping malformed custom translation entry: %r", entry)
            continue
        key = (context, msgid)
        if lang == active_lang:
            exact[key] = msgstr
        elif _primary_subtag(lang) == active_subtag:
            by_subtag[key] = msgstr
    return {**by_subtag, **exact}
