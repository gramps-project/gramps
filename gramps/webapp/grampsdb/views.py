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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Main view handlers
Each object can be operated on with the following actions:
   view: show the data
   delete: delete the object (FIXME: needs undo)
   edit: show the data in its editing widget
     save: action in the form in edit mode; write data to db
   add: show blank data in their editing widget
     create: action in the form in edit mode; add new data to db
"""

import os
import time
import pickle
import base64

#------------------------------------------------------------------------
#
# Django Modules
#
#------------------------------------------------------------------------
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import Context, RequestContext
from django.db.models import Q
from django.forms.models import modelformset_factory
import simplejson

#------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------
from gramps.version import VERSION

# Gramps-connect imports:
import gramps.webapp
from gramps.webapp.utils import _, build_args, db
from gramps.webapp.grampsdb.models import *
from gramps.webapp.grampsdb.view import *
from gramps.webapp.djangodb import DbDjango
import gramps.cli.user

# Menu: (<Nice name>, /<path>/, <Model> | None, Need authentication )
MENU = [
    (_('Browse'), 'browse', None, False),
    (_('Reports'), 'report', Report, True),
    (_('User'), 'user', None, True),
]
# Views: [(<Nice name plural>, /<name>/handle, <Model>), ]
VIEWS = [
    (_('People'), 'person', Name),
    (_('Families'), 'family', Family),
    (_('Events'), 'event', Event),
    (_('Notes'), 'note', Note),
    (_('Media'), 'media', Media),
    (_('Citations'), 'citation', Citation),
    (_('Sources'), 'source', Source),
    (_('Places'), 'place', Place),
    (_('Repositories'), 'repository', Repository),
    (_('Tags'), 'tag', Tag),
    ]

def context_processor(request):
    """
    This function is executed before template processing.
    takes a request, and returns a dictionary context.
    """
    global SITENAME
    context = {}
    if request.user.is_authenticated():
        profile = request.user.profile
        context["css_theme"] = profile.theme_type.name
    else:
        context["css_theme"] = "Web_Mainz.css"
    # Other things for all environments:
    context["gramps_version"] = VERSION
    context["views"] = VIEWS
    context["menu"] = MENU
    context["None"] = None
    context["True"] = True
    context["False"] = False
    context["sitename"] = Config.objects.get(setting="sitename").value
    context["default"] = ""

    search = request.GET.get("search", "") or request.POST.get("search", "")
    page = request.GET.get("page", "") or request.POST.get("page", "")
    context["page"] = page
    context["search"] = search
    context["args"] = build_args(search=search, page=page)
    return context

def main_page(request):
    """
    Show the main page.
    """
    context = RequestContext(request)
    context["view"] = 'home'
    context["tview"] = _('Home')
    return render_to_response("main_page.html", context)

def logout_page(request):
    """
    Logout a user.
    """
    context = RequestContext(request)
    context["view"] = 'home'
    context["tview"] = _('Home')
    logout(request)
    return HttpResponseRedirect('/')

def make_message(request, message):
    if request.user.is_authenticated():
        #request.user.message_set.create(message = message)
        print("FIXME: message_set:", message)
    else:
        request.session['message'] = message

def browse_page(request):
    """
    Show the main list under 'Browse' on the main menu.
    """
    context = RequestContext(request)
    context["view"] = 'browse'
    context["tview"] = _('Browse')
    return render_to_response('browse_page.html', context)

def user_page(request, username=None):
    """
    Show the user page.
    """
    if request.user.is_authenticated():
        if username is None:
            profile = request.user.profile
            username = profile.user.username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404(_('Requested user not found.'))
        context = RequestContext(request)
        context["username"] =  username
        context["view"] = 'user'
        context["tview"] = _('User')
        return render_to_response('user_page.html', context)
    else:
        raise Http404(_("Requested page is not accessible."))

def timestamp():
    """
    Construct a string of current time for filenames.
    """
    return time.strftime("%Y-%m-%d:%H:%M:%S")

def send_file(request, filename, mimetype):
    """
    Send a file through Django without loading the whole file into
    memory at once. The FileWrapper will turn the file object into an
    iterator for chunks of 8KB.
    """
    from django.core.servers.basehttp import FileWrapper
    wrapper = FileWrapper(open(filename, mode="rb"))
    response = HttpResponse(wrapper, content_type=mimetype)
    path, base = os.path.split(filename)
    response['Content-Length'] = os.path.getsize(filename)
    response['Content-Disposition'] = 'attachment; filename=%s' % base
    return response

def process_report_run(request, handle):
    """
    Run a report or export.
    """
    # can also use URL with %0A as newline and "=" is "=":
    # http://localhost:8000/report/ex_gpkg/run?options=off=gpkg%0Ax=10
    from gramps.webapp.reports import import_file, export_file, download
    from gramps.cli.plug import run_report
    import traceback
    if request.user.is_authenticated():
        profile = request.user.profile
        report = Report.objects.get(handle=handle)
        args = {"off": "html"} # basic defaults
        # override from given defaults in table:
        if report.options:
            for pair in str(report.options).split("\\n"):
                if "=" in pair:
                    key, value = [x.strip() for x in pair.split("=", 1)]
                    if key and value:
                        args[key] = value
        # override from options on webpage:
        if "options" in request.GET:
            options = str(request.GET.get("options"))
            if options:
                for pair in options.split("\n"): # from webpage
                    if "=" in pair:
                        key, value = [x.strip() for x in pair.split("=", 1)]
                        if key and value:
                            args[key] = value
        #############################################################################
        if report.report_type == "report":
            filename = "/tmp/%s-%s-%s.%s" % (str(profile.user.username), str(handle), timestamp(), args["off"])
            run_report(db, handle, of=filename, **args)
            mimetype = 'application/%s' % args["off"]
        elif report.report_type == "export":
            filename = "/tmp/%s-%s-%s.%s" % (str(profile.user.username), str(handle), timestamp(), args["off"])
            export_file(db, filename, gramps.cli.user.User()) # callback
            mimetype = 'text/plain'
        elif report.report_type == "import":
            filename = download(args["i"], "/tmp/%s-%s-%s.%s" % (str(profile.user.username),
                                                                 str(handle),
                                                                 timestamp(),
                                                                 args["iff"]))
            if filename is not None:
                if True: # run in background, with error handling
                    import threading
                    def background():
                        try:
                            import_file(db, filename, gramps.cli.user.User()) # callback
                        except:
                            make_message(request, "import_file failed: " + traceback.format_exc())
                    threading.Thread(target=background).start()
                    make_message(request, "Your data is now being imported...")
                    return redirect("/report/")
                else:
                    success = import_file(db, filename, gramps.cli.user.User()) # callback
                    if not success:
                        make_message(request, "Failed to load imported.")
                    return redirect("/report/")
            else:
                make_message(request, "No filename was provided or found.")
                return redirect("/report/")
        else:
            make_message(request, "Invalid report type '%s'" % report.report_type)
            return redirect("/report/")
        # need to wait for the file to exist:
        start = time.time()
        while not os.path.exists(filename):
            # but let's not wait forever:
            if time.time() - start > 10: # after 10 seconds, give up!
                context = RequestContext(request)
                make_message(request, "Failed: '%s' is not found" % filename)
                return redirect("/report/")
            time.sleep(1)
        # FIXME: the following should go into a queue for later presentation
        # like a jobs-result queue
        if filename.endswith(".html"):
            # just give it, perhaps in a new tab
            from django.http import HttpResponse
            response = HttpResponse(content_type="text/html")
            for line in open(filename, mode="rb"):
                response.write(line)
            return response
        else:
            return send_file(request, filename, mimetype)
    # If failure, just fail for now:
    context = RequestContext(request)
    context["message"] = "You need to be logged in to run reports."
    return render_to_response("main_page.html", context)

def view_list(request, view):
    """
    Borwse each of the primary tables.
    """
    context = RequestContext(request)
    search = ""
    if view == "event":
        context["tviews"] = _("Events")
        search = request.GET.get("search") if "search" in request.GET else ""
        query, order, terms = build_event_query(request, search)
        object_list = Event.objects \
            .filter(query) \
            .order_by(*order) \
            .distinct()
        view_template = 'view_events.html'
        total = Event.objects.all().count()
    elif view == "media":
        context["tviews"] = _("Media")
        search = request.GET.get("search") if "search" in request.GET else ""
        query, order, terms = build_media_query(request, search)
        object_list = Media.objects \
            .filter(query) \
            .order_by(*order) \
            .distinct()
        view_template = 'view_media.html'
        total = Media.objects.all().count()
    elif view == "note":
        context["tviews"] = _("Notes")
        search = request.GET.get("search") if "search" in request.GET else ""
        query, order, terms = build_note_query(request, search)
        object_list = Note.objects \
            .filter(query) \
            .order_by(*order) \
            .distinct()
        view_template = 'view_notes.html'
        total = Note.objects.all().count()
    elif view == "person":
        context["tviews"] = _("People")
        search = request.GET.get("search") if "search" in request.GET else ""
        query, order, terms = build_person_query(request, search)
        object_list = Name.objects \
            .filter(query) \
            .order_by(*order) \
            .distinct()
        view_template = 'view_people.html'
        total = Name.objects.all().count()
    elif view == "family":
        context["tviews"] = _("Families")
        search = request.GET.get("search") if "search" in request.GET else ""
        query, order, terms = build_family_query(request, search)
        object_list = Family.objects \
            .filter(query) \
            .order_by(*order) \
            .distinct()
        view_template = 'view_families.html'
        total = Family.objects.all().count()
    elif view == "place":
        context["tviews"] = _("Places")
        search = request.GET.get("search") if "search" in request.GET else ""
        query, order, terms = build_place_query(request, search)
        object_list = Place.objects \
            .filter(query) \
            .order_by(*order) \
            .distinct()
        view_template = 'view_places.html'
        total = Place.objects.all().count()
    elif view == "repository":
        context["tviews"] = _("Repositories")
        search = request.GET.get("search") if "search" in request.GET else ""
        query, order, terms = build_repository_query(request, search)
        object_list = Repository.objects \
            .filter(query) \
            .order_by(*order) \
            .distinct()
        view_template = 'view_repositories.html'
        total = Repository.objects.all().count()
    elif view == "citation":
        context["tviews"] = _("Citations")
        search = request.GET.get("search") if "search" in request.GET else ""
        query, order, terms = build_citation_query(request, search)
        object_list = Citation.objects \
            .filter(query) \
            .order_by(*order) \
            .distinct()
        view_template = 'view_citations.html'
        total = Citation.objects.all().count()
    elif view == "source":
        context["tviews"] = _("Sources")
        search = request.GET.get("search") if "search" in request.GET else ""
        query, order, terms = build_source_query(request, search)
        object_list = Source.objects \
            .filter(query) \
            .order_by(*order) \
            .distinct()
        view_template = 'view_sources.html'
        total = Source.objects.all().count()
    elif view == "tag":
        context["tviews"] = _("Tags")
        search = request.GET.get("search") if "search" in request.GET else ""
        query, order, terms = build_tag_query(request, search)
        object_list = Tag.objects \
            .filter(query) \
            .order_by(*order) \
            .distinct()
        view_template = 'view_tags.html'
        total = Tag.objects.all().count()
    elif view == "report":
        context["tviews"] = _("Reports")
        search = request.GET.get("search") if "search" in request.GET else ""
        query, order, terms = build_report_query(request, search)
        object_list = Report.objects \
            .filter(query) \
            .order_by(*order) \
            .distinct()
        view_template = 'view_report.html'
        total = Report.objects.all().count()
    else:
        raise Http404("Requested page type '%s' not known" % view)

    if request.user.is_authenticated():
        paginator = Paginator(object_list, 20)
    else:
        paginator = Paginator(object_list, 20)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)

    context["search_terms"] = ", ".join(terms) + "; ^start, end$"
    context["page"] = page
    context["view"] = view
    context["tview"] = _(view.title())
    context["search"] = search
    context["total"] = total
    context["object_list"] = object_list
    context["next"] = "/%s/" % view
    if search:
        context["search_query"] = ("&search=%s" % search)
    else:
        context["search_query"] = ""
    return render_to_response(view_template, context)

def check_access(request, context, obj, act):
    """
    Check to see if user has access to object. We don't need to
    sanitize here, just check to see if we even acknowledge it exists.
    """
    if request.user.is_authenticated():
        if request.user.is_superuser:
            return True
        else:
            return act in ["view"]
    else: # outside viewer
        return not obj.private

def add_share(request, view, item, handle):
    """
    Add a new <view> referenced from <item>.
    """
    # /person/share/family/handle
    # Use an existing person with this family
    # r'^(?P<view>(\w+))/share/(?P<item>(\w+))/(?P<handle>(\w+))$',
    act = "share"
    if "action" in request.POST:
        act = request.POST.get("action") # can be "save-share"
    return action(request, view, None, act, (item, handle))

def add_to(request, view, item, handle):
    """
    Add a new <view> referenced from <item>.
    """
    # /view/add/person/handle
    # /family/add/child/handle
    return action(request, view, None, "add", (item, handle))

def action(request, view, handle, act, add_to=None):
    """
    View a particular object given /object/handle (implied view),
    /object/handle/action, or /object/add.
    """
    from gramps.webapp.reports import get_plugin_options
    # redirect:
    rd = None
    obj = None
    context = RequestContext(request)
    if "action" in request.POST:
        act = request.POST.get("action")
    context["action"] = act
    context["view"] = view
    context["tview"] = _('Browse')
    if view == "event":
        if act not in ["add", "create", "share", "save-share"]:
            try:
                obj = Event.objects.get(handle=handle)
            except:
                raise Http404(_("Requested %s does not exist.") % view)
        if not check_access(request, context, obj, act):
            raise Http404(_("Requested %s does not exist.") % view)
        if "format" in request.GET:
            if request.GET["format"] == "json":
                item = db.get_event_from_handle(obj.handle)
                content = str(item.to_struct())
                response = HttpResponse(content, content_type="application/json")
                return response
        view_template = 'view_event_detail.html'
        rd = process_event(request, context, handle, act, add_to)
    elif view == "family":
        if act not in ["add", "create", "share", "save-share"]:
            try:
                obj = Family.objects.get(handle=handle)
            except:
                raise Http404(_("Requested %s does not exist.") % view)
        if not check_access(request, context, obj, act):
            raise Http404(_("Requested %s does not exist.") % view)
        if "format" in request.GET:
            if request.GET["format"] == "json":
                item = db.get_family_from_handle(obj.handle)
                content = str(item.to_struct())
                response = HttpResponse(content, content_type="application/json")
                return response
        view_template = 'view_family_detail.html'
        rd = process_family(request, context, handle, act, add_to)
    elif view == "media":
        if act not in ["add", "create", "share", "save-share"]:
            try:
                obj = Media.objects.get(handle=handle)
            except:
                raise Http404(_("Requested %s does not exist.") % view)
        if not check_access(request, context, obj, act):
            raise Http404(_("Requested %s does not exist.") % view)
        if "format" in request.GET:
            if request.GET["format"] == "json":
                item = db.get_media_from_handle(obj.handle)
                content = str(item.to_struct())
                response = HttpResponse(content, content_type="application/json")
                return response
        view_template = 'view_media_detail.html'
        rd = process_media(request, context, handle, act, add_to)
    elif view == "note":
        if act not in ["add", "create", "share", "save-share"]:
            try:
                obj = Note.objects.get(handle=handle)
            except:
                raise Http404(_("Requested %s does not exist.") % view)
        if not check_access(request, context, obj, act):
            raise Http404(_("Requested %s does not exist.") % view)
        if "format" in request.GET:
            if request.GET["format"] == "json":
                item = db.get_note_from_handle(obj.handle)
                content = str(item.to_struct())
                response = HttpResponse(content, content_type="application/json")
                return response
        view_template = 'view_note_detail.html'
        rd = process_note(request, context, handle, act, add_to)
    elif view == "person":
        if act not in ["add", "create", "share", "save-share"]:
            try:
                obj = Person.objects.get(handle=handle)
            except:
                raise Http404(_("Requested %s does not exist.") % view)
        if not check_access(request, context, obj, act):
            raise Http404(_("Requested %s does not exist.") % view)
        if "format" in request.GET:
            if request.GET["format"] == "json":
                person = db.get_person_from_handle(obj.handle)
                content = str(person.to_struct())
                response = HttpResponse(content, content_type="application/json")
                return response
        view_template = 'view_person_detail.html'
        rd = process_person(request, context, handle, act, add_to)
    elif view == "place":
        if act not in ["add", "create", "share", "save-share"]:
            try:
                obj = Place.objects.get(handle=handle)
            except:
                raise Http404(_("Requested %s does not exist.") % view)
        if not check_access(request, context, obj, act):
            raise Http404(_("Requested %s does not exist.") % view)
        if "format" in request.GET:
            if request.GET["format"] == "json":
                item = db.get_place_from_handle(obj.handle)
                content = str(item.to_struct())
                response = HttpResponse(content, content_type="application/json")
                return response
        view_template = 'view_place_detail.html'
        rd = process_place(request, context, handle, act, add_to)
    elif view == "repository":
        if act not in ["add", "create", "share", "save-share"]:
            try:
                obj = Repository.objects.get(handle=handle)
            except:
                raise Http404(_("Requested %s does not exist.") % view)
        if not check_access(request, context, obj, act):
            raise Http404(_("Requested %s does not exist.") % view)
        if "format" in request.GET:
            if request.GET["format"] == "json":
                item = db.get_repository_from_handle(obj.handle)
                content = str(item.to_struct())
                response = HttpResponse(content, content_type="application/json")
                return response
        view_template = 'view_repository_detail.html'
        rd = process_repository(request, context, handle, act, add_to)
    elif view == "citation":
        if act not in ["add", "create", "share", "save-share"]:
            try:
                obj = Citation.objects.get(handle=handle)
            except:
                raise Http404(_("Requested %s does not exist.") % view)
        if not check_access(request, context, obj, act):
            raise Http404(_("Requested %s does not exist.") % view)
        if "format" in request.GET:
            if request.GET["format"] == "json":
                item = db.get_citation_from_handle(obj.handle)
                content = str(item.to_struct())
                response = HttpResponse(content, content_type="application/json")
                return response
        view_template = 'view_citation_detail.html'
        rd = process_citation(request, context, handle, act, add_to)
    elif view == "source":
        if act not in ["add", "create", "share", "save-share"]:
            try:
                obj = Source.objects.get(handle=handle)
            except:
                raise Http404(_("Requested %s does not exist.") % view)
        if not check_access(request, context, obj, act):
            raise Http404(_("Requested %s does not exist.") % view)
        if "format" in request.GET:
            if request.GET["format"] == "json":
                item = db.get_source_from_handle(obj.handle)
                content = str(item.to_struct())
                response = HttpResponse(content, content_type="application/json")
                return response
        view_template = 'view_source_detail.html'
        rd = process_source(request, context, handle, act, add_to)
    elif view == "tag":
        if act not in ["add", "create", "share", "save-share"]:
            try:
                obj = Tag.objects.get(handle=handle)
            except:
                raise Http404(_("Requested %s does not exist.") % view)
        if not check_access(request, context, obj, act):
            raise Http404(_("Requested %s does not exist.") % view)
        if "format" in request.GET:
            if request.GET["format"] == "json":
                item = db.get_tag_from_handle(obj.handle)
                content = str(item.to_struct())
                response = HttpResponse(content, content_type="application/json")
                return response
        view_template = 'view_tag_detail.html'
        rd = process_tag(request, context, handle, act, add_to)
    elif view == "report":
        if act not in ["add", "create"]:
            try:
                obj = Report.objects.get(handle=handle)
            except:
                raise Http404(_("Requested %s does not exist.") % view)
        override = {}
        if obj.options:
            for pair in obj.options.split("\\n"):
                key, value = pair.split("=", 1)
                override[key] = value
        opt_default, opt_help = get_plugin_options(db, obj.handle)
        retval = ""
        for key in sorted(opt_default.keys()):
            if key in override:
                retval += "%s=%s\n" % (key, override[key])
                del override[key]
            else:
                retval += "%s=%s\n" % (key, opt_default[key])
        # Any leftover overrides:
        for key in sorted(override.keys()):
            retval += "%s=%s\n" % (key, override[key])
        obj.options = retval
        retval = "<ol>"
        for key in sorted(opt_help.keys()):
            retval += "<li><b>%s</b>: %s</li>\n" % (key, opt_help[key][1])
        retval += "</ol>"
        context["help"] = retval
        view_template = 'view_report_detail.html'
        rd = process_report(request, context, handle, act)
    else:
        raise Http404(_("Requested page type not known"))
    if rd:
        return rd
    if obj:
        context[view] = obj
        context["object"] = obj
        context["next"] = "/%s/%s" % (view, obj.handle)
    return render_to_response(view_template, context)

def process_report(request, context, handle, act):
    """
    Process action on report. Can return a redirect.
    """
    if act == "run":
        return process_report_run(request, handle)
    context["tview"] = _("Report")
    context["tviews"] = _("Reports")

def build_string_query(field, value, exact=False, startswith=False, endswith=False):
    retval = None
    if exact:
        retval = Q(**{"%s" % field: value})
    elif startswith:
        retval = Q(**{"%s__istartswith" % field: value})
    elif endswith:
        retval = Q(**{"%s__iendswith" % field: value})
    else: # default
        retval = Q(**{"%s__icontains" % field: value})
    return retval

def build_person_query(request, search):
    """
    Build and return a Django QuerySet and sort order for the Person
    table.
    """
    protect = not request.user.is_authenticated()
    ### Build the order:
    if protect:
        # Do this to get the names sorted by private/alive
        # NOTE: names can be private
        terms = ["surname", "given", "id", "tag"]
        query = Q(private=False) & Q(person__private=False)
        order = ["surname__surname", "private", "person__probably_alive",
                 "first_name"]
    else:
        terms = ["surname", "given", "id", "tag", "public", "private"]
        query = Q()
        order = ["surname__surname", "first_name"]
    ### Build the query:
    if search:
        if "[" in search: # "Surname, Given [I0002]" to match Flexbox and obj.get_select_string()
            search = search.replace("[", ", id=^")
            search = search.replace("]", "$")
        if "," in search or "=" in search:
            for term in [term.strip() for term in search.split(",")]:
                startswith = False
                endswith = False
                exact = False
                if "=" in term:
                    field, value = [s.strip() for s in term.split("=")]
                else:
                    if terms:
                        field = terms.pop(0)
                        value = term
                    else:
                        continue
                if value.startswith("^"):
                    startswith = True
                    value = value[1:]
                if value.endswith("$"):
                    endswith = True
                    value = value[:-1]
                if startswith and endswith:
                    exact = True
                if "." in field and not protect:
                    query &= build_string_query(field.replace(".", "__"), value, exact, startswith, endswith)
                elif field == "surname":
                    query &= build_string_query("surname__surname", value, exact, startswith, endswith)
                elif field == "given":
                    if protect:
                        query &= build_string_query("first_name", value, exact, startswith, endswith) & Q(person__probably_alive=False)
                    else:
                        query &= build_string_query("first_name", value, exact, startswith, endswith)
                elif field == "private":
                    if not protect:
                        query &= Q(person__private=boolean(value))
                elif field == "public":
                    if not protect:
                        query &= Q(person__public=boolean(value))
                elif field == "birth":
                    if protect:
                        query &= Q(person__birth__year1=safe_int(value)) & Q(person__probably_alive=False)
                    else:
                        query &= Q(person__birth__year1=safe_int(value))
                elif field == "death":
                    if protect:
                        query &= Q(person__death__year1=safe_int(value)) & Q(person__probably_alive=False)
                    else:
                        query &= Q(person__death__year1=safe_int(value))
                elif field == "id":
                    query &= build_string_query("person__gramps_id", value, exact, startswith, endswith)
                elif field == "gender":
                    query &= Q(person__gender_type__name=value.title())
                elif field == "tag":
                    query &= build_string_query("person__tags__name", value, exact, startswith, endswith)
                else:
                    make_message(request, "Invalid query field '%s'" % field)
        else: # no search fields, just raw search
            if protect:
                query &= (Q(surname__surname__icontains=search) |
                              Q(surname__prefix__icontains=search) |
                              Q(person__gramps_id__icontains=search))
            else:
                query &= (Q(surname__surname__icontains=search) |
                              Q(first_name__icontains=search) |
                              Q(suffix__icontains=search) |
                              Q(surname__prefix__icontains=search) |
                              Q(title__icontains=search) |
                              Q(person__gramps_id__icontains=search))
    else: # no search
        pass # nothing else to do
    #make_message(request, query)
    return query, order, terms

def build_family_query(request, search):
    """
    Build and return a Django QuerySet and sort order for the Family
    table.
    """
    protect = not request.user.is_authenticated()
    if protect:
        terms = ["father", "mother", "id", "type", "surnames", "tag"]
        query = (Q(private=False) & Q(father__private=False) &
                 Q(mother__private=False))
        order = ["father__name__surname__surname",
                 "father__private", "father__probably_alive",
                 "father__name__first_name",
                 "mother__name__surname__surname",
                 "mother__private", "mother__probably_alive",
                 "mother__name__first_name"]
    else:
        terms = ["father", "mother", "id", "type", "surnames", "father.name.first_name",
                 "mother.name.first_name", "tag", "public", "private"]
        query = Q()
        order = ["father__name__surname__surname",
                 "father__name__first_name",
                 "mother__name__surname__surname",
                 "mother__name__first_name"]
    if search:
        if "," in search or "=" in search:
            for term in [term.strip() for term in search.split(",")]:
                startswith = False
                endswith = False
                exact = False
                if "=" in term:
                    field, value = [s.strip() for s in term.split("=")]
                else:
                    if terms:
                        field = terms.pop(0)
                        value = term
                    else:
                        make_message("Ignoring value without specified field")
                        continue
                if value.startswith("^"):
                    startswith = True
                    value = value[1:]
                if value.endswith("$"):
                    endswith = True
                    value = value[:-1]
                if startswith and endswith:
                    exact = True
                if "." in field and not protect:
                    query &= build_string_query(field.replace(".", "__"), value, exact, startswith, endswith)
                elif field == "surnames":
                    query &= (build_string_query("father__name__surname__surname", value, exact, startswith, endswith) |
                              build_string_query("mother__name__surname__surname", value, exact, startswith, endswith))
                elif field == "father":
                    query &= build_string_query("father__name__surname__surname", value, exact, startswith, endswith)
                elif field == "mother":
                    query &= build_string_query("mother__name__surname__surname", value, exact, startswith, endswith)
                elif field == "type":
                    query &= build_string_query("family_rel_type__name", value, exact, startswith, endswith)
                elif field == "id":
                    query &= build_string_query("gramps_id", value, exact, startswith, endswith)
                elif field == "tag":
                    query &= build_string_query("tags__name", value, exact, startswith, endswith)
                elif field == "private":
                    query &= Q(private=boolean(value))
                elif field == "public":
                    query &= Q(public=boolean(value))
                else:
                    make_message(request, message="Invalid query field '%s'" % field)
        else: # no search fields, just raw search
            if protect: # need to protect!
                query &= (Q(gramps_id__icontains=search) |
                          Q(family_rel_type__name__icontains=search) |
                          Q(father__name__surname__surname__icontains=search) |
                          Q(father__name__first_name__icontains=search) |
                          Q(mother__name__surname__surname__icontains=search) |
                          Q(mother__name__first_name__icontains=search))
            else:
                query &= (Q(gramps_id__icontains=search) |
                          Q(family_rel_type__name__icontains=search) |
                          Q(father__name__surname__surname__icontains=search) |
                          Q(father__name__first_name__icontains=search) |
                          Q(mother__name__surname__surname__icontains=search) |
                          Q(mother__name__first_name__icontains=search))
    else: # no search
        pass # nothing left to do
    #make_message(request, query)
    return query, order, terms

def build_media_query(request, search):
    terms = ["id", "path", "description", "mime", "tag", "public", "private"]
    protect = not request.user.is_authenticated()
    if protect:
        query = Q(private=False) # general privacy
        order = ["gramps_id"]
    else:
        query = Q()
        order = ["gramps_id"]
    if search:
        if "," in search or "=" in search:
            for term in [term.strip() for term in search.split(",")]:
                startswith = False
                endswith = False
                exact = False
                if "=" in term:
                    field, value = [s.strip() for s in term.split("=")]
                else:
                    if terms:
                        field = terms.pop(0)
                        value = term
                    else:
                        continue
                if value.startswith("^"):
                    startswith = True
                    value = value[1:]
                if value.endswith("$"):
                    endswith = True
                    value = value[:-1]
                if startswith and endswith:
                    exact = True
                if "." in field and not protect:
                    query &= build_string_query(field.replace(".", "__"), value, exact, startswith, endswith)
                elif field == "id":
                    query &= build_string_query("gramps_id", value, exact, startswith, endswith)
                elif field == "path":
                    query &= build_string_query("path", value, exact, startswith, endswith)
                elif field == "description":
                    query &= build_string_query("desc", value, exact, startswith, endswith)
                elif field == "mime":
                    query &= build_string_query("mime", value, exact, startswith, endswith)
                elif field == "tag":
                    query &= build_string_query("tags__name", value, exact, startswith, endswith)
                elif field == "private":
                    query &= Q(private=boolean(value))
                elif field == "public":
                    query &= Q(public=boolean(value))
                else:
                    request.user.message_set.create(message="Invalid query field '%s'" % field)
        else: # no search fields, just raw search
            if protect:
                query &= (Q(gramps_id__icontains=search) |
                          Q(path__icontains=search) |
                          Q(desc__icontains=search) |
                          Q(mime__icontains=search))
            else:
                query &= (Q(gramps_id__icontains=search) |
                          Q(path__icontains=search) |
                          Q(desc__icontains=search) |
                          Q(mime__icontains=search))
    else: # no search
        pass # nothing left to do
    return query, order, terms

def build_note_query(request, search):
    terms = ["id", "type", "text", "tag", "public", "private"]
    protect = not request.user.is_authenticated()
    if protect:
        query = Q(private=False) # general privacy
        order = ["gramps_id"]
    else:
        query = Q()
        order = ["gramps_id"]
    if search:
        if "," in search or "=" in search:
            for term in [term.strip() for term in search.split(",")]:
                startswith = False
                endswith = False
                exact = False
                if "=" in term:
                    field, value = [s.strip() for s in term.split("=")]
                else:
                    if terms:
                        field = terms.pop(0)
                        value = term
                    else:
                        continue
                if value.startswith("^"):
                    startswith = True
                    value = value[1:]
                if value.endswith("$"):
                    endswith = True
                    value = value[:-1]
                if startswith and endswith:
                    exact = True
                if "." in field and not protect:
                    query &= build_string_query(field.replace(".", "__"), value, exact, startswith, endswith)
                elif field == "id":
                    query &= build_string_query("gramps_id", value, exact, startswith, endswith)
                elif field == "type":
                    query &= build_string_query("note_type__name", value, exact, startswith, endswith)
                elif field == "text":
                    query &= build_string_query("text", value, exact, startswith, endswith)
                elif field == "tag":
                    query &= build_string_query("tags__name", value, exact, startswith, endswith)
                elif field == "private":
                    query &= Q(private=boolean(value))
                elif field == "public":
                    query &= Q(public=boolean(value))
                else:
                    request.user.message_set.create(message="Invalid query field '%s'" % field)
        else: # no search fields, just raw search
            if protect:
                query &= (Q(gramps_id__icontains=search) |
                          Q(note_type__name__icontains=search) |
                          Q(text__icontains=search))
            else:
                query &= (Q(gramps_id__icontains=search) |
                          Q(note_type__name__icontains=search) |
                          Q(text__icontains=search))
    else: # no search
        pass # nothing left to do
    return query, order, terms

def build_place_query(request, search):
    terms = ["title", "id", "public", "private"]
    protect = not request.user.is_authenticated()
    if protect:
        query = Q(private=False) # general privacy
        order = ["gramps_id"]
    else:
        query = Q()
        order = ["gramps_id"]
    if search:
        if "[" in search: # "Place [I0002]" to match Flexbox and obj.get_select_string()
            search = search.replace("[", "; id=^")
            search = search.replace("]", "$")
        if ";" in search or "=" in search:
            for term in [term.strip() for term in search.split(";")]:
                startswith = False
                endswith = False
                exact = False
                if "=" in term:
                    field, value = [s.strip() for s in term.split("=")]
                else:
                    if terms:
                        field = terms.pop(0)
                        value = term
                    else:
                        continue
                if value.startswith("^"):
                    startswith = True
                    value = value[1:]
                if value.endswith("$"):
                    endswith = True
                    value = value[:-1]
                if startswith and endswith:
                    exact = True
                if "." in field and not protect:
                    query &= build_string_query(field.replace(".", "__"), value, exact, startswith, endswith)
                elif field == "id":
                    query &= build_string_query("gramps_id", value, exact, startswith, endswith)
                elif field == "title":
                    query &= build_string_query("title", value, exact, startswith, endswith)
                elif field == "private":
                    query &= Q(private=boolean(value))
                elif field == "public":
                    query &= Q(public=boolean(value))
                else:
                    request.user.message_set.create(message="Invalid query field '%s'" % field)
        else: # no search fields, just raw search
            if protect:
                query &= (Q(gramps_id__icontains=search) |
                          Q(title__icontains=search))
            else:
                query &= (Q(gramps_id__icontains=search) |
                          Q(title__icontains=search))
    else: # no search
        pass # nothing left to do
    return query, order, terms

def build_repository_query(request, search):
    terms = ["id", "name", "type", "public", "private"]
    protect = not request.user.is_authenticated()
    if protect:
        query = Q(private=False) # general privacy
        order = ["gramps_id"]
    else:
        query = Q()
        order = ["gramps_id"]
    if search:
        if "," in search or "=" in search:
            for term in [term.strip() for term in search.split(",")]:
                startswith = False
                endswith = False
                exact = False
                if "=" in term:
                    field, value = [s.strip() for s in term.split("=")]
                else:
                    if terms:
                        field = terms.pop(0)
                        value = term
                    else:
                        continue
                if value.startswith("^"):
                    startswith = True
                    value = value[1:]
                if value.endswith("$"):
                    endswith = True
                    value = value[:-1]
                if startswith and endswith:
                    exact = True
                if "." in field and not protect:
                    query &= build_string_query(field.replace(".", "__"), value, exact, startswith, endswith)
                elif field == "id":
                    query &= build_string_query("gramps_id", value, exact, startswith, endswith)
                elif field == "name":
                    query &= build_string_query("name", value, exact, startswith, endswith)
                elif field == "type":
                    query &= build_string_query("repository_type__name", value, exact, startswith, endswith)
                elif field == "private":
                    query &= Q(private=boolean(value))
                elif field == "public":
                    query &= Q(public=boolean(value))
                else:
                    request.user.message_set.create(message="Invalid query field '%s'" % field)
        else: # no search fields, just raw search
            if protect:
                query &= (Q(gramps_id__icontains=search) |
                          Q(name__icontains=search) |
                          Q(repository_type__name__icontains=search)
                          )
            else:
                query &= (Q(gramps_id__icontains=search) |
                          Q(name__icontains=search) |
                          Q(repository_type__name__icontains=search)
                          )
    else: # no search
        pass # nothing left to do
    return query, order, terms

def build_citation_query(request, search):
    terms = ["id", "private", "public"]
    protect = not request.user.is_authenticated()
    if protect:
        query = Q(private=False) # general privacy
        order = ["gramps_id"]
    else:
        query = Q()
        order = ["gramps_id"]
    if search:
        if "," in search or "=" in search:
            for term in [term.strip() for term in search.split(",")]:
                startswith = False
                endswith = False
                exact = False
                if "=" in term:
                    field, value = [s.strip() for s in term.split("=")]
                else:
                    if terms:
                        field = terms.pop(0)
                        value = term
                    else:
                        continue
                if value.startswith("^"):
                    startswith = True
                    value = value[1:]
                if value.endswith("$"):
                    endswith = True
                    value = value[:-1]
                if startswith and endswith:
                    exact = True
                if "." in field and not protect:
                    query &= build_string_query(field.replace(".", "__"), value, exact, startswith, endswith)
                elif field == "id":
                    query &= build_string_query("gramps_id", value, exact, startswith, endswith)
                elif field == "private":
                    query &= Q(private=boolean(value))
                elif field == "public":
                    query &= Q(public=boolean(value))
                else:
                    request.user.message_set.create(message="Invalid query field '%s'" % field)
        else: # no search fields, just raw search
            if protect:
                query &= (Q(gramps_id__icontains=search))
            else:
                query &= (Q(gramps_id__icontains=search))
    else: # no search
        pass # nothing left to do
    return query, order, terms

def build_source_query(request, search):
    terms = ["id", "private", "public"]
    protect = not request.user.is_authenticated()
    if protect:
        query = Q(private=False) # general privacy
        order = ["gramps_id"]
    else:
        query = Q()
        order = ["gramps_id"]
    if search:
        if "," in search or "=" in search:
            for term in [term.strip() for term in search.split(",")]:
                startswith = False
                endswith = False
                exact = False
                if "=" in term:
                    field, value = [s.strip() for s in term.split("=")]
                else:
                    if terms:
                        field = terms.pop(0)
                        value = term
                    else:
                        continue
                if value.startswith("^"):
                    startswith = True
                    value = value[1:]
                if value.endswith("$"):
                    endswith = True
                    value = value[:-1]
                if startswith and endswith:
                    exact = True
                if "." in field and not protect:
                    query &= build_string_query(field.replace(".", "__"), value, exact, startswith, endswith)
                elif field == "id":
                    query &= build_string_query("gramps_id", value, exact, startswith, endswith)
                elif field == "private":
                    query &= Q(private=boolean(value))
                elif field == "public":
                    query &= Q(public=boolean(value))
                else:
                    request.user.message_set.create(message="Invalid query field '%s'" % field)
        else: # no search fields, just raw search
            if protect:
                query &= Q(gramps_id__icontains=search)
            else:
                query &= Q(gramps_id__icontains=search)
    else: # no search
        pass # nothing left to do
    return query, order, terms

def build_tag_query(request, search):
    terms = ["name"]
    protect = not request.user.is_authenticated()
    if protect:
        query = Q() # general privacy
        order = ["name"]
    else:
        query = Q()
        order = ["name"]
    if search:
        if "," in search or "=" in search:
            for term in [term.strip() for term in search.split(",")]:
                startswith = False
                endswith = False
                exact = False
                if "=" in term:
                    field, value = [s.strip() for s in term.split("=")]
                else:
                    if terms:
                        field = terms.pop(0)
                        value = term
                    else:
                        continue
                if value.startswith("^"):
                    startswith = True
                    value = value[1:]
                if value.endswith("$"):
                    endswith = True
                    value = value[:-1]
                if startswith and endswith:
                    exact = True
                if "." in field and not protect:
                    query &= build_string_query(field.replace(".", "__"), value, exact, startswith, endswith)
                elif field == "name":
                    query &= Q(name__icontains=value)
                else:
                    request.user.message_set.create(message="Invalid query field '%s'" % field)
        else: # no search fields, just raw search
            if protect:
                query &= Q(name__icontains=search)
            else:
                query &= Q(name__icontains=search)
    else: # no search
        pass # nothing left to do
    return query, order, terms

def build_report_query(request, search):
    terms = ["name"]
    # NOTE: protection is based on super_user status
    protect = not request.user.is_superuser
    if protect:
        query = ~Q(report_type="import") # general privacy
        order = ["name"]
    else:
        query = Q()
        order = ["name"]
    if search:
        if "," in search or "=" in search:
            for term in [term.strip() for term in search.split(",")]:
                startswith = False
                endswith = False
                exact = False
                if "=" in term:
                    field, value = [s.strip() for s in term.split("=")]
                else:
                    if terms:
                        field = terms.pop(0)
                        value = term
                    else:
                        continue
                if value.startswith("^"):
                    startswith = True
                    value = value[1:]
                if value.endswith("$"):
                    endswith = True
                    value = value[:-1]
                if startswith and endswith:
                    exact = True
                if "." in field and not protect:
                    query &= build_string_query(field.replace(".", "__"), value, exact, startswith, endswith)
                elif field == "name":
                    query &= Q(name__icontains=value)
                else:
                    request.user.message_set.create(message="Invalid query field '%s'" % field)
        else: # no search fields, just raw search
            if protect:
                query &= Q(name__icontains=search)
            else:
                query &= Q(name__icontains=search)
    else: # no search
        pass # nothing left to do
    return query, order, terms

def build_event_query(request, search):
    terms = ["id", "type", "place", "description", "private", "public"]
    protect = not request.user.is_authenticated()
    if protect:
        query = Q(private=False) # general privacy
        order = ["gramps_id"]
    else:
        query = Q()
        order = ["gramps_id"]
    if search:
        if "," in search or "=" in search:
            for term in [term.strip() for term in search.split(",")]:
                startswith = False
                endswith = False
                exact = False
                if "=" in term:
                    field, value = [s.strip() for s in term.split("=")]
                else:
                    if terms:
                        field = terms.pop(0)
                        value = term
                    else:
                        continue
                if value.startswith("^"):
                    startswith = True
                    value = value[1:]
                if value.endswith("$"):
                    endswith = True
                    value = value[:-1]
                if startswith and endswith:
                    exact = True
                if "." in field and not protect:
                    query &= build_string_query(field.replace(".", "__"), value, exact, startswith, endswith)
                elif field == "id":
                    query &= build_string_query("gramps_id", value, exact, startswith, endswith)
                elif field == "description":
                    query &= build_string_query("description", value, exact, startswith, endswith)
                elif field == "type":
                    query &= build_string_query("event_type__name", value, exact, startswith, endswith)
                elif field == "place":
                    query &= build_string_query("place__title", value, exact, startswith, endswith)
                elif field == "private":
                    query &= Q(private=boolean(value))
                elif field == "public":
                    query &= Q(public=boolean(value))
                else:
                    request.user.message_set.create(message="Invalid query field '%s'" % field)
        else: # no search fields, just raw search
            if protect:
                query &= (Q(gramps_id__icontains=search) |
                          Q(description__icontains=search) |
                          Q(event_type__name__icontains=search) |
                          Q(place__title__icontains=search))
            else:
                query &= (Q(gramps_id__icontains=search) |
                          Q(description__icontains=search) |
                          Q(event_type__name__icontains=search) |
                          Q(place__title__icontains=search))
    else: # no search
        pass # nothing left to do
    return query, order, terms

def safe_int(num):
    """
    Safely try to convert num to an integer. Return -1 (which should
    not match).
    """
    try:
        return int(num)
    except:
        return -1

def process_reference(request, ref_by, handle, ref_to, order):
    # FIXME: can I make this work for all?
    context = RequestContext(request)
    ref_by_class = dji.get_model(ref_by)
    referenced_by = ref_by_class.objects.get(handle=handle)
    object_type = ContentType.objects.get_for_model(referenced_by)
    ref_to_class = dji.get_model("%sRef" % ref_to.title())
    exclude = ["last_changed_by", "last_changed", "object_type", "object_id", "ref_object"]
    if order == "new":
        referenced_to = ref_to_class.objects.filter(object_id=referenced_by.id,
                                                    object_type=object_type,
                                                    order=0)
        form = modelformset_factory(ref_to_class, exclude=exclude, extra=1)(queryset=referenced_to)
    else:
        referenced_to = ref_to_class.objects.filter(object_id=referenced_by.id,
                                                    object_type=object_type,
                                                    order=order)
        form = modelformset_factory(ref_to_class, exclude=exclude, extra=0)(queryset=referenced_to)
        form.model = referenced_to[0]
    context["form"] = form
    context["view"] = 'reference'
    context["tview"] = _('Reference')
    context["tviews"] = _('References')
    context["object"] = referenced_by
    context["handle"] = referenced_by.handle
    context["url"] = referenced_to[0].get_reference_to().get_url()
    #"/%s/%s" % (referenced_to[0].ref_object.__class__.__name__.lower(),
    #                             referenced_to[0].ref_object.handle)
    context["referenced_by"] = "/%s/%s" % (referenced_by.__class__.__name__.lower(),
                                           referenced_by.handle)
    context["action"] = "view"
    return render_to_response("reference.html", context)

def process_child(request, handle, act, child):
    """
    handle - Family handle
    act - 'remove', 'up', or 'down'
    child - child number
    """
    family = Family.objects.get(handle=handle)
    obj_type = ContentType.objects.get_for_model(family)
    childrefs = dji.ChildRef.filter(object_id=family.id,
                                    object_type=obj_type).order_by("order")

    # FIXME: what about parent_families, families?
    if act == "remove":
        person = childrefs[int(child) - 1].ref_object
        [f.delete() for f in person.parent_families.filter(handle=handle)]
        childrefs[int(child) - 1].delete()
        dji.rebuild_cache(person)
        dji.rebuild_cache(family)
        # FIXME: renumber order after delete
    elif act == "up":
        if int(child) >= 2:
            for ref in childrefs:
                if ref.order == int(child):
                    ref.order = ref.order - 1
                elif ref.order == int(child) - 1:
                    ref.order = ref.order + 1
                else:
                    ref.order = ref.order
            for ref in childrefs:
                ref.save()
            dji.rebuild_cache(family)
    elif act == "down":
        if int(child) <= len(childrefs) - 1:
            childrefs[int(child) - 1].order = int(child) + 1
            childrefs[int(child)].order = int(child)
            childrefs[int(child) - 1].save()
            childrefs[int(child)].save()
            dji.rebuild_cache(family)
    else:
        raise Exception("invalid child action: %s" % act)
    return redirect("/family/%s/" % handle)

def process_list_item(request, view, handle, act, item, index):
    # /person/872323636232635/remove/event/1
    # /family/872323636232635/up/citation/1
    # /citation/872323636232635/down/attribute/2
    index = int(index)
    tab = {
        "eventref":       "#tab-events",
        "citationref":    "#tab-citations",
        "repositoryref":  "#tab-repositories",
        "noteref":        "#tab-notes",
        "attribute":      "#tab-attributes",
        "media":          "#tab-media",
        "lds":            "#tab-lds",
        "parentfamily":   "#tab-references",
        "family":         "#tab-references",
        }
    if view == "person":
        obj = dji.Person.get(handle=handle)
    elif view == "event":
        obj = dji.Event.get(handle=handle)
    elif view == "family":
        obj = dji.Family.get(handle=handle)
    elif view == "citation":
        obj = dji.Citation.get(handle=handle)
    elif view == "source":
        obj = dji.Source.get(handle=handle)
    else:
        raise Exception("add '%s' to list" % view)
    obj_type = ContentType.objects.get_for_model(obj)
    # Next, get reference
    if item == "eventref":
        refs = dji.EventRef.filter(object_id=obj.id,
                                   object_type=obj_type).order_by("order")
    elif item == "citationref":
        refs = dji.CitationRef.filter(object_id=obj.id,
                                      object_type=obj_type).order_by("order")
    elif item == "repositoryref":
        refs = dji.RepositoryRef.filter(object_id=obj.id,
                                        object_type=obj_type).order_by("order")
    elif item == "noteref":
        refs = dji.NoteRef.filter(object_id=obj.id,
                                  object_type=obj_type).order_by("order")
    elif item == "parentfamily":
        refs = dji.MyParentFamilies.filter(person=obj).order_by("order")
    elif item == "family":
        refs = dji.MyFamilies.filter(person=obj).order_by("order")
    else:
        raise Exception("add '%s' to reference list" % item)
    # Next, perform action:
    if act == "remove":
        count = 1
        done = False
        for ref in refs:
            if count == index and not done:
                ref.delete()
                done = True
            else:
                ref.order = count
                ref.save()
                count += 1
    elif act == "up" and index >= 2:
        count = 1
        for ref in refs:
            if count == index - 1:
                ref.order = index
                ref.save()
            elif count == index:
                ref.order = index - 1
                ref.save()
            count += 1
    elif act == "down" and index < len(refs):
        count = 1
        for ref in refs:
            if count == index:
                ref.order = index + 1
                ref.save()
            elif count == index + 1:
                ref.order = index
                ref.save()
            count += 1
    dji.rebuild_cache(obj)
    return redirect("/%s/%s/%s" % (view, handle, tab[item]))

def process_json_request(request):
    """
    Process an Ajax/Json query request.
    """
    import gramps.gen.lib
    from gramps.gen.proxy import PrivateProxyDb, LivingProxyDb
    if not request.user.is_authenticated():
        db = PrivateProxyDb(db)
        db = LivingProxyDb(db,
                           LivingProxyDb.MODE_INCLUDE_LAST_NAME_ONLY,
                           None,            # current year
                           1)               # years after death
    field = request.GET.get("field", None)
    query = request.GET.get("q", "")
    page = int(request.GET.get("p", "1"))
    size = int(request.GET.get("s", "10"))
    if field == "mother":
        q, order, terms = build_person_query(request, query)
        q &= Q(person__gender_type__name="Female")
        matches = Name.objects.filter(q).order_by(*order)
        class_type = gramps.gen.lib.Person
        handle_expr = "match.person.handle"
    elif field == "father":
        q, order, terms = build_person_query(request, query)
        q &= Q(person__gender_type__name="Male")
        matches = Name.objects.filter(q).order_by(*order)
        class_type = gramps.gen.lib.Person
        handle_expr = "match.person.handle"
    elif field == "person":
        q, order, terms = build_person_query(request, query)
        matches = Name.objects.filter(q).order_by(*order)
        class_type = gramps.gen.lib.Person
        handle_expr = "match.person.handle"
    elif field == "place":
        q, order, terms = build_place_query(request, query)
        matches = Place.objects.filter(q).order_by(*order)
        class_type = gramps.gen.lib.Place
        handle_expr = "match.handle"
    else:
        raise Exception("""Invalid field: '%s'; Example: /json/?field=mother&q=Smith&p=1&size=10""" % field)
    ## ------------
    response_data = {"results": [], "total": len(matches)}
    for match in matches[(page - 1) * size:page * size]:
        obj = db.get_from_name_and_handle(class_type.__name__, eval(handle_expr))
        if obj:
            response_data["results"].append(obj.to_struct())
    return HttpResponse(simplejson.dumps(response_data), content_type="application/json")
