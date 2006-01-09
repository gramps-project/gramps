#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _
import gc
import re
import cgi

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
import NameDisplay
import Utils
import DateHandler
import ImgManip
import ReportUtils
import GrampsKeys

_GenderCode = {
    RelLib.Person.MALE    : u'\u2642',
    RelLib.Person.FEMALE  : u'\u2640',
    RelLib.Person.UNKNOWN : u'\u2650',
    }


class AttachList:

    def __init__(self):
        self.list = []
        self.max_x = 0
        self.max_y = 0

    def attach(self,widget,x0,x1,y0,y1,xoptions=gtk.EXPAND|gtk.FILL,
               yoptions=gtk.EXPAND|gtk.FILL):
        self.list.append((widget,x0,x1,y0,y1,xoptions,yoptions))
        self.max_x = max(self.max_x,x1)
        self.max_y = max(self.max_y,y1)

class LinkLabel(gtk.EventBox):

    def __init__(self,label,func,handle):
        gtk.EventBox.__init__(self)
        self.orig_text = cgi.escape(label[0])
        self.gender = label[1]
        text = '<span underline="single">%s</span>' % self.orig_text
        if label[1]:
            text += u' %s' % label[1]
        
        self.label = gtk.Label(text)
        self.label.set_use_markup(True)
        self.label.set_alignment(0,0.5)

        self.add(self.label)
        self.set_visible_window(False)

        self.connect('button-press-event',func,handle)
        self.connect('enter-notify-event',self.enter_text,handle)
        self.connect('leave-notify-event',self.leave_text,handle)
        
    def enter_text(self,obj,event,handle):
        text = '<span foreground="blue" underline="single">%s</span>' % self.orig_text
        if self.gender:
            text += u" %s" % self.gender
        self.label.set_text(text)
        self.label.set_use_markup(True)

    def leave_text(self,obj,event,handle):
        text = '<span underline="single">%s</span>' % self.orig_text
        if self.gender:
            text += u" %s" % self.gender
        self.label.set_text(text)
        self.label.set_use_markup(True)
        
class IconButton(gtk.EventBox):

    def __init__(self,func,handle):
        gtk.EventBox.__init__(self)
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_EDIT,gtk.ICON_SIZE_MENU)
        image.show()
        self.add(image)
        self.show()
        self.connect('button-press-event',func,handle)
        
class LinkBox(gtk.HBox):

    def __init__(self,link,button):
        gtk.HBox.__init__(self)
        self.set_spacing(6)
        self.pack_start(link,False)
        self.pack_start(button,False)
        self.show()

class BasicLabel(gtk.Label):

    def __init__(self,text):
        gtk.Label.__init__(self,text)
        self.set_alignment(0,0.5)
        self.show()

class MarkupLabel(gtk.Label):

    def __init__(self,text):
        gtk.Label.__init__(self,text)
        self.set_alignment(0,0.5)
        self.set_use_markup(True)
        self.show()

class FamilyView(PageView.PersonNavView):

    def __init__(self,dbstate,uistate):
        PageView.PersonNavView.__init__(self,'Pedigree View',dbstate,uistate)
        dbstate.connect('database-changed',self.change_db)
        dbstate.connect('active-changed',self.change_person)
        self.show_siblings = GrampsKeys.get_family_siblings()
        if self.show_siblings == None:
            self.show_siblings = True
        self.show_details = GrampsKeys.get_family_details()
        if self.show_details == None:
            self.show_details = True

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

    def ui_definition(self):
        """
        Specifies the UIManager XML code that defines the menus and buttons
        associated with the interface.
        """
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
            <menu action="ViewMenu">
              <menuitem action="Siblings"/>
              <menuitem action="Details"/>
            </menu>
          </menubar>
          <toolbar name="ToolBar">
            <placeholder name="CommonNavigation">
              <toolitem action="Back"/>  
              <toolitem action="Forward"/>  
              <toolitem action="HomePerson"/>
            </placeholder>
          </toolbar>
          <popup name="Popup">
            <menuitem action="Back"/>
            <menuitem action="Forward"/>
            <menuitem action="HomePerson"/>
            <separator/>
          </popup>
        </ui>'''

    def define_actions(self):
        PageView.PersonNavView.define_actions(self)

        self.add_toggle_action('Details', None, _('Show details'),
                               None, None, self.details_toggle,
                               self.show_details)
        self.add_toggle_action('Siblings', None, _('Show siblings'),
                               None, None, self.siblings_toggle,
                               self.show_siblings)

    def siblings_toggle(self,obj):
        self.show_siblings = obj.get_active()
        self.change_person(self.dbstate.active.handle)
        GrampsKeys.save_family_siblings(self.show_siblings)

    def details_toggle(self,obj):
        self.show_details = obj.get_active()
        self.change_person(self.dbstate.active.handle)
        GrampsKeys.save_family_details(self.show_details)

    def change_db(self,db):
        if self.child:
            self.vbox.remove(self.child)
            self.child = None

    def get_name(self,handle,use_gender=False):
        if handle:
            p = self.dbstate.db.get_person_from_handle(handle)
            name = NameDisplay.displayer.display(p)
            if use_gender:
                gender = _GenderCode[p.gender]
            else:
                gender = ""
            return (name,gender)
        else:
            return (_(u"Unknown"),"")

    def change_person(self,obj):
        if self.child:
            self.vbox.remove(self.child)
        self.attach = AttachList()

        person = self.dbstate.db.get_person_from_handle(obj)
        if not person:
            return

        self.row = 5
        family_handle_list = person.get_parent_family_handle_list()
        for (family_handle,mrel,frel) in family_handle_list:
            if family_handle:
                self.write_parents(family_handle)
                
        family_handle_list = person.get_family_handle_list()
        for family_handle in family_handle_list:
            if family_handle:
                self.write_family(family_handle)

        self.row = 1
        self.write_title(person)

        # Here it is necessary to beat GTK into submission. For some
        # bizzare reason, if you have an empty column that is spanned,
        # you lose the appropriate FILL handling. So, we need to see if
        # column 3 is unused (usually if there is no siblings or children.
        # If so, we need to subtract one index of each x coord > 3.
                
        found = False
        for d in self.attach.list:
            if d[1] == 3 or d[2] == 3:
                found = True

        if found:
            cols = self.attach.max_x
        else:
            cols = self.attach.max_x-1

        self.child = gtk.Table(self.attach.max_y,cols)
        self.child.set_border_width(12)
        self.child.set_col_spacings(12)
        self.child.set_row_spacings(6)

        for d in self.attach.list:
            x0 = d[1]
            x1 = d[2]
            if not found:
                if x0 > 3:
                   x0 -= 1
                if x1 > 3:
                    x1 -= 1
            self.child.attach(d[0],x0,x1,d[3],d[4],d[5],d[6])

        self.child.show_all()
        self.vbox.pack_start(self.child,False)

    def write_title(self,person):

        # name and edit button
        name = NameDisplay.displayer.display(person)
        text = '<span size="larger" weight="bold">%s %s</span>' % (cgi.escape(name),
                                                                   _GenderCode[person.gender])
        label = MarkupLabel(text)
        button = IconButton(self.edit_button_press,person.handle)

        hbox = LinkBox(label,button)
                
        # GRAMPS ID
        self.row = 1

        self.write_person_data("%s:" % _('ID'),person.gramps_id)

        # birth/death events

        birth_ref = person.get_birth_ref()
        if birth_ref:
            birth = self.dbstate.db.get_event_from_handle(birth_ref.ref)
        else:
            birth = None
        self.write_person_event("%s:" % _('Birth'),birth)
        
        death_ref = person.get_death_ref()
        if death_ref:
            death = self.dbstate.db.get_event_from_handle(death_ref.ref)
        else:
            death = None
        self.write_person_event("%s:" % _('Death'),death)

        # separator
        end = self.attach.max_x
        sep = gtk.HSeparator()
        sep.show()
        self.attach.attach(hbox,0,end,0,1,gtk.FILL|gtk.EXPAND)

        # image
        image_list = person.get_media_list()
        if image_list:
            mobj = self.dbstate.db.get_object_from_handle(image_list[0].ref)
            if mobj.get_mime_type()[0:5] == "image":
                pixbuf = ImgManip.get_thumbnail_image(mobj.get_path())
                image = gtk.Image()
                image.set_from_pixbuf(pixbuf)
                image.show()
                self.attach.attach(image,end,end+1,0,4,xoptions=gtk.SHRINK|gtk.FILL)

        self.attach.attach(sep,0,self.attach.max_x,4,5)

    def write_person_event(self, ename, event):
        if event:
            dobj = event.get_date_object()
            phandle = event.get_place_handle()
            if phandle:
                pname = self.place_name(phandle)
            else:
                pname = None
            date_str = DateHandler.displayer.display(dobj)

            value = {
                'date' : DateHandler.displayer.display(dobj),
                'place' : pname,
                }
        else:
            pname = None
            dobj = None

        if dobj:
            if pname:
                self.write_person_data(ename,
                                       _('%(date)s in %(place)s') % value)
            else:
                self.write_person_data(ename,'%(date)s' % value)
        elif pname:
            self.write_person_data(ename,pname)
        else:
            self.write_person_data(ename,'')

    def write_person_data(self,title,data):
        self.attach.attach(BasicLabel(title),1,2,self.row,self.row+1,
                           xoptions=gtk.FILL|gtk.SHRINK)
        self.attach.attach(BasicLabel(data),2,4,self.row,self.row+1)
        self.row += 1

######################################################################

    def write_parents(self,family_handle):
        family = self.dbstate.db.get_family_from_handle(family_handle)
        self.write_person(_('Father'),family.get_father_handle())
        if self.show_details:
            value = self.info_string(family.get_father_handle())
            if value:
                self.attach.attach(BasicLabel(value),2,4,self.row, self.row+1)
                self.row += 1
        self.write_person(_('Mother'),family.get_mother_handle())
        if self.show_details:
            value = self.info_string(family.get_mother_handle())
            if value:
                self.attach.attach(BasicLabel(value),2,4,self.row, self.row+1)
                self.row += 1

        if self.show_siblings:
            active = self.dbstate.active.handle
        
            child_list = [handle for handle in family.get_child_handle_list()\
                          if handle != active]
            label = _("Siblings")
            if child_list:
                for child in child_list:
                    self.write_child(label,child)
                    label = u""

    def write_person(self,title,handle):
        if title:
            format = '<span weight="bold">%s: </span>'
        else:
            format = "%s"

        label = MarkupLabel(format % cgi.escape(title))
        self.attach.attach(label,1,2,self.row,self.row+1,
                           xoptions=gtk.FILL|gtk.SHRINK)

        link_label = LinkLabel(self.get_name(handle,True),self.button_press,handle)
        button = IconButton(self.edit_button_press,handle)
        self.attach.attach(LinkBox(link_label,button),2,4,self.row,self.row+1)
        self.row += 1

    def write_child(self,title,handle):
        if title:
            format = '<span weight="bold">%s: </span>'
        else:
            format = "%s"

        label = MarkupLabel(format % cgi.escape(title))
        self.attach.attach(label,2,3,self.row,self.row+1,
                           xoptions=gtk.FILL|gtk.SHRINK)

        link_label = LinkLabel(self.get_name(handle,True),self.button_press,handle)
        button = IconButton(self.edit_button_press,handle)
        self.attach.attach(LinkBox(link_label,button),3,4,self.row,self.row+1,
                          xoptions=gtk.EXPAND|gtk.FILL)

        self.row += 1

        if self.show_details:
            value = self.info_string(handle)
            if value:
                self.attach.attach(BasicLabel(value),3,4,self.row, self.row+1)
                self.row += 1
        
    def write_data(self,title,start_col=2,stop_col=4):
        self.attach.attach(BasicLabel(title),start_col,stop_col,self.row,
                          self.row+1, xoptions=gtk.EXPAND|gtk.FILL)
        self.row += 1

    def write_label(self,title):
        text = '<span style="oblique" weight="bold">%s</span>' % cgi.escape(title)
        label = MarkupLabel(text)
        self.attach.attach(label,1,4,self.row,self.row+1)
        self.row += 1

    def info_string(self,handle):
        child = self.dbstate.db.get_person_from_handle(handle)
        birth_ref = child.get_birth_ref()
        death_ref = child.get_death_ref()
        value = None
        if birth_ref or death_ref:
            info = ReportUtils.get_birth_death_strings(self.dbstate.db,child)
            bdate = info[0]
            ddate = info[4]
            if bdate and ddate:
                value = _("b. %s, d. %s") % (bdate,ddate)
            elif bdate:
                value = _("b. %s") % (bdate)
            elif ddate:
                value = _("d. %s") % (ddate)
        return value
        

    def button_press(self,obj,event,handle):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            self.dbstate.change_active_handle(handle)

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
                self.write_event_ref(_('Marriage'),event)

    def write_event_ref(self, ename, event,start_col=2,stop_col=4):
        if event:
            dobj = event.get_date_object()
            phandle = event.get_place_handle()
            if phandle:
                pname = self.place_name(phandle)
            else:
                pname = None
            date_str = DateHandler.displayer.display(dobj)

            value = {
                'date' : DateHandler.displayer.display(dobj),
                'place' : pname,
                'event_type' : ename,
                }
        else:
            pname = None
            dobj = None
            value = {
                'event_type' : ename,
                }

        if dobj:
            if pname:
                self.write_data(_('%(event_type)s: %(date)s in %(place)s') %
                                value,start_col,stop_col)
            else:
                self.write_data(_('%(event_type)s: %(date)s') % value,
                                start_col, stop_col)
        elif pname:
            self.write_data(_('%(event_type)s: %(place)s') % value,
                            start_col,stop_col)
        else:
            self.write_data(_('%(event_type)s:') % value,
                            start_col, stop_col)

    def write_family(self,family_handle):
        family = self.dbstate.db.get_family_from_handle(family_handle)
        father_handle = family.get_father_handle()
        mother_handle = family.get_mother_handle()
        if self.dbstate.active.handle == father_handle:
            handle = mother_handle
        else:
            handle = father_handle

        if handle:
            self.write_person(_('Spouse'),handle)

            value = self.info_string(handle)
            if value:
                self.attach.attach(BasicLabel(value),2,4,self.row, self.row+1)
                self.row += 1
            self.write_relationship(family)
            self.write_marriage(family)
        
        child_list = family.get_child_handle_list()
        label = _("Children")
        if child_list:
            for child in child_list:
                self.write_child(label,child)
                label = u""

    def edit_button_press(self, obj, event, handle):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            import EditPerson
            person = self.dbstate.db.get_person_from_handle(handle)
            EditPerson.EditPerson(self.dbstate, self.uistate, [], person)
        
    def edit_person(self,obj,handle):
        import EditPerson
        person = self.dbstate.db.get_person_from_handle(handle)
        EditPerson.EditPerson(self.dbstate, self.uistate, [], person)

    def change_to(self,obj,handle):
        self.dbstate.change_active_handle(handle)

