# Generated by Django 5.1.2 on 2024-10-29 05:35

from django.db import migrations, models

import anbieter.fields


class Migration(migrations.Migration):
    dependencies = [
        ("anbieter", "0021_pre_fill_survey"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="umfrageversendung2024",
            options={"verbose_name_plural": "Umfrage: Mailversand"},
        ),
        migrations.RenameField(
            model_name="companysurvey2024",
            old_name="total_kwh_sold_2023",
            new_name="total_mwh_sold_2023",
        ),
        migrations.AlterField(
            model_name="companysurvey2024",
            name="total_mwh_sold_2023",
            field=anbieter.fields.IntegerField(
                blank=True,
                help_text="Wie viele Megawattstunden Strom hat Ihr Unternehmen im Jahr 2023 verkauft?",
                null=True,
                verbose_name="Verkaufter Strom in 2023",
            ),
        ),
        migrations.AlterField(
            model_name="umfrageversendung2024",
            name="mail_status",
            field=models.BooleanField(
                blank=True,
                choices=[(True, "Sent"), (None, "Not sent"), (False, "Sent failed")],
                db_default=None,
                help_text="Status des Mail versand",
                null=True,
                verbose_name="📤 State",
            ),
        ),
    ]
