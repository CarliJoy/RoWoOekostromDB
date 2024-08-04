from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect

from .models import Anbieter, Oekotest, OkPower, Rowo2019, Stromauskunft, Verivox


@admin.register(OkPower, Oekotest, Rowo2019, Stromauskunft, Verivox)
class ScraperAdmin(admin.ModelAdmin):
    search_fields = ("name",)


autocomplete_fields = (
    "rowo_2019",
    "oekotest",
    "ok_power",
    "stromauskunft",
    "verivox",
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
    form = AnbieterForm
    autocomplete_fields = autocomplete_fields
