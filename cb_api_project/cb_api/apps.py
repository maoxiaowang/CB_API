from django.apps import AppConfig
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key


class APIAppConfig(AppConfig):
    name = 'cb_api'
    # default settings
    API_RESULT_FIELD = 'success'

    def ready(self):
        # clean api page cache
        key = make_template_fragment_key('api_page')
        cache.delete(key)

        # reset api queries cache
        queries = cache.get('api_queries', [])
        for query in queries:
            key = make_template_fragment_key('api_page', [query])
            cache.delete(key)
        cache.delete('api_queries')
