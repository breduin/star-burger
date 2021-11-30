from django import template

register = template.Library()

@register.filter
def restaurants(d, key):
    r = d[key]
    return [(x[0].name, x[1]) for x in r.items()]