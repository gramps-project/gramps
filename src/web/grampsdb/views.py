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

#------------------------------------------------------------------------
#
# Django Modules
#
#------------------------------------------------------------------------
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import Context, RequestContext, escape
from django.db.models import Q

#------------------------------------------------------------------------
#
# Gramps Modules
#
#------------------------------------------------------------------------
import web
from web.grampsdb.models import *
from web.grampsdb.forms import NameForm

_ = lambda text: text

# Views: [(<Nice name plural>, /<name>/handle, <Model>), ]
VIEWS = [(_('People'), 'person', Name), 
         (_('Families'), 'family', Family),
         (_('Events'), 'event', Event),
         (_('Notes'), 'note', Note),
         (_('Media'), 'media', Media),
         (_('Sources'), 'source', Source),
         (_('Places'), 'place', Place),
         (_('Repositories'), 'repository', Repository),
         ]

def context_processor(request):
    """
    This function is executed before template processing.
    takes a request, and returns a dictionary context.
    """
    # FIXME: make the css_theme based on user's selection
    context = {}
    context["css_theme"] = "Web_Mainz.css"
    # FIXME: get the views from a config?
    context["views"] = VIEWS
    return context

# CSS Themes:
#Web_Basic-Ash.css
#Web_Mainz.css
#Web_Basic-Cypress.css
#Web_Nebraska.css
#Web_Basic-Lilac.css
#Web_Print-Default.css
#Web_Basic-Peach.css
#Web_Visually.css
#Web_Basic-Spruce.css

def main_page(request):
    context = RequestContext(request)
    context["view"] = 'home'
    context["cview"] = _('Home')
    return render_to_response("main_page.html", context)
                              
def logout_page(request):
    context = RequestContext(request)
    context["view"] = 'home'
    context["cview"] = _('Home')
    logout(request)
    return HttpResponseRedirect('/')

def user_page(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404(_('Requested user not found.'))
    context = RequestContext(request)
    context["username"] =  username
    context["view"] = 'user'
    context["cview"] = _('User')
    return render_to_response('user_page.html', context)

def view_name_detail(request, handle, order, action="view"):
    if order == "add":
        order = 0
        action = "add"
    if request.POST.has_key("action"):
        action = request.POST.get("action")
    if action == "view":
        person = Person.objects.get(handle=handle)
        name = person.name_set.get(order=order)
        form = NameForm(instance=name)
        form.model = name
    elif action == "edit":
        person = Person.objects.get(handle=handle)
        name = person.name_set.get(order=order)
        form = NameForm(instance=name)
        form.model = name
    elif action == "delete":
        person = Person.objects.get(handle=handle)
        name_to_delete = person.name_set.get(order=order)
        was_preferred = name_to_delete.preferred
        name_to_delete.delete()
        names = person.name_set.all().order_by("order")
        for count in range(names.count()):
            if was_preferred:
                names[count].preferred = True
                was_preferred = False
            names[count].order = count
            names[count].save()
        form = NameForm()
        name = Name()
        action = "back"
    elif action == "add":
        person = Person.objects.get(handle=handle)
        name = Name()
        form = NameForm()
        form.model = name
        action = "edit"
    elif action == "save":
        person = Person.objects.get(handle=handle)
        try:
            name = person.name_set.get(order=order)
        except:
            order = person.name_set.count() + 1
            name = Name(calendar=0, modifier=0, quality=0,
                        year1=0, day1=0, month1=0,
                        sortval = 0, newyear=0, order=order,
                        sort_as=0, display_as=0, person_id=person.id)
        form = NameForm(request.POST, instance=name)
        form.model = name
        if form.is_valid():
            # now it is preferred:
            print "valid"
            if name.preferred: # was preferred, stil must be
                form.cleaned_data["preferred"] = True
            elif form.cleaned_data["preferred"]: # now is
                # set all of the other names to be 
                # not preferred:
                print "set"
                person.name_set.filter(~ Q(id=name.id)) \
                    .update(preferred=False)
            # else some other name is preferred
            print "save"
            n = form.save()
            print n.preferred
        else:
            action = "edit"
    context = RequestContext(request)
    context["action"] = action
    context["cview"] = action #_('Name')
    context["view"] = 'name'
    context["handle"] = handle
    context["id"] = id
    context["person"] = person
    context["form"] = form
    context["order"] = name.order
    view_template = "view_name_detail.html"
    print "action:", action
    if action == "save":
        context["action"] = "view"
        return redirect("/person/%s/name/%d" % 
                        (person.handle, name.order), context)
    elif action == "back":
        return redirect("/person/%s/" % 
                        (person.handle), context)
    else:
        return render_to_response(view_template, context)
    
def view_detail(request, view, handle):
    if view == "event":
        try:
            obj = Event.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_event_detail.html'
    elif view == "family":
        try:
            obj = Family.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_family_detail.html'
    elif view == "media":
        try:
            obj = Media.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_media_detail.html'
    elif view == "note":
        try:
            obj = Note.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_note_detail.html'
    elif view == "person":
        try:
            obj = Person.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_person_detail.html'
    elif view == "place":
        try:
            obj = Place.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_place_detail.html'
    elif view == "repository":
        try:
            obj = Repository.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_repository_detail.html'
    elif view == "source":
        try:
            obj = Source.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_source_detail.html'
    else:
        raise Http404(_("Requested page type not known"))
    cview = view.title()
    context = RequestContext(request)
    context["cview"] = cview
    context["view"] = view
    context["handle"] = handle
    context[view] = obj
    return render_to_response(view_template, context)

def view(request, view):
    cview = view.title()
    search = ""
    if view == "event":
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
        if request.GET.has_key("search"):
            search = request.GET.get("search")
            if request.user.is_authenticated():
                if "," in search:
                    surname, first = [term.strip() for term in 
                                      search.split(",", 1)]
                    object_list = Family.objects \
                        .filter((Q(father__name__surname__istartswith=surname) &
                                 Q(father__name__first_name__istartswith=first)) |
                                (Q(mother__name__surname__istartswith=surname) &
                                 Q(mother__name__first_name__istartswith=first)) 
                                ) \
                        .order_by("gramps_id")
                else: # no comma
                    object_list = Family.objects \
                        .filter(Q(gramps_id__icontains=search) |
                                Q(family_rel_type__name__icontains=search) |
                                Q(father__name__surname__istartswith=search) |
                                Q(father__name__first_name__istartswith=search) |
                                Q(mother__name__surname__istartswith=search) |
                                Q(mother__name__first_name__istartswith=search)
                                ) \
                        .order_by("gramps_id")
            else: 
                # NON-AUTHENTICATED users
                if "," in search:
                    search, trash = [term.strip() for term in search.split(",", 1)]
                object_list = Family.objects \
                    .filter((Q(gramps_id__icontains=search) |
                             Q(family_rel_type__name__icontains=search) |
                             Q(father__name__surname__istartswith=search) |
                             Q(mother__name__surname__istartswith=search)) &
                            Q(private=False) 
                            ) \
                    .order_by("gramps_id")
        else: # no search
            if request.user.is_authenticated():
                object_list = Family.objects.all().order_by("gramps_id")
            else:
                # NON-AUTHENTICATED users
                object_list = Family.objects.filter(private=False).order_by("gramps_id")
        view_template = 'view_families.html'
        total = Family.objects.all().count()
    elif view == "media":
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
        if request.GET.has_key("search"):
            search = request.GET.get("search")
            if request.user.is_authenticated():
                if "," in search:
                    surname, first_name = [term.strip() for term in 
                                           search.split(",", 1)]
                    object_list = Name.objects \
                        .filter(Q(surname__istartswith=surname, 
                                  first_name__istartswith=first_name)) \
                        .order_by("surname", "first_name")
                else:
                    object_list = Name.objects \
                        .filter((Q(surname__icontains=search) | 
                                 Q(first_name__icontains=search) |
                                 Q(suffix__icontains=search) |
                                 Q(prefix__icontains=search) |
                                 Q(patronymic__icontains=search) |
                                 Q(title__icontains=search) |
                                 Q(person__gramps_id__icontains=search))
                                ) \
                        .order_by("surname", "first_name")
            else:
                # BEGIN NON-AUTHENTICATED users
                if "," in search:
                    search, trash = [term.strip() for term in search.split(",", 1)]
                object_list = Name.objects \
                    .filter(Q(surname__istartswith=search) &
                            Q(private=False) &
                            Q(person__private=False)
                            ) \
                    .order_by("surname", "first_name")
                # END NON-AUTHENTICATED users
        else:
            if request.user.is_authenticated():
                object_list = Name.objects.all().order_by("surname", "first_name")
            else:
                # BEGIN NON-AUTHENTICATED users
                object_list = Name.objects.filter(Q(private=False) &
                                                  Q(person__private=False)).order_by("surname", "first_name")
                # END NON-AUTHENTICATED users
        view_template = 'view_people.html'
        total = Name.objects.all().count()
    elif view == "place":
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
    elif view == "source":
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
    else:
        raise Http404("Requested page type not known")

    if request.user.is_authenticated():
        paginator = Paginator(object_list, 50) 
    else:
        paginator = Paginator(object_list, 19) 

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)

    context = RequestContext(request)
    context["page"] = page
    context["view"] = view
    context["cview"] = cview
    context["search"] = search
    context["total"] = total
    if search:
        context["search_query"] = ("&search=%s" % escape(search))
    else:
        context["search_query"] = ""
    return render_to_response(view_template, context)
