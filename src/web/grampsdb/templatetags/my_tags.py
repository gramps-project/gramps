from django.template import escape, Library
from web import libdjango
from web import djangodb
import web.grampsdb.models as models
from gen.lib.date import Date as GDate, Today
import DateHandler

dji = libdjango.DjangoInterface()
register = Library()

_dd = DateHandler.displayer.display
_dp = DateHandler.parser.parse

## FIXME: these dji function wrappers just use the functions
## written for the import/export. Can be done much more directly.

def person_get_birth_date(person):
    return person_get_event(person, models.EventType.BIRTH)
def person_get_death_date(person):
    return person_get_event(person, models.EventType.DEATH)

person_get_birth_date.is_safe = True
register.filter('person_get_birth_date', person_get_birth_date)
person_get_death_date.is_safe = True
register.filter('person_get_death_date', person_get_death_date)

def display_date(obj):
    date_tuple = dji.get_date(obj)
    if date_tuple:
        gdate = GDate()
        gdate.unserialize(date_tuple)
        return _dd(gdate)
    else:
        return ""

def person_get_event(person, event_type):
    event_ref_list = dji.get_event_ref_list(person)
    index = libdjango.lookup_role_index(event_type, event_ref_list)
    if index >= 0:
        event_handle = event_ref_list[index][3]
        # (False, [], [], u'b2cfa6cdec87392cf3b', (1, u'Primary'))
        # WARNING: the same object can be referred to more than once
        objs = models.EventRef.objects.filter(ref_object__handle=event_handle)
        if objs.count() > 0:
            return display_date(objs[0].ref_object)
        else:
            return ""
    else:
        return ""

def make_name(name, user):
    if isinstance(name, models.Name):
        surname = name.surname.strip()
        if not surname:
            surname = "[Missing]"
        if user.is_authenticated():
            return escape("%s, %s" % (surname, name.first_name))
        else:
            if djangodb.probably_alive(name.person.handle):
                return escape("%s, %s" % (surname, "[Living]"))
            else:
                return escape("%s, %s" % (surname, name.first_name))
    elif name:
        name = name.get(preferred=True)
        if name:
            return make_name(name, user)
        else:
            return ""
    else:
        return ""
make_name.is_safe = True
register.filter('make_name', make_name)

def missing(data):
    if data.strip() == "":
        return "[Missing]"
    return escape(data)
missing.is_safe = True
register.filter('missing', missing)

def currentSection(view1, view2):
    if view1.strip().lower() == view2.strip().lower():
        return "CurrentSection"
    return "OtherSection"
currentSection.is_safe = True
register.filter('currentSection', currentSection)

def row_count(row, page):
    return row + (page.number - 1) * page.paginator.per_page

register.filter('row_count', row_count)

def table_header(context, headers = None):
    # add things for the header here
    if headers:
        context["headers"] = headers
    return context

register.inclusion_tag('table_header.html', 
                       takes_context=True)(table_header)

def view_navigation(context):
    # add things for the view here
    return context

register.inclusion_tag('view_navigation.html', 
                       takes_context=True)(view_navigation)

def paginator(context, adjacent_pages=2):
    """
    To be used in conjunction with the object_list generic view.

    Adds pagination context variables for use in displaying first, adjacent and
    last page links in addition to those created by the object_list generic
    view.

    """
## Alternative page_numbers:
    page_numbers = range(max(0, context['page']-adjacent_pages), 
                         min(context['pages'], 
                             context['page']+adjacent_pages)+1) 
    results_this_page = context['object_list'].__len__()
    range_base = ((context['page'] - 1) * context['results_per_page'])

# # Original
# #    page_numbers = [n for n in range(context['page'] - adjacent_pages, 
# #                                     context['page'] + adjacent_pages + 1) 
# #                    if n > 0 and n <= context['pages']]

    return {
        'hits': context['hits'],
        'results_per_page': context['results_per_page'],
        'results_this_page': results_this_page,
        'first_this_page': range_base + 1,
        'last_this_page': range_base + results_this_page,
        'page': context['page'],
        'pages': context['pages'],
        'page_numbers': page_numbers,
        'next': context['next'],
        'previous': context['previous'],
        'has_next': context['has_next'],
        'has_previous': context['has_previous'],
        'show_first': 1 not in page_numbers,
        'show_last': context['pages'] not in page_numbers,
    }

register.inclusion_tag('paginator.html', 
                       takes_context=True)(paginator)
