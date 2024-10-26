# Generated by Django 5.1.2 on 2024-10-26 17:40

from django.db import migrations, models

import anbieter.fields


class Migration(migrations.Migration):
    dependencies = [
        ("anbieter", "0016_fill_survey_access"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="companysurvey2024",
            options={
                "verbose_name": "Umfrage Revision",
                "verbose_name_plural": "Umfrage: Revisionen",
            },
        ),
        migrations.AlterModelOptions(
            name="oekotest",
            options={"verbose_name_plural": "Scrape: Ökopower"},
        ),
        migrations.AlterModelOptions(
            name="okpower",
            options={"verbose_name_plural": "Scrape: OkPower"},
        ),
        migrations.AlterModelOptions(
            name="rowo2019",
            options={"verbose_name_plural": "Scrape: RoWo 2019"},
        ),
        migrations.AlterModelOptions(
            name="stromauskunft",
            options={"verbose_name_plural": "Scrape: Stromauskunft"},
        ),
        migrations.AlterModelOptions(
            name="surveyaccess",
            options={
                "verbose_name": "Umfrage Zugang",
                "verbose_name_plural": "Umfrage: Zugänge",
            },
        ),
        migrations.AlterModelOptions(
            name="verivox",
            options={"verbose_name_plural": "Scrape: Verivox"},
        ),
        migrations.AddField(
            model_name="companysurvey2024",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="surveyaccess",
            name="changed",
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name="companysurvey2024",
            name="power_plants_file",
            field=anbieter.fields.FileField(
                blank=True,
                help_text="Bitte laden Sie die Tabelle hoch.",
                upload_to="uploads/",
                verbose_name="Erzeugungsanlagen Tabelle",
            ),
        ),
        migrations.AlterField(
            model_name="companysurvey2024",
            name="revision",
            field=anbieter.fields.HiddenPositiveIntegerField(default=1),
        ),
    ]
