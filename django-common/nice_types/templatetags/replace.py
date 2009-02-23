import re 

from django import template
register = template.Library()

@register.filter
def replace ( string, args ): 
    n, search, replace = args.split(args[0])
    return re.sub( search, replace, string )
