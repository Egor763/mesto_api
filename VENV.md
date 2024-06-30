### Venv

##### web_py - проект

1. Создание `python -m venv venv`
2. Активация получилось через командную строку windows `call venv/Scripts/activate`
3. Должно получится (`(venv) C:\dev\web_py>`)
4. установка django проекта `python -m django startproject web_py`
5. Установка БД `python web_py/manage.py migrate` (`web_py/manage.py` - web_py/ папка лишняя можно удалить и использовать команду manage.py) должен установиться в корне `db.sqlite3`
6. web_py - главный проект с основными настройками в который вкладывается рабочий проект
7. Создаем рабочий проект mesto `python manage.py startapp mesto`
8. Устанавливаем rest `pip install djangorestframework`
9. Добавить в settings.py

```python
INSTALLED_APPS = [
    "mesto", # рабочий проект
    "web_pys", # главный проект
    "corsheaders", # cors
    "rest_framework", # rest
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
```

10. Создаем модель для БД (создается модель дял каждй коллекции)

```python
from django.db import models

# 3 элемента name, link, owner с подбором типов
class Card(models.Model):
    name = models.CharField(max_length=50)
    link = models.CharField(max_length=100)
    owner = models.CharField(max_length=100)

    # возвращает элемент по которому ищется
    def __str__(self):
        return self.name
```

после каждого изменения или дополнения любой модели выполняются эти две команды

`python manage.py makemigrations`
`python manage.py migrate`
должен добавится файл в папку migrations `0001_initial.py`

11. Создаем файл `serializer.py` (serializer преобразует формат python в json)

```python
from rest_framework import serializers
from .models import Card


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = "__all__" # или fields = ['name', 'detail'] - перечисление элементов модели
```

12. В файле `views.py`

```python
from django.shortcuts import render

from rest_framework import viewsets
from .models import Card
from .serializer import CardSerializer


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
```

13. Главный файл `urls.py`

```python
from django.contrib import admin
from django.urls import path, include


urlpatterns = [path("admin/", admin.site.urls), path("", include("mesto.urls"))]
```

В файл рабочего проекта добавляем

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CardViewSet

router = DefaultRouter()
router.register(r"cards", CardViewSet) # r"cards" - эндпоинт по которому происходит запрос в БД

urlpatterns = [
    path("api/", include(router.urls)), # добавляем api после localhost:8000
]
```

14. Устанавливаем CORS `pip install django-cors-headers` и добавляем в `settings.py`

```python
# HTTP
INSTALLED_APPS = [
    # ...
    'corsheaders',
    # ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # устанавливается сверху

    # ...
]


CORS_ORIGIN_WHITELIST = [
     'http://localhost:3000',  # разрешаем адрес нашего фронтенда
]
```
