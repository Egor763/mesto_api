from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, Card

from .serializer import UserSerializer, TokenSerializer, CardSerializer
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

            card_obj = {
                "title": title,
                "link": link,
                "owner": user["id"],
            }

            # data= сохраняем в БД
            serializer = CardSerializer(data=card_obj)
            if serializer.is_valid():
                serializer.save()
                card = Card.objects.get(owner=user["id"])
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
        if request.method == "DELETE":
            SafeJWTAuthentication.authenticate(self, request)[0]
            # если карточки есть, то карточка удаляется по id
            if cards:
                Card.objects.filter(id=id).delete()
                serializer = CardSerializer(cards, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)


class CardLikeViewSet(APIView):
    def _get_user(self, request, id):
        user = SafeJWTAuthentication.authenticate(self, request)[0]
        # получаем нужную карточку из БД по id из запроса
        card = Card.objects.get(id=id)
        # переводим ее в json
        serializer = CardSerializer(card).data
        return (user, card, serializer)

    def _update_data(self, card, serializer):
        # сериализуем с помощью функции update сериализатора для этого первым аргументом передается карточка (python) вторым
        # аргументом присваеваем data карточку (json) третьим аргументом partial=True если нужно обновить не все поля
        # сравнивает две карточки если есть изменения сохраняет в БД
        serializer_card = CardSerializer(card, data=serializer, partial=True)
        if serializer_card.is_valid():
            serializer_card.save()
            # возвращаем карточку (json)
            return serializer
        else:
            return (
                {
                    "success": False,
                    "message": "Данные карты невалидны",
                },
            )

    def put(self, request, id, format=None):
        if request.method == "PUT":
            user, card, serializer = self._get_user(request, id)

            # проводим нужные изменения
            likes = request.data["likes"]
            likes.append(user["id"])

            # сохраняем изменения в карточки (json)
            serializer["likes"] = likes

            result = self._update_data(card, serializer)
            return Response(result, status=status.HTTP_200_OK)

    def delete(self, request, id, format=None):
        if request.method == "DELETE":

            user, card, serializer = self._get_user(request, id)

            likes = serializer["likes"]
            new_likes = [x for x in likes if x != user["id"]]

            # сохраняем изменения в карточки (json)
            serializer["likes"] = new_likes

            result = self._update_data(card, serializer)
            return Response(result, status=status.HTTP_200_OK)


class UserViewSet(APIView):
    def get(self, request, id, format=None):
        # проверка токена, нужна для защищенной информации
        # SafeJWTAuthentication.authenticate(self, request)

        # вставка без авторизации ======================================
        user = User.objects.filter(id=id).first()
        if user is None:
            # вывод ошибки пользователь не ненайден
            raise exceptions.AuthenticationFailed("Пользователь не найден")

        # self.enforce_csrf(request)
        serializer_user = UserSerializer(user).data
        request.user = serializer_user
        # ========================================================

        user = request.user
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

    def patch(self, request, id, format=None):
        if request.method == "PATCH":
            # user_data = SafeJWTAuthentication.authenticate(self, request)
            # user = user_data[0]
            # вставка без авторизации ======================================
            user_db = User.objects.filter(id=id).first()
            if user_db is None:
                # вывод ошибки пользователь не ненайден
                raise exceptions.AuthenticationFailed("Пользователь не найден")

            # self.enforce_csrf(request)
            user = UserSerializer(user_db).data
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


class LoginView(APIView):
    def post(self, request, format=None):
        email = request.data["email"]
        password = request.data["password"]
        hashed_password = make_password(password=password, salt=SALT)
        try:

            user = User.objects.get(email=email)
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
            del serializer_user["password"]
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
