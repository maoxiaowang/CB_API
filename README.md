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
4. 全局配置项API_RESULT_FIELD表示在返回的json字段中表示结果是否正确的字段名，默认为“result”。

比如返回的结果如下所示，用success来表示成功与否
```json
{
  "success": true,
  "code": 111,
  "message": "test msg",
  "data": {}
}
```
那么，需要在Project/settings.py中配置如下：
```python
CBAPI_RESULT_FIELD = "success"
```
> 页面会根据这个值来判断返回结果是否正确,该配置不会影响测试结果，只影响显示效果。

## 示例截图

![screenshot1.png](https://github.com/maoxiaowang/CB_API/blob/master/screenshot1.png)
