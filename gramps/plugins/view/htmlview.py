#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  The Gramps Project
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
HTML view for capturing debug input and rendering simple HTML.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations

import html
import logging
from html.parser import HTMLParser

LOG = logging.getLogger(".htmlview")

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
try:
    from gi.repository import Gtk
    from gi.repository import Gdk
except ImportError:
    pass

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
try:
    from gramps.gui.views.pageview import PageView

    _HAS_GUI = True
except ImportError:

    class PageView:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            pass

    _HAS_GUI = False

from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# ------------------------------------------------------------
#
# HTMLToPangoParser
#
# ------------------------------------------------------------
class HTMLToPangoParser(HTMLParser):
    """
    A lightweight HTML parser that converts basic HTML markup to Pango markup.
    """

    def __init__(self) -> None:
        """
        Initialise the parser.
        """
        super().__init__()
        self.result: list[str] = []
        self.ignore_content = False
        self.ignore_tags = {"script", "style", "head", "title"}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """
        Handle start tags.
        """
        if tag in self.ignore_tags:
            self.ignore_content = True
            return
        if self.ignore_content:
            return

        if tag in ("b", "strong"):
            self.result.append("<b>")
        elif tag in ("i", "em"):
            self.result.append("<i>")
        elif tag == "u":
            self.result.append("<u>")
        elif tag == "s":
            self.result.append("<s>")
        elif tag == "sub":
            self.result.append("<sub>")
        elif tag == "sup":
            self.result.append("<sup>")
        elif tag in ("h1", "h2", "h3"):
            self.result.append("\n\n<big><b>")
        elif tag in ("h4", "h5", "h6"):
            self.result.append("\n\n<b>")
        elif tag in ("p", "div"):
            self.result.append("\n\n")
        elif tag == "br":
            self.result.append("\n")
        elif tag == "a":
            href = ""
            for name, val in attrs:
                if name == "href" and val:
                    href = html.escape(val)
                    break
            if href:
                self.result.append(f'<a href="{href}">')
            else:
                self.result.append("<a>")

    def handle_endtag(self, tag: str) -> None:
        """
        Handle end tags.
        """
        if tag in self.ignore_tags:
            self.ignore_content = False
            return
        if self.ignore_content:
            return

        if tag in ("b", "strong"):
            self.result.append("</b>")
        elif tag in ("i", "em"):
            self.result.append("</i>")
        elif tag == "u":
            self.result.append("</u>")
        elif tag == "s":
            self.result.append("</s>")
        elif tag == "sub":
            self.result.append("</sub>")
        elif tag == "sup":
            self.result.append("</sup>")
        elif tag in ("h1", "h2", "h3"):
            self.result.append("</b></big>\n")
        elif tag in ("h4", "h5", "h6"):
            self.result.append("</b>\n")
        elif tag in ("p", "div"):
            self.result.append("\n")
        elif tag == "a":
            self.result.append("</a>")

    def handle_data(self, data: str) -> None:
        """
        Handle textual data.
        """
        if self.ignore_content:
            return
        self.result.append(html.escape(data))

    def get_pango_markup(self) -> str:
        """
        Get the resulting Pango markup.

        :returns: Pango XML markup text.
        :rtype: str
        """
        text = "".join(self.result).strip()
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        return text


# ------------------------------------------------------------
#
# HTMLView
#
# ------------------------------------------------------------
class HTMLView(PageView):
    """
    HTMLView interface for developer/debug usage.
    """

    _instance: HTMLView | None = None

    def __init__(self, pdata, dbstate, uistate):
        """
        Create an HTMLView with the current dbstate and uistate.
        """
        PageView.__init__(self, _("HTML"), pdata, dbstate, uistate)
        self.ui_def = []  # No special menu for HTML, simple popup if needed
        HTMLView._instance = self

        self.text_view = None
        self.text_buffer = None
        self.render_label = None

    @classmethod
    def set_html_text(cls, text: str) -> None:
        """
        Set the HTML text of the active HTMLView instance.

        :param text: The HTML content to display.
        :type text: str
        """
        if cls._instance is not None:
            cls._instance.set_text(text)

    @classmethod
    def append_html_text(cls, text: str) -> None:
        """
        Append text to the active HTMLView instance.

        :param text: The HTML content to append.
        :type text: str
        """
        if cls._instance is not None:
            cls._instance.append_text(text)

    def build_interface(self):
        """
        Builds the container widget for the interface.
        Returns a gtk container widget.
        """
        top = self.build_widget()
        top.show_all()
        return top

    def build_widget(self) -> Gtk.Box:
        """
        Builds the container widget for the interface.
        Returns a gtk container widget.

        :returns: The built container widget.
        :rtype: Gtk.Box
        """
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        # Toolbar / Control box at the top
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        toolbar.set_border_width(6)

        clear_btn = Gtk.Button(label=_("Clear"))
        clear_btn.connect("clicked", self.cb_clear_text)
        toolbar.pack_start(clear_btn, False, False, 0)

        paste_btn = Gtk.Button(label=_("Paste from Clipboard"))
        paste_btn.connect("clicked", self.cb_paste_text)
        toolbar.pack_start(paste_btn, False, False, 0)

        info_label = Gtk.Label(
            label=_("Capturing debug input for WebSearch and Grizard functionality")
        )
        info_label.set_alignment(1.0, 0.5)
        toolbar.pack_end(info_label, True, True, 0)

        box.pack_start(toolbar, False, False, 0)

        # Notebook for Render and Source tabs
        notebook = Gtk.Notebook()
        notebook.connect("switch-page", self.cb_switch_tab)

        # Tab 1: Render View
        render_scroll = Gtk.ScrolledWindow()
        render_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        render_scroll.set_shadow_type(Gtk.ShadowType.IN)

        self.render_label = Gtk.Label()
        self.render_label.set_alignment(0.0, 0.0)
        self.render_label.set_xalign(0.0)
        self.render_label.set_yalign(0.0)
        self.render_label.set_line_wrap(True)
        self.render_label.set_selectable(True)
        self.render_label.set_use_markup(True)
        self.render_label.set_margin_top(12)
        self.render_label.set_margin_bottom(12)
        self.render_label.set_margin_left(12)
        self.render_label.set_margin_right(12)

        render_scroll.add(self.render_label)
        notebook.append_page(render_scroll, Gtk.Label(label=_("Render")))

        # Tab 2: Source View
        source_scroll = Gtk.ScrolledWindow()
        source_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        source_scroll.set_shadow_type(Gtk.ShadowType.IN)

        self.text_view = Gtk.TextView()
        self.text_view.set_monospace(True)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.text_buffer = self.text_view.get_buffer()

        source_scroll.add(self.text_view)
        notebook.append_page(source_scroll, Gtk.Label(label=_("Source")))

        box.pack_start(notebook, True, True, 0)

        self.widget = box
        return self.widget

    def set_text(self, text: str) -> None:
        """
        Set the text in the text view buffer and update the rendered view.

        :param text: The text to set.
        :type text: str
        """
        if self.text_buffer is not None:
            self.text_buffer.set_text(text)
        self._update_rendered_html()

    def append_text(self, text: str) -> None:
        """
        Append the text to the text view buffer and update the rendered view.

        :param text: The text to append.
        :type text: str
        """
        if self.text_buffer is not None:
            end_iter = self.text_buffer.get_end_iter()
            self.text_buffer.insert(end_iter, text)
        self._update_rendered_html()

    def _update_rendered_html(self) -> None:
        """
        Parse raw HTML from the text buffer and update the Pango-formatted label.
        """
        if self.text_buffer is None or self.render_label is None:
            return

        start_iter, end_iter = self.text_buffer.get_bounds()
        raw_html = self.text_buffer.get_text(start_iter, end_iter, True)

        if not raw_html.strip():
            self.render_label.set_markup("")
            return

        parser = HTMLToPangoParser()
        try:
            parser.feed(raw_html)
            pango_markup = parser.get_pango_markup()
            self.render_label.set_markup(pango_markup)
        except Exception as err:
            LOG.warning("Failed parsing HTML to Pango: %s", err)
            self.render_label.set_text(raw_html)

    def cb_clear_text(self, widget: Gtk.Button) -> None:
        """
        Callback for clear button clicked.

        :param widget: The button widget.
        :type widget: Gtk.Button
        """
        if self.text_buffer is not None:
            self.text_buffer.set_text("")
        if self.render_label is not None:
            self.render_label.set_markup("")

    def cb_paste_text(self, widget: Gtk.Button) -> None:
        """
        Callback for paste button clicked.

        :param widget: The button widget.
        :type widget: Gtk.Button
        """
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        text = clipboard.wait_for_text()
        if text:
            self.set_text(text)

    def cb_switch_tab(
        self, notebook: Gtk.Notebook, page: Gtk.Widget, page_num: int
    ) -> None:
        """
        Callback for when notebook tabs are switched.

        :param notebook: The notebook widget.
        :type notebook: Gtk.Notebook
        :param page: The page widget being switched to.
        :type page: Gtk.Widget
        :param page_num: The index of the page being switched to.
        :type page_num: int
        """
        if page_num == 0:  # Render tab
            self._update_rendered_html()

    def build_tree(self) -> None:
        """
        Rebuilds the current display.
        """
        pass

    def get_title(self) -> str:
        """
        Used to set the titlebar in the configuration window.

        :returns: The title of the view.
        :rtype: str
        """
        return _("HTML")

    def get_stock(self) -> str:
        """
        Return image associated with the view, which is used for the
        icon for the button.

        :returns: Stock icon name.
        :rtype: str
        """
        return "gramps-view"

    def get_viewtype_stock(self) -> str:
        """
        Type of view in category.

        :returns: Stock icon name.
        :rtype: str
        """
        return "gramps-view"

    def define_actions(self) -> None:
        """
        Defines the UIManager actions.
        """
        pass
