#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Jakim Friant
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

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import GObject

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.plug.docgen import PaperStyle, PAPER_PORTRAIT, PAPER_LANDSCAPE
from gramps.gen.plug.report._paper import paper_sizes
from ...glade import Glade

#-------------------------------------------------------------------------
#
# PaperComboBox
#
#-------------------------------------------------------------------------
class PaperComboBox(Gtk.ComboBox):

    def __init__(self,default_name):
        Gtk.ComboBox.__init__(self)
        self.set_wrap_width(4)

        self.store = Gtk.ListStore(GObject.TYPE_STRING)
        self.set_model(self.store)
        cell = Gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)
        self.mapping = {}

        index = 0
        start_index = 0
        for key in paper_sizes:
            key_name = key.get_name()
            if default_name == key_name or default_name == key.trans_pname:
                start_index = index
            self.mapping[key_name] = key # always use the English paper name
            if key.trans_pname:
                key_name = key.trans_pname # display the translated paper name
            self.store.append(row=[key_name])
            index += 1

        self.set_active(start_index)

    def get_value(self):
        active = self.get_active()
        if active < 0:
            return None
        key = str(self.store[active][0])
        for paper in paper_sizes:
            if key == paper.trans_pname:
                key = paper.get_name()
        return (self.mapping[key],key)

#-------------------------------------------------------------------------
#
# OrientationComboBox
#
#-------------------------------------------------------------------------
class OrientationComboBox(Gtk.ComboBox):

    def __init__(self,default=PAPER_PORTRAIT):
        Gtk.ComboBox.__init__(self)

        self.store = Gtk.ListStore(GObject.TYPE_STRING)
        self.set_model(self.store)
        cell = Gtk.CellRendererText()
        self.pack_start(cell,True)
        self.add_attribute(cell,'text',0)
        self.mapping = {}

        self.store.append(row=[_('Portrait')])
        self.store.append(row=[_('Landscape')])
        if default == PAPER_PORTRAIT:
            self.set_active(0)
        else:
            self.set_active(1)

    def set_value(self,value=0):
        if value == PAPER_PORTRAIT:
            self.set_active(0)
        else:
            self.set_active(1)

    def get_value(self):
        active = self.get_active()
        if active < 0:
            return None
        if active == 0:
            return PAPER_PORTRAIT
        else:
            return PAPER_LANDSCAPE

#-------------------------------------------------------------------------
#
# PaperFrame
#
#-------------------------------------------------------------------------
class PaperFrame(Gtk.Box):
    """PaperFrame provides all the entry necessary to specify a paper style. """
    def __init__(self,default_metric,default_name,default_orientation,
                 margins=[2.54,2.54,2.54,2.54], custom=[29.7,21.0]):
        Gtk.Box.__init__(self)
        glade_xml = Glade()

        self.paper_grid = glade_xml.get_object('paper_grid')
        self.top = glade_xml.get_object('papermenu')

        # get all the widgets
        widgets = ('pwidth', 'pheight', 'lmargin', 'rmargin', 'tmargin',
                   'bmargin', 'lunits1', 'lunits2', 'lunits3', 'lunits4',
                   'lunits5', 'lunits6', 'metric')

        for w in widgets:
            setattr(self, w, glade_xml.get_object(w))

        # insert custom widgets
        self.papersize_menu = PaperComboBox(default_name)
        self.orientation_menu = OrientationComboBox(default_orientation)
        self.metric.set_active(default_metric)

        # connect all widgets
        format_grid = glade_xml.get_object('format_grid')
        format_grid.attach(self.papersize_menu, 1, 0, 1, 1)
        format_grid.attach(self.orientation_menu, 1, 3, 1, 1)

        # connect signals
        self.papersize_menu.connect('changed',self.size_changed)
        self.metric.connect('toggled',self.units_changed)

        # set initial values
        self.paper_unit = 'cm'
        self.paper_unit_multiplier = 1.0

        self.pwidth.set_text("%.2f" % custom[0])
        self.pheight.set_text("%.2f" % custom[1])
        self.lmargin.set_text("%.2f" % margins[0])
        self.rmargin.set_text("%.2f" % margins[1])
        self.tmargin.set_text("%.2f" % margins[2])
        self.bmargin.set_text("%.2f" % margins[3])

        self.paper_grid.show_all()
        # Shift the grid from glade toplevel window to this box
        self.paper_grid.get_parent().remove(self.paper_grid)
        self.add(self.paper_grid)
        # need to get rid of glade toplevel now that we are done with it.
        self.top.destroy()

        self.units_changed(self.metric)
        self.size_changed(None)

    def size_changed(self, obj):
        """Paper size combobox 'changed' callback."""
        size, name = self.get_paper_size()

        is_custom = name == "Custom Size"
        self.pwidth.set_sensitive(is_custom)
        self.pheight.set_sensitive(is_custom)

        if self.paper_unit == 'cm':
            self.pwidth.set_text("%.2f" % size.get_width())
            self.pheight.set_text("%.2f" % size.get_height())
        elif self.paper_unit == 'in.':
            self.pwidth.set_text("%.2f" % size.get_width_inches())
            self.pheight.set_text("%.2f" % size.get_height_inches())
        else:
            raise ValueError('Paper dimension unit "%s" is not allowed' %
                             self.paper_unit)

    def units_changed(self, checkbox):
        """Metric checkbox 'toggled' callback."""
        paper_size, paper_name = self.get_paper_size()
        paper_margins = self.get_paper_margins()

        if checkbox.get_active():
            self.paper_unit = 'cm'
            self.paper_unit_multiplier = 1.0
            paper_unit_text = _("cm")
        else:
            self.paper_unit = 'in.'
            self.paper_unit_multiplier = 2.54
            paper_unit_text = _("in.", "inch")

        self.lunits1.set_text(paper_unit_text)
        self.lunits2.set_text(paper_unit_text)
        self.lunits3.set_text(paper_unit_text)
        self.lunits4.set_text(paper_unit_text)
        self.lunits5.set_text(paper_unit_text)
        self.lunits6.set_text(paper_unit_text)

        if self.paper_unit == 'cm':
            self.pwidth.set_text("%.2f" % paper_size.get_width())
            self.pheight.set_text("%.2f" % paper_size.get_height())
        else:
            self.pwidth.set_text("%.2f" % paper_size.get_width_inches())
            self.pheight.set_text("%.2f" % paper_size.get_height_inches())

        self.lmargin.set_text("%.2f" %
                              (paper_margins[0] / self.paper_unit_multiplier))
        self.rmargin.set_text("%.2f" %
                              (paper_margins[1] / self.paper_unit_multiplier))
        self.tmargin.set_text("%.2f" %
                              (paper_margins[2] / self.paper_unit_multiplier))
        self.bmargin.set_text("%.2f" %
                              (paper_margins[3] / self.paper_unit_multiplier))

    def get_paper_size(self):
        """Read and validate paper size values.

        If needed update the dimensions from the width, height entries,
        and worst case fallback to A4 size.

        """
        papersize, papername = self.papersize_menu.get_value()
        if papername == 'Custom Size':
            try:
                h = float(str(self.pheight.get_text().replace(",", ".")))
                w = float(str(self.pwidth.get_text().replace(",", ".") ))

                if h <= 1.0 or w <= 1.0:
                    papersize.set_height(29.7)
                    papersize.set_width(21.0)
                else:
                    papersize.set_height(h * self.paper_unit_multiplier)
                    papersize.set_width(w * self.paper_unit_multiplier)
            except:
                papersize.set_height(29.7)
                papersize.set_width(21.0)

        return papersize, papername

    def get_paper_margins(self):
        """Get and validate margin values from dialog entries.

        Values returned in [cm].

        """
        paper_margins = [str(margin.get_text()) for margin in
            (self.lmargin, self.rmargin, self.tmargin, self.bmargin)]

        for i, margin in enumerate(paper_margins):
            try:
                paper_margins[i] = float(margin.replace(",", "."))
                paper_margins[i] = paper_margins[i] * self.paper_unit_multiplier
                paper_margins[i] = max(paper_margins[i], 0)
            except:
                paper_margins[i] = 2.54

        return paper_margins

    def get_custom_paper_size(self):
        """Get and validate custom paper size values from dialog entries.
           Float values returned.
        """
        try:
            width = float(self.pwidth.get_text().replace(",", ".")) * \
                        self.paper_unit_multiplier
            height = float(self.pheight.get_text().replace(",", ".")) * \
                        self.paper_unit_multiplier
        except ValueError:
            width = float(21.0)
            height = float(29.7)

        paper_size = [max(width, 1.0), max(height, 1.0)]

        return paper_size

    def get_paper_style(self):
        paper_size, paper_name = self.get_paper_size()
        paper_orientation = self.orientation_menu.get_value()
        paper_margins = self.get_paper_margins()

        pstyle = PaperStyle(paper_size,
                            paper_orientation,
                            *paper_margins)
        return pstyle

    def get_paper_metric(self):
        return self.metric.get_active()

    def get_paper_name(self):
        paper_size, paper_name = self.get_paper_size()
        return paper_name

    def get_orientation(self):
        return self.orientation_menu.get_value()
