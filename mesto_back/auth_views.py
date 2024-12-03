import jwt
from django.conf import settings


from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, Token

from .serializer import UserSerializer, TokenSerializer
from .tokens.create_tokens import (
    generate_access_token,
    generate_refresh_token,
)
from .tokens.auth import SafeJWTAuthentication
from rest_framework import exceptions


SALT = (
    "8b4f6b2cc1868d75ef79e5cfb8779c11b6a374bf0fce05b485581bf4e1e25b96c8c2855015de8449"
)


class RegistrationView(APIView):
    def post(self, request, format=None):
        # хэширование пароля
        request.data["password"] = make_password(
            password=request.data["password"], salt=SALT
        )

        email = request.data["email"]

        user = User.objects.filter(email=email).first()

        if user:
            return Response(
                {
                    "success": False,
                    "message": "пользователь с таким email уже зарегистрирован",
                },
                status=status.HTTP_200_OK,
            )

        serializer = UserSerializer(data=request.data)
        # если сериализатор валидный то он сохраняется и возвращается ответ с ключом True со статусом 200 OK
        if serializer.is_valid():
            serializer.save()
            user_db = User.objects.filter(email=email).first()

            serializer_user = UserSerializer(user_db).data

            access_token = generate_access_token(serializer_user["id"])
            refresh_token = generate_refresh_token(serializer_user["id"])
            token_obj = {
                "token": refresh_token,
                "user_id": serializer_user["id"],
            }
            serializer_token = TokenSerializer(data=token_obj)

            if serializer_token.is_valid():
                serializer_token.save()

            return Response(
                {
                    "success": True,
                    "user": serializer_user,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
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


class LoginView(APIView):
    def post(self, request, format=None):
        email = request.data["email"]
        password = request.data["password"]

        user_db = User.objects.filter(email=email).first()

        if user_db is None:
            raise exceptions.AuthenticationFailed(
                "Пользователь с таким email не найден"
            )

        user = UserSerializer(user_db).data

        hashed_password = make_password(password=password, salt=SALT)

        # если пользователя нет или пароль не равен хэшированному паролю, то возвращается ответ с сключом False со статусом 200 OK
        if (
            user is None
            or user["email"] != email
            or user["password"] != hashed_password
        ):
            return Response(
                {
                    "success": False,
                    "message": "Нет такого пользователя",
                },
                status=status.HTTP_200_OK,
            )
        else:
            # serializer_user = UserSerializer(user, many=False).data
            del user["password"]
            token = Token.objects.filter(user_id=user["id"]).first()

            serializer = TokenSerializer(token).data
            access_token = generate_access_token(user["id"])
            if token:

                return Response(
                    {
                        "success": True,
                        "user": user,
                        "access_token": access_token,
                        "refresh_token": serializer["token"],
                    },
                    status=status.HTTP_200_OK,
                )

            else:
                refresh_token = generate_refresh_token(user["id"])
                token_obj = {
                    "token": refresh_token,
                    "user_id": user["id"],
                }
                serializer = TokenSerializer(data=token_obj)

                if serializer.is_valid():
                    serializer.save()
                    return Response(
                        {
                            "success": True,
                            "user": user,
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                        },
                        status=status.HTTP_200_OK,
                    )


class RefreshToken(APIView):
    def post(self, request, format=None):

        refresh = request.data["refresh"]

        user_id = request.data["userId"]

        token = Token.objects.filter(user_id=user_id).first()

        serializer = TokenSerializer(token).data

        if serializer["token"] == refresh:
            access_token = generate_access_token(user_id)
            return Response(
                {
                    "success": True,
                    "access_token": access_token,
                },
                status=status.HTTP_200_OK,
            )

        else:
            return Response(
                {
                    "success": False,
                },
                status=status.HTTP_200_OK,
            )
