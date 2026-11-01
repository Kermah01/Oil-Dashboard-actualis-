from django.db import models

STATUTS = [("production", "En production"), ("exploration", "En exploration"),
           ("libre", "Libre"), ("evaluation", "En évaluation")]
ZONES = [("onshore", "Onshore"), ("plateau", "Offshore peu profond"), ("plateau_profond", "Peu profond à profond"),
         ("profond", "Offshore profond"), ("profond_ultra", "Profond à ultra-profond"), ("ultra", "Offshore ultra-profond")]


class Operateur(models.Model):
    code = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=120)
    pays = models.CharField(max_length=80, blank=True)
    type = models.CharField(max_length=60, blank=True)
    couleur = models.CharField(max_length=9, default="#8a94a6")

    class Meta:
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class Bloc(models.Model):
    code = models.CharField(max_length=12, unique=True)
    zone = models.CharField(max_length=20, choices=ZONES)
    operateur = models.ForeignKey(Operateur, null=True, blank=True, on_delete=models.SET_NULL, related_name="blocs")
    operateur_2026 = models.ForeignKey(Operateur, null=True, blank=True, on_delete=models.SET_NULL,
                                       related_name="blocs_2026")
    date_cpp = models.DateField(null=True, blank=True)
    date_cpp_2026 = models.DateField(null=True, blank=True)
    superficie_km2 = models.FloatField(null=True, blank=True)
    superficie_officielle = models.BooleanField(default=False)
    superficie_source = models.CharField(max_length=40, blank=True)
    profondeur = models.CharField(max_length=40, blank=True)
    historique = models.JSONField(default=list, blank=True, help_text="CPP successifs : opérateur, partenaires, date")
    statut_2024 = models.CharField(max_length=20, choices=STATUTS)
    statut_2026 = models.CharField(max_length=20, choices=STATUTS)
    note_2026 = models.CharField(max_length=255, blank=True)
    geometrie = models.JSONField(null=True, blank=True, help_text="Anneau GeoJSON [[lon, lat], ...]")
    geometrie_officielle = models.BooleanField(default=False)
    geometrie_note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code

    @property
    def numero(self):
        return int(self.code.split("-")[1])


class Champ(models.Model):
    nom = models.CharField(max_length=120, unique=True)
    serie = models.CharField(max_length=20, blank=True, help_text="Clé des séries DGH (ex. CI-40)")
    blocs = models.ManyToManyField(Bloc, related_name="champs")
    operateur = models.ForeignKey(Operateur, null=True, on_delete=models.SET_NULL)
    statut = models.CharField(max_length=20, choices=STATUTS)
    fluide = models.CharField(max_length=80)
    annee_decouverte = models.IntegerField(null=True, blank=True)
    annee_mise_production = models.IntegerField(null=True, blank=True)
    lon = models.FloatField()
    lat = models.FloatField()
    description = models.TextField(blank=True)
    couleur = models.CharField(max_length=9, default="#3987e5")

    def __str__(self):
        return self.nom


class ProductionAnnuelle(models.Model):
    champ = models.ForeignKey(Champ, on_delete=models.CASCADE, related_name="productions")
    annee = models.IntegerField()
    petrole_bbl = models.BigIntegerField(default=0)
    gaz_mmscf = models.FloatField(default=0)
    ventes_gaz_mmbtu = models.FloatField(default=0)
    pouvoir_calorifique = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("champ", "annee")
        ordering = ["annee"]


class Forage(models.Model):
    type = models.CharField(max_length=30)
    bloc_code = models.CharField(max_length=12)
    operateur = models.CharField(max_length=80)
    annee = models.IntegerField()
    nombre = models.IntegerField()


class Puits(models.Model):
    nom = models.CharField(max_length=80)
    bloc_code = models.CharField(max_length=12)
    type = models.CharField(max_length=30)
    annee = models.IntegerField()
    resultat = models.CharField(max_length=30)
    note = models.CharField(max_length=200, blank=True)


class Exportation(models.Model):
    annee = models.IntegerField()
    champ = models.CharField(max_length=60)
    bloc_code = models.CharField(max_length=20)
    degre_api = models.FloatField()
    total_bbl = models.BigIntegerField()
    etat_bbl = models.BigIntegerField()
    petroci_bbl = models.BigIntegerField()
    prives_bbl = models.BigIntegerField()


class RecetteAnnuelle(models.Model):
    annee = models.IntegerField(unique=True)
    bic_petrole = models.FloatField()
    bic_gaz = models.FloatField()
    taxe_petrole = models.FloatField()
    taxe_gaz = models.FloatField()
    bonus = models.FloatField()
    total = models.FloatField()
    fcfa_usd = models.FloatField(null=True)

    class Meta:
        ordering = ["annee"]


class Brent(models.Model):
    annee = models.IntegerField()
    mois = models.IntegerField(null=True, blank=True, help_text="Vide = moyenne annuelle")
    prix = models.FloatField()
    marge_sir = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["annee", "mois"]


class Evenement(models.Model):
    CATS = [("contrat", "Contrat"), ("decouverte", "Découverte"), ("production", "Production"),
            ("forage", "Forage"), ("politique", "Politique publique")]
    date = models.DateField()
    titre = models.CharField(max_length=160)
    categorie = models.CharField(max_length=20, choices=CATS)
    bloc_code = models.CharField(max_length=12, blank=True)
    description = models.TextField(blank=True)
    source = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["-date"]


class Parametre(models.Model):
    """Clés/valeurs diverses (indicateurs annuaire, sismique, gaz industriel...)."""
    cle = models.CharField(max_length=60, unique=True)
    valeur = models.JSONField()
