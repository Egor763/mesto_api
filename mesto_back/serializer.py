from rest_framework import serializers
from .models import User, Card, Token


# сериализатор пользователя
class UserSerializer(serializers.ModelSerializer):
    # обязательный класс Meta
    class Meta:
        model = User
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.about = validated_data.get("about", instance.about)
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.save()
        return instance


# сериализатор карточки
class CardSerializer(serializers.ModelSerializer):
    # обязательный класс Meta
    class Meta:
        model = Card
        fields = ("id", "title", "link", "owner", "likes")

    # для обновления элементов в БД
    def update(self, instance, validated_data):
        # добавляются поля которые будут обновлятся
        instance.likes = validated_data.get("likes", instance.likes)
        instance.save()
        return instance


# сериализатор токена
class TokenSerializer(serializers.ModelSerializer):
    # обязательный класс Meta
    class Meta:
        model = Token
        fields = "__all__"
