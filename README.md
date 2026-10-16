# Projet Solaris - datamart DVF 2025

## 1. Données source

Télécharger les valeurs foncières 2025 :

https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres

Placer `ValeursFoncieres-2025.txt` à la racine du projet. C'est la **seule source
utilisée** : Power Query le lit directement (473 Mo, séparateur `|`).

## 2. Construire le datamart

Le datamart (1 table de faits détaillée + 1 table de faits agrégée + 7 dimensions)
est construit **intégralement en Power Query**, dans le projet `Projet_Solaris.pbip`.

1. Ouvrir `Projet_Solaris.pbip` dans Power BI Desktop
2. Le rapport s'affiche sur la page « Marché immobilier 2025 » (la matrice)
3. **Accueil → Actualiser** seulement si `ValeursFoncieres-2025.txt` a changé :
   les données sont déjà dans le cache du projet (`68 Mo`)

Voir `MODELE_DATAMART.md` pour le schéma en flocon, les transformations et les mesures.

## 3. Ancien brouillon Python (conservé, non utilisé)

```powershell
.venv\Scripts\python.exe convert_dvf_to_datamart.py
```