from django.contrib import admin
from .models import Card, User, Token


class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "email"]


class CardAdmin(admin.ModelAdmin):
    list_display = ["id", "title"]


admin.site.register(Card, CardAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Token)
