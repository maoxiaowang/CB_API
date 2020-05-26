from django import template

register = template.Library()


@register.filter(is_safe=True)
def label_filter(field, cls):
    """
    Passing a field and return it's label with a class
    """
    if not field:
        return ''
    if 'text-' not in cls and field.field.required is False:
        cls += ' text-muted'
    return field.label_tag(attrs={'class': cls})


@register.simple_tag
def generate_list(*args):
    return args
