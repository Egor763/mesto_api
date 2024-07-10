from django.contrib.postgres.fields import ArrayField
from django.db import models
import uuid


# модель пользователя
class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    password = models.CharField(max_length=300, blank=True, null=True)
    avatar = models.CharField(max_length=300, blank=True, null=True)
    about = models.CharField(max_length=100, blank=True, null=True)


# модель карточки
class Card(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.UUIDField(default=uuid.uuid4, blank=True, null=True)
    title = models.CharField(max_length=100)
    link = models.CharField(max_length=300)
    likes = ArrayField(
        models.UUIDField(blank=True, null=True),
        default=list,
        blank=True,
        null=True,
    )


# модель токена
class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(max_length=250, default="token")
    user_id = models.UUIDField(default=uuid.uuid4)
