from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
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
        }


@admin.register(Anbieter)
class AnbieterAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "active", "homepage_url")
    inlines = (FriendshipInline,)
    list_per_page = 1500
    ordering = ("name",)

    form = AnbieterForm
    autocomplete_fields = autocomplete_fields

    def homepage_url(self, obj: Anbieter) -> str:
        return mark_safe(f"<a href='{obj.homepage}'>{obj.homepage}</a>")

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

    readonly_fields = ("scrape_info",)

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))

        insert_at = fields.index("active")
        fields.insert(insert_at, "scrape_info")

        return fields

    def has_delete_permission(self, request, obj=None):  # noqa ARG002
        return False
