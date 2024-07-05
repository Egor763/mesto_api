from rest_framework import serializers
from .models import User, Card, Token


# сериализатор пользователя
class UserSerializer(serializers.ModelSerializer):
    # обязательный класс Meta
    class Meta:
        model = User
        fields = "__all__"


# сериализатор карточки
class CardSerializer(serializers.ModelSerializer):
    # обязательный класс Meta
    class Meta:
        model = Card
        fields = ("id", "title", "link", "owner")


# сериализатор токена
class TokenSerializer(serializers.ModelSerializer):
    # обязательный класс Meta
    class Meta:
        model = Token
        fields = "__all__"
