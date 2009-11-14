import web.grampsdb.models as models
from web import libdjango
from web.djangodb import DjangoDb
from Simple import SimpleTable, SimpleAccess, make_basic_stylesheet
import Utils
import DbState
import DateHandler
from gen.lib.date import Date as GDate, Today
from gen.plug import BasePluginManager
from cli.grampscli import CLIManager
from django.template import escape
from django.contrib.contenttypes.models import ContentType

dji = libdjango.DjangoInterface()

_dd = DateHandler.displayer.display
_dp = DateHandler.parser.parse

def register_plugins():
    dbstate = DbState.DbState()
    climanager = CLIManager(dbstate, False) # don't load db
    climanager.do_reg_plugins()
    pmgr = BasePluginManager.get_instance()
    return pmgr

def probably_alive(handle):
    db = DjangoDb()
    return Utils.probably_alive(db.get_person_from_handle(handle), db)

class Table(object):
    """
    >>> table = Table()
    >>> table.columns("Col1", "Col2", "Col3")
    >>> table.row("1", "2", "3")
    >>> table.row("4", "5", "6")
    >>> table.get_html()
    """
    def __init__(self):
        self.db = DjangoDb()
        self.access = SimpleAccess(self.db)
        self.table = SimpleTable(self.access)
        class Doc(object):
            def __init__(self, doc):
                self.doc = doc
        # None is paperstyle, which is ignored:
        self.doc =  Doc(HtmlDoc.HtmlDoc(make_basic_stylesheet(), None))
        self.doc.doc._backend = HtmlBackend()
        # You can set elements id, class, etc:
        # self.doc.doc.htmllist += [Html('div', id="grampstextdoc")]
        self.doc.doc.htmllist += [Html('div')]

    def columns(self, *args):
        self.table.columns(*args)

    def row(self, *args):
        self.table.row(*args)

    def get_html(self):
        self.table.write(self.doc) # forces to htmllist
        return str(self.doc.doc.htmllist[0])

_ = lambda text: text

def events_table(djperson):
    table = Table()
    table.columns(_("Description"), 
                  _("Type"),
                  _("ID"),
                  _("Date"),
                  _("Place"),
                  _("Role"))
    obj_type = ContentType.objects.get_for_model(djperson)
    event_ref_list = models.EventRef.objects.filter(
        object_id=djperson.id, 
        object_type=obj_type).order_by("order")
    event_list = [(obj.ref_object, obj) for obj in event_ref_list]
    for (djevent, event_ref) in event_list:
        print djevent.description
        table.row(
            djevent.description,
            str(djevent.event_type),
            djevent.gramps_id, 
            display_date(djevent),
            get_title(djevent.place),
            str(event_ref.role_type))
    return table.get_html()

## FIXME: these dji function wrappers just use the functions
## written for the import/export. Can be done much more directly.

def get_title(place):
    if place:
        return place.title
    else:
        return ""

def person_get_birth_date(person):
    return person_get_event(person, models.EventType.BIRTH)

def person_get_death_date(person):
    return person_get_event(person, models.EventType.DEATH)

def display_date(obj):
    date_tuple = dji.get_date(obj)
    if date_tuple:
        gdate = GDate()
        gdate.unserialize(date_tuple)
        return escape(_dd(gdate))
    else:
        return ""

def person_get_event(person, event_type=None):
    event_ref_list = dji.get_event_ref_list(person)
    if event_type:
        index = libdjango.lookup_role_index(event_type, event_ref_list)
        if index >= 0:
            event_handle = event_ref_list[index][3]
            # (False, [], [], u'b2cfa6cdec87392cf3b', (1, u'Primary'))
            # WARNING: the same object can be referred to more than once
            objs = models.EventRef.objects.filter(ref_object__handle=event_handle)
            if objs.count() > 0:
                return display_date(objs[0].ref_object)
            else:
                return ""
        else:
            return ""
    else:
        retval = [[obj.ref_object for obj in 
                   models.EventRef.objects.filter(ref_object__handle=event_handle[3])] 
                  for event_handle in event_ref_list]
        return [j for i in retval for j in i]

def make_name(name, user):
    if isinstance(name, models.Name):
        surname = name.surname.strip()
        if not surname:
            surname = "[Missing]"
        if user.is_authenticated():
            return escape("%s, %s" % (surname, name.first_name))
        else:
            if probably_alive(name.person.handle):
                return escape("%s, %s" % (surname, "[Living]"))
            else:
                return escape("%s, %s" % (surname, name.first_name))
    elif name:
        name = name.get(preferred=True)
        if name:
            return make_name(name, user)
        else:
            return ""
    else:
        return ""

register_plugins()

# works after registering plugins:
import HtmlDoc 
from libhtmlbackend import HtmlBackend
from libhtml import Html
