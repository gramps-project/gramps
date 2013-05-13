##
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007       Brian G. Matherly
# Copyright (C) 2010       Peter Landgren
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Adam Stein <adam@csh.rit.edu>
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2013       Paul Franklin
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

"""
Provide utilities for printing endnotes in text reports.
"""
from ..docgen import FontStyle, ParagraphStyle, FONT_SANS_SERIF
from ...lib import NoteType, Citation
from ...const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from ...utils.string import confidence

def add_endnote_styles(style_sheet):
    """
    Add paragraph styles to a style sheet to be used for displaying endnotes.
    
    @param style_sheet: Style sheet
    @type style_sheet: L{docgen.StyleSheet}
    """
    font = FontStyle()
    font.set(face=FONT_SANS_SERIF, size=14, italic=1)
    para = ParagraphStyle()
    para.set_font(font)
    para.set_header_level(2)
    para.set_top_margin(0.2)
    para.set_bottom_margin(0.2)
    para.set_description(_('The style used for the generation header.'))
    style_sheet.add_paragraph_style("Endnotes-Header", para)

    para = ParagraphStyle()
    para.set(first_indent=-0.75, lmargin=.75)
    para.set_top_margin(0.2)
    para.set_bottom_margin(0.0)
    para.set_description(_('The basic style used for the endnotes source display.'))
    style_sheet.add_paragraph_style("Endnotes-Source", para)
    
    para = ParagraphStyle()
    para.set(lmargin=.75)
    para.set_top_margin(0.2)
    para.set_bottom_margin(0.0)
    para.set_description(_('The basic style used for the endnotes notes display.'))
    style_sheet.add_paragraph_style("Endnotes-Source-Notes", para)

    para = ParagraphStyle()
    para.set(first_indent=-0.9, lmargin=1.9)
    para.set_top_margin(0.2)
    para.set_bottom_margin(0.0)
    para.set_description(_('The basic style used for the endnotes reference display.'))
    style_sheet.add_paragraph_style("Endnotes-Ref", para)
    
    para = ParagraphStyle()
    para.set(lmargin=1.9)
    para.set_top_margin(0.2)
    para.set_bottom_margin(0.0)
    para.set_description(_('The basic style used for the endnotes reference notes display.'))
    style_sheet.add_paragraph_style("Endnotes-Ref-Notes", para)

def cite_source(bibliography, database, obj):
    """
    Cite any sources for the object and add them to the bibliography.
    
    @param bibliography: The bibliography to contain the citations.
    @type bibliography: L{Bibliography}
    @param obj: An object with source references.
    @type obj: L{gen.lib.CitationBase}
    """
    txt = ""
    slist = obj.get_citation_list()
    if slist:
        first = 1
        for ref in slist:
            if not first:
                txt += ', '
            first = 0
            citation = database.get_citation_from_handle(ref)
            (cindex, key) = bibliography.add_reference(citation)
            txt += "%d" % (cindex + 1)
            if key is not None:
                txt += key
    return txt

def write_endnotes(bibliography, database, doc, printnotes=False, links=False,
                   elocale=glocale):
    """
    Write all the entries in the bibliography as endnotes.
    
    If elocale is passed in (a GrampsLocale), then (insofar as possible)
    the translated values will be returned instead.

    @param bibliography: The bibliography that contains the citations.
    @type bibliography: L{Bibliography}
    @param database: The database that the sources come from.
    @type database: DbBase
    @param doc: The document to write the endnotes into.
    @type doc: L{docgen.TextDoc}
    @param printnotes: Indicate if the notes attached to a source must be
            written too.
    @type printnotes: bool
    @param links: Indicate if URL links should be makde 'clickable'.
    @type links: bool
    @param elocale: allow deferred translation of dates and strings
    @type elocale: a GrampsLocale instance
    """
    if bibliography.get_citation_count() == 0:
        return

    trans_text = elocale.translation.gettext
    # trans_text is a defined keyword (see po/update_po.py, po/genpot.sh)

    doc.start_paragraph('Endnotes-Header')
    doc.write_text(trans_text('Endnotes'))
    doc.end_paragraph()
    
    cindex = 0
    for citation in bibliography.get_citation_list():
        cindex += 1
        source = database.get_source_from_handle(citation.get_source_handle())
        first = True
        
        doc.start_paragraph('Endnotes-Source', "%d." % cindex)
        doc.write_text(_format_source_text(source), links=links)
        doc.end_paragraph()
        
        if printnotes:
            _print_notes(source, database, doc, 'Endnotes-Source-Notes', links)

        for key, ref in citation.get_ref_list():
            doc.start_paragraph('Endnotes-Ref', "%s:" % key)
            doc.write_text(_format_ref_text(ref, key, elocale), links=links)
            doc.end_paragraph()

            if printnotes:
                _print_notes(ref, database, doc, 'Endnotes-Ref-Notes', links)

def _format_source_text(source):
    if not source: return ""

    src_txt = ""
    
    if source.get_author():
        src_txt += source.get_author()
    
    if source.get_title():
        if src_txt:
            src_txt += ", "
        src_txt += '"%s"' % source.get_title()
        
    if source.get_publication_info():
        if src_txt:
            src_txt += ", "
        src_txt += source.get_publication_info()
        
    if source.get_abbreviation():
        if src_txt:
            src_txt += ", "
        src_txt += "(%s)" % source.get_abbreviation()
        
    return src_txt

def _format_ref_text(ref, key, elocale):
    if not ref: return ""
    
    ref_txt = ""
    
    datepresent = False
    date = ref.get_date_object()
    if date is not None and not date.is_empty():
        datepresent = True
    if datepresent:
        if ref.get_page():
            ref_txt = "%s - %s" % (ref.get_page(), elocale.get_date(date))
        else:
            ref_txt = elocale.get_date(date)
    else:
        ref_txt = ref.get_page()
        
    # Print only confidence level if it is not Normal
    if (ref.get_confidence_level() != Citation.CONF_NORMAL
        and elocale == glocale): # FIXME
        # the correct fix would be to enable deferred translation for at
        # least the "confidence" list of strings (in gen/utils/string.py),
        # and possibly others too if they need deferred translation, but that
        # would require searching out every use of a "confidence" string and
        # translating it there, either to the UI language or to a "deferred"
        # language (e.g. when used in a report, as here in this module), but
        # that would require an immense amount of time and testing and since
        # a release is imminent this is not the time to consider that, so I
        # have instead added the above line, which will disable the typeout
        # of any "confidence" rating /if/ a translated value is needed, while
        # continuing to show the "confidence" for the normal case of a user
        # running a report in their own language (when elocale==glocale)
        ref_txt += " [" + confidence[ref.get_confidence_level()] + "]"
    
    return ref_txt

def _print_notes(obj, db, doc, style, links):
    note_list = obj.get_note_list()
    ind = 1
    for notehandle in note_list: 
        note = db.get_note_from_handle(notehandle)
        contains_html = note.get_type() == NoteType.HTML_CODE
        doc.write_styled_note(note.get_styledtext(), note.get_format(), style,
                              contains_html=contains_html, links=links)
        ind += 1
