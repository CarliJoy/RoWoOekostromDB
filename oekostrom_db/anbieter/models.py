from django.core.exceptions import ValidationError
from django.db import models

MAX_PERCENTAGE = 100


def is_percentage(value: float | None) -> None:
    if value is None or (0 < value <= MAX_PERCENTAGE):
        return
    raise ValidationError(
        f"Value must be between 0 and 100 or not set. Got '{value}'.",
        code="invalid",
        params={"value": value},
    )


class AnbieterBase(models.Model):
    name = models.CharField(max_length=255, unique=True)

    street = models.CharField(max_length=255, db_default="", blank=True)
    city = models.CharField(max_length=255, db_default="", blank=True)
    plz = models.CharField(max_length=255, db_default="", blank=True)
    phone = models.CharField(max_length=255, db_default="", blank=True)
    fax = models.CharField(max_length=255, db_default="", blank=True)
    note = models.TextField(db_default="", blank=True, help_text="Interne Notizen")
    mail = models.EmailField(max_length=255, db_default="", blank=True)
    homepage = models.URLField(max_length=1024, db_default="", blank=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name


class ScrapeBase(AnbieterBase):
    scrape_date = models.DateTimeField()

    class Meta:
        abstract = True


class Oekotest(ScrapeBase):
    tarif = models.CharField(max_length=255, db_default="")
    tarif_url = models.URLField(max_length=512, db_default="")
    bewertung = models.CharField(max_length=255, db_default="")


class OkPower(ScrapeBase):
    tarif = models.CharField(max_length=255, db_default="")
    tarif_url = models.URLField(max_length=512, db_default="")
    cert_info = models.CharField(max_length=255, db_default="")


class Rowo2019(ScrapeBase):
    kennzeichnung_url = models.URLField(
        max_length=1024, db_default="", verbose_name="Link Stromkennzeichnung"
    )


class Stromauskunft(ScrapeBase):
    portal_url = models.URLField(max_length=512, db_default="")


class Verivox(ScrapeBase):
    portal_url = models.URLField(max_length=512, db_default="")


KRITERIUM = {
    True: "Erfüllt",
    False: "Nicht erfüllt",
    None: "?",
}


class Anbieter(AnbieterBase):
    active = models.BooleanField(
        db_default=True, default=True, help_text="Gibt es den Anbieter noch?"
    )
    kennzeichnung_url = models.URLField(
        max_length=1024,
        db_default="",
        verbose_name="Link Stromkennzeichnung",
        blank=True,
    )
    rowo_2019 = models.OneToOneField(
        Rowo2019, on_delete=models.CASCADE, null=True, blank=True, db_default=None
    )
    oekotest = models.OneToOneField(
        Oekotest, on_delete=models.CASCADE, null=True, blank=True, db_default=None
    )
    ok_power = models.OneToOneField(
        OkPower, on_delete=models.CASCADE, null=True, blank=True, db_default=None
    )
    stromauskunft = models.OneToOneField(
        Stromauskunft, on_delete=models.CASCADE, null=True, blank=True, db_default=None
    )
    verivox = models.OneToOneField(
        Verivox, on_delete=models.CASCADE, null=True, blank=True, db_default=None
    )
    ee_anteil = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[is_percentage],
        verbose_name="EE Anteil [%]",
        help_text="Anteil Erneuerbare Energien in Prozent",
    )
    nur_oeko = models.BooleanField(
        null=True,
        db_default=None,
        blank=True,
        choices=KRITERIUM,
        verbose_name="100% Ökostrom",
        help_text=(
            "Der Anbieter verkauft ausschließlich Strom aus erneuerbaren Quellen "
            "über direkte Lieferverträge mit Erzeugerkraftwerken oder Zwischenhändlern."
        ),
    )
    unabhaengigkeit = models.BooleanField(
        null=True,
        db_default=None,
        blank=True,
        choices=KRITERIUM,
        verbose_name="Unabhängigkeit",
        help_text=(
            "Der Anbieter ist nicht direkt mit Konzernen verbunden, "
            "die Atom- oder Kohlekraftwerke betreiben oder Strom aus diesen Quellen handeln."
        ),
    )
    zusaetzlichkeit = models.BooleanField(
        null=True,
        db_default=None,
        blank=True,
        choices=KRITERIUM,
        verbose_name="Zusätzlichkeit",
        help_text=(
            "Der Anbieter fördert die Energiewende durch Strombezug aus Neuanlagen "
            "und/oder feste Investitionsprogramme."
        ),
    )
    money_for_ee_only = models.BooleanField(
        null=True,
        db_default=None,
        blank=True,
        choices=KRITERIUM,
        verbose_name="Kein Geld für Kohle und Atom",
        help_text=(
            "Der Anbieter bezieht Strom von Anlagen mit geringen Verflechtungen "
            "mit Kohle- oder Atomkonzernen. "
            "Neuinvestitionen in Kohle- und Atomkraftwerke sind nicht zulässig."
        ),
    )
    begruendung = models.TextField(
        blank=True,
        verbose_name="Begründung",
        help_text="Kurz Begründung warum Kriterien ausgewählt wurden. Wird veröffentlicht.",
    )
