# Projet Solaris - état et étapes restantes

> Dernière vérification : **16 octobre 2026**
> Modèle : 9 tables, 10 relations, 13 mesures, 10 requêtes Power Query.
> Volumes mesurés : 3 714 829 lignes (`fait_mutation`) + 820 774 lignes (`fait_marche_agrege`).

---

## 1. État actuel

| Élément | État |
|---|---|
| Projet Power BI `Projet_Solaris.pbip` (modèle + rapport) | ✅ **enregistré sur le disque** |
| Modèle en flocon (tables, relations, mesures) | ✅ 9 tables / 10 relations / 13 mesures |
| Requêtes Power Query (ETL) | ✅ 10 requêtes M |
| Données chargées | ✅ 3 714 829 + 820 774 lignes |
| Matrice (tableau croisé) | ✅ page « Marché immobilier 2025 » |
| Chiffres de contrôle | ✅ conformes (voir §4) |
| Proposition de la source au professeur | ❓ action humaine (échéance 7/10 dépassée : à confirmer) |

**Historique.** Le modèle construit le 2 octobre a été **perdu** : la fenêtre
Power BI Desktop a été fermée sans enregistrer et aucun fichier n'existait sur le
disque. Il a été **reconstruit le 16 octobre depuis `modele_tmdl/`** (la copie
texte du modèle, versionnée dans git), puis **enregistré** dans un projet `.pbip` :
il ne peut plus être perdu.

---

## 2. Ouvrir / reprendre le projet

1. Ouvrir `Projet_Solaris.pbip` (double-clic, ou *Fichier → Ouvrir*).
2. Le rapport s'ouvre sur la page **« Marché immobilier 2025 »**.
3. **Accueil → Actualiser** uniquement si `ValeursFoncieres-2025.txt` a changé
   (relecture de 473 Mo, plusieurs minutes).

Structure du dossier :

```md
Projet_Solaris/
├── Projet_Solaris.pbip               <- le fichier a ouvrir
├── Projet_Solaris.SemanticModel/     <- modele (TMDL texte) + cache des donnees
├── Projet_Solaris.Report/            <- rapport (PBIR, JSON)
├── modele_tmdl/                      <- copie de secours du modele
└── ValeursFoncieres-2025.txt         <- source 473 Mo, non versionnee
```

> `Projet_Solaris.SemanticModel/definition/` **est** le modèle en texte : c'est la
> sauvegarde versionnable, `modele_tmdl/` en est la copie de secours.

---

## 3. La matrice

Page **« Marché immobilier 2025 »** :

| Zone | Champ |
|---|---|
| Lignes | `dim_commune[commune]` |
| Colonnes | `dim_temps[annee]` (2025) |
| Valeurs | `[Nombre de mutations]`, `[Valeur fonciere totale]`, `[Prix moyen m2]` |

Améliorations facultatives : segment sur `dim_type_local[type_local]` et
`dim_nature_mutation[nature_mutation]`, tri décroissant sur les mutations.

---

## 4. Chiffres de contrôle (revérifiés le 16/10 sur le modèle restauré)

| Indicateur | Valeur |
|---|---:|
| Nombre de mutations | 1 320 973 |
| Valeur foncière totale | 319 901 489 835 € |
| Prix moyen au m² | 2 187,23 € |
| Paris (département 75) | 10 713 €/m² (40 362 mutations) |
| Hauts-de-Seine (92) | 6 924 €/m² |
| Alpes-Maritimes (06) | 4 630 €/m² |
| Var (83) | 3 473 €/m² |
| Appartements (France) | 3 597 €/m² |
| Maisons (France) | 2 124 €/m² |

Cohérence des deux tables de faits : `[Nombre de mutations]` et
`[Nb mutations agrege]` valent tous deux 1 320 973, et `[Valeur fonciere totale]`
= `[Valeur agregee]` = 319 901 489 835 €.

---

## 5. Reste à faire avant le samedi 17 octobre

- [ ] **Proposer la source au professeur** (action humaine, e-mail / Teams) —
      si ce n'est pas déjà fait
      - DVF 2025, `data.gouv.fr` (DGFiP / Etalab), 473 Mo, 3,7 M lignes
- [ ] **Descriptif du cas métier** → déjà rédigé, `MODELE_DATAMART.md` §6
- [ ] **Justification des transformations** → déjà rédigé, `MODELE_DATAMART.md` §4
- [ ] **Données source** → `ValeursFoncieres-2025.txt` (473 Mo, à la racine)
- [ ] **Fichier du projet** → `Projet_Solaris.pbip` ✅
- [ ] (facultatif) Ajouter un segment à la matrice

---

## 6. MCP Power BI (`powerbi-authoring-local`)

Le serveur MCP **ne fait rien tant qu'aucune connexion n'est établie** : chaque
appel répond `No connectionName provided and no last used connection available`.
Il faut donc commencer par demander :

> « Connecte-toi à `Projet_Solaris` dans Power BI Desktop »

À retenir :

- la connexion ne vit que dans le processus du serveur MCP : elle est perdue à
  chaque redémarrage de VS Code ou du serveur ;
- si Power BI Desktop est fermé, il n'y a aucun serveur local à joindre ;
- le MCP ne modélise que le **modèle sémantique**, pas les pages de rapport
  (d'où la page créée en PBIR/JSON pour ce projet).

---

## 7. Nettoyage possible (facultatif)

- [ ] Brouillon Python (`datamart/`, `convert_dvf_to_datamart.py`) : conservé
      comme trace, plus utilisé depuis que l'ETL est dans Power Query
- [ ] `consignes.txt` : extrait texte du PDF, généré pour lecture
- [ ] Désactiver *Date/heure automatique* (`Fichier → Options → Chargement des
      données`) : `dim_temps` est déjà une table de dates