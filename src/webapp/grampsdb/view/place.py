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
from webapp.grampsdb.models import Place
from webapp.grampsdb.forms import *
from webapp.libdjango import DjangoInterface

## Django Modules
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import Context, RequestContext

## Globals
dji = DjangoInterface()

def process_place(request, context, handle, action, add_to=None): # view, edit, save
    """
    Process action on person. Can return a redirect.
    """
    context["tview"] = _("Place")
    context["tviews"] = _("Places")
    context["action"] = "view"
    view_template = "view_place_detail.html"

    if handle == "add":
        action = "add"
    if request.POST.has_key("action"):
        action = request.POST.get("action")

    # Handle: edit, view, add, create, save, delete
    if action == "add":
        place = Place(gramps_id=dji.get_next_id(Place, "P"))
        placeform = PlaceForm(instance=place)
        placeform.model = place
    elif action in ["view", "edit"]: 
        place = Place.objects.get(handle=handle)
        placeform = PlaceForm(instance=place)
        placeform.model = place
    elif action == "save": 
        place = Place.objects.get(handle=handle)
        placeform = PlaceForm(request.POST, instance=place)
        placeform.model = place
        if placeform.is_valid():
            update_last_changed(place, request.user.username)
            place = placeform.save()
            dji.rebuild_cache(place)
            action = "view"
        else:
            action = "edit"
    elif action == "create": 
        place = Place(handle=create_id())
        placeform = PlaceForm(request.POST, instance=place)
        placeform.model = place
        if placeform.is_valid():
            update_last_changed(place, request.user.username)
            place = placeform.save()
            dji.rebuild_cache(place)
            if add_to:
                item, handle = add_to
                model = dji.get_model(item)
                obj = model.objects.get(handle=handle)
                dji.add_place_ref(obj, place.handle)
                dji.rebuild_cache(obj)
                return redirect("/%s/%s#tab-places" % (item, handle))
            action = "view"
        else:
            action = "add"
    elif action == "delete": 
        place = Place.objects.get(handle=handle)
        place.delete()
        return redirect("/place/")
    else:
        raise Exception("Unhandled action: '%s'" % action)

    context["placeform"] = placeform
    context["object"] = place
    context["place"] = place
    context["action"] = action
    
    return render_to_response(view_template, context)
