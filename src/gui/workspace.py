#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2010       Douglas S. Blank <doug.blank@gmail.com>
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

"""
Workspace
"""
#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# GNOME modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import Errors
from gui.sidebar import Sidebar
from gui.widgets.grampletpane import GrampletPane
from gui.views.listview import ListView
from gui.configure import ConfigureDialog
import config

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
GRAMPLET_PAGE = 0
FILTER_PAGE = 1

#-------------------------------------------------------------------------
#
# Workspace class
#
#-------------------------------------------------------------------------
class Workspace(object):
    """
    A Workspace contains panes to contain a view and associated objects such as
    a filter and gramplet pane.
    """
    def __init__(self, uistate, dbstate):
        self.uistate = uistate
        self.dbstate = dbstate
        self.active = False
        self.view = None
        self._config = None
        self.sidebar = Sidebar(self.sidebar_changed, self.sidebar_closed)
        self.hpane = gtk.HPaned()
        self.vpane = gtk.VPaned()
        self.hpane.pack1(self.vpane, resize=True, shrink=True)
        self.hpane.pack2(self.sidebar.get_display(), resize=False, shrink=False)
        self.hpane.show()
        self.vpane.show()
        
    def get_display(self):
        """
        Return the top container widget for the GUI.
        """
        return self.hpane
        
    def add_view(self, view):
        """
        Add a view to the workspace.
        """
        self.view = view
        self.vpane.add1(view.get_display())
        initial_page = self.view._config.get('sidebar.page')
        
        self.gramplet_pane = self.__create_gramplet_pane()

        if isinstance(view, ListView):
            self.add_filter(view.filter_class)

        if self.view._config.get('sidebar.visible'):
            self.sidebar.show()
        else:
            self.sidebar.hide()

        self.sidebar.set_current_page(initial_page)

    def add_aux(self, aux):
        """
        Add an auxilliary object to the workspace.
        """
        self.aux = aux
        self.vpane.add2(aux.get_display())

    def add_filter(self, filter_class):
        """
        Add a filter to the workspace sidebar.
        """
        self.filter_sidebar = filter_class(self.dbstate, self.uistate, 
                                           self.__filter_clicked)
        top = self.filter_sidebar.get_widget()
        top.show_all()
        self.sidebar.add(_('Filter'), top, FILTER_PAGE)

    def remove_filter(self,):
        """
        Remove the filter from the workspace sidebar.
        """
        self.filter_sidebar = None
        self.sidebar.remove(FILTER_PAGE)
        
    def __create_gramplet_pane(self):
        """
        Create a gramplet pane.
        """
        self.uidef = '''<ui>
          <menubar name="MenuBar">
            <menu action="ViewMenu">
              <placeholder name="Bars">
                <menuitem action="Sidebar"/>
              </placeholder>
            </menu>
          </menubar>
          <popup name="Popup">
            <menuitem action="AddGramplet"/>
            <menuitem action="RestoreGramplet"/>
          </popup>
        </ui>'''
        
        eb = gtk.EventBox()
        eb.connect('button-press-event', self._gramplet_button_press)
        
        gramplet_pane = GrampletPane(self.view.ident + "_sidebar", 
                               self, self.dbstate, self.uistate, 
                               column_count=1)
        gramplet_pane.show_all()
        eb.add(gramplet_pane)
        eb.show()                   
        self.sidebar.add(_('Gramplets'), eb, GRAMPLET_PAGE)
        return gramplet_pane
        
    def _gramplet_button_press(self, obj, event):
        """
        Called to display the context menu in the gramplet pane.
        """
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            menu = self.uistate.uimanager.get_widget('/Popup')
            if menu:
                menu.popup(None, None, None, event.button, event.time)
                return True

    def __filter_clicked(self):
        """
        Called when the filter 'Find' button is clicked.
        """
        self.view.generic_filter = self.filter_sidebar.get_filter()
        self.view.build_tree()

    def __sidebar_toggled(self, action):
        """
        Called when the sidebar is toggled.
        """
        active = action.get_active()
        if active:
            self.sidebar.show()
            self.sidebar_changed(self.sidebar.get_page_type(), True, None)
        else:
            self.sidebar.hide()
            self.sidebar_changed(None, False, None)
        self.view._config.set('sidebar.visible', active)

    def sidebar_changed(self, page_type, active, index):
        """
        Called when the sidebar page is changed.
        """
        if index is not None:
            self.view._config.set('sidebar.page', index)
        if isinstance(self.view, ListView):
            if active and page_type == FILTER_PAGE:
                self.view.search_bar.hide()
            else:
                self.view.search_bar.show()

    def sidebar_closed(self):
        """
        Called when the sidebar close button is clicked.
        """
        uimanager = self.uistate.uimanager
        uimanager.get_action('/MenuBar/ViewMenu/Bars/Sidebar').activate()

    def get_title(self):
        """
        Return the title of the view.
        """
        if self.view:
            return self.view.title
        return ''
        
    def define_actions(self):
        """
        Defines the UIManager actions.
        """
        self.action_group = gtk.ActionGroup('Workspace')
        self.action_group.add_toggle_actions([
            ('Sidebar', None, _('_Sidebar'), 
             None, None, self.__sidebar_toggled,
             self.view._config.get('sidebar.visible'))
            ])
        self.action_group.add_actions([
            ("AddGramplet", None, _("Add a gramplet")),
            ("RestoreGramplet", None, _("Restore a gramplet")
            )])

    def set_active(self):
        """
        Called when the view is set as active.
        """
        self.active = True
        self.gramplet_pane.set_active()
        self.view.set_active()

    def set_inactive(self):
        """
        Called when the view is set as inactive.
        """
        self.active = False
        self.gramplet_pane.set_inactive()
        self.view.set_inactive()

    def get_actions(self):
        """
        Return the actions that should be used for the view.
        """
        action_list = self.view.get_actions()
        action_list.append(self.action_group)
        return action_list

    def ui_definition(self):
        """
        Returns the XML UI definition for the UIManager.
        """
        return self.view.ui_definition()

    def additional_ui_definitions(self):
        """
        Return any additional interfaces for the UIManager that the view
        needs to define.
        """
        defs = self.view.additional_ui_definitions()
        defs.append(self.uidef)
        return defs

    def change_page(self):
        """
        Called when the view changes.
        """
        self.view.change_page()

    def on_delete(self):
        """
        Method called on shutdown.
        """
        self.view.on_delete()
        self.gramplet_pane.on_delete()

    def can_configure(self):
        """
        Returns True if the workspace has a configure window.
        """
        return self.view.can_configure() or self.gramplet_pane.can_configure()

    def _get_configure_page_funcs(self):
        """
        Return a list of functions that create gtk elements to use in the 
        notebook pages of the Configuration dialog.
        """
        retval = []
        if self.view.can_configure():
            other = self.view._get_configure_page_funcs()
            if callable(other):
                retval += other()
            else:
                retval += other
        func = self.gramplet_pane._get_configure_page_funcs()
        return retval + func()

    def configure(self):
        """
        Open the configure dialog for the workspace.
        """
        __configure_content = self._get_configure_page_funcs()
        title = _("Configure %(cat)s - %(view)s") % \
                        {'cat': self.view.get_translated_category(), 
                         'view': self.view.get_title()}
        try:
            ViewConfigureDialog(self.uistate, self.dbstate, 
                            __configure_content,
                            self, self.view._config, dialogtitle=title,
                            ident=_("%(cat)s - %(view)s") % 
                                    {'cat': self.view.get_translated_category(),
                                     'view': self.view.get_title()})
        except Errors.WindowActiveError:
            return

class ViewConfigureDialog(ConfigureDialog):
    """
    All workspaces can have their own configuration dialog
    """
    def __init__(self, uistate, dbstate, configure_page_funcs, configobj,
                 configmanager,
                 dialogtitle=_("Preferences"), on_close=None, ident=''):
        self.ident = ident
        ConfigureDialog.__init__(self, uistate, dbstate, configure_page_funcs,
                                 configobj, configmanager,
                                 dialogtitle=dialogtitle, on_close=on_close)
        
    def build_menu_names(self, obj):
        return (_('Configure %s View') % self.ident, None)
