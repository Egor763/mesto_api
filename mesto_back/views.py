from django.shortcuts import render
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, Token, Card

from .serializer import UserSerializer, TokenSerializer, CardSerializer
from django.conf import settings
from datetime import datetime, timedelta
import hashlib
import uuid
from django.utils import timezone
from .tokens.create_tokens import generate_access_token, generate_refresh_token
from rest_framework import exceptions
from .tokens.auth import SafeJWTAuthentication

# соль хэширует пароль
SALT = (
    "8b4f6b2cc1868d75ef79e5cfb8779c11b6a374bf0fce05b485581bf4e1e25b96c8c2855015de8449"
)


# класс регистрации
class RegistrationView(APIView):
    def post(self, request, format=None):
        # хэширование пароля
        request.data["password"] = make_password(
            password=request.data["password"], salt=SALT
        )
        serializer = UserSerializer(data=request.data)
        # если сериализатор валидный то он сохраняется и возвращается ответ с ключом True со статусом 200 OK
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "You are now registered on our website!"},
                status=status.HTTP_200_OK,
            )
        # если сериализатор не валидный то возвращается ответ с ключом False со статусом 200 OK
        else:
            error_msg = ""
            # ошибка
            for key in serializer.errors:
                error_msg += serializer.errors[key][0]
            return Response(
                {"success": False, "message": error_msg},
                status=status.HTTP_200_OK,
            )


class CardViewSet(APIView):
    def get(self, request, format=None):
        # ищется карточка
        cards = Card.objects.all()
        # если карточки есть, то возвращается ответ с сериализатором и статусом 200 OK
        if cards:
            serializer_card = CardSerializer(cards, many=True)
            return Response(serializer_card.data, status=status.HTTP_200_OK)
        # если карточек нет, то возвращается ответ с ключом False и статусом 200 OK
        else:
            return Response(
                {
                    "success": False,
                    "message": "Карточки не найдены",
                },
                status=status.HTTP_200_OK,
            )

    def post(self, request, format=None):
        if request.method == "POST":
            user = SafeJWTAuthentication.authenticate(self, request)[0]
            title = request.data["title"]
            link = request.data["link"]
            serializer_user = UserSerializer(user).data

            card_obj = {
                "title": title,
                "link": link,
                "owner": serializer_user["id"],
            }

            # data= сохраняем в БД
            serializer = CardSerializer(data=card_obj)
            if serializer.is_valid():
                serializer.save()
                card = Card.objects.get(title=title)
                serializer_card = CardSerializer(card).data
                return Response(serializer_card, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "success": False,
                        "message": "Данные карты невалидны",
                    },
                    status=status.HTTP_200_OK,
                )


class CardDeleteViewSet(APIView):
    def delete(self, request, id, format=None):
        cards = Card.objects.all()
        print("id: ", id)
        if request.method == "DELETE":
            user = SafeJWTAuthentication.authenticate(self, request)[0]
            # если карточки есть, то карточка удаляется по id
            if cards:
                Card.objects.filter(id=id).delete()
                serializer = CardSerializer(cards, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(APIView):
    def get(self, request, format=None):
        # проверка токена, нужна для защищенной информации
        SafeJWTAuthentication.authenticate(self, request)
        serializer = UserSerializer(request.user)
        # если сериализатора нет, то возвращается ответ с ключом False со статусом 200 OK
        if serializer is None:
            return Response(
                {
                    "success": False,
                    "message": "Пользователь не найдены",
                },
                status=status.HTTP_200_OK,
            )

        # если сериализатор есть, то возвращается ответ с данными сериализатора со статусом 200 OK
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)


class LoginView(APIView):
    def post(self, request, format=None):
        print("o")
        email = request.data["email"]
        password = request.data["password"]
        hashed_password = make_password(password=password, salt=SALT)
        try:

            user = User.objects.get(email=email)
            print(user)
        # если пользователь с таким email уже есть то возникает ошибка
        except User.MultipleObjectsReturned:
            raise exceptions.AuthenticationFailed(
                "пользователь с таким email уже зарегистрирован"
            )

        # если пользователя нет или пароль не равен хэшированному паролю, то возвращается ответ с сключом False со статусом 200 OK
        if user is None or user.password != hashed_password:
            return Response(
                {
                    "success": False,
                    "message": "Нет такого пользователя",
                },
                status=status.HTTP_200_OK,
            )
        else:
            serializer_user = UserSerializer(user, many=False).data
            access_token = generate_access_token(serializer_user)
            refresh_token = generate_refresh_token(serializer_user)
            token_obj = {"token": refresh_token, "user_id": serializer_user["id"]}
            serializer = TokenSerializer(data=token_obj)

            if serializer.is_valid():
                serializer.save()
            return Response(
                {"token": access_token, "user": serializer_user},
                status=status.HTTP_200_OK,
            )
