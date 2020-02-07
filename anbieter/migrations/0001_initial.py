# Generated by Django 3.0.2 on 2020-02-03 22:42

import django.core.validators
import django.db.models.deletion
import phonenumber_field.modelfields
from django.db import migrations, models

import helpers.model_fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomepageKriterium",
            fields=[
                (
                    "id",
                    models.CharField(
                        max_length=16,
                        primary_key=True,
                        serialize=False,
                        validators=[
                            django.core.validators.RegexValidator(
                                "[a-z][A-Z]*", "Nur Buchstaben sind als ID erlaubt"
                            )
                        ],
                        verbose_name="ID",
                    ),
                ),
                (
                    "kategorie",
                    models.CharField(blank=True, max_length=16, verbose_name="Kategorie"),
                ),
                ("teaser", models.TextField(verbose_name="Teaser")),
                ("text", models.TextField(blank=True, verbose_name="Text")),
                ("link", models.URLField(blank=True, null=True, verbose_name="Link")),
                (
                    "linktitel",
                    models.CharField(
                        blank=True, max_length=128, verbose_name="Linktitel"
                    ),
                ),
                ("methoden", models.TextField(verbose_name="Methoden")),
                (
                    "methoden_link",
                    models.TextField(blank=True, verbose_name="Methodenlink"),
                ),
                ("profil", models.BooleanField(verbose_name="Profil")),
                (
                    "strommix",
                    models.BooleanField(
                        choices=[(None, "?"), (True, "Vorhanden"), (False, "Fehlt")],
                        null=True,
                        verbose_name="Strommix",
                    ),
                ),
                (
                    "empfehlung",
                    models.CharField(
                        choices=[("Y", "yes"), ("N", "no"), ("M", "maybe")],
                        max_length=1,
                        verbose_name="Empfehlung",
                    ),
                ),
            ],
            options={"db_table": "anbieter_kriterium",},
        ),
        migrations.CreateModel(
            name="Zertifizierung",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=64, unique=True, verbose_name="Name"),
                ),
                ("kommentar", models.TextField(verbose_name="Kommentar")),
            ],
            options={"db_table": "anbieter_zertifizierung",},
        ),
        migrations.CreateModel(
            name="Anbieter",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=200, unique=True, verbose_name="Firmenname"
                    ),
                ),
                (
                    "ee_anteil",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=6,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(
                                0, "Der EEG Anteil kann nur zwischen 0% und 100% liegen."
                            ),
                            django.core.validators.MaxLengthValidator(
                                100,
                                "Der EEG Anteil kann nur zwischen 0% und 100% liegen.",
                            ),
                        ],
                        verbose_name="Anteil Erneuerbare Energien (laut Strommix von Lichtblick)",
                    ),
                ),
                (
                    "ee_kategorie",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "Kategorie 1, 0% - 0.99%"),
                            (5, "Kategorie 2, 1% - 4.99%"),
                            (10, "Kategorie 3, 5% - 9.99%"),
                            (20, "Kategorie 4, 10% - 19.99%"),
                            (30, "Kategorie 5, 20% - 29.99%"),
                            (40, "Kategorie 6, 30% - 39.99%"),
                            (50, "Kategorie 7, 40% - 49.99%"),
                            (60, "Kategorie 8, 50% - 59.99%"),
                            (70, "Kategorie 9, 60% - 69.99%"),
                            (80, "Kategorie 10, 70% - 79.99%"),
                            (90, "Kategorie 11, 80% - 89.99%"),
                            (100, "Kategorie 12, 90% - 99.99%"),
                            (101, "Kategorie 13 100%"),
                        ],
                        editable=False,
                        null=True,
                    ),
                ),
                (
                    "strasse",
                    models.CharField(
                        blank=True,
                        help_text="Straßenname mit Hausnummer",
                        max_length=128,
                        verbose_name="Straße",
                    ),
                ),
                (
                    "plz",
                    helpers.model_fields.PostleitzahlField(
                        blank=True, max_length=16, verbose_name="PLZ"
                    ),
                ),
                (
                    "stadt",
                    models.CharField(blank=True, max_length=128, verbose_name="Stadt"),
                ),
                ("homepage", models.URLField(blank=True, verbose_name="Homepage")),
                (
                    "kennzeichnung_link",
                    models.URLField(blank=True, verbose_name="Link der Kennzeichnung"),
                ),
                (
                    "fragebogen",
                    models.CharField(
                        choices=[("", ""), ("x", "x"), ("(x)", "(x)"), ("k.A.", "k.A.")],
                        max_length=5,
                    ),
                ),
                (
                    "rowo_kriterium",
                    models.CharField(
                        choices=[
                            (
                                "X",
                                "X - Überregionale Anbieter mit 100% Ökostrom, Beiträgen zu Förderung der Energiewende und ohne erkennbare Verflechtungen mit Unternehmen die mit Kohle oder Atomstrom handeln oder entsprechende Kraftwerke besitzen",
                            ),
                            (
                                "XX",
                                "XX - Alternative Anbieter mit eher Vermittelnder / Beratender Funktion (z.B. regionale Direktvermarktung aus kleinstanlagen, Mietstromangebote, u.ä.), mit 100% Ökostrom",
                            ),
                            (
                                "R",
                                "R - Regionale Anbieter die den X oder XX Kriterien entsprechen",
                            ),
                            (
                                "RC",
                                "RC - Regionale Anbieter die keinen erkennbare, zusätzlichen Beitrag zur Energiewende leisten",
                            ),
                            (
                                "D",
                                "D - Betreiber von Anlagen aus denen Strom Bezogen produzieren oder verkaufen Strom aus Kohl-Atomenergie",
                            ),
                            (
                                "C",
                                "C - Große, überregionale Anbieter die keinen erkennbare (auch keine eigenen EE Anlagen) zusätzlichen Beitrag zur Energiewende leisten",
                            ),
                            (
                                "B",
                                "B - Eigentumsrechtliche Verflechtungen oder oder Verkauf von nicht regenerativen Energien eines, am Anbieter, beteiligten Unternehmens (Grund in Spalte Begründung angegeben)",
                            ),
                            ("A", "A - keine 100% Ökostrom"),
                            (
                                "0",
                                "0 - Sonstiger Stromanbieter mit Ökostromtarif (Keine Bewertung über die ROBIN WOOD Kriterien da es sich um keinen klassischen Stromanbieter / Stromkenneichung fehlt / Informationen fehlen (z.B. keine Internetpräsenz) oder sonstige Gründe",
                            ),
                            ("", "? - noch nicht geprüft"),
                        ],
                        default="",
                        max_length=3,
                        verbose_name="RoWo Kriterium",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        help_text="Nur für relevante Anbieter benötigt",
                        max_length=254,
                        verbose_name="Kontakt",
                    ),
                ),
                (
                    "telefon",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, region=None, verbose_name="Telefon"
                    ),
                ),
                ("begruendung", models.TextField(blank=True, verbose_name="Begründung")),
                (
                    "anlagen",
                    models.BooleanField(
                        blank=True, default=False, verbose_name="Eigene Anlagen"
                    ),
                ),
                (
                    "anlagen_kommentar",
                    models.TextField(
                        blank=True, verbose_name="Weitere Informationen über Anlagen"
                    ),
                ),
                ("bemerkung", models.TextField(blank=True, verbose_name="Bemerkung")),
                (
                    "gruener_strom",
                    models.BooleanField(blank=True, verbose_name="Grüner Strom Label"),
                ),
                (
                    "ok_power",
                    models.BooleanField(blank=True, verbose_name="OK Power Label"),
                ),
                (
                    "rowo_profil",
                    models.URLField(blank=True, verbose_name="RoWo-Anbieterprofil"),
                ),
                (
                    "homepage_kriterium",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="anbieter.HomepageKriterium",
                        verbose_name="Kriterium-Websuche",
                    ),
                ),
                (
                    "polymorphic_ctype",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="polymorphic_anbieter.anbieter_set+",
                        to="contenttypes.ContentType",
                    ),
                ),
                (
                    "zertifizierung",
                    models.ManyToManyField(
                        blank=True,
                        db_table="anbieter_zertifizierungen",
                        to="anbieter.Zertifizierung",
                        verbose_name="Zertifizierung(en)",
                    ),
                ),
            ],
            options={"db_table": "anbieter",},
        ),
    ]
