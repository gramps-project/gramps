from django.template import escape, Library
from django.utils.safestring import mark_safe
from web.utils import *
import web.utils

register = Library()

util_filters = ['person_event_table', 'person_name_table', 
                'person_source_table', 'person_attribute_table', 
                'person_address_table', 'person_note_table', 
                'person_gallery_table', 'person_internet_table', 
                'person_association_table', 'person_lds_table', 
                'person_reference_table',
                'family_children_table', 'family_event_table', 
                'family_source_table', 'family_attribute_table',
                'family_note_table', 'family_gallery_table', 
                'family_lds_table', 
                'nbsp']
for filter_name in util_filters:
    func = getattr(web.utils, filter_name)
    func.is_safe = True
    register.filter(filter_name, func)

probably_alive.is_safe = True
register.filter('probably_alive', probably_alive)

format_number.is_safe = True
register.filter('format_number', format_number)

person_get_birth_date.is_safe = True
register.filter('person_get_birth_date', person_get_birth_date)

person_get_death_date.is_safe = True
register.filter('person_get_death_date', person_get_death_date)

display_date.is_safe = True
register.filter('display_date', display_date)

person_get_event.is_safe = True
register.filter('person_get_events', person_get_event)

def preview(text, width=40):
    text = text.replace("\n", " ")
    return escape(text[:width])
preview.is_safe = True
register.filter('preview', preview)

make_name.is_safe = True
register.filter('make_name', make_name)

def preferred(name_set, attr):
    name = name_set.get(preferred=True)
    if name:
        return escape(getattr(name, attr))
    else:
        return "[Missing]"
preferred.is_safe = True
register.filter('preferred', preferred)

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
