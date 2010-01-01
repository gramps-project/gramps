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
from web.grampsdb.forms import *
from web.djangodb import DjangoDb

import gen.proxy
from Utils import create_id

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
    context["True"] = True
    context["False"] = False
    context["default"] = ""
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
    context["tview"] = _('Home')
    return render_to_response("main_page.html", context)
                              
def logout_page(request):
    context = RequestContext(request)
    context["view"] = 'home'
    context["tview"] = _('Home')
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
    context["tview"] = _('User')
    return render_to_response('user_page.html', context)

def fix_person(request, person):
    try:
        name = person.name_set.get(preferred=True)
    except:
        names = person.name_set.all().order_by("order")
        if names.count() == 0:
            name = Name(person=person, 
                        surname="? Fixed", 
                        first_name="? Missing name",
                        preferred=True)
            name.save()
        else:
            order = 1
            for name in names:
                if order == 1:
                    name.preferred = True
                else:
                    name.preferred = False
                name.order = order
                name.save()
                order += 1
    if request:
        return redirect("/person/%s" % person.handle, request)

def set_date(obj):
    obj.calendar = 0
    obj.modifier = 0
    obj.quality = 0
    obj.text = ""
    obj.sortval = 0
    obj.newyear = 0
    obj.day1, obj.month1, obj.year1, obj.slash1 = 0, 0, 0, 0
    obj.day2, obj.month2, obj.year2, obj.slash2 = 0, 0, 0, 0

def view_name_detail(request, handle, order, action="view"):
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
            if name.preferred: # was preferred, stil must be
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
    context = RequestContext(request)
    context["action"] = action
    context["tview"] = _('Name')
    context["view"] = 'name'
    context["handle"] = handle
    context["id"] = id
    context["person"] = person
    context["form"] = form
    context["order"] = name.order
    context["next"] = "/person/%s/name/%d" % (person.handle, name.order)
    view_template = "view_name_detail.html"
    if action == "save":
        context["action"] = "view"
        return redirect("/person/%s/name/%d" % 
                        (person.handle, name.order), context)
    elif action == "back":
        return redirect("/person/%s/" % 
                        (person.handle), context)
    else:
        return render_to_response(view_template, context)
    

def view_detail(request, view, handle, action="view"):
    context = RequestContext(request)
    context["action"] = action
    context["view"] = view
    if view == "event":
        try:
            obj = Event.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_event_detail.html'
        context["tview"] = _("Event")
    elif view == "family":
        try:
            obj = Family.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_family_detail.html'
        context["tview"] = _("Family")
    elif view == "media":
        try:
            obj = Media.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_media_detail.html'
        context["tview"] = _("Media")
    elif view == "note":
        try:
            obj = Note.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_note_detail.html'
        context["tview"] = _("Note")
    elif view == "person":
        return view_person_detail(request, view, handle, action)
    elif view == "place":
        try:
            obj = Place.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_place_detail.html'
        context["tview"] = _("Place")
    elif view == "repository":
        try:
            obj = Repository.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_repository_detail.html'
        context["tview"] = _("Repository")
    elif view == "source":
        try:
            obj = Source.objects.get(handle=handle)
        except:
            raise Http404(_("Requested %s does not exist.") % view)
        view_template = 'view_source_detail.html'
        context["tview"] = _("Source")
    else:
        raise Http404(_("Requested page type not known"))
    context[view] = obj
    context["next"] = "/%s/%s" % (view, obj.handle)
    return render_to_response(view_template, context)

def view_person_detail(request, view, handle, action="view"):
    context = RequestContext(request)
    if handle == "add":
        if request.POST.has_key("action"):
            action = request.POST.get("action")
        else:
            action = "add"
    elif request.POST.has_key("action"):
        action = request.POST.get("action")
    if request.user.is_authenticated():
        if action == "edit":
            # get all of the data:
            person = Person.objects.get(handle=handle)
            try:
                name = person.name_set.get(preferred=True)
            except:
                name = Name(person=person, preferred=True)
            pf = PersonForm(instance=person)
            pf.model = person
            nf = NameForm(instance=name)
            nf.model = name
        elif action == "add":
            # make new data:
            person = Person()
            name = Name(person=person, preferred=True,
                        display_as=NameFormatType.objects.get(val=0), 
                        sort_as=NameFormatType.objects.get(val=0), 
                        name_type=NameType.objects.get(val=2))
            nf = NameForm(instance=name)
            nf.model = name
            pf = PersonForm(instance=person)
            pf.model = person
            action = "edit"
        elif action == "save":
            try:
                person = Person.objects.get(handle=handle)
            except:
                person = Person(handle=create_id())
            if person.id: # editing
                name = person.name_set.get(preferred=True)
            else: # adding a new person with new name
                name = Name(person=person, preferred=True)
            pf = PersonForm(request.POST, instance=person)
            pf.model = person
            nf = NameFormFromPerson(request.POST, instance=name)
            nf.model = name
            if nf.is_valid() and pf.is_valid():
                person = pf.save()
                name = nf.save(commit=False)
                name.person = person
                name.save()
            else:
                action = "edit"
        else: # view
            person = Person.objects.get(handle=handle)
            try:
                name = person.name_set.get(preferred=True)
            except:
                return fix_person(request, person)
            pf = PersonForm(instance=person)
            pf.model = person
            nf = NameForm(instance=name)
            nf.model = name
    else: # view person detail
        # BEGIN NON-AUTHENTICATED ACCESS
        person = Person.objects.get(handle=handle)
        if person:
            if person.private:
                raise Http404(_("Requested %s is not accessible.") % view)
            name = person.name_set.get(preferred=True)
            if person.probably_alive:
                name.sanitize()
        else:
            raise Http404(_("Requested %s does not exist.") % view)
        pf = PersonForm(instance=person)
        pf.model = person
        nf = NameForm(instance=name)
        nf.model = name
        # END NON-AUTHENTICATED ACCESS
    if action == "save":
        context["action"] = "view"
        return redirect("/person/%s" % person.handle, context)
    context["action"] = action
    context["view"] = view
    context["tview"] = _("Person")
    context["personform"] = pf
    context["nameform"] = nf
    context["person"] = person
    context["next"] = "/person/%s" % person.handle
    view_template = 'view_person_detail.html'
    return render_to_response(view_template, context)

def view(request, view):
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
        if request.user.is_authenticated():
            if request.GET.has_key("search"):
                search = request.GET.get("search")
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
                             Q(father__name__surname__istartswith=search_text) |
                             Q(mother__name__surname__istartswith=search_text)) &
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
        if request.user.is_authenticated():
            if request.GET.has_key("search"):
                search = request.GET.get("search")
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
                object_list = Name.objects.all().order_by("surname", "first_name")
        else:
            # BEGIN NON-AUTHENTICATED users
            if request.GET.has_key("search"):
                search = request.GET.get("search")
                if "," in search:
                    search_text, trash = [term.strip() for term in search.split(",", 1)]
                else:
                    search_text = search
                object_list = Name.objects \
                    .select_related() \
                    .filter(Q(surname__istartswith=search_text) &
                            Q(private=False) &
                            Q(person__private=False)
                            ) \
                    .order_by("surname", "first_name")
            else:
                object_list = Name.objects \
                                .select_related() \
                                .filter(Q(private=False) &
                                        Q(person__private=False)) \
                                .order_by("surname", "first_name")
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

    context = RequestContext(request)
    context["page"] = page
    context["view"] = view
    context["tview"] = _(view.title())
    context["search"] = search
    context["total"] = total
    context["object_list"] = object_list
    context["next"] = "/person/"
    if search:
        context["search_query"] = ("&search=%s" % search)
    else:
        context["search_query"] = ""
    return render_to_response(view_template, context)
