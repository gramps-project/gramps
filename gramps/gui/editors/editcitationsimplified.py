#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009       Gary Burton
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2011,2014  Nick Hall
# Copyright (C) 2024       Doug Blank
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
EditCitationSimplified — simplified citation editor activated when
interface.use-simplified-interface is True.

Simplified view: normal fields + URL field + inline first-note editor (no tabs).
Full view (toggled): exactly the regular EditCitation layout with all four tabs.
"""

import logging

from gi.repository import Gtk, Gio

from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext

from gramps.gen.lib import Note, NoteType, StyledText, SrcAttribute, SrcAttributeType
from gramps.gen.db import DbTxn

from .editcitation import EditCitation
from .displaytabs import NoteTab, GalleryTab, SrcAttrEmbedList, CitationBackRefList
from ..widgets import StyledTextEditor

_LOG = logging.getLogger(".citation")

_URL_ATTR_TYPE = "URL"


class EditCitationSimplified(EditCitation):
    """
    Citation editor for simplified interface mode.

    Simplified view: normal fields + URL field + inline editor for the first note.
    No tabs are shown in simplified mode.

    Full view (toggled): identical to the regular EditCitation — all four tabs,
    no URL field, no inline note editor.
    """

    def _local_init(self):
        super()._local_init()
        # Use a separate config key so this dialog's saved size doesn't
        # inherit whatever large size the full citation dialog was left at.
        self.setup_configs("interface.citation-simplified", 600, 400)
        self._simplified = True
        self._notebook = None

        grid = self.glade.get_object("table67")

        # Insert URL row between Volume/Page (row 3) and Confidence (row 4).
        grid.insert_row(4)

        self._url_label = Gtk.Label(
            label=_("_Link/URL:"),
            use_underline=True,
            halign=Gtk.Align.END,
        )
        self._url_label.show()
        grid.attach(self._url_label, 0, 4, 1, 1)

        self._url_entry = Gtk.Entry()
        self._url_entry.set_hexpand(True)
        self._url_entry.set_tooltip_text(_("URL or web link for this citation"))
        self._url_entry.set_editable(not self.db.readonly)
        self._url_entry.show()
        grid.attach(self._url_entry, 1, 4, 1, 1)
        self._url_label.set_mnemonic_widget(self._url_entry)

        url_btn = Gtk.Button()
        img = Gtk.Image.new_from_icon_name("web-browser", Gtk.IconSize.BUTTON)
        url_btn.add(img)
        url_btn.set_relief(Gtk.ReliefStyle.NONE)
        url_btn.set_tooltip_text(_("Open URL in browser"))
        url_btn.connect("clicked", self._on_open_url)
        url_btn.show_all()
        grid.attach(url_btn, 2, 4, 1, 1)

        self._url_widgets = [self._url_label, self._url_entry, url_btn]

        # Toggle button on the left side of the action area.
        action_area = self.glade.get_object("dialog-action_area17")
        self._toggle_btn = Gtk.Button(label=_("Show all fields"))
        self._toggle_btn.set_tooltip_text(
            _("Switch between simplified and full editor view")
        )
        self._toggle_btn.connect("clicked", self._toggle_view)
        self._toggle_btn.show()
        action_area.pack_start(self._toggle_btn, False, False, 0)
        action_area.set_child_secondary(self._toggle_btn, True)

    def _setup_fields(self):
        super()._setup_fields()
        self._load_url()
        self._load_first_note()

    def _load_url(self):
        for attr in self.obj.get_attribute_list():
            if str(attr.get_type()) == _URL_ATTR_TYPE:
                self._url_entry.set_text(attr.get_value() or "")
                return
        self._url_entry.set_text("")

    def _load_first_note(self):
        note_list = self.obj.get_note_list()
        if note_list:
            note = self.db.get_note_from_handle(note_list[0])
            self._note_editor.set_text(note.get_styledtext())
        else:
            self._note_editor.set_text(StyledText())

    def _create_tabbed_pages(self):
        vbox = self.glade.get_object("vbox")

        # Inline note editor for simplified mode — packed first so it sits
        # above the notebook in the vbox.
        self._note_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self._note_box.set_border_width(12)

        note_label = Gtk.Label(label=_("Note:"), halign=Gtk.Align.START)
        note_label.show()
        self._note_box.pack_start(note_label, False, False, 0)

        self._note_editor = StyledTextEditor()
        self._note_editor.set_wrap_mode(Gtk.WrapMode.WORD)
        self._note_editor.set_editable(not self.db.readonly)

        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.IN)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw.add(self._note_editor)
        sw.show_all()
        self._note_box.pack_start(sw, True, True, 0)
        self._note_box.show_all()
        vbox.pack_start(self._note_box, True, True, 0)

        # Full notebook for full mode — packed after note_box, hidden initially.
        notebook = Gtk.Notebook()
        self._notebook = notebook

        self.note_tab = NoteTab(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_note_list(),
            "citation_editor_notes",
            self.get_menu_title(),
            notetype=NoteType.CITATION,
        )
        self._add_tab(notebook, self.note_tab)
        self.track_ref_for_deletion("note_tab")

        self.gallery_tab = GalleryTab(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_media_list(),
        )
        self._add_tab(notebook, self.gallery_tab)
        self.track_ref_for_deletion("gallery_tab")

        self.attr_tab = SrcAttrEmbedList(
            self.dbstate,
            self.uistate,
            self.track,
            self.obj.get_attribute_list(),
            "citation_editor_attributes",
        )
        self._add_tab(notebook, self.attr_tab)
        self.track_ref_for_deletion("attr_tab")

        self.citationref_list = CitationBackRefList(
            self.dbstate,
            self.uistate,
            self.track,
            self.db.find_backlink_handles(self.obj.handle),
            "citation_editor_references",
        )
        self._add_tab(notebook, self.citationref_list)
        self.track_ref_for_deletion("citationref_list")

        self._setup_notebook_tabs(notebook)
        notebook.show_all()
        vbox.pack_start(notebook, True, True, 0)

        # Keep hidden in simplified mode. set_no_show_all prevents ManagedWindow's
        # show_all() call from overriding our hidden state.
        notebook.set_no_show_all(True)
        notebook.hide()

    def _toggle_view(self, button):
        if self._simplified:
            # Simplified → Full: commit inline edits, rebuild tabs, swap widgets.
            self._save_first_note()
            self.note_tab.rebuild()
            self._sync_url_attribute()
            self.attr_tab.rebuild()
            for w in self._url_widgets:
                w.hide()
            self._note_box.hide()
            self._notebook.set_no_show_all(False)
            self._notebook.show_all()
            self._simplified = False
            button.set_label(_("Simplified view"))
        else:
            # Full → Simplified: reload first note, swap widgets.
            self._load_url()
            self._load_first_note()
            self._notebook.set_no_show_all(True)
            self._notebook.hide()
            self._note_box.show()
            for w in self._url_widgets:
                w.show()
            self._simplified = True
            button.set_label(_("Show all fields"))

    def _on_open_url(self, widget):
        url = self._url_entry.get_text().strip()
        if url:
            try:
                Gio.AppInfo.launch_default_for_uri(url, None)
            except Exception as err:
                _LOG.warning("Could not open URL %r: %s", url, err)

    def save(self, *obj):
        if self._simplified:
            self._save_first_note()
            self._sync_url_attribute()
        super().save(*obj)

    def _save_first_note(self):
        text = self._note_editor.get_text()
        note_list = self.obj.get_note_list()
        if note_list:
            note = self.db.get_note_from_handle(note_list[0])
            if str(text) != str(note.get_styledtext()):
                note.set_styledtext(text)
                with DbTxn(_("Edit Note"), self.db) as trans:
                    self.db.commit_note(note, trans)
        elif str(text):
            note = Note()
            note.set_type(NoteType.CITATION)
            note.set_styledtext(text)
            with DbTxn(_("Add Note"), self.db) as trans:
                self.db.add_note(note, trans)
            self.obj.get_note_list().insert(0, note.get_handle())

    def _sync_url_attribute(self):
        url = self._url_entry.get_text().strip()
        attr_list = self.obj.get_attribute_list()
        existing = None
        for attr in attr_list:
            if str(attr.get_type()) == _URL_ATTR_TYPE:
                existing = attr
                break
        if url:
            if existing:
                existing.set_value(url)
            else:
                attr = SrcAttribute()
                attr.set_type(SrcAttributeType(_URL_ATTR_TYPE))
                attr.set_value(url)
                attr_list.append(attr)
        elif existing:
            attr_list.remove(existing)
