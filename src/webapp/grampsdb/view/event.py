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
# $Id: utils.py 19637 2012-05-24 17:22:14Z dsblank $
#

""" Views for Person, Name, and Surname """

## Gramps Modules
from webapp.utils import _, boolean, update_last_changed
from webapp.grampsdb.models import Event
from webapp.grampsdb.forms import *
from webapp.libdjango import DjangoInterface
from webapp.dbdjango import DbDjango
from gen.datehandler import displayer, parser

## Django Modules
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import Context, RequestContext

## Globals
dji = DjangoInterface()
db = DbDjango()
dd = displayer.display
dp = parser.parse

def process_event(request, context, handle, action, add_to=None): # view, edit, save
    """
    Process action on person. Can return a redirect.
    """
    context["tview"] = _("Event")
    context["tviews"] = _("Events")
    context["action"] = "view"
    view_template = "view_event_detail.html"

    if handle == "add":
        action = "add"
    if request.POST.has_key("action"):
        action = request.POST.get("action")

    # Handle: edit, view, add, create, save, delete
    if action == "add":
        event = Event(gramps_id=dji.get_next_id(Event, "E"))
        eventform = EventForm(instance=event)
        eventform.model = event
    elif action in ["view", "edit"]: 
        event = Event.objects.get(handle=handle)
        genlibevent = db.get_event_from_handle(handle)
        if genlibevent:
            date = genlibevent.get_date_object()
            event.text = dd(date)
        eventform = EventForm(instance=event)
        eventform.model = event
    elif action == "save": 
        event = Event.objects.get(handle=handle)
        eventform = EventForm(request.POST, instance=event)
        eventform.model = event
        if eventform.is_valid():
            update_last_changed(event, request.user.username)
            event = eventform.save()
            dji.rebuild_cache(event)
            action = "view"
        else:
            action = "edit"
    elif action == "create": 
        event = Event(handle=create_id())
        eventform = EventForm(request.POST, instance=event)
        eventform.model = event
        if eventform.is_valid():
            update_last_changed(event, request.user.username)
            event = eventform.save()
            dji.rebuild_cache(event)
            if add_to:
                item, handle = add_to
                model = dji.get_model(item)
                obj = model.objects.get(handle=handle)
                dji.add_event_ref_default(obj, event)
                return redirect("/%s/%s" % (item, handle))
            action = "view"
        else:
            action = "add"
    elif action == "delete": 
        event = Event.objects.get(handle=handle)
        event.delete()
        return redirect("/event/")
    else:
        raise Exception("Unhandled action: '%s'" % action)

    context["eventform"] = eventform
    context["object"] = event
    context["event"] = event
    context["action"] = action
    
    return render_to_response(view_template, context)
