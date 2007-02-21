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


class MarkupParser(ContentHandler):
    """A simple ContentHandler class to parse Gramps markup'ed text.
    
    Use it with xml.sax.parse() or xml.sax.parseString(). A root tag, 'gramps',
    is required. Parsing result can be obtained via the public attributes of
    the class:    
    @attr content: clean text
    @attr type: str
    @attr elements: list of markup elements 
    @attr type: list[tuple((start, end), name, attrs),]
    
    """
    (EVENT_START,
     EVENT_END) = range(2)

    def startDocument(self):
        self._open_document = False
        self._open_elements = []
        self.elements = []
        self.content = ""
        
    def endDocument(self):
        self._open_document = False

    def startElement(self, name, attrs):
        if not self._open_document:
            if name == 'gramps':
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
        if name == 'gramps':
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
    properly in case of partially overlapping markups.
    It is assumed that 'start name' and 'end name' are equal (e.g. <b>, </b>).
    
    """
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
        
        @param tagdict: dictionary of tags with start and end indices
        @param type: {TextTag: [(start, end),]}
        @return: eventdict
        @rtype: {index: [(TextTag, event_type, pair_index),]}
         index: place of the event
         TextTag: tag to apply 
         event_type: START or END event
         pair_index: index of the pair event, used for sorting
        
        """
        eventdict = {}
        for (start, end), name, attrs in elements:
            # insert START events
            if eventdict.has_key(start):
                eventdict[start].append((name, MarkupParser.EVENT_START, end))
            else:
                eventdict[start] = [(name, MarkupParser.EVENT_START, end)]
            # insert END events
            if eventdict.has_key(end):
                eventdict[end].append((name, MarkupParser.EVENT_END, start))
            else:
                eventdict[end] = [(name, MarkupParser.EVENT_END, start)]

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
        tag_a, type_a, pair_a = event_a
        tag_b, type_b, pair_b = event_b
        
        if (type_a + type_b) == (MarkupParser.EVENT_START +
                                 MarkupParser.EVENT_END):
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
        self._writer.startElement('gramps', self._attrs)
        
        # split the elements to events
        events = self._elements_to_events(elements)
        
        # feed the events into the xml generator
        last_pos = 0
        indices = events.keys()
        indices.sort()
        for index in indices:
            self._writer.characters(text[last_pos:index])
            for name, event_type, p in events[index]:
                if event_type == MarkupParser.EVENT_START:
                    self._startElement(name)
                elif event_type == MarkupParser.EVENT_END:
                    self._endElement(name)
            last_pos = index
        self._writer.characters(text[last_pos:])
        
        # close root element and end doc
        self._writer.endElement('gramps')
        self._writer.endDocument()
        
        # copy result
        self.content = self._output.getvalue()
        
class MarkupBuffer(gtk.TextBuffer):
    """An extended TextBuffer with Gramps XML markup string interface.
    
    It implements MarkupParser and MarkupWriter on the input/output interface.
    Also translates Gramps XML markup language to gtk.TextTag's and vice versa.
    
    Based on 'gourmet-0.13.3' L{http://grecipe-manager.sourceforge.net}
    Pango markup format is replaces by custom Gramps XML format.
    
    """
    texttag_to_xml = {
        'weight700': 'b',
        'style2': 'i',
        'underline1': 'u',
    }
    
    xml_to_texttag = {
        'b': ('weight', 700),
        'i': ('style', 2),
        'u': ('underline', 1),
    }

    def __init__(self):
        self.parser = MarkupParser()
        self.writer = MarkupWriter()
        self.tags = {}
        self.tag_markup = {}
        gtk.TextBuffer.__init__(self)

    def set_text(self, xmltext):
        """Set the content of the buffer with markup tags."""
        try:
            parseString(xmltext, self.parser)
            text = self.parser.content
        except:
            # if parse fails remove all tags and use clear text instead
            text = re.sub(r'(<.*?>)', '', xmltext)
            text = saxutils.unescape(text)
        
        gtk.TextBuffer.set_text(self, text)

        for element in self.parser.elements:
            self.add_element_to_buffer(element)

    def add_element_to_buffer(self, elem):
        """Apply the xml element to the buffer"""
        (start, end), name, attrs = elem

        tag = self.get_tag_from_element(name)

        if tag:
            start_iter = self.get_iter_at_offset(start)
            end_iter = self.get_iter_at_offset(end)

            self.apply_tag(tag, start_iter, end_iter)

    def get_tag_from_element(self, name):
        """Convert xml element to gtk.TextTag."""
        if not self.xml_to_texttag.has_key(name):
            return None
            
        prop, val = self.xml_to_texttag[name]
            
        key = "%s%s" % (prop, val)
        if not self.tags.has_key(key):
            self.tags[key] = self.create_tag()
            self.tags[key].set_property(prop, val)
            self.tag_markup[self.tags[key]] = self.texttag_to_xml[key]

        return self.tags[key]

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
        tags = self.get_tags()
        
        if len(tags):
            # convert the tags to xml elements
            elements = self.get_elements(tags)
            # feed the elements into the xml writer
            self.writer.generate(txt, elements)
            txt = self.writer.content
        
        return txt

    def get_tags(self):
        """Extract TextTags from buffer.
        
        @return: tagdict
        @rtype: {TextTag: [(start, end),]}
        
        """
        tagdict = {}
        for pos in range(self.get_char_count()):
            iter = self.get_iter_at_offset(pos)
            for tag in iter.get_tags():
                if tagdict.has_key(tag):
                    if tagdict[tag][-1][1] == pos - 1:
                        tagdict[tag][-1] = (tagdict[tag][-1][0], pos)
                    else:
                        tagdict[tag].append((pos, pos))
                else:
                    tagdict[tag]=[(pos, pos)]
        return tagdict
    
    def get_elements(self, tagdict):
        """Convert TextTags to xml elements.
        
        Create the format what MarkupWriter likes
        @param tagdict: TextTag dictionary
        @param type: {TextTag: [(start, end),]}
        @return: elements; xml element list
        @rtype: [((start, end), name, attrs)]
        
        """
        elements = []
        for text_tag, indices in tagdict.items():
            for start_idx, end_idx in indices:
                elements.append(((start_idx, end_idx+1),
                                 self.tag_markup[text_tag],
                                 None))
        return elements

    ##def pango_color_to_gdk(self, pc):
        ##return gtk.gdk.Color(pc.red, pc.green, pc.blue)

    ##def color_to_hex(self, color):
        ##hexstring = ""
        ##for col in 'red', 'green', 'blue':
            ##hexfrag = hex(getattr(color, col) / (16 * 16)).split("x")[1]
            ##if len(hexfrag) < 2:
                ##hexfrag = "0" + hexfrag
            ##hexstring += hexfrag
        ##return hexstring
        
    def get_selection(self):
        bounds = self.get_selection_bounds()
        if not bounds:
            iter = self.get_iter_at_mark(self.insert)
            if iter.inside_word():
                start_pos = iter.get_offset()
                iter.forward_word_end()
                word_end = iter.get_offset()
                iter.backward_word_start()
                word_start = iter.get_offset()
                iter.set_offset(start_pos)
                bounds = (self.get_iter_at_offset(word_start),
                          self.get_iter_at_offset(word_end + 1))
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

    def remove_all_tags(self):
        selection = self.get_selection()
        if selection:
            for t in self.tags.values():
                self.remove_tag(t, *selection)

class EditorBuffer(MarkupBuffer):
    """An interactive interface to allow markup a gtk.TextBuffer.

    normal_button is a widget whose clicked signal will make us normal
    toggle_widget_alist is a list that looks like this: [(widget, tag_name),]

    Based on 'gourmet-0.13.3' L{http://grecipe-manager.sourceforge.net}
    Pango markup format is replaces by custom Gramps XML format.
    
    """
    __gtype_name__ = 'EditorBuffer'

    def __init__(self, normal_button=None, toggle_widget_alist=[]):
        MarkupBuffer.__init__(self)
        if normal_button:
            normal_button.connect('clicked',lambda *args: self.remove_all_tags())
        self.tag_widgets = {}
        self.internal_toggle = False
        self.insert = self.get_insert()
        for widg, name in toggle_widget_alist:
            self.setup_widget(widg, name)

    # Virtual methods

    def do_changed(self):
        if not hasattr(self,'last_mark'):
            return

        # If our insertion point has a mark, we want to apply the tag
        # each time the user types...
        old_itr = self.get_iter_at_mark(self.last_mark)
        insert_itr = self.get_iter_at_mark(self.insert)
        if old_itr != insert_itr:
            # Use the state of our widgets to determine what
            # properties to apply...
            for tag, w in self.tag_widgets.items():
                if w.get_active():
                    self.apply_tag(tag, old_itr, insert_itr)

    def do_mark_set(self, iter, mark):
        # Every time the cursor moves, update our widgets that reflect
        # the state of the text.
        if hasattr(self, '_in_mark_set') and self._in_mark_set:
            return

        self._in_mark_set = True
        if mark.get_name() == 'insert':
            for tag,widg in self.tag_widgets.items():
                active = True
                if not iter.has_tag(tag):
                    active = False
                self.internal_toggle = True
                widg.set_active(active)
                self.internal_toggle = False
        if hasattr(self, 'last_mark'):                
            self.move_mark(self.last_mark, iter)
        else:
            self.last_mark = self.create_mark('last', iter, left_gravity=True)
        self._in_mark_set = False

    # Private

    def _toggle(self, widget, tag):
        if self.internal_toggle:
            return
        
        if widget.get_active():
            self.apply_tag_to_selection(tag)
        else:
            self.remove_tag_from_selection(tag)

    # Public API

    def setup_widget_from_xml(self, widg, xmlstring):
        """Setup widget from an xml markup string."""
        try:
            parseString("<gramps>%s</gramps>" % xmlstring, self.parser)
        except:
            log.error('"%s" is not a valid Gramps XML format.' % xmlstring)
        
        (start, end), name, attrs = self.parser.elements[0]
        
        return self.setup_widget(widg, name)

    def setup_widget(self, widg, name):
        """Setup widget from Gramps tag name."""
        tag = self.get_tag_from_element(name)
        self.tag_widgets[tag] = widg
        return widg.connect('toggled', self._toggle, tag)
    
if gtk.pygtk_version < (2,8,0):
    gobject.type_register(EditorBuffer)


if __name__ == '__main__':
    import sys
    
    def main(args):
        win = gtk.Window()
        win.set_title('MarkupBuffer test window')
        win.set_position(gtk.WIN_POS_CENTER)
        def cb(window, event):
            gtk.main_quit()
        win.connect('delete-event', cb)

        accel_group = gtk.AccelGroup()
        win.add_accel_group(accel_group)
        
        vbox = gtk.VBox()
        win.add(vbox)

        text = gtk.TextView()
        text.set_accepts_tab(True)

        flowed = gtk.RadioButton(None, 'Flowed')
        format = gtk.RadioButton(flowed, 'Formatted')

        #if self.note_obj and self.note_obj.get_format():
            #self.format.set_active(True)
            #self.text.set_wrap_mode(gtk.WRAP_NONE)
        #else:
            #self.flowed.set_active(True)
            #self.text.set_wrap_mode(gtk.WRAP_WORD)
        #self.spellcheck = Spell.Spell(self.text)

        #flowed.connect('toggled', flow_changed)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.add(text)   

        vbox.pack_start(scroll, True)
        vbox.set_spacing(6)
        vbox.set_border_width(6)

        hbox = gtk.HBox()
        hbox.set_spacing(12)
        hbox.set_border_width(6)
        hbox.pack_start(flowed, False)
        hbox.pack_start(format, False)

        vbox.pack_start(hbox, False)

        #self.pack_start(vbox, True)
        buf = EditorBuffer()
        text.set_buffer(buf)
        tooltips = gtk.Tooltips()
        for tip,stock,font,accel in [('Italic',gtk.STOCK_ITALIC,'<i>i</i>','<Control>I'),
                                     ('Bold',gtk.STOCK_BOLD,'<b>b</b>','<Control>B'),
                                     ('Underline',gtk.STOCK_UNDERLINE,'<u>u</u>','<Control>U'),
                                     ]:
            button = gtk.ToggleButton()
            image = gtk.Image()
            image.set_from_stock(stock, gtk.ICON_SIZE_MENU)
            button.set_image(image)
            tooltips.set_tip(button, tip)
            button.set_relief(gtk.RELIEF_NONE)
            buf.setup_widget_from_xml(button,font)
            key, mod = gtk.accelerator_parse(accel)
            button.add_accelerator('activate', accel_group,
                                   key, mod, gtk.ACCEL_VISIBLE)
            hbox.pack_start(button, False)

        buf.set_text('<gramps>'
                     '<b>Bold</b>. <i>Italic</i>. <u>Underline</u>.'
                     '</gramps>')
    
        win.show_all()
        gtk.main()
                

    stderrh = logging.StreamHandler(sys.stderr)
    stderrh.setLevel(logging.DEBUG)
    
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    log.addHandler(stderrh)
    
    sys.exit(main(sys.argv))
