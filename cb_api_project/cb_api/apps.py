from django.apps import AppConfig
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

from cb_api.constants import API_QUERIES_KEY


class APIAppConfig(AppConfig):
    name = 'cb_api'

    def ready(self):
        # clean api page cache
        key = make_template_fragment_key('api_page')
        cache.delete(key)

        # reset api queries cache
        queries = cache.get(API_QUERIES_KEY, [])
        for query in queries:
            key = make_template_fragment_key('api_page', [query])
            cache.delete(key)
        cache.delete(API_QUERIES_KEY)
