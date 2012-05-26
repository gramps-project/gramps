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
from webapp.grampsdb.models import Citation
from webapp.grampsdb.forms import *
from webapp.libdjango import DjangoInterface

## Django Modules
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import Context, RequestContext

## Globals
dji = DjangoInterface()

def process_citation(request, context, handle, action, add_to=None): # view, edit, save
    """
    Process action on person. Can return a redirect.
    """
    context["tview"] = _("Citation")
    context["tviews"] = _("Citations")
    context["action"] = "view"
    view_template = "view_citation_detail.html"
    
    if handle == "add":
        action = "add"
    if request.POST.has_key("action"):
        action = request.POST.get("action")

    # Handle: edit, view, add, create, save, delete
    if action == "add":
        source = Source(gramps_id=dji.get_next_id(Source, "S"))
        sourceform = SourceForm(instance=source)
        sourceform.model = source
        citation = Citation(source=source, gramps_id=dji.get_next_id(Citation, "C"))
        citationform = CitationForm(instance=citation)
        citationform.model = citation
    elif action in ["view", "edit"]: 
        citation = Citation.objects.get(handle=handle)
        citationform = CitationForm(instance=citation)
        citationform.model = citation
        source = citation.source
        sourceform = SourceForm(instance=source)
        sourceform.model = source
    elif action == "save": 
        citation = Citation.objects.get(handle=handle)
        citationform = CitationForm(request.POST, instance=citation)
        citationform.model = citation
        if citationform.is_valid():
            update_last_changed(citation, request.user.username)
            citation = citationform.save()
            dji.rebuild_cache(citation)
            action = "view"
        else:
            action = "edit"
    elif action == "create": 
        source = Source(handle=create_id())
        sourceform = SourceForm(request.POST, instance=source)
        sourceform.model = source
        citation = Citation(handle=create_id(), source=source)
        citationform = CitationForm(request.POST, instance=citation)
        citationform.model = citation
        if citationform.is_valid() and sourceform.is_valid():
            update_last_changed(source, request.user.username)
            source = sourceform.save()
            citation.source = source
            update_last_changed(citation, request.user.username)
            citation = citationform.save()
            dji.rebuild_cache(source)
            dji.rebuild_cache(citation)
            if add_to:
                item, handle = add_to
                model = dji.get_model(item)
                obj = model.objects.get(handle=handle)
                dji.add_citation_ref(obj, citation.handle)
                return redirect("/%s/%s" % (item, handle))
            action = "view"
        else:
            action = "add"
    elif action == "delete": 
        citation = Citation.objects.get(handle=handle)
        citation.delete()
        return redirect("/citation/")
    else:
        raise Exception("Unhandled action: '%s'" % action)

    context["citationform"] = citationform
    context["sourceform"] = sourceform
    context["object"] = citation
    context["citation"] = citation
    context["source"] = source
    context["action"] = action
    
    return render_to_response(view_template, context)
