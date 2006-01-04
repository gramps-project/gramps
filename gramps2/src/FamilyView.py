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
import Utils
import DateHandler
import ImgManip

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
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.scroll.show()
        self.vbox = gtk.VBox()
        self.vbox.show()
        self.child = None
        self.scroll.add_with_viewport(self.vbox)
        return self.scroll

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
        self.child = gtk.Table(20,5)
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
        self.vbox.pack_start(self.child,False)

    def make_button(self,handle,icon,func):
        image = gtk.Image()
        image.set_from_stock(icon,gtk.ICON_SIZE_MENU)
        image.show()
        eventbox = gtk.EventBox()
        eventbox.add(image)
        eventbox.show()
        eventbox.connect('button-press-event',self.edit_button_press,handle)
        return eventbox

    def edit_button_press(self, obj, event, handle):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            import EditPerson
            person = self.dbstate.db.get_person_from_handle(handle)
            EditPerson.EditPerson(self.dbstate, self.uistate, [], person)
        
    def make_edit_button(self,handle):
        return self.make_button(handle,gtk.STOCK_EDIT,self.edit_person)

    def write_title(self,person):        
        label = gtk.Label('<span size="larger" weight="bold">%s</span>'
                          % NameDisplay.displayer.display(person))
        label.set_use_markup(True)
        label.set_alignment(0,0.5)
        label.show()
        button = self.make_edit_button(person.handle)

        hbox = gtk.HBox()
        hbox.set_spacing(6)
        hbox.show()
        hbox.pack_start(label,False)
        hbox.pack_start(button,False)

        image_list = person.get_media_list()
        if image_list:
            print image_list
            mobj = self.dbstate.db.get_object_from_handle(image_list[0].ref)
            if mobj.get_mime_type()[0:5] == "image":
                pixbuf = ImgManip.get_thumbnail_image(mobj.get_path())
                image = gtk.Image()
                image.set_from_pixbuf(pixbuf)
                image.show()
                self.child.attach(image,4,5,0,1)
        
        self.child.attach(hbox,0,4,0,1)
#        self.child.attach(button,4,5,0,1,xoptions=0)
        sep = gtk.HSeparator()
        sep.show()
        self.child.attach(sep,0,5,1,2)
        self.row = 2

    def write_data(self,title):
        label = gtk.Label(title)
        label.set_alignment(0,0.5)
        label.show()
        self.child.attach(label,3,5,self.row,self.row+1,
                          xoptions=gtk.EXPAND|gtk.FILL)
        self.row += 1

    def write_label(self,title):
        label = gtk.Label('<span style="oblique" weight="bold">%s</span>' % title)
        label.set_use_markup(True)
        label.set_alignment(0,0.5)
        label.show()
        self.child.attach(label,1,5,self.row,self.row+1)
        self.row += 1

    def write_person(self,title,handle):
        if title:
            format = '<span weight="bold">%s: </span>'
        else:
            format = "%s"

        label = gtk.Label(format % title)
        label.set_use_markup(True)
        label.set_alignment(0,0.5)
        label.show()
        self.child.attach(label,2,3,self.row,self.row+1,xoptions=gtk.FILL)

        label = gtk.Label('<span underline="single">%s</span>' %
                          self.get_name(handle))
        label.set_use_markup(True)
        label.set_alignment(0,0.5)
        label.show()
        eventbox = gtk.EventBox()
        eventbox.add(label)
        eventbox.set_visible_window(False)
        eventbox.connect('button-press-event',self.button_press,handle)
        eventbox.connect('enter-notify-event',self.enter_text,handle)
        eventbox.connect('leave-notify-event',self.leave_text,handle)
        eventbox.show()

        button = self.make_edit_button(handle)

        box = gtk.HBox()
        box.set_spacing(6)
        box.pack_start(eventbox,False)
        box.pack_start(button,False)
        box.show()
        self.child.attach(box,3,4,self.row,self.row+1,
                          xoptions=gtk.EXPAND|gtk.FILL)
        self.row += 1

    def button_press(self,obj,event,handle):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            self.dbstate.change_active_handle(handle)

    def enter_text(self,obj,event,handle):
        label = obj.child
        label.set_text('<span foreground="blue" underline="single">%s</span>' %
                     self.get_name(handle))
        label.set_use_markup(True)

    def leave_text(self,obj,event,handle):
        label = obj.child
        label.set_text('<span underline="single">%s</span>' %
                       self.get_name(handle))
        label.set_use_markup(True)

    def make_enter_notify(self,handle):
        return lambda x: self.enter_text(x,handle)
    
    def write_parents(self,family_handle):
        family = self.dbstate.db.get_family_from_handle(family_handle)
        self.write_person(_('Father'),family.get_father_handle())
        self.write_person(_('Mother'),family.get_mother_handle())

    def write_relationship(self,family):
        rtype = family.get_relationship()
        if type(rtype) == tuple:
            if rtype[0] == RelLib.Family.CUSTOM:
                rel_text = rtype[1]
            else:
                rel_text = Utils.family_relations[rtype[0]]
        else:
            rel_text = Utils.family_relations[rtype]
        self.write_data(_('Relationship type: %s') % rel_text)

    def place_name(self,handle):
        p = self.dbstate.db.get_place_from_handle(handle)
        return p.get_title()

    def write_marriage(self,family):
        for event_ref in family.get_event_ref_list():
            handle = event_ref.ref
            event = self.dbstate.db.get_event_from_handle(handle)
            etype = event.get_type()
            if etype[0] == RelLib.Event.MARRIAGE:
                dobj = event.get_date_object()
                phandle = event.get_place_handle()
                if phandle:
                    pname = self.place_name(phandle)
                else:
                    phandle = None
                value = {
                    'date' : DateHandler.displayer.display(dobj),
                    'place' : pname,
                    }

                if phandle:
                    self.write_data(_('Married: %(date)s in %(place)s') % value)
                else:
                    self.write_data(_('Married: %(date)s') % value)

    def write_family(self,family_handle):
        family = self.dbstate.db.get_family_from_handle(family_handle)
        father_handle = family.get_father_handle()
        mother_handle = family.get_mother_handle()
        if self.dbstate.active.handle == father_handle:
            self.write_person(_('Spouse'),mother_handle)
        else:
            self.write_person(_('Spouse'),father_handle)

        self.write_relationship(family)
        self.write_marriage(family)
        
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

