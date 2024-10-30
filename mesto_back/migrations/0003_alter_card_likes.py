# Generated by Django 5.0.6 on 2024-07-06 14:12

import django.contrib.postgres.fields
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mesto_back", "0002_card_likes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="card",
            name="likes",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.UUIDField(blank=True, default=uuid.uuid4, null=True),
                default=list,
                null=True,
                size=None,
            ),
        ),
    ]