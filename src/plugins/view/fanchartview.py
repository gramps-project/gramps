# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham, Martin Hawlisch
# Copyright (C) 2009 Douglas S. Blank
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

# $Id$

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
from gi.repository import Gdk
from gi.repository import Gtk
import cairo
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import gen.lib
from gui.widgets.fanchart import FanChartWidget, FanChartGrampsGUI
from gui.views.navigationview import NavigationView
from gen.errors import WindowActiveError
from gui.views.bookmarks import PersonBookmarks
from gui.editors import EditPerson
from gui.utils import SystemFonts

# the print settings to remember between print sessions
PRINT_SETTINGS = None

class FanChartView(FanChartGrampsGUI, NavigationView):
    """
    The Gramplet code that realizes the FanChartWidget. 
    """
    #settings in the config file
    CONFIGSETTINGS = (
        ('interface.fanview-maxgen', 9),
        ('interface.fanview-background', 0),
        ('interface.fanview-childrenring', True),
        ('interface.fanview-radialtext', True),
        ('interface.fanview-font', 'Sans'),
        ('interface.color-start-grad', '#ef2929'),
        ('interface.color-end-grad', '#3d37e9'),
        )
    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        self.dbstate = dbstate
        self.uistate = uistate
        NavigationView.__init__(self, _('Fan Chart'),
                                      pdata, dbstate, uistate, 
                                      dbstate.db.get_bookmarks(), 
                                      PersonBookmarks,
                                      nav_group)
        FanChartGrampsGUI.__init__(self, 
                    self._config.get('interface.fanview-maxgen'),
                    self._config.get('interface.fanview-background'),
                    self._config.get('interface.fanview-childrenring'),
                    self._config.get('interface.fanview-radialtext'),
                    self._config.get('interface.fanview-font'),
                    self.on_childmenu_changed)
        
        self.grad_start =  self._config.get('interface.color-start-grad')
        self.grad_end =  self._config.get('interface.color-end-grad')

        dbstate.connect('active-changed', self.active_changed)
        dbstate.connect('database-changed', self.change_db)

        self.additional_uis.append(self.additional_ui())
        self.allfonts = [x for x in enumerate(SystemFonts().get_system_fonts())]

    def navigation_type(self):
        return 'Person'

    def build_widget(self):
        self.set_fan(FanChartWidget(self.dbstate, self.on_popup))
        self.scrolledwindow = Gtk.ScrolledWindow(None, None)
        self.scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC,
                                       Gtk.PolicyType.AUTOMATIC)
        self.fan.show_all()
        self.scrolledwindow.add_with_viewport(self.fan)

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

    def additional_ui(self):
        return '''<ui>
          <menubar name="MenuBar">
            <menu action="GoMenu">
              <placeholder name="CommonGo">
                <menuitem action="Back"/>
                <menuitem action="Forward"/>
                <separator/>
                <menuitem action="HomePerson"/>
                <separator/>
              </placeholder>
            </menu>
            <menu action="EditMenu">
              <placeholder name="CommonEdit">
                <menuitem action="PrintView"/>
              </placeholder>
            </menu>
            <menu action="BookMenu">
              <placeholder name="AddEditBook">
                <menuitem action="AddBook"/>
                <menuitem action="EditBook"/>
              </placeholder>
            </menu>
          </menubar>
          <toolbar name="ToolBar">
            <placeholder name="CommonNavigation">
              <toolitem action="Back"/>  
              <toolitem action="Forward"/>  
              <toolitem action="HomePerson"/>
            </placeholder>
            <placeholder name="CommonEdit">
              <toolitem action="PrintView"/>
            </placeholder>
          </toolbar>
        </ui>
        '''

    def define_actions(self):
        """
        Required define_actions function for PageView. Builds the action
        group information required.
        """
        NavigationView.define_actions(self)

        self._add_action('PrintView', Gtk.STOCK_PRINT, _("_Print/Save View..."), 
                         accel="<PRIMARY>P", 
                         tip=_("Print or save the Fan Chart View"), 
                         callback=self.printview)
    def build_tree(self):
        pass # will build when active_changes

    def active_changed(self, handle):
        """
        Method called when active person changes.
        """
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
        self._change_db(db)
        self.bookmarks.update_bookmarks(self.dbstate.db.get_bookmarks())
        if self.active:
            self.bookmarks.redraw()
        self.update()

    def update(self):
        self.main()
        
    def goto_handle(self, handle):
        self.change_active(handle)
        self.main()

    def get_active(self, object):
        """overrule get_active, to support call as in Gramplets
        """
        return NavigationView.get_active(self)

    def person_rebuild(self, *args):
        self.update()

    def person_rebuild_bm(self, *args):
        """Large change to person database"""
        self.person_rebuild()
        if self.active:
            self.bookmarks.redraw()

    def printview(self, obj):
        """
        Print or save the view that is currently shown
        """
        widthpx = 2*(self.fan.pixels_per_generation * self.fan.nrgen() 
                        + self.fan.center)
        prt = CairoPrintSave(widthpx, self.fan.on_draw, self.uistate.window)
        prt.run()

    def on_childmenu_changed(self, obj, person_handle):
        """Callback for the pulldown menu selection, changing to the person
           attached with menu item."""
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
        nrentry = 7
        table = Gtk.Table(6, 3)
        table.set_border_width(12)
        table.set_col_spacings(6)
        table.set_row_spacings(6)

        configdialog.add_spinner(table, _("Max generations"), 0,
                'interface.fanview-maxgen', (1, 11), 
                callback=self.cb_update_maxgen)
        configdialog.add_combo(table, 
                _('Text Font'), 
                1, 'interface.fanview-font',
                self.allfonts, callback=self.cb_update_font, valueactive=True)
        configdialog.add_combo(table, 
                _('Background'), 
                2, 'interface.fanview-background',
                (
                (0, _('Color scheme 1')),
                (1, _('Color scheme 2')),
                (2, _('Gender colors')),
                (3, _('White')),
                (4, _('Generation based gradient')),
                ),
                callback=self.cb_update_background)
        #colors, stored as hex values
        configdialog.add_color(table, _('Start gradient/Main color'), 3, 
                        'interface.color-start-grad', col=1)
        configdialog.add_color(table, _('End gradient/2nd color'), 4, 
                        'interface.color-end-grad',  col=1)
        
        # options users should not change:
        configdialog.add_checkbox(table, 
                _('Show children ring'), 
                nrentry-2, 'interface.fanview-childrenring')
        configdialog.add_checkbox(table, 
                _('Allow radial text at generation 6'), 
                nrentry-1, 'interface.fanview-radialtext')

        return _('Layout'), table

    def config_connect(self):
        """
        Overwriten from  :class:`~gui.views.pageview.PageView method
        This method will be called after the ini file is initialized,
        use it to monitor changes in the ini file
        """
        self._config.connect('interface.fanview-childrenring',
                          self.cb_update_childrenring)
        self._config.connect('interface.fanview-radialtext',
                          self.cb_update_radialtext)
        self._config.connect('interface.color-start-grad',
                          self.cb_update_color)
        self._config.connect('interface.color-end-grad',
                          self.cb_update_color)

    def cb_update_maxgen(self, spinbtn, constant):
        self.maxgen = spinbtn.get_value_as_int()
        self._config.set(constant, self.maxgen)
        self.update()

    def cb_update_background(self, obj, constant):
        entry = obj.get_active()
        self._config.set(constant, entry)
        self.background = int(entry)
        self.update()

    def cb_update_childrenring(self, client, cnxn_id, entry, data):
        """
        Called when the configuration menu changes the childrenring setting. 
        """
        if entry == 'True':
            self.childring = True
        else:
            self.childring = False
        self.update()

    def cb_update_radialtext(self, client, cnxn_id, entry, data):
        """
        Called when the configuration menu changes the childrenring setting. 
        """
        if entry == 'True':
            self.radialtext = True
        else:
            self.radialtext = False
        self.update()

    def cb_update_color(self, client, cnxn_id, entry, data):
        """
        Called when the configuration menu changes the childrenring setting. 
        """
        self.grad_start = self._config.get('interface.color-start-grad')
        self.grad_end = self._config.get('interface.color-end-grad')
        self.update()

    def cb_update_font(self, obj, constant):
        entry = obj.get_active()
        self._config.set(constant, self.allfonts[entry][1])
        self.fonttype = self.allfonts[entry][1]
        self.update()

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
    
    def __init__(self, widthpx, drawfunc, parent):
        """
        This class provides the things needed so as to dump a cairo drawing on
        a context to output
        """
        self.widthpx = widthpx
        self.drawfunc = drawfunc
        self.parent = parent
    
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
                                              round(self.widthpx * 0.2646),
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
            res = operation.run(Gtk.PrintOperationAction.PRINT_DIALOG, self.parent)
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
        cr = context.get_cairo_context()
        pxwidth = round(context.get_width())
        pxheight = round(context.get_height())
        dpi_x = context.get_dpi_x()
        dpi_y = context.get_dpi_y()
        self.drawfunc(None, cr, scale=pxwidth/self.widthpx)

    def on_paginate(self, operation, context):
        """Paginate the whole document in chunks.
           We don't need this as there is only one page, however,
           we provide a dummy holder here, because on_preview crashes if no 
           default application is set with gir 3.3.2 (typically evince not installed)!
           It will provide the start of the preview dialog, which cannot be
           started in on_preview
        """
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
           default application is set with gir 3.3.2 (typically evince not installed)!
        """
        dlg = Gtk.MessageDialog(parent,
                                   flags=Gtk.DialogFlags.MODAL,
                                   type=Gtk.MessageType.WARNING,
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
        cr = cairo.Context(surface)
        context.set_cairo_context(cr, 72.0, 72.0)
        
        return True 

    def previewdestroy(self, dlg, res):
        self.preview.destroy()
        self.previewopr.end_preview()
