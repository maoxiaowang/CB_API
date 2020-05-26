import re

from django import template

register = template.Library()


@register.filter(is_safe=True)
def method_to_level(method):
    """
    get: primary
    post: success
    put: warning
    delete: danger
    """
    if method == 'get':
        level = 'primary'
    elif method == 'post':
        level = 'success'
    elif method == 'put':
        level = 'warning'
    elif method == 'delete':
        level = 'danger'
    else:
        level = 'secondary'
    return level


@register.filter(is_safe=True)
def format_field_attrs(attrs):
    attr_str = str()
    for attr in attrs:
        if attr[0] != '必填' and attr[1] is not None:
            if attr_str and not attr_str.strip().endswith('/'):
                attr_str += ' / '
            attr_str += '<span class="font-weight-light">%s (%s)</span>' % (attr[0], attr[1])
    if not attr_str:
        attr_str += '-'
    return attr_str


@register.filter(is_safe=True)
def field_required_badge(attrs):
    cls = str()
    required = False
    for attr in attrs:
        if attr[0] == '必填' and attr[1] is True:
            required = True
    if required:
        cls += '<span class="badge badge-pill badge-info">必填</span>'
    return cls


@register.filter(is_safe=True)
def format_field_choices(choices):
    choice_str = str()
    for choice in choices:
        if choice_str and not choice_str.endswith('/'):
            choice_str += ' / '
        choice_str += ('<span>%s</span> '
                       '<span class="text-muted font-weight-light">(%s)</span>' % (choice[0], choice[1]))
    if not choice_str:
        choice_str += '-'
    return choice_str


@register.filter(is_safe=True)
def add_class_for_field(field, extra_cls=None):
    field_widget = field.field.widget
    base_cls = 'form-control'
    if hasattr(field_widget, 'input_type') and field_widget.input_type == 'checkbox':
        default_cls = 'form-check-input'
    else:
        default_cls = 'form-control form-control-sm'
    attrs = field.form.fields[field.name].widget.attrs
    if 'class' in attrs:
        cls = attrs['class']
        if base_cls not in cls.split():
            cls = ' '.join((cls, default_cls))
    else:
        cls = default_cls
    if extra_cls:
        if default_cls not in extra_cls.split():
            cls = ' '.join((cls, extra_cls))
    field.form.fields[field.name].widget.attrs['class'] = cls
    return field


@register.filter(is_safe=True)
def field_wrap_class(field):
    field_widget = field.field.widget
    if hasattr(field_widget, 'input_type') and field_widget.input_type == 'checkbox':
        cls = 'form-check'
    else:
        cls = 'form-control from-control-sm'
    return cls


@register.simple_tag
def decorate_form(form):
    if form is not None:
        form.label_suffix = ''
    return form


@register.filter
def request_url_params(url):
    patterns = re.findall(r'<\w+:\w+>', url)
    input_template = ('<input class="form-control form-control-sm d-inline w-auto" type="%(type)s" '
                      'placeholder="%(placeholder)s" name="%(name)s" data-text-type="%(converter)s" %(extra)s required>')
    result = url
    for ptn in patterns:
        c, p = ptn.lstrip('<').rstrip('>').split(':')
        t, extra = 'text', ''
        if c == 'uuid':
            extra = 'minlength="36" maxlength="36"'
        elif c == 'uuids':
            extra = 'minlength=36'
        elif c == 'id':
            extra = 'min="1"'
            t = 'number'

        result = result.replace(ptn, input_template % {
            'placeholder': ptn, 'name': p, 'converter': c, 'type': t, 'extra': extra
        })
    return result
