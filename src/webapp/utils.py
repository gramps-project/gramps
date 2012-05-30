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
import re
import datetime
from HTMLParser import HTMLParser

#------------------------------------------------------------------------
#
# Django Modules
#
#------------------------------------------------------------------------
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

#------------------------------------------------------------------------
#
# Gramps-Connect Modules
#
#------------------------------------------------------------------------
import webapp.grampsdb.models as models
import webapp.grampsdb.forms as forms
from webapp import libdjango
from webapp.dbdjango import DbDjango

#------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------
from Simple import SimpleTable, SimpleAccess, make_basic_stylesheet
import Utils
import DbState
from gen.datehandler import displayer, parser
from gen.lib.date import Date as GDate, Today
import gen.lib
from gen.utils import get_birth_or_fallback, get_death_or_fallback
from gen.plug import BasePluginManager
from cli.grampscli import CLIManager

_ = lambda msg: msg

util_filters = [
    'nbsp', 
    'date_as_text',
    'render_name',
    ]

util_tags = [
    'render',
    "get_person_from_handle", 
    "event_table",
    "name_table",
    "surname_table",
    "citation_table",
    "source_table",
    "note_table",
    "attribute_table",
    "address_table",
    "gallery_table",
    "internet_table",
    "association_table",
    "lds_table",
    "reference_table",
    "person_reference_table",
    "note_reference_table",
    "event_reference_table",
    "repository_reference_table",
    "citation_reference_table",
    "media_reference_table",
    "tag_reference_table",
    "children_table",
    "make_button",
    ]

#------------------------------------------------------------------------
#
# Module Constants
#
#------------------------------------------------------------------------
dji = libdjango.DjangoInterface()
dd = displayer.display
dp = parser.parse
db = DbDjango()

def register_plugins():
    dbstate = DbState.DbState()
    climanager = CLIManager(dbstate, False) # don't load db
    climanager.do_reg_plugins(dbstate, None)
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
    person = db.get_person_from_handle(handle)
    return Utils.probably_alive(person, db)

def format_number(number, with_grouping=True):
    # FIXME: should be user's setting
    locale.setlocale(locale.LC_ALL, "en_US.utf8")
    if number != "":
        return locale.format("%d", number, with_grouping)
    else:
        return locale.format("%d", 0, with_grouping)

def table_count(table, with_grouping=True):
    # FIXME: should be user's setting
    locale.setlocale(locale.LC_ALL, "en_US.utf8")
    if table == "person":
        number = models.Person.objects.count()
    elif table == "family":
        number = models.Family.objects.count()
    elif table == "event":
        number = models.Event.objects.count()
    elif table == "note":
        number = models.Note.objects.count()
    elif table == "media":
        number = models.Media.objects.count()
    elif table == "citation":
        number = models.Citation.objects.count()
    elif table == "source":
        number = models.Source.objects.count()
    elif table == "place":
        number = models.Place.objects.count()
    elif table == "repository":
        number = models.Repository.objects.count()
    elif table == "tag":
        number = models.Tag.objects.count()
    else:
        return "[unknown table]"
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
        self.db = DbDjango()
        self.access = SimpleAccess(self.db)
        self.table = SimpleTable(self.access)
        class Doc(object):
            def __init__(self, doc):
                self.doc = doc
                self.doc.set_link_attrs({"class": "browsecell"})
        # None is paperstyle, which is ignored:
        self.doc =  Doc(HtmlDoc.HtmlDoc(make_basic_stylesheet(Table={"set_width":95}), None))
        self.doc.doc._backend = HtmlBackend()
        # You can set elements id, class, etc:
        self.doc.doc.htmllist += [Html('div', class_="content", id="Gallery", style="overflow: auto; height:150px; background-color: #261803;")]

    def columns(self, *args):
        self.table.columns(*args)

    def row(self, *args):
        self.table.row(*map(nbsp, args))

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

def make_button(text, url, *args):
    url = url % args
    #return """[ <a href="%s">%s</a> ] """ % (url, text)
    return """<input type="button" value="%s" onclick="document.location.href='%s'"/>""" % (text, url)

def event_table(obj, user, action, url, args):
    retval = ""
    table = Table()
    table.columns(
        _("Description"), 
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
                event_ref,
                table.db.get_event_from_handle(djevent.handle),
                djevent.gramps_id, 
                display_date(djevent),
                get_title(djevent.place),
                str(event_ref.role_type))
    retval += table.get_html()
    if user.is_superuser and action == "view":
        retval += make_button(_("Add Event"), (url % args).replace("$act", "add"))
        retval += make_button(_("Share Event"), (url % args).replace("$act", "share"))
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
            citationq = dji.CitationRef.filter(object_type=obj_type,
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
                      ["No", "Yes"][citationq],
                      note)
            links.append(('URL', 
                          # url is "/person/%s/name"
                          (url % name.person.handle) + ("/%s" % name.order)))
        table.links(links)
    retval += table.get_html()
    if user.is_superuser and url and action == "view":
        retval += make_button(_("Add Name"), (url % args))
    else:
        retval += nbsp("") # to keep tabs same height
    return retval

def surname_table(obj, user, action, url=None, *args):
    person_handle = args[0]
    order = args[1]
    retval = ""
    table = Table()
    table.columns(_("Order"), _("Surname"),)
    if user.is_authenticated():
        try:
            name = obj.name_set.filter(order=order)[0]
        except:
            name = None
        if name:
            links = []
            for surname in name.surname_set.all().order_by("order"):
                table.row(str(surname.order), surname.surname)
                links.append(('URL', 
                              # url is "/person/%s/name/%s/surname"
                              (url % args) + ("/%s" % surname.order)))
            table.links(links)
            retval += table.get_html()
        else:
            retval += "<p id='error'>No such name order = %s</p>" % order
    if user.is_superuser and url and action == "view":
        retval += make_button(_("Add Surname"), (url % args))
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
        citation_refs = dji.CitationRef.filter(object_type=obj_type,
                                             object_id=obj.id)
        for citation_ref in citation_refs:
            if citation_ref.citation:
                if citation_ref.citation.source:
                    source = citation_ref.citation.source
                    table.row(source,
                              source.title,
                              source.author,
                              citation_ref.citation.page,
                              )
    retval += table.get_html()
    if user.is_superuser and url and action == "view":
        retval += make_button(_("Add Source"), (url % args).replace("$act", "add"))
        retval += make_button(_("Share Source"), (url % args).replace("$act", "share"))
    else:
        retval += nbsp("") # to keep tabs same height
    return retval

def citation_table(obj, user, action, url=None, *args):
    retval = ""
    table = Table()
    table.columns(_("ID"), 
                  _("Confidence"),
                  _("Page"))
    if user.is_authenticated():
        obj_type = ContentType.objects.get_for_model(obj)
        citation_refs = dji.CitationRef.filter(object_type=obj_type,
                                               object_id=obj.id)
        for citation_ref in citation_refs:
            if citation_ref.citation:
                citation = table.db.get_citation_from_handle(
                    citation_ref.citation.handle)
                table.row(citation,
                          str(citation.confidence),
                          str(citation.page),
                          )
    retval += table.get_html()
    if user.is_superuser and url and action == "view":
        retval += make_button(_("Add Citation"), (url % args).replace("$act", "add"))
        retval += make_button(_("Share Citation"), (url % args).replace("$act", "share"))
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
    if user.is_superuser and url and action == "view":
        retval += make_button(_("Add Note"), (url % args).replace("$act", "add"))
        retval += make_button(_("Share Note"), (url % args).replace("$act", "share"))
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
    if user.is_superuser and url and action == "view":
        retval += make_button(_("Add Attribute"), (url % args))
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
    if user.is_superuser and url and action == "view":
        retval += make_button(_("Add Address"), (url % args))
    else:
        retval += nbsp("") # to keep tabs same height
    return retval

def gallery_table(obj, user, action, url=None, *args):
    retval = ""
    table = Table()
    table.columns(_("Description"), 
                  _("Type"),
                  )
    if user.is_authenticated():
        obj_type = ContentType.objects.get_for_model(obj)
        media_refs = dji.MediaRef.filter(object_type=obj_type,
                                        object_id=obj.id)
        for media_ref in media_refs:
            media = table.db.get_object_from_handle(
                media_ref.ref_object.handle)
            table.row(table.db.get_object_from_handle(media.handle),
                      str(media_ref.ref_object.desc),
                      media_ref.ref_object.path)
    retval += table.get_html()
    if user.is_superuser and url and action == "view":
        retval += make_button(_("Add Media"), (url % args).replace("$act", "add"))
        retval += make_button(_("Share Media"), (url % args).replace("$act", "share"))
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
    if user.is_superuser and url and action == "view":
        retval += make_button(_("Add Internet"), (str(url) % args))
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
    if user.is_superuser and url and action == "view":
        retval += make_button(_("Add Association"), (url % args))
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
    if user.is_superuser and url and action == "view":
        retval += make_button(_("Add LDS"), (url % args))
    else:
        retval += nbsp("") # to keep tabs same height
    return retval

def reference_table(obj, user, action, url=None, *args):
    retval = ""
    table = Table()
    table.columns(
        _("Type"),
        _("Reference"), 
        _("ID"))
    if user.is_authenticated():
        pass
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    return retval 

def person_reference_table(obj, user, action):
    retval = ""
    table = Table()
    table.columns(
        _("Type"),
        _("Reference"), 
        _("ID"))
    if user.is_authenticated() and action != "add":
        for reference in obj.families.all():
            table.row(
                _("Family (spouse in)"),
                reference,
                reference.gramps_id)
        for reference in obj.parent_families.all():
            table.row(
                _("Family (child in)"),
                reference,
                reference.gramps_id)
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    return retval 

def note_reference_table(obj, user, action):
    retval = ""
    table = Table()
    table.columns(
        _("Type"),
        _("Reference"), 
        _("ID"))
    if user.is_authenticated() and action != "add":
        for reference in models.NoteRef.objects.filter(ref_object=obj):
            ref_from_class = reference.object_type.model_class()
            item = ref_from_class.objects.get(id=reference.object_id)
            table.row(
                item.__class__.__name__,
                item,
                item.gramps_id)
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    return retval 

def event_reference_table(obj, user, action):
    retval = ""
    table = Table()
    table.columns(
        _("Type"),
        _("Reference"), 
        _("ID"))
    if user.is_authenticated() and action != "add":
        for reference in models.EventRef.objects.filter(ref_object=obj):
            ref_from_class = reference.object_type.model_class()
            item = ref_from_class.objects.get(id=reference.object_id)
            table.row(
                item.__class__.__name__,
                item,
                item.gramps_id)
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    return retval 

def repository_reference_table(obj, user, action):
    retval = ""
    table = Table()
    table.columns(
        _("Type"),
        _("Reference"), 
        _("ID"))
    if user.is_authenticated() and action != "add":
        for reference in models.RepositoryRef.objects.filter(ref_object=obj):
            ref_from_class = reference.object_type.model_class()
            item = ref_from_class.objects.get(id=reference.object_id)
            table.row(
                item.__class__.__name__,
                item,
                item.gramps_id)
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    return retval 

def citation_reference_table(obj, user, action):
    retval = ""
    table = Table()
    table.columns(
        _("Type"),
        _("Reference"), 
        _("ID"))
    if user.is_authenticated() and action != "add":
        for reference in models.CitationRef.objects.filter(citation=obj):
            ref_from_class = reference.object_type.model_class()
            item = ref_from_class.objects.get(id=reference.object_id)
            table.row(
                item.__class__.__name__,
                item,
                item.gramps_id)
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    return retval 

def media_reference_table(obj, user, action):
    retval = ""
    table = Table()
    table.columns(
        _("Type"),
        _("Reference"), 
        _("ID"))
    if user.is_authenticated() and action != "add":
        for reference in models.MediaRef.objects.filter(ref_object=obj):
            ref_from_class = reference.object_type.model_class()
            item = ref_from_class.objects.get(id=reference.object_id)
            table.row(
                item.__class__.__name__,
                item,
                item.gramps_id)
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    return retval 

def tag_reference_table(obj, user, action):
    retval = ""
    table = Table()
    table.columns(
        _("Type"),
        _("Reference"), 
        _("ID"))
    if user.is_authenticated() and action != "add":
        querysets = [obj.person_set, obj.family_set, obj.note_set, obj.media_set]
        for queryset in querysets:
            for item in queryset.all():
                table.row(
                    item.__class__.__name__,
                    item,
                    item.gramps_id)
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
                      date_as_text(child.birth, user),
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
    if user.is_superuser and url and action == "view":
        retval += make_button(_("Add Child"), (url % args))
    else:
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
    #db = DbDjango()
    #event = get_birth_or_fallback(db, db.get_person_from_handle(person.handle))
    #if event:
    #    return event.date
    return None

def person_get_death_date(person):
    #db = DbDjango()
    #event = get_death_or_fallback(db, db.get_person_from_handle(person.handle))
    #if event:
    #    return event.date
    return None

def display_date(obj):
    date_tuple = dji.get_date(obj)
    if date_tuple:
        gdate = GDate()
        gdate.unserialize(date_tuple)
        return dd(gdate)
    else:
        return ""

def render(formfield, user, action, test=False, truetext="", id=None):
    if not user.is_authenticated():
        action = "view"
    if action == "view": # show as text
        if (not user.is_authenticated() and not test) or user.is_authenticated():
            fieldname = formfield.name # 'surname'
            try:
                item = getattr(formfield.form.model, fieldname)
                if (item.__class__.__name__ == 'ManyRelatedManager'):
                    retval = ", ".join([i.get_link() for i in item.all()])
                else:
                    retval = str(item)
                    if retval == "True":
                        retval = "Yes"
                    elif retval == "False":
                        retval = "No"
            except:
                # name, "prefix"
                try:
                    retval = str(formfield.form.data[fieldname]) 
                except:
                    retval = "[None]"
        else:
            retval = truetext
    else: # show as widget
        if id != None:
            retval = formfield.as_widget(attrs={"id": id})
        else:
            retval = formfield.as_widget()
    return retval

def render_name(name, user):
    """
    Given a Django or Gramps object, render the name and return.  This
    function uses authentication, privacy and probably_alive settings.
    """
    if name is None:
        return "[None]"
    elif isinstance(name, models.Name):
        if not user.is_authenticated():
            name.sanitize()
        try:
            surname = name.surname_set.get(primary=True)
        except:
            surname = "[No primary surname]"
        return "%s, %s" % (surname, name.first_name)
    elif isinstance(name, forms.NameForm):
        if not user.is_authenticated():
            name.model.sanitize()
        try:
            surname = name.model.surname_set.get(primary=True)
        except:
            surname = "[No primary surname]"
        return "%s, %s" % (surname, 
                           name.model.first_name)
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
        try:
            surname = name.surname_set.get(primary=True)
        except:
            surname = "[No primary surname]"
        return "%s, %s" % (surname, name.first_name)
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

def date_as_text(obj, user):
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
                return dd(gdate)
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

def boolean(s):
    return s.lower() in ["true", "1", "yes", "y", "t"]

def update_last_changed(obj, user):
    obj.last_changed = datetime.datetime.now()
    obj.last_changed_by = user

register_plugins()

# works after registering plugins:
import HtmlDoc 
from libhtmlbackend import HtmlBackend, DocBackend, process_spaces
from libhtml import Html

class WebAppBackend(HtmlBackend):
    SUPPORTED_MARKUP = [
            DocBackend.BOLD,
            DocBackend.ITALIC,
            DocBackend.UNDERLINE,
            DocBackend.FONTFACE,
            DocBackend.FONTSIZE,
            DocBackend.FONTCOLOR,
            DocBackend.HIGHLIGHT,
            DocBackend.SUPERSCRIPT,
            DocBackend.LINK,
            ]

    STYLETAG_MARKUP = {
        DocBackend.BOLD        : ("<b>", "</b>"),
        DocBackend.ITALIC      : ("<i>", "</i>"),
        DocBackend.UNDERLINE   : ('<u>', '</u>'),
        DocBackend.SUPERSCRIPT : ("<sup>", "</sup>"),
    }

### Taken from Narrated Web Report
class StyledNoteFormatter(object):
    def __init__(self, database):
        self.database = database
        self._backend = WebAppBackend()
        self._backend.build_link = self.build_link

    def format(self, note):
        return self.styled_note(note.get_styledtext())

    def styled_note(self, styledtext):
        text = str(styledtext)
        if not text:
            return ''
        s_tags = styledtext.get_tags()
        markuptext = self._backend.add_markup_from_styled(text, s_tags, split='\n').replace("\n\n", "<p></p>").replace("\n", "<br/>")
        return markuptext

    def build_link(self, prop, handle, obj_class):
        """
        Build a link to an item.
        """
        if prop == "gramps_id":
            if obj_class in self.database.get_table_names():
                obj = self.database.get_table_metadata(obj_class)["gramps_id_func"](handle)
                if obj:
                    handle = obj.handle
                else:
                    raise AttributeError("gramps_id '%s' not found in '%s'" % 
                                         handle, obj_class)
            else:
                raise AttributeError("invalid gramps_id lookup " 
                                     "in table name '%s'" % obj_class)
        # handle, ppl
        return "/%s/%s" % (obj_class.lower(), handle)

class WebAppParser(HTMLParser):
    BOLD = 0
    ITALIC = 1
    UNDERLINE = 2
    FONTFACE = 3
    FONTSIZE = 4
    FONTCOLOR = 5
    HIGHLIGHT = 6 # background color
    SUPERSCRIPT = 7
    LINK = 8

    def __init__(self):
        HTMLParser.__init__(self)
        self.__text = ""
        self.__tags = {}
        self.__stack = []

    def handle_data(self, data):
        self.__text += data

    def push(self, pos, tag, attrs):
        self.__stack.append([pos, tag, attrs])

    def pop(self):
        return self.__stack.pop()

    def handle_starttag(self, tag, attrs):
        if tag == "br":
            self.__text += "\n"
            return
        self.push(len(self.__text), tag.lower(), attrs)

    def handle_startstoptag(self, tag, attrs):
        if tag == "br":
            self.__text += "\n"
            return
        elif tag == "p":
            self.__text += "\n\n"
            return
        else:
            print "Unhandled start/stop tag '%s'" % tag

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in ["br"]: return
        (start_pos, start_tag, attrs) = self.pop()
        attrs = dict(attrs)
        if tag != start_tag: return # skip <i><b></i></b> formats
        arg = None
        tagtype = None
        if tag == "span":
            # "span": get color, font, size
            if "style" in attrs:
                style = attrs["style"]
                if 'color' in style:
                    tagtype = self.FONTCOLOR
                    match = re.match("color:([^;]*);", style)
                    if match:
                        arg = match.groups()[0]
                    else:
                        print "Unhandled color tag: '%s'" % style
                elif 'background-color' in style:
                    tagtype = self.HIGHLIGHT
                    match = re.match("background-color:([^;]*);", style)
                    if match:
                        arg = match.groups()[0]
                    else:
                        print "Unhandled background-color tag: '%s'" % style
                elif "font-family" in style:
                    tagtype = self.FONTFACE
                    match = re.match("font-family:'([^;]*)';", style)
                    if match:
                        arg = match.groups()[0]
                    else:
                        print "Unhandled font-family tag: '%s'" % style
                elif "font-size" in style:
                    tagtype = self.FONTSIZE
                    match = re.match("font-size:([^;]*)px;", style)
                    if match:
                        arg = int(match.groups()[0])
                    else:
                        print "Unhandled font-size tag: '%s'" % style
                else:
                    print "Unhandled span arg: '%s'" % attrs
            else:
                print "span has no style: '%s'" % attrs
        # "b", "i", "u", "sup": direct conversion
        elif tag == "b":
            tagtype = self.BOLD
        elif tag == "i":
            tagtype = self.ITALIC
        elif tag == "u":
            tagtype = self.UNDERLINE
        elif tag == "sup":
            tagtype = self.SUPERSCRIPT
        elif tag == "p":
            self.__text += "\n\n"
            return
        elif tag == "div":
            self.__text += "\n"
            return
        elif tag == "a":
            tagtype = self.LINK
            # "a": get /object/handle, or url
            if "href" in attrs:
                href = attrs["href"]
                if href.startswith("/"):
                    parts = href.split("/")
                    arg = "gramps://%s/handle/%s" % (parts[-2].title(), parts[-1])
                else:
                    arg = href
            else:
                print "Unhandled a with no href: '%s'" % attrs
        else:
            return
            print "Unhandled tag: '%s'" % tag

        if start_pos == len(self.__text): return # does nothing
        key = ((tagtype, u''), arg)
        if key not in self.__tags:
            self.__tags[key] = []
        self.__tags[key].append((start_pos, len(self.__text)))

    def tags(self):
        # [((code, u''), string/num, [(start, stop), ...]), ...]
        return [(key[0], key[1], self.__tags[key]) for key in self.__tags]

    def text(self):
        return self.__text

def parse_styled_text(text):
    parser = WebAppParser()
    parser.feed(text)
    parser.close()
    return (parser.text(), parser.tags())

