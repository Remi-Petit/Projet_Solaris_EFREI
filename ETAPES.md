# Étapes restantes - Projet Solaris

> Dernière vérification : **2 octobre 2026**
> Modèle : 9 tables, 10 relations, 13 mesures, 3 714 829 lignes (faits détaillés) + 820 774 lignes (faits agrégés).

---

## ⚠️ État actuel : le modèle existe, mais rien n'est enregistré

| Élément | État |
|---|---|
| Modèle en flocon (tables, relations, mesures) | ✅ **terminé, en mémoire de Power BI Desktop** |
| Requêtes Power Query (ETL) | ✅ terminées |
| Documentation (`MODELE_DATAMART.md`) | ✅ terminée |
| **Fichier `.pbix` sur le disque** | ❌ **n'existe pas** |
| **Matrice (tableau croisé)** | ❌ **pas encore créée** |

**Tant que le point 1 n'est pas fait, tout peut disparaître** : si la fenêtre
Power BI Desktop se ferme sans enregistrer, les 3,7 M de lignes transformées et
les 13 mesures sont perdus.

> Filet de sécurité si cela arrive : `modele_tmdl/` contient la définition complète
> du modèle (14 fichiers texte, dont `expressions.tmdl` avec les requêtes M).
> Je peux tout reconstruire à partir de là en quelques minutes.

---

## 1. Sauvegarder le fichier - **BLOQUANT, à faire tout de suite**

- [ ] Dans Power BI Desktop : **Ctrl+S** (ou *Fichier → Enregistrer sous*)
- [ ] Choisir l'emplacement : `C:\Users\Lenovo\Desktop\PowerBi\Projet_Solaris\`
- [ ] Nom : `solaris.pbix`
- [ ] Vérifier que la barre de titre n'affiche plus « Sans titre »

**Recommandation** : préférer *Fichier → Enregistrer sous → **Projet Power BI (\*.pbip)***.
Un `.pbip` est du texte léger et versionnable, alors qu'un `.pbix` de 3,7 M de
lignes dépassera les 100 Mo et fera échouer le `git push` (c'est déjà le cas
actuellement, ton dernier envoi est ressorti en code 1).

---

## 2. Créer la matrice - **étape 5 de la consigne**

- [ ] Cliquer sur **Vue Rapport** (icône graphique, barre latérale gauche)
- [ ] Dans le volet *Visualisations*, choisir l'icône **Matrice**
- [ ] **Lignes** : glisser `dim_commune[commune]` (ou `dim_departement[cle_departement]`)
- [ ] **Colonnes** : glisser `dim_temps[annee]` (ou `dim_temps[trimestre]`)
- [ ] **Valeurs** : glisser `[Nombre de mutations]`, `[Valeur fonciere totale]`, `[Prix moyen m2]`
- [ ] Ajouter un **segment** avec `dim_type_local[type_local]`
- [ ] Mettre en forme : montants en €, prix au m² en €, titre de page « Marché immobilier 2025 »
- [ ] **Ctrl+S** à nouveau

### Variante « datamart » (plus rapide, utilise la table agrégée)

- Lignes : `dim_commune[commune]`
- Colonnes : `dim_temps[annee]`
- Valeurs : `[Nb mutations agrege]`, `[Valeur agregee]`, `[Prix moyen m2 agrege]`

### Chiffres de contrôle attendus

| Indicateur | Valeur |
|---|---:|
| Nombre de mutations | 1 320 973 |
| Valeur foncière totale | 319 901 489 835 € |
| Prix moyen au m² | 2 187,23 € |
| Paris (75) | 10 713 €/m² |
| Appartements (France) | 3 597 €/m² |
| Maisons (France) | 2 124 €/m² |

---

## 3. Avant le mercredi 7 octobre - **date limite prof**

- [ ] Proposer la source au professeur pour approbation
- [ ] Argumentaire à envoyer : jeu de données **DVF 2025** (*Demandes de valeurs
      foncières*, `data.gouv.fr`), fichier `ValeursFoncieres-2025.txt`
      - source officielle et ouverte (DGFiP / Etalab)
      - 473 Mo, 3,7 M lignes, 43 colonnes : bien au-delà des 100 lignes demandées
      - données réelles, pas fictives

> C'est la **seule étape que je ne peux pas faire** : elle est humaine
> (envoi par mail / Teams). Il reste 5 jours.

---

## 4. Avant le samedi 17 octobre - **remise finale**

- [ ] **Descriptif du cas métier** et des analyses permises
      → déjà rédigé : `MODELE_DATAMART.md` §6
- [ ] **Justification des transformations**
      → déjà rédigé : `MODELE_DATAMART.md` §4 (les 5 transformations, avec leur emplacement Power Query)
- [ ] **Données source dans le format utilisé par Power Query**
      → `ValeursFoncieres-2025.txt` (473 Mo, c'est le fichier lu par `DVF_Brut`)
- [ ] **Fichier `.pbix` comportant l'ensemble du projet**
      → à produire au point 1 + point 2

---

## 5. Nettoyage et confort (optionnel)

- [ ] Ajouter `*.pbix` au `.gitignore` (sinon le push échouera, fichier > 100 Mo)
- [ ] Trancher sur le brouillon Python : `datamart/` et `convert_dvf_to_datamart.py`
      ne sont plus utilisés (l'ETL est dans Power Query). À garder comme trace, ou à supprimer
- [ ] Supprimer ou ignorer `consignes.txt` (extrait de texte du PDF, généré pour lecture)
- [ ] Désactiver *Date/heure automatique* (`Fichier → Options → Chargement des données`) :
      `dim_temps` est marquée comme table de dates, les tables masquées sont inutiles
- [ ] Ajouter le dossier `modele_tmdl/` au dépôt git (sauvegarde texte du modèle, léger)

---

## 6. Vérifications finales avant remise

- [ ] **Accueil → Actualiser** : vérifier qu'aucune table ne remonte d'erreur
- [ ] Vérifier que `fait_mutation` = 3 714 829 lignes et `fait_marche_agrege` = 820 774 lignes
- [ ] Vérifier que la matrice se recalcule quand on filtre sur le type de local
- [ ] Vérifier que le `.pbix`/`.pbip` s'ouvre correctement après fermeture de Desktop
- [ ] Vérifier que `ValeursFoncieres-2025.txt` est bien présent à la racine
      (les requêtes pointent dessus en **chemin absolu**)

---

## Rappel : ce que je ne peux pas faire

| Action | Raison |
|---|---|
| Enregistrer le `.pbix` | action de l'interface Desktop, non exposée par l'API XMLA/TOM |
| Créer la matrice | le MCP ne modélise que le modèle sémantique, pas les pages de rapport |
| Envoyer la proposition au professeur | action humaine |

## Ce que je peux encore faire sur demande

- Rédiger un document de rendu unique (descriptif + justification, prêt à rendre)
- Mettre à jour le `.gitignore`
- Tenter de générer la page de rapport dans un `.pbip` (schéma PBIR, à tester prudemment)
- Reconstruire le modèle à partir de `modele_tmdl/` si le fichier non enregistré est perdu
