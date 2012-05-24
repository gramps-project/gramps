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
from webapp.utils import _, boolean
from webapp.grampsdb.models import Citation
from webapp.grampsdb.forms import *
from webapp.libdjango import DjangoInterface

## Django Modules
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import Context, RequestContext

## Globals
dji = DjangoInterface()

def process_citation(request, context, handle, action): # view, edit, save
    """
    Process action on person. Can return a redirect.
    """
    context["tview"] = _("Citation")
    context["tviews"] = _("Citations")
    context["action"] = "view"
    context["object"] = Citation()
    view_template = "view_citation_detail.html"
    
    return render_to_response(view_template, context)
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
                surname = Surname(name=name, primary=True, order=1)
                surname = Surname(name=name, 
                                  primary=True, 
                                  order=1,
                                  name_origin_type=NameOriginType.objects.get(val=NameOriginType._DEFAULT[0]))
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
                check_preferred(name, person)
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

