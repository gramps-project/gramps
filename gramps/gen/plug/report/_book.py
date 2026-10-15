#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011-2016  Paul Franklin
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

# Written by Alex Roitman,
# largely based on the BaseDoc classes by Don Allingham

"""the non-UI-specific (i.e. common, shared) classes for books"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import copy
import os

# ------------------------------------------------------------------------
#
# Set up logging
#
# ------------------------------------------------------------------------
import logging

LOG = logging.getLogger(".Book")

# -------------------------------------------------------------------------
#
# SAX interface
#
# -------------------------------------------------------------------------
from xml.sax import make_parser, handler, SAXParseException
from xml.sax.saxutils import escape

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ...const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from ...const import USER_DATA
from ...utils.cast import get_type_converter_by_name, type_name
from ..docgen import StyleSheet, StyleSheetList, GraphicsStyle
from .. import BasePluginManager
from . import book_categories

# ------------------------------------------------------------------------
#
# Private Constants
#
# ------------------------------------------------------------------------
_UNSUPPORTED = _("Unsupported")


# ------------------------------------------------------------------------
#
# Book Item class
#
# ------------------------------------------------------------------------
class BookItem:
    """
    Interface into the book item -- a smallest element of the book.
    """

    def __init__(self, dbase, name):
        """
        Create a new empty BookItem.
        TODO: it should be possible to make a non-empty BookItem, a copy

        name:   the book item is retrieved
                from the book item registry using name for lookup
        """
        self.dbase = dbase
        self.style_name = "default"
        pmgr = BasePluginManager.get_instance()

        for pdata in pmgr.get_reg_bookitems():
            if pdata.id == name:
                self.translated_name = pdata.name
                if not pdata.supported:
                    self.category = _UNSUPPORTED
                else:
                    self.category = book_categories[pdata.category]
                mod = pmgr.load_plugin(pdata)
                self.write_item = getattr(mod, pdata.reportclass)
                self.name = pdata.id
                oclass = getattr(mod, pdata.optionclass)
                self.option_class = oclass(self.name, self.dbase)
                self.option_class.load_previous_values()

    def get_name(self):
        """
        Return the name of the item.
        """
        return self.name

    def get_translated_name(self):
        """
        Return the translated name of the item.
        """
        return self.translated_name

    def get_category(self):
        """
        Return the category of the item.
        """
        return self.category

    def get_write_item(self):
        """
        Return the report-writing function of the item.
        """
        return self.write_item

    def set_style_name(self, style_name):
        """
        Set the style name for the item.

        style_name: name of the style to set.
        """
        self.style_name = style_name

    def get_style_name(self):
        """
        Return the style name of the item.
        """
        return self.style_name


# ------------------------------------------------------------------------
#
# Book class
#
# ------------------------------------------------------------------------
class Book:
    """
    Interface into the user-defined Book -- a collection of book items.
    """

    def __init__(self, obj=None, exact_copy=True):
        """
        Create a new empty Book.

        @param obj:         if not None, creates the Book from obj, from the
                            items in obj, instead of creating an empty Book.
        @type obj:          a :class:`.Book` instance
        @param exact_copy:  if True (and obj is not None) the exact same
                            BookItem objects will be in the new Book;
                            if False (and obj is not None) the same number
                            and same type of BookItem objects will be created
        @type exact_copy:   boolean
        """

        self.name = ""  # this is tested for, in several places
        self.dbname = ""
        self.paper_name = None
        self.paper_orientation = None
        self.paper_metric = None
        self.paper_custom_size = None
        self.paper_margins = None
        self.paper_format = None
        self.paper_output = None
        self.item_list = []
        if obj:
            if exact_copy:
                self.item_list = obj.item_list
            else:
                for item in obj.get_item_list():
                    new_item = BookItem(item.dbase, item.get_name())
                    orig_opt_dict = item.option_class.handler.options_dict
                    new_opt_dict = new_item.option_class.handler.options_dict
                    menu = new_item.option_class.menu
                    for optname in orig_opt_dict:
                        new_opt_dict[optname] = orig_opt_dict[optname]
                        menu_option = menu.get_option_by_name(optname)
                        if menu_option:
                            menu_option.set_value(new_opt_dict[optname])
                    new_item.set_style_name(item.get_style_name())
                    self.item_list.append(new_item)

    def set_name(self, name):
        """
        Set the name of the book.

        name:   the name to set.
        """
        self.name = name

    def get_name(self):
        """
        Return the name of the book.
        """
        return self.name

    def get_dbname(self):
        """
        Return the name of the database file used for the book.
        """
        return self.dbname

    def set_dbname(self, name):
        """
        Set the name of the database file used for the book.

        name:   a filename to set.
        """
        self.dbname = name

    def clear(self):
        """
        Clears the contents of the book.
        """
        self.item_list = []

    def append_item(self, item):
        """
        Add an item to the book.

        item:   an item to append.
        """
        self.item_list.append(item)

    def insert_item(self, index, item):
        """
        Inserts an item into the given position in the book.

        index:  a position index.
        item:   an item to append.
        """
        self.item_list.insert(index, item)

    def pop_item(self, index):
        """
        Pop an item from given position in the book.

        index:  a position index.
        """
        return self.item_list.pop(index)

    def get_item(self, index):
        """
        Return an item at a given position in the book.

        index:  a position index.
        """
        return self.item_list[index]

    def set_item(self, index, item):
        """
        Set an item at a given position in the book.

        index:  a position index.
        item:   an item to set.
        """
        self.item_list[index] = item

    def get_item_list(self):
        """
        Return list of items in the current book.
        """
        return self.item_list

    def set_paper_name(self, paper_name):
        """
        Set the paper name for the Book.
        @param paper_name: name of the paper to set.
        @type paper_name: str
        """
        self.paper_name = paper_name

    def get_paper_name(self):
        """
        Return the paper name of the Book.
        @returns: returns the paper name
        @rtype: str
        """
        return self.paper_name

    def set_orientation(self, orientation):
        """
        Set the paper orientation for the Book.
        @param orientation: orientation to set. Possible values are
            PAPER_LANDSCAPE or PAPER_PORTRAIT
        @type orientation: int
        """
        self.paper_orientation = orientation

    def get_orientation(self):
        """
        Return the paper orientation for the Book.
        @returns: returns the selected orientation. Valid values are
            PAPER_LANDSCAPE or PAPER_PORTRAIT
        @rtype: int
        """
        return self.paper_orientation

    def set_paper_metric(self, paper_metric):
        """
        Set the paper metric for the Book.
        @param paper_metric: whether to use metric.
        @type paper_metric: boolean
        """
        self.paper_metric = paper_metric

    def get_paper_metric(self):
        """
        Return the paper metric of the Book.
        @returns: returns whether to use metric
        @rtype: boolean
        """
        return self.paper_metric

    def set_custom_paper_size(self, paper_size):
        """
        Set the custom paper size for the Book.
        @param paper_size: paper size to set in cm.
        @type paper_size: [float, float]
        """
        self.paper_custom_size = paper_size

    def get_custom_paper_size(self):
        """
        Return the custom paper size for the Book.
        @returns: returns the custom paper size in cm
        @rtype: [float, float]
        """
        return self.paper_custom_size

    def set_margins(self, margins):
        """
        Set the paper margins for the Book.
        @param margins: margins to set. Possible values are floats in cm
        @type margins: [float, float, float, float]
        """
        self.paper_margins = copy.copy(margins)

    def get_margins(self):
        """
        Return the paper margins for the Book.
        @returns margins: returns the margins, floats in cm
        @rtype margins: [float, float, float, float]
        """
        return copy.copy(self.paper_margins)

    def set_margin(self, pos, value):
        """
        Set a paper margin for the Book.
        @param pos: Position of margin [left, right, top, bottom]
        @param value: floating point in cm
        @type pos: int
        @type value: float
        """
        self.paper_margins[pos] = value

    def get_margin(self, pos):
        """
        Return a paper margin for the Book.
        @param pos: Position of margin [left, right, top, bottom]
        @type pos: int
        @returns: float cm of margin
        @rtype: float
        """
        return self.paper_margins[pos]

    def set_format_name(self, format_name):
        """
        Set the format name for the Book.
        @param format_name: name of the format to set.
        @type format_name: str
        """
        self.paper_format = format_name

    def get_format_name(self):
        """
        Return the format name of the Book.
        @returns: returns the format name
        @rtype: str
        """
        return self.paper_format

    def set_output(self, output):
        """
        Set the output for the Book.
        @param output: name of the output to set.
        @type output: str
        """
        self.paper_output = output

    def get_output(self):
        """
        Return the output of the Book.
        @returns: returns the output name
        @rtype: str
        """
        return self.paper_output


# ------------------------------------------------------------------------
#
# BookList class
#
# ------------------------------------------------------------------------
class BookList:
    """
    Interface into the user-defined list of books.

    BookList is loaded from a specified XML file if it exists.
    """

    def __init__(self, filename, dbase):
        """
        Create a new BookList from the books that may be defined in the
        specified file.

        file:   XML file that contains book items definitions
        """
        self.dbase = dbase
        self.bookmap = {}
        self._needs_saving = None
        self.file = os.path.join(USER_DATA, filename)
        self.parse()

    def delete_book(self, name):
        """
        Remove a book from the list. Since each book must have a
        unique name, the name is used to delete the book.

        name:   name of the book to delete
        """
        del self.bookmap[name]

    ## 2/2016 the string "get_book_map" appears nowhere else in gramps
    ##    def get_book_map(self):
    ##        """
    ##        Return the map of names to books.
    ##        """
    ##        return self.bookmap
    ##
    def get_book(self, name):
        """
        Return the Book associated with the name

        name:   name associated with the desired Book.
        """
        return self.bookmap[name]

    def get_book_names(self):
        "Return a list of all the book names in the BookList, sorted"
        return sorted(self.bookmap.keys())

    def set_book(self, name, book):
        """
        Add or replaces a Book in the BookList.

        name:   name associated with the Book to add or replace.
        book:   definition of the book -- a :class:`.Book` instance
        """
        self.bookmap[name] = book

    def set_needs_saving(self, needs_saving):
        """
        Set the needs_saving flag for the BookList.

        @param needs_saving: whether the current BookList needs saving
        @type needs_saving: boolean
        """
        self._needs_saving = needs_saving

    def get_needs_saving(self):
        """
        Return the needs_saving flag of the BookList.

        @returns: returns whether the current BookList needs saving to a file
        @rtype: boolean
        """
        return self._needs_saving

    def save(self):
        """
        Saves the current BookList to the associated file.
        """
        with open(self.file, "w", encoding="utf-8") as b_f:
            b_f.write('<?xml version="1.0" encoding="utf-8"?>\n')
            b_f.write("<booklist>\n")
            for name in sorted(self.bookmap):  # enable a diff of archived copies
                book = self.get_book(name)
                dbname = escape(book.get_dbname())
                b_f.write(
                    '  <book name="%s" database="%s">' "\n" % (escape(name), dbname)
                )
                for item in book.get_item_list():
                    b_f.write(
                        '    <item name="%s" '
                        'trans_name="%s">\n'
                        % (item.get_name(), item.get_translated_name())
                    )
                    options = item.option_class.handler.options_dict
                    for option_name in sorted(options.keys()):  # enable a diff
                        option_value = options[option_name]
                        if isinstance(option_value, (list, tuple)):
                            b_f.write(
                                '      <option name="%s" value="" '
                                'length="%d">\n'
                                % (escape(option_name), len(options[option_name]))
                            )
                            for list_index, v in enumerate(option_value):
                                option_type = type_name(v)
                                value = escape(str(v))
                                value = value.replace('"', "&quot;")
                                b_f.write(
                                    '        <listitem number="%d" '
                                    'type="%s" value="%s"/>\n'
                                    % (list_index, option_type, value)
                                )
                            b_f.write("      </option>\n")
                        else:
                            option_type = type_name(option_value)
                            value = escape(str(option_value))
                            value = value.replace('"', "&quot;")
                            b_f.write(
                                '      <option name="%s" type="%s" '
                                'value="%s"/>\n'
                                % (escape(option_name), option_type, value)
                            )

                    b_f.write('      <style name="%s"/>' "\n" % item.get_style_name())
                    b_f.write("    </item>\n")
                if book.get_paper_name():
                    b_f.write('    <paper name="%s"/>' "\n" % book.get_paper_name())
                if book.get_orientation() is not None:  # 0 is legal
                    b_f.write(
                        '    <orientation value="%s"/>' "\n" % book.get_orientation()
                    )
                if book.get_paper_metric() is not None:  # 0 is legal
                    b_p_metric = book.get_paper_metric()
                    if isinstance(b_p_metric, bool):
                        b_p_metric = int(b_p_metric)
                    b_f.write('    <metric value="%s"/>' "\n" % b_p_metric)
                if book.get_custom_paper_size():
                    size = book.get_custom_paper_size()
                    b_f.write('    <size value="%f %f"/>' "\n" % (size[0], size[1]))
                if book.get_margins():
                    for pos, margin in enumerate(book.get_margins()):
                        b_f.write(
                            '    <margin number="%s" '
                            'value="%f"/>\n' % (pos, book.get_margin(pos))
                        )
                if book.get_format_name():
                    b_f.write('    <format name="%s"/>' "\n" % book.get_format_name())
                if book.get_output():
                    b_f.write(
                        '    <output name="%s"/>' "\n" % escape(book.get_output())
                    )
                b_f.write("  </book>\n")

            b_f.write("</booklist>\n")

    def parse(self):
        """
        Loads the BookList from the associated file, if it exists.
        """
        try:
            parser = make_parser()
            parser.setContentHandler(BookParser(self, self.dbase))
            # bug 10387; XML should be utf8, but was not previously saved
            # that way.  So try to read utf8, if fails, try with system
            # encoding.  Only an issue on non-utf8 systems.
            try:
                with open(self.file, encoding="utf-8") as the_file:
                    parser.parse(the_file)
            except UnicodeDecodeError:
                with open(self.file) as the_file:
                    parser.parse(the_file)
        except (
            IOError,
            OSError,
            ValueError,
            SAXParseException,
            KeyError,
            AttributeError,
        ):
            LOG.debug("Failed to parse book list", exc_info=True)


# -------------------------------------------------------------------------
#
# BookParser
#
# -------------------------------------------------------------------------
class BookParser(handler.ContentHandler):
    """
    SAX parsing class for the Books XML file.
    """

    def __init__(self, booklist, dbase):
        """
        Create a BookParser class that populates the passed booklist.

        booklist:   BookList to be loaded from the file.
        """
        handler.ContentHandler.__init__(self)
        self.dbase = dbase
        self.booklist = booklist
        self.book = None
        self.item = None
        self.option = None
        self.an_opt_name = None
        self.an_opt_value = None
        self.style = None
        self.bname = None
        self.iname = None
        self.dbname = None
        self.b_p_name = None
        self.b_p_orient = None
        self.b_p_metric = None
        self.b_p_size = None
        self.b_p_margins = None
        self.b_p_format = None
        self.b_p_output = None

    def startElement(self, tag, attrs):
        """
        Overridden class that handles the start of a XML element
        """
        if tag == "book":
            self.book = Book()
            self.bname = attrs["name"]
            self.book.set_name(self.bname)
            self.dbname = attrs["database"]
            self.book.set_dbname(self.dbname)
            self.b_p_name = None
            self.b_p_orient = None
            self.b_p_metric = None
            self.b_p_size = None
            self.b_p_margins = None
            self.b_p_format = None
            self.b_p_output = None
        elif tag == "item":
            self.item = BookItem(self.dbase, attrs["name"])
            self.option = {}
        elif tag == "option":
            self.an_opt_name = attrs["name"]
            if "length" in attrs:
                self.an_opt_value = []
            else:
                converter = get_type_converter_by_name(attrs["type"])
                self.an_opt_value = converter(attrs["value"])
        elif tag == "listitem":
            converter = get_type_converter_by_name(attrs["type"])
            self.an_opt_value.append(converter(attrs["value"]))
        elif tag == "style":
            self.style = attrs["name"]
        elif tag == "paper":
            self.b_p_name = attrs["name"]
        elif tag == "orientation":
            self.b_p_orient = int(attrs["value"])
        elif tag == "metric":
            self.b_p_metric = int(attrs["value"])
        elif tag == "size":
            width, height = attrs["value"].split()
            self.b_p_size = [float(width), float(height)]
        elif tag == "margin":
            if self.b_p_margins is None:
                self.b_p_margins = [0.0, 0.0, 0.0, 0.0]
            self.b_p_margins[int(attrs["number"])] = float(attrs["value"])
        elif tag == "format":
            self.b_p_format = attrs["name"]
        elif tag == "output":
            self.b_p_output = attrs["name"]
        else:
            pass

    def endElement(self, tag):
        """
        Overridden class that handles the end of a XML element
        """
        if tag == "option":
            self.option[self.an_opt_name] = self.an_opt_value
        elif tag == "item":
            self.item.option_class.handler.options_dict.update(self.option)
            self.item.set_style_name(self.style)
            self.book.append_item(self.item)
        elif tag == "book":
            if self.b_p_name:
                self.book.set_paper_name(self.b_p_name)
            if self.b_p_orient is not None:  # 0 is legal
                self.book.set_orientation(self.b_p_orient)
            if self.b_p_metric is not None:  # 0 is legal
                self.book.set_paper_metric(self.b_p_metric)
            if self.b_p_size:
                self.book.set_custom_paper_size(self.b_p_size)
            if self.b_p_margins:
                self.book.set_margins(self.b_p_margins)
            if self.b_p_format:
                self.book.set_format_name(self.b_p_format)
            if self.b_p_output:
                self.book.set_output(self.b_p_output)
            self.booklist.set_book(self.bname, self.book)


# -------------------------------------------------------------------------
#
# Functions
#
# -------------------------------------------------------------------------
def get_item_style_sheet(item):
    """
    Return the (own, un-namespaced) :class:`.StyleSheet` a book item selected.
    """
    ihandler = item.option_class.handler

    # Set up default style
    ihandler.set_default_stylesheet_name(item.get_style_name())
    default_style = StyleSheet()
    make_default_style = item.option_class.make_default_style
    make_default_style(default_style)

    # Read all style sheets available for this item
    style_file = ihandler.get_stylesheet_savefile()
    style_list = StyleSheetList(style_file, default_style)

    # Get the selected stylesheet
    style_name = ihandler.get_default_stylesheet_name()
    return style_list.get_style_sheet(style_name)


def _add_namespaced_styles(selected_style, style_sheet, prefix):
    """
    Copy every style in ``style_sheet`` into ``selected_style``, each stored
    under ``prefix`` + its original name.

    A draw (graphics) style embeds the *name* of the paragraph style it renders
    text with (``GraphicsStyle.get_paragraph_style()``); the document backend
    resolves that name against the same shared stylesheet (e.g.
    ``svgdrawdoc``/``libcairodoc``: ``get_draw_style(...).get_paragraph_style()``
    then ``get_paragraph_style(name)``). So the embedded reference must be
    namespaced too, or the draw style would resolve its paragraph by the bare
    (colliding) name. With ``prefix == ""`` this is the historical behaviour.
    """
    for name in style_sheet.get_paragraph_style_names():
        selected_style.add_paragraph_style(
            prefix + name, style_sheet.get_paragraph_style(name)
        )

    for name in style_sheet.get_draw_style_names():
        draw_style = GraphicsStyle(style_sheet.get_draw_style(name))
        para_name = draw_style.get_paragraph_style()
        if para_name:
            draw_style.set_paragraph_style(prefix + para_name)
        selected_style.add_draw_style(prefix + name, draw_style)

    for name in style_sheet.get_table_style_names():
        selected_style.add_table_style(prefix + name, style_sheet.get_table_style(name))

    for name in style_sheet.get_cell_style_names():
        selected_style.add_cell_style(prefix + name, style_sheet.get_cell_style(name))


def append_styles(selected_style, item, prefix=""):
    """
    Append the styles for a book item to the book's shared stylesheet.

    Each style is stored under ``prefix`` + its name. A book renders several
    items into one shared document carrying a single shared stylesheet (a hard
    requirement of backends such as ODF, which emit the whole stylesheet once at
    ``open()``). Two items of the same report type define styles under identical
    names (e.g. two Descendant Reports both define "DR-Title"). Without a
    per-item ``prefix`` the second item's style overwrites the first's in the
    flat shared sheet, so both items resolve that name to the last-written values
    (issue 6128). Namespacing by ``prefix`` keeps every item's styles distinct;
    :class:`BookItemStyleProxy` rewrites each item's report's style references to
    the matching prefixed name.

    Returns the item's own (un-namespaced) :class:`.StyleSheet`, so the caller
    can build the item's :class:`BookItemStyleProxy`.
    """
    style_sheet = get_item_style_sheet(item)
    _add_namespaced_styles(selected_style, style_sheet, prefix)
    return style_sheet


def book_item_style_prefix(item_number):
    """
    A per-item style-name namespace, unique across the items of one book.

    ``item_number`` is the item's position in the book's item list. The prefix
    uses the same character set (upper-case letters, digits, hyphen) as the
    report-defined style names it is prepended to, so it survives every document
    backend's style-name handling exactly as the existing distinct style names
    from different report types already do.
    """
    return "BI%03d-" % item_number


class BookItemStyleProxy:
    """
    A thin wrapper around the book's shared document that namespaces a single
    book item's style-name references (issue 6128).

    :func:`append_styles` stores each book item's styles under a per-item
    ``prefix`` in the shared stylesheet so same-named styles from different items
    do not collide. A report's style-name references are baked into the report
    code (e.g. ``self.doc.start_paragraph("DR-Title")``); routing the item's
    report through this proxy rewrites every such reference to the matching
    prefixed name, so the shared document resolves it to that item's own values.

    The proxy overrides every style-name-bearing method of the abstract
    ``TextDoc`` and ``DrawDoc`` interfaces (the only document API a report uses
    to reference styles by name): ``start_paragraph``, ``start_table``,
    ``start_cell``, ``write_styled_note``, ``add_media`` (text) and
    ``draw_path``, ``draw_box``, ``draw_text``, ``center_text``, ``rotate_text``,
    ``draw_line`` (draw). It also keeps the item's stylesheet view in step:
    ``get_style_sheet`` returns the item's own un-prefixed sheet, and
    ``set_style_sheet`` (used by reports that compute styles at run time, e.g.
    AncestorTree/DescendTree/FanChart) re-namespaces the item's changes back into
    the shared document instead of replacing it wholesale. Every other
    attribute/method is delegated unchanged to the shared document.
    """

    def __init__(self, doc, item_style_sheet, prefix):
        self._doc = doc
        self._item_style_sheet = item_style_sheet
        self._prefix = prefix

    # -- the item's stylesheet view (read/modify/write at run time) -----------
    def get_style_sheet(self):
        return StyleSheet(self._item_style_sheet)

    def set_style_sheet(self, style_sheet):
        # Keep the item's own view, and mirror the change into the shared
        # document under this item's prefix (never replace the shared sheet,
        # which holds every other item's namespaced styles).
        self._item_style_sheet = StyleSheet(style_sheet)
        shared = self._doc.get_style_sheet()
        _add_namespaced_styles(shared, style_sheet, self._prefix)
        self._doc.set_style_sheet(shared)

    # -- TextDoc methods that take a style name -------------------------------
    def start_paragraph(self, style_name, leader=None):
        self._doc.start_paragraph(self._prefix + style_name, leader)

    def start_table(self, name, style_name):
        self._doc.start_table(name, self._prefix + style_name)

    def start_cell(self, style_name, span=1):
        self._doc.start_cell(self._prefix + style_name, span)

    def write_styled_note(
        self, styledtext, format, style_name, contains_html=False, links=False
    ):
        self._doc.write_styled_note(
            styledtext, format, self._prefix + style_name, contains_html, links
        )

    def add_media(self, name, align, w_cm, h_cm, alt="", style_name=None, crop=None):
        if style_name is not None:
            style_name = self._prefix + style_name
        self._doc.add_media(name, align, w_cm, h_cm, alt, style_name, crop)

    # -- DrawDoc methods that take a (graphics) style name --------------------
    def draw_path(self, style, path):
        self._doc.draw_path(self._prefix + style, path)

    def draw_box(self, style, text, x, y, w, h, mark=None):
        self._doc.draw_box(self._prefix + style, text, x, y, w, h, mark)

    def draw_text(self, style, text, x1, y1, mark=None):
        self._doc.draw_text(self._prefix + style, text, x1, y1, mark)

    def center_text(self, style, text, x1, y1, mark=None):
        self._doc.center_text(self._prefix + style, text, x1, y1, mark)

    def rotate_text(self, style, text, x, y, angle, mark=None):
        self._doc.rotate_text(self._prefix + style, text, x, y, angle, mark)

    def draw_line(self, style, x1, y1, x2, y2):
        self._doc.draw_line(self._prefix + style, x1, y1, x2, y2)

    # -- everything else is the shared document -------------------------------
    def __getattr__(self, name):
        return getattr(self._doc, name)


def add_book_item_styles(selected_style, item, doc, item_number):
    """
    Collate one book item's styles into the book's shared ``selected_style`` and
    route the item's report through a style-namespacing document proxy, so a book
    with several same-type items renders each with its OWN style values (the
    issue-6128 invariant).

    Must be called BEFORE the item's report object is created: the report grabs
    its document from ``item.option_class.get_document()`` at construction
    (``_reportbase.ReportBase.__init__``), so the proxy is installed via
    ``set_document`` here. Returns the proxy.
    """
    prefix = book_item_style_prefix(item_number)
    item_style_sheet = append_styles(selected_style, item, prefix)
    proxy = BookItemStyleProxy(doc, item_style_sheet, prefix)
    item.option_class.set_document(proxy)
    return proxy
