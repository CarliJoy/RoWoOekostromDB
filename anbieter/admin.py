from django.contrib import admin

from .models import Zertifizierung, HomepageKriterium, Anbieter


@admin.register(Zertifizierung)
class ZertifizierungAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "kommentar")
    search_fields = ("name",)


@admin.register(HomepageKriterium)
class HomepageKriteriumAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "kategorie",
        "teaser",
        "text",
        "link",
        "linktitel",
        "methoden",
        "methoden_link",
        "profil",
        "strommix",
        "empfehlung",
    )
    list_filter = ("profil", "strommix")
    search_fields = ("id",)


@admin.register(Anbieter)
class AnbieterAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "lichtblick_ee",
        "ee_kategorie",
        "rowo_kriterium",
        "homepage_kriterium",
    )
    readonly_fields = ("lichtblick_ee",)
    list_filter = ("anlagen", "gruener_strom", "ok_power", "rowo_kriterium")
    search_fields = ("name",)
    autocomplete_fields = ("homepage_kriterium", "zertifizierung")
    list_per_page = 250

    ordering = ("name",)

    def lichtblick_ee(self, obj: Anbieter):
        return f"{obj.ee_anteil} %"

    lichtblick_ee.short_description = "EE Anteil"
    lichtblick_ee.ordering = "ee_anteil"
