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

SALT = (
    "8b4f6b2cc1868d75ef79e5cfb8779c11b6a374bf0fce05b485581bf4e1e25b96c8c2855015de8449"
)


class RegistrationView(APIView):
    def post(self, request, format=None):
        request.data["password"] = make_password(
            password=request.data["password"], salt=SALT
        )
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "You are now registered on our website!"},
                status=status.HTTP_200_OK,
            )
        else:
            error_msg = ""
            for key in serializer.errors:
                error_msg += serializer.errors[key][0]
            return Response(
                {"success": False, "message": error_msg},
                status=status.HTTP_200_OK,
            )


class CardViewSet(APIView):
    def get(self, request, format=None):
        cards = Card.objects.all()
        if cards:
            serializer_card = CardSerializer(cards, many=True)
            return Response(serializer_card.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {
                    "success": False,
                    "message": "Карточки не найдены",
                },
                status=status.HTTP_200_OK,
            )


class UserViewSet(APIView):
    def get(self, request, format=None):
        serializer = UserSerializer(request.user)
        if serializer is None:
            return Response(
                {
                    "success": False,
                    "message": "Пользователь не найдены",
                },
                status=status.HTTP_200_OK,
            )

        else:
            return Response(serializer.data, status=status.HTTP_200_OK)


class LoginView(APIView):
    def post(self, request, format=None):
        email = request.data["email"]
        password = request.data["password"]
        hashed_password = make_password(password=password, salt=SALT)
        try:

            user = User.objects.get(email=email)
            print(user)

        except User.MultipleObjectsReturned:
            raise exceptions.AuthenticationFailed(
                "пользователь с таким email уже зарегистрирован"
            )

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
