# Projet Solaris - datamart DVF

## 1. Données source

Télécharger les valeurs foncières (DVF) :

https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres

Placer les fichiers à la racine du projet, nommés `ValeursFoncieres-AAAA.txt`.
Le modèle utilise actuellement **2024 et 2025** (≈ 920 Mo, séparateur `|`) ;
`DVF_Brut` liste les années retenues dans la variable `Annees`.

## 2. Construire le datamart

Le datamart (1 table de faits détaillée + 1 table de faits agrégée + 8 dimensions)
est construit **intégralement en Power Query**, dans le projet `Projet_Solaris.pbip`.

1. Ouvrir `Projet_Solaris.pbip` dans Power BI Desktop
2. Le rapport s'ouvre sur la page « Marché immobilier 2025 » (la matrice) ; les
   trois autres pages sont accessibles par les onglets du bas
3. **Accueil → Actualiser** seulement si les fichiers source ont changé :
   les données sont déjà dans le cache du projet (`124 Mo`)

Voir `MODELE_DATAMART.md` pour le schéma en flocon, les transformations et les mesures.

## 3. Ancien brouillon Python (conservé, non utilisé)

```powershell
.venv\Scripts\python.exe convert_dvf_to_datamart.py
```