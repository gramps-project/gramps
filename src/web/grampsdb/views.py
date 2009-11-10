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
from web.settings import VIEWS

def get_views():
    '''
    VIEWS is [("People", "person"), (plural, singular), ...]
    '''
    return VIEWS

def main_page(request):
    context = RequestContext(request)
    context["views"] = [(pair[0], pair[1], 
          getattr(web.grampsdb.models, pair[2]).objects.count()) 
                        for pair in get_views()]
    context["view"] = 'home'
    context["cview"] = 'Home'
    return render_to_response("main_page.html", context)
                              
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

def user_page(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404('Requested user not found.')
    context = RequestContext(request)
    context["username"] =  username
    context["views"] = get_views()
    context["view"] = 'user'
    context["cview"] = 'User'
    return render_to_response('user_page.html', context)

def view_detail(request, view, handle):
    cview = view.title()
    context = RequestContext(request)
    context["views"] = get_views()
    context["cview"] = cview
    context["view"] = view
    context["handle"] = handle
    return render_to_response('view_detail_page.html', context)
    
def view(request, view):
    cview = view.title()
    search = ""
    view_template = 'view_page.html'
    if view == "event":
        object_list = Event.objects.all().order_by("gramps_id")
    elif view == "family":
        object_list = Family.objects.all().order_by("gramps_id")
        view_template = 'view_family.html'
    elif view == "media":
        object_list = Media.objects.all().order_by("gramps_id")
    elif view == "note":
        object_list = Note.objects.all().order_by("gramps_id")
    elif view == "person":
        if request.GET.has_key("search"):
            search = request.GET.get("search")
            if request.user.is_authenticated():
                if "," in search:
                    surname, first_name = [term.strip() for term in search.split(",", 1)]
                    object_list = Name.objects. \
                        select_related().filter(surname__icontains=surname, 
                                                first_name__icontains=first_name).order_by("surname", "first_name")
                else:
                    object_list = Name.objects. \
                        select_related().filter(Q(surname__icontains=search) | 
                                                Q(first_name__icontains=search) |
                                                Q(suffix__icontains=search) |
                                                Q(prefix__icontains=search) |
                                                Q(patronymic__icontains=search) |
                                                Q(title__icontains=search) |
                                                Q(person__gramps_id__icontains=search)
                                                  ).order_by("surname", "first_name")
            else:
                # FIXME: non-authenticated users don't get to search first_names
                if "," in search:
                    search, first_name = [term.strip() for term in search.split(",", 1)]
                object_list = Name.objects. \
                    select_related().filter(surname__icontains=search).order_by("surname", "first_name")
        else:
            object_list = Name.objects.select_related().order_by("surname", "first_name")
        view_template = 'view_person.html'
    elif view == "place":
        object_list = Place.objects.all().order_by("gramps_id")
    elif view == "repository":
        object_list = Repository.objects.all().order_by("gramps_id")
    elif view == "source":
        object_list = Source.objects.all().order_by("gramps_id")

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
    context["views"] = get_views()
    context["view"] = view
    context["cview"] = cview
    context["search"] = search
    if search:
        context["search_query"] = ("&search=%s" % escape(search))
    else:
        context["search_query"] = ""
    return render_to_response(view_template, context)
