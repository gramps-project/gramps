# Create your views here.

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import Context, RequestContext, escape
from django.db.models import Q

import web
from web.grampsdb.models import *

_ = lambda text: text

# Views: [(Nice name plural, /name/handle, Model), ]
VIEWS = [(_('People'), 'person', Person), 
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
        object_list = Event.objects.all().order_by("gramps_id")
        view_template = 'view_events.html'
    elif view == "family":
        object_list = Family.objects.all().order_by("gramps_id")
        view_template = 'view_families.html'
    elif view == "media":
        object_list = Media.objects.all().order_by("gramps_id")
        view_template = 'view_media.html'
    elif view == "note":
        object_list = Note.objects.all().order_by("gramps_id")
        view_template = 'view_notes.html'
    elif view == "person":
        if request.GET.has_key("search"):
            search = request.GET.get("search")
            if request.user.is_authenticated():
                if "," in search:
                    surname, first_name = [term.strip() for term in search.split(",", 1)]
                    object_list = Name.objects \
                        .filter(surname__istartswith=surname, 
                                first_name__istartswith=first_name) \
                                .order_by("surname", "first_name")
                else:
                    object_list = Name.objects \
                        .filter(Q(surname__icontains=search) | 
                                Q(first_name__icontains=search) |
                                Q(suffix__icontains=search) |
                                Q(prefix__icontains=search) |
                                Q(patronymic__icontains=search) |
                                Q(title__icontains=search) |
                                Q(person__gramps_id__icontains=search)
                                ) \
                        .order_by("surname", "first_name")
            else:
                # FIXME: non-authenticated users don't get to search first_names
                if "," in search:
                    search, first_name = [term.strip() for term in search.split(",", 1)]
                object_list = Name.objects \
                    .filter(surname__istartswith=search) \
                    .order_by("surname", "first_name")
        else:
            object_list = Name.objects.order_by("surname", "first_name")
        view_template = 'view_people.html'
    elif view == "place":
        object_list = Place.objects.all().order_by("gramps_id")
        view_template = 'view_places.html'
    elif view == "repository":
        object_list = Repository.objects.all().order_by("gramps_id")
        view_template = 'view_repositories.html'
    elif view == "source":
        object_list = Source.objects.all().order_by("gramps_id")
        view_template = 'view_sources.html'
    else:
        raise Http404("Requested page type not known")

    paginator = Paginator(object_list, 15) 

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
    if search:
        context["search_query"] = ("&search=%s" % escape(search))
    else:
        context["search_query"] = ""
    return render_to_response(view_template, context)
