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
from webapp.grampsdb.models import Media
from webapp.grampsdb.forms import *
from webapp.libdjango import DjangoInterface
from gen.config import config 

## Django Modules
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import Context, RequestContext
from django.http import HttpResponse

## Other Python Modules
from PIL import Image
import os

## Globals
dji = DjangoInterface()

def process_media(request, context, handle, action, add_to=None): # view, edit, save
    """
    Process action on person. Can return a redirect.
    """
    context["tview"] = _("Media")
    context["tviews"] = _("Media")
    context["action"] = "view"
    view_template = "view_media_detail.html"
    
    if handle == "add":
        action = "add"
    if request.POST.has_key("action"):
        action = request.POST.get("action")

    # Handle: edit, view, add, create, save, delete
    if action == "full":
        # FIXME: path should come from config
        media = Media.objects.get(handle=handle)
        media_type, media_ext = media.mime.split("/", 1)
        folder = config.get('behavior.addmedia-image-dir')
        image = Image.open("%s/%s" % (folder, media.path))
        response = HttpResponse(mimetype=media.mime)
        image.save(response, media_ext.upper())
        return response
    elif action == "thumbnail":
        media = Media.objects.get(handle=handle)
        media_type, media_ext = media.mime.split("/", 1)
        folder = config.get('behavior.addmedia-image-dir')
        if os.path.exists("%s/thumbnail/%s" % (folder, media.path)):
            image = Image.open("%s/thumbnail/%s" % (folder, media.path))
        else:
            image = Image.open("%s/%s" % (folder, media.path))
            image.thumbnail((300,300), Image.ANTIALIAS)
            os.makedirs("%s/thumbnail" % folder)
            image.save("%s/thumbnail/%s" % (folder, media.path))
        response = HttpResponse(mimetype=media.mime)
        image.save(response, media_ext.upper())
        return response
    elif action == "add":
        media = Media(gramps_id=dji.get_next_id(Media, "M"))
        mediaform = MediaForm(instance=media)
        mediaform.model = media
    elif action in ["view", "edit"]: 
        media = Media.objects.get(handle=handle)
        mediaform = MediaForm(instance=media)
        mediaform.model = media
    elif action == "save": 
        media = Media.objects.get(handle=handle)
        mediaform = MediaForm(request.POST, instance=media)
        mediaform.model = media
        if mediaform.is_valid():
            update_last_changed(media, request.user.username)
            media = mediaform.save()
            dji.rebuild_cache(media)
            action = "view"
        else:
            action = "edit"
    elif action == "create": 
        media = Media(handle=create_id())
        mediaform = MediaForm(request.POST, instance=media)
        mediaform.model = media
        if mediaform.is_valid():
            update_last_changed(media, request.user.username)
            media = mediaform.save()
            dji.rebuild_cache(media)
            if add_to:
                item, handle = add_to
                model = dji.get_model(item)
                obj = model.objects.get(handle=handle)
                dji.add_media_ref_default(obj, media)
                return redirect("/%s/%s#tab-gallery" % (item, handle))
            action = "view"
        else:
            action = "add"
    elif action == "delete": 
        media = Media.objects.get(handle=handle)
        media.delete()
        return redirect("/media/")
    else:
        raise Exception("Unhandled action: '%s'" % action)

    context["mediaform"] = mediaform
    context["object"] = media
    context["media"] = media
    context["action"] = action
    
    return render_to_response(view_template, context)
