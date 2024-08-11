##
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007       Brian G. Matherly
# Copyright (C) 2010       Peter Landgren
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Adam Stein <adam@csh.rit.edu>
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2013,2015  Paul Franklin
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

"""
Provide utilities for printing endnotes in text reports.
"""

# -------------------------------------------------------------------------
#
# Standard python modules
#
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ...const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from ..docgen import FontStyle, ParagraphStyle, FONT_SANS_SERIF
from ...lib import NoteType, Citation
from ...utils.string import conf_strings
from ...config import config
from ..utils import get_cite


def add_endnote_styles(style_sheet):
    """
    Add paragraph styles to a style sheet to be used for displaying endnotes.

    :param style_sheet: Style sheet
    :type style_sheet: :class:`.StyleSheet`
    """
    font = FontStyle()
    font.set(face=FONT_SANS_SERIF, size=14, italic=1)
    para = ParagraphStyle()
    para.set_font(font)
    para.set_header_level(2)
    para.set_top_margin(0.2)
    para.set_bottom_margin(0.2)
    para.set_description(_("The style used for the generation header."))
    style_sheet.add_paragraph_style("Endnotes-Header", para)

    para = ParagraphStyle()
    para.set(first_indent=-0.75, lmargin=0.75)
    para.set_top_margin(0.2)
    para.set_bottom_margin(0.0)
    para.set_description(_("The basic style used for " "the endnotes source display."))
    style_sheet.add_paragraph_style("Endnotes-Source", para)

    para = ParagraphStyle()
    para.set(lmargin=0.75)
    para.set_top_margin(0.2)
    para.set_bottom_margin(0.0)
    para.set_description(_("The basic style used for " "the endnotes notes display."))
    style_sheet.add_paragraph_style("Endnotes-Source-Notes", para)

    para = ParagraphStyle()
    para.set(first_indent=-0.9, lmargin=1.9)
    para.set_top_margin(0.2)
    para.set_bottom_margin(0.0)
    para.set_description(
        _("The basic style used for " "the endnotes reference display.")
    )
    style_sheet.add_paragraph_style("Endnotes-Ref", para)

    para = ParagraphStyle()
    para.set(lmargin=1.9)
    para.set_top_margin(0.2)
    para.set_bottom_margin(0.0)
    para.set_description(
        _("The basic style used for " "the endnotes reference notes display.")
    )
    style_sheet.add_paragraph_style("Endnotes-Ref-Notes", para)


def cite_source(bibliography, database, obj, elocale=glocale):
    """
    Cite any sources for the object and add them to the bibliography.

    :param bibliography: The bibliography to contain the citations.
    :type bibliography: :class:`.Bibliography`
    :param obj: An object with source references.
    :type obj: :class:`~.citationbase.CitationBase`
    :param elocale: allow deferred translation of dates and strings
    :type elocale: a :class:`.GrampsLocale` instance
    """

    trans_text = elocale.translation.gettext
    # trans_text is a defined keyword (see po/update_po.py, po/genpot.sh)

    txt = ""
    slist = obj.get_citation_list()
    if slist:
        first = True
        for ref in slist:
            if not first:
                # Translators: needed for Arabic, ignore otherwise
                txt += trans_text(", ")
            first = False
            citation = database.get_citation_from_handle(ref)
            (cindex, key) = bibliography.add_reference(citation)
            txt += "%d" % (cindex + 1)
            if key is not None:
                txt += key
    return txt


def write_endnotes(
    bibliography, database, doc, printnotes=False, links=False, elocale=glocale
):
    """
    Write all the entries in the bibliography as endnotes.

    If elocale is passed in (a :class:`.GrampsLocale`), then (insofar as
    possible) the translated values will be returned instead.

    :param bibliography: The bibliography that contains the citations.
    :type bibliography: :class:`.Bibliography`
    :param database: The database that the sources come from.
    :type database: DbBase
    :param doc: The document to write the endnotes into.
    :type doc: :class:`~.docgen.TextDoc`
    :param printnotes: Indicate if the notes attached to a source must be
            written too.
    :type printnotes: bool
    :param links: Indicate if URL links should be makde 'clickable'.
    :type links: bool
    :param elocale: allow deferred translation of dates and strings
    :type elocale: a :class:`.GrampsLocale` instance
    """
    if bibliography.get_citation_count() == 0:
        return

    trans_text = elocale.translation.gettext
    # trans_text is a defined keyword (see po/update_po.py, po/genpot.sh)

    doc.start_paragraph("Endnotes-Header")
    doc.write_text(trans_text("Endnotes"))
    doc.end_paragraph()

    cindex = 0
    cite = get_cite()
    for citation in cite.format(bibliography, database, elocale):
        cindex += 1

        doc.start_paragraph("Endnotes-Source", "%d." % cindex)
        source, text = citation[0]
        doc.write_text(text, links=links)
        doc.end_paragraph()

        if printnotes:
            _print_notes(source, database, doc, "Endnotes-Source-Notes", links)

        for ref, key, text in citation[1]:
            # Translators: needed for French, ignore otherwise
            doc.start_paragraph("Endnotes-Ref", trans_text("%s:") % key)
            doc.write_text(text, links=links)
            doc.end_paragraph()

            if printnotes:
                _print_notes(ref, database, doc, "Endnotes-Ref-Notes", links)


def _print_notes(obj, db, doc, style, links):
    note_list = obj.get_note_list()
    ind = 1
    for notehandle in note_list:
        note = db.get_note_from_handle(notehandle)
        contains_html = note.get_type() == NoteType.HTML_CODE
        doc.write_styled_note(
            note.get_styledtext(),
            note.get_format(),
            style,
            contains_html=contains_html,
            links=links,
        )
        ind += 1
