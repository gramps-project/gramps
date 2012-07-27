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
from gen.simple import SimpleTable, SimpleAccess, make_basic_stylesheet
from gen.utils.alive import probably_alive as alive
from gen.dbstate import DbState
from gen.datehandler import displayer, parser
from gen.lib.date import Date as GDate, Today
import gen.lib
from gen.utils.db import get_birth_or_fallback, get_death_or_fallback
from gen.plug import BasePluginManager
from cli.grampscli import CLIManager

_ = lambda msg: msg

TAB_HEIGHT = 200

util_filters = [
    'nbsp', 
    'date_as_text',
    'render_name',
    ]

util_tags = [
    'render',
    'media_link',
    'render_name',
    "get_person_from_handle", 
    "event_table",
    "history_table",
    "name_table",
    "surname_table",
    "citation_table",
    "note_table",
    "attribute_table",
    "data_table",
    "address_table",
    "location_table",
    "media_table",
    "internet_table",
    "association_table",
    "lds_table",
    "reference_table",
    "repository_table",
    "person_reference_table",
    "note_reference_table",
    "event_reference_table",
    "repository_reference_table",
    "citation_reference_table",
    "source_reference_table",
    "media_reference_table",
    "tag_reference_table",
    "place_reference_table",
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
    dbstate = DbState()
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
    return alive(person, db)

def format_number(number, with_grouping=True):
    # FIXME: should be user's setting
    try:
        locale.setlocale(locale.LC_ALL, "en_US.utf8")
    except:
        pass
    if number != "":
        return locale.format("%d", number, with_grouping)
    else:
        return locale.format("%d", 0, with_grouping)

def table_count(table, with_grouping=True):
    # FIXME: should be user's setting
    try:
        locale.setlocale(locale.LC_ALL, "en_US.utf8")
    except:
        pass
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
    >>> table = Table("css_id")
    >>> table.columns("Col1", "Col2", "Col3")
    >>> table.row("1", "2", "3")
    >>> table.row("4", "5", "6")
    >>> table.get_html()
    """
    def __init__(self, id, style=None):
        self.id = id # css id
        self.db = DbDjango()
        self.access = SimpleAccess(self.db)
        self.table = SimpleTable(self.access)
        self.column_widths = None
        class Doc(object):
            def __init__(self, doc):
                self.doc = doc
                self.doc.set_link_attrs({"class": "browsecell"})
        # None is paperstyle, which is ignored:
        self.doc =  Doc(HtmlDoc(
                make_basic_stylesheet(
                    Table={"set_width":95}, 
                    TableHeaderCell={"set_bottom_border": True,
                                     "set_right_border": True,
                                     "set_padding": .1,
                                     },
                    TableDataCell={"set_bottom_border": True, 
                                   "set_right_border": True,
                                   "set_padding": .1,
                                   },
                    ), 
                None))
        self.doc.doc._backend = HtmlBackend()
        self.doc.doc.use_table_headers = True
        # You can set elements id, class, etc:
        self.doc.doc.htmllist += [
            Html('div', 
                 class_="content", 
                 id=self.id, 
                 style=("overflow: auto; height:%spx; background-color: #f4f0ec;" % TAB_HEIGHT) if not style else style)]

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
        retval = ""
        # The HTML writer escapes data:
        self.table.write(self.doc, self.column_widths) # forces to htmllist
        # FIXME: do once, or once per table?
        self.doc.doc.build_style_declaration(self.id) # can pass id, for whole
        # FIXME: don't want to repeat this, unless diff for each table:
        retval += "<style>%s</style>" % self.doc.doc.style_declaration
        # We have a couple of HTML bits that we want to unescape:
        return retval + str(self.doc.doc.htmllist[0]).replace("&amp;nbsp;", "&nbsp;")

def build_args(**kwargs):
    retval = ""
    first = True
    for key in kwargs:
        if kwargs[key] is not "":
            if first:
                retval+= "?"
                first = False
            else:
                retval += "&"
            retval += "%s=%s" % (key, kwargs[key])
    return retval

def build_search(request):
    search = request.GET.get("search", "") or request.POST.get("search", "")
    page = request.GET.get("page", "") or request.POST.get("page", "")
    return build_args(search=search, page=page)

def make_button(text, url, *args):
    newargs = []
    kwargs = ""
    last = ""
    for arg in args:
        if isinstance(arg, (str, unicode)) and arg.startswith("?"):
            kwargs = arg
        elif isinstance(arg, (str, unicode)) and arg.startswith("#"):
            last = arg
        elif arg == "":
            pass
        else:
            newargs.append(arg)
    if newargs:
        url = url % tuple(newargs)
    return mark_safe("""<input type="button" value="%s" onclick="document.location.href='%s%s%s'"/>""" % 
                     (text, url, kwargs, last))

def event_table(obj, user, act, url, args):
    retval = ""
    has_data = False
    cssid = "tab-events"
    table = Table("event_table")
    table.columns(
        "",
        _("Description"), 
        _("Type"),
        _("ID"),
        _("Date"),
        _("Place"),
        _("Role"))
    table.column_widths = [10, 20, 10, 7, 20, 23, 10]
    if user.is_authenticated():
        obj_type = ContentType.objects.get_for_model(obj)
        event_ref_list = models.EventRef.objects.filter(
            object_id=obj.id, 
            object_type=obj_type).order_by("order")
        event_list = [(o.ref_object, o) for o in event_ref_list]
        links = []
        count = 1
        for (djevent, event_ref) in event_list:
            table.row(Link("[[x%d]][[^%d]][[v%d]]" % (count, count, count)) if user.is_superuser and act == "view" else "",
                djevent.description,
                table.db.get_event_from_handle(djevent.handle),
                djevent.gramps_id, 
                display_date(djevent),
                get_title(djevent.place),
                str(event_ref.role_type))
            links.append(('URL', event_ref.get_url()))
            has_data = True
            count += 1
        table.links(links)
    retval += table.get_html()
    if user.is_superuser and act == "view":
        count = 1
        for (djevent, event_ref) in event_list:
            item = obj.__class__.__name__.lower()
            retval = retval.replace("[[x%d]]" % count, make_button("x", "/%s/%s/remove/eventref/%d" % (item, obj.handle, count)))
            retval = retval.replace("[[^%d]]" % count, make_button("^", "/%s/%s/up/eventref/%d" % (item, obj.handle, count)))
            retval = retval.replace("[[v%d]]" % count, make_button("v", "/%s/%s/down/eventref/%d" % (item, obj.handle, count)))
            count += 1
        retval += make_button(_("Add New Event"), (url % args).replace("$act", "add"))
        retval += make_button(_("Add Existing Event"), (url % args).replace("$act", "share"))
    else:
        retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def history_table(obj, user, act):
    retval = ""
    has_data = False
    cssid = "tab-history"
    table = Table("history_table")
    table.columns(
        _("Action"), 
        _("Comment"),
        )
    if user.is_authenticated():
        obj_type = ContentType.objects.get_for_model(obj)
        for entry in models.Log.objects.filter(
            object_id=obj.id, 
            object_type=obj_type):
            table.row(
                "%s on %s by %s" % (entry.log_type, 
                                    entry.last_changed,
                                    entry.last_changed_by),
                entry.reason)
            has_data = True
        table.row(
            "Latest on %s by %s" % (obj.last_changed,
                                     obj.last_changed_by),
            "Current status")
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def name_table(obj, user, act, url=None, *args):
    retval = ""
    has_data = False
    cssid = "tab-names"
    table = Table("name_table")
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
            has_data = True
        table.links(links)
    retval += table.get_html()
    if user.is_superuser and url and act == "view":
        retval += make_button(_("Add Name"), (url % args))
    else:
        retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def surname_table(obj, user, act, url=None, *args):
    person_handle = args[0]
    order = args[1]
    retval = ""
    has_data = False
    cssid = "tab-surnames"
    table = Table("surname_table")
    table.columns(_("Order"), _("Surname"),)
    if user.is_authenticated():
        try:
            name = obj.name_set.filter(order=order)[0]
        except:
            name = None
        if name:
            for surname in name.surname_set.all().order_by("order"):
                table.row(str(surname.order), surname)
                has_data = True
            retval += table.get_html()
        else:
            retval += "<p id='error'>No such name order = %s</p>" % order
    if user.is_superuser and url and act == "view":
        retval += make_button(_("Add Surname"), (url % args))
    else:
        retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def citation_table(obj, user, act, url=None, *args):
    retval = ""
    has_data = False
    cssid = "tab-citations"
    table = Table("citation_table")
    table.columns("", 
                  _("ID"), 
                  _("Confidence"),
                  _("Page"))
    table.column_widths = [10, 10, 50, 30]
    if user.is_authenticated():
        obj_type = ContentType.objects.get_for_model(obj)
        citation_refs = dji.CitationRef.filter(object_type=obj_type,
                                               object_id=obj.id).order_by("order")
        links = []
        count = 1
        for citation_ref in citation_refs:
            if citation_ref.citation:
                citation = table.db.get_citation_from_handle(
                    citation_ref.citation.handle)
                table.row(Link("[[x%d]][[^%d]][[v%d]]" % (count, count, count)) if user.is_superuser and url and act == "view" else "",
                          citation.gramps_id,
                          str(citation.confidence),
                          str(citation.page),
                          )
                links.append(('URL', citation_ref.get_url()))
                has_data = True
                count += 1
        table.links(links)
    retval += table.get_html()
    if user.is_superuser and url and act == "view":
        count = 1
        for citation_ref in citation_refs:
            item = obj.__class__.__name__.lower()
            retval = retval.replace("[[x%d]]" % count, make_button("x", "/%s/%s/remove/citationref/%d" % (item, obj.handle, count)))
            retval = retval.replace("[[^%d]]" % count, make_button("^", "/%s/%s/up/citationref/%d" % (item, obj.handle, count)))
            retval = retval.replace("[[v%d]]" % count, make_button("v", "/%s/%s/down/citationref/%d" % (item, obj.handle, count)))
            count += 1
        retval += make_button(_("Add New Citation"), (url % args).replace("$act", "add"))
        retval += make_button(_("Add Existing Citation"), (url % args).replace("$act", "share"))
    else:
        retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def repository_table(obj, user, act, url=None, *args):
    retval = ""
    has_data = False
    cssid = "tab-repositories"
    table = Table("repository_table")
    table.columns(
        _("ID"),
        _("Type"),
        _("Note"))
    if user.is_authenticated():
        pass
    retval += table.get_html()
    ## FIXME: missing table
    ## has_data = True
    if user.is_superuser and url and act == "view":
        retval += make_button(_("Add New Repository"), (url % args).replace("$act", "add"))
        retval += make_button(_("Add Existing Repository"), (url % args).replace("$act", "share"))
    else:
        retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def note_table(obj, user, act, url=None, *args):
    retval = ""
    has_data = False
    cssid = "tab-notes"
    table = Table("note_table")
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
            has_data = True
    retval += table.get_html()
    if user.is_superuser and url and act == "view":
        retval += make_button(_("Add New Note"), (url % args).replace("$act", "add"))
        retval += make_button(_("Add Existing Note"), (url % args).replace("$act", "share"))
    else:
        retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def data_table(obj, user, act, url=None, *args):
    retval = ""
    has_data = False
    cssid = "has_data"
    table = Table("data_table")
    table.columns(_("Type"), 
                  _("Value"),
                  )
    if user.is_authenticated():
        pass
    ## FIXME: missing table
    ## has_data = True
    retval += table.get_html()
    if user.is_superuser and url and act == "view":
        retval += make_button(_("Add Data"), (url % args))
    else:
        retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def attribute_table(obj, user, act, url=None, *args):
    retval = ""
    has_data = False
    cssid = "tab-attributes"
    table = Table("attribute_table")
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
            has_data = True
    retval += table.get_html()
    if user.is_superuser and url and act == "view":
        retval += make_button(_("Add Attribute"), (url % args))
    else:
        retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def address_table(obj, user, act, url=None, *args):
    retval = ""
    has_data = False
    cssid = "tab-addresses"
    table = Table("address_table")
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
                has_data = True
    retval += table.get_html()
    if user.is_superuser and url and act == "view":
        retval += make_button(_("Add Address"), (url % args))
    else:
        retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def location_table(obj, user, act, url=None, *args):
    retval = ""
    has_data = False
    cssid = "tab-locations"
    table = Table("location_table")
    table.columns(_("Date"), 
                  _("Address"),
                  _("City"),
                  _("State"),
                  _("Country"))
    if user.is_authenticated():
        pass # FIXME
    ## FIXME: missing table
    ## has_data = True
    retval += table.get_html()
    if user.is_superuser and url and act == "view":
        retval += make_button(_("Add Address"), (url % args))
    else:
        retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def media_table(obj, user, act, url=None, *args):
    retval = ""
    has_data = False
    cssid = "tab-media"
    table = Table("media_table")
    table.columns(_("Description"), 
                  _("Type"),
                  _("Path/Filename"),
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
            has_data = True
    retval += table.get_html()
    if user.is_superuser and url and act == "view":
        retval += make_button(_("Add New Media"), (url % args).replace("$act", "add"))
        retval += make_button(_("Add Existing Media"), (url % args).replace("$act", "share"))
    else:
        retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def internet_table(obj, user, act, url=None, *args):
    retval = ""
    has_data = False
    cssid = "tab-internet"
    table = Table("internet_table")
    table.columns(_("Type"),
                  _("Path"),
                  _("Description"))
    if user.is_authenticated():
        urls = dji.Url.filter(person=obj)
        for url_obj in urls:
            table.row(str(url_obj.url_type),
                      url_obj.path,
                      url_obj.desc)
            has_data = True
    retval += table.get_html()
    if user.is_superuser and url and act == "view":
        retval += make_button(_("Add Internet"), (str(url) % args))
    else:
        retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def association_table(obj, user, act, url=None, *args):
    retval = ""
    has_data = False
    cssid = "tab-associations"
    table = Table("association_table")
    table.columns(_("Name"), 
                  _("ID"),
                  _("Association"))
    if user.is_authenticated():
        gperson = table.db.get_person_from_handle(obj.handle)
        if gperson:
            associations = gperson.get_person_ref_list()
            for association in associations:
                table.row() # FIXME: missing table
                has_data = True
    retval += table.get_html()
    if user.is_superuser and url and act == "view":
        retval += make_button(_("Add Association"), (url % args))
    else:
        retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def lds_table(obj, user, act, url=None, *args):
    retval = ""
    has_data = False
    cssid = "tab-lds"
    table = Table("lds_table")
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
            has_data = True
    retval += table.get_html()
    if user.is_superuser and url and act == "view":
        retval += make_button(_("Add LDS"), (url % args))
    else:
        retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval

def reference_table(obj, user, act, url=None, *args):
    retval = ""
    has_data = False
    cssid = "tab-references"
    table = Table("reference_table")
    table.columns(
        _("Type"),
        _("Reference"), 
        _("ID"))
    if user.is_authenticated():
        pass
    ## FIXME: missing table?
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval 

def person_reference_table(obj, user, act):
    retval = """<div style="overflow: auto; height:%spx;">""" % TAB_HEIGHT
    has_data = False
    cssid = "tab-references"
    text1 = ""
    text2 = ""
    table1 = Table("person_reference_table", style="background-color: #f4f0ec;")
    table1.columns(
        "As Spouse",
        _("ID"),
        _("Reference"), 
        )
    table1.column_widths = [10, 10, 82]
    table2 = Table("person_reference_table", style="background-color: #f4f0ec;")
    table2.columns(
        "As Child",
        _("ID"),
        _("Reference"), 
        )
    table2.column_widths = [10, 10, 82]
    if user.is_authenticated() and act != "add":
        count = 1
        for through in models.PersonFamilyOrder.objects.filter(person=obj).order_by("order"):
            reference = through.family
            table1.row(
                Link("[[x%d]][[^%d]][[v%d]]" % (count, count, count)) if user.is_superuser else "",
                reference.gramps_id,
                reference,
                )
            has_data = True
            count += 1
        text1 += table1.get_html()
        count = 1
        for through in models.PersonFamilyOrder.objects.filter(person=obj).order_by("order"):
            reference = through.family
            text1 = text1.replace("[[x%d]]" % count, make_button("x", "/person/%s/remove/family/%d" % (obj.handle, count)))
            text1 = text1.replace("[[^%d]]" % count, make_button("^", "/person/%s/up/family/%d" % (obj.handle, count)))
            text1 = text1.replace("[[v%d]]" % count, make_button("v", "/person/%s/down/family/%d" % (obj.handle, count)))
            count += 1
        # Parent Families
        count = 1
        for through in models.PersonParentFamilyOrder.objects.filter(person=obj).order_by("order"):
            reference = through.family
            table2.row(
                Link("[[x%d]][[^%d]][[v%d]]" % (count, count, count)) if user.is_superuser else "",
                reference.gramps_id,
                reference,
                )
            has_data = True
            count += 1
        text2 += table2.get_html()
        count = 1
        for through in models.PersonParentFamilyOrder.objects.filter(person=obj).order_by("order"):
            reference = through.family
            text2 = text2.replace("[[x%d]]" % count, make_button("x", "/person/%s/remove/parentfamily/%d" % (obj.handle, count)))
            text2 = text2.replace("[[^%d]]" % count, make_button("^", "/person/%s/up/parentfamily/%d" % (obj.handle, count)))
            text2 = text2.replace("[[v%d]]" % count, make_button("v", "/person/%s/down/parentfamily/%d" % (obj.handle, count)))
            count += 1

    retval += text1 + text2 + "</div>"
    retval += make_button(_("Add as Spouse to New Family"), 
                          "/family/add/spouse/%s" % obj.handle)
    retval += make_button(_("Add as Spouse to Existing Family"), 
                          "/family/share/spouse/%s" % obj.handle)
    retval += make_button(_("Add as Child to New Family"), 
                          "/family/add/child/%s" % obj.handle)
    retval += make_button(_("Add as Child to Existing Family"), 
                          "/family/share/child/%s" % obj.handle)
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval 

def note_reference_table(obj, user, act):
    retval = ""
    has_data = False
    cssid = "tab-references"
    table = Table("note_reference_table")
    table.columns(
        _("Type"),
        _("Reference"), 
        _("ID"))
    if user.is_authenticated() and act != "add":
        for reference in models.NoteRef.objects.filter(ref_object=obj):
            ref_from_class = reference.object_type.model_class()
            item = ref_from_class.objects.get(id=reference.object_id)
            table.row(
                item.__class__.__name__,
                item,
                item.gramps_id)
            has_data = True
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval 

def event_reference_table(obj, user, act):
    retval = ""
    has_data = False
    cssid = "tab-references"
    table = Table("event_reference_table")
    table.columns(
        _("Type"),
        _("Reference"), 
        _("ID"))
    if user.is_authenticated() and act != "add":
        for reference in models.EventRef.objects.filter(ref_object=obj):
            ref_from_class = reference.object_type.model_class()
            try:
                item = ref_from_class.objects.get(id=reference.object_id)
            except:
                print "Warning: Corrupt reference: %s" % reference
                continue
            table.row(
                item.__class__.__name__,
                item,
                item.gramps_id)
            has_data = True
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval 

def repository_reference_table(obj, user, act):
    retval = ""
    has_data = False
    cssid = "tab-references"
    table = Table("repository_reference_table")
    table.columns(
        _("Type"),
        _("Reference"), 
        _("ID"))
    if user.is_authenticated() and act != "add":
        for reference in models.RepositoryRef.objects.filter(ref_object=obj):
            ref_from_class = reference.object_type.model_class()
            item = ref_from_class.objects.get(id=reference.object_id)
            table.row(
                item.__class__.__name__,
                item,
                item.gramps_id)
            has_data = True
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval 

def citation_reference_table(obj, user, act):
    retval = ""
    has_data = False
    cssid = "tab-references"
    table = Table("citation_reference_table")
    table.columns(
        _("Type"),
        _("Reference"), 
#        _("ID")
        )
    if user.is_authenticated() and act != "add":
        for reference in models.CitationRef.objects.filter(citation=obj):
            ref_from_class = reference.object_type.model_class()
            item = ref_from_class.objects.get(id=reference.object_id)
            table.row(
                item.__class__.__name__,
                item)
            has_data = True
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval 

def source_reference_table(obj, user, act):
    retval = ""
    has_data = False
    cssid = "tab-references"
    table = Table("source_reference_table")
    table.columns(
        _("Type"),
        _("Reference"), 
        _("ID"))
    if user.is_authenticated() and act != "add":
        pass
    # FIXME: where is source ref?
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval 

def media_reference_table(obj, user, act):
    retval = ""
    has_data = False
    cssid = "tab-references"
    table = Table("media_reference_table")
    table.columns(
        _("Type"),
        _("Reference"), 
        _("ID"))
    if user.is_authenticated() and act != "add":
        for reference in models.MediaRef.objects.filter(ref_object=obj):
            ref_from_class = reference.object_type.model_class()
            item = ref_from_class.objects.get(id=reference.object_id)
            table.row(
                item.__class__.__name__,
                item,
                item.gramps_id)
            has_data = True
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval 

def place_reference_table(obj, user, act):
    retval = ""
    has_data = False
    cssid = "tab-references"
    table = Table("place_reference_table")
    table.columns(
        _("Type"),
        _("Reference"), 
        _("ID"))
    if user.is_authenticated() and act != "add":
        pass # FIXME
    ## FIXME: missing table
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval 

def tag_reference_table(obj, user, act):
    retval = ""
    has_data = False
    cssid = "tab-references"
    table = Table("tag_reference_table")
    table.columns(
        _("Type"),
        _("Reference"), 
        _("ID"))
    if user.is_authenticated() and act != "add":
        querysets = [obj.person_set, obj.family_set, obj.note_set, obj.media_set]
        for queryset in querysets:
            for item in queryset.all():
                table.row(
                    item.__class__.__name__,
                    item,
                    item.gramps_id)
                has_data = True
    retval += table.get_html()
    retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
    return retval 

class Link(object):
    def __init__(self, string, url=None):
        self.string = string
        self.url = url
    def get_url(self):
        return self.url
    def __str__(self):
        return self.string

def children_table(obj, user, act, url=None, *args):
    retval = ""
    has_data = False
    cssid = "tab-children"
    table = Table("children_table")
    table.columns(
        "",
        _("#"),
        _("ID"),
        _("Name"),
        _("Gender"),
        _("Paternal"),
        _("Maternal"),
        _("Birth Date"),
        )
    table.column_widths = [10, 3, 8, 30, 8, 8, 8, 25] 

    family = obj
    obj_type = ContentType.objects.get_for_model(family)
    childrefs = dji.ChildRef.filter(object_id=family.id,
                                    object_type=obj_type).order_by("order")
    links = []
    count = 1
    for childref in childrefs:
        child = childref.ref_object
        if user.is_authenticated():
            table.row(Link("[[x%d]][[^%d]][[v%d]]" % (count, count, count)) if user.is_superuser and url and act == "view" else "",
                      str(count), 
                      "[%s]" % child.gramps_id,
                      render_name(child, user),
                      child.gender_type,
                      childref.father_rel_type,
                      childref.mother_rel_type,
                      date_as_text(child.birth, user),
                      )
            has_data = True
            links.append(('URL', childref.get_url()))
            count += 1
        else:
            table.row("",
                      str(count), 
                      "[%s]" % child.gramps_id,
                      render_name(child, user) if not child.private else "[Private]",
                      child.gender_type if not child.private else "[Private]",
                      "[Private]",
                      "[Private]",
                      "[Private]",
                      )
            if not child.private and not childref.private:
                links.append(('URL', childref.get_url()))
            else:
                links.append((None, None))
            has_data = True
            count += 1
    table.links(links)
    retval += table.get_html()
    if user.is_superuser and url and act == "view":
        count = 1
        for childref in childrefs:
            retval = retval.replace("[[x%d]]" % count, make_button("x", "/family/%s/remove/child/%d" % (family.handle, count)))
            retval = retval.replace("[[^%d]]" % count, make_button("^", "/family/%s/up/child/%d" % (family.handle, count)))
            retval = retval.replace("[[v%d]]" % count, make_button("v", "/family/%s/down/child/%d" % (family.handle, count)))
            count += 1
        retval += make_button(_("Add New Person as Child"), (url.replace("$act", "add") % args))
        retval += make_button(_("Add Existing Person as Child"), (url.replace("$act", "share") % args))
    else:
        retval += nbsp("") # to keep tabs same height
    if has_data:
        retval += """ <SCRIPT LANGUAGE="JavaScript">setHasData("%s", 1)</SCRIPT>\n""" % cssid
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

def media_link(handle, user, act):
    retval = """<a href="%s"><img src="%s" /></a>""" % (
        "/media/%s/full" % handle, 
        "/media/%s/thumbnail" % handle)
    return retval

def render(formfield, user, act, id=None, url=None, *args):
    if not user.is_authenticated():
        act = "view"
    if act == "view": # show as text
        fieldname = formfield.name # 'surname'
        try:
            item = getattr(formfield.form.model, fieldname)
            if (item.__class__.__name__ == 'ManyRelatedManager'):
                retval = ", ".join([i.get_link() for i in item.all()])
            else:
                if url:
                    retval = """<a href="%s">%s</a>""" % (url % args, item)
                elif hasattr(item, "get_link"):
                    retval = item.get_link()
                else:
                    retval = str(item)
                #### Some cleanup:
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
    else: # show as widget
        if id != None:
            retval = formfield.as_widget(attrs={"id": id})
        else:
            retval = formfield.as_widget()
    return retval

def render_name(name, user, act=None):
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
from htmldoc import HtmlDoc 
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
    text = text.replace("&nbsp;", " ") # otherwise removes them?
    parser.feed(text)
    parser.close()
    return (parser.text(), parser.tags())

def make_log(obj, log_type, last_changed_by, reason, cache):
    """
    Makes a record of the changes performed.
    """
    # Can also add private
    last_changed = datetime.datetime.now()
    log = models.Log(referenced_by=obj,
                     log_type=log_type,
                     order=0,
                     reason=reason,
                     last_changed=last_changed,
                     last_changed_by=last_changed_by,
                     cache=cache)
    log.save()
    
