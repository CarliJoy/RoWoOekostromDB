from django.core.exceptions import ValidationError
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe

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

    @property
    def extra(self) -> str:
        return ""

    @property
    def details(self) -> str:
        result: str = format_html(
            "<p><h5>{}</h5>Scraped as: <q>{}</q><br />",
            self.__class__.__name__,
            self.name,
        )
        if self.street or self.city or self.plz:
            result += format_html(
                "<strong>Address</strong>: {}, {}, {} <br />",
                self.street,
                self.city,
                self.plz,
            )
        if self.phone or self.fax or self.mail:
            result += mark_safe("<strong>Kontakt</strong>:")
            if self.phone:
                result += format_html(
                    " 📞 <a href='tel:{}'>{}</a> ", self.phone, self.phone
                )
            if self.fax:
                result += format_html(" 📠 {} ", self.fax)
            if self.mail:
                result += format_html(
                    " 📧 <a href='mailto:{}'>{}</a> ", self.mail, self.mail
                )
            result += "<br />"
        if self.homepage:
            result += format_html(
                "Homepage: <a href='{}' target='_blank'>{}</a> <br />",
                self.homepage,
                self.homepage,
            )
        if self.extra:
            result += self.extra + "<br />"
        return mark_safe(result + "</p>")

    @property
    def has_address(self) -> bool:
        return bool(self.street and self.city and self.plz)


class ScrapeBase(AnbieterBase):
    scrape_date = models.DateTimeField()

    class Meta:
        abstract = True


class Oekotest(ScrapeBase):
    tarif = models.CharField(max_length=255, db_default="")
    tarif_url = models.URLField(max_length=512, db_default="")
    bewertung = models.CharField(max_length=255, db_default="")

    @property
    def extra(self) -> str:
        return format_html(
            "Bewertung: <a href='{}' target='_blank'>Tarif {} -> {}</a>",
            self.tarif_url,
            self.tarif,
            self.bewertung,
        )


class OkPower(ScrapeBase):
    tarif = models.CharField(max_length=255, db_default="")
    tarif_url = models.URLField(max_length=512, db_default="")
    cert_info = models.CharField(max_length=255, db_default="")

    @property
    def extra(self) -> str:
        result = format_html("{}: {}", self.tarif, self.cert_info)
        if self.tarif_url:
            # wir kombinieren hier f string und format_html,
            # damit wir result nicht doppelt escapen
            result = format_html(
                f"<a href='{{}}' target='_blank'>{result}</a>", self.tarif_url
            )
        return result


class Rowo2019(ScrapeBase):
    kennzeichnung_url = models.URLField(
        max_length=1024, db_default="", verbose_name="Link Stromkennzeichnung"
    )


class Stromauskunft(ScrapeBase):
    portal_url = models.URLField(max_length=512, db_default="")

    @property
    def extra(self):
        return format_html("<a href='{}' target='_blank'>Quelle</a>'", self.portal_url)


class Verivox(ScrapeBase):
    portal_url = models.URLField(max_length=512, db_default="")

    @property
    def extra(self):
        return format_html("<a href='{}' target='_blank'>Quelle</a>", self.portal_url)


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
        Rowo2019, on_delete=models.SET_NULL, null=True, blank=True, db_default=None
    )
    oekotest = models.OneToOneField(
        Oekotest, on_delete=models.SET_NULL, null=True, blank=True, db_default=None
    )
    ok_power = models.OneToOneField(
        OkPower, on_delete=models.SET_NULL, null=True, blank=True, db_default=None
    )
    stromauskunft = models.OneToOneField(
        Stromauskunft, on_delete=models.SET_NULL, null=True, blank=True, db_default=None
    )
    verivox = models.OneToOneField(
        Verivox, on_delete=models.SET_NULL, null=True, blank=True, db_default=None
    )
    status = models.PositiveIntegerField(
        db_default=0,
        choices={
            0: "0 - Nicht geprüft",
            4: "4 - Existenz geprüft",
            8: "8 - Ökostrom geprüft",
            16: "16 - Ökostrom Anteil geprüft",
            32: "32 - EE Anteil geprüft",
            64: "64 - Zusätzlichkeit geprüft",
            128: "128 - Unabhängigkeit geprüft ",
            256: "256 - Kein Geld Atom/Kohl geprüft",
            512: "512 - Fragebogen versendet",
            1024: "1024 - Fragebogen zurück erhalten",
            2048: "2048 - Fragebogen eingearbeitet",
            4096: "4096 - Prüfung beendet",
        },
    )
    mutter = models.ForeignKey(
        "Anbieter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Mutter Firma",
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
    north_data = models.URLField(
        max_length=1024,
        db_default="",
        verbose_name="North Data Profil",
        blank=True,
    )
    wikipedia = models.URLField(
        max_length=1024,
        db_default="",
        verbose_name="Wikipedia Eintrag",
        blank=True,
    )

    def clean(self):
        """
        Ensure no duplicate names are created
        """
        super().clean()
        try:
            obj = AnbieterName.objects.get(name=self.name)
        except AnbieterName.DoesNotExist:
            return
        if obj.anbieter != self:
            raise ValidationError(
                f"{self.name} ist bereits für {obj.anbieter} in Benutzung."
            )


class AnbieterName(models.Model):
    name = models.CharField(max_length=255, unique=True)
    anbieter = models.ForeignKey(Anbieter, on_delete=models.PROTECT)
    rowo_2019 = models.ForeignKey(
        Rowo2019, on_delete=models.SET_NULL, null=True, blank=True, db_default=None
    )
    oekotest = models.ForeignKey(
        Oekotest, on_delete=models.SET_NULL, null=True, blank=True, db_default=None
    )
    ok_power = models.ForeignKey(
        OkPower, on_delete=models.SET_NULL, null=True, blank=True, db_default=None
    )
    stromauskunft = models.ForeignKey(
        Stromauskunft, on_delete=models.SET_NULL, null=True, blank=True, db_default=None
    )
    verivox = models.ForeignKey(
        Verivox, on_delete=models.SET_NULL, null=True, blank=True, db_default=None
    )

    def __str__(self) -> str:
        return self.name
