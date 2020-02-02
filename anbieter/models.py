from logging import getLogger

from django.core import validators
from django.db import models
from polymorphic.models import PolymorphicModel

from helpers.model_fields import PostleitzahlField

EE_ANTEIL_RANGE_MSG = "Der EEG Anteil kann nur zwischen 0% und 100% liegen."

logger = getLogger("anbieter.models")


class Zertifizierung(models.Model):
    name = models.CharField("Name", unique=True, max_length=64)
    kommentar = models.TextField("Kommentar")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "anbieter_zertifizierung"


class HomepageKriterium(models.Model):
    id = models.CharField(
        "ID",
        validators=[
            validators.RegexValidator("[a-z][A-Z]*", "Nur Buchstaben sind als ID erlaubt")
        ],
        max_length=16,
        primary_key=True,
    )
    kategorie = models.CharField("Kategorie", max_length=16, blank=True)
    teaser = models.TextField("Teaser")
    text = models.TextField("Text", blank=True)
    link = models.URLField("Link", blank=True, null=True)
    linktitel = models.CharField("Linktitel", blank=True, max_length=128)
    methoden = models.TextField("Methoden")
    methoden_link = models.TextField("Methodenlink", blank=True)
    profil = models.BooleanField("Profil")
    strommix = models.BooleanField(
        "Strommix",
        null=True,
        choices=((None, "?"), (True, "Vorhanden"), (False, "Fehlt")),
    )
    empfehlung = models.CharField(
        "Empfehlung", max_length=1, choices=(("Y", "yes"), ("N", "no"), ("M", "maybe"))
    )

    def __str__(self):
        return self.id

    class Meta:
        db_table = "anbieter_kriterium"


class Anbieter(PolymorphicModel):
    MAX_EE_KATEGORIE = 101
    EE_KATEGORIEN = (
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
    )

    name = models.CharField("Firmenname", max_length=256, unique=True)
    ee_anteil = models.DecimalField(
        verbose_name="Anteil Erneuerbare Energien " "(laut Strommix von Lichtblick)",
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            validators.MinValueValidator(0, EE_ANTEIL_RANGE_MSG),
            validators.MaxLengthValidator(100, EE_ANTEIL_RANGE_MSG),
        ],
    )
    ee_kategorie = models.PositiveSmallIntegerField(
        choices=EE_KATEGORIEN, editable=False, null=True,
    )
    strasse = models.CharField(
        "Straße", max_length=128, help_text="Straßenname mit Hausnummer"
    )
    plz = PostleitzahlField("PLZ")
    stadt = models.CharField("Stadt", max_length=128)
    homepage = models.URLField("Homepage")
    kennzeichnung_link = models.URLField()
    fragebogen = models.CharField(
        choices=((val, val) for val in ["", "x", "(x)", "k.A."]), max_length=5
    )
    rowo_kriterium = models.CharField(
        "RoWo Kriterium",
        choices=((val, val) for val in ["", "x", "(x)", "k.A."]),
        max_length=5,
    )
    homepage_kriterium = models.ForeignKey(
        HomepageKriterium, verbose_name="Kriterium-Websuche", on_delete=models.PROTECT,
    )
    begruendung = models.TextField("Begründung", blank=True)
    anlagen = models.BooleanField("Eigene Anlagen", default=False, blank=True)
    zertifizierung = models.ManyToManyField(
        Zertifizierung,
        verbose_name="Zertifizierung(en)",
        blank=True,
        db_table="anbieter_zertifizierungen",
    )
    bemerkung = models.TextField("Bemerkung", blank=True)
    gruener_strom = models.BooleanField("Grüner Strom Label", blank=True)
    ok_power = models.BooleanField("OK Power Label", blank=True)
    rowo_profil = models.URLField("RoWo-Anbieterprofil", blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Make save object make sure the correct category is selected
        """

        def select_correct_category():
            if self.ee_anteil is None:
                self.ee_kategorie = None
            for max_percent, name in self.EE_KATEGORIEN:
                if self.ee_anteil < max_percent:
                    self.ee_kategorie = max_percent
                    break
            else:
                logger.warning(f"Invalid percentage value {self.ee_anteil} for {self}")

        select_correct_category()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "anbieter"
