from django import template

register = template.Library()

@register.filter(name='sds')
def sds(value, arg):
    if arg:
        a = arg.strip().lower()
        if a in value:
            return value[a]
    return arg

