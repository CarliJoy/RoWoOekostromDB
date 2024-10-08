# Generated by Django 5.0.7 on 2024-08-04 13:09

import django.db.models.deletion
from django.db import migrations, models

import anbieter.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("anbieter", "0001_init_superuser"),
    ]

    operations = [
        migrations.CreateModel(
            name="Oekotest",
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
                ("name", models.CharField(max_length=255, unique=True)),
                ("street", models.CharField(blank=True, db_default="", max_length=255)),
                ("city", models.CharField(blank=True, db_default="", max_length=255)),
                ("plz", models.CharField(blank=True, db_default="", max_length=255)),
                ("phone", models.CharField(blank=True, db_default="", max_length=255)),
                ("fax", models.CharField(blank=True, db_default="", max_length=255)),
                (
                    "note",
                    models.TextField(
                        blank=True, db_default="", help_text="Interne Notizen"
                    ),
                ),
                ("mail", models.EmailField(blank=True, db_default="", max_length=255)),
                (
                    "homepage",
                    models.URLField(blank=True, db_default="", max_length=1024),
                ),
                ("scrape_date", models.DateTimeField()),
                ("tarif", models.CharField(db_default="", max_length=255)),
                ("tarif_url", models.URLField(db_default="", max_length=512)),
                ("bewertung", models.CharField(db_default="", max_length=255)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="OkPower",
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
                ("name", models.CharField(max_length=255, unique=True)),
                ("street", models.CharField(blank=True, db_default="", max_length=255)),
                ("city", models.CharField(blank=True, db_default="", max_length=255)),
                ("plz", models.CharField(blank=True, db_default="", max_length=255)),
                ("phone", models.CharField(blank=True, db_default="", max_length=255)),
                ("fax", models.CharField(blank=True, db_default="", max_length=255)),
                (
                    "note",
                    models.TextField(
                        blank=True, db_default="", help_text="Interne Notizen"
                    ),
                ),
                ("mail", models.EmailField(blank=True, db_default="", max_length=255)),
                (
                    "homepage",
                    models.URLField(blank=True, db_default="", max_length=1024),
                ),
                ("scrape_date", models.DateTimeField()),
                ("tarif", models.CharField(db_default="", max_length=255)),
                ("tarif_url", models.URLField(db_default="", max_length=512)),
                ("cert_info", models.CharField(db_default="", max_length=255)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Rowo2019",
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
                ("name", models.CharField(max_length=255, unique=True)),
                ("street", models.CharField(blank=True, db_default="", max_length=255)),
                ("city", models.CharField(blank=True, db_default="", max_length=255)),
                ("plz", models.CharField(blank=True, db_default="", max_length=255)),
                ("phone", models.CharField(blank=True, db_default="", max_length=255)),
                ("fax", models.CharField(blank=True, db_default="", max_length=255)),
                (
                    "note",
                    models.TextField(
                        blank=True, db_default="", help_text="Interne Notizen"
                    ),
                ),
                ("mail", models.EmailField(blank=True, db_default="", max_length=255)),
                (
                    "homepage",
                    models.URLField(blank=True, db_default="", max_length=1024),
                ),
                ("scrape_date", models.DateTimeField()),
                (
                    "kennzeichnung_url",
                    models.URLField(
                        db_default="",
                        max_length=1024,
                        verbose_name="Link Stromkennzeichnung",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Stromauskunft",
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
                ("name", models.CharField(max_length=255, unique=True)),
                ("street", models.CharField(blank=True, db_default="", max_length=255)),
                ("city", models.CharField(blank=True, db_default="", max_length=255)),
                ("plz", models.CharField(blank=True, db_default="", max_length=255)),
                ("phone", models.CharField(blank=True, db_default="", max_length=255)),
                ("fax", models.CharField(blank=True, db_default="", max_length=255)),
                (
                    "note",
                    models.TextField(
                        blank=True, db_default="", help_text="Interne Notizen"
                    ),
                ),
                ("mail", models.EmailField(blank=True, db_default="", max_length=255)),
                (
                    "homepage",
                    models.URLField(blank=True, db_default="", max_length=1024),
                ),
                ("scrape_date", models.DateTimeField()),
                ("portal_url", models.URLField(db_default="", max_length=512)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Verivox",
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
                ("name", models.CharField(max_length=255, unique=True)),
                ("street", models.CharField(blank=True, db_default="", max_length=255)),
                ("city", models.CharField(blank=True, db_default="", max_length=255)),
                ("plz", models.CharField(blank=True, db_default="", max_length=255)),
                ("phone", models.CharField(blank=True, db_default="", max_length=255)),
                ("fax", models.CharField(blank=True, db_default="", max_length=255)),
                (
                    "note",
                    models.TextField(
                        blank=True, db_default="", help_text="Interne Notizen"
                    ),
                ),
                ("mail", models.EmailField(blank=True, db_default="", max_length=255)),
                (
                    "homepage",
                    models.URLField(blank=True, db_default="", max_length=1024),
                ),
                ("scrape_date", models.DateTimeField()),
                ("portal_url", models.URLField(db_default="", max_length=512)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Anbieter",
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
                ("name", models.CharField(max_length=255, unique=True)),
                ("street", models.CharField(blank=True, db_default="", max_length=255)),
                ("city", models.CharField(blank=True, db_default="", max_length=255)),
                ("plz", models.CharField(blank=True, db_default="", max_length=255)),
                ("phone", models.CharField(blank=True, db_default="", max_length=255)),
                ("fax", models.CharField(blank=True, db_default="", max_length=255)),
                (
                    "note",
                    models.TextField(
                        blank=True, db_default="", help_text="Interne Notizen"
                    ),
                ),
                ("mail", models.EmailField(blank=True, db_default="", max_length=255)),
                (
                    "homepage",
                    models.URLField(blank=True, db_default="", max_length=1024),
                ),
                (
                    "active",
                    models.BooleanField(
                        db_default=True,
                        default=True,
                        help_text="Gibt es den Anbieter noch?",
                    ),
                ),
                (
                    "kennzeichnung_url",
                    models.URLField(
                        db_default="",
                        max_length=1024,
                        blank=True,
                        verbose_name="Link Stromkennzeichnung",
                    ),
                ),
                (
                    "ee_anteil",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        help_text="Anteil Erneuerbare Energien in Prozent",
                        null=True,
                        validators=[anbieter.models.is_percentage],
                        verbose_name="EE Anteil [%]",
                    ),
                ),
                (
                    "nur_oeko",
                    models.BooleanField(
                        blank=True,
                        choices=[
                            (True, "Erfüllt"),
                            (False, "Nicht erfüllt"),
                            (None, "?"),
                        ],
                        db_default=None,
                        help_text=(
                            "Der Anbieter verkauft ausschließlich Strom aus erneuerbaren Quellen "
                            "über direkte Lieferverträge mit Erzeugerkraftwerken oder Zwischenhändlern."
                        ),
                        null=True,
                        verbose_name="100% Ökostrom",
                    ),
                ),
                (
                    "unabhaengigkeit",
                    models.BooleanField(
                        blank=True,
                        choices=[
                            (True, "Erfüllt"),
                            (False, "Nicht erfüllt"),
                            (None, "?"),
                        ],
                        db_default=None,
                        help_text=(
                            "Der Anbieter ist nicht direkt mit Konzernen verbunden, "
                            "die Atom- oder Kohlekraftwerke betreiben oder Strom aus diesen Quellen handeln."
                        ),
                        null=True,
                        verbose_name="Unabhängigkeit",
                    ),
                ),
                (
                    "zusaetzlichkeit",
                    models.BooleanField(
                        blank=True,
                        choices=[
                            (True, "Erfüllt"),
                            (False, "Nicht erfüllt"),
                            (None, "?"),
                        ],
                        db_default=None,
                        help_text=(
                            "Der Anbieter fördert die Energiewende durch Strombezug "
                            "aus Neuanlagen und/oder feste Investitionsprogramme."
                        ),
                        null=True,
                        verbose_name="Zusätzlichkeit",
                    ),
                ),
                (
                    "money_for_ee_only",
                    models.BooleanField(
                        blank=True,
                        choices=[
                            (True, "Erfüllt"),
                            (False, "Nicht erfüllt"),
                            (None, "?"),
                        ],
                        db_default=None,
                        help_text=(
                            "Der Anbieter bezieht Strom von Anlagen mit geringen Verflechtungen "
                            "mit Kohle- oder Atomkonzernen. "
                            "Neuinvestitionen in Kohle- und Atomkraftwerke sind nicht zulässig."
                        ),
                        null=True,
                        verbose_name="💰 Kein Geld für Kohle und Atom",
                    ),
                ),
                (
                    "begruendung",
                    models.TextField(
                        blank=True,
                        help_text="Kurz Begründung warum Kriterien ausgewählt wurden. Wird veröffentlicht.",
                        verbose_name="Begründung",
                    ),
                ),
                (
                    "oekotest",
                    models.OneToOneField(
                        blank=True,
                        db_default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="anbieter.oekotest",
                    ),
                ),
                (
                    "ok_power",
                    models.OneToOneField(
                        blank=True,
                        db_default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="anbieter.okpower",
                    ),
                ),
                (
                    "rowo_2019",
                    models.OneToOneField(
                        blank=True,
                        db_default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="anbieter.rowo2019",
                    ),
                ),
                (
                    "stromauskunft",
                    models.OneToOneField(
                        blank=True,
                        db_default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="anbieter.stromauskunft",
                    ),
                ),
                (
                    "verivox",
                    models.OneToOneField(
                        blank=True,
                        db_default=None,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="anbieter.verivox",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
