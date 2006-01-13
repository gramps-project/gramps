import gtk
import DateHandler
import NameDisplay
import RelLib
import Utils
import ToolTips
import GrampsLocale

_GENDER = [ _(u'female'), _(u'male'), _(u'unknown') ]

#-------------------------------------------------------------------------
#
# Localized constants
#
#-------------------------------------------------------------------------
_codeset = GrampsLocale.codeset

def sfunc(a,b):
    return locale.strcoll(a[0],b[0])

class EmbeddedList(gtk.HBox):

    _HANDLE_COL = 8
    
    def __init__(self, db, build_model):
        gtk.HBox.__init__(self)
        self.build_model = build_model
        
        self.tree = gtk.TreeView()
        self.tree.set_rules_hint(True)
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        scroll.add_with_viewport(self.tree)
        self.pack_start(scroll,True)
        self.columns = []
        self.db = db
        self.build_columns()
        self.rebuild()
        self.show_all()

    def set_label(self):
        return

    def get_data(self):
        return []

    def column_order(self):
        return []

    def build_columns(self):
        for column in self.columns:
            self.tree.remove_column(column)
        self.columns = []

        #for pair in self.parent.db.get_child_column_order():

        for pair in self.column_order():
            if not pair[0]:
                continue
            name = self.column_names[pair[1]][0]
            column = gtk.TreeViewColumn(name, gtk.CellRendererText(),
                                        text=pair[1])
            column.set_resizable(True)
            column.set_min_width(40)
            column.set_sort_column_id(self.column_names[pair[1]][1])
            self.columns.append(column)
            self.tree.append_column(column)

    def rebuild(self):
        self.model = self.build_model(self.get_data(),self.db)
        self.tree.set_model(self.model)
        self.set_label()

    def get_tab_widget(self):
        return gtk.Label('UNDEFINED')


#-------------------------------------------------------------------------
#
# ChildModel
#
#-------------------------------------------------------------------------
class ChildModel(gtk.ListStore):

    def __init__(self,child_list,db):
        gtk.ListStore.__init__(self,int,str,str,str,str,str,str,str,str,str,int,int)
        self.db = db
        index = 1
        for child_handle in child_list:
            child = db.get_person_from_handle(child_handle)
            self.append(row=[index,
                             child.get_gramps_id(),
                             NameDisplay.displayer.display(child),
                             _GENDER[child.get_gender()],
                             self.column_birth_day(child),
                             self.column_death_day(child),
                             self.column_birth_place(child),
                             self.column_death_place(child),
                             child.get_handle(),
                             child.get_primary_name().get_sort_name(),
                             self.column_birth_sort(child),
                             self.column_death_sort(child),
                             ])
            index += 1

    def column_birth_day(self,data):
        event_ref = data.get_birth_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            return DateHandler.get_date(event)
        else:
            return u""

    def column_birth_sort(self,data):
        event_ref = data.get_birth_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            return event.get_date_object().get_sort_value()
        else:
            return 0

    def column_death_day(self,data):
        event_ref = data.get_death_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            return DateHandler.get_date(event)
        else:
            return u""

    def column_death_sort(self,data):
        event_ref = data.get_death_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            return event.get_date_object().get_sort_value()
        else:
            return 0
        
    def column_birth_place(self,data):
        event_ref = data.get_birth_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            if event:
                place_handle = event.get_place_handle()
                if place_handle:
                    return self.db.get_place_from_handle(place_handle).get_title()
        return u""

    def column_death_place(self,data):
        event_ref = data.get_death_ref()
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            if event:
                place_handle = event.get_place_handle()
                if place_handle:
                    return self.db.get_place_from_handle(place_handle).get_title()
        return u""

def type_name(event):
    t = event.get_type()
    if t[0] == RelLib.Event.CUSTOM:
        return t[1]
    else:
        return Utils.family_events[t[0]]

def place_of(event):
    t = event.get_place_handle()
    return t

#-------------------------------------------------------------------------
#
# EventRefModel
#
#-------------------------------------------------------------------------

class EventRefModel(gtk.ListStore):

    def __init__(self,event_list,db):
        gtk.ListStore.__init__(self,str,str,str,str,str,str)
        self.db = db
        index = 1
        for event_ref in event_list:
            event = db.get_event_from_handle(event_ref.ref)
            self.append(row=[
                event.get_description(),
                event.get_gramps_id(),
                type_name(event),
                self.column_date(event_ref),
                self.column_place(event_ref),
                event.get_cause(),
                ])
            index += 1

    def column_date(self,event_ref):
        event = self.db.get_event_from_handle(event_ref.ref)
        return DateHandler.get_date(event)

    def column_place(self,event_ref):
        if event_ref and event_ref.ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            if event:
                place_handle = event.get_place_handle()
                if place_handle:
                    return self.db.get_place_from_handle(place_handle).get_title()
        return u""

