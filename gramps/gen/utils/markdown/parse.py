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
gramps.gen.utils.markdown.parse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Pure-Python tokenizer for the Gramps markdown dialect.

No GTK, no Gramps GUI dependencies.
"""

import re

# -------------------------------------------------------------------------
#
# Regexes
#
# -------------------------------------------------------------------------

_LINK_RE = re.compile(r"^-\s+(~?)\[([^\]]*)\]\(([^)]*)\)\s*$")
_HEAD_RE = re.compile(r"^(#{1,6})\s+(.*)")
_BLOCK_IMG_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]*)\)\s*$")
_ICON_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]*)\)\s+(.+)")


def _strip_quotes(s: str) -> str:
    """Remove surrounding single or double quotes."""
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1]
    return s


def parse_front_matter(text: str) -> tuple[dict, str]:
    """
    Parse YAML-like front matter delimited by --- lines.

    :returns: ``(config, body)`` where config is a dict of key/value pairs
              and body is the remaining markdown text.
    """
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    yaml_src = text[4:end]
    body = text[end + 5 :]

    config: dict = {}
    lines = yaml_src.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^(\w+):\s*(.*)", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val:
            config[key] = _strip_quotes(val)
            i += 1
        else:
            items: list = []
            kv: dict = {}
            i += 1
            while i < len(lines) and lines[i] and lines[i][0] in " \t":
                sub = lines[i].strip()
                if sub.startswith("- "):
                    items.append(sub[2:].strip())
                elif ":" in sub:
                    k, _, v = sub.partition(":")
                    kv[k.strip()] = _strip_quotes(v.strip())
                i += 1
            config[key] = kv if kv else items
    return config, body


def parse_img_src(src: str) -> tuple[str, int | None, str]:
    """
    Parse image src into ``(path, width, align)``.

    Handles::

        gramps:icon:name:size      -> (src, None, "left")
        gramps:image:file|w|a     -> ("gramps:image:file", w, a)
        plain/path|w|a             -> ("plain/path", w, a)
    """
    if src.startswith("gramps:icon:"):
        return src, None, "left"
    parts = src.split("|")
    path = parts[0]
    width = int(parts[1]) if len(parts) > 1 and parts[1] else None
    align = parts[2] if len(parts) > 2 and parts[2] else "left"
    return path, width, align


def parse_markdown(text: str) -> list[dict]:
    """
    Parse a markdown body into a list of block tokens.

    Token shapes::

        {'type': 'heading',     'level': int, 'text': str, 'icon': str|None}
        {'type': 'paragraph',   'text': str}
        {'type': 'block_image', 'path': str, 'width': int|None, 'align': str}
        {'type': 'icon_para',   'icon': str, 'text': str}
        {'type': 'link',        'text': str, 'url': str, 'translate': bool}
    """
    blocks: list[dict] = []
    para_lines: list[str] = []

    def flush_para() -> None:
        if para_lines:
            blocks.append({"type": "paragraph", "text": " ".join(para_lines)})
            para_lines.clear()

    for line in text.splitlines():
        stripped = line.strip()

        if not stripped:
            flush_para()
            continue

        m_head = _HEAD_RE.match(stripped)
        if m_head:
            flush_para()
            level = len(m_head.group(1))
            head_text = m_head.group(2).strip()
            icon = None
            m_icon = _ICON_RE.match(head_text)
            if m_icon:
                icon = m_icon.group(2).strip()
                head_text = m_icon.group(3).strip()
            blocks.append(
                {"type": "heading", "level": level, "text": head_text, "icon": icon}
            )
            continue

        m_link = _LINK_RE.match(stripped)
        if m_link:
            flush_para()
            blocks.append(
                {
                    "type": "link",
                    "text": m_link.group(2),
                    "url": m_link.group(3),
                    "translate": m_link.group(1) != "~",
                }
            )
            continue

        m_bimg = _BLOCK_IMG_RE.match(stripped)
        if m_bimg:
            flush_para()
            path, width, align = parse_img_src(m_bimg.group(2).strip())
            blocks.append(
                {
                    "type": "block_image",
                    "path": path,
                    "width": width,
                    "align": align,
                }
            )
            continue

        m_icon = _ICON_RE.match(stripped)
        if m_icon:
            flush_para()
            blocks.append(
                {
                    "type": "icon_para",
                    "icon": m_icon.group(2).strip(),
                    "text": m_icon.group(3).strip(),
                }
            )
            continue

        para_lines.append(stripped)

    flush_para()
    return blocks
