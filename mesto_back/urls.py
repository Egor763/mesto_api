from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RegistrationView, CardViewSet, LoginView
from . import views

router = DefaultRouter()
# router.register(r"cards", CardViewSet)

urlpatterns = [
    path("cards", CardViewSet.as_view(), name="cards"),
    # path("users/me", UserViewSet.as_view(), name="users"),
    path("signup", RegistrationView.as_view(), name="register"),
    path("signin", LoginView.as_view(), name="login"),
    # path("review/", views.ReviewCreateView.as_view()),
]
