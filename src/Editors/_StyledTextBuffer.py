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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"Text buffer subclassed from gtk.TextBuffer handling L{StyledText}."

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import re

import logging
_LOG = logging.getLogger(".Editors.StyledTextBuffer")

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
import gtk
from pango import WEIGHT_BOLD, STYLE_ITALIC, UNDERLINE_SINGLE

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.lib import (StyledText, StyledTextTag, StyledTextTagType)

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
(MATCH_START,
 MATCH_END,
 MATCH_FLAVOR,
 MATCH_STRING,) = range(4)

#-------------------------------------------------------------------------
#
# GtkSpellState class
#
#-------------------------------------------------------------------------
class GtkSpellState:
    """A simple state machine kinda thingy.
    
    Trying to track gtk.Spell activities on a buffer and re-apply formatting
    after gtk.Spell replaces a misspelled word.
        
    """
    (STATE_NONE,
     STATE_CLICKED,
     STATE_DELETED,
     STATE_INSERTING) = range(4)

    def __init__(self, textbuffer):
        if not isinstance(textbuffer, gtk.TextBuffer):
            raise TypeError("Init parameter must be instance of gtk.TextBuffer")
            
        textbuffer.connect('mark-set', self.on_buffer_mark_set)
        textbuffer.connect('delete-range', self.on_buffer_delete_range)
        textbuffer.connect('insert-text', self.on_buffer_insert_text)
        textbuffer.connect_after('insert-text', self.after_buffer_insert_text)
        
        self.reset_state()
        
    def reset_state(self):
        self.state = self.STATE_NONE
        self.start = 0
        self.end = 0
        self.tags = None
        
    def on_buffer_mark_set(self, textbuffer, iter, mark):
        mark_name = mark.get_name()
        if  mark_name == 'gtkspell-click':
            self.state = self.STATE_CLICKED
            self.start, self.end = self.get_word_extents_from_mark(textbuffer,
                                                                   mark)
            _LOG.debug("SpellState got start %d end %d" % (self.start, self.end))
        elif mark_name == 'insert':
            self.reset_state()

    def on_buffer_delete_range(self, textbuffer, start, end):
        if ((self.state == self.STATE_CLICKED) and
            (start.get_offset() == self.start) and
            (end.get_offset() == self.end)):
            self.state = self.STATE_DELETED
            self.tags = start.get_tags()
    
    def on_buffer_insert_text(self, textbuffer, iter, text, length):
        if self.state == self.STATE_DELETED and iter.get_offset() == self.start:
            self.state = self.STATE_INSERTING

    def after_buffer_insert_text(self, textbuffer, iter, text, length):
        if self.state == self.STATE_INSERTING:
            mark = textbuffer.get_mark('gtkspell-insert-start')
            insert_start = textbuffer.get_iter_at_mark(mark)
            for tag in self.tags:
                textbuffer.apply_tag(tag, insert_start, iter)
        
        self.reset_state()

    def get_word_extents_from_mark(self, textbuffer, mark):
        """Get the word extents as gtk.Spell does.
        
        Used to get the beginning of the word, in which user right clicked.
        Formatting found at that position used after gtk.Spell replaces
        misspelled words.
        
        """
        start = textbuffer.get_iter_at_mark(mark)
        if not start.starts_word():
            #start.backward_word_start()
            self.backward_word_start(start)
        end = start.copy()
        if end.inside_word():
            #end.forward_word_end()
            self.forward_word_end(end)
        return start.get_offset(), end.get_offset()
    
    def forward_word_end(self, iter):
        """gtk.Spell style gtk.TextIter.forward_word_end.
        
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
        """gtk.Spell style gtk.TextIter.backward_word_start.

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
    
#-------------------------------------------------------------------------
#
# StyledTextBuffer class
#
#-------------------------------------------------------------------------
class StyledTextBuffer(gtk.TextBuffer):
    """An extended TextBuffer for handling StyledText strings.
    
    StyledTextBuffer is an interface between GRAMPS' L{StyledText} format
    and gtk.TextBuffer. To set and get the text use the L{set_text} and 
    L{get_text} methods.
    
    StyledTextBuffer provides an action group (L{format_action_group})
    for GUIs.
    
    StyledTextBuffer has a regexp pattern matching mechanism too. To add a
    regexp pattern to match in the text use the L{match_add} method. To check
    if there's a match at a certain position in the text use the L{match_check}
    method. For an example how to use the matching see L{EditNote}.
    
    """
    __gtype_name__ = 'StyledTextBuffer'
    
    formats = ('italic', 'bold', 'underline',
               'font', 'foreground', 'background',)

    def __init__(self):
        gtk.TextBuffer.__init__(self)

        # Create fix tags.
        # Other tags (e.g. color) have to be created on the fly
        self.create_tag('bold', weight=WEIGHT_BOLD)
        self.create_tag('italic', style=STYLE_ITALIC)
        self.create_tag('underline', underline=UNDERLINE_SINGLE)
        
        # Setup action group used from user interface
        format_toggle_actions = [
            ('italic', gtk.STOCK_ITALIC, None, None,
             _('Italic'), self._on_toggle_action_activate),
            ('bold', gtk.STOCK_BOLD, None, None,
             _('Bold'), self._on_toggle_action_activate),
            ('underline', gtk.STOCK_UNDERLINE, None, None,
             _('Underline'), self._on_toggle_action_activate),
        ]
        
        self.toggle_actions = [action[0] for action in format_toggle_actions]

        format_actions = [
            ('font', 'gramps-font', None, None,
             _('Font'), self._on_action_activate),
            ('foreground', 'gramps-font-color', None, None,
             _('Font Color'), self._on_action_activate),
            ('background', 'gramps-font-bgcolor', None, None,
             _('Background Color'), self._on_action_activate),
            ('clear', gtk.STOCK_CLEAR, None, None,
             _('Clear'), self._format_clear_cb),
        ]
        
        self.action_accels = {
            '<Control>i': 'italic',
            '<Control>b': 'bold',
            '<Control>u': 'underline',
        }

        self.format_action_group = gtk.ActionGroup('Format')
        self.format_action_group.add_toggle_actions(format_toggle_actions)
        self.format_action_group.add_actions(format_actions)

        # internal format state attributes
        ## 1. are used to format inserted characters (self.after_insert_text)
        ## 2. are set each time the Insert marker is set (self.do_mark_set)
        ## 3. are set when format actions are activated (self.*_action_activate)
        self.italic = False
        self.bold = False
        self.underline = False
        self.font = None
        # TODO could we separate font name and size?
        ##self.size = None
        self.foreground = None
        self.background = None
        
        # internally used attribute
        self._internal_toggle = False
        self._insert = self.get_insert()
        
        # create a mark used for text formatting
        start, end = self.get_bounds()
        self.mark_insert = self.create_mark('insert-start', start, True)
        
        # pattern matching attributes
        self.patterns = []
        self.matches = []
        
        # hook up on some signals whose default handler cannot be overriden
        self.connect('insert-text', self.on_insert_text)
        self.connect_after('insert-text', self.after_insert_text)
        self.connect_after('delete-range', self.after_delete_range)
        
        # init gtkspell "state machine"
        self.gtkspell_state = GtkSpellState(self)
        
    # Virtual methods

    def on_insert_text(self, textbuffer, iter, text, length):
        _LOG.debug("Will insert at %d length %d" % (iter.get_offset(), length))
        
        # let's remember where we started inserting
        self.move_mark(self.mark_insert, iter)

    def after_insert_text(self, textbuffer, iter, text, length):
        """Format inserted text."""
        _LOG.debug("Have inserted at %d length %d (%s)" %
                  (iter.get_offset(), length, text))
                  
        if not length:
            return
        
        # where did we start inserting
        insert_start = self.get_iter_at_mark(self.mark_insert)

        # apply active formats for the inserted text
        for format in self.__class__.formats:
            value = getattr(self, format)
            if value:
                if format in self.toggle_actions:
                    value = None
                    
                self.apply_tag(self._find_tag_by_name(format, value),
                               insert_start, iter)
    
    def after_delete_range(self, textbuffer, start, end):
        _LOG.debug("Deleted from %d till %d" %
                  (start.get_offset(), end.get_offset()))
        
        # move 'insert' marker to have the format attributes updated
        self.move_mark(self._insert, start)
        
    def do_changed(self):
        """Parse for patterns in the text."""
        self.matches = []
        text = unicode(gtk.TextBuffer.get_text(self,
                                               self.get_start_iter(),
                                               self.get_end_iter()))
        for regex, flavor in self.patterns:
            iter = regex.finditer(text)
            while True:
                try:
                    match = iter.next()
                    self.matches.append((match.start(), match.end(),
                                         flavor, match.group()))
                    _LOG.debug("Matches: %d, %d: %s [%d]" %
                              (match.start(), match.end(),
                               match.group(), flavor))
                except StopIteration:
                    break

    def do_mark_set(self, iter, mark):
        """Update format attributes each time the cursor moves."""
        _LOG.debug("Setting mark %s at %d" %
                  (mark.get_name(), iter.get_offset()))
        
        if mark.get_name() != 'insert':
            return
        
        if not iter.starts_line():
            iter.backward_char()
            
        tag_names = [tag.get_property('name') for tag in iter.get_tags()]
        for format in self.__class__.formats:
            if format in self.toggle_actions:
                value = format in tag_names
                # set state of toggle action
                action = self.format_action_group.get_action(format)
                self._internal_toggle = True
                action.set_active(value)
                self._internal_toggle = False
            else:
                value = None
                for tname in tag_names:
                    if tname.startswith(format):
                        value = tname.split(' ', 1)[1]
            
            setattr(self, format, value)

    # Private
    
    def _tagname_to_tagtype(self, name):
        """Convert gtk.TextTag names to StyledTextTagType values."""
        tag2type = {
            'bold': StyledTextTagType.BOLD,
            'italic': StyledTextTagType.ITALIC,
            'underline': StyledTextTagType.UNDERLINE,
            'foreground': StyledTextTagType.FONTCOLOR,
            'background': StyledTextTagType.HIGHLIGHT,
            'font': StyledTextTagType.FONTFACE,
        }
        
        return StyledTextTagType(tag2type[name])
    
    def _tagtype_to_tagname(self, tagtype):
        """Convert StyledTextTagType values to gtk.TextTag names."""
        type2tag = {
            StyledTextTagType.BOLD: 'bold',
            StyledTextTagType.ITALIC: 'italic',
            StyledTextTagType.UNDERLINE: 'underline',
            StyledTextTagType.FONTCOLOR: 'foreground',
            StyledTextTagType.HIGHLIGHT: 'background',
            StyledTextTagType.FONTFACE: 'font',
        }
        
        return type2tag[tagtype]
    
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

    def _color_to_hex(self, color):
        """Convert gtk.gdk.Color to hex string."""
        hexstring = ""
        for col in 'red', 'green', 'blue':
            hexfrag = hex(getattr(color, col) / (16 * 16)).split("x")[1]
            if len(hexfrag) < 2:
                hexfrag = "0" + hexfrag
            hexstring += hexfrag
        return '#' + hexstring
        
    def _hex_to_color(self, hex):
        """Convert hex string to gtk.gdk.Color."""
        color = gtk.gdk.color_parse(hex)
        return color

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
                bounds = (self.get_iter_at_offset(word_start),
                          self.get_iter_at_offset(word_end))
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
            
    def _remove_format_from_selection(self, format):
        start, end = self._get_selection()
        tags = self._get_tag_from_range(start.get_offset(), end.get_offset())
        for tag_name in tags.keys():
            if tag_name.startswith(format):
                for start, end in tags[tag_name]:
                    self.remove_tag_by_name(tag_name,
                                            self.get_iter_at_offset(start),
                                            self.get_iter_at_offset(end+1))
                    
    def _get_tag_from_range(self, start=None, end=None):
        """Extract gtk.TextTags from buffer.
        
        Return only the name of the TextTag from the specified range.
        If range is not given, tags extracted from the whole buffer.
        
        @param start: an offset pointing to the start of the range of text
        @param type: int
        @param end: an offset pointing to the end of the range of text
        @param type: int
        @return: tagdict
        @rtype: {TextTag_Name: [(start, end),]}
        
        """
        if start is None:
            start = 0
        if end is None:
            end = self.get_char_count()
            
        tagdict = {}
        for pos in range(start, end):
            iter = self.get_iter_at_offset(pos)
            for tag in iter.get_tags():
                name = tag.get_property('name')
                if tagdict.has_key(name):
                    if tagdict[name][-1][1] == pos - 1:
                        tagdict[name][-1] = (tagdict[name][-1][0], pos)
                    else:
                        tagdict[name].append((pos, pos))
                else:
                    tagdict[name]=[(pos, pos)]
        return tagdict

    def _find_tag_by_name(self, name, value):
        """Fetch TextTag from buffer's tag table by it's name.
        
        If TextTag does not exist yet, it is created.
        
        """
        if value is None:
            tag_name = name
        else:
            tag_name = "%s %s" % (name, value)
        tag = self.get_tag_table().lookup(tag_name)
        if not tag:
            if value is not None:
                tag = self.create_tag(tag_name)
                tag.set_property(name, value)
            else:
                return None
        return tag

    # Callbacks
    
    def _on_toggle_action_activate(self, action):
        """Toggle a format.
        
        Toggle formats are e.g. 'bold', 'italic', 'underline'.
        
        """
        if self._internal_toggle:
            return

        start, end = self._get_selection()
        
        if action.get_active():
            self.apply_tag_by_name(action.get_name(), start, end)
        else:
            self.remove_tag_by_name(action.get_name(), start, end)
            
        setattr(self, action.get_name(), action.get_active())

    def _on_action_activate(self, action):
        """Apply a format."""
        format = action.get_name()
        
        if format == 'foreground':
            color_selection = gtk.ColorSelectionDialog(_("Select font color"))
            if self.foreground:
                color_selection.colorsel.set_current_color(
                    self._hex_to_color(self.foreground))
            response = color_selection.run()
            color = color_selection.colorsel.get_current_color()
            value = self._color_to_hex(color)
            color_selection.destroy()
        elif format == 'background':
            color_selection = gtk.ColorSelectionDialog(_("Select "
                                                         "background color"))
            if self.background:
                color_selection.colorsel.set_current_color(
                    self._hex_to_color(self.background))
            response = color_selection.run()
            color = color_selection.colorsel.get_current_color()
            value = self._color_to_hex(color)
            color_selection.destroy()
        elif format == 'font':
            font_selection = CustomFontSelectionDialog(_("Select font"))
            if self.font:
                font_selection.fontsel.set_font_name(self.font)
            response = font_selection.run()
            value = font_selection.fontsel.get_font_name()
            font_selection.destroy()
        else:
            _LOG.debug("unknown format: '%s'" % format)
            return

        if response == gtk.RESPONSE_OK:
            _LOG.debug("applying format '%s' with value '%s'" % (format, value))
            
            tag = self._find_tag_by_name(format, value)
            self._remove_format_from_selection(format)
            self._apply_tag_to_selection(tag)
            
            setattr(self, format, value)

    def _format_clear_cb(self, action):
        """Remove all formats from the selection.
        
        Remove only our own tags without touching other ones (e.g. gtk.Spell),
        thus remove_all_tags() can not be used.
        
        """
        for format in self.formats:
            self._remove_format_from_selection(format)

    def on_key_press_event(self, widget, event):
        """Handle formatting shortcuts."""
        for accel in self.action_accels.keys():
            key, mod = gtk.accelerator_parse(accel)
            if (event.keyval, event.state) == (key, mod):
                action_name = self.action_accels[accel]
                action = self.format_action_group.get_action(action_name)
                action.activate()
                return True
        return False
        
    # Public API

    def set_text(self, r_text):
        """Set the content of the buffer with markup tags."""
        gtk.TextBuffer.set_text(self, str(r_text))
    
        r_tags = r_text.get_tags()
        for r_tag in r_tags:
            tagname = self._tagtype_to_tagname(int(r_tag.name))
            g_tag = self._find_tag_by_name(tagname, r_tag.value)
            if g_tag is not None:
                for (start, end) in r_tag.ranges:
                    start_iter = self.get_iter_at_offset(start)
                    end_iter = self.get_iter_at_offset(end)
                    self.apply_tag(g_tag, start_iter, end_iter)
                    
    def get_text(self, start=None, end=None, include_hidden_chars=True):
        """Return the buffer text."""
        if not start:
            start = self.get_start_iter()
        if not end:
            end = self.get_end_iter()

        txt = gtk.TextBuffer.get_text(self, start, end, include_hidden_chars)
        txt = unicode(txt)
        
        # extract tags out of the buffer
        g_tags = self._get_tag_from_range()
        r_tags = []
        
        for g_tagname, g_ranges in g_tags.items():
            name_value = g_tagname.split(' ', 1)

            if len(name_value) == 1:
                name = name_value[0]
                r_value = None
            else:
                (name, r_value) = name_value

            if name in self.formats:
                r_tagtype = self._tagname_to_tagtype(name)
                r_ranges = [(start, end+1) for (start, end) in g_ranges]
                r_tag = StyledTextTag(r_tagtype, r_value, r_ranges)
                                      
                r_tags.append(r_tag)
        
        return StyledText(txt, r_tags)

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

#-------------------------------------------------------------------------
#
# CustomFontSelectionDialog class
#
#-------------------------------------------------------------------------
class CustomFontSelectionDialog(gtk.FontSelectionDialog):
    """A FontSelectionDialog without the Style treeview.
    
    This should be only a workaround until a real custom font selector
    is created, because this solution is gtk implementation dependent.
    
    """
    def __init__(self, title):
        gtk.FontSelectionDialog.__init__(self, title)
        
        # hide the Style label and treeview
        for widget in self.fontsel.get_children():
            if isinstance(widget, gtk.Table):
                table = widget
        
        for child in table.get_children():
            if table.child_get_property(child, 'left-attach') == 1:
                child.hide()