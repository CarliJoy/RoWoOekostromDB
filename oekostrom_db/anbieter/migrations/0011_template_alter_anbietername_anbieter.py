# Generated by Django 5.1.2 on 2024-10-09 19:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("anbieter", "0010_anbieter_begruendung_extern_anbieter_sells_from_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Template",
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
                (
                    "name",
                    models.CharField(
                        choices=[("HP_EXPORT", "Homepage Text")],
                        max_length=64,
                        unique=True,
                    ),
                ),
                ("template", models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name="anbietername",
            name="anbieter",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="names",
                to="anbieter.anbieter",
            ),
        ),
    ]
