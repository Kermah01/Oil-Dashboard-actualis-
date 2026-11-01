import json
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from amont import geo, seed_data as S
from amont.models import (Bloc, Brent, Champ, Evenement, Exportation, Forage, Operateur, Parametre,
                          ProductionAnnuelle, Puits, RecetteAnnuelle)


def d(s):
    return date.fromisoformat(s) if s else None


class Command(BaseCommand):
    help = "Charge (ou recharge) la base AMONT·CI depuis l'annuaire DGH 2025 et les faits 2025-2026."

    def add_arguments(self, parser):
        parser.add_argument("--geojson", help="GeoJSON officiel des blocs (propriété 'code') pour remplacer la géométrie indicative")

    @transaction.atomic
    def handle(self, *args, **opts):
        for M in (Puits, Forage, Exportation, RecetteAnnuelle, Brent, Evenement, Parametre, ProductionAnnuelle,
                  Champ, Bloc, Operateur):
            M.objects.all().delete()

        ops = {c: Operateur.objects.create(code=c, nom=n, pays=p, type=t, couleur=col)
               for c, n, p, t, col in S.OPERATEURS}

        DATA = Path(__file__).resolve().parents[3] / "data"
        cad = {f["properties"]["code"]: f for f in json.load(open(DATA / "cadastre.geojson", encoding="utf-8"))["features"]}
        base = json.load(open(DATA / "base_blocs.json", encoding="utf-8"))
        ZMAP = {"onshore": "onshore", "shallow water": "plateau", "shallow à deep water": "plateau_profond",
                "deep water": "profond", "deep à ultra deep water": "profond_ultra", "ultra deep water": "ultra"}
        for code in sorted(set(S.BLOCS_ACTIFS) | set(S.BLOCS_LIBRES_2024), key=lambda c: int(c.split("-")[1])):
            actif = S.BLOCS_ACTIFS.get(code)
            att = S.ATTRIBUTIONS_2026.get(code)
            st24 = actif[3] if actif else "libre"
            bb = base.get(code, {})
            ft = cad.get(code)
            ring = ft["geometry"]["coordinates"][0] if ft else None
            if actif:
                surf, src = actif[2], "DGH 2025"
            elif bb.get("superficie"):
                surf, src = bb["superficie"], "Base AMONT·CI"
            else:
                surf, src = None, ""
            Bloc.objects.create(
                code=code, zone=ZMAP.get(bb.get("profondeur", "").lower(), "plateau"),
                profondeur=bb.get("profondeur", ""), historique=self._historique(bb.get("historique", []), actif, att, ops),
                geometrie_officielle=bool(ft),
                operateur=ops[actif[0]] if actif else None,
                operateur_2026=ops[att[0]] if att else (ops[actif[0]] if actif else None),
                date_cpp=d(actif[1]) if actif else None,
                date_cpp_2026=d(att[1]) if att else (d(actif[1]) if actif else None),
                superficie_km2=surf, superficie_officielle=bool(surf), superficie_source=src,
                **self._controle(ring, surf, (ft or {}).get("properties", {}).get("note", "")),
                statut_2024=st24, statut_2026="exploration" if att else st24,
                note_2026=att[2] if att else "", geometrie=ring)

        if opts.get("geojson"):
            self._geojson(opts["geojson"])

        for (nom, blocs, op, statut, fluide, dec, mep, lon, lat, desc, col) in S.CHAMPS:
            cents = [self._centre(b.geometrie) for b in Bloc.objects.filter(code__in=blocs) if b.geometrie]
            if cents and nom != "Baleine":
                lon, lat = sum(c[0] for c in cents) / len(cents), sum(c[1] for c in cents) / len(cents)
            elif cents:  # Baleine : à cheval sur CI-101 et CI-802
                lon, lat = self._frontiere(blocs)
            ch = Champ.objects.create(nom=nom, serie=S.CHAMP_BLOC_PROD.get(nom, ""), operateur=ops[op],
                                      statut=statut, fluide=fluide, annee_decouverte=dec,
                                      annee_mise_production=mep, lon=lon, lat=lat, description=desc, couleur=col)
            ch.blocs.set(Bloc.objects.filter(code__in=blocs))
            if ch.serie:
                for i, an in enumerate(S.ANNEES):
                    ProductionAnnuelle.objects.create(
                        champ=ch, annee=an, petrole_bbl=S.PROD_PETROLE[ch.serie][i],
                        gaz_mmscf=S.PROD_GAZ[ch.serie][i], ventes_gaz_mmbtu=S.VENTES_GAZ[ch.serie][i],
                        pouvoir_calorifique=S.PCS[ch.serie][i])

        for typ, bloc, op, par_an in S.FORAGES:
            for an, nb in par_an.items():
                Forage.objects.create(type=typ, bloc_code=bloc, operateur=op, annee=an, nombre=nb)
        for p in S.PUITS:
            Puits.objects.create(nom=p[0], bloc_code=p[1], type=p[2], annee=p[3], resultat=p[4], note=p[5])
        for e in S.EXPORTS_2024:
            Exportation.objects.create(annee=2024, champ=e[0], bloc_code=e[1], degre_api=e[2], total_bbl=e[3],
                                       etat_bbl=e[4], petroci_bbl=e[5], prives_bbl=e[6])
        for i, an in enumerate(S.ANNEES):
            RecetteAnnuelle.objects.create(annee=an, fcfa_usd=S.FCFA_USD[an],
                                           **{k: v[i] for k, v in S.RECETTES.items()})
        for an, px in S.BRENT_ANNUEL.items():
            Brent.objects.create(annee=an, prix=px, marge_sir=S.MARGE_SIR.get(an))
        for m, px in enumerate(S.BRENT_2024_MENSUEL, 1):
            Brent.objects.create(annee=2024, mois=m, prix=px)
        for dt, titre, cat, bloc, desc, src in S.EVENEMENTS:
            Evenement.objects.create(date=d(dt), titre=titre, categorie=cat, bloc_code=bloc or "",
                                     description=desc, source=src)
        for cle, val in {"indicateurs_2024": S.INDICATEURS_2024, "sismique": S.SISMIQUE,
                         "gaz_industrie": {str(k): v for k, v in S.GAZ_INDUSTRIE.items()},
                         "forages_total_dgh": {str(k): v for k, v in S.FORAGES_TOTAL_DGH.items()},
                         "imports_brut_2024": S.IMPORTS_BRUT_2024, "brut_local_raffine_2024_tm": S.BRUT_LOCAL_RAFFINE_2024_TM,
                         "objectifs": S.OBJECTIFS, "territoire": geo.TERRITOIRE,
                         "cadastre_ancien": json.load(open(DATA / "cadastre_ancien.geojson", encoding="utf-8"))}.items():
            Parametre.objects.create(cle=cle, valeur=val)

        self.stdout.write(self.style.SUCCESS(
            f"OK : {Bloc.objects.count()} blocs, {Champ.objects.count()} champs, "
            f"{ProductionAnnuelle.objects.count()} lignes de production, {Evenement.objects.count()} événements."))

    @staticmethod
    def _historique(hist, actif, att, ops):
        """Historique de la base AMONT·CI trié par date ; le CPP en cours prend la date et l'opérateur de la DGH."""
        h = sorted([dict(x, source="Base AMONT·CI") for x in hist], key=lambda x: x["date"] or "0")
        for cur, dt, src in ([(actif[0], actif[1], "DGH 2025")] if actif else []) + ([(att[0], att[1], "Conseil des ministres")] if att else []):
            nom = ops[cur].nom
            cle = cur.split()[0][:5].upper()
            if h and cle in h[-1]["operateur"].upper().replace(" ", ""):
                h[-1].update(operateur=nom, date=dt, source=src)
            else:
                h.append({"operateur": nom, "partenaires": "", "date": dt, "source": src})
        return h

    @staticmethod
    def _controle(ring, surf, note):
        """Compare l'aire du contour à la superficie officielle."""
        if ring and surf:
            a = geo.superficie_km2(ring)
            if a / surf > 1.5:
                note = (f"Contour source ≈ {a:,.0f} km² pour {surf:,.0f} km² officiels : périmètre historique probable, "
                        "à vérifier avec la DGH").replace(",", " ")
        return {"geometrie_note": note}

    @staticmethod
    def _centre(ring):
        pts = ring[:-1] if ring[0] == ring[-1] else ring
        return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)

    def _frontiere(self, codes):
        """Point moyen des sommets partagés par deux blocs (sinon milieu des centres)."""
        rings = [Bloc.objects.get(code=c).geometrie for c in codes]
        if len(rings) == 2 and all(rings):
            a = {(round(x, 4), round(y, 4)) for x, y in rings[0]}
            commun = [p for p in {(round(x, 4), round(y, 4)) for x, y in rings[1]} if p in a]
            if len(commun) >= 2:
                return sum(p[0] for p in commun) / len(commun), sum(p[1] for p in commun) / len(commun)
        cs = [self._centre(r) for r in rings if r]
        return sum(c[0] for c in cs) / len(cs), sum(c[1] for c in cs) / len(cs)

    def _geojson(self, path):
        with open(path, encoding="utf-8") as f:
            fc = json.load(f)
        n = 0
        for ft in fc["features"]:
            code = str(ft["properties"].get("code", "")).upper().replace(" ", "")
            g = ft["geometry"]
            ring = g["coordinates"][0] if g["type"] == "Polygon" else g["coordinates"][0][0]
            n += Bloc.objects.filter(code=code).update(geometrie=ring, geometrie_officielle=True)
        self.stdout.write(f"Géométrie officielle appliquée à {n} blocs.")
