from django.template import RequestContext
from django.core.paginator import Paginator
from string import atoi


def get_objects_for_categories(clazz, categories, category_map):
    if len(categories) == 0:
        return clazz._default_manager.all()

    try:    
        category = categories[0]
        category = category_map.get(category, category)
        objects = clazz.__dict__[category].manager.all()
        
        for category in categories[1:]:
            category = category_map.get(category, category)            
            objects = objects & clazz.__dict__[category].manager.all()
            
    except KeyError, e:
        raise KeyError, "Category \"" + category + "\" does not exist for class " + clazz.__class__.__name__
    
    return objects
    
def sort_objects(objects, sort):    
    return objects.order_by(sort)

def unique_list(l):
    l.sort()
    return [l[0]] + [e for i, e in enumerate(l[1:]) if l[i+1] != l[i]]     

def get_list_context(request, default_sort, default_category = "objects", default_page = "1", default_max = "20"):
    sort = request.REQUEST.get("sort", default_sort)
    page = request.REQUEST.get("page", default_page)
    max = request.REQUEST.get("max", default_max)
    category = request.REQUEST.get("category", default_category)
    query = request.REQUEST.get("query", "")

    # two -'s negate each other
    while sort.startswith("--"):
        sort = sort[2:]

    try:
        page = atoi(page)
    except ValueError:
        page = atoi(default_page)

    try:
        max = atoi(max)
    except ValueError:
        max = atoi(default_max)
        
    try:
        categories = category.split("|")
    except:
        categories = [category]
    categories = [cat for cat in categories if len(cat) > 0]
    category = "|".join(categories)
    
    list_context = {"category" : category, "categories" : categories, "sort" : sort, "page" : page, "max" : max, "query" : query}
    
    if len(sort) > 0 and sort[0] != "-":
        list_context["reverse_sort_" + sort] = "-"
        
    list_context["per_page"] = ("10", "25", "50", "100")
    list_context["parent_template"] = "base.html"
    
    return list_context

def filter_objects(clazz, list_context, query_objects = None, filter_permissions = None, get_objects_for_categories = get_objects_for_categories, sort_objects = sort_objects, final_filter = None, category_map = {}):
    objects = get_objects_for_categories(clazz, list_context["categories"], category_map)
    if query_objects:
        objects = query_objects(objects, list_context["query"])
    objects = sort_objects(objects, list_context["sort"])
    if filter_permissions:
        objects = filter_permissions(objects)
    if final_filter:
        objects = final_filter(objects)

    page = list_context["page"]    
    paginator = Paginator(objects, list_context["max"])
    p = paginator.page(page-1)
    

    
    list_context["has_next_page"] = p.has_next()
    list_context["has_previous_page"] = p.has_previous()
    list_context["first_on_page"] = p.start_index()
    list_context["last_on_page"] = p.end_index()
    list_context["page_range"] = paginator.page_range
    
    return p.object_list
