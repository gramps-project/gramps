#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025  Doug Blank
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
gramps.gui.widgets.markdown_render
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Runtime Markdown renderer for Gramps GTK widgets.

Renders the Gramps markdown dialect into a Gtk.TextBuffer, with support
for images, inline formatting, and gramps: URI scheme links.

Public API::

    render_md(text, buf, links, dbstate=None, uistate=None, vars=None)
    load_md(plugin_dir, basename)
    setup_tags(buf)
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import os
import re
from typing import Any

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import GdkPixbuf, Gtk, Pango

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.const import IMAGE_DIR
from gramps.gen.utils.markdown import parse_front_matter, parse_markdown

_INLINE_RE = re.compile(r"(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`)")


# -------------------------------------------------------------------------
#
# Image loading
#
# -------------------------------------------------------------------------


def _load_pixbuf(path: str, width: int | None = None) -> GdkPixbuf.Pixbuf | None:
    """
    Load and optionally scale a pixbuf.

    Handles URI schemes:
    - ``gramps:icon:name:size`` — GTK theme icon by name and size
    - ``gramps:image:filename`` — file relative to IMAGE_DIR
    - plain path — file relative to IMAGE_DIR
    """
    if path.startswith("gramps:icon:"):
        parts = path.split(":")
        name = parts[2]
        size = int(parts[3]) if len(parts) > 3 else 22
        try:
            pixbuf = Gtk.IconTheme.get_default().load_icon(name, size, 0)
        except Exception:
            return None
        if width is not None and pixbuf is not None and width != size:
            orig_h = pixbuf.get_height()
            orig_w = pixbuf.get_width()
            new_h = max(1, int(orig_h * width / orig_w)) if orig_w else size
            pixbuf = pixbuf.scale_simple(width, new_h, GdkPixbuf.InterpType.BILINEAR)
        return pixbuf
    if path.startswith("gramps:image:"):
        filepath = path[len("gramps:image:") :]
    else:
        filepath = path
    if not os.path.isabs(filepath):
        filepath = os.path.join(IMAGE_DIR, filepath)
    if not os.path.exists(filepath):
        return None
    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(filepath)
    except Exception:
        return None
    if width is not None and pixbuf.get_width() > 0:
        orig_w = pixbuf.get_width()
        orig_h = pixbuf.get_height()
        new_h = max(1, int(orig_h * width / orig_w))
        pixbuf = pixbuf.scale_simple(width, new_h, GdkPixbuf.InterpType.BILINEAR)
    return pixbuf


def _ins_image(
    buf: Gtk.TextBuffer, path: str, width: int | None = None, align: str = "left"
) -> None:
    """Insert a scaled pixbuf into buf at the current end position."""
    pixbuf = _load_pixbuf(path, width)
    if pixbuf is None:
        return
    start_offset = buf.get_char_count()
    buf.insert_pixbuf(buf.get_end_iter(), pixbuf)
    if align != "left":
        buf.apply_tag_by_name(
            "align_" + align,
            buf.get_iter_at_offset(start_offset),
            buf.get_end_iter(),
        )


# -------------------------------------------------------------------------
#
# Link insertion
#
# -------------------------------------------------------------------------


def _ins_link(
    buf: Gtk.TextBuffer,
    links: list,
    text: str,
    url: str,
    tag: str = "link",
) -> None:
    """Insert text as a clickable link, appending (start, end, url) to links."""
    start_offset = buf.get_char_count()
    buf.insert(buf.get_end_iter(), text)
    end_offset = buf.get_char_count()
    buf.apply_tag_by_name(
        tag,
        buf.get_iter_at_offset(start_offset),
        buf.get_iter_at_offset(end_offset),
    )
    links.append((start_offset, end_offset, url))


# -------------------------------------------------------------------------
#
# Inline formatting
#
# -------------------------------------------------------------------------


def _render_inline(buf: Gtk.TextBuffer, text: str) -> None:
    """Parse **bold**, *italic*, and `code` in text and insert into buf with tags."""
    pos = 0
    for m in _INLINE_RE.finditer(text):
        if m.start() > pos:
            buf.insert(buf.get_end_iter(), text[pos : m.start()])
        if m.group(2) is not None:
            inner, tag = m.group(2), "bold"
        elif m.group(3) is not None:
            inner, tag = m.group(3), "italic"
        else:
            inner, tag = m.group(4), "code"
        start_offset = buf.get_char_count()
        buf.insert(buf.get_end_iter(), inner)
        buf.apply_tag_by_name(
            tag,
            buf.get_iter_at_offset(start_offset),
            buf.get_end_iter(),
        )
        pos = m.end()
    if pos < len(text):
        buf.insert(buf.get_end_iter(), text[pos:])


# -------------------------------------------------------------------------
#
# URL helpers
#
# -------------------------------------------------------------------------


def wiki(page: str, manual: bool = False) -> str:
    """Build a URL to a Gramps wiki page."""
    from gramps.gen.const import URL_MANUAL_PAGE, URL_WIKISTRING
    from gramps.gui.display import EXTENSION

    url = URL_WIKISTRING
    if manual:
        url += URL_MANUAL_PAGE
    url += page + EXTENSION
    return url


def url_to_value(url: str, vars: dict | None = None) -> str:
    """
    Resolve a markdown URL spec to a string at runtime.

    Handles ``wiki:``, ``wiki_manual:``, ``{VARNAME}`` substitution,
    and literal URLs.
    """
    if url.startswith("wiki_manual:"):
        return wiki(url[len("wiki_manual:") :], manual=True)
    if url.startswith("wiki:"):
        page = url[len("wiki:") :]
        if page.startswith("{") and page.endswith("}"):
            page = (vars or {}).get(page[1:-1], page)
        return wiki(page)
    if "{" in url:
        parts = re.split(r"\{(\w+)\}", url)
        result = ""
        for idx, part in enumerate(parts):
            if idx % 2 == 0:
                result += part
            else:
                result += str((vars or {}).get(part, "{" + part + "}"))
        return result
    return url


# -------------------------------------------------------------------------
#
# Gramps: link dispatcher
#
# -------------------------------------------------------------------------


def handle_gramps_link(url: str, dbstate: Any, uistate: Any) -> None:
    """Dispatch a gramps: scheme URL to the appropriate Gramps action."""
    parts = url.split(":")
    if len(parts) < 3:
        return
    scheme = parts[1]

    if scheme == "view":
        _view_map = {
            "people": "People",
            "families": "Families",
            "events": "Events",
            "places": "Places",
            "sources": "Sources",
            "citations": "Citations",
            "repositories": "Repositories",
            "media": "Media",
            "notes": "Notes",
            "geography": "Geography",
            "charts": "Charts",
            "dashboard": "Dashboard",
        }
        view_name = _view_map.get(parts[2])
        if view_name:
            uistate.viewmanager.goto_page(view_name, None)
        return

    if scheme not in ("edit", "nav") or len(parts) < 4:
        return
    obj_type, gramps_id = parts[2], parts[3]
    db = dbstate.db
    _getters = {
        "Person": db.get_person_from_gramps_id,
        "Family": db.get_family_from_gramps_id,
        "Event": db.get_event_from_gramps_id,
        "Place": db.get_place_from_gramps_id,
        "Source": db.get_source_from_gramps_id,
        "Citation": db.get_citation_from_gramps_id,
        "Repository": db.get_repository_from_gramps_id,
        "Media": db.get_media_from_gramps_id,
        "Note": db.get_note_from_gramps_id,
    }
    getter = _getters.get(obj_type)
    if getter is None:
        return
    obj = getter(gramps_id)
    if obj is None:
        return

    if scheme == "nav":
        uistate.set_active(obj.get_handle(), obj_type)
        return

    from gramps.gui.editors import (
        EditCitation,
        EditEvent,
        EditFamily,
        EditMedia,
        EditNote,
        EditPerson,
        EditPlace,
        EditRepository,
        EditSource,
    )

    _editors = {
        "Person": EditPerson,
        "Family": EditFamily,
        "Event": EditEvent,
        "Place": EditPlace,
        "Source": EditSource,
        "Citation": EditCitation,
        "Repository": EditRepository,
        "Media": EditMedia,
        "Note": EditNote,
    }
    editor_class = _editors.get(obj_type)
    if editor_class:
        editor_class(dbstate, uistate, [], obj)


# -------------------------------------------------------------------------
#
# Tag setup
#
# -------------------------------------------------------------------------


def setup_tags(buf: Gtk.TextBuffer) -> None:
    """Create all standard text tags on buf (idempotent — skips existing tags)."""
    table = buf.get_tag_table()

    def _ensure(name: str, **kwargs: object) -> None:
        if table.lookup(name) is None:
            buf.create_tag(name, **kwargs)

    _ensure("bold", weight=Pango.Weight.BOLD)
    _ensure("italic", style=Pango.Style.ITALIC)
    _ensure(
        "code",
        family="Monospace",
        background="#f0f0f0",
    )
    _ensure("h1", weight=Pango.Weight.BOLD, scale=1.728)
    _ensure("h2", weight=Pango.Weight.BOLD, scale=1.440)
    _ensure("h3", weight=Pango.Weight.BOLD, scale=1.200)
    _ensure("h4", weight=Pango.Weight.BOLD)
    _ensure("h5", weight=Pango.Weight.BOLD)
    _ensure("h6", weight=Pango.Weight.BOLD)
    try:
        _lbl = Gtk.Label()
        _rgba = _lbl.get_style_context().get_color(Gtk.StateFlags.LINK)
        link_color = "#{:02x}{:02x}{:02x}".format(
            int(_rgba.red * 255),
            int(_rgba.green * 255),
            int(_rgba.blue * 255),
        )
    except Exception:
        link_color = "blue"
    _ensure("link", foreground=link_color, underline=Pango.Underline.SINGLE)
    _ensure("gramps_link", foreground="purple", underline=Pango.Underline.SINGLE)
    _ensure("align_center", justification=Gtk.Justification.CENTER)
    _ensure("align_right", justification=Gtk.Justification.RIGHT)


# -------------------------------------------------------------------------
#
# Locale-aware .md loader
#
# -------------------------------------------------------------------------


def load_md(plugin_dir: str, basename: str) -> str:
    """
    Load the best locale-matched .md file for basename.

    Search order::

        {basename}.{lang_full}.md  (e.g., welcomegramplet.fr_FR.md)
        {basename}.{lang}.md       (e.g., welcomegramplet.fr.md)
        {basename}.md              (English fallback)
    """
    lang = glocale.lang
    lang_full = lang.split(".")[0]
    lang_short = lang_full.split("_")[0]

    for name in [
        f"{basename}.{lang_full}.md",
        f"{basename}.{lang_short}.md",
        f"{basename}.md",
    ]:
        path = os.path.join(plugin_dir, name)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                return fh.read()

    raise FileNotFoundError(f"No .md file found for {basename!r} in {plugin_dir!r}")


# -------------------------------------------------------------------------
#
# Main renderer
#
# -------------------------------------------------------------------------


def render_md(
    text: str,
    buf: Gtk.TextBuffer,
    links: list,
    dbstate: Any = None,
    uistate: Any = None,
    vars: dict | None = None,
) -> None:
    """
    Parse and render a markdown string into buf.

    Tags must already exist on buf — call :func:`setup_tags` first.

    :param text: Markdown source.
    :param buf: Gtk.TextBuffer to render into (cleared before rendering).
    :param links: List to which ``(start_offset, end_offset, url)`` tuples
                  are appended for each link.
    :param dbstate: Gramps DbState — required for gramps:edit/nav links.
    :param uistate: Gramps UiState — required for gramps:edit/nav/view links.
    :param vars: Dict of variable name to value for ``{VARNAME}`` URL
                 substitution.
    """
    _config, body = parse_front_matter(text)
    all_vars = dict(vars or {})

    blocks = parse_markdown(body)
    buf.set_text("")

    for block in blocks:
        btype = block["type"]

        if btype == "heading":
            level = block.get("level", 2)
            tag = f"h{level}"
            icon = block.get("icon")
            if icon:
                _ins_image(buf, icon)
                buf.insert(buf.get_end_iter(), " ")
            start = buf.get_char_count()
            buf.insert(buf.get_end_iter(), block["text"])
            buf.apply_tag_by_name(
                tag, buf.get_iter_at_offset(start), buf.get_end_iter()
            )
            buf.insert(buf.get_end_iter(), "\n\n")

        elif btype == "paragraph":
            _render_inline(buf, block["text"])
            buf.insert(buf.get_end_iter(), "\n\n")

        elif btype == "block_image":
            _ins_image(buf, block["path"], width=block["width"], align=block["align"])
            buf.insert(buf.get_end_iter(), "\n\n")

        elif btype == "icon_para":
            _ins_image(buf, block["icon"])
            buf.insert(buf.get_end_iter(), " ")
            _render_inline(buf, block["text"])
            buf.insert(buf.get_end_iter(), "\n\n")

        elif btype == "link":
            resolved_url = url_to_value(block["url"], all_vars)
            is_gramps = block["url"].startswith("gramps:")
            link_tag = "gramps_link" if is_gramps else "link"
            buf.insert(buf.get_end_iter(), "  • ")
            _ins_link(buf, links, block["text"], resolved_url, link_tag)
            buf.insert(buf.get_end_iter(), "\n\n")
