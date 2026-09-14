#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012       Craig Anderson
# Copyright (C) 2026       Eduard Ralph
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
Pango attribute-list helper for the Cairo docgen (:mod:`libcairodoc`).

Split out so the paragraph-split re-indexing can be unit tested without
importing the GUI-entangled :mod:`libcairodoc` module (which pulls in
``gramps.gui`` and therefore Gdk at import time).  This module only needs
Pango, which does not require a display.
"""

# -------------------------------------------------------------------------
#
# Pango modules
#
# -------------------------------------------------------------------------
from gi.repository import Pango


# -------------------------------------------------------------------------
#
# Attribute re-indexing
#
# -------------------------------------------------------------------------
def reindex_split_attrlist(attrlist, index):
    """
    Rebase a paragraph's Pango attribute list onto the second part produced
    when the paragraph is split at plaintext byte offset *index* (bug 6250).

    *index* is a byte offset into the **parsed plaintext** (the Pango
    ``start_index``/``end_index`` contract), so the result is correct
    regardless of how the source markup serialised characters that are
    escaped in markup (``&``, ``<``, ``>``).

    Returns a fresh :class:`Pango.AttrList` in which every style run that
    extends past *index* survives, with its offsets expressed relative to the
    second part's plaintext:

    * a run starting at or after the split has both offsets shifted by
      ``index``;
    * a run straddling the split (or starting exactly at it) is clamped to
      start at 0;
    * a run lying entirely before the split (``end_index <= index``) is
      dropped.

    This replaces the obsolete markup re-serialisation workaround that
    miscounted escaped entities: ``get_iterator()`` is introspectable again,
    so the already-parsed runs are re-indexed directly.
    """
    newattrlist = Pango.AttrList()
    if attrlist is None:
        return newattrlist

    iterator = attrlist.get_iterator()
    seen = set()
    while True:
        for attr in iterator.get_attrs():
            # The iterator reports an attribute in every segment it spans, so
            # collapse the repeats and insert each run exactly once.
            key = (int(attr.klass.type), attr.start_index, attr.end_index)
            if key in seen:
                continue
            seen.add(key)
            if attr.end_index <= index:
                # Run lies entirely in the first part: it has no presence in
                # the second part, so drop it.
                continue
            newattr = attr.copy()
            # Clamp a straddling run's start to the start of the second part.
            newattr.start_index = max(attr.start_index - index, 0)
            newattr.end_index = attr.end_index - index
            newattrlist.insert(newattr)
        if not iterator.next():
            break
    return newattrlist
