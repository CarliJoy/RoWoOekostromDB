import logging
from urllib.parse import urlparse

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
from django.http import HttpRequest
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    Anbieter,
    AnbieterName,
    Oekotest,
    OkPower,
    Rowo2019,
    Stromauskunft,
    Verivox,
)

logger = logging.getLogger(__name__)


@admin.register(OkPower, Oekotest, Rowo2019, Stromauskunft, Verivox)
class ScraperAdmin(admin.ModelAdmin):
    search_fields = ("name",)

    def has_change_permission(self, request, obj=None):  # noqa ARG002
        return False

    def has_add_permission(self, request, obj=None):  # noqa ARG002
        return False

    def has_delete_permission(self, request, obj=None):  # noqa ARG002
        return False


@admin.register(AnbieterName)
class AnbieterNameAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = [
        "name",
        "the_anbieter_id",
        "has_rowo_2019",
        "has_oekotest",
        "has_ok_power",
        "has_stromauskunft",
        "has_verivox",
    ]
    list_per_page = 250

    @admin.display(description="Anbieter", ordering="anbieter__name")
    def the_anbieter_id(self, obj: AnbieterName) -> str:
        return str(obj.anbieter.id)

    @admin.display(
        description="Robinwood 2019", boolean=True, ordering="rowo_2019__name"
    )
    def has_rowo_2019(self, obj: AnbieterName) -> bool:
        return obj.rowo_2019 is not None

    @admin.display(description="Ökotest", boolean=True, ordering="oekotest__name")
    def has_oekotest(self, obj: AnbieterName) -> bool:
        return obj.oekotest is not None

    @admin.display(description="OK Power", boolean=True, ordering="ok_power__name")
    def has_ok_power(self, obj: AnbieterName) -> bool:
        return obj.ok_power is not None

    @admin.display(
        description="Stromauskunft", boolean=True, ordering="stromauskunft__name"
    )
    def has_stromauskunft(self, obj: AnbieterName) -> bool:
        return obj.stromauskunft is not None

    @admin.display(description="Verivox", boolean=True, ordering="verivox__name")
    def has_verivox(self, obj: AnbieterName) -> bool:
        return obj.verivox is not None

    def has_change_permission(self, request, obj=None):  # noqa ARG002
        return False

    def has_delete_permission(self, request, obj=None):  # noqa ARG002
        return False


class FriendshipInline(admin.TabularInline):
    model = AnbieterName
    extra = 1
    fields = ("name",)
    verbose_name_plural = "Alternative Namen für Anbieter"

    def has_change_permission(self, request, obj=None):  # noqa ARG002
        return False

    def has_delete_permission(self, request, obj=None):  # noqa ARG002
        return False


autocomplete_fields = (
    "rowo_2019",
    "oekotest",
    "ok_power",
    "stromauskunft",
    "verivox",
    "mutter",
)


class AnbieterForm(forms.ModelForm):
    class Meta:
        # make autocomplete field larger
        # see https://stackoverflow.com/questions/61679332
        widgets = {
            field: AutocompleteSelect(
                Anbieter._meta.get_field(field),
                admin.site,
                attrs={
                    "data-dropdown-auto-width": "true",
                    "style": "width: 512px",
                },
            )
            for field in autocomplete_fields
        } | {
            "note": forms.Textarea(attrs={"class": "vLargeTextField", "rows": "2"}),
            "plz": forms.TextInput(attrs={"size": "6"}),
        }


@admin.register(Anbieter)
class AnbieterAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = (
        "name",
        "active",
        "has_mutter",
        "status",
        "homepage_url",
        "ee_only",
        "additional",
        "independent",
        "no_bad_money",
    )
    list_filter = [
        "active",
        "status",
        "nur_oeko",
        "zusaetzlichkeit",
        "unabhaengigkeit",
        "money_for_ee_only",
    ]

    change_list_template = "admin/rowo_changelist.html"

    inlines = (FriendshipInline,)
    list_per_page = 1500
    ordering = ("name",)

    form = AnbieterForm
    autocomplete_fields = autocomplete_fields

    @admin.display(description="Homepage", ordering="homepage")
    def homepage_url(self, obj: Anbieter) -> str:
        if not obj.homepage:
            return ""
        url = urlparse(obj.homepage)
        if not url.hostname:
            logger.warning(f"{obj} has invalid homepage url '{obj.homepage}'")
            return ""
        name = url.hostname.removeprefix("www.")
        return format_html(
            "<a href='{url}' target='_blank'>{name}</a>", url=obj.homepage, name=name
        )

    @admin.display(description="Mutter", ordering="mutter", boolean=True)
    def has_mutter(self, obj: Anbieter) -> bool:
        return bool(obj.mutter)

    @admin.display(description="100% Öko", ordering="nur_oeko", boolean=True)
    def ee_only(self, obj: Anbieter) -> bool:
        return obj.nur_oeko

    @admin.display(description="zusatz.", ordering="zusaetzlichkeit", boolean=True)
    def additional(self, obj: Anbieter) -> bool:
        return obj.zusaetzlichkeit

    @admin.display(description="unabh.", ordering="unabhaengigkeit", boolean=True)
    def independent(self, obj: Anbieter) -> bool:
        return obj.unabhaengigkeit

    @admin.display(description="💰", ordering="money_for_ee_only", boolean=True)
    def no_bad_money(self, obj: Anbieter) -> bool:
        return obj.money_for_ee_only

    def such_links(self, obj: Anbieter) -> str:
        return format_html(
            """
            <a href="https://www.google.com/search?q={name}", target="_blank">
                    Google Firmenname</a>, <br />
            <a href="https://www.google.com/search?q={name}+Stromkennzeichnung", target="_blank">
                    Google Stromkennzeichnung</a>, <br />
            <a href="https://www.northdata.de/{name}", target="_blank">
                    North Data</a>, <br />
            <a href="https://de.wikipedia.org/w/index.php?search={name}",target="_blank">
                    Wikipedia</a>, <br />
            """,
            name=obj.name,
        )

    def scrape_info(self, obj: Anbieter) -> str:
        result = ""
        for elm in (
            obj.rowo_2019,
            obj.oekotest,
            obj.ok_power,
            obj.stromauskunft,
            obj.verivox,
        ):
            if elm:
                result += elm.details
        return mark_safe(result)

    readonly_fields = ("scrape_info", "such_links", "last_updated", "created_at")

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "name",
                    "mutter",
                    "active",
                    "status",
                    ("last_updated", "created_at"),
                ]
            },
        ),
        (
            "Kontakt",
            {
                "fields": [
                    "street",
                    ("plz", "city"),
                    "phone",
                    "fax",
                    "note",
                    "mail",
                ]
            },
        ),
        (
            "Kontext",
            {
                "fields": [
                    "scrape_info",
                    "such_links",
                    "homepage",
                    "north_data",
                    "wikipedia",
                ],
                "description": "Hilfreiche Infos für die Recherche",
            },
        ),
        (
            "Prüfung",
            {
                "fields": [
                    "kennzeichnung_url",
                    "ee_anteil",
                    "nur_oeko",
                    "zusaetzlichkeit",
                    "unabhaengigkeit",
                    "money_for_ee_only",
                    "begruendung",
                ]
            },
        ),
        (
            "Scrape Referenz",
            {
                "fields": [
                    "rowo_2019",
                    "oekotest",
                    "ok_power",
                    "stromauskunft",
                    "verivox",
                ],
                "description": "Ändern der Scrape Referenzen",
                "classes": ["collapse"],
            },
        ),
    ]

    def save_model(
        self, request: HttpRequest, obj: Anbieter, form: forms.Form, change: bool
    ) -> None:
        super().save_model(request, obj, form, change)
        # clean should take care that name isn't used already
        if obj.name not in obj.anbietername_set.values_list("name", flat=True):
            AnbieterName.objects.update_or_create(name=obj.name, anbieter=obj)

    def has_delete_permission(self, request, obj=None):  # noqa ARG002
        return False
