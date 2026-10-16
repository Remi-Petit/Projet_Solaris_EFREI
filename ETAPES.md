# Projet Solaris - état et étapes restantes

> Dernière vérification : **16 octobre 2026**
> Modèle : **10 tables, 11 relations, 15 mesures, 13 requêtes Power Query**.
> Volumes mesurés : **7 214 760** lignes (`fait_mutation`) + **1 614 973** lignes
> (`fait_marche_agrege`). Années couvertes : **2024 et 2025**.

---

## 1. État actuel

| Élément | État |
|---|---|
| Projet Power BI `Projet_Solaris.pbip` (modèle + rapport) | ✅ enregistré sur le disque |
| Modèle en flocon | ✅ 10 tables / 11 relations / 15 mesures |
| Requêtes Power Query (ETL) | ✅ 13 requêtes M |
| Données chargées et à jour | ✅ 7 214 760 + 1 614 973 lignes |
| Analyse par **région / département / commune** | ✅ `dim_region` → `dim_departement` → `dim_commune` |
| Page « Marché immobilier 2025 » | ✅ matrice commune × année |
| Page « Marché par région et département 2025 » | ✅ matrices région et département |
| Page « Marché immobilier 2024 » | ✅ matrice commune × année |
| Page « Marché par région et département 2024 » | ✅ matrices région et département |
| Chiffres de contrôle | ✅ vérifiés (voir §4) |
| Proposition de la source au professeur | ✅ faite (à confirmer si retour attendu) |

**Historique.** Le modèle construit le 2 octobre a été perdu (fenêtre Power BI
Desktop fermée sans enregistrer). Il a été reconstruit le 16 octobre depuis
`modele_tmdl/`, puis enregistré dans un projet `.pbip` : il ne peut plus être perdu,
puisque tout (modèle, requêtes, rapport) est en texte dans le dossier.

---

## 2. Ouvrir / reprendre le projet

1. Ouvrir `Projet_Solaris.pbip` (double-clic, ou *Fichier → Ouvrir*).
2. Le rapport s'affiche sur la page **« Marché immobilier 2024-2025 »**.
3. **Accueil → Actualiser** uniquement si les fichiers source ont changé.

Structure du dossier :

```md
Projet_Solaris/
├── Projet_Solaris.pbip               <- le fichier a ouvrir
├── Projet_Solaris.SemanticModel/     <- modele (TMDL texte) + cache des donnees
├── Projet_Solaris.Report/            <- rapport (PBIR, JSON)
├── modele_tmdl/                      <- copie miroir du modele (sauvegarde)
└── ValeursFoncieres-2021..2025.txt   <- sources, non versionnees
```

> `Projet_Solaris.SemanticModel/definition/` **est** le modèle en texte : c'est la
> sauvegarde versionnable. `modele_tmdl/` en est une copie miroir.

---

## 3. Les quatre pages du rapport

Une page par **année** et par **table de faits**. Chaque page porte un **filtre de
page** sur `dim_temps[annee]` : tout ce qui s'y trouve est déjà restreint à l'année.

| Page | Table de faits | Lignes | Colonnes | Valeurs |
|---|---|---|---|---|
| Marché immobilier 2025 | détaillée | `dim_commune[commune]` | `dim_temps[annee]` | `[Nombre de mutations]`, `[Valeur fonciere totale]`, `[Prix moyen m2]` |
| Marché par région et département 2025 | agrégée | `dim_region[nom_region]` | `dim_temps[annee]` | `[Nb mutations agrege]`, `[Valeur agregee]`, `[Prix moyen m2 agrege]` |
| Marché immobilier 2024 | détaillée | `dim_commune[commune]` | `dim_temps[annee]` | idem 2025 |
| Marché par région et département 2024 | agrégée | `dim_region[nom_region]` | `dim_temps[annee]` | idem 2025 |

Les pages « par région et département » ont un **second visuel** qui descend au
département (`dim_departement[nom_departement]`), avec les mêmes mesures.

Améliorations facultatives : segment sur `dim_type_local[type_local]` ou
`dim_nature_mutation[nature_mutation]`, tri décroissant sur les mutations,
ou remplacer la colonne `annee` par `trimestre` pour un croisé intra-annuel.

---

## 4. Chiffres de contrôle (mesurés sur le modèle)

Vue globale :

| Année | Mutations | Valeur foncière totale | Prix moyen au m² |
|---|---:|---:|---:|
| 2024 | 1 237 625 | 285 013 446 757 € | 2 156,13 € |
| 2025 | 1 320 973 | 319 901 489 835 € | 2 187,23 € |
| **Total** | **2 558 598** | **604 914 936 592 €** | **2 172,46 €** |

Les trois indicateurs de prix (le premier mélange terrains et bâtiments, les deux
autres isolent chaque marché) :

| Indicateur | 2024 | 2025 | Total |
|---|---:|---:|---:|
| `Prix moyen m2` (tout) | 2 156,13 € | 2 187,23 € | 2 172,46 € |
| `Prix moyen m2 habitation` (maisons + appartements) | 2 494,36 € | 2 540,76 € | 2 518,95 € |
| `Prix moyen m2 terrain` | 17,88 € | 18,60 € | 18,25 € |

> Une cellule vide dans `Prix moyen m2` est **normale** : la surface bâtie n'existe
> pas pour les terrains et les dépendances (67 % des lignes). Ces communes ont
> souvent un `Prix moyen m2 terrain` renseigné à la place. Détail dans
> `MODELE_DATAMART.md` §3.

Par région :

| Région | Mutations | Prix moyen au m² |
|---|---:|---:|
| Île-de-France | 341 543 | 4 641 € |
| Auvergne-Rhône-Alpes | 347 443 | 2 203 € |
| Provence-Alpes-Côte d'Azur | 235 774 | 3 365 € |
| Corse | 15 487 | 3 465 € |
| Guadeloupe | 6 747 | 4 227 € |
| Grand Est | 111 370 | 1 282 € |

Par département (extraits) :

| Département | Mutations | Prix moyen au m² |
|---|---:|---:|
| Paris (75) | 76 180 | 10 253 € |
| Hauts-de-Seine (92) | 48 202 | 6 364 € |
| Alpes-Maritimes (06) | 64 628 | 4 528 € |
| Bouches-du-Rhône (13) | 70 429 | 3 321 € |
| Var (83) | 58 126 | 3 312 € |

Cohérence des deux tables de faits : `[Nombre de mutations]` et
`[Nb mutations agrege]` valent tous deux 2 558 598, et `[Valeur fonciere totale]`
= `[Valeur agregee]` = 604 914 936 592 €.

---

## 5. Pourquoi seulement 2024-2025 (et comment revenir à 5 ans)

Les 5 fichiers (2021 à 2025) sont présents sur le disque, mais **5 années
représentent ≈ 20 M de lignes** : sur ce poste (13,9 Go de RAM, ≈ 2 Go libres en
cours de travail) l'actualisation part en saturation mémoire — c'est arrivé lors
d'un essai, la RAM libre est descendue à 0,9 Go et le moteur a calé.

Avec **2024 + 2025** (7,2 M de lignes), l'actualisation complète passe sans
difficulté. Pour couvrir davantage d'années :

1. ouvrir `DVF_Brut` dans Power Query ;
2. ajouter les années à la liste `Annees = {"2024", "2025"}` ;
3. *Accueil → Actualiser* — et fermer les applications gourmandes en mémoire avant.

---

## 6. MCP Power BI (`powerbi-authoring-local`)

Le serveur MCP **ne fait rien tant qu'aucune connexion n'est établie** : chaque appel
répond `No connectionName provided and no last used connection available`.
Il faut donc commencer par demander :

> « Connecte-toi à `Projet_Solaris` dans Power BI Desktop »

À retenir :

- la connexion ne vit que dans le processus du serveur MCP : elle est perdue à
  chaque redémarrage de VS Code ou du serveur ;
- si Power BI Desktop est fermé, il n'y a aucun serveur local à joindre ;
- le MCP ne modélise que le **modèle sémantique**, pas les pages de rapport
  (d'où la page créée en PBIR/JSON pour ce projet).

---

## 7. Reste à faire avant la remise

- [ ] **Descriptif du cas métier** → déjà rédigé, `MODELE_DATAMART.md` §6
- [ ] **Justification des transformations** → déjà rédigé, `MODELE_DATAMART.md` §4
- [ ] **Données source** → les `.txt` à la racine (non versionnés, trop volumineux)
- [ ] **Fichier du projet** → `Projet_Solaris.pbip` ✅
- [ ] (facultatif) Ajouter un segment à la page 1

---

## 8. Nettoyage possible (facultatif)

- [ ] Brouillon Python (`datamart/`, `convert_dvf_to_datamart.py`) : conservé comme
      trace, plus utilisé depuis que l'ETL est dans Power Query
- [ ] `consignes.txt` : extrait texte du PDF, généré pour lecture
- [ ] `modele_tmdl/` : copie miroir du modèle, redondante avec
      `Projet_Solaris.SemanticModel/definition/` — à supprimer si tu préfères
      une seule source de vérité
- [ ] Désactiver *Date/heure automatique* (`Fichier → Options → Chargement des
      données`) : `dim_temps` est déjà une table de dates