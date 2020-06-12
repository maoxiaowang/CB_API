# CB_API

Django Class-based API Document and Testing，基于类视图的API文档，可在线测试接口

## 适用版本

Django 2.0+，且使用通用类视图

## 使用方法

1. 将cb_api目录复制到Django项目下
2. 在settings.py中加入App“cb_api”
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

## 示例截图
[截图](http://cdn.sandbook.club/cb_api.png)
