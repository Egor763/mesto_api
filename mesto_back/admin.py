from django.contrib import admin
from .models import Card, User, Token


class UserAdmin(admin.ModelAdmin):
    # обязательные поля в user
    list_display = ["id", "email"]


class CardAdmin(admin.ModelAdmin):
    # обязательные поля в card
    list_display = ["id", "title"]


# вывод карточек на сайт admin
admin.site.register(Card, CardAdmin)
# вывод пользователей на сайт admin
admin.site.register(User, UserAdmin)
# вывод токена на сайт admin
admin.site.register(Token)
