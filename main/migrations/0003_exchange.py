# Generated by Django 5.1.1 on 2024-09-17 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0002_bankbook"),
    ]

    operations = [
        migrations.CreateModel(
            name="Exchange",
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
                ("dollar2won", models.IntegerField(default=0)),
                ("yenn2won", models.IntegerField(default=0)),
                ("pesso2won", models.IntegerField(default=0)),
            ],
        ),
    ]
