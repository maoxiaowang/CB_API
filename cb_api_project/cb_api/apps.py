from django.apps import AppConfig
from django.conf import settings
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key


class APIAppConfig(AppConfig):
    name = 'cb_api'
    # default settings
    CBAPI_RESULT_FIELD = 'result'
    CBAPI_QUERIES_KEY = 'api_queries'

    def ready(self):
        # clean api page cache
        key = make_template_fragment_key('api_page')
        cache.delete(key)

        # reset api queries cache
        queries = cache.get(settings.CBAPI_QUERIES_KEY, [])
        for query in queries:
            key = make_template_fragment_key('api_page', [query])
            cache.delete(key)
        cache.delete(settings.CBAPI_QUERIES_KEY)
