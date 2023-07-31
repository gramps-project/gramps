#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008  Zsolt Foldvari
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

"""Text buffer subclassed from Gtk.TextBuffer handling :class:`.StyledText`."""

__all__ = [
    "ALLOWED_STYLES",
    "MATCH_START",
    "MATCH_END",
    "MATCH_FLAVOR",
    "MATCH_STRING",
    "StyledTextBuffer",
]

# -------------------------------------------------------------------------
#
# Python modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
import re

import logging

_LOG = logging.getLogger(".widgets.styledtextbuffer")

# -------------------------------------------------------------------------
#
# GTK modules
#
# -------------------------------------------------------------------------
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Pango
from .undoablebuffer import UndoableBuffer

WEIGHT_BOLD = Pango.Weight.BOLD
STYLE_ITALIC = Pango.Style.ITALIC
UNDERLINE_SINGLE = Pango.Underline.SINGLE
RISE_SUPERSUB = 5000
SCALE_SMALL = 1 / 1.2

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.lib import StyledText, StyledTextTag, StyledTextTagType

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
ALLOWED_STYLES = (
    StyledTextTagType.BOLD,
    StyledTextTagType.ITALIC,
    StyledTextTagType.UNDERLINE,
    StyledTextTagType.FONTCOLOR,
    StyledTextTagType.HIGHLIGHT,
    StyledTextTagType.FONTFACE,
    StyledTextTagType.FONTSIZE,
    StyledTextTagType.SUPERSCRIPT,
    StyledTextTagType.LINK,
    StyledTextTagType.STRIKETHROUGH,
    StyledTextTagType.SUBSCRIPT,
)

STYLE_TO_PROPERTY = {
    StyledTextTagType.BOLD: "weight",  # permanent tag is used instead
    StyledTextTagType.ITALIC: "style",  # permanent tag is used instead
    StyledTextTagType.UNDERLINE: "underline",  # permanent tag is used instead
    StyledTextTagType.FONTCOLOR: "foreground",
    StyledTextTagType.HIGHLIGHT: "background",
    StyledTextTagType.FONTFACE: "family",
    StyledTextTagType.FONTSIZE: "size-points",
    StyledTextTagType.SUPERSCRIPT: "rise",
    StyledTextTagType.LINK: "link",
    StyledTextTagType.STRIKETHROUGH: "strikethrough",  # permanent tag
    StyledTextTagType.SUBSCRIPT: "rise",
}

(
    MATCH_START,
    MATCH_END,
    MATCH_FLAVOR,
    MATCH_STRING,
) = list(range(4))


# -------------------------------------------------------------------------
#
# LinkTag class
#
# -------------------------------------------------------------------------
class LinkTag(Gtk.TextTag):
    """
    Class for keeping track of link data.
    """

    lid = 0

    def __init__(self, buffer, data, **properties):
        LinkTag.lid += 1
        self.data = data
        Gtk.TextTag.__init__(self, name="link-%d" % LinkTag.lid)
        tag_table = buffer.get_tag_table()
        for property in properties:
            self.set_property(property, properties[property])
        tag_table.add(self)


# -------------------------------------------------------------------------
#
# GspellState class
#
# -------------------------------------------------------------------------
class GspellState:
    """
    A simple state machine kinda thingy.

    Trying to track Gspell activities on a buffer and re-apply formatting
    after Gspell replaces a misspelled word.
    """

    (STATE_NONE, STATE_CLICKED, STATE_DELETED, STATE_INSERTING) = list(range(4))

    def __init__(self, textbuffer):
        if not isinstance(textbuffer, Gtk.TextBuffer):
            raise TypeError("Init parameter must be instance of Gtk.TextBuffer")

        textbuffer.connect("mark-set", self.on_buffer_mark_set)
        textbuffer.connect("delete-range", self.on_buffer_delete_range)
        textbuffer.connect("insert-text", self.on_buffer_insert_text)
        textbuffer.connect_after("insert-text", self.after_buffer_insert_text)

        self.reset_state()

    def reset_state(self):
        self.state = self.STATE_NONE
        self.start = 0
        self.end = 0
        self.tags = None

    def on_buffer_mark_set(self, textbuffer, iter, mark):
        mark_name = mark.get_name()
        if mark_name == "gtkspell-click":
            self.state = self.STATE_CLICKED
            self.start, self.end = self.get_word_extents_from_mark(textbuffer, mark)
            _LOG.debug("SpellState got start %d end %d" % (self.start, self.end))
        elif mark_name == "insert":
            self.reset_state()

    def on_buffer_delete_range(self, textbuffer, start, end):
        if (
            (self.state == self.STATE_CLICKED)
            and (start.get_offset() == self.start)
            and (end.get_offset() == self.end)
        ):
            self.state = self.STATE_DELETED
            self.tags = start.get_tags()

    def on_buffer_insert_text(self, textbuffer, iter, text, length):
        if self.state == self.STATE_DELETED and iter.get_offset() == self.start:
            self.state = self.STATE_INSERTING

    def after_buffer_insert_text(self, textbuffer, iter, text, length):
        if self.state == self.STATE_INSERTING:
            mark = textbuffer.get_mark("gtkspell-insert-start")
            insert_start = textbuffer.get_iter_at_mark(mark)
            for tag in self.tags:
                textbuffer.apply_tag(tag, insert_start, iter)

        self.reset_state()

    def get_word_extents_from_mark(self, textbuffer, mark):
        """
        Get the word extents as Gspell does.

        Used to get the beginning of the word, in which user right clicked.
        Formatting found at that position used after Gspell replaces
        misspelled words.
        """
        start = textbuffer.get_iter_at_mark(mark)
        if not start.starts_word():
            # start.backward_word_start()
            self.backward_word_start(start)
        end = start.copy()
        if end.inside_word():
            # end.forward_word_end()
            self.forward_word_end(end)
        return start.get_offset(), end.get_offset()

    def forward_word_end(self, iter):
        """
        Gspell style Gtk.TextIter.forward_word_end.

        The parameter 'iter' is changing as side effect.
        """
        if not iter.forward_word_end():
            return False

        if iter.get_char() != "'":
            return True

        i = iter.copy()
        if i.forward_char():
            if i.get_char().isalpha():
                return iter.forward_word_end()

        return True

    def backward_word_start(self, iter):
        """
        Gspell style Gtk.TextIter.backward_word_start.

        The parameter 'iter' is changing as side effect.
        """
        if not iter.backward_word_start():
            return False

        i = iter.copy()
        if i.backward_char():
            if i.get_char() == "'":
                if i.backward_char():
                    if i.get_char().isalpha():
                        return iter.backward_word_start()

        return True


# -------------------------------------------------------------------------
#
# StyledTextBuffer class
#
# -------------------------------------------------------------------------
class StyledTextBuffer(UndoableBuffer):
    """
    An extended TextBuffer for handling :class:`.StyledText` strings.

    StyledTextBuffer is an interface between GRAMPS' :class:`.StyledText` format
    and Gtk.TextBuffer. To set and get the text use the :meth:`set_text` and
    :meth:`get_text` methods.

    To set a style to (a portion of) the text (e.g. from GUI) use the
    :meth:`apply_style` and :meth:`remove_style` methods.

    To receive information about the style of the text at the cursor position
    StyledTextBuffer provides two mechanism: message driven and polling.
    To receive notification of style change as cursor moves connect to the
    ``style-changed`` signal. To get the value of a certain style at the cursor
    use the :meth:`get_style_at_cursor` method.

    StyledTextBuffer has a regexp pattern matching mechanism too. To add a
    regexp pattern to match in the text use the :meth:`match_add` method. To
    check if there's a match at a certain position in the text use the
    :meth:`match_check`nmethod. For an example how to use the matching see
    :class:`.EditNote`.
    """

    __gtype_name__ = "StyledTextBuffer"

    __gsignals__ = {
        "style-changed": (
            GObject.SignalFlags.RUN_FIRST,
            None,  # return value
            (GObject.TYPE_PYOBJECT,),
        ),  # arguments
    }

    def __init__(self):
        super(StyledTextBuffer, self).__init__()

        # Create fix tags.
        # Other tags (e.g. color) have to be created on the fly
        # see self._find_tag_by_name
        self.create_tag(str(StyledTextTagType.BOLD), weight=WEIGHT_BOLD)
        self.create_tag(str(StyledTextTagType.ITALIC), style=STYLE_ITALIC)
        self.create_tag(str(StyledTextTagType.UNDERLINE), underline=UNDERLINE_SINGLE)
        self.create_tag(str(StyledTextTagType.STRIKETHROUGH), strikethrough=True)
        self.create_tag(
            str(StyledTextTagType.SUPERSCRIPT), rise=RISE_SUPERSUB, scale=SCALE_SMALL
        )
        self.create_tag(
            str(StyledTextTagType.SUBSCRIPT), rise=-RISE_SUPERSUB, scale=SCALE_SMALL
        )

        # internal format state attributes
        ## 1. are used to format inserted characters (self.after_insert_text)
        ## 2. are set each time the Insert marker is set (self.do_mark_set)
        ## 3. are set when a style is set (self._apply_style_to_selection)
        self.style_state = StyledTextTagType.STYLE_DEFAULT.copy()

        # internally used attribute
        self._insert = self.get_insert()

        # create a mark used for text formatting
        start, end = self.get_bounds()
        self.mark_insert = self.create_mark("insert-start", start, True)

        # pattern matching attributes
        self.patterns = []
        self.matches = []

        # hook up on some signals whose default handler cannot be overriden
        self.connect("insert-text", self.on_insert_text)
        self.connect_after("insert-text", self.after_insert_text)
        self.connect_after("delete-range", self.after_delete_range)

        self.linkcolor = "blue"

        # init gspell "state machine"
        self.gspell_state = GspellState(self)

    # Virtual methods

    def on_insert_text(self, textbuffer, iter, text, length):
        _LOG.debug("Will insert at %d length %d" % (iter.get_offset(), length))

        # let's remember where we started inserting
        self.move_mark(self.mark_insert, iter)

    def after_insert_text(self, textbuffer, iter, text, length):
        """Format inserted text."""
        _LOG.debug(
            "Have inserted at %d length %d (%s)" % (iter.get_offset(), length, text)
        )

        if not length:
            return

        # where did we start inserting
        insert_start = self.get_iter_at_mark(self.mark_insert)

        # apply active formats for the inserted text
        for style in ALLOWED_STYLES:
            value = self.style_state[style]
            if value and (value != StyledTextTagType.STYLE_DEFAULT[style]):
                self.apply_tag(self._find_tag_by_name(style, value), insert_start, iter)

    def after_delete_range(self, textbuffer, start, end):
        _LOG.debug("Deleted from %d till %d" % (start.get_offset(), end.get_offset()))

        # move 'insert' marker to have the format attributes updated
        self.move_mark(self._insert, start)

    def do_changed(self, data=None):
        """Parse for patterns in the text."""
        self.matches = []
        text = str(
            super(StyledTextBuffer, self).get_text(
                self.get_start_iter(), self.get_end_iter(), True
            )
        )
        for regex, flavor in self.patterns:
            iter = regex.finditer(text)
            while True:
                try:
                    match = next(iter)
                    self.matches.append(
                        (match.start(), match.end(), flavor, match.group())
                    )
                    _LOG.debug(
                        "Matches: %d, %d: %s [%d]"
                        % (match.start(), match.end(), match.group(), flavor)
                    )
                except StopIteration:
                    break

    def do_mark_set(self, iter, mark):
        """Update style state each time the cursor moves."""
        _LOG.debug("Setting mark %s at %d" % (mark.get_name(), iter.get_offset()))

        if mark.get_name() != "insert":
            return

        if not iter.starts_line():
            iter.backward_char()

        tag_names = [tag.get_property("name") for tag in iter.get_tags()]
        changed_styles = {}

        for style in ALLOWED_STYLES:
            if StyledTextTagType.STYLE_TYPE[style] == bool:
                value = str(style) in tag_names
            else:
                value = StyledTextTagType.STYLE_DEFAULT[style]
                for tname in tag_names:
                    if tname is None:
                        continue
                    if tname.startswith(str(style)):
                        value = tname.split(" ", 1)[1]
                        value = StyledTextTagType.STYLE_TYPE[style](value)

            if self.style_state[style] != value:
                changed_styles[style] = value

            self.style_state[style] = value

        if changed_styles:
            self.emit("style-changed", changed_styles)

    # Private

    ##def get_tag_value_at_insert(self, name):
    ##"""Get the value of the given tag at the insertion point."""
    ##tags = self.get_iter_at_mark(self._insert).get_tags()

    ##if name in self.toggle_actions:
    ##for tag in tags:
    ##if tag.get_name() == name:
    ##return True
    ##return False
    ##else:
    ##for tag in tags:
    ##if tag.get_name().startswith(name):
    ##return tag.get_name().split()[1]
    ##return None

    def _get_selection(self):
        bounds = self.get_selection_bounds()
        if not bounds:
            iter = self.get_iter_at_mark(self._insert)
            if iter.inside_word():
                start_pos = iter.get_offset()
                iter.forward_word_end()
                word_end = iter.get_offset()
                iter.backward_word_start()
                word_start = iter.get_offset()
                iter.set_offset(start_pos)
                bounds = (
                    self.get_iter_at_offset(word_start),
                    self.get_iter_at_offset(word_end),
                )
            else:
                bounds = (iter, self.get_iter_at_offset(iter.get_offset() + 1))
        return bounds

    def _apply_tag_to_selection(self, tag):
        selection = self._get_selection()
        if selection:
            self.apply_tag(tag, *selection)

    def _remove_tag_from_selection(self, tag):
        selection = self._get_selection()
        if selection:
            self.remove_tag(tag, *selection)

    def _apply_style_to_selection(self, style, value):
        # FIXME can this be unified?
        if StyledTextTagType.STYLE_TYPE[style] == bool:
            start, end = self._get_selection()

            if value:
                self.apply_tag_by_name(str(style), start, end)
            else:
                self.remove_tag_by_name(str(style), start, end)
        elif StyledTextTagType.STYLE_TYPE[style] == str:
            tag = self._find_tag_by_name(style, value)
            self._remove_style_from_selection(style)
            self._apply_tag_to_selection(tag)
        elif StyledTextTagType.STYLE_TYPE[style] == int:
            tag = self._find_tag_by_name(style, value)
            self._remove_style_from_selection(style)
            self._apply_tag_to_selection(tag)
        else:
            # we should never get until here
            return

        self.style_state[style] = value

    def _remove_style_from_selection(self, style):
        start, end = self._get_selection()
        tags = self._get_tag_from_range(start.get_offset(), end.get_offset())
        for tag_name, tag_data in tags.items():
            if tag_name.startswith(str(style)):
                for start, end in tag_data:
                    self.remove_tag_by_name(
                        tag_name,
                        self.get_iter_at_offset(start),
                        self.get_iter_at_offset(end + 1),
                    )

    def clear_selection(self):
        """
        Clear tags from selection.
        """
        start, end = self._get_selection()
        tags = self._get_tag_from_range(start.get_offset(), end.get_offset())
        removed_something = False
        for tag_name, tag_data in tags.items():
            if tag_name.startswith("link"):
                for start_pos, end_pos in tag_data:
                    self.remove_tag_by_name(
                        tag_name,
                        self.get_iter_at_offset(start_pos),
                        self.get_iter_at_offset(end_pos + 1),
                    )
                    removed_something = True

        for style in ALLOWED_STYLES:
            value = self.style_state[style]
            if value and (value != StyledTextTagType.STYLE_DEFAULT[style]):
                self.remove_tag(self._find_tag_by_name(style, value), start, end)
                removed_something = True
        return removed_something

    def _get_tag_from_range(self, start=None, end=None):
        """
        Extract Gtk.TextTags from buffer.

        Return only the name of the TextTag from the specified range.
        If range is not given, tags extracted from the whole buffer.

        :note: TextTag names are always composed like: (%s %s) % (style, value)

        :param start: an offset pointing to the start of the range of text
        :param type: int
        :param end: an offset pointing to the end of the range of text
        :param type: int
        :returns: tagdict
        :rtype: {TextTag_Name: [(start, end),]}
        """
        if start is None:
            start = 0
        if end is None:
            end = self.get_char_count()

        tagdict = {}
        iter = self.get_iter_at_offset(start)
        for pos in range(start, end):
            for tag in iter.get_tags():
                name = tag.get_property("name")
                if name in tagdict:
                    if tagdict[name][-1][1] == pos - 1:
                        tagdict[name][-1] = (tagdict[name][-1][0], pos)
                    else:
                        tagdict[name].append((pos, pos))
                else:
                    tagdict[name] = [(pos, pos)]
            iter.forward_char()
        return tagdict

    def _find_tag_by_name(self, style, value):
        """
        Fetch TextTag from buffer's tag table by it's name.

        If TextTag does not exist yet, it is created.
        """
        if style not in StyledTextTagType.STYLE_TYPE:
            return None
        elif StyledTextTagType.STYLE_TYPE[style] == bool:
            tag_name = str(style)
        elif StyledTextTagType.STYLE_TYPE[style] == str:
            tag_name = "%d %s" % (style, value)
        elif StyledTextTagType.STYLE_TYPE[style] == int:
            tag_name = "%d %d" % (style, value)
        else:
            raise ValueError(
                "Unknown style (%s) value type: %s" % (style, value.__class__)
            )

        tag = self.get_tag_table().lookup(tag_name)

        if not tag:
            if StyledTextTagType.STYLE_TYPE[style] != bool:
                # bool style tags are not created here, but in constuctor
                tag = self.create_tag(tag_name)
                tag.set_property(STYLE_TO_PROPERTY[style], value)
            else:
                return None
        return tag

    # Public API

    def set_text(self, s_text):
        """
        Set the content of the buffer with markup tags.

        .. note:: ``s_`` prefix means StyledText*, while ``g_`` prefix means
                  Gtk.*.
        """
        super(StyledTextBuffer, self).set_text(str(s_text))
        # self.remove_all_tags(self.get_start_iter(), self.get_end_iter())

        s_tags = s_text.get_tags()
        for s_tag in s_tags:
            if s_tag.name == _("Link"):
                g_tag = LinkTag(
                    self,
                    s_tag.value,
                    foreground=self.linkcolor,
                    underline=UNDERLINE_SINGLE,
                )
            else:
                try:
                    g_tag = self._find_tag_by_name(int(s_tag.name), s_tag.value)
                except:
                    g_tag = None
            if g_tag is not None:
                for start, end in s_tag.ranges:
                    start_iter = self.get_iter_at_offset(start)
                    end_iter = self.get_iter_at_offset(end)
                    self.apply_tag(g_tag, start_iter, end_iter)

    def get_text(self, start=None, end=None, include_hidden_chars=True):
        """
        Return the buffer text.

        .. note:: ``s_`` prefix means StyledText*, while ``g_`` prefix means
                  Gtk.*.
        """
        if start is None:
            start = self.get_start_iter()
        if end is None:
            end = self.get_end_iter()

        txt = super(StyledTextBuffer, self).get_text(start, end, include_hidden_chars)
        txt = str(txt)

        # extract tags out of the buffer
        g_tags = self._get_tag_from_range()
        s_tags = []

        for g_tagname, g_ranges in g_tags.items():
            if g_tagname is None:
                continue
            if g_tagname.startswith("link"):
                tag = self.get_tag_table().lookup(g_tagname)
                s_ranges = [(start, end + 1) for (start, end) in g_ranges]
                s_value = tag.data
                s_tag = StyledTextTag(_("Link"), s_value, s_ranges)
                s_tags.append(s_tag)
            else:
                style_and_value = g_tagname.split(" ", 1)

                try:
                    style = int(style_and_value[0])
                    if len(style_and_value) == 1:
                        s_value = None
                    else:
                        s_value = StyledTextTagType.STYLE_TYPE[style](
                            style_and_value[1]
                        )

                    if style in ALLOWED_STYLES:
                        s_ranges = [(start, end + 1) for (start, end) in g_ranges]
                        s_tag = StyledTextTag(style, s_value, s_ranges)

                        s_tags.append(s_tag)
                except ValueError:
                    _LOG.debug("silently skipping Gtk.TextTag '%s'" % g_tagname)

        return StyledText(txt, s_tags)

    def apply_style(self, style, value):
        """
        Apply a style with the given value to the selection.

        :param style: style type to apply
        :type style: :class:`.StyledTextTagStyle` int value
        :param value: value of the style type
        :type value: depends on the ``style`` type
        """
        if not isinstance(value, StyledTextTagType.STYLE_TYPE[style]):
            raise TypeError(
                "Style (%d) value must be %s and not %s"
                % (style, StyledTextTagType.STYLE_TYPE[style], value.__class__)
            )

        self._apply_style_to_selection(style, value)

    def remove_style(self, style):
        """
        Delete all occurences with any value of the given style.

        :param style: style type to apply
        :type style: :class:`.StyledTextTagStyle` int value
        """
        self._remove_style_from_selection(style)

    def get_style_at_cursor(self, style):
        """
        Get the actual value of the given style at the cursor position.

        :param style: style type to apply
        :type style: :class:`.StyledTextTagStyle` int value
        :returns: value of the style type
        :rtype: depends on the ``style`` type
        """
        return self.style_state[style]

    def match_add(self, pattern, flavor):
        """Add a pattern to look for in the text."""
        regex = re.compile(pattern)
        self.patterns.append((regex, flavor))

    def match_check(self, pos):
        """Check if pos falls into any of the matched patterns."""
        for match in self.matches:
            if pos >= match[MATCH_START] and pos <= match[MATCH_END]:
                return match

        return None
