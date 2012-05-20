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

""" Main view handlers """

import os
import cPickle
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

#------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------
import webapp
from webapp.grampsdb.models import *
from webapp.grampsdb.forms import *
from webapp.dbdjango import DbDjango
from webapp.libdjango import DjangoInterface
import cli.user

dji = DjangoInterface()

import gen.proxy
from Utils import create_id
import const

_ = lambda text: text

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
        profile = request.user.get_profile()
        context["css_theme"] = profile.css_theme
    else:
        context["css_theme"] = "Web_Mainz.css"
    # Other things for all environments:
    context["gramps_version"] = const.VERSION
    context["views"] = VIEWS
    context["menu"] = MENU
    context["True"] = True
    context["False"] = False
    context["sitename"] = Config.objects.get(setting="sitename").value
    context["default"] = ""
    return context

def main_page(request):
    """
    """
    context = RequestContext(request)
    context["view"] = 'home'
    context["tview"] = _('Home')
    return render_to_response("main_page.html", context)
                              
def logout_page(request):
    """
    """
    context = RequestContext(request)
    context["view"] = 'home'
    context["tview"] = _('Home')
    logout(request)
    # TODO: allow this once we have an error page
    #if request.GET.has_key("next"):
    #    return redirect(request.GET.get("next"))
    return HttpResponseRedirect('/')

def browse_page(request):
    """
    """
    context = RequestContext(request)
    context["view"] = 'browse'
    context["tview"] = _('Browse')
    return render_to_response('browse_page.html', context)

def user_page(request, username=None):
    """
    """
    if request.user.is_authenticated():
        if username is None:
            profile = request.user.get_profile()
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

def set_date(obj):
    """
    Initial a date object to default.
    """
    obj.calendar = 0
    obj.modifier = 0
    obj.quality = 0
    obj.text = ""
    obj.sortval = 0
    obj.newyear = 0
    obj.day1, obj.month1, obj.year1, obj.slash1 = 0, 0, 0, 0
    obj.day2, obj.month2, obj.year2, obj.slash2 = 0, 0, 0, 0

def view_surname(request, handle, order, sorder, action="view"):
    # /sdjhgsdjhdhgsd/name/1/surname/1  (view)
    # /sdjhgsdjhdhgsd/name/1/surname/add
    # /sdjhgsdjhdhgsd/name/1/surname/2/[edit|view|add|delete]
    if sorder == "add":
        sorder = 0
        action = "add"
    if request.POST.has_key("action"):
        print "override!"
        action = request.POST.get("action")

    person = Person.objects.get(handle=handle)
    name = person.name_set.filter(order=order)[0]
    surname = name.surname_set.filter()[int(sorder) - 1] # sorder is 1-based
    form = NameForm(instance=name)
    form.model = name

    if action == "save":
        active = "view"

    context = RequestContext(request)
    context["action"] = action
    context["tview"] = _("Surname")
    context["handle"] = handle
    context["id"] = id
    context["person"] = person
    context["object"] = person
    context["form"] = form
    context["order"] = name.order
    context["sorder"] = sorder
    view_template = 'view_surname.html'
    return render_to_response(view_template, context)

def view_name(request, handle, order, action="view"):
    if order == "add":
        order = 0
        action = "add"
    if request.POST.has_key("action"):
        action = request.POST.get("action")
    if action == "view":
        person = Person.objects.get(handle=handle)
        try:
            name = person.name_set.filter(order=order)[0]
        except:
            return fix_person(request, person)
        form = NameForm(instance=name)
        form.model = name
    elif action == "edit":
        person = Person.objects.get(handle=handle)
        name = person.name_set.filter(order=order)[0]
        form = NameForm(instance=name)
        form.model = name
    elif action == "delete":
        person = Person.objects.get(handle=handle)
        names = person.name_set.all().order_by("order")
        if names.count() > 1:
            name_to_delete = names[0]
            was_preferred = name_to_delete.preferred
            name_to_delete.delete()
            names = person.name_set.all().order_by("order")
            for count in range(names[1:].count()):
                if was_preferred:
                    names[count].preferred = True
                    was_preferred = False
                names[count].order = count
                names[count].save()
        form = NameForm()
        name = Name()
        action = "back"
    elif action == "add": # add name
        person = Person.objects.get(handle=handle)
        name = Name(person=person, 
                    display_as=NameFormatType.objects.get(val=0), 
                    sort_as=NameFormatType.objects.get(val=0), 
                    name_type=NameType.objects.get(val=2))
        form = NameForm(instance=name)
        form.model = name
        action = "edit"
    elif action == "save":
        person = Person.objects.get(handle=handle)
        try:
            name = person.name_set.filter(order=order)[0]
        except:
            order = person.name_set.count() + 1
            name = Name(person=person, order=order)
        form = NameForm(request.POST, instance=name)
        form.model = name
        if form.is_valid():
            # now it is preferred:
            if name.preferred: # was preferred, still must be
                form.cleaned_data["preferred"] = True
            elif form.cleaned_data["preferred"]: # now is
                # set all of the other names to be 
                # not preferred:
                person.name_set.filter(~ Q(id=name.id)) \
                    .update(preferred=False)
            # else some other name is preferred
            set_date(name)
            n = form.save()
        else:
            action = "edit"
        # FIXME: need to update cache
        # FIXME: need to reset probabily_alive
    context = RequestContext(request)
    context["action"] = action
    context["tview"] = _('Name')
    context["tviews"] = _('Names')
    context["view"] = 'name'
    context["handle"] = handle
    context["id"] = id
    context["person"] = person
    context["object"] = person
    context["form"] = form
    context["order"] = name.order
    context["next"] = "/person/%s/name/%d" % (person.handle, name.order)
    view_template = "view_name.html"
    if action == "save":
        context["action"] = "view"
        return redirect("/person/%s/name/%d" % (person.handle, name.order))
    elif action == "back":
        return redirect("/person/%s/" % (person.handle))
    else:
        return render_to_response(view_template, context)
    
def send_file(request, filename, mimetype):
    """                                                                         
    Send a file through Django without loading the whole file into              
    memory at once. The FileWrapper will turn the file object into an           
    iterator for chunks of 8KB.                                                 
    """
    from django.core.servers.basehttp import FileWrapper
    wrapper = FileWrapper(file(filename))
    response = HttpResponse(wrapper, mimetype=mimetype)
    path, base = os.path.split(filename)
    response['Content-Length'] = os.path.getsize(filename)
    response['Content-Disposition'] = 'attachment; filename=%s' % base
    return response

def process_report_run(request, handle):
    from webapp.reports import import_file, export_file, download
    from cli.plug import run_report
    import traceback
    db = DbDjango()
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        report = Report.objects.get(handle=handle)
        args = {"off": "pdf", "iff": "ged"} # basic defaults
        # override from given defaults in table:
        if report.options:
            for pair in str(report.options).split(" "):
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    args[key] = value
        # override from options on webpage:
        if request.GET.has_key("options"):
            options = str(request.GET.get("options"))
            if options:
                for pair in options.split(" "): # from webpage
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        args[key] = value
        if report.report_type == "textreport":
            filename = "/tmp/%s-%s.%s" % (str(profile.user.username), str(handle), args["off"])
            run_report(db, handle, of=filename, **args)
            mimetype = 'application/%s' % args["off"]
        elif report.report_type == "export":
            filename = "/tmp/%s-%s.%s" % (str(profile.user.username), str(handle), args["off"])
            export_file(db, filename, cli.user.User()) # callback
            mimetype = 'text/plain'
        elif report.report_type == "import":
            filename = download(args["i"], "/tmp/%s-%s.%s" % (str(profile.user.username), 
                                                              str(handle),
                                                              args["iff"]))
            if filename is not None:
                if True: # run in background, with error handling
                    import threading
                    def background():
                        try:
                            import_file(db, filename, cli.user.User()) # callback
                        except:
                            message = "import_file failed: " + traceback.format_exc()
                            request.user.message_set.create(message = message)
                    threading.Thread(target=background).start()
                    message = "Your data is now being imported..."
                    request.user.message_set.create(message = message)
                    return redirect("/report/")
                else:
                    success = import_file(db, filename, cli.user.User()) # callback
                    if not success:
                        message = "Failed to load imported."
                        request.user.message_set.create(message = message)
                    return redirect("/report/")
            else:
                message = "No filename was provided or found."
                request.user.message_set.create(message = message)
                return redirect("/report/")
        else:
            message = "Invalid report type '%s'" % report.report_type
            request.user.message_set.create(message = message)
            return redirect("/report/")
        if os.path.exists(filename):
            return send_file(request, filename, mimetype)
        else:
            context = RequestContext(request)
            message = "Failed: '%s' is not found" % filename
            request.user.message_set.create(message=message)
            return redirect("/report/")
    # If failure, just fail for now:
    context = RequestContext(request)
    context["message"] = "You need to be logged in."
    return render_to_response("process_action.html", context)

def view_list(request, view):
    """
    """
    context = RequestContext(request)
    search = ""
    if view == "event":
        context["tviews"] = _("Events")
        if request.user.is_authenticated():
            private = Q()
        else:
            # NON-AUTHENTICATED users
            private = Q(private=False)
        if request.GET.has_key("search"):
            search = request.GET.get("search")
            object_list = Event.objects \
                .filter((Q(gramps_id__icontains=search) |
                         Q(event_type__name__icontains=search) |
                         Q(place__title__icontains=search)) &
                        private
                        ) \
                .order_by("gramps_id")
        else:
            object_list = Event.objects.filter(private).order_by("gramps_id")
        view_template = 'view_events.html'
        total = Event.objects.all().count()
    elif view == "family":
        context["tviews"] = _("Families")
        if request.user.is_authenticated():
            if request.GET.has_key("search"):
                search = request.GET.get("search")
                if "," in search:
                    surname, first = [term.strip() for term in 
                                      search.split(",", 1)]
                    object_list = Family.objects \
                        .filter((Q(father__name__surname__surname__istartswith=surname) &
                                 Q(father__name__first_name__istartswith=first)) |
                                (Q(mother__name__surname__surname__istartswith=surname) &
                                 Q(mother__name__first_name__istartswith=first)) 
                                ) \
                        .order_by("gramps_id")
                else: # no comma
                    object_list = Family.objects \
                        .filter(Q(gramps_id__icontains=search) |
                                Q(family_rel_type__name__icontains=search) |
                                Q(father__name__surname__surname__istartswith=search) |
                                Q(father__name__first_name__istartswith=search) |
                                Q(mother__name__surname__surname__istartswith=search) |
                                Q(mother__name__first_name__istartswith=search)
                                ) \
                        .order_by("gramps_id")
            else: # no search
                object_list = Family.objects.all().order_by("gramps_id")
        else:
            # NON-AUTHENTICATED users
            if request.GET.has_key("search"):
                search = request.GET.get("search")
                if "," in search:
                    search_text, trash = [term.strip() for term in search.split(",", 1)]
                else:
                    search_text = search
                object_list = Family.objects \
                    .filter((Q(gramps_id__icontains=search_text) |
                             Q(family_rel_type__name__icontains=search_text) |
                             Q(father__name__surname__surname__istartswith=search_text) |
                             Q(mother__name__surname__surname__istartswith=search_text)) &
                            Q(private=False) &
                            Q(mother__private=False) &
                            Q(father__private=False)
                            ) \
                    .order_by("gramps_id")
            else:
                object_list = Family.objects \
                    .filter(Q(private=False) & 
                            Q(mother__private=False) &
                            Q(father__private=False)
                            ) \
                    .order_by("gramps_id")
        view_template = 'view_families.html'
        total = Family.objects.all().count()
    elif view == "media":
        context["tviews"] = _("Media")
        if request.user.is_authenticated():
            private = Q()
        else:
            # NON-AUTHENTICATED users
            private = Q(private=False)
        if request.GET.has_key("search"):
            search = request.GET.get("search")
            object_list = Media.objects \
                .filter(Q(gramps_id__icontains=search) &
                        private
                        ) \
                .order_by("gramps_id")
        else:
            object_list = Media.objects.filter(private).order_by("gramps_id")
        view_template = 'view_media.html'
        total = Media.objects.all().count()
    elif view == "note":
        context["tviews"] = _("Notes")
        if request.user.is_authenticated():
            private = Q()
        else:
            # NON-AUTHENTICATED users
            private = Q(private=False)
        if request.GET.has_key("search"):
            search = request.GET.get("search")
            object_list = Note.objects \
                .filter((Q(gramps_id__icontains=search) |
                         Q(note_type__name__icontains=search) |
                         Q(text__icontains=search)) &
                        private
                        ) \
                .order_by("gramps_id")
        else:
            object_list = Note.objects.filter(private).order_by("gramps_id")
        view_template = 'view_notes.html'
        total = Note.objects.all().count()
    elif view == "person":
        context["tviews"] = _("People")
        if request.user.is_authenticated():
            if request.GET.has_key("search"):
                search = request.GET.get("search")
                query = build_person_query(search, protect=False)
                object_list = Name.objects \
                    .filter(query) \
                    .order_by("surname__surname", "first_name")
            else:
                object_list = Name.objects.all().order_by("surname__surname", "first_name")
        else:
            # BEGIN NON-AUTHENTICATED users
            if request.GET.has_key("search"):
                search = request.GET.get("search")
                query = build_person_query(search, protect=True)
                object_list = Name.objects \
                    .filter(query) \
                    .order_by("surname__surname", "first_name")
            else:
                object_list = Name.objects \
                                .select_related() \
                                .filter(Q(private=False) &
                                        Q(person__private=False)) \
                                .order_by("surname__surname", "first_name")
            # END NON-AUTHENTICATED users
        view_template = 'view_people.html'
        total = Name.objects.all().count()
    elif view == "place":
        context["tviews"] = _("Places")
        if request.user.is_authenticated():
            private = Q()
        else:                 
            # NON-AUTHENTICATED users
            private = Q(private=False)
        if request.GET.has_key("search"):
            search = request.GET.get("search")
            object_list = Place.objects \
                .filter((Q(gramps_id__icontains=search) |
                         Q(title__icontains=search) 
                         ) &
                        private
                        ) \
                .order_by("gramps_id")
        else:
            object_list = Place.objects.filter(private).order_by("gramps_id")
        view_template = 'view_places.html'
        total = Place.objects.all().count()
    elif view == "repository":
        context["tviews"] = _("Repositories")
        if request.user.is_authenticated():
            private = Q()
        else:
            # NON-AUTHENTICATED users
            private = Q(private=False)
        if request.GET.has_key("search"):
            search = request.GET.get("search")
            object_list = Repository.objects \
                .filter((Q(gramps_id__icontains=search) |
                         Q(name__icontains=search) |
                         Q(repository_type__name__icontains=search)
                         ) &
                        private
                        ) \
                .order_by("gramps_id")
        else:
            object_list = Repository.objects.filter(private).order_by("gramps_id")
        view_template = 'view_repositories.html'
        total = Repository.objects.all().count()
    elif view == "citation":
        context["tviews"] = _("Citations")
        if request.user.is_authenticated():
            private = Q()
        else:
            # NON-AUTHENTICATED users
            private = Q(private=False)
        if request.GET.has_key("search"):
            search = request.GET.get("search")
            object_list = Citation.objects \
                .filter(Q(gramps_id__icontains=search) &
                        private
                        ) \
                .order_by("gramps_id")
        else:
            object_list = Citation.objects.filter(private).order_by("gramps_id")
        view_template = 'view_citations.html'
        total = Citation.objects.all().count()
    elif view == "source":
        context["tviews"] = _("Sources")
        if request.user.is_authenticated():
            private = Q()
        else:
            # NON-AUTHENTICATED users
            private = Q(private=False)
        if request.GET.has_key("search"):
            search = request.GET.get("search")
            object_list = Source.objects \
                .filter(Q(gramps_id__icontains=search) &
                        private
                        ) \
                .order_by("gramps_id")
        else:
            object_list = Source.objects.filter(private).order_by("gramps_id")
        view_template = 'view_sources.html'
        total = Source.objects.all().count()
    elif view == "tag":
        context["tviews"] = _("Tags")
        if request.GET.has_key("search"):
            search = request.GET.get("search")
            object_list = Tag.objects \
                .filter(Q(name__icontains=search)) \
                .order_by("name")
        else:
            object_list = Tag.objects.order_by("name")
        view_template = 'view_tags.html'
        total = Tag.objects.all().count()
    elif view == "report":
        context["tviews"] = _("Reports")
        if request.GET.has_key("search"):
            search = request.GET.get("search")
            if request.user.is_superuser:
                object_list = Report.objects \
                    .filter(Q(name__icontains=search)) \
                    .order_by("name")
            else:
                object_list = Report.objects \
                    .filter(Q(name__icontains=search) & ~Q(report_type="import")) \
                    .order_by("name")
        else:
            if request.user.is_superuser:
                object_list = Report.objects.all().order_by("name")
            else:
                object_list = Report.objects \
                    .filter(~Q(report_type="import")) \
                    .order_by("name")
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

def check_access(request, context, obj, action):
    """
    Check to see if user has access to object. We don't need to
    sanitize here, just check to see if we even acknowledge it exists.
    """
    if request.user.is_authenticated():
        if request.user.is_superuser:
            return True
        else:
            return action in ["view"]
    else: # outside viewer
        return not obj.private

def action(request, view, handle, action):
    """
    View a particular object given /object/handle (implied view),
    /object/handle/action, or /object/add.
    """
    # redirect:
    rd = None
    obj = None
    context = RequestContext(request)
    if request.POST.has_key("action"):
        action = request.POST.get("action")
    context["action"] = action
    context["view"] = view
    context["tview"] = _('Browse')
    if view == "event":
        try:
            obj = Event.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        if not check_access(request, context, obj, action):
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_event_detail.html'
        rd = process_event(request, context, handle, action)
    elif view == "family":
        try:
            obj = Family.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_family_detail.html'
        rd = process_family(request, context, handle, action)
    elif view == "media":
        try:
            obj = Media.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_media_detail.html'
        rd = process_media(request, context, handle, action)
    elif view == "note":
        try:
            obj = Note.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_note_detail.html'
        rd = process_note(request, context, handle, action)
    elif view == "person":
        if action not in ["add", "create"]:
            try:
                obj = Person.objects.get(handle=handle)
            except:
                raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_person_detail.html'
        rd = process_person(request, context, handle, action)
    elif view == "place":
        try:
            obj = Place.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_place_detail.html'
        rd = process_place(request, context, handle, action)
    elif view == "repository":
        try:
            obj = Repository.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_repository_detail.html'
        rd = process_repository(request, context, handle, action)
    elif view == "citation":
        try:
            obj = Citation.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_citation_detail.html'
        rd = process_citation(request, context, handle, action)
    elif view == "source":
        try:
            obj = Source.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_source_detail.html'
        rd = process_source(request, context, handle, action)
    elif view == "tag":
        try:
            obj = Tag.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_tag_detail.html'
        rd = process_tag(request, context, handle, action)
    elif view == "report":
        try:
            obj = Report.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_report_detail.html'
        rd = process_report(request, context, handle, action)
    else:
        raise Http404(_("Requested page type not known"))
    if rd:
        return rd
    if obj:
        context[view] = obj
        context["object"] = obj
        context["next"] = "/%s/%s" % (view, obj.handle)
    return render_to_response(view_template, context)

def process_event(request, context, handle, action):
    """
    Process action on event. Can return a redirect.
    """
    context["tview"] = _("Event")
    context["tviews"] = _("Events")

def process_family(request, context, handle, action):
    """
    Process action on family. Can return a redirect.
    """
    context["tview"] = _("Family")
    context["tviews"] = _("Families")

def process_media(request, context, handle, action):
    """
    Process action on media. Can return a redirect.
    """
    context["tview"] = _("Media")
    context["tviews"] = _("Media")

def process_note(request, context, handle, action):
    """
    Process action on note. Can return a redirect.
    """
    context["tview"] = _("Note")
    context["tviews"] = _("Notes")

def process_place(request, context, handle, action):
    """
    Process action on place. Can return a redirect.
    """
    context["tview"] = _("Place")
    context["tviews"] = _("Places")

def process_repository(request, context, handle, action):
    """
    Process action on repository. Can return a redirect.
    """
    context["tview"] = _("Repository")
    context["tviews"] = _("Repositories")

def process_citation(request, context, handle, action):
    """
    Process action on citation. Can return a redirect.
    """
    context["tview"] = _("Citation")
    context["tviews"] = _("Citations")

def process_source(request, context, handle, action):
    """
    Process action on source. Can return a redirect.
    """
    context["tview"] = _("Source")
    context["tviews"] = _("Sources")

def process_tag(request, context, handle, action):
    """
    Process action on tag. Can return a redirect.
    """
    context["tview"] = _("Tag")
    context["tviews"] = _("Tags")

def process_report(request, context, handle, action):
    """
    Process action on report. Can return a redirect.
    """
    if action == "run":
        return process_report_run(request, handle)
    context["tview"] = _("Report")
    context["tviews"] = _("Reports")

def process_person(request, context, handle, action): # view, edit, save
    """
    Process action on person. Can return a redirect.
    """
    context["tview"] = _("Person")
    context["tviews"] = _("People")
    if request.user.is_authenticated():
        if action in ["edit", "view"]:
            pf, nf, sf, person = get_person_forms(handle, empty=False)
        elif action == "add":
            pf, nf, sf, person = get_person_forms(handle=None, protect=False, empty=True)
        elif action == "delete":
            pf, nf, sf, person = get_person_forms(handle, protect=False, empty=True)
            person.delete()
            return redirect("/person/")
        elif action in ["save", "create"]: # could be create a new person
            # look up old data, if any:
            if handle:
                person = Person.objects.get(handle=handle)
                name = person.name_set.get(preferred=True)
                surname = name.surname_set.get(primary=True)
            else: # create new item
                person = Person(handle=create_id())
                name = Name(person=person, preferred=True)
                surname = Surname(name=name, primary=True)
            # combine with user data:
            pf = PersonForm(request.POST, instance=person)
            pf.model = person
            nf = NameFormFromPerson(request.POST, instance=name)
            nf.model = name
            sf = SurnameForm(request.POST, instance=surname)
            # check if valid:
            if nf.is_valid() and pf.is_valid() and sf.is_valid():
                # name.preferred and surname.primary get set False in the above is_valid()
                person = pf.save()
                # Process data:
                name.person = person
                name = nf.save(commit=False)
                # Manually set any data:
                name.suffix = nf.cleaned_data["suffix"] if nf.cleaned_data["suffix"] != " suffix " else ""
                name.preferred = True # FIXME: why is this False?
                name.save()
                # Process data:
                surname.name = name
                surname = sf.save(commit=False)
                # Manually set any data:
                surname.prefix = sf.cleaned_data["prefix"] if sf.cleaned_data["prefix"] != " prefix " else ""
                surname.primary = True # FIXME: why is this False?
                surname.save()
                # FIXME: last_saved, last_changed, last_changed_by
                dji.rebuild_cache(person)
                # FIXME: update probably_alive
                return redirect("/person/%s" % person.handle)
            else: 
                # need to edit again
                if handle:
                    action = "edit"
                else:
                    action = "add"
        else: # error?
            raise Http404(_("Requested %s does not exist.") % "person")
    else: # not authenticated
        # BEGIN NON-AUTHENTICATED ACCESS
        try:
            person = Person.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % "person")
        if person.private:
            raise Http404(_("Requested %s does not exist.") % "person")
        pf, nf, sf, person = get_person_forms(handle, protect=True)
        # END NON-AUTHENTICATED ACCESS
    context["action"] = action
    context["view"] = "person"
    context["tview"] = _("Person")
    context["tviews"] = _("People")
    context["personform"] = pf
    context["nameform"] = nf
    context["surnameform"] = sf
    context["person"] = person
    context["object"] = person
    context["next"] = "/person/%s" % person.handle

def get_person_forms(handle, protect=False, empty=False):
    if handle:
        person = Person.objects.get(handle=handle)
    else:
        person = Person()
        #person.gramps_id = "I0000" # FIXME: get next ID
    ## get a name
    try:
        name = person.name_set.get(preferred=True)
    except:
        name = Name(person=person, preferred=True,
                    display_as=NameFormatType.objects.get(val=0), 
                    sort_as=NameFormatType.objects.get(val=0), 
                    name_type=NameType.objects.get(val=2))
    ## get a surname
    try:
        surname = name.surname_set.get(primary=True)
    except:
        surname = Surname(name=name, primary=True)
    if protect and person.probably_alive:
        name.sanitize()
    pf = PersonForm(instance=person)
    pf.model = person
    name.suffix = make_empty(empty, name.suffix, " suffix ")
    nf = NameForm(instance=name)
    nf.model = name
    surname.prefix = make_empty(empty, surname.prefix, " prefix ")
    sf = SurnameForm(instance=surname)
    sf.model = surname
    return pf, nf, sf, person

def make_empty(empty, value, empty_value):
    if value:
        return value
    elif empty:
        return empty_value
    else:
        return value

def boolean(s):
    return s.lower() in ["true", "1", "yes", "y", "t"]

def build_person_query(search, protect):
    if "," in search or "=" in search:
        query = Q()
        terms = ["surname", "given"]
        for term in [term.strip() for term in search.split(",")]:
            if "=" in term:
                field, value = term.split("=")
            else:
                field = terms.pop(0)
                value = term
            if field == "surname":
                query &= Q(surname__surname__istartswith=value)
            elif field == "given":
                query &= Q(first_name__istartswith=value)
            elif field == "private":
                query &= Q(person__private=boolean(value))
    else:
        query = (Q(surname__surname__icontains=search) | 
                 Q(first_name__icontains=search) |
                 Q(suffix__icontains=search) |
                 Q(surname__prefix__icontains=search) |
                 Q(title__icontains=search) |
                 Q(person__gramps_id__icontains=search))
    if protect:
        query &= (Q(private=False) & Q(person__private=False))
    return query
