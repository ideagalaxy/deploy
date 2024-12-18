# Generated by Django 5.1.1 on 2024-11-11 15:30

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0003_exchange"),
    ]

    operations = [
        migrations.CreateModel(
            name="Log",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("username", models.CharField(max_length=100)),
                ("currency", models.CharField(max_length=100)),
                ("change", models.IntegerField(default=0)),
                ("reg_time", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
