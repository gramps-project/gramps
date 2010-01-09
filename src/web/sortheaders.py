# Author: insin
# Site: http://www.djangosnippets.org/snippets/308/

from django.core.paginator import InvalidPage, EmptyPage
from collections import defaultdict

from unicodedata import normalize
import locale

ORDER_VAR = 'o'
ORDER_TYPE_VAR = 'ot'

def first_letter(text):
    """
    Text should be a unicode string. Returns first letter.
    """
    if len(text) > 0:
        letter = normalize('NFKC', text)[0].upper()
        (lang_country, modifier ) = locale.getlocale()
        if lang_country == "sv_SE" and letter in [u'W', u'V']:
            letter = u'V,W'
        return letter
    else:
        return u'?'

class SortHeaders:
    """
    Handles generation of an argument for the Django ORM's
    ``order_by`` method and generation of table headers which reflect
    the currently selected sort, based on defined table headers with
    matching sort criteria.

    Based in part on the Django Admin application's ``ChangeList``
    functionality.
    """
    def __init__(self, request, headers, default_order_field=None,
            default_order_type='asc', additional_params=None):
        """
        request
            The request currently being processed - the current sort
            order field and type are determined based on GET
            parameters.

        headers
            A list of two-tuples of header text and matching ordering
            criteria for use with the Django ORM's ``order_by``
            method. A criterion of ``None`` indicates that a header
            is not sortable.

        default_order_field
            The index of the header definition to be used for default
            ordering and when an invalid or non-sortable header is
            specified in GET parameters. If not specified, the index
            of the first sortable header will be used.

        default_order_type
            The default type of ordering used - must be one of
            ``'asc`` or ``'desc'``.

        additional_params:
            Query parameters which should always appear in sort links,
            specified as a dictionary mapping parameter names to
            values. For example, this might contain the current page
            number if you're sorting a paginated list of items.
        """
        if default_order_field is None:
            for i, (header, query_lookup) in enumerate(headers):
                if query_lookup is not None:
                    default_order_field = i
                    break
        if default_order_field is None:
            raise AttributeError('No default_order_field was specified and none of the header definitions given were sortable.')
        if default_order_type not in ('asc', 'desc'):
            raise AttributeError('If given, default_order_type must be one of \'asc\' or \'desc\'.')
        if additional_params is None: additional_params = {}

        self.header_defs = headers
        self.additional_params = additional_params
        self.order_field, self.order_type = default_order_field, default_order_type

        # Determine order field and order type for the current request
        params = dict(request.GET.items())
        if ORDER_VAR in params:
            try:
                new_order_field = int(params[ORDER_VAR])
                if headers[new_order_field][1] is not None:
                    self.order_field = new_order_field
            except (IndexError, ValueError):
                pass # Use the default
        if ORDER_TYPE_VAR in params and params[ORDER_TYPE_VAR] in ('asc', 'desc'):
            self.order_type = params[ORDER_TYPE_VAR]

    def headers(self):
        """
        Generates dicts containing header and sort link details for
        all defined headers.
        """
        for i, (header, order_criterion) in enumerate(self.header_defs):
            th_classes = []
            new_order_type = 'asc'
            if i == self.order_field:
                th_classes.append('sorted %sending' % self.order_type)
                new_order_type = {'asc': 'desc', 'desc': 'asc'}[self.order_type]
            yield {
                'text': header,
                'sortable': order_criterion is not None,
                'url': self.get_query_string({ORDER_VAR: i, ORDER_TYPE_VAR: new_order_type}),
                'class_attr': (th_classes and ' class="%s"' % ' '.join(th_classes) or ''),
            }

    def get_query_string(self, params):
        """
        Creates a query string from the given dictionary of
        parameters, including any additonal parameters which should
        always be present.
        """
        params.update(self.additional_params)
        return '?%s' % '&amp;'.join(['%s=%s' % (param, value) \
                                     for param, value in params.items()])

    def get_order_by(self):
        """
        Creates an ordering criterion based on the current order
        field and order type, for use with the Django ORM's
        ``order_by`` method.
        """
        return '%s%s' % (
            self.order_type == 'desc' and '-' or '',
            self.header_defs[self.order_field][1],
        )

class NamePaginator(object):
    """Pagination for string-based objects"""
    
    def __init__(self, object_list, on=None, per_page=25):
        self.object_list = object_list
        self.count = len(object_list)
        self.pages = []
        
        # chunk up the objects so we don't need to iterate over the whole list for each letter
        chunks = defaultdict(list)
        
        for obj in self.object_list:
            if on: 
                obj_str = unicode(getattr(obj, on))
            else: 
                obj_str = unicode(obj)
            
            letter = first_letter(obj_str[0])
            chunks[letter].append(obj)
        
        # the process for assigning objects to each page
        current_page = NamePage(self)
        
        for letter in string.ascii_uppercase:
            if letter not in chunks: 
                current_page.add([], letter)
                continue
            
            sub_list = chunks[letter] # the items in object_list starting with this letter
            
            new_page_count = len(sub_list) + current_page.count
            # first, check to see if sub_list will fit or it needs to go onto a new page.
            # if assigning this list will cause the page to overflow...
            # and an underflow is closer to per_page than an overflow...
            # and the page isn't empty (which means len(sub_list) > per_page)...
            if (new_page_count > per_page and 
                abs(per_page - current_page.count) < abs(per_page - new_page_count) and 
                current_page.count > 0):
                # make a new page
                self.pages.append(current_page)
                current_page = NamePage(self)
            
            current_page.add(sub_list, letter)
        
        # if we finished the for loop with a page that isn't empty, add it
        if current_page.count > 0: self.pages.append(current_page)
        
    def page(self, num):
        """Returns a Page object for the given 1-based page number."""
        if len(self.pages) == 0:
            return None
        elif num > 0 and num <= len(self.pages):
            return self.pages[num-1]
        else:
            raise InvalidPage
    
    @property
    def num_pages(self):
        """Returns the total number of pages"""
        return len(self.pages)

class NamePage(object):
    def __init__(self, paginator):
        self.paginator = paginator
        self.object_list = []
        self.letters = []
    
    @property
    def count(self):
        return len(self.object_list)
    
    @property
    def start_letter(self):
        if len(self.letters) > 0: 
            self.letters.sort(key=locale.strxfrm)
            return first_letter(self.letters)
        else: return None
    
    @property
    def end_letter(self):
        if len(self.letters) > 0: 
            self.letters.sort(key=locale.strxfrm)
            return self.letters[-1]
        else: return None
    
    @property
    def number(self):
        return self.paginator.pages.index(self) + 1
    
    def add(self, new_list, letter=None):
        if len(new_list) > 0: self.object_list = self.object_list + new_list
        if letter: self.letters.append(letter)
    
    def __unicode__(self):
        if self.start_letter == self.end_letter:
            return self.start_letter
        else:
            return u'%c-%c' % (self.start_letter, self.end_letter)
