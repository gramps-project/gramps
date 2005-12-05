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

class Glabel(gtk.Label):

    def __init__(self,val):
        gtk.Label.__init__(self,'<b>%s</b>' % val)
        self.set_use_markup(True)
        self.set_use_underline(True)
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
        scrollwindow = gtk.ScrolledWindow()
        scrollwindow.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        scrollwindow.set_shadow_type(gtk.SHADOW_IN)
        self.child_list = gtk.TreeView()
        self.child_model = DisplayModels.ChildModel([],self.dbstate.db)
        scrollwindow.add(self.child_list)

        table = gtk.Table(9,11)
        table.set_col_spacings(12)
        table.set_row_spacings(6)
        table.set_border_width(12)
        
        table.attach(Glabel(_('_Father')),0,3, 0,1, fill, 0,0,0)
        table.attach(self.father_box,     1,3, 1,2, fill, 0,0,0)

        table.attach(Glabel(_('_Mother')),5,9, 0,1, fill, 0,0,0)
        table.attach(self.mother_box,     6,9, 1,2, fill, 0,0,0)

        table.attach(Glabel(_('_Active person')), 0,3, 3,4, fill,0,0,0)
        table.attach(self.person_name,   1,3, 4,5, fill,0,0,0)
        table.attach(gtk.Label(_('b.')), 1,2, 5,6, 0,0,0,0)
        table.attach(gtk.Label(_('d.')), 1,2, 6,7, 0,0,0,0)
        table.attach(self.person_birth,  2,3, 5,6, fill,0,0,0)
        table.attach(self.person_death,  2,3, 6,7, fill,0,0,0)

        table.attach(Glabel(_('_Spouse/partner')), 5,9, 3,4, fill,0,0,0)
        table.attach(self.spouse_box, 6,9, 4,5, fill, 0,0,0)
        table.attach(gtk.Label(_('Type:')), 7,8, 5,6, 0, 0,0,0)
        table.attach(self.marriage_type, 8,9, 5,6, fill, 0,0,0)
        table.attach(self.marriage_info, 8,9, 5,6, fill, 0,0,0)

        table.attach(Glabel(_('_Children')), 0,8, 7,8, fill, 0,0,0)
        table.attach(scrollwindow, 1,9, 8,9, fill, fill, 0,0)
                     
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
