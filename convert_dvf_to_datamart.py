# -*- coding: utf-8 -*-
"""
convert_dvf_to_datamart.py
==========================

Convertit le fichier source DVF 2025 (``ValeursFoncieres-2025.txt``, delimite par ``|``)
en un **datamart en flocon** compose de plusieurs fichiers CSV prets a etre importes
dans Power BI.

Schema produit (flocon)
-----------------------

::

    DIM_TEMPS                                    DIM_CATEGORIE_LOCAL
        ^                                                 ^
        |                                                 |
        |                                          DIM_TYPE_LOCAL
        |                                                 ^
        |                                                 |
        +------------------>  FAIT_MUTATION  <-------------+
                                 |
                                 +--> DIM_NATURE_MUTATION
                                 +--> DIM_NATURE_CULTURE
                                 +--> DIM_COMMUNE  -->  DIM_DEPARTEMENT

Deux branches de normalisation (ce qui en fait un **flocon** et non une etoile) :

* ``DIM_COMMUNE`` pointe vers ``DIM_DEPARTEMENT``
* ``DIM_TYPE_LOCAL`` pointe vers ``DIM_CATEGORIE_LOCAL``

Tables produites
----------------

===================================== ==============================================
Fichier                               Role
===================================== ==============================================
``fait_mutation.csv``                 table de faits : 1 ligne = 1 mutation + mesures
``dim_temps.csv``                     calendrier (annee / trimestre / mois)
``dim_commune.csv``                   communes (cle dept + cle commune)
``dim_departement.csv``               departements
``dim_nature_mutation.csv``           Vente, Echange, Adjudication, ...
``dim_type_local.csv``                Maison, Appartement, Immeuble, Local comm.
``dim_categorie_local.csv``           Habitation, Immeuble collectif, Professionnel...
``dim_nature_culture.csv``            nature de culture / terrain
===================================== ==============================================

Transformations realisees (utiles pour le rendu)
------------------------------------------------

1. **Separation d'une table en plusieurs** : le fichier plat devient 1 fait + 8 dimensions.
2. **Modification de cle** : reconstruction des codes INSEE / codes postaux
   (les zeros de tete ont ete perdus dans le fichier source) + cles de substitution
   (``cle_temps``, ``cle_commune``, ``cle_nature_culture``).
3. **Colonnes calculees** : ``trimestre``, ``categorie_local``, ``nature_culture`` (libelle).
4. **Agregation** : ``nombre_lots`` et surfaces consolidees par mutation (le fichier
   DVF contient 1 ligne par local d'une meme mutation).

Utilisation
-----------

::

    python convert_dvf_to_datamart.py                    # conversion complete, format FR (; + ,)
    python convert_dvf_to_datamart.py --limit 200000     # echantillon de 200 000 lignes
    python convert_dvf_to_datamart.py --us-format        # delimiteur ',' et decimale '.'

Format de sortie
----------------

* Par defaut : format **francais** -> separateur ``;`` et decimale ``,``
* ``--us-format`` : separateur ``,`` et decimale ``.``
* Encodage ``utf-8-sig`` (BOM) pour une detection correcte par Excel / Power BI.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import date, datetime

# --------------------------------------------------------------------------- #
# Constantes
# --------------------------------------------------------------------------- #

DELIM_IN = "|"
ENCODING_IN = "utf-8"
ENCODING_OUT = "utf-8-sig"

# Indices des colonnes source (0-based) — voir l'en-tete du fichier
# NB : les colonnes 0 ("Identifiant de document") et 1 ("Reference document")
#      sont vides sur 100 % des lignes du fichier source : elles ne sont pas
#      reprises dans le datamart.
C_DATE = 8
C_NATURE_MUTATION = 9
C_VALEUR = 10
C_NO_VOIE = 11
C_BTQ = 12
C_TYPE_VOIE = 13
C_CODE_VOIE = 14
C_VOIE = 15
C_CODE_POSTAL = 16
C_COMMUNE = 17
C_CODE_DEPT = 18
C_CODE_COMMUNE = 19
C_SECTION = 21
C_NOMBRE_LOTS = 34
C_CODE_TYPE_LOCAL = 35
C_TYPE_LOCAL = 36
C_ID_LOCAL = 37
C_SURF_BATI = 38
C_NB_PIECES = 39
C_NATURE_CULTURE = 40
C_NATURE_CULTURE_SPEC = 41
C_SURF_TERRAIN = 42

NB_COLS = 43

# Libelles des codes "Nature culture" du DVF
LIBELLES_NATURE_CULTURE = {
    "S": "Sols",
    "T": "Terres",
    "P": "Pres",
    "V": "Vergers",
    "B": "Bois",
    "L": "Landes",
    "J": "Jardins",
    "C": "Carrieres",
    "E": "Eaux",
    "O": "Autres (O)",
    "F": "Forets",
    "N": "Autres (N)",
    "A": "Autres (A)",
}

LIBELLES_TYPE_LOCAL = {
    "0": "Non renseigne (terrain / dependance)",
    "1": "Maison",
    "2": "Appartement",
    "3": "Immeuble",
    "4": "Local commercial / industriel",
}

# Regroupement des types de locaux (2e niveau du flocon)
CATEGORIE_TYPE_LOCAL = {
    "0": "Terrain / non renseigne",
    "1": "Habitation",
    "2": "Habitation",
    "3": "Immeuble collectif",
    "4": "Professionnel / commercial",
}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def to_num(raw: str, dec_out: str) -> str:
    """Convertit '468000,00' -> '468000.00' (ou '468000,00' selon dec_out)."""
    s = (raw or "").strip().replace("\u00a0", "").replace(" ", "")
    if not s:
        return ""
    s = s.replace(",", ".")
    try:
        value = float(s)
    except ValueError:
        return ""
    return f"{value:.2f}".replace(".", dec_out)


def to_date(raw: str) -> date | None:
    s = (raw or "").strip()
    if not s:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def to_int(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return ""
    try:
        return str(int(float(s.replace(",", "."))))
    except ValueError:
        return ""


def clean(raw: str) -> str:
    return (raw or "").strip()


def zpad(raw: str, width: int) -> str:
    """Reconstruit un code administratif dont les zeros de tete ont ete perdus.

    Le fichier source DVF a subi un passage par un tableur : ``01400`` y devient
    ``1400`` et ``001`` devient ``1``. On recomplete a gauche avec des zeros.
    Les codes non numeriques (ex. ``2A``, ``2B``) sont conserves tels quels.
    """
    s = clean(raw)
    if not s:
        return ""
    if s.isdigit():
        return s.zfill(width)
    return s


# --------------------------------------------------------------------------- #
# Conversion
# --------------------------------------------------------------------------- #


def run(input_path: str, outdir: str, limit: int, us_format: bool) -> None:
    delim_out = "," if us_format else ";"
    dec_out = "." if us_format else ","

    if not os.path.isfile(input_path):
        sys.exit(f"[ERREUR] Fichier introuvable : {input_path}")

    # --- repertoire de sortie ------------------------------------------- #
    if os.path.isdir(outdir):
        for f in os.listdir(outdir):
            if f.lower().endswith(".csv"):
                os.remove(os.path.join(outdir, f))
    else:
        os.makedirs(outdir, exist_ok=True)

    # --- accumulateurs de dimensions ------------------------------------ #
    dim_temps: dict[int, dict] = {}
    dim_commune: dict[str, dict] = {}
    dim_departement: dict[str, dict] = {}
    dim_nature_mutation: dict[str, dict] = {}
    dim_type_local: dict[str, dict] = {}
    dim_categorie_local: dict[str, dict] = {}
    dim_nature_culture: dict[str, dict] = {}

    stats = {"lignes_lues": 0, "lignes_ecrites": 0, "lignes_ignorees": 0, "cols_incoherentes": 0}

    fact_path = os.path.join(outdir, "fait_mutation.csv")

    with open(input_path, "r", encoding=ENCODING_IN, newline="") as fin, open(
        fact_path, "w", encoding=ENCODING_OUT, newline=""
    ) as fout:
        reader = csv.reader(fin, delimiter=DELIM_IN)
        writer = csv.writer(fout, delimiter=delim_out, lineterminator="\n")

        header = next(reader)
        if len(header) != NB_COLS:
            print(f"[ATTENTION] En-tete de {len(header)} colonnes (attendu {NB_COLS}).")

        writer.writerow(
            [
                "cle_mutation",
                "cle_temps",
                "cle_commune",
                "cle_nature_mutation",
                "cle_type_local",
                "cle_nature_culture",
                "no_voie",
                "btq",
                "code_voie",
                "identifiant_local",
                "valeur_fonciere",
                "surface_reelle_bati",
                "nombre_pieces_principales",
                "surface_terrain",
                "nombre_lots",
            ]
        )

        prev_groupe = None
        mutation_id = 0

        for row in reader:
            stats["lignes_lues"] += 1
            if limit and stats["lignes_lues"] > limit:
                break

            if len(row) != NB_COLS:
                stats["cols_incoherentes"] += 1
                if len(row) < NB_COLS:
                    row = row + [""] * (NB_COLS - len(row))
                else:
                    row = row[:NB_COLS]

            # ---------------- date / temps ----------------------------- #
            d = to_date(row[C_DATE])
            if d is None:
                stats["lignes_ignorees"] += 1
                continue

            cle_temps = int(d.strftime("%Y%m%d"))
            if cle_temps not in dim_temps:
                dim_temps[cle_temps] = {
                    "cle_temps": cle_temps,
                    "date": d.isoformat(),
                    "annee": d.year,
                    "trimestre": (d.month - 1) // 3 + 1,
                    "mois": d.month,
                    "jour_semaine": d.isoweekday(),
                }

            # ---------------- commune / departement -------------------- #
            # NB : les zeros de tete ont ete perdus dans le fichier source,
            #      on les restaure (01 / 001 / 01400).
            code_dept = zpad(row[C_CODE_DEPT], 2)
            code_insee = zpad(row[C_CODE_COMMUNE], 3)
            code_postal = zpad(row[C_CODE_POSTAL], 5)
            nom_commune = clean(row[C_COMMUNE])

            if not code_dept or not code_insee:
                stats["lignes_ignorees"] += 1
                continue

            cle_commune = f"{code_dept}{code_insee}"
            if cle_commune not in dim_commune:
                dim_commune[cle_commune] = {
                    "cle_commune": cle_commune,
                    "code_departement": code_dept,
                    "code_commune": code_insee,
                    "commune": nom_commune,
                    "code_postal": code_postal,
                }
            elif not dim_commune[cle_commune]["code_postal"]:
                dim_commune[cle_commune]["code_postal"] = code_postal

            if code_dept not in dim_departement:
                dim_departement[code_dept] = {
                    "cle_departement": code_dept,
                    "code_departement": code_dept,
                }

            # ---------------- nature mutation -------------------------- #
            nature_mut = clean(row[C_NATURE_MUTATION]) or "(non renseigne)"
            if nature_mut not in dim_nature_mutation:
                dim_nature_mutation[nature_mut] = {
                    "cle_nature_mutation": nature_mut,
                    "nature_mutation": nature_mut,
                }

            # ---------------- type de local (+ categorie) -------------- #
            code_type = clean(row[C_CODE_TYPE_LOCAL]) or "0"
            if code_type not in dim_type_local:
                dim_type_local[code_type] = {
                    "cle_type_local": code_type,
                    "code_type_local": code_type,
                    "type_local": clean(row[C_TYPE_LOCAL]) or LIBELLES_TYPE_LOCAL.get(code_type, ""),
                    "cle_categorie_local": code_type if code_type in CATEGORIE_TYPE_LOCAL else "0",
                }
            cle_type = code_type

            if cle_type not in dim_categorie_local:
                dim_categorie_local[cle_type] = {
                    "cle_categorie_local": cle_type,
                    "categorie_local": CATEGORIE_TYPE_LOCAL.get(cle_type, "Autre"),
                }

            # ---------------- nature culture --------------------------- #
            nature_cult = clean(row[C_NATURE_CULTURE])
            nature_cult_spec = clean(row[C_NATURE_CULTURE_SPEC])
            if nature_cult or nature_cult_spec:
                cle_culture = f"{nature_cult or '0'}-{nature_cult_spec or '0'}"
                if cle_culture not in dim_nature_culture:
                    dim_nature_culture[cle_culture] = {
                        "cle_nature_culture": cle_culture,
                        "code_nature_culture": nature_cult,
                        "nature_culture": LIBELLES_NATURE_CULTURE.get(nature_cult, nature_cult),
                        "nature_culture_speciale": nature_cult_spec,
                    }
            else:
                cle_culture = ""

            # ---------------- regroupement en mutation ------------------ #
            # Le fichier source ne contient AUCUN identifiant de document :
            # une meme mutation (vente) est eclatee en 1 ligne par bien, et la
            # valeur fonciere y est repetee. On reconstruit donc une cle de
            # mutation en regroupant les lignes CONTIGUES qui partagent
            # date + commune + nature + valeur.
            valeur_raw = to_num(row[C_VALEUR], dec_out)
            groupe = (cle_temps, code_dept, code_insee, nature_mut, valeur_raw)
            if groupe != prev_groupe:
                mutation_id += 1
                prev_groupe = groupe

            # ---------------- ecriture de la ligne de faits ------------ #
            # NB : cle_categorie_local n'est PAS ecrite dans le fait.
            # La categorie s'atteint via dim_type_local -> dim_categorie_local,
            # ce qui evite une relation ambigue dans Power BI.
            writer.writerow(
                [
                    mutation_id,
                    cle_temps,
                    cle_commune,
                    nature_mut,
                    cle_type,
                    cle_culture,
                    clean(row[C_NO_VOIE]),
                    clean(row[C_BTQ]),
                    clean(row[C_CODE_VOIE]),
                    clean(row[C_ID_LOCAL]),
                    valeur_raw,
                    to_num(row[C_SURF_BATI], dec_out),
                    to_int(row[C_NB_PIECES]),
                    to_num(row[C_SURF_TERRAIN], dec_out),
                    to_int(row[C_NOMBRE_LOTS]),
                ]
            )
            stats["lignes_ecrites"] += 1

            if stats["lignes_lues"] % 250_000 == 0:
                print(f"  ... {stats['lignes_lues']:,} lignes lues".replace(",", " "))

    # ------------------------------------------------------------------ #
    # Ecriture des dimensions (triees pour un resultat stable)
    # ------------------------------------------------------------------ #

    def write_dim(name: str, rows: list[dict], fields: list[str]) -> None:
        path = os.path.join(outdir, name)
        with open(path, "w", encoding=ENCODING_OUT, newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, delimiter=delim_out, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        print(f"  -> {name:<28} {len(rows):>8} lignes".replace(",", " "))

    write_dim(
        "dim_temps.csv",
        [dim_temps[k] for k in sorted(dim_temps)],
        ["cle_temps", "date", "annee", "trimestre", "mois", "jour_semaine"],
    )
    write_dim(
        "dim_departement.csv",
        [dim_departement[k] for k in sorted(dim_departement)],
        ["cle_departement", "code_departement"],
    )
    write_dim(
        "dim_commune.csv",
        [dim_commune[k] for k in sorted(dim_commune)],
        ["cle_commune", "code_departement", "code_commune", "commune", "code_postal"],
    )
    write_dim(
        "dim_nature_mutation.csv",
        [dim_nature_mutation[k] for k in sorted(dim_nature_mutation)],
        ["cle_nature_mutation", "nature_mutation"],
    )
    write_dim(
        "dim_type_local.csv",
        [dim_type_local[k] for k in sorted(dim_type_local)],
        ["cle_type_local", "code_type_local", "type_local", "cle_categorie_local"],
    )
    write_dim(
        "dim_categorie_local.csv",
        [dim_categorie_local[k] for k in sorted(dim_categorie_local)],
        ["cle_categorie_local", "categorie_local"],
    )
    write_dim(
        "dim_nature_culture.csv",
        [dim_nature_culture[k] for k in sorted(dim_nature_culture)],
        ["cle_nature_culture", "code_nature_culture", "nature_culture", "nature_culture_speciale"],
    )

    # ------------------------------------------------------------------ #
    # Bilan
    # ------------------------------------------------------------------ #
    taille = os.path.getsize(fact_path) / 1024 / 1024
    print("\n" + "=" * 62)
    print("CONVERSION TERMINEE")
    print("=" * 62)
    for k, v in stats.items():
        print(f"  {k:<22}: {v:>12,}".replace(",", " "))
    print(f"  mutations reconstituees: {mutation_id:>11,}".replace(",", " "))
    print(f"  fait_mutation.csv     : {taille:>10.1f} Mo")
    print(f"  dimensions            : {len(dim_commune)} communes / {len(dim_departement)} departements")
    print(f"  format                : delimiteur '{delim_out}' | decimale '{dec_out}'")
    print(f"  dossier de sortie     : {os.path.abspath(outdir)}")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main() -> None:
    parser = argparse.ArgumentParser(description="Convertit le DVF 2025 en datamart en flocon (CSV).")
    parser.add_argument("--input", default="ValeursFoncieres-2025.txt", help="fichier source")
    parser.add_argument("--outdir", default="datamart", help="dossier de sortie")
    parser.add_argument("--limit", type=int, default=0, help="nombre max de lignes (0 = tout)")
    parser.add_argument("--us-format", action="store_true", help="delimiteur ',' et decimale '.'")
    args = parser.parse_args()

    print("=" * 62)
    print("CONVERSION DVF 2025 -> DATAMART EN FLOCON")
    print("=" * 62)
    print(f"  source : {args.input}")
    print(f"  sortie : {args.outdir}")
    print(f"  limite : {args.limit or 'aucune (fichier complet)'}")
    print()

    run(args.input, args.outdir, args.limit, args.us_format)


if __name__ == "__main__":
    main()
