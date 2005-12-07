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

    def __init__(self,stock_name,clicked=None):
        gtk.Button.__init__(self)
        image = gtk.Image()
        image.set_from_stock(stock_name,gtk.ICON_SIZE_BUTTON)
        self.add(image)
        if clicked:
            self.connect('clicked',clicked)

class Glabel(gtk.Label):

    def __init__(self,val):
        gtk.Label.__init__(self,'<b>%s</b>' % val)
        self.set_use_markup(True)
        self.set_use_underline(True)
        self.set_alignment(0,0.5)

class Slabel(gtk.Label):

    def __init__(self,val):
        gtk.Label.__init__(self, val)
        self.set_alignment(1.0,0.5)

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

        self.parents_box = gtk.ComboBox()
        self.spouse_box = gtk.ComboBox()
        self.person_name = gtk.Entry()
        self.person_birth = gtk.Entry()
        self.person_death = gtk.Entry()
        self.marriage_type = gtk.Entry()
        self.marriage_info = gtk.Entry()
        self.family_id = gtk.Entry()
        self.child_list = gtk.TreeView()
        self.child_model = DisplayModels.ChildModel([],self.dbstate.db)

        switch = Gbutton(gtk.STOCK_GO_BACK, self.switch_spouse)
        edit_active = Gbutton(gtk.STOCK_EDIT, self.edit_person)
        new_spouse = Gbutton(gtk.STOCK_NEW)
        spouse_select = Gbutton(gtk.STOCK_INDEX)
        rel_edit = Gbutton(gtk.STOCK_EDIT)
        parents_down = Gbutton(gtk.STOCK_GO_DOWN)
        child_up = Gbutton(gtk.STOCK_GO_UP)
        child_new = Gbutton(gtk.STOCK_NEW)
        child_sel = Gbutton(gtk.STOCK_INDEX)
        child_del = Gbutton(gtk.STOCK_REMOVE)

        table = gtk.Table(10,8)
        table.set_col_spacings(12)
        table.set_row_spacings(6)
        table.set_border_width(6)

        # Parents
        table.attach(Glabel(_("_Parents")), 0, 7, 0, 1, gtk.FILL,0,0,0)
        table.attach(self.parents_box, 1, 7, 1, 2, gtk.FILL, gtk.FILL, 0, 0)
        table.attach(parents_down, 7, 8, 1, 2, 0, 0, 0, 0)

        # Active Person
        table.attach(Glabel('_Active person'), 0, 3, 3, 4, gtk.FILL, 0, 0, 0)
        table.attach(self.person_name, 1, 3, 4, 5, gtk.EXPAND | gtk.FILL, 0, 0, 0)
        table.attach(Slabel(_("b.")),   1, 2, 5, 6, gtk.FILL, 0,0,0)
        table.attach(self.person_birth, 2, 3, 5, 6, gtk.EXPAND|gtk.FILL, 0, 0, 0)
        table.attach(Slabel(_("d.")),   1, 2, 6, 7, gtk.FILL, 0, 0, 0)
        table.attach(self.person_death, 2, 3, 6, 7, gtk.EXPAND | gtk.FILL, 0,0,0)
        table.attach(switch, 3, 4, 4, 5, gtk.FILL, 0,0,0)
        table.attach(edit_active, 3, 4, 5, 6, gtk.FILL, 0, 0, 0)

        # Spouse
        table.attach(Glabel(_("_Spouse/Partner")), 4, 7, 3, 4, gtk.FILL, 0,0,0)
        table.attach(self.spouse_box, 5, 7, 4, 5, gtk.FILL, gtk.FILL, 0, 0)
        vbox90 = gtk.VBox(True, 6)
        vbox90.pack_start(new_spouse, False, False, 0)
        vbox90.pack_start(spouse_select, False, False, 0)
        vbox90.pack_start(rel_edit, False, False, 0)
        table.attach(vbox90, 7, 8, 4, 7, gtk.FILL, gtk.FILL, 0, 0)
        table.attach(Slabel('Type:'), 5,6,5,6,gtk.FILL, 0,0,0)
        table.attach(self.marriage_type, 6, 7, 5, 6, gtk.EXPAND|gtk.FILL, 0, 0, 0)
        table.attach(self.marriage_info, 6, 7, 6, 7, gtk.EXPAND|gtk.FILL, 0, 0, 0)

        # Children

        table.attach(Glabel('_Children'), 0, 7, 8, 9, gtk.FILL, 0, 0, 0)
        vbox89 = gtk.VBox(False, 6)
        vbox89.pack_start(child_up,  False, False, 0)
        vbox89.pack_start(child_new, False, False, 0)
        vbox89.pack_start(child_sel, False, False, 0)
        vbox89.pack_start(child_del, False, False, 0)
        table.attach (vbox89, 7, 8, 9, 10, gtk.FILL, gtk.FILL, 0, 0);

        scrolledwindow83 = gtk.ScrolledWindow()
        scrolledwindow83.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolledwindow83.set_shadow_type(gtk.SHADOW_IN)
        scrolledwindow83.add(self.child_list)
        table.attach(scrolledwindow83, 1, 7, 9, 10, gtk.FILL, gtk.EXPAND|gtk.FILL, 0, 0)
                     
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

    def switch_spouse(self,obj):
        print "switch spouse"

    def edit_person(self,obj):
        print "edit person"
