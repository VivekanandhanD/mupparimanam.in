from django import template

register = template.Library()


@register.filter
def rm_web(value):
    if value:
        return value.replace("web", "")
    else:
        return value
