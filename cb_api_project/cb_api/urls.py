from django.urls import path
from cb_api.views import ShowAPI

app_name = 'api'

urlpatterns = [
    path('api/', ShowAPI.as_view(), name='api'),
]
