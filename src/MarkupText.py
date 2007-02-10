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

#-------------------------------------------------------------------------
#
# Python classes
#
#-------------------------------------------------------------------------
from xml.sax import saxutils, xmlreader
from cStringIO import StringIO

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
import logging
log = logging.getLogger(".MarkupText")

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
import gtk
import pango

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
(EVENT_START,
 EVENT_END) = range(2)

class NoteXMLWriter(saxutils.XMLGenerator):
    """Generate XML markup text for Notes.
    
    Provides additional feature of accounting opened tags and closing them
    properly in case of partialy overlapping markups.
    It is assumed that 'start name' and 'end name' are equal (e.g. <b>, </b>).
    
    """
    def __init__(self, output, encoding):
        saxutils.XMLGenerator.__init__(self, output, encoding)
        self.attrs = xmlreader.AttributesImpl({})
        #saxutils.XMLGenerator.startElement(self, u'gramps', self.attrs)
        self.open_elements = []
    
    def startElement(self, name, attrs=None):
        if not attrs:
            attrs = self.attrs
        saxutils.XMLGenerator.startElement(self, name, attrs)
        self.open_elements.append(name)
        
    def endElement(self, name):
        if not len(self.open_elements):
            log.debug("Trying to close element '%s' when non is open" % name)
            return
        
        tmp_list = []
        elem = ''
        
        # close all open elements until we reach to the requested one
        while elem != name:
            try:
                elem = self.open_elements.pop()
                saxutils.XMLGenerator.endElement(self, elem)
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
                self.startElement(elem)
            except:
                break

    def close(self):
        #saxutils.XMLGenerator.endElement(self, u'gramps')
        self.endDocument()

class MarkupBuffer(gtk.TextBuffer):
    fontdesc_to_attr_table = {
        'family': [pango.AttrFamily, ""],
        'style': [pango.AttrStyle, pango.STYLE_NORMAL],        
        'variant': [pango.AttrVariant, pango.VARIANT_NORMAL],
        'weight': [pango.AttrWeight, pango.WEIGHT_NORMAL],
        'stretch': [pango.AttrStretch, pango.STRETCH_NORMAL],
    }

    pango_translation_properties = {
        # pango ATTR TYPE : (pango attr property / tag property)
        pango.ATTR_SIZE : 'size',
        pango.ATTR_WEIGHT: 'weight',
        pango.ATTR_UNDERLINE: 'underline',
        pango.ATTR_STRETCH: 'stretch',
        pango.ATTR_VARIANT: 'variant',
        pango.ATTR_STYLE: 'style',
        pango.ATTR_SCALE: 'scale',
        pango.ATTR_STRIKETHROUGH: 'strikethrough',
        pango.ATTR_RISE: 'rise',
    }

    attval_to_markup = {
        'underline': {pango.UNDERLINE_SINGLE: 'single',
                      pango.UNDERLINE_DOUBLE: 'double',
                      pango.UNDERLINE_LOW: 'low',
                      pango.UNDERLINE_NONE: 'none'
                      },
        'stretch': {pango.STRETCH_ULTRA_EXPANDED: 'ultraexpanded',
                    pango.STRETCH_EXPANDED: 'expanded',
                    pango.STRETCH_EXTRA_EXPANDED: 'extraexpanded',
                    pango.STRETCH_EXTRA_CONDENSED: 'extracondensed',
                    pango.STRETCH_ULTRA_CONDENSED: 'ultracondensed',                                              
                    pango.STRETCH_CONDENSED: 'condensed',
                    pango.STRETCH_NORMAL: 'normal',
                    },
        'variant': {pango.VARIANT_NORMAL: 'normal',
                    pango.VARIANT_SMALL_CAPS: 'smallcaps',
                    },
        'style': {pango.STYLE_NORMAL: 'normal',
                  pango.STYLE_OBLIQUE: 'oblique',
                  pango.STYLE_ITALIC: 'italic',
                  },
        'stikethrough': {1: 'true',
                         True: 'true',
                         0: 'false',
                         False: 'false'
                         },
    }

    # This is an ugly workaround until we get rid of pango
    # only these markups are curently supported
    pango_shortcut = {
        'style2': 'i',
        'weight700': 'b',
        'underline1': 'u',
    }

    def __init__(self):
        self.tagdict = {}
        self.tags = {}
        self.tag_markup = {}
        gtk.TextBuffer.__init__(self)

    def set_text(self, pango_text):
        try:
            attrlist, text, accel = pango.parse_markup(pango_text, u'\x00')
        except:
            log.debug('Escaping text, we seem to have a problem here!')
            escaped_text = saxutils.escape(pango_text)
            attrlist, text, accel = pango.parse_markup(escaped_text, u'\x00')

        gtk.TextBuffer.set_text(self, text)

        attriter = attrlist.get_iterator()
        self.add_iter_to_buffer(attriter)        
        while attriter.next():
            self.add_iter_to_buffer(attriter)

    def add_iter_to_buffer(self, attriter):
        """Insert attributes into the buffer.
        
        Convert the pango.Attribute at the received pango.AttrIterator
        to gtk.TextTag and apply them on the buffer at the proper indices
        
        """
        range = attriter.range()
        start_iter = self.get_iter_at_offset(range[0])
        end_iter = self.get_iter_at_offset(range[1])

        font, lang, attrs = attriter.get_font()
        tags = self.get_tags_from_attrs(font, lang, attrs)

        for tag in tags:
            self.apply_tag(tag, start_iter, end_iter)
        
    def get_tags_from_attrs(self, font, lang, attrs):
        """Convert pango.Attribute to gtk.TextTag."""
        tags = []

        if font:            
            font, fontattrs = self.fontdesc_to_attrs(font)
            fontdesc = font.to_string()
            if fontattrs:
                attrs.extend(fontattrs)
            ##if fontdesc and fontdesc != 'Normal':
                ##if not self.tags.has_key(font.to_string()):                    
                    ##tag = self.create_tag()
                    ##tag.set_property('font-desc', font)
                    ##if not self.tagdict.has_key(tag):
                        ##self.tagdict[tag] = {}
                    ##self.tagdict[tag]['font_desc'] = font.to_string()
                    ##self.tags[font.to_string()] = tag
                ##tags.append(self.tags[font.to_string()])

        ##if lang:
            ##if not self.tags.has_key(lang):
                ##tag = self.create_tag()
                ##tag.set_property('language', lang)
                ##self.tags[lang] = tag
            ##tags.append(self.tags[lang])

        if attrs:
            for a in attrs:
                ##if a.type == pango.ATTR_FOREGROUND:
                    ##gdkcolor = self.pango_color_to_gdk(a.color)
                    ##key = 'foreground%s' % self.color_to_hex(gdkcolor)
                    ##if not self.tags.has_key(key):
                        ##self.tags[key] = self.create_tag()
                        ##self.tags[key].set_property('foreground-gdk', gdkcolor)
                        ##self.tagdict[self.tags[key]] = {}
                        ##self.tagdict[self.tags[key]]['foreground'] = "#%s"\
                            ##% self.color_to_hex(gdkcolor)
                    ##tags.append(self.tags[key])
                    ##continue
                ##if a.type == pango.ATTR_BACKGROUND:
                    ##gdkcolor = self.pango_color_to_gdk(a.color)
                    ##key = 'background%s' % self.color_to_hex(gdkcolor)
                    ##if not self.tags.has_key(key):
                        ##self.tags[key] = self.create_tag()
                        ##self.tags[key].set_property('background-gdk', gdkcolor)
                        ##self.tagdict[self.tags[key]] = {}
                        ##self.tagdict[self.tags[key]]['background'] = "#%s"\
                            ##% self.color_to_hex(gdkcolor)
                    ##tags.append(self.tags[key])
                    ##continue
                if self.pango_translation_properties.has_key(a.type):
                    prop = self.pango_translation_properties[a.type]
                    log.debug('setting property %s of %s '
                              '(type: %s)' % (prop, a, a.type))
                    val = getattr(a, 'value')
                    mval = val
                    if self.attval_to_markup.has_key(prop):
                        log.debug("converting %s in %s" % (prop,val))
                        if self.attval_to_markup[prop].has_key(val):
                            mval = self.attval_to_markup[prop][val]
                        else:
                            log.debug("hmmm, didn't know what to do"
                                      " with value %s" % val)
                    key = "%s%s" % (prop, val)
                    if not self.tags.has_key(key):
                        self.tags[key] = self.create_tag()
                        self.tags[key].set_property(prop,val)
                        self.tagdict[self.tags[key]] = {}
                        self.tagdict[self.tags[key]][prop] = mval
                        self.tag_markup[self.tags[key]] = self.pango_shortcut[key]
                    tags.append(self.tags[key])
                else:
                    log.debug("Don't know what to do with attr %s" % a)

        return tags
    
    def get_text(self, start=None, end=None, include_hidden_chars=True):
        """Returns the buffer text with Pango markup tags."""
        tagdict = self.get_tags()
        eventlist = self.get_event_list(tagdict)

        if not start:
            start = self.get_start_iter()
        if not end:
            end = self.get_end_iter()
        txt = unicode(gtk.TextBuffer.get_text(self, start, end))
        
        output = StringIO()
        note_xml = NoteXMLWriter(output, 'utf-8')

        last_pos = 0
        indices = eventlist.keys()
        indices.sort()
        for index in indices:
            note_xml.characters(txt[last_pos:index])
            for tag, event_type, p in eventlist[index]:
                if event_type == EVENT_START:
                    note_xml.startElement(self.tag_markup[tag][EVENT_START])
                elif event_type == EVENT_END:
                    note_xml.endElement(self.tag_markup[tag][EVENT_START])
            last_pos = index
        note_xml.characters(txt[last_pos:])
        note_xml.close()

        ##cuts = {}
        ##for text_tag, range in tagdict.items():
            ##stag, etag = self.tag_to_markup(text_tag)
            ##for st, e in range:
                ### insert start tag
                ##if cuts.has_key(st):
                    ##cuts[st].append(stag)
                ##else:
                    ##cuts[st] = [stag]
                ### insert end tag
                ##if cuts.has_key(e + 1):
                    ##cuts[e + 1] = [etag] + cuts[e + 1]
                ##else:
                    ##cuts[e + 1] = [etag]

        ##last_pos = 0
        ##outbuff = ""
        ##cut_indices = cuts.keys()
        ##cut_indices.sort()        
        ##soffset = start.get_offset()
        ##eoffset = end.get_offset()
        ##cut_indices = filter(lambda i: eoffset >= i >= soffset, cut_indices)
        ##for c in cut_indices:
            ##if not last_pos == c:
                ##outbuff += saxutils.escape(txt[last_pos:c])
                ##last_pos = c
            ##for tag in cuts[c]:
                ##outbuff += tag
        ##outbuff += saxutils.escape(txt[last_pos:])
        ##return outbuff
        return output.getvalue()

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

    def get_event_list(self, tagdict):
        """Create an event list for XML writer.
        
        @param tagdict: tag dict to convert from
        @param type: {TextTag: [(start, end),]}
        @return: eventlist
        @rtype: {index: [(TextTag, EVENT_TYPE, pair_index),]}
        
        """
        eventlist = {}
        for text_tag, indices in tagdict.items():
            for start_idx, end_idx in indices:
                # end element goes after the last markup'ed char
                end_idx += 1
                # insert START events
                if eventlist.has_key(start_idx):
                    eventlist[start_idx].append((text_tag, EVENT_START, end_idx))
                else:
                    eventlist[start_idx] = [(text_tag, EVENT_START, end_idx)]
                # insert END events
                if eventlist.has_key(end_idx):
                    eventlist[end_idx].append((text_tag, EVENT_END, start_idx))
                else:
                    eventlist[end_idx] = [(text_tag, EVENT_END, start_idx)]

        # sort events at the same index
        indices = eventlist.keys()
        #indices.sort()
        for idx in indices:
            if len(eventlist[idx]) > 1:
                eventlist[idx].sort(self.sort_events)
                
        return eventlist

    def sort_events(self, event_a, event_b):
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
        
        if (type_a + type_b) == (EVENT_START + EVENT_END):
            return type_b - type_a
        else:
            return pair_b - pair_a

    ##def tag_to_markup(self, tag):
        ##"""Convert a gtk.TextTag to Pango markup tags."""
        ##stag = "<span"
        ##for k, v in self.tagdict[tag].items():
            ##stag += ' %s="%s"' % (k, v)
        ##stag += ">"
        ##return stag, "</span>"
        ##stag = "<%s>" % self.tag_markup[tag]
        ##etag = "</%s>" % self.tag_markup[tag]
        ##return stag,etag
        

    def fontdesc_to_attrs(self, font):
        """Convert pango.FontDescription to gtk.Attribute."""
        nicks = font.get_set_fields().value_nicks
        attrs = []
        for n in nicks:
            if self.fontdesc_to_attr_table.has_key(n):
                Attr, norm = self.fontdesc_to_attr_table[n]
                # create an attribute with our current value
                attrs.append(Attr(getattr(font, 'get_%s'%n)()))
                # unset our font's value
                getattr(font,'set_%s'%n)(norm)
        return font, attrs
        
    def pango_color_to_gdk(self, pc):
        return gtk.gdk.Color(pc.red, pc.green, pc.blue)

    def color_to_hex(self, color):
        hexstring = ""
        for col in 'red', 'green', 'blue':
            hexfrag = hex(getattr(color, col) / (16 * 16)).split("x")[1]
            if len(hexfrag) < 2:
                hexfrag = "0" + hexfrag
            hexstring += hexfrag
        return hexstring
        
    ##def apply_font_and_attrs(self, font, attrs):
        ##tags = self.get_tags_from_attrs(font,None,attrs)
        ##for t in tags: self.apply_tag_to_selection(t)

    ##def remove_font_and_attrs(self, font, attrs):
        ##tags = self.get_tags_from_attrs(font,None,attrs)
        ##for t in tags: self.remove_tag_from_selection(t)

    ##def setup_default_tags(self):
        ##self.italics = self.get_tags_from_attrs(None,None,
                                                ##[pango.AttrStyle('italic')])[0]
        ##self.bold = self.get_tags_from_attrs(None,None,
                                             ##[pango.AttrWeight('bold')])[0]
        ##self.underline = self.get_tags_from_attrs(None,None,
                                                  ##[pango.AttrUnderline('single')])[0]

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
    """An interactive interface to allow marking up a gtk.TextBuffer.

    normal_button is a widget whose clicked signal will make us normal
    toggle_widget_alist is a list that looks like this:
    [(widget, (font,attr)),
    (widget2, (font,attr))]

    """
    __gtype_name__ = 'EditorBuffer'

    def __init__(self, normal_button=None, toggle_widget_alist=[]):
        MarkupBuffer.__init__(self)
        if normal_button:
            normal_button.connect('clicked',lambda *args: self.remove_all_tags())
        self.tag_widgets = {}
        self.internal_toggle = False
        self.insert = self.get_insert()
        for w, tup in toggle_widget_alist:
            self.setup_widget(w, *tup)

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
            for tags, w in self.tag_widgets.items():
                if w.get_active():
                    #print 'apply tags...',tags
                    for t in tags:
                        self.apply_tag(t, old_itr, insert_itr)

    def do_mark_set(self, iter, mark):
        # Every time the cursor moves, update our widgets that reflect
        # the state of the text.
        if hasattr(self, '_in_mark_set') and self._in_mark_set:
            return

        self._in_mark_set = True
        if mark.get_name() == 'insert':
            for tags,widg in self.tag_widgets.items():
                active = True
                for t in tags:
                    if not iter.has_tag(t):
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

    def _toggle(self, widget, tags):
        if self.internal_toggle: return
        if widget.get_active():
            for t in tags: self.apply_tag_to_selection(t)
        else:
            for t in tags: self.remove_tag_from_selection(t)
            
        log.debug("Text: %s" % self.get_text())

    # Public API

    def setup_widget_from_pango(self, widg, markupstring):
        """Setup widget from a pango markup string."""
        a, t, s = pango.parse_markup(markupstring, u'\x00')
        ai = a.get_iterator()
        # we're gonna use only the first attr from the attrlist
        font, lang, attrs = ai.get_font()
        return self.setup_widget(widg, font, attrs)

    def setup_widget(self, widg, font, attr):
        tags = self.get_tags_from_attrs(font, None, attr)
        self.tag_widgets[tuple(tags)] = widg
        return widg.connect('toggled', self._toggle, tags)

if gtk.pygtk_version < (2,8,0):
    gobject.type_register(EditorBuffer)


def main(args):
    win = gtk.Window()
    win.set_title('MarkupBuffer test window')
    win.set_position(gtk.WIN_POS_CENTER)
    def cb(window, event):
        gtk.main_quit()
    win.connect('delete-event', cb)
    
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
    for tip,stock,font in [('Italic',gtk.STOCK_ITALIC,'<i>italic</i>'),
                           ('Bold',gtk.STOCK_BOLD,'<b>bold</b>'),
                           ('Underline',gtk.STOCK_UNDERLINE,'<u>underline</u>'),
                           ]:
        button = gtk.ToggleButton()
        image = gtk.Image()
        image.set_from_stock(stock, gtk.ICON_SIZE_MENU)
        button.set_image(image)
        tooltips.set_tip(button, tip)
        button.set_relief(gtk.RELIEF_NONE)
        buf.setup_widget_from_pango(button,font)
        hbox.pack_start(button, False)

    win.show_all()
    gtk.main()
                
if __name__ == '__main__':
    import sys

    stderrh = logging.StreamHandler(sys.stderr)
    stderrh.setLevel(logging.DEBUG)
    
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    log.addHandler(stderrh)
    
    sys.exit(main(sys.argv))
