# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham, Martin Hawlisch
# Copyright (C) 2009 Douglas S. Blank
# Copyright (C) 2014 Bastien Jacquet
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

## Based on the paper:
##   http://www.cs.utah.edu/~draperg/research/fanchart/draperg_FHT08.pdf
## and the applet:
##   http://www.cs.utah.edu/~draperg/research/fanchart/demo/

## Found by redwood:
## http://www.gramps-project.org/bugs/view.php?id=2611

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
import cairo
from gramps.gen.const import GRAMPS_LOCALE as glocale

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import gramps.gui.widgets.fanchart as fanchart
import gramps.gui.widgets.fanchart2way as fanchart2way
from gramps.gui.views.navigationview import NavigationView
from gramps.gui.views.bookmarks import PersonBookmarks
from gramps.gui.utils import SystemFonts
from gramps.plugins.view.fanchartview import FanChartView

# the print settings to remember between print sessions
PRINT_SETTINGS = None
_ = glocale.translation.gettext

class FanChart2WayView(fanchart2way.FanChart2WayGrampsGUI, NavigationView):
    """
    The Gramplet code that realizes the FanChartWidget.
    """
    #settings in the config file
    CONFIGSETTINGS = (
        ('interface.fanview-maxgen-asc', 4),
        ('interface.fanview-maxgen-desc', 4),
        ('interface.fanview-background', fanchart.BACKGROUND_GRAD_GEN),
        ('interface.fanview-background-gradient', True),
        ('interface.fanview-radialtext', True),
        ('interface.fanview-twolinename', True),
        ('interface.fanview-flipupsidedownname', True),
        ('interface.fanview-font', 'Sans'),
        ('interface.fanview-form', fanchart.FORM_CIRCLE),
        ('interface.fanview-showid', False),
        ('interface.color-start-grad', '#ef2929'),
        ('interface.color-end-grad', '#3d37e9'),
        ('interface.angle-algorithm', fanchart2way.ANGLE_WEIGHT),
        ('interface.duplicate-color', '#888a85')
        )
    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        self.dbstate = dbstate
        self.uistate = uistate

        NavigationView.__init__(self, _('2-Way Fan Chart'),
                                pdata, dbstate, uistate,
                                PersonBookmarks, nav_group)
        fanchart2way.FanChart2WayGrampsGUI.__init__(self,
                                                    self.on_childmenu_changed)
        #set needed values
        scg = self._config.get
        self.generations_asc = scg('interface.fanview-maxgen-asc')
        self.generations_desc = scg('interface.fanview-maxgen-desc')
        self.background = scg('interface.fanview-background')
        self.background_gradient = scg('interface.fanview-background-gradient')
        self.radialtext = scg('interface.fanview-radialtext')
        self.twolinename = scg('interface.fanview-twolinename')
        self.flipupsidedownname = scg('interface.fanview-flipupsidedownname')
        self.fonttype = scg('interface.fanview-font')

        self.grad_start = scg('interface.color-start-grad')
        self.grad_end = scg('interface.color-end-grad')
        self.form = fanchart.FORM_CIRCLE
        self.showid = scg('interface.fanview-showid')
        self.angle_algo = scg('interface.angle-algorithm')
        self.dupcolor = scg('interface.duplicate-color')
        self.generic_filter = None
        self.alpha_filter = 0.2
        self.scrolledwindow = None

        dbstate.connect('active-changed', self.active_changed)
        dbstate.connect('database-changed', self.change_db)

        self.additional_uis.append(FanChartView.additional_ui)
        self.allfonts = [x for x in enumerate(SystemFonts().get_system_fonts())]

        self.uistate.connect('font-changed', self.font_changed)

    def font_changed(self):
        self.format_helper.reload_symbols()
        self.update()

    def navigation_type(self):
        return 'Person'

    def get_handle_from_gramps_id(self, gid):
        """
        returns the handle of the specified object
        """
        obj = self.dbstate.db.get_person_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        else:
            return None

    def build_widget(self):
        self.set_fan(fanchart2way.FanChart2WayWidget(self.dbstate, self.uistate,
                                                     self.on_popup))
        self.scrolledwindow = Gtk.ScrolledWindow(hadjustment=None,
                                                 vadjustment=None)
        self.scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC,
                                       Gtk.PolicyType.AUTOMATIC)
        self.fan.show_all()
        self.scrolledwindow.add(self.fan)

        return self.scrolledwindow

    def get_stock(self):
        """
        The category stock icon
        """
        return 'gramps-pedigree'

    def get_viewtype_stock(self):
        """Type of view in category
        """
        return 'gramps-fanchart'

    def define_actions(self):
        """
        Required define_actions function for PageView. Builds the action
        group information required.
        """
        NavigationView.define_actions(self)

        self._add_action('PrintView', self.printview, "<PRIMARY><SHIFT>P")
        self._add_action('PRIMARY-J', self.jump, '<PRIMARY>J')

    def build_tree(self):
        """
        Generic method called by PageView to construct the view.
        Here the tree builds when active person changes or db changes or on
        callbacks like person_rebuild, so build will be double sometimes.
        However, change in generic filter also triggers build_tree ! So we
        need to reset.
        """
        self.update()

    def active_changed(self, handle):
        """
        Method called when active person changes.
        """
        dummy_handle = handle
        # Reset everything but rotation angle (leave it as is)
        self.update()

    def _connect_db_signals(self):
        """
        Connect database signals.
        """
        self._add_db_signal('person-add', self.person_rebuild)
        self._add_db_signal('person-update', self.person_rebuild)
        self._add_db_signal('person-delete', self.person_rebuild)
        self._add_db_signal('person-rebuild', self.person_rebuild_bm)
        self._add_db_signal('family-update', self.person_rebuild)
        self._add_db_signal('family-add', self.person_rebuild)
        self._add_db_signal('family-delete', self.person_rebuild)
        self._add_db_signal('family-rebuild', self.person_rebuild)

    def change_db(self, db):
        """
        We selected a new database
        """
        self._change_db(db)
        if self.active:
            self.bookmarks.redraw()
        self.update()

    def update(self):
        """
        Redraw the fan chart
        """
        self.main()

    def goto_handle(self, handle):
        """
        Draw the fan chart for the active person
        """
        self.change_active(handle)
        self.main()

    def get_active(self, obj):
        """overrule get_active, to support call as in Gramplets
        """
        dummy_obj = obj
        return NavigationView.get_active(self)

    def person_rebuild(self, *args):
        """
        Redraw the fan chart for the person
        """
        dummy_args = args
        self.update()

    def person_rebuild_bm(self, *args):
        """Large change to person database"""
        dummy_args = args
        self.person_rebuild()
        if self.active:
            self.bookmarks.redraw()

    def printview(self, *obj):
        """
        Print or save the view that is currently shown
        """
        dummy_obj = obj
        widthpx = 2 * self.fan.halfdist()
        heightpx = widthpx

        prt = CairoPrintSave(widthpx, heightpx, self.fan.prt_draw,
                             self.uistate.window)
        prt.run()

    def on_childmenu_changed(self, obj, person_handle):
        """Callback for the pulldown menu selection, changing to the person
           attached with menu item."""
        dummy_obj = obj
        self.change_active(person_handle)
        return True

    def can_configure(self):
        """
        See :class:`~gui.views.pageview.PageView
        :return: bool
        """
        return True

    def _get_configure_page_funcs(self):
        """
        Return a list of functions that create gtk elements to use in the
        notebook pages of the Configure dialog

        :return: list of functions
        """
        return [self.config_panel]

    def config_panel(self, configdialog):
        """
        Function that builds the widget in the configuration dialog
        """
        grid = Gtk.Grid()
        grid.set_border_width(12)
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)

        configdialog.add_spinner(grid, _("Max ancestor generations"), 0,
                                 'interface.fanview-maxgen-asc', (1, 11),
                                 callback=self.cb_update_maxgen)
        configdialog.add_spinner(grid, _("Max descendant generations"), 1,
                                 'interface.fanview-maxgen-desc', (1, 11),
                                 callback=self.cb_update_maxgen)
        configdialog.add_combo(grid, _('Text Font'), 2,
                               'interface.fanview-font',
                               self.allfonts, callback=self.cb_update_font,
                               valueactive=True)
        backgrvals = (
            (fanchart.BACKGROUND_GENDER, _('Gender colors')),
            (fanchart.BACKGROUND_GRAD_GEN, _('Generation based gradient')),
            (fanchart.BACKGROUND_GRAD_AGE, _('Age (0-100) based gradient')),
            (fanchart.BACKGROUND_SINGLE_COLOR, _('Single main (filter) color')),
            (fanchart.BACKGROUND_GRAD_PERIOD, _('Time period based gradient')),
            (fanchart.BACKGROUND_WHITE, _('White')),
            (fanchart.BACKGROUND_SCHEME1, _('Color scheme classic report')),
            (fanchart.BACKGROUND_SCHEME2, _('Color scheme classic view')),
            )
        curval = self._config.get('interface.fanview-background')
        nrval = 0
        for nbr, dummy_val in backgrvals:
            if curval == nbr:
                break
            nrval += 1
        configdialog.add_combo(grid, _('Background'), 3,
                               'interface.fanview-background', backgrvals,
                               callback=self.cb_update_background,
                               valueactive=False, setactive=nrval)

        # show names one two line
        configdialog.add_checkbox(grid,
                                  _('Add global background colored gradient'),
                                  4, 'interface.fanview-background-gradient')

        #colors, stored as hex values
        configdialog.add_color(grid, _('Start gradient/Main color'), 5,
                               'interface.color-start-grad', col=1)
        configdialog.add_color(grid, _('End gradient/2nd color'), 6,
                               'interface.color-end-grad', col=1)
        configdialog.add_color(grid, _('Color for duplicates'), 7,
                               'interface.duplicate-color', col=1)
        # algo for the fan angle distribution
        configdialog.add_combo(grid, _('Fan chart distribution'), 8,
                               'interface.angle-algorithm',
                               ((fanchart2way.ANGLE_CHEQUI,
                                 _('Homogeneous children distribution')),
                                (fanchart2way.ANGLE_WEIGHT,
                                 _('Size proportional to number'
                                   ' of descendants')),
                               ),
                               callback=self.cb_update_anglealgo)

        # show names one two line
        configdialog.add_checkbox(grid, _('Show names on two lines'),
                                  9, 'interface.fanview-twolinename')

        # Flip names
        configdialog.add_checkbox(grid, _('Flip name on the left of the fan'),
                                  10, 'interface.fanview-flipupsidedownname')

        # Show gramps id
        configdialog.add_checkbox(grid, _('Show the gramps id'),
                                  11, 'interface.fanview-showid')

        return _('Layout'), grid

    def config_connect(self):
        """
        Overwriten from  :class:`~gui.views.pageview.PageView method
        This method will be called after the ini file is initialized,
        use it to monitor changes in the ini file
        """
        self._config.connect('interface.color-start-grad',
                             self.cb_update_color)
        self._config.connect('interface.color-end-grad',
                             self.cb_update_color)
        self._config.connect('interface.duplicate-color',
                             self.cb_update_color)
        self._config.connect('interface.fanview-flipupsidedownname',
                             self.cb_update_flipupsidedownname)
        self._config.connect('interface.fanview-twolinename',
                             self.cb_update_twolinename)
        self._config.connect('interface.fanview-background-gradient',
                             self.cb_update_background_gradient)
        self._config.connect('interface.fanview-showid',
                             self.cb_update_showid)

    def cb_update_maxgen(self, spinbtn, constant):
        """
        The maximum generations in the fanchart
        """
        self._config.set(constant, spinbtn.get_value_as_int())
        scg = self._config.get
        self.generations_asc = int(scg('interface.fanview-maxgen-asc'))
        self.generations_desc = int(scg('interface.fanview-maxgen-desc'))
        self.update()

    def cb_update_twolinename(self, client, cnxn_id, entry, data):
        """
        Called when the configuration menu changes the twolinename setting.
        """
        self.twolinename = (entry == 'True')
        self.update()

    def cb_update_showid(self, client, cnxn_id, entry, data):
        """
        Called when the configuration menu changes the showid setting.
        """
        self.showid = (entry == 'True')
        self.update()

    def cb_update_background(self, obj, constant):
        """
        The background selected
        """
        entry = obj.get_active()
        Gtk.TreePath.new_from_string('%d' % entry)
        val = int(obj.get_model().get_value(
            obj.get_model().get_iter_from_string('%d' % entry), 0))
        self._config.set(constant, val)
        self.background = val
        self.update()

    def cb_update_background_gradient(self, client, cnxn_id, entry, data):
        """
        Called when the configuration menu changes the twolinename setting.
        """
        self.background_gradient = (entry == 'True')
        self.update()

    def cb_update_form(self, obj, constant):
        """
        Update the fanchart form: CIRCLE, HALFCIRCLE or QUADRANT
        """
        entry = obj.get_active()
        self._config.set(constant, entry)
        self.form = entry
        self.update()

    def cb_update_anglealgo(self, obj, constant):
        """
        Update the angle algorythm : homogeneous children distribution or not
        """
        entry = obj.get_active()
        self._config.set(constant, entry)
        self.angle_algo = entry
        self.update()

    def cb_update_color(self, client, cnxn_id, entry, data):
        """
        Called when the configuration menu changes the childrenring setting.
        """
        self.grad_start = self._config.get('interface.color-start-grad')
        self.grad_end = self._config.get('interface.color-end-grad')
        self.dupcolor = self._config.get('interface.duplicate-color')
        self.update()

    def cb_update_flipupsidedownname(self, client, cnxn_id, entry, data):
        """
        Called when the configuration menu changes the
        flipupsidedownname setting.
        """
        self.flipupsidedownname = (entry == 'True')
        self.update()

    def cb_update_font(self, obj, constant):
        """
        Update the choosed font
        """
        entry = obj.get_active()
        self._config.set(constant, self.allfonts[entry][1])
        self.fonttype = self.allfonts[entry][1]
        self.update()

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return (("Person Filter",),
                ())

#------------------------------------------------------------------------
#
# CairoPrintSave class
#
#------------------------------------------------------------------------
class CairoPrintSave():
    """Act as an abstract document that can render onto a cairo context.

    It can render the model onto cairo context pages, according to the received
    page style.

    """

    def __init__(self, widthpx, heightpx, drawfunc, parent):
        """
        This class provides the things needed so as to dump a cairo drawing on
        a context to output
        """
        self.widthpx = widthpx
        self.heightpx = heightpx
        self.drawfunc = drawfunc
        self.parent = parent
        self.preview = None
        self.previewopr = None

    def run(self):
        """Create the physical output from the meta document.

        """
        global PRINT_SETTINGS

        # set up a print operation
        operation = Gtk.PrintOperation()
        operation.connect("draw_page", self.on_draw_page)
        operation.connect("preview", self.on_preview)
        operation.connect("paginate", self.on_paginate)
        operation.set_n_pages(1)
        #paper_size = Gtk.PaperSize.new(name="iso_a4")
        ## WHY no Gtk.Unit.PIXEL ?? Is there a better way to convert
        ## Pixels to MM ??
        paper_size = Gtk.PaperSize.new_custom("custom",
                                              "Custom Size",
                                              round(self.widthpx * 0.2646),
                                              round(self.heightpx * 0.2646),
                                              Gtk.Unit.MM)
        page_setup = Gtk.PageSetup()
        page_setup.set_paper_size(paper_size)
        #page_setup.set_orientation(Gtk.PageOrientation.PORTRAIT)
        operation.set_default_page_setup(page_setup)
        #operation.set_use_full_page(True)

        if PRINT_SETTINGS is not None:
            operation.set_print_settings(PRINT_SETTINGS)

        # run print dialog
        while True:
            self.preview = None
            res = operation.run(Gtk.PrintOperationAction.PRINT_DIALOG,
                                self.parent)
            if self.preview is None: # cancel or print
                break
            # set up printing again; can't reuse PrintOperation?
            operation = Gtk.PrintOperation()
            operation.set_default_page_setup(page_setup)
            operation.connect("draw_page", self.on_draw_page)
            operation.connect("preview", self.on_preview)
            operation.connect("paginate", self.on_paginate)
            # set print settings if it was stored previously
            if PRINT_SETTINGS is not None:
                operation.set_print_settings(PRINT_SETTINGS)

        # store print settings if printing was successful
        if res == Gtk.PrintOperationResult.APPLY:
            PRINT_SETTINGS = operation.get_print_settings()

    def on_draw_page(self, operation, context, page_nr):
        """Draw a page on a Cairo context.
        """
        dummy_operation = operation
        dummy_page_nr = page_nr
        ctx = context.get_cairo_context()
        pxwidth = round(context.get_width())
        pxheight = round(context.get_height())
        scale = min(pxwidth/self.widthpx, pxheight/self.heightpx)
        self.drawfunc(None, ctx, scale=scale)

    def on_paginate(self, operation, context):
        """Paginate the whole document in chunks.
           We don't need this as there is only one page, however,
           we provide a dummy holder here, because on_preview crashes if no
           default application is set with gir 3.3.2
           (typically evince not installed)!
           It will provide the start of the preview dialog, which cannot be
           started in on_preview
        """
        dummy_context = context
        finished = True
        # update page number
        operation.set_n_pages(1)

        # start preview if needed
        if self.preview:
            self.preview.run()

        return finished

    def on_preview(self, operation, preview, context, parent):
        """Implement custom print preview functionality.
           We provide a dummy holder here, because on_preview crashes if no
           default application is set with gir 3.3.2
           (typically evince not installed)!
        """
        dummy_preview = preview
        dlg = Gtk.MessageDialog(transient_for=parent,
                                modal=True,
                                message_type=Gtk.MessageType.WARNING,
                                buttons=Gtk.ButtonsType.CLOSE,
                                message_format=_('No preview available'))
        self.preview = dlg
        self.previewopr = operation
        #dlg.format_secondary_markup(msg2)
        dlg.set_title("Fan Chart Preview - Gramps")
        dlg.connect('response', self.previewdestroy)

        # give a dummy cairo context to Gtk.PrintContext,
        try:
            width = int(round(context.get_width()))
        except ValueError:
            width = 0
        try:
            height = int(round(context.get_height()))
        except ValueError:
            height = 0
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        context.set_cairo_context(ctx, 72.0, 72.0)

        return True

    def previewdestroy(self, dlg, res):
        """
        Destroy the preview page
        """
        dummy_dlg = dlg
        dummy_res = res
        self.preview.destroy()
        self.previewopr.end_preview()
