#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

"Handling formatted ('rich text') strings"

__revision__ = "$Revision$"
__author__   = "Zsolt Foldvari"

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from xml.sax import saxutils, xmlreader, ContentHandler
from xml.sax import parseString, SAXParseException
import re
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

#-------------------------------------------------------------------------
#
# Set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".MarkupText")

#-------------------------------------------------------------------------
#
# GTK modules
#
#-------------------------------------------------------------------------
import gtk
from pango import WEIGHT_BOLD, STYLE_ITALIC, UNDERLINE_SINGLE

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
ROOT_ELEMENT = 'gramps'
ROOT_START_TAG = '<' + ROOT_ELEMENT + '>'
ROOT_END_TAG = '</' + ROOT_ELEMENT + '>'
LEN_ROOT_START_TAG = len(ROOT_START_TAG)
LEN_ROOT_END_TAG = len(ROOT_END_TAG)

def is_gramps_markup(text):
    return (text[:LEN_ROOT_START_TAG] == ROOT_START_TAG and
            text[-LEN_ROOT_END_TAG:] == ROOT_END_TAG)

def clear_root_tags(text):
    return text[LEN_ROOT_START_TAG:len(text)-LEN_ROOT_END_TAG]
    
class MarkupParser(ContentHandler):
    """A simple ContentHandler class to parse Gramps markup'ed text.
    
    Use it with xml.sax.parse() or xml.sax.parseString(). A root tag is
    required. Parsing result can be obtained via the public attributes of
    the class:    
    @attr content: clean text
    @attr type: str
    @attr elements: list of markup elements 
    @attr type: list[tuple((start, end), name, attrs),]
    
    """
    def startDocument(self):
        self._open_document = False
        self._open_elements = []
        self.elements = []
        self.content = ""
        
    def endDocument(self):
        self._open_document = False
        if len(self._open_elements):
            raise SAXParseException('Unclosed tags')

    def startElement(self, name, attrs):
        if not self._open_document:
            if name == ROOT_ELEMENT:
                self._open_document = True
            else:
                raise SAXParseException('Root element missing')
        else:
            self._open_elements.append({'name': name,
                                        'attrs': attrs.copy(),
                                        'start': len(self.content),
                                    })

    def endElement(self, name):
        # skip root element
        if name == ROOT_ELEMENT:
            return
        
        for e in self._open_elements:
            if e['name'] == name:
                self.elements.append(((e['start'], len(self.content)),
                                       e['name'], e['attrs']))

                self._open_elements.remove(e)
                return

    def characters (self, chunk):
        self.content += chunk

class MarkupWriter:
    """Generate XML markup text for Notes.
    
    Provides additional feature of accounting opened tags and closing them
    properly in case of partially overlapping elements.
    
    """
    (EVENT_START,
     EVENT_END) = range(2)

    def __init__(self, encoding='utf-8'):
        self._output = StringIO()
        self._encoding = encoding
        self._writer = saxutils.XMLGenerator(self._output, self._encoding)
        
        self._attrs = xmlreader.AttributesImpl({})
        
        self._open_elements = []
        self.content = ''

    # Private

    def _elements_to_events(self, elements):
        """Create an event list for XML writer.
        
        @param elements: list of XML elements with start/end indices and attrs
        @param type: [((start, end), xml_element_name, attrs),]
        @return: eventdict
        @rtype: {index: [(xml_element_name, attrs, event_type, pair_index),]}
         index: place of the event
         xml_element_name: element to apply
         attrs: attributes of the tag (xml.sax.xmlreader.AttrubutesImpl)
         event_type: START or END event
         pair_index: index of the pair event, used for sorting
        
        """
        eventdict = {}
        for (start, end), name, attrs in elements:
            # append START events
            if eventdict.has_key(start):
                eventdict[start].append((name, attrs, self.EVENT_START, end))
            else:
                eventdict[start] = [(name, attrs, self.EVENT_START, end)]
            # END events have to prepended to avoid creating empty elements
            if eventdict.has_key(end):
                eventdict[end].insert(0, (name, attrs, self.EVENT_END, start))
            else:
                eventdict[end] = [(name, attrs, self.EVENT_END, start)]

        # sort events at the same index
        indices = eventdict.keys()
        for idx in indices:
            if len(eventdict[idx]) > 1:
                eventdict[idx].sort(self._sort_events)

        return eventdict

    def _sort_events(self, event_a, event_b):
        """Sort events that are at the same index.
        
        Sorting with the following rules:
        1. END event goes always before START event;
        2. from two START events the one goes first, which has it's own END
        event later;
        3. from two END events the one goes first, which has it's own START
        event later.
        
        """
        tag_a, attr_a, type_a, pair_a = event_a
        tag_b, attr_b, type_b, pair_b = event_b
        
        if (type_a + type_b) == (self.EVENT_START + self.EVENT_END):
            return type_b - type_a
        else:
            return pair_b - pair_a

    def _startElement(self, name, attrs=None):
        """Insert start tag."""
        if not attrs:
            attrs = self._attrs
        self._writer.startElement(name, attrs)
        self._open_elements.append(name)
        
    def _endElement(self, name):
        """Insert end tag."""
        if not len(self._open_elements):
            log.debug("Trying to close element '%s' when non is open" % name)
            return
        
        tmp_list = []
        elem = ''
        
        # close all open elements until we reach to the requested one
        while elem != name:
            try:
                elem = self._open_elements.pop()
                self._writer.endElement(elem)
                if elem != name:
                    tmp_list.append(elem)
            except:
                # we need to do something smart here...
                log.debug("Trying to close non open element '%s'" % name)
                break
        
        # open all other elements again
        while True:
            try:
                elem = tmp_list.pop()
                self._startElement(elem)
            except:
                break

    # Public

    def generate(self, text, elements):
        # reset output and start root element
        self._output.truncate(0)
        self._writer.startElement(ROOT_ELEMENT, self._attrs)
        
        # split the elements to events
        events = self._elements_to_events(elements)
        
        # feed the events into the xml generator
        last_pos = 0
        indices = events.keys()
        indices.sort()
        for index in indices:
            self._writer.characters(text[last_pos:index])
            for name, attrs, event_type, p in events[index]:
                if event_type == self.EVENT_START:
                    self._startElement(name, attrs)
                elif event_type == self.EVENT_END:
                    self._endElement(name)
            last_pos = index
        self._writer.characters(text[last_pos:])
        
        # close root element and end doc
        self._writer.endElement(ROOT_ELEMENT)
        self._writer.endDocument()
        
        # copy result
        self.content = self._output.getvalue()
        log.debug("Gramps XML: %s" % self.content)
        
class GtkSpellState:
    """A simple state machine kinda thingy.
    
    Try tracking gtk.Spell activities on a buffer and reapply formatting
    after gtk.Spell replaces a misspelled word.
    
    """
    (STATE_NONE,
     STATE_CLICKED,
     STATE_DELETED,
     STATE_INSERTING) = range(4)

    def __init__(self, buffer):
        if not isinstance(buffer, gtk.TextBuffer):
            raise TypeError("Init parameter must be instance of gtk.TextBuffer")
            
        buffer.connect('mark-set', self.on_buffer_mark_set)
        buffer.connect('delete-range', self.on_buffer_delete_range)
        buffer.connect('insert-text', self.on_buffer_insert_text)
        buffer.connect_after('insert-text', self.after_buffer_insert_text)
        
        self.reset_state()
        
    def reset_state(self):
        self.state = self.STATE_NONE
        self.start = 0
        self.end = 0
        self.tags = None
        
    def on_buffer_mark_set(self, buffer, iter, mark):
        mark_name = mark.get_name()
        if  mark_name == 'gtkspell-click':
            self.state = self.STATE_CLICKED
            self.start, self.end = self.get_word_extents_from_mark(buffer, mark)
            log.debug("SpellState got start %d end %d" % (self.start, self.end))
        elif mark_name == 'insert':
            self.reset_state()

    def on_buffer_delete_range(self, buffer, start, end):
        if ((self.state == self.STATE_CLICKED) and
            (start.get_offset() == self.start) and
            (end.get_offset() == self.end)):
            self.state = self.STATE_DELETED
            self.tags = start.get_tags()
    
    def on_buffer_insert_text(self, buffer, iter, text, length):
        if self.state == self.STATE_DELETED and iter.get_offset() == self.start:
            self.state = self.STATE_INSERTING

    def after_buffer_insert_text(self, buffer, iter, text, length):
        if self.state == self.STATE_INSERTING:
            mark = buffer.get_mark('gtkspell-insert-start')
            insert_start = buffer.get_iter_at_mark(mark)
            for tag in self.tags:
                buffer.apply_tag(tag, insert_start, iter)
        
        self.reset_state()

    def get_word_extents_from_mark(self, buffer, mark):
        """Get the word extents as gtk.Spell does.
        
        Used to get the beginning of the word, in which user right clicked.
        Formatting found at that position used after gtk.Spell replaces
        misspelled words.
        
        """
        start = buffer.get_iter_at_mark(mark)
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
    
class MarkupBuffer(gtk.TextBuffer):
    """An extended TextBuffer with Gramps XML markup string interface.
    
    It implements MarkupParser and MarkupWriter on the input/output interfaces.
    Also translates Gramps XML markup language to gtk.TextTag's and vice versa.
    
    """
    __gtype_name__ = 'MarkupBuffer'
    
    formats = ('italic', 'bold', 'underline',
               'font', 'foreground', 'background',)

    def __init__(self):
        gtk.TextBuffer.__init__(self)

        self.parser = MarkupParser()
        self.writer = MarkupWriter()
        
        # Create fix tags.
        # Other tags (e.g. color) have to be created on the fly
        self.create_tag('bold', weight=WEIGHT_BOLD)
        self.create_tag('italic', style=STYLE_ITALIC)
        self.create_tag('underline', underline=UNDERLINE_SINGLE)
        
        # Setup action group used from user interface
        format_toggle_actions = [
            ('italic', gtk.STOCK_ITALIC, None, None,
             _('Italic'), self.on_toggle_action_activate),
            ('bold', gtk.STOCK_BOLD, None, None,
             _('Bold'), self.on_toggle_action_activate),
            ('underline', gtk.STOCK_UNDERLINE, None, None,
             _('Underline'), self.on_toggle_action_activate),
        ]
        
        self.toggle_actions = [action[0] for action in format_toggle_actions]

        format_actions = [
            ('font', gtk.STOCK_SELECT_FONT, None, None,
             _('Font'), self.on_action_activate),
            ('foreground', 'gramps-font-color', None, None,
             _('Font Color'), self.on_action_activate),
            ('background', 'gramps-font-bgcolor', None, None,
             _('Background Color'), self.on_action_activate),
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
        self.foreground = None
        self.background = None
        
        # internally used attribute
        self._internal_toggle = False
        self._insert = self.get_insert()
        
        # create a mark
        start, end = self.get_bounds()
        self.mark_insert = self.create_mark('insert-start', start, True)
        
        # hook up on some signals whose default handler cannot be overriden
        self.connect('insert-text', self.on_insert_text)
        self.connect_after('insert-text', self.after_insert_text)
        self.connect_after('delete-range', self.after_delete_range)

        # init gtkspell "state machine"
        self.gtkspell_state = GtkSpellState(self)
        
    # Virtual methods

    def on_insert_text(self, buffer, iter, text, length):
        log.debug("Will insert at %d length %d" % (iter.get_offset(), length))
        
        # let's remember where we started inserting
        self.move_mark(self.mark_insert, iter)

    def after_insert_text(self, buffer, iter, text, length):
        """Format inserted text."""
        log.debug("Have inserted at %d length %d (%s)" %
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
    
    def after_delete_range(self, buffer, start, end):
        log.debug("Deleted from %d till %d" %
                  (start.get_offset(), end.get_offset()))
        
        # move 'insert' marker to have the format attributes updated
        self.move_mark(self._insert, start)
        
    def do_mark_set(self, iter, mark):
        """Update toggle widgets each time the cursor moves."""
        log.debug("Setting mark %s at %d" %
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
    
    def _xmltag_to_texttag(self, name, attrs):
        """Convert XML tag to gtk.TextTag.
                
        Return only the name of the TextTag.
        
        @param name: name of the XML tag
        @param type: string
        @param attrs: attributes of the XML tag
        @param type: xmlreader.AttributesImpl
        @return: property of gtk.TextTag, value of property
        @rtype: string, string
        
        """
        if name == 'b':
            return 'bold', None
        elif name == 'i':
            return 'italic', None
        elif name == 'u':
            return 'underline', None
        ##elif name == 'font':
            ##attr_names = attrs.getNames()
            ##if 'color' in attr_names:
                ##return 'foreground', attrs.getValue('color')
            ##elif 'highlight' in attr_names:
                ##return 'background', attrs.getValue('highlight')
            ##elif 'face' in attr_names and 'size' in attr_names:
                ##return 'font', '%s %s' % (attrs.getValue('face'),
                                          ##attrs.getValue('size'))
            ##else:
                ##return None, None
        else:
            return None, None
        
    def _texttag_to_xmltag(self, name):
        """Convert gtk.TextTag to XML tag.
        
        @param name: name of the gtk.TextTag
        @param type: string
        @return: XML tag name, attribute
        @rtype: string, xmlreader.AttributesImpl
        
        """
        attrs = xmlreader.AttributesImpl({})
        if name == 'bold':
            return 'b', attrs
        elif name == 'italic':
            return 'i', attrs
        elif name == 'underline':
            return 'u', attrs
        ##elif name.startswith('foreground'):
            ##attrs._attrs['color'] = name.split()[1]
            ##return 'font', attrs
        ##elif name.startswith('background'):
            ##attrs._attrs['highlight'] = name.split()[1]
            ##return 'font', attrs
        ##elif name.startswith('font'):
            ##name = name.replace('font ', '')
            ##attrs._attrs['face'] = name.rsplit(' ', 1)[0]
            ##attrs._attrs['size'] = name.rsplit(' ', 1)[1]
            ##return 'font', attrs
        else:
            return None, None
        
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
        return gtk.gdk.Color(int(hex[1:3], 16),
                             int(hex[3:5], 16),
                             int(hex[5:7], 16))

    def get_selection(self):
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

    def apply_tag_to_selection(self, tag):
        selection = self.get_selection()
        if selection:
            self.apply_tag(tag, *selection)

    def remove_tag_from_selection(self, tag):
        selection = self.get_selection()
        if selection:
            self.remove_tag(tag, *selection)
            
    def remove_format_from_selection(self, format):
        start, end = self.get_selection()
        tags = self.get_tag_from_range(start.get_offset(), end.get_offset())
        for tag_name in tags.keys():
            if tag_name.startswith(format):
                for start, end in tags[tag_name]:
                    self.remove_tag_by_name(tag_name,
                                            self.get_iter_at_offset(start),
                                            self.get_iter_at_offset(end+1))
                    
    def get_tag_from_range(self, start=None, end=None):
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
    
    def on_toggle_action_activate(self, action):
        """Toggle a format.
        
        Toggle formats are e.g. 'bold', 'italic', 'underline'.
        
        """
        if self._internal_toggle:
            return

        start, end = self.get_selection()
        
        if action.get_active():
            self.apply_tag_by_name(action.get_name(), start, end)
        else:
            self.remove_tag_by_name(action.get_name(), start, end)
            
        setattr(self, action.get_name(), action.get_active())

    def on_action_activate(self, action):
        """Apply a format.
        
        Other tags for the same format have to be removed from the range
        first otherwise XML would get messy.
        
        """
        format = action.get_name()
        
        if format == 'foreground':
            color_selection = gtk.ColorSelectionDialog(_("Select font color"))
            response = color_selection.run()
            color = color_selection.colorsel.get_current_color()
            value = self._color_to_hex(color)
            color_selection.destroy()
        elif format == 'background':
            color_selection = gtk.ColorSelectionDialog(_("Select "
                                                         "background color"))
            response = color_selection.run()
            color = color_selection.colorsel.get_current_color()
            value = self._color_to_hex(color)
            color_selection.destroy()
        elif format == 'font':
            font_selection = gtk.FontSelectionDialog(_("Select font"))
            response = font_selection.run()
            value = font_selection.fontsel.get_font_name()
            font_selection.destroy()
        else:
            log.debug("unknown format: '%s'" % format)
            return

        if response == gtk.RESPONSE_OK:
            log.debug("applying format '%s' with value '%s'" % (format, value))
            
            tag = self._find_tag_by_name(format, value)
            self.remove_format_from_selection(format)
            self.apply_tag_to_selection(tag)
            
            setattr(self, format, value)

    def _format_clear_cb(self, action):
        """Remove all formats from the selection.
        
        Remove only our own tags without touching other ones (e.g. gtk.Spell),
        thus remove_all_tags() can not be used.
        
        """
        for format in self.formats:
            self.remove_format_from_selection(format)

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

    def set_text(self, xmltext):
        """Set the content of the buffer with markup tags."""
        try:
            parseString(xmltext.encode('utf-8'), self.parser)
            text = self.parser.content
        except:
            # if parse fails remove all tags and use clear text instead
            text = re.sub(r'(<.*?>)', '', xmltext)
            text = saxutils.unescape(text)
        
        gtk.TextBuffer.set_text(self, text)

        for element in self.parser.elements:
            (start, end), xmltag_name, attrs = element

            texttag_name, value = self._xmltag_to_texttag(xmltag_name, attrs)

            if texttag_name is not None:
                start_iter = self.get_iter_at_offset(start)
                end_iter = self.get_iter_at_offset(end)
                tag = self._find_tag_by_name(texttag_name, value)
                if tag is not None:
                    self.apply_tag(tag, start_iter, end_iter)

    def get_text(self, start=None, end=None, include_hidden_chars=True):
        """Returns the buffer text with xml markup tags.
        
        If no markup was applied returns clean text.
        
        """
        # get the clear text from the buffer
        if not start:
            start = self.get_start_iter()
        if not end:
            end = self.get_end_iter()
        txt = unicode(gtk.TextBuffer.get_text(self, start, end))

        # extract tags out of the buffer
        texttag = self.get_tag_from_range()
        
        if len(texttag):
            # convert the texttags to xml elements
            xml_elements = []
            for texttag_name, indices in texttag.items():
                xml_tag_name, attrs = self._texttag_to_xmltag(texttag_name)
                if xml_tag_name is not None:
                    for start_idx, end_idx in indices:
                        xml_elements.append(((start_idx, end_idx+1),
                                             xml_tag_name, attrs))

            # feed the elements into the xml writer
            self.writer.generate(txt, xml_elements)
            txt = self.writer.content
        
        return txt

    ##def apply_format(self, format, value=None):
        ##"""."""
        ##if format not in self.formats:
            ##raise TypeError("%s is not a valid format name" % format)

        ##start, end = self.get_selection()
        
        ##log.debug("Applying format '%s' with value '%s' for range %d - %d" %
                  ##(format, value, start.get_offset(), end.get_offset()))
        
        ##if format == 'bold':
            ##self.apply_tag_by_name('bold', start, end)
        ##elif format == 'italic':
            ##self.apply_tag_by_name('italic', start, end)
        ##elif format == 'underline':
            ##self.apply_tag_by_name('underline', start, end)
        ##else:
            ##log.error("Format '%s' is not yet implemented" % format)

    ##def remove_format(self, format, value=None):
        ##"""."""
        ##if format not in self.formats:
            ##raise TypeError("%s is not a valid format name" % format)

        ##start, end = self.get_selection()
        
        ##log.debug("Removing format '%s' with value '%s' for range %d - %d" %
                  ##(format, value, start.get_offset(), end.get_offset()))
        
        ##if format == 'bold':
            ##self.remove_tag_by_name('bold', start, end)
        ##elif format == 'italic':
            ##self.remove_tag_by_name('italic', start, end)
        ##elif format == 'underline':
            ##self.remove_tag_by_name('underline', start, end)
        ##else:
            ##log.error("Format '%s' is not yet implemented" % format)

    ##def remove_all_formats(self):
        ##"""."""
        ##start, end = self.get_selection()
        
        ##log.debug("Removing all format for range %d - %d" %
                  ##(start.get_offset(), end.get_offset()))
        
        ##self.remove_all_tags(start, end)
        
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(MarkupBuffer)
