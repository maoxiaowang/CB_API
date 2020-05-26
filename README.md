# CB_API - Django Class-based API Document and Testing

基于类视图的API文档，可在线测试接口

## 使用方法

1. 将cb_api目录复制到你的Django项目下
2. 在settings.py中加入App“cb_api”，推荐"cb_api.apps.APIAppConfig"
```python
INSTALLED_APPS = [
    ...
    'cb_api.apps.APIAppConfig',
]
```
3. 在根urls.py中导入视图并添加url
```python
from cb_api.views import ShowAPI

urlpatterns = [
    ...
    path('api/', ShowAPI.as_view(), name='api'),
]
```
