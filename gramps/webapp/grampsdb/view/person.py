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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

""" Views for Person, Name, and Surname """

## Gramps Modules
from gramps.webapp.utils import _, boolean, update_last_changed, build_search, make_log
from gramps.webapp.grampsdb.models import Person, Name, Surname
from gramps.webapp.grampsdb.forms import *
from gramps.webapp.libdjango import DjangoInterface

## Django Modules
from django.http import Http404
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import Context, RequestContext

## Globals
dji = DjangoInterface()

## Functions
def check_order(request, person):
    """
    Check for proper ordering 1..., and for a preferred name.
    """
    order = 1
    preferred = False
    for name in person.name_set.all().order_by("order"):
        if name.preferred:
            preferred = True
        if name.order != order:
            name.order = order
            update_last_changed(name, request.user.username)
            name.save()
        order += 1
    if not preferred:
        name = person.name_set.get(order=1)
        name.preferred = True
        update_last_changed(name, request.user.username)
        name.save()

def check_primary(surname, surnames):
    """
    Check for a proper primary surname.
    """
    if surname.primary:
        # then all rest should not be:
        for s in surnames:
            if s.primary:
                s.primary = False
                s.save()
    else:
        # then one of them should be
        ok = False
        for s in surnames:
            if s.id != surname.id:
                if s.primary:
                    ok = True
                    break
                else:
                    s.primary = False
                    s.save()
                    ok = True
                    break
        if not ok:
            surname.primary = True

def check_preferred(request, name, person):
    """
    Check for a proper preferred name.
    """
    names = []
    if person:
        names = person.name_set.all()
    if name.preferred:
        # then all reast should not be:
        for s in names:
            if s.preferred and s.id != name.id:
                s.preferred = False
                update_last_changed(s, request.user.username)
                s.save()
    else:
        # then one of them should be
        ok = False
        for s in names:
            if s.id != name.id:
                if s.preferred:
                    ok = True
                    break
                else:
                    s.preferred = False
                    update_last_changed(s, request.user.username)
                    s.save()
                    ok = True
                    break
        if not ok:
            name.preferred = True

def process_surname(request, handle, order, sorder, act="view"):
    #import pdb; pdb.set_trace()
    # /sdjhgsdjhdhgsd/name/1/surname/1  (view)
    # /sdjhgsdjhdhgsd/name/1/surname/add
    # /sdjhgsdjhdhgsd/name/1/surname/2/[edit|view|add|delete]

    if sorder == "add":
        act = "add"
    if "action" in request.POST:
        act = request.POST.get("action")

    person = Person.objects.get(handle=handle)
    name = person.name_set.get(order=order)

    if act in ["view", "edit"]:
        surname = name.surname_set.get(order=sorder)
        if act == "edit":
            surname.prefix = make_empty(True, surname.prefix, " prefix ")
    elif act in ["delete"]:
        surnames = name.surname_set.all().order_by("order")
        if len(surnames) > 1:
            neworder = 1
            for surname in surnames:
                if surname.order != neworder:
                    surname.order = neworder
                    surname.save()
                    neworder += 1
                elif surname.order == int(sorder):
                    surname.delete()
                else:
                    neworder += 1
        else:
            request.user.message_set.create(message="You can't delete the only surname")
        return redirect("/person/%s/name/%s%s#tab-surnames" % (person.handle, name.order,
                                                               build_search(request)))
    elif act in ["add"]:
        surname = Surname(name=name, primary=False,
                          name_origin_type=NameOriginType.objects.get(val=NameOriginType._DEFAULT[0]))
        surname.prefix = make_empty(True, surname.prefix, " prefix ")
    elif act == "create":
        surnames = name.surname_set.all().order_by("order")
        sorder = 1
        for surname in surnames:
            sorder += 1
        surname = Surname(name=name, primary=True,
                          name_origin_type=NameOriginType.objects.get(val=NameOriginType._DEFAULT[0]),
                          order=sorder)
        sf = SurnameForm(request.POST, instance=surname)
        sf.model = surname
        if sf.is_valid():
            surname.prefix = ssf.cleaned_data["prefix"] if sf.cleaned_data["prefix"] != " prefix " else ""
            surname = sf.save(commit=False)
            check_primary(surname, surnames)
            surname.save()
            person.save_cache()
            return redirect("/person/%s/name/%s/surname/%s%s#tab-surnames" %
                            (person.handle, name.order, sorder,
                             build_search(request)))
        act = "add"
        surname.prefix = make_empty(True, surname.prefix, " prefix ")
    elif act == "save":
        surname = name.surname_set.get(order=sorder)
        sf = SurnameForm(request.POST, instance=surname)
        sf.model = surname
        if sf.is_valid():
            surname.prefix = ssf.cleaned_data["prefix"] if sf.cleaned_data["prefix"] != " prefix " else ""
            surname = sf.save(commit=False)
            check_primary(surname, name.surname_set.all().exclude(order=surname.order))
            surname.save()
            person.save_cache()
            return redirect("/person/%s/name/%s/surname/%s%s#tab-surnames" %
                            (person.handle, name.order, sorder,
                             build_search(request)))
        act = "edit"
        surname.prefix = make_empty(True, surname.prefix, " prefix ")
        # else, edit again
    else:
        raise Exception("unknown act: '%s'" % act)

    sf = SurnameForm(instance=surname)
    sf.model = surname

    context = RequestContext(request)
    context["action"] = act
    context["tview"] = _("Surname")
    context["handle"] = handle
    context["id"] = id
    context["person"] = person
    context["object"] = person
    context["surnameform"] = sf
    context["order"] = name.order
    context["sorder"] = sorder
    view_template = 'view_surname_detail.html'
    return render_to_response(view_template, context)

def process_name(request, handle, order, act="view"):
    if order == "add":
        act = "add"
    if "action" in request.POST:
        act = request.POST.get("action")
    ### Process act:
    if act in "view":
        pf, nf, sf, person = get_person_forms(handle, order=order)
        name = nf.model
    elif act == "edit":
        pf, nf, sf, person = get_person_forms(handle, order=order)
        name = nf.model
    elif act == "delete":
        person = Person.objects.get(handle=handle)
        name = person.name_set.filter(order=order)
        names = person.name_set.all()
        if len(names) > 1:
            name.delete()
            check_order(request, person)
        else:
            request.user.message_set.create(message = "Can't delete only name.")
        return redirect("/person/%s%s#tab-names" % (person.handle,
                                                    build_search(request)))
    elif act == "add": # add name
        person = Person.objects.get(handle=handle)
        name = Name(person=person,
                    preferred=False,
                    display_as=NameFormatType.objects.get(val=NameFormatType._DEFAULT[0]),
                    sort_as=NameFormatType.objects.get(val=NameFormatType._DEFAULT[0]),
                    name_type=NameType.objects.get(val=NameType._DEFAULT[0]))
        nf = NameForm(instance=name)
        nf.model = name
        surname = Surname(name=name,
                          primary=True,
                          order=1,
                          name_origin_type=NameOriginType.objects.get(val=NameOriginType._DEFAULT[0]))
        sf = SurnameForm(request.POST, instance=surname)
        sf.model = surname
    elif act == "create":
        # make new data
        person = Person.objects.get(handle=handle)
        name = Name(preferred=False)
        next_order = max([name.order for name in person.name_set.all()]) + 1
        surname = Surname(name=name,
                          primary=True,
                          order=next_order,
                          name_origin_type=NameOriginType.objects.get(val=NameOriginType._DEFAULT[0]))
        # combine with user data:
        nf = NameForm(request.POST, instance=name)
        name.id = None # FIXME: why did this get set to an existing name? Should be new. Remove from form?
        name.preferred = False
        nf.model = name
        sf = SurnameForm(request.POST, instance=surname)
        sf.model = surname
        if nf.is_valid() and sf.is_valid():
            # name.preferred and surname.primary get set False in the above is_valid()
            # person = pf.save()
            # Process data:
            name = nf.save(commit=False)
            name.person = person
            update_last_changed(name, request.user.username)
            # Manually set any data:
            name.suffix = nf.cleaned_data["suffix"] if nf.cleaned_data["suffix"] != " suffix " else ""
            name.preferred = False # FIXME: why is this False? Remove from form?
            name.order = next_order
            name.save()
            # Process data:
            surname = sf.save(commit=False)
            surname.name = name
            # Manually set any data:
            surname.prefix = sf.cleaned_data["prefix"] if sf.cleaned_data["prefix"] != " prefix " else ""
            surname.primary = True # FIXME: why is this False? Remove from form?
            surname.save()
            person.save_cache()
            return redirect("/person/%s/name/%s%s#tab-surnames" % (person.handle, name.order,
                                                                   build_search(request)))
        else:
            act = "add"
    elif act == "save":
        # look up old data:
        person = Person.objects.get(handle=handle)
        oldname = person.name_set.get(order=order)
        oldsurname = oldname.surname_set.get(primary=True)
        # combine with user data:
        pf = PersonForm(request.POST, instance=person)
        pf.model = person
        nf = NameForm(request.POST, instance=oldname)
        nf.model = oldname
        sf = SurnameForm(request.POST, instance=oldsurname)
        sf.model = oldsurname
        if nf.is_valid() and sf.is_valid():
            # name.preferred and surname.primary get set False in the above is_valid()
            # person = pf.save()
            # Process data:
            oldname.person = person
            name = nf.save()
            # Manually set any data:
            name.suffix = nf.cleaned_data["suffix"] if nf.cleaned_data["suffix"] != " suffix " else ""
            name.preferred = True # FIXME: why is this False? Remove from form?
            update_last_changed(name, request.user.username)
            check_preferred(request, name, person)
            name.save()
            # Process data:
            oldsurname.name = name
            surname = sf.save(commit=False)
            # Manually set any data:
            surname.prefix = sf.cleaned_data["prefix"] if sf.cleaned_data["prefix"] != " prefix " else ""
            surname.primary = True # FIXME: why is this False? Remove from form?
            surname.save()
            person.save_cache()
            return redirect("/person/%s/name/%s%s#tab-surnames" % (person.handle, name.order,
                                                                   build_search(request)))
        else:
            act = "edit"
    context = RequestContext(request)
    context["action"] = act
    context["tview"] = _('Name')
    context["tviews"] = _('Names')
    context["view"] = 'name'
    context["handle"] = handle
    context["id"] = id
    context["person"] = person
    context["object"] = person
    context["nameform"] = nf
    context["surnameform"] = sf
    context["order"] = order
    context["next"] = "/person/%s/name/%d" % (person.handle, name.order)
    view_template = "view_name_detail.html"
    return render_to_response(view_template, context)

def process_person(request, context, handle, act, add_to=None): # view, edit, save
    """
    Process act on person. Can return a redirect.
    """
    context["tview"] = _("Person")
    context["tviews"] = _("People")
    logform = None
    if request.user.is_authenticated():
        if act == "share":
            item, handle = add_to
            context["pickform"] = PickForm("Pick a person",
                                           Person,
                                           ("name__surname__surname",
                                            "name__first_name"),
                                      request.POST)
            context["object_handle"] = handle
            context["object_type"] = item
            return render_to_response("pick.html", context)
        elif act == "save-share":
            item, handle = add_to # ("Family", handle)
            pickform = PickForm("Pick a person",
                                Person,
                                ("name__surname__surname",
                                 "name__first_name"),
                                request.POST)
            if pickform.data["picklist"]:
                person_handle = pickform.data["picklist"]
                person = Person.objects.get(handle=person_handle)
                model = dji.get_model(item) # what model?
                obj = model.objects.get(handle=handle) # get family
                dji.add_child_ref_default(obj, person) # add person to family
                #person.parent_families.add(obj) # add family to child
                pfo = MyParentFamilies(person=person, family=obj,
                                       order=len(person.parent_families.all())+1)
                pfo.save()
                person.save_cache() # rebuild child
                obj.save_cache() # rebuild family
                return redirect("/%s/%s%s" % (item, handle, build_search(request)))
            else:
                context["pickform"] = pickform
                context["object_handle"] = handle
                context["object_type"] = "family"
                return render_to_response("pick.html", context)
        elif act in ["edit", "view"]:
            pf, nf, sf, person = get_person_forms(handle, empty=False)
            if act == "edit":
                logform = LogForm()
        elif act == "add":
            pf, nf, sf, person = get_person_forms(handle=None, protect=False, empty=True)
            logform = LogForm()
        elif act == "delete":
            pf, nf, sf, person = get_person_forms(handle, protect=False, empty=True)
            person.delete()
            return redirect("/person/%s" % build_search(request))
        elif act in ["save", "create"]: # could be create a new person
            # look up old data, if any:
            logform = LogForm(request.POST)
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
            sf.model = surname
            # check if valid:
            if nf.is_valid() and pf.is_valid() and sf.is_valid() and logform.is_valid():
                # name.preferred and surname.primary get set False in the above is_valid()
                update_last_changed(person, request.user.username)
                person = pf.save(save_cache=False)
                # Process data:
                name.person = person
                name = nf.save(commit=False)
                # Manually set any data:
                name.suffix = nf.cleaned_data["suffix"] if nf.cleaned_data["suffix"] != " suffix " else ""
                name.preferred = True # FIXME: why is this False? Remove from form?
                check_preferred(request, name, person)
                update_last_changed(name, request.user.username)
                name.save()
                # Process data:
                surname.name = name
                surname = sf.save(commit=False)
                # Manually set any data:
                surname.prefix = sf.cleaned_data["prefix"] if sf.cleaned_data["prefix"] != " prefix " else ""
                surname.primary = True # FIXME: why is this False? Remove from form?
                surname.save()
                # FIXME: put this in correct place to get correct cache, before changes:
                make_log(person, act, request.user.username, logform.cleaned_data["reason"], person.cache)
                if add_to: # Adding a child to the family
                    item, handle = add_to # ("Family", handle)
                    model = dji.get_model(item) # what model?
                    obj = model.objects.get(handle=handle) # get family
                    dji.add_child_ref_default(obj, person) # add person to family
                    #person.parent_families.add(obj) # add family to child
                    pfo = MyParentFamilies(person=person, family=obj,
                                           order=len(person.parent_families.all())+1)
                    pfo.save()
                    person.save_cache() # rebuild child
                    obj.save_cache() # rebuild family
                    return redirect("/%s/%s%s" % (item, handle, build_search(request)))
                person.save_cache()
                return redirect("/person/%s%s" % (person.handle, build_search(request)))
            else:
                # need to edit again
                if handle:
                    act = "edit"
                else:
                    act = "add"
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
    context["action"] = act
    context["view"] = "person"
    context["tview"] = _("Person")
    context["tviews"] = _("People")
    context["personform"] = pf
    context["nameform"] = nf
    context["surnameform"] = sf
    context["logform"] = logform
    context["person"] = person
    context["object"] = person
    context["next"] = "/person/%s" % person.handle

def get_person_forms(handle, protect=False, empty=False, order=None):
    if handle:
        person = Person.objects.get(handle=handle)
    else:
        person = Person(gramps_id=dji.get_next_id(Person, "I"))
    ## get a name
    name = None
    if order is not None:
        try:
            name = person.name_set.get(order=order)
        except:
            pass
    if name is None:
        try:
            name = person.name_set.get(preferred=True)
        except:
            name = Name(person=person, preferred=True,
                        display_as=NameFormatType.objects.get(val=NameFormatType._DEFAULT[0]),
                        sort_as=NameFormatType.objects.get(val=NameFormatType._DEFAULT[0]),
                        name_type=NameType.objects.get(val=NameType._DEFAULT[0]))
    ## get a surname
    try:
        surname = name.surname_set.get(primary=True)
    except:
        surname = Surname(name=name, primary=True,
                          name_origin_type=NameOriginType.objects.get(val=NameOriginType._DEFAULT[0]),
                          order=1)

    if protect and person.probably_alive:
        name.sanitize()
    pf = PersonForm(instance=person)
    pf.model = person
    name.suffix = make_empty(empty, name.suffix, " suffix ")
    nf = NameForm(instance=name)
    nf.model = name
    surname.prefix = make_empty(empty, surname.prefix, " prefix ")
    sf = SurnameForm(instance=surname)
    sf.model = surname
    return pf, nf, sf, person

def make_empty(empty, value, empty_value):
    if value:
        return value
    elif empty:
        return empty_value
    else:
        return value

