from django.urls import path

from .views import (
    RegistrationView,
    CardViewSet,
    LoginView,
    UserViewSet,
    CardDeleteViewSet,
    CardLikeViewSet,
    UserAddAvatarViewSet,
)


urlpatterns = [
    path("cards", CardViewSet.as_view(), name="cards"),
    # добавление карточки id
    path("cards/<uuid:id>", CardDeleteViewSet.as_view(), name="cards_delete"),
    path("cards/<uuid:id>/likes", CardLikeViewSet.as_view(), name="likes"),
    path("users/me/<uuid:id>", UserViewSet.as_view(), name="users"),
    path("users/me/<uuid:id>/avatar", UserAddAvatarViewSet.as_view(), name="avatar"),
    path("signup", RegistrationView.as_view(), name="register"),
    path("signin", LoginView.as_view(), name="login"),
]
