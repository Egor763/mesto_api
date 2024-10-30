# Generated by Django 5.0.6 on 2024-07-04 14:38

import django.contrib.postgres.fields
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mesto_back", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="card",
            name="likes",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.UUIDField(blank=True, default=uuid.uuid4, null=True),
                default=[],
                size=None,
            ),
        ),
    ]