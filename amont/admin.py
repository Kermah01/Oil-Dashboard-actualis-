from django.contrib import admin
from django.core.cache import cache
from . import models as m

admin.site.site_header = "AMONT·CI — Back-office des données"
admin.site.site_title = "AMONT·CI"


class Base(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.delete("bundle")


@admin.register(m.Bloc)
class BlocAdmin(Base):
    list_display = ("code", "zone", "statut_2024", "statut_2026", "operateur", "operateur_2026", "date_cpp", "superficie_km2")
    list_filter = ("zone", "statut_2024", "statut_2026", "operateur")
    search_fields = ("code",)


@admin.register(m.ProductionAnnuelle)
class ProdAdmin(Base):
    list_display = ("champ", "annee", "petrole_bbl", "gaz_mmscf", "ventes_gaz_mmbtu")
    list_filter = ("champ", "annee")


@admin.register(m.Evenement)
class EvAdmin(Base):
    list_display = ("date", "titre", "categorie", "bloc_code", "source")
    list_filter = ("categorie",)


for model in (m.Operateur, m.Champ, m.Forage, m.Puits, m.Exportation, m.RecetteAnnuelle, m.Brent, m.Parametre):
    admin.site.register(model, Base)
