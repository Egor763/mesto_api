from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, Card

from .serializer import UserSerializer, TokenSerializer, CardSerializer
from .tokens.create_tokens import (
    generate_access_token,
    generate_refresh_token,
    check_access_token,
)
from rest_framework import exceptions
from .tokens.auth import SafeJWTAuthentication

# соль хэширует пароль
SALT = (
    "8b4f6b2cc1868d75ef79e5cfb8779c11b6a374bf0fce05b485581bf4e1e25b96c8c2855015de8449"
)


class UserViewSet(APIView):
    def get(self, request, format=None):
        # проверка токена, нужна для защищенной информации
        user = SafeJWTAuthentication.authenticate(self, request)[0]

        # вставка без авторизации ======================================
        # user = User.objects.filter(id=id).first()

        # if user is None or user["id"] != id:
        #     # вывод ошибки пользователь не ненайден
        #     raise exceptions.AuthenticationFailed("Пользователь не найден")

        # self.enforce_csrf(request)
        # serializer_user = UserSerializer(user).data
        # request.user = serializer_user
        # ========================================================

        # user = request.user
        # если сериализатора нет, то возвращается ответ с ключом False со статусом 200 OK
        if user is None:
            return Response(
                {
                    "success": False,
                    "message": "Пользователь не найдены",
                },
                status=status.HTTP_200_OK,
            )

        # если сериализатор есть, то возвращается ответ с данными сериализатора со статусом 200 OK
        else:
            del user["password"]
            return Response(user, status=status.HTTP_200_OK)

    def patch(self, request, format=None):
        if request.method == "PATCH":
            user_data = SafeJWTAuthentication.authenticate(self, request)
            user = user_data[0]
            user_db = user_data[1]
            # вставка без авторизации ======================================

            # self.enforce_csrf(request)
            # ========================================================
            name = request.data["name"]
            about = request.data["about"]

            user["name"] = name
            user["about"] = about

            # serializer_user = UserSerializer(user_data[1], data=user, partial=True)
            serializer_user = UserSerializer(user_db, data=user, partial=True)

            if serializer_user.is_valid():
                serializer_user.save()
                del user["password"]
                return Response(user, status=status.HTTP_200_OK)

            else:
                return Response(
                    {
                        "success": False,
                        "message": "Пользователь не валиден",
                    },
                    status=status.HTTP_200_OK,
                )


class UserAddAvatarViewSet(APIView):
    def patch(self, request, id, format=None):
        # user_data = SafeJWTAuthentication.authenticate(self, request)
        # user = user_data[0]

        user_bd = User.objects.filter(id=id).first()

        if user_bd is None:
            raise exceptions.AuthenticationFailed("Пользователь не найден")

        user = UserSerializer(user_bd).data

        avatar = request.data["avatar"]

        user["avatar"] = avatar
        print(user)

        serializer = UserSerializer(user_bd, data=user, partial=True)

        if serializer.is_valid():
            serializer.save()
            del user["password"]
            return Response(user, status=status.HTTP_200_OK)
        else:
            return Response(
                {"success": False, "message": "Аватар не обновился"},
                status=status.HTTP_200_OK,
            )
