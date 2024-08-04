from django.contrib import admin

from .models import Anbieter, Oekotest, OkPower, Rowo2019, Stromauskunft, Verivox


@admin.register(Anbieter, OkPower, Oekotest, Rowo2019, Stromauskunft, Verivox)
class AnbieterAdmin(admin.ModelAdmin):
    pass
