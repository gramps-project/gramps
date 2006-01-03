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
import pango

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
import RelLib
import PageView
import DisplayTrace
import NameDisplay

class FamilyView(PageView.PageView):

    def __init__(self,dbstate,uistate):
        PageView.PageView.__init__(self,'Pedigree View',dbstate,uistate)
        dbstate.connect('database-changed',self.change_db)
        dbstate.connect('active-changed',self.change_person)

    def get_stock(self):
        """
        Returns the name of the stock icon to use for the display.
        This assumes that this icon has already been registered with
        GNOME as a stock icon.
        """
        return 'gramps-family'

    def build_widget(self):
        self.vbox = gtk.VBox()
        self.vbox.show()
        self.child = None
        return self.vbox

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

    def get_name(self,handle):
        if handle:
            p = self.dbstate.db.get_person_from_handle(handle)
            return NameDisplay.displayer.display(p)
        else:
            return _(u"Unknown")

    def change_person(self,obj):
        if self.child:
            self.vbox.remove(self.child)
        self.child = gtk.Table(10,8)
        self.child.set_border_width(12)
        self.child.set_col_spacings(12)
        self.child.set_row_spacings(6)

        person = self.dbstate.db.get_person_from_handle(obj)
        self.write_title(person)

        family_handle_list = person.get_parent_family_handle_list()
        for (family_handle,mrel,frel) in family_handle_list:
            if family_handle:
                self.write_label(_('Parents'))
                self.write_parents(family_handle)

        family_handle_list = person.get_family_handle_list()
        for family_handle in family_handle_list:
            if family_handle:
                self.write_label(_('Family'))
                self.write_family(family_handle)
        
        self.child.show()
        self.vbox.pack_start(self.child,expand=False,fill=False)

    def make_button(self,handle,icon,func):
        image = gtk.Image()
        image.set_from_stock(icon,gtk.ICON_SIZE_MENU)
        image.show()
        button = gtk.Button()
        button.add(image)
        button.connect('clicked',func,handle)
        button.show()
        return button

    def make_edit_button(self,handle):
        return self.make_button(handle,gtk.STOCK_EDIT,self.edit_person)

    def make_goto_button(self,handle):
        return self.make_button(handle,gtk.STOCK_JUMP_TO,self.change_to)

    def write_title(self,person):
        label = gtk.Label('<span size="larger" weight="bold">%s</span>'
                          % NameDisplay.displayer.display(person))
        label.set_use_markup(True)
        label.set_alignment(0,0.5)
        label.show()
        self.child.attach(label,0,6,0,1)
        button = self.make_edit_button(person.handle)
        self.child.attach(button,7,8,0,1,xoptions=0)
        self.row = 1

    def write_label(self,title):
        label = gtk.Label('<span weight="bold">%s</span>' % title)
        label.set_use_markup(True)
        label.set_alignment(0,0.5)
        label.show()
        self.child.attach(label,1,6,self.row,self.row+1)
        self.row += 1

    def write_person(self,title,handle):
        if title:
            format = '<span weight="bold">%s: </span>'
        else:
            format = "%s"
        label = gtk.Label(format % title)
        label.set_use_markup(True)
        label.set_alignment(1.0,0.5)
        label.show()
        self.child.attach(label,2,3,self.row,self.row+1,xoptions=0)

        label = gtk.Label(self.get_name(handle))
        label.set_alignment(0,0.5)
        label.show()
        self.child.attach(label,3,4,self.row,self.row+1,
                          xoptions=gtk.EXPAND|gtk.FILL)
        button = self.make_edit_button(handle)
        self.child.attach(button,7,8,self.row,self.row+1,xoptions=0)
        button = self.make_goto_button(handle)
        self.child.attach(button,6,7,self.row,self.row+1,xoptions=0)
        self.row += 1
        
    def write_parents(self,family_handle):
        family = self.dbstate.db.get_family_from_handle(family_handle)
        self.write_person(_('Father'),family.get_father_handle())
        self.write_person(_('Mother'),family.get_mother_handle())

    def write_family(self,family_handle):
        family = self.dbstate.db.get_family_from_handle(family_handle)
        father_handle = family.get_father_handle()
        mother_handle = family.get_mother_handle()
        if self.dbstate.active.handle == father_handle:
            self.write_person(_('Spouse'),mother_handle)
        else:
            self.write_person(_('Spouse'),father_handle)
        child_list = family.get_child_handle_list()
        label = _("Children")
        if child_list:
            for child in child_list:
                self.write_person(label,child)
                label = u""

    def edit_person(self,obj,handle):
        import EditPerson
        person = self.dbstate.db.get_person_from_handle(handle)
        EditPerson.EditPerson(self.dbstate, self.uistate, [], person)

    def change_to(self,obj,handle):
        self.dbstate.change_active_handle(handle)

