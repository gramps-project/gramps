#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007       Brian G. Matherly
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

"Generate files/Marker Report"

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from PluginUtils import register_report
from ReportBase import Report, ReportUtils, ReportOptions, \
     CATEGORY_TEXT, MODE_GUI, MODE_BKI, MODE_CLI
import BaseDoc
import Sort
from RelLib import MarkerType
from Filters import GenericFilter, Rules
from BasicUtils import name_displayer

#------------------------------------------------------------------------
#
# GTK/GNOME modules
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# MarkerReport
#
#------------------------------------------------------------------------
class MarkerReport(Report):

    def __init__(self,database,person,options_class):
        """
        Creates the MarkerReport object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        marker       - The marker each object must match to be included.

        """

        Report.__init__(self,database,person,options_class)

        self.marker = options_class.handler.options_dict['marker']
        self.filter = GenericFilter()
        self.filter.add_rule(Rules.Person.HasMarkerOf([self.marker]))
        
    def write_report(self):
        self.doc.start_paragraph("MR-Title")
        title = _("Marker Report for %s Items") % self.marker
        mark = BaseDoc.IndexMark(title,BaseDoc.INDEX_TYPE_TOC,1)
        self.doc.write_text(title,mark)
        self.doc.end_paragraph()
        
        plist = self.database.get_person_handles(sort_handles=False)
        ind_list = self.filter.apply(self.database,plist)
            
        count = 1
        for person_handle in ind_list:
            person = self.database.get_person_from_handle(person_handle)
            name = name_displayer.display(person)
            mark = ReportUtils.get_person_mark(self.database, person)
            self.doc.start_paragraph('MR-Normal',str(count))
            self.doc.write_text(name,mark)
            self.doc.end_paragraph()
            count = count + 1

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class MarkerOptions(ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.__init__(self,name,person_id)

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'marker'       :  "",
        }
        self.options_help = {
            'marker'        : ("=str","Marker",
                            "The marker each item must match to be included",
                            True),
        }
        
    def add_user_options(self,dialog):
        """
        Override the base class add_user_options task to add generations option
        """
        self.marker_menu = gtk.combo_box_new_text()
        index = 0
        marker_index = 0
        markers = dialog.db.get_marker_types()
        markers.append(MarkerType().get_map()[MarkerType.COMPLETE])
        markers.append(MarkerType().get_map()[MarkerType.TODO_TYPE])
        for marker in markers:
            self.marker_menu.append_text(marker)
            if self.options_dict['marker'] == marker:
                marker_index = index
            index += 1
        self.marker_menu.set_active(marker_index)
        dialog.add_option('Marker',self.marker_menu)

    def parse_user_options(self,dialog):
        """
        Parses the custom options that we have added. Set the value in the
        options dictionary.
        """
        self.options_dict['marker'] = self.marker_menu.get_active_text()

    def make_default_style(self,default_style):
        """Make the default output style for the Marker Report."""
        f = BaseDoc.FontStyle()
        f.set_size(12)
        f.set_type_face(BaseDoc.FONT_SANS_SERIF)
        f.set_bold(1)
        p = BaseDoc.ParagraphStyle()
        p.set_header_level(1)
        p.set_bottom_border(1)
        p.set_top_margin(ReportUtils.pt2cm(3))
        p.set_bottom_margin(ReportUtils.pt2cm(3))
        p.set_font(f)
        p.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        p.set_description(_("The style used for the title of the page."))
        default_style.add_paragraph_style("MR-Title",p)
        
        font = BaseDoc.FontStyle()
        font.set_size(12)
        p = BaseDoc.ParagraphStyle()
        p.set(first_indent=-0.75,lmargin=.75)
        p.set_font(font)
        p.set_top_margin(ReportUtils.pt2cm(3))
        p.set_bottom_margin(ReportUtils.pt2cm(3))
        p.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style("MR-Normal",p)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_report(
    name = 'marker_report',
    category = CATEGORY_TEXT,
    report_class = MarkerReport,
    options_class = MarkerOptions,
    modes = MODE_GUI | MODE_BKI | MODE_CLI,
    translated_name = _("Marker Report"),
    status=(_("Stable")),
    description=_("Generates a list of people with a specified marker"),
    author_name="Brian G. Matherly",
    author_email="pez4brian@gramps-project.org"
    )
