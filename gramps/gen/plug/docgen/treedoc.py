#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2017-2018 Nick Hall
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
""" LaTeX Genealogy Tree adapter for Trees """
#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
import os
import shutil
import re
from subprocess import Popen, PIPE
from io import StringIO
import tempfile
import logging

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ...utils.file import search_for
from ...lib import Person, EventType, EventRoleType, Date
from ...display.place import displayer as _pd
from ...utils.file import media_path_full
from . import BaseDoc, PAPER_PORTRAIT
from ..menu import NumberOption, TextOption, EnumeratedListOption
from ...constfunc import win
from ...config import config
from ...const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# set up logging
#
#-------------------------------------------------------------------------
LOG = logging.getLogger(".treedoc")

#-------------------------------------------------------------------------
#
# Private Constants
#
#-------------------------------------------------------------------------
_DETAIL = [{'name': _("Full"), 'value': "full"},
           {'name': _("Medium"), 'value': "medium"},
           {'name': _("Short"), 'value': "short"}]

_MARRIAGE = [{'name': _("Default"), 'value': ""},
             {'name': _("Above"), 'value': "marriage above"},
             {'name': _("Below"), 'value': "marriage below"},
             {'name': _("Not shown"), 'value': "no marriage"}]

_COLOR = [{'name': _("None"), 'value': "none"},
          {'name': _("Default"), 'value': "default"},
          {'name': _("Preferences"), 'value': "preferences"}]

_TIMEFLOW = [{'name': _("Down (↓)"), 'value': ""},
             {'name': _("Up (↑)"), 'value': "up"},
             {'name': _("Right (→)"), 'value': "right"},
             {'name': _("Left (←)"), 'value': "left"}]

_EDGES = [{'name': _("Perpendicular"), 'value': ""},
          {'name': _("Rounded"), 'value': "rounded", },
          {'name': _("Swing"), 'value': "swing", },
          {'name': _("Mesh"), 'value': 'mesh'}]

_NOTELOC = [{'name': _("Top"), 'value': "t"},
            {'name': _("Bottom"), 'value': "b"}]

_NOTESIZE = [{'name': _("Tiny"), 'value': "tiny"},
             {'name': _("Script"), 'value': "scriptsize"},
             {'name': _("Footnote"), 'value': "footnotesize"},
             {'name': _("Small"), 'value': "small"},
             {'name': _("Normal"), 'value': "normalsize"},
             {'name': _("Large"), 'value': "large"},
             {'name': _("Very large"), 'value': "Large"},
             {'name': _("Extra large"), 'value': "LARGE"},
             {'name': _("Huge"), 'value': "huge"},
             {'name': _("Extra huge"), 'value': "Huge"}]

if win():
    _LATEX_FOUND = search_for("lualatex.exe")
    DETACHED_PROCESS = 8
else:
    _LATEX_FOUND = search_for("lualatex")

def escape(text):
    lookup = {
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
        '~': '\\~{}',
        '^': '\\^{}',
        '\\': '\\textbackslash{}'
        }
    pattern = re.compile('|'.join([re.escape(key) for key in lookup.keys()]))
    return pattern.sub(lambda match: lookup[match.group(0)], text)

#------------------------------------------------------------------------------
#
# TreeOptions
#
#------------------------------------------------------------------------------
class TreeOptions:
    """
    Defines all of the controls necessary
    to configure the genealogy tree reports.
    """
    def add_menu_options(self, menu):
        """
        Add all graph related options to the menu.

        :param menu: The menu the options should be added to.
        :type menu: :class:`.Menu`
        :return: nothing
        """
        ################################
        category = _("Node Options")
        ################################

        detail = EnumeratedListOption(_("Node detail"), "full")
        for item in _DETAIL:
            detail.add_item(item["value"], item["name"])
        detail.set_help(_("Detail of information to be shown in a node."))
        menu.add_option(category, "detail", detail)

        marriage = EnumeratedListOption(_("Marriage"), "")
        for item in _MARRIAGE:
            marriage.add_item(item["value"], item["name"])
        marriage.set_help(_("Position of marriage information."))
        menu.add_option(category, "marriage", marriage)

        nodesize = NumberOption(_("Node size"), 25, 5, 100, 5)
        nodesize.set_help(_("One dimension of a node, in mm. If the timeflow "
                            "is up or down then this is the width, otherwise "
                            "it is the height."))
        menu.add_option(category, "nodesize", nodesize)

        levelsize = NumberOption(_("Level size"), 35, 5, 100, 5)
        levelsize.set_help(_("One dimension of a node, in mm. If the timeflow "
                             "is up or down then this is the height, otherwise "
                             "it is the width."))
        menu.add_option(category, "levelsize", levelsize)

        nodecolor = EnumeratedListOption(_("Color"), "none")
        for item in _COLOR:
            nodecolor.add_item(item["value"], item["name"])
        nodecolor.set_help(_("Node color."))
        menu.add_option(category, "nodecolor", nodecolor)

        ################################
        category = _("Tree Options")
        ################################

        timeflow = EnumeratedListOption(_("Timeflow"), "")
        for item in _TIMEFLOW:
            timeflow.add_item(item["value"], item["name"])
        timeflow.set_help(_("Direction that the graph will grow over time."))
        menu.add_option(category, "timeflow", timeflow)

        edges = EnumeratedListOption(_("Edge style"), "")
        for item in _EDGES:
            edges.add_item(item["value"], item["name"])
        edges.set_help(_("Style of the edges between nodes."))
        menu.add_option(category, "edges", edges)

        leveldist = NumberOption(_("Level distance"), 5, 1, 20, 1)
        leveldist.set_help(_("The minimum amount of free space, in mm, "
                             "between levels.  For vertical graphs, this "
                             "corresponds to spacing between rows.  For "
                             "horizontal graphs, this corresponds to spacing "
                             "between columns."))
        menu.add_option(category, "leveldist", leveldist)

        ################################
        category = _("Note")
        ################################

        note = TextOption(_("Note to add to the tree"), [""])
        note.set_help(_("This text will be added to the tree."))
        menu.add_option(category, "note", note)

        noteloc = EnumeratedListOption(_("Note location"), 't')
        for item in _NOTELOC:
            noteloc.add_item(item["value"], item["name"])
        noteloc.set_help(_("Whether note will appear on top "
                           "or bottom of the page."))
        menu.add_option(category, "noteloc", noteloc)

        notesize = EnumeratedListOption(_("Note size"), 'normalsize')
        for item in _NOTESIZE:
            notesize.add_item(item["value"], item["name"])
        notesize.set_help(_("The size of note text."))
        menu.add_option(category, "notesize", notesize)


#------------------------------------------------------------------------------
#
# TreeDoc
#
#------------------------------------------------------------------------------
class TreeDoc(metaclass=ABCMeta):
    """
    Abstract Interface for genealogy tree document generators. Output formats
    for genealogy tree reports must implement this interface to be used by the
    report system.
    """
    @abstractmethod
    def start_tree(self, option_list):
        """
        Write the start of a tree.
        """

    @abstractmethod
    def end_tree(self):
        """
        Write the end of a tree.
        """

    @abstractmethod
    def start_subgraph(self, level, subgraph_type, family, option_list=None):
        """
        Write the start of a subgraph.
        """

    @abstractmethod
    def end_subgraph(self, level):
        """
        Write the end of a subgraph.
        """

    @abstractmethod
    def write_node(self, db, level, node_type, person, marriage_flag,
                   option_list=None):
        """
        Write the contents of a node.
        """


#------------------------------------------------------------------------------
#
# TreeDocBase
#
#------------------------------------------------------------------------------
class TreeDocBase(BaseDoc, TreeDoc):
    """
    Base document generator for all Graphviz document generators. Classes that
    inherit from this class will only need to implement the close function.
    The close function will generate the actual file of the appropriate type.
    """
    def __init__(self, options, paper_style):
        BaseDoc.__init__(self, None, paper_style)

        self._filename = None
        self._tex = StringIO()
        self._paper = paper_style

        get_option = options.menu.get_option_by_name

        self.detail = get_option('detail').get_value()
        self.marriage = get_option('marriage').get_value()
        self.nodesize = get_option('nodesize').get_value()
        self.levelsize = get_option('levelsize').get_value()
        self.nodecolor = get_option('nodecolor').get_value()

        self.timeflow = get_option('timeflow').get_value()
        self.edges = get_option('edges').get_value()
        self.leveldist = get_option('leveldist').get_value()

        self.note = get_option('note').get_value()
        self.noteloc = get_option('noteloc').get_value()
        self.notesize = get_option('notesize').get_value()

    def write_start(self):
        """
        Write the start of the document.
        """
        paper_size = self._paper.get_size()
        name = paper_size.get_name().lower()
        if name == 'custom size':
            width = str(paper_size.get_width())
            height = str(paper_size.get_height())
            paper = 'papersize={%scm,%scm}' % (width, height)
        elif name in ('a', 'b', 'c', 'd', 'e'):
            paper = 'ansi' + name + 'paper'
        else:
            paper = name + 'paper'

        if self._paper.get_orientation() == PAPER_PORTRAIT:
            orientation = 'portrait'
        else:
            orientation = 'landscape'

        lmargin = self._paper.get_left_margin()
        rmargin = self._paper.get_right_margin()
        tmargin = self._paper.get_top_margin()
        bmargin = self._paper.get_bottom_margin()
        if lmargin == rmargin == tmargin == bmargin:
            margin = 'margin=%scm'% lmargin
        else:
            if lmargin == rmargin:
                margin = 'hmargin=%scm' % lmargin
            else:
                margin = 'hmargin={%scm,%scm}' % (lmargin, rmargin)
            if tmargin == bmargin:
                margin += ',vmargin=%scm' % tmargin
            else:
                margin += ',vmargin={%scm,%scm}' % (tmargin, bmargin)

        self.write(0, '\\documentclass[%s]{article}\n' % orientation)

        self.write(0, '\\IfFileExists{libertine.sty}{\n')
        self.write(0, '    \\usepackage{libertine}\n')
        self.write(0, '}{}\n')

        self.write(0, '\\usepackage[%s,%s]{geometry}\n' % (paper, margin))
        self.write(0, '\\usepackage[all]{genealogytree}\n')
        self.write(0, '\\usepackage{color}\n')
        self.write(0, '\\begin{document}\n')

        if self.nodecolor == 'preferences':
            scheme = config.get('colors.scheme')
            male_bg = config.get('colors.male-dead')[scheme][1:]
            female_bg = config.get('colors.female-dead')[scheme][1:]
            neuter_bg = config.get('colors.unknown-dead')[scheme][1:]
            self.write(0, '\\definecolor{male-bg}{HTML}{%s}\n' % male_bg)
            self.write(0, '\\definecolor{female-bg}{HTML}{%s}\n' % female_bg)
            self.write(0, '\\definecolor{neuter-bg}{HTML}{%s}\n' % neuter_bg)

        if ''.join(self.note) != '' and self.noteloc == 't':
            for line in self.note:
                self.write(0, '{\\%s %s}\\par\n' % (self.notesize, line))
            self.write(0, '\\bigskip\n')

        self.write(0, '\\begin{tikzpicture}\n')

    def start_tree(self, option_list):
        self.write(0, '\\genealogytree[\n')
        self.write(0, 'processing=database,\n')
        if self.marriage:
            info = self.detail + ' ' + self.marriage
        else:
            info = self.detail
        self.write(0, 'database format=%s,\n' % info)
        if self.timeflow:
            self.write(0, 'timeflow=%s,\n' % self.timeflow)
        if self.edges:
            self.write(0, 'edges=%s,\n' % self.edges)
        if self.leveldist != 5:
            self.write(0, 'level distance=%smm,\n' % self.leveldist)
        if self.nodesize != 25:
            self.write(0, 'node size=%smm,\n' % self.nodesize)
        if self.levelsize != 35:
            self.write(0, 'level size=%smm,\n' % self.levelsize)
        if self.nodecolor == 'none':
            self.write(0, 'tcbset={male/.style={},\n')
            self.write(0, '        female/.style={},\n')
            self.write(0, '        neuter/.style={}},\n')
        if self.nodecolor == 'preferences':
            self.write(0, 'tcbset={male/.style={colback=male-bg},\n')
            self.write(0, '        female/.style={colback=female-bg},\n')
            self.write(0, '        neuter/.style={colback=neuter-bg}},\n')

        for option in option_list:
            self.write(0, '%s,\n' % option)

        self.write(0, ']{\n')

    def end_tree(self):
        self.write(0, '}\n')

    def write_end(self):
        """
        Write the end of the document.
        """
        self.write(0, '\\end{tikzpicture}\n')

        if ''.join(self.note) != '' and self.noteloc == 'b':
            self.write(0, '\\bigskip\n')
            for line in self.note:
                self.write(0, '\\par{\\%s %s}\n' % (self.notesize, line))

        self.write(0, '\\end{document}\n')

    def start_subgraph(self, level, subgraph_type, family, option_list=None):
        options = ['id=%s' % family.gramps_id]
        if option_list:
            options.extend(option_list)
        self.write(level, '%s[%s]{\n' % (subgraph_type, ','.join(options)))

    def end_subgraph(self, level):
        self.write(level, '}\n')

    def write_node(self, db, level, node_type, person, marriage_flag,
                   option_list=None):
        options = ['id=%s' % person.gramps_id]
        if option_list:
            options.extend(option_list)
        self.write(level, '%s[%s]{\n' % (node_type, ','.join(options)))
        if person.gender == Person.MALE:
            self.write(level+1, 'male,\n')
        elif person.gender == Person.FEMALE:
            self.write(level+1, 'female,\n')
        elif person.gender == Person.UNKNOWN:
            self.write(level+1, 'neuter,\n')
        name = person.get_primary_name()
        nick = name.get_nick_name()
        surn = name.get_surname()
        name_parts = [self.format_given_names(name),
                      '\\nick{{{}}}'.format(escape(nick)) if nick else '',
                      '\\surn{{{}}}'.format(escape(surn)) if surn else '']
        self.write(level+1, 'name = {{{}}},\n'.format(
            ' '.join([e for e in name_parts if e])))
        for eventref in person.get_event_ref_list():
            if eventref.role == EventRoleType.PRIMARY:
                event = db.get_event_from_handle(eventref.ref)
                self.write_event(db, level+1, event)
        if marriage_flag:
            for handle in person.get_family_handle_list():
                family = db.get_family_from_handle(handle)
                for eventref in family.get_event_ref_list():
                    if eventref.role == EventRoleType.FAMILY:
                        event = db.get_event_from_handle(eventref.ref)
                        self.write_event(db, level+1, event)
        for attr in person.get_attribute_list():
            # Comparison with 'Occupation' for backwards compatibility with Gramps 5.0
            attr_type = str(attr.get_type())
            if attr_type in ('Occupation', _('Occupation')):
                self.write(level+1, 'profession = {%s},\n' %
                           escape(attr.get_value()))
            if attr_type == 'Comment':
                self.write(level+1, 'comment = {%s},\n' %
                           escape(attr.get_value()))
        for mediaref in person.get_media_list():
            media = db.get_media_from_handle(mediaref.ref)
            path = media_path_full(db, media.get_path())
            if os.path.isfile(path):
                if win():
                    path = path.replace('\\', '/')
                self.write(level+1, 'image = {{%s}%s},\n' %
                           os.path.splitext(path))
                break # first image only
        self.write(level, '}\n')

    def write_event(self, db, level, event):
        """
        Write an event.
        """
        modifier = None
        if event.type == EventType.BIRTH:
            event_type = 'birth'
            if 'died' in event.description.lower():
                modifier = 'died'
            if 'stillborn' in event.description.lower():
                modifier = 'stillborn'
            # modifier = 'out of wedlock'
        elif event.type == EventType.BAPTISM:
            event_type = 'baptism'
        elif event.type == EventType.ENGAGEMENT:
            event_type = 'engagement'
        elif event.type == EventType.MARRIAGE:
            event_type = 'marriage'
        elif event.type == EventType.DIVORCE:
            event_type = 'divorce'
        elif event.type == EventType.DEATH:
            event_type = 'death'
        elif event.type == EventType.BURIAL:
            event_type = 'burial'
            if 'killed' in event.description.lower():
                modifier = 'killed'
        elif event.type == EventType.CREMATION:
            event_type = 'burial'
            modifier = 'cremated'
        else:
            return

        date = event.get_date_object()

        if date.get_calendar() == Date.CAL_GREGORIAN:
            calendar = 'AD' # GR
        elif date.get_calendar() == Date.CAL_JULIAN:
            calendar = 'JU'
        else:
            calendar = ''

        if date.get_modifier() == Date.MOD_ABOUT:
            calendar = 'ca' + calendar

        date_str = self.format_iso(date.get_ymd(), calendar)
        if date.get_modifier() == Date.MOD_BEFORE:
            date_str = '/' + date_str
        elif date.get_modifier() == Date.MOD_AFTER:
            date_str = date_str + '/'
        elif date.is_compound():
            stop_date = self.format_iso(date.get_stop_ymd(), calendar)
            date_str = date_str + '/' + stop_date

        place = escape(_pd.display_event(db, event))
        place = place.replace("-", "\--")

        if modifier:
            event_type += '+'
            self.write(level, '%s = {%s}{%s}{%s},\n' %
                       (event_type, date_str, place, modifier))
        elif place == '':
            event_type += '-'
            self.write(level, '%s = {%s},\n' % (event_type, date_str))
        else:
            self.write(level, '%s = {%s}{%s},\n' %
                       (event_type, date_str, place))

    def format_given_names(self, name):
        """
        Format given names.
        """
        first = name.get_first_name()
        call = name.get_call_name()
        if call:
            if call in first:
                where = first.index(call)
                return '{before}\\pref{{{call}}}{after}'.format(
                    before=escape(first[:where]),
                    call=escape(call),
                    after=escape(first[where+len(call):]))
            else:
                # ignore erroneous call name
                return escape(first)
        else:
            return escape(first)

    def format_iso(self, date_tuple, calendar):
        """
        Format an iso date.
        """
        year, month, day = date_tuple
        if year == 0:
            iso_date = ''
        elif month == 0:
            iso_date = str(year)
        elif day == 0:
            iso_date = '%s-%s' % (year, month)
        else:
            iso_date = '%s-%s-%s' % (year, month, day)
        if calendar and calendar != 'AD':
            iso_date = '(%s)%s' % (calendar, iso_date)
        return iso_date

    def write(self, level, text):
        """
        Write indented text.
        """
        self._tex.write('  '*level + text)

    def open(self, filename):
        """ Implement TreeDocBase.open() """
        self._filename = os.path.normpath(os.path.abspath(filename))
        self.write_start()

    def close(self):
        """
        This isn't useful by itself. Other classes need to override this and
        actually generate a file.
        """
        self.write_end()


#------------------------------------------------------------------------------
#
# TreeGraphDoc
#
#------------------------------------------------------------------------------
class TreeGraphDoc(TreeDocBase):
    """
    TreeGraphDoc implementation that generates a .graph file.
    """

    def write_start(self):
        """
        Write the start of the document - nothing for a graph file.
        """
        pass

    def start_tree(self, option_list):
        """
        Write the start of a tree - nothing for a graph file.
        """
        pass

    def end_tree(self):
        """
        Write the end of a tree - nothing for a graph file.
        """
        pass

    def write_end(self):
        """
        Write the end of the document - nothing for a graph file.
        """
        pass

    def close(self):
        """ Implements TreeDocBase.close() """
        TreeDocBase.close(self)

        with open(self._filename, 'w', encoding='utf-8') as texfile:
            texfile.write(self._tex.getvalue())

#------------------------------------------------------------------------------
#
# TreeTexDoc
#
#------------------------------------------------------------------------------
class TreeTexDoc(TreeDocBase):
    """
    TreeTexDoc implementation that generates a .tex file.
    """

    def close(self):
        """ Implements TreeDocBase.close() """
        TreeDocBase.close(self)

        # Make sure the extension is correct
        if self._filename[-4:] != ".tex":
            self._filename += ".tex"

        with open(self._filename, 'w', encoding='utf-8') as texfile:
            texfile.write(self._tex.getvalue())


#------------------------------------------------------------------------------
#
# TreePdfDoc
#
#------------------------------------------------------------------------------
class TreePdfDoc(TreeDocBase):
    """
    TreePdfDoc implementation that generates a .pdf file.
    """

    def close(self):
        """ Implements TreeDocBase.close() """
        TreeDocBase.close(self)

        # Make sure the extension is correct
        if self._filename[-4:] != ".pdf":
            self._filename += ".pdf"

        with tempfile.TemporaryDirectory() as tmpdir:
            basename = os.path.basename(self._filename)
            args = ['lualatex', '-output-directory', tmpdir,
                    '-jobname', basename[:-4]]
            if win():
                proc = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                             creationflags=DETACHED_PROCESS)
            else:
                proc = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            proc.communicate(input=self._tex.getvalue().encode('utf-8'))
            shutil.copy(os.path.join(tmpdir, basename), self._filename)


#------------------------------------------------------------------------------
#
# Various Genealogy Tree formats.
#
#------------------------------------------------------------------------------
FORMATS = []

if _LATEX_FOUND:
    FORMATS += [{'type' : "pdf",
                 'ext'  : "pdf",
                 'descr': _("PDF"),
                 'mime' : "application/pdf",
                 'class': TreePdfDoc}]

FORMATS += [{'type' : "graph",
             'ext'  : "graph",
             'descr': _("Graph File for genealogytree"),
             'class': TreeGraphDoc}]

FORMATS += [{'type' : "tex",
             'ext'  : "tex",
             'descr': _("LaTeX File"),
             'mime' : "application/x-latex",
             'class': TreeTexDoc}]
