from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Card

from .serializer import CardSerializer

from .tokens.auth import SafeJWTAuthentication


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
