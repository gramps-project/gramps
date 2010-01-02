# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009         Douglas S. Blank <doug.blank@gmail.com>
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
#

""" Django/Gramps utilities """

#------------------------------------------------------------------------
#
# Python Modules
#
#------------------------------------------------------------------------
import locale
import sys

#------------------------------------------------------------------------
#
# Django Modules
#
#------------------------------------------------------------------------
from django.template import escape
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType

#------------------------------------------------------------------------
#
# Gramps-Connect Modules
#
#------------------------------------------------------------------------
import web.grampsdb.models as models
import web.grampsdb.forms as forms
from web import libdjango
from web.djangodb import DjangoDb

#------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------
from Simple import SimpleTable, SimpleAccess, make_basic_stylesheet
import Utils
import DbState
import DateHandler
from gen.lib.date import Date as GDate, Today
import gen.lib
from gen.utils import get_birth_or_fallback, get_death_or_fallback
from gen.plug import BasePluginManager
from cli.grampscli import CLIManager

_ = lambda msg: msg

util_filters = [
    'nbsp', 
    'render_date',
    'render_name',
    ]

util_tags = [
    'render',
    "get_person_from_handle", 
    "event_table",
    "name_table",
    "source_table",
    "note_table",
    "attribute_table",
    "address_table",
    "gallery_table",
    "internet_table",
    "association_table",
    "lds_table",
    "reference_table",
    "children_table",
    "make_button",
    ]

#------------------------------------------------------------------------
#
# Module Constants
#
#------------------------------------------------------------------------
dji = libdjango.DjangoInterface()
_dd = DateHandler.displayer.display
_dp = DateHandler.parser.parse

def register_plugins():
    dbstate = DbState.DbState()
    climanager = CLIManager(dbstate, False) # don't load db
    climanager.do_reg_plugins()
    pmgr = BasePluginManager.get_instance()
    return pmgr

def get_person_from_handle(db, handle):
    # db is a Gramps Db interface
    # handle is a Person Handle
    try:
        return db.get_person_from_handle(handle)
    except:
        print >> sys.stderr, "error in get_person_from_handle:"
        import sys, traceback
        cla, exc, trbk = sys.exc_info()
        print  >> sys.stderr, _("Error") + (" : %s %s" %(cla, exc))
        traceback.print_exc()
        return None

def probably_alive(handle):
    return False
    db = DjangoDb()
    person = db.get_person_from_handle(handle)
    return Utils.probably_alive(person, db)

def format_number(number, with_grouping=True):
    # FIXME: should be user's setting
    locale.setlocale(locale.LC_ALL, "en_US.utf8")
    return locale.format("%d", number, with_grouping)

def nbsp(string):
    """
    """
    if string:
        return string
    else:
        return mark_safe("&nbsp;")

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
        self.doc =  Doc(HtmlDoc.HtmlDoc(make_basic_stylesheet(Table={"set_width":95}), None))
        self.doc.doc._backend = HtmlBackend()
        # You can set elements id, class, etc:
        self.doc.doc.htmllist += [Html('div', style="overflow: auto; height:150px; background-color: white;")]

    def columns(self, *args):
        self.table.columns(*args)

    def row(self, *args):
        self.table.row(*[nbsp(arg) for arg in args])

    def link(self, object_type_name, handle):
        self.table.set_link_col((object_type_name, handle))

    def links(self, links):
        """
        A list of (object_type_name, handle) pairs, one per row.
        """
        self.table.set_link_col(links)

    def get_html(self):
        # The HTML writer escapes data:
        self.table.write(self.doc) # forces to htmllist
        # We have a couple of HTML bits that we want to unescape:
        return str(self.doc.doc.htmllist[0]).replace("&amp;nbsp;", "&nbsp;")

_ = lambda text: text

def make_button(text, url, *args):
    url = url % args
    return """[ <a href="%s">%s</a> ] """ % (url, text)

def event_table(obj, user, action, url=None, *args):
    retval = ""
    table = Table()
    table.columns(_("Description"), 
                  _("Type"),
                  _("ID"),
                  _("Date"),
                  _("Place"),
                  _("Role"))
    if user.is_authenticated():
        obj_type = ContentType.objects.get_for_model(obj)
        event_ref_list = models.EventRef.objects.filter(
            object_id=obj.id, 
            object_type=obj_type).order_by("order")
        event_list = [(obj.ref_object, obj) for obj in event_ref_list]
        for (djevent, event_ref) in event_list:
            table.row(
                djevent.description,
                table.db.get_event_from_handle(djevent.handle),
                djevent.gramps_id, 
                display_date(djevent),
                get_title(djevent.place),
                str(event_ref.role_type))
    retval += table.get_html()
    if user.is_authenticated() and url and action == "view":
        retval += make_button(_("Add event"), (url + "/add") % args)
    else:
        retval += nbsp("") # to keep tabs same height
    return retval

def name_table(obj, user, action, url=None, *args):
    retval = ""
    table = Table()
    table.columns(_("Name"), 
                  _("Type"),
                  _("Group As"),
                  _("Source"),
                  _("Note Preview"))
    if user.is_authenticated():
        links = []
        for name in obj.name_set.all().order_by("order"):
            obj_type = ContentType.objects.get_for_model(name)
            sourceq = dji.SourceRef.filter(object_type=obj_type,
                                           object_id=name.id).count() > 0
            note_refs = dji.NoteRef.filter(object_type=obj_type,
                                           object_id=name.id)
            note = ""
            if note_refs.count() > 0:
                try:
                    note = dji.Note.get(id=note_refs[0].object_id).text[:50]
                except:
                    note = None
            table.row(make_name(name, user),
                      str(name.name_type) + ["", " (preferred)"][int(name.preferred)],
                      name.group_as,
                      ["No", "Yes"][sourceq],
                      note)
            links.append(('URL', 
                          # url is "/person/%s/name"
                          (url % name.person.handle) + ("/%s" % name.order)))
        table.links(links)
    retval += table.get_html()
    if user.is_authenticated() and url and action == "view":
        retval += make_button(_("Add name"), (url + "/add") % args)
    else:
        retval += nbsp("") # to keep tabs same height
    return retval

def source_table(obj, user, action, url=None, *args):
    retval = ""
    table = Table()
    table.columns(_("ID"), 
                  _("Title"),
                  _("Author"),
                  _("Page"))
    if user.is_authenticated():
        obj_type = ContentType.objects.get_for_model(obj)
        source_refs = dji.SourceRef.filter(object_type=obj_type,
                                           object_id=obj.id)
        for source_ref in source_refs:
            source = table.db.get_source_from_handle(source_ref.ref_object.handle)
            table.row(source,
                      source_ref.ref_object.title,
                      source_ref.ref_object.author,
                      source_ref.page,
                      )
    retval += table.get_html()
    if user.is_authenticated() and url and action == "view":
        retval += make_button(_("Add source"), (url + "/add") % args)
    else:
        retval += nbsp("") # to keep tabs same height
    return retval

def note_table(obj, user, action, url=None, *args):
    retval = ""
    table = Table()
    table.columns(
        _("ID"),
        _("Type"),
        _("Note"))
    if user.is_authenticated():
        obj_type = ContentType.objects.get_for_model(obj)
        note_refs = dji.NoteRef.filter(object_type=obj_type,
                                       object_id=obj.id)
        for note_ref in note_refs:
            note = table.db.get_note_from_handle(
                note_ref.ref_object.handle)
            table.row(table.db.get_note_from_handle(note.handle),
                      str(note_ref.ref_object.note_type),
                      note_ref.ref_object.text[:50])
    retval += table.get_html()
    if user.is_authenticated() and url and action == "view":
        retval += make_button(_("Add note"), (url + "/add") % args)
    else:
        retval += nbsp("") # to keep tabs same height
    return retval

def attribute_table(obj, user, action, url=None, *args):
    retval = ""
    table = Table()
    table.columns(_("Type"), 
                  _("Value"),
                  )
    if user.is_authenticated():
        obj_type = ContentType.objects.get_for_model(obj)
        attributes = dji.Attribute.filter(object_type=obj_type,
                                          object_id=obj.id)
        for attribute in attributes:
            table.row(attribute.attribute_type.name,
                      attribute.value)
    retval += table.get_html()
    if user.is_authenticated() and url and action == "view":
        retval += make_button(_("Add attribute"), (url + "/add") % args)
    else:
        retval += nbsp("") # to keep tabs same height
    return retval

def address_table(obj, user, action, url=None, *args):
    retval = ""
    table = Table()
    table.columns(_("Date"), 
                  _("Address"),
                  _("City"),
                  _("State"),
                  _("Country"))
    if user.is_authenticated():
        for address in obj.address_set.all().order_by("order"):
            locations = address.location_set.all().order_by("order")
            for location in locations:
                table.row(display_date(address),
                          location.street,
                          location.city,
                          location.state,
                          location.country)
    retval += table.get_html()
    if user.is_authenticated() and url and action == "view":
        retval += make_button(_("Add address"), (url + "/add") % args)
    else:
        retval += nbsp("") # to keep tabs same height
    return retval

def gallery_table(obj, user, action, url=None, *args):
    retval = ""
    table = Table()
    table.columns(_("Name"), 
                  _("Type"),
                  )
    retval += table.get_html()
    if user.is_authenticated() and url and action == "view":
        retval += make_button(_("Add gallery"), (url + "/add") % args)
    else:
        retval += nbsp("") # to keep tabs same height
    return retval

def internet_table(obj, user, action, url=None, *args):
    retval = ""
    table = Table()
    table.columns(_("Type"),
                  _("Path"),
                  _("Description"))
    if user.is_authenticated():
        urls = dji.Url.filter(person=obj)
        for url_obj in urls:
            table.row(str(url_obj.url_type),
                      url_obj.path,
                      url_obj.desc)
    retval += table.get_html()
    if user.is_authenticated() and url and action == "view":
        retval += make_button(_("Add internet"), ((str(url) % args) + "/add"))
    else:
        retval += nbsp("") # to keep tabs same height
    return retval

def association_table(obj, user, action, url=None, *args):
    retval = ""
    table = Table()
    table.columns(_("Name"), 
                  _("ID"),
                  _("Association"))
    if user.is_authenticated():
        gperson = table.db.get_person_from_handle(obj.handle)
        if gperson:
            associations = gperson.get_person_ref_list()
            for association in associations:
                table.row()
    retval += table.get_html()
    if user.is_authenticated() and url and action == "view":
        retval += make_button(_("Add association"), (url + "/add") % args)
    else:
        retval += nbsp("") # to keep tabs same height
    return retval

def lds_table(obj, user, action, url=None, *args):
    retval = ""
    table = Table()
    table.columns(_("Type"), 
                  _("Date"),
                  _("Status"),
                  _("Temple"),
                  _("Place"))
    if user.is_authenticated():
        obj_type = ContentType.objects.get_for_model(obj)
        ldss = obj.lds_set.all().order_by("order")
        for lds in ldss:
            table.row(str(lds.lds_type),
                      display_date(lds),
                      str(lds.status),
                      lds.temple,
                      get_title(lds.place))
    retval += table.get_html()
    if user.is_authenticated() and url and action == "view":
        retval += make_button(_("Add LDS"), (url + "/add") % args)
    else:
        retval += nbsp("") # to keep tabs same height
    return retval

def reference_table(obj, user, action, url=None, *args):
    retval = ""
    table = Table()
    table.columns(_("Type"), 
                  _("ID"),
                  _("Name"))
    if user.is_authenticated():
        references = dji.PersonRef.filter(ref_object=obj)
        for reference in references:
            table.row(str(reference.ref_object),
                      reference.ref_object.gramps_id,
                      make_name(reference.ref_object.name_set, user))
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    return retval 

def children_table(obj, user, action, url=None, *args):
    retval = ""
    table = Table()
    table.columns(
        _("#"),
        _("ID"),
        _("Name"),
        _("Gender"),
        _("Paternal"),
        _("Maternal"),
        _("Birth Date"),
        )

    family = obj
    obj_type = ContentType.objects.get_for_model(family)
    childrefs = dji.ChildRef.filter(object_id=family.id,
                                    object_type=obj_type).order_by("order")
    links = []
    count = 1
    for childref in childrefs:
        child = childref.ref_object
        if user.is_authenticated():
            table.row(str(count), 
                      "[%s]" % child.gramps_id,
                      render_name(child, user),
                      child.gender_type,
                      childref.father_rel_type,
                      childref.mother_rel_type,
                      render_date(child.birth, user),
                      )
            links.append(('URL', ("/person/%s" % child.handle)))
        else:
            table.row(str(count), 
                      "[%s]" % child.gramps_id,
                      render_name(child, user),
                      child.gender_type,
                      "[Private]",
                      "[Private]",
                      "[Private]",
                      )
            links.append(('URL', ("/person/%s" % child.handle)))
        count += 1
    table.links(links)
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    return retval

## FIXME: these dji function wrappers just use the functions
## written for the import/export. Can be done much more directly.

def get_title(place):
    if place:
        return place.title
    else:
        return ""

def person_get_birth_date(person):
    #db = DjangoDb()
    #event = get_birth_or_fallback(db, db.get_person_from_handle(person.handle))
    #if event:
    #    return event.date
    return None

def person_get_death_date(person):
    #db = DjangoDb()
    #event = get_death_or_fallback(db, db.get_person_from_handle(person.handle))
    #if event:
    #    return event.date
    return None

def display_date(obj):
    date_tuple = dji.get_date(obj)
    if date_tuple:
        gdate = GDate()
        gdate.unserialize(date_tuple)
        return _dd(gdate)
    else:
        return ""

def render(formfield, user, action, test=False, truetext=""):
    if not user.is_authenticated():
        action = "view"
    if action == "view":
        if (not user.is_authenticated() and not test) or user.is_authenticated():
            fieldname = formfield.name # 'surname'
            retval = str(getattr(formfield.form.model, fieldname))
        else:
            retval = truetext
    else:
        retval = formfield.as_widget()
    return retval

def render_name(name, user):
    """
    Given a Django or Gramps object, render the name and return.  This
    function uses authentication, privacy and probably_alive settings.
    """
    if isinstance(name, models.Name):
        if not user.is_authenticated():
            name.sanitize()
        return "%s, %s" % (name.surname, name.first_name)
    elif isinstance(name, forms.NameForm):
        if not user.is_authenticated():
            name.model.sanitize()
        return "%s, %s" % (name.model.surname, name.model.first_name)
    elif isinstance(name, gen.lib.Person): # name is a gen.lib.Person
        person = name
        try:
            name = person.get_primary_name()
        except:
            name = None
        if name is None:
            return "[No preferred name]"
        if not user.is_authenticated():
            name.sanitize()
        return "%s, %s" % (name.surname, name.first_name)
    elif isinstance(name, models.Person): # django person
        person = name
        try:
            name = person.name_set.get(preferred=True)
        except:
            return "Error"
        return render_name(name, user)
    else: # no name object
        return "[No preferred name]"

def make_name(name, user):
    return render_name(name, user)

def render_date(obj, user):
    """
    Given a Django object, render the date as text and return.  This
    function uses authentication settings.
    """
    if (user.is_authenticated() or 
        (not user.is_authenticated() and obj and not obj.private)):
        if obj:
            date_tuple = dji.get_date(obj)
            if date_tuple:
                gdate = GDate().unserialize(date_tuple)
                return _dd(gdate)
        return ""
    return "[Private]"

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

class lazy(object):
    EMPTY = []
    used = 0
    total = 0
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = lazy.EMPTY
        lazy.used = lazy.used + 1
        lazy.total = lazy.total + 1
        #print "freeze:", func, args

    def thaw(self):
        self.result = object.__getattribute__(self, "func")(*object.__getattribute__(self, "args"), 
                                                             **object.__getattribute__(self, "kwargs"))
        #print "thaw:", object.__getattribute__(self, "func"), object.__getattribute__(self, "result") 
        lazy.used = lazy.used - 1

    def __getattribute__(self, attr):
        if object.__getattribute__(self, "result") is lazy.EMPTY:
            object.__getattribute__(self, "thaw")()
        return getattr(object.__getattribute__(self, "result"), attr)

    def myclass(self):
        if object.__getattribute__(self, "result") is lazy.EMPTY:
            object.__getattribute__(self, "thaw")()
        return object.__getattribute__(self, "result").__class__

    #__class__ = property(myclass)

    def __str__(self):
        if object.__getattribute__(self, "result") is lazy.EMPTY:
            object.__getattribute__(self, "thaw")()
        return str(object.__getattribute__(self, "result"))

    def __int__(self):
        if object.__getattribute__(self, "result") is lazy.EMPTY:
            object.__getattribute__(self, "thaw")()
        return int(object.__getattribute__(self, "result"))

    def __float__(self):
        if object.__getattribute__(self, "result") is lazy.EMPTY:
            object.__getattribute__(self, "thaw")()
        return float(object.__getattribute__(self, "result"))

    def __repr__(self):
        if object.__getattribute__(self, "result") is lazy.EMPTY:
            object.__getattribute__(self, "thaw")()
        return repr(object.__getattribute__(self, "result"))

    def __getitem__(self, pos):
        if object.__getattribute__(self, "result") is lazy.EMPTY:
            object.__getattribute__(self, "thaw")()
        return object.__getattribute__(self, "result")[pos]

    def __len__(self):
        if object.__getattribute__(self, "result") is lazy.EMPTY:
            object.__getattribute__(self, "thaw")()
        return len(object.__getattribute__(self, "result"))

def freeze(item):
    return lazy(lambda i: i, item)


register_plugins()

# works after registering plugins:
import HtmlDoc 
from libhtmlbackend import HtmlBackend
from libhtml import Html
