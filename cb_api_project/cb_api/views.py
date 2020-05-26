import warnings

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import FieldDoesNotExist
from django.core.handlers.exception import response_for_exception
from django.forms import ModelChoiceField, ChoiceField, modelform_factory
from django.http import Http404
from django.middleware.csrf import get_token
from django.urls import URLPattern, URLResolver
from django.utils.text import slugify
from django.views.generic.base import TemplateView

from cb_api.constants import API_QUERIES_KEY

User = get_user_model()


def list_urls(lst, acc=None):
    if acc is None:
        acc = []
    if not lst:
        return
    l = lst[0]
    if isinstance(l, URLPattern):
        yield acc + [str(l.pattern)], l.callback
    elif isinstance(l, URLResolver):
        yield from list_urls(l.url_patterns, acc + [str(l.pattern)])
    yield from list_urls(lst[1:], acc)


def generate_menu_context(prefix=None, query=None, context=None):
    urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [''])
    urls = list()
    all_urls = list()
    context = context or dict()
    exclude_urls = ['', 'api/', 'setup/']
    display_attrs = {
        'max_length': '最大长度',
        'min_length': '最小长度',
        'required': '必填',
        'max_value': '最大值',
        'min_value': '最小值'
    }
    display_fields = {
        'CharField': '字符串',
        'UUIDField': 'UUID',
        'TypedChoiceField': '限定',
        'ListField': '列表',
        'DictField': '字典',
        'BooleanField': '布尔',
        'IntegerField': '整数',
        'FloatField': '浮点',
        'EmailField': '邮件',
        'ImageField': '图片（二进制）',
        'UsernameField': '用户名',
        'GenericIPAddressField': 'IP地址',
        'ChoiceField': '固定选择',
        'ModelChoiceField': '模型选择',
        'GenericObjectField': '通用对象',
    }
    appended_urls = list()

    def make_fields(visible_fields):
        _fields = list()
        for bound_field in visible_fields:
            f, name = bound_field.field, bound_field.name
            choices = iter(list())
            target_type = None
            foreign_key = False
            if ChoiceField in f.__class__.__bases__:
                # choices info
                if isinstance(f, ModelChoiceField):
                    try:
                        target_type = f.__class__.__name__
                    except Exception as e:
                        raise
                    foreign_key = True
                else:
                    # TypedChoiceField
                    target_type = form._meta.model._meta.get_field(name).__class__.__name__
                    choices = filter(lambda x: x[0], f.choices)
            _type = target_type or f.__class__.__name__
            # verbose name or label
            if hasattr(form, '_meta'):
                try:
                    verbose_name = form._meta.model._meta.get_field(name).verbose_name
                except FieldDoesNotExist:
                    verbose_name = form.fields.get(name).label
            else:
                verbose_name = form.fields.get(name).label
            _fields.append(
                {
                    'name': name,
                    'verbose_name': verbose_name or '-',
                    'attrs': [(display_attrs[k], v) for k, v in f.__dict__.items() if k in display_attrs],
                    'origin_attrs': [(k, v) for k, v in f.__dict__.items() if k in display_attrs],
                    'type': display_fields.get(_type) or _type,
                    'foreign_key': foreign_key,
                    'choices': choices
                }
            )
        return _fields

    for items in list_urls(urlconf.urlpatterns):
        url = ''.join(items[0])
        if url in appended_urls:
            continue
        appended_urls.append(url)
        view = items[1]

        # view could be a function (serve static)
        view_class = getattr(view, 'view_class', None)
        if view_class is None:
            continue

        # "is_api" attribute
        is_api = True
        if hasattr(view_class, 'is_api'):
            try:
                is_api = view.view_initkwargs['is_api']
            except KeyError:
                is_api = bool(view_class.is_api)

        if url in exclude_urls or not is_api:
            continue

        all_urls.append(url)

        # prefix filter, all urls should NOT be filtered
        if prefix and not url.startswith(prefix):
            continue

        doc = (view.__doc__ or '').strip()
        fields = list()
        form = None
        view_class = view.view_class

        # form_class attribute could be None
        if hasattr(view_class, 'form_class') and view_class.form_class:
            form = view.view_class().get_form_class()()
            fields = make_fields(form.visible_fields())
        elif hasattr(view_class, 'fields') and view_class.fields:
            form = modelform_factory(view_class.model, fields=view_class.fields)
            fields = make_fields(form().visible_fields())
            # raise ValueError('Fields on view is NOT supported.')

        # query
        methods = items[1].view_class.http_method_names
        query_match = True
        if query:
            for word in filter(lambda x: x, query.split()):
                if word and not any((word in url, word in doc, word == methods[0])):
                    query_match = False
                    break
        if not query_match:
            continue

        urls.append({
            'url': url,
            'methods': methods,
            'doc': doc,
            'fields': fields,
            'form': form,
        })

    query_slug = slugify(query, allow_unicode=True)
    if query_slug:
        queries.append(query_slug)
        cache.set(API_QUERIES_KEY, queries, 3600)
    menus = make_menus(all_urls)
    context.update(
        urls=urls, query=query, query_slug=query_slug,
        menus=menus, prefix=prefix
    )
    return context


def make_menus(url_list):
    """
    {
        “base”: {“user”: ["list", "detail", ...], ..., “group”: [...], ...}
        “vserver”: {“compute”: [...], “network”: [...],...]
    }
    """
    menus = dict()  # {FIRST_PART_NAME: SECOND_LEVEL_LIST, }
    short_api_warn = 'Detected short API: %s, and this will not be displayed.'
    for url in url_list:
        parts = [u for u in url.split('/') if u]
        if len(parts) < 2:
            # ignore one level urls
            warnings.warn(short_api_warn % url, Warning)
            continue
        first, second = parts[0], parts[1]
        if second.startswith('<'):
            # if second part is a pattern, ignore it
            warnings.warn(short_api_warn % url, Warning)
            continue
        if first not in menus:
            menus[first] = dict()
        if second not in menus[first]:
            menus[first][second] = list()

        # remove patterns
        named_parts = list(filter(lambda x: not x.startswith('<'), parts))

        second_name = named_parts[1]
        if second_name not in menus[first][second]:
            menus[first][second].append(second_name)

    return menus


queries = cache.get(API_QUERIES_KEY, [])


class ShowAPI(TemplateView):
    """
    显示所有URL和对应的doc注释
    """
    template_name = 'api/api.html'

    def dispatch(self, request, *args, **kwargs):
        if settings.DEBUG is False:
            # Only available on DEBUG=True
            return response_for_exception(request, Http404())
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        token = get_token(request)
        response.set_cookie('csrftoken', token)
        return response

    def get_context_data(self, **kwargs):
        query = self.request.GET.get('query', '').strip()
        prefix = self.request.GET.get('prefix', '')
        kwargs = generate_menu_context(prefix=prefix, query=query, context=kwargs)
        return kwargs

    def http_method_not_allowed(self, request, *args, **kwargs):
        return
