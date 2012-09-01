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
from cgi import escape
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.display.name import displayer as name_displayer
from gen.utils.db import (find_children, find_parents, find_witnessed_people)
from libformatting import FormattingHelper
import gen.lib
from gui.widgets.fanchart import FanChartWidget
from gui.views.navigationview import NavigationView
from gen.errors import WindowActiveError
from gui.views.bookmarks import PersonBookmarks
from gui.editors import EditPerson


# the print settings to remember between print sessions
PRINT_SETTINGS = None

class FanChartView(NavigationView):
    """
    The Gramplet code that realizes the FanChartWidget. 
    """
    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        NavigationView.__init__(self, _('Fan Chart'),
                                      pdata, dbstate, uistate, 
                                      dbstate.db.get_bookmarks(), 
                                      PersonBookmarks,
                                      nav_group)        

        dbstate.connect('active-changed', self.active_changed)
        dbstate.connect('database-changed', self.change_db)
        self.dbstate = dbstate
        self.uistate = uistate
        self.generations = 9
        self.format_helper = FormattingHelper(self.dbstate)

        self.additional_uis.append(self.additional_ui())

    def navigation_type(self):
        return 'Person'

    def build_widget(self):
        self.fan = FanChartWidget(self.generations, self.dbstate,
                                  context_popup_callback=self.on_popup)
        self.fan.format_helper = self.format_helper
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

    def change_db(self, db):
        self._change_db(db)
        #self.bookmarks.update_bookmarks(self.dbstate.db.get_bookmarks())
        #if self.active:
        #    self.bookmarks.redraw()
        self.update()

    def update(self):
        self.main()
        
    def goto_handle(self, handle):
        self.main()

    def have_parents(self, person):
        """
        Returns True if a person has parents.
        """
        if person:
            m = self.get_parent(person, False)
            f = self.get_parent(person, True)
            return not m is f is None
        return False
            
    def have_children(self, person):
        """
        Returns True if a person has children.
        """
        if person:
            for family_handle in person.get_family_handle_list():
                family = self.dbstate.db.get_family_from_handle(family_handle)
                if family and len(family.get_child_ref_list()) > 0:
                    return True
        return False
            
    def get_parent(self, person, father):
        """
        Get the father of the family if father == True, otherwise mother
        """
        if person:
            parent_handle_list = person.get_parent_family_handle_list()
            if parent_handle_list:
                family_id = parent_handle_list[0]
                family = self.dbstate.db.get_family_from_handle(family_id)
                if family:
                    if father:
                        person_handle = gen.lib.Family.get_father_handle(family)
                    else:
                        person_handle = gen.lib.Family.get_mother_handle(family)
                    if person_handle:
                        return self.dbstate.db.get_person_from_handle(person_handle)
        return None

    def main(self):
        """
        Fill the data structures with the active data. This initializes all 
        data.
        """
        self.fan.reset_generations()
        person = self.dbstate.db.get_person_from_handle(self.get_active())
        if not person: 
            name = None
        else:
            name = name_displayer.display(person)
        parents = self.have_parents(person)
        child = self.have_children(person)
        self.fan.data[0][0] = (name, person, parents, child)
        for current in range(1, self.generations):
            parent = 0
            # name, person, parents, children
            for (n,p,q,c) in self.fan.data[current - 1]:
                # Get father's details:
                person = self.get_parent(p, True)
                if person:
                    name = name_displayer.display(person)
                else:
                    name = None
                if current == self.generations - 1:
                    parents = self.have_parents(person)
                else:
                    parents = None
                self.fan.data[current][parent] = (name, person, parents, None)
                if person is None:
                    # start,stop,male/right,state
                    self.fan.angle[current][parent][3] = self.fan.COLLAPSED
                parent += 1
                # Get mother's details:
                person = self.get_parent(p, False)
                if person:
                    name = name_displayer.display(person)
                else:
                    name = None
                if current == self.generations - 1:
                    parents = self.have_parents(person)
                else:
                    parents = None
                self.fan.data[current][parent] = (name, person, parents, None)
                if person is None:
                    # start,stop,male/right,state
                    self.fan.angle[current][parent][3] = self.fan.COLLAPSED
                parent += 1
        self.fan.queue_draw()

    def on_childmenu_changed(self, obj, person_handle):
        """Callback for the pulldown menu selection, changing to the person
           attached with menu item."""
        self.change_active(person_handle)
        return True

    def edit_person_cb(self, obj,person_handle):
        person = self.dbstate.db.get_person_from_handle(person_handle)
        if person:
            try:
                EditPerson(self.dbstate, self.uistate, [], person,
                           callback=self.edit_callback)
            except WindowActiveError:
                pass
            return True
        return False

    def edit_callback(self, *args):
        self.update()

    def copy_person_to_clipboard_cb(self, obj, person_handle):
        """Renders the person data into some lines of text and puts that into the clipboard"""
        person = self.dbstate.db.get_person_from_handle(person_handle)
        if person:
            cb = Gtk.Clipboard.get_for_display(Gdk.Display.get_default(), 
                        Gdk.SELECTION_CLIPBOARD)
            cb.set_text( self.format_helper.format_person(person,11), -1)
            return True
        return False

    def on_popup(self, obj, event, person_handle):
        """
        Builds the full menu (including Siblings, Spouses, Children, 
        and Parents) with navigation. Copied from PedigreeView.
        """
        #store menu for GTK3 to avoid it being destroyed before showing
        self.menu = Gtk.Menu()
        menu = self.menu
        menu.set_title(_('People Menu'))

        person = self.dbstate.db.get_person_from_handle(person_handle)
        if not person:
            return 0

        go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO,Gtk.IconSize.MENU)
        go_image.show()
        go_item = Gtk.ImageMenuItem(name_displayer.display(person))
        go_item.set_image(go_image)
        go_item.connect("activate",self.on_childmenu_changed,person_handle)
        go_item.show()
        menu.append(go_item)

        edit_item = Gtk.ImageMenuItem.new_from_stock(stock_id=Gtk.STOCK_EDIT, accel_group=None)
        edit_item.connect("activate", self.edit_person_cb, person_handle)
        edit_item.show()
        menu.append(edit_item)

        clipboard_item = Gtk.ImageMenuItem.new_from_stock(stock_id=Gtk.STOCK_COPY, accel_group=None)
        clipboard_item.connect("activate",self.copy_person_to_clipboard_cb,person_handle)
        clipboard_item.show()
        menu.append(clipboard_item)

        # collect all spouses, parents and children
        linked_persons = []
        
        # Go over spouses and build their menu
        item = Gtk.MenuItem(label=_("Spouses"))
        fam_list = person.get_family_handle_list()
        no_spouses = 1
        for fam_id in fam_list:
            family = self.dbstate.db.get_family_from_handle(fam_id)
            if family.get_father_handle() == person.get_handle():
                sp_id = family.get_mother_handle()
            else:
                sp_id = family.get_father_handle()
            spouse = self.dbstate.db.get_person_from_handle(sp_id)
            if not spouse:
                continue

            if no_spouses:
                no_spouses = 0
                item.set_submenu(Gtk.Menu())
                sp_menu = item.get_submenu()

            go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO, Gtk.IconSize.MENU)
            go_image.show()
            sp_item = Gtk.ImageMenuItem(name_displayer.display(spouse))
            sp_item.set_image(go_image)
            linked_persons.append(sp_id)
            sp_item.connect("activate",self.on_childmenu_changed,sp_id)
            sp_item.show()
            sp_menu.append(sp_item)

        if no_spouses:
            item.set_sensitive(0)

        item.show()
        menu.append(item)
        
        # Go over siblings and build their menu
        item = Gtk.MenuItem(label=_("Siblings"))
        pfam_list = person.get_parent_family_handle_list()
        no_siblings = 1
        for f in pfam_list:
            fam = self.dbstate.db.get_family_from_handle(f)
            sib_list = fam.get_child_ref_list()
            for sib_ref in sib_list:
                sib_id = sib_ref.ref
                if sib_id == person.get_handle():
                    continue
                sib = self.dbstate.db.get_person_from_handle(sib_id)
                if not sib:
                    continue

                if no_siblings:
                    no_siblings = 0
                    item.set_submenu(Gtk.Menu())
                    sib_menu = item.get_submenu()

                if find_children(self.dbstate.db,sib):
                    label = Gtk.Label(label='<b><i>%s</i></b>' % escape(name_displayer.display(sib)))
                else:
                    label = Gtk.Label(label=escape(name_displayer.display(sib)))

                go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO, Gtk.IconSize.MENU)
                go_image.show()
                sib_item = Gtk.ImageMenuItem(None)
                sib_item.set_image(go_image)
                label.set_use_markup(True)
                label.show()
                label.set_alignment(0,0)
                sib_item.add(label)
                linked_persons.append(sib_id)
                sib_item.connect("activate", self.on_childmenu_changed, sib_id)
                sib_item.show()
                sib_menu.append(sib_item)

        if no_siblings:
            item.set_sensitive(0)
        item.show()
        menu.append(item)
        
        # Go over children and build their menu
        item = Gtk.MenuItem(label=_("Children"))
        no_children = 1
        childlist = find_children(self.dbstate.db, person)
        for child_handle in childlist:
            child = self.dbstate.db.get_person_from_handle(child_handle)
            if not child:
                continue
        
            if no_children:
                no_children = 0
                item.set_submenu(Gtk.Menu())
                child_menu = item.get_submenu()

            if find_children(self.dbstate.db,child):
                label = Gtk.Label(label='<b><i>%s</i></b>' % escape(name_displayer.display(child)))
            else:
                label = Gtk.Label(label=escape(name_displayer.display(child)))

            go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO, Gtk.IconSize.MENU)
            go_image.show()
            child_item = Gtk.ImageMenuItem(None)
            child_item.set_image(go_image)
            label.set_use_markup(True)
            label.show()
            label.set_alignment(0,0)
            child_item.add(label)
            linked_persons.append(child_handle)
            child_item.connect("activate", self.on_childmenu_changed, child_handle)
            child_item.show()
            child_menu.append(child_item)

        if no_children:
            item.set_sensitive(0)
        item.show()
        menu.append(item)

        # Go over parents and build their menu
        item = Gtk.MenuItem(label=_("Parents"))
        no_parents = 1
        par_list = find_parents(self.dbstate.db,person)
        for par_id in par_list:
            par = self.dbstate.db.get_person_from_handle(par_id)
            if not par:
                continue

            if no_parents:
                no_parents = 0
                item.set_submenu(Gtk.Menu())
                par_menu = item.get_submenu()

            if find_parents(self.dbstate.db,par):
                label = Gtk.Label(label='<b><i>%s</i></b>' % escape(name_displayer.display(par)))
            else:
                label = Gtk.Label(label=escape(name_displayer.display(par)))

            go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO, Gtk.IconSize.MENU)
            go_image.show()
            par_item = Gtk.ImageMenuItem(None)
            par_item.set_image(go_image)
            label.set_use_markup(True)
            label.show()
            label.set_alignment(0,0)
            par_item.add(label)
            linked_persons.append(par_id)
            par_item.connect("activate",self.on_childmenu_changed,par_id)
            par_item.show()
            par_menu.append(par_item)

        if no_parents:
            item.set_sensitive(0)
        item.show()
        menu.append(item)
    
        # Go over parents and build their menu
        item = Gtk.MenuItem(label=_("Related"))
        no_related = 1
        for p_id in find_witnessed_people(self.dbstate.db,person):
            #if p_id in linked_persons:
            #    continue    # skip already listed family members
            
            per = self.dbstate.db.get_person_from_handle(p_id)
            if not per:
                continue

            if no_related:
                no_related = 0
                item.set_submenu(Gtk.Menu())
                per_menu = item.get_submenu()

            label = Gtk.Label(label=escape(name_displayer.display(per)))

            go_image = Gtk.Image.new_from_stock(Gtk.STOCK_JUMP_TO, Gtk.IconSize.MENU)
            go_image.show()
            per_item = Gtk.ImageMenuItem(None)
            per_item.set_image(go_image)
            label.set_use_markup(True)
            label.show()
            label.set_alignment(0, 0)
            per_item.add(label)
            per_item.connect("activate", self.on_childmenu_changed, p_id)
            per_item.show()
            per_menu.append(per_item)
        
        if no_related:
            item.set_sensitive(0)
        item.show()
        menu.append(item)
        menu.popup(None, None, None, None, event.button, event.time)
        return 1

    def printview(self, obj):
        """
        Print or save the view that is currently shown
        """
        widthpx = 2*(self.fan.pixels_per_generation * self.fan.nrgen() 
                        + self.fan.center)
        prt = CairoPrintSave(widthpx, self.fan.on_draw, self.uistate.window)
        prt.run()

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
