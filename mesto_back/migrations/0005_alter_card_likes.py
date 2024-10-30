# Generated by Django 5.0.6 on 2024-07-08 10:58

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mesto_back", "0004_alter_card_likes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="card",
            name="likes",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.UUIDField(blank=True, null=True),
                blank=True,
                default=list,
                null=True,
                size=None,
            ),
        ),
    ]