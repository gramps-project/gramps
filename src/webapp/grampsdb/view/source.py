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
from webapp.grampsdb.models import Source
from webapp.grampsdb.forms import *
from webapp.libdjango import DjangoInterface

## Django Modules
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import Context, RequestContext

## Globals
dji = DjangoInterface()

def process_source(request, context, handle, action, add_to=None): # view, edit, save
    """
    Process action on person. Can return a redirect.
    """
    context["tview"] = _("Source")
    context["tviews"] = _("Sources")
    context["action"] = "view"
    view_template = "view_source_detail.html"
    
    if handle == "add":
        action = "add"
    if request.POST.has_key("action"):
        action = request.POST.get("action")

    # Handle: edit, view, add, create, save, delete
    if action == "add":
        source = Source(gramps_id=dji.get_next_id(Source, "S"))
        sourceform = SourceForm(instance=source)
        sourceform.model = source
    elif action in ["view", "edit"]: 
        source = Source.objects.get(handle=handle)
        sourceform = SourceForm(instance=source)
        sourceform.model = source
    elif action == "save": 
        source = Source.objects.get(handle=handle)
        sourceform = SourceForm(request.POST, instance=source)
        sourceform.model = source
        if sourceform.is_valid():
            update_last_changed(source, request.user.username)
            source = sourceform.save()
            dji.rebuild_cache(source)
            action = "view"
        else:
            action = "edit"
    elif action == "create": 
        source = Source(handle=create_id())
        sourceform = SourceForm(request.POST, instance=source)
        sourceform.model = source
        if sourceform.is_valid():
            update_last_changed(source, request.user.username)
            source = sourceform.save()
            dji.rebuild_cache(source)
            if add_to:
                raise Exception("Cannot add reference")
            action = "view"
        else:
            action = "add"
    elif action == "delete": 
        source = Source.objects.get(handle=handle)
        source.delete()
        return redirect("/source/")
    else:
        raise Exception("Unhandled action: '%s'" % action)

    context["sourceform"] = sourceform
    context["object"] = source
    context["source"] = source
    context["action"] = action
    
    return render_to_response(view_template, context)



