#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import gc
import re

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gobject
import gtk

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import RelLib
import PageView
import DisplayTrace
import DisplayModels

class Gbutton(gtk.Button):

    def __init__(self,stock_name):
        gtk.Button.__init__(self)
        image = gtk.Image()
        image.set_from_stock(stock_name,gtk.ICON_SIZE_BUTTON)
        self.add(image)

class Glabel(gtk.Label):

    def __init__(self,val):
        gtk.Label.__init__(self,'<b>%s</b>' % val)
        self.set_use_markup(True)
        self.set_use_underline(True)
        self.set_alignment(0,0.5)

class Slabel(gtk.Label):

    def __init__(self,val):
        gtk.Label.__init__(self, val)
        self.set_alignment(0,0.5)

class FamilyView(PageView.PageView):

    def __init__(self,dbstate,uistate):
        PageView.PageView.__init__(self,'Pedigree View',dbstate,uistate)
        dbstate.connect('database-changed',self.change_db)

    def get_stock(self):
        """
        Returns the name of the stock icon to use for the display.
        This assumes that this icon has already been registered with
        GNOME as a stock icon.
        """
        return 'gramps-family'

    def build_widget(self):
        fill = gtk.EXPAND|gtk.FILL

        self.father_box = gtk.ComboBox()
        self.mother_box = gtk.ComboBox()
        self.spouse_box = gtk.ComboBox()
        self.person_name = gtk.Entry()
        self.person_birth = gtk.Entry()
        self.person_death = gtk.Entry()
        self.marriage_type = gtk.Entry()
        self.marriage_info = gtk.Entry()
        self.family_id = gtk.Entry()
        scrollwindow = gtk.ScrolledWindow()
        scrollwindow.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        scrollwindow.set_shadow_type(gtk.SHADOW_IN)
        self.child_list = gtk.TreeView()
        self.child_model = DisplayModels.ChildModel([],self.dbstate.db)
        scrollwindow.add(self.child_list)

        switch = Gbutton(gtk.STOCK_GO_BACK)
        edit_active = Gbutton(gtk.STOCK_EDIT)
        new_spouse = Gbutton(gtk.STOCK_NEW)
        spouse_select = Gbutton(gtk.STOCK_INDEX)
        rel_edit = Gbutton(gtk.STOCK_EDIT)
        parents_down = Gbutton(gtk.STOCK_GO_DOWN)

        table = gtk.Table(9,10)
        table.set_col_spacings(12)
        table.set_row_spacings(6)
        table.set_border_width(6)
        
        table.attach(Glabel(_('_Parents')),0,6,  0,1, fill, 0,0,0)
        table.attach(self.father_box,      1,9,  1,2, fill, 0,0,0)
        table.attach(parents_down,         9,10, 1,2, 0,0,0,0)
                     
        table.attach(Glabel(_('_Active person')), 0,5, 3,4, fill,0,0,0)
        table.attach(self.person_name,   1,5, 4,5, fill,0,0,0)
        table.attach(Slabel(_('b.')), 1,2, 5,6, 0,0,0,0)
        table.attach(Slabel(_('d.')), 1,2, 6,7, 0,0,0,0)
        table.attach(self.person_birth,  2,5, 5,6, fill,0,0,0)
        table.attach(self.person_death,  2,5, 6,7, fill,0,0,0)

        table.attach(switch, 5,6, 4,5, 0,0,0,0)
        table.attach(edit_active, 5,6, 5,6, 0,0,0,0)
        table.attach(new_spouse, 9,10, 4,5, 0,0,0,0)
        table.attach(spouse_select, 9,10, 5,6, 0,0,0,0)
        table.attach(rel_edit, 9,10, 6,7, 0,0,0,0)

        table.attach(Glabel(_('_Spouse/partner')), 6,9, 3,4, fill,0,0,0)
        table.attach(self.spouse_box, 7,9, 4,5, fill, 0,0,0)
        table.attach(Slabel(_('Type:')), 7,8, 5,6, gtk.FILL, 0,0,0)
        table.attach(self.marriage_type, 8,9, 5,6, fill, 0,0,0)
        table.attach(Slabel(_('Marriage:')), 7,8, 6,7, gtk.FILL,0,0,0)
        table.attach(self.marriage_info, 8,9, 6,7, fill, 0,0,0)
#        table.attach(Slabel(_('ID:')), 7,8, 7,8, gtk.FILL, 0,0,0)
#        table.attach(self.family_id, 8,9, 7,8, fill, 0,0,0)

        table.attach(Glabel(_('_Children')), 0,8, 8,9, fill, 0,0,0)
        table.attach(scrollwindow, 1,9, 9,10, fill, gtk.FILL, 0,0)

        bbox = gtk.VBox()
        bbox.set_spacing(6)
        child_up = Gbutton(gtk.STOCK_GO_UP)
        child_new = Gbutton(gtk.STOCK_NEW)
        child_sel = Gbutton(gtk.STOCK_INDEX)
        child_del = Gbutton(gtk.STOCK_REMOVE)
        bbox.add(child_up)
        bbox.add(child_new)
        bbox.add(child_sel)
        bbox.add(child_del)
        
        table.attach(bbox, 9,10, 9,10, 0, 0, 0, 0)
                     
        return table

    def navigation_type(self):
        return PageView.NAVIGATION_PERSON

    def define_actions(self):
        pass

    def ui_definition(self):
        """
        Specifies the UIManager XML code that defines the menus and buttons
        associated with the interface.
        """
        return '''<ui>
        </ui>'''

    def change_db(self,db):
        return
